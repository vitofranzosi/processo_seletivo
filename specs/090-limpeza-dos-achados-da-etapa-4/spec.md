# Feature Specification: A limpeza dos achados da etapa 4

**Feature Branch**: `claude/limpeza-achados-090-a308bc`, especificada sobre a `main` em `46c374cc` (com a
`088`) e implementada sobre `21e36bd4`, com a [`089`](../089-folha-estatica-da-gestao/spec.md)

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: os quatro achados menores que as revisões e as pesquisas da etapa 4 registraram e não
corrigiram, que o usuário pediu em 18/10/2026 que virassem um incremento de limpeza. Cada um sai daqui
com destino explícito — corrigido, com requisito e teste, ou registrado, com o motivo. A linha de base
visual é o [inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), refeito sobre a
`main` com a `089`, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec usa FR-2060 a FR-2072 e SC-800 a SC-806, do começo da faixa
> reservada para ela — trinta números de FR a partir de FR-2060 e dez de SC a partir de SC-800 —, acima
> da faixa da `089`, medida na `main` e no PR 306 em 18/10/2026.

---

## Por que esta feature existe

**O leitor de tela anuncia "irreversível" num lugar só.** A `081` fez a marca "irreversível" descrever
as duas consolidações da Distribuição (`FR-1827` da `081`): quem chega ao botão pelo teclado ouve a
marca junto do rótulo. O desenho que ela copiou — o dos atos do Processo e do Edital — continua com a
marca solta ao lado: "Encerrar Processo", "Cancelar Processo", "Publicar", "Encerrar" e "Cancelar" do
Edital são anunciados só pelo rótulo, e a diferença entre rotina e ato sem volta, para quem não vê, some
justamente nos atos de maior consequência do sistema. A segunda revisão do PR da `081` registrou o
achado (R-008 da pesquisa da `081`). O detalhe da Retificação, com "Publicar Retificação" e "Cancelar
Retificação", tem o mesmo desenho e o mesmo defeito.

**Quem só audita recebe da trilha dois caminhos que não abrem.** Resultados da Etapa, Trilha da
avaliação e Conclusões preservadas abrem para quem preside e para quem audita; a trilha delas leva à
Alocação por Etapa e à Etapa, que respondem **403** a quem audita sem presidir (medido pela `080` em
17/10). A `080` aceitou isso por escrito (a decisão 003 da `080`) porque o pedido dela proibia mudar
view, e a `FR-1804` da `080` fixou que a trilha é a mesma para os dois. A `083` resolveu o mesmo problema
nas telas do Edital com o padrão **nomear não é abrir**: o nível aparece para todos, e é link só para
quem pode abri-lo.

**A 375 px, os botões do rodapé dos formulários quebram o rótulo, e não a linha.** O rodapé comum
(`.salvar`) é uma linha flexível que não quebra. Quando os botões não cabem lado a lado, eles encolhem,
e cada rótulo vai a duas linhas — na conferência da interrupção de um aviso, "Interromper o envio" e
"Voltar sem interromper" viram dois blocos de duas linhas cada (+46 px, achado do code review da `086`).
Nada estoura; o texto quebrado no meio de um botão é que se lê mal.

**A prévia do aviso aberta pelos Resultados divulgados volta aos Avisos aos candidatos.** "Avisar
candidatos" aparece em dois lugares: nos Avisos aos candidatos do Edital e nos Resultados divulgados do
marco. A prévia não sabe por onde se chegou, e a trilha e "Cancelar" levam sempre aos Avisos — a quem
veio do marco, a prévia devolve a uma tela que não viu (R-006 da pesquisa da `086`). A `086` já distingue
três portas da prévia — resultado, chamada e reenvio —, e esta é a quarta.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel ou
fluxo. Nenhuma porta de autorização decide diferente; nenhum ato, nenhum aviso, nenhum destinatário,
nenhuma mensagem de domínio muda. Nenhum rótulo de ação. Nenhuma dependência nova.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O ato sem volta é anunciado como tal (Priority: P1)

