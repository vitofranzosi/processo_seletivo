import hashlib
import json
import unicodedata
from decimal import Decimal
from uuid import UUID

SCHEMA_VERSION = 1


def _default(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, UUID):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    raise TypeError(f"Tipo não canonicalizável: {type(value)!r}")


def canonical_bytes(value) -> bytes:
    text = json.dumps(
        value, default=_default, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return unicodedata.normalize("NFC", text).encode("utf-8")


def canonical_sha256(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()
