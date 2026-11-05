# Feature Specification: A correção da convocação pela gestão

**Feature Branch**: `claude/beautiful-einstein-dd75ba`, sobre a `main` em `015861c7`

**Created**: 2026-11-04

**Status**: Draft, **só documental**. Nenhum código, migration, rota ou tela foi alterado. As
decisões têm duas origens:

- **Do usuário, em 04/11/2026:** D-001 (spec própria, e não emenda à `050`) e as quatro respostas de
  *Clarifications*. Não se reabrem.
- **Propostas de desenho desta spec:** D-002 a D-009, **mantidas pelo usuário** na revisão do commit
  `4b2bd844` (04/11/2026).
- **Da revisão do commit `4b2bd844` (04/11/2026):** os ajustes da FR-3844, da FR-3848, da SC-1144 e
  da FR-3854, e duas ampliações que o plano exigiu, registradas como tal: a D-010 (a confirmação
  assina a prévia, FR-3857), que amplia a D-003, e o complemento da D-009 para o cartão que mudou no
  intervalo.

**Input**: o achado
[`doc/achado-correcao-da-convocacao-pela-gestao-2026-11-04.md`](../../doc/achado-correcao-da-convocacao-pela-gestao-2026-11-04.md),
mergeado no PR #376, seção *"Proposta de escopo e validação"*. O diagnóstico foi conferido de novo em
04/11/2026 sobre a `main` em `015861c7`, e continua valendo: nenhum formulário da gestão envia o
motivo da sucessão, a fila exclui quem tem chamada em aberto, e o cartão da chamada em aberto só
oferece *"Registrar desfecho"*. O PR #384 (implementação da `118`) foi **mergeado em 04/11/2026**
(`4de96c39`), e a validação no portal é feita sobre a jornada que ele entregou.

> **Faixa de identificadores.** Esta spec abre em **FR-3837** e **SC-1141**. O teto foi medido em
> 04/11/2026 em `specs/` de todas as branches locais e remotas (24) e de todas as worktrees desta
> máquina (20): o requisito funcional três mil oitocentos e trinta e seis, da branch do incremento 2
> da `119`, e o critério mil cento e quarenta, da branch do incremento 1 da `119`. A pasta `120` não
> existe em nenhuma delas, nem em PR aberto. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam
> em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-870 da `050`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número. A questão institucional `QI-7` é citada como está no documento de origem.

---

## Por que esta feature existe

**A `115` fez da correção por sucessão o único jeito de dar mais prazo, e a gestão não tem como
praticá-la.** A FR-3618 da `115` diz que dar mais prazo é corrigir a convocação, com motivo e
vencimento novo, por um mecanismo *"que já existe"*. A FR-3622 da `115` diz que essa correção reabre
juntos os documentos e o Requerimento de Matrícula. Os dois existem no domínio, e só nele:

- o comando de convocar, com motivo, sobre uma chamada em aberto, cria a sucessora com o vencimento
  novo e o mesmo número de chamada, e a lista e as apresentações continuam as da chamada;
- a view da gestão lê o motivo do formulário;
- **nenhum formulário o envia.** Os dois que chamam uma pessoa listam a fila, e quem tem chamada em
  aberto está fora dela por construção. O cartão da chamada em aberto oferece o desfecho, o
  indeferimento pelas pendências e o fundamento, e nada mais.

**Consequência operacional.** A comissão que precisa dar mais prazo a um convocado — porque a
mensagem saiu tarde, porque o documento pedido depende de outro órgão, porque o Edital foi
retificado — não tem caminho na tela. Ou registra um desfecho que não corresponde ao que aconteceu,
ou pede a alguém com acesso ao servidor que pratique o ato por fora. As duas saídas contrariam a
Constituição: a primeira grava um fato falso, e a segunda pratica ato do certame sem a interface que
o mostra antes e o registra depois. O usuário trata isto como prioridade operacional alta, antes da
homologação com processos reais.

**A FR-870 da `050` já exige o caminho.** Ela diz que a convocação individual continua para a
exceção, *"inclusive a sucessão"*, e que as derivações aparecem antes da confirmação. A `050`
entregou a precedência justificada e a chamada para regularizar, mas não a sucessão.

### O que esta spec cobre, e o que fica fora

**Cobre:**

- uma ação por cartão de chamada em aberto, *"Corrigir esta convocação"*, para quem pode convocar;
- o formulário com motivo obrigatório, vencimento novo e o complemento opcional do fundamento;
- a prévia das derivações e das consequências antes da confirmação, inclusive o que reabre no portal;
- a confirmação pelo comando que já existe, com a mesma autorização e o mesmo escopo, e com uma
  conferência a mais: a de que a convocação nomeada ainda é a que está em aberto;
- as recusas: as do formulário, as das guardas que o domínio já tem, e a limitação declarada quando
  o recorte não admite correção nenhuma;
- a verificação da gestão ao portal, no navegador.

**Fica fora:**

- **a redação própria da mensagem da sucessora** (*"A sua convocação foi corrigida…"*), que é decisão
  sobre a FR-290 da `019`, com parente em `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`;
  *(Decidida pelo usuário em 05/11/2026 e especificada na `121`, FR-3885 e FR-3890: a mensagem da sucessora comunicada diz que substitui a anterior, com a data do envio substituído e o prazo que ele informava, e sem o motivo.)*
