---

description: "Task list for feature implementation"
---

# Tasks: Gestão da Comissão e Alocação por Etapa

**Input**: Design documents from `/specs/011-comissao-alocacao/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/comissao.md](./contracts/comissao.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos**. O princípio V da Constituição nomeia autorização e concorrência entre
o que precisa de cobertura específica — e são exatamente as duas coisas que esta feature entrega.
Metade do que ela promete só se prova pela recusa: um percurso feliz sem os 404 não demonstra nada.

**Organization**: por história de usuário, na ordem das três entregas da seção 52 da spec — e não em
ordem de camada. Todas as histórias são P1; o desempate é a ordem de entrega que a spec declarou,
porque P-004 recusa cadastro sem efeito observável.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US6, conforme a spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. Um app
nasce nesta feature — `comissoes` (domínio, persistência e comandos) — e as telas ficam em
`interface`, que já é o canal dos dois atores.

> **⚠️ A suíte precisa de PostgreSQL, e o motivo é preciso.** `select_for_update` é inócuo em SQLite
> e os testes marcados `postgresql_only` são pulados em silêncio. Sem `TEST_DB_ENGINE=postgresql`,
> o que deixa de ser verificado é justamente o que D-016 decidiu — o bloqueio do Processo, a
> reavaliação da autorização dentro da transação e a corrida do último presidente. Rode como o
> [quickstart](./quickstart.md) manda, com `DB_NAME` próprio deste worktree.

> **⚠️ Nenhuma tarefa desta lista escreve em `editais` ou `publicacoes`.** Se alguma precisar, a
> decisão D-002 ou D-005 foi violada e o problema é de desenho, não de implementação.

---

## Phase 1: Setup

**Purpose**: o app existir, a permissão existir e as rotas terem onde nascer.

- [X] T001 [P] Criar o esqueleto do app em `backend/processo_seletivo/comissoes/` — `__init__.py`, `apps.py`, `models.py`, `domain/__init__.py`, `application/__init__.py`, `migrations/__init__.py`
- [X] T002 Registrar `processo_seletivo.comissoes` em `INSTALLED_APPS` de `backend/config/settings/base.py`
- [X] T003 Acrescentar `comissao:gerir` à lista de permissões do papel `gestor` em `backend/processo_seletivo/interface/identidade.py`
- [X] T004 [P] Teste de que `comissao:gerir` pertence ao papel `gestor` e a nenhum outro, e de que `comissao:presidir` **não** existe em `PAPEIS`, em `backend/tests/unit/comissoes/test_permissao.py`
- [X] T005 [P] Criar os pacotes de teste `backend/tests/unit/comissoes/` e `backend/tests/integration/comissoes/` com `__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: as duas entidades, a fonte única de Etapas e as duas perguntas de autorização.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T006 Implementar `MembroComissao` em `backend/processo_seletivo/comissoes/models.py` conforme [data-model.md](./data-model.md) §2 — FK protegida ao Processo, `identity_subject`, `display_label`, `funcao`, `ativo` e os campos de inativação
- [X] T007 Implementar `AlocacaoEtapa` em `backend/processo_seletivo/comissoes/models.py` conforme §3 — FK protegida ao membro e ao Edital, `etapa_id` como `UUIDField` **sem** chave estrangeira
- [X] T008 Declarar as quatro constraints em `Meta` dos dois modelos de `backend/processo_seletivo/comissoes/models.py`: duas `UniqueConstraint` parciais (`condition=Q(ativo=True)`) e dois `CheckConstraint` de coerência da inativação
- [X] T009 Gerar a migration inicial em `backend/processo_seletivo/comissoes/migrations/`, e conferir que ela não altera tabela de nenhum outro app
- [X] T010 [P] Teste das constraints em `backend/tests/integration/comissoes/test_constraints.py` — vínculo ativo duplicado recusado, alocação ativa duplicada recusada, e ambos permitidos depois da inativação (`EC-001`, `EC-002`)
- [X] T011 [P] Implementar `PRESIDENTE` e `MEMBRO` e o predicado de presidência em `backend/processo_seletivo/comissoes/domain/funcoes.py`
- [X] T012 Implementar `etapas_vigentes(edital, *, at=None)` em `backend/processo_seletivo/comissoes/domain/etapas.py`, sobre `effective_version` de `publicacoes/application/selectors.py` (D-012)
- [X] T013 [P] Teste do resolvedor em `backend/tests/unit/comissoes/test_etapas_vigentes.py` — devolve as Etapas do conteúdo vigente; **não** consulta `EtapaAvaliacao`; propaga a recusa quando não há versão publicada
- [X] T014 Implementar `pode_gerir_comissao(ator, processo)` em `backend/processo_seletivo/comissoes/domain/autorizacao.py`, devolvendo **qual base** autorizou — permissão sistêmica ou presidência (`FR-016`, D-011)
- [X] T015 Implementar `pode_atuar_na_etapa(ator, edital, etapa_id)` em `backend/processo_seletivo/comissoes/domain/autorizacao.py`, com as quatro condições do [contrato](./contracts/comissao.md) §4 — sem consultar função nem permissão
- [X] T016 [P] Teste unitário das duas funções em `backend/tests/unit/comissoes/test_autorizacao.py`, incluindo o caso do presidente **não** alocado, que gere e não atua (`FR-012`)
- [X] T017 Trocar o padrão de `new_state` e `new_revision` por sentinela `_UNSET` em `backend/processo_seletivo/auditoria/application.py`, mantendo o comportamento de quem já chama (D-014)
- [X] T018 [P] Teste da sentinela em `backend/tests/unit/test_record_event.py` — agregado sem `status`/`revision` grava com valores explícitos, e `new_revision=None` é gravado como nulo em vez de causar `AttributeError`
- [X] T019 Implementar o invólucro de comando em `backend/processo_seletivo/comissoes/application/__init__.py` — abre `command_context()`, faz `select_for_update` no Processo, **reavalia** `pode_gerir_comissao` dentro da transação, chama `ensure_processo_accepts_changes` e só então reserva a idempotência, devolvendo a base usada (D-016, `FR-067`)
- [X] T019a [P] Teste do invólucro em `backend/tests/integration/comissoes/test_comando.py` — Processo encerrado e cancelado recusam os cinco comandos; e a reserva de idempotência acontece **depois** da autorização, não antes

