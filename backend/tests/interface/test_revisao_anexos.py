"""A Revisão pelo canal de quem homologa (020, FR-018).

Conferir bytes que não se pode abrir não é conferir. A tela que pergunta "o que será congelado na
submissão" precisa listar os anexos, entregar o arquivo de cada um e dizer de qual requisito cada
um é o modelo — senão quem homologa vê duas listas sem relação e cruza as duas de cabeça.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models import DocumentoExigido
from processo_seletivo.processos.models import Edital
from tests.fixtures.anexos import criar_anexo
from tests.fixtures.edital import actor_headers
from tests.fixtures.selecao import rascunho_de_selecao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho_de_selecao(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="revisao-anexos-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    edital.refresh_from_db()
    return edital


def test_a_revisao_lista_os_anexos_e_entrega_os_bytes(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    anexo = criar_anexo(edital, rotulo="ANEXO I — REQUERIMENTO", order=1)

    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "revisao"])
    ).content.decode()

    assert "Anexos do Edital" in corpo
    assert "ANEXO I — REQUERIMENTO" in corpo
    assert reverse("interface:anexo-arquivo", args=[edital.id, anexo.id]) in corpo


def test_a_revisao_diz_de_qual_requisito_o_anexo_e_modelo(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    anexo = criar_anexo(edital, rotulo="ANEXO I — REQUERIMENTO", order=1)
    documento = DocumentoExigido.objects.create(
        edital=edital,
        key="requerimento",
        name="Requerimento de inscrição",
        order=1,
        anexo=anexo,
    )

    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "revisao"])
    ).content.decode()

    assert f"modelo de: {documento.name}" in corpo


def test_o_anexo_sem_vinculo_diz_que_nao_e_modelo_de_nada(client, seletor_ligado, edital):
    """Legítimo, e por isso a tela afirma em vez de calar: conteúdo programático não é modelo."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    criar_anexo(edital, rotulo="ANEXO I — CONTEÚDO PROGRAMÁTICO", order=1)

    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "revisao"])
    ).content.decode()

    assert "não é modelo de nenhum requisito" in corpo
