# Feature Specification: As quatro decisões de produto da etapa 4

**Feature Branch**: `claude/decisoes-da-etapa-4-088-698fba`, especificada sobre a `main` em
`cf6d7372` e implementada sobre a `main` em `c97ff8af`, que traz da `081` à `087`

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: as quatro perguntas de produto que as revisões dos incrementos da etapa 4 do
[estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md) deixaram abertas — duas
na [`081`](../081-achados-das-revisoes-077-079/spec.md), duas na
[`084`](../084-telas-de-resultado-e-atos/spec.md), e a do rótulo dos avisos na revisão da
[`086`](../086-telas-dos-avisos-aos-candidatos/spec.md). **Em 18/10/2026 o usuário aprovou as quatro
recomendações** ("pode seguir"). Esta feature as executa e as registra.

> **Faixa de identificadores.** Esta spec abre em FR-2000 e SC-780, acima das faixas reservadas às
> features da etapa 4 em paralelo (a mais alta, a da `087`), medida em 18/10/2026 na `main` e nas
> branches dos PRs abertos (298, 299, 300, 301, 302, 303 e 304). A faixa reservada a ela tem trinta
> números de FR e dez de SC.

---

## Por que esta feature existe

**Impressa, a tela deixou de dizer de onde é.** A `076` tirou do papel a barra e o cabeçalho de
contexto, e na época isso era só a barra e "Trocar identidade". Desde a `077`, a trilha mora no
cabeçalho, e cada incremento seguinte levou mais telas para lá: depois da `084` e da `085`, a Mesa,
nove das onze telas de resultado e atos, a Inscrição recebida e o Recurso, impressos, não dizem mais
de que Edital — ou de que Etapa — são. A folha impressa de um Ato de classificação é documento de
trabalho da comissão; sem a trilha, ela é uma tabela de posições de lugar nenhum.

**Dois avisos do mesmo dia têm o mesmo nome.** A trilha do histórico de um aviso termina em
*Aviso de 18/10/2026*. A comissão que confirma um aviso de manhã e outro à tarde vê duas telas com o
mesmo rótulo, e, na conferência da interrupção, um link "Aviso de 18/10/2026" que não diz qual. O
título da tela já tem a hora; a trilha não.

**Do Ato de uma lista de reserva, "Classificação" leva à ampla concorrência.** Num ato da lista PPI,
o link "Classificação" da trilha abre a ordem da ampla concorrência — o desvio que a `FR-497` da
`034` fechou na conferência da emissão, onde voltar perdia o recorte e a pessoa reabria a
conferência do recorte errado sem perceber. É anterior à `084`; ela só o levou ao cabeçalho, e
registrou o achado (a decisão 006 da `084`).

**E uma das quatro respostas é "fica".** O landmark de trilha sem link da lista de Processos e de
Minhas Etapas continua como está até haver autenticação; a decisão é registrada aqui, sem código.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, ato, endereço de
rota, semântica de papel ou texto fora dos três rótulos de trilha dos avisos. A barra lateral
continua fora do papel. Nenhuma tela muda na tela — só no papel — salvo a largura dos três rótulos
dos avisos.

## Dependências

As telas que esta feature toca ganharam a trilha no cabeçalho em PRs ainda abertos em 18/10/2026:

| PR | Feature | O que traz para cá |
|---|---|---|
| 298 | `081` | a folha comum com a regra da marca "irreversível", e a decisão 001 e a decisão 002 da `081` |
| 300 | `084` | a trilha do Ato de classificação no cabeçalho, a `FR-1881` da `084`, a decisão 005 e a decisão 006 da `084` |
| 302 | `086` | a trilha dos avisos no cabeçalho e a `FR-1941` da `086` |
| 304 | `085` | a trilha da Inscrição recebida e do Recurso no cabeçalho |

Os sete PRs entraram na `main` em 18/10/2026 (`c97ff8af`), e a implementação começou depois de
trazê-la para esta branch.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A tela impressa diz de onde é (Priority: P1)

