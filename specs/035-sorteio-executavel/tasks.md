---

description: "Task list — 035 · Sorteio executável"
---

# Tasks: Sorteio executável

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim, e são obrigatórios.** A feature toca o caminho que constitui ato publicado, e
promete que **nenhum sorteio já realizado muda de resultado**. A rastreabilidade é verificada por
teste neste projeto, e requisito sem linha na matriz é requisito que ninguém sabe se entrou.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: pode correr em paralelo — **arquivos diferentes e nenhuma dependência de tarefa aberta**.
  Tarefa que **acrescenta** a um arquivo que outra **cria** não é paralela.
- **[US1] [US2] [US3]**: a história. As fases 1, 2 e a de polimento não têm.
- **NOVO / EXISTENTE**: toda tarefa diz o que o arquivo é. Onde diz **EXISTENTE**, acrescente ao fim
  — **nunca reescreva**. A `030` sobrescreveu `test_round_trip_do_rascunho.py` e oito regressões
  sumiram sem a suíte ficar vermelha.

---

## Os três portões

**Nenhum é formalidade. Cada um existe porque o projeto já pagou por não tê-lo.**

1. **`T002` roda ANTES de qualquer edição**, e grava **três** coisas: a contagem da suíte, o retrato
   do acervo, e a **semente, a ordem e o manifesto de todo sorteio já realizado**. A `FR-519` e a
   `SC-179` prometem que nenhum deles muda de resultado — e essa prova **não se faz depois**. Ordem
   sorteada publicada é ato; um resultado que mudasse em silêncio seria a pior falha possível desta
   feature, e a única que ninguém veria.

2. **`T004` é PORTÃO DE MEDIÇÃO**, e vem antes de escolher onde a sexta guarda vive. A `FR-514`
   proíbe que ela torne qualquer Edital do acervo irretificável, e há conteúdo publicado que **nunca
   passou** por esta conferência. **Levante quantos Editais do acervo têm ocorrência fora da forma.**
   Se houver algum, o lugar da guarda muda — e isso se decide **com o número na mão**, não depois de
   escolher.

3. **`T024` conserta as fixtures, e nunca a regra.** As três estão nomeadas em `research.md` `R-6`.
   Afrouxar a derivação para procurar o número em qualquer posição criaria ambiguidade:
   `concurso 6100 de 2026` derivaria para **2027**.

---

## Phase 1: Setup e medição do "antes"

**Purpose**: deixar o ambiente de pé e congelar o estado contra o qual a entrega será conferida.

- [ ] T001 Preparar a worktree: copiar `backend/.env` do checkout principal (**EXISTENTE lá, ausente aqui** — é gitignorado), trocar `DB_NAME` e `POSTGRES_DB` por um nome próprio, rodar `uv sync --extra dev` e `make preparar` em `backend/`, conferindo que a saída termina em `N de M` com **N diferente de zero**
- [ ] T002 Medir e gravar o "antes" em `specs/035-sorteio-executavel/antes-do-sorteio-executavel.md` (**NOVO**), em **três** partes: (a) a contagem da suíte (`make test-pg`); (b) o retrato do acervo — por publicação, o resumo do conteúdo canônico, o do documento e o censo dos degraus de elevação; (c) **por sorteio já realizado, a semente, a ordem sorteada e o resumo do manifesto**. A parte (c) é a que a `SC-179` prende, e **só existe agora**. **Esta tarefa roda antes de qualquer edição de código**
- [ ] T003 Inventariar por varredura, em `specs/035-sorteio-executavel/inventario-do-metodo.md` (**NOVO**): todo ponto que **valida** campo do método, todo ponto que **lê** a derivação em prosa, e todo ponto que **trata** a falha da derivação da ocorrência. A classificação sai do `if` que decide, não da leitura da definição da função — foi o que produziu três medições erradas na `033`
- [ ] T004 **PORTÃO DE MEDIÇÃO** — levantar, e registrar em `specs/035-sorteio-executavel/inventario-do-metodo.md` (**EXISTENTE**, criado em T003), **quantos Editais publicados têm ocorrência que não satisfaz a forma exigida**, e quais. Se o número for **zero**, a guarda vai para junto das outras cinco e a `T010` segue como escrita. Se for **maior que zero**, **pare**: o lugar da guarda muda, a `FR-514` é o requisito que governa a escolha, e a decisão é de quem conduz — não de quem implementa. **A fase 2 não começa antes desta tarefa fechar**

**Checkpoint**: o "antes" está gravado — inclusive o dos sorteios já feitos —, a superfície está
contada, e o lugar da guarda está decidido com número.

---

## Phase 2: Fundação — a regra, num lugar só

**Purpose**: garantir que a composição e o motor respondam a mesma coisa. **Bloqueia US1 e US2.**

