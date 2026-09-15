# Feature Specification: Estrutural de vagas — uma declaração só

**Feature Branch**: `claude/vagas-publicacao-apuracao-2753fa`

> **A numeração é `027` porque veio de `--number 27`**, e não da última pasta em `specs/`. A
> varredura de 14/09/2026 percorreu as cinco worktrees desta máquina: `specs/` vai até a `026` em
> todas, e nenhuma tem `027`.

> **Os identificadores continuam a faixa global**, política aberta pela `024` e confirmada pela
> `025`: duas features simultâneas em worktrees diferentes não descobrem o número uma da outra pela
> pasta. Teto medido em todas elas antes de escrever — `FR-315`, `SC-103`, `UX-039` —, e esta spec
> abre em `FR-316`, `SC-104`, `UX-040`. As **decisões** reiniciam em `D-001`, porque são lidas
> dentro da feature que as produziu.

**Created**: 2026-09-14

**Status**: Draft

**Input**: achado P0 da [auditoria exploratória de UX de 13/09/2026](../../doc/auditoria-exploratoria-ux-2026-09-13.md),
§4 fricção #1 (S4) e §11.1 — o único achado em que um Edital publicado hoje afirma ao candidato um
número que não governa nada.

> **A frase que governa:** a quantidade de vagas de um recorte é declarada **uma vez**, e é a mesma
> que o Edital publica e que a apuração usa.

> **E a frase que mantém o corte:** esta feature **reúne as duas declarações**. Não ocupa vaga, não
> convoca, não corta, e não reescreve nada que já foi publicado.

---

## 1. O achado que organiza a feature

No Perfil de Vaga há duas caixas de número. "Vagas imediatas" é o número que o Edital **publica**;
"Quadro de vagas › Ampla concorrência" é o número que a apuração **usa**. Quem preenche só a
primeira — que é a que tem rótulo em português corrente — publica um Edital íntegro por todos os
critérios que o sistema conhece, e inerte por todos os que importam depois.

A auditoria percorreu a cadeia inteira e mediu o silêncio em seis pontos:

| Onde o sistema poderia ter dito | O que ele disse |
|---|---|
| Etapa Perfis de Vaga | **CONCLUÍDA** |
| Etapa 9 · Revisão | **"Nada pendente — o Edital pode ser submetido"** |
| Confirmação da publicação | nada |
| Portal público e PDF | **"2 vagas imediatas"** |
| Emissão da classificação | emitida e publicada |
| Ocupação de vagas | "Este Edital não publicou quadro de vagas para este recorte. **Não há quantidade declarada a apurar.**" |
| Convocação | "Não há mais quem chamar dentro da faixa que o corte alcançou." |

As duas últimas frases são verdadeiras e chegam tarde demais: o Edital já é ato imutável, e a
correção já não é digitar de novo — é Retificar.

**Não é erro de quem digita.** Os três Editais da demonstração oficial estão na mesma condição —
`seed_demo` declara `immediateVacancies` para todos os Perfis e **nenhuma** linha de quadro, em
nenhum deles: 01/2026 com 3 vagas, 26/2026 com 40 e 51/2026 com 2. Os quatro Editais do ambiente
auditado também. Quem escreveu o sistema caiu na mesma armadilha ao escrever a demonstração dele.

### 1.1 É uma contradição constitucional, e não um incômodo de tela

O Princípio II abre com a exigência que este achado viola literalmente:

> *"Cada informação normativa estruturada DEVE possuir uma única fonte autoritativa. **Vagas**,
> perfis, cronogramas, cotas, requisitos [...] NÃO DEVEM existir como dados independentes e
> divergentes."*

Hoje a quantidade de vagas de um recorte existe em dois lugares, um deles governa o documento e o
outro governa a apuração, e nada os relaciona. É a definição de dado independente e divergente. O
mesmo princípio exige que telas e PDFs **derivem** da fonte estruturada quando tecnicamente
aplicável — e aqui é aplicável, porque um Perfil sem lista reservada tem exatamente uma lista de
concorrência, e o número dela já foi digitado.

### 1.2 A `025` está certa, e não é ela que muda

Dois campos existem porque o domínio precisa de dois. A `025` decidiu, e continua valendo:

- **Quadro parcial é legítimo**: um Perfil pode declarar linha para algumas Modalidades e não para
  outras.
- **Linha ausente nunca significa zero**: ausência diz *"o Edital não declarou"*, e `0` diz *"zero
  vagas"*.
- **A ampla concorrência mora na linha geral**, e não na Modalidade homônima, porque é o recorte que
  o sorteio consulta.
- **A soma é conferida contra o total** quando o quadro é completo, e o excesso é recusado sempre
  (`025`, FR-161 e FR-177).

> **As decisões da `025` são citadas aqui pelo que dizem, e não pelo número delas.** A numeração de
> decisão é lida dentro da feature que a produziu, e esta feature reinicia em `D-001`: um `D-006`
> escrito nesta página aponta para a decisão desta página, e não para a daquela.