Quem preside a comissão imprime o Ato de classificação da lista PPI para levar à reunião; quem
avalia imprime a inscrição da Mesa; a secretaria imprime uma Inscrição recebida e um Recurso. No
papel, acima do título, sai a mesma trilha que a tela mostra no cabeçalho — o produto, o Processo, o
Edital e os níveis até a tela —, e a folha volta a dizer de que Edital ou de que Etapa ela é.

**Why this priority**: a perda é de identificação de documento de trabalho, e alcança todas as
telas modernizadas de uma vez — é o achado de maior alcance das quatro perguntas.

**Independent Test**: imprimir (ou emular a mídia de impressão em) quatro telas — a inscrição da
Mesa, um Ato de classificação, uma Inscrição recebida e um Recurso — e ler, na folha, a trilha
inteira acima do título, sem a barra lateral e sem "Trocar identidade".

**Acceptance Scenarios**:

1. **Given** um Ato de classificação da lista PPI do Edital 01/2026, **When** a presidência o
   imprime, **Then** a folha começa pela trilha *GPS › Processos Seletivos › PS-… › Edital 01/2026 ›
   Classificação › Ato N*, e só depois vem o título.
2. **Given** a inscrição de uma candidata na Mesa, **When** quem avalia a imprime, **Then** a folha
   traz *Minhas Etapas › Minha Mesa › Inscrição …* acima do título.
3. **Given** qualquer tela da gestão, **When** ela é impressa, **Then** a barra lateral e o link
   "Trocar identidade" não saem no papel.
4. **Given** uma tela que ainda tem o cabeçalho da `076` — o caminho até a seção, sem trilha —,
   **When** ela é impressa, **Then** sai o caminho até a seção, e nada da tela, na tela, muda.

---

### User Story 2 — Dois avisos do mesmo dia têm nomes diferentes (Priority: P2)

A comissão confirmou um aviso às 09:14 e outro às 16:40 do mesmo dia. No histórico de cada um, a
trilha termina em *Aviso de 18/10/2026 às 09:14* e *Aviso de 18/10/2026 às 16:40*; na conferência
da interrupção e na prévia de um reenvio, o link para o aviso diz a mesma coisa.

**Why this priority**: o rótulo ambíguo leva a interromper ou reenviar o aviso errado, e a
interrupção não se desfaz.

**Independent Test**: confirmar dois avisos no mesmo dia, em minutos diferentes, e ler os dois
rótulos diferentes na trilha de cada tela que nomeia um aviso.

**Acceptance Scenarios**:

1. **Given** um aviso confirmado em 18/10/2026 às 16:40, horário de Brasília, **When** alguém abre o
   histórico dele, **Then** a trilha termina em *Aviso de 18/10/2026 às 16:40*, o mesmo texto do
   título.
2. **Given** esse aviso, **When** alguém abre a conferência da interrupção, **Then** o nível da
   trilha que leva ao aviso é o link *Aviso de 18/10/2026 às 16:40*.
3. **Given** esse aviso, **When** alguém abre a prévia de reenviá-lo, **Then** o nível da trilha que
   leva ao aviso anterior é o link *Aviso de 18/10/2026 às 16:40*.

---

### User Story 3 — Do Ato, a Classificação do mesmo recorte (Priority: P2)

A presidência abre o Ato de classificação da lista PPI e segue "Classificação" na trilha. Chega à
Classificação do marco **na lista PPI** — a tela nomeia esse recorte como o atual —, e não na ampla
concorrência.

**Why this priority**: a ida errada é silenciosa — a tela que abre é legítima, só não é a do ato —,
e é o mesmo desvio que a `034` fechou na conferência.

**Independent Test**: num Edital com reserva, emitir a ordem da lista PPI, abrir o ato e seguir
"Classificação": a tela que abre nomeia a lista PPI como recorte atual. Num ato da ampla
concorrência, o link é o de antes.

**Acceptance Scenarios**:

1. **Given** um Ato de classificação da lista PPI, **When** a presidência segue "Classificação" na
   trilha, **Then** abre a Classificação do mesmo marco no recorte PPI.
