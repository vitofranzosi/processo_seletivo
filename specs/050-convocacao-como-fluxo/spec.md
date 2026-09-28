# Feature Specification: A convocação como fluxo, e não como três formulários por pessoa

**Feature Branch**: `claude/convocacao-fluxo-unificado-11e7a3`

**Created**: 2026-09-28

**Status**: Draft

**Input**: pedido do usuário de 28/09/2026. É o **passo 3** da ordem adotada em 27/09
([decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md), *"Depois da reavaliação de
27/09"*), antecipado para antes do piloto por decisão do usuário. Executa o item 2 da *Priorização* da
[reavaliação de 27/09](../../doc/reavaliacao-pos-consolidacao-2026-09-27.md) (§E.2, §F.2; anexo B, §9 e
§17) e a `DP-16`, decidida em 28/09 pela opção **B**.

> **Faixa de identificadores.** Abre em **FR-860**, **SC-320** e **UX-100**, contíguos, por indicação do
> usuário. O teto medido em 28/09/2026 em todas as worktrees era 831, 305 e 093, da `049` (operar por
> marco, ainda sem commit); a faixa desta spec não encosta nela. As **decisões** reiniciam em `D-001`;
> decisão de outra spec é citada pelo requisito que a registra, e nunca pelo número local dela.

> **Teto proporcional.** Três laços por pessoa viram gestos por recorte, e o que é decisão sobre uma
> pessoa continua por pessoa. Cada requisito tem de nomear o que a tela ou o ato fazem de diferente; o
> que não passar nisso é nota de tarefa.

---

## Por que esta feature existe

**Convocar é o laço mais fino do sistema, e ele não protege decisão nenhuma na maior parte das vezes.**
Hoje, cada pessoa chamada custa três formulários — convocar, comunicar e registrar o desfecho — e cada
desfecho obriga a reapurar a ocupação do recorte antes da chamada seguinte. Em cada convocação,
espécie, vencimento e fundamento são digitados de novo. No 28/2026, com 280 vagas, isso dá **de 460 a
1.270 formulários**, e a conta cresce com as vagas, não com a demanda (anexo B, §15.2).

O código já diz que a primeira chamada não é decisão. A convocação do titular *"é formalizar o que o
número já diz"*: com 40 vagas e 40 titulares habilitados, as 40 pessoas precisam ser chamadas, e a
faixa e a fila já decidiram quem são (`convocacao/application/convocar.py`, no `_recusar_por_deficit`).

| Laço de hoje | Unidade | O que o operador decide nele | O que esta feature faz |
|---|---|---|---|
| Convocar o titular | pessoa | nada: a faixa e a fila decidiram | um ato por recorte, com um registro por pessoa |
| Convocar o suplente | pessoa | quando chamar a vaga que vagou | continua um a um, sem digitar o que é derivado |
| Escolher a espécie | pessoa | nada: a posição da pessoa a determina | derivada, e mostrada |
| Digitar o fundamento | pessoa | nada que o Edital e os atos-fonte já não digam | derivado, e mostrado; complemento opcional |
| Digitar o vencimento | pessoa | o prazo que o Edital publicou, repetido | informado uma vez por ato, ou tirado de um Evento do Cronograma |
| Emitir a comunicação | pessoa | nada: a forma é a que o Edital declarou | sai do próprio ato de convocar; por publicação, um gesto registra onde se publicou |
| Não atendimento dos vencidos | pessoa | que o prazo venceu sem resposta — o mesmo juízo N vezes | um gesto, N registros com autor (`DP-16`, B) |
| Reapurar depois de cada desfecho | recorte × desfecho | nada: é conta | deixa de ser passo à mão (ver o plano) |
| Aceite, indeferimento, regularização, desistência, reclassificação, inércia | pessoa | **sim** — é decisão sobre uma pessoa | continua individual |

**O contrapeso é a `DP-17`.** O que o sistema derivar fica visível antes do ato irreversível, com a
origem de cada valor; e o gesto que alcança N pessoas declara as N antes da confirmação. Aqui um valor
errado não fica num rascunho: vira N atos append-only, que só se corrigem por sucessão, um a um.

**O que não muda.** Um registro por pessoa, append-only, com autor. O cadastro de reserva sem vagas
imediatas continua fora do sistema (`DP-05`). E a Mesa, o recurso e o desfecho que decide sobre uma
pessoa continuam sendo o custo irredutível — é neles, e não na formalização, que o trabalho humano
deve ficar.

---

## Clarifications

### Session 2026-09-28

- Q: De onde vem o vencimento da convocação, se o Edital publicado não o declara em campo próprio? →
  A: Informado **uma vez por ato**, e vale para todas as pessoas do ato; quem conduz pode tirá-lo do fim
  de um Evento do Cronograma publicado, e a prévia mostra a origem. A composição não muda.
- Q: O gesto que convoca num ato só alcança também os suplentes que cobrem as vagas faltantes? → A:
  **Não: só os titulares**, como decidido. O suplente continua chamado um a um, sem digitar espécie,
  vencimento nem fundamento, e com a comunicação saindo do ato.
- Q: Quando o Edital comunica por publicação, onde o gesto registra onde ela foi publicada? → A: **Num
  segundo gesto**: o ato convoca; depois de publicar a lista, quem conduz registra num gesto só onde e
  quando publicou, para todas as convocações do recorte ainda sem comunicação enviada.

---

## User Scenarios & Testing *(mandatory)*

**Ator.** Quem gere a comissão do certame — a mesma base de autoridade que já convoca, emite a ordem,
o corte e a apuração. Esta feature não cria papel, permissão nem capacidade de autoridade nova.

**Unidade.** O recorte: o par (Perfil, Modalidade de Concorrência) de um marco, onde a convocação já
acontece hoje. Operar vários recortes num gesto é da `049`, e não daqui.

### User Story 1 - Convocar os titulares num ato só (Priority: P1)

Quem conduz abre a convocação de um recorte com apuração vigente. A tela mostra, antes de qualquer
ato, **quem será convocado** — os titulares ainda não chamados, na ordem —, o vencimento, o fundamento, a
forma de comunicação que o Edital declarou e, quando alguém da fila fica de fora, quem e por quê. Quem
conduz confirma uma vez. Nascem N convocações, uma por pessoa, com autor, e a comunicação de cada uma
sai no mesmo gesto.

**Why this priority**: é o laço mais caro da operação, e o único em que a pessoa repete o mesmo gesto
por dezenas de pessoas sem decidir nada. Sozinha, esta história já tira ~280 formulários de convocar e
~280 de comunicar do 28/2026.

**Independent Test**: montar um recorte com 5 vagas, 5 titulares habilitados e 3 suplentes, com
apuração emitida e forma de comunicação declarada; abrir a tela; conferir a prévia com as 5 pessoas;
informar o vencimento uma vez; confirmar; conferir 5 convocações para vaga inicial com o mesmo
vencimento, 5 comunicações enviadas, a trilha com uma linha por pessoa e a fila começando pelo primeiro
suplente.

**Acceptance Scenarios**:

1. **Given** um recorte com apuração vigente e 5 titulares ainda não chamados, **When** quem conduz
   abre a convocação, **Then** a tela declara as 5 pessoas, na ordem, com a espécie *"para vaga
   inicial"*, o vencimento, o fundamento e a forma de comunicação, **e nenhum ato é praticado**; e os 3
   suplentes ficam fora da prévia, com a razão: o gesto alcança só os titulares.
2. **Given** a mesma prévia, **When** quem conduz confirma, **Then** nascem 5 convocações, cada uma
   com a proveniência de hoje (apuração, ordem, corte, versão), o mesmo autor e o mesmo instante, e a
   comunicação de cada uma é emitida.
3. **Given** a prévia aberta, **When** outro ato muda o alcance antes da confirmação — uma convocação
   individual, um desfecho, uma apuração nova —, **Then** a confirmação é recusada, nada é gravado, e a
   tela mostra o alcance de agora.
4. **Given** um envio individual que falha para uma das 5 pessoas, **When** o ato termina, **Then** as 5
   convocações continuam praticadas, 4 estão com o prazo em curso e 1 com *"prazo não iniciado"*, e a
   tela diz quantas falharam e oferece emitir de novo as que falharam, num gesto.
5. **Given** o mesmo pedido de confirmação enviado duas vezes, **When** o segundo chega, **Then** ele
   devolve o resultado do primeiro, e nenhuma pessoa é convocada nem comunicada duas vezes.
6. **Given** um Edital que comunica por publicação, **When** o ato de convocar termina, **Then** as N
   convocações nascem com o prazo não iniciado, e a tela oferece registrar, num gesto, onde e quando a
   lista foi publicada; registrado, o prazo das N corre a partir dali.
7. **Given** um Evento do Cronograma publicado com data de fim, **When** quem conduz o escolhe como
   origem do vencimento, **Then** a prévia mostra o vencimento com o nome do Evento ao lado; **Given**
   um vencimento digitado, **Then** a prévia diz que foi informado neste ato.
8. **Given** um recorte cujo Edital não declarou a forma de comunicar a convocação, **When** quem
   conduz abre a tela, **Then** a prévia diz que o ato não pode ser praticado e por quê, e aponta a
   Retificação que declara a forma.

---

### User Story 2 - Espécie, vencimento e fundamento deixam de ser digitados (Priority: P1)

Em toda convocação — a do gesto em lote e a individual, que continua para o suplente e para a
exceção —, a espécie sai da posição da pessoa e o fundamento sai do Edital e dos atos que fundamentam
a chamada. O vencimento é informado uma vez por ato, ou tirado do fim de um Evento do Cronograma
publicado. Os três aparecem antes da confirmação, cada um com a sua origem.

**Why this priority**: sem ela, o gesto em lote teria de pedir os três valores de novo, e a chamada
individual continuaria pedindo o que o sistema sabe. É a metade *"derivar o que é derivável"* do passo 3.

**Independent Test**: no recorte da US1, conferir na prévia a espécie de cada pessoa, a origem do
vencimento e o texto do fundamento; convocar individualmente um suplente e conferir que a tela não
pergunta a espécie e já traz o fundamento.

**Acceptance Scenarios**:

1. **Given** uma pessoa que ocupa vaga pela contagem da apuração e ainda não foi chamada, **When** o
   sistema a inclui numa convocação, **Then** a espécie é *"para vaga inicial"*; **Given** quem não
   ocupa e é chamado para a vaga que falta, **Then** é *"para vaga que vagou"*; **Given** quem está na
   fila dos indeferidos, **Then** é *"para regularizar"*.
2. **Given** um pedido de convocação com espécie informada que diverge da derivada, **When** ele chega
   ao sistema, **Then** é recusado, nomeando a espécie que a posição da pessoa determina.
3. **Given** a prévia, **When** quem conduz a lê, **Then** o fundamento aparece por extenso, citando o
   Edital, o recorte e os atos que o sustentam, e quem conduz pode acrescentar um complemento, que entra
   no registro junto do texto derivado.
4. **Given** a prévia, **When** quem conduz a lê, **Then** o vencimento aparece em data e hora locais,
   com a origem dita — *"informado neste ato"* ou o nome do Evento do Cronograma — e com a referência de
   onde o prazo corre.

---

### User Story 3 - O não atendimento de todos os vencidos, num gesto (Priority: P2)

Quando os prazos de uma chamada vencem, quem conduz vê, no recorte, quantas convocações têm o
vencimento decorrido sem desfecho, e quais. Confirma uma vez. Nasce um desfecho de não atendimento por
pessoa, cada um com autor, fundamento e o efeito na ocupação, exatamente como nasceria um a um.

**Why this priority**: é o segundo maior laço depois da primeira chamada, e o único desfecho que não
decide nada sobre a pessoa além do que o relógio já mostrou. Decidido na `DP-16`, opção B: um gesto, N
registros com autor. A opção C, derivar sem ato, foi recusada porque apaga o autor.

**Independent Test**: convocar 4 pessoas com vencimento próximo, emitir as comunicações, deixar 1
aceitar, avançar o relógio além do vencimento; conferir a prévia com 3 pessoas; confirmar; conferir 3
desfechos de não atendimento, 3 efeitos de exclusão, 3 linhas na trilha com o mesmo autor, e a fila
seguinte.

**Acceptance Scenarios**:

1. **Given** um recorte com 3 convocações de vencimento decorrido e sem desfecho, 1 com o prazo em
   curso e 1 com o prazo não iniciado, **When** quem conduz abre o gesto, **Then** a prévia declara as 3,
   com o vencimento e o envio de cada uma, e diz por que as outras 2 ficam de fora.
2. **Given** a mesma prévia, **When** quem conduz confirma, **Then** nascem 3 desfechos de não
   atendimento, um por convocação, cada um com o seu efeito de exclusão na ocupação e a sua linha na
   trilha, com o autor do gesto.
3. **Given** uma convocação cujo desfecho alguém registrou individualmente depois da prévia, **When** a
   confirmação chega, **Then** ela é recusada, nada é gravado, e a tela mostra o alcance de agora.
4. **Given** um recorte sem convocação vencida, **When** quem conduz abre a tela, **Then** o gesto não é
   oferecido.
5. **Given** um desfecho de não atendimento registrado pelo gesto, **When** alguém o lê no histórico,
   **Then** ele é indistinguível, em forma e em garantia, do registrado um a um, e a trilha permite saber
   quais nasceram do mesmo gesto.

---

### User Story 4 - A apuração seguinte deixa de ser passo à mão (Priority: P2)

Depois de um desfecho, a apuração vigente do recorte envelhece, e hoje convocar é recusado até alguém
abrir a tela da ocupação e emitir a seguinte. Com esta feature, quando a única coisa que mudou desde a
apuração foi o desfecho registrado aqui, a convocação seguinte não exige esse passo: o número que a
motiva já está disponível, e continua sendo o de um ato com autor e proveniência.

**Why this priority**: sem ela, o gesto da US3 é seguido de uma ida obrigatória à ocupação, e cada
desfecho individual também. O laço *"apurar → convocar → desfechar → reapurar"* é o que o anexo B, §9,
aponta como o real.

**Independent Test**: no recorte da US3, depois do gesto de não atendimento, abrir a convocação e
conferir que a prévia seguinte já oferece os próximos da fila, sem visita à ocupação; conferir no
histórico da ocupação que o número que a motiva é reconstruível.

**Acceptance Scenarios**:

1. **Given** uma apuração vigente e não obsoleta, **When** um desfecho é registrado — pelo gesto ou um a
   um —, **Then** a convocação seguinte do recorte não é recusada por apuração obsoleta.
2. **Given** uma apuração que já estava obsoleta por outra causa — ordem sucedida, corte obsoleto,
   quadro retificado, movimento de vaga —, **When** um desfecho é registrado, **Then** nada muda em
   relação a hoje: a obsolescência continua declarada com a causa, e o passo à mão continua exigido.
3. **Given** qualquer desfecho, **When** alguém lê o histórico da ocupação, **Then** o número que motivou
   cada convocação posterior é reconstruível a partir de atos, com autor.
4. **Given** um desfecho depois do qual a conta seguinte moveria vaga entre recortes pela reversão que o
   Edital declarou, **When** o ato termina, **Then** a apuração seguinte **não** é emitida por ele, e a
   tela diz que a emissão, com o movimento, é ato da ocupação: mover quantidade entre recortes continua
   sendo decisão tomada ali, e não efeito de um desfecho (`FR-270`).

---

### User Story 5 - O suplente continua chamado um a um, sem formulário por dentro (Priority: P3)

Depois de desfechos que liberam vaga, a fila diz quem é o próximo. Quem conduz o chama pela chamada
individual, que deixa de perguntar a espécie e já traz o fundamento; informa o vencimento, se o Edital
publica prazo; e a comunicação sai do mesmo ato. É um formulário por suplente, e não três.

**Why this priority**: o usuário fixou o gesto em lote nos titulares, porque chamar a vaga que vagou é
escolha de quando chamar. O que resta é tirar do suplente o que não é escolha.

**Independent Test**: no recorte da US3, com vagas liberadas, convocar o primeiro suplente pela chamada
individual; conferir que a tela não pergunta a espécie, que o fundamento vem derivado e que a
comunicação sai no mesmo ato.

**Acceptance Scenarios**:

1. **Given** um recorte com vaga faltante descoberta e suplentes na fila, **When** quem conduz abre a
   chamada individual, **Then** a espécie aparece como *"para vaga que vagou"*, derivada, e o fundamento
   por extenso, e o único campo a informar é o vencimento, com o complemento opcional.
2. **Given** a chamada confirmada, **When** o ato termina, **Then** a comunicação foi emitida no mesmo
   ato, sem segundo formulário.
3. **Given** o gesto em lote, **When** quem conduz abre a prévia, **Then** nenhum suplente está nela.

---

### Edge Cases

Estes casos são requisitos. Cada um tem linha na matriz de rastreabilidade.

- **O gesto nunca pula ninguém.** O alcance é o começo da fila, na ordem, até o primeiro que o gesto
  não pode incluir; quem vem depois dele fica de fora, e a prévia diz por quê. Passar alguém à frente
  continua sendo a chamada individual com fundamento de precedência, como hoje (`FR-267`).
- **Reabilitado por deferimento à frente.** Ele está no topo da fila (`FR-292b`). Se ocupa vaga pela
  contagem, entra no gesto como qualquer titular; se não ocupa, o gesto para nele, e a prévia diz que a
  decisão recursal devolveu a vez a ele, e que chamá-lo é a chamada individual.
- **Reclassificado.** Continua no fim da fila e só é chamável depois do último suplente (`FR-283`). O
  gesto não o alcança antes disso.
- **Pessoa com chamada em aberto.** Não entra de novo: ela já foi chamada, e a fila já a exclui.
- **Recorte sem apuração, com apuração obsoleta por outra causa, sem ordem vigente ou com a lista
  alcançada esgotada.** O gesto não é oferecido, e a tela diz a recusa que a convocação individual daria
  hoje, com o mesmo código.
- **Recorte de cadastro de reserva sem vagas imediatas.** Continua fora (`DP-05`): não há titular, a
  apuração não tem déficit, e o gesto não alcança ninguém. A tela não sugere o contrário.
- **Forma de comunicação por publicação.** O sistema não publica no site do certame. O ato convoca, e
  as convocações nascem com o prazo não iniciado; depois de publicar a lista, quem conduz registra num
  segundo gesto onde e quando publicou, e o prazo de todas as alcançadas corre dali (`FR-876`).
- **Evento do Cronograma sem data de fim.** Não é oferecido como origem do vencimento: o início de um
  Evento não é prazo para atender.
- **Titular eliminado.** A vaga dele fica faltando, e quem a cobre é suplente: não entra no gesto.
- **Vencimento anterior ao envio.** Nenhuma convocação do gesto nasce com vencimento que já passou ou
  que vence no instante do envio (`FR-269b`); a prévia o recusa antes da confirmação.
- **Convocação sem vencimento.** Onde o Edital não publica prazo, ninguém entra no gesto de não
  atendimento por vencimento: o não atendimento dessas continua individual, como hoje, depois do envio.
- **Prazo não iniciado.** Convocação cuja comunicação falhou não está vencida, por mais antiga que seja
  a data: o prazo não começou (`FR-269a`). Fica fora do gesto de não atendimento.
- **Envio que falha no meio do gesto.** As convocações continuam praticadas, e a falha de uma não
  impede o envio das outras.
- **Estado indeterminado de envio.** Se o registro de uma emissão não chegou a ser gravado depois de a
  mensagem sair, reemitir não reenvia em silêncio: vale a guarda de hoje, pessoa a pessoa.
- **Desfecho registrado enquanto o gesto de não atendimento está na prévia.** A confirmação é recusada
  (US3, cenário 3), porque o alcance mudou.
- **Retificação publicada entre a prévia e a confirmação.** Se ela muda a forma de comunicar, o quadro
  ou o fundamento derivado, o alcance mudou e a confirmação é recusada.
- **Recorte grande.** O gesto de um recorte com 85 pessoas — o maior recorte do 28/2026 — é uma
  confirmação só, e não uma página de 25 como era a consolidação.

---

## Requirements *(mandatory)*

### O ato que convoca N pessoas

- **FR-860**: O sistema MUST permitir convocar, num único ato confirmado, os **titulares** do recorte
  ainda não chamados — quem ocupa vaga pela contagem da apuração vigente —, gravando **uma convocação por pessoa**,
  cada uma com autor, instante, fundamento e a proveniência que a convocação individual já grava
  (`FR-294`).
- **FR-861**: O alcance do ato MUST ser o começo da fila de chamada, na ordem, até o primeiro que não é
  titular, e MUST NOT pular ninguém. Suplente MUST NOT entrar no ato em lote: chamar a vaga que vagou
  continua sendo a chamada individual. A precedência justificada continua exclusiva da chamada
  individual (`FR-267`).
- **FR-862**: Antes da confirmação, a tela MUST declarar cada pessoa alcançada — protocolo, nome,
  posição e espécie —, o vencimento, o fundamento, a forma de comunicação, e, quando o ato para antes
  do fim da fila, quem é o primeiro que fica de fora e por quê (`DP-17`).
- **FR-863**: A confirmação MUST carregar a identidade do alcance que foi declarado, e o sistema MUST
  recusá-la, sem gravar nada, quando o alcance de agora diverge dele; a recusa MUST mostrar o alcance
  de agora.
- **FR-864**: Cada convocação do ato MUST passar pelas mesmas recusas da convocação individual —
  ordem vigente, apuração ausente ou obsoleta, faixa, déficit, chamada em aberto —, e uma recusa de
  qualquer uma MUST impedir o ato inteiro: o ato é um só, e não grava metade.
- **FR-865**: O ato MUST ser idempotente pela chave da confirmação: repetido, devolve o resultado do
  primeiro e não convoca nem comunica ninguém de novo.

### O que é derivado

- **FR-866**: O vencimento MUST ser informado **uma vez por ato** — digitado, ou tirado do fim de um
  Evento do Cronograma publicado, escolhido no ato —, MUST ser o mesmo para todas as convocações do
  ato, MUST ter a origem na trilha de cada convocação, e MUST continuar não sendo calculado em dias úteis
  (`FR-269`). Vazio continua significando que o Edital não publica prazo.
- **FR-867**: A espécie de cada convocação MUST ser derivada da posição da pessoa: *para vaga inicial*
  para quem ocupa vaga pela contagem da apuração vigente; *para vaga que vagou* para quem não ocupa e é
  chamado para vaga faltante; *para regularizar* para quem vem da fila dos indeferidos. A tela MUST
  NOT pedi-la.
- **FR-868**: Um pedido de convocação com espécie informada que diverge da derivada MUST ser recusado,
  nomeando a espécie devida.
- **FR-869**: O fundamento de cada convocação MUST ser derivado — o Edital, o recorte, a espécie, e a
  ordem, o corte e a apuração que fundamentam a chamada —, MUST aparecer por extenso antes da
  confirmação, e MUST admitir um complemento opcional de quem conduz, gravado junto do texto derivado.
  O texto gravado é o que foi mostrado.
- **FR-870**: A convocação individual, que continua para a exceção (precedência justificada, sucessão,
  chamada para regularizar), MUST aplicar as mesmas derivações de espécie, vencimento e fundamento, e
  MUST mostrá-las antes da confirmação.

### A comunicação que sai do ato

- **FR-871**: A comunicação de cada convocação MUST ser emitida pelo próprio ato de convocar — no gesto
  em lote e na chamada individual —, na forma que o Edital declarou, sem um segundo formulário.
- **FR-872**: Cada envio MUST manter as garantias que a emissão avulsa já tem: acontece fora da
  transação do ato, com a chave reservada antes do envio; falha registrada não desfaz a convocação nem
  inicia o prazo (`FR-269a`); estado indeterminado não reenvia em silêncio.
- **FR-873**: A falha de um envio MUST NOT impedir os demais, e o resultado do ato MUST dizer quantas
  comunicações foram enviadas e quantas falharam.
- **FR-874**: O sistema MUST oferecer emitir, num gesto, as comunicações pendentes do recorte — as das
  convocações vigentes sem desfecho e sem envio com sucesso —, com uma emissão por convocação, as
  mesmas garantias da `FR-872`, e a prévia das convocações alcançadas antes da confirmação.
- **FR-875**: Recorte cujo Edital não declarou a forma de comunicar a convocação MUST ter o ato em lote
  recusado antes da confirmação, com a Retificação apontada: convocar ali produziria convocações que
  nunca poderiam ser comunicadas, porque cada uma cita a versão do dia.
- **FR-876**: Quando o Edital comunica por publicação, o sistema MUST continuar sem publicar no site
  do certame; o ato de convocar MUST deixar as convocações com o prazo não iniciado, e o gesto da
  `FR-874` MUST exigir uma referência única de onde e quando a lista foi publicada, gravada em cada
  comunicação, da qual o prazo corre (`FR-288`).

### O não atendimento em lote

- **FR-877**: O sistema MUST permitir registrar, num único gesto confirmado, o desfecho de **não
  atendimento à convocação** de todas as convocações vigentes do recorte com o vencimento decorrido e
  sem desfecho, gravando **um desfecho por convocação**, cada um com autor, instante, fundamento e o
  seu efeito na ocupação (`DP-16`, B).
- **FR-878**: O alcance do gesto MUST ser exatamente o conjunto das convocações no estado *vencimento
  decorrido*; convocação com prazo em curso, com prazo não iniciado, ou sem vencimento MUST ficar de
  fora, e a prévia MUST dizer quantas ficaram e por quê.
- **FR-879**: Antes da confirmação, a tela MUST declarar cada convocação alcançada — pessoa, envio,
  vencimento — e o fundamento derivado; a confirmação MUST carregar a identidade do alcance, e a
  divergência MUST recusar o gesto sem gravar nada (`FR-863`).
- **FR-880**: Cada desfecho do gesto MUST ser indistinguível, em forma e em garantia, do registrado um a
  um: mesma tabela, mesmas recusas, mesmo efeito, e uma linha própria na trilha. A trilha MUST permitir
  reconstruir quais desfechos nasceram do mesmo gesto.
- **FR-881**: Aceite, indeferimento, regularização, desistência expressa, reclassificação e cancelamento
  por inércia MUST continuar individuais, com fundamento informado por quem registra: são decisão sobre
  uma pessoa.

### A apuração seguinte

- **FR-882**: Quando a única causa de obsolescência da apuração vigente de um recorte é um desfecho de
  convocação, a convocação seguinte MUST NOT exigir que alguém emita a apuração à mão.
- **FR-883**: O número de vagas que motiva cada convocação MUST continuar reconstruível a partir de
  atos append-only com autor, e a `FR-266` MUST continuar valendo: convocar sobre número que o sistema
  sabe estar para trás é recusado.
- **FR-884**: Obsolescência por qualquer outra causa — ordem sucedida, corte obsoleto, quadro
  retificado, movimento de vaga — MUST continuar exigindo o ato de hoje, com a causa nomeada.
- **FR-885**: Quando a conta seguinte moveria vaga entre recortes pela reversão que o Edital declarou, o
  desfecho MUST NOT produzir a apuração seguinte, e a tela do ato MUST dizer que ela, com o movimento,
  é emitida na ocupação (`FR-270`).

### O que vale para todos

- **FR-886**: Nenhum gesto desta feature MUST alterar ou excluir registro: tudo o que nasce é
  append-only, e corrigir continua sendo suceder, pessoa a pessoa, com motivo (`FR-272`).
- **FR-887**: Os gestos desta feature MUST exigir a mesma permissão e a mesma verificação de escopo que
  a convocação e o desfecho individuais já exigem, e MUST NOT criar autoridade nova.
- **FR-888**: A leitura do recorte, a prévia e o ato MUST ter custo de consulta que não cresce com o
  número de pessoas alcançadas, fora a gravação de cada registro (`SC-088`, `SC-090`).
- **FR-889**: O cadastro de reserva sem vagas imediatas MUST continuar fora: nenhum gesto desta
  feature produz déficit, e a recusa `sem_deficit` continua valendo (`DP-05`).

### A tela

- **UX-100** — **O alcance vem antes do botão.** A prévia lista as pessoas, na ordem, com a contagem
  por extenso (*"5 pessoas serão convocadas"*), e o botão repete o número (*"Convocar as 5"*). Nenhum
  gesto desta feature tem botão sem número.
- **UX-101** — **Cada valor derivado diz de onde veio.** Espécie, vencimento, fundamento e forma de
  comunicação aparecem com a origem ao lado — *"da posição na fila"*, *"do Edital, Perfil X"* —, e
  nunca como campo pré-preenchido que parece escolha.
- **UX-102** — **Quem fica de fora é nomeado.** Quando o gesto para antes do fim da fila, ou quando uma
  convocação fica fora do não atendimento, a tela diz quem e a razão, nas palavras da recusa que a
  pessoa receberia.
- **UX-103** — **O resultado conta o que aconteceu.** Depois do gesto, a tela diz quantas convocações
  nasceram, quantas comunicações saíram e quantas falharam, e quantos desfechos foram registrados — e
  continua sem dizer *"recebido"*, *"lido"* nem *"entregue"* (`UX-039`).
- **UX-104** — **A recusa por alcance mudado mostra o alcance novo.** Nunca devolve a pessoa a uma
  tela vazia.

### Key Entities

- **Convocação** (existente, `019`): o ato que chama uma pessoa. Continua um registro por pessoa. O
  gesto em lote não cria entidade de lote: a trilha é que reconstrói o que nasceu junto.
- **Comunicação emitida** (existente): o envio de cada convocação, uma por tentativa.
- **Desfecho da convocação** (existente): um por convocação; o de não atendimento em lote é igual ao
  individual.
- **Apuração de ocupação** (existente, `016`): o ato que diz quantas vagas faltam. A seguinte é
  emitida pelo próprio ato de desfecho, com o autor dele, quando a única causa de obsolescência é o
  desfecho e a conta não move vaga ([research](research.md), `D-005`).
- **Prévia do alcance** (nova, sem persistência): o que o gesto alcançaria agora, com a identidade que
  a confirmação carrega.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-320**: Num recorte com 40 titulares habilitados e apuração vigente, convocar e comunicar todos
  custa **uma confirmação**, contra 80 formulários hoje; num Edital de 7 Perfis × 3 recortes, 21
  confirmações para os 280 titulares do 28/2026.
- **SC-321**: Nenhum campo é digitado por pessoa no gesto em lote: espécie, fundamento e forma saem
  derivados, e o vencimento é informado **uma vez por ato**. Na chamada individual do suplente, o único
  campo é o vencimento.
- **SC-322**: Registrar o não atendimento de N convocações vencidas custa uma confirmação, e produz N
  desfechos, N efeitos e N linhas de trilha, todos com o mesmo autor.
- **SC-323**: Entre um desfecho e a convocação seguinte do mesmo recorte, quando nada além do desfecho
  mudou, o número de visitas obrigatórias à tela da ocupação é **zero**.
- **SC-324**: 100% das convocações e desfechos gravados pelos gestos em lote têm autor, instante,
  fundamento não vazio e proveniência completa — a mesma cobertura da chamada individual.
- **SC-325**: Nenhum ato em lote é gravado sobre alcance diferente do que a prévia declarou: em 100% das
  divergências provocadas nos testes, a confirmação é recusada e nada é gravado.
- **SC-326**: A prévia e o ato de um recorte de 85 pessoas usam o mesmo número de consultas de leitura
  que os de um recorte de 5.
- **SC-327**: No 28/2026 estimado, a convocação passa de 460–1.270 formulários para ~21 gestos de
  titulares, mais **um** formulário por suplente chamado (40–85, contra 80–255 hoje) e um por desfecho
  que é decisão sobre uma pessoa; o não atendimento dos vencidos, um gesto por rodada.

---

## Assumptions

### D-001 — O gesto é o começo da fila, e nunca a fila filtrada

O ato em lote convoca, na ordem, até o primeiro que não é titular, e para ali. Só titulares, por
decisão do usuário na clarificação de 28/09: chamar a vaga que vagou é escolha de quando chamar, e
continua sendo um ato por pessoa. A alternativa —
convocar todos os que cabem, pulando quem não cabe — faria o sistema decidir precedência, que a
`FR-267` só admite com fundamento registrado por uma pessoa. Parar é o único comportamento que não
esconde decisão.

### D-002 — Sem forma declarada, o ato em lote não acontece

A convocação cita a versão do Edital vigente no dia, e a forma de comunicar é lida dela. Convocar num
Edital sem forma declarada produz convocações que nenhuma Retificação posterior torna comunicáveis. Hoje
isso é possível um a um, e se descobre na hora de comunicar (anexo D, P1.3); o gesto que alcança 40
pessoas não pode repetir o defeito 40 vezes. A chamada individual continua como hoje.

### D-003 — O fundamento é derivado, com complemento

O fundamento da convocação é a norma e os atos que a sustentam, e o sistema os conhece. O *"no
interesse da Administração"* do 77/2026 cabe no complemento. O texto gravado é o que a prévia mostrou,
e nunca uma reescrita posterior.

### D-004 — A espécie informada que diverge é recusada

Até hoje a espécie era escolha livre, e nada impedia chamar um suplente *"para vaga inicial"*. A
espécie é consequência da posição, e escolhê-la errado grava um ato append-only com um fato falso. A
recusa alcança a API e o formulário forjado, e não só a tela, que deixa de perguntar.

### Outras premissas

- **A unidade é o recorte.** Um gesto por marco, que processe os N recortes, é da `049`, que declara a
  convocação fora do seu escopo; juntar as duas é trabalho de depois das duas.
- **O `callRules` continua sem consumidor.** A reavaliação mandou decidi-lo aqui. Ele é opaco, sem
  esquema e sem valor na amostra, e a tela da composição já não o pede — só a API o aceita. Esta
  feature não o consome, porque a ordem de chamada que ele descreveria entre Modalidades é a do
  cadastro de reserva (P-1), que continua fora pela `DP-05`. O campo não é apagado: os Editais
  publicados o guardam.
- **A revisão da `FR-084` da `010`** continua sendo o que autoriza a mensagem individual; esta feature
  não acrescenta situação de envio, só muda quem a dispara.
- **O portal do candidato não muda.** O convocado vê a convocação como vê hoje.

---

## Out of Scope

- Convocar vários recortes num gesto (`049`, depois).
- Cadastro de reserva, validade do Edital e ordem de chamada entre Modalidades (`DP-05`).
- Qualquer desfecho em lote além do não atendimento (`DP-16`).
- Cálculo de prazo em dias úteis e calendário de feriados (`FR-269`).
- Publicar a convocação no site do certame.
- Documento público da chamada (`DP-15`).
