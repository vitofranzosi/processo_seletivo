# Tasks: Centro de Controle do Edital

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/pagina.md](contracts/pagina.md)

**Tests**: pedidos pela spec (SC-1470 a SC-1480) e pelo plano de produção do estudo. Os testes vêm
junto de cada história.

Caminhos relativos à raiz do repositório. `interface/` é `backend/processo_seletivo/interface/`.

## Phase 1: Setup

- [ ] T001 Conferir o ambiente da worktree: `uv sync --extra dev --extra navegador`, `backend/.env` com `DB_NAME=ps136`, `make preparar` e `migrate --check` no banco da worktree.
- [ ] T002 Acrescentar a entrada `centro-136` (porta 8136, `DB_NAME=ps136`, seletor ligado, `CENARIOS_DE_TREINAMENTO=true`) em `.claude/launch.json`, sem tocar nas outras entradas.

## Phase 2: Foundational

- [ ] T003 Criar `interface/conceitos.py`: as oito fases (chave, nome, pergunta), os três grupos, os quatro andamentos (rótulo e sinal), os conceitos por tipo de ponto da `127` (`simples`, `termo`, `curta`, `porque`, `ao_confirmar`), o conjunto `JARGAO` e as frases fixas; cabeçalho dizendo que os textos são provisórios (D-006); nenhum texto com «recorte», «faixa» ou «geração» (R-002).
- [ ] T004 Criar `interface/centro.py` com as estruturas do data-model e as funções puras `agregar`, `juntar`, `fase_do_ponto`, `fase_da_providencia` (R-004), `paralela` (R-005), `destaque` (R-006), `onde_estamos`, `papel`, `fase_consultada` (R-007) e `compor`.
- [ ] T005 [P] Testes puros em `backend/tests/unit/interface/test_centro_composicao.py`: as tabelas de `agregar` e `juntar` (FR-4710, FR-4711); a fase de cada tipo de ponto e de cada natureza (FR-4709, FR-4716), inclusive que nenhuma natureza da `127` cai no padrão; a paralela com sorteio, com habilitação e com dois Perfis (D-008); as três regras do destaque e o que destrava (FR-4722 a FR-4725); "Onde estamos" (FR-4718, FR-4719); a regra fixa da fase consultada; a fixture da seleção concluída e a de dois Perfis; os conceitos completos e sem os três termos.

## Phase 3: User Story 1 — Saber onde a seleção está (P1) 🎯 MVP

**Goal**: a página, na rota própria, com o topo (onde estamos e os três estados) e o mapa.

**Independent Test**: no C12, como a presidência, o topo e o mapa mostram mais de uma fase em curso e
nenhuma "atual".

