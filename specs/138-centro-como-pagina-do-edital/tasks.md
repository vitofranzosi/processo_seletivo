# Tasks: O Centro de Controle passa a ser a página do Edital

**Input**: [spec.md](spec.md), [plan.md](plan.md), [quickstart.md](quickstart.md)

**Tests**: pedidos pela própria troca — cada ato do conjunto do Edital, a escolha da composição, o
redirecionamento e a página anterior têm teste; os testes do detalhe passam a abrir a página
anterior sem mudar as asserções (R-008 do plano).

Caminhos relativos a `backend/`, salvo indicação.

## Phase 1: Setup

- [X] T001 Banco próprio `ps138` (`make preparar` com `DB_NAME=ps138`) e uma entrada `centro-138` (porta 8138, `INTERFACE_SELETOR_IDENTIDADE=true`) acrescentada a `../.claude/launch.json`, sem sobrescrever as demais

## Phase 2: Foundational

- [X] T002 `LeituraDoEdital` e `_leitura_do_edital(ator, edital, request)` em `processo_seletivo/interface/views.py`: participantes, pendências, segregação, conjunto, em curso, andamento, marcos com os destinos postos em cada Perfil, documentos, avisos, piloto do assistente, condução do imutável e conferência do ato, na ordem de hoje (FR-4861, R-001)
- [X] T003 `_desenhar_o_detalhe(request, leitura, *, pagina_anterior=False)` em `processo_seletivo/interface/views.py`, com o contexto de hoje de `detalhe.html` (R-002)
- [X] T004 `desenhar(request, leitura)` em `processo_seletivo/interface/centro_do_edital.py`, sem importar `views` (R-002)

## Phase 3: User Story 1 — a página do Edital publicado é o Centro (P1) 🎯 MVP

**Independent Test**: a rota do Edital publicado desenha o Centro; a do Edital em elaboração, cancelado ou com derivação indisponível, o detalhe; a de outra unidade, 404.

- [X] T005 [US1] `views.detalhe` passa a ser porta → leitura → Centro se há andamento, senão detalhe, em `processo_seletivo/interface/views.py` (FR-4860, FR-4862)
- [X] T006 [P] [US1] Testes da escolha em `tests/interface/test_centro_como_pagina.py`: publicado → Centro; em elaboração e cancelado → detalhe; derivação que falha → detalhe; outra unidade → 404; sem identidade → identificação (FR-4860 a FR-4862)
- [X] T007 [US1] `tests/performance/test_centro_em_escala.py` e `tests/integration/treinamento/test_centro_nos_cenarios.py` passam a abrir `interface:detalhe` (SC-1520, SC-1524)

## Phase 4: User Story 2 — o retorno do ato no Centro (P1)

**Independent Test**: os sete atos de `atos.ATOS`, praticados pela interface, mostram "Ato registrado" na página de chegada.

- [X] T008 [US2] "Ato registrado" e `_conferencia_do_ato.html` no cabeçalho de `processo_seletivo/interface/templates/interface/centro_do_edital.html`, logo depois do `<h1>` (FR-4865, UX-346)
- [X] T009 [US2] Testes dos sete atos em `tests/interface/test_centro_como_pagina.py`: publicar e encerrar chegam ao Centro com o retorno; cancelar, submeter, homologar, devolver e revogar a homologação chegam ao detalhe com o retorno; a conferência da `116` aparece no Centro depois de publicar (FR-4866, SC-1521)

## Phase 5: User Story 3 — o endereço do Centro leva ao Centro (P2)

**Independent Test**: `/centro/?fase=x` responde 302 para `/editais/<id>/?fase=x`.

- [X] T010 [US3] `centro_do_edital.centro_do_edital` vira redirecionamento sem porta, preservando a query, em `processo_seletivo/interface/centro_do_edital.py` (FR-4863, D-003)
- [X] T011 [US3] `_proximo_nesta_lista` monta `interface:detalhe`, em `processo_seletivo/interface/views.py`; as demais referências internas a `interface:centro-do-edital` saem (FR-4864)
- [X] T012 [P] [US3] Testes do redirecionamento (com e sem query, Edital de outra unidade) em `tests/interface/test_centro_como_pagina.py`, e os testes do Centro que abriam `/centro/` passam a abrir a página do Edital (`tests/interface/test_centro_do_edital.py`, `tests/interface/test_andamento_transicoes.py`, `tests/interface/test_auditoria_passagem_da_retificacao.py`, `tests/integration/treinamento/test_chegada_e_volta_nos_cenarios.py`, `tests/navegador/test_jornada_do_centro.py`) (SC-1523)
- [X] T013 [US3] Nota na linha 39 do inventário, em `../specs/033-navegacao-por-capacidade/inventario-das-negativas.md`, e no comentário de `MODULOS_DE_VIEW` em `tests/test_gramatica_das_portas.py`

