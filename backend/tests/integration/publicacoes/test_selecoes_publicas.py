"""O que o canal público enxerga — e o que ele nunca enxerga (FR-011, FR-012, FR-017).

O seletor é a fronteira entre a elaboração e o candidato. Se ele ler o rascunho, tudo o que vem
depois fica errado em silêncio: a tela mostra o que ainda não foi publicado e a inscrição passa a
responder a regras que ninguém homologou.
"""

import pytest

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application import selectors
from tests.fixtures.edital import actor_headers
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_edital_sem_publicacao_nao_e_selecao_publica(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)

    assert selectors.selecoes_publicas() == []


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_selecao_publicada_aparece_com_a_versao_vigente(
    api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    selecoes = selectors.selecoes_publicas()

    assert [versao.edital_id for versao in selecoes] == [edital.id]
    assert [p["code"] for p in selecoes[0].content["profiles"]] == ["DOC-INFO", "TEC-LAB"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_alteracao_no_rascunho_nao_muda_o_que_o_canal_publico_devolve(
    api_client, manager_headers, process_payload
):
    """FR-011 em uma frase: o candidato lê o publicado, não o que alguém está escrevendo.

    O Edital volta a ser editável por uma Retificação em elaboração? Não — aqui o rascunho é
    reescrito direto pelo canal administrativo, que é o caminho por onde o erro entraria.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    rascunho = rascunho_de_selecao()
    rascunho["profiles"][0]["name"] = "Nome que ninguém publicou"
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="rascunho-depois-0001"),
            "HTTP_IF_MATCH": f'"{Edital.objects.get(pk=edital.pk).revision}"',
        },
    )

    vigente = selectors.selecoes_publicas()[0]

    assert vigente.content["profiles"][0]["name"] == "Professor de Informática"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelado_sai_da_vitrine_e_continua_alcancavel(
    api_client, manager_headers, process_payload
):
    """Anunciar e preservar são coisas diferentes.

    O ato publicado é imutável e não se apaga (princípio II), então a página continua abrindo.
    Mas convidar alguém a se inscrever numa seleção cancelada seria o sistema mentindo.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/cancelamentos",
        {"reason": "Perda de objeto"},
        format="json",
        **{
            **actor_headers("gestor-a", ["edital:cancelar"], key="cancelamento-0001"),
            "HTTP_IF_MATCH": f'"{Edital.objects.get(pk=edital.pk).revision}"',
        },
    )

    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.CANCELADO
    assert selectors.selecoes_publicas() == []
    assert selectors.selecao_publica(edital_id=edital.id) is not None
