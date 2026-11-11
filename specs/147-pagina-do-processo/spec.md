# Feature Specification: A página do Processo Seletivo — o conjunto dos Editais, e o que fazer nele

**Feature Branch**: `claude/gps-processo-seletivo-ui-ux-a59d79`, sobre a `main` em `d3e98a89`

**Created**: 2026-11-11

**Status**: Spec escrita em 11/11/2026, depois da rodada 1 da revisão de UX — diagnóstico, dois
protótipos e validação em sete Processos, sete papéis e cinco larguras. O usuário escolheu a
alternativa B **com os seis ajustes** que a validação mostrou ([research.md](research.md) §2). As
quatro decisões que o relatório deixou abertas foram tomadas pela recomendação dele e estão em
[research.md](research.md) §3, para revisão no PR.

**Input**: *"Melhorar substancialmente a experiência da página de Processo Seletivo — hierarquia,
clareza da situação, orientação operacional, organização dos editais, ruído, responsividade,
acessibilidade e escala para dezenas de editais — sem novo dashboard, sem motor de workflow e sem
regra de negócio nova. O Processo permite compreender e administrar o conjunto; o Edital permite
compreender e conduzir a seleção."* O pedido completo e o relatório da rodada 1 estão resumidos em
[research.md](research.md) §1.

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de cinco mil e trezentos a cinco mil trezentos e trinta e nove;
> - os critérios de mil seiscentos e sessenta a mil seiscentos e setenta e nove;
> - os requisitos de experiência de quatrocentos e quarenta a quatrocentos e quarenta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 11/11/2026 nas `specs/` de todas as worktrees desta máquina: requisito cinco
> mil duzentos e trinta e três, critério mil seiscentos e trinta e cinco e UX quatrocentos e vinte e
> três, todos da `146`. A faixa começa com folga.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature;
> decisão de outra feature, pelo assunto, nunca pelo identificador.

## Por que esta feature existe

A página do Processo foi montada em camadas, por features diferentes, cada uma certa sozinha: a
`038` trouxe o pulso e a Atenção da Supervisão, a `058` ordenou os atos do Processo, a `078` subiu
"O que fazer agora" e pôs os Editais em tabela. Juntas, elas produziram três defeitos que a rodada 1
mediu:

1. **"O que fazer agora" oferece o excepcional e cala o trabalho.** No Processo ativo, o cartão traz
   Encerrar e Cancelar, marcados como irreversíveis, e só depois, recolhido, que os dois estão
   impedidos. As condições de atenção e as ações da pessoa nos Editais não aparecem nele. A página do
   Edital já resolveu isso: os atos de fim de ciclo ficam recolhidos e por último (`FR-4741` da
   `136`).
2. **O acompanhamento cresce em linha reta com os Editais.** Cada Edital ganha um parágrafo, um
   gráfico e uma lista de marcos. Com 31 Editais a página tem 10.369 px a 1366 px de largura, com 14
   gráficos empilhados e 20 sinais no fim.
3. **O que se sabe de um Edital está em três lugares.** A tabela diz número, título e situação; as
   inscrições e os marcos estão mil pixels abaixo; a atenção, no fim. Saber qual Edital precisa de
   alguém exige cruzar à mão.

Nada disso pede regra nova. Os dados existem — o pulso e os sinais da Supervisão, os atos e os
impedimentos do Processo, a faixa "Ações disponíveis para você" da Lista (`FR-2807` da `104`) e as
Retificações em curso (`FR-2706` da `103`). O que muda é **onde cada coisa mora**.

**O que esta spec não faz.** Ela não traz à página do Processo o andamento de cada Edital — o
"Onde estamos" do Edital, o mapa de fases, as providências por lista (`127`, `136`). Essa derivação
custa dezenas de consultas **por Edital** e é o que torna a página do Edital orientadora. O Processo
mostra fatos de cada Edital e leva até ele.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Saber o que fazer agora no Processo (Priority: P1)

Quem abre o Processo vê, no topo, o que **ela** pode fazer nos Editais dele, e quais Editais pedem
atenção — e não os atos de encerrar e cancelar, que são excepcionais.

**Why this priority**: É o defeito de maior impacto. O cartão promete orientação e entrega atos
irreversíveis impedidos.

