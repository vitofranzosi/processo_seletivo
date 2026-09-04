---

description: "Task list for feature implementation"
---

# Tasks: revisão de compatibilidade 012–013 — a Etapa publica a forma da conclusão

**Input**: Design documents from `/specs/012-013-revisao-formas-de-conclusao/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/forma-da-conclusao.md](./contracts/forma-da-conclusao.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos.** Esta revisão troca o significado de um invariante de banco em três
tabelas **com dados históricos**, e a Constituição pede cobertura específica para regra normativa e
para migração. Além disso, dois defeitos já foram encontrados no papel e cada um tem tarefa de teste
própria, nomeada pelo defeito: a constraint que reprovaria toda avaliação concluída por falta de
backfill, e a conferência que aprovaria qualquer sentido porque `NULL IS DISTINCT FROM NULL` é falso.

**Organization**: por história de execução. As sete são as **E1 a E7** do [mapa de execução](./spec.md),
e aparecem aqui como US1 a US7 na mesma ordem — que é a ordem de dependência, e não a de prioridade.
Seis são P1; **US4 é a única P2** e é a única que pode ser adiada sem bloquear as demais.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: paralelizável **entre si, dentro do seu grupo** — arquivos diferentes, sem dependência
  mútua. Um teste marcado `[P]` depende da implementação da sua própria história; o que a marca diz é
  que ele não depende dos **outros** testes marcados ao lado dele
- **[Story]**: US1 a US7, conforme o mapa de execução da spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`, contrato
em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`. **Nenhum app novo, nenhuma rota
nova, nenhuma permissão nova.**

> **⚠️ A suíte precisa de PostgreSQL, e aqui a lista é longa.** Sem `TEST_DB_ENGINE=postgresql` ela
> cai para SQLite **sem avisar**, e deixam de ser verificados: as duas `CheckConstraint` que alternam
> por forma, a trigger de coerência do Resultado, as duas triggers append-only e o teste de upgrade
> inteiro. Rode com `DB_NAME` próprio deste worktree, como manda o [quickstart](./quickstart.md).

> **⚠️ Antes da primeira linha, registre o baseline verde — por identidade, e não por contagem.**
> Rode a suíte inteira e guarde a **lista de node IDs** (`--collect-only -q`), não o total: a revisão
> acrescenta testes, e a contagem cresce de propósito. O que FR-124 e FR-050 cobram é que todo teste
> que existia continue existindo e passando.
>
> **Três asserções vão mudar, e já se sabe quais**: `tests/contract/test_forma_publicada.py:315` e
> `tests/integration/editais/test_contrato_de_inscricao.py:65` fixam `schemaVersion == 5`, e
> `tests/unit/avaliacoes/test_precondicao_de_grafia.py` usa a versão 5 como entrada. Nenhuma delas é
> comportamento da forma pontuada — são o literal da versão canônica, que este incremento sobe. Toda
> alteração de asserção fora dessa natureza é regressão até prova em contrário.

> **⚠️ Todo o esquema nasce na Foundational, e as histórias recebem comportamento, tela e teste.**
> Se alguma tarefa de US1 a US7 precisar de migration, a fatia foi montada errada.

> **⚠️ Três backfills, e esquecer qualquer um derruba a migration.** O PostgreSQL valida a tabela
> inteira ao criar a constraint: `Avaliacao` **concluída**, `ConclusaoAvaliacao` e `ResultadoEtapa`
> recebem `forma = 'PONTUADA'`. **Rascunho de Avaliação permanece sem forma** — ela é lida no ato de
> concluir, e carimbá-la no nascimento faria um rascunho aberto hoje concluir na forma antiga.

> **⚠️ `forma` não é anulável no conteúdo publicado da v6.** A ausência é lida como pontuada em
> conteúdo **anterior** à v6, e só ali. Admitir `null` na v6 criaria duas grafias canônicas para a
> mesma versão, e é isso que a versão canônica existe para impedir.

> **⚠️ A conferência do Resultado não alterna por forma.** Ela compara `forma`, `pontuacao` e
> `sentido` — os três, sempre. Alternar aprovaria qualquer sentido na forma decisória, porque a
> comparação de pontuação entre dois nulos resolve como igualdade.

---

## Phase 1: Setup (vocabulário compartilhado)

**Purpose**: os dois enums e a leitura da ausência, antes de qualquer coisa depender deles

- [X] T001 [P] Criar `Forma` (`PONTUADA`, `DECISORIA`) e `Sentido` (`FAVORAVEL`, `DESFAVORAVEL`) em `backend/processo_seletivo/avaliacoes/domain/formas.py`, com a razão de o rótulo publicado **não** morar aqui (D-008.2)
- [X] T002 Acrescentar `forma_publicada(etapa)` e `rotulos(etapa)` a `backend/processo_seletivo/avaliacoes/domain/previsao.py`, mantendo o contrato do arquivo — a ausência interpretada num lugar só, e `PONTUADA` como o que ela significa (012, FR-120)
- [X] T003 Testar os dois leitores em `backend/tests/unit/avaliacoes/test_previsao.py`: **ausência** e `null` são lidos como `PONTUADA` — o leitor é defensivo de propósito, embora o validador de publicação recuse `null` na v6 (TR-003) —, valor literal atravessa, e valor fora do enum cai em `PONTUADA` sem estourar, como `avaliacoes_previstas` já faz com lixo

**Checkpoint**: o vocabulário existe e é lido de um lugar só

---

## Phase 2: Foundational (o segundo incremento e todo o esquema)

**Purpose**: a norma publicada e as três migrations. **Bloqueia todas as histórias.**

**⚠️ CRITICAL**: nenhuma história começa antes de **T022** — a Foundational só termina quando o salto de versão está provado com dados

### O contrato e a validação

- [X] T004 [P] Declarar `forma` (`required`, `type: string`, `enum: [PONTUADA, DECISORIA]`, **sem `'null'`**) e os dois rótulos (`required`, `type: [string, 'null']`) em `EtapaPublicada`, e os três em `EtapaInput` — ali `forma` entra em `properties` como `type: string` com `enum`, e **fora** de `required`, que hoje é `[id, name]`: omissão é legal na entrada e `null` é recusado pelo próprio esquema, que é a metade contratual da regra do serializer (T010) —, em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, atualizando a `description` para a versão canônica 6 (TR-013)
- [X] T005 Acrescentar os três `Campo` a `ETAPA_PUBLICADA` em `backend/processo_seletivo/editais/domain/validation.py`, com `forma` **não anulável** e os rótulos anuláveis (TR-003)
- [X] T006 Estender `_coerencia_das_etapas` em `backend/processo_seletivo/editais/domain/validation.py` com a condicionalidade por forma: rótulos exigidos em `DECISORIA` e proibidos em `PONTUADA`; `minimumScore` e `maximumScore` **presentes e nulos** em `DECISORIA` — o que se recusa é o valor, porque a chave está sempre lá; rótulo em branco ou só espaços recusado como ausente
- [X] T007 Cobrir os limites de borda dos três campos em `backend/tests/contract/test_limites_de_borda.py` (depende de T005 e T006)

### A versão canônica e a elaboração

- [X] T008 Subir `SCHEMA_VERSION` para 6 em `backend/processo_seletivo/shared/canonical.py`, registrando o segundo incremento no mesmo formato em que o arquivo registra os quatro anteriores — e dizendo que ele nasce de mudança de requisito, não de omissão do primeiro
- [X] T009 Acrescentar `forma` — **não anulável, `default="PONTUADA"`** — e `rotulo_favoravel` e `rotulo_desfavoravel` — anuláveis, sem default — à Etapa de elaboração em `backend/processo_seletivo/editais/models/etapas.py`, o pacote `models/` e não um módulo único, **com migration** em `backend/processo_seletivo/editais/migrations/`. O default é o que mantém publicável todo Edital **já em elaboração**: sem ele, `_stages()` transcreveria `forma: null` e a publicação seria recusada por `field_null_invalid` (TR-003)
- [X] T010 [P] Aceitar os três campos no `StageSerializer` de `backend/processo_seletivo/editais/api/serializers.py`, aplicando `PONTUADA` quando `forma` vier **omitida** e recusando `forma: null` explícito — omissão e nulo não são a mesma coisa e não recebem a mesma resposta —, e propagar no rascunho de `backend/processo_seletivo/editais/application/draft.py` **sem converter ausência em `None`**, que contornaria o default do modelo (TR-003)
- [X] T011 [P] Transcrever os três para o snapshot em `backend/processo_seletivo/publicacoes/application/publish_edital.py`

### A elevação

- [X] T012 Converter `backend/processo_seletivo/publicacoes/domain/elevacao.py` em **cadeia de degraus** — 4 → 5 → 6 —, com o degrau novo escrevendo `forma = "PONTUADA"` e os rótulos nulos, preservando idempotência, alcance restrito ao fluxo de Retificação e a elevação path-aware do `newValue` de cada ato (TR-001, TR-002)
- [X] T013 Estender `diz_o_mesmo_que_a_ausencia` em `backend/processo_seletivo/publicacoes/domain/elevacao.py` para aceitar `forma` ausente **ou** `"PONTUADA"` com rótulos nulos como a mesma coisa, e conferir o efeito em `backend/processo_seletivo/publicacoes/domain/conflicts.py`
- [X] T014 Exercitar a cadeia em `backend/tests/unit/avaliacoes/test_elevacao.py` e a equivalência de grafias em `backend/tests/unit/avaliacoes/test_precondicao_de_grafia.py`: v4 sobe dois degraus, v5 sobe um, v6 atravessa inalterado, e nenhuma grafia equivalente vira conflito

### O esquema da conclusão e do Resultado

- [X] T015 Acrescentar `forma` e `sentido` a `Avaliacao` **e** a `ConclusaoAvaliacao` em `backend/processo_seletivo/avaliacoes/models.py`, com **duas** verificações de banco nomeadas — `ck_avaliacao_concluida_completa` reescrita para alternar por forma, e `ck_conclusao_completa_por_forma` nova na tabela append-only, que hoje garante completude por `NOT NULL` e deixa de poder fazê-lo —, relaxando `ConclusaoAvaliacao.pontuacao` (TR-004, TR-005)
- [X] T016 Escrever a migration de `backend/processo_seletivo/avaliacoes/migrations/` que acrescenta as quatro colunas anuláveis, faz os **dois backfills** — `Avaliacao` só onde `estado = 'CONCLUIDA'`, e `ConclusaoAvaliacao` inteira, esta pelo `DEFAULT` do `ADD COLUMN` com `preserve_default=False` —, e só então cria as duas constraints (TR-004a, TR-005)
- [X] T017 Acrescentar `forma` e `sentido` a `ResultadoEtapa` em `backend/processo_seletivo/resultados/models.py`, relaxar `pontuacao` e criar `ck_resultado_completo_por_forma` — a verificação que alterna, hoje inexistente porque `pontuacao` era `NOT NULL` (TR-006)
- [X] T018 Escrever a migration de `backend/processo_seletivo/resultados/migrations/` com **`dependencies` explícita na migration criada em T016**, porque o SQL de `check_stage_result_source()` lê `avaliacoes_avaliacao.forma` e `.sentido` e o grafo do Django não infere isso da ordem das tarefas; ela acrescenta as colunas, faz o backfill pelo `DEFAULT` do `ADD COLUMN`, cria a constraint e reescreve a trigger para comparar **forma, pontuação e sentido incondicionalmente** (TR-006)

### A regra da 013 que precisa mudar antes de qualquer Resultado decisório

- [X] T019 Condicionar à forma, em `backend/processo_seletivo/resultados/domain/regra.py`, a recusa que hoje é incondicional: `impedimento_da_regra` só exige nota mínima de Etapa eliminatória **na forma pontuada** (013, FR-048). Sem isto, análise documental eliminatória e sem mínima — a configuração real dos Editais 35 e 57 — é recusada, e nenhuma tarefa de US5 consegue consolidar. O caso **simétrico**, da decisória não eliminatória, é de US6 e não entra aqui
- [X] T020 Testar em `backend/tests/unit/resultados/test_regra.py` que Etapa decisória eliminatória e sem nota mínima **não** cai em regra insuficiente, e que a pontuada eliminatória e sem mínima continua caindo (depende de T019)

### A prova do salto — junto das migrations, e não no fim

- [X] T021 Incluir `avaliacoes` e `resultados` em `APPS`, e `conclusao_avaliacao_append_only`, `resultado_etapa_append_only` e `resultado_etapa_coerente` em `TRIGGERS`, em `backend/tests/migrations/test_migrations.py` — hoje nenhuma migration desses dois apps é exercida por teste de upgrade
- [X] T022 Escrever, em `backend/tests/migrations/test_migrations.py`, o teste `postgresql_only` que aplica as migrations até o estado anterior, cria Avaliação concluída, rascunho, conclusão preservada e Resultado pontuados, aplica as três migrations novas e confere os três backfills, o rascunho **sem** forma e as três triggers no lugar; e recusa a reversão, nomeando o ato administrativo que precisa vir antes, quando já existe conclusão decisória (TR-014)

**Checkpoint**: a norma está publicada, o esquema mudou de significado e o salto está provado com dados

---

## Phase 3: US1 — Publicar uma Etapa decisória (Priority: P1) 🎯 MVP

**Goal**: quem elabora consegue declarar que a Etapa não pontua, e publicar os rótulos que o Edital escolheu.

**Independent Test**: [Jornada 1](./quickstart.md) — publicar uma Etapa decisória e ver `forma` e os dois rótulos no snapshot, com `schemaVersion` 6.

- [X] T023 [P] [US1] Ler e escrever os três campos no formulário de Etapa em `backend/processo_seletivo/interface/forms.py`
- [X] T024 [US1] Alternar o formulário por forma em `backend/processo_seletivo/interface/templates/interface/_etapa.html`: nota mínima e máxima na pontuada, par de rótulos na decisória, com "Deferido"/"Indeferido" como **prefill editável e não default normativo**
- [X] T025 [US1] Tornar o formulário condicional de Etapa operável por teclado e legível por leitor de tela em `backend/processo_seletivo/interface/templates/interface/_etapa.html`: a troca de forma anuncia que os campos mudaram, cada rótulo é associado ao seu controle, e a recusa continua ancorada no campo por `aria-describedby`, como o arquivo já faz com `recusa-etapa-…`
- [X] T026 [P] [US1] Exibir a Etapa por forma no resumo de `backend/processo_seletivo/interface/revisao.py`
- [X] T027 [P] [US1] Testar a publicação de uma Etapa decisória em `backend/tests/integration/interface/test_compor.py`: o snapshot traz forma e rótulos, e `schemaVersion` é 6
- [X] T028 [P] [US1] Testar em `backend/tests/integration/editais/` que um Edital criado **antes** da migration continua publicável sem edição nenhuma: as Etapas dele saem no snapshot como `PONTUADA`, e o conteúdo publicado é idêntico ao que seria antes da revisão, exceto pelos três campos novos
- [X] T029 [P] [US1] Testar em `backend/tests/contract/test_edital_draft_api.py` que `forma` omitida no `StageSerializer` vale `PONTUADA` e que `forma: null` explícito é recusado — e que o rascunho gravado não guarda `None`
- [X] T030 [P] [US1] Testar as recusas em `backend/tests/unit/editais/test_etapas.py`: decisória sem rótulo, decisória com pontuação máxima, rótulo em branco, e `forma` fora do enum — cada uma com o código declarado no [contrato](./contracts/forma-da-conclusao.md)

**Checkpoint**: existe Edital publicado cuja Etapa declara que não pontua

---

## Phase 4: US2 — Retificar, inclusive o que foi publicado antes do salto (Priority: P1)

**Goal**: nenhum Edital fica irretificável por evolução de esquema, e a forma é corrigível pelo canal institucional.

**Independent Test**: [Jornadas 5 e 6](./quickstart.md) — retificar um Edital v5 e retificar a forma de uma Etapa.

- [X] T031 [US2] Completar `CAMPOS_ETAPA` em `backend/processo_seletivo/interface/retificacao.py` com **todos** os campos normativos da Etapa: os cinco atuais, `maximumScore` e `evaluationsPerRegistration` que o primeiro incremento deixou para trás, e os três novos (012, D-008.10)
- [X] T032 [P] [US2] Escrever, em `backend/tests/contract/test_retificacoes_api.py`, a guarda que compara `CAMPOS_ETAPA` com um **conjunto declarado explicitamente** — os campos normativos da Etapa, isto é `ETAPA_PUBLICADA` menos `id`, `order` e `scheduleEventId`, cada exclusão justificada em comentário (identidade, insumo da progressão, e vínculo endereçado por outra coleção). O objetivo é que o próximo campo normativo não caia no mesmo buraco em silêncio
- [X] T033 [P] [US2] Testar em `backend/tests/integration/publicacoes/test_elevacao_de_versao.py` que um Edital v5 retificado produz Versão Consolidada v6 com `forma = "PONTUADA"`, que a Publicação original não é tocada e que a elevação não aparece como ato de ninguém
- [X] T034 [P] [US2] Testar em `backend/tests/integration/publicacoes/test_elevacao_de_versao.py` que retificar `PONTUADA → DECISORIA` exige os dois rótulos e recusa manter mínima e máxima
- [X] T035 [P] [US2] Testar em `backend/tests/contract/test_documento_publicado.py` que a consulta pública e o comprovante continuam servindo o conteúdo **literal** do v5, sem elevação, para que o `content_hash` continue provando o que a tela mostra

**Checkpoint**: a norma nova é publicável, corrigível e não quebrou o passado

---

## Phase 5: US3 — Concluir uma avaliação sem nota (Priority: P1)

**Goal**: o avaliador registra deferido ou indeferido, com parecer, e conclui — sem inventar número.

**Independent Test**: [Jornada 2](./quickstart.md) — concluir "Indeferido" numa Etapa decisória, e ser recusado ao enviar pontuação.

- [X] T036 [P] [US3] Condicionar `backend/processo_seletivo/avaliacoes/domain/pontuacao.py` à forma: a recusa "Informe a pontuação." passa a valer só na pontuada, entra "Informe o sentido da decisão.", e `exige_parecer` passa a exigir parecer no `DESFAVORAVEL` **sem** depender do caráter eliminatório (012, FR-123)
- [X] T037 [US3] Ramificar gravar e concluir por forma em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`, lendo a forma **do conteúdo da versão já lida na transação** (FR-096) e gravando-a na conclusão (FR-117); recusar no domínio o envio que traz o campo da outra forma (FR-122)
- [X] T038 [US3] Ler `sentido` em `forms.ler_avaliacao` e devolvê-lo em `_valores_da_avaliacao`, em `backend/processo_seletivo/interface/forms.py` e `backend/processo_seletivo/interface/views.py`, preservando o digitado após uma recusa como já se faz com a pontuação
- [X] T039 [US3] Apresentar o instrumento da forma publicada em `backend/processo_seletivo/interface/templates/interface/mesa_inscricao.html`: par de opções **rotulado pelo Edital** sobre valores `FAVORAVEL`/`DESFAVORAVEL`, e nenhum campo de nota
- [X] T040 [US3] Tornar o par de opções da Mesa operável por teclado em `backend/processo_seletivo/interface/templates/interface/mesa_inscricao.html`: grupo rotulado pela pergunta, navegação por setas, foco visível, e o rótulo publicado como **texto** do controle — nunca só cor ou posição distinguindo favorável de desfavorável
- [X] T041 [P] [US3] Testar por `INSERT` cru, em `backend/tests/integration/avaliacoes/test_constraints.py`, que `DECISORIA` com pontuação é recusada **nas duas tabelas** — `Avaliacao` por `ck_avaliacao_concluida_completa` e `ConclusaoAvaliacao` por `ck_conclusao_completa_por_forma`
- [X] T042 [P] [US3] Testar por `INSERT` cru, em `backend/tests/integration/avaliacoes/test_constraints.py`, que `PONTUADA` com sentido é recusada nas mesmas duas tabelas, e que conclusão sem forma nenhuma é recusada
- [X] T043 [P] [US3] Testar em `backend/tests/integration/avaliacoes/test_avaliacao.py` a ida e volta da forma decisória: rascunho sem sentido, conclusão com sentido, e conclusão desfavorável sem parecer recusada
- [X] T044 [P] [US3] Testar em `backend/tests/integration/interface/test_fluxo.py`, pelo canal HTTP real, que o POST com o campo da outra forma é recusado com mensagem — e não ignorado em silêncio (E2E-015)
- [X] T045 [P] [US3] Testar em `backend/tests/integration/avaliacoes/test_versao_da_avaliacao.py` que a forma gravada é a da versão validada, e que Retificação que muda a forma no intervalo recusa a conclusão
- [X] T046 [P] [US3] Testar em `backend/tests/integration/avaliacoes/test_trilha_da_avaliacao.py` que a trilha **não** guarda o sentido, como já não guarda pontuação nem parecer (012, FR-054)

