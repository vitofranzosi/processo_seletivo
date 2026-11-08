"""Maquetes do estudo de convergência: o trecho proposto, injetado na tela real.

Cada maquete abre a tela verdadeira do Edital 900 num banco de fase (ver o README do estudo), troca
**um** bloco pelo trecho proposto e fotografa. O resto da página é o que o GPS desenha hoje. Os
dados do trecho são os do caso (nomes, notas, datas), conferidos contra `conferir.py` e o banco.

    BASE=http://localhost:8152 SAIDA=../maquetes python maquetes.py A1

A CSP da gestão recusa estilo inline; a maquete usa `bypass_csp` só para desenhar o trecho. A
implementação real iria para a folha da tela, como manda o CLAUDE.md.
"""

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE", "http://localhost:8152")
SAIDA = Path(os.environ.get("SAIDA", "maquetes"))
SAIDA.mkdir(parents=True, exist_ok=True)
E = "/gestao/editais/9e8a1d1a-8b58-4045-ae6b-5480195988a5"
M1 = "3c9e07d8-9253-47be-88ee-76cd5718f647"

ESTILO = """
.mq{border:2px dashed #b45f06;border-radius:6px;padding:4px 10px 10px;position:relative}
.mq-rotulo{position:absolute;top:-11px;right:10px;background:#b45f06;color:#fff;font-size:11px;
  padding:1px 8px;border-radius:9px;font-weight:600;letter-spacing:.03em}
.mq .onde{background:#f1f5f2;border-left:4px solid #1f6f3f;padding:8px 10px;margin:8px 0;font-size:15px}
.mq .prov{list-style:none;padding:0;margin:6px 0}
.mq .prov li{border-left:4px solid #1f6f3f;background:#e8f3ec;padding:7px 10px;margin:6px 0;font-size:15px}
.mq .prov li.espera{border-left-color:#8a8a8a;background:#f3f3f3}
.mq .prov li.nsa{border-left-color:#c9c9c9;background:#fafafa;color:#555}
.mq .sua{background:#1f6f3f;color:#fff;font-size:11px;font-weight:700;padding:1px 6px;border-radius:3px}
.mq .etq{display:inline-block;font-size:11px;font-weight:600;padding:1px 6px;border-radius:3px;
  border:1px solid #888;color:#333;margin-left:4px}
.mq .etq.rec{border-color:#9a6700;color:#7a5200;background:#fff7e0}
.mq .etq.imp{border-color:#a40e26;color:#a40e26;background:#fde8eb}
.mq .cons{display:block;font-size:13px;color:#333;margin-top:3px}
.mq .cons:before{content:"Ao confirmar: ";font-weight:600}
.mq .cons.espera:before{content:"Se fizer agora: "}
.mq table{border-collapse:collapse;width:100%;font-size:13.5px}
.mq th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;text-align:left;color:#555;
  border-bottom:1px solid #ccc;padding:6px}
.mq td{border-bottom:1px solid #e3e3e3;padding:6px;vertical-align:top}
.mq td.n{text-align:right;font-variant-numeric:tabular-nums}
.mq tr.fronteira td{border-bottom:3px solid #1f6f3f}
.mq .porque{font-size:12.5px;color:#333}
.mq .via{font-weight:600}
.mq .fora{color:#777}
.mq .resumo{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.mq .resumo div{border:1px solid #ccc;border-radius:4px;padding:6px 10px;background:#fff;font-size:13px}
.mq .resumo b{display:block;font-size:22px}
.mq .trilho{list-style:none;margin:8px 0;padding:0 0 0 18px;border-left:3px solid #1f6f3f}
.mq .trilho>li{position:relative;margin:0 0 10px;padding:6px 10px;background:#fff;border:1px solid #ddd;border-radius:4px;font-size:14px}
.mq .trilho>li:before{content:"";position:absolute;left:-27px;top:12px;width:12px;height:12px;border-radius:50%;background:#1f6f3f}
.mq .trilho>li.marco{background:#eef4fb;border-color:#9bb8d8}
.mq .trilho>li.marco:before{background:#1c4f86;border-radius:2px;transform:rotate(45deg)}
.mq .liga{display:block;font-size:12.5px;color:#1f6f3f;font-weight:600;margin-top:2px}
.mq .alerta{border-left:4px solid #9a6700;background:#fff7e0;padding:8px 10px;margin:8px 0;font-size:14px}
.mq .alerta.info{border-left-color:#1c4f86;background:#eef4fb}
"""

