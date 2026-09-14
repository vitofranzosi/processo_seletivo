# Matriz de mutabilidade — proposta para aprovação

**Status**: **aprovada em 2026-09-13**, como proposta — as 121 entradas, as 30 linhas marcadas ⚠️ e
as 5 políticas de objeto ausente, sem emenda.

A partir daqui esta matriz é **norma**, e não sugestão. Mudar qualquer linha é decisão nova e
escrita, sujeita à D-011 (a classificação vigente governa os atos futuros) e, na direção
retificável → não retificável, à FR-315.

As marcas ⚠️ ficam no documento de propósito: elas não significam mais "pendente", e sim "esta linha
foi uma escolha entre alternativas defensáveis" — que é o que alguém precisa saber antes de
reclassificá-la.

Esta é a resposta ao achado C2: os artefatos definiam a estrutura do contrato e mandavam o
implementador decidir o conteúdo dela. Natureza, razão e política de ausência são decisões
normativas que afetam direitos, e não cabem numa tarefa de implementação.

**Como ler**: cada linha é uma entrada do `CONTRATO`. A chave é `(coleção, caminho relativo)`.
A coluna **⚠️** marca as linhas em que a proposta é uma escolha entre alternativas defensáveis —
são as que precisam do seu julgamento, e não da sua conferência.

**Como foi medida**: enumerada de `publicacoes/application/publish_edital.py`, que é o que produz o
conteúdo canônico. **121 entradas.** É mais do que os 81–98 campos que a auditoria contou por
Edital, e a diferença não é erro: a auditoria contou ocorrências num Edital concreto; isto é a
forma, que é a união de tudo o que pode aparecer.

Uma consequência disso vale para o guardião, e está em `sections`: `content` e `source` são
**mutuamente exclusivos** — seção redigida tem o primeiro, seção gerada tem o segundo. O domínio de
uma coleção é a **união** das chaves dos seus itens, e nunca a interseção. Exigir que todo item
carregue todo campo faria o guardião falhar conforme a seção que a travessia visse primeiro.

## Naturezas

| Sigla | Natureza | Carrega razão? |
|---|---|---|
| **R** | Retificável | não |
| **N** | Não retificável | **sim**, e normativa |
| **D** | Derivado | não |
| **E** | Identidade / estrutural | não |

---

## 1. Raiz do Edital — 10 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `schemaVersion` | | **E** | Versão da forma canônica. Não é norma do certame. |
| `editalId` | | **E** | Identidade. |
| `processoId` | | **E** | Identidade do Processo. |
| `processoCode` | | **D** | Cópia do código institucional do Processo, para o documento nomeá-lo sem expor UUID. |
| `processoTitle` | | **D** | Idem. |
| `number` | ⚠️ | **N** | O número do Edital é como o certame é citado em todo lugar — outros atos, ofícios, o Diário. Trocá-lo por Retificação faria dois documentos nomearem coisas diferentes com o mesmo nome. |
| `year` | ⚠️ | **N** | Mesma razão. |
| `title` | | **R** | Já oferecido hoje em `CAMPOS_RAIZ`. |
| `description` | | **R** | Já oferecido hoje. |
| `maxInscricoesPorCandidato` | ⚠️ | **N** | Governa quantas inscrições a pessoa pôde fazer. Reduzi-lo depois de aberto o prazo invalidaria inscrição já aceita; aumentá-lo daria a quem se inscreveu depois uma chance que os primeiros não tiveram. **Alternativa defensável**: retificável apenas para mais, e apenas antes de abrir o prazo — mas isso é regra condicional, e o contrato não tem forma para ela. |

