# Feature Specification: O limite do cadastro de reserva lido do corte

**Feature Branch**: `claude/reserve-limit-enforcement-a5f079`, sobre a `main` em `84cbeeb5`

**Created**: 2026-11-13

**Status**: Especificada e implementada em 13/11/2026, sem PR. As quatro decisões de produto e o número
da spec foram escolhidos pelo usuário no mesmo dia (ver *Clarifications*). Pendente: o SC-2304,
humano.

**Input**: o item *"O limite do cadastro de reserva não é aplicado"* da seção "O que ainda precisa
evoluir" da Visão do Sistema (`docs/visao-sistema/index.html`, reescrita em 13/11 no #531), e a
segunda pergunta da DP-05 (`doc/decisoes-pendentes-da-consolidacao.md`), que a `097` deixou fora de
propósito: *"Semântica do limite da reserva e sua relação com o alvo do corte"*.

> **Faixa de identificadores.** Esta spec abre em **FR-6929**, **SC-2298** e **UX-725**. O teto
> medido em 13/11/2026, na `main` e nas worktrees locais, era o requisito seis mil novecentos e vinte
> e oito, o critério dois mil duzentos e noventa e sete e o requisito de experiência setecentos e
> vinte e quatro, todos da `161`. A pasta `161` é a última tomada, e não havia PR aberto. As decisões
> reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-2474 da `097`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

O Perfil declara o cadastro de reserva de três jeitos: não há, limitado, ou ilimitado. Quando é
limitado, a Etapa Perfis pede um número, e o documento imprime *"cadastro de reserva de até seis
classificados por Perfil"*. O portal, a Revisão, o relatório do Edital, a visão institucional e o
assistente repetem esse número.

**Nenhuma regra o lê.** Quem a ordem alcança é decidido pelo **corte** do marco que convoca: o alvo,
o excedente e se o Edital admite continuação. É o corte que a faixa calcula (`014`), que a ocupação
apura (`016`), que a convocação respeita e que a vaga acrescida depois da publicação alcança
(`097`). O número do cadastro e o corte são **duas declarações da mesma norma**, e nada as confronta.

O documento já se contradiz. Um Perfil só de cadastro de reserva, limitado em 6, com corte fixo de
10 e continuação admitida, sai assim, conferido em 13/11 na função que compõe o texto:

> *Seguem no processo os 10 (dez) primeiros classificados. […] Depois, poderão ser chamados outros
> candidatos, além desses, seguindo a mesma ordem.* — e, no mesmo documento, *cadastro de reserva de
> até 6 (seis) classificados por Perfil*.

São três respostas para "quantos podem ser chamados": dez, até seis, e sem fim. E a frase que
explicaria como suplentes e cadastro se relacionam é omitida justamente quando há cadastro, porque a
pergunta estava pendente na DP-05.

A própria demonstração tem o defeito: o Perfil do `seed_demo` declara *limitado em 6*, e o corte
dele (alvo fixo de 2 e excedente de 1, sem continuação, aplicados em cada uma das duas listas, que
têm 1 vaga cada) alcança **dois** classificados além da vaga, em cada lista.

**Nos Editais reais, o número do cadastro é o do excedente do corte.** Nenhum Edital da amostra em
`~/Downloads` publica cadastro de reserva limitado por número. Os só de reserva (140/2025, 173/2025,
89/2026, 90/2026, 69/2026, 76/2026) não dão número; os números que aparecem são de suplentes: *"até
30 (trinta) suplentes para chamada imediata"* (77/2026), *"para cada código de vaga, […] até 20
(vinte) suplentes"* (57/2026), 15 no 28/2026. É exatamente o excedente que a `014` modelou, a partir
desses mesmos três Editais.

**Por isso o corte é a fonte única**, e o número do cadastro passa a ser lido dele. Nenhum motor
muda: o corte, a ocupação, a convocação e o acréscimo já executam esse número. Muda quem o declara e
o que o documento diz.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- o número do cadastro limitado, derivado do corte do marco que convoca, por lista de concorrência;
- a coerência entre a espécie do cadastro e a continuação do corte, recusada na publicação;
- o documento, que deixa de se contradizer e passa a explicar suplentes e cadastro;
- todas as telas que mostram o número, por uma regra só;
- os Editais já publicados com número digitado, que não são reavaliados e ganham uma frase honesta na
  ocupação e na convocação;
