from copy import deepcopy


def _tokens(path):
    if not path.startswith("/"):
        raise ValueError("targetPath deve ser absoluto")
    return [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]


def _list_index(items, token, path, *, allow_end):
    """Resolve um token de caminho sobre uma lista, no estilo JSON Pointer."""
    if allow_end and token == "-":
        return len(items)
    if not token.isdigit() or (len(token) > 1 and token.startswith("0")):
        raise ValueError(f"Índice inválido: {path}")
    index = int(token)
    if index > (len(items) if allow_end else len(items) - 1):
        raise ValueError(f"Caminho inexistente: {path}")
    return index


def _descend(container, token, path):
    if isinstance(container, dict):
        if token not in container:
            raise ValueError(f"Caminho inexistente: {path}")
        return container[token]
    if isinstance(container, list):
        return container[_list_index(container, token, path, allow_end=False)]
    raise ValueError(f"Caminho inexistente: {path}")


def _write(parent, leaf, path, operation, value):
    if isinstance(parent, list):
        if operation == "ADD":
            parent.insert(_list_index(parent, leaf, path, allow_end=True), value)
            return
        index = _list_index(parent, leaf, path, allow_end=False)
        if operation == "REMOVE":
            del parent[index]
        else:
            parent[index] = value
        return
    if not isinstance(parent, dict):
        raise ValueError(f"Caminho inexistente: {path}")
    if operation in {"REPLACE", "REMOVE"} and leaf not in parent:
        raise ValueError(f"Caminho inexistente: {path}")
    if operation == "REMOVE":
        del parent[leaf]
    else:
        parent[leaf] = value


def apply_changes(base, changes, *, publication_id):
    result = deepcopy(base)
    provenance = {}
    for change in changes:
        path = change["targetPath"]
        tokens = _tokens(path)
        parent = result
        for token in tokens[:-1]:
            parent = _descend(parent, token, path)
        operation = change["operation"]
        if operation not in {"ADD", "REPLACE", "REMOVE"}:
            raise ValueError(f"Operação desconhecida: {operation}")
        _write(parent, tokens[-1], path, operation, deepcopy(change.get("newValue")))
        provenance[path] = publication_id
    return result, provenance
