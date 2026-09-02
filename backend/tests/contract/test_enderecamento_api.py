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
from tests.fixtures.edital import actor_headers
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


def test_the_grammar_document_states_that_identity_is_not_content():
    """Um cliente que leia só o contrato precisa saber por que a recusa acontece."""
    gramatica = gramatica_corrida()
    assert "A identidade é substrato, não conteúdo" in gramatica
    assert "carrega `id` UUID" in gramatica
    assert "não é endereçável" in gramatica
    assert "A topologia das identidades só muda onde o ato a endereça" in gramatica
    assert "só aparece por `ADD /colecao/-` e só desaparece por" in gramatica


def test_the_grammar_document_says_what_the_identity_rule_does_not_cover():
    """Declarar o limite é o que separa uma garantia de uma impressão de garantia."""
    gramatica = gramatica_corrida()
    assert "O que esta regra não cobre" in gramatica
    assert "não vigia a forma dos campos" in gramatica or "não a forma dos campos" in gramatica
    # A saída precisa estar nomeada corretamente: validar o valor de cada alteração não alcança
    # o `REMOVE`, que não tem valor nenhum.
    assert "validar o valor de cada alteração não fecharia a família" in gramatica
    assert "validar o **snapshot resultante**" in gramatica


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_stages_e_enderecavel_por_chave_sem_alterar_a_gramatica(
    api_client, manager_headers, process_payload
):
    """FR-024: a coleção nova entra pelo registro declarativo, e nada na gramática muda.

    É a prova de que `stages` não precisou de código de endereçamento próprio: declarada em
    `COLECOES_COM_CHAVE`, ela ganhou seletor por `id=<uuid>`, token de acréscimo e recusa
    posicional pelo mesmo mecanismo que já servia a Perfis e Eventos.
    """
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash
    from tests.fixtures.snapshot import ETAPA, rascunho_com_etapas

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = f"/stages/id={ETAPA['A']}/name"

    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": caminho,
                "operation": "REPLACE",
                "newValue": "Prova didática e arguição",
                "expectedPreviousHash": previous_hash(base.content, caminho),
            }
        ],
        suffix="e",
    )
    publish_retification(api_client, retificacao, suffix="e")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    etapa = next(item for item in vigente.content["stages"] if item["id"] == ETAPA["A"])
    assert etapa["name"] == "Prova didática e arguição"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_acrescentar_etapa_usa_o_token_de_fim_de_lista(
    api_client, manager_headers, process_payload
):
    from tests.fixtures.snapshot import rascunho_com_etapas

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    nova = {
        "id": "00000000-0000-0000-0000-000000000563",
        "name": "Entrevista",
        "order": 3,
        "weight": None,
        "eliminatory": False,
        "classificatory": True,
        "minimumScore": None,
        "scheduleEventId": None,
    }
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": "/stages/-", "operation": "ADD", "newValue": nova}],
        suffix="f",
    )
    publish_retification(api_client, retificacao, suffix="f")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [item["name"] for item in vigente.content["stages"]][-1] == "Entrevista"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_enderecar_etapa_por_posicao_e_recusado(api_client, manager_headers, process_payload):
    """A coleção tem chave; a posição deixa de ser forma admitida no mesmo instante."""
    from tests.fixtures.snapshot import rascunho_com_etapas

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Endereçamento posicional",
            "changes": [{"targetPath": "/stages/0/name", "operation": "REPLACE", "newValue": "X"}],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key="posicional-000001"),
    )

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == "positional_addressing_refused"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_percentual_da_regra_e_retificavel_pelo_caminho_ja_existente(
    api_client, manager_headers, process_payload
):
    """FR-032: nenhuma coleção nova no snapshot, e nenhum caminho novo na gramática.

    `/profiles/*/competitionModalities` já era coleção com chave declarada; o que faltava era a
    identidade da modalidade ser estável entre gravações, sem o que o caminho apontaria, a cada
    salvamento, para outra coisa.
    """
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash
    from tests.fixtures.snapshot import MODALIDADE, PERFIL
    from tests.fixtures.snapshot import rascunho_publicavel as rascunho

    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho())
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = (
        f"/profiles/id={PERFIL['A']}/competitionModalities/id={MODALIDADE['B']}"
        "/normativeRule/percentage"
    )

    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": caminho,
                "operation": "REPLACE",
                "newValue": "25",
                "expectedPreviousHash": previous_hash(base.content, caminho),
            }
        ],
        suffix="p",
    )
    publish_retification(api_client, retificacao, suffix="p")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil = next(item for item in vigente.content["profiles"] if item["id"] == PERFIL["A"])
    modalidade = next(
        item for item in perfil["competitionModalities"] if item["id"] == MODALIDADE["B"]
    )
    assert modalidade["normativeRule"]["percentage"] == "25"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_conteudo_de_secao_textual_e_retificavel_e_o_de_gerada_nao(
    api_client, manager_headers, process_payload
):
    """D-006: a recusa da seção gerada não é regra — é consequência de não haver campo.

    `REPLACE /sections/id=<gerada>/content` falha pelo erro de caminho inexistente que a `004` já
    implementava. Recusá-la por regra nova na gramática custaria mais código, mais um erro nomeado,
    e contrariaria a decisão de não mexer no endereçamento.
    """
    from processo_seletivo.editais.domain import secoes as catalogo
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash

    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    textual = f"/sections/id={catalogo.identidade(edital.id, 'recursos')}/content"
    gerada = f"/sections/id={catalogo.identidade(edital.id, 'cronograma')}/content"

    recusada = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Conteúdo de seção gerada",
            "changes": [
                {
                    "targetPath": gerada,
                    "operation": "REPLACE",
                    "newValue": "Cronograma copiado à mão",
                    "expectedPreviousHash": "f" * 64,
                }
            ],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key="secao-gerada-00001"),
    )
    assert recusada.status_code == 422, recusada.content
    assert recusada.json()["code"] == "invalid_change"
    assert "Caminho inexistente" in recusada.json()["detail"]

    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": textual,
                "operation": "REPLACE",
                "newValue": "Recurso em até três dias úteis.",
                "expectedPreviousHash": previous_hash(base.content, textual),
            }
        ],
        suffix="t",
    )
    publish_retification(api_client, retificacao, suffix="t")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    secao = next(item for item in vigente.content["sections"] if item["key"] == "recursos")
    assert secao["content"] == "Recurso em até três dias úteis."
