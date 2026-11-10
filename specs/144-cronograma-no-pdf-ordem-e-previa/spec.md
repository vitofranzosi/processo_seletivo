# Feature Specification: O Cronograma — visibilidade no PDF, ordenação por data e prévia compacta

**Feature Branch**: `claude/gps-schedule-config-preview-991e36`, sobre a `main` em `daba322f`

**Created**: 2026-11-10

**Status**: Draft, revisada em 10/11/2026 — nenhuma linha de código de produção nesta sessão. A
revisão do usuário trouxe quatro ajustes (o foco na ordenação, a numeração de conteúdo antigo, a
prova sobre o PDF gerado e os seis canais) e a ordem das colunas da prévia; as duas questões (P-1 e
P-2, ao fim) foram decididas na mesma revisão.

**Uma regra só muda, e é de apresentação.** O Evento oculto continua sendo Evento do Cronograma: é
gravado, publicado no conteúdo do ato, vinculável a Etapa, designável como período de inscrições,
conferido pelas mesmas validações e mostrado pelos mesmos canais de hoje. O que deixa de acontecer é
uma coisa: a linha dele na **tabela do Cronograma do PDF do Edital**. Ordenar por data e a prévia
compacta não mudam regra nenhuma — a primeira reescreve a sequência que as setas já reescrevem; a
segunda só lê o formulário.

