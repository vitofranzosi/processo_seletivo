# Feature Specification: Agenda dos Editais — os cronogramas publicados da unidade, num mês e numa lista

**Feature Branch**: `claude/calendario-processos-seletivos-217bea`, sobre a `main` em `0ff70f07`

**Created**: 2026-10-29

**Status**: Draft — implementação do MVP autorizada pelo usuário em 29/10/2026; merge **não**
autorizado.

**Input**: autorização do usuário de 29/10/2026 — *"A decisão é avançar com a funcionalidade,
contemplando a especificação formal, planejamento técnico, implementação, testes e documentação"* —,
sobre o estudo aprovado em
[`doc/estudo-calendario-institucional-2026-10-29.md`](../../doc/estudo-calendario-institucional-2026-10-29.md),
com um ajuste: o **mês** é a visualização inicial, e a lista cronológica é a complementar.

> **Faixa de identificadores.** Esta spec abre em **FR-2609** e **SC-948**. Teto medido em
> 29/10/2026 em `specs/` de todas as worktrees desta máquina, na `main` e nos PRs abertos: `FR-2608`,
> `SC-947`, `UX-222`. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-766 da `047`"); decisão de outra feature, pelo assunto e pela feature, porque `D-` aqui é só
> desta.

---

## Por que esta feature existe

**Cada leitura de datas do sistema é de um Processo ou de um Edital.** A supervisão (`022`) diz os
próximos marcos dos Editais de **um** Processo; a página pública (`047`) diz o cronograma de **um**
Edital; a Visão Geral (`040`), a única leitura entre Processos, diz só o período de inscrições. Quem
coordena uma unidade com vários certames simultâneos não tem onde ver, numa página, como os marcos
de todos se distribuem no mês — e onde se acumulam. A `022` declarou essa visão fora do escopo dela.

**O dado existe, e não precisa ser cadastrado de novo.** Todo Evento publicado tem identidade
estável, início com fuso, término anulável, local, marca de período de inscrições e cancelamento
declarado; a fase dele já é derivada do relógio numa régua única que a gestão e o portal leem. Esta
feature é uma **projeção**: lê o cronograma publicado e vigente e o organiza no tempo.

**E a projeção tem de ser confiável antes de ser bonita.** O cronograma da tela de elaboração diverge
do vigente depois de uma Retificação; uma Retificação pode estar publicada e ainda não vigorar; uma
data prevista que passou não prova que o ato aconteceu. A agenda só serve se nunca disser mais do
que o cronograma publicado diz.

### O que existe e é reaproveitado

| Peça | Onde |
|---|---|
| Conteúdo vigente de vários Editais numa leitura | `publicacoes/application/selectors.py` (`versoes_vigentes`) |
| Fase do Evento, cancelamento, descrição, instantes | `editais/domain/fase_do_evento.py`, `editais/domain/calendario.py` |
| Situação do período de inscrições | `inscricoes/domain/periodo.py` |
| Zona institucional | `shared/tempo.py` |
| Montagem em consultas fixas, filtros na consulta e em memória | `interface/visao_geral.py` (`040`) |
| Barra da gestão por capacidade | `interface/navegacao.py` (`076`) |
| Página pública do Edital, com a seção do cronograma | `portal:selecao` (`024`, `047`) |

### O que esta spec cobre, e o que fica fora

**Cobre**: a página **Agenda dos Editais** na gestão, com as visualizações **Mês** (inicial) e
**Próximos marcos**, a consulta de um dia, a síntese da janela, os filtros de Edital e de espécie do
Evento, o aviso de Retificação a vigorar e a entrada na barra.

**Fica fora**, por decisão do usuário de 29/10/2026:

- criar, editar, concluir ou excluir Evento pela agenda;
- integração com Google Agenda, Outlook ou qualquer calendário externo; exportação `.ics`;
  assinatura de calendário;
