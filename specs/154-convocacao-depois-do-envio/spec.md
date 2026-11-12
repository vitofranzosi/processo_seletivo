# Feature Specification: A convocação depois do envio, e um nome só para o documento reenviado

**Feature Branch**: `claude/sharp-gould-0f18b2`, sobre a `main` em `4ff4098e`

**Created**: 2026-11-11

**Status**: **Revisão de requisitos vigentes; plano e tarefas no PR #484, sem código.** **Todas as
decisões são do usuário, e nenhuma está pendente:**

- **Sobre os achados 20 e 23 do estudo da jornada final, em 11/11/2026:** transcritas na seção
  *Clarifications* e citadas como *1ª a 8ª decisão*.
- **Sobre as propostas de desenho desta spec, no mesmo dia:** D-001 a D-005 aprovadas — a D-002 e a
  D-004 com ajuste de redação do usuário —, e a pergunta sobre a chamada que não pede documento pelo
  portal respondida, registrada como D-006.
- **Sobre a contradição que o `/speckit-analyze` achou, no mesmo dia:** a tela da convocação sem
  documento pedido fica como hoje, sem a advertência, registrada como D-007.

Nenhuma delas se reabre.

**Input**: o [estudo da jornada final](../../doc/estudo-jornada-final-2026-11-11/index.html) de
11/11/2026 (PR #472), achados **20** e **23**, os dois de prioridade baixa:

- **achado 20** (etapa B, portal; evidência `B08-tudo-enviado`): com tudo enviado, o topo da
  convocação continua *"Você foi convocado!"* e *"Se você não atender no prazo, a comissão poderá
  registrar o não atendimento desta convocação."* Impacto: ansiedade desnecessária em quem já
  cumpriu. Causa: interface.
- **achado 23** (etapa D, reenvio; evidências `D05-gestao-ve-versao-2` e `D04-correcao-enviada`): o
  mesmo fato tem três nomes — *"Complementado, aguardando conferência"* e *"Reenviado(s), a conferir
  de novo"* na gestão, *"Novo arquivo recebido… depois da correção pedida"* no portal. Impacto:
  dificulta falar do mesmo item entre comissão e candidato. Causa: texto.

Os dois não cabiam como polimento: o título está fixado na tabela da FR-3858 da `121`; a frase de
consequência é exigida pela FR-1177 da `063` (e pela FR-3864 da `121`) exatamente nessa condição; a
FR-3728 da `118` proíbe dizer que a pessoa "enviou tudo"; e os três nomes do reenviado vêm das
tabelas da `115`, da `118` e da `143`. Por isso esta é uma revisão, com a redação anterior
preservada em cada requisito alterado.

> **Faixa de identificadores.** Esta spec abre em **FR-6200** e **SC-2000**, com folga sobre o teto
> medido em 11/11/2026 na `main` em `4ff4098e` e nos PRs abertos (#475 e #477): o requisito seis mil
> cento e trinta e o critério mil novecentos e cinquenta e seis, os dois da `153`. Ficam reservados
> até o requisito seis mil duzentos e quarenta e nove e o critério dois mil e dezenove. **Nenhum
> `UX-` é aberto aqui.** O número `154` é o primeiro livre depois da
> `153`; a `151` continua livre de propósito. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3728 da `118`"). Uma decisão de outra feature é citada pelo assunto e pela
> feature, nunca pelo número. Os achados do estudo são citados como "achado 20", sem o prefixo do
> estudo, porque o identificador com hífen seria lido como requisito de experiência desta base.

### O que esta spec cobre, e o que fica fora

**Cobre:** o título, a frase de conclusão, o prazo e a frase de consequência da tela da convocação e
do acompanhamento do portal quando a pessoa não tem providência pendente; e o nome do estado do
documento reenviado depois de pendência, na gestão e no portal.

**Fica fora:** a mensagem de convocação e a da correção (elas saem quando tudo ainda está por
fazer); a ressalva da FR-3864 da `121`, que continua igual em todo estado aberto; os achados 02, 03,
14, 19, 22, 24 e 25 do mesmo estudo, que o PR #477 trata em código; e qualquer estado gravado,
coluna, migration, rota ou tela nova.

## Clarifications

### Session 2026-11-11 (decisões do usuário sobre os achados 20 e 23)

- Q: Que título a convocação tem quando a pessoa não tem providência pendente? → A: **"Acompanhe sua
  convocação"** (1ª decisão).
- Q: E a frase de conclusão, com documentos aguardando conferência? → A: Mantém-se: *"Você não tem
  mais documentos para enviar agora. A comissão ainda vai concluir a análise."* (2ª decisão).
- Q: O prazo some quando não há nada a fazer? → A: Não. O prazo continua visível (3ª decisão).
- Q: A advertência do não atendimento? → A: *"Se você não atender no prazo, a comissão poderá
  registrar o não atendimento desta convocação."* aparece **só** quando houver providência pendente
  do candidato (4ª decisão).
- Q: Como a tela trata o que já chegou? → A: Diferencia **documento recebido**, **documento
  conferido** e **convocação concluída**; o recebimento dos arquivos não deve sugerir aprovação (5ª
  decisão).
- Q: E se a análise já terminou? → A: A orientação reflete o próximo passo real (6ª decisão).
- Q: Que nome tem o documento reenviado depois da correção pedida? → A: **"Reenviado — aguardando
  nova conferência"**, igual na gestão e no portal. Explicações adicionais podem contextualizar a
  correção pedida, mas o nome do estado é esse (7ª decisão).
- Q: O que já foi publicado ou gravado muda? → A: Não. Documentos já publicados e atos gravados não
  mudam (8ª decisão; Princípio da imutabilidade da Constituição).

### Session 2026-11-11 (decisões do usuário sobre as propostas da spec)

- Q: O que é providência pendente? → A: Deriva das tarefas obrigatórias do candidato; opcionais e
  itens com a comissão ficam fora (D-001, aprovada).
- Q: Que frase diz que a conferência acabou? → A: *"A conferência dos documentos obrigatórios
  terminou. Aguarde o registro do resultado desta convocação."*, **somente** quando todos os
  obrigatórios estiverem conferidos e não houver tarefa nem desfecho. A frase não afirma que os
  opcionais também foram conferidos (D-002, com a redação do usuário).
- Q: O cartão do reenviado no portal? → A: Aprovada a redação proposta (D-003).
- Q: A contagem do reenviado? → A: Aprovada, com singular e plural naturais — *"1 reenviado —
  aguardando nova conferência"*, *"2 reenviados — aguardando nova conferência"* —, sem "(s)" na tela
  (D-004).
- Q: E sem conferência possível? → A: Aprovadas as variantes no passado com o Processo encerrado ou
  com desfecho. O vencimento do prazo, sozinho, mantém *"aguardando"*, porque a conferência ainda
  pode ocorrer (D-005).
- Q: E a chamada que não pede documento pelo portal? → A: Se o portal pede **só o Requerimento**,
  ele é providência pendente até ser enviado; depois, *"Acompanhe sua convocação"*, sem a
  advertência do não atendimento, e sem a frase da conferência terminada. Se **nada** é pedido pelo
  portal, mantém-se a orientação de seguir as instruções do Edital e o comportamento atual até o
  desfecho, porque o sistema não consegue verificar o cumprimento externo (D-006).

### Session 2026-11-11 (decisão do usuário depois da análise)

- Q: A cena 5 da US2 e a SC-2001 dizem que a tela de hoje da chamada sem documento traz a
  advertência; a página da convocação sem documento nunca a mostrou — só o acompanhamento. Qual
  vale? → A: **A página fica como hoje**: sem a advertência na página da convocação sem documento; a
  advertência dessa chamada continua só no acompanhamento (D-007).

## User Scenarios & Testing *(mandatory)*

Os cenários são os do estudo, no Edital de treinamento SIM09/2026 (C09), e os da `118` e da `121`
(C1, F, G, I1, K, corr), com dois novos: **T** (tudo enviado, nada conferido) e **Tc** (tudo
conferido, sem desfecho).

### User Story 1 — Quem já enviou tudo lê que agora é acompanhar (Priority: P1)

A pessoa enviou todos os documentos obrigatórios e o Requerimento. Ao voltar à convocação, ela lê
*"Acompanhe sua convocação"*, o prazo (que continua lá), a frase de conclusão, o andamento e a
ressalva — e não lê mais que a comissão poderá registrar o não atendimento, porque não há nada que
ela deixou de fazer.

**Why this priority**: é o achado 20. A advertência dirigida a quem já cumpriu é ruído que assusta,
e o título de chamada ("Você foi convocado!") repete um convite que ela já atendeu.

**Independent Test**: no C09, reproduzir a captura `B08-tudo-enviado` e conferir o título, o prazo,
a ausência da advertência e a presença da frase de conclusão, na convocação e no acompanhamento.

**Acceptance Scenarios**:

1. **Given** T (documentos obrigatórios e Requerimento enviados, nada conferido, prazo correndo),
   **When** a pessoa abre a convocação, **Then** o título é *"Acompanhe sua convocação"*, o cartão
   do prazo mostra a data, o dia da semana e a contagem, o resumo é a frase de conclusão, não há
   ação principal, e a advertência do não atendimento não aparece.
2. **Given** T, **When** a pessoa abre o acompanhamento, **Then** a ação é *"Nada por enquanto."*,
   seguida da frase de conclusão; o prazo aparece; a advertência não.
3. **Given** C1 (nada enviado, prazo correndo), **When** a pessoa abre a convocação, **Then** o
   título continua *"Você foi convocado!"* e a advertência aparece uma vez, como hoje.
4. **Given** T, **When** a comissão registra pendência num obrigatório, **Then** a pessoa volta a
   ler *"Você foi convocado!"*, o resumo *"Você ainda precisa corrigir 1 documento."* e a
   advertência.
5. **Given** T com um documento opcional não enviado, **When** a pessoa abre a convocação, **Then**
   o título é *"Acompanhe sua convocação"*, e a linha do opcional segue a frase de conclusão: o
   opcional não é providência pendente.

---

### User Story 2 — Recebido, conferido e concluído não se confundem (Priority: P1)

Os arquivos recebidos ficam *"com a comissão"*; os conferidos dizem *"Conferido: de acordo com o
Edital"*; a convocação só se diz concluída com o resultado registrado. Quando a comissão já
conferiu todos os obrigatórios e falta só registrar o resultado, a página diz esse próximo passo, e
não que a análise ainda vai ser concluída — sem afirmar nada sobre os opcionais.

**Why this priority**: a troca de título, sozinha, poderia ler como "deu certo". A 5ª decisão
proíbe que o recebimento sugira aprovação, e a 6ª pede que a orientação seja verdadeira em cada
momento.

**Independent Test**: no C09, percorrer T → Tc → I1 e conferir, em cada um, título, resumo e o texto
de cada cartão.

**Acceptance Scenarios**:

1. **Given** T, **When** a pessoa lê a página, **Then** nenhum texto diz *aprovado*, *aceito*,
   *deferido*, *concluído*, *tudo certo* ou *enviou tudo*, e nenhum cartão recebido usa a marca
   visual do conferido.
2. **Given** Tc (todos os obrigatórios conferidos — conformes ou *não se aplica* —, nenhuma tarefa,
   sem desfecho), **When** a pessoa abre a convocação ou o acompanhamento, **Then** o título é
   *"Acompanhe sua convocação"* e, no lugar da frase de conclusão, vem *"A conferência dos
   documentos obrigatórios terminou. Aguarde o registro do resultado desta convocação."* (D-002).
3. **Given** uma chamada com um obrigatório conferido e outro aguardando conferência, **When** a
   pessoa abre a convocação, **Then** vale a frase de conclusão (2ª decisão), e não a da conferência
   terminada.
4. **Given** a chamada que pede só o Requerimento, já enviado, **When** a pessoa abre a convocação,
   **Then** o título é *"Acompanhe sua convocação"*, o prazo aparece, a advertência não, e a frase
   da conferência terminada também não (D-006).
5. **Given** a chamada que não pede nada pelo portal, sem desfecho, **When** a pessoa abre a
   convocação, **Then** a tela é a de hoje: *"Você foi convocado!"* e *"Siga as instruções do Edital
   para esta convocação."*, sem a advertência, que nessa chamada só aparece no acompanhamento (D-006,
   D-007).
6. **Given** I1 (vaga aceita), **When** a pessoa abre a convocação, **Then** o título é *"Resultado
   da sua convocação"*, com o rótulo do desfecho e a frase do aceite, como hoje — é a convocação
   concluída.

---

### User Story 3 — O documento reenviado tem um nome só (Priority: P2)

A comissão registra pendência num documento; o candidato envia um arquivo novo. Na página de
documentos da convocação, na condução, no passo da chamada, na contagem e na exclusão do aviso de
pendência, a comissão lê *"Reenviado — aguardando nova conferência"*; no cartão do portal, o
candidato lê o mesmo nome, seguido da explicação de quando o arquivo chegou e de que foi depois da
correção pedida.

**Why this priority**: é o achado 23. Três nomes para o mesmo fato atrapalham a conversa entre a
comissão e o candidato — um diz "complementado", o outro lê "novo arquivo recebido".

**Independent Test**: no C09, reproduzir `D04-correcao-enviada` e `D05-gestao-ve-versao-2` e
comparar, letra a letra, o nome do estado nas duas telas.

**Acceptance Scenarios**:

1. **Given** um obrigatório reenviado depois da pendência, chamada aberta, **When** a comissão abre
   *Documentos da convocação*, **Then** o item diz *"Reenviado — aguardando nova conferência"*, e a
   contagem diz *"1 reenviado — aguardando nova conferência"*; com dois, *"2 reenviados — aguardando
   nova conferência"* (D-004).
2. **Given** o mesmo item, **When** o candidato abre a convocação, **Then** o cartão começa por
   *"Reenviado — aguardando nova conferência."*, seguido da explicação da D-003.
3. **Given** o mesmo item, **When** a comissão abre a condução, **Then** o passo da chamada nomeia o
   estado com o mesmo nome, e a ação continua sendo conferir.
4. **Given** uma pessoa cujo único pendente foi reenviado, **When** a comissão pede o aviso de
   pendência, **Then** a pessoa fica de fora, contada como *"documento reenviado — aguardando nova
   conferência"*; os avisos já registrados continuam com o texto gravado neles.
5. **Given** o reenviado conferido conforme, **When** qualquer das telas abre, **Then** o item diz o
   texto do conferido, e o nome do reenviado não aparece mais.

### Edge Cases

Cada caso abaixo é requisito, e entra na verificação como os `FR-`.

- **Prazo não iniciado, tudo enviado** (a pessoa pode enviar antes de o prazo começar). Título
  *"Acompanhe sua convocação"*; o cartão do prazo diz só a frase do prazo não iniciado do canal; a
  advertência já não aparecia, e continua sem aparecer.
- **Sem vencimento registrado, tudo enviado.** Título *"Acompanhe sua convocação"*; o cartão diz que
  a convocação não tem prazo registrado; sem advertência, como hoje.
- **Chamada só com documento facultativo, nada enviado.** Não há providência pendente: título
  *"Acompanhe sua convocação"*, frase de conclusão seguida da linha do opcional, sem advertência. A
  frase da conferência terminada **não** vale, porque a chamada não tem obrigatório (FR-6205).
- **Tc com um opcional enviado e ainda não conferido.** Vale a frase da conferência terminada,
  porque ela fala só dos obrigatórios; o cartão do opcional continua dizendo que a comissão vai
  conferir (D-002).
- **Facultativo pendente.** Não é providência pendente (o texto dele já diz *"Se quiser…"*): não
  muda o título nem traz a advertência.
- **Pendência nova num obrigatório depois de tudo enviado.** Volta a haver providência pendente:
  *"Você foi convocado!"* e a advertência, se o prazo estiver correndo.
- **Requerimento como única tarefa restante.** É providência pendente: *"Você foi convocado!"* e a
  advertência.
- **O mesmo arquivo enviado de novo sobre um item pendente.** Não é reenvio: a confirmação continua
  *"Este arquivo já tinha sido recebido."*, e o item continua pendente.
- **Facultativo reenviado.** Usa o mesmo nome, com o selo *"Opcional"*.
- **Vencimento decorrido com item reenviado sem conferência.** O título é o do vencido, como hoje; o
  cartão do reenviado mantém o nome, porque a conferência ainda é aceita depois do vencimento
  (FR-3588 da `115`).
- **Processo encerrado ou desfecho registrado com item reenviado sem conferência.** Ninguém vai
  conferir: o portal diz a variante passada da D-005, sem *"aguardando"*. Só o vencimento do prazo
  não basta para a variante passada. Na gestão, o nome segue a
  regra que hoje vale para o *recebido* nessa situação.
- **Convocação corrigida, com documento aproveitado da chamada anterior sem conferência.** O
  aproveitado está com a comissão: vale a frase de conclusão.
- **Chamada que pede só o Requerimento, ainda não enviado.** É providência pendente: *"Você foi
  convocado!"*, e a advertência no acompanhamento, como hoje (FR-6201, D-007).
- **Chamada que pede só o Requerimento, já enviado.** Sem providência pendente: *"Acompanhe sua
  convocação"*, o prazo visível, sem a advertência e sem a frase da conferência terminada (FR-6201).
- **Chamada que não pede nada pelo portal.** Fica como hoje até o desfecho: *"Você foi convocado!"*,
  *"Siga as instruções do Edital para esta convocação."* e, no acompanhamento, a advertência na
  condição da FR-1177 da `063` (FR-6201, D-007).
- **Pessoa com mais de uma inscrição convocada.** Tudo é por convocação: cada uma tem o seu título.

## Requirements *(mandatory)*

### Functional Requirements

#### A. A providência pendente

- **FR-6200**: Na chamada vigente que pede documento pelo portal, a **providência pendente do
  candidato** MUST ser a existência de ao menos uma **tarefa** da projeção da FR-3726 da `118`:
  documento obrigatório *a corrigir*, documento obrigatório *a enviar* ou Requerimento de Matrícula
  *a preencher*. Opcional a enviar, facultativo pendente, item com a comissão e item conferido MUST
  NOT contar como providência pendente. Ela é **derivada** a cada leitura, e nunca gravada (D-001).
- **FR-6201**: Na chamada vigente que **não pede documento** pelo portal (D-006):
  - **só com o Requerimento de Matrícula**: a providência pendente MUST ser o Requerimento ainda não
    enviado. Enviado, o título MUST ser *"Acompanhe sua convocação"*, o prazo MUST continuar visível
    (FR-6208), a advertência do não atendimento MUST NOT aparecer, e a frase da conferência
    terminada (FR-6205) MUST NOT ser usada. A ação e o link de hoje para o Requerimento enviado não
    mudam;
  - **sem nada pedido pelo portal**: a pessoa MUST ser tratada como com providência pendente até o
    desfecho — título *"Você foi convocado!"*, a ação *"Siga as instruções do Edital para esta
    convocação."* e, no acompanhamento, a advertência na condição da FR-1177 da `063` —, como hoje,
    porque o sistema não verifica o cumprimento externo. Nos dois casos, a página da convocação sem
    documento continua **sem** a advertência, como hoje (D-007).

#### B. O título

- **FR-6202**: A linha *"chamada aberta, prazo correndo, sem vencimento ou com a comunicação não
  enviada"* da tabela da FR-3858 da `121` MUST se dividir em duas: **com** providência pendente
  (FR-6200), *"Você foi convocado!"*; **sem** providência pendente, *"Acompanhe sua convocação"*. As
  demais linhas não mudam. O título novo MUST NOT afirmar matrícula, contratação, bolsa, vaga
  garantida ou aprovação, como os demais (FR-3751 da `118`).
- **FR-6203**: O título MUST acompanhar a providência pendente nos dois sentidos: o envio que tira a
  última tarefa leva, na volta da confirmação (FR-3870 da `121`), ao título *"Acompanhe sua
  convocação"*; a pendência nova num obrigatório leva de volta a *"Você foi convocado!"*.

#### C. A frase de conclusão e o próximo passo

- **FR-6204**: Na chamada que pede documento, sem providência pendente e fora do caso da FR-6205 —
  com algum obrigatório **com a comissão** (recebido, aproveitado sem conferência ou reenviado), ou
  sem obrigatório na chamada —, o resumo da chamada (FR-3862 da `121`) e o acompanhamento (linha 5
  da FR-3730 da `118`) MUST dizer a frase de conclusão da FR-3728 da `118`, sem mudança: *"Você não
  tem mais documentos para enviar agora. A comissão ainda vai concluir a análise."*
- **FR-6205**: Na chamada que pede ao menos um documento obrigatório, com **todos** os obrigatórios
  conferidos (*conforme* ou *não se aplica*), sem tarefa e sem desfecho, o resumo e o acompanhamento
  MUST dizer, no lugar da frase de conclusão, a **frase da conferência terminada**: *"A conferência
  dos documentos obrigatórios terminou. Aguarde o registro do resultado desta convocação."* (D-002).
  Ela MUST NOT ser usada em nenhum outro caso — nem na chamada só com facultativo, nem na que pede
  só o Requerimento (FR-6201). O estado dos opcionais não a altera, e ela MUST NOT dizer que eles
  foram conferidos. A linha do opcional da FR-3728 da `118`, quando houver opcional a enviar, MUST
  continuar a segui-la.
- **FR-6206**: Com desfecho vigente, a tela MUST continuar a da FR-3858 da `121` e da FR-3750 da
  `118` — título *"Resultado da sua convocação"*, rótulo do desfecho e, no aceite, a frase de que o
  registro não é matrícula, bolsa nem contrato. É a única situação em que a convocação se diz
  concluída.
- **FR-6207**: Sem desfecho, nenhum título, resumo, frase de estado, confirmação ou cartão MUST
  dizer ou sugerir *aprovado*, *aceito*, *deferido*, *concluído*, *tudo certo*, *pronto* ou *enviou
  tudo*. A marca visual do item conferido (cor, ícone ou selo) MUST NOT ser usada no item recebido,
  aproveitado sem conferência ou reenviado, nem no título *"Acompanhe sua convocação"*.

#### D. O prazo e a advertência

- **FR-6208**: O cartão do prazo (FR-3861 da `121`) e o prazo do acompanhamento MUST continuar
  visíveis com a chamada aberta, **com ou sem** providência pendente, nas mesmas variantes de hoje
  (prazo correndo, não iniciado, sem vencimento).
- **FR-6209**: A frase *"Se você não atender no prazo, a comissão poderá registrar o não atendimento
  desta convocação."* MUST aparecer **somente** com a comunicação enviada, o vencimento registrado,
  o prazo não encerrado **e** providência pendente do candidato (FR-6200 e FR-6201). Sem providência
  pendente, nenhuma frase de consequência MUST aparecer, nem na convocação nem no acompanhamento. É
  a FR-1177 da `063`, revista.
- **FR-6210**: A ressalva da FR-3864 da `121` (*"Esta convocação ainda não é a matrícula…"* ou
  *"…ainda não é o resultado…"*) MUST continuar em todo estado aberto, com ou sem providência
  pendente: ela não é frase de consequência.

#### E. O documento reenviado

- **FR-6211**: O estado do item que a FR-3590 da `115` chamava *complementado, aguardando
  conferência* — conferência pendente sobre apresentação anterior, e apresentação nova — MUST se
  chamar, em todo texto visível, **"Reenviado — aguardando nova conferência"**: com travessão, com
  maiúscula quando abre o rótulo e minúscula dentro de frase. A condição da derivação não muda. O
  identificador interno do estado não é texto de tela, e a implementação decide se o renomeia.
- **FR-6212**: Na gestão, o nome da FR-6211 MUST ser o do item na página *Documentos da convocação*,
  o da contagem dessa página e da condução — no singular, *"1 reenviado — aguardando nova
  conferência"*, e no plural, *"2 reenviados — aguardando nova conferência"*, sem "(s)" (D-004) —, o
  da ordem da condução (FR-3607 da `115`), o do passo da chamada (FR-5011 da `143`) e o da exclusão
  do aviso de pendência (FR-4607 da `134`). O passo PODE seguir com a ação (*"Conferir de novo"*) e
  com a explicação de quem reenviou e quando, desde que nenhuma delas dê outro nome ao estado.
- **FR-6213**: No portal, o cartão do item reenviado (linha *complementado* da tabela da FR-3746 da
  `118`) MUST começar pelo nome da FR-6211 nas colunas *aberta* e *encerrada pelo prazo*, seguido da
  explicação: *"Reenviado — aguardando nova conferência. Novo arquivo recebido em ‹data›, às ‹hora›,
  depois da correção pedida."* (D-003). Nas colunas *encerrada pelo Processo* e *decidida*, MUST
  dizer a variante passada: *"Reenviado em ‹data›; não foi conferido antes do encerramento do
  Processo."* e *"Reenviado em ‹data›; não foi conferido antes do resultado."* (D-005). O vencimento
  do prazo, sozinho, MUST manter o nome com *"aguardando"*, porque a conferência ainda é aceita
  (FR-3588 da `115`).
- **FR-6214**: Depois da implementação, os nomes *"Complementado, aguardando conferência"*,
  *"Reenviado(s), a conferir de novo"*, *"documento reenviado, a conferir de novo"*, *"documento
  reenviado: nova conferência"* e *"documento reenviado, aguardando conferência"* MUST NOT aparecer
  em texto visível da gestão nem do portal. As varreduras de vocabulário da `115` e da `118` MUST
  alcançar essa regra. Comentário e identificador interno não contam.

#### F. O que não muda

- **FR-6215**: Nada já publicado ou gravado MUST mudar: documentos e atos publicados, trilha,
  mensagens já enviadas, avisos de pendência já registrados — corpo e contagem de exclusões
  gravados neles — e exportações já geradas continuam com o texto do dia em que foram produzidos.
  As regras desta spec valem para o que for lido ou produzido depois da implementação.
- **FR-6216**: Esta revisão MUST NOT criar estado gravado, coluna, migration, rota, tela, máquina de
  estados ou notificação. Tudo é derivado do que a `115`, a `118` e a `121` já derivam.

### Key Entities

- **Providência pendente do candidato**: derivação de leitura sobre a projeção das obrigações da
  `118` (as tarefas da FR-3726 da `118`). Não é gravada.
- **Estado do item reenviado**: o estado da FR-3590 da `115` de conferência pendente sobre
  apresentação anterior com apresentação nova. Só o nome muda.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2000**: Nos cenários T, Tc, *só facultativo*, *prazo não iniciado com tudo enviado*, *sem
  vencimento com tudo enviado* e *só Requerimento, já enviado*, o título é *"Acompanhe sua
  convocação"* e a advertência do não atendimento aparece **zero** vezes, na convocação e no
  acompanhamento.
- **SC-2001**: Nos cenários C1, F, *pendência nova depois de tudo enviado*, *só Requerimento, ainda
  não enviado* e *nada pedido pelo portal, sem desfecho*, com o prazo correndo, o título é *"Você
  foi convocado!"* e a advertência aparece **exatamente uma** vez em cada tela que a mostra hoje: a
  convocação e o acompanhamento na chamada que pede documento; só o acompanhamento na que não pede
  (D-007).
- **SC-2002**: Em 100% dos cenários com chamada aberta e vencimento registrado, o prazo aparece,
  com ou sem providência pendente.
- **SC-2003**: Zero falsas conclusões: em nenhum cenário sem desfecho aparece *aprovado*, *aceito*,
  *deferido*, *concluído*, *tudo certo* ou *enviou tudo*; a frase da conferência terminada aparece
  em 100% dos cenários Tc e em **nenhum** outro — nem com obrigatório com a comissão, nem só com
  facultativo, nem só com o Requerimento; em nenhum cenário Tc aparece *"A comissão ainda vai
  concluir a análise."*
- **SC-2004**: O item reenviado tem **um** nome, idêntico letra a letra, nas cinco superfícies da
  gestão da FR-6212 e no cartão do portal — onde o estudo contou três —, e nenhuma contagem mostra
  "(s)": com um, *"1 reenviado"*; com dois, *"2 reenviados"*.
- **SC-2005**: Zero alterações em documento publicado, ato, trilha, mensagem ou aviso gravados antes
  da implementação, conferido pela comparação de uma amostra gravada antes e lida depois.
- **SC-2006**: Repetidas as capturas `B08-tudo-enviado`, `D04-correcao-enviada` e
  `D05-gestao-ve-versao-2` do estudo, as três mostram o comportamento desta spec.

## Assumptions

- A projeção das obrigações da `118` já distingue as tarefas (FR-3726 da `118`) e os totais por
  categoria (FR-3727 da `118`); a providência pendente se lê dela, sem consulta nova.
- O andamento da FR-3865 da `121` — *a corrigir*, *a enviar*, *aguardando conferência*, *conferidos*
  — já diferencia recebido de conferido e continua igual.
- *"Resultado da sua convocação"* e o rótulo do desfecho (FR-3750 da `118`) já são a convocação
  concluída; esta spec não muda a tela com desfecho.
- A mensagem da convocação não muda: ela sai quando tudo ainda está por fazer.

## Compatibilidade com regras anteriores

- **Princípio da imutabilidade (Constituição)**: nada publicado ou gravado muda (FR-6215).
- **A proibição de dizer que a pessoa "enviou tudo"** (decisão da `118` sobre a frase de conclusão)
  continua: o título novo não diz que a pessoa enviou tudo, e a frase de conclusão fica igual.
- **"Nenhuma máquina de estados nova"** (decisão de vocabulário da `118`): respeitada (FR-6216).
- **FR-274 da `019`**: o não atendimento só existe quando alguém o registra. A advertência continua
  sem prometer perda; ela só deixa de aparecer onde não há o que deixar de atender.

## Revisões de requisitos anteriores

> As redações anteriores ficam preservadas ao fim de cada alínea, no arquivo da feature revista, com
> a marca *"revista pela `154` em 2026-11-11, que vigora com a implementação dela"*. *Por que
> mudaram:* a 1ª a 7ª decisões e as D-001 a D-006, todas do usuário.

### `063` — o acompanhamento pela situação

**FR-1177, nova condição da segunda frase neutra.** "Se você não atender no prazo, a comissão poderá
registrar o não atendimento desta convocação." (convocado, **somente** com a comunicação enviada,
vencimento registrado, prazo não encerrado **e providência pendente do candidato** — FR-6200 e
FR-6201 da `154`). Sem providência pendente, nenhuma frase de consequência. O resto do requisito e o
acréscimo da `118` não mudam.

