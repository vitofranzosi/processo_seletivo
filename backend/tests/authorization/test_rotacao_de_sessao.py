"""O identificador de sessão muda no instante da autenticação (FR-035, SC-004).

Sem a rotação, quem induzir a pessoa a usar uma sessão conhecida antes de entrar — um link com o
identificador embutido, um computador compartilhado — continua dentro dela depois. O desafio
inteiro é contornado sem ser tocado: o atacante não precisa do código, precisa que a vítima o
digite numa sessão que ele já conhece.
"""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso
from processo_seletivo.portal.views import CHAVE_DO_ENDERECO

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]

ENDERECO = "maria@exemplo.test"


def sessao_conhecida(client):
    """A sessão que o atacante já viu — criada antes de qualquer autenticação."""
    sessao = client.session
    sessao[CHAVE_DO_ENDERECO] = ENDERECO
    sessao.save()
    client.cookies["sessionid"] = sessao.session_key
    return sessao.session_key


def test_o_identificador_de_sessao_muda_ao_entrar(client):
    antes = sessao_conhecida(client)
    _, codigo = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )

    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})

    assert resposta.status_code == 302
    assert client.session.session_key != antes, "a sessão conhecida continuaria valendo"


def test_a_sessao_anterior_nao_autentica_depois(client):
    antes = sessao_conhecida(client)
    _, codigo = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})

    from django.contrib.sessions.models import Session

    assert not Session.objects.filter(session_key=antes).exists()
