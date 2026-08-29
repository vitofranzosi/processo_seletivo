"""O contrato precisa declarar a extensão, e não deixá-la implícita (FR-017, FR-018).

A gramática de `targetPath` é semântica local: o RFC 6901 não tem seleção por atributo. Quem
audita um ato publicado só consegue saber a quem o caminho se referia se a forma estiver
escrita. Estes testes verificam que está — no `openapi.yaml`, que é a fonte única da API, e no
documento de gramática desta feature.
"""

from pathlib import Path

import pytest
import yaml

from processo_seletivo.publicacoes.models_retificacao import (
    AlteracaoNormativa,
    VersaoConsolidada,
)
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification
from tests.fixtures.snapshot import PERFIL
from tests.fixtures.snapshot import rascunho_publicavel as rascunho

RAIZ = Path(__file__).resolve().parents[3]
CONTRATO = RAIZ / "specs" / "001-processo-seletivo-editais" / "contracts" / "openapi.yaml"
GRAMATICA = (
    RAIZ / "specs" / "004-enderecamento-normativo-estavel" / "contracts" / "enderecamento.md"
)
CODIGOS = ("positional_addressing_refused", "target_key_not_found", "duplicate_key_in_collection")


@pytest.fixture(scope="module")
def contrato():
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def target_path(contrato):
    return contrato["components"]["schemas"]["NormativeChange"]["properties"]["targetPath"][
        "description"
    ]


def test_the_contract_announces_the_extension_instead_of_disguising_it(target_path):
    assert "RFC 6901" in target_path
    assert "extensão local" in target_path
    assert "id=<uuid>" in target_path


def test_the_contract_states_the_container_rule(target_path):
    """A regra que importa: qual forma vale depende de o contêiner ser objeto ou lista."""
    assert "nome de chave literal" in target_path
    assert "não retira do RFC 6901" in target_path


def test_the_contract_states_that_the_comparison_is_exact_text(target_path):
    assert "texto exato" in target_path
    assert "sem" in target_path and "normalização de caixa" in target_path


def test_the_contract_states_the_form_of_add(contrato):
    operacao = contrato["components"]["schemas"]["NormativeChange"]["properties"]["operation"]
    assert '"-"' in operacao["description"]
    assert "Nenhuma outra folha serve" in operacao["description"]
    assert "inserção em posição específica" in operacao["description"]


def test_the_contract_states_what_may_enter_a_keyed_collection(contrato):
    """Sem esta regra escrita, um cliente montaria um Perfil sem `id` e o veria recusado sem saber
    por quê — e a razão é a própria garantia da feature."""
    operacao = contrato["components"]["schemas"]["NormativeChange"]["properties"]["operation"]
    assert '"id" no formato UUID' in operacao["description"]


def gramatica_corrida():
    """O documento é markdown com quebra de linha por largura; as frases atravessam linhas."""
    return " ".join(GRAMATICA.read_text(encoding="utf-8").split())


def test_the_grammar_document_states_that_add_only_takes_the_append_token():
    assert "`ADD` aceita `-` e nada mais" in gramatica_corrida()
    assert "precisa trazer a sua" in gramatica_corrida()


def test_the_grammar_document_states_when_uniqueness_is_checked():
    assert "depois de cada alteração, não só no estado final" in gramatica_corrida()


@pytest.mark.parametrize("codigo", CODIGOS)
def test_each_new_refusal_code_is_declared_where_it_is_produced(contrato, codigo):
    descricoes = " ".join(
        operacao.get("description", "")
        for caminho in contrato["paths"].values()
        for operacao in caminho.values()
        if isinstance(operacao, dict)
    )
    assert codigo in descricoes


def test_the_retired_code_is_gone_from_the_contract(contrato):
    """`target_identity_mismatch` respondia uma pergunta que o caminho passou a responder."""
    assert "target_identity_mismatch" not in CONTRATO.read_text(encoding="utf-8")


@pytest.mark.parametrize("codigo", CODIGOS)
def test_the_grammar_document_declares_each_code_with_its_status_and_moment(codigo):
    gramatica = GRAMATICA.read_text(encoding="utf-8")
    linha = next(linha for linha in gramatica.splitlines() if linha.startswith(f"| `{codigo}`"))
    assert linha.count("|") == 5, "cada código declara HTTP, quando e em que momento"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_published_path_identifies_the_entity_without_the_current_version(
    api_client, manager_headers, process_payload
):
    """FR-018: a auditabilidade é verificável, e não adjetivo.

    O caminho gravado no ato traz o identificador do Perfil. Quem audita compara esse
    identificador com o do Perfil em **qualquer** versão — inclusive uma anterior à Retificação —
    sem precisar saber que posição ele ocupava quando o ato foi elaborado.
    """
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho())
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PERFIL['C']}/name",
                "operation": "REPLACE",
                "newValue": "Renomeado",
            }
        ],
        suffix="a",
    )
    publish_retification(api_client, retificacao, suffix="a")

    alteracao = AlteracaoNormativa.objects.get(retificacao=retificacao)
    identificador = alteracao.target_path.split("id=")[1].split("/")[0]
    alvo = next(p for p in original.content["profiles"] if p["id"] == identificador)

    assert alvo["code"] == "P3"
    assert "/0" not in alteracao.target_path and "/1" not in alteracao.target_path, (
        "nenhum segmento do caminho publicado é posição"
    )
