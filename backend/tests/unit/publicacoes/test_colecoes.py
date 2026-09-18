"""O guarda de FR-012: quais coleções têm chave é declarado, e a declaração é verificada.

Detectar por introspecção — "o elemento é dict e tem `id`" — acerta hoje e erra em silêncio no
dia em que uma coleção nova nascer sem identificador. Estes testes existem para que esse dia
seja uma falha de suíte.
"""

from processo_seletivo.publicacoes.domain import colecoes
from tests.fixtures.snapshot import (
    ANEXO,
    FATO,
    MODALIDADE,
    PERFIL,
    colecoes_nao_declaradas,
    conteudo_normativo,
    elementos_sem_chave,
)


def test_every_collection_in_the_snapshot_is_declared():
    """Lista não declarada é coleção que ninguém decidiu se tem chave — e isso precisa doer."""
    assert colecoes_nao_declaradas(conteudo_normativo()) == []


def test_every_element_of_a_keyed_collection_carries_its_key():
    assert elementos_sem_chave(conteudo_normativo()) == []


def test_an_undeclared_collection_is_reported():
    """O guarda serve para alguma coisa: uma coleção nova aparece nele."""
    conteudo = conteudo_normativo()
    conteudo["annexes"] = [{"id": PERFIL["A"], "title": "Anexo I"}]
    assert colecoes_nao_declaradas(conteudo) == ["/annexes"]


def test_a_keyed_collection_missing_an_identifier_is_reported():
    conteudo = conteudo_normativo()
    del conteudo["profiles"][1]["id"]
    assert elementos_sem_chave(conteudo) == ["/profiles"]


def test_a_colecao_de_anexos_tem_chave():
    """Sem esta declaração o Anexo só resolveria por posição, e coleção inendereçável é coleção
    irretificável — a Retificação não conseguiria substituir o artefato de um anexo (020, FR-003).
    """
    assert colecoes.tem_chave("/attachments")
    assert not colecoes.e_atomica("/attachments")


def test_a_forma_de_convocacao_e_enderecavel_por_identidade():
    """O `callForm` do degrau 15 é alcançado por `/profiles/id=…/callForm` (019, `T025`).

    **Ele não é coleção, e por isso não entra em `COLECOES_COM_CHAVE`** — é campo escalar do
    Perfil. O que precisa valer é o que a `025` registrou como o detalhe que não teria conserto:
    que o endereço exista **antes** da primeira emissão. E existe porque `/profiles` é coleção com
    chave: o Perfil resolve por identidade, e o campo por nome dentro dele.

    O modo de errar aqui seria declará-lo como coleção por analogia com o quadro de vagas. Isso o
    faria ser percorrido como lista, e `declaradas_que_nao_sao_lista` acusaria o conteúdo publicado
    inteiro como malformado — a declaração ficaria falsa em silêncio.
    """
    assert colecoes.tem_chave("/profiles")
    assert not colecoes.tem_chave("/profiles/*/callForm")
    assert not colecoes.e_atomica("/profiles/*/callForm")
    assert not colecoes.e_campo_nao_retificavel("/profiles/*/callForm")
    assert not colecoes.e_campo_de_identidade("callForm")


def test_a_forma_de_convocacao_declarada_nao_quebra_a_topologia():
    """Um Perfil com a forma declarada continua percorrível, e nenhuma coleção some."""
    conteudo = conteudo_normativo()
    for perfil in conteudo["profiles"]:
        perfil["callForm"] = "INDIVIDUAL_MESSAGE"

    assert colecoes_nao_declaradas(conteudo) == []
    assert elementos_sem_chave(conteudo) == []
    assert colecoes.declaradas_que_nao_sao_lista(conteudo) == []


def test_a_colecao_do_quadro_de_vagas_tem_chave():
    """Declarada antes de o snapshot a emitir, e é essa ordem que a torna retificável (025, FR-170).

    Sem a declaração, `changes.py` recusaria o seletor `id=` e sobraria o endereçamento por
    posição — que o sistema proíbe. O primeiro Edital publicado com quadro nasceria irretificável, e
    endereço de retificação não se conserta depois: publicação é ato imutável.
    """
    assert colecoes.tem_chave("/profiles/*/vacancyTable")
    assert not colecoes.e_atomica("/profiles/*/vacancyTable")


def test_todo_anexo_carrega_a_sua_identidade():
    conteudo = conteudo_normativo()
    del conteudo["attachments"][1]["id"]
    assert elementos_sem_chave(conteudo) == ["/attachments"]


def test_a_identidade_do_anexo_nao_e_a_do_artefato():
    """Duas identidades, e o teste existe para que ninguém as funda depois.

    O `id` é do Anexo e sobrevive à Retificação; o `artifactId` é dos bytes daquela versão e muda
    quando a Retificação substitui o artefato. Confundi-los faria substituir o arquivo criar um
    anexo novo em silêncio, que é exatamente o que a D-001 proíbe.
    """
    conteudo = conteudo_normativo()
    primeiro = conteudo["attachments"][0]

    assert primeiro["id"] == ANEXO["A"]
    assert primeiro["artifactId"] != primeiro["id"]


