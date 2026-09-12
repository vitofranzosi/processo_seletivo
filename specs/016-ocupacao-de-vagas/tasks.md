---

description: "Task list for feature implementation"
---

# Tasks: Ocupação de Vagas entre Listas de Concorrência

**Input**: Design documents from `specs/016-ocupacao-de-vagas/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/ocupacao.md](./contracts/ocupacao.md),
[quickstart.md](./quickstart.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo e nomeia
publicação, autorização e concorrência entre os que pedem cobertura específica; o Princípio VI fecha
a feature por percurso do ator. Nenhuma feature anterior abriu exceção.

**Organization**: por user story, para que cada uma seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US5`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`, contrato de API
em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`.

**Esta feature cria um app novo, e é diferente das anteriores.** A `014` avisava, no lugar deste
parágrafo, que criar app seria sinal de tarefa mal lida. Aqui é o contrário: o módulo `ocupacao`
existe por decisão registrada em `R-002` da pesquisa — a dependência corre num sentido só, e
`classificacao` **nunca** importa `ocupacao`. Se alguma tarefa levar você a importar na direção
contrária, ela foi mal lida.

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_016`. Suítes paralelas disputam
`test_processo_seletivo` e se derrubam.

**Três correções de modelagem já estão nos artefatos** e nenhuma tarefa deve reintroduzi-las:
`uq_apuracao_sucessora_unica` existe; o limite é `ocupadas ≤ efetivas` e **não** contra
`publicadas`; e `faltando` **não** é coluna.

---

## Phase 1: Setup

**Purpose**: o app novo, vazio e registrado.

- [ ] T001 Criar o app em `backend/processo_seletivo/ocupacao/` com `__init__.py`, `apps.py`,
      `domain/__init__.py`, `application/__init__.py` e `migrations/__init__.py`
- [ ] T002 Registrar `processo_seletivo.ocupacao` em `INSTALLED_APPS`, em
      `backend/config/settings/base.py`
- [ ] T003 [P] Criar `backend/processo_seletivo/ocupacao/domain/nomes.py` com o vocabulário da
      feature e os códigos de recusa do contrato (`ordem_nao_vigente`, `sem_quadro_publicado`,
      `recorte_sem_linha`, `motivo_da_sucessao_obrigatorio`, `deficit_zero`, `apuracao_obsoleta`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o cálculo puro e o ato. Nenhuma user story começa antes.

**⚠️ CRÍTICO**: a `T010` não pode ficar para depois. Tabela append-only sem privilégio ausente é
append-only de mentira, e a segunda passada do provisionamento é o que o retira.

### O cálculo puro (passo 1 da ordem de execução)

- [ ] T004 [P] Testes de unidade do cálculo em `backend/tests/unit/ocupacao/test_apuracao.py`:
      publicadas da **linha** e nunca do total do Perfil (`FR-240`), ampla por
      `generalCompetitionModalityId` e nunca por nome (`FR-241`), reprodutibilidade (`FR-244`)
- [ ] T005 Implementar `backend/processo_seletivo/ocupacao/domain/apuracao.py` — função pura que
      recebe quadro, ordem, recusas e movimentos lidos e devolve `publicadas`, `efetivas` e
      `ocupadas`. Sem ORM na assinatura, na forma de `classificacao/domain/faixa.py`
- [ ] T006 [P] Implementar `backend/processo_seletivo/ocupacao/domain/reversao.py` — as duas
      espécies de gatilho da `D-007` (`ON_EXHAUSTION`, `ON_BALANCE`) como funções puras
- [ ] T007 [P] Testes de unidade das duas espécies em
      `backend/tests/unit/ocupacao/test_reversao.py`, incluindo o caso que as separa: 13 de 20
      habilitados com a lista **ainda tendo gente** reverte sob saldo e não sob esgotamento

### O ato (passo 2)

- [ ] T008 Criar `ApuracaoDeOcupacao` e `MovimentoDeVaga` em
      `backend/processo_seletivo/ocupacao/models.py`, conforme [data-model.md](./data-model.md) —
      com `efetivas` (e **sem** `faltando`), `universo.movimentosLidos`, e as quatro constraints:
      as duas parciais de primeira apuração, `uq_apuracao_sucessora_unica` e
      `ck_apuracao_ocupadas_no_limite` contra `efetivas`
- [ ] T009 Gerar as migrations em `backend/processo_seletivo/ocupacao/migrations/`
- [ ] T010 Acrescentar `ocupacao_apuracaodeocupacao` e `ocupacao_movimentodevaga` a
      `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`, com o comentário da
      razão, e conferir que o provisionamento passa a informar **26**
- [ ] T011 [P] Teste do append-only em
      `backend/tests/unit/ocupacao/test_apuracao_append_only.py`: `UPDATE` e `DELETE` recusados
      pelo gatilho **e** pela ausência de privilégio (`FR-260`)
- [ ] T012 [P] Teste das constraints em `backend/tests/unit/ocupacao/test_constraints.py`: duas
      primeiras apurações do mesmo recorte recusadas — **inclusive com `lista_id` nulo nas duas**,
      que é o caso que uma constraint só deixaria passar — e **duas sucessoras da mesma anterior
      recusadas**
- [ ] T013 Implementar a emissão em
      `backend/processo_seletivo/ocupacao/application/emissao.py`: autorização, auditoria, sucessão
      com motivo obrigatório, congelamento do `universo` e das quantidades
- [ ] T014 Implementar `backend/processo_seletivo/ocupacao/application/selectors.py`: a vigente por
      recorte (**derivada** — ninguém me sucedeu) e as **quatro** causas de obsolescência
      calculadas com nome (`FR-263`), na forma de `classificacao/application/corte.py:292`
- [ ] T015 [P] Testes de integração da emissão em
      `backend/tests/integration/ocupacao/test_emissao.py`: recusa sobre ordem não vigente
      (`FR-243`), recusa sem quadro publicado (`FR-242`), recusa de sucessão sem motivo, e a
      anterior continuando legível
- [ ] T016 [P] Teste das quatro causas de obsolescência em
      `backend/tests/integration/ocupacao/test_obsolescencia.py` — uma por causa, com a causa
      nomeada na saída

**Checkpoint**: o número existe e é auditável. Nenhuma tela ainda.

---

## Phase 3: User Story 1 — Ver quantas vagas de cada lista ainda faltam (P1) 🎯 MVP

**Goal**: a presidência lê, por recorte, publicadas, ocupadas e faltando — e para de usar planilha.

**Independent Test**: com Edital publicado com quadro, ordem e corte emitidos, abrir a ocupação do
Perfil e ler os três números por recorte, sem emitir nada.

### Testes

- [ ] T017 [P] [US1] Teste de interface em `backend/tests/interface/test_ocupacao.py`: os três
      números por recorte, e **nunca um deles sozinho** (`UX-031`)
- [ ] T018 [P] [US1] Teste do Edital sem quadro em `backend/tests/interface/test_ocupacao.py`: a
      tela diz que o Edital não publicou quadro e **não** mostra zero (`UX-032`, `FR-242`)
- [ ] T019 [P] [US1] Teste de orçamento de consulta em
      `backend/tests/performance/test_ocupacao.py`: a listagem de 7 Perfis × 3 recortes não abre o
      conteúdo publicado por linha (`R-006`)

### Implementação

- [ ] T020 [US1] Implementar a view da ocupação em
      `backend/processo_seletivo/interface/views.py`, lendo colunas e SQL — `faltando` calculado na
      própria linha, como `efetivas − ocupadas`
- [ ] T021 [US1] Criar `backend/processo_seletivo/interface/templates/interface/ocupacao.html` com
      os quatro estados do contrato (`CURRENT`, `OBSOLETE`, `NOT_APPRAISED`, `NO_VACANCY_TABLE`) —
      e os dois últimos **não** são erro nem zero
- [ ] T022 [US1] Rotear a tela em `backend/processo_seletivo/interface/urls.py`, **pendendo do
      marco** como a do corte, e ligar o acesso em
      `backend/processo_seletivo/interface/templates/interface/detalhe.html`
- [ ] T023 [US1] Ação de emitir apuração pela tela — rota em
      `backend/processo_seletivo/interface/urls.py` e view em
      `backend/processo_seletivo/interface/views.py`, com o motivo exigido na sucessão
- [ ] T024 [P] [US1] Teste de responsividade a 375 px, sem tabela horizontal, em
      `backend/tests/interface/test_ocupacao.py`

**Checkpoint**: a História 1 substitui a planilha. É o MVP, e o Princípio VI já está satisfeito.

---

## Phase 4: User Story 2 — Reverter vaga reservada não preenchida (P1)

**Goal**: apurado o déficit e declarada a reversão, o quantitativo passa à linha geral do mesmo
Perfil, nomeado.

**Independent Test**: Perfil `55/20/4` com reversão declarada; a lista de PPI esgota com saldo 7; a
linha geral passa a 62 e a soma por recorte não muda.

### A declaração publicada (passo 4 da ordem de execução)

- [ ] T025 [US2] Acrescentar `especie_de_reversao` — **uma** coluna anulável — ao `PerfilVaga` em
      `backend/processo_seletivo/editais/models/perfis.py`, e a migration
- [ ] T026 [US2] Emitir `vacancyReversion` no Perfil do snapshot em
      `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [ ] T027 [US2] Elevar `SCHEMA_VERSION` para **14** em
      `backend/processo_seletivo/shared/canonical.py`, com o comentário do degrau
