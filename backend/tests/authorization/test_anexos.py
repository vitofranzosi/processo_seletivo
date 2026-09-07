"""A fronteira de regime dos Anexos (020, FR-017, FR-052).

O artefato publicado é conteúdo público versionado, e o não publicado é rascunho de Edital que
ninguém fora da elaboração deveria alcançar. As duas afirmações vivem na mesma tabela e na mesma
coluna — `congelado_em` —, e é por isso que a fronteira precisa de teste próprio: nada no tipo do
objeto lembra qual dos dois regimes ele está seguindo.
"""

import pytest
from django.urls import reverse

from tests.fixtures.anexos import criar_anexo, criar_artefato
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def edital_em_elaboracao(api_client, manager_headers, process_payload):
    from processo_seletivo.processos.models import Edital

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


@pytest.mark.authorization
def test_o_artefato_nao_publicado_nao_tem_endereco_publico(api_client):
    artefato = criar_artefato(marca="A")

    assert api_client.get(reverse("public-anexo", args=[artefato.id])).status_code == 404


@pytest.mark.authorization
def test_o_artefato_publicado_dispensa_identificacao(api_client):
    artefato = criar_artefato(marca="A", congelado=True)

    assert api_client.get(reverse("public-anexo", args=[artefato.id])).status_code == 200


@pytest.mark.authorization
@pytest.mark.django_db(transaction=True)
def test_quem_elabora_alcanca_o_artefato_do_rascunho(client, seletor_ligado, edital_em_elaboracao):
    """A outra metade da fronteira: sem este caminho, quem homologa não tem como conferir os bytes
    que a publicação vai entregar (FR-018)."""
    anexo = criar_anexo(edital_em_elaboracao, rotulo="ANEXO I — REQUERIMENTO", order=1)
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.get(
        reverse("interface:anexo-arquivo", args=[edital_em_elaboracao.id, anexo.id])
    )

    assert resposta.status_code == 200
    assert resposta["Cache-Control"].startswith("no-store")


@pytest.mark.authorization
@pytest.mark.django_db(transaction=True)
def test_quem_homologa_alcanca_o_artefato_do_rascunho(client, seletor_ligado, edital_em_elaboracao):
    """A outra metade da FR-017: sem este caminho, homologar é aprovar o que não se pode abrir."""
    anexo = criar_anexo(edital_em_elaboracao, rotulo="ANEXO I — REQUERIMENTO", order=1)
    identificar(client, "helena.homologadora", ["homologador"])

    resposta = client.get(
        reverse("interface:anexo-arquivo", args=[edital_em_elaboracao.id, anexo.id])
    )

    assert resposta.status_code == 200


@pytest.mark.authorization
@pytest.mark.django_db(transaction=True)
def test_sem_identificacao_o_artefato_do_rascunho_nao_e_entregue(
    client, seletor_ligado, edital_em_elaboracao
):
    anexo = criar_anexo(edital_em_elaboracao, rotulo="ANEXO I — REQUERIMENTO", order=1)

    resposta = client.get(
        reverse("interface:anexo-arquivo", args=[edital_em_elaboracao.id, anexo.id])
    )

    assert resposta.status_code in (302, 403, 404)
    assert resposta.status_code != 200


@pytest.mark.authorization
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("papel", ["publicador", "gestor", "auditor"])
def test_ator_autenticado_sem_a_capacidade_nao_recebe_os_bytes(
    client, seletor_ligado, edital_em_elaboracao, papel
):
    """O achado que a primeira redação deixou passar (FR-017).

    A view conferia **só** identidade e escopo institucional, e escopo diz de quem é o Edital, não
    quem pode vê-lo antes de ele existir para o público. Qualquer identidade da casa — inclusive
    quem publica, quem gere o processo e quem audita — recebia o rascunho.

    A recusa é 404, e não 403: dizer "existe, mas você não pode" já entregaria que existe.
    """
    anexo = criar_anexo(edital_em_elaboracao, rotulo="ANEXO I — REQUERIMENTO", order=1)
    identificar(client, f"ator.{papel}", [papel])

    resposta = client.get(
        reverse("interface:anexo-arquivo", args=[edital_em_elaboracao.id, anexo.id])
    )

    assert resposta.status_code == 404