**Checkpoint**: o avaliador conclui sem nota, e o banco garante que as duas formas não se misturam

---

## Phase 6: US4 — O Edital publicado diz como a Etapa é concluída (Priority: P2)

**Goal**: quem lê o Edital descobre, no documento, que aquela Etapa produz deferimento e não nota.

**Independent Test**: [Jornada 1](./quickstart.md) — o PDF da Etapa decisória mostra os rótulos e nenhuma linha de nota.

- [X] T047 [US4] Montar os pares da Etapa por forma em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, pela mesma mecânica condicional que "Pontuação máxima" já usa
- [X] T048 [P] [US4] Testar em `backend/tests/unit/publicacoes/test_pdf.py` que a Etapa decisória imprime os rótulos publicados e **não** imprime nota mínima nem máxima

**Checkpoint**: a fonte estruturada e o documento dizem a mesma coisa

---

## Phase 7: US5 — Oficializar o Resultado da Etapa decisória (Priority: P1)

**Goal**: o indeferimento vira consequência oficial da Etapa, sem virar zero.

**Independent Test**: [Jornada 3](./quickstart.md) — consolidar uma Etapa decisória eliminatória e ver `ELIMINADA` com o motivo citando "Indeferido".

- [X] T049 [P] [US5] Estender `consequencia` em `backend/processo_seletivo/resultados/domain/regra.py` para receber a conclusão em vez de um decimal, com o ramo decisório — `DESFAVORAVEL → ELIMINADA`, `FAVORAVEL → HABILITADA` — e o **rótulo publicado** no motivo exibível, nunca o enum
- [X] T050 [P] [US5] Acrescentar `forma` a `CAMPOS_COMPARADOS` em `backend/processo_seletivo/resultados/domain/compatibilidade.py`, reusando o leitor de `previsao.py`, e registrar no docstring por que os **rótulos ficam de fora** (TR-008)
- [X] T051 [US5] Copiar a conclusão conforme a forma em `backend/processo_seletivo/resultados/application/consolidacao.py` e carregar `forma` e `sentido` em `backend/processo_seletivo/resultados/application/prontidao.py`
- [X] T052 [US5] Exibir a conclusão por forma em `backend/processo_seletivo/interface/templates/interface/resultados.html`, com o rótulo publicado
- [X] T053 [P] [US5] Testar por `INSERT` cru, em `backend/tests/integration/resultados/test_constraints.py`, que `ck_resultado_completo_por_forma` recusa Resultado decisório com pontuação, pontuado com sentido, e sem forma
- [X] T054 [P] [US5] Testar por `INSERT` cru, no mesmo `backend/tests/integration/resultados/test_constraints.py`, que a **trigger** `resultado_etapa_coerente` recusa Resultado cuja forma, pontuação ou sentido divirja da Avaliação fonte — **incluindo o caso que motivou a decisão**: Resultado decisório com sentido diferente do da fonte, que uma conferência alternante aprovaria em silêncio
- [X] T055 [P] [US5] Testar em `backend/tests/unit/resultados/test_regra.py` a tabela-verdade decisória inteira, com o rótulo no motivo
- [X] T056 [P] [US5] Testar em `backend/tests/unit/resultados/test_compatibilidade.py` que a troca de forma cria incompatibilidade e que a troca de rótulo **não** cria
- [X] T057 [P] [US5] Testar em `backend/tests/acceptance/test_resultado_da_etapa.py` a **consolidação em lote** de uma Etapa decisória: o desfecho conta criadas e recusadas, e o Resultado exibe o rótulo publicado. A progressão fica para a E2E de T062, e não é repetida aqui

