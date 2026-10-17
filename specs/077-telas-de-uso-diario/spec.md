# Feature Specification: As telas de uso diário, primeiro incremento

**Feature Branch**: `claude/determined-jennings-37b730`, sobre a `main` `5c729dd0` (com a `076`)

**Created**: 2026-10-16

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental, começando pelas de uso diário. Primeiro incremento,
com três frentes que a [`075`](../075-entrada-da-gestao/spec.md) e a
[`076`](../076-shell-da-gestao/spec.md) deixaram registradas fora do escopo delas. A linha de base
visual é o [inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), refeito com
o shell.

> **Faixa de identificadores.** Esta spec abre em FR-1740 e SC-670, acima da faixa da `076`.

---

## Por que esta feature existe

A `076` pôs a gestão dentro de uma moldura — barra lateral com as seções e cabeçalho de contexto —
sem tocar o conteúdo de tela nenhuma. Isso deixou três sobras, todas registradas:

1. **A lista de Processos oferece as mesmas seções duas vezes.** Visão Geral, Autoridades da
   unidade e Modelos de aviso estão na barra e continuam como botões na faixa de ações da lista,
   ao lado de "Novo Processo Seletivo", que é a única ação de verdade dali (DP-1 da `076`).
2. **Cinco telas estouram a largura do celular.** O inventário mediu, a 375 px, a página inteira
   rolando para o lado em conclusões preservadas (835 px), reaproveitar Edital (994), sorteio
   (643), anexos da composição (432) e detalhe da Retificação (388). Quem abre uma delas no
   celular perde a margem direita de todo o conteúdo, e não só do trecho largo (DP-3 da `076`).
3. **O cabeçalho de contexto para na seção.** Ele diz *GPS › Minhas Etapas* e, logo abaixo, dentro
   do conteúdo, a tela repete o caminho em outra linha — *Minhas Etapas › Minha Mesa › Inscrição*.
   São dois lugares para a mesma pergunta, "onde estou". A `076` não juntou os dois porque isso é
   mexer no conteúdo das telas (R-004 da `076`).

Este incremento resolve as três, e só nas telas que a pessoa abre todo dia: a lista, Minhas Etapas
e a Mesa. As outras telas continuam como estão; cada uma entra num incremento próprio.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel
ou fluxo. Nenhum endereço. Nenhuma tela fora das nomeadas aqui. Nas cinco telas que estouram, o
conteúdo continua o mesmo — o que muda é só como ele cabe.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A lista oferece o que é dela (Priority: P1)

Um gestor abre a lista de Processos. Na faixa acima dos Processos ele encontra "Novo Processo
Seletivo", e mais nada: a Visão Geral, as Autoridades da unidade e os Modelos de aviso estão na
barra, à esquerda, como em qualquer outra tela.

**Why this priority**: é o defeito mais visível — a primeira tela do dia oferece os mesmos
destinos duas vezes, na barra e nos botões —, e o mais barato de resolver.

**Independent Test**: identificado como Gestor, abrir a lista; a faixa de ações tem só "Novo
Processo Seletivo"; os três destinos continuam na barra.

**Acceptance Scenarios**:

1. **Given** uma identidade com o papel Gestor, **When** ela abre a lista de Processos, **Then** o
   conteúdo da tela oferece "Novo Processo Seletivo" e não oferece Visão Geral, Autoridades da
   unidade nem Modelos de aviso, que continuam na barra lateral.
2. **Given** uma identidade sem a capacidade de criar Processo, **When** ela abre a lista, **Then**
   a faixa de ações não aparece, vazia ou não.
3. **Given** qualquer identidade, **When** ela segue um item da barra que a lista oferecia, **Then**
   chega ao mesmo destino de antes, com a mesma resposta.

---

### User Story 2 — Nenhuma tela rola para o lado no celular (Priority: P1)

Uma presidente de comissão abre as conclusões preservadas de uma Etapa no celular. Hoje a página
inteira tem 835 px e rola para o lado: o título, as orientações e os botões perdem a margem
direita. Com a correção, a página cabe na tela; a tabela, que é larga, rola dentro da própria
moldura, como já rolam as outras tabelas largas.

**Why this priority**: estourar a largura atinge a tela inteira, e não só o trecho largo — e o
inventário prova que é defeito, e não gosto.

**Independent Test**: a 375 px, cada uma das cinco telas tem a largura da janela, e o que nela é
largo rola dentro da própria moldura ou quebra a linha.

