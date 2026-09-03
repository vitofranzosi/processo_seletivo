"""A página que responde "essa oportunidade serve para mim?" (US1, FR-014, FR-011)."""

import re

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


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_os_documentos_exigidos_aparecem_antes_da_identificacao(
    client, api_client, manager_headers, process_payload
):
    """L7 da auditoria de percurso: saber o que preparar antes de começar.

    A página listava requisitos de titulação e nada sobre arquivos. Descobrir que precisaria do
    diploma digitalizado custava identificar-se e abrir uma inscrição — e quem lê no ônibus, sem
    os arquivos à mão, desiste no meio.
    """
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import rascunho_aberto_com_documentos

    edital = publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    # O resumo conta quantos são: um triângulo com “Documentos que serão pedidos” parece enfeite,
    # e a contagem é o que decide se dá para se inscrever agora ou se é preciso preparar.
    assert "documentos que serão pedidos" in corpo
    assert re.search(r"<summary>\s*\d+ documentos? que ser", corpo), corpo[:0]
    assert "Documento de identificação" in corpo, "o que vale para todo mundo"
    assert "Diploma de graduação" in corpo, "o que vale para o Perfil"
    assert "Se concorrer em" in corpo, "e o que a modalidade reservada acrescenta"
    assert "Autodeclaração étnico-racial" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cartao_da_vitrine_e_alvo_inteiro(client, api_client, manager_headers, process_payload):
    """L8: num celular, mirar duas palavras de título é o tipo de precisão que faz errar."""
    publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert '.selecao a.titulo::after{content:"";position:absolute;inset:0}' in corpo
    assert ".selecao:focus-within{outline:" in corpo, "o teclado continua vendo o foco"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_requisito_vem_antes_do_botao_de_inscrever(
    client, api_client, manager_headers, process_payload
):
    """A ordem do cartão é a ordem da decisão.

    Ele dizia nome → dados → INSCREVER-SE → documentos → requisitos: as duas informações com que a
    pessoa decide — “tenho o título?” e “tenho os arquivos?” — vinham depois do botão que pede a
    decisão. Quem lê de cima para baixo era convidado a se inscrever antes de saber se podia.
    """
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import rascunho_aberto_com_documentos

    edital = publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    requisitos = corpo.index("Requisitos")
    documentos = corpo.index("que serão pedidos")
    botao = corpo.index("Inscrever-se nesta vaga")

    assert requisitos < botao, "o requisito é o primeiro filtro que a pessoa aplica"
    assert documentos < botao, "e saber o que preparar decide se dá para começar agora"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cartao_da_vaga_nao_empilha_um_dado_por_linha(
    client, api_client, manager_headers, process_payload
):
    """Localidade e concorrência viram uma linha de dados, e não pares empilhados.

    Em 375 px eram seis linhas para três informações, e o cartão inteiro ocupava mais da metade da
    tela — com dois perfis, a página passava de mil e quatrocentos pixels.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert 'class="dados-vaga"' in corpo
    assert "<dt>Localidade</dt>" not in corpo
    assert "<dt>Vagas imediatas</dt>" not in corpo
    # O número de vagas continua sendo o dado em destaque, agora ao lado da ação.
    assert 'class="vagas-numero"' in corpo
