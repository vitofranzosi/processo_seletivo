# Implementation Plan: Contrato de mutabilidade normativa

**Branch**: `claude/spec-026-contrato-de-mutabilidade-normativa` | **Date**: 2026-09-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/026-contrato-de-mutabilidade-normativa/spec.md`

## Summary

De 13 a 23 campos de norma publicada por Edital não têm decisão de retificabilidade — nem "sim",
nem "não", nem "não se aplica". A feature declara a natureza de mutabilidade de **todo** campo do
conteúdo canônico publicado, põe um guardião que falha por omissão quando nasce campo sem decisão,
e prova o contrato por quatro correções administrativas que hoje só se fazem por chamada de API.

A abordagem técnica, depois da [pesquisa](research.md): **aprofundar um mecanismo que já existe**.
`test_toda_colecao_de_entidades_do_snapshot_esta_declarada` já enumera as coleções de um Edital
publicado de verdade — mas só no nível raiz, e é um nível acima de onde o problema mora. A
travessia recursiva do mesmo snapshot é a fonte da enumeração; um módulo novo de domínio carrega a
classificação; e `interface/retificacao.py` passa a ler o contrato em vez de manter listas próprias.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2, Django REST Framework. Nenhuma dependência nova.

**Storage**: PostgreSQL. **Nenhuma migration**: o contrato é código, revisto em revisão de código
e versionado com ele (R-001).

**Testing**: pytest, contra PostgreSQL (`make test-pg`). O guardião é teste de contrato
(`tests/contract/`); os canários são de integração e de interface.

**Target Platform**: monólito Django servindo a interface administrativa e o portal do candidato.

**Project Type**: web application — `backend/` único, com apps por contexto de domínio.

**Performance Goals**: o guardião publica **um** Edital completo e o percorre em memória; custo
comparável ao teste de coleções-raiz que já existe. Nenhuma consulta por campo.

**Constraints**: nenhuma alteração de conteúdo já publicado; nenhuma reclassificação retroativa
(FR-314); a razão de exclusão não pode repetir-se por entidade na tela (R-006).

**Scale/Scope**: 81 a 98 campos publicados por Edital, em 12 coleções normativas — 6 na raiz e 6
aninhadas. Quatro jornadas de correção.

## Constitution Check

*GATE: passou antes da Fase 0 e foi reavaliado depois da Fase 1.*

| Princípio | Situação | Como esta feature o satisfaz |
|---|---|---|
| **I — Linguagem ubíqua** | ✅ | "Natureza de mutabilidade", "campo publicado", "razão" entram no vocabulário com significado único em spec, código e teste. Nada renomeia conceito existente. |
| **II — Integridade normativa e temporalidade** | ✅ | Nada se sobrescreve. FR-314 proíbe reclassificação retroativa; R-005 confirma que a relação de sorteio congelada carrega o `metodo_hash` e não relê o método vigente. |
| **III — Segurança e auditoria** | ✅ | Nenhum dado pessoal envolvido. As Retificações dos canários seguem o fluxo de atos existente, com autoria e trilha. |
| **IV — Regras explícitas** | ✅ | É o núcleo da feature: D-008 proíbe classificação por heurística, e D-002 proíbe razão técnica. |
| **V — Qualidade e rastreabilidade** | ✅ | O guardião é a rastreabilidade: um campo sem decisão derruba a suíte nomeando-o. |
| **VI — Completude de jornada** | ⚠️ **resolvido por D-009** | Uma feature só de matriz e guardião é trabalho exclusivamente técnico — admissível, mas **inconcluível** como spec. Os quatro canários deixaram de ser insumo de desenho e passaram a ser as jornadas, e o gate de conclusão exige as quatro pelo canal do ator, sem API e sem banco. |

**Gate**: passa. A única tensão — princípio VI contra o escopo "o contrato, não a interface" da
decisão registrada — está resolvida por D-009 e declarada na spec, não silenciada.

**Reavaliação pós-Fase 1**: sem violação nova. O contrato é leitura; a única escrita que a feature
introduz é a Retificação dos canários, que passa pelos atos existentes.

## Project Structure

### Documentation (this feature)

```text
specs/026-contrato-de-mutabilidade-normativa/
├── plan.md              # este arquivo
├── research.md          # Fase 0 — seis perguntas, duas mudam escopo
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   └── mutabilidade.md  # Fase 1 — a forma do contrato e o que ele obriga
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — $speckit-tasks, não criado aqui
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   ├── validation.py          # forma publicada (existe) — não muda
│   └── mutabilidade.py        # NOVO: natureza e razão de cada campo publicado
├── interface/
│   ├── retificacao.py         # passa a LER o contrato em vez de manter CAMPOS_* como fonte
│   └── templates/interface/
│       ├── retificar.html     # o bloco declara o que não alcança (FR-312)
│       └── _retificacao_*.html
└── sorteios/                  # nada muda: metodo_hash já garante FR-309 (R-005)

