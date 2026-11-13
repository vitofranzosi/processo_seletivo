# Feature Specification: Conferência antes de convocar os titulares

**Feature Branch**: `claude/140-conferencia-ao-convocar-d54ffb`, sobre a `main` em `4ae78556`

**Created**: 2026-11-10

**Status**: Implementada e mergeada (#448). As tarefas não foram marcadas à época. *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Draft

**Nenhuma regra de convocação nova.** Quem é chamado, a espécie, a ordem da fila, o fundamento, a
forma de comunicar e o prazo continuam os de hoje, derivados pelos mesmos caminhos da `050`, da
`121` e da `125`. Não há migration, tabela, coluna, permissão nem estado persistido novo. O que muda
é **quando** o ato acontece: o gesto dos titulares deixa de praticar no primeiro clique e passa a
praticar só depois de uma conferência.

**Input**: *"Conferência antes de convocar os titulares (M-04 do estudo de continuidade operacional
de 10/11/2026). O gesto 'Convocar as N' da tela da convocação passa sempre por uma conferência,
mesmo sem complemento: quem será convocado e para que espécie de vaga, o texto que cada pessoa lerá
(o fundamento no portal e a mensagem de e-mail), o prazo ou a falta dele, e quem fica de fora e por
quê. A prévia não tem efeito colateral (não envia, não cria convocação, não grava nada); a
confirmação pratica uma vez só, com a chave de idempotência e a assinatura do alcance preservadas; a
autorização é a de hoje; estado mudado entre prévia e confirmação recusa com a razão. A chamada
individual fica fora. Corrige a ajuda do complemento que prometia a conferência."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil e oitocentos a quatro mil oitocentos e vinte e nove;
> - os critérios de mil e quinhentos a mil quinhentos e nove;
> - os requisitos de experiência de trezentos e trinta a trezentos e trinta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 10/11/2026, nas `specs/` de todas as worktrees desta máquina e da `main`:
> requisito quatro mil setecentos e quarenta e oito e critério mil quatrocentos e oitenta, ambos da
> `136`, que reservou até o requisito quatro mil setecentos e cinquenta e nove. A `139`, escrita em
> paralelo noutra sessão, ainda não tinha spec; a folga entre a reserva da `136` e esta faixa fica
> para ela, e a reserva está registrada nas notas compartilhadas das duas sessões.
>
> **Origem.** O
> [estudo de continuidade operacional de 10/11/2026](../../doc/estudo-continuidade-operacional-2026-11-10/README.md)
> (PR #445): o passo D3 do mapa das jornadas, a melhoria M-04 do inventário e o protótipo
> `convocar-c15-conferencia`. O protótipo é referência de comportamento, e não código a copiar.

## Por que esta feature existe

No C10 dos cenários de treinamento da `134`, "Convocar as 3" praticou as três convocações e **enviou
as três comunicações no mesmo clique**. A convocação é o ato irreversível que mais longe vai: ele
sai do sistema, e a mensagem chega à caixa de entrada de cada candidato. Corrigi-lo é suceder cada
convocação com motivo, uma a uma — e a mensagem que saiu não volta.

A tela já mostrava, antes do botão, quem seria convocado e o fundamento derivado. O que faltava:

1. **A conferência só existia com complemento digitado.** A da `125` intercepta o ato quando há
   texto livre (FR-3993 da `125`), e deixa o gesto sem complemento confirmar direto. A decisão fazia
   sentido para o texto livre; não para um ato que envia N mensagens.
2. **A ajuda prometia o que não acontecia.** Ao lado do complemento, a tela dizia *"antes de
   confirmar, você o verá como o candidato"*. Lida por quem não digitou nada, a frase promete uma
   conferência geral, e o clique seguinte praticava o ato.
3. **A mensagem não aparecia em lugar nenhum.** A tela mostra o fundamento, que o candidato lê no
   portal. O e-mail que sai no mesmo ato — com o prazo, o que a convocação pede e o link — só era
   visto por quem o recebia.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conferir antes de convocar os titulares (Priority: P1)

Quem conduz a convocação abre a tela de um recorte com titulares a chamar, informa o prazo (ou não)
e clica em "Convocar as N". Em vez de o ato acontecer, abre-se uma conferência: as pessoas que serão
convocadas e para que espécie de vaga, o texto que cada uma lerá no portal e na mensagem, o prazo ou
a falta dele, e quem fica de fora e por quê. Só o botão da conferência pratica o ato.

**Why this priority**: é o defeito do estudo. Sem ela, nada mais desta spec tem efeito.

**Independent Test**: no C10 da `134`, clicar "Convocar as 3" sem complemento e conferir que a
página seguinte é a conferência, com as três pessoas, e que nenhuma convocação nasceu e nenhuma
mensagem saiu; confirmar, e conferir que nasceram três e saíram três.

**Acceptance Scenarios**:

1. **Given** um recorte com dois titulares a chamar e uma suplente, **When** quem conduz clica em
   "Convocar as 2" sem complemento, **Then** vê a conferência com as duas pessoas "para vaga
   inicial", o fundamento, a mensagem, o prazo e a suplente como "fica de fora", e nenhuma
   convocação existe nem mensagem saiu.
2. **Given** a conferência aberta, **When** quem conduz confirma, **Then** nascem as duas convocações
   e saem as duas comunicações, e a tela da convocação diz o que aconteceu, como hoje.
3. **Given** a conferência aberta, **When** quem conduz escolhe "Cancelar e voltar", **Then** volta à
   tela da convocação, e nada foi praticado.
4. **Given** um Perfil que comunica por publicação, **When** a conferência abre, **Then** ela diz que
   nenhuma mensagem sai neste ato e que o prazo corre da publicação registrada depois, e o botão não
   promete envio.

---

### User Story 2 - A confirmação pratica uma vez só, e só sobre o que foi conferido (Priority: P1)

Entre a conferência e o clique, a tela pode ser enviada duas vezes (duplo clique, recarga) e o
recorte pode mudar (outra apuração, uma Retificação, outra pessoa convocando). A confirmação pratica
o ato uma única vez, e só se o que a pessoa conferiu ainda for o que será praticado.

**Why this priority**: é o requisito de segurança que o usuário exigiu, e o que separa uma
conferência de um clique a mais.

**Independent Test**: enviar a confirmação duas vezes e contar uma convocação por pessoa e uma
mensagem por pessoa; mudar a apuração entre a conferência e a confirmação e ver a recusa com a
razão, sem convocação nova.

**Acceptance Scenarios**:

1. **Given** uma confirmação já praticada, **When** o mesmo formulário chega de novo, **Then**
   nenhuma convocação nem mensagem nova nasce, e a tela diz o resultado do ato que já aconteceu.
2. **Given** a conferência aberta, **When** o alcance muda antes da confirmação, **Then** a
   confirmação é recusada com a razão, nada é praticado, e quem conduz volta ao alcance de agora.
3. **Given** a conferência aberta, **When** o texto que a pessoa leria muda antes da confirmação — o
   complemento editado na própria conferência, ou o fundamento ou a mensagem derivados de novo —,
   **Then** a confirmação não pratica, e a conferência volta com o texto novo e o aviso de que mudou.

---

### User Story 3 - A ajuda diz o que acontece (Priority: P2)

A ajuda do complemento no gesto dos titulares deixa de prometer uma conferência condicional e passa
a dizer o que acontece: o clique abre a conferência, e o ato só acontece nela.

**Why this priority**: com a conferência sempre, a frase antiga deixa de mentir; a nova evita que
alguém entenda o botão como o ato.

**Independent Test**: ler a tela da convocação e conferir a frase nova, ligada ao campo.

**Acceptance Scenarios**:

1. **Given** a tela da convocação com titulares a chamar, **When** quem conduz lê o gesto, **Then**
   o botão diz que leva à conferência, e a ajuda diz que nada é praticado nem enviado antes dela.

---

### Edge Cases

- **Nada a convocar quando a conferência é pedida** — a apuração ficou obsoleta, a forma de
  comunicar não está declarada, o marco é intermediário, não há titular, ou o Processo não aceita
  mais mudança: a conferência não mostra botão de confirmar; diz a razão, com as mesmas palavras da
  recusa que a confirmação daria, e oferece voltar.
- **Vencimento inválido** — digitado no passado, com Evento e data ao mesmo tempo, ou com Evento
  que saiu do Cronograma: a conferência recusa com a razão do comando, antes de mostrar o botão.
  Conferir um texto para um ato que só pode ser recusado é um passo que não leva a lugar nenhum.
- **A conferência recarregada** — recarregar a página da conferência pede a prévia de novo: nada é
  gravado, e a página mostra o estado de agora.
- **Formulário antigo ou forjado com "confirmar"** — sem o resumo do texto conferido, ou com um
  resumo que não confere, o pedido abre a conferência; nunca pratica.
- **A virada do dia entre a conferência e a confirmação** — a mensagem diz "faltam N dias", e a
  contagem muda à meia-noite. A confirmação volta à conferência com o texto novo; é o
  comportamento da história 2, e não uma recusa à parte.
- **Duas mensagens diferentes no mesmo gesto** — se titulares do mesmo recorte recebem variantes
  diferentes da mensagem (um pede documento, outro não), a conferência mostra cada variante com
  quantas pessoas a receberão.
- **Quem só lê a convocação** — o membro alocado à conferência de documentos e a auditoria veem a
  tela e não veem o gesto; pedir a conferência diretamente é recusado como o ato é hoje.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-4800**: O gesto de convocar os titulares MUST passar por uma conferência antes do ato, com ou
  sem complemento digitado. Nenhum pedido do gesto MUST praticar o ato sem trazer o resumo da
  conferência que o mostrou.
- **FR-4801**: A conferência MUST mostrar cada pessoa que será convocada, na ordem da fila, com
  protocolo e nome, e a espécie de vaga para a qual cada uma será convocada, com a origem da espécie.
- **FR-4802**: A conferência MUST mostrar o fundamento que cada convocação gravará, como o candidato
  o lerá no portal, já com o complemento, quando houver.
- **FR-4803**: Quando a forma do Perfil é a mensagem individual, a conferência MUST mostrar o assunto
  e o texto da mensagem que cada pessoa receberá, compostos pelo mesmo modelo que o envio usa. O
  link da convocação, que é de cada pessoa, MAY aparecer como indicação em vez do endereço.
- **FR-4804**: Quando a forma é a publicação, a conferência MUST dizer que nenhuma mensagem sai neste
  ato e que o prazo corre da publicação que se registra depois.
- **FR-4805**: A conferência MUST mostrar o vencimento e a sua origem — digitado, ou o fim de um
  Evento do Cronograma —, ou dizer que nenhum vencimento foi informado e o que a mensagem dirá nesse
  caso.
- **FR-4806**: A conferência MUST mostrar quem fica de fora do gesto e por quê: a pessoa em que o
  gesto para (suplente ou reabilitada por recurso), as demais da fila depois dela, e quem pode ser
  chamado para regularizar, cada grupo com a razão e com o gesto que o alcançaria.
- **FR-4807**: Pedir a conferência MUST NOT criar convocação, MUST NOT enviar mensagem, MUST NOT
  registrar evento na trilha, MUST NOT reservar a chave de idempotência e MUST NOT gravar nada na
  sessão de quem pede.
- **FR-4808**: A confirmação MUST levar a chave de idempotência e a assinatura do alcance que a tela
  da convocação emitiu, intactas, e o comando MUST conferi-las como hoje.
- **FR-4809**: A confirmação MUST levar o resumo do texto conferido — o fundamento, a mensagem e o
  prazo, com o número de pessoas —, e só pratica quando o resumo recomposto no clique é o mesmo.
  Com resumo diferente, MUST voltar à conferência com o texto de agora e a frase de que o texto mudou.
- **FR-4810**: Com alcance diferente do assinado, a conferência e a confirmação MUST recusar com a
  razão do comando, sem praticar nada e sem mostrar o botão de confirmar.
- **FR-4811**: A conferência MUST recusar, com a razão e antes de mostrar o botão, tudo o que a
  confirmação recusaria pela mesma leitura: marco intermediário, impedimento do gesto, alcance
  mudado, nenhum titular, vencimento inválido e Processo que não aceita mudança. A conferência e o
  comando MUST usar a mesma verificação, e não duas.
- **FR-4812**: Um pedido de confirmação cuja chave já foi concluída MUST ir direto ao comando, que
  repete o resultado do ato já praticado, sem convocação nem mensagem nova.
- **FR-4813**: A conferência e a confirmação MUST exigir a mesma autorização do gesto de hoje. Quem
  não a tem MUST ser recusado como hoje, sem ver a conferência.
- **FR-4814**: Na conferência, o complemento MUST continuar editável, e conferir de novo MUST
  mostrar a prévia nova. O vencimento MUST viajar sem edição: mudá-lo é voltar à tela.
- **FR-4815**: A conferência MUST oferecer "Cancelar e voltar" para a tela da convocação do mesmo
  recorte.
- **FR-4816**: O botão do gesto na tela da convocação e a ajuda do complemento MUST dizer que o
  clique leva à conferência e que nada é praticado nem enviado antes dela.
- **FR-4817**: A chamada individual, a convocação para regularizar e a correção MUST continuar como
  estão, com a conferência de texto da `125` quando há complemento.
- **FR-4818**: A conferência MUST funcionar sem script e sem estilo escrito no template, sob a
  política de conteúdo da gestão.
- **FR-4819**: A ajuda do complemento na correção da convocação MUST dizer que a conferência do
  texto vale quando há complemento escrito, e não prometê-la em geral. É a mesma frase condicional
  que, no gesto dos titulares, lia como promessa geral.

### Requisitos de experiência

- **UX-330**: A conferência MUST seguir o desenho das conferências da gestão: título "Confira antes
  de convocar", o ato irreversível em destaque, os grupos com título e contagem, e "Cancelar e
  voltar" ao lado do botão.
- **UX-331**: O botão de confirmar MUST repetir o número de pessoas e, quando há mensagem, o de
  mensagens ("Convocar as 2 e enviar 2 mensagens").
- **UX-332**: A recusa na conferência MUST dizer a razão com as palavras do comando e oferecer a
  volta à tela, sem formulário.

### Key Entities

Nenhuma entidade nova. A conferência lê a prévia dos titulares da `050`, o fundamento por espécie, a
forma de comunicar do Perfil, o Cronograma da versão vigente e o modelo da mensagem da `121`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1500**: Em 100% dos pedidos do gesto dos titulares sem o resumo da conferência, nenhuma
  convocação nasce e nenhuma mensagem sai; o teste o confere com e sem complemento.
- **SC-1501**: A conferência do C10 mostra as 3 pessoas, a espécie, o fundamento, a mensagem, o
  prazo (ou a falta dele) e quem fica de fora, numa página só, a 1440 px e a 375 px, sem rolagem
  horizontal e sem violação de CSP.
- **SC-1502**: A confirmação enviada duas vezes produz exatamente uma convocação e uma mensagem por
  pessoa.
- **SC-1503**: A confirmação depois de uma mudança de alcance, ou de texto, não produz convocação; a
  resposta diz a razão.
- **SC-1504**: Quem não pode praticar o gesto hoje continua recusado, na conferência e na
  confirmação, com a mesma resposta.
- **SC-1505**: O texto da mensagem que a conferência mostra é, frase a frase, o que o envio
  confirmado entrega, exceto o endereço do link.

## Decisões

### D-001 — A chamada individual fica fora

**Decisão**: a conferência sempre vale só para o gesto dos titulares. A chamada individual, a
convocação para regularizar e a correção continuam com a conferência de texto da `125`, que
intercepta quando há complemento.

**Por quê**: o estudo encontrou o defeito no gesto em lote (o passo D3), e a ajuda que prometia a
conferência é a dele. Na chamada individual a pessoa é escolhida no próprio formulário, uma a uma, e
o fundamento de cada espécie aparece antes do botão. O menor escopo coerente é o lote. Fica
registrado como achado para o usuário decidir: a chamada individual também envia mensagem num
clique, e a mesma conferência caberia nela.

### D-002 — A conferência é uma página própria, respondida ao pedido

**Decisão**: o pedido do gesto responde com a página da conferência, sem redirecionar e sem
portador na sessão. A conferência da `125` guarda a prévia na sessão e redireciona à tela da
convocação; esta não grava nada.

**Por quê**: o usuário exigiu que a prévia não grave nada, e a sessão é gravação. Uma página própria
também segue o desenho das conferências da gestão (`marco_conferir`), em vez de pendurar a
conferência no alto de uma tela longa. Recarregar a página pede a prévia de novo, o que é inofensivo.

### D-003 — A mensagem mostrada é a do modelo do envio, com o link indicado

**Decisão**: a conferência compõe a mensagem pela mesma função que o envio usa, com o mesmo modelo,
a mesma variante — derivada da lista que a versão vigente pede para a pessoa — e a mesma unidade. O
link, que é de cada pessoa, aparece como indicação. Pessoas com a mesma mensagem são agrupadas.

**Por quê**: uma segunda composição feita para a tela poderia divergir do que sai. A mesma função
prova, por construção, que o texto conferido é o que chega (SC-1505).

### D-004 — Uma verificação só, para a conferência e para o comando

**Decisão**: as recusas que o comando faz pela leitura do recorte saem de uma função do domínio que
o comando chama dentro da transação e a conferência chama fora dela, sem trava.

**Por quê**: duas listas de recusas divergiriam. Fora da trava, a resposta da conferência é uma
fotografia; o comando continua sendo quem decide, sob a trava.

### D-005 — A confirmação repetida vai direto ao comando

**Decisão**: se a chave de idempotência do gesto já foi concluída por esta pessoa, a confirmação vai
ao comando, que devolve o resultado do ato já praticado, sem recompor a conferência.

**Por quê**: depois do primeiro clique o alcance mudou — as pessoas já foram convocadas —, e a
recomposição recusaria o segundo pedido como "alcance mudou". Quem deu duplo clique leria uma
recusa sobre um ato que aconteceu. A repetição pela chave é a garantia de hoje.

### D-006 — O resumo do texto cobre fundamento, mensagem e prazo

**Decisão**: o resumo assinado pela conferência é o da `125` (o texto e o número de pessoas), com o
texto sendo a junção do fundamento, das mensagens e da frase do prazo.

**Por quê**: o alcance assinado pela tela já cobre quem, a apuração, a versão e a forma. O que pode
mudar sem mudar o alcance — o complemento, a unidade que assina a mensagem, a contagem de dias — é
texto, e a pessoa tem de ver o texto que sai.

## Assumptions

- A tela da convocação continua emitindo a chave de idempotência e a assinatura do alcance no GET,
  como hoje; a conferência as recebe e devolve sem gerar outras.
- O número de titulares de um gesto é pequeno (dezenas, no máximo), e compor a mensagem por grupo de
  variante cabe no tempo de uma página.
- A suíte de navegador que clica no gesto, quando existir, passa a clicar também na conferência.

## Fora do escopo

- Conferência genérica para os outros atos irreversíveis (o M-12 do estudo).
- A chamada individual (D-001).
- Qualquer mudança de quem é chamado, da espécie, da ordem da fila, do fundamento ou da mensagem.
