"""Precondições de conteúdo por caminho alterado (FR-026, FR-036 da `001`).

`expectedPreviousHash` identifica o conteúdo que a pessoa responsável enxergava ao elaborar a
Alteração Normativa. Comparar esse hash com o conteúdo efetivamente vigente no `targetPath`
impede que uma Retificação sobrescreva silenciosamente outra publicada no intervalo entre a
elaboração e a Publicação.

O campo é opcional, mas `ADD` carrega uma precondição própria e não declarável: adicionar
pressupõe caminho ausente. Sem essa regra, um `ADD` sobre um caminho que outro ato criou seria
sobrescrita silenciosa que nem um cliente cuidadoso conseguiria evitar — não há como declarar
ausência num campo que guarda hash de conteúdo.

A regra vale apenas onde `ADD` de fato substitui, ou seja, em objeto. Em lista, `ADD` acrescenta
ao fim sem apagar nenhum elemento: incluir um Perfil é ato legítimo e não configura sobrescrita.

As precondições valem contra o conteúdo que cada alteração encontra, e não contra o conteúdo
inicial: um ato pode remover um caminho e recriá-lo em seguida.

Declarar o hash é opcional para o cliente, mas a verificação não é opcional para o sistema. Sem
declaração, `derive_preconditions` extrai a precondição da própria base declarada em
`baseSnapshotId` — que é, por construção, o conteúdo que a pessoa enxergava ao elaborar o ato.

**O que este módulo deixou de fazer.** A `003` guardava, além do hash, uma âncora de identidade
por índice atravessado, porque o hash responde "o valor ainda é este?" e não "ainda é esta
entidade?" — e com caminhos posicionais as duas perguntas eram distintas. Com o endereçamento
por chave, o próprio caminho nomeia a entidade, e não sobra índice para deslocar: a âncora
perdeu a pergunta que respondia e saiu inteira (FR-015). O hash ficou, porque a pergunta dele
continua de pé (FR-014).
"""

from copy import deepcopy

from processo_seletivo.publicacoes.domain import colecoes
from processo_seletivo.publicacoes.domain.changes import (
    ABSENT,
    ChaveNaoEncontrada,
    add_overwrites,
    apply_change,
    resolve_path,
)
from processo_seletivo.shared.canonical import canonical_sha256

HASH_MISMATCH = "expected_hash_mismatch"
TARGET_PRESENT = "target_already_present"
KEY_NOT_FOUND = "target_key_not_found"
DUPLICATE_KEY = "duplicate_key_in_collection"


def previous_hash(content, target_path):
    """Hash canônico do conteúdo em `target_path`; vazio quando o caminho não existe."""
    value = resolve_path(content, target_path)
    return "" if value is ABSENT else canonical_sha256(value)


def duplicate_keys(content):
    """Coleções com chave em que algum identificador aparece mais de uma vez (FR-009).

    A unicidade é exigida **dentro** de cada coleção. Um identificador que apareça em duas
    coleções distintas do mesmo snapshot é irrelevante: a resolução é escopada à coleção que o
    caminho nomeia, e supor unicidade global seria uma invariante que ninguém garante.
    """
    repetidas = []
    for forma, lista in colecoes.colecoes_com_chave(content):
        vistos, repetidos = set(), set()
        for elemento in lista:
            chave = elemento.get(colecoes.CAMPO_CHAVE) if isinstance(elemento, dict) else None
            if chave is None:
                continue
            if chave in vistos:
                repetidos.add(chave)
            vistos.add(chave)
        repetidas.extend(f"{forma}/id={chave}" for chave in sorted(repetidos))
    return repetidas


def content_conflicts(content, changes):
    """Precondições que não se verificam em `content`, agrupadas por código de erro.

    Um `expectedPreviousHash` declarado prevalece sobre a regra do `ADD`: quem declara o
    conteúdo anterior sabe que o caminho está ocupado e assume a sobrescrita.

    A simulação também é onde a entidade endereçada é procurada: um caminho por chave que não
    resolve no conteúdo vigente é `target_key_not_found`, e não interrupção silenciosa (FR-008).
    Esse achado **substitui** a verificação de conteúdo, em vez de somar-se a ela: quando a
    entidade não está mais lá, dizer que o hash divergiu descreveria a consequência e esconderia
    a causa. Um caminho de objeto que deixou de existir é outro caso — ali o hash divergente é
    a resposta certa, e é o que continua sendo dito.
    """
    conflicts = {}
    current = deepcopy(content)
    for change in changes:
        path = change["targetPath"]
        seguinte = deepcopy(current)
        try:
            apply_change(seguinte, change)
            falha = None
        except ValueError as exc:
            falha = exc
        if isinstance(falha, ChaveNaoEncontrada):
            conflicts.setdefault(KEY_NOT_FOUND, []).append(path)
        else:
            declared = change.get("expectedPreviousHash")
            if declared:
                if declared != previous_hash(current, path):
                    conflicts.setdefault(HASH_MISMATCH, []).append(path)
            elif change["operation"] == "ADD" and add_overwrites(current, path):
                conflicts.setdefault(TARGET_PRESENT, []).append(path)
        if falha is not None:
            # Alteração inaplicável ao conteúdo simulado: as seguintes partiriam de um
            # estado que não existe. A aplicabilidade é reportada por apply_changes.
            break
        current = seguinte
    repetidas = duplicate_keys(current)
    if repetidas:
        conflicts.setdefault(DUPLICATE_KEY, []).extend(repetidas)
    return conflicts


# `ADD` não tem "antes": acrescentar não sobrescreve, e a precondição própria do ADD é a ausência
# do caminho, verificada por `add_overwrites` e indeclarável como hash de conteúdo.
DERIVABLE_OPERATIONS = frozenset({"REPLACE", "REMOVE"})


def derive_preconditions(content, changes):
    """Hash do conteúdo que cada alteração encontra, na ordem em que serão aplicadas.

    O declarado pelo cliente prevalece. Cadeia vazia para `ADD` e para caminho inexistente, que
    é a ausência de precondição de conteúdo declarável.
    """
    derived = []
    current = deepcopy(content)
    for change in changes:
        declared = change.get("expectedPreviousHash")
        if declared:
            derived.append(declared)
        elif change["operation"] in DERIVABLE_OPERATIONS:
            derived.append(previous_hash(current, change["targetPath"]))
        else:
            derived.append("")
        try:
            apply_change(current, change)
        except ValueError:
            # Alteração inaplicável: as seguintes partiriam de um estado que não existe. A
            # aplicabilidade é reportada por apply_changes; aqui só se para de derivar.
            derived.extend([""] * (len(changes) - len(derived)))
            break
    return derived
