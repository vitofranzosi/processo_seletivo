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

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US7, conforme o mapa de execução da spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`, contrato
em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`. **Nenhum app novo, nenhuma rota
nova, nenhuma permissão nova.**

> **⚠️ A suíte precisa de PostgreSQL, e aqui a lista é longa.** Sem `TEST_DB_ENGINE=postgresql` ela
> cai para SQLite **sem avisar**, e deixam de ser verificados: as duas `CheckConstraint` que alternam
> por forma, a trigger de coerência do Resultado, as duas triggers append-only e o teste de upgrade
> inteiro. Rode com `DB_NAME` próprio deste worktree, como manda o [quickstart](./quickstart.md).

> **⚠️ Antes da primeira linha, registre o baseline verde.** FR-124 e FR-050 cobram que **nenhuma
> asserção existente mude**, e "a suíte passa" só é demonstração se houver com o que comparar. Rode a
> suíte inteira e anote o total antes de T001.

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

- [ ] T001 [P] Criar `Forma` (`PONTUADA`, `DECISORIA`) e `Sentido` (`FAVORAVEL`, `DESFAVORAVEL`) em `backend/processo_seletivo/avaliacoes/domain/formas.py`, com a razão de o rótulo publicado **não** morar aqui (D-008.2)
- [ ] T002 Acrescentar `forma_publicada(etapa)` e `rotulos(etapa)` a `backend/processo_seletivo/avaliacoes/domain/previsao.py`, mantendo o contrato do arquivo — a ausência interpretada num lugar só, e `PONTUADA` como o que ela significa (012, FR-120)
- [ ] T003 [P] Testar os dois leitores em `backend/tests/unit/avaliacoes/test_previsao.py`: ausência, `null`, valor literal e valor inválido

**Checkpoint**: o vocabulário existe e é lido de um lugar só

---

## Phase 2: Foundational (o segundo incremento e todo o esquema)

**Purpose**: a norma publicada e as três migrations. **Bloqueia todas as histórias.**

**⚠️ CRITICAL**: nenhuma história começa antes de T017

### O contrato e a validação

- [ ] T004 [P] Declarar `forma` (`required`, `type: string`, `enum: [PONTUADA, DECISORIA]`, **sem `'null'`**) e os dois rótulos (`required`, `type: [string, 'null']`) em `EtapaPublicada`, e os três em `EtapaInput`, em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, atualizando a `description` para a versão canônica 6 (TR-013)
- [ ] T005 Acrescentar os três `Campo` a `ETAPA_PUBLICADA` em `backend/processo_seletivo/editais/domain/validation.py`, com `forma` **não anulável** e os rótulos anuláveis (TR-003)
- [ ] T006 Estender `_coerencia_das_etapas` em `backend/processo_seletivo/editais/domain/validation.py` com a condicionalidade por forma: rótulos exigidos em `DECISORIA` e proibidos em `PONTUADA`; `minimumScore` e `maximumScore` proibidos em `DECISORIA`; rótulo em branco ou só espaços recusado como ausente
- [ ] T007 [P] Cobrir os limites de borda dos três campos em `backend/tests/contract/test_limites_de_borda.py`

### A versão canônica e a elaboração

- [ ] T008 Subir `SCHEMA_VERSION` para 6 em `backend/processo_seletivo/shared/canonical.py`, registrando o segundo incremento no mesmo formato em que o arquivo registra os quatro anteriores — e dizendo que ele nasce de mudança de requisito, não de omissão do primeiro
- [ ] T009 Acrescentar `forma`, `rotulo_favoravel` e `rotulo_desfavoravel` à Etapa de elaboração em `backend/processo_seletivo/editais/models.py`, anuláveis, **com migration** em `backend/processo_seletivo/editais/migrations/`
- [ ] T010 [P] Aceitar os três campos no `StageSerializer` de `backend/processo_seletivo/editais/api/serializers.py` e no rascunho de `backend/processo_seletivo/editais/application/draft.py`
- [ ] T011 [P] Transcrever os três para o snapshot em `backend/processo_seletivo/publicacoes/application/publish_edital.py`

