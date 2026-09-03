---

description: "Task list for feature implementation"
---

# Tasks: Consolidação do Resultado da Etapa

**Input**: Design documents from `/specs/013-consolidacao-resultado-etapa/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/resultado.md](./contracts/resultado.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos.** O princípio V nomeia avaliação, pontuação, autorização e concorrência
entre o que precisa de cobertura específica, e esta feature entrega as quatro. Além disso, a revisão
do plano encontrou quatro defeitos que só um teste teria denunciado depois — a inscrição eliminada
reaparecendo na Etapa 3, a pessoa impedida mantendo acesso, o Resultado nascendo contraditório e a
Mesa entregando o que a organização já excluía. Cada um deles tem tarefa de teste própria nesta
lista, nomeada pelo defeito.

**Organization**: por história de usuário, na ordem das quatro fatias da §6 do plano. US1 e US2 são
P1; US3 e US4 são P2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US4, conforme a spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. Um app
nasce nesta feature — `resultados` —, e as telas ficam em `interface`, na página que a 012 já usa
para a organização da Etapa.

> **⚠️ A suíte precisa de PostgreSQL, e aqui são quatro motivos.** Sem `TEST_DB_ENGINE=postgresql`
> ela cai para SQLite **sem avisar**, e deixam de ser verificados: a unicidade `(inscricao, etapa)`
> sob concorrência, a trigger append-only, a **trigger de coerência** e o `select_for_update`
> herdado de `comando_de_comissao`. Rode como o [quickstart](./quickstart.md) manda, com `DB_NAME`
> próprio deste worktree.

> **⚠️ O modelo nasce na Foundational, numa migration só, com as duas triggers.** As histórias
> recebem comandos, telas e comportamento — nunca esquema. E as duas triggers entram juntas: sem a
> de coerência, a append-only apenas congela o erro.

> **⚠️ Nenhuma tarefa desta lista acrescenta coluna a modelo da 012 nem toca conteúdo publicado.**
> Se alguma precisar de migration em `editais`, `publicacoes` ou `avaliacoes`, FR-041 foi violado.

> **⚠️ A progressão tem DUAS regras, e confundi-las já custou um buraco.** Eliminação em **qualquer**
> Etapa anterior exclui sempre, sem gate; a exigência de habilitação é da imediatamente anterior e só
> vale depois do primeiro Resultado dela. Se alguma tarefa consultar só a Etapa imediatamente
> anterior para excluir eliminados, a inscrição eliminada na Etapa 1 volta a aparecer na Etapa 3.

> **⚠️ O impedimento se aplica por inteiro.** Se alguma tarefa preservar Atribuição por ela
> fundamentar Resultado, a pessoa recém-declarada impedida continua abrindo a inscrição e os
> documentos dela — a cadeia de autorização não pergunta por impedimento, ela depende de ele ter
> inativado a Atribuição.

> **⚠️ Nenhuma tarefa desta lista verifica autorização dentro de laço de listagem.** Os dois
> conjuntos da progressão são resolvidos uma vez por listagem. A rota individual pode consultar o
> par — ela não é listagem, e o próprio docstring da 012 registra isso.

> **⚠️ `comando_de_comissao` não audita.** Ele abre transação, bloqueia, reautoriza e reserva
> idempotência; a trilha é chamada explícita, como a 011 e a 012 fazem em `auditar()`.

---

## Phase 1: Setup

**Purpose**: o app novo existe e é reconhecido pelo projeto.

- [X] T001 Criar o app em `backend/processo_seletivo/resultados/` com `__init__.py`, `apps.py`, `models.py`, `domain/`, `application/` e `migrations/`
- [X] T002 Registrar `processo_seletivo.resultados` em `backend/config/settings/base.py`, com o comentário que diz por que é app próprio e não um modelo dentro de `avaliacoes` (T-001)
- [X] T003 [P] Criar `backend/tests/unit/resultados/` e `backend/tests/integration/resultados/` com `__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a tabela, suas duas triggers, o privilégio, as três funções puras e o seletor de
conjuntos. **Nenhuma história começa antes.**

**⚠️ CRITICAL**: sem esta fase, nenhuma história tem onde gravar nem como decidir.

