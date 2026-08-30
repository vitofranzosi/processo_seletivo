# Data Model: Integridade do Snapshot Normativo

**Feature**: `005-integridade-do-snapshot` | **Fase**: 1 | **Data**: 2026-08-29

Esta feature **não cria entidade, coluna nem migração**. O que ela acrescenta é uma declaração: qual
é a forma de um Perfil e de um Evento no conteúdo normativo, transcrita do contrato e verificada
contra ele.

## A forma declarada

Transcrição de `PerfilInput` e `EventoInput` do `openapi.yaml` da `001`, nas quatro dimensões que
FR-006 exige. As colunas são o que se verifica; o que o contrato declara além delas está na seção
seguinte.

A verificação alcança cada Perfil e cada Evento do conteúdo (FR-004).

### Perfil — `/profiles/id=<uuid>`

| Campo | Obrigatório | Tipo | Admite nulo | Formato |
| --- | --- | --- | --- | --- |
| `id` | sim | texto | não | uuid |
| `code` | sim | texto | não | — |
| `name` | sim | texto | não | — |
| `immediateVacancies` | sim | inteiro | não | — |
| `reserveType` | sim | texto | não | — |
| `reserveLimit` | não | inteiro | **sim** | — |
| `competitionModalities` | não | lista de objetos | não | — |

### Evento — `/schedule/id=<uuid>`

| Campo | Obrigatório | Tipo | Admite nulo | Formato |
| --- | --- | --- | --- | --- |
| `id` | sim | texto | não | uuid |
| `type` | sim | texto | não | — |
| `description` | sim | texto | não | — |
| `startAt` | sim | texto | não | data-e-hora |
| `endAt` | não | texto | **sim** | data-e-hora |
| `order` | não | inteiro | não | — |

### Raiz do Edital

Sem mudança. As quatro condições que já existem continuam como estão: título obrigatório, ao menos
um Perfil, ao menos um Evento, descrição como aviso.

## O que o contrato declara e esta feature não verifica

```yaml
immediateVacancies: { minimum: 0 }
reserveType:        { enum: [NONE, LIMITED, UNLIMITED] }
reserveLimit:       { minimum: 0 }
order:              { minimum: 0 }
```

São regra de negócio, e FR-009 as mantém fora. **Depois desta feature, um Perfil com
`immediateVacancies: -3` ou `reserveType: "QUALQUER"` continua publicável.** Está escrito aqui para
que a garantia não seja lida como maior do que é.

O teste que confere a declaração contra o contrato compara **apenas as quatro dimensões**. Comparar
tudo o faria exigir o que esta feature decidiu não exigir.

## O que não tem forma declarada

`competitionModalities` é `{ type: array, items: { type: object } }` no contrato: lista de objetos, e
nada sobre o que há dentro. A verificação confere que é lista de objetos e para aí. É o contrato
traçando o limite, não uma omissão — e no dia em que as Modalidades ganharem forma declarada, a
verificação passa a alcançá-las sem mudança de desenho.

`classificationInformation`, `callInformation`, `description` e `requirements` aparecem no snapshot
publicado e **não** estão em `PerfilInput`. Seguem aceitos e não exigidos (FR-008).

## O achado de validação

Sem campo novo. `ValidationFinding` já carrega severidade, código, mensagem e caminho.

| Elemento | Valor |
| --- | --- |
| Severidade | erro impeditivo, para as quatro violações |
| Caminho | `/profiles/id=<uuid>/name` — a gramática da `004`, que nomeia a entidade sem consultar a versão vigente |
| Caminho, sem identificador utilizável | `/profiles/2/name` — recuo de legibilidade num caso que a `004` já recusa na origem, e melhor que achado mudo |

## Invariantes

- Todo Perfil e todo Evento do conteúdo que passa a vigorar tem os campos que o contrato declara
  obrigatórios, com o tipo declarado, nulo apenas onde admitido e formato satisfeito.
- A invariante vale em **cada fronteira de vigência** materializada, e não só na primeira.
- Campo que o contrato não declara nunca é motivo de recusa.
- A verificação não decide nada sobre valor: faixa e enumeração continuam fora.

## Estados e transições

Nenhuma transição nova. A feature não toca no ciclo de vida do Edital nem da Retificação — apenas
acrescenta uma condição de recusa em dois pontos que já recusam.