backend/tests/
├── contract/
│   ├── test_forma_publicada.py        # a travessia passa a ser recursiva
│   └── test_mutabilidade.py           # NOVO: o guardião que falha por omissão
├── integration/editais/               # canários 1 a 4, pelo domínio
└── interface/
    └── test_retificar_*.py            # canários pela tela, e FR-312
```

**Structure Decision**: monólito existente, sem app novo. O contrato entra em `editais/domain/`
porque a natureza de mutabilidade é norma sobre o conteúdo do Edital, e é de lá que tanto o
guardião quanto a interface conseguem lê-la sem inverter dependência (R-001). Nenhuma
infraestrutura nova.

## Fases de execução

A ordem sai da spec (§8) e da pesquisa. Cada fase é verificável sozinha.

| # | Fase | Entrega | Depende de |
|---|---|---|---|
| **A** | Enumerar | Travessia recursiva do snapshot: as 12 coleções, com seus campos | — |
| **B** | Classificar | `mutabilidade.py` com natureza e razão de cada campo, nominalmente | A |
| **C** | Guardar | O guardião que falha por omissão nos dois sentidos | A, B |
| **D** | Reexaminar | As exclusões de razão técnica, reclassificadas ou rejustificadas | B |
| **E** | Canário 1 | Local do evento retificável pela tela | B |
| **F** | Canário 2 | Requisitos de participação retificáveis | B, E |
| **G** | Canário 3 | Janela recursal retificável | B, F |
| **H** | Canário 4 | Método do sorteio retificável | B, G |
| **I** | Declarar | A tela diz o que não alcança, uma vez por bloco de coleção | B |

A fase D é onde a feature pode crescer: se o reexame concluir que `operation`, `normalization`,
`rounding/*`, `appealWindow/unit`, `whenMissing` e `reserveType` são retificáveis — e a pesquisa
indica que a razão técnica que os excluía caiu —, a implementação deles é backlog derivado, e não
escopo desta spec. O que esta spec entrega é a decisão escrita.

## Complexity Tracking

> Preenchido porque a pesquisa encontrou **um requisito da spec que precisa ser corrigido antes de
> `$speckit-tasks`**.

| Item | O que a spec diz | O que a pesquisa encontrou | Recomendação |
|---|---|---|---|
| **FR-300** | "A forma publicada MUST estar declarada para toda coleção normativa … incluindo modalidade, marco, critério de desempate, fato declarado, linha do quadro e a raiz do Edital." | Mistura duas coisas: **enumerar** os campos (de que o contrato precisa, e que a travessia resolve) e **declarar a forma** deles em `validation.py` (que é outra feature, com razão escrita para não ter sido feita — 015, T-009). | Reescrever FR-300 como "toda coleção normativa MUST estar enumerada pelo contrato de mutabilidade". A declaração de forma das coleções aninhadas fica registrada como limite. |
| **Prioridade do canário 4** | US4 em P2, por presumir custo de domínio. | `RelacaoDeHabilitados.metodo_hash` já garante FR-309 estruturalmente (R-005). O canário custa campos na tela e um teste de fronteira. | Reavaliar para P1 em `$speckit-tasks`, ou manter P2 pelo número de campos (dez) e não pelo risco. |

Nenhuma outra violação. Nenhuma dependência nova, nenhum app novo, nenhuma migration.
