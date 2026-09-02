"""Entrega 2 — quem se inscreveu antes reencontra o que enviou, confirmando o CPF uma vez.

E o percurso do engano, que é o caso realista: recusar o convite sem ler, cair numa área vazia,
perceber, e retomar. Encerrar o convite naquele clique poria a perda definitiva do que a pessoa
submeteu atrás de um segundo de desatenção.
"""

import uuid

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.models import (
    CandidateEmail,
    CandidateIdentity,
    novo_subject,
)
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.acceptance]

CPF_DE_MARIA = "12345678909"
ENDERECO = "maria@exemplo.test"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def maria_da_009(selecao):
    """O que a implantação encontrou: identidade reconciliada, com a inscrição que ela já tinha."""
    identidade = CandidateIdentity.objects.create(
        subject=novo_subject(),
        nome="Maria Silva",
        cpf_normalizado=CPF_DE_MARIA,
        created_at=timezone.now(),
    )
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=identidade.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Maria Silva",
        cpf="123.456.789-09",
        cpf_normalizado=CPF_DE_MARIA,
        email=ENDERECO,
        created_at=timezone.now(),
    )
    return identidade


def codigo(caixa):
    import re

    return re.search(r"\b(\d{6})\b", caixa[-1].body).group(1)


def entrar(client, canal, endereco=ENDERECO):
    client.post(reverse("portal:acesso"), {"email": endereco})
    return client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})


def test_confirma_o_cpf_uma_vez_e_reencontra_a_inscricao(client, canal, maria_da_009):
    resposta = entrar(client, canal)
    assert resposta["Location"] == reverse("portal:acesso-reconciliar")

    corpo = client.get(reverse("portal:acesso-reconciliar")).content.decode()
    assert "Encontramos participação anterior" in corpo

    client.post(reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": CPF_DE_MARIA})

    area = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Você ainda não possui inscrições" not in area
    assert CandidateEmail.objects.get(email_canonico=ENDERECO).identidade_id == maria_da_009.pk
    assert Inscricao.objects.get().identity_subject == maria_da_009.subject


def test_no_acesso_seguinte_o_cpf_nao_e_pedido(client, canal, maria_da_009):
    entrar(client, canal)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": CPF_DE_MARIA})
    client.post(reverse("portal:sair"))

    from processo_seletivo.identidade.models import DesafioDeAcesso

    DesafioDeAcesso.objects.all().delete()
    resposta = entrar(client, canal)

    assert resposta["Location"] == reverse("portal:inscricoes")


def test_recusar_por_engano_e_retomar_depois(client, canal, maria_da_009):
    entrar(client, canal)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})

    area = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Você ainda não possui inscrições" in area
    assert "Vincular participação anterior" in area, "o convite tem de estar à mão"

    # Retomar: prova o endereço de novo e confirma o CPF.
    client.post(reverse("portal:acesso-retomar"))
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": CPF_DE_MARIA})

    area = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Você ainda não possui inscrições" not in area
    assert CandidateIdentity.objects.count() == 1, "a identidade vazia foi descartada"
    assert Inscricao.objects.get().identity_subject == maria_da_009.subject


def test_o_convite_some_depois_da_primeira_inscricao(client, canal, maria_da_009, selecao):
    entrar(client, canal)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})
    propria = CandidateIdentity.objects.exclude(pk=maria_da_009.pk).get()
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=propria.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="",
        cpf="",
        cpf_normalizado="",
        email=ENDERECO,
        created_at=timezone.now(),
    )

    area = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Vincular participação anterior" not in area
    assert client.post(reverse("portal:acesso-retomar")).status_code == 404