- a Retificação, que muda o número pelo corte e não pelo campo.

**Fica fora** (ver *Out of Scope*): um teto executado pelo número do cadastro, a validade e a
prorrogação, a ordem de chamada entre modalidades, os Editais de bolsista e o suplente por
multiplicador ("até o triplo das vagas").

---

## Clarifications

### Session 2026-11-13 (decisões do usuário)

- Q: Qual é a fonte do número do cadastro limitado: o corte (A), o próprio número como teto
  executado (B), ou os dois, conferidos na publicação (C)? → A: **o corte** (`D-001`). O número deixa
  de ser digitado e passa a ser derivado do corte do marco que convoca.
- Q: Nos Editais já publicados com o número digitado, que não vai ser aplicado, o que acontece? →
  A: **a ocupação e a convocação avisam** (`D-005`). Nada é reavaliado nem republicado; nas telas da
  ocupação e da convocação daqueles Perfis, uma frase diz que o número publicado não é aplicado pelo
  sistema e qual é o alcance do corte.
- Q: Num Perfil com Modalidade, o corte vale por lista. Como o número derivado aparece? → A: **por
  lista** (`D-004`). O documento diz "em cada lista de concorrência", ou o número de cada lista quando
  eles diferem.
- Q: "Limitado" exige o marco que convoca sem continuação. "Ilimitado" deve exigir o inverso? → A:
  **sim, exigir** (`D-003`). A publicação recusa o par incoerente.
- Q: Qual o número da spec? → A: **162**.

---

## User Scenarios & Testing *(mandatory)*

O ator é quem elabora o Edital (o Setor de Seleção do Cefor, na equipe inicial) e quem o conduz
depois de publicado: a presidência da comissão, que apura e convoca. O candidato lê o documento e o
portal.

### User Story 1 — Quem elabora declara o cadastro limitado, e o número vem do corte (Priority: P1)

Na Etapa Perfis, quem elabora escolhe "Cadastro reserva limitado". A tela não pede mais o número: ela
diz que o número vem do corte do marco que convoca e, se o corte já está declarado, mostra o número
que ele produz em cada lista. Na Revisão, o número aparece, e o par incoerente — limitado com
continuação admitida, ilimitado sem continuação, limitado sem corte ou com número zero — impede a
publicação com uma frase que diz o que mudar.

**Why this priority**: é a mudança que fecha as duas fontes. Sem ela, as outras histórias continuam
mostrando um número que ninguém aplica.

**Independent Test**: num rascunho com um Perfil de 2 vagas, cadastro limitado e marco que convoca
com alvo do quadro, excedente de 3 e sem continuação, a Etapa Perfis não oferece campo de número, e a
Revisão diz "até 3 classificados". Trocando a continuação para admitida, a Revisão recusa a
publicação.

**Acceptance Scenarios**:

1. **Given** um Perfil com cadastro limitado e marco que convoca com alvo do quadro, excedente de 3 e
   sem continuação, **When** a Revisão é aberta, **Then** o cadastro aparece como "até 3 classificados"
   e não há impedimento.
2. **Given** um Perfil só de reserva (0 vaga) com cadastro limitado e alvo fixo de 4 com excedente de
   2, sem continuação, **When** a Revisão é aberta, **Then** o cadastro aparece como "até 6
   classificados".
3. **Given** um Perfil com cadastro limitado e marco que convoca com continuação admitida, **When** a
   publicação é pedida, **Then** ela é recusada com uma frase que diz que cadastro limitado exige corte
   sem continuação, e que nomeia o marco.
4. **Given** um Perfil com cadastro ilimitado e marco que convoca com corte sem continuação, **When**
   a publicação é pedida, **Then** ela é recusada com uma frase que diz que cadastro ilimitado exige
   continuação admitida.
5. **Given** um Perfil com cadastro limitado cujo marco que convoca não declara corte, **When** a
   publicação é pedida, **Then** ela é recusada: sem corte não há de onde o número saia.
6. **Given** um Perfil com 2 vagas, cadastro limitado e alvo fixo de 2 sem excedente, **When** a
   publicação é pedida, **Then** ela é recusada: o cadastro limitado a ninguém não é cadastro.

---

### User Story 2 — O documento não se contradiz (Priority: P1)

