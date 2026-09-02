"""US7 — Cancelar ou Encerrar com Preservação. Rastreia FR-005, FR-006, FR-034 e FR-035."""

import pytest

from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original

GESTOR = ["processo:encerrar", "processo:cancelar", "edital:encerrar", "edital:cancelar"]


def ato(api_client, url, revision, reason, key="us7-key-0000000001"):
    return api_client.post(
        url,
        {"reason": reason},
        format="json",
        **actor_headers("gestor", GESTOR, if_match=revision, key=key),
    )


def ativar(api_client, manager_headers, processo):
    return api_client.post(
        f"/api/v1/admin/processos/{processo.id}/ativacoes",
        {"reason": "Abertura formal"},
        format="json",
        **{
            **manager_headers,
            "HTTP_IF_MATCH": f'"{processo.revision}"',
            "HTTP_IDEMPOTENCY_KEY": "us7-ativacao-000001",
        },
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us7_cancelling_a_published_edital_preserves_its_publications(
    api_client, manager_headers, process_payload
):
    """Cenário 1: o ato muda a situação sem apagar Publicações nem histórico."""
    edital = publish_original(api_client, manager_headers, process_payload)
    publicacoes_antes = list(Publicacao.objects.filter(edital=edital).values_list("id", flat=True))

    response = ato(
        api_client,
        f"/api/v1/admin/editais/{edital.id}/cancelamentos",
        edital.revision,
        "Interrupção administrativa",
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELADO"

    assert list(Publicacao.objects.filter(edital=edital).values_list("id", flat=True)) == (
        publicacoes_antes
    )
    registro = AtoAdministrativo.objects.get(aggregate_id=edital.id, operation="CANCELAR")
    assert registro.reason == "Interrupção administrativa"
    assert registro.actor_subject == "gestor"
    assert registro.occurred_at is not None
    assert api_client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente").status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us7_closed_process_keeps_history_and_rejects_incompatible_changes(
    api_client, manager_headers, process_payload
):
    """Cenário 2: histórico permanece consultável e novas alterações são rejeitadas."""
    edital = publish_original(api_client, manager_headers, process_payload)
    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    ativar(api_client, manager_headers, processo)
    processo.refresh_from_db()

    encerrado = ato(
        api_client,
        f"/api/v1/admin/processos/{processo.id}/encerramentos",
        processo.revision,
        "Certame concluído",
    )
    assert encerrado.status_code == 200
    assert encerrado.json()["status"] == "ENCERRADO"

    historico = api_client.get(
        f"/api/v1/public/editais/{edital.id}/historico", {"limit": 100}
    ).json()
    assert any(item["kind"] == "PUBLICACAO" for item in historico["items"])

    bloqueado = ato(
        api_client,
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        edital.revision,
        "Tardio",
        key="us7-key-0000000002",
    )
    assert bloqueado.status_code == 409
    assert bloqueado.json()["code"] == "invalid_state"


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us7_process_keeps_its_status_until_an_explicit_act(
    api_client, manager_headers, process_payload
):
    """Cenário 3: Editais em estado final não encerram o Processo automaticamente."""
    edital = publish_original(api_client, manager_headers, process_payload)
    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    ativar(api_client, manager_headers, processo)

    ato(
        api_client,
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        edital.revision,
        "Etapas concluídas",
    )
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.ENCERRADO

    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ATIVO
    assert not AtoAdministrativo.objects.filter(
        aggregate_id=processo.id, operation="ENCERRAR"
    ).exists()

    encerrado = ato(
        api_client,
        f"/api/v1/admin/processos/{processo.id}/encerramentos",
        processo.revision,
        "Ato explícito do gestor",
        key="us7-key-0000000003",
    )
    assert encerrado.status_code == 200
    assert encerrado.json()["status"] == "ENCERRADO"


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us7_cancelling_a_process_is_blocked_until_every_edital_is_final(
    api_client, manager_headers, process_payload
):
    """Cenário 4: o bloqueio identifica os Editais pendentes e não propaga cancelamento."""
    edital = publish_original(api_client, manager_headers, process_payload)
    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    segundo = api_client.post(
        f"/api/v1/admin/processos/{processo.id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo Edital"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "us7-segundo-000001"},
    )
    assert segundo.status_code == 201

    bloqueado = ato(
        api_client,
        f"/api/v1/admin/processos/{processo.id}/cancelamentos",
        processo.revision,
        "Cancelamento prematuro",
    )
    assert bloqueado.status_code == 409
    assert bloqueado.json()["code"] == "editais_pendentes"
    assert "01/2026" in bloqueado.json()["detail"]
    assert "02/2026" in bloqueado.json()["detail"]
    assert ProcessoSeletivo.objects.get(pk=processo.pk).status == processo.status
    assert Edital.objects.filter(processo=processo, status=Edital.Status.CANCELADO).count() == 0

    ato(
        api_client,
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        edital.revision,
        "Etapas concluídas",
        key="us7-key-0000000004",
    )
    ato(
        api_client,
        f"/api/v1/admin/editais/{segundo.json()['id']}/cancelamentos",
        segundo.json()["revision"],
        "Não publicado",
        key="us7-key-0000000005",
    )

    processo.refresh_from_db()
    permitido = ato(
        api_client,
        f"/api/v1/admin/processos/{processo.id}/cancelamentos",
        processo.revision,
        "Todos os Editais finalizados",
        key="us7-key-0000000006",
    )
    assert permitido.status_code == 200
    assert permitido.json()["status"] == "CANCELADO"


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us7_closing_an_edital_is_not_treated_as_cancellation(
    api_client, manager_headers, process_payload
):
    """Cenário 5: Encerrado é conclusão regular, distinta de Cancelado, com histórico intacto."""
    edital = publish_original(api_client, manager_headers, process_payload)
    response = ato(
        api_client,
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        edital.revision,
        "Etapas concluídas regularmente",
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ENCERRADO"

    assert AtoAdministrativo.objects.filter(aggregate_id=edital.id, operation="ENCERRAR").exists()
    assert not AtoAdministrativo.objects.filter(
        aggregate_id=edital.id, operation="CANCELAR"
    ).exists()

    recusado = ato(
        api_client,
        f"/api/v1/admin/editais/{edital.id}/cancelamentos",
        response.json()["revision"],
        "Tentativa de reclassificar como cancelado",
        key="us7-key-0000000007",
    )
    assert recusado.status_code == 409
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.ENCERRADO
    assert Publicacao.objects.filter(edital=edital).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us7_edital_cannot_be_created_in_a_finished_processo(
    api_client, manager_headers, process_payload
):
    """FR-011 da 003: encerrar precisa significar o que diz, inclusive para Editais novos.

    `add_edital` não consultava a invariante de FR-035, e um Edital nascia Em elaboração dentro
    de um Processo já encerrado — estado que nenhum ato posterior conseguiria concluir.
    """
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo = ProcessoSeletivo.objects.get(pk=criado.json()["id"])
    for final in (ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO):
        ProcessoSeletivo.objects.filter(pk=processo.pk).update(status=final)

        recusa = api_client.post(
            f"/api/v1/admin/processos/{processo.id}/editais",
            {"number": "99", "year": 2026, "title": "Depois do fim"},
            format="json",
            **actor_headers("gestor-b", ["edital:criar"], key=f"pos-{final}-000001"),
        )

        assert recusa.status_code == 409, recusa.content
        assert recusa.json()["code"] == "invalid_state"
        assert Edital.objects.filter(processo=processo).count() == 1