2. **Given** um Ato de classificação da ampla concorrência, **When** a presidência segue
   "Classificação", **Then** abre a Classificação do marco sem recorte pedido, como antes.
3. **Given** qualquer Ato, **Then** o rótulo do link continua "Classificação", e nenhum outro nível
   da trilha muda.

---

### Edge Cases

- **Tela sem trilha, impressa.** Depois da `087`, só a recusa tem o cabeçalho da `076`, e ela
  imprime o caminho até a seção (*GPS › Processos Seletivos*). É menos que uma trilha, e é o que a
  tela diz na tela; não se inventa trilha só para o papel (D-005).
- **"Trocar identidade" no papel.** Não sai: é ação, não identificação, e no papel não leva a lugar
  nenhum.
- **A trilha longa no papel.** A folha impressa é mais estreita que a tela larga; a trilha quebra a
  linha, como no celular, e nenhum nível é cortado.
- **Links no papel.** Saem como o texto que são; a folha não anexa endereço a cada nível.
- **A tela, na tela.** A regra é só da mídia de impressão: nenhuma medida de tela muda por ela, a 375
  ou a 1280 px, com a barra expandida ou recolhida.
- **Dois avisos confirmados no mesmo minuto.** Continuam com o mesmo rótulo — o título também. A hora
  com segundos tornaria o rótulo ilegível para resolver um caso que a confirmação, que pede
  conferência, quase não produz (D-007).
- **Aviso confirmado perto da meia-noite em UTC.** A data e a hora são as de America/Sao_Paulo, como
  o título e o resto do sistema; um aviso das 22:30 de 18/10 não vira 19/10 na trilha.
- **A lista de avisos.** A linha *Aviso de 09/10, 14:02* da lista de avisos não é trilha, e não muda.
- **Ato de um recorte que a Retificação tirou.** Se a Modalidade do ato não existe mais na versão
  vigente do Edital, "Classificação" leva ao recorte do ato assim mesmo, e a Classificação responde
  como responde a qualquer recorte que não corresponde a Modalidade alguma (`FR-499` da `034`). O
  link não volta à ampla concorrência para esconder a falta (D-006).
- **Ato sucedido.** O link é o recorte **deste** ato, lido do próprio ato, e não de um sucessor.
- **Quem audita.** O link e o destino são os mesmos para a presidência e para a auditoria; a porta da
  Classificação continua a dela.

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no papel (decisão (1) do usuário; D-001, D-005)

- **FR-2000**: Na impressão de toda tela da gestão que tem a barra, o cabeçalho de contexto MUST sair
  no papel, antes do conteúdo, com o que ele mostra na tela: a trilha, nas telas que a têm; o
  caminho até a seção, nas demais.
- **FR-2001**: Na impressão, a barra lateral MUST continuar fora do papel, e o link "Trocar
  identidade" MUST NOT sair.
- **FR-2002**: A regra MUST ser uma só, na folha comum, e valer para toda tela que use o cabeçalho de
  contexto; nenhuma tela MUST precisar de regra própria para imprimir a trilha.
- **FR-2003**: Na tela, nada MUST mudar por causa da regra de impressão: nenhuma medida de nenhuma
  tela, em nenhuma largura, em nenhum estado da barra.
- **FR-2004**: No papel, a trilha MUST quebrar a linha quando não couber, sem cortar nível algum.

*Substitui* o caso-limite "Impressão" da `076` ("A barra e o caminho não saem no papel") quanto ao
caminho, e o caso-limite "Impressão" da `077`, quanto ao cabeçalho de contexto; supera a decisão 002
da `081` e a decisão 005 da `084`, que deixaram a pergunta com o produto.

#### O landmark de trilha sem link (decisão (2) do usuário; D-002)

- **FR-2005**: Na lista de Processos e em Minhas Etapas, a trilha do cabeçalho MUST continuar como
  está — navegação nomeada com o produto, em texto, e a própria tela —, até haver autenticação. Esta
  feature não muda nenhuma linha delas.

#### A hora no rótulo do aviso (decisão (3) do usuário; D-003, D-007)

