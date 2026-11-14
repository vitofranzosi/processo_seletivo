# Feature Specification: As regras de deliberação dos pareceres

**Feature Branch**: `claude/165-regras-de-deliberacao-9f8a47`, sobre a `claude/164-efeito-do-desfecho-por-lista`
em `443c84f0`

**Created**: 2026-11-14

**Status**: Especificada em 14/11. Só a spec: plano e implementação esperam o pedido do usuário. PR só
de documento, empilhado sobre o da `164` (#543), que está sobre o da `163` (#542). Nenhum dos dois
tem merge.

**Input**: a decisão **P-3** do usuário em 13/11/2026, no estudo da verificação da autodeclaração
(`doc/estudo-verificacao-da-autodeclaracao-2026-11-13/`, PR #541, regra R-4):

> *O GPS oferece as três regras, e o Edital escolhe uma: confirma por maioria; confirma só por
> unanimidade; recusa só por unanimidade.*

A R-4 do estudo acrescenta que cada membro registra o seu parecer **sem ver o dos outros**, como a
avaliação "individual e independente" da IN Conjunta 261/2025, art. 23. É a terceira entrega da
camada A. A primeira é a `163`, o alcance da Etapa por Modalidade; a segunda é a `164`, o efeito do
desfecho por lista. Esta spec parte das duas e não as redefine.

> **Faixa de identificadores.** Esta spec abre em **FR-7050**, **SC-2350** e **UX-750**. Os tetos
> medidos em 14/11/2026 eram, na `main`, o requisito seis mil novecentos e cinquenta e um, o critério
> dois mil trezentos e quatro e o requisito de experiência setecentos e vinte e sete. A `163`, no PR
> #542, vai até o requisito seis mil novecentos e oitenta e sete. A `164`, no PR #543, vai até o
> requisito sete mil e trinta e dois e reservou até o sete mil e quarenta e nove, o critério dois mil
> trezentos e quarenta e nove e o requisito de experiência setecentos e quarenta e nove. A pasta `165`
> estava livre na `main`, nos PRs abertos (#541 a #544) e nas worktrees locais. As decisões reiniciam
> em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-015 da `013`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> **A `163` e a `164` são citadas só pelo assunto**, porque não estão na `main`.

---

## Por que esta feature existe

Hoje uma Etapa que prevê mais de uma avaliação por inscrição é **impedida por inteiro** na
consolidação (FR-015 da `013`). A Mesa da `012` distribui, cada membro avalia, as conclusões ficam
registradas, e nenhuma vira Resultado: a regra diz que o Edital não declara como combiná-las, e
inventar a combinação seria aplicar ao candidato uma norma que ninguém escreveu.

A heteroidentificação é colegiada por definição:

- a Res. CS 61/2019 cria a comissão local (CLVA), e o Ato 15/2021 a fixa em no mínimo quatro membros,
  um deles o acolhedor, que orienta e não dá parecer;
- o Ofício Circular MEC nº 3/2025 pede comissão de número ímpar, com no mínimo três, e decisão por
  **maioria simples** (item 21);
- a IN Conjunta 261/2025, para concursos, decide por maioria, com avaliação **individual e
  independente, sem interação** (art. 23).

As leituras divergem sobre o que fazer quando a comissão não concorda:

| Regra | De onde vem | Com três pareceres, o desfecho é favorável quando |
|---|---|---|
| **Confirma por maioria** | Ofício MEC 3/2025, item 21; IN 261, art. 23 | dois ou três são favoráveis |
| **Confirma só por unanimidade** | leitura literal da Res. CS 61/2019, art. 15, III, b: indefere-se o que não for constatado "de maneira unânime" | os três são favoráveis |
| **Recusa só por unanimidade** | leitura dos editais do Ifes | ao menos um é favorável |

Sem regra, a heteroidentificação composta no GPS não produz Resultado, e a `164` não tem desfecho
desfavorável a que aplicar o efeito. **Esta spec diz *quando* o desfecho é desfavorável; a `164` diz o
que ele produz.**

### O que esta spec cobre, e o que fica fora

**Cobre:**

- como o Edital declara a regra de deliberação de uma Etapa decisória com mais de uma avaliação;
- o parecer às cegas: o que cada membro, e cada pessoa da gestão que também é membro, deixa de ver;
- a deliberação: de N pareceres para um sentido, e daí para a consequência de hoje;
- o recurso contra o Resultado deliberado, nos caminhos que a `018` já tem;
- a Retificação da regra;
- o que o documento, a gestão e o candidato leem.

**Fica fora**, como registro e não como escopo:

- o **vídeo** (camada B), bloqueado por norma (P-0);
- a **lista fechada de motivos** (R-5 do estudo). A regra não a exige: ela combina sentidos, e não
  motivos (ver *Edge Cases*);
- a **visibilidade da Etapa não restrita** que nenhum marco enumera (R-8);
- o **recurso colegiado** e a nova entrevista síncrona na instância recursal (P-5);
- a **composição da CLVA**: o mínimo de membros, o acolhedor, a diversidade (P-4);
- a **combinação de notas** de uma Etapa pontuada com mais de uma avaliação (média, soma, descarte),
  que continua impedida (ver *Achados*);
- **qual regra os Editais do Ifes usarão**. É pergunta à CPVA, e ela não bloqueia esta spec.

---

## Clarifications

### Session 2026-11-13 (decisões do usuário, no estudo)

- **P-3 — Qual regra de deliberação?** O GPS oferece as três, e o Edital escolhe uma. Qual delas os
  Editais do Ifes usarão continua sendo pergunta à CPVA, e ela não bloqueia a implementação.
  *(Estudo, README, "Decisões"; diagnóstico, §7.)* É o objeto desta spec.
- **P-1** é a `163`, e **P-2** é a `164`. **P-4** e **P-5** podem esperar, e ficam fora.

### Session 2026-11-14 (decisões desta spec, abertas à revisão do usuário)

As decisões D-001 a D-009 são as que a redação exigiu, e cada uma registra a alternativa descartada.
Nenhuma escolhe entre as três regras: todas deixam ao Edital a escolha que a P-3 lhe deu.

---

## User Scenarios & Testing *(mandatory)*

Os exemplos usam o Edital da `164`: três Perfis, cada um com as Modalidades `AC`, `PPI` e `PcD`, e a
**Heteroidentificação** decisória, eliminatória, só para `PPI`, com o efeito *"Deixa de concorrer pela
reserva e continua na ampla concorrência"*. Os rótulos publicados são *"Deferido"* e *"Indeferido"*.
Esta spec acrescenta: a Heteroidentificação prevê **três avaliações por inscrição**, e a CLVA tem três
membros que dão parecer, Ana, Bruno e Carla.

### User Story 1 — Quem elabora declara como a comissão decide (Priority: P1)

Quem elabora o Edital informa três avaliações por inscrição na Heteroidentificação. A tela passa a
perguntar *"Como a comissão chega ao resultado?"*, com três opções e **nenhuma marcada**. A pessoa lê o
item do Edital, escolhe *"«Deferido» quando a maioria dos pareceres for «Deferido»"* e grava. O
documento passa a dizer, na Etapa, que cada inscrição recebe três pareceres, registrados de forma
independente, e que o resultado é o da maioria.

**Why this priority**: sem a declaração, a Etapa continua impedida, e nada do resto existe. É a única
parte que muda o documento oficial.

**Independent Test**: compor a Etapa com cada uma das três regras, publicar, e conferir o conteúdo
publicado, a Revisão e o documento.

**Acceptance Scenarios**:

1. **Given** a Heteroidentificação decisória com três avaliações por inscrição, **When** quem elabora a
   abre, **Then** a pergunta da regra aparece com as três opções e nenhuma marcada.
2. **Given** a mesma Etapa sem regra escolhida, **When** o Edital vai à publicação, **Then** a
   publicação é impedida, e a mensagem nomeia a Etapa e diz que ela precisa declarar como a comissão
   chega ao resultado.
3. **Given** a Etapa com quatro avaliações por inscrição, **When** quem elabora escolhe a maioria,
   **Then** a gravação passa, a publicação é impedida, e a mensagem diz que a maioria exige número
   ímpar de pareceres, porque o empate não tem regra publicada. As duas regras de unanimidade passam.
4. **Given** uma Etapa decisória com uma avaliação por inscrição, ou uma Etapa pontuada, **When** quem
   elabora a abre, **Then** a pergunta da regra não aparece.
5. **Given** o Edital publicado com a regra, **When** o documento é lido, **Then** ele diz, na Etapa,
   quantos pareceres cada inscrição recebe, que cada membro registra o seu sem conhecer o dos demais, e
   a regra com os rótulos publicados. As outras Etapas saem com o texto de antes desta feature.

---

### User Story 2 — Cada membro dá o parecer sem ver o dos outros (Priority: P1)

Ana abre a Mesa da Heteroidentificação e vê as inscrições atribuídas a ela. Na inscrição de Maria, ela
não vê se Bruno ou Carla já concluíram, nem em que sentido, nem o que escreveram. Uma frase diz que os
demais membros não veem o parecer dela, e que ela não vê o deles. Ana conclui *"Indeferido"*, com o
parecer escrito. Depois de concluir, a Mesa continua sem mostrar o dos outros.

Bruno é também a presidência da Etapa. Enquanto o parecer dele sobre Maria estiver pendente, nenhuma
tela da gestão mostra a ele o sentido nem o texto do parecer de Ana ou de Carla sobre Maria: nem a
prontidão, nem as conclusões preservadas, nem a conferência da consolidação.

**Why this priority**: a independência é o que a norma pede de uma deliberação colegiada. Um parecer
dado depois de ler o dos colegas é um voto, e não uma avaliação.

**Independent Test**: com um ator que tem parecer pendente sobre uma inscrição, percorrer toda tela e
consulta que mostra conclusões daquela Etapa, e conferir que nenhuma mostra o sentido ou o texto dos
pareceres dos outros membros sobre aquela inscrição.

**Acceptance Scenarios**:

1. **Given** Ana com parecer pendente sobre Maria, e Bruno com parecer concluído, **When** Ana abre a
   Mesa, **Then** ela não vê o sentido, o texto nem a existência da conclusão de Bruno.
2. **Given** Ana com parecer concluído, **When** ela reabre a Mesa, **Then** continua sem ver o dos
   outros.
3. **Given** Bruno, presidência e membro, com parecer pendente sobre Maria, **When** ele abre as
   conclusões preservadas da Etapa, **Then** as conclusões de Ana e de Carla sobre Maria aparecem sem
   sentido e sem texto, com a indicação de que ele ainda tem parecer pendente sobre aquela inscrição.
   As de outras inscrições, sobre as quais ele não tem pendência, aparecem como hoje.
4. **Given** Bruno sem parecer pendente sobre Maria, **When** ele abre as mesmas telas, **Then** vê as
   conclusões como hoje.
5. **Given** a presidência reabre o parecer de Ana sobre Maria, **When** Ana volta à Mesa, **Then** ela
   está de novo na condição de quem tem parecer pendente, e nenhuma tela lhe mostra o dos outros.

---

### User Story 3 — A deliberação aplica a regra publicada (Priority: P1)

Ana e Bruno concluem *"Indeferido"*; Carla conclui *"Deferido"*. A presidência abre a consolidação. Na
conferência, antes de confirmar, a linha de Maria diz *"Indeferido — 2 de 3 pareceres «Indeferido»,
por maioria"*. Ela confirma. O Resultado de Maria tem a consequência que a `164` dá ao desfecho
desfavorável: *retirada da reserva*. O motivo diz que a comissão deliberou *"Indeferido"* por maioria,
com dois dos três pareceres, e que Maria deixa a reserva e continua na ampla.

Sob *"«Indeferido» só quando todos os pareceres forem «Indeferido»"*, os mesmos três pareceres dariam
*"Deferido"*. Sob *"«Deferido» só quando todos forem «Deferido»"*, dariam *"Indeferido"*.

**Why this priority**: é a decisão P-3 inteira. Sem ela, nenhum Resultado de Etapa colegiada existe.

**Independent Test**: consolidar a mesma combinação de pareceres sob cada regra e comparar o sentido,
a consequência e o motivo com a tabela publicada.

**Acceptance Scenarios**:

1. **Given** dois *"Indeferido"* e um *"Deferido"* sob a maioria, **When** a presidência consolida,
   **Then** o desfecho é *"Indeferido"*, e a consequência é a que a Etapa declara para o desfavorável.
2. **Given** os mesmos pareceres sob *"recusa só por unanimidade"*, **When** a presidência consolida,
   **Then** o desfecho é *"Deferido"*, e a consequência é *habilitada*.
3. **Given** os mesmos pareceres sob *"confirma só por unanimidade"*, **When** a presidência consolida,
   **Then** o desfecho é *"Indeferido"*.
4. **Given** só dois dos três pareceres concluídos, ambos *"Indeferido"*, sob *"confirma só por
   unanimidade"*, **When** a presidência abre a consolidação, **Then** Maria não está pronta, e a
   linha diz que falta um dos três pareceres. O desfecho não é antecipado, ainda que o terceiro não
   possa mudá-lo.
5. **Given** o Resultado de Maria, **When** alguém o lê depois, por si, **Then** ele diz a regra
   aplicada, quantos pareceres houve em cada sentido, a versão cuja regra foi aplicada, e quais
   pareceres o formaram. Nunca quem deu cada um.
6. **Given** um Edital com uma avaliação por inscrição, **When** a presidência consolida, **Then** tudo
   segue como hoje.

---

### User Story 4 — O candidato entende como a comissão decidiu (Priority: P2)

No acompanhamento, Maria lê que, na Heteroidentificação, a comissão decidiu *"Indeferido"* por
maioria, com dois dos três pareceres. Enquanto o prazo de recurso estiver aberto, ela lê o texto de
cada parecer *"Indeferido"*, sem o nome de quem o escreveu, e pode recorrer. A lista pública não diz
nada disso: traz só o desfecho, como hoje.

**Why this priority**: o recurso se escreve contra a fundamentação, e a regra muda o que conta como
fundamentação. Sob a maioria, dois pareceres fundamentam; sob *"confirma só por unanimidade"*, um basta.

**Independent Test**: abrir o acompanhamento e a publicação do marco sob cada regra e conferir o que
cada um mostra.

**Acceptance Scenarios**:

1. **Given** o Resultado deliberado de Maria, visível pela regra de hoje, **When** ela abre o
   acompanhamento, **Then** a linha diz o desfecho, a regra e a contagem, sem autoria.
2. **Given** o prazo de recurso aberto, **When** ela abre o parecer, **Then** lê o texto de cada parecer
   desfavorável da deliberação, sem autoria, e não lê o texto dos favoráveis.
3. **Given** a publicação do marco, **When** qualquer pessoa a lê, **Then** ela não traz a regra, a
   contagem, o texto nem a autoria de nenhum parecer.

---

### User Story 5 — O recurso reabre a deliberação inteira (Priority: P2)

Maria recorre. Ana, Bruno e Carla ficam impedidos de julgar, porque concluíram pareceres naquela
Etapa sobre ela. A CPVA defere, determinando reavaliação. A Heteroidentificação de Maria precisa de três
pareceres novos, de membros que não deram parecer na deliberação anterior, sob a mesma regra e às
cegas. Os três pareceres antigos continuam registrados, e não contam.

**Why this priority**: a reavaliação da `018` pede uma Avaliação nova. Numa Etapa colegiada, o desfecho
é da comissão, e trocar um parecer só deixaria a decisão nova presa à antiga.

**Independent Test**: determinar reavaliação contra um Resultado deliberado, concluir os pareceres
novos, consolidar, e conferir a sucessão e a vedação de piora.

**Acceptance Scenarios**:

1. **Given** a reavaliação determinada, **When** a presidência distribui, **Then** só membros que não
   deram parecer sobre Maria naquela Etapa podem receber a atribuição.
2. **Given** dois pareceres novos concluídos de três, **When** a presidência abre a consolidação,
   **Then** Maria não está pronta, e a linha diz quantos pareceres novos faltam.
3. **Given** os três pareceres novos, **When** a presidência consolida, **Then** nasce o Resultado
   sucessor, citando a decisão, e a vedação de piora compara as consequências como compara hoje.
4. **Given** uma decisão de correção fixada, **When** o julgador decide, **Then** ele fixa o desfecho
   (*"Deferido"* ou *"Indeferido"*), e não pareceres individuais, e a consequência sai da regra.
5. **Given** a comissão sem três membros elegíveis para a reavaliação, **When** a presidência tenta
   distribuir, **Then** a pendência é nomeada como hoje, e nenhum parecer antigo é aproveitado.

---

### User Story 6 — A Retificação da regra não muda a decisão no meio do caminho (Priority: P2)

Publicado o Edital, alguém percebe que o item do Edital diz unanimidade e a composição diz maioria. Uma
Retificação troca a regra antes do primeiro Resultado na Etapa, e passa. Em outro Edital, a mesma troca
vem depois de dez Resultados, e é recusada.

**Why this priority**: a regra é norma. Trocá-la depois de aplicada daria a dois candidatos com os
mesmos pareceres desfechos diferentes.

**Independent Test**: retificar a regra, e o número de avaliações, antes e depois do primeiro
Resultado por avaliação.

**Acceptance Scenarios**:

1. **Given** a Etapa sem Resultado por avaliação, com pareceres já concluídos, **When** uma Retificação
   troca a regra, **Then** ela passa, os pareceres continuam valendo, e a deliberação aplica a regra
   nova.
2. **Given** a Etapa com Resultado por avaliação, favorável ou desfavorável, vigente ou superado,
   **When** uma Retificação troca a regra ou o número de avaliações, **Then** ela é recusada, e a
   mensagem nomeia a Etapa e diz quantos Resultados por avaliação ela já tem.
3. **Given** uma Retificação que troca a regra e uma consolidação ao mesmo tempo, **When** as duas
   chegam, **Then** uma prevalece por inteiro, e nenhum Resultado aplica a regra de uma versão que não
   era a vigente no ato.
4. **Given** um Edital publicado antes desta feature, com uma Etapa decisória de duas avaliações e sem
   regra, **When** uma Retificação declara a regra, **Then** ela passa, e a Etapa deixa de ser
   impedida.

---

### Edge Cases

Cada caso abaixo é requisito, e cita o requisito que o resolve.

- **O empate.** A maioria com número par de pareceres pode empatar, e nenhuma das leituras diz o que o
  empate produz. A publicação recusa a maioria com número par (FR-7052, D-003). As duas regras de
  unanimidade nunca empatam.
- **O desfecho inevitável antes do último parecer.** Sob *"confirma só por unanimidade"*, o primeiro
  *"Indeferido"* já decide. A deliberação espera os N pareceres mesmo assim, e a tela não antecipa o
  desfecho (FR-7062, D-005).
- **Uma avaliação por inscrição.** A regra não se declara, e a consolidação copia a conclusão da única
  avaliação, como hoje (FR-7053, FR-7068).
- **Etapa pontuada com mais de uma avaliação.** Continua impedida pela regra da `013`. Combinar notas é
  outra decisão (FR-7053; *Achados*).
- **Etapa decisória não eliminatória com regra.** Continua impedida pela FR-047 da `013`: a regra diz o
  sentido, e não o que o desfavorável produz (FR-7064).
- **O acervo publicado.** A Etapa decisória com mais de uma avaliação publicada antes desta feature
  continua sem regra e impedida, como hoje, até uma Retificação declarar a regra. Nada se lê por padrão
  (FR-7054, D-002).
- **Pareceres a menos.** A inscrição não está pronta, e a linha diz quantos faltam (FR-7062).
- **Pareceres a mais.** Uma Retificação reduziu o número de avaliações antes do primeiro Resultado, e
  uma inscrição tem mais conclusões elegíveis que o novo número. Ela fica não consolidável, como hoje, e
  o sistema não escolhe quais pareceres contam (FR-7062).
- **Membro impedido depois de concluir.** A inativação da Atribuição por ato nomeado torna o parecer
  inelegível, pela FR-092 da `012`. A deliberação conta só os elegíveis, e a inscrição espera outro
  parecer (FR-7061, FR-7062).
- **Pareceres concluídos sob versões diferentes.** Cada parecer passa pela conferência de
  compatibilidade de hoje, e um incompatível deixa a inscrição não pronta (FR-7063). A regra aplicada é
  a da versão vigente no ato, e o Resultado a identifica (FR-7065, FR-7074).
- **Retificação da regra depois de pareceres concluídos e antes de qualquer Resultado.** Passa. O
  parecer não depende da regra, e continua valendo (FR-7073, FR-7074).
- **Retificação da regra ou do número de avaliações depois do primeiro Resultado.** Recusada, ainda que
  todos os Resultados tenham sido superados (FR-7073, D-008).
- **A presidência ou a auditoria que também é membro.** Enquanto ela tiver parecer pendente sobre uma
  inscrição, as telas da gestão lhe escondem o sentido e o texto dos outros pareceres sobre aquela
  inscrição (FR-7056).
- **A conferência da consolidação.** Só alcança inscrições prontas, isto é, com os N pareceres. Quem as
  confere não tem pendência sobre elas, salvo a de outra inscrição, que não aparece ali (FR-7056,
  FR-7067).
- **A reabertura.** O parecer reaberto pela presidência volta a ser pendente, e o membro volta a não ver
  os dos outros. A reabertura de parecer que já fundamentou Resultado segue a regra de hoje (FR-7058).
- **O membro que leu antes de concluir.** Não acontece pelo sistema: nenhuma tela lhe mostra o parecer
  dos outros enquanto o seu está pendente (FR-7056, FR-7057).
- **Às cegas não é anonimização do candidato.** A Mesa continua mostrando o nome e os dados da
  inscrição, pela FR-030 da `012` (FR-7059).
- **A trilha.** Registra que cada parecer foi concluído e por quem, e nunca o sentido ou o texto. O
  evento da consolidação diz a consequência, e não a contagem (FR-7060). Sob uma regra de unanimidade, a
  consequência às vezes basta para deduzir todos os sentidos, como hoje a de uma avaliação única basta:
  quem lê a trilha da consolidação já pode ler o Resultado.
- **O não comparecimento.** É Ocorrência, registrada pela presidência, com o efeito que a Etapa declara
  para a ausência. Não há pareceres a deliberar, e esta spec não o toca (FR-7064).
- **Motivos diferentes no mesmo sentido.** Ana indefere por fenótipo e Bruno por recusa à filmagem. A
  regra combina **sentidos**, e os dois contam como *"Indeferido"*. O efeito é um por Etapa, pela
  `164`, e a lista fechada de motivos não é precondição (FR-7061; *Achados*).
- **O recurso.** Todos os membros que deram parecer ficam impedidos de julgá-lo (FR-7069). A correção
  fixada fixa o desfecho (FR-7070). A reavaliação é uma deliberação nova inteira, de membros que não
  deram parecer antes (FR-7071), e a vedação de piora a alcança (FR-7072).
- **Reavaliação sem membros elegíveis suficientes.** A pendência é nomeada como hoje, e nenhum parecer
  antigo é reaproveitado (FR-7071).
- **A Etapa restrita.** Só as inscrições que a Etapa alcança recebem pareceres, pela regra da `163`. O
  Resultado deliberado é visível e recorrível pelo marco que o leu, pela regra da `164` (FR-7076).
- **A parte pública.** Não traz a regra, a contagem nem os pareceres (FR-7078).
- **A prévia da classificação.** Não simula deliberação (FR-7080).
- **Rótulos ausentes.** O conteúdo antigo sem rótulos publicados mostra *"favorável"* e
  *"desfavorável"*, como mostra hoje (FR-7066, FR-7075).

## Requirements *(mandatory)*

### Functional Requirements

#### A declaração

- **FR-7050**: A Etapa **decisória** que prevê **mais de uma avaliação por inscrição** DEVE declarar a
  **regra de deliberação**, uma de três (D-001):
  - **maioria**: o desfecho é favorável quando mais da metade dos pareceres é favorável;
  - **unanimidade para o favorável**: o desfecho é favorável só quando todos os pareceres são
    favoráveis;
  - **unanimidade para o desfavorável**: o desfecho é desfavorável só quando todos os pareceres são
    desfavoráveis.
- **FR-7051**: A regra NÃO DEVE ter padrão. A composição NÃO DEVE marcar nenhuma das três, e a
  publicação e a Retificação DEVEM ser impedidas enquanto a Etapa da FR-7050 não declarar a regra, com
  mensagem que nomeie a Etapa e diga o que falta (D-002).
- **FR-7052**: A **maioria** DEVE exigir número **ímpar** de avaliações por inscrição. A publicação e a
  Retificação DEVEM ser impedidas quando a Etapa declarar a maioria com número par, com mensagem que
  diga que o empate não tem regra publicada. As duas regras de unanimidade DEVEM admitir qualquer número
  a partir de dois (D-003).
- **FR-7053**: A Etapa **pontuada** e a Etapa com **uma** avaliação por inscrição NÃO DEVEM declarar
  regra, e a publicação e a Retificação DEVEM ser impedidas quando uma delas a declarar. A Etapa
  pontuada com mais de uma avaliação DEVE continuar impedida na consolidação, pela FR-015 da `013`.
- **FR-7054**: A regra DEVE fazer parte do conteúdo normativo publicado do Edital, num degrau novo da
  versão canônica. O conteúdo publicado antes desse degrau DEVE ser lido **sem regra**, e a Etapa
  decisória com mais de uma avaliação, nele, DEVE continuar impedida na consolidação como hoje. O resumo
  canônico de toda Publicação existente DEVE continuar o mesmo (D-002).
- **FR-7055**: A regra DEVE ser classificada no contrato de mutabilidade como **retificável**, com a
  restrição da FR-7073. O guardião do contrato DEVE cobri-la como cobre os demais campos da Etapa.

#### O parecer às cegas

- **FR-7056**: Enquanto uma pessoa tiver **parecer pendente** sobre uma inscrição numa Etapa, isto é,
  Atribuição ativa sem conclusão vigente, nenhuma tela, consulta ou exportação DEVE lhe mostrar o
  **sentido** nem o **texto** dos pareceres de outros membros sobre aquela inscrição naquela Etapa.
  Isso DEVE valer também para as telas da gestão (prontidão, conclusões preservadas, consolidação,
  julgamento), quando quem as abre é também membro com parecer pendente. A tela DEVE dizer que o
  conteúdo está oculto porque a pessoa ainda tem parecer pendente sobre a inscrição.
- **FR-7057**: Na **Mesa**, o membro NÃO DEVE ver os pareceres dos outros membros, nem a existência nem
  a situação deles, antes ou depois de concluir o seu (D-004).
- **FR-7058**: O parecer **reaberto** pela presidência, pela FR-036 da `012`, DEVE devolver o membro à
  condição de parecer pendente, e a FR-7056 DEVE voltar a valer para ele. A reabertura de parecer que
  já fundamentou Resultado DEVE seguir a regra que vale hoje para a avaliação consolidada.
- **FR-7059**: O parecer às cegas é **entre pares**, e NÃO DEVE esconder do membro a identidade do
  candidato. A Mesa DEVE continuar mostrando os dados da FR-030 da `012`.
- **FR-7060**: A trilha DEVE continuar sem o conteúdo do parecer, pela FR-054 da `012`: o evento de
  cada conclusão diz quem concluiu e quando, e nunca o sentido nem o texto. O evento da consolidação
  deliberada DEVE dizer a consequência, como hoje, e NÃO DEVE trazer a regra aplicada nem a contagem.

#### A deliberação

- **FR-7061**: A **deliberação** DEVE aplicar a regra publicada aos pareceres **elegíveis** da
  inscrição na Etapa, pelo contrato de elegibilidade da `012`, e produzir um sentido, favorável ou
  desfavorável, só pela contagem dos sentidos. Ela NÃO DEVE considerar o motivo, o texto, a ordem nem o
  autor dos pareceres. Nem a presidência nem a comissão escolhem o desfecho.
- **FR-7062**: A inscrição DEVE estar **pronta** para consolidar só com **exatamente** o número de
  pareceres elegíveis que a Etapa prevê. Com menos, ela DEVE estar não pronta, e a linha DEVE dizer
  quantos faltam. Com mais, ela DEVE estar não consolidável, como hoje, e o sistema NÃO DEVE escolher
  quais contam. A deliberação NÃO DEVE ser antecipada quando os pareceres presentes já tornam o desfecho
  inevitável (D-005).
- **FR-7063**: Cada parecer DEVE passar pela conferência de compatibilidade entre a versão sob a qual foi
  concluído e a vigente, como a conclusão única passa hoje. Um parecer incompatível DEVE deixar a
  inscrição não pronta, com a frase de hoje.
- **FR-7064**: O sentido deliberado DEVE produzir a consequência pela regra de hoje: o favorável
  habilita; o desfavorável produz a consequência desfavorável que a Etapa declara, a eliminação ou o
  efeito por lista da `164`. A deliberação NÃO DEVE mudar o que o desfecho produz, e NÃO DEVE alcançar a
  Ocorrência, nem a Etapa decisória não eliminatória, que continua impedida pela FR-047 da `013`.
- **FR-7065**: O Resultado deliberado DEVE identificar **todos** os pareceres que formaram a
  deliberação, a **regra** aplicada, a **contagem** de cada sentido e a **versão normativa** cuja regra
  foi aplicada. A reprodução do ato, lendo esses pareceres e essa versão, DEVE chegar à mesma
  consequência (D-006).
- **FR-7066**: O motivo do Resultado deliberado DEVE citar o rótulo publicado do desfecho, a regra e a
  contagem, por exemplo *"a comissão deliberou Indeferido por maioria: 2 de 3 pareceres Indeferido"*.
  Na retirada da reserva, ele DEVE ser completado como a `164` completa. Ele NÃO DEVE nomear quem deu
  cada parecer. Lido depois, por si, ele DEVE significar o mesmo.
- **FR-7067**: A consolidação deliberada DEVE ser o ato da presidência que existe hoje, em lote, sob o
  mesmo invólucro. A conferência que precede a confirmação e o ato DEVEM usar o mesmo cálculo, e a
  conferência DEVE mostrar, por inscrição, o desfecho deliberado e a contagem.
- **FR-7068**: Com **uma** avaliação por inscrição, a consolidação DEVE continuar copiando a conclusão
  da única avaliação, pela FR-016 da `013`, com o mesmo Resultado e o mesmo motivo de hoje.

#### Recurso

- **FR-7069**: O Resultado deliberado DEVE ser recorrível como o Resultado de hoje. **Todo** membro que
  concluiu parecer sobre aquela inscrição naquela Etapa DEVE ficar impedido de julgar o recurso, pela
  regra de impedimento da `018` aplicada a cada um.
- **FR-7070**: A **correção fixada** numa Etapa colegiada DEVE fixar o **desfecho** (o sentido), e não
  pareceres individuais. A consequência DEVE continuar derivada da regra da versão que a decisão cita,
  pela FR-059 da `018`.
- **FR-7071**: A **reavaliação determinada** numa Etapa colegiada DEVE exigir uma **deliberação nova
  inteira**: o número de pareceres que a Etapa prevê, todos novos, de membros que não concluíram parecer
  sobre aquela inscrição naquela Etapa, às cegas pela FR-7056, sob a regra vigente. Os pareceres
  anteriores DEVEM continuar registrados e NÃO DEVEM contar. Sem membros elegíveis suficientes, a
  pendência DEVE ser nomeada como hoje (D-007).
- **FR-7072**: A vedação de piora da `018`, na ordem de gravidade que a `164` lhe deu, DEVE alcançar o
  Resultado da deliberação nova como alcança o da reavaliação de hoje (FR-073 da `018`).

#### A Retificação

- **FR-7073**: A Retificação que muda a **regra de deliberação**, ou o **número de avaliações por
  inscrição** de uma Etapa decisória, DEVE ser impedida desde o **primeiro** Resultado por avaliação
  registrado nela, favorável ou desfavorável, vigente ou superado. A mensagem DEVE nomear a Etapa e dizer
  quantos Resultados por avaliação ela já tem. Antes disso, a Retificação DEVE passar, e os pareceres já
  concluídos DEVEM continuar valendo (D-008).
- **FR-7074**: A Retificação da regra e a consolidação na mesma Etapa DEVEM ser serializadas: o
  Resultado DEVE aplicar a regra da versão vigente no instante do ato, e a Retificação DEVE ser recusada
  se, ao ser publicada, a FR-7073 a impedir.

#### O que o documento, a gestão e o candidato leem

- **FR-7075**: O documento do Edital DEVE dizer, na Etapa que declara a regra, quantos pareceres cada
  inscrição recebe, que cada membro registra o seu sem conhecer o dos demais, e a regra, escrita com os
  rótulos publicados. A Etapa sem regra DEVE sair com o texto de antes desta feature. A Revisão, a
  página pública do Edital e a tela de Retificação DEVEM dizer a regra com as mesmas palavras.
- **FR-7076**: O acompanhamento DEVE mostrar ao titular, na linha do Resultado deliberado, o desfecho,
  a regra e a contagem, sem autoria. A visibilidade DEVE ser a que o Resultado da Etapa já tem para o
  titular, inclusive a da Etapa restrita pela `164`.
- **FR-7077**: O parecer entregue ao titular pela FR-522 da `036` DEVE ser, no Resultado deliberado
  desfavorável, o **texto de cada parecer desfavorável** da deliberação, sem autoria, nas mesmas
  condições de prazo. Os pareceres favoráveis DEVEM aparecer só na contagem (D-009).
- **FR-7078**: A parte pública, a publicação do marco inclusive, NÃO DEVE trazer a regra aplicada a uma
  pessoa, a contagem, o texto nem a autoria de parecer nenhum. Ela DEVE trazer só o desfecho, como hoje.
- **FR-7079**: A prontidão e a organização da Etapa DEVEM contar as inscrições **aguardando pareceres**
  à parte das prontas e das não consolidáveis por outro motivo. Toda leitura nova da consequência que
  esta spec criar DEVE entrar no inventário do guardião dos leitores da consequência da `164`.
- **FR-7080**: A prévia da classificação NÃO DEVE simular deliberação nesta entrega. A equivalência
  entre a prévia e o caminho oficial DEVE continuar valendo para todo cenário que ela simula.

### Requisitos de experiência

- **UX-750**: A pergunta da regra DEVE aparecer só na Etapa decisória com mais de uma avaliação, como
  três opções exclusivas, nenhuma marcada, escritas com os rótulos publicados: *"«Deferido» quando a
  maioria dos pareceres for «Deferido»"*, *"«Deferido» só quando todos os pareceres forem «Deferido»"* e
  *"«Indeferido» só quando todos os pareceres forem «Indeferido»"*. Com número par de avaliações, a
  primeira DEVE dizer, ao lado, que exige número ímpar.
- **UX-751**: A Mesa da Etapa colegiada DEVE dizer, uma vez, que os demais membros não veem o parecer da
  pessoa, e que ela não vê o deles.
- **UX-752**: A conferência da consolidação DEVE mostrar, por inscrição, *"«desfecho» — k de N pareceres
  «desfecho», por «regra»"*, e, antes da confirmação, quantas inscrições terão cada desfecho.
- **UX-753**: O texto ao candidato DEVE dizer *"a comissão decidiu"*, e nunca *"o avaliador"* nem o nome
  de um membro.

### Key Entities

- **Etapa de avaliação**: ganha a **regra de deliberação**, só quando decisória e com mais de uma
  avaliação por inscrição. É norma publicada, retificável até o primeiro Resultado por avaliação, e o
  número de avaliações dela passa a ter a mesma restrição.
- **Avaliação (parecer)**: não muda. O que muda é quem a vê enquanto a de outro membro está pendente.
- **Resultado da Etapa**: o Resultado por avaliação passa a poder ter como fonte **vários** pareceres,
  com a regra, a contagem e a versão cuja regra aplicou. As consequências são as de hoje.
- **Decisão de recurso**: a correção fixada fixa o desfecho da deliberação; a reavaliação determinada
  exige deliberação nova.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2350**: **Todo** Edital publicado antes desta feature, recomposto depois dela, produz o mesmo
  resumo canônico e o mesmo documento, byte a byte.
- **SC-2351**: Para três e para cinco pareceres, em **todas** as combinações de sentidos, sob cada uma
  das três regras, o desfecho da consolidação, o da conferência e o da reprodução do ato coincidem com a
  tabela da FR-7050 em **100%** dos casos.
- **SC-2352**: Num percurso de **toda** tela e consulta que mostra conclusões de uma Etapa, com um ator
  que tem parecer pendente sobre uma inscrição, **zero** mostram o sentido ou o texto de outro parecer
  sobre ela.
- **SC-2353**: No Edital com uma avaliação por inscrição, a consolidação produz Resultados **idênticos**
  aos que o sistema de antes desta feature produz para o mesmo cenário.
- **SC-2354**: **100%** das Retificações que mudariam a regra ou o número de avaliações de Etapa decisória
  com Resultado por avaliação são recusadas, inclusive quando todos foram superados, e nenhuma linha de
  Resultado muda.
- **SC-2355**: **Zero** publicações com Etapa decisória de mais de uma avaliação sem regra, ou com a
  maioria e número par.
- **SC-2356**: *(humano)* Uma pessoa da CPVA ou de uma CLVA, lendo só o documento publicado do Edital
  de exemplo, responde corretamente qual é o desfecho de dois *"Indeferido"* e um *"Deferido"* sob a
  regra publicada.

## Assumptions

- **A `163` e a `164` entram antes.** Esta spec usa o alcance, a consequência *retirada da reserva*, a
  ordem de gravidade do recurso e a visibilidade da Etapa restrita. Se uma delas mudar no merge, esta
  spec é revista.
- **O parecer não depende da regra.** O membro julga o fenótipo, e não o desfecho coletivo. Por isso a
  troca da regra antes do primeiro Resultado não invalida pareceres.
- **O número de avaliações conta só quem dá parecer.** O acolhedor do Ato 15/2021 não é Atribuição. A
  composição da CLVA é a P-4, e fica fora.
- **Hoje a Mesa já mostra a cada membro só a própria Atribuição.** Quem mostra pareceres de outros são
  as telas da gestão, e é nelas que a FR-7056 acrescenta a restrição.
- **A escolha da CPVA não bloqueia.** Qualquer das três regras que ela indicar é representável.
- **Um sentido por parecer.** A forma decisória da `012` tem dois valores, e a regra combina só eles.

## Out of Scope

- O vídeo assíncrono (camada B).
- A lista fechada de motivos (R-5).
- A visibilidade e a recorribilidade da Etapa não restrita que nenhum marco enumera (R-8).
- O recurso colegiado e a nova entrevista síncrona (P-5).
- A composição da CLVA (P-4).
- A combinação de notas de Etapa pontuada com mais de uma avaliação.
- A deliberação na prévia da classificação.
- O aviso por e-mail do desfecho (avisos complementares da `066`).

## Dependências

- **Esta spec depende de:**
  - a `012`, pela Mesa, pela Atribuição, pela elegibilidade, pela reabertura e pela trilha;
  - a `013`, pela consolidação e pela regra da Etapa;
  - a `018`, pelo recurso, pelo impedimento, pela reavaliação e pela vedação de piora;
  - a `036`, pelo parecer entregue ao titular;
  - a `163`, pelo alcance;
  - a `164`, pelo efeito do desfecho, pela ordem de gravidade e pela visibilidade da Etapa restrita.
- **Desta spec dependem** o recurso colegiado (P-5) e a camada B, cujo vídeo só confirma: a
  confirmação pelo vídeo é uma deliberação com uma regra.

## Achados (registro, e não escopo)

- **A combinação de notas.** A Etapa pontuada com mais de uma avaliação continua impedida. Média, soma,
  descarte da maior e da menor e diferença máxima entre avaliadores são decisões que nenhum Edital lido
  para esta spec escreve. O barema por curso pode precisar delas.
- **A regra por motivo.** O 28/2026, 6.9.14, lista motivos de indeferimento além do fenótipo. Se a CPVA
  responder que a recusa à filmagem indefere sem deliberação, o motivo passa a decidir antes da regra, e
  a R-5 vira precondição. Pergunta à CPVA, ao lado da P-3.
- **A IN 261, art. 32.** Para concursos, quando as duas instâncias divergem sem unanimidade, prevalece a
  autodeclaração. É regra entre instâncias, e não dentro da comissão: pertence ao recurso colegiado
  (P-5).
- **A presidência que é membro.** Nenhuma norma lida proíbe. Se a CPVA entender que a presidência não
  deve dar parecer, é regra de composição (P-4).

## Decisões

### D-001 — A regra é declaração da Etapa, com três formas

A P-3 diz que o Edital escolhe. Declarar na Etapa, e não no Edital inteiro, é o que o domínio pede: o
número de avaliações já é da Etapa, e um Edital pode ter a heteroidentificação colegiada e a análise
documental com um analista. As três formas são as da P-3, escritas pelo sentido, e não pelo nome
*"confirma"*: a mesma regra serve à análise documental com dois analistas, em que *"confirmar"* não diz
nada. *Descartados:* (a) regra por Modalidade, que nenhum Edital escreve; (b) uma quarta forma,
*"a presidência desempata"*, que nenhuma das leituras traz e que tiraria a decisão da comissão.

### D-002 — Sem padrão, e o acervo continua impedido

A `164` teve padrão porque a P-2 o fixou. A P-3 não fixou, e a pergunta à CPVA está aberta: marcar uma
das três seria o sistema respondendo por ela. Pela mesma razão, o conteúdo já publicado não ganha regra
por leitura: a Etapa colegiada dele continua impedida, que é o que ela era no dia em que foi publicada,
e a Retificação a destrava. *Descartados:* a maioria como padrão, que é a orientação do MEC e não a
leitura dos editais do Ifes; e ler o acervo pela maioria, que mudaria norma publicada sem Retificação.

### D-003 — A maioria exige número ímpar

Com quatro pareceres, dois e dois não é maioria de nenhum lado. As saídas seriam favorecer a
autodeclaração, favorecer o indeferimento ou dar o voto de minerva a alguém, e nenhum Edital lido
escreve qualquer delas. O Ofício MEC pede comissão ímpar. Recusar na publicação é dizer ao Edital o que
ele não declarou, em vez de decidir por ele. *Descartados:* o empate favorável, que é a leitura do art.
32 da IN 261 aplicada fora do lugar dele; e o voto de minerva da presidência.

### D-004 — Na Mesa, o membro nunca vê o parecer do outro

A R-4 diz *"até registrar"*. Mostrar depois de registrar abriria o caminho de concluir, ler o dos
colegas e pedir a reabertura. A Mesa é o instrumento de quem avalia, e o parecer do colega não serve ao
trabalho de ninguém ali. Quem precisa ver os pareceres, a presidência e a auditoria, vê pelas telas da
gestão, e nelas a restrição é só a da pendência. *Descartado:* mostrar na Mesa depois de concluir, que é
a leitura literal da R-4 e a mais fraca.

### D-005 — A deliberação espera os N pareceres

Sob *"confirma só por unanimidade"*, o primeiro *"Indeferido"* decide. Consolidar ali dispensaria os
outros membros, e o Edital publicou N pareceres, e não *"até decidir"*. E a tela que dissesse *"já
decidido"* contaria a quem ainda vai avaliar que alguém indeferiu, que é o que o parecer às cegas
impede. *Descartado:* a deliberação antecipada.

### D-006 — O Resultado cita todos os pareceres e a versão cuja regra aplicou

Hoje o Resultado por avaliação cita uma Avaliação, e a versão dela. Com N pareceres, citar um seria
escolher qual valeu. E a versão da regra pode não ser a de nenhum parecer: a Retificação antes do
primeiro Resultado troca a regra e mantém os pareceres. A reprodução do ato precisa dos dois, os
pareceres e a regra, e o Princípio II da Constituição pede que o ato se reproduza pelo que gravou.
*Descartados:* citar o último parecer concluído; e gravar só a contagem, que não diz quais pareceres
contaram.

### D-007 — A reavaliação é uma deliberação nova

A `018` impede quem concluiu a Avaliação original de concluir a reavaliação. Aplicada a cada um dos N,
a regra já pede membros novos. Trocar só um parecer deixaria a decisão nova formada em maioria pela
antiga, que o recurso deferiu. *Descartados:* (a) reavaliar só os pareceres desfavoráveis, que poria a
regra a trabalhar sobre um painel montado depois de conhecido o desfecho; (b) devolver aos mesmos
membros, que a `018` proíbe.

### D-008 — A regra e o número de avaliações se retificam até o primeiro Resultado

É a razão da `164` para o efeito, aplicada aqui com uma diferença: a regra decide também o desfecho
favorável, e por isso o impedimento conta todo Resultado por avaliação, e não só o desfavorável. O
número de avaliações entra junto, porque três pareceres para uns e cinco para outros é a mesma
desigualdade. Antes do primeiro Resultado nada foi decidido, e o parecer não depende da regra.
*Descartados:* não retificável, que deixaria sem correção a divergência entre o item do Edital e a opção
marcada; e retificável só para o futuro, que é a desigualdade acima.

### D-009 — Ao titular, o texto de cada parecer desfavorável, sem autoria

A `036` entrega ao titular o parecer que fundamenta o desfavorável, porque é contra ele que se recorre.
Com N pareceres, a fundamentação do desfavorável são os pareceres desfavoráveis: sob a maioria, dois de
três; sob *"confirma só por unanimidade"*, às vezes um só. A contagem diz ao titular que houve
divergência, o que é argumento de recurso, e a ausência de nome protege quem deu o parecer sem tirar
nada da defesa. A parte pública não recebe nada disso, como a R-9 do estudo pede. *Descartados:* (a) só o
desfecho e a regra, sem contagem nem texto, que deixaria o titular sem ter contra o que recorrer; (b)
todos os textos, que entregaria o favorável, que a regra da `012` não obriga a escrever e que ninguém
escreveu para o candidato ler; (c) os textos com autoria, que expõe o membro e não ajuda o recurso.
