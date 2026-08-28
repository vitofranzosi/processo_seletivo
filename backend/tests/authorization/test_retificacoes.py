import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.integration.publicacoes.test_retificacoes import publish_original


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_retification_requires_explicit_permission(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    response = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Correção",
            "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Novo"}],
        },
        format="json",
        **actor_headers("leitor", ["auditoria:consultar"]),
    )
    assert response.status_code == 403
