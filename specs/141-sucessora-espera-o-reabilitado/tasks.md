# Tasks: A ordem sucessora e o corte esperam a avaliação do reabilitado

**Input**: [spec.md](spec.md), [plan.md](plan.md)

Formato: `[ID] [P?] [História] Descrição`. `[P]` pode correr em paralelo (arquivos diferentes).

## Phase 1: Fundação

- [x] T001 Acrescentar `Celula.vigente_para_tras` e a função `ordem_para_tras` em
  `backend/processo_seletivo/interface/andamento.py` (FR-4833)

## Phase 2: User Story 1 — A sucessora espera a Etapa do reabilitado (P1)

- [x] T002 [US1] Em `situacao_da_ordem`, o ramo obsoleto com `faltam` devolve *Depois*, com a razão
  da UX-340 e o dado da T001 (FR-4830, FR-4831, FR-4832)
- [x] T003 [US1] O resultado lê `ordem_para_tras` nos três pontos que liam `OBSOLETO` (FR-4833)
- [x] T004 [US1] Em `_Leitor._marco`, a lista vazia só é perguntada sem Etapa por fazer (FR-4843)
- [x] T005 [P] [US1] Testes puros da ordem e de quem a lê, em
  `backend/tests/unit/interface/test_sucessora_espera_o_reabilitado.py` (FR-4830 a FR-4834)

## Phase 3: User Story 2 — O corte espera o reingresso (P1)

- [x] T006 [US2] `situacao_do_corte` recebe `reingresso` e diz *Depois* nas duas formas, com a razão
  da UX-341 (FR-4835, FR-4836, FR-4837)
- [x] T007 [US2] `_Leitor._reingresso_pendente`, pela função da publicação, uma vez por marco e só
  quando o corte seria providência; nunca no sorteio (FR-4835, FR-4838, FR-4843)
- [x] T008 [P] [US2] Testes puros do corte, no mesmo arquivo da T005
- [x] T009 [US2] Integração: a sucessora parcial emitida pela tela, e o corte anterior ao recurso, que
  continua vigente até a sucessora (D-004), em
  `backend/tests/integration/treinamento/test_sucessora_espera_o_reabilitado.py`

## Phase 4: User Story 3 — A cadeia inteira (P1)

- [x] T010 [US3] Integração: recurso deferido que reabilita → títulos pendente → consolidada →
  sucessora → corte → Análise documental, no C08, para três papéis no primeiro passo (SC-1510,
  SC-1511, SC-1513, FR-4839)

## Phase 5: User Story 4 — A correção de nota não espera (P1)

- [x] T011 [US4] Integração: o recurso do 07, que corrige a prova sem reabilitar, oferece a sucessora
  na hora; emitida, o corte segue o prazo recursal e depois é providência (SC-1512)

## Phase 6: User Story 5 — O aviso na tela do corte (P3)

- [x] T012 [US5] `_reingressos_no_corte` na view `corte`, e o aviso no template, antes do botão
  (FR-4840, FR-4841)
- [x] T013 [US5] Integração: a tela avisa com reingresso, não avisa sem ele, e o comando continua
  aceitando (FR-4841, FR-4842)

## Phase 6b: O Centro de Controle (achado na verificação no navegador)

- [x] T017 [US1] `centro.agregar`: o *Depois* com ordem vigente para trás é fase em curso (FR-4845),
  com teste em `backend/tests/unit/interface/test_sucessora_espera_o_reabilitado.py`

## Phase 7: Fechamento

- [x] T014 `make lint check test-pg` com `DB_NAME=ps_141`; o orçamento da `127` e a coerência com a
  `128` sem mudança de expectativa (SC-1514, SC-1515, FR-4844)
- [x] T015 O C08 no navegador, num banco descartável, registrado em [verificacao.md](verificacao.md)
  (SC-1516)
- [x] T016 [rastreabilidade.md](rastreabilidade.md) e a linha da `141` no README

## Dependências

T001 antes de T002, T003 e T006. As histórias US1 e US2 se provam em separado; a US3 depende das duas.
A US5 é independente da derivação.