O candidato lê o Edital e encontra uma resposta só para "quantos podem ser chamados". O número do
cadastro é o que o corte alcança além das vagas; a explicação de como suplentes e cadastro se
relacionam, hoje omitida quando há cadastro, passa a sair. No Perfil só de reserva, a frase do corte
deixa de dizer "Seguem no processo", porque não há vaga para a qual seguir: ela diz quem compõe o
cadastro.

**Why this priority**: o documento é o ato legal. Uma contradição nele é defeito normativo, e não de
polimento.

**Independent Test**: compor o documento de um Edital com um Perfil só de reserva limitado (alvo fixo
de 6, sem continuação) e um Perfil com vagas e cadastro limitado (alvo do quadro, excedente de 3), e
ler: cada Perfil diz um número só, e nenhum Perfil só de reserva diz "Seguem no processo".

**Acceptance Scenarios**:

1. **Given** um Perfil com vagas, cadastro limitado e alvo do quadro com excedente de 3, **When** o
   documento é composto, **Then** a frase do corte diz os primeiros em número igual ao das vagas "mais
   3 (três) suplentes", o cadastro diz "até 3 (três) classificados", e uma frase diz que os suplentes
   formam o cadastro de reserva e são chamados, na ordem, para as vagas não preenchidas.
2. **Given** um Perfil só de reserva com cadastro limitado e alvo fixo de 6 sem continuação, **When**
   o documento é composto, **Then** a frase do corte diz que os 6 (seis) primeiros classificados
   compõem o cadastro de reserva, e não "Seguem no processo".
3. **Given** um Perfil só de reserva com cadastro ilimitado e alvo fixo de 10 com continuação
   admitida, **When** o documento é composto, **Then** a frase diz que os classificados compõem o
   cadastro de reserva, sem limite, e que os 10 primeiros são os da primeira chamada, seguidos, na
   ordem, pelos demais.
4. **Given** um Perfil com ampla, PcD e PPI, cadastro limitado e alvo do quadro com excedente de 2,
   **When** o documento é composto, **Then** o cadastro diz "até 2 (dois) classificados em cada lista
   de concorrência".

---

### User Story 3 — Todas as telas dizem o mesmo número (Priority: P2)

O portal, a Revisão, o relatório do Edital, a visão institucional, a tabela da etapa e o assistente
mostram o número derivado, pela mesma regra que o documento usa. Ninguém lê o número de um lugar e
encontra outro em outro.

**Why this priority**: as telas repetem o número hoje; derivá-lo só no documento abriria a terceira
fonte.

**Independent Test**: para o mesmo Perfil, comparar o número que o documento, o portal, a Revisão, o
relatório, a visão institucional e o assistente dizem; os seis são iguais.

**Acceptance Scenarios**:

1. **Given** um Edital publicado depois desta feature, com Perfil só de reserva limitado cujo corte
   alcança 6, **When** o candidato abre a página do Perfil no portal, **Then** ela diz "até 6
   classificados, para convocação futura".
2. **Given** o mesmo Edital, **When** alguém pergunta ao assistente quantas pessoas o cadastro de
   reserva comporta, **Then** a resposta diz 6 e cita o mesmo trecho que o documento.
3. **Given** um Perfil com Modalidade cujo número difere entre listas, **When** o relatório do Edital
   é aberto, **Then** ele mostra o número de cada lista, e não um número só.

---

### User Story 4 — O Edital já publicado não é reavaliado, e a ocupação não finge (Priority: P2)

Um Edital publicado antes desta feature, com cadastro "limitado em 6" digitado, continua dizendo o
que disse. O documento e o portal mostram o número publicado, que é fato do Edital. Na ocupação e na
convocação daquele Perfil, uma frase diz que o número publicado não é aplicado pelo sistema, e qual é
o alcance do corte.

**Why this priority**: a publicação é imutável; o que se pode corrigir é o que a condução sabe.

**Independent Test**: com um Edital publicado com número digitado, abrir a ocupação e a convocação do
Perfil: a frase aparece, com o número publicado e o alcance do corte; o documento e o portal não
mudaram.

**Acceptance Scenarios**:

1. **Given** um Edital publicado antes desta feature, Perfil limitado em 6 digitado e corte com
   alcance de 3 sem continuação, **When** a presidência abre a ocupação do recorte, **Then** a tela diz
   que o Edital publicou cadastro limitado em 6, que o sistema não aplica esse número e que a
   convocação alcança quem o corte alcança — até 3 classificados além das vagas.
