# Tasks: O caminho do candidato até a convocação e o Requerimento de Matrícula

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec — a `SC-426` e a `SC-427` são verificadas por teste, e a Constituição
(Princípio V) exige cobertura de autorização. Cada história escreve o teste antes da tela.

**Caminhos**: relativos à raiz do repositório. `backend/` é o projeto Django.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US4)

---

## Phase 1: Setup

- [X] T001 Preparar a worktree: `uv sync --extra dev` em `backend/`, `.env` copiado do principal, e conferir `manage.py migrate --check` contra o banco de desenvolvimento
- [X] T002 Medir o estado de partida e guardar em `specs/059-acesso-a-convocacao/verificacao.md`: consultas da lista em `backend/tests/performance/test_area_do_candidato.py` (com 1 e 2 inscrições) e, no seed, `document.elementFromPoint` no centro de "Acompanhar" em "Minhas inscrições" (hipótese da `D-010`)

---

## Phase 2: Foundational (bloqueia todas as histórias)

**Propósito**: a regra de vigência única (`D-001`, `FR-1100`), que a lista, o acompanhamento e a tela da convocação passam a ler.

- [X] T003 [P] Teste do seletor `vigentes_por_inscricao` em `backend/tests/integration/convocacao/test_vigentes_por_inscricao.py`: devolve a vigente mais recente por inscrição; a sucessora no lugar da sucedida; inscrição sem convocação ausente do dicionário; lista vazia sem consulta; número de consultas igual com 1 e 3 inscrições convocadas (cenário `montar_cenario_da_convocacao`)
- [X] T004 Implementar `vigentes_por_inscricao(inscricao_ids)` em `backend/processo_seletivo/convocacao/application/selectors.py`, com `sucessoras__isnull=True`, ordem `-criado_em` e `prefetch_related("desfechos", "comunicacoes")`; docstring dizendo por que é a regra da tela e não `chamada_em_aberto`
- [X] T005 Reescrever a busca da `convocacao` em `backend/processo_seletivo/portal/views.py` sobre `vigentes_por_inscricao([registro.id])`, sem mudar o que a tela mostra; `backend/tests/interface/test_portal_convocacao.py` continua verde sem edição
- [X] T006 Função de tradução `_convocacao_para_a_tela(chamada, agora)` em `backend/processo_seletivo/portal/views.py`: devolve `convocacao`, `desfecho`, `enviada_em`, `estado`, `aberta` — ou `None` — a partir de `desfecho_de`, `envio_de` e `estado_de`; a view `convocacao` passa a usá-la

**Checkpoint**: uma regra de vigência só, consumida pela tela que já existia.

---

## Phase 3: User Story 1 — Em "Minhas inscrições", a convocação aberta aparece e leva à tela dela (P1) 🎯 MVP

**Goal**: indicação de convocação aberta, "Ver convocação" como ação principal, "Acompanhar" secundária, nota da concluída (`FR-1089` a `FR-1092`, `UX-145`, `UX-146`).

**Independent Test**: duas inscrições enviadas, uma convocada; a lista mostra a indicação e "Ver convocação" só na convocada, e o link leva a `portal:convocacao` dela.

### Tests

- [X] T007 [P] [US1] Testes de tela em `backend/tests/interface/test_portal_caminho_da_convocacao.py` (classe da lista): convocação aberta → "Convocação aberta" + "Ver convocação" com `href` da convocação daquela inscrição + "Acompanhar" no mesmo item; antes do envio da comunicação → também indicada; sem convocação → "Acompanhar" e nenhuma indicação; com desfecho → "Convocação: <espécie>" e ação principal "Acompanhar"; vencimento decorrido sem desfecho → continua aberta; a mensagem enviada ao convocar pela gestão contém o endereço de `portal:inscricoes` (`FR-1104`, achado C1 do analyze)
- [X] T008 [P] [US1] Orçamento em `backend/tests/performance/test_lista_com_convocacao.py`: a lista lê as convocações numa consulta só (com `IN`) e faz **zero** consultas às tabelas do requerimento; no seletor (`test_vigentes_por_inscricao.py`), o custo é o mesmo com uma e com duas convocadas (`SC-426`). *Nota da implementação: a garantia é por composição (`D-002`) — custo fixo + seletor constante + **zero** consultas por item em tabela nenhuma (`test_o_item_da_lista_nao_consulta_nada_em_tabela_nenhuma`, conferido reprovando com uma consulta por item introduzida de propósito). Cinco certames num teste são possíveis, mas as fixtures de hoje colidem no segundo; a composição prova o caso geral sem depender delas.*

### Implementation

