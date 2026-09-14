"""A Retificação do local vigora, e a versão anterior continua legível (026, US1, SC-097).

O que este arquivo guarda é a metade que a tela não mostra: depois de publicada a Retificação, o
conteúdo vigente carrega o local novo **e** a versão consolidada anterior continua carregando o
antigo. É a Constituição em ato — "Um Edital publicado NÃO PODE ser sobrescrito" —, e é o que
distingue corrigir de reescrever.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original, retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ANTIGO = "Campus Serra — Auditório"
NOVO = "Campus Vitória — Sala 204"


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    rascunho = complete_draft()
    rascunho["schedule"][0]["location"] = ANTIGO
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def test_o_local_corrigido_passa_a_vigorar_e_o_anterior_continua_legivel(api_client, edital):
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    evento = original.content["schedule"][0]
    assert evento["location"] == ANTIGO

    retify(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": f"/schedule/id={evento['id']}/location",
                "newValue": NOVO,
            }
        ],
    )

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.id != original.id, "a Retificação materializa versão nova"
    assert vigente.content["schedule"][0]["location"] == NOVO

    original.refresh_from_db()
    assert original.content["schedule"][0]["location"] == ANTIGO, (
        "a versão consolidada anterior foi reescrita — publicação é ato imutável"
    )


def test_o_restante_do_evento_atravessa_a_retificacao_intacto(api_client, edital):
    """Corrigir um campo não pode levar junto os vizinhos.

    É o defeito que o `replace_draft` já produziu uma vez, por outro caminho: o que não é reenviado
    desaparece. Aqui a Retificação endereça **um** campo por identidade, e o resto do Evento
    precisa chegar igual do outro lado.
    """
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    antes = dict(original.content["schedule"][0])

    retify(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": f"/schedule/id={antes['id']}/location",
                "newValue": NOVO,
            }
        ],
    )

    depois = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    evento = depois.content["schedule"][0]
    assert {chave: valor for chave, valor in evento.items() if chave != "location"} == {
        chave: valor for chave, valor in antes.items() if chave != "location"
    }
