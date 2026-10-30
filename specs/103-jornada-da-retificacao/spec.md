# Feature Specification: Jornada operacional da Retificação — encontrar, retomar, corrigir e passar adiante pela navegação comum

**Feature Branch**: `claude/silly-cerf-78b884`, sobre a `main` em `0061f28e`

**Created**: 2026-10-30

**Status**: Implementada nesta branch; merge não autorizado. A validação com as pessoas da reunião
de 29/10 (SC-978) espera o usuário.

**Input**: a auditoria de 29/10/2026,
[`doc/auditoria-retificacao-passagem-e-sorteio-2026-10-29.md`](../../doc/auditoria-retificacao-passagem-e-sorteio-2026-10-29.md),
trazida do PR #338, e o teste de reprodução que a acompanha
(`backend/tests/interface/test_auditoria_passagem_da_retificacao.py`). A auditoria resolve os achados
AUD-RET-01 a AUD-RET-04. O AUD-RET-05 é de governança e fica fora (ver *Pendências do usuário*). A
recusa do sorteio da mesma reunião já foi resolvida pela `102` e também fica fora.

> **Faixa de identificadores.** Esta spec abre em **FR-2701** e **SC-971**. O teto foi medido em
> 30/10/2026 em `specs/` de todas as worktrees desta máquina e nos PRs abertos: o requisito
> funcional dois mil seiscentos e setenta e um, da `101`, e o critério novecentos e cinquenta e nove,
> da `102`. O salto até a centena seguinte deixa folga para sessões paralelas. **Nenhum `UX-` é
> aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-021 da `001`"). Uma decisão ou princípio de outra feature é citado pelo assunto e
> pela feature, porque `D-` aqui é só desta spec.

---

## Por que esta feature existe

Na reunião de validação de 29/10, quem homologa não encontrou a Retificação que outra pessoa
submetera, e só chegou a ela colando o endereço copiado da sessão anterior. A auditoria confirmou a
causa: **nenhuma tela lista Retificação que ainda não foi publicada.** O único caminho até o detalhe
de uma Retificação sai do cartão "Documentos publicados" do Edital, e só existe depois da
Publicação. Nem quem criou o rascunho o reencontra depois de sair da tela.

**O servidor está certo, e esta feature não o muda.** A URL copiada só funcionou porque a pessoa
tinha a permissão. Quem não tem recebe 403, quem é de outra unidade recebe 404, e o ato fora da
situação recebe 409. A segregação de funções é verificada no servidor. O que falta é o corredor até
a porta, e não a fechadura.

Três lacunas acompanham a primeira:

- **AUD-RET-02.** A Retificação não diz quem age a seguir. O Edital diz, desde a `007` (passagem de
  bastão, FR-028 a FR-031 daquela feature). Depois de submeter, a tela só mostra "Ato registrado".
- **AUD-RET-03.** O detalhe oferece "Publicar Retificação" a quem a segregação vai recusar. O Edital
  antecipa essa recusa, e a Retificação não.
- **AUD-RET-04.** A tela de Retificar sempre **cria**. A edição do rascunho existe no domínio e só a
  API a chama. A devolução promete "pode ser editada novamente", e a tela não cumpre: quem corrige
  compõe outra Retificação, e a devolvida fica em elaboração para sempre.

### O que foi verificado no código em 30/10/2026

- O detalhe da Retificação já é aberto a todo ator do escopo, e os atos oferecidos já saem da
  permissão e da situação (`atos_retificacao.disponiveis`). Listar as Retificações a esse mesmo
  público **não amplia acesso nenhum**.
- O comando de edição do rascunho existe, confere a revisão por comparação e troca, só aceita a
  Retificação em elaboração e substitui o conjunto inteiro de alterações. Ele não registra evento na
  trilha.
- A segregação da Retificação tem a mesma forma da do Edital: recusa publicar quando quem submeteu e
  quem homologou são o próprio ator. A tela do Edital antecipa essa recusa com duas funções de
  leitura que recebem só os nomes dos participantes, e por isso servem à Retificação sem cópia.
- Os atos da Retificação têm as mesmas chaves dos atos do Edital (`submeter`, `homologar`,
  `devolver`, `publicar`). A tabela de "a quem este ato entrega" do Edital serve aos dois.

