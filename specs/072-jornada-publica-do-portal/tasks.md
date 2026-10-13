---
description: "Tarefas da 072 — a jornada pública do portal"
---

# Tasks: A jornada pública do portal — encontrar, começar, preparar e acompanhar

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/telas-publicas.md](contracts/telas-publicas.md), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec (SC-600 a SC-607) e pelo plano — cada história traz os seus, escritos
antes da implementação dela.

**Caminhos**: relativos a `backend/` quando começam por `processo_seletivo/` ou `tests/`.

## Phase 1: Setup

- [X] T001 Conferir o ambiente da worktree: `uv sync --extra dev`, `manage.py migrate --check` (sem pipe) contra `ps_ux_conversao`, e a entrada temporária `ux-conversao` (porta 8077) em `.claude/launch.json`, a desfazer no fim (T046)

## Phase 2: Foundational — as leituras que mais de uma história usa

- [X] T002 Acrescentar `historico_publico_dos_editais(editais) -> {edital_id: vigentes}` em `processo_seletivo/divulgacao/application/selectors.py`, com o corpo de `historico_publico_do_edital` aplicado a `edital__in` (cadeia ligada em memória por Edital), e fazer a função de um Edital delegar a ela (research T-001)
- [X] T003 Extrair de `views.selecao` para `processo_seletivo/portal/leitura.py` a função que acrescenta `recurso_ate` aos vigentes (`conteudos_citados` + `janela_da_publicacao_divulgada` + `agora <= fim`), recebendo `vigentes`, o conteúdo vigente de cada Edital e `agora`; `views.selecao` passa a chamá-la em `processo_seletivo/portal/views.py`
- [X] T004 [P] Acrescentar em `processo_seletivo/portal/leitura.py` `quantidade_da_oferta(vagas, tipo_de_reserva)` (FR-1607) e `os_primeiros(itens, teto, termo, chave)` — itens até o teto, quantos sobram, e os que casam com o termo da busca primeiro (FR-1608 a FR-1610) — reusando `RESERVA` e `dobrar`
- [X] T005 [P] Testes sem banco das duas funções em `tests/portal/test_oferta_e_teto.py`: singular e plural, reserva com e sem vaga, sem reserva e sem vaga (vazio), teto exato, "e mais N", termo que casa além do teto vem primeiro
- [X] T006 Rodar sem alteração os testes da página da seleção que cobrem resultados e prazo (`tests/portal/test_prazo_recursal_publico.py`, `tests/portal/test_resultados_por_perfil.py`, `tests/integration/portal/test_historico_publico.py`, `tests/integration/portal/test_detalhe_selecao.py`) — prova de que T002 e T003 não mudaram a página

**Checkpoint**: leitura em lote e regra de prazo num lugar só; página da seleção inalterada.

## Phase 3: User Story 1 — Encontrar pelo celular (P1) 🎯 MVP

**Goal**: busca à vista, filtros recolhidos, cartão titulado pelo Edital com oferta por Perfil e lugar.

**Independent Test**: vitrine do seed medida pelo script da auditoria nas telas do SC-600; leitura dos cartões.

