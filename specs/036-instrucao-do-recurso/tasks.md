---

description: "Task list — 036 · Instrução do recurso"
---

# Tasks: Instrução do recurso

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim, e são obrigatórios.** Esta feature **concede acesso a dado pessoal** — a primeira
da série que o faz. Requisito sem linha na matriz é requisito que ninguém sabe se entrou, e aqui o
que não se sabe é *quem passou a ver o quê*.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: arquivos diferentes, nenhuma dependência aberta. **Se uma tarefa ganhar arquivo depois, o
  `[P]` sai** — foi assim que a regra se quebrou na `035`, em silêncio.
- **[US1] [US2] [US3]**: a história. As fases 1, 2 e a de polimento não têm.
- **NOVO / EXISTENTE**: onde diz existente, **acrescente ao fim; nunca reescreva**. A `030`
  sobrescreveu `test_round_trip_do_rascunho.py` e oito regressões sumiram sem a suíte ficar vermelha.

---

## Os quatro portões

1. **`T002` roda ANTES de qualquer edição.** Grava a contagem da suíte e **o que o único caso
   alterado afirma hoje** — `research.md` `R-6` o nomeia. A `034` previu oito casos e entregou doze;
   a conta se refaz contra a implementação, e sem o "antes" não há contra o que comparar.

2. **`T006` é a migration, e ela tem DUAS camadas.** A tabela do ato nasce **append-only**, e a
   Constituição exige trigger **e** privilégio ausente — nenhuma das duas é contornável em
   desenvolvimento. **Depois dela, `make preparar` roda de novo**, e o total da saída `N de M` sobe
   de **31 para 32**. Quem não reprovisionar vai ver falha de permissão num arquivo sorteado, longe
   da causa.

3. **`T021` e `T024` são contraprovas OBRIGATÓRIAS**, e não conferências de rotina:
   - o **mesmo julgador** abrindo **outro** recurso — é o que distingue **ato** de **permissão**;
   - o **conteúdo do parecer** não aparecendo em registro nenhum da trilha.

   Se a primeira falhar, o que se construiu foi uma permissão com outro nome. Se a segunda falhar,
   criou-se a segunda cópia do dado sensível que a `018` existe para impedir.

4. **`T026` recontá os casos alterados, caso a caso.** Um teste pode manter o número de asserções e
   trocar o que afirma.

---

## Phase 1: Setup e medição do "antes"

- [ ] T001 Preparar a worktree: copiar `backend/.env` do checkout principal (**EXISTENTE lá, ausente aqui** — é gitignorado), trocar `DB_NAME` e `POSTGRES_DB` por um nome próprio, rodar `uv sync --extra dev` e `make preparar` em `backend/`, conferindo que a saída termina em **`N de 31`** com N diferente de zero. **Guarde esse número**: a `T006` o muda
- [ ] T002 Medir e gravar o "antes" em `specs/036-instrucao-do-recurso/antes-da-instrucao.md` (**NOVO**): a contagem da suíte (`make test-pg`), e **o que afirma hoje** o único caso que `research.md` `R-6` nomeia — `tests/interface/test_proveniencia_do_recurso.py::test_quem_so_julga_alcanca_o_edital_e_le_o_que_lhe_falta` —, citado. Registre também os **dois vizinhos que permanecem**, porque são a contraprova de que a feature não ampliou nada por engano. **Esta tarefa roda antes de qualquer edição de código**
- [ ] T003 Confirmar por varredura, em `specs/036-instrucao-do-recurso/antes-da-instrucao.md` (**EXISTENTE**, criado em T002), as três medições de que a feature depende: que o parecer **já está carregado** na porta da peça; que a auditoria **já registra leitura** (o padrão da `031`); e que o acompanhamento **já exibe o motivo**. As três estão em `research.md`; esta tarefa é o "confirme, não assuma" que a `035` provou valer

**Checkpoint**: o "antes" está gravado, e as três premissas foram reconferidas contra o código.

---

## Phase 2: Fundação — o ato, e a proteção dele

**Purpose**: a entidade e o alcance. **Bloqueia US2 e US3.** A `US1` não depende desta fase.

