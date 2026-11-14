"""O efeito do desfecho na gravação e na publicação (164, US1, FR-7002, contrato `recusas.md`).

Puro, sobre o conteúdo do exemplo da `163`: a Heteroidentificação restrita a `PPI`.
"""

import pytest

from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stage
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from tests.unit.editais.test_alcance_da_etapa import _conteudo, _etapa


def _codigos(conteudo):
    return sorted(
        achado.code
        for achado in blocking_findings(validate_for_publication(conteudo))
        if achado.code.startswith("efeito_")
    )


def test_a_etapa_restrita_e_eliminatoria_declara_efeito_sem_achado():
    etapa = _etapa(eliminatory=True, unfavorableOutcomeEffect="RESERVE_REMOVAL")

    assert _codigos(_conteudo(etapa=etapa)) == []


@pytest.mark.parametrize(
    "campos",
    [{"modalityCodes": None}, {"eliminatory": False}],
    ids=["para todas", "não eliminatória"],
)
def test_efeito_em_etapa_sem_reserva_impede_a_publicacao(campos):
    """FR-7002: a Etapa que volta a alcançar todas, ou deixa de eliminar, com o efeito escrito."""
    etapa = _etapa(**{"eliminatory": True, "unfavorableOutcomeEffect": "RESERVE_REMOVAL", **campos})

    assert _codigos(_conteudo(etapa=etapa)) == ["efeito_sem_reserva"]


def test_o_nulo_nao_e_achado():
    """FR-7005: `null` é "sem efeito declarado", em qualquer Etapa."""
    etapa = _etapa(modalityCodes=None, unfavorableOutcomeEffect=None, absenceEffect=None)

    assert _codigos(_conteudo(etapa=etapa)) == []


def test_a_gravacao_recusa_o_valor_fora_das_escolhas():
    with pytest.raises(StageValidationError) as recusa:
        validate_stage(_etapa(unfavorableOutcomeEffect="TALVEZ"), event_ids=frozenset())

    assert "não é um dos previstos" in str(recusa.value)
