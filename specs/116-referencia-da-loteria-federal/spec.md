# Feature Specification: Referência da Loteria Federal conferida antes do compromisso — o Edital não publica, e a relação não congela, sob um concurso já realizado

**Feature Branch**: `claude/loteria-federal-validation-gps-a628fa`, sobre a `main` em `83cd5863`

**Created**: 2026-11-03

**Status**: Draft. As decisões de produto foram tomadas pelo usuário em 03/11/2026, ao ler o estudo
(ver *Clarifications* e D-001 a D-008). Não há autorização para implementar antes de o plan e as
tasks serem aprovados.

**Input**: [`doc/estudo-extracao-da-loteria-federal-2026-11-03.md`](../../doc/estudo-extracao-da-loteria-federal-2026-11-03.md),
com a POC e as respostas da Caixa gravadas em 03/11/2026
([`doc/estudo-extracao-da-loteria-federal-2026-11-03/`](../../doc/estudo-extracao-da-loteria-federal-2026-11-03/)).
O estudo reproduziu, executando o código da `main`, um concurso de 2015 associado a uma data de
dezembro de 2026. Ele atravessa a composição, a publicação e o congelamento, e só é recusado na
constituição do sorteio.

> **Faixa de identificadores.** Esta spec abre em **FR-3623** e **SC-1094**. O teto foi medido em
> 03/11/2026 em `specs/` de todas as worktrees desta máquina e das 40 branches remotas mais
> recentes: o requisito funcional três mil seiscentos e vinte e dois e o critério mil e noventa e
> três, ambos da `115`, que ainda não foi mergeada. **Nenhum `UX-` é aberto aqui.** As decisões
> reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-016 da `021`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> As oito decisões do usuário de 03/11/2026 são citadas como "1ª" a "8ª".

---

## Por que esta feature existe

**A garantia de integridade está de pé.** Na constituição do sorteio, a extração precisa ser
posterior ao congelamento da relação (a FR-016 da `021`). A data que a fonte publica decide, e o
método vale pelo resumo que a relação gravou ao congelar. Nada nesta spec mexe nisso.

**O que falta é prevenção.** O número do concurso (`occurrence`) e o instante declarado
(`occurrenceAt`) são dois campos independentes:

- a composição confere a **forma** do número: ele precisa terminar em algarismo;
- a publicação, desde a `102`, confere a **data declarada** contra o fim das inscrições;
- **nenhum ato confere o número contra a fonte** antes do dia do sorteio.

Um número já realizado, copiado de um Edital antigo pelo reaproveitamento ou digitado errado, só é
recusado com o certame em curso, quando a saída já custa uma Retificação **e** uma relação nova.

**A Caixa permite saber um fato, e só um.** Medido em 03/11/2026:

- o endpoint principal devolve o último concurso realizado, e todo número menor ou igual a ele já
  foi realizado;
- um número maior **ainda não foi realizado no instante da consulta**;
- a API não diz quando ele será: o próximo, o 9999 e o −1 recebem a mesma resposta HTTP 500;
- o calendário oficial é um PDF protegido contra robôs.

Esta spec usa o fato e não promete o que a fonte não diz.

### O que esta spec cobre, e o que fica fora

**Cobre:**

- a forma numérica da referência da Loteria Federal, conferida no backend;
- a conferência "já realizado?" em quatro atos: submissão, publicação do Edital, publicação de
  Retificação que introduz ou substitui a referência, e congelamento da relação;
- a decisão operacional de cada desfecho da conferência;
- as mensagens;
- o registro na trilha existente;
- uma conferência sob demanda na tela, para ver antes de agir.

**Fica fora** (2ª e 6ª decisões do usuário, e o estudo, seção 8):

- confirmação automática de data futura;
- seleção assistida de concursos;
- qualquer mudança na regra de substituição, na observação ou na comparação da constituição;
- o defeito do adaptador que trata HTTP 500 como falha de acesso. Ele está registrado à parte em
  [`doc/achado-cadeia-de-substituicao-inexecutavel-contra-a-caixa.md`](../../doc/achado-cadeia-de-substituicao-inexecutavel-contra-a-caixa.md).

