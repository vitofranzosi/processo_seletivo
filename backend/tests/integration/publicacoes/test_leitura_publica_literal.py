"""A leitura pública serve o conteúdo **literal**, e nunca a projeção elevada (012, T-002).

A elevação existe para que Edital publicado antes do incremento continue retificável. Ela vale
dentro do fluxo de Retificação — elaboração, composição, consolidação — e **em lugar nenhum além**.

Elevar no caminho público faria a página mostrar conteúdo que o `content_hash` da Publicação não
cobre, e a verificação de integridade da `005` passaria a comparar coisas diferentes: a tela diria
uma coisa e o hash provaria outra. É por isso que convivem Etapas com e sem as duas propriedades, e
por isso a ausência tem um leitor de domínio em vez de uma reescrita do conteúdo.
"""

import pytest

from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.legado import PROPRIEDADES_DO_INCREMENTO, publicar_na_versao_anterior
from tests.fixtures.snapshot import rascunho_com_etapas

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def legado(api_client, manager_headers, process_payload):
    return publicar_na_versao_anterior(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )


def test_a_versao_vigente_publica_nao_e_elevada(api_client, legado):
    resposta = api_client.get(f"/api/v1/public/editais/{legado.id}/versao-vigente")

    assert resposta.status_code == 200, resposta.content
    conteudo = resposta.json()["content"]
    assert conteudo["schemaVersion"] == 4
    for etapa in conteudo["stages"]:
        assert not any(chave in etapa for chave in PROPRIEDADES_DO_INCREMENTO)


def test_o_hash_publicado_continua_cobrindo_o_que_a_consulta_serve(api_client, legado):
    """A afirmação que a elevação no caminho público quebraria."""
    resposta = api_client.get(f"/api/v1/public/editais/{legado.id}/versao-vigente")
    conteudo = resposta.json()["content"]

    versao = legado.versoes_consolidadas.get()
    assert canonical_sha256(conteudo) == versao.content_hash


def test_a_publicacao_original_serve_o_que_foi_publicado(api_client, legado):
    publicacao = legado.publicacoes.get()

    resposta = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}")

    assert resposta.status_code == 200, resposta.content
    assert resposta.json()["contentHash"] == publicacao.content_hash


def test_o_seletor_do_dominio_publico_tambem_e_literal(legado):
    """`selecao_publica` alimenta a vitrine e a inscrição: elevar ali vazaria para o candidato."""
    selecao = selecao_publica(edital_id=legado.id)

    for etapa in selecao.content["stages"]:
        assert not any(chave in etapa for chave in PROPRIEDADES_DO_INCREMENTO)