- notificação automática; controle de tarefa; atribuição de responsável;
- visão entre unidades;
- classificação de Evento por palavra-chave ou por IA; taxonomia nova de modalidade ou de categoria;
- painel analítico além da síntese;
- prazo **efetivamente aberto** pela publicação de um ato (o recursal) como item da agenda.

---

## Clarifications

### Session 2026-10-29

Nenhuma pergunta foi feita ao usuário: as decisões de produto estavam tomadas no estudo e nas
mensagens de 29/10, e a autorização pede que a execução não pare por pergunta resolvível com
segurança. As cinco lacunas abaixo foram encontradas na varredura e resolvidas pela regra mais
conservadora que o próprio sistema já aplica, registradas aqui para revisão.

- Q: A janela de Próximos marcos começa no instante da leitura ou no começo do dia de hoje? → A: No
  começo do dia de hoje, na zona institucional; o marco de hoje cuja hora já passou aparece como
  *data passada*, porque "o que acontece hoje" inclui a manhã.
- Q: O período de inscrições sem término aparece na lista de períodos de quais meses? → A: De todo
  mês a partir do início, enquanto o Edital estiver publicado — é o que a régua do período diz: ele
  segue aberto.
- Q: Um Evento que é período de inscrições e também está ligado a uma Etapa cai em qual espécie do
  filtro? → A: Em *período de inscrições*; a marca do período é a mais específica, e cada Evento cai
  em uma espécie só.
- Q: No dia consultado, o que são os "períodos em curso naquele dia"? → A: Os períodos cujo intervalo
  contém o dia sem começar nem terminar nele — os que começam ou terminam nele já são marcos do dia.
- Q: Quais Editais recebem o aviso de Retificação a vigorar? → A: Todo Edital considerado pela página
  (depois do filtro de Edital) que tem Retificação publicada com vigência futura, tenha ou não marco
  na janela — a Retificação pode trazer um marco para dentro dela.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Ver como os marcos dos Editais se distribuem no mês (Priority: P1) 🎯 MVP

Quem coordena a unidade abre a Agenda e vê o mês corrente numa grade: em cada dia, quantos marcos
dos cronogramas publicados caem nele, com os dias de dois ou mais marcos destacados. Em tela larga,
cada dia nomeia até dois marcos. Abaixo da grade, os períodos que tocam o mês aparecem uma vez cada,
como intervalos. A pessoa passa para o mês seguinte e para o anterior.

**Why this priority**: é a pergunta que motivou a feature — a visão consolidada do mês de vários
certames simultâneos — e nenhuma tela a responde hoje.

**Independent Test**: com três Editais publicados no escopo, cada um com Eventos pontuais e um
período em novembro, abrir a Agenda em novembro e conferir contagens, destaque, nomes e a lista de
períodos.

**Acceptance Scenarios**:

1. **Given** dois Editais com um Evento pontual cada no dia 12, **When** a pessoa abre o mês, **Then**
   a célula do dia 12 diz *2 marcos* e está destacada, e a do dia de um marco só não está.
2. **Given** um período de inscrições de 03/11 a 15/11, **When** a pessoa abre novembro, **Then** a
   célula de 03/11 contém a abertura, a de 15/11 o encerramento, nenhuma célula entre as duas contém
   o período, e ele aparece uma vez na lista de períodos do mês, como *03/11 a 15/11*.
3. **Given** o mês corrente aberto, **When** a pessoa escolhe o mês seguinte, **Then** a grade, a
   lista de períodos e a síntese passam a ser do mês seguinte.

---

### User Story 2 — Consultar tudo o que cai num dia (Priority: P1)

Na grade, a pessoa escolhe um dia e vê a relação completa dos marcos daquele dia — hora, descrição
oficial, Edital, Processo, local, se é abertura ou encerramento de período —, com o acesso ao
Edital e ao cronograma oficialmente publicado. Vê também os períodos que estão correndo naquele dia.

**Why this priority**: um número sem os itens que ele representa não informa. A célula diz quantos;
o dia diz quais.

