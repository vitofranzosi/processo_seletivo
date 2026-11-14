# Feature Specification: As regras de deliberação dos pareceres

**Feature Branch**: `claude/165-regras-de-deliberacao-9f8a47`, sobre a `claude/164-efeito-do-desfecho-por-lista`
em `df54d2c1`, que tem a correção da revisão de código da `164`

**Created**: 2026-11-14

**Status**: Especificada em 14/11. Só a spec: plano e implementação esperam o pedido do usuário. PR só
de documento, empilhado sobre o da `164` (#543), que está sobre o da `163` (#542). Nenhum dos dois
tem merge. Revista no mesmo dia pela revisão do PR #545, com seis achados.

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
Nenhuma escolhe entre as três regras: todas deixam ao Edital a escolha que a P-3 lhe deu. A D-010 veio
do `/speckit-clarify`, abaixo.

### Session 2026-11-14 (/speckit-clarify)

- Q: Quando a autoridade recursal defere um recurso contra o Resultado de uma Etapa colegiada e
  manda reavaliar, quem faz a reavaliação? → A: **Ninguém, nesta entrega.** Na Etapa colegiada, o
  deferimento que corrige o Resultado é a **correção fixada**: a autoridade recursal informa o sentido,
  e o sistema deriva a consequência pela regra publicada. A **reavaliação determinada** fica
  indisponível, recusada antes de gravar e explicada na interface. O indeferimento e as demais espécies
  da `018` mantêm as regras de cabimento delas. A correção cria Resultado sucessor sem alterar os
  pareceres antigos nem simular votação nova. Se a CPVA de fato quiser uma nova avaliação, isso fica
  fora desta entrega, e o sistema não a converte em correção fixada: quem reavalia, com que composição
  e por que procedimento é a P-5 (FR-7070, FR-7071, FR-7072, D-007).
- Q: Quando o resultado deliberado é desfavorável, o que o candidato lê sobre os pareceres? → A: **A
  regra aplicada, a contagem dos dois sentidos e o texto de cada parecer desfavorável, sem identificação
  dos membros.** Os favoráveis aparecem só na contagem. A exibição segue as condições da `036`: prazo
  recursal aberto, ou recurso do titular contra aquele Resultado ainda pendente. Com quatro condições:
  o motivo (desfecho, regra e contagem) e os textos dos pareceres ficam separados, sem concatenação; os
  textos são os das conclusões que fundamentaram aquele Resultado, e uma reabertura posterior não os
  substitui; "sem autoria" oculta identificadores e metadados dos membros, mas não garante anonimato
  quando o próprio texto identifica alguém, e por isso a orientação de preenchimento o considera,
  preservando o original; e a restrição é só da apresentação ao candidato, sem reduzir o que a
  autoridade recursal vê (FR-7066, FR-7076, FR-7077, FR-7081, UX-754, D-009).
- Q: Quando a mesma pessoa é presidência ou auditoria da Etapa e também membro do painel, como o
  sistema impede que ela leia os pareceres dos colegas antes de dar o dela? → A: **Enquanto ela tiver
  parecer pendente sobre uma inscrição naquela Etapa, nem as telas nem as respostas do servidor lhe
  entregam o sentido ou o texto dos pareceres dos colegas, qualquer que seja o papel acumulado, e a
  interface explica o motivo.** A proteção é do servidor, e não só do HTML: link direto, detalhe,
  exportação e resposta consumida por tela a respeitam. Ficam ocultas também contagens por sentido,
  prévias do desfecho e resumos que permitam deduzir os pareceres alheios. O escopo é inscrição ×
  Etapa: a presidência continua gerindo e consolidando as outras inscrições prontas, e a que espera o
  parecer dela já não está pronta, o que dispensa um bloqueio geral. **E o caminho inverso fica fechado**:
  quem já recebeu o sentido ou o texto de parecer de outro membro sobre a inscrição não pode receber
  atribuição nela, nem ter o próprio parecer reaberto (FR-7056, FR-7082, FR-7083, D-010).
- Q: Uma Etapa sob a regra da maioria pode ter número par de pareceres, e o que o empate produz? → A:
  **Não pode: a maioria exige número ímpar**, e a publicação e a Retificação recusam o par. O Edital
  com número par tem as duas regras de unanimidade (FR-7052, D-003).
- Q: Depois de concluir o próprio parecer, o membro passa a ver na Mesa os pareceres dos colegas sobre
  a mesma inscrição? → A: **Nunca.** A Mesa não mostra o parecer dos colegas, nem a existência nem a
  situação deles, antes ou depois de concluir, nem depois do Resultado. Quem precisa vê-los, a
  presidência, a auditoria e a autoridade recursal, vê pelas telas da gestão e do julgamento, com as
  restrições da pendência e da exposição (FR-7057, D-004).

### Session 2026-11-14 (revisão do PR #545, pedida pelo usuário)

Seis achados, corrigidos sem mudar nenhuma decisão:
- **A reavaliação travava em "pareceres a mais".** Os pareceres antigos continuam elegíveis, e três
  antigos com três novos davam seis. → No cumprimento, contavam só os concluídos depois da decisão.
  *Superado pela resposta do clarify acima*: a reavaliação na Etapa colegiada saiu desta entrega, e a
  regra da contagem ficou registrada como condição para a P-5 (*Achados*).
- **A FR-7065 contradizia a invariante de proveniência da `013`**: uma Avaliação por Resultado, e a
  versão dela. → A spec declara que a revê, e dá a redação nova (FR-7065, D-006).
- **O julgador com parecer pendente** julgaria sem ver o que julga. → Fica impedido também (FR-7069).
- **"Pareceres a mais" não tinha saída.** → A Retificação que o produziria é impedida (FR-7073), e o
  resíduo de conteúdo antigo sai pela inativação da Atribuição por ato nomeado (FR-7062).
- **"Nunca quem deu cada um" × a identificação dos pareceres.** → A autoria fica com a presidência e a
  auditoria, e nunca chega ao titular nem à parte pública (FR-7081).
- **A base da spec** passou a ser a correção da revisão de código da `164`: a vedação de piora voltou a
  recusar a nota menor qualquer que seja a consequência, e o motivo da retirada recebe o nome da
  reserva já resolvido (FR-7066, FR-7072).

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
6. **Given** Bruno com parecer pendente sobre Maria, **When** ele pede por link direto o detalhe da
   conclusão de Ana ou a exportação das conclusões da Etapa, **Then** a resposta do servidor não traz o
   sentido nem o texto dos pareceres de Ana e de Carla sobre Maria, nem uma contagem por sentido que
   os revele.
7. **Given** Bruno, presidência, com parecer pendente sobre Maria e nenhum sobre João, **When** João está
   pronto, **Then** Bruno vê os pareceres de João e o consolida normalmente.
8. **Given** Carla, auditora sem atribuição, que abriu as conclusões preservadas e leu os pareceres de
   Ana e de Bruno sobre Maria, **When** a presidência tenta atribuir Maria a Carla na Heteroidentificação,
   **Then** a distribuição recusa, e a mensagem diz que Carla já teve acesso aos pareceres dos colegas
   sobre essa inscrição.
9. **Given** Ana com parecer concluído sobre Maria, que depois leu como presidência os de Bruno e de
   Carla, **When** a presidência tenta reabrir o parecer de Ana, **Then** a reabertura é recusada, e a
   tela oferece a inativação da Atribuição por ato nomeado e a atribuição a outro membro.

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
   pareceres o formaram. A presidência e a auditoria veem quem deu cada um, como veem hoje; o titular e
   a parte pública, nunca.
6. **Given** um Edital com uma avaliação por inscrição, **When** a presidência consolida, **Then** tudo
   segue como hoje.

---

### User Story 4 — O candidato entende como a comissão decidiu (Priority: P2)

No acompanhamento, Maria lê que, na Heteroidentificação, a comissão decidiu *"Indeferido"* por
maioria, com dois dos três pareceres *"Indeferido"* e um *"Deferido"*. Enquanto o prazo de recurso
estiver aberto, ou enquanto o recurso dela contra esse Resultado estiver pendente, ela lê, à parte do
motivo, o texto de cada parecer *"Indeferido"*, sem o nome nem outro dado de quem o escreveu, e pode
recorrer. A lista pública não diz nada disso: traz só o desfecho, como hoje.

**Why this priority**: o recurso se escreve contra a fundamentação, e a regra muda o que conta como
fundamentação. Sob a maioria, dois pareceres fundamentam; sob *"confirma só por unanimidade"*, um basta.

**Independent Test**: abrir o acompanhamento e a publicação do marco sob cada regra, dentro e fora das
condições da `036`, e conferir o que cada um mostra.

**Acceptance Scenarios**:

1. **Given** o Resultado deliberado de Maria, visível pela regra de hoje, **When** ela abre o
   acompanhamento, **Then** a linha diz o desfecho, a regra e a contagem dos dois sentidos, sem
   autoria.
2. **Given** o prazo de recurso aberto, **When** ela abre o parecer, **Then** lê o texto de cada parecer
   desfavorável da deliberação, separado do motivo, sem nome nem outro dado dos membros, e não lê o
   texto dos favoráveis.
3. **Given** o prazo encerrado e o recurso de Maria contra esse Resultado ainda pendente, **When** ela
   abre o parecer, **Then** continua lendo os textos. Encerrados os dois, eles somem, e a tela diz por
   quê, como na `036`.
4. **Given** um dos pareceres desfavoráveis reaberto pela presidência depois do Resultado, **When**
   Maria abre o parecer, **Then** lê o texto da conclusão que fundamentou o Resultado, e não o do estado
   atual da Avaliação.
5. **Given** o recurso de Maria em julgamento, **When** a CPVA abre o recurso, **Then** ela vê todos os
   pareceres da deliberação, favoráveis e desfavoráveis, com a autoria.
6. **Given** a publicação do marco, **When** qualquer pessoa a lê, **Then** ela não traz a regra, a
   contagem, o texto nem a autoria de nenhum parecer.

---

### User Story 5 — O recurso corrige o desfecho, e não refaz a votação (Priority: P2)

Maria recorre. Ana, Bruno e Carla ficam impedidos de julgar, porque concluíram pareceres naquela
Etapa sobre ela. A CPVA, julgando com `recurso:julgar`, defere e informa o sentido *"Deferido"*. O
sistema deriva a consequência pela regra publicada e cria o Resultado sucessor. Os três pareceres
continuam registrados como estavam, e nada no sucessor finge que houve uma votação nova.

A CPVA não consegue determinar reavaliação: a tela não oferece a espécie na Etapa colegiada, e o
pedido que chegar assim é recusado antes de gravar qualquer decisão.

**Why this priority**: o recurso contra o desfecho da verificação é obrigação da Res. CS 61/2019,
art. 17, que põe a decisão na CPVA. A reavaliação colegiada pediria uma segunda comissão e um rito que a
P-5 ainda não definiu.

**Independent Test**: julgar recursos contra um Resultado deliberado com cada espécie de decisão da
`018`, e conferir o sucessor, a recusa da reavaliação e os pareceres intactos.

**Acceptance Scenarios**:

1. **Given** o recurso admitido contra o Resultado deliberado de Maria, **When** a CPVA defere com
   correção fixada e informa *"Deferido"*, **Then** nasce o Resultado sucessor *habilitada*, citando a
   decisão, e os três pareceres não mudam.
2. **Given** o mesmo recurso, **When** a CPVA tenta deferir determinando reavaliação, **Then** a decisão
   é recusada antes de ser gravada, e a mensagem diz que a reavaliação de Etapa colegiada não está
   disponível e que o recurso pode ser decidido por correção fixada.
3. **Given** a tela de julgamento de um recurso contra Resultado de Etapa colegiada, **When** a CPVA a
   abre, **Then** a reavaliação determinada não aparece entre as espécies, e uma frase diz por quê.
4. **Given** o mesmo recurso, **When** a CPVA o indefere, **Then** o Resultado continua vigente, como
   hoje.
5. **Given** a correção fixada que tornaria a situação de Maria pior que a do Resultado recorrido,
   **When** a CPVA conclui o julgamento, **Then** o desfecho é indeferimento, pela vedação de piora da
   `018`.
6. **Given** um recurso contra Resultado de Etapa com **uma** avaliação por inscrição, **When** a CPVA
   determina reavaliação, **Then** tudo segue como hoje.

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
- **Pareceres a mais.** Uma Retificação que reduzisse o número de avaliações abaixo das conclusões que
  uma inscrição já tem é impedida, e a mensagem diz quantas inscrições ficariam assim (FR-7073). O caso
  só sobra em conteúdo anterior a esta feature. Ali, a inscrição fica não consolidável, o sistema não
  escolhe quais pareceres contam, e a saída é a de hoje: a presidência inativa a Atribuição excedente
  por ato nomeado, com motivo, pela FR-092 da `012`, a partir da linha da inscrição (FR-7062).
- **A reavaliação na Etapa colegiada.** Não existe nesta entrega. A decisão que a determinasse é
  recusada antes de gravar, e a tela de julgamento não a oferece (FR-7071). O sistema não converte a
  vontade de reavaliar em correção fixada: se a CPVA quer uma nova avaliação, o recurso espera a P-5 ou
  é decidido por outra espécie, por escolha dela.
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
  inscrição, o servidor lhe nega o sentido e o texto dos outros pareceres sobre aquela inscrição, por
  qualquer caminho, e também a contagem por sentido que os revele. As outras inscrições seguem como
  hoje, e ela consolida as prontas (FR-7056).
- **Leu como presidência e recebeu atribuição depois.** A restrição pela pendência não cobre esse
  caminho, porque quando ela leu não havia pendência. A leitura fica registrada como exposição, e a
  distribuição recusa atribuir a inscrição a quem foi exposto (FR-7082, D-010).
- **Concluiu, leu como presidência, e o parecer é reaberto.** A reabertura a devolveria à pendência já
  sabendo o que os colegas decidiram. Ela é recusada, e a correção sai pela substituição de quem avalia
  (FR-7083).
- **A conferência da consolidação.** Só alcança inscrições prontas, isto é, com os N pareceres. Quem as
  confere não tem pendência sobre elas, salvo a de outra inscrição, que não aparece ali (FR-7056,
  FR-7067).
- **A reabertura.** O parecer reaberto pela presidência volta a ser pendente, e o membro volta a não ver
  os dos outros. A reabertura de parecer que já fundamentou Resultado segue a regra de hoje (FR-7058).
- **O membro que leu antes de concluir.** Não acontece pelo sistema: nada lhe entrega o parecer dos
  outros enquanto o seu está pendente, e quem já o recebeu não chega a ter parecer pendente sobre
  aquela inscrição (FR-7056, FR-7057, FR-7082).
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
- **O recurso.** Todos os membros que deram parecer ficam impedidos de julgá-lo, e também quem tem
  parecer pendente sobre aquela inscrição naquela Etapa, que julgaria sem ver o que julga (FR-7069). A correção
  fixada fixa o desfecho e cria o sucessor sem tocar os pareceres (FR-7070); a vedação de piora a alcança
  (FR-7072). O indeferimento e as demais espécies da `018` seguem as regras delas (FR-7071).
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
  Atribuição ativa sem conclusão vigente, o sistema NÃO DEVE lhe entregar o **sentido** nem o **texto**
  dos pareceres de outros membros sobre aquela inscrição naquela Etapa, qualquer que seja o papel que
  ela acumula:
  - a restrição DEVE ser aplicada **no servidor**, e não só na tela. Ela DEVE valer para toda página,
    link direto, detalhe, exportação e resposta consumida por tela, inclusive as da gestão (prontidão,
    conclusões preservadas, consolidação, julgamento);
  - ela DEVE alcançar a **revelação indireta**: contagem por sentido, prévia do desfecho e resumo que
    permitam deduzir o sentido de um parecer alheio sobre aquela inscrição DEVEM ficar ocultos para ela.
    O número de pareceres concluídos e o que falta, sem sentido, PODEM aparecer na gestão;
  - o escopo DEVE ser **inscrição × Etapa**. As outras inscrições, e as outras Etapas, aparecem a ela
    como hoje, e a presidência DEVE poder gerir e consolidar as inscrições prontas, sem bloqueio geral.
    A inscrição que espera o parecer dela não está pronta, pela FR-7062.

  A tela DEVE dizer que o conteúdo está oculto porque a pessoa ainda tem parecer pendente sobre a
  inscrição.
- **FR-7057**: Na **Mesa**, o membro NÃO DEVE ver os pareceres dos outros membros, nem a existência nem
  a situação deles, antes ou depois de concluir o seu, e também depois do Resultado. A Mesa NÃO DEVE
  ser, por isso, caminho de exposição (D-004).
- **FR-7058**: O parecer **reaberto** pela presidência, pela FR-036 da `012`, DEVE devolver o membro à
  condição de parecer pendente, e a FR-7056 DEVE voltar a valer para ele. A reabertura de parecer que
  já fundamentou Resultado DEVE seguir a regra que vale hoje para a avaliação consolidada, e a de
  parecer cujo autor já foi exposto segue a FR-7083.
- **FR-7082**: O sistema DEVE guardar, por pessoa, inscrição e Etapa, o fato de ter **entregado** a uma
  pessoa o sentido ou o texto de parecer de outro membro sobre aquela inscrição: a **exposição**. Ela
  DEVE ser registrada em toda entrega que a FR-7056 controla, e só pelo fato, sem o conteúdo entregue
  (FR-054 da `012`). A distribuição DEVE **recusar** atribuir a inscrição, naquela Etapa, a pessoa já
  exposta, com mensagem que diga por quê, e a recusa DEVE valer também para a redistribuição depois de
  um impedimento (D-010).
- **FR-7083**: A **reabertura** de parecer cujo autor foi exposto aos pareceres dos colegas sobre aquela
  inscrição depois de concluir DEVE ser recusada, com mensagem que diga por quê. O caminho para corrigir
  o parecer, nesse caso, DEVE ser o de hoje para substituir quem avalia: a inativação da Atribuição por
  ato nomeado, com motivo, pela FR-092 da `012`, e a atribuição a outro membro não exposto.
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
  quais contam. A linha DEVE dizer quantos pareceres há e quantos a Etapa prevê, e a tela da presidência
  DEVE oferecer, a partir dela, a inativação da Atribuição excedente por ato nomeado, com motivo, pela
  FR-092 da `012`. A deliberação NÃO DEVE ser antecipada quando os pareceres presentes já tornam o
  desfecho inevitável (D-005).
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
  consequência (D-006). Isso **revê a invariante de proveniência da `013`**, a da decisão sobre o
  Resultado sem Avaliação, que hoje diz: o Resultado por avaliação cita exatamente uma Avaliação, e a
  versão dele coincide com a da Avaliação fonte. A redação nova DEVE ser:
  - o Resultado por avaliação de **uma** avaliação continua citando exatamente uma Avaliação, com a
    versão dela, como hoje;
  - o Resultado **deliberado** cita os N pareceres que contaram, e a versão dele é a vigente no ato,
    cuja regra foi aplicada. Cada parecer citado DEVE ter sido concluído sob versão compatível com ela,
    pela FR-7063, e a versão de um parecer PODE diferir da do Resultado;
  - um parecer DEVE fundamentar no máximo um Resultado, nos dois ramos, como hoje uma Avaliação
    fundamenta no máximo um.

  A garantia de banco que hoje confere essa coerência DEVE passar a conferir a redação nova, com a mesma
  força: nenhum Resultado deliberado sem pareceres, nenhum parecer de outra inscrição ou de outra Etapa,
  e nenhuma versão de outro Edital.
- **FR-7066**: O motivo do Resultado deliberado DEVE citar o rótulo publicado do desfecho, a regra e a
  contagem, por exemplo *"a comissão deliberou Indeferido por maioria: 2 de 3 pareceres Indeferido"*.
  Na retirada da reserva, ele DEVE ser completado como a `164` completa: a causa, e depois a reserva
  perdida e a ampla mantida. Ele NÃO DEVE nomear quem deu cada parecer, e NÃO DEVE conter o texto de
  parecer nenhum: o texto vai à parte, pela FR-7077. Lido depois, por si, ele DEVE significar o mesmo.
- **FR-7081**: A **autoria** de cada parecer DEVE continuar visível à presidência, à auditoria e à
  autoridade recursal autorizada, nas telas da gestão e do julgamento, com a restrição da FR-7056. A
  autoridade recursal DEVE ver todos os pareceres da deliberação, favoráveis inclusive, com o texto e a
  autoria: a restrição da FR-7077 é da apresentação ao candidato, e NÃO DEVE reduzir o que ela vê. Ela NÃO DEVE aparecer ao titular, no acompanhamento, no
  parecer entregue pela FR-7077 nem no motivo, e NÃO DEVE aparecer na parte pública.
- **FR-7067**: A consolidação deliberada DEVE ser o ato da presidência que existe hoje, em lote, sob o
  mesmo invólucro. A conferência que precede a confirmação e o ato DEVEM usar o mesmo cálculo, e a
  conferência DEVE mostrar, por inscrição, o desfecho deliberado e a contagem.
- **FR-7068**: Com **uma** avaliação por inscrição, a consolidação DEVE continuar copiando a conclusão
  da única avaliação, pela FR-016 da `013`, com o mesmo Resultado e o mesmo motivo de hoje.

#### Recurso

- **FR-7069**: O Resultado deliberado DEVE ser recorrível como o Resultado de hoje. **Todo** membro que
  concluiu parecer sobre aquela inscrição naquela Etapa DEVE ficar impedido de julgar o recurso, pela
  regra de impedimento da `018` aplicada a cada um. **Também** DEVE ficar impedido quem tem parecer
  pendente sobre aquela inscrição naquela Etapa, pela FR-7056: julgaria sem ver o que julga, e o
  impedimento DEVE valer enquanto a pendência existir.
- **FR-7070**: No deferimento que corrige o Resultado de uma Etapa colegiada, a espécie DEVE ser a
  **correção fixada**: a autoridade recursal informa o **desfecho** (o sentido favorável ou
  desfavorável), e não pareceres individuais, e a consequência DEVE ser derivada da regra da versão que a
  decisão cita, pela FR-059 da `018`. A correção DEVE criar o Resultado sucessor pelo mecanismo da
  `018`, citando a decisão. Ela NÃO DEVE alterar, inativar nem substituir os pareceres originais, e o
  sucessor NÃO DEVE se apresentar como deliberação nem trazer contagem de pareceres: o fundamento dele
  é a decisão recursal.
- **FR-7071**: A **reavaliação determinada** NÃO DEVE estar disponível contra Resultado de Etapa
  colegiada nesta entrega (D-007):
  - a tela de julgamento NÃO DEVE oferecê-la, e DEVE dizer por quê;
  - o comando DEVE recusá-la **antes de gravar** qualquer decisão, com mensagem que diga que ela não está
    disponível e que o recurso pode ser decidido por correção fixada. Nenhuma decisão impossível de
    cumprir DEVE existir;
  - o sistema NÃO DEVE converter a determinação de reavaliar em correção fixada, nem em outra espécie.

  O indeferimento, a inadmissão e as demais espécies da `018` DEVEM manter as regras de cabimento
  delas. A motivação da decisão, os impedimentos da FR-7069, a vedação de piora e a preservação dos
  pareceres continuam valendo. Na Etapa de **uma** avaliação, a reavaliação determinada DEVE continuar
  como hoje.
- **FR-7072**: A vedação de piora da `018` DEVE alcançar a correção fixada contra Resultado deliberado,
  pelas duas perguntas que ela faz, cada uma bastando: a consequência mais grave, na ordem de gravidade
  que a `164` lhe deu, e a pontuação menor, pela FR-070 da `018`. Na Etapa decisória não há pontuação, e
  só a primeira se aplica. Concluindo o julgamento por situação pior, o desfecho DEVE ser indeferimento,
  pela FR-072 da `018`.

#### A Retificação

- **FR-7073**: A Retificação que muda a **regra de deliberação**, ou o **número de avaliações por
  inscrição** de uma Etapa decisória, DEVE ser impedida desde o **primeiro** Resultado por avaliação
  registrado nela, favorável ou desfavorável, vigente ou superado. A mensagem DEVE nomear a Etapa e dizer
  quantos Resultados por avaliação ela já tem. Antes disso, a Retificação DEVE passar, e os pareceres já
  concluídos DEVEM continuar valendo (D-008), salvo um caso: a Retificação que **reduz** o número de
  avaliações abaixo das conclusões elegíveis que alguma inscrição já tem DEVE ser impedida, e a mensagem
  DEVE dizer quantas inscrições ficariam com pareceres a mais.
- **FR-7074**: A Retificação da regra e a consolidação na mesma Etapa DEVEM ser serializadas: o
  Resultado DEVE aplicar a regra da versão vigente no instante do ato, e a Retificação DEVE ser recusada
  se, ao ser publicada, a FR-7073 a impedir.

#### O que o documento, a gestão e o candidato leem

- **FR-7075**: O documento do Edital DEVE dizer, na Etapa que declara a regra, quantos pareceres cada
  inscrição recebe, que cada membro registra o seu sem conhecer o dos demais, e a regra, escrita com os
  rótulos publicados. A Etapa sem regra DEVE sair com o texto de antes desta feature. A Revisão, a
  página pública do Edital e a tela de Retificação DEVEM dizer a regra com as mesmas palavras.
- **FR-7076**: O acompanhamento DEVE mostrar ao titular, na linha do Resultado deliberado, o desfecho,
  a regra e a contagem dos dois sentidos, sem autoria. A visibilidade DEVE ser a que o Resultado da Etapa
  já tem para o titular, inclusive a da Etapa restrita pela `164`.
- **FR-7077**: O parecer entregue ao titular pela FR-522 da `036` DEVE ser, no Resultado deliberado
  desfavorável, o **texto de cada parecer desfavorável** da deliberação (D-009):
  - nas **mesmas condições** da `036`: prazo recursal aberto para aquele Resultado, ou recurso do titular
    contra ele ainda pendente; encerradas as duas, os textos somem, e a tela diz por quê;
  - **à parte do motivo**, como a `036` já os separa, e nunca concatenados a ele;
  - **os das conclusões que fundamentaram aquele Resultado**, citadas por ele pela FR-7065. Uma reabertura
    posterior NÃO DEVE substituir o texto apresentado;
  - **sem autoria**: sem nome, identificador, instante nem outro metadado que identifique o membro. O
    sistema NÃO DEVE alterar o texto original para isso.

  Os pareceres favoráveis DEVEM aparecer só na contagem.
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
- **UX-754**: Na Mesa da Etapa colegiada, a orientação de preenchimento do parecer DEVE dizer que o texto
  desfavorável será lido pelo candidato sem o nome de quem o escreveu, e que ele não deve conter o
  nome, a assinatura nem outro dado que identifique o membro. A orientação NÃO DEVE bloquear a
  conclusão: o anonimato pelo texto é responsabilidade de quem escreve, e o sistema guarda o original.

### Key Entities

- **Etapa de avaliação**: ganha a **regra de deliberação**, só quando decisória e com mais de uma
  avaliação por inscrição. É norma publicada, retificável até o primeiro Resultado por avaliação, e o
  número de avaliações dela passa a ter a mesma restrição.
- **Avaliação (parecer)**: não muda. O que muda é quem a vê enquanto a de outro membro está pendente.
- **Exposição**: o fato de o sistema ter entregado a uma pessoa o sentido ou o texto de parecer de outro
  membro sobre uma inscrição numa Etapa. Guarda a pessoa, a inscrição, a Etapa e o instante, nunca o
  conteúdo. Impede a atribuição e a reabertura (FR-7082, FR-7083).
- **Resultado da Etapa**: o Resultado por avaliação passa a poder ter como fonte **vários** pareceres,
  com a regra, a contagem e a versão cuja regra aplicou, e a invariante de proveniência da `013` é
  revista pela FR-7065. As consequências são as de hoje.
- **Decisão de recurso**: contra Resultado de Etapa colegiada, a correção fixada informa o desfecho e
  cria o sucessor sem tocar os pareceres; a reavaliação determinada não é admitida nesta entrega.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2350**: **Todo** Edital publicado antes desta feature, recomposto depois dela, produz o mesmo
  resumo canônico e o mesmo documento, byte a byte.
- **SC-2351**: Para três e para cinco pareceres, em **todas** as combinações de sentidos, sob cada uma
  das três regras, o desfecho da consolidação, o da conferência e o da reprodução do ato coincidem com a
  tabela da FR-7050 em **100%** dos casos.
- **SC-2352**: Num percurso de **toda** tela, link direto, exportação e resposta do servidor que mostra
  conclusões de uma Etapa, com um ator que tem parecer pendente sobre uma inscrição e acumula os papéis de
  presidência e de auditoria, **zero** entregam o sentido, o texto ou uma contagem por sentido de outro
  parecer sobre ela, e **100%** das tentativas de atribuir a inscrição a uma pessoa já exposta são
  recusadas.
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
- A reavaliação determinada contra Resultado de Etapa colegiada (D-007).
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

- **A reavaliação colegiada, para a P-5.** Quando o rito existir, os pareceres da deliberação anterior
  continuarão elegíveis pelo contrato da `012`, e nada os inativa. A contagem do cumprimento precisará
  considerar só os pareceres concluídos depois da decisão, como a FR-068 da `018` faz com a avaliação
  única. Sem isso, três antigos e três novos dariam seis pareceres, e a inscrição travaria em "pareceres
  a mais". Achado da revisão do PR #545.
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

Confirmada pelo usuário em 14/11, no `/speckit-clarify`.

Com quatro pareceres, dois e dois não é maioria de nenhum lado. As saídas seriam favorecer a
autodeclaração, favorecer o indeferimento ou dar o voto de minerva a alguém, e nenhum Edital lido
escreve qualquer delas. O Ofício MEC pede comissão ímpar. Recusar na publicação é dizer ao Edital o que
ele não declarou, em vez de decidir por ele. *Descartados:* o empate favorável, que é a leitura do art.
32 da IN 261 aplicada fora do lugar dele; e o voto de minerva da presidência.

### D-004 — Na Mesa, o membro nunca vê o parecer do outro

Confirmada pelo usuário em 14/11, no `/speckit-clarify`. A R-4 diz *"até registrar"*. Mostrar depois
de registrar abriria o caminho de concluir, ler o dos colegas e pedir a reabertura, e com a exposição da
D-010 todo membro ficaria impedido de ter o parecer reaberto por erro material. A Mesa é o instrumento de quem avalia, e o parecer do colega não serve ao
trabalho de ninguém ali. Quem precisa ver os pareceres, a presidência e a auditoria, vê pelas telas da
gestão, e nelas valem a pendência e a exposição. *Descartados:* mostrar na Mesa depois de concluir, que é
a leitura literal da R-4 e a mais fraca; e mostrar depois do Resultado, que não serve ao trabalho de
ninguém na Mesa: o que se faz com o Resultado depois dele é recurso, e quem o julga vê os pareceres pela
tela do julgamento.

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

Isso **revê uma invariante da `013`**, e a spec o diz em vez de contorná-la. A decisão da `013` sobre o
Resultado sem Avaliação fez da versão um campo do Resultado e mandou a garantia de banco conferir que,
na origem por avaliação, ela coincide com a da fonte. A razão era a reprodutibilidade: a norma que
fundamentou é a da Avaliação. Com N pareceres, a norma que fundamentou é a da regra aplicada, e cada
parecer só precisa ter sido concluído sob versão compatível com ela, que é a conferência que a
conclusão única já passa hoje. O ramo de uma avaliação não muda (FR-7065).

*Descartados:*
- citar o último parecer concluído, que escolhe um;
- gravar só a contagem, que não diz quais pareceres contaram;
- exigir que todos os pareceres tenham a versão da regra, que obrigaria a refazer pareceres depois de
  uma Retificação que trocou só a regra, e o parecer não depende dela.

### D-007 — Na Etapa colegiada, o recurso corrige o desfecho, e não reavalia

Decidido pelo usuário em 14/11, no `/speckit-clarify`. A `018` impede quem concluiu a Avaliação original
de concluir a reavaliação. Aplicada a cada um dos N, a reavaliação pediria N membros novos, e a CLVA do
Ato 15/2021, com quatro membros e um deles o acolhedor, não teria como reavaliar ninguém. O estudo já
recomendava que a primeira entrega usasse o julgador da `018`, e o art. 17 da Res. CS 61/2019 põe a
decisão na CPVA. Quem reavalia, com que composição e por que procedimento é a P-5.

A recusa é **antes de gravar**, porque uma decisão de reavaliação gravada e impossível de cumprir
deixaria a inscrição com uma pendência que nada resolve. E ela **não converte**: se a CPVA quer uma nova
avaliação, a correção fixada não é a mesma coisa, e decidir por ela é escolha da CPVA, e não do sistema.

*Descartados:*
- **deliberação nova inteira**, de membros que não deram parecer, que exigiria uma segunda comissão
  antes de a P-5 definir o rito;
- **reavaliar só os pareceres desfavoráveis**, que poria a regra a trabalhar sobre um painel montado
  depois de conhecido o desfecho;
- **devolver aos mesmos membros**, que a `018` proíbe.

### D-008 — A regra e o número de avaliações se retificam até o primeiro Resultado

É a razão da `164` para o efeito, aplicada aqui com uma diferença: a regra decide também o desfecho
favorável, e por isso o impedimento conta todo Resultado por avaliação, e não só o desfavorável. O
número de avaliações entra junto, porque três pareceres para uns e cinco para outros é a mesma
desigualdade. Antes do primeiro Resultado nada foi decidido, e o parecer não depende da regra.
*Descartados:* não retificável, que deixaria sem correção a divergência entre o item do Edital e a opção
marcada; e retificável só para o futuro, que é a desigualdade acima.

### D-009 — Ao titular, o texto de cada parecer desfavorável, sem autoria

Decidido pelo usuário em 14/11, no `/speckit-clarify`. A `036` entrega ao titular o parecer que
fundamenta o desfavorável, porque é contra ele que se recorre. Com N pareceres, a fundamentação do
desfavorável são os pareceres desfavoráveis: sob a maioria, dois de três; sob *"confirma só por
unanimidade"*, às vezes um só. A contagem diz ao titular que houve divergência, o que é argumento de
recurso, e a ausência de nome protege quem deu o parecer sem tirar nada da defesa. A parte pública não
recebe nada disso, como a R-9 do estudo pede.

Quatro condições acompanham a decisão:
- **motivo e parecer continuam separados**, como na `036`. O motivo é a regra aplicada à contagem; o
  parecer é a razão que alguém escreveu, e é contra ele que se recorre;
- **o texto é o que fundamentou o Resultado.** Uma reabertura posterior, pela regra de hoje, não troca
  em silêncio o que o titular leu;
- **"sem autoria" é sobre metadados, e não garante anonimato.** O texto pode identificar quem o
  escreveu, e o sistema não o reescreve: a orientação de preenchimento avisa (UX-754), e o original fica;
- **a restrição é da apresentação ao candidato.** A autoridade recursal vê todos os pareceres, com a
  autoria (FR-7081).

*Descartados:*
- **sem a contagem**, que esconderia do titular a divergência, que é argumento de recurso;
- **todos os textos**, que exporia o favorável, que a regra da `012` não obriga a escrever e que ninguém
  escreveu para o candidato ler, sem necessidade demonstrada nesta entrega;
- **só o desfecho e a regra**, que deixaria o titular sem ter contra o que recorrer;
- **os textos com autoria**, que expõe o membro e não ajuda o recurso.

### D-010 — A exposição impede a atribuição e a reabertura

Pedido pelo usuário em 14/11, no `/speckit-clarify`, ao responder a pergunta 3: o caso precisava ser
fechado. A forma de fechá-lo é desta spec, aberta à revisão. A restrição pela pendência protege quem ainda vai
avaliar, e não cobre dois caminhos em que a leitura vem antes da pendência: a presidência que lê os
pareceres e recebe a atribuição depois, numa redistribuição; e o membro que conclui, lê como presidência
e tem o parecer reaberto. Nos dois, a pessoa avaliaria sabendo o que os colegas decidiram, e a spec
prometeria uma independência que o fluxo deixa contornar.

O fato que decide é a **entrega**, e não o papel: quem recebeu o sentido ou o texto está exposto, e quem
só tem a permissão de ver não está. Por isso o sistema registra a entrega, e não infere de quem poderia
ter visto. O registro guarda o fato, sem o conteúdo, como a trilha da `012`.

*Descartados:*
- **proibir o acúmulo de papéis no painel**, que a equipe pequena não comporta;
- **recusar atribuir a quem tem papel de gestão na Etapa**, que barraria também quem nunca abriu as
  telas, e é a mesma proibição com outro nome;
- **confiar no termo de sigilo**, que é necessário e não é verificável.