- **o aviso de pendência (`QI-7`)**, que continua com a decisão institucional registrada na `118`;
- **correção em lote, prazo próprio por item e mudança na fila** — a fila continua sem quem tem
  chamada em aberto, e o lote continua sem sucessão (FR-861 da `050`);
- **papel, tabela, estado, desfecho ou mensagem novos**;
- **qualquer regra nova no portal**: o convocado lê a sucessora pelas regras da `115` e da `118`.

## Clarifications

### Session 2026-11-04

- Q: Emenda curta à `050` ou spec própria? → A: Spec própria, a `120`. A `050` está fechada, com
  matriz de rastreabilidade cobrada requisito a requisito, e o escopo cruza a `019`, a `050` e a
  `115` (D-001).
- Q: A chamada com vencimento decorrido e sem desfecho entra? → A: Sim. Ela continua em aberto, e é o
  caso típico de dar mais prazo (FR-3837).
- Q: A recusa por apuração superada basta como está? → A: Não. Preservar a guarda não demonstra que a
  jornada funciona: ela MUST aparecer como limitação explícita, com orientação compreensível para
  quem opera (FR-3839, D-005).
- Q: A validação no portal depende do PR #384? → A: Ele foi mergeado em 04/11/2026. A validação usa
  a jornada consolidada da `118`, e a reabertura é a da FR-3622 da `115`.

### Session 2026-11-04 (revisão do commit `4b2bd844`)

- Q: Com o prazo em curso, a prévia diz sempre "prazo estendido"? → A: Não. A própria spec admite
  antecipar. A prévia distingue estender, antecipar e manter o vencimento, pelo vencimento informado
  (FR-3844), e o resultado diz qual aconteceu (FR-3849).
- Q: "Uma comunicação" vale com a forma por publicação e com falha de envio? → A: O requisito é
  impedir duplicidade, e não garantir envio. O ato pode ficar aguardando publicação, ou com a
  comunicação falha; a repetição devolve esse mesmo resultado (FR-3848, SC-1144).
- Q: Registrar um defeito do portal dispensa demonstrar a User Story 2? → A: Não. A demonstração é
  condição de conclusão. Se um defeito a impedir, a conclusão fica bloqueada até ele ser resolvido,
  por decisão do usuário, sem que o defeito entre no escopo desta feature (FR-3854).
- Q: Identificar a convocação corrigida garante que espécie e fundamento gravados sejam os da
  prévia? → A: Não. A apuração seguinte, ou uma Retificação, pode mudar os dois no intervalo sem
  tocar na convocação. A confirmação passa a assinar a prévia (FR-3857, D-010).

## User Scenarios & Testing *(mandatory)*

Os atores são os da `050`: **quem conduz a convocação** (a presidência da comissão, ou quem tem a
base de gestão da comissão no Processo), o **membro alocado à conferência** (lê a condução, não
convoca), a **auditoria** (lê, não convoca) e o **convocado**, no portal.

### User Story 1 — A comissão dá mais prazo a uma chamada em aberto (Priority: P1)

A presidência abre a condução da convocação de um recorte. No cartão de uma chamada em aberto — com
o prazo em curso, com o vencimento decorrido ou ainda sem comunicação enviada —, ela abre *"Corrigir
esta convocação"*, declara o motivo, informa o vencimento novo e lê, antes do botão, o que o ato vai
fazer. Ela confirma. A chamada passa a ter a sucessora, com o vencimento novo, e a corrigida continua
legível no histórico com o motivo.

**Why this priority**: é o único caminho para dar mais prazo (FR-3618 da `115`), e hoje ele não
existe pela tela. Sem ele a comissão registra um desfecho falso ou pratica o ato por fora.

**Independent Test**: num recorte com apuração e ordem vigentes e uma chamada em aberto com
vencimento, corrigir pela tela e conferir a sucessora (vencimento novo, mesmo número de chamada,
motivo), o cartão, o histórico e a trilha.

**Acceptance Scenarios**:

1. **Given** uma chamada com o prazo em curso, **When** a presidência abre a ação no cartão,
   **Then** vê o motivo e o vencimento novo como campos obrigatórios, o complemento como opcional, e,
   antes do botão, a pessoa, o número da chamada, o vencimento atual, a espécie e o fundamento que a
   sucessora levará, a forma de comunicação do Perfil e o que continua da chamada.
2. **Given** o formulário preenchido, **When** ela confirma, **Then** nasce uma convocação que
   sucede a corrigida, com o vencimento novo e o mesmo número de chamada; a tela diz que a convocação
   foi corrigida, de que vencimento para qual, e o resultado da comunicação.
3. **Given** a chamada corrigida, **When** a presidência volta ao cartão, **Then** ele mostra o
   vencimento novo e a situação recalculada, e indica que a convocação foi corrigida, com o caminho
   para o histórico.
4. **Given** a chamada com o vencimento decorrido, **When** ela é corrigida com vencimento futuro,
   **Then** a chamada sai da lista do gesto do não atendimento dos vencidos e volta a *"Prazo em
   curso"* — ou a *"Sem comunicação enviada"*, até que a comunicação saia.
5. **Given** o histórico do recorte, **When** ele é aberto depois da correção, **Then** a corrigida
   aparece como sucedida, com o motivo, e a sucessora como vigente; depois de uma segunda correção,
   são três linhas, cada sucedida com o seu motivo.

---

### User Story 2 — O convocado vê o prazo novo e retoma o que o prazo fechava (Priority: P1)

