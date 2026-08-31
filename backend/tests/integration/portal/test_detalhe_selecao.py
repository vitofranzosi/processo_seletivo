"""A página que responde "essa oportunidade serve para mim?" (US1, FR-014, FR-011)."""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_apresenta_os_perfis_com_o_que_decide_a_candidatura(
    client, api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Professor de Informática" in corpo
    assert "Técnico de Laboratório" in corpo
    assert "Campus Serra" in corpo
    assert "Mestrado em Computação ou área afim" in corpo
    assert "Ampla concorrência" in corpo
    assert "Pessoas pretas, pardas e indígenas" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_deriva_da_versao_vigente_e_nao_do_rascunho(
    client, api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    rascunho = rascunho_de_selecao()
    rascunho["profiles"][0]["name"] = "Nome que ninguém publicou"
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="rascunho-portal-0001"),
            "HTTP_IF_MATCH": f'"{Edital.objects.get(pk=edital.pk).revision}"',
        },
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Nome que ninguém publicou" not in corpo
    assert "Professor de Informática" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_selecao_sem_publicacao_nao_tem_pagina(
    client, api_client, manager_headers, process_payload
):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()

    assert client.get(reverse("portal:selecao", args=[edital.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_nao_expoe_identificador_tecnico_no_corpo(
    client, api_client, manager_headers, process_payload
):
    """A `007` tirou o UUID do documento pelo mesmo motivo: não prova nada a quem lê.

    O identificador continua no endereço, porque é assim que se chega à página — e identificador
    público não confere autorização (princípio I).
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    corpo_visivel = corpo.split("<main")[1]

    assert str(edital.processo_id) not in corpo_visivel


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_ler_o_edital_nao_disputa_a_decisao_com_inscrever_se(
    client, api_client, manager_headers, process_payload
):
    """SC-UX-008: duas chamadas de ação não disputam a mesma decisão.

    Enquanto usava o mesmo verde sólido dos botões de inscrição, `Ler o Edital completo (PDF)` era
    o único botão preenchido na primeira dobra em 375px — a página anunciava "baixe um PDF" onde
    queria anunciar "inscreva-se".
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert 'class="documento secundaria"' in corpo
    assert ".documento.secundaria{background:var(--branco)" in corpo
    assert corpo.count('class="documento secundaria"') == 1, "só o PDF é secundário"
