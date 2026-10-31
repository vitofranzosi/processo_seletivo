"""Conceder e revogar acesso, e ler o que está vigente (106, `D-005`, `D-006`).

**Dois níveis, e nenhum concede a si mesmo.** O administrador de acessos da unidade concede os
papéis operacionais na unidade dele; o administrador institucional concede o administrador de
acessos de qualquer unidade e nenhum poder operacional; o administrador institucional nasce só pelo
comando de implantação. A comparação com o ator é pelo identificador interno, e não pelo nome nem
pelo login: é ela que torna a regra efetiva contra quem troca de sessão ou de unidade (`FR-3012`).

**As recusas seguem a doutrina da `033`.** Falta de capacidade é 403; capacidade em outra unidade é
404, porque o ator não deve saber o que existe fora do seu escopo (`FR-3010`).
"""

import hashlib

from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.db.models import Q

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_DE_ACESSOS,
    ADMINISTRADOR_INSTITUCIONAL,
    ADMINISTRAR,
    CONSULTAR,
    ESCOPO_INSTITUCIONAL,
    GERIR,
    INTEGRANTE,
    PAPEIS_DE_ACESSO,
    PAPEIS_INSTITUCIONAIS,
)
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.seguranca.autenticacao import PREFIXO_DO_IDENTIFICADOR
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.seguranca.models import RevogacaoDeVinculo, Vinculo
from processo_seletivo.shared.api.problems import DomainError

# As recusas (`FR-3013`, `FR-3014`).
AUTOCONCESSAO = "autoconcessao"
MOTIVO_OBRIGATORIO = "motivo_obrigatorio"
PAPEL_INEXISTENTE = "papel_inexistente"
PAPEL_SO_POR_IMPLANTACAO = "papel_so_por_implantacao"
VINCULO_JA_VIGENTE = "vinculo_ja_vigente"
VINCULO_JA_REVOGADO = "vinculo_ja_revogado"
ESCOPO_INVALIDO = "escopo_invalido"
ADMINISTRACAO_JA_CONCEDIDA = "administracao_ja_concedida"
# A retirada e a substituição da administração institucional (107, incremento 2, `D-018`).
SEM_ADMINISTRACAO = "pessoa_sem_administracao_institucional"
ULTIMA_ADMINISTRACAO = "ultima_administracao_institucional"
# A recusa da pessoa que não está disponível para receber acesso: desativada, ou um identificador
# que não é de pessoa institucional nenhuma (107, `D-004`, `D-011`). Uma recusa só para os dois
# casos, para que o campo oculto adulterado não sirva de sonda de quem existe.
PESSOA_INDISPONIVEL = "pessoa_indisponivel"

# A busca de pessoas (107, `D-005`). O piso e o teto são o que impede a tela de virar a listagem dos
# servidores: sem termo não há resultado, e com termo curto também não.
PISO_DA_BUSCA = 3
TETO_DA_BUSCA = 10

# O ator da trilha quando quem concede é a implantação — o mesmo sujeito da sincronização das
# unidades (`unidades/domain/nomes.py`), e pela mesma razão: o comando roda com o acesso de quem
# implanta, e não há permissão a conferir.
IMPLANTACAO = "implantacao"

# A trava da decisão "já há administração institucional?" — uma constante só, como a do despacho dos
# avisos. **Trava de sessão do PostgreSQL, e não `FOR UPDATE`**: a role de runtime não tem `UPDATE`
# sobre os vínculos append-only, e trancar uma linha deles seria recusado em produção.
TRAVA_DA_ADMINISTRACAO_INSTITUCIONAL = (
    int.from_bytes(hashlib.sha256(b"seguranca:administracao-institucional").digest()[:8], "big")
    >> 1
)


def _papeis_operacionais():
    # Importado aqui, e não no topo: o `PAPEIS` mora na fronteira de identidade da interface, e
    # ela importa este módulo para resolver o ator institucional.
    from processo_seletivo.interface.identidade import PAPEIS

    return {**PAPEIS, INTEGRANTE: PAPEIS_DE_ACESSO[INTEGRANTE]}


def catalogo():
    """Todo papel concedível, com o nome e as permissões, nos três catálogos (`FR-3009`)."""
    return {**_papeis_operacionais(), **PAPEIS_DE_ACESSO, **PAPEIS_INSTITUCIONAIS}


