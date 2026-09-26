---

description: "Task list — 045 · Condução confiável do Processo vivo"
---

# Tasks: Condução confiável do Processo vivo

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim.** A proposta pede nove testes de regressão por nome (spec, *"Os testes de regressão
da proposta"*), e a feature **apaga** comportamento cercado por teste — o `UX-001`, o `UX-002` e o
`Marco.declarado`. Apagar sem contar é o modo de perder guarda sem perceber.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: arquivos diferentes, nenhuma dependência aberta. **Ganhou arquivo em comum depois, o `[P]`
  sai.**
- **NOVO / EXISTENTE**: onde diz existente, **acrescente; não reescreva** o que a tarefa não manda
  mudar. Onde a tarefa manda apagar ou reescrever, ela nomeia o caso.

---

## Os cinco portões

1. **`T002` roda ANTES de qualquer edição**: a contagem da suíte e a contagem, **caso a caso**, dos
   arquivos que esta feature reescreve (`research.md`, `R-8`). A `034` previu oito alterados e entregou
   doze.
2. **Esta feature NÃO tem migration.** O `make preparar` continua **`N de 34`**, com N diferente de
   zero. Outro número é worktree atrás da `main`, e não defeito.
3. **`T003` vem antes de qualquer recusa da fase.** O ajudante `levar_a_publicacao` engole o 400 do
   `PUT` do rascunho, e a recusa da `T017` apareceria como falha de submissão com causa enganosa.
4. **A `US4` espera a `US3`.** Enquanto o `UX-001` e o `UX-002` existem, a condução seria escrita
   para sinais que vão sumir.
5. **Nada de `make test`.** `make test-pg`, com `DB_NAME` próprio da worktree; `lint` são **dois**
   passos (`ruff check` **e** `ruff format --check`); e não edite template durante a suíte.

---

## Phase 1: Setup e medição do "antes"

- [ ] T001 Preparar a worktree em `backend/`: copiar `backend/.env` do checkout principal (**gitignorado**, ausente aqui), trocar `DB_NAME` e `POSTGRES_DB` por nome próprio desta worktree, `uv sync --extra dev`, `make preparar` — conferir **`N de 34`** com N diferente de zero — e `manage.py migrate --check`
- [ ] T002 Medir e gravar o "antes" em `specs/045-conducao-confiavel-processo/antes-da-conducao.md` (**NOVO**): a contagem da suíte (`make test-pg`); o número de casos de cada arquivo que a `R-8` nomeia — `tests/integration/supervisao/test_sinais.py`, `tests/interface/test_supervisao.py`, `tests/unit/interface/test_supervisao.py`, `tests/acceptance/test_supervisao_do_processo.py`, `tests/integration/supervisao/test_autorizacao.py`, `tests/integration/supervisao/test_pulso.py`, `tests/interface/test_distribuicao.py`, `tests/interface/test_round_trip_do_rascunho.py`, `tests/integration/editais/test_reaproveitamento.py`, `tests/unit/editais/test_etapas.py`; e a **frase de ausência que cada papel lê hoje** no Processo do `seed_demo` (Gestor, Publicador, Julgador, Auditor). **Antes de qualquer edição**

**Checkpoint**: o "antes" está gravado, com a contagem por arquivo.

---

## Phase 2: Foundational — o ajudante que engole o erro

- [ ] T003 Fazer `levar_a_publicacao` conferir a resposta do `PUT` do rascunho em `backend/tests/fixtures/publicacao.py` (**EXISTENTE**, ~linhas 63-68): recusa ali precisa falhar **ali**, com o corpo da resposta na mensagem, e não reaparecer como `blocking_findings` na submissão. Rodar `make test-pg` depois — **deve continuar verde**; se não continuar, alguma fixture já publicava rascunho recusado, e isso se registra antes de seguir (`research.md`, `R-4`)

**Checkpoint**: um 400 do rascunho, em qualquer teste, falha com a causa certa.

---

## Phase 3: US1 — A ausência respeita o alcance de quem lê (P1) 🎯 MVP

**Goal**: quem alcança parte das espécies lê a ausência relativa; a frase não depende do que o leitor
não alcança.

**Independent Test**: três identidades — Gestor, Publicador, Julgador — sobre o mesmo Processo; a
frase de cada um é a relativa, e é **idêntica** com e sem condição fora do seu alcance.

- [ ] T004 [US1] Acrescentar a escolha da frase em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**, junto de `alcance`), `FR-730`, `FR-731`: uma função que recebe o dicionário de `alcance(ator, processo)` e devolve a frase global quando **todas** as espécies são alcançadas e a relativa quando **alguma** é, conforme o contrato ([contracts/a-atencao-depois-da-045.md](contracts/a-atencao-depois-da-045.md), seção 1). **Nunca** `alcance_no_edital` nem os sinais montados — é o que fecha o vazamento (`research.md`, `R-1`). Uma função só, para que Processo e Supervisão não escolham cada um a sua (`038`, `FR-557`)
- [ ] T005 [US1] Passar a frase às duas páginas em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**, `processo_detalhe` ~3921 e `supervisao` ~4009), lida da função de T004 sobre o **mesmo** `alcancadas` que já decide `atencao_visivel`
- [ ] T006 [US1] Exibi-la em `backend/processo_seletivo/interface/templates/interface/processo_detalhe.html` e `backend/processo_seletivo/interface/templates/interface/supervisao.html` (**EXISTENTES**, a linha `<p class="nenhuma">` ~140), `UX-084`. Atualizar o comentário do bloco: ele diz *"FR-559"* e passa a dizer também `FR-730`
- [ ] T007 [US1] Prender a `US1` em `backend/tests/interface/test_supervisao.py` (**EXISTENTE** — acrescente ao fim): (a) Publicador e Julgador sem sinal leem a frase **relativa**; (b) **a região da Atenção do mesmo leitor é idêntica, byte a byte**, com e sem uma condição que só o Gestor alcança — o teste 9 da proposta; (c) um ator com Gestor, Julgador e Publicador num Processo sem condição lê a **global**; (d) o Gestor sozinho, na Supervisão, lê a **relativa** — ele não alcança recursos nem divulgação; (e) o ator sem espécie nenhuma continua sem a região (o caso da `038` permanece); (f) quem alcança todas as espécies, num Processo cujos Editais **todos pararam por ato**, lê a frase **global** — o estado retirou espécies do Edital, e não do leitor (spec, caso-limite *"O alcance muda com o estado do Edital"*)

