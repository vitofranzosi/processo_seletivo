"""Inventário visual da gestão: captura cada tela a 1280 e 375 px e mede o estouro horizontal.

Roda com o ambiente do backend (DB_NAME=ps_inventario_telas etc.). Sobe um servidor WSGI numa
thread deste processo, e o Chrome (Playwright, channel=chrome) navega contra ele.
"""

import json
import os
import sys
import threading
from pathlib import Path

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
sys.path.insert(0, os.getcwd())

import django  # noqa: E402

django.setup()

from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


class Quieto(WSGIRequestHandler):
    def log_message(self, *a):
        pass


PORTA = int(os.environ.get("PORTA", "8097"))
BASE = f"http://localhost:{PORTA}"
SAIDA = Path(sys.argv[1])
(SAIDA / "png").mkdir(parents=True, exist_ok=True)

servidor = ThreadedWSGIServer(("localhost", PORTA), Quieto)
servidor.set_app(StaticFilesHandler(get_wsgi_application()))
threading.Thread(target=servidor.serve_forever, daemon=True).start()

# --- objetos do seed ---------------------------------------------------------------------------
P = "6bb9dc91-75bd-48c1-9994-344cabc538d0"  # PS-DEMO-2026, ATIVO
P27 = "214d989f-3a43-4c89-9427-3e633623ebb8"  # PS-DEMO-2026-R, EM_ELABORACAO
E51 = "af86be76-27f3-4e6a-b621-2b0771c323b2"  # 51/2026, publicado, seleção concluída
E26 = "bd6e4985-c88c-4b8f-a04d-ea380376d781"  # 26/2026, sorteio
E01 = "ec6018d1-6970-4bfb-8697-350922669a20"  # 01/2026, retificado
E76 = "2c4491c3-68f1-4d17-aa05-5c1cf6a1567b"  # 76/2027, em elaboração
ETAPA = "00000000-0000-0000-0051-0000000000d1"
M51 = "00000000-0000-0000-0051-0000000000a1"
M26 = "00000000-0000-0000-0026-0000000000a1"
ATO51 = "ac2080d5-e5a7-47ac-b251-246e03fbde81"
ATO26 = "f38ca7e9-1b65-46bc-8487-07edb00e1f47"
CORTE = "47f4cc31-35d4-440a-9a9c-2c1db924fd97"
INSC = "3cd5294d-bbf6-4fbe-88fc-95c3a62b927b"  # Ana Silva, Edital 51
RET = "392c15f3-8d3d-4552-b5dc-b83a1ca84cae"  # Retificação publicada do 01
MODELO = "87c71c47-4017-4aed-b8fe-f29e379c3359"
REC_PENDENTE = "6539ef46-cee4-4d45-b9f8-8fe605b312ac"
REC_ADMITIDO = "c7b47be9-fdcd-488d-8e3d-fe6be445072e"

IDENTIDADES = {
    "gustavo.gestor": ["gestor"],
    "ana.elaboradora": ["elaborador"],
    "bruno.homologador": ["homologador"],
    "paula.publicadora": ["publicador"],
    "paulo.presidente": [],
    "joana.avaliadora": [],
    "inventario.auditora": ["auditor"],
    "inventario.julgadora": ["julgador"],
    "inventario.exportadora": ["exportador"],
    "inventario.piloto": ["gestor", "participante-piloto-assistente"],
}
ORDEM = list(IDENTIDADES)

