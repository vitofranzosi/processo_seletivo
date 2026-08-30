"""Precondições de conteúdo por caminho alterado (FR-026, FR-036).

`expectedPreviousHash` identifica o conteúdo que a pessoa responsável enxergava ao
elaborar a Alteração Normativa. Comparar esse hash com o conteúdo efetivamente vigente
no `targetPath` impede que uma Retificação sobrescreva silenciosamente outra publicada
no intervalo entre a elaboração e a Publicação.

O campo é opcional, mas `ADD` carrega uma precondição própria e não declarável: adicionar
pressupõe caminho ausente. Sem essa regra, um `ADD` sobre um caminho que outro ato criou
seria sobrescrita silenciosa que nem um cliente cuidadoso conseguiria evitar — não há como
declarar ausência num campo que guarda hash de conteúdo.

A regra vale apenas onde `ADD` de fato substitui, ou seja, em objeto. Em lista, `ADD` insere
e desloca os elementos seguintes, sem apagar nenhum: incluir um Perfil antes dos existentes
é ato legítimo e não configura sobrescrita.

As precondições valem contra o conteúdo que cada alteração encontra, e não contra o
conteúdo inicial: um ato pode remover um caminho e recriá-lo em seguida.

Declarar o hash é opcional para o cliente, mas a verificação não é opcional para o sistema.
Sem declaração, `derive_preconditions` extrai a precondição da própria base declarada em
`baseSnapshotId` — que é, por construção, o conteúdo que a pessoa enxergava ao elaborar o ato.
Sem isso, `REPLACE` e `REMOVE` passavam sem verificação alguma e, como os caminhos endereçam
coleções por índice, uma Retificação publicada no intervalo deslocava os índices e o ato
seguinte atingia em silêncio um item normativo diferente do homologado.

Hash de conteúdo, porém, responde "o valor ainda é este?", não "ainda é esta entidade?". Dois
Perfis podem ter a denominação idêntica, e aí o hash confere depois do deslocamento e o ato
altera o Perfil errado mesmo assim. `ADD` posicional não tem sequer valor anterior a comparar,
e deslocar a posição de inserção muda a ordem normativa publicada.

Por isso cada índice de lista atravessado por um caminho carrega também uma **âncora**: a
identidade da entidade que ocupava aquela posição na base. `id` quando a entidade tem um; o
hash do elemento inteiro quando não tem. A âncora é sempre derivada pelo servidor e não é
declarável pelo cliente: ela não descreve conteúdo, descreve de quem o ato fala. Enquanto o
endereçamento por chave estável não substituir os índices, é ela que sustenta a garantia.
"""

from copy import deepcopy

from processo_seletivo.publicacoes.domain.changes import (
    ABSENT,
    add_overwrites,
    apply_change,
    parse_path,
    resolve_path,
)
from processo_seletivo.shared.canonical import canonical_sha256

HASH_MISMATCH = "expected_hash_mismatch"
TARGET_PRESENT = "target_already_present"
ANCHOR_MISMATCH = "target_identity_mismatch"


def previous_hash(content, target_path):
    """Hash canônico do conteúdo em `target_path`; vazio quando o caminho não existe."""
    value = resolve_path(content, target_path)
    return "" if value is ABSENT else canonical_sha256(value)


def _identity(element):
    """Como esta entidade é reconhecida depois de a lista mudar de forma.

    `id` quando existe — é o identificador estável que o snapshot já carrega. Sem ele, o hash do
    elemento inteiro: menos preciso, porque o elemento pode ser editado, mas ainda distingue
    entidades diferentes que ocupem a mesma posição, que é o que a âncora precisa fazer.
    """
    if isinstance(element, dict) and element.get("id"):
        return f"id:{element['id']}"
    return f"hash:{canonical_sha256(element)}"


