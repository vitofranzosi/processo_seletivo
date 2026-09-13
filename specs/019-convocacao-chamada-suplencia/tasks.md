---

description: "Task list for feature implementation"
---

# Tasks: Convocação, Chamada e Suplência

**Input**: Design documents from `specs/019-convocacao-chamada-suplencia/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/convocacao.md](./contracts/convocacao.md),
[quickstart.md](./quickstart.md)

**Tests**: **obrigatórios**, e não opcionais — o Princípio V exige teste no nível certo e nomeia
autorização e concorrência entre os que pedem cobertura própria; o Princípio VI fecha a feature por
percurso do ator. Nenhuma feature anterior abriu exceção.

**Organization**: por user story, para que cada uma seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US6`)
- Caminho de arquivo exato em toda tarefa
- **Alínea** (`T030a`): tarefa acrescentada pela análise de consistência, no lugar de execução que
  lhe cabe. A numeração das demais não muda, para as referências deste arquivo seguirem válidas

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`, contrato de API
em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`.

**Esta feature cria o app `convocacao` e mexe em três features entregues.** A dependência corre num
sentido só: `convocacao` lê `ocupacao`, `classificacao` e `resultados`, e **nenhum deles importa
`convocacao`**. Se alguma tarefa levar você a importar na direção contrária, ela foi mal lida.

**Banco próprio nesta worktree**: passe `DB_NAME=ps_demo_019`. Suítes paralelas disputam
`test_processo_seletivo` e se derrubam.

**Três coisas já decididas nos artefatos, e nenhuma tarefa deve reabri-las:**

1. **A contagem é de titulares iniciais** (`R-001`), porque a exclusão sozinha não movia o
   número — 28 desistências eram necessárias. Fase 2, e antes de tudo.
2. **Vaga individual não é entidade** (`D-011`). Não crie `Vaga`.
3. **Não existe calendário de dias úteis** (`R-004`). O vencimento é informado.

---

## Phase 1: Setup

**Purpose**: o app novo e o vocabulário, antes de qualquer regra

- [ ] T001 Criar o app em `backend/processo_seletivo/convocacao/` com `__init__.py`, `apps.py`,
      `domain/__init__.py`, `application/__init__.py` e `migrations/__init__.py`
- [ ] T002 Registrar `processo_seletivo.convocacao` em `INSTALLED_APPS` em
      `backend/config/settings/base.py` — o `settings` mora em `config/`, não no pacote de domínio
- [ ] T003 [P] Escrever `backend/processo_seletivo/convocacao/domain/nomes.py` com as espécies de
      convocação — `VAGA_INICIAL`, `SUPLENCIA`, `PARA_REGULARIZAR` —, os sete desfechos, as espécies
      de atestado e **todos** os códigos de recusa do [contrato](./contracts/convocacao.md), num
      lugar só, como `ocupacao/domain/nomes.py` faz. As **formas de comunicar** não entram aqui: são
      vocabulário do publicado (T019a)