- [ ] T006 [US1] Criar a view `centro_do_edital` em `interface/centro_do_edital.py`: identidade, porta `obter_edital` (404), 302 para o detalhe sem andamento (D-002), e as funções do detalhe na mesma ordem (R-003); rota `editais/<uuid:edital_id>/centro/` (`centro-do-edital`) em `interface/urls.py`.
- [ ] T007 [US1] Registrar a view em `MODULOS_DE_VIEW` de `backend/tests/test_gramatica_das_portas.py` e a linha "acrescentada pela `136`" em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`.
- [ ] T008 [US1] Criar `interface/templates/interface/centro_do_edital.html` com a trilha de navegação, o título, a linha de validação com o link para o detalhe (UX-318), "Onde estamos", os três estados (FR-4720, FR-4721) e o mapa em três grupos com andamento e marcas separados (FR-4708, FR-4715, UX-314), e a legenda recolhida.
- [ ] T009 [P] [US1] Criar `interface/static/interface/telas/centro.css` com a grade, o mapa, os grupos, as marcas, a fase consultada (UX-315) e os pontos de quebra (UX-317, FR-4746); sem `}}` numa linha.
- [ ] T010 [US1] Testes da página em `backend/tests/interface/test_centro_do_edital.py`: 200 no publicado, 302 antes da publicação e no cancelado, 404 em outra unidade; o topo e o mapa; nenhum `aria-current` além do da fase consultada.

## Phase 4: User Story 2 — O que fazer agora, e por quê (P1)

**Goal**: o cartão com o destaque e o critério, as suas, as em espera, as de outros papéis, as
Retificações em curso.

**Independent Test**: C06 destaca "Fixar os participantes"; C12 não destaca; C08 destaca "Classificar a
lista".

- [ ] T011 [US2] Desenhar "O que fazer agora" em `interface/templates/interface/centro_do_edital.html` (FR-4722 a FR-4729, UX-316), com o link de cada providência vindo dela.
- [ ] T012 [US2] Testes nos cenários em `backend/tests/integration/treinamento/test_centro_nos_cenarios.py`: o destaque do C06, do C08 e do C12 (SC-1471); "Nenhuma ação é sua agora" para quem não tem; a coerência com o `Andamento` (SC-1473); o link ausente para quem não pratica e a recusa da tela real (SC-1475).

## Phase 5: User Story 3 — Entender uma fase (P2)

**Goal**: o detalhe da fase consultada, com o roteiro e a tabela por lista.

**Independent Test**: no C12, Classificação consultada e Convocação em curso são distintas.

- [ ] T013 [US3] Desenhar o detalhe da fase em `interface/templates/interface/centro_do_edital.html` (FR-4730 a FR-4736): a pergunta, as marcas, o roteiro, a tabela por lista só com `ve_a_matriz`, "Entenda os passos desta fase" recolhido, e o detalhe próprio das fases Edital, Inscrições e Conclusão.
- [ ] T014 [US3] Testes: no C12, `?fase=classificacao` leva `aria-current` e "fase consultada" à Classificação, e a Convocação fica *Em curso* sem eles (SC-1472); no C06, o roteiro da Classificação com "no GPS: congelar a relação" e a razão do passo da semente; quem não vê a matriz não recebe tabela nem roteiro por lista — em `backend/tests/integration/treinamento/test_centro_nos_cenarios.py`.

## Phase 6: User Story 4 — Onde cada lista está (P2)

- [ ] T015 [US4] Desenhar "Onde cada lista está" em `interface/templates/interface/centro_do_edital.html` (FR-4737 a FR-4739), com a matriz da `127` recolhida e os destinos do marco.
- [ ] T016 [US4] Testes por papel (presidência, avaliação, Gestor, Publicador) nos C06, C08 e C12, e dois Perfis por fixture de teste, em `backend/tests/integration/treinamento/test_centro_nos_cenarios.py` e `backend/tests/interface/test_centro_do_edital.py` (SC-1474, SC-1480).

## Phase 7: User Story 5 — Administrar sem esbarrar no irreversível (P3)

- [ ] T017 [US5] Desenhar "Administração e histórico" em `interface/templates/interface/centro_do_edital.html` (FR-4740, FR-4741): documentos com "o que mudou", consultas do conjunto de ações, avisos, quem atuou, validação, e Encerrar e Cancelar em `<details>`.
- [ ] T018 [US5] Testes: Encerrar e Cancelar recolhidos para o Gestor, ausentes para a avaliação e o Publicador — em `backend/tests/integration/treinamento/test_centro_nos_cenarios.py`.

## Phase 8: User Story 6 — Ir e voltar (P3)

- [ ] T019 [US6] Acrescentar o link de ida em `interface/templates/interface/detalhe.html`, só com andamento, com a regra na folha comum ou em `telas/andamento.css` (FR-4703).
- [ ] T020 [US6] Testes dos dois links, em `backend/tests/interface/test_centro_do_edital.py` (SC-1478).

## Phase 9: Polish & Cross-Cutting

- [ ] T021 [P] Orçamento de consultas em `backend/tests/performance/test_centro_em_escala.py` (FR-4744, SC-1476): igual com 3 e 30 inscrições, abaixo do teto.
- [ ] T022 [P] Jornada no navegador em `backend/tests/navegador/test_jornada_do_centro.py` (SC-1470, SC-1477, FR-4747): C06 a 1440 × 900 com as três respostas na dobra; 375 px sem rolagem horizontal; nenhuma violação de CSP; a ordem do Tab.
- [ ] T023 Casos-limite em `backend/tests/interface/test_centro_do_edital.py` (SC-1480): Edital sem providência, prazo, impedimento com quem resolve, Retificação em curso.
- [ ] T024 `specs/136-centro-de-controle-do-edital/rastreabilidade.md` cobrindo FR-4700 a FR-4748, SC-1470 a SC-1480 e UX-314 a UX-318.
- [ ] T025 Conferir no navegador os C06, C08 e C12 com dois papéis (quickstart), e registrar em `specs/136-centro-de-controle-do-edital/verificacao.md`.
- [ ] T026 `cd backend && make lint check test-pg`, sem falha nova; os números da suíte em `verificacao.md`.

## Dependencies

- T003 → T004 → T005; T004 → T006 → T008 → T011 → T013 → T015 → T017.
- T009 em paralelo a T008. T019 depende de T006 (a rota). T021 e T022 dependem do template completo.
- As histórias dividem o mesmo template; a ordem é a das camadas. Cada fase é testável ao terminar.

## Parallel Example

```text
T005 (testes puros)  ‖  T009 (folha)
T021 (orçamento)     ‖  T022 (navegador)
```

## Implementation Strategy

MVP = US1 + US2 (o topo, o mapa e "O que fazer agora"): é o que responde às tarefas 1, 2 e 4 da
validação com operadores. US3 a US6 completam a página antes do PR; nenhuma vai sem as outras, porque o
plano de produção pede uma página que nasce completa.
