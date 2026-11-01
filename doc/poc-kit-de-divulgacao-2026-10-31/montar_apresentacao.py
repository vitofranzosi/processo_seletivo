"""A galeria das peças e o wireframe da tela, montados **do que a POC gerou** em `saidas/`.

Nada aqui é redigitado: os textos, as notas e a imagem do wireframe são lidos dos arquivos que o
roteiro produziu, para que a maquete mostre o material real, e não uma versão idealizada dele.

    uv run --with resvg-py python montar_apresentacao.py   (de dentro desta pasta)

Sem Django: lê JSON e PNG, e só. A galeria sai pelo mesmo rasterizador das peças, com a mesma fonte.
"""

import base64
import html
import json
from pathlib import Path

import resvg_py

PASTA = Path(__file__).resolve().parent
SAIDAS = PASTA / "saidas"
FONTES = [
    str(PASTA.parents[1] / "backend/processo_seletivo/publicacoes/infrastructure/fontes" / nome)
    for nome in ("EditalSans-Regular.ttf", "EditalSans-Bold.ttf")
]
DESTAQUE = "91-prorrogado-por-retificacao"

ORDEM = [
    "91-inscricoes-futuras",
    "91-inscricoes-em-andamento",
    "91-prorrogado-por-retificacao",
    "01-retificacao-a-vigorar",
    "01-depois-da-vigencia",
    "92-muitos-perfis",
    "um-perfil",
    "localidade-ausente",
    "sem-periodo-designado",
    "92-retificacao-que-nao-muda-o-material",
]


def _ler(cenario, arquivo):
    return (SAIDAS / cenario / arquivo).read_text()


def _png64(cenario):
    return base64.b64encode((SAIDAS / cenario / "peca-feed-1080x1350.png").read_bytes()).decode()


def galeria():
    colunas, largura, altura, margem, legenda = 5, 360, 450, 40, 96
    linhas = (len(ORDEM) + colunas - 1) // colunas
    total_l = colunas * (largura + margem) + margem
    total_a = linhas * (altura + legenda + margem) + margem + 70
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_l}" height="{total_a}">',
        f'<rect width="{total_l}" height="{total_a}" fill="#f4f4f0"/>',
        f'<text x="{margem}" y="56" font-family="Edital Sans" font-size="30" font-weight="700" '
        'fill="#1c1c1c">POC do Kit de Divulgação — as peças dos cenários (31/10/2026)</text>',
    ]
    for posicao, cenario in enumerate(ORDEM):
        linha, coluna = divmod(posicao, colunas)
        x = margem + coluna * (largura + margem)
        y = 90 + linha * (altura + legenda + margem)
        conferencia = json.loads(_ler(cenario, "conferencia.json"))
        partes.append(
            f'<rect x="{x - 1}" y="{y - 1}" width="{largura + 2}" height="{altura + 2}" fill="#cfcfc8"/>'
            f'<image x="{x}" y="{y}" width="{largura}" height="{altura}" '
            f'href="data:image/png;base64,{_png64(cenario)}"/>'
            f'<text x="{x}" y="{y + altura + 34}" font-family="Edital Sans" font-size="20" '
            f'font-weight="700" fill="#1c1c1c">{html.escape(cenario)}</text>'
        )
        descricao = conferencia["descricao"]
        for indice, pedaco in enumerate(_partir(descricao, 40)[:2]):
            partes.append(
                f'<text x="{x}" y="{y + altura + 60 + indice * 22}" font-family="Edital Sans" '
                f'font-size="17" fill="#555555">{html.escape(pedaco)}</text>'
            )
    partes.append("</svg>")
    png = resvg_py.svg_to_bytes(
        svg_string="".join(partes), font_files=FONTES, skip_system_fonts=True
    )
    (SAIDAS / "galeria.png").write_bytes(bytes(png))


