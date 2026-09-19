# Feature Specification: Quatro becos que o sistema já conhece

**Feature Branch**: `claude/spec-037-quatro-becos`

**Created**: 2026-09-19

**Status**: Draft

**Input**: reauditoria de 2026-09-16 ([doc/auditoria-exploratoria-ux-2026-09-16.md](../../doc/auditoria-exploratoria-ux-2026-09-16.md)) — `ACH-46` parte (c) da melhoria 13.1, `ACH-02` e `ACH-30` da 12.1, `ACH-08` da 12.2 e `ACH-16` da 6.10. É o item 3 da ordem de investimento do §13 da reavaliação de 18/09.

> **Faixa de identificadores.** Esta spec abre em **FR-538**, **SC-188** e **UX-062**. Teto medido
> em 19/09/2026 contra a `main` `2beb2d9` **e contra as onze worktrees**, inclusive a
> `spec-036-implementacao`, que está com a implementação da `036` em curso: **FR-537 / SC-187 /
> UX-061**. As **decisões** reiniciam em `D-001`.

---

## Por que esta feature existe

**Nenhum dos quatro achados pede informação nova.** Em todos, o sistema já sabe — e a informação não
chega ao lugar onde a pessoa decide.

| O beco | O que o sistema já sabe | Onde a pessoa trava |
|---|---|---|
| o link do corte some | a tela do corte **já explica** por que está vazia | o caminho até ela não é oferecido |
| duas frases calam | a frase que conduz existe **seis linhas acima**, no mesmo cartão | o bloqueio é dito, o que fazer não |
| a régua está mal calibrada | o portal lê o mesmo Evento como **acontecendo agora** | a gestão o chama de vencido |
| o rótulo mente | a conferência **já sabe** que o peso virou obrigatório | ela só diz na etapa 9 |

As quatro medições abaixo foram feitas no código em 19/09/2026 e **devem ser reconferidas** pelo
Phase 0 do plano: nas quatro features anteriores a medição corrigiu a spec cinco vezes.

### O que a medição achou, e que encolhe metade de um requisito

A melhoria 13.1 pede que o link do corte "passe a levar a uma tela que explica por que está vazio".
**A tela já explica.** A view de destino captura a recusa do domínio e a exibe, com a razão escrita
no próprio código: *"'este marco não corta' e 'a ordem está obsoleta' são estados legítimos da tela,
e quem os lê precisa do motivo"*. O que falta é **só o link**. Esta feature não reescreve a tela —
ver `D-001`.

### O que a medição achou, e que briga com a direção da auditoria

A direção do `ACH-16` é pedir o peso "no momento em que a Etapa é enumerada pelo marco". Medido: o
peso é campo **da Etapa**, e o marco enumera Etapas por uma lista de seleção múltipla. Cumprir a
direção ao pé da letra exigiria mover o peso para o par marco×Etapa — **mudança de modelo, com
migração e conteúdo publicado a preservar** — ou acrescentar um controle por Etapa ao cartão que a
própria auditoria acusa de ter **28 controles**. Ver `D-003`.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O caminho até o corte deixa de sumir (Priority: P1)

Quem conduz um marco classificatório encontra o destino do corte **sempre**, tenha o marco declarado
regra de corte ou não. Quem o abre num marco sem regra lê o motivo, em vez de não ter tido caminho.

**Why this priority**: é a parte (c) da 13.1, o único trecho do `ACH-46` que continua aberto, e a
metade cara dela já está pronta. Custo mínimo contra um achado `P0` parcialmente fechado.

**Independent Test**: compor um marco classificatório **sem** regra de corte, publicar, e conferir
pela tela do Edital que o destino do corte é oferecido e que abri-lo diz por que está vazio.

**Acceptance Scenarios**:

1. **Given** um marco classificatório **sem** regra de corte declarada, **When** alguém que conduz o
   Edital abre a tela dele, **Then** o destino do corte **é oferecido**.
2. **Given** esse mesmo marco, **When** a pessoa abre o destino do corte, **Then** ela lê **por que
   não há faixa** — a frase que a tela já produz hoje, sem alteração.
