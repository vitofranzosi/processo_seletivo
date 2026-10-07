# Tasks: Resultados divulgados por Perfil, etapa e lista

**Input**: Design documents from `specs/062-resultados-por-perfil-etapa-lista/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/bloco-de-resultados.md, quickstart.md

**Tests**: pedidos pela Constituição (V) — cada cenário de aceitação e cada invariante do
[contrato](contracts/bloco-de-resultados.md) tem caso em
`backend/tests/portal/test_resultados_por_perfil.py` (**TR**).

P = `backend/processo_seletivo/portal/`; T = `backend/tests/portal/`.

## Phase 1: Setup

- [X] T001 Conferir o ambiente da worktree: `backend/.env` presente, `uv sync --extra dev`, e `DB_NAME=ps_062` nas rodadas; rodar T`test_historico_de_resultados.py`, T`test_prazo_recursal_publico.py` e T`test_resultado_publico.py` verdes **antes** de mudar qualquer coisa, para separar regressão de adaptação (D-012)

## Phase 2: Foundational — a árvore e os dados dela

**⚠️ Nenhum template muda antes desta fase terminar.**

- [X] T002 Em `backend/processo_seletivo/divulgacao/application/selectors.py`, `_rotulos` devolve também `perfil` (o nome congelado do cabeçalho, vazio quando ausente), com comentário do porquê (D-009)
- [X] T003 Em P`leitura.py`, escrever `resultados_por_perfil(vigentes, conteudo)`: recebe os itens de `historico_publico_do_edital` (já com `recurso_ate`) e o conteúdo vigente, e devolve a árvore de `data-model.md` — Perfis na ordem de `profiles` (ausentes por último, pela publicação mais recente), etapas por `marco_codigo` e nome, listas com o recorte sem lista primeiro e depois `competitionModalities` do Perfil (desconhecidas por último, pelo nome), nome do Perfil vigente com o congelado de reserva, título da etapa da vigente mais recente, histórico por etapa agrupado na ordem das listas e mais recente primeiro (D-005, D-008, D-009, D-010)
- [X] T004 Testes de unidade de `resultados_por_perfil` em TR, com publicações em memória (`SimpleNamespace`), sem banco: as três ordens, o Perfil ausente do vigente, a lista desconhecida, o recorte sem lista primeiro, a etapa sem histórico com `anteriores` vazio, o título da etapa vindo da vigente mais recente

**Checkpoint**: a árvore existe e está provada; a página ainda é a antiga.

## Phase 3: User Story 1 — Achar o resultado da própria vaga (P1) 🎯 MVP

**Goal**: FR-1148 a FR-1154, UX-151, UX-152. **Independent Test**: Edital com dois Perfis e três listas cada; um grupo por Perfil na ordem da seção Vagas, a etapa, as três listas com natureza e data e o nome da lista como link.

- [X] T005 [US1] Em P`views.py`, na view `selecao`, montar `contexto["resultados_por_perfil"]` com `leitura.resultados_por_perfil` depois do laço que preenche `recurso_ate`; manter `resultados_divulgados` (o `if` do bloco o usa)
- [X] T006 [US1] Em P`templates/portal/selecao.html`, reescrever o bloco conforme o contrato: `h2` → `div.resultados-do-perfil` com `h3` → `div.resultados-da-etapa` com `h4` → `ul.listas-da-etapa` de `li.lista-divulgada`; o link com o nome da lista e `span.oculto` " — etapa — Perfil"; `span.meta` com natureza e data; atualizar o comentário de template (FR-050 da `017`, `FR-772`, decisão recebida 1)
- [X] T007 [US1] Em P`templates/portal/base.html`, acrescentar `.oculto` (a mesma regra de `interface/base.html`) e as regras de `.resultados-do-perfil`, `.resultados-da-etapa`, `.listas-da-etapa` e `.lista-divulgada`, substituindo as de `.resultados-divulgados` que deixarem de ter uso; `flex-wrap` na linha da lista para a meta quebrar a 375 px (UX-153)
- [X] T008 [US1] Testes em TR, com dois Perfis declarados no rascunho e publicações gravadas como em T`test_historico_de_resultados.py`: um grupo por Perfil na ordem da seção Vagas; nenhum resultado de um Perfil no grupo do outro; a etapa como `h4`; três listas com natureza e data na linha; "Ampla concorrência" para o recorte sem lista; os dois links "Ampla concorrência" com nomes acessíveis distintos, cada um começando pelo texto visível (US1 cenários 1–5, SC-443, SC-444)
- [X] T009 [US1] Teste em TR de hierarquia de títulos do bloco sem saltos (`h2` → `h3` → `h4`) (UX-151)

**Checkpoint**: a árvore aparece; o histórico e o convite ainda faltam.

## Phase 4: User Story 2 — Listas em fases diferentes (P1)

**Goal**: FR-1155, FR-1156. **Independent Test**: duas listas no definitivo e uma no preliminar com prazo aberto.

- [X] T010 [US2] Em P`templates/portal/selecao.html`, o `span.prazo-recursal` dentro de `li.lista-divulgada`, nas mesmas condições de hoje (`FR-770`, `FR-771`)
- [X] T011 [US2] Testes em TR: cada lista diz a sua natureza; `h3` e `h4` não contêm natureza nem data, mesmo com todas as listas coincidentes; o prazo só na lista que o tem (US2 cenários 1–2, SC-445)
- [X] T012 [US2] Adaptar T`test_prazo_recursal_publico.py` à marcação nova (localizar `section.resultados` em vez de `ul.resultados-divulgados`), mantendo cada asserção, inclusive a de uma consulta só à tabela de publicações (D-011, D-012)

## Phase 5: User Story 3 — O histórico, consolidado e separado por lista (P2)

**Goal**: FR-1157 a FR-1159. **Independent Test**: três listas com preliminar sucedido; um bloco por etapa.

- [X] T013 [US3] Em P`templates/portal/selecao.html`, um `details.publicacoes-anteriores` por etapa com sucedida, resumo com o total da etapa, itens com o nome da lista como texto do link, `span.oculto` " — natureza, publicado em data — etapa — Perfil" e `span.meta` com natureza, data e "sucedido"
- [X] T014 [US3] Testes em TR: um bloco por etapa com a contagem total; cada item com lista, natureza, data, "sucedido" e link; nenhuma publicação de uma lista sob outra; etapa sem sucedida sem bloco (US3 cenários 1–4, SC-446)
- [X] T015 [US3] Adaptar T`test_historico_de_resultados.py` e T`test_resultado_publico.py` à marcação nova, mantendo cada garantia: vigente fora do histórico, ordem da cadeia de três, histórico da PPI fora do da PcD, nenhum identificador de ator, e a regressão do #255 lendo o nome acessível (D-012)

## Phase 6: User Story 4 — Ir direto à situação individual (P2)

**Goal**: FR-1160 a FR-1163. **Independent Test**: sem sessão, com sessão e uma inscrição enviada, com sessão sem inscrição enviada.

- [X] T016 [US4] Em P`views.py`, `_de_volta_a_vaga` reconhece também `portal:selecao` e devolve a página do Edital com `#resultados-titulo`; atualizar a docstring com o porquê (página pública, GET, sem ato); e em `_entrar` o desvio para "Seus dados" por falta de núcleo passa a valer só quando o destino é uma vaga (D-007, FR-1161)
- [X] T017 [US4] Em P`views.py`, na view `selecao`, montar `contexto["convite_da_situacao"]` a partir de `iniciadas` já lidas: sem sessão → acesso com `destino` na página do Edital; uma enviada → o acompanhamento da inscrição (corrigido na verificação, ver `verificacao.md` §3); duas ou mais → a lista; nenhuma → `None` (D-003 da spec)
- [X] T018 [US4] Em P`templates/portal/selecao.html` e P`templates/portal/base.html`, o `aside.convite-da-situacao` depois dos grupos, com o texto da decisão recebida 6 e a regra de estilo dele
- [X] T019 [US4] Testes em TR: os quatro casos da tabela do data-model; o convite fora de qualquer `div.resultados-do-perfil`; a volta do acesso com `destino` da página do Edital leva a ela na âncora, sem passar por "Seus dados" quando falta o núcleo, enquanto o `destino` de vaga continua passando; um `destino` de outra rota continua indo para "Minhas inscrições" (US4 cenários 1–4, SC-447)

