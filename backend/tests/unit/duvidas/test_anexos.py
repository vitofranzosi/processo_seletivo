"""Anexos pelo vínculo e pela citação do rótulo; nada sobre o que contêm (`R-012`, T032)."""

import copy

from processo_seletivo.duvidas.domain import anexos
from tests.fixtures.corpus import conteudo


def test_92_cita_o_anexo_iv_no_nome_da_etapa_e_na_instrucao():
    publicado = conteudo("92", 2)
    etapa = publicado["stages"][0]["name"]
    instrucao = next(
        d["instructions"]
        for d in publicado["documentRequirements"]
        if d["name"] == "Documentos passíveis de pontuação"
    )
    encontrados, inexistentes = anexos.resolver([etapa, instrucao], publicado)
    assert [a["label"] for a in encontrados] == [
        "ANEXO IV — FICHA DE AVALIAÇÃO DA PROVA DE TÍTULOS"
    ]
    assert inexistentes == ()


def test_91_cita_o_anexo_i_na_instrucao_da_autodeclaracao():
    publicado = conteudo("91", 2)
    instrucao = next(
        d["instructions"]
        for d in publicado["documentRequirements"]
        if d["name"] == "Autodeclaração étnico-racial"
    )
    encontrados, _ = anexos.resolver([instrucao], publicado)
    assert [a["label"] for a in encontrados] == ["ANEXO I — MODELO DE AUTODECLARAÇÃO ÉTNICO-RACIAL"]


def test_anexo_citado_que_nao_existe_e_devolvido_para_revisao():
    publicado = copy.deepcopy(conteudo("91", 2))
    encontrados, inexistentes = anexos.resolver(["Conforme o Anexo IX deste Edital."], publicado)
    assert encontrados == ()
    assert inexistentes == ("ix",)


def test_anexo_sem_identificador_nao_e_citacao():
    # 01/2026: "Conforme o modelo do Anexo do Edital." — não diz qual.
    assert anexos.citados("Conforme o modelo do Anexo do Edital.") == ()
    assert anexos.citados("O anexo mencionado no item anterior.") == ()


def test_a_citacao_pede_romano_valido_e_ignora_o_anexo_de_outra_norma():
    """Revisão de 12/10: os falsos positivos e negativos da citação."""
    assert anexos.citados("o anexo civil do contrato") == ()
    assert anexos.citados("Anexo I do Decreto nº 9.508/2018") == ()
    assert anexos.citados("conforme os Anexos III e IV") == ("iii", "iv")
    assert anexos.citados("Anexos I, II e V deste Edital") == ("i", "ii", "v")
    assert anexos.citados("ver o Anexo 04") == ("4",)
    assert anexos.citados("Anexo IV — ficha") == ("iv",)