3. **Given** o marco sem regra e a recusa exibida, **When** a pessoa procura o que fazer, **Then** o
   caminho oferecido é o **da regra de corte**, e não o da classificação — que resolve as outras duas
   recusas desta tela e não esta.
4. **Given** um marco **com** regra de corte declarada, **When** a tela é aberta, **Then** nada muda:
   o destino continua sendo oferecido, continua levando à faixa, e o caminho da recusa de ordem
   ausente continua sendo o da classificação.
5. **Given** alguém que **não alcança** a classificação deste Edital, **When** a tela é montada,
   **Then** o destino do corte **não** lhe é oferecido — a garantia da `033` não é desfeita.

---

### User Story 2 - Os dois bloqueios que calam passam a conduzir (Priority: P1)

Quem esbarra num bloqueio lê **o que fazer e a quem pedir**, na formulação que o produto já pratica,
em vez de ler só que não pode.

**Why this priority**: é o achado de maior retorno por linha alterada de toda a reauditoria, e é `P1`.
A frase modelo já existe **dentro do mesmo cartão** de um dos dois casos.

**Independent Test**: abrir a tela de um Edital publicado como gestor e conferir que o aviso nomeia
a ação e a permissão. *O segundo bloco entra no teste **se** o percurso da `FR-542b` apontar que há o
que fechar* — e, não apontando, o que se confere é o registro dessa decisão.

**Acceptance Scenarios**:

1. **Given** um Edital **publicado**, **When** um gestor abre a tela dele, **Then** o aviso de
   conteúdo imutável nomeia **a ação** (Retificação) e **quem pode praticá-la**.
2. **Given** um Edital recém-criado **sem Perfil** **e o percurso da `FR-542b` tendo apontado que
   falta permissão ao ator**, **When** a validação é exibida, **Then** o impedimento diz o que fazer
   e **a quem pedir**. *Apontando o percurso que nada o impede, este cenário não se aplica* — e o
   que vale é o cenário 5.
3. **Given** um ator que **pode** praticar a ação, **When** o bloco é exibido, **Then** ele recebe o
   caminho — e não a frase de pedir a outra pessoa.
4. **Given** o Edital sem Perfil, **When** a pendência é exibida, **Then** ela **continua** dizendo o
   que falta e levando à etapa de Perfis — o que já existe não é refeito.
5. **Given** o percurso reproduzindo o ator da auditoria, **When** ele esbarra no impedimento,
   **Then** ou falta-lhe uma permissão — e a condução a nomeia — ou não falta, e **isso fica
   registrado como o fechamento do achado**.
6. **Given** qualquer dos dois casos, **When** a condução é escrita, **Then** ela nomeia **a
   permissão**, nunca uma pessoa: não há fila, designação nem nome próprio na tela.

---

### User Story 3 - Um período em curso deixa de ser chamado de vencido (Priority: P2)

Um Edital cujas inscrições **abrem no dia da publicação** deixa de ficar com a etapa do Cronograma
eternamente pendente, e as duas superfícies do produto param de discordar sobre o mesmo Evento.

**Why this priority**: é calibragem, não regra nova — mas hoje um Edital perfeitamente legítimo
**nunca** consegue concluir a etapa 3, e o portal contradiz a gestão sobre o mesmo dado.

**Independent Test**: compor um Cronograma com período de inscrições **em curso**, e conferir que a
etapa do Cronograma conclui e que a conferência de publicação não o acusa.

**Acceptance Scenarios**:

1. **Given** um Evento com início **passado** e término **futuro**, **When** a régua o avalia,
   **Then** ele **não** está vencido, a etapa do Cronograma conclui, e a conferência não o acusa.
2. **Given** um Evento **pontual** — sem término declarado — cujo instante já passou, **When** a
   régua o avalia, **Then** ele **continua** vencido: ausência de término não é término no futuro.
3. **Given** um Evento com início e término **ambos passados**, **When** a conferência o acusa,
   **Then** a frase continua nomeando o **término**, como hoje.
4. **Given** qualquer Evento vencido, **When** o Edital é publicado, **Then** a conferência continua
   **advertindo, e nunca recusando** — nada nesta feature transforma advertência em impedimento.