## 2. `profiles` — 17 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `code` | | **E** | Identificador estável do Perfil dentro do Edital; a inscrição o referencia. |
| `name` | | **R** | Já oferecido. |
| `description` | | **R** | ⚠️ Não está em `CAMPOS_PERFIL` hoje. Proposta: retificável, pela mesma razão de `duties` e `compensation`, que a FR-016 já admitiu. |
| `requirements` | | **R** | **Canário 2.** Decide quem pode concorrer. |
| `immediateVacancies` | ⚠️ | **N** | Número de vagas publicado. Alterá-lo depois da publicação muda a expectativa de quem se inscreveu contando com ele. **É o campo que a spec estrutural de vagas vai reorganizar** — e a razão precisa ser dela, não desta. |
| `reserveType` | ⚠️ | **N** | Espécie do cadastro reserva. A auditoria a listou como norma sem decisão. A exclusão de hoje tem razão técnica ("valor fechado"), que a D-002 não aceita. |
| `reserveLimit` | ⚠️ | **N** | Idem, e depende de `reserveType`. |
| `locality` | | **R** | Já oferecido. |
| `duties` | | **R** | Já oferecido (FR-016). |
| `workload` | | **R** | Já oferecido. |
| `compensation` | | **R** | Já oferecido. |
| `classificationInformation` | ⚠️ | **N** | **Objeto opaco.** Classificado inteiro. Não há forma declarada para dizer o que muda dentro dele. |
| `callInformation` | ⚠️ | **N** | **Objeto opaco.** Idem. |
| `generalCompetitionModalityId` | | **R** | Já oferecido (014, FR-231). |
| `vacancyReversion/kind` | | **R** | Já oferecido — `CAMPOS_DA_REVERSAO`. |
| `callForm` | ⚠️ | **R** | **É o precedente que deu origem a esta feature.** O código registra que "o primeiro Edital publicado com a forma declarada nasceria irretificável nela". Propor **R** é fechar esse precedente. |

## 3. `competitionModalities` — 13 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade; a inscrição e o quadro a referenciam. |
| `code` | | **E** | Identificador estável. |
| `name` | | **R** | Já oferecido. |
| `description` | | **R** | Já oferecido. |
| `normativeRule/id` | | **E** | Identidade. |
| `normativeRule/foundation` | | **R** | Já oferecido. |
| `normativeRule/version` | | **R** | Já oferecido. |
| `normativeRule/percentage` | | **R** | Já oferecido. |
| `normativeRule/effectiveFrom` | ⚠️ | **R** | Não oferecido hoje. Proposta: retificável, pela mesma razão do fundamento e da versão — os três descrevem a norma externa que a Modalidade cita. |
| `normativeRule/calculation` | ⚠️ | **N** | **Objeto opaco.** |
| `normativeRule/rounding` | ⚠️ | **N** | **Objeto opaco.** |
| `normativeRule/distribution` | ⚠️ | **N** | **Objeto opaco.** |
| `normativeRule/callRules` | ⚠️ | **N** | **Objeto opaco.** |

## 4. `vacancyTable` — 3 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade da linha (025, FR-170). |
| `modalityId` | | **R** | Já oferecido. |
| `immediateVacancies` | ⚠️ | **R** | Já oferecido — e note a tensão com `profiles/immediateVacancies`, proposto **N**. É exatamente a incoerência que a spec estrutural de vagas existe para resolver. |

## 5. `declaredFacts` — 4 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `code` | | **E** | Identificador estável dentro do Perfil. |
| `label` | | **R** | Já oferecido. |
| `type` | | **N** | Razão já escrita em `retificacao.py`, e normativa: trocar o tipo reinterpretaria valor já congelado sob o tipo anterior. Mudar o tipo é remover um fato e acrescentar outro (015, FR-058). |

