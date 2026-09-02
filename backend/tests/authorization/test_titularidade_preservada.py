"""Nenhuma inscrição muda de titular em nenhum desfecho da reconciliação (FR-042, SC-007).

É a promessa central da feature, e a que mais custaria se fosse quebrada em silêncio: uma inscrição
que troca de dono não dá erro, não aparece em log e não é notada por ninguém — até o dia em que a
pessoa procura o que enviou e não encontra.
"""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import (
    CandidateIdentity,
    DesafioDeAcesso,
    novo_subject,
)
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]

CPF_DE_MARIA = "12345678909"
ENDERECO = "maria@exemplo.test"


@pytest.fixture
def legada(selecao):
    identidade = CandidateIdentity.objects.create(
        subject=novo_subject(), nome="Maria", cpf_normalizado=CPF_DE_MARIA,
        created_at=timezone.now(),
    )
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=identidade.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Maria",
        cpf=CPF_DE_MARIA,
        cpf_normalizado=CPF_DE_MARIA,
        email=ENDERECO,
        created_at=timezone.now(),
    )
    return identidade


def titulares():
    return sorted(Inscricao.objects.values_list("id", "identity_subject"))


def ate_o_convite(client):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    DesafioDeAcesso.objects.all().delete()
    _, codigo = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})


@pytest.mark.parametrize(
    "desfecho",
    [
        {"acao": "continuar"},
        {"acao": "confirmar", "cpf": "111.222.333-44"},
        {"acao": "confirmar", "cpf": CPF_DE_MARIA},
    ],
    ids=["recusa", "cpf-errado", "cpf-certo"],
)
def test_nenhum_desfecho_troca_o_titular(client, legada, desfecho):
    antes = titulares()
    ate_o_convite(client)
    client.post(reverse("portal:acesso-reconciliar"), desfecho)
    assert titulares() == antes


def test_reconciliar_torna_a_inscricao_visivel_sem_mudar_de_dono(client, legada):
    antes = titulares()
    ate_o_convite(client)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": CPF_DE_MARIA})

    corpo = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Você ainda não possui inscrições" not in corpo
    assert titulares() == antes


def test_a_retomada_tambem_nao_troca_o_titular(client, legada):
    antes = titulares()
    ate_o_convite(client)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})
    from processo_seletivo.identidade.models import CandidateEmail

    propria = CandidateEmail.objects.get(email_canonico=ENDERECO).identidade

    associacao.retomar(vazia=propria, destino=legada)

    assert titulares() == antes
