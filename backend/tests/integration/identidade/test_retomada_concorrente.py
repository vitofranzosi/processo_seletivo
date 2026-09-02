"""A retomada e a abertura de rascunho, ao mesmo tempo (FR-055, SC-016, D-010).

`Inscricao` não referencia a identidade por chave estrangeira — e não passa a referenciar, porque a
`010` tem proibição expressa de tocar naquele campo. Sem integridade referencial, nada além do
bloqueio compartilhado impede um rascunho de nascer entre a verificação de "identidade vazia" e o
descarte dela: a inscrição ficaria órfã de uma identidade que deixou de existir, e ninguém a
reencontraria.

Os dois caminhos tomam a mesma linha. O desfecho é sempre um dos dois inteiros, nunca metade.
"""

import threading
import uuid

import pytest
from django.db import connections
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import (
    CandidateEmail,
    CandidateIdentity,
    novo_subject,
)
from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.identidade import contrato_de
from tests.conftest import encerrar_conexoes_da_thread
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CPF_DE_MARIA = "12345678909"
ANTIGO = "maria.antiga@exemplo.test"


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
        email=ANTIGO,
        created_at=timezone.now(),
    )
    return identidade


def test_ou_a_movimentacao_inteira_ou_nenhuma(legada, selecao):
    vazia = associacao.criar_identidade_com(ANTIGO, ANTIGO)
    barreira = threading.Barrier(2)
    resultados = {}

    def retomar():
        try:
            barreira.wait()
            resultados["retomou"] = associacao.retomar(vazia=vazia, destino=legada)
        finally:
            encerrar_conexoes_da_thread()

    def abrir():
        try:
            barreira.wait()
            abrir_inscricao(
                identidade=contrato_de(vazia),
                edital_id=selecao.id,
                profile_id=PERFIL_TECNICO,
            )
            resultados["abriu"] = True
        except Exception as recusa:  # a abertura pode perder legitimamente, e isso é um desfecho
            resultados["abriu"] = recusa
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=retomar), threading.Thread(target=abrir)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join()
    connections.close_all()

    sobrou = CandidateIdentity.objects.filter(pk=vazia.pk).exists()
    if resultados.get("retomou"):
        # Retomou: a identidade sumiu, e nenhuma inscrição pode ter ficado apontando para ela.
        assert not sobrou
        assert not Inscricao.objects.filter(identity_subject=vazia.subject).exists()
        assert CandidateEmail.objects.filter(email_canonico=ANTIGO).count() == 1
    else:
        # Não retomou: nada se moveu, e a identidade continua inteira com a sua credencial.
        assert sobrou
        assert CandidateEmail.objects.get(email_canonico=ANTIGO).identidade_id == vazia.pk


def test_a_inscricao_legada_nunca_muda_de_dono(legada, selecao):
    vazia = associacao.criar_identidade_com(ANTIGO, ANTIGO)
    antes = list(Inscricao.objects.values_list("id", "identity_subject"))
    associacao.retomar(vazia=vazia, destino=legada)
    assert list(Inscricao.objects.values_list("id", "identity_subject")) == antes
