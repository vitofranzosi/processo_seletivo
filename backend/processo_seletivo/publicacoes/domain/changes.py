import re
from copy import deepcopy

APPEND_TOKEN = "-"
OPERATIONS = frozenset({"ADD", "REPLACE", "REMOVE"})
_INDEX = re.compile(r"0|[1-9][0-9]*")


def _unescape(token):
    return token.replace("~1", "/").replace("~0", "~")


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


def apply_changes(base, changes, *, publication_id):
    result = deepcopy(base)
    provenance = {}
    for change in changes:
        path = change["targetPath"]
        if not path.startswith("/"):
            raise ValueError("targetPath deve ser absoluto")
        operation = change["operation"]
        if operation not in OPERATIONS:
            raise ValueError(f"Operação desconhecida: {operation}")
        tokens = [_unescape(part) for part in path[1:].split("/")]
        parent = result
        for token in tokens[:-1]:
            parent = _descend(parent, token, path)
        value = deepcopy(change.get("newValue"))
        if isinstance(parent, dict):
            _apply_to_dict(parent, tokens[-1], operation, value, path)
        elif isinstance(parent, list):
            _apply_to_list(parent, tokens[-1], operation, value, path)
        else:
            raise ValueError(f"Caminho inexistente: {path}")
        provenance[path] = publication_id
    return result, provenance