2. **Given** o mesmo Perfil com continuação admitida, **When** a presidência abre a convocação,
   **Then** a frase diz que o alcance cresce pela faixa seguinte do corte, sem dar número.
3. **Given** qualquer Edital publicado antes desta feature, **When** a feature entra em produção,
   **Then** nenhum Edital é reavaliado, republicado ou recebe advertência nova na Revisão.

---

### User Story 5 — A Retificação muda o número pelo corte (Priority: P3)

Num Edital publicado depois desta feature, a Retificação não oferece mais o campo "Limite do Cadastro
Reserva": o número muda quando se retificam o alvo ou o excedente do corte, e o quadro de alterações
diz o número de antes e o de depois. Num Edital publicado antes, o campo continua retificável como
hoje.

**Why this priority**: a Retificação do alvo e do excedente já existe; o que muda é o efeito que ela
mostra e uma recusa nova.

**Independent Test**: retificar o excedente de 3 para 5 num Perfil limitado: o quadro de alterações
diz "até 3" → "até 5"; retificar para 0 num Perfil em que isso zera o cadastro é recusado.

**Acceptance Scenarios**:

1. **Given** um Edital publicado depois desta feature, Perfil limitado com excedente de 3, **When** a
   Retificação muda o excedente para 5, **Then** o quadro de alterações e o documento retificado dizem
   o cadastro "até 5".
2. **Given** o mesmo Perfil, **When** a Retificação leva o número derivado a zero, **Then** ela é
   recusada com a mesma frase da publicação.
3. **Given** um Edital publicado antes desta feature, **When** a Retificação muda o campo do limite,
   **Then** ela é aceita como hoje, e a regra de coerência nova não a bloqueia.

---

### Edge Cases

Os que mudam comportamento viraram requisito (`FR-6938`, `FR-6939`, `FR-6940`, `FR-6948`,
`FR-6949`); os demais são consequência do que já existe.

- **Empate que atravessa a última posição, com o Edital admitindo excedente.** A faixa pode passar do
  número; o documento já diz que "passam todos os empatados". A frase do cadastro não pode afirmar o
  contrário: com esse desfecho, ela diz que os empatados na última posição também entram
  (`FR-6938`).
- **Mais de um marco que convoca no mesmo Perfil.** Não há caso conhecido. Se os números derivados
  coincidirem em cada lista, vale o número; se divergirem, a publicação recusa, porque o documento não
  teria um número para dizer (`FR-6939`).
- **Alvo fixo menor que as vagas da lista.** O número derivado é negativo; é o mesmo caso do
  cadastro limitado a ninguém, e é recusado (`FR-6936`).
- **Rascunho que ainda guarda um número digitado.** Ele não entra no conteúdo publicado. A Revisão diz
  o número digitado e o derivado quando diferem, para que quem elabora veja a troca antes de publicar
  (`FR-6940`).
- **Gravação de rascunho que traz o número**, pela tela antiga em cache ou pelo assistente de
  elaboração: o número não é gravado, e a resposta diz que ele vem do corte (`FR-6931`).
- **Cadastro ilimitado sem corte no marco que convoca.** Não há contradição no documento: nada diz
  quantos. Fica como hoje, fora desta feature.
- **Cadastro inexistente com suplentes e continuação** — o 77/2026: suplentes "para chamada imediata"
  e chamada "até que se preencha o número total de vagas", sem cadastro de reserva declarado. É
  legítimo, e a regra de coerência não o alcança (`D-006`).
- **Edital publicado antes, retificado depois.** Continua legado: o número digitado e a frase da
  ocupação permanecem, e a Retificação não é recusada pela regra nova (`FR-6948`).
- **Edital legado cujo número digitado coincide com o alcance do corte.** A frase da ocupação aparece
  igual: ela diz que o sistema não aplica o número, e isso continua verdade (`FR-6949`).

---

## Requirements *(mandatory)*

### Functional Requirements

#### O número vem do corte

- **FR-6929**: O número do cadastro de reserva limitado MUST ser derivado do corte do marco que
  convoca do Perfil — o marco que não é intermediário, na definição da FR-4531 da `133` —, por lista
  de concorrência: o alcance da faixa sem continuação menos as vagas imediatas da linha daquela lista.
  Com alvo do quadro, o número é o excedente; com alvo fixo, é o alvo mais o excedente menos as vagas
  da linha.
