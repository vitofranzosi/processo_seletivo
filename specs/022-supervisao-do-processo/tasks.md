---

description: "Task list for feature implementation"
---

# Tasks: Supervisão do Processo

**Input**: Design documents from `specs/022-supervisao-do-processo/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/supervisao.md](./contracts/supervisao.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo, e a
`test_citacoes_de_requisito.py` cobra as citações de todo `FR-`, `SC-` e `UX-` que aparecer em
código, template ou spec. Todas as features anteriores escrevem teste; esta não abre exceção.

**Organization**: por user story, para que cada faixa seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US4`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`. **Nenhum app
novo, nenhum modelo, nenhuma migration** — `T-001` e `D-007`.

---

## Phase 1: Setup

**Purpose**: o esqueleto do módulo de leitura e o lugar dos testes.

- [X] T001 [P] Criar o pacote de testes em `backend/tests/integration/supervisao/__init__.py`
- [X] T002 [P] Criar `backend/processo_seletivo/interface/supervisao.py` com as formas de leitura de [data-model.md](./data-model.md) §2 — `Pulso`, `PulsoDoEdital`, `PeriodoDeInscricoes`, `Marco` e `Sinal` — como estruturas imutáveis sem derivação ainda. *`medida` do `Sinal` é par completo ou ausente, e não dois campos opcionais: é `FR-032` expresso na forma, e não confiado à disciplina de quem escreve o template*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a porta, a rota e a página vazia. Sem isto nenhuma story tem onde aparecer.

**⚠️ CRÍTICO**: nenhuma user story começa antes deste checkpoint.

- [X] T003 Implementar `pode_supervisionar(ator, processo)` em `backend/processo_seletivo/interface/supervisao.py`, delegando a `comissoes.domain.autorizacao.pode_gerir_comissao` — as duas bases já existentes, sem papel nem permissão nova (`FR-002`)
- [X] T004 Acrescentar a view de leitura `supervisao` em `backend/processo_seletivo/interface/views.py`, devolvendo o 404 uniforme para escopo distinto, ausência de vínculo e Processo inexistente (`FR-001`, `FR-003`)
- [X] T005 Acrescentar a rota `processos/<uuid:processo_id>/supervisao` em `backend/processo_seletivo/interface/urls.py` (`FR-001`)
- [X] T006 [P] Criar `backend/processo_seletivo/interface/templates/interface/supervisao.html` com as duas regiões anunciadas como regiões, cada uma com título próprio, ainda vazias (`UX-006`)
- [X] T007 [P] Teste de autorização em `backend/tests/integration/supervisao/test_autorizacao.py`: presidência ativa, permissão sistêmica de gerir comissão, escopo institucional distinto, sem vínculo, e Processo inexistente — as três últimas com resposta **literalmente igual**. **Inclui o Processo cancelado, que continua legível para quem preside**: os fatos permanecem e alguém responde por eles (`FR-002`, `FR-003`, `SC-012`)
- [X] T008 Acrescentar o caminho até a supervisão em `backend/processo_seletivo/interface/templates/interface/processo_detalhe.html`, reusando o catálogo de ações existente e **sem** rederivar o conjunto de atos do Edital (`FR-008`)
- [X] T009 Resolver, em `backend/processo_seletivo/interface/supervisao.py`, os Editais do Processo e as Etapas da versão publicada de cada um, pelo resolvedor que a `011` já usa — nunca por leitura própria do conteúdo (`FR-005`)

**Checkpoint**: a página abre para quem preside, recusa para os demais, e está vazia.

---

## Phase 3: User Story 1 — O pulso do Processo, numa tela (Priority: P1) 🎯 MVP

**Goal**: a soma que hoje não existe em nível nenhum — inscrições do Processo, desdobradas por
Edital nomeado, com rascunho como grandeza distinta.

**Independent Test**: abrir a supervisão de um Processo com dois Editais e conferir que o total é a
soma dos dois, que cada Edital aparece nomeado, e que o rascunho não entra na conta.

### Tests for User Story 1

- [X] T010 [P] [US1] Teste da soma e do desdobramento em `backend/tests/integration/supervisao/test_pulso.py`: total do Processo igual à soma dos Editais, cada Edital nomeado, inclusive o de zero inscrições (`FR-010`, `FR-011`, `SC-002`, `SC-007`)
- [X] T011 [P] [US1] Teste de que rascunho **não** soma, em `backend/tests/integration/supervisao/test_pulso.py` (`FR-012`, `SC-003`)
- [X] T012 [P] [US1] Teste de que nenhum percentual é apresentado sobre inscrição, em `backend/tests/interface/test_supervisao.py` (`FR-017`, `SC-005`)

### Implementation for User Story 1

- [X] T013 [US1] Implementar as contagens por Edital em `backend/processo_seletivo/interface/supervisao.py` — submetidas e rascunhos em agregações separadas, jamais somadas (`FR-010`, `FR-011`, `FR-012`)
- [X] T014 [US1] Acrescentar o instante da leitura ao `Pulso` em `backend/processo_seletivo/interface/supervisao.py` (`FR-009`)
- [X] T015 [US1] Renderizar o Pulso em `backend/processo_seletivo/interface/templates/interface/supervisao.html`, com o Edital nomeado em toda linha que lhe pertença — **inclusive quando o Processo tem um Edital só** (`FR-011`, `FR-020`, `UX-007`)
- [X] T016 [US1] Adotar em `backend/processo_seletivo/interface/templates/interface/supervisao.html` o mesmo termo que a `009` usa para rascunho, até que haja decisão de vocabulário — dois termos para o mesmo conceito é o que o Princípio I recusa

**Checkpoint**: `US1` completa e demonstrável sozinha. É o MVP.

---

## Phase 4: User Story 2 — Acompanhar a procura enquanto o prazo corre (Priority: P1)

**Goal**: o eixo do tempo — período, tempo restante, marcos, últimas 24 horas e a série diária.

**Independent Test**: submeter inscrições em dias distintos e conferir que a série reflete a
distribuição, que o rascunho fica fora dela, e que o prazo nomeia o Edital.

### Tests for User Story 2

- [X] T017 [P] [US2] Teste do período, do tempo restante e dos próximos marcos por Edital em `backend/tests/integration/supervisao/test_pulso.py` — **incluindo que Evento `CANCELADO` não entra na lista de marcos** (`FR-019`, `FR-021`, `SC-007`)
- [X] T018 [P] [US2] Teste da série em `backend/tests/integration/supervisao/test_pulso.py`: agrupada por instante de submissão, com rascunho antigo fora dela, e com dia de zero presente na série (`FR-014`, `FR-015`)
- [X] T018a [P] [US2] Teste das últimas 24 horas em `backend/tests/integration/supervisao/test_pulso.py`: soma os Editais do Processo, exclui submissão mais antiga que a janela **e** a de exatamente 24 h — a borda é onde o fora-por-um mora —, e **não** é apresentado quando nenhum Edital tem período em curso (`FR-013`)
- [X] T019 [P] [US2] Teste do equivalente textual da série em `backend/tests/interface/test_supervisao.py` — mesmos valores do gráfico (`FR-016`, `SC-015`)
- [X] T020 [P] [US2] Teste das declarações de ausência em `backend/tests/integration/supervisao/test_pulso.py`: nenhum Edital com período em curso, Edital sem cronograma, cronograma sem período marcado (`FR-018`, `FR-022`)

### Implementation for User Story 2

- [X] T021 [US2] Ler, por Edital, o Evento marcado como período de inscrições em `backend/processo_seletivo/interface/supervisao.py` — pela marca do domínio, nunca inferindo do texto livre do tipo (`FR-019`)
- [X] T022 [US2] Implementar a contagem das últimas 24 horas em `backend/processo_seletivo/interface/supervisao.py` (`FR-013`)
- [X] T023 [US2] Implementar a série diária em `backend/processo_seletivo/interface/supervisao.py`: uma agregação por Edital, por instante de submissão, recortada no período declarado, com os dias de zero preenchidos (`FR-014`, `FR-015`)
- [X] T024 [US2] Implementar os próximos marcos por Edital em `backend/processo_seletivo/interface/supervisao.py`, apresentando o `status` como **declaração** e sem alterá-lo, e **excluindo da lista o Evento `CANCELADO`** — cancelado sai da leitura temporal, aqui pela mesma razão que sai de `UX-002` (`FR-021`, `FR-023`)
- [X] T025 [US2] Implementar as declarações de ausência em `backend/processo_seletivo/interface/supervisao.py` (`FR-018`, `FR-022`)
- [X] T026 [US2] Criar `backend/processo_seletivo/interface/templates/interface/_serie_de_inscricoes.html` com a série **diária** e o equivalente textual, sem depender de cor e sem rolagem horizontal do corpo (`FR-016`, `UX-008`)
- [X] T027 [US2] **Conferência manual** — nenhuma automação substitui: abrir `backend/processo_seletivo/interface/templates/interface/supervisao.html` em 375 px e verificar que nem tabela nem gráfico forçam rolagem horizontal do corpo. *A `013` deixou a mesma conferência pendente em T063; esta não deve seguir o mesmo caminho* (`FR-016`)

**Checkpoint**: o Pulso está fechado. `US1` e `US2` funcionam independentemente.

---

## Phase 5: User Story 3 — Saber o que impede o próximo ato (Priority: P1)

**Goal**: os cinco sinais, e nenhum a mais.

**Independent Test**: montar cada condição, conferir o sinal, desfazê-la e conferir que ele some sem
deixar seção vazia.

**Ordem interna é a do custo crescente** (`T-002`): cronograma, cobertura pronta, confirmação em
duas passagens, e por fim a consulta agregada.

### Forma da região

- [X] T028 [P] [US3] Criar `backend/processo_seletivo/interface/templates/interface/_sinal.html` — forma única dos cinco, com `medida` renderizada como par ou omitida, e **sem** campo de gravidade (`UX-006`, `FR-032`)
- [X] T029 [US3] Montar a região de atenção em `backend/processo_seletivo/interface/supervisao.py` a partir de uma enumeração fechada de cinco espécies, e declarar a ausência em **uma linha** quando não houver sinal (`FR-024`, `FR-025`, `SC-011`)
- [X] T030 [P] [US3] Teste de que a enumeração tem exatamente cinco espécies em `backend/tests/unit/interface/test_supervisao.py` — acrescentar uma sexta quebra o teste, que é o que torna `D-002` executável (`FR-024`)

### `UX-001` — Etapa sem marco no cronograma

- [X] T031 [P] [US3] Teste em `backend/tests/integration/supervisao/test_sinais.py`: Etapa sem Evento vinculado produz o sinal, e **não** produz situação temporal, atraso nem progresso zero (`FR-026`, `SC-008`)
- [X] T032 [US3] Implementar a detecção em `backend/processo_seletivo/interface/supervisao.py`, com a redação de `UX-001` e o Edital nomeado (`FR-026`)

### `UX-002` — Declarado × temporal

- [X] T033 [P] [US3] Teste de `UX-002` em `backend/tests/integration/supervisao/test_sinais.py` cobrindo a **tabela-verdade inteira** de `T-005` — as seis combinações que produzem sinal, incluindo `EM_ANDAMENTO` antes do início e `EM_ANDAMENTO` depois do término, as três coerentes que não produzem, e as duas exclusões (`CANCELADO` e Evento sem `end_at`). *Combinação omitida é a que ninguém testa* (`FR-027`, `SC-009`)
- [X] T034 [US3] Implementar a detecção de `UX-002` em `backend/processo_seletivo/interface/supervisao.py`, apresentando **as duas** informações e sem arbitrar entre elas nem alterar o `status` (`FR-027`, `FR-023`)

### `UX-003` — Cobertura insuficiente

- [X] T035 [P] [US3] Teste de `UX-003` em `backend/tests/integration/supervisao/test_sinais.py`: o sinal traz numerador e denominador, e a inscrição **sem nenhum** avaliador conta como carente **e** permanece no denominador (`FR-028`, `FR-032`, `FR-033`, `SC-004`, `SC-006`)
- [X] T036 [US3] Implementar a detecção de `UX-003` em `backend/processo_seletivo/interface/supervisao.py` reusando `avaliacoes.application.selectors.resumo_da_etapa` como está, nomeando Etapa e Edital (`FR-028`, `FR-032`)

### `UX-004` — Ato vigente obsoleto

- [X] T037 [P] [US3] Teste de `UX-004` em `backend/tests/integration/supervisao/test_sinais.py`: ato obsoleto produz sinal sem abrir o marco; **e a contraprova** — fato posterior que não altera o universo do marco **não** produz sinal (`FR-029`)
- [X] T038 [US3] Implementar o filtro barato em `backend/processo_seletivo/interface/supervisao.py` com as **duas** condições de `T-003` — versão vigente do Edital diferente da citada pelo ato, **ou** `ResultadoEtapa` vigente nas Etapas do marco com `consolidado_em` posterior a `emitido_em`. *Conservador de propósito: admitir candidato que a confirmação descarta é barato; perder um é silencioso* (`T-003`)
- [X] T039 [US3] Confirmar cada candidato com `classificacao.application.selectors.estado_do_marco`, e emitir o sinal `UX-004` **apenas** com `obsoleto` verdadeiro, em `backend/processo_seletivo/interface/supervisao.py` (`FR-029`, `T-003`)

### `UX-005` — Comissão inteira impedida

- [X] T040 [P] [US3] Teste em `backend/tests/integration/supervisao/test_sinais.py`: com todos os membros ativos impedidos por autoria, o sinal aparece; bastando um desimpedido, ele some (`FR-030`, `SC-010`)
- [X] T041 [P] [US3] Teste da redação de `UX-005` em `backend/tests/interface/test_supervisao.py`: a mensagem nomeia a condição — todos os membros impedidos — e **não** afirma que o julgamento é impossível (`UX-005`, `FR-030a`)
- [X] T042 [US3] Implementar `UX-005` em `backend/processo_seletivo/interface/supervisao.py`: o conjunto de impedidos pelas cinco origens de `subject` de [data-model.md](./data-model.md) §3.5, comparado com a comissão ativa, **sem** iterar `recurso × membro` com o guardião individual, e com a redação de `UX-005` (`UX-005`, `FR-030`, `FR-031`)
- [X] T043 [US3] Teste de orçamento de consulta em `backend/tests/integration/supervisao/test_sinais.py` com `django_assert_num_queries`: dobrar o número de recursos pendentes **não** dobra as consultas (`FR-031`)

**Checkpoint**: os cinco sinais nascem e somem, um a um.

---

## Phase 6: User Story 4 — Do sinal ao lugar onde se resolve (Priority: P2)

**Goal**: encaminhamento por sinal e supressão silenciosa por alcance.

**Independent Test**: acionar o destino de cada sinal e conferir que chega à dona; e, com um ator
que não alcança uma das donas, conferir que aquele sinal simplesmente não está lá.

### Tests for User Story 4

- [X] T044 [P] [US4] Teste dos destinos em `backend/tests/interface/test_supervisao.py`: cada um dos cinco leva à tela dona correspondente (`FR-035`)
- [X] T045 [P] [US4] Teste da supressão em `backend/tests/integration/supervisao/test_autorizacao.py`: ator que preside mas não alcança os recursos não vê `UX-005`, **e nada indica a supressão**; e a contraprova de `FR-004a` — os agregados do Pulso continuam visíveis para esse mesmo ator (`FR-004`, `FR-004a`, `SC-013`)
- [X] T045a [P] [US4] Teste do Processo cancelado em `backend/tests/integration/supervisao/test_autorizacao.py`: a supervisão continua legível, **e o encaminhamento que a situação não admite não é oferecido** — a contraprova que falta a T049 (`FR-036`)
- [X] T046 [P] [US4] Teste de que a supervisão **não** lista os registros contados, em `backend/tests/interface/test_supervisao.py` (`FR-037`)

### Implementation for User Story 4

- [X] T047 [US4] Implementar o destino de cada sinal em `backend/processo_seletivo/interface/supervisao.py`, conforme a tabela de `T-008` (`FR-035`)
- [X] T048 [US4] Suprimir o sinal cujo destino o ator não alcança em `backend/processo_seletivo/interface/supervisao.py` — sem montar a forma, e sem marca de ausência (`FR-004`)
- [X] T049 [US4] Deixar a recusa para a tela de destino em `backend/processo_seletivo/interface/supervisao.py`: a supervisão decide **se oferece**, e não se autoriza. **Num Processo cancelado, encaminhamento que a situação não admite não é oferecido** — oferecer um beco é o que a `007` passou uma feature inteira tirando (`FR-036`)

**Checkpoint**: todas as user stories funcionam de forma independente.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T050 [P] Teste de fronteira em `backend/tests/integration/supervisao/test_fronteira.py`: a feature não escreve em tabela alguma, não apresenta carga por membro, não classifica desempenho e **não exibe nome, CPF nem protocolo de candidato** (`FR-006`, `FR-034`, `FR-004a`)
- [X] T051 [P] Acrescentar `test_a_022_nao_acrescenta_migration_aos_apps_que_ela_apenas_le` em `backend/tests/migrations/test_migrations.py`, no formato de guarda **por contagem de migrations por app** que a `017` e a `011` já usam — com a justificativa em comentário se alguma contagem subir por decisão de outra feature (`FR-007`, `SC-014`)
- [X] T052 [P] Teste de aceitação de ponta a ponta em `backend/tests/acceptance/test_supervisao_do_processo.py`: quem preside abre o Processo e obtém situação, volume, prazo e impedimento numa única tela (`SC-001`, `FR-005`)
- [X] T053 [P] Teste de orçamento da página inteira em `backend/tests/integration/supervisao/test_fronteira.py` com `django_assert_num_queries`: o custo cresce com o que mudou, e não com o tamanho do Processo (`T-002`, `T-003`)
- [X] T054 [P] Acrescentar a `022` à tabela de incrementos do `README.md`
- [X] T055 Executar [quickstart.md](./quickstart.md) inteiro — os cinco roteiros, com o papel exato de quem preside
  - **`UX-004` e `UX-005` percorridos em 2026-09-09**, pela interface, no banco `ps022_impl`. Eram os dois que faltavam: os testes automatizados os cobriam, e a demonstração não os havia montado.
  - `UX-004`: distribuir a inscrição sem avaliador em *Análise de títulos* (Edital 51/2026) → avaliar como `otavio.avaliador` → consolidar como `paulo.presidente`. O sinal apareceu **sem** abrir o marco, e o encaminhamento chegou à ordenação já com a divergência diagnosticada posição a posição. Emitido o sucessor, o sinal sumiu. **Contraprova da `T-003`**: um Resultado consolidado depois do ato, mas em Etapa que o marco **não** enumera (*Análise documental*), não trouxe o sinal de volta.
  - `UX-005`: impedimento declarado para `otavio.avaliador` na inscrição `INS-2026-20A31AC901`, recurso interposto pela candidata no portal contra o Resultado de *Análise de títulos* — avaliado por `joana.avaliadora` e consolidado por `paulo.presidente` —, admitido por um julgador de fora da comissão. Com os três membros alcançados, o sinal apareceu; incluído um quarto membro sem autoria, sumiu. A redação **não** afirma que o julgamento é impossível (`FR-030a`).
  - **A supressão do `UX-005` apareceu de graça** (`FR-004`, `SC-013`, Roteiro 4): `paulo.presidente` sem `recurso:julgar` não via o sinal, e nada na região indicava que houvesse algo oculto. `SC-012` conferido literalmente — a resposta do Processo existente para quem não tem vínculo é byte a byte a do Processo inexistente, normalizado o UUID que a página de erro do modo de depuração ecoa.
  - Conferidos também: soma do pulso contra as telas de inscrição de cada Edital (108 + 27 = 135), equivalente textual da série com os mesmos valores das barras e dia de zero presente, ausência de percentual sobre inscrição, e nenhuma rolagem horizontal a 375 px — a tabela larga rola dentro do próprio `.tabela-rolavel`.
- [X] T056 Executar `cd backend && make lint check test-pg`, e a varredura de citações por esta feature tocar `specs/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependência
- **Foundational (Fase 2)**: depende da Fase 1 — **bloqueia todas as user stories**
- **US1 (Fase 3)**: depende da Fase 2
- **US2 (Fase 4)**: depende de `US1` pela forma `PulsoDoEdital`
- **US3 (Fase 5)**: depende da Fase 2; **independente de `US1` e `US2`**
- **US4 (Fase 6)**: depende de `US3`, porque encaminha sinais
- **Polish (Fase 7)**: depende do que se quiser entregar

