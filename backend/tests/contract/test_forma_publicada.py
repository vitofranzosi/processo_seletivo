"""A forma que o domínio exige não pode divergir da que o contrato declara.

O domínio não lê o `openapi.yaml` em execução — ele vive em `specs/`, é artefato de processo e não é
distribuído com o pacote. A transcrição em `validation.py` é o preço disso, e este teste é o que
impede que ela vire uma segunda verdade: alterar o contrato sem alterar a transcrição falha aqui.
"""

from pathlib import Path

import pytest
import yaml

from processo_seletivo.editais.domain import validation

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs"
    / "001-processo-seletivo-editais"
    / "contracts"
    / "openapi.yaml"
)

TIPO_DO_CONTRATO = {"string": str, "integer": int, "array": list, "object": dict}


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
    }


def transcrito(campo):
    return {
        "obrigatorio": True,
        "tipo": campo.tipo,
        "admite_nulo": campo.admite_nulo,
        "formato": campo.formato,
        "minimo": campo.minimo,
        "valores": campo.valores,
    }


FORMAS = (
    ("PerfilPublicado", validation.PERFIL_PUBLICADO),
    ("EventoPublicado", validation.EVENTO_PUBLICADO),
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
