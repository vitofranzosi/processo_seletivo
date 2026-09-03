"""`Minhas Etapas` conta o trabalho que existe — e não o que a Etapa já excluiu.

Sem isto, a Mesa fica corretamente vazia enquanto esta tela anuncia as mesmas inscrições como
pendentes: duas telas dizendo coisas diferentes sobre a mesma Etapa, e quem trabalha acredita na
que promete trabalho.
"""

import pytest

from processo_seletivo.avaliacoes.application.selectors import carga_nas_etapas
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def apos_consolidar(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1510, codigo="1510"
    )
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1510")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    concluir_como(cenario, "joao", inscricoes[1], pontuacao="40")
    # A Etapa 2 recebe as três **antes** da consolidação, quando ela ainda as aceita.
    distribuir_para(
        {**cenario, "etapa": cenario["segunda"]}, gestor, ["joao"], inscricoes, chave="l2-1510"
    )
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[inscricoes[0].id, inscricoes[1].id],
        idempotency_key="k-1510",
        correlation_id="teste",
    )
    cenario["inscricoes"] = inscricoes
    return cenario


def test_a_contagem_da_etapa_seguinte_exclui_quem_nao_participa(apos_consolidar):
    """Três Atribuições ativas, **uma** participante: só a habilitada conta como trabalho."""
    contagens = carga_nas_etapas(
        ator=ator_institucional("joao"),
        atribuicoes=[
            {"edital": apos_consolidar["edital"], "etapa_id": str(apos_consolidar["segunda"])}
        ],
    )
    chave = (apos_consolidar["edital"].id, str(apos_consolidar["segunda"]))
    assert contagens[chave]["total"] == 1
    assert contagens[chave]["pendentes"] == 1


def test_a_primeira_etapa_continua_contando_todas(apos_consolidar):
    """Não há Etapa anterior: a contagem da 012 fica exatamente como estava."""
    contagens = carga_nas_etapas(
        ator=ator_institucional("joao"),
        atribuicoes=[
            {"edital": apos_consolidar["edital"], "etapa_id": str(apos_consolidar["primeira"])}
        ],
    )
    chave = (apos_consolidar["edital"].id, str(apos_consolidar["primeira"]))
    assert contagens[chave]["total"] == 3
    assert contagens[chave]["concluidas"] == 2