- [X] T009 [US1] Em `backend/processo_seletivo/portal/views.py`: `inscricoes` pede `vigentes_por_inscricao` só para as inscrições enviadas (nenhuma consulta quando não há); `_item_da_lista` recebe a convocação e devolve `convocacao_aberta`, `convocacao_concluida` (rótulo do desfecho) e `acao` "Ver convocação" quando aberta; docstring atualizada com a `D-003`
- [X] T010 [US1] Em `backend/processo_seletivo/portal/templates/portal/inscricoes.html`: linha de situação "Convocação aberta" com símbolo; ação principal para `portal:convocacao`; "Acompanhar" como link secundário; nota discreta da concluída; comentário com o porquê (`D-003`, `D-004`)
- [X] T011 [US1] Em `backend/processo_seletivo/portal/templates/portal/base.html`: regra para cada classe nova da lista e para as ações do cartão ficarem acima do título esticado (`position:relative; z-index`), com comentário da `D-010`; `test_acessibilidade` verde

**Checkpoint**: a mensagem leva à lista, e a lista leva à convocação em um clique (`SC-424`).

---

## Phase 4: User Story 2 — O Requerimento de Matrícula pedido na convocação tem porta (P1)

**Goal**: o chamado ao requerimento na tela da convocação e na seção do acompanhamento, traduzindo o estado de leitura da `029` (`FR-1096` a `FR-1099`, `D-006`, `D-007`).

**Independent Test**: Edital *na convocação*, pessoa convocada → "Preencher Requerimento de Matrícula" na convocação; depois do envio → "Conferir o Requerimento de Matrícula enviado".

### Tests

- [X] T012 [P] [US2] Testes em `backend/tests/interface/test_portal_caminho_da_convocacao.py` (classe do requerimento), com o cenário de `test_portal_sucessao.py` (`declarar("AT_CALL")`): convocada sem rascunho → "Preencher Requerimento de Matrícula" com `href` de `portal:requerimento`; com rascunho → mesmo chamado; enviado → "Conferir o Requerimento de Matrícula enviado" e nenhum "Preencher"; enviado e convocação desfechada → ainda "Conferir"; desfechada sem envio → nenhum chamado; Edital sem requerimento → nenhum chamado

### Implementation

- [X] T013 [P] [US2] Parcial novo `backend/processo_seletivo/portal/templates/portal/_chamado_do_requerimento.html`, com a tabela da `D-007` e comentário do porquê; estados por `requerimento_nomes` (sem string solta no template)
- [X] T014 [US2] Em `backend/processo_seletivo/portal/views.py`: helper `_requerimento_da_convocacao(registro, conteudo)` que chama `preencher_requerimento.apurar` e devolve o estado de leitura, **só** chamado quando há convocação vigente; a view `convocacao` passa a enviar `requerimento` ao template
- [X] T015 [US2] Em `backend/processo_seletivo/portal/templates/portal/convocacao.html`: incluir o parcial abaixo da seção da chamada e acima de "Voltar ao acompanhamento"

**Checkpoint**: quem é convocado num Edital *na convocação* chega ao requerimento em dois cliques a partir da lista (`SC-425`).

---

## Phase 5: User Story 3 — O acompanhamento apresenta a convocação, aberta ou concluída (P2)

**Goal**: seção "Convocação" no acompanhamento, com situação, "Ver convocação" e o chamado (`FR-1093` a `FR-1095`, `FR-1103`).

**Independent Test**: com a convocação aberta e depois desfechada, o acompanhamento mostra a seção nos dois estados; sem convocação, não mostra.

### Tests

- [X] T016 [P] [US3] Testes em `backend/tests/interface/test_portal_caminho_da_convocacao.py` (classe do acompanhamento): seção com espécie, prazo e "Ver convocação"; os quatro textos de situação (`contracts/telas.md`); sucessão → mostra a sucessora e não o vencimento antigo; sem convocação → sem seção; abrir lista e acompanhamento não grava `CONVOCACAO_LER` e abrir a convocação grava uma (`D-008`); `test_o_acompanhamento_nao_toca_a_feature` da `029` continua verde sem edição; a lista e o acompanhamento com convocação cabem em 375 px, no molde de `test_a_tela_cabe_em_375_px` da `019` (`UX-146`, achado C2)

### Implementation