O convocado tinha um documento pendente de complementação e o Requerimento de Matrícula por enviar
quando o prazo venceu, e o portal passou a recusar os dois com a mesma frase (FR-3622 da `115`).
Depois da correção, o portal mostra o prazo novo, e os dois reabrem juntos até ele.

**Why this priority**: é o efeito para o qual a correção existe. Sem ele, a ação da gestão seria só
um registro.

**Independent Test**: de ponta a ponta, no navegador: corrigir na gestão uma chamada vencida com um
documento pendente; no portal, como o convocado, ver o prazo novo, complementar o documento e
preencher e enviar o Requerimento.

**Acceptance Scenarios**:

1. **Given** uma chamada vencida, com um documento pendente e o Requerimento declarado na convocação
   não enviado, **When** a gestão a corrige com vencimento futuro, **Then** o portal mostra o prazo
   novo no formato único da `118`, e não mostra mais a recusa por prazo decorrido.
2. **Given** o portal depois da correção, **When** o convocado complementa o documento pendente,
   **Then** a complementação é aceita, entra na chamada como as demais, e a conferência anterior do
   item continua legível.
3. **Given** o portal depois da correção, **When** o convocado preenche e envia o Requerimento,
   **Then** o envio é aceito; o rascunho feito antes do vencimento antigo continua sendo o ponto de
   partida.
4. **Given** a sucessora, **When** o vencimento novo também decorre, **Then** documentos e
   Requerimento voltam a ser recusados juntos, com a mesma frase.
5. **Given** a gestão depois da correção, **When** ela abre os documentos da convocação, **Then** a
   lista, as apresentações e as conferências são as da chamada, e nenhuma se perdeu.

---

### User Story 3 — A correção que não pode acontecer diz por quê e o que fazer (Priority: P1)

Algumas correções não podem acontecer: porque falta o motivo, porque o vencimento já passou, porque a
chamada teve desfecho ou já foi corrigida por outra pessoa, porque quem tenta não pode convocar, ou
porque o recorte está num estado em que nenhuma convocação nasce — a apuração foi superada, a ordem
foi sucedida. Em todos os casos, nada é gravado, e quem opera sabe o que aconteceu e qual é o passo
seguinte.

**Why this priority**: a recusa por apuração superada é a mais provável na operação real — basta um
desfecho em outro cartão do mesmo recorte para que a apuração fique para trás. Se ela aparecer só
depois do clique, com o motivo digitado perdido, a ação parece quebrada.

**Independent Test**: provocar cada recusa e conferir a mensagem, a orientação, a preservação do que
foi digitado e a ausência de qualquer registro novo.

**Acceptance Scenarios**:

1. **Given** um recorte cuja apuração vigente já se sabe para trás, **When** a presidência abre a
   ação num cartão em aberto, **Then** no lugar do formulário a tela diz que a correção está
   impedida, nomeia a causa com as palavras que a condução já usa, e oferece o caminho para emitir a
   apuração seguinte na tela da ocupação.
2. **Given** o formulário com o motivo vazio, **When** ela confirma, **Then** a recusa nomeia o
   motivo como obrigatório, junto do cartão, e o vencimento digitado continua no campo.
3. **Given** um vencimento que já passou, ou que vence no instante do ato, **When** ela confirma,
   **Then** a recusa é a da FR-269b da `019`, junto do cartão, e o motivo digitado continua no campo.
4. **Given** duas abas abertas no mesmo cartão, **When** a segunda confirma depois da primeira,
   **Then** a segunda é recusada porque a convocação nomeada já foi corrigida, e nenhuma segunda
   sucessora nasce.
5. **Given** um desfecho registrado na chamada entre a abertura do formulário e a confirmação,
   **When** a confirmação chega, **Then** ela é recusada porque a chamada já tem desfecho, e
   **nenhuma chamada nova nasce** no lugar da correção.
6. **Given** quem não pode convocar — o membro alocado à conferência, a auditoria —, **When** ele
   abre a condução, **Then** não vê a ação; **When** envia o formulário montado à mão, **Then**
   recebe 403, com a recusa explicada, e nada é gravado.
7. **Given** um Edital de outra unidade, **When** o formulário é enviado, **Then** a resposta é 404,
   e nada é gravado.
8. **Given** a pessoa que saiu da faixa por um ato posterior, ou a vaga faltante que deixou de
   existir para o suplente, **When** a correção é confirmada, **Then** a recusa do domínio aparece
   junto do cartão, nas palavras dele, com o motivo e o vencimento preservados.

---

### User Story 4 — Um ato, uma vez (Priority: P2)

O clique duplo, o reenvio do navegador e a confirmação repetida produzem uma sucessora só e uma
comunicação só.

**Why this priority**: o duplo envio de um ato irreversível que comunica o candidato produziria duas
mensagens com o mesmo prazo, e duas linhas de sucessão sem diferença. A guarda de idempotência já
existe no comando; o que esta história exige é que o formulário a use.

**Independent Test**: enviar o mesmo formulário duas vezes e contar sucessoras, comunicações e
eventos de trilha.

**Acceptance Scenarios**:

1. **Given** o formulário de correção, **When** ele é enviado duas vezes seguidas, **Then** nasce uma
   sucessora, sai uma comunicação, e a segunda resposta é o resultado da primeira.
