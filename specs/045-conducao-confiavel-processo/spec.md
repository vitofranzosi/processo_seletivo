# Feature Specification: Condução confiável do Processo vivo

**Feature Branch**: `claude/conducao-confiavel-processo-a5a78b`

**Created**: 2026-09-26

**Status**: Draft

**Input**: proposta do usuário de 26/09/2026, *"Condução confiável do Processo vivo"*. Consolida a
B-1 da [auditoria de consolidação](../../doc/auditoria-de-consolidacao-2026-09-26.md) — `RC-78`,
`RC-79`, `RC-80`, `RC-81`, `RC-82` e a parte do `RC-84` que toca os sinais — e fecha as
condicionantes `C1`, `C2`, `C4`, `C5` e `C6` da
[convergência de 20/09](../../doc/auditoria-de-convergencia-pos-038-2026-09-20.md). A proposta
responde às perguntas `DP-01` a `DP-04` das
[decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md), e o registro de cada resposta
entra lá, no bloco *"O que foi decidido"* de cada uma.

> **Faixa de identificadores.** Abre em **FR-730**, **SC-269** e **UX-084**. O teto medido em
> 26/09/2026 em todas as worktrees (`git worktree list`) e nas branches abertas é `FR-729`,
> `SC-268` e `UX-083`, todos da `044`, que já está na `main` — sem negrito, porque não são requisitos
> desta spec e a matriz de rastreabilidade cobra todo identificador em negrito. A `039`, aberta no PR #175, vive
> numa faixa anterior e não disputa esta. As **decisões** reiniciam em `D-001`; as da `022` e da
> `038` citadas aqui vão sempre com a spec de origem ao lado.

> **Teto proporcional.** A `038` fixou o método em 19/09: *"requisito que existe para impedir alguém
> de ler errado outro requisito não é requisito"*. Esta spec corrige uma feature entregue, **encolhe**
> o catálogo em vez de aumentá-lo, e cabe em **quatro histórias** e **dezesseis requisitos**. O que
> sobrar é nota de tarefa.

---

## Por que esta feature existe

**A Supervisão afirma mais do que observa.** A `038` levou pulso e Atenção à página do Processo, e
Processo e Supervisão passaram a dizer a mesma coisa — o maior acerto da feature, medido em 20/09. A
convergência mediu também o que ela diz de errado, e são cinco defeitos da mesma família:

| | O que a tela diz | O que é verdade | Onde |
|---|---|---|---|
| `RC-78` | *"Nenhuma condição de atenção neste Processo"* | o leitor alcança parte das espécies; as outras não foram lidas | `processo_detalhe.html:140`, `supervisao.html:140` |
| `RC-79` | nada, enquanto o recurso espera admissibilidade; e *"Recursos recebidos (N)"* conta também os decididos | a peça espera decisão de quem julga | `supervisao.py:1162-1167`; `acoes.py:118-128` |
| `RC-80` | um `UX-002` por Evento cujo início passou; `UX-001` e `UX-002` mandam retificar | o `status` nasce `PLANEJADO` e ninguém o declara nem o deriva; a Retificação não alcança nenhum dos dois campos | `mutabilidade.py:432`, `:447`; `supervisao.py:635-662` |
| `RC-81` | frase solta, sem caminho | quem lê não tem a capacidade, e não sabe a quem pedir | `_sinal.html`; `supervisao.py`, `admite_encaminhamento` |
| `RC-82` | *"2 de 5 sem avaliador suficiente"* | a tela de destino lista **4** — uma inscrição foi eliminada antes | `supervisao.py:686`; `avaliacoes/application/selectors.py:204-241` |

**O número que decide a prioridade.** Com o papel Gestor, em 20/09, a Atenção mostrava **15** sinais:
**9** sem caminho — 6 `UX-001` e 3 `UX-002`. Nenhum deles era trabalho que o gestor pudesse fazer, e
nenhum era trabalho que *alguém* pudesse fazer pela tela para onde o sinal apontava. O Publicador,
no mesmo instante, lia *"Nenhuma condição de atenção neste Processo"*.

### O que a verificação contra o código acrescentou à proposta

A proposta foi conferida contra a `main` em `2ffe5a2`. Seis fatos mudam o desenho, e nenhum muda a
direção:

1. **O `UX-002` não é reescrito: ele desaparece.** A condição dele é *estado declarado incompatível
   com a posição no relógio*, e já exclui `CANCELADO`. Derivada a fase ordinária, declarado e relógio
   não têm como discordar, e o sinal fica sem condição que o dispare. Mantê-lo no catálogo seria
   guardar uma espécie morta. O catálogo **encolhe**: de dez espécies para oito (`FR-744`).
2. **O `UX-001` não tem para onde "mover".** A validação do conteúdo do Edital hoje confere que a
   Etapa não referencie Evento **inexistente**, e não diz nada da Etapa que não referencia Evento
   **nenhum**. O aviso de composição que a `DP-03` recomenda precisa **nascer** — como aviso, e nunca
   como impeditivo, porque a ausência é publicável e legítima (`022`, `FR-026`).