O que está errado é o que a `025` não tinha por escopo: a interface põe os dois números **no mesmo
cartão**, rotula um em português corrente e deixa o outro sem explicação visível — a frase "Em
branco: quantidade não declarada" é `.oculto`, invisível a quem enxerga —, e a validação só os
relaciona quando existe regra de corte derivada do quadro. Fora desse caso, ninguém pergunta nada.

### 1.3 Onde a `026` desimpediu esta spec

O acervo já publicado não podia ser respondido antes, e agora pode:

- **O endereço existe.** A `025` criou a linha acrescentada por Retificação exatamente por isto, e
  deixou a razão escrita em `interface/retificacao.py`: *"Sem ela, nenhum Edital já publicado
  poderia ganhar quadro: todos eles foram publicados antes de a capacidade existir, e a coleção
  deles é vazia."*
- **A natureza está declarada.** O contrato de mutabilidade da `026` classifica
  `vacancyTable/immediateVacancies` e `vacancyTable/modalityId` como **retificáveis**, e a FR-304
  daquela feature exige que todo campo retificável seja alcançável **pelo canal do ator** — a tela,
  e não a API.
- **E a `026` nomeou esta spec.** Ela deixou fora de escopo, por escrito, *"a spec estrutural de
  vagas — ela vem depois, e vem obrigada a obedecer este contrato"*, e listou entre os itens que
  continuavam backlog *"o AVISO ligando 'vagas imediatas' à linha do quadro"*.

Sobra, portanto, exatamente o que esta feature faz: **fazer o sistema dizer quem precisa do ato, e
parar de produzir Editais novos que precisem dele.**

---

## 2. O que já existe, e que esta feature NÃO reconstrói

- **O quadro de vagas como coleção normativa do Perfil**, com identidade por linha, publicação no
  conteúdo canônico, endereçamento por identidade e Retificação que acrescenta, altera e remove
  linha (`025`).
- **A conferência da soma** — igualdade quando o quadro é completo, recusa do excesso sempre
  (`025`, FR-161 e FR-177). Esta feature não inventa conferência nova; ela faz a conferência ter o
  que conferir.
- **A declaração de qual Modalidade é a da ampla concorrência**, que já existe no Perfil e cuja
  ausência significa *"este Perfil não declara nenhuma"* (`014`). Casar o nome foi recusado por
  escrito (`025`, R-006) e continua recusado.
- **A Revisão que lê do conteúdo canônico**, e por isso já exibe as linhas do quadro quando elas
  existem. O que falta é o que ela diz quando elas **não** existem.
- **A severidade de advertência na validação de publicação**, que já distingue erro de aviso e já
  encaminha cada pendência para a etapa que a resolve.
- **O contrato de mutabilidade** (`026`), que governa esta feature em vez de ser alterado por ela.

---

## 3. Decisões fechadas antes do planejamento

### D-001 — A linha geral não é digitada: ela é a vaga imediata do Perfil

Um Perfil sem lista reservada tem exatamente uma lista de concorrência. Pedir o mesmo número duas
vezes não é redundância inofensiva: é a criação da divergência que o Princípio II proíbe. Enquanto
o Perfil não declarar lista reservada, a linha geral do quadro é **derivada** do total de vagas
imediatas declarado por quem compõe, e não existe caixa onde digitá-la diferente.

Derivar não é calcular: a fonte é o número que a própria pessoa declarou no mesmo Perfil, e nunca
percentual, fundamento normativo ou campo da Regra Normativa — a FR-157 da `025` continua inteira.

### D-002 — O bloco do quadro aparece quando existe a primeira lista reservada, e não antes

**Lista reservada** é uma Modalidade declarada no Perfil que **não** seja aquela que o Perfil
declara ser a da ampla concorrência. Enquanto não houver nenhuma, o bloco "Quadro de vagas" não é
desenhado — não há repartição a pedir, e desenhá-lo é o que produz o defeito.

Declarada a primeira, o bloco aparece com a linha geral já preenchida com o total e pede a
repartição, conferida contra ele. É a partir daí que a linha geral passa a ser **declarada**: ela
carrega a ampla concorrência, que já não é o total.

### D-003 — Repartição incompleta continua legítima, e deixa de ser silenciosa

A D-006 da `025` está certa e não é revogada: um Edital pode declarar linha para uma lista e não
para outra, e ausência nunca é zero. O que muda é que o sistema **diz** — advertência explícita, na
etapa que a resolve, na Revisão e na confirmação da publicação, nomeando cada lista sem linha e a
consequência: aquele recorte não terá quantidade a apurar.

Advertência, e não recusa. Recusar transformaria "o Edital não declarou" em "o Edital não pode
existir", que é o oposto do que a `025` decidiu e do que os Editais reais fazem.

### D-004 — A linha geral deixa de ser omissível; as reservadas continuam opcionais

