# Feature Specification: O shell da gestão

**Feature Branch**: `claude/great-grothendieck-2155ee`, sobre a `main` `31268896`

**Created**: 2026-10-16

**Status**: Especificada — as três decisões do responsável pelo produto tomadas em 16/10 (ver
*Decisões do responsável pelo produto*)

**Input**: etapa 2 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§3, §6 e §7), no conceito A, escolhido pelo responsável pelo produto em 16/10/2026. A etapa 1 é a
[`075`](../075-entrada-da-gestao/spec.md). A linha de base visual é o
[inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), refeito depois da `075`.

> **Faixa de identificadores.** Esta spec abre em FR-1710 e SC-660, acima da faixa da `075`.

---

## Por que esta feature existe

A gestão tem uma página de entrada desde a `075`, mas, depois dela, continua sem navegação. O
cabeçalho tem um link só, "Minhas Etapas". Visão Geral, Autoridades da unidade e Modelos de aviso
são botões dentro da lista de Processos; de qualquer outra tela, o único caminho até eles é voltar
à lista pela marca (achado N5 do estudo). Quem está fundo num Edital não sabe onde está em relação
ao resto, e não tem como ir a outra seção sem voltar ao começo.

Esta feature dá à gestão uma moldura fixa — barra lateral com as seções e cabeçalho de contexto
com o caminho — **em volta** das telas que já existem. O conteúdo de cada tela não muda.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão ou semântica de
papel. A barra só oferece o destino que a autorização já abriria, e retirar um link nunca
substitui a recusa no servidor (`FR-482` e `FR-483` da `033`). Nenhuma tela muda de conteúdo,
de endereço ou de comportamento.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — De qualquer tela, chegar a qualquer seção (Priority: P1)

Uma gestora está no detalhe de um Edital e precisa ver a Visão Geral. Hoje ela volta à lista pela
marca e procura o botão. Com o shell, a Visão Geral está na barra lateral, à esquerda, em toda
tela; ela clica e chega.

**Why this priority**: é o defeito que motiva a feature (N5) e o ganho que se percebe no primeiro
dia.

**Independent Test**: identificado como Gestor, abrir uma tela qualquer da gestão e encontrar na
barra cada seção que o papel alcança; seguir cada uma leva à seção.

**Acceptance Scenarios**:

1. **Given** uma identidade com o papel Gestor, **When** ela abre qualquer tela da gestão, **Then**
   a barra lateral mostra o grupo *Trabalho* (Processos Seletivos, Minhas Etapas, Visão Geral) e o
   grupo *Unidade* com as seções que o papel alcança.
2. **Given** a barra aberta numa tela qualquer, **When** a pessoa segue um item, **Then** chega à
   seção, sem passar pela lista.
3. **Given** uma identidade sem papel nenhum, que só preside uma comissão, **When** ela abre a
   gestão, **Then** a barra mostra Processos Seletivos e Minhas Etapas, e nenhuma seção que a
   autorização recusaria.

---

### User Story 2 — A barra nunca oferece o que a autorização recusa (Priority: P1)

Um Elaborador não pode ver a Visão Geral nem gerir autoridades. A barra não lhe mostra esses
itens — e, se ele montar o endereço à mão, recebe a mesma recusa de hoje.

**Why this priority**: oferecer destino que a autorização recusa é o defeito que a `033` fechou;
uma barra presente em toda tela o reabriria em toda tela.

**Independent Test**: para cada papel, os itens da barra são exatamente os destinos que aquele
papel abre; os endereços dos itens ausentes continuam recusados como antes.

**Acceptance Scenarios**:

1. **Given** uma identidade só com o papel Elaborador, **When** ela abre a gestão, **Then** a barra
   não traz Visão Geral, Autoridades da unidade nem Modelos de aviso, e o grupo *Unidade* não
   aparece.
2. **Given** a mesma identidade, **When** ela abre à mão o endereço da Visão Geral, **Then** recebe
   a mesma resposta que recebia antes desta feature.
3. **Given** uma identidade com o papel Publicador, **When** ela abre a gestão, **Then** a barra
   traz Modelos de aviso, e não traz Autoridades da unidade.

---

### User Story 3 — Saber onde se está (Priority: P2)

Quem abre uma tela vê, no topo, em que seção da gestão ela está, e, na barra, a mesma seção
destacada. Do mesmo topo, troca de identidade. O caminho detalhado até a tela — o Processo, o
Edital, a Etapa — continua sendo a trilha que 54 telas já têm no próprio conteúdo.

**Why this priority**: orienta, mas não destrava trabalho; a P1 já resolve o deslocamento.