## 6. `classificationMilestones` — 26 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `code` | | **E** | Identificador estável. |
| `name` | | **R** | Já oferecido. |
| `stages` | ⚠️ | **N** | Quais Etapas entram na ordem. A auditoria a listou como norma sem decisão; a exclusão de hoje é técnica ("lista de identidades"). |
| `operation` | ⚠️ | **N** | Como as pontuações se combinam. **Era o canário 4 da decisão de origem** (ver D-010). Exclusão de hoje é técnica. |
| `normalization` | ⚠️ | **N** | Valor de lista fechada. Exclusão de hoje é técnica. |
| `rounding` | ⚠️ | **N** | **Objeto opaco.** Classificado inteiro: `rounding/mode` e `rounding/scale` deixam de ser endereçáveis separadamente. Era metade do canário 4 original. |
| `appealWindow/admits` | | **R** | **Canário 3.** |
| `appealWindow/durationDays` | | **R** | **Canário 3.** |
| `appealWindow/unit` | | **R** | **Canário 3.** Lista fechada, oferecida como escolha (FR-311). |
| `drawMethod/algorithm` | | **R** | **Canário 4.** |
| `drawMethod/source` | | **R** | **Canário 4.** |
| `drawMethod/occurrence` | | **R** | **Canário 4.** |
| `drawMethod/occurrenceAt` | | **R** | **Canário 4.** |
| `drawMethod/derivation` | | **R** | **Canário 4.** |
| `drawMethod/normalization/rule` | | **R** | **Canário 4.** |
| `drawMethod/normalization/text` | | **R** | **Canário 4.** |
| `drawMethod/substitutionRule/rule` | | **R** | **Canário 4.** |
| `drawMethod/substitutionRule/text` | | **R** | **Canário 4.** |
| `drawMethod/qualifyingStageId` | | **R** | **Canário 4.** |
| `cutRule/targetKind` | ⚠️ | **N** | Espécie do alvo. Exclusão de hoje é técnica. |
| `cutRule/targetCount` | | **R** | Já oferecido (014, FR-184) — "onde se lê 10, leia-se 12". |
| `cutRule/surplusCount` | | **R** | Já oferecido. |
| `cutRule/tieOutcome` | | **R** | Já oferecido. |
| `cutRule/governedStage` | ⚠️ | **N** | Etapa governada. Exclusão de hoje é técnica ("UUID digitado"). |
| `cutRule/continuation` | ⚠️ | **N** | Política de continuação. Exclusão de hoje é técnica. |

## 7. `tiebreakers` — 5 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade (015, FR-015). |
| `order` | | **R** | Já oferecido — **a ordem é a norma**. |
| `type` | ⚠️ | **N** | O que o critério compara. |
| `parameters` | ⚠️ | **N** | **Objeto opaco.** |
| `whenMissing` | ⚠️ | **N** | O que fazer quando o valor não existe. Lista fechada; exclusão de hoje é técnica. |

## 8. `schedule` — 9 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade; a Etapa a referencia. |
| `type` | ⚠️ | **N** | Espécie do Evento. |
| `description` | | **R** | Já oferecido. |
| `startAt` | | **R** | Já oferecido. |
| `endAt` | | **R** | Já oferecido. |
| `order` | | **E** | Posição no Cronograma. |
| `status` | | **D** | Produzido pelo sistema. Nenhum esquema declara a enumeração dele. |
| `location` | | **R** | **Canário 1.** Hoje nem forma declarada tem. |
| `isRegistrationPeriod` | ⚠️ | **N** | Qual Evento é o período de inscrições. Trocá-lo depois de publicado redefiniria retroativamente quando as inscrições estiveram abertas. |

## 9. `stages` — 13 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Já era `NAO_SAO_NORMA`. |
| `order` | | **E** | Insumo da progressão. Já era `NAO_SAO_NORMA`. |
| `scheduleEventId` | | **E** | ⚠️ Vínculo endereçado pela coleção do Cronograma. Já era `NAO_SAO_NORMA`, **sem razão escrita** — esta linha é a razão que faltava. |
| `name` | | **R** | Já oferecido. |
| `weight` | | **R** | Já oferecido. |
| `minimumScore` | | **R** | Já oferecido. |
| `maximumScore` | | **R** | Já oferecido (012). |
| `evaluationsPerRegistration` | | **R** | Já oferecido (012). |
| `eliminatory` | | **R** | Já oferecido. |
| `classificatory` | | **R** | Já oferecido. |
| `forma` | | **R** | Já oferecido. |
| `rotuloFavoravel` | | **R** | Já oferecido. |
| `rotuloDesfavoravel` | | **R** | Já oferecido. |

