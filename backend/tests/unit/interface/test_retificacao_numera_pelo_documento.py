"""A tela da Retificação numera a seção pelo documento (054, FR-985; code review do PR 233).

A etapa Conteúdo e a Revisão passaram a usar `pdf.numeracao`; a Retificação continuava pela `order`
do catálogo, e dizia "16 — Da Matrícula" para a seção que o PDF que se retifica imprime como "11".
"""

from processo_seletivo.interface.retificacao import campos_editaveis
from processo_seletivo.publicacoes.infrastructure.pdf import numeracao
from tests.unit.publicacoes.test_pdf import snapshot


def _com_textos(**textos):
    conteudo = snapshot()
    for secao in conteudo["sections"]:
        if secao["type"] == "TEXT":
            secao["content"] = textos.get(secao["key"], "")
    return conteudo


def _nomes_das_secoes(conteudo):
    return {grupo["nome"] for grupo in campos_editaveis(conteudo) if grupo.get("tipo") == "Seção"}


def test_a_secao_leva_o_numero_do_documento_e_a_vazia_diz_que_nao_sai():
    conteudo = _com_textos(
        apresentacao="A Diretora faz saber.",
        **{"publico-alvo": "Graduados.", "matricula": "Na secretaria."},
    )
    numeros = numeracao(conteudo)
    nomes = _nomes_das_secoes(conteudo)

    assert f"{numeros['matricula']} — Da Matrícula" in nomes
    assert numeros["matricula"] != 16, "o cenário precisa de número diferente da ordem"
    assert "Apresentação (preâmbulo)" in nomes
    assert "Do Certificado (vazia — não sai no documento)" in nomes
    assert not any(nome.startswith("16 — ") for nome in nomes)