> *Redação anterior:* "(convocado, **somente** com a comunicação enviada, vencimento registrado e
> prazo não encerrado)" — o resto, igual.

**FR-1178, nova redação.** "Nada por enquanto" DEVE ser a ação quando nenhum ato pede algo da
pessoa. Na convocação com documento pedido e nada a fazer, ela DEVE vir seguida da frase de
conclusão da FR-3728 da `118` ou, com todos os obrigatórios conferidos e sem desfecho, da frase da
conferência terminada (FR-6205 da `154`).

> *Redação anterior:* a mesma, terminando em "seguida da frase de conclusão da FR-3728 da `118`, que
> diz que a comissão ainda vai concluir a análise."

### `115` — documentos na convocação

**FR-3590, linha da tabela.** *reenviado — aguardando nova conferência* | conferência pendente sobre
apresentação anterior, e apresentação nova.

> *Redação anterior:* *complementado, aguardando conferência* | (a mesma condição).

**FR-3591, linha *para conferir*.** algum item *recebido* ou *reenviado*.

> *Redação anterior:* algum item *recebido* ou *complementado*.

**FR-3607, contagens e ordem.** "as contagens (recebidos, pendentes, reenviados, conformes e
obrigatórios)"; na ordem, *reenviado* no lugar de *complementado*.