A FR-160 da `025` — *"o quadro MUST ser opcional: um Perfil sem quadro declarado MUST permanecer
submetível e publicável"* — **fica estreitada por esta feature, e só nesta metade**: com a
derivação da D-001, a linha geral existe sempre, e um Perfil submetido ou publicado sem ela passa a
ser recusado. As linhas reservadas do quadro seguem opcionais, pela D-003.

A mudança é declarada aqui porque é mudança de decisão anterior, e decisão anterior não se altera
por efeito colateral. O que a `025` protegia — que o sistema não invente quantidade — continua
protegido: a linha geral não é inventada, é o número que a pessoa declarou.

### D-005 — A derivação acontece na autoria e na publicação, nunca na leitura

O conteúdo publicado sai com a linha geral **escrita nele**, com identidade própria, como qualquer
outra linha. Nenhuma leitura infere linha ausente.

A alternativa — derivar na leitura, e com isso fazer o acervo antigo apurar sem ato nenhum — foi
**recusada por duas razões, e a segunda é medida**. A primeira é constitucional: publicação é ato
imutável, e fazer um Edital publicado passar a afirmar uma quantidade que ele não publicou é
reescrevê-lo por interpretação. A segunda é que **não funcionaria**: a derivação só é inequívoca
onde não há lista reservada, e os três Editais da demonstração declaram Modalidade — nenhum deles
declara qual é a da ampla concorrência. Derivar na leitura conserta **zero** dos três Editais que a
auditoria mostrou quebrados. A auditoria contemplou essa migração de leitura em §11.1 ao medir o
risco; a medição acima é a resposta.

### D-006 — O acervo publicado muda por Retificação, e o sistema mostra quem precisa dela

Nada é convertido, preenchido ou reescrito automaticamente. O que o sistema passa a fazer é
**dizer**: quais Editais publicados publicam vaga imediata sem linha correspondente, quais recortes
ficam sem quantidade a apurar, e qual é o ato que declara — a Retificação do Perfil, pelo caminho
que a `025` abriu e que a `026` obrigou a existir na tela.

A Ocupação e a Convocação deixam de terminar em constatação. A frase continua verdadeira e ganha
uma segunda metade: o ato que a resolve, e onde ele se pratica.

### D-007 — Acrescentar linha a Edital publicado vale para o que vier, e não alcança ato praticado

Ordem emitida, resultado publicado e convocação feita permanecem como estão. A Retificação dá ao
Edital a quantidade que ele não tinha, e é dela em diante que a apuração passa a existir. É a mesma
regra que a `026` fixou para o método do sorteio (FR-309), e pela mesma razão.

### D-008 — O total e a linha geral mudam no mesmo ato

Num Perfil sem lista reservada os dois números são o mesmo número. Uma Retificação que altere um e
não o outro publicaria de novo, e por outro caminho, exatamente a divergência que esta feature
existe para eliminar: é recusada, com os dois números ditos. É a leitura da SC-049 da `025` —
*"os dois movimentos são um ato só"* — aplicada ao caso simples.

### D-009 — A demonstração oficial passa a publicar quadro

`seed_demo` não é ilustração: é o Edital que qualquer pessoa abre para entender o sistema, e hoje
ele **ensina o defeito**. Ele passa a declarar quadro nos três Editais, com pelo menos um Perfil
repartido por lista reservada e um sem lista reservada nenhuma, de modo que a Ocupação e a
Convocação tenham quantidade a apurar — que é a jornada que o Princípio VI exige demonstrável.

### D-010 — Esta feature não ocupa, não convoca e não corta

A FR-175 da `025` continua inteira. O que esta spec entrega é a quantidade declarada uma vez e dita
em voz alta; quem a consome já existe e não muda.

---

## 4. Problema

Quem compõe um Edital digita a quantidade de vagas no campo que tem rótulo em português corrente,
conclui todas as etapas, é informado de que nada está pendente, publica, e descobre semanas depois
— na tela de Ocupação, quando já não há como corrigir sem Retificar — que o número digitado não
governa nada. Quem lê o Edital publicado, inclusive o candidato, lê um número verdadeiro como
documento e inerte como norma operante.

O estado medido em 13/09/2026:

```
Editais da demonstração oficial sem linha de quadro      3 de 3
Editais do ambiente auditado sem linha de quadro         4 de 4
Pontos da cadeia que poderiam ter avisado e não avisam   6
Editais em que a apuração tem quantidade a apurar        0
```

Esta feature não acrescenta capacidade nova de apuração: ela faz a capacidade que já existe receber
o número de que precisa, e faz o sistema parar de produzir Editais que nasçam sem ele.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Compor um Perfil simples sem descobrir que há dois números (Priority: P1)

Quem compõe abre um Perfil que não declara cota nenhuma, escreve `2` em vagas imediatas e segue.
Não existe um segundo campo, não existe bloco a preencher, e o Edital publicado apura por aquele
`2` — o mesmo que o portal e o PDF publicam.

**Why this priority**: é o caso mais comum e o que produz o defeito hoje. Sem ele, todo o resto é
remendo sobre a armadilha em vez da remoção dela.