- [X] T004 Criar `ResultadoEtapa` em `backend/processo_seletivo/resultados/models.py` com os campos de [data-model.md](./data-model.md), `consequencia` em `TextChoices`, e `save()`/`delete()` recusando mutação — sem o campo `versao`, que é alcançado pela fonte (T-011)
- [X] T005 Escrever `backend/processo_seletivo/resultados/migrations/0001_initial.py` com a unicidade `(inscricao, etapa_id)`, o `OneToOne` sobre `Avaliacao`, os três checks, o índice `(edital, etapa_id)`, a trigger `resultado_etapa_coerente` `BEFORE INSERT` — inscrição, Etapa, Edital e pontuação conferidos contra a Avaliação fonte, mais `estado = CONCLUIDA` e **`Atribuicao.ativo = true`**, tudo pela junção que `Avaliacao.atribuicao` já obriga — e a trigger `resultado_etapa_append_only` `BEFORE UPDATE OR DELETE`, no molde de `publicacoes/migrations/0002_retificacoes.py`
- [X] T006 Acrescentar `resultados_resultadoetapa` a `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`, retirando `UPDATE` e `DELETE` do papel de runtime
- [X] T007 [P] Escrever `backend/processo_seletivo/resultados/domain/regra.py` com a tabela-verdade de T-003: consequência a partir de `eliminatory`, `minimum_score` e quantidade prevista, comparando `Decimal`, devolvendo motivo exibível ou a razão do impedimento. Sem consulta, sem modelo
- [X] T008 [P] Escrever `backend/processo_seletivo/resultados/domain/compatibilidade.py` comparando semanticamente os quatro campos de D-005 entre a Etapa da versão histórica e a vigente, normalizando decimais antes de comparar e tratando a ausência pelos leitores herdados (T-004)
- [X] T009 [P] Escrever `backend/processo_seletivo/resultados/domain/progressao.py` — puro — devolvendo a Etapa imediatamente anterior (maior `order` estritamente menor) e **a lista de todas as anteriores**, a partir do dicionário de Etapas vigentes (T-005)
- [X] T010 Escrever `backend/processo_seletivo/resultados/application/selectors.py` com `ha_resultado_em(...)`, `eliminadas_em(...)` e `habilitadas_em(...)`, cada um resolvendo um conjunto por consulta (T-005)
- [X] T011 [P] Teste unitário da regra em `backend/tests/unit/resultados/test_regra.py`, cobrindo as quatro linhas da tabela-verdade, **nota exatamente igual à mínima** e Etapa eliminatória sem nota mínima
- [X] T012 [P] Teste unitário da compatibilidade em `backend/tests/unit/resultados/test_compatibilidade.py`, incluindo `"60.0000"` contra `"60.00"` como compatíveis, versão sem a identidade da Etapa como incompatível, e **nome, cronograma, peso e caráter classificatório divergentes como compatíveis**
- [X] T013 [P] Teste unitário da progressão em `backend/tests/unit/resultados/test_progressao.py`, com ordem não contígua, primeira Etapa e Etapa ausente do vigente
- [X] T014 [P] Teste de integração das duas triggers em `backend/tests/integration/resultados/test_imutabilidade_do_resultado.py`: `UPDATE` e `DELETE` recusados, e `INSERT` recusado em cada uma das seis divergências — inscrição, Etapa, Edital, pontuação, Avaliação em `RASCUNHO` e **Avaliação sob Atribuição inativa**, esta última a que torna a invariante 2 uma garantia de banco
- [X] T015 [P] Conferir em `backend/tests/integration/test_imutabilidade_do_historico.py` e `test_database_permissions.py` que a tabela nova entrou nas duas varreduras sem ajuste manual
- [X] T016 [P] Teste de custo dos conjuntos em `backend/tests/performance/test_progressao.py`: o número de consultas não cresce com o número de inscrições

**Checkpoint**: a tabela existe, é imutável, não nasce contraditória, e as decisões de domínio são testáveis sem banco.

---

## Phase 3: User Story 1 — Enxergar a prontidão real da Etapa (Priority: P1) 🎯 MVP

**Goal**: a organização da Etapa passa a dizer quantas inscrições podem ser consolidadas e por que
as demais não podem, sem tela nova.

**Independent Test**: preparar inscrições sem avaliação, com avaliação elegível, com versão
incompatível, aguardando Etapa anterior e já eliminadas; abrir a organização e conferir que
contagens, filtros e motivos particionam exatamente a população.