> *Redação anterior:* "complementados" e *complementado*.

### `118` — a jornada consolidada do convocado

**FR-3728, acréscimo.** Com todos os obrigatórios conferidos, sem tarefa e sem desfecho, vale a
frase da conferência terminada (FR-6205 da `154`) no lugar da frase de conclusão; só nesse caso. A
proibição de dizer que a pessoa enviou tudo, que está tudo certo, aceito, aprovado ou concluído
continua.

> *Redação anterior:* a mesma, sem este acréscimo.

**FR-3737, acréscimo.** O cartão do prazo continua com ou sem tarefa (FR-6208 da `154`); a frase de
consequência, só com providência pendente (FR-6209 da `154`).

> *Redação anterior:* a mesma, sem este acréscimo.

**FR-3746, linha *complementado* da tabela, que passa a se chamar *reenviado — aguardando nova
conferência*.** Colunas *aberta* e *encerrada pelo prazo*: *"Reenviado — aguardando nova
conferência. Novo arquivo recebido em ‹data›, às ‹hora›, depois da correção pedida."* (D-003);
*encerrada pelo Processo*: *"Reenviado em ‹data›; não foi conferido antes do encerramento do
Processo."*; *decidida*: *"Reenviado em ‹data›; não foi conferido antes do resultado."* (D-005).

