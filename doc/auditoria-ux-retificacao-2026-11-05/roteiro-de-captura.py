"""Roteiro de captura da auditoria de UX da Retificação (05/11/2026). Não é teste da suíte.

Percorre os cenários A–G sobre o Edital 01/2026 do `seed_demo`, num servidor local já no ar, e
grava capturas e medidas em `UX_SAIDA`. Cada passo que uma pessoa faria (clique, digitação,
envio) conta uma ação em `acoes`; é medida do roteiro automatizado, não de pessoa real.

Preparação usada em 05/11 (banco isolado, nunca o de quem desenvolve):

    createdb -h localhost ps_retif_ux
    make preparar DB_NAME=ps_retif_ux ... (ver o README desta pasta)
    manage.py seed_demo
    runserver 8135 com INTERFACE_SELETOR_IDENTIDADE=true

Rodar, do `backend/`, com o grupo `navegador`:

    UX_BASE=http://localhost:8135 UX_SAIDA=<pasta> uv run python \
        ../doc/auditoria-ux-retificacao-2026-11-05/roteiro-de-captura.py

O roteiro **cria e submete** Retificações: rode-o uma vez por banco recém-semeado.
"""

import json
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UX_BASE", "http://localhost:8135")
SAIDA = Path(os.environ.get("UX_SAIDA", "/tmp/ux-retificacao"))
EDITAL = os.environ.get("UX_EDITAL", "0b0173ac-9992-4e27-aad0-50e19c459f37")
SAIDA.mkdir(parents=True, exist_ok=True)

MEDIR = """() => {
  const q = s => [...document.querySelectorAll(s)];
  const main = document.querySelector('main') || document.body;
  return {
    url: location.pathname + location.search,
    altura: document.documentElement.scrollHeight,
    largura: document.documentElement.scrollWidth,
    janela: window.innerHeight,
    rolagem: window.scrollY,
    cartoes: q('fieldset[data-linha]').length,
    campos: q('#formulario-da-retificacao [name^="campo:"]').length,
    linhas_do_resumo: q('.consequencias tbody tr').length,
    texto: main.innerText.slice(0, 6000),
  };
}"""

medidas = {}


class Roteiro:
    def __init__(self, pagina, nome):
        self.p = pagina
        self.nome = nome
        self.acoes = 0
        self.passos = []

    def passo(self, descricao):
        self.acoes += 1
        self.passos.append(f"{self.acoes}. {descricao}")

    def captura(self, rotulo, *, inteira=False, alvo=None):
        arquivo = SAIDA / f"{rotulo}.jpg"
        if alvo is not None:
            alvo.screenshot(path=arquivo, type="jpeg", quality=70)
        else:
            self.p.screenshot(path=arquivo, full_page=inteira, type="jpeg", quality=70)
        medidas.setdefault(self.nome, {}).setdefault("capturas", {})[rotulo] = self.p.evaluate(
            MEDIR
        )

    def fechar(self):
        medidas.setdefault(self.nome, {}).update(acoes=self.acoes, passos=self.passos)


def entrar(contexto, identidade):
    pagina = contexto.new_page()
    pagina.goto(f"{BASE}/gestao/identificar/demonstracao")
    pagina.locator(f'button[name="identidade_sugerida"][value="{identidade}"]').click()
    pagina.wait_for_load_state()
    return pagina


def cartao(pagina, trecho):
    return pagina.locator(f'fieldset[data-linha][data-nome*="{trecho}"]').first


def campo(pagina, trecho_do_cartao, rotulo):
    return cartao(pagina, trecho_do_cartao).get_by_label(rotulo, exact=True)


def ver_o_que_vai_mudar(r):
    r.passo("clica em «Ver o que vai mudar» (barra fixa)")
    r.p.get_by_role("button", name="Ver o que vai mudar").click()
    r.p.wait_for_load_state()