**Checkpoint**: `C1` fechada. Nenhum leitor com alcance parcial ouve que o Processo está em dia.

---

## Phase 4: US2 — O recurso aparece desde que chega (P2)

**Goal**: a peça produz sinal enquanto espera admissibilidade e enquanto espera julgamento; decidida,
sai do sinal e da contagem.

**Independent Test**: interpor, abrir como Julgador (sinal, fase *admissibilidade*), admitir (mesmo
sinal, fase *julgamento*), julgar (sem sinal, contagem menor).

- [ ] T008 [US2] Ampliar `sinais_do_recurso` em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**, ~1130-1199), `FR-732`, `FR-733`, `UX-085`: **uma** chamada a `recursos_do_edital(edital)` sem filtro, e as pendentes são as de situação `AGUARDANDO_ADMISSIBILIDADE` **ou** `AGUARDANDO_JULGAMENTO`; a partição `travadas`/`soltas` corre sobre a união, **no mesmo ato** (a lição da `038`). A mensagem de cada sinal diz a fase das peças que **aquele** sinal conta — *admissibilidade*, *julgamento* ou *decisão — admissibilidade ou julgamento* —, conforme o contrato, seção 2. Atualizar a docstring: a razão de o impedimento valer igual nas duas fases é `admitir.py:54` sem `etapa_id` (`research.md`, `R-2`)
- [ ] T009 [US2] Trocar a contagem da ação em `backend/processo_seletivo/interface/acoes.py` (**EXISTENTE**, ~118-128), `FR-734`: contar só as peças **sem juízo** ou **com juízo que admitiu e sem decisão**, numa consulta com `Exists` — **sem** materializar peça —, e o rótulo passa a *"Recursos aguardando decisão (N)"*. Corrigir o comentário que diz que *"o recurso corre contra prazo"*: não há prazo de resposta modelado (spec, fato 6)
- [ ] T010 [US2] Prender a `US2` em `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE** — acrescente ao fim; os casos do recurso da `038` permanecem): (a) peça recém-interposta produz `UX-064` com a fase *admissibilidade* — o teste 2 da proposta; (b) admitida, o **mesmo** sinal diz *julgamento*; (c) na admissibilidade com a comissão inteira impedida, `UX-005` e **não** `UX-064`; (d) inadmitida, e julgada, **nenhum** dos dois — o teste 3; (e) uma peça em cada fase, a mensagem diz as duas. Conferir que `test_dobrar_os_recursos_pendentes_nao_dobra_as_consultas` continua passando **sem mudar o número**
- [ ] T011 [P] [US2] Prender a contagem em `backend/tests/interface/test_hardening_pos_auditoria.py` (**EXISTENTE**, junto de `test_quem_julga_recurso_chega_a_tela_de_recursos` ~136): com uma peça pendente e uma julgada, a lista de Processos e o cartão do Edital dizem *"Recursos aguardando decisão (1)"* — hoje nenhum teste confere o número

**Checkpoint**: `C2` fechada. Nenhuma peça esperando decisão fica fora da Atenção de quem julga.

---

## Phase 5: US3 — O Cronograma deixa de produzir alarme (P3)

**Goal**: a fase é derivada; o `UX-002` deixa de existir; a Etapa sem Evento é aviso de composição, e
não sinal de condução.

**Independent Test**: Edital publicado com Evento passado, corrente e futuro e uma Etapa sem Evento —
zero sinais de Cronograma, fase do relógio no pulso, aviso na validação.

### A fase

- [ ] T012 [P] [US3] Acrescentar `fase(inicio, termino, *, agora)` em `backend/processo_seletivo/editais/domain/calendario.py` (**EXISTENTE**), `FR-735`: *planejado* antes do início, *concluído* se `vencido`, *em andamento* entre os dois; `None` sem início. **Lê `vencido`, não o reescreve** (`037`, `FR-547`). Prender em `backend/tests/unit/editais/test_calendario.py` (**EXISTENTE** — acrescente): os três casos com término, o pontual antes e depois, o `<` estrito no instante exato, e sem início
- [ ] T013 [US3] Trocar `Marco.declarado` por `Marco.fase` em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**, ~122-128 e `marcos_do_edital` ~339-367), `FR-735`, `FR-736`, `UX-088`: `CANCELADO` continua saindo; o período de inscrições lê a fase do **estado do período** (`periodo_de_inscricoes` — futuro, aberto, encerrado), e os demais, `calendario.fase`; o corte da lista passa a ser *concluído*, e não `termina <= agora` (`research.md`, `R-3`). Apagar `DECLARACOES` se nada mais o usar
- [ ] T014 [US3] Exibir a fase nos próximos marcos em `backend/processo_seletivo/interface/templates/interface/supervisao.html` (~112-121) e `backend/processo_seletivo/interface/templates/interface/processo_detalhe.html` (~114-121) (**EXISTENTES**), `UX-088`: *"em andamento"* no marco em curso, nenhuma marca no futuro, e **nunca** *"declarado"*. Reescrever o comentário que cita `FR-023` e `D-004` da `022`: os dois foram substituídos
- [ ] T015 [US3] Prender a fase no pulso em `backend/tests/integration/supervisao/test_pulso.py` (**EXISTENTE** — acrescente): o período de inscrições **sem término** continua nos próximos marcos, *em andamento*; o Evento pontual sai da lista quando vence; o cancelado não aparece — o teste 5 da proposta; e um conteúdo **já publicado** com `EM_ANDAMENTO` num Evento futuro — montado direto em `backend/tests/fixtures/snapshot.py`, porque depois da T017 nenhum caminho de entrada o produz — é lido como *não cancelado* e exibido *planejado*, sem ser reescrito (spec, caso-limite *"Edital publicado antes desta feature"*). E reescrever `backend/tests/interface/test_supervisao.py::test_o_processo_e_a_supervisao_dizem_a_mesma_coisa_do_mesmo_edital` (~516-523), que conta marcos pela regex `declarado (...)`: contar pelas descrições dos marcos

### A entrada

- [ ] T016 [US3] Tirar das fixtures o `status` que existia só para não disparar o `UX-002`: `status_do_periodo="EM_ANDAMENTO"` em `backend/tests/conftest.py` (~252-267, `edital_c`), `backend/tests/fixtures/supervisao.py` (~27-91), `backend/tests/interface/test_supervisao.py` (~199, `processo_limpo`) e `backend/tests/acceptance/test_supervisao_do_processo.py` (~65, ~78) (**EXISTENTES**). Mover o `CONCLUIDO` da origem de `backend/tests/integration/editais/test_reaproveitamento.py` (~185; a asserção de ~645-652) do `PUT` para o ORM, onde a docstring de `_vincular_anexo_e_fechar_cronograma` já o espera. **Antes da T017**: ela os recusaria
- [ ] T017 [US3] Recusar a fase declarada no domínio em `backend/processo_seletivo/editais/application/draft.py` (**EXISTENTE**, `replace_draft` ~379-396), `FR-737`: `status` aceita `PLANEJADO` e `CANCELADO`; os outros dois, recusa com *"A fase do Evento é derivada das datas; só o cancelamento é declarado."* O `ChoiceField` de `backend/processo_seletivo/editais/api/serializers.py` (**EXISTENTE**, ~185-188) passa a oferecer os mesmos dois valores. E a tela normaliza o que só herdou, em `backend/processo_seletivo/interface/forms.py` (**EXISTENTE**, `eventos_persistidos` ~1309-1339): o que não for `CANCELADO` vai como `PLANEJADO` (`research.md`, `R-4`)
- [ ] T018 [US3] Prender a entrada: pela API, `EM_ANDAMENTO` e `CONCLUIDO` recusados com a razão e `CANCELADO` aceito, em `backend/tests/contract/test_edital_draft_api.py` (**EXISTENTE** — acrescente); e reescrever `backend/tests/interface/test_round_trip_do_rascunho.py` (**EXISTENTE**, ~357), que prende o `EM_ANDAMENTO` sobrevivendo à tela: passa a prender a **normalização** para `PLANEJADO`, e o `CANCELADO` sobrevivendo

### O aviso da Etapa sem Evento

- [ ] T019 [P] [US3] Acrescentar o aviso em `backend/processo_seletivo/editais/domain/validation.py` (**EXISTENTE**, `_coerencia_das_etapas` ~1238, e a chamada em `validate_for_publication` ~1355-1429), `FR-739`, `UX-086`: `ValidationFinding(Severity.WARNING, "stage_without_schedule_event", ...)` no caminho `/stages/id=<uuid>/scheduleEventId`, **só** quando o `ato` for o de publicação — a função passa a receber o `ato`, como `_eventos_vencidos`. **Código próprio**, e não `field_constraint_violated` (`research.md`, `R-5`). Mensagem conforme o contrato, seção 4
- [ ] T020 [US3] Agrupar as repetidas em `backend/processo_seletivo/interface/templatetags/interface_extras.py` (**EXISTENTE**, `RESUMO_DAS_REPETIDAS` ~335-372): várias Etapas sem Evento viram uma linha
- [ ] T021 [US3] Prender o aviso: em `backend/tests/unit/editais/` (**NOVO** arquivo `test_etapa_sem_evento.py`): aviso no ato de publicação, **ausente** no ato de Retificação, nunca impeditivo, e o código fora do conjunto dos impeditivos (o invariante de `test_invariantes_da_declaracao_unica.py` continua verde); em `backend/tests/interface/test_compor.py` (**EXISTENTE** — acrescente): o aviso aparece na etapa *Etapas*, na Revisão e em *"Validação do conteúdo"* de um Edital **publicado**, como *"Aviso"*. Corrigir `backend/tests/unit/editais/test_etapas.py::test_a_pontuada_sem_nota_nenhuma_e_legitima` (~162-164), que filtra por caminho e não por severidade: passa a filtrar impeditivos

### O catálogo encolhe

- [ ] T022 [US3] Retirar o `UX-001` e o `UX-002` de `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**), `FR-738`, `FR-739`, `FR-744`: `UX_001`, `UX_002` e as entradas em `ESPECIES` (dez → **oito**); `etapas_sem_marco`, `divergencias_temporais`, `posicao_temporal`, `COERENTES`, `FRASES_DA_POSICAO`, as três constantes de posição e `_dia`; as entradas de `ROTULOS_DO_DESTINO`, `destino_de` e `alcance`; `ENCAMINHAMENTOS_QUE_ALTERAM_O_EDITAL` passa a `{UX_046}`; as chamadas em `sinais`; o `__all__`. **Manter** `nome_da_etapa`, `_citado` e o import de `EventoCronograma`. Reescrever as docstrings que dizem *"cinco"* e a de `alcance_no_edital`, cuja premissa (*"continua podendo Retificar"*) era falsa (spec, caso-limite)
- [ ] T023 [US3] Apagar e reescrever os testes do comportamento retirado, **caso a caso contra a T002**, `R-8`: em `backend/tests/integration/supervisao/test_sinais.py` apagar os blocos do `UX-001` (~38-71) e do `UX-002` (~74-175, com `COMBINACOES` e `edital_da_tabela_verdade`), e reescrever `test_o_edital_parado_nao_silencia_as_especies_anteriores` (~1010-1040) montando um `UX-004` ou `UX-046`; em `backend/tests/interface/test_supervisao.py` apagar a fixture `edital_divergente` e reescrever os casos de ~271, ~374, ~407, ~430 e ~572; em `backend/tests/integration/supervisao/test_autorizacao.py` (~143-172) trocar o `UX_001` por uma espécie que exista; em `backend/tests/unit/interface/test_supervisao.py` (~10) **dez → oito**, com a docstring dizendo quais saíram e por quê. Nenhum caso a mais do que a `R-8` nomeia sem registro na `T036`
- [ ] T024 [US3] Acrescentar o teste do `UX-002` espúrio em `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE** — acrescente): um Edital publicado **pela tela** — `PLANEJADO` em todos os Eventos —, com Evento passado, corrente e futuro, não produz sinal algum de Cronograma — o teste 6 da proposta
- [ ] T025 [US3] Marcar a precedência nas specs de origem, `FR-745`: em `specs/022-supervisao-do-processo/spec.md` (**EXISTENTE**) a `D-004`, a `FR-023`, a `FR-027`, o `UX-001`, o `UX-002`, a `FR-030`, o `UX-005` e a `FR-033`, e no bloco da `FR-024` a nota de que a `FR-565` foi substituída pela `FR-744` — **sem apagar** a tabela de 19/09; em `specs/038-painel-de-conducao/spec.md` (**EXISTENTE**) a `FR-561`, a `FR-565` e o `UX-064`. Cada marca diz *"substituída"* ou *"refinada"*, com a data e o ponteiro para a `045`, na forma que a `FR-024` recebeu em 19/09. **Não** trocar `FR-`/`UX-` por texto: o teste de citações precisa continuar resolvendo
- [ ] T026 [US3] Mudar o guarda do catálogo em `backend/tests/acceptance/test_supervisao_do_processo.py` (**EXISTENTE**): `test_o_requisito_que_fecha_o_catalogo_nomeia_as_especies_que_o_produto_apresenta` passa a ler o bloco da `FR-744` em `specs/045-conducao-confiavel-processo/spec.md` (até `FR-745`) e continua exigindo *"SUBSTITUÍDA"* no bloco da `FR-024` da `022`. **Armadilha**: o texto riscado da `FR-024` contém `UX-001`, e compará-lo com oito espécies reprova (`R-8`). E tirar a asserção de *"sem marco no cronograma"* do percurso de aceitação (~108-109)

**Checkpoint**: `C5` e `C6` fechadas. O catálogo tem oito espécies, e nenhuma delas é ruído de Cronograma.

---

## Phase 6: US4 — O sinal que fica diz o que conta e a quem pedir (P4)

**Goal**: todo sinal cujo ato o leitor não pratica diz a quem pedir; o `UX-046` sai onde ninguém pode
retificar; a cobertura conta participantes; toda medida tem unidade.

**Independent Test**: Gestor sem retificar diante do `UX-046`; Auditor no sorteio e na ocupação;
Publicador diante de ato obsoleto na prévia; presidência comparando o `UX-003` com a lista da distribuição.

**Depende da `US3`** (portão 4).

### A condução

- [ ] T027 [US4] Dar ao `Sinal` a condução, em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**), e exibi-la em `backend/processo_seletivo/interface/templates/interface/_sinal.html` (**EXISTENTE**) quando não há destino, `FR-740`: para o `UX-046` a quem não pode retificar, **exatamente** `CONDUCAO_DA_RETIFICACAO`. Ela vive hoje em `interface/views.py` (~4362-4365): **extrair** a constante e sua base para onde `views.py` e `supervisao.py` a alcancem, e nunca redigi-la de novo (`037`, `FR-543`). Quem pode retificar recebe o caminho e **não** a frase (`037`, `FR-544`)
- [ ] T028 [US4] Separar, em `admite_encaminhamento` de `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**, ~1240-1259), **falta de permissão** de **situação que não admite**, `FR-741`, `D-003`: a primeira produz o sinal com a condução da T027; a segunda — Edital fora do estado publicado, ou Processo em estado final — **não produz o sinal**. Hoje as duas caem no mesmo `None`
- [ ] T029 [US4] Acrescentar a condução nas telas de destino que recebem quem só consulta, **pelo mecanismo único** (`frase_do_aviso`), conforme o contrato, seção 2, e `research.md`, `R-7`: `backend/processo_seletivo/interface/templates/interface/sorteio.html` para o Auditor (bases gestão e presidência, *"que o emita"* — a mesma que a ordenação já monta em `views.py` ~5827-5831); `ocupacao.html` para o Auditor (*"que a apure"*); `previa_de_publicacao.html` para o Publicador diante de ato obsoleto (gestão e presidência, *"que emita o ato sucessor"*). A frase nasce na view de cada tela, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**), e só aparece a quem **não** pode agir. **A peça do recurso fica como está**: ao Julgador impedido ela já diz o impedimento e quem pode apreciar, e *"peça a alguém com a permissão de julgar"* seria falso para quem tem a permissão (`037`, `FR-544`)
- [ ] T030 [US4] Prender a condução — o teste 8 da proposta: em `backend/tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py` (**EXISTENTE** — acrescente): o Gestor sem retificar recebe a frase e nenhum caminho; o Elaborador recebe o caminho e nenhuma frase; num Edital **encerrado**, nenhum dos dois recebe o sinal. E em `backend/tests/interface/` (**NOVO** arquivo `test_conducao_nas_telas_de_destino.py`): as três telas da T029, cada uma com o leitor que não pode (a frase aparece) e o que pode (a frase não aparece)

