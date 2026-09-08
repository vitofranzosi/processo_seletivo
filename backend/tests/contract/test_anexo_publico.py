"""A rota pública do artefato de Anexo (020, FR-039, FR-041, FR-042, FR-043, FR-052).

O endereço é o do **artefato**, e não o do par publicação-anexo. Sendo imutável, ele resolve "o de
então" por construção — não há outro que ele pudesse resolver —, e é isso que permite o cache
`immutable` e dispensa consultar versão nenhuma para responder.
"""

import pytest
from django.urls import reverse

from tests.fixtures.anexos import criar_artefato, pdf_de_teste

pytestmark = [pytest.mark.contract, pytest.mark.django_db]


def endereco(artefato):
    return reverse("public-anexo", args=[artefato.id])


def test_o_artefato_publicado_e_entregue_a_quem_nao_se_identifica(api_client):
    """É norma: exigir identificação para ler o Edital seria a fronteira no lugar errado."""
    artefato = criar_artefato(marca="A", congelado=True)

    resposta = api_client.get(endereco(artefato))

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"
    assert b"".join(resposta.streaming_content if resposta.streaming else [resposta.content])


def test_o_artefato_carrega_resumo_e_cache_de_conteudo_imutavel(api_client):
    artefato = criar_artefato(marca="A", congelado=True)

    resposta = api_client.get(endereco(artefato))

    assert resposta["ETag"] == f'"{artefato.document_hash}"'
    assert resposta["Cache-Control"] == "public, max-age=31536000, immutable"
    assert resposta["Content-Disposition"].startswith("attachment")


def test_quem_ja_tem_a_mesma_representacao_recebe_304(api_client):
    """A assimetria que a `PublishedDocumentView` tem e esta rota não repete: sem isto, cada
    revalidação transferiria o arquivo inteiro de novo."""
    artefato = criar_artefato(marca="A", congelado=True)

    resposta = api_client.get(endereco(artefato), HTTP_IF_NONE_MATCH=f'"{artefato.document_hash}"')

    assert resposta.status_code == 304


def test_o_artefato_nao_publicado_responde_404_e_nao_403(api_client):
    """Dizer "existe, mas não é público" já entregaria que existe (FR-017)."""
    artefato = criar_artefato(marca="A")

    assert api_client.get(endereco(artefato)).status_code == 404


def test_dois_artefatos_de_conteudos_distintos_tem_resumos_distintos(api_client):
    """O que separa esta feature de um gerenciador de arquivos: os dois coexistem (FR-042)."""
    antigo = criar_artefato(marca="A", congelado=True)
    novo = criar_artefato(marca="B", congelado=True)

    respostas = [api_client.get(endereco(item)) for item in (antigo, novo)]

    assert [resposta.status_code for resposta in respostas] == [200, 200]
    assert antigo.document_hash != novo.document_hash
    assert respostas[0].content != respostas[1].content


def test_artefatos_de_conteudo_identico_sao_legitimos(api_client):
    """O resumo é integridade, e não chave de unicidade — uma Retificação pode reverter outra."""
    primeiro = criar_artefato(marca="A", congelado=True)
    segundo = criar_artefato(marca="A", congelado=True)

    assert primeiro.id != segundo.id
    assert primeiro.document_hash == segundo.document_hash
    assert api_client.get(endereco(segundo)).content == pdf_de_teste("A")
