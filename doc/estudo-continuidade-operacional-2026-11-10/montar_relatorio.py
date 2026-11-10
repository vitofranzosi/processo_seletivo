# ruff: noqa: E501 — roteiro de estudo, fora do lint do backend.
"""O estudo inteiro num HTML só, para ler fora do repositório ou entregar a outro agente.

    cd backend && uv run --with markdown python ../doc/estudo-continuidade-operacional-2026-11-10/montar_relatorio.py

Junta o README e as entregas 01 a 06, a validação e as capturas que sustentam as conclusões. As capturas
vão embutidas, reduzidas a 1000 px de largura e em JPEG, para o arquivo caber num anexo. As 110
capturas originais continuam em `capturas/`; o HTML não as substitui.

Sem dependência externa no resultado: estilo inline, nenhuma fonte, nenhum script. É um arquivo para
abrir no navegador, e não uma página da gestão — a CSP da gestão não se aplica a ele.
"""

import base64
import html
import re
import subprocess
import tempfile
from pathlib import Path

import markdown

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "estudo-continuidade-operacional.html"

DOCUMENTOS = [
    ("README.md", "inicio", "Resumo"),
    ("01-mapa-das-jornadas.md", "mapa", "A · Mapa das jornadas"),
    ("02-diagnostico.md", "diagnostico", "B · Diagnóstico"),
    ("03-inventario-de-melhorias.md", "inventario", "C · Inventário de melhorias"),
    ("04-prototipos.md", "prototipos", "D · Protótipos"),
    ("05-plano-de-evolucao.md", "plano", "E · Plano de evolução"),
    ("06-achados-funcionais.md", "achados", "Achados funcionais"),
    ("07-triagem-f1-f3.md", "triagem", "Triagem F-1 a F-3"),
]

# As capturas que sustentam as conclusões principais, na ordem em que o leitor precisa delas.
EVIDENCIAS = [
    (
        "a02-c06-sorteio-antes-dobra",
        'A2 · Sorteio (C06): a primeira dobra ao chegar pela providência. O método e o botão primário "Observar" vêm antes; "Publicar e congelar" só aparece a 1.681 px.',
    ),
    (
        "a04b-c06-congelado-1-dobra",
        'A4 · Depois de congelar a ampla: "Próximo nesta lista: Observar a extração", com a PPP ainda por fixar.',
    ),
    (
        "a05-c06-centro-apos-congelar-1",
        'A5 · O Centro depois do primeiro congelamento: "Todas já podem ser feitas … o GPS não escolhe a ordem".',
    ),
    (
        "a09-c06-sortear-ppp-congelada-depois",
        "A8 · O sorteio da PPP, congelada depois da semente, é recusado; a saída é Retificar (F-1).",
    ),
    (
        "d03-c10-convocado-num-clique",
        'D3 · "Convocar as 3" praticou e enviou as 3 comunicações num clique (M-04).',
    ),
    (
        "c10-c08-ordem-sucessora-previa",
        'C7 · A prévia da ordem sucessora: o reabilitado sairia "sem posição" (F-2).',
    ),
    (
        "t03-c08-sucessora-conferencia",
        "Triagem F-2 · A conferência da sucessora avisa que ela ficará obsoleta; o serviço aceita (128).",
    ),
    (
        "t06-c08-corte-emitido-sobre-incompleta",
        "Triagem F-2 · O corte sobre a ordem incompleta é aceito sem aviso; o próximo já é a Análise documental.",
    ),
    (
        "t01-c06r4-so-a-data-apos-fixar-ampla",
        'Triagem F-1 · Fonte "só a data": depois de fixar a ampla, o retorno não aponta a semente, que aguarda o dia da extração.',
    ),
]
PROTOTIPOS = [
    ("sorteio-c06-inicial", "Sorteio antes de fixar — M-03, M-06 (D-5 marcado)"),
    ("sorteio-c06-apos-fixar-a-ampla", "Depois de fixar a ampla — M-01, M-07 (D-5 marcado)"),
    ("documentos-c12-apos-conferir", "Documentos depois da conferência — M-01, M-07, M-08"),
    (
        "convocar-c15-conferencia",
        "Convocar os titulares — antes: a tela da convocação; depois: a conferência (M-04)",
    ),
]