**Input**: *"Especificar uma melhoria incremental na etapa 3 — Cronograma do assistente de
elaboração de editais do GPS: (A) controlar, evento a evento, se ele aparece no PDF do edital, com um
botão de olho nas ações da linha — ocultar não é desativar; (B) uma ação explícita «Ordenar por data
de início ↑», estável, que reorganiza a sequência efetiva do formulário sem gravar sozinha; (C) uma
prévia compacta no topo da página, que reflete o formulário inclusive no que ainda não foi salvo.
Três incrementos na mesma spec. Simplicidade, previsibilidade, reutilização; sem estados novos, sem
infraestrutura genérica de canais, sem drag-and-drop."* O pedido completo, com os dez cenários
mínimos de aceitação, está resumido em [research.md](research.md) §1.

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de cinco mil e cem a cinco mil cento e quarenta e nove;
> - os critérios de mil quinhentos e oitenta a mil quinhentos e noventa e nove;
> - os requisitos de experiência de trezentos e noventa a trezentos e noventa e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 10/11/2026, nas `specs/` de todas as worktrees desta máquina e de todas as
> branches remotas: requisito cinco mil e vinte e oito, critério mil quinhentos e sessenta e seis e
> o UX trezentos e setenta e quatro, todos da `143` (PR #453, aberto), cuja reserva vai até o
> requisito cinco mil e noventa e nove, o critério mil quinhentos e setenta e nove e o UX trezentos
> e oitenta e nove. A `137` está reservada pelo plano do Centro de Controle, sem pasta; a `138` a
> `143` estão tomadas. Por isso esta é a `144`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-1369 da `069`"); decisão de outra feature, pelo assunto, nunca pelo identificador.
>
> **Os dez cenários do pedido** foram numerados de um a dez. Aqui eles são os critérios SC-1580 a
> SC-1589, na mesma ordem; a correspondência está na [rastreabilidade](rastreabilidade.md).

## Por que esta feature existe

A etapa Cronograma é uma lista de cartões, um por Evento, na ordem em que foram digitados ou
movidos pelas setas. Três coisas faltam a quem a preenche, e as três foram medidas no código em
10/11/2026 (ver [research.md](research.md) §2):

1. **Tudo o que entra no Cronograma sai na tabela do PDF.** Não há como registrar um Evento que o
   sistema precisa — a data de uma Etapa interna, um marco operacional da comissão — sem que ele
   vire linha do ato publicado. Hoje a saída é não cadastrá-lo, e então a Etapa fica sem vínculo e
   o aviso da `022` acusa a falta.
2. **A ordem é só a manual.** Com oito Eventos, corrigir uma data obriga a subir ou descer o cartão
   uma posição por clique, e nada indica que a sequência ficou fora da cronologia.
3. **Não há visão do conjunto.** Cada cartão ocupa uma faixa inteira de campos; para conferir a
   sequência das datas, a pessoa rola a página e lê cartão por cartão.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Ocultar um Evento do PDF sem tirá-lo do Edital (Priority: P1)

Quem elabora cadastra um Evento que o sistema usa — a avaliação curricular interna, vinculada a uma
Etapa — e não quer que ele vire linha na tabela do Cronograma do Edital. No cartão do Evento, aciona
o olho; o cartão passa a dizer "Oculto do PDF". Grava a etapa. O Evento continua no Cronograma, na
lista de Eventos que a Etapa oferece, nas validações e no conteúdo publicado; a tabela do PDF não o
mostra.

**Why this priority**: é a única das três capacidades que muda o que se publica, e é a que resolve
uma limitação real (o Evento operacional que não pode existir sem virar linha do ato).

**Independent Test**: com um Edital de três Eventos, ocultar o segundo, gravar e abrir a prévia do
PDF: a tabela tem duas linhas, numeradas 1 e 2; a Etapa vinculada ao oculto continua dizendo quando
será feita; a lista de Eventos da etapa Etapas continua oferecendo os três.

**Acceptance Scenarios**:

1. **Given** um Edital criado antes desta feature, **When** a prévia do PDF é gerada, **Then** a
   tabela mostra todos os Eventos, como hoje (SC-1580).
2. **Given** um Evento oculto, **When** a prévia do PDF é gerada, **Then** a tabela não o mostra, e o
   Evento continua gravado, com as mesmas datas, vínculos e designação (SC-1581).
3. **Given** um Evento oculto vinculado a uma Etapa, **When** o Edital é publicado, **Then** a Etapa
   continua vinculada a ele, o PDF continua dizendo quando a Etapa será feita, e a operação que lê o
   vínculo lê o mesmo Evento (SC-1582).
4. **Given** um Evento oculto, **When** quem elabora grava outra etapa do assistente, **Then** o Evento
   continua oculto (SC-1584).
5. **Given** um Edital com Evento oculto, **When** ele é reaproveitado, **Then** o Evento chega oculto
   ao Edital novo; **Given** um Edital publicado antes desta feature, **When** reaproveitado, **Then**
   todos chegam exibidos (SC-1586).
6. **Given** todos os Eventos ocultos, **When** a prévia do PDF é gerada, **Then** o documento não tem
   seção Cronograma, a numeração das seções e das tabelas fecha, e a Revisão diz que a seção não será
   impressa (SC-1587).

---

### User Story 2 — Ordenar por data de início com um clique (Priority: P2)

Quem elabora corrige uma data e a sequência fica fora da cronologia. Aciona "Ordenar por data de
início ↑": os cartões se reorganizam do mais cedo ao mais tarde, cada um com tudo o que tinha. Nada é
gravado até a pessoa gravar a etapa. As setas continuam disponíveis para o ajuste fino.

**Why this priority**: poupa o trabalho mais repetitivo da etapa e não muda nada do que se publica
além do que as setas já mudam.

**Independent Test**: com três Eventos fora de ordem, um deles oculto e outro vinculado a uma Etapa,
ordenar, gravar e recarregar: a sequência é a cronológica, e identidade, datas, local, visibilidade,
vínculo e designação de cada Evento são os de antes.

**Acceptance Scenarios**:

1. **Given** Eventos fora da ordem cronológica, **When** a pessoa ordena, **Then** a sequência do
   formulário passa a ser a crescente por início, e a prévia acompanha (SC-1583).
2. **Given** dois Eventos com o mesmo início, **When** a pessoa ordena, **Then** os dois mantêm entre si
   a ordem de antes (SC-1587).
3. **Given** um Evento sem início preenchido, **When** a pessoa ordena, **Then** ele vai para o fim,
   nenhum campo dele muda, e a mensagem diz que há Evento sem data (SC-1587).
4. **Given** a pessoa altera uma data, **When** sai do campo, **Then** nada se reordena sozinho.
5. **Given** a ordenação feita, **When** a pessoa sai sem gravar, **Then** o banco guarda a ordem de
   antes, e o rascunho local guarda a nova, como acontece hoje com as setas.

---

### User Story 3 — Ver o Cronograma inteiro antes dos cartões (Priority: P2)

No topo da etapa, antes dos cartões, uma lista compacta mostra cada Evento numa linha: o que é,
quando começa, quando termina e se sai no PDF. O cabeçalho conta: "3 eventos · 2 no PDF · 1 oculto". A
lista acompanha o formulário enquanto a pessoa digita, acrescenta, remove, oculta, move ou ordena.

**Why this priority**: é o que torna as outras duas legíveis — sem ela, ocultar e ordenar só se
conferem rolando a página.

**Independent Test**: acrescentar, editar, remover, ocultar, mover e ordenar Eventos, sem gravar, e a
cada gesto conferir a prévia contra o formulário (SC-1585).

**Acceptance Scenarios**:

1. **Given** a etapa aberta, **When** a página carrega, **Then** a prévia lista os Eventos na sequência
   do formulário, com a contagem no cabeçalho.
2. **Given** qualquer gesto sobre os cartões, **When** ele termina, **Then** a prévia já o mostra, sem
   pedido ao servidor (SC-1585).
3. **Given** nenhum Evento, **When** a página carrega, **Then** a prévia diz que o Cronograma ainda não
   tem Evento (SC-1587).
4. **Given** todos os Eventos ocultos, **When** a prévia se atualiza, **Then** ela diz que nenhum sai no
   PDF e que a seção Cronograma não será impressa (SC-1587).

---

### A jornada inteira (as três juntas)

O exemplo do pedido, que é também o roteiro do teste no navegador (SC-1590): cadastrar três Eventos
e vê-los na prévia; ocultar um, e o cabeçalho passa a "3 eventos · 2 no PDF · 1 oculto"; mudar uma
data, deixando a sequência fora da cronologia; ordenar, e o formulário e a prévia mostram a nova
sequência; gravar; voltar à etapa e encontrar ordem e visibilidade; abrir a prévia do PDF e encontrar
só os dois exibidos, com a Etapa vinculada ao oculto ainda dizendo quando será feita.

### Edge Cases

São requisitos, e cada um tem linha na [rastreabilidade](rastreabilidade.md).

- **Nenhum Evento.** O botão de ordenar fica desabilitado; a prévia diz "Nenhum Evento no
  Cronograma ainda."; nada muda na pendência de hoje, que acusa o Cronograma vazio.
- **Um Evento só.** Ordenar não move nada e diz "Os Eventos já estão em ordem de início."
- **Todos ocultos.** A seção Cronograma não sai no PDF, pela mesma regra que já omite a seção gerada
  de fonte vazia; o resumo do início do documento deixa de dizer "Datas: no Cronograma"; a Revisão e
  a prévia dizem que a seção não será impressa. **Não** é impeditivo de publicação (D-004).
- **O Evento do período de inscrições oculto.** Continua o período: o portal abre e fecha por ele, e o
  PDF continua dizendo o período no resumo e em "Como se inscrever?". Só a remissão "(Cronograma,
  nº N)" sai da frase, porque não há linha a que remeter (D-003).
