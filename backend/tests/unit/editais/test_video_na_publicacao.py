"""A admissão do vídeo na publicação (166, US1, FR-7103, FR-7104; `contracts/recusas.md`).

Puro, sobre o conteúdo do exemplo da `163` e da `165`: a Heteroidentificação colegiada, com alcance,
agora com o período da Etapa e `videoOption`.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_RETIFICACAO,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.verificacao.domain import admissao
from tests.unit.editais.test_alcance_da_etapa import _conteudo, _etapa

EVENTO = "00000000-0000-0000-0000-000000000403"
CODIGOS = (
    "video_sem_protocolo",
    "video_fora_da_colegiada",
    "video_sem_alcance",
    "video_sem_periodo",
)


def _com_periodo(etapa, *, inicio="2026-12-01T08:00:00-03:00", fim="2026-12-05T18:00:00-03:00"):
    conteudo = _conteudo(etapa=etapa)
    conteudo["schedule"] = [
        {
            "id": EVENTO,
            "type": "VERIFICACAO",
            "description": "Verificação",
            "startAt": inicio,
            "endAt": fim,
        }
    ]
    return conteudo


def _video(**campos):
    return _etapa(
        **{
            "evaluationsPerRegistration": 3,
            "deliberationRule": "UNANIMOUS_FOR_FAVORABLE",
            "scheduleEventId": EVENTO,
            "videoOption": True,
            **campos,
        }
    )


def _codigos(conteudo, **ato):
    return sorted(
        achado.code
        for achado in blocking_findings(validate_for_publication(conteudo, **ato))
        if achado.code in CODIGOS
    )


def test_a_etapa_colegiada_com_alcance_e_periodo_publica(settings):
    settings.VERIFICACAO_POR_VIDEO = True
    assert _codigos(_com_periodo(_video())) == []


def test_sem_a_chave_a_publicacao_e_impedida(settings):
    """FR-7104: o vídeo depende de protocolo institucional que ainda não existe."""
    settings.VERIFICACAO_POR_VIDEO = False
    assert _codigos(_com_periodo(_video())) == ["video_sem_protocolo"]


def test_sem_a_chave_a_retificacao_nao_recusa_o_que_ja_admitia(settings):
    """Achado I1: quem recusa o acréscimo na Retificação é `retificacoes.py`, que vê a mudança."""
    settings.VERIFICACAO_POR_VIDEO = False
    assert _codigos(_com_periodo(_video()), ato=ATO_DE_RETIFICACAO) == []


@pytest.mark.parametrize(
    ("campos", "codigo"),
    [
        ({"forma": "PONTUADA", "deliberationRule": None}, "video_fora_da_colegiada"),
        ({"evaluationsPerRegistration": 1, "deliberationRule": None}, "video_fora_da_colegiada"),
        ({"deliberationRule": None}, "video_fora_da_colegiada"),
        ({"modalityCodes": None}, "video_sem_alcance"),
        ({"scheduleEventId": None}, "video_sem_periodo"),
    ],
)
def test_cada_falta_e_nomeada(settings, campos, codigo):
    """FR-7103: só a Etapa colegiada, com alcance e período."""
    settings.VERIFICACAO_POR_VIDEO = True
    assert codigo in _codigos(_com_periodo(_video(**campos)))


def test_periodo_sem_fim_e_recusado(settings):
    settings.VERIFICACAO_POR_VIDEO = True
    assert _codigos(_com_periodo(_video(), fim=None)) == ["video_sem_periodo"]


def test_a_etapa_que_nao_admite_nao_tem_achado(settings):
    settings.VERIFICACAO_POR_VIDEO = False
    assert _codigos(_conteudo(etapa=_etapa(videoOption=False))) == []


def test_a_frase_do_documento_so_onde_admite():
    """FR-7106, UX-770: as duas formas valem igual, e o vídeo só confirma."""
    assert "as duas formas valem igual" in admissao.frase({"videoOption": True})
    assert "só confirma" in admissao.frase({"videoOption": True})
    assert admissao.frase({"videoOption": False}) == ""
    assert admissao.frase({}) == ""
