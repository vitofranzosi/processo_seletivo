"""Quem pode fazer o quê com o Anexo depois de publicado (020, FR-037).

**São cinco capacidades, e de papéis distintos** — `retificacao:elaborar`, `:submeter`,
`:homologar`, `:publicar` e `:cancelar` —, declaradas em `interface/identidade.py` e exigidas uma a
uma em `interface/atos_retificacao.py`. A primeira redação da tarefa dizia duas, e pedia as duas do
mesmo ator: isso não é a regra, é uma leitura apressada dela.

O que importa aqui é que **nenhuma é derivada de outra**. Elaborar a substituição do artefato não
dá o poder de submetê-la; homologar não dá o de publicar. É a mesma segregação que a `017` afirmou
para o resultado — emitir constitui, publicar torna público, e são atos de autoridades distintas.
"""

import pytest

from tests.fixtures.anexos import criar_artefato
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import SIGNATORY, create_retification, publish_original
from tests.fixtures.snapshot import rascunho_completo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.authorization]


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


def substituicao(publicado):
    from processo_seletivo.editais.models import AnexoEdital

    anexo = AnexoEdital.objects.get(edital=publicado)
    novo = criar_artefato(marca="Z")
    return [
        {
            "targetPath": f"/attachments/id={anexo.id}/artifactId",
            "operation": "REPLACE",
            "newValue": str(novo.id),
        },
        {
            "targetPath": f"/attachments/id={anexo.id}/artifactHash",
            "operation": "REPLACE",
            "newValue": novo.document_hash,
        },
    ]


def test_elaborar_a_substituicao_exige_a_capacidade_de_elaborar(api_client, publicado):
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    base = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")

    recusa = api_client.post(
        f"/api/v1/admin/editais/{publicado.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Sem a capacidade",
            "changes": substituicao(publicado),
        },
        format="json",
        **actor_headers("intruso", ["edital:elaborar"], key="anexo-sem-permissao-0001"),
    )

    assert recusa.status_code == 403


@pytest.mark.parametrize(
    ("etapa", "capacidade", "outras"),
    [
        ("submissoes", "retificacao:submeter", ["retificacao:elaborar"]),
        ("homologacoes", "retificacao:homologar", ["retificacao:submeter"]),
        ("publicacoes", "retificacao:publicar", ["retificacao:homologar"]),
    ],
)
def test_cada_ato_da_retificacao_exige_a_sua_propria_capacidade(
    api_client, publicado, etapa, capacidade, outras
):
    """Quem tem a capacidade **anterior** não herda a seguinte: é o que "não derivada" significa."""
    retificacao = create_retification(api_client, publicado, substituicao(publicado), suffix="p")

    recusa = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/{etapa}",
        # Corpo **válido**, para que a recusa seja de autorização e não de forma: com payload
        # inválido a resposta seria 422, e o teste estaria provando outra coisa.
        {"reason": "OK", "signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("vizinho", outras, key=f"anexo-{etapa}-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert recusa.status_code == 403, f"{etapa} aceitou quem tem {outras} e não tem {capacidade}"
