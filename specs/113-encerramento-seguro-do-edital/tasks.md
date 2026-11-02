# Tasks: Encerramento seguro do Edital (113)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/encerramento.md](contracts/encerramento.md), [quickstart.md](quickstart.md)

**Tests**: pedidos — cada FR e SC tem teste na [matriz de rastreabilidade](rastreabilidade.md). Os testes
de cada história vêm antes da implementação dela e devem falhar primeiro.

Caminhos relativos a `backend/`. Suíte sempre contra PostgreSQL (`make test-pg`), com `DB_NAME` próprio
da worktree.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1–US4 da spec

---

## Phase 1: Setup

- [X] T001 Registrar a linha de base: rodar `PYTEST_ADDOPTS="tests/interface/test_relatorio.py tests/unit/interface/test_relatorio_do_edital.py tests/interface/test_relatorio_consolidado.py tests/integration/publicacoes/test_retificacao_de_edital_encerrado.py tests/acceptance/test_us7_finalizacao.py tests/contract/test_finalizacao_api.py tests/integration/processos/test_finalizacao_concorrente.py -q" make test-pg PYTEST_WORKERS=0` e anotar os totais em `specs/113-encerramento-seguro-do-edital/verificacao.md` (arquivo novo)

---

## Phase 2: Foundational (leituras reaproveitadas, sem mudança de comportamento)

**⚠️ Bloqueia todas as histórias.** Nenhum teste existente pode mudar de resultado nesta fase.

- [X] T002 [P] Mover `_aguardando_decisao` de `processo_seletivo/interface/acoes.py` para `processo_seletivo/recursos/application/selectors.py` como `aguardando_decisao()` (mesma consulta, mesma docstring); `acoes.recursos_aguardando_decisao` e `acoes.recursos_por_edital` passam a importá-la, com a mesma assinatura (R-002)
- [X] T003 [P] Promover `_janela_aberta` de `processo_seletivo/divulgacao/domain/publicabilidade.py` a `janela_aberta_ate(*, edital, marco_id, marco, at, lista_id=None)` pública, sem mudar a regra, e atualizar os chamadores do próprio módulo (R-002, R-003)
- [X] T004 Criar `processo_seletivo/processos/application/pendencias_do_edital.py` com: a dataclass congelada `Situacao(especie, tipo, quantidade=1, marco="", ate=None, retificacao_id=None, criada_em=None)`; as constantes `IMPEDIMENTO`, `ADVERTENCIA` e **todos** os tipos de [data-model.md](data-model.md) — os da `099` passam a ser definidos só aqui, e `interface/relatorio_do_edital.py` os importa em vez de defini-los (uma definição, D-004 da spec); os imports de `recursos`, `divulgacao` e `publicacoes` ficam dentro das funções (R-001); e `recurso_pendente_do_marco(*, edital, marco) -> tuple[bool, bool]` (reavaliação, providência), extraído de `interface/relatorio_do_edital.py:_pendencias_de_recurso`, que passa a chamá-lo (D-004 da spec)
- [X] T005 Rodar de novo a linha de base do T001: os mesmos totais, sem falha nova

**Checkpoint**: as leituras estão onde o command alcança, e a `099` e a `104` não mudaram.

---

## Phase 3: User Story 1 — encerrar é impedido quando a conclusão ainda não aconteceu (P1) 🎯 MVP

**Goal**: o command e a tela recusam os cinco impedimentos, com a frase e a ação de cada um.

**Independent Test**: cada impedimento sozinho recusa (tela e serviço) sem mudar nada; resolvido, encerra.

### Tests (escrever antes, ver falhar)

