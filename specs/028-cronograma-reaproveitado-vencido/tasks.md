---

description: "Task list for feature implementation"
---

# Tasks: Cronograma reaproveitado não nasce publicável

**Input**: Design documents from `specs/028-cronograma-reaproveitado-vencido/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/cronograma-vencido.md](./contracts/cronograma-vencido.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo e nomeia
publicação e retificação entre os que exigem cobertura específica; a §5 da spec fecha a feature em
oito invariantes verificáveis, e a `SC-118` é literalmente um teste. Nenhuma feature anterior abriu
exceção; esta não abre.

**Organization**: por user story, para que cada faixa seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US5`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

**Nenhuma migration, nenhum degrau de schema, nenhum app novo, nenhuma dependência nova, nenhum
campo no conteúdo publicado.** Se alguma tarefa abaixo levar você a criar migration, a abrir degrau
ou a acrescentar biblioteca, a tarefa foi mal lida — a forma publicada não muda
([contracts/cronograma-vencido.md](./contracts/cronograma-vencido.md), §7).

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_028`, e **como variável do Make** —
`make DB_NAME=ps_demo_028 …`, nunca `DB_NAME=ps_demo_028 make …`. O `Makefile` faz `include .env`
seguido de `export`, e `include` **sobrepõe** variável de ambiente: o prefixo é engolido pelo
`DB_NAME` do `.env`, e a suíte desta worktree derruba a de outra sem avisar. Fora do `make` —
`manage.py` chamado direto — o prefixo é a forma certa, porque ali não há `include` nenhum.

**Esta feature depende do relógio.** Todo teste que afirme "no passado" ou "no futuro" deve declarar
o instante do ato — passando `agora=` — em vez de depender do dia em que a suíte rodar. Um teste que
passe hoje e reprove em janeiro é o defeito que a `SC-118` existe para impedir.

---

## Phase 1: Setup

**Purpose**: ter o verde de partida medido antes de mexer no que vai mudá-lo.

- [X] T001 Preparar o banco desta worktree com `cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_028 POSTGRES_USER="$USER" preparar` e confirmar `migrate --check` limpo. *A forma `make DB_NAME=…` não é estilo: o prefixo de ambiente é sobreposto pelo `include .env` do `Makefile`, e esta worktree acabaria preparando o banco de outra pessoa. `preparar` são três passos nesta ordem — provisionar, migrar, provisionar de novo; se a segunda passada disser `0 de N protegidas`, ela não rodou. Migration desaplicada contamina a sessão inteira, com sintoma longe da causa. Se a worktree for nova, `uv sync --extra dev` antes, ou `make test-pg` falha com "Failed to spawn: pytest"*
- [X] T002 Rodar `make DB_NAME=ps_demo_028 lint check test-pg` em `backend/` e **gravar a contagem de partida** (passaram, pularam) num arquivo de trabalho fora do repositório. *A `T-008` prevê que a `T015` derrube seis lugares que hoje publicam Edital com a inscrição já encerrada. Sem a contagem de antes, não há como distinguir a queda esperada da regressão. Anote também a **data da execução**: esta feature julga contra o relógio, e a contagem de partida tem validade*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: existir uma única regra de "vencido" e um único instante por ato. **Nenhuma user story
começa antes desta fase.**

- [X] T003 [P] Criar `backend/processo_seletivo/editais/domain/calendario.py` com `vencido(inicio, termino, *, agora) -> bool` e `ano_do_evento(instante) -> int`, puros, sem Django, importando a zona de `processo_seletivo/shared/tempo.py`. O `<` é **estrito**; `termino` nulo não vence por si; `inicio` nulo não vence. `ano_do_evento` converte para a zona institucional antes de ler o ano. *O módulo existe para que a regra tenha **um** lugar: a conferência a chama sobre texto ISO do snapshot e o selo a chama sobre `datetime` do ORM, e escrevê-la duas vezes é a divergência que a feature inteira existe para não produzir ([research.md](./research.md), `T-003`). `shared/tempo.py` foi criado exatamente para o domínio poder importar a zona sem passar pela interface, e está escrito lá*
- [X] T004 [P] Teste unitário em `backend/tests/unit/editais/test_calendario.py`, **sem banco**: o `<` estrito (instante igual ao do ato não venceu), término nulo, início nulo, início vencido com término futuro, e — o caso que dá nome à `SC-118` — `ano_do_evento` sobre `2026-12-31T23:30:00-03:00` devolvendo **2026**, e não 2027. *O último é a classe registrada em [doc/achado-teste-com-data-em-utc.md](../../doc/achado-teste-com-data-em-utc.md), que já reprovou o CI do PR #102 num teste que aquele branch não tocava. Ele reproduz de madrugada e some de dia, e é por isso que o instante é fixado no teste em vez de vir do relógio*
- [X] T005 Dar a `validate_for_publication` em `backend/processo_seletivo/editais/domain/validation.py:1322` o parâmetro `agora`, resolvido **uma vez no topo da função** — `agora = agora or datetime.now(ZONA)` — e repassado às verificações que dele precisam. O padrão `None` lê o relógio. *Uma vez, e não a cada Evento: resolver dentro de cada verificação faria dois Eventos do mesmo cronograma serem julgados contra instantes diferentes, e um cronograma cujo Evento vence no meio da passada produziria relatório que não corresponde a estado nenhum (`FR-341`). O padrão copia o do `ato` que a `027` introduziu, e pela mesma razão: esquecer o parâmetro faz a conferência **acusar**, e não silenciar*
- [X] T006 Passar o instante do ato nas chamadas de `validate_for_publication`: `backend/processo_seletivo/publicacoes/application/publish_edital.py:431` e `:649` recebem o `now` do `command_context()`; `backend/processo_seletivo/interface/views.py:528` recebe o instante da requisição, resolvido uma vez. *É o que a Constituição pede no Princípio II — "operações relacionadas DEVEM compartilhar referência temporal consistente na mesma transação" —, e o efeito é que o achado e o registro da publicação falam do mesmo instante. `:431` é a submissão e `:649` é a publicação efetiva: **são atos distintos, em instantes distintos**, e é essa distinção que a `FR-358` exige que sobreviva*
- [X] T007 **Não tocar** em `backend/processo_seletivo/publicacoes/application/retificacoes.py:577`, e registrar por que num comentário. *A linha chama `validate_for_publication(content)` **sem `ato=`**, e parece esquecimento. Não é: ela calcula o conjunto de códigos impeditivos **para subtraí-los** da lista que a linha 580 produz sob `ATO_DE_RETIFICACAO`. "Consertar" o `ato` ali mudaria o conjunto subtraído e alteraria, em silêncio, o que a confirmação da Retificação mostra. Confira com teste em vez de corrigir de memória*
- [X] T008 Teste em `backend/tests/unit/editais/test_cronograma_vencido.py` de que a conferência usa **um** instante: um cronograma com dois Eventos separados por microssegundos em torno de um `agora` fixo produz o mesmo relatório em execuções repetidas, e passar `agora` explicitamente produz resultado independente do relógio da máquina. *É a `FR-341` verificada, e é o único teste que distingue "resolvido uma vez" de "resolvido a cada Evento" — os dois passam em todos os outros casos*

**Checkpoint**: existe uma regra de vencimento e um instante por ato. Nada mudou de comportamento
ainda.

---

## Phase 3: User Story 1 — O cronograma copiado não se anuncia pronto (P1) 🎯 MVP

**Goal**: quem reaproveita vê a etapa Cronograma **pendente**, com a frase que diz por quê, sem que
nenhuma data tenha sido tocada.

**Independent Test**: reaproveitar um Edital cujo cronograma esteja no passado e abrir a composição —
a etapa Cronograma aparece pendente na primeira abertura, sem nenhuma gravação.

- [X] T009 [US1] Acrescentar `schedule_event_in_past` em `backend/processo_seletivo/editais/domain/validation.py`, como verificação nova chamada ao lado de `_periodo_de_inscricoes` (linha 1375), **advertência**, **um achado por Evento**, endereçando o **término** vencido — e o início só quando não houver término declarado (`FR-343a`) —, e **produzida apenas no ato de publicação** (`if ato != ATO_DE_PUBLICACAO: return []`). Instante que não converte é ignorado em silêncio. *O caminho é o do Evento, e **nunca `/schedule`**: `DESTINO_DA_PENDENCIA` tem entrada exata para `/schedule` que manda para a etapa **Inscrição** — correta para a designação do período, errada para a data. Com o caminho da entidade, `_destino` percorre os segmentos e entrega `cronograma` sozinho, sem entrada nova (`FR-349`, `T-005`). O recuo em silêncio sobre instante malformado é o mesmo de `_perfis_bem_formados`: empilhar duas acusações sobre a mesma causa esconde a que resolve*
- [X] T010 [US1] Escrever, junto com a T009 e em `backend/tests/unit/editais/test_cronograma_vencido.py`, o teste do **ato** e o da **precedência**: (a) o mesmo conteúdo produz o achado sob `ATO_DE_PUBLICACAO` e **nenhum** sob `ATO_DE_RETIFICACAO`; (b) Evento com início e término vencidos produz **um** achado, que nomeia o **término** e endereça `/endAt`; (c) Evento vencido sem término declarado nomeia o início e endereça `/startAt` (`FR-343a`). *A alínea (a) entra junto, e não depois. Sem o recorte do ato, toda Retificação de todo Edital do acervo passa a carregar uma advertência por Evento vencido do cronograma inteiro — e o que se repete a cada ato deixa de ser lido. É a mesma armadilha que a `027` teve de nomear para não cometer*
- [X] T011 [US1] Mudar o critério do selo em `backend/processo_seletivo/interface/views.py:677` (`_progresso`): `CONCLUIDA` passa a exigir Evento **e** nenhum deles vencido, chamando `vencido` da T003 sobre os `datetime` do ORM. `.exists()` vira `.all()` sobre a mesma relação. *Uma consulta, como hoje — um Cronograma tem uma dezena de Eventos. **Não filtrar no banco**: um `Q(start_at__lt=agora)` poria a `FR-359` numa expressão de ORM que o predicado do domínio não alcança, e a regra passaria a ter duas grafias que ninguém compara (`T-003`). **O ano não entra no selo**: `FR-359` fala de passado, e apagar o selo por divergência de ano daria a um Edital legítimo de dezembro a aparência de incompleto*
- [X] T012 [P] [US1] Teste de interface em `backend/tests/interface/test_selo_do_cronograma.py`: Edital com Evento no passado exibe a etapa Cronograma pendente; com tudo no futuro, concluída; corrigir as datas devolve o selo sem gravação além da correção; e **os outros oito selos não mudam de critério** em nenhum dos casos. Exigir também, com o Cronograma pendente, que o botão de avançar entre etapas funcione e que a submissão **não** seja recusada por causa do selo (`FR-362`). *Cobre `FR-359`, `FR-360`, `FR-361` e `FR-362`. A asserção dos oito selos impede a generalização acidental: cada etapa tem uma noção própria de "válida", e decidi-las em bloco é o que produz regra que ninguém revisou. A da `FR-362` impede a confusão mais provável de quem implementar a T011 — pendente **orienta** quem retoma o trabalho, e não fecha porta; quem fecha é o impeditivo da T015, e ele é um só. **"Avanço" aqui é a navegação do assistente**, que é o único sentido que a spec dá à palavra*
- [X] T013 [P] [US1] Teste de interface no mesmo arquivo: criar um Edital por reaproveitamento a partir de um Edital com cronograma vencido, abrir a composição **sem gravar nada**, e exigir (a) a etapa Cronograma pendente, (b) a etapa Cronograma exibindo o achado em `pendencias_aqui`, (c) o aviso permanente da `023` ainda presente, (d) **nenhuma data diferente** da do Edital de origem. *A alínea (b) é a `UX-049`, e ela não custa template novo: `views.py` já calcula `_pendencias` em cada página do assistente e `compor_cronograma.html` já renderiza `pendencias_aqui` (`T-004`). A alínea (d) é a `FR-351` e a `SC-116` — o invariante que a feature inteira protege —, e é a única que, quebrada, reproduz por dentro o defeito que a Constituição proíbe do lado de fora*
- [X] T014 [P] [US1] Teste em `backend/tests/unit/editais/test_cronograma_vencido.py` de que o achado chega à etapa **Cronograma**, e não à **Inscrição**: afirmar o destino resolvido por `_destino` para o caminho produzido. *É a `FR-349` verificada em vez de suposta. A auditoria já registrou uma vez o mesmo defeito em outra tela — "Pendência de marco roteada para a tela errada", P1 —, e ele não falha em execução: falha mandando a pessoa para uma tela sem o campo que resolve*

**Checkpoint**: um Edital reaproveitado com cronograma vencido já se anuncia pendente, e diz por quê.

---

## Phase 4: User Story 2 — Publicar um certame que ninguém pode disputar é impedido (P1)

**Goal**: o período de inscrições já encerrado fecha a submissão e a publicação, com o instante do
encerramento dito.

**Independent Test**: compor um Edital cujo Evento marcado como período de inscrições termina no
passado e tentar publicá-lo — a publicação é recusada, e a mensagem diz quando o prazo venceu.

- [X] T015 [US2] Acrescentar `registration_period_closed` em `backend/processo_seletivo/editais/domain/validation.py`, **erro impeditivo**, endereçando `/schedule/id=<uuid>/endAt`, produzido **apenas no ato de publicação**, reusando `periodo_de_inscricoes(snapshot, agora).estado == ENCERRADO` de `backend/processo_seletivo/inscricoes/domain/periodo.py:45`. *Reusar, e não reescrever: essa é a função que o **portal** obedece para decidir se aceita uma inscrição, e duas leituras discordantes fariam o sistema recusar publicar um Edital que em seguida aceitaria inscrição — dado independente e divergente, que é o Princípio II ao pé da letra (`T-002`). A importação entre apps de domínio foi medida e não cria ciclo: `periodo.py` não importa nada de `editais`, e `avaliacoes/domain/conjunto.py` já o importa*
- [X] T016 [P] [US2] Teste das bordas em `backend/tests/unit/editais/test_cronograma_vencido.py`, com `agora` fixo: término **igual** ao instante do ato **não** encerra; término ausente **não** encerra; período em curso (início vencido, término futuro) **não** encerra e produz só a advertência; período futuro não produz nada; Edital sem Evento marcado produz a advertência que já existia e **nenhum achado novo**; dois Eventos marcados continuam produzindo o impeditivo que já existia. Exigir, no mesmo arquivo, que `registration_period_closed` **não** seja produzido sob `ATO_DE_RETIFICACAO` (`FR-354`). *O `>` estrito de `periodo_de_inscricoes` já é a `FR-347`, e este teste existe para que ninguém o troque por `>=` sem perceber o que está decidindo. As três últimas linhas são a `FR-350`: os achados existentes não mudam*
- [X] T017 [P] [US2] Teste em `backend/tests/unit/editais/test_cronograma_vencido.py` de que a mensagem do impeditivo diz **quando** as inscrições se encerraram, em forma legível na zona institucional, e **o que acontece** se o Edital for publicado assim — e que ela não contém texto ISO cru, JSON Pointer nem instante em UTC. *É a `UX-047` e a `UX-048`. A régua vem do achado P1 da auditoria, "JSON Pointer e UTC na conferência da Retificação": esta feature não é o lugar de repeti-lo*
- [X] T018 [US2] Converter `backend/tests/integration/avaliacoes/test_conjunto_fechado.py:130-137` para publicar com o período **aberto** e fechá-lo por Retificação, usando `retify` de `backend/tests/fixtures/publicacao.py:190`. *Primeiro dos seis, e o mais instrutivo: o teste precisa de conjunto fechado para distribuir, e hoje o obtém publicando um Edital cujas inscrições já acabaram — atalho que nenhum Edital do mundo pratica. Publicado antes e fechado pelo tempo é como o caso acontece, e a `FR-355` autorizou por escrito a Retificação que declara término já passado*
- [X] T019 [P] [US2] Converter, pelo mesmo caminho da T018 — são **quatro**, e não cinco: `backend/tests/integration/portal/test_vitrine.py:178-180`, `backend/tests/integration/portal/test_situacao_inscricoes.py:74`, `backend/tests/integration/portal/test_cronograma_publico.py:214`, e `backend/tests/integration/supervisao/test_pulso.py:254`. *São os restantes medidos em `T-008`. **`test_cronograma_publico.py:40` ficou de fora de propósito**: o `endAt` vencido daquela linha é do Evento *Homologação*, e o período de inscrições daquele cenário corre de `-2d` a `+10d` — aberto, e portanto não bloqueado. Ele ganha a advertência nova e nada mais. Converter o que não precisa é trabalho que parece necessário e não é. **Não excetuar a regra para teste nem para demonstração**: uma porta lateral na conferência é encontrada pela primeira pessoa que precisar dela em produção*
- [X] T020 [US2] Em `backend/processo_seletivo/processos/management/commands/seed_demo.py:717` (`_edital_encerrado`), publicar o segundo Edital com o período de inscrições **aberto** e fechá-lo por Retificação publicada **antes** do passo que distribui — `_congelar_e_distribuir` exige conjunto fechado, e uma Retificação publicada depois dele deixaria a distribuição correndo com o prazo ainda aberto, que o domínio recusa. *Está na fase da US2, e não na da US5, porque quem a torna necessária é a `T015`: **assim que o impedimento existir, `seed_demo` para de semear**, e `backend/tests/integration/test_seed_demo.py` fica vermelho até que esta tarefa entre. Parar a entrega em US2, US3 ou US4 sem ela deixa a suíte quebrada. O quarto Edital continua sendo da US5. Sem isto a demonstração não semeia: a `FR-346` recusa a publicação que ela faz hoje com `cronograma(agora - timedelta(days=60), numero)`. Não é conserto de fixture — é o Edital passando a contar a verdade, e a demonstração passando a **mostrar** o ato que encerra um prazo*
- [X] T021 [US2] Teste em `backend/tests/integration/publicacoes/` de que a recusa alcança os dois atos: submeter um Edital com o período aberto e tentar publicá-lo com um `agora` posterior ao término — a publicação é recusada; e publicar um Edital sem que a Revisão tenha sido aberta é recusado pelo mesmo impedimento. *É a `FR-357` e a `FR-358`. A segunda metade já é verdade estrutural — `publish_edital:649` confere de novo, independentemente da submissão —, e o teste existe para que continue sendo depois de alguém "otimizar" a conferência duplicada*

**Checkpoint**: nenhum Edital chega à publicação com as inscrições já fechadas, e a suíte está verde
de novo.

---

## Phase 5: User Story 3 — Advertir sem recusar o Edital de dezembro (P1)

**Goal**: divergência de ano adverte e não recusa, e o cenário do 12/2027 produz exatamente os três
achados.

**Independent Test**: compor um Edital de ano seguinte com eventos futuros e ver a advertência sem
impedimento; compor o cenário do 12/2027 e ver as três coisas ao mesmo tempo.

- [X] T022 [US3] Acrescentar `schedule_event_year_mismatch` em `backend/processo_seletivo/editais/domain/validation.py`, **advertência**, endereçando `/schedule/id=<uuid>/startAt`, comparando `ano_do_evento(inicio)` com `snapshot["year"]`, produzida **apenas no ato de publicação**. *O ano é o do **início**, e nunca o do término: um Evento que começa em dezembro e termina em janeiro é a definição de período que atravessa o ano, e conferir os dois acusaria todo Edital de fim de ano — o caso que a `D-006` decidiu não incomodar (`T-006`). E é advertência, nunca recusa, porque o `year` é **não retificável** pelo contrato da `026`: um impedimento apontaria para um campo que ninguém pode mexer*
- [X] T023 [P] [US3] Teste em `backend/tests/unit/editais/test_cronograma_vencido.py`: Edital de 2027 com Eventos de 2027 conferido em dezembro de 2026 produz a advertência de ano e **nenhum** impedimento; Evento em `2026-12-31T23:30:00-03:00` num Edital de 2026 produz **nenhuma** advertência de ano; um Evento que esteja no passado **e** com ano divergente produz **duas** advertências, cada uma uma vez, cada uma nomeando o instante de que fala; e `schedule_event_year_mismatch` **não** é produzido sob `ATO_DE_RETIFICACAO` (`FR-354`). *A última repete, para este código, o que a T010 fixou para o primeiro: a condição por ato é por achado, e um teste que a prove só uma vez deixa os outros dois livres para nascer sem ela. A segunda linha é a `SC-118` no lugar em que ela paga: lido em UTC, esse Evento é de 2027 e o Edital correto seria acusado de divergir de si mesmo. A terceira é a `FR-345`*
- [X] T024 [US3] Teste em `backend/tests/unit/editais/test_cronograma_vencido.py` reproduzindo o **cenário medido pela auditoria**: Edital `12/2027`, Evento "Período de inscrição" de `2026-09-13T08:00-03:00` a `2026-09-13T09:00-03:00`, marcado como período de inscrições, conferido num `agora` posterior. Exigir exatamente três achados desta feature — advertência de passado, advertência de ano divergente e impedimento de inscrições encerradas — e **nada sobre a duração de uma hora**. *É a `SC-114`, e a última cláusula é a `D-005`: a janela de uma hora é evidência, não regra. Duração é decisão normativa — uma hora é janela legítima para um sorteio ou uma sessão de prova —, e declarar um mínimo seria o sistema escrevendo calendário que nenhum Edital lhe pediu*
- [X] T025 [P] [US3] Teste em `backend/tests/interface/` de que a Revisão **não** afirma que nada está pendente enquanto houver achado desta feature, e de que um Edital composto **do zero**, sem reaproveitamento, com Evento no passado, produz os mesmos achados. *A `UX-050` e a `FR-363`. A segunda é o recorte que a `023` pediu por escrito ao deixar a regra fora do escopo dela: "É regra de **todo** Edital, e não remendo desta cópia"*

**Checkpoint**: o Edital legítimo de dezembro continua publicável, e o do 12/2027 não.

---

## Phase 6: User Story 4 — Retificar um Edital antigo não vira enxurrada (P1)

**Goal**: nenhum dos três achados existe num ato de Retificação, e o acervo continua alcançável.

**Independent Test**: abrir a conferência de uma Retificação sobre um Edital publicado com cronograma
inteiramente vencido e contar os achados desta feature: zero.

- [X] T026 [US4] Teste em `backend/tests/integration/editais/` — ao lado de `test_acervo_sem_quadro_continua_retificavel.py`, que é o vizinho que já faz isto para a `027` — publicando um Edital, deixando o cronograma inteiro vencer, e exigindo **zero** achados desta feature na conferência do ato e na publicação da Retificação. *É a `SC-115`. O arquivo vizinho existe porque a `027` precisou provar exatamente a mesma coisa sobre outro achado, e a docstring dele nomeia o mecanismo: `retificacoes.py` afere com `blocking_findings(validate_for_publication(content))`*
- [X] T027 [P] [US4] Teste em `backend/tests/integration/publicacoes/` de que uma Retificação que **antecipa o encerramento das inscrições** para um instante já passado não é recusada, e de que os achados existentes sobre o período — marca ausente, marca ambígua — continuam sendo produzidos como antes. *É a `FR-355` e a `FR-350`. Antecipar ou encerrar prazo é ato normativo de quem assina o Edital, e o contrato da `026` já classifica `startAt` e `endAt` como retificáveis*
- [X] T028 [P] [US4] Teste em `backend/tests/integration/publicacoes/` de que `advertencias_do_ato` (`backend/processo_seletivo/publicacoes/application/retificacoes.py:540`) não passa a exibir nenhum dos três achados. *Guarda a T007. A linha 577 chama a conferência sob o ato de publicação **de propósito**, para subtrair os códigos impeditivos da lista da linha 580 — e com o impeditivo novo existindo, o conjunto subtraído muda. O resultado esperado não muda, porque a lista devolvida vem do ato de Retificação; este teste é o que prova que não mudou*

**Checkpoint**: o acervo inteiro continua retificável, e nada nesta feature o alcança.

---

## Phase 7: User Story 5 — A demonstração contém o caso (P2)

**Goal**: a demonstração ganha um quarto Edital reaproveitado que exercita o cenário e para onde o
sistema o para.

**Independent Test**: semear a demonstração e percorrer o quarto Edital, da composição até a recusa
da publicação.

- [X] T029 [US5] Acrescentar a `seed_demo.py` um **quarto** Edital, criado pelo serviço de reaproveitamento (`backend/processo_seletivo/editais/application/reaproveitamento.py`) a partir do segundo, com ano declarado um à frente, e **deixado em elaboração**. *Pela mesma porta que a pessoa usa, e não escrevendo o rascunho direto: a demonstração existe para mostrar o caminho que alguém vai percorrer, que é a razão de a `023` existir. Reaproveitar o segundo produz as três condições de uma vez, sem arranjo nenhum — Eventos no passado, período encerrado e, com o ano à frente, a divergência. Ele fica em elaboração porque o sistema o impede de publicar, e é isso que ele demonstra (`FR-367`)*
- [X] T030 [US5] Estender `backend/tests/integration/test_seed_demo.py`: o quarto Edital existe, está em elaboração, tem a etapa Cronograma pendente, a Revisão com os três achados, e a publicação recusada; o segundo continua com as inscrições encerradas **por Retificação publicada**; e os três Editais anteriores continuam percorríveis. *É a `SC-119` e a `D-010`. A penúltima cláusula é o que impede a T029 de virar "mudei a data e pronto": o ato tem de estar lá*

**Checkpoint**: a demonstração mostra o caso, e mostra onde ele para.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T031 [P] Escrever `specs/028-cronograma-reaproveitado-vencido/rastreabilidade.md`: cada `FR-`, `SC-` e `UX-` desta feature, onde foi feito e onde é verificado. *É o Princípio V, e é o artefato que a `027` produziu na fase equivalente. Um requisito sem linha aqui é um requisito que ninguém sabe se entrou. **Três requisitos não têm tarefa dedicada e precisam nomear o guardião existente que os verifica**, ou a rastreabilidade registra lacuna onde há cobertura: a `FR-353` (nenhum campo novo no conteúdo publicado) em `backend/tests/contract/test_forma_publicada.py`; a `FR-364` (o reaproveitamento não muda) em `backend/tests/unit/editais/test_reaproveitamento.py` e `backend/tests/integration/editais/test_reaproveitamento.py`; a `FR-365` (conteúdo publicado não se reescreve) em `backend/tests/integration/publicacoes/test_integridade_publicacao.py` e `test_retificacao_intocada.py`. Todos são exercitados pela T033*
- [X] T032 Percorrer os quatro percursos de [quickstart.md](./quickstart.md) na interface, anotando **a data da execução** ao lado de cada resultado. *O percurso `B9` exige espera real — declarar o término a poucos minutos à frente, submeter e homologar dentro da janela, confirmar a publicação depois dela. Não há relógio a congelar na interface, e é assim que o caso acontece na vida*
- [X] T033 Rodar `cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_028 POSTGRES_USER="$USER" lint check test-pg` e comparar com a contagem da T002. *`test-pg`, e não `test`: sem o par de variáveis a suíte cai para SQLite, onde 33 casos falham por motivo que nada tem com o diff. `lint` são **dois** passos — `ruff check` **e** `ruff format --check` —, e rodar só o primeiro declara verde local e quebra no CI. A queda esperada é a dos seis lugares da T018/T019, e ela já deve ter sido paga; qualquer outra é lida, e nenhuma é silenciada*
- [X] T034 [P] Rodar `cd backend && uv run pytest tests/test_citacoes_de_requisito.py` antes de empurrar. *PR de documentação também quebra o CI: a varredura lê `specs/**/*.md` e `backend/**/*.{py,html,js}` e falha se alguma citação `FR-`, `SC-`, `UX-` ou `D-` apontar para identificador que nenhuma spec define. As docstrings desta feature citam requisitos, e é por aí que ela quebraria*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependências.
- **Foundational (Fase 2)**: depende do Setup. **Bloqueia todas as user stories** — sem o predicado
  e sem o instante, nenhum achado pode ser escrito corretamente.
- **US1 (Fase 3)**: depende da Fase 2. É o MVP.
- **US2 (Fase 4)**: depende da Fase 2. Independente da US1.
- **US3 (Fase 5)**: depende da Fase 2. Reusa o esqueleto de verificação da T009, então é mais barata
  depois da US1 — mas não depende dela.
- **US4 (Fase 6)**: depende da Fase 2 e de **pelo menos um** achado existir (T009 ou T015), porque é
  o que ela prova ausente no ato de Retificação. Na prática: depois da US2.
- **US5 (Fase 7)**: depende da US2 e da US1. **A tarefa que a US2 tornou obrigatória — a T020, que
  faz `seed_demo` voltar a semear — subiu para a Fase 4**, porque sem ela a suíte fica vermelha assim
  que o impedimento existir. O que resta na Fase 7 é o quarto Edital, que é da US5.
- **Polish (Fase 8)**: depois de todas.

### Dentro de cada user story

A condição por ato entra **junto** com o achado, e nunca depois — T010 com T009, e o `ato` já escrito
em T015 e T022. Escrever o achado primeiro e o recorte em seguida deixa, no intervalo, uma versão do
código que prende o acervo inteiro.

### Parallel Opportunities

- **Fase 2**: T003 e T004 em paralelo (módulo e teste, arquivos distintos).
- **Fase 3**: T012, T013 e T014 em paralelo depois de T009 e T011.
- **Fase 4**: T016 e T017 em paralelo depois de T015; T018, T019 e T020 em paralelo entre si
  (arquivos distintos), e todos depois de T015.
- **Fase 5**: T023 e T025 em paralelo depois de T022.
- **Fase 6**: T027 e T028 em paralelo depois de T026.
- **Fase 8**: T031 e T034 em paralelo.
- **Entre stories**: US2 e US3 podem correr em paralelo por pessoas diferentes depois da Fase 2 —
  tocam a mesma `validation.py`, então coordenem o arquivo ou sequenciem as duas tarefas de achado.

---

## Parallel Example: Fase 4

```bash
# Depois da T015, em paralelo:
Task: "T016 bordas do impedimento em backend/tests/unit/editais/test_cronograma_vencido.py"
Task: "T017 forma da mensagem no mesmo arquivo"
Task: "T019 converter os cinco lugares restantes"
```

---

## Implementation Strategy

### MVP (US1)

1. Fase 1 → Fase 2 → Fase 3.
2. **PARE E VALIDE**: reaproveitar um Edital com cronograma vencido e ver a etapa pendente, com a
   frase, sem nenhuma data mexida.
3. É a metade do achado que custa menos e já muda o que a pessoa vê no primeiro segundo.

### Entrega incremental

1. Fase 2 → fundação pronta.
2. US1 → o cronograma copiado se anuncia pendente. **MVP.**
3. US2 → o Edital sem saída deixa de nascer. É o P0 fechado.
4. US3 → o Edital legítimo de dezembro continua publicável, e o cenário da auditoria é caso de teste.
5. US4 → o acervo continua alcançável.
6. US5 → a demonstração conta a história.

**Parar depois da US1 entrega valor e não fecha o P0.** O que fecha é a US2; a US3 e a US4 são o que
a mantêm usável, e sem elas a feature é um bloqueio que incomoda quem está certo.

---

## Notes

- `[P]` = arquivos distintos, sem dependência pendente.
- **Nenhuma tarefa desta lista altera, desloca ou sugere data.** Se alguma parecer pedir isso, foi
  mal lida: é o primeiro invariante da spec, e o único que, quebrado, reproduz por dentro o defeito
  que a Constituição proíbe do lado de fora.
- **Nenhuma tarefa cria migration.** Se o `migrate --check` acusar algo, é ambiente.
- Todo teste que afirme "passado" ou "futuro" passa `agora=` explicitamente. Um teste que dependa do
  dia em que a suíte rodar é o defeito que a `SC-118` existe para impedir.
- Commit a cada tarefa ou grupo lógico; parar em qualquer checkpoint valida a story sozinha.
