"""O que não pode aparecer em registro técnico nem em auditoria (FR-009, FR-088).

Nem código, nem CPF completo, nem conteúdo de documento. O identificador opaco existe justamente
para que a trilha possa nomear o autor de um ato sem carregar o documento dele — e um `print` bem
intencionado desfaz isso sem que ninguém perceba.
"""

import logging
import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import DesafioDeAcesso
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
CPF = "12345678909"


@pytest.fixture
def registro_tecnico():
    """O que os loggers da aplicação emitiram — `caplog` não serve: `propagate` é falso."""

    class Coletor(logging.Handler):
        def __init__(self):
            super().__init__()
            self.linhas = []

        def emit(self, registro):
            self.linhas.append(self.format(registro))

        @property
        def texto(self):
            return "\n".join(self.linhas)

    coletor = Coletor()
    logger = logging.getLogger("processo_seletivo")
    anterior = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(coletor)
    yield coletor
    logger.removeHandler(coletor)
    logger.setLevel(anterior)


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def test_o_codigo_nao_aparece_em_registro_tecnico(client, canal, registro_tecnico):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    valor = re.search(r"\b(\d{6})\b", canal[-1].body).group(1)
    client.post(reverse("portal:acesso-codigo"), {"codigo": "000000"})
    client.post(reverse("portal:acesso-codigo"), {"codigo": valor})

    assert valor not in registro_tecnico.texto


def test_o_codigo_nao_aparece_na_auditoria(client, canal):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    valor = re.search(r"\b(\d{6})\b", canal[-1].body).group(1)
    client.post(reverse("portal:acesso-codigo"), {"codigo": valor})

    tudo = " ".join(str(linha) for linha in RegistroAuditoria.objects.values())
    assert valor not in tudo


def test_o_codigo_nao_e_guardado_em_forma_recuperavel(client, canal):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    valor = re.search(r"\b(\d{6})\b", canal[-1].body).group(1)

    guardado = " ".join(str(linha) for linha in DesafioDeAcesso.objects.values())
    assert valor not in guardado


def test_a_falha_de_envio_nao_registra_endereco_nem_codigo(monkeypatch, registro_tecnico):
    from processo_seletivo.identidade.application import mensagem

    def explodir(*_args, **_kwargs):
        raise OSError("indisponível")

    monkeypatch.setattr(mensagem, "send_mail", explodir)
    mensagem.enviar_codigo(para=ENDERECO, codigo="424242")

    assert "424242" not in registro_tecnico.texto
    assert ENDERECO not in registro_tecnico.texto
    assert "Falha ao enviar" in registro_tecnico.texto, "mas a falha é registrada"


def test_a_auditoria_de_credencial_nao_carrega_cpf_nem_endereco(client):
    identidade = associacao.criar_identidade_com(ENDERECO, ENDERECO)
    from processo_seletivo.identidade.application import credenciais as nucleo

    nucleo.gravar_nucleo(identidade, nome="Maria Silva", cpf="123.456.789-09")
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    associacao.associar_credencial(identidade, "outro@exemplo.test", "outro@exemplo.test")
    nucleo.registrar_ato(identidade, operacao="ASSOCIAR_CREDENCIAL")

    tudo = " ".join(str(linha) for linha in RegistroAuditoria.objects.values())
    assert CPF not in tudo and "123.456.789-09" not in tudo
    assert ENDERECO not in tudo
