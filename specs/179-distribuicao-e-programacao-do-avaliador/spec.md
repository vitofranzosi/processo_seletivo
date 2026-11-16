# Feature Specification: A distribuição coerente com a agenda e a programação de quem avalia

**Feature Branch**: `claude/agenda-bancas-comunicacao-078bfc`, sobre a `main` em `619a4ae0`

**Created**: 2026-11-16

**Status**: Especificada em 16/11/2026, a partir do estudo do mesmo dia
([doc/estudo-agenda-para-as-bancas-2026-11-16.md](../../doc/estudo-agenda-para-as-bancas-2026-11-16.md)),
autorizada pelo usuário na terceira rodada dele. **Dois incrementos**, que se implementam em ordem:
o **Incremento 1** (distribuição coerente e programação no GPS) e o **Incremento 2** (aviso por
e-mail ao avaliador). O segundo usa a programação e os destinatários que o primeiro define, e não o
reformula. As três decisões que estavam recomendadas foram aprovadas pelo usuário no mesmo dia
(ver *Clarifications*); plan e tasks no mesmo dia.

**Input**: o pedido de 16/11/2026 para que cada banca receba por e-mail a programação das
entrevistas; as duas rodadas do estudo, que mostraram que a pergunta certa não é "quem está na
banca", e sim "quem avalia cada candidato, e quando"; e a direção do usuário na terceira rodada:
corrigir primeiro a coerência da distribuição, mostrar a programação na Mesa e em Minhas atividades,
e depois comunicar por e-mail, sem cadastro de e-mail nas bancas.

