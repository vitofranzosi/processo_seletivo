# Feature Specification: A composição das telas da inscrição no portal

**Feature Branch**: `claude/177-composicao-das-telas-da-inscricao`, nascida da `main` em `399f90be`
(o merge do #574, da `176`)

**Created**: 2026-11-15

**Status**: Especificada, planejada e implementada em 15/11, no mesmo PR, sem merge. A validação com a
equipe não aconteceu, como a das mudanças da `172` e da `175`. O merge é do usuário.

**Input**: em 15/11 o usuário abriu, a 1440 px, as três telas da inscrição de uma candidata (a
Candidata 2, do Processo 1659166) e descreveu o que viu — *Por que esta feature existe*, abaixo. Pediu
a composição da jornada do candidato do estudo de design system de 14/11 nas três: **Minhas
inscrições**, **Minha inscrição** (a conferência, "O que você informou") e **Acompanhar**.

> **Faixa de identificadores.** Esta spec abre em **FR-8100**, **SC-2800** e **UX-950**, e reserva até
> o requisito oito mil cento e quarenta e nove, o critério dois mil oitocentos e dezenove e o requisito
> de experiência novecentos e sessenta e nove. Os tetos medidos em 15/11/2026, na `main` e em todas as
> worktrees, eram o requisito oito mil e cinquenta e quatro, o critério dois mil setecentos e cinquenta
> e nove e o requisito de experiência novecentos e vinte e quatro. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-7857 da `174`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> Os achados (`E7`, `E12`), as composições e o roadmap (`P2.3`) são do estudo de design system, em
> `doc/auditoria-design-system-2026-11-14/`, e se citam por extenso.

---

## Por que esta feature existe

A `174` pôs a composição centrada da jornada do candidato nas telas da verificação por vídeo, e a
`175` levou os padrões do piloto a toda a gestão. As três telas por onde o candidato volta depois de
se inscrever ficaram como estavam, e o estudo já as apontava (achado `E7`: "Minhas inscrições"
estreita e encostada à esquerda). O que o usuário viu a 1440 px:

1. **Minhas inscrições.** Um cartão estreito encostado à esquerda, e a página vazia à direita. O título
   do cartão é o nome do Perfil — na seleção do exemplo, literalmente "Perfil" —, e não o Processo. O
   cartão não diz a situação de modo que se veja de longe nem o prazo. O botão "Acompanhar" ocupa o
   cartão inteiro. O subtítulo da página é um link solto, "Acesso à conta".
2. **Minha inscrição.** Nove pares de rótulo e valor empilhados numa coluna estreita e comprida, com a
   metade direita da tela vazia.
3. **Acompanhar.** Três larguras na mesma tela: "Sua situação" para em cerca de 68 caracteres, e "Sua
   participação" e "Cronograma do processo" vão até a borda da página. O subtítulo é só "Processo
   1659166", que não diz qual das inscrições da pessoa é esta. E há dois botões cheios: a ação do bloco
   da situação e "Ver o que enviei", no fim.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora, e por quê |
|---|---|
| A composição das três telas: a coluna centrada, o começo da tela, a largura dos blocos, a ação principal | o conteúdo de cada bloco, que é das features que o decidiram (`010`, `059`, `063`, `118`, `167`) |
| O cartão de inscrição de "Minhas inscrições": o que ele diz e em que ordem | a derivação da situação e da ação, que continua a de hoje (`010`, `059`, `171`) |
| A grade de rótulo e valor de "O que você informou" | os campos e os valores, que são os do comprovante (`010`) |
| A posição do bloco "Sua situação" no Acompanhamento | o que está **dentro** dele: o selo, o prazo do passo e a ação do passo são da `174`; a ordem situação, por quê e o que fazer é da `063`; o prazo da convocação é da `118` |
| As capturas antes e depois nas cinco larguras | a validação com a equipe e com candidatos |
| — | "Recorrer" (o resto do `E7`) e o Requerimento de Matrícula (`E12`): são as próximas telas da `P2.3`, e ficam como registro (A-1) |

**Nada muda no que as telas sabem.** As rotas, as views, as consultas e as frases de situação continuam
as de hoje. O único dado novo é o prazo no cartão da lista, e ele sai do que a lista já lê (FR-8106).

### Como esta spec se relaciona com a `174`

A `174` decidiu a composição centrada da jornada do candidato **para as telas da verificação** (a
FR-7850 da `174`) e, no Acompanhamento, só o que diz respeito ao passo da Etapa restrita: o selo em
pílula em todas as situações provisórias (a FR-7856 da `174`), o prazo do passo em linha própria (a
FR-7857 da `174`) e o rótulo da ação do passo (a FR-7858 da `174`). Ela deixou o resto do
Acompanhamento para a `P2.3` do estudo, e esta spec é essa parte.

| Assunto | De quem é |
|---|---|
| A coluna centrada de 44rem e o botão de 48 px | da `174` (a FR-7850 e a FR-7851 da `174`); esta spec os **estende** às três telas, sem mudar a medida |
| O selo da situação, o prazo do passo e a ação do passo, dentro de "Sua situação" | da `174`; esta spec não os toca |
| A ordem dentro de "Sua situação" e as frases dela | da `063` e da `118`; esta spec não as toca |
| O lugar de "Sua situação" na tela, a largura dele e a dos blocos seguintes | desta spec |
| O começo das três telas (onde estou, título, identificação) | desta spec |
| O cartão de "Minhas inscrições" e a grade de "O que você informou" | desta spec |

Nenhuma decisão da `174` é revista. Onde as duas se tocam — o prazo no começo da tela —, esta spec
declara que o prazo do Acompanhamento continua onde a `174` o pôs (FR-8111).

---

## Clarifications

### Session 2026-11-15 (restrições do pedido)

- Partir da `174` e não contradizê-la; declarar o que é de qual (seção acima).
- **O portal mantém a medida de leitura.** A migração da `175` foi só da gestão; no portal, o texto
  corrido continua em `--leitura` (68ch), e `test_o_texto_corrido_do_portal_tem_medida_propria`
  continua valendo (FR-8104).
- Os textos não mudam sem registro nesta spec (FR-8120). Nada de texto gerado pela folha de estilo,
  nem de estilo ou script no template: a política de conteúdo os recusa (FR-8121).
- Celular primeiro, conferido a 375, 768, 1280, 1440 e 1920 px, sem rolagem horizontal.
- Governança é do usuário: achado fora destas três telas vira registro.

Nenhuma pergunta ficou aberta: o pedido decidiu a direção, e os detalhes têm resposta no estudo ou no
que a `174` já fez. As escolhas de redação estão em *Decisões*, para o usuário revê-las no PR.

---

## User Scenarios & Testing *(mandatory)*

Os cenários usam uma candidata com uma inscrição enviada num Processo com Etapa restrita (como a
Candidata 2 do exemplo), e outra com três inscrições: uma enviada, uma em rascunho dentro do período e
uma com convocação aberta.

### User Story 1 — Achar a inscrição certa e o que fazer nela (Priority: P1)

A candidata entra no portal e cai em "Minhas inscrições". Em cada cartão ela lê de qual Processo é, o
Edital e o Perfil, em que pé está, até quando tem prazo, e qual é o próximo passo — e toca nele.

**Why this priority**: é a porta das outras duas telas, e é para ela que o e-mail de aviso manda a
pessoa (a `059` e a `171`).

**Independent Test**: "Minhas inscrições" com uma, três e nenhuma inscrição, a 375 e a 1440 px.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada, **When** a lista abre, **Then** o título do cartão é o nome do
   Processo, a linha seguinte diz o Edital e o Perfil, a situação aparece em selo, e a ação é
   "Acompanhar" (FR-8105, FR-8107).
2. **Given** um rascunho dentro do período com término, **When** a lista abre, **Then** o cartão diz
   "Prazo: até {data}, às {hora}" e a ação é "Continuar inscrição" (FR-8106).
3. **Given** a convocação aberta com vencimento, **When** a lista abre, **Then** o cartão diz
   "Convocação aberta", o prazo da convocação, a ação "Ver convocação" e, abaixo, o link
   "Acompanhar" (FR-8106, FR-8108).
4. **Given** a tela a 1440 px, **When** ela abre, **Then** os cartões ficam na coluna centrada, e o
   botão do cartão tem a largura do próprio texto, e não a do cartão (FR-8101, FR-8108).
5. **Given** a tela a 375 px, **When** ela abre, **Then** o botão do cartão ocupa a largura do cartão,
   com pelo menos 48 px de altura (FR-8108).

---

### User Story 2 — Saber em que pé está a inscrição (Priority: P1)

A candidata abre "Acompanhar". No topo ela vê de onde veio ("Minhas inscrições"), qual inscrição é
(Processo, Edital, Perfil) e, logo abaixo, a situação. Todos os blocos da tela têm a mesma largura.

**Why this priority**: é a tela a que a pessoa volta toda vez que espera um resultado.

**Independent Test**: o Acompanhamento da Candidata 2 (passo enviado, aguardando o resultado) e o de
uma inscrição com classificação divulgada e convocação, a 375, 768, 1280, 1440 e 1920 px.

**Acceptance Scenarios**:

1. **Given** o Acompanhamento a 1440 px, **When** ele abre, **Then** "Sua situação", os blocos de
   resultado, "Sua participação" e "Cronograma do processo" têm as mesmas bordas esquerda e direita,
   na coluna centrada (FR-8102, SC-2801).
2. **Given** o Acompanhamento, **When** ele abre, **Then** o começo diz "Minhas inscrições ›
   {Processo} · {Edital}", o título "Acompanhar" e "Perfil de Vaga: {nome}" (FR-8110).
3. **Given** o Acompanhamento com uma ação no bloco da situação, **When** ele abre, **Then** só ela é
   botão cheio; "Ver o que enviei" é secundário (FR-8103, FR-8113).

---

### User Story 3 — Conferir o que foi enviado (Priority: P2)

A candidata abre "Minha inscrição" para conferir o que informou. Na tela larga, cada rótulo fica ao
lado do valor; no celular, um sobre o outro. A ação principal é baixar o comprovante.

**Why this priority**: é a tela de conferência, que a pessoa abre menos, mas é a que mostra o que vale.

**Independent Test**: "Minha inscrição" com e sem documentos, a 375 e a 1440 px.

**Acceptance Scenarios**:

1. **Given** a tela a 1440 px, **When** ela abre, **Then** "O que você informou" é um bloco com cada
   rótulo à esquerda e o valor à direita, na mesma linha (FR-8115).
2. **Given** a tela a 375 px, **When** ela abre, **Then** cada rótulo fica acima do seu valor
   (FR-8115).
3. **Given** a tela, **When** ela abre, **Then** "Baixar comprovante" é o único botão cheio, e
   "Acompanhar esta inscrição" vem ao lado, como secundário (FR-8103, FR-8116).

---

### Edge Cases

- **A seleção sem versão vigente** (a lista não lê o conteúdo): o cartão diz "Inscrição" no título,
  como hoje, sem Edital, sem Perfil e sem prazo.
- **Perfil retirado por Retificação**: a identificação some no Acompanhamento ("Perfil de Vaga" não
  aparece), e o resto da tela não muda.
- **Nome de Processo longo** (mais de 120 caracteres): quebra em linhas no título do cartão e na trilha,
  sem transbordar a 320 px.
- **Rascunho fechado pelo prazo**: o cartão diz a frase de hoje ("Inscrições encerradas em …") e não
  mostra prazo, porque não há mais prazo a cumprir.
- **Período sem término declarado**: sem linha de prazo — o sistema não inventa prazo que o Edital não
  fixou (a regra do período da `009`).
- **Passo pendente e convocação aberta ao mesmo tempo**: o prazo do cartão é o da convocação, porque é
  ela que a ação principal abre.
- **Lista vazia**: o estado vazio de hoje ("Você ainda não possui inscrições." e "Ver processos
  seletivos"), na mesma coluna, e o convite "Já participou antes?" quando cabe.
- **Mensagem de retorno** (aviso depois de um gesto): logo abaixo do começo da tela, na largura da
  coluna.
- **Zoom de 400% ou celular de 320 px**: nada transborda, e a grade de rótulo e valor empilha.
- **Impressão de "Minha inscrição"**: não é comprovante (o comprovante tem rota própria, `010`); a tela
  imprime na largura do papel, como hoje.

## Requirements *(mandatory)*

### Functional Requirements

#### A composição das três telas

- **FR-8100**: As três telas — "Minhas inscrições", "Minha inscrição" e "Acompanhar" — DEVEM usar a
  composição centrada da jornada do candidato, a mesma das telas da verificação (a FR-7850 da `174`):
  uma coluna de no máximo 44rem, centrada na página.
- **FR-8101**: A 1280, 1440 e 1920 px, nenhuma das três DEVE deixar o conteúdo encostado à esquerda com
  a área à direita vazia: as margens dos dois lados da coluna DEVEM ser iguais.
- **FR-8102**: Todos os blocos de uma tela — cartões, painéis, listas de marcos, avisos e a mensagem de
  retorno — DEVEM ter as mesmas bordas esquerda e direita, as da coluna. Nenhum bloco DEVE parar na
  medida de leitura enquanto outro vai até a borda.
- **FR-8103**: Cada tela DEVE ter **uma** ação principal em botão cheio, com pelo menos 48 px de altura
  (`--controle-g`, da `174`), e as outras ações DEVEM ser secundárias ou links. "Minhas inscrições" é
  lista: nela a regra vale **por cartão**, como já é (a `010`).
- **FR-8104**: O texto corrido DEVE continuar na medida de leitura do portal (`--leitura`, 68ch) dentro
  da coluna: a medida é do texto, e não do bloco. A regra comum `main>p` do portal DEVE continuar.

#### "Minhas inscrições"

- **FR-8105**: O cartão de inscrição DEVE dizer, nesta ordem: o nome do Processo, como título e link
  para "Minha inscrição"; o Edital e o Perfil, numa linha ("Edital 01/2026 · Professor de
  Informática"); a situação; o prazo, quando houver; o protocolo; e a ação seguinte. Sem o nome do
  Processo, o título continua "Inscrição".
- **FR-8106**: O cartão DEVE mostrar "Prazo: até {data}, às {hora}" quando houver prazo correndo para a
  ação do cartão, nesta precedência:
  1. a convocação aberta com vencimento: o vencimento da convocação;
  2. o passo pendente de Etapa restrita com término: o término do período da Etapa (a `171`);
  3. o rascunho que ainda pode ser enviado, com término do período de inscrições: esse término.

  Sem nenhum deles, a linha não aparece. O prazo DEVE sair do que a lista já lê, sem consulta nova ao
  banco. O prazo da convocação aparece **com ou sem** providência pendente da pessoa, como no
  Acompanhamento (a FR-6208 da `154`; D-009).
- **FR-8107**: A situação do cartão DEVE aparecer em selo, com as frases de hoje: "✓ Inscrição
  enviada" em selo registrado; "Falta um passo seu: {Etapa}" e "Convocação aberta" em selo de atenção,
  com a seta; "Inscrição não enviada…" em selo neutro. A distinção entre eles DEVE ser visível sem cor:
  pela marca (✓ ou ➜) e pela palavra.
- **FR-8108**: A ação principal do cartão DEVE ter a largura do próprio rótulo na tela a partir de
  40rem, e a largura do cartão abaixo disso, sempre com pelo menos 48 px de altura. "Acompanhar", quando
  a convocação aberta toma a ação principal, continua link, abaixo dela (a `059`).
- **FR-8109**: O começo da tela DEVE ter o título "Minhas inscrições" e, na mesma faixa, à direita na tela
  larga e abaixo no celular, o link "Acesso à conta", que deixa de ser subtítulo.

#### O começo de "Minha inscrição" e de "Acompanhar"

- **FR-8110**: As duas telas DEVEM começar pelo mesmo molde: a trilha "Minhas inscrições ›
  {Processo} · Edital {número}/{ano}", com "Minhas inscrições" como link; o título da tela, como hoje;
  e a identificação "Perfil de Vaga: {nome}", no lugar do subtítulo que repetia o Processo. Sem Perfil,
  a identificação não aparece. O começo das duas DEVE sair da mesma versão, a vigente; "O que você
  informou" continua na versão aceita (D-008).
- **FR-8111**: O prazo do Acompanhamento DEVE continuar onde a `174` e a `118` o puseram — o do passo em
  linha própria dentro de "Sua situação" (a FR-7857 da `174`), o da convocação em "O que fazer" —, e
  "Sua situação" DEVE ser o primeiro bloco depois do começo da tela. Esta spec não repete o prazo no
  começo, para que a pessoa não leia duas datas.
- **FR-8112**: A mensagem de retorno de um gesto (`_mensagens`), quando houver, DEVE vir logo depois do
  começo da tela, antes do primeiro bloco.

#### "Acompanhar"

- **FR-8113**: "Ver o que enviei" DEVE passar de botão cheio a secundário. A ação principal da tela é a
  do bloco da situação, quando há; sem ela, a tela não tem botão cheio, e "Ver o que enviei" continua
  secundário.
- **FR-8114**: A ordem dos blocos NÃO DEVE mudar: situação, aviso de Retificação, horário, convocação,
  classificação por lista, resultado das etapas, recursos, participação e cronograma (a `063` e a
  `167`).

#### "Minha inscrição"

- **FR-8115**: "O que você informou" DEVE ser um bloco com borda, em grade de duas colunas a partir de
  40rem — rótulo à esquerda, valor à direita, uma linha por par, com separador entre as linhas — e
  empilhado abaixo disso, rótulo acima do valor.
- **FR-8116**: "Baixar comprovante" DEVE continuar a ação principal, e "Acompanhar esta inscrição" DEVE vir
  na mesma faixa, como secundário. "Ver dados de integridade" continua recolhido no fim (a `010`).
- **FR-8117**: A situação ("✓ Inscrição enviada") e o protocolo DEVEM vir juntos, numa faixa logo depois
  do começo da tela, com a situação em selo registrado, como no cartão da lista (FR-8107).

#### O que não muda

- **FR-8118**: Esta spec NÃO DEVE mudar as rotas, as views além do prazo do cartão e da identificação
  do Perfil, as frases de situação de `portal/situacao.py`, nem a ordem dentro de "Sua situação".
- **FR-8119**: As outras telas do portal NÃO DEVEM mudar. O que é novo na folha DEVE valer só sob a
  marca das três telas, e o que é comum ao portal (o `main`, o `.principal`, o `dl.campos`, o
  `.selecoes` da vitrine) NÃO DEVE mudar de regra.
- **FR-8120**: As únicas frases novas ou mudadas são as registradas em D-002 a D-005: o prazo do cartão,
  a trilha, a identificação do Perfil e a troca de título e linha do cartão. Nenhuma outra DEVE mudar.
- **FR-8121**: Nenhum template DEVE ter estilo ou script embutido, e nenhum texto DEVE ser gerado pela
  folha de estilo. Toda classe nova DEVE ter regra na folha do portal.

#### A verificação

- **FR-8122**: A entrega DEVE guardar as capturas das três telas antes e depois a 375, 768, 1280, 1440 e
  1920 px, e citá-las no PR.

### Requisitos de experiência

- **UX-950**: Celular primeiro: coluna única, botão de largura cheia abaixo de 40rem, nenhum par de
  rótulo e valor lado a lado em tela estreita.
- **UX-951**: A tela larga não é para ser preenchida: a coluna centrada deixa margens iguais, e o
  conteúdo fica no meio, onde o olhar vai (o critério das composições do estudo).
- **UX-952**: Nenhuma cor sozinha diz estado: o selo leva a marca (✓, ➜) e a palavra.
- **UX-953**: A trilha é navegação, e é anunciada como tal ("Onde você está"); a parte que não é link é a
  página atual.

### Key Entities

Nenhuma entidade nova. A spec lê o que as views já leem: a inscrição, o conteúdo publicado do Edital
(Processo, número, ano, Perfil, período), a convocação vigente e o passo da Etapa restrita.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2800**: A 1280, 1440 e 1920 px, nas três telas, a diferença entre as margens esquerda e direita
  da coluna é de no máximo 1 px.
- **SC-2801**: A partir de 768 px, nas três telas, todos os blocos de primeiro nível da coluna têm as
  mesmas bordas esquerda e direita, com no máximo 1 px de diferença.
- **SC-2802**: Nas cinco larguras (375, 768, 1280, 1440 e 1920 px) e a 320 px, nenhuma das três telas
  rola na horizontal.
- **SC-2803**: "Minha inscrição" e "Acompanhar" têm no máximo um botão cheio cada; em "Minhas
  inscrições", cada cartão tem exatamente um.
- **SC-2804**: Toda ação principal das três telas tem pelo menos 48 px de altura; a partir de 40rem, a
  do cartão é mais estreita que o cartão.
- **SC-2805**: A 1280 px, cada par de "O que você informou" ocupa uma linha só (rótulo e valor na mesma
  altura); a 375 px, o rótulo fica acima do valor.
- **SC-2806**: "Minhas inscrições" faz o mesmo número de consultas ao banco que antes desta spec, com
  uma, três e dez inscrições.
- **SC-2807**: Nenhum parágrafo das três telas passa da medida de leitura do portal.
- **SC-2808**: As capturas antes e depois das três telas, nas cinco larguras, estão no repositório e no
  PR.

## Assumptions

- A `174` (#568) e a `175` (#565) estão na `main` em `399f90be`, com a `.jornada`, o `--coluna` e o
  `--controle-g`.
- O prazo da convocação no cartão é o vencimento registrado da convocação vigente, o mesmo que o
  Acompanhamento mostra em "O que fazer" (a `118`); a frase do prazo não iniciado continua só no
  Acompanhamento e na convocação.
- O término do passo é o do período da Etapa restrita que a `171` já calcula para o cartão.
- A formatação do prazo é a da convocação (a FR-3747 da `118`: "até 12/11/2026, às 17h00"), uma só para
  os três casos no cartão.

## Out of Scope

- "Recorrer" (o resto do achado `E7`) e o Requerimento de Matrícula (`E12`).
- A convocação do candidato, a seleção pública, a vitrine, o comprovante e as telas do acesso.
- O conteúdo e a ordem de "Sua situação", e qualquer frase de `portal/situacao.py`.
- Tokens novos: a spec usa os da `172` e o `--controle-g` da `174`.
- A medida de leitura do portal: continua 68ch.

## Dependências

- **`174`** (#566 e #568, na `main`): a `.jornada`, o selo em pílula e o `--controle-g`.
- **`172` e `175`** (#564 e #565, na `main`): os tokens de espaço, raio e coluna.
- **`171`**: o passo pendente da lista, de onde sai o prazo do passo.

## Achados (registro, e não escopo)

- **A-1 — "Recorrer" e o Requerimento de Matrícula continuam fora da jornada.** O `E7` cita "Recorrer"
  com a mesma coluna estreita à esquerda, e o `E12` o Requerimento com cinco campos por linha. São as
  próximas telas da `P2.3` do estudo, cada uma com spec própria.
- **A-2 — A convocação do candidato tem moldura própria de 76rem.** A referência interna desta spec (a
  tela da convocação) usa `.pagina-da-convocacao`, com 76rem e duas colunas a partir de 64rem, e não a
  coluna de 44rem. Quem vem do Acompanhamento para a convocação muda de largura. Alinhar as duas é
  decisão do usuário: a `118` e a `121` escolheram a largura da convocação de propósito.
- **A-3 — O "Por quê" de "Sua situação" repete a Etapa por extenso.** Na tela do exemplo, a frase diz
  "quem se inscreve nela passa também por esta etapa: Heteroidentificação". É redação da `171`, e não
  composição.

## Decisões

### D-001 — A coluna da `174`, e não uma nova

As três telas usam a mesma `.jornada` das telas da verificação: 44rem, centrada. Uma segunda coluna
para o portal criaria duas larguras na mesma jornada, e quem vai do Acompanhamento à verificação
mudaria de largura no meio do caminho. A medida de leitura continua no texto (FR-8104), e não no bloco.

### D-002 — O título do cartão é o Processo

O estudo diz que o cartão nomeia o Processo e o Edital. O Perfil continua, na linha seguinte: quem tem
duas inscrições no mesmo Processo, em Perfis diferentes, ainda as distingue. Antes, o título era o
Perfil e a linha seguinte o Processo; a troca não remove nada.

### D-003 — O prazo do cartão é um só, o da ação principal

Três prazos podem existir ao mesmo tempo. O cartão mostra o da ação que ele oferece — a convocação, o
passo ou o envio do rascunho —, porque é esse que a pessoa cumpre ao tocar no botão. A frase é "Prazo:
até {data}, às {hora}", na forma da convocação da `118`.

### D-004 — A trilha no lugar do "Voltar"

A `174` usa "Voltar ao acompanhamento" no topo das telas da verificação, porque elas são filhas do
Acompanhamento. "Minha inscrição" e "Acompanhar" são filhas de "Minhas inscrições" e irmãs entre si, e
a trilha "Minhas inscrições › {Processo} · {Edital}" diz as duas coisas: de onde se veio e qual
inscrição é. É o "onde estou" do protótipo da convocação do estudo.

### D-005 — "Perfil de Vaga: {nome}" no lugar do subtítulo

O Processo subiu para a trilha, e repeti-lo no subtítulo seria dizer a mesma coisa duas vezes. O Perfil
é o que faltava para identificar a inscrição, e o rótulo é o de "O que você informou".

### D-006 — "Acesso à conta" sai do subtítulo, e não da tela

O link é a única porta para as credenciais da conta (a `010`). Ele fica no começo da tela, na faixa do
título, como ação secundária, e deixa de ocupar o lugar do subtítulo.

### D-007 — Um botão cheio por tela

O Acompanhamento tinha dois: a ação de "Sua situação" e "Ver o que enviei". A ação da situação é a
resposta da tela (a `063`); conferir o que se enviou é consulta, e vira secundário.

### D-008 — O começo das duas telas irmãs sai da versão vigente

Revisão de código do #577. "Minha inscrição" lia o começo da versão aceita, e "Acompanhar", da vigente:
depois de uma Retificação que renomeasse o Perfil ou o Processo, as duas telas irmãs mostravam nomes
diferentes no mesmo cabeçalho. O começo passa a sair da vigente nas duas — é o nome de hoje, o mesmo da
lista e da página da seleção. "O que você informou" continua na aceita, porque é a conferência do que
foi enviado sob aquela versão (a `010`), e é ali que o nome do dia do envio continua legível.

### D-009 — O prazo da convocação fica no cartão com ou sem providência pendente

Revisão de código do #577, que perguntou se o cartão deveria esconder o vencimento quando a pessoa já
entregou o que a convocação pede (o Requerimento enviado, por exemplo). Não esconde, por duas razões:

1. **A `154` decidiu o contrário para o Acompanhamento e para a convocação.** A FR-6208 da `154` manda
   o prazo continuar visível com a chamada aberta, **com ou sem** providência pendente; só a advertência
   do não atendimento depende dela (a FR-6209 da `154`). Na tela de exemplo da revisão, o Acompanhamento
   diz "Seu Requerimento de Matrícula foi enviado" **e** "Prazo desta convocação: até …". Esconder o
   prazo só no cartão faria a lista e o Acompanhamento discordarem, que é o defeito que a revisão quis
   evitar. O teste `test_o_cartao_diz_o_mesmo_prazo_que_o_acompanhamento_com_e_sem_providencia`
   confere os dois nos cenários com providência (C1), com tudo enviado (E) e só com o Requerimento
   enviado (B2).
2. **A derivação custaria consulta por item.** "Não falta nada" sai da leitura dos documentos da
   chamada e da política do Requerimento (a `118` e a `154`), que a lista não faz; o laço da lista
   continua sem consulta (`test_lista_com_convocacao`).

Se o usuário quiser outro comportamento, ele muda a FR-6208 da `154` primeiro, e o cartão a segue.

