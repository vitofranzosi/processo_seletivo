# Feature Specification: Sorteio viável desde a publicação — o Edital não publica uma extração que o sorteio sempre recusará

**Feature Branch**: `claude/elegant-boyd-8955eb`, sobre a `main` em `0ff70f07`

**Created**: 2026-10-29

**Status**: Draft. Escrita a pedido da sessão que investigou o sorteio recusado do Edital 72/2026. As
três perguntas de produto marcadas abaixo vão para o usuário, no `/speckit-clarify`. Não há
autorização para implementar antes de o plan e as tasks serem aprovados.

**Input**: lacuna 1 do achado de 29/10/2026,
[`doc/achado-sorteio-com-extracao-no-dia-do-congelamento.md`](../../doc/achado-sorteio-com-extracao-no-dia-do-congelamento.md),
que está no PR #335 e ainda não chegou à `main`. O achado registra que o Edital foi publicado com o
fim das inscrições (28/10, às 9h) e a extração declarada (28/10, às 20h05) no mesmo dia. Isso tornou
o sorteio impossível desde a publicação, e nada avisou. A lacuna 2 do mesmo achado, os instantes em
UTC na mensagem de recusa, é tratada à parte e **não** entra aqui.

> **Faixa de identificadores.** Esta spec abre em **FR-2647** e **SC-954**. O teto foi medido em
> 29/10/2026 em `specs/` de **todas as worktrees desta máquina**: o requisito funcional seiscentos e
> quarenta e seis da faixa dos dois mil, e o critério novecentos e cinquenta e três, os dois da `101`,
> que ainda não foi mergeada. A `main` para em `FR-2608` e `SC-947`. **Nenhum `UX-` é aberto aqui.**
> As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-077 da `021`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> porque `D-` aqui é só desta spec.

---

## Por que esta feature existe

**A recusa do dia 29/10 está certa.** A Caixa publica a data da extração (`dataApuracao`) sem
horário. Desde a correção registrada em `_nao_antes_de`, essa data vale como o início do dia, e o
sorteio exige que a relação tenha sido congelada **antes** desse instante. A relação foi congelada em
28/10, às 11h20, e 00h00 de 28/10 não é posterior a isso. A garantia de que a semente vem depois do
compromisso do universo funcionou.

**O defeito estava num ato anterior, e era visível nele.** No momento da publicação, o sistema já
sabia três coisas:

1. a relação só se congela **depois** do fim do período de inscrições, porque o congelamento recusa
   antes disso;
2. a fonte declarada publica só a data, e a data vale como o início do dia;
3. o instante declarado da extração era 28/10/2026, às 20h05.

Com as inscrições terminando em 28/10, às 9h, o congelamento mais cedo possível era 28/10, às 9h, e
ele nunca é anterior a 00h00 do mesmo dia. **O sorteio estava condenado desde a publicação.** A
conferência de `occurrenceAt` na elaboração verifica só o formato e o fuso, e nenhuma regra compara o
dia da extração com o fim das inscrições.

**O custo cai no pior momento.** A recusa aparece no dia do sorteio, com o certame em curso e o
cronograma já publicado. A saída custa dois atos públicos, e nenhum deles é barato (ver adiante). O
operador que congelou no mesmo dia não tinha como saber, e congelar não se desfaz.

**E o caso nunca aparece em desenvolvimento.** Lá, e na suíte, a fonte é a de demonstração. Ela
informa que a extração aconteceu "agora", de modo que todo congelamento fica antes dela, até no
mesmo dia. Só a fonte real, num ambiente que não liga a fonte de demonstração, reproduz o caso.

### O que foi verificado no código em 29/10/2026

**Uma relação congelada não aceita a extração de um método retificado.** O achado deixou essa
pergunta em aberto, e a resposta é **não**. Ao constituir o sorteio, o sistema lê o método da versão
do Edital que **a relação cita**, e não o da versão vigente. Depois confere esse método contra o
resumo que a relação gravou ao congelar. A ocorrência só é aceita se for a que **aquele** método
declara, ou a que a regra de substituição dele põe no lugar. Uma Retificação que troque o concurso
6113 pelo 6114 não muda o que a relação congelada exige: a ocorrência 6114 seria recusada como "não
declarada".