- **Mesmo início em dois Eventos.** A ordenação é estável: os dois mantêm a ordem relativa anterior.
- **Ordem gravada com `0` ou com lacunas.** A API aceita qualquer `order` não negativo e sem
  repetição, e o conteúdo publicado o guarda como chegou. Sem Evento oculto, o "Nº" do PDF continua
  sendo esse valor — "0, 2, 5" sai "0, 2, 5", como hoje; só com algum oculto a tabela numera os
  exibidos de 1 a k (D-003).
- **Foco depois de mover.** Ordenar ou usar as setas não é acrescentar: o foco fica no botão
  acionado, e não vai para o primeiro campo do cartão movido (D-010).
- **Início incompleto ou vazio durante a edição.** O navegador entrega valor vazio para o campo de data
  incompleto. Ordenar põe esses Eventos ao fim, na ordem relativa em que estavam, sem tocar em campo
  nenhum; a prévia os mostra como "sem data de início"; a gravação recusa como hoje.
- **Término vazio.** É o Evento pontual; a prévia mostra só o início.
- **Evento recém-acrescentado.** Nasce exibido no PDF, e entra na prévia vazio até ser preenchido.
- **Recusa na gravação.** A tela reexibe o digitado — inclusive a visibilidade e a sequência que a
  pessoa tinha ordenado.
