"""Aplicação determinística de Alterações Normativas sobre o conteúdo canônico.

Caminhos seguem JSON Pointer (RFC 6901) e as operações seguem a semântica do RFC 6902,
sobre objetos **e** listas: o snapshot expõe `profiles`, `schedule` e `competitionModalities`
como arrays, e uma Retificação precisa alcançar um Perfil ou Evento específico.

Em objeto, `ADD` grava a chave — criando ou substituindo. Em lista, `ADD` **insere** na
posição e não substitui nada; `-` acrescenta ao final. Essa distinção importa para a
precondição de sobrescrita em `conflicts.py`.
"""

import re
from copy import deepcopy

ABSENT = object()

APPEND_TOKEN = "-"
OPERATIONS = frozenset({"ADD", "REPLACE", "REMOVE"})
_INDEX = re.compile(r"0|[1-9][0-9]*")


def parse_path(path):
    if not path.startswith("/"):
        raise ValueError("targetPath deve ser absoluto")
    return [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]


def _index(token, size, *, allow_append):
    """Resolve token RFC 6901 em índice de lista; grafia ambígua é recusada."""
    if token == APPEND_TOKEN:
        return size if allow_append else None
    if not _INDEX.fullmatch(token):
        return None
    position = int(token)
    return position if position <= (size if allow_append else size - 1) else None


def _descend(container, token, path):
    if isinstance(container, dict):
        if token not in container:
            raise ValueError(f"Caminho inexistente: {path}")
        return container[token]
    if isinstance(container, list):
        position = _index(token, len(container), allow_append=False)
        if position is None:
            raise ValueError(f"Caminho inexistente: {path}")
        return container[position]
    raise ValueError(f"Caminho inexistente: {path}")


def _parent_of(content, path):
    """Contêiner que hospeda a folha do caminho, e a própria folha."""
    tokens = parse_path(path)
    parent = content
    for token in tokens[:-1]:
        parent = _descend(parent, token, path)
    return parent, tokens[-1]


def resolve_path(content, path):
    """Valor canônico atualmente em `path`, ou ABSENT quando o caminho não existe.

    A posição de acréscimo (`-`) nunca existe: nada há ali para ser sobrescrito.
    """
    current = content
    for token in parse_path(path):
        if isinstance(current, dict):
            if token not in current:
                return ABSENT
            current = current[token]
        elif isinstance(current, list):
            position = _index(token, len(current), allow_append=False)
            if position is None:
                return ABSENT
            current = current[position]
        else:
            return ABSENT
    return current


def add_overwrites(content, path):
    """`ADD` neste caminho substituiria conteúdo existente?

    Só em objeto: em lista, `ADD` insere e desloca, sem apagar nada. É o que separa a
    sobrescrita silenciosa, que `conflicts.py` recusa, da inserção legítima de um Perfil.
    """
    try:
        parent, leaf = _parent_of(content, path)
    except ValueError:
        return False
    return isinstance(parent, dict) and leaf in parent


def _apply_to_dict(parent, leaf, operation, value, path):
    if operation in {"REPLACE", "REMOVE"} and leaf not in parent:
        raise ValueError(f"Caminho inexistente: {path}")
    if operation == "REMOVE":
        del parent[leaf]
    else:
        parent[leaf] = value


def _apply_to_list(parent, leaf, operation, value, path):
    position = _index(leaf, len(parent), allow_append=operation == "ADD")
    if position is None:
        raise ValueError(f"Caminho inexistente: {path}")
    if operation == "REMOVE":
        del parent[position]
    elif operation == "ADD":
        parent.insert(position, value)
    else:
        parent[position] = value


def apply_change(content, change):
    """Aplica uma Alteração Normativa em `content`, no lugar. ValueError se o caminho não serve."""
    path = change["targetPath"]
    operation = change["operation"]
    if operation not in OPERATIONS:
        raise ValueError(f"Operação desconhecida: {operation}")
    parent, leaf = _parent_of(content, path)
    value = deepcopy(change.get("newValue"))
    if isinstance(parent, dict):
        _apply_to_dict(parent, leaf, operation, value, path)
    elif isinstance(parent, list):
        _apply_to_list(parent, leaf, operation, value, path)
    else:
        raise ValueError(f"Caminho inexistente: {path}")


def apply_changes(base, changes, *, publication_id):
    result = deepcopy(base)
    provenance = {}
    for change in changes:
        apply_change(result, change)
        provenance[change["targetPath"]] = publication_id
    return result, provenance
