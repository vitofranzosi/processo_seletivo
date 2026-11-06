"""Capturas do detalhe do Edital, antes e depois da 127, por papel. Não é teste da suíte.

Só GET: nada aqui pratica ato. O banco é o clone do banco do estudo de 06/11 (`ps_spec127`, num
container `postgres:18` próprio, porta 55437), migrado. O servidor "antes" roda o código da `main`
(exportado com `git archive`); o "depois", o desta branch. Os dois com o seletor de identidade:

    DB_HOST=localhost DB_PORT=55437 DB_NAME=ps_spec127 DB_USER=postgres DB_PASSWORD=estudo \
      DB_RUNTIME_USER=postgres DB_RUNTIME_PASSWORD=estudo INTERFACE_SELETOR_IDENTIDADE=true \
      uv run python manage.py runserver 8129

E, do `backend/`, com o grupo `navegador`:

    UX_BASE=http://localhost:8129 UX_SAIDA=../specs/127-andamento-da-selecao/capturas/depois \
      uv run python ../specs/127-andamento-da-selecao/capturas/capturar.py

Além das imagens, grava `medidas.json`: a altura da página e onde termina "O que fazer agora" (UX-232,
SC-1240), e se a página rola de lado (SC-1241).
"""

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UX_BASE", "http://localhost:8129")
SAIDA = Path(os.environ.get("UX_SAIDA", Path(__file__).resolve().parent / "depois"))
SAIDA.mkdir(parents=True, exist_ok=True)
ABRIR = os.environ.get("UX_ABRIR", "")  # "1" abre o primeiro Perfil do "Andamento da seleção" (B2)

E = {
    "35": "c6ea917b-e8da-42d9-a32c-38afcd8da1f3",
    "57": "d3fa2087-7927-4f51-bdee-982caeb38285",
    "26": "1bddd8ac-d54b-483a-b449-732802161b13",
    "51": "e65d328e-0886-495d-a397-a6964b5196ea",
    "91": "3693043f-0281-43ba-8145-959fb93321a0",
    "72": "7ca63ff6-5b55-49da-ab25-e48fcc2b350a",
    "90": "c1620fe6-2f43-48f4-8804-0c78dbdba3cf",
}
ACOES = "section[aria-labelledby=acoes-titulo]"
#: (Edital, papel) — os do quickstart. `@` é a identidade sugerida da demonstração.
CASOS = [
    ("35", "gestor"),
    ("35", "publicador"),
    ("35", "elaborador"),
    ("57", "gestor"),
    ("51", "gestor"),
    ("91", "@arodrigues"),
    ("91", "gestor"),
    ("72", "gestor"),
    ("26", "gestor"),
    ("90", "elaborador"),
]


def entrar(contexto, papel):
    pagina = contexto.new_page()
    pagina.goto(BASE + "/gestao/identificar/demonstracao")
    with pagina.expect_navigation():
        if papel.startswith("@"):
            botao = pagina.locator(f"button[name=identidade_sugerida][value='{papel[1:]}']").first
        else:
            botao = pagina.locator(f"form:has(input[name=papeis][value='{papel}']) button").first
        # Pelo DOM, e não pelo ponteiro: a 375 px o painel "Sobre o sistema" cobre o botão.
        botao.evaluate("b => b.click()")
    assert "/identificar" not in pagina.url, f"não entrou como {papel}: {pagina.url}"
    return pagina


def medir(pagina):
    return pagina.evaluate(
        """(seletor) => {
            const acoes = document.querySelector(seletor);
            const caixa = acoes ? acoes.getBoundingClientRect() : null;
            const fim = (sel) => {
                const nos = acoes ? acoes.querySelectorAll(sel) : [];
                if (!nos.length) return null;
                return Math.round(nos[nos.length - 1].getBoundingClientRect().bottom + window.scrollY);
            };
            return {
                // UX-232: onde termina a lista das providências, e onde terminam as da pessoa.
                fim_das_providencias: fim(":scope > ul.providencias, :scope > p.nada-em-aberto"),
                fim_das_suas: fim(":scope > ul.providencias.suas"),
                altura: document.documentElement.scrollHeight,
                fim_do_nivel_1: caixa ? Math.round(caixa.bottom + window.scrollY) : null,
                rola_de_lado: document.documentElement.scrollWidth > window.innerWidth,
                texto: acoes ? acoes.innerText.slice(0, 1500) : "",
            };
        }""",
        ACOES,
    )


def main():
    medidas = {}
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        for largura in (1280, 375):
            for numero, papel in CASOS:
                contexto = navegador.new_context(viewport={"width": largura, "height": 900})
                pagina = entrar(contexto, papel)
                pagina.goto(f"{BASE}/gestao/editais/{E[numero]}/")
                if ABRIR:
                    resumo = pagina.locator("details.perfil-do-andamento > summary")
                    if resumo.count():
                        resumo.first.click()
                nome = f"{numero}-{papel.strip('@').replace('.', '-')}-{largura}"
                pagina.screenshot(
                    path=str(SAIDA / f"{nome}.jpg"), type="jpeg", quality=80, full_page=True
                )
                medidas[nome] = medir(pagina)
                print(nome, medidas[nome])
                contexto.close()
        navegador.close()
    (SAIDA / "medidas.json").write_text(json.dumps(medidas, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