def imagem(caminho):
    with tempfile.TemporaryDirectory() as pasta:
        destino = Path(pasta) / "x.jpg"
        subprocess.run(
            [
                "sips",
                "-s",
                "format",
                "jpeg",
                "-s",
                "formatOptions",
                "70",
                "--resampleWidth",
                "1000",
                str(caminho),
                "--out",
                str(destino),
            ],
            check=True,
            capture_output=True,
        )
        dados = base64.b64encode(destino.read_bytes()).decode()
    return f"data:image/jpeg;base64,{dados}"


def figura(nome, legenda):
    arquivo = AQUI / "capturas" / f"{nome}.png"
    return (
        f'<figure><img src="{imagem(arquivo)}" alt="{html.escape(legenda)}">'
        f"<figcaption>{html.escape(legenda)} <code>{nome}.png</code></figcaption></figure>"
    )


ITEM = re.compile(r"^( *)([-*]|\d+\.) ")


def normalizar_listas(texto):
    """Ajusta o Markdown do GitHub ao Python-Markdown, que é mais estrito em duas coisas.

    No GitHub, uma lista pode vir logo abaixo do parágrafo e aninhar com 2 ou 3 espaços. O
    Python-Markdown exige uma linha em branco antes da lista e 4 espaços por nível; sem os dois, a
    lista vira texto corrido com hífens, e a resposta do README some num parágrafo só.
    """
    saida = []
    item = None  # o recuo do último item, enquanto a lista não acaba
    for linha in texto.splitlines():
        casou = ITEM.match(linha)
        if casou:
            nivel = len(casou.group(1)) // 2 if casou.group(1) else 0
            linha = "    " * nivel + linha.lstrip()
            anterior = saida[-1] if saida else ""
            if anterior.strip() and item is None:
                saida.append("")
            item = 4 * nivel
        elif linha.startswith("  ") and item is not None:
            # A continuação de um item acompanha o recuo dele, e não o da linha anterior.
            linha = " " * (item + 4) + linha.lstrip()
        elif not linha.strip() or not linha.startswith(" "):
            item = None
        saida.append(linha)
    return "\n".join(saida)


def converter(texto):
    corpo = markdown.markdown(
        normalizar_listas(texto), extensions=["tables", "fenced_code", "sane_lists"]
    )
    # Os links entre as entregas viram âncoras desta página; os de arquivo do repositório ficam como
    # texto em código, porque fora do repositório eles não abrem.
    for arquivo, ancora, _ in DOCUMENTOS:
        corpo = corpo.replace(f'href="{arquivo}"', f'href="#{ancora}"')
    corpo = re.sub(
        r'<a href="(?!#|https?://)([^"]+)">(.*?)</a>',
        lambda m: f'{m.group(2)} <span class="caminho">({html.escape(m.group(1))})</span>',
        corpo,
    )
    return corpo