- [ ] T005 Expor, em `backend/processo_seletivo/sorteios/domain/substituicao.py` (**EXISTENTE**), a pergunta *"esta referência é derivável por esta regra?"* como função consultável, **reutilizando a regra que já existe** e sem duplicá-la (`FR-515`). A derivação continua sendo a mesma função; o que se acrescenta é poder perguntar antes de tentar
- [ ] T006 Prender a igualdade em `backend/tests/unit/sorteios/test_forma_da_ocorrencia.py` (**NOVO**): para o mesmo conjunto de referências — as que derivam e as que não —, a resposta da consulta e o desfecho da derivação **coincidem** (`SC-177`). Compara respostas, e não implementações

**Checkpoint**: existe **uma** resposta para *"esta referência é derivável?"*, e ela é consultável.

---

## Phase 3: US1 — A composição ensina a forma (P1) 🎯 MVP

**Goal**: quem compõe **escolhe** o algoritmo e a fonte, e **lê** o que a ocorrência precisa ser.

**Independent Test**: compor o método inteiro pela interface, sem saber de antemão que a ocorrência
precisa terminar em número, e chegar a um método que roda.

- [ ] T007 [US1] Oferecer o algoritmo e a fonte como **escolha entre os valores publicados** em `backend/processo_seletivo/interface/templates/interface/_marco.html` (**EXISTENTE**), montando as opções a partir do próprio vocabulário — **como `interface/retificacao.py` já faz com o algoritmo** (`FR-507`). Não invente uma segunda maneira de montar a lista
- [ ] T008 [US1] Fazer o mesmo no método **comum do Edital**, em `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html` (**EXISTENTE**). Os dois lugares declaram o mesmo método e precisam ensinar igual
- [ ] T009 [US1] Fazer a escolha **mostrar o valor publicado que não está entre as opções**, identificado como o que foi publicado, nos dois templates e no que os alimenta — `backend/processo_seletivo/interface/forms.py` e os dois de composição (**EXISTENTE**) — `FR-511`. É o preço da `D-002`: o acervo tem valores que a escolha não oferece, e um `select` que os omite faz o campo parecer **vazio** num Edital que declarou. Prenda em `backend/tests/interface/test_metodo_do_marco.py` (**EXISTENTE**, acrescente ao fim)
- [ ] T010 [US1] Acrescentar a ajuda do campo da **ocorrência** em `backend/processo_seletivo/interface/templates/interface/_marco.html` e `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html` (**EXISTENTE**): **forma, exemplo e consequência**, dizendo que ali vai **só a referência** — a fonte já está declarada acima — e **por que** ela precisa terminar em número (`FR-508`). Siga a formulação do campo do instante da ocorrência, citada em `research.md` `R-5`; uma segunda redação para a mesma coisa é o que a `FR-509` proíbe
- [ ] T011 [US1] **Não tocar** o campo *"como a ocorrência decorre da data programada"* — `FR-510`. Esta tarefa é uma conferência, e existe porque é o requisito mais fácil de perder de vista: ele manda **não fazer** o que a auditoria parecia pedir. Registre em `specs/035-sorteio-executavel/inventario-do-metodo.md` (**EXISTENTE**) que o campo continua texto livre e que a varredura de leitores continua devolvendo zero
- [ ] T012 [US1] Prender as duas telas em `backend/tests/interface/test_metodo_do_marco.py` (**EXISTENTE** — **acrescente ao fim**): o algoritmo e a fonte são oferecidos como escolha, nas duas; a ocorrência traz ajuda que diz forma, exemplo e consequência; e o campo da derivação **continua** sendo texto livre
- [ ] T013 [P] [US1] Corrigir o rótulo divergente do campo da derivação — *"Como a ocorrência decorre da data programada"* na composição e *"Como a ocorrência foi escolhida"* na Retificação —, em `backend/processo_seletivo/interface/retificacao.py` (**EXISTENTE**). Dois rótulos para o mesmo campo é o que o Princípio I proíbe; foi achado de passagem em `research.md` `R-3`

**Checkpoint**: **este é o MVP.** A composição ensina, e quem segue a tela produz um método que roda.

---

## Phase 4: US2 — A sexta guarda (P2)

**Goal**: a ocorrência é recusada quando não tem a forma que a regra consome, **no mesmo lugar e
momento** em que os outros cinco campos já são conferidos.

**Independent Test**: declarar a ocorrência em prosa, gravar, e ser recusado com uma frase que nomeia
o campo e a forma — sem precisar chegar à Revisão.

**Depende de US1** apenas na ordem de entrega: ensinar antes de recusar é o que evita que a guarda
pareça arbitrária. Tecnicamente são independentes.

