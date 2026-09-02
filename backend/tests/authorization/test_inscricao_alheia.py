"""Uma identidade não enxerga inscrição de outra, e a recusa não revela que ela existe.

`404` e não `403`: dizer "existe, mas não é seu" já entrega que existe — e a lista de inscrições de
um certame é justamente o que ninguém de fora pode enumerar.
"""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import JOAO, MARIA, PERFIL_DOCENTE, identificar

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def de_joao(selecao):
    return Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=JOAO.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome=JOAO.nome,
        cpf=JOAO.cpf,
        cpf_normalizado="98765432100",
        email=JOAO.email,
        created_at=timezone.now(),
    )


def test_a_inscricao_alheia_responde_404(client, de_joao):
    identificar(client, MARIA)
    assert client.get(reverse("portal:inscricao", args=[de_joao.id])).status_code == 404


def test_a_recusa_e_indistinguivel_da_inexistente(client, de_joao):
    identificar(client, MARIA)
    alheia = client.get(reverse("portal:inscricao", args=[de_joao.id]))
    inexistente = client.get(
        reverse("portal:inscricao", args=["00000000-0000-0000-0000-0000000009ff"])
    )
    assert alheia.status_code == inexistente.status_code == 404


def test_a_inscricao_alheia_nao_aparece_na_lista(client, de_joao):
    identificar(client, MARIA)
    corpo = client.get(reverse("portal:inscricoes")).content.decode()
    assert str(de_joao.id) not in corpo