- [ ] T004 [P] Criar as pastas de teste `backend/tests/unit/convocacao/` e
      `backend/tests/integration/convocacao/` com `__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a correção da contagem, a porta, o degrau canônico e a revisão da `010`

**⚠️ CRITICAL**: nenhuma user story começa antes desta fase. A `T005` corrige a contagem que a §1.0
da spec mediu errada; construir tela ou ato sobre a contagem antiga é construir sobre número falso.

### A contagem de titulares na `016`

- [ ] T005 Estender `apurar` em `backend/processo_seletivo/ocupacao/domain/apuracao.py` para receber
      a **sequência ordenada** dos que progrediram, mais `efeitos_lidos`, e computar `ocupadas =
      |titulares habilitados − excluídos ∪ incluídos|` limitado a `efetivas` (`R-001`)
- [ ] T006 Recusar em `apurar` a determinação de titulares quando houver empate residual não julgado
      atravessando a fronteira do alvo, com o código `empate_na_fronteira_do_alvo` (`R-002`)
- [ ] T007 [P] Testar em `backend/tests/unit/ocupacao/test_titulares.py` o cenário da `SC-093`: 40
      vagas, faixa de 70, 67 habilitadas — uma desistência dá 39 e o aceite da suplente devolve 40
- [ ] T008 [P] Testar em `backend/tests/unit/ocupacao/test_titulares.py` que **nada muda** onde não
      há desfecho, preservando o comportamento que os testes da `016` já prendem
- [ ] T009 [P] Testar em `backend/tests/unit/ocupacao/test_titulares.py` que exclusão de quem não
      era titular não desconta nada, e que duas exclusões da mesma pessoa não produzem `−2`
      (`FR-278d`)
- [ ] T010 Atualizar `backend/processo_seletivo/ocupacao/application/emissao.py` para montar a
      sequência ordenada a partir de `PosicaoNaOrdem` e ler os efeitos vigentes do recorte
- [ ] T011 Rodar a suíte de `ocupacao` inteira e conferir que nenhum teste da `016` ficou verde
      por acidente com a contagem nova:
      `cd backend && uv run pytest tests/unit/ocupacao tests/integration/ocupacao`

### A porta de efeitos

- [ ] T012 Criar `EfeitoDeOcupacao` em `backend/processo_seletivo/ocupacao/models.py` conforme o
[data-model](./data-model.md) §5, com `inscricao_id` e `ato_de_origem_id` como UUID **e não FK**
- [ ] T013 Migration da tabela nova em `backend/processo_seletivo/ocupacao/migrations/`, com gatilho
      append-only no mesmo formato das duas tabelas da `016`
- [ ] T014 Acrescentar a tabela a `TABELAS_APPEND_ONLY` em
      `backend/processo_seletivo/seguranca/papeis.py` — é lá que a lista mora, e o command apenas a
      consome — e conferir por `make provisionar` que o `N de M` cresce
- [ ] T015 Escrever `backend/processo_seletivo/ocupacao/application/efeitos.py` com
      `registrar_efeito(...)`, transacional, exigindo fundamento e proveniência
- [ ] T016 Acrescentar a quinta causa de obsolescência — efeito posterior à apuração vigente — em
      `backend/processo_seletivo/ocupacao/application/selectors.py` e em
      `backend/processo_seletivo/ocupacao/domain/nomes.py`
- [ ] T017 [P] Testar em `backend/tests/unit/ocupacao/test_efeito_append_only.py` que `UPDATE` e
      `DELETE` são recusados por gatilho **e** por privilégio ausente
- [ ] T018 [P] Testar em `backend/tests/unit/ocupacao/test_obsolescencia.py` que efeito posterior
      torna a apuração vigente obsoleta, com a causa nomeada

### O degrau 15 — a forma de comunicar

- [ ] T019 Acrescentar `callForm` ao Perfil publicado em
      `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [ ] T019a [P] Declarar `PUBLICATION` e `INDIVIDUAL_MESSAGE` no vocabulário do conteúdo publicado,
      ao lado do precedente em
      `backend/processo_seletivo/publicacoes/domain/vocabulario_da_regra.py` — uma grafia só, e não
      duas em módulos diferentes
- [ ] T020 Elevar para `SCHEMA_VERSION = 15` em `backend/processo_seletivo/shared/canonical.py` e
      escrever o degrau em `backend/processo_seletivo/publicacoes/domain/elevacao.py`, com a chave
      **ausente** para todo Edital anterior
- [ ] T021 Declarar `"/profiles/*/callForm"` no catálogo de Retificação em
`backend/processo_seletivo/publicacoes/domain/colecoes.py` — **antes** da primeira emissão, pela
      lição que a `025` registrou como a que não teria conserto
- [ ] T022 [P] Exibir a forma declarada no documento publicado em
      `backend/processo_seletivo/publicacoes/infrastructure/humano.py` e em
      `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` — os dois estão em
      `infrastructure/`, e não em `domain/`
- [ ] T023 Compor a declaração na interface em `backend/processo_seletivo/interface/forms.py` e no
      passo correspondente do assistente de Edital
- [ ] T024 [P] Testar em `backend/tests/unit/publicacoes/test_elevacao.py` que o degrau 15 é
      idempotente e que Edital anterior lê ausência — e **não** um padrão
