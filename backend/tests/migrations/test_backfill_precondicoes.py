"""A migração 0006 reconstrói a precondição das Retificações elaboradas antes dela.

Retificação em curso sem precondição publica sem verificação alguma — é o estado em que ficam
todas as que existirem no momento da implantação. O backfill não adivinha: recalcula da base
declarada e da sequência ordenada de alterações, que é o mesmo insumo da elaboração.
"""

from importlib import import_module

import pytest
from django.apps import apps as registro_de_modelos

from processo_seletivo.publicacoes.models_retificacao import AlteracaoNormativa, Retificacao
from tests.fixtures.publicacao import create_retification, publish_original

backfill = import_module(
    "processo_seletivo.publicacoes.migrations.0006_backfill_precondicoes"
).preencher


def _apagar_precondicoes(retificacao_id):
    AlteracaoNormativa.objects.filter(retificacao_id=retificacao_id).update(
        expected_previous_hash="", expected_anchors={}
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_backfill_recalcula_a_precondicao_de_retificacao_em_curso(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": "/profiles/0/name", "operation": "REPLACE", "newValue": "Outro"}],
    )
    esperado = list(
        AlteracaoNormativa.objects.filter(retificacao=retificacao).values_list(
            "expected_previous_hash", "expected_anchors"
        )
    )
    assert esperado[0][1], "a elaboração já deve derivar âncora — o backfill precisa reproduzi-la"
    _apagar_precondicoes(retificacao.id)

    backfill(registro_de_modelos, None)

    obtido = list(
        AlteracaoNormativa.objects.filter(retificacao=retificacao).values_list(
            "expected_previous_hash", "expected_anchors"
        )
    )
    assert obtido == esperado


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_backfill_nao_toca_retificacao_publicada(
    api_client, manager_headers, process_payload
):
    """Publicada é final e imutável: reescrevê-la seria falsificar histórico já produzido."""
    from tests.fixtures.publicacao import publish_retification

    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": "/profiles/0/name", "operation": "REPLACE", "newValue": "Outro"}],
    )
    publish_retification(api_client, retificacao, suffix="a")
    assert Retificacao.objects.get(pk=retificacao.pk).status == Retificacao.Status.PUBLICADA
    _apagar_precondicoes(retificacao.id)

    backfill(registro_de_modelos, None)

    intocada = AlteracaoNormativa.objects.get(retificacao=retificacao)
    assert intocada.expected_previous_hash == ""
    assert intocada.expected_anchors == {}
