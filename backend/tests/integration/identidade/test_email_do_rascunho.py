"""O rascunho é alimentado pelo e-mail **principal**, e não pelo que autenticou a sessão (FR-013).

Não é detalhe: `Inscricao.email` é o registro de contato do ato administrativo. "O endereço da
sessão" faria a mesma pessoa constar de duas inscrições com contatos diferentes conforme a caixa
que ela abriu naquele dia — e quem recebe a inscrição não teria como saber qual vale.
"""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateEmail
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PRINCIPAL = "principal@exemplo.test"
SEGUNDO = "segundo@exemplo.test"


@pytest.fixture
def com_dois_enderecos(client):
    identidade = associacao.criar_identidade_com(PRINCIPAL, PRINCIPAL)
    associacao.associar_credencial(identidade, SEGUNDO, SEGUNDO)
    sessao = client.session
    sessao["portal_identidade"] = str(identidade.pk)
    sessao.save()
    return identidade


def test_o_rascunho_recebe_o_principal(client, com_dois_enderecos, selecao):
    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": "123.456.789-09"})
    client.post(reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE]))

    assert Inscricao.objects.get().email == PRINCIPAL


def test_a_segunda_credencial_nao_vira_contato(client, com_dois_enderecos, selecao):
    assert CandidateEmail.objects.filter(identidade=com_dois_enderecos).count() == 2
    assert (
        CandidateEmail.objects.get(identidade=com_dois_enderecos, principal=True).email_canonico
        == PRINCIPAL
    )