- [X] T017 [US1] Escrever `backend/processo_seletivo/resultados/application/prontidao.py` classificando cada participante em pendente, pronta, consolidada ou impedida por motivo, consumindo o conjunto elegível herdado da 012 e a compatibilidade de T008
- [X] T018 [US1] Ampliar `resumo_da_etapa` em `backend/processo_seletivo/avaliacoes/application/selectors.py` com participantes, aguardando anterior, eliminadas anteriormente, pendentes, prontas, consolidadas e impedidas — **na mesma agregação**, com `Count` condicional, recebendo os conjuntos da progressão como parâmetro (T-008)
- [X] T019 [US1] Acrescentar o filtro de prontidão a `inscricoes_da_etapa` em `backend/processo_seletivo/avaliacoes/application/selectors.py`, sem criar segunda listagem
- [X] T020 [US1] Passar o contexto novo em `backend/processo_seletivo/interface/views.py`, na view `distribuicao`, resolvendo os conjuntos **uma vez** antes de montar resumo e linhas
- [X] T021 [US1] Estender `backend/processo_seletivo/interface/templates/interface/distribuicao.html` com as contagens e os filtros de prontidão, sem criar página paralela de Resultado (D-004)
- [X] T022 [P] [US1] Teste de aceitação da partição em `backend/tests/acceptance/test_resultado_da_etapa.py`: a soma dos estados de prontidão é igual ao total de participantes, e nenhuma inscrição aparece em dois
- [X] T023 [P] [US1] Teste de custo em `backend/tests/performance/test_resumo_da_etapa.py`: o resumo continua sendo uma agregação e o número de consultas não cresce com as inscrições
- [X] T024 [P] [US1] Teste de integração dos motivos em `backend/tests/integration/resultados/test_prontidao.py`: cada impedimento tem frase acionável, e Etapa que prevê mais de uma avaliação impede a Etapa inteira nomeando a quantidade publicada

**Checkpoint**: a presidência enxerga o que pode consolidar e o que a impede, antes de existir qualquer Resultado.

---

## Phase 4: User Story 2 — Consolidar Resultados em lote (Priority: P1)

**Goal**: as avaliações concluídas viram consequência rastreável num ato confirmado, sem transcrever
pontuação.

**Independent Test**: selecionar num único envio inscrições prontas, pendentes e já consolidadas;
confirmar e verificar que as prontas recebem Resultado, as demais são recusadas com motivo e a
repetição da mesma chave devolve exatamente o desfecho original.

- [X] T025 [US2] Escrever `backend/processo_seletivo/resultados/application/consolidacao.py` sob `comando_de_comissao(..., operation="resultado:consolidar")`, devolvendo `ctx.desfecho_anterior` quando `ctx.repetido`, resolvendo elegíveis, Resultados existentes e conjuntos da progressão **antes** do laço, e fechando com `ctx.concluir_sem_resultado(201, resultado)`
- [X] T026 [US2] Montar o desfecho em `backend/processo_seletivo/resultados/application/consolidacao.py` com `resultado_declarado(criados, recusas, "consolidada")`, com o catálogo de recusas de item da §4 do [contrato](./contracts/resultado.md)
- [X] T027 [US2] Emitir, em `backend/processo_seletivo/resultados/application/consolidacao.py`, um evento de auditoria por Resultado criado, com ator, base autorizadora, agregado, correlação e chave — **sem pontuação nem parecer** na trilha
- [X] T028 [US2] Acrescentar a rota `editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/consolidar` em `backend/processo_seletivo/interface/urls.py`
- [X] T029 [US2] Implementar a view de consolidação em `backend/processo_seletivo/interface/views.py`, com chave de idempotência gerada por render e o desfecho preservado na sessão, como a distribuição já faz
- [X] T030 [US2] Acrescentar a ação e a exibição do desfecho agrupado por motivo em `distribuicao.html`, sem campo de pontuação, consequência ou justificativa
- [X] T031 [P] [US2] Teste de aceitação do lote misto em `backend/tests/acceptance/test_resultado_da_etapa.py`: prontas, pendentes e já consolidadas na mesma submissão
- [X] T032 [P] [US2] Teste de idempotência em `backend/tests/integration/resultados/test_consolidacao_idempotente.py`: mesma chave e mesmo conteúdo devolve o desfecho original sem evento novo; mesma chave e conteúdo diferente conflita; chave nova sobre par consolidado recusa o item
- [X] T033 [US2] Teste de concorrência em `backend/tests/integration/resultados/test_consolidacao_idempotente.py`: duas transações consolidando a mesma inscrição produzem exatamente um Resultado, e a perdedora recebe desfecho explícito, sem erro de integridade vazando
- [X] T034 [P] [US2] Teste de volume em `backend/tests/performance/test_consolidacao_em_lote.py`: um envio com **1.000** inscrições prontas consolida numa submissão só, sem interação por inscrição e sem consulta por linha dentro do laço (SC-002)
- [X] T035 [P] [US2] Teste de contrato em `backend/tests/contract/test_consolidacao.py`: seleção vazia, Etapa de leitura múltipla e Etapa eliminatória sem nota mínima são **erro do pedido**, e nenhuma criação acontece
- [X] T036 [P] [US2] Teste de autorização em `backend/tests/authorization/test_consolidacao.py`: quem não preside recebe 404 uniforme, e a autorização é reavaliada **dentro** do ato protegido

