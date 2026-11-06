# Tasks: Andamento da seleção (127)

**Input**: `specs/127-andamento-da-selecao/` — spec (D-001 a D-016), plan, research (R-001 a R-013),
data-model, contracts/telas.md, quickstart.

**Tests**: pedidos pela spec (SC-1230, SC-1235 a SC-1239, SC-1243) e pelo pedido da feature.

Caminhos relativos à raiz do repositório. `[P]` = arquivo diferente, sem dependência pendente.

## Phase 1: Setup

- [x] T001 Banco de teste próprio da worktree (`DB_NAME=spec127`), `uv sync --extra dev`, `migrate --check`; linha de base de `make lint check` registrada em `specs/127-andamento-da-selecao/verificacao.md`
- [x] T002 Clonar `processo_seletivo_guia` como `ps_spec127` no container `ps-sorteio-35` e migrar; capturas **antes** dos Editais 35, 57, 51, 91, 72 e 90 por papel, a 1280 e a 375 px, com o roteiro `specs/127-andamento-da-selecao/capturas/capturar.py`, em `specs/127-andamento-da-selecao/capturas/antes/`

## Phase 2: Foundational (a derivação, para os dois incrementos)

- [x] T003 Nome público `quem_exige_o_resultado` em `backend/processo_seletivo/editais/domain/validation.py`, com o privado chamando o público (R-003)
- [x] T004 [P] Constantes, dataclasses (`Celula`, `Ponto`, `PerfilNoAndamento`, `Providencia`, `Atencao`, `Andamento`) e responsáveis em `backend/processo_seletivo/interface/andamento.py` (data-model)
- [x] T005 Expectativa das Etapas (enumerada, governada, habilitação, desempate, progressão por ponto fixo; sorteio só consolidável) em `backend/processo_seletivo/interface/andamento.py` (FR-4060, D-012)
- [x] T006 Regras puras das sete situações por ponto — Etapa, relação, semente, sorteio, ordem, corte, apuração, resultado, convocação — em `backend/processo_seletivo/interface/andamento.py` (FR-4052, FR-4062, FR-4065 a FR-4076)
- [x] T007 Composição da sequência do Perfil pela `jornada()`, com o reposicionamento de S3 (D-011) e os grupos de colunas, em `backend/processo_seletivo/interface/andamento.py` (FR-4103, FR-4104)
- [x] T008 Leitura dos fatos: `recortes_do_marco`, `indicador_do_marco`, panorama + resumo, `leitura_do_recorte` + prévias, `aferir` da definitiva, Perfil das inscrições, conferências pendentes, `trabalho.do_ator`; e `do_edital(edital, ator, agora=)` em `backend/processo_seletivo/interface/andamento.py` (R-004 a R-010)
- [x] T009 [P] Agrupamento (D-016) e ordem fixa do nível 1 (FR-4082, FR-4083), contagem e "nada em aberto" em `backend/processo_seletivo/interface/providencias.py`
- [x] T010 [P] Testes puros das sete situações em cada família, inclusive S3 e P3 compostos, em `backend/tests/unit/interface/test_andamento_situacoes.py` (SC-1235, SC-1237)
- [x] T011 [P] Testes puros da composição (S1, S2, S3, P1, P2, P3, CR, mista) e da expectativa em `backend/tests/unit/interface/test_andamento_composicao.py` (SC-1243, D-011, D-012)
- [x] T012 [P] Testes puros do agrupamento e da ordem em `backend/tests/unit/interface/test_providencias.py`

**Checkpoint**: a derivação existe e está provada sem banco.

## Phase 3: US1 + US2 + US3 — o nível 1 (B1, P1) 🎯 MVP

**Goal**: "O que fazer agora" do Edital publicado começa pelas providências, por papel.

**Independent Test**: os cenários de sorteio (S1), pontuação com Etapas (P1), pontuação com Etapa
governada (P2) e cadastro de reserva (CR) lidos por gestor, presidência, publicador, elaborador,
julgador e auditor.

- [x] T013 [US1] `views.detalhe` chama `andamento.do_edital` só em Edital publicado ou encerrado, sem trilha depois da publicação (D-002), em `backend/processo_seletivo/interface/views.py`
- [x] T014 [US1] Parcial `backend/processo_seletivo/interface/templates/interface/_providencias.html` e o cartão em `backend/processo_seletivo/interface/templates/interface/detalhe.html` (contrato §nível 1): contagem, suas, de outros, em espera, "Mais N", Atenção, ações de hoje sem cheia, imutável numa linha
- [x] T015 [P] [US1] Folha `backend/processo_seletivo/interface/static/interface/telas/andamento.css` com as classes novas, carregada no detalhe
- [x] T016 [US1] Testes de integração do nível 1 — S1, P2, CR, inscrições em curso, extração futura, Perfil sem inscrito, lista vazia, nada em aberto, encerrado, em elaboração — em `backend/tests/interface/test_andamento_do_edital.py` (SC-1231, SC-1232, SC-1234)
- [x] T017 [US2] Testes da presidência por pontuação (avaliar, distribuir, consolidar, Atenção, ordem *Depois*) em `backend/tests/interface/test_andamento_do_edital.py` (SC-1233)
- [x] T018 [US3] Testes por papel — publicador (definitivo seu), elaborador (sem link, sem nível 2), auditor (nada seu), julgador (recursos) — em `backend/tests/interface/test_andamento_do_edital.py` (FR-4055, FR-4056, FR-4081)

