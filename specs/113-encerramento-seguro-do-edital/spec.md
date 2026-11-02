# Feature Specification: Encerramento seguro do Edital — encerrar confere o que torna a conclusão falsa, e diz o que continua

**Feature Branch**: `claude/a11-edital-encerramento-diagnostico-a392fa`, sobre a `main` em `f90835e6`

**Created**: 2026-11-01

**Status**: Draft. As regras foram decididas pelo usuário em 01/11/2026, ao aceitar as seis
recomendações do parecer (ver *Clarifications*). Não há autorização para implementar antes de o plan
e as tasks serem aprovados.

**Input**: achado A-11 da
[auditoria de prontidão de 31/10/2026](../../doc/auditoria-prontidao-arquitetural-e-operacional-2026-10-31.md)
e o [parecer de 01/11/2026](../../doc/parecer-a11-encerramento-do-edital-2026-11-01.md), que reproduz o
comportamento atual, traz a matriz de decisão e as contradições entre specs, domínio e tela.

> **Faixa de identificadores.** Esta spec abre em **FR-3528** e **SC-1067**. O teto foi medido em
> 01/11/2026 em `specs/` de todas as worktrees desta máquina e no PR aberto da `112`: o requisito
> funcional três mil quinhentos e vinte e sete, e o critério mil e sessenta e seis. **Nenhum `UX-` é
> aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-2524 da `099`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

**Encerrar o Edital não confere nada.** O ato exige só que o Edital esteja publicado. Em 01/11/2026 um
mesmo Edital foi encerrado — e, noutro caso, cancelado — com recurso admitido sem julgamento,
convocação comunicada sem desfecho, inscrição em rascunho e Retificação homologada. A tela de
confirmação não listou nada e ofereceu "Confirmar". Depois do ato, julgar o recurso e registrar o
aceite da convocação continuaram aceitos, e a Retificação homologada ficou presa: desde o A-09 ela não
se publica, não se devolve e não se cancela.

**A tela afirma o que o ato não garante.** A primeira consequência anunciada é "o Edital passa a
Encerrado, registrando a conclusão regular de suas etapas". A FR-006 da `001` define Encerrado como
"conclusão regular após o término das etapas", mas nenhuma etapa é conferida. A `099` já decidiu que
"encerramento" não diz "concluído", e o relatório dela chama de *acompanhamento* o Edital encerrado com
providência pendente.

**Quem encerra não vê o que está pendente.** O gestor, que detém a permissão de encerrar, não tem no
detalhe do Edital a contagem de recursos aguardando decisão: ela só aparece para quem julga.

### O que esta spec cobre, e o que fica fora

Cobre: o que impede encerrar, o que só se adverte ao encerrar e ao cancelar, a tela de confirmação dos
dois atos, a coerência sob concorrência, e como a Retificação parada de Edital em estado final é
exibida.

Fica fora:

- **o que se pode praticar depois do encerramento.** Nenhum ato passa a ser recusado por causa do
  encerramento além dos que já são — o recebimento de inscrição e os atos da Retificação;
- **o encerramento do Processo.** O que ele impede é incoerente — convocação sim, julgamento e
  publicação de resultado não (parecer, C-7) —, e isso é registro, não escopo;
- **o efeito jurídico do cancelamento** sobre recurso e convocação pendentes (ver *Pendências do
  usuário*);
- **reabrir o A-09.** Edital em estado final continua sem Retificação de qualquer espécie.

## Clarifications

### Session 2026-11-01

As seis decisões foram propostas na §9 do parecer e aceitas pelo usuário como estão.

- Q: Recurso aguardando decisão, e reavaliação ou providência de recurso pendente, impedem encerrar?
  → A: Sim.
- Q: Janela recursal aberta impede encerrar? → A: Sim. O caso-limite da `047` "encerrado com prazo
  recursal em curso" deixa de nascer por encerramento.
- Q: Período de inscrições aberto ou por abrir impede encerrar? → A: Sim. O caminho é retificar o
  período ou cancelar.
- Q: Retificação homologada impede encerrar, e só adverte no cancelamento? → A: Sim, nos dois. Em
  elaboração e em revisão, só advertência.
- Q: Convocação sem desfecho e resultado definitivo não publicado só advertem? → A: Sim.
- Q: No cancelamento, o que acontece com recurso pendente e com convocado sem desfecho? → A: Fica como
  hoje — tudo continua operável — e o ato só adverte, até a decisão institucional.