**Garantia, nos seus limites.** Com a Caixa respondendo, nenhum Edital é publicado e nenhuma relação
é congelada sob concurso que a Caixa já registrava como realizado no instante da consulta. **Com a
Caixa fora do ar, a conferência é inconclusiva**: o ato prossegue com advertência registrada, e o
concurso antigo pode passar. Nesse caso vale a recusa de sempre, na constituição do sorteio. Esta
spec não promete mais do que isso.

## Clarifications

### Session 2026-11-03

As oito decisões do usuário, ao ler o estudo:

- Q: Forma da referência? → A: Para a Loteria Federal, só inteiro positivo em algarismos. `6106-9`,
  `Concurso 6115`, `-1`, `0` e decimais são recusados. Zeros à esquerda se normalizam, e o dígito
  verificador nunca vira outro número em silêncio (1ª; D-001).
- Q: Concurso já realizado? → A: Recusar a introdução, a submissão, a publicação, a Retificação que o
  introduz ou substitui num marco não sorteado, e o congelamento (2ª; D-002).
- Q: Concurso ainda não realizado? → A: Não bloquear. Não declarar a data confirmada. Mostrar o
  último concurso, a distância e a necessidade de conferir no cronograma oficial. Sem estimativa (3ª;
  D-003).
- Q: Caixa indisponível? → A: Advertir, permitir prosseguir e registrar o resultado inconclusivo, sem
  afirmar nada sobre o concurso (4ª; D-004).
- Q: Congelamento? → A: A conferência é parte da operação, e não só da prévia. Recusa se realizado,
  advertência se inconclusivo. A regra da `102` não muda (5ª; D-005).
- Q: Retificação? → A: Só a referência introduzida ou modificada. A correção de outros elementos não
  se bloqueia por problema preexistente, e marcos sorteados ficam fora (6ª; D-006).
- Q: Interface? → A: O preenchimento continua o mesmo. Nenhuma lista de concursos, e nenhuma consulta
  a cada renderização. Conferência sob demanda mais a verificação obrigatória nos atos (7ª; D-007).
- Q: Arquitetura? → A: Sem papel, permissão, infraestrutura, migration ou dependência nova. A trilha
  e a abstração de fontes existentes são reutilizadas, sem ampliar a interface de todas as fontes
  além do necessário (8ª; D-008).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem elabora não publica um Edital sob concurso já realizado (Priority: P1)

Quem compõe declara o concurso 5000 e a data 06/12/2026. Ao submeter, o sistema consulta a Caixa,
que registra o 5000 como realizado em 26/08/2015, e recusa a submissão. A mensagem diz:

- o número;
- a data em que ele foi realizado;
- o último concurso realizado e a data dele;
- o que fazer: declarar um concurso posterior ao último, que ocorra depois do fim das inscrições,
  conferido no calendário oficial.

A publicação confere de novo, porque é outro ato, em outro instante.

**Why this priority**: é o incidente relatado. Sem esta história a feature não existe.

**Independent Test**: com a fonte substituída por respostas gravadas, submeter e publicar um Edital
cujo método declara o 5000 e ver as duas recusas, pela tela e pela API. O mesmo Edital com o 6116
passa.

**Acceptance Scenarios**:

1. **Given** um Edital cujo método comum declara o concurso 5000 da Loteria Federal, e a Caixa
   registra 6114 como último, **When** quem compõe submete, **Then** a submissão é recusada com
   impeditivo, e a mensagem diz "26/08/2015" e "6114, de 01/11/2026".
2. **Given** o mesmo Edital submetido e homologado quando o 5000 ainda não constava como realizado,
   **When** quem publica publica, **Then** a publicação confere de novo e recusa.
3. **Given** dois marcos com método próprio, um com 6116 e outro com 6113, **When** submete, **Then**
   há um impeditivo, e só no marco do 6113. A consulta ao último concurso acontece uma vez.
4. **Given** o mesmo Edital, **When** a submissão chega pela API e não pela tela, **Then** a recusa é
   a mesma.

---

