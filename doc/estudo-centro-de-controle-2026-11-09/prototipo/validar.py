"""Tarefas do estudo, conferidas por Playwright na tela atual e na proposta. Inspeção automatizada:
mede onde a resposta está (na primeira dobra, na página sem clique, ou ausente), e **não** é teste
com pessoas.

    cd backend && uv run python ../doc/estudo-centro-de-controle-2026-11-09/prototipo/validar.py
"""

import json
import re

from capturar import BASE, entrar
from playwright.sync_api import sync_playwright

C06 = "fc75a001-bc0a-46d3-83bb-8e8e08c66cae"
C12 = "984bb23b-d6d9-4b6f-9940-305da7537dfb"
C08 = "ec9fa21d-3b7f-4910-9510-ca267d478309"
DOBRA = 900

# (cenário, edital, tarefa, expressão que é a resposta)
TAREFAS = [
    (
        "C06",
        C06,
        "T1 Situação operacional dita em palavras",
        r"Onde estamos|frentes? ao mesmo tempo|fase de",
    ),
    (
        "C06",
        C06,
        "T2 Próxima operação do operador",
        r"Fixar os participantes|[Cc]ongelar a relação",
    ),
    (
        "C06",
        C06,
        "T3 Por que o sorteio ainda não pode",
        r"[Nn]enhuma relação deste marco está congelada|[Ff]alta congelar a relação",
    ),
    ("C06", C06, "T5 O que é congelar a relação", r"não muda mais"),
    (
        "C06",
        C06,
        "T5b A Etapa de títulos não segura o sorteio",
        r"[Pp]aralela ao sorteio|corre em paralelo",
    ),
    (
        "C12",
        C12,
        "T1 Situação operacional dita em palavras",
        r"Onde estamos|frentes? ao mesmo tempo",
    ),
    ("C12", C12, "T4 Onde está a lista PPP", r"PPP"),
    ("C12", C12, "T6 Pendência atribuída ao operador", r"\bSUA\b|\bSua\b"),
    ("C12", C12, "T7 Espera com data (resposta dos convocados)", r"09/12"),
    ("C12", C12, "T8 Histórico de etapa concluída (link do ato feito)", r"ver o ato|✓ Feito"),
    (
        "C08",
        C08,
        "T7 Corte aguarda o prazo de recurso",
        r"(recurso deferido tornaria o corte obsoleto|até 14/11)",
    ),
    (
        "C08",
        C08,
        "T1 Situação operacional dita em palavras",
        r"Onde estamos|frentes? ao mesmo tempo",
    ),
    ("C06", C06, "T10 Por que esta ação vem primeiro", r"Por que esta"),
    ("C12", C12, "T11 Ações independentes, sem ranking", r"não escolhe a ordem entre elas"),
    ("C06", C06, "T12 Fase em curso com marca de ação sua", r"Em curso[\s\S]{0,40}1 sua"),
]


def medir(pagina, url, padrao):
    pagina.goto(BASE + url)
    pagina.set_viewport_size({"width": 1440, "height": DOBRA})
    pagina.evaluate("() => window.scrollTo(0, 0)")
    # Só o texto visível na primeira dobra: elementos cujo topo está acima dela e que renderizam.
    dobra = pagina.evaluate(
        """(limite) => {
          const it = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT);
          let saida = []; let n;
          while ((n = it.nextNode())) {
            const r = document.createRange(); r.selectNodeContents(n);
            const b = r.getBoundingClientRect();
            if (b.height > 0 && b.top < limite && b.bottom > 0 && n.parentElement.checkVisibility()) saida.push(n.textContent);
          }
          return saida.join(' ');
        }""",
        DOBRA,
    )
    # O texto da página sem clique: o de <details> fechado não conta (innerText o omite).
    visivel = pagina.evaluate("() => document.querySelector('main').innerText")
    inteiro = pagina.evaluate("() => document.querySelector('main').textContent")
    if re.search(padrao, dobra):
        return "na primeira dobra"
    if re.search(padrao, visivel):
        altura = pagina.evaluate(
            """(p) => { const re = new RegExp(p);
              const it = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT);
              let n; while ((n = it.nextNode())) { if (re.test(n.textContent)) {
                const r = document.createRange(); r.selectNodeContents(n);
                const b = r.getBoundingClientRect(); if (b.height > 0) return Math.round(b.top + window.scrollY); } }
              return -1; }""",
            padrao,
        )
        return f"rolando, a {altura}px"
    if re.search(padrao, inteiro):
        return "só abrindo um bloco recolhido"
    return "ausente"


def main():
    linhas = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 1440, "height": DOBRA}, locale="pt-BR")
        pagina = entrar(contexto, "treino.presidencia", [])
        for cenario, edital, tarefa, padrao in TAREFAS:
            atual = medir(pagina, f"/gestao/editais/{edital}/", padrao)
            proposta = medir(pagina, f"/gestao/prototipo-centro/editais/{edital}/", padrao)
            linhas.append((cenario, tarefa, atual, proposta))
        alturas = {}
        for nome, url in (
            ("atual C06", f"/gestao/editais/{C06}/"),
            ("proposta C06", f"/gestao/prototipo-centro/editais/{C06}/"),
            ("atual C12", f"/gestao/editais/{C12}/"),
            ("proposta C12", f"/gestao/prototipo-centro/editais/{C12}/"),
        ):
            pagina.goto(BASE + url)
            alturas[nome] = pagina.evaluate(
                "() => [document.documentElement.scrollHeight, document.querySelectorAll('main a').length]"
            )
        # Teclado: a ordem do Tab a partir do topo do conteúdo, nas 12 primeiras paradas.
        pagina.goto(BASE + f"/gestao/prototipo-centro/editais/{C06}/")
        paradas = []
        pagina.keyboard.press("Tab")
        for _ in range(40):
            alvo = pagina.evaluate(
                "() => { const e = document.activeElement; return e && e.closest('main') ? (e.innerText || e.getAttribute('aria-label') || e.tagName).trim().replace(/\\s+/g,' ').slice(0,50) : null }"
            )
            if alvo:
                paradas.append(alvo)
            if len(paradas) >= 14:
                break
            pagina.keyboard.press("Tab")
        navegador.close()
    print("| Cenário | Tarefa | Tela atual | Proposta |")
    print("|---|---|---|---|")
    for cenario, tarefa, atual, proposta in linhas:
        print(f"| {cenario} | {tarefa} | {atual} | {proposta} |")
    print()
    print("Altura da página e links no conteúdo:", json.dumps(alturas, ensure_ascii=False))
    print()
    print("Ordem do Tab no conteúdo (proposta C06):", " → ".join(paradas))


if __name__ == "__main__":
    main()
