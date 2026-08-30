"""A gramática do segmento de caminho e a regra do contêiner.

Quatro formas de segmento — nome, índice, `-` e `id=<uuid>` — e qual delas vale depende de o
contêiner ser objeto ou lista. É essa dependência que preserva a expressividade do RFC 6901
enquanto elimina o endereçamento por posição de onde há chave.
"""

from copy import deepcopy

import pytest

from processo_seletivo.publicacoes.domain.changes import (
    ABSENT,
    AcrescimoPosicionado,
    CaminhoInexistente,
    ChaveNaoEncontrada,
    ColecaoAtomica,
    ColecaoDescaracterizada,
    EnderecamentoPosicional,
    EntidadeSemChave,
    IdentidadeImplicita,
    IdentidadeNaoEnderecavel,
    SeletorInvalido,
    add_overwrites,
    apply_change,
    resolve_path,
    selector_uuid,
)
from tests.fixtures.snapshot import MODALIDADE, PERFIL, conteudo_normativo

P1, P2, P3 = PERFIL["A"], PERFIL["B"], PERFIL["C"]
M1, M2 = MODALIDADE["A"], MODALIDADE["B"]


def alterado(conteudo, **change):
    resultado = deepcopy(conteudo)
    apply_change(resultado, change)
    return resultado


# --- As quatro formas ---------------------------------------------------------------------


def test_a_key_in_an_object_is_a_literal_name():
    conteudo = conteudo_normativo()
    assert resolve_path(conteudo, "/title") == "Edital de teste"


def test_a_selector_in_a_list_finds_the_element_by_its_identifier():
    conteudo = conteudo_normativo()
    assert resolve_path(conteudo, f"/profiles/id={P2}/name") == "Perfil B"


def test_the_selector_does_not_depend_on_the_position():
    """O ponto inteiro da feature: mover o Perfil na lista não muda de quem o caminho fala."""
    conteudo = conteudo_normativo()
    invertido = {**conteudo, "profiles": list(reversed(conteudo["profiles"]))}
    assert resolve_path(invertido, f"/profiles/id={P2}/name") == "Perfil B"


def test_the_append_token_never_resolves_to_a_value():
    assert resolve_path(conteudo_normativo(), "/profiles/-") is ABSENT


def test_an_index_over_a_keyed_collection_is_refused_and_not_merely_missing():
    with pytest.raises(EnderecamentoPosicional) as recusa:
        resolve_path(conteudo_normativo(), "/profiles/0/name")
    # A recusa nomeia o caminho e diz o que fazer no lugar (FR-010).
    assert "/profiles/0/name" in str(recusa.value)
    assert "id=<uuid>" in str(recusa.value)


# --- A regra do contêiner -----------------------------------------------------------------


def test_a_selector_over_an_object_is_a_literal_key_name():
    """FR-002: a extensão não retira do RFC 6901 nada que ele permitia."""
    conteudo = {"rotulos": {f"id={P1}": "valor literal"}}
    assert resolve_path(conteudo, f"/rotulos/id={P1}") == "valor literal"


def test_a_malformed_selector_over_an_object_is_still_a_literal_key_name():
    conteudo = {"rotulos": {"id=nao-e-uuid": "valor literal"}}
    assert resolve_path(conteudo, "/rotulos/id=nao-e-uuid") == "valor literal"


def test_a_malformed_selector_over_a_list_is_refused():
    with pytest.raises(SeletorInvalido):
        resolve_path(conteudo_normativo(), "/profiles/id=nao-e-uuid/name")


# --- A exigência de UUID ------------------------------------------------------------------


MISTO = "0000000a-0000-0000-0000-00000000bcde"


@pytest.mark.parametrize("token", [f"id={P1}", f"id={MISTO}", f"id={MISTO.upper()}"])
def test_a_well_formed_selector_yields_its_uuid(token):
    assert selector_uuid(token) == token.removeprefix("id=")


@pytest.mark.parametrize(
    "token",
    [
        "profiles",
        "0",
        "-",
        "id=",
        "id=123",
        "id=00000000-0000-0000-0000-00000000050",  # um dígito a menos
        "id=00000000-0000-0000-0000-0000000005011",  # um a mais
        "id=00000000_0000_0000_0000_000000000501",  # separador errado
        f"identidade={P1}",
    ],
)
def test_what_is_not_a_well_formed_selector_is_not_one(token):
    assert selector_uuid(token) is None


