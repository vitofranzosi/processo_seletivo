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
| `weight` | decimal(7,4) nulo | opcional; quando informado, maior que zero (FR-020) |
| `eliminatory` | booleano | padrão falso |
| `classificatory` | booleano | padrão falso |
| `minimum_score` | decimal(7,4) nulo | opcional; quando informado, não negativo |
| `evento` | FK → `EventoCronograma` nula | opcional; `on_delete=SET_NULL`; deve pertencer ao mesmo Edital |

**Restrições de banco**: `UniqueConstraint(edital, order)`, no molde de
`uq_evento_cronograma_order`; `CheckConstraint` de `minimum_score >= 0` e de `weight > 0`.

**Ordenação declarada**: `["order", "id"]`.

**Invariantes de domínio** (`editais/domain/etapas.py`): nome obrigatório; ordem sem ambiguidade;
`weight` maior que zero quando informado; `minimum_score` não negativo; `evento` existente e do mesmo
Edital. Uma Etapa pode ser
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
| `id` | UUID | chave primária; **é o mesmo UUID determinístico do snapshot** — `uuid5` sobre `(edital.id, key)` — para que a seção tenha uma identidade só |
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

Nenhum campo novo, e a mesma correção de identidade: hoje também é criada sem o `id` recebido
(`editais/application/draft.py:95-105`), e esse `id` viaja no conteúdo publicado
(`publicacoes/application/publish_edital.py:36`). Passa a ser preservado e verificado **contra a
Modalidade**, que é o contêiner dela (`editais/models/perfis.py:63-66`) — verificar só até o Perfil
deixaria passar a troca de identidades entre Modalidades irmãs.

`percentage` ganha faixa validada no domínio: opcional e, quando informado, maior que zero e menor
ou igual a cem (FR-030). `foundation` e `version` passam a ter interface — `version` é obrigatório no
command e no contrato desde a `001`, de modo que sem campo nenhuma regra nova seria gravável.

`calculation`, `rounding`, `distribution` e `call_rules` permanecem intocados e fora da interface
(FR-032): pertencem à jornada do candidato.

---

## Snapshot canônico

