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
    escopos = escopos_vigentes(pessoa_id)
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
        get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
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
        get_user_model().objects.select_for_update().filter(pk=pessoa.pk).first()
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