**Checkpoint**: o domínio responde às duas perguntas e o banco recusa duplicidade. Nada é navegável
ainda — e é por isso que esta fase não é entrega.

---

## Phase 3: User Story 1 — Constituir a comissão (P1)

**Goal**: o responsável registra quem integra a comissão do Processo e quem a preside.

**Independent Test**: com o papel Gestor, abrir `/gestao/processos/<id>/comissao`, adicionar uma
Presidente e um Membro, e ver os dois na lista — sem que nenhum deles tenha ganhado acesso a Etapa
alguma.

- [X] T020 [US1] Implementar `adicionar_membro` em `backend/processo_seletivo/comissoes/application/comissao.py` — reserva idempotência, valida função, grava e audita com a base que autorizou
- [X] T021 [P] [US1] Teste do comando em `backend/tests/integration/comissoes/test_adicionar_membro.py` — inclusão, recusa de duplicidade ativa, e repetição da mesma `idempotency_key` devolvendo o resultado original (`FR-064`)
- [X] T021a [P] [US1] Teste de idempotência dos **cinco** comandos em `backend/tests/integration/comissoes/test_idempotencia.py` — mesma chave e mesmo corpo devolve o resultado original; mesma chave com corpo diferente devolve `idempotency_conflict`; chave nova para vínculo equivalente recai na constraint (contrato §3)
- [X] T022 [P] [US1] Teste de autorização em `backend/tests/authorization/test_gestao_da_comissao.py` — ator sem base nenhuma recebe 404; ator de outro escopo recebe 404 e não 403 (`SC-016`)
- [X] T023 [US1] Implementar o formulário de membro em `backend/processo_seletivo/interface/forms.py` — identificador, rótulo opcional e função
- [X] T024 [US1] Implementar a view `comissao` (GET e POST) em `backend/processo_seletivo/interface/views.py`, no padrão de `processo_detalhe`
- [X] T025 [US1] Registrar a rota `processos/<uuid:processo_id>/comissao` em `backend/processo_seletivo/interface/urls.py`
- [X] T026 [US1] Criar `backend/processo_seletivo/interface/templates/interface/comissao.html` — lista com função, aviso de que o identificador **não** é verificado, e o formulário de inclusão (`FR-020`)
- [X] T026a [US1] Criar a etapa de confirmação em `backend/processo_seletivo/interface/templates/interface/comissao_confirmar.html`, no padrão de `processo_confirmar.html` — mostra o identificador **exatamente como será gravado**, a função e o rótulo, e só o envio dessa tela grava (`FR-022`)
- [X] T027 [US1] Ligar a Comissão à navegação a partir de `interface/templates/interface/processo_detalhe.html`
- [X] T028 [P] [US1] Teste de interface em `backend/tests/interface/test_comissao.py` — a tela lista, inclui, e mostra o aviso do identificador não verificado
- [X] T028a [US1] Teste da confirmação em `backend/tests/interface/test_comissao.py` — o primeiro envio **não** grava nada e devolve a tela de conferência com o identificador; só o segundo cria o membro (`FR-022`, `SC-UX-008`)

