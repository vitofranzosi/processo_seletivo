# Implementation Plan: O corte emitido depois do recurso não nasce obsoleto

**Branch**: `claude/sweet-faraday-1be5f6` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/061-corte-apos-recurso/spec.md`

## Summary

`_reingressou`, em `classificacao/application/corte.py`, passa a excluir da pergunta os Resultados
sucessores que o ato de ordenação já cita no `stageResults` (`D-001`). É uma cláusula na consulta que
já existia. Os cinco consumidores da obsolescência leem `estado_do_corte` e herdam a correção sem
mudança própria. Testes novos cobrem a cronologia que faltava, a publicação nas duas cronologias e o
custo da pergunta; os da `014` ficam sem edição.

## Technical Context

**Language/Version**: Python 3.13 (Django, versão do `pyproject.toml`)

**Primary Dependencies**: as do monólito; nenhuma nova

**Storage**: PostgreSQL — só leitura, em `resultados_resultadoetapa` e no `universo` do ato; nenhuma
escrita nova, nenhuma migration

**Testing**: pytest + pytest-django contra PostgreSQL (`make test-pg`); `CaptureQueriesContext` para
o custo

**Target Platform**: servidor Linux

**Project Type**: monólito web (Django, server-rendered)

**Performance Goals**: a pergunta continua sendo uma consulta (`FR-1147`)

**Constraints**: a cronologia *corte → recurso* não pode mudar (`FR-1145`, `SC-441`)

**Scale/Scope**: 1 função alterada, 1 arquivo de teste novo com 7 casos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "reingresso", "ato de ordenação", "geração" com o sentido da `014` e da `015`; nenhum termo novo | ✅ |
| II. Imutabilidade | Nada escrito; o corte emitido não é alterado nem sucedido pela correção (`D-003`) | ✅ |
| III. Segurança e dados | Nenhuma rota, permissão ou dado exibido muda | ✅ |
| IV. Regras no domínio | A pergunta continua na aplicação da classificação; os consumidores não ganham regra (`FR-1143`) | ✅ |
| V. Rastreabilidade e simplicidade | Matriz em `rastreabilidade.md`; uma cláusula numa consulta existente | ✅ |
| VI. Completude de jornada | É o que o defeito violava: a Etapa governada travava, e o caminho oferecido não levava a lugar nenhum (`FR-1144`) | ✅ — é a razão da feature |

Nenhuma violação; *Complexity Tracking* fica vazio.

## Project Structure

### Documentation (this feature)

```text
specs/061-corte-apos-recurso/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # D-001 a D-005
├── quickstart.md
├── checklists/requirements.md
├── tasks.md
├── rastreabilidade.md    # matriz requisito → teste
└── verificacao.md        # antes e depois, no teste e no banco de demonstração
```

Sem `data-model.md` nem `contracts/`: nenhuma entidade, campo, tela ou contrato muda.

### Source Code (repository root)

```text
backend/processo_seletivo/classificacao/application/corte.py   # _reingressou
backend/tests/integration/classificacao/test_corte_apos_recurso.py
doc/achado-corte-nasce-obsoleto-apos-recurso.md                 # o achado, com o estado atualizado
doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md    # a pergunta que ficou fora (D-002)
README.md                                                       # linha da 061 na tabela de incrementos
```

**Structure Decision**: a correção mora onde a pergunta já morava. Nenhum módulo novo.

## Complexity Tracking

Vazio.
