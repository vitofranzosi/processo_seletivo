# Feature Specification: As telas de quem elabora, segundo incremento

**Feature Branch**: `claude/festive-tereshkova-9a826c`, sobre a `main` `a41b67c0` (com a `075`, a
`076` e a `077`)

**Created**: 2026-10-17

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Segundo incremento, depois das telas de uso diário
([`077`](../077-telas-de-uso-diario/spec.md)), com duas frentes: as duas causas latentes que a
`077` registrou no fim da [pesquisa](../077-telas-de-uso-diario/research.md), e as telas de quem
elabora, as mais usadas depois da Mesa. A linha de base visual é o
[inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), no estado
`depois-da-077`.

> **Faixa de identificadores.** Esta spec abre em FR-1760 e SC-680, acima da faixa da `077`
> (FR-1752, SC-675), medida em todas as worktrees em 17/10/2026.

---

## Por que esta feature existe

**As duas causas que a `077` corrigiu tela a tela continuam vivas na folha comum.** Duas das cinco
telas que estouravam a 375 px estouravam por causas que não são delas:

1. **O rótulo invisível que alarga a página.** As tabelas largas rolam dentro de uma moldura. Um
   rótulo que só a tecnologia assistiva lê, posicionado de forma absoluta, toma como referência o
   primeiro ancestral posicionado — e a moldura não é posicionada. Quando ele cai além da borda,
   alarga a página inteira, e não a moldura. Nas conclusões preservadas a página tinha 835 px.
2. **O grupo de campos que cresce até o conteúdo.** Por padrão do navegador, um grupo de campos
   (`fieldset`) não encolhe abaixo da largura mínima do que carrega. Uma tabela larga dentro dele
   nunca chega a rolar na própria moldura, e um campo de arquivo o empurra para fora. Em reaproveitar
   Edital a página tinha 994 px; nos anexos da composição, 432.

A `077` pôs uma regra na folha de cada uma das três telas e registrou a regra geral como decisão de
outro incremento. **Medido em 17/10/2026, antes desta feature**, no banco do inventário:

| | Variantes medidas | Têm a estrutura | Estouram hoje | Caixas que a regra geral move |
|---|---|---|---|---|
| Moldura que rola, sem posição, com elemento absoluto dentro | 84 | **19** (18 a 1280, 19 a 375) | 0 | 0 |
| Grupo de campos | 84 | **14** | 0 | 0 |

As 19 são a Visão Geral (só a 375), reaproveitar, a distribuição, os resultados da Etapa, a
ordenação, o corte e o histórico dele, o ato de ordenação, o sorteio, a prévia de publicação, as
publicações do marco, os recursos, a Etapa da Mesa, os modelos de aviso, os três estados dos avisos
do Edital, o aviso e o reenvio do aviso. As conclusões preservadas, que a `077` já corrigiu, são a
20ª. Nenhuma estoura hoje porque, com os dados do inventário, nenhum rótulo cai além da borda — e
basta uma tabela com uma coluna a mais, ou um nome mais longo, para que caia. A regra geral não move
caixa nenhuma em nenhuma das 84 variantes: muda só a referência do que um dia estourar.

**As telas de quem elabora são as últimas do dia a dia com a trilha dentro do conteúdo.** Quem
elabora passa o dia entre três lugares: o Processo, o Edital e a composição do Edital. Nos três, o
cabeçalho de contexto diz *GPS › Processos Seletivos*, e logo abaixo, dentro do conteúdo, a tela
repete o caminho em outra linha — a duplicação que a `077` resolveu nas telas de uso diário. E a
ação que o fluxo pede fica longe:

- **No detalhe do Processo**, o cartão "O que fazer agora" — com "Elaborar o Edital", quando há um
  para elaborar — vem depois de "Onde cada Edital está", que no Processo do inventário tem 1250 px
  de altura a 1280 px de janela. A ação está a dois terços da página.
- **No detalhe do Edital**, "O que fazer agora" é a segunda coluna. A 375 px as colunas empilham, e
  ela desce para baixo de "Quem atuou" — a história do Edital vem antes do que fazer com ele.