Portanto, **a saída do Edital 72 tem três passos, nesta ordem**:

1. retificar o método, declarando uma extração de dia posterior àquele em que a relação nova será
   congelada;
2. publicar uma relação nova, sucedendo a atual com motivo escrito. Ela cita a versão retificada e o
   método novo;
3. observar a ocorrência nova e sortear.

**Suceder a relação sem retificar não resolve.** A relação nova seria congelada ainda mais tarde,
diante da mesma extração de 28/10. **Retificar sem suceder também não resolve**, pelo motivo acima.
Nenhum dos dois atos, sozinho, chega ao sorteio. A recusa de hoje não diz nenhum dos dois.

**A fonte é escolhida pelo nome publicado, e a granularidade não está escrita em lugar nenhum.** O
vocabulário de fontes liga cada nome ao adaptador que o executa. Que a Loteria Federal publica só a
data é algo que só o adaptador sabe, num comentário. Nenhuma regra fora dele consegue perguntar isso.

**As fixtures da suíte e a `seed_demo` declaram a extração em 1º/01/2020, com a fonte de
demonstração.** São quatro fixtures centrais, das quais 46 arquivos de teste dependem. O passado é
proposital: a `seed_demo` diz *"para que o roteiro possa observar a ocorrência logo depois de
semear"*. A data só funciona porque a fonte de demonstração ignora o instante declarado e responde
"agora". Medido em 29/10/2026 na `main`, em `0ff70f07`.

### O que esta spec cobre, e o que fica fora

**Cobre** os quatro pontos da lacuna 1:

- a conferência na publicação, e na Retificação;
- o aviso antes de congelar a relação;
- o que a recusa diz e o que a tela diz antes dela;
- o jeito de reproduzir o caso em desenvolvimento.

**Fica fora:**

- **Os instantes em UTC na mensagem de recusa.** É a lacuna 2 do mesmo achado. Esta spec não a
  corrige, mas os textos novos que ela escreve já saem no fuso institucional (FR-2668).
- **Os campos trocados do método do Edital 72** (normalização com a Lotofácil, derivação com a
  Loteria Federal). O sistema aceita texto livre ali, e o caso é do ensaio, não da regra.
- **A Etapa de habilitação antes do sorteio.** Quando o método declara essa Etapa, a relação só se
  congela depois do resultado dela, que pode ser bem posterior ao fim das inscrições. Esta spec
  confere contra o limite que o sistema já conhece com certeza, que é o fim das inscrições (D-002).
- **A publicação da relação declarada no cronograma.** É Evento livre, e só existe quando quem
  elabora o declara (D-002).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem elabora fica sabendo, ao publicar, que o sorteio é impossível (Priority: P1)

Quem elabora o Edital declara o método do sorteio, com a extração da Loteria Federal, e o cronograma,
com o fim das inscrições. Hoje, um Edital com a extração no mesmo dia do fim das inscrições é
publicado sem nenhum achado. Com esta feature, a conferência de publicação acusa o caso, nomeia o
marco, a fonte, o dia da extração e o fim das inscrições, e diz o que mudar.

**Why this priority**: é o único momento em que a correção é barata. Antes da publicação, trocar a
extração é editar o rascunho. Depois dela, é Retificação e sucessão de relação.

**Independent Test**: componha o Edital 72/2026 como foi publicado (inscrições até 28/10, às 9h;
Loteria Federal, concurso 6113, extração em 28/10, às 20h05) e confira a publicação: aparece o
achado. Mude a extração para 29/10: o achado some.

**Acceptance Scenarios**:

1. **Given** um marco por sorteio com a Loteria Federal e a extração em 28/10, às 20h05, e o fim das
   inscrições em 28/10, às 9h, **When** quem elabora confere a publicação, **Then** aparece um achado
   que nomeia o marco, a fonte, o dia 28/10 e o fim das inscrições, e diz que a extração precisa ser
   de dia posterior ao fim das inscrições.