- [ ] T004 Criar a entidade do **ato de instrução** em `backend/processo_seletivo/recursos/models.py` (**EXISTENTE** — acrescente ao fim, junto de `Recurso`, `JuizoDeAdmissibilidade` e `DecisaoRecurso`), conforme [data-model.md](data-model.md): guarda o recurso alcançado, o que foi anexado **por espécie**, quem instruiu e quando. **Não guarda cópia do documento, nem o texto do parecer, nem lista de quem pode ver**
- [ ] T005 Escrever o ato em `backend/processo_seletivo/recursos/application/instruir.py` (**NOVO**) — `FR-527` —: append-only, com autor e instante, na disciplina dos outros atos do produto. Instruir de novo **acrescenta**, e não substitui
- [ ] T006 Criar a migration em `backend/processo_seletivo/recursos/migrations/` (**NOVO**) com as **duas camadas** de proteção append-only — trigger **e** privilégio ausente —, como as outras 31 tabelas. Depois dela, rodar `make preparar` **de novo** e conferir que a saída passou a dizer **`N de 32`**
- [ ] T007 Derivar o alcance em `backend/processo_seletivo/recursos/application/instruir.py` (**EXISTENTE**, criado em T005): quem julga **aquele** recurso, **enquanto ele não estiver decidido** (`FR-528`, `FR-529`). **Derivado, e nunca persistido como lista** — lista de pessoas é permissão com outro nome, e é o que a `FR-530` proíbe
- [ ] T008 Prender o alcance em `backend/tests/integration/recursos/test_alcance_da_instrucao.py` (**NOVO**): abre com o ato; **não** alcança outro recurso; **fecha** com a decisão; e o registro permanece depois de fechar

**Checkpoint**: o ato existe, é append-only, está protegido nas duas camadas, e o alcance nasce e
morre onde deve.

---

## Phase 3: US1 — O candidato lê a razão (P1) 🎯 MVP

**Goal**: o titular lê o parecer enquanto o prazo corre.

**Independent Test**: eliminar por nota abaixo da mínima, divulgar, e ler o parecer pelo portal.

**Não depende da fase 2**: o parecer do titular não passa por instrução nenhuma.