- **Os Editais do Processo** são uma lista corrida — número, título e situação numa linha que quebra
  onde der —, enquanto a lista de Processos, que mostra os mesmos Editais, já os mostra em tabela,
  com colunas. E o Processo sem Edital diz "Nenhum Edital." num item de lista, e não no estado vazio
  das outras telas.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel
ou fluxo. Nenhum endereço. Nenhum conteúdo normativo: os mesmos atos, as mesmas ações, os mesmos
avisos, as mesmas pendências, os mesmos valores. Nenhuma tela fora das nomeadas aqui, salvo as que
a regra geral alcançar — e nessas, nada que se veja.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Nenhuma tela volta a rolar para o lado pelas mesmas causas (Priority: P1)

Uma presidente de comissão abre, no celular, a ordenação de um marco com mais Perfis do que o
Edital do inventário. A tabela é larga e tem, em cada linha, um rótulo que só o leitor de tela lê.
Hoje o rótulo da última coluna pode cair além da borda e fazer a página inteira rolar para o lado.
Com a correção, a tabela rola dentro da própria moldura, como foi desenhada para rolar, e a página
fica com a largura da janela.

**Why this priority**: a `077` provou que estouro de largura é defeito, e não gosto — estraga a tela
inteira, e não só o trecho largo. Corrigir na causa impede que as próximas telas, e os próximos
dados, o tragam de volta.

**Independent Test**: a regra está na folha comum, as três regras pontuais da `077` saíram das
telas, e o inventário refeito mostra as três telas que elas corrigiam com a largura da janela a
375 px; nenhuma outra variante muda de largura ou de altura.

**Acceptance Scenarios**:

1. **Given** qualquer tela da gestão com uma tabela larga em moldura que rola, **When** um elemento
   posicionado de forma absoluta cai além da borda da janela dentro da moldura, **Then** quem rola é
   a moldura, e não a página.
2. **Given** qualquer grupo de campos da gestão com conteúdo mais largo que a janela, **When** a tela
   abre a 375 px, **Then** o grupo cabe na largura, e o que é largo rola na própria moldura.
3. **Given** as conclusões preservadas, reaproveitar Edital e os anexos da composição, sem as regras
   que a `077` pôs na folha de cada uma, **When** abrem a 375 px, **Then** cabem na janela, como
   cabiam com elas.
4. **Given** qualquer outra variante do inventário, **When** abre a 375 ou a 1280 px, **Then** tem a
   mesma largura e a mesma altura de antes.

---

### User Story 2 — O que fazer, antes do resto (Priority: P1)

Uma elaboradora abre o Processo em que trabalha. Logo abaixo do título e da situação estão o cartão
"O que fazer agora" — com "Elaborar o Edital 76/2027" — e a tabela dos Editais do Processo. O pulso
das inscrições e a Atenção vêm depois. Ela abre o Edital: "O que fazer agora", com a ação que o
fluxo pede, vem antes de "Quem atuou", na tela larga e no celular.

**Why this priority**: é a pergunta com que se abre a tela — "o que eu faço aqui?" — e hoje a
resposta está a dois terços da página do Processo, e abaixo da história do Edital no celular.

**Independent Test**: no detalhe do Processo e no do Edital, a região "O que fazer agora" é a
primeira das regiões de conteúdo depois da situação; nada nela muda; a 375 px ela é a primeira a
aparecer depois da situação.

**Acceptance Scenarios**:

1. **Given** um Processo com um Edital em elaboração, aberto por quem pode elaborá-lo, **When** a
   página abre, **Then** "O que fazer agora" vem antes dos Editais e de "Onde cada Edital está", com
   "Elaborar o Edital" no mesmo lugar dentro do cartão.
2. **Given** um Processo ativo, aberto pelo gestor, **When** a página abre, **Then** o cartão traz os
   mesmos atos de antes — Encerrar e Cancelar contornados, por último, com "irreversível" — e o
   mesmo aviso de impedimento depois deles.