### User Story 2 — Quem conduz o certame não congela a relação sob concurso já realizado (Priority: P1)

O Edital foi publicado quando o concurso ainda não tinha acontecido, mas a extração ocorreu antes do
congelamento: o calendário mudou, ou o número estava errado e caiu numa extração próxima. No
congelamento, a conferência é feita de novo. Ela acha o concurso realizado e recusa. A mensagem diz
que congelar agora condenaria o sorteio, e que a saída é retificar o método antes de congelar.

**Why this priority**: o congelamento é append-only e é o último controle antes de um compromisso
que só se desfaz com relação nova (5ª decisão).

**Independent Test**: publicar com a fonte dizendo "ainda não realizado", trocar a resposta para
"realizado" e tentar congelar.

**Acceptance Scenarios**:

1. **Given** um Edital publicado sob o concurso 6115, e a Caixa agora registra 6115 como realizado,
   **When** quem conduz publica a relação, **Then** o congelamento é recusado, nenhuma relação é
   gravada, e a mensagem diz o número, a data e a saída.
2. **Given** a Caixa registra 6115 como ainda não realizado, **When** congela, **Then** a relação é
   gravada como hoje, e a trilha do ato registra a conferência.
3. **Given** a declarada já registrada como indisponível, de modo que a substituta é a da vez,
   **When** congela, **Then** a conferência se cala, como a `102` faz para a substituta.

---

### User Story 3 — A Caixa fora do ar não paralisa o certame (Priority: P1)

A Caixa não responde no momento de um dos quatro atos. O ato prossegue, desde que as demais regras o
permitam. Quem age recebe uma advertência dizendo:

- que a verificação não foi possível;
- que isso não confirma nem recusa o concurso;
- que o concurso deve ser conferido no resultado oficial.

A trilha registra a tentativa e o resultado inconclusivo.

**Why this priority**: um ato administrativo com prazo não pode ficar preso à disponibilidade de um
serviço que o Ifes não controla (4ª decisão).

**Independent Test**: para cada ato, a fonte responde com tempo esgotado, 500, 503, HTML no lugar de
JSON e JSON sem os bilhetes. O ato conclui com a advertência.

**Acceptance Scenarios**:

1. **Given** a Caixa sem responder, **When** submete, publica, publica a Retificação ou congela,
   **Then** o ato conclui, a advertência aparece, e o registro da trilha diz "inconclusiva" e por quê.
2. **Given** a Caixa sem responder **e** a data declarada no dia do fim das inscrições, **When**
   publica, **Then** o impeditivo da `102` continua impedindo: as regras locais não se suspendem.

---

### User Story 4 — A Retificação confere só o que ela muda (Priority: P2)

Uma Retificação que troca o concurso declarado tem o número novo conferido, e é recusada se ele já
foi realizado. Uma Retificação que só prorroga as inscrições, num Edital cujo concurso antigo já está
consolidado, não consulta a Caixa e não é bloqueada por ele.

**Why this priority**: a Retificação é a saída do Edital com defeito. Bloqueá-la por um problema que
ela não causou tiraria a saída (6ª decisão).

**Independent Test**: duas Retificações sobre o mesmo Edital, uma trocando `occurrence` para um
número realizado e outra trocando só uma data do cronograma.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com 6116, **When** uma Retificação troca para 6113 (realizado),
   **Then** a publicação da Retificação é recusada.
2. **Given** um Edital publicado com 5000, **When** uma Retificação muda só o fim das inscrições,
   **Then** ela é publicada sem consulta e sem impeditivo desta feature.
3. **Given** um Edital com o marco já sorteado, **When** uma Retificação muda a referência desse
   marco, **Then** a referência dele não é conferida.
4. **Given** uma Retificação que troca a fonte de um método de demonstração para a Loteria Federal,
   **When** publica, **Then** a referência é conferida como introduzida.

---

### User Story 5 — A forma errada é recusada na gravação (Priority: P2)

Quem compõe digita `6106-9`, como no comunicado da Caixa, ou `Concurso 6115`. A gravação recusa e
diz o que digitar: "informe só o número do concurso, como 6106 — sem dígito verificador, texto ou
ano". `006114` é gravado como `6114`.