- Q: Prazo de recurso não declarado e período de inscrições sem término declarado impedem encerrar?
  → A: Não; só advertem (D-002 e D-008). Acrescentadas pela spec e confirmadas pelo usuário em
  01/11/2026.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem encerra é impedido quando a conclusão ainda não aconteceu, e sabe o que fazer (Priority: P1)

O gestor abre "Encerrar" num Edital com recurso aguardando decisão. A tela diz que há uma pendência que
impede o ato, quantas peças aguardam, e oferece o caminho até os recursos. Não há botão de confirmar.
Julgado o recurso, ele volta, a tela diz que nada impede, e ele encerra.

**Why this priority**: é o defeito do A-11. Sem isto o Edital é dito concluído com obrigação pendente.

**Independent Test**: para cada impedimento da FR-3529 a FR-3533, montar um Edital publicado só com ele,
tentar encerrar pela tela e pelo serviço, e conferir a recusa, a lista e que nada mudou; resolver o
impedimento e conferir que o encerramento é aceito.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com um recurso admitido e sem decisão, **When** o gestor abre a
   confirmação de encerrar, **Then** a tela mostra "1 recurso aguarda decisão" como impedimento, com o
   caminho até os recursos ou a quem pedir, e não oferece confirmar.
2. **Given** o mesmo Edital, **When** o encerramento é pedido diretamente ao serviço, **Then** ele é
   recusado como conflito, com a mesma lista, e o Edital continua publicado, sem ato administrativo nem
   registro de auditoria novos.
3. **Given** o período de inscrições ainda em curso, com término declarado, **When** o gestor abre a confirmação, **Then** a
   tela diz até quando o período vai e que encerrar antes disso não é conclusão regular: altere o período
   por Retificação ou cancele o Edital.
4. **Given** uma Retificação homologada e não publicada, **When** o gestor abre a confirmação, **Then**
   a tela a identifica pela data de criação e pede que seja publicada ou devolvida antes, com o caminho
   até ela.
5. **Given** um resultado publicado cujo prazo de recurso declarado ainda corre, **When** o gestor abre a
   confirmação, **Then** a tela diz o marco e até quando vai o prazo.
6. **Given** todos os impedimentos resolvidos, **When** o gestor confirma com motivo, **Then** o Edital
   passa a Encerrado.

---

### User Story 2 — Quem encerra sabe o que continua depois do ato (Priority: P1)

O gestor encerra um Edital com uma convocação aguardando resposta. A tela não impede, mas diz, à parte
dos impedimentos, que uma convocação aguarda resposta até tal data e que o desfecho continua podendo ser
registrado. O relatório do Edital, emitido depois, diz a mesma coisa como providência.

**Why this priority**: a `099` tem esse estado como normal; o que faltava era a ciência no momento do ato.

**Independent Test**: montar um Edital com cada situação da FR-3534, abrir a confirmação, conferir a
advertência e o botão de confirmar; encerrar e conferir que o relatório da `099` lista a mesma
providência.

**Acceptance Scenarios**:

1. **Given** uma convocação comunicada com prazo em curso, **When** o gestor abre a confirmação,
   **Then** a tela diz "1 convocação aguarda resposta até DD/MM" entre as situações que continuam, e
   oferece confirmar.
2. **Given** o Edital encerrado com essa convocação, **When** o desfecho é registrado no dia seguinte,
   **Then** ele é aceito, como hoje.
3. **Given** nenhuma pendência nem advertência, **When** o gestor abre a confirmação, **Then** a tela diz
   "Nenhuma pendência registrada no GPS impede o encerramento" e não afirma que a seleção foi concluída.

---

### User Story 3 — Cancelar continua sempre possível, e diz o que será atingido (Priority: P2)

O gestor precisa interromper um Edital com inscrições abertas e um recurso pendente. A tela de
cancelamento lista o que será atingido — inscrições em preenchimento que não poderão ser enviadas,
recurso aguardando decisão, Retificação homologada que não será publicada — e deixa confirmar.

**Why this priority**: o cancelamento existe para quando o fluxo regular não pode terminar; impedi-lo
por pendência inverteria o ato.

**Independent Test**: montar um Edital com todas as situações juntas e cancelar pela tela e pelo
serviço; conferir que o ato é aceito e que a tela listou cada situação.

**Acceptance Scenarios**:

1. **Given** um Edital com todos os impedimentos do encerramento, **When** o gestor cancela com motivo,
   **Then** o ato é aceito.
2. **Given** o mesmo Edital, **When** o gestor abre a confirmação de cancelar, **Then** cada situação
   aparece sob "Serão atingidos pelo cancelamento", e nenhuma como impedimento.

---