- **FR-6930**: A derivação MUST ser uma regra só, lida pelo documento, pelo portal, pela Revisão, pelo
  relatório do Edital, pela visão institucional, pela tabela da etapa, pelo quadro de alterações da
  Retificação e pelo assistente. Nenhum desses lugares MUST calcular o número por conta própria.
- **FR-6931**: A Etapa Perfis MUST NOT pedir número para o cadastro limitado, e a gravação de
  rascunho MUST NOT gravar número enviado para ele, por qualquer caminho; a resposta MUST dizer que o
  número vem do corte do marco que convoca.
- **FR-6932**: Com cadastro limitado escolhido, a Etapa Perfis MUST dizer de onde o número vem e,
  quando o corte do marco que convoca já está declarado, MUST mostrar o número que ele produz em cada
  lista.

#### A coerência entre a espécie e o corte

- **FR-6933**: A publicação MUST ser recusada quando um Perfil com cadastro limitado tiver o marco
  que convoca com continuação admitida.
- **FR-6934**: A publicação MUST ser recusada quando um Perfil com cadastro ilimitado tiver o marco
  que convoca com corte sem continuação admitida.
- **FR-6935**: A publicação MUST ser recusada quando um Perfil com cadastro limitado tiver o marco
  que convoca sem regra de corte.
- **FR-6936**: A publicação MUST ser recusada quando o número derivado de alguma lista de um Perfil
  com cadastro limitado for zero ou negativo.
- **FR-6937**: Cada recusa das FR-6933 a FR-6936 MUST nomear o Perfil e o marco, dizer o que está
  incoerente e o que mudar, e aparecer na Revisão antes do pedido de publicação, como os demais
  impedimentos.
- **FR-6938**: Quando o marco que convoca admite excedente por empate na última posição, a frase do
  cadastro limitado MUST dizer que os empatados nessa posição também entram.
- **FR-6939**: A publicação MUST ser recusada quando o Perfil tiver mais de um marco que convoca com
  corte e os números derivados divergirem em alguma lista.
- **FR-6940**: Um rascunho que guarda número digitado para o cadastro limitado MUST NOT publicá-lo; a
  Revisão MUST mostrar uma advertência com o número digitado e o derivado quando eles diferem.

#### O documento

- **FR-6941**: O documento MUST imprimir, para o cadastro limitado, só o número derivado, com "em
  cada lista de concorrência" quando o Perfil tem Modalidade e o número é o mesmo em todas, ou o
  número de cada lista quando eles diferem.
- **FR-6942**: A explicação de como suplentes e cadastro se relacionam MUST sair nos Perfis com
  cadastro limitado ou ilimitado e vagas imediatas: os suplentes formam o cadastro de reserva e são
  chamados, na ordem, para as vagas não preenchidas. A omissão que a FR-1362 da `069` fazia por causa
  da pergunta pendente MUST deixar de valer para esses Perfis, e a explicação que já existe para os
  Perfis sem cadastro MUST sair também quando outro Perfil do mesmo Edital tem cadastro.
- **FR-6943**: No Perfil só de cadastro de reserva, a frase do corte do marco que convoca MUST NOT
  começar por "Seguem no processo" nem por "Passam para"; ela MUST começar dizendo que os
  classificados alcançados compõem o cadastro de reserva — com o número, se limitado; sem limite, e
  com a primeira chamada e a continuação, se ilimitado. Quando o corte governa uma Etapa, a frase MUST
  dizer também que esses classificados participam dela.
- **FR-6944**: O documento de um Edital publicado antes desta feature MUST NOT mudar: a recomposição
  dele, quando houver, MUST reproduzir o número digitado que ele publicou, e a unidade do corte do
  Perfil legado MUST sair como saía — sem a abertura da FR-6943 e sem a frase da FR-6942. Nesse Edital, todos os
  lugares da FR-6930 MUST mostrar o número publicado, que é fato do Edital, e não o derivado.

#### As telas

- **FR-6945**: O portal MUST mostrar o número derivado na oferta do Perfil e na frase do cadastro do
  acompanhamento; num Edital publicado antes desta feature, o número publicado.
- **FR-6946**: O assistente de dúvidas MUST responder pelo número derivado, citando o trecho do
  documento que o diz; num Edital publicado antes desta feature, pelo número publicado.

#### Os Editais já publicados