**Checkpoint**: a fronteira está fechada — o trabalho decisório vira consequência oficial

---

## Phase 8: US6 — Não oficializar o que o Edital não publicou (Priority: P1)

**Goal**: diante de uma Etapa decisória sem caráter eliminatório, o sistema recusa e explica, em vez de inventar o efeito.

> A outra metade de FR-048 — a recusa por nota mínima ausente passando a valer só na forma pontuada —
> **não está aqui**. Ela é pré-requisito de US5, porque sem ela a Etapa decisória eliminatória e sem
> mínima dos Editais 35 e 57 é recusada antes de chegar à consolidação, e por isso mora na
> Foundational.

**Independent Test**: [Jornada 4](./quickstart.md) — a Etapa não é consolidável, e a prontidão diz por quê.

- [X] T058 [US6] Acrescentar a `impedimento_da_regra`, em `backend/processo_seletivo/resultados/domain/regra.py`, o **caso simétrico**: decisória e não eliminatória não publicou o efeito da decisão desfavorável, e por isso a Etapa não é consolidável (013, FR-047). A metade que condiciona a recusa existente à forma já foi feita na Foundational, e não é refeita aqui
- [X] T059 [P] [US6] Testar em `backend/tests/unit/resultados/test_regra.py` a tabela de impedimentos inteira, com os três casos lado a lado: mais de uma avaliação prevista, pontuada eliminatória sem mínima, e decisória não eliminatória
- [X] T060 [P] [US6] Testar em `backend/tests/integration/resultados/test_prontidao.py` que Etapa decisória **não** eliminatória produz zero Resultados e que a prontidão exibe a frase que diz por quê

