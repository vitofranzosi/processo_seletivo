"""Nenhuma tela da formalização afirma o que o GPS não sabe, e todas cabem em 375 px (117).

**FR-3680, SC-1112.** O GPS sabe que serviu um arquivo e que gerou e disponibilizou um pacote. Não
sabe se o setor o recebeu, nem se a matrícula foi efetivada ou a bolsa concedida — e por isso as
telas não dizem *obtido*, *encaminhado*, *recebido*, *entregue*, *matriculado*, *matrícula
efetivada*, *bolsa concedida*, *vinculado* nem *contratado* (FR-3610 da `115`).

**A lista de telas é literal**, como nas outras varreduras: tela nova escaparia dela em silêncio.

**375 px** (FR-3680): a medida de `scrollWidth` mora na jornada do navegador
(`tests/navegador/test_jornada_da_formalizacao.py`); aqui fica o que a produz — nenhuma largura fixa
na folha da tela e a quebra dos textos sem espaço, como em `test_larguras.py`.
"""

import re
from pathlib import Path

import pytest

from tests.test_vocabulario_da_convocacao import visivel

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
TEMPLATES = RAIZ / "interface/templates/interface"
FOLHA = RAIZ / "interface/static/interface/telas/formalizacao.css"

DA_117 = [
    TEMPLATES / "formalizacao_lista.html",
    TEMPLATES / "formalizacao_edital.html",
    TEMPLATES / "formalizacao_verificacao.html",
    TEMPLATES / "formalizacao_recusa.html",
    TEMPLATES / "formalizacao_definicao.html",
    TEMPLATES / "_formalizacao_historico.html",
    TEMPLATES / "acessos_formalizacao.html",
]

PROIBIDOS = (
    r"obtid[oa]s?",
    r"encaminhad[oa]s?",
    r"recebid[oa]s?",
    r"entregues?",
    r"matriculad[oa]s?",
    r"matr[íi]cula efetivada",
    r"bolsa concedida",
    r"vinculad[oa]s?",
    r"contratad[oa]s?",
)


@pytest.mark.parametrize("caminho", DA_117, ids=lambda item: item.name)
def test_nenhuma_tela_afirma_o_que_o_gps_nao_sabe(caminho):
    corpo = visivel(caminho).lower()
    achados = [termo for termo in PROIBIDOS if re.search(rf"\b{termo}\b", corpo)]
    assert achados == [], f"{caminho.name}: {achados}"


def test_os_rotulos_e_as_frases_do_dominio_tambem_nao():
    from processo_seletivo.formalizacao.application import definir, exportar
    from processo_seletivo.formalizacao.domain import nomes

    textos = [
        *nomes.ROTULO_DA_SITUACAO.values(),
        *nomes.ROTULOS_DA_TRILHA.values(),
        nomes.EM_ANDAMENTO,
        nomes.DEFASADA,
        nomes.INVALIDA,
        nomes.EXPIRADA,
        nomes.INTERROMPIDA,
        nomes.SEM_CONFERENCIA_NA_CONVOCACAO,
        definir.AVISO_DA_INSCRICAO,
        definir.AVISO_DE_MODALIDADE,
        exportar.frase_do_resultado("COMPLETO", 1, 1),
        exportar.frase_do_resultado("PARCIAL", 1, 2),
    ]
    for texto in textos:
        achados = [t for t in PROIBIDOS if re.search(rf"\b{t}\b", texto.lower())]
        assert achados == [], texto


def test_a_pagina_diz_disponibilizado_e_nao_mais():
    """A ausência não basta: o que o GPS afirma tem nome, e é este (FR-3699, D-015)."""
    from processo_seletivo.formalizacao.domain import nomes

    assert nomes.ROTULOS_DA_TRILHA[nomes.EXPORTAR] == (
        "Pacote gerado e disponibilizado para download"
    )


def test_a_folha_da_tela_nao_crava_largura_e_quebra_o_que_nao_tem_espaco():
    folha = re.sub(r"/\*.*?\*/", "", FOLHA.read_text(), flags=re.S)
    assert not re.search(r"(?<![\w-])(min-)?width:\s*\d+px", folha)
    for seletor in (
        ".documentos-da-formalizacao li",
        ".pessoa-da-formalizacao h3",
        ".hash-do-pacote code",
        ".nao-incluidas ul",
    ):
        regra = re.search(rf"{re.escape(seletor)}\{{([^}}]*)\}}", folha)
        assert regra, seletor
        assert "overflow-wrap:anywhere" in regra.group(1), seletor
