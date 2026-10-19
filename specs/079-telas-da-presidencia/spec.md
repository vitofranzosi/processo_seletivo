# Feature Specification: As telas da presidência da comissão, terceiro incremento

**Feature Branch**: `claude/gallant-kepler-eabdb2`, sobre a branch da `078`
(`claude/festive-tereshkova-9a826c`, `e781dfb3`, PR 293 ainda aberto), que traz a `075`, a `076` e a
`077`

**Created**: 2026-10-17

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Terceiro incremento, depois de quem avalia
([`077`](../077-telas-de-uso-diario/spec.md)) e de quem elabora
([`078`](../078-telas-de-quem-elabora/spec.md)): o grupo de uso diário que falta, o da presidência da
comissão — a Comissão do Processo, com a conferência da inclusão, a Alocação por Etapa e a
Distribuição de uma Etapa. A linha de base visual é o
[inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), no estado `depois-da-078`,
reproduzido em 17/10/2026 sobre `e781dfb3` sem diferença nenhuma, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec abre em FR-1780 e SC-690, acima da faixa da `078`
> (FR-1777, SC-686), medida em todas as worktrees e branches em 17/10/2026.

---

## Por que esta feature existe

**A presidência é a última a ler "onde estou" duas vezes.** Depois da `077` e da `078`, quem avalia e
quem elabora leem o caminho uma vez, no cabeçalho de contexto. Quem preside passa o dia entre quatro
telas — a Comissão, a conferência de quem vai entrar nela, a Alocação por Etapa e a Distribuição de
cada Etapa —, e nas quatro o cabeçalho diz *GPS › Processos Seletivos*, e logo abaixo, dentro do
conteúdo, a tela repete o caminho em outra linha. A Etapa aberta pela gestão em Minhas Etapas já tem
a trilha da Alocação no cabeçalho desde a `077` (`FR-1752`): a Distribuição, que é a tela vizinha
dela, ainda não.

**Na Distribuição, os lugares da Etapa estão no meio da página.** Impedimentos, Registrar ocorrência,
Resultados e Trilha são os lugares para onde a presidência sai da Etapa — como Supervisão, Comissão e
Alocação são os do Processo, numa faixa logo abaixo do título (`078`), e como a Comissão e a Alocação
levam uma à outra, também logo abaixo do título. Na Distribuição a faixa vem depois da ficha, dos dois
grupos de filtros e da tabela de quem está alocado. **Medido em 17/10/2026**, na Etapa do inventário,
que tem duas pessoas alocadas: a faixa começa em y ≈ 644 px a 1280 px de janela, e em y ≈ 998 px a
375 px — abaixo da primeira tela do celular. Ela desce cerca de 40 px por pessoa alocada, porque a
tabela de carga tem uma linha por pessoa.

**A Comissão não tem título para os membros.** A página tem "Adicionar membro" e "Adicionar vários de
uma vez" como seções com título, e os membros — o conteúdo principal dela — como uma lista sem título
entre o filtro e as seções de inclusão. Quem navega por títulos pula dos membros sem saber que eles
estão ali, e quem lê não sabe quantos são sem contar os cartões, enquanto os Editais do Processo dizem
"Editais (3)" desde a `078`. E a comissão ainda vazia mostra o filtro — "Só quem está sem Etapa (0 de
0)" — para procurar em nada, antes de dizer que não há ninguém.