**Checkpoint**: as duas recusas por regra insuficiente são simétricas e visíveis antes de qualquer tentativa

---

## Phase 9: US7 — Provar que nada da forma pontuada mudou (Priority: P1)

**Goal**: a demonstração, e não a intenção.

**Independent Test**: a suíte inteira passa, e a lista de node IDs do baseline é um **subconjunto** da lista final — todo teste que existia continua existindo. A contagem total cresce, de propósito.

- [X] T061 [US7] Rodar a suíte inteira com PostgreSQL e comparar a lista de node IDs com o baseline: **todo teste que existia continua existindo e passando**. Enumerar em `specs/012-013-revisao-formas-de-conclusao/traceability.md` cada asserção alterada, com o motivo — só as do literal da versão canônica são admissíveis (012, FR-124 · 013, FR-050)
- [X] T062 [P] [US7] Acrescentar a jornada decisória de ponta a ponta a `backend/tests/acceptance/test_mesa_de_avaliacao.py`: publicar decisória, distribuir, concluir indeferido, consolidar, e a inscrição sumir da Etapa seguinte
- [X] T063 [P] [US7] Cobrir em `backend/tests/acceptance/test_quickstart.py` as jornadas do [quickstart](./quickstart.md) que **não** são a E2E de T062 — J1, J4, J5 e J6 —, sem reencenar publicar→avaliar→consolidar→progredir

