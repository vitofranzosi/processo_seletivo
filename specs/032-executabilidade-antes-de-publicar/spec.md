# Feature Specification: Executabilidade antes de publicar

**Feature Branch**: `032-executabilidade-antes-de-publicar`

**Created**: 2026-09-18

**Status**: Draft

**Input**: Reauditoria exploratória de UX de 2026-09-16 —
[doc/auditoria-exploratoria-ux-2026-09-16.md](../../doc/auditoria-exploratoria-ux-2026-09-16.md) —,
problema estrutural **E-7**, melhoria **13.7**, achados **ACH-49**, **ACH-50**, **ACH-47** e
**ACH-46**.

## Por que esta feature existe

A validação de publicabilidade pergunta se o Edital está **preenchido**. Ela nunca pergunta se ele
**funciona**.

Hoje `IMPEDE` cobre a existência de título, de Perfil e de Evento. Não cobre nada do que faz o
certame acontecer depois. A auditoria encontrou quatro consequências disso, e as quatro têm a mesma
forma: **a prosa da tela afirma a regra, e a validação não a aplica**.

| Achado | O que a tela afirma | O que o sistema deixou passar |
|---|---|---|
| **ACH-49** · S4 | *"Um Perfil sem marco não classifica"* | Edital publicado com `classificationMilestones = []`. A Revisão respondeu `IMPEDE: []` |
| **ACH-50** · S4 | *"o método é conteúdo publicado do Edital"* | Documento de um Edital de sorteio sem algoritmo, sem fonte, sem semente, sem normalização e sem regra de substituição |
| **ACH-47** · S4 | a soma do quadro é validada, e a reserva publicada com fundamento legal | Cotas publicadas que o sistema não apura nem convoca — dois dos três botões de ocupação sempre falham |
| **ACH-46** · S3 | *"sem ele, a Etapa seguinte recebe todos os habilitados"* | A consequência que importa — sem regra de corte **não há convocação** — nunca é dita |

O agravante é comum aos quatro: **publicação é ato imutável**. Quando o operador descobre, o Edital
já está público, e a saída é Retificar. Nos três primeiros, o erro é irrecuperável sem um ato
administrativo que ninguém planejou.

Esta especificação **não muda regra de domínio alguma**. O que ela muda é **quando o operador
descobre**. É por isso que ela é a de maior retorno da auditoria: hoje a prosa já explica tudo isso,
e o Edital sai errado mesmo assim. O que falta não é texto — é a verificação.

**Uma capacidade nova também entra**, e não é de validação: o documento publicado de um Edital de
sorteio passa a carregar o método. Sem ele, quem recebe o resultado não tem base normativa para
conferir o sorteio contra o que o Edital prometeu.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Revisão recusa o Edital que não vai funcionar (Priority: P1)

Uma servidora termina de compor um Edital e abre a etapa de Revisão antes de submeter. Em vez de
`IMPEDE: []` sobre um Edital que não classifica ninguém, ela lê o que está faltando, de que Perfil
se trata e em que etapa do assistente corrigir. Ela também lê, como aviso, que o marco sem regra de
corte não terá convocação — e isso chega **antes** da submissão, enquanto ainda é edição de
rascunho e não Retificação.

**Why this priority**: fecha o achado de maior severidade da auditoria pelo caminho mais curto, e
faz sozinho a diferença entre um Edital publicado inútil e um Edital publicado. Entregue isolado,
já elimina a classe inteira de "publiquei e não percebi".

**Independent Test**: reencenar o Edital 03/2026 da auditoria — um Perfil, nenhum marco — e conferir
que a Revisão recusa nomeando Perfil, falta e lugar; e reencenar o marco sem regra de corte,
conferindo o aviso que nomeia a convocação.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração cujo Perfil não declara marco classificatório algum, **When** a
   validação de conteúdo é executada, **Then** ela devolve erro impeditivo que nomeia o Perfil, diz
   que sem marco ninguém é classificado e indica a etapa de Classificação como lugar de correção.
2. **Given** o mesmo Edital, **When** a pessoa tenta submeter, **Then** a submissão é recusada e a
   recusa é a mesma frase da Revisão.
3. **Given** um Edital em elaboração com marco que não declara regra de corte alguma, **When** a
   validação é executada, **Then** ela devolve **aviso** — não impeditivo — que nomeia a cadeia
   inteira: sem corte não há geração, sem geração não há faixa, e sem faixa não há convocação.