2. **Given** o mesmo cartão, **When** a página é recarregada e a correção é feita de novo, com outro
   motivo, **Then** a segunda corrige a sucessora: é outro ato, e o histórico mostra os dois.

---

### Edge Cases

Os casos-limite são requisitos: cada um tem linha própria na matriz de rastreabilidade, como os FR- e
os SC-.

- **Chamada sem comunicação enviada.** É corrigível. A sucessora comunica como a chamada individual
  comunica; a comunicação pendente da corrigida deixa de ser oferecida em *"Comunicações que ainda não
  saíram"*, porque ela não é mais a vigente. O plano confere que a leitura atual já se comporta assim.
- **Correção em cadeia.** A sucessora também é corrigível, enquanto estiver em aberto. O número da
  chamada continua o mesmo em toda a cadeia.
- **Vencimento novo anterior ao atual, mas futuro.** É admitido: corrigir um prazo informado errado é
  correção legítima. O formulário avisa que vencimento anterior ao atual encurta um prazo já
  comunicado, e o resultado diz que o prazo foi antecipado.
- **Chamada sem vencimento.** A ação não aparece (D-004). O Edital que não publica prazo não tem prazo
  a dar.
- **Chamada para regularizar em aberto.** É corrigível, com a espécie dela, sem a guarda de ordem dos
  indeferidos — a pessoa já foi chamada.
- **Espécie derivada diferente da corrigida.** Quando a posição da pessoa mudou entre a chamada e a
  correção — o suplente que passou a ocupar pela contagem —, a sucessora leva a espécie derivada, e a
  prévia a mostra ao lado da atual (D-006).
- **Fundamento diferente.** A sucessora cita a apuração vigente no ato da correção. Quando ela não é a
  que a corrigida citou, a prévia diz (D-006).
- **Apuração seguinte emitida, ou Retificação publicada, entre a prévia e a confirmação.** O recorte
  não fica impedido, mas o fundamento, e talvez a espécie, mudaram: a confirmação é recusada como
  prévia superada, com a prévia nova à vista e os campos preservados (FR-3857).
- **O cartão mudou no intervalo.** Quando a recusa é porque a chamada foi corrigida por outra pessoa,
  ou teve desfecho, o motivo digitado aparece para copiar, e o formulário da sucessora nasce vazio
  (FR-3850).
- **Ordem sucedida, apuração ausente ou superada.** O recorte inteiro está impedido; a ação mostra a
  limitação e o caminho, sem formulário (FR-3839). Se o impedimento surgir entre a abertura e a
  confirmação, a recusa vem com a mesma orientação.
- **Processo em estado final.** A ação não aparece; o formulário montado à mão é recusado como toda
  escrita no Processo encerrado.
- **Requerimento em rascunho.** O rascunho feito antes do vencimento antigo continua sendo o
  rascunho, nem apagado nem convertido; depois da correção, ele se envia.
- **Conferências da chamada.** Item conforme continua conforme; item pendente continua pendente, e a
  complementação nova entra para conferência (FR-3573 e FR-3588 da `115`).
- **Desfecho que inclui.** Depois da correção, o desfecho se registra na sucessora, como em qualquer
  chamada em aberto, e a pendência documental continua bloqueando o aceite (FR-3592 da `115`).
- **Membro alocado à conferência.** Lê o cartão e o histórico; não vê a ação, e o POST dele recebe
  403.

## Requirements *(mandatory)*

### Functional Requirements

#### A ação

- **FR-3837**: O cartão de cada chamada **em aberto** — vigente e sem desfecho, com o prazo em curso,
  com o vencimento decorrido ou sem comunicação enviada — e **com vencimento** MUST oferecer a ação
  *"Corrigir esta convocação"* a quem pode convocar no recorte, com a mesma base e a mesma
  verificação de escopo da chamada individual (FR-887 da `050`).
- **FR-3838**: A ação MUST NOT aparecer na chamada com desfecho, em convocação sucedida, em chamada
  sem vencimento (D-004), com o Processo em estado final, nem a quem só lê a condução — o membro
  alocado à conferência e a auditoria.
- **FR-3839**: Quando o recorte tem um impedimento que a leitura da condução já conhece — ordem não
  vigente, apuração ausente, apuração superada —, a ação MUST continuar visível e, no lugar do
  formulário, MUST dizer que a correção está impedida, nomear a causa com as mesmas palavras que a
  condução já usa para ela, e oferecer o mesmo caminho que a condução já oferece no topo para o
  passo seguinte — *"Emitir a apuração seguinte"*, na ocupação, para a apuração superada. MUST NOT
  oferecer formulário que a confirmação recusaria por essa causa (D-005).

#### O formulário

- **FR-3840**: O **motivo** MUST ser obrigatório, em texto livre, e gravado como o motivo da
  sucessão. Vazio, ou só com espaços, MUST ser recusado nomeando o campo, sem gravar nada.
- **FR-3841**: O **vencimento novo** MUST ser obrigatório, informado como na chamada individual —
  digitado, ou o fim de um Evento do Cronograma publicado (FR-866 da `050`) —, e MUST NOT vir
  pré-preenchido. Ele MUST ser posterior ao instante do ato, com a recusa da FR-269b da `019`.
- **FR-3842**: O complemento do fundamento MUST ser opcional, e gravado junto do texto derivado, como
  na chamada individual (FR-869 da `050`).
