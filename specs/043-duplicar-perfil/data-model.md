# Data Model: Duplicar Perfil

**Feature**: [spec.md](./spec.md) · **Pesquisa**: [research.md](./research.md)

**Nenhuma entidade nova, nenhum campo novo, nenhuma migration.** A cópia é um Perfil de Vaga comum,
com a forma do contrato do rascunho que `replace_draft` já aceita. O que este documento fixa é a
**transformação** origem → cópia, campo a campo, porque é ela que `FR-639` manda conferir contra o
contrato inteiro.

---

## A transformação

Entrada: um Perfil na forma de `forms.ler_perfis` — o que está digitado —, com
`classificationMilestones` preenchido pela origem certa (`R-003`); o Código e a Localidade
informados; as identidades das Etapas do Edital; o Código e a denominação **gravados** da origem,
quando ela está gravada (`R-005`).

Saída: um Perfil na mesma forma.

| Campo do Perfil | Na cópia | Requisito |
|---|---|---|
| `id` | **novo** | `FR-640` |
| `code` | o informado no diálogo | `FR-635` |
| `locality` | a informada no diálogo | `FR-635` |
| `name`, `description`, `requirements`, `workload`, `compensation`, `duties` | iguais | `FR-639` |
| `immediateVacancies`, `reserveType`, `reserveLimit` | iguais | `FR-639` |
| `vacancyReversion`, `callForm` | iguais | `FR-639` |
| `generalCompetitionModalityId` | a Modalidade **da cópia** correspondente; `None` segue `None` | `FR-641` |
| `competitionModalities[].id` | **novo** | `FR-640` |
| `competitionModalities[].normativeRule.id` | **novo**, distinto por Regra mesmo quando a origem a traz vazia | `FR-640` · `R-002` |
| demais campos da Modalidade e da Regra | iguais | `FR-639` |
| `vacancyTable[]` geral (`modalityId` nulo) — `id` | `identidade_da_linha_geral(<id novo>)` | `FR-640` |
| `vacancyTable[]` reservada — `id` | **novo** | `FR-640` |
| `vacancyTable[]` reservada — `modalityId` | a Modalidade **da cópia** correspondente | `FR-641` |
| `vacancyTable[].immediateVacancies` | igual | `FR-639` |
| `declaredFacts[].id` | **novo** | `FR-640` |
| demais campos do fato | iguais | `FR-639` |
| `classificationMilestones[].id` | **novo** | `FR-640` |
| `classificationMilestones[].code`, `.name` | derivados do Perfil novo **se** derivados da origem; senão iguais | `FR-644` · `R-005` |
| `classificationMilestones[].stages[]` | **iguais** — Etapas do Edital | `FR-642` |
| `classificationMilestones[].drawMethod.qualifyingStageId` | **igual** — Etapa do Edital | `FR-642` |
| `classificationMilestones[].cutRule.governedStage` | **igual** — Etapa do Edital, ou o sentinela de *nenhuma*. `remapear` a troca desde o #169, e aqui a Etapa do Edital mapeia para si mesma; Etapa de fora estoura | `FR-642` |
| demais campos do marco (forma da ordem, operação, normalização, arredondamento, janela recursal, método de sorteio, regra de corte) | iguais | `FR-639` |
| `tiebreakers[].id` | **novo** | `FR-640` |
| `tiebreakers[].parameters.factId` | o fato **da cópia** correspondente | `FR-641` |
| `tiebreakers[].parameters.stageId` | **igual** — Etapa do Edital | `FR-642` |
| `classificationInformation`, `callInformation` | **ausentes** | `FR-643` |

**Regra de fechamento**: todo campo do contrato do Perfil está em exatamente uma destas categorias —
*igual*, *novo*, *remapeado para dentro*, *preservado para fora*, *informado*, *derivado* ou
*ausente*. O teste de completude enumera os campos a partir do **contrato** — a saída de
`forms.perfis_persistidos`, que é o formato que a gravação reenvia e o único que carrega também os
campos sem tela —, e não desta tabela nem do leitor da tela: `ler_perfis` não conhece
`classificationInformation` e `callInformation`, e um campo novo sem tela passaria sem categoria.
Campo do contrato que não tiver categoria reprova.

## Invariantes da cópia

- **Nenhuma identidade compartilhada** com a origem, nem com qualquer Perfil do Edital (`SC-232`).
- **Nenhuma referência para a origem**: toda referência interna aponta a própria cópia; toda
  referência externa aponta o Edital (`SC-232`).
- **Referência interna sem contraparte estoura** `ReferenciaNaoMapeada` — nunca atravessa
  (`FR-641`).
- **A origem não muda**: a função é pura, e não altera o dicionário que recebe (`FR-646`).
- **Nenhum Documento Exigido** é produzido (`FR-645`).

## O campo em trânsito

`perfil-<i>-marcosEmTransito` — JSON `{"marcos": [...], "derivados": [[código, nome], ...]}`: a
coleção `classificationMilestones` na forma do contrato do rascunho e, por marco, se o código e a
denominação são derivados do Perfil. A leitura os deriva de novo do Código e da denominação
digitados então, para que corrigir o Código da cópia antes de gravar leve o marco junto (revisão de
código, FR-644). Emitido pelo cartão **só** para Perfil ainda não gravado que tenha marcos; lido por
`ler_perfis`; devolvido por `_reexibir_perfis`. Não é campo do contrato: é transporte da tela, e
some quando o Perfil é gravado (`R-003`).

JSON inválido no campo é recusa da gravação com mensagem no Perfil, e não erro 500. E a gravação
confere que os marcos em trânsito de Perfil novo citam só Etapas **deste** Edital e fatos **do
próprio** Perfil (`views._conferir_marcos_em_transito`): o campo é entrada de quem envia, e não passa
pelo leitor da Classificação.
