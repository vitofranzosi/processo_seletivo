# Feature Specification: O desfecho da convocação comunicado ao candidato

**Feature Branch**: `claude/intelligent-robinson-4466a5`, sobre a `main` em `240cac91` (com a `154`,
PR #479, e o plano da `152`, PR #480, mergeados)

**Created**: 2026-11-11

**Status**: **Spec com as decisões do usuário incorporadas; sem plano nem código.** As decisões têm
duas origens:

- **Do usuário, em 11/11/2026**: a *1ª* à *9ª decisão*, em *Clarifications*, sobre as nove perguntas
  da primeira versão desta spec. Não se reabrem.
- **Propostas de desenho desta spec:** D-001 a D-017, ao fim. Elas fecham o que as decisões deixaram
  aberto e estão sujeitas à revisão do PR.

As **revisões de requisitos de outras specs** estão escritas nas specs de origem, com a redação
anterior preservada em cada alínea, e vigoram com a implementação desta (seção *As revisões, escritas
nas specs de origem*). As **pendências institucionais** da validação do envio estão em PI-1 a PI-6;
elas condicionam só a habilitação do envio, e não o plano.

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
> quarenta e nove, e a `154` usou até seis mil duzentos e dezesseis. As decisões reiniciam em `D-001`.
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
nenhum dos dois. A parte do achado 17 que é de ambiente não se resolve aqui; a que é de tela, sim.

**O e-mail é a parte que depende de terceiro.** O aviso por e-mail usa o endereço da pessoa para uma
finalidade que o Edital não declara, e a `066` deixou registrado que esse uso espera validação
institucional antes de produção. O resto desta spec — o portal, a desistência, o texto do e-mail que
já sai — não espera por ela. A orientação do usuário pede justamente essa separação.

### O que esta spec cobre, e o que fica fora

**Cobre:**

1. **O portal em cada desfecho**: a frase simples por espécie, o fundamento do ato recolhido, o
   próximo passo do aceite e da regularização pelo Edital publicado, o caminho para recorrer quando o
   Edital o prevê, e o contato. Também a convocação ainda sem desfecho, nas duas camadas.
2. **O texto da mensagem da convocação**, que deixa de dizer *"contado do envio desta mensagem"*.
3. **A desistência pelo portal**, como pedido registrado e cancelável, que a comissão homologa ao
   registrar o desfecho, e as consequências dele no resto do sistema.
4. **O aviso do desfecho por e-mail**: quais desfechos, quando, com que texto, por qual despacho.
5. **A dependência de validação institucional**, separada entre o que as specs anteriores exigem e
   as hipóteses desta, e a habilitação que ela condiciona.

**Fica fora:**

- O título, a frase de conclusão, a advertência e o nome do reenviado das chamadas abertas: são da
  `154`, e esta spec parte do que ela decidiu, sem refazer. A FR-6206 da `154` exige que a tela com
  desfecho continue a da FR-3750 da `118` — título, rótulo e, no aceite, a frase de que o registro
  não é matrícula, bolsa nem contrato. A FR-3750 revista mantém as três, e a FR-6206 continua
  satisfeita sem mudar de redação.
- **Campo de contato da comissão** (5ª decisão) e **campo estruturado do próximo passo** no Edital.
- **Aviso da disponibilização ao setor** (9ª decisão).
- O recurso contra o indeferimento dentro do sistema (a questão institucional `QI-6` da `115`):
  esta spec só aponta para o que o Edital diz.
- A confirmação de recebimento pelo setor de formalização e o vínculo formalizado (`117`).
- Vocabulário por natureza da seleção (curso, bolsa, contratação) nos rótulos dos desfechos: spec
  própria, registrada pela `152`.
- O aviso aos que tiveram desfecho **antes** da habilitação ser ligada (D-011).
- Recibo por e-mail do pedido de desistência (D-008).
- Canais além do e-mail, descadastro e rastreio de abertura (fora pela `066`).
- As frases do portal que dizem *"contado do envio da comunicação"* no cartão do prazo (FR-3998 da
  `125`): o achado 18 é sobre a mensagem.

---

## Clarifications

### Session 2026-11-11 (decisões do usuário sobre as nove perguntas)

- Q: O que o e-mail do desfecho diz? → A: **Texto neutro**, que informa que há resultado registrado e
  indica o acesso ao portal. Resultado e fundamento ficam no ambiente autenticado. *(1ª decisão)*
- Q: Chave própria ou a da `066`? → A: **Chave própria, dependente também da chave geral dos
  avisos.** O envio permanece desligado até a validação institucional correspondente. *(2ª decisão)*
- Q: O parecer é do Encarregado, e um pedido só cobre as três finalidades? → A: **Nada disso está
  confirmado** — nem o responsável, nem a existência do pedido, nem a possibilidade de um parecer
  único. Esses pontos são **pendências institucionais**, e a spec distingue o que as specs
  anteriores exigem das hipóteses desta proposta. Isso não impede avançar nas partes independentes
  do envio. *(3ª decisão)*
- Q: Qual é o próximo passo do aceite? → A: **Orientar para a seção aplicável do Edital publicado e
  oferecer o contato. Não presumir matrícula**: pode haver bolsa, contratação ou outra formalização.
  Sem orientação identificável, indicar a consulta ao Edital e ao atendimento, **sem inventar um
  próximo passo**. *(4ª decisão)*
- Q: Qual contato? → A: **O canal da unidade, com alternativa no canal da instalação.** Nenhum campo
  da comissão nesta entrega. Sem contato configurado, **omitir a linha**. *(5ª decisão)*
- Q: O pedido de desistência pode ser cancelado? → A: **Sim, enquanto a comissão não tiver
  registrado o desfecho.** Pedido e cancelamento preservam o histórico. A tela deixa claro que
  **solicitar a desistência ainda não é ter a desistência efetivada**. *(6ª decisão)*
- Q: Com o pedido pendente, o envio de documentos fica suspenso? → A: **Não.** Os envios permitidos
  pelas regras vigentes continuam; o pedido não suspende nem prorroga o prazo; o candidato não é
  bloqueado enquanto ainda pode cancelar o pedido e cumprir a convocação. *(7ª decisão)*
- Q: A opção de avisar vem marcada? → A: **Desmarcada por padrão**, com solicitação explícita. A
  confirmação distingue **aviso solicitado** de **aviso enviado**. *(8ª decisão)*
- Q: O portal diz que a documentação foi disponibilizada ao setor? → A: **Sem aviso específico nesta
  entrega.** Essa operação interna não se apresenta como matrícula, contratação ou formalização
  concluída. *(9ª decisão)*
- Instrução que acompanhou as decisões: incorporar as decisões e as revisões dos requisitos
  anteriores na documentação **antes do plano**, preservando as redações anteriores, e explicitar as
  consequências do novo pedido de desistência e os encontros com a `152` e a `153`.

---

## A validação institucional do envio

Esta seção responde à orientação do usuário e à 3ª decisão: o que falta validar, separando o que já
é exigência escrita do que é hipótese desta proposta, e o que a falta impede.

### O que as specs anteriores exigem

São requisitos escritos e vigentes. Esta spec não os altera; ela os estende à finalidade nova.

| Origem | O que está escrito |
|---|---|
| decisão 10 da `066` (decisões recebidas) | *"A validação institucional fica registrada como pendente, e é exigida antes da entrada em produção."* |
| precondição de produção da `066` | *"A base legal do uso do e-mail para aviso complementar e a retenção da lista de destinatários dependem de validação institucional, com o encarregado de dados, antes da entrada em produção."* E: *"Se a base legal exigir direito de oposição, o descadastro entra como incremento."* |
| decisão da chave de habilitação da `066` | `AVISOS_AOS_CANDIDATOS` desligada em produção *"até a validação institucional de LGPD e da infraestrutura de correio"*; a reativação não envia o que ficou fora da janela de despacho |
| 5ª decisão da `134` | a mesma chave, desligada em produção *"até a validação de LGPD e de SPF/DKIM"* |
| PC-003 da `010` | a área do candidato não entra em produção com dados reais sem política institucional documentada de retenção e descarte |

O que essas exigências deixam **dito**: há uma validação institucional de LGPD pendente, que
envolve o encarregado de dados, sobre a base legal do uso do e-mail para aviso e sobre a retenção da
lista de destinatários; e há uma validação, separada, da infraestrutura de correio. O que elas
**não** dizem: quem emite a validação, se o pedido foi feito, e se uma validação cobre mais de uma
finalidade.

### As hipóteses desta proposta

Não estão confirmadas (3ª decisão). Servem para preparar o pedido, e não o substituem.

- **H-1 — Quem valida.** A hipótese é que a validação seja do Encarregado pelo Tratamento de Dados
  Pessoais do Ifes (art. 41 da LGPD), em nome do controlador. A `066` diz *"com o encarregado"*, o que
  não define quem emite nem quem aprova.
- **H-2 — O alcance.** A hipótese é que o tratamento do aviso do desfecho seja do mesmo tipo do aviso
  complementar e do de pendência — e-mail sem efeito sobre ato já praticado —, e que por isso possa
  ser examinado junto com eles. Pode não ser: o desfecho é resultado individual.
- **H-3 — A base legal.** As hipóteses que a validação deve confirmar ou afastar: o art. 7º, III, com
  o art. 23 (tratamento pelo poder público para executar atribuição legal do serviço público); e o
  art. 7º, II (obrigação legal), se se entender que o dever de dar ciência ao interessado dos atos
  que restringem direito (Lei nº 9.784/1999, art. 26 e 28) alcança este aviso. A proposta **não**
  usa consentimento: entre poder público e candidato ele não é livre, e o aviso deixaria de alcançar
  quem não respondesse.
- **H-4 — A minimização.** A hipótese é que o texto neutro da 1ª decisão reduza o tratamento ao
  endereço e ao fato de haver resultado registrado no Edital tal, sem a espécie do desfecho, que no
  indeferimento de quem concorre por reserva de vagas poderia revelar dado sensível por inferência
  (art. 5º, II, e art. 11).

### O tratamento a validar

| | O que é |
|---|---|
| **Dado tratado** | o endereço de e-mail da pessoa convocada, na ordem da `066` (a credencial verificada pelo código de acesso antes do endereço da inscrição); o número e o ano do Edital; e, pelo próprio envio, o fato de que esta pessoa foi convocada e teve o resultado da convocação registrado. Sem espécie, rótulo, fundamento, nome, CPF, protocolo, modalidade nem posição (FR-6438) |
| **Finalidade** | avisar a pessoa de que há resultado registrado da sua convocação, para que ela o consulte no portal e cumpra a providência seguinte que o Edital indica, ou exerça no prazo o direito de recorrer que o Edital preveja. O aviso não é o ato, não intima e não altera prazo nem resultado |
| **Base legal** | a confirmar (H-3) |
| **Operador** | o serviço de correio que transmite a mensagem |
| **Retenção** | o registro do aviso e de cada destinatário, que a `066` guarda, pela política da PC-003 da `010` |
| **Direitos do titular** | se a base legal exigir oposição, o descadastro entra como incremento, como a `066` previa |

### As pendências institucionais

Condicionam só a habilitação do envio (FR-6443). Não são perguntas desta spec ao usuário: são o que
precisa existir fora do sistema antes de ligar a chave.

- **PI-1 — Responsável pela validação**: quem emite e quem aprova (H-1).
- **PI-2 — Existência do pedido**: se a validação já foi pedida, por quem e quando, e se o pedido
  da `066` e da `134` existe. O repositório não registra nenhum dos dois.
- **PI-3 — Alcance**: se uma validação pode cobrir a `066`, a `134` e esta, ou se esta precisa de uma
  própria (H-2). A chave própria (2ª decisão) funciona nos dois casos.
- **PI-4 — Base legal**: a hipótese confirmada, e o que ela exige (H-3).
- **PI-5 — Retenção**: a política da PC-003 da `010`, que continua pendente.
- **PI-6 — Infraestrutura de correio**: SPF e DKIM do remetente. Não é LGPD, e é exigida pela `066`
  e pela `134` do mesmo modo.

### O que a falta impede

**Só o envio do aviso do desfecho por e-mail**: a opção de avisar, no registro do desfecho, e a
saída da mensagem pelo despacho. Com a habilitação desligada, a opção não aparece, nada é gravado, e
o despacho não tem o que enviar (FR-6434, FR-6440 e FR-6441).

### O que ela não impede

| Parte desta spec | Por que não depende da validação |
|---|---|
| O portal em cada desfecho, nas duas camadas (§A a §C) | Mostra à própria pessoa, autenticada, o que o sistema já mostra a ela hoje, em outras palavras. Nenhum dado novo, nenhuma finalidade nova |
| O contato (§D) | É dado institucional, e não pessoal |
| A desistência pelo portal (§E e §F) | É manifestação da pessoa no próprio procedimento do certame, pela mesma via em que ela se inscreve e envia documentos. Sem campo de motivo (D-007), não coleta dado novo. A PC-003 da `010` vale para ela como vale para o resto do portal |
| O texto corrigido da mensagem da convocação (§G) | A mensagem já sai, na terceira situação da FR-084 da `010`, que é o próprio ato; muda a redação, e não o tratamento |
| O plano, a implementação e os testes do aviso | A chave vem ligada em `development` e `test`, como a da `066` |

---

## O que o pedido de desistência muda, e o que não muda

O pedido é registro novo, da pessoa, sobre a chamada (D-009). **Pedir não é desistir** (6ª
decisão): até a comissão registrar o desfecho, a convocação continua a mesma.

| Onde | Com o pedido pendente | Requisito |
|---|---|---|
| Prazo da convocação | não suspende, não prorroga, não reinicia | FR-6419, FR-6422 |
| Envio de documentos e do Requerimento | continua pelas regras vigentes (FR-3578 e FR-3582 da `115`) | FR-6422 |
| Conferência dos documentos | continua; a comissão pode conferir o que chegar | FR-6422 |
| Aviso de pendência da `134` | continua alcançando a pessoa: o pedido não é desfecho, e a pessoa pode cancelar e cumprir | D-015 |
| Ocupação, apuração, fila e sucessora | nada muda; o efeito na contagem nasce só do desfecho (FR-273 da `019`) | D-006 |
| Registro do desfecho individual, de qualquer espécie | possível; a confirmação avisa do pedido e pede ciência, salvo pelo atalho da desistência pedida | FR-6426, FR-6428 |
| Registro do não atendimento dos vencidos em lote | a pessoa fica de fora, contada à parte (FR-878 da `050`, revista) | FR-6429 |
| Atalho de indeferimento pelas pendências (`152`) | continua oferecido nas condições da FR-5800 da `152`; ao confirmar, a ciência do pedido se soma à da FR-5803 da `152` | FR-6428 |
| Correção da convocação por sucessão (`120`) | o pedido acompanha a convocação vigente da chamada | D-009 |
| "O que fazer agora" da condução (`127`) | ganha a providência *"Registrar a desistência pedida pelo portal"* | FR-6430 |
| Encerramento do Edital e do Processo | a confirmação adverte dos pedidos pendentes, sem impedir | FR-6431 |
| Formalização (`117`, `153`) | nada: a pessoa só fica apta com aceite | §Encontros |
| Trilha | pedido e cancelamento, sem endereço | FR-6424 |

---

## Encontros com a `152` e a `153`

**Com a `152`** (prevenção nos atos irreversíveis; plano no PR #480, implementação em curso):

- **O seletor do desfecho continua sem espécie pré-escolhida** (FR-5839 da `152`). O atalho
  *"Registrar a desistência pedida"* não é o seletor: é gesto próprio, como o atalho de indeferimento
  da `152`, com a espécie fixa e o fundamento derivado do pedido (D-016). O seletor continua
  oferecendo as espécies que o comando aceita agora (FR-5835 da `152`); o pedido não muda essa
  verificação.
- **As ciências se somam.** Indeferir com o prazo em curso pede a ciência da FR-5803 da `152`; com
  pedido pendente, a confirmação pede também a da FR-6428. São duas marcas, cada uma com a sua frase,
  e o comando confere as duas.
- **A conferência do texto mostra as duas camadas.** A FR-5813 da `152` manda a conferência da
  chamada mostrar o fundamento *"como o candidato o lerá no portal"*, e a FR-3993 da `125` manda a
  prévia mostrar o texto *"como o candidato o verá"*. Com as duas camadas, o candidato lê a frase
  simples e, recolhido, o fundamento; a prévia passa a mostrar os dois (FR-3993 da `125`, revista).
  A FR-5813 não muda de redação: ela segue o portal.
- **O cartão sem nada apresentado** (FR-5809 da `152`) aponta o não atendimento; com pedido
  pendente, o cartão mostra antes o pedido e o atalho da desistência pedida (FR-6427).
- **Nenhuma fronteira da `152` se afrouxa**: o comando de desfecho continua recusando o que recusa.

**Com a `153`** (formalização na jornada guiada):

- **Pessoa apta é a do aceite** (FR-6101 da `153`, FR-3669 da `117`). O pedido pendente não a torna
  apta nem a tira dessa condição; a desistência homologada é desfecho de exclusão, e a pessoa nunca
  chega à formalização.
- **As providências não se misturam**: as três da `153` são da fase Conclusão; a desta spec é da
  fase da convocação, na ordem fixa da FR-4082 da `127` (da pessoa, *Pendente*, sem prazo, pela
  espera mais antiga).
- **A advertência do encerramento** (FR-6124 e FR-6128 da `153`) ganha uma linha irmã, a dos pedidos
  pendentes (FR-6431), na mesma confirmação e pela mesma regra de caminho.
- **O vocabulário é o mesmo** (9ª decisão; FR-6123 da `153`, FR-3751 da `118`): nada no portal diz
  que a documentação foi *encaminhada*, *entregue* ou *recebida*, nem apresenta a disponibilização
  ao setor como matrícula, contratação ou formalização concluída (FR-6415).

---

## User Scenarios & Testing *(mandatory)*

Os cenários são os do estudo, no SIM09/2026 (C09): **Alice**, aceita; **Cecília**, que desistiu;
**Davi**, que não atendeu no prazo. Acrescentam-se **Elisa**, indeferida por documento, e **Fábio**,
que pede a desistência pelo portal. Dados fictícios.

### User Story 1 — Quem foi aceito sabe onde está o próximo passo e a quem perguntar (Priority: P1)

Alice teve a vaga aceita. Ao abrir a convocação, ela lê que a comissão registrou o resultado, que o
registro não é matrícula, bolsa nem contrato, em que seção do Edital publicado está o que vem depois
— com o caminho até lá — e com quem falar se tiver dúvida.

**Why this priority**: é o achado 07 na pessoa que mais precisa agir.

**Independent Test**: no C09, reproduzir `F14-portal-alice-aceite` e conferir a frase, o caminho para
a seção aplicável e o contato, sem abrir o fundamento.

**Acceptance Scenarios**:

1. **Given** Alice com aceite, num Edital cujo texto publicado tem a seção aplicável preenchida
   (FR-6411), **When** ela abre a convocação ou o acompanhamento, **Then** lê *"Vaga aceita"*, a frase
   simples, o título da seção como o Edital o publicou, com o caminho até ela, e o contato.
2. **Given** um Edital sem seção aplicável preenchida — uma seleção de bolsista, por exemplo —,
   **When** Alice abre a convocação, **Then** lê *"Consulte o Edital publicado para saber o que vem
   depois."* e o contato, e nada fala de matrícula como próximo passo.
3. **Given** Alice com aceite, **When** ela lê a página, **Then** nada diz *matriculado*, *contratado*,
   *bolsa concedida*, *encaminhado*, *formalizado* nem *apto para formalização*.
4. **Given** a regularização registrada, **Then** a frase é a da regularização, e o próximo passo e o
   contato seguem a mesma regra.

---

### User Story 2 — Quem perdeu a vaga entende por quê, em uma frase (Priority: P1)

Davi não atendeu no prazo. Ao abrir a convocação, ele lê, em linguagem simples, que o prazo terminou
na data tal sem que a convocação fosse atendida, que a comissão registrou isso e que a convocação está
encerrada para ele. O fundamento do ato continua lá, recolhido.

**Why this priority**: é o achado 18.

**Independent Test**: para cada uma das sete espécies de desfecho, a tela mostra a frase simples da
FR-6406 e o fundamento recolhido; nenhum termo da FR-6403 aparece fora do fundamento.

**Acceptance Scenarios**:

1. **Given** Davi com não atendimento, **When** ele abre a convocação, **Then** lê *"Convocação não
   atendida"* e a frase simples, com a data do fim do prazo; o fundamento está sob *"Fundamento do
   registro"*.
2. **Given** Elisa com indeferimento, num Edital que publica como recorrer, **Then** a frase diz que a
   comissão registrou o indeferimento e que o motivo está no fundamento, e a página oferece o caminho
   para a seção de recursos.
3. **Given** Cecília com desistência registrada, **Then** a frase diz que a comissão registrou a
   desistência dela, em que data, e que a convocação está encerrada para ela.
4. **Given** qualquer desfecho, **When** a pessoa abre o fundamento recolhido, **Then** lê o texto
   gravado no ato, palavra por palavra, com a data do registro.

---

### User Story 3 — A convocação ainda aberta diz por que a pessoa foi chamada (Priority: P2)

Antes de qualquer desfecho, a página da convocação diz em uma frase por que a pessoa foi chamada e
recolhe o fundamento derivado da norma.

**Independent Test**: para cada espécie de convocação, a tela mostra a frase simples da FR-6408 e o
fundamento recolhido; *"faixa vigente"* e *"recorte"* não aparecem fora dele.

**Acceptance Scenarios**:

1. **Given** uma convocação para vaga inicial, **Then** a pessoa lê que foi chamada porque a posição
   dela na lista está dentro das vagas da lista.
2. **Given** uma convocação para vaga que vagou, **Then** lê que foi chamada porque uma vaga da lista
   ficou livre e ela é a próxima na classificação.
3. **Given** o complemento escrito por quem convocou, **Then** ele aparece dentro do fundamento
   recolhido, depois do texto derivado.

---

### User Story 4 — O contato é o da unidade, ou nenhum (Priority: P1)

Na convocação, no resultado e no aviso, a pessoa lê o canal de atendimento da unidade que conduz o
certame, como link, ou o da instalação na falta dele. Sem nenhum, a linha não aparece.

**Independent Test**: com o canal da unidade preenchido, a convocação, o resultado e o aviso o
mostram; sem canal nenhum, nenhuma tela da convocação ou do resultado diz *"o atendimento
institucional"*.

**Acceptance Scenarios**:

1. **Given** a unidade com canal *selecao@unidade.exemplo.test*, **Then** a linha *"Atendimento"* traz o
   endereço, como link de e-mail.
2. **Given** a unidade sem canal e a instalação com `PORTAL_ATENDIMENTO`, **Then** a linha traz o da
   instalação.
3. **Given** nenhum dos dois, **Then** a linha não aparece, nem a frase *"fale com o atendimento"*.

---

### User Story 5 — Fábio pede a desistência, e pode voltar atrás até a comissão registrar (Priority: P2)

Fábio foi convocado e não quer a vaga. No fim da página da convocação há *"Desistir desta
convocação"*. A página seguinte diz que o pedido ainda não é a desistência, que a comissão é quem a
registra, que o prazo continua o mesmo e que ele pode cancelar o pedido até o registro. Confirmado, o
pedido ganha protocolo, e a convocação continua aberta para ele.

**Why this priority**: é o achado 17, na parte de capacidade.

**Independent Test**: Fábio pede a desistência, envia um documento depois do pedido, cancela o pedido
e o refaz; a trilha tem os três registros, sem endereço; nenhum desfecho foi registrado; o prazo é o
mesmo do começo.

**Acceptance Scenarios**:

1. **Given** Fábio com convocação sem desfecho e visível no portal, **When** ele aciona *"Desistir
   desta convocação"*, **Then** vê a página de confirmação, com o que o pedido faz e não faz, e sem
   campo de motivo.
2. **Given** a página de confirmação, **When** ele confirma sem marcar a ciência, **Then** nada é
   gravado.
3. **Given** a ciência marcada, **When** ele confirma, **Then** o pedido é gravado com instante,
   credencial e protocolo, e a convocação diz que o pedido foi enviado, que a desistência ainda não foi
   registrada e que, até lá, a convocação continua com o mesmo prazo.
4. **Given** o pedido pendente e o prazo correndo, **When** Fábio abre a convocação, **Then** o envio
   de documentos e do Requerimento continua oferecido como antes do pedido.
5. **Given** o pedido pendente, **When** Fábio aciona *"Cancelar o pedido de desistência"* e confirma,
   **Then** o cancelamento é gravado como registro próprio, o pedido continua no histórico como
   cancelado, e a convocação volta a oferecer *"Desistir desta convocação"*.
6. **Given** um duplo clique na confirmação, **Then** um pedido só é gravado.

---

### User Story 6 — A comissão homologa o pedido ao registrar a desistência (Priority: P2)

O cartão de Fábio na condução da convocação diz *"Pedido de desistência pelo portal em ‹data›"* e
oferece *"Registrar a desistência pedida"*. Confirmado, o desfecho é a desistência expressa de
sempre, citando o pedido.

**Why this priority**: sem a homologação, o pedido seria desfecho automático, que a orientação
proíbe e a regra de um desfecho por convocação (FR-273 da `019`) não admite fora da comissão.

**Acceptance Scenarios**:

1. **Given** um pedido pendente, **When** a comissão abre a condução do recorte, **Then** o cartão
   mostra o pedido e o atalho, e o *"O que fazer agora"* traz *"Registrar a desistência pedida pelo
   portal"*.
2. **Given** o atalho, **When** quem pode registrar desfecho confirma, **Then** o desfecho é a
   desistência expressa, com o fundamento que cita data, hora e protocolo do pedido, e o pedido fica
   homologado.
3. **Given** um pedido pendente, **When** a comissão registra outro desfecho, **Then** a confirmação
   avisa do pedido e pede ciência; registrado, o pedido fica encerrado por outro desfecho.
4. **Given** um pedido pendente e o vencimento passado, **When** a comissão aciona o não atendimento
   dos vencidos, **Then** a pessoa fica de fora, contada como *"pedido de desistência pendente"*.
5. **Given** um pedido cancelado, **Then** o cartão não mostra pedido pendente, e o histórico da
   convocação mostra o pedido e o cancelamento.

---

### User Story 7 — O resultado chega por e-mail, quando pedido e quando habilitado (Priority: P3)

Com a habilitação ligada, quem registra o desfecho vê, na confirmação, *"Avisar a pessoa por
e-mail"*, desmarcado. Marcado e confirmado, a tela diz *"Aviso solicitado"*; o despacho da `066` o
envia depois, e o cartão passa a dizer *"Aviso enviado em ‹data›"*. O e-mail é neutro: diz que há
resultado registrado e como entrar no portal.

**Why this priority**: é a parte do achado 07 que depende da validação institucional.

**Acceptance Scenarios**:

1. **Given** a habilitação ligada, **When** a comissão registra o desfecho sem marcar a opção,
   **Then** nenhum aviso é gravado.
2. **Given** a opção marcada, **When** a comissão confirma, **Then** um aviso é gravado na mesma
   transação, nenhuma mensagem sai na requisição, e a resposta diz *"Aviso solicitado"*, e não
   *"enviado"*.
3. **Given** o aviso solicitado, **When** o despacho o envia, **Then** o cartão diz *"Aviso enviado em
   ‹data e hora›"*; falhando ou interrompido, diz isso, com o motivo.
4. **Given** o aviso solicitado, **When**, antes do despacho, a convocação é corrigida por sucessão e o
   desfecho deixa de ser o vigente, **Then** o despacho o interrompe.
5. **Given** a habilitação desligada, **Then** a confirmação não oferece a opção, e nenhum aviso é
   gravado.

---

### User Story 8 — O e-mail da convocação diz o prazo como ele é (Priority: P2)

A mensagem da convocação e a da correção dizem *"Prazo para atender: até ‹data por extenso›."* e
*"Prazo válido para atender: até ‹data por extenso›."*, sem *"contado do envio desta mensagem"*.

**Independent Test**: as mensagens novas, inicial e de correção, em texto puro e em HTML, não contêm
*"contado do envio"*; as já enviadas não mudam.

---

### Edge Cases

- **Inércia**: a frase simples cita o fato atestado em linguagem simples (FR-6407).
- **Reclassificação**: a frase não promete nova chamada.
- **Edital sem seção aplicável ou sem a de recursos**: nenhuma frase aponta para seção vazia, e nenhuma
  inventa o próximo passo (FR-6412, FR-6414).
- **Convocação corrigida por sucessão** depois do pedido: o pedido é da chamada (D-009).
- **Convocação por publicação ainda não publicada** (*K-pub* da `125`): não aparece no portal, e o
  pedido não é oferecido.
- **Pedido depois do vencimento**: admitido enquanto não houver desfecho (D-010).
- **Processo encerrado ou cancelado**: pedido e cancelamento são recusados; o pendente continua visível
  à comissão e no histórico.
- **Cancelar e pedir de novo**: cada pedido é registro próprio, com protocolo próprio; o histórico
  mostra todos.
- **Pessoa sem endereço**, com a habilitação ligada: a opção de avisar aparece desabilitada, com a
  razão.
- **Desfecho registrado com a habilitação desligada, e ela ligada depois**: nenhum aviso retroativo
  (D-011).
- **Duas sessões do mesmo candidato** pedindo ao mesmo tempo: um pedido só, pela trava da convocação.
- **O fundamento digitado expõe outra pessoa**: a regra da `125` continua; recolhido não quer dizer
  escondido.

---

## Requirements *(mandatory)*

### Functional Requirements

#### A. As duas camadas

- **FR-6400**: Toda tela do portal que mostra um desfecho de convocação ou o fundamento de uma
  convocação MUST mostrar primeiro a **frase simples** desta spec e, depois dela, o **fundamento do
  ato** recolhido, sob o rótulo *"Fundamento do registro"* (desfecho) ou *"Fundamento da convocação"*
  (convocação), aberto por gesto da pessoa e legível sem script.
- **FR-6401**: O fundamento recolhido MUST ser o texto gravado no ato, sem edição, com a data do
  registro e o complemento depois do texto derivado, como hoje.
- **FR-6402**: A frase simples MUST ser derivada da espécie e dos dados do ato no momento da leitura, e
  MUST NOT ser gravada no ato. Ato já gravado MUST NOT mudar (8ª decisão da `154`).
- **FR-6403**: Fora do fundamento recolhido, as telas do portal da convocação e do desfecho MUST NOT
  conter *"faixa vigente"*, *"recorte"*, *"apuração"*, *"decorreu"*, *"desfecho registrado"*,
  *"vencimento informado no ato"* nem *"espécie"*. A varredura de vocabulário da `063` MUST alcançar
  as frases desta spec.
- **FR-6404**: As telas da gestão MUST continuar mostrando o fundamento como hoje; as duas camadas são
  do portal. A prévia do texto (FR-3993 da `125`, revista) MUST mostrar as duas camadas, como o
  portal as mostrará.

#### B. O portal em cada desfecho

- **FR-6405**: O rótulo de cada desfecho MUST continuar o da tabela da FR-1172 da `063`, e o título da
  página o da FR-3858 da `121` (*"Resultado da sua convocação"*), como a `154` o deixou.
- **FR-6406**: A frase simples de cada desfecho MUST ser a desta tabela, com ‹data› a data local do
  registro e ‹fim do prazo› o vencimento da convocação vigente:

  | Desfecho | Frase simples |
  |---|---|
  | Aceite | *"A comissão registrou o resultado da sua convocação em ‹data›. Este registro não é matrícula, bolsa nem contrato."*, seguida do próximo passo (FR-6410 a FR-6413) |
  | Regularização | *"A comissão registrou a regularização da sua situação nesta convocação em ‹data›. Este registro não é matrícula, bolsa nem contrato."*, seguida do próximo passo |
  | Indeferimento | *"A comissão registrou o indeferimento desta convocação em ‹data›: ela concluiu que o que o Edital pede nesta etapa não foi cumprido. O motivo está no fundamento, abaixo."*, seguida do caminho para recorrer (FR-6414) |
  | Desistência expressa | *"A comissão registrou a sua desistência desta convocação em ‹data›. Esta convocação está encerrada para você."* |
  | Não atendimento | *"O prazo desta convocação terminou em ‹fim do prazo› sem que ela fosse atendida, e a comissão registrou isso em ‹data›. Esta convocação está encerrada para você."* |
  | Cancelamento por inércia | *"A comissão registrou o cancelamento em ‹data›, porque ‹fato atestado, FR-6407›. Esta convocação está encerrada para você."* |
  | Reclassificação | *"A comissão registrou a sua reclassificação em ‹data›. Esta convocação está encerrada para você; o que acontece depois é o que o Edital diz."* |

- **FR-6407**: No cancelamento por inércia, o fato atestado MUST ser dito assim: *"não houve acesso ao
  ambiente do curso"*, *"não houve presença na primeira semana do curso"* e *"a entrega presencial não
  foi feita"*, uma por espécie de atestado da `019`.
- **FR-6408**: A frase simples da convocação sem desfecho MUST ser, por espécie: vaga inicial —
  *"Você foi chamado porque a sua posição na lista ‹nome da lista› está dentro das vagas desta
  lista."*; vaga que vagou — *"Você foi chamado porque uma vaga da lista ‹nome da lista› ficou livre
  e você é a próxima pessoa na classificação."*; para regularizar — *"Você foi chamado para
  regularizar a sua situação na lista ‹nome da lista›, porque há vaga."*.
- **FR-6409**: Nenhuma frase desta spec MUST afirmar perda definitiva de vaga, nova chamada, posição na
  lista ou consequência que nenhum ato declarou. *"Esta convocação está encerrada para você"* diz o
  efeito do desfecho registrado sobre a chamada, e não sobre o certame (D-003; FR-1177 da `063`,
  revista).

#### C. O próximo passo do aceite e da regularização

- **FR-6410**: Com aceite ou regularização, a página MUST dizer o próximo passo depois da frase
  simples, no lugar de *"Os próximos passos são os que o Edital indica."* (FR-3750 da `118`, revista).
  O próximo passo MUST vir só do texto publicado do Edital vigente e do contato, e MUST NOT ser
  inventado pelo sistema (4ª decisão).
- **FR-6411**: A **seção aplicável** MUST ser a seção do catálogo que trata da etapa depois do resultado
  da convocação — a de chave `matricula` (*"Da Matrícula"*, ou *"Como será a matrícula?"* no catálogo
  da `069`, com as partes *Acesso ao curso* e *Homologação da matrícula* que esse catálogo lhe junta)
  —, quando o texto publicado a tiver não vazia. O título MUST ser o que o Edital publicado lhe dá, e
  o próximo passo MUST ser *"O Edital explica o que vem depois em «‹título da seção›»."*, com o
  caminho para essa seção na página pública do Edital (D-004).
- **FR-6412**: Sem seção aplicável não vazia, o próximo passo MUST ser *"Consulte o Edital publicado
  para saber o que vem depois."*, com o caminho para a página pública do Edital, e nenhuma frase MUST
  presumir matrícula, bolsa ou contratação como próximo passo.
- **FR-6413**: O próximo passo MUST terminar com *"Se tiver dúvida, fale com ‹contato›."* quando houver
  canal (FR-6416), e MUST NOT nomear setor, pessoa ou data que o Edital não publique.
- **FR-6414**: Com indeferimento, quando o texto publicado tiver a seção de recursos não vazia, a página
  MUST dizer *"O Edital diz se e como recorrer em «‹título da seção›»."*, com o caminho para ela; sem a
  seção, nada sobre recurso.
- **FR-6415**: Nenhum texto do portal MUST dizer que a documentação da pessoa foi disponibilizada,
  encaminhada, entregue ou recebida por setor, nem apresentar a disponibilização da `117` como
  matrícula, contratação ou formalização concluída (9ª decisão).

#### D. O contato

- **FR-6416**: O contato MUST ser o canal de atendimento da unidade do Edital, com a recaída no canal da
  instalação da FR-3214 da `109`, mostrado como link (e-mail ou endereço) na convocação, no resultado e
  no aviso. Nenhum campo de contato da comissão MUST ser criado nesta entrega (5ª decisão).
- **FR-6417**: Sem canal nenhum, a linha *"Atendimento"* e a frase *"fale com o atendimento"* MUST NOT
  aparecer nas telas da convocação e do resultado, nem nas mensagens da convocação, da correção e do
  aviso do desfecho, e nenhuma delas MUST dizer *"o atendimento institucional"*. As outras telas do
  portal que usam a frase genérica não mudam.
- **FR-6418**: Os cenários de treinamento da `134` MUST declarar um canal fictício na unidade que
  usam, para que os estudos vejam o contato como em produção.

#### E. A desistência pelo portal: o pedido

- **FR-6419**: A página da convocação MUST oferecer *"Desistir desta convocação"* à pessoa cuja
  convocação vigente está visível no portal, sem desfecho e sem pedido pendente, com o Processo fora de
  estado final. A oferta MUST ser link secundário, no fim da página, e nunca a ação principal. A página
  de confirmação MUST dizer, nesta ordem: que o pedido vai à comissão; que **pedir ainda não é
  desistir** — a desistência só vale quando a comissão a registrar; que, registrada, ela encerra a
  convocação e não se desfaz pelo portal; que o pedido não suspende nem prorroga o prazo, e que até o
  registro a pessoa pode continuar enviando documentos; e que, até o registro, o pedido pode ser
  cancelado. A página MUST pedir a ciência, numa caixa a marcar, e MUST NOT ter campo de motivo nem
  texto livre (D-007).
- **FR-6420**: O pedido MUST ser gravado com a convocação, a inscrição, a credencial que o fez, o
  instante e um protocolo, em registro que não se altera nem se exclui, e MUST ser recusado sem a
  ciência, com a convocação já desfechada, com pedido pendente, com o Processo em estado final ou com
  a convocação fora do portal. O comando MUST correr sob a trava da convocação e com chave de
  idempotência.
- **FR-6421**: Com pedido pendente, a página MUST dizer *"Pedido de desistência enviado em ‹data e
  hora›, protocolo ‹protocolo›. A desistência ainda não foi registrada: até a comissão registrá-la, a
  sua convocação continua, com o mesmo prazo, e você pode cancelar o pedido."*, e MUST continuar
  mostrando o prazo como antes do pedido.
- **FR-6422**: O pedido pendente MUST NOT mudar o que a pessoa pode enviar nem o que a comissão pode
  conferir: os envios de documento e do Requerimento continuam pelas regras vigentes, e o prazo não se
  suspende, não se prorroga e não se reinicia (7ª decisão).
- **FR-6423**: Com pedido pendente, a página MUST oferecer *"Cancelar o pedido de desistência"*, com
  confirmação. O cancelamento MUST ser gravado como registro próprio, que não altera nem exclui o
  pedido; o pedido cancelado MUST continuar no histórico da convocação, na gestão, com o
  cancelamento; e a página MUST voltar a oferecer *"Desistir desta convocação"* (6ª decisão). O
  cancelamento MUST ser recusado depois do desfecho.
- **FR-6424**: O pedido e o cancelamento MUST entrar na trilha, sem endereço de e-mail.

#### F. A desistência pelo portal: a homologação

- **FR-6425**: Na condução da convocação, o cartão da pessoa com pedido pendente MUST mostrar *"Pedido
  de desistência pelo portal em ‹data e hora›"* e oferecer *"Registrar a desistência pedida"* a quem
  pode registrar desfecho. O atalho MUST ser gesto próprio, e não o seletor do desfecho (D-016): a
  espécie é a desistência expressa, e o fundamento derivado é *"Desistência expressa pedida pela
  pessoa convocada, pelo portal, em ‹data e hora›, protocolo ‹protocolo›."*, ao qual quem registra
  pode acrescentar complemento. A conferência do texto e a prévia da FR-3993 da `125` MUST valer.
- **FR-6426**: Registrar o desfecho de uma convocação com pedido pendente MUST encerrar o pedido como
  **homologado**, se o desfecho for a desistência expressa, ou como **encerrado por outro desfecho**,
  nos demais casos. Nenhum pedido MUST virar desfecho sem esse registro.
- **FR-6427**: Com pedido pendente, o cartão MUST mostrar o pedido e o atalho antes de qualquer outra
  indicação de desfecho, inclusive a do não atendimento da FR-5809 da `152`.
- **FR-6428**: A confirmação de qualquer outro desfecho, individual, numa convocação com pedido
  pendente MUST dizer que há pedido de desistência pendente, com data e protocolo, e MUST pedir
  ciência numa marca desmarcada, que o comando confere. A ciência se soma às da `152`, sem
  substituí-las.
- **FR-6429**: O registro do não atendimento dos vencidos em lote MUST deixar de fora a pessoa com
  pedido pendente, contada à parte como *"pedido de desistência pendente"* (FR-878 da `050`, revista).
- **FR-6430**: O *"O que fazer agora"* da condução MUST derivar a providência *"Registrar a desistência
  pedida pelo portal"* enquanto houver pedido pendente no recorte, do mesmo cálculo do cartão, como
  providência *Pendente* de quem pode registrar desfecho, na ordem da FR-4082 da `127`, e uma só por
  recorte, com a contagem.
- **FR-6431**: A confirmação de encerrar o Edital e a de encerrar o Processo MUST advertir dos pedidos
  de desistência pendentes, com a contagem e o caminho para a condução, ao lado da advertência da
  FR-6124 e da FR-6128 da `153`. A advertência MUST NOT impedir o encerramento (D-017).

#### G. A mensagem da convocação

- **FR-6432**: A mensagem inicial de convocação MUST dizer *"Prazo para atender: até ‹data por
  extenso›."*, e a da correção *"Prazo válido para atender: até ‹data por extenso›."*, nas versões em
  texto puro e em HTML, sem *"contado do envio desta mensagem"* (FR-3883 da `121`, revista). Mensagens
  já enviadas e os resumos gravados delas MUST NOT mudar.

#### H. O aviso do desfecho

- **FR-6433**: A FR-084 da `010` MUST ser revista para uma **sexta** situação: o **aviso do desfecho da
  convocação**, que quem registra o desfecho pede, de forma explícita, que seja enviado à pessoa
  convocada, sem efeito sobre prazo, resultado ou direito. A guarda
  `backend/tests/test_situacoes_de_mensagem.py` MUST contar seis.
- **FR-6434**: Com a habilitação ligada, a confirmação de todo registro de desfecho — individual, pelo
  atalho da desistência pedida e no não atendimento dos vencidos em lote — MUST oferecer *"Avisar a
  pessoa por e-mail"* (no lote, *"Avisar as pessoas por e-mail"*), **desmarcada** por padrão (8ª
  decisão). Nada MUST gravar aviso de desfecho sem que quem confirma a marque.
- **FR-6435**: Marcada a opção, o aviso MUST ser gravado na mesma transação do desfecho, no registro de
  avisos da `066`, e enviado só pelo despacho dela, fora da requisição.
- **FR-6436**: A resposta da confirmação MUST dizer *"Aviso solicitado"*, e nunca *"enviado"*. O cartão
  da convocação MUST mostrar o estado do aviso pelo registro da `066`: *"Aviso solicitado em ‹data›"*
  até a tentativa; *"Aviso enviado em ‹data e hora›"* depois de o servidor de correio aceitar a
  mensagem — nunca *"recebido"* (FR-288a da `019`) —; e, falhando, expirando ou interrompido, o
  estado e o motivo.
- **FR-6437**: Antes de cada tentativa, o despacho MUST reler o desfecho e interromper o aviso, com o
  motivo, quando ele deixou de ser o desfecho da convocação vigente, como a FR-4623 da `134` faz com a
  pendência. A janela de despacho da `066` MUST valer.
- **FR-6438**: O assunto MUST ser *"‹instituição› · Edital ‹número›/‹ano›: há resultado registrado na
  sua convocação"*, e MUST NOT começar por "Convocação". O corpo MUST dizer *"Há resultado registrado
  da sua convocação no Edital ‹número›/‹ano›. Para ver o resultado e o que fazer depois, entre na sua
  área do candidato."*, com o link da convocação (o mesmo da mensagem da convocação), a instrução de
  acesso por código, o contato (FR-6416), quando houver, e o rodapé fixo *"Este aviso não é o
  registro oficial e não altera prazo nem resultado. O que vale é o que está na sua área do candidato
  e o que o Edital publica."* O texto MUST ser o mesmo para todas as espécies, e o corpo e o assunto
  MUST NOT conter a espécie, o rótulo, o fundamento, o nome, o CPF, o protocolo, a modalidade nem a
  posição. A mensagem MUST NOT ter anexo (1ª decisão).
- **FR-6439**: A pessoa sem endereço MUST ficar sem aviso, e a confirmação MUST mostrar a opção
  desabilitada, com a razão.

#### I. A habilitação

- **FR-6440**: O aviso do desfecho MUST depender de uma chave própria, `AVISOS_DE_DESFECHO`, e só valer
  com ela **e** `AVISOS_AOS_CANDIDATOS` ligadas (2ª decisão). As duas MUST vir desligadas em produção,
  ligadas em `development` e `test`.
- **FR-6441**: Com a habilitação desligada, a opção da FR-6434 MUST NOT aparecer, o POST que a trouxer
  MUST ser recusado com `aviso_envio_desabilitado` sem registrar o desfecho, e o despacho MUST NOT
  enviar aviso de desfecho.
- **FR-6442**: A habilitação MUST NOT condicionar nenhum outro requisito desta spec: as seções A a G
  MUST funcionar igualmente com ela ligada ou desligada.
- **FR-6443**: A chave MUST ser ligada em produção só depois de resolvidas as pendências PI-1 a PI-6
  para esta finalidade. A ligação é ato de configuração; o documento de implantação MUST registrar a
  validação obtida, quem a emitiu, a data e a data em que a chave foi ligada.

#### J. As revisões

- **FR-6444**: As revisões que esta spec impõe MUST estar escritas nas specs de origem, com a redação
  anterior preservada, e vigorar com a implementação desta: a FR-084 da `010`; a FR-1172 e a FR-1177
  da `063`; a FR-3750 da `118`; a FR-3883 da `121`; a FR-3993 da `125`; e a FR-878 da `050`.

### Requisitos de experiência

- **UX-620**: A frase simples MUST ter no máximo duas frases antes do próximo passo, e MUST vir antes
  de qualquer protocolo ou fundamento.
- **UX-621**: O fundamento recolhido MUST abrir pelo teclado, anunciar o estado (aberto ou fechado) e
  não ter rolagem horizontal a 375 px.
- **UX-622**: *"Desistir desta convocação"* MUST ter aparência de link secundário, sem a cor de ação
  principal nem a de perigo, e a confirmação MUST ter o botão *"Enviar o pedido de desistência"* e o
  caminho de volta *"Voltar à convocação"*, este primeiro na ordem do teclado. *"Cancelar o pedido de
  desistência"* MUST ter o mesmo peso visual de *"Desistir desta convocação"*.
- **UX-623**: A opção *"Avisar a pessoa por e-mail"* MUST dizer, ao lado, *"O e-mail diz só que há
  resultado registrado, sem dizer qual. Ele sai depois, pelo envio automático."*

### Key Entities

- **Pedido de desistência**: a manifestação da pessoa convocada, feita pelo portal, sobre uma
  chamada. Guarda a convocação, a inscrição, a credencial, o instante e o protocolo. Não se altera nem
  se exclui; o estado (pendente, cancelado, homologado, encerrado por outro desfecho) sai dos
  registros que o sucedem.
- **Cancelamento do pedido**: o registro da pessoa que desfaz o próprio pedido antes do desfecho.
- **Aviso do desfecho**: um aviso no registro da `066`, de origem *desfecho*, com um destinatário,
  ligado ao desfecho que o motivou.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2120**: Nas sete espécies de desfecho e nas três de convocação, nenhum termo da FR-6403 aparece
  no portal fora do fundamento recolhido, verificado por varredura sobre as telas renderizadas.
- **SC-2121**: Numa rodada do estudo da jornada final com pelo menos cinco pessoas que não conhecem o
  sistema, ao menos quatro dizem, só pela tela do aceite, onde está o próximo passo e com quem falar;
  e ao menos quatro dizem, pela tela do não atendimento, o que aconteceu e quando.
- **SC-2122**: Em 100% das telas da convocação e do resultado com canal configurado, o contato aparece
  como link; em nenhuma aparece *"o atendimento institucional"*.
- **SC-2123**: Num Edital sem a seção aplicável preenchida, nenhuma tela do aceite fala de matrícula,
  bolsa ou contratação como próximo passo.
- **SC-2124**: Toda desistência registrada a partir de pedido cita o protocolo do pedido, e todo pedido
  termina homologado, cancelado ou encerrado por outro desfecho — nenhum vira desfecho sem registro da
  comissão, e nenhum pedido ou cancelamento some do histórico.
- **SC-2125**: Com pedido pendente, o vencimento e o que a pessoa pode enviar são, em 100% dos casos,
  os mesmos de antes do pedido.
- **SC-2126**: Repetida a etapa E do estudo, a desistência de Cecília tem pedido no sistema, com
  instante e protocolo, antes do desfecho.
- **SC-2127**: Com a habilitação desligada, zero aviso de desfecho é gravado ou enviado, e as telas do
  portal são idênticas, letra a letra, às da habilitação ligada.
- **SC-2128**: Com a habilitação ligada, só os desfechos registrados com a opção marcada produzem aviso,
  um cada, e nenhuma tela diz *"enviado"* antes de o despacho registrar a aceitação pelo servidor.
- **SC-2129**: Nenhum aviso de desfecho contém espécie, rótulo, fundamento, nome, CPF, protocolo ou
  modalidade.
- **SC-2130**: Nenhuma mensagem de convocação ou de correção enviada depois da implementação contém
  *"contado do envio"*.

---

## Assumptions

- **A `154` já está na `main`.** Os títulos e as frases das chamadas abertas são os dela; esta spec só
  toca o estado com desfecho, o fundamento da convocação e a mensagem.
- **A `152` está sendo implementada** (plano no PR #480). Esta spec não muda nenhum requisito dela; os
  encontros estão na seção própria, e a implementação desta parte da `main` com a `152`.
- **O despacho da `066` aguenta a sexta situação** sem processo novo.
- **A seção aplicável tem caminho próprio na página pública do Edital.** Se não tiver, o plano decide
  entre criar a âncora e levar ao topo da página.
- **O pedido de desistência é ato da pessoa autenticada pelo código de acesso**, a mesma prova de
  autoria da inscrição e dos documentos.
- **O pedido e o cancelamento são tabelas que não se alteram nem se excluem**: entram na contagem das
  tabelas protegidas que o provisionamento informa, como as append-only de antes.

---

## As revisões, escritas nas specs de origem

Cada alínea revista tem a nova redação, a marca *"revista pela `156` em 2026-11-11, que vigora com a
implementação dela"* e a redação anterior preservada ao fim da alínea.

| Spec | Requisito | O que muda |
|---|---|---|
| `010` | FR-084 | sexta situação: o aviso do desfecho da convocação, pedido por quem registra o desfecho |
| `063` | FR-1172 | o porquê do desfecho em duas camadas: a frase simples e o fundamento recolhido, com a data |
| `063` | FR-1177 | acréscimo, sobre a redação da `154`: a frase simples de desfecho registrado descreve o ato, e não é frase de consequência |
| `118` | FR-3750 | a segunda frase do aceite dá lugar ao próximo passo pelo Edital publicado e ao contato |
| `121` | FR-3883 | o prazo da mensagem inicial sem *"contado do envio desta mensagem"*, e o atendimento omitido sem canal |
| `125` | FR-3993 | a prévia mostra as duas camadas, como o portal as mostrará |
| `050` | FR-878 | o lote do não atendimento deixa de fora quem tem pedido de desistência pendente |

**Sem mudança de redação, e por quê**: a FR-6206 da `154` (a FR-3750 revista mantém o título, o
rótulo e a frase de que o registro não é matrícula, bolsa nem contrato); a FR-5813 e a FR-5839 da
`152` (a primeira segue o portal; a segunda vale para o seletor, e o atalho é gesto próprio); a
FR-3885 da `121` (o rótulo *"Prazo válido para atender"* não muda; a cláusula do envio vem do *"resto
como a inicial"*, e sai com a FR-3883); a FR-4606 da `134` (o pedido não é desfecho, D-015).

---

## Decisões desta spec

Propostas de desenho, sujeitas à revisão do PR.

#### D-001 — As revisões se escrevem antes do plano, e vigoram com a implementação

A instrução do usuário pede as revisões na documentação antes do plano. Escritas agora, com a marca de
vigência, o plano e as tarefas leem a regra que vão implementar, e a redação anterior continua
descrevendo o sistema até lá.

#### D-002 — Duas camadas, derivadas na leitura

A frase simples não se grava: é derivada da espécie e dos dados do ato quando a tela é lida. Gravar
exigiria mudar ato que não se altera ou criar uma segunda versão do mesmo fato; derivar permite
corrigir a frase sem tocar no ato.

#### D-003 — "Encerrada para você", e não "perdeu a vaga"

O indeferimento pode ser regularizado (a convocação para regularizar da `019`), e a reclassificação
devolve a pessoa à fila. *"Perdeu a vaga"* seria falso em dois de cinco desfechos de exclusão.

#### D-004 — A seção aplicável é a do catálogo, com o título do Edital

O catálogo das seções é declarado (`054`, `069`), e a seção que trata da etapa depois do resultado
tem chave fixa. O sistema não lê o texto para adivinhar o próximo passo: ele só aponta a seção que
existe, com o título que o Edital lhe deu. Um Edital de bolsista que não a preencha cai na consulta ao
Edital, e nada presume matrícula (4ª decisão).

#### D-005 — Sem canal, nenhuma linha

A frase genérica só aparece onde não há canal nenhum, o que a produção não admite. Em desenvolvimento
e em estudo, ela fez parecer que o contato não existe.

#### D-006 — Desistir é pedido, e o desfecho continua da comissão

Um desfecho por convocação, registrado por quem pode registrá-lo (FR-273 da `019`). O pedido é a
prova da manifestação, e o desfecho a cita.

#### D-007 — Sem motivo no pedido

Um campo de motivo coletaria o que a pessoa escrever — saúde, trabalho, família —, que a comissão não
precisa para registrar a desistência. Minimização (Princípio III da Constituição).

#### D-008 — Sem recibo por e-mail do pedido

O comprovante é a própria página, com instante e protocolo. Um recibo por e-mail seria uma sétima
situação da FR-084 da `010`, com a mesma validação pendente.

#### D-009 — O pedido é da chamada

Como o limite diário da `134`, o pedido pertence à chamada (a raiz), e não à convocação vigente: a
correção por sucessão não o perde nem abre um segundo.

#### D-010 — O pedido vale depois do vencimento

Até o desfecho, a convocação é da comissão decidir, e a manifestação da pessoa ajuda a decidir certo.

#### D-011 — Nenhum aviso retroativo

Ligar a habilitação não avisa desfechos já registrados, como a `066` decidiu para a reativação da
chave dela.

#### D-012 — O aviso nasce no gesto do desfecho

A FR-084 da `010` exige decisão humana. Aqui o desfecho é o ato, e a confirmação dele é o gesto; a
marca desmarcada (8ª decisão) faz do aviso uma solicitação explícita.

#### D-013 — O lote do não atendimento deixa de fora quem pediu desistência

Registrar em lote o não atendimento de quem pediu para desistir registraria um fato diferente do que
aconteceu. O registro individual continua possível, com a ciência da FR-6428.

#### D-014 — A mensagem da convocação diz só a data

O prazo é a data informada no ato, e o envio só o põe em curso
(`doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`). *"Contado do envio desta mensagem"* é
inexato na primeira mensagem e enganoso na segunda.

#### D-015 — O pedido não muda a convocação

Pedir não é desistir (6ª decisão), e a pessoa pode cancelar e cumprir (7ª decisão). Por isso o prazo,
os envios, a conferência e o aviso de pendência da `134` continuam como estavam: tirá-la do aviso de
pendência a deixaria sem saber de uma correção justamente quando ainda pode voltar atrás.

#### D-016 — O atalho da desistência pedida é gesto próprio

A FR-5839 da `152` proíbe espécie pré-escolhida no seletor, para que ninguém registre por inércia a
única espécie oferecida. O atalho não é o seletor: nasce de um pedido registrado, nomeia a espécie no
botão e passa pela conferência do texto, como o atalho de indeferimento da `152`.

#### D-017 — Encerrar com pedido pendente adverte, e não impede

O encerramento fecha a escrita, e o pedido pendente ficaria sem homologação. Impedir encerrar por
pedido de candidato daria a ele um veto sobre o calendário do certame; a advertência, ao lado da da
`153`, dá à comissão a chance de registrar antes.