### Dentro de cada story

- Teste antes da implementação, e falhando antes
- Derivação em `supervisao.py` antes do template
- Sinal completo — detecção, redação e destino — antes do seguinte

### Conflitos de arquivo a respeitar

- `supervisao.py` é tocado por quase toda tarefa: **T013, T014, T021 a T025, T029, T032, T034, T036, T038, T039, T042 e T047 a T049 são sequenciais entre si**, e por isso nenhuma leva `[P]`
- `supervisao.html` é tocado por T006, T015 e T027 — sequenciais
- `test_pulso.py` reúne T010, T011, T017, T018, T018a e T020; `test_sinais.py` reúne T031, T033, T035, T037, T040 e T043. **Marcados `[P]` porque são escritos antes da implementação e podem ser distribuídos entre pessoas**, mas quem os escrever em série no mesmo arquivo evita conflito

### Parallel Opportunities

- T001 e T002 juntas
- T006 e T007 juntas, depois de T003 a T005
- Todos os testes de uma story marcados `[P]`, antes da implementação dela
- `US3` inteira em paralelo com `US1` e `US2`, por pessoas distintas
- Quase toda a Fase 7 em paralelo

---

## Parallel Example: User Story 3

```bash
# Os testes dos cinco sinais, antes de qualquer detecção:
Task: "T031 Teste de UX-001 em backend/tests/integration/supervisao/test_sinais.py"
Task: "T033 Teste de UX-002, com as duas ausências de sinal"
Task: "T035 Teste de UX-003, com o denominador preservado"
Task: "T037 Teste de UX-004, com a contraprova do fato posterior sem divergência"
Task: "T040 Teste de UX-005, com a comissão inteira impedida"
```