### A medida

- [ ] T031 [US4] Contar a cobertura sobre participantes em `backend/processo_seletivo/avaliacoes/application/selectors.py` (**EXISTENTE**, `resumo_da_etapa` ~204-241), `FR-742`: com `panorama`, restringir a agregação a `panorama["participantes"]` — o **mesmo** conjunto da lista; sem panorama, aplicar uma restrição **recebida por parâmetro** — o painel passa `restringir_a_participantes(..., prefixo="")` — porque `avaliacoes` não importa `resultados` (ciclo; `research.md`, `R-6`). Em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**, ~686), passar a restrição
- [ ] T032 [US4] Casar o número com a lista em `backend/processo_seletivo/avaliacoes/application/selectors.py` (**EXISTENTE**, `inscricoes_da_etapa`) e `backend/processo_seletivo/interface/templates/interface/distribuicao.html` (**EXISTENTE**, ~46-60): um filtro `carente` — `atribuidas < previstas`, **inclusive zero** — para o link *"sem avaliador suficiente"*; `incompleta` continua existindo; *"todas"* e a ficha passam a mostrar os participantes, que é o que a lista lista
- [ ] T033 [US4] Dar unidade à medida, `FR-743`, `UX-087`: `Medida` ganha `unidade` em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**), declarada por espécie — *inscrições* no `UX-003` e no `UX-063`, *recursos* no `UX-064`, *recortes* no `UX-046` —, com o plural pelo denominador; `_sinal.html` a exibe; a mensagem do `UX-046` deixa de repetir os dois números da medida
- [ ] T034 [US4] Prender a medida — o teste 7 da proposta: em `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE** — acrescente) uma Etapa com uma inscrição eliminada na anterior, uma aguardando o resultado da anterior e uma fora do corte: o denominador do `UX-003` conta **só** os participantes, e é **igual** ao da distribuição montada com panorama no mesmo cenário; `test_inscricao_sem_avaliador_e_carente_e_permanece_no_denominador` continua verde (`022`, `FR-033`); e uma Etapa cujas inscrições foram **todas** eliminadas na anterior **não** produz `UX-003` — *"0 de 0"* não é condição (spec, caso-limite). Em `backend/tests/interface/test_distribuicao.py` (**EXISTENTE** — acrescente): o número *"sem avaliador suficiente"* e a lista que ele abre têm o mesmo tamanho, **inclusive** com participante sem avaliador nenhum. Conferir `backend/tests/performance/test_resumo_da_etapa.py` **sem mudar o teto** (`<= 6`), e `test_fronteira.py` sem mudar o orçamento

**Checkpoint**: `C4` fechada, e o `RC-82` também. Refeita a medição de 20/09, zero sinais mudos.

---

## Phase 7: Polimento e conferência

- [ ] T035 Percorrer os cinco percursos de `specs/045-conducao-confiavel-processo/quickstart.md` (**EXISTENTE**) **pela interface**, com as identidades separadas, e registrar o resultado de cada passo em `specs/045-conducao-confiavel-processo/antes-da-conducao.md` (**EXISTENTE**, criado em T002), ao lado do "antes": `SC-269` a `SC-274`. Recurso pelo portal com `PORTAL_IDENTIDADE_DEMO=true`, código de acesso nos logs do servidor
- [ ] T036 Conferir **caso a caso** os testes alterados contra o "antes" da T002, e **recontar** por arquivo. Cada caso apagado ou reescrito ganha uma linha com o motivo; caso alterado que a `R-8` não previa ganha uma linha dizendo por que não previa
- [ ] T037 Escrever `specs/045-conducao-confiavel-processo/rastreabilidade.md` (**NOVO**): uma linha por `FR-`, `SC-` e `UX-` **em negrito** na spec, com o nome real da função de teste; **uma linha por caso-limite** da spec, com o teste que o prende — eles não têm identificador e nenhuma ferramenta os cobra; o do *"Julgador impedido continua vendo o `UX-064`"* é comportamento da `038`, e a linha aponta o teste que já o prende; as nove linhas de *"Os testes de regressão da proposta"*; e os testes alterados da T036. Rodar `cd backend && make lint check test-pg` e registrar a contagem final. As promessas que se conferem **lendo o diff**: nenhuma capacidade nova, nenhuma migration, nenhum conteúdo publicado reescrito, nenhum valor tirado do `choices` do `status`, nada apagado de spec anterior — só marcado
- [ ] T038 Depois do merge, e não antes: marcar `RC-78` a `RC-82` como resolvidos em `doc/auditoria-de-consolidacao-2026-09-26.md` (**EXISTENTE**) — e o `RC-84` como **parcialmente**, porque as formas de prazo e a exportação vazia ficaram fora —, na forma que o `RC-54` recebeu no #178

---

## Dependências

```
Phase 1 (T001–T002) ──► Phase 2 (T003)
                            │
                            ├──► US1 (T004–T007)   🎯 MVP
                            │       │
                            │       ▼   supervisao.py em comum
                            ├──► US2 (T008–T011)
                            │       │
                            │       ▼   supervisao.py em comum
                            └──► US3 (T012–T026)
                                    │
                                    ▼   portão 4
                                 US4 (T027–T034) ──► Polimento (T035–T038)