4. **Given** um marco cuja regra de corte declara explicitamente **não governar Etapa alguma**
   (`FR-224` da `014`), **When** a validação é executada, **Then** nenhum aviso é emitido: a regra
   existe, a faixa nasce, e a convocação alcança.
5. **Given** um rascunho ainda pela metade, **When** a pessoa grava, **Then** a gravação é aceita
   como sempre foi — a família nova é impeditiva apenas no ato de publicação.
6. **Given** a tela de ocupação de um marco sem regra de corte, **When** ela é aberta, **Then** ela
   **não oferece** "Pedir a faixa seguinte" e declara por que a ação não existe ali.

---

### User Story 2 - O documento publicado carrega o método do sorteio (Priority: P2)

Uma candidata recebe o Edital publicado de um certame por sorteio. O documento diz que a ordem
daquele marco é produzida por sorteio, e traz o método inteiro: algoritmo e versão, fonte pública
externa da semente, qual ocorrência a fixa e quando, como a ocorrência decorre da data programada,
como o material bruto vira semente e o que vale se a ocorrência faltar. Ela consegue conferir o
sorteio contra a norma sem pedir nada à instituição.

**Why this priority**: é a única história que entrega capacidade observável a quem está fora da
instituição, e é o que dá base normativa à verificação pública que a `021` construiu. Depende do
mesmo lugar do código que a P1 toca, mas se entrega sozinha.

**Independent Test**: publicar um Edital de sorteio e ler o documento gerado, conferindo os sete
dados do método e a declaração da forma da ordem.

**Acceptance Scenarios**:

1. **Given** um Edital cujo marco ordena por sorteio e declara método próprio, **When** o documento
   é gerado, **Then** a seção daquele marco imprime a forma da ordem e os sete dados do método.
2. **Given** um marco que ordena por sorteio e **referencia o método comum do Edital** (`FR-429` da
   `030`), **When** o documento é gerado, **Then** ele imprime o método que efetivamente governa
   aquele marco e diz que é o comum do Edital.
3. **Given** um marco que ordena por sorteio e declara método próprio divergente do comum, **When**
   o documento é gerado, **Then** ele imprime o método próprio e **nomeia a divergência**.
4. **Given** um marco que ordena por sorteio, **When** o documento é gerado, **Then** ele **não**
   imprime linha de combinação de pontuações: aquela ordem não vem de nota.
5. **Given** um marco que ordena por sorteio e cujo método não será publicado — nem próprio nem
   comum —, **When** a validação de publicação é executada, **Then** ela recusa, nomeando o marco e
   dizendo que o sorteio sem método publicado não tem como ser conferido.
6. **Given** um Edital publicado antes desta feature, **When** qualquer documento seu é consultado,
   **Then** o conteúdo e o resumo criptográfico são idênticos aos de antes.

---

### User Story 3 - A reserva sem via de apuração deixa de ser silenciosa (Priority: P3)

Uma servidora declara modalidades com vagas reservadas num Perfil cujo marco produz uma ordem
única. Antes de publicar, o sistema diz que aquele quadro não terá apuração por recorte — nomeando
a causa, e não o sintoma — e diz qual é a saída. Ela decide publicar mesmo assim, sabendo o que a
espera, e não descobre no dia de convocar diante de três botões idênticos dos quais dois sempre
falham. Esses dois botões deixam de ser oferecidos.

**Why this priority**: é o achado de maior dano da auditoria, e também o único cuja correção de
fundo — emitir ordem por lista em marco computado — é feature de porte próprio e decisão de
governança.

**O tratamento é aviso, e não impedimento — a decisão foi tomada em 18/09/2026 e o porquê fica
registrado.** Impedir era a leitura mais forte, e é o que esta spec faz nos outros três achados.
Aqui ela custaria caro e protegeria pouco: três Editais da amostra real (57/2026, 28/2026,
173/2025) declaram reserva em marco computado, e para eles a publicação é a única parte da jornada
que hoje funciona — a apuração por recorte já acontece fora do sistema. Impedir retiraria o que
funciona sem consertar o que não funciona. **O achado S4 continua alcançável**, e é honesto dizê-lo:
o que esta feature remove é o silêncio, não o limite. O limite sai com a feature de emissão por
lista.