3. **A régua temporal já existe, e é única.** A `037` fez de "o Evento venceu" um módulo só
   (`editais/domain/calendario.py`, `FR-545` a `FR-547`): havendo término, vence quem terminou; não
   havendo, vence quem começou. A fase derivada **é essa régua lida por inteiro**, e não uma segunda
   — é o que a proposta chama de "contrato temporal existente". Com uma exceção que já está escrita: o
   período de inscrições tem régua própria (`inscricoes/domain/periodo.py`, `FR-347`), e é ela que
   decide se o sistema recebe inscrição; a fase desse Evento não pode dizer outra coisa.
   **E a fase já é exibida hoje**: o pulso marca cada próximo marco com *"declarado planejado"* — em
   todo Edital composto pela tela, porque nada escreve outro valor. É essa a "fase exibida" do cenário
   C da proposta.
4. **Depois de derivar o `status` e tirar o `UX-001`, quase todo sinal sem caminho some.** Dos 9 que
   a convergência contou, nenhum sobrevive. O que resta do `RC-81` é o `UX-046` — o único sinal que
   ainda leva à Retificação — para quem não pode retificar, ou num Edital que já parou. A frase para
   o primeiro caso **já existe**, pronta, na `037` (`CONDUCAO_DA_RETIFICACAO`, `FR-543`). O segundo
   caso é a `D-003`.
5. **O denominador da cobertura é pior do que "conta quem foi eliminado".** Ele conta **toda
   inscrição submetida do Edital**: eliminada em Etapa anterior, à espera do resultado da Etapa
   anterior, fora do corte. Nenhuma delas pode ser distribuída ali, e por isso fica "sem avaliador
   suficiente" para sempre. E o defeito não é só do painel: a própria tela de distribuição mostra o
   mesmo número ao lado de uma lista que conta outra população — só os participantes —, e com outro
   filtro — o número inclui quem não tem avaliador nenhum, a lista para onde ele leva, não. A fonte
   única de participação **já existe** (`resultados/application/prontidao.py`, `participacao_detalhada`)
   e a distribuição, a Mesa e a classificação já a usam; o resumo da cobertura é o que ficou de fora.
6. **O recurso não tem prazo de resposta modelado.** A proposta e a auditoria falam da peça *"com
   prazo"*; o único prazo que o sistema conhece é a janela de **interposição**. A urgência de responder
   é institucional, e esta feature não a modela: o sinal diz que há peça esperando decisão, e não que
   um prazo corre. E o `UX-064` é **agregado por Edital**, com medida — não um sinal por peça —; é o
   agregado que passa a contar as duas fases.

E mais um, que a proposta intuía e o código confirma: **nenhum papel sozinho alcança o catálogo
inteiro.** O Gestor não alcança os recursos nem a divulgação; o Julgador só alcança os recursos; a
Publicador só a divulgação. Depois desta feature, a frase de ausência global só será dita a quem
acumula papéis — e isso é o comportamento certo, não um efeito colateral (`D-004`).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A ausência respeita o alcance de quem lê (Priority: P1)

Quem alcança só parte do que a Atenção acompanha, e não vê nenhuma condição, lê que não há condição
**entre as que acompanha** — e não que o Processo está em dia.

**Why this priority**: é o único ponto em que o produto quebra a ausência honesta (`C1`, S3), e o
defeito aparece exatamente quando as funções são segregadas — que é a operação institucional para a
qual o piloto deveria servir de prova. É também a menor mudança da feature.

**Independent Test**: com três identidades — Gestor, Publicador, Julgador — sobre o mesmo Processo,
deixar condições que só o Gestor alcança e conferir a frase que cada um lê; depois resolver as
condições e conferir que a frase de quem não as alcançava **não mudou**.

**Acceptance Scenarios**:

1. **Given** um Processo com condições que só o Gestor alcança, **When** o Publicador abre o
   Processo ou a Supervisão, **Then** lê a ausência **relativa** ao seu alcance, e nunca a global.
2. **Given** o mesmo Processo **sem** condição alguma, **When** o Publicador o abre, **Then** lê
   **exatamente a mesma frase** do cenário anterior — a frase não depende do que ela não vê.
3. **Given** um ator que acumula os papéis que alcançam todas as espécies, **When** não há condição
   alguma, **Then** lê a ausência global.
4. **Given** um ator que não alcança espécie nenhuma, **When** abre o Processo, **Then** a região da
   Atenção continua não aparecendo (`038`, sem mudança).

---

### User Story 2 - O recurso aparece desde que chega (Priority: P2)

A peça recém-interposta produz sinal enquanto espera admissibilidade, continua produzindo enquanto
espera julgamento, e deixa de produzir quando é decidida.