### O que esta spec cobre, e o que fica fora

**Cobre**: a descoberta das Retificações em curso, no Edital e na Lista; o detalhe que responde onde
está, em que situação, quem age a seguir e o que a pessoa pode fazer; a edição do mesmo registro,
com a revisão conferida; a passagem de bastão; a antecipação da recusa por segregação; e as jornadas
completas, por sessões independentes, sem endereço digitado.

**Fica fora**: fila nominal, caixa de entrada, notificação, atribuição a pessoa, papel ou permissão
nova, estado ou transição nova, mudança na interpretação da FR-021 da `001` (AUD-RET-05), leitura de
Retificação pela API, e o reapontamento da base de uma Retificação para a versão vigente pela tela.

---

## Clarifications

### Session 2026-10-30

As perguntas que a auditoria deixou ao usuário foram respondidas no pedido desta feature, escrito
pela sessão que a conduziu:

- Q: A devolvida se reabre na tela, ou devolver significa recompor? → A: Reabre. A tela edita o
  mesmo registro, pelo comando de edição que já existe, com a revisão conferida (D-001).
- Q: A descoberta mora onde? → A: Em dois níveis. No detalhe do Edital, uma seção "Retificações em
  curso". Fora dele, a menor entrada que deixe quem homologa e quem publica perceber trabalho sem
  percorrer cada Edital, escolhida entre a Lista, "Minhas Etapas" e o próximo responsável (D-002).
- Q: Uma Retificação em curso impede criar outra? → A: Não. Unicidade não tem fundamento na norma. A
  tela mostra as que existem antes e durante a decisão de criar (D-005).
- Q: O "elaborou" da FR-021 da `001` é quem submete ou quem compõe? → A: Fora desta feature. A
  interpretação atual, quem submete, é preservada e a pergunta fica registrada (AUD-RET-05).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem homologa e quem publica encontram o trabalho sem endereço (Priority: P1)

Bruno homologa Retificações. Ana submeteu uma, e Bruno abre o sistema pela página inicial. Na Lista,
a linha do Edital diz que há uma Retificação em revisão e que ele pode homologá-la. Um clique o leva
ao detalhe da Retificação. Depois que Bruno homologa, Carla, que publica, encontra a mesma
Retificação pelo mesmo caminho, com a marca "Publicar Retificação".

**Why this priority**: é o achado que parou a reunião. Sem ele, todo o resto só anda por URL
copiada.

**Independent Test**: três sessões independentes; quem homologa e quem publica partem só das seções
da barra lateral e alcançam o detalhe da Retificação em até dois cliques.

**Acceptance Scenarios**:

1. **Given** uma Retificação em revisão, **When** quem homologa abre a Lista, **Then** a linha do
   Edital mostra a Retificação em revisão, nomeia o ato que ele pode praticar e liga ao detalhe.
2. **Given** a mesma Retificação, **When** quem homologa abre o detalhe do Edital, **Then** a seção
   "Retificações em curso" a lista com a situação, quem age a seguir e o link.
3. **Given** uma Retificação homologada, **When** quem publica percorre o mesmo caminho, **Then** ele
   a encontra com o ato "Publicar Retificação".
4. **Given** uma Retificação em revisão, **When** quem só elabora abre a Lista, **Then** ele vê a
   Retificação e quem age a seguir ("aguarda quem homologa"), sem ato oferecido a ele.
5. **Given** um Edital publicado sem Retificação em curso, **When** alguém abre o detalhe do Edital,
   **Then** a seção diz que não há Retificação em curso e onde estão as publicadas.

---

### User Story 2 — Quem elabora retoma o rascunho e o corrige no mesmo registro (Priority: P1)

Ana compôs uma Retificação e saiu da tela. No dia seguinte, ela a encontra no Edital, abre "Editar a
Retificação", vê o que já tinha declarado, muda um valor e confirma. A Retificação é a mesma, com a
mesma identidade, e a trilha registra a edição. Se Bruno a devolver, Ana lê o motivo no detalhe,
corrige pela mesma tela e submete de novo, quantas vezes for preciso.

**Why this priority**: sem isto, cada devolução produz uma segunda Retificação, e a primeira fica em
elaboração para sempre.

