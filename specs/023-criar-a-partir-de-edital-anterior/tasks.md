---

description: "Task list for feature implementation"
---

# Tasks: Criar Edital a partir de Edital anterior

**Input**: Design documents from `specs/023-criar-a-partir-de-edital-anterior/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/copia.md](./contracts/copia.md),
[quickstart.md](./quickstart.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige cobertura específica de documentos,
cotas, elegibilidade, classificação e autorização — que é exatamente do que a cópia é feita. E há uma
razão própria desta feature: `T-005` mostra que **a cópia preserva a coerência interna**, de modo que
um identificador não remapeado atravessa a gravação sem recusa. Onde não há guarda de domínio a
herdar, o teste **é** a guarda.

**Organization**: por user story, para que cada faixa seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US3`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`. **Nenhum app
novo, nenhum modelo, nenhuma migration, nenhuma permissão** — é a régua de `§2` da spec, e `T042` a
verifica.

---

## Phase 1: Setup

**Purpose**: os dois arquivos novos, vazios, para que as tarefas seguintes tenham onde escrever.

- [ ] T001 [P] Criar `backend/processo_seletivo/editais/domain/reaproveitamento.py` com as assinaturas das funções puras de [research.md](./research.md) — `mapa_de_identidades`, `remapear`, `converter_instantes`, `payload_do_conteudo` — sem implementação. *Funções puras no domínio porque é o que se testa exaustivamente sem banco; a transação é da aplicação*
- [ ] T002 [P] Criar `backend/processo_seletivo/editais/application/reaproveitamento.py` com a assinatura de `reaproveitar_edital` exatamente como [contracts/copia.md](./contracts/copia.md) a declara, ainda sem corpo

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: as funções puras. Elas carregam todo o risco técnico da feature e não dependem de tela
nem de banco.

**⚠️ CRÍTICO**: nenhuma user story começa antes deste checkpoint.

- [ ] T003 [P] Teste do mapa de identidades em `backend/tests/unit/editais/test_reaproveitamento.py`: toda chave que **é** identidade em `T-005` entra no mapa, e duas execuções sobre o mesmo conteúdo produzem identidades distintas (`FR-009`)
- [ ] T004 Implementar `mapa_de_identidades(conteudo)` em `backend/processo_seletivo/editais/domain/reaproveitamento.py`, percorrendo as dez posições de identidade de `T-005` (`FR-009`)
- [ ] T005 [P] Teste do remapeamento em `backend/tests/unit/editais/test_reaproveitamento.py`: as oito posições que **referenciam** identidade — `scheduleEventId`, `profileId`, `modalityId`, `attachmentId`, `classificationMilestones[].stages[]`, `tiebreakers[].parameters.stageId`, `…factId` e `drawMethod.qualifyingStageId`. **Inclui a asserção negativa**: nenhum identificador da origem sobrevive em posição alguma do payload (`FR-010`)
- [ ] T006 Implementar `remapear(conteudo, mapa)` em `backend/processo_seletivo/editais/domain/reaproveitamento.py` como substituição uniforme, e **falhar alto** diante de identificador em posição de referência que não esteja no mapa — chave nova detectável em vez de silenciosa (`FR-010`, `FR-010a`)
- [ ] T007 [P] Teste da conversão de instantes em `backend/tests/unit/editais/test_reaproveitamento.py`: `schedule[].startAt`, `schedule[].endAt` e `normativeRule.effectiveFrom` chegam como texto ISO e saem como instantes com offset. **Com a contraprova**: sem a conversão, `validate_event` estoura em vez de recusar (`FR-006`, `T-002`)
- [ ] T008 Implementar `converter_instantes(conteudo)` em `backend/processo_seletivo/editais/domain/reaproveitamento.py`, e **só nos três campos** — converter por varredura de formato transformaria em data qualquer texto que se pareça com uma (`FR-006`, `T-002`)
- [ ] T009 [P] Teste de `payload_do_conteudo` em `backend/tests/unit/editais/test_reaproveitamento.py`: seção gerada não passa e **toda** textual passa, inclusive a que ninguém editou — o conteúdo publicado traz o padrão do catálogo quando não há linha (`T-006`); `maxInscricoesPorCandidato`, `classificationInformation` e `callInformation` não passam (`FR-008`); `status` do Evento sai `PLANEJADO` qualquer que fosse (`FR-008a`); `isRegistrationPeriod` é preservado; `number`, `year`, `title`, `description`, `processoCode`, `processoTitle` e `schemaVersion` não passam (`FR-007`)
- [ ] T010 Implementar `payload_do_conteudo(conteudo)` em `backend/processo_seletivo/editais/domain/reaproveitamento.py`, produzindo as cinco coleções que `replace_draft` aceita (`FR-006`, `FR-007`, `FR-008`, `FR-008a`)
- [ ] T011 [P] Teste de `rascunho_vazio` em `backend/tests/integration/editais/test_reaproveitamento.py`: as seis coleções uma a uma — Perfil, Evento, Etapa, Documento Exigido, Seção persistida e Anexo —, cada uma sozinha bastando para o rascunho não estar vazio (`FR-002`)
- [ ] T012 Implementar `rascunho_vazio(edital)` em `backend/processo_seletivo/editais/application/reaproveitamento.py` (`FR-002`, `D-002`)

**Checkpoint**: `T-002`, `T-005`, `T-006`, `FR-007`, `FR-008` e `FR-008a` estão cobertos sem tocar em
banco. Nada disso é observável por quem usa ainda.

---

## Phase 3: User Story 1 — Partir da edição anterior (Priority: P1) 🎯 MVP

**Goal**: quem elabora escolhe um Edital publicado e recebe a configuração dele no assistente.

**Independent Test**: cenários 1, 7 e 9 do [quickstart.md](./quickstart.md) — a jornada, a recusa
sobre rascunho não vazio, e a origem inelegível.

### Tests for User Story 1

- [ ] T013 [P] [US1] Teste do serviço em `backend/tests/integration/editais/test_reaproveitamento.py`: partindo de origem publicada, o destino passa a ter Perfis, modalidades, regras, fatos, marcos, critérios, Eventos, Etapas, Documentos Exigidos, Seções e Anexos, e **nenhuma identidade em comum com a origem** (`FR-006`, `FR-009`, `SC-002`)
- [ ] T014 [P] [US1] Teste de que a origem não se move, em `backend/tests/integration/editais/test_reaproveitamento.py`: situação, revisão e resumo criptográfico da versão vigente idênticos antes e depois (`FR-012`, `SC-004`)
- [ ] T015 [P] [US1] Teste de autorização em `backend/tests/authorization/test_reaproveitamento.py`: sem `edital:elaborar` recusa; destino de outro escopo, origem de outro escopo, origem inexistente, origem em elaboração e origem cancelada respondem **literalmente igual** — `404`. **E os dois casos positivos, porque a fronteira tem dois lados**: origem `PUBLICADO` e origem `ENCERRADO` são aceitas (`FR-003`, `FR-004`, `T-007`)
- [ ] T016 [P] [US1] Teste de interface em `backend/tests/interface/test_reaproveitar.py`: a jornada do cenário 1, e a afordância **ausente** quando o rascunho não está vazio (`FR-001`, `FR-002`)

### Implementation for User Story 1

- [ ] T017 [US1] Implementar a leitura da origem em `backend/processo_seletivo/editais/application/reaproveitamento.py`: `elevar(effective_version(edital_id=origem_id).content)`, o idioma que `retificacoes.py` já usa — nunca as tabelas relacionais (`FR-005`, `D-003`, `T-001`)
- [ ] T018 [US1] Implementar a cópia dos Anexos em `backend/processo_seletivo/editais/application/reaproveitamento.py`: `ArtefatoAnexo` novo com os bytes do artefato congelado da origem, `congelado_em` nulo, e `AnexoEdital` na ordem da origem. **Sem passar pelos comandos de Anexo** — `N` comandos seriam `N` saltos de revisão e `N` registros para uma operação (`FR-011`, `T-003`, `D-007`)
- [ ] T019 [US1] Orquestrar `reaproveitar_edital` em `backend/processo_seletivo/editais/application/reaproveitamento.py` na ordem de [contracts/copia.md](./contracts/copia.md) — autorização e escopo, **reserva da chave e saída da repetição conhecida, e só então as precondições mutáveis** (`FR-017a`) —, numa transação só, chamando `replace_draft` com `area` que **não é nome de etapa** — vazio devolveria o registro indistinguível que a `006`/FR-042 corrigiu, e nome de etapa afirmaria que alguém a compôs (`FR-017`, `FR-019`, `T-004`)
- [ ] T020 [US1] Implementar `origens_elegiveis(actor)` em `backend/processo_seletivo/editais/application/reaproveitamento.py`: Editais do escopo do ator em situação publicada ou encerrada, com número, ano, título e Processo (`FR-004`, `D-008`)
- [ ] T021 [US1] Acrescentar a view `reaproveitar` em `backend/processo_seletivo/interface/views.py` e a rota `editais/<uuid:edital_id>/reaproveitar` em `backend/processo_seletivo/interface/urls.py`, com o `404` uniforme de `T-007`. A view lê os dois campos do formulário direto, sem `ler_*` em `forms.py` — ele existe para reconstruir coleções a partir de campos indexados, e aqui são dois (`FR-001`, `FR-004`)
- [ ] T022 [US1] Criar `backend/processo_seletivo/interface/templates/interface/reaproveitar.html`: a lista de origens elegíveis, localizável por número, ano, título e Processo, com `chave_idempotencia` no formulário como nas telas de criação, e **mensagem própria quando não há origem elegível** — nunca lista vazia sem explicação (`FR-004`, `FR-017`, `T-009`)
- [ ] T023 [US1] Acrescentar o cartão *partir de um Edital anterior* em `backend/processo_seletivo/interface/templates/interface/compor_identificacao.html`, visível **apenas** com rascunho vazio — oferecer o que se vai recusar é pior do que não oferecer (`FR-001`, `FR-002`)

**Checkpoint**: a jornada existe e é navegável. É o MVP: quem elabora já para de redigitar o Edital
inteiro.

---

## Phase 4: User Story 2 — O novo Edital não carrega o certame anterior (Priority: P1)

**Goal**: provar o isolamento — nada de execução veio junto, e nenhuma referência alcança a origem.

**Independent Test**: cenários 3, 4, 5, 6 e 8 do [quickstart.md](./quickstart.md).

**Por que esta story é quase toda de teste**: as regras que ela garante foram implementadas na
Fase 2 e na `US1`. O que falta é a **prova**, e nesta feature a prova não é formalidade — `T-005`
mostra que o defeito que ela caça atravessa a gravação sem recusa.

### Tests for User Story 2

- [ ] T024 [P] [US2] Teste em `backend/tests/integration/editais/test_reaproveitamento.py`: origem **com execução** — inscrições, avaliações, resultado divulgado e recurso julgado — produz destino com zero de cada um (`FR-013`, `SC-006`)
- [ ] T025 [P] [US2] Teste do vínculo com o Anexo em `backend/tests/integration/editais/test_reaproveitamento.py`: o Documento Exigido do destino entrega o artefato **do destino**. **Com a contraprova**: sem o remapeamento, a gravação passa e só a publicação recusa (`FR-010a`, `SC-003`)
- [ ] T026 [P] [US2] Teste do marco em `backend/tests/integration/editais/test_reaproveitamento.py`: as Etapas que o marco enumera são as do destino, e a contraprova de que a gravação passaria sem o remapeamento (`FR-010a`, `SC-003`)
- [ ] T027 [P] [US2] Teste do critério de desempate em `backend/tests/integration/editais/test_reaproveitamento.py`: `parameters.stageId` e `parameters.factId` apontam Etapa e fato do destino, com a mesma contraprova (`FR-010a`, `SC-003`)
- [ ] T028 [P] [US2] Teste do método de sorteio em `backend/tests/integration/editais/test_reaproveitamento.py`: `drawMethod.qualifyingStageId` aponta Etapa do destino. **É o mais traiçoeiro dos quatro** — na gravação ele é conferido apenas contra as Etapas que o próprio marco enumera, que vieram juntas da origem (`FR-010a`, `SC-003`, `T-005`)
- [ ] T029 [P] [US2] Teste do calendário em `backend/tests/integration/editais/test_reaproveitamento.py`: origem com Eventos `CONCLUIDO` e `CANCELADO` produz destino com todos `PLANEJADO`, e o período de inscrições designado continua designado (`FR-008a`)
- [ ] T030 [P] [US2] Teste das exclusões em `backend/tests/integration/editais/test_reaproveitamento.py`: origem com `maxInscricoesPorCandidato`, `classificationInformation` e `callInformation` preenchidos produz destino sem os três, e a prévia do destino não os exibe (`FR-008`)
- [ ] T031 [US2] Teste da origem **retificada** em `backend/tests/integration/editais/test_reaproveitamento.py`: publicada, depois retificada em data e em vagas, o destino nasce com os valores retificados. É o teste que separa ler a versão vigente de ler o estado relacional (`FR-005`, `SC-008`, `D-003`)
- [ ] T031a [US2] Teste da origem em **esquema anterior ao corrente**, em `backend/tests/integration/editais/test_reaproveitamento.py`: versão vigente gravada num degrau antigo do esquema canônico produz destino completo e já no esquema atual, sem inventar o que aquele degrau não declarava. Prova a integração `elevar → copiar`, e não só a leitura (`FR-005`)
- [ ] T032 [US2] Teste de atomicidade e idempotência em `backend/tests/integration/editais/test_reaproveitamento.py`: falha ao criar o último Anexo não deixa Anexo nem conteúdo no destino; a mesma chave enviada duas vezes executa **uma** cópia; e **a repetição sobre o destino já copiado devolve o mesmo Edital, não `draft_not_empty`** — é o que prende a ordem entre a reserva e as precondições mutáveis, e o defeito que ela evita é invisível até a segunda requisição (`FR-017`, `FR-017a`, `T-009`)
- [ ] T033 [US2] Teste de independência em `backend/tests/integration/editais/test_reaproveitamento.py`: alterar o destino não altera a origem, e retificar a origem depois da cópia não altera o destino (`FR-018`, `SC-003` inverso)

**Checkpoint**: o isolamento é fato verificado, e não consequência presumida do desenho.

---

## Phase 5: User Story 3 — Saber de onde este Edital partiu (Priority: P2)

**Goal**: a origem fica dita, na tela e na trilha, e sobrevive à publicação.

**Independent Test**: cenário 11 do [quickstart.md](./quickstart.md).

### Tests for User Story 3

- [ ] T034 [P] [US3] Teste do registro em `backend/tests/integration/editais/test_reaproveitamento.py`, conferindo a forma declarada em [contracts/copia.md](./contracts/copia.md): operação própria, agregado igual ao **destino**, ator, instante, e o motivo carregando o **identificador da versão consolidada** de onde o conteúdo saiu — nunca prosa. **Inclui a prova que a Constituição cobra**: retificada a origem depois da cópia, a trilha continua dizendo de qual versão se partiu (`FR-015`, `FR-015a`)
- [ ] T035 [P] [US3] Teste de interface em `backend/tests/interface/test_reaproveitar.py`: o aviso nomeia a origem em todas as etapas da composição enquanto o Edital está em elaboração, e o registro continua consultável depois da publicação (`FR-014`, `SC-005`)
- [ ] T036 [P] [US3] Teste em `backend/tests/unit/editais/test_reaproveitamento.py` de que a origem **não** entra no conteúdo canônico do destino: o snapshot publicado não menciona o Edital de origem em campo algum (`FR-016`)

### Implementation for User Story 3

- [ ] T037 [US3] Registrar o evento de origem em `backend/processo_seletivo/editais/application/reaproveitamento.py`, com operação própria e o identificador da **versão consolidada** de origem no motivo — um identificador só, do qual o Edital deriva por `edital_id`, porque é ele que preserva *independência e versão*. **Nomear o conceito de `origem`, nunca de `proveniência`** — a palavra já designa `caminho normativo → Publicação` em `VersaoConsolidada.proveniencias` (`FR-015`, `FR-015a`, `T-008`)
- [ ] T038 [US3] Montar o aviso permanente em `backend/processo_seletivo/interface/views.py` e exibi-lo em `backend/processo_seletivo/interface/templates/interface/compor_base.html`, que todas as etapas do assistente estendem — **e não em `base.html`**, onde mexer já custou asserção de template quebrada e que alcançaria telas a que o aviso não pertence. Resolve a **versão** pelo identificador do registro e chega ao Edital por `edital_id`, renderizando número, ano e título da linha (`FR-014`, `FR-015a`)
- [ ] T039 [US3] Tornar a trilha legível em `backend/processo_seletivo/interface/views.py`: entrada em `OPERACOES` para a operação nova, e **enriquecimento do motivo** — resolver a versão e o Edital e exibir *"a partir do Edital 173/2025, versão de 12/03/2026"* em lugar do identificador. Sem isto, `US3` fica atendida no banco e não no canal do ator, que é o que o princípio VI recusa (`FR-014a`, `T-010`)
- [ ] T040 [P] [US3] Teste de leitura humana da trilha em `backend/tests/interface/test_reaproveitar.py`: a entrada nomeia Edital e versão **antes e depois da publicação** do destino, e **continua nomeando os mesmos** depois de uma Retificação posterior na origem — a prova de que guardar identificador não custou legibilidade (`FR-014a`, `SC-005`)

**Checkpoint**: a feature está completa.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T041 [P] Conferir a tela nova contra o padrão de acessibilidade das demais telas de gestão, em `backend/tests/interface/test_acessibilidade.py`
- [ ] T042 Verificar a régua de `§2`: `cd backend && uv run python manage.py makemigrations --check --dry-run` limpo, e na revisão do diff nenhum modelo novo, nenhuma entrada nova em `PAPEIS` e nenhum achado impeditivo novo em `validate_for_publication` (`SC-007`)
- [ ] T043 `cd backend && make lint check test-pg` — os **dois** passos do lint, e a suíte contra PostgreSQL
- [ ] T044 Percorrer os treze cenários do [quickstart.md](./quickstart.md) pelo navegador, com Gestor e Elaborador em identidades **distintas** e uma origem retificada (Princípio VI)

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Setup (T001–T002)
   ↓
Foundational (T003–T012)          ← bloqueia tudo
   ↓
US1 (T013–T023)  🎯 MVP           ← a jornada
   ↓
US2 (T024–T033, inclusive T031a)                   ← a prova do isolamento
   ↓
US3 (T034–T040)                   ← a origem dita
   ↓
Polish (T041–T044)
```

