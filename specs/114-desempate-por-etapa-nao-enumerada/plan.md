# Implementation Plan: Desempate pela nota de Etapa que o marco não enumera

**Branch**: `claude/114-desempate-por-etapa-nao-enumerada` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/114-desempate-por-etapa-nao-enumerada/spec.md`

## Summary

O cálculo oficial passa a ler, na mesma consulta das Etapas enumeradas, os Resultados vigentes das
Etapas citadas por critério "maior pontuação numa Etapa" do marco. A preparação do universo separa o
que cada Resultado contribui: de toda Etapa lida vem a pontuação; da Etapa enumerada vem também a
consequência. Os Resultados lidos entram no universo gravado, a trigger de proveniência passa a aceitar
os das Etapas citadas pelo marco, e a reprodução do ato aplica a mesma separação. A prévia dá aos
candidatos fictícios uma nota na Etapa do desempate, derivada das notas enumeradas.

## Technical Context

**Language/Version**: Python 3.12, Django 5

**Primary Dependencies**: as do monólito; nenhuma nova

**Storage**: PostgreSQL. Uma migration nova em `classificacao` (`0007`) substitui a função da trigger
`check_ordering_act_provenance`; nenhuma tabela ou coluna muda

**Testing**: pytest contra PostgreSQL (`make test-pg`), com `DB_NAME` próprio da worktree

**Target Platform**: servidor Linux; o mesmo de sempre

**Project Type**: monólito web

**Performance Goals**: nenhuma consulta nova no cálculo. O filtro `etapa_id__in` ganha as Etapas
citadas; o orçamento de consultas verificado por teste não muda

**Constraints**: nenhum resultado oficial muda para marco sem critério por Etapa não enumerada
(FR-3557); as tabelas absolutas da `094` não são editadas

**Scale/Scope**: quatro módulos de `classificacao`, uma migration, testes de integração

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como se cumpre |
|---|---|
| I. Linguagem ubíqua | "Etapa do desempate" é termo da spec, usado igual em código e testes. |
| II. Integridade normativa | A regra continua sendo a publicada: o critério já citava a Etapa; o cálculo passa a obedecê-lo. Atos emitidos não são reescritos; ficam obsoletos e se sucedem com motivo (FR-3550). |
| III. Auditoria | O universo gravado passa a citar tudo o que decidiu a ordem; a proveniência do desempate grava a nota comparada. |
| IV. Regras no backend | A regra mora em `universo_classificavel.preparar`, a função pura que o oficial e a prévia chamam; a conferência da proveniência continua no banco. |
| V. Rastreabilidade e testes | Cada FR tem teste; o do A11 perde o `xfail`; a migration nova não reescreve a `0003`. |
| VI. Jornada | A jornada já existe — a tela do marco calcula e emite a ordem. O que muda é que ela passa a mostrar o desempate que o edital publica (quickstart). |

Sem violação. Nenhuma complexidade a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/114-desempate-por-etapa-nao-enumerada/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/universo-do-ato.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/classificacao/
├── application/calculo.py              # lê as Etapas citadas na mesma consulta
├── application/reproducao.py           # eliminação só das Etapas enumeradas
├── domain/universo_classificavel.py    # pontuação de toda Etapa lida; consequência só das enumeradas
├── domain/desempate.py                 # etapas_do_desempate(marco): uma derivação só
├── domain/cenarios_da_previa.py        # nota fictícia na Etapa do desempate
├── application/previa.py               # passa as Etapas do desempate aos cenários
└── migrations/0007_desempate_por_etapa_nao_enumerada.py

backend/tests/
├── integration/classificacao/test_desempate_por_etapa_nao_enumerada.py   # A11 sem xfail, e os novos
├── integration/classificacao/test_previa_equivale_ao_oficial.py          # caso novo na matriz
├── unit/classificacao/ (preparar e cenários)                              # casos puros
└── migrations/test_migrations.py                                         # contagem por app: 6 → 7
```

**Structure Decision**: tudo dentro de `classificacao`. Nenhuma tela muda: o seletor de alvos e a
validação continuam como estão (fora de escopo pela spec).

## Phase 0 e Phase 1

- [research.md](research.md) — R-001 a R-006.
- [data-model.md](data-model.md) — nenhuma entidade nova; o que muda no universo e na trigger.
- [contracts/universo-do-ato.md](contracts/universo-do-ato.md) — o formato do universo, que não muda, e a
  regra nova da conferência.
- [quickstart.md](quickstart.md) — os testes e o percurso pela tela do marco.

## Revisão de 02/11

O usuário pediu a revisão do PR preservando a capacidade genérica. O que entrou:

- `desempate.etapas_que_a_ordem_le` — a dependência efetiva da ordem, chamada pelo cálculo, pela
  Supervisão e pela pertinência dos recursos (`recursos/application/selectors.py`);
- a `0007` substitui também a função da `citacao_coerente` (`0004`), e a reversão restaura as duas;
- o caso "Desempate pela nota de outra Etapa" na prévia (`cenarios_da_previa`, `previa`,
  `interface/previa_da_classificacao.py`);
- testes: recursos e controle no arquivo da `114`; as três telas concordando sobre a obsolescência; o
  percurso do corte em `test_desempate_pela_etapa_que_o_corte_governa.py`; o caso novo na equivalência
  e em `tests/unit/classificacao/test_previa.py`.

Pesquisa em R-007 a R-009. Nenhum tratamento para atos anteriores: o sistema não está em produção
(D-003).

## Re-check pós-desenho

Sem mudança no quadro acima. O risco que o desenho introduz — a eliminação da Etapa do desempate vazar
para a ordem — é fechado em dois lugares (preparo e reprodução), e cada um tem teste próprio.
