"""O Pulso: a soma acima do Edital, e o tempo acima de todos.

A capacidade que hoje não existe em nível nenhum. Um Processo com três Editais não tem, em lugar
algum, quantas inscrições recebeu — e é isso que a `US1` entrega sozinha.
"""

import pytest

from processo_seletivo.interface import supervisao
from tests.fixtures.supervisao import rascunhar, submeter

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def do_edital(pulso, edital):
    return next(item for item in pulso.por_edital if item.edital.id == edital.id)


def test_o_total_do_processo_e_a_soma_dos_editais(processo_a, edital_a, edital_c):
    """`FR-010` e `SC-002`: o número da supervisão é o que as duas telas de inscrição somam."""
    submeter(edital_a, 5)
    submeter(edital_c, 3, seed=2)

    lido = supervisao.pulso(processo_a)

    assert lido.submetidas_no_processo == 8
    assert do_edital(lido, edital_a).submetidas == 5
    assert do_edital(lido, edital_c).submetidas == 3


def test_cada_edital_aparece_nomeado_inclusive_o_de_zero_inscricoes(processo_a, edital_a, edital_c):
    """`FR-011` e `SC-007`: zero é resposta, e é apresentada como tal.

    O Edital sem inscrição alguma continua na leitura — some-lo da lista faria a soma parecer
    completa quando ela cobre menos Editais do que o Processo tem.
    """
    submeter(edital_a, 2)

    lido = supervisao.pulso(processo_a)

    nomeados = {(item.edital.number, item.edital.year) for item in lido.por_edital}
    assert nomeados == {
        (edital_a.number, edital_a.year),
        (edital_c.number, edital_c.year),
    }
    assert do_edital(lido, edital_c).submetidas == 0


def test_o_rascunho_nao_soma_ao_total_de_submetidas(processo_a, edital_a, edital_c):
    """`FR-012` e `SC-003`: duas grandezas, e nunca uma."""
    submeter(edital_a, 4)
    rascunhar(edital_a, 3)
    rascunhar(edital_c, 2, seed=2)

    lido = supervisao.pulso(processo_a)

    assert lido.submetidas_no_processo == 4
    assert lido.rascunhos_no_processo == 5
    assert do_edital(lido, edital_a).rascunhos == 3
    assert do_edital(lido, edital_c).rascunhos == 2


def test_o_instante_da_leitura_acompanha_os_indicadores(processo_a, edital_a, edital_c):
    """`FR-009`: o contrato é o instante lido, e não a tecnologia de atualização."""
    from django.utils import timezone

    antes = timezone.now()

    lido = supervisao.pulso(processo_a)

    assert antes <= lido.lido_em <= timezone.now()
