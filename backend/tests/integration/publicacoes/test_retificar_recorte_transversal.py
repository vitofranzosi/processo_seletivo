"""Retificar o recorte transversal (044, US3; FR-704, FR-706, FR-722, FR-724).

O código é oferecido pela tela de Retificação como campo próprio, e as recusas valem sobre o
conteúdo **que a Retificação produziria**: renomear a modalidade num Perfil só, declará-la ampla,
ou tirá-la de todos os Perfis deixaria o documento publicado dizendo uma coisa e o portal outra.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.candidato import MODALIDADE_PPP, PERFIL_DOCENTE, PERFIL_TECNICO
from tests.fixtures.publicacao import create_retification, retify, try_publish_retification
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    MODALIDADE_PPP_TECNICO,
    publicar_selecao,
    rascunho_com_ppp_nos_dois_perfis,
)
from tests.interface.conftest import identificar
from tests.interface.test_retificar import campos

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def exato(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """A PPP nos dois Perfis, e a autodeclaração pedida só da PPP do Perfil docente (exato)."""
    rascunho = rascunho_com_ppp_nos_dois_perfis(timezone.now() - timedelta(seconds=1))
    documento = next(
        item for item in rascunho["documentRequirements"] if item["id"] == DOCUMENTO_DA_MODALIDADE
    )
    documento.pop("modalityCode")
    documento.update({"profileId": PERFIL_DOCENTE, "modalityId": MODALIDADE_PPP})
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


@pytest.fixture
def transversal(raiz_de_arquivos, api_client, manager_headers, process_payload):
    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_com_ppp_nos_dois_perfis(timezone.now() - timedelta(seconds=1)),
    )


def _caminho(campo):
    return f"/documentRequirements/id={DOCUMENTO_DA_MODALIDADE}/{campo}"


def test_a_tela_oferece_o_codigo_com_o_alcance_e_sem_a_ampla(client, seletor_ligado, exato):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(reverse("interface:retificar", args=[exato.id])).content.decode()

    assert "Modalidade em todos os Perfis" in corpo
    assert "Não recorta por código" in corpo
    assert "(PPP) — em todos os Perfis que a têm (2 de 2)" in corpo
    assert "(AC) — em todos os Perfis" not in corpo


def test_trocar_de_exato_para_transversal_no_mesmo_ato_publica(
    client, seletor_ligado, api_client, exato
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    vigente = VersaoConsolidada.objects.filter(edital=exato).latest("materialized_at")

    resposta = client.post(
        reverse("interface:retificar", args=[exato.id]),
        {
            **campos(
                vigente,
                **{
                    _caminho("profileId"): "",
                    _caminho("modalityId"): "",
                    _caminho("modalityCode"): "PPP",
                },
            ),
            "justificativa": "Todo candidato PPP apresenta a autodeclaração",
            "confirmar": "1",
        },
    )

    assert resposta.status_code == 302
    retificacao = Retificacao.objects.get(edital=exato)
    assert _caminho("modalityCode") in {a.target_path for a in retificacao.alteracoes.all()}
    publicada = try_publish_retification(api_client, retificacao, suffix="troca")
    assert publicada.status_code == 201, publicada.content
    conteudo = VersaoConsolidada.objects.filter(edital=exato).latest("materialized_at").content
    documento = next(
        item for item in conteudo["documentRequirements"] if item["id"] == DOCUMENTO_DA_MODALIDADE
    )
    assert (documento["profileId"], documento["modalityId"], documento["modalityCode"]) == (
        None,
        None,
        "PPP",
    )


def test_codigo_fabricado_e_recusado_pela_tela(client, seletor_ligado, exato):
    identificar(client, "ana.elaboradora", ["elaborador"])
    vigente = VersaoConsolidada.objects.filter(edital=exato).latest("materialized_at")

    resposta = client.post(
        reverse("interface:retificar", args=[exato.id]),
        {
            **campos(vigente, **{_caminho("modalityCode"): "PTT"}),
            "justificativa": "Tentativa",
            "confirmar": "1",
        },
    )

    assert resposta.status_code == 200
    assert not Retificacao.objects.filter(edital=exato).exists()


def _nome(perfil, modalidade):
    return {
        "targetPath": f"/profiles/id={perfil}/competitionModalities/id={modalidade}/name",
        "operation": "REPLACE",
        "newValue": "Pessoas negras e indígenas",
    }


def test_renomear_a_modalidade_num_perfil_so_e_impedido(api_client, transversal):
    """Recusado já ao elaborar: o conteúdo que a Retificação produziria tem o IMPEDE."""
    recusa = create_retification(
        api_client,
        transversal,
        [_nome(PERFIL_TECNICO, MODALIDADE_PPP_TECNICO)],
        suffix="ren1",
        esperar=422,
    )

    assert recusa["code"] == "blocking_findings"
    assert "'Pessoas negras e indígenas' em TEC-LAB" in recusa["detail"]
    assert "'Pessoas pretas, pardas e indígenas' em DOC-INFO" in recusa["detail"]


def test_renomear_nos_dois_perfis_passa(api_client, transversal):
    retify(
        api_client,
        transversal,
        [_nome(PERFIL_TECNICO, MODALIDADE_PPP_TECNICO), _nome(PERFIL_DOCENTE, MODALIDADE_PPP)],
        suffix="ren2",
    )


def test_declarar_ampla_a_modalidade_do_codigo_e_impedido(api_client, transversal):
    recusa = create_retification(
        api_client,
        transversal,
        [
            {
                "targetPath": f"/profiles/id={PERFIL_TECNICO}/generalCompetitionModalityId",
                "operation": "REPLACE",
                "newValue": MODALIDADE_PPP_TECNICO,
            }
        ],
        suffix="amp1",
        esperar=422,
    )

    assert "ela é a ampla concorrência no Perfil 'TEC-LAB'" in recusa["detail"]
