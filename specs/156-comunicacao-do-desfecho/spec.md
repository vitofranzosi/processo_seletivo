# Feature Specification: O desfecho da convocação comunicado ao candidato

**Feature Branch**: `claude/intelligent-robinson-4466a5`, sobre a `main` em `d1ec1e0a` (com a `154`, PR #479, mergeada).
Revista em `claude/156-revisao-das-decisoes`, sobre a `main` em `17e9665c`.

**Created**: 2026-11-11

**Status**: **Mergeada em 11/11/2026 (PR #485) e revista no mesmo dia com as decisões do usuário;
sem plano nem código.** As nove perguntas (P-1 a P-9) foram respondidas pelo usuário — a *1ª* à *9ª
decisão*, em *Clarifications* —, e **não se reabrem**. Cada requisito alterado por elas traz a marca
*"revista em 2026-11-11"* e a redação mergeada ao fim da alínea; os acrescidos trazem *"acrescida em
2026-11-11"*. Nenhum identificador mergeado mudou de sentido nem de número. As propostas de desenho
(D-001 a D-017) continuam sujeitas à revisão do PR. A **validação institucional** do envio está nas
pendências PI-1 a PI-6, que condicionam só a habilitação do envio.

> **Status anterior, de 11/11/2026 (PR #485), preservado:** *"Rascunho, só a spec. Não há plano,
> tarefas nem código. As propostas de desenho (D-001 a D-014, ao fim) estão sujeitas à revisão do PR,
> e as nove perguntas ao usuário (P-1 a P-9, em Perguntas ao usuário) estão abertas. Onde uma
> pergunta está aberta, o texto adota a recomendação dela, marcada como tal, para que a spec continue
> coerente; a resposta pode trocá-la."*

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
- *(acrescidos em 2026-11-11)* **Campo de contato da comissão** (5ª decisão) e campo estruturado do
  próximo passo no Edital (4ª decisão); **aviso da disponibilização ao setor** (9ª decisão); e as
  frases do portal que dizem *"contado do envio da comunicação"* no cartão do prazo (FR-3998 da
  `125`), porque o achado 18 é sobre a mensagem.

---

## Clarifications

### Session 2026-11-11 (decisões do usuário sobre as perguntas P-1 a P-9)

*Acrescida em 2026-11-11.* As respostas do usuário às nove perguntas da redação mergeada. Não se
reabrem. Onde a redação mergeada adotava uma recomendação que a resposta não confirmou, a alínea foi
revista, com a redação anterior preservada.

- Q (P-1): O que o e-mail do desfecho diz? → A: **Texto neutro**, que informa que há resultado
  registrado e indica o acesso ao portal. Resultado e fundamento ficam no ambiente autenticado.
  *(1ª decisão)*
- Q (P-2): Chave própria ou a da `066`? → A: **Chave própria, dependente também da chave geral dos
  avisos.** O envio permanece desligado até a validação institucional correspondente. *(2ª decisão)*
- Q (P-3): Quem valida, e um pedido só cobre as três finalidades? → A: **O responsável, a abrangência
  e a existência do pedido de validação continuam como pendências institucionais**, e não se
  confirmam por inferência. A spec distingue o que as specs anteriores exigem das hipóteses desta
  proposta. O envio permanece desligado; as partes independentes podem avançar. *(3ª decisão)*
- Q (P-4): Qual é o próximo passo do aceite? → A: **Orientar para a seção aplicável do Edital publicado
  e oferecer o contato. Não presumir matrícula**: pode haver bolsa, contratação ou outra formalização.
  Sem orientação identificável, indicar a consulta ao Edital e ao atendimento, **sem inventar um
  próximo passo**. *(4ª decisão)*
- Q (P-5): Qual contato? → A: **O canal da unidade, com alternativa no canal da instalação.** Nenhum
  campo da comissão nesta entrega. A linha é omitida **somente quando os dois faltarem**. *(5ª
  decisão)*
- Q (P-6): O pedido de desistência pode ser cancelado? → A: **Sim, enquanto a comissão não tiver
  registrado o desfecho.** Pedido e cancelamento preservam o histórico. A tela deixa claro que
  **solicitar a desistência ainda não é ter a desistência efetivada**. *(6ª decisão)*
- Q (P-7): Com o pedido pendente, o envio de documentos fica suspenso? → A: **Não.** Os envios
  previstos nas regras vigentes continuam permitidos enquanto o pedido estiver pendente; o prazo não é
  suspenso nem prorrogado; o candidato não é bloqueado enquanto ainda pode cancelar o pedido e cumprir
  a convocação. *(7ª decisão)*
- Q (P-8): A opção de avisar vem marcada? → A: **Desmarcada por padrão**, com solicitação explícita.
  A confirmação distingue **aviso solicitado** de **aviso enviado**. *(8ª decisão)*
- Q (P-9): O portal diz que a documentação foi disponibilizada ao setor? → A: **Sem aviso específico
  nesta entrega.** Essa operação interna não se apresenta como matrícula, contratação ou formalização
  concluída. *(9ª decisão)*
- Instrução que acompanhou as decisões: registrar as alterações em revisão explícita, preservando as
  redações anteriores; incorporar as revisões dos requisitos de outras specs na documentação **antes
  do plano**; e explicitar as consequências do novo pedido de desistência e os encontros com a `152`
  e a `153`.

---

## A validação institucional do envio

*Seção revista em 2026-11-11 pela 3ª decisão; a redação anterior, sob o título "A dependência de LGPD,
nomeada", está ao fim dela.* Ela separa o que já é exigência escrita do que é hipótese desta
proposta, e diz o que a falta da validação impede.

### O que as specs anteriores exigem

São requisitos escritos e vigentes. Esta spec não os altera; ela os estende à finalidade nova.

| Origem | O que está escrito |
|---|---|
| decisão 10 da `066` (decisões recebidas) | *"A validação institucional fica registrada como pendente, e é exigida antes da entrada em produção."* |
| precondição de produção da `066` | *"A base legal do uso do e-mail para aviso complementar e a retenção da lista de destinatários dependem de validação institucional, com o encarregado de dados, antes da entrada em produção."* E: *"Se a base legal exigir direito de oposição, o descadastro entra como incremento."* |
| decisão da chave de habilitação da `066` | `AVISOS_AOS_CANDIDATOS` desligada em produção *"até a validação institucional de LGPD e da infraestrutura de correio"*; a reativação não envia o que ficou fora da janela de despacho |
| 5ª decisão da `134` | a mesma chave, desligada em produção *"até a validação de LGPD e de SPF/DKIM"* |
| PC-003 da `010` | a área do candidato não entra em produção com dados reais sem política institucional documentada de retenção e descarte |

O que essas exigências deixam dito: há uma validação institucional de LGPD pendente, sobre a base
legal do uso do e-mail para aviso e sobre a retenção da lista de destinatários, e há uma validação,
separada, da infraestrutura de correio. Quem a emite, se foi pedida e quanto ela alcança não está
escrito em lugar nenhum, e esta spec não o supõe (PI-1 a PI-3).

### As hipóteses desta proposta

Não confirmadas. Servem para preparar a validação, e não a substituem nem a antecipam.

- **H-1 — A base legal.** As hipóteses que a validação deve confirmar ou afastar: o art. 7º, III, com
  o art. 23 da LGPD (tratamento pelo poder público para executar atribuição legal do serviço
  público); e o art. 7º, II (obrigação legal), se se entender que o dever de dar ciência ao
  interessado dos atos que restringem direito (Lei nº 9.784/1999, art. 26 e 28) alcança este aviso. A
  proposta **não** usa consentimento: entre poder público e candidato ele não é livre, e o aviso
  deixaria de alcançar quem não respondesse.
- **H-2 — A minimização.** A hipótese é que o texto neutro da 1ª decisão reduza o tratamento ao
  endereço e ao fato de haver resultado registrado no Edital tal, sem a espécie do desfecho, que no
  indeferimento de quem concorre por reserva de vagas poderia revelar dado sensível por inferência
  (art. 5º, II, e art. 11).

### O tratamento a validar

| | O que é |
|---|---|
| **Dado tratado** | o endereço de e-mail da pessoa convocada, na ordem da `066` (a credencial verificada pelo código de acesso antes do endereço da inscrição); o número e o ano do Edital; e, pelo próprio envio, o fato de que esta pessoa foi convocada e teve o resultado da convocação registrado. Sem espécie, rótulo, fundamento, nome, CPF, protocolo, modalidade nem posição (FR-6435) |
| **Finalidade** | avisar a pessoa de que há resultado registrado da sua convocação, para que ela o consulte no portal e cumpra a providência seguinte que o Edital indica, ou exerça no prazo o direito de recorrer que o Edital preveja. O aviso não é o ato, não intima e não altera prazo nem resultado |
| **Base legal** | a confirmar (H-1, PI-4) |
| **Operador** | o serviço de correio que transmite a mensagem |
| **Retenção** | o registro do aviso e de cada destinatário, que a `066` guarda, pela política da PC-003 da `010` |
| **Direitos do titular** | se a base legal exigir oposição, o descadastro entra como incremento, como a `066` previa |

### As pendências institucionais

Condicionam só a habilitação do envio (FR-6440). São o que precisa existir fora do sistema antes de
ligar a chave, e nenhum texto do sistema as dá por resolvidas.

- **PI-1 — Responsável pela validação**: quem a emite e quem a aprova.
- **PI-2 — Existência do pedido**: se a validação foi pedida, por quem e quando.
- **PI-3 — Abrangência**: se uma validação cobre a `066`, a `134` e esta, ou se esta precisa de uma
  própria. A chave própria (2ª decisão) funciona nos dois casos.
- **PI-4 — Base legal**: a hipótese confirmada, e o que ela exige (H-1).
- **PI-5 — Retenção**: a política da PC-003 da `010`.
- **PI-6 — Infraestrutura de correio**: SPF e DKIM do remetente. Não é LGPD, e é exigida pela `066`
  e pela `134` do mesmo modo.

### O que a falta impede

**Só o envio do aviso do desfecho por e-mail**: a opção de avisar, no registro do desfecho, e a
saída da mensagem pelo despacho. Com a habilitação desligada, a opção não aparece, nada é gravado, e
o despacho não tem o que enviar (FR-6430, FR-6437 e FR-6438). O envio fica implementado e desligado.

### O que ela não impede

| Parte desta spec | Por que não depende da validação |
|---|---|
| O portal em cada desfecho, nas duas camadas (§A a §C) | Mostra à própria pessoa, autenticada, o que o sistema já mostra a ela hoje, em outras palavras. Nenhum dado novo, nenhuma finalidade nova |
| O contato (§D) | É dado institucional, e não pessoal |
| A desistência pelo portal (§E e §F) | É manifestação da pessoa no próprio procedimento do certame, pela mesma via em que ela se inscreve e envia documentos. Sem campo de motivo (D-007), não coleta dado novo. A PC-003 da `010` vale para ela como vale para o resto do portal |
| O texto corrigido da mensagem da convocação (§G) | A mensagem já sai, na terceira situação da FR-084 da `010`, que é o próprio ato; muda a redação, e não o tratamento |
| O plano, a implementação e os testes do aviso | A chave vem ligada em `development` e `test`, como a da `066` |

### Redação anterior desta seção, preservada

*Mergeada em 11/11/2026 (PR #485) sob o título "A dependência de LGPD, nomeada". A 3ª decisão a substituiu: o responsável, o alcance e a existência do pedido não estão confirmados, e o que esta redação dizia deles era recomendação, e não fato.*

>
> Esta seção responde à orientação do usuário: qual validação falta, de quem, sobre qual tratamento,
> e o que ela impede.
>
> ### Qual validação
>
> **O parecer do Encarregado pelo Tratamento de Dados Pessoais do Ifes** (art. 41 da LGPD), em nome do
> controlador, que é o Ifes, sobre o tratamento descrito abaixo. É a mesma *"validação institucional,
> com o encarregado de dados"* que a `066` registrou como precondição de produção e que a `134`
> herdou; esta spec pede que ela cubra **uma finalidade a mais**, e a nomeia. Nada indica, no
> repositório, que esse parecer tenha sido pedido ou emitido (P-3).
>
> Ao lado dela, e **independente dela**, continua pendente a validação da infraestrutura de correio
> (SPF e DKIM do remetente), que a `066` e a `134` também exigem. Não é LGPD, e a habilitação depende
> das duas (FR-6440).
>
> ### Sobre qual tratamento
>
> | | O que é |
> |---|---|
> | **Dado tratado** | o endereço de e-mail da pessoa convocada, na ordem que a `066` usa (a credencial verificada pelo código de acesso antes do endereço da inscrição); o número e o ano do Edital; o instante do registro; e, por consequência do próprio envio, **o fato de que esta pessoa foi convocada e teve o resultado da convocação registrado**. Com o texto recomendado (P-1), o corpo não leva a espécie do desfecho, o motivo, o nome, o CPF, a modalidade nem a posição |
> | **Dado que o texto recomendado evita** | a espécie do desfecho (*indeferido*, *não atendida*), que é resultado individual, e que no indeferimento de quem concorre por reserva de vagas pode revelar, por inferência, dado sensível (art. 5º, II, e art. 11 da LGPD) — a razão pela qual a decisão 5 da `066` tirou o resultado individual do corpo do aviso |
> | **Finalidade** | avisar a pessoa de que há resultado registrado da sua convocação, para que ela o consulte no portal e cumpra a providência seguinte que o Edital indica, ou exerça no prazo o direito de recorrer que o Edital preveja. O aviso não é o ato, não intima e não altera prazo nem resultado |
> | **Base legal** | **a definir pelo parecer**. As hipóteses que ele deve confirmar ou afastar: o art. 7º, III, com o art. 23 (tratamento pelo poder público para executar política pública e atribuição legal do serviço público); e o art. 7º, II (cumprimento de obrigação legal), se o parecer entender que o dever de dar ciência ao interessado dos atos que restringem direito (Lei nº 9.784/1999, art. 26 e 28) alcança este aviso. A spec **não** propõe consentimento: entre poder público e candidato ele não é livre, e o aviso deixaria de alcançar quem não respondesse |
> | **Operador** | o serviço de correio que transmite a mensagem. Se for de terceiro, o parecer diz se o contrato o cobre |
> | **Retenção** | o registro do aviso e de cada destinatário, que a `066` guarda; a política de retenção é a mesma que a PC-003 da `010` já exige do portal, e continua pendente |
> | **Direitos do titular** | se a base legal escolhida exigir direito de oposição, o descadastro entra como incremento, como a `066` já previa |
>
> ### O que ela impede
>
> **Só o envio do aviso do desfecho por e-mail**: a opção de avisar, no registro do desfecho, e a
> saída da mensagem pelo despacho. Com a habilitação desligada, a opção não aparece, nada é gravado, e
> o despacho não tem o que enviar (FR-6430, FR-6437 e FR-6438).
>
> ### O que ela não impede
>
> | Parte desta spec | Por que não depende do parecer |
> |---|---|
> | O portal em cada desfecho, nas duas camadas (§A a §C) | Mostra à própria pessoa, autenticada, o que o sistema já mostra a ela hoje, em outras palavras. Nenhum dado novo, nenhuma finalidade nova |
> | O contato da comissão (§D) | É dado institucional, e não pessoal |
> | A desistência pelo portal (§E e §F) | É manifestação da pessoa no próprio procedimento do certame, pela mesma via e com a mesma base em que ela se inscreveu e envia documentos. Sem campo de motivo (D-007), não coleta dado novo. A PC-003 da `010` vale para ela como vale para o resto do portal |
> | O texto corrigido da mensagem da convocação (§G) | A mensagem já sai, na terceira situação da FR-084 da `010`, que é o próprio ato; a correção muda a redação, e não o tratamento |
> | A implementação e os testes do aviso | A chave vem ligada em `development` e `test`, como a da `066`; tudo pode ser construído e verificado antes do parecer |

---

## O que o pedido de desistência muda, e o que não muda

*Acrescida em 2026-11-11.* O pedido é registro novo, da pessoa, sobre a chamada (D-009). **Pedir não
é desistir** (6ª decisão): até a comissão registrar o desfecho, a convocação continua a mesma.

| Onde | Com o pedido pendente | Requisito |
|---|---|---|
| Prazo da convocação | não suspende, não prorroga, não reinicia | FR-6419, FR-6421 |
| Envio de documentos e do Requerimento | continua pelas regras vigentes (FR-3578 e FR-3582 da `115`) | FR-6421 |
| Conferência dos documentos | continua; a comissão pode conferir o que chegar | FR-6421 |
| Aviso de pendência da `134` | continua alcançando a pessoa: o pedido não é desfecho, e a pessoa pode cancelar e cumprir | D-015 |
| Ocupação, apuração, fila e sucessora | nada muda; o efeito na contagem nasce só do desfecho (FR-273 da `019`) | D-006 |
| Registro do desfecho individual, de qualquer espécie | possível; a confirmação avisa do pedido e pede ciência, salvo pelo atalho da desistência pedida | FR-6425 |
| Registro do não atendimento dos vencidos em lote | a pessoa fica de fora, contada à parte (FR-878 da `050`, revista) | FR-6426 |
| Atalho de indeferimento pelas pendências (`152`) | continua oferecido nas condições da FR-5800 da `152`; ao confirmar, a ciência do pedido se soma à da FR-5803 da `152` | FR-6425 |
| Correção da convocação por sucessão (`120`) | o pedido acompanha a convocação vigente da chamada | D-009 |
| "O que fazer agora" da condução (`127`) | ganha a providência *"Registrar a desistência pedida pelo portal"* | FR-6427 |
| Encerramento do Edital e do Processo | a confirmação adverte dos pedidos pendentes, sem impedir | FR-6444 |
| Formalização (`117`, `153`) | nada: a pessoa só fica apta com aceite | §Encontros |
| Trilha | pedido e cancelamento, sem endereço | FR-6423 |

---

## Encontros com a `152` e a `153`

*Acrescida em 2026-11-11.*

**Com a `152`** (prevenção nos atos irreversíveis):

- **O seletor do desfecho continua sem espécie pré-escolhida** (FR-5839 da `152`). O atalho
  *"Registrar a desistência pedida"* não é o seletor: é gesto próprio, como o atalho de indeferimento
  da `152`, com a espécie fixa e o fundamento derivado do pedido (FR-6424, D-016). O seletor continua
  oferecendo as espécies que o comando aceita agora (FR-5835 da `152`); o pedido não muda essa
  verificação.
- **As ciências se somam.** Indeferir com o prazo em curso pede a ciência da FR-5803 da `152`; com
  pedido pendente, a confirmação pede também a da FR-6425. São duas marcas, cada uma com a sua frase,
  e o comando confere as duas.
- **A conferência do texto mostra as duas camadas.** A FR-5813 da `152` manda a conferência da
  chamada mostrar o fundamento *"como o candidato o lerá no portal"*, e a FR-3993 da `125` manda a
  prévia mostrar o texto *"como o candidato o verá"*. Com as duas camadas, a prévia passa a mostrar a
  frase simples e o fundamento (FR-6404; FR-3993 da `125`, revista). A FR-5813 não muda de redação:
  ela segue o portal.
- **O cartão sem nada apresentado** (FR-5809 da `152`) aponta o não atendimento; com pedido
  pendente, o cartão mostra antes o pedido e o atalho (FR-6443).
- **Nenhuma fronteira da `152` se afrouxa**: o comando de desfecho continua recusando o que recusa.

**Com a `153`** (formalização na jornada guiada):

- **Pessoa apta é a do aceite** (FR-6101 da `153`, FR-3669 da `117`). O pedido pendente não a torna
  apta nem a tira dessa condição; a desistência homologada é desfecho de exclusão, e a pessoa nunca
  chega à formalização.
- **As providências não se misturam**: as três da `153` são da fase Conclusão; a desta spec é da
  fase da convocação, na ordem fixa da FR-4082 da `127` (FR-6427).
- **A advertência do encerramento** (FR-6124 e FR-6128 da `153`) ganha uma linha irmã, a dos pedidos
  pendentes (FR-6444), na mesma confirmação e pela mesma regra de caminho.
- **O vocabulário é o mesmo** (9ª decisão; FR-6123 da `153`, FR-3751 da `118`): nada no portal diz
  que a documentação foi *encaminhada*, *entregue* ou *recebida*, nem apresenta a disponibilização
  ao setor como matrícula, contratação ou formalização concluída (FR-6413).

---

## As revisões, escritas nas specs de origem

*Acrescida em 2026-11-11.* Cada alínea revista tem a nova redação, a marca *"revista pela `156` em
2026-11-11, que vigora com a implementação dela"* e a redação anterior preservada ao fim da alínea.

| Spec | Requisito | O que muda |
|---|---|---|
| `010` | FR-084 | sexta situação: o aviso do desfecho da convocação, pedido por quem registra o desfecho |
| `063` | FR-1172 | o porquê do desfecho em duas camadas: a frase simples e o fundamento recolhido, com a data |
| `063` | FR-1177 | acréscimo, sobre a redação da `154`: a frase simples de desfecho registrado descreve o ato, e não é frase de consequência |
| `118` | FR-3750 | a segunda frase do aceite dá lugar ao próximo passo pelo Edital publicado e ao contato |
| `118` | FR-3740 | *(acrescida em 2026-11-13)* o fundamento da convocação em duas camadas, e a espécie dita na linha da chamada |
| `121` | FR-3883 | o prazo da mensagem inicial sem *"contado do envio desta mensagem"*, e o atendimento omitido sem canal |
| `125` | FR-3993 | a prévia mostra as duas camadas, como o portal as mostrará |
| `050` | FR-878 | o lote do não atendimento deixa de fora quem tem pedido de desistência pendente |

**Sem mudança de redação, e por quê**: a FR-6206 da `154` (a FR-3750 revista mantém o título, o
rótulo e a frase de que o registro não é matrícula, bolsa nem contrato); a FR-5813 e a FR-5839 da
`152` (a primeira segue o portal; a segunda vale para o seletor, e o atalho é gesto próprio); a
FR-3885 da `121` (o rótulo *"Prazo válido para atender"* não muda; a cláusula do envio vem do *"resto
como a inicial"*, e sai com a FR-3883); a FR-4606 da `134` (o pedido não é desfecho, D-015).

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
2. **Given** um Edital sem a seção aplicável preenchida — uma seleção de bolsista, por exemplo —,
   **When** Alice abre a convocação, **Then** lê *"Consulte o Edital publicado para saber o que vem
   depois."* e o contato, e nada fala de matrícula como próximo passo. *(Revisto em 2026-11-11 pela 4ª
   decisão; antes: "Given um Edital cuja seção da matrícula está vazia, When Alice abre a convocação,
   Then a frase diz que o próximo passo é o que o Edital publica, sem caminho para seção, e o contato
   aparece.")*
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
para uma das vagas da lista, pela posição dela, ou porque uma vaga ficou livre — e recolhe o
fundamento derivado da norma. *(Revisto em 2026-11-11: antes, "porque a posição dela está dentro das
vagas".)*

**Why this priority**: o mesmo jargão do achado 18, numa tela que a pessoa lê antes de agir.

**Independent Test**: para cada espécie de convocação, a tela mostra a frase simples e o fundamento
recolhido; *"faixa vigente"* e *"recorte"* não aparecem fora dele.

**Acceptance Scenarios**:

1. **Given** uma convocação para vaga inicial, **When** a pessoa abre a convocação, **Then** lê que foi
   chamada para uma das vagas da lista, pela posição dela na classificação. *(Revisto em 2026-11-11:
   antes, "porque a posição dela na lista está dentro das vagas da lista", expressão que a UX-158 da
   `063` proíbe.)*
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
4. **Given** o pedido pendente e o prazo correndo, **When** Fábio abre a convocação, **Then** o envio
   de documentos e do Requerimento continua oferecido pelas regras vigentes, e o prazo é o mesmo de
   antes do pedido. *(Revisto em 2026-11-11 pela 7ª decisão; antes: "Then o envio de documentos não é
   oferecido, e o prazo continua visível com a frase de que o pedido não o suspende (P-7).")*
5. **Given** o pedido pendente, **When** Fábio aciona *"Cancelar o pedido de desistência"* e confirma,
   **Then** o cancelamento é gravado como registro próprio, o pedido continua no histórico como
   cancelado, e a convocação volta a oferecer *"Desistir desta convocação"*. *(Revisto em 2026-11-11
   pela 6ª decisão; antes: "Then o cancelamento é gravado, e a convocação volta a ser a de antes
   (P-6).")*
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
e-mail"*, **desmarcado**. Marcado por ela e confirmado, a tela diz *"Aviso solicitado"*; o despacho da
`066` o envia depois, e só então o cartão diz *"Aviso enviado em ‹data›"*. O e-mail é neutro: diz que
há resultado registrado e como entrar no portal, com o contato. *(Revisto em 2026-11-11 pela 1ª e
pela 8ª decisão; antes: "vê, na confirmação, Avisar a pessoa por e-mail, marcado (P-8). Confirmado, o
aviso é gravado no registro de avisos e o despacho da 066 o envia: um e-mail neutro (P-1) que diz que
o resultado da convocação no Edital tal foi registrado e traz o link da convocação e o contato.")* Com a habilitação desligada, nada disso aparece, e o portal é
o mesmo.

**Why this priority**: é a parte do achado 07 que depende do parecer. Vem por último porque a
habilitação não depende desta equipe, e tudo o mais funciona sem ela.

**Independent Test**: com a habilitação ligada, registrar um aceite com a opção marcada grava um
aviso, e `despachar_avisos` o envia; com ela desligada, a opção não aparece e nada é gravado.

**Acceptance Scenarios**:

1. **Given** a habilitação ligada, **When** a comissão registra o desfecho com a opção marcada, **Then**
   um aviso é gravado para a pessoa, na mesma transação, nenhuma mensagem sai na requisição, e a
   resposta diz *"Aviso solicitado"*, e não *"enviado"*; sem marcar a opção, nenhum aviso é gravado.
   *(Revisto em 2026-11-11 pela 8ª decisão; antes, sem a última oração.)*
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
- **Pessoa sem endereço**, com a habilitação ligada: não há aviso, e a opção de avisar aparece
  desabilitada, com a razão. *(Revisto em 2026-11-11 pela 8ª decisão; antes: "a confirmação do
  desfecho diz que a pessoa não será avisada por falta de endereço.")*
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
- **FR-6404** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  As telas da gestão MUST continuar mostrando o fundamento como hoje; as duas camadas são
  do portal. A prévia do texto (FR-3993 da `125`, revista) MUST mostrar as duas camadas, como o
  portal as mostrará.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > A tela de quem registra o desfecho e a de quem convoca MUST continuar mostrando o
  > fundamento como hoje; as duas camadas são do portal.
  >
  > *Por que mudou:* a prévia da FR-3993 da `125` e a conferência da FR-5813 da `152` mostram o texto como o candidato o lerá; com as duas camadas no portal, elas precisam mostrar as duas (encontro com a `152`).


#### B. O portal em cada desfecho

- **FR-6405**: O rótulo de cada desfecho MUST continuar o da tabela da FR-1172 da `063`, e o título da
  página o da FR-3858 da `121` (*"Resultado da sua convocação"*), como a `154` o deixou.
- **FR-6406** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  A frase simples de cada desfecho MUST ser a desta tabela, com ‹data› a data local do
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

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > A frase simples de cada desfecho MUST ser a desta tabela, com ‹data› a data local do
  > registro e ‹fim do prazo› o vencimento da convocação vigente:
  >
  > | Desfecho | Frase simples |
  > |---|---|
  > | Aceite | *"A comissão registrou o resultado da sua convocação em ‹data›. Este registro ainda não é a matrícula, a bolsa nem o contrato."*, seguida do próximo passo (FR-6410 a FR-6413) |
  > | Regularização | *"A comissão registrou a regularização da sua situação nesta convocação em ‹data›. Este registro ainda não é a matrícula, a bolsa nem o contrato."*, seguida do próximo passo |
  > | Indeferimento | *"A comissão registrou o indeferimento desta convocação em ‹data›: ela concluiu que o que o Edital pede nesta etapa não foi cumprido. O motivo está no fundamento, abaixo."*, seguida do caminho para recorrer (FR-6414) |
  > | Desistência expressa | *"A comissão registrou a sua desistência desta convocação em ‹data›. Esta convocação está encerrada para você."* |
  > | Não atendimento | *"O prazo desta convocação terminou em ‹fim do prazo› sem que ela fosse atendida, e a comissão registrou isso em ‹data›. Esta convocação está encerrada para você."* |
  > | Cancelamento por inércia | *"A comissão registrou o cancelamento em ‹data›, porque ‹fato atestado, FR-6407›. Esta convocação está encerrada para você."* |
  > | Reclassificação | *"A comissão registrou a sua reclassificação em ‹data›. Esta convocação está encerrada para você; o que acontece depois é o que o Edital diz."* |
  >
  > *Por que mudou:* *"ainda não é a matrícula, a bolsa nem o contrato"* presumia que um dos três viria depois; a 4ª decisão manda não presumir matrícula, e a frase volta à forma da FR-3750 da `118`, que só nega.

- **FR-6407**: No cancelamento por inércia, o fato atestado MUST ser dito assim: *"não houve acesso ao
  ambiente do curso"*, *"não houve presença na primeira semana do curso"* e *"a entrega presencial não
  foi feita"*, uma por espécie de atestado da `019`.
- **FR-6408**: Nenhuma frase desta spec MUST afirmar perda definitiva de vaga, nova chamada, posição na
  lista ou consequência que nenhum ato declarou. *"Esta convocação está encerrada para você"* diz o
  efeito do desfecho registrado sobre a chamada, e não sobre o certame.
- **FR-6409**: A FR-1177 da `063` MUST ser revista para dizer que a frase simples de um desfecho
  **registrado** descreve o ato, e não é frase de consequência; a regra das duas frases neutras
  continua valendo antes do desfecho.
- **FR-6442** *(acrescida em 2026-11-11, pelas decisões do usuário)*: A frase simples da convocação sem desfecho MUST ser, por espécie: vaga
  inicial — *"Você foi chamado para uma das vagas da lista ‹nome da lista›, pela sua posição na
  classificação."*; vaga que vagou — *"Você foi chamado porque uma vaga da lista ‹nome da lista› ficou
  livre e você é a próxima pessoa na classificação."*; para regularizar — *"Você foi chamado para
  regularizar a sua situação na lista ‹nome da lista›, porque há vaga."*. A User Story 3 pedia estas
  frases, e nenhuma alínea as fixava. Nenhuma delas MUST dizer *"dentro das vagas"*, que a UX-158 da
  `063` proíbe no acompanhamento porque se lê como aprovação.

#### C. O próximo passo do aceite e da regularização

- **FR-6410** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Com aceite ou regularização, a página MUST dizer o próximo passo depois da frase
  simples, no lugar de *"Os próximos passos são os que o Edital indica."* (FR-3750 da `118`, revista).
  O próximo passo MUST vir só do texto publicado do Edital vigente e do contato, e MUST NOT ser
  inventado pelo sistema (4ª decisão).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Com aceite ou regularização, a página MUST dizer o próximo passo depois da frase
  > simples, no lugar de *"Os próximos passos são os que o Edital indica."* (FR-3750 da `118`, revista).
  >
  > *Por que mudou:* a 4ª decisão: orientar para o Edital publicado e o contato, sem inventar um próximo passo.

- **FR-6411** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  A **seção aplicável** MUST ser a seção do catálogo que trata da etapa depois do resultado
  da convocação — a de chave `matricula` (*"Da Matrícula"*, ou *"Como será a matrícula?"* no catálogo
  da `069`, com as partes *Acesso ao curso* e *Homologação da matrícula* que esse catálogo lhe junta)
  —, quando o texto publicado a tiver não vazia. O título MUST ser o que o Edital publicado lhe dá, e
  o próximo passo MUST ser *"O Edital explica o que vem depois em «‹título da seção›»."*, com o
  caminho para essa seção na página pública do Edital (D-004).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Quando o texto publicado do Edital vigente tiver a seção da matrícula não vazia (*"Da
  > Matrícula"*, ou *"Como será a matrícula?"* no catálogo da `069`), o próximo passo MUST ser *"O
  > Edital diz como será a próxima etapa em «‹título da seção›»."*, com o caminho para essa seção na
  > página pública do Edital. *(Adota a recomendação de P-4.)*
  >
  > *Por que mudou:* a 4ª decisão: a frase anterior dizia *"a próxima etapa"* sob o título da matrícula e adotava a recomendação de P-4; agora é a seção aplicável, com o título que o próprio Edital publica, e a frase não nomeia a etapa.

- **FR-6412** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Sem seção aplicável não vazia, o próximo passo MUST ser *"Consulte o Edital publicado
  para saber o que vem depois."*, com o caminho para a página pública do Edital, e nenhuma frase MUST
  presumir matrícula, bolsa ou contratação como próximo passo.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Sem essa seção, o próximo passo MUST ser *"A próxima etapa é a que o Edital publica."*,
  > sem caminho para seção.
  >
  > *Por que mudou:* a 4ª decisão: sem orientação identificável, indicar a consulta ao Edital e ao atendimento, sem inventar um próximo passo.

- **FR-6413** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  O próximo passo MUST terminar com *"Se tiver dúvida, fale com ‹contato›."* quando houver
  canal (FR-6415), e MUST NOT nomear setor, pessoa ou data que o Edital não publique. Nenhum texto do
  portal MUST dizer que a documentação da pessoa foi disponibilizada, encaminhada, entregue ou
  recebida por setor, nem apresentar a disponibilização da `117` como matrícula, contratação ou
  formalização concluída (9ª decisão).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > O próximo passo MUST terminar com *"Se tiver dúvida sobre a próxima etapa, fale com
  > ‹contato›."* quando houver canal (FR-6415), e MUST NOT nomear setor, pessoa ou data que o Edital não
  > publique, nem dizer que a documentação foi disponibilizada a alguém. *(Adota a recomendação de
  > P-9.)*
  >
  > *Por que mudou:* a 9ª decisão (sem aviso da disponibilização ao setor, e sem apresentá-la como formalização) substitui a recomendação de P-9 que esta alínea adotava; a frase do contato perde *"sobre a próxima etapa"*, pela 4ª.

- **FR-6414**: Com indeferimento, quando o texto publicado do Edital tiver a seção de recursos não
  vazia, a página MUST dizer *"O Edital diz se e como recorrer em «‹título da seção›»."*, com o
  caminho para ela; sem a seção, nada sobre recurso.

#### D. O contato

- **FR-6415** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  O contato MUST ser o canal de atendimento da unidade do Edital, com a recaída no canal
  da instalação da FR-3214 da `109`, mostrado como link (e-mail ou endereço) na convocação, no
  resultado e no aviso. Nenhum campo de contato da comissão MUST ser criado nesta entrega (5ª
  decisão).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > O contato MUST ser o canal de atendimento da unidade do Edital, com a recaída da FR-3214
  > da `109`, mostrado como link (e-mail ou endereço) na convocação, no resultado e no aviso.
  > *(Adota a recomendação de P-5.)*
  >
  > *Por que mudou:* a 5ª decisão confirma o canal da unidade com a alternativa da instalação, que esta alínea adotava como recomendação de P-5, e exclui o campo da comissão nesta entrega.

- **FR-6416** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Sem canal nenhum — nem o da unidade, nem o da instalação —, a linha *"Atendimento"* e
  a frase *"fale com o atendimento"* MUST NOT aparecer nas telas da convocação e do resultado, nem
  nas mensagens da convocação, da correção e do aviso do desfecho, e nenhuma delas MUST dizer *"o
  atendimento institucional"*. As outras telas do portal que usam a frase genérica não mudam.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Sem canal nenhum, a linha *"Atendimento"* e a frase *"fale com o atendimento"* MUST NOT
  > aparecer nas telas da convocação e do resultado, e nenhuma delas MUST dizer *"o atendimento
  > institucional"*. As outras telas do portal que usam a frase genérica não mudam.
  >
  > *Por que mudou:* a 5ª decisão: omitir a linha somente quando os dois canais faltarem, e a regra vale também nas mensagens que citam o atendimento.

- **FR-6417**: Os cenários de treinamento da `134` MUST declarar um canal fictício na unidade que
  usam, para que os estudos vejam o contato como em produção.

#### E. A desistência pelo portal: o pedido

- **FR-6418**: A página da convocação MUST oferecer *"Desistir desta convocação"* à pessoa cuja
  convocação vigente está visível no portal, sem desfecho e sem pedido pendente, com o Processo fora de
  estado final. A oferta MUST ser link secundário, no fim da página, e nunca a ação principal.
- **FR-6419** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  O link MUST levar a uma página de confirmação que diga, nesta ordem: que o pedido vai
  à comissão; que **pedir ainda não é desistir** — a desistência só vale quando a comissão a
  registrar; que, registrada, ela encerra a convocação e não se desfaz pelo portal; que o pedido não
  suspende nem prorroga o prazo, e que até o registro a pessoa pode continuar enviando o que as regras
  vigentes permitem; e que, até o registro, o pedido pode ser cancelado. A página MUST pedir a
  ciência, numa caixa a marcar, e MUST NOT ter campo de motivo nem texto livre.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > O link MUST levar a uma página de confirmação que diga, nesta ordem: que o pedido vai
  > à comissão, que registra a desistência; que, registrada, a desistência encerra a convocação e não
  > se desfaz pelo portal; que o pedido não suspende nem prorroga o prazo; e que, até o registro, o
  > pedido pode ser cancelado (P-6). A página MUST pedir a ciência, numa caixa a marcar, e MUST NOT ter
  > campo de motivo nem texto livre.
  >
  > *Por que mudou:* a 6ª decisão (deixar claro que solicitar a desistência ainda não é tê-la efetivada) e a 7ª (os envios continuam).

- **FR-6420**: O pedido MUST ser gravado com a convocação, a inscrição, a credencial que o fez, o
  instante e um protocolo, em registro que não se altera nem se exclui, e MUST ser recusado sem a
  ciência, com a convocação já desfechada, com pedido pendente, com o Processo em estado final ou com
  a convocação fora do portal. O comando MUST correr sob a trava da convocação e com chave de
  idempotência.
- **FR-6421** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Com pedido pendente, a página MUST dizer *"Pedido de desistência enviado em ‹data e
  hora›, protocolo ‹protocolo›. A desistência ainda não foi registrada: até a comissão registrá-la, a
  sua convocação continua, com o mesmo prazo, e você pode cancelar o pedido."*, MUST continuar
  mostrando o prazo como antes do pedido, e MUST continuar oferecendo os envios de documento e do
  Requerimento que as regras vigentes permitem. O pedido pendente MUST NOT mudar o que a pessoa pode
  enviar nem o que a comissão pode conferir, e o prazo não se suspende, não se prorroga e não se
  reinicia (7ª decisão).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Com pedido pendente, a página MUST dizer *"Pedido de desistência enviado em ‹data e
  > hora›, protocolo ‹protocolo›. A comissão vai registrá-lo."*, MUST continuar mostrando o prazo, e MUST
  > NOT oferecer envio de documento nem do Requerimento. *(Adota a recomendação de P-7.)*
  >
  > *Por que mudou:* a 7ª decisão: os envios previstos nas regras vigentes continuam permitidos enquanto o pedido estiver pendente, e o prazo não se suspende nem se prorroga. A redação anterior, que suspendia o envio, adotava a recomendação de P-7, que o usuário não aceitou.

- **FR-6422** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Com pedido pendente, a página MUST oferecer *"Cancelar o pedido de desistência"*, com
  confirmação. O cancelamento MUST ser gravado como registro próprio, que não altera nem exclui o
  pedido; o pedido cancelado MUST continuar no histórico da convocação, na gestão, com o
  cancelamento; e a página MUST voltar a oferecer *"Desistir desta convocação"*. O cancelamento MUST
  ser recusado depois do desfecho (6ª decisão).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Com pedido pendente, a página MUST oferecer *"Cancelar o pedido de desistência"*, com
  > confirmação; o cancelamento MUST ser gravado como registro próprio, e a convocação MUST voltar ao
  > estado de antes do pedido. *(Adota a recomendação de P-6.)*
  >
  > *Por que mudou:* a 6ª decisão: cancelar enquanto a comissão não tiver registrado o desfecho, com o pedido e o cancelamento preservados no histórico.

- **FR-6423**: O pedido e o cancelamento MUST entrar na trilha, sem endereço de e-mail.

#### F. A desistência pelo portal: a homologação

- **FR-6424** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Na condução da convocação, o cartão da pessoa com pedido pendente MUST mostrar *"Pedido
  de desistência pelo portal em ‹data e hora›"* e oferecer *"Registrar a desistência pedida"* a quem
  pode registrar desfecho. O atalho MUST ser gesto próprio, e não o seletor do desfecho (D-016): a
  espécie é a desistência expressa, e o fundamento derivado é *"Desistência expressa pedida pela
  pessoa convocada, pelo portal, em ‹data e hora›, protocolo ‹protocolo›."*, ao qual quem registra
  pode acrescentar complemento. A conferência do texto e a prévia da FR-3993 da `125` MUST valer.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Na condução da convocação, o cartão da pessoa com pedido pendente MUST mostrar *"Pedido
  > de desistência pelo portal em ‹data e hora›"* e oferecer *"Registrar a desistência pedida"* a quem
  > pode registrar desfecho, que abre o registro do desfecho com a desistência expressa escolhida e o
  > fundamento *"Desistência expressa pedida pela pessoa convocada, pelo portal, em ‹data e hora›,
  > protocolo ‹protocolo›."*, ao qual quem registra pode acrescentar complemento.
  >
  > *Por que mudou:* encontro com a `152`: a FR-5839 dela proíbe espécie pré-escolhida no seletor, e o atalho precisa ser dito como gesto próprio.

- **FR-6425** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Registrar o desfecho de uma convocação com pedido pendente MUST encerrar o pedido como
  **homologado**, se o desfecho for a desistência expressa, ou como **encerrado por outro desfecho**,
  nos demais casos. Na confirmação de qualquer outro desfecho individual, a tela MUST dizer que há
  pedido de desistência pendente, com data e protocolo, e MUST pedir ciência numa marca desmarcada,
  que o comando confere; essa ciência se soma às da `152` (FR-5803 da `152`), sem substituí-las.
  Nenhum pedido MUST virar desfecho sem esse registro.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > Registrar o desfecho de uma convocação com pedido pendente MUST encerrar o pedido:
  > como **homologado**, se o desfecho for a desistência expressa; como **encerrado por outro desfecho**,
  > nos demais casos, e então a confirmação do desfecho MUST avisar que há pedido pendente e pedir
  > ciência. Nenhum pedido MUST virar desfecho sem esse registro.
  >
  > *Por que mudou:* encontro com a `152`: o indeferimento com o prazo em curso já pede uma ciência, e as duas precisam conviver.

- **FR-6426**: O registro do não atendimento dos vencidos em lote MUST deixar de fora a pessoa com
  pedido pendente, contada à parte como *"pedido de desistência pendente"*.
- **FR-6427** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  O *"O que fazer agora"* da condução MUST derivar a providência *"Registrar a desistência
  pedida pelo portal"* enquanto houver pedido pendente no recorte, do mesmo cálculo do cartão, como
  providência *Pendente* de quem pode registrar desfecho, na ordem da FR-4082 da `127`, uma só por
  recorte, com a contagem.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > O *"O que fazer agora"* da condução MUST derivar a providência *"Registrar a desistência
  > pedida pelo portal"* enquanto houver pedido pendente no recorte, do mesmo cálculo do cartão.
  >
  > *Por que mudou:* encontro com a `153`, que acrescentou providências ao mesmo nível 1: a desta spec precisa da posição na ordem fixa da `127`.

- **FR-6443** *(acrescida em 2026-11-11, pelas decisões do usuário)*: Com pedido pendente, o cartão MUST mostrar o pedido e o atalho antes de
  qualquer outra indicação de desfecho, inclusive a do não atendimento da FR-5809 da `152`.
- **FR-6444** *(acrescida em 2026-11-11, pelas decisões do usuário)*: A confirmação de encerrar o Edital e a de encerrar o Processo MUST advertir
  dos pedidos de desistência pendentes, com a contagem e o caminho para a condução, ao lado da
  advertência da FR-6124 e da FR-6128 da `153`. A advertência MUST NOT impedir o encerramento
  (D-017).

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
- **FR-6430** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  Com a habilitação ligada, a confirmação de todo registro de desfecho — individual,
  pelo atalho da desistência pedida e no registro do não atendimento dos vencidos em lote — MUST
  oferecer *"Avisar a pessoa por e-mail"* (no lote, *"Avisar as pessoas por e-mail"*), **desmarcada**
  por padrão (8ª decisão). Nada MUST gravar aviso de desfecho sem que quem confirma a marque.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > O aviso MUST ser oferecido na confirmação de todo registro de desfecho — individual,
  > pelo atalho da desistência pedida e no registro do não atendimento dos vencidos em lote —, como a
  > opção *"Avisar a pessoa por e-mail"* (no lote, *"Avisar as pessoas por e-mail"*), marcada por padrão
  > e desmarcável. *(Adota a recomendação de P-8.)* Nada MUST gravar aviso de desfecho sem esse gesto.
  >
  > *Por que mudou:* a 8ª decisão: desmarcada por padrão, com solicitação explícita. A redação anterior a marcava, pela recomendação de P-8, que o usuário não aceitou.

- **FR-6431**: Marcada a opção, o aviso MUST ser gravado na mesma transação do desfecho, no registro de
  avisos da `066`, e enviado só pelo despacho dela, fora da requisição.
- **FR-6432**: Antes de cada tentativa, o despacho MUST reler o desfecho e interromper o aviso, com o
  motivo, quando ele deixou de ser o desfecho da convocação vigente, como a FR-4623 da `134` faz com a
  pendência. A janela de despacho da `066` MUST valer.
- **FR-6433** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  O assunto MUST ser *"‹instituição› · Edital ‹número›/‹ano›: há resultado registrado na
  sua convocação"*, e MUST NOT começar por "Convocação".

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > O assunto MUST ser *"‹instituição› · Edital ‹número›/‹ano›: há atualização na sua
  > convocação"*, e MUST NOT começar por "Convocação".
  >
  > *Por que mudou:* a 1ª decisão: o texto neutro informa que há resultado registrado, e o assunto diz o mesmo, sem dizer qual.

- **FR-6434** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  O corpo MUST dizer *"Há resultado registrado da sua convocação no Edital ‹número›/‹ano›.
  Para ver o resultado e o que fazer depois, entre na sua área do candidato."*, com o link da
  convocação (o mesmo da mensagem da convocação), a instrução de acesso por código, o contato
  (FR-6415), quando houver, e o rodapé fixo *"Este aviso não é o registro oficial e não altera prazo
  nem resultado. O que vale é o que está na sua área do candidato e o que o Edital publica."* O texto
  MUST ser o mesmo para todas as espécies (1ª decisão).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > O corpo MUST dizer *"O resultado da sua convocação no Edital ‹número›/‹ano› foi
  > registrado pela comissão em ‹data›. Veja o resultado e o que fazer depois na sua área do
  > candidato."*, com o link da convocação (o mesmo da mensagem da convocação), a instrução de acesso
  > por código, o contato (FR-6415) e o rodapé fixo *"Este aviso não é o registro oficial e não altera
  > prazo nem resultado. O que vale é o que está na sua área do candidato e o que o Edital publica."*
  > O texto MUST ser o mesmo para todas as espécies. *(Adota a recomendação de P-1.)*
  >
  > *Por que mudou:* a 1ª decisão: informar que há resultado registrado e indicar o acesso ao portal; resultado e fundamento ficam no ambiente autenticado. A redação anterior dava a data do registro, que não é necessária para isso.

- **FR-6435**: O corpo e o assunto MUST NOT conter a espécie do desfecho, o rótulo, o fundamento, o
  nome, o CPF, o protocolo, a modalidade nem a posição, e a mensagem MUST NOT ter anexo.
- **FR-6436** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  A pessoa sem endereço MUST ficar sem aviso, e a confirmação do desfecho MUST mostrar a
  opção de avisar desabilitada, com a razão.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > A pessoa sem endereço MUST ficar sem aviso, e a confirmação do desfecho MUST dizê-lo.
  >
  > *Por que mudou:* a 8ª decisão: com a solicitação explícita, quem confirma precisa saber, antes de marcar, que a pessoa não pode ser avisada.

- **FR-6445** *(acrescida em 2026-11-11, pelas decisões do usuário)*: A resposta da confirmação do desfecho MUST dizer *"Aviso solicitado"*, e
  nunca *"enviado"*. O cartão da convocação MUST mostrar o estado do aviso pelo registro da `066`:
  *"Aviso solicitado em ‹data›"* até a tentativa; *"Aviso enviado em ‹data e hora›"* depois de o
  servidor de correio aceitar a mensagem — nunca *"recebido"* (FR-288a da `019`) —; e, falhando,
  expirando ou interrompido, o estado e o motivo (8ª decisão).

#### I. A habilitação

- **FR-6437**: O aviso do desfecho MUST depender de uma chave própria, `AVISOS_DE_DESFECHO`, e só valer
  com ela **e** `AVISOS_AOS_CANDIDATOS` ligadas. *(Adota a recomendação de P-2.)* As duas MUST vir
  desligadas em produção, ligadas em `development` e `test`.
- **FR-6438**: Com a habilitação desligada, a opção da FR-6430 MUST NOT aparecer, o POST que a trouxer
  MUST ser recusado com `aviso_envio_desabilitado` sem registrar o desfecho, e o despacho MUST NOT
  enviar aviso de desfecho.
- **FR-6439**: A habilitação MUST NOT condicionar nenhum outro requisito desta spec: as seções A a G
  MUST funcionar igualmente com ela ligada ou desligada.
- **FR-6440** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  A chave MUST ser ligada em produção só depois de resolvidas, para esta finalidade, as
  pendências institucionais PI-1 a PI-6. A ligação é ato de configuração; o documento de implantação
  MUST registrar a validação obtida, quem a emitiu e a data dela, e a data em que a chave foi ligada.
  Nenhum texto do sistema MUST afirmar quem valida nem se a validação foi pedida (3ª decisão).

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > A chave MUST ser ligada em produção só depois do parecer do Encarregado sobre o
  > tratamento da seção *A dependência de LGPD, nomeada* e da validação do correio. A ligação é ato de
  > configuração; o registro do parecer, e da data em que a chave foi ligada, MUST ficar no documento de
  > implantação.
  >
  > *Por que mudou:* a 3ª decisão: o responsável, o alcance e a existência do pedido não estão confirmados, e ficam como pendências institucionais. A redação anterior nomeava o responsável como fato.


#### J. As revisões

- **FR-6441** *(revista em 2026-11-11 e em 2026-11-13, pelas decisões do usuário — as redações anteriores estão ao fim desta alínea)*:
  As revisões que esta spec impõe MUST estar escritas nas specs de origem, com a redação
  anterior preservada, e vigorar com a implementação desta: a FR-084 da `010`; a FR-1172 e a FR-1177
  da `063`; a FR-3740 e a FR-3750 da `118`; a FR-3883 da `121`; a FR-3993 da `125`; e a FR-878 da `050`.

  > **Redação de 11/11/2026, preservada:** a mesma, sem a FR-3740 da `118`.
  >
  > *Por que mudou:* a FR-3740 da `118` exigia o bloco *"Sobre esta convocação"* sem `details`, com o
  > fundamento — o oposto da FR-6400 para o fundamento da convocação. O conflito apareceu na
  > implementação (PR #525), e o usuário decidiu rever a FR-3740 em 13/11/2026.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > As revisões que esta spec impõe — a FR-084 da `010`, a FR-1172 e a FR-1177 da `063`, a
  > FR-3750 da `118` e o texto da mensagem da `121`; e a FR-6206 da `154`, que passa a citar a FR-3750
  > revista — MUST ser escritas nas specs de origem, com a
  > redação anterior preservada, no PR da implementação desta spec (D-001).
  >
  > *Por que mudou:* o usuário pediu as revisões na documentação antes do plano (D-001, revista).


### Requisitos de experiência

- **UX-620**: A frase simples MUST ter no máximo duas frases antes do próximo passo, e MUST vir antes
  de qualquer data técnica, protocolo ou fundamento.
- **UX-621**: O fundamento recolhido MUST abrir pelo teclado, anunciar o estado (aberto ou fechado) e
  não ter rolagem horizontal a 375 px.
- **UX-622** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  *"Desistir desta convocação"* MUST ter aparência de link secundário, sem a cor de ação
  principal nem a de perigo, e a confirmação MUST ter o botão *"Enviar o pedido de desistência"* e o
  caminho de volta *"Voltar à convocação"*, este primeiro na ordem do teclado. *"Cancelar o pedido de
  desistência"* MUST ter o mesmo peso visual de *"Desistir desta convocação"*.

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > *"Desistir desta convocação"* MUST ter aparência de link secundário, sem a cor de ação
  > principal nem a de perigo, e a confirmação MUST ter o botão *"Enviar o pedido de desistência"* e o
  > caminho de volta *"Voltar à convocação"*, este primeiro na ordem do teclado.
  >
  > *Por que mudou:* a 6ª decisão trouxe o cancelamento, que precisa do mesmo peso do pedido.

- **UX-623** *(revista em 2026-11-11, pelas decisões do usuário — a redação anterior está ao fim desta alínea)*:
  A opção *"Avisar a pessoa por e-mail"* MUST dizer, ao lado, *"O e-mail diz só que há
  resultado registrado, sem dizer qual. Ele sai depois, pelo envio automático."*

  > **Redação anterior, de 11/11/2026 (PR #485), preservada:**
  > A opção *"Avisar a pessoa por e-mail"* MUST dizer, ao lado, *"O e-mail diz só que há
  > resultado registrado, sem dizer qual."*
  >
  > *Por que mudou:* a 8ª decisão: a confirmação distingue aviso solicitado de aviso enviado, e a ajuda da opção já o diz.


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
- **SC-2129** *(acrescido em 2026-11-11)*: Num Edital sem a seção aplicável preenchida, nenhuma tela do
  aceite fala de matrícula, bolsa ou contratação como próximo passo.
- **SC-2130** *(acrescido em 2026-11-11)*: Com pedido pendente, o vencimento e o que a pessoa pode
  enviar são, em 100% dos casos, os mesmos de antes do pedido.
- **SC-2131** *(acrescido em 2026-11-11)*: Com a habilitação ligada, só os desfechos registrados com a
  opção marcada produzem aviso, e nenhuma tela diz *"enviado"* antes de o despacho registrar a
  aceitação pelo servidor de correio.

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

*Respondidas pelo usuário em 11/11/2026; as respostas estão em Clarifications e, abaixo de cada
pergunta, a indicação de onde a redação mudou.* O texto das perguntas fica como foi mergeado.

Nove decisões que a spec não toma. Cada uma tem a recomendação, e o texto acima a adota
provisoriamente, marcada.

**P-1 — O que o e-mail do desfecho diz.** *Recomendado:* **neutro** — *"o resultado da sua convocação
foi registrado; veja na sua área do candidato"*, igual para todas as espécies. Alternativa: dizer o
resultado (*"Vaga aceita"*, *"Convocação não atendida"*) e, no aceite, o próximo passo. A neutra
segue a decisão 5 da `066` (sem resultado individual no corpo), não revela por inferência dado
sensível no indeferimento de cota, e facilita o parecer; o custo é a pessoa precisar entrar no portal
para saber qual foi.

> **Resposta (1ª decisão):** texto neutro, que informa que há resultado registrado e indica o acesso ao portal; resultado e fundamento ficam no ambiente autenticado. Coincide com a recomendação; revistos o assunto e o corpo (FR-6433, FR-6434), que agora dizem *"há resultado registrado"*.

**P-2 — A habilitação.** *Recomendado:* **chave própria**, `AVISOS_DE_DESFECHO`, que só vale com a
`AVISOS_AOS_CANDIDATOS` também ligada. Alternativa: a mesma chave da `066`, como a `134` decidiu. A
própria deixa o parecer aprovar uma finalidade sem aprovar a outra; o custo é uma chave a mais na
implantação.

> **Resposta (2ª decisão):** chave própria, dependente também da chave geral dos avisos; o envio permanece desligado até a validação institucional correspondente. Coincide com a recomendação; nenhuma alínea mudou por ela.

**P-3 — O parecer.** Você confirma que a validação é do **Encarregado pelo Tratamento de Dados
Pessoais do Ifes**, e que **um pedido só** pode cobrir as três finalidades pendentes — o aviso
complementar da `066`, o de pendência da `134` e o do desfecho desta —, com a descrição do
tratamento desta spec? Quem leva o pedido, e se ele já foi feito, é informação que o repositório não
tem.

> **Resposta (3ª decisão):** responsável, abrangência e existência do pedido de validação continuam como pendências institucionais (PI-1 a PI-3), sem confirmação por inferência. O envio permanece desligado; as partes independentes avançam. Revistas a seção da validação e a FR-6440.

**P-4 — O próximo passo do aceite.** *Recomendado:* o **caminho para a seção da matrícula** do Edital
publicado, sem campo novo. Alternativa: um campo estruturado e curto no Edital — *"Depois do resultado
da convocação"*: quem conduz a etapa seguinte e como procura a pessoa —, mostrado no portal e,
conforme P-1, no aviso. O campo responde melhor ao *"quem vai procurá-lo"* do achado 07, mas é norma
nova no Edital, com a regra de Retificação que isso traz.

> **Resposta (4ª decisão):** a seção aplicável do Edital publicado e o contato, sem presumir matrícula e sem inventar próximo passo. Revistas a FR-6406, a FR-6410, a FR-6411, a FR-6412 e a FR-6413.

**P-5 — O contato.** *Recomendado:* o **canal da unidade**, com a recaída da instalação, e a linha
omitida quando não houver nenhum. Alternativa: um canal da comissão por Edital ou por Processo, que
recai no da unidade. O recomendado não muda dado; a alternativa serve à unidade que conduz certames
com comissões de contatos diferentes.

> **Resposta (5ª decisão):** o canal da unidade, com alternativa no da instalação; sem campo da comissão; a linha é omitida somente quando os dois faltarem. Revistas a FR-6415 e a FR-6416.

**P-6 — Cancelar o pedido.** *Recomendado:* **sim**, até a comissão registrar o desfecho. O endereço
de e-mail pode ser compartilhado, e o pedido é uma manifestação que a pessoa pode reconsiderar enquanto
nada foi decidido. Alternativa: pedido irrevogável pelo portal, e a reconsideração pelo canal da
comissão.

> **Resposta (6ª decisão):** sim, enquanto a comissão não tiver registrado o desfecho, com pedido e cancelamento no histórico, e a tela diz que pedir ainda não é desistir. Revistas a FR-6419, a FR-6421 e a FR-6422.

**P-7 — Enviar documento com o pedido pendente.** *Recomendado:* **não**: o envio fica suspenso até o
cancelamento, porque enviar e desistir ao mesmo tempo deixa a comissão sem saber o que vale. O prazo
corre do mesmo jeito. Alternativa: o envio continua oferecido, com aviso.

> **Resposta (7ª decisão):** os envios previstos nas regras vigentes continuam permitidos; o prazo não é suspenso nem prorrogado. **Contrária à recomendação.** Revista a FR-6421.

**P-8 — A opção de avisar no registro do desfecho.** *Recomendado:* **marcada por padrão**,
desmarcável. Alternativa: desmarcada por padrão. A marcada faz o aviso ser a regra quando a
habilitação estiver ligada; ela continua sendo um gesto humano, porque é parte da confirmação.

> **Resposta (8ª decisão):** desmarcada por padrão, com solicitação explícita; a confirmação distingue aviso solicitado de aviso enviado. **Contrária à recomendação.** Revistas a FR-6430 e a FR-6436, e acrescida a FR-6445.

**P-9 — Dizer ao candidato que a documentação foi disponibilizada ao setor (`117`).** *Recomendado:*
**não**. O GPS sabe que disponibilizou, e não sabe se o setor agiu; a frase criaria a expectativa de
contato que o sistema não acompanha. Alternativa: *"A comissão disponibilizou a sua documentação ao
setor responsável pela próxima etapa em ‹data›."*, depois do aceite.

> **Resposta (9ª decisão):** sem aviso específico nesta entrega, e a operação interna não se apresenta como matrícula, contratação ou formalização concluída. Revista a FR-6413.

---

## Decisões desta spec

Propostas de desenho, sujeitas à revisão do PR.

#### D-001 — As revisões de outras specs se escrevem na implementação *(revista em 2026-11-11 — a redação anterior está ao fim)*

A instrução do usuário de 11/11/2026 pediu as revisões na documentação antes do plano. Elas estão
escritas nas specs de origem, com a marca de vigência na implementação desta: o plano e as tarefas
leem a regra que vão implementar, e a redação anterior continua descrevendo o sistema até lá.

> **Redação anterior, de 11/11/2026 (PR #485), preservada:**
> A `154` acabou de rever a `063`, a `118`, a `121` e a `134`, e as sessões da `152`, da `153` e da `155`
> seguem abertas sobre a mesma jornada. Revisar alíneas normativas neste PR, com nove perguntas ainda
> abertas, produziria texto que a resposta pode mudar e conflito resolvido à mão. Esta spec nomeia o que
> revê (FR-6441) e deixa a escrita para o PR da implementação, já com as respostas.
>
> *Por que mudou:* a instrução do usuário que acompanhou as decisões.

#### D-002 — Duas camadas, derivadas na leitura

A frase simples não se grava: é derivada da espécie e dos dados do ato quando a tela é lida. Gravar
exigiria mudar ato append-only ou criar uma segunda versão do mesmo fato; derivar permite corrigir a
frase sem tocar no ato, e o fundamento, que é o ato, continua palavra por palavra.

#### D-003 — "Encerrada para você", e não "perdeu a vaga"

O indeferimento pode ser regularizado (a convocação para regularizar da `019`), e a reclassificação
devolve a pessoa à fila. *"Perdeu a vaga"* seria falso em dois de cinco desfechos de exclusão. A frase
diz o efeito sobre a chamada, que é o que o desfecho registra.

#### D-004 — O próximo passo vem do Edital, nunca do sistema *(revista em 2026-11-11 — a redação anterior está ao fim)*

O GPS não conduz a formalização (`117`): para em *disponibilizado*. O catálogo das seções é
declarado (`054`, `069`), e a seção que trata da etapa depois do resultado tem chave fixa. O sistema
não lê o texto para adivinhar o próximo passo: ele só aponta a seção que existe, com o título que o
Edital lhe deu. Um Edital de bolsista que não a preencha cai na consulta ao Edital, e nada presume
matrícula (4ª decisão).

> **Redação anterior, de 11/11/2026 (PR #485), preservada:**
> O GPS não conduz a formalização (`117`): para em *disponibilizado*. O que vem depois do aceite é o que
> o Edital publica, e a tela aponta para lá. Sem a seção, ela diz que é o que o Edital publica, e dá o
> contato.
>
> *Por que mudou:* a 4ª decisão: não presumir matrícula, e indicar a consulta ao Edital quando não houver orientação identificável.

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

#### D-015 — O pedido não muda a convocação *(acrescida em 2026-11-11)*

Pedir não é desistir (6ª decisão), e a pessoa pode cancelar e cumprir (7ª decisão). Por isso o prazo,
os envios, a conferência e o aviso de pendência da `134` continuam como estavam: tirá-la do aviso de
pendência a deixaria sem saber de uma correção justamente quando ainda pode voltar atrás.

#### D-016 — O atalho da desistência pedida é gesto próprio *(acrescida em 2026-11-11)*

A FR-5839 da `152` proíbe espécie pré-escolhida no seletor, para que ninguém registre por inércia a
única espécie oferecida. O atalho não é o seletor: nasce de um pedido registrado, nomeia a espécie no
botão e passa pela conferência do texto, como o atalho de indeferimento da `152`.

#### D-017 — Encerrar com pedido pendente adverte, e não impede *(acrescida em 2026-11-11)*

O encerramento fecha a escrita, e o pedido pendente ficaria sem homologação. Impedir encerrar por
pedido de candidato daria a ele um veto sobre o calendário do certame; a advertência, ao lado da da
`153`, dá à comissão a chance de registrar antes.
