import json
from pathlib import Path
from playwright.sync_api import sync_playwright

DEST = Path(__file__).resolve().parent.parent
URL = "http://localhost:8113/gestao/editais/d35fc1c9-0a9b-4755-a998-ebbbc999815a/marcos/00000000-0000-0000-0026-0000000000a1/sorteio"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(
        storage_state="/tmp/ps_uxclass_presidente.json",
        viewport={"width": 1440, "height": 1000},
    )
    page = ctx.new_page()
    page.goto(URL)
    page.get_by_text("Anular este sorteio", exact=True).click()
    f = page.locator('form[action$="/anular"]')
    print(
        f.locator("input,textarea").evaluate_all("(els)=>els.map(e=>[e.name,e.type])")
    )
    for campo in f.locator('[name="motivo"]').all():
        campo.fill(
            "Ensaio sintético: pedido de sucessão com ocorrência no mesmo dia do congelamento, para conferir a recusa."
        )
    with page.expect_response(lambda r: "/sorteio/anular" in r.url) as resp:
        f.get_by_role(
            "button", name="Anular e constituir o sucessor", exact=True
        ).click()
    page.wait_for_load_state("networkidle")
    print("HTTP", resp.value.status)
    print(page.locator("main").inner_text()[:2300])
    page.screenshot(
        path=str(DEST / "capturas/atual/18-recusa-de-execucao.png"), full_page=True
    )
    (DEST / "recusa-temporal.json").write_text(
        json.dumps(
            {"http": resp.value.status, "texto": page.locator("main").inner_text()},
            ensure_ascii=False,
            indent=2,
        )
    )
    b.close()
