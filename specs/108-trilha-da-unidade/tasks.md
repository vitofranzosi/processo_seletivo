---

description: "Tarefas da 108 — Trilha da unidade"
---

# Tasks: Trilha da unidade

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/trilha-da-unidade.md](contracts/trilha-da-unidade.md)

**Tests**: pedidos. O repositório cobra rastreabilidade por teste, e os critérios SC-1021 a SC-1024
só se verificam por teste. Caminhos relativos a `backend/`, salvo os de `specs/` e `doc/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec

---

## Phase 1: Setup

- [x] T001 Conferir que a worktree está na `origin/main` (`ca1e53ed`) e que `migrate --check` não acusa nada no banco de teste da worktree (`DB_NAME` próprio)

---

## Phase 2: Foundational (bloqueia todas as histórias)

- [x] T002 Extrair a paginação por cursor de `consultar` para uma função comum, sem mudar o comportamento de `consultar`, em `processo_seletivo/auditoria/selectors.py` (D-007)
- [x] T003 Escrever `ASSUNTOS_DA_UNIDADE` e `trilha_da_unidade(*, actor, assunto, cursor, limit)` com o critério do data-model — escopo do ator, tipos do assunto, e a condição institucional do vínculo da unidade —, em `processo_seletivo/auditoria/selectors.py` (D-002, D-003, D-007; FR-3154, FR-3157, FR-3158, FR-3159)

**Checkpoint**: o seletor responde a consulta de qualquer história.

---

## Phase 3: User Story 1 — O Auditor lê os atos administrativos (P1) 🎯 MVP

**Goal**: a página lista, do mais recente para o mais antigo, os atos de unidade, autoridade, modelo
e aviso, com autor, situação e motivo.

**Independent Test**: com autoridade cadastrada e encerrada, modelos iniciais e aviso confirmado e
interrompido, o Auditor lê os atos sem terminal.

### Tests

- [x] T004 [P] [US1] Casos de leitura — cadastro e encerramento de autoridade, registro e alteração da unidade (dados mudados), modelos iniciais pela "Implantação", modelo editado sem assunto nem corpo, aviso confirmado e interrompido com o Edital, exclusão do piloto com as contagens — em `tests/interface/test_trilha_da_unidade.py` (FR-3160, FR-3161, FR-3162, FR-3163, FR-3164)
- [x] T005 [P] [US1] Casos de paginação — vinte e uma linhas, "Ver atos anteriores", nenhuma repetida nem pulada, empate de instante — e de consultas constantes (uma linha contra vinte, cinco assuntos) em `tests/interface/test_trilha_da_unidade.py` (FR-3166, FR-3168, SC-1023)
- [x] T006 [P] [US1] Guardião dos rótulos: toda operação dos assuntos incluídos tem rótulo, e toda situação gravada tem tradução, em `tests/interface/test_trilha_da_unidade.py` (FR-3165)

### Implementation

- [x] T007 [US1] A view `trilha_da_unidade`, a montagem das linhas (sobre o quê, dados mudados, situação, motivo) e o enriquecimento de avisos e interrupções por uma consulta por tipo, em `processo_seletivo/interface/trilha_da_unidade.py` (D-005, D-006)
- [x] T008 [US1] A rota `trilha-da-unidade` em `processo_seletivo/interface/urls.py`
- [x] T009 [US1] O template `processo_seletivo/interface/templates/interface/trilha_da_unidade.html`, com o caminho de navegação, a lista `ol.auditoria`, a paginação e o estado vazio (contrato)
- [x] T010 [P] [US1] A folha `processo_seletivo/interface/static/interface/telas/trilha-da-unidade.css`, com regra para cada classe nova (FR-3170)

**Checkpoint**: o Auditor do seletor lê a trilha da unidade.

---

## Phase 4: User Story 2 — Só a unidade de quem lê (P1)

**Goal**: 403 explicado sem a permissão; nada de outra unidade, de escopo vazio ou da trilha do
certame.

**Independent Test**: com atos no `cefor` e na `campus-a`, o Auditor do `cefor` vê só os dele, com
qualquer parâmetro; o Elaborador recebe a recusa.

- [x] T011 [P] [US2] Casos de recusa (cada papel sem `auditoria:consultar`; o escopo institucional) e de método (POST 405), e o caso de que abrir a página não grava registro de trilha nem de idempotência, em `tests/interface/test_trilha_da_unidade.py` (FR-3152, FR-3153, FR-3169)
- [x] T012 [P] [US2] Casos de vazamento — atos da `campus-a` com e sem parâmetros que a nomeiem, credencial de candidato, publicação de Edital, cursor adulterado — em `tests/interface/test_trilha_da_unidade.py` (FR-3154, FR-3159, SC-1022)
- [x] T013 [US2] A conferência de permissão e de escopo, com a recusa explicada da `033`, em `processo_seletivo/interface/trilha_da_unidade.py` (D-001, D-003)

---

## Phase 5: User Story 3 — Quem deu e quem tirou acesso (P2)

**Goal**: concessões e revogações da unidade, inclusive a do Administrador de acessos gravada no
institucional, com o nome das pessoas e o papel.

**Independent Test**: concessão de Elaborador e do Administrador de acessos do `cefor`, lidas pelo
Auditor do `cefor`; a da `campus-a` não aparece; suspensão e sessão não aparecem.

- [x] T014 [P] [US3] Casos de acesso, com pessoas institucionais e as funções da `106` — concessão e revogação no `cefor`, concessão institucional do Administrador de acessos do `cefor` e da `campus-a`, suspensão, entrada de sessão; nomes sem `pessoa-<uuid>` — em `tests/seguranca/test_trilha_da_unidade_acessos.py` (FR-3158, FR-3161, SC-1024)
- [x] T015 [US3] O "sobre o quê" do vínculo — a pessoa pelo nome e o papel pelo catálogo — em `processo_seletivo/interface/trilha_da_unidade.py` e no template (FR-3162)

---

## Phase 6: User Story 4 — Filtrar por assunto (P2)

**Goal**: o filtro por assunto, preservado na paginação; valor desconhecido vale como todos.

- [x] T016 [P] [US4] Casos de filtro — cada assunto, "Todos", filtro preservado no cursor, filtro sem atos, valor desconhecido — em `tests/interface/test_trilha_da_unidade.py` (FR-3167)
- [x] T017 [US4] O formulário do filtro no template, o `assunto` na página seguinte e o "Limpar", em `processo_seletivo/interface/templates/interface/trilha_da_unidade.html` e `processo_seletivo/interface/trilha_da_unidade.py` (D-009)

---

## Phase 7: User Story 5 — Demonstrável pelo seletor (P3)

**Goal**: o item na barra para quem tem `auditoria:consultar`, inclusive o Auditor do seletor.

- [x] T018 [US5] O item "Trilha da unidade" em `SECOES`, no grupo da unidade, com `pode_ver_trilha_da_unidade`, em `processo_seletivo/interface/navegacao.py`, e o símbolo `i-trilha` no sprite de `processo_seletivo/interface/templates/interface/base.html` (FR-3155, FR-3156)
- [x] T019 [US5] O teste do ícone de `tests/interface/test_shell_da_gestao.py` passa a identificar o Gestor **e** o Auditor, para continuar cobrindo todos os itens; o teste "itens = destinos que abrem" cobre o novo sem mudança
- [x] T020 [US5] O módulo novo em `MODULOS_DE_VIEW` de `tests/test_gramatica_das_portas.py` (D-008)

---

## Phase 8: Polish & Cross-Cutting

- [x] T021 [P] O guia de implantação aponta a página, em `doc/implantacao-em-producao-ubuntu.md`, §20.3 (FR-3171)
- [x] T022 [P] O quickstart com o roteiro pelo navegador, em `specs/108-trilha-da-unidade/quickstart.md`
- [x] T023 `make lint check test-pg` com `DB_NAME` exclusivo, e a verificação em `specs/108-trilha-da-unidade/verificacao.md` (SC-1026)
- [x] T024 A demonstração pelo seletor no navegador, num banco com `make preparar` e `seed_demo`, com capturas (SC-1025)

---

## Dependencies & Execution Order

- Phase 2 (T002, T003) bloqueia todas as histórias.
- US1 (T004–T010) antes de US2–US4, que estendem a mesma view e o mesmo template.
- US5 depende só da rota (T008).
- Os testes de cada história são escritos antes da implementação dela e falham primeiro.

### Parallel Opportunities

- T004, T005, T006 e T010 tocam arquivos ou casos independentes.
- T021 e T022 podem correr junto da Phase 7.

## Implementation Strategy

MVP: Phase 2 e US1 — o Auditor lê os atos da unidade. Depois, US2 (o escopo, que é a garantia), US3
e US4, e por último a barra (US5), que torna a página demonstrável.