- **Rascunho local restaurado.** A visibilidade volta com os demais campos, porque viaja num campo do
  formulário (D-007).
- **Somente leitura** (Edital submetido, homologado, ou papel sem edição). A prévia aparece; o olho, as
  setas e o botão de ordenar não aparecem; a marca "Oculto do PDF" aparece no cartão.
- **Sem JavaScript.** A prévia, o botão de ordenar e o olho saem do servidor com `hidden`, e só o
  script os mostra: sem ele, não aparecem — botão inerte é pior do que botão ausente. A visibilidade
  gravada atravessa intacta no campo oculto, e o formulário funciona como hoje.
- **Edital publicado antes desta feature.** O PDF já guardado não muda (os documentos publicados não se
  regeneram); a Retificação e o consolidado leem o conteúdo elevado, em que todo Evento é exibido.

## Requirements *(mandatory)*

### Functional Requirements

**Incremento A — visibilidade no PDF**

- **FR-5100**: Cada Evento do Cronograma MUST ter um atributo de visibilidade no PDF, com dois valores
  — exibido e oculto. Todo Evento existente MUST ser exibido depois da migração, e todo Evento novo
  MUST nascer exibido, inclusive o acrescentado pela tela, pela API e pela Retificação.
- **FR-5101**: O cartão de cada Evento MUST oferecer, no grupo de ações da linha, um controle que
  alterna a visibilidade, com o estado e a ação ditos em texto acessível (UX-390).
- **FR-5102**: Alternar a visibilidade MUST mudar só o formulário. A mudança MUST ser gravada pelo
  gesto de gravar a etapa, como os demais campos, e MUST ser registrada pelo rascunho local; nenhum
  pedido ao servidor MUST acontecer ao alternar.
- **FR-5103**: O Evento oculto MUST continuar, sem diferença nenhuma do exibido: gravado; publicado no
  conteúdo do ato; oferecido na lista de Eventos da etapa Etapas; designável como período de
  inscrições; contado entre os Eventos vencidos que deixam a etapa pendente; conferido pelas
  validações de rascunho, de submissão e de publicação; lido pelos fluxos que leem o vínculo da Etapa.
- **FR-5104**: A visibilidade MUST atravessar todos os caminhos de gravação do rascunho: a etapa
  Cronograma; as demais etapas, que reenviam o Cronograma gravado; a recusa, que reexibe o digitado;
  a API do rascunho; a restauração do rascunho local. Omitida num caminho de escrita da API, MUST valer
  exibido.
- **FR-5105**: O conteúdo publicado MUST levar a visibilidade em cada Evento, sempre presente. O
  conteúdo de versão anterior MUST ser lido como exibido em todo Evento, por um degrau novo da cadeia
  de elevação (D-001).
- **FR-5106**: A tabela do Cronograma do PDF MUST mostrar só os Eventos exibidos, na sequência do
  Cronograma. Sem nenhum Evento oculto, a coluna "Nº" MUST imprimir o `order` de cada Evento, como
  hoje, inclusive `0` e lacunas; com algum oculto, MUST numerar os exibidos de 1 ao total deles
  (D-003). A coluna "Onde" MUST aparecer só quando algum Evento **exibido** declara local.
- **FR-5107**: A frase do período de inscrições do PDF MUST remeter ao número do Evento na tabela
  impressa, e MUST omitir a remissão quando o Evento estiver oculto, mantendo o período.
- **FR-5108**: A frase da Etapa no PDF ("Será feita de … a …") MUST continuar lendo o Evento vinculado,
  oculto ou não.