```

**US1, US2 e US3 são independentes em comportamento, e não em arquivo**: as três mexem em
`interface/supervisao.py`. Correm em sequência na mesma worktree; em worktrees separadas, colidiriam
no merge sem ganho.

### Dentro das fases

- **T004 → T005 → T006 → T007**: a escolha, a view, o template, o teste.
- **T008 → T010** e **T009 → T011**: o sinal e a contagem são arquivos diferentes; T011 leva `[P]`
  contra T008 e T010.
- **T012** leva `[P]`: `calendario.py` e o teste dele não encostam em nada da fase.
- **T016 → T017 → T018**: as fixtures deixam de mandar o valor **antes** de ele ser recusado.
- **T019** leva `[P]`: `validation.py` não encosta em `supervisao.py`.
- **T022 → T023 → T024**: tirar o código, depois os testes que o prendiam, depois o teste do
  espúrio — que só é significativo com o `UX-002` fora.
- **T025 → T026**: a marca na spec antes do teste que a lê.
- **T027 → T028 → T030** e **T029 → T030**: a condução no sinal, a separação de situação, os testes.
- **T031 → T032 → T034** e **T033 → T034**.
- **T036 e T037 depois de todos os percursos.** T038 depois do merge.

### Oportunidades de paralelismo

Poucas, e é o esperado numa feature que corrige um módulo: **T011**, **T012** e **T019** — cada uma
num arquivo que nenhuma outra tarefa aberta toca.

---

## Estratégia de entrega

**MVP**: a `US1`. Quatro tarefas, e fecha a única condicionante S3 que não precisa de decisão nenhuma
— o painel deixa de dizer *"tudo em dia"* a quem enxerga parte.

**Depois**: a `US2` (a outra S3), a `US3` (o maior efeito sobre sinal e ruído, e o maior churn de
teste) e a `US4`, nesta ordem. Cada fase termina verde em `make test-pg` antes da seguinte.

**O que não se faz**:

- acrescentar `scheduleEventId` ou `status` à Retificação para dar destino aos sinais — a convergência
  vetou, e a `D-003` decide o contrário;
- redigir à mão qualquer frase de condução — há um mecanismo, e ele é público para que não nasça um
  segundo;
- ajustar número de orçamento de consulta até passar — nenhum orçamento desta feature deve mudar, e
  se mudar, a razão entra escrita ao lado;
- apagar teste para ficar verde sem linha na T036.