2. **Given** o mesmo Edital com a extração em 29/10, **When** a publicação é conferida, **Then** não
   há achado.
3. **Given** a extração em 27/10, antes do fim das inscrições, **When** a publicação é conferida,
   **Then** o achado aparece, porque o caso é o mesmo, só que mais evidente.
4. **Given** o método comum do Edital, sem método próprio nos marcos, **When** a publicação é
   conferida, **Then** o achado aparece uma vez para o método comum, e não uma vez por marco.
5. **Given** um Edital sem período de inscrições designado, ou com período sem término, **When** a
   publicação é conferida, **Then** este achado não aparece, porque não há instante contra o qual
   comparar.

---

### User Story 2 — Quem conduz o certame é avisado antes de congelar a relação (Priority: P1)

Na tela do sorteio, antes de "Publicar e congelar a relação", quem conduz vê um aviso quando congelar
**agora** tornaria impossível sortear com a extração declarada. É o caso do Edital 72 já publicado:
em 28/10, às 11h20, o aviso teria dito que congelar naquele dia condenava o sorteio, e que a saída
era retificar o método antes de congelar.

**Why this priority**: o congelamento é ato append-only. Para Editais já publicados, e para os que
passarem pela conferência por advertência (se essa for a escolha), este aviso é a última chance.

**Independent Test**: com o Edital 72 publicado e as inscrições encerradas, abra a tela do sorteio
no dia 28/10: o aviso aparece antes do botão. Abra a mesma tela num Edital com extração em 30/10: o
aviso não aparece.

**Acceptance Scenarios**:

1. **Given** um recorte ainda não congelado, a Loteria Federal declarada e hoje no dia da extração
   declarada, ou depois dele, **When** quem conduz abre a tela do sorteio, **Then** antes do botão de
   congelar aparece um aviso. Ele diz que a fonte publica só a data e que congelar hoje torna
   impossível sortear com aquela extração. Diz também que a saída é retificar o método para uma
   extração de dia posterior ao do congelamento, e só então congelar.
2. **Given** a extração declarada num dia posterior a hoje, **When** a tela é aberta, **Then** não há
   aviso.
3. **Given** uma relação já congelada que não pode mais sortear com a extração que o método dela
   declara, **When** a tela é aberta, **Then** antes de "Realizar o sorteio" aparece o mesmo
   diagnóstico, com a saída em três passos: retificar, suceder a relação, observar a nova ocorrência.

---

### User Story 3 — A recusa diz o que fazer (Priority: P2)

Quando a recusa `occurrence_precedes_freeze` acontece, quem a lê fica sabendo, na própria mensagem,
que suceder a relação sozinha não resolve, e que a saída é retificar o método e depois suceder a
relação. Fica sabendo também que a fonte não publica o horário, para não ir investigar o horário.

**Why this priority**: as US1 e US2 tornam o caso raro, mas não o eliminam. Editais já publicados e
relações já congeladas continuam chegando a esta recusa.

**Independent Test**: reproduza a recusa com uma relação congelada no dia da extração e confira que a
mensagem traz os três passos e a frase sobre a granularidade da fonte.

**Acceptance Scenarios**:

1. **Given** uma relação congelada no dia da extração declarada, com fonte que publica só a data,
   **When** quem conduz realiza o sorteio, **Then** a recusa diz que a fonte publica só a data, que a
   data vale a partir de 00h00, que suceder a relação sem retificar não resolve, e a ordem dos três
   passos.
2. **Given** uma fonte que publica a data e a hora, **When** a mesma recusa acontece, **Then** a
   mensagem não fala de "só a data". A saída é a mesma.

---

### User Story 4 — O caso pode ser reproduzido em desenvolvimento (Priority: P3)

Quem desenvolve ou demonstra o sistema consegue ver, sem a rede e sem a Caixa, o sorteio recusado por
extração no dia do congelamento, e as mensagens das US1 a US3.