`US2` depende de `US1` por um motivo prático, e não conceitual: seus testes exercitam o serviço
inteiro, que só existe ao fim da `US1`. `US3` é independente das duas e poderia vir antes — a ordem
segue a prioridade da spec.

### Dentro de cada story

Teste antes da implementação que ele prende, sempre. Na Fase 2 os pares são explícitos:
`T003→T004`, `T005→T006`, `T007→T008`, `T009→T010`, `T011→T012`.

### Conflitos de arquivo a respeitar

- `domain/reaproveitamento.py` — `T004`, `T006`, `T008`, `T010` são o **mesmo arquivo**: em série
- `application/reaproveitamento.py` — `T012`, `T017`, `T018`, `T019`, `T020`, `T037`: em série
- `interface/views.py` — `T021`, `T038`, `T039`: em série
- `tests/interface/test_reaproveitar.py` — `T016`, `T035`, `T040`: em série
- `tests/unit/editais/test_reaproveitamento.py` — `T003`, `T005`, `T007`, `T009`, `T036`: em série
- `tests/integration/editais/test_reaproveitamento.py` — `T011`, `T013`, `T014`, `T024`–`T034`: em
  série entre si, ainda que marcados `[P]` em relação às demais frentes
- `interface/views.py` e `urls.py` — `T021` e `T038`: em série

