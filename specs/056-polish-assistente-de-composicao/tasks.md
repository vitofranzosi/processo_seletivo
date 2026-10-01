# Tasks: Polish do assistente de composição

**Input**: Design documents from `specs/056-polish-assistente-de-composicao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/assistente.md](contracts/assistente.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos. Toda mudança tem guarda em `backend/tests/interface/test_polish_da_056.py` (ou no
teste de JavaScript do script que muda), porque a medida no navegador não roda na CI.

F = `backend/processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Conferir que a `055` e a conversão dos comentários da folha (PR 244) estão na `main`; medir
  a faixa de identificadores em todas as worktrees; registrar em `specs/056-polish-assistente-de-composicao/research.md` (D-001)
- [x] T002 Criar o banco `ps_056_polish` a partir de `ps_polish_audit`, `migrate --check`, e acrescentar
  a entrada `polish-056` em `.claude/launch.json` (revertida antes do commit)

## Phase 2: Foundational (medida "antes")

- [x] T003 Medir, a 1280 × 900 no Edital 76/2027, stepper, h2, página, "Avançar" e o envio de "Salvar
  rascunho" de cada etapa; cartões de Evento, Etapa, Documento e Modalidade; campos longos do Perfil,
  do Documento e do Retificar (01/2026) — registrar em `specs/056-polish-assistente-de-composicao/verificacao.md`
- [x] T004 Medir o HTML da distribuição com `tests/performance/test_escala_da_mesa.py` isolado (print
  temporário, revertido)
- [x] T005 Capturas "antes" (cliente de teste + Chrome sem janela) em `specs/056-polish-assistente-de-composicao/capturas/`

**Checkpoint**: nada de template ou folha mudou até aqui.

## Phase 3: User Story 1 — O stepper numa linha (P1) 🎯 MVP

**Goal**: nove etapas numa linha a 1280 px, ≤ 80 px, colunas iguais abaixo (FR-1020, FR-1021,
FR-1022; SC-386, SC-387; UX-137).

**Independent Test**: altura de `ol.assistente` e h2 de Perfis; larguras dos `li` a 375 px.

- [x] T006 [US1] Guarda: `test_o_stepper_e_grade_de_colunas_iguais` e
  `test_a_situacao_da_etapa_continua_em_texto` em `backend/tests/interface/test_polish_da_056.py`
- [x] T007 [US1] Trocar as regras de `.assistente` em F`base.html` pela grade de [D-002](research.md);
  saem `flex:1 1 160px`, o `flex-wrap` e o `text-transform` de `.estado`
- [x] T008 [US1] Medir no navegador (altura, h2 de Perfis, 375 px) e recapturar o envio de todas as etapas

## Phase 4: User Story 4 — O Conteúdo do Edital compacto (P1)

**Goal**: página ≤ 3.000 px; seção vazia pequena e ainda dizendo que não sai (FR-1029 a FR-1032;
SC-391).

**Independent Test**: altura da página do Conteúdo; marca em toda seção vazia.

- [x] T009 [US4] Guardas: `test_a_secao_vazia_nasce_com_duas_linhas`,
  `test_a_secao_preenchida_mantem_a_altura`, `test_a_secao_gerada_nao_tem_caixa`,
  `test_a_marca_de_secao_vazia_continua` em `backend/tests/interface/test_polish_da_056.py`
- [x] T010 [US4] Em F`compor_conteudo.html`: `rows` condicional; o link da seção gerada dentro do
  parágrafo de ajuda; o `estilo_da_pagina` com a largura, a seção gerada sem caixa e a marca sem
  caixa-alta ([D-007](research.md), [D-008](research.md), [D-009](research.md))
- [x] T011 [US4] Medir o Conteúdo (1280 e 375 px) e recapturar o envio da etapa

## Phase 5: User Story 2 e 3 — Cartões com ações na legenda; Evento numa faixa (P1)

**Goal**: nenhuma linha só de ações; legenda com o item; Evento com datas lado a lado (FR-1023 a
FR-1028; SC-388, SC-389, SC-390; UX-138, UX-139).

**Independent Test**: cartões de Cronograma, Etapas, Inscrição e editor do Perfil.

- [x] T012 [US2] Em `backend/processo_seletivo/interface/static/interface/ordenacao.js`, `rotular`
  escreve a posição em `[data-ordem]` quando a legenda o tiver ([D-004](research.md)); caso novo em
  `backend/tests/javascript/ordenacao.test.js`; rodar `tests/test_javascript.py`
- [x] T013 [US2] Em F`base.html`: `fieldset.linha` posicionado; `fieldset.linha>.acoes-da-linha` no
  canto da legenda, e no fluxo abaixo de 48 rem; saem as regras de `.campos>.acoes-da-linha` e da
  reserva de rótulo ([D-003](research.md)); em F`_acoes_da_linha.html` sai `.rotulo-vazio`
- [x] T014 [P] [US2] [US3] F`_evento.html`: legenda em duas vozes com `[data-ordem]`; ações depois da
  legenda; Descrição `largo`; "Onde acontece" no fim da faixa, até 20 rem ([D-006](research.md))
