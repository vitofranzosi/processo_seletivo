"""A leitura do efeito, a gravidade e as frases do documento (164, research T-003).

Função pura sobre a Etapa do conteúdo publicado, e por isso a tabela-verdade cabe aqui inteira.
"""

from types import SimpleNamespace

import pytest

from processo_seletivo.recursos.domain.pejus import piora
from processo_seletivo.resultados.domain import efeito
from processo_seletivo.resultados.domain.regra import consequencia
from processo_seletivo.resultados.models import ResultadoEtapa


def _etapa(**campos):
    return {
        "id": "e1",
        "name": "Heteroidentificação",
        "order": 2,
        "eliminatory": True,
        "forma": "DECISORIA",
        "rotuloFavoravel": "Confirmada",
        "rotuloDesfavoravel": "Não confirmada",
        "modalityCodes": ["PPI"],
        "unfavorableOutcomeEffect": "RESERVE_REMOVAL",
        "absenceEffect": None,
        **campos,
    }


def test_o_vocabulario_e_o_do_modelo():
    """Divergir do enum faria a retirada gravada passar despercebida por quem a lê."""
    assert efeito.RETIRADA_DA_RESERVA == ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA
    assert efeito.ELIMINADA == ResultadoEtapa.Consequencia.ELIMINADA
    assert efeito.HABILITADA == ResultadoEtapa.Consequencia.HABILITADA


def test_o_explicito_vale():
    assert efeito.efeito_desfavoravel(_etapa()) == efeito.RETIRA_DA_RESERVA
    assert efeito.efeito_desfavoravel(_etapa(unfavorableOutcomeEffect="ELIMINATION")) == (
        efeito.ELIMINA
    )


def test_o_nulo_do_acervo_restrito_e_eliminatorio_se_le_elimina():
    """FR-7001, D-002: o nulo publicado é o de antes do degrau 23, e eliminava."""
    assert efeito.efeito_desfavoravel(_etapa(unfavorableOutcomeEffect=None)) == efeito.ELIMINA


@pytest.mark.parametrize(
    "campos", [{"modalityCodes": None}, {"eliminatory": False}], ids=["para todas", "não elimina"]
)
def test_sem_reserva_nao_ha_efeito(campos):
    """FR-7002: a Etapa para todas, e a não eliminatória, não declaram efeito."""
    assert efeito.efeito_desfavoravel(_etapa(**campos)) is None
    assert efeito.efeito_da_ausencia(_etapa(**campos)) is None
    assert efeito.frase_do_efeito(_etapa(**campos)) == ""


def test_a_ausencia_tem_o_mesmo_efeito_pelo_padrao():
    """FR-7004: `null` na ausência é "o mesmo efeito"."""
    assert efeito.efeito_da_ausencia(_etapa()) == efeito.RETIRA_DA_RESERVA
    assert efeito.efeito_da_ausencia(_etapa(absenceEffect="ELIMINATION")) == efeito.ELIMINA


def test_a_publicacao_grava_o_padrao_so_onde_ha_reserva():
    """FR-7001, FR-7005: o vazio do rascunho vira "retira" na Etapa restrita; `null` nas demais."""
    assert efeito.publicar(_etapa(), "", "") == {
        "unfavorableOutcomeEffect": "RESERVE_REMOVAL",
        "absenceEffect": None,
    }
    assert efeito.publicar(_etapa(modalityCodes=None), "ELIMINA", "") == {
        "unfavorableOutcomeEffect": None,
        "absenceEffect": None,
    }


def test_a_regra_aplica_o_efeito_ao_desfavoravel():
    """FR-7007: a consequência sai da regra publicada, e nunca de quem consolida."""
    conclusao = SimpleNamespace(sentido="DESFAVORAVEL", pontuacao=None)

    assert consequencia(_etapa(), conclusao)[0] == efeito.RETIRADA_DA_RESERVA
    elimina = _etapa(unfavorableOutcomeEffect="ELIMINATION")
    assert consequencia(elimina, conclusao)[0] == efeito.ELIMINADA
    assert consequencia(_etapa(modalityCodes=None), conclusao)[0] == efeito.ELIMINADA


@pytest.mark.parametrize(
    ("desfavoravel", "ausencia", "frase"),
    [
        (
            "RESERVE_REMOVAL",
            None,
            "O candidato com resultado desfavorável ou que não comparecer deixa de concorrer "
            "pela reserva de vagas e continua concorrendo pela ampla concorrência.",
        ),
        (
            "ELIMINATION",
            None,
            "O candidato com resultado desfavorável ou que não comparecer é eliminado do "
            "processo seletivo.",
        ),
        (
            "RESERVE_REMOVAL",
            "ELIMINATION",
            "O candidato com resultado desfavorável deixa de concorrer pela reserva de vagas e "
            "continua concorrendo pela ampla concorrência. O candidato que não comparecer é "
            "eliminado do processo seletivo.",
        ),
    ],
)
def test_as_frases_do_documento(desfavoravel, ausencia, frase):
    """FR-7023: uma frase quando coincidem, uma por caso quando diferem."""
    etapa = _etapa(unfavorableOutcomeEffect=desfavoravel, absenceEffect=ausencia)
    assert efeito.frase_do_efeito(etapa) == frase


def _protegido(consequencia_):
    return SimpleNamespace(consequencia=consequencia_, pontuacao=None)


@pytest.mark.parametrize(
    ("antes", "depois", "piorou"),
    [
        ("RETIRADA_DA_RESERVA", "ELIMINADA", True),
        ("HABILITADA", "RETIRADA_DA_RESERVA", True),
        ("HABILITADA", "ELIMINADA", True),
        ("ELIMINADA", "RETIRADA_DA_RESERVA", False),
        ("RETIRADA_DA_RESERVA", "HABILITADA", False),
        ("ELIMINADA", "HABILITADA", False),
    ],
)
def test_a_vedacao_de_piora_segue_a_gravidade(antes, depois, piorou):
    """FR-7028: a retirada não vira eliminação por recurso; a eliminação por ausência pode virar
    retirada pela reavaliação."""
    assert piora(protegido=_protegido(antes), consequencia=depois, pontuacao=None) is piorou


def test_a_nota_menor_continua_piora_mesmo_com_consequencia_menos_grave():
    """FR-070 da `018`: a gravidade não dispensa a nota. Eliminada com 50 que viraria habilitada com
    40 — possível quando uma Retificação baixou a mínima — continua sendo piora na nota."""
    from decimal import Decimal

    protegido = SimpleNamespace(consequencia="ELIMINADA", pontuacao=Decimal("50"))

    assert piora(protegido=protegido, consequencia="HABILITADA", pontuacao=Decimal("40")) is True
    assert piora(protegido=protegido, consequencia="HABILITADA", pontuacao=Decimal("60")) is False
