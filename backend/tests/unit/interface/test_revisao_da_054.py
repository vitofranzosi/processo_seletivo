"""A Revisão diz por que a seção não sai (054, FR-985; code review do PR 233)."""

from processo_seletivo.interface import revisao
from tests.unit.publicacoes.test_pdf import snapshot


def _linhas_da_conferencia(conteudo):
    bloco = next(bloco for bloco in revisao.blocos(conteudo) if bloco["etapa"] == "conteudo")
    return {item["titulo"]: item["linhas"] for item in bloco["itens"]}


def test_a_gerada_que_nao_sai_diz_de_onde_viria():
    conteudo = snapshot(stages=[])
    linhas = _linhas_da_conferencia(conteudo)
    assert linhas["Etapas de Avaliação"] == ["Nada cadastrado em Etapas — não sai no documento."]


def test_a_textual_vazia_diz_que_nao_sai():
    conteudo = snapshot()
    for secao in conteudo["sections"]:
        if secao["key"] == "certificado":
            secao["content"] = ""
    linhas = _linhas_da_conferencia(conteudo)
    assert linhas["Do Certificado"] == ["Vazia — não sai no documento."]