- [ ] T007 [P] [US1] Testes em `tests/integration/portal/test_vitrine.py`: `<title>` e `h1` "Processos seletivos" com a sigla da unidade; linha de contagem de abertas (uma, várias, nenhuma); texto do link = título do Edital, e do Processo sem ele; oferta por Perfil com quantidade e teto de 3; lugares únicos com teto; "01/2026" não repetido quando está no título; sigla "Cefor"; ordem fixa dos blocos no cartão (FR-1604 a FR-1609, FR-1611, FR-1612, FR-1614)
- [ ] T008 [P] [US1] Testes em `tests/integration/portal/test_consulta_da_vitrine.py`: busca casa com lugar; com busca, o Perfil e o lugar casados vêm primeiro; `<details class="mais-filtros">` sem `open` sem consulta, com `open` quando unidade, situação, Perfil ou ordem não padrão estão aplicados, sem `open` só com busca; estado vazio numa frase com caminho para as abertas e para o catálogo (FR-1600, FR-1601, FR-1610, FR-1613)
- [ ] T009 [US1] Em `processo_seletivo/portal/views.py` (`vitrine`, `_selecao_da_vitrine`): sigla da unidade por uma leitura de `Unidade` para a página (research T-006); oferta por Perfil e lugares com `os_primeiros`; marca de número já presente no título (`NN/AAAA`); contagem de abertas; título com a sigla quando o catálogo tem uma unidade
- [ ] T010 [US1] Em `processo_seletivo/portal/leitura.py`: `_texto_do_cartao` alcança os lugares (FR-1610); `consulta_da_vitrine` devolve se algum filtro recolhido está aplicado (FR-1601)
- [ ] T011 [US1] Reescrever `processo_seletivo/portal/templates/portal/_cartao_da_selecao.html` na ordem do contrato: marca · título do Edital (link único) · oferta · lugares · período · acompanhamento (vazio até a US5) · convite · dados de apoio
- [ ] T012 [US1] Reescrever `processo_seletivo/portal/templates/portal/_consulta.html`: busca e botão "Filtrar" fora; `<details class="mais-filtros">` com `<summary>Mais filtros e ordenação</summary>` e os quatro controles; `open` vindo do servidor; `<script>` síncrono de `portal/consulta.js` logo depois do `<details>` (FR-1600, FR-1601, FR-1603)
- [ ] T013 [P] [US1] Criar `processo_seletivo/portal/static/portal/consulta.js`: em tela larga (`matchMedia`), abrir o grupo e marcar a classe que esconde o `summary`; acompanhar a mudança de largura (FR-1602, research T-002)
- [ ] T014 [US1] Em `processo_seletivo/portal/templates/portal/vitrine.html`: bloco `titulo` "Processos seletivos", `h1` com a sigla, linha de contagem, subtítulo novo, estado vazio numa frase (FR-1611 a FR-1613)
- [ ] T015 [US1] Regras em `processo_seletivo/portal/templates/portal/base.html` para `.mais-filtros` (celular e tela larga), oferta, lugares e dados de apoio do cartão — cada classe nova com regra, CSS em linhas separadas, comentário sem vocabulário proibido

**Checkpoint**: US1 verificável sozinha no seed.

## Phase 4: User Story 5 — Acompanhar pela vitrine (P1)

**Goal**: resultado e prazo de recurso no cartão, pela regra D-004.

**Independent Test**: cartões do Edital 51/2026 e 26/2026 do seed; cenários de 1, 3 e 5 vigentes nos testes.

- [ ] T016 [P] [US5] Testes sem banco em `tests/portal/test_resumo_do_acompanhamento.py`, com itens em `SimpleNamespace`: um vigente com e sem prazo; vários com prazo único igual; parcial ("1 de 3"); términos diferentes ("2 de 2", primeiro término entre os abertos); todos encerrados; natureza comum e mista; lista vazia → `None` (FR-1629 a FR-1633, D-004)
- [ ] T017 [P] [US5] Testes com banco em `tests/portal/test_acompanhamento_na_vitrine.py`, reaproveitando `montar`, `depois_do_prazo` e `consultas` de `tests/portal/test_prazo_recursal_publico.py`: cartão diz o mesmo que a página no mesmo instante; sucedida fora de N, M e da data; prazo encerrado some; sem resultado nada; convite certo; **orçamento**: vitrine com 1 e com 4 Editais com resultado faz o mesmo número de consultas (FR-1634, FR-1635, SC-604)
- [ ] T017b [P] [US5] Estender `tests/integration/portal/test_leitura_sem_escrita.py`: a vitrine com resultados e a seleção, abertas por anônimo, não gravam nada; com sessão, a única escrita admitida é a da própria sessão ao remover a chave de volta (FR-1637, SC-606)
- [ ] T018 [US5] Função pura `resumo_do_acompanhamento(vigentes)` em `processo_seletivo/portal/leitura.py` (data-model, "Resumo do acompanhamento")
- [ ] T019 [US5] Em `processo_seletivo/portal/views.py` (`vitrine`): um `agora` para a página; `historico_publico_dos_editais` para os Editais carregados; a função de T003 com o conteúdo vigente de cada um; `resumo_do_acompanhamento` por cartão; convite conforme o resumo (FR-1634)
- [ ] T020 [US5] Bloco de acompanhamento e convites em `processo_seletivo/portal/templates/portal/_cartao_da_selecao.html`, e a regra dele em `processo_seletivo/portal/templates/portal/base.html` (FR-1629 a FR-1634, FR-1636)

**Checkpoint**: US1 + US5 = a vitrine inteira da 072.

## Phase 5: User Story 2 — Visitante novo, da vaga ao rascunho (P1)

**Goal**: atalho para as vagas, vaga nomeada no acesso, volta explicada, confirmação mantida.

**Independent Test**: teste de aceitação com identidade nova atravessando os formulários (SC-603).

