# Tasks: Polish — os resíduos dos três lotes

**Input**: Design documents from `specs/058-polish-residuos/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/telas.md, quickstart.md

**Tests**: pedidos pela feature — cada item tem o seu caso em
`backend/tests/interface/test_polish_da_058.py`, e as provas da 2ª decisão são medidas antes e
depois.

F = `backend/processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [X] T001 Acrescentar a entrada `polish-058` (porta 8058, `DB_NAME=ps_058_polish`) ao `.claude/launch.json`, para reverter antes do commit
- [X] T002 Escrever os scripts de prova em `specs/058-polish-residuos/capturas/acoes.py` (destinos por papel, D-010) e `specs/058-polish-residuos/capturas/rascunho.py` (rascunho gravado das Etapas, D-005)

## Phase 2: Foundational — a medição "antes"

**⚠️ Nenhum template nem folha muda antes desta fase terminar.**

- [X] T003 Gravar `specs/058-polish-residuos/acoes-antes.json` com `capturas/acoes.py`, para `ana.gestora` e `joana.avaliadora`, nas telas tocadas
- [X] T004 Gravar o envio de "Salvar rascunho" das etapas Etapas e Revisão do 76/2027 (FormData, decisões 005 e 015 da `056`) e o rascunho gravado das Etapas (`capturas/rascunho.py`) em `specs/058-polish-residuos/verificacao.md`
- [X] T005 Medir a 1280 × 900 o Processo, a Matrículas, os Resultados, a Revisão do 76/2027, a Ocupação, o Sorteio, a Ordenação, o Corte e as Etapas; e a 375 px a Lista e a Condução; gravar em `specs/058-polish-residuos/verificacao.md` e as capturas "antes" do Processo, da Lista a 375 e da Revisão em `specs/058-polish-residuos/capturas/`
- [X] T006 Medir o HTML da distribuição (`tests/performance/test_escala_da_mesa.py`) com `print(len(corpo))` temporário, e gravar em `specs/058-polish-residuos/verificacao.md`

## Phase 3: User Story 1 — Processo, os irreversíveis não são os mais fortes (P1) 🎯 MVP

**Goal**: FR-1069, FR-1070. **Independent Test**: Processo Ativo do seed sem ato cheio, Encerrar e Cancelar à parte e contornados.

- [X] T007 [US1] Criar F`_estilo_das_terminais.html` com `.lista-acoes.em-linha`, `.lista-acoes+.terminais`, `.terminais .botao` e `:hover`, tirados do bloco de estilo de F`detalhe.html`, que passa a incluí-lo (D-002)
- [X] T008 [US1] Em F`processo_detalhe.html`: incluir o parcial no `estilo_da_pagina`; desenhar os atos não irreversíveis em `ul.lista-acoes.em-linha` como `botao secundario`, e os irreversíveis em `ul.lista-acoes.em-linha.terminais` com o marcador; manter a frase de ausência e o aviso depois (D-001)
- [X] T009 [US1] Testes de R1 em `backend/tests/interface/test_polish_da_058.py`: renderização do Processo Ativo e em elaboração; o parcial resolvido nas duas telas; nenhuma regra na folha comum
- [X] T010 [US1] Recapturar os destinos do Processo e do Detalhe do Edital e rodar `test_acessibilidade` e `test_polish_da_057`

## Phase 4: User Story 2 — A 375 px, toda ação se alcança (P1)

**Goal**: FR-1071 a FR-1073. **Independent Test**: documento = 375 na Lista e na Condução; moldura alcança o último botão.

- [X] T011 [US2] Em F`base.html`, acrescentar `.rolavel-no-estreito` ao seletor da regra `overflow-x:auto` da `@media (max-width:60rem)` da `.distribuicao-moldura`, com comentário de template (D-003)
- [X] T012 [US2] Em F`lista.html`, envolver a `table` de cada Processo em `div.rolavel-no-estreito`
- [X] T013 [US2] Em F`marco.html`, envolver a tabela "Recortes deste marco" em `div.rolavel-no-estreito`
- [X] T014 [US2] Testes de R2 em `backend/tests/interface/test_polish_da_058.py`: a regra só dentro da `@media`, na mesma da Alocação; a moldura nas duas telas
- [X] T015 [US2] Medir a 375 px a Lista e a Condução, e a 1280 px a Alocação (cabeçalho fixo); recapturar os destinos

## Phase 5: User Story 3 — A mesma decisão na tela vizinha (P2)