### User Story 4 — A Retificação parada de um Edital encerrado não anuncia um próximo passo (Priority: P3)

Um Edital foi encerrado com uma Retificação em elaboração. Na seção "Retificações em curso", ela aparece
como "não pode mais prosseguir: o Edital foi encerrado", sem próximo responsável e sem ato oferecido.

**Why this priority**: hoje a seção anuncia um responsável que nada pode fazer.

**Independent Test**: encerrar e cancelar um Edital com Retificação em elaboração e em revisão; conferir
a frase e a ausência de responsável e de ato.

**Acceptance Scenarios**:

1. **Given** um Edital encerrado com Retificação em revisão, **When** alguém abre o detalhe do Edital,
   **Then** a Retificação aparece com "não pode mais prosseguir: o Edital foi encerrado", sem próximo
   responsável.
2. **Given** um Edital cancelado na mesma situação, **Then** a frase diz "cancelado".

---

### Edge Cases

- **Edital sem período de inscrições designado.** Não há período a terminar; não impede.
- **Período de inscrições cancelado por Retificação.** Conta como encerrado; não impede.
- **Período aberto sem término declarado.** A publicação o admite, e ele recebe inscrição para sempre:
  impedir tornaria o encerramento impossível. É advertência, e encerrar é o ato que põe fim ao
  recebimento (decisão D-008).
- **Período prorrogado por Retificação.** Vale o período da versão vigente no instante do ato.
- **Retificação homologada com vigência futura.** Impede como qualquer homologada: publicá-la é o
  caminho, e a vigência não muda isso.
- **Várias Retificações em curso.** Cada homologada é um impedimento, identificada pela data de criação; as em elaboração
  ou revisão aparecem juntas numa advertência.
- **Marco que não admite recurso.** Não abre janela; não impede.
- **Prazo de recurso não declarado.** A interposição fica aceita sem prazo, e por isso não é janela
  aberta: impedir por ela tornaria o encerramento impossível para sempre. É advertência (FR-3534).
- **Prazo de recurso declarado e não computável** (sem duração). Tratado como não declarado.
- **Recurso não admitido.** Está decidido; não impede.
- **Recurso admitido julgado com reavaliação determinada.** O recurso deixa de impedir; a reavaliação
  pendente passa a impedir até ser concluída.
- **Recurso interposto, admitido ou publicação de resultado entre a abertura da tela e o confirmar.** O
  ato confere no instante em que é praticado e recusa com a lista atual (FR-3543).
- **Rascunho com o período já encerrado.** Não é pendência e não aparece (decisão D-007).
- **Ator que encerra sem permissão de julgar recursos.** Vê a contagem e "peça a quem julga recursos";
  não recebe caminho que a tela de destino recusaria.
- **Repetição do mesmo pedido de encerramento já concluído.** Devolve o ato, como hoje.
- **Edital ainda não publicado.** Encerrar continua indisponível pela situação; cancelar segue como hoje,
  e nenhuma das situações desta spec existe antes da publicação.

## Requirements *(mandatory)*

### Functional Requirements

#### O que impede encerrar

- **FR-3528**: Encerrar o Edital MUST ser recusado, como conflito, quando houver ao menos um impedimento
  das FR-3529 a FR-3533 no instante do ato. A recusa MUST listar cada impedimento com a frase e a ação
  que o resolve, e MUST NOT gravar ato, auditoria nem mudança de situação. Vale para a tela e para o
  serviço.
- **FR-3529**: É impedimento o período de inscrições da versão vigente estar **aberto com término
  declarado** ou **por abrir**. Período não designado, encerrado, cancelado, ou aberto **sem término
  declarado** MUST NOT impedir; o último é advertência (FR-3534).
- **FR-3530**: É impedimento haver resultado publicado e vigente cujo prazo de recurso, **declarado e
  computável** pelo Edital, ainda não terminou — o mesmo prazo que a interposição aplica. Prazo não
  declarado, não computável, ou marco que não admite recurso MUST NOT impedir.
- **FR-3531**: É impedimento haver recurso aguardando admissibilidade ou, admitido, aguardando julgamento
  — a mesma definição da contagem "Recursos aguardando decisão" da gestão.
- **FR-3532**: É impedimento haver reavaliação determinada por recurso ainda não concluída, ou providência
  pendente de marco — as mesmas da FR-2524 da `099`.
- **FR-3533**: É impedimento haver Retificação homologada e não publicada.

#### O que só se adverte

