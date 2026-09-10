# Contrato — 025 · Quadro de Vagas por Modalidade

Fase 1. Três contratos, e nenhum deles é novo em espécie: uma coleção no rascunho, uma coleção no
conteúdo publicado, e os caminhos de Retificação que a segunda habilita.

O contrato canônico do projeto é `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, e
`tests/contract/test_openapi_conformance.py` verifica o comportamento observável contra ele. **Este
documento diz o que muda lá**, e não substitui aquele arquivo.

---

## 1 · Rascunho — `PUT /api/v1/editais/{id}/draft`

`PerfilInput` (`openapi.yaml:630`) ganha uma coleção **opcional**:

```yaml
vacancyTable:
  type: array
  items: { $ref: '#/components/schemas/LinhaDoQuadroInput' }
```

```yaml
LinhaDoQuadroInput:
  type: object
  description: >-
    Uma linha do quadro de vagas do Perfil. `modalityId` nulo ou ausente é a **linha geral** — a da
    ampla concorrência —, e há no máximo uma por Perfil. Com `modalityId`, é linha reservada, e há no
    máximo uma por Modalidade. `id` é obrigatório e preservado na gravação, como o de Perfil,
    Modalidade e Etapa: identificador que já pertença a outro contêiner responde 409
    identifier_belongs_to_another_edital.
  required: [id, immediateVacancies]
  properties:
    id: { $ref: '#/components/schemas/Id' }
    modalityId: { type: [string, 'null'], format: uuid }
    immediateVacancies: { type: integer, minimum: 0 }
```

**Opcional** porque o rascunho legitimamente não traz quadro (`FR-160`), como
`classificationMilestones` e `declaredFacts` já são.

**`id` obrigatório** pela razão que `ModalidadeInput` já documenta: opcional, ele reabriria o defeito
que a estabilidade veio fechar — o servidor geraria um identificador que a resposta não devolve, e a
gravação seguinte trocaria a identidade de novo.

### Recusas

| Situação | Código | HTTP | Requisito |
|---|---|---|---|
| `modalityId` de Modalidade de **outro Perfil** | `invalid_profiles` | 422 | `FR-158` |
| `modalityId` que não é de Perfil nenhum deste Edital | `invalid_profiles` | 422 | `FR-158` |
| duas linhas gerais no mesmo Perfil | `invalid_profiles` | 422 | `FR-154` |
| duas linhas para a mesma Modalidade | `invalid_profiles` | 422 | `FR-155` |
| `immediateVacancies` negativo ou não inteiro | `invalid_profiles` | 422 | `FR-156` |
| `id` de linha pertencente a outro Edital | `identifier_belongs_to_another_edital` | 409 | — |

Toda recusa carrega `campo` e `identidade` — `campo="modalityId"` ou `"immediateVacancies"`,
`identidade=<id da linha>` —, que é a forma que `RecusaDeCampo` define para a interface ancorar o
erro na linha certa.

**As mensagens de referência cruzada são as que já existem**, com o sujeito trocado:

```
A linha do quadro aponta uma modalidade que não pertence ao Perfil declarado.
A linha do quadro aponta uma modalidade que não é de nenhum Perfil deste Edital.
```

---

## 2 · Submissão e publicação

`POST /api/v1/editais/{id}/submit` e `POST /api/v1/editais/{id}/publish`.

Nenhuma rota nova. Dois achados novos entram na classificação que a operação já produz:

| Código | Nível | Quando | Requisito |
|---|---|---|---|
| `vacancy_sum_mismatch` | **impeditivo** | quadro **completo** cuja soma diverge do total de vagas imediatas do Perfil | `FR-161`, `SC-054` |
| `vacancy_sum_exceeds_total` | **impeditivo** | quadro **completo ou parcial** cuja soma **excede** o total | `FR-177` |
| `vacancy_row_modality_missing` | **impeditivo** | linha cujo `modalityId` não existe no Perfil | `FR-166`, `FR-172` |
| `vacancy_row_percentage_divergence` | **aviso** | quantidade diverge do percentual da Regra Normativa | `FR-163` |

A mensagem de `vacancy_sum_mismatch` diz os **três** números (`UX-023`):

```
O quadro de vagas do Perfil 'P1' soma 79 e o Perfil declara 80 vagas imediatas — diferença de 1.
```

**Quadro completo** = linha geral presente **e** nenhuma Modalidade declarada sem linha. Quadro
parcial e quadro ausente não disparam a conferência **de igualdade** (`D-006`, `FR-160`) — mas o
limite superior da `FR-177` vale para todo quadro declarado, porque somar mais do que o Perfil
oferece não é legítimo em quadro algum.

**A conferência alcança a Retificação**, sobre o conteúdo que ela produziria: um quadro que fecha não
pode ser retificado para um que não fecha (`FR-161`). Reduzir uma linha e o total do Perfil é um ato
só, e quem retifica declara os dois — como na `D-008`.

---

## 3 · Conteúdo publicado

`PerfilPublicado` (`openapi.yaml:735`) ganha `vacancyTable` em `properties` **e** em `required`.

```yaml
LinhaDoQuadroPublicada:
  type: object
  description: >-
    Uma linha do quadro publicado. `modalityId` nulo é a linha geral, a da ampla concorrência — a
    mesma grafia que `AtoDeOrdenacao.lista_id` e `Inscricao.modality_id` já praticam. A ordem da
    linha é a posição no array e não é campo: ela é apresentação, não norma.
  required: [id, modalityId, immediateVacancies]
  properties:
    id: { $ref: '#/components/schemas/Id' }
    modalityId: { type: [string, 'null'], format: uuid }
    immediateVacancies: { type: integer, minimum: 0 }