**Why this priority**: sem isso, o roteiro local nunca mostra o caso, e as três histórias acima só
podem ser conferidas por teste automatizado ou no servidor.

**Independent Test**: no ambiente de desenvolvimento, declare a fonte de demonstração que imita a
Loteria Federal, congele a relação e realize o sorteio no mesmo dia: a recusa aparece.

**Acceptance Scenarios**:

1. **Given** o ambiente de desenvolvimento com a fonte de demonstração ligada, **When** quem
   desenvolve declara a variante que imita a fonte real, congela e sorteia no mesmo dia, **Then** o
   sorteio é recusado como no servidor de 29/10.
2. **Given** a fonte de demonstração atual, **When** a `seed_demo` e a suíte rodam, **Then** nada
   muda para elas.

---

### Edge Cases

- **Extração exatamente às 00h00 do dia seguinte ao fim das inscrições.** O limite previsto é esse
  instante, e ele é posterior ao fim: não há achado (FR-2651).
- **O fim das inscrições às 23h59 e a extração no dia seguinte.** Ainda é viável, desde que o
  congelamento aconteça antes da meia-noite. A conferência de publicação não acusa (FR-2651). O aviso
  da tela do sorteio cobre quem deixar para congelar no dia seguinte (FR-2659).
- **O dia é o do fuso institucional.** `occurrenceAt` declarado com outro deslocamento é convertido
  para o fuso institucional antes de se tomar o dia, que é como a fonte real interpreta a data dela
  (FR-2650).
- **Fonte que publica a hora.** O limite previsto é o próprio instante declarado. O achado aparece
  quando ele não é posterior ao fim das inscrições (FR-2650, FR-2651).
- **Período de inscrições ausente, sem término ou cancelado.** Não há fim contra o qual comparar, e o
  achado não aparece. O período cancelado tem sua própria conferência (FR-2655).
- **Método inválido ou com fonte que o sistema não executa.** Já existe achado próprio para isso, e
  este não se soma a ele (FR-2655).
- **Retificação que prorroga as inscrições até o dia da extração.** O caso é o mesmo, e chega pela
  Retificação (FR-2656).
- **Edital do acervo já sorteado.** Um marco cujo sorteio já foi constituído não recebe o achado na
  Retificação. O método dele não governa mais nenhum ato a fazer (FR-2656).
- **A ocorrência substituta.** A regra de substituição aponta a extração seguinte, cujo instante o
  Edital não declara. O aviso antes do congelamento só fala da ocorrência declarada, que é a única
  com instante publicado (FR-2659).
- **Vários marcos por sorteio no mesmo Edital.** Cada um é conferido contra o seu método, com o mesmo
  fim de inscrições (FR-2652).
- **Relação já congelada e método já retificado.** A relação congelada continua exigindo a extração
  do método dela, e a tela diz isso: falta suceder a relação (FR-2660, FR-2661).

## Requirements *(mandatory)*

### Functional Requirements

#### A granularidade da fonte

- **FR-2647**: Cada fonte do vocabulário de fontes MUST declarar se publica **só a data** da
  ocorrência ou **a data e a hora**. A declaração mora junto do nome da fonte e do adaptador, e MUST
  NOT ser deduzida do conteúdo do Edital nem da resposta da fonte.
- **FR-2648**: A Loteria Federal MUST ser declarada como fonte que publica só a data. A fonte de
  demonstração atual MUST ser declarada como fonte que publica a data e a hora, que é o que ela já
  faz hoje.
- **FR-2649**: O adaptador de uma fonte declarada como "só a data" MUST continuar a devolver o início
  do dia publicado como limite inferior da ocorrência. Uma fonte declarada como "data e hora" MUST
  devolver o horário publicado. A declaração da FR-2647 e o comportamento do adaptador MUST ser
  conferidos um contra o outro por teste.

#### O limite previsto da ocorrência

