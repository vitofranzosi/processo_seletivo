---

description: "Task list — 037 · Quatro becos que o sistema já conhece"
---

# Tasks: Quatro becos que o sistema já conhece

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim, e são obrigatórios.** Três das quatro histórias são essencialmente **prosa**, e
prosa é o que muda sem que nada quebre. Requisito sem linha na matriz é requisito que ninguém sabe se
entrou.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: arquivos diferentes, nenhuma dependência aberta. **Se uma tarefa ganhar arquivo depois, o
  `[P]` sai** — foi assim que a regra se quebrou na `035`.
- **[US1] [US2] [US3] [US4]**: a história. A fase 1 e a de polimento não têm.
- **NOVO / EXISTENTE**: onde diz existente, **acrescente ao fim; nunca reescreva**. A `030`
  sobrescreveu `test_round_trip_do_rascunho.py` e oito regressões sumiram sem a suíte ficar vermelha.
  **Aqui isso é mais perigoso do que de costume**: três histórias alteram arquivos de teste que já
  existem e que têm casos vizinhos que devem permanecer.

---

## Os cinco portões

1. **`T002` roda ANTES de qualquer edição.** E aqui ela tem alvo nomeado: os **quatro** casos que
   mudam de sentido, listados um a um em `research.md` `R-4`, com **o que cada um afirma hoje,
   citado**. Dois defendem o defeito por escrito.

2. **Esta feature NÃO tem migration.** Nenhuma entidade, nenhuma tabela. O total do `make preparar`
   continua **`N de 32`** — a 32ª veio da `036`, que acabou de entrar na `main`. **Se a saída disser
   31, a worktree está atrás da `main`**, e isso é ambiente, não defeito do diff.

   > **Medido, e a atribuição acima está errada.** A `036` **não** estava na `main` quando esta
   > implementação começou: ela entrou em `0c96283`, depois da base `23bf70e`, e é ela que traz a
   > **33ª** tabela (`recursos/0002_ato_de_instrucao`). Os números certos são **32 sem a `036`** e
   > **33 com ela**, e os dois foram medidos. A conferência que este portão quer continua valendo
   > com o total corrigido: integrada a `main`, o `make preparar` fecha em `33 de 33`, que é o mesmo
   > que a `main` sozinha fecha — nenhuma tabela nasceu aqui.

3. **A `US2` começa por um PERCURSO, e não por código.** A `T011` **decide** se o `ACH-02` ainda tem
   o que fechar. As duas saídas estão nomeadas na tarefa, e uma delas **cancela a `T015`**.

4. **A `T010` é contraprova OBRIGATÓRIA**, e é o que separa esta feature de um beco novo: o marco
   **sem regra** recebe o caminho **da regra**; o marco **com regra e sem ordem** continua recebendo
   o caminho **da classificação**. Se os dois oferecerem o mesmo, a feature abriu o beco que existe
   para fechar — **mesmo com o link aparecendo corretamente**.

5. **`T031` reconta os casos alterados, caso a caso.** `R-4` prevê **quatro**; a `034` previu oito e
   entregou doze. Um teste pode manter o número de asserções e trocar o que afirma.

---

## Phase 1: Setup e medição do "antes"