5. **Given** um mesmo Evento em curso, **When** ele é lido pela gestão e pelo canal do candidato,
   **Then** as duas superfícies **dizem a mesma coisa**.

---

### User Story 4 - O rótulo do peso para de mentir, e a contradição antecipa (Priority: P3)

Quem declara uma Etapa lê que o peso é opcional **enquanto ninguém a enumerar**; e quem enumera a
Etapa num marco descobre ali, e não nove etapas depois, que ela está sem peso.

**Why this priority**: é o menor dos quatro em consequência — a contradição hoje aparece, só que
tarde. Fica por último e pode ser entregue sozinho.

**Independent Test**: declarar uma Etapa sem peso, enumerá-la num marco, e conferir que o cartão do
marco o diz naquele momento.

**Acceptance Scenarios**:

1. **Given** o campo do peso na Etapa, **When** a pessoa o lê, **Then** o rótulo **declara a
   condição**: vazio é legítimo até que um marco enumere esta Etapa.
2. **Given** um marco que enumera uma Etapa **sem peso declarado**, **When** o cartão do marco é
   exibido, **Then** ele **nomeia a Etapa** que falta pesar.
3. **Given** uma Etapa sem peso que **nenhum** marco enumera, **When** as telas são exibidas,
   **Then** nada a acusa: o vazio continua legítimo.
4. **Given** um marco que **ordena por sorteio** e não enumera Etapa alguma, **When** o cartão é
   exibido, **Then** nada é acusado.

---

### Edge Cases

- **Marco que ordena por sorteio.** Não corta e não enumera Etapa. O destino do corte é oferecido do
  mesmo modo, e a tela diz que este marco não corta — que é verdade, e é a mesma frase que ela já
  produz. Registrar se a prosa serve ao caso do sorteio ou se precisa de palavra própria.
- **Ator que pode praticar a ação do bloqueio.** A condução não pode virar *"peça a alguém"* para
  quem já pode: seria mandar pedir a si mesmo.
- **Evento sem início e sem término.** A conferência de forma já o acusa; a régua simplesmente não
  responde, e continua assim.
- **Evento cujo início ainda não chegou.** Não vence, hoje e depois.
- **Edital publicado cujo ator não tem nenhuma das permissões.** A frase precisa nomear a permissão
  sem prometer um caminho que ele não alcança.
- **Etapa enumerada por dois marcos.** O peso é um só — é da Etapa —, e os dois cartões o cobram.
  Quando o peso é declarado, os dois param de cobrar.

---

## Requirements *(mandatory)*

### O caminho até o corte

- **FR-538**: O destino do corte MUST ser oferecido em todo marco classificatório, **declarada ou não
  a regra de corte**. Hoje ele é condicionado à regra, e quem mais precisa entender por que não há
  faixa é exatamente quem não a declarou.
- **FR-539**: A tela de destino MUST continuar explicando por que está vazia, **e esta feature NÃO a
  reescreve** — ela já o faz, e reescrevê-la criaria uma segunda verdade sobre a mesma lista
  (`D-001`).
- **FR-539a**: O **caminho** oferecido ao lado da recusa MUST depender de **qual recusa é**. A tela
  imprime hoje, para as três recusas do corte, o mesmo *"Ir para a classificação deste recorte"* — e
  ele resolve duas delas. Para o marco **sem regra de corte** o que falta é conteúdo do Edital, não
  ordem: mandar quem lê para a classificação seria abrir, no fim do caminho que a `FR-538` cria, um
  segundo caminho que não resolve. *A `FR-538` torna alcançável uma combinação que hoje ninguém
  alcança* — e é por isso que este requisito nasce com ela, e não depois dela.
- **FR-539b**: O caminho da recusa **do marco sem regra** MUST respeitar o que o ator alcança. A tela
  do corte só é percorrida **depois da publicação**, e num Edital publicado a regra de corte não se
  edita: ela muda por **Retificação**. Quem classifica pode não poder retificar — e oferecer-lhe o
  caminho seria abrir, dentro da correção de um beco, o beco que a `033` fechou. Havendo alcance, o
  caminho; não havendo, **a frase que diz a quem pedir**, pelo mesmo mecanismo da `FR-543`.