- [X] T006 [P] [US1] `tests/unit/processos/test_pendencias_do_edital.py` (com `django_db`): um caso por tipo de impedimento e por caso-limite da spec — período com término em curso, por abrir, não designado, encerrado, cancelado por Retificação, prorrogado (vale o vigente), **sem término (não impede)**; prazo recursal computável aberto, fechado, não declarado (não impede), não computável (não impede), marco com `admits: false` (não impede); recurso sem juízo, admitido sem decisão, não admitido (não impede), julgado com reavaliação (o recurso sai, a reavaliação entra); providência pendente; Retificação homologada, inclusive com vigência futura, e duas homologadas (duas situações)
- [X] T007 [P] [US1] `tests/integration/processos/test_encerramento_seguro.py` (transacional): para cada impedimento sozinho, `close_edital` recusa com `pendencias_impeditivas`/409 e `retrato` igual antes e depois (situação, `revision`, `AtoAdministrativo`, `RegistroAuditoria`); resolvido, aceita; repetir o pedido concluído devolve o ato sem reconferir; a recusa e o aceite cabem nos privilégios de produção (`como_producao`)
- [X] T008 [P] [US1] `tests/integration/processos/test_encerramento_concorrente.py` (transacional, só PostgreSQL): recurso interposto e admitido em outra conexão que confirma antes do encerramento → recusa; encerramento que confirma antes → a admissão roda depois e o Edital fica encerrado (comportamento atual de ato posterior, FR-3545); publicação de resultado que abre prazo recursal em paralelo, nos dois sentidos; nenhum deadlock com os atos da Retificação (rodar junto `tests/integration/publicacoes/test_retificacao_de_edital_encerrado.py`)
- [X] T009 [P] [US1] Em `tests/contract/test_finalizacao_api.py`: `POST .../encerramentos` com recurso aguardando → 409, `code` `pendencias_impeditivas`, `detail` começando por "Antes de encerrar, resolva:"; o `GET` do Edital mostra a mesma `revision`
- [X] T010 [P] [US1] `tests/interface/test_confirmacao_do_encerramento.py`: com cada impedimento, a tela de `interface:ato` `encerrar` mostra o bloco "Antes de encerrar, resolva" com a frase de [contracts/encerramento.md](contracts/encerramento.md) e **não** tem "Confirmar"; o caminho até os recursos aparece para quem tem `recurso:julgar` e, para o gestor sem ela, a contagem com "peça a quem julga recursos" (SC-1071); o caminho "Retificar" só para quem `pode_retificar`; POST com impedimento devolve a tela com 409 e a lista atual (FR-3543)

### Implementation

- [X] T011 [US1] Em `processo_seletivo/processos/application/pendencias_do_edital.py`, `situacoes(edital, *, agora, com_advertencias=False)`: os sete tipos de impedimento (R-002), lendo o conteúdo vigente uma vez (`effective_version`), `periodo_de_inscricoes`, `janela_aberta_ate` sobre os pares `(marco, lista)` com `PublicacaoResultado` do Edital, `aguardando_decisao().filter(inscricao__edital=edital).count()`, `recurso_pendente_do_marco` por marco publicado, e `Retificacao` homologada ordenada por `created_at`
- [X] T012 [US1] Em `processo_seletivo/processos/domain/finalizacao.py`, `ensure_edital_can_be_closed(edital, impedimentos=())`: depois das conferências de estado atuais, recusa `DomainError("pendencias_impeditivas", "Antes de encerrar, resolva: " + "; ".join(frases) + ".", 409)`; as frases vêm de uma função pura `frase_do_impedimento(situacao)` no mesmo módulo, com o texto do contrato
- [X] T013 [US1] Em `processo_seletivo/processos/application/finalizacao.py`, `_finalize_edital`: ler `processo_id` do Edital (escopo do ator) sem trava, travar o `ProcessoSeletivo` com `select_for_update`, depois o Edital (`_lock_edital`), recusar como conflito se o `processo_id` relido mudou (R-004); `close_edital` passa a `check` que chama `situacoes(edital, agora=now)` e `ensure_edital_can_be_closed`; `cancel_edital` ganha só a ordem de travas
- [X] T014 [US1] Criar `processo_seletivo/interface/encerramento.py`: `pendencias_da_confirmacao(edital, ator, *, acao, agora)` devolve itens no formato que `confirmar.html` já lê (`severidade`, `mensagem`) mais `caminho` (`url`, `rotulo`) ou `a_quem_pedir`, pelas regras de R-006 (`acoes.pode_retificar`, `recurso:julgar`, a mesma pergunta de `views._destinos_do_marco` para o marco)
- [X] T015 [US1] Em `processo_seletivo/interface/views.py`, `praticar_ato`: para `encerrar`, `pendencias = encerramento.pendencias_da_confirmacao(...)` (hoje só `submeter`/`publicar` montam); `recusa_certa` já reage a `severidade == "erro"`; ~~`acoes._motivo_previsivel` passa a contar as impeditivas também para `encerrar`~~ — **não feito, de propósito**: custaria a conferência inteira a cada abertura do detalhe e da Lista (orçamentos de consulta da `104`), e nenhuma FR pede; a confirmação já impede e explica
- [X] T016 [US1] Em `processo_seletivo/interface/templates/interface/confirmar.html`: bloco de erro (com as classes `erro` e `aviso` que a folha já define — nenhuma classe nova, nenhuma regra de CSS nova) com título "Antes de encerrar, resolva N pendência(s)" e, por item, o caminho ou "peça a …" — sem `style`, sem `<script>` (CSP); regra na folha da gestão (`interface/static/interface/gestao/`) para toda classe nova; conferir a varredura de vocabulário e o guardião de classes sem regra