- [X] T017 [P] [US3] Parcial novo `backend/processo_seletivo/portal/templates/portal/_convocacao_da_inscricao.html`: título "Convocação", `dl` com espécie, envio e prazo, a situação nos quatro casos com os termos da tela da convocação, "Ver convocação", e o `_chamado_do_requerimento.html`
- [X] T018 [US3] Em `backend/processo_seletivo/portal/views.py`, `acompanhamento`: `vigentes_por_inscricao([registro.id])`, `_convocacao_para_a_tela`, e o estado do requerimento só com convocação vigente (`D-006`)
- [X] T019 [US3] Em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html`: incluir a seção depois do aviso de Retificação e antes de "Sua participação", com comentário da `D-005`; a página já tem mais de uma `.principal` (Recorrer, Ver o que enviei) — a regra de uma ação principal é do item da lista (achado I1)

**Checkpoint**: o estado concluído fica consultável sem depender da mensagem.

---

## Phase 6: User Story 4 — Ninguém alcança a convocação ou o requerimento de outra pessoa (P1)

**Goal**: a recusa uniforme preservada nos caminhos novos (`FR-1101`, `FR-1102`, `SC-427`).

**Independent Test**: Maria e João convocados; nada de João na lista e no acompanhamento de Maria; as quatro rotas de João respondem a Maria como inscrição inexistente.

- [X] T020 [P] [US4] Testes em `backend/tests/authorization/test_convocacao_alheia.py`: a lista e o acompanhamento de Maria não contêm o identificador da inscrição de João nem o `href` da convocação ou do requerimento dele; `acompanhamento`, `convocacao`, `requerimento` e `requerimento-anterior` da inscrição de João respondem a Maria com o mesmo status **e** o mesmo corpo que um UUID inexistente; sem sessão, as quatro rotas respondem como hoje; nenhum `href` novo carrega CPF, nome ou e-mail
- [X] T021 [US4] Se algum teste da T020 reprovar, corrigir a view em `backend/processo_seletivo/portal/views.py` pela titularidade (`exigir_titularidade`), nunca por filtro de template

---

## Phase 7: Polish & Cross-Cutting

- [X] T022 [P] Acrescentar `_convocacao_da_inscricao.html` e `_chamado_do_requerimento.html` a `DA_019` em `backend/tests/test_vocabulario_da_convocacao.py` (`D-011`, `UX-147`)
- [X] T023 [P] Matriz `specs/059-acesso-a-convocacao/rastreabilidade.md`: cada FR-, SC- e UX- da spec com o teste que o prende; a `FR-1105` mapeia à revisão do diff — nenhuma rota em `portal/urls.py`, nenhum arquivo em `interface/`, nenhuma migration (achado C3)
- [X] T024 `cd backend && make lint check test-pg DB_NAME=test_ps_059` — `ruff check` **e** `ruff format --check`; total e pulados em `specs/059-acesso-a-convocacao/verificacao.md`, comparados aos 9129/11 do `CLAUDE.md`
- [X] T025 Verificação no navegador pelo `quickstart.md` §2: entrada `acesso-059` acrescentada ao `.claude/launch.json`, banco `ps_demo_059` semeado, lista → convocação → requerimento, acompanhamento, 375 px sem rolagem horizontal, `elementFromPoint` em "Ver convocação" e "Acompanhar" (`D-010`); capturas e medidas em `verificacao.md`, inclusive o antes e o depois de "Acompanhar" e "Continuar inscrição" de quem não foi convocado (achado U1)
- [X] T026 Atualizar os números da suíte no `CLAUDE.md` se mudarem, com a repartição dos pulados

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003–T006)** → histórias.
- **US1 (T007–T011)** depende só da fundação; é o MVP.
- **US2 (T012–T015)** depende da fundação; o chamado entra na tela da convocação independentemente da US1.
- **US3 (T016–T019)** depende da US2 (inclui o parcial do chamado, T013).
- **US4 (T020–T021)** depende das telas da US1 e da US3 estarem prontas para que a ausência seja provada nelas.
- **Polish** depois de tudo; T024 roda sozinha (editar durante a suíte falseia o resultado).

## Parallel Opportunities

- T003 (teste do seletor) em paralelo com o preparo de T002.
- Dentro da US1: T007 e T008 juntos.
- US2: T012 e T013 juntos.
- US3: T016 e T017 juntos.
- T022 e T023 juntos.

## Implementation Strategy

1. **MVP**: fundação + US1 — a lista indica e leva à convocação; já resolve o achado principal e
   faz a mensagem chegar a algum lugar.
2. **US2**: o requerimento ganha porta — a etapa que decide a vaga deixa de ser inalcançável.
3. **US3**: o acompanhamento fala de convocação; os estados concluídos ficam consultáveis.
4. **US4**: a recusa uniforme provada nos caminhos novos.
5. **Polish**: varredura, matriz, suíte, navegador.
