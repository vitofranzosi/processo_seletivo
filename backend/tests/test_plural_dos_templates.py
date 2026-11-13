"""O plural dos templates, pelo filtro `pluralize` do Django.

O filtro só acrescenta sufixo, e o português troca terminação: *Retificação* vira *Retificações*, e
não *Retificaçãoões* — que foi o título da tela Retificar de 30/10 a 13/11. Com dois argumentos, o
primeiro é o do singular, e `pluralize:"m,"` punha *pertencem* no singular e *pertence* no plural,
em `_perfis_do_edital.html`, desde que a tela existe. Nenhum dos dois dava erro: só lendo a tela.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "processo_seletivo"

ARGUMENTO = re.compile(r'pluralize:"([^"]*)"')
# Sufixos que só servem trocando a terminação: precisam da forma "singular,plural", e com o radical
# cortado antes do `{{` (`inscriç{{ n|pluralize:"ão,ões" }}`).
SO_COM_TROCA = {"ões", "ães", "is"}


def _usos():
    for arquivo in sorted(RAIZ.rglob("templates/**/*")):
        if arquivo.suffix not in (".html", ".txt"):
            continue
        for numero, linha in enumerate(arquivo.read_text().splitlines(), 1):
            for argumento in ARGUMENTO.findall(linha):
                yield f"{arquivo.relative_to(RAIZ)}:{numero}", argumento


def test_a_varredura_encontra_os_plurais():
    assert sum(1 for _ in _usos()) > 50, "a varredura não achou os templates — a pasta mudou?"


def test_nenhum_plural_deixa_o_sufixo_no_singular():
    """`"m,"` é singular "m" e plural vazio: o contrário do que se quis."""
    invertidos = [
        onde for onde, argumento in _usos() if "," in argumento and not argumento.split(",")[1]
    ]

    assert invertidos == []


def test_nenhum_plural_que_troca_a_terminacao_e_so_acrescentado():
    """`Retificação{{ n|pluralize:"ões" }}` dizia *Retificaçãoões*."""
    colados = [onde for onde, argumento in _usos() if argumento in SO_COM_TROCA]

    assert colados == []