- [ ] T028 [US2] Implementar o degrau 14 em
      `backend/processo_seletivo/publicacoes/domain/elevacao.py` — escreve `vacancyReversion: null`
      em todo Perfil anterior, que é conversão sem invenção
- [ ] T029 [P] [US2] Teste de contrato do degrau em
      `backend/tests/contract/test_elevacao_degrau_14.py`: o acervo anterior continua legível e
      nenhuma tela passa a afirmar reversão onde não há
- [ ] T030 [US2] Ler a declaração no rascunho em
      `backend/processo_seletivo/editais/application/draft.py`
- [ ] T031 [US2] Conferir a declaração em
      `backend/processo_seletivo/editais/domain/validation.py`: os três impeditivos do contrato —
      `vacancy_reversion_kind_required` (`FR-251`), `vacancy_reversion_kind_unknown` e
      `vacancy_reversion_sem_quadro`
- [ ] T032 [P] [US2] Testes da conferência em
      `backend/tests/unit/editais/test_reversao_declarada.py`, com o caso que a `FR-251` nomeia:
      reversão declarada **sem** espécie recusa a publicação, e a ausência não vira padrão
- [ ] T033 [US2] Acrescentar a declaração a `CAMPOS_PERFIL` em
      `backend/processo_seletivo/interface/retificacao.py`, com tipo **`REFERENCIA`** e a lista
      `ESPECIES_DE_REVERSAO` — **não** caixa de texto, pelo precedente de `cutRule/tieOutcome` — e
      o rótulo do vazio dizendo o que o vazio provoca
