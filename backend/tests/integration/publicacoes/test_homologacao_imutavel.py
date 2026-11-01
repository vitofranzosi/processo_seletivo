"""A Homologação, imutável no banco salvo a revogação, uma vez (A-03; `publicacoes/0012`).

Como a role de produção, `UPDATE publicacoes_homologacao SET homologated_by = 'alguem'` passava. A
única escrita legítima depois do `INSERT` é a revogação, que preenche três colunas na própria linha;
o gatilho admite só ela, e só com a homologação ainda vigente.
"""

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Homologacao
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.skipif(connection.vendor != "postgresql", reason="os gatilhos são do PostgreSQL"),
]

IMUTAVEL = "homologations are immutable"
HOMOLOGADOR = ["edital:homologar"]


def _homologar(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"2"'},
    )
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "Conferido"},
        format="json",
        **{**actor_headers("homologador", HOMOLOGADOR), "HTTP_IF_MATCH": '"3"'},
    )
    assert resposta.status_code == 200, resposta.content
    return edital


def _revogar(api_client, edital):
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/revogacoes-homologacao",
        {"reason": "Erro identificado na revisão"},
        format="json",
        **{
            **actor_headers("homologador", HOMOLOGADOR, key="revogar-a03-000001"),
            "HTTP_IF_MATCH": '"4"',
        },
    )


@pytest.fixture
def homologado(api_client, manager_headers, process_payload):
    return _homologar(api_client, manager_headers, process_payload)


def test_homologar_e_revogar_passam_como_producao(
    api_client,
    manager_headers,
    process_payload,
    como_producao,  # noqa: F811
):
    with como_producao():
        edital = _homologar(api_client, manager_headers, process_payload)
        revogada = _revogar(api_client, edital)

    assert revogada.status_code == 200, revogada.content
    homologacao = Homologacao.objects.get(revisao__edital=edital)
    assert homologacao.revoked_by == "homologador"
    assert homologacao.revocation_reason == "Erro identificado na revisão"
    assert (homologacao.homologated_by, homologacao.reason) == ("homologador", "Conferido")


@pytest.mark.parametrize(
    "campos",
    [{"homologated_by": "alguem"}, {"reason": "Outro motivo"}],
    ids=["autoria", "motivo"],
)
def test_a_homologacao_nao_muda(homologado, como_producao, campos):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=IMUTAVEL), transaction.atomic():
        Homologacao.objects.filter(revisao__edital=homologado).update(**campos)


def test_a_revogacao_nao_leva_a_autoria_junto(homologado, como_producao):  # noqa: F811
    from django.utils import timezone

    with como_producao(), pytest.raises(DatabaseError, match=IMUTAVEL), transaction.atomic():
        Homologacao.objects.filter(revisao__edital=homologado).update(
            revoked_at=timezone.now(), revoked_by="alguem", homologated_by="alguem"
        )


@pytest.mark.parametrize("motivo", ["", "   "], ids=["vazio", "espacos"])
def test_a_revogacao_sem_motivo_e_recusada_no_banco(homologado, como_producao, motivo):  # noqa: F811
    from django.utils import timezone

    with como_producao(), pytest.raises(DatabaseError, match=IMUTAVEL), transaction.atomic():
        Homologacao.objects.filter(revisao__edital=homologado).update(
            revoked_at=timezone.now(), revoked_by="homologador", revocation_reason=motivo
        )


def test_o_comando_recusa_revogar_sem_motivo(homologado):
    """O contrato e a tela já exigiam o motivo; agora o comando também, com recusa legível."""
    from processo_seletivo.publicacoes.application.publish_edital import revoke_homologation
    from processo_seletivo.shared.api.problems import DomainError
    from tests.conftest import ator_institucional

    with pytest.raises(DomainError) as recusa:
        revoke_homologation(
            actor=ator_institucional("homologador", *HOMOLOGADOR),
            edital_id=homologado.id,
            expected_revision=4,
            reason="   ",
            idempotency_key="revogar-sem-motivo-a03",
            correlation_id="teste",
        )

    assert recusa.value.code == "reason_required"
    assert Homologacao.objects.get(revisao__edital=homologado).revoked_at is None


def test_a_revogacao_nao_se_repete_nem_se_reescreve(api_client, homologado, como_producao):  # noqa: F811
    from django.utils import timezone

    assert _revogar(api_client, homologado).status_code == 200

    with como_producao():
        for campos in (
            {"revoked_by": "outra-pessoa"},
            {"revocation_reason": "Outro motivo"},
            {"revoked_at": timezone.now()},
            {"revoked_at": None, "revoked_by": "", "revocation_reason": ""},
        ):
            with pytest.raises(DatabaseError, match=IMUTAVEL), transaction.atomic():
                Homologacao.objects.filter(revisao__edital=homologado).update(**campos)


@pytest.mark.parametrize(
    "comando",
    [
        "UPDATE publicacoes_homologacao SET homologated_at = now()",
        "DELETE FROM publicacoes_homologacao",
    ],
    ids=["instante", "exclusao"],
)
def test_a_homologacao_nao_muda_por_sql(homologado, como_producao, comando):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=IMUTAVEL), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(comando)