def permissoes_dos_papeis(papeis):
    todos = catalogo()
    return frozenset(permissao for papel in papeis for permissao in todos.get(papel, ("", []))[1])


def vigentes():
    return Vinculo.objects.filter(revogacao__isnull=True)


def papeis_vigentes(pessoa_id, escopo):
    """Os papéis vigentes da pessoa no escopo, numa consulta (`FR-3017`)."""
    if not escopo:
        return []
    return sorted(
        set(vigentes().filter(pessoa_id=pessoa_id, escopo=escopo).values_list("papel", flat=True))
    )


def escopos_vigentes(pessoa_id):
    return sorted(set(vigentes().filter(pessoa_id=pessoa_id).values_list("escopo", flat=True)))


def unidade_inicial(pessoa_id):
    """A primeira unidade, em ordem de código, em que a pessoa atua; ou o escopo institucional.

    Nenhuma das duas, `None`: a pessoa entrou e não tem onde atuar (`FR-3019`).
    """
    return _unidade_inicial_entre(escopos_vigentes(pessoa_id))


def unidade_inicial_de(vigentes_da_pessoa):
    """A mesma regra, sobre os pares (escopo, papel) já lidos — sem consulta (107, `D-006`)."""
    return _unidade_inicial_entre(sorted({escopo for escopo, _ in vigentes_da_pessoa}))


def _unidade_inicial_entre(escopos):
    unidades = [escopo for escopo in escopos if escopo != ESCOPO_INSTITUCIONAL]
    if unidades:
        return unidades[0]
    return ESCOPO_INSTITUCIONAL if ESCOPO_INSTITUCIONAL in escopos else None


def vinculos_vigentes_da_unidade(ator):
    """Quem atua na unidade do ator, com o papel e a concessão (`FR-3016`)."""
    require_permission(ator, CONSULTAR)
    return (
        vigentes()
        .filter(escopo=ator.institution_scope)
        .select_related("pessoa")
        .order_by("pessoa__username", "papel")
    )


def _exigir_motivo(motivo):
    motivo = (motivo or "").strip()
    if not motivo:
        raise DomainError(
            MOTIVO_OBRIGATORIO,
            "Informe o motivo — por exemplo, o número da portaria. A trilha guarda por que o "
            "acesso foi dado ou tirado.",
            422,
        )
    return motivo


def _exigir_unidade(escopo):
    from processo_seletivo.unidades.application.selectors import exigir_unidade

    if escopo == ESCOPO_INSTITUCIONAL:
        raise DomainError(
            ESCOPO_INVALIDO,
            "Este papel se concede numa unidade, e não no escopo institucional.",
            422,
        )
    exigir_unidade(escopo, ativa=True)


def _autoridade(ator, *, escopo, papel):
    """A permissão com que o ator concede ou revoga este papel neste escopo, ou a recusa."""
    if papel in _papeis_operacionais():
        require_permission(ator, GERIR, institution_scope=escopo)
        return GERIR
    if papel == ADMINISTRADOR_DE_ACESSOS:
        require_permission(ator, ADMINISTRAR, institution_scope=ESCOPO_INSTITUCIONAL)
        return ADMINISTRAR
    if papel == ADMINISTRADOR_INSTITUCIONAL:
        raise DomainError(
            PAPEL_SO_POR_IMPLANTACAO,
            "A administração institucional de acessos se concede só pelo comando de implantação, "
            "com o ato que a designa.",
            403,
        )
    raise DomainError(PAPEL_INEXISTENTE, f"{papel} não é um papel do sistema.", 422)


def _recusar_proprio(ator, pessoa):
    if pessoa.username == ator.subject:
        raise DomainError(
            AUTOCONCESSAO,
            "Ninguém concede nem revoga o próprio acesso. Peça a outra pessoa com a mesma "
            "permissão.",
            403,
        )


