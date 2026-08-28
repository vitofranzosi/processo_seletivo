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
"""

from copy import deepcopy

from processo_seletivo.publicacoes.domain.changes import (
    ABSENT,
    add_overwrites,
    apply_change,
    resolve_path,
)
from processo_seletivo.shared.canonical import canonical_sha256

HASH_MISMATCH = "expected_hash_mismatch"
TARGET_PRESENT = "target_already_present"


def previous_hash(content, target_path):
    """Hash canônico do conteúdo em `target_path`; vazio quando o caminho não existe."""
    value = resolve_path(content, target_path)
    return "" if value is ABSENT else canonical_sha256(value)


def requires_content_check(changes):
    """Há precondição a verificar? Sem hash declarado, só `ADD` depende do conteúdo."""
    return any(
        change.get("expectedPreviousHash") or change["operation"] == "ADD" for change in changes
    )


def content_conflicts(content, changes):
    """Precondições que não se verificam em `content`, agrupadas por código de erro.

    Um `expectedPreviousHash` declarado prevalece sobre a regra do `ADD`: quem declara o
    conteúdo anterior sabe que o caminho está ocupado e assume a sobrescrita.
    """
    conflicts = {}
    current = deepcopy(content)
    for change in changes:
        path = change["targetPath"]
        declared = change.get("expectedPreviousHash")
        if declared:
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