**Checkpoint**: US1 sozinha já fecha o A-11 no essencial — o Edital não é dito concluído com obrigação pendente.

---

## Phase 4: User Story 2 — quem encerra sabe o que continua (P1)

**Goal**: advertências separadas, iguais às providências da `099`; consequências corrigidas.

**Independent Test**: cada advertência aparece sem impedir; o relatório emitido depois lista o mesmo.

### Tests

- [X] T017 [P] [US2] Em `tests/interface/test_confirmacao_do_encerramento.py`: cada advertência de FR-3534 aparece em "Continuam depois do encerramento" e o botão "Confirmar" está presente; sem situação nenhuma, a frase "Nenhuma pendência registrada no GPS impede o encerramento" e nenhuma ocorrência de "concluída"/"conclusão regular"; as consequências do contrato; nenhuma frase com nome, CPF, e-mail ou protocolo de candidato do cenário (SC-1071); o número de consultas da confirmação num Edital com 400 inscrições é o mesmo que com 5 (orçamento fixo, `django_assert_max_num_queries`), em `tests/performance/test_confirmacao_do_encerramento.py`, porque tempo de relógio oscila na suíte paralela (CLAUDE.md, *Um teste de tempo oscila sob carga*)
- [X] T018 [P] [US2] Em `tests/interface/test_confirmacao_do_encerramento.py`: para os cenários `pendente` e `sem-pendencia` de `tests/fixtures/relatorio.py`, encerrar e conferir que toda providência de `fatos_do_edital` depois do ato foi exibida na confirmação antes dele (SC-1069); o desfecho da convocação registrado depois do encerramento continua aceito (US2, cena 2)

### Implementation

- [X] T019 [US2] Em `pendencias_do_edital.situacoes(..., com_advertencias=True)`: `RETIFICACAO_EM_CURSO`, `PRAZO_RECURSAL_NAO_DECLARADO` (publicação vigente sem janela computável, marco sem `admits: false`) e `PERIODO_SEM_TERMINO`
- [X] T020 [US2] Em `interface/encerramento.py`: acrescentar as advertências da `099` lendo `relatorio_do_edital.fatos_do_edital(edital, agora=agora).pendencias` dos tipos `CONVOCACAO_AGUARDANDO`, `CONVOCACAO_VENCIDA`, `RESULTADO_NAO_DIVULGADO`, `DEFINITIVO_NAO_PUBLICADO`, `APURACAO_DESATUALIZADA`, redigidas por `texto_da_pendencia` (a mesma frase do relatório) e respeitando os Perfis omitidos; as demais pela tabela do contrato; severidade `aviso`
- [X] T021 [US2] Em `confirmar.html`: título "Continuam depois do encerramento" sobre os avisos de `encerrar`; a linha "Nenhuma pendência registrada no GPS impede o encerramento." quando não houver item
- [X] T022 [US2] Em `processo_seletivo/interface/atos.py`, `ATOS["encerrar"].consequencias`: as três frases do contrato, no lugar de "registrando a conclusão regular de suas etapas" e "Nenhuma Retificação poderá ser publicada depois disso"; ajustar testes que prendem o texto antigo (`grep -rn "conclusão regular de suas etapas" tests`)

---

## Phase 5: User Story 3 — cancelar continua sempre possível (P2)

**Goal**: o cancelamento nunca recusa por situação; a tela diz o que será atingido.

**Independent Test**: Edital com tudo junto é cancelado; a tela lista cada situação como advertência.