**Independent Test**: num dia com cinco marcos de três Editais, escolher o dia e conferir que os
cinco aparecem, cada um com os dois links.

**Acceptance Scenarios**:

1. **Given** um dia com cinco marcos, **When** a pessoa escolhe o dia, **Then** os cinco aparecem,
   com a descrição publicada, o Edital, o Processo e os links *Edital* e *Cronograma publicado*.
2. **Given** um dia sem marco mas dentro de um período, **When** a pessoa escolhe o dia, **Then** a
   página diz que não há marco naquele dia e lista o período em curso nele.
3. **Given** um dia consultado, **When** a pessoa volta ao mês, **Then** volta ao mesmo mês, com os
   mesmos filtros.

---

### User Story 3 — Os próximos marcos, em lista (Priority: P2)

A pessoa troca para **Próximos marcos** e vê os próximos sete dias, dia a dia, com os períodos
abertos agora num bloco próprio no alto. Pode ampliar para trinta dias.

**Why this priority**: responde *"o que acontece nesta semana"* sem leitura de grade, e é a forma
natural no celular.

**Independent Test**: com marcos espalhados pelos próximos 40 dias, conferir que a lista de 7 dias
mostra só os 7 primeiros dias, e a de 30 os 30.

**Acceptance Scenarios**:

1. **Given** um período que abriu antes de hoje e encerra daqui a 10 dias, **When** a pessoa abre
   Próximos marcos com a janela de 7 dias, **Then** ele aparece uma vez no bloco *em curso*, com o
   tempo que falta, e em nenhum dia da lista — nem a abertura nem o encerramento caem na janela.
2. **Given** um Evento cancelado dentro da janela, **When** a pessoa abre Próximos marcos, **Then**
   ele aparece no seu dia identificado como *Cancelado*, e não entra em número nenhum.
3. **Given** a janela de 7 dias sem marco, **When** a pessoa abre Próximos marcos, **Then** a página
   diz que não há marco na janela e nomeia o próximo marco previsto, quando há.

---

### User Story 4 — Filtrar e trocar de visualização sem perder o filtro (Priority: P2)

A pessoa restringe a agenda a um Edital, ou a uma espécie de Evento — período de inscrições, Evento
ligado a Etapa, demais —, e troca entre o mês, o dia e a lista sem perder o filtro.

**Why this priority**: com muitos Editais, o mês inteiro é ruído para quem conduz um só.

**Independent Test**: filtrar por um Edital no mês, trocar para Próximos marcos e para um dia, e
conferir que só os marcos daquele Edital aparecem nas três telas e na síntese.

**Acceptance Scenarios**:

1. **Given** o filtro de um Edital aplicado no mês, **When** a pessoa troca para Próximos marcos,
   **Then** o filtro continua aplicado, e a síntese conta só os marcos dele.
2. **Given** um filtro que não deixa marco nenhum, **When** a página é exibida, **Then** ela diz que o
   filtro não encontrou marcos e oferece limpar os filtros.

---

### User Story 5 — Confiar que é o cronograma publicado e vigente (Priority: P1)

A pessoa precisa saber que a agenda mostra o que os Editais publicaram e que vigora agora — nem
rascunho, nem Retificação ainda não vigente, nem Edital de outra unidade —, e que uma data prevista
não é a prova de que o ato aconteceu.

**Why this priority**: uma agenda que mistura rascunho com publicado, ou previsto com executado, é
pior do que nenhuma: induz a pessoa a agir sobre uma data que ninguém oficializou.

**Independent Test**: um Edital em elaboração com Eventos no mês, um Edital publicado com Retificação
vigente que mudou uma data, e outro com Retificação de vigência futura; conferir o que aparece em
cada caso.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração com Eventos no mês, **When** a pessoa abre a agenda, **Then**
   nenhum marco, contagem ou filtro dele aparece.
2. **Given** uma Retificação publicada e vigente que mudou o início de um Evento, **When** a pessoa
   abre a agenda, **Then** o marco aparece na data nova.