- **FR-2650**: O **limite previsto** da ocorrência declarada é o instante mais cedo em que a fonte vai
  situá-la, calculado a partir de `occurrenceAt` e da granularidade da fonte. Para "só a data", é
  00h00, no fuso institucional, do dia de `occurrenceAt` tomado nesse fuso. Para "data e hora", é o
  próprio `occurrenceAt`. Uma regra só MUST calcular esse limite, e a conferência de publicação, a
  tela do sorteio e a recusa MUST usá-la.
- **FR-2651**: Uma extração declarada é **inviável** quando o limite previsto não é posterior ao
  instante mais cedo em que a relação pode ser congelada. Na publicação e na Retificação, esse
  instante é o fim do período de inscrições da versão conferida. Na tela do sorteio, é o momento em
  que se congela.

#### Na publicação e na Retificação

- **FR-2652**: A conferência de publicação MUST produzir um achado para cada método inviável. Conta
  como método o comum do Edital, uma vez, e o próprio de cada marco que o declara, uma vez cada. Para
  saber que método governa cada marco, MUST usar a mesma resolução que o congelamento usa. O achado
  é [NEEDS CLARIFICATION: impeditivo ou advertência na publicação? A recusa é a resposta para um caso
  que é certo, e não provável. Contra ela pesa que a mesma data passaria a valer com uma fonte que
  publique a hora. A pergunta Q1 cobre também o congelamento (FR-2659)].
- **FR-2653**: O achado MUST nomear o marco (ou dizer "método comum a este Edital"), a fonte, o dia
  da extração declarada e o fim das inscrições, com instantes por extenso no fuso institucional. MUST
  dizer o que mudar: uma extração de dia posterior ao fim das inscrições, ou um fim de inscrições
  anterior ao dia da extração. Para fonte que publica só a data, MUST dizer que ela não publica o
  horário e que a data vale a partir de 00h00.
- **FR-2654**: O achado MUST aparecer onde a revisão da composição já mostra os achados de
  publicação, apontando para a etapa em que o método é declarado. Esta feature MUST NOT criar tela
  nova.
- **FR-2655**: O achado MUST NOT aparecer quando não há período de inscrições designado, quando o
  período não declara término, quando o período está cancelado ou quando o método já tem achado de
  forma, de fonte ou de instante.
- **FR-2656**: Na Retificação, o achado MUST ser advertência e nunca impeditivo. A Retificação é a
  saída do Edital que já está condenado. MUST NOT aparecer para um marco que já tenha sorteio
  constituído em todos os recortes.
- **FR-2657**: Conforme o alcance decidido, [NEEDS CLARIFICATION: a conferência vale para toda fonte,
  pela granularidade declarada, ou só para fonte que publica só a data? Valer para toda fonte também
  acusa as fixtures e a `seed_demo`, que declaram a extração em 2020 com a fonte de demonstração.
  Valer só para "só a data" não toca nelas, mas deixa sem conferência a fonte com hora declarada
  antes do fim das inscrições].

#### Antes de congelar

- **FR-2658**: Ao montar a tela do sorteio, a viabilidade de um recorte ainda não congelado MUST ser
  calculada a partir do método que a relação comprometeria se fosse congelada agora, que é o da
  versão vigente.
- **FR-2659**: Quando a extração declarada for inviável para um congelamento feito agora (FR-2651), a
  tela MUST mostrar, antes do botão "Publicar e congelar a relação", um aviso com o diagnóstico e a
  saída: retificar o método para uma extração de dia posterior ao do congelamento, e só então
  congelar. Na pergunta Q1, a resposta para o congelamento é aviso com o botão disponível, ou recusa.
  O aviso MUST NOT aparecer para a ocorrência substituta, que não tem instante declarado.
- **FR-2660**: Para uma relação já congelada cuja extração declarada é inviável (limite previsto não
  posterior ao congelamento), a tela MUST mostrar, antes de "Realizar o sorteio", que esta relação
  não sorteia com aquela extração. MUST mostrar também a saída em três passos: retificar o método,
  publicar relação nova sucedendo a atual, observar a ocorrência nova.
- **FR-2661**: Quando o método já foi retificado e a relação congelada ainda cita a versão anterior,
  a tela MUST dizer que falta o passo de suceder a relação. A relação congelada não lê o método
  vigente.

