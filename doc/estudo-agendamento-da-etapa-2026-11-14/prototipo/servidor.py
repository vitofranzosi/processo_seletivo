# ruff: noqa: E501 — roteiro de estudo, fora do lint do backend.
"""Serve o protótipo do agendamento da Etapa, estático, com as folhas reais e a CSP de produção.

    python3 doc/estudo-agendamento-da-etapa-2026-11-14/prototipo/servidor.py 8166

Abra <http://localhost:8166/>. Nada aqui fala com o GPS: o estado do percurso fica no
`sessionStorage` do navegador, e "Recomeçar" o apaga.

**As folhas não são cópia.** `/static/shared/`, `/static/interface/` e `/static/portal/` são servidas
direto de `backend/processo_seletivo/*/static/`, de modo que o protótipo envelhece junto com a
gestão, e o que só funciona aqui por causa de uma regra copiada não existe.

**A CSP é a de produção** (`shared/politica_de_conteudo.py`: `style-src 'self'`, `script-src 'self'`,
sem `unsafe-inline`). Sem ela, um `style=""` escrito no protótipo funcionaria aqui e sumiria em
silêncio na implementação — a armadilha que o CLAUDE.md registra.

**As páginas são fragmentos.** Cada arquivo de `paginas/` traz só o conteúdo de `main`, com um
cabeçalho em comentário (`titulo`, `trilha`, `moldura`), e o servidor o envolve na moldura da
gestão (`gestao`), do portal (`portal`) ou do e-mail (`correio`). A moldura é a renderizada pelo
`base.html` real, sem as seções que o protótipo não percorre.
"""

from __future__ import annotations

import functools
import html
import http.server
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PAGINAS = AQUI / "paginas"
PROPRIOS = AQUI / "static"
BACKEND = AQUI.parents[2] / "backend" / "processo_seletivo"
ESTATICOS = {
    "/static/shared/": BACKEND / "shared" / "static" / "shared",
    "/static/interface/": BACKEND / "interface" / "static" / "interface",
    "/static/portal/": BACKEND / "portal" / "static" / "portal",
    "/static/prototipo/": PROPRIOS,
}
CSP = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:"
FOLHAS_DA_GESTAO = [
    "base",
    "moldura",
    "impressao",
    "componentes",
    "formularios",
    "tabelas",
    "telas",
]

SIMBOLOS = """<svg class="simbolos" width="0" height="0" aria-hidden="true" focusable="false">
  <symbol id="i-pasta" viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></symbol>
  <symbol id="i-prancheta" viewBox="0 0 24 24"><rect x="5" y="4" width="14" height="17" rx="2"></rect><path d="M9 4V3h6v1M9 12.5l2 2 4-4"></path></symbol>
  <symbol id="i-calendario" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M3 10h18M8 3v4M16 3v4M7.5 14h2M11 14h2M14.5 14h2M7.5 17.5h2M11 17.5h2"></path></symbol>
  <symbol id="i-envelope" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="M3 7l9 6 9-6"></path></symbol>
  <symbol id="i-livro" viewBox="0 0 24 24"><path d="M12 6.5C10.5 5 8 4.5 4 4.5v13c4 0 6.5.5 8 2 1.5-1.5 4-2 8-2v-13c-4 0-6.5.5-8 2zM12 6.5v13"></path></symbol>
  <symbol id="i-sair" viewBox="0 0 24 24"><path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l5-5-5-5M15 12H4"></path></symbol>
  <symbol id="i-painel" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"></rect><path d="M9 4v16"></path></symbol>
</svg>"""

GESTAO = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} — Cefor/Ifes</title>
<link rel="stylesheet" href="/static/shared/tokens.css">
{folhas}
{folhas_da_tela}
<link rel="stylesheet" href="/static/prototipo/agenda.css">
</head>
<body data-pagina="{pagina}">
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<div class="shell" data-barra="expandida">
<script src="/static/interface/shell.js"></script>
{simbolos}
<div class="barra-lateral">
  <div class="marca-da-barra">
    <a class="marca" href="/"><span class="sigla-do-produto" aria-hidden="true">GPS</span><span class="nome-do-produto">Gestão de Processos Seletivos<span>Cefor/Ifes</span></span></a>
  </div>
  <button type="button" class="abrir-secoes" popovertarget="secoes-da-gestao">Seções</button>
  <div class="secoes-da-gestao" id="secoes-da-gestao" popover="">
    <button type="button" class="fechar-secoes" popovertarget="secoes-da-gestao" popovertargetaction="hide">Fechar</button>
    <nav aria-label="Seções da gestão">
      <p class="grupo-de-secoes" id="grupo-de-secoes-1">Trabalho</p>
      <ul aria-labelledby="grupo-de-secoes-1">
        <li><a href="/" aria-current="true"><svg class="icone-da-secao" aria-hidden="true"><use href="#i-pasta"></use></svg><span class="rotulo-da-secao">Processos Seletivos</span></a></li>
        <li><a href="/"><svg class="icone-da-secao" aria-hidden="true"><use href="#i-prancheta"></use></svg><span class="rotulo-da-secao">Minhas Etapas</span></a></li>
        <li><a href="/"><svg class="icone-da-secao" aria-hidden="true"><use href="#i-calendario"></use></svg><span class="rotulo-da-secao">Agenda</span></a></li>
      </ul>
      <p class="grupo-de-secoes" id="grupo-de-secoes-2">Ajuda</p>
      <ul aria-labelledby="grupo-de-secoes-2">
        <li><a href="/"><svg class="icone-da-secao" aria-hidden="true"><use href="#i-livro"></use></svg><span class="rotulo-da-secao">Documentação do Sistema</span></a></li>
      </ul>
    </nav>
    <div class="pessoa-identificada">
      <span class="iniciais" aria-hidden="true">PC</span>
      <span class="nome-da-pessoa"><strong>Presidência da comissão</strong></span>
    </div>
    <button type="button" class="alternar-barra" data-alternar-barra=""><svg class="icone-da-secao" aria-hidden="true"><use href="#i-painel"></use></svg><span class="rotulo-da-secao" data-rotulo="">Recolher a barra lateral</span></button>
  </div>
