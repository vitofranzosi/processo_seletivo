# Tasks: O corte emitido depois do recurso não nasce obsoleto

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos pela spec — a `SC-440` e a `SC-441` são verificadas por teste. O teste de
reprodução foi escrito antes da correção e falhou contra a `main`.

**Caminhos**: relativos à raiz do repositório. `backend/` é o projeto Django.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US3)

---

## Phase 1: Setup

- [X] T001 Medir o estado de partida e guardar em `specs/061-corte-apos-recurso/verificacao.md`: o estado dos cortes do Edital 72/2026 no banco `ps_apresentacao_grafico`, e a comparação entre os sucessores acusados e os citados pelo ato

---

## Phase 2: Reprodução (bloqueia a correção)

- [X] T002 [US1] Em `backend/tests/integration/classificacao/test_corte_apos_recurso.py`: recurso deferido → ordem sucessora → corte; o corte não está obsoleto, e o ato lido cita o sucessor
- [X] T003 [US1] No mesmo arquivo: a Etapa governada não tem impedimento por corte obsoleto
- [X] T004 [US1] No mesmo arquivo: a geração sucessora emitida sobre o mesmo ato está em dia
- [X] T005 [US2] No mesmo arquivo: a publicabilidade do ato vigente não é impedida por corte obsoleto
- [X] T006 [US3] No mesmo arquivo: corte → recurso continua impedindo a publicação, com a causa *participante reingressou*
- [X] T007 Rodar o arquivo contra a `main`: T002 a T005 falham, T006 passa

---

## Phase 3: Correção

- [X] T008 Em `backend/processo_seletivo/classificacao/application/corte.py::_reingressou`: excluir da consulta os `id` do `stageResults` do ato (`D-001`), com o comentário do porquê e a docstring estendida
- [X] T009 [P] No arquivo de teste: a pergunta continua sendo uma consulta (`FR-1147`)
- [X] T010 Rodar o arquivo novo, `test_corte_obsoleto.py` sem edição e as pastas `tests/integration/classificacao/` e `tests/integration/divulgacao/`

---

## Phase 4: Registro e fechamento

- [X] T011 [P] Atualizar o estado de `doc/achado-corte-nasce-obsoleto-apos-recurso.md`
- [X] T012 [P] Registrar `doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md` (`D-002`)
- [X] T013 [P] Linha da `061` na tabela de incrementos do `README.md`
- [X] T014 Medir o depois no banco de demonstração e guardar em `verificacao.md`
- [X] T015 `cd backend && make lint check test-pg` com banco próprio; o total em `verificacao.md` e no `AGENTS.md`

---

## Dependencies & Execution Order

- Phase 2 antes da Phase 3: a reprodução tem de falhar contra a `main` antes da correção.
- T011 a T013 independem entre si.
- T015 por último, sem editar arquivo durante a suíte.