- **FR-3843**: O formulário MUST nomear a **convocação que corrige**, e não só a inscrição. A
  confirmação MUST ser recusada quando, no instante do ato e sob a mesma trava do comando, a
  convocação nomeada não for mais a vigente em aberto daquela inscrição no recorte — porque foi
  sucedida, ou porque teve desfecho, no intervalo. A recusa MUST dizer qual dos dois aconteceu, e MUST
  NOT corrigir a sucessora nem praticar chamada nova no lugar (D-003).

#### A prévia (FR-870 da `050`)

- **FR-3844**: Antes do botão, o formulário MUST mostrar, cada valor com a origem ao lado (UX-101 da
  `050`):
  - a pessoa, pelo protocolo e pelo nome, e o número da chamada;
  - o vencimento atual e a situação da chamada;
  - a espécie e o fundamento que a sucessora levará, derivados como na chamada individual, e a
    indicação de quando diferem dos da convocação corrigida (D-006);
  - a forma de comunicação do Perfil e o que ela fará no ato *(item revisto pela `121` em 2026-11-05,
    que vigora com a implementação dela — a redação anterior está ao fim deste item)*: a mensagem
    individual sai de novo, **como mensagem da correção**, com o prazo válido, dizendo que substitui a
    anterior e sem o motivo (FR-3885 e FR-3890 da `121`); por publicação, a comunicação aguarda a
    publicação, como hoje;

    > **Redação anterior à `121`, preservada:** a mensagem individual sai de novo, com o texto da
    > convocação e o prazo novo, sem dizer que corrige a anterior (D-007); por publicação, a
    > comunicação aguarda a publicação, como hoje;
  - o efeito do vencimento informado sobre o atual, que são três, e a prévia diz qual:
    - **posterior ao atual:** o prazo é estendido até o vencimento novo;
    - **anterior ao atual, e ainda futuro:** o prazo é **antecipado**, e encurta um prazo já
      comunicado;
    - **igual ao atual:** o vencimento é mantido, e a correção muda só o que mais ela levar — o
      fundamento derivado no ato, o complemento e a comunicação.

    Enquanto nenhum vencimento foi informado, a prévia diz as três regras; quando é informado, diz a
    que se aplica. A FR-3849 repete, depois do ato, a que se aplicou;
  - o que reabre, quando a chamada já venceu: até o vencimento novo, o convocado volta a poder enviar
    e complementar os documentos da chamada e preencher e enviar o Requerimento declarado na
    convocação (FR-3622 da `115`). Com o prazo em curso, nada estava fechado, e a prévia não diz que
    reabre;
  - o que não muda: a lista, as apresentações e as conferências da chamada (FR-3573 da `115`), e a
    convocação corrigida, que continua legível no histórico com o motivo.
