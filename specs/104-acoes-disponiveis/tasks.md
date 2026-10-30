# Tasks: Ações disponíveis

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[contracts/telas.md](contracts/telas.md). Caminhos relativos à raiz do repositório. Prioridades do
pedido: P0 consistência funcional, P1 descoberta, P2 clareza, P3 qualidade transversal.

## Phase 1: Setup

- [ ] T001 Branch `claude/acoes-disponiveis-104` sobre a `103`; linha da `104` na tabela de incrementos do `README.md`
- [ ] T002 Capturas "antes" (homologador, elaboradora, publicadora, gestor, 375 px) já feitas no diagnóstico; copiar para `specs/104-acoes-disponiveis/capturas/antes/`

## Phase 2: Foundational — leituras em lote (bloqueia US1 e US2)

- [ ] T003 [P] `participantes_em_lote(editais)` em `backend/processo_seletivo/publicacoes/application/selectors.py`, mesma forma de `participantes_do_edital` (R-004)
- [ ] T004 [P] `contagens_da_lista(editais)` e `recursos_por_edital(editais)` em `backend/processo_seletivo/interface/acoes.py`; `do_edital(..., contagens=)` lê as contagens quando vêm (R-003, FR-2818)
- [ ] T005 `atos_retificacao.resumo` com `devolvida`, `reenviada`, `rotulo_situacao`, `desde`; `_CAMPOS_DO_RESUMO` com `return_reason`, `submitted_at`, `homologated_at` em `backend/processo_seletivo/interface/atos_retificacao.py` (R-008, FR-2821–FR-2823)

## Phase 3: US2 — a Lista não se contradiz (P0)

- [ ] T006 [US2] `acoes.para_a_lista(conjunto, edital)`: "Conferir e submeter"/"Conferir e publicar" levando ao detalhe (R-005, FR-2815)
- [ ] T007 [US2] `views.lista`: contagens em lote, segregação em lote passada a `do_edital`, `para_a_lista`, ato da Retificação ao lado do grupo (FR-2814, FR-2816, FR-2818)
- [ ] T008 [US2] `lista.html`: ato da Retificação na coluna; "Nenhuma ação" só com as duas listas vazias; marca só com a situação da Retificação e quem aguarda (FR-2814, FR-2817)

## Phase 4: US1 — a faixa (P1)

- [ ] T009 [US1] `backend/processo_seletivo/interface/trabalho.py`: `ObjetoDeTrabalho`, `do_ator(ator, editais)` com Edital, Retificação, recursos e avaliação, deduplicação e ordem (R-001, FR-2801–FR-2806)
- [ ] T010 [P] [US1] Testes unitários da derivação em `backend/tests/unit/interface/test_trabalho_do_ator.py` (ordem, deduplicação, rótulos, segregação, devolvida)
- [ ] T011 [US1] Parcial `_acoes_disponiveis.html` e chamada em `lista.html` depois dos avisos; regras em `telas/lista.css` (R-002, FR-2807–FR-2813)

## Phase 5: US3, US4, US5, US7 — clareza dos procedimentos (P2)

- [ ] T012 [US3] "O que fazer agora" do detalhe do Edital com a Retificação que espera a pessoa (R-007, FR-2819, FR-2820)
- [ ] T013 [US4] Devolvida e reenviada em `_retificacoes_em_curso.html`, `retificacao_detalhe.html` e na marca (FR-2821, FR-2822)
- [ ] T014 [US5] `advertencias_do_vigente` em `publicacoes/application/retificacoes.py`; confirmação com a tabela em homologar e devolver e as advertências separadas (R-009, FR-2824–FR-2826)
- [ ] T015 [US7] Estado vazio de `minhas_etapas.html` (R-010, FR-2827)

## Phase 6: Testes de jornada, escala e regressão (P3)

- [ ] T016 Jornadas A (homologação, sumiço para todos), B (publicação), C (devolução até publicação), D (Edital com pendência e com segregação), E (múltiplos papéis, um item), F (sem ação), G (vários procedimentos: contagem, ordem, links, sem duplicidade), I (regressão: Visão Geral, Minhas Etapas, Agenda, permissões — FR-2828) em `backend/tests/interface/test_acoes_disponiveis.py` (SC-981–SC-983, SC-986, SC-987)
- [ ] T017 [P] Escala da derivação e da Lista com 0, 3, 30 e 300 Editais em `backend/tests/performance/test_trabalho_em_escala.py` (SC-984, SC-985)
- [ ] T018 Ajustar os testes existentes que leem o texto antigo da marca, sem enfraquecer o que eles provam
- [ ] T019 H — acessibilidade e 375 px no navegador; capturas "depois" em `specs/104-acoes-disponiveis/capturas/depois/` (SC-989)

## Phase 7: Polish

- [ ] T020 `rastreabilidade.md` (uma linha por FR e SC) e `verificacao.md` com os números e o roteiro de SC-990 pendente
- [ ] T021 `cd backend && make lint check test-pg` e o recorte de Edital, Retificação e publicação (SC-988); conferir que nenhuma migration nem tabela nasceu (FR-2829)

## Dependencies

T003–T005 antes de US1 e US2. T009 depende de T003–T005. T016–T019 depois de todas as histórias.

## Implementation Strategy

P0 primeiro (US2: a coluna deixa de mentir), depois a faixa (US1), depois clareza (US3–US7), depois
testes de jornada e escala.