- **FR-540**: O destino MUST continuar sendo oferecido **apenas a quem o alcança**. A garantia da
  `033` — a tela não oferece caminho que o ator não abre — não é desfeita por esta feature.

### Os dois bloqueios que calam

- **FR-541**: O aviso de **conteúdo imutável** de um Edital publicado MUST nomear a ação e a
  permissão que a pratica, na formulação que o produto já usa. *Ele hoje diz que correções ocorrem
  por Retificação e para aí* — e o mesmo cartão, seis linhas acima, já pratica a frase que falta.
- **FR-541a**: A pergunta *"esta pessoa pode retificar?"* MUST ser derivada **uma vez**. O mesmo
  cartão já a responde para decidir se oferece a ação de Retificar; o aviso passa a depender da
  **mesma** derivação, e não de uma segunda. *Duas respostas para a mesma pergunta divergem na
  primeira mudança* — é o que a `034` gastou uma feature inteira corrigindo em outra tela.
- **FR-541b**: O aviso MUST **calar** quando a ação de Retificar já está oferecida ali. Dizer *"peça
  a alguém"* ao lado do botão que a pessoa pode clicar é pior do que não dizer nada: ensina a
  desconfiar da tela.
- **FR-541c**: A condução MUST ser **prosa no aviso**, e não uma ação desabilitada na lista. A lista
  de ações **não oferece destino que o ator não abre** — é a regra que a `007` e a `033` deixaram,
  e transformar Retificar em botão morto com motivo a desfaria. *Esta linha existe porque a
  alternativa é plausível e está errada*, e quem implementar vai considerá-la.
- **FR-542**: O impedimento por **ausência de Perfil** MUST dizer **a quem pedir** quando o ator não
  pode resolvê-lo. *"O que fazer" já é dito*: a pendência é marcada corrigível e leva à etapa de
  Perfis, e isso foi fechado por feature anterior. O que falta é a outra metade — e dizê-la exige
  que a montagem das pendências conheça **o ator**, o que hoje ela não conhece.
- **FR-542b**: Antes de a condução ser escrita, o percurso MUST decidir **se ainda há o que fechar**:
  a auditoria inferiu papel ausente da ausência de controle, e o controle existe. Se o gestor da
  auditoria travava por outra razão, o achado se fecha **registrando isso**, e não escrevendo frase
  para um problema que não existe.
- **FR-542a**: A condução MUST nascer **onde a tela a exibe**, e não na mensagem normativa. A
  mensagem descreve o defeito do **conteúdo**, é lida por mais de uma superfície e não conhece quem
  está olhando; condução depende de quem lê (`D-002`).
- **FR-543**: Toda condução MUST ser produzida pelo **mecanismo único** que o produto já tem para
  dizê-la, e não redigida à mão. Existe **uma** maneira de dizer isto, e ela é pública exatamente
  para que não nasça uma segunda; imitar o texto numa tela nova derrota a guarda que a criou.
- **FR-543a**: A formulação MUST ser a **cheia** — *"peça a alguém com a permissão de X **que Y**"*.
  Das quatro ocorrências de hoje, uma larga a oração final e diz só a quem pedir, sem dizer o quê.
- **FR-543b**: Toda condução MUST nomear **a permissão**, nunca uma pessoa. Não há fila, designação
  nem nome próprio — é a disciplina que o produto já mantém.
- **FR-544**: Quem **pode** praticar a ação MUST receber o caminho, e não a frase de pedir a outra
  pessoa. *Medido: a lista de ações do cartão **já entrega** o caminho a quem pode retificar.* O que
  esta feature acrescenta não é o caminho — é o silêncio do aviso nesse caso (`FR-541b`) e a frase
  no caso oposto.

### A régua do vencido

- **FR-545**: Havendo **término declarado**, o Evento MUST ser considerado vencido somente quando o
  término já passou. Um período em curso não é um período vencido.
- **FR-546**: **Não** havendo término, o Evento MUST continuar vencendo pelo início. *Este requisito
  existe para impedir a correção errada*: trocar a régua por "o término passou" silenciaria o Evento
  pontual, e a ausência de término é Evento que o Edital não fechou — nunca um fim no futuro.
