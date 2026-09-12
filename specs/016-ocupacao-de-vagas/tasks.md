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

- [X] T001 Criar o app em `backend/processo_seletivo/ocupacao/` com `__init__.py`, `apps.py`,
      `domain/__init__.py`, `application/__init__.py` e `migrations/__init__.py`
- [X] T002 Registrar `processo_seletivo.ocupacao` em `INSTALLED_APPS`, em
      `backend/config/settings/base.py`
- [X] T003 [P] Criar `backend/processo_seletivo/ocupacao/domain/nomes.py` com o vocabulário da
      feature e os códigos de recusa do contrato (`ordem_nao_vigente`, `sem_quadro_publicado`,
      `recorte_sem_linha`, `motivo_da_sucessao_obrigatorio`, `deficit_zero`, `apuracao_obsoleta`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o cálculo puro e o ato. Nenhuma user story começa antes.

**⚠️ CRÍTICO**: a `T010` não pode ficar para depois. Tabela append-only sem privilégio ausente é
append-only de mentira, e a segunda passada do provisionamento é o que o retira.

### O cálculo puro (passo 1 da ordem de execução)

- [X] T004 [P] Testes de unidade do cálculo em `backend/tests/unit/ocupacao/test_apuracao.py`:
      publicadas da **linha** e nunca do total do Perfil (`FR-240`), ampla por
      `generalCompetitionModalityId` e nunca por nome (`FR-241`), reprodutibilidade (`FR-244`)
- [X] T005 Implementar `backend/processo_seletivo/ocupacao/domain/apuracao.py` — função pura que
      recebe quadro, ordem, recusas e movimentos lidos e devolve `publicadas`, `efetivas` e
      `ocupadas`. Sem ORM na assinatura, na forma de `classificacao/domain/faixa.py`
- [X] T006 [P] Implementar `backend/processo_seletivo/ocupacao/domain/reversao.py` — as duas
      espécies de gatilho da `D-007` (`ON_EXHAUSTION`, `ON_BALANCE`) como funções puras
- [X] T007 [P] Testes de unidade das duas espécies em
      `backend/tests/unit/ocupacao/test_reversao.py`, incluindo o caso que as separa: 13 de 20
      habilitados com a lista **ainda tendo gente** reverte sob saldo e não sob esgotamento

### O ato (passo 2)

- [X] T008 Criar `ApuracaoDeOcupacao` e `MovimentoDeVaga` em
      `backend/processo_seletivo/ocupacao/models.py`, conforme [data-model.md](./data-model.md) —
      com `efetivas` (e **sem** `faltando`), `universo.movimentosLidos`, e as quatro constraints:
      as duas parciais de primeira apuração, `uq_apuracao_sucessora_unica` e
      `ck_apuracao_ocupadas_no_limite` contra `efetivas`
- [X] T009 Gerar as migrations em `backend/processo_seletivo/ocupacao/migrations/`
- [X] T010 Acrescentar `ocupacao_apuracaodeocupacao` e `ocupacao_movimentodevaga` a
      `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`, com o comentário da
      razão, e conferir que o provisionamento passa a informar **26**
- [X] T011 [P] Teste do append-only em
      `backend/tests/unit/ocupacao/test_apuracao_append_only.py`: `UPDATE` e `DELETE` recusados
      pelo gatilho **e** pela ausência de privilégio (`FR-260`)
- [X] T012 [P] Teste das constraints em `backend/tests/unit/ocupacao/test_constraints.py`: duas
      primeiras apurações do mesmo recorte recusadas — **inclusive com `lista_id` nulo nas duas**,
      que é o caso que uma constraint só deixaria passar — e **duas sucessoras da mesma anterior
      recusadas**
- [X] T013 Implementar a emissão em
      `backend/processo_seletivo/ocupacao/application/emissao.py`: autorização, auditoria, sucessão
      com motivo obrigatório, congelamento do `universo` e das quantidades
- [X] T014 Implementar `backend/processo_seletivo/ocupacao/application/selectors.py`: a vigente por
      recorte (**derivada** — ninguém me sucedeu) e as **quatro** causas de obsolescência
      calculadas com nome (`FR-263`), na forma de `classificacao/application/corte.py:292`
- [X] T015 [P] Testes de integração da emissão em
      `backend/tests/integration/ocupacao/test_emissao.py`: recusa sobre ordem não vigente
      (`FR-243`), recusa sem quadro publicado (`FR-242`), recusa de sucessão sem motivo, e a
      anterior continuando legível
- [X] T016 [P] Teste das quatro causas de obsolescência em
      `backend/tests/integration/ocupacao/test_obsolescencia.py` — uma por causa, com a causa
      nomeada na saída

**Checkpoint**: o número existe e é auditável. Nenhuma tela ainda.

---

## Phase 3: User Story 1 — Ver quantas vagas de cada lista ainda faltam (P1) 🎯 MVP

**Goal**: a presidência lê, por recorte, publicadas, ocupadas e faltando — e para de usar planilha.

**Independent Test**: com Edital publicado com quadro, ordem e corte emitidos, abrir a ocupação do
Perfil e ler os quatro números por recorte, sem emitir nada.

### Testes

- [X] T017 [P] [US1] Teste de interface em `backend/tests/interface/test_ocupacao.py`: com apuração
      emitida, os **quatro** números por recorte — publicadas, efetivas, ocupadas, faltando —, e
      **nunca um deles sozinho** (`UX-031`). Onde nenhum movimento alcançou o recorte, publicadas e
      efetivas coincidem; onde divergem, os dois aparecem
- [X] T017a [P] [US1] Teste do recorte **sem apuração** no mesmo arquivo (`UX-032a`): a tela diz
      "ocupação ainda não apurada", oferece a ação de emitir, mostra as **publicadas** — que são
      fato do Edital — e **não** mostra efetivas, ocupadas nem faltando. *Zero ali seria afirmar
      "não há vaga a ocupar" sem ato que o sustente*
- [X] T018 [P] [US1] Teste do Edital sem quadro em `backend/tests/interface/test_ocupacao.py`: a
      tela diz que o Edital não publicou quadro e **não** mostra zero (`UX-032`, `FR-242`)
- [X] T019 [P] [US1] Teste de orçamento de consulta em
      `backend/tests/performance/test_ocupacao.py`: a listagem de 7 Perfis × 3 recortes não abre o
      conteúdo publicado por linha (`R-006`)
- [X] T019a [P] [US1] Teste em `backend/tests/interface/test_ocupacao.py` de que **ler não ocupa**
      (`FR-261`): abrir a tela do recorte **não** emite apuração — contagem de
      `ApuracaoDeOcupacao` igual antes e depois do `GET`. *Nenhuma outra tarefa provava isso, e a
      `014` já nomeou o defeito equivalente: ler não corta*
- [X] T019b [P] [US1] Medir o teto de volume em
      `backend/tests/performance/test_ocupacao.py` (`SC-082`): apuração de um Edital com **7
      Perfis** — os polos, pela `D-005` — de 3 listas cada, com **1.000 participantes por
      recorte**, em **no máximo o dobro** do tempo da emissão da ordem no mesmo volume, medido na
      mesma execução. *A `T019` mede contagem de consulta, que é outra grandeza; e a razão contra
      uma operação já existente é mais estável que um tempo absoluto, que varia com a máquina*

### Implementação

- [X] T020 [US1] Implementar a view da ocupação em
      `backend/processo_seletivo/interface/views.py`, lendo colunas e SQL — `faltando` calculado na
      própria linha, como `efetivas − ocupadas`, e `publicadas` exibida **sem** ser alterada por
      movimento (`FR-239a`). Quantidade que nenhum ato produziu chega **nula** à tela, nunca zero
- [X] T021 [US1] Criar `backend/processo_seletivo/interface/templates/interface/ocupacao.html` com
      os quatro números da `UX-031` e os quatro estados do contrato (`CURRENT`, `OBSOLETE`,
      `NOT_APPRAISED`, `NO_VACANCY_TABLE`) — e os dois últimos **não** são erro nem zero. Em
      `NOT_APPRAISED` a linha traz a quantidade publicada e a ação de emitir, e nada mais
- [X] T022 [US1] Rotear a tela em `backend/processo_seletivo/interface/urls.py`, **pendendo do
      marco** como a do corte, e ligar o acesso em
      `backend/processo_seletivo/interface/templates/interface/detalhe.html`
- [X] T023 [US1] Ação de emitir apuração pela tela — rota em
      `backend/processo_seletivo/interface/urls.py` e view em
      `backend/processo_seletivo/interface/views.py`, com o motivo exigido na sucessão
- [X] T024 [P] [US1] Teste de responsividade a 375 px, sem tabela horizontal, em
      `backend/tests/interface/test_ocupacao.py`

**Checkpoint**: a História 1 substitui a planilha. É o MVP, e o Princípio VI já está satisfeito.

---

## Phase 4: User Story 2 — Reverter vaga reservada não preenchida (P1)

**Goal**: apurado o déficit e declarada a reversão, o quantitativo passa à linha geral do mesmo
Perfil, nomeado.

**Independent Test**: Perfil `55/20/4` com reversão declarada; a lista de PPI esgota com saldo 7; a
linha geral passa a 62 e a soma por recorte não muda.

### A declaração publicada (passo 4 da ordem de execução)

- [X] T025 [US2] Acrescentar `especie_de_reversao` — **uma** coluna anulável — ao `PerfilVaga` em
      `backend/processo_seletivo/editais/models/perfis.py`, e a migration
- [X] T026 [US2] Emitir `vacancyReversion` no Perfil do snapshot em
      `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [X] T027 [US2] Elevar `SCHEMA_VERSION` para **14** em
      `backend/processo_seletivo/shared/canonical.py`, com o comentário do degrau
- [X] T028 [US2] Implementar o degrau 14 em
      `backend/processo_seletivo/publicacoes/domain/elevacao.py` — escreve `vacancyReversion: null`
      em todo Perfil anterior, que é conversão sem invenção
- [X] T029 [P] [US2] Teste de contrato do degrau em
      `backend/tests/contract/test_elevacao_degrau_14.py`: o acervo anterior continua legível e
      nenhuma tela passa a afirmar reversão onde não há
- [X] T030 [US2] Ler a declaração no rascunho em
      `backend/processo_seletivo/editais/application/draft.py`
- [X] T031 [US2] Conferir a declaração em
      `backend/processo_seletivo/editais/domain/validation.py`: os três impeditivos do contrato —
      `vacancy_reversion_kind_required` (`FR-251`), `vacancy_reversion_kind_unknown` e
      `vacancy_reversion_sem_quadro`
- [X] T032 [P] [US2] Testes da conferência em
      `backend/tests/unit/editais/test_reversao_declarada.py`, com o caso que a `FR-251` nomeia:
      reversão declarada **sem** espécie recusa a publicação, e a ausência não vira padrão
- [X] T033 [US2] Acrescentar a declaração a `CAMPOS_PERFIL` em
      `backend/processo_seletivo/interface/retificacao.py`, com tipo **`REFERENCIA`** e a lista
      `ESPECIES_DE_REVERSAO` — **não** caixa de texto, pelo precedente de `cutRule/tieOutcome` — e
      o rótulo do vazio dizendo o que o vazio provoca
- [X] T034 [P] [US2] Teste da Retificação da declaração em
      `backend/tests/integration/interface/test_retificacao_reversao.py`
- [X] T035 [US2] Elaborar a declaração na tela de composição do Perfil, em
      `backend/processo_seletivo/interface/forms.py` e `_perfil.html`
- [X] T036 [US2] Incluir a declaração no documento publicado, em
      `backend/processo_seletivo/publicacoes/` (gerador do PDF)
- [X] T037 [P] [US2] Teste do documento em `backend/tests/unit/publicacoes/test_pdf.py`: a
      reversão declarada aparece no documento, e o Edital sem ela não ganha seção vazia

### A reversão (passo 5)

- [X] T038 [US2] Implementar `backend/processo_seletivo/ocupacao/application/movimento.py` — a
      reversão cria o `MovimentoDeVaga` **na mesma transação** da apuração da origem, conforme a
      §*Quando o movimento nasce* do data-model
- [X] T039 [US2] Em `backend/processo_seletivo/ocupacao/application/emissao.py`, fazer a apuração
      do destino **ler** o movimento por `destino_lista_id` e congelar os ids em
      `universo.movimentosLidos`, sem criar um segundo registro
- [X] T040 [P] [US2] Teste do invariante da soma constante em
      `backend/tests/unit/ocupacao/test_soma_constante.py` — **propriedade** sobre sequências
      aleatórias de reversão, afirmando o invariante nos **dois** recortes que o movimento toca,
      porque a composição erra e não cada movimento (`R-007`).
      No mesmo arquivo, que **`publicadas` nunca muda** por movimento algum (`FR-239a`): o que a
      reversão move é a quantidade efetiva, e o publicado é intocável
- [X] T041 [P] [US2] Teste de que nenhuma vaga atravessa Perfil em
      `backend/tests/integration/ocupacao/test_reversao.py` (`FR-246`) — é o item 4.5 do 57/2026
- [X] T042 [P] [US2] Teste da obsolescência do destino em
      `backend/tests/integration/ocupacao/test_reversao.py`: recebida a reversão, o recorte de
      destino aparece obsoleto **sem que ninguém emita nada**, e vigente na emissão seguinte
      (`SC-084`)
- [X] T043 [US2] Exibir o movimento nomeado em
      `backend/processo_seletivo/interface/templates/interface/ocupacao.html`, com origem, destino e
      quantidade — e não como mudança silenciosa do número (`UX-033`)
- [X] T044 [P] [US2] Teste de que o Edital sem declaração não reverte, e a tela o diz, em
      `backend/tests/interface/test_ocupacao.py`

**Checkpoint**: o 57 e o 28 passam a ser conduzíveis na reversão.

---

## Phase 5: User Story 3 — Causar a faixa seguinte com déficit apurado (P1)

**Goal**: o déficit apurado substitui o motivo textual que a `014` hoje exige de quem emite.

**Independent Test**: recusada a documentação de 3 na faixa da ampla, a apuração dá `faltando` = 3 e
a faixa seguinte é emitida com o déficit como causa.

### Testes

- [X] T045 [P] [US3] Teste de integração em
      `backend/tests/integration/ocupacao/test_causar_faixa.py`: o ato da faixa guarda o **déficit
      apurado** como causa, e não texto digitado (`FR-255`)
- [X] T046 [P] [US3] Teste da recusa com déficit zero (`FR-256`) e da recusa sobre apuração
      obsoleta (`FR-263`), em `backend/tests/integration/ocupacao/test_causar_faixa.py`
- [X] T047 [P] [US3] Teste de dependência em
      `backend/tests/test_dependencia_da_ocupacao.py`, varrendo os imports por AST. Duas asserções:
      **nenhum** módulo de `classificacao` importa `ocupacao` (`R-002`); e **nenhum** módulo de
      `ocupacao` importa o que ordena ou desempata (`FR-257`) — a lista permitida é
      `classificacao.models`, `classificacao.application.selectors` e
      `classificacao.application.emissao_do_corte`, e ficam **proibidos**
      `classificacao.application.emissao` (que emite ordem), `classificacao.domain.combinacao` e
      `classificacao.domain.desempate`. *É o que torna a proibição verificável: ela é de import, e
      não de redação — `emissao_do_corte` é a única porta, porque é por ela que a `016` causa a
      faixa sem escolher ninguém*

### Implementação

- [X] T048 [US3] Implementar `backend/processo_seletivo/ocupacao/application/causar_faixa.py`,
      chamando `classificacao.application.emissao_do_corte` com o déficit — a seta é desta feature
      para a `014`, nunca o contrário
- [X] T049 [US3] Ação para pedir a faixa seguinte pela ocupação — rota em
      `backend/processo_seletivo/interface/urls.py` e view em
      `backend/processo_seletivo/interface/views.py`
- [X] T050 [P] [US3] Teste do vocabulário em `backend/tests/test_vocabulario_da_ocupacao.py`:
      nenhuma tela, ato ou mensagem desta feature usa termo de convocação, aceite ou matrícula
      (`FR-258`, `UX-034`), na forma de `test_vocabulario_do_corte.py`. *A proibição estrutural da
      `FR-257` mora na `T047`, e não aqui: varredura de texto não prova que nenhum caminho ordena —
      prova de import prova*

**Checkpoint**: o ciclo do 77/2026 fecha de ponta a ponta.

---

## Phase 6: User Story 4 — Quem ocupa por duas listas ao mesmo tempo (P2)

**Goal**: ocupar pela ampla exclui a pessoa do preenchimento da reservada, sem mover quantidade.

**Independent Test**: alguém dentro do número de vagas nas duas listas ocupa pela ampla, não consta
ocupando na reservada, e a vaga dela continua na **lista reservada**, alcançando o próximo.

### Testes

- [X] T051 [P] [US4] Teste em `backend/tests/integration/ocupacao/test_concomitancia.py`: quem
      está dentro nas duas listas ocupa pela ampla (`FR-254`) e não é computado na reservada
      (`FR-252`)
- [X] T052 [P] [US4] Teste de que a exclusão **não transfere quantidade**, em
      `backend/tests/integration/ocupacao/test_concomitancia.py`: a vaga reservada permanece no
      recorte reservado e as efetivas dos dois recortes não se alteram (`FR-253`). É a troca que
      mantém a soma certa com os recortes errados — 1 e 2 onde o Edital manda 2 e 1 —, e só a
      asserção por recorte a pega
- [X] T053 [P] [US4] Teste do caso em que a lista reservada esgota, em
      `backend/tests/integration/ocupacao/test_concomitancia.py`: o que sobra é déficit reservado,
      e a reversão da História 2 decide o destino

### Implementação

- [X] T054 [US4] Implementar a exclusão em
      `backend/processo_seletivo/ocupacao/domain/apuracao.py`, pelo parâmetro `ocupantes_da_ampla`
      que sai do cálculo das ocupadas do recorte reservado — **no cálculo, e não em movimento**.
      *A redação anterior pedia implementá-la em `application/movimento.py` com `inscricao`
      preenchida, sob a constraint `ck_movimento_inscricao_conforme_especie`: é a modelagem que a
      revisão da US4 derrubou, e a migration `0002_liberacao_nao_e_movimento` desfez.*
- [X] T055 [US4] Exibir na tela, em
      `backend/processo_seletivo/interface/templates/interface/ocupacao.html`, que a reservada
      mantém a vaga de quem ocupou pela ampla — **sem** desenhar movimento, porque a concomitância
      não move quantidade nenhuma. *A redação anterior pedia "a liberação nomeada, distinta da
      reversão", e partia da modelagem que a revisão da US4 derrubou.*

**Checkpoint**: o item 8.9 do 28/2026 está alcançado. A outra metade do 8.8 continua fora, por
depender de desistência, que é fato da `019` (`R-001`).

---

## Phase 7: User Story 5 — Auditar a ocupação de ponta a ponta (P3)

**Goal**: cada número exibido tem trilha até o ato que o produziu.

**Independent Test**: reconstruir o número de hoje a partir do quadro publicado, pela auditoria.

- [X] T056 [P] [US5] Teste em `backend/tests/integration/ocupacao/test_auditoria.py`: a sequência
      quadro → apurações → movimentos reconstrói o número vigente (`FR-259`), pelo invariante
      completo `publicadas + recebidas − cedidas = efetivas` e afirmado **nos dois recortes** que o
      movimento tocou — só o destino deixaria a origem sem verificação, e é nela que a reversão
      poderia ceder a mesma quantidade duas vezes
- [X] T057 [P] [US5] Teste de que fica legível **qual versão do quadro** cada apuração leu, em
      `backend/tests/integration/ocupacao/test_auditoria.py`
- [X] T058 [US5] Tela de histórico em
      `backend/processo_seletivo/interface/templates/interface/ocupacao_historico.html`, com rota em
      `backend/processo_seletivo/interface/urls.py` que **carrega** o marco no caminho e **não o
      resolve** no snapshot vigente. *A redação anterior dizia "rota pendendo do Edital… que pende
      do Edital e não do marco", e descrevia mal as duas coisas: o caminho é
      `editais/<edital>/marcos/<marco>/ocupacao/historico` — o marco está nele —, e o que mantém o
      histórico acessível não é a forma do caminho, é a view não chamar `_perfil_do_marco`, que
      levanta 404 quando o marco não está na versão vigente.* O precedente é `corte-historico`, que
      endereça o **corte** e não o marco pela mesma razão. A série é encontrada pelas identidades
      publicadas que as apurações guardaram, e a regressão
      `test_o_historico_sobrevive_a_retificacao_que_remove_o_marco` prende as duas metades:
      `interface:ocupacao` devolve 404 e o histórico devolve 200
- [X] T059 [US5] Registrar ator, ato, estados, motivo e correlação na auditoria, em
      `backend/processo_seletivo/ocupacao/application/emissao.py`

**Checkpoint**: todas as histórias estão independentemente funcionais.

---

## Phase 8: Polish & Cross-Cutting

- [X] T060 [P] Acrescentar `vacancyReversion` ao `openapi.yaml` em
      `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, nos **dois** lugares em que o
      Perfil aparece. **E ela encontrou um defeito que nenhuma tarefa desta feature previu**: o
      campo era emitido pela publicação e elevado pelo degrau 14, e a **forma publicada não o
      conferia** — `PERFIL_PUBLICADO` em `backend/processo_seletivo/editais/domain/validation.py`
      não o transcrevia, e o Perfil acrescentado por Retificação nascia sem ele. É literalmente o
      defeito que o `T110` da `014` fechou para `generalCompetitionModalityId` — *"o degrau 13
      emitia campo que a forma publicada não conferia"* —, repetido um degrau depois. Quem o
      encontrou foi `tests/contract/test_forma_publicada.py`, que confronta a transcrição com o
      contrato: enquanto o contrato não declarava o campo, as duas listas coincidiam **por
      ausência**. Fechado em quatro lugares: a transcrição, o Perfil acrescentado por Retificação,
      a fixture do snapshot e o conjunto esperado de `test_forma_do_snapshot.py`
- [X] T061 [P] Converter a §2 de `specs/016-ocupacao-de-vagas/contracts/ocupacao.md` em **contrato
      de aplicação** e retirar dela os três caminhos `/api/...`. *A tarefa pedia acrescentá-los ao
      `openapi.yaml`, e isso estava errado: eles não existem. Nenhuma tarefa desta feature
      implementou rota HTTP — a `T017`, a `T020` e a `T045` entregam a capacidade por
      `interface/views.py` —, e o `openapi.yaml` não tem um único caminho de classificação, corte ou
      sorteio: a `014` acrescentou ali apenas a **forma do conteúdo** (`cutRule`,
      `generalCompetitionModalityId`), pela mesma razão. Declará-los seria documentar interface que
      responde 404, e contrato de API é a promessa mais barata de quebrar sem notar, porque teste
      nenhum o confronta com as rotas.* Os nomes da seção passaram a ser os dos selectors e dos
      commands — `ocupacao_do_recorte`, `emitir_apuracao`, `causar_faixa_seguinte` —, e o cabeçalho
      declara as duas naturezas: a §1 é contrato de API, a §2 é de aplicação. Que a ocupação venha a
      ter API é decisão aberta, e o desenho de partida fica registrado ali
- [X] T062 [P] Escrever `specs/016-ocupacao-de-vagas/rastreabilidade.md` — matriz
      `FR-239`–`FR-263` (incluindo `FR-239a` e `FR-253a`), `SC-078`–`SC-084`, `UX-031`–`UX-034`
      (incluindo `UX-032a`) contra arquivo de teste, **medida por varredura e não afirmada**.
      Cobertura 39 de 39, e a matriz **torna explícitos os dez** que chegaram aqui provados por
      teste que não os citava: `FR-239`, `FR-253`, `FR-253a`, `FR-254`, `FR-258`, `UX-034`,
      `SC-078`, `SC-080`, `SC-083` e — por rótulo parcial — a metade de interface da `SC-081`.
      A prova existia; o rótulo, não, e quatro critérios continuam dependendo da `T065`
- [X] T063 [P] Acrescentar a linha da `016` à tabela de incrementos do `README.md` — o resíduo já
      apareceu três vezes, e nenhum `tasks.md` anterior tinha esta tarefa. **Faltava também a da
      `014`**, já mergeada na `main`: a tabela ia de `013` a `015`, e as duas entraram
- [X] T064 Atualizar a contagem da suíte no `README.md` e no `AGENTS.md` com o número medido:
      **5082 passando e 2 pulados** contra PostgreSQL, e **33 falham / 4850 passam / 201 puladas**
      no modo padrão, reclassificadas em 13 + 9 + 11 por causa medida. *As duas do modo padrão que
      a `016` acrescenta são da segunda classe: a mensagem do SQLite não nomeia
      `uq_apuracao_sucessora_unica`, e o `pytest.raises(match=...)` não casa.* **Atenção ao
      mergear**: o PR do achado da `R-006` altera estas mesmas linhas com os números de antes da
      `016` (4862 e 24 tabelas), e o conflito é esperado — quem entrar depois fica com 5076 e 26
- [X] T065 Percorrer o [quickstart](./quickstart.md) pela interface, contra servidor real, e
      registrar o relatório em `doc/e2e/016-ocupacao-de-vagas/relatorio.md`. **Seis defeitos
      encontrados e corrigidos, com teste que os prende** — dois eram afirmação falsa na tela, um
      deixava apuração vencida parecendo vigente (`corte_obsoleto` só olhava um sentido) e um
      deixava a ação irreversível da faixa seguinte **sem confirmação alguma**. E **dois defeitos do
      guia**: o Cenário 3 mandava introduzir a declaração de reversão por Retificação, o que o
      catálogo não oferece, e os Cenários 3 e 5 exigem marco de **sorteio**, que o guia não dizia —
      num marco calculado só a linha geral tem ordem. Os dois foram corrigidos no `quickstart.md`
- [X] T066 Rodar `cd backend && DB_NAME=ps_demo_016 make lint check test-pg` e registrar o
      resultado no commit que fecha a feature: **`lint` limpo nos dois passos**, `check` e
      `makemigrations --check` sem pendência, e **5082 passando com 2 pulados** — os dois
      deliberados. *Rodada **depois** da `T065`, e não antes: o percurso conduzido acrescentou seis
      testes, e medir antes dele teria registrado um número que o commit não teria.*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: sem dependências
- **Foundational (2)**: depende de 1 — **bloqueia todas as histórias**
- **US1 (3)**: depende de 2. É o MVP
- **US2 (4)**: depende de 2. A declaração publicada (`T025`–`T037`) é pré-requisito da reversão
  (`T038`+), e não o contrário
- **US3 (5)**: depende de 2. Independe da US2
- **US4 (6)**: depende de 2 e **da US2** — não porque a exclusão mova quantidade, e sim porque a
  `T053` exige a reversão para decidir o destino do déficit que sobra na reservada esgotada
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
2. **PARE e VALIDE**: os quatro números na tela, e o Edital sem quadro dizendo que não tem quadro
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
- `T019a` e `T019b` nasceram do `/speckit-analyze`, depois da numeração fechar. Sufixo de letra é a
  convenção do repositório para tarefa acrescentada depois — renumerar 66 itens custaria mais e
  quebraria as referências dos commits
- Comitar por tarefa ou grupo lógico; parar em qualquer checkpoint para validar