**Independent Test**: Abrir o Processo com quatro Editais, como gestor e como elaborador, e conferir
que o cartão "O que fazer agora" mostra o trabalho de cada um, que "Precisa de atenção" mostra as
condições agrupadas por Edital, e que Encerrar e Cancelar estão em "Administração do Processo",
recolhidos.

**Acceptance Scenarios**:

1. **Given** um Processo ativo com quatro Editais e seis condições de atenção em dois deles, **When**
   o gestor abre a página, **Then** "Precisa de atenção" diz "6 em 2 Editais", com um grupo por
   Edital, e nenhum ato irreversível aparece fora de "Administração do Processo".
2. **Given** um Processo com dezesseis Editais em elaboração, **When** quem elabora abre a página,
   **Then** o botão "Elaborar o Edital N" é o primeiro passo, as demais elaborações aparecem como
   ações dela (cinco à vista, as outras recolhidas), e o Edital do botão não se repete na lista.
3. **Given** uma pessoa avaliadora com inscrições pendentes numa Etapa de um Edital do Processo,
   **When** ela abre a página, **Then** "Avaliar (N pendentes)" aparece em "O que fazer agora", e as
   Etapas dela em outros Processos não aparecem.
4. **Given** uma pessoa sem nenhuma ação nos Editais do Processo, **When** ela abre a página,
   **Then** o cartão diz que não há ação dela no nível do Processo e diz o que a lista de ações não
   cobre, com a mesma frase da Lista.

---

### User Story 2 — Ler o conjunto dos Editais numa lista que escala (Priority: P1)

Quem abre o Processo reconhece cada Edital, a situação dele e os fatos que importam — inscrições,
próximo marco, atenção, ações suas — numa linha só, em grupos por situação, também com dezenas de
Editais e no celular.

**Why this priority**: A lista é o conteúdo próprio do Processo. Sem ela escalando, as demais
melhorias se perdem no comprimento da página.

**Independent Test**: Abrir o Processo de 31 Editais a 1366 px e a 390 px e conferir a altura, os
grupos e que nada rola para o lado.

**Acceptance Scenarios**:

1. **Given** um Processo ativo com Editais publicados, em elaboração, encerrados e cancelados,
   **When** a página abre, **Then** os Editais aparecem em três grupos — Publicados, Em preparo, e
   Encerrados e cancelados —, este último recolhido, cada grupo com a contagem.
2. **Given** um Edital publicado com inscrições abertas e três condições de atenção, **When** a
   linha dele aparece, **Then** ela diz a situação, "Inscrições abertas até dd/mm · N recebidas", o
   próximo marco com a data, "3 de atenção" e, se houver, quantas ações são da pessoa.
3. **Given** um Edital com Retificação em curso, **When** a linha dele aparece, **Then** ela traz a
   marca da Retificação com a situação dela e quem ela aguarda, como na Lista.
4. **Given** um Processo encerrado, **When** a página abre, **Then** os Editais encerrados e
   cancelados aparecem abertos, e não recolhidos.

---

### User Story 3 — Reconhecer o Processo e a situação dele de relance (Priority: P2)

O topo diz qual Processo é, em que situação administrativa está, e onde está o conjunto dos Editais,
numa frase — e oferece os caminhos de comissão e supervisão a quem os alcança.

**Why this priority**: Hoje a situação aparece duas vezes (selo e faixa de etapas) e o conjunto não
aparece nenhuma.

**Independent Test**: Abrir Processos em elaboração, ativo, encerrado e cancelado e ler o topo.

**Acceptance Scenarios**:

1. **Given** um Processo ativo com 31 Editais, **When** a página abre, **Then** o topo diz "31
   Editais: 16 em elaboração, 13 publicados, 1 encerrado, 1 cancelado." e, abaixo, em quantos
   Editais há inscrições abertas e quantos têm condição de atenção.
2. **Given** qualquer Processo, **When** a página abre, **Then** o ciclo Em elaboração · Ativo ·
   Encerrado aparece numa linha, com a situação atual marcada em texto e símbolo; no cancelado, a
   frase do topo diz que o Processo foi cancelado e que os Editais mantêm as próprias situações.