- **FR-546a**: A escolha do **instante que a frase nomeia** MUST mudar junto com a régua. Se o
  predicado deixar de vencer o Evento em curso e a escolha do instante continuar apontando o início
  dele, as duas passam a **discordar sobre o mesmo Evento** — que é a divergência que levou a régua a
  virar módulo. Elas mudam no mesmo ato ou o módulo perde a razão de existir.
- **FR-547**: A régua MUST continuar **única**. As duas superfícies que a consultam — o selo da etapa
  do Cronograma e a conferência de publicação — derivam dela, e foi para que não discordassem que ela
  virou módulo.
- **FR-548**: O vencido MUST continuar sendo **advertência, e nunca recusa** (`FR-343`). Existe Edital
  legítimo com Evento vencido, e esta feature não toca nisso.
- **FR-549**: A frase da conferência MUST continuar nomeando o **término** quando os dois instantes
  passaram (`FR-343a`), e o caminho do achado MUST continuar acompanhando o instante nomeado.
- **FR-549a**: A concordância entre a gestão e o canal do candidato é de **desfecho**, e não de
  código. As duas leituras são independentes — o canal do candidato deriva a situação do Evento por
  conta própria —, e **unificá-las não é escopo desta feature**. O que se exige é que passem a dizer
  a mesma coisa sobre o mesmo Evento; como cada uma chega lá continua sendo assunto delas.

### O rótulo do peso

- **FR-550**: O rótulo do peso MUST **declarar a condição** em vez de afirmar opcionalidade sem
  ressalva: o vazio é legítimo até que um marco enumere aquela Etapa.
- **FR-551**: O cartão do marco MUST **nomear as Etapas que ele enumera sem peso declarado**, no
  momento em que as enumera. A conferência já sabe disso; ela só diz nove etapas depois.
- **FR-551a**: Nenhum **controle novo** MUST ser acrescentado ao cartão do marco. Ele já carrega 28,
  e a densidade dele é achado próprio, fora desta feature.
- **FR-552**: O peso MUST continuar sendo campo **da Etapa**. Movê-lo para o par marco×Etapa é
  mudança de modelo, com migração e conteúdo publicado a preservar, e não cabe aqui (`D-003`).

### O que esta feature não faz

- **FR-553**: Nenhuma regra de domínio MUST mudar **o que decide**. O que muda é onde a informação é
  avaliada, quando ela é dita e a calibragem de um predicado — nunca o desfecho de um ato.
- **FR-554**: Nenhuma ajuda visível MUST ser acrescentada aos cartões. Microcópia nova vai para onde
  a regra do produto já manda, e essa decisão foi tomada deliberadamente pela `030`.
- **FR-555**: Nenhum conteúdo publicado MUST ser reescrito, e nada MUST ser apagado.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-188**: Um marco **sem** regra de corte declarada oferece o destino do corte, e quem o abre lê
  por que não há faixa — percorrido pela interface, **sem shell e sem banco**.
- **SC-189**: **Zero** bloqueios no cartão "O que fazer agora" sem ação nomeada e sem a quem pedir —
  contados na tela, antes e depois. *Este critério alcança o aviso de conteúdo imutável, e só ele*:
  o cartão existe numa tela, e a pendência de Perfil vive noutra.
- **SC-195**: O `ACH-02` tem **desfecho escrito**, qualquer que ele seja: ou a condução existe e é
  lida nas telas de composição que exibem a pendência, ou está registrado por que não há o que
  escrever. *Um achado sem desfecho registrado é um achado que volta na próxima auditoria* — e este
  é o único da feature cujo resultado depende de um percurso.
- **SC-190**: Um Edital cujo período de inscrições está **em curso** conclui a etapa do Cronograma —
  hoje ela é impossível de concluir.
- **SC-191**: **Zero** divergências entre a gestão e o canal do candidato sobre o mesmo Evento.
- **SC-192**: Quem enumera uma Etapa sem peso lê isso **no momento em que enumera**, e não na etapa
  de conferência.
