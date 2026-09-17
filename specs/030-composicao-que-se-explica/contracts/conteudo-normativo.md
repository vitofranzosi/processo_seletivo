# Contrato — conteúdo normativo publicado

O Edital publica um documento canônico. Este contrato registra **o que a feature acrescenta a ele** e
o que ela promete não tocar.

## Regra que governa tudo abaixo

**Edital publicado antes desta feature não ganha chave nenhuma.** A ausência de `orderProduction` e
de `drawMethod` no nível do Edital é o estado legítimo de todo Edital já publicado, e os leitores
derivam dela o comportamento de hoje. Acrescentar chave a snapshot publicado mudaria o conteúdo e o
resumo dele — o que o princípio II proíbe (SC-142).

## `classificationMilestones[]` — chave nova

```jsonc
{
  "id": "…",
  "code": "FINAL",
  "name": "Classificação final",
  "orderProduction": "POR_SORTEIO",   // NOVO — ausente em Edital publicado antes desta feature
  "stages": [],
  "operation": "SOMA_PONDERADA",
  "normalization": "NENHUMA",
  "rounding": { "scale": 2, "mode": "MEIO_PARA_CIMA" },
  "drawMethod": { }                    // vazio = referencia o método comum do Edital (FR-429)
}
```

| Chave | Valor | Significado |
|---|---|---|
| `orderProduction` | `POR_PONTUACAO` | A ordem nasce da pontuação combinada das Etapas enumeradas |
| `orderProduction` | `POR_SORTEIO` | A ordem nasce de sorteio |
| `orderProduction` | *ausente* | Edital anterior à feature: sorteia se `drawMethod` está declarado |

**`operation` e `normalization` com uma Etapa** (FR-416): continuam publicados, com o valor que o
Edital afirma. O que muda é que deixam de ser **perguntados** — a tela declara que a pontuação
combinada é a da Etapa única. A regra derivada mora em um lugar só, nunca duplicada entre template e
cálculo.

## Nível do Edital — chave nova

```jsonc
{
  "drawMethod": {                      // NOVO — o método comum, declarado uma vez (FR-429)
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "…",
    "occurrence": "…",
    "occurrenceAt": "2026-11-20T20:00:00-03:00",
    "derivation": "…",
    "normalization":    { "rule": "DIGITOS_EM_SEQUENCIA", "text": "…" },
    "substitutionRule": { "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE", "text": "…" }
  }
}
```

**Divergência é explícita** (FR-430): o marco que declara `drawMethod` próprio diverge do comum, e a
divergência se lê do documento sem inferência — a chave está lá, preenchida, sob o marco.

## Catálogo de mutabilidade — entradas novas

`backend/processo_seletivo/editais/domain/mutabilidade.py` ganha nove entradas no nível do Edital,
espelhando as nove que já existem sob `classificationMilestones`:

```python
("edital", "drawMethod/algorithm"):              retificavel(),
("edital", "drawMethod/source"):                 retificavel(),
("edital", "drawMethod/occurrence"):             retificavel(),
("edital", "drawMethod/occurrenceAt"):           retificavel(),
("edital", "drawMethod/derivation"):             retificavel(),
("edital", "drawMethod/normalization/rule"):     retificavel(),
("edital", "drawMethod/normalization/text"):     retificavel(),
("edital", "drawMethod/substitutionRule/rule"):  retificavel(),
("edital", "drawMethod/substitutionRule/text"):  retificavel(),

("classificationMilestones", "orderProduction"): retificavel(),
```

**As nove do marco permanecem.** Elas endereçam a divergência, e Edital publicado depende delas.
