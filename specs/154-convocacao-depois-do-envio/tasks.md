# Tasks: A convocação depois do envio, e um nome só para o documento reenviado

**Input**: `specs/154-convocacao-depois-do-envio/` (spec, plan, research, data-model, contracts,
quickstart)

**Tests**: pedidos — a rastreabilidade é verificada por teste (CLAUDE.md), a spec conta ocorrências
(SC-2000, SC-2001) e exige identidade letra a letra (SC-2004). Os testes de cada história vêm antes
da implementação dela, e precisam falhar primeiro.

Caminhos relativos a `backend/`, salvo os de `specs/` e `docs/`. Nenhuma tarefa cria migration,
modelo, rota nem estado gravado (FR-6216).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: US1, US2 ou US3, da spec

## Phase 1: Setup

- [ ] T001 Banco descartável `ps154` com os cenários de treinamento (`CENARIOS_DE_TREINAMENTO=true uv run python manage.py carregar_cenarios_de_treinamento --banco ps154`) e a entrada `convocacao-154` **acrescentada** a `../.claude/launch.json`, sem sobrescrever as outras (quickstart, §2)
- [ ] T002 Capturas do antes em `../specs/154-convocacao-depois-do-envio/capturas/antes-*.png`: C1, T, Tc, o reenviado no portal e na gestão — as três do estudo (`B08`, `D04`, `D05`) mais Tc e a condução

## Phase 2: Foundational

**Purpose**: o vocabulário do reenviado e as derivações da projeção, de que as três histórias dependem.

- [ ] T003 [P] Teste do vocabulário em `tests/unit/convocacao/test_vocabulario_dos_documentos.py`: `REENVIADO` com travessão U+2014 e espaços, `reenviado_em_frase()` em minúscula, `reenviados(1)` e `reenviados(2)` sem "(s)", e as formas derivadas contendo o rótulo letra a letra, salvo a caixa da inicial (FR-6211, D-004, SC-2004)
- [ ] T004 [P] Módulo `processo_seletivo/convocacao/domain/vocabulario_dos_documentos.py`: `REENVIADO`, `reenviado_em_frase()`, `reenviados(n)`; puro, sem Django, com o comentário de por que existe (achado 23 do estudo; R-006)
- [ ] T005 Testes unitários das derivações em `tests/unit/portal/test_obrigacoes_da_convocacao.py`: `providencia_pendente`, `conferencia_terminada` e `cabe_a_consequencia` sobre cada linha da tabela de decisão de `data-model.md`, e `providencia_pendente_sem_documento` sobre as quatro linhas da tabela sem documento (FR-6200, FR-6201, FR-6205, FR-6209; D-001, D-006)
- [ ] T006 `processo_seletivo/portal/obrigacoes.py`: `Obrigacoes.providencia_pendente`, `Obrigacoes.conferencia_terminada`, `Obrigacoes.cabe_a_consequencia` e `providencia_pendente_sem_documento(disponibilidade)` (R-001, R-002, R-004, R-005)

**Checkpoint**: T003 e T005 verdes; nenhuma tela mudou ainda.

## Phase 3: User Story 1 — quem já enviou tudo lê que agora é acompanhar (P1) 🎯 MVP

**Goal**: sem providência pendente, o título é *"Acompanhe sua convocação"*, o prazo continua, a
advertência sai — na convocação e no acompanhamento (achado 20 do estudo).

**Independent Test**: no C09, a captura `B08-tudo-enviado` refeita mostra o título novo, o cartão
do prazo e a frase de conclusão, e nenhuma advertência; C1 continua com *"Você foi convocado!"* e a
advertência uma vez.

### Testes da US1