- **FR-2010**: No histórico de um aviso, a página atual da trilha MUST ser *Aviso de DD/MM/AAAA às
  HH:MM* — a data e a hora em que o aviso foi confirmado, no fuso America/Sao_Paulo —, o mesmo texto
  do título da tela.
- **FR-2011**: Na conferência da interrupção de um aviso e na prévia do reenvio de um aviso, o nível
  da trilha que leva ao aviso MUST ter o mesmo rótulo, com a hora, e MUST continuar levando ao mesmo
  destino.
- **FR-2012**: Nenhum outro nível da trilha dessas três telas MUST mudar, nem de rótulo, nem de
  destino, nem de ordem.

*Substitui* a `FR-1941` da `086` quanto ao rótulo *Aviso de DD/MM/AAAA*; o resto dela continua.

#### "Classificação" no recorte do ato (decisão (4) do usuário; D-004, D-006)

- **FR-2020**: Na trilha do Ato de classificação, o link "Classificação" MUST levar à Classificação
  do marco **no recorte do ato**: no ato de uma lista, ao recorte dessa lista; no ato da ampla
  concorrência, à Classificação sem recorte pedido, como antes.
- **FR-2021**: O endereço do recorte MUST ser derivado do mesmo modo que a conferência da emissão o
  deriva desde a `FR-497` da `034`, e não montado à parte para esta tela.
- **FR-2022**: O rótulo "Classificação" e os demais níveis da trilha do Ato MUST continuar os
  mesmos.

*Substitui* a `FR-1881` da `084` quanto ao destino de "Classificação" no Ato — "os links que a tela
já tinha MUST levar ao mesmo destino" deixa de valer para esse link; o resto dela continua. Fecha o
achado da decisão 006 da `084`.

#### O que não muda

- **FR-2025**: Nenhuma regra de negócio, permissão, porta, endereço de rota, ato, texto de tela ou
  botão MUST mudar, salvo os rótulos de FR-2010 e FR-2011 e o destino de FR-2020.
- **FR-2026**: Os guardiões que já existem — acessibilidade, larguras, estáticos, vocabulário e os
  testes de trilha da `077` à `087` — MUST continuar passando; o que prende um comportamento que esta
  feature substitui MUST ser ajustado no mesmo commit da mudança, dizendo por quê.

### Key Entities

Nenhuma entidade nova nem alterada. Lidas, sem mudança: o **Aviso aos candidatos** (a data e a hora
de confirmação) e o **Ato de classificação** (o recorte que ele congelou — a lista, ou nenhuma, para
a ampla concorrência).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-780**: Impressas, a inscrição da Mesa, um Ato de classificação, uma Inscrição recebida e um
  Recurso trazem no papel, **as quatro**, a trilha inteira que a tela mostra, acima do título; a
  barra lateral e "Trocar identidade" não saem em **nenhuma**.
- **SC-781**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e fora
  das três telas dos avisos nenhuma variante muda de largura ou altura, nos dois estados da barra.
- **SC-782**: Dois avisos confirmados no mesmo dia, em minutos diferentes, têm rótulos de trilha
  **diferentes** em cada uma das três telas que os nomeiam.
- **SC-783**: Num ato da lista PPI, seguir "Classificação" abre a Classificação com a lista PPI
  nomeada como recorte atual — **zero** idas à ampla concorrência a partir de um ato de lista.
- **SC-784**: A suíte contra PostgreSQL fecha sem falha, com as regras de negócio e de permissão
  intocadas — nenhum teste delas ajustado.

## Decisões

### D-001 — A trilha do cabeçalho sai no papel

**Aprovada pelo usuário em 18/10/2026** ("pode seguir"), como recomendada. A `076` tirou o cabeçalho
de contexto da impressão quando ele só tinha o caminho até a seção e "Trocar identidade"; a `077`
pôs nele a trilha e aceitou por escrito que ela não saísse; da `078` à `085`, o mesmo valeu para
cada tela que se modernizou, até que a Mesa, nove das onze telas de resultado e atos, a Inscrição
recebida e o Recurso deixaram de dizer, impressos, de que Edital ou Etapa são. A decisão 002 da
`081` e a decisão 005 da `084` registraram a pergunta. A alternativa — acrescentar o Edital à linha
abaixo do título em cada tela — mudaria texto em dezenas de telas e repetiria a trilha na tela; a
regra única na folha devolve a todas, de uma vez, a mesma identificação que a tela já mostra.

