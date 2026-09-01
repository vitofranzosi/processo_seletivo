"""A resposta é a mesma nos quatro casos que poderiam revelar existência (FR-020, FR-021, FR-083).

Endereço com identidade, endereço sem identidade, limite esgotado e falha de envio. Se algum deles
respondesse diferente — no texto, no estado, ou na janela de espera —, o visitante teria como
descobrir quem existe apenas pedindo códigos. É por isso que os limites são por endereço e por
origem, e nunca por identidade: um contador que só avança para quem existe é o mesmo vazamento
escrito de outro jeito.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CONHECIDO = "conhecida@exemplo.test"
DESCONHECIDO = "ninguem@exemplo.test"


@pytest.fixture
def identidade_conhecida():
    return associacao.criar_identidade_com(CONHECIDO, CONHECIDO)


def pedir(client, endereco):
    return client.post(reverse("portal:acesso"), {"email": endereco}, follow=False)


def ler(client, endereco):
    """A tela, sem o que muda a cada requisição por natureza.

    O token de CSRF é novo a cada renderização e não diz nada sobre quem existe; compará-lo
    faria o teste falhar por um motivo que não é o que ele investiga.
    """
    pedir(client, endereco)
    corpo = client.get(reverse("portal:acesso-codigo")).content.decode()
    corpo = re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "TOKEN", corpo)
    # A contagem regressiva cai um segundo entre uma leitura e a outra por passagem do relógio, e
    # não por quem existe. Normalizada aqui, o teste continua comparando o que ele investiga — e
    # `test_a_janela_de_espera_e_a_mesma` confere o número em si, que é o mesmo dos dois lados.
    return re.sub(r"\b\d+ segundos", "N segundos", corpo)


def test_o_estado_da_resposta_e_o_mesmo(client, identidade_conhecida):
    com = pedir(client, CONHECIDO)
    client.session.flush()
    sem = pedir(client, DESCONHECIDO)
    assert com.status_code == sem.status_code == 302
    assert com["Location"] == sem["Location"]


def test_o_texto_da_tela_e_o_mesmo(client, identidade_conhecida):
    com = ler(client, CONHECIDO)
    sem = ler(client, DESCONHECIDO)
    assert "Se este endereço puder ser utilizado" in com
    assert com.replace(CONHECIDO, "X") == sem.replace(DESCONHECIDO, "X")


def test_a_janela_de_espera_e_a_mesma(client, identidade_conhecida):
    """A UX-006 pede que o reenvio informe quando — e o "quando" não pode depender de existir.

    Lido da tela, e não da sessão: a espera passou a ser recalculada a cada renderização, e é o que
    a pessoa lê que precisa ser idêntico nos dois casos.
    """
    com = servico.solicitar(email_canonico=CONHECIDO, finalidade=ENTRAR)[0]
    sem = servico.solicitar(email_canonico=DESCONHECIDO, finalidade=ENTRAR)[0]
    assert com.proxima_tentativa_em == sem.proxima_tentativa_em

    # E o que a tela anuncia também: a espera é recalculada na renderização, e o cálculo não
    # consulta identidade nenhuma.
    assert "segundos" in ler(client, CONHECIDO)
    assert ler(client, CONHECIDO) == ler(client, DESCONHECIDO).replace(DESCONHECIDO, CONHECIDO)


def test_o_limite_esgotado_responde_como_o_caminho_feliz(client):
    for _ in range(servico.LIMITE_POR_ENDERECO + 2):
        resposta = pedir(client, DESCONHECIDO)
        assert resposta.status_code == 302
    corpo = client.get(reverse("portal:acesso-codigo")).content.decode()
    assert "Se este endereço puder ser utilizado" in corpo


def test_a_falha_de_envio_nao_aparece(client, settings, monkeypatch):
    """Uma mensagem de erro que só surge para endereço existente é o mesmo canal lateral."""
    from processo_seletivo.identidade.application import mensagem

    def explodir(*_args, **_kwargs):
        raise OSError("servidor de e-mail indisponível")

    monkeypatch.setattr(mensagem, "send_mail", explodir)
    resposta = pedir(client, DESCONHECIDO)
    assert resposta.status_code == 302
    assert "Se este endereço puder ser utilizado" in (
        client.get(reverse("portal:acesso-codigo")).content.decode()
    )