**Na Alocação, a ação principal diz outra coisa.** A tela se chama Alocação, e não Distribuição, por
decisão registrada no próprio template: "uma palavra por conceito", porque a Distribuição é a tela
vizinha, que põe inscrições em avaliadores. A mensagem de sucesso diz "Alocação salva." — e o botão
que a produz diz "Salvar distribuição". A arquitetura do manual registrou a divergência ("embora o
ato seja alocar").

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel —
presidir é vínculo com a comissão, e não papel — ou fluxo. Nenhum endereço, nenhuma view. Nenhum
conteúdo normativo. Nenhuma ação da Distribuição — consolidar, propor, confirmar, distribuir,
retirar — muda de lugar, de peso ou de rótulo. A matriz da Alocação continua regida pela `FR-1062` da
`057`, com a barra recolhida em qualquer largura (DP-4 da `076`). Nenhuma tela fora destas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, também para quem preside (Priority: P1)

O presidente da comissão abre a Distribuição da Prova objetiva. No topo, o cabeçalho de contexto diz
*GPS › Processos Seletivos › PS-DEMO-2026 › Alocação por Etapa › Prova objetiva*, e cada nível acima
da tela leva a ele. O conteúdo começa pelo título. O mesmo vale na Comissão, na conferência da
inclusão e na Alocação.

**Why this priority**: é o que a `077` e a `078` fizeram nas telas dos outros dois públicos; sem
isso, a presidência é o único público que ainda lê o caminho duas vezes, e a Distribuição diverge da
Etapa aberta pela gestão, que já tem a trilha no cabeçalho.

**Independent Test**: nas quatro telas, o caminho está no cabeçalho de contexto, com um link por
nível acima da tela e a tela como página atual; o conteúdo não tem trilha; a página tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** a Comissão de um Processo, **When** a página abre, **Then** o cabeçalho mostra *GPS ›
   Processos Seletivos › código do Processo › Comissão*, com os dois níveis do meio como links, e o
   conteúdo começa pelo título.
2. **Given** a conferência da inclusão de um membro ou de uma lista, **When** a página abre, **Then**
   o cabeçalho mostra *GPS › Processos Seletivos › código › Comissão › Conferir*, com a Comissão como
   link.
3. **Given** a Alocação por Etapa, **When** a página abre, a 1280 ou a 375 px, **Then** o cabeçalho
   mostra *GPS › Processos Seletivos › código › Alocação por Etapa*, a barra continua recolhida e a
   matriz continua sem rolagem interna na tela larga, com o cabeçalho dela preso à janela.
4. **Given** a Distribuição de uma Etapa, **When** a página abre, **Then** o cabeçalho mostra *GPS ›
   Processos Seletivos › código › Alocação por Etapa › nome da Etapa*, como a Etapa aberta pela gestão.
5. **Given** as telas que se abrem a partir da Distribuição — Impedimentos, Registrar ocorrência,
   Resultados, Trilha, as conclusões preservadas, a retirada de atribuições —, **When** abrem, **Then**
   o cabeçalho continua o da `076`, e a trilha continua no conteúdo.

---

### User Story 2 — Os lugares da Etapa logo abaixo do título (Priority: P1)

A presidente abre a Distribuição de uma Etapa com uma banca de dez pessoas. Logo abaixo do título e do
Edital, estão Impedimentos, Registrar ocorrência, Resultados e Trilha — os mesmos links, na mesma
ordem, no mesmo desenho. A ficha, os números, quem está alocado e o trabalho vêm depois, como antes.

**Why this priority**: é o desenho que as outras três telas da presidência e o Processo já têm — os
lugares de onde se sai, junto do título —, e hoje a faixa desce com o tamanho da banca, para baixo da
primeira tela do celular.

**Independent Test**: a faixa dos lugares da Etapa é o primeiro bloco do conteúdo depois do título,
do Edital e das mensagens sobre o último envio; tem os mesmos quatro links, na mesma ordem; nada
mais na página muda de lugar.

**Acceptance Scenarios**:

1. **Given** a Distribuição de qualquer Etapa, **When** a página abre, **Then** a faixa com
   Impedimentos, Registrar ocorrência, Resultados e Trilha vem antes da ficha da Etapa, e os quatro
   links levam aonde levavam.
2. **Given** a Distribuição depois de um envio, com o resultado do lote, **When** a página abre,
   **Then** o resultado continua logo abaixo do título, antes da faixa.
3. **Given** a Distribuição com prontas para consolidar, **When** a página abre, **Then** "Consolidar
   as prontas" continua logo depois dos números de prontidão, com a frase que diz que o ato não se
   desfaz, e "Distribuir as selecionadas", "Consolidar as selecionadas" e "Retirar as selecionadas"
   continuam onde estavam, no mesmo desenho.

---

### User Story 3 — A Comissão com título para quem está nela (Priority: P2)

A presidente abre a Comissão. Abaixo do título, a seção "Membros (3)" traz o filtro e os cartões; as
seções de inclusão vêm depois, como antes. Numa comissão ainda vazia, não há filtro: a seção diz
"Esta comissão ainda não tem membros." e leva a "Adicionar membro", logo abaixo.

**Why this priority**: dá à página a estrutura das outras — título por região, quantidade no título,
estado vazio que diz o que fazer —, sem mudar o que se alcança; as P1 tiram a duplicação e trazem a
saída para cima.

**Independent Test**: a lista de membros está sob um título de seção com a quantidade; sem membro, o
filtro não vem e o estado vazio leva ao formulário de inclusão.

**Acceptance Scenarios**:

1. **Given** uma comissão com três membros, **When** a página abre, **Then** há uma seção "Membros
   (3)" com o filtro e os três cartões, antes de "Adicionar membro".
2. **Given** uma comissão de três membros filtrada para um, **When** a página abre, **Then** o título
   continua "Membros (3)", e a linha "1 de 3 membros." continua dizendo o recorte.
3. **Given** uma comissão sem membro, **When** a página abre, **Then** o filtro não aparece, o estado
   vazio diz "Esta comissão ainda não tem membros." e leva a "Adicionar membro", na mesma página.
4. **Given** um filtro sem resultado, **When** a página abre, **Then** o filtro continua, para ser
   desfeito, e o estado vazio diz "Nenhum membro corresponde ao filtro.", como antes.

---

### User Story 4 — A ação principal da Alocação diz o que faz (Priority: P3)

O presidente marca duas pessoas na coluna de uma Etapa e aperta "Salvar alocação". A tela responde
"Alocação salva.", como antes.

**Why this priority**: corrige um rótulo que contradiz a decisão de vocabulário da própria tela; não
muda o que o botão faz, onde está nem quando aparece.

**Independent Test**: com presidência designada e membros na matriz, o botão diz "Salvar alocação";
sem presidência, não há botão, como antes.

**Acceptance Scenarios**:

1. **Given** a Alocação com presidência e membros, **When** a página abre, **Then** o botão depois da
   matriz diz "Salvar alocação", no mesmo lugar e no mesmo desenho.
2. **Given** a Alocação sem presidência, **When** a página abre, **Then** não há botão de salvar, e o
   aviso da presidência continua.

### Edge Cases

- **Trilha longa no celular.** A da Distribuição e a da conferência têm cinco níveis, e o nome da
  Etapa pode ser longo. A 375 px a trilha quebra a linha dentro do cabeçalho; nem ela nem "Trocar
  identidade" estouram a largura.
- **A Alocação no celular e na tela larga.** O cabeçalho de contexto fica acima da matriz, fora da
  moldura dela; a barra continua no topo, sem prender. A trilha não tira largura da matriz, porque o
  cabeçalho de contexto já estava lá.
- **Alocação sem Edital publicado, ou sem Etapa.** O estado vazio continua como está; só a trilha sobe.
- **Alocações sem Etapa correspondente.** A seção, com "Remover", continua onde está, no mesmo
  desenho: é ação, e não lugar.
- **Distribuição com o período de inscrições em curso, ou com a Etapa que não pode ser consolidada.**
  Os avisos continuam onde estão, antes dos números a que se referem.
- **Distribuição depois de uma consolidação.** O desfecho agrupado continua onde está, junto dos
  números de prontidão que ele muda.
- **Comissão sem presidente.** O aviso continua logo depois da faixa, antes dos membros: é a situação
  da comissão, e não uma ação.
- **Comissão filtrada só por "sem Etapa", sem ninguém nessa condição.** O filtro continua, porque há
  membros; o estado vazio é o do filtro.
- **A conferência da lista.** A tabela, as pastilhas "será incluída" e "já integra a comissão" e os
  dois botões não mudam; só a trilha sobe.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de
  baixo dele continuam identificando o Processo e a Etapa impressos.
  *Substituído pela [`088`](../088-decisoes-da-etapa-4/spec.md) em 18/10/2026, por decisão do
  usuário*: a trilha do cabeçalho de contexto sai no papel; ficam fora só a barra e "Trocar
  identidade".

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no cabeçalho de contexto

- **FR-1780**: Na Comissão do Processo, na conferência da inclusão, na Alocação por Etapa e na
  Distribuição de uma Etapa, o cabeçalho de contexto MUST mostrar a trilha da tela, como navegação
  nomeada: o produto, cada nível acima da tela como link, e a própria tela como a página atual —
  como nas telas da `077` e da `078` (`FR-1746` da `077`, `FR-1767` da `078`).
- **FR-1781**: Nessas quatro telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter
  uma trilha só, e o conteúdo MUST começar pelo título. Os níveis e os rótulos MUST ser os que cada
  tela já mostrava, precedidos do produto — na Distribuição, os da Alocação por Etapa, como a Etapa
  aberta pela gestão (`FR-1752` da `077`).
- **FR-1782**: Nas demais telas da gestão — fora das da `077`, da `078` e destas —, inclusive as que
  se abrem a partir da Distribuição, o cabeçalho de contexto MUST continuar o da `076`, e a trilha
  MUST continuar no conteúdo (`FR-1769` da `078`).
  *Emendada pela [`080`](../080-telas-filhas-da-distribuicao/spec.md) em 17/10/2026*: Impedimentos,
  Registrar ocorrência, Resultados, Trilha da avaliação, as Conclusões preservadas, a conferência da
  retirada e a Auditoria da comissão também passaram a ter a trilha no cabeçalho (`FR-1800` da
  `080`). "As demais telas" são, daí em diante, as que nem a `077`, nem a `078`, nem esta, nem a
  `080` nomeiam — entre elas, a Auditoria do Edital (`FR-1803` da `080`). *Emendada de novo pela
  [`083`](../083-telas-do-edital/spec.md) em 18/10/2026*: a Auditoria do Edital e as outras onze telas
  que se abrem do detalhe do Edital passaram ao cabeçalho (`FR-1850` da `083`).
- **FR-1783**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.
- **FR-1784**: Na Alocação por Etapa, a barra MUST continuar recolhida em qualquer largura (DP-4 da
  `076`), e a matriz MUST continuar como a `FR-1062` da `057` a rege — sem rolagem interna na tela
  larga, com o cabeçalho dela preso à janela.

#### Os lugares da Etapa, na Distribuição

- **FR-1785**: Na Distribuição, a faixa dos lugares da Etapa — Impedimentos, Registrar ocorrência,
  Resultados e Trilha — MUST vir logo depois do título, do Edital e das mensagens sobre o último envio,
  antes da ficha da Etapa. Os links MUST continuar os mesmos, na mesma ordem e no mesmo desenho.
- **FR-1786**: Nenhuma ação da Distribuição MUST mudar de lugar, de desenho ou de rótulo:
  consolidar as prontas, propor e confirmar a distribuição, distribuir e consolidar as selecionadas e
  retirar atribuições continuam onde estão, com as frases que as precedem (`FR-422` da `030`). Os
  avisos e os desfechos que se referem aos números da Etapa MUST continuar junto deles.

#### A Comissão

- **FR-1787**: Na Comissão, os membros MUST vir numa seção com título, que diz quantos são na comissão
  inteira, e que reúne o filtro e a lista; as seções de inclusão MUST continuar depois dela.
- **FR-1788**: Sem membro na comissão, o filtro MUST NOT aparecer, e o estado vazio MUST dizer "Esta
  comissão ainda não tem membros." e levar a "Adicionar membro", na mesma página. Com membro, o filtro
  MUST continuar como está, inclusive quando o recorte não traz ninguém ("Nenhum membro corresponde ao
  filtro.").
- **FR-1789**: Na conferência da inclusão, a tabela, as pastilhas, o texto e os botões MUST continuar
  os mesmos.

#### A Alocação

- **FR-1790**: Na Alocação por Etapa, o botão que grava a matriz MUST dizer "Salvar alocação", no
  mesmo lugar, no mesmo desenho e nas mesmas condições — com presidência e com membros.

#### O que não pode piorar

- **FR-1791**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; e só as telas desta
  feature MUST mudar de largura ou de altura.
- **FR-1792**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário e
  bytes que já varrem a gestão — o link de salto, o `main`, toda classe com regra na folha, a ação
  principal com o desenho de ação principal (`FR-1008` da `055`), e o teto de 120 000 caracteres da
  Distribuição.

### Key Entities

Nenhuma. Só apresentação.

## Success Criteria *(mandatory)*

- **SC-690**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e
  **nenhuma** muda de `status`, nos dois estados da barra.
- **SC-691**: Fora da Comissão, da Alocação e da Distribuição, **nenhuma** variante muda de largura ou
  de altura.
- **SC-692**: Nas quatro telas da presidência, "onde estou" aparece **uma** vez por página, no
  cabeçalho de contexto, e cada nível acima da tela está a **um** clique.
- **SC-693**: Na Distribuição do inventário, a faixa dos lugares da Etapa sobe **mais de 300 px** a
  1280 px de janela e **mais de 500 px** a 375 px, e deixa de depender do tamanho da banca.
- **SC-694**: A Distribuição no cenário de escala continua **abaixo de 120 000** caracteres, e a
  diferença para antes fica medida e registrada.
- **SC-695**: A suíte contra PostgreSQL continua sem falhas.
- **SC-696**: O percurso da presidência — entrar como presidente, abrir a Comissão, alocar e
  distribuir — é feito só pelo teclado, com foco visível, a 1280 e a 375 px.

## Assumptions

- "Telas da presidência" são as do pedido: a Comissão do Processo e a conferência da inclusão, a
  Alocação por Etapa e a Distribuição. As telas que se abrem a partir da Distribuição — Impedimentos,
  Registrar ocorrência, Resultados, Trilha, as conclusões preservadas e a retirada de atribuições — e
  a auditoria da comissão ficam para outro incremento, com o cabeçalho da `076`.
- A conferência da inclusão não está no inventário visual: ela é a resposta a um envio, e o inventário
  só abre telas pelo endereço. É provada pelos testes e no navegador.
- "Ação principal evidente" é, como na `078`, a posição e o nome do que já existe, e não um segundo
  botão. Na Comissão e na Distribuição, "Filtrar" continua com o desenho de ação principal: a `055` o
  decidiu assim (`FR-1008`), e mudá-lo aqui reabriria aquela decisão. Na Distribuição, cada ação
  continua no lugar em que a frase que a explica está (`FR-1786`).
- A faixa da Distribuição leva a telas, e não pratica ato nenhum: Registrar ocorrência leva a uma tela
  com conteúdo e confirmação próprios, onde o ato acontece. Mover o link não move o ato.
- O título dos membros conta a comissão inteira, e não o recorte: o recorte já tem a linha dele, e um
  título que muda com o filtro diria duas coisas diferentes com o mesmo rótulo.
- O produto no começo da trilha é a sigla GPS, como na `076`, na `077` e na `078`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