> *Redação anterior:* *"Novo arquivo recebido em ‹data›, às ‹hora›, depois da correção pedida. A
> comissão vai conferir."* | idem à coluna *aberta* | *"Novo arquivo recebido em ‹data›; não foi
> conferido antes do encerramento do Processo."* | *"Novo arquivo enviado em ‹data›; não foi
> conferido antes do resultado."*

> Nos arquivos das outras features, as decisões desta spec são citadas pelo requisito que as
> aplica (FR-6213 da `154`), porque a varredura de decisões lê cada pasta como sua.

### `121` — a experiência da convocação

**Clarificação do título, acréscimo.** A resposta vale com providência pendente; sem ela, o título é
*"Acompanhe sua convocação"* (FR-6202 da `154`, por decisão do usuário de 11/11/2026).

**Caso-limite *Prazo não iniciado* (cenário K), acréscimo.** O título é *"Você foi convocado!"* com
providência pendente, e *"Acompanhe sua convocação"* sem ela.

**Caso-limite novo, *Chamada que não pede documento*.** Só com o Requerimento: *"Você foi
convocado!"* até o envio, e *"Acompanhe sua convocação"* depois, sem a advertência; sem nada pedido
pelo portal, como hoje até o desfecho (FR-6201 da `154`).

**FR-3858, linha da tabela dividida** (FR-6202 da `154`):

