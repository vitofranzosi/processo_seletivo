"""Nenhum caminho de credencial termina em beco sem saída (P-009, FR-052).

Recusar o convite, errar o CPF, esgotar as tentativas, deixar expirar: todos terminam com a pessoa
dentro de uma identidade própria e utilizável. A alternativa — recusar e não dar sessão — puniria
o dono legítimo de um endereço reciclado, que é o caso mais provável de todos.

E identidades **não se fundem**: quem já tem uma e prova endereço novo sem correspondência recebe
outra, nunca uma mistura das duas (FR-056).
"""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import (
    CandidateEmail,
    CandidateIdentity,
    DesafioDeAcesso,
    novo_subject,
)
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal import identidade as identidade_do_candidato
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CPF_DE_MARIA = "12345678909"
ENDERECO = "maria@exemplo.test"


@pytest.fixture
def legada(selecao):
    identidade = CandidateIdentity.objects.create(
        subject=novo_subject(),
        nome="Maria",
        cpf_normalizado=CPF_DE_MARIA,
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


def entrar_ate_o_convite(client):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    codigo = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )[1]
    if not codigo:
        DesafioDeAcesso.objects.all().delete()
        _, codigo = servico.solicitar(
            email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
        )
    return client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})


def test_o_convite_aparece_para_quem_tem_participacao_anterior(client, legada):
    resposta = entrar_ate_o_convite(client)
    assert resposta["Location"] == reverse("portal:acesso-reconciliar")


def test_recusar_o_convite_da_identidade_propria_com_sessao(client, legada):
    entrar_ate_o_convite(client)
    resposta = client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})

    assert resposta["Location"] == reverse("portal:inscricoes")
    assert identidade_do_candidato.CHAVE_SESSAO in client.session
    propria = CandidateIdentity.objects.exclude(pk=legada.pk).get()
    assert propria.credenciais.get().email_canonico == ENDERECO


def test_recusar_nao_toca_a_identidade_anterior(client, legada):
    antes = list(Inscricao.objects.values_list("id", "identity_subject"))
    entrar_ate_o_convite(client)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})

    legada.refresh_from_db()
    assert list(Inscricao.objects.values_list("id", "identity_subject")) == antes
    assert legada.cpf_normalizado == CPF_DE_MARIA


def test_esgotar_as_tentativas_ainda_da_sessao(client, legada):
    entrar_ate_o_convite(client)
    from processo_seletivo.identidade.models import TETO_DE_TENTATIVAS

    # A quinta tentativa é a que encerra: ela conta, falha, e já leva a pessoa para dentro da
    # identidade própria. Não há uma sexta a fazer.
    for _ in range(TETO_DE_TENTATIVAS):
        resposta = client.post(
            reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": "111.222.333-44"}
        )
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:inscricoes")
    assert identidade_do_candidato.CHAVE_SESSAO in client.session


def test_nao_funde_identidades(client):
    """Endereço novo sem correspondência produz identidade nova — nunca uma mistura (FR-056)."""
    primeira = associacao.criar_identidade_com("uma@exemplo.test", "uma@exemplo.test")
    segunda = associacao.criar_identidade_com("outra@exemplo.test", "outra@exemplo.test")

    assert primeira.pk != segunda.pk
    assert CandidateEmail.objects.filter(identidade=primeira).count() == 1
    assert CandidateEmail.objects.filter(identidade=segunda).count() == 1


def test_o_convite_expirado_ainda_da_sessao(client, legada):
    """O outro lado da correção: quem **provou** o endereço não pode ficar de fora (FR-052b).

    Recusar a rota sem prova era necessário; recusá-la a quem provou e só demorou a decidir teria
    trocado um desvio de autenticação por um beco sem saída.
    """
    from datetime import timedelta

    from django.utils import timezone

    entrar_ate_o_convite(client)
    DesafioDeAcesso.objects.update(reconciliacao_ate=timezone.now() - timedelta(seconds=1))

    resposta = client.get(reverse("portal:acesso-reconciliar"))

    assert resposta["Location"] == reverse("portal:inscricoes")
    assert identidade_do_candidato.CHAVE_SESSAO in client.session
    propria = CandidateEmail.objects.get(email_canonico=ENDERECO).identidade
    assert propria.pk != legada.pk, "identidade própria, e não a anterior"


def test_o_convite_expirado_na_retomada_reentra_na_propria_identidade(client, legada, selecao):
    """A retomada expirada devolve a pessoa à identidade dela — e não a uma órfã (revisão).

    A versão anterior chamava direto a criação de identidade, e só não errava porque a violação de
    unicidade era capturada e devolvia a dona do endereço. Correção por acidente: tornada estrita
    aquela captura, esta linha passaria a trocar a identidade da pessoa por uma vazia.
    """
    from datetime import timedelta

    from django.utils import timezone

    entrar_ate_o_convite(client)
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})
    propria = CandidateEmail.objects.get(email_canonico=ENDERECO).identidade
    quantas = CandidateIdentity.objects.count()

    client.post(reverse("portal:acesso-retomar"))
    codigo = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.RETOMAR
    )[1]
    if not codigo:
        DesafioDeAcesso.objects.filter(finalidade="RETOMAR").delete()
        _, codigo = servico.solicitar(
            email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.RETOMAR
        )
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})
    DesafioDeAcesso.objects.filter(finalidade="RETOMAR").update(
        reconciliacao_ate=timezone.now() - timedelta(seconds=1)
    )

    resposta = client.get(reverse("portal:acesso-reconciliar"))

    assert resposta["Location"] == reverse("portal:inscricoes")
    assert CandidateIdentity.objects.count() == quantas, "nenhuma identidade a mais"
    assert CandidateEmail.objects.get(email_canonico=ENDERECO).identidade_id == propria.pk
