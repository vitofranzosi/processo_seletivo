"""Maquetes v2 do estudo de orientação da jornada, depois da revisão de 06/11/2026.

O que muda da v1 (`maquetes.py`):

- **Dois níveis.** O nível 1 mora dentro de "O que fazer agora": as providências em aberto, as da
  pessoa primeiro. O nível 2 substitui o cartão "Classificação", no mesmo lugar e no mesmo tamanho:
  uma linha por Perfil, recolhida, e a matriz por lista só quando a pessoa a abre.
- **Por papel.** O mesmo Edital 35 visto por quem conduz, por quem publica e por quem elabora; e o 91
  pela presidência da comissão.
- **Nada acrescentado sem tirar algo.** A trilha de situação sai depois da publicação (D1), e o aviso de
  conteúdo imutável cai para uma linha.

Os dados são os do banco `ps_jornada` em 06/11/2026; o componente é simulado. A situação de cada item
segue o `contrato-de-derivacao.md`.

Rodar, do `backend/`, com o servidor de `capturar.py` no ar:

    uv run python ../doc/estudo-orientacao-da-jornada-2026-11-06/roteiro/maquetes_v2.py
"""

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UX_BASE", "http://localhost:8140")
AQUI = Path(__file__).resolve().parent.parent
SAIDA = AQUI / "maquetes"
CSS = (SAIDA / "proposta.css").read_text()

E35 = "/gestao/editais/c6ea917b-e8da-42d9-a32c-38afcd8da1f3/"
E57 = "/gestao/editais/d3fa2087-7927-4f51-bdee-982caeb38285/"
E91 = "/gestao/editais/3693043f-0281-43ba-8145-959fb93321a0/"


def item(quem, texto, onde, *, sua=False, aguarda=False, link=True):
    classe = "sua" if sua else ("aguarda" if aguarda else "")
    corpo = f'<a href="#">{texto}</a>' if link else texto
    return f'<li class="{classe}"><span class="quem">{quem}</span><div>{corpo}<span class="onde">{onde}</span></div></li>'


def nivel1(contagem, itens):
    return (
        f'<div class="providencias proposto"><p class="contagem">{contagem}</p>'
        f'<ul class="lista-providencias">{"".join(itens)}</ul></div>'
    )


# --- O nível 2 do 35: uma linha por Perfil; a matriz do Cefor, por lista -------------------------
CABECALHO = (
    '<thead><tr><th scope="col">Lista</th><th scope="col">Relação</th><th scope="col">Semente</th>'
    '<th scope="col">Sorteio</th><th scope="col">Corte</th><th scope="col">Apuração</th>'
    '<th scope="col">Resultado</th><th scope="col">Convocação</th></tr></thead>'
)


def linha(nome, celulas):
    tds = "".join(f'<td data-m="{m}">{t}</td>' for m, t in celulas)
    return f'<tr><th scope="row">{nome}</th>{tds}</tr>'


F = "feito"
MATRIZ_35_CEFOR = (
    '<div class="rolavel-no-estreito" tabindex="0" role="region" aria-label="Listas do Perfil"><table>'
    + CABECALHO
    + "<tbody>"
    + linha("Ampla concorrência", [(F, "✓ 11"), (F, "✓ 6115"), (F, "✓"), (F, "✓ 2 faixas"), (F, "✓"),
             (F, "✓ preliminar"), ("falta", '● 1 sem comunicação<span class="detalhe">5 chamadas · 4 com desfecho</span>')])
    + linha("PcD", [(F, "✓ 2"), (F, "✓ 6115"), (F, "✓"), (F, "✓ 2 faixas"), (F, "✓"), (F, "✓ preliminar"),
             (F, '✓<span class="detalhe">1 chamada · aceite</span>')])
    + linha("PPI", [(F, "✓ 3"), (F, "✓ 6115"), (F, "✓"), (F, "✓ 1 faixa"), (F, "✓"), (F, "✓ preliminar"),
             (F, '✓<span class="detalhe">1 chamada · aceite</span>')])
    + "</tbody></table></div>"
)


def nivel2(inscricoes, perfis, *, aberto=None):
    blocos = []
    for indice, (nome, resumo, miolo) in enumerate(perfis):
        abre = " open" if aberto == indice else ""
        blocos.append(
            f'<details class="perfil"{abre}><summary><span class="nome">{nome}</span>'
            f'<span class="resumo">{resumo}</span></summary>{miolo}</details>'
        )
    return (
        '<section class="cartao andamento proposto" aria-labelledby="andamento-titulo">'
        '<h2 id="andamento-titulo">Andamento por Perfil</h2>'
        f'<p class="linha-inscricoes">{inscricoes}</p>{"".join(blocos)}</section>'
    )