def conceder(ator, *, pessoa, escopo, papel, motivo, now, correlation_id=""):
    """O vínculo novo, depois de todas as recusas, com a trilha (`FR-3010` a `FR-3015`)."""
    permissao = _autoridade(ator, escopo=escopo, papel=papel)
    _recusar_proprio(ator, pessoa)
    motivo = _exigir_motivo(motivo)
    _exigir_unidade(escopo)
    with transaction.atomic():
        # A pessoa trancada serializa duas concessões do mesmo papel: a segunda vê a primeira.
        travada = get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
        # Desativada não acumula acesso para quando voltar (107, `D-011`). Conferido sob a trava: a
        # desativação que chegar antes dela é vista aqui.
        if travada is None or not travada.is_active:
            raise _indisponivel()
        if vigentes().filter(pessoa=pessoa, escopo=escopo, papel=papel).exists():
            raise DomainError(VINCULO_JA_VIGENTE, "A pessoa já tem este papel nesta unidade.", 409)
        vinculo = Vinculo.objects.create(
            pessoa=pessoa,
            escopo=escopo,
            papel=papel,
            concedido_em=now,
            concedido_por=ator.subject,
            motivo=motivo,
        )
        _registrar(ator, permissao, "ACESSO_CONCEDER", vinculo, now, correlation_id, motivo)
    return vinculo


def conferir_concessao(ator, *, pessoa, escopo, papel):
    """As recusas da concessão, sem gravar nada — a primeira etapa da tela (107, `D-003`).

    A confirmação chama `conceder`, que confere tudo de novo sob a trava: o que vale é a segunda
    conferência, e esta só evita mostrar a confirmação de um ato que já se sabe recusado.
    """
    _autoridade(ator, escopo=escopo, papel=papel)
    _recusar_proprio(ator, pessoa)
    _exigir_unidade(escopo)
    if not pessoa.is_active:
        raise _indisponivel()
    if vigentes().filter(pessoa=pessoa, escopo=escopo, papel=papel).exists():
        raise DomainError(VINCULO_JA_VIGENTE, "A pessoa já tem este papel nesta unidade.", 409)


def conferir_revogacao(ator, *, vinculo):
    """As recusas da revogação, sem gravar nada (107, `D-003`)."""
    _autoridade(ator, escopo=vinculo.escopo, papel=vinculo.papel)
    _recusar_proprio(ator, vinculo.pessoa)
    if RevogacaoDeVinculo.objects.filter(vinculo_id=vinculo.pk).exists():
        raise DomainError(VINCULO_JA_REVOGADO, "Este vínculo já foi revogado.", 409)


def revogar(ator, *, vinculo, motivo, now, correlation_id=""):
    """A revogação, com as regras de autoridade da concessão do mesmo papel (`FR-3014`)."""
    permissao = _autoridade(ator, escopo=vinculo.escopo, papel=vinculo.papel)
    _recusar_proprio(ator, vinculo.pessoa)
    motivo = _exigir_motivo(motivo)
    ja_revogado = DomainError(VINCULO_JA_REVOGADO, "Este vínculo já foi revogado.", 409)
    with transaction.atomic():
        # A pessoa trancada, e não o vínculo: `SELECT ... FOR UPDATE` exige o privilégio de
        # `UPDATE`, que a role de runtime não tem sobre as tabelas append-only — trancar o vínculo
        # passava na suíte, que roda como superusuário, e recusaria toda revogação em produção. A
        # segunda revogação simultânea o banco recusa de qualquer modo, pela unicidade.
        get_user_model().objects.select_for_update().filter(pk=vinculo.pessoa_id).first()
        if RevogacaoDeVinculo.objects.filter(vinculo_id=vinculo.pk).exists():
            raise ja_revogado
        try:
            with transaction.atomic():
                revogacao = RevogacaoDeVinculo.objects.create(
                    vinculo=vinculo, revogado_em=now, revogado_por=ator.subject, motivo=motivo
                )
        except IntegrityError as erro:
            raise ja_revogado from erro
        _registrar(ator, permissao, "ACESSO_REVOGAR", vinculo, now, correlation_id, motivo)
    return revogacao