Uma servidora que usa leitor de tela abre o detalhe de um Processo e percorre as ações pelo Tab. Em
"Encerrar Processo", o leitor diz o rótulo e, em seguida, "irreversível". O mesmo em "Cancelar
Processo", nos atos sem volta do Edital e nos da Retificação. Quem vê a tela não nota diferença
nenhuma.

**Why this priority**: é o único achado sobre ato de consequência; e é a extensão de um requisito que
já vale numa tela.

**Independent Test**: em cada um dos três detalhes, todo ato marcado como irreversível tem a marca como
descrição acessível; nenhum outro ato tem; o desenho, o rótulo e o destino não mudam.

**Acceptance Scenarios**:

1. **Given** o detalhe de um Processo com "Encerrar Processo" e "Cancelar Processo" disponíveis,
   **When** o foco chega a cada um, **Then** a descrição acessível dele é "irreversível".
2. **Given** o detalhe de um Edital em elaboração com "Publicar" disponível, **When** o foco chega a
   ele, **Then** a descrição acessível dele é "irreversível"; as ações que se desfazem não têm descrição.
3. **Given** um ato do Edital indisponível, **When** a página abre, **Then** ele continua desabilitado e
   descrito pelo motivo, como antes, e sem marca.
4. **Given** o detalhe de uma Retificação com "Publicar Retificação" disponível, **When** o foco chega a
   ele, **Then** a descrição acessível dele é "irreversível".

---

### User Story 2 — A trilha não oferece porta fechada (Priority: P1)

Um auditor sem presidência abre os Resultados da Etapa de um Edital. A trilha diz, como sempre,
Processos Seletivos › o Processo › Alocação por Etapa › a Etapa › Resultados; mas "Alocação por Etapa"
e o nome da Etapa são texto, sem link — ele não pode abrir aquelas telas, e a trilha não o convida a
tentar. O Processo continua link, porque ele o abre. A presidente do mesmo Processo, na mesma tela, lê a
trilha com os quatro links.

**Why this priority**: hoje a trilha leva quem audita a duas recusas; é a única mudança de
comportamento do incremento, e emenda um requisito escrito.

**Independent Test**: nas três telas, com quem preside, os níveis da Alocação e da Etapa são links; com
quem só audita, são texto; para os dois, todo link da trilha abre (status 200) quando seguido pela mesma
pessoa; a contagem de consultas de cada tela não muda.

**Acceptance Scenarios**:

1. **Given** quem preside o Processo, **When** abre Resultados, Trilha da avaliação ou Conclusões
   preservadas, **Then** a trilha tem a Alocação por Etapa e a Etapa como links, como antes.
2. **Given** quem só audita, **When** abre qualquer das três, **Then** a trilha tem os mesmos níveis, na
   mesma ordem e com os mesmos rótulos, e a Alocação por Etapa e a Etapa são texto, sem link.
3. **Given** qualquer das duas pessoas, **When** segue cada link da trilha, **Then** nenhum responde
   recusa.
4. **Given** quem gere comissões pela permissão sistêmica, sem presidir, **When** abre as três, **Then**
   os dois níveis são links, porque ele abre as duas telas.

---

### User Story 3 — O rodapé quebra a linha, não o rótulo (Priority: P2)

No celular, a gestora abre a conferência da interrupção de um aviso. "Interromper o envio" ocupa uma
linha, com o rótulo inteiro; "Voltar sem interromper" vem logo abaixo, também inteiro. No computador,
nada muda: os dois botões continuam lado a lado.

**Why this priority**: legibilidade, sem risco de ato errado; mas a regra é comum e alcança todas as
telas com o rodapé dos formulários, e por isso a prova é o inventário inteiro.

**Independent Test**: o rodapé comum quebra a linha entre os botões; no inventário, a 1280 px nenhuma
variante muda de medida, e a 375 px só mudam de altura as que têm o rodapé com mais de um elemento que
não cabem lado a lado.

**Acceptance Scenarios**:

1. **Given** a conferência da interrupção a 375 px, **When** a página abre, **Then** cada botão do
   rodapé tem o rótulo numa linha, e o segundo vem abaixo do primeiro.
2. **Given** qualquer tela com o rodapé comum a 1280 px, **When** a página abre, **Then** o rodapé tem o
   mesmo desenho e a mesma medida de antes.