**Why this priority**: é o segundo S3 (`C2`). A peça recém-chegada é invisível na condução, para
todos os papéis, até que alguém a admita — e só a admite quem a encontrou por outro caminho. A
recuperação lateral — *"Recursos recebidos (N)"* — conta também as peças já decididas.

**Independent Test**: interpor um recurso pelo portal e conferir, como Julgador, que a Atenção o
mostra antes de qualquer ato; admiti-lo e conferir que o sinal continua, com a fase trocada; julgá-lo
e conferir que ele sai do sinal e da contagem.

**Acceptance Scenarios**:

1. **Given** um recurso recém-interposto, **When** o Julgador abre o Processo, **Then** há sinal que
   diz que há recurso **aguardando admissibilidade** naquele Edital e leva aos recursos dele.
2. **Given** o recurso admitido, **When** a Atenção é montada, **Then** o sinal continua, e diz que
   ele **aguarda julgamento** — o mesmo sinal, com a fase trocada, e não um segundo.
3. **Given** a comissão inteira impedida, **When** a peça aguarda admissibilidade, **Then** o sinal é
   o `UX-005`, e não o `UX-064` — a partição da `038` vale nas duas fases.
4. **Given** o recurso inadmitido, ou julgado, **When** a Atenção e a lista de Processos são
   montadas, **Then** ele não compõe sinal nem a contagem de pendentes.

---

### User Story 3 - O Cronograma deixa de produzir alarme (Priority: P3)

Um Edital com Eventos passados, correntes e futuros não produz sinal nenhum por isso. A Etapa sem
Evento é dita onde pode ser corrigida — na composição —, e não na condução, onde nenhuma tela a
corrige.

**Why this priority**: são **9 dos 15** sinais do Gestor (`C5`, `C6`). É também o que desbloqueia a
`US4`: sem ela, a instrução *"a quem pedir"* seria escrita para sinais que não deveriam existir.

**Independent Test**: publicar um Edital com um Evento encerrado, um em curso e um futuro, e uma
Etapa sem Evento; conferir que a Atenção não mostra nenhum dos quatro fatos, que a fase de cada Evento
é a do relógio, e que a Etapa sem Evento aparece como **aviso** na Revisão antes de publicar e na
validação do Edital depois.

**Acceptance Scenarios**:

1. **Given** Eventos passados, correntes e futuros, **When** a fase de cada um é lida, **Then** ela é
   *concluído*, *em andamento* e *planejado*, sem que ninguém tenha declarado nada.
2. **Given** um Evento `CANCELADO` cujas datas estão em curso, **When** a fase é lida pela gestão,
   **Then** ele é *cancelado*, e nunca *em andamento*.
3. **Given** qualquer Edital publicado, **When** a Atenção é montada, **Then** não há sinal de
   divergência entre estado declarado e relógio — a espécie deixou de existir.
4. **Given** uma Etapa sem Evento vinculado, **When** o Edital é revisado antes de publicar, **Then**
   há **aviso**, que não impede a publicação; **and when** o Edital já está publicado, **Then** o fato
   aparece na validação do conteúdo do Edital, e **não** na Atenção.

---

### User Story 4 - O sinal que fica diz o que conta e a quem pedir (Priority: P4)

Todo sinal que continua na Atenção ou leva a uma tela onde quem lê age, ou diz a capacidade de que
depende. Toda medida diz o que conta, e conta o mesmo que a lista para onde leva.

**Why this priority**: é o `C4` e o `RC-82`. Vem por último porque depende da `US3`: dos 9 sinais sem
caminho da convergência, a `US3` elimina todos, e o que sobra para esta história é pouco e preciso.

**Independent Test**: como Gestor sem a permissão de retificar, abrir um Processo com `UX-046`
disparado e conferir a frase de condução; como Gestor, abrir a Atenção de uma Etapa com inscrição
eliminada antes e conferir que o denominador do sinal é o número de linhas da distribuição.

**Acceptance Scenarios**:

1. **Given** um sinal cujo ato o leitor não pode praticar, **When** a Atenção é montada, **Then** o
   sinal diz a permissão de que o ato depende e o que pedir, sem nomear pessoa.
2. **Given** o mesmo sinal lido por quem **pode** praticar o ato, **When** a Atenção é montada,
   **Then** ele recebe o caminho, e **não** a frase de pedir (`037`, `FR-544`).
3. **Given** uma Etapa com inscrições eliminadas em Etapa anterior, **When** a cobertura é medida,
   **Then** o denominador conta só quem ainda precisa ser avaliado ali, e coincide com a lista da
   distribuição.
4. **Given** qualquer sinal com medida, **When** é lido, **Then** a medida diz a unidade — *"2 de 4
   inscrições"*, e nunca *"2 de 4"*.

---

### Edge Cases

Cada um destes é requisito, e ganha linha própria na matriz de rastreabilidade.

