"""Reenviar responde por escrito — inclusive quando não envia.

O botão estava sempre clicável e, dentro da janela de espera, não enviava nada e não dizia nada: a
página recarregava idêntica, e a recusa que estava na tela sumia junto. O clique **parecia** ter
funcionado, e a pessoa passava a esperar um e-mail que nunca saiu. Somado à recusa que não
distinguia o teto do código errado (`test_recusa_do_codigo`), fechava o laço que perdia candidato
no primeiro minuto.

Silêncio é a pior resposta possível aqui, porque é indistinguível de sucesso.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR
ENDERECO = "reenvia@exemplo.test"


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def tela(client):
    return client.get(reverse("portal:acesso-codigo")).content.decode()


def test_reenviar_dentro_da_espera_diz_que_nada_foi_enviado(client, caixa):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    assert len(caixa) == 1

    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    corpo = tela(client)

    assert len(caixa) == 1, "nada novo saiu — e é justamente isso que precisa ser dito"
    assert "Ainda não enviamos outro código" in corpo
    assert "Veja abaixo quando será possível pedir de novo" in corpo
    # Um número só para a mesma espera: o do contador ao lado do botão, que é recalculado a cada
    # renderização. Repetir aqui o valor apurado no POST punha dois números diferentes na tela.
    assert len(re.findall(r"\d+ segundos", corpo)) == 1


def test_reenviar_depois_da_espera_envia_e_avisa(client, caixa, monkeypatch):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})

    # O relógio anda; o teste não espera um minuto por isso.
    monkeypatch.setattr(servico, "ESPERA_ENTRE_ENVIOS", servico.timedelta(seconds=0))
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    corpo = tela(client)

    assert len(caixa) == 2
    assert "Enviamos um código novo" in corpo
    assert "Use o mais recente" in corpo


def test_o_primeiro_pedido_nao_anuncia_reenvio(client, caixa):
    """A tela já diz "Enviado para X"; repetir a notícia seria ruído no caminho normal."""
    client.post(reverse("portal:acesso"), {"email": ENDERECO})

    corpo = tela(client)

    assert "Enviamos um código novo" not in corpo
    assert "Ainda não enviamos" not in corpo


def test_a_contagem_e_recalculada_e_nao_congelada(client, caixa, monkeypatch):
    """A espera vinha da sessão e envelhecia com a página: dois minutos parada ali, e ela ainda
    anunciava sessenta segundos."""
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    primeira = int(re.search(r"daqui a (\d+) segundos", tela(client)).group(1))

    monkeypatch.setattr(servico, "ESPERA_ENTRE_ENVIOS", servico.timedelta(seconds=30))
    segunda = int(re.search(r"daqui a (\d+) segundos", tela(client)).group(1))

    assert primeira > segunda, "o número acompanha o relógio, e não o instante do pedido"


def test_a_tela_traz_a_contagem_para_quem_tem_javascript(client, caixa):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})

    corpo = tela(client)

    assert 'id="reenvio"' in corpo and "data-espera=" in corpo
    assert "portal/reenvio.js" in corpo
    assert "daqui a" in corpo, "'em até 60 segundos' se lia como *dentro de* 60 segundos"
    assert "em até" not in corpo


def test_o_botao_continua_clicavel_no_servidor(client, caixa):
    """Desabilitar no servidor prenderia quem está sem JavaScript: a página não se atualiza
    sozinha, e o botão nunca voltaria. A resposta escrita é o que cobre esse caso."""
    client.post(reverse("portal:acesso"), {"email": ENDERECO})

    corpo = tela(client)
    formulario = corpo.split('id="reenvio"')[1].split("</form>")[0]

    assert "disabled" not in formulario