- [x] T001 Preparar a worktree: copiar `backend/.env` do checkout principal (**EXISTENTE lá, ausente aqui** — é gitignorado), trocar `DB_NAME` e `POSTGRES_DB` por um nome próprio, rodar `uv sync --extra dev` e `make preparar` em `backend/`, conferindo que a saída termina em **`N de 32`** com N diferente de zero. **32, e não 31**: a `036` acrescentou a 32ª tabela append-only e já está na `main`. Ver 31 significa worktree desatualizada
- [x] T002 Medir e gravar o "antes" em `specs/037-quatro-becos-conhecidos/antes-dos-quatro-becos.md` (**NOVO**): a contagem da suíte (`make test-pg`) e, **citado**, o que cada um dos **quatro** casos de `research.md` `R-4` afirma hoje — os dois de `tests/unit/editais/test_calendario.py` e os dois de `tests/unit/editais/test_cronograma_vencido.py`. Registre também a contagem de `test_destinos_do_edital.py` (10), `test_corte.py` (13) e `test_selo_do_cronograma.py` (11), que são os vizinhos que **devem permanecer**. **Esta tarefa roda antes de qualquer edição de código**
- [x] T003 Confirmar por varredura, em `specs/037-quatro-becos-conhecidos/antes-dos-quatro-becos.md` (**EXISTENTE**, criado em T002), as quatro premissas de que a feature depende: que a recusa do marco sem regra sai como **conflito e não como ausência** (`R-1`); que a pendência de Perfil **já é corrigível e já leva à etapa** (`R-5`); que `frase_da_recusa` existe e é pública (`R-6`); e que a lista de Etapas do cartão do marco **não carrega o peso** (`R-8`). É o "confirme, não assuma" que a `035` provou valer

**Checkpoint**: o "antes" está gravado, com os quatro casos citados, e as quatro premissas conferidas.

---

## Phase 2: Foundational — **não existe nesta feature**

**E vale dizer por quê.** As quatro histórias nascem de achados reunidos por **causa comum**, e não
por dependência técnica: não há entidade a criar, esquema a preparar nem mecanismo que as anteceda.
Inventar uma fase 2 aqui seria fabricar bloqueio.

**Cuidado com o que isso NÃO significa.** As quatro são independentes **na entrega** — cada uma
fecha sozinha. Não são independentes **na edição**: a `US1`, a `US2` e a `US4` tocam o mesmo
`backend/processo_seletivo/interface/views.py`. **Por isso nenhuma tarefa desta feature leva `[P]`.**

---

## Phase 3: US1 — O caminho até o corte deixa de sumir (P1) 🎯 MVP

**Goal**: o destino do corte é oferecido em todo marco classificatório, e o caminho que a recusa
oferece passa a ser o da coisa que falta.

**Independent Test**: compor um marco sem regra de corte, publicar, e conferir pela tela do Edital
que o destino aparece e que abri-lo leva à regra.

- [x] T004 [US1] Oferecer o destino do corte **sem condicioná-lo à regra** em `backend/processo_seletivo/interface/views.py` (**EXISTENTE** — a montagem dos destinos do marco), `FR-538`. A condição que sai é `if marco.get("cutRule")`; o que **não** sai é a condição de alcance do ator, que é outra coisa e é a garantia da `033` (`FR-540`)
- [x] T005 [US1] Escolher o **caminho conforme a recusa** na view do corte, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**, o mesmo arquivo de T004), `FR-539a` e [contracts/o-caminho-da-recusa.md](contracts/o-caminho-da-recusa.md). São **três** recusas passando pelo mesmo bloco: ordem ausente e ordem obsoleta continuam indo para a classificação; **marco sem regra vai para a Retificação**, que é onde a regra de um Edital publicado se declara. A frase de cada recusa **não muda** — ela nasce no domínio e tem código próprio
- [x] T006 [US1] Condicionar **esse** caminho ao que o ator alcança, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**, o mesmo arquivo de T005), `FR-539b`. Quem alcança a Retificação recebe o caminho; **quem não alcança recebe a frase que diz a quem pedir**, pelo mesmo mecanismo da `FR-543`. Sem isto, a correção de um beco abre o beco que a `033` fechou — e este é o segundo lugar da feature onde o mesmo erro cabe
- [x] T007 [US1] Imprimir o caminho que a view escolheu, em `backend/processo_seletivo/interface/templates/interface/corte.html` (**EXISTENTE**). O template hoje anexa um caminho fixo; ele passa a imprimir o que recebeu. **Emende o comentário do bloco**, que registra a razão do caminho único e cita o `ACH-40` — a razão continua válida, o que mudou é que agora há três recusas alcançáveis e não duas. **Não apague a frase**
- [x] T008 [US1] Prender o destino em `backend/tests/interface/test_destinos_do_edital.py` (**EXISTENTE** — acrescente ao fim; os 10 casos de hoje permanecem): o destino **aparece** no marco sem regra; **continua aparecendo** no marco com regra; e **não aparece** para quem não alcança a classificação (`FR-538`, `FR-540`)
- [x] T009 [US1] Prender a tela em `backend/tests/interface/test_corte.py` (**EXISTENTE** — acrescente ao fim; os 13 casos de hoje permanecem): abrir o corte num marco sem regra **mostra a recusa** e não devolve página inexistente — a recusa é conflito, não ausência (`FR-539`). **Afirme a frase literalmente**, e não só que alguma recusa apareceu: a `FR-539` é uma proibição de reescrever, e sem asserção literal uma reescrita bem-intencionada na T005 ou na T007 passaria por todas as tarefas sem ser notada
- [x] T010 [US1] **CONTRAPROVA OBRIGATÓRIA** — os dois caminhos lado a lado, em `backend/tests/interface/test_corte.py` (**EXISTENTE**, o mesmo arquivo de T009): marco **sem regra** recebe o caminho **da regra**; marco **com regra e sem ordem** recebe o caminho **da classificação**. **Se os dois forem iguais, a `FR-539a` não foi cumprida** — e a feature abriu o beco que existe para fechar, ainda que o link do T004 apareça certo. Acrescente o caso do ator **que não alcança a Retificação**: ele recebe a **frase**, e não o caminho (`FR-539b`). E acrescente o **marco que ordena por sorteio**: ele não corta e não enumera Etapa, o destino é oferecido do mesmo modo, e a tela diz que este marco não corta — **registre se a prosa serve ao caso ou se precisa de palavra própria**, que é o que o caso de borda da spec deixou em aberto