- **Leitor que acumula todos os papéis.** Lê a ausência global. Na equipe inicial de 2–3 pessoas isso
  vai acontecer, e está certo: essa pessoa de fato leu tudo.
- **O alcance muda com o estado do Edital.** As espécies de trabalho pendente saem num Edital que
  parou por ato (`038`). Isso **não** torna a leitura parcial: o estado respondeu, e não foi o leitor
  que deixou de ver. A escolha da frase olha o alcance do **leitor**, e não o que o estado retirou.
- **Evento sem término.** A régua da `037` vale inteira: sem término, vence quem começou. Um Evento
  pontual é *planejado* antes do início e *concluído* depois dele — nunca *em andamento* para sempre.
- **Período de inscrições sem término.** É a exceção: a régua do período (`FR-347`) o mantém aberto,
  e a fase dele é *em andamento* enquanto o sistema recebe inscrição. A fase não pode dizer
  *concluído* de um período em que o candidato ainda consegue se inscrever.
- **Quatro regras para o Evento sem término.** O código tem hoje quatro leituras diferentes dele — a
  régua da `037`, a do período, a do pulso e a do portal do candidato, que é privada e compara só o
  dia. Esta feature usa as duas primeiras e alinha o pulso a elas; o portal fica como está e a
  divergência fica **registrada** (ver *Out of Scope*). Não há discordância visível nova: o pulso tira
  o Evento pontual da lista no instante em que ele passa, e o portal só o chama de *em curso* depois
  disso.
- **Evento sem início** não deveria existir no conteúdo publicado, e a conferência de forma o acusa.
  Se existir, a fase não é inventada: ele não recebe fase ordinária.
- **Edital publicado antes desta feature** com fase ordinária declarada pela API. O conteúdo publicado
  não é reescrito; a leitura deixa de considerar a fase ordinária declarada, e só `CANCELADO` continua
  sendo lido do que foi publicado.
- **Recurso admitido.** Continua sendo **uma** peça pendente: muda a fase que a mensagem diz, e não o
  número de sinais.
- **O Julgador impedido nesta peça** continua vendo o `UX-064`, cuja condição é do conjunto — *há*
  membro desimpedido. A tela dos recursos já trata o impedimento individual; o sinal não o antecipa.
- **Etapa sem ninguém a avaliar** — todos eliminados antes. Não há cobertura a medir, e não há sinal:
  *"0 de 0"* não é condição.
- **Inscrição à espera do resultado da Etapa anterior, ou fora do corte.** Não é participante ainda,
  e não entra no denominador. Entra quando a Etapa anterior a habilitar — é a regra da fonte única de
  participação, e não uma nova.
- **Participante sem avaliador nenhum** continua no denominador e continua carente (`022`,
  `FR-033`). E a lista para onde o número leva MUST mostrá-lo: hoje o filtro da distribuição o deixa
  de fora.
- **`UX-046` num Edital que parou por ato.** A Retificação só incide sobre Edital **publicado**; no
  encerrado ou cancelado, ninguém pode praticá-la. O sinal sai da Atenção (`D-003`).
- **Outra espécie com o mesmo defeito.** Se o plano medir que uma espécie fora das tratadas aqui leva,
  numa situação, a um ato que ninguém pode praticar, isso vira **achado registrado**, e não escopo. A
  premissa escrita no código da `038` para manter `UX-001` e `UX-002` num Edital encerrado
  (*"continua podendo Retificar"*) é falsa, e é por isso que a pergunta existe. **Medido no plano**
  (`research.md`, `R-7`): o `UX-004` e o `UX-005` num Edital encerrado **não** têm o defeito —
  reemitir a ordem e julgar o recurso continuam possíveis enquanto o Processo não estiver em estado
  final. O `UX-065` em recorte sem quadro tem, e ficou registrado.

---

## Requirements *(mandatory)*

### A ausência respeita o alcance

- **FR-730**: A ausência **global** de condições MUST ser dita apenas a quem alcança **todas** as
  espécies do catálogo naquele Processo. A quem alcança parte delas, e não tem sinal algum, MUST ser
  dita a ausência **relativa** ao seu alcance (`UX-084`). Quem não alcança nenhuma continua sem a
  região (`038`). A regra vale igualmente para a página do Processo e para a Supervisão, que leem a
  mesma derivação (`038`, `FR-557`).
- **FR-731**: A escolha entre as duas frases MUST depender **exclusivamente** do alcance do leitor, e
  MUST NOT depender da existência, da quantidade ou da natureza de sinal que ele não alcança. *É a
  garantia contra vazamento por agregação que a `022` (`FR-004`) já exige da supressão, estendida à
  frase de ausência: a frase não pode ser o canal por onde a supressão se revela.*

### O recurso aparece desde que chega