3. **Given** quem gere a comissão, **When** a página abre, **Then** Supervisão, Comissão e Alocação
   por Etapa aparecem junto do código, num grupo nomeado; Auditoria da comissão aparece para quem
   audita; quem não alcança nenhum não vê o grupo.

---

### User Story 4 — Administrar o Processo sem que isso domine a página (Priority: P2)

Ativar, encerrar e cancelar continuam disponíveis a quem pode, no fim da página; quando impedidos,
aparecem desabilitados com os Editais que impedem nomeados.

**Why this priority**: São atos raros e irreversíveis. Precisam continuar descobríveis e
protegidos, sem ocupar o lugar da orientação.

**Independent Test**: Abrir um Processo ativo com Edital não final, como gestor, e abrir
"Encerrar ou cancelar o Processo".

**Acceptance Scenarios**:

1. **Given** um Processo ativo com Editais não finais, **When** o gestor abre "Encerrar ou cancelar
   o Processo", **Then** os dois atos aparecem desabilitados, com o marcador "irreversível", e a
   frase nomeia os Editais que precisam ser encerrados ou cancelados antes, cada um com link.
2. **Given** um Processo ativo com todos os Editais encerrados ou cancelados, **When** o gestor abre
   o grupo, **Then** Encerrar e Cancelar levam às telas de confirmação de hoje.
3. **Given** um Processo em elaboração, **When** o gestor chega à Administração, **Then** "Ativar
   Processo" aparece com a explicação de que a publicação do primeiro Edital já ativa.
4. **Given** um Processo encerrado ou cancelado, **When** a página abre, **Then** a Administração não
   oferece ato algum.

---

### User Story 5 — Acompanhar as inscrições enquanto estão abertas (Priority: P3)

Durante o período de inscrições, quem acompanha vê a série diária de submissões dos Editais com
período em curso. Encerrado o período, a série vive na Supervisão.

**Why this priority**: A série só tem valor enquanto o período corre; repetida para todo Edital, ela
é o que mais alonga a página.

**Independent Test**: Abrir o Processo com dois Editais de inscrições abertas e onze encerradas e
contar os gráficos.

**Acceptance Scenarios**:

1. **Given** dois Editais com período em curso e onze encerrados, **When** a página abre, **Then**
   "Submissões por dia" mostra exatamente dois gráficos, cada um nomeando o Edital.
2. **Given** nenhum período em curso, **When** a página abre, **Then** a seção não aparece.

### Edge Cases

- **Processo sem Edital.** Não nasce pela aplicação — o Processo é criado com o primeiro Edital —,
  mas o dado legado existe: a lista diz "Nenhum Edital neste Processo." no estado vazio de sempre
  (mantém `FR-1772` da `078`), "Onde estamos" diz "Nenhum Edital", e "Novo Edital" continua para
  quem pode criar.
- **Quem não alcança espécie alguma da Atenção.** A região "Precisa de atenção" não aparece, e
  "O que fazer agora" ocupa a largura toda. Dizer "nenhuma condição" a essa pessoa afirmaria uma
  ausência (a regra da `038`, preservada).
- **Quem alcança parte das espécies.** A linha de ausência é a relativa, como hoje (`FR-730` da
  `045`).
- **Edital encerrado com condição de atenção.** O sinal continua contado e agrupado (as espécies que
  não param com o Edital continuam valendo); a linha do Edital, no grupo recolhido, traz a marca.
- **Muitos Editais com atenção.** Os grupos de "Precisa de atenção" vêm recolhidos, um por Edital,
  com a contagem no resumo; com um Edital só, vem aberto.
- **Mais de seis marcos.** Os seis primeiros aparecem; os demais, em "Ver os outros N".
- **Edital sem cronograma vigente ou sem período.** A linha diz "Sem período de inscrições"; o
  Edital ainda não publicado diz só a situação.
- **Período cancelado.** A linha diz "Período cancelado", e não as datas.
- **Título longo de Edital.** Quebra dentro da própria coluna; a página não rola para o lado.
- **Pessoa que elabora e não tem Edital em elaboração.** Nem botão nem lista de elaboração.
- **"Aguardando quem elabora".** Só para quem gere o Processo (ver `FR-5304`); quem só avalia,
  divulga ou julga não recebe a frase.