**Why this priority**: a API recusa essas grafias com HTTP 400, e o defeito só apareceria no dia do
sorteio. É regra local, sem rede (1ª decisão).

**Independent Test**: gravar a etapa Classificação com cada grafia e ler o que ficou no rascunho.

**Acceptance Scenarios**:

1. **Given** fonte Loteria Federal, **When** grava `6106-9`, **Then** recusa, e nada é gravado.
2. **Given** fonte Loteria Federal, **When** grava `006114`, **Then** o rascunho guarda `6114`.
3. **Given** fonte de demonstração, **When** grava `Concurso 5900`, **Then** a regra desta spec não
   se aplica.

---

### User Story 6 — Quem compõe ou conduz pode conferir antes de agir (Priority: P3)

Junto do campo do concurso, na composição e na tela do sorteio antes de congelar, há "Conferir na
Caixa". O resultado aparece no lugar, com a mesma mensagem que o ato daria. Nada é gravado, e
nenhuma página consulta a Caixa sozinha.

**Why this priority**: a Constituição pede que o operador veja antes do ato irreversível (Princípio
IV). Os atos já recusam; esta história antecipa a informação (7ª decisão).

**Independent Test**: clicar no botão e contar as chamadas à fonte. Renderizar a página e verificar
que nenhuma chamada houve.

**Acceptance Scenarios**:

1. **Given** a composição com 6113 declarado, **When** clica, **Then** a tela diz "já realizado em
   28/10/2026" e o que fazer.
2. **Given** a mesma tela, **When** só a abre, **Then** nenhuma chamada à fonte acontece.

---

### Edge Cases

- **Concurso muito distante** (9999 com último 6114): ainda não realizado, com "5885 concursos
  adiante". Não há limite arbitrário nem recusa por distância (3ª decisão).
- **O mesmo concurso em dois marcos**, ou no método comum e num marco: uma consulta principal por
  ato, e um achado por método que governa marco não sorteado, como na `102`.
- **Método comum que governa marcos sorteados e não sorteados**: conferido enquanto houver marco por
  sortear, como a `102` faz na Retificação.
- **Concurso realizado entre a consulta e a gravação** (segundos): a conferência vale para o instante
  da consulta, que fica registrado. Se escapar, a precedência na constituição recusa, como hoje.
- **Conteúdo travado com referência que não foi consultada** (o rascunho mudou entre a consulta e a
  trava): a situação é inconclusiva para essa referência, e nunca "ainda não realizado".
- **Consulta principal conclusiva e consulta por número falha**: realizado, sem data. A mensagem diz
  "data não informada pela Caixa", e a recusa vale.
- **A Caixa muda a resposta depois** (Cenário H): nada gravado muda. A ocorrência observada continua
  a mesma linha append-only, o `metodo_hash` da relação não muda, e a conferência só vale no ato em
  que roda.
- **Edital do acervo com grafia fora da forma** (`Concurso 6100`): não é reconferido. No
  congelamento, a referência que a Caixa não aceita gera advertência, e não recusa, pelo mesmo
  princípio da FR-514 da `035` (D-005).
- **Fonte de demonstração**: responde à conferência por tabela, sem rede.
- **Repetição idempotente de um ato**: devolve o desfecho anterior, sem consultar de novo.
- **Ato recusado por outro impeditivo**: a conferência pode ter rodado. A recusa não grava trilha,
  como as demais recusas de publicação, e o registro estruturado de log guarda a conferência (D-004).

---

## Requirements *(mandatory)*

### Functional Requirements

#### A forma da referência

- **FR-3623**: Para a fonte Loteria Federal, a referência MUST ser um inteiro positivo de um a seis
  algarismos, sem outro caractere. `6106-9`, `Concurso 6115`, `6115/2026`, `0`, `-1`, `6114.0` e o
  vazio MUST ser recusados. Zeros à esquerda MUST ser aceitos e gravados sem eles (`006114` → `6114`).
  Nenhuma outra transformação é permitida: o dígito verificador nunca é retirado, nem o texto
  aparado.
