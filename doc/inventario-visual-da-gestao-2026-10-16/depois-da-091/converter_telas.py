"""O estilo de cada tela sai do modelo para arquivo estático (091, R-006).

    converter_telas.py <backend>

Para cada modelo da gestão com `{% block estilo_da_pagina %}`: o que o bloco inclui de um parcial
`_estilo_*.html` vira `<link>` para `interface/grupos/<grupo>.css`, gerado do parcial; as regras
próprias da tela viram `interface/telas/<tela>.css`, e um `<link>` para ele, na mesma posição. Os
`{% comment %}` de dentro viram `/* */` (D-002 da `089`). O `<style>` que envolvia o bloco nas duas
bases e no fragmento do protótipo sai — essas três passagens são feitas à mão, e o script só confere
que nenhum `<style>` sobrou.

Idempotente não é: roda uma vez, sobre a árvore de antes. A equivalência é do `equivalencia_telas.py`.
"""

import re
import sys
from pathlib import Path

BACKEND = Path(sys.argv[1])
MODELOS = BACKEND / "processo_seletivo/interface/templates/interface"
ESTATICOS = BACKEND / "processo_seletivo/interface/static/interface"

BLOCO = re.compile(r"\{% block estilo_da_pagina %\}(.*?)\{% endblock %\}", re.S)
INCLUI = re.compile(r'\{% include "interface/_estilo_(\w+)\.html" %\}')
COMENTARIO = re.compile(r"\{% comment %\}(.*?)\{% endcomment %\}", re.S)

GRUPOS = {
    "do_acesso": "acesso",
    "do_aviso": "aviso",
    "das_terminais": "terminais",
    "da_vista": "vista",
    "da_lista_exigida": "lista-exigida",
}


def css(texto):
    """O texto de modelo como folha: só comentários e regras, e os comentários como `/* */`."""

    def troca(achado):
        prosa = achado.group(1)
        assert "*/" not in prosa, f"comentário que fecharia antes do fim: {prosa[:80]!r}"
        return "/*" + prosa + "*/"

    convertido = COMENTARIO.sub(troca, texto)
    assert "{%" not in convertido and "{{" not in convertido, convertido[:200]
    return convertido


def link(caminho):
    return f"<link rel=\"stylesheet\" href=\"{{% estatico '{caminho}' %}}\">"


def carregar_estaticos(modelo):
    """`{% load estaticos %}` no topo: a carga de biblioteca não passa da base para a filha."""
    if re.search(r"\{% load [^%]*\bestaticos\b", modelo):
        return modelo
    carga = re.search(r"\{% load ([^%]+?) %\}", modelo[:300])
    if carga:
        return modelo[: carga.start(1)] + carga.group(1) + " estaticos" + modelo[carga.end(1) :]
    extends = re.match(r'\{% extends "[^"]+" %\}', modelo)
    if extends:
        return modelo[: extends.end()] + "{% load estaticos %}" + modelo[extends.end() :]
    return "{% load estaticos %}" + modelo


(ESTATICOS / "grupos").mkdir(exist_ok=True)
(ESTATICOS / "telas").mkdir(exist_ok=True)

for parcial, grupo in GRUPOS.items():
    origem = MODELOS / f"_estilo_{parcial}.html"
    (ESTATICOS / "grupos" / f"{grupo}.css").write_text(css(origem.read_text()))

for arquivo in sorted(MODELOS.glob("*.html")):
    if arquivo.name.startswith("_estilo_"):
        continue
    modelo = arquivo.read_text()
    achado = BLOCO.search(modelo)
    if not achado or not achado.group(1).strip():
        continue
    tela = arquivo.stem.replace("_", "-")
    corpo = achado.group(1)
    links, proprios = [], []
    posicao = 0
    for inclusao in INCLUI.finditer(corpo):
        trecho = corpo[posicao : inclusao.start()]
        if trecho.strip():
            proprios.append(trecho)
            links.append(link(f"interface/telas/{tela}.css"))
        links.append(link(f"interface/grupos/{GRUPOS[inclusao.group(1)]}.css"))
        posicao = inclusao.end()
    if corpo[posicao:].strip():
        proprios.append(corpo[posicao:])
        links.append(link(f"interface/telas/{tela}.css"))
    assert len(proprios) <= 1, f"{arquivo.name}: regras próprias antes e depois de um parcial"
    if proprios:
        (ESTATICOS / "telas" / f"{tela}.css").write_text(css(proprios[0]).strip("\n") + "\n")
    novo = "{% block estilo_da_pagina %}" + "".join(links) + "{% endblock %}"
    modelo = modelo[: achado.start()] + novo + modelo[achado.end() :]
    arquivo.write_text(carregar_estaticos(modelo))
    print(f"{arquivo.name:34} {len(links)} link(s)  próprio: {bool(proprios)}")
