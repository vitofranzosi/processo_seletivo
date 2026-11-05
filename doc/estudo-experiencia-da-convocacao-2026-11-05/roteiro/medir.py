"""Mede a primeira tela das maquetes da convocação em seis condições (versão 2).

Para cada maquete e condição: onde termina a ação principal, se há rolagem horizontal, e se a ação
vem antes do andamento na ordem do documento — que é o critério que não depende de pixel.

Uso: uv run python medir.py <pasta-das-maquetes>
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

MAQUETES = ["convocacao", "convocacao-pendencia", "convocacao-apos-envio", "convocacao-sucessora"]
CONDICOES = [
    # nome, largura, altura, fonte da raiz (None = a do navegador, 16 px)
    ("375 × 812", 375, 812, None),
    ("320 × 568", 320, 568, None),
    ("375, fonte 125 %", 375, 812, "20px"),
    ("375, fonte 150 %", 375, 812, "24px"),
    ("zoom 200 % (1280 × 900)", 640, 450, None),
    ("1280 × 900", 1280, 900, None),
]
MEDIDA = """() => {
  const acao = document.querySelector('.chamada-da-convocacao a.principal');
  const andamento = document.querySelector('.andamento');
  const antes = acao && andamento
    ? !!(acao.compareDocumentPosition(andamento) & Node.DOCUMENT_POSITION_FOLLOWING) : null;
  return {
    fim: acao ? Math.round(acao.getBoundingClientRect().bottom + window.scrollY) : null,
    largura: document.documentElement.scrollWidth,
    antes,
    foco: document.activeElement ? (document.activeElement.id || document.activeElement.tagName) : null,
  };
}"""

pasta = Path(sys.argv[1]).resolve()
print("| Maquete | Condição | Fim da ação | Altura da tela | Na primeira tela | Rolagem horizontal | Ação antes do andamento |")
print("|---|---|---|---|---|---|---|")
with sync_playwright() as p:
    b = p.chromium.launch()
    for nome in MAQUETES:
        for rotulo, w, h, fonte in CONDICOES:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto((pasta / f"{nome}.html").as_uri())
            if fonte:
                pg.add_style_tag(content=f"html{{font-size:{fonte}}}")
            m = pg.evaluate(MEDIDA)
            cabe = "sim" if m["fim"] is not None and m["fim"] <= h else "não"
            rolagem = "não" if m["largura"] <= w else f"sim ({m['largura']} px)"
            print(f"| {nome} | {rotulo} | {m['fim']} px | {h} px | {cabe} | {rolagem} | {'sim' if m['antes'] else 'não'} |")
            pg.close()
    # Depois do envio: o envio volta a #o-que-fazer. Onde fica a confirmação, e quem tem o foco?
    pg = b.new_page(viewport={"width": 375, "height": 812})
    pg.goto((pasta / "convocacao-apos-envio.html").as_uri() + "#confirmacao")
    caixa = pg.evaluate("(() => { const c = document.querySelector('[data-confirmacao]').getBoundingClientRect(); return [Math.round(c.top), Math.round(c.bottom)] })()")
    foco = pg.evaluate("document.activeElement.id || document.activeElement.tagName")
    print(f"\nDepois do envio, em #confirmacao a 375 × 812: a confirmação ocupa {caixa[0]}–{caixa[1]} px da tela; o foco está em {foco!r} (sem script nenhum).")
    b.close()
