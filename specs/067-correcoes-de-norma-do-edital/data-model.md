# Modelo de dados — 067

**Nenhuma mudança.** Nenhum modelo, campo, constraint, migration, gatilho ou versão do esquema do
conteúdo canônico (`FR-1327`).

O que a feature lê, todos já existentes no conteúdo canônico:

| Entidade | Campos | Uso |
|---|---|---|
| Marco classificatório (`profiles[].classificationMilestones[]`) | `name`, `code`, `orderProduction`, `appealWindow`, `rounding`, `cutRule.tieOutcome` | frase de recurso; dispensa e omissão sob sorteio; aviso |
| Evento (`schedule[]`) | `type`, `description`, `startAt`, `endAt`, `order` | Evento de recurso no aviso |
| Perfil (`profiles[]`) | `code`, `immediateVacancies`, `vacancyTable[].immediateVacancies`, `vacancyReversion` | Perfil sem vaga imediata |

**Uma consequência de dado, sem mudança de forma:** marco por sorteio composto pela tela depois desta
feature é gravado com `arredondamento = {}` (`D-008`) — o mesmo valor padrão que a coluna JSON já
admite. Marcos gravados antes conservam o que têm; o documento não imprime o arredondamento deles sob
sorteio (`FR-1313`).
