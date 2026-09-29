"""A espécie sai da posição da pessoa, e a informada que diverge é recusada (050).

São a `FR-867` e a `FR-868`.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


def fila(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]


def test_sem_especie_informada_o_titular_e_chamado_para_vaga_inicial(cenario_do_77, gestor):
    edital, _, _ = cenario_do_77

    declarado = convocar(edital, gestor, fila(edital)[0], idempotency_key="deriva-titular")

    assert declarado["especie"] == nomes.VAGA_INICIAL


def test_o_suplente_chamado_para_vaga_inicial_e_recusado(cenario_do_77, gestor):
    """Até a `050`, o ato append-only guardava esse fato falso sem que nada acusasse."""
    edital, _, _ = cenario_do_77
    titular, _, suplente = fila(edital)
    convocada = convocar(edital, gestor, titular, idempotency_key="deriva-t")
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        especie=nomes.DESISTENCIA_EXPRESSA,
        fundamento="Desistiu.",
        idempotency_key="deriva-desiste",
        correlation_id="teste",
    )
    # O segundo titular ainda está à frente; convocá-lo abre caminho à suplente.
    convocar(edital, gestor, fila(edital)[0], idempotency_key="deriva-t2")

    with pytest.raises(DomainError) as recusa:
        convocar(
            edital, gestor, suplente, especie=nomes.VAGA_INICIAL, idempotency_key="deriva-errada"
        )

    assert recusa.value.code == nomes.ESPECIE_DIVERGENTE_DA_POSICAO
    assert "para vaga que vagou" in recusa.value.detail

    certa = convocar(edital, gestor, suplente, idempotency_key="deriva-certa")
    assert certa["especie"] == nomes.SUPLENCIA
    assert Convocacao.objects.count() == 3
