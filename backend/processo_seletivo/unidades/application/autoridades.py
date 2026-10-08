"""As autoridades da unidade: conferi-las no ato de publicar, e mantê-las (060).

**Uma regra, chamada pelos três atos de publicar.** Edital, Retificação e Resultado chamam
`autoridade_para_o_ato` dentro da transação que grava a Publicação, antes de gravá-la. A verificação
é do domínio, e não da tela (FR-1126): a tela oferece só as vigentes da unidade, mas o que só a tela
filtra um formulário forjado contorna.

**A trava é da linha.** Encerrar e corrigir travam a mesma linha que a publicação trava; o
encerramento confirmado entre a abertura da tela e a publicação é visto por ela, e a correção que
chega depois do primeiro uso encontra `usada_em` preenchida e é recusada (R-005).
"""

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import finish, reserve
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.application.selectors import exigir_unidade, identificador
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.domain.rotulos import rotulo_da_autoridade
from processo_seletivo.unidades.domain.vigencia import periodo, situacao, vigente
from processo_seletivo.unidades.models import AutoridadeHabilitada


def conferir(autoridade_id, *, unidade_codigo, data, travar=False):
    """A autoridade escolhida, se habilitada na unidade e vigente na data — ou a recusa.

    Inexistente e de outra unidade recusam com a **mesma** mensagem: a de outra unidade é
    indistinguível de inexistente. Fora de vigência diz o período, porque é o que quem publica
    precisa saber para escolher outra.

    Sem `travar`, é a conferência que antecede um gesto e não grava nada; o ato mesmo passa por
    `autoridade_para_o_ato`, que trava a linha e confere de novo.
    """
    if not str(autoridade_id or "").strip():
        raise DomainError(
            nomes.SIGNATARIO_OBRIGATORIO,
            "Escolha a autoridade que responde por este ato.",
            422,
            campo="autoridade",
        )
    chave = identificador(autoridade_id)
    consulta = AutoridadeHabilitada.objects.select_related("unidade").filter(
        pk=chave, unidade__codigo=str(unidade_codigo or "")
    )
    if travar:
        consulta = consulta.select_for_update()
    autoridade = consulta.first() if chave else None
    if autoridade is None:
        raise DomainError(
            nomes.AUTORIDADE_INDISPONIVEL,
            "A autoridade escolhida não está habilitada para esta unidade.",
            422,
            campo="autoridade",
        )
    if not vigente(autoridade, data):
        raise DomainError(
            nomes.AUTORIDADE_FORA_DE_VIGENCIA,
            f"A autoridade escolhida não está vigente hoje (período: {periodo(autoridade)}).",
            422,
            campo="autoridade",
        )
    return autoridade


def autoridade_para_o_ato(autoridade_id, *, unidade_codigo, data_do_ato, now):
    """A autoridade conferida e travada para o ato, ou a recusa sem nada gravado (FR-1126).

    Grava `usada_em` no primeiro uso. A partir dali nome, cargo, ato de nomeação e início ficam
    imutáveis, no domínio e no banco (FR-1121).
    """
    autoridade = conferir(
        autoridade_id, unidade_codigo=unidade_codigo, data=data_do_ato, travar=True
    )
    if autoridade.usada_em is None:
        autoridade.usada_em = now
        autoridade.save(update_fields=["usada_em"])
    return autoridade


# ---------------------------------------------------------------------------------------------
# A manutenção: cadastrar, corrigir e encerrar, pelo Gestor da própria unidade (D-005, FR-1122).
# ---------------------------------------------------------------------------------------------


def _campos(autoridade):
    """O que a trilha guarda de antes e de depois: o registro, legível, sem o identificador."""
    return {
        "cargo": autoridade.cargo,
        "nome": autoridade.nome,
        "ato_de_nomeacao": autoridade.ato_de_nomeacao,
        "inicio_vigencia": autoridade.inicio_vigencia.isoformat(),
        "fim_vigencia": (autoridade.fim_vigencia.isoformat() if autoridade.fim_vigencia else None),
    }


