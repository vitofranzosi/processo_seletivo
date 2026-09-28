"""Editais publicados antes da 047: a projeção omite o que o registro não tem (`FR-775`).

**Por que sem banco.** A projeção pública é leitura pura do conteúdo publicado: o conteúdo entra,
a estrutura de tela sai. O que um Edital antigo tem de diferente é **o que falta** no conteúdo
dele — `appealWindow`, `location`, uma fase declarada que a API aceitava antes da `045`. Estes
casos alimentam as funções de leitura com o conteúdo na forma antiga, que é a pergunta inteira; o
caminho pela view já é exercido pelos testes de cada história.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from processo_seletivo.editais.domain.fase_do_evento import fase_do_evento
from processo_seletivo.portal import leitura
from processo_seletivo.recursos.domain.janela import computavel, declaracao_do_marco

VITORIA = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 9, 26, 15, 0, tzinfo=VITORIA)


def test_marco_sem_appeal_window_nao_produz_prazo():
    """O conteúdo anterior a 07/09 não tem a chave: prazo não computável, e nada é dito."""
    conteudo = {"profiles": [{"classificationMilestones": [{"id": "m1", "stages": ["e1"]}]}]}

    assert computavel(declaracao_do_marco(conteudo, "m1")) is None


def test_evento_sem_location_nao_escreve_local():
    conteudo = {
        "schedule": [
            {
                "id": "e1",
                "description": "Prova",
                "startAt": (AGORA + timedelta(days=3)).isoformat(),
                "order": 0,
            }
        ]
    }

    (evento,) = leitura.cronograma(conteudo, AGORA)

    assert evento["local"] == ""


def test_fase_declarada_pela_api_antiga_e_lida_como_nao_cancelado():
    """Antes da 045 a API aceitava `EM_ANDAMENTO`. O conteúdo não é reescrito, e a fase vem das
    datas: um Evento futuro com `status` "em andamento" continua *por vir*."""
    evento = {
        "id": "e1",
        "description": "Resultado",
        "startAt": (AGORA + timedelta(days=5)).isoformat(),
        "order": 0,
        "status": "EM_ANDAMENTO",
    }
    conteudo = {"schedule": [evento]}

    assert leitura.situacao_do_evento(evento, conteudo, AGORA) == "futuro"
    assert fase_do_evento(evento, conteudo, AGORA) == "PLANEJADO"
    assert leitura.agora_e_proximo(conteudo, AGORA)["proximos"][0]["nome"] == "Resultado"


def test_evento_sem_inicio_nao_tem_fase_nem_e_proximo():
    evento = {"id": "e1", "description": "Sem data", "order": 0}
    conteudo = {"schedule": [evento]}

    assert leitura.situacao_do_evento(evento, conteudo, AGORA) == ""
    assert leitura.agora_e_proximo(conteudo, AGORA) == {"em_andamento": [], "proximos": []}


def test_cronograma_vazio_nao_inventa_agora_nem_proximo():
    assert leitura.agora_e_proximo({}, AGORA) == {"em_andamento": [], "proximos": []}