- **FR-732**: A condição do `UX-064` e a do `UX-005` MUST passar de *"aguardando julgamento"* para
  *"aguardando decisão"* — admissibilidade **ou** julgamento. Os dois continuam agregados por Edital,
  e a mensagem MUST dizer em que fase estão as peças que contam (`UX-085`). A partição da `038` MUST
  continuar valendo nas duas fases: nenhuma peça conta nos dois sinais. Substitui a `FR-561` da `038`
  e amplia a `FR-030` da `022`.
- **FR-733**: A peça decidida — inadmitida, ou julgada — MUST deixar de compor sinal e medida na
  primeira leitura depois da decisão.
- **FR-734**: A contagem de recursos oferecida como ação a quem julga — na lista de Processos e no
  cartão do Edital — MUST contar apenas as peças que aguardam decisão, e o rótulo MUST dizer que conta
  pendentes. A tela de recursos, para onde ela leva, continua listando todas.

### O Cronograma deixa de produzir alarme

- **FR-735**: A fase **ordinária** de um Evento — planejado, em andamento, concluído — MUST ser
  derivada das datas dele e do instante da leitura, pelas réguas que o produto já tem: a do vencido
  (`037`, `FR-545` a `FR-547`) — antes do início, planejado; vencido, concluído; entre os dois, em
  andamento — e, para o período de inscrições, a do próprio período (`FR-347`), com a qual a fase
  MUST concordar. Nenhuma superfície MUST ler a fase ordinária declarada; onde a gestão exibe a fase —
  hoje, os próximos marcos do pulso —, ela é a derivada (`UX-088`). O portal do candidato já exibe fase
  por regra própria, que não lê o declarado; alinhá-lo a estas réguas fica fora (*Out of Scope*).
  Substitui a `D-004` e a `FR-023` da `022` (`D-001`).
- **FR-736**: `CANCELADO` MUST continuar sendo o único estado **declarado**, e MUST prevalecer sobre a
  derivação: nas superfícies da gestão, Evento cancelado nunca é apresentado em fase ordinária. O
  portal e o documento publicado, que hoje não filtram o cancelado, ficam registrados e fora (*Out of
  Scope*). Esta feature MUST NOT criar caminho novo para declará-lo.
- **FR-737**: Nenhum caminho de entrada — tela ou API — MUST aceitar *em andamento* ou *concluído*
  como declaração. O campo guardado passa a responder uma pergunta só — cancelado ou não —, e a forma
  do conteúdo publicado não muda. *Um valor aceito e nunca lido é uma segunda fonte para o que as
  datas já dizem, e a Constituição (Princípio II) exige uma só.*
- **FR-738**: O `UX-002` MUST ser retirado do catálogo. Substitui a `FR-027` e o `UX-002` da `022`.
- **FR-739**: A Etapa sem Evento vinculado MUST deixar a Atenção e MUST passar a ser dita como
  **aviso** na validação do conteúdo do Edital — na composição, na Revisão antes de publicar e na
  página do Edital publicado (`UX-086`). O aviso vale para o ato de **publicação**; na Retificação,
  onde o vínculo não pode ser mudado, ele não aparece (`D-003`). O aviso MUST NOT impedir a
  publicação: o que o sistema aceita publicar não muda (`022`, `FR-026`).

### O sinal que fica diz o que conta e a quem pedir

- **FR-740**: Todo sinal cujo ato o leitor não pode praticar MUST dizer a permissão de que o ato
  depende e o que pedir — no próprio sinal, quando ele não tem caminho; ou na tela a que leva, quando
  o leitor a abre só para consultar —, pelo **mecanismo único** da `037` (`FR-543`, `FR-543a`,
  `FR-543b`). Quem detém a permissão recebe o caminho e não a frase (`037`, `FR-544`).
- **FR-741**: O sinal cujo destino é a Retificação MUST NOT ser condição de Atenção quando a situação
  não a admite — Edital fora do estado publicado, ou Processo em estado final —, porque ninguém pode
  praticá-la (`D-003`). Depois desta feature, a única espécie nessa situação é o `UX-046`.
- **FR-742**: As medidas da Etapa — a cobertura (`UX-003`) e a avaliação parada (`UX-063`) — MUST ser
  contadas sobre os **participantes** da Etapa, como a fonte única de participação já os define para a
  distribuição, a Mesa e a classificação: fora ficam a inscrição eliminada antes, a que espera o
  resultado da Etapa anterior e a que ficou fora do corte. O número e a lista para onde ele leva MUST
  contar **o mesmo conjunto** — mesma população e mesmo filtro —, no painel e na própria tela de
  distribuição. *Refina a `FR-033` da `022`: unidade de trabalho esperada é quem segue na Etapa, e só
  dela o denominador não pode ser retirado.*
- **FR-743**: Toda medida apresentada num sinal MUST nomear a sua unidade (`UX-087`). O alcance é o
  dos sinais e da contagem da `FR-734`; as três formas de prazo do sistema (`RC-84`) ficam fora.

### O catálogo e a precedência