**Independent Test**: compor um Perfil sem Modalidade, publicar e abrir a Ocupação — a quantidade a
apurar é a mesma que o documento publica, sem que nada além do total tenha sido digitado.

**Acceptance Scenarios**:

1. **Given** um Perfil sem Modalidade declarada, **When** quem compõe declara 2 vagas imediatas,
   **Then** a tela não oferece nenhum segundo campo para a mesma quantidade, e o Perfil passa a ter
   linha geral de 2.
2. **Given** o mesmo Perfil, **When** o Edital é publicado, **Then** o conteúdo publicado carrega a
   linha geral escrita nele, com identidade própria, e o documento a exibe.
3. **Given** o Edital publicado, **When** a Ocupação é aberta no recorte da ampla concorrência,
   **Then** há quantidade declarada a apurar, e ela é 2.
4. **Given** um Perfil de cadastro de reserva com zero vagas imediatas, **When** ele é publicado,
   **Then** a linha geral publicada é `0` — que é o que o Edital afirma —, e nenhuma tela diz que
   ele não declarou quadro.

---

### User Story 2 — Repartir quando a primeira lista reservada aparece (Priority: P1)

O mesmo Perfil ganha uma Modalidade PPI. O bloco "Quadro de vagas" aparece então — e não antes —,
já com a linha geral preenchida com o total, e pede quantas vagas cabem em cada lista. A soma é
conferida contra o total, em números.

**Why this priority**: é a metade que o domínio realmente precisa de dois campos, e é onde a
divergência passa a ser informação e não defeito.

**Independent Test**: acrescentar a primeira Modalidade a um Perfil e ver o bloco surgir preenchido,
repartir, e ver a conferência recusar a soma que não fecha.

**Acceptance Scenarios**:

1. **Given** um Perfil com 80 vagas imediatas e nenhuma lista reservada, **When** quem compõe
   declara a Modalidade PPI, **Then** o bloco do quadro aparece com a linha geral em 80 e pede a
   repartição, com uma frase visível explicando por que ele apareceu agora.
2. **Given** o bloco aberto, **When** quem compõe declara PPI 20 e reduz a linha geral para 60,
   **Then** a soma fecha em 80 e nada é recusado.
3. **Given** o mesmo bloco, **When** a linha geral fica em 80 e PPI em 20, **Then** a submissão é
   recusada porque a soma excede o total, com os três números ditos.
4. **Given** um Perfil que declara a Modalidade "Ampla concorrência" **e** a declara como a da ampla
   concorrência, **When** ela é a única Modalidade, **Then** não há lista reservada, o bloco não
   aparece e a linha geral continua derivada do total.
5. **Given** um Perfil com duas Modalidades e nenhuma declarada como a da ampla concorrência,
   **When** ele é revisado, **Then** há advertência própria dizendo isso, distinta da advertência de
   lista sem linha.
6. **Given** um Perfil com lista reservada, **When** a última lista reservada é removida, **Then** a
   linha geral volta a ser derivada do total, e nenhuma quantidade divergente sobrevive em silêncio.

---

### User Story 3 — Ser avisado do que ficará inerte, antes de publicar (Priority: P1)

Quem submete vê, no mesmo bloco de cada Perfil da Revisão, o total que o Edital vai publicar e o
quadro que ele vai publicar, lado a lado. Onde uma lista reservada não tem linha, a Revisão diz qual
é e o que acontecerá com ela. A confirmação da publicação repete.

**Why this priority**: é o ponto em que a correção ainda é barata. Depois da publicação, a mesma
informação custa uma Retificação.

**Independent Test**: submeter um Edital com uma lista reservada sem linha e ver a advertência na
etapa que a resolve, na Revisão e na confirmação — sem que a submissão seja bloqueada.

**Acceptance Scenarios**:

1. **Given** um Perfil com PPI declarada e sem linha para ela, **When** a Revisão é aberta, **Then**
   ela exibe o total e o quadro lado a lado e adverte, nomeando PPI, que aquele recorte não terá
   quantidade a apurar.
2. **Given** o mesmo Edital, **When** a Revisão é aberta, **Then** ela não afirma que nada está
   pendente.
3. **Given** a mesma advertência, **When** a publicação é confirmada, **Then** a confirmação a
   repete, em números, e a publicação prossegue se quem publica confirmar.
4. **Given** um Perfil sem lista reservada nenhuma, **When** a Revisão é aberta, **Then** não há
   advertência alguma, porque não há repartição a declarar.

---

### User Story 4 — Declarar o quadro de um Edital já publicado (Priority: P1)

Um dos Editais publicados antes desta feature publica 40 vagas e nenhuma linha. Quem tem competência
abre a Retificação, acrescenta a linha geral pela tela, publica a Retificação — e a Ocupação daquele
Edital passa a ter quantidade a apurar. A ordem já emitida não muda.