**Independent Test**: reencenar o quadro 7/1/2 da auditoria num marco que ordena por pontuação e
conferir que o sistema se manifesta antes da publicação, com mensagem que nomeia a causa.

**Acceptance Scenarios**:

1. **Given** um Perfil que declara Modalidade com vagas reservadas e cujo marco produz ordem única,
   **When** a validação de publicação é executada, **Then** o sistema emite **aviso** que nomeia a
   causa — a ordem daquele marco é emitida em lista única, e só a ordem sorteada é emitida por
   recorte — e a saída, **sem impedir a publicação**.
2. **Given** um Perfil nas mesmas condições cujo Edital já está publicado, **When** a tela de
   ocupação é aberta, **Then** ela **não oferece** "Apurar a ocupação deste recorte" para os
   recortes que aquele marco não emite, e declara por quê.
3. **Given** um Perfil com reserva cujo marco ordena por sorteio, **When** a validação é executada,
   **Then** nada é apontado: o sorteio emite por lista, e o quadro tem via de apuração.

---

### Edge Cases

- **Regra de corte que não governa Etapa alguma.** É declaração legítima (`FR-224` da `014`), e é o
  caso do Edital 69/2026 da amostra — sorteia, publica, convoca, sem análise documental entre a
  ordem e a chamada. O aviso de `FR-461` distingue **ausência de regra** de **regra que declara não
  governar Etapa**, e só a primeira o dispara.
- **Edital do acervo sem marco, sem método publicado ou com reserva sem apuração.** Ele existe: é
  o que a auditoria publicou. Uma Retificação sobre ele continua sendo aceita, porque o valor
  publicado é intocável e a família nova não pode tornar impossível corrigir justamente o Edital que
  ela existe para evitar.
- **Perfil sem marco num Edital que ainda não tem Etapa alguma.** A recusa de `FR-457` continua
  valendo e aponta a etapa de Classificação; a de Etapa ausente, quando houver, é a que a `030` já
  emite.
- **Marco de sorteio sem Etapa.** Aceito desde a `030` (`FR-432`). A ausência de Etapa não é
  motivo de achado de executabilidade aqui.
- **Mais de um achado no mesmo Edital.** Os quatro Editais da auditoria disparam achados
  diferentes; a Revisão os apresenta todos, e não o primeiro.

## Requirements *(mandatory)*

### Functional Requirements

#### A família de executabilidade, e o seu alcance

- **FR-457**: O sistema MUST recusar, como erro impeditivo da publicação, Edital em que algum Perfil
  de Vaga não declare marco classificatório algum.
- **FR-458**: Toda recusa e todo aviso desta família MUST nomear **a entidade** de que fala, **o que
  falta** e **em que etapa do assistente** a correção é feita — nunca apenas o sintoma.
- **FR-459**: As verificações desta família MUST ser impeditivas somente no **ato de publicação**. A
  gravação do rascunho MUST continuar aceitando o Edital pela metade, como já aceita para regra de
  corte, método do sorteio e janela recursal.
- **FR-460**: A Retificação de Edital do acervo MUST continuar aceitando as ausências que aquele
  Edital já publicou. A família nova MUST NOT tornar irretificável um Edital publicado antes dela.
- **FR-461**: O sistema MUST emitir **aviso**, não impeditivo, para marco que não declara regra de
  corte alguma, e o aviso MUST nomear a consequência real: sem corte não há geração, sem geração não
  há faixa, e sem faixa não há convocação.
- **FR-462**: A mesma consequência MUST ser declarada na **composição**, no cartão do marco, no
  momento em que a decisão sobre o corte é tomada — e não apenas na Revisão.
- **FR-463**: A tela de ocupação MUST NOT oferecer "Pedir a faixa seguinte" para marco que não
  declara regra de corte, e MUST declarar a razão no lugar da ação.

#### O método do sorteio no documento publicado

- **FR-464**: O documento publicado do Edital MUST declarar, na seção de cada marco, **como a ordem
  daquele marco é produzida** — por pontuação combinada das Etapas ou por sorteio.
- **FR-465**: Para marco que ordena por sorteio, o documento MUST imprimir o método que o governa:
  algoritmo e versão, fonte pública externa da semente, a ocorrência que fixa a semente, o instante
  publicado dessa ocorrência, como a ocorrência decorre da data programada, como o material bruto
  vira semente e o que vale se a ocorrência faltar, atrasar, bifurcar ou vier inválida.