| Estado | Título |
|---|---|
| chamada *aberta*, prazo correndo, sem vencimento ou com a comunicação não enviada, **com** providência pendente | *"Você foi convocado!"* |
| chamada *aberta*, prazo correndo, sem vencimento ou com a comunicação não enviada, **sem** providência pendente | *"Acompanhe sua convocação"* |

> *Redação anterior:* uma linha só, *"Você foi convocado!"*.

**FR-3864, acréscimo.** A frase de consequência só aparece na condição da FR-1177 da `063`, revista
pela `154` — com providência pendente. A ressalva continua em todo estado aberto.

> *Redação anterior:* a mesma, sem este acréscimo.

### `134` — o aviso de pendência documental

**FR-4607, acréscimo.** A pessoa de fora é contada como *"documento reenviado — aguardando nova
conferência"* (FR-6212 da `154`). Os avisos já registrados guardam o texto deles.

> *Redação anterior:* a mesma, sem este acréscimo. O cenário 3 da história do gesto dizia
> *"documento reenviado, aguardando conferência"*.

### `143` — a convocação e os documentos

**FR-5011, nome do passo.** "documento reenviado — aguardando nova conferência" no lugar de
"documento reenviado, a conferir de novo". O cenário 3 da User Story 3 passa a dizer o mesmo nome.

