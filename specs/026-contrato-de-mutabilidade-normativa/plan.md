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

**Constraints**: nenhuma alteração de conteúdo já publicado; a classificação vigente governa os
atos futuros e não é congelada por Publicação (FR-314, D-011); a razão de exclusão não pode
repetir-se por entidade na tela (R-006).

**Scale/Scope**: **123 entradas de contrato** — a forma, que é a união de tudo o que pode aparecer,
medida em `publish_edital.py`. Os 81 a 98 da auditoria são ocorrências num Edital concreto, que é
outra conta. 12 coleções normativas — 6 na raiz e 6 aninhadas. Quatro jornadas de correção.

## Constitution Check

*GATE: passou antes da Fase 0 e foi reavaliado depois da Fase 1.*

| Princípio | Situação | Como esta feature o satisfaz |
|---|---|---|
| **I — Linguagem ubíqua** | ✅ | "Natureza de mutabilidade", "campo publicado", "razão" entram no vocabulário com significado único em spec, código e teste. Nada renomeia conceito existente. |
| **II — Integridade normativa e temporalidade** | ✅ | Nada se sobrescreve. FR-314, na redação de D-011, preserva o **conteúdo** publicado e deixa a classificação vigente governar os atos futuros; R-005 confirma que a relação de sorteio congelada carrega o `metodo_hash` e não relê o método vigente. |
| **III — Segurança e auditoria** | ✅ | Nenhum dado pessoal envolvido. As Retificações dos canários seguem o fluxo de atos existente, com autoria e trilha. |
| **IV — Regras explícitas** | ✅ | É o núcleo da feature: D-008 proíbe classificação por heurística, e D-002 proíbe razão técnica. A `matriz.md` é onde essas regras ficam explícitas antes de virarem código — e é ela que impede que a classificação seja decidida por quem implementa. |
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
├── matriz.md            # a classificação, campo a campo — APROVADA em 2026-09-13
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
├── editais/
│   ├── api/serializers.py     # a borda alinhada ao contrato: `requirements` é texto, sem quebra
│   │                          #   e sem branco (convergência)
│   └── domain/
│       ├── validation.py      # forma publicada (existe) — ganha `location`, e a coerência da
│       │                      #   janela, do método e dos requisitos (T036 + convergência)
│       └── mutabilidade.py    # NOVO: natureza e razão de cada campo publicado
├── publicacoes/domain/        # ACRESCENTADO NA CONVERGÊNCIA — o terceiro consumidor (FR-298)
│   ├── colecoes.py            # deriva do contrato o que o ato não alcança; era um literal
│   └── changes.py             # recusa com a razão do contrato; políticas de objeto ausente
├── interface/
│   ├── retificacao.py         # passa a LER o contrato em vez de manter CAMPOS_* como fonte;
│   │                          #   o objeto ausente se declara inteiro, num REPLACE só
│   └── templates/interface/
│       ├── retificar.html     # o bloco declara o que não alcança (FR-312)
│       └── _retificacao_*.html
└── sorteios/                  # nada muda: metodo_hash já garante FR-309 (R-005)

backend/tests/
├── contract/
│   ├── test_forma_publicada.py                 # a travessia passa a ser recursiva
│   ├── test_mutabilidade.py                    # NOVO: o guardião que falha por omissão
│   └── test_contrato_governa_a_retificacao.py  # NOVO na convergência: o contrato no ato
├── integration/editais/               # canários 1 a 4, pelo domínio
└── interface/
    └── test_retificar_*.py            # canários pela tela, e FR-312
