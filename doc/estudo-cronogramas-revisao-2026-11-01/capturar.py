"""Capturas e medições das POCs, num Chromium sem janela (Playwright do grupo `navegador`).

Executar de backend/: .venv/bin/python ../doc/estudo-cronogramas-revisao-2026-11-01/capturar.py
Abre os HTML por file://, sem servidor. Grava em capturas/ as imagens e medidas.json.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PASTA = Path(__file__).resolve().parent
POC = (PASTA / "prototipo").as_uri()
SAIDA = PASTA / "capturas"
LARGURAS = {
    "desktop": (1440, 1000),
    "notebook": (1024, 768),
    "tablet": (768, 1024),
    "celular": (375, 812),
}

# Quantos pontos de foco o teclado atravessa até o fim da lista, e se a página rola de lado.
MEDIR = """() => {
  const painel = document.querySelector('#painel') || document.querySelector('main');
  const focaveis = [...painel.querySelectorAll('a[href],button,summary,[tabindex="0"]')]
    .filter(e => e.checkVisibility());
  return {
    alturaPagina: document.documentElement.scrollHeight,
    alturaPainel: Math.round(painel.getBoundingClientRect().height),
    rolagemLateral: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    focaveis: focaveis.length,
    // Do título do calendário ao fim: a Agenda como o usuário a percorre, grade incluída.
    alturaDaAgenda: (() => { const t = document.querySelector('.titulo-do-mes');
      if (!t) return null;
      const topo = t.getBoundingClientRect().top + scrollY;
      return Math.round(document.documentElement.scrollHeight - topo); })(),
    pxPorDia: (() => { const r = document.querySelector('.regua');
      return r ? +(r.getBoundingClientRect().width / r.children.length).toFixed(1) : null; })(),
  };
}"""

# O defeito da primeira versão: o marco pontual fora da coluna do seu dia. Confere cada marco e
# cada barra contra a célula da régua do mesmo dia.
CONFERIR = """() => {
  const celulas = [...document.querySelectorAll('.regua .dia-regua')]
    .map(c => c.getBoundingClientRect());
  const erros = [];
  let marcos = 0, barras = 0;
  for (const m of document.querySelectorAll('.trilha .marco')) {
    if (!m.checkVisibility()) continue;
    const r = m.getBoundingClientRect();
    const c = celulas[+m.dataset.dia - 1], centro = r.left + r.width / 2;
    marcos++;
    if (centro < c.left || centro > c.right) erros.push(['marco', m.dataset.dia, centro]);
  }
  for (const b of document.querySelectorAll('.trilha .barra')) {
    if (!b.checkVisibility()) continue;
    const r = b.getBoundingClientRect();
    const i = celulas[+b.dataset.de - 1], f = celulas[+b.dataset.ate - 1];
    barras++;
    const fora = Math.abs(r.left - i.left) > 1.5 || Math.abs(r.right - f.right) > 1.5;
    if (fora) erros.push(['barra', b.dataset.de, b.dataset.ate]);
  }
  return {marcos, barras, erros};
}"""


RETIFICADO = "visao=c&cenario=retificacao&referencia=2026-11-05"
INSCRICOES_EM_CURSO = "visao=c&cenario=denso&especie=inscricoes&fase=em_curso"
SO_EVENTOS = INSCRICOES_EM_CURSO + "&alcance=eventos"


def no_painel(pagina):
    pagina.evaluate(
        "() => { const t = document.querySelector('#titulo-mes');"
        " if (t) window.scrollBy(0, t.getBoundingClientRect().top - 8); }"
    )


def main():
    SAIDA.mkdir(exist_ok=True)
    medidas, conferencias, avisos = [], [], []
    with sync_playwright() as p:
        navegador = p.chromium.launch()

        def abrir(caminho, largura):
            w, h = LARGURAS[largura]
            pg = navegador.new_page(viewport={"width": w, "height": h})
            pg.on(
                "console",
                lambda m: avisos.append(m.text) if m.type in ("error", "warning") else None,
            )
            pg.on("pageerror", lambda e: avisos.append(str(e)))
            pg.goto(f"{POC}/{caminho}")
            pg.wait_for_timeout(150)
            return pg

        for visao in "cab":
            for largura in LARGURAS:
                pg = abrir(f"index.html?visao={visao}&cenario=denso", largura)
                medida = pg.evaluate(MEDIR)
                medidas.append(
                    {"tela": visao, "cenario": "23 Editais", "largura": largura, **medida}
                )
                if visao != "b":
                    conferencia = pg.evaluate(CONFERIR)
                    conferencias.append({"tela": visao, "largura": largura, **conferencia})
                no_painel(pg)
                pg.screenshot(path=SAIDA / f"{visao}-{largura}.jpg", quality=80)
                if largura in ("desktop", "celular"):
                    pg.screenshot(
                        path=SAIDA / f"{visao}-{largura}-inteira.jpg", quality=80, full_page=True
                    )
                pg.close()

        # Calendário + lista (hoje) contra calendário + C: a mesma página, com e sem a troca.
        for largura in ("desktop", "celular"):
            pg = abrir("agenda-completa.html?visao=c", largura)
            medida = pg.evaluate(MEDIR)
            medidas.append({"tela": "agenda-completa-com-c", "largura": largura, **medida})
            pg.screenshot(path=SAIDA / f"agenda-completa-{largura}.jpg", quality=80, full_page=True)
            pg.close()

        for nome in ("atual-mes", "atual-mes-denso", "atual-proximos", "atual-proximos-denso"):
            for largura in ("desktop", "celular"):
                pg = abrir(f"{nome}.html", largura)
                medidas.append({"tela": nome, "largura": largura, **pg.evaluate(MEDIR)})
                pg.screenshot(path=SAIDA / f"{nome}-{largura}.jpg", quality=80, full_page=True)
                pg.close()

        casos = [
            ("c-dezembro", "index.html?visao=c&cenario=denso&mes=2026-12", "desktop"),
            ("c-outubro", "index.html?visao=c&cenario=denso&mes=2026-10", "desktop"),
            ("c-retificacao-antes", "index.html?visao=c&cenario=retificacao", "desktop"),
            ("c-retificacao-depois", "index.html?" + RETIFICADO, "desktop"),
            ("c-inscricoes-em-curso", "index.html?" + INSCRICOES_EM_CURSO, "desktop"),
            ("c-inscricoes-so-eventos", "index.html?" + SO_EVENTOS, "desktop"),
            ("a-dezembro", "index.html?visao=a&cenario=denso&mes=2026-12", "desktop"),
        ]
        for nome, caminho, largura in casos:
            pg = abrir(caminho, largura)
            conferencias.append({"tela": nome, "largura": largura, **pg.evaluate(CONFERIR)})
            no_painel(pg)
            pg.screenshot(path=SAIDA / f"{nome}.jpg", quality=80)
            pg.close()

        # C aberto: a sequência textual de um Edital, pelo teclado, e a ficha de um evento.
        for largura in ("desktop", "celular"):
            pg = abrir("index.html?visao=c&cenario=demo", largura)
            alvo = pg.locator("details.linha-edital summary", has_text="Edital 102/2026")
            alvo.focus()
            pg.keyboard.press("Enter")
            alvo.scroll_into_view_if_needed()
            pg.evaluate("window.scrollBy(0, -60)")
            pg.screenshot(path=SAIDA / f"c-aberto-{largura}.jpg", quality=80)
            conferencias.append({"tela": "c-aberto", "largura": largura, **pg.evaluate(CONFERIR)})
            if largura == "desktop":
                pg.locator("details[open] .linha-evento").first.focus()
                pg.keyboard.press("Enter")
                pg.wait_for_timeout(100)
                pg.screenshot(path=SAIDA / "c-ficha-teclado.jpg", quality=80)
                pg.keyboard.press("Escape")
                foco = pg.evaluate("document.activeElement.textContent")
                conferencias.append({"tela": "ficha", "focoAoFechar": foco})
            pg.close()
        navegador.close()

    (SAIDA / "medidas.json").write_text(
        json.dumps(
            {"medidas": medidas, "conferencias": conferencias, "avisosDoConsole": avisos},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    erros = [c for c in conferencias if c.get("erros")]
    print(
        f"{len(medidas)} medidas, {len(conferencias)} conferências, "
        f"{len(erros)} com erro, {len(avisos)} avisos."
    )
    sys.exit(1 if erros or avisos else 0)


if __name__ == "__main__":
    main()
