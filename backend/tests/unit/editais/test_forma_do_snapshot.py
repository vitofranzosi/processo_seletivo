"""A forma de cada Perfil e Evento do conteúdo publicado.

Cinco dimensões — presença, tipo, nulabilidade, formato e as restrições que o contrato já escreve —
e a fronteira que as separa do que **não** é violação: valor vazio admissível, nulo onde se admite
nulo, e campo que o contrato não declara.
"""

import pytest

from processo_seletivo.editais.domain import validation as v
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from tests.fixtures.snapshot import (
    AUSENTE,
    PERFIL,
    VIOLACOES_DE_EVENTO,
    VIOLACOES_DE_PERFIL,
    com_violacao,
    conteudo_normativo,
    perfil_mutilado,
)

P1 = PERFIL["A"]


def impeditivos(conteudo):
    return blocking_findings(validate_for_publication(conteudo))


# --- As cinco violações ---------------------------------------------------------------------


@pytest.mark.parametrize(("rotulo", "campo", "valor"), VIOLACOES_DE_PERFIL)
def test_cada_violacao_no_perfil_e_erro_impeditivo(rotulo, campo, valor):
    achados = impeditivos(com_violacao(conteudo_normativo(), "profiles", 0, campo, valor))

    assert len(achados) == 1, rotulo
    assert achados[0].path.endswith(f"/{campo}")
    assert campo in achados[0].message or "identificador" in achados[0].message


@pytest.mark.parametrize(("rotulo", "campo", "valor"), VIOLACOES_DE_EVENTO)
def test_cada_violacao_no_evento_e_erro_impeditivo(rotulo, campo, valor):
    achados = impeditivos(com_violacao(conteudo_normativo(), "schedule", 0, campo, valor))

    assert len(achados) == 1, rotulo
    assert achados[0].path.startswith("/schedule/id=")


@pytest.mark.parametrize(
    ("campo", "valor", "codigo"),
    [
        ("name", AUSENTE, v.CAMPO_AUSENTE),
        ("name", [], v.TIPO_INVALIDO),
        ("locality", None, v.NULO_INVALIDO),
        ("id", "não-é-uuid", v.FORMATO_INVALIDO),
        ("immediateVacancies", -3, v.RESTRICAO_VIOLADA),
        ("reserveType", "QUALQUER", v.RESTRICAO_VIOLADA),
    ],
)
def test_o_achado_diz_qual_violacao_ocorreu(campo, valor, codigo):
    """FR-011: sem isto, quem recebe sabe onde e não sabe o quê."""
    achados = impeditivos(com_violacao(conteudo_normativo(), "profiles", 0, campo, valor))

    assert achados[0].code == codigo


def test_booleano_nao_conta_como_numero():
    """`bool` é subclasse de `int` em Python, e `True` não é um número de vagas."""
    achados = impeditivos(
        com_violacao(conteudo_normativo(), "profiles", 0, "immediateVacancies", True)
    )

    assert achados[0].code == v.TIPO_INVALIDO


def test_o_perfil_reduzido_aos_campos_de_entrada_e_recusado():
    """O caso que motivou a feature: cada campo é plausível, e o conjunto não é um Perfil."""
    conteudo = conteudo_normativo()
    conteudo["profiles"][0] = perfil_mutilado(P1)

    ausentes = {a.path.rsplit("/", 1)[1] for a in impeditivos(conteudo)}
    assert ausentes == {
        "description",
        "requirements",
        "reserveLimit",
        "locality",
        "classificationInformation",
        "callInformation",
        "competitionModalities",
    }


def test_item_que_nem_objeto_e_tem_caminho_posicional():
    conteudo = conteudo_normativo()
    conteudo["profiles"][1] = "nem é objeto"

    achados = impeditivos(conteudo)
    assert achados[0].code == v.TIPO_INVALIDO
    assert achados[0].path == "/profiles/1"


# --- O que NÃO é violação -------------------------------------------------------------------


def test_valor_vazio_admissivel_nao_e_ausencia():
    """FR-007: lista vazia continua sendo lista, e texto em branco continua sendo texto."""
    conteudo = conteudo_normativo()
    conteudo["profiles"][0].update(
        description="",
        locality="",
        requirements=[],
        classificationInformation={},
        callInformation={},
        competitionModalities=[],
    )

    assert impeditivos(conteudo) == []


def test_nulo_onde_se_admite_nulo_passa():
    conteudo = conteudo_normativo()
    conteudo["profiles"][0]["reserveLimit"] = None
    conteudo["schedule"][0]["endAt"] = None

    assert impeditivos(conteudo) == []


def test_campo_que_o_contrato_nao_declara_e_aceito():
    """FR-008: recusar o desconhecido tornaria toda evolução de esquema uma quebra."""
    conteudo = conteudo_normativo()
    conteudo["profiles"][0]["campoQueAindaNaoExiste"] = {"qualquer": "coisa"}
    conteudo["schedule"][0]["outroCampoNovo"] = 1

    assert impeditivos(conteudo) == []


def test_a_forma_das_modalidades_nao_e_verificada():
    """Limite declarado.

    A verificação alcança Perfil e Evento; a coleção de Modalidades é conferida como lista, e nada
    sobre o que há dentro dela.
    """
    conteudo = conteudo_normativo()
    conteudo["profiles"][0]["competitionModalities"] = [{"sem": "forma"}]

    assert impeditivos(conteudo) == []


def test_conteudo_integro_nao_produz_achado_impeditivo():
    assert impeditivos(conteudo_normativo()) == []


# --- O caminho ------------------------------------------------------------------------------


def test_o_caminho_nomeia_a_entidade_pela_chave():
    """FR-011: quem recebe identifica o Perfil sem consultar a versão vigente."""
    achados = impeditivos(com_violacao(conteudo_normativo(), "profiles", 2, "name", AUSENTE))

    assert achados[0].path == f"/profiles/id={PERFIL['C']}/name"


@pytest.mark.parametrize("colecao", ["profiles", "schedule"])
def test_colecao_que_nao_e_lista_nao_quebra_a_verificacao(colecao):
    """A `004` recusa isso na origem; aqui a função só não pode estourar.

    `validate_for_publication` lê conteúdo que ela não produziu — o caminho da Publicação original,
    a tela, um teste. Percorrer um objeto como se fosse coleção levantaria erro interno onde cabe,
    no máximo, o achado de raiz que já existe.
    """
    conteudo = conteudo_normativo()
    conteudo[colecao] = {"nem": "lista"}

    codigos = [a.code for a in impeditivos(conteudo)]
    assert v.TIPO_INVALIDO not in codigos