- **FR-6947**: Nas telas da ocupação e da convocação de um Perfil publicado com número digitado, uma
  frase MUST dizer que o Edital publicou o cadastro limitado naquele número, que o sistema não o
  aplica, e qual é o alcance do corte: o número, quando não há continuação; que ele cresce pela faixa
  seguinte, quando há.
- **FR-6948**: Editais publicados antes desta feature MUST NOT ser reavaliados, republicados nem
  recebidos com advertência nova; a Retificação deles MUST NOT ser recusada pelas FR-6933 a FR-6939, e
  o campo do limite MUST continuar retificável neles.
- **FR-6949**: A frase da FR-6947 MUST aparecer também quando o número publicado coincide com o
  alcance do corte.

#### A Retificação

- **FR-6950**: Num Edital publicado depois desta feature, a Retificação MUST NOT oferecer o campo do
  limite; o quadro de alterações MUST mostrar o número derivado de antes e o de depois quando a
  Retificação do alvo ou do excedente o mudar.
- **FR-6951**: A Retificação de um Edital publicado depois desta feature MUST ser recusada quando
  levar o número derivado de alguma lista a zero ou negativo, com a frase da FR-6936.

### Requisitos de experiência

- **UX-725**: A frase da Etapa Perfis sobre a origem do número MUST ser um único elemento de ajuda,
  sem link para outra etapa; o número de cada lista, quando há, aparece numa lista curta, e não
  em tabela.
- **UX-726**: As recusas de coerência MUST usar o vocabulário do documento ("cadastro de reserva",
  "continuação", "corte"), e não os nomes técnicos das espécies.
- **UX-727**: A frase da ocupação e da convocação do Edital legado MUST ser nota, e não alerta: ela
  informa um limite da condução, e não pede ação.

### Key Entities

- **Perfil de Vaga**: já existe. A espécie do cadastro (não há, limitado, ilimitado) continua
  declarada e não retificável. O número digitado deixa de ser declarado em Edital novo e continua
  existindo nos publicados antes desta feature.
- **Regra de corte do marco que convoca**: já existe. Alvo, excedente, desfecho do empate e
  continuação; passa a ser a fonte do número do cadastro.
- **Número do cadastro de reserva**: não é dado gravado em Edital novo; é derivado, por lista, da
  regra de corte e do quadro de vagas da versão.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2298**: Em todo Edital publicado depois desta feature, para todo Perfil com cadastro limitado,
  o número que o documento, o portal, a Revisão, o relatório, a visão institucional e o assistente
  dizem é o mesmo, e é igual ao alcance do corte menos as vagas, em cada lista — 100% dos Perfis limitados
  das fixtures conferidos.
- **SC-2299**: Nenhum documento composto depois desta feature começa a frase do corte do marco que
  convoca de um Perfil só de cadastro de reserva por "Seguem no processo" ou "Passam para".
- **SC-2300**: Os seis pares incoerentes (limitado com continuação, ilimitado sem continuação,
  limitado sem corte, limitado com número zero, limitado com número negativo, marcos que convocam com
  números divergentes) são recusados na publicação em 100% dos casos, e nenhum par coerente é recusado.
- **SC-2301**: Nenhum Edital publicado antes desta feature muda de documento, é republicado ou recebe
  advertência nova; em 100% dos Perfis deles com número digitado, a ocupação e a convocação mostram a
  frase da FR-6947.
- **SC-2302**: O documento composto do Perfil do `seed_demo` e do Perfil só de reserva do exemplo de
  13/11 diz um número só para "quantos podem ser chamados".
- **SC-2303**: A Retificação do excedente ou do alvo de um Perfil limitado publicado depois desta
  feature muda o número em todos os lugares do SC-2298, e o quadro de alterações o mostra.
- **SC-2304**: *(humano)* Uma pessoa da equipe que não participou desta feature lê o documento de um
  Edital com um Perfil só de reserva limitado e um Perfil com vagas e cadastro, e responde, sem ajuda,
  quantos podem ser chamados em cada um.

---

## Assumptions

- **O marco que convoca é o não intermediário**, como a `133` o definiu; a definição não muda aqui.
- **Os motores não mudam.** O corte, a faixa, a continuação sem teto (a FR-204 da `014`), a ocupação,
  a convocação e a vaga acrescida da `097` continuam como estão. O que esta spec faz é tirar a segunda
  fonte e alinhar o texto ao que eles já executam.
- **"Antes desta feature" é um fato do Perfil publicado**: a versão publicada traz número digitado
  para o cadastro limitado. Não depende de data.
