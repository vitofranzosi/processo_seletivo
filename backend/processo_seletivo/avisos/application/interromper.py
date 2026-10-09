"""A interrupção do aviso: o que ainda não saiu não sai mais (066, `D-006`, `FR-1273`).

**A defesa contra o engano que o usuário nomeou**, "centenas de candidatos por engano", no único
momento em que ela ainda funciona: os primeiros minutos do envio.

**Sob a mesma trava que o despacho toma antes de cada tentativa** (`R-002`). O despacho trava o
aviso, confere a interrupção e grava o início da tentativa, numa transação só; a interrupção trava
o mesmo aviso e grava. Uma das duas espera a outra: a tentativa que começou antes da interrupção é
registrada, e nenhuma começa depois dela.

**O que o servidor de correio aceitou não volta** (`UX-177`). A interrupção não recolhe nada.
"""

from processo_seletivo.avisos.application.comando import comando_de_aviso
from processo_seletivo.avisos.application.despacho import travar_o_aviso
from processo_seletivo.avisos.application.selectors import aviso_do_ator, estados_do_aviso
from processo_seletivo.avisos.domain import estado as estado_
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import InterrupcaoDoAviso
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.idempotency import finish


def interromper(*, actor, aviso_id, motivo, idempotency_key, correlation_id):
    from processo_seletivo.avaliacoes.application.trilha import auditar

    motivo = (motivo or "").strip()
    if not motivo:
        raise DomainError(
            nomes.AVISO_TEXTO_INVALIDO,
            "Diga por que o envio está sendo interrompido: o motivo fica no registro.",
            422,
            campo="motivo",
        )
    aviso = aviso_do_ator(actor, aviso_id)
    with comando_de_aviso(
        actor=actor,
        processo_id=aviso.edital.processo_id,
        origem=aviso.origem,
        operation=nomes.ATO_INTERROMPER,
        payload={"aviso": str(aviso.id), "motivo": motivo},
        idempotency_key=idempotency_key,
        protetor=True,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        travar_o_aviso(aviso.id)
        estados = [estado for _, estado, _ in estados_do_aviso(aviso, agora=ctx.now)]
        if InterrupcaoDoAviso.objects.filter(aviso=aviso).exists() or estado_.concluido(estados):
            raise DomainError(
                nomes.AVISO_CONCLUIDO,
                "Este aviso já terminou, ou já foi interrompido: não há envio a parar.",
                409,
            )
        interrupcao = InterrupcaoDoAviso.objects.create(
            aviso=aviso, motivo=motivo, interrompido_por=actor.subject, interrompido_em=ctx.now
        )
        aceitas = estados.count(nomes.ESTADO_ACEITA)
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=nomes.OPERACAO_INTERROMPER,
            aggregate=interrupcao,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=(
                f"Aviso {aviso.id} interrompido com {aceitas} mensagem(ns) já aceita(s) pelo "
                f"servidor de correio. Motivo: {motivo}"
            ),
            idempotency_key=idempotency_key,
        )
        declarado = {"aviso": str(aviso.id), "aceitas": aceitas}
        finish(ctx.reserva, interrupcao, 201, declarado)
        return declarado


__all__ = ["interromper"]
