"""A forma que o domínio exige não pode divergir da que o contrato declara.

O domínio não lê o `openapi.yaml` em execução — ele vive em `specs/`, é artefato de processo e não é
distribuído com o pacote. A transcrição em `validation.py` é o preço disso, e este teste é o que
impede que ela vire uma segunda verdade: alterar o contrato sem alterar a transcrição falha aqui.
"""

from pathlib import Path

import pytest
import yaml

from processo_seletivo.editais.domain import validation
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs"
    / "001-processo-seletivo-editais"
    / "contracts"
    / "openapi.yaml"
)

TIPO_DO_CONTRATO = {
    "string": str,
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


@pytest.fixture(scope="module")
def esquemas():
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))["components"]["schemas"]


def declarado(esquema, nome):
    """As dimensões que a `005` verifica, extraídas de uma propriedade do contrato."""
    propriedade = esquema["properties"][nome]
    tipos = propriedade.get("type")
    if "$ref" in propriedade:  # Id → string com formato uuid
        tipos, formato = "string", "uuid"
    else:
        formato = propriedade.get("format", "")
    if isinstance(tipos, list):
        admite_nulo = "null" in tipos
        tipos = next(t for t in tipos if t != "null")
    else:
        admite_nulo = False
    return {
        "obrigatorio": nome in esquema["required"],
        "tipo": TIPO_DO_CONTRATO[tipos],
        "admite_nulo": admite_nulo,
        "formato": formato,
        "minimo": propriedade.get("minimum"),
        "valores": tuple(propriedade.get("enum", ())),
        "padrao": propriedade.get("pattern", ""),
    }


def transcrito(campo):
    return {
        "obrigatorio": True,
        "tipo": campo.tipo,
        "admite_nulo": campo.admite_nulo,
        "formato": campo.formato,
        "minimo": campo.minimo,
        "valores": campo.valores,
        "padrao": campo.padrao,
    }


# O nome do esquema de cada coleção declarada. É esta tabela que o teste de cobertura confronta
# com `COLECOES_PUBLICADAS`: uma coleção nova que nasça sem entrada aqui falha lá, em vez de
# simplesmente não ser mencionada — que era o modo de falha desta lista antes da `006`.
ESQUEMA_DA_COLECAO = {
    "profiles": "PerfilPublicado",
    "schedule": "EventoPublicado",
    "stages": "EtapaPublicada",
    "sections": "SecaoPublicada",
}

FORMAS = tuple(
    (ESQUEMA_DA_COLECAO[colecao], forma) for colecao, forma in validation.COLECOES_PUBLICADAS
)


@pytest.mark.contract
@pytest.mark.parametrize(("nome", "forma"), FORMAS)
def test_a_transcricao_cobre_todos_os_campos_do_contrato(esquemas, nome, forma):
    assert sorted(campo.nome for campo in forma) == sorted(esquemas[nome]["properties"])


@pytest.mark.contract
@pytest.mark.parametrize(("nome", "forma"), FORMAS)
def test_a_transcricao_confere_dimensao_por_dimensao(esquemas, nome, forma):
    esquema = esquemas[nome]
    divergentes = {
        campo.nome: (transcrito(campo), declarado(esquema, campo.nome))
        for campo in forma
        if transcrito(campo) != declarado(esquema, campo.nome)
    }
    assert divergentes == {}


@pytest.mark.contract
@pytest.mark.parametrize(("nome", "forma"), FORMAS)
def test_todo_campo_do_conteudo_publicado_e_obrigatorio(esquemas, nome, forma):
    """No conteúdo publicado não há campo opcional.

    Obrigatório aqui significa presente, e não preenchido.
    """
    assert sorted(esquemas[nome]["required"]) == sorted(esquemas[nome]["properties"])


@pytest.mark.contract
def test_os_esquemas_de_entrada_nao_foram_promovidos_a_saida(esquemas):
    """A distinção que a revisão do plano encontrou: entrada exige 5 dos 12 campos publicados."""
    entrada = set(esquemas["PerfilInput"]["required"])
    publicado = set(esquemas["PerfilPublicado"]["required"])

    assert entrada < publicado
    assert "requirements" in publicado - entrada, (
        "requisitos ficariam sem verificação se a entrada fosse a autoridade"
    )


@pytest.mark.contract
def test_o_contrato_declara_o_codigo_da_recusa():
    """`blocking_findings` era emitido em nove pontos e não aparecia no contrato.

    O schema `Problem` declara `code` como texto livre, então nada quebrava; o cliente é que nunca
    soube o que esperar. Esta feature passa a produzi-lo num momento novo e o declara.
    """
    assert CONTRATO.read_text(encoding="utf-8").count("blocking_findings") >= 3


@pytest.mark.contract
def test_o_contrato_diz_que_a_verificacao_alcanca_cada_fronteira(esquemas):
    """FR-003: o singular permitiria implementar só a primeira fronteira."""
    import yaml as _yaml

    contrato = _yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))
    publicar = contrato["paths"]["/admin/retificacoes/{retificacaoId}/publicacoes"]["post"]

    assert "cada versão consolidada que o ato materializa" in publicar["description"]
    assert "recusa o ato inteiro" in publicar["description"]


