# Tasks: A entrada da gestão

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/rotas.md](contracts/rotas.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`.

## Phase 1: Setup

- [x] T001 Banco `ps_redesign_acesso` com `seed_demo` e entrada `redesign-acesso` no `.claude/launch.json` apontando para `/gestao/identificar` (quickstart)

## Phase 2: Foundational — a fronteira de identidade

- [x] T002 `DESCRICOES`, `metodos_disponiveis()`, `destino_seguro()`, `pedir_identificacao()`, a origem em `identificar()` e a recusa em `ator_da_sessao()`, e `metodos_de_acesso` em `contexto_identidade()`, em `processo_seletivo/interface/identidade.py`
- [x] T003 [P] Testes da fronteira — descrição de todo papel, destino seguro, origem e recusa com o seletor desligado — em `tests/interface/test_entrada_da_gestao.py`
- [x] T004 Trocar as 90 chamadas `redirect(reverse("interface:identificar"))` por `identidade.pedir_identificacao(request)` em `processo_seletivo/interface/views.py`, `avisos.py`, `duvidas.py` e `assistente.py`

## Phase 3: User Story 1 — a página de acesso (P1) 🎯 MVP

**Goal**: quem gere chega pela "Área de gestão" a uma página que apresenta o produto e oferece a entrada.

**Independent Test**: com o seletor ligado, a vitrine traz os dois acessos e a página de acesso leva à escolha.

- [x] T005 [US1] `base_de_acesso.html` (duas colunas, sprite, selo) e `_estilo_do_acesso.html` em `processo_seletivo/interface/templates/interface/`
- [x] T006 [US1] `identificar.html` sobre a base nova: "Bem-vindo à gestão", o método de demonstração, o caminho do candidato, e "continuar como" quando já há identidade (FR-1697)
- [x] T007 [US1] View `identificar` (GET) e o repasse de `proximo` em `processo_seletivo/interface/views.py`
- [x] T008 [P] [US1] Testes da página de acesso em `tests/interface/test_entrada_da_gestao.py`

## Phase 4: User Story 2 — a escolha de identidade (P1)

**Goal**: identidades agrupadas e descritas, sem código de permissão; opções avançadas; busca acima de oito.

**Independent Test**: a escolha lista as identidades do banco e entrar por cada uma grava o que ela promete.

- [x] T009 [US2] `processo_seletivo/interface/demonstracao.py`: entradas de comissão e de responsabilidade com o nome da trilha
- [x] T010 [US2] `identificar_demonstracao.html`, com a busca, e a rota `identificar/demonstracao` em `processo_seletivo/interface/urls.py`
- [x] T011 [US2] View `identificar_demonstracao` e o POST de `identificar` — papéis filtrados, 422 na escolha sem nome — em `processo_seletivo/interface/views.py`
- [x] T012 [P] [US2] Testes da escolha em `tests/interface/test_entrada_da_gestao.py`; ajustar `tests/interface/test_caminho_ate_a_mesa.py` e `tests/interface/test_csrf.py` à página nova

## Phase 5: User Story 3 — o destino preservado (P2)

**Independent Test**: uma página protegida sem identidade leva ao acesso com o destino, e a identificação leva a ele.

- [x] T013 [US3] O POST de `identificar` segue `destino_seguro()` em `processo_seletivo/interface/views.py`
- [x] T014 [P] [US3] Testes do destino (interno, externo, laço, POST sem destino) em `tests/interface/test_entrada_da_gestao.py`; ajustar `tests/interface/test_lista.py`, `tests/authorization/test_mesa_por_post.py` e `tests/interface/test_duvidas.py`

## Phase 6: User Story 4 — sem método de entrada (P2)

**Independent Test**: com o seletor desligado, 503 com a mensagem, nada gravado, e a vitrine sem "Área de gestão".

- [x] T015 [US4] `sem_autenticacao.html` sobre a base nova, sem ação de entrar e sem a palavra que o guardião proíbe
- [x] T016 [US4] O cabeçalho do portal: "Minhas inscrições" no lugar de "Entrar" e "Área de gestão" com `metodos_de_acesso`, em `processo_seletivo/portal/templates/portal/base.html`
- [x] T017 [P] [US4] Testes em `tests/interface/test_entrada_da_gestao.py` e `tests/integration/portal/test_porta_de_entrada.py`

## Phase 7: User Story 5 — sair e trocar (P3)

- [x] T018 [US5] Testes de saída e de "continuar como" em `tests/interface/test_entrada_da_gestao.py`

## Phase 8: Polish

- [x] T019 O nome "Gestão de Processos Seletivos" (GPS no celular) nos cabeçalhos de `processo_seletivo/interface/templates/interface/base.html` e `processo_seletivo/portal/templates/portal/base.html` (FR-1700)
- [x] T020 Remover `processo_seletivo/interface/prototipo_do_acesso.py`, `templates/interface/prototipo_acesso/`, `tests/interface/test_prototipo_do_acesso.py` e as rotas (FR-1702)
- [x] T021 `rastreabilidade.md`, o estudo em `doc/` apontando para a 075, e o README/AGENTS se citarem a tela de identificação
- [x] T022 Navegador a 1280 e 375 px (quickstart) e `make lint check test-pg`

## Dependencies

- Phase 2 bloqueia todas as histórias. US1 e US2 compartilham a base (T005). US3 depende de T004 e T011.
  US4 depende de T005. US5 depende de T006.
- Paralelos: os testes ([P]) de cada fase, contra o arquivo de teste comum, depois da implementação da fase.

## Implementation Strategy

US1 + US2 são o MVP — a porta e a escolha. US3 e US4 fecham a segurança e o retorno; US5 e o polimento
fecham a feature. Tudo num PR só, porque as cinco histórias mexem nas mesmas três views.