**Why this priority**: é o acervo inteiro. Sem isto a feature conserta o futuro e deixa quatro
Editais reais e três de demonstração inertes para sempre.

**Independent Test**: retificar um Edital publicado sem quadro acrescentando a linha geral, pelo
canal do ator, e ver a Ocupação apurar — sem shell, sem API, sem tocar no banco.

**Acceptance Scenarios**:

1. **Given** um Edital publicado cujo Perfil publica 40 vagas e nenhuma linha, **When** uma
   Retificação acrescenta a linha geral com 40, **Then** ela é publicada e a Ocupação passa a ter
   quantidade a apurar naquele recorte.
2. **Given** o mesmo Edital, **When** a Retificação é publicada, **Then** a ordem já emitida, o
   resultado já publicado e as convocações já feitas permanecem como estavam.
3. **Given** um Edital publicado sem lista reservada, **When** uma Retificação altera o total de
   vagas imediatas e não altera a linha geral, **Then** ela é recusada, dizendo os dois números e o
   que falta mudar.
4. **Given** um Edital publicado com quadro, **When** qualquer leitura o consulta, **Then** ela lê o
   que está publicado e não infere linha ausente.
5. **Given** o conteúdo publicado de qualquer Edital anterior a esta feature, **When** nada é
   retificado, **Then** ele permanece idêntico, com o mesmo resumo canônico.

---

### User Story 5 — Encontrar, no acervo, quem precisa do ato (Priority: P2)

Quem supervisiona não descobre o problema Edital por Edital, na tela de Ocupação, meses depois. O
sistema diz quais Editais publicados publicam vaga imediata sem linha correspondente, e quais
recortes ficam sem quantidade.

**Why this priority**: sem isto a US4 é possível e invisível — dependeria de alguém abrir cada
Edital para descobrir que precisa dela.

**Independent Test**: semear o acervo no estado de hoje e ver a lista nomear os Editais e os
recortes afetados.

**Acceptance Scenarios**:

1. **Given** um acervo com Editais publicados sem linha de quadro, **When** a lista é consultada,
   **Then** ela nomeia cada Edital, cada Perfil e cada recorte sem quantidade a apurar.
2. **Given** a tela de Ocupação de um desses Editais, **When** ela é aberta, **Then** a frase de
   ausência nomeia o ato que declara a quantidade e o Perfil a que ele se aplica.
3. **Given** a mesma tela, **When** ela é aberta, **Then** nada é retificado por ela: apontar o ato
   não é praticá-lo.

---

### User Story 6 — A demonstração oficial deixa de ensinar o defeito (Priority: P2)

Quem abre a demonstração encontra Editais que publicam quadro, apuram ocupação e convocam — e um
Perfil repartido por lista reservada, para que a repartição também se veja.

**Why this priority**: é a jornada demonstrável de que o Princípio VI depende, e hoje ela demonstra
o contrário do que a feature entrega.

**Independent Test**: semear a demonstração e percorrer, nos três Editais, do documento publicado
até a Ocupação com quantidade a apurar.

**Acceptance Scenarios**:

1. **Given** a demonstração recém-semeada, **When** a Ocupação de cada um dos três Editais é aberta,
   **Then** há quantidade declarada a apurar em cada recorte que o Edital publica.
2. **Given** a demonstração, **When** os Perfis são lidos, **Then** ao menos um reparte vagas por
   lista reservada e ao menos um não declara lista reservada nenhuma.
3. **Given** um Perfil da demonstração que declara Modalidade homônima da ampla concorrência,
   **When** ele é lido, **Then** ele declara qual delas é a da ampla concorrência.

---

### Edge Cases

- **Perfil com zero vagas imediatas.** A linha geral publicada é `0`, e `0` diz zero — não "não
  declarou". É o que o Edital afirma, e é o que a apuração deve ler.
- **Perfil só de cadastro de reserva.** Continua sem repartição de cadastro de reserva, que não é
  desta feature; a linha geral de vaga imediata é publicada do mesmo jeito.
- **Modalidade única homônima da ampla concorrência, declarada como tal.** Não é lista reservada: o
  bloco não aparece e a linha geral segue derivada.
- **Modalidade declarada e nenhuma apontada como a da ampla concorrência.** Advertência própria,
  porque o ato que a resolve é outro — declarar qual é, e não escrever uma linha.
- **Retificação que acrescenta a primeira Modalidade a um Edital publicado.** O quadro publicado
  fica parcial, que é legítimo; a conferência da Retificação adverte, como a submissão adverteria, e
  não recusa.
- **Retificação que remove a última lista reservada de um Edital publicado.** A linha geral
  publicada permanece; ela é conteúdo, e não derivação, depois de publicada.
- **Soma das listas reservadas maior que o total.** Recusada, como já é hoje.
- **Perfil cuja linha geral é zerada pelo operador com listas reservadas somando o total.** É
  legítimo: o Edital reserva todas as vagas, e a ampla concorrência tem zero.
- **Edital publicado que ganha linha depois de a classificação ter sido emitida.** A ordem não muda;
  a apuração passa a existir dali em diante.