### D-002 — O landmark de trilha sem link fica, até haver autenticação

**Aprovada pelo usuário em 18/10/2026**, como recomendada. Na lista de Processos e em Minhas Etapas,
a trilha é uma navegação nomeada sem link — o produto, em texto, e a própria tela. A decisão 001 da
`081` deixou a pergunta: tirar a navegação nomeada contraria a `FR-1746` da `077`; dar destino ao
produto pede uma página inicial que nenhuma spec definiu e que, para quem só avalia, não pode ser a
lista. Com autenticação haverá uma entrada por pessoa, e é ela que o produto poderá levar. Até lá,
fica; sem código nesta feature.

### D-003 — O rótulo do aviso ganha a hora

**Aprovada pelo usuário em 18/10/2026**, como recomendada. A `FR-1941` da `086` fixou os rótulos que
cada tela já mostrava, e por isso o do aviso ficou só com a data, embora o título tivesse a hora. O
rótulo passa a ser o do título — *Aviso de DD/MM/AAAA às HH:MM* —, que já é o nome que a tela dá a
si mesma; outro formato (*18/10, 16:40*, como na lista de avisos) criaria um terceiro nome para a
mesma coisa.

### D-004 — "Classificação", no Ato, leva ao recorte do ato

**Aprovada pelo usuário em 18/10/2026**, como recomendada. A decisão 006 da `084` registrou o desvio:
num ato de lista, o link leva à ampla concorrência, e a `FR-1881` da `084` pedia o mesmo destino de
antes. O ato congelou o recorte; voltar dele à Classificação é voltar àquele recorte, exatamente como
"Cancelar e voltar" faz na conferência da emissão desde a `FR-497` da `034`. O endereço sai do mesmo
lugar que o da conferência, para que nenhum template monte `?lista=` à mão.

### D-005 — No papel sai o cabeçalho inteiro, menos "Trocar identidade"

O que se imprime é o que o cabeçalho mostra na tela, sem regra por tela: a trilha, onde há trilha; o
caminho até a seção, onde ainda não há. Imprimir só a trilha e esconder o caminho exigiria distinguir
as duas na folha, e a tela não modernizada perderia no papel até a seção, que ela mostra na tela.
"Trocar identidade" é ação, não identificação, e fica fora.

### D-006 — Recorte que deixou de existir: o link vai ao recorte assim mesmo

Um ato antigo pode ser de uma Modalidade que uma Retificação tirou. O link leva ao recorte do ato, e
a Classificação responde como responde a qualquer recorte que não corresponde a Modalidade alguma
(`FR-499` da `034`). Voltar, nesse caso, à ampla concorrência reabriria em silêncio o desvio que esta
feature fecha, trocando uma resposta honesta ("esse recorte não existe mais") por uma tela legítima
de outro recorte.

### D-007 — Dois avisos no mesmo minuto continuam com o mesmo rótulo

A hora vai até o minuto, como no título. Segundos resolveriam o caso, à custa de um rótulo que
ninguém lê; e a confirmação de um aviso, que passa por prévia e conferência, quase não produz dois no
mesmo minuto. Se produzir, o título e a trilha empatam do mesmo jeito, e o histórico da lista os
distingue pela ordem.

## Assumptions

- O fuso de exibição é o do sistema (America/Sao_Paulo), o mesmo que o título do aviso e todas as
  datas da gestão já usam.
- A impressão é a do navegador; não há PDF gerado pelo sistema para estas telas — o PDF oficial é o do
  Edital, que não passa por esta folha.
- A conferência de impressão se faz pela emulação da mídia de impressão no navegador, ou pelo Chrome
  sem interface com impressão para PDF; o CI não imprime.