- **SC-193**: **Zero** controles acrescentados ao cartão do marco e **zero** campos movidos de
  entidade — conferido por comparação do antes e do depois.
- **SC-194**: **Zero** desfechos de ato alterados: as mesmas entradas produzem as mesmas decisões.

---

## Assumptions

### D-001 — a tela do corte já explica, e não será reescrita

Decidido em 19/09/2026, pela medição.

A melhoria 13.1(c) descreve duas coisas: o link deixar de ser condicionado, e o destino explicar por
que está vazio. **A segunda já existe** — a view captura a recusa do domínio e a mostra, com a razão
registrada por escrito no código. Reescrevê-la produziria uma segunda frase sobre o mesmo estado, e
duas verdades sobre a mesma lista divergem na primeira mudança.

**A Phase 0 conferiu, e a frase é deste caso.** Ela tem código próprio — a recusa distingue *"este
marco não declara regra de corte"* de *"a ordem está obsoleta"* — e sai como conflito, não como
ausência, de modo que a tela a mostra em vez de virar erro de página inexistente. Nada a reescrever.

**Mas a mesma medição achou o que a decisão não cobria.** O que a tela anexa à frase — o caminho — é
único para as **três** recusas que passam por ali, e foi escrito para as outras duas. Abrir o link
sem corrigir isso entregaria um beco no fim do caminho criado para remover um beco. Daí a `FR-539a`:
**a frase não muda; o caminho passa a depender de qual recusa é.**

### D-002 — a condução nasce na tela, e não na mensagem normativa

Decidido em 19/09/2026.

O impedimento por ausência de Perfil é achado de **validação**, e a frase nasce no domínio. Ela fica
como está. A condução — o que fazer, a quem pedir — é acrescentada **onde a tela exibe o achado**.

**A razão é que condução depende de quem lê.** A mensagem normativa descreve um defeito do conteúdo:
ela é a mesma para qualquer pessoa, é lida por mais de uma superfície e não conhece as permissões de
quem está olhando. "Peça a alguém com a permissão de X" é falso para quem tem a permissão de X —
`FR-544` —, e uma mensagem de domínio não tem como saber disso.

**Alternativa descartada**: enriquecer a mensagem no domínio, que seria menos código e uma frase só —
e que obrigaria o domínio a conhecer o ator, contrariando a separação que o produto mantém.

### D-003 — o peso continua sendo da Etapa; a contradição é que antecipa

Decidido em 19/09/2026 por quem governa o backlog, com a medição na mesa.

A direção literal do `ACH-16` — pedir o peso onde a Etapa é enumerada — exigiria movê-lo para o par
marco×Etapa. **Isso é mudança de modelo**, com migração e conteúdo publicado a preservar, e briga
com as duas restrições desta feature: "nenhuma regra muda" e "meio dia de trabalho".

O que se entrega no lugar: o rótulo **para de mentir** (`FR-550`) e a contradição **antecipa** —
o cartão do marco nomeia, ao enumerar, as Etapas sem peso (`FR-551`). Nenhum controle novo, nenhum
campo movido.

**O que fica em aberto, e é decisão de governança:** a mesma Etapa pode legitimamente pesar diferente
em dois marcos, e hoje não pode. Isso é modelo, tem spec própria, e **fica registrado aqui como
achado, não como escopo**.

---

## Out of Scope

Cada um com spec própria:

- a **instrução do recurso** (`036`), **em implementação agora** — esta feature não encosta nas telas
  e nos modelos que ela está mudando;
- a **validação cruzada entre fontes normativas** (`E-4`, `ACH-41`, `ACH-13`, `ACH-18`, `ACH-26`);
- as **sete recusas de autorização fora das portas**, com o inventário que a `033` deixou pronto;
- o **painel de condução do Processo vivo** (`E-6`, `ACH-25`);
- o **renderizador normativo único** das telas de ato (`E-3`);
- a **densidade do marco e do Perfil** (`ACH-10`, `ACH-05`) e os **oito contadores concorrentes**
  (`ACH-27`) — são densidade, e esta feature é sobre conduta;
- o **peso por marco×Etapa**, registrado em `D-003`.
