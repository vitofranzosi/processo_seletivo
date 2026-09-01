"""A lista: todas e somente as suas, mais recente primeiro, uma ação principal por item."""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import (
    JOAO,
    MARIA,
    PERFIL_DOCENTE,
    PERFIL_TECNICO,
    identificar,
    registrar,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def inscricao(selecao, identidade, *, perfil=PERFIL_DOCENTE, quando=None, enviada=False):
    registro = Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=identidade.subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome=identidade.nome,
        cpf=identidade.cpf,
        cpf_normalizado=identidade.cpf.replace(".", "").replace("-", ""),
        email=identidade.email,
        created_at=quando or timezone.now(),
    )
    if enviada:
        from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

        Inscricao.objects.filter(pk=registro.pk).update(
            status="SUBMETIDA",
            submitted_at=timezone.now(),
            declaracoes_aceitas_em=timezone.now(),
            versao_aceita=VersaoConsolidada.objects.filter(edital_id=selecao.id).first(),
            protocolo="INS-2027-K7M4Q2PX",
        )
        registro.refresh_from_db()
    return registro


def test_mostra_todas_as_minhas(client, selecao):
    inscricao(selecao, MARIA)
    inscricao(selecao, MARIA, perfil=PERFIL_TECNICO)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    assert corpo.count("Continuar inscrição") == 2


def test_nao_mostra_a_de_outro_candidato(client, selecao):
    alheia = inscricao(selecao, JOAO)
    registrar(JOAO)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    assert str(alheia.id) not in corpo
    assert "Você ainda não possui inscrições" in corpo


def test_a_mais_recente_vem_primeiro(client, selecao):
    from datetime import timedelta

    agora = timezone.now()
    inscricao(selecao, MARIA, quando=agora - timedelta(days=3))
    recente = inscricao(selecao, MARIA, perfil=PERFIL_TECNICO, quando=agora)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    itens = [
        bloco
        for bloco in corpo.split('<li class="selecao">')
        if "/inscricoes/" in bloco
    ]
    assert str(recente.id) in itens[0], "a mais recente encabeça a lista"


def test_a_acao_principal_e_uma_so_e_e_inequivoca(client, selecao):
    inscricao(selecao, MARIA, enviada=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    assert "Acompanhar" in corpo
    assert "Continuar inscrição" not in corpo, "enviada não se continua"
    assert "INS-2027-K7M4Q2PX" in corpo
    assert "✓ Inscrição enviada" in corpo


def test_cada_item_diz_de_qual_Edital_e_de_qual_Perfil_e(client, selecao):
    """O que a lista promete: reencontrar sem procurar o certame de novo.

    Sem Edital e sem Perfil, a lista devolve à pessoa a pergunta que ela existe para responder — e
    foi assim que ela ficou por uma versão inteira, porque o nome do atributo estava errado e a
    captura larga demais engolia o erro.
    """
    inscricao(selecao, MARIA)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    assert "Edital 01/2026" in corpo
    assert "Professor" in corpo or "Docente" in corpo, corpo[corpo.find("selecao"):][:400]


def test_o_rascunho_diz_que_nao_foi_enviado(client, selecao):
    inscricao(selecao, MARIA)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricoes")).content.decode()

    assert "Inscrição não enviada" in corpo
    assert "Continuar inscrição" in corpo