3. **Given** um Edital aberto por qualquer papel, **When** a página abre, **Then** "O que fazer agora"
   vem antes de "Quem atuou", com as mesmas ações, no mesmo peso e na mesma ordem, e as duas colunas
   continuam alinhadas pelo topo.
4. **Given** um papel sem ato nenhum, **When** abre o Processo ou o Edital, **Then** o cartão continua
   dizendo "Nenhum ato disponível para seus papéis nesta situação.", agora em primeiro.

---

### User Story 3 — Onde estou, dito uma vez só, também para quem elabora (Priority: P2)

A elaboradora está na etapa Cronograma da composição do Edital 76/2027. No topo, o cabeçalho de
contexto diz *GPS › Processos Seletivos › PS-DEMO-2026-R › Edital 76/2027 › Compor*, e cada nível
acima da tela leva a ele — inclusive o Processo, que a trilha da composição pulava. O conteúdo
começa pelo título.

**Why this priority**: orienta e tira uma linha repetida das telas que quem elabora mais abre; as P1
corrigem defeito e trazem a ação para cima.

**Independent Test**: no detalhe do Processo, no do Edital e em cada etapa da composição, o caminho
está no cabeçalho de contexto, com um link por nível acima da tela e a tela como página atual; o
conteúdo não tem trilha; a página tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** o detalhe de um Processo, **When** a página abre, **Then** o cabeçalho mostra *GPS ›
   Processos Seletivos › código do Processo*, com Processos Seletivos como link e o código como a
   página atual, e o conteúdo começa pelo título.
2. **Given** o detalhe de um Edital, **When** a página abre, **Then** o cabeçalho mostra *GPS ›
   Processos Seletivos › código do Processo › Edital número/ano*.
3. **Given** qualquer etapa da composição, **When** a página abre, **Then** o cabeçalho mostra *GPS ›
   Processos Seletivos › código do Processo › Edital número/ano › Compor*, e o passo atual continua
   marcado na navegação das etapas, como antes.
4. **Given** qualquer tela da gestão fora das da `077` e destas, **When** ela abre, **Then** o
   cabeçalho continua como na `076` — *GPS ›* e a seção, em texto —, e a trilha continua no conteúdo.

---

### User Story 4 — Os Editais do Processo como a lista os mostra (Priority: P3)

No detalhe do Processo, os Editais aparecem numa tabela — Edital, Título e Situação —, como na lista
de Processos, com o número e o título levando ao Edital e a situação na mesma pastilha. Um Processo
sem Edital mostra o estado vazio das outras telas, com a mesma frase da lista: "Nenhum Edital neste
Processo."; "Novo Edital neste Processo" continua logo abaixo, para quem pode criar.

**Why this priority**: consistência entre duas telas que mostram a mesma coisa; não corrige defeito
nem muda o que se alcança.

**Independent Test**: a região dos Editais tem uma tabela com uma linha por Edital, os mesmos links
e as mesmas pastilhas; sem Edital, o estado vazio.

**Acceptance Scenarios**:

1. **Given** um Processo com três Editais, **When** a página abre, **Then** a região dos Editais tem
   uma tabela com três linhas, cada uma com o número e o título como links para o Edital e a
   situação em pastilha.
2. **Given** um Processo sem Edital, **When** a página abre, **Then** a região mostra "Nenhum Edital
   neste Processo." no estado vazio, e "Novo Edital neste Processo" para quem pode criar.
3. **Given** a tabela a 375 px, **When** a página abre, **Then** a tabela cabe ou rola dentro da
   própria moldura, e a página não rola para o lado.

### Edge Cases

- **Elemento absoluto que alguém quis fora da moldura.** Nenhum hoje: a sonda não achou caixa que a
  regra geral mova. Se um dia uma tela precisar de algo que escape da moldura, a regra da tela o diz
  — e o guardião de larguras aponta o estouro.
- **Grupo de campos que precisava crescer.** Encolher até zero não esconde conteúdo: o que é largo
  passa a rolar na moldura ou a quebrar a linha. Medido: nenhuma caixa muda em nenhuma das 84
  variantes.
