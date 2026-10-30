# Tasks: Identidade institucional preparada

**Input**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/adaptador-e-configuracao.md)

**Tests**: obrigatórios — o pedido enumera doze, e cada um está na
[matriz](rastreabilidade.md).

## Phase 1: Incremento A — arquitetura e compatibilidade

- [x] T001 Diagnóstico Django Auth × identidade própria em `doc/diagnostico-autenticacao-da-gestao-2026-10-30.md`
- [x] T002 ADR em `doc/decisao-identidade-e-autorizacao-da-gestao.md`
- [x] T003 Spec, plano, pesquisa, modelo de dados e contrato do adaptador nesta pasta

## Phase 2: Incremento B — núcleo de identidade e autorização (US2, US3)

- [x] T004 [US2] Modelos `IdentidadeExterna`, `Vinculo`, `RevogacaoDeVinculo` em `backend/processo_seletivo/seguranca/models.py`
- [x] T005 [US2] Migration `seguranca/0001_initial` com os três gatilhos append-only e os dois da `auth_user`
- [x] T006 [US2] As três tabelas em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py`); `seguranca` nas listas de `tests/migrations/test_migrations.py`
- [x] T007 [US3] Catálogo de acesso e escopo institucional em `seguranca/acessos.py`; a sincronização recusa o código reservado
- [x] T008 [US3] `conceder`, `revogar`, `vinculos_vigentes_da_unidade` em `seguranca/application/acessos.py`
- [x] T009 [US2] `BackendInstitucional` e `IdentidadeAutenticada` em `seguranca/autenticacao.py`; `AUTHENTICATION_BACKENDS` em `base.py`
- [x] T010 [US2] Origem institucional em `interface/identidade.py`: `ator_da_sessao`, `encerrar`, `contexto_identidade`, `metodos_disponiveis`; entrada, troca de unidade e saída com trilha
- [x] T011 [P] [US2] [US3] Testes do núcleo em `backend/tests/seguranca/test_vinculos.py` e `test_ator_institucional.py`

## Phase 3: Incremento C — adaptador simulado (US2)

- [x] T012 [US2] Provedor simulado em `backend/tests/fixtures/provedor_simulado.py`
- [x] T013 [US2] Rotas de entrada, retorno e unidade ativa em `interface/views.py` e `urls.py`; o botão em `identificar.html` só com provedor
- [x] T014 [US2] Testes de tela em `backend/tests/seguranca/test_entrada_institucional.py`: entrada, cabeçalho forjado, estado, fluxo da gestão, revogação, segregação, comissão

## Phase 4: Incremento D — preparação da ativação (US1, US4)

- [x] T015 [US4] `seletor_disponivel()` recusa sob `AMBIENTE_DE_PRODUCAO`
- [x] T016 [US4] Recusas de `production.py`: provedor de teste, não importável, *backend* além do institucional
- [x] T017 [US4] Comando `conceder_administracao_institucional`
- [x] T018 [P] [US1] [US4] Testes em `backend/tests/seguranca/test_ativacao.py`, `test_homologacao_preservada.py` e `tests/test_configuracao_producao.py`
- [x] T019 [US1] `doc/homologacao-com-o-seletor-de-demonstracao.md`
- [x] T020 [US4] `doc/ativacao-do-sso-institucional.md`

## Phase 5: Verificação

- [x] T021 Matriz de rastreabilidade e relatório de regressões em `verificacao.md`
- [x] T022 `cd backend && make lint check test-pg`; contagem `N de M` do `provisionar_papeis`
- [x] T023 CLAUDE.md: o `M` passa a 44

## Dependências

T004–T006 antes de T008–T010; T009–T010 antes de T012–T014; T015–T017 independentes do C.