def _partir(texto, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        if len(f"{atual} {palavra}".strip()) > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = f"{atual} {palavra}".strip()
    return [*linhas, atual] if atual else linhas


def _bloco_de_texto(rotulo, texto, chave):
    return f"""
      <article class="texto">
        <header><h3>{html.escape(rotulo)}</h3>
          <button type="button" class="copiar" data-alvo="{chave}">Copiar</button></header>
        <pre id="{chave}">{html.escape(texto)}</pre>
      </article>"""


def wireframe():
    ficha = json.loads(_ler(DESTAQUE, "ficha.json"))
    manifesto = json.loads(_ler(DESTAQUE, "manifesto.json"))
    blocos = json.loads(_ler(DESTAQUE, "textos.json"))
    notas = blocos["notas"]
    desatualizado = [n for n in notas if n.startswith("Material anterior")]
    demais = [n for n in notas if not n.startswith("Material anterior")]
    alternativo = _ler(DESTAQUE, "texto-alternativo.txt").strip()

    ofertas = "".join(
        f"<tr><td>{html.escape(o['localidade'] or o['nome'])}</td><td>{html.escape(o['quantidade'])}</td></tr>"
        for o in ficha["ofertas"]
    )
    textos = "".join(
        _bloco_de_texto(rotulo, blocos[chave], f"t-{indice}")
        for indice, (rotulo, chave) in enumerate(
            (
                ("Legenda para rede social", "legenda"),
                ("Resumo institucional", "resumo"),
                ("Chamada curta para o site", "chamada_para_o_site"),
                ("Texto para mensagens", "texto_para_mensagem"),
                ("Link oficial", "link_oficial"),
            )
        )
    )
    estados = []
    for cenario, rotulo in (
        ("01-retificacao-a-vigorar", "Retificação publicada a vigorar"),
        ("sem-periodo-designado", "Edital sem período designado"),
        ("92-muitos-perfis", "Título longo e 18 opções"),
        ("cancelado", "Edital cancelado"),
    ):
        caminho = SAIDAS / cenario / "textos.json"
        primeira = (
            "\n".join(json.loads(caminho.read_text())["notas"])
            if caminho.exists()
            else _ler(cenario, "kit.txt").strip()
        )
        estados.append(
            f"<article class='estado'><h3>{html.escape(rotulo)}</h3><pre>{html.escape(primeira)}</pre></article>"
        )
    omissoes = json.loads(_ler("92-muitos-perfis", "conferencia.json"))["omissoes"]

    pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kit de divulgação — wireframe</title>
<style>
  :root {{ --verde:#15803d; --verde-texto:#146c37; --verde-escuro:#0b5a2a; --verde-claro:#e7f5ec;
          --texto:#1c1c1c; --fraco:#555; --borda:#d4d4d4; --fundo:#f8f8f8; --amarelo:#8a5300;
          --amarelo-fundo:#fdf5e5; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:"Open Sans","Segoe UI",system-ui,sans-serif; color:var(--texto);
          background:var(--fundo); }}
  .topo {{ background:var(--verde-escuro); color:#fff; padding:10px 16px; display:flex; gap:10px;
           align-items:center; }}
  .sigla {{ background:#fff; color:var(--verde-escuro); font-weight:700; border-radius:6px;
            padding:2px 6px; font-size:.75rem; }}
  .conceito {{ background:var(--amarelo-fundo); color:var(--amarelo); border-bottom:1px solid #e8d3a8;
               padding:8px 16px; font-size:.875rem; }}
  main {{ max-width:1180px; margin:0 auto; padding:16px; }}
  .trilha {{ font-size:.875rem; color:var(--fraco); }}
  h1 {{ margin:.25rem 0 0; font-size:1.6rem; }}
  .sub {{ color:var(--fraco); margin:.25rem 0 1rem; }}
  .aviso {{ border-left:4px solid var(--amarelo); background:var(--amarelo-fundo); padding:10px 14px;
            margin:0 0 16px; border-radius:4px; }}
  .aviso strong {{ color:var(--amarelo); }}
  section {{ background:#fff; border:1px solid var(--borda); border-radius:8px; padding:16px;
             margin-bottom:16px; }}
  h2 {{ font-size:1.1rem; margin:0 0 .75rem; }}
  table {{ border-collapse:collapse; width:100%; font-size:.95rem; }}
  td, th {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--borda); vertical-align:top; }}
  th {{ width:14rem; color:var(--fraco); font-weight:600; }}
  .duas {{ display:grid; grid-template-columns:minmax(0,1.2fr) minmax(0,1fr); gap:16px; }}
  @media (max-width:860px) {{ .duas {{ grid-template-columns:1fr; }} }}
  .texto {{ border:1px solid var(--borda); border-radius:6px; margin-bottom:10px; }}
  .texto header {{ display:flex; justify-content:space-between; align-items:center; padding:6px 10px;
                   background:var(--fundo); border-bottom:1px solid var(--borda); }}
  .texto h3 {{ margin:0; font-size:.95rem; }}
  pre {{ white-space:pre-wrap; word-break:break-word; margin:0; padding:10px; font-family:inherit;
         font-size:.9rem; }}
  button, .botao {{ font:inherit; font-size:.875rem; border:1px solid var(--verde-texto);
                    color:var(--verde-texto); background:#fff; border-radius:6px; padding:4px 10px;
                    cursor:pointer; text-decoration:none; display:inline-block; }}
  .primario {{ background:var(--verde-escuro); color:#fff; border-color:var(--verde-escuro);
               padding:8px 16px; }}
  .peca img {{ width:100%; height:auto; border:1px solid var(--borda); border-radius:4px; }}
  .peca .acoes {{ display:flex; gap:8px; margin:10px 0; flex-wrap:wrap; }}
  .alt {{ font-size:.85rem; color:var(--fraco); }}
  .omissao {{ font-size:.85rem; color:var(--amarelo); }}
  .estados {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; }}
  .estado {{ border:1px dashed var(--borda); border-radius:6px; padding:8px; }}
  .estado h3 {{ margin:0 0 6px; font-size:.9rem; }}
  .estado pre {{ font-size:.8rem; padding:0; color:var(--fraco); }}
  .pacote {{ display:flex; gap:16px; align-items:center; flex-wrap:wrap; }}
  .pacote p {{ margin:0; color:var(--fraco); font-size:.9rem; flex:1 1 20rem; }}