> *Redação anterior:* "documento reenviado, a conferir de novo"; no cenário, "documento reenviado:
> nova conferência".

## Impacto para a implementação

Registrado para o plano; **nada disto foi implementado.** Medido na `main` em `4ff4098e`. O PR #477,
aberto, também mexe em `interface/views.py` e em `interface/conducao_da_convocacao.py`: o plano
desta spec precisa partir da `main` depois dele.

| Onde | O que diz hoje | O que muda |
|---|---|---|
| `portal/obrigacoes.py`, `TITULO_ABERTA` e `TITULOS` | *"Você foi convocado!"* para toda chamada aberta | título por providência pendente (FR-6202) |
| `portal/obrigacoes.py`, frase de conclusão | uma frase só sem tarefa | a frase da conferência terminada em Tc, e só nele (FR-6205) |
| `portal/obrigacoes.py`, texto do item `ITEM_COMPLEMENTADO` | *"Novo arquivo recebido em …, depois da correção pedida. A comissão vai conferir."* e as duas variantes | D-003 e D-005 (FR-6213) |
| `portal/situacao.py`, `NAO_ATENDIMENTO_PODE_SER_REGISTRADO` nas duas montagens da ação | posta sempre que há vencimento e o prazo corre | só com providência pendente (FR-6209); na montagem sem documento, tirar no ramo do Requerimento enviado e manter no de *"Siga as instruções do Edital"* (FR-6201) |
| título da convocação que pede só o Requerimento | *"Você foi convocado!"* sempre | *"Acompanhe sua convocação"* depois do envio (FR-6201) |
| `portal/views.py`, contexto da convocação (`consequencia`) e `portal/templates/portal/_chamada_da_convocacao.html` (`{% if o.prazo %}`) | a consequência aparece sempre que o prazo aparece | separar a condição do prazo da condição da consequência (FR-6208, FR-6209) |
| `portal/templates/portal/acompanhamento.html` | `acao.consequencia` | idem |
| `interface/views.py`, `ROTULO_DO_ITEM["COMPLEMENTADO"]` | *"Complementado, aguardando conferência"* | FR-6211 |
| `interface/templates/interface/convocacao_documentos.html`, contagem | *"Reenviado(s), a conferir de novo"*, com o plural por filtro | *"1 reenviado — aguardando nova conferência"*, *"2 reenviados — …"*, sem "(s)" (D-004) |
| `interface/conducao_da_convocacao.py`, passo `REENVIADO` | *"Conferir de novo: o candidato reenviou …"* | nomear o estado (FR-6212); a ação pode ficar |
| `avisos/application/pendencias.py`, `COMPLEMENTADA` | *"documento reenviado, aguardando conferência"* | FR-6212; o que já foi gravado fica (FR-6215) |
| `tests/test_vocabulario_dos_documentos_da_convocacao.py` | proíbe *enviou tudo*, *documento aprovad*… | acrescentar os nomes antigos da FR-6214 e os termos da FR-6207 |
| `tests/unit/portal/test_obrigacoes_da_convocacao.py`, `tests/interface/test_portal_convocacao.py`, `tests/interface/test_portal_documentos_da_convocacao.py`, `tests/integration/portal/test_destino_da_convocacao.py`, `tests/integration/convocacao/test_visibilidade_ao_candidato.py`, `tests/navegador/test_jornada_da_convocacao_121.py`, `tests/navegador/test_jornada_dos_documentos_da_convocacao.py`, `tests/unit/interface/test_conducao_da_convocacao.py` | afirmam *"Você foi convocado!"*, *"Complementado, aguardando conferência"* ou *"… depois da correção pedida"* | conferir cada um: os que montam cenário com tarefa continuam; os outros mudam |
| `docs/visao-sistema/` | descreve as telas de hoje | acompanhar no merge da implementação |

