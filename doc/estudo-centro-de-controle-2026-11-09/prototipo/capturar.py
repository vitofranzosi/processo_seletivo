"""Capturas do estudo: a tela atual e o protótipo, pelo Playwright, contra o servidor da 8150.

    cd backend && uv run python ../doc/estudo-centro-de-controle-2026-11-09/prototipo/capturar.py roteiro.json

O roteiro é uma lista de {"nome", "url", "identidade", "papeis"?, "largura"?, "altura"?,
"pagina_inteira"?, "clicar"?}. A entrada é a do seletor de demonstração — um POST em
`/gestao/identificar`, como o clique faria —, e cada identidade tem o seu contexto de navegador.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8150"
SAIDA = Path(__file__).resolve().parent.parent / "capturas"


def entrar(contexto, identidade, papeis):
    pagina = contexto.new_page()
    pagina.goto(f"{BASE}/gestao/identificar/demonstracao?proximo=/gestao/")
    token = pagina.locator("input[name=csrfmiddlewaretoken]").first.get_attribute("value")
    dados = {"csrfmiddlewaretoken": token, "proximo": "/gestao/", "subject": identidade}
    corpo = "&".join([f"{k}={v}" for k, v in dados.items()] + [f"papeis={p}" for p in papeis])
    pagina.request.post(
        f"{BASE}/gestao/identificar",
        data=corpo,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": pagina.url},
    )
    return pagina


def main():
    roteiro = json.loads(Path(sys.argv[1]).read_text())
    SAIDA.mkdir(exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contextos = {}
        for passo in roteiro:
            chave = (
                passo["identidade"],
                tuple(passo.get("papeis", [])),
                passo.get("largura", 1440),
            )
            if chave not in contextos:
                contexto = navegador.new_context(
                    viewport={
                        "width": passo.get("largura", 1440),
                        "height": passo.get("altura", 900),
                    },
                    locale="pt-BR",
                )
                contextos[chave] = entrar(contexto, passo["identidade"], passo.get("papeis", []))
            pagina = contextos[chave]
            violacoes = []
            pagina.on(
                "console",
                lambda m, v=violacoes: v.append(m.text)
                if "Content Security Policy" in m.text
                else None,
            )
            pagina.goto(BASE + passo["url"])
            for alvo in passo.get("clicar", []):
                for elemento in pagina.locator(alvo).all():
                    elemento.click()
            pagina.wait_for_timeout(200)
            destino = SAIDA / f"{passo['nome']}.png"
            pagina.screenshot(path=str(destino), full_page=passo.get("pagina_inteira", True))
            medida = pagina.evaluate(
                "() => [document.documentElement.scrollWidth, window.innerWidth]"
            )
            excesso = " ROLAGEM HORIZONTAL" if medida[0] > medida[1] else ""
            print(f"{destino.name}: {pagina.title()} {medida}{excesso} csp={len(violacoes)}")
        navegador.close()


if __name__ == "__main__":
    main()
