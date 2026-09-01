"""Duas confirmações simultâneas do mesmo endereço produzem uma credencial (FR-011, SC-015).

A exclusividade é do banco, e não de uma consulta prévia. Verificar antes de gravar perde a corrida
entre as duas — e o que se perde nessa corrida é a exclusividade de uma credencial, que é o que
impede um endereço autenticar duas identidades.
"""

import threading

import pytest
from django.db import connections

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateEmail
from tests.conftest import encerrar_conexoes_da_thread

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

DISPUTADO = "disputado@exemplo.test"


def em_paralelo(tarefa, quantidade=6):
    barreira = threading.Barrier(quantidade)
    resultados = []

    def correr():
        try:
            barreira.wait()
            try:
                resultados.append(tarefa())
            except Exception as recusa:
                resultados.append(recusa)
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=correr) for _ in range(quantidade)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join()
    connections.close_all()
    return resultados


def test_seis_criacoes_simultaneas_produzem_uma_credencial():
    em_paralelo(lambda: associacao.criar_identidade_com(DISPUTADO, DISPUTADO))

    assert CandidateEmail.objects.filter(email_canonico=DISPUTADO).count() == 1


def test_todas_terminam_na_mesma_identidade():
    """Perder a corrida não é erro: quem chega depois entra na identidade que passou a existir."""
    resultados = em_paralelo(lambda: associacao.criar_identidade_com(DISPUTADO, DISPUTADO))

    identidades = {r.pk for r in resultados if not isinstance(r, Exception)}
    assert len(identidades) == 1, "todas devolvem a mesma identidade"
    assert not [r for r in resultados if isinstance(r, Exception)], "e nenhuma estoura"


def test_adicionar_o_mesmo_endereco_a_duas_identidades_falha_no_banco():
    uma = associacao.criar_identidade_com("uma@exemplo.test", "uma@exemplo.test")
    outra = associacao.criar_identidade_com("outra@exemplo.test", "outra@exemplo.test")
    associacao.associar_credencial(uma, DISPUTADO, DISPUTADO)

    from django.db import IntegrityError, transaction

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            associacao.associar_credencial(outra, DISPUTADO, DISPUTADO)