**Checkpoint**: a revisão está entregue e demonstrada

---

## Phase 10: Polish & Cross-Cutting Concerns

- [X] T064 [P] Fechar a rastreabilidade em `specs/012-013-revisao-formas-de-conclusao/traceability.md`, ligando FR e SC das duas specs às tarefas e aos testes, como 012 e 013 fizeram
- [X] T065 [P] Acrescentar uma Etapa decisória aos dados de demonstração em `backend/processo_seletivo/processos/management/commands/seed_demo.py`, para que a forma nova exista em ambiente de demonstração e não só em teste
- [X] T066 [P] Atualizar `doc/briefing-revisao-012-013-formas-de-conclusao.md` marcando as fases executadas, como o próprio documento já faz com os passos 1 a 3

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup — **bloqueia todas as histórias**, e só termina na
  última tarefa dela, o teste de upgrade
- **US1**: depende da Foundational
- **US2**: depende de US1 — só se retifica o que se sabe publicar
- **US3**: depende da Foundational; **não** depende de US2
- **US4** (P2): depende de US1. Única P2, e a única cuja ausência não impede as outras de existirem
- **US5**: depende de US3 **e da tarefa da Foundational que condiciona `impedimento_da_regra` à
  forma** — sem ela, a Etapa decisória eliminatória e sem nota mínima dos Editais 35 e 57 é recusada
  antes de chegar à consolidação, e os testes de US5 não passam