- **A advertência da FR-2474 da `097`** (o alcance da faixa no Perfil só de reserva) continua; com o
  cadastro limitado, o alcance que ela diz é o mesmo número desta spec.
- **O `seed_demo` e as fixtures mudam junto.** Cerca de cinquenta arquivos de teste citam o número
  digitado ou a espécie limitada; a regra impeditiva nova os alcança, e a correção é nas fixtures.

## Out of Scope

- **Um teto executado pelo número do cadastro** (a opção B): a continuação do corte e o acréscimo
  recusarem além das vagas mais o número (`D-007`).
- A validade do Edital, a prorrogação e o suplente convocável para a turma seguinte (P-3).
- A ordem de chamada entre modalidades sem quadro quantitativo (P-1) e o acréscimo em Modalidade
  reservada, que a `097` deixou fora.
- Os Editais de bolsista de cadastro de reserva (140/2025, 173/2025, 89/2026, 90/2026), que a `097`
  remeteu a spec própria.
- O suplente por multiplicador das vagas, *"até o triplo do número de vagas"* (46/2026): nem o corte
  nem o cadastro o modelam hoje.
- Cadastro ilimitado sem corte no marco que convoca.

---

## Decisões

### D-001 — O corte é a fonte única do número

Decisão do usuário em 13/11/2026, entre três opções: o corte como fonte (A), o número do cadastro como
teto executado (B), ou os dois conferidos na publicação (C). **A.** Pesou a favor: os números
"limitados" dos Editais reais são de suplentes, que o excedente do corte já executa; o Princípio II da
Constituição pede uma fonte só; e nenhum motor muda. A C deixaria duas fontes, e a B construiria um
segundo mecanismo para uma norma que nenhum Edital da amostra escreve.

### D-002 — O número é o que o corte alcança além das vagas, por lista

O cadastro é de quem a ordem alcança e as vagas não absorvem. Por isso o número é o alcance da faixa
sem continuação menos as vagas da linha, e não o alcance inteiro: "até 3 classificados" num Perfil de
2 vagas com 5 alcançados. No Perfil só de reserva, as vagas são zero, e o número é o alcance. É a
mesma conta que a FR-2474 da `097` já faz para dizer quantos a faixa alcança.

### D-003 — Limitado exige corte sem continuação; ilimitado, com continuação

Decisão do usuário em 13/11/2026. Com continuação admitida, a faixa cresce sem teto, e "até N" seria
falso; sem continuação, a faixa para, e "sem limite" seria falso. A espécie e a continuação não se
retificam depois da publicação (`mutabilidade.py`), e por isso a coerência, conferida na publicação,
vale pela vida do Edital. A recusa é impeditiva porque o par incoerente é contradição no ato legal.

### D-004 — Com Modalidade, o número vale por lista

Decisão do usuário em 13/11/2026. O corte é aplicado em cada lista (a FR-4553 da `133`), e o número
derivado é o de cada lista. O 57/2026 e o 28/2026 escrevem "para cada código de vaga". O documento diz
"em cada lista de concorrência" quando o número é o mesmo em todas, e o de cada lista quando difere.
Um número para o Perfil inteiro exigiria contar pessoas entre listas de concorrência concomitante, e
seria a ordem de chamada entre modalidades, que está fora.

### D-005 — Os Editais legados ganham uma nota na condução

Decisão do usuário em 13/11/2026. A publicação é imutável: o documento e o portal continuam dizendo o
número publicado. O que se corrige é o que a condução sabe: na ocupação e na convocação, a nota diz
que o número não é aplicado e qual é o alcance do corte. Ficar sem nota repetiria o defeito — "aceita,
publica e não executa" — em silêncio.

### D-006 — A espécie continua declarada

Derivar também a espécie do corte (sem continuação = limitado; com continuação = ilimitado) mudaria
o 77/2026, que tem suplentes e continuação e não declara cadastro de reserva: o documento passaria a
dizer que ele tem cadastro ilimitado. A espécie é norma do Edital, e a coerência só a confronta com o
corte quando ela afirma cadastro.

### D-007 — Nenhum teto novo é executado

O número derivado já é o que o corte executa quando não há continuação, e com continuação a espécie é
ilimitada por coerência. Um teto executado a partir do número só faria sentido com duas fontes, que é
o que esta spec elimina. A opção B fica fora.