def conceder_administracao_institucional(*, pessoa, motivo, adicional, now, correlation_id=""):
    """O primeiro administrador institucional, pela implantação (`FR-3029`).

    **Uma vez só, salvo marca explícita.** A segunda pessoa com poder institucional é decisão, e
    não engano de terminal: sem `adicional`, o comando recusa.
    """
    motivo = _exigir_motivo(motivo)
    ator = Actor(IMPLANTACAO, ESCOPO_INSTITUCIONAL)
    with transaction.atomic():
        # **A decisão é global, e a trava também.** Trancar só a pessoa deixava duas execuções para
        # pessoas diferentes trancarem linhas diferentes, verem as duas que ainda não havia ninguém
        # e gravarem dois administradores sem `adicional` (revisão do #345). A trava de transação
        # serializa a consulta e a gravação, e sai sozinha no fim do bloco. Fora do PostgreSQL é
        # no-op, e é honesto que seja: o SQLite serializa a escrita inteira.
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_advisory_xact_lock(%s)", [TRAVA_DA_ADMINISTRACAO_INSTITUCIONAL]
                )
        travada = get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
        # Suspensa ou desativada não recebe poder institucional pela implantação, como não recebe
        # vínculo pela tela (revisão do #346: só a substituição conferia).
        if travada is None or not travada.is_active:
            raise _indisponivel()
        existentes = vigentes().filter(
            escopo=ESCOPO_INSTITUCIONAL, papel=ADMINISTRADOR_INSTITUCIONAL
        )
        if existentes.filter(pessoa=pessoa).exists():
            raise DomainError(
                VINCULO_JA_VIGENTE, "A pessoa já é administradora institucional de acessos.", 409
            )
        if existentes.exists() and not adicional:
            raise DomainError(
                ADMINISTRACAO_JA_CONCEDIDA,
                "Já há administração institucional de acessos vigente. Para conceder a mais uma "
                "pessoa, repita com --adicional.",
                409,
            )
        vinculo = Vinculo.objects.create(
            pessoa=pessoa,
            escopo=ESCOPO_INSTITUCIONAL,
            papel=ADMINISTRADOR_INSTITUCIONAL,
            concedido_em=now,
            concedido_por=IMPLANTACAO,
            motivo=motivo,
        )
        _registrar(ator, IMPLANTACAO, "ACESSO_CONCEDER", vinculo, now, correlation_id, motivo)
    return vinculo


def _indisponivel():
    return DomainError(
        PESSOA_INDISPONIVEL,
        "Esta pessoa não está disponível para receber acesso: está suspensa ou desativada, ou o "
        "identificador não é de pessoa institucional.",
        409,
    )


def pessoas_institucionais():
    """As pessoas que entraram pelo provedor e estão ativas — o universo da busca (107, `D-005`).

    O prefixo separa a pessoa institucional de qualquer outro `auth_user` que exista no banco, como
    um superusuário criado à mão, que não tem vínculo e não entra (`D-008` da `106`).
    """
    return get_user_model().objects.filter(
        is_active=True, username__startswith=PREFIXO_DO_IDENTIFICADOR
    )


def pessoa_institucional(identificador):
    """A pessoa ativa daquele identificador interno, ou a recusa (107, `D-004`)."""
    pessoa = pessoas_institucionais().filter(username=identificador or "").first()
    if pessoa is None:
        raise _indisponivel()
    return pessoa


def buscar_pessoas(ator, termo, *, permissao, escopo, com_inativas=False):
    """Até dez pessoas com o termo no nome ou no e-mail, e se havia mais (107, `FR-3112`–`FR-3114`).

    **A capacidade é conferida antes da consulta**, no escopo em que o ator concede: quem não pode
    conceder não descobre quem existe. O próprio ator não aparece — a autoconcessão é recusada de
    qualquer modo, e oferecê-la seria convite ao erro.
    """
    require_permission(ator, permissao, institution_scope=escopo)
    termo = (termo or "").strip()
    if len(termo) < PISO_DA_BUSCA:
        return [], False
    # `com_inativas` é só da seção de suspensão (107, `D-017`): é ali que se acha quem está
    # suspenso para reativar. A concessão nunca as vê (`FR-3140`).
    universo = (
        get_user_model().objects.filter(username__startswith=PREFIXO_DO_IDENTIFICADOR)
        if com_inativas
        else pessoas_institucionais()
    )
    achadas = list(
        universo.exclude(username=ator.subject)
        .filter(Q(first_name__icontains=termo) | Q(email__icontains=termo))
        .order_by("first_name", "email", "username")
        .only("username", "first_name", "email", "is_active")[: TETO_DA_BUSCA + 1]
    )
    return achadas[:TETO_DA_BUSCA], len(achadas) > TETO_DA_BUSCA


