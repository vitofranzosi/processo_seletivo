"""O contrato operacional de inscrição, de ponta a ponta (US2 da 009).

O que o elaborador declara precisa chegar ao conteúdo publicado com identidade estável, ser
alcançável por Retificação pela gramática que já existe, e recusar o estado incoerente na
publicação — que é onde uma sequência de Retificações produziria o que a elaboração impede.
"""

import pytest
from django.db.utils import IntegrityError

from processo_seletivo.editais.models import DocumentoExigido, EventoCronograma
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers, identificador
from tests.fixtures.publicacao import create_retification, publish_retification
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao

DOCUMENTOS = [
    {
        "id": identificador(408, 0),
        "key": "identificacao",
        "name": "Documento de identificação",
        "instructions": "Frente e verso em arquivo único.",
        "required": True,
        "order": 1,
    },
    {
        "id": identificador(409, 0),
        "key": "diploma",
        "name": "Diploma de graduação",
        "required": True,
        "order": 2,
        "profileId": identificador(401, 0),
    },
    {
        "id": identificador(410, 0),
        "key": "autodeclaracao",
        "name": "Autodeclaração étnico-racial",
        "required": True,
        "order": 3,
        "modalityId": identificador(404, 0),
    },
]


def _rascunho_com_contrato(**ajustes):
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    rascunho["documentRequirements"] = [dict(documento) for documento in DOCUMENTOS]
    rascunho.update(ajustes)
    return rascunho


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_contrato_declarado_chega_ao_conteudo_publicado(
    api_client, manager_headers, process_payload
):
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=_rascunho_com_contrato()
    )

    conteudo = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content

    assert conteudo["schemaVersion"] == 5
    assert [documento["key"] for documento in conteudo["documentRequirements"]] == [
        "identificacao",
        "diploma",
        "autodeclaracao",
    ]
    designados = [e["id"] for e in conteudo["schedule"] if e["isRegistrationPeriod"]]
    assert designados == [identificador(402, 0)], "um Evento designado, e é o do rascunho"
    # As quatro combinações se leem por ausência, e é isso que o conteúdo publicado carrega.
    por_chave = {d["key"]: d for d in conteudo["documentRequirements"]}
    assert (por_chave["identificacao"]["profileId"], por_chave["identificacao"]["modalityId"]) == (
        None,
        None,
    )
    assert por_chave["diploma"]["profileId"] == identificador(401, 0)
    assert por_chave["autodeclaracao"]["modalityId"] == identificador(404, 0)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_secao_gerada_enuncia_os_documentos_no_documento_publicado(
    api_client, manager_headers, process_payload
):
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=_rascunho_com_contrato()
    )
    conteudo = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content

    secoes = {secao["key"]: secao for secao in conteudo["sections"]}

    assert secoes["documentos-exigidos"]["source"] == "documentRequirements"
    assert secoes["documentos-exigidos"]["type"] == "GENERATED"
    assert "content" not in secoes["documentos-exigidos"], "seção gerada não persiste texto"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_retificacao_alcanca_o_documento_e_a_designacao(
    api_client, manager_headers, process_payload
):
    """Pela gramática existente, sem nenhuma regra nova de endereçamento (FR-009)."""
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=_rascunho_com_contrato()
    )
    caminho_documento = f"/documentRequirements/id={identificador(409, 0)}/required"
    caminho_designacao = f"/schedule/id={identificador(402, 0)}/isRegistrationPeriod"

    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": caminho_documento,
                "operation": "REPLACE",
                "newValue": False,
                "expectedPreviousHash": "",
            },
            {
                "targetPath": caminho_designacao,
                "operation": "REPLACE",
                "newValue": False,
                "expectedPreviousHash": "",
            },
        ],
        suffix="doc",
    )
    publish_retification(api_client, retificacao, suffix="doc")

    conteudo = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    por_chave = {d["key"]: d for d in conteudo["documentRequirements"]}
    assert por_chave["diploma"]["required"] is False
    assert [e for e in conteudo["schedule"] if e["isRegistrationPeriod"]] == []


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_banco_recusa_o_segundo_periodo_no_mesmo_cronograma(
    api_client, manager_headers, process_payload
):
    """A constraint parcial é a garantia; a interface nem oferece o segundo (FR-001)."""
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=_rascunho_com_contrato()
    )
    designado = EventoCronograma.objects.get(cronograma__edital=edital, is_registration_period=True)
    outro = EventoCronograma.objects.create(
        cronograma=designado.cronograma,
        type="Prova",
        description="Prova objetiva",
        start_at=designado.start_at,
        order=99,
    )

    outro.is_registration_period = True
    with pytest.raises(IntegrityError):
        outro.save()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_documento_com_modalidade_de_outro_perfil_e_recusado_na_elaboracao(
    api_client, manager_headers, process_payload
):
    """A combinação impossível é recusada na gravação, com código próprio e sem gravar nada."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital_id = Edital.objects.get(processo_id=criado.json()["id"]).id
    rascunho = _rascunho_com_contrato()
    # A modalidade `PPP` é do Perfil docente; restringir o documento ao Perfil técnico e à
    # modalidade docente é a combinação que não existe em Edital nenhum.
    rascunho["documentRequirements"][2]["profileId"] = identificador(406, 0)

    recusa = api_client.put(
        f"/api/v1/admin/editais/{edital_id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="documento-alheio-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.json()["code"] == "invalid_document_requirements"
    assert "modalidade" in recusa.json()["detail"]
    assert DocumentoExigido.objects.count() == 0, "recusa não grava metade do rascunho"