- **FR-466**: Quando o marco **referencia o método comum do Edital**, o documento MUST imprimir o
  método que efetivamente o governa e MUST dizer que ele é o comum; quando o marco declara método
  próprio divergente do comum, o documento MUST nomear a divergência.
- **FR-467**: O sistema MUST recusar, como erro impeditivo da publicação, marco que ordena por
  sorteio cujo método não será publicado — nem próprio, nem comum.
- **FR-468**: Para marco que ordena por sorteio, o documento MUST NOT imprimir linha de combinação
  de pontuações.
- **FR-469**: Nenhum documento de Edital publicado antes desta feature MUST mudar de conteúdo nem de
  resumo criptográfico.

#### A reserva de vagas sem via de apuração

- **FR-470**: O sistema MUST emitir **aviso**, não impeditivo, antes da publicação, sobre Perfil que
  declara Modalidade com vagas reservadas cujo marco produz ordem única. A publicação MUST continuar
  possível: três Editais da amostra real — 57/2026, 28/2026 e 173/2025 — têm essa forma, e impedi-la
  retiraria a única parte da jornada que hoje funciona para eles. O que o aviso remove não é a
  publicação: é a surpresa no dia de convocar.
- **FR-471**: A mensagem de `FR-470` MUST nomear **a causa** — a ordem daquele marco é emitida em
  lista única, e só a ordem sorteada é emitida por recorte — e a saída, em vez do sintoma que a
  auditoria leu no dia da apuração (*"Este recorte não tem ordem emitida"*).
- **FR-472**: A tela de ocupação MUST NOT oferecer "Apurar a ocupação deste recorte" para recorte
  que o marco daquele Perfil não emite, e MUST declarar a razão no lugar da ação.

### Key Entities

- **Achado de validação**: o que a validação de conteúdo devolve. Tem severidade (informação, aviso,
  erro impeditivo), um código estável, a mensagem que a pessoa lê e o endereço da entidade de que
  fala. A família desta feature acrescenta achados; não muda a classificação nem o vocabulário.
- **Marco classificatório**: onde a ordem entre participantes é produzida, por Perfil. Carrega a
  forma da ordem (`030`), o método do sorteio quando sorteia, e a regra de corte quando corta.
- **Regra de corte**: declara qual Etapa o corte governa, **ou declara explicitamente que não
  governa Etapa alguma**. A ausência da regra e a regra que não governa Etapa são estados
  diferentes, e esta feature depende dessa diferença.
- **Método do sorteio**: os sete campos que tornam a semente reproduzível por terceiro. Pode ser
  declarado no marco ou ser o comum do Edital (`030`).
- **Recorte de concorrência**: a lista em que a ordem é emitida. Hoje um ato computado tem um
  recorte só — o da ampla concorrência.
- **Documento publicado do Edital**: o que a candidata lê. É gerado no ato da publicação a partir do
  conteúdo canônico da versão, e não se regenera depois.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-157**: Nenhum dos quatro Editais que a auditoria montou chega à submissão sem que a Revisão
  nomeie o problema — 4 de 4, reencenados pelo mesmo caminho da interface.
- **SC-158**: O documento publicado de um Edital de sorteio contém os sete dados do método, e quem o
  recebe consegue reproduzir a semente sem pedir nada à instituição.
- **SC-159**: 100% dos achados novos citam a etapa do assistente em que a correção é feita.
- **SC-160**: Gravar um rascunho incompleto continua possível em 100% dos casos em que hoje é
  possível — nenhuma das verificações novas alcança a gravação.
- **SC-161**: Nenhum Edital do acervo muda de conteúdo publicado nem de resumo criptográfico, e
  todos continuam retificáveis.
- **SC-162**: Quem deixa o corte em branco lê a consequência sobre a convocação **na etapa em que a
  decisão é tomada**, e não semanas depois — verificável na composição, sem abrir a Revisão.
- **SC-163**: Nenhuma tela oferece ação que sempre falha: as duas ações impossíveis que a auditoria
  encontrou — a faixa seguinte sem corte e a apuração de recorte não emitido — deixam de ser
  oferecidas e passam a declarar a razão.

## Assumptions