3. **Given** um rodapé com um botão só, **When** a página abre em qualquer largura, **Then** nada muda.

---

### User Story 4 — A prévia volta para onde se veio (Priority: P2)

O publicador abre os Resultados divulgados de um marco, vê a publicação vigente ainda não avisada e
aperta "Avisar candidatos". Na prévia, a trilha diz Processos Seletivos › o Processo › o Edital ›
Classificação › Resultados divulgados › Avisar candidatos; "Cancelar" leva de volta aos Resultados
divulgados daquele marco. Se ele troca o modelo de texto, atualiza a prévia ou recebe uma recusa ao
enviar, a trilha continua a mesma. Quem abriu a prévia pelos Avisos aos candidatos continua vendo a
trilha dos Avisos.

**Why this priority**: navegação; nada no aviso muda.

**Independent Test**: a prévia aberta pelo link dos Resultados divulgados tem, acima da tela, os
Resultados divulgados do marco, e "Cancelar" leva a eles; a mesma prévia aberta pelos Avisos aos
candidatos tem a trilha de antes; o universo, o texto e a confirmação são os mesmos nas duas.

**Acceptance Scenarios**:

1. **Given** os Resultados divulgados de um marco com resultado não avisado, **When** a pessoa aperta
   "Avisar candidatos", **Then** a prévia tem os Resultados divulgados como nível acima e "Cancelar"
   leva a eles.
2. **Given** essa prévia, **When** a pessoa usa outro modelo, atualiza a prévia ou envia e recebe uma
   recusa, **Then** a trilha e "Cancelar" continuam levando aos Resultados divulgados.
3. **Given** os Avisos aos candidatos, **When** a pessoa aperta "Avisar candidatos", **Then** a prévia
   tem a trilha de antes.
4. **Given** a prévia de qualquer das duas portas, **When** a pessoa confirma, **Then** o aviso gravado
   é o mesmo, e a tela seguinte é o histórico do aviso, como antes.

### Edge Cases

- **Quem preside e audita.** É presidência: os níveis são links.
- **Quem preside outro Processo e audita este.** Não preside este: os níveis são texto.
- **A marca de ato indisponível.** Ato do Edital desabilitado não tem marca, e continua descrito pelo
  motivo.
- **O rodapé dentro do filtro.** "Filtrar" e "Limpar" já cabem lado a lado a 375 px; a quebra só
  aparece se não couberem.
- **O rodapé com frase.** Nas conferências da consolidação e da retirada sem nada a fazer, o rodapé
  tem uma frase e um link; a frase passa a ocupar a linha dela, e o link vem abaixo.
- **Endereço da prévia guardado ou aberto noutra aba.** A porta é dita pelo endereço, e não pela tela
  anterior do navegador: o mesmo endereço dá a mesma trilha.
- **Porta desconhecida, ou que quem lê não abre.** A prévia cai na trilha dos Avisos aos candidatos,
  que todo mundo que avisa abre.
- **Os Resultados divulgados para quem não abre a Classificação.** O nível "Classificação" é texto, como
  na trilha dos próprios Resultados divulgados.
- **A prévia de chamada e a de reenvio.** Não mudam: as portas delas já são as de onde se abrem.
- **Impressão.** A trilha sai no papel (`088`); o nível em texto sai como texto.

## Requirements *(mandatory)*

### Functional Requirements

#### A marca "irreversível" para quem não a vê

- **FR-2060**: No detalhe do Processo, no detalhe do Edital e no detalhe da Retificação, todo ato
  disponível que não se desfaz MUST ser descrito, para a tecnologia assistiva, pela marca "irreversível"
  que o acompanha: quem chega a ele pelo teclado ou pelo leitor de tela MUST ouvir "irreversível" junto
  do rótulo, como na Distribuição (`FR-1827` da `081`). Nenhum outro ato dessas telas MUST ter a marca
  como descrição.
- **FR-2061**: O rótulo, o destino, o desenho e o lugar dos atos, e o texto e o desenho da marca, MUST
  continuar os mesmos. O ato indisponível do Edital MUST continuar desabilitado e descrito pelo motivo,
  sem marca.

#### A trilha das consultas da Etapa