- **FR-3624**: A forma MUST ser conferida no backend, na gravação do rascunho e na conferência de
  publicação, e MUST valer igual pela tela e pela API. Na Retificação, MUST ser conferida só para a
  referência que a Retificação introduz ou altera (FR-3633). O conteúdo do acervo que ela não toca
  não é reconferido (a FR-514 da `035`).
- **FR-3625**: A forma é propriedade da fonte. As fontes de demonstração MUST continuar aceitando o
  que aceitam hoje.
- **FR-3626**: A recusa de forma MUST dizer o valor recusado e a correção: "informe só o número do
  concurso, como 6106 — sem dígito verificador, texto ou ano".

#### A situação da referência

- **FR-3627**: A conferência MUST classificar cada referência em exatamente uma de quatro situações,
  e a situação MUST ser separada da decisão que cada ato toma sobre ela:
  - **realizado**: a fonte registra o concurso como já sorteado;
  - **ainda não realizado**: a fonte registra um último concurso menor que a referência;
  - **inconclusivo**: não foi possível saber;
  - **referência inválida**: a forma da FR-3623 não se cumpre.
- **FR-3628**: A evidência principal MUST ser o último concurso realizado, informado pela fonte. Ele
  só vale se a resposta trouxer número inteiro, data no formato da fonte e os cinco bilhetes. Faltando
  qualquer um deles, a situação é inconclusiva. Referência menor ou igual ao último é realizada.
  Maior é ainda não realizada.
- **FR-3629**: A consulta pela própria referência MUST servir só para acrescentar a data de um
  concurso já sabido realizado. Uma resposta de erro dela, qualquer que seja o código, MUST NOT
  determinar situação nenhuma. Se ela falhar, a situação é realizado, sem data.
- **FR-3630**: A conferência MUST NOT estimar a data de concurso futuro e MUST NOT recusar ou
  advertir por distância. Ela informa a distância em concursos, a partir do último realizado, e em
  dias, entre a data do último e a data declarada.
- **FR-3631**: Num ato, a consulta ao último concurso MUST acontecer no máximo uma vez, qualquer que
  seja o número de referências. A consulta por referência só acontece para referência realizada, uma
  vez por referência distinta. Cada chamada tem tempo limite e nenhuma repetição, de modo que a
  espera acrescentada a um ato é limitada (SC-1097).
- **FR-3632**: A conferência MUST acontecer fora da transação do ato, antes dela. Dentro da
  transação, MUST valer só para as referências do conteúdo efetivamente travado. Uma referência
  desse conteúdo sem consulta correspondente MUST ser tratada como inconclusiva. O instante da
  consulta MUST ser registrado separado do instante do ato.

#### A decisão de cada ato

- **FR-3633**: São conferidas as referências da Loteria Federal dos métodos que governam ao menos
  um marco que ordena por sorteio e ainda tem sorteio a fazer. Na Retificação, só as introduzidas ou
  substituídas por ela: diferentes da referência do mesmo método no conteúdo-base, ou num método que
  passou a ser da Loteria Federal.
- **FR-3634**: Na **submissão** e na **publicação** do Edital:
  - realizado é **impeditivo**, por método, com código próprio;
  - referência inválida é impeditivo (FR-3623);
  - inconclusivo é **advertência**;
  - ainda não realizado é **informação**, que não impede e não adverte.
- **FR-3635**: Na **publicação da Retificação**, a mesma decisão da FR-3634, aplicada só às
  referências da FR-3633. As referências que a Retificação não muda não são consultadas.
- **FR-3636**: No **congelamento da relação**, a conferência MUST fazer parte da operação: o comando
  confere, e não só a prévia. A referência conferida é a declarada no método que a relação vai citar:
  - realizado MUST recusar o congelamento, sem gravar relação;
  - inconclusivo MUST deixar congelar e devolver a advertência junto do desfecho;
  - ainda não realizado congela, como hoje.

  Com a declarada registrada como indisponível, a conferência se cala.
