"""Invariantes da Etapa de Avaliação (FR-019 a FR-022).

Elas vivem no domínio, e não no serializer, porque a interface administrativa invoca o command
diretamente: validar só na API deixaria sem verificação justamente o canal onde o dado é digitado.
"""

from decimal import Decimal

import pytest

from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stages

EVENTO = "00000000-0000-0000-0000-000000000701"
OUTRO_EVENTO = "00000000-0000-0000-0000-000000000702"

CRONOGRAMA = [{"id": EVENTO, "type": "INSCRICAO", "order": 1}]


def etapa(**alteracoes):
    base = {
        "id": "00000000-0000-0000-0000-000000000801",
        "name": "Prova didática",
        "order": 1,
        "weight": None,
        "eliminatory": False,
        "classificatory": True,
        "minimumScore": None,
        "scheduleEventId": None,
    }
    return {**base, **alteracoes}


def test_sem_etapa_nenhuma_e_valido():
    """Etapas são opcionais: nem todo certame as declara nesta versão do Edital."""
    validate_stages([], schedule=CRONOGRAMA)


def test_etapa_completa_e_valida():
    validate_stages(
        [etapa(weight=Decimal("2.0000"), minimumScore=Decimal("7"), scheduleEventId=EVENTO)],
        schedule=CRONOGRAMA,
    )


def test_etapa_pode_ser_eliminatoria_e_classificatoria_ao_mesmo_tempo():
    """FR-019: nenhuma regra as opõe, e opô-las seria inventar regra de certame."""
    validate_stages([etapa(eliminatory=True, classificatory=True)], schedule=CRONOGRAMA)


@pytest.mark.parametrize("nome", ["", "   "])
def test_etapa_sem_nome_e_recusada(nome):
    with pytest.raises(StageValidationError, match="exige nome"):
        validate_stages([etapa(name=nome)], schedule=CRONOGRAMA)


@pytest.mark.parametrize("peso", [Decimal("0"), Decimal("-1")])
def test_peso_zero_ou_negativo_e_recusado(peso):
    """FR-020: peso zero afirmaria uma ponderação que não pondera.

    A ausência é que exprime "esta Etapa não pondera" — pelo mesmo raciocínio do percentual da
    Regra Normativa.
    """
    with pytest.raises(StageValidationError, match="maior que zero"):
        validate_stages([etapa(weight=peso)], schedule=CRONOGRAMA)


def test_nota_minima_negativa_e_recusada():
    with pytest.raises(StageValidationError, match="não pode ser negativa"):
        validate_stages([etapa(minimumScore=Decimal("-0.5"))], schedule=CRONOGRAMA)


def test_nota_minima_zero_e_aceita():
    """Zero é nota mínima legítima; é o peso que não pode ser zero."""
    validate_stages([etapa(minimumScore=Decimal("0"))], schedule=CRONOGRAMA)


def test_referencia_a_evento_inexistente_e_recusada():
    with pytest.raises(StageValidationError, match="não existe no Cronograma"):
        validate_stages([etapa(scheduleEventId=OUTRO_EVENTO)], schedule=CRONOGRAMA)


def test_referencia_e_conferida_contra_o_cronograma_da_mesma_gravacao():
    """FR-022 e o caso de borda da spec: o vínculo não sobrevive ao Evento que o sustenta.

    `replace_draft` substitui o rascunho inteiro. Um Evento removido no mesmo POST já não existe,
    e conferir contra o banco aprovaria um vínculo que a gravação está prestes a quebrar.
    """
    with pytest.raises(StageValidationError, match="não existe no Cronograma"):
        validate_stages([etapa(scheduleEventId=EVENTO)], schedule=[])


def test_etapas_nao_repetem_identidade():
    with pytest.raises(StageValidationError, match="repetir identidade"):
        validate_stages([etapa(), etapa(order=2)], schedule=CRONOGRAMA)


def test_etapas_nao_repetem_ordem():
    outra = etapa(id="00000000-0000-0000-0000-000000000802", name="Títulos")
    with pytest.raises(StageValidationError, match="repetir ordem"):
        validate_stages([etapa(), outra], schedule=CRONOGRAMA)


# ------------------------------------------ a aplicabilidade por forma (012, FR-119, FR-121)


def _publicada(**extra):
    """Uma Etapa na forma do conteúdo publicado, com todas as chaves presentes."""
    return {
        "id": "00000000-0000-0000-0000-0000000000a1",
        "name": "Análise documental",
        "order": 1,
        "weight": None,
        "eliminatory": True,
        "classificatory": False,
        "minimumScore": None,
        "evaluationsPerRegistration": 1,
        "maximumScore": None,
        "forma": "PONTUADA",
        "rotuloFavoravel": None,
        "rotuloDesfavoravel": None,
        "scheduleEventId": None,
        **extra,
    }


def _recusas(etapa):
    from processo_seletivo.editais.domain.validation import validate_for_publication

    achados = validate_for_publication({"schemaVersion": 6, "stages": [etapa]})
    return {achado.path: achado.message for achado in achados if achado.path.startswith("/stages")}


def test_a_decisoria_sem_rotulo_e_recusada():
    caminhos = _recusas(_publicada(forma="DECISORIA"))

    assert any("rotuloFavoravel" in caminho for caminho in caminhos)
    assert any("rotuloDesfavoravel" in caminho for caminho in caminhos)


def test_a_decisoria_com_nota_e_recusada():
    """Publicar máxima numa Etapa que não pontua é a regra fictícia que P-007 impede."""
    caminhos = _recusas(
        _publicada(
            forma="DECISORIA",
            rotuloFavoravel="Deferido",
            rotuloDesfavoravel="Indeferido",
            minimumScore="60.0000",
            maximumScore="100.0000",
        )
    )

    assert any("minimumScore" in caminho for caminho in caminhos)
    assert any("maximumScore" in caminho for caminho in caminhos)


def test_a_pontuada_com_rotulo_e_recusada():
    caminhos = _recusas(_publicada(rotuloFavoravel="Deferido"))

    assert any("rotuloFavoravel" in caminho for caminho in caminhos)


def test_a_pontuada_sem_nota_nenhuma_e_legitima():
    """Limite não declarado é o que FR-066 chama de ausência, e não falta."""
    assert _recusas(_publicada()) == {}


def test_rotulo_em_branco_nao_conta_como_publicado():
    caminhos = _recusas(
        _publicada(forma="DECISORIA", rotuloFavoravel="   ", rotuloDesfavoravel="Indeferido")
    )

    assert any("rotuloFavoravel" in caminho for caminho in caminhos)


def test_forma_fora_do_par_e_recusada():
    caminhos = _recusas(_publicada(forma="ORDINAL"))

    assert any("forma" in caminho for caminho in caminhos)