- [ ] T014 [US2] Acrescentar a sexta guarda em `backend/processo_seletivo/editais/domain/perfis.py` (**EXISTENTE**), **ao lado das outras cinco**, consumindo a consulta de T005 (`FR-512`, `FR-515`). A guarda **lê** a regra de `sorteios/domain` e não inverte a direção de dependência que a `021` declarou (`FR-521`). Ela vale para o método próprio do marco **e** para o comum do Edital — há uma função só, e é ela que os dois atravessam
- [ ] T015 [US2] Escrever a frase da recusa em `backend/processo_seletivo/editais/domain/perfis.py` (**EXISTENTE**, mesma função de T014) nomeando **o campo, a forma e por quê** (`FR-513`, `SC-178`), na mesma gramática das cinco vizinhas. Leia as cinco antes de escrever a sexta: *"o método não é executável"* descreve o sintoma, e nenhuma das cinco fala assim
- [ ] T016 [US2] Prender a guarda em `backend/tests/unit/editais/test_forma_da_ocorrencia_na_composicao.py` (**NOVO**): referência em prosa é recusada; referência que termina em número é aceita; a recusa nomeia campo, forma e razão; **e o método comum do Edital recebe a mesma recusa**
- [ ] T017 [US2] Prender o que **não** dispara em `backend/tests/unit/editais/test_forma_da_ocorrencia_na_composicao.py` (**EXISTENTE**, criado em T016 — acrescente ao fim): marco que **não** sorteia, e Edital sem método algum, não produzem nada desta família
- [ ] T018 [P] [US2] Prender a `FR-514` em `backend/tests/integration/editais/test_acervo_com_ocorrencia_em_prosa_continua_retificavel.py` (**NOVO**): Edital publicado cuja ocorrência não satisfaz a forma **continua retificável**, e a guarda não o alcança. É o teste que a `T004` decide como escrever — se o acervo estiver limpo, ele prende a garantia; se não, ele prende a saída escolhida

**Checkpoint**: nenhum Edital novo atravessa a composição com ocorrência que o motor não deriva.

---

## Phase 5: US3 — A recusa do dia para de culpar a fonte (P3)

**Goal**: a tela do sorteio distingue *a fonte não publicou* de *a declaração não pôde ser lida*.

**Independent Test**: com um Edital publicado cuja ocorrência não é derivável, abrir a tela do
sorteio e ler uma frase que nomeia a declaração — e não a indisponibilidade da fonte.

**É a única das três que ajuda quem já publicou.** Depois da US1 e da US2, quase nenhum Edital novo
chega aqui.

- [ ] T019 [US3] Separar as duas causas em `backend/processo_seletivo/sorteios/application/previa.py` (**EXISTENTE**), onde hoje ambas caem no mesmo tratamento de erro (`FR-516`). **A frase certa já existe**, específica e correta, e é descartada a uma linha de onde seria exibida — o trabalho é parar de jogá-la fora, e não escrevê-la
- [ ] T020 [US3] Fazer a tela dizer, quando a causa é a declaração, **qual campo e o que ele precisa conter**, e só então que corrigir exige Retificação — nesta ordem (`FR-517`). Toca `backend/processo_seletivo/interface/templates/interface/sorteio.html` (**EXISTENTE**)
- [ ] T021 [US3] **Não tocar** a frase da indisponibilidade real, em `backend/processo_seletivo/interface/templates/interface/sorteio.html` e `backend/processo_seletivo/sorteios/application/previa.py` (**EXISTENTE**) — `FR-518`. Conferência, como T011: ela está certa para a causa dela, e esta feature não mexe no que está certo
- [ ] T022 [US3] Prender as duas causas em `backend/tests/interface/test_recusa_do_sorteio.py` (**NOVO**): referência não derivável produz a frase da **declaração**, nomeando campo e forma; cadeia esgotada por indisponibilidade real produz a frase **de hoje**, inalterada; e as duas são distinguíveis uma da outra

**Checkpoint**: quem publicou antes da guarda sabe o que corrigir.

---

## Phase 6: Polimento e conferência