- **FR-3637**: No congelamento, uma referência fora da forma (conteúdo do acervo) MUST gerar
  advertência, e não recusa.
- **FR-3638**: A regra da `102` (da FR-2650 à FR-2665), a recusa por precedência na constituição
  (a FR-016 da `021`), a observação, a regra de substituição e o resumo do método gravado na relação
  MUST continuar como estão. Esta feature soma uma conferência, e não substitui nenhuma.

#### As mensagens

- **FR-3639**: A mensagem de **realizado** MUST dizer:
  - fonte e número;
  - a data em que foi realizado, ou "data não informada pela Caixa";
  - o último concurso realizado e a data dele;
  - o que fazer.

  Nos atos do Edital, o que fazer é declarar concurso posterior ao último, que ocorra depois do fim
  das inscrições, conferido no calendário oficial. No congelamento, é retificar o método antes de
  congelar.
- **FR-3640**: A mensagem de **ainda não realizado** MUST dizer:
  - "ainda não realizado na consulta de DD/MM/AAAA às HH:MM";
  - o último concurso e a data dele;
  - a distância;
  - "a data prevista não é verificada pela Caixa: confira no calendário oficial que o concurso N é o
    de DD/MM/AAAA".

  Ela MUST NOT qualificar o concurso ou a data como validado, confirmado ou conferido.
- **FR-3641**: A mensagem de **inconclusivo** MUST dizer, em palavras de quem opera, por que não foi
  possível: "a Caixa não respondeu", ou "a Caixa respondeu sem o último concurso". Ela MUST dizer que
  isso não confirma nem recusa o concurso, e que ele deve ser conferido no resultado oficial. Ela MUST
  NOT trazer código de exceção, corpo da resposta nem rastro de pilha.
- **FR-3642**: Toda data e hora das mensagens e da trilha MUST estar no fuso institucional.

#### A interface

- **FR-3643**: O campo do concurso MUST continuar campo de texto, com rótulo e ajuda que pedem só o
  número ("como 6115"). Nenhuma lista de concursos é oferecida.
- **FR-3644**: Nenhuma renderização de página MUST consultar a fonte.
- **FR-3645**: Na composição do método, do marco e comum, e na tela do sorteio antes de congelar,
  MUST haver uma conferência sob demanda. Ela mostra, no lugar, a situação e a mensagem das
  FR-3639 a FR-3641, não grava nada, e vale as mesmas chamadas da FR-3631 para uma referência.
- **FR-3646**: As recusas e advertências dos atos MUST aparecer onde as do mesmo ato já aparecem, na
  revisão, na publicação, na Retificação e na tela do sorteio, sem tela nova.

#### A trilha

- **FR-3647**: Todo ato concluído em que a conferência rodou MUST registrar, no registro de
  auditoria que o ato já grava:
  - a referência e a fonte;
  - o instante da consulta;
  - o último concurso informado e a data dele, quando houve;
  - a situação;
  - se a consulta foi conclusiva;
  - a decisão tomada: prosseguiu, ou prosseguiu com advertência.

  Nenhuma tabela nova é criada.
- **FR-3648**: O registro MUST NOT conter o corpo da resposta da fonte, código de exceção ou rastro
  de pilha. O motivo de inconclusão se registra nas mesmas palavras da FR-3641.
- **FR-3649**: O ato recusado pela conferência MUST registrar a conferência no log estruturado, com
  a correlação do pedido, como as demais falhas relevantes (Princípio V). Ele MUST NOT gravar trilha
  de um ato que não aconteceu (D-004).

#### Desenvolvimento e suíte

- **FR-3650**: As fontes de demonstração MUST responder à conferência sem rede, por tabela
  declarada:
  - um conjunto fixo de referências realizadas, para reproduzir a recusa;
  - uma referência inconclusiva, para reproduzir a advertência;
  - as demais, ainda não realizadas.

  Elas continuam fora de produção (a FR-757 da `046`).
- **FR-3651**: A suíte MUST NOT chamar a Caixa. Os casos que declaram a Loteria Federal recebem uma
  conferência substituta que responde "ainda não realizado", salvo quando o caso declara outra
  situação. O teste opt-in contra a fonte real (`SORTEIO_E2E_FONTE_REAL`) MUST continuar passando.
