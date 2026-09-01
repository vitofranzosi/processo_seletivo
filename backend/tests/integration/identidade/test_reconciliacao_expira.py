"""A reconciliação pendente expira dez minutos depois do consumo — e expirar não é ficar sem saída.

FR-052b. O prazo é o mesmo do código, e por decisão: duas durações diferentes seriam duas
explicações a dar, e nenhuma delas melhoraria nada.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import VALIDADE_EM_MINUTOS, DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_a_reconciliacao_nasce_com_prazo(desafio_consumido):
    alvo = associacao.criar_identidade_com("alvo@exemplo.test", "alvo@exemplo.test")
    associacao.abrir_reconciliacao(desafio_consumido, [alvo])

    prazo = DesafioDeAcesso.objects.get(pk=desafio_consumido.pk).reconciliacao_ate
    esperado = timezone.now() + timedelta(minutes=VALIDADE_EM_MINUTOS)
    assert abs((prazo - esperado).total_seconds()) < 5


def test_pendente_enquanto_dentro_do_prazo(desafio_consumido):
    alvo = associacao.criar_identidade_com("alvo@exemplo.test", "alvo@exemplo.test")
    associacao.abrir_reconciliacao(desafio_consumido, [alvo])
    assert associacao.reconciliacao_pendente(desafio_consumido)


def test_deixa_de_estar_pendente_depois_do_prazo(desafio_consumido):
    alvo = associacao.criar_identidade_com("alvo@exemplo.test", "alvo@exemplo.test")
    associacao.abrir_reconciliacao(desafio_consumido, [alvo])
    DesafioDeAcesso.objects.update(reconciliacao_ate=timezone.now() - timedelta(seconds=1))
    desafio_consumido.refresh_from_db()

    assert not associacao.reconciliacao_pendente(desafio_consumido)


def test_desafio_sem_reconciliacao_nao_esta_pendente(desafio_consumido):
    assert not associacao.reconciliacao_pendente(desafio_consumido)
    assert not associacao.reconciliacao_pendente(None)
