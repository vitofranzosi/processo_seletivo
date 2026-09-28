"""O fundamento derivado: a norma e os atos que sustentam a chamada, por extenso (050, `D-009`)."""

import re

import pytest

from processo_seletivo.convocacao.domain import fundamento, nomes

ARGUMENTOS = {"edital": "Edital nº 28/2026", "recorte": "Polo Vitória, ampla concorrência"}


@pytest.mark.parametrize("especie", nomes.ESPECIES_DE_CONVOCACAO)
def test_cada_especie_tem_texto_que_cita_o_edital_o_recorte_e_a_apuracao(especie):
    texto = fundamento.da_convocacao(especie=especie, data_da_apuracao="28/09/2026", **ARGUMENTOS)

    assert "Edital nº 28/2026" in texto
    assert "Polo Vitória, ampla concorrência" in texto
    assert "28/09/2026" in texto


def test_as_tres_especies_dizem_tres_coisas_diferentes():
    textos = {
        fundamento.da_convocacao(especie=especie, data_da_apuracao="x", **ARGUMENTOS)
        for especie in nomes.ESPECIES_DE_CONVOCACAO
    }
    assert len(textos) == 3


def test_o_complemento_vem_depois_e_nunca_no_lugar():
    texto = fundamento.com_complemento("Base.", "No interesse da Administração.")

    assert texto == "Base. Complemento: No interesse da Administração."


def test_complemento_em_branco_nao_deixa_rastro():
    assert fundamento.com_complemento("Base.", "   ") == "Base."


@pytest.mark.parametrize(
    "texto",
    [
        *(
            fundamento.da_convocacao(especie=especie, data_da_apuracao="x", **ARGUMENTOS)
            for especie in nomes.ESPECIES_DE_CONVOCACAO
        ),
        fundamento.do_nao_atendimento(**ARGUMENTOS),
    ],
)
def test_o_texto_nao_promete_vaga_nem_afirma_recebimento(texto):
    """A frase vai para um ato append-only e para a tela: o vocabulário da `019` vale para ela."""
    for proibido in (r"direito [àa] vaga", r"vaga garantida", r"recebid[oa] em", r"lid[oa] em"):
        assert not re.search(proibido, texto.lower())