@pytest.mark.contract
def test_o_tipo_do_item_da_colecao_e_transcrito(esquemas):
    """`items: { type: object }` está escrito; conferi-lo é aplicar, não inventar."""
    declarado_no_contrato = esquemas["PerfilPublicado"]["properties"]["competitionModalities"]
    campo = next(c for c in validation.PERFIL_PUBLICADO if c.nome == "competitionModalities")

    assert TIPO_DO_CONTRATO[declarado_no_contrato["items"]["type"]] is campo.tipo_do_item


@pytest.mark.contract
def test_nenhum_outro_campo_declara_tipo_de_item(esquemas):
    """A transcrição não pode inventar restrição onde o contrato não a escreve."""
    for nome, forma in FORMAS:
        for campo in forma:
            propriedade = esquemas[nome]["properties"][campo.nome]
            tem_items = "items" in propriedade and "type" in propriedade["items"]
            assert (campo.tipo_do_item is not None) == tem_items, campo.nome


@pytest.mark.contract
def test_o_padrao_do_instante_e_o_do_contrato(esquemas):
    """O padrão não é interpretação nossa da norma: é transcrição do que o contrato escreve.

    Ele é deliberadamente mais estreito que RFC 3339 — descreve a forma que o sistema materializa.
    Se um dia ele mudar no contrato sem mudar aqui, este teste falha antes de a divergência virar
    recusa indevida.
    """
    for campo in ("startAt", "endAt"):
        assert esquemas["EventoPublicado"]["properties"][campo]["pattern"] == validation.INSTANTE


@pytest.mark.contract
def test_toda_colecao_declarada_tem_esquema_no_contrato(esquemas):
    """A ponte entre a declaração do domínio e a do contrato, nomeada e não convencionada.

    Derivar o nome do esquema da chave da coleção — `stages` → `EtapaPublicada` — exigiria uma
    convenção que o repositório não tem e que a próxima coleção quebraria. A tabela é explícita, e
    o que este teste garante é que ela cubra tudo o que o domínio declara e aponte para esquemas
    que existem.
    """
    declaradas = {colecao for colecao, _ in validation.COLECOES_PUBLICADAS}

    assert declaradas <= set(ESQUEMA_DA_COLECAO), (
        "coleção declarada no domínio sem esquema nomeado: "
        f"{sorted(declaradas - set(ESQUEMA_DA_COLECAO))}"
    )
    ausentes = [ESQUEMA_DA_COLECAO[colecao] for colecao in declaradas]
    assert [nome for nome in ausentes if nome not in esquemas] == []


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_toda_colecao_de_entidades_do_snapshot_esta_declarada(
    esquemas, api_client, manager_headers, process_payload
):
    """A cobertura que não existia, e cuja ausência esta feature descobriu (FR-046).

    Até aqui, a conferência da forma publicada era feita contra uma lista nomeada item a item:
    acrescentar uma coleção ao snapshot e esquecer de declará-la em `COLECOES_PUBLICADAS` não
    fazia falhar nada — a lista simplesmente não a mencionava. Isto liga as três declarações:
    o que o snapshot produz, o que o domínio verifica, e o que o contrato descreve.

    O snapshot vem de um Edital publicado de verdade, e não de uma fixture: uma coleção nova
    nasce em `edital_snapshot`, e é lá que ela precisa ser encontrada.
    """
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.snapshot import rascunho_com_etapas

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    conteudo = VersaoConsolidada.objects.get(edital=edital).content

    de_entidades = {
        chave
        for chave, valor in conteudo.items()
        if isinstance(valor, list)
        and valor
        and all(isinstance(item, dict) and "id" in item for item in valor)
    }
    declaradas = {colecao for colecao, _ in validation.COLECOES_PUBLICADAS}

    assert de_entidades == declaradas, (
        "coleção-raiz de entidades no snapshot sem forma declarada, ou o contrário: "
        f"{sorted(de_entidades ^ declaradas)}"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_a_identidade_da_secao_e_a_mesma_antes_e_depois_de_editar_e_republicar(
    api_client, manager_headers, process_payload
):
    """D-010: determinística de propósito, e não aleatória.

    A seção precisa ter identidade **antes de existir linha em `SecaoEdital`** — a gerada nunca tem
    linha, e a textual só passa a ter depois da primeira edição. Derivá-la de `(edital.id, key)` dá
    identidade estável desde o primeiro snapshot, e é o que torna a coleção endereçável por uma
    Retificação elaborada sobre um conteúdo anterior à edição.
    """
    from processo_seletivo.editais.domain import secoes as catalogo
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash
    from tests.fixtures.publicacao import publish_original, retify

    edital = publish_original(api_client, manager_headers, process_payload)
    primeira = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = f"/sections/id={catalogo.identidade(edital.id, 'recursos')}/content"
    antes = {item["key"]: item["id"] for item in primeira.content["sections"]}

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": caminho,
                "operation": "REPLACE",
                "newValue": "Outro prazo recursal.",
                "expectedPreviousHash": previous_hash(primeira.content, caminho),
            }
        ],
        suffix="i",
    )

    segunda = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert {item["key"]: item["id"] for item in segunda.content["sections"]} == antes
    editada = next(item for item in segunda.content["sections"] if item["key"] == "recursos")
    assert editada["content"] == "Outro prazo recursal.", "o conteúdo mudou; a identidade não"