- **FR-3534**: MUST ser exibidas como advertência, sem impedir, ao encerrar e ao cancelar: convocação sem
  desfecho com prazo em curso, com a data mais distante; convocação sem desfecho com prazo vencido;
  marco sem resultado divulgado; marco sem resultado definitivo vigente; apuração desatualizada;
  Retificação em elaboração ou em revisão, identificada pela data de criação, como na seção da `103`;
  resultado publicado sem prazo de recurso declarado, dizendo que recursos continuam podendo ser
  interpostos; e período de inscrições aberto sem término declarado, dizendo que o encerramento põe
  fim ao recebimento.
- **FR-3535**: As advertências de convocação, resultado e apuração MUST vir da mesma regra que produz as
  providências do relatório da `099` (FR-2524 da `099`), e não de uma segunda definição: toda providência
  que o relatório listar logo depois do ato MUST ter sido exibida na confirmação.

#### Cancelar

- **FR-3536**: Cancelar o Edital MUST NOT ser recusado por nenhuma situação desta spec. A confirmação MUST
  exibir, sob "Serão atingidos pelo cancelamento", as situações das FR-3529 a FR-3534 presentes, e também
  as inscrições em preenchimento quando o período estiver aberto, com a frase de que não poderão ser
  enviadas.

#### A confirmação

- **FR-3537**: Na confirmação de encerrar, os impedimentos MUST aparecer antes das consequências, cada um
  com contagem ou identificação, a frase e a ação que o resolve; havendo ao menos um, a confirmação MUST
  NOT ser oferecida.
- **FR-3538**: O caminho até a tela que resolve cada situação MUST ser oferecido só a quem essa tela
  aceita; a quem ela recusaria, a frase MUST dizer a quem pedir.
- **FR-3539**: As advertências MUST aparecer à parte dos impedimentos, como o que continua depois do ato.
- **FR-3540**: A confirmação MUST NOT exibir dado pessoal de candidato — nome, CPF, e-mail ou protocolo.
  Diz contagens do Edital, o nome publicado do marco e a data de criação da Retificação.
- **FR-3541**: Sem impedimento nem advertência, a confirmação de encerrar MUST dizer "Nenhuma pendência
  registrada no GPS impede o encerramento", e MUST NOT dizer que a seleção foi concluída.
- **FR-3542**: As consequências anunciadas do encerramento MUST NOT afirmar a conclusão regular das
  etapas. MUST dizer que o Edital deixa de receber inscrição e Retificação, e que o que aparece como
  advertência continua possível e consta do relatório do Edital.
- **FR-3543**: A conferência MUST valer no instante em que o ato é praticado, e não no da abertura da
  tela: um impedimento criado por ato confirmado antes, ainda que concorrente, MUST levar à recusa; e um
  ato que criaria impedimento, confirmado depois do encerramento, segue as regras que já valem para
  Edital encerrado. A recusa MUST reexibir a confirmação com a lista atual.

#### A Retificação parada

- **FR-3544**: Na seção "Retificações em curso", a Retificação em elaboração, em revisão ou homologada de
  Edital encerrado ou cancelado MUST ser dita "não pode mais prosseguir: o Edital foi encerrado" (ou
  "cancelado"), sem próximo responsável e sem ato oferecido.

#### O que não muda

- **FR-3545**: Esta spec MUST NOT tornar recusado nenhum ato posterior ao encerramento ou ao cancelamento
  que hoje é aceito, MUST NOT permitir ato de Retificação em Edital em estado final, e MUST NOT alterar
  as regras de encerramento e cancelamento do Processo.

### Key Entities

- **Situação pendente do Edital**: fato derivado, no instante do ato, de recursos, publicações de
  resultado, convocações, apurações, Retificações e do período de inscrições vigente. Tem espécie
  (impedimento ou advertência), contagem ou identificação, a frase e a ação que a resolve. Não é gravada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1067**: Cada um dos cinco impedimentos, presente sozinho, leva à recusa do encerramento em 100%
  dos casos de teste, pela tela e pelo serviço, sem nenhuma mudança de situação, ato ou auditoria.
- **SC-1068**: Um Edital com todos os impedimentos e todas as advertências juntos é cancelado em 100% dos
  casos de teste.
- **SC-1069**: Em 100% dos cenários de teste, toda providência listada pelo relatório do Edital emitido
  logo depois do encerramento foi exibida antes na confirmação.
- **SC-1070**: Com recurso interposto, recurso admitido ou resultado publicado em paralelo ao
  encerramento, nenhum Edital termina encerrado com impedimento confirmado antes dele, em repetidas
  execuções concorrentes.
- **SC-1071**: Quem encerra sem permissão de julgar vê o número de recursos aguardando decisão; nenhuma
  tela desta feature exibe nome, CPF, e-mail ou protocolo de candidato.