- **FR-744**: A `FR-565` da `038` MUST ser **explicitamente substituída**, e o requisito sucessor
  MUST nomear, por extenso, as **oito** espécies vigentes: `UX-003`, `UX-004`, `UX-005`, `UX-046`,
  `UX-063`, `UX-064`, `UX-065` e `UX-066`. *O catálogo fechado cresce por decisão escrita, e encolhe
  do mesmo jeito.*
- **FR-745**: Cada requisito ou decisão anterior que esta feature substitui ou refina MUST receber,
  **na spec de origem**, a marca de substituição com o ponteiro para cá — como a `FR-024` da `022`
  recebeu em 19/09 —, e MUST NOT ser apagado. A tabela *"Precedência"*, abaixo, é a lista completa.

---

## Requisitos de apresentação

- **UX-084** — **A ausência relativa diz que é relativa.** A frase nomeia que não há condição **entre
  as que o leitor acompanha** neste Processo. Ela não enumera o que o leitor não alcança, não diz que
  há algo oculto, e não varia com o que existe fora do alcance. A redação segue a da frase global, de
  que é a variante.
- **UX-085** — **A fase é dita.** O `UX-064` e o `UX-005` dizem se as peças que contam aguardam
  admissibilidade, julgamento, ou as duas coisas. A distinção entre as fases continua sendo da tela
  dos recursos; o sinal só a nomeia, e não diz quem deve decidir.
- **UX-086** — **A Etapa sem Evento é aviso, e nunca atraso.** A Etapa e o Edital são nomeados, e a
  ausência é dita nesses termos — nunca como *aguardando*, *atrasada* ou progresso zero. É a regra de
  apresentação do `UX-001` da `022`, levada para a superfície onde o fato pode ser corrigido.
- **UX-087** — **A medida diz o que conta.** *"2 de 4 inscrições"*, e nunca *"2 de 4"*. Continua par
  ou nada (`022`, `FR-032`), e não repete o que a mensagem já diz — hoje o `UX-046` escreve os mesmos
  dois números na frase e na medida.
- **UX-088** — **O marco diz a fase derivada, e nunca "declarado".** O pulso deixa de marcar os
  próximos marcos com *"declarado planejado"*; o marco em curso é dito *em andamento*. É a fase do
  relógio, e a tela não a apresenta como declaração de ninguém.

---

## Success Criteria *(mandatory)*

- **SC-269**: Percorrido pela interface com **três identidades distintas** — Gestor (ou presidência),
  Publicador e Julgador — sobre o mesmo Processo: cada um vê só as espécies do seu alcance; **zero**
  leitores com alcance parcial recebem a frase global; e a frase de cada um é **idêntica** com e sem
  condições fora do seu alcance.
- **SC-270**: Um recurso interposto pelo portal aparece na Atenção do Julgador **na primeira leitura
  seguinte**, antes de qualquer ato; e sai do sinal e da contagem na primeira leitura depois da decisão.
- **SC-271**: Num Edital publicado com Eventos passados, correntes e futuros, **zero** sinais de
  Cronograma na Atenção, e a fase de **100%** dos Eventos — a exibida no pulso e a lida pela
  derivação — coincide com a régua.
- **SC-272**: Refeita a medição de 20/09 com o Gestor, e repetida com Publicador, Julgador e Auditor:
  **zero** sinais cujo ato o leitor não pode praticar e que não digam, no sinal ou na tela a que
  levam, a quem pedir. Com o Gestor, eram 9 de 15.
- **SC-273**: Para cada sinal com medida, o denominador coincide com o número de linhas da tela de
  destino — **zero** divergências —, e **100%** das medidas nomeiam a unidade.
- **SC-274**: O requisito que fecha o catálogo nomeia **exatamente** as espécies que o produto
  apresenta — conferido contando as duas listas —, e **zero** requisitos vigentes da `022` e da `038`
  contradizem esta spec sem a marca de substituição.

---

## Precedência

Esta spec é a decisão posterior. Ela **não apaga** o que a `022` e a `038` decidiram: marca, em cada
uma, o que foi substituído ou refinado, e por quê (`FR-745`).

| Onde | O que dizia | O que passa a valer |
|---|---|---|
| `022` `D-004` | o `status` do Evento é declarado; a divergência é o sinal | **substituída** — a fase ordinária é derivada (`D-001`, `FR-735`) |
| `022` `FR-023` | não alterar a semântica declarada do estado | **substituída** pela `FR-735` |
| `022` `FR-026` | identificar a Etapa sem Evento | **mantida**; muda a superfície — da Atenção para a validação (`FR-739`) |
| `022` `FR-027` e `UX-002` | sinal de declarado × posição temporal | **retirados** (`FR-738`) |
| `022` `UX-001` | a Etapa sem Evento como espécie da Atenção | **deixa de ser espécie**; a regra de apresentação vai ao aviso (`UX-086`) |
| `022` `FR-030` e `UX-005` | recurso aguardando julgamento, comissão impedida | **ampliados** para *aguardando decisão* (`FR-732`) |
| `022` `FR-033` | unidade esperada não sai do denominador | **refinada** — esperada é quem segue na Etapa (`FR-742`) |
| `038` `FR-559` | a ausência de todos é uma linha declarada | **mantida**; a linha tem duas formas (`FR-730`) |
| `038` `FR-561` e `UX-064` | recurso aguardando julgamento, com julgador disponível | **substituídos** pela `FR-732` |
| `038` `FR-565` | o catálogo tem dez espécies | **substituída** pela `FR-744` — oito |
| `037` `FR-547` | a régua do vencido é única | **mantida**; a fase derivada é mais um leitor dela (`FR-735`) |
| `026`, mutabilidade | `schedule.status` é derivado | **mantida**; pela primeira vez alguém o deriva — na leitura |