- **FR-2062**: Em Resultados da Etapa, Trilha da avaliação e Conclusões preservadas, os níveis da
  Alocação por Etapa e da Etapa MUST ser link para quem pode abrir aquelas telas, e texto sem link para
  quem não pode — os mesmos níveis, na mesma ordem e com os mesmos rótulos para todos.
- **FR-2063**: Nenhum link da trilha dessas três telas MUST levar a uma tela que recuse quem a lê.
- **FR-2064**: Quem pode abrir os dois níveis MUST ser decidido pela mesma regra das portas da Alocação
  e da Distribuição — gerir a comissão do Processo, pela permissão sistêmica ou pela presidência —, sem
  mudar nenhuma porta, e as três telas MUST NOT fazer consulta a mais ao banco para decidi-lo.

#### O rodapé dos formulários

- **FR-2065**: O rodapé comum dos formulários MUST quebrar a linha entre os elementos dele quando não
  cabem lado a lado, e não dentro do rótulo de um botão que caberia inteiro na largura.
- **FR-2066**: A 1280 px, nenhuma tela com o rodapé comum MUST mudar de medida; a 375 px, as que mudam
  MUST mudar só de altura.

#### A prévia aberta pelos Resultados divulgados

- **FR-2067**: Na prévia do aviso de resultado aberta pelos Resultados divulgados de um marco, os
  níveis acima da tela MUST ser os da trilha dos Resultados divulgados — o Processo, o Edital, a
  Classificação e os Resultados divulgados —, com a Classificação como link só para quem pode abri-la,
  como lá; e "Cancelar" MUST levar aos Resultados divulgados do mesmo marco.
- **FR-2068**: A porta MUST sobreviver a "Usar este modelo", a "Atualizar a prévia" e à recusa do
  envio; MUST ser dita pelo endereço da prévia; e uma porta desconhecida, ou que quem lê não pode abrir,
  MUST dar a trilha dos Avisos aos candidatos.
- **FR-2069**: A porta MUST NOT mudar o universo, o texto, a confirmação nem a tela seguinte à
  confirmação; a prévia aberta pelos Avisos aos candidatos, a da chamada e a do reenvio MUST continuar
  como antes.

#### O que não pode piorar

- **FR-2070**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; a 1280 px nenhuma
  MUST mudar de medida; a 375 px, só as que têm o rodapé comum MUST mudar, e só de altura.
- **FR-2071**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário e
  folha que já varrem a gestão, e pelo inventário de negativas da `033`.
- **FR-2072**: Os requisitos que esta feature contraria MUST ser anotados como emendados na spec de
  origem: a `FR-1800` e a `FR-1804` da `080`, e a `FR-1942` e a `FR-1946` da `086`.

### Key Entities

Nenhuma. Só apresentação e navegação.

## Decisões

| Achado | Origem | Destino |
|---|---|---|
| A marca "irreversível" sem descrição acessível no Processo e no Edital | R-008 da pesquisa da `081` | corrigido — `FR-2060`, `FR-2061`; D-001 |
| Quem só audita vê na trilha Alocação e Etapa, que respondem 403 | decisão 003 e pesquisa da `080` | corrigido — `FR-2062` a `FR-2064`; D-002 |
| `.salvar` não quebra a linha a 375 px | code review do PR da `086` | corrigido — `FR-2065`, `FR-2066`; D-003 |
| A prévia aberta pelo marco volta aos Avisos | R-006 da pesquisa da `086` | corrigido — `FR-2067` a `FR-2069`; D-004 |

### D-001 — A Retificação entra com o Processo e o Edital

O achado nomeia o detalhe do Processo e o do Edital. O detalhe da Retificação tem o mesmo desenho — o
ato, a marca solta ao lado — e o mesmo defeito, e a correção é a mesma linha. Deixá-lo de fora faria
desta feature o que a `081` foi para as outras duas: uma tela corrigida e a vizinha registrada.

### D-002 — Nomear não é abrir, também nas consultas da Etapa

