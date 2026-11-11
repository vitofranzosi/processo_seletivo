# Feature Specification: O envio de vários documentos da convocação, sem perder escolha

**Feature Branch**: `claude/candidate-document-upload-issue-99ca4c`, sobre a `main` em `1b467b4f`

**Created**: 2026-11-11

**Status**: Spec escrita em 11/11/2026, a partir de um relato de uso na área do candidato e do
diagnóstico do código. As decisões estão em [research.md](research.md), para revisão no PR.

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

### Edge Cases

- **O mesmo arquivo escolhido em dois cartões.** Cada cartão o envia como envio próprio; o sistema não
  compara arquivos entre documentos hoje, e esta spec não cria a regra.
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
- **FR-5610**: Se a conexão falhar ou o acesso expirar no meio do envio de vários, a tela MUST NOT
  sair da página. Ela MUST dizer quais documentos foram recebidos até ali e quais não foram, com a
  frase de falha de hoje; os não enviados MUST continuar escolhidos, e o botão MUST voltar a oferecer
  o envio deles.
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

### Requisitos de experiência

- **UX-500**: O botão "Enviar os N documentos escolhidos" é o destaque de cada cartão com arquivo
  escolhido, como o "Enviar" já é hoje; não há botão flutuante nem barra fixa na tela.
- **UX-501**: A mudança do N é anunciada a quem usa leitor de tela, sem roubar o foco: "3 documentos
  escolhidos para enviar." O progresso do envio de vários também, a cada documento.
- **UX-502**: A 375 px de largura, o botão com o texto mais longo cabe no cartão sem rolagem
  horizontal, quebrando a linha se preciso.
- **UX-503**: "Remover a escolha" é ação secundária, de texto, ao lado do nome do arquivo escolhido;
  o nome acessível dela diz o documento ("Remover a escolha: ‹documento›").

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

## Decisões

As decisões estão com a razão e as alternativas descartadas em [research.md](research.md). O resumo:

- **D-001** — com dois ou mais escolhidos, todo botão de enviar envia todos, e diz isso.
- **D-002** — um envio por documento, em sequência, e não uma requisição com todos.
- **D-003** — nada se envia ao escolher o arquivo.
- **D-004** — a inscrição fica fora, registrada como achado.
- **D-005** — sem script, uma frase, e não um formulário único.

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
- Qualquer mudança na gestão, na conferência ou na trilha.