**Acceptance Scenarios**:

1. **Given** a tela das conclusões preservadas a 375 px, **When** ela abre, **Then** a página não
   rola para o lado, e a tabela rola dentro da moldura que já tinha.
2. **Given** a tela de reaproveitar um Edital a 375 px, **When** ela abre, **Then** a página não
   rola para o lado, e a tabela das origens rola dentro da moldura que já tinha.
3. **Given** a tela do sorteio a 375 px, **When** ela abre, **Then** os resumos criptográficos
   quebram a linha dentro da largura, sem perder nenhum caractere.
4. **Given** a etapa de anexos da composição a 375 px, **When** ela abre, **Then** o cartão de
   anexo novo cabe na largura, com os mesmos campos.
5. **Given** o detalhe de uma Retificação a 375 px, **When** ele abre, **Then** a página não rola
   para o lado, e a tabela das alterações rola dentro de uma moldura própria.
6. **Given** qualquer uma das cinco telas a 1280 px, **When** ela abre, **Then** ela continua igual
   ao que era.

---

### User Story 3 — Onde estou, dito uma vez só (Priority: P2)

Um avaliador abre uma inscrição na Mesa. No topo, o cabeçalho de contexto diz o caminho inteiro —
*GPS › Minhas Etapas › Minha Mesa › Inscrição INS-2026-0001* —, e cada nível acima da tela leva a
ele. O conteúdo da tela começa pelo título, sem uma segunda linha de caminho.

**Why this priority**: orienta, e tira uma linha repetida da tela mais usada; as P1 corrigem
defeitos.

**Independent Test**: nas quatro telas de uso diário, o caminho está no cabeçalho de contexto, com
um link por nível acima da tela e a própria tela marcada como atual; o conteúdo não tem trilha; a
página tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** uma inscrição aberta na Mesa, **When** a página abre, **Then** o cabeçalho de contexto
   mostra *GPS › Minhas Etapas › Minha Mesa › Inscrição …*, com Minhas Etapas e Minha Mesa como
   links e a inscrição como a página atual, e o conteúdo começa pelo título.
2. **Given** uma Etapa aberta a partir de Minhas Etapas, **When** a página abre, **Then** o
   cabeçalho mostra *GPS › Minhas Etapas › nome da Etapa*.
3. **Given** a mesma Etapa aberta pela Alocação, por quem gere a comissão, **When** a página abre,
   **Then** o cabeçalho mostra o caminho que a tela já mostrava, pela Alocação por Etapa.
4. **Given** a lista de Processos ou Minhas Etapas, **When** a página abre, **Then** o cabeçalho
   mostra *GPS ›* e o nome da tela, marcado como a página atual.
5. **Given** qualquer outra tela da gestão, **When** ela abre, **Then** o cabeçalho continua como
   na `076` — *GPS ›* e a seção, em texto —, e a trilha continua no conteúdo dela.

### Edge Cases

- **Lista sem nenhuma ação.** Quem não pode criar Processo não vê a faixa de ações — nem vazia. A
  orientação de quem não tem papel continua onde está.
- **Os botões removidos e a autorização.** Tirar o botão não muda quem chega ao destino: o item da
  barra continua condicionado à mesma capacidade, e o endereço montado à mão continua recebendo a
  mesma resposta.
- **Caminho longo no celular.** O caminho da inscrição na Mesa tem quatro níveis. A 375 px ele
  quebra a linha dentro do cabeçalho; nem ele nem "Trocar identidade" estouram a largura.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título: o caminho fica
  antes, junto da barra, e é pulado com ela.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). Nas quatro telas, o
  caminho sai com o cabeçalho; o título e a linha de baixo dele — o Edital e o Processo —
  continuam identificando o que se imprimiu.
- **A Etapa aberta pela gestão.** O endereço é o de Minhas Etapas, e a barra destaca Minhas Etapas
  (`076`), mas o caminho que a tela já dava, e que continua dando, passa pela Alocação por Etapa.
  É o que a tela dizia antes, e não muda aqui.
- **Rótulo invisível dentro de tabela que rola.** O estouro das conclusões preservadas vinha de um
  rótulo que só tecnologia assistiva lê, e não de nada visível. O rótulo continua existindo e
  sendo lido do mesmo jeito.
- **Resumo criptográfico partido.** O resumo quebra a linha por caractere; copiá-lo continua dando
  o valor inteiro, sem espaço nem hífen.

## Requirements *(mandatory)*

