# ruff: noqa: E501 — roteiro de estudo, fora do lint do backend: as linhas longas são
# descrições de página e frases de asserção, que se leem melhor inteiras.
"""O "depois" dos protótipos: o HTML real do "antes", transformado no navegador e salvo estático.

    cd backend && uv run python ../doc/estudo-continuidade-operacional-2026-11-10/prototipo/montar_depois.py

Cada página do "depois" é uma página do "antes" mais uma transformação de `transformacoes/`, e nada
além disso. É o que garante que o protótipo parte da tela real, e que a diferença entre os dois é
exatamente a melhoria proposta — e não um redesenho escondido. Se a tela real mudar a ponto de a
transformação não encontrar o que muda, a montagem falha alto (`exigir` em `comum.js`).
"""

import html
import json
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from servidor import servir

AQUI = Path(__file__).resolve().parent
SITIO = AQUI / "sitio"
TRANSFORMACOES = AQUI / "transformacoes"
PORTA = 8172

# (página do depois, página do antes de que nasce, transformação, contexto, melhorias, descrição)
PAGINAS = [
    (
        "centro-c06-inicial",
        "centro-c06-inicial",
        "centro",
        {
            "ancoras": {
                "Abrir a tela": "sorteio-c06-inicial.html#titulo-recortes",
                "Fixar os participantes": "sorteio-c06-inicial.html#titulo-recortes",
            },
            "d5": False,
        },
        "M-02",
        "Jornada A, C06 · o Centro antes de qualquer ato; a providência leva aos recortes, e não ao topo",
    ),
    (
        "sorteio-c06-inicial",
        "sorteio-c06-inicial",
        "sorteio",
        {
            "paginas": {"sorteioApos": "sorteio-c06-apos-fixar-a-ampla.html"},
            "centro": "centro-c06-inicial.html",
        },
        "M-03, M-06, D-5",
        "Jornada A, C06 · a tela do sorteio antes de fixar: o objetivo, os passos e o ato antes do método",
    ),
    (
        "sorteio-c06-apos-fixar-a-ampla",
        "sorteio-c06-apos-fixar-a-ampla",
        "sorteio",
        {
            "paginas": {"sorteioApos": "sorteio-c06-apos-fixar-a-ampla.html"},
            "centro": "centro-c06-apos-fixar-a-ampla.html",
        },
        "M-01, M-07, D-5",
        "Jornada A, C06 · logo depois de fixar a ampla: a lista que falta, a consequência e a volta",
    ),
    (
        "centro-c06-apos-fixar-a-ampla",
        "centro-c06-apos-fixar-a-ampla",
        "centro",
        {
            "ancoras": {
                "Fixar os participantes": "sorteio-c06-apos-fixar-a-ampla.html#recorte-ppp",
                "Obter a semente pública": "sorteio-c06-apos-fixar-a-ampla.html#titulo-ocorrencia",
            },
            "d5": True,
        },
        "M-02, D-5",
        "Jornada A, C06 · o Centro depois de fixar a ampla: a exceção à ordem livre, marcada D-5",
    ),
    (
        "centro-c12",
        "centro-c12",
        "centro",
        {"ancoras": {"Conferir os documentos": "convocacao-c12.html#chamadas"}, "d5": False},
        "M-02, M-11",
        "Jornada E, C12 · a providência de conferir leva às chamadas praticadas, a 1.900 px do topo",
    ),
    (
        "convocacao-c12",
        "convocacao-c12",
        "convocacao",
        {"documentos": {"Cecília": "documentos-c12-apos-conferir.html"}},
        "M-05, M-09",
        "Jornadas D e E, C12 · a convocação com o índice das seções e as vagas ditas pela apuração",
    ),
    (
        "documentos-c12-apos-conferir",
        "documentos-c12-apos-conferir",
        "documentos",
        {
            "desfecho": "convocacao-c12.html#chamada-3",
            "chamadas": "convocacao-c12.html#chamadas",
            "centro": "centro-c12.html",
        },
        "M-01, M-07, M-08",
        "Jornada E, C12 · depois de conferir: o próximo passo desta pessoa, o da lista e a volta",
    ),
    (
        "convocacao-c15",
        "convocacao-c15",
        "convocacao",
        {"conferencia": "convocar-c15-conferencia.html"},
        "M-04, M-05, M-09",
        "Jornada D, C15 · convocar os titulares passa pela conferência; a ajuda deixa de prometer o que não há",
    ),
    (
        "convocar-c15-conferencia",
        "convocacao-c15",
        "conferencia_da_convocacao",
        {"voltar": "convocacao-c15.html"},
        "M-04",
        "Jornada D, C15 · a conferência nova, com as peças das conferências que a gestão já tem",
    ),
]


def indice():
    linhas = []
    for nome, antes, _, _, melhorias, descricao in PAGINAS:
        linhas.append(
            f"<tr><td>{html.escape(descricao)}</td><td>{melhorias}</td>"
            f'<td><a href="antes/{antes}.html">antes</a></td>'
            f'<td><a href="depois/{nome}.html">depois</a></td></tr>'
        )
    corpo = "\n".join(linhas)
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Protótipo — continuidade operacional</title>
<link rel="stylesheet" href="/static/shared/tokens.css"><link rel="stylesheet" href="/static/interface/gestao/base.css">
<link rel="stylesheet" href="/static/interface/gestao/tabelas.css"><link rel="stylesheet" href="/static/prototipo/continuidade.css">
</head><body><main id="conteudo" class="indice-do-prototipo">
<h1>Protótipo — continuidade operacional do GPS</h1>
<p class="prototipo-faixa">Estudo de 10/11/2026. O "antes" é o HTML real das telas, salvo do banco descartável do
estudo; o "depois" é o mesmo HTML com só a melhoria aplicada. Os contornos tracejados marcam o que
depende da D-5 e não se adota sem ela. Nada aqui grava no GPS.</p>
<p>Percurso navegável: comece pelo <a href="depois/centro-c06-inicial.html">Centro do C06</a> (sorteio) ou pelo
<a href="depois/centro-c12.html">Centro do C12</a> (conferência documental), e siga as providências.</p>
<table><thead><tr><th>Tela e estado</th><th>Melhorias</th><th>Antes</th><th>Depois</th></tr></thead>
<tbody>
{corpo}
</tbody></table>
</main></body></html>
"""


def main():
    servidor = servir(PORTA)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    comum = (TRANSFORMACOES / "comum.js").read_text()
    destino = SITIO / "depois"
    destino.mkdir(exist_ok=True)
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
            for nome, antes, transformacao, contexto, _, _ in PAGINAS:
                pagina.goto(f"http://127.0.0.1:{PORTA}/antes/{antes}.html")
                codigo = (TRANSFORMACOES / f"{transformacao}.js").read_text()
                ctx = {"antes": f"{antes}.html", **contexto}
                pagina.evaluate(f"(ctx) => {{\n{comum}\n{codigo}\n}}", ctx)
                saida = "<!DOCTYPE html>\n" + pagina.evaluate("document.documentElement.outerHTML")
                (destino / f"{nome}.html").write_text(saida)
                print(f"montado depois/{nome}.html ← antes/{antes}.html + {transformacao}.js")
            navegador.close()
    finally:
        servidor.shutdown()
    (SITIO / "index.html").write_text(indice())
    (AQUI / "paginas.json").write_text(
        json.dumps(
            [{"depois": n, "antes": a, "melhorias": m} for n, a, _, _, m, _ in PAGINAS], indent=1
        )
    )


if __name__ == "__main__":
    main()