### A elevação

- [ ] T012 Converter `backend/processo_seletivo/publicacoes/domain/elevacao.py` em **cadeia de degraus** — 4 → 5 → 6 —, com o degrau novo escrevendo `forma = "PONTUADA"` e os rótulos nulos, preservando idempotência, alcance restrito ao fluxo de Retificação e a elevação path-aware do `newValue` de cada ato (TR-001, TR-002)
- [ ] T013 Estender `diz_o_mesmo_que_a_ausencia` em `backend/processo_seletivo/publicacoes/domain/elevacao.py` para aceitar `forma` ausente **ou** `"PONTUADA"` com rótulos nulos como a mesma coisa, e conferir o efeito em `backend/processo_seletivo/publicacoes/domain/conflicts.py`
- [ ] T014 [P] Exercitar a cadeia em `backend/tests/unit/avaliacoes/test_elevacao.py` e a equivalência de grafias em `backend/tests/unit/avaliacoes/test_precondicao_de_grafia.py`: v4 sobe dois degraus, v5 sobe um, v6 atravessa inalterado, e nenhuma grafia equivalente vira conflito

### O esquema da conclusão e do Resultado

- [ ] T015 Acrescentar `forma` e `sentido` a `Avaliacao` e a `ConclusaoAvaliacao` em `backend/processo_seletivo/avaliacoes/models.py`, trocar `ck_avaliacao_concluida_completa` pela que alterna por forma e relaxar `ConclusaoAvaliacao.pontuacao`, **com migration** em `backend/processo_seletivo/avaliacoes/migrations/` que faça os dois backfills — `Avaliacao` só onde `estado = 'CONCLUIDA'` — e derrube e recrie `conclusao_avaliacao_append_only` na mesma transação (TR-004, TR-004a, TR-005)
- [ ] T016 Acrescentar `forma` e `sentido` a `ResultadoEtapa` em `backend/processo_seletivo/resultados/models.py`, relaxar `pontuacao` e reescrever `check_stage_result_source()` para comparar **forma, pontuação e sentido incondicionalmente**, **com migration** em `backend/processo_seletivo/resultados/migrations/` que faça o backfill e recrie as duas triggers (TR-006)

### A prova do salto — junto das migrations, e não no fim

- [ ] T017 Incluir `avaliacoes` e `resultados` em `APPS`, e `conclusao_avaliacao_append_only`, `resultado_etapa_append_only` e `resultado_etapa_coerente` em `TRIGGERS`, em `backend/tests/migrations/test_migrations.py` — hoje nenhuma migration desses dois apps é exercida por teste de upgrade
- [ ] T018 Escrever, em `backend/tests/migrations/test_migrations.py`, o teste `postgresql_only` que aplica as migrations até o estado anterior, cria Avaliação concluída, rascunho, conclusão preservada e Resultado pontuados, aplica as três migrations novas e confere os três backfills, o rascunho **sem** forma e as três triggers recriadas (TR-014)

**Checkpoint**: a norma está publicada, o esquema mudou de significado e o salto está provado com dados

---

## Phase 3: US1 — Publicar uma Etapa decisória (Priority: P1) 🎯 MVP

**Goal**: quem elabora consegue declarar que a Etapa não pontua, e publicar os rótulos que o Edital escolheu.

**Independent Test**: [Jornada 1](./quickstart.md) — publicar uma Etapa decisória e ver `forma` e os dois rótulos no snapshot, com `schemaVersion` 6.