---

## Implementation Strategy

### MVP primeiro (apenas `US1`)

1. Fase 1 — Setup
2. Fase 2 — Foundational (bloqueia tudo)
3. Fase 3 — `US1`
4. **Pare e valide**: a soma no nível do Processo é capacidade que hoje não existe em lugar nenhum
5. Demonstre

### Entrega incremental

1. Setup + Foundational → a página existe e recusa corretamente
2. `US1` → o Processo acima do Edital — **MVP**
3. `US2` → o tempo; o Pulso fecha
4. `US3` → os cinco sinais, um a um, cada um demonstrável sozinho
5. `US4` → o encaminhamento, que é o que impede a tentação de listar

**Não adie `US4` por muito tempo depois de `US3`.** Sinal sem destino é aviso sem remédio, e a
pressão para listar na própria supervisão nasce exatamente aí.

---

## Cobertura de requisitos

| Requisito | Tarefas | Como |
|---|---|---|
| `FR-001` | T004, T005 | rota |
| `FR-002`, `FR-003` | T003, T004, T007 | teste |
| `FR-004`, `FR-004a` | T045, T048 | teste |
| `FR-005` | T009, T052 | aceitação |
| `FR-006` | T050 | teste |
| `FR-007` | T051 | teste |
| `FR-008` | T008 | reuso |
| `FR-009` | T014 | implementação |
| `FR-010` a `FR-012` | T010, T011, T013 | teste |
| `FR-013` | T018a, T022 | teste |
| `FR-014`, `FR-015` | T018, T023 | teste |
| `FR-016` | T019, T026, T027 | teste |
| `FR-017` | T012 | teste |
| `FR-018` | T020, T025 | teste |
| `FR-019` | T017, T021 | teste |
| `FR-020` | T015 | template |
| `FR-021` | T017, T024 | teste |
| `FR-022` | T020, T025 | teste |
| `FR-023` | T024, T034 | implementação |
| `FR-024` | T029, T030 | teste |
| `FR-025` | T029 | implementação |
| `FR-026` | T031, T032 | teste |
| `FR-027` | T033, T034 | teste |
| `FR-028` | T035, T036 | teste |
| `FR-029` | T037, T039 | teste |
| `FR-030`, `FR-030a` | T040, T041, T042 | teste |
| `FR-031` | T042, T043 | orçamento |
| `FR-032` | T028, T035 | forma |
| `FR-033` | T035 | teste |
| `FR-034` | T050 | teste |
| `FR-035` | T044, T047 | teste |
| `FR-036` | T045a, T049 | teste |
| `FR-037` | T046 | teste |
| `UX-001` a `UX-005` | T032, T034, T036, T039, T042 | implementação |
| `UX-006` | T006, T028, T029 | template |
| `UX-007` | T015 | template |
| `UX-008` | T026 | template |
| `SC-001` | T052 | aceitação |
| `SC-002`, `SC-003` | T010, T011 | teste |
| `SC-004`, `SC-006` | T035 | teste |
| `SC-005` | T012 | teste |
| `SC-007` | T010, T017 | teste |
| `SC-008` | T031 | teste |
| `SC-009` | T033 | teste |
| `SC-010` | T040 | teste |
| `SC-011` | T029 | teste |
| `SC-012` | T007 | teste |
| `SC-013` | T045 | teste |
| `SC-014` | T051 | teste |
| `SC-015` | T019 | teste |

---

## Notes

- `[P]` = arquivos distintos, sem dependência pendente
- Teste falhando antes da implementação, sempre
- Commit por tarefa ou grupo lógico
- Pare em qualquer checkpoint para validar a story isoladamente
- **A tarefa que pedir migration está errada.** `D-007` faz da necessidade de persistir estado um
  motivo para revisar a spec, não para escrever migration
