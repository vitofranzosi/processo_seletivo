"""O alvo anotado decide a confirmação — e sobreviver ao descarte da identidade é do modelo.

Duas correções de revisão vivem aqui. A primeira: o campo era gravado e nunca lido, e o comentário
prometia uma garantia que ninguém impunha. A segunda: ele apagava desafios em cascata, o que
levaria junto o contador de tentativas de CPF — registro de segurança.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import (
    CandidateIdentity,
    DesafioDeAcesso,
    novo_subject,
)
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
CPF_DE_MARIA = "12345678909"
CPF_DE_JOAO = "98765432100"


def legada(selecao, cpf, email=ENDERECO, perfil=PERFIL_DOCENTE):
    identidade = CandidateIdentity.objects.create(
        subject=novo_subject(), nome="Alguém", cpf_normalizado=cpf, created_at=timezone.now()
    )
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=identidade.subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome="Alguém",
        cpf=cpf,
        cpf_normalizado=cpf,
        email=email,
        created_at=timezone.now(),
    )
    return identidade


def test_o_alvo_anotado_decide_a_confirmacao(selecao, desafio_consumido):
    """Uma única candidata: o alvo é anotado, e é contra ele que o CPF confere."""
    alvo = legada(selecao, CPF_DE_MARIA)
    associacao.abrir_reconciliacao(desafio_consumido, [alvo])
    desafio_consumido.refresh_from_db()

    assert desafio_consumido.reconciliacao_alvo_id == alvo.pk
    assert associacao.confirmar_cpf(desafio_consumido, CPF_DE_MARIA).pk == alvo.pk


def test_uma_candidata_nova_nao_desvia_o_convite_ja_aberto(selecao, desafio_consumido):
    """O conjunto de candidatas não muda sob um desafio já aberto.

    Antes, `confirmar_cpf` refazia a busca: uma inscrição criada noutra sessão entre a abertura do
    convite e a confirmação entrava no conjunto, e a identidade reconciliada podia não ser a que o
    convite anunciou.
    """
    alvo = legada(selecao, CPF_DE_MARIA)
    associacao.abrir_reconciliacao(desafio_consumido, [alvo])
    desafio_consumido.refresh_from_db()

    intrusa = legada(selecao, CPF_DE_JOAO, perfil=PERFIL_TECNICO)

    assert associacao.confirmar_cpf(desafio_consumido, CPF_DE_JOAO) is None
    assert CandidateIdentity.objects.filter(pk=intrusa.pk).exists()


def test_com_mais_de_uma_candidata_o_cpf_desempata(selecao, desafio_consumido):
    """Nenhum alvo é anotado quando há ambiguidade — escolher ali seria escolher antes de saber."""
    de_maria = legada(selecao, CPF_DE_MARIA)
    de_joao = legada(selecao, CPF_DE_JOAO, perfil=PERFIL_TECNICO)
    associacao.abrir_reconciliacao(desafio_consumido, [de_maria, de_joao])
    desafio_consumido.refresh_from_db()

    assert desafio_consumido.reconciliacao_alvo_id is None
    assert associacao.confirmar_cpf(desafio_consumido, CPF_DE_JOAO).pk == de_joao.pk


def test_descartar_a_identidade_alvo_nao_apaga_o_desafio(selecao, desafio_consumido):
    """A anotação deixa de valer; o desafio — e o que ele conta — permanece."""
    alvo = legada(selecao, CPF_DE_MARIA)
    associacao.abrir_reconciliacao(desafio_consumido, [alvo])
    associacao.confirmar_cpf(desafio_consumido, "111.222.333-44")

    Inscricao.objects.filter(identity_subject=alvo.subject).delete()
    alvo.delete()

    sobrevivente = DesafioDeAcesso.objects.filter(pk=desafio_consumido.pk).first()
    assert sobrevivente is not None, "o desafio não pode sumir junto com a anotação"
    assert sobrevivente.reconciliacao_alvo_id is None
    assert sobrevivente.tentativas_cpf == 1, "o contador de tentativas é registro de segurança"
