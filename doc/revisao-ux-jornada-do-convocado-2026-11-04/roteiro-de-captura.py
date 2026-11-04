"""Roteiro de captura da revisão de UX da jornada do convocado (04/11/2026). Não é teste da suíte.

Monta os cenários A–K da revisão sobre as fixtures da 115 e da 059 e captura, a 375 px e em
desktop, as telas do candidato num Chromium. Grava o texto visível e medidas de posição em JSON.

Para reproduzir, copie para `backend/tests/navegador/` (é lá que as fixtures alcançam) e rode, com
o grupo `navegador` instalado:

    UX_SAIDA=<pasta> TEST_DB_ENGINE=postgresql DB_USER=$USER DB_RUNTIME_USER=$USER \
        DB_NAME=ps_ux115 uv run pytest tests/navegador/roteiro-de-captura.py -q

Apague a cópia depois: o arquivo não pertence à suíte.
"""

import json
import os
import time
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

from django.urls import reverse  # noqa: E402
from django.utils import timezone  # noqa: E402

from processo_seletivo.convocacao.domain import nomes  # noqa: E402
from tests.fixtures import documentos_da_convocacao as cenarios  # noqa: E402
from tests.fixtures.convocacao import montar_cenario_da_convocacao  # noqa: E402
from tests.fixtures.documentos_da_convocacao import (  # noqa: E402
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
)
from tests.navegador.test_jornada_dos_documentos_da_convocacao import CELULAR, DESKTOP, Tela  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

SAIDA = Path(os.environ.get("UX_SAIDA", "/tmp/ux115"))

MEDIR = """() => {
  const main = document.querySelector('main') || document.body;
  const pos = (sel) => { const e = document.querySelector(sel); return e ? Math.round(e.getBoundingClientRect().top + window.scrollY) : null; };
  return {
    texto: main.innerText,
    altura: document.documentElement.scrollHeight,
    largura: document.documentElement.scrollWidth,
    y_documentos: pos('#documentos-da-convocacao'),
    y_primeiro_item: pos('#documentos-da-convocacao li.requisito'),
    y_requerimento: pos("a[href*='requerimento']"),
    y_o_que_fazer: (() => { const h = [...document.querySelectorAll('h3,h2')].find(x => /O que fazer/.test(x.innerText)); return h ? Math.round(h.getBoundingClientRect().top + window.scrollY) : null; })(),
  };
}"""


@pytest.fixture
def tela(navegador, live_server, settings, request, raiz_de_arquivos):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()


def publicar_com_requerimento():
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    def publicar(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client, manager_headers, process_payload, draft=draft,
            antes_de_submeter=declarar("AT_CALL"),
        )

    return publicar


def certame(gestor, api_client, manager_headers, process_payload, *, prefixo, documentos=None,
            requerimento=False, documentos_da_inscricao=None):
    extras = {}
    if requerimento:
        extras["publicar"] = publicar_com_requerimento()
    if documentos is not None:
        extras["documentos"] = documentos
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo=prefixo,
        documentos_da_inscricao=documentos_da_inscricao, **extras,
    )


def enviar_requerimento(pessoa):
    from processo_seletivo.requerimentos.application import preencher
    from tests.fixtures.requerimento import campos_de_exemplo

    preencher.abrir_rascunho(inscricao=pessoa)
    preencher.gravar(inscricao=pessoa, dados=campos_de_exemplo(), expected_revision=None)
    versao = preencher._conteudo(pessoa)
    return preencher.enviar(
        identidade=cenarios.Titular(pessoa), inscricao=pessoa, versao_exibida_id=versao.id,
        declaracao_exibida=preencher.declaracao_publicada(versao.content), aceite=True,
    )