- [ ] T007 [P] [US1] Título e resumo em `tests/unit/portal/test_obrigacoes_da_convocacao.py`: C1 e F com *"Você foi convocado!"*; T, T com opcional não enviado e *só facultativo* com *"Acompanhe sua convocação"*; pendência nova depois de T volta a *"Você foi convocado!"* (FR-6202, FR-6203; cenários 1, 3, 4 e 5 da US1)
- [ ] T008 [P] [US1] A consequência nas duas montagens da ação em `tests/unit/portal/test_situacao_da_inscricao.py`: com documento, sem tarefa e com prazo correndo → `consequencia == ""` e `prazo` preenchido; com tarefa → a frase; sem documento, Requerimento da chamada enviado → sem a frase; Requerimento da inscrição enviado → com a frase; nada pedido → com a frase (FR-6201, FR-6208, FR-6209)
- [ ] T009 [P] [US1] Página da convocação em `tests/interface/test_portal_convocacao.py`: a advertência conta **zero** em T, *prazo não iniciado com tudo enviado*, *sem vencimento com tudo enviado* e *só Requerimento já enviado*, e **exatamente uma** em C1, F, *pendência nova*, *só Requerimento não enviado* e *nada pedido* (SC-2000, SC-2001); o cartão do prazo presente com e sem providência (SC-2002); a ressalva presente em todo estado aberto, com e sem providência (FR-6210)
- [ ] T010 [P] [US1] Acompanhamento em `tests/portal/test_acompanhamento_pela_situacao.py`: *"Nada por enquanto."* + frase de conclusão, o prazo e nenhuma advertência em T; a advertência uma vez em C1 (cenário 2 da US1; FR-1177 da `063`, revista)
- [ ] T011 [P] [US1] Casos-limite do prazo em `tests/interface/test_portal_jornada_consolidada.py`: *prazo não iniciado, tudo enviado* (título novo, só a frase do canal no cartão), *sem vencimento, tudo enviado* (título novo, *"Esta convocação não tem prazo registrado."*), *convocação corrigida com aproveitado sem conferência* (frase de conclusão) e *duas inscrições convocadas* (cada uma com o seu título)

### Implementação da US1

- [ ] T012 [US1] `processo_seletivo/portal/obrigacoes.py`: `TITULO_SEM_PROVIDENCIA` e `Obrigacoes.titulo` pela providência (R-003); o comentário diz que a linha da FR-3858 da `121` se dividiu, e por quê
- [ ] T013 [US1] `processo_seletivo/portal/templates/portal/_chamada_da_convocacao.html`: a consequência sob `{% if o.cabe_a_consequencia %}`, e o comentário do template revisto (FR-6209; achado 20 do estudo)
- [ ] T014 [US1] `processo_seletivo/portal/situacao.py`: `_acao_das_obrigacoes` só põe a `consequencia` com `obrigacoes.providencia_pendente`, e mantém o `prazo` (R-004); `_acao_da_convocacao` só a põe com `providencia_pendente_sem_documento(politica)` (R-005); o comentário das frases de consequência ganha a condição nova
- [ ] T015 [US1] `processo_seletivo/portal/views.py`, `_chamada_da_tela`, ramo sem projeção: com o momento `ABERTA` e sem providência, `TITULO_SEM_PROVIDENCIA` (FR-6201, D-006)

**Checkpoint**: T007 a T011 verdes; a US1 entrega o achado 20 sem a frase da conferência terminada.

## Phase 4: User Story 2 — recebido, conferido e concluído não se confundem (P1)

**Goal**: com todos os obrigatórios conferidos e sem desfecho, a frase da conferência terminada no
lugar da frase de conclusão, nas três superfícies; nenhuma falsa conclusão sem desfecho.

**Independent Test**: no C09, T → Tc → I1: título, resumo e o texto de cada cartão em cada um.

### Testes da US2

- [ ] T016 [P] [US2] Conclusão em `tests/unit/portal/test_obrigacoes_da_convocacao.py`: Tc (conformes e *não se aplica*) e Tc com opcional enviado e não conferido → frase da conferência terminada; meio conferido, *só facultativo* e convocação corrigida com aproveitado → frase de conclusão; a confirmação do envio de um opcional em Tc → frase da conferência terminada, e nunca *"ainda vai concluir a análise"* (FR-6204, FR-6205; SC-2003; R-002)
- [ ] T017 [P] [US2] Falsas conclusões em `tests/interface/test_convocacao_depois_do_envio.py` (novo): a convocação e o acompanhamento renderizados em C1, T, Tc, *só facultativo*, *só Requerimento enviado* e com um reenviado, sem desfecho — nenhum `aprovad`, `aceit`, `deferid`, `concluíd`, `tudo certo`, `pront[oa]` nem `enviou tudo`, com fronteira de palavra; nenhum cartão recebido, aproveitado ou reenviado com `selo-conferido`; o `<h1>` sem classe nova (FR-6207, SC-2003; R-013)
- [ ] T018 [P] [US2] Com desfecho, em `tests/interface/test_portal_convocacao.py`: I1 com *"Resultado da sua convocação"*, o rótulo do desfecho e a frase do aceite, como hoje (FR-6206; cenário 6 da US2)
- [ ] T019 [P] [US2] *Só Requerimento, já enviado* e *nada pedido pelo portal* em `tests/interface/test_portal_convocacao.py`: o primeiro com o título novo, o prazo, sem advertência e **sem** a frase da conferência terminada; o segundo, a tela de hoje (FR-6201, FR-6205; cenários 4 e 5 da US2)