### Os testes de regressão da proposta

A proposta (§8) pede nove testes. Cada um tem o requisito que o cobra, e a matriz de rastreabilidade
os prende pelo nome real do teste:

| # | O que o teste prende | Requisito |
|---|---|---|
| 1 | ausência relativa ao alcance | `FR-730` |
| 2 | recurso em admissibilidade visível | `FR-732` |
| 3 | recurso decidido fora da contagem de pendentes | `FR-733`, `FR-734` |
| 4 | derivação temporal do Evento | `FR-735` |
| 5 | a exceção `CANCELADO` | `FR-736` |
| 6 | nenhum `UX-002` espúrio | `FR-738` |
| 7 | população correta no indicador de avaliação | `FR-742` |
| 8 | capacidade a pedir no sinal sem destino | `FR-740` |
| 9 | nenhum vazamento entre papéis | `FR-731`, `SC-269` |

---

## Assumptions

### D-001 — A fase ordinária do Evento é derivada; `CANCELADO` é declaração

**Decidido pelo usuário em 26/09** (`DP-01`, opção A). A `022` tratava o `status` como declarado; a
`026` o registrou como derivado; o código não fazia nenhum dos dois — nasce `PLANEJADO` e fica.

Derivar é a única opção que não pede a ninguém trabalho manual para manter um dado que as datas já
contêm. O receio da `022` era derivar **atraso** e produzir alarme falso; derivar a **fase** não
produz alarme nenhum — produz o que o relógio diz. Publicação é ato imutável: se a fase fosse
declarada, cada mudança de fase seria uma Retificação publicada, e nenhum Edital declara como norma
que *"o período de inscrições está em andamento"*.

`CANCELADO` é outra coisa: muda o que o Edital diz, e nenhuma data o deriva. Continua declaração, e o
caminho para declará-lo pela tela — uma Retificação que cancela o Evento — é pergunta que só vale
abrir quando houver caso.

*Descartadas*: declarar a fase como registro operacional fora do conteúdo publicado (um modelo, uma
tela e uma permissão novos para manter o que as datas já dizem), e declará-la por Retificação (fase de
Evento como ato normativo, contra o veto da convergência §21).

### D-002 — A admissibilidade amplia o `UX-064` e o `UX-005`

**Decidido pelo usuário em 26/09** (`DP-02`): *"a solução de menor complexidade que preserve clareza
para o operador"*. É a ampliação.

Admitir e julgar exigem a mesma permissão e a mesma regra de impedimento. Para quem conduz, as duas
fases são o mesmo fato — uma peça espera decisão de quem tem a permissão de julgar —, com o mesmo ator
e o mesmo destino. Espécies separadas multiplicariam o catálogo por uma diferença que não muda quem
age nem onde. A distinção entre as fases mora na tela do recurso, que já a faz bem, e o sinal só a
nomeia (`UX-085`).

### D-003 — Condição sem destino operacional não pertence à Atenção

**Decidido pelo usuário em 26/09** (`DP-03`, opção A). A Atenção é *"há trabalho parado"*; a
validação do conteúdo é *"a composição tem imperfeição"* (convergência §21, sobre o `N-08`).

A Etapa sem Evento só se corrige sem custo na composição, e é lá que ela deve ser dita. Um painel de
condução que mostra, para sempre, um fato sobre o qual ninguém pode agir treina quem lê a ignorá-lo —
6 dos 15 sinais do Gestor eram isso.

**Isto não é silenciar o `UX-001` nem o `UX-002`**, que a convergência (§21) vetou. O `UX-001` continua
dito, na superfície onde tem remédio. O `UX-002` não é silenciado: a causa dele deixa de existir.

**Nem acrescentar `scheduleEventId` à Retificação**, que a convergência (§21) também vetou e esta
feature não faz: seria dar destino ao sinal mudando o contrato de mutabilidade para um caso que nenhum
Edital da amostra pediu.

### D-004 — A ausência é relativa ao alcance

