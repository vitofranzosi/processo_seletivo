# Feature Specification: Prevenção de erro nos atos irreversíveis da convocação

**Feature Branch**: `claude/stoic-newton-ea19a6`, sobre a `main` em `95eee5ed`

**Created**: 2026-11-11

**Status**: Draft — as três questões respondidas pelo usuário em 11/11/2026 (D-002, D-010, D-011)

**Uma regra nova, e só uma.** Com o prazo em curso e documento ainda não conforme, o indeferimento
passa a exigir a ciência de quem registra, e o comando a confere (FR-5805). O resto é **quando e com
que conferência** os atos que já existem acontecem: quem é chamado, a espécie, a fila, o fundamento,
a mensagem, a faixa do corte e as guardas de cada desfecho continuam as de hoje, pelos mesmos
comandos. Não há tabela, permissão nem estado de convocação novos.

**Input**: *"Escrever a spec de prevenção de erro nos atos irreversíveis da convocação. Três achados
do estudo da jornada final (PR #472): achado 04 — 'Indeferir pelas pendências de documento' é oferecido e
aceito numa convocação sem pendência, sem documento enviado e com 30 dias de prazo; proponha o gesto
só com pendência e, com prazo em curso, a tela dizendo que o candidato ainda pode corrigir e pedindo
confirmação explícita; bloquear ou só avisar é decisão do usuário. Achado 08 — a ordem e o lote de
titulares têm 'Confira antes'; o corte e a chamada individual do suplente são praticados num clique,
e a chamada já envia o e-mail; peça a mesma conferência da 140 para a chamada individual, e
confirmação no corte. Achado 12 — o desfecho oferece as 7 espécies sempre, inclusive 'Cancelamento de
matrícula por inércia' numa seleção de professor, e o atestado oferece 'Não acessou o ambiente';
peça o filtro pelas espécies que cabem no estado da chamada e deixe o vocabulário por natureza da
seleção como pergunta. A spec parte do estado do #467 e do #468, não os refaz."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de cinco mil e oitocentos a cinco mil oitocentos e quarenta e nove;
> - os critérios de mil e novecentos a mil novecentos e dezenove;
> - os requisitos de experiência de quinhentos e trinta a quinhentos e quarenta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 11/11/2026 na `main`, em todas as branches remotas e nas `specs/` de todas as
> worktrees desta máquina: requisito cinco mil setecentos e trinta e seis e critério mil oitocentos e
> sessenta e cinco, da `149`; experiência quatrocentos e sessenta e cinco, da `148`. A `150` (#471,
> aberto) usa requisitos de cinco mil e seiscentos, critérios de mil e oitocentos e experiência de
> quinhentos a quinhentos e três. A `151` fica para a spec da formalização na jornada guiada, escrita
> em paralelo noutra sessão; a reserva está nas notas compartilhadas das duas.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-3594 da `115`"); decisão de outra feature, pelo assunto, nunca pelo identificador.
>
> **Origem.** O
> [estudo da jornada final de 11/11/2026](../../doc/estudo-jornada-final-2026-11-11/index.html)
> (PR #472), achados 04, 08 e 12 do inventário e passos A3, E2 e F1 do percurso, sobre os
> cenários de treinamento C09 e C11 da `134`. No estudo os achados levam o prefixo dos requisitos de
> experiência; aqui eles se escrevem "achado 04", para que a varredura de citações não os leia como
> requisitos desta spec.
>
> **O estado de partida.** O #467 (conferência da emissão, da classificação e da convocação) e o
> #468 (corte e conferência do lote) estão na `main`. Os rótulos que esta spec segue são os deles:
> o botão "Conferir antes de convocar as N" e "Conferir antes de emitir", e as páginas "Confira
> antes de convocar" e "Confira antes de emitir". Nada aqui os refaz.

## Por que esta feature existe

O estudo percorreu a jornada final de um certame pela interface real e encontrou três atos
irreversíveis protegidos de forma diferente dos vizinhos, ou oferecidos onde não cabem:

1. **O indeferimento pelas pendências aparece onde não há pendência** (achado 04, prioridade alta). No
   C11, a convocação de Alice tinha dois documentos a apresentar, nenhum enviado e o prazo vencendo
   dali a 30 dias. O atalho "Indeferir pelas pendências de documento" estava no cartão, trazia o
   fundamento pré-redigido — *"Documentação exigida na convocação não atendida — Diploma de
   graduação; Comprovante de residência"* — e o registro foi aceito
   (`img/X02-indeferir-Alice.png`, `img/X04-indeferido-Alice.png`).

   A FR-3594 da `115` fala em *"convocação com pendência"*. A tela lê "pendência" como **tudo o que
   impede o aceite**: o documento ainda não enviado com o prazo correndo, e o enviado que a comissão
   ainda não conferiu. Nos dois casos, nada falta da parte da pessoa — ela ainda pode cumprir, ou já
   cumpriu e espera a comissão. O desfecho encerra a chamada, libera a vaga e não volta. A decisão
   "Nada automático" da `115` continua certa: ninguém indeferiu sozinho. O defeito é a tela convidar
   a um ato que a própria leitura dela contradiz ("Próximo passo: aguardando o candidato enviar 2
   documentos").

2. **O mesmo tipo de ato com proteção diferente** (achado 08). A ordem e o lote de titulares passam por
   "Confira antes". Dois atos igualmente irreversíveis não passam:
   - a **chamada individual** ("Chamar uma pessoa da fila") convoca e envia o e-mail no primeiro
     clique (`img/E03-chamar-da-fila.png`, `img/E04-chamar-conferir.png`). Um suplente chamado com o
     vencimento errado só se corrige por sucessão, e a mensagem que saiu não volta. A `140` deixou a
     chamada individual fora de propósito e registrou o achado para o usuário decidir;
   - o **corte** é emitido no primeiro clique (`img/A07-corte-antes.png`, `img/A09-corte-emitido.png`).
     A proposta calculada aparece na tela, mas o botão está logo abaixo dela, sem o passo que a ordem
     tem.

3. **O desfecho oferece o que a chamada não admite** (achado 12). O seletor "O que aconteceu" lista as
   sete espécies sempre (`img/F02-desfecho-aceite-preenchido.png`). Numa chamada para vaga inicial de
   professor, com tudo conforme e o prazo em curso, aparecem "Regularização", que a espécie da chamada
   nunca admite; "Não atendimento à convocação", que o comando recusa antes do vencimento; e
   "Cancelamento de matrícula por inércia", que exige atestado que não existe. O comando recusa os
   três — as guardas estão no domínio —, mas a tela os oferece. O "Atestar fato externo" oferece
   "Não acessou o ambiente" e "Ausente na primeira semana" a uma seleção que não tem ambiente nem
   semana letiva.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O atalho do indeferimento só onde há pendência (Priority: P1)

Quem conduz a convocação vê o cartão de uma chamada. O atalho "Indeferir pelas pendências de
documento" aparece só quando a comissão registrou pendência num documento pedido, ou quando o prazo
venceu sem que um obrigatório fosse apresentado, tendo a pessoa apresentado ao menos um documento.
Documento a apresentar com o prazo correndo, ou enviado e ainda não conferido, não faz o atalho
aparecer. Com o prazo vencido e nada apresentado, o cartão orienta para o não atendimento à
convocação.

**Why this priority**: é o achado de prioridade alta do estudo, e o único dos três em que a tela
convida a um ato contra a própria leitura dela.

**Independent Test**: no C11, abrir o cartão de Alice (nada enviado, prazo em curso) e não encontrar
o atalho; registrar pendência num documento de Bernardo e encontrar o atalho no cartão dele, com o
fundamento citando só o documento pendente e o motivo.

**Acceptance Scenarios**:

1. **Given** uma chamada com dois documentos a apresentar e o prazo em curso, **When** quem conduz
   abre o cartão, **Then** o atalho não aparece, e o desfecho geral continua disponível.
2. **Given** uma chamada com um documento conferido como pendente e outro conforme, **When** quem
   conduz abre o atalho, **Then** o fundamento pré-redigido cita o pendente e o motivo registrado, e
   não cita o conforme.
3. **Given** uma chamada com um documento pendente e outro enviado ainda sem conferência, **When**
   quem conduz abre o atalho, **Then** o fundamento cita só o pendente, e o formulário diz que o
   outro aguarda conferência e que o indeferimento o deixa sem conferir.
4. **Given** uma chamada com o vencimento decorrido, um documento apresentado e um obrigatório nunca
   apresentado, **When** quem conduz abre o cartão, **Then** o atalho aparece, e o fundamento diz que
   o documento não foi apresentado no prazo.
5. **Given** uma chamada com documentos apenas enviados e ainda não conferidos, **When** quem conduz
   abre o cartão, **Then** o atalho não aparece; o passo do cartão continua sendo conferir.
6. **Given** uma chamada com o vencimento decorrido e nenhum documento apresentado, **When** quem
   conduz abre o cartão, **Then** o atalho não aparece, o cartão diz que nada foi apresentado no prazo
   e aponta o desfecho "Não atendimento à convocação", e o indeferimento continua no desfecho geral.

---

### User Story 2 — Indeferir com o prazo em curso pede ciência (Priority: P1)

Quem registra um indeferimento — pelo atalho ou pelo desfecho geral — numa chamada cujo prazo ainda
corre, e que tem documento pedido ainda não conforme, lê antes do ato que a pessoa ainda pode enviar
ou corrigir até o vencimento, e só registra marcando que sabe disso. Sem a marca, o indeferimento não
é registrado.

**Why this priority**: é a segunda metade do achado 04. Mesmo com pendência registrada, a pessoa pode
corrigir dentro do prazo (a correção de documento pendente é aceita até o vencimento); indeferir
antes é decisão legítima, mas tem de ser decisão, e não descuido.

**Independent Test**: no C11, registrar pendência num documento de Bernardo, abrir o indeferimento e
ler o vencimento e a frase; tentar registrar sem a marca e ver a recusa, sem desfecho; marcar e
registrar.

**Acceptance Scenarios**:

1. **Given** uma chamada com pendência registrada e o prazo vencendo em 11/12/2026 17:44, **When**
   quem conduz abre o indeferimento, **Then** lê que o prazo vence em 11/12/2026 17:44 e que até lá
   a pessoa ainda pode enviar ou corrigir os documentos, e vê a marca de ciência, desmarcada.
2. **Given** o mesmo formulário sem a marca, **When** quem conduz registra, **Then** nada é gravado,
   a tela diz por quê e devolve o formulário com o fundamento digitado.
3. **Given** a marca, **When** quem conduz registra, **Then** o indeferimento é registrado como hoje,
   e o registro permite saber depois que foi feito com o prazo em curso e com a ciência.
4. **Given** uma chamada para vaga inicial com o prazo em curso, **When** quem conduz escolhe
   "Indeferimento" no desfecho geral, **Then** a mesma frase e a mesma marca são exigidas.
5. **Given** o vencimento já decorrido, ou todos os documentos pedidos conformes, **When** quem
   conduz indefere, **Then** nenhuma marca é pedida.

---

### User Story 3 — Conferir antes de chamar uma pessoa da fila (Priority: P1)

Quem conduz escolhe uma pessoa em "Chamar uma pessoa da fila", informa o vencimento e clica. Em vez
do ato, abre-se "Confira antes de convocar", com a pessoa, a espécie da chamada e de onde ela vem, o
texto que ela lerá no portal e no e-mail, o prazo, e — se ela não for a próxima — quem fica para
trás. Só o botão da conferência convoca e envia. O mesmo vale para "Chamar para regularizar".

**Why this priority**: é a chamada que mais acontece depois do lote — cada desistência e cada não
atendimento produzem uma —, e hoje ela sai no primeiro clique com a mensagem.

**Independent Test**: no C09, depois da desistência de Cecília, chamar Davi pela fila; conferir que a
página seguinte é a conferência e que nenhuma convocação nasceu e nenhuma mensagem saiu; confirmar e
conferir que nasceram uma e saiu uma.

**Acceptance Scenarios**:

1. **Given** Davi como próximo da fila, para vaga que vagou, **When** quem conduz clica em "Conferir
   antes de convocar", **Then** vê Davi, "para vaga que vagou" com a origem, o fundamento, o assunto e
   o texto do e-mail, o vencimento e a origem dele, e nenhuma convocação existe nem mensagem saiu.
2. **Given** a conferência, **When** quem conduz confirma, **Then** nasce uma convocação e sai uma
   comunicação, e a tela da convocação diz o que aconteceu, como hoje.
3. **Given** Estela escolhida no lugar de Davi, com a marca de precedência, **When** a conferência
   abre, **Then** ela diz que Estela passa à frente de Davi e que a exceção fica registrada na trilha.
4. **Given** Estela escolhida sem a marca de precedência, **When** quem conduz pede a conferência,
   **Then** a conferência recusa com a razão do comando, sem botão de confirmar.
5. **Given** a conferência aberta, **When** outra pessoa convoca Davi antes da confirmação, **Then**
   a confirmação é recusada com a razão, e nada é praticado.
6. **Given** uma inscrição indeferida que pode ser chamada para regularizar, **When** quem conduz
   clica em "Chamar para regularizar", **Then** a mesma conferência abre, com a espécie "para
   regularizar" e o Resultado indeferido que a chamada regulariza.

---

### User Story 4 — Conferir antes de emitir o corte (Priority: P2)

Quem preside abre o corte de um recorte, lê a faixa calculada e clica em "Conferir antes de emitir".
Abre-se "Confira antes de emitir o corte", com a faixa, quem progride, quem fica fora e por quê, os
avisos que a tela já dava, e o que acontece depois. Só o botão da conferência emite. A sucessão do
corte e a faixa seguinte passam pela mesma conferência.

**Why this priority**: o corte decide quem segue para a habilitação, e é o único ato da cadeia
ordem → corte → convocação que ainda acontece no primeiro clique. A proposta já aparece na tela, e
por isso o risco é menor que o da chamada, que envia e-mail.

**Independent Test**: no C09, clicar em "Conferir antes de emitir" e conferir que nenhum corte
existe; confirmar e conferir que existe um, com a faixa conferida.

**Acceptance Scenarios**:

1. **Given** a faixa calculada (alvo 4, suplentes 2, 6 progridem até a 6ª), **When** quem preside
   clica em "Conferir antes de emitir", **Then** vê a mesma faixa, as seis pessoas com posição e
   consequência, quem fica fora com a causa, e nenhum corte foi gravado.
2. **Given** a conferência, **When** quem preside confirma, **Then** o corte é emitido como hoje, e a
   tela diz o que aconteceu e qual é o próximo passo.
3. **Given** a conferência aberta, **When** a ordem é sucedida antes da confirmação, **Then** a
   confirmação é recusada pela conferência do cálculo, como hoje, e nada é emitido.
4. **Given** um corte vigente e "Faixa seguinte" com quantidade 2 e motivo, **When** quem preside
   pede a conferência, **Then** vê as duas posições e as duas pessoas que a faixa alcança, o motivo,
   e que a faixa anterior não é revogada.
5. **Given** a recomendação de aguardar ou o reingresso pendente na tela do corte, **When** a
   conferência abre, **Then** o aviso se repete nela, com o mesmo texto.

---

### User Story 5 — O desfecho oferece o que cabe na chamada agora (Priority: P2)

Quem registra o desfecho escolhe entre as espécies que aquela chamada admite e que o comando
aceitaria agora. As que a chamada admite mas ainda não cabem aparecem numa nota abaixo do seletor,
cada uma com a razão e, quando houver, a partir de quando. As que a chamada nunca admite não
aparecem.

**Why this priority**: o comando já recusa as espécies que não cabem, e por isso o erro não se
grava; o custo hoje é carga e tentativa contra porta fechada, num formulário irreversível.

**Independent Test**: no C09, abrir o desfecho de Alice (vaga inicial, tudo conforme, prazo em curso,
sem atestado) e contar quatro opções; ler na nota "Não atendimento à convocação" com a data do
vencimento e "Cancelamento de matrícula por inércia" com a exigência do atestado; não encontrar
"Regularização" em lugar nenhum.

**Acceptance Scenarios**:

1. **Given** a chamada de Alice, **When** o formulário abre, **Then** o seletor oferece Aceite,
   Indeferimento, Desistência expressa e Reclassificação, sem nenhuma pré-escolhida.
2. **Given** a mesma chamada, **When** quem conduz lê a nota, **Then** ela diz que o não atendimento
   cabe a partir do vencimento, com a data, e que o cancelamento por inércia exige atestado de fato
   externo registrado.
3. **Given** uma chamada com documento ainda por conferir, **When** o formulário abre, **Then** Aceite
   não está no seletor, e a nota diz o que falta conferir, como a tela já dizia.
4. **Given** uma chamada para regularizar, **When** o formulário abre, **Then** Aceite e Cancelamento
   de matrícula por inércia não aparecem em lugar nenhum, e Regularização está no seletor quando
   nada falta conferir.
5. **Given** o vencimento decorrido, **When** o formulário abre, **Then** Não atendimento à
   convocação está no seletor.

---

### User Story 6 — O atestado só onde a inércia cabe (Priority: P3)

O gesto "Atestar fato externo" — que só serve de insumo ao cancelamento por inércia — aparece só nas
chamadas cuja espécie admite a inércia. O vocabulário dos fatos, que hoje é de curso a distância,
continua o de hoje nesta entrega (D-010).

**Why this priority**: é a menor parte do achado 12; o atestado não decide nada sozinho, mas oferecê-lo
onde a inércia não cabe ensina um caminho que não leva a desfecho nenhum.

**Independent Test**: abrir uma chamada para regularizar e não encontrar o gesto; abrir uma chamada
para vaga inicial e encontrá-lo.

**Acceptance Scenarios**:

1. **Given** uma chamada para regularizar, **When** o cartão abre, **Then** "Atestar fato externo"
   não está na linha das outras ações.
2. **Given** uma chamada para vaga inicial ou para vaga que vagou, **When** o cartão abre, **Then** o
   gesto está onde a `143` o pôs, com os fatos de hoje.

---

### Edge Cases

- **Pendência corrigida enquanto o formulário estava aberto.** A pessoa reenvia o documento pendente
  entre a abertura do atalho e o clique. O indeferimento continua possível — FR-3593 da `115` —, e o
  fundamento pré-redigido, já na tela, cita um documento que agora aguarda conferência. O comando não
  confere o fundamento, que é de quem registra (FR-3594 da `115`); a ciência da FR-5805, lida no
  instante do ato, continua exigida enquanto o prazo correr. Recusar o indeferimento porque o
  documento mudou seria regra nova, e fica fora.
- **Convocação sem vencimento informado** (Edital sem prazo publicado). O envio é aceito enquanto a
  chamada estiver em aberto (FR-3578 da `115`). Não há "prazo em curso" com data: a frase da FR-5804
  diz que não há vencimento e que a pessoa pode enviar enquanto não houver desfecho, e a ciência é a
  mesma.
- **Vencimento que decorre entre a abertura e o clique.** A ciência deixa de ser exigida; o comando a
  aceita se vier, e não recusa por ela.
- **Convocação corrigida entre a abertura e o clique** (`120`). O comando já recusa desfecho em
  convocação sucedida; a ciência não muda isso.
- **Nada enviado e o prazo vencido.** O atalho não aparece, e o cartão orienta para o não
  atendimento à convocação (FR-5809, D-011). O indeferimento continua no desfecho geral, para quem
  tiver outro fundamento.
- **Só um facultativo apresentado, e o prazo vencido sem os obrigatórios.** Houve apresentação: o
  atalho aparece pelos obrigatórios não apresentados (FR-5800). A pessoa respondeu à convocação, e o
  que falta é documento.
- **Chamada individual sem ninguém na fila.** O gesto não aparece, como hoje; a conferência pedida
  diretamente recusa com a razão do comando.
- **A conferência da chamada recarregada.** Pede a prévia de novo: nada é gravado, e a página mostra
  o estado de agora.
- **Formulário antigo ou forjado com "confirmar"** — na chamada, no corte ou na faixa seguinte. Sem o
  resumo do que foi conferido, ou com resumo que não confere, o pedido abre a conferência; nunca
  pratica.
- **Faixa seguinte maior que o resto da ordem.** O comando a aceita e alcança só quem resta — às
  vezes ninguém (FR-5846). A conferência mostra a quantidade pedida ao lado de quantas pessoas a
  faixa alcança, antes do botão.
- **Duplo clique na confirmação** — chamada, corte ou faixa seguinte. A chave de idempotência já
  concluída devolve o resultado do ato praticado, sem ato novo.
- **Quem só lê** — o membro alocado à conferência de documentos e a auditoria — não vê nenhum dos
  gestos, e pedir a conferência diretamente é recusado como o ato é hoje.
- **Desfecho que deixa de caber entre a abertura e o clique** (o atestado foi registrado noutra aba;
  o vencimento passou). O seletor é fotografia; o comando decide, como hoje.

## Requirements *(mandatory)*

### Functional Requirements

#### O indeferimento pelas pendências

- **FR-5800**: O atalho de indeferimento pelas pendências MUST ser oferecido só quando a chamada tem
  ao menos um documento pedido em uma destas situações:
  - conferido como **pendente**, com o motivo registrado pela comissão;
  - **obrigatório não apresentado**, com o vencimento informado já decorrido e com ao menos um
    documento apresentado pela pessoa nesta chamada (D-011).

  Documento a apresentar com o prazo em curso, ou apresentado e ainda sem conferência, MUST NOT, por
  si, fazer o atalho aparecer.
- **FR-5801**: O fundamento pré-redigido do atalho MUST citar só os documentos que o fizeram
  aparecer — o pendente com o motivo; o não apresentado com a frase de que não foi apresentado no
  prazo. MUST NOT citar documento conforme, aguardando conferência ou a apresentar com o prazo em
  curso. O texto continua editável, obrigatório e de quem registra (FR-3594 da `115`).
- **FR-5802**: Havendo documento apresentado e ainda sem conferência, o formulário de indeferimento
  — atalho ou desfecho geral — MUST nomeá-lo e dizer que o indeferimento o deixa sem conferir.
- **FR-5803**: O indeferimento registrado — pelo atalho ou pelo desfecho geral — numa chamada com o
  vencimento informado ainda não decorrido e com ao menos um documento pedido ainda não conforme
  MUST, antes do ato, dizer o vencimento e que até ele a pessoa ainda pode enviar ou corrigir os
  documentos, e pedir a ciência de quem registra, numa marca desmarcada.
- **FR-5804**: Na convocação sem vencimento informado, com documento pedido ainda não conforme, a
  frase da FR-5803 MUST dizer que a convocação não tem vencimento e que a pessoa pode enviar ou
  corrigir enquanto não houver desfecho; a ciência é a mesma.
- **FR-5805**: O comando de desfecho MUST recusar o indeferimento nas condições da FR-5803 ou da
  FR-5804 que chegue sem a ciência: nada é gravado, a recusa tem código próprio e diz por quê, e a
  tela devolve o formulário com o fundamento digitado. A condição MUST ser lida pelo comando no
  instante do ato, e não pelo formulário.
- **FR-5806**: O registro do indeferimento praticado com a ciência MUST permitir saber, depois, que
  ele foi feito com o prazo em curso — ou sem vencimento — e com a ciência de quem o registrou.
- **FR-5807**: A conferência do texto do desfecho, quando houver, MUST repetir o vencimento e a frase
  da FR-5803, e a ciência marcada antes dela MUST chegar ao comando sem ser pedida de novo.
- **FR-5808**: Nenhum outro desfecho MUST passar a depender do estado documental ou do prazo por esta
  spec. O indeferimento continua possível em qualquer estado documental (FR-3593 da `115`); o que
  muda é a ciência. Nada nasce do decurso (FR-274 da `019`).
- **FR-5809**: Com o vencimento informado decorrido e nenhum documento apresentado pela pessoa nesta
  chamada, o atalho MUST NOT aparecer, e o cartão MUST dizer que nada foi apresentado no prazo e
  apontar o desfecho "Não atendimento à convocação" (D-011). O documento aproveitado da inscrição não
  conta como apresentado nesta chamada. O indeferimento MUST continuar disponível pelo desfecho
  geral, com as regras desta spec.

#### A chamada individual e a chamada para regularizar

- **FR-5810**: Os gestos "Chamar uma pessoa da fila" e "Chamar para regularizar" MUST passar por uma
  conferência antes do ato, com ou sem complemento digitado. Nenhum pedido desses gestos MUST
  praticar o ato sem trazer o resumo da conferência que o mostrou.
- **FR-5811**: A conferência MUST mostrar a pessoa (protocolo e nome), a posição dela na fila, a
  espécie da chamada e a origem da espécie. Na chamada para regularizar, MUST mostrar o Resultado
  indeferido que a chamada regulariza.
- **FR-5812**: Quando a pessoa escolhida não é a próxima da fila, a conferência MUST mostrar quem ela
  passa à frente e dizer que a exceção fica registrada na trilha. Sem a marca de precedência, MUST
  recusar antes do botão, com a razão do comando.
- **FR-5813**: A conferência MUST mostrar o fundamento como o candidato o lerá no portal, já com o
  complemento; quando a forma do Perfil é a mensagem individual, o assunto e o texto da mensagem,
  compostos pelo mesmo modelo que o envio usa, com o link indicado; quando é a publicação, que
  nenhuma mensagem sai neste ato e que o prazo corre da publicação.
- **FR-5814**: A conferência MUST mostrar o vencimento e a origem dele — digitado, ou o fim de um
  Evento do Cronograma —, ou dizer que nenhum vencimento foi informado e o que a mensagem dirá.
- **FR-5815**: Pedir a conferência MUST NOT criar convocação, enviar mensagem, registrar evento na
  trilha, reservar a chave de idempotência nem gravar nada na sessão de quem pede.
- **FR-5816**: A confirmação MUST levar a chave de idempotência emitida pela tela da convocação e o
  resumo do que foi conferido — a pessoa, a espécie, o fundamento, a mensagem e o prazo —, e só
  pratica quando o resumo recomposto no clique é o mesmo. Com resumo diferente, MUST voltar à
  conferência com o texto de agora e a frase de que ele mudou.
- **FR-5817**: A conferência MUST recusar, com a razão e antes de mostrar o botão, tudo o que o
  comando recusaria pela mesma leitura: pessoa já convocada ou fora da fila, precedência sem marca,
  apuração obsoleta ou ausente, forma de comunicar não declarada, vencimento inválido e Processo que
  não aceita mudança. A conferência e o comando MUST usar a mesma verificação, e não duas.
- **FR-5818**: Um pedido de confirmação cuja chave já foi concluída MUST ir direto ao comando, que
  repete o resultado do ato já praticado, sem convocação nem mensagem nova.
- **FR-5819**: A conferência e a confirmação MUST exigir a mesma autorização do gesto de hoje.
- **FR-5820**: Na conferência, o complemento MUST continuar editável, e conferir de novo MUST mostrar a
  prévia nova; o vencimento e a pessoa MUST viajar sem edição — mudá-los é voltar à tela. A
  conferência MUST oferecer "Cancelar e voltar" para a tela da convocação do mesmo recorte.
- **FR-5821**: Para estes dois gestos, a conferência desta spec MUST substituir a conferência de texto
  que a `125` abre quando há complemento (FR-3993 da `125`): uma conferência só, nunca duas em
  sequência. Revê a FR-4817 da `140` para estes dois gestos.
- **FR-5822**: O botão dos dois gestos e a ajuda do complemento MUST dizer que o clique leva à
  conferência e que nada é praticado nem enviado antes dela.
- **FR-5823**: A correção da convocação (`120`) MUST continuar como está, com a prévia assinada dela
  (FR-3857 da `120`).

#### O corte

- **FR-5825**: A emissão do corte — a primeira e a sucessão — MUST passar por uma conferência antes do
  ato. Nenhum pedido MUST emitir sem trazer o resumo da conferência que o mostrou.
- **FR-5826**: A conferência do corte MUST mostrar a faixa que será emitida: alvo declarado, alvo
  apurado, suplentes, quantos progridem, quantos ficam fora e a última posição alcançada; quem
  progride, com posição; quem fica fora, com posição e causa. Na sucessão, MUST mostrar também o
  motivo digitado e que a geração vigente continua legível.
- **FR-5827**: A conferência do corte MUST dizer o que acontece depois: quem progride segue para a
  Etapa seguinte que o marco declara, quem fica fora continua registrado no ato, e corrigir é suceder
  com motivo.
- **FR-5828**: Os avisos que a tela do corte dá antes do botão — a recomendação de aguardar e o
  reingresso pendente por recurso — MUST se repetir na conferência, com o mesmo texto.
- **FR-5829**: A faixa seguinte MUST passar pela mesma conferência, mostrando a quantidade pedida, as
  posições e as pessoas que a faixa alcança, o motivo, e que a faixa anterior não é revogada.
  Quantidade que o comando recusaria MUST ser recusada na conferência, antes do botão.
- **FR-5830**: Pedir a conferência do corte ou da faixa seguinte MUST NOT gravar ato, evento na
  trilha, chave de idempotência nem nada na sessão de quem pede.
- **FR-5831**: A confirmação MUST levar intacta a chave de idempotência que a tela do corte emitiu, e
  a conferência do cálculo da faixa que a conferência mostrou, recomposta nela; o comando MUST
  conferi-la como hoje. O que mudou entre a tela do corte e a conferência MUST ser dito na
  conferência. Cálculo mudado entre a conferência e a confirmação MUST recusar com a razão, sem
  emitir, e devolver à tela do corte com a faixa de agora.
- **FR-5832**: Um pedido de confirmação cuja chave já foi concluída MUST ir direto ao comando, que
  repete o resultado do ato já praticado.
- **FR-5833**: A conferência e a confirmação do corte MUST exigir a mesma autorização de hoje, e a
  conferência MUST oferecer "Cancelar e voltar" para a tela do corte do mesmo recorte.

#### O desfecho e o atestado

- **FR-5835**: O seletor do desfecho MUST oferecer só as espécies que:
  - a espécie da chamada admite, pela tabela de desfechos por espécie de convocação que o domínio já
    tem e o comando já aplica; e
  - o comando aceitaria agora pelas guardas de hoje, entre elas: o não atendimento só depois do
    envio da comunicação e do vencimento, quando há vencimento (FR-269a da `019`); a inércia só com
    atestado registrado (FR-277 da `019`) e com a pessoa ocupando vaga no recorte; o aceite e a
    regularização só sem documento obrigatório por conferir (FR-3592 da `115`).
- **FR-5836**: As espécies que a chamada admite e que não cabem agora MUST aparecer numa nota abaixo do
  seletor, cada uma com a razão, com as palavras da recusa do comando, e, quando a razão é o prazo,
  com a data e a hora a partir das quais cabe.
- **FR-5837**: As espécies que a espécie da chamada nunca admite MUST NOT aparecer no seletor nem na
  nota.
- **FR-5838**: O seletor e o comando MUST ler a mesma verificação, e não duas. O comando MUST
  continuar recusando como hoje: o seletor não é fronteira.
- **FR-5839**: O seletor MUST continuar sem espécie pré-escolhida, mesmo quando só uma cabe.
- **FR-5840**: O gesto "Atestar fato externo" MUST aparecer só nas chamadas cuja espécie admite o
  cancelamento por inércia; nas chamadas para regularizar, MUST NOT aparecer.
- **FR-5841**: Os rótulos das espécies de desfecho e dos fatos do atestado MUST continuar os de hoje
  nesta entrega (D-010). Esta spec MUST NOT mudar rótulo de espécie já registrada, nem texto de
  documento publicado, e MUST NOT inferir a natureza da seleção de dado nenhum — em particular, da
  declaração do Requerimento de Matrícula.

#### Comum

- **FR-5845**: As conferências desta spec MUST funcionar sem script e sem estilo escrito no template,
  sob a política de conteúdo da gestão.
- **FR-5846**: Nada nesta spec MUST mudar quem é chamado, a espécie, a ordem da fila, o fundamento
  derivado, a mensagem, a faixa calculada, a autorização de qualquer gesto, nem as guardas de
  desfecho, exceto a ciência da FR-5805.

### Requisitos de experiência

- **UX-530**: Os gestos da chamada individual e da chamada para regularizar MUST dizer "Conferir
  antes de convocar", e a conferência MUST seguir o desenho da do lote — título "Confira antes de
  convocar", o ato irreversível em destaque, "Cancelar e voltar" ao lado do botão. O botão de
  confirmar MUST nomear a pessoa e, quando há mensagem, dizê-la ("Convocar Davi e enviar 1
  mensagem").
- **UX-531**: O botão do corte MUST dizer "Conferir antes de emitir", como o da ordem, e a página,
  "Confira antes de emitir o corte"; o de confirmar, "Emitir o corte". Na faixa seguinte: "Conferir a
  faixa seguinte", e "Emitir a faixa seguinte".
- **UX-532**: O aviso do prazo em curso MUST vir imediatamente antes da marca de ciência, ligado a
  ela, e a marca MUST dizer o que se sabe, e não "concordo": por exemplo, *"Sei que o prazo vence em
  11/12/2026 17:44 e que a pessoa ainda pode enviar ou corrigir, e indefiro agora."*
- **UX-533**: A nota das espécies que não cabem agora MUST ser curta, uma linha por espécie, sob o
  título "Ainda não cabem nesta chamada".
- **UX-534**: A recusa numa conferência MUST dizer a razão com as palavras do comando e oferecer a
  volta à tela, sem formulário.
- **UX-535**: A orientação da FR-5809 MUST ocupar o lugar do passo do cartão, e não o de uma ação:
  por exemplo, *"O prazo venceu em 11/12/2026 17:44 sem nenhum documento apresentado. O desfecho que
  descreve isso é o não atendimento à convocação."*, com o caminho ao formulário do desfecho.

### Key Entities

Nenhuma entidade nova. A ciência do indeferimento (FR-5806) é atributo do registro do desfecho; onde
ela mora é decisão do plano. As conferências leem a fila e as prévias da `050`, o fundamento por
espécie, a forma de comunicar do Perfil, o modelo da mensagem da `121`, a proposta e a conferência
do cálculo do corte, e a leitura documental da `115`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1900**: No C11, o cartão de Alice — nada enviado, prazo em curso — não oferece o atalho do
  indeferimento; em 100% das chamadas sem documento pendente e sem obrigatório não apresentado após o
  vencimento, o atalho não aparece.
- **SC-1901**: Em 100% dos indeferimentos pedidos com o prazo em curso — ou sem vencimento — e com
  documento ainda não conforme, sem a ciência, nenhum desfecho é gravado; o teste o confere pelo
  atalho e pelo desfecho geral.
- **SC-1902**: Em 100% dos pedidos da chamada individual e da chamada para regularizar sem o resumo da
  conferência, nenhuma convocação nasce e nenhuma mensagem sai; com e sem complemento.
- **SC-1903**: A confirmação enviada duas vezes produz exatamente uma convocação e uma mensagem; o
  mesmo vale para um corte e para uma faixa seguinte.
- **SC-1904**: Em 100% dos pedidos de emissão do corte, de sucessão e de faixa seguinte sem o resumo
  da conferência, nenhum ato é gravado.
- **SC-1905**: No C09, o seletor do desfecho de Alice oferece exatamente 4 espécies; a nota nomeia 2;
  "Regularização" não aparece na página.
- **SC-1906**: Para toda combinação de espécie de chamada, estado do prazo, estado documental e
  existência de atestado do conjunto de casos do teste, uma espécie oferecida no seletor nunca é
  recusada pelas guardas da FR-5835, e uma não oferecida sempre seria.
- **SC-1907**: O texto da mensagem que a conferência da chamada individual mostra é, frase a frase, o
  que o envio confirmado entrega, exceto o endereço do link.
- **SC-1908**: As páginas novas — conferência da chamada e conferência do corte — cabem a 1440 px e a
  375 px sem rolagem horizontal e sem violação da política de conteúdo.
- **SC-1909**: Quem não pode praticar um gesto hoje continua recusado, na conferência e na confirmação,
  com a mesma resposta.
- **SC-1910**: Em 100% das chamadas com o vencimento decorrido e nenhum documento apresentado, o
  atalho do indeferimento não aparece e o cartão aponta o não atendimento; com ao menos um apresentado
  e um obrigatório faltando, o atalho aparece.

## Decisões

### D-001 — O atalho segue a pendência, e não o que impede o aceite

*Proposta.* "Pendência" no atalho é o documento conferido como pendente, com motivo, ou o obrigatório
não apresentado depois do vencimento por quem apresentou ao menos um documento (FR-5800, D-011). Hoje a tela usa a lista do que impede o aceite, que
inclui o documento ainda no prazo e o enviado à espera da comissão.

**Por quê**: as duas listas respondem a perguntas diferentes. "O que impede o aceite?" inclui o que
está do lado da comissão; "do que a pessoa deixou de cumprir?" não. O fundamento do indeferimento é
mostrado à pessoa no portal, e não pode dizer que ela não atendeu o que ainda podia atender ou o que
a comissão ainda não leu. **Descartado**: esconder o atalho só pelo prazo — com pendência registrada e
prazo em curso, o atalho é útil, e a FR-5803 protege o caso.

### D-002 — Avisar e pedir ciência, nos dois caminhos

**Decisão do usuário (11/11/2026), questão 1, opção A.** Com o prazo em curso e documento não
conforme, o indeferimento pede a ciência explícita — pelo atalho e pelo desfecho geral —, conferida
pelo comando, e não é bloqueado: pode haver fundamento para decidir antes do vencimento.

**Por quê**: a FR-3593 da `115` diz que os demais desfechos não dependem do estado documental, e a
decisão "Nada automático" da mesma spec deixa o desfecho a quem conduz. Há indeferimento legítimo no
prazo — a pessoa declarou não ter o diploma; o documento apresentado é de outra pessoa. Bloquear
mudaria regra de domínio da `115`; a ciência mantém a regra e torna a decisão deliberada. Aplicá-la
só no atalho deixaria o mesmo ato, pelo desfecho geral, sem proteção — o defeito do achado 08 em outra
forma.

### D-003 — A ciência é conferida pelo comando

*Proposta.* A marca não é só da tela: o comando recusa sem ela (FR-5805), como já faz com a ciência
das inaplicabilidades no aceite (FR-4468 da `131`).

**Por quê**: a Constituição (Princípio IV) põe no domínio as regras que afetam documentação e
desfecho; validação de interface não é fronteira. Um formulário antigo, ou outra tela que um dia
registre desfecho, não pode pular a ciência.

### D-004 — A chamada individual usa a conferência do lote, com uma pessoa

*Proposta.* A conferência da chamada individual é a da `140` — mesma página, mesma composição da
mensagem, mesmo resumo assinado, mesma recusa —, com uma pessoa e com o que é próprio dela: a
posição na fila e a precedência.

**Por quê**: o estudo pediu "a mesma conferência"; uma segunda composição divergiria da primeira e
do envio. A `140` deixou a chamada individual fora para o menor escopo coerente e registrou o achado
para o usuário decidir; o estudo o confirmou na prática, com o e-mail saindo no primeiro clique.

### D-005 — A chamada para regularizar entra junto

*Proposta.* "Chamar para regularizar" passa pela mesma conferência (FR-5810).

**Por quê**: é o mesmo ato pelo mesmo caminho — convoca e comunica no clique —, com a mesma
consequência. Deixá-la fora repetiria, um nível abaixo, o "mesmo tipo de ato, proteção diferente" que
o achado 08 aponta. **Alternativa**, se o usuário preferir o menor escopo: só a chamada individual, com a
regularização registrada como achado.

### D-006 — O corte ganha página de conferência, como a ordem

*Proposta.* "Conferir antes de emitir" abre uma página própria (FR-5825). **Descartado**: uma marca
"Conferi a faixa" na própria tela do corte, que seria mais leve — a proposta já está visível — e
deixaria a ordem e o corte, atos vizinhos e do mesmo peso, com proteções diferentes.

**Por quê**: o achado é a diferença de proteção entre atos do mesmo tipo. A ordem tem página; o lote
de titulares tem página; o corte, entre os dois, deve ter a mesma. A página também dá lugar a dizer o
que acontece depois (FR-5827), que a tela do corte só diz depois do clique.

### D-007 — A faixa seguinte e a sucessão do corte entram

*Proposta.* As duas passam pela conferência do corte (FR-5825, FR-5829).

**Por quê**: a faixa seguinte recebe uma quantidade digitada, e é ali que um 40 no lugar de 4 alcança
36 pessoas a mais; a sucessão troca o ato vigente. As duas são tão irreversíveis quanto a primeira
emissão.

### D-008 — O seletor lê as guardas do comando; o que não cabe agora é dito, o que nunca cabe some

*Proposta.* O seletor oferece o que o comando aceitaria; a nota diz o que caberá depois e por quê; o
que a espécie da chamada nunca admite não aparece (FR-5835 a FR-5837).

**Por quê**: esconder sem dizer faria quem procura "Não atendimento" achar que o sistema não o tem;
mostrar tudo é o defeito. A nota responde "onde está?" sem convidar ao clique. A tabela de desfechos
por espécie de convocação já existe no domínio, e a verificação única evita que tela e comando
divirjam.

### D-009 — O atestado segue a inércia

*Proposta.* O gesto do atestado aparece só onde a inércia é admitida (FR-5840). Os fatos oferecidos
não mudam nesta entrega (D-010).

**Por quê**: o atestado não tem outro uso no sistema senão fundamentar a inércia. Filtrar os fatos por
natureza da seleção exige um eixo que o sistema não tem, e fica para spec própria (D-010).

### D-010 — Os rótulos ficam; o vocabulário por natureza é spec própria

**Decisão do usuário (11/11/2026), questão 2, opção A.** Os rótulos das espécies de desfecho e dos
fatos do atestado continuam os de hoje nesta entrega (FR-5841). O vocabulário por natureza da seleção
fica para uma spec própria, e **sem** inferir a natureza pela existência de Requerimento de Matrícula.

**Por quê**: o sistema não tem natureza do Processo — a `029` decidiu não criá-la —, e inventá-la
aqui, ou deduzi-la da declaração do requerimento, mudaria o vocabulário de todos os certames por um
sinal que não foi feito para isso. O filtro por estado desta spec já tira do seletor o que a chamada
não admite.

### D-011 — Prazo vencido sem nada apresentado aponta o não atendimento

**Decisão do usuário (11/11/2026), questão 3, opção B.** Com o vencimento decorrido e nenhum
documento apresentado, o atalho de indeferimento não aparece, e o cartão orienta para "Não
atendimento à convocação" (FR-5809). Com apresentação parcial, o atalho aparece pelos obrigatórios
não apresentados e pelas pendências (FR-5800). O indeferimento continua disponível pelo desfecho
geral.

**Por quê**: o não atendimento é o desfecho que a `019` desenhou para quem foi chamado e não
respondeu; o indeferimento pelas pendências descreve quem respondeu com falta. A distinção fica na
tela, sem tirar de quem conduz o caminho do desfecho geral.

*Proposta, na leitura da decisão.* "Apresentado" é o que a pessoa enviou **nesta chamada**. O
documento aproveitado da inscrição não conta: ele não é resposta à convocação, e contá-lo faria o
atalho aparecer para quem nunca respondeu.

## Questões respondidas

As três questões foram respondidas pelo usuário em 11/11/2026, e as respostas estão nas decisões.

- **Questão 1 — Com o prazo em curso, o indeferimento é avisado ou bloqueado?** Avisado, com ciência
  explícita pelos dois caminhos, conferida pelo comando (D-002). Descartados: esconder o atalho até o
  vencimento; recusar todo indeferimento com documento não conforme até o vencimento, que reveria a
  FR-3593 da `115`.
- **Questão 2 — O vocabulário muda com a natureza da seleção?** Não nesta entrega; fica para spec
  própria, sem inferência pelo Requerimento de Matrícula (D-010). Descartados nesta entrega: rótulos
  neutros para todos; criar a natureza da seleção no Processo; deduzi-la da declaração do
  requerimento.
- **Questão 3 — Prazo vencido sem nada apresentado: o atalho aparece?** Não; o cartão orienta para o
  não atendimento, e o atalho fica para a apresentação parcial (D-011). Descartado: o atalho sempre
  que houver obrigatório não apresentado após o vencimento.

## Achados registrados

Encontrados ao escrever esta spec, fora do escopo dela. Governança é do usuário.

- **A inércia de quem aceitou não tem gesto na tela.** O comando admite suceder um desfecho com
  motivo — a recusa dele cita *"o cancelamento por inércia de quem havia aceitado"* —, mas o
  formulário do desfecho só aparece na chamada **sem** desfecho, e não tem campo de motivo. Na tela,
  a inércia só é alcançável antes do aceite, numa pessoa que conta como ocupante pela apuração e que
  nunca se matriculou. O filtro desta spec não corrige isso: ele oferece a inércia onde o comando a
  aceita.
- **A conferência genérica dos atos irreversíveis** (melhoria M-12 do estudo de continuidade de
  10/11) continua fora: esta spec cobre os três atos que o estudo de 11/11 encontrou.

## Assumptions

- A tela da convocação e a do corte continuam emitindo a chave de idempotência no GET; o corte, a
  conferência do cálculo. As conferências as recebem e devolvem sem gerar outras.
- A leitura documental da chamada distingue, como hoje, pendente, a apresentar, apresentado sem
  conferência, conforme e não se aplica; a FR-5800 lê esses estados, sem estado novo.
- A correção de documento pendente pela pessoa, dentro do prazo, é aceita como hoje (`115`).
- Os cenários C09 e C11 da `134` servem de caso de verificação; o resultado do estudo neles é o
  "antes".

## Fora do escopo

- A correção da convocação (`120`), que tem prévia assinada própria.
- A mudança de rótulos por natureza da seleção, que fica para spec própria (D-010).
- O gesto da inércia de quem aceitou (achado registrado).
- A conferência de texto do desfecho além do aviso da FR-5807.
- Qualquer mudança de quem é chamado, da espécie, da fila, do fundamento, da mensagem, da faixa ou
  das guardas dos desfechos, exceto a ciência da FR-5805.