- [ ] T019 [P] [US1] Ler e escrever os três campos no formulário de Etapa em `backend/processo_seletivo/interface/forms.py`
- [ ] T020 [US1] Alternar o formulário por forma em `backend/processo_seletivo/interface/templates/interface/_etapa.html`: nota mínima e máxima na pontuada, par de rótulos na decisória, com "Deferido"/"Indeferido" como **prefill editável e não default normativo**
- [ ] T021 [P] [US1] Exibir a Etapa por forma no resumo de `backend/processo_seletivo/interface/revisao.py`
- [ ] T022 [P] [US1] Testar a publicação de uma Etapa decisória em `backend/tests/integration/interface/`: o snapshot traz forma e rótulos, e `schemaVersion` é 6
- [ ] T023 [P] [US1] Testar as recusas em `backend/tests/integration/editais/`: decisória sem rótulo, decisória com pontuação máxima, rótulo em branco, e `forma` fora do enum — cada uma com o código declarado no [contrato](./contracts/forma-da-conclusao.md)

**Checkpoint**: existe Edital publicado cuja Etapa declara que não pontua

---

## Phase 4: US2 — Retificar, inclusive o que foi publicado antes do salto (Priority: P1)

**Goal**: nenhum Edital fica irretificável por evolução de esquema, e a forma é corrigível pelo canal institucional.

**Independent Test**: [Jornadas 5 e 6](./quickstart.md) — retificar um Edital v5 e retificar a forma de uma Etapa.

- [ ] T024 [US2] Completar `CAMPOS_ETAPA` em `backend/processo_seletivo/interface/retificacao.py` com **todos** os campos normativos da Etapa: os cinco atuais, `maximumScore` e `evaluationsPerRegistration` que o primeiro incremento deixou para trás, e os três novos (012, D-008.10)
- [ ] T025 [P] [US2] Escrever, em `backend/tests/contract/`, a guarda que compara a lista da tela com o contrato da Etapa publicada, para que o próximo campo normativo não caia no mesmo buraco em silêncio
- [ ] T026 [P] [US2] Testar em `backend/tests/integration/publicacoes/test_elevacao_de_versao.py` que um Edital v5 retificado produz Versão Consolidada v6 com `forma = "PONTUADA"`, que a Publicação original não é tocada e que a elevação não aparece como ato de ninguém
- [ ] T027 [P] [US2] Testar em `backend/tests/integration/publicacoes/` que retificar `PONTUADA → DECISORIA` exige os dois rótulos e recusa manter mínima e máxima
- [ ] T028 [P] [US2] Testar em `backend/tests/contract/test_documento_publicado.py` que a consulta pública e o comprovante continuam servindo o conteúdo **literal** do v5, sem elevação, para que o `content_hash` continue provando o que a tela mostra

**Checkpoint**: a norma nova é publicável, corrigível e não quebrou o passado

---

## Phase 5: US3 — Concluir uma avaliação sem nota (Priority: P1)

**Goal**: o avaliador registra deferido ou indeferido, com parecer, e conclui — sem inventar número.

**Independent Test**: [Jornada 2](./quickstart.md) — concluir "Indeferido" numa Etapa decisória, e ser recusado ao enviar pontuação.

