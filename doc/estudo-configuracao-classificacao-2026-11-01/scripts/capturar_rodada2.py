"""Capturas e verificações do protótipo da rodada 2.

Requer o servidor de arquivos da pasta do estudo:
    python3 -m http.server 8769 --bind 127.0.0.1 --directory doc/estudo-configuracao-classificacao-2026-11-01
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8769/prototipos/v2/index.html"
DEST = Path(__file__).resolve().parent.parent / "capturas" / "rodada2"
DEST.mkdir(parents=True, exist_ok=True)
registro = []


def esperar(page):
    # Só nas capturas: o inspetor deixa de rolar por dentro, para sair inteiro na imagem.
    page.add_style_tag(content=".inspetor{position:static!important;max-height:none!important}")
    page.wait_for_timeout(250)


def capturar(page, nome, alvo=None):
    caminho = DEST / f"{nome}.png"
    if alvo:
        page.locator(alvo).first.screenshot(path=str(caminho))
    else:
        page.screenshot(path=str(caminho), full_page=True)
    registro.append({"captura": nome, "url": page.url})


def mudar(page, seletor, valor=None):
    el = page.locator(seletor).first
    tipo = el.get_attribute("type")
    if tipo in ("checkbox", "radio"):
        el.set_checked(valor is not False)
    elif el.evaluate("e => e.tagName") == "SELECT":
        el.select_option(valor)
    else:
        el.fill(str(valor))
        el.press("Tab")
    esperar(page)


with sync_playwright() as p:
    nav = p.chromium.launch()
    erros = []
    ctx = nav.new_context(viewport={"width": 1440, "height": 1000})
    page = ctx.new_page()
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)

    page.goto(BASE + "?cenario=diario")
    esperar(page)
    capturar(page, "v2-01-trilho-como-no-diario")

    page.goto(BASE + "?cenario=diario&sel=marco:final")
    esperar(page)
    capturar(page, "v2-02-final-idade-invertida")
    mudar(page, '[data-k="crit:docinfo:final:1:q"]', "velho")
    capturar(page, "v2-03-final-idade-corrigida", ".inspetor")

    page.goto(BASE + "?cenario=pronto&sel=etapa:did&mover=did:up")
    esperar(page)
    capturar(page, "v2-04-reordenar-previa-do-efeito")

    page.goto(BASE + "?cenario=zero")
    esperar(page)
    capturar(page, "v2-05-do-zero")
    page.locator('[data-k="novo-marco:0"]').click()
    esperar(page)
    capturar(page, "v2-06-do-zero-nova-ordem-sem-resposta")
    marco = page.evaluate("window.GPS2.estado.sel.id")
    k = f"marco:docinfo:{marco}:"
    mudar(page, f'[data-k="{k}dep-segue"]')
    mudar(page, f'[data-k="{k}tipo-fixo"]')
    mudar(page, f'[data-k="{k}alvo"]', 12)
    capturar(page, "v2-07-do-zero-incompleta-empate-e-faixa")
    mudar(page, f'[data-k="{k}emp-todos"]')
    mudar(page, f'[data-k="{k}cont-nao"]')
    capturar(page, "v2-08-do-zero-corte-pronto-sem-final")

    page.goto(BASE + "?cenario=pronto&marca=manual&sel=etapa:tit")
    esperar(page)
    mudar(page, '[data-k="etapa:tit:marca"]', False)
    capturar(page, "v2-09-marca-manual-retirada")

    page.goto(BASE + "?cenario=pronto&sel=etapa:did")
    esperar(page)
    mudar(page, '[data-k="etapa:did:min"]', "")
    capturar(page, "v2-10-etapa-eliminatoria-sem-minima", ".inspetor")

    page.goto(BASE + "?cenario=circular&sel=marco:postit")
    esperar(page)
    capturar(page, "v2-11-destino-circular")

    page.goto(BASE + "?cenario=pronto&perfil=teclab")
    esperar(page)
    capturar(page, "v2-12-tec-lab-etapas-compartilhadas")

    page.goto(BASE + "?cenario=desempateFora&perfil=docmat&sel=marco:matfinal")
    esperar(page)
    capturar(page, "v2-16-porta-e-desempate-fora-da-ordem")

    page.goto(BASE + "?cenario=diario&modo=texto")
    esperar(page)
    capturar(page, "v2-13-texto-do-edital-como-no-diario")

    page.goto(BASE + "?cenario=pronto&modo=trilho&sel=marco:final")
    esperar(page)
    capturar(page, "v2-14-pronto-por-hipotese")

    # teclado: do primeiro cartão de Etapa, Tab chega aos controles do inspetor sem mouse
    page.goto(BASE + "?cenario=pronto")
    esperar(page)
    page.locator('[data-k="sel:etapa:obj"]').focus()
    page.keyboard.press("Enter")
    esperar(page)
    foco_titulo = page.evaluate("document.activeElement.id")
    page.keyboard.press("Tab")
    foco_seguinte = page.evaluate("document.activeElement.dataset.k || document.activeElement.tagName")

    largo = {}
    for modo in ("trilho", "texto"):
        movel = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pm = movel.new_page()
        pm.on("pageerror", lambda e: erros.append(str(e)))
        pm.goto(BASE + f"?cenario=diario&modo={modo}&sel=marco:final")
        pm.wait_for_timeout(300)
        largo[modo] = pm.evaluate("document.documentElement.scrollWidth")
        pm.screenshot(path=str(DEST / f"v2-15-movel-{modo}.png"), full_page=False)
        registro.append({"captura": f"v2-15-movel-{modo}", "url": pm.url})
        movel.close()

    resultado = {
        "erros_de_javascript": erros,
        "teclado": {"foco_apos_enter": foco_titulo, "foco_apos_tab": foco_seguinte},
        "largura_da_pagina_em_390": largo,
        "capturas": registro,
    }
    (DEST.parent.parent / "verificacao-rodada2.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2)
    )
    print(json.dumps({k: v for k, v in resultado.items() if k != "capturas"}, ensure_ascii=False))
    nav.close()