**Checkpoint**: US1 + US2 entregam a jornada central — ver o que está pronto e transformá-lo em Resultado.

---

## Phase 5: User Story 3 — Prosseguir somente com quem foi habilitado (Priority: P2)

**Goal**: a Etapa seguinte usa os Resultados da anterior para definir seus participantes, em todas
as seis superfícies que hoje devolvem inscrição por Etapa.

**Independent Test**: consolidar a primeira Etapa com uma habilitada e uma eliminada; abrir a
distribuição e a Mesa da segunda e comprovar que somente a habilitada pode ser distribuída, contada
e acessada — e que a terceira Etapa continua excluindo a eliminada mesmo sem Resultado na segunda.

- [X] T037 [US3] Recusar em `_inscricoes_atribuiveis`, em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`, a inscrição excluída pela progressão — como **erro do pedido** (`inscricao_fora_da_etapa`, 422), na mesma classificação já usada para inscrição não submetida
- [X] T038 [US3] Acrescentar a terceira pergunta a `pode_avaliar_inscricao` em `backend/processo_seletivo/avaliacoes/domain/autorizacao.py`, **só na rota individual**, atualizando o docstring que hoje afirma "duas condições, e não três" para registrar por que a terceira cabe ali e não em listagem
- [X] T039 [US3] Fazer `_autorizar` em `backend/processo_seletivo/avaliacoes/application/mesa.py` herdar a decisão, cobrindo a inscrição de trabalho e a entrega de documento
- [X] T040 [US3] Filtrar `mesa(...)` em `backend/processo_seletivo/avaliacoes/application/selectors.py` pelos conjuntos da progressão, resolvidos uma vez por listagem
- [X] T041 [US3] Filtrar `proxima_pendente(...)` em `backend/processo_seletivo/avaliacoes/application/selectors.py` — sem isso, a navegação entrega a inscrição excluída **sem que ninguém a peça pelo identificador**
- [X] T042 [US3] Ajustar `carga_nas_etapas(...)` em `backend/processo_seletivo/avaliacoes/application/selectors.py`, para que Minhas Etapas não anuncie trabalho que não existe mais
- [X] T043 [P] [US3] Teste de aceitação da **transitividade** em `backend/tests/acceptance/test_resultado_da_etapa.py`: eliminada na Etapa 1, com a Etapa 2 sem nenhum Resultado, continua fora da Etapa 3
- [X] T044 [US3] Teste de aceitação do **gate dormente** em `backend/tests/acceptance/test_resultado_da_etapa.py`: Edital cuja Etapa 1 prevê duas avaliações mantém a Etapa 2 distribuível com todas as submetidas
- [X] T045 [P] [US3] Teste de autorização em `backend/tests/authorization/test_progressao.py`: inscrição excluída responde **404 uniforme** na Mesa, na inscrição de trabalho, no documento e na próxima pendente — e trocar o identificador na URL não alcança nada
- [X] T046 [P] [US3] Teste de contrato em `backend/tests/contract/test_distribuicao_com_progressao.py`: distribuir inscrição excluída pela progressão responde 422 `inscricao_fora_da_etapa` — **erro do pedido**, e não recusa de linha —, e nenhuma Atribuição é criada (FR-007)
- [X] T047 [P] [US3] Teste de custo em `backend/tests/performance/test_progressao.py`: nenhuma listagem passa a verificar autorização por linha
- [X] T048 [P] [US3] Teste de não regressão em `backend/tests/integration/resultados/test_nao_regressao_012.py`: a primeira Etapa conserva integralmente o comportamento da 012, e a Atribuição criada enquanto a exigência estava dormente volta a autorizar quando o Resultado habilitador existe

**Checkpoint**: a eliminação produz efeito operacional, e nenhuma porta da 012 ficou aberta.

---

## Phase 6: User Story 4 — Consultar a decisão e sua origem (Priority: P2)

**Goal**: cada Resultado é consultável com a Avaliação, a regra, o autor e o instante que o
fundamentaram — e as entradas da decisão ficam fechadas para reabertura.

**Independent Test**: consolidar, publicar uma Retificação não retroativa e remover o avaliador da
comissão; consultar o Resultado e reproduzir total, consequência, fonte normativa e duas autorias.

- [X] T049 [US4] Escrever o seletor de Resultados em `backend/processo_seletivo/resultados/application/selectors.py`, com `select_related("avaliacao__versao")` para a proveniência, paginação e filtro por consequência
- [X] T050 [US4] Acrescentar a rota `editais/<uuid:edital_id>/distribuicao/<uuid:etapa_id>/resultados` em `urls.py` e a view em `views.py`, aberta à presidência e a `auditoria:consultar`, pela mesma porta das conclusões preservadas
- [X] T051 [US4] Criar `backend/processo_seletivo/interface/templates/interface/resultados.html` mostrando pontuação, consequência e motivo, Avaliação fonte, versão normativa, quem avaliou, quem consolidou e quando — marcado como não armazenável pelo navegador
- [X] T052 [US4] Acrescentar o guard em `reabrir`, em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`, entre a localização da Avaliação e o `compare_and_swap`: 409 `avaliacao_fundamenta_resultado`, nomeando inscrição e Etapa **sem expor pontuação**
- [X] T053 [US4] Acrescentar `resultados_contestados` ao desfecho de `registrar_impedimento`, em `backend/processo_seletivo/avaliacoes/application/impedimento.py` — **declaração, não decisão**: nenhuma Atribuição é preservada e nenhum Resultado é alterado
- [X] T054 [US4] Exibir a contestação superveniente junto do Resultado em `resultados.html`, para que quem consulta saiba que a origem foi contestada depois
- [X] T055 [P] [US4] Teste de aceitação da proveniência em `backend/tests/acceptance/test_resultado_da_etapa.py`: depois de Retificação não retroativa e da saída do avaliador da comissão, total, consequência, fonte normativa e as duas autorias continuam reproduzíveis
- [X] T056 [P] [US4] Teste de integração do guard em `backend/tests/integration/resultados/test_fechamento_das_entradas.py`: a reabertura é recusada antes de qualquer efeito, a Avaliação conserva estado e revisão, e a trilha não ganha evento
- [X] T057 [P] [US4] Teste de autorização em `backend/tests/authorization/test_impedimento_superveniente.py`: registrado o impedimento, a pessoa impedida acessa **zero** inscrições alcançadas — inclusive a que fundamenta Resultado — na Mesa, na inscrição de trabalho e no documento (SC-009)
- [X] T058 [US4] Teste de não regressão em `backend/tests/integration/resultados/test_fechamento_das_entradas.py`: reabrir avaliação **não** consolidada continua funcionando exatamente como na 012
- [X] T059 [P] [US4] Teste de autorização em `backend/tests/authorization/test_consulta_de_resultado.py`: auditoria consulta e **não** adquire poder de consolidar; identificador de outro escopo responde 404
- [X] T060 [P] [US4] Teste de integração em `backend/tests/integration/resultados/test_armazenamento_da_consulta.py`: a resposta de `.../resultados` carrega `SEM_ARMAZENAMENTO` — a varredura de `backend/tests/test_armazenamento_no_navegador.py` alcança só `portal/`, e nunca `interface/`, de modo que esta garantia não tem cobertura automática (FR-039)

