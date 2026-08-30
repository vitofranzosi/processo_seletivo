# Fase 1 — Modelo de dados

O que muda no domínio, na persistência e no snapshot. O que não aparece aqui não muda.

## Visão

```text
ProcessoSeletivo
└── Edital                         título e descrição passam a ser alteráveis em elaboração
    ├── PerfilVaga                 (existente)
    │   └── ModalidadeConcorrencia (existente) — passa a ter identidade preservada
    │       └── RegraNormativa     (existente) — ganha faixa e interface
    ├── Cronograma                 (existente)
    │   └── EventoCronograma       (existente) — ganha reordenação na interface
    ├── EtapaAvaliacao             NOVO — do Edital, vale para todos os Perfis
    └── SecaoEdital                NOVO — só o conteúdo das seções textuais
```

`EtapaAvaliacao` pertence ao Edital, e não ao Perfil. A Constituição admite Perfis com Etapas
distintas; esta versão não exerce a permissão (spec, FR-023).

---

## EtapaAvaliacao (novo)

Fase pela qual os candidatos passam. Nasce no padrão de `EventoCronograma`, do qual herda a forma de
ordenação e de identidade.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | chave primária; **preservada** na gravação do rascunho |
| `edital` | FK → `Edital` | `on_delete=CASCADE`, `related_name="etapas"` |
| `name` | texto (200) | obrigatório, não vazio |
| `order` | inteiro positivo | único por Edital |
| `weight` | decimal(7,4) nulo | opcional |
| `eliminatory` | booleano | padrão falso |
| `classificatory` | booleano | padrão falso |
| `minimum_score` | decimal(7,4) nulo | opcional; quando informado, não negativo |
| `evento` | FK → `EventoCronograma` nula | opcional; `on_delete=SET_NULL`; deve pertencer ao mesmo Edital |

**Restrições de banco**: `UniqueConstraint(edital, order)`, no molde de
`uq_evento_cronograma_order`; `CheckConstraint` de `minimum_score >= 0`.

**Ordenação declarada**: `["order", "id"]`.

**Invariantes de domínio** (`editais/domain/etapas.py`): nome obrigatório; ordem sem ambiguidade;
`minimum_score` não negativo; `evento` existente e do mesmo Edital. Uma Etapa pode ser
eliminatória e classificatória ao mesmo tempo (FR-019) — nenhuma regra as opõe. Peso não é exigido
por ser classificatória: exigi-lo seria inventar regra de certame.

**Datas**: quando a Etapa referencia um Evento, as datas são as do Evento e não são copiadas
(FR-021). Não há campo de data na Etapa.

---

## SecaoEdital (novo)

Guarda **apenas** o conteúdo redigido das seções textuais. A estrutura do documento — quais seções
existem, em que ordem, de que tipo, com que título — é declaração em
`editais/domain/secoes.py`, não linha de tabela.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | chave primária; preservada na gravação |
| `edital` | FK → `Edital` | `on_delete=CASCADE`, `related_name="secoes"` |
| `key` | texto (60) | chave do catálogo; única por Edital; deve existir no catálogo e ser de seção textual |
| `content` | texto | conteúdo redigido; nasce com o texto institucional do catálogo |

O Edital que ainda não teve uma seção textual editada simplesmente não tem a linha: o conteúdo é o
padrão do catálogo. Uma seção gerada nunca tem linha.

### Catálogo de seções (declaração)

Cada entrada declara `key`, `title`, `order`, `type` e, conforme o tipo, `source` ou `default_text`.

| type | Significado | Campo próprio |
|---|---|---|
| `GENERATED` | conteúdo derivado dos dados estruturados | `source` — qual coleção origina (`profiles`, `schedule`, `stages`, modalidades) |
| `TEXT` | conteúdo redigido por quem elabora | `default_text` — redação institucional inicial |

Uma seção `GENERATED` cuja fonte esteja vazia não é composta no documento (caso de borda da spec).

---

## Alterações em entidades existentes

### Edital

