import json
from pathlib import Path
from playwright.sync_api import sync_playwright

DEST = Path(__file__).resolve().parent.parent
URL = "http://localhost:8113/gestao/editais/d35fc1c9-0a9b-4755-a998-ebbbc999815a/marcos/00000000-0000-0000-0026-0000000000a1/sorteio"
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1440, "height": 1000})
    page.goto("http://localhost:8113/gestao/identificar/demonstracao")
    page.locator('button[value="paulo.presidente"]').click()
    page.goto(URL)
    print(page.locator("main").inner_text()[:15000])
    print(
        "FORMULARIOS",
        page.locator("main form").evaluate_all(
            '(els)=>els.map(e=>({action:e.action,campos:Array.from(new FormData(e).entries()).filter(([k])=>k!=="csrfmiddlewaretoken"),botoes:Array.from(e.querySelectorAll("button")).map(b=>b.textContent)}))'
        ),
    )
    page.screenshot(
        path=str(DEST / "capturas/atual/15-sorteio-aviso-atual.png"), full_page=True
    )
    page.context.storage_state(path="/tmp/ps_uxclass_presidente.json")
    (DEST / "auditoria-sorteio-inicial.json").write_text(
        json.dumps(
            {"url": URL, "texto": page.locator("main").inner_text()},
            ensure_ascii=False,
            indent=2,
        )
    )
    b.close()