#### A recusa

- **FR-2662**: A recusa `occurrence_precedes_freeze` MUST dizer, além do que diz hoje, que suceder a
  relação sem retificar não resolve, e a ordem dos três passos da saída.
- **FR-2663**: Quando a fonte publica só a data, a recusa MUST dizer que a fonte não publica o horário
  e que a data vale a partir de 00h00. Quem lê não deve concluir que a fonte informou um horário.
- **FR-2664**: A comparação que decide a recusa MUST NOT mudar. Ela continua usando o limite inferior
  que a fonte devolveu, contra o instante do congelamento. Esta feature avisa antes, e não afrouxa a
  garantia de que a semente é posterior ao compromisso.

#### Em desenvolvimento

- **FR-2665**: Conforme a forma decidida, o ambiente de desenvolvimento MUST oferecer um jeito de
  reproduzir a recusa sem rede [NEEDS CLARIFICATION: uma segunda fonte de demonstração, declarada como
  "só a data", que devolve o início do dia corrente (a fonte atual e a suíte ficam como estão); a
  fonte de demonstração atual passando a imitar a real, o que exige levar o instante declarado ao
  adaptador e mexer nas datas da `seed_demo` e das fixtures; ou nada além dos testes automatizados?].
- **FR-2666**: Qualquer variante de demonstração MUST continuar fora do vocabulário em produção, como
  a de hoje.

#### O que não muda

- **FR-2667**: Esta feature MUST NOT alterar conteúdo publicado nem reconferir Editais já publicados.
  A regra vale nos atos de publicação e de Retificação feitos daqui em diante, e na leitura da tela
  do sorteio.
- **FR-2668**: Todo instante nos textos novos desta feature (achado, aviso, acréscimo à recusa) MUST
  sair no fuso institucional e por extenso. A frase da recusa que já existe é da lacuna 2, e fica
  como está.

### Key Entities

- **Granularidade da fonte**: "só a data" ou "data e hora", declarada por fonte do vocabulário, junto
  do adaptador. Não é conteúdo do Edital.
- **Limite previsto da ocorrência**: derivado de `occurrenceAt` e da granularidade (FR-2650). Não se
  grava: é calculado sempre que alguém pergunta.
- **Congelamento mais cedo possível**: o fim do período de inscrições da versão conferida, na
  publicação e na Retificação, ou o momento do congelamento, na tela do sorteio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-954**: Na matriz de casos, com granularidade (só a data, data e hora) cruzada com a posição da
  extração em relação ao fim das inscrições (dia anterior, mesmo dia antes do fim, mesmo dia depois
  do fim, dia seguinte à meia-noite, dia seguinte), a conferência de publicação acusa **exatamente**
  os casos em que um congelamento feito no fim das inscrições seria recusado pelo sorteio. São zero
  falsos positivos e zero falsos negativos.
- **SC-955**: O Edital 72/2026 reproduzido como foi publicado recebe o achado na conferência de
  publicação. Com a extração movida para 29/10, não recebe.
- **SC-956**: Na tela do sorteio, o aviso antes do congelamento aparece em 100% dos casos em que
  congelar naquele momento seria seguido de recusa por precedência, e em nenhum outro.
- **SC-957**: O conjunto de sorteios constituídos pela suíte é o mesmo antes e depois da feature.
  Nenhuma recusa nova de sorteio é introduzida (FR-2664).
- **SC-958**: Num roteiro com quem conduz o certame, ao menos 4 de cada 5 pessoas que leem só a recusa
  ou o aviso da relação congelada dizem, sem ajuda, os dois atos da saída (retificar e suceder) e a
  ordem entre eles.

## Assumptions

- **O dia que a fonte publica é o dia de `occurrenceAt`.** A extração declarada para 28/10 é
  publicada pela Caixa com `dataApuracao` de 28/10. Quando a Caixa adia uma extração, o caso é da
  regra de substituição, e não desta feature.