- [x] T015 [P] [US2] F`_etapa.html`: legenda em duas vozes; ações depois da legenda
- [x] T016 [P] [US2] F`_documento.html`: legenda em duas vozes; ações depois da legenda
- [x] T017 [P] [US2] F`_modalidade.html`: legenda com o Código; "Aplicar aos demais Perfis" e
  "Remover esta Modalidade" no grupo de ações depois da legenda
- [x] T018 [US2] Guardas em `backend/tests/interface/test_polish_da_056.py`: ações logo depois da
  legenda nos quatro cartões; nenhum botão dentro da `legend`; `data-rotulo` igual à categoria;
  item sem identificador sem `.nome` vazio; Descrição antes das datas e "Onde acontece" depois
- [x] T019 [US2] Medir os quatro cartões (1280 e 375 px), a confirmação de remoção e recapturar o
  envio de Cronograma, Etapas, Inscrição e Perfis

## Phase 6: User Story 5 — A Revisão em grade (P2)

**Goal**: rótulos em coluna, conteúdo e ordem iguais, altura ≤ +10% (FR-1033, FR-1034; SC-392).

**Independent Test**: texto de cada item igual; nenhuma linha rotulada em `span.detalhe`.

- [x] T020 [US5] `Rotulada` e `com_origem` que a preserva em
  `backend/processo_seletivo/interface/origens.py`; as linhas rotuladas de
  `backend/processo_seletivo/interface/revisao.py` e de `origens.campos_definitivos` nascem por ela
  ([D-010](research.md))
- [x] T021 [US5] Filtro `em_trechos` em `backend/processo_seletivo/interface/templatetags/interface_extras.py`;
  F`compor_revisao.html` desenha os trechos, com o limite da coluna do rótulo no `estilo_da_pagina`
- [x] T022 [US5] Guardas: `Rotulada` igual à cadeia; `com_origem` preserva; texto de quem elabora com
  dois-pontos não vira rótulo; a Revisão renderizada tem `dt` para as linhas rotuladas
- [x] T023 [US5] Medir a Revisão e comparar o texto de cada item com o "antes"

## Phase 7: User Story 6 — Texto longo (P2)

**Goal**: FR-1035, FR-1036; SC-393.

- [x] T024 [P] [US6] F`_perfil.html` (Descrição) e F`_documento.html` (Instrução) em `textarea`
  `rows="2"`, mesmo `name`
- [x] T025 [US6] `CAMPOS_RAIZ` de `backend/processo_seletivo/interface/retificacao.py`: três campos para
  `TEXTO_LONGO`; F`_retificacao_linha.html` com 2 linhas para eles ([D-011](research.md))
- [x] T026 [US6] Guardas dos cinco campos; medir sem corte no navegador; recapturar o envio de Perfis
  e Inscrição

## Phase 8: User Story 7 — Anexos (P3)

**Goal**: FR-1037; SC-394.

- [x] T027 [US7] `.navegacao-etapa{max-width:none}` em F`base.html`; estado vazio de F`compor_anexos.html`
  sem a medida de leitura ([D-012](research.md)); guarda; medir "Avançar"

## Phase 9: User Story 8 — Ordem do Perfil no Retificar (P3, dispensável)

**Goal**: FR-1038.

- [x] T028 [US8] Filtro que reordena os campos do grupo de Perfil depois da referência atribuída;
  F`_retificacao_linha.html` o usa ([D-013](research.md)); guarda de que os nomes não mudam e a ordem
  segue a do Compor

## Phase 10: Polish & Cross-Cutting

- [x] T029 Conferir o diff contra a FR-1041 (ajuda, gravação, PDF, padrão de interação); `make lint
  check test-pg` com `DB_NAME` próprio; nada editado durante a suíte (FR-1040; SC-396)
- [x] T030 Medida "depois" no mesmo banco (1280 e 375 px), envio de todas as etapas (FR-1039,
  SC-395), tamanho da distribuição, 375 px (FR-1042, SC-397); capturas "depois"; `verificacao.md` completo
- [x] T031 `rastreabilidade.md` requisito a requisito; reverter `.claude/launch.json`; commit e PR sem merge

## Dependencies & Execution Order

- Setup → Foundational (a medida "antes" precede qualquer mudança) → histórias.
- As histórias são independentes entre si; a ordem acima é a de entrega do prompt (F1, F3, F2, F4,
  F5, D4, F6).
- Dentro da Fase 5, T012 e T013 antes de T014–T017 (a legenda nova depende do script e da folha);
  T014–T017 são arquivos diferentes e podem correr juntos.

## Parallel Example

```text
T014 _evento.html · T015 _etapa.html · T016 _documento.html · T017 _modalidade.html
```

## Implementation Strategy

MVP é a US1: sozinha, ela sobe o trabalho de todas as nove etapas em ~108 px. Depois, uma etapa por
vez, com o envio recapturado e `test_acessibilidade` rodado ao fim de cada fase.