</div>
<div class="area-de-trabalho">
<header class="cabecalho-de-contexto">
  <nav aria-label="Trilha de navegação" class="caminho-da-secao"><abbr title="Gestão de Processos Seletivos">GPS</abbr> › {trilha}</nav>
</header>
<main id="conteudo" tabindex="-1">
<p class="prototipo-faixa">Protótipo · nada aqui grava no GPS · <a href="/">roteiro</a> · <button type="button" class="acao" data-recomecar>Recomeçar</button></p>
{conteudo}
</main>
</div>
</div>
<script src="/static/prototipo/agenda.js"></script>
</body></html>"""

PORTAL = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} — Cefor/Ifes</title>
<link rel="stylesheet" href="/static/shared/tokens.css">
<link rel="stylesheet" href="/static/portal/portal.css">
<link rel="stylesheet" href="/static/prototipo/agenda-portal.css">
</head>
<body data-pagina="{pagina}">
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <span class="marca"><a href="/">Cefor/Ifes · <span class="nome-por-extenso">Gestão de Processos Seletivos</span></a></span>
  <nav class="acessos" aria-label="Acessos">{acessos}</nav>
</header>
<main id="conteudo" tabindex="-1">
<p class="prototipo-faixa">Protótipo · {trilha} · <a href="/">roteiro</a></p>
{conteudo}
</main>
<script src="/static/prototipo/agenda.js"></script>
</body></html>"""

CORREIO = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<link rel="stylesheet" href="/static/prototipo/agenda-correio.css">
</head>
<body data-pagina="{pagina}">
<p class="prototipo-faixa">Protótipo · {trilha} · <a href="/">roteiro</a></p>
{conteudo}
<script src="/static/prototipo/agenda.js"></script>
</body></html>"""

CABECALHO = re.compile(r"\A<!--(.*?)-->\s*", re.S)


def montar(nome: str) -> bytes | None:
    arquivo = PAGINAS / nome
    if not arquivo.is_file() or arquivo.suffix != ".html":
        return None
    texto = arquivo.read_text(encoding="utf-8")
    meta = {"titulo": nome, "trilha": "", "moldura": "gestao", "acessos": "", "folhas": ""}
    achado = CABECALHO.match(texto)
    if achado:
        for linha in achado.group(1).strip().splitlines():
            chave, _, valor = linha.partition(":")
            meta[chave.strip()] = valor.strip()
        texto = texto[achado.end() :]
    if meta["moldura"] == "indice":
        return texto.encode("utf-8")
    molde = {"gestao": GESTAO, "portal": PORTAL, "correio": CORREIO}[meta["moldura"]]
    folhas = "\n".join(
        f'<link rel="stylesheet" href="/static/interface/gestao/{f}.css">' for f in FOLHAS_DA_GESTAO
    )
    return molde.format(
        titulo=html.escape(meta["titulo"]),
        trilha=meta["trilha"],
        acessos=meta["acessos"],
        pagina=arquivo.stem,
        folhas=folhas,
        folhas_da_tela="\n".join(
            f'<link rel="stylesheet" href="/static/{f}">' for f in meta["folhas"].split()
        ),
        simbolos=SIMBOLOS,
        conteudo=texto,
    ).encode("utf-8")


class Manipulador(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def translate_path(self, path):
        caminho = path.split("?", 1)[0].split("#", 1)[0]
        for prefixo, raiz in ESTATICOS.items():
            if caminho.startswith(prefixo):
                alvo = (raiz / caminho[len(prefixo) :]).resolve()
                if raiz.resolve() in alvo.parents:
                    return str(alvo)
                return str(raiz / "inexistente")
        return super().translate_path(path)

    def do_GET(self):
        caminho = self.path.split("?", 1)[0]
        if caminho == "/":
            caminho = "/index.html"
        if not caminho.startswith("/static/"):
            corpo = montar(caminho.lstrip("/"))
            if corpo is None:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return
        super().do_GET()

    def log_message(self, *args):
        pass


def servir(porta):
    return http.server.ThreadingHTTPServer(
        ("127.0.0.1", porta), functools.partial(Manipulador, directory=str(AQUI))
    )


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8166
    print(f"Protótipo em http://localhost:{porta}/")
    servir(porta).serve_forever()
