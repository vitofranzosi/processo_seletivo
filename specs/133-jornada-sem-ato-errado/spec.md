# Feature Specification: A jornada não aponta o ato errado

**Feature Branch**: `claude/133-jornada-sem-ato-errado`, sobre a `main` em `da566ff2`

**Created**: 2026-11-07

**Status**: Implementada e mergeada (#432). *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Draft, para revisão antes do plano. **Uma regra de domínio nova**: a recusa de apurar
ocupação e de convocar num marco intermediário, decidida pelo usuário em 07/11/2026 (R1). O resto
corrige apresentação. Não há migration, tabela, coluna, permissão nem estado persistido novo.

**Input**: *"A jornada não aponta o ato errado: correções da derivação do andamento (CV-01 a CV-04) e
da frase do corte fixo (CV-10) do estudo de convergência UX de 07/11/2026. R1 decidido: apuração e
convocação recusadas no comando em marco intermediário. R2 decidido: o corte com prazo recursal aberto
é recomendação de aguardar, com a consequência explícita, e continua emissível. Preservar os atos e os
PDFs já publicados."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil quinhentos e trinta a quatro mil quinhentos e setenta e nove;
> - os critérios de mil quatrocentos e vinte a mil quatrocentos e trinta e nove.
>
> Os números não usados ficam livres. O teto foi medido em 07/11/2026 nas `specs/` de todas as
> worktrees desta máquina: o requisito quatro mil quinhentos e dezesseis e o critério mil
> quatrocentos e sete, ambos da `132`, e o UX-304 da `131`. A folga é de propósito. **Nenhum `UX-` é
> aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-4069 da `127`"). Decisão de outra feature, pelo assunto e pela feature.
>
> **Origem.** O
> [estudo de convergência UX de 07/11/2026](../../doc/estudo-convergencia-ux-2026-11-07/README.md)
> (PR #431), achados CV-01, CV-02, CV-03, CV-04 e CV-10, e as decisões R1, R2 e R4 do usuário, de
> 07/11/2026. As decisões R3 (explicar a posição ao candidato), a prévia com notas reais e a Revisão
> como plano de execução ficam para entregas seguintes.

## Por que esta feature existe

Desde a `127`, o GPS diz o que falta e de quem é: "O que fazer agora", o "Andamento da seleção" e o
"Próximo nesta lista". O estudo de 07/11 reproduziu do zero o Edital 900/2026 fictício: quatro Etapas,
dois marcos e três listas. Na classificação com mais de um marco, essa orientação **aponta o ato
errado** em quatro pontos.

1. **Ela manda apurar e convocar o marco intermediário** (CV-01). Em 29/12, a primeira providência
   da presidência é "Apurar a ocupação" da *Classificação para a entrevista*, e não "Convocar
   titulares" da *Classificação final*. Com as seis vagas já ocupadas por aceite, a providência
   continua lá.

   Numa cópia descartável do banco, o comando de apuração **aceitou** o ato. O cartão passou então a
   pedir "Convocar 4 titulares" desse marco, e o comando de convocação aceitou chamar, para vaga,
   duas pessoas que não poderiam ser chamadas:

   - a que já tinha desistido no marco final;
   - a que ficou em 7º na classificação final, fora das vagas.

   A comunicação ao candidato sai no ato da convocação.
2. **Ela sugere o corte com o prazo de recurso aberto** (CV-02). Logo depois da ordem, e no mesmo
   cartão em que a definitiva "aguarda o prazo recursal… até 12/12", a providência da presidência é
   "Emitir o corte".

   Emitido assim, o corte ficou obsoleto com o recurso deferido de 13/12. A Etapa governada ficou
   impedida, e a sucessão exigiu motivo.
3. **Depois de uma desistência, ela esconde a próxima da fila** (CV-03). A ampla fica com 1 vaga a
   ocupar, e a tela da convocação aponta a próxima da fila. O cartão diz só "Aguarda: resposta de 1
   convocação".

   A convocação em aberto é a de um **titular**, que já conta como ocupado. A conta a desconta de
   novo.
4. **Ela oferece a quem publica uma definitiva que o comando recusa** (CV-04). Depois do recurso
   deferido, a ordem fica obsoleta, mas a publicação definitiva continua *Pendente*.

E uma frase do Edital diz uma regra diferente da que o motor aplica (CV-10). O corte de alvo fixo
publica "Passam para a Etapa 'Entrevista' os 8 (oito) primeiros classificados". O motor aplica 8
**em cada lista de concorrência**. No caso, 12 pessoas foram à Entrevista, e o teto era 24.

**Nenhum dos quatro defeitos é de regra de cálculo.** A ordem, o corte, a ocupação e a fila estão
certos. O que erra é a orientação que lê esses resultados. A exceção é a CV-01: lá o domínio também
aceita um ato sem sentido, e o usuário decidiu recusá-lo no comando (R1). É a mesma forma da `128`:
a porta de gravação recusa, e a tela prevê a recusa.

### O que foi conferido nas specs vigentes

- **A `016` apura "por recorte do ato de ordenação (Perfil, marco e lista)"** (a FR-239 da `016`), em
  qualquer marco. Nenhuma spec distingue o marco que decide quem vai a uma Etapa do marco que decide
  as vagas.
- **A `040` registrou a falta dessa definição** (a lacuna G-012 dela): "não há definição inequívoca de
  'classificação final'". O "marco terminal" do corte, sem Etapa governada, não é universal, porque
  há marco sem regra de corte. Esta spec **não** define "classificação final". Ela define o seu
  oposto estreito, o **marco intermediário**, só pelo que é inequívoco no conteúdo publicado.
- **A `127` fez a apuração esperar a Etapa governada** (a decisão sobre a apuração e a Etapa
  governada, na `127`). O caso que ela tinha em mente é o sorteio seguido de uma Etapa de
  habilitação, sem marco depois. Esse caso continua: lá a apuração é legítima, e esta spec não o
  alcança.
- **Convocar é ato de vaga, e não de Etapa.** O
  [registro de 09/10](../../doc/registro-convocacao-para-etapas-2026-10-09.md) diz que "convocar para a
  Etapa não é ato". Por isso a convocação num marco intermediário nunca chama ninguém para a Etapa
  seguinte: chama para uma vaga que esse marco não decide.
- **A Etapa governada pelo corte e as Etapas que um marco enumera são não retificáveis** depois da
  publicação (`editais/domain/mutabilidade.py`). Uma definição que só as lê é a mesma durante toda a
  vida do Edital, com ou sem Retificação.

### O que esta spec cobre, e o que fica fora

Cobre:

1. **A definição de marco intermediário**, e a recusa, no comando, de apurar, mover ou acrescentar
   vaga e convocar nele (CV-01, R1).
2. **A derivação do andamento** nos quatro pontos, com a previsão nas telas da ocupação e da
   convocação (CV-01 a CV-04).
3. **A consequência do corte antes do fim do prazo recursal**, como recomendação, sem recusa (CV-02,
   R2).
4. **A frase do corte de alvo fixo** no Edital e na Revisão (CV-10).

Fica fora, de propósito:

- **Explicar a posição, a progressão e quem ocupa** nas telas dos atos: é a Entrega 2 do estudo.
- **A Revisão como plano de execução e a prévia com notas reais**: Entregas 3 e 4.
- **O alerta de vagas do simulador** num marco intermediário (CV-15): é da mesma raiz, mas a prévia
  é de composição, e entra com a Entrega 3.
- **A espécie "fixo no total"** do corte (a decisão G1 do estudo de 07/11): a frase passa a dizer o que
  o motor faz, e não muda o que ele faz.
- **O que "ocupada" significa** (G6 e Q8): continua como está.

## Clarifications

### Session 2026-11-07 (decisões do usuário que abrem a spec)

- R1: o marco intermediário deve ser protegido também no comando, ou basta a derivação? → **No
  comando.** Corrigir só o cartão deixaria o ato acessível por outros caminhos.
- R2: o corte com prazo recursal aberto é recomendação ou impedimento? → **Recomendação.** A tela
  orienta a aguardar e explica a consequência antes da confirmação, e o corte continua emissível.
- R4: abrir a spec antes do teste com pessoas? → **Sim.** São defeitos com evidência reproduzida.

### Session 2026-11-08

- Q: O marco **sem** corte que governe Etapa, seguido de outro marco, também é intermediário? → A:
  **Não.** Só o marco cujo corte governa uma Etapa que outro marco do Perfil enumera (D-001). A
  definição não se amplia sem caso conhecido e sem o acervo conferido.
- Q: A correção de uma convocação já existente num marco intermediário continua permitida? → A:
  **Não.** A correção cria uma convocação nova, com comunicação: é começar um ato. Encerrar a chamada
  existente continua possível pelo desfecho e pela conferência (FR-4534, FR-4535).
- Q: A espera recomendada do corte vale também para o marco por sorteio? (levantada pela revisão
  do PR #432) → A: **Sim.** A FR-4541 abrange todo marco com prazo recursal, e a recomendação
  continua permitindo emitir o corte no mesmo dia. O rito do Edital 35 (publicar a preliminar e
  cortar no mesmo dia), por si só, não justifica uma exceção (D-006).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O marco intermediário não apura nem convoca (Priority: P1)

A presidência conduz um Perfil com dois marcos:

- a *Classificação para a entrevista*, cujo corte decide quem faz a Entrevista;
- a *Classificação final*, que lê a Entrevista e decide as vagas.

Depois dos cortes e da apuração do marco final, a presidência abre o Edital. "O que fazer agora"
pede as convocações do marco final. O marco intermediário aparece como **Não se aplica**: "decide
quem vai à Entrevista; as vagas são da Classificação final". Se alguém abrir a ocupação ou a
convocação do marco intermediário, por link antigo ou pela URL, a tela diz o mesmo e não oferece
nenhum ato. O comando, chamado de qualquer jeito, recusa sem gravar nada e sem comunicar ninguém.

**Why this priority**: é o único ponto em que a orientação de hoje leva a um ato irreversível com
efeito externo: uma convocação, com comunicação, de quem desistiu ou ficou fora das vagas.

**Independent Test**: no Edital 900 reproduzido até a apuração do marco final, conferir as
providências e tentar apurar e convocar o marco intermediário pelo comando e pela tela.

**Acceptance Scenarios**:

1. **Given** o Edital 900 com as ordens, os cortes e a apuração do marco final emitidos, **When** a
   presidência abre o detalhe, **Then** as providências são "Convocar 4 titulares" (ampla), "Convocar
   1 titular" (PCD) e "Convocar 1 titular" (PPI), todas do marco final. Nenhuma providência é do
   marco intermediário.
2. **Given** o mesmo estado, **When** o "Andamento da seleção" é aberto, **Then** a apuração e a
   convocação do marco intermediário aparecem como *Não se aplica*, com a nota, e não entram na
   contagem "apuração N de M".
3. **Given** o mesmo estado, **When** o comando de apuração é chamado para o marco intermediário, em
   qualquer lista, **Then** ele recusa com código próprio e frase simples. Nenhuma apuração, movimento
   de vaga, acréscimo, faixa ou evento de trilha de emissão é gravado.
4. **Given** o mesmo estado, **When** o comando de convocação é chamado para o marco intermediário,
   individual ou em lote, para titular ou para a vaga que vagou, **Then** ele recusa, e nenhuma
   convocação nem comunicação é gravada ou enviada.
5. **Given** o Edital 900 com as seis vagas ocupadas por aceite, **When** a presidência abre o
   detalhe, **Then** nada fica em aberto por causa do marco intermediário.
6. **Given** um Perfil com um marco por sorteio cujo corte governa uma Etapa de habilitação que
   **nenhum** outro marco enumera, **When** a presidência apura e convoca esse marco, **Then** tudo
   continua como hoje: ele **não** é intermediário.

---

### User Story 2 — O corte espera o prazo recursal, como recomendação (Priority: P2)

A presidência emite a ordem do marco 1, e quem publica divulga a preliminar. O prazo recursal corre
até 12/12. O cartão diz que o corte **aguarda o prazo**, com a marca de recomendação, e por quê: o
corte decide quem vai à Entrevista, e um recurso deferido até 12/12 o tornaria obsoleto, com
sucessão motivada na trilha.

Se a presidência abrir a tela do corte mesmo assim, ela lê a mesma consequência **antes** de
confirmar, e pode emitir.

**Why this priority**: o ato errado aqui é reversível só por sucessão, sem efeito externo. Mas é o
momento mais frequente da classificação, e a orientação de hoje o contradiz no mesmo cartão.

**Independent Test**: no Edital 900 com a preliminar do marco 1 publicada, em 10/12, conferir o
cartão, o "Próximo nesta lista" depois da ordem e a tela do corte. Depois, emitir o corte e confirmar
que o comando aceita.

**Acceptance Scenarios**:

1. **Given** a ordem do marco 1 emitida e ainda não divulgada, **When** a presidência emite a ordem,
   **Then** o "Próximo nesta lista" não diz "Emitir o corte". O primeiro passo da lista é divulgar o
   resultado, de quem publica, e o corte aparece como aguardando.
2. **Given** a preliminar publicada e o prazo recursal aberto até 12/12, **When** a presidência abre
   o detalhe, **Then** o corte de cada lista aparece em espera, com a data, a marca de recomendação e a
   consequência em uma frase, e **não** como "SUA" a praticar.
3. **Given** o mesmo estado, **When** a presidência abre a tela do corte, **Then** a consequência
   aparece antes da confirmação, e o botão de emitir continua disponível.
4. **Given** o mesmo estado, **When** a presidência emite o corte, **Then** o comando aceita, como
   hoje.
5. **Given** o prazo encerrado, sem recurso pendente e com a definitiva publicada, **When** a
   presidência abre o detalhe, **Then** o corte é *Pendente* e "SUA", como hoje.
6. **Given** um recurso pendente de decisão no marco, depois do fim do prazo, **When** a presidência
   abre o detalhe, **Then** o corte continua em espera, até a decisão.

---

### User Story 3 — A próxima da fila aparece quando há vaga a ocupar (Priority: P2)

Bruno, titular da ampla, desiste. Rafael, outro titular, está com documento pendente. A ampla fica
com 3 de 4 ocupadas, e a fila tem Diana. O cartão e o "Próximo nesta lista" dizem "Chamar a próxima da
fila", e a resposta pendente de Rafael aparece em espera, à parte. É a mesma conclusão que a tela da
convocação já mostra.

**Why this priority**: deixa uma vaga parada enquanto a presidência espera um prazo que não é o da
vaga. Não grava nada errado, mas contradiz a tela do ato.

**Independent Test**: no Edital 900 em 05/01, com a desistência de Bruno registrada e Rafael pendente,
comparar o cartão com a tela da convocação.

**Acceptance Scenarios**:

1. **Given** 1 vaga a ocupar na ampla, uma convocação em aberto **de titular** e a próxima da fila
   disponível, **When** a presidência abre o detalhe, **Then** "Chamar a próxima da fila" é providência
   dela, e a resposta do titular aparece em espera.
2. **Given** 1 vaga a ocupar e uma convocação em aberto **para a vaga que vagou**, sem resposta,
   **When** a presidência abre o detalhe, **Then** "Chamar a próxima da fila" **não** aparece, e a
   resposta pendente aparece em espera. É o comportamento de hoje, que continua.
3. **Given** a tela da convocação e o cartão no mesmo instante, **Then** os dois apontam a mesma
   próxima ação para a lista.

---

### User Story 4 — Ninguém é mandado publicar o que o comando recusa (Priority: P3)

Depois do recurso deferido, a ordem da ampla fica obsoleta. Para quem publica, o resultado definitivo
da ampla aparece como *Depois*, com a razão: "a ordem vigente está para trás; o ato sucessor vem antes
de divulgar". Vale o mesmo quando quem fica para trás é o corte de que o resultado depende.

**Why this priority**: é uma tentativa frustrada, com recusa clara no comando, e sem ato errado.

**Independent Test**: no Edital 900 em 13/12, com o recurso deferido e antes da ordem sucessora,
conferir as providências de quem publica e tentar publicar a definitiva da ampla.

**Acceptance Scenarios**:

1. **Given** a preliminar da ampla publicada e a ordem da ampla obsoleta, **When** quem publica abre
   o detalhe, **Then** o definitivo da ampla não é *Pendente*. Ele aparece como *Depois*, com a razão.
2. **Given** o corte que o resultado reflete obsoleto, **When** quem publica abre o detalhe, **Then**
   o definitivo aparece *Impedido*, com a razão do corte e quem resolve, e não *Pendente*.
3. **Given** a ordem sucessora emitida, **When** quem publica abre o detalhe, **Then** o definitivo
   volta a ser *Pendente*, como hoje.

---

### User Story 5 — O Edital diz "de cada lista" (Priority: P2)

Quem elabora declara um corte de alvo fixo 8 num Perfil com ampla, PCD e PPI. A Revisão e o documento
do Edital passam a dizer: "Passam para a Etapa 'Entrevista' os 8 (oito) primeiros classificados de
cada lista de concorrência".

**Why this priority**: a frase vai ao documento oficial (`pdf.py`) e diz hoje uma regra diferente da
executada. Corrigir não muda o cálculo.

**Independent Test**: compor o marco 1 do Edital 900 e ler a frase na Revisão e no PDF da prévia de
publicação. Conferir que um Edital já publicado continua com o documento que publicou.

**Acceptance Scenarios**:

1. **Given** um corte de alvo fixo N num Perfil que declara modalidade reservada, **Then** a frase
   diz "os N (por extenso) primeiros classificados de cada lista de concorrência", na Revisão e no
   documento.
2. **Given** um corte de alvo fixo num Perfil só com a ampla, **Then** a frase continua como hoje.
3. **Given** um Edital publicado antes desta feature, **Then** o documento dele é o mesmo, byte a
   byte, e nenhum ato é regenerado.

---

### Edge Cases

- **O marco intermediário com apuração ou convocação já gravadas antes desta feature.** Elas continuam
  vigentes, válidas e legíveis, e a trilha não muda. A recusa vale para **atos novos**. Os atos que
  **encerram** uma convocação já existente continuam permitidos (desfecho, conferência de documento,
  comunicação pendente), para que ninguém fique preso numa chamada sem saída. A **correção** da
  convocação existente é recusada: ela cria uma convocação nova (decidido em 08/11). A derivação mostra o
  que existe, sem chamar de erro, e não pede ato novo.
- **O marco intermediário por sorteio.** O sorteio cujo corte governa uma Etapa que outro marco lê é
  intermediário pela mesma regra. A definição não olha a forma de ordenar.
- **Mais de dois marcos em cadeia.** Cada marco cuja Etapa governada é lida por **algum** marco do
  mesmo Perfil é intermediário. O último, que nenhum outro alimenta, não é.
- **Marco sem regra de corte, ou com corte que não governa Etapa, seguido de outro marco.** **Não** é
  intermediário por esta definição (D-001, confirmada em 08/11). Ele continua apurando e convocando
  como hoje.
- **A faixa seguinte do corte num marco intermediário.** Ela é ato de corte, e não de ocupação: amplia
  quem vai à Etapa seguinte, e continua permitida. O que se recusa é a faixa **causada por déficit de
  ocupação**, que só existe com apuração.
- **O recurso decidido, mas a definitiva ainda não publicada, com o prazo encerrado.** O corte deixa de
  esperar quando nada mais pode mudar a ordem: prazo encerrado e nenhum recurso, reavaliação ou
  providência pendente no marco. A publicação da definitiva **não** é condição, porque o domínio não a
  exige para cortar, e a recomendação não inventa uma regra que o domínio não tem.
- **Marco sem prazo recursal declarado.** Não há o que esperar, e o corte é *Pendente* assim que a
  ordem é vigente, como hoje.
- **A ordem emitida e ainda não divulgada, num marco com prazo recursal.** O prazo nem começou. O corte
  aparece em espera, com a razão "o prazo de recurso começa com a divulgação". A providência da
  lista é divulgar, e é de quem publica.
- **Uma Retificação de Edital anterior a esta feature.** O documento da Retificação é gerado agora, e
  terá a frase nova. A frase descreve a **mesma** regra, e a comparação de alterações da Retificação
  é sobre o conteúdo, e não sobre a prosa. Ela **não** pode apontar alteração do corte só por causa da
  redação (SC-1426).

## Requirements *(mandatory)*

### Functional Requirements

**O marco intermediário (CV-01, R1)**

- **FR-4530**: Um marco MUST ser **intermediário** num Perfil quando a regra de corte dele governa uma
  Etapa **e** essa Etapa está entre as Etapas que outro marco do mesmo Perfil enumera. A definição
  MUST ler só o conteúdo vigente do Edital, e só campos não retificáveis: a Etapa governada e as
  Etapas enumeradas.
- **FR-4531**: A definição MUST ser uma regra só, de domínio, usada pelo comando, pela previsão nas
  telas e pela derivação do andamento. Nenhuma das três MUST reescrevê-la.
- **FR-4532**: O comando de apuração da ocupação MUST recusar a emissão, inicial ou sucessora, num
  recorte de marco intermediário.
- **FR-4533**: Os comandos que movem vaga, acrescentam vaga ou causam faixa por déficit de ocupação
  MUST recusar o marco intermediário pela mesma regra.
- **FR-4534**: O comando de convocação MUST recusar o marco intermediário em toda espécie (titular,
  vaga que vagou, regularização) e em toda forma (individual, em lote, correção da convocação).
- **FR-4535**: Os atos que encerram uma convocação **já existente** num marco intermediário MUST
  continuar permitidos: desfecho, conferência de documento e comunicação pendente.
- **FR-4536**: A recusa MUST acontecer dentro da trava do Processo, antes de qualquer gravação. Ela
  MUST NOT gravar ato, movimento, faixa, convocação, comunicação, evento de trilha de emissão nem
  chave de idempotência que a faça parecer atendida.
- **FR-4537**: A recusa MUST ter código próprio e uma frase em linguagem simples, sem identificador
  interno. A frase MUST nomear o marco e o que ele decide, e apontar o marco onde se apura. Exemplo:
  "A *Classificação para a entrevista* decide quem vai à Entrevista; as vagas são apuradas na
  *Classificação final*".
- **FR-4538**: As telas da ocupação e da convocação de um marco intermediário MUST prever a recusa:
  não oferecem formulário de apuração, sucessão, convocação ou chamada, dizem o motivo com a mesma
  frase e levam ao marco onde se apura. O que já existe continua legível.
- **FR-4539**: Na derivação do andamento (`127`), a apuração e a convocação de um marco intermediário
  MUST ser *Não se aplica*, com a nota do que o marco decide. Elas MUST NOT entrar nas providências
  nem na contagem de apurações do resumo do Perfil. A publicação do resultado dele continua como hoje.
- **FR-4540**: As apurações e convocações já gravadas em marco intermediário MUST continuar vigentes,
  válidas e legíveis. Nenhuma migration nem rotina as altera ou exclui.

**O corte com prazo recursal aberto (CV-02, R2)**

- **FR-4541**: Na derivação do andamento, o corte de uma lista MUST ficar em espera, e não *Pendente*,
  enquanto o marco declarar prazo recursal e qualquer destes ocorrer:
  - o resultado da lista ainda não foi divulgado;
  - o prazo está aberto;
  - há recurso, reavaliação ou providência pendente que alcança o marco.
- **FR-4542**: A espera do corte MUST ser apresentada como **recomendação**, e não como impedimento.
  Ela traz uma marca que diga isso, a data até a qual se espera (quando houver) e a consequência em
  uma frase: o corte decide quem participa da Etapa seguinte, e um recurso deferido o tornaria
  obsoleto, com sucessão motivada.
- **FR-4543**: A espera do corte MUST NOT ser contada entre as providências "suas". O "Próximo nesta
  lista", depois da ordem, MUST apontar primeiro o ato que destrava a lista (divulgar, de quem publica)
  e mencionar o corte em espera.
- **FR-4544**: A tela do corte MUST mostrar a mesma consequência **antes** da confirmação, quando a
  regra da FR-4541 estiver em espera, e MUST continuar oferecendo a emissão.
- **FR-4545**: O comando de emissão do corte MUST NOT mudar: a recomendação não recusa.
- **FR-4546**: A espera do corte MUST sair da mesma aferição que decide se a definitiva pode ser
  publicada, e não de uma segunda leitura do prazo.

**A próxima da fila (CV-03)**

- **FR-4547**: Na derivação da convocação de uma lista, as vagas a ocupar **sem chamada** MUST
  descontar só as convocações em aberto cujo aceite ocuparia uma vaga ainda não contada como ocupada:
  as chamadas para a vaga que vagou e de regularização. As convocações em aberto de **titulares** MUST
  NOT ser descontadas, porque o titular já conta como ocupado.
- **FR-4548**: Com vaga a ocupar sem chamada e próxima da fila disponível, "Chamar a próxima da fila"
  MUST ser providência de quem conduz, e as respostas em aberto MUST continuar em espera, à parte.
- **FR-4549**: O cartão e a tela da convocação MUST apontar a mesma próxima ação para a lista, no mesmo
  instante.

**A publicação que o comando recusaria (CV-04)**

- **FR-4550**: Na derivação do resultado de uma lista, a publicação MUST ser *Depois*, com a razão,
  sempre que a ordem vigente estiver obsoleta, **também** quando já houver publicação preliminar.
- **FR-4551**: Quando o corte do marco, do qual o resultado depende, estiver obsoleto, a publicação
  MUST ser *Impedido* ou *Depois*, com a razão e quem resolve, e nunca *Pendente*. *Ajustada no plano
  (R-007 da pesquisa): a aferição da definitiva já devolve o impedimento do corte obsoleto, com a
  mesma frase da prévia de publicação.*
- **FR-4552**: A derivação MUST NOT dizer *Pendente* para uma publicação que o comando de publicação
  recusaria pelos mesmos motivos. É a mesma garantia que a `128` deu à ordem, agora para a divulgação.

**A frase do corte fixo (CV-10)**

- **FR-4553**: A frase do corte de alvo fixo MUST dizer "de cada lista de concorrência" quando o
  Perfil declara ao menos uma modalidade reservada, no documento do Edital e na Revisão, que usam a
  mesma frase.
- **FR-4554**: Num Perfil só com a ampla, a frase MUST continuar como hoje.
- **FR-4555**: Os documentos já publicados MUST NOT ser regenerados nem alterados. A frase nova vale
  para os documentos gerados depois desta feature.
- **FR-4556**: A comparação de alterações de uma Retificação MUST NOT apontar alteração do corte só
  pela mudança de redação.

**Coerência e regressão**

- **FR-4557**: Os quatro instantes do estudo (10/12, 13/12, 29/12 e 05/01 do Edital 900) MUST ter
  teste de regressão sobre a derivação, nas paradas equivalentes de uma versão reduzida do Edital 900
  (R-009 da pesquisa), com o resultado que a sonda do estudo conferiu. O Edital 900 completo é o da
  demonstração no navegador.
- **FR-4558**: Cada recusa nova MUST ter teste que chame o comando diretamente, sem passar pela tela,
  e confira que nada foi gravado nem comunicado.
- **FR-4559**: Os casos da `127` que hoje provam a apuração depois da Etapa governada, quando nenhum
  marco posterior a lê, MUST continuar passando sem mudança de expectativa.

### Key Entities

- **Marco intermediário**: não é entidade nem estado. É uma qualidade do marco, derivada do conteúdo
  vigente pela regra da FR-4530: a Etapa governada pelo corte dele é lida por outro marco do Perfil.
- **Espera recomendada do corte**: não é estado. É a apresentação da célula do corte enquanto a
  aferição da definitiva acusa espera ou o resultado não foi divulgado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1420**: Em **100%** das tentativas de apurar, mover ou acrescentar vaga, causar faixa por
  déficit ou convocar num marco intermediário, pelo comando ou pela tela, o pedido é recusado, e
  **zero** registros e **zero** comunicações são gravados.
- **SC-1421**: No Edital 900 (completo na demonstração, reduzido na suíte) em 29/12 e em 06/01, **zero** providências do marco intermediário
  aparecem para qualquer papel. Em 29/12, as três providências da presidência são as convocações do
  marco final.
- **SC-1422**: No Edital 900 em 10/12, **zero** providências "suas" de corte. O corte das três listas
  aparece em espera, com a data de 12/12 e a consequência, e o comando continua aceitando a emissão.
- **SC-1423**: No Edital 900 em 05/01, depois da desistência de Bruno, "Chamar a próxima da fila" é
  providência da presidência na ampla, e o cartão e a tela da convocação apontam a mesma ação.
- **SC-1424**: No Edital 900 em 13/12, **zero** publicações *Pendentes* que o comando recusaria.
- **SC-1425**: **100%** dos documentos de Editais publicados antes desta feature continuam
  byte a byte iguais.
- **SC-1426**: Uma Retificação de Edital com corte de alvo fixo, que não mexe no corte, **não** aponta
  alteração do corte.
- **SC-1427**: Os casos existentes da `127` e da `016` para marco sem sucessor que o leia passam sem
  mudança de expectativa. A suíte contra PostgreSQL fecha sem falha nova em relação à linha de base da
  branch.
- **SC-1428**: **Zero** migrations, tabelas, colunas, permissões ou estados persistidos novos.

## Assumptions

- O estudo de 07/11 (PR #431) é a evidência. Os bancos de fase e a sonda dele (`roteiro/sonda.py`)
  são o roteiro da demonstração no navegador.
- A recusa da FR-4532 a FR-4534 é **regra de domínio nova**, decidida pelo usuário (R1). Ela muda o
  que a `016` e a `019` aceitavam num recorte de marco intermediário. Nenhum requisito vigente
  **exige** apurar ou convocar nesse recorte. A FR-239 da `016` define **como** se apura por recorte,
  e não que todo recorte se apura.
- O marco sem corte que governe Etapa, seguido de outro marco, **não** é intermediário (decidido em
  08/11, *Clarifications*). Ampliar a definição seria decisão própria, com o acervo conferido.
- O texto exato das frases (recusa, espera, consequência) é do plano, em linguagem simples, sem
  identificador interno. As frases das maquetes A1 a A3 do estudo são o ponto de partida.
- A demonstração no navegador e `make lint check test-pg` fazem parte da verificação da entrega, como
  pedido.

## Compatibilidade com regras anteriores

| Regra | O que esta spec faz com ela |
|---|---|
| FR-239 da `016` (apurar por recorte) | Mantém. Restringe o recorte a marco não intermediário |
| Convocação por recorte, da `019` | Mantém para marco não intermediário. Recusa novos atos no intermediário e deixa encerrar os existentes |
| A apuração espera a Etapa governada (decisão da `127`) | Mantém para o marco que nenhum outro lê |
| FR-4069 e FR-4071 da `127` | A célula do corte ganha a espera recomendada, e a do resultado ganha *Depois* com a ordem ou o corte obsoletos |
| FR-4073 da `127` (convocação no andamento) | Corrige a conta das vagas sem chamada |
| FR-4090 da `127` ("Próximo nesta lista") | Mantém. Passa a ler as células corrigidas |
| FR-217 da `014` (corte imutável) | Intocada: a recomendação não altera nem recusa corte |
| A `128` (a previsão sai da regra do comando) | Mesma forma: regra única, previsão nas telas, recusa no comando |
| O documento publicado não se regenera | Intocado (FR-4555) |

## Achado fora do escopo (registro)

- A `051` diz que o segundo marco de um Perfil "nasce **sem** corte". O estudo de 07/11 observou o 2º
  marco nascer com o corte pelo quadro e "não governa Etapa" (diário C08 daquele estudo). Fica
  registrado para o usuário. Não é escopo desta spec.

## Decisões

### D-001 — O marco intermediário se define pela Etapa governada que outro marco lê

**Alternativas.**

- **(a)** Corte que governa uma Etapa enumerada por outro marco do Perfil. **Escolhida.**
- **(b)** Todo marco que não é o último do Perfil.
- **(c)** Todo marco cujo corte governa Etapa.

**Por que (a).** É a única que lê só campos não retificáveis e que separa os dois casos reais:

- no Edital 900, a Entrevista é governada pelo marco 1 e lida pelo marco 2, então o marco 1 é
  intermediário;
- no sorteio seguido de Etapa de habilitação, nenhum marco lê a Etapa, então o marco não é
  intermediário, e continua apurando.

A (b) depende da ordem de exibição, que não é norma. A (c) recusaria o caso do sorteio, que a `127`
trata como legítimo.

### D-002 — A recusa vale para atos novos; encerrar o que existe continua permitido

Recusar também o desfecho deixaria uma convocação já feita sem saída: a pessoa chamada não teria
desfecho registrável. O que se protege é o **começo** de um ato sem sentido, e não o fim de um que
já existe.

### D-003 — A espera do corte é recomendação, e lê a aferição da definitiva

É a decisão R2 do usuário. Ler a mesma aferição que decide a definitiva (janela aberta e recurso,
reavaliação ou providência pendente) evita uma segunda regra de prazo, que divergiria na primeira
mudança.

A publicação da definitiva **não** é condição para sair da espera. O domínio não a exige para cortar,
e uma recomendação mais estrita que o domínio ensinaria a ignorá-la.

### D-004 — Só o titular fica fora do desconto das vagas sem chamada

O titular conta como ocupado desde a apuração, pelo mapa de efeitos da convocação. A chamada em aberto
para a vaga que vagou, ou de regularização, ainda não conta: ela já responde pela vaga, e chamar outra
pessoa duplicaria a chamada. É a regra da tela da convocação, que a derivação passa a seguir.

### D-005 — A frase muda só onde o Perfil tem mais de uma lista

Num Perfil só com a ampla, "de cada lista" seria verdadeiro e estranho. A regra é a mesma, e a frase
só precisa do complemento quando existe mais de uma lista.

### D-006 — A espera vale também para o sorteio

Decisão do usuário de 08/11/2026, depois da revisão do PR #432. O marco por sorteio que declara
prazo recursal recebe a mesma espera recomendada do corte que o marco por pontuação. A ordem
sorteada também pode ser atacada por recurso, e um corte emitido antes da decisão teria a mesma
sucessão motivada. A emissão continua permitida no mesmo dia: quem segue o rito do Edital 35 vê a
recomendação e decide. Não há exceção por forma de ordem, e o teste
`test_o_sorteio_com_recurso_declarado_tambem_espera` prende a decisão.