- **FR-3652**: Nenhum Edital publicado, Retificação publicada, relação congelada ou ocorrência
  observada MUST ser alterado ou reconferido por esta feature. Não há migration.

### Key Entities

- **Situação da referência**: valor transitório, nunca persistido como entidade. Tem a situação
  (uma das quatro), a referência, o último concurso e a data dele, a data da referência quando
  realizada, o instante da consulta e o motivo de inconclusão.
- **Conferência registrada**: o mesmo conteúdo da situação, mais a decisão do ato, no detalhe
  estruturado do registro de auditoria do ato.
- **Forma da referência**: propriedade declarada da fonte, ao lado da granularidade que a `102` já
  declara por fonte.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1094**: Sobre as respostas gravadas da Caixa, nos quatro atos e pela tela e pela API, toda
  referência **realizada** é recusada: zero falsos negativos. Nenhuma referência **ainda não
  realizada** ou **inconclusiva** é recusada por esta feature: zero falsos positivos.
- **SC-1095**: Nenhuma mensagem, rótulo ou registro produzido para "ainda não realizado" contém
  "validad", "confirmad" ou "conferid" aplicado ao concurso ou à data. A verificação é uma varredura
  por teste.
- **SC-1096**: Com a fonte sem responder, nas oito formas de falha da POC, os quatro atos concluem
  com advertência: nenhum ato é impedido só pela indisponibilidade. As regras locais (`102`, forma,
  demais impeditivos) continuam impedindo.
- **SC-1097**: Um ato faz no máximo uma consulta ao último concurso, mais uma por referência
  realizada distinta. Nenhuma renderização de página consulta a fonte. A espera acrescentada a um ato
  com a fonte sem responder não passa de 15 segundos.
- **SC-1098**: Para todo ato concluído com conferência, as seis perguntas da FR-3647 são respondidas
  lendo só o registro de auditoria do ato.
- **SC-1099**: A suíte inteira passa sem nenhuma conexão à Caixa: um vigia recusa a chamada. As
  expectativas de testes existentes só mudam nos casos inventariados no plano.
- **SC-1100**: Nenhuma Retificação que deixa a referência intacta faz consulta ou recebe achado desta
  feature, inclusive a de Edital cujo concurso consolidado já foi realizado.

## Assumptions

- O endpoint principal da Caixa continua devolvendo o último concurso realizado com número, data e
  bilhetes, como em 03/11/2026. Se a forma mudar, a conferência degrada para "inconclusivo" (FR-3628),
  e nada é recusado por isso.
- A numeração dos concursos é monotônica: um número menor ou igual ao último já foi realizado. A
  cadeia `numeroConcursoAnterior` das respostas gravadas é coerente com isso.
- A Loteria Federal é a única fonte de produção. Uma fonte nova declara forma e conferência
  próprias, ou fica sem elas: forma livre e nenhuma conferência, sem achado nem advertência.
- A conferência sob demanda (FR-3645) é leitura, e não ato: não exige permissão além da de ver a
  tela onde aparece, e não grava trilha.
- O tempo limite e a ausência de repetição da conferência são do plano. O teto de 15 segundos da
  SC-1097 é o compromisso.

---

## Decisões

### D-001 — A forma é a que a fonte aceita, e se confere sem rede

A API recusa com HTTP 400 tudo que não é inteiro, inclusive a grafia `6106-9` do próprio comunicado
da Caixa. Conferir a forma não precisa de rede, e a gravação do rascunho é o lugar mais barato para
corrigir. Normalizar os zeros à esquerda é inequívoco: a Caixa devolve o mesmo concurso. Retirar um
dígito verificador não é: `6106-9` poderia ser o 6106 ou um erro de digitação do 61069, e por isso
se recusa. Alternativa descartada: aceitar e normalizar `6106-9` para `6106`, o que a 1ª decisão do
usuário proíbe.

### D-002 — "Realizado" é fato, e se recusa em todo ato que compromete