def _texto(valor, campo, *, obrigatorio=False):
    texto = str(valor or "").strip()
    if obrigatorio and not texto:
        raise DomainError(
            nomes.CARGO_OBRIGATORIO, "Informe o cargo da autoridade.", 422, campo=campo
        )
    if len(texto) > 255:
        raise DomainError("campo_longo_demais", "Use no máximo 255 caracteres.", 422, campo=campo)
    return texto


def _hoje(now):
    return now.astimezone(ZONA).date()


def _da_unidade_do_ator(actor, autoridade_id):
    """A autoridade travada, se for da unidade do ator; senão, a mesma recusa de inexistente."""
    chave = identificador(autoridade_id)
    autoridade = (
        AutoridadeHabilitada.objects.select_for_update()
        .filter(pk=chave, unidade__codigo=actor.institution_scope)
        .first()
        if chave
        else None
    )
    if autoridade is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return autoridade


def _auditar(*, actor, operation, autoridade, now, correlation_id, idempotency_key, detalhe):
    record_event(
        actor=actor,
        permission=nomes.GERIR,
        operation=operation,
        aggregate=autoridade,
        now=now,
        correlation_id=correlation_id,
        reason=rotulo_da_autoridade(autoridade),
        # Agregado sem ciclo de vida declarado: a situação é derivada da vigência, e a trilha a
        # registra como era no instante do ato (D-014 da 011).
        new_state=situacao(autoridade, _hoje(now)).upper(),
        new_revision=None,
        idempotency_key=idempotency_key,
        detalhe=detalhe,
    )


def cadastrar(
    *,
    actor,
    cargo,
    inicio_vigencia,
    nome="",
    ato_de_nomeacao="",
    idempotency_key,
    correlation_id,
):
    """Uma autoridade habilitada na unidade do ator (FR-1116).

    Unidade desativada também recebe cadastro: o certame que nela segue em curso precisa de quem
    responda pelos atos que faltam (FR-1110).
    """
    require_permission(actor, nomes.GERIR)
    dados = {
        "cargo": _texto(cargo, "cargo", obrigatorio=True),
        "nome": _texto(nome, "nome"),
        "ato_de_nomeacao": _texto(ato_de_nomeacao, "ato_de_nomeacao"),
    }
    if inicio_vigencia is None:
        raise DomainError(
            nomes.VIGENCIA_INVERTIDA,
            "Informe o início da vigência.",
            422,
            campo="inicio_vigencia",
        )
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation="autoridade:cadastrar",
            key=idempotency_key,
            payload={**dados, "inicio_vigencia": inicio_vigencia.isoformat()},
        )
        if idem.result_id:
            return AutoridadeHabilitada.objects.get(pk=idem.result_id)
        unidade = exigir_unidade(actor.institution_scope)
        autoridade = AutoridadeHabilitada.objects.create(
            unidade=unidade,
            inicio_vigencia=inicio_vigencia,
            cadastrada_por=actor.subject,
            cadastrada_em=now,
            **dados,
        )
        _auditar(
            actor=actor,
            operation="CADASTRAR_AUTORIDADE",
            autoridade=autoridade,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            detalhe={"depois": _campos(autoridade)},
        )
        finish(idem, autoridade, 201)
        return autoridade


