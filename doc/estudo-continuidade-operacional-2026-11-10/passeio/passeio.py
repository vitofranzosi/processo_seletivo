"""O walkthrough do estudo, pelo Playwright, contra o servidor da 8170.

    cd backend && uv run python \
        ../doc/estudo-continuidade-operacional-2026-11-10/passeio/passeio.py \
        <identidade> '<passos em JSON>' [--papeis gestor,publicador]

Cada chamada é um trecho da jornada. A sessão de cada identidade fica guardada num arquivo de
estado fora do repositório, e por isso o trecho seguinte continua de onde o anterior parou — como o
operador, que não entra de novo a cada clique. Entrar é o POST do seletor de demonstração, o mesmo
que o clique faria.

Passos (uma lista; cada um é um objeto com uma chave):
    {"ir": "/gestao/..."}                      navega
    {"clicar": "<seletor Playwright>"}         clica no primeiro que casar, e espera a navegação
    {"preencher": ["<seletor>", "valor"]}       preenche um campo
    {"marcar": "<seletor>"}                    marca uma caixa
    {"anexar": ["<seletor>", "/caminho.pdf"]}  escolhe o arquivo de um campo de envio
    {"escolher": ["<seletor>", "valor"]}        escolhe uma opção de <select>
    {"capturar": "nome", "inteira": true}      grava capturas/<nome>.png
    {"texto": "<seletor>"}                     imprime o texto visível (padrão: main)
    {"links": "<seletor>"}                     imprime os links e botões, com o destino
    {"esperar": 500}                           espera, em milissegundos
    {"campos": "<seletor>"}                    imprime os campos do formulário (nome, tipo, valor)
    {"posicao": "<seletor>"}                   imprime a altura em que o elemento aparece

Não há asserção aqui: este é o caderno do percurso. A validação dos protótipos é outra peça.
"""

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("PASSEIO_BASE", "http://localhost:8170")
AQUI = Path(__file__).resolve().parent
CAPTURAS = AQUI.parent / "capturas"
# O estado da sessão não é evidência, é credencial de demonstração: fica fora do repositório.
ESTADOS = Path(os.environ.get("PASSEIO_ESTADOS", "/tmp/passeio-continuidade"))


def entrar(contexto, identidade, papeis):
    pagina = contexto.new_page()
    # O candidato entra pelo código no e-mail, e não pelo seletor: a sessão começa vazia, e o
    # próprio roteiro percorre o acesso do portal.
    if identidade.startswith("portal:"):
        return pagina
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


def imprimir_links(pagina, seletor):
    for item in pagina.locator(f"{seletor} a, {seletor} button").all():
        try:
            if not item.is_visible():
                continue
            texto = " ".join(item.inner_text().split())[:90]
            destino = item.get_attribute("href") or (
                "[" + (item.get_attribute("formaction") or item.get_attribute("type") or "") + "]"
            )
            print(f"  · {texto} -> {destino}")
        except Exception:  # noqa: BLE001 — elemento que some no meio da leitura não é achado
            continue


def main():
    identidade = sys.argv[1]
    passos = json.loads(sys.argv[2])
    papeis = []
    if "--papeis" in sys.argv:
        papeis = sys.argv[sys.argv.index("--papeis") + 1].split(",")
    largura = int(os.environ.get("PASSEIO_LARGURA", "1440"))
    ESTADOS.mkdir(parents=True, exist_ok=True)
    CAPTURAS.mkdir(exist_ok=True)
    estado = ESTADOS / f"{identidade}-{'-'.join(papeis) or 'sem-papel'}.json"
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(
            viewport={"width": largura, "height": 900},
            locale="pt-BR",
            storage_state=str(estado) if estado.exists() else None,
        )
        pagina = contexto.new_page() if estado.exists() else entrar(contexto, identidade, papeis)
        violacoes = []
        pagina.on(
            "console",
            lambda m: violacoes.append(m.text) if "Content Security Policy" in m.text else None,
        )
        # A confirmação nativa é parte do ato em algumas telas: aceita, e registra a pergunta.
        pagina.on("dialog", lambda d: (print(f"  [diálogo] {d.message}"), d.accept()))
        for passo in passos:
            try:
                executar(pagina, passo)
            except Exception as erro:  # noqa: BLE001 — o caderno registra e segue, como o operador
                print(f"✗ {passo}: {str(erro).splitlines()[0]}")
                break
        medida = pagina.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
        rolagem = " ROLAGEM HORIZONTAL" if medida[0] > medida[1] else ""
        print(
            f"= {pagina.url.replace(BASE, '')} · {pagina.title()} · csp={len(violacoes)}{rolagem}"
        )
        contexto.storage_state(path=str(estado))
        navegador.close()


def executar(pagina, passo):
    if "ir" in passo:
        resposta = pagina.goto(BASE + passo["ir"])
        print(f"→ {passo['ir']} [{resposta.status if resposta else '?'}]")
    elif "clicar" in passo:
        with pagina.expect_navigation(wait_until="load", timeout=15000):
            pagina.locator(passo["clicar"]).first.click()
        print(f"✓ clicou {passo['clicar']} → {pagina.url.replace(BASE, '')}")
    elif "clicar_sem_navegar" in passo:
        pagina.locator(passo["clicar_sem_navegar"]).first.click()
        print(f"✓ clicou {passo['clicar_sem_navegar']}")
    elif "preencher" in passo:
        pagina.locator(passo["preencher"][0]).first.fill(passo["preencher"][1])
    elif "anexar" in passo:
        pagina.locator(passo["anexar"][0]).first.set_input_files(passo["anexar"][1])
    elif "marcar" in passo:
        pagina.locator(passo["marcar"]).first.check()
    elif "escolher" in passo:
        pagina.locator(passo["escolher"][0]).first.select_option(passo["escolher"][1])
    elif "capturar" in passo:
        destino = CAPTURAS / f"{passo['capturar']}.png"
        pagina.screenshot(path=str(destino), full_page=passo.get("inteira", True))
        print(f"📷 {destino.name}")
    elif "texto" in passo:
        seletor = passo["texto"] or "main"
        texto = pagina.locator(seletor).first.inner_text()
        print("\n".join(linha for linha in texto.splitlines() if linha.strip()))
    elif "links" in passo:
        imprimir_links(pagina, passo["links"] or "main")
    elif "esperar" in passo:
        pagina.wait_for_timeout(passo["esperar"])
    elif "campos" in passo:
        for campo in pagina.locator(
            f"{passo['campos'] or 'main'} :is(input, select, textarea)"
        ).all():
            tipo = campo.get_attribute("type") or campo.evaluate("e => e.tagName")
            if tipo == "hidden":
                continue
            print(
                f"  ▢ {tipo} name={campo.get_attribute('name')} "
                f"id={campo.get_attribute('id')} value={campo.get_attribute('value')}"
            )
    elif "posicao" in passo:
        # Onde, na página, o operador encontra o que veio buscar: a distância da dobra é a medida
        # de "a providência leva ao lugar do ato" que o estudo usa.
        caixa = pagina.locator(passo["posicao"]).first.bounding_box()
        altura = pagina.evaluate("() => document.documentElement.scrollHeight")
        y = round(caixa["y"]) if caixa else None
        print(f"  ↧ {passo['posicao']}: y={y} de {altura} (dobra em 900)")


if __name__ == "__main__":
    main()
