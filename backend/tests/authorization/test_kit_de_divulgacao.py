"""A porta do kit de divulgação (111, FR-3402 a FR-3405).

A ordem é a do contrato: o escopo responde "não encontrado"; a capacidade, a recusa explicada; o
estado, 409. E a capacidade não abre ato nenhum: quem divulga não pratica ato.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface.identidade import PAPEIS, permissoes_de
from tests.fixtures import kit
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db

COMUNICACAO = ["comunicacao"]


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    from processo_seletivo.processos.models import Edital

    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


@pytest.fixture
def publicado(api_client):
    return kit.publicar(api_client, ate=1, chave="porta-do-kit")


def _url(edital):
    return reverse("interface:kit-de-divulgacao", args=[edital.id])


def test_sem_a_capacidade_recebe_a_recusa_explicada(client, seletor_ligado, publicado):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(_url(publicado))
    assert resposta.status_code == 403
    assert "Peça" in resposta.content.decode()


def test_outra_unidade_e_inexistente_recebem_nao_encontrado(client, seletor_ligado, publicado):
    identificar(client, "cora.comunicacao", COMUNICACAO, escopo="outra-unidade")
    assert client.get(_url(publicado)).status_code == 404
    identificar(client, "cora.comunicacao", COMUNICACAO)
    inexistente = reverse(
        "interface:kit-de-divulgacao", args=["00000000-0000-4000-8000-000000000999"]
    )
    assert client.get(inexistente).status_code == 404


def test_nao_publicado_409(client, seletor_ligado, em_elaboracao):
    identificar(client, "cora.comunicacao", COMUNICACAO)
    resposta = client.get(_url(em_elaboracao))
    assert resposta.status_code == 409
    assert "disponível quando o Edital for publicado" in resposta.content.decode()


def test_formato_que_nao_existe_e_nao_encontrado(client, seletor_ligado, publicado):
    identificar(client, "cora.comunicacao", COMUNICACAO)
    url = reverse("interface:kit-de-divulgacao-exportar", args=[publicado.id, "exe"])
    assert client.post(url).status_code == 404


def test_a_capacidade_nao_abre_ato_nenhum():
    """Testado pela lista inteira de permissões, e não por amostra (FR-3403)."""
    concedidas = permissoes_de(COMUNICACAO)
    assert concedidas == {"material:gerar"}
    atos = {p for _, (_, lista) in PAPEIS.items() for p in lista} - {"material:gerar"}
    assert not concedidas & atos


def test_retificacao_em_elaboracao_nao_aparece(api_client, client, seletor_ligado, publicado):
    """A tela só lê o publicado (FR-3404): uma Retificação em curso não chega a ela."""
    from tests.fixtures.publicacao import create_retification

    evento = kit.evento_das_inscricoes(publicado)
    create_retification(
        api_client,
        publicado,
        [
            {
                "targetPath": f"/schedule/id={evento['id']}/endAt",
                "operation": "REPLACE",
                "newValue": "2099-12-31T23:59:00-03:00",
            }
        ],
        suffix="em-curso",
    )
    identificar(client, "cora.comunicacao", COMUNICACAO)
    corpo = client.get(_url(publicado)).content.decode()
    assert "31/12/2099" not in corpo
    assert not RegistroAuditoria.objects.filter(operation="EXPORTAR_MATERIAL").exists()
