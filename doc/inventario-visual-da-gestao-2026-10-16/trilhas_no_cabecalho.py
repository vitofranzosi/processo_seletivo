"""Quantas telas da gestão ainda não têm a trilha no cabeçalho de contexto (087, `SC-776`).

Conta os modelos de página que estendem `interface/base.html` diretamente, pelo texto. Sem o bloco
`caminho_do_contexto`, a tela tem o cabeçalho da 076 e a trilha, se houver, no conteúdo. Com o bloco e
`block.super` dentro dele, há variante que continua com o da 076 — a Auditoria do Edital, que divide o
modelo com a Trilha da avaliação (D-002 da 080) —, e ela é listada à parte. As nove etapas da
composição estendem `compor_base.html`, que tem o bloco, e não entram na conta.

    python3 doc/inventario-visual-da-gestao-2026-10-16/trilhas_no_cabecalho.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TEMPLATES = RAIZ / "backend" / "processo_seletivo" / "interface" / "templates" / "interface"
BASE = '{% extends "interface/base.html" %}'
BLOCO = "{% block caminho_do_contexto %}"


def main():
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else TEMPLATES
    modelos = sorted(p for p in pasta.glob("*.html") if p.read_text().startswith(BASE))
    sem_bloco = [p.stem for p in modelos if BLOCO not in p.read_text()]
    com_variante = [
        p.stem
        for p in modelos
        if BLOCO in p.read_text()
        and "block.super" in p.read_text().split(BLOCO)[1].split("{% endblock %}")[0]
    ]
    print(f"estendem interface/base.html: {len(modelos)}")
    print(f"sem o bloco caminho_do_contexto: {len(sem_bloco)}")
    for nome in sem_bloco:
        print(f"  {nome}")
    print(f"com o bloco e uma variante com o cabeçalho da 076: {len(com_variante)}")
    for nome in com_variante:
        print(f"  {nome}")


if __name__ == "__main__":
    main()