def vigentes_da_pessoa(pessoa_id):
    """Os pares (escopo, papel) vigentes da pessoa, numa consulta (107, `D-006`)."""
    return sorted(set(vigentes().filter(pessoa_id=pessoa_id).values_list("escopo", "papel")))


def nome_legivel(pessoa):
    """Como a pessoa aparece na tela: nome, ou e-mail, nunca o identificador interno (`FR-3103`)."""
    if pessoa is None:
        return "pessoa sem nome informado"
    return pessoa.first_name or pessoa.email or "pessoa sem nome informado"


def nomes_dos_autores(identificadores):
    """Quem concedeu ou revogou, pelo nome, numa consulta só (107, `D-008`)."""
    identificadores = set(identificadores)
    nomes = {IMPLANTACAO: "Implantação"}
    for pessoa in get_user_model().objects.filter(username__in=identificadores):
        nomes[pessoa.username] = nome_legivel(pessoa)
    return {
        identificador: nomes.get(identificador, identificador) for identificador in identificadores
    }


def historico(ator, *, permissao, no_escopo, escopos, papeis=None, limite=200):
    """As concessões e revogações de um escopo, mais recentes primeiro (107, `FR-3107`).

    Lidas dos próprios vínculos e revogações, e não da trilha: são eles a resposta de quem tinha
    qual papel quando. A permissão se confere no escopo em que o ator está (`no_escopo`); os
    `escopos` lidos são a unidade dele, ou as unidades registradas, no nível institucional.
    """
    require_permission(ator, permissao, institution_scope=no_escopo)
    vinculos = Vinculo.objects.filter(escopo__in=list(escopos)).select_related(
        "pessoa", "revogacao"
    )
    if papeis is not None:
        vinculos = vinculos.filter(papel__in=list(papeis))
    vinculos = list(vinculos.order_by("-concedido_em")[:limite])
    eventos = []
    for vinculo in vinculos:
        eventos.append(
            ("concessao", vinculo.concedido_em, vinculo.concedido_por, vinculo.motivo, vinculo)
        )
        # O acesso reverso ausente levanta um `DoesNotExist` que também é `AttributeError`, e por
        # isso o padrão do `getattr` basta.
        revogacao = getattr(vinculo, "revogacao", None)
        if revogacao is not None:
            eventos.append(
                (
                    "revogacao",
                    revogacao.revogado_em,
                    revogacao.revogado_por,
                    revogacao.motivo,
                    vinculo,
                )
            )
    eventos.sort(key=lambda evento: evento[1], reverse=True)
    return eventos


def administradores_por_unidade(ator):
    """Cada unidade registrada, com os administradores de acessos vigentes (107, `FR-3120`)."""
    from processo_seletivo.unidades.models import Unidade

    require_permission(ator, ADMINISTRAR, institution_scope=ESCOPO_INSTITUCIONAL)
    unidades = list(Unidade.objects.order_by("codigo"))
    por_escopo = {}
    for vinculo in (
        vigentes()
        .filter(papel=ADMINISTRADOR_DE_ACESSOS, escopo__in=[u.codigo for u in unidades])
        .select_related("pessoa")
        .order_by("pessoa__first_name", "pessoa__username")
    ):
        por_escopo.setdefault(vinculo.escopo, []).append(vinculo)
    return [(unidade, por_escopo.get(unidade.codigo, [])) for unidade in unidades]


def _trancar_a_administracao_institucional():
    # A mesma trava da primeira administração: toda decisão sobre quantas pessoas a têm passa por
    # ela, e a retirada e a substituição também decidem isso.
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_advisory_xact_lock(%s)", [TRAVA_DA_ADMINISTRACAO_INSTITUCIONAL]
            )


def _administracao_vigente_de(pessoa):
    vinculo = (
        vigentes()
        .filter(pessoa=pessoa, escopo=ESCOPO_INSTITUCIONAL, papel=ADMINISTRADOR_INSTITUCIONAL)
        .first()
    )
    if vinculo is None:
        raise DomainError(
            SEM_ADMINISTRACAO, "A pessoa não tem administração institucional vigente.", 409
        )
    return vinculo