## Phase 7: Polish & Cross-Cutting

- [X] T020 Teste em TR do custo constante: a mesma página com N e 2N publicações faz o mesmo número de consultas (SC-448, D-011)
- [X] T021 Teste em TR de que o destaque continua com o Edital encerrado e some com inscrições abertas, e de que a página de cada publicação não mudou (FR-1164, FR-1165)
- [X] T022 Verificar no navegador conforme o [quickstart](quickstart.md) §3, a 1280 × 900 e a 375 px (largura de rolagem do documento = 375; natureza e data quebrando), e a ida e volta pelo convite; registrar as medidas em `specs/062-resultados-por-perfil-etapa-lista/verificacao.md` (UX-153, UX-154, SC-449)
- [X] T023 Escrever `specs/062-resultados-por-perfil-etapa-lista/rastreabilidade.md` com uma linha para cada FR-, SC- e UX- da spec: onde entrou e o teste que o prende
- [ ] T024 `cd backend && make lint check test-pg DB_NAME=ps_062`, depois de mesclar `origin/main`; registrar o total em `verificacao.md` da feature

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T004)** → US1 (T005–T009).
- **US2** e **US3** dependem de US1 (o bloco precisa existir); são independentes entre si, mas mexem em `selecao.html` — em sequência, não em paralelo.
- **US4** depende só de T005 (a view); T016 é independente do template e pode correr junto de US2/US3.
- **Polish** depois de todas as histórias; T023 pode começar quando os testes tiverem nome.

## Parallel Opportunities

- T002 e o esqueleto de T004 tocam arquivos diferentes.
- T016 (`_de_volta_a_vaga`) em paralelo com T010–T015.
- T012 e T015 adaptam arquivos de teste diferentes.

## Implementation Strategy

MVP = Phases 1–3: a árvore por Perfil, etapa e lista com os nomes acessíveis. Depois as fases
seguem a ordem das prioridades: US2 (P1), US3 e US4 (P2). A suíte completa roda uma vez no fim
(T024); antes disso, só os arquivos de teste do portal tocados pela feature e as guardas de acessibilidade do portal.