# (id, nome da rota, caminho, identidade preferida, observação)
EDT = f"/gestao/editais/{E51}"
MRC = f"{EDT}/marcos/{M51}"
DST = f"{EDT}/distribuicao/{ETAPA}"
ROTAS_A = [
    ("lista", "lista", "/gestao/", "gustavo.gestor", ""),
    ("identificar", "identificar", "/gestao/identificar", None, "sem identidade"),
    ("identificar-demonstracao", "identificar-demonstracao", "/gestao/identificar/demonstracao", None, "sem identidade; etapa da página de acesso (075)"),
    ("visao-geral", "visao-geral", "/gestao/visao-geral", "gustavo.gestor", ""),
    ("autoridades", "autoridades", "/gestao/autoridades", "gustavo.gestor", ""),
    ("processo-criar", "processo-criar", "/gestao/processos/criar", "gustavo.gestor", ""),
    ("processo-detalhe", "processo-detalhe", f"/gestao/processos/{P}/", "gustavo.gestor", ""),
    ("edital-criar", "edital-criar", f"/gestao/processos/{P}/editais/criar", "gustavo.gestor", ""),
    ("processo-ato-ativar", "processo-ato", f"/gestao/processos/{P27}/atos/ativar", "gustavo.gestor", "acao=ativar, Processo 2027"),
    ("processo-ato-encerrar", "processo-ato", f"/gestao/processos/{P}/atos/encerrar", "gustavo.gestor", "acao=encerrar"),
    ("processo-ato-cancelar", "processo-ato", f"/gestao/processos/{P}/atos/cancelar", "gustavo.gestor", "acao=cancelar"),
    ("supervisao", "supervisao", f"/gestao/processos/{P}/supervisao", "gustavo.gestor", ""),
    ("detalhe-51", "detalhe", f"{EDT}/", "gustavo.gestor", "Edital 51, publicado"),
    ("detalhe-76", "detalhe", f"/gestao/editais/{E76}/", "ana.elaboradora", "Edital 76, em elaboração"),
    ("detalhe-26", "detalhe", f"/gestao/editais/{E26}/", "gustavo.gestor", "Edital 26, sorteio"),
    ("duvidas", "duvidas", f"/gestao/editais/{E01}/duvidas/", "gustavo.gestor", "Edital 01"),
    ("assistente", "assistente", f"/gestao/editais/{E01}/assistente/", "inventario.piloto", "Edital 01"),
    ("assistente-prototipo", "assistente-prototipo", f"/gestao/editais/{E01}/assistente/prototipo/", "inventario.piloto", "Edital 01"),
    ("compor", "compor", f"/gestao/editais/{E76}/compor", "ana.elaboradora", "Edital 76"),
]
for etapa in ["identificacao", "perfis", "cronograma", "etapas", "classificacao", "inscricao",
              "anexos", "conteudo", "revisao"]:
    ROTAS_A.append((f"compor-{etapa}", "compor-etapa", f"/gestao/editais/{E76}/compor/{etapa}",
                    "ana.elaboradora", f"etapa={etapa}, Edital 76"))
ROTAS_A += [
    ("reaproveitar", "reaproveitar", f"/gestao/editais/{E76}/reaproveitar", "ana.elaboradora", "Edital 76"),
    ("previa", "previa", f"/gestao/editais/{E76}/previa", "ana.elaboradora", "Edital 76"),
    ("ato-submeter", "ato", f"/gestao/editais/{E76}/atos/submeter", "ana.elaboradora", "acao=submeter, Edital 76"),
    ("ato-homologar", "ato", f"/gestao/editais/{E76}/atos/homologar", "bruno.homologador", "acao=homologar, Edital 76"),
    ("ato-devolver", "ato", f"/gestao/editais/{E76}/atos/devolver", "bruno.homologador", "acao=devolver, Edital 76"),
    ("ato-revogar-homologacao", "ato", f"/gestao/editais/{E76}/atos/revogar-homologacao", "bruno.homologador", "acao=revogar-homologacao, Edital 76"),
    ("ato-publicar", "ato", f"/gestao/editais/{E76}/atos/publicar", "paula.publicadora", "acao=publicar, Edital 76"),
    ("ato-encerrar", "ato", f"{EDT}/atos/encerrar", "gustavo.gestor", "acao=encerrar, Edital 51"),
    ("ato-cancelar", "ato", f"{EDT}/atos/cancelar", "gustavo.gestor", "acao=cancelar, Edital 51"),
    ("retificar", "retificar", f"/gestao/editais/{E01}/retificar", "ana.elaboradora", "Edital 01"),
    ("auditoria", "auditoria", f"{EDT}/auditoria", "inventario.auditora", ""),
    ("exportar-matriculas", "exportar-matriculas", f"{EDT}/matriculas", "inventario.exportadora", ""),
    ("inscricoes", "inscricoes", f"{EDT}/inscricoes", "gustavo.gestor", ""),
    ("inscricao-recebida", "inscricao-recebida", f"/gestao/inscricoes/{INSC}/", "gustavo.gestor", "Ana Silva"),
    ("retificacao-detalhe", "retificacao-detalhe", f"/gestao/retificacoes/{RET}/", "ana.elaboradora", "Retificação publicada"),
]
for acao, quem in [("submeter", "ana.elaboradora"), ("homologar", "bruno.homologador"),
                   ("publicar", "paula.publicadora"), ("devolver", "bruno.homologador"),
                   ("cancelar", "gustavo.gestor")]:
    ROTAS_A.append((f"retificacao-ato-{acao}", "retificacao-ato",
                    f"/gestao/retificacoes/{RET}/atos/{acao}", quem, f"acao={acao}, Retificação publicada"))