**Checkpoint**: a comissão existe e é navegável. Ninguém ganhou acesso a nada — que é o resultado
correto (§13 da spec).

---

## Phase 4: User Story 3 — Alocar membros às Etapas (P1)

**Goal**: o responsável indica em quais Etapas cada membro atuará, e a alocação passa a existir como
autorização.

**Independent Test**: com a comissão da US1, alocar o Membro à Etapa A1 de um Edital publicado; e
tentar alocar num Edital em elaboração, recebendo a recusa nomeada.

- [X] T029 [US3] Implementar `alocar` em `backend/processo_seletivo/comissoes/application/alocacao.py` — pelo invólucro de T019, com `reserve()`: membro ativo, Edital publicado, Etapa em `etapas_vigentes`, comissão com presidente ativo (`FR-030`, `FR-032`, `FR-033`)
- [X] T030 [US3] Implementar a verificação de coerência `etapa → edital → processo` em `backend/processo_seletivo/comissoes/application/alocacao.py` (`FR-004`), com o Edital já carregado
- [X] T031 [P] [US3] Teste do comando em `backend/tests/integration/comissoes/test_alocar.py` — sucesso; Etapa de Edital de outro Processo recusada (`EC-004`); pessoa que não é membro recusada (`EC-005`); Edital sem versão publicada recusado (`EC-014`)
- [X] T032 [P] [US3] Teste do invariante de presidência em `backend/tests/integration/comissoes/test_presidencia.py` — comissão sem presidente não aloca, e a recusa nomeia o caminho (`FR-029`, `FR-030`, `EC-006`)
- [X] T033 [US3] Implementar o seletor da organização por Edital em `backend/processo_seletivo/comissoes/application/selectors.py`, agrupando Etapas vigentes e membros alocados
- [X] T034 [US3] Implementar o formulário de alocação em `backend/processo_seletivo/interface/forms.py`
- [X] T035 [US3] Implementar a view `alocacoes` (GET e POST) em `backend/processo_seletivo/interface/views.py`
- [X] T036 [US3] Registrar a rota `processos/<uuid:processo_id>/alocacoes` em `backend/processo_seletivo/interface/urls.py`
- [X] T037 [US3] Criar `interface/templates/interface/alocacoes.html` — agrupado por Edital publicado, com **dois** estados vazios distintos: não há Edital publicado, e o Edital publicado não tem Etapas (`UX-007`, `EC-008`, `EC-014`)
- [X] T038 [P] [US3] Teste de interface em `backend/tests/interface/test_alocacoes.py` — agrupamento por Edital; Etapas homônimas de Editais distintos como objetos distintos (`EC-012`); e os dois estados vazios do `EC-008` distinguíveis um do outro

**Checkpoint**: existe distribuição registrada. Ela ainda não produz efeito para o alocado — a
próxima fase é a que fecha a vertical.