- [ ] T025 [P] Testar em `backend/tests/unit/publicacoes/test_colecoes.py` o endereçamento por
      identidade da nova coleção

### A revisão da `FR-084` da `010`

- [ ] T026 Revisar por escrito a `FR-084` em `specs/010-area-do-candidato/spec.md`, registrando a
      redação anterior e admitindo a convocação como terceira situação de mensagem (`R-008`)
- [ ] T027 [P] Atualizar `backend/tests/` onde a contagem de situações de e-mail é asseverada, para
      que a regra revisada seja a verificada
- [ ] T027a Implementar a guarda `envio_sem_revisao_da_010` em
      `backend/processo_seletivo/convocacao/application/comunicar.py` — recusa de **implantação**, e
      não de domínio: mensagem individual não existe enquanto a `FR-084` não estiver revisada
      (`FR-289`)

**Checkpoint**: contagem correta, porta pronta, forma declarável e canal autorizado — as histórias
podem começar.

---

## Phase 3: User Story 1 — Chamar para a vaga que falta e registrar a resposta (P1) 🎯 MVP

**Goal**: convocar quem a ordem indica para a vaga faltante, comunicar, e registrar o desfecho.

**Independent Test**: com um certame até a apuração, convocar três pessoas, registrar três desfechos
diferentes e ler o recorte — tudo pela interface, sem shell.

### Testes primeiro

- [ ] T028 [P] [US1] Testes de recusa da convocação em
      `backend/tests/unit/convocacao/test_recusas.py`: `apuracao_ausente`, `apuracao_obsoleta`,
      `sem_deficit`, `fora_da_faixa`, `ordem_nao_vigente`, `precedencia_na_ordem`,
      `convocacao_vigente_existente`
- [ ] T029 [P] [US1] Testes de append-only em
      `backend/tests/unit/convocacao/test_append_only.py` para `Convocacao` e
      `DesfechoDaConvocacao` — gatilho e privilégio
- [ ] T030 [P] [US1] Testes do prazo em `backend/tests/unit/convocacao/test_prazo.py`: vencimento
      informado, recusa de vencimento anterior ao envio, e prazo que não corre sem envio
- [ ] T030a [P] [US1] Teste no mesmo arquivo de que o **decurso não produz desfecho** (`FR-274`): a
      leitura mostra o vencimento passado, e nenhum desfecho nasce sem ato de quem conduz
- [ ] T031 [P] [US1] Teste de autorização em
      `backend/tests/integration/convocacao/test_autorizacao.py` — negar por padrão, com o papel
      exato de cada ator

### Implementação

- [ ] T032 [US1] Criar `Convocacao` em `backend/processo_seletivo/convocacao/models.py` conforme o
      [data-model](./data-model.md) §1, com as três metades de unicidade parcial que o `NULL` do
      `lista_id` obriga
- [ ] T033 [US1] Criar `DesfechoDaConvocacao` no mesmo arquivo, com as constraints de forma —
      inércia exige atestado, regularização exige sucessor
- [ ] T034 [US1] Criar `ComunicacaoEmitida` no mesmo arquivo, com `enviado_em` anulável e
      `resultado`
- [ ] T035 [US1] Migration das três tabelas com gatilho append-only em
      `backend/processo_seletivo/convocacao/migrations/0001_initial.py`
- [ ] T036 [US1] Acrescentar as três a `TABELAS_APPEND_ONLY` em
      `backend/processo_seletivo/seguranca/papeis.py` e conferir o `N de M`
- [ ] T037 [P] [US1] Escrever `backend/processo_seletivo/convocacao/domain/fila.py` — puro: quem é
      titular, quem é suplente, quem é chamável, e em que ordem
- [ ] T038 [P] [US1] Escrever `backend/processo_seletivo/convocacao/domain/prazo.py` — puro: a
      relação entre vencimento informado, envio e decurso
- [ ] T039 [US1] Escrever `backend/processo_seletivo/convocacao/application/convocar.py` com as sete
      recusas, autorização, idempotência e auditoria
- [ ] T040 [US1] Escrever `backend/processo_seletivo/convocacao/application/desfechar.py` com os
      sete desfechos, um por convocação, chamando `ocupacao.application.efeitos` para excluir ou
      incluir
