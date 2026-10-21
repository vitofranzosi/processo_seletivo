"""A recusa da verificação anti-falsificação na moldura do sistema (093).

Os casos de `test_csrf.py` provam **que** a verificação recusa; estes provam **o que** a pessoa vê
quando ela recusa. Antes, era o `403_csrf.html` do framework: em inglês, com o estilo num `<style>`
que a política de segurança de conteúdo não deixa aplicar, e sem caminho de volta.
"""

import logging
import re
from html.parser import HTMLParser

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.checks.security.csrf import check_csrf_failure_view
from django.test import Client, RequestFactory
from django.urls import reverse

from processo_seletivo.interface.erros import falha_de_csrf
from processo_seletivo.shared.politica_de_conteudo import CABECALHO, POLITICA
from tests.fixtures.candidato import MARIA, identificar

pytestmark = pytest.mark.django_db

TITULO = "O formulário não pôde ser enviado"
TERMOS_TECNICOS = ("csrf", "token", "cookie", "referer")


class _TextoVisivel(HTMLParser):
    """O texto que a pessoa lê, sem atributos: o `csrfmiddlewaretoken` do "Sair" não é texto."""

    def __init__(self):
        super().__init__()
        self.partes = []
        self._oculto = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "title"):
            self._oculto += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "title"):
            self._oculto -= 1

    def handle_data(self, data):
        if not self._oculto:
            self.partes.append(data)


def texto_visivel(resposta):
    leitor = _TextoVisivel()
    leitor.feed(resposta.content.decode())
    return " ".join(" ".join(leitor.partes).split())


@pytest.fixture
def registro():
    """O que o logger do projeto escreve: ele não propaga até a raiz, e o `caplog` não o vê."""

    class Coletor(logging.Handler):
        def __init__(self):
            super().__init__(level=logging.DEBUG)
            self.mensagens = []

        def emit(self, record):
            self.mensagens.append(record.getMessage())

    coletor = Coletor()
    logger = logging.getLogger("processo_seletivo")
    logger.addHandler(coletor)
    try:
        yield coletor.mensagens
    finally:
        logger.removeHandler(coletor)


@pytest.fixture
def cliente_rigoroso():
    return Client(enforce_csrf_checks=True)


def _gestao(cliente, **cabecalhos):
    return cliente.post(
        reverse("interface:identificar"), {"subject": "alguem", "papeis": ["gestor"]}, **cabecalhos
    )


def _portal(cliente, **cabecalhos):
    return cliente.post(reverse("portal:acesso"), {"email": "m@ex.br"}, **cabecalhos)


AREAS = {
    "gestao": (_gestao, "interface/recusa.html", "interface/base.html"),
    "portal": (_portal, "portal/recusa.html", "portal/base.html"),
}


@pytest.mark.parametrize("area", AREAS)
def test_a_recusa_vem_na_moldura_da_area(cliente_rigoroso, seletor_ligado, area):
    """FR-2150, FR-2151, FR-2152: 403, a recusa da área, sobre a base da área."""
    enviar, recusa, base = AREAS[area]
    resposta = enviar(cliente_rigoroso)

    assert resposta.status_code == 403
    usados = [modelo.name for modelo in resposta.templates]
    assert recusa in usados
    assert base in usados
    assert "403_csrf.html" not in usados


@pytest.mark.parametrize("area", AREAS)
def test_a_mensagem_diz_o_que_aconteceu_e_o_que_fazer(cliente_rigoroso, seletor_ligado, area):
    """FR-2153: nada gravado, o motivo em palavras de quem lê, e o caminho — o mesmo texto."""
    texto = texto_visivel(AREAS[area][0](cliente_rigoroso))

    assert TITULO in texto
    assert "Nada foi gravado." in texto
    assert "O formulário expirou ou foi enviado de outra página" in texto
    assert "recarregue-a e envie de novo" in texto
    assert "copie antes o que quiser manter" in texto


@pytest.mark.parametrize("area", AREAS)
def test_o_motivo_vai_ao_registro_e_nao_a_pagina(cliente_rigoroso, seletor_ligado, registro, area):
    """FR-2154, FR-2155: a página sem termo técnico; o registro com o motivo e o endereço."""
    resposta = AREAS[area][0](cliente_rigoroso)

    texto = texto_visivel(resposta).lower()
    assert [termo for termo in TERMOS_TECNICOS if termo in texto] == []
    # O motivo que o framework dá quando o navegador não trouxe a prova.
    assert "CSRF cookie not set" not in resposta.content.decode()
    linhas = [linha for linha in registro if "verificação de CSRF" in linha]
    assert len(linhas) == 1
    assert "CSRF cookie not set" in linhas[0]
    assert resposta.wsgi_request.path in linhas[0]