**Checkpoint**: **este é o MVP.** A parte (c) da 13.1 fecha, e sem beco novo no fim dela.

---

## Phase 4: US2 — Quem esbarra num bloqueio passa a saber a quem pedir (P1)

**Goal**: quem esbarra **e ainda não sabe** lê a quem pedir, pelo mecanismo único que já existe — e
quem já sabe não lê nada, porque o caminho está ali.

**Independent Test**: abrir a tela de um Edital publicado como gestor **sem** a permissão de
retificar e ler a ação e a permissão; abri-la **com** a permissão e conferir que o aviso **cala** e a
ação está na lista. O segundo bloqueio entra no teste **só se** a `T011` apontar que há o que fechar.

- [x] T011 [US2] **PERCURSO QUE DECIDE, e ele vem antes do código** (`FR-542b`). Percorra o cenário 2 passo 1 de `specs/037-quatro-becos-conhecidos/quickstart.md` (**EXISTENTE**) com o ator exato da auditoria, e registre o desfecho em `specs/037-quatro-becos-conhecidos/achado-do-ach-02.md` (**NOVO**) — **é esta tarefa que satisfaz a `SC-195`**, e ela a satisfaz nas duas saídas, porque o que o critério exige é o desfecho escrito, e não um desfecho em particular. **Duas saídas, e as duas são legítimas**: (a) **alguma permissão impede** o gestor → a `T015` é executada; (b) **nada o impede**, e o caminho até os Perfis já está na tela → **o `ACH-02` fecha aqui, registrando isso, e a `T015` NÃO é executada**. Escrever frase para problema que não existe é pior do que não escrever
- [x] T012 [US2] Derivar **uma vez** se o ator pode retificar, em `backend/processo_seletivo/interface/acoes.py` (**EXISTENTE**) e `backend/processo_seletivo/interface/views.py` (**EXISTENTE**), `FR-541a` e `FR-544`. **Leia primeiro `acoes.py`**: o cartão já responde a essa pergunta para decidir se oferece a ação de Retificar — `edital.status == "PUBLICADO" and ator.can("retificacao:elaborar")` —, e **quem pode já recebe o caminho**. O aviso passa a depender da **mesma** derivação, e não de uma segunda; duas respostas para a mesma pergunta divergem na primeira mudança
- [x] T013 [US2] Ampliar o mecanismo único para produzir a **forma cheia**, em `backend/processo_seletivo/seguranca/application/authorization.py` (**EXISTENTE**), `FR-543c` e `FR-543d`. **Medido: ele não a produz hoje** — termina em *"Peça a alguém com a permissão de X."*, sem a oração do ato, e sem esta tarefa a `FR-543` e a `FR-543a` se contradizem. **Duas situações de fala**: a de hoje **recusa uma operação tentada** e abre com *"Esta operação depende de…"*; a desta feature **avisa numa tela onde ninguém tentou nada**, e dizer "esta operação" ao lado de *"Conteúdo imutável"* nomeia uma operação que não houve. As duas compartilham a construção do **a quem pedir**. **Medido também: nenhum teste afirma o texto deste helper hoje** — crie `backend/tests/unit/seguranca/test_frase_da_recusa.py` (**NOVO**) prendendo as duas formas, inclusive a contração que o português exige e o caso de duas bases
- [x] T014 [US2] Conduzir no aviso de conteúdo imutável, em `backend/processo_seletivo/interface/templates/interface/detalhe.html` (**EXISTENTE**), `FR-541`, `FR-541b` e `FR-541c`. A frase sai de `frase_da_recusa`, em `backend/processo_seletivo/seguranca/application/authorization.py` — **não redija o texto à mão** (`FR-543`), e use a formulação **cheia** (`FR-543a`). **O aviso cala quando a ação já está oferecida ali**: dizer *"peça a alguém"* ao lado do botão que a pessoa pode clicar ensina a desconfiar da tela. **E não transforme Retificar em botão desabilitado com motivo**: a lista de navegação não oferece destino que o ator não abre, e desfazer isso desfaria a regra da `007` e da `033`
- [x] T015 [US2] **SÓ SE a `T011` apontar a saída (a)** — levar o ator à montagem das pendências, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**, o mesmo arquivo de T014) e exibir a condução em `backend/processo_seletivo/interface/templates/interface/_pendencias.html` (**EXISTENTE**), `FR-542` e `FR-542a`. **Este parcial é incluído por OITO telas** — `compor_identificacao`, `compor_perfis`, `compor_etapas`, `compor_cronograma`, `compor_inscricao`, `compor_conteudo`, `compor_anexos` e `compor_revisao` —, e a mudança alcança as oito de uma vez. Dimensione a conferência para isso, e não para uma. **A mensagem normativa não é tocada**: ela descreve o defeito do conteúdo, é lida por mais de uma superfície e não conhece quem está olhando — a condução nasce **onde a tela exibe o achado**. **É assinatura a mudar, com chamadores a encontrar** — não é uma frase a mais. O que a tela **já diz** (o que falta, e o caminho até a etapa) **permanece intocado**
- [x] T016 [US2] Prender as conduções em `backend/tests/interface/test_conducao_dos_bloqueios.py` (**NOVO**): o Edital publicado nomeia a ação e a permissão; quem **pode** recebe o caminho e **não** a frase de pedir; e a pendência de Perfil **continua** dizendo o que falta e levando à etapa (`FR-541`, `FR-542`, `FR-544`)
- [x] T017 [US2] Conferir que a gramática das recusas não se partiu, em `backend/tests/test_gramatica_das_portas.py` (**EXISTENTE**, o guardião que já existe): a formulação continua única, e as frases novas passam por ela (`FR-543`, `FR-543a`). Confira também que **nenhuma condução nomeia pessoa** — só a permissão, sem fila e sem designação (`FR-543b`)