- **Repartição pedida e ignorada.** Declarada a primeira lista reservada, a linha geral fica no
  total com que foi pré-preenchida (`FR-321`), e é esse número que o Edital publica para a ampla
  concorrência enquanto ninguém o repartir. É quadro parcial, é legítimo, e é advertido em números
  (`FR-324`) — mas não é zerado nem retido: zerar inventaria uma repartição que o Edital não
  declarou, e reter impediria de publicar o que a `025` decidiu que é publicável.

---

## Requirements *(mandatory)*

### Functional Requirements

#### A declaração única

- **FR-316**: Um Perfil sem lista reservada MUST ter exatamente um lugar onde a quantidade de vagas
  imediatas é declarada, e a interface MUST NOT oferecer um segundo campo para o mesmo número.
- **FR-317**: **Lista reservada** MUST significar uma Modalidade de Concorrência declarada no Perfil
  distinta daquela que o Perfil declara ser a da ampla concorrência; a identificação MUST vir da
  declaração do Edital e NÃO DEVE ser feita casando denominação.

  > **Lista reservada não é linha reservada, e a diferença de uma letra é cara.** A **lista** é a
  > Modalidade — um recorte de concorrência. A **linha** é o que o quadro escreve sobre ela — uma
  > quantidade com identidade própria, no vocabulário que a `025` fixou. Uma lista reservada sem
  > linha é o caso inteiro da FR-324, e dizer "linha" onde se quer dizer "lista" troca o defeito
  > pela sua ausência.
- **FR-318**: Enquanto o Perfil não declarar lista reservada, a linha geral do quadro MUST ser
  derivada do total de vagas imediatas declarado no Perfil, inclusive quando esse total é zero.
- **FR-319**: A derivação MUST NOT ter outra fonte que o total declarado no próprio Perfil — nunca
  percentual, fundamento normativo ou qualquer campo da Regra Normativa (`025`, FR-157).
- **FR-320**: A derivação MUST NOT alterar, sobrescrever ou recalcular o total de vagas imediatas,
  que continua declarado por quem compõe (`025`, FR-162).
- **FR-321**: Declarada a primeira lista reservada, o bloco do quadro MUST aparecer com a linha geral
  preenchida com o total e MUST pedir a repartição das listas reservadas, com a soma conferida
  contra o total (`025`, FR-161 e FR-177, que continuam valendo sem alteração).
- **FR-322**: Removida a última lista reservada de um Perfil ainda não publicado, a linha geral MUST
  voltar a ser derivada do total, e nenhuma quantidade divergente MUST sobreviver sem ser dita na
  tela.
- **FR-323**: Um Perfil MUST NOT ser submetido nem publicado sem linha geral; as linhas reservadas
  do quadro permanecem opcionais (D-003, D-004). A exigência alcança a submissão e a publicação de Edital
  composto por este assistente, e NÃO DEVE alcançar a Retificação de Edital publicado antes desta
  feature: recusar ali bloquearia correções que nada têm com vagas, e coagir não é o mecanismo —
  para o acervo valem a FR-331 e a FR-332.

#### O que o sistema diz antes de publicar

- **FR-324**: Lista reservada sem linha MUST produzir advertência que nomeie cada lista afetada e a
  consequência — aquele recorte não terá quantidade a apurar —, e a advertência MUST NOT bloquear a
  submissão nem a publicação.
- **FR-325**: Perfil que declara Modalidade e não declara qual delas é a da ampla concorrência MUST
  produzir advertência própria, distinta da anterior, porque o ato que a resolve é outro (`025`,
  FR-176).
- **FR-326**: A etapa de Revisão MUST exibir, no bloco de cada Perfil, o total de vagas imediatas e
  o quadro lado a lado, inclusive quando o quadro não cobre todas as listas declaradas.
- **FR-327**: As advertências desta feature MUST aparecer na etapa do assistente que as resolve e na
  Revisão, e a Revisão MUST NOT afirmar que nada está pendente enquanto alguma delas existir.
- **FR-328**: A confirmação da publicação MUST repetir as advertências pendentes, dizendo em números
  o que o Edital publicará e o que a apuração alcançará.
- **FR-329**: A publicação MUST emitir a linha geral no conteúdo publicado, com identidade própria,
  como qualquer outra linha, e o documento MUST exibi-la na ordem declarada, com a linha geral em
  primeiro lugar (`025`, FR-169).

#### O acervo publicado

- **FR-330**: Nenhuma leitura de conteúdo publicado MUST inferir, derivar ou completar linha de
  quadro ausente; o publicado é lido como foi publicado (D-005).
- **FR-331**: O sistema MUST identificar, pelo canal do ator, os Editais publicados cujo Perfil
  publica vagas imediatas e não publica linha correspondente, nomeando o Edital, o Perfil e os
  recortes que ficam sem quantidade a apurar.
