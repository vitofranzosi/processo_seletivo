"""Corrigir nome e CPF — e o que congela quando (FR-008, FR-014).

Pedido uma vez não é irrevogável. Erro de digitação e alteração de nome são eventos normais, e a
`009` permitia redigitar os dois a cada identificação: uma identidade persistente não pode ser mais
rígida do que o estado que ela substitui.
"""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import credenciais as nucleo
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal import identidade as identidade_do_candidato
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MEU = "meu@exemplo.test"
CPF = "123.456.789-09"
OUTRO_CPF = "987.654.321-00"


@pytest.fixture
def dentro(client):
    identidade = associacao.criar_identidade_com(MEU, MEU)
    nucleo.gravar_nucleo(identidade, nome="Maria Silva", cpf=CPF)
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
        nome=identidade.nome,
        cpf=CPF,
        cpf_normalizado=identidade.cpf_normalizado,
        email=MEU,
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


def test_corrigir_o_nome_alcanca_o_rascunho(client, dentro, selecao):
    rascunho = inscricao(selecao, dentro)

    client.post(reverse("portal:meus-dados"), {"nome": "Maria S. Silva", "cpf": CPF})

    corpo = client.get(reverse("portal:inscricao", args=[rascunho.id])).content.decode()
    assert "Maria S. Silva" in corpo


def test_corrigir_o_nome_nao_alcanca_a_enviada(client, dentro, selecao):
    enviada = inscricao(selecao, dentro, enviada=True)
    antes = Inscricao.objects.values().get(pk=enviada.pk)

    client.post(reverse("portal:meus-dados"), {"nome": "Maria S. Silva", "cpf": CPF})

    assert Inscricao.objects.values().get(pk=enviada.pk) == antes
    corpo = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()
    assert "Maria Silva" in corpo, "o comprovante registra o nome que constava no ato"


def test_o_cpf_e_corrigivel_enquanto_nao_houver_enviada(client, dentro, selecao):
    inscricao(selecao, dentro)

    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": OUTRO_CPF})

    dentro.refresh_from_db()
    assert dentro.cpf_normalizado == "98765432100"


def test_o_cpf_congela_na_primeira_enviada(client, dentro, selecao):
    inscricao(selecao, dentro, enviada=True)

    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": OUTRO_CPF})

    dentro.refresh_from_db()
    assert dentro.cpf_normalizado == "12345678909"


def test_a_tela_explica_por_que_o_cpf_nao_muda_mais(client, dentro, selecao):
    inscricao(selecao, dentro, enviada=True)

    corpo = client.get(reverse("portal:meus-dados")).content.decode()

    assert "readonly" in corpo
    assert "atendimento institucional" in corpo


def test_o_nome_continua_corrigivel_depois_da_enviada(client, dentro, selecao):
    """O nome não congela: ele não decide propriedade, e o que já foi submetido não muda."""
    inscricao(selecao, dentro, enviada=True)
    rascunho = inscricao(selecao, dentro, perfil=PERFIL_TECNICO)

    client.post(reverse("portal:meus-dados"), {"nome": "Maria S. Silva", "cpf": CPF})

    dentro.refresh_from_db()
    assert dentro.nome == "Maria S. Silva"
    corpo = client.get(reverse("portal:inscricao", args=[rascunho.id])).content.decode()
    assert "Maria S. Silva" in corpo