`SCHEMA_VERSION` passa de 1 para 2, uma vez, cobrindo as duas coleções novas (FR-045).

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
    { "id": "…", "key": "disposicoes-preliminares", "title": "…", "order": 1,
      "type": "TEXT", "content": "…" },
    { "id": "…", "key": "cronograma", "title": "…", "order": 5,
      "type": "GENERATED", "source": "schedule" }
  ]
}
```

A seção `GENERATED` **não tem `content`**. É essa ausência que a torna não endereçável, sem regra
nova na gramática (D-006).

**`id` e `key` são coisas diferentes, e as duas são necessárias.** O `id` é UUID porque o seletor da
gramática só aceita UUID (`publicacoes/domain/changes.py:101-113`); a `key` é o identificador
textual do catálogo, que dá sentido humano ao item e liga o snapshot à declaração. O `id` é
determinístico — `uuid5` sobre `(edital.id, key)` — para que a seção tenha identidade estável antes
de existir qualquer linha em `SecaoEdital`, o que é sempre o caso das geradas e o caso inicial das
textuais (D-010).

### Registros a atualizar

| Registro | Arquivo | O que entra |
|---|---|---|
| Coleções com chave | `publicacoes/domain/colecoes.py` | `/stages`, `/sections` |
| Forma publicada | `editais/domain/validation.py` | tuplas `ETAPA_PUBLICADA` e `SECAO_PUBLICADA` em `COLECOES_PUBLICADAS` |
| Snapshot | `publicacoes/application/publish_edital.py` | `stages` e `sections` em `edital_snapshot` |

Os três são declarativos, mas **a suíte hoje não acusa sozinha o esquecimento de qualquer um deles**:
a transcrição da forma publicada é conferida contra uma lista explícita
(`tests/contract/test_forma_publicada.py:67-70`). Por isso esta feature acrescenta um teste de
cobertura ligando as três declarações — para cada coleção do snapshot, forma declarada em
`COLECOES_PUBLICADAS` e esquema correspondente no `openapi.yaml` (D-005).

### Forma publicada das coleções novas

`ETAPA_PUBLICADA`: `id` (uuid), `name`, `order` (mínimo 0), `weight` (texto com padrão decimal,
admite nulo), `eliminatory` (booleano), `classificatory` (booleano), `minimumScore` (texto com
padrão decimal, admite nulo), `scheduleEventId` (uuid, admite nulo).

`SECAO_PUBLICADA`: `id` (uuid), `key`, `title`, `order` (mínimo 0), `type` (valores `GENERATED`,
`TEXT`).

**O decimal precisa de formato, não só de padrão.** `_formato_satisfeito` só é alcançado quando o
campo declara `formato`, e o leitor é buscado em `_LEITOR_DE_FORMATO` — um formato declarado sem
leitor registrado levanta `KeyError` de propósito (`editais/domain/validation.py:119-144`).
Portanto: `formato="decimal"` com leitor `Decimal` registrado.

**O padrão descreve a forma canônica, e só ela.** Os dois campos são `decimal(7,4)`: no máximo três
dígitos inteiros, sempre quatro casas, e **sem zeros à esquerda**, porque é assim que a persistência
os materializa. `^-?(0|[1-9]\d{0,2})\.\d{4}$`. As duas versões anteriores erravam por excesso:
`^\d+(\.\d{1,4})?$` aceitava inteiro de qualquer tamanho e casas de menos, e `^\d{1,3}\.\d{4}$`
ainda aceitava `001.0000` — forma que o sistema nunca escreve e que permitiria a uma Retificação
semanticamente nula alterar o hash do conteúdo. `edital_snapshot` materializa os dois com quatro
casas explícitas, e não pelo `str` de um `Decimal` qualquer.

**O sinal é admitido no padrão de propósito, e a faixa é regra de domínio.** Nenhum dos dois valores
é negativo hoje — as restrições de banco impedem —, mas o padrão descreve **forma**, não permissão.
Deixá-lo recusar o sinal misturaria as duas coisas, e foi assim que a versão anterior deste documento
acabou derivando de uma expressão regular uma invariante que a spec não declarava. A faixa fica onde
pertence: na verificação direcionada das Etapas, que já percorre a coleção para conferir a referência
ao Evento — peso maior que zero, nota mínima não negativa. Uma passagem, três conferências.

`content` e `source` não entram na forma declarada porque dependem do tipo, e `Campo` não expressa
coerência entre campos — ausência deliberada, registrada no próprio módulo.

### O que a forma declarada não alcança

Duas verificações próprias entram na validação de publicação, porque a forma por campo não as
cobre e sem elas o catálogo fixo e a fonte normativa única deixariam de valer depois da publicação
(D-011):

| Verificação | O que recusa |
|---|---|
| Topologia de `sections` contra o catálogo | seção acrescentada ou removida; `type`, `order`, `title`, `key` ou `source` alterados; textual sem `content`; gerada com `content` |
| Coerência de cada Etapa | `scheduleEventId` que não existe em `schedule`; peso menor ou igual a zero; nota mínima negativa |

Só o `content` das seções textuais pode variar. As duas são verificações escritas para estes dois
casos, no arquivo que já faz a verificação de publicação — não um mecanismo de regras entre campos.

---

## Migrations

Duas, ambas diretas. Sem mecanismo de compatibilidade e sem migração de conteúdo (FR-048).

1. `EtapaAvaliacao` com suas restrições.
2. `SecaoEdital` com unicidade de `key` por Edital.

Modalidades **não exigem migration**: a preservação de identidade é comportamento da camada de
aplicação, sobre um campo que já existe.

Seeds e fixtures são regenerados. `seed_demo` passa a criar Etapas e a exercitar uma modalidade com
Regra Normativa completa, para que a demonstração tenha conteúdo desde o primeiro `runserver`.