**Checkpoint**: a decisão é demonstrável, a entrada está fechada para reabertura, e a contestação superveniente é visível.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T061 [P] Escrever `specs/013-consolidacao-resultado-etapa/traceability.md` ligando os 45 requisitos e os 11 critérios a tarefa, arquivo e teste, como a 011 e a 012 fizeram
- [X] T062 Executar `specs/013-consolidacao-resultado-etapa/quickstart.md` inteiro pela interface administrativa, incluindo o passo 4 da Entrega 4 e o passo 4 da Entrega 5 — os dois que provam as correções da revisão
- [ ] T063 [P] Conferir `backend/processo_seletivo/interface/templates/interface/distribuicao.html` e `resultados.html` em 375 px, sem tabela horizontal
- [X] T064 [P] Rodar `ruff format --check` e `ruff check` sobre `backend/` — é portão de CI desde a 012
- [X] T065 [P] Rodar `backend/tests/test_citacoes_de_requisito.py`: toda citação de FR e SC no código novo aponta para requisito que existe
- [X] T066 [P] Escrever a varredura de vocabulário em `backend/tests/test_vocabulario_do_resultado.py`: nenhum template nem resposta da 013 afirma colocação, classificação, aprovação final, ocupação de vaga ou direito à convocação (FR-045)
- [X] T067 Rodar `backend/tests/` inteira com `TEST_DB_ENGINE=postgresql` e `DB_NAME` próprio, confirmando que nenhum teste da 011 ou da 012 regrediu

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup — **bloqueia todas as histórias**
- **US1 (Phase 3)** e **US2 (Phase 4)**: dependem da Foundational. US2 depende de US1 apenas para a tela, não para o comando
- **US3 (Phase 5)**: depende de US2, porque o filtro de progressão só tem o que ler depois que existem Resultados
- **US4 (Phase 6)**: depende de US2 pelo mesmo motivo; os guards só têm o que proteger depois do primeiro Resultado
- **Polish (Phase 7)**: depende de tudo