- [ ] T009 [US1] Levar o parecer ao acompanhamento em `backend/processo_seletivo/portal/views.py` (**EXISTENTE**): o da avaliação que **fundamenta o resultado contestável** (`FR-523`, `D-002`), e o do registro histórico quando houve reabertura
- [ ] T010 [US1] Exibi-lo em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html` (**EXISTENTE**) **ao lado do motivo, e não no lugar dele** (`FR-525a`). O motivo é a regra aplicada ao número; o parecer é a razão que a pessoa escreveu. Identifique-o como a fundamentação daquele resultado
- [ ] T011 [US1] Condicionar às **duas** condições da `FR-522` — prazo recursal aberto **ou** recurso dele ainda não decidido (`D-001`) —, e **dizer por que saiu** quando as duas se encerram (`FR-524`), em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html` (**EXISTENTE**). Sumir em silêncio faria a pessoa pensar que perdeu algo — é a diferença entre a feature e um defeito
- [ ] T012 [US1] Dizer que **não há parecer** quando não há (`FR-525`), em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html` (**EXISTENTE**). A obrigatoriedade depende do caráter da Etapa e da forma da avaliação, e a ausência é real
- [ ] T013 [US1] **Emendar o comentário** de `backend/processo_seletivo/portal/templates/portal/acompanhamento.html` (**EXISTENTE**) que hoje diz *"Nada aqui é de terceiro: nenhum nome, nenhuma nota alheia, nenhum parecer, nenhuma avaliação"*. O sujeito dele é **de terceiro**, e a emenda MUST **dizer a distinção** — parecer de terceiro continua proibido, parecer do próprio titular é o que a feature entrega. **Não apague a frase**: ela é a regra escrita onde alguém a lê antes de mexer
- [ ] T014 [US1] Prender a `US1` em `backend/tests/portal/test_parecer_do_titular.py` (**NOVO**): o titular lê; lê **ao lado** do motivo; **continua lendo enquanto o recurso dele corre, mesmo com o prazo fechado**; não lê depois de as duas condições se encerrarem, **e a tela diz por quê**; não lê quando não há, **e a tela diz**; e **outro candidato não alcança nada** (`FR-526`, `FR-535`, `SC-186`). Inclua o caso do **escopo institucional divergente**, que recebe a resposta uniforme (`FR-536`)

**Checkpoint**: **este é o MVP.** Quem foi eliminado sabe por quê, e pode recorrer com fundamento.

---

## Phase 4: US2 — Quem julga recebe a prova (P2)

**Goal**: a autoridade instrui; quem só julga passa a ver o que foi instruído.

**Independent Test**: instruir e conferir, como alguém que **só** julga, que a prova aparece — sem
que nenhuma permissão tenha mudado.

**Depende da fase 2**, e da `US1` apenas na ordem de entrega: primeiro o candidato recorre sabendo
contra o quê, depois quem julga decide vendo o quê.

- [ ] T015 [US2] Oferecer o ato de instrução na peça, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**), a quem tem a **base composta** que a `033` já sabe exigir — gestão **ou** presidência. **Nenhuma capacidade nova** (`FR-530`)
- [ ] T016 [US2] Exibir o que foi instruído em `backend/processo_seletivo/interface/templates/interface/recurso.html` (**EXISTENTE**): o parecer atacado, e o caminho para o documento citado **por referência** (`FR-531`). **Exiba o que a porta já carregou** — `research.md` `R-3` — e **não** busque de novo: há teste de orçamento de consulta nesta tela
- [ ] T017 [US2] Distinguir os **três** estados da tela em `backend/processo_seletivo/interface/templates/interface/recurso.html` (**EXISTENTE**) — `FR-532`: (a) **nada instruído** → o que falta e a quem pedir, na formulação que o produto já pratica; (b) **instruído e não decidido** → a prova; (c) **houve instrução e o acesso terminou** → que houve, e que o alcance se encerrou. **O terceiro é o que a primeira redação não tinha**: sem ele a tela diz *"nada foi instruído"* a quem viu a prova ontem, e isso é falso sobre um ato que aconteceu. **Em nenhum dos três ofereça caminho que aquele ator não alcança** — é a garantia da `033`, e esta é a tarefa que mais facilmente a desfaz
- [ ] T018 [US2] Prender o que quem julga passa a ver, em `backend/tests/interface/test_instrucao_na_peca.py` (**NOVO**): sem instrução, lê o que falta; com instrução, lê o parecer e alcança o documento; **depois de decidido, lê que houve instrução e que o alcance terminou**; e a tela **não** oferece o que ele não alcança (`FR-535`, `FR-536`). Acrescente a asserção da `FR-531a`: o documento é alcançado **por referência**, e **nada foi duplicado** — conferido no armazenamento, e não só no caminho que a tela aponta
- [ ] T019 [US2] Atualizar o **único** caso alterado, em `backend/tests/interface/test_proveniencia_do_recurso.py` (**EXISTENTE** — altere **só** `test_quem_so_julga_alcanca_o_edital_e_le_o_que_lhe_falta`). **Os dois vizinhos permanecem** e são a contraprova de que nada se ampliou por engano
- [ ] T020 [US2] Conferir que o **orçamento de consulta** da tela não mudou, em `backend/tests/interface/test_proveniencia_do_recurso.py` (**EXISTENTE**, o caso que já existe). Exibir o já carregado não custa consulta; se o número subiu, a `T016` buscou de novo
- [ ] T021 [US2] **CONTRAPROVA OBRIGATÓRIA** — o mesmo julgador, **outro** recurso da mesma Etapa, em `backend/tests/integration/recursos/test_alcance_da_instrucao.py` (**EXISTENTE**, criado em T008 — acrescente): ele **não** alcança nada por causa da instrução anterior (`SC-185`). **Se alcançar, o que se construiu foi uma permissão**, e a feature está errada no seu ponto central

**Checkpoint**: o `ACH-43` fecha — o último `P0`.

---

## Phase 5: US3 — A instituição sabe o que foi mostrado a quem (P3)

**Goal**: o ato e o acesso ficam registrados; o conteúdo, nunca.

**Independent Test**: instruir, exercer o acesso, e encontrar os dois registros na trilha — sem o
texto do parecer em lugar nenhum.

- [ ] T022 [US3] Registrar o **ato** de instrução (`FR-533`) em `backend/processo_seletivo/recursos/application/instruir.py` (**EXISTENTE**): autor, instante, recurso alcançado e o que foi anexado **por espécie**
- [ ] T023 [US3] Registrar o **acesso exercido** (`FR-534`) em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**), **seguindo o padrão da `031`** — a prévia da exportação, com revisão nula e uma razão que descreve o **escopo** do que foi visto. `research.md` `R-2` traz a forma; não invente uma segunda
- [ ] T024 [US3] **CONTRAPROVA OBRIGATÓRIA** — o conteúdo **não** vaza para a trilha, em `backend/tests/integration/recursos/test_trilha_da_instrucao.py` (**NOVO**): o ato e o acesso aparecem; **o texto do parecer, o conteúdo do documento e a fundamentação de quem recorreu não aparecem em registro nenhum** (`SC-184`). É a regra que a `018` já pratica, e acrescentar registros é exatamente como se a quebra

**Checkpoint**: o acesso é defensável — há quem, quando, e por decisão de quem.

---

## Phase 6: Polimento e conferência

- [ ] T025 Percorrer os **cenários 1 e 2** de `specs/036-instrucao-do-recurso/quickstart.md` (**EXISTENTE**) pelo portal, com o seletor de identidade do candidato — inclusive as três contraprovas do cenário 1 — é o `SC-182`. **O código de acesso do portal sai no terminal do servidor**
- [ ] T026 Percorrer os **cenários 3 e 4** de `specs/036-instrucao-do-recurso/quickstart.md` (**EXISTENTE**) pela interface administrativa, **inclusive o passo 5 do cenário 3** — o mesmo julgador em outro recurso, que é o que distingue ato de permissão. O cenário 3 é o `SC-183`
- [ ] T027 Percorrer o **cenário 5** de `specs/036-instrucao-do-recurso/quickstart.md` (**EXISTENTE**) — a trilha, com a contraprova do conteúdo que não pode aparecer
- [ ] T028 Conferir **caso a caso** os testes alterados contra o "antes" gravado em `specs/036-instrucao-do-recurso/antes-da-instrucao.md` (**EXISTENTE**, criado em T002), e **recontar**: `research.md` `R-6` prevê **um**, e a `034` previu oito e entregou doze porque um código vivia num dicionário compartilhado. Se forem mais, registre por que
- [ ] T029 Escrever `specs/036-instrucao-do-recurso/rastreabilidade.md` (**NOVO**): uma linha por `FR-`, uma por `SC-`, **uma por teste alterado com o motivo** — e, porque esta feature concede acesso a dado pessoal, **uma seção que responde, por escrito: quem passou a ver o quê, por quanto tempo, e o que ficou registrado**
- [ ] T030 Rodar `cd backend && make lint check test-pg` e registrar a contagem final em `specs/036-instrucao-do-recurso/rastreabilidade.md` (**EXISTENTE**, criado em T029). `test-pg` e **nunca** `test`; `lint` são **dois** passos. **Esta feature tem migration**: o `makemigrations --check` prova que a migration cobre o modelo, e **não** prova "nada mudou". As promessas que se conferem lendo o diff são **nenhuma capacidade nova, nenhum papel novo e nenhum parecer alterado** (`FR-530`, `FR-537`, `SC-187`)

---

## Dependências

```
Phase 1 (T001–T003)
      │
      ├──────────────────────────► US1 (T009–T014)  🎯 MVP   ← não depende da fase 2
      │
      └──► Phase 2 (T004–T008) ──► US2 (T015–T021) ──► US3 (T022–T024)
                                          │                    │
                                          └────────┬───────────┘
                                                   ▼
                                        Polimento (T025–T030)