def main():
    secoes = []
    for arquivo, ancora, _titulo in DOCUMENTOS:
        corpo = converter((AQUI / arquivo).read_text())
        secoes.append(
            f'<section id="{ancora}" class="documento"><p class="origem">{arquivo}</p>{corpo}</section>'
        )
        if ancora == "diagnostico":
            secoes.append(
                '<section id="evidencias" class="documento"><h1>Evidências — as capturas principais</h1>'
                "<p>Reduzidas para caber no arquivo. As 110 originais estão em <code>capturas/</code>.</p>"
                + "".join(figura(n, legenda) for n, legenda in EVIDENCIAS)
                + "</section>"
            )
        if ancora == "prototipos":
            pares = "".join(
                f'<h3>{html.escape(legenda)}</h3><div class="par">'
                + figura(f"prototipo-antes-{nome}-dobra", "Antes — a tela real")
                + figura(f"prototipo-depois-{nome}-dobra", "Depois — o protótipo")
                + "</div>"
                for nome, legenda in PROTOTIPOS
            )
            validacao = html.escape((AQUI / "validacao.txt").read_text())
            secoes.append(
                '<section id="prototipos-imagens" class="documento"><h1>Protótipos — antes e depois, na primeira dobra (1440 × 900)</h1>'
                f"{pares}<h2>Validação automatizada (validacao.txt)</h2><pre>{validacao}</pre></section>"
            )
    indice = "".join(f'<li><a href="#{a}">{html.escape(t)}</a></li>' for _, a, t in DOCUMENTOS)
    indice = indice.replace(
        '<li><a href="#mapa">',
        '<li><a href="#evidencias">Evidências</a></li><li><a href="#mapa">',
        1,
    )
    SAIDA.write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Continuidade operacional do GPS</title>
<style>
:root{{--fundo:#f7f7f5;--papel:#fff;--texto:#1d2420;--fraco:#5b6660;--borda:#d9ddd9;--verde:#1b6b3a;--amarelo:#fff6dc}}
@media (prefers-color-scheme:dark){{:root{{--fundo:#141816;--papel:#1c211e;--texto:#e6ebe7;--fraco:#a3aea7;--borda:#333b36;--verde:#6fcf97;--amarelo:#3a3320}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--fundo);color:var(--texto);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
nav{{position:sticky;top:0;z-index:2;background:var(--papel);border-bottom:1px solid var(--borda);padding:.5rem 16px}}
nav ul{{display:flex;flex-wrap:wrap;gap:.25rem 1rem;list-style:none;margin:0;padding:0;font-size:.9rem}}
main{{max-width:1100px;margin:0 auto;padding:1rem 16px 4rem}}
.documento{{background:var(--papel);border:1px solid var(--borda);border-radius:8px;padding:1.25rem 1.5rem;margin:1.5rem 0;overflow-wrap:anywhere}}
.origem{{margin:0;color:var(--fraco);font-size:.8rem;font-family:ui-monospace,monospace}}
h1{{font-size:1.5rem;margin:.4rem 0 1rem}} h2{{font-size:1.2rem;margin-top:1.8rem}} h3{{font-size:1.05rem;margin-top:1.4rem}}
a{{color:var(--verde)}}
table{{border-collapse:collapse;width:100%;font-size:.85rem;margin:.8rem 0;display:block;overflow-x:auto}}
th,td{{border:1px solid var(--borda);padding:.35rem .5rem;vertical-align:top;text-align:left}}
th{{background:var(--fundo)}}
code,pre{{font-family:ui-monospace,monospace;font-size:.85em}}
pre{{background:var(--fundo);border:1px solid var(--borda);padding:.75rem;overflow-x:auto;white-space:pre-wrap}}
blockquote{{margin:1rem 0;padding:.5rem 1rem;border-left:4px solid var(--verde);background:var(--fundo)}}
.caminho{{color:var(--fraco);font-family:ui-monospace,monospace;font-size:.8em}}
figure{{margin:1rem 0}} figure img{{max-width:100%;border:1px solid var(--borda);border-radius:4px}}
figcaption{{font-size:.85rem;color:var(--fraco)}}
.par{{display:grid;grid-template-columns:1fr;gap:.25rem}}
</style></head><body>
<nav aria-label="Seções"><ul>{indice}<li><a href="#prototipos-imagens">Antes e depois</a></li></ul></nav>
<main>
<p class="origem">doc/estudo-continuidade-operacional-2026-11-10 · PR vitofranzosi/processo_seletivo#445 · gerado por montar_relatorio.py</p>
{"".join(secoes)}
</main></body></html>
""")
    print(f"{SAIDA.name}: {SAIDA.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