**Independent Test**: uma sessão cria, sai, reencontra pela navegação, edita e confirma; o
identificador não muda, e o conteúdo proposto passa a ser o editado. Depois de duas devoluções, o
mesmo registro é publicado.

**Acceptance Scenarios**:

1. **Given** uma Retificação em elaboração, **When** quem elabora abre a edição, **Then** o
   formulário mostra o conteúdo proposto, com as alterações já declaradas, a justificativa e a
   vigência.
2. **Given** a edição aberta, **When** a pessoa muda um campo e confere, **Then** a tela mostra o que
   muda em relação ao rascunho, sem gravar.
3. **Given** a conferência, **When** a pessoa confirma, **Then** a mesma Retificação passa a declarar
   o ato inteiro, as alterações anteriores que ela não tocou continuam declaradas, e a trilha registra
   a edição com a revisão anterior e a posterior.
4. **Given** uma Retificação devolvida, **When** quem elabora abre o detalhe, **Then** o motivo da
   devolução aparece em destaque, ao lado de "Editar a Retificação".
5. **Given** outra pessoa do mesmo escopo com o papel de elaborar, **When** ela abre a Retificação de
   Ana, **Then** ela também pode editá-la e submetê-la.
6. **Given** uma remoção já declarada no rascunho, **When** a pessoa a desfaz na edição, **Then** a
   remoção sai do ato.

---

### User Story 3 — Cada ato diz a quem entrega, e a tela não oferece o que o servidor recusa (Priority: P1)

Ao submeter, Ana lê que a Retificação fica aguardando quem homologa. Depois do ato, o detalhe diz
quem age a seguir. Dora acumula os três papéis: ao homologar o que ela mesma submeteu, a tela avisa
que a publicação ficará com outra pessoa; e, homologada, o detalhe mostra "Publicar Retificação"
desabilitado, com o motivo, em vez de um botão que leva a uma recusa.

**Why this priority**: é o que transforma a localização em jornada. Encontrar a tela e não saber
quem age, ou clicar num ato que será recusado, é a mesma falha com outra roupa.

**Independent Test**: para cada combinação de papel e situação, o que a tela oferece é exatamente o
que o servidor aceita; com a segregação, o ato aparece desabilitado com o motivo.

**Acceptance Scenarios**:

1. **Given** uma Retificação em elaboração, **When** quem elabora abre a confirmação de submeter,
   **Then** a tela diz que o ato entrega a Retificação a quem homologa.
2. **Given** uma Retificação submetida, **When** o detalhe é aberto, **Then** ele diz que quem age a
   seguir é quem homologa, e se é a própria pessoa.
3. **Given** quem submeteu e homologou a mesma Retificação, **When** abre o detalhe, **Then**
   "Publicar Retificação" aparece desabilitado com o motivo, e a confirmação não oferece
   "Confirmar".
4. **Given** quem submeteu, **When** abre a confirmação de homologar, **Then** a tela avisa que, se
   homologar, a publicação ficará com outra pessoa, e o ato continua disponível.
5. **Given** uma recusa, **When** ela vem de falta de permissão, de segregação ou de situação
   incompatível, **Then** a mensagem diz qual das três foi.

---

### User Story 4 — Quem decide criar uma Retificação vê as que já estão em curso (Priority: P2)

Ana abre "Retificar" num Edital que já tem uma Retificação em elaboração. Antes do formulário, a tela
diz que existe uma em curso, em que situação, e oferece continuar a elaboração dela. Ana pode, ainda
assim, compor outra.

**Why this priority**: evita a segunda Retificação por desconhecimento da primeira, sem impor
unicidade.

**Independent Test**: com uma Retificação em elaboração, a tela de Retificar cita a existente e liga
à edição dela; compor outra continua possível.

**Acceptance Scenarios**:

1. **Given** uma Retificação em curso, **When** quem elabora abre Retificar, **Then** a tela lista a
   existente com a situação e o caminho até ela.
2. **Given** a mesma tela, **When** a pessoa compõe e confirma uma nova, **Then** a nova é criada,
   e as duas aparecem em curso.

---

### User Story 5 — Exceções: concorrência, situação e escopo (Priority: P2)