- [ ] T034 [P] [US2] Teste da Retificação da declaração em
      `backend/tests/integration/interface/test_retificacao_reversao.py`
- [ ] T035 [US2] Elaborar a declaração na tela de composição do Perfil, em
      `backend/processo_seletivo/interface/forms.py` e `_perfil.html`
- [ ] T036 [US2] Incluir a declaração no documento publicado, em
      `backend/processo_seletivo/publicacoes/` (gerador do PDF)
- [ ] T037 [P] [US2] Teste do documento em `backend/tests/unit/publicacoes/test_pdf.py`: a
      reversão declarada aparece no documento, e o Edital sem ela não ganha seção vazia

### A reversão (passo 5)

- [ ] T038 [US2] Implementar `backend/processo_seletivo/ocupacao/application/movimento.py` — a
      reversão cria o `MovimentoDeVaga` **na mesma transação** da apuração da origem, conforme a
      §*Quando o movimento nasce* do data-model
- [ ] T039 [US2] Em `backend/processo_seletivo/ocupacao/application/emissao.py`, fazer a apuração
      do destino **ler** o movimento por `destino_lista_id` e congelar os ids em
      `universo.movimentosLidos`, sem criar um segundo registro
- [ ] T040 [P] [US2] Teste do invariante da soma constante em
      `backend/tests/unit/ocupacao/test_soma_constante.py` — **propriedade** sobre sequências
      aleatórias de reversão e liberação, porque a composição erra e não cada movimento (`R-007`)
- [ ] T041 [P] [US2] Teste de que nenhuma vaga atravessa Perfil em
      `backend/tests/integration/ocupacao/test_reversao.py` (`FR-246`) — é o item 4.5 do 57/2026
- [ ] T042 [P] [US2] Teste da obsolescência do destino em
      `backend/tests/integration/ocupacao/test_reversao.py`: recebida a reversão, o recorte de
      destino aparece obsoleto **sem que ninguém emita nada**, e vigente na emissão seguinte
      (`SC-084`)
- [ ] T043 [US2] Exibir o movimento nomeado em
      `backend/processo_seletivo/interface/templates/interface/ocupacao.html`, com origem, destino e
      quantidade — e não como mudança silenciosa do número (`UX-033`)
