# Tasks: Polish das telas de operação

**Input**: Design documents from `specs/057-polish-telas-de-operacao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos. Toda mudança tem guarda em `backend/tests/interface/test_polish_da_057.py`,
porque a medida no navegador não roda na CI.

F = `backend/processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Conferir que a `055`, a `056` e a conversão dos comentários da folha estão na `main`; medir
  a faixa de identificadores em todas as worktrees; registrar em `specs/057-polish-telas-de-operacao/research.md` (D-001)
- [x] T002 Criar o banco `ps_057_polish` a partir de `ps_polish_audit`, `migrate --check`, e acrescentar
  a entrada `polish-057` em `.claude/launch.json` (revertida antes do commit)

## Phase 2: Foundational (medida "antes")

- [x] T003 Capturar, com `ana.gestora` e com `joana.avaliadora`, a lista de destinos de ação
  ([D-017](research.md)) de toda tela tocada — Lista, Detalhe do 01/2026 e do 51/2026, Condução do
  marco, ordem, corte, histórico do corte, ocupação, convocação, sorteio, matrículas, Processo,
  Supervisão, Auditoria, Detalhe da inscrição, Distribuição, Minha etapa, Alocação — em
  `specs/057-polish-telas-de-operacao/acoes-antes.json` (FR-1064, FR-1065; SC-408)
- [x] T004 Medir, a 1280 × 900, as medidas das decisões recebidas 3ª a 9ª e a tabela "antes" da
  auditoria — registrar em `specs/057-polish-telas-de-operacao/verificacao.md`
- [x] T005 Medir o HTML da distribuição com `backend/tests/performance/test_escala_da_mesa.py` isolado
  (print temporário, revertido)
- [x] T006 Capturas "antes" do Detalhe do Edital, da Lista, da Auditoria e da Alocação em
  `specs/057-polish-telas-de-operacao/capturas/`

**Checkpoint**: nada de template ou folha mudou até aqui.

## Phase 3: User Story 1 — Hierarquia no Detalhe do Edital (P1) 🎯 MVP

**Goal**: uma principal, secundárias em linha, terminais por último e contornadas; colunas pelo topo
(FR-1043 a FR-1047; SC-398; UX-140).

**Independent Test**: contar preenchidas e ler a posição de `.terminais` no Detalhe do 01/2026.

- [x] T007 [US1] Guarda: `test_a_hierarquia_reparte_sem_perder_acao`, `test_a_preferida_impedida_nao_e_substituida`
  e `test_o_detalhe_desenha_uma_principal_e_as_terminais_por_ultimo` em `backend/tests/interface/test_polish_da_057.py`
- [x] T008 [US1] `hierarquia(conjunto)` e `Acao.quantidade` em `backend/processo_seletivo/interface/acoes.py` (D-002, D-006)
- [x] T009 [US1] O detalhe passa o conjunto repartido em `backend/processo_seletivo/interface/views.py`
  e `F/detalhe.html` desenha principal, secundárias e `.terminais` (D-003)
- [x] T010 [US1] Regras do grupo de ações e das terminais; `align-items:start` em `.colunas` em `F/base.html`
- [x] T011 [US1] Recapturar a lista de destinos do Detalhe e comparar; rodar `test_acessibilidade.py`

## Phase 4: User Story 2 — Um gesto em destaque na Condução (P1)

**Goal**: o primeiro gesto preenchido, os demais secundários, lado a lado (FR-1048; SC-399).

- [x] T012 [US2] Guarda `test_a_conducao_destaca_so_o_primeiro_gesto` em `backend/tests/interface/test_polish_da_057.py`
- [x] T013 [US2] `F/marco.html`: o primeiro gesto `botao`, os demais `botao secundario`, num grupo em
  linha (D-008); regra em `F/base.html` se preciso
- [x] T014 [US2] Recapturar a lista de destinos da Condução e comparar

## Phase 5: User Story 3 — A coluna de ações da Lista (P1)

**Goal**: frequentes primeiro, terminais no fim e separadas, zerada esmaecida; linha ≤ 90 px
(FR-1049, FR-1050; SC-400).

- [x] T015 [US3] Guarda `test_a_lista_poe_as_frequentes_primeiro_e_as_terminais_no_fim` e
  `test_o_contador_zero_esmaece_sem_perder_o_rotulo` em `backend/tests/interface/test_polish_da_057.py`
- [x] T016 [US3] `views.lista` ordena e reparte as ações; `F/lista.html` desenha `.terminais` e
  `.zerada` (D-004, D-005, D-006)
- [x] T017 [US3] Regras de `.acao.zerada` e do grupo terminal em linha em `F/base.html`; medir a linha (D-007)
- [x] T018 [US3] Recapturar a lista de destinos da Lista e comparar

## Phase 6: User Story 4 — O glossário recolhido (P2)

**Goal**: o glossário num `details.como-preencher` fechado, a faixa à vista (FR-1051 a FR-1053;
SC-401; UX-141).

- [x] T019 [US4] Guarda `test_o_glossario_fica_recolhido_e_a_garantia_a_vista` (parametrizado pelas
  oito telas) em `backend/tests/interface/test_polish_da_057.py`
