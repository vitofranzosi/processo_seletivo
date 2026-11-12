# Feature Specification: O desfecho da convocação comunicado ao candidato

**Feature Branch**: `claude/intelligent-robinson-4466a5`, sobre a `main` em `d1ec1e0a` (com a `154`, PR #479, mergeada)

**Created**: 2026-11-11

**Status**: **Rascunho, só a spec.** Não há plano, tarefas nem código. As propostas de desenho
(D-001 a D-014, ao fim) estão sujeitas à revisão do PR, e as **nove perguntas ao usuário** (P-1 a
P-9, em *Perguntas ao usuário*) estão abertas. Onde uma pergunta está aberta, o texto adota a
recomendação dela, marcada como tal, para que a spec continue coerente; a resposta pode trocá-la.

**Input**: o [estudo da jornada final](../../doc/estudo-jornada-final-2026-11-11/index.html) de
11/11/2026 (PR #472), achados **07**, **17** e **18**, os três de prioridade média, e a orientação
do usuário de 11/11/2026, transcrita:

> "avance na especificação do que aparece no portal e do que será comunicado por aviso. Identifique
> exatamente qual validação de LGPD falta e quais partes ela impede. Essa dependência deve
> condicionar a habilitação do envio correspondente, sem paralisar todo o tratamento dos achados."

O que o estudo observou, no Edital de treinamento SIM09/2026 (C09):

- **achado 07** (etapas E e F; evidências `F14-portal-alice-aceite`, `E05-portal-cecilia-desistencia`,
  `E11-portal-davi-nao-atendimento`): aceite, desistência, não atendimento e indeferimento não geram
  e-mail; só chegaram à caixa a convocação, o código de acesso e o aviso de pendência. Quem foi
  aceito lê *"Vaga aceita… Os próximos passos são os que o Edital indica"* e não sabe o que vem
  depois nem quem vai procurá-lo; quem perdeu a vaga só descobre entrando no portal.
- **achado 17** (etapas B e E; evidências `B04-convocacao-portal`, `E05-portal-cecilia-desistencia`):
  o portal não tem como desistir, e o campo *"Atendimento"* mostra só *"o atendimento
  institucional"*, sem endereço nem telefone. A desistência chega por canal informal, e a comissão a
  registra sem prova no sistema.
- **achado 18** (etapas B e E; evidências `B01-email-convocacao`, `E11-portal-davi-nao-atendimento`):
  fundamentos em jargão — *"na faixa vigente deste recorte"*, *"o vencimento… decorreu sem desfecho
  registrado"* —, e o e-mail diz *"contado do envio desta mensagem"* para um prazo que é data fixa.

> **Faixa de identificadores.** Esta spec abre em **FR-6400**, **SC-2120** e **UX-620**, reservados
> para ela até o requisito seis mil quatrocentos e quarenta e nove, o critério dois mil cento e
> trinta e nove e o requisito de experiência seiscentos e trinta e nove, na nota de reserva das
> sessões de 11/11/2026. Na mesma data a `155` reservou de seis mil e trezentos a seis mil trezentos e
> quarenta e nove, e a `154` (PR #479, mergeado em 12/11) usou até seis mil duzentos e dezesseis. As decisões reiniciam
> em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3750 da `118`"). Uma decisão de outra feature é citada pelo assunto e pela
> feature, nunca pelo número. Os achados do estudo são citados como "achado 07", sem prefixo,
> porque o identificador com hífen seria lido como requisito de experiência desta base.

---

## Por que esta feature existe

**O desfecho é o ato que mais importa ao candidato, e é o único que o sistema não conta a ele.** A
convocação sai por e-mail (`019`, quando o Edital comunica por mensagem); a pendência documental
também (`134`). O resultado da convocação — a vaga aceita, a desistência, o não atendimento, o
indeferimento — fica no portal, à espera de que a pessoa volte. Quem perdeu a vaga descobre tarde;
quem a ganhou não sabe o que fazer.

**O que o portal diz depois do desfecho é o fundamento do ato, e não uma explicação.** A FR-1172 da
`063` mandou o porquê trazer o fundamento e a data do registro, e o fundamento é texto de ato: o da
convocação é derivado da norma (*"…dentro das vagas que a apuração de ocupação emitida em ‹data›
considerou, na faixa vigente deste recorte"*), e o do não atendimento também (*"a comunicação foi
enviada e o vencimento informado no ato da convocação decorreu sem desfecho registrado"*). Os dois
estão certos como motivação do ato, e ninguém fora da comissão os entende. O aceite troca o
fundamento por uma frase que não diz nada (*"Os próximos passos são os que o Edital indica"*).

**Desistir não tem caminho, e por isso não tem prova.** A desistência expressa existe como espécie
de desfecho desde a `019`, mas só a comissão a registra, a partir do que a pessoa disse por um canal
que o sistema não vê. O registro fica sem a manifestação que o fundamenta.

**O contato existe, e não chegou à tela do estudo.** O canal de atendimento é da unidade (FR-3211 da
`109`), recai no `PORTAL_ATENDIMENTO` da instalação (FR-3214 da `109`), que a produção exige, e só
na falta dos dois vira a frase genérica *"o atendimento institucional"*. O banco do estudo não tinha
nenhum dos dois. Em produção a linha teria um canal — mas um canal só, em uma linha, que pode não
ser o da comissão que conduz o certame. A parte do achado 17 que é de ambiente não se resolve aqui;
a que é de tela, sim.

**O e-mail, a parte que depende de terceiro.** O aviso por e-mail usa o endereço da pessoa para uma
finalidade que o Edital não declara, e a `066` deixou registrado que esse uso espera validação
institucional de LGPD antes de produção (decisão 10 da `066`; a chave da decisão de habilitação da
`066`). O resto desta spec — o portal, a desistência, o texto do e-mail que já sai — não espera por
ela. A orientação do usuário pede justamente essa separação.

### O que esta spec cobre, e o que fica fora

**Cobre:**

1. **O portal em cada desfecho**: a frase simples por espécie, o fundamento do ato recolhido, o
   próximo passo real do aceite e da regularização, o caminho para recorrer quando o Edital o prevê, e
   o contato. Também a convocação ainda sem desfecho, nas duas camadas.
2. **O texto da mensagem da convocação**, que deixa de dizer *"contado do envio desta mensagem"*.
3. **A desistência pelo portal**, como pedido registrado que a comissão homologa ao registrar o
   desfecho.
4. **O aviso do desfecho por e-mail**: quais desfechos, quando, com que texto, por qual despacho.
5. **A dependência de LGPD**, nomeada, e a habilitação que ela condiciona.

**Fica fora:**

- O título, a frase de conclusão, a advertência e o nome do reenviado das chamadas abertas: são da
  `154` (PR #479, mergeado), e esta spec parte do que ela decidiu, sem refazer. A FR-6206 da `154`
  manteve a tela com desfecho como a da FR-3750 da `118`; esta spec revê a FR-3750 e mantém o que a
  FR-6206 exige — o título, o rótulo e, no aceite, a frase de que o registro não é matrícula, bolsa
  nem contrato.
- O recurso contra o indeferimento dentro do sistema (a questão institucional `QI-6` da `115`):
  esta spec só aponta para o que o Edital diz.
- A confirmação de recebimento pelo setor de formalização e o vínculo formalizado (`117`): o GPS
  continua parando em *disponibilizado*.
- Vocabulário por natureza da seleção (curso, bolsa, contratação) nos desfechos: spec própria,
  registrada pela `152`.
- O aviso aos que tiveram desfecho **antes** da habilitação ser ligada (D-011).
- Recibo por e-mail do pedido de desistência (D-008).
- Canais além do e-mail, descadastro e rastreio de abertura (fora pela `066`).
- O dado do canal em cada ambiente: preencher o canal das unidades e o `PORTAL_ATENDIMENTO` é
  configuração, e não requisito.

---

## A dependência de LGPD, nomeada

Esta seção responde à orientação do usuário: qual validação falta, de quem, sobre qual tratamento,
e o que ela impede.

### Qual validação

**O parecer do Encarregado pelo Tratamento de Dados Pessoais do Ifes** (art. 41 da LGPD), em nome do
controlador, que é o Ifes, sobre o tratamento descrito abaixo. É a mesma *"validação institucional,
com o encarregado de dados"* que a `066` registrou como precondição de produção e que a `134`
herdou; esta spec pede que ela cubra **uma finalidade a mais**, e a nomeia. Nada indica, no
repositório, que esse parecer tenha sido pedido ou emitido (P-3).

Ao lado dela, e **independente dela**, continua pendente a validação da infraestrutura de correio
(SPF e DKIM do remetente), que a `066` e a `134` também exigem. Não é LGPD, e a habilitação depende
das duas (FR-6440).

### Sobre qual tratamento

| | O que é |
|---|---|
| **Dado tratado** | o endereço de e-mail da pessoa convocada, na ordem que a `066` usa (a credencial verificada pelo código de acesso antes do endereço da inscrição); o número e o ano do Edital; o instante do registro; e, por consequência do próprio envio, **o fato de que esta pessoa foi convocada e teve o resultado da convocação registrado**. Com o texto recomendado (P-1), o corpo não leva a espécie do desfecho, o motivo, o nome, o CPF, a modalidade nem a posição |
| **Dado que o texto recomendado evita** | a espécie do desfecho (*indeferido*, *não atendida*), que é resultado individual, e que no indeferimento de quem concorre por reserva de vagas pode revelar, por inferência, dado sensível (art. 5º, II, e art. 11 da LGPD) — a razão pela qual a decisão 5 da `066` tirou o resultado individual do corpo do aviso |
| **Finalidade** | avisar a pessoa de que há resultado registrado da sua convocação, para que ela o consulte no portal e cumpra a providência seguinte que o Edital indica, ou exerça no prazo o direito de recorrer que o Edital preveja. O aviso não é o ato, não intima e não altera prazo nem resultado |
| **Base legal** | **a definir pelo parecer**. As hipóteses que ele deve confirmar ou afastar: o art. 7º, III, com o art. 23 (tratamento pelo poder público para executar política pública e atribuição legal do serviço público); e o art. 7º, II (cumprimento de obrigação legal), se o parecer entender que o dever de dar ciência ao interessado dos atos que restringem direito (Lei nº 9.784/1999, art. 26 e 28) alcança este aviso. A spec **não** propõe consentimento: entre poder público e candidato ele não é livre, e o aviso deixaria de alcançar quem não respondesse |
| **Operador** | o serviço de correio que transmite a mensagem. Se for de terceiro, o parecer diz se o contrato o cobre |
| **Retenção** | o registro do aviso e de cada destinatário, que a `066` guarda; a política de retenção é a mesma que a PC-003 da `010` já exige do portal, e continua pendente |
| **Direitos do titular** | se a base legal escolhida exigir direito de oposição, o descadastro entra como incremento, como a `066` já previa |

### O que ela impede

**Só o envio do aviso do desfecho por e-mail**: a opção de avisar, no registro do desfecho, e a
saída da mensagem pelo despacho. Com a habilitação desligada, a opção não aparece, nada é gravado, e
o despacho não tem o que enviar (FR-6430, FR-6437 e FR-6438).

### O que ela não impede

| Parte desta spec | Por que não depende do parecer |
|---|---|
| O portal em cada desfecho, nas duas camadas (§A a §C) | Mostra à própria pessoa, autenticada, o que o sistema já mostra a ela hoje, em outras palavras. Nenhum dado novo, nenhuma finalidade nova |
| O contato da comissão (§D) | É dado institucional, e não pessoal |
| A desistência pelo portal (§E e §F) | É manifestação da pessoa no próprio procedimento do certame, pela mesma via e com a mesma base em que ela se inscreveu e envia documentos. Sem campo de motivo (D-007), não coleta dado novo. A PC-003 da `010` vale para ela como vale para o resto do portal |
| O texto corrigido da mensagem da convocação (§G) | A mensagem já sai, na terceira situação da FR-084 da `010`, que é o próprio ato; a correção muda a redação, e não o tratamento |
| A implementação e os testes do aviso | A chave vem ligada em `development` e `test`, como a da `066`; tudo pode ser construído e verificado antes do parecer |

---

## User Scenarios & Testing *(mandatory)*

Os cenários são os do estudo, no SIM09/2026 (C09): **Alice**, aceita; **Cecília**, que desistiu;
**Davi**, que não atendeu no prazo. Acrescentam-se **Elisa**, indeferida por documento, e **Fábio**,
que pede a desistência pelo portal. Dados fictícios.

### User Story 1 — Quem foi aceito sabe o que vem depois e a quem perguntar (Priority: P1)

Alice teve a vaga aceita. Ao abrir a convocação, ela lê que a comissão registrou o resultado, que
isso ainda não é a matrícula, onde o Edital diz como será a próxima etapa — com o caminho até lá — e
com quem falar se tiver dúvida.

**Why this priority**: é o achado 07 na pessoa que mais precisa agir. A frase de hoje deixa o próximo
passo para uma busca no Edital.

**Independent Test**: no C09, reproduzir `F14-portal-alice-aceite` e conferir a frase, o caminho para
a seção do Edital e o contato, sem abrir o fundamento.

**Acceptance Scenarios**:

1. **Given** Alice com aceite, num Edital cujo texto publicado tem a seção da matrícula preenchida,
   **When** ela abre a convocação ou o acompanhamento, **Then** lê *"Vaga aceita"*, a frase simples do
   aceite, o caminho para a seção do Edital que diz como será a matrícula e o contato.
2. **Given** um Edital cuja seção da matrícula está vazia, **When** Alice abre a convocação, **Then** a
   frase diz que o próximo passo é o que o Edital publica, sem caminho para seção, e o contato aparece.
3. **Given** Alice com aceite, **When** ela lê a página, **Then** nada diz *matriculado*, *contratado*,
   *bolsa concedida*, *encaminhado* nem *apto para formalização*.
4. **Given** a regularização registrada, **When** a pessoa abre a convocação, **Then** a frase é a da
   regularização, e o próximo passo e o contato são os do aceite.

---

### User Story 2 — Quem perdeu a vaga entende por quê, em uma frase (Priority: P1)

Davi não atendeu no prazo. Ao abrir a convocação, ele lê, em linguagem simples, que o prazo terminou
na data tal sem que a convocação fosse atendida, que a comissão registrou isso e que a convocação está
encerrada para ele. O fundamento do ato continua lá, recolhido, para quem quiser lê-lo.

**Why this priority**: é o achado 18. O fundamento técnico como única explicação deixa a pessoa sem
saber o que aconteceu.

**Independent Test**: para cada uma das sete espécies de desfecho, a tela mostra a frase simples da
tabela da FR-6406 e o fundamento recolhido; nenhum termo da lista da FR-6403 aparece fora do
fundamento.

**Acceptance Scenarios**:

1. **Given** Davi com não atendimento, **When** ele abre a convocação, **Then** lê *"Convocação não
   atendida"* e a frase simples, com a data do fim do prazo; o fundamento está recolhido sob
   *"Fundamento do registro"*.
2. **Given** Elisa com indeferimento, num Edital que publica como recorrer, **When** ela abre a
   convocação, **Then** a frase diz que a comissão registrou o indeferimento, que o motivo está no
   fundamento, e oferece o caminho para a seção do Edital que diz como recorrer.
3. **Given** Cecília com desistência registrada, **When** ela abre a convocação, **Then** a frase diz
   que a comissão registrou a desistência dela, em que data, e que a convocação está encerrada para
   ela.
4. **Given** qualquer desfecho, **When** a pessoa abre o fundamento recolhido, **Then** lê o texto
   gravado no ato, palavra por palavra, com a data do registro.

---

### User Story 3 — A convocação ainda aberta diz por que a pessoa foi chamada (Priority: P2)

Antes de qualquer desfecho, a página da convocação diz em uma frase por que a pessoa foi chamada —
porque a posição dela está dentro das vagas, ou porque uma vaga ficou livre — e recolhe o fundamento
derivado da norma.

**Why this priority**: o mesmo jargão do achado 18, numa tela que a pessoa lê antes de agir.

**Independent Test**: para cada espécie de convocação, a tela mostra a frase simples e o fundamento
recolhido; *"faixa vigente"* e *"recorte"* não aparecem fora dele.

**Acceptance Scenarios**:

1. **Given** uma convocação para vaga inicial, **When** a pessoa abre a convocação, **Then** lê que foi
   chamada porque a posição dela na lista está dentro das vagas da lista.
2. **Given** uma convocação para vaga que vagou, **Then** lê que foi chamada porque uma vaga da lista
   ficou livre e ela é a próxima na classificação.
3. **Given** o complemento do fundamento escrito por quem convocou, **Then** ele aparece dentro do
   fundamento recolhido, depois do texto derivado, como hoje.

---

### User Story 4 — O contato é o da comissão, e não uma frase (Priority: P1)

Na convocação, no resultado e no aviso, a pessoa lê o canal de atendimento da unidade que conduz o
certame, como link. Se não houver canal nenhum — o que só acontece fora de produção —, a linha não
aparece, em vez de dizer *"o atendimento institucional"*.

**Why this priority**: é o achado 17, na parte que é de tela. Mandar procurar sem dizer onde é
abandonar quem pediu ajuda (o comentário de `_atendimento.html` já o diz).

**Independent Test**: com o canal da unidade preenchido, a convocação, o resultado e o aviso o
mostram; sem canal nenhum, a linha *"Atendimento"* some e nenhuma tela da convocação diz *"o
atendimento institucional"*.

**Acceptance Scenarios**:

1. **Given** a unidade com canal *selecao@unidade.exemplo.test*, **When** a pessoa abre a convocação,
   **Then** a linha *"Atendimento"* traz o endereço, como link de e-mail.
2. **Given** a unidade sem canal e a instalação com `PORTAL_ATENDIMENTO`, **Then** a linha traz o da
   instalação.
3. **Given** nenhum dos dois, **Then** a linha não aparece, e a frase *"fale com o atendimento"*
   também não.

---

### User Story 5 — Fábio pede a desistência pelo portal (Priority: P2)

Fábio foi convocado e não quer a vaga. No fim da página da convocação há *"Desistir desta
convocação"*. A página seguinte diz o que o pedido faz e o que não faz, pede que ele confirme que
entendeu, e registra o pedido com data, hora e protocolo. A convocação passa a dizer que o pedido foi
enviado e que a comissão vai registrá-lo; até lá, ele pode cancelar o pedido (P-6).

**Why this priority**: é o achado 17, na parte de capacidade. Sem o pedido, a desistência chega por
canal informal e o desfecho fica sem a manifestação que o fundamenta.

**Independent Test**: Fábio pede a desistência; a página mostra o pedido com protocolo; a comissão o
vê; a trilha tem o pedido, sem endereço; nenhum desfecho foi registrado.

**Acceptance Scenarios**:

1. **Given** Fábio com convocação sem desfecho e visível no portal, **When** ele aciona *"Desistir
   desta convocação"*, **Then** vê a página de confirmação, com o que acontece e sem campo de motivo.
2. **Given** a página de confirmação, **When** ele confirma sem marcar a ciência, **Then** o pedido é
   recusado, e nada é gravado.
3. **Given** a ciência marcada, **When** ele confirma, **Then** o pedido é gravado com instante,
   credencial e protocolo, e a convocação diz *"Pedido de desistência enviado em ‹data e hora›. A
   comissão vai registrá-lo."*.
4. **Given** o pedido pendente, **When** Fábio abre a convocação, **Then** o envio de documentos não é
   oferecido, e o prazo continua visível com a frase de que o pedido não o suspende (P-7).
5. **Given** o pedido pendente, **When** Fábio aciona *"Cancelar o pedido de desistência"* e confirma,
   **Then** o cancelamento é gravado, e a convocação volta a ser a de antes (P-6).
6. **Given** um duplo clique na confirmação, **Then** um pedido só é gravado.

---

### User Story 6 — A comissão homologa o pedido ao registrar a desistência (Priority: P2)

O cartão de Fábio na condução da convocação diz *"Pedido de desistência pelo portal em ‹data›"* e
oferece *"Registrar a desistência pedida"*, que abre o registro do desfecho com a desistência
expressa escolhida e o fundamento derivado do pedido. Confirmado, o desfecho é o de sempre, e cita o
pedido.

**Why this priority**: sem a homologação, o pedido seria um desfecho automático, que a orientação
proíbe e a regra de um desfecho por convocação (FR-273 da `019`) não admite fora da comissão.

**Independent Test**: com um pedido pendente, a comissão registra a desistência pelo atalho; o
desfecho cita o protocolo do pedido; o pedido passa a homologado; o portal mostra o resultado.

**Acceptance Scenarios**:

1. **Given** um pedido pendente, **When** a comissão abre a condução do recorte, **Then** o cartão
   mostra o pedido e o atalho, e o *"O que fazer agora"* traz a providência *"Registrar a desistência
   pedida pelo portal"*.
2. **Given** o atalho, **When** quem pode registrar desfecho confirma, **Then** o desfecho é a
   desistência expressa, com o fundamento que cita data, hora e protocolo do pedido, e o pedido fica
   homologado.
3. **Given** um pedido pendente, **When** a comissão registra outro desfecho, **Then** a confirmação
   avisa que há pedido de desistência pendente e pede ciência; registrado, o pedido fica encerrado
   por outro desfecho.
4. **Given** um pedido pendente e o vencimento passado, **When** a comissão aciona o registro do não
   atendimento dos vencidos, **Then** a pessoa com pedido fica de fora, contada como *"pedido de
   desistência pendente"*.

---

### User Story 7 — O resultado chega por e-mail, quando a habilitação estiver ligada (Priority: P3)

Com a habilitação ligada, quem registra o desfecho vê, na confirmação, *"Avisar a pessoa por
e-mail"*, marcado (P-8). Confirmado, o aviso é gravado no registro de avisos e o despacho da `066` o
envia: um e-mail neutro (P-1) que diz que o resultado da convocação no Edital tal foi registrado e
traz o link da convocação e o contato. Com a habilitação desligada, nada disso aparece, e o portal é
o mesmo.

**Why this priority**: é a parte do achado 07 que depende do parecer. Vem por último porque a
habilitação não depende desta equipe, e tudo o mais funciona sem ela.

**Independent Test**: com a habilitação ligada, registrar um aceite com a opção marcada grava um
aviso, e `despachar_avisos` o envia; com ela desligada, a opção não aparece e nada é gravado.

**Acceptance Scenarios**:

1. **Given** a habilitação ligada, **When** a comissão registra o desfecho com a opção marcada, **Then**
   um aviso é gravado para a pessoa, na mesma transação, e nenhuma mensagem sai na requisição.
2. **Given** o aviso gravado, **When** o despacho corre, **Then** a mensagem sai com o assunto e o
   corpo das FR-6433 a FR-6435.
3. **Given** o aviso gravado, **When**, antes do despacho, a convocação é corrigida por sucessão e o
   desfecho deixa de ser o vigente, **Then** o despacho o interrompe, com o motivo.
4. **Given** a habilitação desligada, **When** a comissão registra o desfecho, **Then** a confirmação
   não oferece a opção, e nenhum aviso é gravado.
5. **Given** o registro do não atendimento dos vencidos em lote, com a habilitação ligada, **When** a
   comissão o confirma com a opção marcada, **Then** um aviso por pessoa é gravado.

---

### User Story 8 — O e-mail da convocação diz o prazo como ele é (Priority: P2)

A mensagem da convocação e a da correção dizem *"Prazo para atender: até ‹data por extenso›."*, sem
*"contado do envio desta mensagem"*.

**Why this priority**: é o achado 18 no e-mail. A cláusula sugere prazo novo a cada reenvio
(`doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`), e o prazo é a data informada no ato.

**Independent Test**: as mensagens novas, inicial e de correção, em texto puro e em HTML, não contêm
*"contado do envio"*; as já enviadas não mudam.

**Acceptance Scenarios**:

1. **Given** uma convocação comunicada por mensagem, **When** a mensagem sai, **Then** a linha do prazo
   é *"Prazo para atender: até ‹data por extenso›."*.
2. **Given** a correção, **Then** a linha é *"Prazo válido para atender: até ‹data por extenso›."*.

---

### Edge Cases

- **Desfecho sem fundamento digitado**: as espécies que a comissão registra têm fundamento
  obrigatório (`019`); o não atendimento em lote tem o derivado. Não há desfecho sem fundamento a
  recolher.
- **Inércia**: a frase simples cita o fato atestado em linguagem simples (FR-6407); o atestado
  continua no fundamento.
- **Reclassificação**: a frase não promete nova chamada; diz que a convocação está encerrada e que o
  que acontece depois é o que o Edital diz (FR-6406).
- **Edital sem a seção da matrícula ou sem a de recursos**: nenhuma frase aponta para seção vazia
  (FR-6411, FR-6414).
- **Convocação corrigida por sucessão** depois do pedido de desistência: o pedido é da chamada e
  acompanha a convocação vigente (D-009).
- **Pedido de desistência com a convocação por publicação ainda não publicada** (o estado *K-pub* da
  `125`): a convocação não aparece no portal, e o pedido não é oferecido.
- **Pedido depois do vencimento**: admitido enquanto não houver desfecho (D-010).
- **Processo encerrado ou cancelado**: o pedido e o cancelamento são recusados; o pendente continua
  visível à comissão.
- **Pessoa sem endereço**, com a habilitação ligada: não há aviso, e a confirmação do desfecho diz que
  a pessoa não será avisada por falta de endereço.
- **Desfecho registrado com a habilitação desligada, e ela ligada depois**: nenhum aviso retroativo
  (D-011).
- **Duas sessões do mesmo candidato** pedindo ao mesmo tempo: um pedido só, pela trava da convocação.
- **O fundamento digitado expõe outra pessoa**: a regra da `125` continua — o campo diz que o texto será
  mostrado ao candidato; recolhido não quer dizer escondido.

---

## Requirements *(mandatory)*

### Functional Requirements

#### A. As duas camadas

- **FR-6400**: Toda tela do portal que mostra um desfecho de convocação ou o fundamento de uma
  convocação MUST mostrar primeiro a **frase simples** desta spec e, depois dela, o **fundamento do
  ato** recolhido, sob o rótulo *"Fundamento do registro"* (desfecho) ou *"Fundamento da convocação"*
  (convocação), aberto por gesto da pessoa e legível sem script.
- **FR-6401**: O fundamento recolhido MUST ser o texto gravado no ato, sem edição, com a data do
  registro, o complemento depois do texto derivado como hoje, e nada além disso.
- **FR-6402**: A frase simples MUST ser derivada da espécie e dos dados do ato no momento da leitura, e
  MUST NOT ser gravada no ato. Ato já gravado MUST NOT mudar (Princípio da imutabilidade; 8ª decisão
  da `154`).
- **FR-6403**: Fora do fundamento recolhido, as telas do portal da convocação e do desfecho MUST NOT
  conter *"faixa vigente"*, *"recorte"*, *"apuração"*, *"decorreu"*, *"desfecho registrado"*,
  *"vencimento informado no ato"* nem *"espécie"*. A varredura de vocabulário da `063` MUST alcançar
  as frases desta spec.
- **FR-6404**: A tela de quem registra o desfecho e a de quem convoca MUST continuar mostrando o
  fundamento como hoje; as duas camadas são do portal.

#### B. O portal em cada desfecho

- **FR-6405**: O rótulo de cada desfecho MUST continuar o da tabela da FR-1172 da `063`, e o título da
  página o da FR-3858 da `121` (*"Resultado da sua convocação"*), como a `154` o deixou.
- **FR-6406**: A frase simples de cada desfecho MUST ser a desta tabela, com ‹data› a data local do
  registro e ‹fim do prazo› o vencimento da convocação vigente:

  | Desfecho | Frase simples |
  |---|---|
  | Aceite | *"A comissão registrou o resultado da sua convocação em ‹data›. Este registro ainda não é a matrícula, a bolsa nem o contrato."*, seguida do próximo passo (FR-6410 a FR-6413) |
  | Regularização | *"A comissão registrou a regularização da sua situação nesta convocação em ‹data›. Este registro ainda não é a matrícula, a bolsa nem o contrato."*, seguida do próximo passo |
  | Indeferimento | *"A comissão registrou o indeferimento desta convocação em ‹data›: ela concluiu que o que o Edital pede nesta etapa não foi cumprido. O motivo está no fundamento, abaixo."*, seguida do caminho para recorrer (FR-6414) |
  | Desistência expressa | *"A comissão registrou a sua desistência desta convocação em ‹data›. Esta convocação está encerrada para você."* |
  | Não atendimento | *"O prazo desta convocação terminou em ‹fim do prazo› sem que ela fosse atendida, e a comissão registrou isso em ‹data›. Esta convocação está encerrada para você."* |
  | Cancelamento por inércia | *"A comissão registrou o cancelamento em ‹data›, porque ‹fato atestado, FR-6407›. Esta convocação está encerrada para você."* |
  | Reclassificação | *"A comissão registrou a sua reclassificação em ‹data›. Esta convocação está encerrada para você; o que acontece depois é o que o Edital diz."* |

- **FR-6407**: No cancelamento por inércia, o fato atestado MUST ser dito assim: *"não houve acesso ao
  ambiente do curso"*, *"não houve presença na primeira semana do curso"* e *"a entrega presencial não
  foi feita"*, uma por espécie de atestado da `019`.
- **FR-6408**: Nenhuma frase desta spec MUST afirmar perda definitiva de vaga, nova chamada, posição na
  lista ou consequência que nenhum ato declarou. *"Esta convocação está encerrada para você"* diz o
  efeito do desfecho registrado sobre a chamada, e não sobre o certame.
- **FR-6409**: A FR-1177 da `063` MUST ser revista para dizer que a frase simples de um desfecho
  **registrado** descreve o ato, e não é frase de consequência; a regra das duas frases neutras
  continua valendo antes do desfecho.

#### C. O próximo passo do aceite e da regularização

- **FR-6410**: Com aceite ou regularização, a página MUST dizer o próximo passo depois da frase
  simples, no lugar de *"Os próximos passos são os que o Edital indica."* (FR-3750 da `118`, revista).
- **FR-6411**: Quando o texto publicado do Edital vigente tiver a seção da matrícula não vazia (*"Da
  Matrícula"*, ou *"Como será a matrícula?"* no catálogo da `069`), o próximo passo MUST ser *"O
  Edital diz como será a próxima etapa em «‹título da seção›»."*, com o caminho para essa seção na
  página pública do Edital. *(Adota a recomendação de P-4.)*
- **FR-6412**: Sem essa seção, o próximo passo MUST ser *"A próxima etapa é a que o Edital publica."*,
  sem caminho para seção.
- **FR-6413**: O próximo passo MUST terminar com *"Se tiver dúvida sobre a próxima etapa, fale com
  ‹contato›."* quando houver canal (FR-6415), e MUST NOT nomear setor, pessoa ou data que o Edital não
  publique, nem dizer que a documentação foi disponibilizada a alguém. *(Adota a recomendação de
  P-9.)*
- **FR-6414**: Com indeferimento, quando o texto publicado do Edital tiver a seção de recursos não
  vazia, a página MUST dizer *"O Edital diz se e como recorrer em «‹título da seção›»."*, com o
  caminho para ela; sem a seção, nada sobre recurso.

#### D. O contato

- **FR-6415**: O contato MUST ser o canal de atendimento da unidade do Edital, com a recaída da FR-3214
  da `109`, mostrado como link (e-mail ou endereço) na convocação, no resultado e no aviso.
  *(Adota a recomendação de P-5.)*
- **FR-6416**: Sem canal nenhum, a linha *"Atendimento"* e a frase *"fale com o atendimento"* MUST NOT
  aparecer nas telas da convocação e do resultado, e nenhuma delas MUST dizer *"o atendimento
  institucional"*. As outras telas do portal que usam a frase genérica não mudam.
- **FR-6417**: Os cenários de treinamento da `134` MUST declarar um canal fictício na unidade que
  usam, para que os estudos vejam o contato como em produção.

#### E. A desistência pelo portal: o pedido

- **FR-6418**: A página da convocação MUST oferecer *"Desistir desta convocação"* à pessoa cuja
  convocação vigente está visível no portal, sem desfecho e sem pedido pendente, com o Processo fora de
  estado final. A oferta MUST ser link secundário, no fim da página, e nunca a ação principal.
- **FR-6419**: O link MUST levar a uma página de confirmação que diga, nesta ordem: que o pedido vai
  à comissão, que registra a desistência; que, registrada, a desistência encerra a convocação e não
  se desfaz pelo portal; que o pedido não suspende nem prorroga o prazo; e que, até o registro, o
  pedido pode ser cancelado (P-6). A página MUST pedir a ciência, numa caixa a marcar, e MUST NOT ter
  campo de motivo nem texto livre.
- **FR-6420**: O pedido MUST ser gravado com a convocação, a inscrição, a credencial que o fez, o
  instante e um protocolo, em registro que não se altera nem se exclui, e MUST ser recusado sem a
  ciência, com a convocação já desfechada, com pedido pendente, com o Processo em estado final ou com
  a convocação fora do portal. O comando MUST correr sob a trava da convocação e com chave de
  idempotência.
- **FR-6421**: Com pedido pendente, a página MUST dizer *"Pedido de desistência enviado em ‹data e
  hora›, protocolo ‹protocolo›. A comissão vai registrá-lo."*, MUST continuar mostrando o prazo, e MUST
  NOT oferecer envio de documento nem do Requerimento. *(Adota a recomendação de P-7.)*
- **FR-6422**: Com pedido pendente, a página MUST oferecer *"Cancelar o pedido de desistência"*, com
  confirmação; o cancelamento MUST ser gravado como registro próprio, e a convocação MUST voltar ao
  estado de antes do pedido. *(Adota a recomendação de P-6.)*
- **FR-6423**: O pedido e o cancelamento MUST entrar na trilha, sem endereço de e-mail.

#### F. A desistência pelo portal: a homologação

- **FR-6424**: Na condução da convocação, o cartão da pessoa com pedido pendente MUST mostrar *"Pedido
  de desistência pelo portal em ‹data e hora›"* e oferecer *"Registrar a desistência pedida"* a quem
  pode registrar desfecho, que abre o registro do desfecho com a desistência expressa escolhida e o
  fundamento *"Desistência expressa pedida pela pessoa convocada, pelo portal, em ‹data e hora›,
  protocolo ‹protocolo›."*, ao qual quem registra pode acrescentar complemento.
- **FR-6425**: Registrar o desfecho de uma convocação com pedido pendente MUST encerrar o pedido:
  como **homologado**, se o desfecho for a desistência expressa; como **encerrado por outro desfecho**,
  nos demais casos, e então a confirmação do desfecho MUST avisar que há pedido pendente e pedir
  ciência. Nenhum pedido MUST virar desfecho sem esse registro.
- **FR-6426**: O registro do não atendimento dos vencidos em lote MUST deixar de fora a pessoa com
  pedido pendente, contada à parte como *"pedido de desistência pendente"*.
- **FR-6427**: O *"O que fazer agora"* da condução MUST derivar a providência *"Registrar a desistência
  pedida pelo portal"* enquanto houver pedido pendente no recorte, do mesmo cálculo do cartão.

#### G. A mensagem da convocação

- **FR-6428**: A mensagem inicial de convocação MUST dizer *"Prazo para atender: até ‹data por
  extenso›."*, e a da correção *"Prazo válido para atender: até ‹data por extenso›."*, nas versões em
  texto puro e em HTML, sem *"contado do envio desta mensagem"*. Mensagens já enviadas e os resumos
  gravados delas MUST NOT mudar.

#### H. O aviso do desfecho

- **FR-6429**: A FR-084 da `010` MUST ser revista para uma **sexta** situação: o **aviso do desfecho da
  convocação**, que quem registra o desfecho decide enviar à pessoa convocada, sem efeito sobre prazo,
  resultado ou direito. As redações anteriores MUST ficar ao fim da alínea, e a guarda
  `backend/tests/test_situacoes_de_mensagem.py` MUST contar seis.
- **FR-6430**: O aviso MUST ser oferecido na confirmação de todo registro de desfecho — individual,
  pelo atalho da desistência pedida e no registro do não atendimento dos vencidos em lote —, como a
  opção *"Avisar a pessoa por e-mail"* (no lote, *"Avisar as pessoas por e-mail"*), marcada por padrão
  e desmarcável. *(Adota a recomendação de P-8.)* Nada MUST gravar aviso de desfecho sem esse gesto.
- **FR-6431**: Marcada a opção, o aviso MUST ser gravado na mesma transação do desfecho, no registro de
  avisos da `066`, e enviado só pelo despacho dela, fora da requisição.
- **FR-6432**: Antes de cada tentativa, o despacho MUST reler o desfecho e interromper o aviso, com o
  motivo, quando ele deixou de ser o desfecho da convocação vigente, como a FR-4623 da `134` faz com a
  pendência. A janela de despacho da `066` MUST valer.
- **FR-6433**: O assunto MUST ser *"‹instituição› · Edital ‹número›/‹ano›: há atualização na sua
  convocação"*, e MUST NOT começar por "Convocação".
- **FR-6434**: O corpo MUST dizer *"O resultado da sua convocação no Edital ‹número›/‹ano› foi
  registrado pela comissão em ‹data›. Veja o resultado e o que fazer depois na sua área do
  candidato."*, com o link da convocação (o mesmo da mensagem da convocação), a instrução de acesso
  por código, o contato (FR-6415) e o rodapé fixo *"Este aviso não é o registro oficial e não altera
  prazo nem resultado. O que vale é o que está na sua área do candidato e o que o Edital publica."*
  O texto MUST ser o mesmo para todas as espécies. *(Adota a recomendação de P-1.)*
- **FR-6435**: O corpo e o assunto MUST NOT conter a espécie do desfecho, o rótulo, o fundamento, o
  nome, o CPF, o protocolo, a modalidade nem a posição, e a mensagem MUST NOT ter anexo.
- **FR-6436**: A pessoa sem endereço MUST ficar sem aviso, e a confirmação do desfecho MUST dizê-lo.

#### I. A habilitação

- **FR-6437**: O aviso do desfecho MUST depender de uma chave própria, `AVISOS_DE_DESFECHO`, e só valer
  com ela **e** `AVISOS_AOS_CANDIDATOS` ligadas. *(Adota a recomendação de P-2.)* As duas MUST vir
  desligadas em produção, ligadas em `development` e `test`.
- **FR-6438**: Com a habilitação desligada, a opção da FR-6430 MUST NOT aparecer, o POST que a trouxer
  MUST ser recusado com `aviso_envio_desabilitado` sem registrar o desfecho, e o despacho MUST NOT
  enviar aviso de desfecho.
- **FR-6439**: A habilitação MUST NOT condicionar nenhum outro requisito desta spec: as seções A a G
  MUST funcionar igualmente com ela ligada ou desligada.
- **FR-6440**: A chave MUST ser ligada em produção só depois do parecer do Encarregado sobre o
  tratamento da seção *A dependência de LGPD, nomeada* e da validação do correio. A ligação é ato de
  configuração; o registro do parecer, e da data em que a chave foi ligada, MUST ficar no documento de
  implantação.

#### J. As revisões

- **FR-6441**: As revisões que esta spec impõe — a FR-084 da `010`, a FR-1172 e a FR-1177 da `063`, a
  FR-3750 da `118` e o texto da mensagem da `121`; e a FR-6206 da `154`, que passa a citar a FR-3750
  revista — MUST ser escritas nas specs de origem, com a
  redação anterior preservada, no PR da implementação desta spec (D-001).

### Requisitos de experiência

- **UX-620**: A frase simples MUST ter no máximo duas frases antes do próximo passo, e MUST vir antes
  de qualquer data técnica, protocolo ou fundamento.
- **UX-621**: O fundamento recolhido MUST abrir pelo teclado, anunciar o estado (aberto ou fechado) e
  não ter rolagem horizontal a 375 px.
- **UX-622**: *"Desistir desta convocação"* MUST ter aparência de link secundário, sem a cor de ação
  principal nem a de perigo, e a confirmação MUST ter o botão *"Enviar o pedido de desistência"* e o
  caminho de volta *"Voltar à convocação"*, este primeiro na ordem do teclado.
- **UX-623**: A opção *"Avisar a pessoa por e-mail"* MUST dizer, ao lado, *"O e-mail diz só que há
  resultado registrado, sem dizer qual."*

### Key Entities

- **Pedido de desistência**: a manifestação da pessoa convocada, feita pelo portal, sobre uma
  chamada. Guarda a convocação, a inscrição, a credencial, o instante e o protocolo. Não se altera nem
  se exclui; o estado (pendente, cancelado, homologado, encerrado por outro desfecho) sai dos
  registros que o sucedem.
- **Cancelamento do pedido**: o registro da pessoa que desfaz o próprio pedido antes do desfecho.
- **Aviso do desfecho**: um aviso no registro da `066`, de origem *desfecho*, com um destinatário, ligado
  ao desfecho que o motivou.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2120**: Nas sete espécies de desfecho e nas três de convocação, nenhum termo da lista da FR-6403
  aparece no portal fora do fundamento recolhido, verificado por varredura sobre as telas renderizadas.
- **SC-2121**: Numa rodada do estudo da jornada final com pelo menos cinco pessoas que não conhecem o
  sistema, ao menos quatro dizem, só pela tela do aceite, qual é o próximo passo e com quem falar; e ao
  menos quatro dizem, pela tela do não atendimento, o que aconteceu e quando.
- **SC-2122**: Em 100% das telas da convocação e do resultado com canal declarado, o contato aparece
  como link; em nenhuma aparece *"o atendimento institucional"*.
- **SC-2123**: Toda desistência registrada a partir de pedido pelo portal cita o protocolo do pedido, e
  todo pedido termina homologado, cancelado ou encerrado por outro desfecho — nenhum vira desfecho sem
  registro da comissão.
- **SC-2124**: Repetida a etapa E do estudo, a desistência de Cecília tem pedido no sistema, com
  instante e protocolo, antes do desfecho.
- **SC-2125**: Com a habilitação desligada, zero aviso de desfecho é gravado ou enviado, e as telas do
  portal são idênticas, letra a letra, às da habilitação ligada.
- **SC-2126**: Com a habilitação ligada, cada desfecho registrado com a opção marcada produz exatamente
  um aviso, e nenhum aviso sai para desfecho que deixou de ser o vigente antes do despacho.
- **SC-2127**: Nenhum aviso de desfecho contém espécie, rótulo, fundamento, nome, CPF, protocolo ou
  modalidade.
- **SC-2128**: Nenhuma mensagem de convocação ou de correção enviada depois da implementação contém
  *"contado do envio"*.

---

## Assumptions

- **A `154` já está na `main`.** Os títulos e as frases das chamadas abertas são os
  dela; esta spec só toca o estado com desfecho, o fundamento da convocação e a mensagem.
- **O canal da unidade é o contato da comissão.** A FR-3211 da `109` o declara como o canal de
  atendimento ao candidato da unidade; a pergunta P-5 trata do caso em que a comissão tenha canal
  próprio.
- **O despacho da `066` aguenta a sexta situação** sem processo novo: o aviso do desfecho é um
  destinatário por aviso, como o de pendência.
- **A seção da matrícula tem caminho próprio na página pública do Edital.** Se não tiver, o plano
  decide entre criar a âncora e levar ao topo da página.
- **O pedido de desistência é ato da pessoa autenticada pelo código de acesso.** A credencial
  verificada é a prova de autoria que o portal já usa para a inscrição e para os documentos.

---

## Perguntas ao usuário

Nove decisões que a spec não toma. Cada uma tem a recomendação, e o texto acima a adota
provisoriamente, marcada.

**P-1 — O que o e-mail do desfecho diz.** *Recomendado:* **neutro** — *"o resultado da sua convocação
foi registrado; veja na sua área do candidato"*, igual para todas as espécies. Alternativa: dizer o
resultado (*"Vaga aceita"*, *"Convocação não atendida"*) e, no aceite, o próximo passo. A neutra
segue a decisão 5 da `066` (sem resultado individual no corpo), não revela por inferência dado
sensível no indeferimento de cota, e facilita o parecer; o custo é a pessoa precisar entrar no portal
para saber qual foi.

**P-2 — A habilitação.** *Recomendado:* **chave própria**, `AVISOS_DE_DESFECHO`, que só vale com a
`AVISOS_AOS_CANDIDATOS` também ligada. Alternativa: a mesma chave da `066`, como a `134` decidiu. A
própria deixa o parecer aprovar uma finalidade sem aprovar a outra; o custo é uma chave a mais na
implantação.

**P-3 — O parecer.** Você confirma que a validação é do **Encarregado pelo Tratamento de Dados
Pessoais do Ifes**, e que **um pedido só** pode cobrir as três finalidades pendentes — o aviso
complementar da `066`, o de pendência da `134` e o do desfecho desta —, com a descrição do
tratamento desta spec? Quem leva o pedido, e se ele já foi feito, é informação que o repositório não
tem.

**P-4 — O próximo passo do aceite.** *Recomendado:* o **caminho para a seção da matrícula** do Edital
publicado, sem campo novo. Alternativa: um campo estruturado e curto no Edital — *"Depois do resultado
da convocação"*: quem conduz a etapa seguinte e como procura a pessoa —, mostrado no portal e,
conforme P-1, no aviso. O campo responde melhor ao *"quem vai procurá-lo"* do achado 07, mas é norma
nova no Edital, com a regra de Retificação que isso traz.

**P-5 — O contato.** *Recomendado:* o **canal da unidade**, com a recaída da instalação, e a linha
omitida quando não houver nenhum. Alternativa: um canal da comissão por Edital ou por Processo, que
recai no da unidade. O recomendado não muda dado; a alternativa serve à unidade que conduz certames
com comissões de contatos diferentes.

**P-6 — Cancelar o pedido.** *Recomendado:* **sim**, até a comissão registrar o desfecho. O endereço
de e-mail pode ser compartilhado, e o pedido é uma manifestação que a pessoa pode reconsiderar enquanto
nada foi decidido. Alternativa: pedido irrevogável pelo portal, e a reconsideração pelo canal da
comissão.

**P-7 — Enviar documento com o pedido pendente.** *Recomendado:* **não**: o envio fica suspenso até o
cancelamento, porque enviar e desistir ao mesmo tempo deixa a comissão sem saber o que vale. O prazo
corre do mesmo jeito. Alternativa: o envio continua oferecido, com aviso.

**P-8 — A opção de avisar no registro do desfecho.** *Recomendado:* **marcada por padrão**,
desmarcável. Alternativa: desmarcada por padrão. A marcada faz o aviso ser a regra quando a
habilitação estiver ligada; ela continua sendo um gesto humano, porque é parte da confirmação.

**P-9 — Dizer ao candidato que a documentação foi disponibilizada ao setor (`117`).** *Recomendado:*
**não**. O GPS sabe que disponibilizou, e não sabe se o setor agiu; a frase criaria a expectativa de
contato que o sistema não acompanha. Alternativa: *"A comissão disponibilizou a sua documentação ao
setor responsável pela próxima etapa em ‹data›."*, depois do aceite.

---

## Decisões desta spec

Propostas de desenho, sujeitas à revisão do PR.

#### D-001 — As revisões de outras specs se escrevem na implementação

A `154` acabou de rever a `063`, a `118`, a `121` e a `134`, e as sessões da `152`, da `153` e da `155`
seguem abertas sobre a mesma jornada. Revisar alíneas normativas neste PR, com nove perguntas ainda
abertas, produziria texto que a resposta pode mudar e conflito resolvido à mão. Esta spec nomeia o que
revê (FR-6441) e deixa a escrita para o PR da implementação, já com as respostas.

#### D-002 — Duas camadas, derivadas na leitura

A frase simples não se grava: é derivada da espécie e dos dados do ato quando a tela é lida. Gravar
exigiria mudar ato append-only ou criar uma segunda versão do mesmo fato; derivar permite corrigir a
frase sem tocar no ato, e o fundamento, que é o ato, continua palavra por palavra.

#### D-003 — "Encerrada para você", e não "perdeu a vaga"

O indeferimento pode ser regularizado (a convocação para regularizar da `019`), e a reclassificação
devolve a pessoa à fila. *"Perdeu a vaga"* seria falso em dois de cinco desfechos de exclusão. A frase
diz o efeito sobre a chamada, que é o que o desfecho registra.

#### D-004 — O próximo passo vem do Edital, nunca do sistema

O GPS não conduz a formalização (`117`): para em *disponibilizado*. O que vem depois do aceite é o que
o Edital publica, e a tela aponta para lá. Sem a seção, ela diz que é o que o Edital publica, e dá o
contato.

#### D-005 — Sem canal, nenhuma linha

A frase *"o atendimento institucional"* só aparece onde não há canal nenhum, o que a produção não
admite. Em desenvolvimento e em estudo, ela fez parecer que o contato não existe. Omitir a linha diz a
verdade: não há canal configurado.

#### D-006 — Desistir é pedido, e o desfecho continua da comissão

Um desfecho por convocação, registrado por quem pode registrá-lo (FR-273 da `019`). O pedido é a
prova da manifestação, e o desfecho a cita. Assim a desistência deixa de ser registrada sem prova, e o
pedido nunca é um desfecho automático.

#### D-007 — Sem motivo no pedido

Um campo de motivo coletaria o que a pessoa escrever — saúde, trabalho, família —, que a comissão não
precisa para registrar a desistência e o sistema passaria a guardar. Minimização (Princípio III da
Constituição).

#### D-008 — Sem recibo por e-mail do pedido

O comprovante é a própria página, com instante e protocolo. Um recibo por e-mail seria uma sétima
situação da FR-084 da `010`, com o mesmo parecer pendente. Se o usuário quiser, entra como incremento.

#### D-009 — O pedido é da chamada

Como o limite diário da `134`, o pedido pertence à chamada (a raiz), e não à convocação vigente: a
correção por sucessão não o perde nem abre um segundo.

#### D-010 — O pedido vale depois do vencimento

Até o desfecho, a convocação é da comissão decidir, e a manifestação da pessoa ajuda a decidir certo.
Depois do vencimento, sem o pedido, o registro seria o não atendimento, que descreve outro fato.

#### D-011 — Nenhum aviso retroativo

Ligar a habilitação não avisa desfechos já registrados. É a mesma regra que a `066` escreveu para a
reativação da chave: mensagem antiga disparada de uma vez é o que se quer evitar.

#### D-012 — O aviso nasce no gesto do desfecho

A FR-084 da `010` exige decisão humana. Na `134` o gesto é próprio, porque a pendência não é ato. Aqui
o desfecho é o ato, e a confirmação dele é o gesto: um segundo botão, depois, seria esquecido justamente
quando mais importa.

#### D-013 — O lote do não atendimento deixa de fora quem pediu desistência

Registrar o não atendimento de quem pediu para desistir registraria um fato diferente do que
aconteceu. A pessoa fica para o atalho da desistência pedida.

#### D-014 — A mensagem da convocação diz só a data

O prazo é a data informada no ato, e o envio só o põe em curso (o achado do reenvio, de 09/10/2026).
*"Contado do envio desta mensagem"* é inexato na primeira mensagem e enganoso na segunda.