## 10. `sections` — 7 campos (6 por item)

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade derivada de `(edital, key)`. |
| `key` | | **E** | Chave do catálogo. |
| `title` | | **N** | O catálogo é fixo: título divergente é recusado pela verificação de topologia. |
| `order` | | **N** | Idem. |
| `type` | | **N** | Idem. |
| `content` | | **R** | Já oferecido. |
| `source` | | **E** | ⚠️ **Campo condicional**: só existe em seção gerada, onde `content` não existe. Declara a coleção que origina o texto. |

## 11. `attachments` — 5 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade que o Documento Exigido referencia. |
| `label` | | **R** | Já oferecido. |
| `order` | | **R** | Já oferecido — ordem editorial. |
| `artifactId` | | **R** | Já oferecido — o arquivo se troca por Retificação. |
| `artifactHash` | | **D** | Derivado dos bytes do artefato. `retificacao.py` já escreve por quê: oferecê-lo faria a tela pedir que alguém copiasse um SHA-256 à mão. |

## 12. `documentRequirements` — 9 campos

| Caminho | ⚠️ | Proposta | Razão / observação |
|---|---|---|---|
| `id` | | **E** | Identidade. |
| `key` | | **N** | Razão já escrita e normativa: é com ela que a inscrição já submetida nomeia o arquivo enviado; trocá-la desligaria o documento do que os candidatos mandaram. |
| `name` | | **R** | Já oferecido. |
| `instructions` | | **R** | Já oferecido. |
| `required` | | **R** | Já oferecido. |
| `order` | | **R** | Já oferecido. |
| `profileId` | | **R** | Já oferecido. |
| `modalityId` | | **R** | Já oferecido. |
| `attachmentId` | | **R** | Já oferecido (020, FR-020). |

---

## Política de objeto ausente — FR-313

Cinco objetos podem estar ausentes do conteúdo. `null` não é campo sem natureza: é declaração que
não foi feita, e a pergunta é se ela pode passar a existir por Retificação.

| Objeto | ⚠️ | Proposta |
|---|---|---|
| `classificationMilestones/cutRule` | ⚠️ | Pode passar a existir. Um marco que não cortava passa a cortar por Retificação, com a regra inteira num ato só — declarar pela metade é o que a validação já recusa. |
| `classificationMilestones/appealWindow` | ⚠️ | Pode passar a existir. Declarar janela onde não havia **concede** prazo, e conceder é menos grave do que retirar. |
| `classificationMilestones/drawMethod` | ⚠️ | **Não pode.** Um marco que não declarou método não sorteia; fazê-lo sortear depois de publicado muda a espécie da ordenação, e não um parâmetro dela. |
| `profiles/vacancyReversion` | ⚠️ | Pode passar a existir — a `016` já a trata como declaração do Edital. |
| `competitionModalities/normativeRule` | ⚠️ | **Não pode.** Modalidade sem regra normativa é Modalidade sem fundamento; acrescentá-lo depois é criar reserva que o Edital publicado não tinha. |

---

## Resumo da proposta

| Natureza | Quantas |
|---|---|
| **R** — retificável | 64 |
| **N** — não retificável | 29 |
| **E** — identidade/estrutural | 24 |
| **D** — derivado | 4 |
| **Total** | **121** |

**30 linhas marcadas ⚠️**, mais as 5 de objeto ausente. São as que precisam do seu julgamento. As demais transcrevem decisão
que o código já registra com razão normativa, ou são identidade sem controvérsia.

**O padrão que a matriz revela**: quase toda linha ⚠️ marcada **N** tem hoje uma exclusão por razão
técnica — "valor fechado", "lista de identidades", "UUID digitado". São exatamente as que a FR-310
manda reexaminar. Se o reexame concluir que boa parte delas é retificável, o número de **R** sobe e
a implementação campo a campo vira backlog derivado — não escopo desta spec.

**A tensão que a matriz não resolve, e que não é dela**: `profiles/immediateVacancies` proposto
**N** e `vacancyTable/immediateVacancies` proposto **R** dizem coisas diferentes sobre o mesmo
número. É o achado S4 da auditoria aparecendo de novo, e a spec estrutural de vagas é quem o
resolve — esta só precisa não fingir que ele não existe.
