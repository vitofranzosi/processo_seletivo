"""Maquetes v3 do estudo de orientação da jornada: a generalidade (06/11/2026, segunda revisão).

A v2 tinha colunas fixas do sorteio (Relação, Semente, Sorteio…) e não via as Etapas de avaliação.
Aqui a mesma estrutura serve às duas famílias que o GPS implementa:

- **as colunas vêm da configuração do Perfil**, na ordem de `classificacao/domain/jornada.jornada()`
  (094): as Etapas, que valem para o Perfil inteiro, e os atos do marco, que valem por lista;
- **o marco por sorteio** abre a ordem em relação, semente e sorteio; **o marco por pontuação** a tem
  depois das Etapas que enumera; uma **Etapa decisória fora de marco** aparece onde o Edital a pôs;
- **o nível 1 é o mesmo componente** para todos: providências, com as da pessoa primeiro.

Os números vêm do banco `ps_jornada` em 06/11/2026: as telas de distribuição de cada Etapa (`gestor-91`,
`gestor-35etapas`, `gestor-51etapas`), a condução e o sorteio. O componente é simulado.

Rodar, do `backend/`, com o servidor da `capturar.py` no ar:

    uv run python ../doc/estudo-orientacao-da-jornada-2026-11-06/roteiro/maquetes_v3.py
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
E91 = "/gestao/editais/3693043f-0281-43ba-8145-959fb93321a0/"
E51 = "/gestao/editais/e65d328e-0886-495d-a397-a6964b5196ea/"


def item(quem, texto, onde, *, sua=False, aguarda=False, link=True):
    classe = "sua" if sua else ("aguarda" if aguarda else "")
    corpo = f'<a href="#">{texto}</a>' if link else texto
    return (
        f'<li class="{classe}"><span class="quem">{quem}</span>'
        f'<div>{corpo}<span class="onde">{onde}</span></div></li>'
    )


def nivel1(contagem, itens, mais=0):
    resto = f'<p class="ajuda"><a href="#">Mais {mais}</a></p>' if mais else ""
    return (
        f'<div class="providencias proposto"><p class="contagem">{contagem}</p>'
        f'<ul class="lista-providencias">{"".join(itens)}</ul>{resto}</div>'
    )


def tabela(grupos, colunas, linhas):
    """`grupos`: [(rótulo, classe, quantas colunas)]; `colunas`: [(nome, forma)]; `linhas`: html."""
    g = "".join(f'<th scope="colgroup" colspan="{n}" class="{c}">{r}</th>' for r, c, n in grupos)
    h = "".join(
        f'<th scope="col">{nome}{f"<span class=forma>{forma}</span>" if forma else ""}</th>'
        for nome, forma in colunas
    )
    return (
        '<div class="rolavel-no-estreito" tabindex="0" role="region" aria-label="Andamento do Perfil">'
        f'<table class="jornada"><thead><tr class="grupos"><th></th>{g}</tr>'
        f'<tr><th scope="col">Lista</th>{h}</tr></thead><tbody>{linhas}</tbody></table></div>'
    )


def celula(m, texto, *, etapa=False, rowspan=1):
    classe = ' class="etapa"' if etapa else ""
    rs = f' rowspan="{rowspan}"' if rowspan > 1 else ""
    return f'<td data-m="{m}"{classe}{rs}>{texto}</td>'


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
        '<h2 id="andamento-titulo">Andamento da seleção</h2>'
        f'<p class="linha-inscricoes">{inscricoes}</p>{"".join(blocos)}</section>'
    )


D = "depois"

# --- 91: marco por pontuação, duas Etapas pontuadas enumeradas, uma decisória fora do marco --------
ETAPAS_91 = [
    ("Prova de Títulos", "pontuada · no marco"),
    ("Desempenho Didático", "pontuada · no marco"),
    ("Entrevista (autodeclaração)", "decisória · nenhum ato depende dela"),
]
MARCO_91 = [("Ordem", ""), ("Corte", ""), ("Apuração", ""), ("Resultado", ""), ("Convocação", "")]
LISTAS_91 = ["Ampla concorrência", "PCD", "PPIQ", "PTT"]


def linhas_91():
    linhas = []
    for i, lista in enumerate(LISTAS_91):
        etapas = ""
        if i == 0:
            n = len(LISTAS_91)
            etapas = (
                celula("falta", '● 0 de 8 avaliadas<span class="detalhe">1 avaliador alocado</span>', etapa=True, rowspan=n)
                + celula("falta", '● sem avaliador<span class="detalhe">8 inscrições</span>', etapa=True, rowspan=n)
                + celula("aguarda", '◷ sem avaliador<span class="detalhe">8 inscrições · sem efeito no GPS</span>', etapa=True, rowspan=n)
            )
        apuracao = celula(D, "—") if i == 0 else celula("na", "não se aplica<span class=\"detalhe\">sem vaga no quadro</span>")
        linhas.append(
            f'<tr><th scope="row">{lista}</th>{etapas}'
            + celula(D, "depois das Etapas")
            + celula(D, "—")
            + apuracao
            + celula(D, "—")
            + celula(D, "—")
            + "</tr>"
        )
    return "".join(linhas)


TABELA_91 = tabela(
    [("Etapas · valem para o Perfil", "g-etapas", 3), ("Marco “Classificação final” · por pontuação, por lista", "g-marco", 5)],
    ETAPAS_91 + MARCO_91,
    linhas_91(),
)

# --- 35: marco por sorteio sem Etapa; duas Etapas decisórias fora do marco ------------------------
LISTAS_35 = [
    ("Ampla concorrência", "✓ 11", "✓ 2 faixas", '● 1 sem comunicação<span class="detalhe">5 chamadas · 4 com desfecho</span>', "falta"),
    ("PcD", "✓ 2", "✓ 2 faixas", '✓<span class="detalhe">1 chamada · aceite</span>', "feito"),
    ("PPI", "✓ 3", "✓ 1 faixa", '✓<span class="detalhe">1 chamada · aceite</span>', "feito"),
]


def linhas_35():
    linhas = []
    for i, (lista, relacao, corte, convocacao, m_conv) in enumerate(LISTAS_35):
        semente = celula("feito", '✓ 6115<span class="detalhe">observada 05/11</span>', rowspan=3) if i == 0 else ""
        etapas = ""
        if i == 0:
            etapas = (
                celula("aguarda", '◷ sem avaliador<span class="detalhe">11 · sem efeito no GPS</span>', etapa=True, rowspan=3)
                + celula("aguarda", '◷ sem avaliador<span class="detalhe">11 · sem efeito no GPS</span>', etapa=True, rowspan=3)
            )
        linhas.append(
            f'<tr><th scope="row">{lista}</th>'
            + celula("feito", relacao)
            + semente
            + celula("feito", "✓")
            + celula("feito", corte)
            + celula("feito", "✓")
            + celula("feito", "✓ preliminar")
            + celula(m_conv, convocacao)
            + etapas
            + "</tr>"
        )
    return "".join(linhas)


TABELA_35 = tabela(
    [
        ("Marco “Classificação final” · por sorteio, por lista", "g-marco", 7),
        ("Etapas que nenhum ato consome", "g-etapas", 2),
    ],
    [("Relação", ""), ("Semente", ""), ("Sorteio", "dá a ordem"), ("Corte", ""), ("Apuração", ""),
     ("Resultado", ""), ("Convocação", ""), ("Análise da documentação", "decisória"),
     ("Autodeclaração (PPI)", "decisória")],
    linhas_35(),
)

# --- 51: marco por pontuação cujo corte alimenta uma Etapa decisória (Análise documental) ---------
TABELA_51 = tabela(
    [
        ("Etapas · valem para o Perfil", "g-etapas", 2),
        ("Marco “Classificação final” · por pontuação, por lista", "g-marco", 2),
        ("Etapa governada pela faixa", "g-etapas", 1),
        ("Depois da faixa", "g-depois", 3),
    ],
    [("Prova objetiva", "pontuada"), ("Análise de títulos", "pontuada"), ("Ordem", ""), ("Corte", "faixa"),
     ("Análise documental", "decisória · só a faixa"), ("Apuração", ""), ("Resultado", ""), ("Convocação", "")],
    (
        '<tr><th scope="row">Ampla concorrência</th>'
        + celula("feito", "✓ consolidada", etapa=True, rowspan=2)
        + celula("feito", "✓ consolidada", etapa=True, rowspan=2)
        + celula("feito", "✓") + celula("feito", "✓")
        + celula("feito", '✓ 3 de 3<span class="detalhe">consolidadas</span>', etapa=True, rowspan=2)
        + celula("feito", "✓") + celula("feito", "✓")
        + celula("falta", '● 1 sem comunicação<span class="detalhe">prazo não iniciado</span>')
        + "</tr>"
        + '<tr><th scope="row">PPP</th>'
        + celula("falta", "● falta a ordem") + celula(D, "depois da ordem")
        + celula(D, "—") + celula(D, "—") + celula(D, "—")
        + "</tr>"
    ),
)

CENARIOS = [
    {
        "nome": "G1-91-presidencia-por-pontuacao",
        "papel": "@presidente.b",
        "url": E91,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · as 2 são suas",
            [
                item("Sua", "Avaliar 12 inscrições", "Avaliação · Prova de Títulos · 0 de 12 concluídas", sua=True),
                item("Sua", "Distribuir 12 inscrições", "Distribuição · Prova de Desempenho Didático · sem nenhum avaliador", sua=True),
                item("Atenção", "Entrevista para verificação da autodeclaração: 12 sem avaliador",
                     "Declarada no Edital, mas nenhum ato do GPS depende dela (decisão D9)", aguarda=True, link=False),
            ],
        ),
        "nivel2": nivel2(
            "<strong>Inscrições encerradas</strong> em 03/11/2026 · 12 enviadas",
            [
                ("Produção de Texto e Pesquisa em Computação (1º Perfil · 8 inscrições)",
                 "por pontuação · a classificação vem depois da Prova de Títulos e do Desempenho Didático", TABELA_91),
                ("Produção de Texto e Pesquisa em Computação (2º Perfil · 4 inscrições)",
                 "por pontuação · a classificação vem depois das duas Etapas", ""),
                ("Produção de Texto e Pesquisa em Computação (3º Perfil)",
                 "Não se aplica: nenhuma inscrição", ""),
            ],
            aberto=0,
        ),
    },
    {
        "nome": "G2-35-quem-conduz-com-as-etapas",
        "papel": "gestor",
        "url": E35,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · 1 é sua",
            [
                item("Sua", "Emitir a comunicação de INS-2026-FICTC010",
                     "Convocação · Cefor · Ampla concorrência · o prazo só começa com o envio", sua=True),

                item("Quem publica resultado", "Publicar o resultado definitivo",
                     "Divulgação · Cefor · 3 listas com resultado preliminar desde 05/11", link=False),
                item("Atenção", "2 Etapas declaradas, com 11 inscrições sem avaliador",
                     "Análise da documentação e verificação da autodeclaração: nenhum ato do GPS depende "
                     "delas, e o resultado não chega ao candidato (decisão D9; achado G-07)", aguarda=True, link=False),
            ],
        ),
        "nivel2": nivel2(
            "<strong>Inscrições encerradas</strong> em 28/10/2026 às 12h28 · 11 enviadas · "
            '1 rascunho não enviado, que não conta · <a href="#">Ver inscrições</a>',
            [
                ("Oferta de Vagas Pós-graduação em Educação Especial Inclusiva",
                 "por sorteio · resultado preliminar · convocação: 1 pendente · 2 Etapas declaradas sem efeito no GPS",
                 TABELA_35),
                ("… · Polo Vitória", "Não se aplica: nenhuma inscrição nas 3 listas", ""),
            ],
            aberto=0,
        ),
    },
    {
        "nome": "G3-51-pontuacao-com-etapa-governada",
        "papel": "gestor",
        "url": E51,
        "nivel1": nivel1(
            "<strong>2 providências em aberto</strong> · as 2 são suas",
            [
                item("Sua", "Emitir a comunicação da convocação",
                     "Convocação · Professor de Informática · Ampla concorrência · o prazo só começa com o envio", sua=True),
                item("Sua", "Emitir a ordem da lista PPP",
                     "Classificação · Professor de Informática · as Etapas do marco estão consolidadas", sua=True),
            ],
        ),
        "nivel2": nivel2(
            "<strong>Inscrições encerradas</strong> em 09/09/2026 · 5 enviadas",
            [
                ("Professor de Informática", "por pontuação · faixa na Análise documental · convocação em curso", TABELA_51),
                ("Técnico de Laboratório", "Não se aplica: nenhuma inscrição", ""),
            ],
            aberto=0,
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


TRANSFORMAR = (Path(__file__).parent / "maquetes_v2.py").read_text().split('TRANSFORMAR = """')[1].split('"""')[0]


with sync_playwright() as p:
    nav = p.chromium.launch()
    paginas, medidas = {}, {}
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
            " s.textContent = 'MAQUETE v3 — componente proposto, dados do banco de demonstração';"
            " document.body.appendChild(s); }"
        )
        pagina.evaluate(TRANSFORMAR, [cenario["nivel1"], cenario["nivel2"]])
        medidas[cenario["nome"]] = {"hoje": antes, "proposta": pagina.evaluate("() => document.documentElement.scrollHeight")}
        pagina.screenshot(path=str(SAIDA / f"{cenario['nome']}.jpg"), type="jpeg", quality=82, full_page=True)
        print(cenario["nome"], medidas[cenario["nome"]])
    (SAIDA / "medidas-v3.json").write_text(json.dumps(medidas, indent=1, ensure_ascii=False))
    nav.close()