**Goal**: FR-1074 a FR-1077.

- [X] T016 [P] [US3] Em F`matriculas.html`, tirar `class="resumo"` da `section` (R3)
- [X] T017 [P] [US3] Em F`resultados.html`, `class="tabela"` na tabela e `numero` só na célula pontuada (R4, D-009)
- [X] T018 [US3] Trocar os plurais com parênteses de F`distribuicao.html`, F`matriculas.html`, F`recurso.html`, F`ocupacao.html` l. 117, F`ocupacao_historico.html` l. 71 e F`compor_base.html` l. 70 por `plural`/`contagem`, conferindo antes cada um (D-004)
- [X] T019 [US3] Reescrever para a grafia nova as asserções de `backend/tests/interface/test_compor_quadro.py`, `backend/tests/interface/test_consolidar_todas_as_prontas.py` e `backend/tests/acceptance/test_resultado_da_etapa.py`
- [X] T020 [US3] Testes de R3, R4 e R5 em `backend/tests/interface/test_polish_da_058.py`; recapturar os destinos

## Phase 6: User Story 4 — O valor das Etapas (P2)

**Goal**: FR-1078, FR-1079.

- [X] T021 [US4] Em `backend/processo_seletivo/interface/forms.py`, `etapas_do_edital` escreve Peso, Nota mínima e Pontuação máxima sem zeros à direita, com ponto decimal (D-005)
- [X] T022 [US4] Medir o rascunho gravado depois de "Salvar rascunho" com o formulário novo e comparar com T004; se diferir, reverter T021 e registrar no achado do F8
- [X] T023 [US4] Testes de R6 em `backend/tests/interface/test_polish_da_058.py`: "2", "6", "87.5", vazio continua vazio

## Phase 7: User Story 5 — Revisão e motivos (P3)

**Goal**: FR-1080 a FR-1083.

- [X] T024 [P] [US5] Em F`compor_revisao.html`, coluna de rótulos `min(Nrem, 40%)`, com `N` da medida de T005 (D-006)
- [X] T025 [P] [US5] Em F`ocupacao.html`, "Motivo da nova apuração" em `p.campo` com `textarea rows="3"` e `span.ajuda` (D-007)
- [X] T026 [P] [US5] Em F`sorteio.html`, "Motivo da sucessão" como `textarea rows="3"`; "Motivo da anulação" fica (D-007, D-008)
- [X] T027 [US5] Testes de R7 e R8 em `backend/tests/interface/test_polish_da_058.py`; medir o x dos valores da Revisão e o controle e a largura do motivo nas quatro telas; recapturar os destinos e o envio da Revisão

## Phase 8: Polish & Cross-Cutting

- [X] T028 [P] R9: em `specs/056-polish-assistente-de-composicao/research.md`, a D-003 passa a dizer 60 rem
- [X] T029 Gravar `specs/058-polish-residuos/acoes-depois.json` e o `diff` com o antes; o envio das etapas depois
- [X] T030 `cd backend && make lint check test-pg DB_NAME=test_ps_058` — sem editar arquivo durante a suíte; o total em `verificacao.md`
- [X] T031 Medição "depois" completa e capturas "depois" em `specs/058-polish-residuos/verificacao.md` e `capturas/`; o tamanho da distribuição depois
- [X] T032 [P] `specs/058-polish-residuos/rastreabilidade.md`, requisito a requisito
- [X] T033 [P] Fechar os achados: `doc/achado-lista-e-conducao-a-375px.md`, `doc/achado-resumo-na-secao-das-matriculas.md`, `doc/achado-coluna-numerica-dos-resultados.md`, `doc/achado-f8-textos-que-saem-da-tela.md` — situação "resolvido pela `058`", com a medida
- [X] T034 Reverter a entrada do `.claude/launch.json`; commit e PR, sem merge

## Dependencies

- Phase 2 bloqueia todas as histórias (a medição "antes").
- US1 a US5 são independentes entre si; T018 e T016 tocam o mesmo arquivo (`matriculas.html`) e
  correm em sequência; T025 e T018 tocam `ocupacao.html` em linhas diferentes, também em sequência.
- Phase 8 depois de todas.

## Parallel Example

```text
T016, T017 (templates diferentes) · T024, T025, T026 · T028, T032, T033
```

## Implementation Strategy

Um item por vez, na ordem das histórias; depois de cada um, recapturar a prova que ele toca e rodar
`test_acessibilidade`. O MVP é a US1. Item que mude uma prova sai, é revertido e vira registro.