---

## Phase 5: User Story 5 — Minhas Etapas (P1) — **MVP**

**Goal**: o membro entra e vê exatamente as Etapas em que tem atribuição, e nada além.

**Independent Test**: a demonstração da seção 49 da spec, inteira — A1 abre; A2 devolve 404; B1
devolve 404; UUID adulterado devolve 404.

- [X] T039 [US5] Implementar `minhas_etapas(ator)` em `backend/processo_seletivo/comissoes/application/selectors.py` — alocações ativas, no escopo do ator, com a Etapa resolvida pelo conteúdo vigente e as órfãs fora da lista (`FR-043`, `FR-047`)
- [X] T040 [US5] Implementar a view `minhas_etapas` em `backend/processo_seletivo/interface/views.py`, **sem** exigir permissão de gestão
- [X] T041 [US5] Implementar a view `atribuicao` em `backend/processo_seletivo/interface/views.py`, que autoriza por `pode_atuar_na_etapa` **ou** `pode_gerir_comissao` e declara por qual das duas o ator chegou (`FR-050`, D-006)
- [X] T042 [US5] Registrar as rotas `minhas-etapas` e `minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>` em `backend/processo_seletivo/interface/urls.py` (D-015)
- [X] T043 [US5] Criar `interface/templates/interface/minhas_etapas.html` — Etapa, Edital, Processo, período e ação, com o estado vazio da seção 26 da spec
- [X] T044 [US5] Criar `interface/templates/interface/atribuicao.html` — contexto da Etapa e **nenhum** controle de avaliação (`FR-051`, `FR-052`)
- [X] T045 [US5] Ligar `Minhas Etapas` à navegação da base administrativa em `interface/templates/interface/base.html`, visível a qualquer identidade institucional (`UX-008`)
- [X] T046 [P] [US5] Teste de autorização em `backend/tests/authorization/test_acesso_a_etapa.py` — os quatro 404 da demonstração, mais o do escopo alheio (`SC-009`, `SC-010`, `SC-016`)
- [X] T046a [P] [US5] Teste da separação dos dois eixos de identidade em `backend/tests/authorization/test_eixos_de_identidade.py` — sessão de candidato do `portal` recebe 404 nas cinco rotas da comissão, e `MembroComissao` não concede ownership sobre `Inscricao` nem acesso a documento (`FR-061`, `FR-062`, `FR-081`, `SC-012`)
- [X] T047 [US5] Teste de que privilégio administrativo **não** injeta Etapa em `Minhas Etapas`, em `backend/tests/authorization/test_acesso_a_etapa.py` (`FR-044`, `SC-008`)
- [X] T048 [P] [US5] Teste de aceitação do percurso inteiro em `backend/tests/acceptance/test_comissao_e_alocacao.py`, com dois atores
- [X] T049 [P] [US5] Teste de fronteira em `backend/tests/interface/test_atribuicao.py` — a página não contém documento, nota, parecer nem botão de avaliar (§50 da spec)

**Checkpoint**: **MVP completo.** Gestor constitui → aloca → membro vê → não alocado não acessa. É o
contrato arquitetural da feature, e é o que a 012 vai herdar.

---

## Phase 6: User Story 6 — Alterações com efeito imediato (P1)

**Goal**: remover uma alocação revoga o acesso na hora, sem tocar em papel global.

**Independent Test**: remover o membro da Etapa A1 e ver, na janela dele, `Minhas Etapas` esvaziar e
a URL de A1 passar a devolver 404.

- [X] T050 [US6] Implementar `remover_alocacao` em `backend/processo_seletivo/comissoes/application/alocacao.py` — pelo invólucro de T019, com `reserve()`: inativa, grava quem e quando, audita
- [X] T051 [US6] Acrescentar a ação de remoção em `backend/processo_seletivo/interface/views.py` e `interface/templates/interface/alocacoes.html`, com rótulo **Remover desta Etapa** (`UX-003`)
- [X] T052 [P] [US6] Teste de integração em `backend/tests/integration/comissoes/test_remover_alocacao.py` — o vínculo de comissão permanece (`SC-006`)
- [X] T053 [P] [US6] Teste de revogação em `backend/tests/authorization/test_acesso_a_etapa.py` — depois da remoção, `Minhas Etapas` não lista e a URL devolve 404 (`FR-036`, `SC-007`)