</style>
</head>
<body>
<div class="topo"><span class="sigla">GPS</span> Gestão de Processos Seletivos</div>
<div class="conceito"><strong>Maquete conceitual.</strong> Tela não integrada ao GPS; textos e peça são
os que a POC gerou para o Edital de demonstração 91/2026 depois da Retificação nº 1. A faixa de marca da
peça é marcador, e não ativo oficial.</div>
<main>
  <div class="trilha">Editais › {html.escape(ficha["identificacao"])} › Kit de divulgação</div>
  <h1>Kit de divulgação</h1>
  <p class="sub">{html.escape(ficha["identificacao"])} — {html.escape(ficha["titulo_sem_numero"])} ·
    {html.escape(ficha["unidade_sigla"])}</p>

  {"".join(f'<p class="aviso"><strong>Material anterior desatualizado.</strong> Mudou: {html.escape(n.split("Mudou: ", 1)[1])}. Os textos e a peça abaixo já usam a versão nova.</p>' for n in desatualizado)}

  <section>
    <h2>1. Confira as informações oficiais</h2>
    <table>
      <tr><th>Situação ({html.escape(ficha["referencia_texto"])})</th><td>{html.escape(ficha["situacao_rotulo"])}</td></tr>
      <tr><th>Inscrições</th><td>{html.escape(ficha["inicio_data"])}, {html.escape(ficha["inicio_hora"])}
        a {html.escape(ficha["fim_data"])}, {html.escape(ficha["fim_hora"])}
        {"<br><strong>Prorrogado</strong>: o término era " + html.escape(ficha["fim_original_data"]) if ficha["prorrogado"] else ""}</td></tr>
      <tr><th>Oferta</th><td><table>{ofertas}</table></td></tr>
      <tr><th>Unidade</th><td>{html.escape(ficha["unidade_nome"] or ficha["unidade_sigla"])}</td></tr>
      <tr><th>Versão usada</th><td>{html.escape(ficha["versao_ato"])}, vigente desde {html.escape(ficha["versao_desde_texto"])}
        · ref. {html.escape(ficha["impressao"][:8])}</td></tr>
      <tr><th>Página oficial</th><td><a href="{html.escape(ficha["endereco"])}">{html.escape(ficha["endereco"])}</a></td></tr>
    </table>
    <ul class="alt">{"".join(f"<li>{html.escape(n)}</li>" for n in demais)}</ul>
  </section>

  <div class="duas">
    <section>
      <h2>2. Textos para divulgação</h2>
      {textos}
    </section>
    <section class="peca">
      <h2>3. Criativo — feed 1080 × 1350</h2>
      <img src="data:image/png;base64,{_png64(DESTAQUE)}" alt="{html.escape(alternativo)}">
      <div class="acoes">
        <a class="botao" href="#">Baixar PNG</a><a class="botao" href="#">Baixar SVG</a>
        <button type="button" class="copiar" data-alvo="alt">Copiar texto alternativo</button>
      </div>
      <p class="alt"><strong>Texto alternativo:</strong> <span id="alt">{html.escape(alternativo)}</span></p>
      <p class="alt">Template {html.escape(manifesto["peca"]["template"])} · {html.escape(manifesto["peca"]["rasterizador"])}</p>
    </section>
  </div>

  <section>
    <h2>4. Exportar tudo</h2>
    <div class="pacote">
      <a class="botao primario" href="#">Baixar pacote (.zip)</a>
      <p>Textos (.md e .txt), peça (.svg e .png), texto alternativo, a ficha e o manifesto com a versão
      usada, o instante da geração e os próximos marcos conhecidos.</p>
    </div>
  </section>

  <section>
    <h2>Outros estados da mesma tela</h2>
    <div class="estados">{"".join(estados)}</div>
    <p class="omissao">Título longo (92/2026): {html.escape("; ".join(omissoes))}</p>
  </section>
</main>
<script>
  document.querySelectorAll("button.copiar").forEach(function (botao) {{
    botao.addEventListener("click", function () {{
      var alvo = document.getElementById(botao.dataset.alvo);
      if (navigator.clipboard && alvo) {{
        navigator.clipboard.writeText(alvo.textContent).then(function () {{
          botao.textContent = "Copiado";
        }});
      }}
    }});
  }});
</script>
</body>
</html>
"""
    (PASTA / "wireframe.html").write_text(pagina)


if __name__ == "__main__":
    galeria()
    wireframe()