- [ ] T029 [P] [US3] Condicionar `backend/processo_seletivo/avaliacoes/domain/pontuacao.py` à forma: a recusa "Informe a pontuação." passa a valer só na pontuada, entra "Informe o sentido da decisão.", e `exige_parecer` passa a exigir parecer no `DESFAVORAVEL` **sem** depender do caráter eliminatório (012, FR-123)
- [ ] T030 [US3] Ramificar gravar e concluir por forma na camada de aplicação de `backend/processo_seletivo/avaliacoes/`, lendo a forma **do conteúdo da versão já lida na transação** (FR-096) e gravando-a na conclusão (FR-117); recusar no domínio o envio que traz o campo da outra forma (FR-122)
- [ ] T031 [US3] Ler `sentido` em `forms.ler_avaliacao` e devolvê-lo em `_valores_da_avaliacao`, em `backend/processo_seletivo/interface/forms.py` e `backend/processo_seletivo/interface/views.py`, preservando o digitado após uma recusa como já se faz com a pontuação
- [ ] T032 [US3] Apresentar o instrumento da forma publicada em `backend/processo_seletivo/interface/templates/interface/mesa_inscricao.html`: par de opções **rotulado pelo Edital** sobre valores `FAVORAVEL`/`DESFAVORAVEL`, e nenhum campo de nota
- [ ] T033 [P] [US3] Testar por `INSERT` cru, em `backend/tests/integration/avaliacoes/test_constraints.py`, que conclusão `DECISORIA` com pontuação é recusada pelo banco
- [ ] T034 [P] [US3] Testar por `INSERT` cru, em `backend/tests/integration/avaliacoes/test_constraints.py`, que conclusão `PONTUADA` com sentido é recusada pelo banco
- [ ] T035 [P] [US3] Testar em `backend/tests/integration/avaliacoes/test_avaliacao.py` a ida e volta da forma decisória: rascunho sem sentido, conclusão com sentido, e conclusão desfavorável sem parecer recusada
- [ ] T036 [P] [US3] Testar em `backend/tests/integration/interface/`, pelo canal HTTP real, que o POST com o campo da outra forma é recusado com mensagem — e não ignorado em silêncio (E2E-015)
- [ ] T037 [P] [US3] Testar em `backend/tests/integration/avaliacoes/test_versao_da_avaliacao.py` que a forma gravada é a da versão validada, e que Retificação que muda a forma no intervalo recusa a conclusão
- [ ] T038 [P] [US3] Testar em `backend/tests/integration/avaliacoes/test_trilha_da_avaliacao.py` que a trilha **não** guarda o sentido, como já não guarda pontuação nem parecer (012, FR-054)

**Checkpoint**: o avaliador conclui sem nota, e o banco garante que as duas formas não se misturam

---

## Phase 6: US4 — O Edital publicado diz como a Etapa é concluída (Priority: P2)

**Goal**: quem lê o Edital descobre, no documento, que aquela Etapa produz deferimento e não nota.

**Independent Test**: [Jornada 1](./quickstart.md) — o PDF da Etapa decisória mostra os rótulos e nenhuma linha de nota.

- [ ] T039 [US4] Montar os pares da Etapa por forma em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, pela mesma mecânica condicional que "Pontuação máxima" já usa
- [ ] T040 [P] [US4] Testar em `backend/tests/unit/publicacoes/test_pdf.py` que a Etapa decisória imprime os rótulos publicados e **não** imprime nota mínima nem máxima

**Checkpoint**: a fonte estruturada e o documento dizem a mesma coisa

---

## Phase 7: US5 — Oficializar o Resultado da Etapa decisória (Priority: P1)

**Goal**: o indeferimento vira consequência oficial da Etapa, sem virar zero.

**Independent Test**: [Jornada 3](./quickstart.md) — consolidar uma Etapa decisória eliminatória e ver `ELIMINADA` com o motivo citando "Indeferido".

