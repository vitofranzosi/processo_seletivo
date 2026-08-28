import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao, RevisaoEdital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import create_retification, publish_original, retify

VACANCIES = "/profiles/0/immediateVacancies"


@pytest.fixture
def edital_publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db
@pytest.mark.authorization
def test_public_consultation_needs_no_credentials(api_client, edital_publicado):
    """FR-031: conteúdo publicado é acessível sem autorização administrativa."""
    publicacao = Publicacao.objects.get(edital=edital_publicado)
    versao = VersaoConsolidada.objects.get(edital=edital_publicado)
    for url in (
        f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente",
        f"/api/v1/public/editais/{edital_publicado.id}/historico",
        f"/api/v1/public/publicacoes/{publicacao.id}",
        f"/api/v1/public/versoes/{versao.id}",
    ):
        assert api_client.get(url).status_code == 200, url


@pytest.mark.django_db
@pytest.mark.authorization
def test_unpublished_retification_is_not_revealed_to_the_public(api_client, edital_publicado):
    """US6 cenário 3: Retificação em elaboração não altera nem aparece na consulta pública."""
    rascunho = create_retification(
        api_client,
        edital_publicado,
        [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 999}],
    )
    assert api_client.get(f"/api/v1/public/retificacoes/{rascunho.id}").status_code == 404

    vigente = api_client.get(f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente").json()
    assert vigente["content"]["profiles"][0]["immediateVacancies"] == 1

    historico = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/historico", {"limit": 100}
    ).json()
    assert str(rascunho.id) not in [item["id"] for item in historico["items"]]


@pytest.mark.django_db
@pytest.mark.authorization
def test_public_projection_never_exposes_elaboration_identifiers(api_client, edital_publicado):
    """FR-031: material de elaboração e revisão exige autorização."""
    publicacao = Publicacao.objects.get(edital=edital_publicado)
    revisao = RevisaoEdital.objects.get(edital=edital_publicado)
    corpo = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}").content.decode()

    assert str(revisao.id) not in corpo
    assert "prepared_by" not in corpo and "preparedBy" not in corpo
    assert "revisao" not in corpo and "revisionId" not in corpo
    assert publicacao.published_by not in corpo


@pytest.mark.django_db
@pytest.mark.authorization
def test_public_projection_never_exposes_audit_trail(api_client, edital_publicado):
    retify(
        api_client,
        edital_publicado,
        [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 7}],
    )
    assert RegistroAuditoria.objects.exists()
    corpo = api_client.get(
        f"/api/v1/public/editais/{edital_publicado.id}/historico", {"limit": 100}
    ).content.decode()

    for registro in RegistroAuditoria.objects.all():
        assert str(registro.event_id) not in corpo
    assert "correlation" not in corpo.lower()
    assert "homologated_by" not in corpo and "homologatedBy" not in corpo


@pytest.mark.django_db
@pytest.mark.authorization
def test_public_endpoints_reject_write_attempts(api_client, edital_publicado):
    publicacao = Publicacao.objects.get(edital=edital_publicado)
    for url in (
        f"/api/v1/public/editais/{edital_publicado.id}/versao-vigente",
        f"/api/v1/public/publicacoes/{publicacao.id}",
    ):
        assert api_client.post(url, {}, format="json").status_code == 405, url
        assert api_client.delete(url).status_code == 405, url


@pytest.mark.django_db
@pytest.mark.authorization
def test_public_query_does_not_reveal_editais_from_another_edital(
    api_client, manager_headers, process_payload
):
    """Anti-IDOR: identificador de outro Edital não devolve conteúdo cruzado."""
    edital = publish_original(api_client, manager_headers, process_payload)
    agora = timezone.now()
    outro = Edital.objects.create(
        processo=edital.processo,
        institution_scope=edital.institution_scope,
        number="99",
        year=2026,
        title="Edital sem publicação",
        created_at=agora,
        created_by="gestor-a",
        last_edited_by="gestor-a",
    )
    response = api_client.get(f"/api/v1/public/editais/{outro.id}/versao-vigente")
    assert response.status_code == 404
    assert response.json()["code"] == "no_effective_version"

    historico = api_client.get(f"/api/v1/public/editais/{outro.id}/historico").json()
    assert historico["items"] == []
