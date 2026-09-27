"""A régua da fase no domínio, e a lista do que ainda vem (045 `FR-735`, 047 `FR-765` a `FR-767`).

**Sem banco e sem relógio.** O conteúdo é o dicionário publicado, e todo instante é fixado no teste.
Cada Evento é lido em três instantes — antes, durante e depois —, porque uma régua que acerta um
deles e erra outro é exatamente a divergência que a `047` existe para remover.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.editais.domain.calendario import CONCLUIDO, EM_ANDAMENTO, PLANEJADO
from processo_seletivo.editais.domain.fase_do_evento import (
    fase_do_evento,
    fase_publica_do_evento,
    marcos_pendentes,
)

VITORIA = ZoneInfo("America/Sao_Paulo")
INICIO = datetime(2026, 10, 5, 9, 0, tzinfo=VITORIA)
TERMINO = datetime(2026, 10, 9, 18, 0, tzinfo=VITORIA)


def evento(identificador, *, inicio=INICIO, termino=None, periodo=False, status="PLANEJADO"):
    return {
        "id": identificador,
        "description": identificador,
        "startAt": inicio.isoformat() if inicio else None,
        "endAt": termino.isoformat() if termino else None,
        "order": 0,
        "status": status,
        "isRegistrationPeriod": periodo,
    }


def conteudo(*eventos):
    return {"schedule": list(eventos)}


ANTES = INICIO - timedelta(hours=1)
DURANTE = INICIO + timedelta(hours=1)
DEPOIS = TERMINO + timedelta(hours=1)


@pytest.mark.parametrize(
    ("agora", "esperada"),
    [(ANTES, PLANEJADO), (DURANTE, EM_ANDAMENTO), (DEPOIS, CONCLUIDO)],
)
def test_evento_com_termino(agora, esperada):
    lido = evento("prova", termino=TERMINO)
    assert fase_do_evento(lido, conteudo(lido), agora) == esperada


@pytest.mark.parametrize(
    ("agora", "esperada"),
    [(ANTES, PLANEJADO), (DURANTE, CONCLUIDO), (DEPOIS, CONCLUIDO)],
)
def test_evento_sem_termino_conclui_no_instante_do_inicio(agora, esperada):
    """`D-004` da `047`: uma hora depois do início, a prova pontual já é *concluída*.

    A régua anterior do portal a mantinha *acontecendo agora* até a meia-noite — em UTC.
    """
    lido = evento("resultado")
    assert fase_do_evento(lido, conteudo(lido), agora) == esperada


@pytest.mark.parametrize(
    ("agora", "esperada"),
    [(ANTES, PLANEJADO), (DURANTE, EM_ANDAMENTO), (DEPOIS, EM_ANDAMENTO)],
)
def test_periodo_de_inscricoes_sem_termino_segue_aberto(agora, esperada):
    """A régua do período (FR-347): sem término, o período não conclui pelo início."""
    lido = evento("inscricoes", periodo=True)
    assert fase_do_evento(lido, conteudo(lido), agora) == esperada


@pytest.mark.parametrize("agora", [ANTES, DURANTE, DEPOIS])
def test_cancelado_nao_tem_fase(agora):
    lido = evento("prova", termino=TERMINO, status="CANCELADO")
    assert fase_do_evento(lido, conteudo(lido), agora) is None
    assert fase_publica_do_evento(lido, conteudo(lido), agora) is None


@pytest.mark.parametrize("agora", [ANTES, DURANTE, DEPOIS])
def test_sem_inicio_nao_tem_fase(agora):
    lido = evento("sem-inicio", inicio=None)
    assert fase_do_evento(lido, conteudo(lido), agora) is None


def test_periodo_cancelado_a_gestao_le_o_cancelamento_e_o_portal_le_o_periodo():
    """A única diferença entre as duas leituras, e ela é nomeada (047, caso-limite).

    A gestão diz o que foi declarado (045 `FR-736`). O portal não pode dizer *cancelado* de um
    período em que o sistema continua recebendo inscrição, porque a marca da mesma página diz
    *aberta* pela mesma régua.
    """
    lido = evento("inscricoes", termino=TERMINO, periodo=True, status="CANCELADO")

    assert fase_do_evento(lido, conteudo(lido), DURANTE) is None
    assert fase_publica_do_evento(lido, conteudo(lido), DURANTE) == EM_ANDAMENTO


@pytest.mark.parametrize("agora", [ANTES, DURANTE, DEPOIS])
def test_fora_do_periodo_cancelado_as_duas_leituras_coincidem(agora):
    eventos = [
        evento("prova", termino=TERMINO),
        evento("resultado"),
        evento("inscricoes", periodo=True),
        evento("cancelado", status="CANCELADO"),
    ]
    for lido in eventos:
        assert fase_publica_do_evento(lido, conteudo(*eventos), agora) == fase_do_evento(
            lido, conteudo(*eventos), agora
        )


def test_marcos_pendentes_tira_o_concluido_e_o_cancelado_e_mantem_o_em_curso():
    em_curso = evento("em-curso", inicio=INICIO - timedelta(days=1), termino=TERMINO)
    concluido = evento("concluido", inicio=INICIO - timedelta(days=2))
    futuro = evento("futuro", inicio=INICIO + timedelta(days=3))
    cancelado = evento("cancelado", inicio=INICIO + timedelta(days=1), status="CANCELADO")
    lido = conteudo(futuro, cancelado, concluido, em_curso)

    pendentes = marcos_pendentes(lido, DURANTE)

    assert [item[0]["id"] for item in pendentes] == ["em-curso", "futuro"]
    assert [item[3] for item in pendentes] == [EM_ANDAMENTO, PLANEJADO]
