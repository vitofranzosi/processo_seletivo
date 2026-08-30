import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original

GESTOR = ["processo:encerrar", "processo:cancelar", "edital:encerrar", "edital:cancelar"]


@pytest.fixture
def edital_publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db
@pytest.mark.authorization
@pytest.mark.parametrize(
    "rota,permissao",
    [
        ("editais/{edital}/encerramentos", "edital:encerrar"),
        ("editais/{edital}/cancelamentos", "edital:cancelar"),
        ("processos/{processo}/encerramentos", "processo:encerrar"),
        ("processos/{processo}/cancelamentos", "processo:cancelar"),
    ],
)
def test_final_acts_deny_by_default(api_client, edital_publicado, rota, permissao):
    """FR-033: sem a permissão explícita o ato é negado, sem revelar estado."""
    url = "/api/v1/admin/" + rota.format(
        edital=edital_publicado.id, processo=edital_publicado.processo_id
    )
    outras = [item for item in GESTOR if item != permissao]
    response = api_client.post(
        url,
        {"reason": "Tentativa"},
        format="json",
        **actor_headers("intruso", outras, if_match=1),
    )
    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"
    assert Edital.objects.get(pk=edital_publicado.pk).status == Edital.Status.PUBLICADO


@pytest.mark.django_db
@pytest.mark.authorization
def test_final_acts_do_not_cross_institutional_scope(api_client, edital_publicado):
    """Anti-IDOR: identificador válido em outro escopo não concede acesso."""
    response = api_client.post(
        f"/api/v1/admin/editais/{edital_publicado.id}/encerramentos",
        {"reason": "Outro escopo"},
        format="json",
        **{
            "HTTP_AUTHORIZATION": f"Bearer gestor|outra-instituicao|{','.join(GESTOR)}",
            "HTTP_IDEMPOTENCY_KEY": "escopo-key-00000001",
            "HTTP_IF_MATCH": '"5"',
            "HTTP_X_CORRELATION_ID": "escopo",
        },
    )
    assert response.status_code == 404
    assert Edital.objects.get(pk=edital_publicado.pk).status == Edital.Status.PUBLICADO


@pytest.mark.django_db
@pytest.mark.authorization
def test_final_act_audits_actor_reason_and_state_transition(api_client, edital_publicado):
    """FR-032: o ato registra ator, motivo, estados anterior e posterior e a revisão."""
    api_client.post(
        f"/api/v1/admin/editais/{edital_publicado.id}/encerramentos",
        {"reason": "Etapas concluídas"},
        format="json",
        **actor_headers("gestor", GESTOR, if_match=edital_publicado.revision),
    )
    registro = RegistroAuditoria.objects.get(aggregate_id=edital_publicado.id, operation="ENCERRAR")
    assert registro.actor_subject == "gestor"
    assert registro.permission == "edital:encerrar"
    assert registro.previous_state == Edital.Status.PUBLICADO
    assert registro.new_state == Edital.Status.ENCERRADO
    assert registro.previous_revision == edital_publicado.revision
    assert registro.new_revision == edital_publicado.revision + 1
    assert registro.reason == "Etapas concluídas"


@pytest.mark.django_db
@pytest.mark.authorization
def test_finalization_preserves_publications_and_history(api_client, edital_publicado):
    """FR-034: cancelar não é excluir; documentos e consulta pública permanecem."""
    publicacao_url = f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente"
    antes = api_client.get(publicacao_url).json()
    api_client.post(
        f"/api/v1/admin/editais/{edital_publicado.id}/cancelamentos",
        {"reason": "Interrompido"},
        format="json",
        **actor_headers("gestor", GESTOR, if_match=edital_publicado.revision),
    )
    depois = api_client.get(publicacao_url).json()
    assert depois == antes

    historico = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/historico", {"limit": 100}
    ).json()
    assert any(item["kind"] == "PUBLICACAO" for item in historico["items"])


@pytest.mark.django_db
@pytest.mark.authorization
def test_finalized_process_blocks_new_changes_to_its_editais(
    api_client, manager_headers, process_payload
):
    """FR-035: depois do desfecho do Processo, alterações incompatíveis são rejeitadas."""
    edital = publish_original(api_client, manager_headers, process_payload)
    gestor = actor_headers("gestor", GESTOR, if_match=edital.revision)
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        {"reason": "Fim"},
        format="json",
        **gestor,
    )
    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    api_client.post(
        f"/api/v1/admin/processos/{processo.id}/cancelamentos",
        {"reason": "Cancelado após encerrar os Editais"},
        format="json",
        **actor_headers("gestor", GESTOR, if_match=processo.revision, key="cancelar-key-000001"),
    )
    assert ProcessoSeletivo.objects.get(pk=processo.pk).status == ProcessoSeletivo.Status.CANCELADO

    bloqueado = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(edital.versoes_consolidadas.first().id),
            "justification": "Tardia",
            "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": "X"}],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key="tardia-key-00000001"),
    )
    assert bloqueado.status_code == 409
    assert bloqueado.json()["code"] == "invalid_state"
    assert AtoAdministrativo.objects.filter(aggregate_id=edital.id).exists()
