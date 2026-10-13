"""A Publicação registra com que redação o documento foi composto (069, FR-1397, R-004).

A página do ato de ordenação **reconstrói** a frase do desempate na hora de exibir. Um ato publicado
antes da `069` não pode passar a dizer uma frase que nunca publicou, e por isso a redação é
**identificável** — gravada no ato, e não deduzida de uma data de corte ou dos bytes do documento.

- a Publicação de um Edital e a de uma Retificação gravam a redação vigente, a 2;
- a Publicação que já existia quando a coluna chegou lê a 1, pelo padrão da migration;
- a coluna não muda depois: a tabela é append-only, pelo modelo e pelo gatilho.
"""

import pytest
from django.db import DatabaseError, connection, transaction
from django.db.migrations.executor import MigrationExecutor

from processo_seletivo.publicacoes.domain.vocabulario_da_regra import REDACAO_1, REDACAO_2
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original, retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e migration validados em PostgreSQL"
)


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


def test_a_publicacao_do_edital_grava_a_redacao_vigente(publicado):
    publicacao = Publicacao.objects.get(edital=publicado)

    assert publicacao.redacao_do_documento == REDACAO_2


def test_a_publicacao_da_retificacao_grava_a_redacao_vigente(api_client, publicado):
    base = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")
    secao = next(item for item in base.content["sections"] if item["key"] == "recursos")
    retify(
        api_client,
        publicado,
        [
            {
                "targetPath": f"/sections/id={secao['id']}/content",
                "operation": "REPLACE",
                "newValue": "Recurso em dois dias úteis.",
                "expectedPreviousHash": _hash_anterior(base.content, secao["id"]),
            }
        ],
        suffix="redacao",
    )

    ordens = list(
        Publicacao.objects.filter(edital=publicado)
        .order_by("publication_order")
        .values_list("redacao_do_documento", flat=True)
    )
    assert ordens == [REDACAO_2, REDACAO_2]


def _hash_anterior(conteudo, secao_id):
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash

    return previous_hash(conteudo, f"/sections/id={secao_id}/content")


def test_o_modelo_recusa_mudar_a_redacao_depois(publicado):
    publicacao = Publicacao.objects.get(edital=publicado)
    publicacao.redacao_do_documento = REDACAO_1

    with pytest.raises(TypeError, match="append-only"):
        publicacao.save()


@postgresql_only
def test_o_gatilho_recusa_mudar_a_redacao_depois(publicado):
    """A segunda camada: um `UPDATE` que contorne o modelo é recusado pelo banco."""
    with pytest.raises(DatabaseError), transaction.atomic():
        Publicacao.objects.filter(edital=publicado).update(redacao_do_documento=REDACAO_1)

    assert Publicacao.objects.get(edital=publicado).redacao_do_documento == REDACAO_2


@postgresql_only
def test_a_publicacao_que_ja_existia_le_a_redacao_1(publicado):
    """A coluna chega com o padrão 1: toda Publicação anterior a ela foi composta na redação 1.

    Desfaz a `0011` e a refaz sobre a Publicação gravada, como uma instalação que já tinha atos
    publicados. `ADD COLUMN` com padrão constante não reescreve linha, e o gatilho append-only não
    dispara.
    """
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    publicacoes = sorted(
        name for app, name in executor.loader.disk_migrations if app == "publicacoes"
    )
    alvo = "0011_redacao_do_documento"
    anterior = publicacoes[publicacoes.index(alvo) - 1]
    try:
        executor.migrate([("publicacoes", anterior)])
        executor.loader.build_graph()
        executor.migrate([("publicacoes", alvo)])
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT redacao_do_documento FROM publicacoes_publicacao WHERE edital_id = %s",
                [str(publicado.id)],
            )
            ((redacao,),) = cursor.fetchall()
    finally:
        executor.loader.build_graph()
        completos = [node for node in executor.loader.graph.leaf_nodes()]
        executor.migrate(completos)

    assert redacao == REDACAO_1