- [ ] T023 Percorrer os **cenários 1 e 2** de `specs/035-sorteio-executavel/quickstart.md` (**EXISTENTE**) pela interface administrativa, com o seletor de identidade ligado — inclusive a contraprova do marco que não sorteia
- [ ] T024 Corrigir as **três fixtures** nomeadas em `research.md` `R-6`, em `backend/tests/unit/publicacoes/test_pdf_classificacao.py` (**EXISTENTE** — altere **só** as três declarações de ocorrência). **Corrija as fixtures, e nunca a regra**: afrouxar a derivação para achar o número em qualquer posição faria `concurso 6100 de 2026` derivar para **2027**. Elas são a evidência do defeito, não um obstáculo a ele
- [ ] T025 Percorrer o **cenário 3** de `specs/035-sorteio-executavel/quickstart.md` (**EXISTENTE**) — o sorteio de ponta a ponta, do congelamento à verificação pública. **É o `SC-176`, e é o que decide se a feature entra.** Se qualquer passo exigir shell, banco ou endereço digitado, o critério não fechou
- [ ] T026 [P] Percorrer o **cenário 4** de `specs/035-sorteio-executavel/quickstart.md` (**EXISTENTE**) — a recusa do acervo, e a contraprova da indisponibilidade real
- [ ] T027 Percorrer o **cenário 5** de `specs/035-sorteio-executavel/quickstart.md` (**EXISTENTE**): exportar o acervo **e os sorteios já realizados** agora, e comparar com o retrato de T002. **Nenhum sorteio muda de resultado** (`FR-519`, `SC-179`)
- [ ] T028 [P] Varrer os Editais de sorteio da amostra real de `doc/avaliacao-de-capacidade-editais-2026-09-12.md` (**EXISTENTE**, leitura) e registrar em `specs/035-sorteio-executavel/varredura-da-amostra.md` (**NOVO**) **como cada um declara — ou não declara — a ocorrência**, e o que alguém teria de escrever no campo ao compor a partir dele (`SC-180`). A leitura de quatro deles, em `research.md` `R-7`, mostrou que **nenhum declara ocorrência externa**: confirme ou refute isso nos demais, porque é o que a ajuda da `FR-508` precisa ensinar
- [ ] T029 Escrever `specs/035-sorteio-executavel/rastreabilidade.md` (**NOVO**), citando a varredura de T028: uma linha por `FR-`, uma por `SC-` — e **uma por fixture ou teste alterado, com o motivo**
- [ ] T030 Rodar `cd backend && make lint check test-pg` e registrar a contagem final em `specs/035-sorteio-executavel/rastreabilidade.md` (**EXISTENTE**, criado em T029). `test-pg` e **nunca** `test`; `lint` são **dois** passos. O `make check` inclui `makemigrations --check`, e é ele o guarda de **nenhuma migration** (`SC-181`). Registre junto, por leitura do diff, as duas promessas que comando nenhum prova: **nenhuma capacidade ou papel novo** e **nenhum vocabulário alargado** (`FR-520`, `SC-181`). **Não edite arquivo do projeto enquanto a suíte roda**

---

## Dependências

```
Phase 1 (T001–T004) ──► T004 é PORTÃO DE MEDIÇÃO ──► Phase 2 (T005–T006)
                                                            │
                                                            ▼
                                                     US1 (T007–T013)  🎯 MVP
                                                            │
                                                 ┌──────────┴──────────┐
                                                 ▼                     ▼
                                          US2 (T014–T018)       US3 (T019–T022)
                                                 └──────────┬──────────┘
                                                            ▼
                                                  Polimento (T023–T030)
```

**US2 e US3 são independentes entre si**: a primeira vive em `editais/domain`, a segunda em
`sorteios/application` e na tela do sorteio.

### Dentro das fases

- **T005 → T006** — não há o que comparar antes de a consulta existir.
- **T007 → T008 → T009 → T010** são os **dois mesmos templates**, e por isso **nenhuma leva `[P]`**.
  Parecem independentes porque falam de campos diferentes — a escolha, o valor do acervo, a ajuda —,
  e não são: as quatro editam os mesmos dois arquivos. A `T009` entrou na cadeia quando o `tasks`
  achou a `FR-511` sem tarefa, e a cadeia teve de ser recontada.
- **T014 → T015** são a mesma função.
- **T016 → T017** são o mesmo arquivo, criado em T016.
- **T019 → T020** — a tela só pode dizer a causa certa depois de as duas serem separadas.
- **T024 antes de T025** — a suíte precisa estar verde antes do percurso que decide a feature.

### Oportunidades de paralelismo

| Tarefas | Por que podem |
|---|---|
| T013 · T018 | arquivos diferentes, nenhuma dependência aberta |
| T026 · T028 | percursos independentes, um sem banco e outro só de leitura |
| US2 inteira · US3 inteira | módulos disjuntos, depois que a US1 fecha |

**T027 fica de fora do paralelismo**: ele compara o acervo e os sorteios contra o retrato de T002, e
qualquer percurso que publique ou sorteie em paralelo muda o que ele conta.

---

## Estratégia de entrega

**MVP = fase 1 + fase 2 + US1.** A composição passa a ensinar, e quem segue a tela produz um método
que roda. É o elo que faltava, e sem ele os outros dois tratam o sintoma: a guarda recusaria o que a
tela acabou de convidar a escrever.

**Se algo travar, entregue o MVP inteiro e diga o que ficou.**

**A US3 não deve ser adiada indefinidamente.** Ela é a única das três que alcança quem **já
publicou** — e para quem já publicou, a frase errada é a diferença entre saber o que corrigir e
esperar por uma fonte que nunca esteve indisponível.