- **Cabeçalho fixo da distribuição.** A moldura da matriz da distribuição não pode virar contêiner de
  rolagem na tela larga, porque o cabeçalho fixo deixaria de funcionar (`058`). Ganhar posição não
  muda a rolagem: ela continua sem rolar na tela larga, e o cabeçalho continua fixo.
- **Trilha longa no celular.** A da composição tem cinco níveis. A 375 px ela quebra a linha dentro do
  cabeçalho; nem ela nem "Trocar identidade" estouram a largura.
- **Processo sem Edital e sem quem crie.** O estado vazio aparece sozinho, sem botão: a ação só existe
  para quem pode criar Edital, como hoje.
- **Processo cancelado.** O aviso de cancelamento continua logo depois da situação, antes do cartão
  — é a situação do Processo dita por extenso, e não uma ação.
- **Edital publicado.** O parágrafo do conteúdo imutável e a passagem de bastão continuam no cartão,
  na ordem de antes; só o cartão sobe.
- **Composição somente leitura.** O aviso de somente leitura e o resto da etapa não mudam; só a
  trilha sobe.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título: o caminho fica
  antes, junto da barra, e é pulado com ela.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de
  baixo dele continuam identificando o Processo e o Edital impressos.

## Requirements *(mandatory)*

### Functional Requirements

#### As causas latentes, na folha comum

- **FR-1760**: Toda moldura que rola na gestão MUST ser a referência de posição do que carrega: um
  elemento posicionado de forma absoluta dentro dela MUST alargar a moldura, e nunca a página.
- **FR-1761**: Todo grupo de campos da gestão MUST poder encolher até a largura disponível, abaixo da
  largura mínima do que carrega; o que for largo MUST rolar na própria moldura ou quebrar a linha.
- **FR-1762**: As regras pontuais que a `077` pôs nas conclusões preservadas, em reaproveitar Edital
  e nos anexos da composição para essas duas causas MUST sair das telas; as três MUST continuar
  cabendo na janela a 375 px. As correções da `077` que têm outra causa — o sorteio e o detalhe da
  Retificação — MUST ficar como estão.
- **FR-1763**: Fora das três telas do `FR-1762`, nenhuma variante do inventário MUST mudar de
  largura nem de altura por causa das regras dos `FR-1760` e `FR-1761`.

#### A ação que o fluxo pede, antes do resto

- **FR-1764**: No detalhe do Processo, a região "O que fazer agora" MUST vir antes da região dos
  Editais, e as duas MUST vir antes de "Onde cada Edital está". O conteúdo de cada região MUST
  continuar o mesmo, na mesma ordem interna (`FR-1069` e `FR-1070` da `058`; `FR-556` e `FR-557` da
  `038`).
- **FR-1765**: No detalhe do Edital, a região "O que fazer agora" MUST vir antes de "Quem atuou". As
  ações MUST continuar as mesmas, no mesmo peso e na mesma ordem (`FR-1043` a `FR-1046` da `057`), e
  as colunas MUST continuar alinhadas pelo topo (`FR-1047` da `057`).
- **FR-1766**: A 375 px, nas duas telas, "O que fazer agora" MUST ser a primeira região de conteúdo
  depois da situação e dos avisos sobre ela.
- **FR-1776**: No detalhe do Processo, a faixa das seções do Processo — Supervisão, Comissão,
  Alocação por Etapa, Auditoria da comissão — MUST NOT aparecer, nem vazia, para quem não alcança
  nenhuma delas; para quem alcança, MUST continuar com os mesmos itens, no mesmo lugar (a regra da
  lista na `FR-1741` da `077`).

#### A trilha no cabeçalho de contexto

- **FR-1767**: No detalhe do Processo, no detalhe do Edital e em cada etapa da composição do Edital,
  o cabeçalho de contexto MUST mostrar a trilha da tela, como navegação nomeada: o produto, cada
  nível acima da tela como link, e a própria tela como a página atual — como nas telas da `077`
  (`FR-1746` da `077`).