@pytest.mark.parametrize("area", AREAS)
def test_sem_estilo_nem_script_embutido_e_sob_a_politica(cliente_rigoroso, seletor_ligado, area):
    """FR-2157, FR-2159: a página passa pela política em recusa, a mesma de toda página."""
    resposta = AREAS[area][0](cliente_rigoroso)
    corpo = resposta.content.decode()

    assert resposta[CABECALHO] == POLITICA
    assert "Content-Security-Policy-Report-Only" not in resposta
    assert "<style" not in corpo
    assert not re.search(r"\sstyle\s*=", corpo)
    assert not re.search(r"\son[a-z]+\s*=", corpo)
    # Todo `<script>` da página aponta para um arquivo: o que não tem `src` é embutido.
    scripts = re.findall(r"<script\b[^>]*>", corpo)
    assert all(" src=" in script for script in scripts), scripts
    assert 'rel="stylesheet"' in corpo


@pytest.mark.parametrize("area", AREAS)
def test_reabre_a_pagina_de_origem_quando_e_do_sistema(cliente_rigoroso, seletor_ligado, area):
    """FR-2156: a origem do próprio servidor vira link."""
    origem = "http://testserver/selecoes/acesso?destino=/selecoes/inscricoes/"
    resposta = AREAS[area][0](cliente_rigoroso, HTTP_REFERER=origem)

    assert resposta.context["reabrir"] == origem
    assert 'href="http://testserver/selecoes/acesso?destino=/selecoes/inscricoes/"' in (
        resposta.content.decode()
    )


@pytest.mark.parametrize("origem", ["https://outro.example/forjado", "", "javascript:alert(1)"])
@pytest.mark.parametrize("area", AREAS)
def test_nunca_oferece_link_para_fora(cliente_rigoroso, seletor_ligado, area, origem):
    """FR-2156, D-005: numa falsificação de fato, a origem é o site de quem a montou."""
    cabecalhos = {"HTTP_REFERER": origem} if origem else {}
    resposta = AREAS[area][0](cliente_rigoroso, **cabecalhos)

    assert resposta.status_code == 403
    assert resposta.context["reabrir"] == ""
    corpo = resposta.content.decode()
    assert "Reabrir a tela" not in corpo
    assert "Abrir a página do formulário" not in corpo
    if origem:
        assert origem not in corpo


@pytest.mark.parametrize("area", AREAS)
def test_a_mesma_pagina_com_a_depuracao_ligada(cliente_rigoroso, seletor_ligado, settings, area):
    """FR-2160, D-003: o runserver mostra o que a produção mostra; e sob a política, sem escapar."""
    settings.DEBUG = True
    enviar, recusa, _ = AREAS[area]
    resposta = enviar(cliente_rigoroso)

    assert resposta.status_code == 403
    assert recusa in [modelo.name for modelo in resposta.templates]
    assert resposta[CABECALHO] == POLITICA


def test_fora_das_duas_areas_a_moldura_e_a_do_portal(seletor_ligado):
    """FR-2151, D-002: nenhum formulário fica fora delas hoje; se um vier, a moldura é a pública."""
    pedido = RequestFactory().post("/um-formulario-futuro")
    SessionMiddleware(lambda pedido: None).process_request(pedido)

    resposta = falha_de_csrf(pedido, reason="CSRF cookie not set.")

    assert resposta.status_code == 403
    corpo = resposta.content.decode()
    assert TITULO in corpo
    assert "Voltar às seleções" in corpo
    assert "CSRF" not in corpo


def test_o_sair_da_pagina_de_recusa_funciona(cliente_rigoroso):
    """Edge case: o candidato com sessão vê o "Sair", e a prova que a página emite vale."""
    identificar(cliente_rigoroso, MARIA)
    recusa = cliente_rigoroso.post(reverse("portal:inscricoes"), {})
    assert recusa.status_code == 403
    assert "Sair" in texto_visivel(recusa)

    saida = cliente_rigoroso.post(
        reverse("portal:sair"), {"csrfmiddlewaretoken": str(recusa.context["csrf_token"])}
    )

    assert saida.status_code == 302
    assert "portal_identidade" not in cliente_rigoroso.session


def test_o_ajuste_do_framework_aponta_para_a_view_do_sistema(settings):
    """FR-2158: a troca é só de quem escreve a página; a verificação do framework a aceita."""
    assert settings.CSRF_FAILURE_VIEW == "processo_seletivo.interface.erros.falha_de_csrf"
    assert check_csrf_failure_view(None) == []
