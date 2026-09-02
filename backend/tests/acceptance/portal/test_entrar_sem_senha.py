"""Entrega 1 — informar o e-mail, informar o código, chegar à área. Sem senha e sem CPF.

O percurso é o da spec: quem nunca se inscreveu prova uma caixa de e-mail e passa a ter um lugar.
A área está vazia, e vazio aqui não é erro — é o estado normal de todo candidato novo, no minuto
seguinte ao primeiro acesso.
"""

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity

pytestmark = [pytest.mark.django_db, pytest.mark.acceptance]

ENDERECO = "candidata.nova@exemplo.test"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def codigo_recebido(caixa):
    """O que a pessoa lê na mensagem — seis dígitos, e nada de link."""
    import re

    return re.search(r"\b(\d{6})\b", caixa[0].body).group(1)


def test_percurso_completo_sem_senha_e_sem_cpf(client, canal):
    # 1. Informa o e-mail.
    resposta = client.post(reverse("portal:acesso"), {"email": ENDERECO}, follow=True)
    corpo = resposta.content.decode()
    assert "Se este endereço puder ser utilizado" in corpo
    assert "CPF" not in corpo, "candidato novo não informa CPF em momento algum"

    # 2. Recebe e digita o código, colado como veio.
    codigo = codigo_recebido(canal)
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo}, follow=True)

    # 3. Chega à área — vazia, e sem cara de erro.
    corpo = resposta.content.decode()
    assert "Minhas inscrições" in corpo
    assert "Você ainda não possui inscrições" in corpo
    assert "Ver processos seletivos" in corpo
    # "Sem cara de erro" dito de forma verificável: o estado vazio não usa a marcação de recusa.
    assert 'class="recusa"' not in corpo

    # 4. E passou a existir, com a credencial que acabou de provar.
    identidade = CandidateIdentity.objects.get()
    credencial = CandidateEmail.objects.get()
    assert credencial.identidade_id == identidade.pk
    assert credencial.principal is True
    assert identidade.nome == "" and identidade.cpf_normalizado == ""


def test_o_codigo_pode_ser_colado_com_separadores(client, canal):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    codigo = codigo_recebido(canal)
    colado = f"{codigo[:3]} {codigo[3:]}"
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": colado})
    assert resposta["Location"] == reverse("portal:inscricoes")


def test_erro_no_codigo_nao_apaga_o_endereco(client, canal):
    """UX-007: quem erra o código não recomeça o fluxo."""
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": "000000"})
    assert ENDERECO in resposta.content.decode()


def test_a_area_diz_quem_esta_mesmo_sem_nome(client, canal):
    """Quem entrou pela primeira vez ainda não tem nome; o cabeçalho não pode ficar vazio."""
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo_recebido(canal)})
    corpo = client.get(reverse("portal:inscricoes")).content.decode()
    assert ENDERECO in corpo
    assert "Sair" in corpo
