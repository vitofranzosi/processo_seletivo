# Tasks: A ordem por pontuação sem nenhum resultado é recusada (128)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[contracts/telas.md](contracts/telas.md)

**Tests**: pedidos pela spec (SC-1300 a SC-1306); escritos antes da implementação de cada fase.

## Phase 1: Setup

- [ ] T001 Conferir `gh pr view 414 --json state,mergeable` e a base da branch (R-6)
- [ ] T002 Aceitar `pontuacoes=()` em `backend/tests/fixtures/corte.py::montar_cenario_do_corte` (sem distribuir nem consolidar), para o cenário sem nenhuma avaliação

## Phase 2: Foundational — a regra (D-004)

- [ ] T003 [P] Testes puros em `backend/tests/unit/classificacao/test_ordem_sem_resultado.py`: universo vazio, parcial, porta, eliminação, só desempate, a frase no singular, no plural e com várias Etapas (FR-4200 a FR-4202, FR-4211, UX-260)
- [ ] T004 `nenhuma_com_resultado` em `backend/processo_seletivo/classificacao/domain/universo_classificavel.py`
- [ ] T005 `impedimento` e `recusar` em `backend/processo_seletivo/classificacao/application/ordem_sem_resultado.py` (R-3)

## Phase 3: User Story 1 — o comando recusa (P1)

- [ ] T006 [US1] Testes em `backend/tests/integration/classificacao/test_ordem_sem_resultado.py`: recusa sem gravar nada; parcial; universo vazio; depois que o resultado chega; sucessão de uma ordem do acervo; Ocorrência basta; só desempate não basta; repetição devolve o desfecho; a ordem vazia do acervo continua vigente e *Feito* (FR-4200 a FR-4210, FR-4219, SC-1304)
- [ ] T007 [US1] A recusa em `emitir_ordem`, depois do cálculo e antes do vigente, em `backend/processo_seletivo/classificacao/application/emissao.py` (FR-4206, D-005)

## Phase 4: User Story 2 — a tela não oferece o que seria recusado (P1)

- [ ] T008 [US2] Testes em `backend/tests/interface/test_ordem_sem_resultado.py`: sem formulário, frase e links para quem gere; sem links nem pedido para quem não gere; sucessão do acervo sem bloco; a confirmação não abre; o formulário antigo é recusado sem repetir a frase; o parcial continua (FR-4212 a FR-4215)
- [ ] T009 [US2] O impedimento no contexto de `ordenacao` e o retorno de `emitir_ordenacao`, em `backend/processo_seletivo/interface/views.py`
- [ ] T010 [US2] O bloco no lugar do formulário em `backend/processo_seletivo/interface/templates/interface/ordenacao.html` (UX-261)
- [ ] T011 [US2] `conferencia_da_ordem.resumo` lê `nenhuma_com_resultado` em `backend/processo_seletivo/interface/conferencia_da_ordem.py`; ajustar `tests/interface/test_orientacao_p0.py` e `tests/unit/interface/test_conferencia_da_ordem.py` se preciso (FR-4217)

## Phase 5: User Story 3 — a conferência do gesto (P2)

- [ ] T012 [US3] Testes na mesma `tests/interface/test_ordem_sem_resultado.py`: recorte impedido com a frase; universo vazio continua a praticar; a confirmação do gesto recusa no comando (FR-4208, FR-4216, UX-262)
- [ ] T013 [US3] A recusa em `_alcance_da_ordem`, em `backend/processo_seletivo/interface/conducao_do_marco.py`

## Phase 6: Polish

- [ ] T014 Rodar a suíte e ajustar os testes e fixtures de conveniência (R-5, FR-4220)
- [ ] T015 Coerência com a `127`: leitura de `andamento.situacao_da_ordem`; teste se ela estiver na `main` (FR-4218, SC-1306)
- [ ] T016 `make lint check test-pg` com `DB_NAME` próprio; `migrate --check` sem migration nova (FR-4219, SC-1305)
- [ ] T017 Captura antes e depois da tela da ordem, em `capturas/` (quickstart)
- [ ] T018 `rastreabilidade.md`, `verificacao.md` e a linha da `128` no README
- [ ] T019 Revisão independente por subagente; corrigir os achados
- [ ] T020 PR, dizendo que depende do #414; conferir o CI

## Dependencies

- T002 antes de T006 e T008. T004–T005 antes de T007, T009, T011, T013.
- US1, US2 e US3 são independentes entre si depois da Phase 2; a tela (US2) é útil sem o comando, mas
  a regra só fecha com US1.
- T014 depois de T007 e T013: as falhas de conveniência só aparecem com a recusa ligada.