- [ ] T041 [P] [US5] Estender `consequencia` em `backend/processo_seletivo/resultados/domain/regra.py` para receber a conclusão em vez de um decimal, com o ramo decisório — `DESFAVORAVEL → ELIMINADA`, `FAVORAVEL → HABILITADA` — e o **rótulo publicado** no motivo exibível, nunca o enum
- [ ] T042 [P] [US5] Acrescentar `forma` a `CAMPOS_COMPARADOS` em `backend/processo_seletivo/resultados/domain/compatibilidade.py`, reusando o leitor de `previsao.py`, e registrar no docstring por que os **rótulos ficam de fora** (TR-008)
- [ ] T043 [US5] Copiar a conclusão conforme a forma em `backend/processo_seletivo/resultados/application/consolidacao.py` e carregar `forma` e `sentido` em `backend/processo_seletivo/resultados/application/prontidao.py`
- [ ] T044 [US5] Exibir a conclusão por forma em `backend/processo_seletivo/interface/templates/interface/resultados.html`, com o rótulo publicado
- [ ] T045 [P] [US5] Testar por `INSERT` cru, em `backend/tests/integration/resultados/`, que a trigger recusa Resultado cuja forma, pontuação ou sentido divirja da Avaliação fonte — **incluindo o caso que motivou a decisão**: Resultado decisório com sentido diferente do da fonte, que uma conferência alternante aprovaria
- [ ] T046 [P] [US5] Testar em `backend/tests/unit/resultados/test_regra.py` a tabela-verdade decisória inteira, com o rótulo no motivo
- [ ] T047 [P] [US5] Testar em `backend/tests/unit/resultados/test_compatibilidade.py` que a troca de forma cria incompatibilidade e que a troca de rótulo **não** cria
- [ ] T048 [P] [US5] Testar em `backend/tests/acceptance/test_resultado_da_etapa.py` a consolidação em lote de uma Etapa decisória, e que a inscrição indeferida some de todas as Etapas seguintes

**Checkpoint**: a fronteira está fechada — o trabalho decisório vira consequência oficial

---

## Phase 8: US6 — Não oficializar o que o Edital não publicou (Priority: P1)

**Goal**: diante de uma Etapa decisória sem caráter eliminatório, o sistema recusa e explica, em vez de inventar o efeito.

**Independent Test**: [Jornada 4](./quickstart.md) — a Etapa não é consolidável, e a prontidão diz por quê.

- [ ] T049 [US6] Condicionar `impedimento_da_regra` em `backend/processo_seletivo/resultados/domain/regra.py`: a recusa por "eliminatória sem nota mínima" passa a valer **só na forma pontuada**, e entra o caso simétrico — decisória e não eliminatória não publicou o efeito da decisão desfavorável (013, FR-047, FR-048)
- [ ] T050 [P] [US6] Testar em `backend/tests/unit/resultados/test_regra.py` que Etapa decisória **eliminatória e sem nota mínima** consolida normalmente — a configuração real dos Editais 35 e 57, hoje recusada
- [ ] T051 [P] [US6] Testar em `backend/tests/integration/resultados/` que Etapa decisória **não** eliminatória produz zero Resultados e que a prontidão exibe a frase que diz por quê

**Checkpoint**: as duas recusas por regra insuficiente são simétricas e visíveis antes de qualquer tentativa

---

## Phase 9: US7 — Provar que nada da forma pontuada mudou (Priority: P1)

**Goal**: a demonstração, e não a intenção.

**Independent Test**: a suíte inteira passa, e a contagem bate com o baseline anotado antes de T001.

- [ ] T052 [US7] Rodar a suíte inteira com PostgreSQL e confirmar **zero alteração de asserção** em teste existente, listando em `specs/012-013-revisao-formas-de-conclusao/` qualquer asserção que tenha precisado mudar e por quê (012, FR-124 · 013, FR-050)
- [ ] T053 [P] [US7] Acrescentar a jornada decisória de ponta a ponta a `backend/tests/acceptance/test_mesa_de_avaliacao.py`: publicar decisória, distribuir, concluir indeferido, consolidar, e a inscrição sumir da Etapa seguinte
- [ ] T054 [P] [US7] Cobrir as seis jornadas do [quickstart](./quickstart.md) em `backend/tests/acceptance/test_quickstart.py`

**Checkpoint**: a revisão está entregue e demonstrada

---

## Phase 10: Polish & Cross-Cutting Concerns

