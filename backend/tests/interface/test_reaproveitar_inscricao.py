"""O que as telas do reaproveitamento dizem sobre o teto e o Requerimento (023, emenda do A-10).

A tela "O que não vem" não mencionava a etapa Inscrição, e a cópia não a trazia: quem partia de um
Edital que pedia o Requerimento não tinha como saber que o novo não pediria. Agora a cópia traz, e o
risco virou o simétrico — confiar no que veio. As telas dizem o que vem da origem, o que fica do
destino, e que copiado não é conferido.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.requerimentos.domain import nomes
from tests.fixtures.publicacao import publish_original
from tests.integration.editais.test_reaproveitamento_da_inscricao import DECLARACAO, declarar
from tests.interface.conftest import identificar
from tests.interface.test_reaproveitar import composicao, escolher

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("seletor_ligado")]


@pytest.fixture
def origem(api_client, manager_headers, process_payload):
    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        antes_de_submeter=declarar(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO),
    )


@pytest.fixture
def destino(api_client, manager_headers, origem):
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-011",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "80", "year": 2027, "title": "Edital da nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-a10-tela-0001"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def visivel(html):
    """O texto como se lê: sem comentário de template, sem marcação, sem quebra de linha."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_a_escolha_distingue_o_que_vem_do_que_fica(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])

    pagina = visivel(
        client.get(reverse("interface:reaproveitar", args=[destino.id])).content.decode()
    )

    assert "teto de inscrições por candidato" in pagina
    assert "Requerimento de Matrícula" in pagina
    assert "Número, ano, título, descrição e Processo Seletivo continuam sendo os deste" in pagina
    # A coluna da origem diz o que ela traz da etapa Inscrição.
    assert "teto de 2 inscrições" in pagina
    assert "Requerimento de Matrícula na convocação" in pagina


def test_o_aviso_persistente_pede_a_revisao_da_inscricao_e_leva_a_ela(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    assert escolher(client, destino, origem).status_code == 302

    corpo = client.get(composicao(destino, "perfis")).content.decode()

    aviso = re.search(r"atualize as informações desta oferta(.*?)</p>", corpo, re.S).group(1)
    texto = visivel(aviso)
    for termo in ("datas e prazos", "vagas", "teto de inscrições", "Requerimento de Matrícula"):
        assert termo in texto
    assert "o momento e o texto" in texto
    assert f'href="{composicao(destino, "inscricao")}"' in aviso
    assert f'href="{composicao(destino, "revisao")}"' in aviso
    # Copiar não é validar: o aviso não diz que o que veio está certo.
    assert "não quer dizer que valham" in texto


def test_a_confirmacao_enumera_o_teto_e_o_requerimento_do_destino(client, destino, origem):
    """Destino sem coleção nenhuma, só com a etapa Inscrição declarada: há o que perder."""
    Edital.objects.filter(pk=destino.pk).update(
        max_inscricoes_por_candidato=3,
        requerimento_momento=nomes.NA_INSCRICAO,
        requerimento_declaracao="Do destino.",
    )
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = escolher(client, destino, origem)

    assert resposta.status_code == 200
    corpo = visivel(resposta.content.decode())
    assert "Isto substitui o que já está composto" in corpo
    assert "O teto de 3 inscrições por candidato" in corpo
    assert "O Requerimento de Matrícula na inscrição e o texto da declaração" in corpo
    destino.refresh_from_db()
    assert destino.max_inscricoes_por_candidato == 3
    assert destino.requerimento_momento == nomes.NA_INSCRICAO