INSCRICOES_35 = (
    "<strong>Inscrições encerradas</strong> em 28/10/2026 às 12h28 · 11 enviadas · "
    '1 rascunho não enviado, que não conta · <a href="#">Ver inscrições</a>'
)
PERFIS_35 = [
    (
        "Oferta de Vagas Pós-graduação em Educação Especial Inclusiva",
        "3 listas · sorteadas, cortadas e apuradas · resultado preliminar · convocação: 1 pendente",
        MATRIZ_35_CEFOR,
    ),
    (
        "… · Polo Vitória",
        "Não se aplica: nenhuma inscrição nas 3 listas",
        '<p class="ajuda">Nenhuma inscrição enviada escolheu este Perfil. Não há relação a congelar, '
        "sorteio, corte nem convocação.</p>",
    ),
]

COMUNICAR_C10 = (
    "Emitir a comunicação de INS-2026-FICTC010",
    "Convocação · Cefor · Ampla concorrência · o prazo só começa com o envio",
)
DEFINITIVO_CEFOR = (
    "Publicar o resultado definitivo",
    "Divulgação · Cefor · 3 listas com resultado preliminar desde 05/11",
)

CENARIOS = [
    {
        "nome": "N1-35-quem-conduz",
        "papel": "gestor",
        "url": E35,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · 1 é sua",
            [
                item("Sua", *COMUNICAR_C10, sua=True),
                item("Quem publica resultado", *DEFINITIVO_CEFOR, link=False),
            ],
        ),
        "nivel2": nivel2(INSCRICOES_35, PERFIS_35),
    },
    {
        "nome": "N1b-35-quem-conduz-com-o-perfil-aberto",
        "papel": "gestor",
        "url": E35,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · 1 é sua",
            [
                item("Sua", *COMUNICAR_C10, sua=True),
                item("Quem publica resultado", *DEFINITIVO_CEFOR, link=False),
            ],
        ),
        "nivel2": nivel2(INSCRICOES_35, PERFIS_35, aberto=0),
    },
    {
        "nome": "N2-35-quem-publica",
        "papel": "publicador",
        "url": E35,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · 1 é sua",
            [
                item("Sua", *DEFINITIVO_CEFOR, sua=True),
                item("Quem conduz", *COMUNICAR_C10, link=False),
            ],
        ),
        "nivel2": nivel2(INSCRICOES_35, PERFIS_35),
    },
    {
        "nome": "N3-35-quem-elabora",
        "papel": "elaborador",
        "url": E35,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · nenhuma é sua",
            [
                item("Quem conduz", *COMUNICAR_C10, link=False),
                item("Quem publica resultado", *DEFINITIVO_CEFOR, link=False),
            ],
        ),
        # D3 recomendado: o nível 2 só para quem hoje vê o cartão "Classificação". Quem elabora não
        # o via, e continua não vendo; o nível 1 já lhe diz quem faz o quê.
        "nivel2": "",
    },
    {
        "nome": "N4-57-quem-conduz-listas-em-estagios-distintos",
        "papel": "gestor",
        "url": E57,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · as 2 são suas",
            [
                item(
                    "Sua",
                    "Congelar a relação das 3 listas",
                    "Sorteio · Tecnologias Digitais, Campus Vitória · inscrições encerradas em 04/11 · "
                    "congelar não se desfaz",
                    sua=True,
                ),
                item(
                    "Sua",
                    "Observar a extração 6116 da Loteria Federal",
                    "Sorteio · Design Educacional · relações congeladas em 04/11 · o Edital não declara a "
                    "hora; antes da extração, nada é gravado",
                    sua=True,
                ),
            ],
        ),
        "nivel2": nivel2(
            "<strong>Inscrições encerradas</strong> em 04/11/2026 · 12 enviadas · 1 rascunho não "
            'enviado, que não conta · <a href="#">Ver inscrições</a>',
            [
                (
                    "Curso de Aperfeiçoamento em Design Educacional",
                    "3 listas · relações congeladas · semente por observar",
                    '<div class="rolavel-no-estreito" tabindex="0" role="region" aria-label="Listas"><table>'
                    + CABECALHO
                    + "<tbody>"
                    + "".join(
                        linha(nome, [(F, f"✓ {n}"), ("falta", "● 6116"), ("depois", "depois da semente"),
                                     ("depois", "—"), ("depois", "—"), ("depois", "—"), ("depois", "—")])
                        for nome, n in (("Ampla concorrência", 9), ("PcD", 3), ("PPI", 2))
                    )
                    + "</tbody></table></div>",
                ),
                (
                    "Curso de Aperfeiçoamento em Tecnologias Digitais Aplicadas à Educação · Campus Vitória",
                    "3 listas · relação por congelar (3, 1 e 1 inscritos)",
                    "",
                ),
            ],
            aberto=0,
        ),
    },
    {
        "nome": "N5-91-presidencia-da-comissao",
        "papel": "@presidente.b",
        "url": E91,
        "nivel1": nivel1(
            "<strong>1 providência sua</strong>",
            [
                item(
                    "Sua",
                    "Avaliar 12 inscrições",
                    "Avaliação · Prova de Títulos · 0 de 12 concluídas",
                    sua=True,
                ),
            ],
        ),
        "nivel2": nivel2(
            "<strong>Inscrições encerradas</strong> em 03/11/2026 · 12 enviadas",
            [
                (
                    "Os 3 Perfis de Produção de Texto e Pesquisa em Computação",
                    "Classificação depois das avaliações (Etapas por avaliação: D6)",
                    "",
                )
            ],
        ),
    },
]