O `[P]` desta lista significa *paralelo com outras frentes*, não *paralelo dentro do arquivo*.

### Parallel Opportunities

- `T001` e `T002`: arquivos distintos
- Na Fase 2, cada teste unitário pode ser escrito enquanto outra dupla é implementada, desde que a
  ordem do arquivo seja respeitada
- Na `US1`, `T015` (autorização) e `T016` (interface) são arquivos próprios e correm com `T013`/`T014`
- Na `US2`, `T025`–`T028` são quatro testes independentes entre si — mas no mesmo arquivo

## Implementation Strategy

### MVP primeiro (`US1`)

Fases 1 a 3. Ao fim, quem elabora escolhe um Edital anterior e recebe a configuração no assistente —
que é a feature inteira do ponto de vista de quem a pediu. O que falta depois é **garantia** e
**proveniência**, não capacidade.

### Entrega incremental

Uma PR por faixa, com a demonstração como condição de merge, na ordem `US1 → US2 → US3`. `US2` não
entrega tela nova e mesmo assim não é opcional: sem ela, a feature funciona e ninguém sabe se está
certa.

### Onde parar e revisar o desenho

Se qualquer tarefa exigir migration, tabela, modelo, permissão nova, estado persistido de revisão ou
recusa de publicação nova, **pare**. É a régua de `§2` da spec sendo cruzada, e o desenho volta para
revisão em vez de a régua ser reescrita.