- **FR-3845**: O formulário MUST declarar, antes do botão, que corrigir é irreversível, que a
  correção é uma convocação nova que sucede a anterior, e que um vencimento anterior ao atual encurta
  um prazo já comunicado. O botão MUST nomear a pessoa pelo protocolo (*"Corrigir a convocação de
  <protocolo>"*): há um formulário por cartão, e o botão sem nome se confunde entre eles.

#### A confirmação

- **FR-3846**: A confirmação MUST praticar o ato pelo comando de convocar que já existe, com motivo —
  a sucessora aponta a corrigida, tem o mesmo número de chamada e o vencimento novo —, acrescido só
  das conferências da FR-3843 e da FR-3857. MUST NOT criar comando, papel, tabela, estado, desfecho ou mensagem
  novos.
- **FR-3847**: Sem base para convocar, a confirmação MUST ser recusada com 403 e a recusa explicada;
  Edital de outra unidade, ou inexistente, MUST responder 404 (FR-478 da `033`), e a convocação
  nomeada que não é do recorte ou da inscrição do formulário também, porque é referência fora do
  escopo do ato. Nos casos, nada é gravado.
- **FR-3848**: O mesmo formulário enviado mais de uma vez MUST NOT produzir duplicidade: no máximo
  **uma** sucessora, **um** evento de trilha do ato e **uma** mensagem enviada para ela. A repetição
  MUST devolver o resultado do primeiro envio, qualquer que ele tenha sido: comunicação enviada,
  aguardando publicação ou com falha de envio. A repetição MUST NOT ser o caminho para tentar de novo
  uma comunicação que falhou; esse caminho continua sendo o das comunicações que ainda não saíram,
  como na chamada individual.
- **FR-3849**: Depois do ato, a tela MUST dizer que a convocação foi corrigida, o vencimento anterior
  e o novo — e se o prazo foi estendido ou antecipado —, e o resultado da comunicação, como a chamada
  individual diz (UX-103 da `050`), sem *"recebido"*, *"lido"* nem *"entregue"* (UX-039 da `019`).
  O cartão MUST passar a mostrar a sucessora, com o vencimento novo, a situação recalculada e a
  indicação de que foi corrigida, com o caminho para o histórico.
- **FR-3850**: A recusa MUST aparecer junto do cartão da chamada, nas palavras do domínio, e MUST
  preservar o motivo, o vencimento e o complemento digitados (UX-104 da `050`). Vale para as recusas
  que a leitura da condução não antecipa — fora da faixa, sem vaga faltante, impedimento surgido no
  intervalo, prévia superada (FR-3857) — e para as do formulário (D-009). Quando a recusa é porque a
  convocação corrigida já foi sucedida ou teve desfecho (FR-3843), o cartão daquela chamada mostra a
  situação nova, a recusa diz quem praticou o ato e quando, e o motivo digitado aparece como texto,
  para copiar: ele MUST NOT pré-preencher o formulário da sucessora, porque foi escrito para outra
  convocação.

#### A trilha e o histórico

- **FR-3851**: Cada correção MUST registrar um evento de trilha, com o ator, a base que o autorizou,
  o escopo institucional e o instante, como os demais atos da condução, e com o motivo, a convocação
  corrigida, o vencimento anterior, o novo e a origem do novo (FR-866 da `050`).
- **FR-3852**: O histórico do recorte MUST mostrar a corrigida como sucedida, com o motivo, e a
  sucessora como vigente, com a proveniência de cada uma (FR-295 da `019`); N correções em cadeia
  MUST aparecer como N + 1 linhas da mesma chamada.

#### O que não muda

- **FR-3853**: A fila de chamada, a fila dos regularizáveis e os gestos em lote MUST NOT mudar: quem
  tem chamada em aberto continua fora das filas, o lote continua sem sucessão (FR-861 da `050`), e
  nenhum item de documento ganha prazo próprio (FR-3618 da `115`).
- **FR-3854**: O portal MUST mostrar o prazo novo e reabrir documentos e Requerimento pelas regras
  que a `115` e a `118` já fixaram; esta feature MUST NOT acrescentar regra ao portal. Divergência
  encontrada na verificação é defeito daquelas specs, registrado como achado. **A demonstração da
  User Story 2, de ponta a ponta, é condição de conclusão desta feature:** se o defeito a impedir, a
  conclusão fica bloqueada até que ele seja resolvido, pela via que o usuário decidir, e ele não
  entra no escopo desta feature por ter sido encontrado aqui.
- **FR-3855**: O custo de consulta da tela da condução MUST NOT crescer com o número de cartões que
  oferecem a ação (FR-888 da `050`).
- **FR-3856**: O nome do ato na tela MUST ser *"Corrigir esta convocação"*. A tela MUST NOT chamar o
  ato de *"prorrogação"* nem de *"reabertura de prazo"*, porque esses atos não existem (FR-3618 da
  `115`); a ajuda da ação PODE dizer que é por ela que se dá mais prazo.

#### A prévia confirmada (ampliação da revisão de `4b2bd844`)

- **FR-3857**: O formulário MUST carregar a assinatura do que a prévia mostrou: a convocação
  corrigida, a apuração, a versão do Edital e a espécie derivada. A confirmação MUST ser recusada
  quando, sob a trava do ato, qualquer uma delas diferir da vigente — porque a apuração seguinte foi
  emitida, porque uma Retificação mudou a versão, ou porque a posição da pessoa mudou a espécie. A
  recusa MUST mostrar a prévia nova, com os campos preservados (FR-3850), e nada é gravado. O
  fundamento gravado é função desses quatro e do complemento digitado, e é por isso o que foi
  mostrado (FR-869 da `050`) (D-010).

### Key Entities

Nenhuma entidade nova. A feature usa:

- **Convocação**, append-only: a sucessora aponta a corrigida, carrega o motivo da sucessão e
  reaproveita o número da chamada (FR-272 da `019`).
- **Chamada**: o número compartilhado pela cadeia de sucessão, ao qual pertencem a lista, as
  apresentações e as conferências (FR-3573 da `115`).
- **Evento de trilha** do ato de convocar, com a razão que já registra o motivo da sucessão.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1141**: Pela tela, quem conduz corrige uma chamada em aberto em **um** envio de formulário, sem
  shell nem chamada direta ao serviço — verificado no navegador, nos três estados em aberto.
- **SC-1142**: No cenário de ponta a ponta — chamada vencida, com documento pendente e Requerimento
  por enviar —, depois da correção o convocado vê o prazo novo no portal e conclui a complementação e
  o envio do Requerimento, os dois antes do vencimento novo; decorrido o vencimento novo, os dois são
  recusados com a mesma frase.
- **SC-1143**: Cada uma das recusas — motivo vazio, vencimento passado, chamada com desfecho,
  convocação já sucedida, prévia superada, ator sem base (403), Edital de outra unidade (404), recorte
  impedido — grava
  **zero** convocações, **zero** comunicações e **zero** eventos de trilha.
- **SC-1144**: Dois envios do mesmo formulário produzem exatamente **uma** sucessora e **um** evento
  de trilha do ato, e no máximo **uma** mensagem enviada; a segunda resposta repete a primeira nos
  três resultados possíveis da comunicação — enviada, aguardando publicação e falha de envio.
- **SC-1145**: Depois de duas correções em cadeia, o histórico mostra **três** linhas da mesma
  chamada, com o motivo em cada sucedida, e a lista, as apresentações e as conferências da chamada
  têm a mesma contagem antes e depois.
- **SC-1146**: Com a apuração superada, **todos** os cartões em aberto do recorte mostram a limitação
  e o caminho, e **nenhum** oferece formulário.
- **SC-1147**: A tela da condução gasta o mesmo número de consultas com uma chamada em aberto e com
  vinte.
- **SC-1148**: Em toda recusa junto do cartão, o motivo e o vencimento digitados continuam nos campos
  — quem opera não redigita nada para tentar de novo.
- **SC-1149**: Cada correção tem **um** evento de trilha que nomeia o ator, o motivo, a convocação
  corrigida e os dois vencimentos.

## Assumptions

- A autorização de corrigir é a de convocar: a base de gestão da comissão no Processo. A conferência
  documental e a auditoria leem e não convocam (FR-887 da `050`).
- O comando de convocar já recusa o vencimento passado, o Processo em estado final, a ordem não
  vigente, a apuração ausente ou superada, a pessoa fora da faixa e o suplente sem vaga faltante, e já
  é idempotente pela chave do formulário. Esta feature não muda nenhuma dessas guardas.
- A sucessora já reabre documentos e Requerimento no domínio: o caso está coberto por teste de serviço
  (`tests/integration/requerimentos/test_prazo_da_chamada.py`). O que falta é o caminho de tela e a
  verificação de ponta a ponta.
- A verificação no navegador usa os cenários da `115` e da `118` e um banco de teste próprio desta
  worktree.

## Proteção de dados (LGPD)

Nenhum dado pessoal novo é coletado, guardado ou enviado.

- **O motivo da correção** é texto da comissão sobre o ato, e é guardado onde o motivo da sucessão já
  mora: na convocação, append-only, e na razão da trilha. Ele não vai ao convocado: a mensagem da
  sucessora é a de hoje (D-007), e o portal não o mostra. Quem redige o motivo MUST NOT precisar de
  dado pessoal além do que a convocação já identifica, e a ajuda do campo o diz. *(Desde a `121`,
  revista em 2026-11-05, a mensagem da sucessora é a da correção, que diz o que substitui; o motivo
  continua fora dela e do portal.)*
- **A sessão do operador** guarda os campos digitados só entre a recusa e a tela seguinte, que os
  consome ao exibir (D-009). Nada disso vai a log.
- **A prévia** mostra o protocolo e o nome do convocado, que o cartão já mostra, a quem já pode
  convocar; nenhuma leitura nova de dado da inscrição.
- **Nenhum endereço novo carrega dado pessoal**: a correção usa a rota da chamada individual, por POST.

## Compatibilidade com regras anteriores

| Regra | Como esta spec se relaciona |
|---|---|
| FR-870 da `050` | **cumprida** para a sucessão: as derivações aparecem antes da confirmação |
| FR-861 da `050` | preservada: o lote continua sem sucessão |
| FR-866 da `050` | preservada: o vencimento é informado uma vez, digitado ou de um Evento, com a origem na trilha |
| FR-886 da `050` | preservada: nada se altera; corrigir é suceder |
| FR-887 da `050` | preservada: mesma permissão e mesmo escopo, sem autoridade nova |
| FR-888 da `050` | preservada (FR-3855) |
| FR-272 da `019` | preservada: correção é sucessão com motivo |
| FR-269b da `019` | preservada: vencimento posterior ao ato |
| FR-290 da `019` | **não tocada**: a mensagem da sucessora é a de hoje (D-007) |
| FR-084 da `010` | preservada: a sucessora comunica pela terceira situação, quando o Perfil declara mensagem individual |
| FR-3618 da `115` | **cumprida**: dar mais prazo é corrigir, e a tela passa a oferecer o caminho |
| FR-3622 da `115` | **verificada de ponta a ponta**: a correção reabre tudo junto |
| FR-3573 da `115` | preservada: a sucessora usa a lista, as apresentações e as conferências da chamada |

## Decisões

### D-001 — Spec própria, e não emenda à `050`

*Do usuário, em 04/11/2026.* A `050` está fechada, com tarefas, contratos e matriz de rastreabilidade
cobrada requisito a requisito; a emenda reabriria uma feature mergeada. O escopo cruza a `019` (a
sucessão), a `050` (a tela da condução) e a `115` (o prazo e a reabertura), e uma spec própria cita
as três sem reescrever nenhuma.

### D-002 — A ação mora no cartão da chamada, e a fila não muda

A pessoa a corrigir já foi chamada: ela está nos cartões, e não na fila. Pôr a correção no seletor
da fila exigiria devolver à fila quem tem chamada em aberto, e a fila deixaria de dizer *"quem pode
ser chamado"*. No cartão, o formulário já sabe qual convocação corrige, e o desfecho e a correção
ficam lado a lado — as duas coisas que se fazem com uma chamada em aberto.

### D-003 — A correção nomeia a convocação que corrige

O comando de hoje recebe a inscrição e corrige a convocação em aberto dela no instante do ato. Pela
tela isso abre dois caminhos errados:

- um formulário aberto antes de outra pessoa corrigir a chamada corrigiria **a sucessora**, com um
  motivo escrito para a anterior;
- um formulário aberto antes de um desfecho chegaria sem convocação em aberto, e o comando praticaria
  uma **chamada nova**, ignorando o motivo.

A confirmação leva a convocação nomeada e é recusada quando ela não é mais a vigente em aberto,
conferida sob a trava. É a mesma ideia da assinatura do alcance que o gesto dos vencidos da `050` já
confere: a pessoa confirma o que viu, ou nada acontece. O plano decide onde a conferência mora; o
requisito é que ela aconteça sob a trava.

### D-004 — Pela tela só se corrige chamada com vencimento, e o vencimento novo é obrigatório

A necessidade operacional é o prazo (FR-3618 da `115`). Corrigir só o complemento do fundamento, sem
tocar no prazo, é raro, e continua possível como hoje pelo serviço. A chamada sem vencimento existe
porque o Edital não publica prazo (FR-866 da `050`); dar a ela um vencimento por correção seria criar
um prazo que o Edital não tem. Por isso a ação não aparece nela, e na chamada com vencimento o
vencimento novo é obrigatório.

### D-005 — A apuração superada é limitação declarada antes do formulário

A guarda que recusa convocar sobre apuração superada é correta e fica. Mas na operação ela é o
impedimento mais provável — um desfecho em outro cartão basta —, e se aparecer só depois do clique,
com o motivo perdido, a ação parece quebrada. A condução já calcula as causas de obsolescência do
recorte para mostrá-las no topo da tela; a ação usa a mesma leitura e, no lugar do formulário, diz
*"A correção está impedida: …"*, com a causa e o caminho para a ocupação. Vale igualmente para a ordem
não vigente e para a apuração ausente. As recusas que dependem da pessoa — fora da faixa, sem vaga
faltante — não se antecipam sem custo por cartão, e aparecem na confirmação, pela D-009.

### D-006 — Espécie e fundamento da sucessora são os derivados no ato

O comando deriva a espécie da posição da pessoa e o fundamento da apuração vigente no ato da
correção. Os dois podem diferir dos da convocação corrigida. A prévia mostra os que a sucessora vai
levar e diz quando diferem: a sucessora é uma convocação nova, e o que ela afirma é o que vale no
instante dela.

### D-007 — A comunicação é a de hoje

Com o Perfil que convoca por mensagem individual, a sucessora comunica com o texto da convocação e o
prazo novo, como a chamada individual. A mensagem não diz que corrige a anterior, e a prévia diz isso
com essas palavras, para ninguém supor o contrário. A redação própria da correção é decisão sobre a
FR-290 da `019`, fora desta spec.

> **Revista pela `121` em 2026-11-05**, que vigora com a implementação dela: a redação própria foi
> decidida pelo usuário, e a sucessora comunicada por mensagem individual sai com a **mensagem da
> correção**, que diz o que substitui e não diz o motivo (FR-3885 da `121`); a prévia passa a dizê-lo
> (FR-3890 da `121`). O resto desta decisão continua.

### D-008 — A prévia está no próprio formulário, como na chamada individual da `050`

A chamada individual da `050` mostra as derivações no formulário, antes do botão, e não numa segunda
tela. A correção faz o mesmo: o que é derivado (espécie, fundamento, forma de comunicação, o que
reabre, o que continua) não depende do que se digita, e o que se digita (motivo e vencimento) está
nos campos à vista. O resultado depois do ato repete o vencimento anterior e o novo. Uma tela
intermediária de confirmação acrescentaria rota e estado sem mostrar nada que o formulário não mostre.

*Na revisão de `4b2bd844`:* a única parte da prévia que depende do que se digita é o efeito do
vencimento — estende, antecipa ou mantém (FR-3844). O formulário a diz pelo valor informado, e, sem
o valor, diz as três regras. A decisão de não ter tela intermediária fica.

### D-009 — A recusa volta ao cartão com o que foi digitado

Hoje a recusa da condução aparece no topo da tela, e os campos voltam vazios. Para um ato com motivo
obrigatório, redigitar o motivo a cada recusa é o atrito que faz a pessoa desistir, ou escrever menos
na segunda vez. A recusa da correção volta aberta no cartão da chamada, com os campos como estavam.

*Complemento da revisão de `4b2bd844`:* quando o cartão mudou no intervalo — a chamada foi corrigida
por outra pessoa, ou teve desfecho —, os campos não voltam para um formulário, porque o formulário
que existe agora é o da sucessora, ou nenhum. O motivo aparece como texto, para copiar, e a recusa diz
quem praticou o ato e quando (FR-3850).

### D-010 — A confirmação assina a prévia

*Ampliação da D-003, na revisão de `4b2bd844`.* Nomear a convocação corrigida impede corrigir a
sucessora ou praticar chamada nova, mas não impede gravar um fundamento que ninguém viu: a apuração
seguinte, emitida por outra pessoa entre a prévia e a confirmação, muda a data que o fundamento cita
sem tocar na convocação; uma Retificação muda os rótulos do Edital e do recorte; a contagem nova pode
mudar a espécie. O formulário leva a assinatura do que mostrou — convocação, apuração, versão e
espécie —, e o comando a confere sob a mesma trava em que deriva o fundamento. É a mesma garantia que
a assinatura do alcance dá ao gesto dos vencidos da `050`: confirma-se o que se viu, ou nada
acontece.

## Registrado, sem desenvolver

- **A mensagem da sucessora.** Uma redação que diga *"A sua convocação foi corrigida: o novo prazo é
  …"* é decisão sobre a FR-290 da `019`, com parente em
  `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`. Fica para o usuário.
  *(Decidida pelo usuário em 05/11/2026 e especificada na `121`, FR-3885 e FR-3890: a mensagem da sucessora comunicada diz que substitui a anterior, com a data do envio substituído e o prazo que ele informava, e sem o motivo.)* O texto não diz *"novo prazo"*, porque a sucessora pode antecipar (FR-3856).
- **O aviso de pendência (`QI-7`).** Continua com a decisão institucional registrada na `118`.
- **O formulário montado à mão.** O achado observava, sem executar, que um POST montado por quem já
  pode convocar criaria a sucessora. Com a FR-3843 esse POST continua possível para quem tem a
  competência — é o próprio ato —, mas passa a exigir a convocação nomeada, e não corrige outra que
  não a vista.