def entrar(nav, papel):
    contexto = nav.new_context(viewport={"width": 1280, "height": 900}, bypass_csp=True)
    pagina = contexto.new_page()
    pagina.goto(BASE + "/gestao/identificar/demonstracao")
    with pagina.expect_navigation():
        if papel.startswith("@"):
            pagina.locator(f"button[name=identidade_sugerida][value='{papel[1:]}']").first.click()
        else:
            pagina.locator(f"form:has(input[name=papeis][value='{papel}']) button").first.click()
    return pagina


TRANSFORMAR = """([nivel1, nivel2]) => {
  // D1: a trilha de situação sai depois da publicação; o selo ao lado do título continua.
  document.querySelector('ol.etapas')?.remove();
  const acoes = document.querySelector('section[aria-labelledby=acoes-titulo]');
  const titulo = acoes.querySelector('h2');
  // O aviso de conteúdo imutável cai para uma linha, no pé do cartão.
  const imutavel = acoes.querySelector('.imutavel');
  imutavel?.remove();
  // Some a frase genérica "nenhum ato" quando o nível 1 diz o que há.
  acoes.querySelectorAll('li.nenhuma').forEach(e => e.closest('ul')?.remove());
  titulo.insertAdjacentHTML('afterend', nivel1);
  // A ação que hoje é cheia ("Inscrições recebidas") deixa de competir com a providência.
  acoes.querySelectorAll('ul.lista-acoes:not(.terminais) .botao').forEach(b => b.classList.add('secundario'));
  const terminais = acoes.querySelector('ul.terminais');
  const linha = '<p class="publicado-curto proposto">Publicado: o conteúdo só muda por Retificação.</p>';
  if (terminais) terminais.insertAdjacentHTML('beforebegin', linha); else acoes.insertAdjacentHTML('beforeend', linha);
  // O nível 2 ocupa o lugar do cartão "Classificação", logo depois das duas colunas.
  document.querySelector('section[aria-labelledby=classificacao-titulo]')?.remove();
  document.querySelector('.colunas.ao-topo').insertAdjacentHTML('afterend', nivel2);
}"""

MEDIR = """() => ({
  altura: document.documentElement.scrollHeight,
  ate_o_nivel1: Math.round(document.querySelector('.providencias').getBoundingClientRect().bottom + scrollY),
})"""


with sync_playwright() as p:
    nav = p.chromium.launch()
    medidas = {}
    paginas = {}
    for cenario in CENARIOS:
        papel = cenario["papel"]
        if papel not in paginas:
            paginas[papel] = entrar(nav, papel)
        pagina = paginas[papel]
        pagina.goto(BASE + cenario["url"])
        antes = pagina.evaluate("() => document.documentElement.scrollHeight")
        pagina.add_style_tag(content=CSS)
        pagina.evaluate(
            "() => { const s = document.createElement('div'); s.className = 'selo-maquete';"
            " s.textContent = 'MAQUETE v2 — componente proposto, dados do banco de demonstração';"
            " document.body.appendChild(s); }"
        )
        pagina.evaluate(TRANSFORMAR, [cenario["nivel1"], cenario["nivel2"]])
        medida = pagina.evaluate(MEDIR)
        medidas[cenario["nome"]] = {"hoje": antes, "proposta": medida["altura"], "fim_do_nivel1": medida["ate_o_nivel1"]}
        pagina.screenshot(path=str(SAIDA / f"{cenario['nome']}.jpg"), type="jpeg", quality=82, full_page=True)
        print(cenario["nome"], medidas[cenario["nome"]])
    (SAIDA / "medidas-v2.json").write_text(json.dumps(medidas, indent=1, ensure_ascii=False))
    nav.close()
