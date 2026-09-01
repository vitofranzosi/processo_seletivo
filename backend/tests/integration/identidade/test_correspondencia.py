"""O convite aparece só com correspondência anterior — e o CPF é que desempata (FR-050, FR-051).

Correspondência é **indício**: o endereço foi digitado num formulário, pode ter erro, pode
pertencer a terceiro. O que ele autoriza é oferecer o convite. Quem confirma é o CPF, e ele confirma
uma correspondência que o sistema já encontrou — nunca cria uma.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateIdentity, novo_subject
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
CPF_DE_MARIA = "12345678909"
CPF_DE_JOAO = "98765432100"


def identidade_legada(cpf, subject=None):
    return CandidateIdentity.objects.create(
        subject=subject or novo_subject(),
        nome="Alguém",
        cpf_normalizado=cpf,
        created_at=timezone.now(),
    )


def inscricao_de(selecao, identidade, email, perfil=PERFIL_DOCENTE):
    return Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=identidade.subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome=identidade.nome,
        cpf=identidade.cpf_normalizado,
        cpf_normalizado=identidade.cpf_normalizado,
        email=email,
        created_at=timezone.now(),
    )


def test_sem_participacao_anterior_nao_ha_correspondencia():
    assert associacao.correspondencia_historica("ninguem@exemplo.test") == []


def test_o_endereco_de_uma_inscricao_anterior_produz_correspondencia(selecao):
    dona = identidade_legada(CPF_DE_MARIA)
    inscricao_de(selecao, dona, ENDERECO)
    assert [item.pk for item in associacao.correspondencia_historica(ENDERECO)] == [dona.pk]


def test_a_correspondencia_ignora_a_caixa_do_endereco(selecao):
    dona = identidade_legada(CPF_DE_MARIA)
    inscricao_de(selecao, dona, "Maria@Exemplo.TEST")
    assert associacao.correspondencia_historica(ENDERECO)


def test_o_cpf_desempata_entre_identidades_distintas(selecao, desafio_consumido):
    """Um endereço compartilhado — uma família, um e-mail de trabalho — não impede reconciliar."""
    de_maria = identidade_legada(CPF_DE_MARIA)
    de_joao = identidade_legada(CPF_DE_JOAO)
    inscricao_de(selecao, de_maria, ENDERECO)
    inscricao_de(selecao, de_joao, ENDERECO, perfil=PERFIL_TECNICO)

    associacao.abrir_reconciliacao(
        desafio_consumido, associacao.correspondencia_historica(ENDERECO)
    )
    escolhida = associacao.confirmar_cpf(desafio_consumido, CPF_DE_JOAO)

    assert escolhida is not None and escolhida.pk == de_joao.pk


def test_cpf_que_nao_confere_com_nenhuma_nao_reconcilia(selecao, desafio_consumido):
    dona = identidade_legada(CPF_DE_MARIA)
    inscricao_de(selecao, dona, ENDERECO)
    associacao.abrir_reconciliacao(desafio_consumido, [dona])

    assert associacao.confirmar_cpf(desafio_consumido, "111.222.333-44") is None
