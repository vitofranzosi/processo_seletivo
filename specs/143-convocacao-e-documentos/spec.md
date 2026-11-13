# Feature Specification: A convocação e a conferência documental, pelas perguntas de quem conduz

**Feature Branch**: `claude/143-convocacao-e-documentos-770b40`, sobre a `main` em `daba322f`

**Created**: 2026-11-10

**Status**: Implementada e mergeada (#453). *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Draft

**Nenhuma regra de domínio nova.** Quem é chamado, a espécie, a ordem da fila, o fundamento, a
forma de comunicar, o prazo, a conferência de cada documento, o desfecho, a apuração da ocupação e
o aviso de pendência continuam os de hoje, pelos mesmos comandos e pelas mesmas portas. Não há
migration, rota, permissão, tabela, coluna nem estado persistido novo. O que muda é **como as duas
telas organizam o que já sabem**: a da convocação de um recorte e a dos documentos de uma
convocação.

**Input**: *"Evolução de UI/UX da convocação e da conferência documental (G5). Reorganizar a
convocação em áreas de trabalho; diferenciar, no texto e no visual, as vagas da apuração e as
pessoas efetivamente convocadas, aguardando resposta e com desfecho; a conferência orientada à
pessoa convocada, com o contexto completo e a passagem natural ao desfecho; depois da conferência,
deixar claro se o candidato foi ou não avisado da pendência — 'pendência registrada' nunca é
'candidato comunicado'; ações rotineiras destacadas e as excepcionais sem competir com elas;
navegação entre pessoas e tarefas sem perder o contexto; explicações breves de Ocupação, Corte,
Desfecho e Sucessão. Não reimplementar a 140; não criar fluxo paralelo de decisão; não inventar
estado; não criar outra lógica de prioridade."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de cinco mil a cinco mil e noventa e nove;
> - os critérios de mil quinhentos e sessenta a mil quinhentos e setenta e nove;
> - os requisitos de experiência de trezentos e setenta a trezentos e oitenta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`. A faixa foi reservada pela
> sessão que coordena as frentes G4 e G5, e conferida livre em 10/11/2026 na `main` e em todas as
> branches remotas. A `138` (PR #451) vai até o requisito quatro mil oitocentos e setenta e seis; a
> G4 (`142`) usa a faixa de quatro mil e novecentos.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-4763 da `139`"); decisão de outra feature, pelo assunto, nunca pelo identificador.
>
> **Origem.** O
> [estudo de continuidade operacional de 10/11/2026](../../doc/estudo-continuidade-operacional-2026-11-10/README.md)
> (PR #445): as jornadas D e E do mapa (`01-mapa-das-jornadas.md`), as melhorias M-05, M-08, M-09 e
> M-19 do inventário (`03-inventario-de-melhorias.md`) e os protótipos da convocação e dos
> documentos (`04-prototipos.md`). O protótipo é referência de comportamento, e não código a copiar.

## Por que esta feature existe

O estudo percorreu a convocação e a entrega documental nos cenários de treinamento da `134` (C10,
C11, C12 e C15) e encontrou o estado coerente e a tela difícil de ler:

1. **A tela da convocação tem ~3.500 px e nenhuma hierarquia.** Vagas, titulares, fila, avisos,
   chamadas, documentos, desfechos e regularização se sucedem como seções do mesmo peso. No C12, as
   chamadas — onde está todo o trabalho do dia — começam a ~1.900 px; o formulário do desfecho de
   uma convocação pronta, a ~3.000 px (passos E2 e E10 do estudo).
2. **"3 Ocupadas · 0 A ocupar" se lê como "três pessoas já preenchem as vagas"**, antes de qualquer
   chamada (passo D2). O número é da apuração: o titular habilitado conta como ocupante desde que a
   apuração foi emitida. Convocadas, responderam e matriculadas são outra coisa, e a tela não diz.
3. **Cada chamada oferece cinco ou seis botões do mesmo peso** — desfecho, indeferimento, atestado,
   reenvio da comunicação, correção —, e nenhum diz qual é o passo daquela pessoa agora.
4. **Registrar uma pendência não avisa ninguém** (passo E13): o gesto "Avisar as pessoas com
   documento pendente" existe, mas está noutra parte da tela, e nem a chamada nem a página dos
   documentos dizem se o candidato já foi avisado.
5. **A página dos documentos não diz de que Edital, Perfil e lista é a pessoa** (passo E3), não leva
   ao desfecho dela, e não leva à pessoa seguinte: depois de conferir, a volta é ao topo da
   convocação.

As cinco se resolvem com o que o sistema já sabe: o estado de cada chamada (`019`), o estado
documental de cada convocação (`115`, `117`, `131`), a apuração vigente (`016`), os avisos de
pendência e as tentativas de envio deles (`066`, `134`).

### O que esta spec cobre, e o que fica fora

**Cobre:**
- a tela da convocação de um recorte: contexto, um índice do que há a fazer, a leitura das vagas,
  o agrupamento das seções, o cartão de cada chamada;
- a página dos documentos de uma convocação: contexto, resumo, situação depois da conferência,
  caminho ao aviso e ao desfecho, navegação entre pessoas;
- explicações breves, recolhidas, de Ocupação, Corte, Desfecho e Sucessão.

**Fica fora:**
- a conferência antes de convocar os titulares, que é a `140` e não muda;
- qualquer conferência nova para a chamada individual ou para a convocação para regularizar (D-004);
- o Centro de Controle e o detalhe do Edital (PR #451, `138`) e a tela do sorteio (`142`);
- o portal do candidato.

## Clarifications

### Session 2026-11-10

- Q: A tela vira abas? → A: Não. Abas esconderiam informação e quebrariam os fragmentos da `139`
  (o `#chamadas`, o `#chamada-N`, o `#titulares`). As seções continuam todas na página, na mesma
  ordem lógica, agrupadas em áreas com rótulo e um índice no alto (D-001).
- Q: O índice no alto é um painel de indicadores? → A: Não. Cada linha é uma pergunta de quem
  conduz, com a resposta lida dos dados da própria tela e um link para o lugar do ato (D-002).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Saber, ao abrir a convocação, o que há a fazer neste recorte (Priority: P1)

A presidência abre a convocação de um recorte e vê, antes de qualquer seção: de que Edital, Perfil,
marco e lista se trata; quantas pessoas há a convocar, quantas foram convocadas, quantas aguardam
resposta e até quando, quantas têm documento a conferir, quantas têm pendência e quantas podem ser
avisadas agora, quantas estão prontas para o desfecho e quantas já têm desfecho. Cada linha com
trabalho leva ao lugar do ato.

**Why this priority**: é a pergunta que a pessoa traz para a tela, e hoje a resposta está espalhada
por 3.500 px.

**Independent Test**: no C12 (três convocados, nada conferido), a tela mostra "3 com documento a
conferir" no alto, e o link leva à primeira chamada; no C10 (ninguém convocado), "3 titulares a
convocar", com o link para o gesto da `140`.

**Acceptance Scenarios**:

1. **Given** o C10 antes de convocar, **When** a presidência abre a convocação da ampla, **Then** o
   alto diz Edital, Perfil, marco e lista, e o índice diz 3 titulares a convocar e 0 convocadas.
2. **Given** o C11, **When** a presidência abre a convocação, **Then** o índice diz 3 aguardando
   resposta com a data do primeiro vencimento, 1 com documento a conferir, 1 com pendência (1 pode
   ser avisada agora) e 1 aguardando o envio dos documentos.
3. **Given** um recorte em que ninguém mais pode ser chamado e nenhuma chamada está em aberto,
   **When** a tela abre, **Then** o índice não oferece link para ato nenhum e diz que não há
   providência neste recorte.

---

### User Story 2 — Ler as vagas sem confundir apuração com convocação (Priority: P1)

As vagas aparecem em dois grupos com títulos e aparência distintos: o que a **apuração da
ocupação** calculou (publicadas no Edital, efetivas, consideradas ocupadas na apuração, a ocupar na
apuração, e a data da apuração) e o que as **chamadas praticaram** (pessoas convocadas, aguardando
resposta, com desfecho registrado, aptas para formalização). Uma frase diz que estar considerada
ocupada na apuração não é ter sido convocada nem matriculada. Uma explicação recolhida diz o que é
a ocupação, com os números do recorte.

**Why this priority**: é o erro de leitura mais recorrente do estudo (M-09), e induz a não convocar.

**Independent Test**: no C10, antes de convocar, a tela diz "3 consideradas ocupadas na apuração" e
"0 pessoas convocadas" em grupos separados, e os números são os mesmos de antes desta spec.

**Acceptance Scenarios**:

1. **Given** o C10 antes de convocar, **When** a tela abre, **Then** os números da apuração são os
   de hoje, rotulados como da apuração, e o grupo das chamadas diz 0 convocadas.
2. **Given** a apuração obsoleta ou não emitida, **When** a tela abre, **Then** os avisos e os
   caminhos de hoje continuam, e o grupo das chamadas continua.

---

### User Story 3 — Cada chamada diz o próximo passo dela, e o aviso da pendência (Priority: P1)

Cada cartão de chamada começa pelo que falta para aquela pessoa, lido do estado do prazo e do estado
documental: emitir a comunicação; aguardar a resposta até tal data; aguardar o envio dos documentos;
conferir os documentos recebidos (ou o documento reenviado, que pede nova conferência); aguardar a
correção da pendência; registrar o desfecho, porque está pronta ou porque o vencimento decorreu; ou
o desfecho registrado. A ação rotineira desse passo é a primeira e a mais visível do cartão; as
excepcionais (indeferir pelas pendências, atestar fato externo, emitir a comunicação de novo,
corrigir) continuam no cartão, recolhidas, com peso menor.

Quando a chamada tem ou teve pendência, o cartão diz, sem confundir: quando a pendência foi
registrada; se houve aviso de pendência depois dela e em que situação ele está — registrado e
aguardando o despacho, aceito pelo servidor de correio, ou outra situação que o registro do envio
mostre —; ou que nenhum aviso foi registrado desde a pendência, e se o aviso pode ser pedido agora
(com o link para o gesto) ou por que não.

**Why this priority**: o operador registra a pendência e acha que o candidato foi comunicado
(E13); e a chamada pronta para o desfecho não se distingue das outras.

**Independent Test**: no C11, a chamada do 02 diz "nenhum aviso desde esta pendência — o aviso
pode ser pedido agora"; depois do gesto, "aviso registrado, sai pelo despacho dos avisos"; depois do
`despachar_avisos`, "aceito pelo servidor de correio em …".

**Acceptance Scenarios**:

1. **Given** uma chamada pronta para o desfecho, **When** a tela abre, **Then** o cartão diz "Pronta
   para o desfecho" e o formulário do desfecho vem aberto nele.
2. **Given** uma chamada com pendência registrada e nenhum aviso depois dela, **When** a tela abre,
   **Then** o cartão não usa "avisado", "comunicado", "enviado" nem "entregue" para a pendência.
3. **Given** o candidato reenviou o documento pendente, **When** a tela abre, **Then** o cartão diz
   "documento reenviado — aguardando nova conferência" e não oferece o aviso. *Revisto pela `154` em
   2026-11-11, que vigora com a implementação dela (FR-6212 da `154`); a redação anterior dizia
   "documento reenviado: nova conferência".*
4. **Given** quem só consulta (auditoria) ou quem só confere, **When** a tela abre, **Then** o
   cartão diz o passo, mas não oferece ação que essa pessoa não pode praticar.

---

### User Story 4 — Conferir os documentos sabendo quem é a pessoa, e seguir (Priority: P1)

A página dos documentos diz, no alto: a pessoa e a inscrição; o Edital, o Perfil, o marco e a lista;
a espécie, a situação e o vencimento da convocação. Um resumo conta os documentos conformes, a
conferir, pendentes, a apresentar e "não se aplica". Uma seção "Situação desta convocação" diz o que
acontece agora — o mesmo passo do cartão da chamada, com o aviso da pendência —, e leva: ao primeiro
documento a conferir; ao gesto do aviso; ao desfecho desta pessoa, no cartão dela na convocação; à
pessoa anterior e à seguinte do recorte; à próxima com documento a conferir; e de volta às chamadas.

**Why this priority**: conferir e decidir são da mesma pessoa e da mesma convocação, e hoje ficam
em telas que não se apontam.

**Independent Test**: no C12, conferir tudo como conforme numa convocação leva a "Pronta para o
desfecho" com o link "Registrar o desfecho desta convocação", que abre a convocação no cartão dela,
com o formulário aberto.

**Acceptance Scenarios**:

1. **Given** a página dos documentos de qualquer convocação, **When** ela abre, **Then** o Edital, o
   Perfil, o marco e a lista estão no alto, fora da migalha.
2. **Given** uma pendência registrada agora, **When** a página volta, **Then** a situação diz que a
   pendência foi registrada e que o candidato só recebe e-mail pelo gesto do aviso.
3. **Given** um recorte com três convocações, **When** a página da segunda abre, **Then** há link
   para a primeira e para a terceira, e para a próxima com documento a conferir.

---

### User Story 5 — As operações excepcionais em seu lugar, explicadas (Priority: P2)

A chamada individual, a fila de suplentes e a convocação para regularizar ficam numa área própria,
"Fila, suplentes e regularização", depois das chamadas, com uma frase que diz quando elas servem. Os
termos Ocupação, Corte, Desfecho e Sucessão ganham uma explicação de duas ou três frases, recolhida,
no lugar em que aparecem.

**Why this priority**: são operações legítimas e raras; hoje dividem a atenção com as rotineiras.

**Independent Test**: no C11 (titulares todos chamados), a fila aparece depois das chamadas, e o
formulário de chamar uma pessoa da fila continua o mesmo.

**Acceptance Scenarios**:

1. **Given** o C15 depois de convocar as duas habilitadas, **When** a tela abre, **Then** a área da
   fila diz que não há mais quem chamar, com a explicação do corte, e o índice não oferece ato.

### Edge Cases

- **Recorte que ninguém declarou** (a `126`): o índice diz "Não se aplica" e não oferece ato; as
  áreas que não se aplicam não aparecem.
- **Marco intermediário** (a `133`): a tela não convoca; o índice não conta titulares a convocar e a
  área da fila não aparece, como hoje.
- **Ordem por documentos** (`?ordem=documentos`): os cartões mudam de ordem, e os links do índice
  continuam levando à chamada certa, pela âncora estável da convocação.
- **Convocação corrigida**: a âncora estável é a da convocação vigente; o aviso registrado para a
  convocação que ela sucedeu conta para a mesma chamada.
- **Aviso anterior à pendência**: um aviso registrado antes da pendência mais recente não a cobre; o
  cartão diz que não houve aviso desde ela.
- **Envio de avisos desabilitado na instalação**: o aviso não é oferecido, e o cartão diz que o
  envio de avisos está desabilitado.
- **Chamada sem documento pedido**: o passo é o do prazo (aguardando resposta até…), sem linha de
  documentos.
- **Vencimento decorrido com documento a conferir**: o passo é registrar o desfecho; a linha dos
  documentos continua dizendo o que há a conferir.
- **Quem só confere** (alocado à conferência): vê o índice e os cartões; o desfecho, que é da
  gestão, aparece como passo de quem conduz, sem formulário.
- **Auditoria**: lê tudo, sem nenhuma ação.

## Requirements *(mandatory)*

### Functional Requirements

**Contexto e índice da convocação**

- **FR-5000**: A tela da convocação MUST dizer, logo abaixo do título, o número do Edital, o Perfil,
  o marco e a lista do recorte.
- **FR-5001**: A tela da convocação MUST ter, antes das seções, um índice "Neste recorte, agora" que
  responde, com números lidos da mesma leitura do recorte que a tela já faz: titulares a convocar
  (para quem pode convocar), convocações sem comunicação, aguardando resposta (com o primeiro
  vencimento), vencidas sem desfecho, com documento a conferir, com pendência aguardando o
  candidato (e quantas podem ser avisadas agora), aguardando o envio dos documentos, prontas para o
  desfecho e com desfecho.
- **FR-5002**: Cada linha do índice com número diferente de zero MUST levar ao lugar do ato: a
  seção que a tela já tem, ou o cartão da primeira chamada naquele estado. Linha de que a pessoa
  não pode praticar o ato leva à leitura (as chamadas), e não ao formulário.
- **FR-5003**: O índice MUST NOT ordenar, priorizar nem escolher providências: a ordem das linhas é
  fixa, e a prioridade continua sendo a do andamento, mostrada depois de um ato pelo bloco do
  próximo passo da `127` e da `139`.
- **FR-5004**: Sem providência no recorte, o índice MUST dizer isso, sem link.

**As vagas**

- **FR-5005**: Os números da apuração MUST aparecer num grupo próprio, "Pela apuração da ocupação",
  rotulados como publicadas no Edital, efetivas, consideradas ocupadas na apuração e a ocupar na
  apuração, com a data em que a apuração vigente foi emitida. Os valores MUST ser os de hoje.
- **FR-5006**: As contagens das chamadas MUST aparecer num grupo distinto, "Pelas chamadas
  praticadas": pessoas convocadas, aguardando resposta, com desfecho registrado e aptas para
  formalização.
- **FR-5007**: A seção das vagas MUST dizer que estar considerada ocupada na apuração não é ter sido
  convocada nem matriculada, e MUST oferecer, recolhida, uma explicação da ocupação com os números
  do recorte.

**Áreas**

- **FR-5008**: As seções da tela MUST ficar agrupadas em três áreas, nesta ordem: "Convocar"
  (titulares; comunicações a emitir), "Acompanhar e conferir" (não atendimento das vencidas; aviso
  de pendência; aviso das chamadas publicadas; chamadas praticadas) e "Fila, suplentes e
  regularização" (quem pode ser chamado, a chamada individual, a regularização). Área sem seção não
  aparece.
- **FR-5009**: Os identificadores e fragmentos que a `139` usa (`numeros`, `titulares`,
  `pendentes`, `vencidos`, `fila`, `regularizar`, `avisar-pendencias`, `chamadas`, `chamada-N` na
  ordem padrão) MUST continuar existindo e levando às mesmas seções.

**O cartão da chamada**

- **FR-5010**: Cada chamada MUST ter um identificador estável, derivado da convocação vigente, que
  não depende da ordem da tela.
- **FR-5011** *(revista pela `154` em 2026-11-11, que vigora com a implementação dela — a redação anterior está ao fim desta alínea)*:
  Cada chamada MUST começar pelo passo dela, lido do estado do prazo e do estado
  documental já derivados: desfecho registrado; comunicação a emitir; vencimento decorrido sem
  desfecho; documentos a conferir; documento reenviado — aguardando nova conferência; pendência
  aguardando o candidato; aguardando o envio dos documentos; pronta para o desfecho; aguardando a
  resposta. O passo do reenviado nomeia o estado como a FR-6211 da `154`; a ação dele (*"Conferir de
  novo"*) e a explicação de quem reenviou e quando podem segui-lo (FR-6212 da `154`).

  > **Redação anterior à `154`, preservada:** a mesma lista, com *"documento reenviado, a conferir
  > de novo"* no quinto passo. *Por que mudou:* o mesmo fato tinha três nomes entre a gestão e o
  > portal (achado 23 do estudo da jornada final, decisão do usuário de 11/11/2026).
- **FR-5012**: O passo MUST oferecer a ação rotineira dele só a quem pode praticá-la: conferir, para
  quem confere; o desfecho, a emissão e o não atendimento, para quem conduz.
- **FR-5013**: Na chamada pronta para o desfecho, e na de vencimento decorrido sem desfecho, o
  formulário do desfecho MUST vir aberto. Nas demais, recolhido, como hoje.
- **FR-5014**: As ações excepcionais da chamada — indeferir pelas pendências, atestar fato externo,
  emitir a comunicação de novo, corrigir — MUST continuar no cartão, com o mesmo formulário e o
  mesmo comando, com peso visual menor que a ação do passo.

**O aviso da pendência**

- **FR-5015**: A chamada com documento pendente ou reenviado MUST dizer quando a pendência mais
  recente foi registrada.
- **FR-5016**: Se houve aviso de pendência para a chamada depois dessa pendência, a chamada MUST
  dizer quando ele foi registrado e a situação do envio, pela derivação de estado da `066`, com as
  palavras dela ("aceita pelo servidor de correio", e nunca "entregue", "recebida" ou "lida").
- **FR-5017**: Sem aviso depois da pendência, a chamada MUST dizer que nenhum aviso foi registrado
  desde ela e que o candidato a vê no portal; e MUST dizer se o gesto do aviso a alcançaria agora,
  com o link para ele, ou o motivo pelo qual não alcançaria, pela mesma regra da prévia do gesto.
- **FR-5018**: Nenhum texto da tela MUST tratar pendência registrada como comunicação ao candidato.

**A página dos documentos**

- **FR-5019**: A página dos documentos MUST dizer, no alto, a pessoa e a inscrição, o Edital, o
  Perfil, o marco e a lista, a espécie, a situação do prazo e o vencimento.
- **FR-5020**: A página MUST mostrar um resumo dos documentos pedidos: conformes, a conferir,
  pendentes, a apresentar e não se aplica após análise.
- **FR-5021**: A página MUST ter uma seção "Situação desta convocação" com o mesmo passo e a mesma
  situação do aviso do cartão da chamada (FR-5011, FR-5015 a FR-5017).
- **FR-5022**: Pronta para o desfecho, a seção MUST levar, para quem conduz, ao cartão desta
  convocação na tela da convocação, pela âncora estável, onde o formulário vem aberto. Nenhum
  formulário de desfecho novo é criado nesta página.
- **FR-5023**: Com pendência, a seção MUST levar ao gesto do aviso na tela da convocação, dizendo
  que ele alcança todas as pessoas com pendência do recorte.
- **FR-5024**: A página MUST levar à pessoa anterior e à seguinte do recorte, na ordem da tela da
  convocação, à próxima com documento a conferir (se houver outra), às chamadas e à fila de
  conferência (a ordem por documentos).

**Explicações**

- **FR-5025**: Ocupação, Corte, Desfecho e Sucessão MUST ter, onde aparecem, uma explicação
  recolhida de no máximo três frases, com o efeito no recorte quando houver número a citar.

**Restrições**

- **FR-5026**: Nenhum comando, porta, autorização, chave de idempotência, assinatura de alcance ou
  conferência de texto MUST mudar. O gesto dos titulares continua passando pela conferência da
  `140`.
- **FR-5027**: A tela da convocação MUST continuar sem consulta por linha: o aviso de cada chamada
  sai de leituras de número fixo para o recorte.
- **FR-5028**: Nada desta spec usa estilo ou script escrito no template.

### Requisitos de experiência

- **UX-370**: A 1440 × 900, o índice "Neste recorte, agora" está inteiro na primeira tela no C11 e
  no C12.
- **UX-371**: O passo da chamada é a primeira linha do cartão, abaixo do nome, com borda e cor do
  tipo de passo, e a cor nunca é a única informação.
- **UX-372**: Os dois grupos de números da seção das vagas são distintos à vista: o da apuração com
  borda tracejada e o rótulo "calculado", o das chamadas com borda contínua.
- **UX-373**: A 375 px, nenhuma das duas telas rola na horizontal.
- **UX-374**: As ações excepcionais da chamada ficam numa linha de botões secundários; aberta uma,
  ela ocupa a largura do cartão.

### Key Entities

- **Passo da chamada**: leitura, nunca gravada, do estado do prazo (`019`) e do estado documental
  (`115`) de uma convocação vigente.
- **Situação do aviso de pendência**: leitura, nunca gravada, da conferência pendente mais recente
  e do destinatário de aviso de pendência mais recente da chamada, com o estado derivado da `066`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1560**: No C12, a 1440 × 900, as respostas "com documento a conferir" e "prontas para o
  desfecho" ficam dentro da primeira tela (antes, a primeira chamada estava a ~1.900 px).
- **SC-1561**: No C12, seguir "Registrar o desfecho desta convocação" a partir dos documentos de uma
  convocação pronta deixa o formulário do desfecho dela dentro da primeira tela (antes, ~3.000 px).
- **SC-1562**: Em todos os cenários da `134` que têm convocação, os números da apuração e das
  chamadas são os mesmos antes e depois desta spec.
- **SC-1563**: No C11, a chamada com pendência diz, nos três momentos — sem aviso, com aviso
  registrado e depois do despacho —, a situação real, e em nenhum diz "avisado" antes do registro.
- **SC-1564**: A tela da convocação não ganha consulta por linha: com 5 e com 45 convocações com
  documentos, a diferença de consultas continua dentro da margem de hoje.
- **SC-1565**: Nenhuma rota, migration, permissão, linha no inventário de negativas ou violação de
  CSP nova; a suíte inteira passa contra PostgreSQL.
- **SC-1566**: A 375 px, as duas telas não rolam na horizontal nos cenários C10, C11, C12 e C15.

## Assumptions

- O cenário com mais de uma lista é o do Perfil com ampla e cota PPP dos cenários da `134`: a ampla
  com convocações e a PPP noutro estado.
- O estado de envio do aviso é o que a `066` deriva dos registros de tentativa; o sistema não sabe
  o que acontece depois da aceitação pelo servidor de correio.
- A prévia do aviso de pendência já seleciona pessoa a pessoa; expor o motivo de cada uma à tela
  não muda a regra.

## Compatibilidade com regras anteriores

- A FR-4763 e a FR-4764 da `139` continuam: o `#chamadas` e o `#chamada-N` existem e levam ao mesmo
  lugar.
- As conferências da `125` e da `140` continuam as mesmas; o formulário do desfecho continua
  passando pela conferência do texto.
- A ordem por documentos da `115` continua; o índice usa a âncora estável para não depender dela.

## Decisões

### D-001 — Áreas com rótulo, e não abas

**Decisão**: as seções ficam todas na página, agrupadas em três áreas com rótulo e uma frase, depois
do índice. Nenhuma seção fica escondida atrás de aba ou de bloco recolhido que não estivesse
recolhido antes.

**Por quê**: abas exigiriam script e esconderiam o alvo dos fragmentos da `139` — o navegador não
abre uma aba para rolar até o id. O índice e as áreas dão a hierarquia sem esconder nada.

### D-002 — O índice responde perguntas, e não prioriza

**Decisão**: o índice lista perguntas fixas com o número e o link para o lugar do ato. Ele não
destaca "a sua próxima providência" nem reordena por urgência; marca, só por estilo, as linhas que
têm trabalho para quem está vendo.

**Por quê**: a prioridade é do andamento (`interface/andamento.py`), e o usuário vetou uma segunda
lógica. O bloco do próximo passo da `127` continua aparecendo depois de cada ato.

### D-003 — A âncora estável da chamada é a convocação vigente

**Decisão**: cada cartão ganha `id="convocacao-<id da convocação vigente>"`, além do `chamada-N` da
`139`. O índice e a página dos documentos levam a ela.

**Por quê**: o `chamada-N` muda com a ordem por documentos, e a página dos documentos não conhece a
posição da pessoa sem ler o recorte inteiro na ordem da tela.

### D-004 — A chamada individual e a regularização ficam como estão

**Decisão**: a chamada de uma pessoa da fila e a convocação para regularizar continuam praticando e
comunicando no clique, com a conferência de texto da `125` quando há complemento. Esta spec não
acrescenta conferência a elas.

**Por quê**: a `140` já registrou essa escolha (a primeira decisão dela) como achado para o usuário
decidir, e a decisão continua sendo dele: uma conferência a mais é um passo a mais em atos raros e
deliberados, escolhidos pessoa a pessoa no próprio formulário. Conferido em 10/11: nenhuma das duas
ajudas promete conferência que não aconteça. **Decisão em aberto, do usuário:** passar a chamada
individual e a regularização pela conferência da `140`.

### D-005 — O desfecho continua na convocação

**Decisão**: a página dos documentos não ganha formulário de desfecho; ela leva ao cartão da
convocação, onde o formulário vem aberto quando a chamada está pronta.

**Por quê**: o desfecho é da gestão e a conferência é também do membro alocado; o formulário tem a
ciência das inaplicabilidades, os atestados e a conferência do texto, e volta à convocação. Um
segundo formulário seria o fluxo paralelo de decisão que o pedido veta.

### D-006 — O aviso alcança o recorte, e a página da pessoa não o pratica

**Decisão**: a página dos documentos leva ao gesto do aviso na convocação e diz que ele alcança
todas as pessoas com pendência do recorte; ela não tem botão próprio.

**Por quê**: o gesto da `134` é do recorte, com o limite de um por pessoa por dia. Um botão na
página de uma pessoa leria como "avisar esta pessoa" e avisaria todas.

### D-007 — O passo da chamada é uma leitura do estado, e não uma regra

**Decisão**: o passo de cada chamada é escolhido pela precedência desfecho → comunicação → vencimento
→ estado documental → prazo, sobre estados que já existem; ele não muda o que o comando aceita. O
formulário do desfecho continua presente em toda chamada sem desfecho para quem conduz, como hoje.

**Por quê**: o passo orienta; quem decide se o ato pode ser praticado continua sendo o comando.
Esconder o desfecho de uma chamada que "não está pronta" seria a interface proibindo o que o
serviço permite (o indeferimento, a desistência expressa).

## Fora do escopo

- Conferência para a chamada individual e para a regularização (D-004).
- O Centro de Controle, o detalhe do Edital e a tela do sorteio.
- O portal do candidato (M-20 do estudo).
- Qualquer mudança no texto do aviso, no limite diário ou no despacho.
