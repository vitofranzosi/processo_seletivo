"""O período da Etapa, lido do conteúdo já carregado (171, T-002; FR-7305)."""

from datetime import UTC, datetime

from processo_seletivo.editais.domain.cronograma import CANCELADO, periodo_da_etapa

EVENTO = "e1"
INICIO = datetime(2026, 12, 1, 12, 0, tzinfo=UTC)
FIM = datetime(2026, 12, 5, 23, 0, tzinfo=UTC)


def conteudo(**evento):
    base = {"id": EVENTO, "startAt": INICIO.isoformat(), "endAt": FIM.isoformat()}
    return {"schedule": [{**base, **evento}]}


def test_le_o_evento_que_a_etapa_aponta():
    assert periodo_da_etapa(conteudo(), {"scheduleEventId": EVENTO}) == (INICIO, FIM)


def test_aceita_o_instante_do_rascunho():
    rascunho = {"schedule": [{"id": EVENTO, "startAt": INICIO, "endAt": FIM}]}
    assert periodo_da_etapa(rascunho, {"scheduleEventId": EVENTO}) == (INICIO, FIM)


def test_sem_evento_nao_ha_periodo():
    assert periodo_da_etapa(conteudo(), {}) == (None, None)
    assert periodo_da_etapa(conteudo(), {"scheduleEventId": "outro"}) == (None, None)
    assert periodo_da_etapa(None, None) == (None, None)


def test_o_evento_cancelado_nao_e_periodo():
    assert periodo_da_etapa(conteudo(status=CANCELADO), {"scheduleEventId": EVENTO}) == (
        None,
        None,
    )


def test_o_evento_sem_fim_tem_so_o_inicio():
    assert periodo_da_etapa(conteudo(endAt=None), {"scheduleEventId": EVENTO}) == (INICIO, None)