```

**A árvore acima cresceu durante a execução**, e o acréscimo tem nome: `publicacoes/domain/` não
estava aqui porque o plano seguia FR-298 na redação que nomeava dois consumidores. A revisão do
PR #114 emendou o requisito e a árvore junto — ver `research.md` e `contracts/mutabilidade.md`.

**Structure Decision**: monólito existente, sem app novo. O contrato entra em `editais/domain/`
porque a natureza de mutabilidade é norma sobre o conteúdo do Edital, e é de lá que tanto o
guardião, a interface e a aplicação do ato conseguem lê-la sem inverter dependência (R-001).
Nenhuma infraestrutura nova.

## Fases de execução

A ordem sai da spec (§8) e da pesquisa. Cada fase é verificável sozinha.

| # | Fase | Entrega | Depende de |
|---|---|---|---|
| **A** | Enumerar | Travessia recursiva do snapshot, sem lista nomeada de coleções, e parando nos seis objetos opacos | — |
| **B** | Classificar | `mutabilidade.py` transcrevendo a `matriz.md` aprovada | A |
| **C** | Guardar | O guardião que falha por omissão nos dois sentidos | A, B |
| **D** | Reexaminar | As exclusões de razão técnica, reclassificadas ou rejustificadas | B |
| **E** | Canário 1 | Local do evento retificável pela tela | B |
| **F** | Canário 2 | Requisitos de participação retificáveis | B, E |
| **G** | Canário 3 | Janela recursal retificável | B, F |
| **H** | Canário 4 | Método do sorteio retificável | B, G |
| **I** | Declarar | A tela diz o que não alcança, uma vez por bloco de coleção | B |
| **J** | Fechar | Os campos **R** que nenhum canário alcança, até `AINDA_SEM_TELA` esvaziar | B, E–H |

**A fase D aconteceu em dois tempos.** O reexame das exclusões por razão técnica foi feito ao
montar a `matriz.md`, e a fase D do plano virou conferência (T018) em vez de investigação.
`whenMissing`, `reserveType`, `targetKind`, `governedStage` e `continuation` continuam **não
retificáveis**, com razão normativa escrita.

O segundo tempo foi a revisão do PR #114, ao ligar o contrato à API: **`operation` e
`normalization` voltaram a retificáveis**, junto com `maxInscricoesPorCandidato` e
`isRegistrationPeriod` — as quatro contradiziam decisões anteriores implementadas e testadas. Com
`rounding/scale`, `rounding/mode` e os demais, são **72 retificáveis e 23 não**.

**A fase J existe por consequência, e não por escolha.** Com a matriz aprovada, a FR-304 obriga
tela para os 72 campos **R**; a tela oferece 49 e os canários acrescentam 15. Chamar os quatro
restantes de "backlog derivado" era possível antes de a matriz existir — depois dela, não: não há
"resto" para campo **R**.

## Complexity Tracking

> Preenchido porque a pesquisa encontrou **um requisito da spec que precisava ser corrigido antes
> de `$speckit-tasks`**. Ele foi corrigido; a linha fica como registro do que mudou e por quê.

| Item | O que a spec diz | O que a pesquisa encontrou | Recomendação |
|---|---|---|---|
| **FR-300** ✅ **corrigida** | Dizia "a forma publicada MUST estar declarada para toda coleção normativa …". | Misturava **enumerar** os campos (de que o contrato precisa, e que a travessia resolve) com **declarar a forma** deles em `validation.py` — outra feature, com razão escrita para não ter sido feita (015, T-009). | Reescrita: "toda coleção normativa MUST estar enumerada pelo contrato de mutabilidade", e a enumeração não depende de forma declarada. Arrastou D-005, dois casos de fronteira, a premissa da fonte autoritativa e o passo 1 da ordem sugerida. |
| **Prioridade do canário 4** | US4 em P2, por presumir custo de domínio. | `RelacaoDeHabilitados.metodo_hash` já garante FR-309 estruturalmente (R-005). O canário custa campos na tela e um teste de fronteira. | Reavaliar para P1 em `$speckit-tasks`, ou manter P2 pelo número de campos (dez) e não pelo risco. |

Nenhuma outra violação. Nenhuma dependência nova, nenhum app novo, nenhuma migration.
