"""A instalação existente continua igual, e o que foi publicado não muda (110, FR-3323, FR-3337).

O Cefor da instalação funciona sem nenhuma ação depois da atualização (item 1 do pedido). E editar
a unidade pela aplicação muda os próximos atos, e não os publicados: a Publicação congela a unidade
do dia (`060`), e o documento é o que foi gravado (item 12 do pedido, SC-1045).
"""

import hashlib

import pytest

from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.application import identificacao, registro
from processo_seletivo.unidades.application.selectors import exigir_unidade
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.autoridades import CEFOR
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ADMINISTRADORA = Actor("pessoa-administradora", "institucional", frozenset({"unidade:administrar"}))


def test_o_cefor_continua_sem_acao():
    """FR-3337: sem migração de dado; a unidade registrada é a de antes, e opera."""
    cefor = exigir_unidade("cefor", ativa=True)

    assert (cefor.sigla, cefor.nome, cefor.cabecalho, cefor.local) == (
        CEFOR["sigla"],
        CEFOR["nome"],
        CEFOR["cabecalho"],
        CEFOR["local"],
    )
    assert identificacao.da_implantacao().rotulo == "Cefor/Ifes"


def _estado(publicacao):
    documento = DocumentoPublicado.objects.get(publicacao=publicacao)
    publicacao.refresh_from_db()
    return {
        "documento": hashlib.sha256(bytes(documento.bytes)).hexdigest(),
        "document_hash": documento.document_hash,
        "content_hash": publicacao.content_hash,
        "unidade": (
            publicacao.unidade_codigo,
            publicacao.unidade_sigla,
            publicacao.unidade_nome,
            publicacao.unidade_cabecalho,
            publicacao.unidade_local,
        ),
    }


def test_editar_a_unidade_nao_muda_o_publicado(api_client, manager_headers, process_payload):
    """FR-3323, SC-1045: byte a byte, o documento e o conteúdo publicados são os do dia."""
    edital = publish_original(api_client, manager_headers, process_payload)
    publicacao = Publicacao.objects.get(edital=edital)
    antes = _estado(publicacao)
    cefor = Unidade.objects.get(codigo="cefor")
    campos = {
        "sigla": "Cefor-Novo",
        "nome": "Nome novo do Cefor",
        "cabecalho": ["Cabeçalho novo"],
        "local": "Serra (ES)",
        "atendimento": "novo@ifes.edu.br",
    }
    versao = registro.conferir_alteracao(ADMINISTRADORA, codigo="cefor", campos=campos)["versao"]

    registro.alterar(ADMINISTRADORA, codigo="cefor", campos=campos, versao=versao, motivo="Teste")

    assert _estado(publicacao) == antes
    assert antes["unidade"] == (
        "cefor",
        cefor.sigla,
        cefor.nome,
        cefor.cabecalho,
        cefor.local,
    ), "a Publicação guarda a unidade do dia, e não a de agora"
