import json
from pathlib import Path
from playwright.sync_api import sync_playwright

D = Path(__file__).resolve().parent.parent
URL = "http://localhost:8113/gestao/editais/28a8713e-68c5-41f1-a241-94fbeb18b81d/marcos/00000000-0000-0000-0027-0000000000a1/sorteio"
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
        "Ensaio sintético após Retificação: fonte com horário, para verificar precedência no mesmo dia."
    )
    page.get_by_role(
        "button", name="Publicar relação nova, sucedendo a atual", exact=True
    ).click()
    page.wait_for_load_state("networkidle")
    page.screenshot(
        path=str(D / "capturas/atual/19-relacao-com-horario.png"), full_page=True
    )
    reg.append(
        {
            "passo": "relação com método retificado",
            "texto": page.locator("main").inner_text(),
        }
    )
    page.get_by_role(
        "button", name="Observar a ocorrência 9003 na fonte", exact=True
    ).click()
    page.wait_for_load_state("networkidle")
    page.screenshot(
        path=str(D / "capturas/atual/20-ocorrencia-posterior.png"), full_page=True
    )
    reg.append(
        {
            "passo": "ocorrência com horário posterior",
            "texto": page.locator("main").inner_text(),
        }
    )
    page.get_by_text("Anular este sorteio", exact=True).click()
    f = page.locator('form[action$="/anular"]')
    f.locator('[name="ocorrencia_id"]').select_option(
        label="Fonte de demonstração — 9003, observada em "
        + f.locator('[name="ocorrencia_id"] option')
        .last.inner_text()
        .split("observada em ")[-1]
    )
    f.locator('[name="motivo"]').fill(
        "Ensaio sintético: sucessor após relação nova e fonte com limite horário posterior ao compromisso."
    )
    f.get_by_role("button", name="Anular e constituir o sucessor", exact=True).click()
    page.wait_for_load_state("networkidle")
    texto = page.locator("main").inner_text()
    print(texto[:2100])
    assert "Não foi possível" not in texto
    assert "Sorteio anulado" in texto or "sucessor" in texto
    page.screenshot(
        path=str(D / "capturas/atual/21-sorteio-sucessor-constituido.png"),
        full_page=True,
    )
    reg.append({"passo": "sorteio sucessor constituído", "texto": texto})
    (D / "auditoria-sorteio-com-horario.json").write_text(
        json.dumps(reg, ensure_ascii=False, indent=2)
    )
    b.close()