## Decisões

Todas do usuário, em 11/11/2026. Nenhuma está pendente.

### D-001 — Providência pendente é ter tarefa obrigatória

**Decisão do usuário (11/11/2026), aprovando a proposta.** A providência pendente deriva das tarefas
obrigatórias do candidato; opcionais e itens com a comissão ficam fora (FR-6200). A projeção da
`118` já separa o que a pessoa precisa fazer do que está com a comissão e do que é opcional, e ler
dali evita uma segunda regra que divergisse do resumo *"Você ainda precisa…"*: a página nunca diz
*"Acompanhe sua convocação"* e, logo abaixo, uma tarefa.

*Alternativa descartada:* contar o opcional não enviado como providência — manteria a advertência
para quem cumpriu tudo o que é obrigatório, que é o achado 20.

### D-002 — A frase da conferência terminada

**Decisão do usuário (11/11/2026), com redação dele.** *"A conferência dos documentos obrigatórios
terminou. Aguarde o registro do resultado desta convocação."* — **somente** quando todos os
obrigatórios estiverem conferidos e não houver tarefa nem desfecho (FR-6205). A frase fala dos
obrigatórios para não afirmar que os opcionais também foram conferidos. O resultado só existe quando
registrado (FR-6206), e cada cartão continua dizendo *"Conferido: de acordo com o Edital"* ou *"Não
se aplica"*.