- **FR-5109**: Sem nenhum Evento exibido, a seção Cronograma MUST não ser composta, e a numeração das
  seções, a contagem de tabelas, o sumário e o resumo do documento MUST acompanhar, nas duas
  apresentações do PDF — a plana e a por perguntas.
- **FR-5110**: A Revisão MUST dizer, no Evento oculto, que ele não sai no PDF; e, quando nenhum sai,
  que a seção Cronograma não será impressa.
- **FR-5111**: O reaproveitamento MUST preservar a visibilidade de cada Evento da origem. Origem
  publicada antes do degrau novo MUST chegar com todos os Eventos exibidos.
- **FR-5112**: Os demais canais que mostram o Cronograma MUST continuar mostrando todos os Eventos,
  como hoje: a página pública da seleção no portal, o assistente de dúvidas, a Agenda dos Editais, o
  Kit de Divulgação, o relatório do Edital e a leitura pela API (P-2). Cada um dos seis MUST ter teste
  que o confere com um Evento oculto.
- **FR-5113**: A visibilidade MUST ser retificável pelo mecanismo genérico de campo da Retificação, e o
  Evento acrescentado por Retificação MUST nascer exibido (P-1, decidida pelo usuário).
- **FR-5114**: Nenhum documento publicado MUST ser regenerado ou alterado por esta feature; o efeito
  sobre ato já publicado só existe pela Retificação.

**Incremento B — ordenação crescente**

- **FR-5120**: A etapa MUST oferecer, quando editável, a ação "Ordenar por data de início ↑", junto da
  lista de Eventos.
- **FR-5121**: Ordenar MUST reorganizar a sequência efetiva do formulário — a posição dos cartões e o
  campo de ordem de cada um — de forma crescente por data e hora de início, e MUST preservar todo o
  resto de cada Evento: identidade, tipo, descrição, datas, local, visibilidade, vínculos e
  designação.
- **FR-5122**: A ordenação MUST ser estável: Eventos de mesmo início mantêm a ordem relativa anterior.
- **FR-5123**: Eventos sem início válido no formulário MUST ir para o fim, na ordem relativa anterior,
  sem que campo nenhum deles seja alterado.
- **FR-5124**: Nada MUST se reordenar sem o gesto: editar data, acrescentar ou remover Evento não
  ordena.
- **FR-5125**: O resultado MUST ser anunciado em região viva — quantos Eventos mudaram de posição, que
  já estavam em ordem, ou que há Evento sem data de início — e o foco MUST ficar no botão, **depois**
  de os observadores da lista terem respondido à mutação.
- **FR-5126**: A ordenação MUST não gravar nada; ela MUST ser registrada pelo rascunho local e gravada
  com a etapa. As setas MUST continuar funcionando antes e depois dela.
- **FR-5127**: Mover cartões já existentes — pela ordenação ou pelas setas — MUST não ser tratado como
  acréscimo pelo comportamento de foco das listas do assistente: só o nó que entra na lista sem ter
  saído dela na mesma mutação é linha nova (D-010).

**Incremento C — prévia compacta**

- **FR-5130**: A etapa MUST mostrar, antes dos cartões, uma prévia com uma linha por Evento, nesta
  ordem: o Evento (a descrição, ou o tipo quando ela estiver vazia, como o PDF imprime), o início, o
  término quando houver, e a visibilidade no PDF. Primeiro o quê, depois o quando — a ordem em que o
  cartão se preenche.
- **FR-5131**: O cabeçalho da prévia MUST contar os Eventos, os exibidos e os ocultos, com
  concordância de número ("1 evento · 1 no PDF", "3 eventos · 2 no PDF · 1 oculto").
- **FR-5132**: A prévia MUST seguir a sequência atual do formulário e refletir o que ainda não foi
  gravado, atualizando-se a cada digitação, acréscimo, remoção, alternância, movimento pelas setas e
  ordenação.
- **FR-5133**: A prévia MUST ter o estado vazio ("Nenhum Evento no Cronograma ainda.") e o estado de
  todos ocultos ("Nenhum Evento sai no PDF: a seção Cronograma não será impressa.").
