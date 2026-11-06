"""Roteiro de captura do estudo de orientação da jornada (06/11/2026). Não é teste da suíte.

Só GET: nenhuma captura daqui pratica ato. As quatro transições (semente, corte, apuração) foram
praticadas antes, por `transicao.py`, e suas capturas foram copiadas para `capturas/` à parte.

Banco: `ps_jornada`, clone de `processo_seletivo_guia` (a cópia pseudonimizada do Edital 35 usada no
guia de 05/11), num container `postgres:18`, migrado na base `250efe97`. Servidor:

    DB_HOST=localhost DB_PORT=55435 DB_NAME=ps_jornada DB_USER=postgres ... \
    INTERFACE_SELETOR_IDENTIDADE=true manage.py runserver 8140

Rodar, do `backend/`, com o grupo `navegador`:

    uv run python ../doc/estudo-orientacao-da-jornada-2026-11-06/roteiro/capturar.py
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UX_BASE", "http://localhost:8140")
SAIDA = Path(os.environ.get("UX_SAIDA", Path(__file__).resolve().parent.parent / "capturas"))
SAIDA.mkdir(parents=True, exist_ok=True)

E = {
    "35": "c6ea917b-e8da-42d9-a32c-38afcd8da1f3",
    "57": "d3fa2087-7927-4f51-bdee-982caeb38285",
    "26": "1bddd8ac-d54b-483a-b449-732802161b13",
    "51": "e65d328e-0886-495d-a397-a6964b5196ea",
    "91": "3693043f-0281-43ba-8145-959fb93321a0",
    "72": "7ca63ff6-5b55-49da-ab25-e48fcc2b350a",
    "90": "c1620fe6-2f43-48f4-8804-0c78dbdba3cf",
}
M35_CEFOR = "e5c32a65-e641-4416-8cb8-f729542fe21a"
M35_VITORIA = "3000f443-9943-4b18-9a9c-7d01e419487b"
M57_DESIGN = "68f0c761-6a44-4ee5-92d0-c78afaefa130"
PROCESSO_35 = "3f5296ca-794d-4dc2-b7c4-b154a4b2ea65"
ACOES = "section[aria-labelledby=acoes-titulo]"
CLASSIFICACAO = "section[aria-labelledby=classificacao-titulo]"


def edital(n, resto=""):
    return f"/gestao/editais/{E[n]}/{resto}"


def entrar(contexto, papel):
    pagina = contexto.new_page()
    pagina.goto(BASE + "/gestao/identificar/demonstracao")
    with pagina.expect_navigation():
        if papel.startswith("@"):
            pagina.locator(f"button[name=identidade_sugerida][value='{papel[1:]}']").first.click()
        else:
            # O botão leva a identidade sugerida (name/value); requestSubmit() sem ele a perde.
            pagina.locator(f"form:has(input[name=papeis][value='{papel}']) button").first.click()
    assert "/identificar" not in pagina.url, f"não entrou como {papel}: {pagina.url}"
    return pagina


def foto(pagina, nome, *, seletor=None, inteira=False, altura=None):
    caminho = str(SAIDA / f"{nome}.jpg")
    if seletor:
        pagina.locator(seletor).first.screenshot(path=caminho, type="jpeg", quality=82)
    elif altura:
        pagina.screenshot(
            path=caminho, type="jpeg", quality=82, full_page=True,
            clip={"x": 0, "y": 0, "width": 1280, "height": altura},
        )
    else:
        pagina.screenshot(path=caminho, type="jpeg", quality=82, full_page=inteira)
    print(nome)
    return caminho


def lado_a_lado(navegador, nome, titulos_e_imagens, colunas=3):
    """Uma prancha com recortes de telas reais, para comparar o mesmo cartão em Editais diferentes."""
    celulas = "".join(
        f'<figure><figcaption>{t}</figcaption><img src="file://{c}"></figure>'
        for t, c in titulos_e_imagens
    )
    html = f"""<html><body style="margin:0;padding:16px;background:#eef0ec;font:14px system-ui">
    <div style="display:grid;grid-template-columns:repeat({colunas},1fr);gap:16px">{celulas}</div>
    <style>figure{{margin:0;background:#fff;padding:8px;border:1px solid #ccc}}
    figcaption{{font-weight:600;margin:0 0 6px}} img{{width:100%}}</style></body></html>"""
    temp = SAIDA / f"_{nome}.html"
    temp.write_text(html)
    pagina = navegador.new_page(viewport={"width": 1280 if colunas < 3 else 1500, "height": 600})
    pagina.goto(f"file://{temp}")
    pagina.wait_for_timeout(300)
    pagina.screenshot(path=str(SAIDA / f"{nome}.jpg"), type="jpeg", quality=82, full_page=True)
    pagina.close()
    temp.unlink()
    for _, c in titulos_e_imagens:
        Path(c).unlink()
    print(nome)


with sync_playwright() as p:
    nav = p.chromium.launch()
    novo = lambda: nav.new_context(viewport={"width": 1280, "height": 900})  # noqa: E731

    g = entrar(novo(), "gestor")
    g.goto(BASE + "/gestao/")
    foto(g, "01-lista-gestor")
    g.goto(BASE + edital("35"))
    foto(g, "04-detalhe-35-gestor", inteira=True)

    # O mesmo cartão em cinco Editais em momentos diferentes.
    cartoes = []
    for n, momento in [
        ("57", "57 — relações congeladas, semente não observada"),
        ("26", "26 — ampla sorteada e apurada; PPP sem relação"),
        ("91", "91 — em avaliação pela comissão"),
        ("51", "51 — em convocação"),
        ("72", "72 — Retificação homologada à espera"),
        ("35", "35 — convocação com pendência"),
    ]:
        g.goto(BASE + edital(n))
        cartoes.append((momento, foto(g, f"_acoes-{n}", seletor=ACOES)))
    lado_a_lado(nav, "05-o-que-fazer-agora-em-seis-editais", cartoes)

    resumos = []
    for n, momento in [
        ("57", "57 — uma relação congelada, a outra não; semente pendente"),
        ("91", "91 — sem relação nenhuma; Edital por avaliação"),
    ]:
        g.goto(BASE + edital(n))
        resumos.append((momento, foto(g, f"_classif-{n}", seletor=CLASSIFICACAO)))
    lado_a_lado(nav, "06-classificacao-57-e-91", resumos, colunas=2)

    g.goto(BASE + edital("57", f"marcos/{M57_DESIGN}/sorteio"))
    foto(g, "07-sorteio-57-semente-pendente", seletor="section[aria-labelledby=titulo-ocorrencia]")
    g.goto(BASE + edital("35", f"marcos/{M35_CEFOR}/sorteio"))
    g.get_by_text("Não congele a relação hoje").first.evaluate(
        "e => window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - 140)"
    )
    foto(g, "08-sorteio-35-aviso-fora-de-contexto")
    g.goto(BASE + edital("57"))
    foto(g, "04b-detalhe-57-gestor", inteira=True)
    g.goto(BASE + edital("57", f"marcos/{M57_DESIGN}/conducao"))
    foto(g, "09b-conducao-57-design", inteira=True)
    g.goto(BASE + edital("35", f"marcos/{M35_CEFOR}/conducao"))
    foto(g, "10-conducao-35-cefor", inteira=True)
    g.goto(BASE + edital("35", f"marcos/{M35_VITORIA}/conducao"))
    foto(g, "11-conducao-35-vitoria-sem-inscritos", inteira=True)
    g.goto(BASE + edital("35", f"marcos/{M35_VITORIA}/convocacao"))
    foto(g, "12-convocacao-35-vitoria-orientacao-contraditoria", altura=1250)
    g.goto(BASE + edital("35", f"marcos/{M35_CEFOR}/convocacao"))
    foto(g, "22-convocacao-35-ampla", altura=1700)
    g.goto(BASE + edital("35", "atos/encerrar"))
    foto(g, "16-encerrar-35-unica-lista-de-pendencias", inteira=True)
    g.goto(BASE + "/gestao/visao-geral")
    foto(g, "19-visao-geral", altura=1500)
    g.goto(BASE + "/gestao/agenda")
    foto(g, "20-agenda", altura=1100)
    g.goto(BASE + f"/gestao/processos/{PROCESSO_35}/")
    foto(g, "21-processo-35", inteira=True)

    el = entrar(novo(), "elaborador")
    el.goto(BASE + "/gestao/")
    foto(el, "02-lista-elaborador")
    el.goto(BASE + edital("90"))
    foto(el, "03-detalhe-90-elaboracao", inteira=True)

    pub = entrar(novo(), "publicador")
    pub.goto(BASE + edital("35"))
    foto(pub, "17-publicador-35", altura=1500)

    pres = entrar(novo(), "@presidente.b")
    pres.goto(BASE + "/gestao/")
    a = foto(pres, "_pres-lista", seletor="section.acoes-disponiveis")
    pres.goto(BASE + edital("91"))
    b = foto(pres, "_pres-detalhe", seletor=ACOES)
    lado_a_lado(
        nav,
        "18-presidente-91-lista-e-detalhe",
        [("Lista — a faixa da 104", a), ("Detalhe do 91 — o cartão", b)],
        colunas=2,
    )
    nav.close()
