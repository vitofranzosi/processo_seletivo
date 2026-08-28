from copy import deepcopy

ABSENT = object()


def parse_path(path):
    if not path.startswith("/"):
        raise ValueError("targetPath deve ser absoluto")
    return [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]


def resolve_path(content, path):
    """Valor canônico atualmente em `path`, ou ABSENT quando o caminho não existe."""
    current = content
    for token in parse_path(path):
        if not isinstance(current, dict) or token not in current:
            return ABSENT
        current = current[token]
    return current


def apply_changes(base, changes, *, publication_id):
    result = deepcopy(base)
    provenance = {}
    for change in changes:
        path = change["targetPath"]
        tokens = parse_path(path)
        parent = result
        for token in tokens[:-1]:
            if not isinstance(parent, dict) or token not in parent:
                raise ValueError(f"Caminho inexistente: {path}")
            parent = parent[token]
        leaf = tokens[-1]
        operation = change["operation"]
        if not isinstance(parent, dict) or (
            operation in {"REPLACE", "REMOVE"} and leaf not in parent
        ):
            raise ValueError(f"Caminho inexistente: {path}")
        if operation == "REMOVE":
            del parent[leaf]
        elif operation in {"ADD", "REPLACE"}:
            parent[leaf] = deepcopy(change.get("newValue"))
        else:
            raise ValueError(f"Operação desconhecida: {operation}")
        provenance[path] = publication_id
    return result, provenance
