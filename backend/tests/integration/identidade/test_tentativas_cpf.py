"""As tentativas de confirmar o CPF: cinco, contadas no desafio, e nunca contra o alvo.

Três propriedades, e cada uma existe contra um erro concreto de desenho.

**Cinco** (FR-052a). CPF não é segredo, mas cinco tentativas por desafio, com desafios limitados
por endereço e por origem, é a composição que impede varredura.

**No desafio, e não na sessão** (D-016). Uma aba nova zeraria um contador de sessão — e aba nova é
exatamente o caminho de quem está adivinhando.

**Nunca no alvo** (FR-052c). Um contador preso à identidade alvo deixaria um terceiro esgotar as
tentativas e **impedir o titular legítimo de reconciliar**. É a mesma classe de bloqueio que a
FR-036 e a FR-064 foram escritas para evitar, e seria a mais fácil de introduzir sem perceber.
"""

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import (
    TETO_DE_TENTATIVAS,
    CandidateIdentity,
    DesafioDeAcesso,
    novo_subject,
)
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENDERECO = "maria@exemplo.test"
CPF_DE_MARIA = "12345678909"
ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR


@pytest.fixture
def maria_legada(selecao):
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


def desafio_novo(endereco=ENDERECO):
    _, codigo = servico.solicitar(email_canonico=endereco, finalidade=ENTRAR)
    desafio = servico.validar(email_canonico=endereco, finalidade=ENTRAR, codigo=codigo)
    associacao.abrir_reconciliacao(desafio, associacao.correspondencia_historica(endereco))
    return desafio


def afastar_a_espera():
    DesafioDeAcesso.objects.update(criado_em=timezone.now() - timedelta(minutes=5))


def test_cinco_tentativas_e_o_convite_morre(maria_legada):
    desafio = desafio_novo()
    for _ in range(TETO_DE_TENTATIVAS):
        assert associacao.confirmar_cpf(desafio, "111.222.333-44") is None
    assert not associacao.reconciliacao_pendente(desafio)


def test_o_cpf_certo_nao_passa_depois_do_teto(maria_legada):
    desafio = desafio_novo()
    for _ in range(TETO_DE_TENTATIVAS):
        associacao.confirmar_cpf(desafio, "111.222.333-44")
    assert associacao.confirmar_cpf(desafio, CPF_DE_MARIA) is None


def test_a_contagem_nao_e_zerada_por_uma_aba_nova(maria_legada):
    """O contador vive na linha do desafio, e a linha não sabe o que é uma aba."""
    desafio = desafio_novo()
    associacao.confirmar_cpf(desafio, "111.222.333-44")
    associacao.confirmar_cpf(desafio, "111.222.333-44")

    relido = DesafioDeAcesso.objects.get(pk=desafio.pk)
    assert relido.tentativas_cpf == 2


def test_tentativas_de_terceiro_nao_impedem_o_titular(maria_legada):
    """A propriedade que mais importa: o contador incide sobre quem tenta, não sobre o alvo.

    O terceiro esgota o desafio **dele**. Quando Maria chega, com o desafio **dela**, reconcilia
    normalmente — porque a identidade que ele atacou nunca teve contador nenhum.
    """
    do_terceiro = desafio_novo()
    for _ in range(TETO_DE_TENTATIVAS):
        associacao.confirmar_cpf(do_terceiro, "111.222.333-44")
    assert not associacao.reconciliacao_pendente(do_terceiro)

    afastar_a_espera()
    da_maria = desafio_novo()
    assert associacao.confirmar_cpf(da_maria, CPF_DE_MARIA) is not None


def test_o_alvo_nao_guarda_contador(maria_legada):
    desafio = desafio_novo()
    for _ in range(TETO_DE_TENTATIVAS):
        associacao.confirmar_cpf(desafio, "111.222.333-44")
    maria_legada.refresh_from_db()
    assert not hasattr(maria_legada, "tentativas"), "o alvo não pode carregar estado de ataque"
