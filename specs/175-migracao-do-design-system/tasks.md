# Tasks: A migração do design system para toda a gestão

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Estado em 15/11**: as tarefas T001 a T012 foram feitas na branch antes desta spec existir (ver o
status da spec), e as T013 a T015 são as correções da revisão de código. As T016 em diante são o que
falta, e dependem do usuário.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Medida (antes de mudar)

- [x] T001 Rastrear as 123 telas da `main` (entrada `piloto-antiga`, 8172) sobre `ps_piloto_validacao`, por `doc/auditoria-design-system-2026-11-14/migracao/scripts/rastrear_gestao.sh`

## Phase 2: User Story 1 — O texto na largura (P1)

- [x] T002 [US1] Tirar `max-width:var(--leitura)` de `backend/processo_seletivo/interface/static/interface/gestao/componentes.css` e de `gestao/telas.css`, e os 44rem de `.ajuda` e `.explicacao` (FR-7900)
- [x] T003 [P] [US1] Tirar as medidas de leitura das folhas de grupo e de tela em `backend/processo_seletivo/interface/static/interface/grupos/` e `telas/` (FR-7900)
- [x] T004 [US1] Tirar o teto de `--leitura` dos campos em `backend/processo_seletivo/interface/static/interface/gestao/formularios.css` (FR-7902)

## Phase 3: User Story 2 — Os mesmos componentes (P1)

- [x] T005 [US2] Indicador em grade de partes iguais em `gestao/componentes.css` (FR-7901)
- [x] T006 [US2] Aviso, cartão das consequências, botão e ação de altura única e respiro em `gestao/telas.css` (FR-7904)
- [x] T007 [US2] Lista de definição em "rótulo e valor" na linha, com o caso da lista agrupada em `div`, em `gestao/telas.css` (FR-7903)

## Phase 4: User Story 3 — Nada some e o portal não muda (P2)

- [x] T008 [US3] Reescrever os guardiões que prendiam as medidas antigas em `backend/tests/interface/test_larguras.py`, `test_polish_da_056.py` e `test_polish_da_058.py`, e registrar as duas classes sem desenho em `backend/tests/interface/conftest.py` (FR-7909)
- [x] T009 [US3] Rastrear a branch (entrada `migracao-ds`, 8175) e comparar com `doc/auditoria-design-system-2026-11-14/migracao/scripts/comparar_telas.py` (SC-2700, SC-2701, SC-2702)
- [x] T010 [US3] Corrigir a lista agrupada em `div` que rolava de lado a 768 px, e rastrear de novo
- [x] T011 [US3] Montar o antes e o depois com `doc/auditoria-design-system-2026-11-14/migracao/scripts/montar_html.py`
- [x] T012 Rodar `cd backend && make lint check test-pg` (SC-2703)

## Phase 5: Correções da revisão de código (15/11, aprovadas pelo usuário)

- [x] T013 [US2] Tirar os dois-pontos gerados (`dt::after`) de `gestao/telas.css` e a classe `rotulo-com-dois-pontos` de `backend/processo_seletivo/interface/templates/interface/_linhas_da_revisao.html` e do teste dela (FR-7903, UX-900, D-002)
- [x] T014 [US3] Tirar de `backend/processo_seletivo/interface/static/interface/grupos/piloto-ds.css` as regras que a folha comum já tem com os mesmos valores (FR-7908)
- [x] T015 [US3] Retirar `grupos/confirmacao-de-ato.css`, o `<link>` de `confirmar.html`, `processo_confirmar.html` e `retificacao_confirmar.html`, a entrada em `backend/tests/interface/test_folha_estatica.py` e o assert em `backend/tests/interface/test_confirmacao_do_encerramento.py` (FR-7907)

## Phase 6: User Story 4 — A validação (P3), e as pendências

- [ ] T016 [US4] **Humano**: a equipe faz as tarefas de `specs/172-piloto-do-design-system/validacao.md` nas duas versões (SC-2704, FR-7911)
- [ ] T017 Decidir as pendências P-1 a P-5 da spec, com o usuário
- [ ] T018 Desfazer `grupos/piloto-ds.css` para `telas/`, se o usuário decidir a P-4

## Dependencies

- As fases 1 a 5 estão feitas. A T016 e a T017 dependem do usuário; a T018, da T017.

## Rastreabilidade: requisito → tarefa

| Requisito | Tarefas |
|---|---|
| FR-7900 | T002, T003 |
| FR-7901 | T005 |
| FR-7902 | T004 |
| FR-7903 | T007, T013 |
| FR-7904 | T006 |
| FR-7905 | T009 |
| FR-7906 | T009, T011 |
| FR-7907 | T015 |
| FR-7908 | T014, T018 |
| FR-7909 | T008 |
| FR-7910 | T013, T014, T015 |
| FR-7911 | T016 |
| UX-900 | T013 |
| UX-901 | T009 |
| SC-2700, SC-2701, SC-2702 | T009, T010 |
| SC-2703 | T012 |
| SC-2704 | T016 |
