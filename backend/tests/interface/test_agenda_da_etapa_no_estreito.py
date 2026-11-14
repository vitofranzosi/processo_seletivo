"""As telas da agenda sob a política de conteúdo e no estreito (167, T034, SC-2397, UX-763, UX-767).

Estilo e script escritos no template não funcionam: a política os recusa em silêncio. E a grade vira
lista cronológica abaixo de 40rem só pela folha, sobre a mesma marcação — a regra precisa estar
dentro da consulta de largura.
"""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo/interface"
TEMPLATES = RAIZ / "templates/interface"
FOLHA = RAIZ / "static/interface/telas/agenda-da-etapa.css"

DA_167 = [
    "agenda_configurar.html",
    "_agenda_formulario.html",
    "_agenda_capacidade.html",
    "agenda_montar.html",
    "_agenda_grade.html",
    "_agenda_painel.html",
    # A entrega B: conferir e a agenda publicada.
    "agenda_conferir.html",
    "agenda_publicada.html",
]


@pytest.mark.parametrize("nome", DA_167)
def test_nada_escrito_em_linha(nome):
    texto = (TEMPLATES / nome).read_text()

    assert not re.search(r"\sstyle=", texto)
    assert "<style" not in texto
    # Só o arquivo do htmx, servido da própria origem: script escrito no documento a CSP recusa.
    assert not re.search(r"<script(?![^>]*\bsrc=)", texto)
    assert not re.search(r"\son[a-z]+=", texto)
    assert "hx-on" not in texto and "js:" not in texto


def _bloco_da_consulta(folha, largura):
    inicio = folha.index(f"@media (max-width:{largura})")
    return folha[inicio : folha.index("\n}", inicio)]


def test_a_grade_vira_lista_so_dentro_da_consulta_estreita():
    folha = FOLHA.read_text()
    estreito = _bloco_da_consulta(folha, "40rem")

    assert ".grade-compacta thead{display:none;}" in estreito
    assert ".banca-no-estreito{display:inline;" in estreito
    fora = folha.replace(estreito, "")
    assert ".banca-no-estreito{display:none}" in fora
    assert ".grade-compacta thead{display:none" not in fora


def test_o_painel_vem_antes_da_grade_no_estreito():
    """UX-761: o painel ao lado no desktop, e acima da grade em telas estreitas."""
    assert ".painel-de-acao{order:-1;}" in _bloco_da_consulta(FOLHA.read_text(), "64rem")


@pytest.mark.parametrize("nome", ["agenda_configurar.html", "agenda_montar.html"])
def test_as_paginas_carregam_o_htmx(nome):
    """O simulador e o painel dependem dele; sem o arquivo, a tela cai no caminho sem script."""
    assert "interface/htmx.min.js" in (TEMPLATES / nome).read_text()
