"""A retomada: disponível enquanto a identidade estiver vazia, e não depois (FR-053 a FR-055).

O caso que ela existe para cobrir não é o ataque — é a Maria clicando em "Continuar sem isso" sem
ler. Encerrar o convite nesse clique poria a perda definitiva do que ela submeteu atrás de um
engano de um segundo, e ela é a usuária mais importante deste fluxo.

E a janela fecha sozinha: assim que a identidade nova tem qualquer inscrição, deixa de haver
"identidade vazia" para descartar, e a operação perde o que a tornava segura.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import (
    CandidateEmail,
    CandidateIdentity,
    novo_subject,
)
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CPF_DE_MARIA = "12345678909"
ANTIGO = "maria.antiga@exemplo.test"
NOVO = "maria.nova@exemplo.test"


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
        email=ANTIGO,
        created_at=timezone.now(),
    )
    return identidade


@pytest.fixture
def vazia():
    return associacao.criar_identidade_com(ANTIGO, ANTIGO)


def test_move_a_credencial_e_descarta_a_identidade_vazia(legada, vazia):
    assert associacao.retomar(vazia=vazia, destino=legada) is True

    assert not CandidateIdentity.objects.filter(pk=vazia.pk).exists()
    assert CandidateEmail.objects.get(email_canonico=ANTIGO).identidade_id == legada.pk


def test_move_todas_as_credenciais_e_nao_so_a_que_correspondia(legada, vazia):
    """Cada uma já foi provada por desafio; mover só uma perderia o que a pessoa comprovou."""
    associacao.associar_credencial(vazia, NOVO, NOVO)

    associacao.retomar(vazia=vazia, destino=legada)

    assert set(
        CandidateEmail.objects.filter(identidade=legada).values_list("email_canonico", flat=True)
    ) == {ANTIGO, NOVO}


def test_a_identidade_de_destino_fica_com_exatamente_uma_principal(legada, vazia):
    associacao.associar_credencial(vazia, NOVO, NOVO)
    associacao.retomar(vazia=vazia, destino=legada)
    assert CandidateEmail.objects.filter(identidade=legada, principal=True).count() == 1


def test_nao_retoma_quando_a_identidade_ja_tem_inscricao(legada, vazia, selecao):
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=vazia.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="",
        cpf="",
        cpf_normalizado="",
        email=ANTIGO,
        created_at=timezone.now(),
    )

    assert associacao.retomar(vazia=vazia, destino=legada) is False
    assert CandidateIdentity.objects.filter(pk=vazia.pk).exists(), "nada se move, nada se descarta"


def test_a_retomada_nao_toca_nenhuma_inscricao(legada, vazia):
    antes = list(Inscricao.objects.values_list("id", "identity_subject", "revision"))
    associacao.retomar(vazia=vazia, destino=legada)
    assert list(Inscricao.objects.values_list("id", "identity_subject", "revision")) == antes


def test_o_convite_so_e_oferecido_a_quem_pode_aceitar(legada, vazia):
    assert associacao.credencial_com_correspondencia(vazia) is not None

    sem_passado = "sem.historico@exemplo.test"
    sozinha = associacao.criar_identidade_com(sem_passado, sem_passado)
    assert associacao.credencial_com_correspondencia(sozinha) is None