def test_the_comparison_is_exact_text_and_does_not_normalise_case():
    """Dois textos diferentes são duas chaves diferentes; normalizar criaria equivalência falsa.

    O UUID gravado no snapshot vem de `str(uuid4())`, sempre minúsculo. Aceitar a forma maiúscula
    faria o sistema resolver um identificador que não está lá — e a auditoria de um ato publicado
    passaria a depender de saber qual normalização o servidor aplicava na época.
    """
    conteudo = {"profiles": [{"id": MISTO, "name": "Perfil"}]}
    assert resolve_path(conteudo, f"/profiles/id={MISTO}/name") == "Perfil"
    with pytest.raises(ChaveNaoEncontrada):
        apply_change(
            conteudo,
            {
                "targetPath": f"/profiles/id={MISTO.upper()}/name",
                "operation": "REPLACE",
                "newValue": "X",
            },
        )


# --- Aninhamento e objetos com identificador ----------------------------------------------


def test_nested_collections_resolve_level_by_level():
    conteudo = conteudo_normativo()
    caminho = f"/profiles/id={P1}/competitionModalities/id={M2}/code"
    assert resolve_path(conteudo, caminho) == "PPI"


def test_a_nested_selector_ignores_a_modality_of_another_profile():
    conteudo = conteudo_normativo()
    caminho = f"/profiles/id={P2}/competitionModalities/id={M1}/code"
    with pytest.raises(ChaveNaoEncontrada):
        apply_change(conteudo, {"targetPath": caminho, "operation": "REMOVE"})


def test_normative_rule_is_addressed_by_key_even_though_it_carries_an_identifier():
    """FR-005: ter `id` não faz de um objeto elemento de coleção."""
    conteudo = conteudo_normativo()
    caminho = f"/profiles/id={P1}/competitionModalities/id={M2}/normativeRule/percentage"
    # O snapshot guarda percentual como texto, para não depender de ponto flutuante.
    assert resolve_path(conteudo, caminho) == "20"
    depois = alterado(conteudo, targetPath=caminho, operation="REPLACE", newValue="25")
    assert resolve_path(depois, caminho) == "25"


# --- Aplicação ----------------------------------------------------------------------------


def test_replace_by_key_hits_the_entity_and_not_the_position():
    conteudo = conteudo_normativo()
    depois = alterado(
        conteudo, targetPath=f"/profiles/id={P2}/name", operation="REPLACE", newValue="Renomeado"
    )
    assert [perfil["name"] for perfil in depois["profiles"]] == [
        "Perfil A",
        "Renomeado",
        "Perfil C",
    ]


def test_remove_by_key_removes_the_entity_and_leaves_the_others():
    conteudo = conteudo_normativo()
    depois = alterado(conteudo, targetPath=f"/profiles/id={P1}", operation="REMOVE")
    assert [perfil["id"] for perfil in depois["profiles"]] == [P2, PERFIL["C"]]


def test_removing_and_replacing_in_any_order_reaches_the_same_result():
    """Sem índice não há coreografia: a ordem das alterações deixou de ser a garantia."""
    conteudo = conteudo_normativo()
    remover = {"targetPath": f"/profiles/id={P1}", "operation": "REMOVE"}
    renomear = {
        "targetPath": f"/profiles/id={PERFIL['C']}/name",
        "operation": "REPLACE",
        "newValue": "Renomeado",
    }
    primeiro, segundo = deepcopy(conteudo), deepcopy(conteudo)
    for change in (remover, renomear):
        apply_change(primeiro, change)
    for change in (renomear, remover):
        apply_change(segundo, change)
    assert primeiro == segundo


def test_add_appends_at_the_end():
    conteudo = conteudo_normativo()
    novo = {"id": "00000000-0000-0000-0000-0000000005ff", "code": "P9", "name": "Novo"}
    depois = alterado(conteudo, targetPath="/profiles/-", operation="ADD", newValue=novo)
    assert depois["profiles"][-1]["id"] == novo["id"]


def test_add_by_index_is_refused_like_any_other_positional_form():
    with pytest.raises(EnderecamentoPosicional):
        apply_change(
            conteudo_normativo(),
            {"targetPath": "/profiles/1", "operation": "ADD", "newValue": {}},
        )