Duas pessoas abrem a edição da mesma Retificação; a primeira confirma, e a segunda é recusada sem
gravar, com a explicação de que a Retificação mudou depois de aberta. A Retificação submetida não
abre a edição. Quem é de outra unidade não a vê na Lista nem no Edital, e recebe "não encontrado"
pela URL.

**Why this priority**: as garantias do servidor já existem; a tela precisa dizê-las sem perder
trabalho calado nem sobrescrever o de outra pessoa.

**Independent Test**: duas sessões, uma edição concorrente e uma tentativa de edição fora da
situação.

**Acceptance Scenarios**:

1. **Given** duas sessões com a edição aberta, **When** as duas confirmam, **Then** a primeira grava
   e a segunda é recusada, sem gravar, com a orientação de reabrir.
2. **Given** uma Retificação em revisão, **When** alguém abre a edição, **Then** a tela recusa com a
   situação atual e o caminho (devolver para elaboração).
3. **Given** uma Retificação publicada ou cancelada, **When** alguém abre o detalhe, **Then** ele diz
   que está encerrada e não oferece ato nem edição.
4. **Given** um ator de outra unidade, **When** ele abre a Lista, o Edital ou a URL, **Then** a
   Retificação não aparece, e a URL responde "não encontrado".

---

### Edge Cases

- **Várias Retificações em curso no mesmo Edital.** Todas aparecem, da mais antiga para a mais
  recente, cada uma com a sua situação e o seu próximo responsável.
- **Retificação devolvida duas vezes.** O motivo exibido é o da última devolução; as anteriores
  estão na trilha.
- **Ator com vários papéis.** As permissões se somam, como no resto do sistema. Os atos oferecidos
  são os de todos os papéis, e a segregação entra só onde a regra a põe (publicar).
- **Remover uma entidade que o próprio rascunho acrescentou.** O acréscimo sai do ato, e nenhuma
  remoção é declarada sobre o conteúdo vigente.
- **Voltar um campo ao valor vigente.** A alteração daquele campo sai do ato.
- **Edição que zera o ato.** Desfazer tudo deixaria a Retificação sem alteração; a gravação é
  recusada como na criação ("Nenhum campo foi alterado").
- **Edital encerrado ou Processo finalizado com Retificação em curso.** A seção continua listando,
  e os atos continuam sendo recusados pelo servidor com a razão dele.
- **A versão vigente mudou depois da base do rascunho.** A edição continua sobre a base em que o
  rascunho nasceu; a publicação confere conflitos, como hoje.
- **Sem nenhuma permissão de Retificação.** O ator vê a seção e as marcas, com quem age a seguir, e
  nenhum ato.

---

## Requirements *(mandatory)*

### Functional Requirements

#### No detalhe do Edital

- **FR-2701**: O detalhe do Edital MUST exibir a seção "Retificações em curso" com toda Retificação
  do Edital em elaboração, em revisão ou homologada, a todo ator do escopo do Edital, da mais antiga
  para a mais recente.
- **FR-2702**: Cada Retificação listada MUST dizer a situação por extenso, quando e por quem foi
  criada, a justificativa, quem age a seguir (FR-2711) e o caminho até o detalhe dela. Quando o ator
  tem o ato seguinte entre os que pode praticar (FR-2730), MUST nomear esse ato.
- **FR-2703**: Retificação publicada ou cancelada MUST NOT entrar na seção. A publicada continua no
  cartão "Documentos publicados", sem duplicação.
- **FR-2704**: Edital publicado sem Retificação em curso MUST mostrar a seção com um estado vazio que
  diga que não há Retificação em curso. Edital não publicado e sem Retificação em curso MUST NOT
  mostrar a seção.
- **FR-2705**: A seção MUST ler as Retificações do Edital num número de consultas que não cresce com
  o número de Retificações.

#### Na Lista

- **FR-2706**: Na Lista, a linha de cada Edital com Retificação em curso MUST trazer uma marca por
  Retificação, com a situação e o caminho até o detalhe dela. Quando o ator tem o ato principal da
  situação (FR-2711), a marca MUST nomeá-lo; quando não tem, MUST dizer quem age a seguir.
- **FR-2707**: A Lista MUST ler as Retificações em curso de todos os Editais exibidos num número de
  consultas que não cresce com o número de Editais nem de Retificações.