- [ ] T041 [US1] Escrever `backend/processo_seletivo/convocacao/application/comunicar.py` — emissão
      na forma declarada, registro do resultado, e falha que não apaga o ato
- [ ] T041a [US1] Compor o conteúdo da mensagem com **o que fazer, o prazo e o canal de
      atendimento**, e nada da inscrição além do necessário para identificar a chamada (`FR-290`),
      com teste em `backend/tests/unit/convocacao/test_mensagem.py`
- [ ] T042 [US1] Escrever `backend/processo_seletivo/convocacao/application/selectors.py` com a
      leitura do recorte e o estado *"convocado, prazo não iniciado"* (`R-009`)
- [ ] T043 [US1] Rotas de gestão em `backend/processo_seletivo/interface/views.py`, registradas em
      `backend/processo_seletivo/interface/urls.py`, conforme o
      [contrato](./contracts/convocacao.md) §1
- [ ] T044 [US1] Tela `backend/processo_seletivo/interface/templates/interface/convocacao.html` — os
      quatro números da `016` mais convocados, respondidos, faltantes e esgotamento; o prazo como
      data e hora locais, dizendo de que referência corre (`UX-038`)
- [ ] T045 [US1] Confirmação antes de cada ação irreversível, com a mensagem de sucesso nomeando **o
      ato praticado** (`UX-036`) — foi o defeito `E2E16-004` da `016`
- [ ] T046 [P] [US1] Testes de interface em `backend/tests/interface/test_convocacao.py`: os estados
      distintos, a confirmação, e a ausência de *"recebido em"*
- [ ] T046a [P] [US1] Teste no mesmo arquivo de que a tela **não afirma número de ocupação diferente
      do apurado** (`FR-278a`): entre o desfecho e a emissão seguinte aparece o apurado, com a
      obsolescência declarada
- [ ] T047 [P] [US1] Teste de integração em
      `backend/tests/integration/convocacao/test_ciclo_do_77.py` cobrindo a `SC-085` até o desfecho
- [ ] T047a [P] [US1] Teste em `backend/tests/integration/convocacao/test_ato_praticado.py` de que
      **Retificação, nova apuração e nova faixa não desfazem convocação praticada** (`FR-282`) — as
      três, e não uma delas

**Checkpoint**: US1 funciona sozinha — convoca, comunica, desfecha e mostra.

---

## Phase 4: User Story 2 — Chamar o suplente quando a vaga vaga (P1)

**Goal**: a vaga liberada é chamada para o próximo do **mesmo** recorte, até o teto publicado.

**Independent Test**: liberar vaga reservada e verificar que o chamado é da mesma lista; esgotar o
teto e ler a recusa.

- [ ] T048 [P] [US2] Teste em `backend/tests/unit/convocacao/test_fila.py` de que a suplência não
      atravessa recorte (`SC-086`)
- [ ] T049 [P] [US2] Teste em `backend/tests/unit/convocacao/test_fila.py` do esgotamento da lista
      alcançada, com `lista_alcancada_esgotada`
- [ ] T050 [P] [US2] Teste em `backend/tests/unit/convocacao/test_fila.py` de que a Inscrição
      reabilitada por deferimento fica em primeiro e bloqueia quem está abaixo (`FR-292b`,
      `reabilitado_a_frente`)
- [ ] T050a [P] [US2] Teste em `backend/tests/integration/convocacao/test_ato_praticado.py` de que
      o deferimento **não desfaz convocação praticada e não cancela matrícula efetivada**
      (`FR-292a`) — é a metade da `D-007` que nenhuma outra tarefa cobre
- [ ] T051 [US2] Implementar em `domain/fila.py` o próximo chamável do recorte, respeitando o teto
      de suplentes que a faixa da `014` alcançou
- [ ] T052 [US2] Implementar em `application/convocar.py` a espécie `SUPLENCIA`, recusando
      atravessar recorte
- [ ] T053 [US2] Implementar a precedência do reabilitado em `domain/fila.py` e a recusa
      correspondente
- [ ] T054 [US2] Mostrar na tela o esgotamento e que a faixa seguinte é ato da `014` — sem oferecer
      botão que esta feature não pode cumprir
