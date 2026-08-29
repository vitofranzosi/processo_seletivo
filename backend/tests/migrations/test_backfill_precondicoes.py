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
    """Estado final é imutável: reescrevê-lo seria falsificar ato já produzido.

    A Retificação é esvaziada **antes** de virar final, porque depois disso nem o teste consegue
    tocá-la — a trigger da migração `0007` recusa. Feita final, o backfill roda e a deixa como
    está, que é o que se quer demonstrar.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": "/profiles/0/name", "operation": "REPLACE", "newValue": "Outro"}],
    )
    _apagar_precondicoes(retificacao.id)
    Retificacao.objects.filter(pk=retificacao.pk).update(status=Retificacao.Status.CANCELADA)

    backfill(registro_de_modelos, None)

    intocada = AlteracaoNormativa.objects.get(retificacao=retificacao)
    assert intocada.expected_previous_hash == ""
    assert intocada.expected_anchors == {}


CONTEUDO = {
    "title": "Original",
    "description": "Texto",
    "rules": {"a": 1, "b": {"c": 2}},
    "profiles": [
        {"id": "id-1", "code": "P1", "name": "A", "requirements": ["x", "y"]},
        {"id": "id-2", "code": "P2", "name": "B", "requirements": []},
    ],
    "schedule": [{"type": "INSCRICAO", "startAt": "2026-09-01T09:00:00-03:00"}],
}

CASOS = [
    [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Novo"}],
    [{"targetPath": "/rules/b/c", "operation": "REPLACE", "newValue": 9}],
    [{"targetPath": "/profiles/1/name", "operation": "REPLACE", "newValue": "Renomeado"}],
    [{"targetPath": "/profiles/0/requirements/1", "operation": "REPLACE", "newValue": "z"}],
    [{"targetPath": "/profiles/0", "operation": "REMOVE"}],
    [{"targetPath": "/description", "operation": "REMOVE"}],
    [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": {"id": "id-3"}}],
    [{"targetPath": "/profiles/0", "operation": "ADD", "newValue": {"id": "id-0"}}],
    [{"targetPath": "/anexo", "operation": "ADD", "newValue": {"a": 1}}],
    # Sequência: remover desloca, e a derivação seguinte parte do conteúdo já alterado.
    [
        {"targetPath": "/profiles/0", "operation": "REMOVE"},
        {"targetPath": "/profiles/0/name", "operation": "REPLACE", "newValue": "Depois"},
    ],
    # Remover e recriar o mesmo caminho no mesmo ato.
    [
        {"targetPath": "/rules", "operation": "REMOVE"},
        {"targetPath": "/rules", "operation": "ADD", "newValue": {"a": 3}},
    ],
    # Hash declarado prevalece sobre o derivado.
    [
        {
            "targetPath": "/title",
            "operation": "REPLACE",
            "newValue": "Novo",
            "expectedPreviousHash": "declarado-pelo-cliente",
        }
    ],
    # Caminho inaplicável: a derivação para e o restante fica vazio.
    [
        {"targetPath": "/inexistente/0/x", "operation": "REPLACE", "newValue": 1},
        {"targetPath": "/title", "operation": "REPLACE", "newValue": "Nunca chega"},
    ],
]


@pytest.mark.parametrize("changes", CASOS, ids=range(len(CASOS)))
def test_a_copia_congelada_produz_o_mesmo_que_a_regra_viva(changes):
    """A duplicação da migração `0006` só é aceitável enquanto não divergir.

    O teste de backfill sozinho exercita um caso; estes cobrem as formas que a derivação
    encontra em conteúdo real — lista, objeto aninhado, remoção que desloca índice, acréscimo no
    fim, hash declarado e caminho inaplicável. Divergência entre a cópia e o domínio aparece
    aqui, não em produção sobre dados de gente.
    """
    from processo_seletivo.publicacoes.domain.conflicts import derive_preconditions

    congelada = import_module(
        "processo_seletivo.publicacoes.migrations.0006_backfill_precondicoes"
    )._derive_preconditions

    assert congelada(CONTEUDO, changes) == derive_preconditions(CONTEUDO, changes)