- **Ato recém-registrado.** O retorno "Ato registrado." continua no topo, como hoje.

## Requirements *(mandatory)*

### Functional Requirements

**Incremento A — o topo, "O que fazer agora" e a Administração**

- **FR-5300**: O topo MUST mostrar o título do Processo como único `h1`, o código e a pastilha da
  situação, e, para quem alcança, o grupo "Comissão e supervisão" com Supervisão, Comissão, Alocação
  por Etapa e Auditoria da comissão, nas mesmas condições de hoje (`FR-1776` da `078`, `FR-476` da
  `033`). Quem não alcança nenhum MUST NOT ver o grupo, nem vazio.
- **FR-5301**: O topo MUST dizer "Onde estamos" numa frase, composta só de contagens que a página já
  lê: o número de Editais por situação, em quantos há inscrições abertas e em quantos há condição
  de atenção visível à pessoa. No Processo encerrado e no cancelado a frase MUST dizer a situação
  final; no cancelado, MUST dizer que os Editais mantêm as próprias situações e que o histórico está
  preservado.
- **FR-5302**: O ciclo administrativo (Em elaboração, Ativo, Encerrado) MUST aparecer numa linha,
  com a situação atual marcada em texto e símbolo e anunciada como atual a quem ouve a tela. No
  cancelado, MUST marcar os três como fora do ciclo. A faixa de etapas em cartão de largura total
  sai.
- **FR-5303**: "O que fazer agora" MUST mostrar, nesta ordem: o próximo passo de elaboração
  ("Elaborar o Edital N", para quem elabora); as ações da pessoa nos Editais do Processo, lidas da
  faixa da `104` (`FR-2801` e `FR-2806` da `104`) e recortadas aos Editais deste Processo, cinco à
  vista e as demais recolhidas; e a frase de cobertura da faixa, a mesma da Lista (`FR-4324` da
  `129`). O Edital do próximo passo MUST NOT se repetir entre as ações.
- **FR-5304**: "Aguardando quem elabora para compor o Edital N" MUST aparecer só para quem não
  elabora e gere o Processo — pode criar Edital ou gerir a comissão dele. Substitui a regra de hoje,
  que mostra a frase a todo papel sem elaboração.
- **FR-5305**: Sem próximo passo, sem ação e sem espera a nomear, "O que fazer agora" MUST dizer que
  não há ação da pessoa no nível do Processo e onde o trabalho está, conforme a situação: no ativo,
  em cada Edital; em elaboração, compor e publicar o Edital; no final, só consulta.
- **FR-5306**: Os atos do Processo MUST sair de "O que fazer agora" e ir para "Administração do
  Processo", a última região da página. "Ativar Processo" MUST aparecer ali, secundário, com a ajuda
  de hoje. Encerrar e Cancelar MUST ficar recolhidos num grupo "Encerrar ou cancelar o Processo", com
  o marcador "irreversível" descrevendo cada um (`FR-2060` da `090`).
- **FR-5307**: Quando Encerrar ou Cancelar dependem dos Editais e há Edital não final, o resumo do
  grupo MUST dizer que estão impedidos, o corpo MUST nomear os Editais pendentes com link, e os dois
  MUST aparecer **desabilitados**, sem link, anunciados como indisponíveis. Sem impedimento, MUST
  levar às telas de confirmação de hoje.
- **FR-5308**: No Processo encerrado ou cancelado, "Administração do Processo" MUST NOT aparecer
  quando não há ato a oferecer.
- **FR-5309**: As ações da pessoa MUST custar o mesmo para qualquer número de Editais: a carga de
  avaliação MUST ser calculada só sobre as atribuições da pessoa nos Editais deste Processo, antes
  do cálculo, e não sobre todas as dela.

**Incremento B — os Editais**

- **FR-5310**: Os Editais MUST aparecer numa lista compacta, uma linha por Edital, em três grupos na
  ordem: **Publicados**; **Em preparo** (em elaboração, em revisão e homologados); **Encerrados e
  cancelados**. Cada grupo MUST ter título com a contagem; grupo vazio MUST NOT aparecer; com um grupo
  só, o título do grupo MUST NOT aparecer. Dentro do grupo, a ordem MUST ser a de hoje (ano e
  número).