- **FR-332**: Onde a apuração não tem quantidade declarada, a mensagem MUST nomear o ato que a
  declara — a Retificação daquele Perfil — e MUST NOT praticá-lo.
- **FR-333**: Esta feature MUST NOT converter, preencher, migrar nem reescrever conteúdo publicado;
  o acervo muda exclusivamente por Retificação (Princípio II).
- **FR-334**: A Retificação que acrescente linha ao quadro de um Edital publicado MUST NOT alcançar
  ato já praticado — ordem emitida, resultado publicado, convocação feita — e vale para o que vier
  (`026`, FR-309).
- **FR-335**: A Retificação que altere o total de vagas imediatas de um Perfil publicado que
  **publica linha geral** e não declara lista reservada MUST exigir que a linha geral mude no mesmo
  ato, recusando quem altere só um dos dois e dizendo os dois números. Onde o Perfil publicado não
  tem linha geral — o acervo anterior a esta feature —, a conferência MUST advertir em vez de
  recusar, dizendo que o total alterado continua sem governar a apuração e nomeando o ato que o
  resolve.
- **FR-336**: A conferência da Retificação MUST dizer, sobre o conteúdo que ela produziria, o mesmo
  que a submissão diz sobre o rascunho, advertências inclusive — com a **única** exceção que a
  FR-323 nomeia: a ausência de linha geral, impeditiva no ato de publicação, NÃO DEVE ser dita como
  impedimento no ato de Retificação.

  > **A exceção é uma, e é esta.** Escrita sem ela, a FR-336 lida ao pé da letra manda fechar a
  > brecha que a FR-323 abriu de propósito — e quem a fechar estará prendendo o acervo inteiro
  > achando que obedece à spec. Estendê-la a qualquer outro achado exige decisão escrita.
- **FR-337**: Todo campo que esta feature faça alcançável MUST obedecer ao contrato de mutabilidade
  vigente, e esta feature MUST NOT alterar a natureza declarada de campo algum (`026`, FR-297).

#### A demonstração

- **FR-338**: A demonstração oficial MUST publicar quadro nos seus Editais, de modo que a Ocupação e
  a Convocação tenham quantidade a apurar em cada recorte publicado.
- **FR-339**: A demonstração MUST incluir ao menos um Perfil com repartição por lista reservada e ao
  menos um sem lista reservada nenhuma, e MUST declarar qual Modalidade é a da ampla concorrência
  onde declarar Modalidade homônima.

#### O corte

- **FR-340**: Esta feature MUST NOT ocupar vaga, atribuir candidato a lista, remanejar, convocar nem
  cortar (`025`, FR-175).

### Requisitos de apresentação

- **UX-040**: O cartão do Perfil MUST NOT apresentar dois campos numéricos para a mesma quantidade.
- **UX-041**: A chegada do bloco do quadro MUST ser explicada por frase visível na tela, e nenhuma
  explicação necessária à decisão MUST depender de conteúdo oculto a quem enxerga.
- **UX-042**: A linha geral MUST ser identificada como a da ampla concorrência onde quer que apareça
  — composição, Revisão, documento publicado e Retificação —, sem depender de cor (`025`, UX-022).
- **UX-043**: A Revisão MUST mostrar o total e o quadro no mesmo bloco do Perfil, lado a lado.
- **UX-044**: Toda advertência desta feature MUST ser dita em números — o que o Perfil publica, o que
  o quadro reparte e o que fica sem quantidade —, e nunca apenas sinalizada.
- **UX-045**: A mensagem de ausência de quantidade na Ocupação e na Convocação MUST nomear o ato que
  a declara e o Perfil a que ele se aplica.
- **UX-046**: A leitura do acervo exigida pela FR-331 MUST chegar a quem supervisiona pelo caminho
  que ele já percorre, junto dos demais sinais do Processo, e NÃO DEVE exigir tela nova nem visita
  Edital a Edital.

  > **Acrescentado no planejamento, e declarado por isso.** A FR-331 exigia a leitura e não dizia
  > por onde ela chega; o plano encontrou a supervisão do Processo, que já monta sinais por Edital
  > com destino e alcance por ator, e a ausência de requisito de apresentação teria deixado a
  > escolha para quem implementa.

### Key Entities

- **Perfil de Vaga**: já existe. O total de vagas imediatas continua declarado por quem compõe, e
  passa a ser a fonte da linha geral enquanto não houver lista reservada.
- **Linha do quadro de vagas**: já existe (`025`). A linha geral passa a nascer derivada e a ser
  publicada sempre; as reservadas continuam declaradas e opcionais.
- **Modalidade de Concorrência**: já existe e não muda. Passa a decidir, pela declaração de qual
  delas é a da ampla concorrência, se existe lista reservada no Perfil.
- **Advertência de publicação**: já existe como severidade da validação. Ganha os casos desta
  feature e o encaminhamento para a etapa que os resolve.

---

## 5. Invariantes observáveis

Verificáveis a qualquer momento, em qualquer estado do acervo:

