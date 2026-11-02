# Data Model: Desempate pela nota de Etapa que o marco não enumera

Nenhuma entidade, tabela ou coluna nova.

## O que muda no que já existe

| Elemento | Antes | Depois |
|---|---|---|
| `AtoDeOrdenacao.universo.stageResults` | Resultados vigentes das Etapas enumeradas | os mesmos, mais os das Etapas do desempate (FR-3549) |
| `PosicaoNaOrdem.desempate[].value` do critério por Etapa não enumerada | sempre nulo | a nota comparada (FR-3554) |
| Função `check_ordering_act_provenance` | aceita `stageId` enumerado pelo marco | aceita enumerado **ou** citado por critério `MAIOR_PONTUACAO_NA_ETAPA` do marco (FR-3551) |

## Regras

- **Etapa do desempate** = `stageId` de critério `MAIOR_PONTUACAO_NA_ETAPA` do marco, fora de
  `marco.stages`.
- Resultado de Etapa do desempate contribui com `pontuacao` para `pontuacoes[etapa]`; **não** contribui
  com `consequencia` nem `motivo` (FR-3547, FR-3548).
- Participante sem Resultado vigente na Etapa do desempate: `pontuacoes[etapa]` ausente; vale o
  `whenMissing` do critério (FR-3553).
- O universo é comparado por identidade de Resultado (`universo.comparar`): Resultado novo ou sucessor na
  Etapa do desempate → `resultados_alterados` (FR-3550).
