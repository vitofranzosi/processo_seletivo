"""A tabela larga rola dentro de si; a página continua cabendo em 375 px."""

from pathlib import Path


def test_toda_tabela_da_classificacao_tem_conteiner_rolavel():
    templates = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo"
        / "interface"
        / "templates"
        / "interface"
    )
    for nome in ("ordenacao.html", "ato_ordenacao.html"):
        corpo = (templates / nome).read_text()
        assert corpo.count("<table") == corpo.count('class="tabela-rolavel"')


def test_o_conteiner_limita_a_rolagem_horizontal():
    base = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo"
        / "interface"
        / "templates"
        / "interface"
        / "base.html"
    )
    assert ".tabela-rolavel{overflow-x:auto}" in base.read_text()