**Checkpoint**: `ACH-30` fechado; `ACH-02` fechado **ou registrado como já fechado**.

---

## Phase 5: US3 — Um período em curso deixa de ser chamado de vencido (P2)

**Goal**: o Edital que abre inscrições no dia da publicação conclui a etapa do Cronograma.

**Independent Test**: compor um período em curso e conferir que o selo conclui e a conferência cala.

- [x] T018 [US3] Corrigir a régua **e a escolha do instante no MESMO ato**, em `backend/processo_seletivo/editais/domain/calendario.py` (**EXISTENTE**), `FR-545`, `FR-546` e `FR-546a`, conforme [contracts/a-regua-do-vencido.md](contracts/a-regua-do-vencido.md). **Havendo término, vence quem terminou; não havendo, vence quem começou.** Trocar por "o término passou" silenciaria o Evento pontual, e o módulo já registra por escrito que *"ausência não vence"*. **Separar as duas funções em dois atos faz o módulo discordar de si mesmo** — que é a razão de ele existir, e é o que a `FR-547` prende: a régua continua **única**, e as duas superfícies continuam derivando dela em vez de cada uma responder por conta. **Não toque** na função homônima de `backend/processo_seletivo/interface/static/interface/rascunho.js`: ela é sobre validade de rascunho no navegador e não consulta esta régua
- [x] T019 [US3] Atualizar os **dois** casos nomeados em `backend/tests/unit/editais/test_calendario.py` (**EXISTENTE** — altere **só** `test_evento_em_curso_vence_pelo_inicio` e `test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro`). **Renomeie os dois**: um caso chamado *"vence pelo início"* que passa a afirmar *"não vence"* é a forma mais discreta de a suíte mentir. **Os outros doze casos permanecem**, e são a contraprova de que a régua não se afrouxou
- [x] T020 [US3] Atualizar os **dois** casos nomeados em `backend/tests/unit/editais/test_cronograma_vencido.py` (**EXISTENTE** — altere **só** `test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro` e `test_periodo_em_curso_adverte_mas_nao_impede`). O segundo é o mais perigoso: a docstring dele diz *"O Edital que abre inscrições e é publicado no mesmo dia é legítimo"* — **descreve a intenção certa e prende o comportamento errado** —, e o nome fica falso depois da correção. **Renomear é obrigatório.** Confira, no mesmo arquivo e **sem alterar os casos**, que o vencido continua sendo **advertência e nunca recusa** (`FR-548`) e que a frase continua nomeando o **término** quando os dois instantes passaram (`FR-549`). O impedimento por **período encerrado** é outra regra e **não é tocado**
- [x] T021 [US3] Conferir o selo da etapa em `backend/tests/interface/test_selo_do_cronograma.py` (**EXISTENTE**, os 11 casos): o período em curso **conclui**, e os casos do Evento passado e do Cronograma inteiro no futuro **não mudam de sentido** (`SC-190`)
- [x] T022 [US3] Prender a concordância com o canal do candidato em `backend/tests/integration/portal/test_cronograma_publico.py` (**EXISTENTE** — acrescente ao fim): o **mesmo** Evento em curso é *acontecendo agora* nos dois lados (`FR-549a`, `SC-191`). **A concordância é de desfecho, e não de código**: as duas superfícies derivam a situação por conta própria, e unificá-las **não é escopo**

