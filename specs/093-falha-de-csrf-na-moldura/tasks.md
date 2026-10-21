# Tasks: A recusa da verificação anti-falsificação na moldura do sistema

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade é verificada por teste, e cada requisito tem linha em
[rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`.

## Phase 1: Setup

- [x] T001 Conferir a faixa na `main` (`745f115f`): maior FR, FR-2145; maior SC, SC-826 — SC-820 a SC-826 já são da `092`, e esta usa SC-827 a SC-829; banco de teste `DB_NAME=ps_093`
- [x] T002 Ler o que o framework faz e o que os testes da verificação esperam (`tests/interface/test_csrf.py`): eles provam só o status e o efeito, e nenhum muda (R-001)

## Phase 2: User Stories 1 e 2 — a recusa na moldura das duas áreas (P1)

**Goal**: o candidato e o servidor veem a recusa com o desenho da área, o que aconteceu e o que fazer.

**Independent Test**: enviar sem a prova, na gestão e no portal, e ler status, moldura, texto e cabeçalho.

- [x] T003 [US1] [US2] `interface/erros.py`: `falha_de_csrf(request, reason="")`, a moldura por `path_info` (FR-2150, FR-2151, FR-2152, FR-2153, D-001, D-002, D-004)
- [x] T004 [US1] [US2] `_tela_de_origem`, tirada da recusa do envio grande e usada pelas duas (FR-2156, D-005)
- [x] T005 [US1] `portal/recusa.html`: a ajuda e o link de reabrir, opcionais (FR-2153, FR-2156)
- [x] T006 [US1] [US2] `config/settings/base.py`: `CSRF_FAILURE_VIEW` (FR-2158, FR-2160)
- [x] T007 [US1] [US2] `tests/interface/test_falha_de_csrf.py`: moldura, texto, política, link, depuração, fora das duas áreas, o "Sair" da página de recusa (FR-2150 a FR-2160)

## Phase 3: User Story 3 — o motivo no registro (P2)

- [x] T008 [US3] O motivo e o caminho no logger do projeto; a página sem termo técnico; medir para onde vai a linha do framework (FR-2154, FR-2155, R-003)

## Phase 4: Polish

- [x] T009 Prova no navegador: as duas áreas a 1280 e a 375 px, console sem violação (SC-827, R-005)
- [x] T010 `make lint check test-pg DB_NAME=ps_093` (SC-829)
- [x] T011 Registrar o que ficou de fora: o envio por fragmento (R-004) e o `path` da recusa do domínio
