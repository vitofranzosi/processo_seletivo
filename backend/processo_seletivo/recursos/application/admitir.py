"""O juízo de admissibilidade — receber a peça não é admiti-la.

**A autorização é capacidade própria, fora da transação**, no molde de `publicar_resultado` — e
não `comando_de_comissao`, que autoriza por presidência da comissão. Autorizar por presidência
seria exatamente a derivação que a D-005 proíbe: quem preside a comissão que avaliou é quem tende
a estar impedido de julgar o recurso contra o que ela produziu (T-005, FR-037, FR-038).

**O impedimento é reavaliado dentro da transação, depois do bloqueio do Processo** (FR-043). A tela
já o nomeou antes de oferecer o botão, mas entre abrir a tela e confirmar pode ter nascido um
`Impedimento` — e a verificação que vale é a do instante da gravação.

**Admitir também é ato motivado.** Exigir motivo só na inadmissão faria a admissão parecer
automática, e ela não é: é a afirmação de que a peça é tempestiva, própria e regularmente instruída.
"""

from django.db import IntegrityError, transaction

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.recursos.application.porta import exigir_elegibilidade, travar
from processo_seletivo.recursos.models import JuizoDeAdmissibilidade
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import finish, reserve

PERMISSAO = "recurso:julgar"
OPERACAO = "recurso:admitir"

SEM_MOTIVO = "O juízo de admissibilidade é motivado nas duas direções: escreva a razão."
JA_APRECIADO = "Este recurso já teve a admissibilidade apreciada."
ESTADO_MUDOU = (
    "A situação deste recurso mudou enquanto esta página estava aberta. Recarregue e confira "
    "antes de decidir."
)


def admitir(
    *,
    actor,
    recurso_id,
    admitido,
    motivo,
    assinatura_do_estado,
    idempotency_key,
    correlation_id="",
):
    """Grava o juízo, ou recusa antes de gravar."""
    require_permission(actor, PERMISSAO)
    if not (motivo or "").strip():
        raise DomainError("appeal_reason_required", SEM_MOTIVO, 422)

    with command_context() as agora:
        peca = travar(actor, recurso_id)
        exigir_elegibilidade(actor, peca)
        _recusar_se_obsoleto(peca, assinatura_do_estado)

        reserva = reserve(
            actor=actor,
            operation=f"{OPERACAO}:{peca.pk}",
            key=idempotency_key,
            payload={"admitido": bool(admitido), "motivo": motivo},
        )
        if reserva.result_id:
            return JuizoDeAdmissibilidade.objects.get(pk=reserva.result_id)

        juizo = _gravar(
            recurso=peca,
            admitido=bool(admitido),
            motivo=motivo.strip(),
            decidido_por=actor.subject,
            decidido_em=agora,
        )
        auditar(
            actor=actor,
            permissao=PERMISSAO,
            operation=OPERACAO,
            aggregate=juizo,
            now=agora,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        finish(reserva, juizo, 201)
        return juizo


def _recusar_se_obsoleto(peca, assinatura_do_estado):
    """A tela leu um estado; se ele mudou, a confirmação é recusada (FR-100).

    Sem isto, duas pessoas abrindo a mesma peça ao mesmo tempo veriam a mesma tela e a segunda
    gravaria por cima do que a primeira decidiu — ou, pior, decidiria sem saber que já havia
    decisão.
    """
    from processo_seletivo.recursos.application.selectors import assinatura_do_estado_da_peca

    if assinatura_do_estado and assinatura_do_estado != assinatura_do_estado_da_peca(peca):
        raise DomainError("stale_appeal_state", ESTADO_MUDOU, 409)


def _gravar(**campos):
    """A gravação e a segunda barreira: `uq_juizo_por_recurso` responde sob concorrência.

    A leitura prévia não existe aqui de propósito — a constraint já responde, e consultá-la antes
    seria conforto de mensagem que a corrida desfaz de todo jeito (FR-032, FR-099).
    """
    try:
        with transaction.atomic():
            return JuizoDeAdmissibilidade.objects.create(**campos)
    except IntegrityError as exc:
        raise DomainError("appeal_already_reviewed", JA_APRECIADO, 409) from exc
