"""A numeração apresentada: uma regra, consciente da apresentação, lida por todos (069, R-003).

Na apresentação por perguntas, `numeracao` devolve "N" para a seção e "N.k" para a chave que sai
como subseção; `itens_do_documento` e `tabelas_do_documento` dizem o que a composição escreve. Na
plana — os Editais publicados antes e os consolidados deles — os números são os de sempre: inteiros,
um por seção que sai (FR-1394, FR-1399).

O guardião que compõe o documento de verdade e compara os itens com o que ele escreve, nas duas
apresentações, é `test_itens_do_documento.py`; aqui se afirma a forma e os casos de presença.
"""

import re

import pytest

from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.editais.domain.validation import _DESCRICAO_DO_ITEM
from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.test_pdf import secoes, snapshot
from tests.unit.publicacoes.test_pdf_classificacao import ETAPAS, marco


def _por_perguntas(**alteracoes):
    return snapshot(sections=secoes(catalogo_=catalogo.CATALOGO_DA_069), **alteracoes)


def _esvaziar(conteudo, *chaves):
    for secao in conteudo["sections"]:
        if secao["key"] in chaves:
            secao["content"] = ""
    return conteudo


def _com_marco(conteudo, **alteracoes):
    perfil = conteudo["profiles"][0]
    perfil["classificationMilestones"] = [marco(**alteracoes)]
    conteudo["stages"] = ETAPAS
    return conteudo


def test_por_perguntas_a_secao_e_n_e_a_chave_reunida_e_n_k():
    numeros = pdf.numeracao(_por_perguntas())
    assert numeros["apresentacao"] == 0
    assert numeros["disposicoes-preliminares"] == "1"
    assert numeros["informacoes-gerais"] == "2"
    assert (numeros["publico-alvo"], numeros["requisitos-gerais"]) == ("3.1", "3.2")
    assert numeros["perfis"] == "4"
    assert numeros["cronograma"] == "5"
    assert (numeros["inscricao"], numeros["atendimento-pcd"]) == ("6", "6.1")
    assert numeros["classificacao"] == "7"
    assert numeros["recursos"] == "8"
    assert numeros["matricula"] == "10"
    assert (numeros["acesso-ao-curso"], numeros["homologacao-matricula"]) == ("10.1", "10.2")
    assert numeros["disposicoes-finais"] == "13"


def test_na_plana_os_numeros_sao_os_de_sempre():
    """FR-1394, FR-1399: o Edital publicado antes mostra, nas telas, os números do PDF dele."""
    numeros = pdf.numeracao(snapshot())
    assert numeros["apresentacao"] == 0
    assert numeros["disposicoes-preliminares"] == 1
    assert numeros["perfis"] == 5
    assert numeros["inscricao"] == 6
    assert numeros["disposicoes-finais"] == 19
    assert all(isinstance(numero, int) for numero in numeros.values() if numero is not None)


def test_a_mesma_regra_na_numeracao_impressa():
    for conteudo in (_por_perguntas(), snapshot()):
        assert pdf.numeracao_impressa(conteudo) == pdf.numeracao(conteudo)


def test_a_textual_vazia_nao_sai_e_nao_abre_buraco():
    numeros = pdf.numeracao(_esvaziar(_por_perguntas(), "publico-alvo", "informacoes-gerais"))
    assert numeros["publico-alvo"] is None
    assert numeros["informacoes-gerais"] is None
    assert numeros["requisitos-gerais"] == "2.1", "a reunida vira a primeira subseção"
    assert numeros["perfis"] == "3"


def test_a_textual_so_com_invisivel_nao_sai_na_numeracao_impressa():
    conteudo = _por_perguntas()
    for secao in conteudo["sections"]:
        if secao["key"] == "informacoes-gerais":
            secao["content"] = "​"
    assert pdf.numeracao_impressa(conteudo)["informacoes-gerais"] is None
    assert pdf.numeracao_impressa(conteudo)["publico-alvo"] == "2.1"


def test_a_secao_que_so_tem_norma_do_sistema_sai():
    """ "Como recorrer?" sem texto de quem redigiu, mas com o recurso de um marco, sai."""
    conteudo = _com_marco(
        _esvaziar(_por_perguntas(), "recursos"),
        appealWindow={"admits": True, "durationDays": 2, "unit": "DIAS_UTEIS"},
    )
    plano = pdf._apresentacao().plano(conteudo)
    assert plano.numero_da("Como recorrer?")
    # A chave principal tem o número da seção que sai: é onde o texto dela sairia (UX-132).
    assert pdf.numeracao(conteudo)["recursos"] == plano.numero_da("Como recorrer?")


def test_a_secao_sem_nada_a_dizer_nao_sai():
    conteudo = _esvaziar(_por_perguntas(), "publico-alvo", "requisitos-gerais")
    conteudo["profiles"][0]["requirements"] = []
    plano = pdf._apresentacao().plano(conteudo)
    assert plano.numero_da("Quem pode se inscrever?") == ""
    assert "Quem pode se inscrever?" not in {
        item.descricao for item in pdf.itens_do_documento(conteudo)
    }


def test_os_itens_por_perguntas_sao_secoes_e_subsecoes():
    conteudo = _com_marco(_por_perguntas())
    itens = pdf.itens_do_documento(conteudo)
    por_numero = {item.numero: item for item in itens}
    assert por_numero["3"].descricao == "Quem pode se inscrever?"
    assert (por_numero["3.1"].natureza, por_numero["3.1"].descricao) == ("subsecao", "Público-alvo")
    assert por_numero["3.3"].descricao == "Requisitos dos Perfis"
    selecao = [item for item in itens if item.numero.startswith(f"{por_numero['7'].numero}.")]
    assert [item.descricao for item in selecao] == [
        "Classificação",
        "Prova didática",
        "Análise de títulos",
        "Verificação da autodeclaração",
    ]
    assert [item.natureza for item in selecao] == ["subsecao", "etapa", "etapa", "subsecao"]


def test_os_itens_da_plana_sao_os_de_sempre():
    itens = pdf.itens_do_documento(snapshot())
    assert all("." not in item.numero for item in itens if item.natureza == "secao")
    assert {item.natureza for item in itens} <= {"secao", "perfil", "etapa"}
    assert "subsecao" not in {item.natureza for item in itens}


@pytest.mark.parametrize("apresentacao", ["por perguntas", "plana"])
def test_a_contagem_de_tabelas_e_a_da_composicao(apresentacao):
    conteudo = _por_perguntas() if apresentacao == "por perguntas" else snapshot()
    texto = pdf.render_edital_pdf(
        conteudo,
        "a" * 64,
        pdf.MODO_PREVIA,
        unidade=pdf.UnidadeDoAto(cabecalho=("Centro",), local="Vitória (ES)"),
    ).decode("latin-1")
    # A legenda como o fluxo a desenha: "Tabela N — ", com o travessão em WinAnsi.
    legendas = {int(numero) for numero in re.findall(r"\(Tabela (\d+) \x97 ", texto)}
    assert legendas, "o caso precisa ter tabela, ou a igualdade não prova nada"
    assert pdf.tabelas_do_documento(conteudo) == len(legendas)


@pytest.mark.parametrize("apresentacao", ["por perguntas", "plana"])
def test_toda_natureza_de_item_tem_descricao_na_conferencia(apresentacao):
    """Uma natureza desconhecida derrubava a conferência com `KeyError` (R-003)."""
    conteudo = _com_marco(_por_perguntas() if apresentacao == "por perguntas" else snapshot())
    for item in pdf.itens_do_documento(conteudo):
        assert item.natureza in _DESCRICAO_DO_ITEM, item