**Checkpoint**: a alocação produz e retira efeito. A US6 da spec está demonstrada.

---

## Phase 7: User Story 2 — Gerir composição (P1)

**Goal**: alterar função e remover membro, sem deixar a comissão em estado inválido.

**Independent Test**: promover outro presidente, rebaixar o anterior, e remover um membro com duas
alocações — vendo as duas sumirem juntas.

- [X] T054 [US2] Implementar `alterar_funcao` em `backend/processo_seletivo/comissoes/application/comissao.py`, pelo invólucro de T019 e com `reserve()`, recusando rebaixar o último presidente havendo alocação ativa (`FR-030`)
- [X] T055 [US2] Implementar `remover_membro` em `backend/processo_seletivo/comissoes/application/comissao.py`, pelo invólucro de T019 e com `reserve()`, **inativando as alocações dele na mesma transação** e gravando **um evento `ALOCACAO_REMOVER` por alocação inativada** (D-016, `EC-003`, `FR-074`)
- [X] T056 [P] [US2] Teste de integração em `backend/tests/integration/comissoes/test_remover_membro.py` — cascata atômica, e nenhuma alocação ativa sob membro inativo
- [X] T057 [P] [US2] Teste da recusa do último presidente em `backend/tests/integration/comissoes/test_presidencia.py`, incluindo o caminho feliz de designar outro antes
- [X] T058 [US2] Acrescentar as duas ações a `interface/templates/interface/comissao.html`, com rótulos distintos — **Remover da comissão** versus **Remover desta Etapa** (`UX-003`, `SC-UX-002`)
- [X] T059 [P] [US2] Teste de que o presidente gere sem possuir a permissão sistêmica, e o gestor sem ser membro, em `backend/tests/authorization/test_gestao_da_comissao.py` (`SC-020`)
- [X] T060 [P] [US2] Teste de interface em `backend/tests/interface/test_comissao.py` — os dois rótulos de remoção são distinguíveis por nome acessível (`FR-077`)

**Checkpoint**: a composição é gerível por quem deve, e nenhuma operação deixa estado inválido.

---

## Phase 8: User Story 4 — Visualizar a organização do trabalho (P1)

**Goal**: o responsável vê, numa visão só, quais Etapas têm equipe e quais não têm.

**Independent Test**: abrir a organização de um Processo com três Etapas, uma sem ninguém, e
identificar a lacuna sem abrir membro nenhum.

- [X] T061 [US4] Acrescentar em `backend/processo_seletivo/comissoes/application/selectors.py` a contagem por Etapa e a marca de Etapa sem membros (`FR-038`, `SC-014`)
- [X] T062 [US4] Implementar a derivação de alocação órfã na leitura em `backend/processo_seletivo/comissoes/application/selectors.py` — comparação com `etapas_vigentes`, sem campo nem sincronizador (`FR-047`, `EC-011`)
- [X] T063 [P] [US4] Teste da derivação em `backend/tests/unit/comissoes/test_orfas.py` — Etapa removida por Retificação vira órfã; alterar nome ou peso preservando o `id` **não** vira (`FR-084`)
- [X] T064 [US4] Acrescentar a visão por membro em `backend/processo_seletivo/comissoes/application/selectors.py` e `interface/templates/interface/comissao.html` — as Etapas de uma pessoa, com o Edital de cada uma (`FR-040`)
- [X] T065 [US4] Apresentar a marca de "sem membros" e a de órfã em `interface/templates/interface/alocacoes.html` sem depender de cor (`FR-076`, `SC-UX-007`)
- [X] T066 [US4] Oferecer a remoção da alocação órfã em `interface/templates/interface/alocacoes.html`, sobre `comissoes/application/alocacao.py`, sem apagá-la em silêncio (`EC-011`)
- [X] T067 [P] [US4] Teste de regressão de D-002 em `backend/tests/integration/comissoes/test_retificacao_com_alocacao.py` — a Retificação que remove Etapa alocada é aplicada, não falha e não apaga alocação (`FR-084`, `SC-017`)

