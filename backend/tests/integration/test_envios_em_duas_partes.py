"""As mensagens do acesso e da inscrição saem em duas partes, ao mesmo destinatário de antes.

A moldura nova não pode mudar quem recebe nem quantas mensagens saem: uma por gesto, um endereço só,
o texto puro como corpo e o HTML como alternativa.

**E toda mensagem do sistema se declara automática** (`Auto-Submitted`, RFC 3834): era só dos
avisos, e sem ele a resposta de férias de quem recebe o código volta para uma caixa que ninguém lê.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core import mail

from processo_seletivo.convocacao.application.comunicar import enviar_mensagem_de_convocacao
from processo_seletivo.convocacao.domain.mensagem import INICIAL, EscolhaDaMensagem
from processo_seletivo.identidade.application.mensagem import (
    avisar_mudanca_de_credencial,
    enviar_codigo,
)
from processo_seletivo.identidade.models import DesafioDeAcesso
from processo_seletivo.inscricoes.application.mensagem import enviar_comprovante

pytestmark = pytest.mark.django_db

COMPROVANTE = {
    "protocolo": "2026-0001-0001",
    "verificacao": "AAAA-BBBB",
    "selecao": "Especialização\nEdital 1/2026",
    "perfil": "Perfil A",
    "modalidade": "Ampla concorrência",
    "quando": "13/11/2026 às 10:00",
    "documentos": [{"requisito": "RG", "arquivo": "rg.pdf"}],
    "endereco": "http://testserver/selecoes/",
}


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.mark.parametrize(
    "enviar",
    [
        lambda: enviar_codigo(para="pessoa@exemplo.test", codigo="123456"),
        lambda: enviar_codigo(
            para="pessoa@exemplo.test",
            codigo="123456",
            finalidade=DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL,
        ),
        lambda: avisar_mudanca_de_credencial(
            para="pessoa@exemplo.test",
            endereco="outra@exemplo.test",
            acao="removido",
            atendimento="atendimento@exemplo.test",
        ),
        lambda: enviar_comprovante(para="pessoa@exemplo.test", dados=COMPROVANTE),
    ],
    ids=["codigo", "vinculo", "mudanca", "comprovante"],
)
def test_uma_mensagem_ao_mesmo_destinatario_com_texto_e_html(caixa, enviar):
    enviar()

    (mensagem,) = caixa
    assert mensagem.to == ["pessoa@exemplo.test"]
    assert mensagem.cc == [] and mensagem.bcc == []
    assert mensagem.from_email == "nao-responda@exemplo.test"
    (html,) = [conteudo for conteudo, tipo in mensagem.alternatives if tipo == "text/html"]
    assert html.startswith("<!doctype html>")
    assert mensagem.body.endswith("Esta mensagem é automática; não responda.\n")
    assert "{{" not in mensagem.body + html and "{%" not in mensagem.body + html
    assert mensagem.extra_headers == {"Auto-Submitted": "auto-generated"}
    assert "Auto-Submitted: auto-generated" in mensagem.message().as_string()


def test_a_convocacao_tambem_se_declara_automatica(caixa):
    envio = enviar_mensagem_de_convocacao(
        para="pessoa@exemplo.test",
        dados={
            "edital": "Edital 1/2026",
            "processo": "Especialização",
            "vencimento": datetime(2030, 1, 10, 17, 0, tzinfo=ZoneInfo("America/Sao_Paulo")),
            "link": "/selecoes/inscricoes/x/convocacao",
            "escolha": EscolhaDaMensagem(modelo=INICIAL, variante="so_documento"),
            "atendimento": "atendimento@exemplo.test",
            "assinatura": "Cefor/Ifes",
            "unidade": "Cefor",
        },
    )

    assert envio.detalhe == ""
    (mensagem,) = caixa
    assert mensagem.to == ["pessoa@exemplo.test"]
    assert mensagem.extra_headers == {"Auto-Submitted": "auto-generated"}


def test_sem_destinatario_nada_sai(caixa):
    enviar_comprovante(para="", dados=COMPROVANTE)
    avisar_mudanca_de_credencial(
        para="", endereco="x@exemplo.test", acao="removido", atendimento=""
    )
    assert caixa == []