1. Nenhuma quantidade de vagas de um recorte é declarável em dois lugares ao mesmo tempo.
2. Todo Perfil publicado por esta interface depois desta feature publica linha geral.
3. Nenhuma linha de quadro é inferida na leitura de conteúdo publicado.
4. Nenhum conteúdo publicado muda sem Retificação.
5. Nenhuma advertência desta feature bloqueia submissão ou publicação.
6. Nenhuma tela que constata ausência de quantidade deixa de nomear o ato que a declara.
7. Nenhuma tela desta feature ocupa vaga, convoca ou corta.
8. Nenhuma quantidade derivada tem outra fonte que o total declarado no próprio Perfil.

> **O oitavo é o que a `025` escreveu como primeiro dela, um degrau adiante.** Lá a proibição era
> derivar quantidade de percentual; aqui existe uma derivação legítima, e o invariante é o que a
> mantém com **uma** fonte. Sem ele, a FR-319 seria a única proibição desta feature sem nada que a
> verificasse — e proibição sem guarda é a forma como uma razão deixa de valer sem que ninguém
> perceba.

---

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-104**: Quem compõe um Perfil sem lista reservada declara a quantidade de vagas **uma vez**, e
  o Edital publicado apura por ela — zero campos redigitados e zero conhecimento prévio exigido.
- **SC-105**: 100% dos Editais publicados por esta interface depois desta feature chegam à Ocupação
  com quantidade declarada a apurar no recorte da ampla concorrência.
- **SC-106**: Em 100% dos Perfis com lista reservada sem linha, a Revisão e a confirmação da
  publicação dizem, em números e nomeando o recorte, o que ficará sem quantidade a apurar.
- **SC-107**: Os três Editais da demonstração oficial publicam quadro, e a Ocupação apura quantidade
  em cada recorte que eles publicam — hoje são 0 de 3.
- **SC-108**: Para 100% dos Editais publicados antes desta feature que publicam vaga imediata sem
  linha correspondente, o sistema os nomeia e aponta o ato, sem que nenhum conteúdo publicado mude
  por si.
- **SC-109**: O ciclo do acervo — retificar um Edital publicado acrescentando a linha geral e ver a
  Ocupação passar a apurar — é percorrido em uma sessão, pelo canal do ator, sem shell, sem API e
  sem manipulação de banco.
- **SC-110**: 100% dos conteúdos publicados antes desta feature permanecem com o mesmo resumo
  canônico até que uma Retificação os alcance.
- **SC-111**: Nenhuma pessoa precisa saber que existiram dois campos para compor um Edital correto —
  verificável por percurso de composição sem consulta a documentação.

---

## 7. Out of Scope

Fora deste incremento, e por decisão:

- **Ocupar vaga, convocar, cortar e remanejar.** Continuam onde estão (`025`, FR-175).
- **Repartir o cadastro de reserva por Modalidade**, que a `025` deixou fora com razão escrita. O
  `76/2026` continua sendo o Edital que pedirá essa repartição, e continua sendo registro.
- **Reconciliar as duas grafias da ampla concorrência no domínio do sorteio** (`025`, §7). Esta
  feature usa a declaração que o Edital faz, e não reescreve o ato de ordenação.
- **Converter o acervo publicado automaticamente** (D-005, D-006). Publicação é ato imutável.
- **Depreciar os campos da Regra Normativa.** A `025` decidiu que a preservação do que já foi
  publicado é obrigatória e que a depreciação futura é pergunta aberta; esta feature não a reabre.
- **Alterar o contrato de mutabilidade** (`026`). Esta feature o obedece.
- **Os demais achados da auditoria de 13/09/2026** — o cronograma vencido do Edital copiado, a
  microcópia invisível como classe, o segundo Edital no mesmo Processo, a porta de entrada de quem
  julga recurso, as trinta decisões da Classificação. São registro, e o Princípio VI proíbe derivar
  deles automaticamente a prioridade da spec seguinte.

---

## Assumptions

- A `025` está entregue e o quadro de vagas existe como coleção normativa do Perfil, publicável,
  endereçável por identidade e retificável — inclusive a linha acrescentada por Retificação, que é o
  que torna o acervo alcançável.
- A `026` está entregue e o contrato de mutabilidade classifica os campos da linha do quadro como
  retificáveis, com caminho exigido pelo canal do ator.
- A declaração de qual Modalidade é a da ampla concorrência já existe no Perfil, e sua ausência
  significa "este Perfil não declara nenhuma" — nunca "a primeira serve".
- A validação de publicação já distingue erro de advertência e já encaminha cada pendência para a
  etapa do assistente que a resolve; esta feature acrescenta casos, e não mecanismo.
- Os quatro Editais do ambiente auditado estão na mesma condição dos três da demonstração. A
  medição de 13/09/2026 é a fonte; os três da demonstração foram reconferidos no código em
  14/09/2026.
- Nenhum Edital publicado até hoje declara linha de quadro, de modo que não há acervo misto a
  conciliar: a resposta ao acervo é uniforme.
