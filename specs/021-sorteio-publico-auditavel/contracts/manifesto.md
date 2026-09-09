# Contrato — manifesto do sorteio

Documento público, derivado deterministicamente da relação congelada, do método, da ocorrência e do
ato (R-007). Não é cópia: o que se grava é o `manifestHash`, e o download regenera.

## Forma

```json
{
  "manifestVersion": 1,
  "drawId": "<uuid>",
  "process": {"processId": "<uuid>", "editalId": "<uuid>", "editalNumber": "77/2026",
              "versionId": "<uuid>"},
  "scope": {"profileId": "<uuid>", "profileCode": "…", "listId": "<uuid|null>",
            "listName": "Ampla concorrência"},
  "method": {"algorithm": "IFES-SORTEIO-SHA256-v1", "source": "…", "occurrence": "…",
             "derivation": "…", "normalization": "…", "substitutionRule": "…",
             "methodHash": "<64 hex>"},
  "relation": {"relationId": "<uuid>", "criterion": "…", "count": 237,
               "publishedAt": "<iso8601>", "relationHash": "<64 hex>"},
  "seed": {"rawMaterial": "…", "normalized": "…", "observedAt": "<iso8601>"},
  "execution": {"executedAt": "<iso8601>"},
  "participants": [
    {"publicNumber": 1, "key": "<64 hex>", "position": 42}
  ],
  "manifestHash": "<64 hex>"
}
```

`manifestHash` é o `canonical_sha256` do objeto **sem** o próprio campo.

## Regras

1. **Sem dado pessoal além do que a relação publicada já expõe** (FR-044). O manifesto identifica
   participante por `publicNumber` — nunca por CPF, identificador interno ou identidade do provedor.
2. **Ordenado por `publicNumber` crescente**, e não por posição: quem confere lê a entrada, não o
   resultado.
3. **Autossuficiente**: tudo o que o verificador precisa está dentro, exceto a implementação de
   SHA-256.
4. **Estável**: dois downloads do mesmo sorteio produzem bytes idênticos.