def retirar_administracao_institucional(
    *, pessoa, motivo, sem_administracao=False, now, correlation_id=""
):
    """A retirada pela implantação, com motivo e trilha (107, `FR-3147`, decisão P3).

    **Não deixa o sistema sem administração por engano** (`D-018`; confirmada pelo usuário, P5 da
    `107`): retirar a última pessoa exige `sem_administracao`, como a
    segunda concessão exige `adicional`. Sem administração institucional, ninguém concede o
    administrador de acessos de unidade nenhuma até a implantação conceder de novo.
    """
    motivo = _exigir_motivo(motivo)
    ator = Actor(IMPLANTACAO, ESCOPO_INSTITUCIONAL)
    with transaction.atomic():
        _trancar_a_administracao_institucional()
        get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
        vinculo = _administracao_vigente_de(pessoa)
        restantes = (
            vigentes()
            .filter(escopo=ESCOPO_INSTITUCIONAL, papel=ADMINISTRADOR_INSTITUCIONAL)
            .exclude(pk=vinculo.pk)
            .exists()
        )
        if not restantes and not sem_administracao:
            raise DomainError(
                ULTIMA_ADMINISTRACAO,
                "Esta é a última administração institucional vigente. Para retirá-la mesmo assim, "
                "repita com --sem-administracao; para trocar de pessoa, use a substituição.",
                409,
            )
        RevogacaoDeVinculo.objects.create(
            vinculo=vinculo, revogado_em=now, revogado_por=IMPLANTACAO, motivo=motivo
        )
        _registrar(ator, IMPLANTACAO, "ACESSO_REVOGAR", vinculo, now, correlation_id, motivo)
    return vinculo


def substituir_administracao_institucional(*, de, para, motivo, now, correlation_id=""):
    """Revoga a de uma pessoa e concede a outra, numa transação só (107, `FR-3148`, decisão P3).

    Não há instante com o anterior ainda ativo nem com uma administração a mais: se a concessão é
    recusada, a revogação sai com o *rollback*. Os dois eventos levam o mesmo motivo e a mesma
    correlação, para que a trilha os leia como um ato.
    """
    import uuid

    motivo = _exigir_motivo(motivo)
    correlation_id = correlation_id or f"substituicao-{uuid.uuid4().hex}"
    ator = Actor(IMPLANTACAO, ESCOPO_INSTITUCIONAL)
    if de.pk == para.pk:
        raise DomainError(VINCULO_JA_VIGENTE, "A pessoa nova é a mesma que sai.", 409)
    with transaction.atomic():
        _trancar_a_administracao_institucional()
        # As duas pessoas, em ordem de chave, para que duas substituições cruzadas não se esperem
        # uma à outra.
        list(
            get_user_model()
            .objects.select_for_update()
            .filter(pk__in=[de.pk, para.pk])
            .order_by("pk")
        )
        anterior = _administracao_vigente_de(de)
        if (
            vigentes()
            .filter(pessoa=para, escopo=ESCOPO_INSTITUCIONAL, papel=ADMINISTRADOR_INSTITUCIONAL)
            .exists()
        ):
            raise DomainError(
                VINCULO_JA_VIGENTE, "A pessoa nova já é administradora institucional.", 409
            )
        if not get_user_model().objects.filter(pk=para.pk, is_active=True).exists():
            raise _indisponivel()
        RevogacaoDeVinculo.objects.create(
            vinculo=anterior, revogado_em=now, revogado_por=IMPLANTACAO, motivo=motivo
        )
        _registrar(ator, IMPLANTACAO, "ACESSO_REVOGAR", anterior, now, correlation_id, motivo)
        novo = Vinculo.objects.create(
            pessoa=para,
            escopo=ESCOPO_INSTITUCIONAL,
            papel=ADMINISTRADOR_INSTITUCIONAL,
            concedido_em=now,
            concedido_por=IMPLANTACAO,
            motivo=motivo,
        )
        _registrar(ator, IMPLANTACAO, "ACESSO_CONCEDER", novo, now, correlation_id, motivo)
    return anterior, novo


def _registrar(ator, permissao, operacao, vinculo, now, correlation_id, motivo):
    record_event(
        actor=ator,
        permission=permissao,
        operation=operacao,
        aggregate=vinculo,
        now=now,
        correlation_id=correlation_id,
        reason=motivo,
        new_state="revogado" if operacao == "ACESSO_REVOGAR" else "vigente",
        new_revision=None,
        detalhe={
            "pessoa": vinculo.pessoa.username,
            "escopo": vinculo.escopo,
            "papel": vinculo.papel,
        },
    )
