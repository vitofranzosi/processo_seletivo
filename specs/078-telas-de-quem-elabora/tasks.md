# Tasks: As telas de quem elabora, segundo incremento

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`.

## Phase 1: Setup

- [ ] T001 Banco de teste próprio (`DB_NAME=ps_078`), o `ps_inventario_telas` em dia com as migrations e `uv sync --extra dev --extra assistente`
- [ ] T002 Inventário de antes, nos dois estados da barra, sobre `a41b67c0`, e a sonda das causas latentes (R-001); medir o teto da distribuição antes (`tests/performance/test_escala_da_mesa.py`)

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho já existe desde a `077`.

## Phase 3: User Story 1 — nenhuma tela volta a rolar pelas mesmas causas (P1) 🎯 MVP

**Goal**: as duas causas corrigidas na folha comum, sem as regras pontuais da `077`.

**Independent Test**: a folha comum tem as duas regras; as três telas não as têm; o inventário dá `scrollWidth` 375 nelas e nenhuma outra variante muda.

- [ ] T003 [US1] `processo_seletivo/interface/templates/interface/base.html`: `position:relative` para as molduras que rolam, com `.distribuicao-moldura` no meio do seletor, e `min-width:0` na regra de `fieldset` (R-002; FR-1760, FR-1761)
- [ ] T004 [P] [US1] Tirar as regras pontuais de `conclusoes.html`, `reaproveitar.html` e `compor_anexos.html`, com os comentários que as explicavam (FR-1762)
- [ ] T005 [US1] Testes em `tests/interface/test_telas_de_quem_elabora.py` (as duas regras na folha comum, fora de `@media`; as três fora das telas) e `tests/interface/test_telas_de_uso_diario.py::test_cada_correcao_vale_so_na_sua_tela` só com o sorteio (FR-1760, FR-1761, FR-1762, SC-680)

## Phase 4: User Story 2 — o que fazer, antes do resto (P1)

**Goal**: "O que fazer agora" primeiro no Processo e no Edital.

**Independent Test**: a região "O que fazer agora" vem antes das demais regiões de conteúdo, nas duas telas.

- [ ] T006 [P] [US2] `processo_detalhe.html`: a `div.colunas` antes de "Onde cada Edital está", com "O que fazer agora" em primeiro (R-003; FR-1764, FR-1766)
- [ ] T007 [P] [US2] `detalhe.html`: "O que fazer agora" antes de "Quem atuou", na `div.colunas.ao-topo` (R-003; FR-1765, FR-1766)
- [ ] T008 [US2] Testes da ordem das regiões nas duas telas em `tests/interface/test_telas_de_quem_elabora.py` (FR-1764, FR-1765, FR-1766, SC-683)

## Phase 5: User Story 3 — onde estou, dito uma vez só (P2)

**Goal**: a trilha no cabeçalho nas telas de quem elabora.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título.

- [ ] T009 [P] [US3] `processo_detalhe.html` e `detalhe.html`: a trilha sai do conteúdo e vai ao bloco `caminho_do_contexto` (R-004; FR-1767, FR-1768)
- [ ] T010 [P] [US3] `compor_base.html`: a trilha no bloco, com o Processo entre a seção e o Edital (R-004; FR-1767, FR-1768)
- [ ] T011 [US3] Testes da trilha nas três telas e nas nove etapas da composição em `tests/interface/test_telas_de_quem_elabora.py`; `tests/interface/test_shell_da_gestao.py::test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha` passa a usar as inscrições recebidas (FR-1767, FR-1768, FR-1769, SC-684)

## Phase 6: User Story 4 — os Editais do Processo como a lista os mostra (P3)

**Goal**: a tabela dos Editais e o estado vazio comum.

**Independent Test**: uma linha por Edital, com os mesmos links e pastilhas; sem Edital, o estado vazio.

- [ ] T012 [US4] `processo_detalhe.html`: os Editais na tabela da lista, em `div.tabela-rolavel`; sem Edital, `p.vazio` com "Nenhum Edital neste Processo." (R-005; FR-1771, FR-1772, FR-1773)
- [ ] T013 [US4] Testes da tabela e do estado vazio em `tests/interface/test_telas_de_quem_elabora.py` (FR-1771, FR-1772)

## Phase 7: Polish & verificação

- [ ] T014 `make lint check` e `make test-pg DB_NAME=ps_078`; o teto da distribuição medido de novo (FR-1775, SC-685)
- [ ] T015 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-078/`, comparado por `comparar.py` com `depois-da-077/`, e as capturas comparadas pixel a pixel com as de antes; as capturas das telas que mudaram; a seção "Depois da 078" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1762, FR-1763, FR-1770, FR-1773, FR-1774, SC-681, SC-682)
- [ ] T016 O percurso do quickstart no navegador, a 1280 e a 375 px, só pelo teclado (FR-1770, SC-686)
- [ ] T017 `rastreabilidade.md` com cada FR e SC; a `FR-1745` e a `FR-1748` da `077` anotadas como emendadas, na spec e na rastreabilidade dela

## Dependencies

US1 é independente das demais. US2, US3 e US4 tocam `processo_detalhe.html` e devem ir em sequência
nesse arquivo (T006 → T009 → T012); `detalhe.html` e `compor_base.html` são independentes entre si.
T014–T016 depois de tudo.

## Implementation Strategy

US1 primeiro: é a correção de causa, independente das telas, e o inventário a prova sozinho. Depois
US2 e US3 juntas, por arquivo, e US4 por último. Cada fase termina com os testes dela passando.
