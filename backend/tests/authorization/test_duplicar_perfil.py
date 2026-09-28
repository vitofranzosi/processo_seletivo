"""Quem pode pedir a cópia de um Perfil, e o que ela nunca lê (043, FR-648, R-006).

Os outros fragmentos da composição devolvem linhas vazias ou listas; este lê **marcos e Documentos
gravados**. Por isso a guarda de escopo não basta, e a de compor vem por cima: negar por padrão, e
verificar escopo em toda operação.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.interface.conftest import identificar
from tests.interface.test_compor import PERFIL, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def edital(client, settings, api_client, manager_headers, process_payload):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(reverse("interface:compor-etapa", args=[edital.id, "perfis"]), perfis())
    assert resposta.status_code == 302, resposta.content
    return edital


def _duplicar(client, **parametros):
    return client.get(
        reverse("interface:fragmento-perfil-duplicado", args=["0"]),
        {**perfis(), "duplicar-codigo": "TEC-ADM-2", **parametros},
    )


def test_sem_o_edital_na_query_e_404(client, edital):
    assert _duplicar(client).status_code == 404


def test_edital_de_outra_unidade_e_404(client, edital):
    identificar(client, "ana.elaboradora", ["elaborador"], escopo="outra-unidade")

    assert _duplicar(client, edital=str(edital.id)).status_code == 404


def test_quem_alcanca_o_edital_mas_nao_elabora_recebe_403(client, edital):
    identificar(client, "hugo.homologador", ["homologador"])

    assert _duplicar(client, edital=str(edital.id)).status_code == 403


def test_edital_fora_da_elaboracao_recebe_403_mesmo_de_quem_elabora(client, edital):
    Edital.objects.filter(pk=edital.pk).update(status=Edital.Status.EM_REVISAO)

    assert _duplicar(client, edital=str(edital.id)).status_code == 403


def test_origem_que_nao_e_do_edital_nao_e_lida_do_banco(client, edital):
    """Uma identidade forjada é tratada como origem não gravada: nada do banco entra na resposta —
    nem marco, nem contagem de documento."""
    from processo_seletivo.editais.models.documentos import DocumentoExigido

    DocumentoExigido.objects.create(edital=edital, key="laudo", name="Laudo", perfil_id=PERFIL)
    forjada = "aaaaaaaa-0000-4000-8000-0000000430aa"

    resposta = _duplicar(client, edital=str(edital.id), **{"perfil-0-id": forjada})

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "marcosEmTransito" not in corpo
    assert "replicado" not in corpo


def test_indice_que_nao_e_numero_e_404(client, edital):
    """O índice é refletido num cabeçalho: um `%0A` na rota derrubaria a resposta com 500."""
    resposta = client.get(
        reverse("interface:fragmento-perfil-duplicado", args=["0\nX"]),
        {**perfis(), "edital": str(edital.id), "duplicar-codigo": ""},
    )

    assert resposta.status_code == 404


def test_cartao_acrescentado_com_edital_de_outra_unidade_e_404(client, edital):
    identificar(client, "ana.elaboradora", ["elaborador"], escopo="outra-unidade")

    resposta = client.get(reverse("interface:fragmento-perfil"), {"edital": str(edital.id)})

    assert resposta.status_code == 404