- [ ] T055 [P] Fechar a rastreabilidade em `specs/012-013-revisao-formas-de-conclusao/traceability.md`, ligando FR e SC das duas specs às tarefas e aos testes, como 012 e 013 fizeram
- [ ] T056 [P] Acrescentar uma Etapa decisória aos dados de demonstração em `backend/processo_seletivo/processos/management/commands/seed_demo.py`, para que a forma nova exista em ambiente de demonstração e não só em teste
- [ ] T057 [P] Atualizar `doc/briefing-revisao-012-013-formas-de-conclusao.md` marcando as fases executadas, como o próprio documento já faz com os passos 1 a 3

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup — **bloqueia todas as histórias**
- **US1 (Phase 3)**: depende da Foundational
- **US2 (Phase 4)**: depende de US1 — só se retifica o que se sabe publicar
- **US3 (Phase 5)**: depende da Foundational; **não** depende de US2
- **US4 (Phase 6)**: depende de US1. É a única P2, e a única que pode ser adiada
- **US5 (Phase 7)**: depende de US3 — não há Resultado decisório sem conclusão decisória
- **US6 (Phase 8)**: depende de US5
- **US7 (Phase 9)**: depende de todas
- **Polish (Phase 10)**: depende de US7

### A dependência que esta revisão não pode quebrar

As histórias **não** são independentes, e fingir que são seria repetir o erro que a revisão existe
para corrigir. `US3` sem `US5` é exatamente a fronteira quebrada que o briefing descreve: o avaliador
conclui "indeferido" e a Etapa nunca produz resultado.

```text
US3 entregue  ∧  US5 não entregue  →  não vai para main
```

Parar entre as duas é legítimo **dentro da branch**, e só ali.

### Parallel Opportunities

- T001 e T003 no Setup
- T004, T007, T010, T011 e T014 na Foundational, depois que T005 e T009 existirem
- Todos os testes marcados [P] dentro de cada história
- US2 e US3 podem correr em paralelo depois da Foundational, por pessoas diferentes: uma toca
  `interface/retificacao.py` e `publicacoes/`, a outra `avaliacoes/` e a Mesa

---

## Parallel Example: US3

```bash
# Os seis testes da história, depois que T029 a T032 estiverem de pé:
Task: "INSERT cru — DECISORIA com pontuação é recusada"
Task: "INSERT cru — PONTUADA com sentido é recusada"
Task: "ida e volta da forma decisória, e desfavorável sem parecer recusado"
Task: "POST com o campo da outra forma recusado no canal HTTP real"
Task: "a forma gravada é a da versão validada"
Task: "a trilha não guarda o sentido"
```

---

## Implementation Strategy

### MVP

O MVP desta revisão **não é uma história**: é `Foundational + US1 + US3 + US5`. Antes de US5 o
sistema aceita um trabalho que não produz efeito, e essa é a única combinação que não pode chegar a
`main`.

### Entrega incremental

1. Setup + Foundational → a norma existe e o salto está provado com dados
2. US1 → publica-se uma Etapa que não pontua
3. US3 → avalia-se sem nota **(ainda não vai para main sozinha)**
4. US5 → o indeferimento vira Resultado oficial **(aqui pode ir)**
5. US6 → a recusa do que o Edital não publicou
6. US2, US4 → retificação e documento
7. US7 + Polish → a demonstração

### Ordem de risco

Se algo desta revisão vai falhar, falha em T015, T016 e T018 — os backfills e as triggers, sobre
tabelas com dados históricos e protegidas contra `UPDATE`. É por isso que a prova do salto é
**Foundational**, e não polimento: descobrir um backfill quebrado em T052 invalidaria seis fases.

---

## Notes

- `[P]` = arquivos diferentes, sem dependência
- Commit por tarefa ou por grupo lógico
- **Nenhuma tarefa desta lista cria rota, permissão, ato administrativo, app ou dependência.** Se
  alguma precisar, a fatia foi montada errada
- **Nenhuma tarefa toca `progressao.py`.** Ele consome `HABILITADA` e `ELIMINADA` e não sabe da
  forma — é o limite que mantém esta revisão estreita