def test_replacing_a_key_that_is_not_there_is_key_not_found():
    with pytest.raises(ChaveNaoEncontrada) as recusa:
        apply_change(
            conteudo_normativo(),
            {
                "targetPath": "/profiles/id=00000000-0000-0000-0000-0000000005ff/name",
                "operation": "REPLACE",
                "newValue": "X",
            },
        )
    assert "0000000005ff" in str(recusa.value)


# --- Coleções atômicas e controle interno --------------------------------------------------


def test_an_atomic_collection_is_replaced_whole():
    conteudo = conteudo_normativo()
    caminho = f"/profiles/id={P1}/requirements"
    depois = alterado(conteudo, targetPath=caminho, operation="REPLACE", newValue=["Só este"])
    assert resolve_path(depois, caminho) == ["Só este"]


def test_an_atomic_collection_accepts_being_emptied():
    conteudo = conteudo_normativo()
    caminho = f"/profiles/id={P1}/requirements"
    depois = alterado(conteudo, targetPath=caminho, operation="REPLACE", newValue=[])
    assert resolve_path(depois, caminho) == []


@pytest.mark.parametrize("sufixo", ["/0", "/-", "/id=00000000-0000-0000-0000-0000000005ff"])
def test_an_atomic_collection_is_never_read_item_by_item(sufixo):
    with pytest.raises(ColecaoAtomica) as recusa:
        resolve_path(conteudo_normativo(), f"/profiles/id={P1}/requirements{sufixo}")
    assert "/profiles/*/requirements" in str(recusa.value)


@pytest.mark.parametrize("operacao", ["ADD", "REPLACE", "REMOVE"])
@pytest.mark.parametrize("sufixo", ["/0", "/-", "/id=00000000-0000-0000-0000-0000000005ff"])
def test_an_atomic_collection_is_never_written_item_by_item(operacao, sufixo):
    """Ler e aplicar são portas distintas, e a versão anterior só fechava a de ler.

    `ADD` com a folha `-` não passava por onde a recusa morava, e acrescentava um requisito à
    coleção que FR-011 declara atômica. Exercitar `resolve_path` dava a impressão de cobertura.
    """
    with pytest.raises(ColecaoAtomica):
        apply_change(
            conteudo_normativo(),
            {
                "targetPath": f"/profiles/id={P1}/requirements{sufixo}",
                "operation": operacao,
                "newValue": "clandestino",
            },
        )


def test_internal_control_lists_are_not_addressable():
    with pytest.raises(ValueError, match="controle interno"):
        apply_change(
            {"applied_publications": ["a"]},
            {"targetPath": "/applied_publications/0", "operation": "REMOVE"},
        )


# --- Coleção sem declaração: o índice continua valendo -------------------------------------

# Uma lista que nenhuma declaração alcança — conteúdo livre dentro de `classificationInformation`,
# por exemplo. Ali não há chave a usar, e recusar o índice deixaria o caminho sem forma alguma.
LIVRE = {"classificationInformation": {"criterios": ["a", "b", "c"]}}


def test_an_index_over_an_undeclared_list_is_still_admitted():
    assert resolve_path(LIVRE, "/classificationInformation/criterios/1") == "b"


def test_replacing_by_index_in_an_undeclared_list_works():
    depois = alterado(
        LIVRE,
        targetPath="/classificationInformation/criterios/2",
        operation="REPLACE",
        newValue="z",
    )
    assert depois["classificationInformation"]["criterios"] == ["a", "b", "z"]


def test_an_index_beyond_the_end_of_an_undeclared_list_does_not_resolve():
    assert resolve_path(LIVRE, "/classificationInformation/criterios/9") is ABSENT
    with pytest.raises(CaminhoInexistente):
        apply_change(
            deepcopy(LIVRE),
            {
                "targetPath": "/classificationInformation/criterios/9",
                "operation": "REPLACE",
                "newValue": "z",
            },
        )


# --- Caminhos que não resolvem --------------------------------------------------------------


def test_descending_through_an_index_beyond_the_end_does_not_resolve():
    with pytest.raises(CaminhoInexistente):
        apply_change(
            deepcopy(LIVRE),
            {
                "targetPath": "/classificationInformation/criterios/9/x",
                "operation": "REPLACE",
                "newValue": 1,
            },
        )


def test_a_relative_path_is_refused():
    with pytest.raises(ValueError, match="absoluto"):
        apply_change(conteudo_normativo(), {"targetPath": "title", "operation": "REMOVE"})


