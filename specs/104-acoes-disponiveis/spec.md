# Feature Specification: Ações disponíveis — a Lista que começa pelo trabalho de quem a abre

**Feature Branch**: `claude/acoes-disponiveis-104`, empilhada sobre `claude/silly-cerf-78b884` (a
`103`, PR #339, ainda aberto) e sobre a `main` em `0061f28e`

**Created**: 2026-10-30

**Status**: Implementada nesta branch; merge não autorizado. A validação com pessoas (SC-990) espera
o usuário.

**Input**: o diagnóstico de UX de 30/10/2026, "Onde está o meu trabalho?"
(<https://claude.ai/artifact/GqXFAReaxgwMuZLApgUf3z>, exportado como `acoesGPS.pdf`), e o pedido
que adotou a alternativa D dele. Os achados do diagnóstico foram reconferidos contra o código desta
branch antes de escrever os requisitos.

> **Faixa de identificadores.** Esta spec abre em **FR-2801** e **SC-981**. O teto medido em
> 30/10/2026 em `specs/` de todas as worktrees desta máquina é o requisito dois mil setecentos e
> trinta e dois e o critério novecentos e setenta e oito, os dois da `103`. **Nenhum `UX-` é aberto
> aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-541b da `037`"); decisão de outra feature pelo assunto e pela feature.

---

## Por que esta feature existe

O GPS foi construído para **consultar objetos**. Toda tela responde "o que se pode fazer com este
Edital"; nenhuma responde "o que eu tenho a fazer". O trabalho que mora dentro do Edital —
Retificação, recurso, avaliação, divulgação de resultado — aparece em quatro lugares, com quatro
gramáticas. A `103` deu à Retificação uma porta, e a validação visual mostrou o resto do problema.

### O que foi reconferido no código em 30/10/2026

- **A coluna "O que posso fazer" só conhece o Edital.** `acoes.do_edital` monta os atos do Edital;
  a marca da Retificação vem de `atos_retificacao.em_curso_por_edital`, e as duas não se veem. Um
  homologador lê "Nenhuma ação disponível para seus papéis" ao lado de "Retificação em revisão ·
  Homologar".
- **A Lista não prevê o que o detalhe prevê.** `views.lista` chama `do_edital` sem pendências nem
  segregação, de propósito ("Sem pendências nem segregação: a listagem não as exibe"). O detalhe
  mostra "Submeter para revisão" desabilitado com "1 pendência impeditiva"; a Lista o mostra
  habilitado.
- **Calcular a pendência impeditiva custa a validação inteira.** `views._pendencias` monta o
  snapshot do Edital e roda `validate_draft`: dezenas de consultas por Edital. Fazer isso por linha
  é exatamente o N+1 que a Lista não pode ter.
- **O detalhe do Edital se contradiz.** `acoes.proximo_passo` devolve nada para Edital publicado;
  "O que fazer agora" diz "Nenhum ato disponível", e a seção da `103` logo abaixo diz "O próximo ato
  é seu".
- **A devolvida é indistinguível.** `atos_retificacao.resumo` não lê `return_reason`; na Lista, a
  devolvida e o rascunho nunca enviado dizem a mesma coisa.
- **Minhas Etapas é só avaliação** (011, D-006), e o estado vazio diz "Você não possui Etapas
  atribuídas", que quem tem outro trabalho lê como "nada para você".
- **A confirmação de homologar não mostra o que se homologa.** A tabela de alterações só aparece
  na de publicar; as advertências são do conteúdo inteiro, e não do que a Retificação mudou.
- **Já existe o padrão certo, num lugar só.** "Recursos aguardando decisão (n)" é trabalho de
  objeto filho, contado, rotulado pelo que se faz, na coluna de ações. Mas a contagem é uma
  consulta por Edital, como "Inscrições recebidas (n)".
- **A barra lateral não consulta o banco** (076, FR-1715). Um número nela custaria uma consulta em
  toda tela.

### O que esta spec cobre, e o que fica fora

**Cobre**: uma derivação de leitura do trabalho do ator; a faixa "Ações disponíveis para você" na
Lista; a coerência da coluna de ações; a continuidade no detalhe do Edital; a devolvida
reconhecível; a confirmação de homologar com o objeto da decisão; o estado vazio de Minhas Etapas;
o custo da Lista; os testes de jornada e de escala.

**Fica fora**: página inicial nova, painel, central de notificações, contador na barra lateral,
fila ou atribuição nominal, estado novo, mudança de regra de autorização, de segregação (FR-021 da
`001`, AUD-RET-05), de vigência ou de publicação, e a Agenda, que não muda.

---

## Clarifications

### Session 2026-10-30

As perguntas foram respondidas no pedido da feature, ou decididas aqui com o fundamento registrado:

- Q: Qual arquitetura? → A: A alternativa D do diagnóstico: Processos Seletivos continua a entrada,
  aberta por uma faixa de trabalho que só existe quando há ação (D-001).
- Q: Que trabalho a faixa cobre? → A: Edital, Retificação, recursos e avaliação de comissão.
  Classificação, divulgação de resultado e avisos ficam no detalhe de cada Edital, e a faixa diz
  isso (D-002).
- Q: Como a Lista mostra um ato cuja recusa depende da validação do conteúdo? → A: Ela não o
  oferece como ato; leva à conferência no detalhe, com rótulo que diz isso (D-004).
- Q: Minhas Etapas muda de nome? → A: Não nesta feature; muda o estado vazio (D-007).
- Q: Quantos itens a faixa mostra? → A: Cinco, e os demais num "Mostrar as outras N", sem página
  nova (D-009).
- Q: Em que ordem vêm os itens, se nem todos têm instante de espera? → A: Primeiro os que têm
  instante, do mais antigo para o mais recente; depois os demais, pelo ano e número do Edital. A
  ordem é determinística e não sugere urgência.
- Q: Para onde leva cada item? → A: Para a página em que o ato principal se pratica: a composição
  (continuar a elaboração), o detalhe do Edital (homologar, publicar), o detalhe da Retificação, a
  tela de recursos do Edital e a mesa da Etapa. Nunca direto à confirmação (D-003).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem tem um ato a praticar o vê na primeira tela (Priority: P1)

Bruno homologa. Ele entra na gestão e, antes do inventário, lê "Ações disponíveis para você · 1":
"Analisar a Retificação do Edital 26/2026 — em revisão desde 30/10". Um clique e ele está no detalhe
da Retificação. Depois de homologar, a faixa some para ele e para Beatriz, que também homologa.

**Why this priority**: é a reclamação que originou o diagnóstico.

**Independent Test**: com uma Retificação em revisão, a faixa aparece para todo homologador, com um
item, e some depois da homologação.

**Acceptance Scenarios**:

1. **Given** uma Retificação em revisão, **When** um homologador abre a Lista, **Then** a faixa vem
   antes do inventário, com um item que identifica o Edital, a Retificação, a situação, desde quando
   e o ato, e leva ao detalhe da Retificação.
2. **Given** a Retificação homologada, **When** um publicador abre a Lista, **Then** o item diz
   "Publicar a Retificação".
3. **Given** que o ato foi praticado, **When** qualquer pessoa com o mesmo papel abre a Lista,
   **Then** o item não está mais lá.
4. **Given** uma pessoa sem ação disponível, **When** ela abre a Lista, **Then** não há faixa nem
   contador zero, e o inventário é o de sempre.

---

### User Story 2 — A Lista não se contradiz (Priority: P1)

Na coluna "O que posso fazer", Bruno vê "Analisar a Retificação", e não "Nenhuma ação disponível".
A situação do Edital ("Publicado") e a da Retificação ("em revisão") ficam em lugares distintos.
Ana, elaboradora, não vê "Submeter para revisão" como botão num Edital que tem pendência impeditiva:
vê "Conferir e submeter", que a leva às pendências no detalhe.

**Why this priority**: uma faixa certa ao lado de uma coluna errada ensina a desconfiar das duas.

**Independent Test**: para cada papel e situação dos testes da `103` e da `057`, a coluna e a faixa
concordam, e nenhuma das duas afirma ausência de ação quando há.

**Acceptance Scenarios**:

1. **Given** uma Retificação em revisão, **When** um homologador lê a linha do Edital, **Then** a
   coluna tem o ato da Retificação e não diz "Nenhuma ação disponível".
2. **Given** um Edital em elaboração, **When** uma elaboradora lê a linha, **Then** a coluna oferece
   "Elaborar o Edital" e "Conferir e submeter", e nenhum botão de ato que a validação possa recusar.
3. **Given** um Edital homologado por quem também o submeteu, **When** essa pessoa lê a linha,
   **Then** "Publicar" aparece desabilitado com o motivo da segregação.

---

### User Story 3 — O detalhe do Edital diz o que espera a pessoa (Priority: P2)

No detalhe do Edital 26/2026, "O que fazer agora" diz "Uma Retificação deste Edital aguarda você"
com o caminho até ela, em vez de "Nenhum ato disponível". Para quem não tem o ato, diz quem age a
seguir.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com Retificação em revisão, **When** um homologador abre o
   detalhe, **Then** "O que fazer agora" nomeia a Retificação e o ato, e não afirma ausência de ato.
2. **Given** o mesmo Edital, **When** uma publicadora abre o detalhe, **Then** o cartão diz que a
   Retificação aguarda quem homologa.

---

### User Story 4 — A devolvida se reconhece e se retoma (Priority: P2)

Ana abre a Lista e lê, na faixa, "Corrigir a Retificação devolvida — Edital 51/2026", com o começo do
motivo. Na Lista e no detalhe do Edital, a Retificação diz "devolvida". Depois que ela reenvia, a
Retificação diz "reenviada" até ser homologada.

**Acceptance Scenarios**:

1. **Given** uma Retificação devolvida, **When** a elaboradora abre a Lista, **Then** o item diz
   "Corrigir a Retificação devolvida" e mostra o motivo, e leva ao detalhe com "Editar a
   Retificação".
2. **Given** a mesma Retificação reenviada, **When** o homologador abre a Lista, **Then** o item diz
   que ela foi reenviada depois de devolvida.
3. **Given** um rascunho nunca enviado, **When** a elaboradora abre a Lista, **Then** ele diz "em
   elaboração", sem "devolvida".

---

### User Story 5 — Quem homologa vê o que homologa (Priority: P2)

Na confirmação de "Homologar", Bruno vê a tabela das alterações desta Retificação, as advertências
que ela introduz separadas das que o Edital vigente já tinha, e o que acontece depois.

**Acceptance Scenarios**:

1. **Given** uma Retificação em revisão, **When** o homologador abre a confirmação, **Then** a tabela
   "O que esta Retificação altera" está lá, com antes e depois.
2. **Given** advertências que já valiam no Edital vigente, **When** a confirmação é aberta, **Then**
   elas aparecem recolhidas, separadas das que a Retificação introduz.

---

### User Story 6 — Quem acumula papéis vê um item por objeto (Priority: P2)

Dora acumula os quatro papéis. A faixa lista cada objeto uma vez, com o ato principal. A publicação
que ela mesma submeteu e homologou não aparece como ação disponível.

**Acceptance Scenarios**:

1. **Given** uma Retificação em revisão, **When** Dora abre a Lista, **Then** há um item, e não um
   para homologar e outro para devolver.
2. **Given** uma Retificação que Dora submeteu e homologou, **When** ela abre a Lista, **Then** o
   item não está na faixa; a marca da linha diz que aguarda outra pessoa.

---

### User Story 7 — Minhas Etapas diz o que é (Priority: P3)

Sem alocação, Bruno abre Minhas Etapas e lê que a área é de avaliação da comissão e que atos de
Edital e Retificação estão em Processos Seletivos.

---

### Edge Cases

- **Mais de cinco itens**: os cinco primeiros, e os demais num "Mostrar as outras N" que não muda de
  página.
- **Um Edital com Retificação e recurso**: dois itens, porque são dois objetos.
- **Duas Retificações em curso no mesmo Edital**: um item por Retificação.
- **Edital encerrado com Retificação em curso**: o item aparece se o ato está entre as ofertas; o
  servidor recusa com a razão dele, como hoje.
- **Pessoa de outra unidade**: nenhum item de outro escopo, nem na faixa nem na coluna.
- **Ordem**: os itens com instante de espera primeiro, do mais antigo; os demais depois, pelo ano e
  número do Edital.
- **Etapa alocada sem inscrição distribuída**: não é ação (carga zero), não entra.
- **A pendência impeditiva aparece depois da homologação**: a publicação do Edital é contada; a
  conferência no detalhe mostra o impedimento antes de confirmar (D-004, limite registrado).

---

## Requirements *(mandatory)*

### Functional Requirements

#### A derivação do trabalho

- **FR-2801**: O sistema MUST ter uma derivação de leitura do trabalho do ator que reúne, a partir
  das regras que já decidem as telas de detalhe, os objetos em que a pessoa pode atuar agora. Ela
  MUST NOT autorizar nem praticar ato, e MUST NOT ser persistida.
- **FR-2802**: Cada objeto de trabalho MUST aparecer uma vez, com o ato principal da situação dele,
  ainda que admita atos alternativos (homologar ou devolver).
- **FR-2803**: Ato que o domínio recusaria por segregação, situação ou permissão MUST NOT ser contado
  como ação disponível. A previsão MUST vir das mesmas funções que o detalhe usa. O impedimento
  que só a validação do conteúdo revela (pendência impeditiva) é dito na conferência do detalhe, e
  não na Lista nem na faixa (D-004).
- **FR-2804**: A derivação MUST cobrir: Edital em elaboração (continuar a elaboração), em revisão
  (homologar) e homologado (publicar); Retificação em curso (o ato principal da `103`); recursos
  aguardando decisão de um Edital; Etapa de avaliação com inscrições pendentes. A cobertura MUST
  estar declarada na tela.
- **FR-2805**: A derivação MUST respeitar o escopo institucional do ator.
- **FR-2806**: O número de consultas da derivação MUST NOT crescer com o número de Editais do escopo.
  Ele MAY crescer com as alocações de avaliação da própria pessoa, que a tela de Minhas Etapas já
  paga.

#### A faixa na Lista

- **FR-2807**: A Lista MUST abrir, depois do título e dos avisos obrigatórios (inclusive o de
  ambiente de demonstração), com a faixa "Ações disponíveis para você" quando houver ao menos um
  objeto de trabalho, antes dos contadores e do inventário.
- **FR-2808**: Sem objeto de trabalho, a faixa MUST NOT aparecer, nem com contador zero; a Lista
  MUST dizer, numa linha discreta, que não há ação **do tipo que a faixa cobre** para a pessoa agora,
  e o que fica fora dela, sem afirmar que não há trabalho institucional (D-012).
- **FR-2809**: Cada item MUST dizer a natureza do procedimento, o Edital (e a Retificação, quando
  for o caso), a situação, desde quando espera (quando o modelo registra o instante) e o ato, e MUST
  levar à página do objeto onde o ato se pratica. O item inteiro MUST ser um link só, com o ato no
  nome acessível, e nenhum texto dele MUST parecer clicável sem ser (D-011).
- **FR-2810**: A faixa MUST mostrar o total de objetos e no máximo cinco itens; os demais MUST ficar
  acessíveis na própria faixa, sem página nova.
- **FR-2811**: Os rótulos MUST NOT sugerir atribuição nominal ("sua tarefa", "atribuído a você");
  falam do que a pessoa pode fazer.
- **FR-2812**: A faixa MUST dizer o que ela não cobre (classificação, divulgação de resultado e
  avisos) e onde isso está.
- **FR-2813**: A faixa MUST ser uma lista de itens, e não tabela, legível a 375 px sem rolagem
  horizontal, alcançável por teclado na ordem de leitura, sem depender de cor.

#### A coluna de ações

- **FR-2814**: A coluna "O que posso fazer" MUST incluir o ato da Retificação em curso que cabe à
  pessoa, e MUST NOT afirmar "Nenhuma ação disponível" quando a linha tem ação para ela.
- **FR-2815**: Ato do Edital cuja recusa depende da validação do conteúdo (submeter e publicar)
  MUST NOT aparecer na Lista como botão de ato; MUST aparecer como "Conferir e submeter" ou
  "Conferir e publicar", levando ao detalhe, onde a previsão é feita.
- **FR-2816**: Ato do Edital que a segregação recusaria MUST aparecer desabilitado, com o motivo, na
  Lista, como no detalhe.
- **FR-2817**: A situação do Edital e a da Retificação MUST ficar em lugares distintos da linha; a
  marca da Retificação MUST dizer só a situação dela e quem age a seguir.
- **FR-2818**: As contagens de inscrições e de recursos da coluna MUST ser lidas para a página
  inteira, sem consulta por Edital.

#### O detalhe do Edital

- **FR-2819**: Quando o Edital não tem ato para a pessoa e uma Retificação em curso tem, "O que fazer
  agora" MUST nomear a Retificação, o ato e o caminho, e MUST NOT dizer "Nenhum ato disponível".
- **FR-2820**: Quando nenhuma Retificação em curso tem ato para a pessoa, "O que fazer agora" MUST
  dizer quem age a seguir em cada uma, a partir da mesma derivação da `103`.

#### Devolvida e reenviada

- **FR-2821**: Retificação em elaboração com motivo de devolução MUST ser dita "devolvida" na faixa,
  na marca, na seção do Edital e no detalhe, e o item MUST mostrar o motivo e levar à edição do mesmo
  registro.
- **FR-2822**: Retificação em revisão que já foi devolvida MUST ser dita "reenviada depois de
  devolvida".
- **FR-2823**: A distinção MUST sair do motivo de devolução já gravado, sem situação nova.

#### A confirmação

- **FR-2824**: A confirmação de homologar e a de devolver uma Retificação MUST mostrar a tabela das
  alterações declaradas, com antes e depois, como a de publicar.
- **FR-2825**: As advertências da confirmação MUST separar as que a Retificação introduz das que o
  conteúdo vigente já tinha; as segundas MUST ficar recolhidas, com o rótulo que diz que já valiam.
- **FR-2826**: A confirmação de publicar MUST continuar mostrando o conteúdo que passará a vigorar,
  a vigência e as consequências, sem mudança de regra.

#### Minhas Etapas e Agenda

- **FR-2827**: Sem alocação, Minhas Etapas MUST dizer que a área é de avaliação da comissão e que os
  atos de Edital e de Retificação estão em Processos Seletivos, com o link.
- **FR-2828**: Minhas Etapas, a Agenda e a Visão Geral MUST NOT mudar de função; a faixa MUST NOT
  repetir marcos da Agenda.

#### O que não muda

- **FR-2829**: Nenhuma permissão, papel, situação, transição, tabela, fila ou notificação MUST ser
  criada; a segregação MUST continuar a do domínio.

### Key Entities

- **Objeto de trabalho** (derivado): um Edital, uma Retificação, o conjunto de recursos de um Edital
  ou uma Etapa alocada, com o ato principal, a situação, desde quando e o caminho.
- **Ação disponível** (derivada): o ato principal de um objeto de trabalho que a pessoa pode
  praticar agora.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-981**: Com uma Retificação em revisão, 100% dos homologadores do escopo veem o item na faixa,
  na primeira tela, a 1280 e a 375 px; depois do ato, 0%.
- **SC-982**: Para toda combinação de papel e situação dos testes, o conjunto de objetos da faixa é
  exatamente o dos objetos cujo detalhe oferece o ato principal habilitado.
- **SC-983**: Nenhuma linha da Lista afirma "Nenhuma ação disponível" ao lado de uma ação da pessoa.
- **SC-984**: O número de consultas da faixa é o mesmo com 0, 3, 30 e 300 Editais no escopo.
- **SC-985**: O número de consultas da Lista inteira não cresce com o número de Editais publicados
  sem atos de fluxo, para quem não exporta matrícula.
- **SC-986**: Uma Retificação com homologar e devolver conta um item, para quem acumula papéis.
- **SC-987**: A devolvida, a reenviada e o rascunho novo são distinguíveis por texto em 100% das
  telas que os listam.
- **SC-988**: As jornadas da `103` e da `057` continuam passando, e a suíte completa contra
  PostgreSQL não tem regressão.
- **SC-989**: Nenhuma tela desta feature rola para o lado a 375 px.
- **SC-990**: No roteiro com três pessoas reais, cada uma encontra o seu ato, ou sabe que não tem,
  sem ajuda.

---

## Assumptions

- A espera se mede pelo instante gravado do último ato: `submitted_at` e `homologated_at` da
  Retificação; `RevisaoEdital.submitted_at` e `Homologacao.homologated_at` do Edital. A devolução não
  tem instante no modelo, e por isso a devolvida não diz desde quando.
- Editais em elaboração são poucos por vez; continuar a elaboração é ação de todo elaborador do
  escopo.
- O custo da avaliação é o de Minhas Etapas, proporcional às alocações da própria pessoa.

---

## Decisões

### D-001 — A alternativa D: a faixa na Lista, e nenhuma página nova

Processos Seletivos continua a entrada; a faixa vem antes do inventário. Uma página inicial nova
duplicaria a Visão Geral e a Agenda, e trocar a entrada custaria um clique por dia a quem consulta.

### D-002 — A cobertura é a que se deriva sem ler o conteúdo de cada Edital

Edital e Retificação saem da situação e de campos de linha; recursos, de uma agregação; avaliação,
da derivação de Minhas Etapas. Classificação, divulgação de resultado e avisos dependem do conteúdo
publicado de cada Edital e dos atos emitidos por marco, e ficam no detalhe do Edital, onde já estão.
A faixa diz isso, para não se apresentar como "todas as pendências".

### D-003 — Um item por objeto, com o ato principal, e o caminho é a página do objeto

O ato principal é o de `PROXIMO_RESPONSAVEL` (Retificação) e o de `PREFERENCIA_DA_PRINCIPAL`
(Edital). O item leva à página do objeto, e não à confirmação: é lá que a pessoa vê o que vai
decidir, e lá que a previsão completa é feita.

### D-004 — O ato que depende da validação do conteúdo não é ato na Lista

Prever a pendência impeditiva custa montar o snapshot e validar o Edital, dezenas de consultas por
linha. A Lista não faz isso: "Submeter" e "Publicar" do Edital viram "Conferir e submeter" e
"Conferir e publicar", que levam ao detalhe. Na faixa, o Edital em elaboração conta como "continuar
a elaboração", que nunca é recusado; o homologado conta como "publicar", e a pendência que só a
validação descobre aparece na conferência antes da confirmação. É o limite desta feature, e por
isso o rótulo do item é "Conferir e publicar o Edital", o mesmo verbo da coluna, e não "Publicar o
Edital" (revisão de 30/10/2026).

### D-005 — A segregação do Edital é lida em lote

Os participantes de todos os Editais em revisão ou homologados da página saem de duas consultas, e a
mesma `impede_por_segregacao` do detalhe decide.

### D-006 — Devolvida e reenviada saem do motivo já gravado

`return_reason` não é apagado no reenvio; ele distingue a devolvida e a reenviada sem situação nova.

### D-007 — Minhas Etapas não muda de nome

O nome é conhecido da comissão. Muda o estado vazio, que deixa de soar como "nada para você".

### D-008 — As advertências se separam pelo par código e caminho

As do conteúdo vigente são calculadas com a mesma função, sem as alterações; a diferença é o que a
Retificação introduz. As que já valiam ficam recolhidas, **com a mesma severidade de aviso**: a
FR-1309 da `067` exige que o aviso de prazos de recurso apareça como aviso na Retificação, e recolher
muda a ordem de leitura, e não a severidade. A suíte completa apontou o conflito na primeira versão,
que as rebaixava a nota.

### D-009 — Cinco itens e "Mostrar as outras N"

Um `details` nativo, sem script, sem página nova.

### D-011 — O item inteiro é um link, e um só

Revisão de 30/10/2026. Na primeira versão só o título era link, e o ato, à direita, em verde e em
negrito, parecia botão e não respondia ao clique. Dois links para o mesmo destino dobrariam as
paradas do teclado; um só, cobrindo o item, resolve o clique e o teclado. O nome acessível é "ato:
objeto", e a situação, a espera e o detalhe chegam como descrição.

### D-012 — O estado vazio diz o que a faixa olhou

Revisão de 30/10/2026. "Nenhuma ação disponível para você agora" levaria o publicador com resultado a
divulgar — que a faixa não cobre — a concluir que não havia nada. A frase passa a nomear o que a faixa
cobre e o que fica no detalhe de cada Edital. O título "Ações disponíveis para você" fica: com itens,
a nota de cobertura está logo abaixo deles.

### D-013 — Um verbo para a devolvida

Revisão de 30/10/2026. A faixa e o cartão diziam "Corrigir a Retificação devolvida", e a passagem de
bastão da `103`, na seção logo abaixo, "submeter a Retificação para revisão". Para a devolvida, a
passagem de bastão passa a dizer "corrigir a Retificação devolvida e submetê-la de novo": primeiro
corrigir, depois submeter, nessa ordem. O ato de domínio continua o mesmo (`submeter`).

### D-014 — Cinco itens, mais densos

Revisão de 30/10/2026, com medições em 1, 5, 25 e 100 objetos (`verificacao.md`). Com cinco itens de
quatro linhas, a faixa empurrava o inventário para baixo da primeira tela até no desktop (início em
955 px numa tela de 860). O limite de cinco não mudou; mudou a densidade: situação e detalhe numa
linha só, com reticências, e o texto inteiro no HTML. Com cinco itens, o inventário passou a começar
em 821 px no desktop. A faixa fechada mede o mesmo com 25 e com 100 objetos.

### D-010 — As contagens da coluna saem de uma consulta para a página

Inscrições e recursos por Edital passam a ser agregados para todos os Editais da Lista, e a coluna
lê o resultado. Corrige o custo por linha que a faixa tornaria visível.

---

## Pendências do usuário

- **SC-990**: o roteiro com pessoas reais está em `quickstart.md`; não foi executado.
- **Classificação, divulgação de resultado e avisos** fora da faixa (D-002).
- **Publicação do Edital com pendência descoberta só na conferência** (D-004).
- **Renomear Minhas Etapas** (D-007), se a pesquisa com pessoas pedir.
- **AUD-RET-05**, da `103`, segue de governança.
