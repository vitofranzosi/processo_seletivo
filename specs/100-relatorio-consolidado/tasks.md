# Tasks: Relatório consolidado da unidade

**Input**: Design documents from `specs/100-relatorio-consolidado/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/relatorio-consolidado.md

**Tests**: obrigatórios — a autorização do usuário de 24/10/2026 enumera as dez frentes de teste.

**Caminhos**: relativos à raiz do repositório; código em `backend/processo_seletivo/`, testes em
`backend/tests/`.

## Phase 1: Setup

- [x] T001 Registrar a linha de base da composição do relatório do Edital nos quatro estados do cenário (R-001), em teste temporário fora do commit, e guardar os resumos no `research.md` da feature, em `specs/100-relatorio-consolidado/research.md`

## Phase 2: Foundational — a `099` separada em fatos e redação

**Purpose**: o consolidado só existe sobre fatos estruturados (FR-2569, FR-2570).

- [x] T002 Acrescentar `Pendencia` (com os oito tipos) e `FatosDoEdital` em `backend/processo_seletivo/interface/relatorio_do_edital.py`
- [x] T003 Extrair `fatos_do_edital(edital, *, agora)` de `montar` — leituras e regras, pendências como `Pendencia` —, e a redação das pendências como função sobre os tipos, em `backend/processo_seletivo/interface/relatorio_do_edital.py`
- [x] T004 Reescrever `montar` sobre `fatos_do_edital` mais as leituras do anexo, sem mudar o documento, em `backend/processo_seletivo/interface/relatorio_do_edital.py`
- [x] T005 Reaplicar a linha de base de T001 e conferir composição idêntica nos quatro estados (SC-940); rodar `tests/integration/relatorio`, `tests/unit/interface/test_relatorio_do_edital.py`, `tests/interface/test_relatorio.py` e `tests/performance/test_relatorio.py`
- [x] T006 Parametrizar o cenário coerente por `numero` e `publicado_em`, com os padrões de hoje, em `backend/tests/fixtures/relatorio.py`

**Checkpoint**: a `099` expõe fatos; o documento individual não mudou.

## Phase 3: User Story 5 (parte da `099`) — correções autorizadas no relatório do Edital

- [x] T007 [P] [US5] Função pura `omitidos_por_complemento(populacoes, limiar)` e seus unitários (grupo único, complemento, total omitido, desempate) em `backend/processo_seletivo/interface/relatorio_do_edital.py` e `backend/tests/unit/interface/test_relatorio_do_edital.py`
- [x] T008 [US5] Aplicar a supressão complementar aos Perfis e omitir os totais não públicos do Edital quando `total_omitido` (indicadores, frases, recursos, linha de pendências escondidas) em `backend/processo_seletivo/interface/relatorio_do_edital.py` e `backend/processo_seletivo/interface/relatorio_pdf.py` (FR-2587, FR-2588)
- [x] T009 [US4] Marco de Perfil sem inscrição, período encerrado, sem publicação e sem ato: fora das pendências e dos resultados previstos, com "não se aplica: nenhuma inscrição enviada" (FR-2589) em `backend/processo_seletivo/interface/relatorio_do_edital.py`
- [x] T010 [US4] A trilha dita como registros da trilha de auditoria no ponto de atenção e no anexo (FR-2581) em `backend/processo_seletivo/interface/relatorio_do_edital.py` e `backend/processo_seletivo/interface/relatorio_pdf.py`
- [x] T011 [US5] Testes de integração das três correções sobre o cenário coerente (Perfil pequeno, Perfil vazio, frase da trilha) em `backend/tests/integration/relatorio/test_correcoes_da_100.py`

## Phase 4: User Story 1 — o balanço do semestre num documento (P1) 🎯 MVP

**Goal**: conjunto por primeira publicação, camada executiva na página, PDF.

**Independent Test**: três Editais do cenário publicados em datas diferentes; escolher o 1º semestre;
números da camada executiva iguais à soma dos fatos de cada Edital; baixar o PDF.

- [x] T012 [US1] `consolidar(fatos, conjunto, agora)` pura — universo, somas, razão Σ/Σ, ausências, cancelados, exclusão do Edital com total omitido, envios por mês, pendências por tipo e por Edital, seis indicadores, frases, pontos de atenção — em `backend/processo_seletivo/interface/relatorio_consolidado.py`
- [x] T013 [P] [US1] Unitários da soma com fatos sintéticos: agregação, conjunto vazio, só cancelados, cadastro de reserva, período aberto (parcial), resultado incompleto, registros posteriores, privacidade por exclusão em `backend/tests/unit/interface/test_relatorio_consolidado.py`
- [x] T014 [US1] Conjunto por primeira publicação com atalhos de ano e semestre, elegibilidade e "fora do conjunto", escopo do ator, limite, e `ler(conjunto, *, agora)` numa leitura consistente, em `backend/processo_seletivo/interface/relatorio_consolidado.py`
- [x] T015 [US1] Composição do PDF (camada executiva, seções, anexo, faixa em toda página, marcadores) em `backend/processo_seletivo/interface/relatorio_consolidado_pdf.py`
- [x] T016 [US1] Views de escolha, página e emissão, com a porta `visao:consultar`, resposta privada e recusas do contrato, em `backend/processo_seletivo/interface/relatorio.py`; rotas em `backend/processo_seletivo/interface/urls.py`
- [x] T017 [US1] Templates `relatorio_consolidado_escolha.html` e `relatorio_consolidado.html`, folha `static/interface/telas/relatorio-consolidado.css` e o link na Visão Geral em `backend/processo_seletivo/interface/templates/interface/`
- [x] T018 [US1] Integração: números do consolidado × soma dos fatos de cada Edital × Visão Geral para o mesmo universo (SC-939); listas sobrepostas contadas uma vez; cadastro de reserva fora da razão, em `backend/tests/integration/relatorio_consolidado/test_numeros.py`

## Phase 5: User Story 2 — o que foi analisado, e de quando (P1)

- [x] T019 [US2] Ficha e anexo com o critério por extenso e a data dos dados (FR-2561, FR-2565); série "Inscrições enviadas, por mês do envio" com a nota (FR-2578) em `backend/processo_seletivo/interface/relatorio_consolidado.py` e `backend/processo_seletivo/interface/relatorio_consolidado_pdf.py`
- [x] T020 [US2] Critério por ano do número e a diferença para a primeira publicação (48/2025 publicado em 2026) em `backend/processo_seletivo/interface/relatorio_consolidado.py`
- [x] T021 [US2] Integração: partição por semestre, ano do número × publicação, ato depois do fim do período aparecendo, instante único (o `SET TRANSACTION` emitido) em `backend/tests/integration/relatorio_consolidado/test_conjunto.py`

## Phase 6: User Story 3 — escolher os Editais à mão (P2)

- [x] T022 [US3] Escolha manual (critério `manual` com busca) e desmarcação no critério, com retirados e acrescentados ditos, em `backend/processo_seletivo/interface/relatorio_consolidado.py` e no template de escolha
- [x] T023 [US3] Integração e interface: desmarcar, escolher cinco, identificador de outro escopo ignorado em `backend/tests/integration/relatorio_consolidado/test_conjunto.py` e `backend/tests/interface/test_relatorio_consolidado.py`

## Phase 7: User Story 4 — o que está em curso no conjunto (P2)

- [x] T024 [US4] Seção de providências por tipo e por Edital, registros na trilha por Edital, "o que este relatório não diz" em `backend/processo_seletivo/interface/relatorio_consolidado_pdf.py` e no template da página
- [x] T025 [US4] Integração: encerrado com convocação no prazo, resultado só preliminar, Perfil sem inscrição, registros depois do encerramento em `backend/tests/integration/relatorio_consolidado/test_providencias.py`

## Phase 8: User Story 5 — emissão rastreável e privacidade (P2)

- [x] T026 [US5] Emissão: trava da Unidade, número pela trilha, evento com o conjunto e o resumo (R-005) em `backend/processo_seletivo/interface/relatorio.py`
- [x] T027 [US5] Integração: dois eventos e números 1 e 2; determinismo da composição; nenhum dado pessoal; nada por Perfil ou lista; Edital pequeno igual com e sem ele em `backend/tests/integration/relatorio_consolidado/test_emissao.py` e `backend/tests/integration/relatorio_consolidado/test_privacidade.py`
- [x] T028 [US5] Interface: porta (sem capacidade, recusa explicada), páginas renderizam, resposta privada, link na Visão Geral só para quem tem a capacidade em `backend/tests/interface/test_relatorio_consolidado.py`

## Phase 9: Polish & Cross-Cutting

- [x] T029 Orçamento: consultas por Edital constantes entre 1, 2 e 3 Editais e independentes da escala; tempo de um conjunto grande registrado, para confirmar o limite (R-006), em `backend/tests/performance/test_relatorio_consolidado.py`
- [x] T030 Guardiões: vocabulário, CSP, folha estática, gramática das portas, larguras — o que a suíte acusar — nos arquivos de teste correspondentes
- [x] T031 [P] Matriz de rastreabilidade em `specs/100-relatorio-consolidado/rastreabilidade.md`
- [x] T032 [P] README (linha da `100`), CLAUDE.md se a contagem de append-only ou a suíte mudarem de forma relevante, e quickstart executado
- [x] T033 PDF demonstrativo gerado pelo sistema e roteiro de semeadura em `doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/`
- [x] T034 `cd backend && make lint check test-pg DB_NAME=ps100`

## Phase 10: Revisão visual (pedido do usuário de 24/10/2026)

- [x] T035 Compositor de blocos marcado e o documento reescrito sobre ele, com os testes de diagramação em `backend/processo_seletivo/interface/diagramacao.py`, `backend/processo_seletivo/interface/relatorio_consolidado_pdf.py` e `backend/tests/unit/interface/test_diagramacao_do_consolidado.py`
- [x] T036 Título institucional, endereços só em host público e o subconjunto dito por extenso em `backend/processo_seletivo/interface/relatorio_consolidado.py` e `backend/processo_seletivo/interface/relatorio.py`
- [x] T037 Demonstração heterogênea (sete Editais de natureza diferente), PDF emitido pelo endpoint e comparação visual página a página em `doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/`

## Phase 11: Polish da página (pedido de 25/10/2026)

- [x] T038 Ficha e emissão num painel; cartões do PDF em 3 × 2; "Emitir e baixar PDF" com a frase da trilha ligada ao botão e um clique por emissão (`static/interface/emissao-do-relatorio.js`, o da `099`); seções com espaço próprio, em `backend/processo_seletivo/interface/templates/interface/relatorio_consolidado.html` e `telas/relatorio-consolidado.css` (FR-2566, FR-2573, FR-2574, FR-2591)

## Dependencies & Execution Order

- Phase 2 bloqueia tudo: o consolidado lê `fatos_do_edital`.
- Phase 3 (correções da `099`) antes da soma, porque `total_omitido` e o Perfil vazio entram nos fatos.
- US1 antes de US2–US5: as demais acrescentam ao mesmo módulo e às mesmas páginas.
- T029 depois de T016; T031–T034 no fim.

## Parallel Opportunities

- T007 e T013 (funções puras e seus unitários) em paralelo com as leituras.
- T031 e T032 (documentação) em paralelo.

## Implementation Strategy

MVP = Phases 1–4 (com as correções da `099`): o relatório do semestre emitido pela Visão Geral. As
fases 5–8 completam o que a autorização obriga antes de o PR ir para revisão.
