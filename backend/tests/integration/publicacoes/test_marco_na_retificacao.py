"""O marco atravessa a Retificação, e a Retificação o protege (015, D-001).

Duas provas de naturezas opostas. A primeira é a que a spec cobra por extenso: **remover a Etapa
que um marco enumera, sem ajustar o marco, não publica**. É esse impedimento que faz o "critério
pendurado" não ser estado que alguma tela precise tratar depois — o caso real de não
recomputabilidade é a remoção do marco, e não a da Etapa (FR-043).

A segunda é a que o desenho da ordem publicada existe para sustentar: **reordenar critérios
preserva os identificadores**. Se a Retificação substituísse a lista inteira, os `id` mudariam a
cada reordenação, e a identidade que ela usa para endereçar deixaria de designar o mesmo critério
(FR-015).
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    publish_retification,
)
from tests.fixtures.snapshot import ETAPA, PERFIL, rascunho_com_etapas

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MARCO = "00000000-0000-0000-0000-000000000541"
CRITERIOS = (
    "00000000-0000-0000-0000-000000000551",
    "00000000-0000-0000-0000-000000000552",
)


def criterio(identificador, ordem):
    return {
        "id": identificador,
        "order": ordem,
        "type": "MAIOR_PONTUACAO_NA_ETAPA",
        "parameters": {"stageId": ETAPA["A"]},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    }


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    """Um Edital publicado com um marco que enumera a primeira Etapa e tem dois critérios."""
    rascunho = rascunho_com_etapas()
    perfil = next(item for item in rascunho["profiles"] if item["id"] == PERFIL["B"])
    perfil["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [ETAPA["A"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "tiebreakers": [criterio(CRITERIOS[0], 1), criterio(CRITERIOS[1], 2)],
        }
    ]
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def marco_publicado(edital):
    perfil = next(item for item in vigente(edital).content["profiles"] if item["id"] == PERFIL["B"])
    return perfil["classificationMilestones"][0]


def test_o_marco_publicado_carrega_os_criterios_na_ordem_declarada(publicado):
    """A contraprova: sem ela, os dois testes abaixo poderiam passar sobre conteúdo vazio."""
    marco = marco_publicado(publicado)

    assert [criterio["id"] for criterio in marco["tiebreakers"]] == list(CRITERIOS)
    assert [criterio["order"] for criterio in marco["tiebreakers"]] == [1, 2]


def test_remover_a_etapa_enumerada_sem_ajustar_o_marco_e_recusado(api_client, publicado):
    """E a recusa acontece **na elaboração do ato**, não na publicação dele.

    A primeira redação deste teste esperava a recusa ao publicar, e o sistema recusou antes: a
    verificação de conteúdo roda sobre o que a Retificação *produziria*, de modo que o erro chega a
    quem está elaborando, e não a quem vai assinar. É o momento certo, e vale estar afirmado — se
    algum dia a recusa migrar para a publicação, este teste denuncia a mudança em vez de continuar
    passando por outro motivo.
    """
    base = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")

    recusa = api_client.post(
        f"/api/v1/admin/editais/{publicado.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Remover a Etapa sem ajustar o marco",
            "changes": [{"targetPath": f"/stages/id={ETAPA['A']}", "operation": "REMOVE"}],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key="retificacao-x-0001"),
    )

    assert recusa.status_code == 422, recusa.content
    assert "marco classificatório enumera uma Etapa que não existe" in recusa.json()["detail"]
    assert marco_publicado(publicado)["stages"] == [ETAPA["A"]]


def test_reordenar_criterios_preserva_os_identificadores(api_client, publicado):
    troca = [
        {
            "targetPath": f"/profiles/id={PERFIL['B']}/classificationMilestones/id={MARCO}"
            f"/tiebreakers/id={CRITERIOS[1]}/order",
            "operation": "REPLACE",
            "newValue": 1,
        },
        {
            "targetPath": f"/profiles/id={PERFIL['B']}/classificationMilestones/id={MARCO}"
            f"/tiebreakers/id={CRITERIOS[0]}/order",
            "operation": "REPLACE",
            "newValue": 2,
        },
    ]

    publish_retification(api_client, create_retification(api_client, publicado, troca))

    tiebreakers = marco_publicado(publicado)["tiebreakers"]
    ordem_por_id = {criterio["id"]: criterio["order"] for criterio in tiebreakers}
    assert ordem_por_id == {CRITERIOS[1]: 1, CRITERIOS[0]: 2}
    assert set(ordem_por_id) == set(CRITERIOS), "os identificadores são os mesmos de antes"


def test_o_snapshot_publicado_com_marco_e_inteiramente_enderecavel(publicado):
    """O único guarda que enxerga coleção aninhada esquecida, sobre conteúdo real (015, T-009).

    `test_forma_publicada` só varre a **raiz** do conteúdo, e `test_colecoes` varre uma fixture. Uma
    coleção nova dentro do Perfil passaria pelos dois sem ser notada; aqui ela não passa, porque a
    varredura é recursiva e o snapshot é o que o sistema efetivamente materializou.

    Vale para os três níveis que a `015` acrescentou: os fatos declarados, os marcos e os critérios
    dentro deles — este último é o que a primeira redação de `COLECOES_COM_CHAVE` tinha esquecido.
    """
    from tests.fixtures.snapshot import colecoes_nao_declaradas, elementos_sem_chave

    conteudo = vigente(publicado).content

    assert colecoes_nao_declaradas(conteudo) == []
    assert elementos_sem_chave(conteudo) == []
    assert marco_publicado(publicado)["tiebreakers"], "o guarda precisa de critérios para valer"