- **SC-1072**: A confirmação de encerrar de um Edital com 400 inscrições abre em menos de 1 segundo.

## Assumptions

- O ato de encerrar continua o mesmo — permissão, motivo, idempotência, auditoria —, e só ganha a
  conferência.
- "Por abrir" é o período designado cujo início ainda não chegou. Encerrar nesse caso é desistir antes de
  começar, e o ato próprio é o cancelamento.
- A reprodução e as contagens do parecer valem para a `main` em `f90835e6`.
- Os casos de teste que hoje chegam a "encerrado com período em curso", "encerrado com período por abrir"
  e "encerrado com prazo recursal em curso" (`047`) passam a chegar ao estado por outro caminho; a regra
  de exibição da `047` para esses estados continua necessária para dados anteriores.

## Proteção de dados (LGPD)

Avaliação exigida pelo princípio III da Constituição.

- **Dado tratado.** Nenhum dado pessoal novo é coletado, gravado ou derivado. A conferência lê
  recursos, convocações, inscrições e Retificações que já existem, e só para contar.
- **Necessidade e minimização.** A confirmação mostra contagens do Edital, o nome publicado do marco,
  datas de prazo e a data de criação da Retificação (FR-3540). Recurso e convocação são fato não
  público: nunca aparecem por pessoa, e as advertências que vêm do relatório respeitam a omissão de
  detalhe por Perfil da `099`.
- **Finalidade e acesso.** A tela é de quem detém `edital:encerrar` ou `edital:cancelar`; quem quer
  saber *quem* segue o caminho até a tela dona, sob a permissão dela (FR-3538).
- **Registros.** A recusa não grava auditoria nem ato, e a mensagem dela não cita pessoa; o registro de
  recusa de domínio que já existe continua sem conteúdo pessoal.
- **Retenção.** Nada novo é guardado, e por isso nada novo a reter ou descartar.

## Decisões

### D-001 — Encerrar impede; cancelar só adverte

Encerrado é conclusão regular (FR-006 da `001`); Cancelado é interrupção. Pendência que torna a conclusão
falsa impede o primeiro. No segundo, impedir inverteria o ato: ele existe justamente para quando o fluxo
não pode terminar. Decisão do usuário de 01/11/2026.

### D-002 — Só o prazo de recurso declarado e computável impede

Sem prazo declarado a interposição é aceita para sempre (o sistema não inventa prazo). Impedir por isso
tornaria o encerramento impossível; adverte-se que recursos continuam possíveis.

### D-003 — A Retificação homologada impede; as outras advertem

Mudança aprovada e não publicada contradiz a conclusão regular, e o A-09 a deixaria presa sem saída.
Cancelá-la automaticamente feriria a regra de que nenhum ato propaga desfecho; permitir cancelá-la depois
do encerramento reabriria o A-09. Em elaboração e em revisão é trabalho não aprovado: adverte-se.

### D-004 — As advertências são as providências da `099`

Uma regra, duas leituras: o que a confirmação adverte é o que o relatório dirá depois. Uma lista própria
da confirmação divergiria na primeira mudança.

### D-005 — A conferência é serializada pelo Processo

Recurso, convocação e publicação de resultado já se serializam na linha do Processo; a Retificação, na do
Edital; o envio de inscrição espera pela do Edital. O encerramento passa a travar o Processo antes do
Edital — a ordem que o encerramento do Processo já usa — e confere os impedimentos depois das duas
travas. Nenhuma trava em tabela nova.

### D-006 — Contagens do Edital, sem pessoa

Recurso e convocação são fato não público. A confirmação diz quantos, e a tela dona — com a permissão
dela — diz quem.

### D-007 — Rascunho com o período encerrado não é pendência

É abandono do candidato, e já não podia ser enviado. Com o período aberto, o rascunho é coberto pelo
impedimento do período, e no cancelamento vira advertência.

### D-008 — Período sem término declarado não impede

A publicação admite o Evento de inscrição sem término, e a régua do recebimento o lê como aberto para
sempre. Pela mesma razão da D-002, impedir tornaria o encerramento impossível; o Edital que não fixou
prazo tem no encerramento o ato que põe fim ao recebimento, e a confirmação adverte isso.

## Pendências do usuário


- **Efeito do cancelamento** sobre recurso pendente e convocado sem desfecho: decisão institucional e
  jurídica. Até ela, tudo continua operável e o ato só adverte.
- **O que o encerramento do Processo impede** (parecer, C-7): registro, fora desta spec.