- **US6**: depende de US5
- **US7**: depende de todas
- **Polish**: depende de US7

### O gate de merge, que não é o gate de commit

A entrega é incremental **dentro da branch** e indivisível na saída dela:

```text
commit  →  qualquer checkpoint
merge   →  US1 a US7 completas
```

Não há flag de funcionalidade no plano, e por isso não há como esconder meia revisão em produção.
Levar para `main` sem US2 deixaria a forma publicada corrigível só pela API, o que D-008.10 recusa
como resultado aceitável; sem US4, o PDF diverge da fonte estruturada e P-007 vale só na metade que
ninguém lê; sem US6, o sistema infere consequência que o Edital não publicou; sem US7, não há
demonstração de que a forma pontuada continua intacta. E sem US5 o avaliador conclui um indeferimento
que não produz efeito — a fronteira quebrada que esta revisão existe para eliminar.

O MVP citado adiante é **marco de validação interna**, e não permissão de merge.

### Parallel Opportunities

- Nenhuma no Setup: o leitor depende dos enums, e o teste do leitor depende do leitor
- Na Foundational: o contrato e os limites de borda correm ao lado do modelo de elaboração; a
  transcrição para o snapshot e o serializer correm juntos depois que o modelo existir. A cadeia de
  elevação e a equivalência de grafias são o mesmo arquivo e **não** correm em paralelo entre si