- **FR-1768**: Nessas telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter uma
  trilha só, e o conteúdo MUST começar pelo título. Os níveis e os rótulos MUST ser os que cada tela
  já mostrava, precedidos da seção; na composição, o Processo MUST entrar entre a seção e o Edital,
  com o mesmo rótulo do detalhe do Edital.
- **FR-1769**: Nas demais telas da gestão — fora das da `077` e destas —, o cabeçalho de contexto
  MUST continuar o da `076`, e a trilha MUST continuar no conteúdo (`FR-1748` da `077`).
- **FR-1770**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.

#### Os Editais do Processo

- **FR-1771**: No detalhe do Processo, os Editais MUST aparecer em tabela, com as colunas Edital,
  Título e Situação, uma linha por Edital, na ordem de hoje; o número e o título MUST levar ao Edital,
  e a situação MUST ser a pastilha de sempre.
- **FR-1772**: Sem Edital, a região MUST mostrar "Nenhum Edital neste Processo." no estado vazio das
  demais telas. "Novo Edital neste Processo" MUST continuar logo abaixo, só para quem pode criar.
- **FR-1773**: A tabela dos Editais MUST rolar dentro da própria moldura quando não couber, e a
  página MUST NOT rolar para o lado.

#### O que não pode piorar

- **FR-1774**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; e só as telas
  desta feature e as três do `FR-1762` MUST mudar de largura ou de altura.
- **FR-1775**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário
  e bytes que já varrem a gestão — o link de salto, o `main`, toda classe com regra na folha, o teto
  da distribuição.

### Key Entities

Nenhuma. Só apresentação.

## Success Criteria *(mandatory)*

- **SC-680**: As duas causas latentes deixam de depender de cada tela: **zero** regras pontuais
  para elas fora da folha comum, e as três telas que a `077` corrigia continuam com a largura da
  janela a 375 px.
- **SC-681**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e
  **nenhuma** muda de `status`, nos dois estados da barra.
- **SC-682**: Fora das telas desta feature e das três da `077`, **nenhuma** variante muda de largura
  ou de altura.
- **SC-683**: No detalhe do Processo e no do Edital, "O que fazer agora" é a **primeira** região de
  conteúdo depois da situação, nas duas larguras; no Processo do inventário, a ação sobe mais de
  1000 px a 1280 px de janela.
- **SC-684**: Nas telas de quem elabora — o detalhe do Processo, o do Edital e as nove etapas da
  composição —, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto, e cada nível
  acima da tela está a **um** clique.
- **SC-685**: A suíte contra PostgreSQL continua sem falhas.
- **SC-686**: O percurso lista → Processo → Edital → composição → de volta pelo caminho é feito só
  pelo teclado, com foco visível, a 1280 e a 375 px.

## Assumptions

- "Telas de quem elabora" são as do pedido: o detalhe do Processo, o detalhe do Edital e as nove
  etapas da composição, que compartilham uma moldura. As telas de atos (submeter, homologar,
  publicar), a prévia, reaproveitar e a Retificação ficam para outro incremento.
- "Moldura que rola" são as molduras da folha comum que rolam na horizontal — a das tabelas largas,
  a da conferência, a da matriz da distribuição, a da tabela da Lista no estreito — e a da tabela da
  Visão Geral, que a própria tela declara.
- A composição não muda além da trilha: a navegação das etapas, o título e a linha da situação já
  são os do detalhe do Edital, e os estados vazios dela já usam o estado vazio comum.
- "Ação principal evidente" é a posição do cartão que já a carrega, e não um segundo botão no
  cabeçalho da página: repetir a ação fora do cartão separaria a ação da passagem de bastão e do
  motivo da indisponibilidade (`FR-1045` da `057`), e duplicaria o que a `077` acabou de deduplicar.
- As seções do Processo na faixa abaixo do título — Supervisão, Comissão, Alocação por Etapa e
  Auditoria da comissão — são lugares do próprio Processo, e não da barra; ficam onde estão. Para
  quem não alcança nenhuma, a faixa era um parágrafo vazio entre o título e a situação, e deixa de
  vir (`FR-1776`), como a da lista na `077`.
- O produto no começo da trilha é a sigla GPS, como na `076` e na `077`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
