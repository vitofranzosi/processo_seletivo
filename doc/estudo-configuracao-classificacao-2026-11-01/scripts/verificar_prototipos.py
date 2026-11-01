"""Percursos do estudo em Chromium; não é teste de usabilidade com operadores."""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PASTA = Path(__file__).resolve().parent.parent
URL = "http://127.0.0.1:8768/prototipos/"
registros = []
erros = []
with sync_playwright() as p:
    navegador = p.chromium.launch()
    pagina = navegador.new_page(
        viewport={"width": 1440, "height": 1050}, reduced_motion="reduce"
    )
    pagina.on("pageerror", lambda e: erros.append(str(e)))

    def captura(nome):
        pagina.screenshot(
            path=str(PASTA / "capturas/prototipos" / f"{nome}.png"), full_page=True
        )
        registros.append(
            {
                "captura": nome,
                "url": pagina.url,
                "titulo": pagina.title(),
                "overflow": pagina.evaluate(
                    "document.documentElement.scrollWidth>innerWidth"
                ),
            }
        )

    for proposta in ["mapa", "caderno"]:
        pagina.goto(URL + proposta + ".html")
        captura(proposta + "-01-normal")
        pagina.get_by_role(
            "button", name="Incompleta · peso ausente", exact=True
        ).click()
        assert (
            pagina.get_by_role(
                "heading",
                name="Falta declarar o peso de Análise de títulos",
                exact=True,
            ).count()
            == 1
        )
        captura(proposta + "-02-incompleta")
        pagina.get_by_role(
            "button", name="Declarar peso 1 neste exemplo", exact=True
        ).click()
        assert (
            pagina.get_by_role(
                "heading",
                name="Falta declarar o peso de Análise de títulos",
                exact=True,
            ).count()
            == 0
        )
        assert pagina.evaluate("document.activeElement!==document.body")
        pagina.locator("#marca").uncheck()
        assert (
            pagina.get_by_role(
                "heading", name="A etapa deixou de poder entrar nos marcos", exact=True
            ).count()
            == 1
        )
        captura(proposta + "-03-marca-retirada")
        pagina.get_by_role(
            "button", name="Restaurar marca classificatória", exact=True
        ).click()
        pagina.get_by_role(
            "button", name="Circular · destino incorreto", exact=True
        ).click()
        assert (
            pagina.get_by_role(
                "heading",
                name="O corte alimentaria uma de suas próprias entradas",
                exact=True,
            ).count()
            == 1
        )
        captura(proposta + "-04-circular")
        pagina.get_by_role(
            "button", name="Alimentar Análise documental", exact=True
        ).click()
        pagina.get_by_role(
            "button",
            name="Exemplo fictício" if proposta == "mapa" else "Experimentar um caso",
            exact=True,
        ).click()
        pagina.get_by_label("Peso de títulos no exemplo", exact=True).select_option("2")
        assert "7,86" in pagina.locator("main").inner_text()
        captura(proposta + "-05-exemplo")
        pagina.get_by_role(
            "button",
            name="Revisão completa" if proposta == "mapa" else "Conferir compromissos",
            exact=True,
        ).first.click()
        if (
            proposta == "caderno"
            and pagina.get_by_role(
                "button", name="Abrir revisão completa", exact=True
            ).count()
        ):
            pagina.get_by_role(
                "button", name="Abrir revisão completa", exact=True
            ).click()
        pagina.get_by_role(
            "button", name="Confirmar leitura nesta maquete", exact=True
        ).click()
        assert (
            "Leitura confirmada apenas nesta página"
            in pagina.locator("main").inner_text()
        )
        pagina.get_by_role(
            "button", name="Ver hipótese pronta para operação", exact=True
        ).click()
        captura(proposta + "-06-revisao-pronta")
        pagina.get_by_role("button", name="Sorteio e tempo", exact=True).click()
        assert "28/10 00h00 ≤ 28/10 09h15" in pagina.locator("main").inner_text()
        captura(proposta + "-07-tempo-inviavel")
        pagina.get_by_role(
            "button", name="Ver hipótese após retificar e suceder", exact=True
        ).click()
        assert (
            pagina.get_by_role(
                "heading",
                name="Configuração temporal viável; ainda não executável",
                exact=True,
            ).count()
            == 1
        )
        pagina.get_by_role(
            "button", name="Ocorrência observada · pronta", exact=True
        ).click()
        captura(proposta + "-08-tempo-pronto")
        pagina.get_by_role("button", name="Normal", exact=True).click()
        pagina.get_by_label("Perfil em análise").select_option("TEC")
        assert "RESERVA" in pagina.locator("main").inner_text()
        captura(proposta + "-09-outro-perfil")
        pagina.set_viewport_size({"width": 390, "height": 844})
        pagina.goto(URL + proposta + ".html")
        pagina.get_by_role(
            "button", name="Inválida · marca retirada", exact=True
        ).click()
        captura(proposta + "-10-mobile")
        assert not pagina.evaluate("document.documentElement.scrollWidth>innerWidth")
        pagina.get_by_role(
            "button", name="Restaurar marca classificatória", exact=True
        ).focus()
        pagina.keyboard.press("Enter")
        assert (
            pagina.get_by_role(
                "heading", name="A etapa deixou de poder entrar nos marcos", exact=True
            ).count()
            == 0
        )
        pagina.set_viewport_size({"width": 1440, "height": 1050})
    navegador.close()
assert not erros, erros
(PASTA / "verificacao-prototipos.json").write_text(
    json.dumps(
        {
            "capturas": registros,
            "erros_javascript": erros,
            "conclusao": "Percursos, correções, foco e ausência de overflow móvel conferidos. Não é auditoria WCAG completa.",
        },
        ensure_ascii=False,
        indent=2,
    )
)
print(
    f"{len(registros)} capturas; dois percursos completos; nenhum erro JavaScript; sem overflow móvel."
)
