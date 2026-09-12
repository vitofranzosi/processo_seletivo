import pytest

from processo_seletivo.editais.models.perfis import PerfilVaga
from processo_seletivo.processos.models import Edital


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us2_replaces_profiles_without_affecting_other_edital(
    api_client, manager_headers, process_payload
):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo_id = created.json()["id"]
    api_client.post(
        f"/api/v1/admin/processos/{processo_id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "us2-second-edital"},
    )
    first, second = Edital.objects.order_by("number")
    response = api_client.put(
        f"/api/v1/admin/editais/{first.id}/rascunho",
        {
            "profiles": [
                {
                    "id": "00000000-0000-0000-0000-000000000211",
                    "code": "CR",
                    "name": "Somente cadastro reserva",
                    "immediateVacancies": 0,
                    "reserveType": "UNLIMITED",
                    "competitionModalities": [
                        {
                            "id": "00000000-0000-0000-0000-000000000212",
                            "code": "AC",
                            "name": "Ampla concorrência",
                        }
                    ],
                }
            ],
            "schedule": [],
        },
        format="json",
        HTTP_AUTHORIZATION="Bearer gestor-a|cefor|edital:elaborar",
        HTTP_IF_MATCH='"1"',
    )
    assert response.status_code == 200
    assert PerfilVaga.objects.filter(edital=first).count() == 1
    assert PerfilVaga.objects.filter(edital=second).count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_o_ciclo_completo_do_quadro_de_vagas_do_57_de_2026(
    api_client, manager_headers, process_payload
):
    """`SC-049` inteiro: declarar `AC 56`, `PcD 4`, `PPI 20`, publicar, e retificar.

    A Retificação reduz `PPI 20 → 18` **junto com o total do Perfil, 80 → 78**. Os dois movimentos
    são um ato só, e é a `FR-161` que os amarra: reduzir a vaga reservada sem reduzir o total
    publicaria um quadro que não fecha, e o sistema recusa — pela mesma razão da `D-007`.

    O que este teste prova, e que nenhum outro prova junto: **nenhuma outra linha muda, e nenhuma
    quantidade é recalculada**. É o ciclo que faz três Editais reais passarem a ser publicáveis
    como documento inteiro, sem anexo binário para o quadro (`SC-053`).
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.edital import complete_draft
    from tests.fixtures.publicacao import (
        create_retification,
        publish_original,
        publish_retification,
    )

    perfil_id = "00000000-0000-0000-0000-000000000401"
    pcd = "00000000-0000-0000-0000-0000005701cd"
    ppi = "00000000-0000-0000-0000-0000005701b1"
    geral = "00000000-0000-0000-0000-000000570001"
    linha_pcd = "00000000-0000-0000-0000-000000570002"
    linha_ppi = "00000000-0000-0000-0000-000000570003"

    rascunho = complete_draft()
    perfil = rascunho["profiles"][0]
    perfil["immediateVacancies"] = 80
    perfil["competitionModalities"] = [
        {"id": pcd, "code": "PCD", "name": "Pessoa com deficiência"},
        {"id": ppi, "code": "PPI", "name": "Pretos, pardos e indígenas"},
    ]
    perfil["vacancyTable"] = [
        {"id": geral, "modalityId": None, "immediateVacancies": 56},
        {"id": linha_pcd, "modalityId": pcd, "immediateVacancies": 4},
        {"id": linha_ppi, "modalityId": ppi, "immediateVacancies": 20},
    ]

    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)

    def vigente():
        return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content

    publicado = vigente()["profiles"][0]
    assert publicado["vacancyTable"] == perfil["vacancyTable"]
    assert publicado["immediateVacancies"] == 80

    base = f"/profiles/id={perfil_id}"
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": f"{base}/vacancyTable/id={linha_ppi}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 18,
                },
                {
                    "targetPath": f"{base}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 78,
                },
            ],
        ),
    )

    retificado = vigente()["profiles"][0]
    assert retificado["vacancyTable"] == [
        {"id": geral, "modalityId": None, "immediateVacancies": 56},
        {"id": linha_pcd, "modalityId": pcd, "immediateVacancies": 4},
        {"id": linha_ppi, "modalityId": ppi, "immediateVacancies": 18},
    ]
    assert retificado["immediateVacancies"] == 78

    # E o conteúdo anterior permanece legível, sob a norma que o governou: a Retificação
    # materializa versão nova, e não reescreve byte nenhum do que já saiu (FR-173).
    anteriores = [
        versao.content["profiles"][0]["vacancyTable"]
        for versao in VersaoConsolidada.objects.filter(edital=edital).order_by("materialized_at")
    ]
    assert anteriores[0] == perfil["vacancyTable"], "o quadro de 20 continua legível"
