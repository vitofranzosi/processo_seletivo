from pathlib import Path
import json
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8113"
D = "7f3d4272-5092-44b0-87b0-557052579ee1"
PF = "381d2ed4-437e-462e-8b21-4994b5da7811"
DEST = Path(__file__).resolve().parent.parent
reg = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(
        storage_state="/tmp/ps_uxclass_browser.json",
        viewport={"width": 1440, "height": 1000},
    )
    page = ctx.new_page()

    def ir(s):
        page.goto(f"{BASE}/gestao/editais/{D}/compor/{s}")

    def wait():
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(350)

    def salvar():
        invalidos = page.locator("#formulario :invalid").evaluate_all(
            "(els)=>els.map(e=>[e.name,e.value,e.validationMessage])"
        )
        print("INVALIDOS", invalidos, flush=True)
        assert not invalidos
        page.get_by_role("button", name="Salvar rascunho", exact=True).click()
        wait()
        print("SALVOU", page.url, flush=True)

    def shot(n, alvo):
        alvo.scroll_into_view_if_needed()
        page.screenshot(path=str(DEST / "capturas/atual" / f"{n}.png"))
        reg.append(
            {"captura": n, "url": page.url, "texto": page.locator("main").inner_text()}
        )

    # Reabrir revela a persistência e usa o novo índice sequencial.
    ir("etapas")
    stages = page.locator("fieldset.etapa").evaluate_all(
        '(els)=>els.map(e=>({id:e.querySelector("input[name$=\\"-id\\"]").value,nome:e.querySelector("input[name$=\\"-name\\"]").value}))'
    )
    ids = [s["id"] for s in stages]
    ir("classificacao")
    page.get_by_role("button", name="Editar DOC-INFO", exact=True).click()
    card = page.locator(f"#cartao-{PF}")

    def definir(
        sub, code, name, sel, target, dest, operation="MEDIA_PONDERADA", suplentes="0"
    ):
        base = f"marco-{PF}-{sub}-"

        def loc(s):
            return page.locator(f'[name="{base}{s}"]')

        loc("orderProduction").select_option("POR_PONTUACAO")
        wait()
        loc("code").fill(code)
        loc("name").fill(name)
        print("DEFININDO", sub, code, flush=True)
        for sid in ids:
            box = page.locator(f'input[name="{base}stages"][value="{sid}"]')
            box.set_checked(sid in sel)
            wait()
        if (
            loc("operation").count()
            and loc("operation").evaluate("(e)=>e.tagName") == "SELECT"
        ):
            loc("operation").select_option(operation)
        if (
            loc("normalization").count()
            and loc("normalization").evaluate("(e)=>e.tagName") == "SELECT"
        ):
            loc("normalization").select_option("NENHUMA")
        for details in page.locator(f"#marco-{PF}-{sub} details").all():
            details.evaluate("(el)=>el.open=true")
        loc("cutTargetKind").select_option(
            "FROM_VACANCY_TABLE" if target is None else "FIXED"
        )
        if target is not None:
            loc("cutTargetCount").fill(str(target))
        loc("cutSurplusCount").fill(suplentes)
        loc("cutTieOutcome").select_option("ADMITS_SURPLUS")
        loc("cutGovernedStage").select_option(dest)
        loc("cutContinuation").select_option("NONE")

    definir("0", "POS-TIT", "Após títulos", ids[:2], 6, ids[2], suplentes="2")
    for code, name, sel, target, dest in [
        ("PRE", "Seleção para títulos", [ids[0]], 12, ids[1]),
        ("FINAL", "Classificação final", ids, None, "NONE"),
    ]:
        card.get_by_role("button", name="Acrescentar marco", exact=True).click()
        wait()
        novo = card.locator("fieldset.marco").last
        sub = novo.get_attribute("id").split("-")[-1]
        definir(sub, code, name, sel, target, dest)
    print(
        "CAMPOS FINAIS",
        page.locator("#formulario").evaluate(
            '(f)=>Array.from(new FormData(f).entries()).filter(([k])=>k.includes("marco-") && !k.includes("draw-"))'
        ),
        flush=True,
    )
    shot("11-tres-marcos-configurados", card.locator("fieldset.marco").last)
    salvar()
    ir("classificacao")
    page.get_by_role("button", name="Editar DOC-INFO", exact=True).click()
    shot("12-visao-complexa", page.locator(f"#cartao-{PF}"))
    card = page.locator(f"#cartao-{PF}")
    final = card.locator("fieldset.marco").filter(
        has=page.locator('input[name$="-code"][value="FINAL"]')
    )
    final.get_by_role("button", name="Simular classificação", exact=True).click()
    wait()
    shot("13-previa-final-multietapas", page.locator("#painel-da-previa"))
    ir("revisao")
    shot("14-revisao-complexa", page.locator("main"))
    (DEST / "cenario-configurado.json").write_text(
        json.dumps(
            {"edital": D, "perfil": PF, "etapas": stages}, ensure_ascii=False, indent=2
        )
    )
    (DEST / "auditoria-complexa.json").write_text(
        json.dumps(reg, ensure_ascii=False, indent=2)
    )
    b.close()
