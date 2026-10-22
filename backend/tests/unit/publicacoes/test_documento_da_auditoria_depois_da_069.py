"""O que a `069` mudou nos documentos da auditoria — e o que ela não pode ter perdido (SC-516).

O "antes" é o documento que a `068` gravou (`specs/068-…/demonstracao/`), que era a `main` antes
desta feature; o "agora", o que a `069` gravou (`specs/069-…/demonstracao/`), com os snapshots
congelados levados ao catálogo novo (`levado_ao_catalogo_novo`) e o mesmo contexto do ato.

A `069` reorganiza o documento inteiro — redação, ordem, seções reunidas —, e por isso a prova não é
"o texto fora de tal seção é o mesmo", como na `068`. É a **cobertura de fatos**: cada data, hora,
número por extenso, percentual, código, fundamento, Anexo, localidade, documento, o e-mail e o hash
do documento de antes estão no de agora. A equivalência das regras, enunciado por enunciado, está em
`specs/069-…/demonstracao/equivalencia.md` (FR-1396, SC-517).
"""

import re

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import (
    congelado,
    por_perguntas,
    variante_de_b,
)
from tests.unit.publicacoes.test_documento_da_auditoria_depois_da_068 import da_068
from tests.unit.publicacoes.test_itens_do_documento import RAIZ
from tests.unit.publicacoes.test_pdf import texto_de

DEMONSTRACAO_069 = RAIZ / "specs" / "069-edital-linguagem-simples" / "demonstracao"

COMPOSTOS = {
    "A-publicado-069.pdf": lambda: por_perguntas("A"),
    "B-publicado-069.pdf": lambda: por_perguntas("B"),
    "B-variante-069.pdf": lambda: por_perguntas("B", variante_de_b()),
}

# Os fatos que o documento afirma e que nenhuma reorganização pode perder (SC-516).
FATOS = {
    "data": r"\d{2}/\d{2}/\d{4}",
    "hora": r"\b\d{1,2}h(?:\d{2})?\b",
    "número com extenso": r"\b\d+ \([a-zçãâéêíóú ]+\)",
    "percentual": r"\b\d+(?:,\d+)?%",
    "código": r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b",
    "e-mail": r"[\w.]+@[\w.]+\.\w+",
    "hash": r"\b[0-9a-f]{64}\b",
    "fundamento": r"(?:Resolução|Lei|Portaria|Decreto)[^,;.]*?\d+/\d{4}",
    "Anexo": r"ANEXO [IVX]+",
}


def da_069(nome):
    return (DEMONSTRACAO_069 / nome).read_bytes()


def _corrido(documento):
    return " ".join(texto_de(documento).split())


def _em_ordem(palavras, tokens):
    restantes = iter(tokens)
    return all(any(token == palavra for token in restantes) for palavra in palavras)


# Os do B mudaram de propósito na `096` (o `CR` dos tutores presenciais e a nota), e o composto
# agora é comparado com os que ela gravou; os da `069` continuam onde estão, como evidência, e os
# testes de cobertura abaixo os leem. O que mudou entre os dois é preso por
# `test_documento_da_auditoria_depois_da_096.py`.
DEMONSTRACAO_096 = RAIZ / "specs" / "096-cadastro-de-reserva-como-cr" / "demonstracao"


def gravado_agora(nome):
    if nome.startswith("B-"):
        return (DEMONSTRACAO_096 / nome.replace("-069.pdf", "-096.pdf")).read_bytes()
    return da_069(nome)


@pytest.mark.parametrize("nome", sorted(COMPOSTOS))
def test_o_documento_sai_com_os_bytes_gravados(nome):
    """Os PDFs da demonstração são os que o compositor faz agora — determinísticos (SC-523)."""
    assert COMPOSTOS[nome]() == gravado_agora(nome)


@pytest.mark.parametrize("cenario", ["A", "B"])
@pytest.mark.parametrize("fato", sorted(FATOS))
def test_todo_fato_de_antes_esta_no_documento_novo(cenario, fato):
    antes = set(re.findall(FATOS[fato], _corrido(da_068(cenario))))
    depois = set(re.findall(FATOS[fato], _corrido(da_069(f"{cenario}-publicado-069.pdf"))))
    assert antes, f"o cenário {cenario} precisa ter {fato}"
    assert antes <= depois, sorted(antes - depois)


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_localidades_documentos_e_perfis_estao_todos(cenario):
    conteudo = congelado(cenario)["content"]
    texto = _corrido(da_069(f"{cenario}-publicado-069.pdf"))
    for perfil in conteudo["profiles"]:
        assert perfil["code"] in texto
        # Numa célula de tabela a localidade longa reflui, e o extrator intercala as colunas: o que
        # se confere é que todas as palavras dela estão lá, na ordem.
        assert _em_ordem(perfil["locality"].split(), texto.split()), perfil["locality"]
    for documento in conteudo["documentRequirements"]:
        assert " ".join(documento["name"].split()) in texto, documento["name"]


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_os_rotulos_internos_e_a_descricao_sairam(cenario):
    """FR-1360, FR-1366, FR-1378: os pares viraram frase; a descrição não é do ato."""
    texto = _corrido(da_069(f"{cenario}-publicado-069.pdf"))
    for rotulo in (
        "Ordem:",
        "Combinação:",
        "Normalização:",
        "Habilitação:",
        "Corte:",
        "Continuação:",
        "Marcos classificatórios",
        "INTEGRIDADE",
    ):
        assert rotulo not in texto, rotulo
    descricao = " ".join(congelado(cenario)["content"]["description"].split())
    assert descricao not in texto


@pytest.mark.parametrize(
    ("trecho", "antes"),
    [
        ("IFES-SORTEIO-SHA256-v1", 1),
        ("Participam do sorteio todas as inscrições enviadas.", 1),
        ("Não havendo extração na data prevista", 1),
    ],
)
def test_em_a_o_que_e_comum_sai_uma_vez(trecho, antes):
    assert _corrido(da_069("A-publicado-069.pdf")).count(trecho) == antes


def test_a_apresentacao_dos_tres_e_por_perguntas():
    for nome in COMPOSTOS:
        texto = texto_de(da_069(nome))
        assert "Resumo deste Edital" in texto
        assert re.search(r"^\d+\. Como será a seleção\?$", texto, re.M)
        assert pdf.MARCA_DE_PREVIA not in texto
