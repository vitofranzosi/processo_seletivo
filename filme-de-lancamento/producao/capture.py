"""Captura das telas reais do sistema (servidor local em 8090, banco ps_filme).

Cada tomada grava <nome>.png (página inteira, escala 2) e <nome>.json com as caixas dos seletores
pedidos, em pixels da imagem — é delas que o compositor tira os recortes e os alvos de câmera."""
import json, os, sys, time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8090"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cap")
os.makedirs(OUT, exist_ok=True)

E01 = "afaf823b-c183-4fd2-bd1a-07672bc3afa7"
E26 = "7e8dc780-7913-4c1a-aaa7-091544069710"
E51 = "c943dc8b-6cbd-4922-8610-afac32feea16"
E76 = "787e0e3c-b9df-4a3f-8f8c-724af90ab4b3"
P = "bc14489d-ea2c-48be-89db-594a6e5ccb6a"
M51 = "00000000-0000-0000-0051-0000000000a1"
M26 = "00000000-0000-0000-0026-0000000000a1"
PUB51 = "4eaa424e-17bb-4cbe-935a-844cbb1c2767"
ATO51 = "214fa21d-30b7-4f37-8604-e1481443921a"
SORT = "908a5894-372b-428e-b5d4-f55587deca81"
REL = "f623ef8f-1faf-485b-a166-9be000976e1e"
RET = "26042de3-11f7-4950-91ea-b0ef13c83c73"

def shoot(pg, name, url=None, sel=None, width=1440, full=True, before=None, wait=400):
    if url:
        pg.goto(BASE + url, wait_until="networkidle")
    if before:
        before(pg)
    pg.wait_for_timeout(wait)
    path = os.path.join(OUT, name + ".png")
    pg.screenshot(path=path, full_page=full)
    meta = {"url": pg.url, "title": pg.title(), "boxes": {}}
    dpr = pg.evaluate("window.devicePixelRatio")
    for key, css in (sel or {}).items():
        els = pg.query_selector_all(css)
        bx = []
        for e in els[:40]:
            b = e.bounding_box()
            if b:
                sy = pg.evaluate("window.scrollY") if not full else 0
                bx.append([b["x"] * dpr, (b["y"] + (pg.evaluate("window.scrollY") if full else 0)) * dpr,
                           b["width"] * dpr, b["height"] * dpr])
        meta["boxes"][key] = bx
    json.dump(meta, open(os.path.join(OUT, name + ".json"), "w"), indent=1, ensure_ascii=False)
    print("ok", name, pg.url, file=sys.stderr)

def sair(pg):
    pg.goto(BASE + "/gestao/identificar", wait_until="networkidle")
    if pg.query_selector("form[action$='sair']"):
        with pg.expect_navigation():
            pg.evaluate("document.querySelector(\"form[action$='sair']\").submit()")
        pg.goto(BASE + "/gestao/identificar", wait_until="networkidle")

def login_gestao(pg, subject, papeis):
    sair(pg)
    sug = pg.query_selector(f"button[name=identidade_sugerida][value='{subject}']")
    if sug and not papeis:
        sug.click()
    else:
        pg.fill("input[name=subject]", subject)
        for p in papeis:
            pg.check(f"input[name=papeis][value='{p}']")
        pg.click("form:has(input[name=subject]) button[type=submit]")
    pg.wait_for_load_state("networkidle")
    print("login", subject, pg.url, file=sys.stderr)

def run(batch):
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="pt-BR")
        pg = ctx.new_page()
        batch(pg, ctx, b)
        b.close()

