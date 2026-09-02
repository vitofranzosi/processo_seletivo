"""Entrega 6 — cuidar das próprias credenciais antes de precisar delas.

O caso real é a troca de provedor entre um certame e outro. Quem espera perder a caixa antiga já
perdeu; a hora de resolver é agora, com ela ainda funcionando.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import credenciais as nucleo
from processo_seletivo.identidade.models import CandidateEmail, DesafioDeAcesso
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.acceptance]

ANTIGO = "antigo@provedor-que-vai-fechar.test"
NOVO = "novo@provedor.test"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def codigo(canal):
    return re.search(r"\b(\d{6})\b", canal[-1].body).group(1)


@pytest.fixture
def dentro(client):
    identidade = associacao.criar_identidade_com(ANTIGO, ANTIGO)
    nucleo.gravar_nucleo(identidade, nome="Maria Silva", cpf="123.456.789-09")
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    return identidade


def test_percurso_da_entrega_6(client, canal, dentro):
    # 1. Acrescenta o endereço novo, provando a caixa. Sem CPF.
    conta = client.get(reverse("portal:conta")).content.decode()
    assert ANTIGO in conta and "Adicionar e-mail" in conta

    client.post(reverse("portal:conta-adicionar"), {"email": NOVO})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})

    conta = client.get(reverse("portal:conta")).content.decode()
    assert NOVO in conta

    # 2. Torna o novo principal.
    nova = CandidateEmail.objects.get(identidade=dentro, email_canonico=NOVO)
    client.post(reverse("portal:conta-principal", args=[nova.id]))
    assert CandidateEmail.objects.get(identidade=dentro, principal=True).email_canonico == NOVO

    # 3. Remove o antigo, e nenhuma inscrição muda.
    antiga = CandidateEmail.objects.get(identidade=dentro, email_canonico=ANTIGO)
    antes = list(Inscricao.objects.order_by("id").values())
    client.post(reverse("portal:conta-remover", args=[antiga.id]))

    assert list(Inscricao.objects.order_by("id").values()) == antes
    assert list(
        CandidateEmail.objects.filter(identidade=dentro).values_list("email_canonico", flat=True)
    ) == [NOVO]

    # 4. E a última não sai.
    restante = CandidateEmail.objects.get(identidade=dentro)
    client.post(reverse("portal:conta-remover", args=[restante.id]))
    assert CandidateEmail.objects.filter(pk=restante.pk).exists()
    assert "não pode remover seu último e-mail" in (
        client.get(reverse("portal:conta")).content.decode()
    )

    # 5. Entra pelo endereço novo — o antigo já não serve.
    client.post(reverse("portal:sair"))
    DesafioDeAcesso.objects.all().delete()
    client.post(reverse("portal:acesso"), {"email": NOVO})
    assert client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})[
        "Location"
    ] == reverse("portal:inscricoes")


def test_corrigir_o_nome_pela_conta(client, canal, dentro):
    conta = client.get(reverse("portal:conta")).content.decode()
    assert reverse("portal:meus-dados") in conta

    client.post(reverse("portal:meus-dados"), {"nome": "Maria S. Silva", "cpf": "123.456.789-09"})

    dentro.refresh_from_db()
    assert dentro.nome == "Maria S. Silva"
