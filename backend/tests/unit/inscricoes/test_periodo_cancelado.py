"""RC-119: o período de inscrições declarado `CANCELADO` não recebe inscrição.

**Decidido pelo usuário em 28/09** (`doc/registro-pre-piloto-2026-09-28.md`, *O que foi
decidido*). A régua do período lia só as datas, e o período cancelado continuava recebendo; o
`CANCELADO` é a única declaração do Evento, e prevalece (045, `FR-736`). O período cancelado fica
**encerrado**, quaisquer que sejam as datas, e marcado como cancelado para que ninguém diga que ele
"encerrou em" um término que ainda não chegou.
"""

from datetime import datetime, timedelta

from processo_seletivo.avaliacoes.domain.conjunto import conjunto_fechado
from processo_seletivo.editais.domain.validation import validate_for_publication
from processo_seletivo.inscricoes.domain.periodo import (
    ABERTO,
    ENCERRADO,
    periodo_de_inscricoes,
    recebe_inscricoes,
)
from processo_seletivo.shared.tempo import ZONA

AGORA = datetime(2026, 10, 10, 12, tzinfo=ZONA)


def _conteudo(status="PLANEJADO"):
    return {
        "schedule": [
            {
                "id": "00000000-0000-0000-0000-000000000119",
                "type": "INSCRICAO",
                "description": "Período de inscrições",
                "startAt": (AGORA - timedelta(days=2)).isoformat(),
                "endAt": (AGORA + timedelta(days=5)).isoformat(),
                "status": status,
                "isRegistrationPeriod": True,
            }
        ]
    }


def test_o_periodo_cancelado_esta_encerrado_dentro_das_datas():
    periodo = periodo_de_inscricoes(_conteudo("CANCELADO"), AGORA)

    assert periodo.estado == ENCERRADO
    assert periodo.cancelado
    assert not periodo.aberto
    # As datas publicadas continuam lidas: são o Evento, e o Evento não se reescreve.
    assert periodo.fim == AGORA + timedelta(days=5)


def test_o_periodo_cancelado_nao_recebe_inscricao():
    assert recebe_inscricoes(status="PUBLICADO", conteudo=_conteudo(), agora=AGORA)
    assert not recebe_inscricoes(status="PUBLICADO", conteudo=_conteudo("CANCELADO"), agora=AGORA)


def test_o_periodo_nao_cancelado_continua_pela_regua_das_datas():
    periodo = periodo_de_inscricoes(_conteudo(), AGORA)
    assert periodo.estado == ABERTO
    assert not periodo.cancelado


def test_com_o_periodo_cancelado_o_conjunto_de_inscricoes_esta_fechado():
    """A distribuição e a relação do sorteio esperam o conjunto fechar, e ele fechou."""
    assert not conjunto_fechado(_conteudo(), AGORA)
    assert conjunto_fechado(_conteudo("CANCELADO"), AGORA)


def test_a_publicacao_nao_diz_que_o_periodo_cancelado_encerrou_em_data_futura():
    """O `FR-346` é sobre o término vencido, e o período cancelado não venceu."""
    achados = validate_for_publication(_conteudo("CANCELADO"), agora=AGORA)
    assert "registration_period_closed" not in {achado.code for achado in achados}
