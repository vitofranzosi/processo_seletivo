# Tasks: A tela do sorteio como a jornada de quem o conduz (142)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/tela-do-sorteio.md](contracts/tela-do-sorteio.md)

Os testes fazem parte do pedido (os dez cenários da validação) e entram em cada história.

## Phase 1: Setup

- [ ] T001 Branch sobre `origin/main` em `daba322f`; `.specify/feature.json` apontando para `specs/142-jornada-do-sorteio`; `backend/.env` com `DB_NAME=ps142`; a linha da `142` na tabela de incrementos do `README.md`; a entrada `jornada-do-sorteio-142` acrescentada ao `.claude/launch.json`
- [ ] T002 Banco descartável `ps142_dev` com C06 e C07 da `134` e a cópia `ps142_base`; as capturas do antes por `specs/142-jornada-do-sorteio/capturas/capturar.py antes`

## Phase 2: Foundational

- [ ] T003 A âncora da execução: `ancora_do_sorteio` e `"sorteio-"` em `_SECAO_DAS_ANCORAS`, e a célula do sorteio com ela, em `backend/processo_seletivo/interface/andamento.py`; o filtro `ancora_do_sorteio` em `backend/processo_seletivo/interface/templatetags/interface_extras.py`
- [ ] T004 O módulo de apresentação `backend/processo_seletivo/interface/jornada_do_sorteio.py`: `Passo`, `da_tela`, `URGENCIA`, `ordem_gravada`, os textos do passo 4
- [ ] T005 [P] Os testes puros de `jornada_do_sorteio` em `backend/tests/unit/interface/test_jornada_do_sorteio.py` e os da âncora em `backend/tests/unit/interface/test_chegada_ao_ato.py`
- [ ] T006 A view `sorteio` lê o andamento do Perfil uma vez e entrega `jornada` e a ordem gravada de cada recorte; `_proximo_nesta_lista` aceita `atual`, em `backend/processo_seletivo/interface/views.py`

## Phase 3: User Story 1 — a sequência e a tarefa de agora (P1) 🎯 MVP

**Independent Test**: C06 recém-carregado: quatro passos, o primeiro marcado "Agora", fixar antes de observar.

- [ ] T007 [US1] A navegação dos passos e as quatro seções, na ordem, em `backend/processo_seletivo/interface/templates/interface/sorteio.html`
- [ ] T008 [US1] As regras dos passos, da marca "Agora" e das situações em `backend/processo_seletivo/interface/static/interface/telas/sorteio.css`; `andamento.css` carregada pela tela
- [ ] T009 [US1] O botão de observar como ação secundária enquanto o passo 1 tem lista a praticar (D-004), em `sorteio.html`
- [ ] T010 [US1] Os cenários 1, 3 e 4 em `backend/tests/interface/test_jornada_do_sorteio.py`

## Phase 4: User Story 2 — fixar sabendo o que se fixa (P1)

- [ ] T011 [US2] O cartão da lista: a conferência antes do botão, o registro depois, a tabela recolhida depois de fixada, o diagnóstico da `102` e a sucessão, em `sorteio.html`
- [ ] T012 [US2] Os cenários 2 e 9 (lista sem inscrição) em `backend/tests/interface/test_jornada_do_sorteio.py`

## Phase 5: User Story 3 — várias listas, uma semente (P1)

- [ ] T013 [US3] O passo 2 do marco (ocorrência, observar, descartadas, recusas, o método recolhido) e o passo 3 por lista (sortear, razão, anular), em `sorteio.html`
- [ ] T014 [US3] Os cenários 5, 6 e 8 e a coerência com o Centro (SC-1541) em `backend/tests/interface/test_jornada_do_sorteio.py`

## Phase 6: User Story 4 — o resultado sem confundir com a divulgação (P2)

- [ ] T015 [US4] O passo 4: o que é cada coisa, a ordem gravada por lista (aberta na que acabou de ser sorteada), a divulgação pela célula do resultado, verificar, publicar, o corte só com sorteio, em `sorteio.html`
- [ ] T016 [US4] O cenário 7 e os SC-1543, SC-1544 e SC-1546 em `backend/tests/interface/test_jornada_do_sorteio.py`

## Phase 7: User Story 5 — quem não conduz (P3)

- [ ] T017 [US5] O cenário 10 (Auditor) em `backend/tests/interface/test_jornada_do_sorteio.py`

## Phase 8: Polish

- [ ] T018 Os testes que liam a prosa antiga passam a ler o controle: `backend/tests/interface/test_tela_do_sorteio.py` e os que a suíte acusar
- [ ] T019 Os formulários de ato iguais antes e depois em cada estado (SC-1542), medidos pelo roteiro das capturas
- [ ] T020 `cd backend && make lint check test-pg` com `DB_NAME=ps142`
- [ ] T021 As capturas do depois, a medição a 375 px e da CSP, e `specs/142-jornada-do-sorteio/verificacao.md` com antes e depois
- [ ] T022 `specs/142-jornada-do-sorteio/rastreabilidade.md`, requisito a requisito
- [ ] T023 O PR contra a `main`, com spec, implementação e verificação, sem merge

## Dependencies

T003 e T004 antes de T006; T006 antes das histórias; as histórias 1 a 4 mexem no mesmo template e
seguem em ordem; T018 a T023 no fim. Paralelo só T005 com T006.

## Implementation Strategy

MVP é a história 1 com o passo 1 (US2): a sequência e o ato que mais se faz. As outras completam a
mesma tela, e o PR leva todas.