Nenhuma superfície transforma *"não encontrei dentro do que consigo observar"* em *"não existe no
Processo"*. E a frase que diz a diferença não pode ela mesma revelar o que está fora do alcance
(`FR-731`): o objetivo não é informar *"há três problemas que você não pode ver"*, é não afirmar
falsamente *"não há problemas"*.

Consequência medida: **nenhum papel sozinho alcança o catálogo inteiro** — o Gestor não alcança os
recursos nem a divulgação —, e a frase global passa a ser de quem acumula papéis. É o comportamento
certo.

### D-005 — A capacidade a pedir usa a frase que já existe

A `037` fez do *"peça a alguém com a permissão de X que Y"* um mecanismo único, e a Retificação já tem
a sua frase pronta. O painel a usa; não redige outra (`037`, `FR-543`). O produto continua não ligando
identidade a papel: a frase nomeia a permissão, nunca a pessoa (`038`, `FR-564`; convergência §16 —
*"o que falta não é o nome da pessoa: é a capacidade a pedir"*).

### Outras premissas

- **O registro das decisões.** A proposta de 26/09 é a resposta do usuário às `DP-01` a `DP-04`. A
  resposta entra em [`decisoes-pendentes-da-consolidacao.md`](../../doc/decisoes-pendentes-da-consolidacao.md)
  como bloco *"O que foi decidido"* em cada uma, sem apagar as opções.
- **O alcance de cada espécie não muda.** Quem vê qual sinal continua sendo a tabela de alcance da
  `038`; esta feature muda o que é sinal, a frase de ausência e o que o sinal diz.
- **Nenhuma capacidade nova, nenhum estado persistido novo, nenhum conteúdo publicado reescrito, nada
  apagado** (`038`, `FR-566`). A fase é calculada na leitura.
- **O contrato de mutabilidade não muda.** A `026` classifica `schedule.status` como derivado, e a
  Retificação continua não o oferecendo. O que muda é que, pela primeira vez, alguém o deriva — na
  leitura, e não gravando. Declarar `CANCELADO` por Retificação é a pergunta que a `D-001` deixa para
  quando houver caso.

---

## Out of Scope

Da proposta, e mantido: painel novo; a visão institucional `040`–`042`; sorteio e requerimentos de
matrícula na Atenção; métricas analíticas e gráficos; responsável individual por sinal; notificação
por e-mail; fila automática; autorização por Perfil ou polo; otimização de consulta sem medição;
redesenho dos recursos; estados manuais novos de Evento; Retificação além de deixar de apontá-la onde
ela não resolve.

E, conferido contra o código:

- **O caminho de tela para declarar `CANCELADO`.** Hoje só a API o aceita, e esta feature não o cria.
- **As três formas de prazo** (*"Faltam 19 dias"* × *"2 semanas, 5 dias"* × só a data) e a
  **exportação vazia sem mensagem** (`N-10`): são a outra metade do `RC-84`, e não tocam os sinais.
- **Juntar os avisos da validação do Edital à Atenção** (`N-08`). Esta feature move um fato no
  sentido oposto — da Atenção para a validação — e não decide a fronteira entre as duas.
- **Outra espécie com o mesmo defeito que a `FR-741` trata**: registro, não escopo (ver *Edge Cases*).
  O plano mediu três, e as três ficam registradas em `research.md` (`R-7`): o `UX-065` em recorte sem
  quadro, que ninguém pode apurar; o `UX-004` num Processo em estado final, cuja tela oferece um
  formulário que recusa com 409; e a tela do sorteio, que não mostra o ato obsoleto que produziu o
  sinal.

**Achados da verificação, registrados e não tomados** — nenhum é da Atenção, e cada um pede decisão
ou medição própria:

- **O portal do candidato tem regra própria de fase** (`portal/leitura.py`, `_situacao_do_evento`):
  compara só o dia, sem a zona institucional, e chama de *em curso* o Evento pontual até a meia-noite.
  É a quarta leitura do Evento sem término.
- **O portal e o documento publicado não filtram `CANCELADO`**: um Evento cancelado aparece como
  qualquer outro. Hoje só a API o produz.
- **O pulso diz *"Encerra em…"* antes de o período abrir**, e mede o tempo do instante da montagem, e
  não do instante da leitura que ele mesmo declara (`supervisao.html:100-102`).
- ~~**Evento acrescentado por Retificação nasce sem `location` nem `isRegistrationPeriod`**~~
  (`interface/retificacao.py`, `_evento_completo`). **Resolvido** em 26/09/2026, mesclado no PR #179
  (`claude/dreamy-swartz-9ea9b4`). Confirmado, e mais cedo do que a suspeita dizia: a Retificação não
  chegava a publicar porque **nem nascia** — a elaboração recusava o ato com *"campo obrigatório não
  está presente"*. O Evento acrescentado passou a nascer com a forma publicada, a tela passou a
  oferecer o local, e `isRegistrationPeriod` ficou fora por decisão. O registro completo está em
  `doc/achado-evento-acrescentado-sem-local.md`.
