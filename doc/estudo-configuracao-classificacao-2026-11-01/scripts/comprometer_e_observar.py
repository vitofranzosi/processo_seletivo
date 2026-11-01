import json
from pathlib import Path
from playwright.sync_api import sync_playwright

DEST = Path(__file__).resolve().parent.parent
URL = "http://localhost:8113/gestao/editais/d35fc1c9-0a9b-4755-a998-ebbbc999815a/marcos/00000000-0000-0000-0026-0000000000a1/sorteio"
reg = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(
        storage_state="/tmp/ps_uxclass_presidente.json",
        viewport={"width": 1440, "height": 1000},
    )
    page = ctx.new_page()
    page.goto(URL)
    page.locator('form[action$="/relacao"] [name="motivo"]').fill(
        "Caso sintético de UX: reproduzir a recusa temporal, após o aviso, com fonte de demonstração."
    )
    page.get_by_role(
        "button", name="Publicar relação nova, sucedendo a atual", exact=True
    ).click()
    page.wait_for_load_state("networkidle")
    print("APOS RELACAO", page.locator("main").inner_text()[-6200:])
    page.screenshot(
        path=str(DEST / "capturas/atual/16-relacao-sucessora-inviavel.png"),
        full_page=True,
    )
    reg.append(
        {"etapa": "relacao sucessora", "texto": page.locator("main").inner_text()}
    )
    page.get_by_role(
        "button", name="Observar a ocorrência 9001 na fonte", exact=True
    ).click()
    page.wait_for_load_state("networkidle")
    page.screenshot(
        path=str(DEST / "capturas/atual/17-ocorrencia-observada-inviavel.png"),
        full_page=True,
    )
    reg.append(
        {"etapa": "ocorrencia observada", "texto": page.locator("main").inner_text()}
    )
    print("BOTOES", page.locator("main button").all_text_contents())
    print(
        "LINKS",
        page.locator("main a").evaluate_all(
            "(els)=>els.map(e=>[e.textContent,e.href])"
        ),
    )
    (DEST / "auditoria-sorteio.json").write_text(
        json.dumps(reg, ensure_ascii=False, indent=2)
    )
    b.close()
