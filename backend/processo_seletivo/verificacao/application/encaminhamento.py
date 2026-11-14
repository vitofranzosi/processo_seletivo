"""O encaminhamento à entrevista ao vivo: o vídeo não confirmou (166, FR-7138 a FR-7144, D-005).

**Ato da presidência, explícito, e sem a contagem.** Quem o pratica é quem consolida — a mesma
capacidade, no mesmo Processo —, sobre as inscrições que o plano da consolidação separou como "o
vídeo não confirmou". A tela mostra o alcance antes da confirmação (Constituição, IV), e não mostra
como cada membro votou: a entrevista ao vivo ainda vai ser dada por eles, e o parecer às cegas da
`165` vale também para ela.

**Nada paralelo.** O encaminhamento grava a linha que diz que aconteceu e devolve as Avaliações à
Mesa pela **reabertura da `012`**, com o motivo fixo. As conclusões pelo vídeo ficam preservadas,
como toda conclusão reaberta. Se a `165` recusar alguma reabertura — o autor foi exposto aos
pareceres alheios —, a inscrição inteira volta ao que era: meio encaminhada ela não fica.
"""

import uuid

from django.db import IntegrityError, transaction

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.verificacao.application import disponibilidade, ganchos
from processo_seletivo.verificacao.models import EncaminhamentoAoVivo

ENCAMINHAR = "ENCAMINHAR_A_ENTREVISTA_AO_VIVO"
MOTIVO_DA_REABERTURA = (
    "Encaminhada à entrevista ao vivo: a deliberação pelo vídeo não confirmou a autodeclaração, "
    "e o vídeo só confirma (R-11)."
)
NAO_ENCAMINHAVEL = "esta inscrição não está entre as que o vídeo não confirmou"
DUPLICADO = "esta inscrição já foi encaminhada à entrevista ao vivo"


class _Recusa:
    def __init__(self, inscricao, motivo):
        self.inscricao = inscricao
        self.motivo = motivo

    def declarada(self):
        return {
            "inscricao": self.inscricao.protocolo or str(self.inscricao.id),
            "motivo": self.motivo,
        }


def a_encaminhar(*, edital, etapa_id) -> list:
    """As inscrições prontas da Etapa cuja deliberação pelo vídeo não confirmou (FR-7138)."""
    from processo_seletivo.resultados.application.consolidacao import _plano_do_lote

    try:
        _etapa, _consolidaveis, recusas = _plano_do_lote(edital, etapa_id, None)
    except DomainError as erro:
        if erro.code == "nada_pronto":
            return []
        raise
    return [recusa.inscricao for recusa in recusas if recusa.motivo == ganchos.ENCAMINHAR_AO_VIVO]


def encaminhar(
    *, actor, processo_id, edital_id, etapa_id, inscricao_ids, idempotency_key, correlation_id
):
    """Encaminha as inscrições marcadas, uma transação por inscrição, e declara as recusadas."""
    from processo_seletivo.avaliacoes.application.avaliacao import reabrir
    from processo_seletivo.avaliacoes.application.trilha import auditar
    from processo_seletivo.avaliacoes.models import Avaliacao
    from processo_seletivo.comissoes.application import comando_de_comissao
    from processo_seletivo.comissoes.application.comissao import identificador
    from processo_seletivo.resultados.application.consolidacao import (
        ATO,
        _edital_do_processo,
        _plano_do_lote,
    )

    ids = [identificador(item) for item in inscricao_ids]
    if not ids:
        raise DomainError(
            "selecao_vazia",
            "Selecione ao menos uma inscrição para encaminhar.",
            422,
            campo="inscricao_id",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload={
            "encaminhar": str(etapa_id),
            "inscricoes": sorted(str(item) for item in ids),
        },
        idempotency_key=idempotency_key,
    ) as ctx:
        edital = _edital_do_processo(ctx.processo, edital_id)
        if ctx.repetido:
            return ctx.desfecho_anterior
        # **A mesma regra que a tela declarou, relida no ato**: o plano da consolidação, que é a
        # fonte única de "o vídeo não confirmou" (D-006).
        _etapa, consolidaveis, recusas = _plano_do_lote(edital, etapa_id, ids)
        elegiveis = {
            recusa.inscricao.id: recusa.inscricao
            for recusa in recusas
            if recusa.motivo == ganchos.ENCAMINHAR_AO_VIVO
        }
        feitos, recusadas = [], []
        recusadas.extend(_Recusa(item.inscricao, NAO_ENCAMINHAVEL) for item in consolidaveis)
        for recusa in recusas:
            if recusa.inscricao.id not in elegiveis:
                recusadas.append(_Recusa(recusa.inscricao, NAO_ENCAMINHAVEL))
        for inscricao in elegiveis.values():
            video = disponibilidade.video_vigente(
                edital=edital, etapa_id=etapa_id, inscricao_id=inscricao.id
            )
            avaliacoes = list(
                Avaliacao.objects.filter(
                    atribuicao__edital=edital,
                    etapa_id=etapa_id,
                    inscricao_id=inscricao.id,
                    estado=Avaliacao.Estado.CONCLUIDA,
                ).order_by("concluida_em", "id")
            )
            try:
                with transaction.atomic():
                    encaminhamento = EncaminhamentoAoVivo.objects.create(
                        inscricao=inscricao,
                        edital=edital,
                        etapa_id=etapa_id,
                        video=video,
                        pareceres=[str(item.id) for item in avaliacoes],
                        registrado_em=ctx.now,
                        registrado_por=actor.subject,
                    )
                    for avaliacao in avaliacoes:
                        reabrir(
                            actor=actor,
                            processo_id=processo_id,
                            avaliacao_id=avaliacao.id,
                            motivo=MOTIVO_DA_REABERTURA,
                            expected_revision=avaliacao.revision,
                            idempotency_key=str(
                                uuid.uuid5(uuid.NAMESPACE_URL, f"{idempotency_key}:{avaliacao.id}")
                            ),
                            correlation_id=correlation_id,
                        )
                    auditar(
                        actor=actor,
                        permissao=ATO,
                        operation=ENCAMINHAR,
                        aggregate=encaminhamento,
                        now=ctx.now,
                        correlation_id=correlation_id,
                        reason=(
                            f"Inscrição {inscricao.protocolo or inscricao.id} encaminhada à "
                            "entrevista ao vivo: o vídeo só confirma."
                        ),
                        idempotency_key=idempotency_key,
                    )
            except IntegrityError:
                recusadas.append(_Recusa(inscricao, DUPLICADO))
                continue
            except DomainError as erro:
                recusadas.append(_Recusa(inscricao, erro.detail.rstrip(".").lower()))
                continue
            feitos.append(encaminhamento)
        declarado = {
            "feitas": len(feitos),
            "verbo": "encaminhada",
            "recusadas": len(recusadas),
            "ids": [str(item.id) for item in feitos],
            "motivos": [item.declarada() for item in recusadas],
        }
        ctx.concluir_sem_resultado(201, declarado)
        return declarado