- [ ] T044 [P] [US2] Teste de que o Edital sem declaração não reverte, e a tela o diz, em
      `backend/tests/interface/test_ocupacao.py`

**Checkpoint**: o 57 e o 28 passam a ser conduzíveis na reversão.

---

## Phase 5: User Story 3 — Causar a faixa seguinte com déficit apurado (P1)

**Goal**: o déficit apurado substitui o motivo textual que a `014` hoje exige de quem emite.

**Independent Test**: recusada a documentação de 3 na faixa da ampla, a apuração dá `faltando` = 3 e
a faixa seguinte é emitida com o déficit como causa.

### Testes

- [ ] T045 [P] [US3] Teste de integração em
      `backend/tests/integration/ocupacao/test_causar_faixa.py`: o ato da faixa guarda o **déficit
      apurado** como causa, e não texto digitado (`FR-255`)
- [ ] T046 [P] [US3] Teste da recusa com déficit zero (`FR-256`) e da recusa sobre apuração
      obsoleta (`FR-263`), em `backend/tests/integration/ocupacao/test_causar_faixa.py`
- [ ] T047 [P] [US3] Teste de direção da dependência em
      `backend/tests/test_dependencia_da_ocupacao.py`: **nenhum** módulo de `classificacao` importa
      `ocupacao` (`R-002`)

### Implementação

- [ ] T048 [US3] Implementar `backend/processo_seletivo/ocupacao/application/causar_faixa.py`,
      chamando `classificacao.application.emissao_do_corte` com o déficit — a seta é desta feature
      para a `014`, nunca o contrário
- [ ] T049 [US3] Ação para pedir a faixa seguinte pela ocupação — rota em
      `backend/processo_seletivo/interface/urls.py` e view em
      `backend/processo_seletivo/interface/views.py`
- [ ] T050 [P] [US3] Teste do vocabulário em `backend/tests/test_vocabulario_da_ocupacao.py`:
      nenhuma tela, ato ou mensagem desta feature usa termo de convocação, aceite ou matrícula
      (`FR-258`, `UX-034`), na forma de `test_vocabulario_do_corte.py`

**Checkpoint**: o ciclo do 77/2026 fecha de ponta a ponta.

---

## Phase 6: User Story 4 — Quem ocupa por duas listas ao mesmo tempo (P2)

**Goal**: ocupar pela ampla libera a vaga reservada, que volta ao recorte reservado.

**Independent Test**: alguém dentro do número de vagas nas duas listas ocupa pela ampla, e a vaga
reservada alcança o próximo da **lista reservada**.

### Testes

- [ ] T051 [P] [US4] Teste em `backend/tests/integration/ocupacao/test_concomitancia.py`: quem
      está dentro nas duas listas ocupa pela ampla (`FR-254`) e não é computado na reservada
      (`FR-252`)
- [ ] T052 [P] [US4] Teste do recorte de destino da liberação em
      `backend/tests/integration/ocupacao/test_concomitancia.py`: a vaga volta para a **lista
      reservada** e nunca para a linha geral (`FR-253`). É a troca que mantém a soma certa com o
      recorte errado, e só a asserção de recorte a pega
- [ ] T053 [P] [US4] Teste do caso em que a lista reservada esgota, em
      `backend/tests/integration/ocupacao/test_concomitancia.py`: o que sobra é déficit reservado,
      e a reversão da História 2 decide o destino

### Implementação

- [ ] T054 [US4] Implementar a liberação em
      `backend/processo_seletivo/ocupacao/application/movimento.py`, com `inscricao` preenchida —
      é movimento de pessoa, e a constraint `ck_movimento_inscricao_conforme_especie` o exige
- [ ] T055 [US4] Exibir a liberação nomeada em
      `backend/processo_seletivo/interface/templates/interface/ocupacao.html`, distinta da
      reversão

**Checkpoint**: o item 8.9 do 28/2026 está alcançado. A outra metade do 8.8 continua fora, por
depender de desistência, que é fato da `019` (`R-001`).

---

## Phase 7: User Story 5 — Auditar a ocupação de ponta a ponta (P3)

**Goal**: cada número exibido tem trilha até o ato que o produziu.

**Independent Test**: reconstruir o número de hoje a partir do quadro publicado, pela auditoria.

- [ ] T056 [P] [US5] Teste em `backend/tests/integration/ocupacao/test_auditoria.py`: a sequência
      quadro → apurações → movimentos reconstrói o número vigente (`FR-259`)
