"""Capturas do complemento de generalidade (06/11/2026): as famílias que não são só sorteio. Só GET.

Rodar, do `backend/`, com o servidor da `capturar.py` no ar:

    uv run python ../doc/estudo-orientacao-da-jornada-2026-11-06/roteiro/capturar_generalidade.py
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UX_BASE", "http://localhost:8140")
SAIDA = Path(__file__).resolve().parent.parent / "capturas"

E91 = "/gestao/editais/3693043f-0281-43ba-8145-959fb93321a0/"
M91 = "marcos/92af8ee6-c3b6-40bf-8bc1-b0ad1d73a0fb"  # o 1º Perfil, com 8 inscrições
E35 = "/gestao/editais/c6ea917b-e8da-42d9-a32c-38afcd8da1f3/"
E51 = "/gestao/editais/e65d328e-0886-495d-a397-a6964b5196ea/"


def entrar(nav, papel):
    pagina = nav.new_context(viewport={"width": 1280, "height": 900}).new_page()
    pagina.goto(BASE + "/gestao/identificar/demonstracao")
    with pagina.expect_navigation():
        if papel.startswith("@"):
            pagina.locator(f"button[name=identidade_sugerida][value='{papel[1:]}']").first.click()
        else:
            pagina.locator(f"form:has(input[name=papeis][value='{papel}']) button").first.click()
    return pagina


def foto(pagina, url, nome, altura=None):
    pagina.goto(BASE + url)
    opcoes = {"path": str(SAIDA / f"{nome}.jpg"), "type": "jpeg", "quality": 82, "full_page": True}
    if altura:
        opcoes["clip"] = {"x": 0, "y": 0, "width": 1280, "height": altura}
    pagina.screenshot(**opcoes)
    print(nome)


with sync_playwright() as p:
    nav = p.chromium.launch()
    g = entrar(nav, "gestor")
    foto(g, E91, "30-detalhe-91-gestor-sem-etapas", altura=1500)
    foto(g, E91 + M91 + "/conducao", "31-conducao-91-falta-a-ordem-sem-avaliacao")
    foto(g, E91 + M91, "32-ordem-91-emitivel-sem-ninguem-avaliado")
    foto(g, E51 + "marcos/00000000-0000-0000-0051-0000000000a1/conducao", "35-conducao-51-pontuacao")
    pres = entrar(nav, "@presidente.b")
    foto(pres, E91 + "distribuicao/7589e191-1bf0-4635-aeed-ab18fb38efe7", "33-distribuicao-91-sem-avaliador", altura=1100)
    foto(pres, "/gestao/minhas-etapas", "34-minhas-etapas-91-presidencia", altura=1100)
    foto(g, "/gestao/processos/3f5296ca-794d-4dc2-b7c4-b154a4b2ea65/alocacoes", "36-alocacoes-35-etapas-sem-ninguem", altura=1100)
    nav.close()