# ------------------------------------------------------------------ lotes
def gestao(pg, ctx, b):
    login_gestao(pg, "gustavo.gestor", ["gestor", "publicador", "auditor", "elaborador", "exportador"])
    T = "table tbody tr"
    shoot(pg, "g_home", "/gestao/", {"rows": T, "h1": "h1"})
    shoot(pg, "g_painel", f"/gestao/processos/{P}/", {"h1": "h1", "sinais": ".sinal, [class*=sinal]", "rows": T})
    shoot(pg, "g_supervisao", f"/gestao/processos/{P}/supervisao", {"h1": "h1", "rows": T})
    shoot(pg, "g_visao", "/gestao/visao-geral", {"h1": "h1", "rows": T})
    shoot(pg, "g_criar_processo", "/gestao/processos/criar", {"h1": "h1", "fields": "form label"})
    for slug in ["identificacao", "perfis", "cronograma", "etapas", "classificacao", "inscricao", "anexos", "conteudo", "revisao"]:
        shoot(pg, f"g_compor_{slug}", f"/gestao/editais/{E76}/compor/{slug}",
              {"h1": "h1", "nav": "nav a", "fieldsets": "fieldset", "sections": "section", "rows": T})
    shoot(pg, "g_reaproveitar", f"/gestao/editais/{E76}/reaproveitar", {"h1": "h1"})
    shoot(pg, "g_previa", f"/gestao/editais/{E76}/previa", {"h1": "h1"})
    shoot(pg, "g_edital01", f"/gestao/editais/{E01}/", {"h1": "h1", "rows": T})
    shoot(pg, "g_edital51", f"/gestao/editais/{E51}/", {"h1": "h1", "rows": T})
    shoot(pg, "g_retificacao", f"/gestao/retificacoes/{RET}/", {"h1": "h1"})
    shoot(pg, "g_inscricoes51", f"/gestao/editais/{E51}/inscricoes", {"h1": "h1", "rows": T})
    shoot(pg, "g_marco51", f"/gestao/editais/{E51}/marcos/{M51}", {"h1": "h1", "rows": T})
    shoot(pg, "g_conducao51", f"/gestao/editais/{E51}/marcos/{M51}/conducao", {"h1": "h1", "rows": T})
    shoot(pg, "g_corte51", f"/gestao/editais/{E51}/marcos/{M51}/corte", {"h1": "h1", "rows": T})
    shoot(pg, "g_ocupacao51", f"/gestao/editais/{E51}/marcos/{M51}/ocupacao", {"h1": "h1", "rows": T})
    shoot(pg, "g_publicacoes51", f"/gestao/editais/{E51}/marcos/{M51}/publicacoes", {"h1": "h1", "rows": T})
    shoot(pg, "g_convocacao51", f"/gestao/editais/{E51}/marcos/{M51}/convocacao", {"h1": "h1", "rows": T})
    shoot(pg, "g_matriculas51", f"/gestao/editais/{E51}/matriculas", {"h1": "h1", "rows": T})
    shoot(pg, "g_auditoria51", f"/gestao/editais/{E51}/auditoria", {"h1": "h1", "rows": T})
    shoot(pg, "g_sorteio26", f"/gestao/editais/{E26}/marcos/{M26}/sorteio", {"h1": "h1", "rows": T})
    shoot(pg, "g_avisos51", f"/gestao/editais/{E51}/avisos", {"h1": "h1", "rows": T})
    shoot(pg, "g_modelos_aviso", "/gestao/modelos-de-aviso", {"h1": "h1", "rows": T})
    shoot(pg, "g_comissao", f"/gestao/processos/{P}/comissao", {"h1": "h1", "rows": T})
    shoot(pg, "g_autoridades", "/gestao/autoridades", {"h1": "h1", "rows": T})
    shoot(pg, "g_auditoria_proc", f"/gestao/processos/{P}/auditoria", {"h1": "h1", "rows": T})
    shoot(pg, "g_identificar_papeis", None, before=lambda pg: (pg.goto(BASE + "/gestao/identificar"),), sel={"papeis": "input[name=papeis]"})
    # distribuição e resultados de etapa, como presidente
    login_gestao(pg, "paulo.presidente", [])
    for et in ["d1", "d2"]:
        e = f"00000000-0000-0000-0051-0000000000{et}"
        shoot(pg, f"g_distrib51_{et}", f"/gestao/editais/{E51}/distribuicao/{e}", {"h1": "h1", "rows": T})
        shoot(pg, f"g_result_etapa51_{et}", f"/gestao/editais/{E51}/distribuicao/{e}/resultados", {"h1": "h1", "rows": T})
    login_gestao(pg, "joana.avaliadora", [])
    shoot(pg, "g_minhas_etapas", "/gestao/minhas-etapas", {"h1": "h1", "rows": T})
    shoot(pg, "g_mesa51_d1", f"/gestao/minhas-etapas/{E51}/00000000-0000-0000-0051-0000000000d1", {"h1": "h1", "rows": T})

def portal(pg, ctx, b):
    T = "table tbody tr"
    shoot(pg, "p_lista", "/selecoes/", {"h1": "h1", "cards": "article, .cartao, li.selecao", "form": "form"})
    shoot(pg, "p_lista_busca", "/selecoes/?busca=inform%C3%A1tica", {"h1": "h1", "cards": "article"})
    shoot(pg, "p_edital01", f"/selecoes/{E01}/", {"h1": "h1", "h2": "h2", "sections": "section"})
    shoot(pg, "p_edital51", f"/selecoes/{E51}/", {"h1": "h1", "h2": "h2", "sections": "section"})
    shoot(pg, "p_edital26", f"/selecoes/{E26}/", {"h1": "h1", "h2": "h2"})
    shoot(pg, "p_resultado51", f"/selecoes/resultados/{PUB51}/", {"h1": "h1", "rows": T})
    shoot(pg, "p_relacao26", f"/selecoes/sorteio/relacoes/{REL}/", {"h1": "h1", "rows": T})
    shoot(pg, "p_verificar26", f"/selecoes/sorteio/{SORT}/verificar", {"h1": "h1", "pre": "pre, code"})
    shoot(pg, "p_acesso", "/selecoes/acesso", {"h1": "h1", "form": "form"})
    # celular
    m = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, locale="pt-BR",
                      is_mobile=True, has_touch=True)
    mp = m.new_page()
    shoot(mp, "m_lista", "/selecoes/", {"h1": "h1", "cards": "article"})
    shoot(mp, "m_edital01", f"/selecoes/{E01}/", {"h1": "h1"})
    shoot(mp, "m_resultado51", f"/selecoes/resultados/{PUB51}/", {"h1": "h1"})
    m.close()

if __name__ == "__main__":
    which = sys.argv[1]
    run(globals()[which])