- [ ] T055 [P] [US2] Teste de integração em
      `backend/tests/integration/convocacao/test_suplencia.py`: desistência em vaga reservada →
      chamada na mesma lista → apuração nova em 40

**Checkpoint**: a primeira desistência não para mais o certame.

---

## Phase 5: User Story 3 — Convocar para regularizar o indeferimento (P2)

**Goal**: quem teve a matrícula indeferida é convocado, na ordem, para corrigir — e a regularização
sucede o Resultado.

**Independent Test**: com três indeferidos e vagas sobrando, convocar o primeiro, registrar a
regularização e ver a vaga ocupada sem reabrir a ordem.

### A travessia na `018`

- [ ] T056 [US3] Acrescentar `REGULARIZACAO` a `ResultadoEtapa.Origem` em
      `backend/processo_seletivo/resultados/models.py`
- [ ] T057 [US3] Estender `ck_resultado_origem` com a **quinta** linha legítima — origem nova,
      avaliação nula, anterior presente, fonte jurídica própria (`R-005`) — sem afrouxar as quatro
      existentes
- [ ] T058 [US3] Estender o gatilho que confere o Resultado contra a fonte, com o ramo da origem
      nova
- [ ] T059 [US3] Migration em `backend/processo_seletivo/resultados/migrations/` — constraint e
      gatilho, nenhuma migration reescrita
- [ ] T060 [P] [US3] Teste em `backend/tests/unit/resultados/test_origem_regularizacao.py` de que
      sucessor sem fonte jurídica continua recusado, e de que as quatro linhas antigas seguem
      válidas

### A convocação para regularizar

- [ ] T061 [P] [US3] Teste em `backend/tests/unit/convocacao/test_regularizacao.py` de que a
      convocação respeita a ordem de classificação e registra o fundamento do 77 (8.2)
- [ ] T062 [US3] Implementar a espécie `PARA_REGULARIZAR` em `application/convocar.py`, admitida só
      quando as matrículas deferidas do recorte são menos que as vagas — o desfecho homônimo é outra
      coisa, e os nomes não se confundem
- [ ] T063 [US3] Implementar o desfecho de regularização em `application/desfechar.py`: grava o
      Resultado sucessor e **inclui** pela porta, na mesma transação
- [ ] T064 [US3] Rota e controle na tela para convocar quem foi indeferido, com o fundamento visível
- [ ] T065 [P] [US3] Teste de integração em
      `backend/tests/integration/convocacao/test_regularizacao.py`: o indeferido continua existindo
      sucedido, a apuração seguinte o conta, e a ordem não é reaberta

**Checkpoint**: a via administrativa do 77, do 58 e do 59 funciona sem recurso.

---

## Phase 6: User Story 6 — O candidato vê que foi convocado, e até quando (P2)

**Goal**: a chamada é legível pelo canal do ator, sem depender de e-mail.

**Independent Test**: convocar e ler a convocação na área do candidato, com prazo visível.

- [ ] T066 [P] [US6] Teste em `backend/tests/interface/test_portal_convocacao.py` de que a tela
      distingue *"não há convocação"* de *"você não foi chamado"*
- [ ] T067 [P] [US6] Teste no mesmo arquivo de que a tela escreve *"enviado em"* e nunca
      *"recebido em"* (`UX-039`)
- [ ] T068 [US6] Selector da convocação do titular em
      `backend/processo_seletivo/portal/views.py`, restrito à própria inscrição
- [ ] T069 [US6] Tela `backend/processo_seletivo/portal/templates/portal/convocacao.html` com a
      chamada, o que fazer, o prazo e o canal de atendimento
- [ ] T070 [US6] Registrar o acesso autenticado na trilha **sem** mover o relógio (`FR-288b`)
- [ ] T071 [P] [US6] Verificar a tela em 375 px, e não deixar isso para o fim como a `013` deixou

**Checkpoint**: a pessoa convocada não depende de caixa de entrada para saber.

---

## Phase 7: User Story 4 — Reclassificar quem não compareceu (P3)

**Goal**: o ausente vai para o fim da fila, e volta a ser chamável depois do esgotamento.

