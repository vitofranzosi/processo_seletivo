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

O bloco `method` é cópia fiel do `drawMethod` do marco **na versão que a relação cita** (D-013), e
`methodHash` é o resumo canônico desse objeto — o mesmo que a relação gravou ao congelar (FR-067).
Ler o método do conteúdo vigente, e não do citado, tornaria o manifesto instável a cada Retificação
posterior, o que contraria a regra 4.

## Regras

1. **Sem dado pessoal além do que a relação publicada já expõe** (FR-044). O manifesto identifica
   participante por `publicNumber` — nunca por CPF, identificador interno ou identidade do provedor.
   **E o `relationHash` obedece à mesma regra**: ele cobre a projeção pública da relação — número,
   nome e protocolo —, e nada além. Um resumo que cobrisse identificador interno seria um número que
   o leitor teria de aceitar sem poder refazer, que é justamente a palavra que esta feature não pede
   (R-015).
2. **Ordenado por `publicNumber` crescente**, e não por posição: quem confere lê a entrada, não o
   resultado.
3. **Autossuficiente para reproduzir a ordem**: tudo o que o verificador precisa para recalcular as
   chaves e a ordem está dentro, exceto a implementação de SHA-256. Para refazer também o
   `relationHash` — e não apenas aceitá-lo — ele lê a relação publicada no portal, que é pública e
   anônima.
4. **Estável**: dois downloads do mesmo sorteio produzem bytes idênticos.