- **FR-5311**: No Processo que não está em situação final, o grupo "Encerrados e cancelados" MUST vir
  recolhido, com a contagem no resumo; no Processo encerrado ou cancelado, MUST vir aberto.
- **FR-5312**: Cada linha MUST trazer: número e ano; título, como o link único da linha para o
  Edital, com o número no nome acessível; a pastilha da situação; as marcas das Retificações em
  curso, com a situação e quem aguardam (`FR-2706` e `FR-2708` da `103`); o estado das inscrições;
  o próximo marco; a marca de atenção; e a marca das ações da pessoa.
- **FR-5313**: O estado das inscrições MUST ser, conforme o pulso do Edital: "Inscrições abertas até
  dd/mm/aaaa · N recebidas", ou "sem término declarado" no lugar da data quando o período não declara
  fim; "Inscrições a partir de dd/mm/aaaa"; "Inscrições encerradas · N recebidas";
  "Período cancelado"; "Sem período de inscrições" para o publicado sem período; e nada para o
  Edital ainda não publicado, cuja linha tem uma altura só.
- **FR-5314**: O próximo marco MUST ser o primeiro dos próximos marcos do pulso do Edital, com a
  descrição e a data com ano: o início, para o marco que ainda vem; "em andamento até" o término,
  para o que já começou — nunca uma data passada sob "Próximo". A marca de atenção MUST dizer "N de atenção" em
  texto; a das ações, "N sua(s)".
- **FR-5315**: A lista MUST NOT ser tabela, e a página MUST NOT rolar para o lado em nenhuma largura;
  no estreito, cada linha empilha sem perder fato.
- **FR-5316**: "Novo Edital" MUST continuar junto do título da região, só para quem pode criar e com
  o Processo fora de situação final.

**Incremento C — atenção, marcos e série**

- **FR-5317**: "Precisa de atenção" MUST mostrar os sinais da Supervisão, lidos da mesma função
  (`FR-557` da `038`), agrupados por Edital: um grupo por Edital com sinal, com o número do Edital, a
  contagem e o título no resumo, e os sinais de sempre dentro, com a mesma forma, medida e destino. O
  título da região MUST dizer o total e o número de Editais. Com um Edital, o grupo MUST vir aberto;
  com mais, recolhido.
- **FR-5318**: Sem sinal, a região MUST mostrar a linha de ausência de hoje, global ou relativa
  (`FR-559` da `038`, `FR-730` da `045`). Quem não alcança espécie alguma MUST NOT receber a região.
- **FR-5319**: Os próximos marcos de todos os Editais MUST aparecer numa lista única em "O que fazer
  agora", ordenada por data, cada um com o Edital que o sustenta, a data com ano e, quando houver, o
  término; o marco em curso diz até quando vai. Seis à vista, os demais em
  "Ver os outros N". Sem marco, uma linha diz que não há marco por vir.
- **FR-5320**: A série diária de submissões MUST aparecer só para os Editais com período de
  inscrições em curso, numa seção "Submissões por dia", com o parcial de sempre. Sem período em
  curso, a seção MUST NOT aparecer.
- **FR-5321**: As inscrições no Processo — recebidas, em preenchimento e, com período em curso, nas
  últimas 24 horas — MUST aparecer no topo, como estado, com o instante da leitura.
- **FR-5322**: Nenhum número da página MUST ser calculado por ela: tudo sai do pulso, dos sinais,
  dos atos e Editais pendentes, da faixa da `104` e das Retificações em curso, já lidos hoje.

**Revisões de requisitos de outras features**

