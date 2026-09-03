"""T046 — distribuir inscrição excluída é **erro do pedido**, e não recusa de linha.

A classificação é a mesma que `_inscricoes_atribuiveis` já aplicava a inscrição não submetida, e o
motivo também: uma seleção que a tela não deveria ter oferecido não é o caminho normal esbarrando
numa regra. Responder "0 distribuídas" a ela faria a tela afirmar um ato que não aconteceu.
"""

import pytest

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.contract, pytest.mark.django_db]


@pytest.fixture
def com_eliminada(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1410, codigo="1410"
    )
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1410")
    for inscricao, nota in zip(inscricoes, ("75", "40"), strict=True):
        concluir_como(cenario, "joao", inscricao, pontuacao=nota)
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="k-1410",
        correlation_id="teste",
    )
    cenario["habilitada"], cenario["eliminada"] = inscricoes
    return cenario


def distribuir_na_segunda(cenario, gestor, inscricoes, *, chave):
    return distribuir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["segunda"],
        membro_ids=[cenario["membros"]["joao"].id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_a_eliminada_recusa_o_pedido_inteiro(com_eliminada, gestor):
    antes = Atribuicao.objects.filter(etapa_id=com_eliminada["segunda"]).count()
    with pytest.raises(DomainError) as recusa:
        distribuir_na_segunda(com_eliminada, gestor, [com_eliminada["eliminada"]], chave="d1")
    assert recusa.value.code == "inscricao_fora_da_etapa"
    assert recusa.value.status == 422
    # Nenhuma Atribuição criada: erro do pedido desfaz o lote inteiro.
    assert Atribuicao.objects.filter(etapa_id=com_eliminada["segunda"]).count() == antes


def test_a_selecao_mista_tambem_recusa_o_pedido_inteiro(com_eliminada, gestor):
    """Distribuir a parte válida seria adivinhar a intenção de quem selecionou errado."""
    with pytest.raises(DomainError) as recusa:
        distribuir_na_segunda(
            com_eliminada,
            gestor,
            [com_eliminada["habilitada"], com_eliminada["eliminada"]],
            chave="d2",
        )
    assert recusa.value.code == "inscricao_fora_da_etapa"
    assert Atribuicao.objects.filter(etapa_id=com_eliminada["segunda"]).count() == 0


def test_a_habilitada_continua_distribuivel(com_eliminada, gestor):
    """A não regressão que acompanha a recusa: o caminho legítimo não fechou junto."""
    desfecho = distribuir_na_segunda(
        com_eliminada, gestor, [com_eliminada["habilitada"]], chave="d3"
    )
    assert desfecho["feitas"] == 1