## Phase 6: User Story 4 — a marca de validação sai (P2)

**Independent Test**: nenhum "em validação" nem "provisórios" no HTML da página do Edital e nos conceitos.

- [X] T014 [P] [US4] Sai o botão de `processo_seletivo/interface/templates/interface/detalhe.html` (FR-4867)
- [X] T015 [P] [US4] Sai a faixa, o caminho termina em "Edital N/AAAA", o título é o do Edital, em `processo_seletivo/interface/templates/interface/centro_do_edital.html` (FR-4867, FR-4868, D-006)
- [X] T016 [P] [US4] Sai `.cc-em-validacao` de `processo_seletivo/interface/static/interface/telas/centro.css` (FR-4870)
- [X] T017 [P] [US4] Docstrings de `processo_seletivo/interface/conceitos.py` e `processo_seletivo/interface/centro.py` sem "provisórios"; `tests/unit/interface/test_centro_composicao.py` prende a ausência (FR-4869, SC-1522)

## Phase 7: User Story 5 — a página anterior, por um ciclo (P3)

**Independent Test**: o link único do Centro leva à página anterior, que desenha o detalhe de antes.

- [X] T018 [US5] `views.pagina_anterior` e a rota `editais/<uuid:edital_id>/pagina-anterior/` (`interface:pagina-anterior`) em `processo_seletivo/interface/views.py` e `processo_seletivo/interface/urls.py` (FR-4873)
- [X] T019 [US5] O caminho "Edital N/AAAA › Página anterior" em `detalhe.html`, só com `pagina_anterior` (FR-4875)
- [X] T020 [US5] O link único, discreto, no fim de "Administração e histórico" do Centro, e a regra `.cc-pagina-anterior` em `telas/centro.css` (FR-4874, UX-345)
- [X] T021 [US5] Linha nova para `pagina_anterior` no inventário da `033` (`../specs/033-navegacao-por-capacidade/inventario-das-negativas.md`)
- [X] T022 [US5] Testes da página anterior em `tests/interface/test_centro_como_pagina.py`: a porta, o caminho, o link único no Centro e nenhum outro template levando a ela (FR-4873 a FR-4875, SC-1525)

## Phase 8: O que só o detalhe oferecia (FR-4871, FR-4872, D-005)

- [X] T023 Respostas do assistente de dúvidas, conversa com o assistente (piloto) e o aviso de conteúdo imutável com a condução no cartão "Ações e consultas do Edital" de `centro_do_edital.html`
- [X] T024 Datas e unidade em "Quem atuou" do Centro, sem o link "Autoridade, unidade e datas"
- [X] T025 Testes em `tests/interface/test_centro_como_pagina.py`: o link das dúvidas, o do piloto só com o piloto, o imutável calado para quem pode retificar, as datas

## Phase 9: Polish & Cross-Cutting

- [X] T026 Rodar a suíte e repartir as falhas pela R-008: os testes do detalhe passam a abrir `interface:pagina-anterior` sem mudar as asserções; os que conferem a página do Edital publicado passam a conferir o Centro. A repartição vai para `../specs/138-centro-como-pagina-do-edital/verificacao.md`
- [X] T027 [P] Atualizar `../doc/estudo-centro-de-controle-2026-11-09/08-plano-de-producao.md` (as decisões de 10/11, o incremento 3 feito), o `../README.md` e a Visão do Sistema, se existir
- [X] T028 `DB_NAME=ps138 make lint check test-pg` sem falha
- [X] T029 Conferência no navegador com C06, C08 e C12 num banco isolado (quickstart), registrada em `verificacao.md`
- [X] T030 PR contra a `main`, sem merge (#451)

## Dependencies & Execution Order

- T002–T004 bloqueiam tudo.
- US1 (T005–T007) é o MVP; US2 depende de T004 e T005.
- US3, US4 e US5 dependem só da fase 2 e de T005; entre si, só compartilham `centro_do_edital.html` e `test_centro_como_pagina.py`.
- T026 depois de todas as histórias; T028–T030 por último.

## Parallel Example

T014, T016 e T017 tocam arquivos diferentes e podem andar juntas; T006 e T012 escrevem no mesmo arquivo de teste e vão em sequência.

## Implementation Strategy

Uma sessão, um PR. A fase 2 e a US1 primeiro, depois US2 (sem ela a troca quebra o retorno de Publicar e Encerrar), e o resto na ordem; a suíte uma vez no fim para a R-008, e de novo para fechar.