### Implementação da US2

- [ ] T020 [US2] `processo_seletivo/portal/obrigacoes.py`: `FRASE_DA_CONFERENCIA_TERMINADA`; `_aberta` escolhe entre ela e `FRASE_DE_CONCLUSAO` pela `conferencia_terminada`; `resumo_do_que_falta` e `confirmacao_do_envio` leem `frase_de_conclusao` (R-002); o comentário da frase de conclusão diz que a proibição de dizer *"enviou tudo"* continua (decisão da `118`)

**Checkpoint**: T016 a T019 verdes; a US1 continua verde.

## Phase 5: User Story 3 — o documento reenviado tem um nome só (P2)

**Goal**: *"Reenviado — aguardando nova conferência"* no cartão do portal, no item, nas duas
contagens, no passo da chamada e na exclusão do aviso de pendência (achado 23 do estudo).

**Independent Test**: no C09, `D04-correcao-enviada` e `D05-gestao-ve-versao-2` refeitas, com o
nome comparado letra a letra.

### Testes da US3

- [ ] T021 [P] [US3] Cartão do portal em `tests/unit/portal/test_obrigacoes_da_convocacao.py`: D-003 com a chamada aberta **e** com o prazo vencido (o vencimento sozinho mantém *"aguardando"*); D-005 com o Processo encerrado e com desfecho; facultativo reenviado com o selo *Opcional* (FR-6213; casos-limite do reenviado)
- [ ] T022 [P] [US3] Passo e frase do reenvio em `tests/unit/interface/test_conducao_da_convocacao.py`: *"Conferir de novo: 1 documento reenviado — aguardando nova conferência."*, o plural com dois, o código `REENVIADO` e a ação `CONFERIR` inalterados; `frase_da_pendencia` sem paráfrase do estado (FR-6212; R-009)
- [ ] T023 [P] [US3] Página de documentos em `tests/interface/test_portal_documentos_da_convocacao.py` (o portal) e em `tests/interface/test_convocacao_depois_do_envio.py` (a página de documentos da gestão): o rótulo do item, a contagem com um e com dois, e o HTML renderizado sem *complementad*; depois de conferido conforme, nenhuma das telas diz o nome do reenviado (cenários 1, 2, 3 e 5 da US3; SC-2004; R-013)
- [ ] T024 [P] [US3] Condução em `tests/interface/test_convocacao.py`: a linha documental do cartão com *"1 reenviado — aguardando nova conferência"* e sem *complementado* (R-008)
- [ ] T025 [P] [US3] Aviso de pendência em `tests/integration/avisos/test_aviso_de_pendencia.py`: a pessoa cujo único pendente foi reenviado fica de fora como *"documento reenviado — aguardando nova conferência"*; um gesto gravado **antes**, com o texto antigo no `reason` e no `detalhe`, continua lido com ele (FR-6215, SC-2005; cenário 4 da US3)
- [ ] T026 [P] [US3] Varredura em `tests/test_vocabulario_dos_documentos_da_convocacao.py`: `NOMES_ANTIGOS_DO_REENVIADO` com os cinco nomes da FR-6214, sobre `DA_115` mais `interface/conducao_da_convocacao.py`, `interface/views.py` e `avisos/application/pendencias.py` (FR-6214; R-013)
- [ ] T027 [P] [US3] Identidade em `tests/unit/convocacao/test_vocabulario_dos_documentos.py`: `ROTULO_DO_ITEM["COMPLEMENTADO"]`, `COMPLEMENTADA`, a frase do passo e o texto do cartão do portal contêm o mesmo nome do vocabulário (SC-2004)

### Implementação da US3

- [ ] T028 [US3] Antes de mudar a constante: buscar em `processo_seletivo/` e em `tests/` quem lê de volta o motivo gravado do aviso de pendência (`exclusoes` do `detalhe`, ou o `reason`) e o compara com `COMPLEMENTADA`; se houver, parar e registrar — a troca precisaria de alias (R-011)
- [ ] T029 [US3] `processo_seletivo/avisos/application/pendencias.py`: `COMPLEMENTADA` montada do vocabulário (R-011)
- [ ] T030 [P] [US3] `processo_seletivo/portal/obrigacoes.py`, `texto_do_item`, ramo `ITEM_COMPLEMENTADO`: D-003 e D-005 (R-012)
- [ ] T031 [P] [US3] `processo_seletivo/interface/views.py`: `ROTULO_DO_ITEM["COMPLEMENTADO"]` do vocabulário (R-010)
- [ ] T032 [P] [US3] `processo_seletivo/interface/conducao_da_convocacao.py`: a frase do passo `REENVIADO` e `frase_da_pendencia` (R-009)
- [ ] T033 [P] [US3] Filtro `reenviados` em `processo_seletivo/interface/templatetags/interface_extras.py`, que só chama `vocabulario_dos_documentos.reenviados` (plano, §4)
- [ ] T034 [US3] `processo_seletivo/interface/templates/interface/convocacao_documentos.html`: a contagem do resumo pelo filtro (R-008); confirmar no navegador que a classe da linha não mudou e que nada de estilo inline entrou (CSP)
- [ ] T035 [US3] `processo_seletivo/interface/templates/interface/convocacao.html`: só a contagem da linha documental, pelo filtro (R-008) — o resto do template é da `152` (R-015)