**Independent Test**: em telas de seções diferentes, o cabeçalho de contexto nomeia a seção certa
e a barra destaca o mesmo item; "Trocar identidade" leva à página de acesso.

**Acceptance Scenarios**:

1. **Given** o detalhe de um Edital, **When** a página abre, **Then** o cabeçalho de contexto diz
   Processos Seletivos, Processos Seletivos está destacado na barra como a seção atual, e a trilha
   da tela continua a de antes.
2. **Given** uma Etapa aberta a partir de Minhas Etapas, **When** a página abre, **Then** Minhas
   Etapas é a seção atual.
3. **Given** qualquer tela, **When** a pessoa usa "Trocar identidade", **Then** chega à página de
   acesso, que mostra com quem está e oferece continuar ou trocar (`075`).
4. **Given** o pé da barra, **When** a pessoa o lê, **Then** encontra o próprio nome, as
   responsabilidades e "Sair".

---

### User Story 4 — No celular, a barra recolhe (Priority: P2)

No celular, a barra não come a tela. Ela fica recolhida atrás de um botão no topo; quem precisa
mudar de seção a abre, escolhe e segue.

**Why this priority**: sem isso, a barra empurraria o conteúdo de toda tela para baixo, ou para o
lado, a 375 px.

**Independent Test**: a 375 px, a barra começa fechada; abri-la pelo botão mostra os mesmos itens;
nenhuma tela passa a ter rolagem horizontal.

**Acceptance Scenarios**:

1. **Given** uma tela larga como a de um celular, **When** a página abre, **Then** a barra está
   recolhida e o conteúdo começa logo abaixo do topo.
2. **Given** a barra recolhida, **When** a pessoa aciona o botão, por toque ou teclado, **Then** a
   barra abre com os mesmos itens da tela larga.
3. **Given** um navegador sem script, **When** a página abre no celular, **Then** as seções
   continuam alcançáveis.

### Edge Cases

- **Página sem identidade.** As telas que se mostram sem identidade (a recusa de quem não está
  identificado, por exemplo) não têm barra: não há seção a oferecer a quem não é ninguém. O topo
  mostra só a marca, como hoje.
- **Papel que não alcança grupo nenhum de *Unidade*.** O grupo não aparece — nem o título dele.
- **Trilha duplicada.** O cabeçalho de contexto não repete o título nem a trilha da tela: ele diz a
  seção, e a trilha que a tela já tem diz o resto. Levar a trilha das 54 telas para o topo é mexer
  no conteúdo delas, e fica para a modernização por tela (etapa 4 do estudo).
- **Seção cujo acesso vem de vínculo, e não de papel.** Nenhuma das seções da barra é assim hoje;
  as telas de comissão e alocação são de um Processo, e continuam alcançadas pela lista.
- **Tela com conteúdo largo a 1280 px** (matriz de alocação, tabelas de oito colunas). A barra tira
  largura do conteúdo; nenhuma tela que cabia a 1280 pode passar a estourar.
- **Link de salto.** Continua o primeiro foco da página e leva ao conteúdo, passando por cima da
  barra e do caminho.
- **Impressão.** A barra e o caminho não saem no papel.

## Requirements *(mandatory)*

### Functional Requirements

#### A moldura

- **FR-1710**: Toda tela da gestão vista por alguém identificado MUST ter a barra lateral de
  navegação e o cabeçalho de contexto em volta do conteúdo. O conteúdo de cada tela MUST continuar
  o mesmo, no mesmo endereço e com o mesmo comportamento.
- **FR-1711**: Tela da gestão vista sem identidade MUST NOT ter barra lateral, e o topo MUST
  mostrar só a marca.
- **FR-1712**: O link de salto MUST continuar sendo o primeiro foco da página e MUST levar o foco
  ao conteúdo, pulando a barra e o caminho.

#### A barra

- **FR-1713**: A barra MUST agrupar as seções em *Trabalho* — Processos Seletivos, Minhas Etapas,
  Visão Geral — e *Unidade* — Autoridades da unidade, Modelos de aviso (DP-1). "Novo Processo
  Seletivo" MUST continuar na lista, e os botões da lista MUST continuar onde estão.
- **FR-1714**: Cada item MUST aparecer só para quem tem a capacidade que o destino exige, pelo
  mesmo critério que hoje condiciona os botões da lista. Grupo sem item MUST NOT aparecer.
  Processos Seletivos e Minhas Etapas MUST aparecer para toda identidade.
