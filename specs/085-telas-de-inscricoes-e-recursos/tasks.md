# Tasks: As telas de inscrições e de recursos, sétimo incremento

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco do inventário próprio (`ps_inventario_085`, cópia do `ps_inventario_080`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_085`) e `uv sync --extra dev --extra assistente`; nenhuma entrada no `.claude/launch.json`
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `cf6d7372`, guardado em `depois-da-085/antes/`; comparado com `depois-da-080/` — nenhuma variante com medida diferente
- [x] T003 As consultas de cada tela medidas antes da mudança: Inscrições 15, Inscrição recebida 6, Recursos 5, Recurso 8 (R-002)

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho existe desde a `077`, e o parcial do produto desde a `078`.

## Phase 3: User Story 1 — onde estou, dito uma vez só (P1) 🎯 MVP

**Goal**: a trilha no cabeçalho nas quatro telas, passando pelo Processo.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título.

- [x] T004 [P] [US1] `inscricoes.html`, `inscricao_detalhe.html`, `recursos.html`, `recurso.html`: a trilha do Edital com a tela no fim, no bloco `caminho_do_contexto` (R-001; FR-1910, FR-1911, FR-1912)
- [x] T005 [US1] `inscricoes/application/consulta.py`: o Processo na mesma leitura do Edital, em `_edital_no_escopo` e em `inscricao_para_consulta` (R-002; FR-1917)
- [x] T006 [US1] Testes em `tests/interface/test_telas_de_inscricoes_e_recursos.py`: a trilha única no cabeçalho e o conteúdo pelo título nas quatro telas e no rascunho; nenhuma consulta só pelo Processo; cada nível do Recurso abre para quem julga; nada da pessoa além do protocolo; o Recurso sem caminho para a inscrição de quem só julga; a recusa com o cabeçalho da `076` (FR-1910 a FR-1915, FR-1917, FR-1920, SC-752 a SC-754)
- [x] T007 [US1] Conferir que o teste de consulta reprova sem a junção — retirada a mudança de T005, as duas telas das inscrições falham (R-002)

## Phase 4: User Story 2 — sem inscrição, o estado vazio (P2)

- [x] T008 [US2] `inscricoes.html`: "Nenhuma inscrição recebida até agora." como `p.vazio`, com o comentário do porquê (R-003; FR-1918)
- [x] T009 [US2] Testes: o estado vazio sem inscrição; a advertência dos rascunhos continua aviso (FR-1918)

## Phase 5: User Story 3 — os rascunhos como região (P3)

- [x] T010 [US3] `inscricoes.html`: a `section aria-labelledby="em-preenchimento"` em volta do título, da advertência, da tabela e da paginação dos rascunhos (R-004; FR-1919)
- [x] T011 [US3] Teste: a região com o título, a advertência e a tabela (FR-1919)

## Phase 6: Polish & verificação

- [x] T012 Os guardiões vizinhos sem emenda — inscrições recebidas e em escala, proveniência e instrução do recurso, julgamento, consulta administrativa, polish da 055, 057 e 058, acessibilidade, estáticos —; o da `076` que usava as Inscrições como tela abaixo do Edital passa aos Avisos do Edital, achado pela suíte completa (R-005)
- [x] T013 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel com o de antes; as capturas das cinco variantes do escopo, antes e depois; a seção "Depois da 085" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1916, FR-1921, SC-750, SC-751)
- [x] T014 O percurso do quickstart no navegador, pelo teclado: do Processo ao Edital, às Inscrições (e às de um Edital sem inscrição, no estado vazio), à inscrição de Ana Silva e de volta pela trilha, com foco visível; como `inventario.julgadora`, aos Recursos e ao recurso pendente, sem caminho para a inscrição; a 375 px, a trilha do Recurso em três linhas dentro do cabeçalho e nenhuma rolagem lateral (FR-1916, SC-756)
- [x] T015 `make lint check` e `make test-pg DB_NAME=ps_085` (FR-1922, SC-755)
- [x] T016 `rastreabilidade.md` com cada FR e SC; a linha da `085` no README

## Dependencies

T004 e T005 primeiro; T008 e T010 tocam o mesmo template depois de T004. Os testes de cada fase depois
da mudança dela. T012–T016 depois de tudo.

## Implementation Strategy

US1 primeiro: é o desenho que a `077` à `080` já provaram, e sozinha fecha o MVP. Depois US2 e US3,
que só tocam as Inscrições. Cada fase termina com os testes dela passando.