- [X] T023 [P] [US3] Em `tests/integration/processos/test_encerramento_seguro.py`: Edital com todos os impedimentos e advertências é cancelado por `cancel_edital` e por `POST .../cancelamentos` (SC-1068); em `tests/interface/test_confirmacao_do_encerramento.py`, a tela de `cancelar` mostra cada situação sob "Serão atingidos pelo cancelamento", nenhuma como impedimento, as inscrições em preenchimento com período aberto, e o botão presente
- [X] T024 [US3] Em `pendencias_do_edital.py`, `RASCUNHOS_NAO_ENVIAVEIS` (contagem de `Inscricao.RASCUNHO` quando o período está aberto); em `interface/encerramento.py`, para `acao="cancelar"`, toda situação vira `aviso`; em `praticar_ato`, montar `pendencias` também para `cancelar`; em `confirmar.html`, o título "Serão atingidos pelo cancelamento"

---

## Phase 6: User Story 4 — a Retificação parada não anuncia próximo passo (P3)

- [X] T025 [P] [US4] `tests/interface/test_retificacao_parada.py`: Edital encerrado com Retificação em elaboração e em revisão, e cancelado com uma homologada — o detalhe do Edital e a tela de Retificar dizem "Não pode mais prosseguir: o Edital foi encerrado" (ou "cancelado"), sem "Aguardando", sem "O próximo ato é seu" e sem "Continuar a elaboração"
- [X] T026 [US4] Em `processo_seletivo/interface/atos_retificacao.py`, `resumo`: campo `parada` (`"encerrado"`/`"cancelado"`/`""`) a partir de `EDITAL_FINAL`, sem `passo` quando parada; em `processo_seletivo/interface/templates/interface/_retificacoes_em_curso.html`, a frase no lugar do bastão e sem o link de continuar

---

## Phase 7: Polish & Cross-Cutting

- [X] T027 Ajustar os testes de R-008 que encerram com período com término ou prazo recursal em curso — `tests/integration/portal/test_desfecho_publico.py` (`test_encerrado_com_periodo_por_abrir_nunca_vai_para_as_proximas` e vizinhos), `tests/portal/test_prazo_recursal_publico.py::test_edital_encerrado_com_prazo_em_curso_continua_dizendo_o_prazo`, `tests/integration/agenda/test_fonte.py::test_edital_cancelado_some_e_encerrado_so_mostra_o_que_passou`, `tests/fixtures/relatorio.py` — gravando o estado final como dado anterior à regra (comentário dizendo por quê), sem mudar o que cada teste afirma
- [X] T028 Atualizar [rastreabilidade.md](rastreabilidade.md) com os nomes reais dos testes
- [X] T029 `cd backend && make lint check test-pg`; se falharem em bloco arquivos que encerram Edital, procurar a causa na fixture antes do diff; anotar totais em `verificacao.md`
- [X] T030 Medir isolado o tempo da confirmação num Edital com 400 inscrições (SC-1072, < 1 s), cinco vezes, e registrar a distribuição em `verificacao.md`. Validação pela interface conforme [quickstart.md](quickstart.md) §3, com capturas de encerrar (impedimento, advertência, sem nada) e de cancelar em `verificacao.md`; desfazer a entrada temporária do `.claude/launch.json`
- [X] T031 Atualizar a linha da `113` no `README.md` (situação) e o número `M`/totais do `CLAUDE.md` só se a suíte mudar de contagem de pulados

---

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T005)** → histórias.
- **US1** depende só do Foundational. **US2** depende de T011 e T014 (mesmos módulos). **US3** depende de
  T014–T015. **US4** é independente das demais depois do Foundational.
- **Polish** depois das histórias; T027 pode começar assim que T013 existir (é quando os testes de R-008
  passam a falhar).

### Parallel

- T002 e T003 em paralelo; T004 depois de nenhum dos dois (arquivo próprio, mas lê o relatório).
- Os testes de cada história marcados [P] em paralelo entre si (arquivos diferentes, exceto T017/T018,
  mesmo arquivo — escrever em sequência).
- US4 (T025–T026) em paralelo com US2/US3.

## Implementation Strategy

1. **MVP = Phases 1–3**: o command recusa e a tela explica. Já resolve o A-11 no essencial.
2. US2 traz as advertências e corrige o texto; US3 o cancelamento; US4 a exibição da Retificação.
3. Um PR só, pequeno: sem migration, sem trava nova. Validação pela interface antes do PR.