```

**A `US1` é independente da fase 2**, e é por isso que ela é o MVP: o parecer do titular não passa
por instrução nenhuma. Se a fase 2 travar, a `US1` entrega sozinha — e ela é a que fecha o `ACH-42`.

### Dentro das fases

- **T004 → T005 → T006 → T007** — a entidade antes do ato, o ato antes da proteção, a proteção antes
  do alcance. E **T006 antes de qualquer teste que toque a tabela**: sem reprovisionar, a falha
  aparece longe da causa.
- **T005 → T007 → T022** são o **mesmo arquivo**, e por isso **nenhuma leva `[P]`**.
- **T009 → T010 → T011 → T012 → T013** são o **mesmo template**, com uma exceção: a `T009` é a view.
  Nenhuma leva `[P]` — as quatro últimas se empilham no mesmo arquivo.
- **T008 → T021** são o mesmo arquivo, criado em T008.
- **T016 → T020** — o orçamento se confere depois de a tela mudar.
- **T025 → T026 → T027** — os percursos são cadeia, e não conjunto: a `T027` lê o que a `T026` escreve.
- **T028 depois de todos os percursos** — percurso que ache defeito muda o estado que ela confere.

### Oportunidades de paralelismo

| Tarefas | Por que podem |
|---|---|
| US1 inteira · fase 2 | canais diferentes, e a `US1` não depende do ato |

**Nenhum percurso é paralelo, e a razão é uma cadeia:** a `T027` lê a trilha **da instrução que a
`T026` pratica**. Rodá-las fora de ordem faz a `T027` procurar registro que ainda não existe e
encontrar a trilha vazia — que é um verde falso, e não uma falha.

*A primeira redação marcava `T025 · T027` como paralelas e explicava ao contrário: dizia que a `T026`
ficava de fora "porque pratica atos que mudam o estado que a T027 lê". Isso é a razão de a `T027` vir
**depois**, e não de a `T026` não ser paralela.*

---

## Estratégia de entrega

**MVP = fase 1 + US1.** O candidato eliminado passa a saber por quê — e isso fecha o `ACH-42`
sozinho, sem entidade nova, sem migration e sem conceder acesso a ninguém.

**A fase 2 e a `US2` fecham o `ACH-43`, que é o último `P0`.** Elas trazem a migration e o acesso, e
é nelas que está todo o risco desta feature.

**A `US3` não é opcional.** Sem ela, a instrução é uma ampliação de acesso sem rastro — que é a
`FR-105` da `018` violada com outro nome. Se ela ficar para depois, a `US2` **não** deve entrar.