**Checkpoint**: a etapa que era impossível de concluir conclui, e as duas superfícies param de discordar.

---

## Phase 6: US4 — O rótulo do peso para de mentir (P3)

**Goal**: o rótulo declara a condição, e a contradição aparece no momento em que a Etapa é enumerada.

**Independent Test**: declarar uma Etapa sem peso, enumerá-la num marco, e ver o cartão dizê-lo ali.

- [x] T023 [US4] Declarar a condição no rótulo, em `backend/processo_seletivo/interface/templates/interface/_etapa.html` (**EXISTENTE**), `FR-550`. O vazio é legítimo **até que um marco enumere esta Etapa** — e é essa ressalva que falta, não a palavra "opcional"
- [x] T024 [US4] Levar **se a Etapa tem peso** à lista que o cartão já recebe, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**), `FR-551`. **Derive num lugar só**: a lista é montada por um helper e consumida em **quatro** pontos do arquivo; acrescentar o campo no helper cobre os quatro, e acrescentá-lo em três deixa o cartão mudo numa das rotas — que é a falha que a `034` descreveu por inteiro. **Campo, e não controle** (`FR-551a`)
- [x] T025 [US4] Nomear as Etapas enumeradas sem peso, em `backend/processo_seletivo/interface/templates/interface/_marco.html` (**EXISTENTE**), `FR-551`. O cartão **já se reconstrói a cada mudança da seleção**, e é esse ciclo que dá o *"no momento em que enumera"* — não há tela a inventar. **A frase é aviso derivado do estado, e não ajuda instrucional** (`FR-554a`): ela existe só enquanto houver Etapa enumerada sem peso, some quando o peso é declarado, e não ensina a preencher nada — é por isso que ela não desrespeita a `FR-554`, e escrever a distinção aqui é o que impede a conferência da `T033` de a acusar. A frase nova **não pode contradizer** a que já está lá: *"O peso de cada uma é o que ela já publica; aqui se escolhe quais entram."*, nem as duas que cobram o peso na conferência e no domínio
- [x] T026 [US4] Prender em `backend/tests/interface/test_peso_no_momento_de_enumerar.py` (**NOVO**): o rótulo declara a condição; enumerar uma Etapa sem peso **nomeia a Etapa**; declarar o peso **some com a cobrança**; Etapa sem peso que **nenhum** marco enumera **não é acusada**; e marco que **ordena por sorteio** e não enumera nada **não acusa** (`FR-550`, `FR-551`). **Exercite as QUATRO rotas** que consomem a lista da `T024`, uma a uma — inclusive o **fragmento recomposto**, que é o ciclo que dá o *"no momento em que enumera"*. Um teste que passe só pela composição fica verde com o cartão mudo justamente na rota que importa; é a conta que a `034` pagou para aprender