> **Faixa de identificadores.** Esta spec abre em **FR-8200**, **SC-2840** e **UX-970**, e reserva até
> o requisito oito mil duzentos e quarenta e nove, o critério dois mil oitocentos e cinquenta e nove
> e o requisito de experiência novecentos e oitenta e nove. Nasceu como `178`, na faixa a partir do
> requisito oito mil cento e cinquenta e do critério dois mil oitocentos e vinte; no mesmo dia, a
> spec dos documentos em PDF/A foi mergeada na `main` (#581) com a pasta `178` e essa mesma faixa, e
> esta passou a `179`, com os requisitos deslocados em cinquenta e os critérios em vinte, sem mudar
> de conteúdo. Os requisitos de experiência não colidiam e ficaram. A pasta `179` e a faixa nova
> estavam livres na `main` em `4ce126af`, no único PR aberto e nas worktrees locais. As decisões
> reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-020 da `012`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

A `167` deu a cada candidato um horário publicado, numa banca, com local ou sala. A `012` deu a cada
avaliador as inscrições que ele avalia, pela Atribuição, e a Mesa as lista. **As duas metades nunca
se encontraram.** A Mesa não mostra horário; a Distribuição não lê a agenda; e nada impede que a
mesma pessoa receba dois candidatos no mesmo horário, em duas bancas.

O estudo mediu isso com o próprio código do rodízio, no caso que o pedido descreveu — 43 candidatos,
6 avaliadores, 3 bancas simultâneas, dupla avaliação. O rodízio forma três duplas fixas, mas as
reparte na ordem do protocolo, que não tem relação com o horário: em cinco sorteios da ordem dos
protocolos, a mesma dupla ficou com dois candidatos ao mesmo tempo em 8, 10, 10, 13 e 14 dos 15
horários. Percorrendo as inscrições na ordem da agenda, o mesmo código deu zero, nos três sorteios
testados.

Por isso a comissão monta, fora do GPS, a planilha de "quem atende quem, quando e onde", e a manda
aos avaliadores por e-mail. É essa planilha que esta feature elimina.

**O princípio.** A Etapa é o eixo. A Atribuição diz quem avalia cada candidato; o horário publicado
diz quando e onde. A programação de um avaliador é o cruzamento dos dois, e não um cadastro. A banca
continua sendo ponto de atendimento, e não grupo de pessoas, como a `167` decidiu.

### O que esta spec cobre, e o que fica fora

**Incremento 1 — distribuição coerente e programação no GPS:**

- a definição de conflito de horário de um avaliador, considerando a duração de cada atendimento;
- a recusa de atribuição que cria conflito, no lote e no rodízio, e o rodízio que percorre a agenda;
- o filtro por dia e banca na Distribuição, para atribuir uma sessão inteira num gesto;
- a visão do que a agenda mudou depois de distribuída, com os conflitos que ela criou;
- a programação na Mesa e a próxima entrevista em Minhas atividades;
- quem avalia cada pessoa, na agenda publicada da gestão, e só nela.

**Incremento 2 — o aviso por e-mail ao avaliador:**

- um aviso individual, sem lista, com o link para a programação na Mesa;
- o envio decidido pela comissão, quando a programação está pronta, e o aviso das mudanças depois;
- a revisão da FR-084 da `010`, que passa a admitir uma oitava situação.

**Fica fora:** cadastro de e-mail nas bancas; composição fixa de banca; lista de candidatos no
e-mail; anexo; envio automático a cada remarcação; redistribuição automática; conflito entre
Editais diferentes; disponibilidade declarada pelo avaliador; arquivo de calendário. Ver *Out of
Scope*.

## Clarifications

### Session 2026-11-16 (direção do usuário, terceira rodada do estudo)

- Q: Cadastrar e-mail nas bancas? → A: **Não.** A Etapa é o eixo, e os vínculos que existem bastam.
- Q: Abandonar o e-mail em favor da programação no GPS? → A: **Não.** A programação no GPS é a
  fonte; o e-mail avisa que ela existe e que mudou, porque não se pode presumir que todo avaliador
  entre no GPS por conta própria.
- Q: O conflito de horário é aviso ou integridade? → A: **Integridade operacional**, sem bloquear
  quando a distribuição ainda não aconteceu (`D-002`, `D-003`).
- Q: "Avaliam: …" pode aparecer na agenda? → A: **Só na visão interna da comissão**, com permissão
  explícita, e nunca no que é público (`D-007`).

### Session 2026-11-16 (decisões do usuário sobre as recomendações da spec)

- Q-A: A remarcação depois da publicação, que é ato da agenda e às vezes urgente, pode criar um
  conflito para quem avalia a pessoa? → A: **Sim**, desde que a confirmação identifique quem ficará
  em conflito, e a pendência continue visível até ser resolvida. A Atribuição permanece intacta
  (`D-003`).
- Q-B: A sala virtual da banca pode aparecer na Mesa? → A: **Sim, só ao avaliador autenticado e
  atribuído àquela entrevista**, revisando a redação da FR-7229 da `167` (`D-006`).
- Q-C: O rodízio passa a seguir a agenda? → A: **Sim**: percorre as inscrições na ordem da agenda e
  recusa os pares com sobreposição, preservando os demais critérios da distribuição — menor carga
  projetada, desempate estável, impedimento, exposição, proposta conferida sob trava —, revisando a
  FR-107 da `012` (`D-004`).

---

## User Scenarios & Testing *(mandatory)*

Os atores são a **comissão** da Etapa — quem pode gerir a comissão, a presidência inclusive, que
distribui e acompanha — e o **avaliador**, membro da comissão alocado à Etapa, que entra no GPS pela
identidade institucional e trabalha na Mesa.

### Incremento 1

#### User Story 1 — A comissão distribui uma sessão inteira sem conflito (Priority: P1)

A agenda está montada: três bancas, dois dias. Na Distribuição da Etapa, a comissão escolhe "25/11"
e "Banca 01" no filtro, vê as sete pessoas daquela sessão com o horário de cada uma, seleciona todas,
marca Ana e Bruno, e distribui. Repete para as outras bancas e para o outro dia. Se uma das escolhas
põe alguém em dois lugares ao mesmo tempo, a linha é recusada e nomeada, e o resto é distribuído.

**Why this priority**: sem distribuição coerente, qualquer programação que o GPS mostre seria fiel
ao sistema e impossível de cumprir. É a correção que o estudo encontrou.

**Independent Test**: com 43 pessoas em 3 bancas e 2 dias, e 6 avaliadores alocados, a comissão
distribui toda a Etapa em seis submissões filtradas, e nenhum avaliador fica com dois candidatos em
horários que se sobrepõem.

**Acceptance Scenarios**:

1. **Given** a agenda publicada, **When** a comissão abre a Distribuição, **Then** a lista de
   inscrições mostra o horário e a banca de cada pessoa, e o filtro oferece os dias e as bancas da
   agenda.
2. **Given** o filtro "25/11 · Banca 01", **When** a comissão seleciona todas as inscrições da página
   e dois avaliadores e distribui, **Then** cada inscrição selecionada recebe os dois, como o lote já
   faz, e o resultado diz quantas atribuições foram criadas.
3. **Given** Ana com uma entrevista às 08:00–08:15 de 25/11 na Banca 01, **When** a comissão atribui
   a Ana a pessoa das 08:00–08:15 da Banca 02, **Then** essa linha é recusada com "Ana Lima já tem
   entrevista das 08:00 às 08:15 de 25/11 (Banca 01)", e as demais linhas do lote são distribuídas.
4. **Given** Ana com uma entrevista das 08:00 às 08:15, **When** a comissão lhe atribui a pessoa das
   08:15 às 08:30, **Then** a atribuição é aceita: horários que só se tocam não são conflito.
5. **Given** uma Etapa sem agenda, ou com agenda sem horário para aquelas pessoas, **When** a
   comissão distribui, **Then** nada muda em relação a hoje: não há horário a conferir.
6. **Given** a agenda em montagem, ainda não publicada, **When** a comissão distribui, **Then** os
   horários da montagem valem para o filtro e para o conflito, e a tela diz que a agenda ainda pode
   mudar.
7. **Given** a comissão pede o rodízio numa Etapa com agenda, **When** a proposta é mostrada,
   **Then** ela não contém par que crie conflito, percorre as inscrições na ordem da agenda, e diz,
   para cada inscrição que não cobriu, que as pessoas selecionadas têm entrevista naquele horário.
8. **Given** duas sessões da comissão atribuindo a Ana, ao mesmo tempo, pessoas de horários
   simultâneos, **When** as duas confirmam, **Then** só uma atribuição vale, e a outra é recusada
   como conflito.

---

#### User Story 2 — O avaliador entra no GPS e encontra a própria programação (Priority: P1)

Ana abre Minhas atividades e lê "Entrevista — Edital 28/2026 · 14 pendentes · próxima: 25/11 às
08:00, Banca 01". Abre a Mesa e vê a programação: um bloco por dia, em ordem de horário, com cada
candidato, a banca, o local ou o botão da sala, e a situação da avaliação dela. Pelo celular, a
mesma lista cabe na tela.

**Why this priority**: é o que tira o avaliador da planilha. O e-mail do Incremento 2 só aponta para
cá.

**Independent Test**: com a agenda publicada e a distribuição feita, Ana entra, encontra a próxima
entrevista em Minhas atividades e, na Mesa, a lista dos dois dias, sem ver ninguém que não lhe foi
atribuído.

**Acceptance Scenarios**:

1. **Given** a agenda publicada e 14 inscrições atribuídas a Ana, **When** ela abre a Mesa, **Then**
   a visão "Programação" é a primeira, agrupada por dia, em ordem de horário, com hora de início e
   fim, candidato, banca, local ou sala, e a situação da avaliação.
2. **Given** a mesma Mesa, **When** Ana escolhe "Por inscrição", **Then** vê a lista de hoje, por
   protocolo, com os filtros de andamento de hoje.
3. **Given** uma inscrição atribuída a Ana sem horário publicado, **When** ela abre a programação,
   **Then** a inscrição aparece num bloco "Sem horário publicado", depois dos dias.
4. **Given** a agenda ainda não publicada, **When** Ana abre a Mesa, **Then** a programação diz que a
   agenda desta Etapa ainda não foi publicada, e a lista por inscrição continua como hoje.
5. **Given** uma pessoa remarcada depois da publicação, **When** Ana abre a programação, **Then** a
   pessoa aparece no horário novo, com "remarcada em" e a data, e não aparece no anterior.
6. **Given** uma Etapa remota, **When** Ana vê a programação, **Then** cada entrevista leva o acesso à
   sala da banca daquela entrevista, e só dela (`D-006`).
7. **Given** Ana alocada à Etapa e com entrevistas futuras, **When** ela abre Minhas atividades,
   **Then** a linha da Etapa diz a próxima entrevista — dia, hora e banca — e leva à programação.
8. **Given** Bruno, que avalia outras pessoas na mesma Etapa, **When** ele abre a Mesa, **Then** não
   vê nenhuma entrevista de Ana.

---

#### User Story 3 — A comissão vê o que a agenda mudou depois da distribuição (Priority: P2)

Uma candidata é remarcada da Banca 01 para um horário da Banca 02. A tela da remarcação, antes de
confirmar, diz quem a avalia e se essas pessoas estão livres no horário novo. Depois, a agenda
publicada mostra, numa linha, quantas pessoas estão sem avaliador suficiente e quantos conflitos
existem, com o caminho para resolver na Distribuição.

**Why this priority**: a agenda continua mudando depois da distribuição — recurso, falha de conexão,
quem deixa de participar —, e a coerência tem de sobreviver a isso sem que a comissão precise
procurar o problema.

**Independent Test**: remarcar uma pessoa para um horário em que um dos avaliadores dela já tem
entrevista; ver o aviso antes da confirmação, o conflito na agenda publicada e na Distribuição, e
desfazê-lo trocando a atribuição.

**Acceptance Scenarios**:

1. **Given** a pessoa avaliada por Ana e Bruno, **When** a comissão escolhe um horário novo na
   remarcação, **Then** a tela diz "Avaliam esta pessoa: Ana Lima e Bruno Reis", e marca os horários
   livres em que um deles já tem entrevista.
2. **Given** um horário em que Ana já tem entrevista, **When** a comissão confirma a remarcação para
   ele, **Then** a remarcação acontece, e a confirmação já dizia, antes, que criaria um conflito para
   Ana (`D-003`).
3. **Given** um conflito existente, **When** a comissão abre a agenda publicada, **Then** uma linha
   diz "1 avaliador em dois lugares: Ana Lima, às 09:30 de 25/11 (Banca 01 e Banca 02)", com o link
   para a Distribuição já filtrada naquele horário.
4. **Given** pessoas com menos avaliadores do que a Etapa prevê, **When** a comissão abre a agenda
   publicada, **Then** a mesma linha diz quantas são, com o link para a Distribuição filtrada por
   cobertura.
5. **Given** a agenda publicada, **When** a comissão a abre, **Then** cada linha mostra quem avalia a
   pessoa; e a página pública, o documento da publicação e a área do candidato não mostram.
6. **Given** a pessoa que deixou de participar e teve o agendamento cancelado, **When** a comissão
   abre a Distribuição, **Then** as atribuições dela continuam como hoje, e não entram em conflito
   nenhum, porque ela não tem horário vigente.

### Incremento 2

#### User Story 4 — A comissão avisa os avaliadores quando a programação está pronta (Priority: P1)

Com a agenda publicada, a distribuição feita e nenhum conflito, a agenda publicada diz "Programação
dos avaliadores pronta: 6 avaliadores, 43 de 43 pessoas com avaliadores" e oferece "Avisar os
avaliadores (6)". A comissão vê, antes de confirmar, quem recebe, quem está sem e-mail e o texto
exato. Confirma. Cada avaliador recebe um e-mail curto, sem lista, com o link para a própria
programação.

**Why this priority**: é a necessidade que originou o pedido. Um avaliador que não sabe que tem
entrevista não abre o GPS.

**Independent Test**: confirmar o aviso de seis avaliadores, rodar o despacho, e ver seis mensagens,
uma por pessoa, sem nome de candidato, cada uma com o link para a Mesa daquela Etapa.

**Acceptance Scenarios**:

1. **Given** a programação pronta, **When** a comissão escolhe "Avisar os avaliadores", **Then** a
   tela mostra quantos receberão, quem está sem e-mail, quem está fora por conflito, e o assunto e o
   texto da mensagem, sem gravar nada.
2. **Given** a confirmação, **When** o despacho roda, **Then** cada avaliador com e-mail recebe
   exatamente uma mensagem com o Edital, a Etapa, o número de entrevistas, o primeiro e o último dia,
   as bancas, e o link para a programação dele na Mesa.
3. **Given** a mensagem, **When** ela é lida, **Then** não contém nome, protocolo, CPF, e-mail ou
   telefone de candidato, nem a sala.
4. **Given** um avaliador sem e-mail conhecido, **When** a comissão confirma, **Then** ele não recebe,
   e a seção o nomeia como "sem e-mail", com o que fazer.
5. **Given** a confirmação repetida, **When** a comissão confirma de novo sem mudança na programação,
   **Then** nenhum aviso novo nasce.
6. **Given** o servidor de correio recusando um endereço, **When** a comissão abre a agenda
   publicada, **Then** a pessoa aparece como "não entregue", com o reenvio.
7. **Given** os avisos da `066` desabilitados, **When** a comissão abre a agenda publicada, **Then** a
   seção diz que os avisos estão desligados, e não oferece o envio.
8. **Given** o link da mensagem aberto por outra pessoa, **When** ela entra, **Then** recebe a
   recusa da Mesa, como hoje, e não a programação de outrem.

---

#### User Story 5 — Quem teve a programação mudada é avisado, e só ele (Priority: P2)

Depois do aviso, a comissão remarca uma pessoa e troca um avaliador. A seção dos avaliadores passa a
dizer "A programação de 2 avaliadores mudou depois do aviso" e oferece "Avisar as mudanças (2)". Os
dois recebem "Sua programação mudou", com o mesmo link. Os outros quatro, nada.

**Why this priority**: sem isso, o avaliador vê a programação certa só se entrar por acaso; com
envio automático a cada remarcação, recebe cinco mensagens num dia de ajustes.

**Independent Test**: depois do aviso de seis, remarcar uma pessoa avaliada por Ana e Bruno; ver
"2 avaliadores"; avisar; ver duas mensagens, e nenhuma aos outros quatro.

**Acceptance Scenarios**:

1. **Given** o aviso feito, **When** uma remarcação muda o horário de uma pessoa avaliada por Ana e
   Bruno, **Then** os dois aparecem como "mudou depois do aviso".
2. **Given** uma atribuição removida de Carla e dada a Davi, **When** a comissão abre a seção,
   **Then** Carla e Davi aparecem como "mudou depois do aviso".
3. **Given** três remarcações seguidas que afetam Ana, **When** a comissão avisa as mudanças uma
   vez, **Then** Ana recebe uma mensagem.
4. **Given** uma remarcação que volta a pessoa ao horário que Ana já tinha recebido, **When** a
   comissão abre a seção, **Then** Ana não aparece como mudada: o que conta é o estado, e não o
   histórico.
5. **Given** uma mudança que cria conflito para Ana, **When** a comissão avisa as mudanças, **Then**
   Ana fica fora do envio, nomeada com o conflito, até ele ser resolvido.

---

### Edge Cases

- **Distribuição antes da agenda.** A Distribuição exige o prazo de inscrição encerrado, e a agenda
  pode ser configurada antes ou depois. Sem horário, não há conflito a conferir: a atribuição é
  aceita, e o conflito que a montagem criar depois aparece na Distribuição e na agenda (FR-8206).
- **Preenchimento automático depois da distribuição.** O preenchimento da `167` ordena por nome e não
  conhece os avaliadores; ele pode criar conflitos. A conferência da agenda os mostra como aviso, e
  não impede a publicação, que é ato para os candidatos (FR-8208).
- **Avaliador em duas Etapas do mesmo Edital com agenda.** O conflito conta entre Etapas do mesmo
  Edital (FR-8202). Entre Editais diferentes, fica fora.
- **Entrevistas já passadas.** Um conflito em que as duas entrevistas já terminaram é mostrado como
  passado, e não impede o aviso.
- **Atribuição com avaliação concluída.** A troca de avaliador continua sujeita à FR-092 da `012`: a
  avaliação concluída não sai pela via comum, e o conflito é mostrado sem oferecer a troca impossível.
- **Inscrição com mais avaliadores do que a Etapa prevê.** Não é conflito; a cobertura de hoje já a
  mostra.
- **Banca vazia num dia.** Não aparece no filtro daquele dia.
- **Avaliador alocado sem nenhuma entrevista.** Não tem programação, não aparece entre os que
  recebem aviso, e Minhas atividades não muda para ele.
- **Membro da comissão cujo identificador não corresponde a conta nenhuma** (identificador de
  demonstração escrito à mão, digitado errado, pessoa que nunca entrou). Não tem e-mail conhecido; aparece como
  "sem e-mail", nunca é pulado em silêncio (FR-8226).
- **Pessoa institucional suspensa.** Não recebe aviso, e aparece como tal.
- **Agenda sem duração conhecida para um horário.** Não existe: todo horário publicado tem início e
  fim (a `167`).

---

## Requirements *(mandatory)*

### Functional Requirements

#### A programação e o conflito (base dos dois incrementos)

- **FR-8200**: A **programação** de um avaliador numa Etapa MUST ser derivada, a cada leitura, das
  Atribuições ativas dele naquela Etapa que a Mesa já alcança (a FR-020 da `012`), cruzadas com o
  horário de cada inscrição. MUST NOT existir cadastro, lista ou composição de banca que a guarde.
- **FR-8201**: O **horário** de uma inscrição numa Etapa MUST ser o horário publicado vigente, quando
  a agenda está publicada, e o horário da montagem, antes disso. A programação na Mesa e o aviso
  MUST usar só o publicado; a Distribuição e o conflito MUST usar os dois, dizendo qual.
- **FR-8202**: Há **conflito** quando o mesmo avaliador tem Atribuições ativas em duas inscrições cujos
  horários, no mesmo Edital, se sobrepõem: o início de cada um é anterior ao fim do outro. Horários
  que só se tocam MUST NOT ser conflito. O intervalo entre atendimentos MUST NOT entrar na conta.
- **FR-8203**: O conflito MUST ser lido de dados que existem — Atribuição, horário, início e fim —, e
  MUST NOT ser gravado como fato próprio.

#### A distribuição (Incremento 1)

- **FR-8204**: A Distribuição MUST mostrar, numa Etapa com agenda, o horário e a banca de cada
  inscrição, e MUST oferecer filtro por dia e por banca, combinável com os filtros de hoje. Com o
  filtro, o lote uniforme de hoje MUST atribuir a sessão inteira num gesto.
- **FR-8205**: A atribuição que criaria conflito MUST ser recusada como **regra sobre a linha** da
  FR-085 da `012`: a linha é nomeada, com o avaliador, o horário e a banca do outro compromisso, e o
  restante do lote é distribuído. O conflito entre duas linhas do mesmo lote MUST ser recusado do
  mesmo jeito. A conferência MUST valer sob operações simultâneas.
- **FR-8206**: Inscrição sem horário MUST NOT ser recusada por conflito. A distribuição feita antes
  da agenda MUST continuar válida, e o conflito que a agenda criar depois MUST aparecer onde a
  FR-8208 diz.
- **FR-8207**: O rodízio, numa Etapa com horários, MUST tratar o par que criaria conflito como
  inelegível — como trata o impedimento — e MUST percorrer as inscrições na ordem da agenda (dia,
  horário, banca); sem horários, na ordem de hoje. A inscrição que ficar sem cobertura por conflito
  MUST ser dita com esse motivo. Os demais critérios do rodízio MUST NOT mudar (`D-004`).
- **FR-8208**: A Distribuição e a agenda publicada MUST mostrar, à comissão, os conflitos existentes
  — avaliador, dia, horários e bancas — e quantas pessoas com horário têm menos avaliadores do que a
  Etapa prevê, cada contagem com o link para a Distribuição já filtrada onde se resolve. A
  conferência da agenda MUST mostrar os conflitos como aviso, e MUST NOT impedir a publicação por
  causa deles.

#### A agenda depois da distribuição (Incremento 1)

- **FR-8209**: A remarcação e a inclusão MUST mostrar, antes da confirmação, quem avalia a pessoa, e
  MUST marcar, entre os horários livres, aqueles em que algum desses avaliadores já tem entrevista.
  Confirmar um horário que cria conflito MUST ser possível, e a confirmação MUST identificar, antes,
  cada avaliador que ficará em conflito, com o horário e as duas bancas. O conflito MUST continuar
  visível, na agenda publicada e na Distribuição, até ser resolvido (`D-003`). A agenda MUST NOT
  mudar Atribuição nenhuma.
- **FR-8210**: O cancelamento de um agendamento MUST tirar a inscrição da programação e dos conflitos,
  sem tocar nas Atribuições.

#### A programação no GPS (Incremento 1)

- **FR-8211**: A Mesa, numa Etapa com agenda publicada, MUST ter a visão **Programação** como a
  primeira: as entrevistas do avaliador agrupadas por dia, em ordem de início, cada uma com início e
  fim, o candidato pelo nome e pelo protocolo — o que a ficha da Mesa já lhe mostra —, a banca, o local ou o acesso à sala da banca daquela
  entrevista, "remarcada em" com a data quando houve remarcação, e a situação da avaliação dele. As
  Atribuições sem horário publicado MUST vir num bloco à parte, depois dos dias.
- **FR-8212**: A visão "Por inscrição" de hoje MUST continuar disponível na mesma Mesa, com os
  filtros de hoje. Antes da publicação da agenda, a Programação MUST dizer que a agenda ainda não foi
  publicada.
- **FR-8213**: A Programação MUST mostrar todas e somente as entrevistas das Atribuições do próprio
  avaliador (a FR-020 da `012`); nenhum horário, banca ou sala de entrevista de outrem.
- **FR-8214**: A linha da Etapa em Minhas atividades MUST dizer a próxima entrevista do avaliador —
  dia, hora e banca — quando houver entrevista futura, e MUST levar à Programação.
- **FR-8215**: A agenda publicada da gestão MUST mostrar, em cada linha, quem avalia a pessoa. A
  página pública, o documento do ato, a área do candidato e o aviso ao candidato MUST NOT mostrar
  quem avalia, nem a contagem de avaliadores (a FR-7226 da `167` continua valendo como está).

#### O aviso ao avaliador (Incremento 2)

- **FR-8220**: A comissão MUST poder avisar por e-mail os avaliadores da Etapa de que a programação
  deles está disponível, por um gesto na agenda publicada. O aviso MUST NOT sair sozinho da
  publicação, da distribuição ou da remarcação: o gesto é a decisão humana que a FR-084 da `010`
  exige.
- **FR-8221**: Recebe o aviso o avaliador alocado à Etapa, com ao menos uma entrevista com horário
  publicado, sem conflito em entrevista futura, e com e-mail conhecido (FR-8226). Quem não recebe
  MUST ser nomeado, com o motivo e o que fazer.
- **FR-8222**: Antes da confirmação, a tela MUST mostrar quantos avaliadores receberão, quem fica fora
  e por quê, e o assunto e o texto exatos de uma das mensagens, sem gravar nem enviar nada.
- **FR-8223**: A mensagem MUST ter o Edital, a Etapa, o número de entrevistas, o primeiro e o último
  dia, os nomes das bancas, o link para a Programação dele na Mesa, e a frase de que a programação
  que vale é a do GPS. A mensagem MUST NOT ter nome, protocolo, CPF, e-mail ou telefone de candidato,
  Modalidade, nem o endereço da sala.
- **FR-8224**: Para cada avaliador, o GPS MUST guardar o estado da programação que lhe foi avisado. A
  programação dele **mudou depois do aviso** quando o estado de hoje difere do avisado — e só então;
  voltar ao estado avisado MUST desfazer a marca.
- **FR-8225**: Depois do primeiro aviso, o gesto MUST alcançar só quem ainda não foi avisado e quem
  teve a programação mudada, com o texto "Sua programação mudou". Repetir o gesto sem mudança MUST
  NOT criar aviso. Uma pessoa MUST receber no máximo um aviso por gesto.
- **FR-8226**: O endereço MUST ser o e-mail da pessoa — a conta de acesso ao GPS — cujo identificador
  é o do membro da comissão, congelado no aviso no instante do gesto. Sem essa pessoa, sem e-mail nela
  ou com ela suspensa, o avaliador MUST aparecer como "sem e-mail" ou "suspenso". MUST NOT existir
  campo onde alguém digite o e-mail de um avaliador — na banca, na alocação, no aviso ou noutro
  lugar.
- **FR-8227**: O envio MUST ser o do despacho dos avisos da `066` — a fila, o limite por minuto, a
  tentativa gravada antes do envio, a retentativa e o reenvio —, e MUST obedecer à habilitação dos
  avisos da `066`, sem chave própria. Desligada a habilitação, a seção MUST dizer isso no lugar do
  gesto. A falha de envio MUST ser mostrada por pessoa, com o reenvio.
- **FR-8228**: A agenda publicada MUST mostrar, por avaliador: avisado em (data e hora), na fila, não
  entregue, mudou depois do aviso, sem e-mail, suspenso, ou com conflito; e, para a Etapa, se a
  programação está pronta para ser avisada.
- **FR-8229**: A FR-084 da `010` MUST ser revista para admitir a oitava situação — o aviso de
  programação ao avaliador —, com a redação anterior preservada, como as revisões anteriores fizeram;
  a revisão vigora com a implementação do Incremento 2. A redação proposta está em *Requisitos de
  outras features afetados*.

#### Autorização, dados e trilha (os dois incrementos)

- **FR-8230**: Filtrar, distribuir e ver os conflitos MUST exigir a base que a Distribuição já exige.
  Avisar os avaliadores MUST exigir a permissão de gerir a comissão e o escopo do Edital, conferidos
  no servidor, como a publicação da agenda.
- **FR-8231**: A Programação MUST ser resposta privada, sem cache, como a Mesa. O acesso à sala MUST
  aparecer só ao avaliador autenticado e atribuído àquela entrevista (`D-006`).
- **FR-8232**: A remarcação ou inclusão que cria conflito MUST registrar na trilha, no próprio
  evento do ato, os avaliadores que ficaram em conflito; o aviso e o reenvio MUST gerar registro na
  trilha, com ator, instante e alcance. A recusa por conflito no lote MUST constar do resultado
  declarado, como as demais recusas sobre a linha. Nenhum registro MUST conter e-mail nem endereço
  de sala.

### Requisitos de experiência

- **UX-970**: O filtro por dia e banca MUST estar no mesmo formulário dos filtros de hoje da
  Distribuição, e a sessão filtrada MUST caber numa página, para "selecionar todas desta página"
  alcançar a sessão inteira.
- **UX-971**: A recusa por conflito MUST dizer o que fazer: escolher outro avaliador para aquela
  linha, ou distribuí-la noutro gesto.
- **UX-972**: A Programação MUST funcionar a 375 px sem rolagem horizontal da página: no celular,
  cada entrevista é um item de lista com a hora em destaque, e não linha de tabela.
- **UX-973**: O acesso à sala MUST ser um botão por entrevista, e não o endereço por extenso.
- **UX-974**: A agenda publicada MUST dizer o estado da coerência e do aviso numa linha só quando
  tudo está em ordem, e abrir o detalhe só quando há o que resolver. Nenhuma tela nova; nenhum
  centro de controle.
- **UX-975**: O gesto de aviso MUST aparecer só quando há quem avisar, e o rótulo MUST dizer quantos
  ("Avisar os avaliadores (6)", "Avisar as mudanças (2)").
- **UX-976**: As telas MUST usar as folhas e componentes da gestão, sem estilo ou script escrito no
  documento.

### Key Entities

- Já existem e são o que esta feature cruza: a **Alocação** do membro à Etapa (pode atuar), a
  **Atribuição** (avalia esta inscrição), o **horário publicado** e o **agendamento** da `167` (quando
  e em que banca), a **banca** (onde: local ou sala), a **pessoa institucional** (quem é, e o e-mail).
- **Programação do avaliador** *(derivada, não gravada)*: as entrevistas de um avaliador numa Etapa.
- **Conflito** *(derivado, não gravado)*: duas entrevistas do mesmo avaliador que se sobrepõem.
- **Aviso de programação** *(Incremento 2)*: o aviso a um avaliador, com o estado da programação que
  ele avisou; é a única coisa nova que se grava, e se grava no mecanismo de avisos que já existe.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2840**: Nas fixtures de distribuição com agenda — lote manual, lote entre linhas simultâneas,
  rodízio, duas operações concorrentes —, nenhuma atribuição cria conflito, em 100% dos casos; e
  nenhuma atribuição a inscrição sem horário é recusada por conflito.
- **SC-2841**: No caso de 43 pessoas, 3 bancas, 2 dias, 6 avaliadores e dupla avaliação, a comissão
  distribui a Etapa inteira, sem conflito, em no máximo seis submissões filtradas.
- **SC-2842**: No mesmo caso, o rodízio propõe uma distribuição sem conflito em 100% das ordens de
  protocolo testadas.
- **SC-2843**: Em 100% dos casos de teste, a Programação de um avaliador contém todas e somente as
  entrevistas das Atribuições dele, na ordem de início.
- **SC-2844**: *(humano)* Um avaliador que não participou desta feature encontra, pelo celular, a
  próxima entrevista e o acesso à sala em menos de 30 segundos a partir de Minhas atividades.
- **SC-2845**: Em 100% das remarcações que criam conflito, a confirmação o disse antes, e o conflito
  aparece na agenda publicada e na Distribuição logo depois.
- **SC-2846**: Nenhuma página pública, documento de ato, área do candidato ou aviso ao candidato
  contém o nome de um avaliador.
- **SC-2847**: *(Incremento 2)* Com a programação pronta, cada avaliador com e-mail recebe exatamente
  um aviso por gesto; repetir o gesto sem mudança cria zero avisos; depois de uma remarcação, só os
  avaliadores daquela pessoa recebem "Sua programação mudou".
- **SC-2848**: *(Incremento 2)* Nenhuma mensagem ao avaliador contém nome, protocolo, CPF, e-mail ou
  telefone de candidato, Modalidade ou endereço de sala.
- **SC-2849**: *(Incremento 2)* A varredura das situações de envio conta a oitava, e a revisão da
  FR-084 está datada na `010`.
- **SC-2850**: Todas as telas tocadas abrem a 375 px sem rolagem horizontal da página e passam na
  política de conteúdo sem violação.

---

## Assumptions

- **A comissão distribui por sessão** quando as bancas são simultâneas: uma dupla (ou trio) por banca
  e por dia, ou por janela. O estudo o supõe, e o usuário não o contestou; se a prática for outra, o
  conflito continua valendo e o filtro perde importância, sem mudar o resto.
- **A duração de cada atendimento é a do horário**, de início a fim, como a `167` grava. O intervalo
  entre atendimentos é folga da agenda, e não tempo do avaliador.
- **O e-mail do avaliador é o do provedor institucional**, que a `106` copia para a pessoa a cada
  entrada. Em produção todo ator é pessoa institucional. **Na demonstração, o percurso do
  Incremento 2 precisa ser feito pela tela** (Princípio VI): o cenário de treinamento C20 passa a
  criar os membros da comissão da Entrevista como contas de acesso com e-mail de exemplo — o que o
  gerador já faz com a conta da Formalização do C16 e do C17 —, sem conceder papel. Assim a comissão
  vê os avaliadores "prontos", avisa, e as mensagens saem no terminal do despacho.
- **A habilitação dos avisos da `066` está ligada por padrão** em todo ambiente desde 15/11
  (`doc/decisao-avisos-ligados-por-padrao-2026-11-15.md`).
- **Conflito entre Etapas** conta dentro do mesmo Edital: é onde o membro da comissão, a Atribuição e
  a agenda se encontram sem consulta entre Processos.
- **A situação da entrevista** é a situação da avaliação do próprio avaliador, que a Mesa já tem. A
  ausência continua sendo Ocorrência da Etapa, e não estado da agenda (a FR-7250 da `167`).

## Out of Scope

- Cadastro de e-mail nas bancas, e qualquer destinatário digitado à mão.
- Composição fixa de banca, ou banca como grupo de pessoas.
- Lista de candidatos, sala ou anexo no e-mail; agenda completa da Etapa a cada avaliador.
- Envio automático a cada remarcação, distribuição ou publicação.
- Redistribuição automática quando a agenda muda.
- Conflito entre Editais diferentes; disponibilidade declarada pelo avaliador.
- A combinação de notas de mais de uma avaliação numa Etapa pontuada. A `179` distribui duplas e
  trios, mas a Etapa pontuada com mais de uma avaliação continua sem fechar resultado, como já era;
  é achado registrado em `doc/achado-combinacao-de-notas-2026-11-16.md`, e não escopo (decisão do
  usuário em 16/11).
- Arquivo de calendário e integração com Google ou Outlook.
- A busca da pessoa na inclusão do membro da comissão (pendência registrada em
  `doc/ativacao-do-sso-institucional.md`): esta feature a torna visível, como "sem e-mail", e não a
  resolve.

---

## Requisitos de outras features afetados

| Requisito | Feature | O que muda | Incremento |
|---|---|---|---|
| FR-084 | `010` | **Revisão**: oitava situação, o aviso de programação ao avaliador. | 2 |
| FR-085 | `012` | **Acréscimo**: o conflito de horário é regra sobre a linha, ao lado do impedimento e do teto. | 1 |
| FR-107 | `012` | **Revisão**: o rodízio trata o conflito como inelegibilidade e percorre a agenda (`D-004`). | 1 |
| FR-020 | `012` | **Nenhuma**: a Programação é outra visão das mesmas Atribuições. | 1 |
| FR-7229 | `167` | **Revisão de redação**: a sala chega também ao avaliador atribuído, na Mesa (`D-006`). | 1 |
| FR-7240 | `167` | **Acréscimo**: a remarcação e a inclusão mostram quem avalia e o conflito (FR-8209). | 1 |
| FR-7226 | `167` | **Nenhuma**: o público continua sem avaliador (FR-8215 o explicita). | 1 |

**Redação proposta para a FR-084 da `010`** (a aplicar no PR do Incremento 2, com a anterior
preservada, como a regra manda): onde se lê "o sistema envia mensagem em exatamente **sete**
situações", passa a ler **oito**, e a enumeração acrescenta, depois do aviso de agenda: *"e o
**aviso de programação** (`179`), que diz ao avaliador alocado a uma Etapa que a sua programação de
entrevistas está disponível no GPS, ou que mudou, e que a comissão decide enviar depois de ver quem
recebe; ele não leva candidato, horário individual nem sala, e o que vale é a programação na Mesa"*.
E a frase final: "acrescentar uma **nona** situação exige revisar esta regra de novo". É a primeira
situação dirigida a quem trabalha no certame, e não ao candidato; a regra já enumera "o sistema", e
não "o candidato", e por isso cabe nela sem regra nova.

---

## Decisões

### D-001 — A programação é derivada, e não cadastro

O GPS já sabe quem avalia cada candidato (Atribuição) e quando cada candidato é atendido (horário).
Uma tabela de "programação" ou uma composição de banca seriam a segunda fonte que o Princípio II
proíbe, e divergiriam na primeira remarcação. O que se grava é só o que é fato novo: o aviso, no
Incremento 2.

### D-002 — O conflito é recusado onde nasce na Distribuição

A atribuição é o ato que põe a pessoa num horário; recusá-la ali é barato, explicável e já tem forma
— a regra sobre a linha da FR-085 da `012`. Avisar sem recusar deixaria a integridade depender de a
comissão perceber, que é o que o usuário recusou. Recusar a inscrição sem horário seria bloquear a
distribuição que vem antes da agenda; por isso a regra só vale com horário (FR-8206).

### D-003 — A agenda pode criar conflito, mas nunca em silêncio

*Decidida pelo usuário em 16/11 (Q-A).* A remarcação é ato da agenda, sobre o candidato, e às
vezes urgente — a conexão caiu, o Edital manda reagendar. Recusá-la por causa de um avaliador
ocupado inverteria a ordem: a comissão teria de redistribuir antes de poder remarcar. A alternativa
adotada diz o conflito antes da confirmação (FR-8209), o mostra depois (FR-8208) e o faz impedir o
aviso aos avaliadores envolvidos (FR-8221). O mesmo vale para a montagem antes da publicação.

### D-004 — O rodízio percorre a agenda e evita o conflito

*Decidida pelo usuário em 16/11 (Q-C).* A FR-107 da `012` diz "o que existe é isto, e nada além";
mudar o rodízio é revisá-la. A revisão é pequena — o conflito vira inelegibilidade, como o
impedimento, e a ordem das inscrições passa a ser a da agenda quando ela existe — e o estudo mediu o
efeito: na ordem do protocolo, a mesma dupla ficou com dois candidatos ao mesmo tempo em 8 a 14 de
15 horários; na ordem da agenda, em nenhum dos sorteios testados. A regra por menor carga, o
desempate estável e a proposta conferida sob trava não mudam: continua sem sorteio e reprodutível.

### D-005 — A programação vive na Mesa, e não em tela nova

A Mesa já é "todas e somente as inscrições desta pessoa nesta Etapa", com a autorização certa e o
orçamento de consulta testado. A Programação é outra ordem e outro agrupamento das mesmas linhas.
Uma tela de "minha agenda" seria a segunda porta para os mesmos dados.

### D-006 — A sala aparece ao avaliador daquela entrevista

*Decidida pelo usuário em 16/11 (Q-B).* A FR-7229 da `167` diz que o endereço da sala "MUST
chegar só à própria pessoa". As telas da gestão já o mostram a quem gere a comissão, que o cadastrou;
a leitura em vigor é "nada de público, nada a outro candidato". O avaliador atribuído é quem entra
naquela sala. A revisão de redação acrescenta "e ao avaliador autenticado e atribuído àquela
entrevista, na Mesa". Nenhum outro avaliador, nem a comissão por esta via, recebe a sala de uma
entrevista que não avalia.

### D-007 — Quem avalia é informação interna

A composição de quem avalia cada pessoa não é ato publicado, e na heteroidentificação nomear a banca
de cada candidato exporia quem julga quem. Por isso ela aparece só nas telas da gestão que já mostram
Atribuições (a Distribuição) e na agenda publicada da gestão, e nunca no conteúdo público, no
documento do ato ou na área do candidato (FR-8215).

### D-008 — O e-mail avisa; a Mesa informa

O e-mail não leva lista. Leva o suficiente para o avaliador saber que tem trabalho — quantas
entrevistas, em que dias, em que bancas — e o caminho até a Mesa, onde está a programação vigente.
Assim ele nunca fica com uma cópia velha na caixa, nenhum nome de candidato sai do GPS, e a mudança
pode ser avisada sem que a mensagem precise dizer o quê.

### D-009 — Uma mensagem por gesto, e não por mudança

Avisar a cada remarcação produziria várias mensagens por dia de ajustes. A comissão avisa quando
termina, e o GPS sabe a quem: quem não foi avisado e quem teve a programação mudada (FR-8224). O
estado, e não o histórico, decide: uma mudança desfeita não gera mensagem.

### D-010 — O aviso usa o despacho da `066`, sem remetente novo

O despacho já tem a fila, o limite por minuto — que é global e seria contornado por um segundo
remetente —, a tentativa gravada antes do envio, a retentativa, o reenvio e a moldura dos e-mails.
Hoje o destinatário de um aviso é uma inscrição; o plano decide como ele passa a admitir o
avaliador, sem tocar o que vale para o candidato.