A `FR-1804` da `080` diz que "nenhum nível MUST aparecer, sumir ou deixar de ser link conforme quem
lê", e a `FR-1800` da `080`, que cada nível acima da tela é link. Os dois foram escritos para que a
trilha não mudasse de forma por papel; e a decisão 003 da `080` já registrava o custo — oferecer a quem
audita duas portas que respondem 403 — e o motivo de não corrigi-lo ali: pedia à view uma informação
que ela não entregava, e o pedido proibia mudar view. A `083` resolveu o mesmo conflito nas telas do
Edital pelo padrão *nomear não é abrir*: o nível aparece para todos, no mesmo lugar e com o mesmo
rótulo, e é link só para quem pode abri-lo. Esta feature aplica o mesmo padrão e emenda as duas FRs
só nesse ponto: nada aparece nem some conforme quem lê; deixar de ser link passa a ser exigido para
quem não abre o destino. A informação vem da porta que as três telas já atravessam, que já pergunta se
quem lê gere a comissão — e por isso não custa consulta.

### D-003 — A quebra vai na regra comum, e não tela a tela

A `086` deixou o achado para "quem decidir mexer na regra geral". Corrigir só a interrupção trataria o
sintoma numa tela das dezoito que usam o rodapé; corrigir a regra comum resolve todas, ao custo de uma
prova maior — o inventário inteiro, nas duas larguras e nos dois estados da barra, de onde sai que nada
muda a 1280 px.

### D-004 — A porta é dita pelo endereço

A prévia poderia descobrir de onde se veio pela página anterior do navegador. Mas o navegador nem
sempre a informa, e o mesmo endereço, aberto noutra aba ou guardado, daria trilhas diferentes. O link
dos Resultados divulgados passa a dizer a porta no próprio endereço, como a chamada já diz a lista. Uma
porta que quem lê não pode abrir é ignorada: a trilha não oferece porta fechada (D-002), e os Avisos aos
candidatos abrem para todo mundo que avisa. A Classificação entra na trilha porque é a trilha dos
Resultados divulgados (a regra da `FR-1942` da `086` para o reenvio: o nível acima é a tela de onde se
abre, com a trilha dela); como lá, é link só para quem a abre. Saber isso pede, só nesta porta, a mesma
pergunta que os Resultados divulgados fazem — e é o único lugar desta feature em que uma tela pode
fazer uma consulta a mais, medida no plano. A `FR-1946` da `086` diz, para as telas dos avisos, o que a
`FR-1804` da `080` diz para as consultas da Etapa — nenhum nível deixa de ser link conforme quem lê —, e
é emendada no mesmo ponto e pelo mesmo motivo (D-002).

## Success Criteria *(mandatory)*

- **SC-800**: Dos quatro achados que o usuário pediu, **quatro** têm destino escrito nesta spec.
- **SC-801**: Nos detalhes do Processo, do Edital e da Retificação, os atos irreversíveis anunciados
  como tais pelo leitor de tela passam de **zero** para **todos** os disponíveis, e os demais atos
  continuam sem descrição.
- **SC-802**: Nas três consultas da Etapa, os links da trilha que respondem recusa a quem só audita
  passam de **dois por tela** para **zero**; para quem preside, os links continuam **quatro**.
- **SC-803**: A 375 px, na conferência da interrupção de um aviso, os rótulos de botão do rodapé
  quebrados em duas linhas passam de **dois** para **zero**.
- **SC-804**: A prévia aberta pelos Resultados divulgados passa a ter **um** caminho de volta a eles —
  pela trilha — e "Cancelar" passa a levar a eles.
- **SC-805**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, **nenhuma**
  muda de `status`, e **nenhuma** muda de medida a 1280 px, nos dois estados da barra.
- **SC-806**: A suíte contra PostgreSQL continua sem falhas.

## Assumptions

- Os quatro achados são os do pedido de 18/10/2026: R-008 da `081`, decisão 003 da `080`, o code review
  do PR da `086` e o R-006 da `086`.
- "Pode abrir a Alocação e a Distribuição" é a mesma pergunta das duas portas — gerir a comissão do
  Processo —, e é a única pergunta que as decide; a Etapa da trilha é a Distribuição.
- Os Avisos aos candidatos abrem para todo mundo que pode abrir a prévia do aviso de resultado.
- A implementação parte da `main` com a `089`, em que a regra comum mora na folha estática da gestão.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