def percorrer(tela, pessoa, cenario, telas=("inscricoes", "acompanhamento", "convocacao")):
    destino = SAIDA / cenario
    destino.mkdir(parents=True, exist_ok=True)
    medidas = {}
    rotas = {
        "inscricoes": reverse("portal:inscricoes"),
        "acompanhamento": reverse("portal:acompanhamento", args=[pessoa.id]),
        "convocacao": reverse("portal:convocacao", args=[pessoa.id]),
        "requerimento": reverse("portal:requerimento", args=[pessoa.id]),
    }
    for nome_vp, vp in (("375", CELULAR), ("desktop", DESKTOP)):
        pagina = tela.candidato(pessoa, viewport=vp)
        for nome in telas:
            pagina.goto(tela.servidor.url + rotas[nome])
            pagina.wait_for_load_state()
            pagina.screenshot(path=str(destino / f"{nome}-{nome_vp}.png"), full_page=True)
            medidas[f"{nome}-{nome_vp}"] = pagina.evaluate(MEDIR)
    (destino / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=2))
    return medidas


def teclado(tela, pessoa, cenario, passos=40):
    """A ordem do Tab na tela da convocação a 375 px, e se o foco se vê."""
    pagina = tela.candidato(pessoa, viewport=CELULAR)
    pagina.goto(tela.servidor.url + reverse("portal:convocacao", args=[pessoa.id]))
    ordem = []
    for _ in range(passos):
        pagina.keyboard.press("Tab")
        ordem.append(pagina.evaluate("""() => { const e = document.activeElement; const s = getComputedStyle(e);
          return {tag: e.tagName, texto: (e.innerText || e.value || e.getAttribute('aria-label') || e.id || '').trim().slice(0, 60),
                  outline: s.outlineStyle + ' ' + s.outlineWidth, sombra: s.boxShadow.slice(0, 40),
                  visivel: e.offsetParent !== null || e.tagName === 'BODY'}; }"""))
    (SAIDA / cenario / "teclado.json").write_text(json.dumps(ordem, ensure_ascii=False, indent=2))
    pagina.screenshot(path=str(SAIDA / cenario / "teclado-375.png"), full_page=False)


def convocar(cenario, gestor, *, vencimento_em=None, comunicar=True, chave="c"):
    edital = cenario[0]
    kwargs = {}
    if vencimento_em is not None:
        kwargs["vencimento"] = timezone.now() + vencimento_em
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor, chave=f"convocar-{chave}-ux", **kwargs)
    if comunicar:
        cenarios.comunicar(edital, gestor, convocacao, chave=f"comunicar-{chave}-ux")
    return pessoa, convocacao


CINCO_DIAS = timezone.timedelta(days=5)


def test_a_documentos_sem_requerimento(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-a",
                documentos=cenarios.documentos_do_aluno())
    pessoa, _ = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="a")
    percorrer(tela, pessoa, "A")
    teclado(tela, pessoa, "A")


def test_b_requerimento_sem_documentos(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-b", requerimento=True)
    pessoa, _ = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="b")
    percorrer(tela, pessoa, "B", telas=("inscricoes", "acompanhamento", "convocacao", "requerimento"))


def test_c_ambos(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-c",
                documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, _ = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="c")
    percorrer(tela, pessoa, "C1-nada-enviado")
    # O caminho principal leva ao requerimento; a pessoa o envia e volta.
    enviar_requerimento(pessoa)
    percorrer(tela, pessoa, "C2-so-o-requerimento-enviado",
              telas=("inscricoes", "acompanhamento", "convocacao", "requerimento"))


def test_d_aproveitado_da_inscricao(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-d",
                documentos=cenarios.documentos_do_certificado(),
                documentos_da_inscricao=(IDENTIDADE, CERTIFICADO))
    pessoa, _ = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="d")
    percorrer(tela, pessoa, "D")


def test_e_enviado_aguardando(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-e",
                documentos=cenarios.documentos_do_aluno())
    pessoa, conv = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="e")
    for req in (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA):
        cenarios.apresentar(pessoa, conv, req, corpo=str(req).encode())
    percorrer(tela, pessoa, "E")


