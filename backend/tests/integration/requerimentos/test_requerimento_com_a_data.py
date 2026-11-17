"""O requerimento de matrícula nasce com a data do cadastro (180, D-003, FR-8313, SC-2907; R6).

Ponto de partida, e não verdade imposta: só na criação, alterável ali, sem tocar o cadastro.
"""

from datetime import date

import pytest

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.requerimentos.application import preencher
from tests.fixtures.candidato import MARIA, NASCIMENTO_PADRAO
from tests.fixtures.requerimento import pronta_para_enviar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def inscricao(selecao_na_inscricao, candidatos_registrados):
    return pronta_para_enviar(selecao_na_inscricao)


def _cadastro():
    return CandidateIdentity.objects.get(subject=MARIA.subject)


def test_nasce_com_a_data_do_cadastro(inscricao):
    rascunho = preencher.abrir_rascunho(inscricao=inscricao)
    assert rascunho.data_de_nascimento == NASCIMENTO_PADRAO


def test_cadastro_sem_data_deixa_o_campo_vazio(inscricao):
    CandidateIdentity.objects.filter(subject=MARIA.subject).update(data_nascimento=None)
    rascunho = preencher.abrir_rascunho(inscricao=inscricao)
    assert rascunho.data_de_nascimento is None


def test_alterar_no_requerimento_nao_muda_o_cadastro(inscricao):
    rascunho = preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(
        inscricao=inscricao,
        dados={"data_de_nascimento": "1990-05-04"},
        expected_revision=rascunho.revision,
    )

    assert preencher.vigente_de(inscricao).data_de_nascimento == date(1990, 5, 4)
    assert _cadastro().data_nascimento == NASCIMENTO_PADRAO


def test_reabrir_nao_sobrescreve_a_correcao(inscricao):
    rascunho = preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(
        inscricao=inscricao,
        dados={"data_de_nascimento": "1990-05-04"},
        expected_revision=rascunho.revision,
    )

    reaberto = preencher.abrir_rascunho(inscricao=inscricao)

    assert reaberto.data_de_nascimento == date(1990, 5, 4)