def corrigir(
    *,
    actor,
    autoridade_id,
    cargo,
    inicio_vigencia,
    nome="",
    ato_de_nomeacao="",
    idempotency_key,
    correlation_id,
):
    """Corrige o registro enquanto ele não respondeu por ato nenhum (FR-1121, `D-004`).

    Depois do primeiro uso, o identificador já liga uma Publicação a este registro, e mudar o nome
    faria a auditoria responder errado a quem assinou: a correção vira encerrar e cadastrar outra.
    """
    require_permission(actor, nomes.GERIR)
    dados = {
        "cargo": _texto(cargo, "cargo", obrigatorio=True),
        "nome": _texto(nome, "nome"),
        "ato_de_nomeacao": _texto(ato_de_nomeacao, "ato_de_nomeacao"),
    }
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"autoridade:corrigir:{autoridade_id}",
            key=idempotency_key,
            payload={**dados, "inicio_vigencia": str(inicio_vigencia)},
        )
        if idem.result_id:
            return AutoridadeHabilitada.objects.get(pk=idem.result_id)
        autoridade = _da_unidade_do_ator(actor, autoridade_id)
        if autoridade.usada_em is not None:
            raise DomainError(
                nomes.AUTORIDADE_JA_USADA,
                "Esta autoridade já respondeu por um ato publicado, e o registro dela não se "
                "corrige: encerre-a e cadastre outra.",
                422,
            )
        if inicio_vigencia is None or (
            autoridade.fim_vigencia is not None and inicio_vigencia > autoridade.fim_vigencia
        ):
            raise DomainError(
                nomes.VIGENCIA_INVERTIDA,
                "O início da vigência não pode ser posterior ao fim.",
                422,
                campo="inicio_vigencia",
            )
        antes = _campos(autoridade)
        for campo, valor in dados.items():
            setattr(autoridade, campo, valor)
        autoridade.inicio_vigencia = inicio_vigencia
        autoridade.save(update_fields=[*dados, "inicio_vigencia"])
        _auditar(
            actor=actor,
            operation="CORRIGIR_AUTORIDADE",
            autoridade=autoridade,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            detalhe={"antes": antes, "depois": _campos(autoridade)},
        )
        finish(idem, autoridade, 200)
        return autoridade


def encerrar(*, actor, autoridade_id, fim_vigencia, idempotency_key, correlation_id):
    """Encerra a vigência, sem retroagir, com fim inclusivo (FR-1120).

    O fim não pode ser anterior a hoje: o registro passaria a dizer que a autoridade não respondia
    em dias em que pode ter respondido. Encerrar com o fim de hoje a mantém disponível hoje e a
    retira amanhã. Um fim futuro já declarado pode ser antecipado ou adiado, desde que não retroaja.
    """
    require_permission(actor, nomes.GERIR)
    with command_context() as now:
        idem = reserve(
            actor=actor,
            operation=f"autoridade:encerrar:{autoridade_id}",
            key=idempotency_key,
            payload={"fim_vigencia": str(fim_vigencia)},
        )
        if idem.result_id:
            return AutoridadeHabilitada.objects.get(pk=idem.result_id)
        autoridade = _da_unidade_do_ator(actor, autoridade_id)
        hoje = _hoje(now)
        if autoridade.fim_vigencia is not None and autoridade.fim_vigencia < hoje:
            raise DomainError(
                nomes.AUTORIDADE_JA_ENCERRADA,
                f"Esta autoridade já está encerrada ({periodo(autoridade)}).",
                422,
            )
        if fim_vigencia is None or fim_vigencia < autoridade.inicio_vigencia:
            raise DomainError(
                nomes.VIGENCIA_INVERTIDA,
                "O fim da vigência não pode ser anterior ao início.",
                422,
                campo="fim_vigencia",
            )
        if fim_vigencia < hoje:
            raise DomainError(
                nomes.ENCERRAMENTO_RETROATIVO,
                "O fim da vigência não pode ser anterior a hoje. Para retirá-la agora, encerre "
                "com o fim de hoje: ela continua disponível até o fim deste dia.",
                422,
                campo="fim_vigencia",
            )
        antes = _campos(autoridade)
        autoridade.fim_vigencia = fim_vigencia
        autoridade.encerrada_por = actor.subject
        autoridade.encerrada_em = now
        autoridade.save(update_fields=["fim_vigencia", "encerrada_por", "encerrada_em"])
        _auditar(
            actor=actor,
            operation="ENCERRAR_AUTORIDADE",
            autoridade=autoridade,
            now=now,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            detalhe={"antes": antes, "depois": _campos(autoridade)},
        )
        finish(idem, autoridade, 200)
        return autoridade