- **FR-1715**: Montar a barra MUST NOT custar consulta ao banco: as capacidades já estão na sessão.
- **FR-1716**: A seção a que a tela pertence MUST estar destacada — fundo verde-claro e filete — e
  marcada como atual para tecnologia assistiva. Cada tela da gestão MUST pertencer a no máximo uma
  seção.
- **FR-1717**: O pé da barra MUST mostrar o nome da identidade, as responsabilidades dela e a ação
  de sair, que continua encerrando a identidade e levando à página de acesso (`075`).

#### O cabeçalho de contexto

- **FR-1718**: O cabeçalho de contexto MUST mostrar o caminho do produto até a seção da tela e a
  ação "Trocar identidade", que leva à página de acesso. Ele MUST NOT repetir o título nem a trilha
  que a tela já traz no conteúdo.

#### Celular

- **FR-1719**: Abaixo da largura de tablet, a barra MUST começar recolhida, atrás de um botão no
  topo que a abre e fecha por toque e por teclado, e anuncia se está aberta. A moldura MUST NOT
  depender de script: a Visão Geral não carrega script nenhum, e continua sem carregar.

#### O que não pode piorar

- **FR-1720**: Nenhuma tela do inventário visual de 16/10 MUST deixar de carregar, nem passar a
  ter rolagem horizontal a 375 ou a 1280 px. Os cinco estouros que já existiam a 375 px MUST NOT
  crescer, e ficam registrados, fora do escopo (DP-3).
- **FR-1721**: O conjunto de pares (identidade, tela) que abre MUST ser exatamente o de antes desta
  feature. A barra não cria nem afrouxa autorização.
- **FR-1722**: A tela de distribuição MUST continuar abaixo do teto de bytes que a protege, e as
  regras visuais da moldura MUST viver na folha comum, sem reescrevê-la: toda classe nova com
  regra própria.
- **FR-1723**: A moldura MUST passar pelos guardiões de acessibilidade, larguras e vocabulário que
  já varrem a gestão — marcos de navegação nomeados, foco visível, contraste dos tokens.

### Key Entities

Nenhuma. A barra é apresentação derivada das capacidades da identidade, que já estão na sessão.

## Success Criteria *(mandatory)*

- **SC-660**: De qualquer tela da gestão, uma pessoa identificada chega a qualquer seção que o
  papel dela alcança com **um** clique na tela larga e **dois** no celular.
- **SC-661**: Para cada um dos papéis de responsabilidade e para a identidade só com vínculo, os
  itens da barra são exatamente os destinos que aquela identidade abre — nenhum a mais, nenhum a
  menos.
- **SC-662**: Refeito o inventário visual com a moldura, as 84 variantes capturadas na linha de
  base continuam carregando, e nenhuma passa a estourar a 375 ou a 1280 px.
- **SC-663**: A suíte contra PostgreSQL continua sem falhas.
- **SC-664**: A barra e o caminho são percorríveis só pelo teclado, com foco visível, na tela larga
  e no celular.

## Decisões do responsável pelo produto

Tomadas em 16/10/2026, nas três propostas que a spec levou.

- **DP-1 — Quais seções entram na barra.** As cinco do `FR-1713`. "Novo Processo Seletivo" fica
  na lista, por ser ação e não lugar. Os botões da lista continuam onde estão (`FR-1710`: o
  conteúdo das telas não muda); retirá-los é passo de outra feature.
- **DP-2 — Se a moldura entra atrás de uma chave.** Sem chave. A moldura é só apresentação, não
  abre nem fecha nada; voltar atrás é reverter o PR, e a suíte prova um cabeçalho só.
- **DP-3 — Os cinco estouros a 375 px já conhecidos.** Ficam registrados, fora do escopo — são do
  conteúdo das telas, e não da moldura —, e a comparação prova que nenhum deles piora. São eles:
  conclusoes-preservadas (835 px), reaproveitar (994), sorteio (643), compor-anexos (432) e
  retificacao-detalhe (388).

## Assumptions

- A largura de tablet é a que a folha já usa para o painel do documento (64rem); abaixo dela, a
  barra recolhe.
- A seção de cada tela se decide pelo endereço, e não por marcação nas telas — é o que permite não
  tocar o conteúdo delas.
- O botão que recolhe a barra usa o comportamento nativo do navegador para painéis sobrepostos.
  Num navegador antigo que não o conheça, a barra simplesmente fica aberta no celular, e o botão
  não aparece.
- O ícone de cada item, se houver, é desenhado na própria página, sem biblioteca nova.
- A marca do produto no topo da barra é o nome "Gestão de Processos Seletivos" e a sigla GPS
  (`075`); a marca oficial do Ifes continua fora.
