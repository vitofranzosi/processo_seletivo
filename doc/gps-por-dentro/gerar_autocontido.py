"""Exporta o guia e seus anexos num único HTML, sem dependências de execução.

O índice permanece como fonte. A cópia incorpora os documentos e evidências para
que os links de apoio continuem funcionando quando só o HTML for compartilhado.
"""

import base64
import html
import json
import re
from pathlib import Path

PASTA = Path(__file__).resolve().parent
SAIDA = PASTA / "gps-por-dentro-autocontido.html"
DOCUMENTOS = {
    "inventario.md": ("inventario", "Inventário conceitual e fontes"),
    "roteiro-pedagogico.md": ("roteiro", "Roteiro pedagógico"),
    "validacao.md": ("validacao", "Evidências de validação"),
    "avaliacao-critica.md": ("avaliacao", "Avaliação crítica"),
}
CAPTURAS = {
    "capturas/02-marco-desktop.png": ("marco", "Marco no desktop"),
    "capturas/03-corte-desktop.png": ("corte", "Corte no desktop"),
    "capturas/04-apuracao-375.png": ("apuracao", "Apuração no celular"),
}
REGISTROS = {
    "verificacao-postgresql.txt": ("postgresql", "Registro da suíte PostgreSQL"),
    "verificacao-documentacao.txt": (
        "documentacao",
        "Registro dos testes de documentação",
    ),
}
ROTAS = {arquivo: "#anexo/" + dados[0] for arquivo, dados in DOCUMENTOS.items()}
ROTAS.update(
    {arquivo: "#anexo/captura-" + dados[0] for arquivo, dados in CAPTURAS.items()}
)
ROTAS.update(
    {arquivo: "#anexo/registro-" + dados[0] for arquivo, dados in REGISTROS.items()}
)


def em_linha(texto):
    codigos = []

    def proteger(grupo):
        codigos.append("<code>" + html.escape(grupo[1]) + "</code>")
        return f"\x00CODIGO{len(codigos) - 1}\x00"

    texto = re.sub(r"`([^`]+)`", proteger, texto)
    texto = html.escape(texto)

    def vincular(grupo):
        rotulo, destino = grupo[1], html.unescape(grupo[2])
        if destino in ROTAS:
            return '<a href="' + ROTAS[destino] + '">' + rotulo + "</a>"
        # As fontes do repositório são referências bibliográficas, não recursos
        # necessários ao guia. Mantê-las como caminhos evita links locais quebrados.
        return (
            rotulo
            + ' <small class="muted">(referência: '
            + html.escape(destino)
            + ")</small>"
        )

    texto = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", vincular, texto)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", texto)
    for indice, codigo in enumerate(codigos):
        texto = texto.replace(f"\x00CODIGO{indice}\x00", codigo)
    return texto


def markdown(texto):
    linhas, partes, indice = texto.splitlines(), [], 0
    while indice < len(linhas):
        linha = linhas[indice]
        if not linha.strip():
            indice += 1
            continue
        if linha.startswith("```"):
            bloco = []
            indice += 1
            while indice < len(linhas) and not linhas[indice].startswith("```"):
                bloco.append(linhas[indice])
                indice += 1
            partes.append(
                "<pre><code>" + html.escape("\n".join(bloco)) + "</code></pre>"
            )
            indice += 1
            continue
        titulo = re.match(r"^(#{1,6})\s+(.+)$", linha)
        if titulo:
            nivel = min(len(titulo[1]) + 1, 6)
            partes.append(f"<h{nivel}>" + em_linha(titulo[2]) + f"</h{nivel}>")
            indice += 1
            continue
        if (
            linha.startswith("|")
            and indice + 1 < len(linhas)
            and re.match(r"^\|[\s:|\-]+\|\s*$", linhas[indice + 1])
        ):
            cabecalho = linha.strip().strip("|").split("|")
            tabela = [
                '<div class="anexo-tabela" tabindex="0" role="region" aria-label="Tabela de referência; role horizontalmente se necessário"><table><thead><tr>'
                + "".join(
                    '<th scope="col">' + em_linha(c.strip()) + "</th>"
                    for c in cabecalho
                )
                + "</tr></thead><tbody>"
            ]
            indice += 2
            while indice < len(linhas) and linhas[indice].startswith("|"):
                celulas = linhas[indice].strip().strip("|").split("|")
                tabela.append(
                    "<tr>"
                    + "".join("<td>" + em_linha(c.strip()) + "</td>" for c in celulas)
                    + "</tr>"
                )
                indice += 1
            partes.append("".join(tabela) + "</tbody></table></div>")
            continue
        if linha.startswith("- "):
            itens = []
            while indice < len(linhas) and linhas[indice].startswith("- "):
                item = [linhas[indice][2:]]
                indice += 1
                while indice < len(linhas) and linhas[indice].startswith("  "):
                    item.append(linhas[indice].strip())
                    indice += 1
                itens.append("<li>" + em_linha(" ".join(item)) + "</li>")
            partes.append("<ul>" + "".join(itens) + "</ul>")
            continue
        paragrafo = [linha.strip()]
        indice += 1
        while (
            indice < len(linhas)
            and linhas[indice].strip()
            and not linhas[indice].startswith(("#", "- ", "```", "|"))
        ):
            paragrafo.append(linhas[indice].strip())
            indice += 1
        partes.append("<p>" + em_linha(" ".join(paragrafo)) + "</p>")
    return "\n".join(partes)