**Checkpoint**: a contradição da etapa 9 passa a aparecer na etapa 5.

---

## Phase 7: Polimento e conferência

- [x] T027 Percorrer o **cenário 1** de `specs/037-quatro-becos-conhecidos/quickstart.md` (**EXISTENTE**) pela interface — **inclusive a contraprova dos dois caminhos e o passo de quem não alcança**. É o `SC-188`
- [x] T028 Percorrer o **cenário 2** de `specs/037-quatro-becos-conhecidos/quickstart.md` (**EXISTENTE**), lembrando que o passo 1 dele já foi percorrido na `T011` e que o registro daquela tarefa é a entrada deste. É o `SC-189`
- [x] T029 Percorrer o **cenário 3** de `specs/037-quatro-becos-conhecidos/quickstart.md` (**EXISTENTE**), **inclusive as duas contraprovas da régua** — o Evento pontual passado, que **continua** vencido, e o Evento com os dois instantes passados, que continua nomeando o término. São o `SC-190` e o `SC-191`. **O código de acesso do portal sai no terminal do servidor**
- [x] T030 Percorrer os **cenários 4 e 5** de `specs/037-quatro-becos-conhecidos/quickstart.md` (**EXISTENTE**) — o peso, e depois **o que não pode ter mudado**: contar os controles do cartão do marco antes e depois (`FR-551a`), e conferir que **o peso continua sendo campo da Etapa** (`FR-552`) e que nenhum conteúdo publicado foi reescrito nem nada apagado (`FR-555`). São o `SC-192`, o `SC-193` e o `SC-194`
- [x] T031 Conferir **caso a caso** os testes alterados contra o "antes" gravado em `specs/037-quatro-becos-conhecidos/antes-dos-quatro-becos.md` (**EXISTENTE**, criado em T002), e **recontar**: `research.md` `R-4` prevê **quatro**, e a `034` previu oito e entregou doze. Se forem mais, registre por quê. Confira também que os **vizinhos permaneceram** — 10, 13 e 11 casos nos três arquivos medidos
- [x] T032 Escrever `specs/037-quatro-becos-conhecidos/rastreabilidade.md` (**NOVO**): uma linha por `FR-`, uma por `SC-`, **uma por teste alterado com o motivo**, e uma seção que responde por escrito **o que o percurso da `T011` decidiu** (`SC-195`) — porque é a única tarefa desta feature cujo desfecho muda o que foi entregue, e **achado sem desfecho registrado volta na próxima auditoria**
- [x] T033 Rodar `cd backend && make lint check test-pg` e registrar a contagem final em `specs/037-quatro-becos-conhecidos/rastreabilidade.md` (**EXISTENTE**, criado em T032). `test-pg` e **nunca** `test`; `lint` são **dois** passos. **Esta feature não tem migration**, e o `makemigrations --check` aqui prova exatamente isso. As promessas que se conferem **lendo o diff** são três: nenhuma decisão de **autorização** e nenhum aceite ou recusa de ato mudou (`FR-553`), nenhuma **ajuda instrucional** entrou nos cartões (`FR-554`) e nenhum conteúdo publicado foi reescrito (`FR-555`). **Ao conferir a `FR-554`, leia antes a `FR-554a`**: a frase que a `US4` acrescenta ao cartão é aviso derivado do estado, não ajuda, e conferir sem a distinção produz um falso positivo contra a própria feature. **Rode a suíte inteira, e não só os arquivos tocados**: a varredura deste repositório **lê o comentário do template**, e três das quatro histórias são prosa