### Within Each User Story

- Domínio antes de aplicação, aplicação antes de rota, rota antes de template
- Testes de uma história podem ser escritos em paralelo entre si, e devem falhar antes da implementação correspondente
- História completa antes de passar à próxima prioridade

### Parallel Opportunities

- T007, T008 e T009 são três arquivos independentes de domínio puro — paralelos
- T011 a T016 são seis arquivos de teste independentes — paralelos
- Em cada história, todas as tarefas marcadas [P] são arquivos distintos. T033, T044 e T058 **não**
  levam [P] de propósito: cada uma escreve no mesmo arquivo de teste que a tarefa imediatamente
  anterior, e duas mãos no mesmo arquivo não é paralelismo, é conflito
- **US3 e US4 podem ser trabalhadas em paralelo por pessoas diferentes** depois de US2: uma toca as seis superfícies da 012, a outra toca consulta e guards

---

## Parallel Example: Foundational

```bash
# As três funções de domínio puro, juntas:
Task: "Escrever resultados/domain/regra.py com a tabela-verdade de T-003"
Task: "Escrever resultados/domain/compatibilidade.py com os quatro campos de D-005"
Task: "Escrever resultados/domain/progressao.py com a Etapa anterior e todas as anteriores"

# Os seis testes da fundação, juntos:
Task: "Teste unitário da regra em tests/unit/resultados/test_regra.py"
Task: "Teste unitário da compatibilidade em tests/unit/resultados/test_compatibilidade.py"
Task: "Teste unitário da progressão em tests/unit/resultados/test_progressao.py"
Task: "Teste das duas triggers em tests/integration/resultados/test_imutabilidade_do_resultado.py"
```

---

## Implementation Strategy

### MVP (US1 + US2)

1. Phase 1 e Phase 2 — a tabela existe e as decisões são testáveis
2. Phase 3 — a presidência enxerga o que pode consolidar
3. Phase 4 — e consolida
4. **PARE e VALIDE**: as Entregas 1 a 3 do quickstart passam de ponta a ponta

Neste ponto a planilha já saiu do caminho, que é o problema da §3 da spec.

### Incremental Delivery

1. Setup + Foundational → fundação pronta
2. US1 → prontidão visível → demonstrável
3. US2 → Resultado em lote → **MVP**
4. US3 → a eliminação produz efeito operacional
5. US4 → a decisão é auditável e a entrada está fechada

### Ordem que não deve ser invertida

US3 e US4 **depois** de US2. Antecipá-las produz código com um único caminho testável — o de nunca
haver Resultado —, e foi assim que a primeira versão do plano subestimou o risco delas.

---

## Notes

- [P] = arquivos diferentes, sem dependência
- Verifique que o teste falha antes de implementar
- Commit por tarefa ou por grupo lógico
- Pare em qualquer checkpoint para validar a história isoladamente
- **Se uma tarefa exigir migration fora de `resultados`, ou verificação por linha em listagem, ou preservar Atribuição por existir Resultado, ou consultar só a Etapa imediatamente anterior para excluir eliminados — a decisão correspondente da spec foi violada, e a resposta é voltar à spec, não improvisar no código**