- [ ] T021 [P] [US2] Testes em `tests/integration/portal/test_detalhe_selecao.py`: resumo da oferta no cabeçalho antes do botão do PDF, com âncora por Perfil e a ação para `#vagas-titulo` ("Ver vagas e inscrever-se" / "Ver vagas"); teto de 5; "← Todas as seleções" sem consulta e "← Voltar aos resultados" com consulta (FR-1615, FR-1616, FR-1618)
- [ ] T022 [P] [US2] Testes em `tests/integration/portal/test_contexto_do_acesso.py` (novo): com destino de vaga, acesso, código, reconciliação e "Seus dados" nomeiam Perfil e Edital, e o `h1` do acesso diz que se confirma o e-mail para se inscrever; com destino externo, rota inexistente, página do Edital ou Perfil de outro Edital, nada é nomeado; o corpo da resposta ao pedir código é o mesmo exista ou não identidade; ajuda de spam na tela do código (FR-1619 a FR-1621, SC-602)
- [ ] T023 [P] [US2] Teste de aceitação em `tests/acceptance/portal/test_jornada_publica.py` (novo): identidade **nova** — página da seleção → POST "Inscrever-se" → acesso → código lido da caixa de saída de teste → "Seus dados" **postado pelo formulário** com os valores de teste do repositório → volta com a vaga e a mensagem → **nenhuma** `Inscricao` existe → POST "Inscrever-se" → rascunho daquela vaga; recarregar não repete a mensagem; a resposta com mensagem é privada; destino colado por terceiro não abre inscrição; "Seus dados foram guardados." não aparece mais na tela da inscrição; com o período de inscrições encerrado entre o clique e a volta, a mensagem não convida a abrir inscrição (FR-1622 a FR-1625, SC-603)
- [ ] T024 [US2] Em `processo_seletivo/portal/views.py`: `_vaga_do_destino(destino)` sobre `_rota_do_destino` e `selectors.selecao_publica` (research T-004); contexto passado por `acesso`, `acesso_codigo`, `acesso_reconciliar` e `meus_dados`
- [ ] T025 [US2] Em `processo_seletivo/portal/views.py`: chave de sessão `portal_volta_a_vaga` gravada em `_entrar` e em `meus_dados` a caminho de uma vaga (sem o `_avisar` genérico nesse caso); `selecao` lê e remove a chave só para Perfil do próprio Edital, passa a mensagem ao template e marca a resposta como privada (research T-003); mensagem sem convite quando o Edital não recebe inscrição (FR-1623)
- [ ] T026 [US2] Em `processo_seletivo/portal/views.py` (`selecao`): resumo da oferta com `quantidade_da_oferta` e `os_primeiros` (teto 5); volta condicional pela presença de consulta
- [ ] T027 [US2] Em `processo_seletivo/portal/templates/portal/selecao.html`: volta condicional; resumo da oferta no cabeçalho antes do botão do PDF; mensagem de volta dentro do Perfil, com `role="status"`
- [ ] T028 [US2] Em `processo_seletivo/portal/templates/portal/acesso_email.html`, `acesso_codigo.html` e `acesso_reconciliar.html`: bloco de contexto da vaga; `h1` do acesso com destino de vaga; ajuda de spam no código
- [ ] T029 [US2] Regras em `processo_seletivo/portal/templates/portal/base.html`: resumo da oferta, contexto da vaga no acesso, mensagem de volta, `.perfil:target` com borda mais grossa e etiqueta textual, `scroll-margin-top` (FR-1617, research T-007)

**Checkpoint**: o visitante novo vai do cartão ao rascunho sem perder a vaga de vista.

## Phase 6: User Story 3 — Quem já tem identidade (P2)

**Goal**: o caminho recorrente ganha o mesmo contexto e não regride.

**Independent Test**: identidade com núcleo, sem sessão e com sessão.

- [ ] T030 [US3] Em `tests/acceptance/portal/test_jornada_publica.py`: identidade com nome e CPF, sem sessão → volta à vaga com mensagem, sem "Seus dados"; com sessão → POST abre o rascunho direto, sem mensagem; com rascunho → "Continuar inscrição" (US3, cenários 1 a 3)

## Phase 7: User Story 4 — Preparar antes de se identificar (P2)

**Goal**: o Requerimento anunciado quando pedido na inscrição; finalidade de nome e CPF dita.

**Independent Test**: página de um Edital com Requerimento na inscrição, sem Requerimento e na convocação.