- Todos os testes marcados `[P]` dentro de cada história
- US2 e US3 correm em paralelo depois da Foundational, por pessoas diferentes: uma toca
  `interface/retificacao.py` e `publicacoes/`, a outra `avaliacoes/` e a Mesa

---

## Parallel Example: US3

```bash
# Os testes da história, depois que a camada de domínio, a aplicação e a tela estiverem de pé:
Task: "INSERT cru — DECISORIA com pontuação recusada nas duas tabelas"
Task: "INSERT cru — PONTUADA com sentido recusada nas duas tabelas"
Task: "ida e volta da forma decisória, e desfavorável sem parecer recusado"
Task: "POST com o campo da outra forma recusado no canal HTTP real"
Task: "a forma gravada é a da versão validada"
Task: "a trilha não guarda o sentido"
```

---

## Implementation Strategy

### Marco de validação interna

`Foundational + US1 + US3 + US5`. É a menor combinação em que o sistema faz algo coerente de ponta a
ponta: publica uma Etapa que não pontua, avalia sem nota e transforma o indeferimento em consequência
oficial. **Não é permissão de merge** — ver o gate acima.

### Ordem de execução

1. Setup + Foundational → a norma existe, o esquema mudou de significado, o salto está provado com
   dados, e a regra da 013 já não exige nota mínima de Etapa decisória
