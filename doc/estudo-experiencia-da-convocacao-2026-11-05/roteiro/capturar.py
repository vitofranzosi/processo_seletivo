"""Capturas reais do portal para o estudo da convocação (05/11/2026).

uv run python capturar.py cenarios <saida>   — páginas de cada cenário, por cookie de sessão
uv run python capturar.py acesso1 <saida>    — sem sessão: 404, lista, acesso, pedido de código
uv run python capturar.py acesso2 <saida> CODIGO — digita o código e segue até a convocação e o envio
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SP = Path(__file__).parent
CENARIOS = {
    "c1": (8131, "85d3d64f-a150-454d-bc6d-f1e651f171fc", "gkdrw3qwf9s2yufhkr4r18nmhslb39x9"),
    "f": (8132, "2c398155-5f8f-4d76-b94c-4218785c4e91", "jq14aiup00m5fi4xcomrud0ywa06z90k"),
    "g": (8133, "ca9ac2a3-cbef-498f-9f93-10097c65ccf9", "hvdwqz9ibo5vsvepunji4cslpfkosv8p"),
    "i1": (8134, "6a96c891-b804-4561-a192-425c6fec6446", "8uob6kdg3v7bsmwixynn18nprnjtd9hw"),
    "corr": (8135, "288d206d-21e5-43d2-ad60-86e28bd84c63", "0nxycy3z5ed4j9lj4r5myz0mvsvjjqz6"),
}
LARGURAS = {"desktop": (1280, 900), "375": (375, 812)}


def contexto(browser, largura, porta=None, sessao=None, estado=None):
    w, h = LARGURAS[largura]
    ctx = browser.new_context(
        viewport={"width": w, "height": h},
        device_scale_factor=1 if largura == "desktop" else 2,
        storage_state=estado,
        locale="pt-BR",
    )
    if sessao:
        ctx.add_cookies([{"name": "sessionid", "value": sessao, "url": f"http://localhost:{porta}"}])
    return ctx


def foto(page, saida, nome, inteira=True):
    caminho = Path(saida) / f"{nome}.png"
    page.screenshot(path=str(caminho), full_page=inteira)
    print("captura", caminho.name, page.url)


def cenarios(saida):
    with sync_playwright() as p:
        b = p.chromium.launch()
        for letra, (porta, insc, sessao) in CENARIOS.items():
            for largura in LARGURAS:
                ctx = contexto(b, largura, porta, sessao)
                page = ctx.new_page()
                base = f"http://localhost:{porta}/selecoes"
                for tela, url in (
                    ("convocacao", f"{base}/inscricoes/{insc}/convocacao"),
                    ("acompanhamento", f"{base}/inscricoes/{insc}/acompanhamento"),
                    ("lista", f"{base}/inscricoes/"),
                ):
                    if tela == "lista" and letra not in ("c1", "corr"):
                        continue
                    page.goto(url)
                    foto(page, saida, f"{letra}-{tela}-{largura}")
                    if tela == "convocacao" and largura == "375":
                        foto(page, saida, f"{letra}-{tela}-375-primeira-tela", inteira=False)
                ctx.close()
        b.close()


def acesso1(saida):
    porta, insc, _ = CENARIOS["c1"]
    base = f"http://localhost:{porta}/selecoes"
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = contexto(b, "375")
        page = ctx.new_page()
        page.goto(f"{base}/inscricoes/{insc}/convocacao")
        foto(page, saida, "sem-sessao-link-direto-404-375")
        # O link que a mensagem de hoje leva: a lista.
        page.goto(f"{base}/inscricoes/")
        foto(page, saida, "sem-sessao-link-da-mensagem-375")
        page.fill("input[name=email]", "candidata601@exemplo.br")
        foto(page, saida, "acesso-email-375")
        page.click("button[type=submit]")
        page.wait_for_load_state()
        foto(page, saida, "acesso-codigo-375")
        ctx.storage_state(path=str(SP / "estado-acesso.json"))
        b.close()


def acesso2(saida, codigo):
    porta, insc, _ = CENARIOS["c1"]
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = contexto(b, "375", estado=str(SP / "estado-acesso.json"))
        page = ctx.new_page()
        page.goto(f"http://localhost:{porta}/selecoes/acesso/codigo")
        page.fill("input[name=codigo]", codigo)
        page.click("form button[type=submit]")
        page.wait_for_load_state()
        foto(page, saida, "depois-do-codigo-375")
        # Da lista para a convocação: o caminho que a pessoa faz hoje.
        links = page.locator("main a").all()
        print("links na lista:", [(a.inner_text(), a.get_attribute("href")) for a in links])
        alvo = page.locator("main a", has_text="onvoca").first
        alvo.click()
        page.wait_for_load_state()
        foto(page, saida, "lista-para-convocacao-375")
        # Envio real de um PDF no primeiro item.
        pdf = SP / "documento.pdf"
        pdf.write_bytes(
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>"
            b"endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"
        )
        primeiro = page.locator("form[data-envio]").first
        primeiro.locator("input[type=file]").set_input_files(str(pdf))
        primeiro.locator("button[type=submit]").click()
        page.wait_for_load_state()
        foto(page, saida, "depois-do-envio-375")
        foto(page, saida, "depois-do-envio-375-primeira-tela", inteira=False)
        page.set_viewport_size({"width": 1280, "height": 900})
        page.reload()
        foto(page, saida, "depois-do-envio-desktop")
        ctx.storage_state(path=str(SP / "estado-logado.json"))
        print(json.dumps([c["name"] for c in ctx.cookies()]))
        b.close()


if __name__ == "__main__":
    modo, saida = sys.argv[1], sys.argv[2]
    Path(saida).mkdir(parents=True, exist_ok=True)
    if modo == "cenarios":
        cenarios(saida)
    elif modo == "acesso1":
        acesso1(saida)
    else:
        acesso2(saida, sys.argv[3])