- **FR-2708**: A marca MUST ser texto legível, e a cor só reforço. Os caminhos novos desta feature
  (marca, seção, edição, ato desabilitado) MUST ser alcançáveis por teclado, e o ato desabilitado
  MUST ter o motivo associado a ele para leitor de tela. A 375 px de largura, nenhuma tela desta
  feature MUST rolar a página para o lado.

#### Na tela de Retificar

- **FR-2709**: A tela de Retificar MUST listar, antes do formulário, as Retificações em curso do
  Edital, com a situação e o caminho até cada uma. Para a que está em elaboração, a quem pode
  elaborar, MUST oferecer continuar a elaboração dela. A tela MUST NOT impedir a criação de outra.

#### No detalhe da Retificação

- **FR-2710**: O detalhe MUST responder às quatro perguntas: onde está (a trilha Processo, Edital,
  Retificação), em que situação, quem age a seguir e o que a pessoa pode fazer.
- **FR-2711**: Quem age a seguir MUST ser derivado só da situação: em elaboração, quem elabora
  (submeter); em revisão, quem homologa (homologar ou devolver); homologada, quem publica (publicar).
  Publicada e cancelada MUST ser ditas encerradas, sem próximo responsável. O responsável MUST ser
  dito por papel, e nunca por pessoa, e nada disso é persistido.
- **FR-2712**: O detalhe MUST dizer se o próximo ato é da própria pessoa, a partir do mesmo conjunto
  de atos oferecidos (FR-2730). Com a segregação (FR-2725), MUST dizer que o ato exige outra pessoa.
- **FR-2713**: O detalhe MUST mostrar quem já atuou: quem criou, quem submeteu, quem homologou e
  quem publicou, com o instante de cada ato que tiver ocorrido.
- **FR-2714**: Uma Retificação em elaboração que já foi devolvida MUST mostrar o motivo da última
  devolução em destaque.
- **FR-2715**: Em elaboração, a quem pode elaborar Retificação, o detalhe MUST oferecer "Editar a
  Retificação".

#### A edição

- **FR-2716**: A edição MUST alterar a mesma Retificação. A identidade, o autor e o instante de
  criação, a base e a trilha MUST ser preservados, e nenhuma Retificação nova MUST ser criada.
- **FR-2717**: O formulário de edição MUST partir do conteúdo proposto: a versão em que a Retificação
  se baseia com as alterações já declaradas aplicadas. A justificativa e a vigência MUST vir
  preenchidas.
- **FR-2718**: A gravação MUST declarar o ato inteiro contra a mesma base: as alterações anteriores
  não tocadas continuam, as tocadas passam a ter o valor novo, as que voltam ao valor vigente saem, e
  o acréscimo removido na edição sai sem virar remoção. O conteúdo que o ato gravado produz MUST ser
  o que a pessoa conferiu; quando não for, a gravação MUST ser recusada sem gravar nada.
- **FR-2719**: As remoções já declaradas MUST ser listadas na edição, cada uma com a opção de
  desfazê-la.
- **FR-2720**: A edição MUST ter conferência antes da gravação, como a criação, dizendo o que muda em
  relação ao rascunho. Só a confirmação grava.
- **FR-2721**: A edição MUST ser oferecida e aceita só em elaboração. Fora dela, MUST recusar com
  situação incompatível, dizendo a situação atual e o caminho (devolver para elaboração). Sem a
  permissão de elaborar, MUST recusar por falta de permissão. Fora do escopo, MUST responder "não
  encontrado".
- **FR-2722**: A tela de edição MUST carregar a revisão da Retificação que mostrou. Se a Retificação
  mudou depois de aberta, a gravação MUST ser recusada sem gravar nada, dizendo que ela foi alterada
  depois de aberta e pedindo para reabrir. O formulário MUST NOT ser interpretado contra um conteúdo
  diferente do que mostrou.
- **FR-2723**: Cada edição gravada MUST registrar na trilha o ator, a permissão de elaborar, a
  operação de edição, a situação e as revisões anterior e posterior. Vale também para a edição pela
  API.
- **FR-2724**: Os gestos de "aplicar a todos" (da `051`) MUST NOT ser oferecidos na edição.

#### Atos, passagem de bastão e segregação