- **FR-5134**: A prévia MUST ser só leitura do formulário: nenhum pedido ao servidor, nenhuma
  validação e nenhuma regra de negócio própria. Evento sem início aparece como "sem data de início".
- **FR-5135**: Em somente leitura, a prévia MUST aparecer, com o mesmo conteúdo.
- **FR-5136**: Sem JavaScript, a prévia MUST não aparecer, e o formulário MUST funcionar como hoje.

### Requisitos de experiência

- **UX-390**: O controle de visibilidade MUST ser um botão de alternância no grupo de ações da linha,
  antes das setas, com o glifo de olho aberto (exibido) e de olho fechado (oculto) em SVG, nome
  acessível constante "Ocultar do PDF", `aria-pressed` verdadeiro quando oculto, e `title` que diz o
  estado ("Exibido no PDF — ocultar" / "Oculto do PDF — exibir").
- **UX-391**: O cartão do Evento oculto MUST dizer "Oculto do PDF" em texto na legenda, ao lado do
  nome, e MUST ter aparência atenuada que não se confunda com campo desabilitado; a diferença não pode
  depender só de cor.
- **UX-392**: O botão "Ordenar por data de início ↑" MUST ser secundário, ficar na linha da contagem de
  Eventos, acima dos cartões, e estar desabilitado com menos de dois Eventos.
- **UX-393**: A prévia MUST ser uma tabela compacta (Evento · Início · Término · PDF) com cabeçalho de
  colunas, legível a 1440 px e a 375 px sem rolagem horizontal da página; a 375 px cada linha empilha
  as datas sob o nome.
- **UX-394**: Na prévia, a linha oculta MUST dizer "Oculto" em texto e ficar atenuada; a exibida, "No
  PDF". A prévia MUST não ser região viva — o anúncio é só o da ordenação (FR-5125).

### Key Entities

- **Evento do Cronograma** — ganha um atributo: a visibilidade no PDF, booleano, exibido por padrão.
  Nenhum estado novo; o `status` e a fase derivada das datas continuam os de hoje.
- Nenhuma tabela, papel, permissão ou estado novo. Uma migration (coluna com padrão verdadeiro) e um
  degrau da versão canônica do conteúdo publicado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1580**: Compatibilidade — um Edital gravado antes da migração e um conteúdo publicado em versão
  anterior produzem, na prévia do PDF, a tabela com todos os Eventos; o texto extraído do PDF é o
  mesmo de antes da feature, inclusive com `order` começando em `0` e com lacunas.
- **SC-1581**: Ocultação — com um Evento oculto, o texto extraído do PDF não contém a descrição dele na
  tabela, e o Evento continua no banco e no conteúdo publicado com os mesmos valores.
- **SC-1582**: Associação — um Evento oculto vinculado a uma Etapa continua no vínculo depois de gravar,
  publicar e reaproveitar; o PDF diz quando a Etapa será feita; a lista de Eventos da etapa Etapas o
  oferece.
- **SC-1583**: Ordenação — depois de ordenar, a sequência é crescente por início, com empates na ordem
  anterior e incompletos ao fim, e cada Evento conserva identidade, campos, visibilidade, vínculo e
  designação.
- **SC-1584**: Persistência — ordem e visibilidade são as mesmas depois de gravar e recarregar a etapa,
  e depois de gravar qualquer outra etapa do assistente.
- **SC-1585**: Prévia — depois de cada um dos seis gestos (acrescentar, editar, remover, ocultar, mover,
  ordenar), linhas e contagem da prévia coincidem com o formulário, sem pedido ao servidor.
- **SC-1586**: Reaproveitamento — a visibilidade da origem chega intacta ao Edital novo; origem
  anterior ao degrau novo chega toda exibida.
- **SC-1587**: Casos extremos — nenhum Evento, todos ocultos, mesmo início e início incompleto têm o
  comportamento dos casos-limite, verificado um a um.
- **SC-1588**: PDF — as afirmações sobre o documento são feitas sobre o texto extraído do PDF gerado, nas
  duas apresentações, e não sobre o HTML ou o estado do botão: um oculto, todos ocultos (sem seção,
  numeração e tabelas fechando) e a remissão do período, com o período exibido e oculto.