## Cobertura de requisitos

| Requisito | Tarefas |
|---|---|
| FR-001 | T016, T021, T023 |
| FR-002 | T011, T012, T016, T023 |
| FR-003 | T015 |
| FR-004 | T015, T020, T021, T022 |
| FR-005 | T017, T031, T031a |
| FR-006 | T007, T008, T010, T013 |
| FR-007 | T009, T010 |
| FR-008 | T009, T010, T030 |
| FR-008a | T009, T010, T029 |
| FR-009 | T003, T004, T013 |
| FR-010 | T005, T006 |
| FR-010a | T006, T025, T026, T027, T028 |
| FR-011 | T018, T025 |
| FR-012 | T014 |
| FR-013 | T024 |
| FR-014 | T035, T038 |
| FR-014a | T039, T040 |
| FR-015 | T034, T037 |
| FR-015a | T034, T037, T038 |
| FR-016 | T036 |
| FR-017 | T019, T022, T032 |
| FR-017a | T019, T032 |
| FR-018 | T033 |
| FR-019 | T019 |
| FR-020 | T013 |
| SC-001 | T044 |
| SC-002 | T013 |
| SC-003 | T025, T026, T027, T028 |
| SC-004 | T014 |
| SC-005 | T034, T035, T039, T040 |
| SC-006 | T024 |
| SC-007 | T042 |
| SC-008 | T031 |

## Notes

- **A suíte contra PostgreSQL, sempre.** `make test-pg` e não `make test`: sem o par
  `TEST_DB_ENGINE=postgresql` e `DB_USER` ela cai para SQLite e mente. Havendo outra worktree ativa,
  passe um `DB_NAME` próprio.
- **`T031` precisa de fixture com Retificação**, e não só de Edital publicado. É a fixture mais cara
  desta lista, e é a que sustenta a decisão `D-003` — não a substitua por um teste de unidade sobre o
  seletor.
- **As contraprovas de `T025`–`T028` são parte do teste**, não comentário: elas registram que a
  gravação passa sem o remapeamento, que é a razão de esses quatro testes existirem.
- Toda citação `FR-`, `SC-` ou `D-` escrita em código, template ou spec é varrida por
  `backend/tests/test_citacoes_de_requisito.py`. Identificador inventado quebra o CI.