- **FR-2725**: Quando quem submeteu e quem homologou a Retificação são o próprio ator, o detalhe MUST
  mostrar "Publicar Retificação" desabilitado, com o motivo, e não como caminho. A confirmação MUST
  dizer o motivo e MUST NOT oferecer "Confirmar". A regra é a mesma que o servidor aplica, e a
  previsão MUST vir da mesma leitura que o Edital usa.
- **FR-2726**: Quando o ator é quem submeteu, a confirmação de homologar MUST avisar que, homologando,
  a publicação ficará com outra pessoa. O ato MUST continuar disponível.
- **FR-2727**: A recusa MUST dizer qual foi a causa: falta de permissão, segregação de funções ou
  situação incompatível, cada uma com mensagem própria.
- **FR-2728**: A confirmação de submeter, homologar e devolver MUST dizer a quem o ato entrega a
  Retificação, por papel. Depois do ato, o detalhe MUST dizer quem age a seguir.
- **FR-2729**: A devolução, de revisão ou de homologada, MUST levar ao mesmo registro editável, e o
  ciclo devolver, corrigir e submeter MUST poder se repetir até a publicação.
- **FR-2730**: A disponibilidade dos atos MUST ter uma única derivação, usada pela Lista, pelo
  detalhe do Edital, pelo detalhe da Retificação e pela confirmação.

#### O que não muda

- **FR-2731**: Nenhuma permissão, papel, situação ou transição MUST ser criada. As respostas 403, 404
  e 409, a trava da linha com conferência de revisão e a trilha existentes MUST ser preservadas. A
  segregação MUST continuar lendo quem submeteu (FR-021 da `001`, sem reinterpretação).
- **FR-2732**: Nada desta feature MUST criar fila, caixa de entrada, notificação, atribuição a pessoa
  ou estado persistido de passagem de bastão (passagem de bastão como informação, da `007`).

### Key Entities

- **Retificação** (existente): o ato de correção de um Edital publicado, com situação, revisão,
  justificativa, vigência, base e alterações. Nenhum campo novo.
- **Retificação em curso** (derivada): a que está em elaboração, em revisão ou homologada.
- **Próximo responsável** (derivado): o papel que age a seguir, calculado da situação; nunca
  persistido.
- **Registro de edição** (novo tipo de evento na trilha existente): a operação de edição da
  Retificação, com ator e revisões.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-971**: As jornadas de criar, localizar, retomar, editar, submeter, homologar, devolver das
  duas origens, corrigir, reenviar, publicar e cancelar se completam por sessões independentes, cada
  uma com o seu papel, partindo só das seções da barra lateral e sem endereço digitado, em 100% dos
  casos automatizados.
- **SC-972**: Os quatro casos da auditoria marcados como falha esperada passam sem a marca, com as
  asserções originais.
- **SC-973**: Em todas as combinações testadas de papel e situação, a tela oferece exatamente os atos
  que o servidor aceita, e mostra desabilitado, com o motivo, o que a segregação recusa.
- **SC-974**: O número de consultas da Lista e do detalhe do Edital é o mesmo com uma e com cinco
  Retificações em curso, e com um e com três Editais.
- **SC-975**: Depois de duas devoluções, a mesma Retificação, com o mesmo identificador, chega à
  publicação; o Edital termina com uma Retificação, e não três.
- **SC-976**: Em 100% dos casos de edição concorrente testados, nenhuma gravação sobrescreve outra em
  silêncio.
- **SC-977**: A suíte completa contra PostgreSQL não tem regressão em relação à `main`.
- **SC-978**: Repetida a jornada da reunião de 29/10 com três pessoas, cada uma no seu papel, nenhuma
  precisa de URL copiada nem de ajuda para chegar ao seu ato.

---

## Assumptions

- O público de leitura das Retificações em curso é o mesmo que já abre o detalhe da Retificação: todo
  ator autenticado do escopo da unidade.
- A Lista é a primeira tela do dia de quem homologa e de quem publica, que não têm etapa de comissão
  a avaliar. "Minhas Etapas" é a mesa da comissão, e não o lugar da Retificação.
- Retificações em curso são poucas por Edital, e a marca na Lista não precisa de paginação própria.
- O conteúdo proposto de uma Retificação é reproduzível: aplicar as alterações gravadas à base
  produz sempre o mesmo conteúdo.

---

## Decisões

