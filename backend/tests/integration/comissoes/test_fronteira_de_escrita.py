"""T077a — em runtime, a 011 escreve onde disse que escreveria, e em nada mais.

A migration é conferida em `tests/migrations`. Aqui é o outro lado: nenhum comando pode tocar
`editais` ou `publicacoes`, e nenhum pode mexer em revisão, snapshot ou hash do Edital (FR-069).
"""

import pytest

from processo_seletivo.comissoes.application.alocacao import remover_alocacao
from processo_seletivo.comissoes.application.comissao import alterar_funcao, remover_membro
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import alocar_em

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _retrato(edital):
    edital.refresh_from_db()
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    return {
        "revision": edital.revision,
        "status": edital.status,
        "hash": versao.content_hash,
        "content": versao.content,
        "etapas_de_elaboracao": list(
            edital.etapas.order_by("order").values_list("id", "name", "order")
        ),
    }


def test_os_cinco_comandos_nao_tocam_o_edital(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    antes = _retrato(edital_a)

    joao = comissao_de_a["joao"]
    alocacao = alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a2)
    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=alocacao.id,
        idempotency_key="k1",
        correlation_id="c",
    )
    alterar_funcao(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        funcao="PRESIDENTE",
        idempotency_key="k2",
        correlation_id="c",
    )
    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        idempotency_key="k3",
        correlation_id="c",
    )

    assert _retrato(edital_a) == antes


def test_nenhuma_versao_consolidada_nova_e_criada(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """SC-018: alterar comissão nunca exige Retificação, e nunca produz versão."""
    antes = VersaoConsolidada.objects.count()

    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    assert VersaoConsolidada.objects.count() == antes
