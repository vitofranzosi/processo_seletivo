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
# 3 → 4 na `009`, uma vez, cobrindo o contrato operacional de inscrição (FR-008):
#   1. `isRegistrationPeriod` em cada item de `schedule` — qual Evento é o período de inscrições;
#   2. `documentRequirements` na raiz — o que o candidato precisa apresentar;
#   3. a seção gerada `documentos-exigidos` no catálogo — `sections` passa de dez para onze itens.
#
# 4 → 5 na `012`, uma vez, cobrindo o contrato normativo da avaliação (FR-007, FR-008):
#   1. `evaluationsPerRegistration` em cada item de `stages` — quantas avaliações a inscrição
#      recebe naquela Etapa, que decide se uma nota isolada elimina ou se há segunda leitura;
#   2. `maximumScore` no mesmo item — o limite contra o qual a pontuação é validada.
#
# As duas entram juntas pela razão de sempre, e esta é a primeira vez que o incremento **não**
# torna irretificável o que já estava publicado. Ele é aditivo sobre uma coleção existente, e a
# `012` declara o que a ausência significa — uma avaliação, limite não declarado. Existe, portanto,
# conversão sem invenção, e ela vive em `publicacoes/domain/elevacao.py`: função pura aplicada na
# **leitura**, dentro do fluxo de Retificação, que não escreve linha nenhuma (012, D-002, T-001).
#
# Conteúdo publicado na versão 2 torna-se irretificável, por versão **e** por topologia de seções.
# É a integridade funcionando, e é o que a precondição de implantação da `007` admite: a feature
# precede o primeiro Edital de produção, e os dados de demonstração são recriados. A `009` repete
# a mesma precondição pela mesma razão, e ela vale igual para o conteúdo da versão 3.
SCHEMA_VERSION = 5


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