**Independent Test**: reclassificar um convocado, esgotar a fila e verificar que ele volta a ser
chamável — nessa ordem, e não antes.

- [ ] T072 [P] [US4] Teste em `backend/tests/unit/convocacao/test_reclassificacao.py` de que o
      reclassificado passa a constar depois do último suplente
- [ ] T073 [P] [US4] Teste no mesmo arquivo da recusa `reclassificado_antes_do_esgotamento`
- [ ] T074 [P] [US4] Teste no mesmo arquivo de que a reclassificação **não** afirma perda de
      habilitação (`D-008`)
- [ ] T075 [US4] Implementar o desfecho de reclassificação em `application/desfechar.py`: exclui
      pela porta e move na fila
- [ ] T076 [US4] Implementar a posição do reclassificado em `domain/fila.py`
- [ ] T077 [US4] Mostrar a reclassificação no histórico com o fundamento e a posição nova

**Checkpoint**: o 69/2026 deixa de precisar de planilha paralela.

---

## Phase 8: User Story 5 — Registrar a desistência que aconteceu fora daqui (P3)

**Goal**: quem tem competência atesta a inércia; a matrícula é cancelada e o próximo fica chamável.

**Independent Test**: atestar a inércia de um matriculado e verificar que o cancelamento registra o
atestante, não o relógio.

- [ ] T078 [P] [US5] Teste em `backend/tests/unit/convocacao/test_atestado.py` de que inércia sem
      atestado é recusada por constraint, e não apenas por código (`atestado_obrigatorio`)
- [ ] T079 [P] [US5] Teste no mesmo arquivo de que o decurso do prazo **não** cancela nada sozinho
- [ ] T080 [US5] Criar `AtestadoDeFatoExterno` em `backend/processo_seletivo/convocacao/models.py`
      conforme o [data-model](./data-model.md) §3
- [ ] T081 [US5] Migration da tabela em `backend/processo_seletivo/convocacao/migrations/` e entrada
      em `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`
- [ ] T082 [US5] Escrever `backend/processo_seletivo/convocacao/application/atestar.py` — quem
      atestou, o que concluiu, e a referência do prazo copiada do conteúdo publicado
- [ ] T083 [US5] Implementar o desfecho de cancelamento por inércia em `application/desfechar.py`,
      **distinto** do não atendimento à convocação (`D-011`)
- [ ] T084 [US5] Rota e controle do atestado conforme o [contrato](./contracts/convocacao.md) §1
- [ ] T085 [P] [US5] Teste de integração em
      `backend/tests/integration/convocacao/test_inercia.py`: atestado → cancelamento → suplente
      chamável

**Checkpoint**: o aluno que desaparece não trava mais o certame.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T086 [P] Varredura de vocabulário em
      `backend/tests/test_vocabulario_da_convocacao.py`: esta feature **não** afirma contagem de
      ocupação (`UX-035`, `SC-092`), não diz *"recebido em"*, *"lido em"* nem *"entregue em"*
      (`UX-039`), e não diz *"direito à vaga"* (`FR-292c`)
- [ ] T087 [P] Conferir que `backend/tests/test_vocabulario_da_ocupacao.py` continua verde — a `016`
      segue proibida de falar de convocação, e a fronteira vale nos dois sentidos
- [ ] T088 [P] Prova de import em `backend/tests/test_dependencia_da_convocacao.py`: nenhum módulo
      de `ocupacao`, `classificacao` ou `resultados` importa `convocacao`
- [ ] T088a [P] Teste no mesmo arquivo de que **nenhum caminho desta feature move quantidade entre
      recortes** (`FR-270`) — mover quantidade é a reversão da `016`, e prova de texto não a cobre
- [ ] T088b [P] Medir em `backend/tests/performance/test_convocacao.py` que o histórico responde
      **por conjunto** (`SC-088`): a contagem de consultas não cresce com o número de convocações do
      recorte
- [ ] T089 [P] Medir a `SC-090` em `backend/tests/performance/test_convocacao.py` — 1.000
      participantes, teto de 3 s, e contagem de consultas que **não** cresce com o número de
      convocações