ROTAS_A += [
    ("comissao", "comissao", f"/gestao/processos/{P}/comissao", "gustavo.gestor", ""),
    ("alocacoes", "alocacoes", f"/gestao/processos/{P}/alocacoes", "gustavo.gestor", ""),
    ("auditoria-comissao", "auditoria-comissao", f"/gestao/processos/{P}/auditoria", "inventario.auditora", ""),
    ("distribuicao", "distribuicao", DST, "paulo.presidente", "Prova objetiva, Edital 51"),
    ("registrar-ocorrencia", "registrar-ocorrencia", f"{DST}/ocorrencia", "paulo.presidente", ""),
    ("impedimentos", "impedimentos", f"{DST}/impedimentos", "paulo.presidente", ""),
    ("trilha-da-avaliacao", "trilha-da-avaliacao", f"{DST}/trilha", "paulo.presidente", ""),
    ("resultados-da-etapa", "resultados-da-etapa", f"{DST}/resultados", "paulo.presidente", ""),
    ("conclusoes-preservadas", "conclusoes-preservadas", f"{DST}/conclusoes", "paulo.presidente", ""),
    ("ordenacao", "ordenacao", MRC, "paulo.presidente", "marco FINAL, Edital 51"),
    ("corte-historico", "corte-historico", f"{EDT}/cortes/{CORTE}", "paulo.presidente", ""),
    ("ato-de-ordenacao", "ato-de-ordenacao", f"{MRC}/atos/{ATO51}", "paulo.presidente", ""),
    ("corte", "corte", f"{MRC}/corte", "paulo.presidente", ""),
    ("ocupacao", "ocupacao", f"{MRC}/ocupacao", "paulo.presidente", ""),
    ("ocupacao-historico", "ocupacao-historico", f"{MRC}/ocupacao/historico", "paulo.presidente", ""),
    ("convocacao", "convocacao", f"{MRC}/convocacao", "paulo.presidente", ""),
    ("convocacao-historico", "convocacao-historico", f"{MRC}/convocacao/historico", "paulo.presidente", ""),
    ("sorteio", "sorteio", f"/gestao/editais/{E26}/marcos/{M26}/sorteio", "paulo.presidente", "Edital 26"),
    ("previa-de-publicacao", "previa-de-publicacao", f"{MRC}/atos/{ATO51}/publicar", "paula.publicadora", ""),
    ("publicacoes-do-marco", "publicacoes-do-marco", f"{MRC}/publicacoes", "paula.publicadora", ""),
    ("marco", "marco", f"{MRC}/conducao", "paulo.presidente", "condução do marco"),
    ("recursos", "recursos", f"{EDT}/recursos", "inventario.julgadora", ""),
    ("recurso-pendente", "recurso", f"/gestao/recursos/{REC_PENDENTE}", "inventario.julgadora", "recurso aguardando admissibilidade (criado para o inventário)"),
    ("recurso-admitido", "recurso", f"/gestao/recursos/{REC_ADMITIDO}", "inventario.julgadora", "recurso admitido (criado para o inventário)"),
    ("minhas-etapas", "minhas-etapas", "/gestao/minhas-etapas", "joana.avaliadora", ""),
    ("minha-etapa", "minha-etapa", f"/gestao/minhas-etapas/{E51}/{ETAPA}", "joana.avaliadora", ""),
    ("mesa-inscricao", "mesa-inscricao", f"/gestao/minhas-etapas/{E51}/{ETAPA}/inscricoes/{INSC}", "joana.avaliadora", ""),
    ("modelos-de-aviso", "modelos-de-aviso", "/gestao/modelos-de-aviso", "gustavo.gestor", ""),
    ("modelo-de-aviso-novo", "modelo-de-aviso-novo", "/gestao/modelos-de-aviso/novo", "gustavo.gestor", ""),
    ("modelo-de-aviso", "modelo-de-aviso", f"/gestao/modelos-de-aviso/{MODELO}", "gustavo.gestor", ""),
    ("avisos-do-edital-antes", "avisos-do-edital", f"{EDT}/avisos", "gustavo.gestor", "antes de qualquer aviso"),
    ("aviso-da-chamada", "aviso-da-chamada", f"{MRC}/convocacao/avisos/novo", "gustavo.gestor", ""),
    ("aviso-do-resultado", "aviso-do-resultado", f"{MRC}/avisos/novo", "gustavo.gestor", ""),
]