def test_descending_through_a_missing_object_key_does_not_resolve():
    with pytest.raises(CaminhoInexistente):
        apply_change(
            conteudo_normativo(),
            {"targetPath": "/inexistente/algum", "operation": "REPLACE", "newValue": 1},
        )


def test_descending_through_a_scalar_does_not_resolve():
    assert resolve_path(conteudo_normativo(), "/title/0") is ABSENT
    with pytest.raises(CaminhoInexistente):
        apply_change(
            conteudo_normativo(),
            {"targetPath": "/title/0/x", "operation": "REPLACE", "newValue": 1},
        )


def test_an_add_whose_parent_does_not_resolve_overwrites_nothing():
    """`add_overwrites` responde sobre conteúdo existente; caminho que não resolve não o tem."""
    assert add_overwrites(conteudo_normativo(), "/inexistente/algum") is False
    assert add_overwrites(conteudo_normativo(), "/title") is True


# --- `ADD` em lista só aceita a folha `-` (FR-006) ------------------------------------------


def test_add_by_selector_does_not_insert_before_the_selected_item():
    """O seletor resolveria a posição de uma entidade existente, e inserir antes dela é
    exatamente a operação em posição que esta feature retirou da gramática."""
    with pytest.raises(AcrescimoPosicionado) as recusa:
        apply_change(
            conteudo_normativo(),
            {
                "targetPath": f"/profiles/id={P2}",
                "operation": "ADD",
                "newValue": {"id": "00000000-0000-0000-0000-0000000005ff"},
            },
        )
    assert "token `-`" in str(recusa.value)


def test_add_by_index_over_a_keyed_collection_keeps_its_own_code():
    """Índice é endereçamento posicional antes de ser acréscimo: o código específico prevalece."""
    with pytest.raises(EnderecamentoPosicional):
        apply_change(
            conteudo_normativo(),
            {"targetPath": "/profiles/1", "operation": "ADD", "newValue": {"id": P1}},
        )


def test_add_by_index_in_an_undeclared_list_is_refused_too():
    """Não há inserção em posição em lista nenhuma — declarada ou não."""
    with pytest.raises(AcrescimoPosicionado):
        apply_change(
            deepcopy(LIVRE),
            {
                "targetPath": "/classificationInformation/criterios/1",
                "operation": "ADD",
                "newValue": "z",
            },
        )


def test_appending_to_an_undeclared_list_still_works():
    depois = alterado(
        LIVRE, targetPath="/classificationInformation/criterios/-", operation="ADD", newValue="d"
    )
    assert depois["classificationInformation"]["criterios"] == ["a", "b", "c", "d"]


# --- Quem entra numa coleção com chave precisa trazer a sua (FR-001) ------------------------


@pytest.mark.parametrize(
    "valor",
    [
        {"code": "SEM", "name": "Sem identificador"},
        {"id": "", "code": "VAZIO"},
        {"id": "nao-e-uuid", "code": "TORTO"},
        {"id": ["lista"], "code": "NAO_TEXTO"},
        {"id": {"objeto": 1}, "code": "NAO_TEXTO"},
        {"id": 42, "code": "NUMERO"},
        "nem sequer é objeto",
        None,
    ],
)
def test_appending_without_a_usable_key_is_refused(valor):
    with pytest.raises(EntidadeSemChave) as recusa:
        apply_change(
            conteudo_normativo(),
            {"targetPath": "/profiles/-", "operation": "ADD", "newValue": valor},
        )
    assert "UUID" in str(recusa.value)


def test_appending_with_a_well_formed_key_is_accepted():
    novo = {"id": "00000000-0000-0000-0000-0000000005ff", "code": "PX"}
    depois = alterado(
        conteudo_normativo(), targetPath="/profiles/-", operation="ADD", newValue=novo
    )
    assert depois["profiles"][-1]["id"] == novo["id"]


def test_an_undeclared_list_accepts_anything_because_it_has_no_key_to_demand():
    depois = alterado(
        LIVRE, targetPath="/classificationInformation/criterios/-", operation="ADD", newValue=42
    )
    assert depois["classificationInformation"]["criterios"][-1] == 42


# --- A identidade é substrato, e não conteúdo (FR-018) ---------------------------------------