---

## Dependências

```
Phase 1 (T001–T003)
      │
      ├──► US1 (T004–T010)  🎯 MVP
      ├──► US2 (T011–T017)   ← T011 decide se T015 existe
      ├──► US3 (T018–T022)
      └──► US4 (T023–T026)
                 │
                 ▼
        Polimento (T027–T033)
```

**As quatro histórias são independentes na ENTREGA**: cada uma fecha um achado sozinha, e nenhuma
precisa de outra para ser percorrida. **Não são independentes na EDIÇÃO**: `US1`, `US2` e `US4`
tocam o mesmo `interface/views.py`.

### Dentro das fases

- **T004 → T005** são o **mesmo arquivo**, e a ordem importa: oferecer o link antes de o caminho
  distinguir a recusa deixa o beco novo aberto entre uma tarefa e a outra.
- **T005 → T006** são o **mesmo arquivo** e a mesma decisão em dois passos: qual caminho, e se este
  ator o alcança. Separá-las em ordem inversa oferece o caminho antes de perguntar quem o abre.
- **T006 → T007** — a view escolhe, o template imprime.
- **T009 → T010** são o mesmo arquivo, e a contraprova vem depois do caso simples.
- **T011 → T015** — o percurso decide se a tarefa existe.
- **T012 → T015** são o mesmo arquivo (`interface/views.py`), e a `T012` vem antes porque é ela que
  cria a derivação única de que a `T015` depende.
- **T013 → T014** — o mecanismo antes da tela que o usa. Invertidas, a `T014` não teria como produzir
  a forma cheia e alguém a escreveria à mão, que é exatamente o que a `FR-543` proíbe.
- **T018 → T019 → T020 → T021 → T022** — o módulo antes dos testes das duas superfícies, e as duas
  superfícies depois dele. **T018 é um ato só**: predicado e escolha do instante juntos.
- **T024 → T025** — o campo antes da frase que o lê.
- **T031 depois de todos os percursos** — percurso que ache defeito muda o estado que ela confere.

### Oportunidades de paralelismo

**Nenhuma.** Três das quatro histórias tocam `interface/views.py`, e por isso **nenhuma tarefa desta
feature leva `[P]`**. A independência das histórias é de entrega, e a regra do `[P]` é de arquivo.

---

## Estratégia de entrega

**MVP**: a `US1` sozinha. Ela fecha a parte que sobrou do `ACH-46` e é a única cuja ausência deixa um
achado `P0` parcialmente aberto.

**Incremental**: `US1` → `US2` → `US3` → `US4`, em ordem de prioridade. Qualquer uma pode ser
entregue e percorrida isoladamente; travar numa não bloqueia as outras.

**Se o tempo apertar**: a `US4` é a que menos custa deixar para depois — a contradição dela hoje
aparece, só que tarde. A `US3` é a que menos se deve adiar: hoje há Edital legítimo que **não
consegue** concluir uma etapa.
