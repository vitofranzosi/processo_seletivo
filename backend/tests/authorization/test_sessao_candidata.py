"""A sessão do candidato não abre nenhuma porta institucional (FR-003, FR-039, SC-014).

São dois eixos de identidade, com chaves de sessão distintas, e é isso que impede o candidato de
atravessar `require_permission`: ele não é ator, é titular. O dia em que uma permissão fosse
concedida a mais, um candidato praticaria ato institucional.
"""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]

ENDERECO = "maria@exemplo.test"


@pytest.fixture
def candidato(client):
    identidade = associacao.criar_identidade_com(ENDERECO, ENDERECO)
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    return identidade


def test_a_gestao_nao_reconhece_a_sessao_do_candidato(client, candidato, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    resposta = client.get(reverse("interface:lista"))
    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta["Location"]


def test_as_duas_chaves_de_sessao_nao_se_misturam(client, candidato):
    assert identidade_do_candidato.CHAVE_SESSAO in client.session
    assert "interface_identidade" not in client.session


def test_o_candidato_entra_no_portal(client, candidato):
    assert client.get(reverse("portal:inscricoes")).status_code == 200