# A primeira rodada de correções vigiava a operação — o `ADD` — em vez do estado. A mesma
# entidade sem chave entrava por outras quatro portas, e a identidade de uma entidade existente
# podia ser trocada ou apagada sem que nada acusasse.

NOVO_UUID = "00000000-0000-0000-0000-0000000005ff"


def substituir(caminho, valor):
    return {"targetPath": caminho, "operation": "REPLACE", "newValue": valor}


def perfil_intacto(**campos):
    return {**conteudo_normativo()["profiles"][0], **campos}


@pytest.mark.parametrize(
    ("descricao", "valor"),
    [
        ("id trocado por outro UUID", perfil_intacto(id=NOVO_UUID)),
        ("id trocado pelo de outro Perfil", perfil_intacto(id=P2)),
        ("Modalidades apagadas", {"id": P1, "code": "X"}),
        ("Modalidades com ids trocados", perfil_intacto(competitionModalities=[{"id": NOVO_UUID}])),
    ],
)
def test_replacing_a_whole_element_may_not_move_the_identities_inside_it(descricao, valor):
    """Comparar só o `id` do elemento substituído alcançava um caso de vários.

    Preservar o `id` do Perfil e apagar as Modalidades de dentro fazia um caminho já publicado
    deixar de resolver, sem que o ato tivesse endereçado nenhuma Modalidade.
    """
    with pytest.raises(IdentidadeImplicita) as recusa:
        apply_change(conteudo_normativo(), substituir(f"/profiles/id={P1}", valor))
    assert "não endereça" in str(recusa.value), descricao


def test_replacing_a_whole_element_keeping_every_identity_is_legitimate():
    depois = alterado(
        conteudo_normativo(),
        targetPath=f"/profiles/id={P1}",
        operation="REPLACE",
        newValue=perfil_intacto(name="Reescrito por inteiro"),
    )
    assert depois["profiles"][0]["name"] == "Reescrito por inteiro"
    assert [m["id"] for m in depois["profiles"][0]["competitionModalities"]] == [M1, M2]


@pytest.mark.parametrize(
    "change",
    [
        substituir(f"/profiles/id={P1}/id", NOVO_UUID),
        substituir(f"/profiles/id={P1}/id", "torto"),
        substituir(f"/profiles/id={P1}/id", ["lista"]),
        {"targetPath": f"/profiles/id={P1}/id", "operation": "REMOVE"},
        {"targetPath": f"/profiles/id={P1}/id", "operation": "ADD", "newValue": NOVO_UUID},
    ],
)
def test_the_identifier_of_an_entity_is_not_addressable(change):
    with pytest.raises(IdentidadeNaoEnderecavel):
        apply_change(conteudo_normativo(), change)


def test_a_nested_modality_identifier_is_not_addressable_either():
    with pytest.raises(IdentidadeNaoEnderecavel):
        apply_change(
            conteudo_normativo(),
            substituir(f"/profiles/id={P1}/competitionModalities/id={M1}/id", NOVO_UUID),
        )


def test_an_identifier_of_a_plain_object_stays_ordinary_content():
    """`normativeRule` tem `id` e não é elemento de coleção: o `id` dela não endereça nada."""
    caminho = f"/profiles/id={P1}/competitionModalities/id={M1}/normativeRule/id"
    depois = alterado(conteudo_normativo(), targetPath=caminho, operation="REPLACE", newValue="x")
    assert resolve_path(depois, caminho) == "x"


def test_replacing_a_whole_collection_may_not_drop_the_identifiers():
    with pytest.raises(EntidadeSemChave) as recusa:
        apply_change(conteudo_normativo(), substituir("/profiles", [{"code": "A"}, {"code": "B"}]))
    assert "/profiles" in str(recusa.value)


def test_replacing_a_whole_collection_may_not_swap_the_entities():
    """Trocar a lista por outras entidades é criar e destruir identidades sem endereçá-las."""
    with pytest.raises(IdentidadeImplicita):
        apply_change(
            conteudo_normativo(), substituir("/profiles", [{"id": NOVO_UUID, "code": "ÚNICO"}])
        )


def test_replacing_a_whole_collection_reordering_it_is_legitimate():
    """Ordem é conteúdo normativo; identidade não. Reordenar não move entidade nenhuma."""
    invertidos = list(reversed(conteudo_normativo()["profiles"]))
    depois = alterado(
        conteudo_normativo(), targetPath="/profiles", operation="REPLACE", newValue=invertidos
    )
    assert [p["id"] for p in depois["profiles"]] == [P3, P2, P1]