- **FR-5323**: Esta feature substitui, no detalhe do Processo: `FR-1764` e `FR-1771` da `078` (a
  ordem das regiões e a tabela de Editais); `FR-1773` da `078`, na parte da moldura da tabela (a
  página continua sem rolar para o lado); `FR-1069` e `FR-1070` da `058` (os atos dentro de "O que
  fazer agora"); e, da `038`, a apresentação da série de cada Edital em `FR-556` — o pulso e a
  Atenção continuam na página, a série do período encerrado passa a viver só na Supervisão. Cada
  requisito substituído MUST ser marcado como tal na spec de origem, com o link para esta.

### Requisitos de experiência

- **UX-440**: A ordem da página é: topo (título; código, situação e acessos; "Onde estamos"; ciclo e
  inscrições); a grade "O que fazer agora" (com os marcos) ao lado de "Precisa de atenção"; os
  Editais; "Submissões por dia"; "Administração do Processo". No estreito, "Precisa de atenção" vem
  antes dos marcos.
- **UX-441**: O vocabulário é o da página do Edital: "Onde estamos", "O que fazer agora",
  "Administração". As regiões que existem nas duas têm o mesmo desenho.
- **UX-442**: A linha do Edital com atenção tem um traço âmbar à esquerda **e** a marca em texto; o
  traço nunca sozinho.
- **UX-443**: A página não cresce além da largura de estrutura da gestão; acima disso, centraliza.
  Nada é otimizado para ultrawide.
- **UX-444**: Encerrar e Cancelar desabilitados têm o mesmo desenho do botão indisponível da gestão,
  com contraste de texto de leitura.

### Key Entities

Nenhuma entidade nova, nenhuma persistência. A página lê: **Processo Seletivo**, **Edital**,
**Retificação** em curso, o **pulso** e os **sinais** da Supervisão, os atos do Processo e os
**objetos de trabalho** da `104`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1660**: No Processo de 31 Editais do banco de demonstração, a página tem no máximo 4.500 px de
  altura a 1366 × 768 (hoje 10.369 px).
- **SC-1661**: No Processo de 4 Editais com seis condições de atenção, o gestor vê na primeira tela,
  a 1366 × 768, o cartão "O que fazer agora" e o título de "Precisa de atenção" com o total.
- **SC-1662**: A página não rola para o lado a 390, 1366, 1440, 1920 e 3440 px de largura, com a
  barra lateral aberta e recolhida, em todos os cenários.
- **SC-1663**: Para cada papel — gestor, elaborador, homologador, publicador, julgador, auditor,
  comunicação e presidência —, a página faz no máximo três consultas a mais que a de hoje, e o
  número não cresce entre um Processo de 1, 4 e 30 Editais além do que a página de hoje já cresce.
  Para quem avalia, o acréscimo é a carga das Etapas **dela neste Processo**, e só elas: cresce com
  as alocações da própria pessoa, como a faixa da Lista já cresce (`FR-2806` da `104`), e não com as
  alocações dela em outros Processos.
- **SC-1664**: Nenhum ato irreversível aparece fora de "Administração do Processo", e, impedidos,
  nenhum deles é link.
- **SC-1665**: Toda ação e todo destino que a página de hoje oferece a um papel continuam oferecidos
  ao mesmo papel, levando ao mesmo endereço — exceto "Aguardando quem elabora", restrita por
  `FR-5304`, e a série do período encerrado, que fica na Supervisão.
- **SC-1666**: Cada Edital aparece numa linha só, com situação em texto, e quem procura o Edital
  com atenção encontra a marca na linha dele sem rolar até outra região.

## Decisões

As decisões estão com a razão e as alternativas descartadas em [research.md](research.md). O resumo:

- **D-001** — alternativa B: a página reorganizada pelo acompanhamento, e não a evolução da atual.
- **D-002** — as ações da pessoa vêm da faixa da `104`, e não de um segundo mecanismo.
- **D-003** — o andamento de cada Edital fica na página do Edital.
- **D-004** — a série diária só para período em curso.
- **D-005** — "Aguardando quem elabora" só para quem gere o Processo.
- **D-006** — Encerrados e cancelados recolhidos no Processo ativo.

## Assumptions

- O banco de demonstração da rodada 1 (`ps_ux_147`) é o de referência para as medidas; os testes
  automatizados montam os próprios cenários.
- "Gerir o Processo" é poder criar Edital nele ou gerir a comissão dele; não há papel novo.
- A ordem dos grupos segue a do certame — publicados primeiro, porque é onde há trabalho —, e não a
  administrativa.

## Fora do escopo

- O andamento de cada Edital no Processo (fase, mapa, providências por lista).
- Filtro, busca ou paginação na lista de Editais.
- Mudanças na Supervisão, na Lista de Processos ou nas telas de ato.
- Qualquer permissão, situação ou persistência nova.
