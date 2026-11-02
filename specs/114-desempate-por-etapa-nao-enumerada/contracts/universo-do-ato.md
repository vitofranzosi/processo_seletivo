# Contrato: o universo do ato de ordenação

O formato do JSON gravado em `AtoDeOrdenacao.universo` **não muda**. Muda o conjunto de itens que
`stageResults` pode conter, e a regra que o banco confere.

```json
{
  "processoId": "…", "editalId": "…", "profileId": "…", "milestoneId": "…", "versionId": "…",
  "participants": ["…"],
  "stageResults": [
    {"id": "…", "registrationId": "…", "stageId": "<Etapa enumerada ou Etapa do desempate>",
     "versionId": "…", "consolidatedAt": "…"}
  ]
}
```

## Conferência no `INSERT` do ato (trigger `ato_coerente`)

Cada item de `stageResults` MUST:

1. existir em `resultados_resultadoetapa` com o mesmo `id`, Edital, inscrição, Etapa e versão;
2. ter `stageId` em `marco.stages` **ou** em
   `marco.tiebreakers[type = MAIOR_PONTUACAO_NA_ETAPA].parameters.stageId`, lido do marco publicado na
   versão citada pelo ato.

Qualquer outro `stageId` é recusado com `ordering act cites stage results that do not belong to its
milestone` — a mesma mensagem de antes.

## Conferência no `INSERT` da citação de decisão (trigger `citacao_coerente`)

Para decisão sobre recurso contra `ResultadoEtapa`, a Etapa alcançada MUST estar em `marco.stages`
**ou** em `marco.tiebreakers[type = MAIOR_PONTUACAO_NA_ETAPA].parameters.stageId` do marco do ato, lido
da versão citada por ele (FR-3560). Qualquer outra é recusada com `ordering act cites a decision
pertinent to another milestone` — a mesma mensagem de antes. O ramo do recurso contra a publicação não
muda.