3. **Given** uma Retificação publicada com vigência a partir de daqui a cinco dias, **When** a pessoa
   abre a agenda hoje, **Then** as datas são as vigentes hoje, e um aviso diz que aquele Edital tem
   Retificação publicada que vigora a partir daquela data.
4. **Given** um Edital de outra unidade, **When** a pessoa abre a agenda, **Then** nada dele aparece,
   nem pedindo o Edital pelo filtro.
5. **Given** um marco de *Resultado* cuja data prevista já passou, **When** a pessoa o vê, **Then** a
   página diz que a data prevista passou, e não que o resultado foi publicado.

---

### Edge Cases

- **Evento às 23:30 de 31/12 na zona institucional**: cai em 31/12, na grade de dezembro, e não em
  01/01 — o dia é sempre o da zona, nunca o de UTC.
- **Período que atravessa o mês**: começa em outubro e termina em dezembro. Em novembro ele não tem
  marco nenhum na grade, e aparece na lista de períodos do mês.
- **Período que começa e termina no mesmo dia** (prova das 8h às 12h): é marco pontual, com as duas
  horas, e não período.
- **Período de inscrições sem término declarado**: tem só a abertura, e continua no bloco *em curso*
  como *sem término declarado*. Nunca ganha encerramento inventado.
- **Evento cancelado**: identificado na lista do dia e na de Próximos marcos; fora da grade e de todo
  número. Um dia cujos únicos marcos são cancelados não tem contagem na grade.
- **Edital encerrado com Evento ainda por vir**: o Evento não aparece. O que a instituição encerrou
  não se anuncia.
- **Edital cancelado**: não aparece.
- **Retificação publicada com vigência futura que acrescenta um Evento**: o Evento só aparece a
  partir da vigência; antes, só o aviso.
- **Dia com dez ou mais marcos**: a célula diz a contagem e no máximo dois nomes; o dia consultado
  lista todos, agrupados por Edital.
- **Mês de quatro semanas exatas** (fevereiro de 2026) e **de seis** (agosto de 2026): a grade tem 4
  e 6 linhas.
- **Nenhum Edital publicado no escopo**: a página diz isso e não desenha a grade.
- **Filtro com identificador de Edital de outra unidade, ou inexistente**: é ignorado, sem distinção
  entre os dois.
- **Mês ou dia inválido pedido à página** (um mês 13, um dia que não existe): o mês inválido cai no
  mês corrente, e o dia inválido é ignorado — a página mostra o mês —, sem erro.
- **Evento sem descrição**: o nome é a espécie publicada do Evento, como no portal.

## Requirements *(mandatory)*

### Functional Requirements

#### Acesso e alcance

- **FR-2609**: A gestão MUST oferecer a página **Agenda dos Editais** a toda identidade da gestão,
  pela barra, sem papel novo e sem permissão nova.
- **FR-2610**: A agenda MUST conter só Editais do escopo da unidade do ator. Identificador de Edital
  de outro escopo, ou inexistente, enviado como filtro MUST ser ignorado, sem distinção entre os
  dois, e MUST NOT gerar recusa que revele a existência do Edital.
- **FR-2611**: A agenda MUST ser só de leitura: MUST NOT oferecer controle de criação, alteração,
  conclusão ou exclusão de Evento, nem gravar estado nenhum.

#### Fonte

- **FR-2612**: A fonte MUST ser o cronograma da versão consolidada **vigente** de cada Edital no
  instante da leitura. A agenda MUST NOT ler o cronograma de elaboração, o conteúdo submetido à
  homologação, nem alteração de Retificação não publicada.
- **FR-2613**: Uma Retificação publicada e vigente MUST se refletir na leitura seguinte, sem
  sincronização. Evento acrescentado por Retificação MUST aparecer, e Evento cuja data a Retificação
  mudou MUST aparecer na data nova.