### D-001 — A devolvida se reabre na tela, e a edição reescreve o ato inteiro

A tela edita o mesmo registro pelo comando de edição que já existe, que substitui o conjunto de
alterações. O formulário parte do conteúdo proposto, e a gravação compõe o ato inteiro contra a base:
as alterações já declaradas e a diferença da edição se fundem caminho a caminho. A fusão é conferida
pelo resultado: aplicar o ato gravado à base precisa produzir exatamente o conteúdo conferido, e se
não produzir a gravação é recusada. A alternativa "devolver é recompor" foi recusada pelo pedido: ela
deixa uma Retificação morta em elaboração a cada devolução.

### D-002 — A descoberta mora no detalhe do Edital e na linha da Lista

A seção "Retificações em curso" no detalhe do Edital é o primeiro nível. O segundo é uma marca na
linha do Edital, na Lista, que diz a situação e o ato que cabe à pessoa. "Minhas Etapas" foi
descartada: é a mesa da comissão, e homologador e publicador não a usam. Estender o próximo passo do
Edital foi descartado: ele fala do Edital, e o Edital publicado não tem próximo ato. A Lista já é a
tela que todos abrem, e a marca custa uma consulta por página.

### D-003 — O próximo responsável é derivado da situação, e o "é você" do conjunto de atos

A tabela é da Retificação, porque as situações têm nomes próprios ("homologada", e não "homologado"),
mas a entrega de cada ato reaproveita a do Edital, que é chaveada pelo ato e tem as mesmas chaves.
"É você" sai do mesmo conjunto de atos que a tela oferece, para que a frase e o botão não divirjam.

### D-004 — A segregação antecipada é a do Edital, com os nomes da Retificação

As duas leituras que o Edital usa recebem só quem elaborou e quem homologou. A Retificação as chama
com quem submeteu e quem homologou. A regra continua escrita uma vez no servidor; a tela só a
antecipa. A interpretação da FR-021 da `001` não muda (AUD-RET-05).

### D-005 — Não há unicidade

Duas Retificações em curso no mesmo Edital são legítimas: podem tratar de assuntos diferentes, e a
publicação já confere conflito de conteúdo entre elas. A tela de Retificar mostra as existentes antes
do formulário, e oferece continuar a que está em elaboração.

### D-006 — A edição entra na trilha

O comando de edição não registrava evento. A Constituição (Princípio III) pede auditoria de operação
sensível, e mudar o conteúdo normativo de um ato em preparação é uma. O evento leva o ator, a
permissão, a situação e as duas revisões. Ele não muda a segregação, que continua lendo quem submeteu,
mas deixa escrito quem compôs, o que informa a pergunta do AUD-RET-05.

### D-007 — A revisão viaja no formulário, e a divergência recusa antes de interpretar

O formulário identifica os campos por posição no conteúdo que mostrou. Interpretá-lo contra um
conteúdo que mudou trocaria um campo por outro. Por isso a revisão é conferida antes de ler o
formulário, e de novo na gravação, pela comparação e troca do comando. Nada se mescla com a edição de
outra pessoa.

### D-008 — Sem gestos de "aplicar a todos" na edição

O gesto é registrado na trilha como ato próprio ao criar. Na edição, ele teria de ser conciliado com
o que o rascunho já declara, e a fusão de D-001 cobre alterações, e não gestos. A pessoa edita os
campos um a um. Se o uso pedir o gesto na edição, é feature própria.

---

## Pendências do usuário

- **AUD-RET-05.** Na FR-021 da `001`, "elaborou" quer dizer quem submeteu ou quem compôs? A resposta
  vale para o Edital e para a Retificação. O teste de caracterização
  `test_caracterizacao_quem_so_compos_conclui_se_outra_pessoa_submeter` continua passando como está;
  a trilha passa a registrar quem editou (D-006), o que dá à governança o dado para decidir.
- **Reapontar a base pela tela.** O comando aceita trocar a base de uma Retificação em elaboração; a
  tela não oferece. Se outra Retificação for publicada antes, a publicação recusa por conflito, e a
  saída hoje é compor outra.
- **A trilha grava a permissão, e não o papel** (registrado pela auditoria). Sem mudança aqui.
- **SC-978** espera uma sessão com pessoas reais.