## Phase 4: US4 — coerência com o backend (B1, P1)

- [x] T019 [US4] Teste de coerência: por cenário e por papel, toda *Pendente* da pessoa leva a uma tela cujo GET mostra o controle do ato; toda *Aguarda*/*Impedido* a uma que diz a mesma razão ou não oferece o ato, em `backend/tests/interface/test_andamento_coerencia.py` (SC-1230)
- [x] T020 [US4] Testes de transição de leitura: depois de corte, apuração, publicação e convocação, a providência da lista muda, em `backend/tests/interface/test_andamento_coerencia.py` (SC-1236)
- [x] T021 [P] [US4] Orçamento de consultas do detalhe (3 × 30 inscrições, teto) em `backend/tests/performance/test_andamento_em_escala.py` (SC-1239, FR-4120)

## Phase 5: Fechamento do B1

- [x] T022 Capturas **depois** do nível 1 no clone, a 1280 e a 375 px, e medidas (UX-232, SC-1240), em `specs/127-andamento-da-selecao/capturas/depois-b1/`
- [x] T023 `make lint check test-pg` com `DB_NAME=spec127`; números contra a linha de base do CLAUDE.md em `specs/127-andamento-da-selecao/verificacao.md`
- [x] T024 Revisão independente do B1 (subagente que não escreveu o código: recomendação que o backend recusa, generalidade, permissões, custo); achados corrigidos e registrados em `specs/127-andamento-da-selecao/verificacao.md`
- [x] T025 `specs/127-andamento-da-selecao/rastreabilidade.md` com todo FR, SC, UX e caso-limite da parte B1; commit e PR do B1

## Phase 6: US5 — "Andamento da seleção" (B2, P2)

**Goal**: o cartão "Classificação" vira o andamento por Perfil, composto pela configuração.

- [ ] T026 [US5] Resumo em palavras por Perfil, linha das inscrições e nota da matrícula em `backend/processo_seletivo/interface/andamento.py` (FR-4101, FR-4102, FR-4109)
- [ ] T027 [US5] Parcial `backend/processo_seletivo/interface/templates/interface/_andamento_da_selecao.html` no lugar do cartão "Classificação" em `detalhe.html`, para quem via o cartão, com os destinos de `_marcos_publicados` (FR-4100, FR-4105, FR-4108)
- [ ] T028 [P] [US5] Moldura com rolagem própria e a tabela acessível em `backend/processo_seletivo/interface/static/interface/telas/andamento.css` (FR-4106, FR-4121, UX-233)
- [ ] T029 [US5] Testes do nível 2: colunas por família, Perfil sem inscrito em uma linha, quem vê, destinos preservados, nenhuma pendência só na matriz, em `backend/tests/interface/test_andamento_da_selecao.py` (SC-1243, FR-4107)
- [ ] T030 [US5] Capturas do nível 2 recolhido e aberto a 1280 e 375 px; altura recolhida contra a do cartão antigo (SC-1241, SC-1242) em `specs/127-andamento-da-selecao/capturas/depois-b2/`

## Phase 7: US6 — "Próximo nesta lista" (B1, por último, D-015)

- [ ] T031 [US6] Conferir com a sessão da `126` o estado dela; base sobre a `126` mergeada ou sobre a branch dela
- [ ] T032 [US6] `andamento.da_lista(edital, ator, marco_id, lista_id)` e o parcial `backend/processo_seletivo/interface/templates/interface/_proximo_nesta_lista.html` (FR-4090, FR-4091)
- [ ] T033 [US6] Incluir o parcial nas mensagens de sucesso de corte, ordenação, ocupação, sorteio, convocação e documentos, em `backend/processo_seletivo/interface/views.py` e templates (FR-4092)
- [ ] T034 [US6] Testes de transição nas telas em `backend/tests/interface/test_andamento_transicoes.py` (SC-1238)

## Phase 8: Polish

- [ ] T035 Suíte completa contra PostgreSQL, lint em dois passos; `verificacao.md` com os números
- [ ] T036 Revisão independente do B2 (e das transições); achados corrigidos
- [ ] T037 Rastreabilidade completa; commit e PR do B2, empilhado sobre o do B1; CI conferido nos dois

## Dependencies & Execution Order

- Setup → Foundational (T003 a T012) → B1 (T013 a T025) → B2 (T026 a T030) → Transições (T031 a
  T034) → Polish.
- T004 antes de T005 a T008 (mesmo arquivo, sequenciais); T009 a T012 em paralelo depois de T004.
- US4 depende de US1 (a tela) e de US3 (os papéis).
- US6 depende da `126` (D-015) e da derivação.

## Parallel Example

```text
Depois de T004: T009 (providencias.py) · T010, T011, T012 (testes puros) em paralelo.
Na B2: T028 (folha) em paralelo com T027 (parcial).
```

## Implementation Strategy

MVP = Phases 1 a 5: a derivação inteira e o nível 1 para todas as famílias, com o PR do B1. O B2 é
apresentação sobre a mesma derivação. As transições ficam para o fim, quando os templates da `126`
estiverem estáveis.
