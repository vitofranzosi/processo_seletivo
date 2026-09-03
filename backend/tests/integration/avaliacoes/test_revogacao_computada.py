"""A revogação é computada, e nunca desnormalizada (FR-069, D-004).

Mil inscrições com dupla avaliação são duas mil atribuições. Se retirar alguém de uma Etapa
exigisse marcar as atribuições dele, o ato custaria centenas de escritas — e, pior, a correção do
engano custaria outras tantas. A conjunção avaliada a cada acesso resolve os dois: nenhum ato da
011 escreve aqui, e devolver a alocação restaura o acesso às **mesmas** linhas.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.comissoes.application.alocacao import alocar, remover_alocacao
from processo_seletivo.comissoes.application.comissao import remover_membro
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, inscrever

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def trabalho(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    membro = comissao_de_a["joao"]
    alocacao = alocar_em(gestor, processo_a, membro, edital_a, etapa_a1)
    inscricoes = inscrever(edital_a, 3)
    distribuir(
        actor=gestor,
        processo_id=processo_a.id,
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        membro_ids=[membro.id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="trabalho",
        correlation_id="teste",
    )
    return {"membro": membro, "alocacao": alocacao, "inscricoes": inscricoes}


def escritas_em_atribuicao(consultas):
    return [
        c["sql"]
        for c in consultas
        if "avaliacoes_atribuicao" in c["sql"]
        and any(c["sql"].lstrip().upper().startswith(v) for v in ("UPDATE", "INSERT", "DELETE"))
    ]


def test_remover_a_alocacao_nao_escreve_em_atribuicao(gestor, processo_a, trabalho):
    with CaptureQueriesContext(connection) as consultas:
        remover_alocacao(
            actor=gestor,
            processo_id=processo_a.id,
            alocacao_id=trabalho["alocacao"].id,
            idempotency_key="tirar",
            correlation_id="teste",
        )

    assert escritas_em_atribuicao(consultas.captured_queries) == []
    assert Atribuicao.objects.filter(ativo=True).count() == 3


def test_remover_o_membro_tambem_nao_escreve_em_atribuicao(gestor, processo_a, trabalho):
    """Remover da comissão inativa as alocações — e para por aí (011, e FR-069 aqui)."""
    with CaptureQueriesContext(connection) as consultas:
        remover_membro(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=trabalho["membro"].id,
            idempotency_key="remover-membro",
            correlation_id="teste",
        )

    assert escritas_em_atribuicao(consultas.captured_queries) == []
    assert Atribuicao.objects.filter(ativo=True).count() == 3


def test_a_conjuncao_e_que_revoga_e_que_restaura(gestor, processo_a, edital_a, etapa_a1, trabalho):
    joao = ator_institucional("joao")
    inscricao = trabalho["inscricoes"][0]
    assert pode_avaliar_inscricao(joao, edital_a, etapa_a1, inscricao.id) is not None

    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=trabalho["alocacao"].id,
        idempotency_key="tirar",
        correlation_id="teste",
    )
    revogado = pode_avaliar_inscricao(joao, edital_a, etapa_a1, inscricao.id)

    alocar(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=trabalho["membro"].id,
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        idempotency_key="devolver",
        correlation_id="teste",
    )

    assert revogado is None
    assert pode_avaliar_inscricao(joao, edital_a, etapa_a1, inscricao.id) is not None


def test_etapa_fora_da_versao_vigente_nao_concede_acesso(
    api_client, gestor, processo_a, edital_a, etapa_a1, trabalho
):
    """EC-011, pela mesma regra da alocação órfã.

    A Etapa que a Retificação removeu deixa de existir no conteúdo vigente, e a Atribuição sobre
    ela deixa de conceder acesso — sem que nenhuma linha daqui seja tocada. A Avaliação registrada
    permanece, porque é registro do que foi afirmado (EC-004).
    """
    from tests.fixtures.publicacao import create_retification, publish_retification

    joao = ator_institucional("joao")
    inscricao = trabalho["inscricoes"][0]
    assert pode_avaliar_inscricao(joao, edital_a, etapa_a1, inscricao.id) is not None

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital_a,
            [{"targetPath": f"/stages/id={etapa_a1}", "operation": "REMOVE"}],
        ),
        suffix="a",
    )

    assert pode_avaliar_inscricao(joao, edital_a, etapa_a1, inscricao.id) is None
    assert Atribuicao.objects.filter(ativo=True).count() == 3