A1 = """
<h2 id="acoes-titulo">O que fazer agora</h2>
<div class="mq"><span class="mq-rotulo">PROPOSTA</span>
<p class="onde"><strong>Onde está:</strong> a Classificação final está publicada como definitiva nas 3 listas
(28/12) e as vagas foram apuradas (29/12). Ninguém foi convocado ainda.</p>
<p><strong>3 providências · 3 são suas</strong></p>
<ul class="prov">
<li><span class="sua">SUA</span> <a href="#">Convocar 4 titulares</a> — Ampla concorrência · Helena Prado, João Benedito,
Bruno Taveira e Rafael Quintão
<span class="cons">4 convocações e 4 comunicações num ato só; o prazo de cada uma corre a partir do envio. O ato é imutável.</span></li>
<li><span class="sua">SUA</span> <a href="#">Convocar 1 titular</a> — PCD · Elisa Viana</li>
<li><span class="sua">SUA</span> <a href="#">Convocar 1 titular</a> — PPI · Kátia Moura
<span class="cons">João Benedito é o 1º da PPI, mas ocupa pela ampla; por isso a vaga PPI vai a Kátia.</span></li>
</ul>
<ul class="prov"><li class="nsa"><strong>Classificação para a entrevista</strong> — não apura vagas nem convoca: ela decidiu quem
foi à Entrevista (12 pessoas). As vagas são da Classificação final.</li></ul>
</div>
"""

A2 = """
<h2 id="acoes-titulo">O que fazer agora</h2>
<div class="mq"><span class="mq-rotulo">PROPOSTA</span>
<p class="onde"><strong>Onde está:</strong> convocação em curso. Ampla: 3 de 4 vagas ocupadas — Bruno Taveira desistiu hoje
(05/01). PCD e PPI: titulares convocados, prazo até 08/01.</p>
<p><strong>4 providências · 2 são suas</strong></p>
<ul class="prov">
<li><span class="sua">SUA</span> <a href="#">Chamar a próxima da fila</a> — Ampla · <strong>Diana Ferraz</strong>, para a vaga que vagou
<span class="cons">convocação individual, imutável, com comunicação no mesmo ato. Caio Bettencourt passa a ser o próximo.</span></li>
<li><span class="sua">SUA</span> <a href="#">Conferir os documentos</a> — PPI · Kátia Moura enviou a Identidade</li>
<li class="espera">◷ <strong>Aguarda</strong> Rafael Quintão reenviar a Identidade (pendente: ilegível) — Ampla · até 08/01</li>
<li class="espera">◷ <strong>Aguarda</strong> Elisa Viana responder — PCD · até 08/01</li>
</ul>
</div>
"""

A3 = """
<h2 id="acoes-titulo">O que fazer agora</h2>
<div class="mq"><span class="mq-rotulo">PROPOSTA</span>
<p class="onde"><strong>Onde está:</strong> Classificação para a entrevista emitida e publicada como preliminar nas 3 listas (09/12).
O prazo de recurso corre até <strong>12/12, 23h59</strong>.</p>
<p><strong>2 providências · nenhuma pede ato agora</strong></p>
<ul class="prov">
<li class="espera">◷ <strong>Aguarda o prazo</strong> <a href="#">Emitir o corte</a> — Ampla, PCD e PPI
<span class="etq rec">recomendação</span>
<span class="cons espera">o GPS aceita, mas o corte decide quem vai à Entrevista. Um recurso deferido até 12/12 o torna obsoleto, e a sucessão exige motivo e fica na trilha.</span></li>
<li class="espera">◷ <strong>Aguarda o prazo</strong> Publicar o resultado definitivo — Ampla, PCD e PPI
<span class="etq imp">impedido até 12/12</span></li>
</ul>
</div>
"""

