# Data Model: Integridade do Snapshot Normativo

**Feature**: `005-integridade-do-snapshot` | **Fase**: 1 | **Data**: 2026-08-29

Esta feature **não cria entidade, coluna nem migração**. O que ela acrescenta é a forma canônica do
Perfil e do Evento **publicados**, declarada no contrato e transcrita no domínio.

## Por que não os esquemas de entrada

`PerfilInput` e `EventoInput` descrevem o que o rascunho **aceita**, e não o que a Publicação
**produz**. A diferença é material:

| | Campos |
| --- | --- |
| Perfil publicado | 12 |
| Exigidos por `PerfilInput` | 5 |
| Ficariam sem verificação | `description`, `requirements`, `reserveLimit`, `locality`, `classificationInformation`, `callInformation`, `competitionModalities` |

Um Perfil reduzido aos cinco campos de entrada passaria — e ele é exatamente o Perfil mutilado que
esta feature existe para impedir. `requirements`, medido como defeito na avaliação da spec, está
entre os que ficariam de fora.

Por isso o contrato ganha **`PerfilPublicado`** e **`EventoPublicado`**: esquemas de saída, que
reaproveitam o que os de entrada já declaram e completam o que eles não cobrem (FR-005).

## Perfil publicado — `/profiles/id=<uuid>`

| Campo | Obrigatório | Tipo | Admite nulo | Restrição declarada |
| --- | --- | --- | --- | --- |
| `id` | sim | texto | não | formato uuid |
| `code` | sim | texto | não | — |
| `name` | sim | texto | não | — |
| `description` | sim | texto | não | — |
| `requirements` | sim | lista | não | — |
| `immediateVacancies` | sim | inteiro | não | mínimo 0 |
| `reserveType` | sim | texto | não | um de `NONE`, `LIMITED`, `UNLIMITED` |
| `reserveLimit` | sim | inteiro | **sim** | mínimo 0 |
| `locality` | sim | texto | não | — |
| `classificationInformation` | sim | objeto | não | — |
| `callInformation` | sim | objeto | não | — |
| `competitionModalities` | sim | lista de objetos | não | — |

**Obrigatório aqui significa presente**, e não preenchido. `description` e `locality` podem ser texto
vazio; `requirements`, lista vazia; `classificationInformation`, objeto vazio. É a distinção de
FR-007 entre "não preenchido" e "malformado".

## Evento publicado — `/schedule/id=<uuid>`

| Campo | Obrigatório | Tipo | Admite nulo | Restrição declarada |
| --- | --- | --- | --- | --- |
| `id` | sim | texto | não | formato uuid |
| `type` | sim | texto | não | — |
| `description` | sim | texto | não | — |
| `startAt` | sim | texto | não | formato data-e-hora |
| `endAt` | sim | texto | **sim** | formato data-e-hora |
| `order` | sim | inteiro | não | mínimo 0 |
| `status` | sim | texto | não | — |

`status` é produzido pelo sistema e nenhum esquema de entrada o declara. Entra como presença e tipo;
**a enumeração dele não é declarada aqui**, porque escrevê-la seria inventar restrição, e não
transcrever uma (FR-009).

## Restrições que se aplicam, e a que não se aplica

| | Situação |
| --- | --- |
| `minimum` e `enum` já escritos no contrato | **Aplicados.** Não aplicá-los criaria garantia nova para preservar comportamento inválido. |
| Coerência entre campos — `reserveLimit` conforme `reserveType`, `endAt` depois de `startAt` | **Fora.** Ninguém decidiu essas regras ainda, e decidi-las aqui seria decidir por antecipação. |
| Enumeração de `status`, que só o serializer conhece | **Fora.** Transcrever o contrato é aplicar; transcrever o serializer para o contrato é escrever regra nova. |

## Raiz do Edital

Sem mudança. As quatro condições que já existem continuam como estão: título obrigatório, ao menos
um Perfil, ao menos um Evento, descrição como aviso.

## O que fica sem forma declarada

`competitionModalities` é conferido como lista de objetos, e nada sobre o que há dentro. A
verificação alcança Perfil e Evento (FR-004); a Publicação original também não confere Modalidades,
de modo que SC-005 continua de pé. Fechar isso é feature própria, e está no *Out of Scope*.

## O achado de validação

Sem campo novo. `ValidationFinding` já carrega severidade, código, mensagem e caminho.

| Elemento | Valor |
| --- | --- |
| Severidade | erro impeditivo |
| Caminho | `/profiles/id=<uuid>/requirements` — a gramática da `004`, que nomeia a entidade sem consultar a versão vigente |
| Mensagem | diz **qual** violação ocorreu: ausente, tipo diferente, nulo indevido, formato inválido, fora da restrição (FR-011) |

## Invariantes

- Todo Perfil e todo Evento do conteúdo que passa a vigorar tem os campos da forma canônica, com o
  tipo declarado, nulo apenas onde admitido, formato satisfeito e dentro das restrições escritas.
- A invariante vale em **cada fronteira de vigência** materializada, e não só na primeira.
- Campo que a forma canônica não declara nunca é motivo de recusa.
- Coerência entre campos não é verificada, e a garantia não a inclui.

## Estados e transições

Nenhuma transição nova. A feature não toca no ciclo de vida do Edital nem da Retificação — apenas
acrescenta uma condição de recusa em dois pontos que já recusam.