Nenhum campo novo. `title` e `description` passam a ser alteráveis por
`update_edital_identification` enquanto o status for `EM_ELABORACAO` (FR-006).

### ModalidadeConcorrencia

Nenhum campo novo. Muda o **comportamento da gravação**: passa a ser criada com o `id` recebido, como
`PerfilVaga` e `EventoCronograma` já são (`editais/application/draft.py:87-92`), e o identificador
recebido passa a ser verificado quanto ao pertencimento, junto dos demais.

### RegraNormativa

Nenhum campo novo. `percentage` ganha faixa validada no domínio: opcional e, quando informado,
maior que zero e menor ou igual a cem (FR-030). `foundation` passa a ter interface.

`calculation`, `rounding`, `distribution` e `call_rules` permanecem intocados e fora da interface
(FR-032): pertencem à jornada do candidato.

---

## Snapshot canônico

`SCHEMA_VERSION` passa de 1 para 2, uma vez, cobrindo as duas coleções novas (FR-043).

```jsonc
{
  "schemaVersion": 2,
  "editalId": "…", "processoId": "…",
  "number": 1, "year": 2026, "title": "…", "description": "…",
  "profiles": [ /* inalterado */ ],
  "schedule": [ /* inalterado */ ],
  "stages": [
    {
      "id": "…", "name": "Prova didática", "order": 1,
      "weight": "2.0000", "eliminatory": true, "classificatory": true,
      "minimumScore": "7.0000", "scheduleEventId": "…"
    }
  ],
  "sections": [
    { "key": "disposicoes-preliminares", "title": "…", "order": 1,
      "type": "TEXT", "content": "…" },
    { "key": "cronograma", "title": "…", "order": 5,
      "type": "GENERATED", "source": "schedule" }
  ]
}
```

A seção `GENERATED` **não tem `content`**. É essa ausência que a torna não endereçável, sem regra
nova na gramática (D-006).

### Registros a atualizar

| Registro | Arquivo | O que entra |
|---|---|---|
| Coleções com chave | `publicacoes/domain/colecoes.py` | `/stages`, `/sections` |
| Forma publicada | `editais/domain/validation.py` | tuplas `ETAPA_PUBLICADA` e `SECAO_PUBLICADA` em `COLECOES_PUBLICADAS` |
| Snapshot | `publicacoes/application/publish_edital.py` | `stages` e `sections` em `edital_snapshot` |

Os três são declarativos e a `005` já falha a suíte quando uma coleção do snapshot não está
declarada — esquecer um deles aparece como falha, não como silêncio.

### Forma publicada das coleções novas

`ETAPA_PUBLICADA`: `id` (uuid), `name`, `order` (mínimo 0), `weight` (texto, admite nulo),
`eliminatory` (booleano), `classificatory` (booleano), `minimumScore` (texto, admite nulo),
`scheduleEventId` (uuid, admite nulo).

`SECAO_PUBLICADA`: `key`, `title`, `order` (mínimo 0), `type` (valores `GENERATED`, `TEXT`).
`content` e `source` não são declarados obrigatórios porque dependem do tipo — a coerência entre
campos não é expressável em `Campo`, e a declaração existente registra essa ausência como
deliberada.

**Chave estável das seções**: a coleção é endereçada por `id` como as demais, e o `id` da seção no
snapshot é a `key` do catálogo — estável por construção, legível no caminho de Retificação, e
independente de posição.

---

## Migrations

Três, todas diretas. Sem mecanismo de compatibilidade e sem migração de conteúdo (FR-046).

1. `EtapaAvaliacao` com suas restrições.
2. `SecaoEdital` com unicidade de `key` por Edital.
3. Nenhuma alteração de esquema é necessária para modalidades: a preservação de identidade é
   comportamento da camada de aplicação.

Seeds e fixtures são regenerados. `seed_demo` passa a criar Etapas e a exercitar uma modalidade com
Regra Normativa completa, para que a demonstração tenha conteúdo desde o primeiro `runserver`.