LINHAS_M1 = [
    # pos, nome, mod, cur, pro, comb, porque, via
    (1, "Helena Prado", "AC", 90, 92, "91,50", "", "Ampla"),
    (2, "João Benedito", "PPI", 85, 88, "87,25", "", "Ampla · também na faixa PPI"),
    (3, "Bruno Taveira", "AC", 80, 85, "83,75", "", "Ampla"),
    (4, "Sofia Arruda", "AC", 66, 80, "76,50", "empatou com Rafael em 76,50; <b>separou: maior nota na Prova</b> (80 × 76)", "Ampla"),
    (5, "Rafael Quintão", "AC", 78, 76, "76,50", "perdeu para Sofia no 1º critério (Prova 76 × 80)", "Ampla"),
    (6, "Caio Bettencourt", "AC", 72, 74, "73,50", "empatou com Diana em 73,50 e na Prova (74); <b>separou: nascimento mais antigo</b> (05/06/1980 × 01/12/1992)", "Ampla"),
    (7, "Diana Ferraz", "AC", 72, 74, "73,50", "perdeu para Caio no 2º critério (nascimento)", "Ampla"),
    (8, "Gustavo Lemos", "AC", 60, "76 <small>(era 68; recurso)</small>", "72,00", "subiu de 11º para 8º com a correção do recurso", "Ampla · última da faixa"),
    (9, "Elisa Viana", "PCD", 64, 72, "70,00", "", "<span class='via'>pela PCD</span> (1ª)"),
    (10, "Patrícia Nogueira", "AC", 68, 70, "69,50", "", "<span class='fora'>não vai: fora das três faixas</span>"),
    (11, "Kátia Moura", "PPI", 62, 70, "68,00", "", "<span class='via'>pela PPI</span> (2ª)"),
    (12, "Iara Batista", "PCD", 58, 66, "64,00", "", "<span class='via'>pela PCD</span> (2ª)"),
    (13, "Luan Tavares", "PPI", 55, 64, "61,75", "", "<span class='via'>pela PPI</span> (3º)"),
    (14, "Renato Sales", "AC", 50, 62, "59,00", "", "<span class='fora'>não vai: fora das três faixas</span>"),
]


def tabela_m1():
    linhas = []
    for pos, nome, mod, cur, pro, comb, porque, via in LINHAS_M1:
        classe = " class='fronteira'" if pos == 8 else ""
        linhas.append(
            f"<tr{classe}><td>{pos}º</td><td>{nome} <span class='etq'>{mod}</span></td>"
            f"<td class='n'>{cur}</td><td class='n'>{pro}</td><td class='n'><b>{comb}</b></td>"
            f"<td class='porque'>{porque}</td><td>{via}</td></tr>"
        )
    sem = [
        ("Lívia Montes", "Prova 55 &lt; mínima 60 — eliminada"),
        ("Fábio Guerra", "Prova 52 &lt; mínima 60 — eliminado"),
        ("Otávio Rangel", "ausente na Prova — eliminado"),
    ]
    for nome, motivo in sem:
        linhas.append(f"<tr><td>—</td><td>{nome}</td><td colspan='4' class='porque'>{motivo}</td><td class='fora'>não vai</td></tr>")
    return "".join(linhas)


B = (
    """
<div class="mq"><span class="mq-rotulo">PROPOSTA</span>
<h2>Quem vai à Entrevista</h2>
<div class="resumo"><div><b>12</b>vão à Entrevista</div><div><b>8</b>pela faixa da ampla</div>
<div><b>2</b>só pela PCD</div><div><b>2</b>só pela PPI</div><div><b>2</b>não alcançados</div><div><b>3</b>eliminados antes</div></div>
<p class="porque">O corte deste marco é <b>8 de cada lista</b>. João Benedito está na faixa da ampla e na da PPI, e conta uma vez.
Abaixo, a ordem da ampla — que inclui todos — com a lista pela qual cada pessoa chega à Entrevista.</p>
<table><thead><tr><th>Pos.</th><th>Participante</th><th>Currículo ×1</th><th>Prova ×3</th><th>Combinada</th>
<th>Por que nesta posição</th><th>Vai à Entrevista</th></tr></thead><tbody>"""
    + tabela_m1()
    + """</tbody></table>
<p class="porque">Combinada = (Currículo + 3 × Prova) ÷ 4, 2 casas, meio para cima. Linha verde: a última posição da faixa da ampla.</p>
</div>
"""
)

