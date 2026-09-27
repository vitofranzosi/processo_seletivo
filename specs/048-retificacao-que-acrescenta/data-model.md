# Data model — 048 · A Retificação acrescenta o que o contrato já permite

**Nada persiste de novo.** Nenhuma entidade, nenhuma coluna, nenhuma migration. O `make preparar`
continua em `N de 34`. O que muda é o que uma Retificação pode escrever no **conteúdo canônico**, que
já é JSON versionado, e as guardas que o conferem.

## O que uma Retificação passa a escrever

As formas são as que `publicacoes/application/publish_edital.edital_snapshot` produz. Um objeto que
nasce ou um item acrescentado tem de ter a forma que a composição teria publicado, e não um
subconjunto.

| Alteração | Caminho | Valor |
|---|---|---|
| Modalidade acrescentada | `ADD /profiles/id=P/competitionModalities/-` | `{id, code, name, description, normativeRule}` — `normativeRule` é `null` ou `{id, foundation, version, percentage, calculation: {}, rounding: {}, distribution: {}, callRules: {}, effectiveFrom: null}` |
| Declaração da ampla | `REPLACE /profiles/id=P/generalCompetitionModalityId` | a identidade da Modalidade acrescentada |
| Linha do quadro da cota acrescentada | `ADD /profiles/id=P/vacancyTable/-` | `{id, modalityId, immediateVacancies}` |
| Janela que nasce | `REPLACE /profiles/id=P/classificationMilestones/id=M/appealWindow` | `{admits: true, durationDays: N, unit: "DIAS_CORRIDOS"}`, N > 0 |
| Regra de corte que nasce | `REPLACE …/classificationMilestones/id=M/cutRule` | `{targetKind, targetCount, surplusCount, tieOutcome, governedStage, continuation}` |
| Reversão que nasce | `REPLACE /profiles/id=P/vacancyReversion` | `{kind}` |
| Critério acrescentado | `ADD …/classificationMilestones/id=M/tiebreakers/-` | `{id, order, type, parameters: {stageId} ou {factId}, whenMissing}` |

**Identidades.** A da Modalidade e a do critério nascem no fragmento e atravessam as duas fases do
formulário (`R-5`). A da linha do quadro e a do objeto `normativeRule` nascem em `diferencas`, como
hoje.

**Ordem das Modalidades.** O snapshot da composição as ordena por código, e o `ADD` acrescenta no fim.
A ordem não carrega sentido: `recortes_do_perfil` e o PDF leem na ordem do conteúdo, e nenhuma leitura
depende de posição.

## O que as guardas novas conferem

| Guarda | Onde | Sobre o quê | Recusa |
|---|---|---|---|
| A janela que nasce concede (`FR-787`) | `publicacoes/domain/changes.py`, função nova chamada pela aplicação (`R-1`) | `appealWindow` ausente antes e presente depois | idem, com a razão da `D-003` |
| O corte sobre Etapa avaliada (`FR-789`) | `publicacoes/application/retificacoes.py` (`R-3`) | `cutRule` ausente antes e presente depois, com Etapa governada que tem Resultado | `DomainError` 422, nomeando marco e Etapa |
| A Modalidade e o critério da composição (`FR-778`, `FR-793`) | `editais/domain/perfis.py`, extraído (`R-4`); chamado pela aplicação | entidades presentes depois e ausentes antes | `ProfileValidationError` → `DomainError` 422 |

**Nenhuma delas corre em `consolidation.consolidate`.** A troca de campo não retificável por objeto
inteiro pela API continua como está: é o achado A-6 da spec. A reprodução de atos já publicados continua
aplicando só as recusas que existiam quando eles foram praticados (`R-1`).

## O que o contrato de mutabilidade ganha

Nada em `CONTRATO` nem em `PODE_PASSAR_A_EXISTIR`: as decisões já estavam lá. O que se acrescenta é
**do lado da tela**, em `interface/retificacao.py`:
- o registro das listas de nascimento (`R-2`);
- a segunda conferência da guarda de carga: lista de nascimento só para objeto que pode nascer, e só com
  campos que o contrato conhece (`FR-803`).

## O que não muda

- `Retificacao`, `AlteracaoNormativa` e `VersaoConsolidada`: mesmas tabelas, mesmos estados, mesma
  segregação de funções.
- As tabelas relacionais do Edital: a Retificação continua não as escrevendo. O vigente sai do
  conteúdo canônico.
- `Inscricao.modality_id`, `ItemDaListaExigida`, `AtoDeOrdenacao`, `RelacaoDeHabilitados`, `Sorteio`,
  cortes e apurações: nenhum é tocado pelo ato. As consequências sobre eles são as que as regras de
  obsolescência já produzem (`R-8`).
