from pathlib import Path
import json
from playwright.sync_api import sync_playwright

DEST = Path(__file__).resolve().parent.parent / "capturas/atual"
BASE = "http://localhost:8113"
DRAFT = "7f3d4272-5092-44b0-87b0-557052579ee1"
PF = "381d2ed4-437e-462e-8b21-4994b5da7811"
B = f"marco-{PF}-0-"
reg = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(
        storage_state="/tmp/ps_uxclass_browser.json",
        viewport={"width": 1440, "height": 1000},
    )
    page = ctx.new_page()

    def ir(etapa):
        r = page.goto(f"{BASE}/gestao/editais/{DRAFT}/compor/{etapa}")
        assert r.status == 200

    def capt(nome, alvo=None):
        if alvo:
            alvo.scroll_into_view_if_needed()
        page.screenshot(path=str(DEST / f"{nome}.png"), full_page=False)
        reg.append(
            {
                "captura": nome,
                "url": page.url,
                "texto": page.locator("main").inner_text(),
            }
        )

    def salvar():
        page.get_by_role("button", name="Salvar rascunho", exact=True).click()
        page.wait_for_load_state("networkidle")

    def editar():
        page.get_by_role("button", name="Editar DOC-INFO", exact=True).click()

    ir("classificacao")
    editar()
    capt("03-marco-aberto", page.locator(f'[id="{B}code"]'))
    page.get_by_role("button", name="Simular classificação", exact=True).first.click()
    page.locator("#painel-da-previa").wait_for(state="visible")
    page.wait_for_timeout(250)
    capt("04-simulacao-existente", page.locator("#painel-da-previa"))
    ir("etapas")
    page.locator('[name="etapa-0-weight"]').fill("")
    salvar()
    ir("classificacao")
    editar()
    capt("05-peso-ausente", page.locator(f'[id="{B}stages"]'))
    page.get_by_role("button", name="Simular classificação", exact=True).first.click()
    page.wait_for_timeout(200)
    capt("06-simulacao-incompleta", page.locator("#painel-da-previa"))
    ir("etapas")
    page.locator('[name="etapa-0-weight"]').fill("2")
    page.locator('[name="etapa-0-classificatory"]').uncheck()
    salvar()
    ir("classificacao")
    editar()
    capt("07-marca-retirada", page.locator(f'[id="{B}code"]'))
    ir("revisao")
    capt("08-revisao-apos-marca-retirada")
    ir("etapas")
    page.locator('[name="etapa-0-classificatory"]').check()
    salvar()
    ir("etapas")
    page.get_by_role("button", name="Acrescentar Etapa", exact=True).click()
    page.wait_for_timeout(200)
    novo = page.locator("fieldset.etapa").last
    print(
        "NOVOS",
        novo.locator("input").evaluate_all(
            "(els)=>els.map(e=>({name:e.name,value:e.value,type:e.type}))"
        ),
    )
    capt("09-nova-etapa", novo)
    Path("/tmp/ps_uxclass_nova_etapa.json").write_text(
        json.dumps(
            novo.locator("input").evaluate_all(
                "(els)=>els.map(e=>({name:e.name,value:e.value,type:e.type}))"
            )
        )
    )
    (DEST.parent.parent / "auditoria-navegacao.json").write_text(
        json.dumps(reg, ensure_ascii=False, indent=2)
    )
    ctx.storage_state(path="/tmp/ps_uxclass_browser.json")
    b.close()