### Functional Requirements

#### A lista de Processos

- **FR-1740**: O conteúdo da lista de Processos MUST NOT oferecer Visão Geral, Autoridades da
  unidade nem Modelos de aviso: esses destinos estão na barra lateral (`FR-1713` da `076`).
- **FR-1741**: "Novo Processo Seletivo" MUST continuar na lista, no mesmo lugar, para quem tem a
  capacidade de criar Processo (DP-1 da `076`). Sem essa capacidade, a faixa de ações MUST NOT
  aparecer.
- **FR-1742**: Os itens da barra MUST continuar exatamente os da `076`, papel a papel, e cada
  destino MUST continuar respondendo a cada identidade como antes (`FR-1721` da `076`).

#### Os estouros a 375 px

- **FR-1743**: As telas das conclusões preservadas, de reaproveitar Edital, do sorteio, dos anexos
  da composição e do detalhe da Retificação MUST caber na largura da janela a 375 px, sem rolagem
  horizontal da página.
- **FR-1744**: Em cada uma delas, o conteúdo MUST continuar o mesmo — os mesmos textos, campos,
  tabelas, colunas e valores, na mesma ordem —, e o que é largo MUST rolar dentro da própria
  moldura ou quebrar a linha. Nenhum caractere de resumo criptográfico MUST se perder.
- **FR-1745**: A 1280 px, essas cinco telas MUST continuar sem estouro, e a correção de cada uma
  MUST valer só nela: nenhuma outra tela do inventário MUST mudar de largura.

#### A trilha no cabeçalho de contexto

- **FR-1746**: Na lista de Processos, em Minhas Etapas, na Etapa da Mesa e na inscrição da Mesa, o
  cabeçalho de contexto MUST mostrar a trilha da tela, como navegação nomeada: o produto, cada
  nível acima da tela como link, e a própria tela como a página atual.
- **FR-1747**: Nessas quatro telas, a trilha MUST NOT aparecer de novo no conteúdo: a página MUST
  ter uma trilha só. Os níveis e os rótulos MUST ser os que a tela já mostrava — inclusive o
  caminho pela Alocação por Etapa, quando a Etapa é aberta pela gestão.
- **FR-1748**: Nas demais telas da gestão, o cabeçalho de contexto MUST continuar o da `076` —
  o produto e a seção, em texto —, e a trilha MUST continuar no conteúdo delas.
- **FR-1749**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.

#### O que não pode piorar

- **FR-1750**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida.
- **FR-1751**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras,
  vocabulário e bytes que já varrem a gestão — o link de salto, o `main`, toda classe com regra na
  folha, o teto da distribuição.

### Key Entities

Nenhuma. Só apresentação.

## Success Criteria *(mandatory)*

- **SC-670**: Na lista de Processos, a faixa de ações tem **uma** ação — "Novo Processo Seletivo"
  — para quem pode criar Processo, e nenhuma para quem não pode.
- **SC-671**: Refeito o inventário visual, o número de telas que estouram a 375 px cai de **cinco**
  para **zero**, e nenhuma estoura a 1280 px.
- **SC-672**: Comparado tela a tela com a linha de base do shell, nenhuma variante muda de
  `status` nem ganha estouro, com a barra expandida e recolhida.
- **SC-673**: Nas quatro telas de uso diário, "onde estou" aparece **uma** vez por página, no
  cabeçalho de contexto, e cada nível acima da tela está a **um** clique.
- **SC-674**: A suíte contra PostgreSQL continua sem falhas.
- **SC-675**: O percurso lista → Minhas Etapas → Etapa → inscrição → de volta pelo caminho é
  feito só pelo teclado, com foco visível, a 1280 e a 375 px.

## Assumptions

- "Telas de uso diário" são as quatro do estudo (§7): a lista, Minhas Etapas e a Mesa — a Etapa
  (`minha_etapa`) e a inscrição. A trilha da avaliação e o documento da Mesa ficam para outro
  incremento.
- O produto no começo da trilha é a sigla GPS, como no cabeçalho de contexto da `076`; quem leva à
  lista é a marca e a barra, e a sigla continua em texto.
- Os cinco estouros são os do inventário refeito com o shell, com os mesmos `scrollWidth` da linha
  de base. Nenhum outro foi medido.
- O link "Ver minhas atribuições", na orientação de quem integra comissão, não é um dos três botões
  que a `076` duplicou na barra — é parte da frase —, e fica.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