def test_as_colecoes_sem_chave_sao_declaradas_uma_a_uma():
    """Eram uma; passaram a ser duas, e a lista continua literal de propósito.

    Uma coleção atômica é valor normativo substituído inteiro. `requirements` é lista de frases;
    `stages` de um marco é lista de identidades de Etapa — em nenhuma das duas há entidade a
    endereçar. Manter a lista escrita, e não derivada, é o que faz a terceira exigir uma decisão em
    vez de aparecer por acidente.
    """
    assert colecoes.COLECOES_ATOMICAS == frozenset(
        {
            "/profiles/*/requirements",
            "/profiles/*/classificationMilestones/*/stages",
        }
    )


def test_nested_collections_are_declared_by_shape_and_not_by_profile():
    """A regra vale para as Modalidades de qualquer Perfil, e não de um Perfil em particular."""
    assert colecoes.tem_chave("/profiles/*/competitionModalities")
    assert not colecoes.tem_chave(f"/profiles/id={PERFIL['A']}/competitionModalities")


def test_normative_rule_is_an_object_and_not_a_collection():
    """Ter `id` não faz de `normativeRule` item de lista: ela continua sendo nome de chave."""
    formas = {forma for forma, _ in colecoes.colecoes_com_chave(conteudo_normativo())}
    assert "/profiles/*/competitionModalities/*/normativeRule" not in formas


def test_control_lists_are_named_and_not_guessed():
    assert colecoes.e_controle_interno("applied_publications")
    assert not colecoes.e_controle_interno("profiles")


def test_the_shape_escapes_keys_so_a_slash_in_a_name_cannot_forge_a_collection():
    assert colecoes.escapar("a/b") == "a~1b"
    assert colecoes.escapar("a~b") == "a~0b"


def test_the_identity_topology_names_every_addressable_entity():
    """É o que a guarda compara antes e depois: caminho concreto, e não só o conjunto de chaves.

    Sem o caminho, `/profiles/id=A/competitionModalities` e a coleção de outro Perfil seriam
    indistinguíveis, e mover uma Modalidade de um Perfil para outro passaria por imutável.
    """
    topologia = colecoes.identidades(conteudo_normativo())

    assert f"/profiles/id={PERFIL['A']}" in topologia
    assert f"/profiles/id={PERFIL['A']}/competitionModalities/id={MODALIDADE['A']}" in topologia
    assert f"/profiles/id={PERFIL['B']}/declaredFacts/id={FATO['NASCIMENTO']}" in topologia
    assert f"/attachments/id={ANEXO['A']}" in topologia
    assert len(topologia) == 3 + 2 + 2 + 2 + 2 + 3 + 3, (
        "três Perfis, duas Modalidades do primeiro, dois Eventos, dois Fatos Declarados do "
        "segundo, dois Anexos, a linha geral do quadro de cada um dos três Perfis — que a `027` "
        "passou a materializar na gravação — e o marco classificatório de cada um dos três, que a "
        "`032` tornou precondição de publicar: um Perfil sem marco não classifica ninguém "
        "(`FR-457`), e o construtor deixou de produzir esse estado"
    )


def test_the_topology_skips_a_key_that_is_not_text_instead_of_breaking():
    """A função lê conteúdo que ela não produziu.

    Chave estranha é para ignorar, não para estourar.
    """
    conteudo = {"profiles": [{"id": ["lista"]}, {"id": PERFIL["A"]}, {"sem": "chave"}]}
    assert colecoes.identidades(conteudo) == {f"/profiles/id={PERFIL['A']}"}


def test_no_declared_collection_lives_under_a_collection_without_a_key():
    """A premissa que `identidades` assume, congelada como teste.

    A topologia percorre coleção com chave e para nas sem chave, porque dentro de uma coleção
    sem identificador não há caminho concreto a registrar. Se uma declaração futura pendurar uma
    coleção com chave sob uma sem, a topologia deixaria de enxergá-la — e a guarda de identidade
    passaria a aprovar em silêncio o que deveria recusar.
    """
    declaradas = colecoes.COLECOES_COM_CHAVE | colecoes.COLECOES_ATOMICAS
    for forma in declaradas:
        partes = forma.strip("/").split("/")
        ancestrais_lista = [
            "/" + "/".join(partes[:indice])
            for indice, parte in enumerate(partes)
            if parte == colecoes.CURINGA
        ]
        for ancestral in ancestrais_lista:
            assert colecoes.tem_chave(ancestral), (
                f"{forma} está sob {ancestral}, que não é coleção com chave"
            )
