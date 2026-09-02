"""Trocar a principal alcança os rascunhos; remover não alcança nada (FR-014, FR-019).

A distinção é a mesma regra única dos três campos do núcleo: enquanto a inscrição é rascunho, ela
acompanha a identidade; no envio, congela. Remover credencial é outro ato — é como se entra, não o
que se enviou.
"""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateEmail
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal import identidade as identidade_do_candidato
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PRIMEIRO = "primeiro@exemplo.test"
SEGUNDO = "segundo@exemplo.test"


@pytest.fixture
def dentro(client):
    identidade = associacao.criar_identidade_com(PRIMEIRO, PRIMEIRO)
    associacao.associar_credencial(identidade, SEGUNDO, SEGUNDO)
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    return identidade


def inscricao(selecao, identidade, *, perfil=PERFIL_DOCENTE, enviada=False):
    registro = Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=identidade.subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome="Maria Silva",
        cpf="123.456.789-09",
        cpf_normalizado="12345678909",
        email=PRIMEIRO,
        created_at=timezone.now(),
    )
    if enviada:
        Inscricao.objects.filter(pk=registro.pk).update(
            status="SUBMETIDA",
            submitted_at=timezone.now(),
            declaracoes_aceitas_em=timezone.now(),
            versao_aceita=VersaoConsolidada.objects.filter(edital_id=selecao.id).first(),
            protocolo=f"INS-{uuid.uuid4().hex[:8].upper()}",
        )
        registro.refresh_from_db()
    return registro


def credencial(identidade, endereco):
    return CandidateEmail.objects.get(identidade=identidade, email_canonico=endereco)


def test_trocar_a_principal(client, dentro):
    resposta = client.post(
        reverse("portal:conta-principal", args=[credencial(dentro, SEGUNDO).id])
    )

    assert resposta["Location"] == reverse("portal:conta")
    assert credencial(dentro, SEGUNDO).principal is True
    assert credencial(dentro, PRIMEIRO).principal is False


def test_a_troca_alcanca_o_rascunho(client, dentro, selecao):
    rascunho = inscricao(selecao, dentro)

    client.post(reverse("portal:conta-principal", args=[credencial(dentro, SEGUNDO).id]))

    corpo = client.get(reverse("portal:inscricao", args=[rascunho.id])).content.decode()
    assert SEGUNDO in corpo, "o rascunho aberto acompanha a identidade"


def test_a_troca_nao_alcanca_a_enviada(client, dentro, selecao):
    enviada = inscricao(selecao, dentro, enviada=True)
    antes = Inscricao.objects.values().get(pk=enviada.pk)

    client.post(reverse("portal:conta-principal", args=[credencial(dentro, SEGUNDO).id]))

    assert Inscricao.objects.values().get(pk=enviada.pk) == antes
    assert Inscricao.objects.get(pk=enviada.pk).email == PRIMEIRO


def test_remover_nao_altera_inscricao_alguma(client, dentro, selecao):
    rascunho = inscricao(selecao, dentro)
    enviada = inscricao(selecao, dentro, perfil=PERFIL_TECNICO, enviada=True)
    antes = list(Inscricao.objects.order_by("id").values())

    client.post(reverse("portal:conta-remover", args=[credencial(dentro, SEGUNDO).id]))

    assert list(Inscricao.objects.order_by("id").values()) == antes
    assert Inscricao.objects.get(pk=rascunho.pk).email == PRIMEIRO
    assert Inscricao.objects.get(pk=enviada.pk).email == PRIMEIRO


def test_remover_a_principal_promove_a_mais_antiga_que_resta(client, dentro):
    client.post(reverse("portal:conta-remover", args=[credencial(dentro, PRIMEIRO).id]))

    restante = CandidateEmail.objects.get(identidade=dentro)
    assert restante.email_canonico == SEGUNDO
    assert restante.principal is True, "a identidade nunca fica sem principal"


def test_tornar_principal_credencial_de_outra_identidade_responde_404(client, dentro):
    alheia = associacao.criar_identidade_com("alheia@exemplo.test", "alheia@exemplo.test")
    de_outra = CandidateEmail.objects.get(identidade=alheia)

    assert client.post(reverse("portal:conta-principal", args=[de_outra.id])).status_code == 404
    assert CandidateEmail.objects.get(pk=de_outra.pk).principal is True


def test_remover_credencial_de_outra_identidade_nao_a_remove(client, dentro):
    alheia = associacao.criar_identidade_com("alheia@exemplo.test", "alheia@exemplo.test")
    de_outra = CandidateEmail.objects.get(identidade=alheia)

    client.post(reverse("portal:conta-remover", args=[de_outra.id]))

    assert CandidateEmail.objects.filter(pk=de_outra.pk).exists()