- A classificação de achados em **informação**, **aviso** e **erro impeditivo** já existe e é a que
  o Princípio IV exige. Esta feature acrescenta achados a ela; não cria um segundo mecanismo.
- "Edital do acervo" significa Edital publicado antes desta feature entrar. A distinção é a mesma
  que a `030` usou ao separar o ato de publicação do ato de retificação.
- O documento publicado é gerado no ato da publicação e guardado; ele não se regenera quando o
  renderizador muda. `FR-469` é, por isso, consequência do desenho existente, e o que se verifica é
  que nada o contraria.
- O método do sorteio já é validado inteiro quando declarado — os sete campos, a fonte que o sistema
  consulta, as duas regras com identificador e frase. Esta feature não muda essa validação; ela a
  leva ao documento e recusa o marco que sorteia sem método.
- A forma da ordem (`orderProduction`) é declarada por todo marco publicado a partir da `030`, e o
  marco do acervo pode não a declarar. Onde a forma não é declarada, o comportamento de hoje
  permanece.
- As mensagens novas seguem a rubrica de microcópia deste repositório: a explicação longa vai para o
  bloco `como-preencher` da etapa, e não para dentro do cartão.
- Um Edital com reserva em marco computado continua tendo a apuração por recorte feita fora do
  sistema. Esta feature assume esse fato e o nomeia; ela não o corrige.

## Out of Scope

Cada item abaixo tem spec própria a abrir, e nenhum deles é escopo desta.

- **Emitir ordem por lista em marco computado** — a correção de fundo do `ACH-47`. É feature de
  porte próprio e decisão de governança: três Editais da amostra (57/2026, 28/2026, 173/2025)
  dependem dela.
- **Navegação derivada da capacidade** — `ACH-40`, melhoria 13.3.
- **Renderizador normativo único das telas de ato** — `ACH-39`, `ACH-31`, `ACH-45`, melhoria 13.4.
- **Ato de instrução do recurso e o parecer que chega ao candidato** — `ACH-43`, `ACH-42`,
  melhoria 13.2.
- **Validação cruzada entre fontes normativas** — janela recursal × Evento de recurso, término das
  inscrições × designação, numeração de seção — `ACH-41`, `ACH-13`, `ACH-18`, melhoria 13.5.
- **Painel de condução do Processo vivo** — `ACH-25`, melhoria 13.6.
- **A fonte da semente em texto livre e a derivação da ocorrência não computável** — `ACH-51` e
  `ACH-55`. São da mesma família de "descobrir tarde", mas a causa é outra: o valor é criado num
  campo que não oferece a lista fechada que o sistema conhece.
- **`Peso (opcional)` que vira impeditivo** — `ACH-16`. Pertence à composição, e a `030` o deixou
  aberto.

## Conformidade com a Constituição

**Princípio IV — Regras Explícitas e Consistência Operacional.** É o princípio que esta feature
cumpre literalmente: *"A operação DEVE validar inconsistências, classificá-las como informação,
aviso ou erro impeditivo e bloquear a publicação diante de erro impeditivo."* O que a auditoria
encontrou foi essa exigência cumprida pela metade — a classificação existe, e o que ela verifica não
alcança o que faz o certame funcionar. Nenhuma regra de domínio nova é criada aqui; o que muda é
onde as regras já escritas passam a ser conferidas.

**Princípio II — Integridade Normativa, Imutabilidade e Temporalidade.** `FR-460`, `FR-469` e
`SC-161` existem para que a feature não toque no que já foi publicado. O Edital do acervo continua
retificável, e o documento dele continua idêntico.

**Princípio VI — Completude de Jornada e Valor Demonstrável.** A tensão é real e vale declará-la: o
Princípio VI diz que validação é requisito de qualidade e **não pode substituir** capacidade
observável. Por isso as três histórias são escritas como jornada, e não como regra:

- a **P1** entrega a quem elabora a informação de que o Edital não vai funcionar **enquanto ainda é
  rascunho** — hoje essa informação só existe depois da publicação, e só como falha;
- a **P2** entrega a quem está **fora da instituição** a base normativa para conferir o sorteio, que
  é capacidade nova e observável no documento público;
- a **P3** remove duas ações que o sistema oferece e nunca consegue executar.

O cenário demonstrável de ponta a ponta é o da auditoria, reencenado: montar os quatro Editais pela
interface administrativa e verificar que nenhum deles chega ao público quebrado.