def path_anchors(content, target_path):
    """Identidade da entidade em cada índice de lista que o caminho atravessa.

    Chaveado pelo prefixo do caminho até o índice, para que a mensagem de recusa possa dizer
    exatamente onde a identidade mudou. Posição de acréscimo (`-`) e índice além do fim não têm
    âncora: não há entidade ali, e acrescentar ao fim é estável por definição.
    """
    anchors = {}
    current = content
    prefix = ""
    for token in parse_path(target_path):
        if isinstance(current, list):
            if not token.isdigit() or int(token) >= len(current):
                break
            prefix = f"{prefix}/{token}"
            current = current[int(token)]
            anchors[prefix] = _identity(current)
            continue
        if isinstance(current, dict) and token in current:
            prefix = f"{prefix}/{token}"
            current = current[token]
            continue
        break
    return anchors


def _anchor_conflicts(current, change):
    """Prefixos cujo ocupante mudou de identidade desde a elaboração.

    Verificado antes do hash porque responde à pergunta anterior: o hash diz se o valor é o
    mesmo, a âncora diz se a entidade é a mesma. Sem ela, dois Perfis de denominação idêntica
    tornam o hash indistinguível e o ato atinge o Perfil errado com a precondição satisfeita.
    """
    divergentes = []
    for prefix, identity in (change.get("expectedAnchors") or {}).items():
        value = resolve_path(current, prefix)
        if value is ABSENT or _identity(value) != identity:
            divergentes.append(prefix)
    return divergentes


def content_conflicts(content, changes):
    """Precondições que não se verificam em `content`, agrupadas por código de erro.

    Um `expectedPreviousHash` declarado prevalece sobre a regra do `ADD`: quem declara o
    conteúdo anterior sabe que o caminho está ocupado e assume a sobrescrita. Nenhuma
    declaração dispensa a âncora, que não é sobre conteúdo e não é declarável.
    """
    conflicts = {}
    current = deepcopy(content)
    for change in changes:
        path = change["targetPath"]
        declared = change.get("expectedPreviousHash")
        divergentes = _anchor_conflicts(current, change)
        if divergentes:
            conflicts.setdefault(ANCHOR_MISMATCH, []).extend(divergentes)
        elif declared:
            if declared != previous_hash(current, path):
                conflicts.setdefault(HASH_MISMATCH, []).append(path)
        elif change["operation"] == "ADD" and add_overwrites(current, path):
            conflicts.setdefault(TARGET_PRESENT, []).append(path)
        try:
            apply_change(current, change)
        except ValueError:
            # Alteração inaplicável ao conteúdo simulado: as seguintes partiriam de um
            # estado que não existe. A aplicabilidade é reportada por apply_changes.
            break
    return conflicts


# `ADD` não tem "antes": inserir não sobrescreve, e a precondição própria do ADD é a ausência
# do caminho, verificada por `add_overwrites` e indeclarável como hash de conteúdo.
DERIVABLE_OPERATIONS = frozenset({"REPLACE", "REMOVE"})


def derive_preconditions(content, changes):
    """Precondição efetiva de cada alteração, na ordem em que serão aplicadas.

    Para cada alteração, o hash do conteúdo que ela encontra — ou o declarado pelo cliente, que
    prevalece — e as âncoras dos índices que o caminho atravessa. Cadeia vazia de hash para `ADD`
    e para caminho inexistente, que é a ausência de precondição de conteúdo declarável; as
    âncoras, essas, valem para toda operação, inclusive `ADD` posicional.
    """
    derived = []
    current = deepcopy(content)
    for change in changes:
        declared = change.get("expectedPreviousHash")
        if declared:
            content_hash = declared
        elif change["operation"] in DERIVABLE_OPERATIONS:
            content_hash = previous_hash(current, change["targetPath"])
        else:
            content_hash = ""
        derived.append(
            {"hash": content_hash, "anchors": path_anchors(current, change["targetPath"])}
        )
        try:
            apply_change(current, change)
        except ValueError:
            # Alteração inaplicável: as seguintes partiriam de um estado que não existe. A
            # aplicabilidade é reportada por apply_changes; aqui só se para de derivar.
            derived.extend([{"hash": "", "anchors": {}}] * (len(changes) - len(derived)))
            break
    return derived