def test_f_pendente_prazo_em_curso(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-f",
                documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="f")
    for req in (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO):
        cenarios.apresentar(pessoa, conv, req, corpo=str(req).encode())
    cenarios.conferir(gestor, conv, CERTIDAO, "CONFORME", chave="f-c1-ux-conferencia")
    cenarios.conferir(gestor, conv, CERTIFICADO_DO_MEDIO, "CONFORME", chave="f-c2-ux-conferencia")
    cenarios.conferir(gestor, conv, HISTORICO, "PENDENTE", chave="f-c3-ux-conferencia",
                      motivo="Falta a página 2.")
    enviar_requerimento(pessoa)
    percorrer(tela, pessoa, "F")
    teclado(tela, pessoa, "F")


def test_g_pendente_prazo_vencido(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-g",
                documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, gestor, vencimento_em=timezone.timedelta(seconds=25), chave="g")
    cenarios.apresentar(pessoa, conv, HISTORICO, corpo=b"historico")
    cenarios.conferir(gestor, conv, HISTORICO, "PENDENTE", chave="g-c1-ux-conferencia",
                      motivo="Falta a página 2.")
    while timezone.now() < conv.vencimento + timezone.timedelta(seconds=1):
        time.sleep(1)
    percorrer(tela, pessoa, "G", telas=("inscricoes", "acompanhamento", "convocacao", "requerimento"))


def test_h_tudo_enviado_sem_decisao(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-h",
                documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="h")
    for n, req in enumerate((CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)):
        cenarios.apresentar(pessoa, conv, req, corpo=str(req).encode())
        cenarios.conferir(gestor, conv, req, "CONFORME", chave=f"h-c{n}-ux-conferencia")
    enviar_requerimento(pessoa)
    percorrer(tela, pessoa, "H")


def test_i_desfecho_registrado(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-i",
                documentos=cenarios.documentos_do_aluno(), requerimento=True)
    edital = c[0]
    pessoa, conv = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="i")
    for n, req in enumerate((CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)):
        cenarios.apresentar(pessoa, conv, req, corpo=str(req).encode())
        cenarios.conferir(gestor, conv, req, "CONFORME", chave=f"i-c{n}-ux-conferencia")
    enviar_requerimento(pessoa)
    cenarios.desfechar(edital, gestor, conv, nomes.ACEITE, chave="i-desfecho-ux-aceite",
                       fundamento="Documentação conferida e conforme.")
    percorrer(tela, pessoa, "I1-aceite")


def test_i2_indeferido_com_item_sem_envio(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-i2",
                documentos=cenarios.documentos_do_aluno())
    edital = c[0]
    pessoa, conv = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="i2")
    cenarios.apresentar(pessoa, conv, CERTIDAO, corpo=b"certidao")
    cenarios.apresentar(pessoa, conv, HISTORICO, corpo=b"historico")
    cenarios.conferir(gestor, conv, HISTORICO, "PENDENTE", chave="i2-c1-ux-conferencia",
                      motivo="Falta a página 2.")
    cenarios.desfechar(edital, gestor, conv, nomes.INDEFERIMENTO, chave="i2-desfecho-ux-indef",
                       fundamento="Documentação exigida na convocação não atendida.")
    percorrer(tela, pessoa, "I2-indeferido")


def test_j_pendencia_sem_envio(tela, gestor, api_client, manager_headers, process_payload):
    """A pendência registrada sobre item que nem chegou — o texto diz "outro arquivo"?"""
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-j",
                documentos=cenarios.documentos_do_aluno())
    pessoa, conv = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="j")
    cenarios.conferir(gestor, conv, RESIDENCIA, "PENDENTE", chave="j-c1-ux-conferencia",
                      motivo="Envie conta de água, luz ou telefone dos últimos 3 meses.")
    percorrer(tela, pessoa, "J-pendencia-sem-envio", telas=("convocacao",))


def test_k_prazo_nao_iniciado(tela, gestor, api_client, manager_headers, process_payload):
    c = certame(gestor, api_client, manager_headers, process_payload, prefixo="ux-k",
                documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, _ = convocar(c, gestor, vencimento_em=CINCO_DIAS, chave="k", comunicar=False)
    percorrer(tela, pessoa, "K-prazo-nao-iniciado", telas=("acompanhamento", "convocacao"))