- **FR-2614**: Uma Retificação publicada com vigência futura MUST NOT ser aplicada antes da
  vigência. Enquanto ela não vigora, a página MUST avisar, para cada Edital considerado pela página
  (depois do filtro de Edital) que a tem, a data a partir da qual ela vigora, e que as datas exibidas
  são as vigentes hoje.
- **FR-2615**: Entram Editais **publicados** e **encerrados**. Edital **cancelado** MUST NOT
  aparecer. De Edital encerrado MUST aparecer só Evento cuja data prevista já passou.
- **FR-2616**: O dia de um Evento MUST ser o dia do instante na zona institucional.
- **FR-2617**: A fase de cada Evento — por vir, em curso, data passada — MUST ser a da régua
  existente, com o cancelamento antes da fase e o período de inscrições pela regra do período (`009`),
  sem regra nova.

#### Marcos e períodos

- **FR-2618**: Evento sem término, ou com término no mesmo dia do início, MUST produzir **um** marco,
  no seu dia, com a hora — ou as duas horas, quando há término. O instante à meia-noite exata, sem
  término, é o Edital que declarou só a data: o marco MUST NOT inventar hora para ele.
- **FR-2619**: Evento com término em outro dia é **período**, e MUST produzir dois marcos — a
  **abertura**, no dia do início, e o **encerramento**, no dia do término —, ambos com o intervalo
  escrito. O período MUST NOT ocupar os dias intermediários.
- **FR-2620**: Período sem término declarado MUST produzir só a abertura, e MUST NOT receber
  encerramento presumido.
- **FR-2621**: Evento cancelado MUST aparecer na relação do dia e em Próximos marcos identificado como
  **Cancelado**, com a data publicada; MUST NOT ocupar célula da grade; e MUST NOT entrar em número
  nenhum.
- **FR-2622**: O nome de cada marco MUST ser a descrição publicada do Evento, ou a espécie publicada
  quando a descrição está vazia. A agenda MUST NOT classificar Evento por palavra-chave nem atribuir
  importância a ele.

#### Mês

- **FR-2623**: **Mês** MUST ser a visualização inicial, no mês corrente da zona institucional, com
  navegação para o mês anterior, o seguinte e o corrente.
- **FR-2624**: A grade MUST ter sete colunas, de domingo a sábado, e as semanas que o mês ocupa (de
  quatro a seis); os dias de fora do mês MUST ficar vazios. A grade MUST ser uma tabela com título e
  cabeçalho de colunas.
- **FR-2625**: Cada dia do mês MUST mostrar a data e, quando há marco, a quantidade de marcos, como
  acesso ao dia. Dia com **dois ou mais** marcos MUST ser destacado, e o destaque MUST NOT depender só
  de cor: a contagem fica escrita, em negrito, com borda. O acesso ao dia MUST dizer a data por
  extenso a quem usa leitor de tela. O dia de hoje MUST ser identificado.
- **FR-2626**: Em tela larga, cada dia MUST nomear até **dois** marcos — os dois primeiros na ordem do
  dia (FR-2632) —, cada nome em até duas linhas, com o número do Edital antes do nome e cortado com
  reticências quando não cabe, e dizer quantos mais há. Numa linha só, a prova visual de 29/10 mostrou
  que o número do Edital e *Abre ·* ocupavam a célula inteira, e o nome sumia. Em tela estreita, o dia MUST mostrar só a data e a quantidade.
- **FR-2627**: Abaixo da grade, a página MUST listar uma vez cada período que toca o mês, com o
  nome, o Edital, o intervalo e a fase, em ordem de início. O período de inscrições sem término toca
  todo mês a partir do início. Período cancelado MUST NOT entrar nessa lista nem no bloco *em curso*:
  ele não está correndo, e os marcos dele seguem a FR-2621.

#### O dia

- **FR-2628**: Escolher um dia MUST mostrar todos os marcos daquele dia — inclusive os cancelados,
  identificados — e, à parte, os períodos em curso naquele dia: os que contêm o dia sem começar nem
  terminar nele. Os marcos seguem a ordem do dia (FR-2632), e o título do dia diz quantos são; o dia
  não tem síntese. A página MUST oferecer a volta ao mês daquele dia.
