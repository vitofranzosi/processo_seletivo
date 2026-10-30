# Tasks: Ações disponíveis

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[contracts/telas.md](contracts/telas.md). Caminhos relativos à raiz do repositório. Prioridades do
pedido: P0 consistência funcional, P1 descoberta, P2 clareza, P3 qualidade transversal.

## Phase 1: Setup

- [X] T001 Branch `claude/acoes-disponiveis-104` sobre a `103`; linha da `104` na tabela de incrementos do `README.md`
- [X] T002 Capturas "antes" (homologador, elaboradora, publicadora, gestor, 375 px) já feitas no diagnóstico; copiar para `specs/104-acoes-disponiveis/capturas/antes/`

## Phase 2: Foundational — leituras em lote (bloqueia US1 e US2)

- [X] T003 [P] `participantes_em_lote(editais)` em `backend/processo_seletivo/publicacoes/application/selectors.py`, mesma forma de `participantes_do_edital` (R-004)
- [X] T004 [P] `contagens_da_lista(editais)` e `recursos_por_edital(editais)` em `backend/processo_seletivo/interface/acoes.py`; `do_edital(..., contagens=)` lê as contagens quando vêm (R-003, FR-2818)
- [X] T005 `atos_retificacao.resumo` com `devolvida`, `reenviada`, `rotulo_situacao`, `desde`; `_CAMPOS_DO_RESUMO` com `return_reason`, `submitted_at`, `homologated_at` em `backend/processo_seletivo/interface/atos_retificacao.py` (R-008, FR-2821–FR-2823)

## Phase 3: US2 — a Lista não se contradiz (P0)

- [X] T006 [US2] `acoes.para_a_lista(conjunto, edital)`: "Conferir e submeter"/"Conferir e publicar" levando ao detalhe (R-005, FR-2815)
- [X] T007 [US2] `views.lista`: contagens em lote, segregação em lote passada a `do_edital`, `para_a_lista`, ato da Retificação ao lado do grupo (FR-2814, FR-2816, FR-2818)
- [X] T008 [US2] `lista.html`: ato da Retificação na coluna; "Nenhuma ação" só com as duas listas vazias; marca só com a situação da Retificação e quem aguarda (FR-2814, FR-2817)

## Phase 4: US1 — a faixa (P1)

- [X] T009 [US1] `backend/processo_seletivo/interface/trabalho.py`: `ObjetoDeTrabalho`, `do_ator(ator, editais)` com Edital, Retificação, recursos e avaliação, deduplicação e ordem (R-001, FR-2801–FR-2806)
- [X] T010 [P] [US1] Testes unitários da derivação em `backend/tests/unit/interface/test_trabalho_do_ator.py` (ordem, deduplicação, rótulos, segregação, devolvida)
- [X] T011 [US1] Parcial `_acoes_disponiveis.html` e chamada em `lista.html` depois dos avisos; regras em `telas/lista.css` (R-002, FR-2807–FR-2813)

## Phase 5: US3, US4, US5, US7 — clareza dos procedimentos (P2)

- [X] T012 [US3] "O que fazer agora" do detalhe do Edital com a Retificação que espera a pessoa (R-007, FR-2819, FR-2820)
- [X] T013 [US4] Devolvida e reenviada em `_retificacoes_em_curso.html`, `retificacao_detalhe.html` e na marca (FR-2821, FR-2822)
- [X] T014 [US5] `advertencias_do_vigente` em `publicacoes/application/retificacoes.py`; confirmação com a tabela em homologar e devolver e as advertências separadas (R-009, FR-2824–FR-2826)
- [X] T015 [US7] Estado vazio de `minhas_etapas.html` (R-010, FR-2827)

## Phase 6: Testes de jornada, escala e regressão (P3)

- [X] T016 Jornadas A (homologação, sumiço para todos), B (publicação), C (devolução até publicação), D (Edital com pendência e com segregação), E (múltiplos papéis, um item), F (sem ação), G (vários procedimentos: contagem, ordem, links, sem duplicidade), I (regressão: Visão Geral, Minhas Etapas, Agenda, permissões — FR-2828) em `backend/tests/interface/test_acoes_disponiveis.py` (SC-981–SC-983, SC-986, SC-987)
- [X] T017 [P] Escala da derivação e da Lista com 0, 3, 30 e 300 Editais em `backend/tests/performance/test_trabalho_em_escala.py` (SC-984, SC-985)
- [X] T018 Ajustar os testes existentes que leem o texto antigo da marca, sem enfraquecer o que eles provam
- [X] T019 H — acessibilidade e 375 px no navegador; capturas "depois" em `specs/104-acoes-disponiveis/capturas/depois/` (SC-989)

## Phase 7: Polish

- [X] T020 `rastreabilidade.md` (uma linha por FR e SC) e `verificacao.md` com os números e o roteiro de SC-990 pendente
- [X] T021 `cd backend && make lint check test-pg` e o recorte de Edital, Retificação e publicação (SC-988); conferir que nenhuma migration nem tabela nasceu (FR-2829)

## Dependencies

T003–T005 antes de US1 e US2. T009 depende de T003–T005. T016–T019 depois de todas as histórias.

## Implementation Strategy

P0 primeiro (US2: a coluna deixa de mentir), depois a faixa (US1), depois clareza (US3–US7), depois
testes de jornada e escala.

## Phase 8: Convergence

- [X] T022 Testar o Edital em revisão na faixa ("Homologar o Edital", some depois da homologação) em `backend/tests/interface/test_acoes_disponiveis.py` per FR-2804 (partial)
- [X] T023 Registrar em `specs/104-acoes-disponiveis/verificacao.md` o parcial `_item_de_trabalho.html` como parte da faixa per plan: estrutura (unrequested)

## Phase 9: Revisão de prontidão (30/10/2026)

Achados da avaliação independente do relatório de revisão, confirmados no código.

- [X] T024 O item inteiro como um link só, com o ato no nome acessível e o contexto como descrição, em `_item_de_trabalho.html` e `telas/lista.css` per FR-2809, D-011
- [X] T025 Estado vazio que diz o que a faixa cobre, em `_acoes_disponiveis.html` per FR-2808, D-012
- [X] T026 "Conferir e publicar o Edital" no item do Edital homologado, em `interface/trabalho.py` per D-004
- [X] T027 Um verbo para a devolvida na passagem de bastão, em `atos_retificacao.proximo_passo` per D-013
- [X] T028 Restaurar no teste da 103 a asserção da situação na marca para quem publica, em `tests/interface/test_jornada_da_retificacao.py`
- [X] T029 Faixa com 1, 5, 25 e 100 objetos: teste de consultas em `tests/performance/test_trabalho_em_escala.py` e medição no navegador em 1280 e 375 px; densidade do item per D-014
- [X] T030 Testes de afordância e de verbo em `tests/interface/test_acoes_disponiveis.py` e `tests/unit/interface/test_atos_da_retificacao.py`
