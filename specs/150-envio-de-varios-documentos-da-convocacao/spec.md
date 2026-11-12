# Feature Specification: O envio de vários documentos da convocação, sem perder escolha

**Feature Branch**: `claude/candidate-document-upload-issue-99ca4c`, sobre a `main` em `1b467b4f`

**Created**: 2026-11-11

**Status**: Spec escrita em 11/11/2026, a partir de um relato de uso na área do candidato e do
diagnóstico do código. As decisões estão em [research.md](research.md), para revisão no PR.
Revista em 11/11/2026 para incluir o achado 11 do estudo da jornada final — o mesmo arquivo em dois
documentos (User Story 5, FR-5615 a FR-5619, UX-504, SC-1806, SC-1807, D-006) —, com o plano e as
tarefas. Depois da análise cruzada, a FR-5610 foi revista (o documento em voo na queda de
conexão), entraram dois casos-limite e a seção *Achados registrados*.

**Input**: *"Na área do candidato, na convocação que pede documentos, o candidato escolhe arquivos em
vários cartões e clica em Enviar num deles: só o arquivo daquele cartão é enviado, a página recarrega
e as outras escolhas se perdem sem aviso. Corrigir para que o candidato possa enviar de uma vez todos
os arquivos escolhidos, sem perder nenhuma escolha em silêncio, mantendo o envio individual por
cartão."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de cinco mil e seiscentos a cinco mil seiscentos e vinte e nove;
> - os critérios de mil e oitocentos a mil oitocentos e nove;
> - os requisitos de experiência de quinhentos a quinhentos e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 11/11/2026 nas `specs/` de todas as worktrees desta máquina: requisito cinco
> mil quatrocentos e trinta e oito, critério mil setecentos e quinze e UX quatrocentos e sessenta e
> cinco. Dois PRs abertos nesta data (#469 e #470) disputam o número `148` e a faixa a partir de cinco
> mil e quatrocentos; um deles há de se renumerar, e por isso esta spec toma o número `150` e começa
> a faixa com folga.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature;
> decisão de outra feature, pelo assunto, nunca pelo identificador.

## Por que esta feature existe

A convocação que pede documentos mostra um cartão por documento, e cada cartão tem o próprio campo
de arquivo e o próprio botão "Enviar" (`FR-3745` da `118`). Cada botão envia só o arquivo do seu
cartão, e a volta é a página inteira de novo, na confirmação (`FR-3870` da `121`).

A pessoa candidata não lê a tela assim. Ela vê quatro documentos pedidos, escolhe os quatro arquivos e
clica em "Enviar" uma vez — no último cartão, ou no primeiro. Um documento chega; a página recarrega;
os outros três cartões voltam a "Nenhum arquivo escolhido". **Nada diz que as escolhas se perderam.**
Quem não confere o "Andamento" acredita que enviou tudo, e o prazo corre.

A própria tela induz o erro: a escolha de um arquivo dá peso ao botão "Enviar" do cartão, e com
quatro escolhas a página mostra quatro botões destacados, todos prometendo a mesma coisa que só um
deles cumpre.

Nada disso pede regra nova. A validação do arquivo, o prazo, a trilha e a conferência continuam as da
`115`: o que muda é que **um clique pode levar todos os arquivos escolhidos, e nenhum arquivo
escolhido some sem ter sido enviado ou sem a tela dizer**.

**O que esta spec não faz.** A inscrição tem o mesmo defeito — os cartões da lista exigida trocam o
bloco inteiro a cada envio, e as outras escolhas também somem —, mas fica fora daqui: está
registrada como achado em [research.md](research.md), para decisão do usuário (D-004).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Enviar de uma vez os documentos escolhidos (Priority: P1)

A pessoa convocada escolhe os arquivos de vários documentos e os envia com um clique só. Cada
documento é recebido como se tivesse sido enviado sozinho.

**Why this priority**: É o defeito relatado. Hoje a pessoa perde o trabalho de escolher e, pior,
pode acreditar que enviou o que não enviou, com prazo correndo.

**Independent Test**: Numa convocação que pede quatro documentos, escolher os quatro arquivos e
acionar o botão de enviar de qualquer um dos cartões; conferir que os quatro foram recebidos, que a
confirmação diz os quatro, e que o "Andamento" conta quatro enviados.

**Acceptance Scenarios**:

1. **Given** uma convocação aberta com quatro documentos a enviar e nenhum escolhido, **When** a
   pessoa escolhe o arquivo do primeiro, **Then** o botão desse cartão diz "Enviar", como hoje, e os
   demais cartões não mudam.
2. **Given** o primeiro arquivo escolhido, **When** a pessoa escolhe o arquivo do terceiro, **Then**
   o botão do primeiro e o do terceiro passam a dizer "Enviar os 2 documentos escolhidos".
3. **Given** quatro arquivos escolhidos, **When** a pessoa aciona o botão de qualquer um dos quatro
   cartões, **Then** a tela diz qual documento está sendo enviado e quantos faltam ("Enviando 2 de 4:
   ‹documento›… Não feche esta página."), e ao fim volta à confirmação, que lista os quatro
   documentos recebidos com data e hora.
4. **Given** os quatro recebidos, **When** a tela volta, **Then** os quatro cartões estão em "O que
   você já apresentou", na situação "Aguardando conferência", e a próxima tarefa é a da `FR-3726` da
   `118` — o Requerimento, se faltar, ou nenhuma.

---

### User Story 2 — Saber o que não foi recebido, sem perder o que foi (Priority: P1)

Quando um dos arquivos é recusado — não é PDF, passa do limite, o prazo venceu — ou a conexão cai no
meio, a pessoa sabe exatamente o que chegou e o que não chegou, e o que chegou continua recebido.

**Why this priority**: Sem isto, o envio de vários troca uma perda silenciosa por outra. A recusa é
comum: foto do documento no lugar do PDF é o caso que a `009` já orienta.

**Independent Test**: Escolher quatro arquivos, sendo o segundo uma imagem; enviar; conferir que três
foram recebidos, que a confirmação diz os três e aponta o que faltou, e que o cartão do segundo traz a
recusa de hoje.

**Acceptance Scenarios**:

1. **Given** quatro arquivos escolhidos, o segundo uma imagem, **When** a pessoa envia, **Then** o
   primeiro, o terceiro e o quarto são recebidos, a confirmação diz "Recebemos 3 de 4 documentos" com
   os três nomes, e diz que um não foi recebido, com link para o cartão dele; o cartão do segundo
   traz a recusa de hoje sobre foto e PDF.
2. **Given** dois arquivos escolhidos, os dois acima do limite, **When** a pessoa envia, **Then**
   nenhum é recebido, a tela volta ao cartão do primeiro, com o foco na recusa, e o cartão do segundo
   também traz a recusa dele.
3. **Given** quatro arquivos escolhidos, **When** a conexão cai durante o envio do terceiro, **Then**
   a tela não sai da página: diz que o primeiro e o segundo foram recebidos, que o terceiro e o quarto
   não foram, com a frase de falha de conexão de hoje, e os dois continuam escolhidos, com o botão
   "Enviar os 2 documentos escolhidos" disponível de novo.
4. **Given** quatro arquivos escolhidos e o acesso da pessoa expirado noutra aba, **When** ela envia,
   **Then** nenhum documento é recebido, a tela não sai da página e diz a frase de acesso expirado de
   hoje, e as quatro escolhas continuam no lugar.

---

### User Story 3 — Enviar só um, mesmo com outros escolhidos (Priority: P2)

A pessoa escolheu vários arquivos mas quer enviar só um agora — por exemplo, porque desconfia de um
deles. Ela desfaz as escolhas que não quer e envia o que quer, sem que nada se perca às escondidas.

**Why this priority**: Mantém o envio individual, que é o que a pessoa tinha. É P2 porque o caso
comum é enviar tudo.

**Independent Test**: Escolher três arquivos, desfazer a escolha de dois, conferir que o botão do que
resta diz "Enviar", enviar e conferir que só aquele foi recebido.

**Acceptance Scenarios**:

1. **Given** três arquivos escolhidos, **When** a pessoa aciona "Remover a escolha" em dois cartões,
   **Then** esses dois voltam a "Nenhum arquivo escolhido" e o botão do terceiro passa a dizer
   "Enviar".
2. **Given** dois arquivos escolhidos, **When** a pessoa aciona o botão de enviar de um terceiro
   cartão, sem arquivo, **Then** a tela não sai da página, o cartão vazio diz "Escolha um arquivo PDF
   antes de enviar." e as duas escolhas continuam no lugar.

---

### User Story 4 — A tela sem script continua honesta (Priority: P3)

No navegador sem script, a pessoa continua enviando um documento por vez, como hoje, e a tela lhe diz
isso antes que ela escolha vários.

**Why this priority**: O portal funciona sem script desde a `010`, e o envio da convocação também
(`FR-3872` da `121`). O caso é raro, mas a perda silenciosa nele seria a mesma de hoje.

**Independent Test**: Abrir a convocação com o script desligado e conferir a frase antes do primeiro
cartão; enviar um documento e conferir a volta de hoje.

**Acceptance Scenarios**:

1. **Given** o script desligado e documentos a enviar, **When** a pessoa abre a convocação, **Then**
   antes do primeiro cartão com envio a tela diz que os documentos se enviam um de cada vez, e que o
   arquivo escolhido nos outros cartões não é guardado quando um deles é enviado.
2. **Given** o script ligado, **When** a pessoa abre a mesma convocação, **Then** essa frase não
   aparece.

---

### User Story 5 — Saber, antes de enviar, que o arquivo é o mesmo de outro documento (Priority: P2)

*(Acrescentada em 2026-11-11, pelo achado 11 do estudo da jornada final.)*

A pessoa escolhe para um documento o mesmo arquivo que escolheu — ou que já enviou — para outro. Antes
de enviar, o cartão lhe diz isso; ela troca o arquivo ou envia assim mesmo.

**Why this priority**: No estudo, o mesmo PDF foi aceito como "Diploma" e como "Comprovante de
residência", e o erro só apareceu na conferência: uma rodada de pendência, aviso e reenvio, com prazo
correndo. O envio de vários torna o engano mais provável — quatro escolhas seguidas na mesma tela. É
P2 porque o aviso não muda o que se recebe; poupa a rodada.

**Independent Test**: Numa convocação com "Diploma" e "Comprovante de residência", escolher o mesmo
PDF nos dois cartões; conferir o aviso nos dois, antes do envio, e que o envio dos dois continua
possível. Enviar o diploma; depois, escolher o mesmo PDF no cartão do comprovante e conferir o aviso
"que você já enviou para Diploma".

**Acceptance Scenarios**:

1. **Given** dois documentos a enviar, **When** a pessoa escolhe `diploma.pdf` para o primeiro e o
   mesmo arquivo, renomeado `residencia.pdf`, para o segundo, **Then** o cartão do segundo diz que o
   arquivo é o mesmo escolhido para o primeiro, o do primeiro diz o mesmo do segundo, e o botão dos
   dois continua "Enviar os 2 documentos escolhidos".
2. **Given** o aviso nos dois cartões, **When** a pessoa troca o arquivo do segundo por outro, **Then**
   o aviso some dos dois.
3. **Given** o diploma já enviado, **When** a pessoa escolhe o mesmo PDF no cartão do comprovante,
   **Then** o cartão diz que o arquivo é o mesmo que ela já enviou para o diploma, e ela pode enviá-lo
   assim mesmo, com a confirmação de hoje.
4. **Given** dois arquivos diferentes de mesmo nome, **When** a pessoa os escolhe em dois cartões,
   **Then** nenhum aviso aparece.

### Edge Cases

- **O mesmo arquivo escolhido em dois cartões** *(revista em 2026-11-11, pelo achado 11 do estudo da
  jornada final — a redação anterior está ao fim desta alínea)*. Cada cartão o envia como envio
  próprio, e nenhum dos dois é recusado; mas, antes do envio, os dois cartões dizem que o arquivo é o
  mesmo (FR-5615 a FR-5619). Vale também para o arquivo escolhido que é idêntico ao já enviado para
  outro documento da convocação. O aviso não bloqueia (D-006).

  > **Redação anterior, preservada:** Cada cartão o envia como envio próprio; o sistema não compara
  > arquivos entre documentos hoje, e esta spec não cria a regra.
- **O mesmo arquivo de novo no mesmo cartão.** Não é a regra do arquivo repetido entre documentos: o
  servidor já o reconhece e diz *"Este arquivo já tinha sido recebido."* (`FR-3581` da `115`). O aviso
  da FR-5615 não compara o cartão com o próprio arquivo recebido.
- **Mesmo nome, conteúdo diferente — ou nomes diferentes, mesmo conteúdo.** O que decide é o
  conteúdo: dois arquivos de nome igual e conteúdo diferente não produzem aviso; dois de nome
  diferente e conteúdo idêntico produzem.
- **O prazo vence no meio do envio de vários.** Cada documento é julgado no instante em que chega,
  pela regra de hoje (`FR-3578` da `115`): os que chegaram antes são recebidos, os seguintes recebem a
  recusa de prazo no cartão.
- **A comissão decide a convocação no meio do envio.** O mesmo: o que chegou antes fica; os
  seguintes são recusados pela regra de hoje.
- **A pessoa fecha a página no meio.** Os já recebidos ficam; os não enviados se perdem, e o aviso
  "não feche esta página" já estava à vista.
- **A pessoa volta pelo botão "voltar" do navegador depois do envio.** A página restaurada não deixa
  botão desabilitado nem aviso de envio à mostra (o cuidado que a `121` já tem com o envio de um).
- **Cartão de "Enviar outro arquivo"**, dos documentos já apresentados, e cartão de documento
  opcional. Contam como qualquer outro: com arquivo escolhido, entram no envio de vários.
- **Um cartão só tem envio possível.** Nada muda em relação a hoje.
- **Escolher de novo um arquivo no mesmo cartão.** Troca a escolha; a contagem não muda.
- **Um arquivo acima do limite no meio do lote** *(acrescentado em 2026-11-11, pela análise cruzada do
  plano)*. É recusado como hoje, com a frase de tamanho de hoje no cartão dele, e os seguintes são
  enviados (FR-5606). O arquivo grande não precisa viajar para ser recusado (R-009 do research).
- **Dois lotes ao mesmo tempo, em duas abas da mesma pessoa.** Cada documento continua recebido ou
  recusado pela regra de hoje; a confirmação da volta pode mostrar só o lote que começou por último.
  Limite aceito: o caso é raro, e o "Andamento" conta tudo.

## Requirements *(mandatory)*

### Functional Requirements

#### A. Nenhuma escolha se perde em silêncio

- **FR-5600**: Com script, nenhum envio iniciado na tela da convocação MUST descartar o arquivo
  escolhido em outro cartão sem que esse arquivo tenha sido enviado ou sem que a tela diga, no cartão
  dele, que não foi.
- **FR-5601**: Com dois ou mais cartões com arquivo escolhido, o botão de enviar de **cada um desses
  cartões** MUST dizer "Enviar os N documentos escolhidos", com o N corrente, e enviar todos eles.
  Com exatamente um, o botão MUST dizer "Enviar" e enviar só aquele, como hoje.
- **FR-5602**: O N MUST contar todos os cartões da tela com envio possível e arquivo escolhido — os
  de "O que falta", os opcionais e os de "Enviar outro arquivo" dos já apresentados.
- **FR-5603**: Cada cartão com arquivo escolhido MUST oferecer "Remover a escolha", que volta o
  cartão a "Nenhum arquivo escolhido" e atualiza o N dos demais.
- **FR-5604**: Com script, acionar o envio num cartão sem arquivo escolhido MUST NOT sair da página:
  o cartão MUST dizer a frase de hoje, "Escolha um arquivo PDF antes de enviar.", e as escolhas dos
  outros cartões MUST continuar no lugar.

#### B. O envio de vários

- **FR-5605**: O envio de vários MUST registrar cada documento como um envio próprio, idêntico ao
  envio de um só: a mesma validação, o mesmo prazo, a mesma trilha e o mesmo efeito sobre a
  conferência (`FR-3578` da `115`). Nenhuma regra de aceitação nova.
- **FR-5606**: Os documentos MUST ser enviados um de cada vez, na ordem em que os cartões aparecem na
  tela, e a recusa de um MUST NOT impedir o envio dos seguintes. O documento recebido MUST continuar
  recebido se um seguinte for recusado ou se a conexão cair.
- **FR-5607**: Durante o envio de vários, a tela MUST dizer qual documento está sendo enviado e
  quantos são ("Enviando 2 de 4: ‹documento›… Não feche esta página."), e os botões de enviar, de
  escolher e de remover a escolha MUST ficar desabilitados até o fim.
- **FR-5608**: Terminado o envio de vários com ao menos um documento recebido, a tela MUST voltar à
  convocação na âncora da confirmação (`FR-3870` da `121`), e a confirmação MUST:
  - dizer quantos documentos foram recebidos e quantos foram enviados ("Recebemos 3 de 4
    documentos"), e listar cada recebido com data e hora;
  - havendo recusados, dizer quantos não foram recebidos, com link para o cartão de cada um;
  - trazer a próxima tarefa como a `FR-3870` da `121` já traz.
  A recusa de cada documento não recebido MUST estar no cartão dele, com a frase de hoje
  (`FR-3871` da `121`).
- **FR-5609**: Terminado o envio de vários sem nenhum documento recebido, a tela MUST voltar ao cartão
  do primeiro recusado, com o foco na recusa, e a recusa de cada um dos outros MUST estar no cartão
  dele.
- **FR-5610** *(revista em 2026-11-11, pela análise cruzada do plano — a redação anterior está ao fim
  desta alínea)*: Se a conexão falhar ou o acesso expirar no meio do envio de vários, a tela MUST NOT
  sair da página. Ela MUST dizer quais documentos foram recebidos até ali e quais não foram enviados,
  com a frase de falha de hoje. O documento que estava sendo enviado quando a conexão caiu pode ter
  chegado sem que a resposta voltasse: dele, a tela MUST NOT afirmar nem que chegou nem que não
  chegou; MUST dizer que não é possível saber, e que recarregar a página mostra o que foi recebido.
  Os não enviados e esse documento MUST continuar escolhidos, e o botão MUST voltar a oferecer o
  envio deles — reenviar o que já tinha chegado não duplica nada (`FR-3581` da `115`).

  > **Redação anterior, preservada:** Se a conexão falhar ou o acesso expirar no meio do envio de
  > vários, a tela MUST NOT sair da página. Ela MUST dizer quais documentos foram recebidos até ali e
  > quais não foram, com a frase de falha de hoje; os não enviados MUST continuar escolhidos, e o
  > botão MUST voltar a oferecer o envio deles.
- **FR-5611**: O envio de vários MUST NOT guardar nada no navegador — nem nome de arquivo, nem
  arquivo, nem progresso —, como o envio de um já não guarda: a tela carrega documentos pessoais, e
  num computador compartilhado o que fica guardado é o que vaza.

#### C. Sem script

- **FR-5612**: Sem script, cada cartão MUST continuar com o envio de um documento, com a volta de hoje
  (`FR-3870` e `FR-3871` da `121`). A tela MUST dizer, antes do primeiro cartão com envio, que os
  documentos se enviam um de cada vez e que o arquivo escolhido nos outros cartões não é guardado
  quando um deles é enviado. Com script, essa frase MUST NOT aparecer.

#### D. O que esta spec revisa

- **FR-5613**: Esta spec revisa a `FR-3745` da `118` só no nome acessível do botão de enviar enquanto
  houver dois ou mais escolhidos: ele MUST ser o texto visível, "Enviar os N documentos escolhidos",
  porque todos os botões fazem então a mesma coisa. Com um só escolhido, ou nenhum, vale a `FR-3745`
  como está.
- **FR-5614**: Esta spec revisa a `FR-3872` da `121` na parte "nenhum script novo": o envio de vários
  MAY vir num script estático próprio, ou nos já carregados, sem biblioteca nova e sem script ou
  estilo escritos no template, que a política de conteúdo recusa.

#### E. O mesmo arquivo em dois documentos

*(Acrescentada em 2026-11-11, pelo achado 11 do estudo da jornada final,
`doc/estudo-jornada-final-2026-11-11/`: o candidato enviou o mesmo PDF como "Diploma" e como
"Comprovante de residência"; o GPS conhecia o resumo SHA-256 dos dois e aceitou sem alerta, e o erro
só apareceu na conferência, ao custo de uma rodada de pendência e reenvio.)*

- **FR-5615**: Com script, ao escolher um arquivo num cartão, a tela MUST compará-lo, **pelo
  conteúdo** (o resumo SHA-256 que a `115` já guarda em cada apresentação), com:
  - o arquivo escolhido, e ainda não enviado, em cada **outro** cartão da tela; e
  - o arquivo vigente de cada **outro** documento da mesma convocação que já tenha apresentação —
    aguardando conferência, conferido, com pendência, ou aproveitado da inscrição.

  Sendo idêntico a algum deles, o cartão MUST dizer, junto ao nome do arquivo escolhido e antes do
  envio, com qual documento o arquivo coincide: *"Atenção: este arquivo é o mesmo que você escolheu
  para ‹documento›."* ou *"Atenção: este arquivo é o mesmo que você já enviou para ‹documento›."* —
  e, coincidindo com mais de um, o nome de cada um.
- **FR-5616**: O aviso da FR-5615 MUST NOT impedir o envio, pedir confirmação, mudar o rótulo ou o
  destaque do botão, nem tirar o cartão do envio de vários: um mesmo documento pode servir
  legitimamente a dois itens (D-006). O envio do arquivo avisado segue a FR-5605, sem regra de
  aceitação nova.
- **FR-5617**: Quando dois cartões com arquivo escolhido coincidem entre si, o aviso MUST aparecer
  **nos dois**, cada um nomeando o outro. O aviso MUST sumir do cartão quando a escolha que o causou
  for trocada ou removida (FR-5603), aqui ou no outro cartão.
- **FR-5618**: A comparação MUST acontecer no navegador, sem enviar ao servidor o arquivo, o resumo
  ou o nome antes do ato de enviar — escolher continua não enviando nada (D-003) — e sem guardar nada
  no navegador (FR-5611).
- **FR-5619**: Sem script, ou quando o navegador não consegue calcular o resumo, não há aviso antes
  do envio, e a tela MUST NOT dizer que comparou o arquivo; o envio segue como na FR-5612. Se a
  comparação ainda não terminou quando a pessoa aciona o envio, o envio MUST seguir sem esperá-la.

### Requisitos de experiência

- **UX-500**: O botão "Enviar os N documentos escolhidos" é o destaque de cada cartão com arquivo
  escolhido, como o "Enviar" já é hoje; não há botão flutuante nem barra fixa na tela.
- **UX-501**: A mudança do N é anunciada a quem usa leitor de tela, sem roubar o foco: "3 documentos
  escolhidos para enviar." O progresso do envio de vários também, a cada documento.
- **UX-502**: A 375 px de largura, o botão com o texto mais longo cabe no cartão sem rolagem
  horizontal, quebrando a linha se preciso.
- **UX-503**: "Remover a escolha" é ação secundária, de texto, ao lado do nome do arquivo escolhido;
  o nome acessível dela diz o documento ("Remover a escolha: ‹documento›").
- **UX-504**: O aviso do arquivo repetido (FR-5615) é texto de atenção, em palavra e não só em cor,
  logo abaixo do nome do arquivo escolhido, e faz parte da descrição acessível do campo do cartão. Ele
  é anunciado a quem usa leitor de tela quando aparece, sem roubar o foco, e cabe a 375 px sem rolagem
  horizontal.

### Key Entities

Nenhuma entidade nova. O envio de vários é uma sequência de apresentações de documento da `115`,
cada uma com o seu registro e a sua trilha.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1800**: Numa convocação com quatro documentos pedidos, escolher os quatro arquivos e acionar
  **um** botão resulta em quatro documentos recebidos, em qualquer um dos quatro cartões em que o
  botão for acionado.
- **SC-1801**: Em cada um dos cenários — um documento só; vários, todos aceitos; vários, um recusado;
  vários, todos recusados; queda de conexão no meio; acesso expirado; envio acionado em cartão vazio —
  o número de arquivos escolhidos que somem sem ter sido enviados e sem frase na tela é **zero**.
- **SC-1802**: Num envio de quatro em que o segundo é recusado, três são recebidos, e a pessoa
  identifica pela confirmação qual não foi, sem abrir outra tela.
- **SC-1803**: Sem script, o envio de um documento segue idêntico ao de hoje, e a frase da
  `FR-5612` aparece; com script, ela não aparece.
- **SC-1804**: Só pelo teclado e com leitor de tela, a pessoa escolhe três arquivos, envia os três e
  ouve o progresso e a confirmação; a 375 px, nenhuma etapa provoca rolagem horizontal.
- **SC-1805**: Numa sessão de validação com pelo menos três pessoas que nunca viram a tela, todas
  enviam os quatro documentos pedidos na primeira tentativa, sem orientação.
- **SC-1806**: Numa convocação com dois documentos pedidos, com script, escolher o mesmo PDF nos dois
  cartões — com o mesmo nome ou com nomes diferentes —, ou escolher para um o PDF já enviado para o
  outro, mostra o aviso da FR-5615 antes do envio em **todos** os casos; e o envio continua possível,
  com o mesmo número de cliques de hoje.
- **SC-1807**: Arquivos de conteúdo diferente — inclusive os de mesmo nome — produzem **zero**
  avisos; e o reenvio do mesmo arquivo para o mesmo documento continua com a frase de hoje, sem o
  aviso da FR-5615.

## Decisões

As decisões estão com a razão e as alternativas descartadas em [research.md](research.md). O resumo:

- **D-001** — com dois ou mais escolhidos, todo botão de enviar envia todos, e diz isso.
- **D-002** — um envio por documento, em sequência, e não uma requisição com todos.
- **D-003** — nada se envia ao escolher o arquivo.
- **D-004** — a inscrição fica fora, registrada como achado.
- **D-005** — sem script, uma frase, e não um formulário único.
- **D-006** — o arquivo repetido entre documentos é avisado no cartão, antes do envio, e não
  bloqueado (acrescentada em 2026-11-11, pelo achado 11 do estudo da jornada final).

## Perguntas ao usuário

Abertas em 2026-11-11, com a revisão do achado 11. A spec, como está escrita, adota a resposta
indicada em cada uma; a implementação não depende de outra resposta para começar.

- **Pergunta 1 — Sem script, o aviso vem depois do recebimento?** A FR-5619 deixa o caminho sem
  script sem aviso nenhum: o envio é um formulário por cartão, e não há onde comparar antes. O
  servidor poderia dizer, na confirmação, que o arquivo recebido é idêntico ao já enviado para outro
  documento — regra nova no servidor, depois do ato, que também cobriria o navegador sem o cálculo do
  resumo. **Como está:** não; o aviso é só antes do envio, com script.
- **Pergunta 2 — A comissão vê a coincidência na conferência?** O achado 11 nasceu do lado do
  candidato, mas a comissão também ganharia ao saber, na conferência, que dois documentos da pessoa
  têm o mesmo arquivo. É mudança na gestão, que esta spec deixa fora, e a tela de conferência está
  sendo mexida pela `157` (o visualizador). **Como está:** fora desta spec.
- **Pergunta 3 — O aviso alcança documentos de outra chamada?** A FR-5615 compara só dentro da mesma
  convocação. Uma pessoa convocada de novo, depois de vaga reaberta, pode reaproveitar arquivos
  legitimamente. **Como está:** só a mesma convocação.

O bloqueio total foi considerado e não é proposto: o usuário decidiu que o aviso não bloqueia
(D-006).

## Achados registrados

Encontrados ao planejar esta spec, fora do escopo dela. Governança é do usuário.

- **A tela da convocação não é marcada como não armazenável.** `portal.views.convocacao` responde
  sem `Cache-Control: no-store`, ao contrário de outras telas do portal com dado pessoal, que usam
  `resposta_privada` ou `marcar_como_privada` (`shared/http.py`). A tela já traz nome, documentos
  pedidos e o link do arquivo de cada um; esta spec acrescenta o resumo SHA-256 do arquivo vigente
  (FR-5615), que não revela o conteúdo. Constatado em 11/11/2026, na `main` em `ef568113`.

## Assumptions

- Uma convocação pede poucos documentos — da ordem de uma dezena —, e o envio em sequência de todos
  cabe na espera que a pessoa já tem hoje para um de cada vez.
- O limite de tamanho por arquivo continua o de hoje, por documento, e o limite de corpo da requisição
  do portal, no proxy de produção, continua dimensionado para **um** arquivo por requisição.
- O prazo, a validação do arquivo e as frases de recusa são os de hoje; esta spec não os toca.

## Fora do escopo

- A lista exigida da inscrição, que tem o mesmo defeito (D-004).
- Vários arquivos para um mesmo documento: continua um arquivo por documento (`FR-3578` da `115`).
- Arrastar e soltar arquivos, ou escolher vários arquivos de uma vez num campo só e distribuí-los
  entre os documentos.
- Retomada de envio interrompido, envio em pedaços ou envio em segundo plano.
- Qualquer mudança na gestão, na conferência ou na trilha — inclusive mostrar à comissão que dois
  documentos têm o mesmo arquivo (Pergunta 2).
- Recusar, no servidor, o arquivo idêntico ao de outro documento (D-006).