C = """
<div class="mq"><span class="mq-rotulo">PROPOSTA</span>
<h2>Como o Edital será executado</h2>
<p class="porque">Lido do conteúdo que você configurou. Nada aqui é configuração nova: é a mesma informação, na ordem em que o GPS a aplica.</p>
<ol class="trilho">
<li><strong>1 · Análise dos requisitos</strong> — decisória, eliminatória
<span class="liga">Indeferido sai de tudo o que vem depois</span></li>
<li><strong>2 · Análise do currículo</strong> — nota 0–100, peso 1, só classificatória
<span class="liga">Todos seguem; a nota só soma</span></li>
<li><strong>3 · Prova escrita</strong> — nota 0–100, mínima 60, peso 3, eliminatória
<span class="liga">Abaixo de 60 ou ausente: sai</span></li>
<li class="marco"><strong>◆ Classificação para a entrevista</strong> — lê Currículo e Prova: (CUR + 3·PRO) ÷ 4.
Desempate: Prova › nascimento mais antigo.
<span class="liga">Corte: os 8 primeiros de <u>cada</u> lista (ampla, PCD, PPI) → decide quem faz a Entrevista. Não apura vagas.</span></li>
<li><strong>4 · Entrevista</strong> — só quem está numa das faixas acima; nota 0–100, mínima 60, peso 2, eliminatória
<span class="liga">Abaixo de 60 ou ausente: sai</span></li>
<li class="marco"><strong>◆ Classificação final</strong> — lê Currículo, Prova e Entrevista: (CUR + 3·PRO + 2·ENT) ÷ 6.
Desempate: Entrevista › Prova › nascimento.
<span class="liga">Corte: as vagas de cada lista (4 · 1 · 1) + 2 suplentes → ocupação e convocação</span></li>
</ol>
<div class="alerta"><strong>Confira:</strong> com corte fixo por lista, até <b>24</b> pessoas podem ir à Entrevista (8 + 8 + 8).
A prévia com a população fictícia leva <b>14</b>. Se a intenção era 8 no total, o GPS não tem essa espécie hoje (decisão G1 do estudo de 07/11).</div>
<div class="alerta info"><strong>O peso vale em todos os marcos:</strong> a Prova pesa 3 na Classificação para a entrevista e na final.</div>
</div>
"""

MAQUETES = {
    # nome: (url, seletor do bloco a trocar, html, captura do bloco ou janela)
    "A1": (f"{E}/", "section[aria-labelledby=acoes-titulo]", A1),
    "A2": (f"{E}/", "section[aria-labelledby=acoes-titulo]", A2),
    "A3": (f"{E}/", "section[aria-labelledby=acoes-titulo]", A3),
    "B": (f"{E}/marcos/{M1}/corte", "table", B),
    "C": (f"{E}/compor/revisao", "section[aria-labelledby=conferencia-titulo]", C),
}

so = sys.argv[1:] or list(MAQUETES)
with sync_playwright() as p:
    navegador = p.chromium.launch()
    contexto = navegador.new_context(
        viewport={"width": 1280, "height": 900}, locale="pt-BR", bypass_csp=True
    )
    pagina = contexto.new_page()
    for nome in so:
        url, seletor, html = MAQUETES[nome]
        pagina.context.clear_cookies()
        pagina.goto(f"{BASE}/gestao/identificar/demonstracao")
        with pagina.expect_navigation():
            pagina.click('button[name=identidade_sugerida][value="demo.presidente"]')
        pagina.goto(BASE + url)
        pagina.wait_for_load_state("networkidle")
        pagina.add_style_tag(content=ESTILO)
        ok = pagina.evaluate(
            """([sel, html]) => { const el = document.querySelector(sel); if (!el) return false;
                 if (el.tagName === 'TABLE') { const d = document.createElement('div'); d.innerHTML = html;
                   (el.closest('.tabela-rolavel') || el).replaceWith(d); d.scrollIntoView(); return true; }
                 el.innerHTML = html; el.scrollIntoView(); return true; }""",
            [seletor, html],
        )
        if not ok:
            print("sem bloco", nome, seletor)
            continue
        pagina.wait_for_timeout(300)
        destino = SAIDA / f"{nome}.jpg"
        if nome.startswith("A"):
            pagina.locator("main").first.screenshot(path=destino, type="jpeg", quality=80)
        elif nome == "C":
            # A Revisão é longa; o bloco proposto basta, com o título da página acima dele.
            pagina.locator(".mq").first.screenshot(path=destino, type="jpeg", quality=80)
        else:
            pagina.screenshot(path=destino, type="jpeg", quality=80, full_page=True)
        print("ok", nome)
    navegador.close()
