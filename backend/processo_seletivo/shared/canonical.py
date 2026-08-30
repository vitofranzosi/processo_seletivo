import hashlib
import json
import unicodedata
from decimal import Decimal
from uuid import UUID

# 1 → 2 na `006`, uma única vez, cobrindo as duas coleções novas do conteúdo publicado: `stages` e
# `sections`. As duas entram juntas de propósito — subir a versão com uma e acrescentar a outra
# depois produziria snapshots de versão 2 com e sem a propriedade, e a versão canônica deixaria de
# identificar uma forma.
#
# 2 → 3 na `007`, também uma única vez, cobrindo **três** mudanças de forma que viajam juntas pelo
# mesmo motivo (FR-017, FR-018):
#   1. as três seções institucionais novas do catálogo — `sections` passa de sete para dez itens;
#   2. `duties`, `workload` e `compensation` em cada item de `profiles`;
#   3. `processoCode` e `processoTitle` na raiz, sem os quais o documento não teria como nomear o
#      Processo sem expor UUID a quem lê.
#
# Conteúdo publicado na versão 2 torna-se irretificável, por versão **e** por topologia de seções.
# É a integridade funcionando, e é o que a precondição de implantação da `007` admite: a feature
# precede o primeiro Edital de produção, e os dados de demonstração são recriados.
SCHEMA_VERSION = 3


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