- **FR-2629**: Cada marco listado — no dia ou em Próximos marcos — MUST dizer a data e a hora, a
  descrição publicada, o Edital (número e ano), o Processo Seletivo, o local quando declarado, se é
  abertura ou encerramento de período, *Edital encerrado* quando for o caso, e MUST oferecer o acesso
  ao Edital na gestão e ao cronograma na página pública do Edital.
- **FR-2630**: Um dia com mais de oito marcos MUST agrupá-los por Edital.

#### Próximos marcos

- **FR-2631**: **Próximos marcos** MUST mostrar os próximos sete dias — hoje, desde o começo do dia
  na zona institucional, e os seis seguintes —, e MUST oferecer ampliar para trinta dias.
- **FR-2632**: A lista MUST agrupar os marcos por dia, com a quantidade de marcos no título de cada
  dia — e, quando o dia tem marco cancelado, quantos são os cancelados, porque a quantidade não os
  conta e o item deles está logo abaixo —, e MUST omitir dia sem marco. Dentro do dia, a ordem MUST ser pelo instante, depois pelo Edital
  (ano e número), depois pelo nome — e é a mesma no dia consultado e na célula do mês.
- **FR-2633**: Um bloco **em curso** MUST listar uma vez cada período aberto no instante da leitura,
  com o tempo que falta para o encerramento previsto — em dias corridos até o dia do término na zona
  institucional, ou *encerra hoje* —, ou *sem término declarado*.

#### Síntese

- **FR-2634**: Cada visualização MUST apresentar, sobre a sua janela e os seus filtros, a quantidade
  de **marcos previstos**, de **Editais envolvidos**, de **encerramentos de período** e a
  **concentração** — no mês, quantos dias têm dois ou mais marcos e qual é o mais carregado; em
  Próximos marcos, o dia mais carregado. Os números MUST ser calculados sobre os marcos exibidos, e
  marcos cancelados MUST NOT ser contados.
- **FR-2635**: A soma das quantidades das células do mês MUST ser igual ao número de marcos previstos
  da síntese do mês.
- **FR-2636**: A síntese MUST NOT usar linguagem de carga de trabalho, pendência, atraso ou
  cumprimento.

#### Filtros

- **FR-2637**: A página MUST oferecer filtro por **Edital** e por **espécie do Evento** — *período de
  inscrições*, *ligado a Etapa*, *demais* —, lidos do próprio cronograma publicado, e aplicados da
  mesma forma às duas visualizações, ao dia e à síntese. Cada Evento cai numa espécie só, e o período
  de inscrições prevalece sobre o vínculo com Etapa. As opções de Edital são os Editais considerados
  que têm algum Evento no cronograma vigente; Edital sem Evento não é opção nem conta como envolvido.
- **FR-2638**: Trocar de visualização, de mês, de janela ou escolher um dia MUST preservar os
  filtros. O estado da página MUST estar inteiro no endereço, de modo que um link reproduza a
  mesma tela.
- **FR-2639**: A página MUST NOT oferecer filtro por unidade, modalidade de seleção ou categoria de
  Evento.

#### Previsto × efetivo

- **FR-2640**: A página MUST dizer que as datas são as **previstas** nos cronogramas publicados e
  vigentes, e que o cronograma oficial é o do Edital e de suas Retificações.
- **FR-2641**: A página MUST dizer que prazos contados a partir da publicação de um ato — como o de
  recurso — podem diferir das datas previstas. Ela MUST NOT exibir prazo efetivamente aberto por ato.
- **FR-2642**: Marco cuja data prevista passou MUST ser dito como *data passada*, e MUST NOT ser dito
  concluído, cumprido, realizado ou publicado.

#### Forma

- **FR-2643**: A página MUST declarar o instante da leitura.
- **FR-2644**: A página MUST ter estados próprios para: nenhum Edital com cronograma publicado no
  escopo; janela sem marco, nomeando o próximo marco previsto quando houver — o primeiro marco não
  cancelado depois da janela, com os filtros aplicados —; filtro sem resultado, com a opção de
  limpá-lo.