def gerar():
    anexos = {}
    for arquivo, (chave, titulo) in DOCUMENTOS.items():
        anexos[chave] = {
            "titulo": titulo,
            "html": markdown((PASTA / arquivo).read_text()),
        }
    for arquivo, (chave, titulo) in CAPTURAS.items():
        imagem = base64.b64encode((PASTA / arquivo).read_bytes()).decode()
        anexos["captura-" + chave] = {
            "titulo": titulo,
            "html": '<p>Captura real da POC, incluída no registro de validação de 08/11/2026.</p><img class="anexo-imagem" alt="'
            + html.escape(titulo)
            + '" src="data:image/png;base64,'
            + imagem
            + '">',
        }
    for arquivo, (chave, titulo) in REGISTROS.items():
        anexos["registro-" + chave] = {
            "titulo": titulo,
            "html": "<pre>" + html.escape((PASTA / arquivo).read_text()) + "</pre>",
        }
    fonte = (PASTA / "index.html").read_text()
    for arquivo, rota in ROTAS.items():
        fonte = fonte.replace('href="' + arquivo + '"', 'href="' + rota + '"')
    fonte = fonte.replace(
        "As fontes e o inventário estão no arquivo inventario.md da mesma pasta.",
        "Os documentos e evidências estão incorporados a este mesmo HTML.",
    )
    fonte = fonte.replace(
        "Funciona localmente, sem conexão ou cadastro.",
        "Versão autocontida · aplicativo e anexos no mesmo arquivo.",
    )
    dados = json.dumps(anexos, ensure_ascii=False).replace("<", "\\u003c")
    inicio = "<script>\n'use strict';"
    assert fonte.count(inicio) == 1
    fonte = fonte.replace(
        inicio,
        '<script type="application/json" id="anexos">' + dados + "</script>\n" + inicio,
    )
    comportamento = r"""
const ANEXOS=JSON.parse(document.getElementById('anexos').textContent);
function anexo(id){
 const documento=ANEXOS[id];
 if(!documento)return sobre();
 return `<div class="cabecalho"><div><span class="etiqueta">Material incorporado · consulta offline</span><h1>${esc(documento.titulo)}</h1></div><a class="botao claro" href="#sobre">← Fontes e limites</a></div><nav class="botoes anexo-nav" aria-label="Documentos incorporados"><a class="botao claro" href="#anexo/inventario">Inventário</a><a class="botao claro" href="#anexo/roteiro">Roteiro</a><a class="botao claro" href="#anexo/validacao">Validação</a><a class="botao claro" href="#anexo/avaliacao">Avaliação crítica</a></nav><article class="anexo">${documento.html}</article>`;
}
"""
    fonte = fonte.replace(inicio, inicio + "\n" + comportamento)
    fonte = fonte.replace(
        "tipo==='sobre'?sobre():", "tipo==='anexo'?anexo(id):tipo==='sobre'?sobre():"
    )
    fonte = fonte.replace(
        "</style>",
        """
.anexo{max-width:100%;overflow-wrap:anywhere}.anexo-nav{margin-bottom:28px}
.anexo h2,.anexo h3,.anexo h4{margin:28px 0 16px}.anexo h2{font-size:2rem}
.anexo h3{font:1.5rem/1.25 Georgia,serif}.anexo p{max-width:900px;margin:12px 0}
.anexo li{margin:8px 0;max-width:900px}.anexo pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--branco);border:1px solid var(--linha);border-radius:10px;padding:20px;font-size:.8rem}
.anexo-tabela{overflow:auto;border:1px solid var(--linha);border-radius:10px;margin:20px 0}
.anexo table{width:100%;min-width:700px;border-collapse:collapse;font-size:.83rem;background:var(--branco)}
.anexo th,.anexo td{padding:12px 15px;border-bottom:1px solid var(--linha);text-align:left;vertical-align:top}
.anexo th{background:var(--suave)}.anexo-imagem{display:block;max-width:100%;height:auto;margin:20px auto}
@media(max-width:760px){.anexo h2{font-size:1.7rem}.anexo-nav{gap:8px}.anexo-nav .botao{font-size:.75rem;padding:9px 12px}.anexo pre{padding:14px;font-size:.73rem}}
</style>""",
    )
    SAIDA.write_text(fonte)
    print(
        f"{SAIDA.name}: {SAIDA.stat().st_size:,} bytes; 4 documentos, 3 capturas e 2 registros incorporados."
    )


if __name__ == "__main__":
    gerar()