MEDIR = r"""() => {
  const de = document.documentElement, cw = de.clientWidth;
  const culpados = [];
  const rolam = (el) => { const s = getComputedStyle(el).overflowX; return s === 'auto' || s === 'scroll' || s === 'hidden' || s === 'clip'; };
  for (const el of document.body.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.right <= cw + 1) continue;
    let contido = false;
    for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
      if (rolam(a) && a.getBoundingClientRect().right <= cw + 1) { contido = true; break; }
    }
    if (contido) continue;
    // só o mais externo: o pai também estoura? então o filho é consequência
    const p = el.parentElement, pr = p && p !== document.body ? p.getBoundingClientRect() : null;
    if (pr && pr.right > cw + 1) continue;
    let nome = el.tagName.toLowerCase();
    if (el.id) nome += '#' + el.id;
    if (el.classList.length) nome += '.' + [...el.classList].slice(0, 2).join('.');
    culpados.push(nome + ' (' + Math.round(r.right) + 'px)');
  }
  return {scrollWidth: de.scrollWidth, clientWidth: cw, altura: de.scrollHeight,
          titulo: document.title, h1: (document.querySelector('h1')||{}).textContent?.trim().slice(0,120) || '',
          culpados: culpados.slice(0, 6)};
}"""


def contexto_para(browser, quem):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
    # A preferência da barra retrátil da 076 mora no armazenamento do navegador. `BARRA=recolhida`
    # (ou `expandida`) a grava antes de cada página, como se a pessoa já a tivesse escolhido; sem a
    # variável, vale o padrão de quem chega pela primeira vez.
    barra = os.environ.get("BARRA")
    if barra:
        ctx.add_init_script(f"try {{ localStorage.setItem('gps.barra', '{barra}') }} catch (e) {{}}")
    if quem is None:
        return ctx
    pg = ctx.new_page()
    # Desde a 075 o formulário mora na etapa da demonstração, e a página de acesso não emite o
    # cookie de CSRF. O envio continua indo a `identificar`.
    pg.goto(f"{BASE}/gestao/identificar/demonstracao")
    token = next(c["value"] for c in ctx.cookies() if c["name"] == "csrftoken")
    from urllib.parse import urlencode

    pares = [("csrfmiddlewaretoken", token), ("identidade_sugerida", quem)]
    pares += [("papeis", p) for p in IDENTIDADES[quem]]
    r = ctx.request.post(f"{BASE}/gestao/identificar", data=urlencode(pares),
                         headers={"Content-Type": "application/x-www-form-urlencoded",
                                  "X-CSRFToken": token, "Referer": f"{BASE}/gestao/identificar"})
    assert r.ok, (quem, r.status)
    pg.close()
    return ctx


def abrir(ctx, caminho):
    pg = ctx.new_page()
    resp = pg.goto(BASE + caminho, wait_until="load")
    final = pg.url.replace(BASE, "")
    tipo = resp.headers.get("content-type", "") if resp else ""
    return pg, (resp.status if resp else 0), final, tipo


