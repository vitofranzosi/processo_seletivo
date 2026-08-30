"""Reconstrói a precondição das Retificações elaboradas antes de ela existir.

A precondição é função determinística de `base_snapshot.content` e da sequência ordenada de
alterações — exatamente o que a elaboração passa a calcular. Por isso o backfill não adivinha:
recalcula o que teria sido gravado se a regra já existisse.

Só Retificações ainda em curso são tocadas. Publicada e Cancelada são finais e imutáveis: uma
Publicação já produziu seus efeitos e reescrevê-la seria falsificar histórico, e a Constituição
proíbe. As em curso são justamente as que ainda vão publicar, que é onde o risco está.

**A lógica abaixo é uma cópia congelada, e é assim de propósito.** Importar as funções do domínio
faria uma alteração futura nelas mudar retroativamente o que esta migration já executou em
produção — uma migration aplicada tem de continuar significando o que significava no dia em que
rodou. A duplicação é o preço de a história ser fixa; se a regra do domínio evoluir, a correção
entra como migration nova, nunca reescrevendo esta.

Congelado de `publicacoes/domain/changes.py`, `publicacoes/domain/conflicts.py` e
`shared/canonical.py` no estado do commit e3a6992.
"""

import hashlib
import json
import re
import unicodedata
from copy import deepcopy
from decimal import Decimal
from uuid import UUID

from django.db import migrations

EM_CURSO = ("EM_ELABORACAO", "EM_REVISAO", "HOMOLOGADA")
DERIVABLE_OPERATIONS = frozenset({"REPLACE", "REMOVE"})
APPEND_TOKEN = "-"
ABSENT = object()
_INDEX = re.compile(r"0|[1-9][0-9]*")


def _default(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, UUID):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    raise TypeError(f"Tipo não canonicalizável: {type(value)!r}")


def _canonical_sha256(value):
    text = json.dumps(
        value, default=_default, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(unicodedata.normalize("NFC", text).encode("utf-8")).hexdigest()


def _parse_path(path):
    if not path.startswith("/"):
        raise ValueError("targetPath deve ser absoluto")
    return [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]


def _index(token, size, *, allow_append):
    if token == APPEND_TOKEN:
        return size if allow_append else None
    if not _INDEX.fullmatch(token):
        return None
    position = int(token)
    return position if position <= (size if allow_append else size - 1) else None


def _resolve_path(content, path):
    current = content
    for token in _parse_path(path):
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


def _apply_change(content, change):
    path = change["targetPath"]
    operation = change["operation"]
    tokens = _parse_path(path)
    parent = content
    for token in tokens[:-1]:
        parent = _descend(parent, token, path)
    leaf = tokens[-1]
    value = deepcopy(change.get("newValue"))
    if isinstance(parent, dict):
        if operation in {"REPLACE", "REMOVE"} and leaf not in parent:
            raise ValueError(f"Caminho inexistente: {path}")
        if operation == "REMOVE":
            del parent[leaf]
        else:
            parent[leaf] = value
    elif isinstance(parent, list):
        position = _index(leaf, len(parent), allow_append=operation == "ADD")
        if position is None:
            raise ValueError(f"Caminho inexistente: {path}")
        if operation == "REMOVE":
            del parent[position]
        elif operation == "ADD":
            parent.insert(position, value)
        else:
            parent[position] = value
    else:
        raise ValueError(f"Caminho inexistente: {path}")


def _previous_hash(content, target_path):
    value = _resolve_path(content, target_path)
    return "" if value is ABSENT else _canonical_sha256(value)


def _identity(element):
    if isinstance(element, dict) and element.get("id"):
        return f"id:{element['id']}"
    return f"hash:{_canonical_sha256(element)}"


def _path_anchors(content, target_path):
    anchors = {}
    current = content
    prefix = ""
    for token in _parse_path(target_path):
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


def _derive_preconditions(content, changes):
    derived = []
    current = deepcopy(content)
    for change in changes:
        declared = change.get("expectedPreviousHash")
        if declared:
            content_hash = declared
        elif change["operation"] in DERIVABLE_OPERATIONS:
            content_hash = _previous_hash(current, change["targetPath"])
        else:
            content_hash = ""
        derived.append(
            {"hash": content_hash, "anchors": _path_anchors(current, change["targetPath"])}
        )
        try:
            _apply_change(current, change)
        except ValueError:
            derived.extend([{"hash": "", "anchors": {}}] * (len(changes) - len(derived)))
            break
    return derived


def preencher(apps, schema_editor):
    Retificacao = apps.get_model("publicacoes", "Retificacao")
    AlteracaoNormativa = apps.get_model("publicacoes", "AlteracaoNormativa")
    for retificacao in (
        Retificacao.objects.filter(status__in=EM_CURSO)
        .select_related("base_snapshot")
        .prefetch_related("alteracoes")
    ):
        alteracoes = list(retificacao.alteracoes.order_by("order"))
        if not alteracoes:
            continue
        preconditions = _derive_preconditions(
            retificacao.base_snapshot.content,
            [
                {
                    "targetPath": item.target_path,
                    "operation": item.operation,
                    "newValue": item.new_value,
                    "expectedPreviousHash": item.expected_previous_hash,
                }
                for item in alteracoes
            ],
        )
        for item, precondition in zip(alteracoes, preconditions, strict=True):
            item.expected_previous_hash = precondition["hash"]
            item.expected_anchors = precondition["anchors"]
        AlteracaoNormativa.objects.bulk_update(
            alteracoes, ["expected_previous_hash", "expected_anchors"]
        )


def esvaziar(apps, schema_editor):
    """A reversão devolve o estado anterior; a coluna some junto na 0005."""
    AlteracaoNormativa = apps.get_model("publicacoes", "AlteracaoNormativa")
    AlteracaoNormativa.objects.update(expected_anchors={})


class Migration(migrations.Migration):
    dependencies = [("publicacoes", "0005_ancoras_de_alteracao")]

    operations = [migrations.RunPython(preencher, esvaziar)]
