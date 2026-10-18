"""As regras de antes e as de depois são as mesmas, na mesma ordem (089, FR-2030, FR-2033).

    equivalencia.py <commit-de-antes>      (de backend/)

Antes: o `<style>` do `interface/base.html` e o parcial dos tokens, no commit dado, sem os
`{% comment %}` (e sem os `/* */` que os tokens já tinham). Depois: `gestao.css` e `tokens.css`, sem os `/* */`. As duas sequências de linhas —
espaço só aparado no fim, linhas vazias fora — têm de ser iguais. E nenhum comentário de CSS pode fechar
antes do fim: depois de tirar os comentários, não pode sobrar `/*` nem `*/`.
"""

import re
import subprocess
import sys
from pathlib import Path

commit = sys.argv[1]


def mostrar(caminho):
    return subprocess.run(["git", "show", f"{commit}:backend/{caminho}"], capture_output=True,
                          text=True, check=True).stdout


def linhas(texto):
    return [l.rstrip() for l in texto.split("\n") if l.strip()]


DJANGO = re.compile(r"{% comment %}.*?{% endcomment %}", re.S)
CSS = re.compile(r"/\*.*?\*/", re.S)

modelo = mostrar("processo_seletivo/interface/templates/interface/base.html")
inicio = modelo.index("<style>\n") + len("<style>\n")
fim = modelo.index("{% block estilo_da_pagina %}")
folha_antes = DJANGO.sub("", modelo[inicio:fim])
tokens_antes = DJANGO.sub("", mostrar("processo_seletivo/shared/templates/shared/_tokens.css.html"))
antes = linhas(CSS.sub("", folha_antes.replace('{% include "shared/_tokens.css.html" %}', tokens_antes)))

gestao = Path("processo_seletivo/interface/static/interface/gestao.css").read_text(encoding="utf-8")
tokens = Path("processo_seletivo/shared/static/shared/tokens.css").read_text(encoding="utf-8")
depois_bruto = CSS.sub("", tokens) + "\n" + CSS.sub("", gestao)
depois = linhas(depois_bruto)

assert "/*" not in depois_bruto and "*/" not in depois_bruto, "comentário que fecha antes do fim"
assert "{%" not in tokens + gestao and "{{" not in tokens + gestao, "sintaxe de modelo nos .css"
comentarios_antes = len(DJANGO.findall(modelo[inicio:fim]))
comentarios_depois = len(CSS.findall(gestao))
print(f"linhas de regra: antes {len(antes)}, depois {len(depois)}")
print(f"comentários no <style> de antes: {comentarios_antes} (um é o do ponto de extensão, que fica no modelo)")
print(f"comentários em gestao.css: {comentarios_depois} (o cabeçalho da 089 mais os que vieram do modelo)")
assert comentarios_depois == comentarios_antes - 1 + 1
if antes != depois:
    for i, (a, b) in enumerate(zip(antes, depois)):
        if a != b:
            print("primeira diferença na linha", i, repr(a), repr(b))
            break
    sys.exit("DIFERENTES")
print("IGUAIS: as mesmas regras, na mesma ordem")