- [ ] T057 [P] [US5] Teste de que fica legível **qual versão do quadro** cada apuração leu, em
      `backend/tests/integration/ocupacao/test_auditoria.py`
- [ ] T058 [US5] Tela de histórico em
      `backend/processo_seletivo/interface/templates/interface/ocupacao_historico.html`, com rota
      pendendo do Edital em `backend/processo_seletivo/interface/urls.py` — o precedente é
      `corte-historico`, que pende do Edital e não do marco justamente para sobreviver à Retificação
- [ ] T059 [US5] Registrar ator, ato, estados, motivo e correlação na auditoria, em
      `backend/processo_seletivo/ocupacao/application/emissao.py`

**Checkpoint**: todas as histórias estão independentemente funcionais.

---

## Phase 8: Polish & Cross-Cutting

- [ ] T060 [P] Acrescentar `vacancyReversion` ao `openapi.yaml` em
      `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, nos **dois** lugares em que o
      Perfil aparece
- [ ] T061 [P] Acrescentar os três endpoints do contrato ao `openapi.yaml`
- [ ] T062 [P] Escrever `specs/016-ocupacao-de-vagas/rastreabilidade.md` — matriz
      `FR-239`–`FR-263`, `SC-078`–`SC-084`, `UX-031`–`UX-034` contra arquivo de teste
- [ ] T063 [P] Acrescentar a linha da `016` à tabela de incrementos do `README.md` — o resíduo já
      apareceu três vezes, e nenhum `tasks.md` anterior tinha esta tarefa
- [ ] T064 Atualizar a contagem da suíte no `README.md` e no `AGENTS.md` com o número medido
- [ ] T065 Percorrer o [quickstart](./quickstart.md) pela interface, contra servidor real, e
      registrar o relatório em `doc/e2e/016-ocupacao-de-vagas/relatorio.md`
- [ ] T066 Rodar `cd backend && DB_NAME=ps_demo_016 make lint check test-pg` e registrar o
      resultado no commit que fecha a feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: sem dependências
- **Foundational (2)**: depende de 1 — **bloqueia todas as histórias**
- **US1 (3)**: depende de 2. É o MVP
- **US2 (4)**: depende de 2. A declaração publicada (`T025`–`T037`) é pré-requisito da reversão
  (`T038`+), e não o contrário
- **US3 (5)**: depende de 2. Independe da US2
- **US4 (6)**: depende de 2 e **da US2**, porque a liberação usa o `MovimentoDeVaga` que a `T038`
  cria
- **US5 (7)**: depende de 2; rende mais depois da US2 e da US4, que geram movimentos para auditar
- **Polish (8)**: depois das histórias desejadas

### A única dependência entre histórias

`US4 → US2`, pelo `MovimentoDeVaga`. As demais são independentes entre si e só dependem da
Foundational. **US1, US2 e US3 podem correr em paralelo** depois da Phase 2.

### Parallel Opportunities

- `T003` na Phase 1
- `T004`, `T006`, `T007` (cálculo puro) antes de `T008`; `T011`, `T012`, `T015`, `T016` depois dela
- Todos os testes marcados `[P]` dentro de cada história
- `T060`–`T063` na Phase 8

---

## Implementation Strategy

### MVP: só a US1

1. Phase 1 → Phase 2 → Phase 3
2. **PARE e VALIDE**: os três números na tela, e o Edital sem quadro dizendo que não tem quadro
3. A planilha já foi substituída, e o Princípio VI está satisfeito

### Entrega incremental

1. Setup + Foundational → o número existe e é auditável
2. + US1 → a tela (MVP)
3. + US3 → o ciclo do 77/2026 fecha
4. + US2 → o 57 e o 28 na reversão
5. + US4 → a concorrência concomitante do 28
6. + US5 → a trilha completa

**A ordem 3 antes de 4 é deliberada**: a US3 não precisa da declaração publicada, e fecha um Edital
inteiro com menos travessia. A §8 da spec sugere o contrário, e aqui a dependência real manda.

---

## Notas

- `[P]` = arquivos distintos, sem dependência pendente
- Nenhuma tarefa reintroduz `faltando` como coluna, nem compara `ocupadas` com `publicadas`
- Nenhuma tarefa faz `classificacao` importar `ocupacao`
- `T010` não se adia: sem ela as tabelas não são append-only de verdade
- Comitar por tarefa ou grupo lógico; parar em qualquer checkpoint para validar
