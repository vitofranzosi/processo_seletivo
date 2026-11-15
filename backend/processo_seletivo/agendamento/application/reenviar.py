"""Reenviar o aviso de agenda que não saiu: um aviso filho, com o mesmo texto (167, FR-7233).

**Pela agenda, e não pela tela de reenvio da `066`.** O reenvio da `066` recompõe um texto só para o
universo inteiro do ato; o aviso de agenda tem o texto de uma pessoa — o horário dela, a sala dela.
O precedente é o aviso de pendência da `134`, que também não se reenvia por lá
(`recusar_reenvio_da_pendencia`). Aqui o filho repete o texto do pai, como o "reenvio de falhas" da
`066` faz: terminar de entregar o que foi decidido, e não decidir de novo.

**Só o que não saiu** — falha definitiva ou expirado sem envio, o alcance de
`REENVIO_DE_FALHAS` —, e só a partir do último da cadeia: o pai não muda (append-only), e um segundo
filho sobre o mesmo pai mandaria de novo a quem o primeiro já entregou (`FR-1264` da `066`). O
endereço é relido, porque a pessoa pode ter corrigido a credencial desde a falha.
"""

from django.utils import timezone

from processo_seletivo.agendamento.domain import nomes, recusas
from processo_seletivo.agendamento.models import HorarioPublicado
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.avisos.application.comando import recusar_se_desabilitado
from processo_seletivo.avisos.application.selectors import estados_do_aviso
from processo_seletivo.avisos.domain import nomes as nomes_dos_avisos
from processo_seletivo.avisos.models import Aviso, DestinatarioDoAviso
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.processos.models import Edital

OPERACAO = "agenda:reenviar"


def raiz(aviso):
    """O primeiro aviso da cadeia de reenvios: o que o `HorarioPublicado` aponta."""
    while aviso.aviso_anterior_id is not None:
        aviso = aviso.aviso_anterior
    return aviso


def reenviar(*, actor, edital, etapa_id, aviso_id, idempotency_key, correlation_id=""):
    """Põe de novo na fila o aviso de uma pessoa que não saiu. Devolve o `Aviso` filho."""
    from processo_seletivo.agendamento.application import leitura
    from processo_seletivo.identidade.application.endereco import enderecos_das_inscricoes

    recusar_se_desabilitado()
    with comando_de_comissao(
        actor=actor,
        processo_id=edital.processo_id,
        operation=OPERACAO,
        payload={"edital": str(edital.id), "etapa": str(etapa_id), "aviso": str(aviso_id)},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return Aviso.objects.get(pk=ctx.desfecho_anterior["id"])
        agora = ctx.now or timezone.now()
        edital = Edital.objects.filter(pk=edital.id, processo=ctx.processo).first()
        if edital is None:
            raise nao_encontrado()
        agenda = leitura.agenda_da_etapa(edital, etapa_id, travar=True)
        anterior = (
            Aviso.objects.filter(pk=aviso_id, edital=edital, origem=nomes_dos_avisos.AGENDA)
            .select_related("aviso_anterior")
            .first()
            if agenda is not None
            else None
        )
        if anterior is None:
            raise nao_encontrado()
        horario = (
            HorarioPublicado.objects.filter(aviso=raiz(anterior), ato__agenda=agenda)
            .select_related("inscricao")
            .first()
        )
        if horario is None:
            raise nao_encontrado()
        nome = horario.inscricao.nome or horario.inscricao.protocolo
        alcance = nomes_dos_avisos.ALCANCE_DO_REENVIO[nomes_dos_avisos.REENVIO_DE_FALHAS]
        estados = estados_do_aviso(anterior, agora=agora)
        if anterior.reenvios.exists() or not any(estado in alcance for _, estado, _ in estados):
            raise recusas.aviso_nao_reenviavel(nome)
        endereco = enderecos_das_inscricoes([horario.inscricao]).get(horario.inscricao.id, "")
        filho = Aviso.objects.create(
            edital=edital,
            institution_scope=edital.institution_scope,
            origem=nomes_dos_avisos.AGENDA,
            motivo=nomes_dos_avisos.REENVIO_DE_FALHAS,
            aviso_anterior=anterior,
            perfil_id=anterior.perfil_id,
            marco_id=None,
            referencia_da_publicacao=anterior.referencia_da_publicacao,
            assunto=anterior.assunto,
            corpo=anterior.corpo,
            solicitado_por=actor.subject,
            solicitado_em=agora,
            idempotency_key=idempotency_key or "",
            correlation_id=correlation_id or "",
        )
        DestinatarioDoAviso.objects.create(
            aviso=filho,
            inscricao=horario.inscricao,
            elegibilidade=nomes_dos_avisos.ELEGIVEL,
            endereco=endereco,
        )
        record_event(
            actor=actor,
            permission=ctx.base.permissao,
            operation=nomes.REENVIO_DO_AVISO_DA_AGENDA,
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            reason="Reenvio do aviso de agenda que não saiu",
            previous_state="PUBLICADA",
            new_state="PUBLICADA",
            previous_revision=agenda.revision,
            new_revision=agenda.revision,
            idempotency_key=idempotency_key or "",
            # O aviso e o anterior, e não o endereço nem o nome (FR-7256, FR-1278 da `066`).
            detalhe={"aviso": str(filho.id), "anterior": str(anterior.id)},
        )
        ctx.concluir_sem_resultado(201, {"id": str(filho.id)})
        return filho
