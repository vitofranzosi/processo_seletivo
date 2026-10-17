# Tasks: As telas de uso diário, primeiro incremento

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`.

## Phase 1: Setup

- [x] T001 Banco de teste próprio (`DB_NAME=ps_077`), o `ps_inventario_telas` em dia com as migrations e `uv sync --extra dev --extra assistente`
- [x] T002 Medir o teto da distribuição antes (`tests/performance/test_escala_da_mesa.py`) e anotar o valor — 94 908 bytes na `main` `5c729dd0`

## Phase 2: Foundational — o bloco do cabeçalho

- [x] T003 O bloco `caminho_do_contexto` no `header.cabecalho-de-contexto` de `processo_seletivo/interface/templates/interface/base.html`, com o caminho da `076` como conteúdo padrão, e a regra `.caminho-da-secao a` na folha (R-001; FR-1748)

## Phase 3: User Story 1 — a lista oferece o que é dela (P1) 🎯 MVP

**Goal**: a faixa de ações da lista só com "Novo Processo Seletivo".

**Independent Test**: como Gestor, a faixa tem uma ação; como Elaborador, não há faixa; a barra continua a mesma.

- [x] T004 [US1] `processo_seletivo/interface/templates/interface/lista.html`: a faixa só com "Novo Processo Seletivo", e só para quem pode criar (FR-1740, FR-1741)
- [x] T005 [US1] `processo_seletivo/interface/views.py::lista` sem os três `pode_*`; a docstring de `processo_seletivo/interface/navegacao.py` atualizada (R-003)
- [x] T006 [P] [US1] `tests/interface/test_shell_da_gestao.py::test_a_lista_e_a_barra_oferecem_as_mesmas_secoes` vira `test_a_lista_deixou_as_secoes_para_a_barra`: o conteúdo não oferece as seções, papel a papel; testes da faixa em `tests/interface/test_telas_de_uso_diario.py` (FR-1740, FR-1741, FR-1742, SC-670)

## Phase 4: User Story 2 — nenhuma tela rola para o lado (P1)

**Goal**: as cinco telas cabem em 375 px, com o mesmo conteúdo.

**Independent Test**: a sonda do inventário dá `scrollWidth` 375 nas cinco.

- [x] T007 [P] [US2] `conclusoes.html`: `.tabela-rolavel{position:relative}` na folha da tela (FR-1743, FR-1744)
- [x] T008 [P] [US2] `reaproveitar.html`: `fieldset{min-width:0}` na folha da tela
- [x] T009 [P] [US2] `sorteio.html`: `.imutavel code{overflow-wrap:anywhere}` na folha da tela
- [x] T010 [P] [US2] `compor_anexos.html`: `fieldset.linha.anexo-novo{min-width:0}` no bloco de estilo da tela
- [x] T011 [P] [US2] `retificacao_detalhe.html`: a tabela das alterações dentro de `div.tabela-rolavel`
- [x] T012 [US2] Testes em `tests/interface/test_telas_de_uso_diario.py`: cada correção presente na sua tela e ausente da folha comum (FR-1743, FR-1744, FR-1745)

## Phase 5: User Story 3 — onde estou, dito uma vez só (P2)

**Goal**: nas quatro telas, a trilha no cabeçalho e nenhuma no conteúdo.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", dentro do cabeçalho de contexto, e o `main` não tem nenhuma.

- [x] T013 [P] [US3] `lista.html` e `minhas_etapas.html`: a trilha de um nível no bloco (FR-1746)
- [x] T014 [P] [US3] `minha_etapa.html`: a trilha sai do conteúdo e vai ao bloco, pelas duas portas — Minhas Etapas e Alocação por Etapa (FR-1746, FR-1747)
- [x] T015 [P] [US3] `mesa_inscricao.html`: a trilha sai do conteúdo e vai ao bloco (FR-1746, FR-1747)
- [x] T016 [US3] Testes em `tests/interface/test_telas_de_uso_diario.py`: a trilha no cabeçalho, uma só, com links e página atual, nas quatro telas e nas duas portas da Etapa; o cabeçalho da `076` numa tela de fora (FR-1746, FR-1747, FR-1748, SC-673)

## Phase 6: Polish & verificação

- [x] T017 `make lint check` e `make test-pg DB_NAME=ps_077`; o teto da distribuição medido de novo (FR-1751, SC-674) — 11 456 passando e 11 pulados, nenhuma falha; distribuição em 94 957 bytes
- [x] T018 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-077/`, comparado por `comparar.py` com `com-o-shell/`; as capturas das nove telas tocadas; a seção "Depois da 077" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1745, FR-1749, FR-1750, SC-671, SC-672)
- [x] T019 O percurso do quickstart no navegador, a 1280 e a 375 px, só pelo teclado (FR-1749, SC-675)
- [x] T020 `rastreabilidade.md` com cada FR e SC, e o achado do R-002 registrado na seção de fora de escopo

## Dependencies

T003 antes de T013–T016. US1 e US2 são independentes entre si e de T003. T017–T019 depois de tudo.