**Checkpoint**: T021 a T027 verdes; US1 e US2 continuam verdes.

## Phase 6: Polish & cross-cutting

- [ ] T036 [P] Conferir, um a um, os testes da R-014 que ainda não passaram por T007–T027 — `tests/integration/portal/test_destino_da_convocacao.py`, `tests/integration/convocacao/test_visibilidade_ao_candidato.py`, `tests/navegador/test_jornada_da_convocacao_121.py`, `tests/navegador/test_jornada_dos_documentos_da_convocacao.py`, `tests/integration/treinamento/test_convocacao_pelas_perguntas.py` e `tests/unit/convocacao/test_escolha_da_mensagem.py` (este, só conferir: a mensagem não muda); cada expectativa alterada cita o requisito da `154`
- [ ] T037 [P] Revisões inline nas specs da `063`, `115`, `118`, `121`, `134` e `143`: conferir que a redação revista pelo PR #479 bate com o que foi implementado; nenhuma muda sem decisão do usuário
- [ ] T038 [P] `../specs/154-convocacao-depois-do-envio/rastreabilidade.md`: cada FR-6200 a FR-6216, SC-2000 a SC-2006 e cada caso-limite com o teste que o prende
- [ ] T039 Capturas do depois em `../specs/154-convocacao-depois-do-envio/capturas/depois-*.png`, refazendo `B08`, `D04` e `D05` e o Tc, a 1280 e a 375 px (SC-2006; quickstart, §2)
- [ ] T040 A busca do quickstart, §3, sem resultado fora de comentário, teste ou spec
- [ ] T041 `../README.md`: a linha da `154` diz implementada; `../docs/visao-sistema/` acompanha no merge da implementação
- [ ] T042 `cd backend && make lint check test-pg` — `ruff check` **e** `ruff format --check`; a suíte uma de cada vez com as outras sessões, com `DB_NAME` próprio; os guardiões de `tests/performance/` sem mudança de número (R-016)

## Dependencies & Execution Order

- **Setup (T001–T002)**: sem dependência; T002 antes de qualquer mudança de produto.
- **Foundational (T003–T006)**: bloqueia as três histórias. T004 depois de T003; T006 depois de T005.
- **US1 (T007–T015)**: depois de T006. É o MVP: sozinha já fecha o achado 20 no que ele tem de
  ansiedade (título e advertência).
- **US2 (T016–T020)**: depois de T006. Toca `portal/obrigacoes.py` como a US1 (T012 e T020): em
  sequência, não em paralelo.
- **US3 (T021–T035)**: depende só da fase 2 (T004). Pode correr em paralelo com US1 e US2, salvo T030,
  que toca `portal/obrigacoes.py`: depois de T012 e T020.
- **Polish (T036–T042)**: depois das três.

### Dentro de cada história

Testes primeiro, falhando; depois a implementação; o checkpoint fecha a história.

## Parallel Example

```text
# Fase 2:
T003 (teste do vocabulário)   ∥ T005 (teste das derivações)

# US1, os testes:
T007 ∥ T008 ∥ T009 ∥ T010 ∥ T011

# US3, a implementação da gestão, em arquivos distintos:
T031 (views.py) ∥ T032 (conducao_da_convocacao.py) ∥ T033 (interface_extras.py)
```

## Implementation Strategy

1. Fase 1 e 2.
2. **US1** — o achado 20 no que a pessoa sente: título e advertência. Parar e validar no C09.
3. **US2** — a frase da conferência terminada e a varredura das falsas conclusões.
4. **US3** — o achado 23, inteiro.
5. Polish, capturas e a suíte.

Um PR só, como a spec é uma revisão só. Se a `152` (PR #480) for implementada antes, refazer o merge
em `interface/conducao_da_convocacao.py`, `interface/views.py` e `convocacao.html` antes de T032,
T031 e T035 (R-015).