**Checkpoint**: as três entregas da spec estão cobertas. Falta o que atravessa todas.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: o que atravessa as histórias — e a tela sem a qual a auditoria não está entregue.

- [X] T068 Implementar `trilha_da_comissao(actor, processo, ...)` em `backend/processo_seletivo/auditoria/selectors.py`, reunindo membros e alocações pelo `consultar` existente (D-018)
- [X] T069 Implementar a view de auditoria do Processo em `backend/processo_seletivo/interface/views.py`, sob `auditoria:consultar`, no padrão da view `auditoria` do Edital
- [X] T070 Registrar a rota `processos/<uuid:processo_id>/auditoria` em `backend/processo_seletivo/interface/urls.py` e ligá-la a partir de `processo_detalhe.html`
- [X] T071 Acrescentar as cinco operações novas ao dicionário `OPERACOES` de `backend/processo_seletivo/interface/views.py`
- [X] T072 [P] Teste da trilha em `backend/tests/integration/comissoes/test_auditoria.py` — os cinco eventos aparecem, o `permission` de cada um diz a base real, e remover um membro com três alocações grava **quatro** eventos: um do membro e três de alocação (`FR-016`, `FR-074`, `SC-013`)
- [X] T073 [P] Teste de concorrência em `backend/tests/integration/comissoes/test_concorrencia.py`, marcado `postgresql_only`, no padrão de `test_finalizacao_concorrente.py` — **dois** presidentes e alocação ativa; remover ou rebaixar os dois concorrentemente, e exatamente uma das operações vence: a comissão nunca fica com zero presidentes (`SC-019`)
- [X] T073a Teste da reavaliação de autorização em `backend/tests/integration/comissoes/test_concorrencia.py` — um presidente rebaixado concorrentemente não conclui a alteração que começou, porque a base é reavaliada depois do bloqueio (D-016)
- [X] T074 [P] Teste de acessibilidade das quatro telas em `backend/tests/interface/test_acessibilidade.py`, no padrão existente
- [X] T075 Percorrer o [checklist-ux.md](./checklist-ux.md) em `interface/templates/interface/{comissao,alocacoes,minhas_etapas,atribuicao}.html`, incluindo teclado e 375 px (`FR-078`)
- [X] T076 [P] Conferir que nenhuma tela da feature consulta `inscricoes` nem exibe dado de candidato, em `backend/tests/interface/test_fronteira_012.py`
- [X] T076a Conferir em `backend/tests/interface/test_fronteira_012.py` que os cinco comandos não alteram `Inscricao` — contagem, `revision` e `status` inalterados depois de constituir, alocar e remover (`FR-082`)
- [X] T077 [P] Conferir que nenhuma migration da 011 toca `editais`, `publicacoes` ou `auditoria`, em `backend/tests/migrations/test_migrations.py` (`FR-083`, `SC-018`)
- [X] T077a [P] Conferir em `backend/tests/integration/comissoes/test_fronteira_de_escrita.py` que, em **runtime**, os cinco comandos escrevem apenas em `comissoes_*`, na trilha de auditoria e na reserva de idempotência — e que revisão, snapshot e hash do Edital ficam idênticos (`FR-069`, `SC-018`)
- [X] T078 Escrever a matriz de rastreabilidade em `specs/011-comissao-alocacao/traceability.md`, ligando cada FR ao teste que o prova (princípio V)

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Setup (T001–T005)
   ↓
Foundational (T006–T019a)   ← bloqueia tudo
   ↓
US1 (T020–T028a)
   ↓
US3 (T029–T038)             ← precisa de comissão com presidente
   ↓
US5 (T039–T049, com T046a)  ← MVP: a vertical fecha aqui
   ↓
US6 (T050–T053)
   ↓
US2 (T054–T060)   e   US4 (T061–T067)   ← independentes entre si
   ↓