- **FR-2645**: A página MUST atender ao WCAG 2.1 AA e ao eMAG: estrutura semântica, instante legível
  por máquina, navegação por teclado na ordem do documento, foco visível, aba ativa indicada como
  página atual, contraste, informação que não dependa só de cor, e funcionamento a 375 px de largura
  sem rolagem horizontal da página.
- **FR-2646**: O custo de leitura da página MUST NOT crescer com o número de Editais do escopo, e
  MUST ser o mesmo nas duas visualizações.

### Key Entities

- **Marco** (derivado, não persistido): um ponto da agenda — Evento pontual, abertura de período ou
  encerramento de período —, com o dia na zona institucional, a hora, o Evento de origem, o Edital, a
  fase e a marca de cancelado.
- **Período** (derivado): um Evento com início e término em dias diferentes, ou o período de
  inscrições sem término; dito uma vez, como intervalo.
- **Janela**: o mês, os próximos 7 ou 30 dias, ou um dia — o recorte do tempo de cada visualização.
- **Síntese**: os quatro números de uma janela, calculados dos marcos exibidos.
- **Aviso de Retificação a vigorar**: um Edital da agenda e a data em que a Retificação publicada
  passa a vigorar.

Nenhuma entidade persistida é criada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-948**: Em sessão observada, uma pessoa que gere Processos responde, usando só a agenda, às
  cinco perguntas do estudo — o que acontece nesta semana; quais Processos têm marcos; se há marcos
  concentrados num dia; qual Edital originou um marco; onde consultar o cronograma oficial —, cada
  uma em menos de um minuto.
- **SC-949**: Zero marcos de Edital em elaboração, em revisão, homologado, cancelado ou de outra
  unidade aparecem, em qualquer visualização, nos cenários de teste.
- **SC-950**: O custo de leitura da página é o mesmo com um e com vários Editais publicados, nas duas
  visualizações — verificado por teste com um e com cinco, e medido com trinta.
- **SC-951**: Em todo mês testado, a soma das quantidades das células é igual ao número de marcos da
  síntese, e todo marco contado numa célula aparece na relação do dia.
- **SC-952**: Uma Retificação vigente se reflete na primeira leitura seguinte, e uma de vigência
  futura não se reflete antes dela — em 100% dos cenários de teste.
- **SC-953**: A página passa nos guardiões de acessibilidade, contraste, política de conteúdo e
  larguras do projeto, e não tem rolagem horizontal a 375 px no mês, no dia e em Próximos marcos.

## Assumptions

- A ordem de grandeza é de dezenas de Editais publicados por unidade, com 4 a 18 Eventos cada; se o
  escopo passar de algumas centenas de Editais publicados não encerrados, a estratégia de leitura é
  revista (ver o plano).
- A semana começa no domingo, como nos calendários brasileiros de parede.
- "Tela larga" e "tela estreita" seguem o ponto de quebra que a gestão já usa para tabelas.
- A página do Edital na gestão não tem seção de cronograma; o acesso ao cronograma é pela página
  pública do Edital, que o mostra.
- Edital de outra unidade é simplesmente invisível, como nas demais listagens da gestão.

## Decisões

### D-001 — A agenda é projeção da versão vigente, e não cadastro

Nenhuma tabela, nenhum cache, nenhuma sincronização. A versão consolidada é imutável, e a Retificação
nova materializa outra versão: a leitura seguinte a vê. Uma tabela de projeção seria uma segunda
fonte de datas, que a Constituição recusa (Princípio II), e teria de ser mantida coerente com o
relógio e com as Retificações.

### D-002 — Marco é ponto; período é intervalo