- [ ] T031 [P] [US4] Testes em `tests/integration/portal/test_detalhe_selecao.py`: frase do Requerimento antes do primeiro Perfil com `matriculationRequest.moment` na inscrição; ausente sem Requerimento e com o momento na convocação; documentos e teto continuam (FR-1626, FR-1628)
- [ ] T032 [US4] Em `processo_seletivo/portal/views.py` (`selecao`) e `processo_seletivo/portal/templates/portal/selecao.html`: ler `matriculationRequest.moment` da versão vigente e escrever a frase antes do primeiro Perfil
- [ ] T033 [US4] Em `processo_seletivo/portal/templates/portal/meus_dados.html`: vaga do destino e o texto de finalidade proposto (FR-1627), com teste em `tests/integration/portal/test_contexto_do_acesso.py`

## Phase 8: Polish & verificação

- [ ] T034 [P] Teste novo `tests/portal/test_vocabulario_das_telas_publicas.py`: `PROIBIDAS` (importado de `tests/portal/test_acompanhamento_pela_situacao.py`) sobre o texto visível da vitrine, da seleção aberta e encerrada com resultado, e das telas de acesso com destino de vaga (FR-1638, research T-008)
- [ ] T035 [P] Atualizar `tests/interface/test_acessibilidade_do_portal.py`: a consulta continua sem `hx-`/`onclick`, com rótulos ligados e `summary` presente; mensagem de volta com `role="status"` (FR-1639, FR-1640)
- [ ] T036 Ajustar os testes de texto que a reconciliação aponta — `test_detalhe_selecao.py` ("Voltar aos resultados"), `tests/integration/portal/test_atos_que_respondem.py` ("Seus dados foram guardados"), `tests/acceptance/portal/test_entrar_sem_senha.py` e `tests/integration/identidade/test_mudanca_de_credencial.py` ("Sem senha") —, cada um relido contra a decisão que o originou
- [ ] T037 Criar `specs/072-jornada-publica-do-portal/rastreabilidade.md`: FR-1600 a FR-1640 e SC-600 a SC-607 → teste ou verificação
- [ ] T038 Criar `specs/072-jornada-publica-do-portal/validacao-humana.md`: roteiro do percurso conduzido com cinco pessoas (SC-605), com tarefas, critérios e ficha de registro; e o texto de finalidade de "Seus dados" para validação por quem responde pela proteção de dados (FR-1627) — ambos marcados como pendentes
- [ ] T039 Guardião de citações: `uv run pytest -q tests/test_citacoes_de_requisito.py`
- [ ] T040 Verificação canônica: `make lint check test-pg DB_NAME=ps_072_teste POSTGRES_USER=$USER`, com `uv run ruff format --check` incluído no `lint`
- [ ] T041 Navegador, telas do SC-600 e do SC-601: script de medição da auditoria contra o seed; capturas em 375 × 667 e 1280 × 900 da vitrine e da seleção
- [ ] T042 Navegador, SC-607: nenhuma rolagem lateral em 320, 360, 375, 390, 768, 1280 e 1440 nas telas alteradas
- [ ] T043 Navegador, sem script: vitrine e seleção renderizadas em `iframe` com `sandbox="allow-same-origin"`; filtros recolhidos operáveis (FR-1603)
- [ ] T044 Navegador, jornadas: visitante novo até "Seus dados" (o CPF fica para a pessoa — o agente não o digita) e, a partir dali, a candidata do fixture para volta, mensagem e confirmação; recorrente; participante no Edital 51/2026
- [ ] T045 Registrar `specs/072-jornada-publica-do-portal/verificacao.md`: o que foi verificado, como, e o que continua pendente (SC-605, FR-1627)
- [ ] T046 Desfazer a entrada temporária de `.claude/launch.json` (`git checkout -- .claude/launch.json`)

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T006)** → histórias.
- **US1 (T007–T015)** e **US5 (T016–T020)** tocam o mesmo cartão: US1 primeiro, US5 em seguida (T020 depende de T011).
- **US2 (T021–T029)** depende só da Foundational (T004 para o resumo da oferta).
- **US3 (T030)** depende de T025.
- **US4 (T031–T033)**: T032 toca `selecao.html` depois de T027; T033 depois de T024.
- **Polish (T034–T046)** depois de todas.

### Paralelismo

- T004 e T005 em paralelo com T002/T003.
- Testes de cada história (T007/T008, T016/T017, T021/T022/T023, T031) em paralelo entre si, antes da implementação da história.
- T013 (script) em paralelo com T011/T012.
- T034 e T035 em paralelo.

## Implementation Strategy

**MVP**: Setup + Foundational + US1 — a vitrine que mostra oportunidade antes de filtro. Em seguida US5
(acompanhar, P1), US2 (começar, P1), US3 e US4 (P2), e a verificação. Cada fase fecha com os seus testes
verdes antes da seguinte.