```

**`required` no publicado, opcional no input**, é a `D-005` no contrato: depois do degrau 12 todo
conteúdo publicado **tem** a chave — vazia nos anteriores. Duas grafias para a ausência, ausente e
vazia, é o que a `D-005` existe para não permitir.

**A forma interna é verificada**, ao contrário da de `competitionModalities` — que é a única coleção
do snapshot cuja forma de dentro não é declarada. A linha carrega um número que a conferência vai
somar, e somar campo não verificado é somar o que ninguém garantiu ser inteiro.

### Versão de schema

```
schemaVersion: 11  →  12
```

Todo conteúdo publicado antes do degrau passa a ser lido com `vacancyTable: []`. **Lista vazia
significa quadro não publicado, nunca zero vaga.**

---

## 4 · Retificação — os caminhos que passam a existir

Nenhuma gramática nova. Declarada a coleção em `COLECOES_COM_CHAVE`, as três operações que já existem
passam a alcançá-la:

| Operação | Caminho | Efeito |
|---|---|---|
| `ADD` | `/profiles/id=…/vacancyTable/-` | acrescenta linha; nasce com identidade própria (`FR-171`) |
| `REPLACE` | `/profiles/id=…/vacancyTable/id=…/immediateVacancies` | altera a quantidade daquela linha |
| `REPLACE` | `/profiles/id=…/vacancyTable/id=…/modalityId` | corrige a Modalidade que a linha aponta |
| `REMOVE` | `/profiles/id=…/vacancyTable/id=…` | remove a linha e o que estava dentro dela |

**Endereçamento por posição é recusado**, como em toda coleção com chave:
`/profiles/id=…/vacancyTable/0` responde `422 positional_addressing_refused` (`FR-170`).

`REPLACE` e `REMOVE` exigem `expectedPreviousHash`, como em toda a gramática — sem ele,
`precondition_missing`.

### A recusa que a `D-008` exige

```
REMOVE /profiles/id=P1/competitionModalities/id=PPI
```

…sozinha é **recusada** enquanto existir linha apontando `PPI`, com `vacancy_row_modality_missing`
nomeando a linha. O mesmo ato contendo **as duas** remoções passa: a verificação é sobre o conteúdo
**resultante**, e não sobre cada operação.

> **A tela não desfaz o vínculo sozinha.** Para os Anexos ela faz — remover um Anexo emite
> automaticamente o `REPLACE …/attachmentId → None`. Aqui isso está **proibido**: lá a emissão
> automática desfaz um vínculo; aqui apagaria uma quantidade publicada como efeito colateral de
> outro movimento, que é a alternativa que a `D-008` recusou por escrito. Quem retifica declara os
> dois movimentos.

---

## 5 · Contrato de tela

Rota nenhuma muda. A composição do Perfil (`/gestao/editais/<id>/compor/perfis/`) ganha uma seção
dentro do cartão de cada Perfil; a Retificação ganha a coleção no catálogo de campos.

| Regra | Requisito |
|---|---|
| O quadro é seção da tela de composição do Perfil, e não tela à parte | `UX-020` |
| Só quantidades são digitadas; as linhas vêm das Modalidades já declaradas | `UX-021`, `SC-048`, `SC-052` |
| A linha geral é distinguível sem depender de cor, e diz na tela que é a da ampla concorrência | `UX-022` |
| A divergência é dita em números — soma, declarado, diferença | `UX-023` |
| Quantidade em branco **não grava linha**; ausência nunca vira zero | `FR-159`, `D-006` |
