"""Maquetes do estudo de orientação da jornada (06/11/2026). Não é teste nem código do produto.

Cada maquete abre a **tela real** do GPS como o papel indicado, com as folhas reais da gestão, e troca
só o trecho proposto (marcado com contorno tracejado e o selo "MAQUETE"). Os números são os do banco de
demonstração `ps_jornada` em 06/11/2026, lidos nas telas e no banco; o componente é simulado.

A CSP da gestão recusa estilo injetado; o contexto do navegador a ignora (`bypass_csp`) só aqui.

Rodar, do `backend/`, com o servidor da `capturar.py` no ar:

    uv run python ../doc/estudo-orientacao-da-jornada-2026-11-06/roteiro/maquetes.py
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UX_BASE", "http://localhost:8140")
AQUI = Path(__file__).resolve().parent.parent
SAIDA = AQUI / "maquetes"
CSS = (SAIDA / "proposta.css").read_text()

E35 = "/gestao/editais/c6ea917b-e8da-42d9-a32c-38afcd8da1f3/"
E57 = "/gestao/editais/d3fa2087-7927-4f51-bdee-982caeb38285/"
M57 = "marcos/68f0c761-6a44-4ee5-92d0-c78afaefa130/"
M35V = "marcos/3000f443-9943-4b18-9a9c-7d01e419487b/"
CORTE_26 = "/gestao/editais/1bddd8ac-d54b-483a-b449-732802161b13/marcos/00000000-0000-0000-0026-0000000000a1/corte"

PUBLICADO_CURTO = (
    "<strong>Publicado.</strong> O conteúdo só muda por Retificação, que pede a permissão de retificar."
)

# ---------------------------------------------------------------------------------------------
# M1 — Edital 35, quem conduz (gestor.a): visão geral de um Edital em andamento
# ---------------------------------------------------------------------------------------------
M1_BASTAO = """<p class="bastao proposto"><strong>Uma convocação aguarda você:</strong>
<a href="#">emitir a comunicação de INS-2026-FICTC010</a> (Ampla concorrência, Cefor).
<span class="ajuda">O prazo dela só começa a correr depois do envio.</span></p>"""

M1_ANDAMENTO = """<section class="cartao andamento proposto" aria-labelledby="andamento-titulo">
<h2 id="andamento-titulo">Andamento da seleção</h2>
<p class="ajuda">Lido dos atos já praticados, em 06/11/2026 às 11h12. Cada Perfil e cada lista anda no
seu ritmo: o Edital não tem uma etapa única.</p>
<p class="linha-inscricoes"><strong>Inscrições encerradas</strong> em 28/10/2026 às 12h28 · 11 enviadas ·
1 rascunho não enviado, que não conta. <a href="#">Ver inscrições</a></p>
<div class="rolavel-no-estreito" tabindex="0" role="region" aria-labelledby="andamento-titulo"><table>
<caption class="sub">Quantas listas de cada Perfil têm o ato vigente. Cada célula leva à tela onde o ato se faz.</caption>
<thead><tr><th scope="col">Perfil</th><th scope="col">Relação</th><th scope="col">Semente</th>
<th scope="col">Sorteio</th><th scope="col">Corte</th><th scope="col">Apuração</th>
<th scope="col">Resultado</th><th scope="col">Convocação</th></tr></thead>
<tbody>
<tr><th scope="row"><a href="#">Oferta de Vagas Pós-graduação em Educação Especial Inclusiva</a>
<span class="detalhe">3 listas · sorteio público</span></th>
<td data-m="feito">✓ 3 de 3<span class="detalhe">congeladas 03/11</span></td>
<td data-m="feito">✓ 6115<span class="detalhe">observada 05/11</span></td>
<td data-m="feito">✓ 3 de 3</td><td data-m="feito">✓ 3 de 3</td><td data-m="feito">✓ 3 de 3</td>
<td data-m="feito">✓ 3 de 3<span class="detalhe">preliminar</span></td>
<td data-m="falta"><a href="#">● 1 sem comunicação</a><span class="detalhe">7 chamadas · 6 com desfecho</span></td></tr>
<tr><th scope="row"><a href="#">Oferta de Vagas … · Polo Vitória</a>
<span class="detalhe">3 listas · sorteio público</span></th>
<td colspan="7" data-m="na">— Nenhuma inscrição nas 3 listas: não há o que congelar, sortear nem convocar.</td></tr>
</tbody></table></div>
<h3>Em aberto</h3>
<ul class="em-aberto">
<li><span class="quem voce">Você</span><span>1 convocação sem comunicação enviada — Ampla concorrência, Cefor.
<a href="#">Abrir a convocação</a></span></li>
<li><span class="quem">Quem publica resultado</span><span>Resultado definitivo ainda não publicado — as 3 listas
do Cefor têm só o preliminar.</span></li>
</ul>
</section>"""

# ---------------------------------------------------------------------------------------------
# M2 — Edital 57, quem conduz: duas listas em estágios distintos
# ---------------------------------------------------------------------------------------------
M2_BASTAO = """<p class="bastao proposto"><strong>Há 2 atos que você pode praticar neste Edital.</strong>
Eles estão em "Em aberto", abaixo.</p>"""

M2_ANDAMENTO = """<section class="cartao andamento proposto" aria-labelledby="andamento-titulo">
<h2 id="andamento-titulo">Andamento da seleção</h2>
<p class="ajuda">Lido dos atos já praticados, em 06/11/2026 às 11h12. Cada Perfil e cada lista anda no
seu ritmo: o Edital não tem uma etapa única.</p>
<p class="linha-inscricoes"><strong>Inscrições encerradas</strong> em 04/11/2026 · 12 enviadas ·
1 rascunho não enviado, que não conta. <a href="#">Ver inscrições</a></p>
<div class="rolavel-no-estreito" tabindex="0" role="region" aria-labelledby="andamento-titulo"><table>
<caption class="sub">Quantas listas de cada Perfil têm o ato vigente. Cada célula leva à tela onde o ato se faz.</caption>
<thead><tr><th scope="col">Perfil</th><th scope="col">Relação</th><th scope="col">Semente</th>
<th scope="col">Sorteio</th><th scope="col">Corte</th><th scope="col">Apuração</th>
<th scope="col">Resultado</th><th scope="col">Convocação</th></tr></thead>
<tbody>
<tr><th scope="row"><a href="#">Curso de Aperfeiçoamento em Design Educacional</a>
<span class="detalhe">3 listas · sorteio público</span></th>
<td data-m="feito">✓ 3 de 3<span class="detalhe">congeladas 04/11</span></td>
<td data-m="falta"><a href="#">● 6116 não observada</a></td>
<td data-m="depois">aguarda a semente</td><td data-m="depois">—</td><td data-m="depois">—</td>
<td data-m="depois">—</td><td data-m="depois">—</td></tr>
<tr><th scope="row"><a href="#">Curso de Aperfeiçoamento em Tecnologias Digitais Aplicadas à Educação · Campus Vitória</a>
<span class="detalhe">3 listas · sorteio público</span></th>
<td data-m="falta"><a href="#">● 0 de 3</a><span class="detalhe">3, 1 e 1 inscritos</span></td>
<td data-m="depois">aguarda a relação</td><td data-m="depois">—</td><td data-m="depois">—</td>
<td data-m="depois">—</td><td data-m="depois">—</td><td data-m="depois">—</td></tr>
</tbody></table></div>
<h3>Em aberto</h3>
<ul class="em-aberto">
<li><span class="quem voce">Você</span><span>Observar a extração 6116 da Loteria Federal — Design Educacional.
Antes de a Caixa publicá-la, a observação é recusada e nada é gravado. <a href="#">Abrir o sorteio</a></span></li>
<li><span class="quem voce">Você</span><span>Congelar a relação das 3 listas — Tecnologias Digitais, Campus Vitória.
Congelar não se desfaz. <a href="#">Abrir o sorteio</a></span></li>
</ul>
</section>"""

# ---------------------------------------------------------------------------------------------
# M3 — Condução do marco (57, Design Educacional): o que está impedido e por quê
# ---------------------------------------------------------------------------------------------
M3_TABELA = """<div class="proposto">
<div class="proximo"><p><strong>Próximo neste marco:</strong> observar a extração 6116 da Loteria Federal.</p>
<p class="ajuda">As 3 relações estão congeladas desde 04/11. O sorteio de cada lista só fica disponível
depois da semente observada; antes de a Caixa publicar a extração, observar é recusado sem gravar nada.</p>
<a class="botao" href="#">Ir ao sorteio do marco</a></div>
<div class="rolavel-no-estreito andamento" tabindex="0" role="region"><table>
<caption class="sub">Feitos por operação: relação 3 de 3 · sorteio 0 de 3 · corte 0 de 3 · apuração 0 de 3 ·
publicação 0 de 3 · convocação 0 de 3</caption>
<thead><tr><th scope="col">Recorte</th><th scope="col">Relação</th><th scope="col">Sorteio<span class="detalhe">dá a ordem</span></th>
<th scope="col">Corte</th><th scope="col">Apuração</th><th scope="col">Publicação</th><th scope="col">Convocação</th></tr></thead>
<tbody>
<tr><th scope="row">Todos os inscritos (ampla)</th><td data-m="feito">✓ Feito<span class="detalhe">9 participantes</span></td>
<td data-m="aguarda">◷ Aguarda a semente</td><td data-m="depois">depois do sorteio</td><td data-m="depois">—</td><td data-m="depois">—</td><td data-m="depois">—</td></tr>
<tr><th scope="row">Pessoa com Deficiência (PcD)</th><td data-m="feito">✓ Feito<span class="detalhe">3 participantes</span></td>
<td data-m="aguarda">◷ Aguarda a semente</td><td data-m="depois">depois do sorteio</td><td data-m="depois">—</td><td data-m="depois">—</td><td data-m="depois">—</td></tr>
<tr><th scope="row">Preto, Pardos e Indígenas (PPI)</th><td data-m="feito">✓ Feito<span class="detalhe">2 participantes</span></td>
<td data-m="aguarda">◷ Aguarda a semente</td><td data-m="depois">depois do sorteio</td><td data-m="depois">—</td><td data-m="depois">—</td><td data-m="depois">—</td></tr>
</tbody></table></div></div>"""

# M3b — o marco sem inscrito (35, Polo Vitória): "Não se aplica", e nenhum gesto oferecido.
M3B_TABELA = """<div class="proposto"><p class="bastao"><strong>Nada a conduzir neste marco.</strong>
Nenhuma inscrição enviada escolheu este Perfil; ele fica assim até o encerramento do Edital.</p>
<div class="rolavel-no-estreito andamento" tabindex="0" role="region"><table>
<thead><tr><th scope="col">Recorte</th><th scope="col">Relação</th><th scope="col">Sorteio</th><th scope="col">Corte</th>
<th scope="col">Apuração</th><th scope="col">Publicação</th><th scope="col">Convocação</th></tr></thead><tbody>
<tr><th scope="row">Ampla concorrência</th><td colspan="6" data-m="na">— Não se aplica: nenhum inscrito</td></tr>
<tr><th scope="row">Pessoa com Deficiência (PCD)</th><td colspan="6" data-m="na">— Não se aplica: nenhum inscrito</td></tr>
<tr><th scope="row">Pretos, Pardos e Indígenas (PPI)</th><td colspan="6" data-m="na">— Não se aplica: nenhum inscrito</td></tr>
</tbody></table></div></div>"""

# ---------------------------------------------------------------------------------------------
# M4 — Depois de emitir o corte (26, ampla): a transição que diz para onde ir
# ---------------------------------------------------------------------------------------------
M4_SUCESSO = """<div class="proximo proposto" role="status">
<p><strong>Corte emitido</strong> para Ampla concorrência: 7 progridem, nenhum fica fora. O ato é imutável.</p>
<p><strong>Próximo nesta lista:</strong> apurar a ocupação das vagas.</p>
<a class="botao" href="#">Apurar a ocupação deste recorte</a>
<p class="ajuda" style="margin-top:.6rem">Ainda neste marco: <strong>Pessoas pretas, pardas e indígenas</strong> não tem
relação congelada, e por isso não tem ordem nem corte. <a href="#">Abrir o sorteio</a> ·
<a href="#">Conduzir o marco</a></p></div>"""


def entrar(nav, papel):
    contexto = nav.new_context(viewport={"width": 1280, "height": 900}, bypass_csp=True)
    pagina = contexto.new_page()
    pagina.goto(BASE + "/gestao/identificar/demonstracao")
    with pagina.expect_navigation():
        pagina.locator(f"form:has(input[name=papeis][value='{papel}']) button").first.click()
    return pagina


def preparar(pagina, url):
    pagina.goto(BASE + url)
    pagina.add_style_tag(content=CSS)
    pagina.evaluate(
        "() => { const s = document.createElement('div'); s.className = 'selo-maquete';"
        " s.textContent = 'MAQUETE — componente proposto, dados do banco de demonstração';"
        " document.body.appendChild(s); }"
    )


def detalhe_proposto(pagina, url, bastao, andamento):
    preparar(pagina, url)
    pagina.evaluate(
        """([curto, bastao, andamento]) => {
          const acoes = document.querySelector('section[aria-labelledby=acoes-titulo]');
          const imutavel = acoes.querySelector('.imutavel');
          imutavel.innerHTML = curto; imutavel.classList.add('proposto');
          imutavel.insertAdjacentHTML('afterend', bastao);
          document.querySelector('.colunas.ao-topo').insertAdjacentHTML('afterend', andamento);
          document.querySelector('section[aria-labelledby=classificacao-titulo]')?.remove();
        }""",
        [PUBLICADO_CURTO, bastao, andamento],
    )


def conducao_proposta(pagina, url, tabela):
    preparar(pagina, url)
    pagina.evaluate(
        """(tabela) => {
          const sec = document.querySelector('#divulgacao');
          sec.querySelector('.rolavel-no-estreito').outerHTML = tabela;
          document.querySelectorAll('section[aria-labelledby=gestos-titulo], p.nota').forEach(e => e.remove());
        }""",
        tabela,
    )


def corte_proposto(pagina):
    preparar(pagina, CORTE_26)
    pagina.evaluate(
        """(sucesso) => {
          const alvo = [...document.querySelectorAll('main p')].find(p => p.textContent.includes('Geração vigente'));
          alvo.insertAdjacentHTML('beforebegin', sucesso);
          const form = document.querySelector('form[action$="/corte/emitir"]');
          const d = document.createElement('details'); d.className = 'sucessao-recolhida proposto';
          d.innerHTML = '<summary>Suceder este corte (exige motivo)</summary>';
          form.parentNode.insertBefore(d, form); d.appendChild(form);
          const aviso = [...document.querySelectorAll('main p')].find(p => p.textContent.startsWith('Emitir é irreversível'));
          if (aviso) d.appendChild(aviso);
        }""",
        M4_SUCESSO,
    )


def foto(pagina, nome, altura=None):
    opcoes = {"path": str(SAIDA / f"{nome}.jpg"), "type": "jpeg", "quality": 82, "full_page": True}
    if altura:
        opcoes["clip"] = {"x": 0, "y": 0, "width": 1280, "height": altura}
    pagina.screenshot(**opcoes)
    print(nome)


with sync_playwright() as p:
    nav = p.chromium.launch()
    g = entrar(nav, "gestor")
    detalhe_proposto(g, E35, M1_BASTAO, M1_ANDAMENTO)
    foto(g, "v1/M1-detalhe-35-andamento")
    detalhe_proposto(g, E57, M2_BASTAO, M2_ANDAMENTO)
    foto(g, "v1/M2-detalhe-57-listas-em-estagios-distintos")
    conducao_proposta(g, E57 + M57 + "conducao", M3_TABELA)
    foto(g, "M3-conducao-57-operacao-impedida")
    conducao_proposta(g, E35 + M35V + "conducao", M3B_TABELA)
    foto(g, "M3b-conducao-35-vitoria-nao-se-aplica")
    corte_proposto(g)
    foto(g, "M4-depois-do-corte-26", altura=1300)
    nav.close()
