# Feature Specification: O caminho do candidato até a convocação e o Requerimento de Matrícula

**Feature Branch**: `claude/friendly-chaplygin-8884a1`

**Created**: 2026-10-06

**Status**: Draft

**Input**: o achado **H.18** da Revisão 5 do manual (PR vitofranzosi/processo_seletivo#250), conferido
em 06/10/2026 sobre a `main` 4602b04, e o escopo mínimo que o usuário decidiu para ele na mesma data.

> **Faixa de identificadores.** Abre em **FR-1089**, **SC-424** e **UX-145**. O teto medido em
> 06/10/2026 em todas as worktrees, com quatro dígitos, era FR-1088, SC-423 e UX-144 — da `058` e da
> `057`, já mergeadas. As decisões desta spec nascem em `D-001` e moram no [research.md](research.md);
> decisão de outra feature é citada pela feature e pelo número dela, por extenso.

**A frase que governa:**

> Quem foi convocado chega à convocação pelo portal, sem depender da mensagem — e, quando o Edital
> pede o Requerimento de Matrícula na convocação, chega a ele pelo mesmo caminho.

**E a frase que mantém o corte:**

> Esta feature é navegação. Nenhuma regra de convocação, de prazo ou de requerimento muda; nenhuma
> tela da gestão muda; nenhuma rota nasce.

---

## Por que esta feature existe

A `019` criou a tela da convocação do candidato e escreveu, no comentário da própria view, que *"o
candidato não deve depender da caixa de entrada para saber que foi chamado"*. A `029` criou o
Requerimento de Matrícula e registrou, no orçamento de consulta dela, que *"o caminho para o
requerimento é o cartão da inscrição e a tela da convocação"*. A `050` declarou que *"o portal do
candidato não muda"*. As três frases supunham uma navegação que nenhuma das três construiu:

| O que existe | Por onde se chega hoje |
|---|---|
| A tela da convocação (`inscricoes/<id>/convocacao`) | por nenhuma tela do portal — só digitando o endereço |
| O Requerimento, quando o Edital o pede **na inscrição** | pelo cartão em "Sua inscrição" |
| O Requerimento, quando o Edital o pede **na convocação** | por nenhuma tela do portal |
| A mensagem de convocação | aponta "Minhas inscrições", que não mostra a convocação |

O resultado é que a pessoa convocada, ao seguir a mensagem, chega a uma lista que diz "Acompanhar";
o acompanhamento não fala de convocação; e o requerimento, que só abre depois da chamada, não tem
porta nenhuma. Quem não recebeu a mensagem — caiu no spam, foi para um endereço antigo — não tem como
saber que foi chamado, que é exatamente o caso que a `019` existia para cobrir. E o prazo corre do
**envio** da comunicação, e não da leitura.

**O que não muda.** O conteúdo da tela da convocação, o registro da leitura dela na trilha
(`FR-288b` da `019`), as duas ausências (`FR-294`), a política de disponibilidade do requerimento
(`FR-373`, `FR-405`, `FR-410` da `029`) e a recusa uniforme da titularidade (`FR-071`, `FR-399`).

---

## Clarifications

### Session 2026-10-06

- Q: Para onde a mensagem de convocação deve apontar? → A: Continua apontando "Minhas inscrições",
  que passa a mostrar a convocação; endereço e texto não mudam, e nada muda na gestão nem nos lotes
  da `050` (FR-1104).
- Q: A exibição da convocação no acompanhamento entra na trilha como leitura? → A: Não. Só a abertura
  da tela da convocação registra leitura; lista e acompanhamento não gravam nada (FR-1103).
- Q: Convocação concluída aparece em "Minhas inscrições"? → A: Sim, como nota discreta de texto com o
  desfecho registrado; a ação principal continua "Acompanhar" (FR-1091).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Em "Minhas inscrições", a convocação aberta aparece e leva à tela dela (Priority: P1)

Joana se inscreveu, foi classificada e, semanas depois, foi convocada. A mensagem foi para um
endereço que ela não lê mais. Ela entra no portal para acompanhar e, na lista, a inscrição diz que
há convocação aberta, com a ação "Ver convocação". Um clique a leva à convocação daquela inscrição,
com o prazo e o que fazer.

**Why this priority**: É o achado em si. Sem isto, a tela da convocação é inalcançável e o prazo da
pessoa corre sem que o portal a avise.

**Independent Test**: Com uma inscrição convocada e outra não, abrir "Minhas inscrições": só a
convocada mostra a indicação e "Ver convocação"; o clique leva a `portal:convocacao` daquela
inscrição.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada com convocação vigente sem desfecho, **When** a titular abre
   "Minhas inscrições", **Then** o item diz, por texto e por símbolo, que há convocação aberta, e a
   ação principal dele é "Ver convocação", que leva à tela da convocação daquela inscrição.
2. **Given** a mesma convocação antes do envio da comunicação, **When** a titular abre a lista,
   **Then** o item também a indica — o portal é o lugar onde a informação está sempre, inclusive
   antes da mensagem partir.
3. **Given** uma inscrição sem convocação, **When** a titular abre a lista, **Then** o item continua
   como hoje, com "Acompanhar".
4. **Given** uma inscrição com convocação já desfechada, **When** a titular abre a lista, **Then** o
   item diz, em texto discreto, a situação registrada da convocação, e a ação principal continua
   "Acompanhar".
5. **Given** um item com convocação aberta, **When** a titular quer o acompanhamento, **Then** ele
   continua alcançável a partir do mesmo item.

---

### User Story 2 — O Requerimento de Matrícula pedido na convocação tem porta (Priority: P1)

O Edital de Carlos pede o Requerimento de Matrícula "quando o candidato for convocado". Carlos foi
convocado. Na tela da convocação e no acompanhamento aparece "Preencher Requerimento de Matrícula";
ele preenche, envia, e volta depois para conferir o que enviou pelo mesmo caminho.

**Why this priority**: Sem isto, quem é convocado num Edital que coleta na convocação não tem como
cumprir a etapa pelo portal — e a etapa decide a vaga.

**Independent Test**: Num Edital com o momento "na convocação", convocar a pessoa e conferir que a
tela da convocação e o acompanhamento oferecem "Preencher Requerimento de Matrícula"; depois do envio,
que oferecem a conferência do enviado.

**Acceptance Scenarios**:

1. **Given** Edital que pede o requerimento na convocação e inscrição com convocação em aberto,
   **When** a titular abre a tela da convocação ou o acompanhamento, **Then** vê o chamado
   "Preencher Requerimento de Matrícula", que leva à tela do requerimento daquela inscrição.
2. **Given** o requerimento já em preenchimento, **When** a titular volta, **Then** o mesmo chamado
   leva ao rascunho, com o que ela já preencheu.
3. **Given** o requerimento enviado, **When** a titular volta — com a convocação em aberto ou já
   desfechada —, **Then** vê o caminho para conferir o que enviou, e não o chamado para preencher.
4. **Given** Edital que pede o requerimento na inscrição, já enviado, e inscrição convocada,
   **When** a titular abre a convocação, **Then** vê o caminho para conferir o enviado, que é onde a
   `029` oferece *conferir e atualizar* (`FR-410`).
5. **Given** convocação desfechada sem requerimento enviado, ou Edital que não pede requerimento,
   **When** a titular abre a convocação ou o acompanhamento, **Then** nenhum chamado ao requerimento
   aparece — um botão que só levaria a recusa é pior do que nenhum.

---

### User Story 3 — O acompanhamento apresenta a convocação, aberta ou concluída (Priority: P2)

Joana atendeu à convocação e a instituição registrou o desfecho. Meses depois ela volta ao
acompanhamento e encontra a convocação ali: a espécie, o prazo que havia, a situação registrada, e o
caminho para a tela completa.

**Why this priority**: É o que torna o estado concluído consultável, e o que faz o acompanhamento
cumprir o nome dele. Vem depois das duas primeiras porque, sem elas, a pessoa nem chega à fase.

**Independent Test**: Com a convocação aberta e, depois, com desfecho registrado, abrir o
acompanhamento e conferir a seção da convocação nos dois estados.

**Acceptance Scenarios**:

1. **Given** inscrição com convocação vigente, **When** a titular abre o acompanhamento, **Then** há
   uma seção "Convocação" com a espécie, o prazo, a situação e "Ver convocação".
2. **Given** a convocação com desfecho registrado, **When** a titular abre o acompanhamento, **Then**
   a seção continua lá, dizendo a situação registrada, e "Ver convocação" continua levando à tela.
3. **Given** convocação corrigida por sucessão, **When** a titular abre o acompanhamento, **Then** a
   seção mostra a sucessora, e nunca o prazo que deixou de valer.
4. **Given** inscrição sem convocação nenhuma, **When** a titular abre o acompanhamento, **Then** não
   há seção de convocação — a ausência se diz em ausência de dado.

---

### User Story 4 — Ninguém alcança a convocação ou o requerimento de outra pessoa (Priority: P1)

Os caminhos novos levam à convocação e ao requerimento **da própria** inscrição. Um identificador de
outra inscrição, de outra pessoa, digitado ou trocado no endereço, recebe a mesma recusa que um
identificador inexistente.

**Why this priority**: Estas telas carregam o dado mais sensível do portal — filiação, documento,
endereço, cor/raça. Mostrar o caminho a mais gente sem conferir a titularidade seria pior do que não
mostrar caminho nenhum.

**Independent Test**: Com duas pessoas, cada uma com inscrição convocada, conferir que a lista e o
acompanhamento de uma não mostram a convocação da outra, e que as rotas da outra respondem como as
de uma inscrição inexistente.

**Acceptance Scenarios**:

1. **Given** Maria e João, os dois convocados, **When** Maria abre a lista e o acompanhamento,
   **Then** só a convocação dela aparece, e nenhum endereço da convocação ou do requerimento de João.
2. **Given** Maria autenticada, **When** ela pede a convocação, o requerimento, o requerimento
   anterior ou o acompanhamento da inscrição de João, **Then** recebe a mesma resposta — status e
   corpo — que para um identificador que não existe.
3. **Given** ninguém autenticado, **When** se pede qualquer dessas rotas, **Then** a resposta é a de
   hoje, e nenhuma delas revela se a inscrição existe.

---

### Edge Cases

- **Duas inscrições da mesma pessoa, uma convocada.** Só o item convocado muda; o outro continua com
  "Acompanhar".
- **Convocação corrigida por sucessão.** Lista, acompanhamento e tela da convocação mostram a
  sucessora — a mesma regra de vigência em todos os lugares.
- **Prazo decorrido sem desfecho.** A convocação continua aberta: o vencimento não decide nada
  sozinho (`019`), e a lista continua levando à tela, que diz que o prazo informado passou.
- **Comunicação ainda não enviada.** A convocação já é indicada, e a tela diz que o prazo não começou.
- **Requerimento em rascunho e convocação desfechada antes do envio.** A política da `029` responde
  "ainda indisponível", e nenhum chamado aparece; o que a política decide não é reescrito aqui.
- **Edital que pede o requerimento na inscrição.** O cartão de "Sua inscrição" continua como está; a
  convocação acrescenta só o caminho de conferência.
- **Inscrição em rascunho.** Não há convocação de rascunho; a lista continua levando à inscrição.
- **Mais de uma convocação vigente na mesma inscrição.** Mostra-se a mais recente, pela mesma regra
  que a tela da convocação já usa.

## Requirements *(mandatory)*

### Functional Requirements

**Em "Minhas inscrições"**

- **FR-1089**: Item de inscrição com convocação **em aberto** — vigente e sem desfecho, em qualquer
  dos estados de prazo — MUST dizer, por texto e por símbolo, que há convocação aberta.
- **FR-1090**: A ação principal desse item MUST ser "Ver convocação", levando à tela da convocação da
  inscrição. O item continua com **uma** ação principal; o acompanhamento MUST continuar alcançável a
  partir dele, como ação secundária.
- **FR-1091**: Item com convocação **concluída** MUST dizer, em texto discreto, a situação registrada
  — a espécie do desfecho —, e a ação principal dele MUST continuar "Acompanhar". Item sem convocação
  MUST ficar como está hoje.
- **FR-1092**: O custo de leitura da lista MUST NOT crescer com o número de inscrições, e a lista MUST
  NOT ler as tabelas do Requerimento de Matrícula — o zero que a `029` prende para esta tela continua
  zero.

**No acompanhamento**

- **FR-1093**: Inscrição com convocação vigente — aberta ou concluída — MUST ter, no acompanhamento,
  uma seção "Convocação" com a espécie, o prazo quando houver, a situação e o caminho "Ver
  convocação".
- **FR-1094**: A situação MUST distinguir quatro casos, nos termos que a tela da convocação já usa:
  comunicação ainda não enviada; prazo correndo; prazo informado decorrido sem registro; desfecho
  registrado, com a espécie dele.
- **FR-1095**: Inscrição sem convocação vigente MUST NOT ter seção de convocação no acompanhamento.

**O Requerimento de Matrícula**

- **FR-1096**: Quando o Edital pede o requerimento e ele está **disponível** ou **em preenchimento**,
  a tela da convocação e a seção "Convocação" do acompanhamento MUST oferecer "Preencher Requerimento
  de Matrícula" como ação principal, levando à tela do requerimento da inscrição.
- **FR-1097**: Quando o requerimento foi **enviado**, os mesmos dois lugares MUST oferecer o caminho
  para conferir o que foi enviado — com a convocação aberta ou concluída —, e MUST NOT oferecer o
  chamado para preencher.
- **FR-1098**: Quando o requerimento está **ainda indisponível** ou **não se aplica**, nenhum chamado
  ao requerimento MUST aparecer.
- **FR-1099**: O estado do requerimento MUST vir da mesma política que a tela do requerimento
  consulta. Nenhuma tela desta feature decide disponibilidade por conta própria.

**Uma regra de vigência só**

- **FR-1100**: Lista, acompanhamento e tela da convocação MUST apresentar a **mesma** convocação de
  uma inscrição, escolhida pela regra que a tela da convocação já usa: a vigente mais recente.

**Autorização e trilha**

- **FR-1101**: A lista e o acompanhamento MUST mostrar só convocações das inscrições da própria
  identidade. A convocação, o requerimento, o requerimento anterior e o acompanhamento de inscrição
  alheia MUST responder com a mesma recusa — status e corpo — que um identificador inexistente.
- **FR-1102**: Nenhum endereço desta feature MUST carregar dado pessoal; o único identificador é o da
  inscrição, como nas rotas que já existem.
- **FR-1103**: Mostrar a indicação na lista e a seção no acompanhamento MUST NOT registrar leitura na
  trilha nem mover prazo: a leitura registrada continua sendo a abertura da tela da convocação.

**A mensagem**

- **FR-1104**: O endereço da mensagem de convocação MUST continuar sendo "Minhas inscrições", que
  passa a mostrar a convocação; o texto da mensagem MUST NOT mudar.

**O corte**

- **FR-1105**: A feature MUST NOT criar rota, mudar tela da gestão, mudar regra de convocação, de
  prazo ou de requerimento, nem mudar o conteúdo da tela da convocação além de acrescentar o chamado
  ao requerimento.

### Requisitos de experiência

- **UX-145**: A indicação de convocação aberta MUST ser legível sem cor — texto e símbolo —, como a
  situação do item já é.
- **UX-146**: A 375 px, a indicação, "Ver convocação", o acompanhamento e o chamado ao requerimento
  MUST caber sem rolagem horizontal.
- **UX-147**: Nenhuma frase nova MUST dizer que a mensagem foi recebida, lida ou entregue, nem
  prometer a vaga ou a matrícula — as regras da `019` (`UX-039`, `FR-292c`) valem para os textos novos.

### Key Entities

- **Convocação vigente da inscrição**: a convocação mais recente que ninguém sucedeu. *Aberta* quando
  não tem desfecho; *concluída* quando tem.
- **Estado de leitura do requerimento**: os cinco estados da `029` (`FR-405`) — não aplicável, ainda
  indisponível, disponível, em preenchimento, enviado. Esta feature os lê; não os redefine.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-424**: Quem foi convocado chega à convocação a partir de "Minhas inscrições" em **1** clique
  (antes: só digitando o endereço).
- **SC-425**: Num Edital que pede o requerimento na convocação, quem foi convocado chega ao
  requerimento a partir de "Minhas inscrições" em **2** cliques (antes: nenhum caminho).
- **SC-426**: A lista custa o mesmo número de consultas com uma e com cinco inscrições convocadas, e
  **zero** consultas às tabelas do requerimento.
- **SC-427**: Em cada uma das cinco rotas — acompanhamento, convocação, requerimento, requerimento
  anterior e lista —, a pessoa não titular não vê nada da inscrição alheia, e a recusa é idêntica à
  de identificador inexistente.
- **SC-428**: A suíte (`make lint check test-pg`) fica verde, e o total vai para a `verificacao.md`.

### O que esta feature não cobre, deliberadamente

- A integração da Ajuda e do manual no sistema.
- O texto da mensagem de convocação, e o endereço de cada mensagem individual.
- Qualquer tela da gestão.
- Aviso ativo — mensagem nova, notificação — além do que o portal mostra quando a pessoa entra.

## Assumptions

- **Convocação é de inscrição enviada.** A seção e a indicação só se aplicam a inscrição enviada;
  rascunho não é convocado.
- **A tela da convocação continua aberta a quem não foi chamado**, com as duas ausências da `FR-294`.
  O que muda é que agora se chega a ela pelo portal quando há convocação.
- **"Minhas inscrições" é o destino canônico da mensagem**: ele serve às mensagens disparadas em lote
  pela `050`, que levam um endereço só para muitas pessoas, e não exige mudar a gestão, que monta o
  endereço.
- **A `050` declarou que o portal não muda.** Esta feature muda a navegação do portal, e não o que a
  convocação mostra; o registro fica no research.