2. US1 → publica-se uma Etapa que não pontua
3. US3 → avalia-se sem nota
4. US5 → o indeferimento vira Resultado oficial **(marco de validação interna)**
5. US6 → a recusa do que o Edital não publicou
6. US2 → a norma nova é corrigível pelo canal institucional
7. US4 → o documento diz o que a fonte estruturada diz
8. US7 + Polish → a demonstração, e o merge

### Ordem de risco

Se algo desta revisão vai falhar, falha nas migrations e no teste de upgrade — backfills sobre
tabelas com dados históricos, protegidas contra `UPDATE` por trigger, e uma dependência cruzada entre
apps que o grafo do Django não infere da ordem das tarefas. É por isso que a prova do salto é
**Foundational**, e não polimento: descobrir um backfill quebrado na última fase invalidaria seis.

---

## Notes

- `[P]` = arquivos diferentes e sem dependência entre as tarefas marcadas juntas
- Commit por tarefa ou por grupo lógico
- **Nenhuma tarefa desta lista cria rota, permissão, ato administrativo, app ou dependência externa.**
  Um módulo novo existe — `avaliacoes/domain/formas.py`, para os dois enums —, e ele é a única
  estrutura nova da revisão
- **Nenhuma tarefa toca `progressao.py`.** Ele consome `HABILITADA` e `ELIMINADA` e não sabe da
  forma — é o limite que mantém esta revisão estreita