*Redação proposta e substituída:* *"A comissão já conferiu seus documentos. Agora ela vai registrar
o resultado desta convocação."* — dizia "seus documentos", o que incluiria os opcionais.

### D-003 — O cartão do reenviado no portal, com a chamada aberta

**Decisão do usuário (11/11/2026), aprovando a proposta.** *"Reenviado — aguardando nova
conferência. Novo arquivo recebido em ‹data›, às ‹hora›, depois da correção pedida."* (FR-6213). O
nome abre o cartão (7ª decisão); a segunda frase é a explicação que contextualiza a correção. *"A
comissão vai conferir."* sai, porque o nome já o diz.

### D-004 — A contagem diz o nome, no singular e no plural

**Decisão do usuário (11/11/2026), com ajuste dele.** Na página *Documentos da convocação* e na
condução, *"1 reenviado — aguardando nova conferência"* e *"2 reenviados — aguardando nova
conferência"*, com singular e plural naturais e sem "(s)" na tela; nas contagens da FR-3607 da
`115`, *reenviados* (FR-6212). A contagem é do mesmo fato, e um terceiro nome para ela recriaria o
achado 23.

### D-005 — Sem conferência possível, o nome no passado

**Decisão do usuário (11/11/2026), aprovando a proposta.** Com o Processo encerrado ou o desfecho
registrado, ninguém vai conferir, e *"aguardando nova conferência"* seria falso. O portal diz
*"Reenviado em ‹data›; não foi conferido antes do encerramento do Processo."* e *"Reenviado em
‹data›; não foi conferido antes do resultado."* (FR-6213). **O vencimento do prazo, sozinho, mantém
*"aguardando"***, porque a conferência ainda pode ocorrer (FR-3588 da `115`).

### D-006 — A chamada que não pede documento pelo portal

**Decisão do usuário (11/11/2026), respondendo à pergunta da spec** (FR-6201):

- **Só o Requerimento pedido pelo portal:** ele conta como providência pendente até ser enviado.
  Depois, *"Acompanhe sua convocação"*, sem a advertência do não atendimento. A frase da conferência
  terminada não se aplica a esse caso, porque ele não tem documento a conferir.
- **Nada pedido pelo portal:** mantém-se a orientação de seguir as instruções do Edital e o
  comportamento atual até o desfecho — *"Você foi convocado!"* e a advertência na condição da
  FR-1177 da `063` —, porque o sistema não consegue verificar o cumprimento externo.

### D-007 — A página da convocação sem documento fica como hoje

**Decisão do usuário (11/11/2026), respondendo à contradição que o `/speckit-analyze` achou.** A cena 5
da US2 e a SC-2001 diziam que a tela de hoje da chamada sem documento traz a advertência do não
atendimento. A página da convocação sem documento nunca a mostrou: o parcial da chamada só a põe com
a projeção das obrigações, que essa chamada não tem; quem a mostra é o acompanhamento. **Fica como
hoje.** Na chamada que não pede documento — só o Requerimento ainda não enviado, ou nada pedido pelo
portal —, a advertência aparece só no acompanhamento, na condição da FR-1177 da `063` revista pela
FR-6209; a página da convocação continua sem ela (FR-6201, SC-2001).

*Alternativa descartada:* pôr a advertência também na página sem documento — seria mudança de tela
que a D-006 não pediu, e que a spec dizia ser "a de hoje".