- [x] T020 [P] [US4] `F/marco.html`, `F/ordenacao.html`, `F/corte.html`, `F/corte_historico.html`,
  `F/ocupacao.html`, `F/convocacao.html`, `F/sorteio.html`, `F/matriculas.html`: o `p.definicoes`
  dentro do `details`, rótulo "Termos desta tela" (D-009)
- [x] T021 [US4] Rodar `backend/tests/test_vocabulario_da_composicao.py`; medir o topo do primeiro
  controle em cada tela; recapturar as listas de destinos

## Phase 7: User Story 6 — Números, datas e plurais (P2)

**Goal**: a Revisão, a Supervisão e a Condução sem "2.0000", "(s)" nem aaaa-mm-dd (FR-1058 a
FR-1060; SC-405).

- [x] T022 [US6] Guarda `test_a_revisao_escreve_numeros_datas_e_plurais_como_gente` em
  `backend/tests/interface/test_polish_da_057.py`
- [x] T023 [US6] `backend/processo_seletivo/interface/revisao.py`: percentual, Peso, Nota mínima,
  Pontuação máxima por `pontuacao`; versão em dd/mm/aaaa; plurais (D-015)
- [x] T024 [P] [US6] `backend/processo_seletivo/interface/supervisao.py`,
  `backend/processo_seletivo/interface/conducao_do_marco.py` e o resumo de acréscimo de
  `backend/processo_seletivo/interface/retificacao.py`: plurais
- [x] T025 [US6] Registro do que ficou: `doc/achado-f8-textos-que-saem-da-tela.md`

## Phase 8: User Story 5 — Sem caixa dentro de caixa (P2)

**Goal**: Atenção, Auditoria, documentos e fichas (FR-1054 a FR-1057; SC-402 a SC-404; UX-142).

- [x] T026 [US5] Guardas `test_a_atencao_e_lista_com_faixa_ambar`, `test_o_evento_de_auditoria_nao_e_cartao`,
  `test_os_documentos_da_inscricao_seguem_a_mesa` e `test_a_ficha_curta_tem_a_largura_do_conteudo` em
  `backend/tests/interface/test_polish_da_057.py`
- [x] T027 [US5] `.sinais` e `.sinal` em `F/base.html` (D-011); recapturar Processo e Supervisão
- [x] T028 [US5] `.auditoria li` em `F/base.html` (D-012); medir a altura média
- [x] T029 [US5] `F/inscricao_detalhe.html` em `ul.documentos`; saem as regras mortas de `F/base.html`;
  o resumo do arquivo vai para o estilo da página (D-013)
- [x] T030 [US5] `dl.ficha.curta` em `F/distribuicao.html` e `F/minha_etapa.html`; regra em `F/base.html`
  (D-014); medir o teto da distribuição de novo
- [x] T031 [US5] Recapturar as listas de destinos das telas de T3

## Phase 9: User Story 7 — A matriz de Alocação (P3)

**Goal**: página ≤ 1.280 px, `thead` ≤ 130 px, Edital como linha de grupo (FR-1061, FR-1062; SC-406).

- [x] T032 [US7] Guarda `test_a_matriz_agrupa_por_edital_e_fixa_o_cabecalho` em
  `backend/tests/interface/test_polish_da_057.py`
- [x] T033 [US7] `F/alocacoes.html`: linha de grupo por `regroup`, controles numa faixa; `F/base.html`:
  `thead` fixo e colunas mais estreitas (D-016)
- [x] T034 [US7] Medir largura e `thead`; recapturar a lista de destinos

## Phase 10: User Story 8 — O envio do portal numa linha (P3)

**Goal**: seletor, nome e "Enviar" numa linha (FR-1063; SC-407).

- [x] T035 [US8] Guarda `test_o_envio_de_documento_e_uma_linha` em `backend/tests/interface/test_polish_da_057.py`
- [x] T036 [US8] `backend/processo_seletivo/portal/templates/portal/_documentos.html` e
  `backend/processo_seletivo/portal/templates/portal/base.html` (D-018)
- [x] T037 [US8] Medir no portal com a candidata `MARIA` (`m@ex.br`), por cliques

## Phase 11: Polish & Cross-Cutting

- [x] T038 `make lint check test-pg DB_NAME=ps057t` em `backend/`; nenhum arquivo editado durante a suíte
  (FR-1066, FR-1067; SC-409)
- [x] T039 Medição "depois", a 1280 × 900 e a 375 px (FR-1068; SC-410); diff das listas de destinos (vazio); capturas
  "depois" — em `specs/057-polish-telas-de-operacao/verificacao.md`
- [x] T040 `specs/057-polish-telas-de-operacao/rastreabilidade.md`, requisito a requisito
- [ ] T041 Reverter `.claude/launch.json`; commit; PR com a tabela antes/depois, o diff vazio, o tamanho
  da distribuição e o total da suíte. Sem merge.

## Dependencies

- Setup → Foundational → as histórias. Nenhuma história depende de outra, salvo o arquivo comum
  `F/base.html`, que serializa as tarefas de folha.
- Ordem de entrega se faltar espaço no teto: US1, US2, US3, US4, US6, US5, US7, US8.

## Parallel Opportunities

- T020 (oito templates independentes); T024 (três módulos Python).

## Implementation Strategy

MVP = US1 (o Detalhe do Edital). Cada história fecha com a lista de destinos recapturada e
`test_acessibilidade.py` verde antes da seguinte.