def principal():
    with sync_playwright() as pw:
        navegador = pw.chromium.launch()
        desktop = navegador.new_context(viewport={"width": 1280, "height": 900}, locale="pt-BR")
        ana = entrar(desktop, "ana.elaboradora")

        # ── 1. Entrada: do detalhe do Edital até a tela Retificar ───────────────────────────
        r = Roteiro(ana, "entrada")
        ana.goto(f"{BASE}/gestao/editais/{EDITAL}/")
        r.captura("01-detalhe-do-edital")
        r.captura("01b-detalhe-do-edital-inteiro", inteira=True)
        r.passo("clica em «Retificar» no detalhe do Edital")
        ana.get_by_role("link", name=re.compile(r"^Retificar")).first.click()
        ana.wait_for_load_state()
        r.captura("02-retificar-primeira-dobra")
        r.captura("03-retificar-pagina-inteira", inteira=True)
        r.fechar()

        # ── A. Prorrogar o término das inscrições ───────────────────────────────────────────
        r = Roteiro(ana, "A-cronograma")
        r.passo("clica em «Cronograma» no índice «Ir para»")
        ana.locator("nav.indice").get_by_role("link", name=re.compile("Cronograma")).click()
        r.captura("A1-cronograma-pelo-indice")
        termino = campo(ana, "Inscrições", "Término")
        medidas["A-cronograma"] = {"termino_mostrado": termino.input_value()}
        r.passo("altera «Término» do Evento 1 — Inscrições")
        termino.fill("2026-12-12T23:59")
        r.captura("A2-campo-alterado-com-selo", alvo=cartao(ana, "Inscrições"))
        ver_o_que_vai_mudar(r)
        r.captura("A3-conferencia-o-que-vai-mudar")
        r.passo("preenche a Justificativa (no fim da página)")
        ana.locator("#justificativa").fill("Prorrogação do período de inscrições.")
        r.passo("clica em «Criar Retificação»")
        ana.get_by_role("button", name=re.compile("^Criar Retificação")).click()
        ana.wait_for_load_state()
        r.captura("A4-detalhe-da-retificacao-criada", inteira=True)
        url_a = ana.url
        r.fechar()

        # ── B. Vagas de um Perfil ───────────────────────────────────────────────────────────
        r = Roteiro(ana, "B-vagas")
        ana.goto(f"{BASE}/gestao/editais/{EDITAL}/retificar")
        r.captura("B0-retificar-com-retificacao-em-curso")
        r.passo("digita «vagas» em «Encontrar»")
        ana.locator("#filtro-da-retificacao").fill("vagas")
        r.captura("B1-encontrar-vagas")
        medidas["B-vagas"] = {"encontrar_vagas": ana.locator(".achados").inner_text()}
        ana.locator("#filtro-da-retificacao").fill("")
        r.passo("clica em «Perfis de Vaga» no índice")
        ana.locator("nav.indice").get_by_role("link", name=re.compile("Perfis de Vaga")).click()
        r.passo("rola até o Perfil DOC-INFO e altera «Vagas imediatas» de 3 para 4")
        campo(ana, "Professor de Informática", "Vagas imediatas").fill("4")
        r.captura("B2-perfil-alterado", alvo=cartao(ana, "Professor de Informática"))
        ver_o_que_vai_mudar(r)
        r.captura("B3-conferencia-vagas-sem-quadro")
        r.passo("altera também a linha «Ampla concorrência — DOC-INFO» do quadro")
        campo(ana, "Linha do quadro Ampla concorrência — DOC-INFO", "Vagas imediatas").fill("3")
        ver_o_que_vai_mudar(r)
        r.captura("B4-conferencia-vagas-com-quadro")
        r.fechar()

        # ── C. Requisito de participação e documento exigido ───────────────────────────────
        r = Roteiro(ana, "C-requisitos")
        ana.goto(f"{BASE}/gestao/editais/{EDITAL}/retificar")
        r.passo("digita «requisito» em «Encontrar»")
        ana.locator("#filtro-da-retificacao").fill("requisito")
        medidas["C-requisitos"] = {"encontrar_requisito": ana.locator(".achados").inner_text()}
        r.captura("C1-encontrar-requisito")
        ana.locator("#filtro-da-retificacao").fill("Técnico de Laboratório")
        r.passo("digita «Técnico de Laboratório» em «Encontrar»")
        r.captura("C2-encontrar-o-perfil")
        req = campo(ana, "Técnico de Laboratório", "Requisitos de participação")
        r.passo("acrescenta uma linha a «Requisitos de participação»")
        req.fill(req.input_value() + "\nExperiência mínima de 6 meses em laboratório.")
        ana.locator("#filtro-da-retificacao").fill("Diploma")
        r.passo("digita «Diploma» em «Encontrar»")
        r.captura("C3-documento-exigido", alvo=cartao(ana, "Diploma"))
        ver_o_que_vai_mudar(r)
        r.captura("C4-conferencia-requisitos")
        r.fechar()

        # ── D. Retificação múltipla, em seções distintas ────────────────────────────────────
        r = Roteiro(ana, "D-multipla")
        ana.goto(f"{BASE}/gestao/editais/{EDITAL}/retificar")
        r.passo("altera o Local da Prova objetiva (Cronograma)")
        campo(ana, "Prova objetiva", "Local").first.fill("Campus Serra, bloco B")
        r.passo("altera a Remuneração do Perfil TEC-LAB")
        campo(ana, "Técnico de Laboratório", "Remuneração").fill("R$ 3.200,00")
        r.passo("altera o Prazo em dias do recurso do Marco FINAL")
        campo(ana, "Marco FINAL", "Prazo em dias").fill("3")
        r.passo("liga «Só o que eu alterei»")
        ana.locator("#so-alteradas").check()
        r.captura("D1-so-o-que-eu-alterei", inteira=True)
        ver_o_que_vai_mudar(r)
        r.captura("D2-conferencia-multipla")
        medidas["D-multipla"] = {
            "depois_da_conferencia_contagem": ana.locator(".barra-de-acoes .contagem").inner_text()
        }
        r.captura("D3-barra-depois-da-conferencia", alvo=ana.locator(".barra-de-acoes"))
        r.fechar()

        # ── G. Sucessivas: o que a tela chama de «vigente» ─────────────────────────────────
        r = Roteiro(ana, "G-sucessivas")
        ana.goto(f"{BASE}/gestao/editais/{EDITAL}/")
        r.captura("G1-detalhe-do-edital-documentos", inteira=True)
        r.fechar()

        # ── Submeter a de A, e o homologador ────────────────────────────────────────────────
        r = Roteiro(ana, "F-submeter")
        ana.goto(url_a)
        r.passo("clica em «Submeter»")
        ana.get_by_role("link", name=re.compile("^Submeter")).first.click()
        ana.wait_for_load_state()
        r.captura("F0-confirmar-submeter", inteira=True)
        r.passo("confirma")
        ana.get_by_role("button", name=re.compile("^Confirmar")).click()
        ana.wait_for_load_state()
        r.captura("F1-detalhe-apos-submeter")
        r.fechar()

        bruno = entrar(
            desktop.browser.new_context(viewport={"width": 1280, "height": 900}, locale="pt-BR"),
            "bruno.homologador",
        )
        r = Roteiro(bruno, "F-homologar")
        r.captura("F2-inicio-do-homologador", inteira=True)
        bruno.goto(f"{BASE}/gestao/editais/{EDITAL}/")
        r.captura("F3-edital-visto-pelo-homologador", inteira=True)
        bruno.goto(url_a)
        r.captura("F4-detalhe-visto-pelo-homologador", inteira=True)
        r.passo("clica em «Homologar»")
        bruno.get_by_role("link", name=re.compile("^Homologar")).first.click()
        bruno.wait_for_load_state()
        r.captura("F5-confirmar-homologar", inteira=True)
        r.fechar()

        # ── Largura estreita ────────────────────────────────────────────────────────────────
        celular = navegador.new_context(
            viewport={"width": 375, "height": 812}, locale="pt-BR", is_mobile=True, has_touch=True
        )
        ana375 = entrar(celular, "ana.elaboradora")
        r = Roteiro(ana375, "375")
        ana375.goto(f"{BASE}/gestao/editais/{EDITAL}/retificar")
        r.captura("M1-retificar-375")
        r.captura("M2-retificar-375-inteira", inteira=True)
        r.fechar()

        navegador.close()
    (SAIDA / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    principal()