- **SC-1589**: Integridade — com o Evento oculto, a pendência por Evento vencido, a validação de datas,
  a validação de vínculo da Etapa e a abertura das inscrições pelo período designado se comportam como
  com ele exibido.
- **SC-1590**: A jornada inteira do exemplo roda no navegador, de ponta a ponta, sem violação de CSP, a
  1440 px e a 375 px; depois de ordenar e de cada seta, o elemento focado é o botão acionado.

## Decisões

As decisões de desenho estão com a razão e as alternativas descartadas em
[research.md](research.md). O resumo:

- **D-001** — o atributo é um booleano do próprio Evento, sempre presente no conteúdo publicado, com
  degrau novo de elevação (ausência = exibido).
- **D-002** — o filtro mora numa função só da composição do PDF; as frases que citam Evento por
  vínculo continuam lendo todos.
- **D-003** — sem oculto, "Nº" é o `order`, como hoje; com algum, a posição entre os exibidos. A
  remissão do período usa o mesmo número, e some quando ele está oculto.
- **D-004** — todos ocultos não impede publicar: a seção não sai, como a de fonte vazia.
- **D-005** — ordenar é do cliente, estável, sem gravar, reaproveitando a renumeração das setas.
- **D-006** — a prévia é do cliente, lida do formulário; sem filtro "Todos / Somente no PDF".
- **D-007** — o controle é botão de alternância sobre um campo oculto do formulário.
- **D-008** — reaproveitar preserva a visibilidade.
- **D-009** — a Revisão mostra a visibilidade; o campo entra na partição do que ela lê.
- **D-010** — mover não é acrescentar: o foco das listas distingue o nó movido do nó novo.

## Questões decididas pelo usuário

As duas foram decididas em 10/11/2026, na revisão desta spec, pela recomendação de cada uma. Não se
reabrem.

- **P-1 — A Retificação alcança a visibilidade? Decidido: sim**, pelo mecanismo genérico de campo
  (uma linha nos campos do Evento da Retificação; linha "R" na matriz da `026`; o Evento acrescentado
  nasce exibido). Custo: uma tarefa e um teste. Alternativa: classificá-la como não retificável — o
  que se publicou oculto fica oculto; custa a mesma linha na matriz e nenhuma tela, e deixa sem saída
  o Edital que ocultou por engano — razão da escolha: um erro de ocultação precisa de correção formal.
- **P-2 — Os outros canais acompanham o PDF? Decidido: não nesta spec**, como o pedido manda. A
  página pública da seleção e o assistente de dúvidas mostram todos os Eventos; quem quiser que eles
  também ocultem decide depois, sabendo que a página pública é onde o candidato confere o calendário,
  e que esconder lá um Evento que o sistema executa é outra decisão de norma.

## Assumptions

- "PDF do edital" é o documento composto por `publicacoes/infrastructure/pdf.py`, nas duas
  apresentações (a plana e a por perguntas da `069`), o mesmo da prévia, da publicação, da Retificação
  e do consolidado.
- O Edital da `069` em diante sai na apresentação por perguntas; os anteriores e os consolidados deles,
  na plana. As duas recebem o mesmo filtro.
- A data e a hora de início comparadas na ordenação são as do campo `datetime-local`, no horário de
  Brasília, como a etapa já declara.

## Fora do escopo

- Arrastar e soltar; ordenação decrescente; ordenar por término; ordenar automaticamente.
- Ocultar em qualquer canal que não seja o PDF (P-2); infraestrutura de "canais de publicação".
- Filtro "Todos / Somente no PDF" na prévia (D-006).
- Outro comportamento de foco das listas. D-010 muda só a distinção entre mover e acrescentar, e ela
  vale para todas as listas do assistente porque o script é um só.
- Reproduzir na prévia o layout do PDF; a prévia do PDF continua sendo o botão "Ver o Edital".
- Mudar a ordem de Edital publicado: `order` continua estrutural na Retificação.
- Qualquer estado novo de Evento.
