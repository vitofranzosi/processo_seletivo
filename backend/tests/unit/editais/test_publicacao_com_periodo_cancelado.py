"""RC-119, fechado pela revisão do PR 221: publicar com o período cancelado é impedido.

Desde 28/09/2026 o período declarado `CANCELADO` não recebe inscrição. A publicação, que já impedia
o período vencido (`028`, `FR-346`), deixava passar o cancelado sem achado nenhum: o Edital nascia
sem receber inscrição, e ninguém avisava.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)

AGORA = datetime(2026, 10, 7, 12, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
CODIGO = "registration_period_cancelled"


def _snapshot(status, *, marcados=1):
    eventos = [
        {
            "id": f"e-{indice}",
            "type": "Inscrições",
            "description": "Período de inscrições",
            "startAt": (AGORA + timedelta(days=1)).isoformat(),
            "endAt": (AGORA + timedelta(days=10)).isoformat(),
            "order": indice,
            "status": status,
            "isRegistrationPeriod": indice <= marcados,
        }
        for indice in (1, 2)
    ]
    return {"title": "Edital 7/2026", "schedule": eventos}


def _achados(snapshot, ato=ATO_DE_PUBLICACAO):
    return [
        item
        for item in validate_for_publication(snapshot, ato=ato, agora=AGORA)
        if item.code == CODIGO
    ]


def test_o_periodo_cancelado_impede_a_publicacao_e_diz_o_que_fazer():
    [achado] = _achados(_snapshot("CANCELADO"))

    assert achado.severity == Severity.BLOCKING_ERROR
    assert "'Período de inscrições'" in achado.message
    assert "não receberá inscrição alguma" in achado.message
    assert "etapa Inscrição" in achado.message and "pela API" in achado.message
    assert achado.path == "/schedule/id=e-1/status"


def test_nao_e_o_impedimento_do_vencido():
    """A `FR-347` proíbe o do vencido com término futuro, e a `FR-348` pede código próprio."""
    codigos = {item.code for item in validate_for_publication(_snapshot("CANCELADO"), agora=AGORA)}
    assert "registration_period_closed" not in codigos


def test_sem_cancelamento_com_marca_ambigua_e_na_retificacao_nao_ha_achado():
    assert _achados(_snapshot("PLANEJADO")) == []
    assert _achados(_snapshot("CANCELADO", marcados=2)) == []
    assert _achados(_snapshot("CANCELADO"), ato=ATO_DE_RETIFICACAO) == []
