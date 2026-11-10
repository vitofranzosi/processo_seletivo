# ruff: noqa: E501 — roteiro de estudo, fora do lint do backend: as linhas longas são
# descrições de página e frases de asserção, que se leem melhor inteiras.
"""O "antes" dos protótipos: o HTML real de cada tela, salvo no estado em que o operador a vê.

    cd backend && uv run python ../doc/estudo-continuidade-operacional-2026-11-10/prototipo/capturar_antes.py

Pratica os atos de verdade no banco descartável do estudo (`ps_continuidade`, porta 8170) e salva a
página logo depois de cada um — a mensagem de sucesso só existe na resposta ao ato, e uma captura
posterior a perderia. Por isso o roteiro tem ordem, e roda **uma vez por rodada do cenário**: o C06
precisa estar recém-restaurado (`restaurar_cenario_de_treinamento --cenario C06`), e o C12 e o C15
no estado em que o estudo os deixou (a Cecília do C12 sem conferência; o C15 sem convocação).

O protótipo não reconstrói tela nenhuma à mão: o "depois" nasce deste HTML, por `montar_depois.py`.
As folhas e os scripts que as páginas citam vêm junto, do mesmo servidor, para que o protótipo tenha a
linguagem visual exata da gestão.
"""

import json
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("PASSEIO_BASE", "http://localhost:8170")
AQUI = Path(__file__).resolve().parent
SITIO = AQUI / "sitio"
ANTES = SITIO / "antes"

# Os identificadores do banco do estudo. Um banco novo tem outros: `ids.json` os substitui.
IDS = {
    "c06": "8f0f4129-4fa6-4b24-91cf-5a314e27da3b",
    "c12": "6e51666a-5ddf-4cad-9337-ae81c7477b5f",
    "c12_marco": "2f8b3812-cbe6-5f74-860e-a25a2e95348e",
    "c12_cecilia": "855fc021-9e0c-4259-a05c-90f50f3461ee",
    "c15": "71ed42cd-a440-4fc4-a6af-8402df0c274c",
    "c15_marco": "d57ac8ed-d5e6-56ef-8cf7-3d9533b6570a",
}
if (AQUI / "ids.json").exists():
    IDS.update(json.loads((AQUI / "ids.json").read_text()))


def entrar(contexto, identidade):
    pagina = contexto.new_page()
    pagina.goto(f"{BASE}/gestao/identificar/demonstracao?proximo=/gestao/")
    token = pagina.locator("input[name=csrfmiddlewaretoken]").first.get_attribute("value")
    pagina.request.post(
        f"{BASE}/gestao/identificar",
        data=f"csrfmiddlewaretoken={token}&proximo=/gestao/&subject={identidade}",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": pagina.url},
    )
    return pagina


def salvar(pagina, nome):
    # O token CSRF da sessão de demonstração não é evidência de nada: sai do arquivo versionado.
    html = re.sub(r'(name="csrfmiddlewaretoken" value=")[^"]*', r"\1", pagina.content())
    (ANTES / f"{nome}.html").write_text(html)
    for caminho in sorted(set(re.findall(r'(?:href|src)="(/static/[^"?]+)', html))):
        destino = SITIO / caminho.lstrip("/")
        if destino.exists():
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(pagina.request.get(BASE + caminho).body())
    print(f"salvo {nome} ({pagina.url.replace(BASE, '')})")


def clicar(pagina, seletor):
    with pagina.expect_navigation():
        pagina.locator(seletor).first.click()


def main():
    ANTES.mkdir(parents=True, exist_ok=True)
    so = set(sys.argv[1:])
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 1440, "height": 900}, locale="pt-BR")
        pagina = entrar(contexto, "treino.presidencia")

        if not so or "c06" in so:
            centro = f"/gestao/editais/{IDS['c06']}/centro/"
            pagina.goto(BASE + centro)
            salvar(pagina, "centro-c06-inicial")
            clicar(pagina, "a:has-text('Abrir a tela')")
            salvar(pagina, "sorteio-c06-inicial")
            clicar(pagina, "button:has-text('Publicar e congelar a relação')")
            salvar(pagina, "sorteio-c06-apos-fixar-a-ampla")
            pagina.goto(BASE + centro)
            salvar(pagina, "centro-c06-apos-fixar-a-ampla")

        if not so or "c12" in so:
            pagina.goto(f"{BASE}/gestao/editais/{IDS['c12']}/centro/")
            salvar(pagina, "centro-c12")
            convocacao = f"/gestao/editais/{IDS['c12']}/marcos/{IDS['c12_marco']}/convocacao"
            pagina.goto(BASE + convocacao)
            salvar(pagina, "convocacao-c12")
            documentos = f"{convocacao}/{IDS['c12_cecilia']}/documentos"
            pagina.goto(BASE + documentos)
            # O "conforme" exige a abertura; o arquivo abre por GET, como o clique em "Abrir".
            for href in set(
                re.findall(rf'href="({re.escape(documentos)}/[0-9a-f-]{{36}})"', pagina.content())
            ):
                pagina.request.get(BASE + href)
            for n in (1, 2):
                pagina.goto(BASE + documentos)
                pagina.locator(f"#conforme-{n}").check()
                clicar(pagina, f"#conforme-{n} >> xpath=ancestor::form[1] >> button[type=submit]")
            salvar(pagina, "documentos-c12-apos-conferir")

        if not so or "c15" in so:
            pagina.goto(f"{BASE}/gestao/editais/{IDS['c15']}/marcos/{IDS['c15_marco']}/convocacao")
            salvar(pagina, "convocacao-c15")

        navegador.close()


if __name__ == "__main__":
    main()
