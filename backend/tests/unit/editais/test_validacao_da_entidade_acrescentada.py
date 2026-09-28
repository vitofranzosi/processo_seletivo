"""A Modalidade e o critério que uma Retificação acrescenta valem o que a composição exigiria (048).

As frases são as da composição, e por isso os casos as comparam: uma recusa que dissesse outra
coisa na Retificação seria uma segunda regra com o mesmo nome.
"""

import pytest

from processo_seletivo.editais.domain.perfis import (
    CRITERIO_COM_ORDEM_REPETIDA,
    CRITERIO_SEM_ALVO,
    CRITERIO_SEM_COMPORTAMENTO_NA_AUSENCIA,
    MODALIDADE_REPETIDA,
    ProfileValidationError,
    validar_criterio,
    validar_modalidade,
    validate_classification_milestones,
    validate_profile,
)


def modalidade(**alteracoes):
    base = {
        "id": "m-nova",
        "code": "AC",
        "name": "Ampla concorrência",
        "description": "",
        "normativeRule": None,
    }
    return {**base, **alteracoes}


def regra(**alteracoes):
    base = {"id": "r-nova", "foundation": "Lei 12.711/2012", "version": "2023", "percentage": "20"}
    return {**base, **alteracoes}


def criterio(**alteracoes):
    base = {
        "id": "c-novo",
        "order": 2,
        "type": "MAIOR_PONTUACAO_NA_ETAPA",
        "parameters": {"stageId": "etapa-1"},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    }
    return {**base, **alteracoes}


def test_a_modalidade_completa_passa():
    validar_modalidade(modalidade(), codigos_do_perfil={"PPI", "PCD"})
    validar_modalidade(modalidade(code="EP", normativeRule=regra()), codigos_do_perfil={"AC"})


def test_codigo_repetido_e_recusado_com_a_frase_da_composicao():
    with pytest.raises(ProfileValidationError) as recusa:
        validar_modalidade(modalidade(code="PPI"), codigos_do_perfil={"PPI"})
    assert MODALIDADE_REPETIDA in str(recusa.value)
    assert "PPI" in str(recusa.value)
    assert recusa.value.campo == "code"


def test_a_composicao_recusa_o_mesmo_codigo_com_a_mesma_frase():
    perfil = {
        "immediateVacancies": 1,
        "reserveType": "NONE",
        "reserveLimit": None,
        "competitionModalities": [{"code": "PPI"}, {"code": "PPI"}],
    }
    with pytest.raises(ProfileValidationError, match=MODALIDADE_REPETIDA):
        validate_profile(perfil)


@pytest.mark.parametrize(
    ("alteracoes", "campo"),
    [
        ({"code": ""}, "code"),
        ({"name": "  "}, "name"),
        ({"normativeRule": regra(foundation="")}, "foundation"),
        ({"normativeRule": regra(version="")}, "version"),
    ],
)
def test_a_forma_que_o_serializer_exigia_e_exigida(alteracoes, campo):
    with pytest.raises(ProfileValidationError) as recusa:
        validar_modalidade(modalidade(**alteracoes), codigos_do_perfil=set())
    assert recusa.value.campo == campo


def test_o_percentual_fora_da_faixa_tem_a_frase_da_regra_normativa():
    with pytest.raises(ProfileValidationError, match="maior que zero"):
        validar_modalidade(modalidade(normativeRule=regra(percentage="0")), codigos_do_perfil=set())


def test_o_criterio_completo_passa():
    validar_criterio(criterio(), ordens_do_marco={1})
    validar_criterio(
        criterio(type="MENOR_VALOR_DE_FATO", parameters={"factId": "idade"}),
        ordens_do_marco=set(),
    )


def test_ordem_repetida_tem_a_frase_da_composicao():
    with pytest.raises(ProfileValidationError, match="compartilhar a mesma ordem"):
        validar_criterio(criterio(order=1), ordens_do_marco={1})
    marco = {
        "code": "M1",
        "stages": ["etapa-1"],
        "tiebreakers": [criterio(order=1), criterio(id="outro", order=1)],
    }
    with pytest.raises(ProfileValidationError) as da_composicao:
        validate_classification_milestones([marco])
    assert str(da_composicao.value) == CRITERIO_COM_ORDEM_REPETIDA


def test_a_ordem_do_criterio_removido_pode_ser_reusada():
    """Remover um critério e acrescentar outro na mesma posição é a troca que a US4 permite: quem
    chama passa só as ordens dos que **continuam**."""
    validar_criterio(criterio(order=1), ordens_do_marco=set())


@pytest.mark.parametrize("ordem", [0, -1, None, "1", True])
def test_a_ordem_e_inteiro_a_partir_de_um(ordem):
    with pytest.raises(ProfileValidationError) as recusa:
        validar_criterio(criterio(order=ordem), ordens_do_marco=set())
    assert recusa.value.campo == "order"


def test_tipo_fora_do_vocabulario_e_recusado():
    with pytest.raises(ProfileValidationError) as recusa:
        validar_criterio(criterio(type="SORTE"), ordens_do_marco=set())
    assert recusa.value.campo == "type"


def test_o_alvo_tem_de_ser_o_do_tipo():
    """Um critério por Etapa com parâmetro de fato não compara nada: a composição recusaria."""
    with pytest.raises(ProfileValidationError, match=CRITERIO_SEM_ALVO):
        validar_criterio(criterio(parameters={"factId": "idade"}), ordens_do_marco=set())
    with pytest.raises(ProfileValidationError, match=CRITERIO_SEM_ALVO):
        validar_criterio(
            criterio(type="MAIOR_VALOR_DE_FATO", parameters={"stageId": "etapa-1"}),
            ordens_do_marco=set(),
        )


@pytest.mark.parametrize("comportamento", [None, "", "ZERO"])
def test_o_comportamento_na_ausencia_e_declarado_e_do_vocabulario(comportamento):
    with pytest.raises(ProfileValidationError) as recusa:
        validar_criterio(criterio(whenMissing=comportamento), ordens_do_marco=set())
    assert str(recusa.value) == CRITERIO_SEM_COMPORTAMENTO_NA_AUSENCIA
