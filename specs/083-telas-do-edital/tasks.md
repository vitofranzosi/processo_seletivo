# Tasks: As telas do Edital, quinto incremento

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco do inventário próprio (`ps_inventario_083`, cópia do `ps_inventario_telas`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_083`) e `uv sync --extra dev --extra assistente`; o servidor de preview por variáveis na linha de comando, sem tocar no `.claude/launch.json`
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `cf6d7372`, guardado em `depois-da-083/antes/`; comparado com `depois-da-080/` — 0 estouros, nenhum `status` diferente, nenhuma variante mudou

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho existe desde a `077`, e o parcial do produto desde a `078`.

## Phase 3: User Story 1 — onde estou, dito uma vez só (P1) 🎯 MVP

**Goal**: a trilha no cabeçalho nas doze telas.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título.

- [x] T003 [P] [US1] `edital_criar.html`, `retificar.html`, `retificacao_detalhe.html`, `retificacao_confirmar.html`, `previa.html`, `reaproveitar.html`, `reaproveitar_confirmar.html`, `marco.html`, `marco_conferir.html`, `previa_de_publicacao.html`, `publicacoes_do_marco.html`: a trilha do Edital com os níveis de cada tela, no bloco `caminho_do_contexto`; os comentários da E2E17-002 acompanham os dois níveis condicionais (R-001; FR-1850, FR-1851, FR-1852, FR-1854)
- [x] T004 [P] [US1] `auditoria.html`: o ramo do Edital no bloco, e nenhuma trilha no conteúdo (R-001; FR-1850, FR-1852)
- [x] T005 [US1] Consultas medidas antes e depois nas doze telas, com um teste descartável: nenhuma a mais (R-002)
- [x] T006 [US1] Testes em `tests/interface/test_telas_do_edital.py`: a trilha única no cabeçalho e o conteúdo pelo título nas doze telas; os níveis condicionais nomeados para quem só publica e links para quem alcança a classificação; a seção da barra (FR-1850 a FR-1852, FR-1854, SC-732, SC-733)
- [x] T007 [US1] Os guardiões da `077` e da `080` que fixavam a Auditoria do Edital com o cabeçalho da `076`: o da `080` sai, com um comentário que aponta para o arquivo novo; o da `077` passa à Supervisão (R-006; FR-1853)

## Phase 4: User Story 2 — o que acabou de acontecer (P2)

**Goal**: a recusa do último envio logo abaixo do título.

**Independent Test**: em Retificar e na Prévia de publicação, a recusa antes da ajuda.

- [x] T008 [P] [US2] `retificar.html` e `previa_de_publicacao.html`: a recusa logo depois do `p.sub`, com o comentário do porquê (R-003; FR-1856)
- [x] T009 [US2] Na Condução do marco, a resposta ao gesto foi subida e devolvida ao lugar: o desfecho usa *recorte* antes do `dfn` (D-007; R-003)
- [x] T010 [US2] Testes: a recusa de Retificar antes de "Como funciona"; a da Prévia de publicação antes da frase da prévia, e as consequências antes do formulário (FR-1856)

## Phase 5: User Story 3 — no detalhe da Retificação, o que fazer primeiro (P2)

- [x] T011 [US3] `retificacao_detalhe.html`: "O que fazer agora" como primeiro cartão de `.colunas` (R-004; FR-1857)
- [x] T012 [US3] Teste: "O que fazer agora" antes de "Vigência", e as duas antes das alterações (FR-1857)

## Phase 6: User Story 4 — "Filtrar" em Partir de um Edital anterior (P3)

- [x] T013 [US4] `reaproveitar.html`: "Filtrar" como `botao` e "Limpar" como `acao` (R-005; FR-1858)
- [x] T014 [US4] Testes: "Filtrar" com o desenho de ação principal, "Limpar" com o de secundária quando há busca, "Usar como base" sem mudança; as ações que não se desfazem com o desenho de antes (FR-1858, FR-1859)

## Phase 7: Polish & verificação

- [x] T015 `make lint check` e `make test-pg DB_NAME=ps_083` (FR-1861, SC-734) — 11 659 passando e 11 pulados, nenhuma falha, em 2441s com 4 workers (cinco suítes de outras worktrees no mesmo cluster ao mesmo tempo)
- [x] T016 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel com o de antes; as capturas das telas do escopo, antes e depois; a seção "Depois da 083" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1855, FR-1860, SC-730, SC-731)
- [x] T017 O percurso do quickstart no navegador, a 1280 e a 375 px, pelo teclado (FR-1855, SC-735)
- [x] T018 `rastreabilidade.md` com cada FR e SC; a `FR-1782` da `079` e a `FR-1803` da `080` anotadas como emendadas, na spec e na rastreabilidade de cada uma; a linha da `083` no README

## Dependencies

T003 e T004 primeiro; T008, T011 e T013 tocam os mesmos templates depois deles. Os testes de cada
fase depois da mudança dela. T015–T018 depois de tudo.

## Implementation Strategy

US1 primeiro: é o desenho que da `077` à `080` já se provou, e sozinha fecha o MVP. Depois US2 e US3,
e US4 por último. Cada fase termina com os testes dela passando.
