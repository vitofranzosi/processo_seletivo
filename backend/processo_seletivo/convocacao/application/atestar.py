"""O que aconteceu fora do sistema, e quem atestou que aconteceu (019, `US5`, `D-004`).

**O sistema não detém o artefato e não infere o fato.** Ele registra que uma pessoa competente
concluiu alguma coisa — que o convocado não acessou o ambiente, não apareceu na primeira semana,
não entregou presencialmente. A prova daquilo vive onde sempre viveu: no processo, na ata, no
relatório de acesso do ambiente virtual.

**Sem atestante não há atestado**, e é a razão de esta capacidade existir separada do desfecho. O
cancelamento de matrícula por inércia decide a vaga de alguém, e *"o prazo venceu"* não é uma pessoa
responsável: o `D-003` fechou que nenhum desfecho nasce do relógio, e o `D-004` que alguém
competente tem de concluir. O atestado é o lugar onde esse alguém fica escrito.

**E ele é distinto do não atendimento à convocação** (`D-011`). São dois desfechos com atores,
prazos e fundamentos diferentes: o não atendimento olha o vencimento informado na convocação; a
inércia olha um fato posterior à matrícula, que aconteceu fora daqui. Colapsá-los apagaria norma.
"""

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import AtestadoDeFatoExterno
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError

ATESTAR = "CONVOCACAO_ATESTAR"
ATO = "convocacao:atestar"


def atestar(
    *,
    actor,
    processo_id,
    inscricao_id,
    especie,
    conclusao,
    referencia_do_prazo,
    idempotency_key,
    correlation_id,
):
    """Registra o atestado e devolve o que ele declarou. Nada aqui cancela matrícula nenhuma.

    **O atestado é insumo do desfecho, e não o desfecho.** Quem cancela a matrícula é quem registra
    o desfecho de inércia, citando este atestado — e são dois atos porque podem ser duas pessoas: a
    que constata o fato e a que decide a consequência dele.
    """
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload={"inscricao": str(inscricao_id), "especie": (especie or "").strip()},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        inscricao = _inscricao_do_processo(ctx.processo, inscricao_id)
        especie = _especie(especie)
        texto = (conclusao or "").strip()
        if not texto:
            raise DomainError(
                nomes.CONCLUSAO_OBRIGATORIA,
                "Declare o que foi concluído: o atestado é a conclusão de quem o assina, e sem "
                "ela ele não atesta nada.",
                422,
                campo="conclusao",
            )
        prazo = (referencia_do_prazo or "").strip()
        if not prazo:
            # **Copiada do conteúdo publicado por quem atesta, e não lida de campo.** O sistema não
            # tem prazo de matrícula publicado para ler — a `R-004` recusou criar calendário —, e
            # sem a referência o atestado diria "não apareceu" sem dizer até quando deveria ter
            # aparecido. Uma Retificação posterior também não reescreve o que a pessoa leu ao
            # concluir, porque o que fica gravado é a cópia.
            raise DomainError(
                nomes.REFERENCIA_DO_PRAZO_OBRIGATORIA,
                "Declare o prazo que o Edital publicou para este ato, copiado do conteúdo "
                "publicado: sem ele o atestado não diz até quando a pessoa deveria ter agido.",
                422,
                campo="referencia_do_prazo",
            )
        atestado = AtestadoDeFatoExterno(
            inscricao=inscricao,
            especie=especie,
            conclusao=texto,
            referencia_do_prazo=prazo,
            atestado_por=str(getattr(actor, "subject", actor)),
            atestado_em=ctx.now,
        )
        atestado.save()
        return _concluir(ctx, atestado, actor, correlation_id, idempotency_key)


def _especie(valor):
    especie = (valor or "").strip()
    if especie not in nomes.ESPECIES_DE_ATESTADO:
        raise DomainError(
            nomes.ESPECIE_DE_ATESTADO_INVALIDA,
            "O fato externo é um dos três que os Editais nomeiam, e nada mais.",
            422,
            campo="especie",
        )
    return especie


def _concluir(ctx, atestado, actor, correlation_id, idempotency_key):
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=ATESTAR,
        aggregate=atestado,
        now=ctx.now,
        correlation_id=correlation_id,
        # **Quem atestou fica na razão, e não só no agregado.** É a pergunta que alguém fará um dia:
        # não *"o prazo venceu?"*, e sim *"quem concluiu que venceu, e contra qual prazo?"*.
        reason=(
            f"Atestado de fato externo {atestado.especie} sobre a inscrição "
            f"{atestado.inscricao_id}. Prazo de referência: {atestado.referencia_do_prazo}. "
            f"Conclusão: {atestado.conclusao}"
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(atestado.id),
        "inscricao": str(atestado.inscricao_id),
        "especie": atestado.especie,
        "atestadoPor": atestado.atestado_por,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


def _inscricao_do_processo(processo, inscricao_id):
    inscricao = Inscricao.objects.filter(
        id=identificador(inscricao_id), edital__processo=processo
    ).first()
    if inscricao is None:
        raise DomainError("inscricao_nao_encontrada", "Inscrição não encontrada.", 404)
    return inscricao


__all__ = ["atestar"]