Um número menor ou igual ao último realizado é o único fato que a fonte permite afirmar. Com ele, o
sorteio é certamente recusado na constituição: a data da extração é anterior a qualquer congelamento
futuro. Recusar antes não tem falso positivo, e por isso a recusa vale em todos os atos que
comprometem: submissão, publicação, Retificação que introduz e congelamento.

### D-003 — "Ainda não realizado" é informação, e não confirmação

A fonte não publica data futura, e a POC usava "CONFERIDA", que sugeria uma confirmação inexistente.
O desfecho é informação: não impede e não adverte, porque nada de errado foi encontrado. A mensagem
dá a quem lê o que permite julgar (último concurso, distância) e diz o que não foi verificado.
Estimar a data pela sequência foi descartado: a antecipação da 6106 em 03/10/2026 mostra o custo.

### D-004 — "Inconclusivo" adverte e deixa prosseguir, e só o ato concluído grava trilha

Recusar por queda de terceiro trocaria um erro evitável por um ato legal preso a um serviço que o
Ifes não controla. A garantia de integridade não depende da conferência, porque a precedência na
constituição continua. A trilha registra o ato que aconteceu. Gravar trilha de ato recusado exigiria
escrever fora da transação revertida, que é mecanismo novo, e nenhuma recusa de publicação o faz
hoje. Por isso a recusa vai ao log estruturado com a correlação (FR-3649).

### D-005 — O congelamento recusa o realizado e adverte sobre a forma do acervo

A `102` deixou o congelamento disponível diante de uma **previsão** (a FR-2659 da `102`). Aqui é
**fato**: a relação congelada sob concurso realizado nunca sorteia, e congelar não se desfaz (5ª
decisão). A forma fora do padrão, porém, só existe em Edital do acervo, publicado antes desta
feature. Recusar o congelamento dele deixaria o certame sem saída além da Retificação. A advertência
diz que a Caixa não aceitará a referência, e a decisão fica com quem conduz.

### D-006 — A Retificação confere o que ela introduz, e nada mais

"Introduzido" é a referência diferente da do mesmo método no conteúdo-base, ou a de um método que
passou a ser da Loteria Federal. A definição é por valor, e não pelo caminho declarado na
Retificação: assim ela pega também a troca de método inteiro. Marcos sem sorteio a fazer ficam fora,
pela mesma pergunta que a `102` já faz.

### D-007 — Sob demanda na tela, obrigatória nos atos

Consultar a cada renderização seria carga sobre a Caixa e latência para quem compõe (7ª decisão). O
ato confere sempre. A tela confere quando pedem, com o mesmo resultado, e é isso que permite ver
antes do ato irreversível (Princípio IV).

**A gravação do rascunho também não consulta.** Era uma leitura da 2ª decisão, que pede recusar
"a introdução em nova configuração", e o usuário a confirmou em 04/11/2026. O rascunho não é ato: grava-se a etapa Classificação muitas
vezes, a Caixa fora do ar não pode impedir guardar trabalho, e a gravação recusa o que é local (a
forma, FR-3623). A introdução de um concurso realizado é recusada no primeiro ato que o compromete,
a submissão, e pode ser vista antes pela conferência sob demanda. A alternativa — consultar na
gravação quando a referência muda — foi descartada.

### D-008 — A conferência é da fonte que sabe responder, e a trilha é a que existe

A conferência e a forma ficam ao lado da granularidade que a `102` já declara por fonte. Fonte que
não as declara cai no padrão: forma livre e nenhuma conferência. Assim nenhuma fonte é obrigada a
implementar o que não sabe, e a falta de conferência não vira advertência em todo Edital dela. O detalhe estruturado do registro de auditoria já
existe e já guarda o alcance de atos (a FR-921 da `051`). Usá-lo evita tabela nova e não mistura a
conferência com o motivo humano do ato.

## Pendências do usuário

- **SC humano.** A compreensão das três mensagens por quem opera (realizado, ainda não realizado,
  inconclusivo) não é medida por teste. Se o usuário quiser um roteiro de leitura com a comissão,
  como a `102` fez, ele entra aqui.