def tentar(browser, contextos, caminho, preferida):
    ordem = [preferida] + [q for q in ORDEM if q != preferida] if preferida else [None]
    tentativas = []
    for quem in ordem:
        if quem not in contextos:
            contextos[quem] = contexto_para(browser, quem)
        pg, status, final, tipo = abrir(contextos[quem], caminho)
        ok = status == 200 and "text/html" in tipo and (
            quem is None or not final.startswith("/gestao/identificar"))
        tentativas.append(f"{quem}:{status}")
        if ok:
            return quem, pg, status, final, tipo, tentativas
        pg.close()
    return None, None, status, final, tipo, tentativas


# `ESTILOS=1` (089) acrescenta o resumo das regras que a página aplica (ver `estilos.py`).
sys.path.insert(0, str(Path(__file__).parent))
from estilos import ESTILOS  # noqa: E402


def capturar(rid, pg, largura, altura):
    pg.set_viewport_size({"width": largura, "height": altura})
    pg.wait_for_timeout(150)
    m = pg.evaluate(MEDIR)
    if os.environ.get("ESTILOS"):
        m["estilos"] = pg.evaluate(ESTILOS)
    arquivo = SAIDA / "png" / f"{rid}--{largura}.png"
    pg.screenshot(path=str(arquivo), full_page=True)
    m["arquivo"] = arquivo.name
    return m


def rodar(rotas, browser, contextos, resultados):
    for rid, nome, caminho, preferida, obs in rotas:
        quem, pg, status, final, tipo, tentativas = tentar(browser, contextos, caminho, preferida)
        linha = {"id": rid, "rota": nome, "caminho": caminho, "obs": obs, "identidade": quem,
                 "status": status, "final": final, "tipo": tipo, "tentativas": tentativas}
        if pg is not None:
            linha["1280"] = capturar(rid, pg, 1280, 900)
            linha["375"] = capturar(rid, pg, 375, 812)
            pg.close()
        resultados.append(linha)
        print(rid, quem, status, linha.get("375", {}).get("scrollWidth"), flush=True)


def criar_aviso(contextos):
    """Confirma o aviso de resultado pela tela, como o gestor faria, e devolve o id do aviso."""
    pg = contextos["gustavo.gestor"].new_page()
    pg.goto(f"{BASE}{MRC}/avisos/novo")
    pg.locator("button[name=acao][value=confirmar]").first.click()
    pg.wait_for_load_state("load")
    url = pg.url
    pg.close()
    return url.rstrip("/").split("/")[-1] if "/gestao/avisos/" in url else None


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    contextos = {}
    resultados = []
    so = set(filter(None, os.environ.get("SO", "").split(",")))
    if so:
        rodar([r for r in ROTAS_A if r[0] in so], browser, contextos, resultados)
        anteriores = json.loads((SAIDA / "resultados.json").read_text())
        novos = {l["id"]: l for l in resultados}
        resultados = [novos.get(l["id"], l) for l in anteriores]
        browser.close()
        (SAIDA / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
        servidor.shutdown()
        sys.exit(0)
    rodar(ROTAS_A, browser, contextos, resultados)
    # Reusar o aviso de uma passada anterior, em vez de confirmar outro: um segundo aviso mudaria a
    # tela `avisos-do-edital` entre o antes e o depois, e a diferença não seria do shell.
    aviso_id = os.environ.get("AVISO") or criar_aviso(contextos)
    print("aviso criado:", aviso_id, flush=True)
    if aviso_id:
        rodar([
            ("aviso", "aviso", f"/gestao/avisos/{aviso_id}", "gustavo.gestor", "aviso de resultado confirmado para o inventário"),
            ("aviso-interromper", "aviso-interromper", f"/gestao/avisos/{aviso_id}/interromper", "gustavo.gestor", ""),
            ("aviso-reenviar", "aviso-reenviar", f"/gestao/avisos/{aviso_id}/reenviar", "gustavo.gestor", ""),
            ("avisos-do-edital", "avisos-do-edital", f"{EDT}/avisos", "gustavo.gestor", "depois do aviso"),
        ], browser, contextos, resultados)
    browser.close()

(SAIDA / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
servidor.shutdown()
