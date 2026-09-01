"""As rotas do convite e da retomada, conforme `contracts/acesso.md`."""

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
from processo_seletivo.portal import identidade as identidade_do_candidato
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.contract]

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


def ate_o_convite(client):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    DesafioDeAcesso.objects.all().delete()
    _, codigo = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    return client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})


def autenticar(client, identidade):
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()


def test_o_convite_responde_200(client, legada):
    ate_o_convite(client)
    assert client.get(reverse("portal:acesso-reconciliar")).status_code == 200


def test_o_convite_nao_revela_nada_da_identidade_anterior(client, legada):
    ate_o_convite(client)
    corpo = client.get(reverse("portal:acesso-reconciliar")).content.decode()
    for revelador in ("Maria", CPF_DE_MARIA, "123.456.789-09"):
        assert revelador not in corpo


def test_cpf_certo_leva_a_minhas_inscricoes(client, legada):
    ate_o_convite(client)
    resposta = client.post(
        reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": CPF_DE_MARIA}
    )
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:inscricoes")


def test_cpf_errado_responde_200_sem_dizer_de_quem_e(client, legada):
    ate_o_convite(client)
    resposta = client.post(
        reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": "111.222.333-44"}
    )
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Não foi possível confirmar" in corpo
    assert "Maria" not in corpo


def test_a_retomada_nao_existe_para_quem_ja_tem_inscricao(client, legada):
    autenticar(client, legada)
    assert client.post(reverse("portal:acesso-retomar")).status_code == 404


def test_a_retomada_nao_existe_sem_correspondencia(client):
    propria = associacao.criar_identidade_com("sozinha@exemplo.test", "sozinha@exemplo.test")
    autenticar(client, propria)
    assert client.post(reverse("portal:acesso-retomar")).status_code == 404


def test_a_retomada_pede_o_codigo_de_novo(client, legada):
    """O ato que move credenciais e descarta uma identidade é reprovado no instante (D-016)."""
    ate_o_convite(client)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})

    resposta = client.post(reverse("portal:acesso-retomar"))

    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso-codigo")
    assert DesafioDeAcesso.objects.filter(finalidade="RETOMAR").exists()


def test_a_retomada_exige_sessao(client):
    resposta = client.post(reverse("portal:acesso-retomar"))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso")