@pytest.mark.parametrize(
    "change",
    [
        substituir(f"/profiles/id={P1}/competitionModalities", []),
        {"targetPath": f"/profiles/id={P1}/competitionModalities", "operation": "REMOVE"},
    ],
)
def test_emptying_a_nested_collection_wholesale_is_refused(change):
    """Esvaziar a coleção retira identidades; retirá-las é ato declarado, uma a uma."""
    with pytest.raises(IdentidadeImplicita):
        apply_change(conteudo_normativo(), change)


def test_adding_and_removing_entities_by_their_own_paths_stays_allowed():
    """A recíproca das recusas acima: é assim que a topologia muda legitimamente."""
    acrescido = alterado(
        conteudo_normativo(),
        targetPath="/profiles/-",
        operation="ADD",
        newValue={"id": NOVO_UUID, "competitionModalities": [{"id": M1}]},
    )
    assert [p["id"] for p in acrescido["profiles"]] == [P1, P2, P3, NOVO_UUID]

    removido = alterado(conteudo_normativo(), targetPath=f"/profiles/id={P1}", operation="REMOVE")
    assert [p["id"] for p in removido["profiles"]] == [P2, P3]


# --- Uma coleção declarada continua sendo uma coleção ----------------------------------------


@pytest.mark.parametrize(
    "caminho, valor",
    [
        ("/profiles", {"a": 1}),
        ("/profiles", "nem lista"),
        ("/schedule", 42),
        (f"/profiles/id={P1}/requirements", "nem lista"),
    ],
)
def test_a_declared_collection_may_not_stop_being_one(caminho, valor):
    """FR-012 tem uma premissa: as coleções declaradas existem e são coleções.

    Trocar `/profiles` por um objeto tornava a declaração falsa em silêncio — nada percorreria a
    coleção, nenhum elemento seria verificado, e o caminho por chave deixaria de resolver.
    """
    with pytest.raises(ColecaoDescaracterizada) as recusa:
        apply_change(conteudo_normativo(), substituir(caminho, valor))
    assert caminho.split("/id=")[0] in str(recusa.value)


def test_an_atomic_collection_may_still_be_replaced_by_a_list():
    caminho = f"/profiles/id={P1}/requirements"
    depois = alterado(conteudo_normativo(), targetPath=caminho, operation="REPLACE", newValue=[])
    assert resolve_path(depois, caminho) == []


@pytest.mark.parametrize(
    ("descricao", "conteudo", "change"),
    [
        (
            "`-` como nome literal de chave num objeto",
            {"rules": {}},
            {"targetPath": "/rules/-", "operation": "ADD", "newValue": {"id": NOVO_UUID}},
        ),
        (
            "seletor como nome literal de chave num objeto",
            {"rules": {f"id={NOVO_UUID}": {"x": 1}}},
            {"targetPath": f"/rules/id={NOVO_UUID}", "operation": "REMOVE"},
        ),
    ],
)
def test_a_path_that_only_looks_like_a_collection_earns_no_identity_permission(
    descricao, conteudo, change
):
    """A permissão de mexer na topologia depende do contêiner, não da aparência do caminho.

    Nada é explorável por aqui hoje, porque nenhuma coleção declarada mora nesses lugares. Mas
    permissão concedida sobre premissa errada é o que fica esperando a próxima declaração.
    """
    from processo_seletivo.publicacoes.domain.changes import _identidade_permitida

    assert _identidade_permitida(change, change["targetPath"], "/rules") is None, descricao
    apply_change(conteudo, change)  # segue admitido: é chave de objeto, e não move identidade


def test_the_permission_is_granted_where_the_container_really_is_a_keyed_collection():
    from processo_seletivo.publicacoes.domain.changes import _identidade_permitida

    acrescimo = {"targetPath": "/profiles/-", "operation": "ADD", "newValue": {"id": NOVO_UUID}}
    assert _identidade_permitida(acrescimo, "/profiles/-", "/profiles") == (
        f"/profiles/id={NOVO_UUID}"
    )
    remocao = {"targetPath": f"/profiles/id={P1}", "operation": "REMOVE"}
    assert _identidade_permitida(remocao, f"/profiles/id={P1}", "/profiles") == f"/profiles/id={P1}"