O marco é o Evento pontual, a abertura ou o encerramento de um período. O período não ocupa os dias
intermediários: repeti-lo dia a dia criaria eventos que o Edital não publicou e esconderia, sob
dezenas de linhas iguais, o dia que concentra marcos de verdade. Ele é dito uma vez, como intervalo,
na lista de períodos do mês, no bloco *em curso* e no dia consultado. O término no mesmo dia do
início não faz período: é a régua que o relatório do Edital (`099`) já usa.

### D-003 — O mês é a visualização inicial

O estudo propunha a lista como padrão; o usuário, em 29/10/2026, inverteu: a pergunta original é a
visão consolidada de vários certames ao longo do mês. A lista continua na mesma página, como
**Próximos marcos**, e é a forma natural no celular.

### D-004 — Toda identidade da gestão acessa

Decidido pelo usuário em 29/10/2026 (a `Q1` do estudo). A agenda só mostra cronograma publicado — o
que a página pública já mostra a qualquer pessoa —, e a lista de Processos já mostra esses Editais a
toda identidade do escopo. Restringir a agenda a quem consulta a visão institucional excluiria a
presidência e a comissão, que conduzem os Processos, sem proteger dado nenhum. Condição do usuário:
só publicado e vigente, só o escopo da unidade, sem visão entre unidades.

### D-005 — O cancelado é dito na lista, e não ocupa a grade

O Evento cancelado continua publicado — a data dele é o que o Edital declarou —, e a página pública o
diz cancelado (a FR-766 da `047`). Na lista do dia e em Próximos marcos ele aparece com *Cancelado*.
Na grade e nos números ele não entra: uma contagem que soma o que não vai acontecer mede a coisa
errada.

### D-006 — Previsto não é executado

A régua de fase chama de *concluído* o Evento cuja data passou. Na agenda, essa fase é dita **data
passada**: a agenda lê o cronograma, e não os atos, e um *Resultado preliminar* com data passada não
prova que o resultado saiu. O mesmo vale para *em curso*, dito sempre *em curso pelo cronograma*. O prazo **efetivamente** aberto por ato (o recursal, contado da
publicação) é outra fonte, fica fora desta entrega, e a página diz que ele pode diferir.

### D-007 — Só filtros que o dado sustenta

Edital e espécie estrutural do Evento — marcado como período de inscrições, ligado a uma Etapa, ou
nenhum dos dois. Unidade não: cada ator tem um escopo só. Modalidade de seleção não: o sistema não
tem essa taxonomia. Categoria pela espécie do Evento não: ela é texto livre, e inferir categoria dele seria decidir
regra lendo o que alguém digitou. O Processo não é filtro: o Edital já o nomeia.

### D-008 — A Retificação de vigência futura é anunciada, e não aplicada

Até a vigência, as datas vigentes são as antigas, como no portal. A agenda olha semanas à frente, e a
pessoa precisa saber que aquelas datas vão mudar: daí o aviso, com o Edital e a data da vigência. Ele
nunca mostra as datas futuras — mostrá-las anteciparia o que ainda não vige.

### D-009 — O Edital encerrado mostra só o que já passou; o cancelado não aparece

Encerrado e cancelado pararam por ato. O cancelado sai, como na vitrine pública. Do encerrado fica o
que já passou — para quem navega para meses anteriores —, e sai o que viria: anunciar marco de
certame encerrado é anunciar o que a instituição decidiu não fazer.

### D-010 — Domingo primeiro, dias de fora vazios, destaque a partir de dois

Domingo primeiro, como os calendários brasileiros. Os dias do mês vizinho ficam vazios: mostrar os
marcos deles contaria o mesmo marco em duas páginas e quebraria a igualdade entre a soma das células
e a síntese. O destaque é para *mais de um* marco — as palavras do pedido, "datas com múltiplos
marcos" —, e não um limiar inventado.

## Pendências do usuário

- **SC-948** depende de sessão observada com quem gere Processos; não é verificável por teste.
- As decisões do estudo sobre o nome na barra (*Agenda*) e sobre a visão entre unidades continuam
  como estão: *Agenda dos Editais*, e nenhuma visão entre unidades.