Polish (T068–T078)
```

### User Story Dependencies

As histórias desta feature **não** são mutuamente independentes, e fingir que são produziria a
ordem horizontal que a seção 52 da spec recusa:

- **US1** não depende de ninguém.
- **US3** depende de US1: não há a quem alocar, e `FR-030` exige presidente.
- **US5** depende de US3: sem alocação, a lista é sempre o estado vazio.
- **US6** depende de US5: a revogação só é observável onde o acesso era observável.
- **US2** e **US4** dependem de US1 e US3, e não uma da outra.

### Parallel Opportunities

- Setup: T001, T004 e T005 juntas.
- Foundational: T011, T013, T016, T018 e T019a juntas depois de T006–T009; T012 e T014 tocam arquivos
  diferentes e podem seguir em paralelo.
- Dentro de cada história, todo teste marcado `[P]` roda em paralelo com os demais da mesma fase.
- T047, T073a e T076a **não** são `[P]`: cada uma escreve no mesmo arquivo da tarefa anterior (T046,
  T073 e T076). T053 toca o mesmo arquivo, mas em
  outra fase, e por isso mantém a marca.
- US2 e US4 podem ser tocadas por duas pessoas ao mesmo tempo — atenção só a `alocacoes.html`, que
  T065 e T066 compartilham.

---

## Implementation Strategy

### MVP — as fases 1 a 5

O MVP **não** é a US1. Entregar cadastro de comissão sem efeito seria exatamente o que P-004 recusa,
e o que a seção 52 da spec chama de ordem errada. O MVP é a vertical inteira:

> constituir → designar presidente → alocar → o membro vê → o não alocado recebe 404.

Ele termina em T049, e a condição de aceite não é a contagem de testes: é a demonstração da seção 49
percorrida no navegador, com as quatro URLs recusadas.

### Entrega incremental

1. **Entrega 1** — fases 1 a 5 (T001–T049, com os sufixos): a vertical e a demonstração de segurança.
2. **Entrega 2** — fases 6 a 8 (T050–T067): gestão, revogação, visão administrativa e as órfãs.
3. **Entrega 3** — fase 9 (T068–T078): trilha navegável, concorrência, acessibilidade e
   rastreabilidade.

Cada entrega termina navegável no `interface`, como o princípio VI exige.

### Notas

- A base de autorização é reavaliada **depois** do `select_for_update`, em todo comando mutável. Se
  alguma tarefa implementar a verificação antes do bloqueio, D-016 foi violada.
- Nenhuma tarefa referencia `EtapaAvaliacao`. A leitura de Etapa é sempre `etapas_vigentes()`.
- `comissao:presidir` é rótulo de trilha e não pode aparecer em `PAPEIS` — T004 existe para prender
  isso.

---

## Phase 10: Convergence

Apurado pelo `$speckit-converge` contra o código em `ebe57be`. Três lacunas, nenhuma delas
CRITICAL.

- [X] T079 Orientar em `interface/templates/interface/minhas_etapas.html` quem se identificou sem papel sistêmico e não possui alocação — o aviso que a 002 exige e que hoje só existe em `lista.html`, mantendo intacto o acesso contextual de quem tem alocação e nenhum papel per spec §45 e 002/FR-028 (contradicts)
- [X] T080 Fazer o teste de `backend/tests/interface/test_lista.py` seguir o redirecionamento e verificar a página efetivamente apresentada, em vez de abrir a lista depois do POST per spec §45 (contradicts)
- [X] T081 Sinalizar alteração concluída nas telas de Comissão e Alocação em `interface/templates/interface/comissao.html` e `alocacoes.html`, no padrão `<p class="sucesso" role="status">` já usado por `compor_base.html` e `detalhe.html`, com teste em `backend/tests/interface/test_comissao.py` per UX-006 (partial)
- [X] T082 Executar e registrar o percurso manual do [checklist-ux.md](./checklist-ux.md) nas quatro telas — teclado ponta a ponta, leitor de tela nos anúncios de sucesso e recusa, e 375 px — atualizando `traceability.md` com o resultado per SC-UX-005, SC-UX-006 e T075 (missing)

