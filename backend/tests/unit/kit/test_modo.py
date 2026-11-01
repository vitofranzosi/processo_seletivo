"""O modo do material, pelo período e pelo desfecho (111, FR-3410, revisão de código de 01/11)."""

from datetime import datetime

from processo_seletivo.inscricoes.domain.periodo import ABERTO, Periodo
from processo_seletivo.portal import ficha as fichas
from processo_seletivo.processos.application.selectors import Desfecho


def test_periodo_designado_sem_datas_e_neutro():
    """Sem início nem término, qualquer frase de prazo sairia vazia: "até , às"."""
    modo, motivo = fichas._modo(Periodo(ABERTO), None)
    assert modo == fichas.NEUTRO
    assert "não tem datas" in motivo


def test_processo_cancelado_e_dito_cancelado():
    desfecho = Desfecho("PROCESSO", "CANCELADO", datetime(2026, 11, 1, tzinfo=fichas.ZONA))
    modo, motivo = fichas._modo(Periodo(ABERTO), desfecho)
    assert modo == fichas.SEM_MATERIAL
    assert "O Processo foi cancelado em 01/11/2026" in motivo


def test_processo_encerrado_e_dito_encerrado():
    desfecho = Desfecho("PROCESSO", "ENCERRADO", None)
    assert "O Processo foi encerrado." in fichas._modo(Periodo(ABERTO), desfecho)[1]
