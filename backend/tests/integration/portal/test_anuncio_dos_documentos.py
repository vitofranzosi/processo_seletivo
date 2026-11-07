"""A página pública conta os obrigatórios a todos e marca o facultativo (132, US4).

O resumo dizia "4 documentos que serão pedidos" somando o facultativo e o que só uma modalidade
pede, e nenhum facultativo vinha marcado: quem lê antes de se inscrever tomava o facultativo por
obrigatório e a soma por sua. A conta passou a ser a dos obrigatórios pedidos na inscrição a todos
do Perfil (FR-4513, decisão do usuário de 07/11/2026), e a lista marca o facultativo em todo grupo
(FR-4514).
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.portal.views import _documentos_anunciados
from processo_seletivo.publicacoes.application import selectors
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

PERFIL_DOCENTE = identificador(401, 0)
PERFIL_TECNICO = identificador(406, 0)
MODALIDADE_PPI = identificador(404, 0)
MARCA = '<span class="ajuda">(facultativo)</span>'


def _documento(numero, nome, ordem, **campos):
    return {
        "id": identificador(numero, 0),
        "key": f"doc{numero}",
        "name": nome,
        "required": True,
        "order": ordem,
        **campos,
    }


def _publicar(api_client, manager_headers, process_payload, documentos):
    rascunho = rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
    rascunho["documentRequirements"] = documentos
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


@pytest.fixture
def selecao(api_client, manager_headers, process_payload):
    """Docente: dois obrigatórios a todos do Perfil, um facultativo e um da modalidade reservada.
    Técnico: só o facultativo na inscrição. A convocação pede um facultativo a todos."""
    return _publicar(
        api_client,
        manager_headers,
        process_payload,
        [
            _documento(501, "Documento de identificação", 1, profileId=PERFIL_DOCENTE),
            _documento(502, "Diploma de graduação", 2, profileId=PERFIL_DOCENTE),
            _documento(503, "Currículo", 3, required=False),
            _documento(504, "Autodeclaração étnico-racial", 4, modalityId=MODALIDADE_PPI),
            _documento(505, "Comprovante de residência", 5, moment="AT_CALL", required=False),
        ],
    )


def _anunciados(edital, perfil_id):
    conteudo = selectors.selecao_publica(edital_id=edital.id).content
    perfil = next(p for p in conteudo["profiles"] if p["id"] == perfil_id)
    return _documentos_anunciados(conteudo, perfil)


def _cartao(corpo, nome):
    """O cartão do Perfil na lista de vagas: o nome aparece também no sumário do topo da página."""
    (cartao,) = [trecho for trecho in corpo.split('<li class="perfil"')[1:] if nome in trecho]
    return cartao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_conta_e_a_dos_obrigatorios_a_todos_na_inscricao(selecao):
    """SC-1405: nem o facultativo, nem o da modalidade, nem o da convocação entram na conta."""
    docente = _anunciados(selecao, PERFIL_DOCENTE)

    assert docente["total"] == 2
    assert docente["sempre"] == ["Documento de identificação", "Diploma de graduação", "Currículo"]
    assert [d.obrigatorio for d in docente["sempre"]] == [True, True, False]
    assert _anunciados(selecao, PERFIL_TECNICO)["total"] == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_resumo_diz_o_criterio_da_conta(client, selecao):
    corpo = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()

    docente = _cartao(corpo, "Professor de Informática")
    assert re.search(r"<summary>\s*2 documentos obrigatórios na inscrição\s*</summary>", docente)
    assert "que serão pedidos" not in corpo, "a frase antiga somava tudo"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_obrigatorio_a_todos_o_resumo_nao_diz_zero(client, selecao):
    """FR-4515: o técnico só tem o facultativo na inscrição."""
    corpo = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()

    tecnico = _cartao(corpo, "Técnico de Laboratório")
    assert "<summary>Documentos que podem ser pedidos na inscrição</summary>" in tecnico
    assert not re.search(r"<summary>\s*0 documento", corpo)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_todo_facultativo_leva_a_marca_e_o_obrigatorio_nao(client, selecao):
    """FR-4514: na lista de todos e na da convocação, com a mesma marca da inscrição."""
    corpo = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()
    docente = _cartao(corpo, "Professor de Informática")

    assert f"<li>Currículo {MARCA}</li>" in docente
    assert f"<li>Comprovante de residência {MARCA}</li>" in docente, "a convocação também"
    assert "<li>Documento de identificação</li>" in docente
    assert "<li>Autodeclaração étnico-racial</li>" in docente


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_so_a_convocacao_pede_e_o_resumo_diz_isso(
    client, api_client, manager_headers, process_payload
):
    """FR-4515: o técnico nada apresenta na inscrição, e a convocação pede um documento a todos."""
    edital = _publicar(
        api_client,
        manager_headers,
        process_payload,
        [
            _documento(511, "Diploma de graduação", 1, profileId=PERFIL_DOCENTE),
            _documento(512, "Comprovante de residência", 2, moment="AT_CALL"),
        ],
    )
    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    tecnico = _cartao(corpo, "Técnico de Laboratório")
    assert "<summary>Documentos pedidos só na convocação</summary>" in tecnico
    assert "<li>Comprovante de residência</li>" in tecnico


def test_o_documento_anunciado_sobrevive_a_copia_e_ao_pickle():
    """Um `str` derivado se reconstrói por `cls(texto)`: o construtor recebe o nome, e a marca de
    obrigatório viaja no estado (revisão do PR #429)."""
    import copy
    import pickle

    from processo_seletivo.portal.views import DocumentoAnunciado

    facultativo = DocumentoAnunciado.do_requisito({"name": "Currículo", "required": False})

    for copia in (
        copy.copy(facultativo),
        copy.deepcopy(facultativo),
        pickle.loads(pickle.dumps(facultativo)),
    ):
        assert copia == "Currículo"
        assert copia.obrigatorio is False
