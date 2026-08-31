"""O que a publicação recusa no contrato de inscrição, e o que ela apenas avisa (US2 da 009).

A elaboração já recusa o incoerente, e o banco garante um período por Cronograma. Nenhuma das
duas alcança o conteúdo que **passa a vigorar**: duas Retificações sucessivas produzem o estado
que a interface impede, cada uma partindo de uma versão em que ele não existia. A publicação é
onde esse estado para.
"""

import pytest

from processo_seletivo.editais.domain.validation import Severity, validate_for_publication
from tests.fixtures.snapshot import DOCUMENTO, MODALIDADE, rascunho_completo

# Fora do conjunto de Perfis do construtor — que tem três, e todos os três são deste Edital.
PERFIL_DE_OUTRO_EDITAL = "00000000-0000-0000-0000-0000000009fe"


def _conteudo(**ajustes):
    base = rascunho_completo()
    base.update({"title": "Edital", "description": "Descrição"})
    base.update(ajustes)
    return base


def _codigos(conteudo, severidade):
    return [
        achado.code
        for achado in validate_for_publication(conteudo)
        if achado.severity == severidade
    ]


def test_dois_eventos_designados_produzem_achado_impeditivo():
    conteudo = _conteudo()
    for evento in conteudo["schedule"][:2]:
        evento["isRegistrationPeriod"] = True

    assert "registration_period_ambiguous" in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_um_evento_designado_nao_produz_achado():
    conteudo = _conteudo()
    conteudo["schedule"][0]["isRegistrationPeriod"] = True

    achados = validate_for_publication(conteudo)

    assert [a.code for a in achados if a.code.startswith("registration_period")] == []


def test_nenhum_evento_designado_e_aviso_e_nao_impedimento():
    """FR-004: nem todo Edital abre inscrição por este sistema, e isso não impede publicar."""
    conteudo = _conteudo()

    assert "registration_period_missing" in _codigos(conteudo, Severity.WARNING)
    assert "registration_period_missing" not in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_documento_restrito_a_perfil_inexistente_e_impeditivo():
    conteudo = _conteudo()
    conteudo["documentRequirements"][1]["profileId"] = PERFIL_DE_OUTRO_EDITAL

    assert "document_requirement_profile_unknown" in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_documento_restrito_a_modalidade_fora_do_alcance_e_impeditivo():
    conteudo = _conteudo()
    conteudo["documentRequirements"][0]["modalityId"] = "00000000-0000-0000-0000-0000000009ff"

    assert "document_requirement_modality_unknown" in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_modalidade_do_perfil_declarado_passa():
    conteudo = _conteudo()
    conteudo["documentRequirements"][1]["modalityId"] = MODALIDADE["A"]

    assert [
        codigo
        for codigo in _codigos(conteudo, Severity.BLOCKING_ERROR)
        if codigo.startswith("document_requirement")
    ] == []


@pytest.mark.parametrize("valor", ["texto", {"a": 1}, None])
def test_colecao_malformada_nao_faz_a_coerencia_explodir(valor):
    """Forma é assunto da declaração, que já reporta. A coerência ignora, e não levanta exceção."""
    conteudo = _conteudo(documentRequirements=valor)

    achados = validate_for_publication(conteudo)

    assert all(a.code != "document_requirement_profile_unknown" for a in achados)


def test_a_identidade_do_documento_e_a_declarada():
    conteudo = _conteudo()

    identidades = [documento["id"] for documento in conteudo["documentRequirements"]]

    assert identidades == [DOCUMENTO["A"], DOCUMENTO["B"]]
