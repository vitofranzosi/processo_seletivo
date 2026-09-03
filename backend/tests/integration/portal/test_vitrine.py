"""A porta: quem é de fora encontra a seleção sem passar pela gestão (US1, FR-012 a FR-014).

Os testes afirmam duas coisas de naturezas diferentes: que o que deve aparecer aparece, e que o
que é de dentro não vaza. A segunda é a que ninguém percebe quebrada — uma página pública com
nome de quem elaborou continua parecendo certa.
"""

from pathlib import Path

import pytest
from django.urls import reverse

from tests.fixtures.selecao import publicar_selecao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_abre_sem_identificacao(client, api_client, manager_headers, process_payload):
    publicar_selecao(api_client, manager_headers, process_payload)

    resposta = client.get(reverse("portal:vitrine"))

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Processo Seletivo 2026" in corpo
    assert "PS-2026-001" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_leva_ao_detalhe_da_selecao(client, api_client, manager_headers, process_payload):
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert reverse("portal:selecao", args=[edital.id]) in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_edital_nao_publicado_nao_aparece(client, api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert "Processo Seletivo 2026" not in corpo
    assert "Nenhuma seleção" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_nao_expoe_dado_de_gestao(client, api_client, manager_headers, process_payload):
    """Quem elaborou, quem publicou e o estado interno do Edital são de dentro.

    Nenhum deles é segredo — a auditoria os publica a quem tem permissão. Mas a vitrine é uma
    página de oportunidade, e cada um deles ali é dado de gestão sem finalidade para quem lê.
    """
    publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    for de_dentro in ("preparador", "homologador", "publicador", "PUBLICADO", "EM_ELABORACAO"):
        assert de_dentro not in corpo, f"{de_dentro} é dado de gestão e não pertence à vitrine"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vitrine_e_cacheavel(client, api_client, manager_headers, process_payload):
    """Contraponto de FR-075a: a vitrine **não** carrega dado pessoal, e não é marcada como
    privada. Marcar tudo seria perder a distinção que a marcação existe para fazer."""
    publicar_selecao(api_client, manager_headers, process_payload)

    resposta = client.get(reverse("portal:vitrine"))

    assert "no-store" not in resposta.headers.get("Cache-Control", "")


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cartao_diz_para_qual_vaga_e_quantas(
    client, api_client, manager_headers, process_payload
):
    """ "Existe uma seleção" e "existe uma seleção para mim" são coisas diferentes.

    Descobrir se havia vaga para si custava abrir a página — o que quem procura emprego faz uma
    vez, não dez.
    """
    _publicar_aberta(api_client, manager_headers, process_payload)

    texto = " ".join(client.get(reverse("portal:vitrine")).content.decode().split())

    assert "Professor de Informática" in texto
    assert "Técnico de Laboratório" in texto
    assert "vagas imediatas" in texto
    assert "cadastro reserva" in texto
    assert "Ver vagas e inscrever-se" in texto, "o cartão convida, em vez de esperar adivinhação"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_abertas_vem_primeiro_e_em_secao_propria(
    client, api_client, manager_headers, process_payload
):
    """Quem chega quer saber onde ainda dá para se inscrever.

    Misturar o que fechou com o que está aberto obriga a ler tudo para descobrir o que interessa.
    """
    _publicar_aberta(api_client, manager_headers, process_payload)

    texto = " ".join(client.get(reverse("portal:vitrine")).content.decode().split())

    assert "Inscrições abertas" in texto
    assert texto.index("Inscrições abertas") < texto.index('class="selecoes"'), (
        "a seção nomeia o que vem depois dela"
    )


def _publicar_aberta(api_client, manager_headers, process_payload):
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import rascunho_aberto_com_documentos

    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )


CARTAO = (
    Path(__file__).resolve().parents[3]
    / "processo_seletivo/portal/templates/portal/_cartao_da_selecao.html"
)


def test_o_separador_do_cartao_acompanha_o_valor_que_ele_separa():
    """`processoCode` pode não existir no conteúdo publicado, e o ponto saía sozinho.

    A linha começava com "· Edital 07/2026", e ponto que não separa nada é ruído com aparência de
    erro de dado — quem lê não tem como saber que aquele é o segundo campo, e não o primeiro.

    O que se prende é a **forma**: o separador vive dentro da condição do valor que o precede.
    Renderizar não serve de prova aqui, porque a seleção que expõe o defeito é justamente a que
    não se consegue publicar pelo caminho normal — o código é obrigatório na elaboração.
    """
    marcacao = CARTAO.read_text()

    assert "{% if selecao.processo_codigo %}{{ selecao.processo_codigo }} · {% endif %}" in marcacao
    assert "{{ selecao.processo_codigo }} · Edital" not in marcacao