- **O fim das inscrições é o limite certo.** O congelamento recusa antes dele (a conferência de
  inscrições em curso da relação), de modo que ele é o instante mais cedo possível. Uma Etapa de
  habilitação só empurra o congelamento para depois, e nesse caso a conferência erra pelo lado que
  deixa passar, nunca pelo que recusa sem motivo.
- **Uma fonte só no vocabulário real.** Hoje a única fonte de produção é a Loteria Federal. A
  granularidade por fonte é o que permite a uma fonte futura com horário não herdar a regra da
  Caixa.
- **O custo da opção "toda fonte" (FR-2657) é real.** Quatro fixtures centrais e a `seed_demo`
  declaram a extração em 1º/01/2020 com a fonte de demonstração, e 46 arquivos de teste dependem
  delas. Se a regra valer para toda fonte, essas datas precisam passar para depois do fim das
  inscrições de cada cenário. Se a regra for impeditiva, isso precisa acontecer **antes** de a regra
  entrar, ou a suíte quebra em bloco.
- **O aviso na tela do sorteio não precisa de dado novo.** Ele lê o método vigente, o cronograma e a
  hora atual, que a tela já tem.

## Decisões

### D-001 — A granularidade é declarada por fonte, e não deduzida

Decisão desta spec, que o achado já indicava. Deduzir a granularidade do texto de `occurrenceAt`
(por exemplo, "às 00h00" significar "só a data") misturaria o que o Edital promete com o que a fonte
entrega. Deduzi-la da resposta da fonte só funcionaria depois da extração, que é tarde demais. Por
isso ela é uma propriedade da fonte, no mesmo lugar onde o nome publicado se liga ao adaptador, e o
teste da FR-2649 confere que as duas coisas dizem o mesmo.

### D-002 — Compara-se com o fim das inscrições, e não com a publicação da relação no cronograma

Decisão desta spec, que segue a segunda pergunta do achado. O fim do período de inscrições é limite
rígido: o congelamento o respeita por regra, e ele está em todo Edital que recebe inscrições. A
publicação da relação no cronograma é Evento livre. Ela só existe quando quem elabora a declara, e
nada obriga o congelamento a acontecer nela. Comparar com ela acusaria menos Editais e daria a
impressão de que existe uma regra que o sistema não aplica.

### D-003 — Na Retificação o achado só adverte

Decisão desta spec, com a mesma forma de duas conferências já existentes: a do método do sorteio
publicável e a da forma da ocorrência. As duas valem só na publicação, porque a Retificação é a
única saída do Edital que já tem o defeito. Recusar a Retificação que corrige uma vírgula num Edital
já condenado tiraria dele também a saída. E o marco cujo sorteio já foi constituído não recebe o
achado, porque o método dele não governa mais nenhum ato a fazer.

### D-004 — A saída é retificar e suceder, nessa ordem, e a recusa diz isso

Verificado no código em 29/10/2026 (ver *O que foi verificado no código*). A relação congelada cita a
versão em que congelou e o resumo do método dela, e o sorteio lê o método daquela versão, não do
vigente. Esse é o compromisso que a `021` construiu para impedir que uma Retificação posterior mude
em silêncio a regra sob a qual o certame se comprometeu, e esta spec não mexe nele. A consequência é
que a saída do caso tem dois atos públicos, e a mensagem precisa dizer os dois.

## Pendências do usuário

- **Q1, Q2 e Q3**, marcadas nas FR-2652, FR-2657 e FR-2665, são as perguntas do `/speckit-clarify`.
- **A lacuna 2 do achado** (instantes em UTC na mensagem de recusa), e a varredura das outras
  mensagens de domínio que formatam instantes sem passar pelo fuso, continuam fora daqui.
- **A Etapa de habilitação antes do sorteio** empurra o congelamento para depois do resultado dela.
  Se o usuário quiser conferir também esse caso, a comparação passa a depender do Evento da Etapa, que
  é declarado à parte.
- **Os campos trocados do método no ensaio do Edital 72** são matéria de Retificação no ensaio, e não
  regra do sistema.
