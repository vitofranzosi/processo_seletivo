"""A lista corrigida chega à página pública, e a inscrição anterior continua sob a que aceitou.

026, US2, SC-098. É a metade que a tela não mostra: quem já se inscreveu aceitou uma lista de
requisitos, e a Retificação não pode reescrever o que aquela pessoa aceitou — ela publica a lista
nova para quem vier.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original, retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ANTES = ["Diploma de graduação", "Registro no conselho profissional"]
DEPOIS = ["Diploma de graduação em Computação", "Registro no conselho profissional"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    rascunho = complete_draft()
    rascunho["profiles"][0]["requirements"] = list(ANTES)
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def test_a_lista_corrigida_vigora_e_a_versao_anterior_continua_legivel(api_client, edital):
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil = original.content["profiles"][0]
    assert perfil["requirements"] == ANTES

    retify(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": f"/profiles/id={perfil['id']}/requirements",
                "newValue": DEPOIS,
            }
        ],
    )

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.content["profiles"][0]["requirements"] == DEPOIS

    original.refresh_from_db()
    assert original.content["profiles"][0]["requirements"] == ANTES, (
        "a versão sob a qual alguém se inscreveu foi reescrita — publicação é ato imutável"
    )


def test_a_lista_pode_ficar_vazia_e_isso_e_diferente_de_nao_declarada(api_client, edital):
    """Um Perfil pode deixar de exigir requisito, e a lista vazia é declaração.

    O que a `026` recusa é o item em branco, não a lista sem itens: `[]` diz "este Perfil não exige
    requisito específico", e `[""]` afirmaria que existe uma exigência sem texto.
    """
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil = original.content["profiles"][0]

    retify(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": f"/profiles/id={perfil['id']}/requirements",
                "newValue": [],
            }
        ],
    )

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.content["profiles"][0]["requirements"] == []