- [ ] T090 [P] Histórico com proveniência em
      `backend/processo_seletivo/interface/templates/interface/convocacao_historico.html` (`FR-294`)
- [ ] T091 [P] Trilha de auditoria do Edital listando os atos desta feature em linguagem humana
      (`FR-296`)
- [ ] T092 Matriz de rastreabilidade em `specs/019-convocacao-chamada-suplencia/rastreabilidade.md`
      — `FR-264`–`FR-296`, `SC-085`–`SC-094`, `UX-035`–`UX-039`, cada um com o teste que o prende
- [ ] T093 Percurso conduzido pela interface seguindo o [quickstart](./quickstart.md), com relatório
      em `doc/e2e/019-convocacao/relatorio.md`
- [ ] T094 Atualizar a tabela de incrementos do `README.md` com a `019` e a contagem nova da suíte,
      e o `N de M` do provisionamento em `README.md` e `AGENTS.md` — o resíduo que reapareceu cinco
      vezes
- [ ] T095 `cd backend && make lint check test-pg` verde, e `uv run pytest
      tests/test_citacoes_de_requisito.py` antes de empurrar qualquer artefato

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 Setup
   └─▶ Phase 2 Foundational  ⚠️ bloqueia tudo
          ├─▶ Phase 3 US1 (P1)  🎯 MVP
          │      └─▶ Phase 4 US2 (P1)      precisa do desfecho para haver vaga liberada
          ├─▶ Phase 5 US3 (P2)             precisa da porta e da convocação
          ├─▶ Phase 6 US6 (P2)             precisa da convocação existir
          ├─▶ Phase 7 US4 (P3)             precisa da fila da US2
          └─▶ Phase 8 US5 (P3)             precisa do desfecho
                 └─▶ Phase 9 Polish
```

### User Story Dependencies

- **US1** depende só da Fase 2 — é o MVP.
- **US2** depende da US1: sem desfecho não há vaga liberada.
- **US3** depende da US1 e da travessia na `018` (`T056`–`T060`).
- **US4** depende da fila da US2.
- **US5** depende da US1.
- **US6** depende da US1, e é independente das outras.

### Parallel Opportunities

- **Fase 2**: os três blocos — contagem (`T005`–`T011`), porta (`T012`–`T018`) e degrau
  (`T019`–`T025`) — tocam arquivos distintos e correm em paralelo. A revisão da `010`
  (`T026`–`T027`) também.
- **Fase 3**: `T028`–`T031` em paralelo; `T037` e `T038` em paralelo depois dos modelos.
- **Fases 5 a 8**: as quatro histórias correm em paralelo depois da US2, em arquivos distintos —
  exceto `application/desfechar.py`, tocado por US3, US4 e US5. Sequencie as três tarefas que o
  editam (`T063`, `T075`, `T083`).
- **Fase 9**: tudo em paralelo, menos `T093` a `T095`.

## Parallel Example: Phase 2

```
T005 ─ T006 ─ T010 ─ T011      (contagem, sequencial entre si)
T007 · T008 · T009             (testes da contagem, em paralelo)
T012 ─ T013 ─ T014 ─ T015 ─ T016   (a porta)
T017 · T018                    (testes da porta)
T019 ─ T020 ─ T021 ─ T023      (o degrau)
T022 · T024 · T025             (documento e testes do degrau)
T026 ─ T027                    (a revisão da 010)
```

## Implementation Strategy

**MVP é a US1 mais a Fase 2.** Ela entrega o que hoje mora em planilha: chamar, comunicar, registrar
o que a pessoa respondeu, e ver o recorte. Nada além dela é necessário para o 77/2026 começar a ser
conduzido pelo sistema — mas a US2 é o que impede a primeira desistência de parar tudo, e por isso
as duas são P1.

**A ordem de entrega recomendada:** Fase 2 → US1 → US2 (fecha a `SC-085` e o ciclo do 77) → US3 →
US6 → US4 → US5 → Polish. As fases 5 a 8 podem ser distribuídas entre pessoas depois da US2.

**O que não fazer, mesmo parecendo atalho:** implementar a tela antes da `T005`. A contagem antiga
produz número plausível e errado, e plausível é o que faz passar.
