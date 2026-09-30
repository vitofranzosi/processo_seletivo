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


def _secoes(conteudo):
    return {
        grupo["nome"]: grupo["campos"][0]["descricao"]
        for grupo in campos_editaveis(conteudo)
        if grupo.get("tipo") == "Seção"
    }


def test_a_secao_leva_o_numero_do_documento_e_o_estado_vai_para_o_campo():
    conteudo = _com_textos(
        apresentacao="A Diretora faz saber.",
        **{"publico-alvo": "Graduados.", "matricula": "Na secretaria."},
    )
    numeros = numeracao(conteudo)
    secoes = _secoes(conteudo)

    assert numeros["matricula"] != 16, "o cenário precisa de número diferente da ordem"
    assert secoes[f"{numeros['matricula']} — Da Matrícula"] == (
        f"sai no documento como a seção {numeros['matricula']}"
    )
    assert secoes["Apresentação"] == "sai como preâmbulo, sem número"
    assert secoes["Do Certificado"] == "vazia, e não sai no documento"
    assert not any(nome.startswith("16 — ") for nome in secoes)


def test_o_nome_da_secao_nao_carrega_estado():
    """Code review do PR 233: o título do grupo é reusado fora da tela — no resumo da confirmação
    e nas pendências da Revisão —, e "vazia" nele rotularia assim a seção que se preenche."""
    titulos = [
        grupo["titulo"] for grupo in campos_editaveis(_com_textos()) if grupo.get("tipo") == "Seção"
    ]
    assert "Seção Do Certificado" in titulos
    assert not any("vazia" in titulo or "preâmbulo" in titulo for titulo in titulos)
