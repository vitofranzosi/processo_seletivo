# Feature Specification: O agendamento dos participantes da Etapa

**Feature Branch**: `claude/agendamento-etapa-gps-9bca12`, sobre a `main` em `37ed0ad0`

**Created**: 2026-11-14

**Status**: Especificada em 14/11/2026, a partir do estudo do mesmo dia, sem plan nem tasks. As três
perguntas ao usuário foram respondidas no mesmo dia (ver *Clarifications*). A experiência visual
espera a aprovação do protótipo pela comissão, que o estudo põe como marco anterior a qualquer
implementação.

**Input**: o pedido de 14/11/2026 para especificar o agendamento de participantes em Etapas que
exigem comparecimento em dia e horário — entrevista, verificação da autodeclaração, arguição —, como
capacidade transversal da Etapa, e não como módulo de entrevistas; o registro
`doc/registro-convocacao-para-etapas-2026-10-09.md`, que anotou a lacuna e as cinco perguntas dela; e
o estudo `doc/estudo-agendamento-da-etapa-2026-11-14/`, com diagnóstico, proposta (regras R-01 a
R-26 e modelo mínimo), protótipo navegável e plano de entregas.

> **Faixa de identificadores.** Esta spec abre em **FR-7100**, **SC-2370** e **UX-760**. Os tetos
> medidos em 14/11/2026 eram, na `main`, o requisito seis mil novecentos e cinquenta e um, o critério
> dois mil trezentos e quatro e o requisito de experiência setecentos e vinte e sete; nos PRs
> abertos (#542 a #545), o requisito sete mil e oitenta e três, o critério dois mil trezentos e
> cinquenta e seis e o requisito de experiência setecentos e cinquenta e quatro. A pasta `166`
> estava livre na `main`, nos PRs abertos e nas worktrees locais. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-084 da `010`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> **A `163`, a `164` e a `165` são citadas só pelo assunto.** Quando esta spec foi escrita, nenhuma
> estava na `main`; as três entraram no mesmo dia, depois dela (#542, #543, #545).

---

## Por que esta feature existe

O GPS sabe **quem** faz cada Etapa: a participação é uma projeção única, recalculada a cada leitura,
que segue a eliminação, a habilitação na Etapa anterior e o corte. Ele não sabe **quando** cada
pessoa é atendida. Não existe horário por pessoa, nem banca como lugar de atendimento, nem ato que
diga "compareça às 8h15". A Etapa aponta um Evento do cronograma, com uma data e um local, e é tudo.

Os Editais do Cefor tratam o horário como ato. No 28/2026, os autodeclarados pretos e pardos são
convocados "por meio de listagem divulgada", o endereço da sala vem "no ato da convocação", a
justificativa da ausência conta 24 horas do horário marcado, e a ausência indefere. No 146/2025, "as
datas, horários e o endereço da sala virtual serão divulgados conforme o cronograma", e quem falta é
desclassificado. Hoje a comissão monta essa escala numa planilha, publica fora do sistema, manda o
endereço da sala por e-mail um a um, e remarca do mesmo jeito.

A heteroidentificação está entrando no GPS como Etapa, pelas specs do alcance por Modalidade, do
efeito do desfecho por lista e das regras de deliberação. O estudo que as originou deixou de fora
"a agenda individual da entrevista ao vivo", porque ela "serve a qualquer entrevista, e não só a
esta". É esta spec.

**O princípio.** A Etapa diz quem participa. A agenda diz quando e onde cada pessoa é atendida. A
avaliação, o resultado e a ausência continuam onde estão.

### O que esta spec cobre, e o que fica fora

**Cobre:** configurar a agenda de uma Etapa e ver a capacidade; montar a agenda, automaticamente
com prévia e à mão; conferir e publicar; mostrar o horário na página pública e na área do
candidato; avisar cada pessoa por e-mail; e mudar a agenda publicada só por ato individual —
remarcação, inclusão e cancelamento.

**Fica fora:** autosserviço de escolha de horário pelo candidato; disponibilidade individual dos
avaliadores; calendário institucional; integração com Google ou Outlook; videoconferência
embutida; gravação; registro de presença na agenda; lembrete na véspera; publicação da agenda em
partes. Ver *Out of Scope*.

## Clarifications

### Session 2026-11-14 (decisões do usuário)

- Q: Que ato é a agenda publicada: a publicação formal, com a natureza da relação de convocados da
  `149` e o veículo escolhido como na `159` (A), ou uma publicação informativa, sem autoridade (B)?
  → A: **A** (`D-008`).
- Q: Na Etapa restrita por Modalidade, a página pública identifica a pessoa só pelo protocolo (A),
  ou pelo nome e protocolo, como as demais (B)? → A: **A**, só o protocolo (`D-009`).
- Q: A lista fechada da FR-084 da `010` é revista para incluir o aviso de agenda, como origem do aviso
  complementar e sem envio novo (A), ou a agenda fica sem e-mail (B)? → A: **A** (`D-010`).

---

## User Scenarios & Testing *(mandatory)*

Os atores são a **comissão** da Etapa — quem pode geri-la, e a presidência, que publica — e o
**candidato**, que lê a área dele, a página pública da seleção e o e-mail.

### User Story 1 — A comissão configura a agenda e vê se cabe todo mundo (Priority: P1)

Na página da Etapa, a seção "Agenda" está vazia e diz para que serve. A comissão escolhe
"Configurar a agenda": atendimento remoto ou presencial, duração e intervalo, os dias com uma ou
mais janelas, as bancas — cada uma com nome e local ou endereço da sala — e as orientações ao
candidato. Enquanto ela digita, um painel ao lado diz quantos horários há e se cabem as pessoas que
hoje participam da Etapa. A configuração pode ser feita antes de a lista de participantes fechar.

**Why this priority**: sem configuração não há horário; e a capacidade é a primeira pergunta da
comissão — "cabe?" — que hoje se responde com conta à mão.

**Independent Test**: numa Etapa com 43 participantes e período de 23 a 25/11 no cronograma,
configurar 23/11 com 08:00–12:00 e 13:00–17:00, 10 minutos com 5 de intervalo e uma banca mostra
32 horários e "faltam 11"; acrescentar 24/11 mostra 64 e "cabem as 43".

**Acceptance Scenarios**:

1. **Given** uma Etapa sem agenda, **When** a comissão abre a página da Etapa, **Then** a seção
   "Agenda" diz que a Etapa ainda não tem agenda, para que ela serve, e oferece "Configurar a
   agenda".
2. **Given** a configuração do teste independente, **When** a comissão a digita, **Then** o painel
   mostra 32 horários, "16 atendimentos por banca × 1 banca" por janela e por dia, e "faltam 11
   horários para as 43 pessoas", sem salvar nada.
3. **Given** duas bancas e uma janela de 08:00 a 12:00 com 20 minutos e 10 de intervalo, **When**
   a comissão digita, **Then** o painel mostra 16 horários, 8 por banca.
4. **Given** uma janela de 12:00 a 12:05 com 10 minutos de duração, **When** a comissão tenta
   salvar, **Then** a configuração é recusada com "A janela 12:00–12:05 não comporta um atendimento
   de 10 minutos. Amplie a janela ou reduza a duração."
5. **Given** um dia fora do período do Evento da Etapa no cronograma vigente, **When** a comissão
   tenta salvar, **Then** a configuração é recusada com o período publicado e a frase de que mudar o
   período pede Retificação.
6. **Given** duas janelas que se sobrepõem no mesmo dia, ou duas bancas com o mesmo nome, **When**
   a comissão tenta salvar, **Then** a configuração é recusada e a frase nomeia o par.
7. **Given** uma Etapa cuja Etapa anterior ainda não tem Resultado, **When** a comissão configura a
   agenda, **Then** a configuração é aceita, e a capacidade é comparada com quem participa naquele
   momento, com a frase de que a lista ainda pode mudar.

---

### User Story 2 — A comissão monta a agenda sem planilha (Priority: P1)

Na tela "Montar a agenda", um resumo só diz quantas pessoas já têm horário, quantos horários há e
quanto sobra ou falta. Uma aba por dia mostra a grade horário × banca, e ao lado fica o painel de
ação, que começa pela lista "Sem horário". A comissão pede "Preencher automaticamente", vê no painel a
prévia — quantas pessoas recebem horário, a distribuição por dia e banca, o que sobra e a ordem
usada — e aplica. Depois ajusta à mão: clica numa pessoa e escolhe, no painel, um horário livre de
qualquer dia; ou clica num horário livre e escolhe quem vai para ele; ou libera um horário.

**Why this priority**: é a escala que hoje vive na planilha. É o que o pedido mede: sair de uma
lista de 43 pessoas para uma agenda montada.

**Independent Test**: com a configuração de 64 horários e 43 participantes, o preenchimento dá
horário a todos na ordem por nome; agendar à mão uma pessoa às 08:15 de 24/11 antes de preencher a
mantém ali depois do preenchimento.

**Acceptance Scenarios**:

1. **Given** 43 participantes sem horário e 32 horários, **When** a comissão pede o preenchimento,
   **Then** a prévia diz que 32 pessoas receberão horário e 11 continuarão sem, lista os primeiros
   pares, diz a ordem, e nada é gravado.
2. **Given** a prévia aberta, **When** a comissão aplica, **Then** os 32 pares são gravados como
   "preenchidos automaticamente", e a tela diz quantas pessoas receberam horário.
3. **Given** uma pessoa já agendada à mão, **When** a comissão preenche, **Then** essa pessoa não
   muda de horário, e o horário dela não é dado a outra.
4. **Given** a prévia aberta, **When** outra sessão muda a agenda antes da aplicação, **Then** a
   aplicação é recusada com "a agenda mudou desde a prévia", e a prévia nova aparece.
5. **Given** uma pessoa escolhida na lista "Sem horário", **When** a comissão escolhe no painel um
   horário livre e confirma, **Then** a pessoa passa a ocupar o horário e sai da lista; e, partindo
   de um horário livre da grade, escolher a pessoa e "Agendar aqui" dá o mesmo resultado.
6. **Given** uma pessoa agendada, **When** a comissão a escolhe na grade, escolhe no painel um horário
   livre de outro dia e confirma "Mudar de horário", **Then** a pessoa passa ao horário novo e o
   anterior fica livre.
7. **Given** uma pessoa agendada, **When** a comissão escolhe "Liberar", **Then** o horário fica
   livre e a pessoa volta para "Pessoas sem horário".
8. **Given** duas pessoas da comissão escolhendo o mesmo horário livre ao mesmo tempo, **When** as
   duas confirmam, **Then** só a primeira ocupa, e a segunda recebe "Esse horário acabou de ser
   ocupado" com a grade atualizada.
9. **Given** uma configuração salva que remove uma janela com pessoas agendadas, ainda antes da
   publicação, **When** a montagem é aberta, **Then** essas pessoas estão em "Pessoas sem horário",
   e a tela diz quem voltou e por quê.

---

### User Story 3 — A comissão confere e publica, e cada pessoa vê o próprio horário (Priority: P1)

Na conferência — a mesma moldura da conferência antes de convocar —, a comissão vê o que impede a
publicação, com o caminho para resolver; o que será publicado; a prévia exata da página pública; a
mensagem que cada pessoa recebe; e escolhe a autoridade signatária. Ao confirmar, a agenda é
publicada como ato imutável; a página pública da seleção e a área de cada pessoa passam a mostrar o
horário.

**Why this priority**: a agenda só tem efeito quando publicada; e o horário que o candidato não
encontra é o que faz perder a entrevista.

**Independent Test**: com as 43 pessoas agendadas, publicar, abrir a página pública e encontrar o
horário de uma pessoa pelo número de inscrição; entrar na área dela e ver o dia, a hora, a banca, o
endereço da sala e as orientações.

**Acceptance Scenarios**:

1. **Given** 9 participantes sem horário, **When** a comissão abre a conferência, **Then** a
   publicação está impedida, a tela lista as 9 pessoas e oferece "Voltar à montagem".
2. **Given** uma pessoa agendada que deixou de participar da Etapa, **When** a comissão abre a
   conferência, **Then** a publicação está impedida e a tela nomeia a pessoa.
3. **Given** uma banca sem local ou endereço de sala, **When** a comissão abre a conferência,
   **Then** a publicação está impedida e a tela nomeia a banca.
4. **Given** a agenda completa, **When** a comissão abre a conferência, **Then** nada é gravado nem
   enviado, e a tela mostra os fatos (Etapa, período do cronograma, dias, duração, bancas, pessoas),
   a prévia pública, o assunto e o texto da mensagem, e a escolha da autoridade.
5. **Given** a conferência aberta, **When** a agenda muda noutra sessão e a comissão confirma,
   **Then** a publicação é recusada e a conferência é refeita.
6. **Given** a conferência aberta, **When** a comissão confirma duas vezes seguidas, **Then** nasce
   um só ato, e a segunda confirmação devolve o primeiro.
7. **Given** a agenda publicada, **When** qualquer pessoa abre a página pública da seleção, **Then**
   ela vê a agenda por dia, com horário, banca e a identificação definida pela FR-7125, e nunca o
   endereço da sala, o CPF, o e-mail ou o telefone.
8. **Given** a agenda publicada, **When** o candidato abre a área dele, **Then** vê o dia e a hora
   em destaque, a duração prevista, a banca, o local ou o botão da sala virtual, e as orientações.
9. **Given** a agenda ainda não publicada, **When** o candidato abre a área dele, **Then** lê que o
   horário ainda não foi publicado, e o período da Etapa no cronograma.

---

### User Story 4 — Cada pessoa recebe um aviso, e a falha não desfaz nada (Priority: P2)

Publicada a agenda, cada pessoa recebe um aviso por e-mail com o dia, a hora, a banca, o local ou a
sala e as orientações, na moldura dos e-mails do GPS. A tela da agenda publicada mostra quantos
avisos saíram, quantos estão na fila e quais não foram entregues, com "Reenviar o aviso".

**Why this priority**: o aviso é o que leva a pessoa até a publicação; mas o ato é a publicação, e
por isso o aviso vem depois dela e não a condiciona.

**Independent Test**: publicar a agenda de 43 pessoas, rodar o despacho dos avisos, e ver 43 avisos
de origem "agenda", um por pessoa, cada um citando a publicação.

**Acceptance Scenarios**:

1. **Given** a agenda publicada, **When** o despacho roda, **Then** cada pessoa da agenda recebe um
   aviso, e nenhuma recebe dois.
2. **Given** a publicação confirmada, **When** nenhum despacho rodou ainda, **Then** a tela diz que
   os avisos estão na fila, e a agenda já está pública.
3. **Given** um endereço recusado pelo servidor do destinatário, **When** a comissão abre a agenda
   publicada, **Then** a tela diz que a agenda vale para essa pessoa do mesmo jeito, nomeia a pessoa
   e oferece o reenvio.
4. **Given** uma Etapa remota, **When** o aviso é composto, **Then** ele traz o endereço da sala
   daquela pessoa, e só dela.

---

### User Story 5 — Depois de publicada, só se muda uma pessoa de cada vez (Priority: P2)

A conexão de uma pessoa falhou, e o Edital manda reagendar. A comissão abre "Remarcar" na linha
dela, escolhe um horário livre e escreve o motivo. Só aquela pessoa muda e só ela é avisada; a
página pública mostra o horário novo com "remarcado em"; o anterior fica no histórico. Quem passou a
participar depois da publicação — um recurso deferido — aparece em destaque, e é agendado do mesmo
jeito. Quem estava agendado e deixou de participar tem o agendamento cancelado, com motivo.

**Why this priority**: remarcar é o trabalho que se repete depois da publicação; republicar a
agenda inteira para mudar uma pessoa avisaria todo mundo de novo.

**Independent Test**: com a agenda publicada, remarcar uma pessoa de 23/11 09:30 para 24/11 14:00
com o motivo "falha de conexão comprovada"; ver um aviso só, para ela; ver na página pública o
horário novo com a marca; ver na trilha o horário anterior, o novo, o autor e o motivo.

**Acceptance Scenarios**:

1. **Given** a agenda publicada, **When** a comissão abre a montagem, **Then** não há preenchimento
   automático nem "Liberar" sobre horário publicado; cada linha oferece "Remarcar".
2. **Given** a remarcação aberta sem motivo, **When** a comissão confirma, **Then** a remarcação é
   recusada com a frase de que o motivo fica na trilha e não aparece ao candidato.
3. **Given** a remarcação confirmada, **When** a página pública é aberta, **Then** a pessoa aparece
   no horário novo, com "remarcado em" e a data, e o horário anterior está livre.
4. **Given** a remarcação confirmada, **When** o despacho roda, **Then** só a pessoa remarcada recebe
   aviso, e o aviso diz que o horário anterior não vale mais.
5. **Given** uma pessoa que passou a participar depois da publicação, **When** a comissão abre a
   agenda publicada, **Then** a pessoa aparece em "Passou a participar depois da publicação", com
   "Agendar esta pessoa".
6. **Given** uma pessoa agendada que deixou de participar, **When** a comissão cancela o
   agendamento com motivo, **Then** a pessoa sai da agenda vigente na página pública, o publicado
   antes continua no histórico, e o horário fica livre.
7. **Given** duas pessoas da comissão remarcando para o mesmo horário ao mesmo tempo, **When** as duas
   confirmam, **Then** só a primeira remarcação vale, e a segunda é recusada com a lista atualizada.
8. **Given** a agenda publicada sem horário livre, **When** a comissão abre a remarcação, **Then** a
   tela diz que não há horário livre e leva à configuração, onde só se pode acrescentar dia, janela
   ou banca.

---

### Edge Cases

- **A lista muda entre a montagem e a publicação.** Um recurso deferido acrescenta uma pessoa; uma
  eliminação tira outra. A montagem mostra a primeira em "Pessoas sem horário" e sinaliza a segunda
  na grade; a conferência impede a publicação até as duas serem resolvidas (FR-7121).
- **O Evento da Etapa é retificado depois da configuração**, e um dia da agenda fica fora do período.
  A montagem avisa; a conferência impede (FR-7121); publicada a agenda, o horário publicado continua
  valendo como foi publicado, e a gestão é avisada de que ele está fora do período vigente.
- **Agenda parcialmente preenchida.** Pode ser salva e reaberta quantas vezes for preciso; só a
  publicação exige todos.
- **Capacidade sobrando.** Não é aviso: os horários livres aparecem como livres, e servem a
  remarcações e inclusões depois.
- **Uma pessoa com duas inscrições na mesma Etapa** (dois Perfis do mesmo Edital) recebe dois
  horários, um por inscrição, porque a participação é por inscrição. A tela não as junta.
- **Etapa sem Evento no cronograma.** A configuração não tem período para conferir os dias; ela é
  aceita, e a conferência mostra, como aviso, que a Etapa não tem período publicado.
- **Atendimento presencial com local em várias salas.** Cada sala é uma banca.
- **A pessoa sem endereço de e-mail válido.** A agenda vale para ela pela publicação; o aviso falha
  como qualquer outro, e a tela o mostra.
- **Publicação repetida.** Devolve o mesmo ato e não gera aviso novo (FR-7123).
- **Uma Etapa sem agenda.** Nada muda para ela: o agendamento é opcional por Etapa.

---

## Requirements *(mandatory)*

### Functional Requirements

#### A agenda e a configuração

- **FR-7100**: Uma Etapa de avaliação MAY ter uma agenda, e no máximo uma. A agenda MUST ser
  operacional: configurá-la, montá-la ou publicá-la MUST NOT alterar o Edital, a Etapa, o cronograma
  ou pedir Retificação.
- **FR-7101**: A agenda MUST se referir à Etapa pela identidade dela no Edital, e continuar válida
  para Etapa acrescentada por Retificação.
- **FR-7102**: A configuração MUST ter: a forma de atendimento (remota ou presencial); a duração de
  cada atendimento e o intervalo entre atendimentos, em minutos; um ou mais dias, cada um com uma ou
  mais janelas de início e fim; uma ou mais bancas, cada uma com nome e local (presencial) ou
  endereço da sala (remota); e orientações ao candidato.
- **FR-7103**: Os horários MUST ser derivados da configuração, e não digitados: em cada janela, o
  primeiro atendimento começa no início; cada seguinte começa depois da duração mais o intervalo; o
  último termina até o fim da janela. Cada horário existe uma vez em cada banca.
- **FR-7104**: A configuração MUST ser recusada, com frase que diz o que mudar, quando: um dia
  estiver fora do período do Evento da Etapa no cronograma vigente; uma janela terminar antes de
  começar; uma janela for menor que a duração; duas janelas do mesmo dia se sobrepuserem; uma banca
  não tiver nome; duas bancas tiverem o mesmo nome; a duração não for positiva; o intervalo for
  negativo.
- **FR-7105**: A capacidade MUST ser o número de horários vezes o número de bancas, e MUST ser
  comparada com o número de pessoas que participam da Etapa naquele momento. A insuficiência MUST
  ser dita com o número que falta, e MUST NOT impedir salvar a configuração.
- **FR-7106**: A sobra no fim de uma janela que não comporta outro atendimento MUST ser informada,
  e MUST NOT ser tratada como erro.
- **FR-7107**: A configuração MUST poder ser salva antes de a participação da Etapa estar definida.
- **FR-7108**: Antes da publicação, mudar a configuração MUST devolver a "sem horário" quem estava
  num horário que deixou de existir, e MUST dizer quem foi devolvido. Depois da publicação, a
  configuração MUST só aceitar acrescentar dia, janela ou banca, e MUST recusar mudança que remova ou
  mova um horário publicado.

#### A montagem

- **FR-7110**: Quem precisa de horário MUST ser quem participa da Etapa pela regra de participação
  vigente, lida a cada abertura da agenda. A agenda MUST NOT manter lista própria de participantes.
- **FR-7111**: Uma inscrição MUST ter no máximo um horário na agenda, e um horário de uma banca MUST
  ter no máximo uma inscrição. As duas regras MUST valer sob operações simultâneas.
- **FR-7112**: A comissão MUST poder agendar uma pessoa sem horário num horário livre, mudar uma
  pessoa de horário e liberar um horário, antes da publicação.
- **FR-7113**: O preenchimento automático MUST alocar só pessoas sem horário, só em horários livres,
  sem mexer em quem já tem horário, na ordem: pessoas pelo nome, e pelo protocolo no empate;
  horários do mais cedo ao mais tarde; com mais de uma banca, as bancas lado a lado em cada horário.
- **FR-7114**: O preenchimento MUST mostrar uma prévia sem gravar nada — quantas pessoas receberão
  horário, quantas continuarão sem, os pares e a ordem — e MUST gravar só na aplicação.
- **FR-7115**: A aplicação MUST ser recusada quando a agenda tiver mudado desde a prévia, e MUST
  mostrar a prévia nova.
- **FR-7116**: Cada agendamento MUST registrar a origem (à mão ou automático), quem o fez e quando.
- **FR-7117**: A montagem MUST mostrar, separados, quem participa e não tem horário, e quem tem
  horário e não participa mais.

#### A conferência e a publicação

- **FR-7120**: A conferência MUST NOT gravar, enviar ou reservar nada.
- **FR-7121**: A publicação MUST ser impedida quando houver: pessoa que participa sem horário;
  pessoa agendada que não participa mais; configuração que a FR-7104 recusaria, relida contra o
  cronograma vigente; banca sem local ou endereço; nenhuma autoridade signatária vigente. Cada
  impedimento MUST nomear o que está errado e levar ao lugar de corrigir.
- **FR-7122**: A conferência MUST mostrar os fatos da publicação (Etapa, período do cronograma,
  dias, duração e intervalo, bancas, forma de atendimento, pessoas e horários), a prévia da página
  pública, o assunto e o texto da mensagem, e a escolha da autoridade signatária.
- **FR-7123**: A confirmação MUST levar a assinatura do que foi conferido (configuração e pares
  pessoa-horário) e MUST ser recusada se a agenda mudou desde a conferência. A confirmação repetida
  MUST devolver o ato já criado, sem criar outro e sem aviso novo.
- **FR-7124**: A publicação MUST ser um ato imutável, que registra autor, autoridade signatária,
  instante, e o conteúdo público tal como foi publicado, com o seu resumo criptográfico. Ela MUST
  ter a mesma natureza da relação de convocados da `149`, e o veículo MUST ser escolhido na
  confirmação como na `159`: publicar no GPS, declarando onde o Edital admite a página pública como
  veículo, ou registrar depois a publicação feita fora dele (`D-008`).
- **FR-7125**: O conteúdo público MUST ter, por pessoa: o dia, o horário, o nome da banca quando há
  mais de uma, e a identificação da pessoa. A identificação MUST ser o nome e o protocolo, como a
  FR-5712 da `149`, salvo na Etapa cujo alcance é restrito por Modalidade, em que a identificação
  MUST ser só o protocolo (`D-009`). Na área do candidato, identificado, nada muda: ele vê tudo o que
  é dele.
- **FR-7126**: O conteúdo público MUST NOT conter o endereço da sala, o CPF inteiro ou parcial, o
  e-mail, o telefone, a Modalidade ou o desfecho de Etapa alguma.
- **FR-7127**: A página pública da seleção MUST mostrar a agenda publicada por dia, e MUST permitir
  encontrar um horário pelo protocolo, e também pelo nome quando o nome é público.
- **FR-7128**: A área do candidato MUST mostrar, na inscrição agendada: o dia e a hora em destaque,
  a duração prevista, a banca, o local ou o acesso à sala virtual, e as orientações. Antes da
  publicação, MUST dizer que o horário ainda não foi publicado e o período da Etapa no cronograma.
- **FR-7129**: O endereço da sala virtual MUST chegar só à própria pessoa: na área dela, depois de
  identificada, e no aviso dela.

#### Os avisos

- **FR-7130**: A publicação MUST criar um aviso por pessoa publicada, que cita o ato, pela origem
  "agenda" dos avisos complementares; a confirmação MUST NOT enviar, e o envio MUST ser o do
  despacho de avisos. A lista fechada da FR-084 da `010` MUST ser revista para incluir o aviso de
  agenda — na publicação, na remarcação e na inclusão — como origem do aviso complementar, sem envio
  novo (`D-010`).
- **FR-7131**: O aviso MUST trazer o dia, a hora, a duração prevista, a banca quando há mais de uma,
  o local ou o endereço da sala, as orientações, o protocolo, e a frase de que o que vale é a agenda
  publicada.
- **FR-7132**: Uma pessoa MUST NOT receber dois avisos do mesmo ato.
- **FR-7133**: A falha de envio MUST NOT desfazer nem suspender o ato. A tela da agenda publicada
  MUST mostrar quantos avisos saíram, quantos estão na fila e quais falharam, com o reenvio dos
  avisos complementares.

#### Depois da publicação

- **FR-7140**: Publicada a agenda, toda mudança MUST ser ato individual, sobre uma pessoa, com
  motivo; o preenchimento automático e a liberação de horário publicado MUST NOT estar disponíveis.
- **FR-7141**: A remarcação MUST levar a pessoa a um horário livre, MUST exigir motivo, e MUST
  registrar o horário anterior, o novo, o autor, o instante e o motivo. O registro anterior MUST
  continuar existindo.
- **FR-7142**: A inclusão MUST agendar, num horário livre e com motivo, quem passou a participar da
  Etapa depois da publicação, pelo mesmo ato da remarcação, sem horário anterior.
- **FR-7143**: O cancelamento MUST tirar da agenda vigente, com motivo, quem estava agendado e
  deixou de participar, sem apagar o que foi publicado, e MUST liberar o horário.
- **FR-7144**: A remarcação e a inclusão MUST gerar aviso só à pessoa afetada; a remarcação MUST
  dizer que o horário anterior não vale mais.
- **FR-7145**: A página pública e a área do candidato MUST mostrar o horário vigente, com "remarcado
  em" e a data quando houve remarcação.
- **FR-7146**: O motivo da remarcação, da inclusão e do cancelamento MUST ficar na trilha e MUST NOT
  aparecer ao candidato nem na página pública.
- **FR-7147**: As regras da FR-7111 MUST valer também para a remarcação e a inclusão.

#### O que a agenda não faz

- **FR-7150**: A agenda MUST NOT registrar presença, nota, parecer, ausência ou resultado. A ausência
  MUST continuar sendo registrada como Ocorrência na Etapa.
- **FR-7151**: A agenda MUST NOT calcular prazo a partir do horário. O horário MUST ser gravado e
  mostrado como dado do ato.
- **FR-7152**: A agenda MUST NOT conter regra de avaliação de Etapa alguma; o que é próprio de uma
  Etapa (documento a apresentar, acompanhamento de menor, gravação, conexão) MUST entrar só como
  texto das orientações.

#### Autorização e trilha

- **FR-7155**: Configurar e montar a agenda MUST exigir a permissão de gerir a Etapa; publicar,
  remarcar, incluir e cancelar MUST exigir também o escopo do Edital, e MUST ser negados por padrão.
- **FR-7156**: Configuração salva, preenchimento aplicado, agendamento à mão, publicação,
  remarcação, inclusão, cancelamento e reenvio MUST gerar registro na trilha, com ator, instante,
  estado anterior e posterior, e motivo quando houver; o registro MUST NOT conter e-mail nem endereço
  de sala.

### Requisitos de experiência

- **UX-760**: A capacidade MUST estar à vista enquanto se configura, ao lado dos campos no desktop e
  depois deles no celular, e MUST mudar a cada campo digitado.
- **UX-761**: A montagem MUST mostrar um dia por vez, em abas com a contagem de ocupados por dia, um
  resumo único de progresso no alto, e um painel de ação ao lado da grade no desktop e acima dela em
  telas estreitas. A ação acontece no painel; a grade MUST NOT repetir texto de ação em cada linha.
- **UX-762**: O ajuste à mão MUST funcionar sem arrastar: escolher uma pessoa e depois um horário,
  com teclado, leitor de tela e toque. Arrastar MAY existir como atalho, nunca como único caminho.
- **UX-763**: No celular, a grade MUST virar lista cronológica, com a banca dentro de cada horário.
- **UX-764**: A ação principal da montagem MUST ser a que falta fazer: "Preencher automaticamente"
  enquanto há pessoa sem horário e horário livre; "Conferir e publicar" depois. Nenhuma ação MUST
  aparecer duas vezes na mesma tela.
- **UX-765**: O estado vazio da agenda MUST dizer para que ela serve e que pode ser configurada antes
  de a lista fechar.
- **UX-766**: Toda recusa e todo impedimento MUST dizer o que fazer, e não só o que está errado.
- **UX-767**: As telas MUST usar as folhas e componentes da gestão e do portal, e nenhum estilo ou
  script escrito no documento.

### Key Entities

- **Agenda da Etapa**: a configuração operacional de uma Etapa — forma de atendimento, duração,
  intervalo, orientações — e a versão que a prévia confere. Uma por Etapa.
- **Janela de atendimento**: um dia e um intervalo de horas da agenda.
- **Banca**: um ponto de atendimento simultâneo, com nome e local ou endereço da sala. Não é grupo de
  avaliadores.
- **Agendamento**: quem está em que horário de que banca agora, com origem, autor e instante.
- **Ato da agenda**: a publicação, a remarcação, a inclusão ou o cancelamento; imutável, com autor,
  instante, motivo nos individuais e autoridade na publicação.
- **Horário publicado**: o que cada ato publicou, por pessoa; o de uma remarcação substitui o
  anterior sem apagá-lo.
- Já existem e não mudam: a **Etapa de Avaliação**, o **Evento de Cronograma**, a **Inscrição**, a
  **participação** da Etapa, a **Ocorrência**, o **aviso complementar** (que ganha uma origem).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2370**: *(humano)* Uma pessoa da comissão que não participou desta feature sai de uma lista
  de 43 participantes para uma agenda conferida e publicada, pela interface, sem planilha e sem
  ajuda, em menos de 15 minutos.
- **SC-2371**: Para as configurações das fixtures — uma ou duas janelas por dia, uma a três bancas,
  durações e intervalos variados —, o número de horários mostrado é igual ao derivado pela FR-7103 em
  100% dos casos, e os oito casos de recusa da FR-7104 são recusados em 100%.
- **SC-2372**: Depois de qualquer preenchimento, nenhuma pessoa tem dois horários, nenhum horário
  tem duas pessoas, e nenhuma pessoa agendada à mão mudou de horário — 100% dos casos de teste,
  inclusive sob duas operações simultâneas.
- **SC-2373**: Nenhuma publicação acontece com pessoa sem horário, pessoa que não participa mais ou
  banca sem local — 100% dos casos impeditivos recusados, e nenhum caso completo recusado.
- **SC-2374**: Em 100% das publicações, o conteúdo da página pública não contém endereço de sala,
  CPF, e-mail, telefone ou Modalidade.
- **SC-2375**: Cada pessoa publicada recebe exatamente um aviso por ato; numa remarcação, exatamente
  uma pessoa recebe aviso.
- **SC-2376**: A confirmação repetida da publicação cria um ato e zero avisos a mais.
- **SC-2377**: Todas as telas da feature abrem a 375 px de largura sem rolagem horizontal da página,
  e passam na política de conteúdo sem violação.
- **SC-2378**: *(humano)* Um candidato que não participou desta feature encontra o próprio horário
  na página pública, pelo celular, em menos de 1 minuto.

---

## Assumptions

- **Bancas simultâneas entram no MVP** (Q-1 do estudo). Custam pouco, e o cenário de
  heteroidentificação do Cefor já tem duas salas.
- **Publicação inteira, e não em partes** (Q-4). Todo participante precisa de horário antes de
  publicar; publicar por dia fica para quando um Edital o pedir.
- **A ordem do preenchimento é por nome** (Q-6), com o protocolo no empate: explicável e sem expor a
  posição na classificação.
- **A sala é por banca** (Q-7), como os Editais descrevem: uma sala da RNP por comissão.
- **A participação é a da Etapa**, inclusive o alcance por Modalidade quando a spec dele estiver na
  `main`. Sem ela, a agenda vale para qualquer Etapa que toda inscrição enviada faz.
- **A zona temporal é a institucional.** O horário é o do dia e da janela, na zona do domínio.
- **O prazo de justificativa da ausência** que alguns Editais contam do horário fica com o Edital; o
  GPS mostra o horário, e não calcula prazo.
- **A experiência visual é aprovada antes da implementação**, pelo protótipo do estudo.

## Out of Scope

- Autosserviço de escolha ou troca de horário pelo candidato.
- Disponibilidade individual dos avaliadores e composição das bancas.
- Calendário institucional, arquivo de calendário e integração com Google ou Outlook.
- Videoconferência embutida, sala de espera e gravação.
- Registro de presença na agenda.
- Lembrete na véspera e aviso de cancelamento, que seriam situações novas de mensagem.
- Publicação da agenda em partes.
- O vídeo assíncrono da verificação da autodeclaração, que é outra solução para outra parte do
  problema.

---

## Decisões

### D-001 — A agenda é operacional, e não norma do Edital

A Etapa e o Evento são norma, e mudá-los pede Retificação; o horário de cada pessoa não é norma: é a
execução de uma norma que o Edital já escreve em texto ("as datas, horários e o endereço da sala
serão divulgados"). Por isso não há caixa "esta Etapa exige agendamento" no Edital: a Etapa que pede
comparecimento tem agenda, e a outra não tem. Uma caixa seria norma sem efeito próprio.

### D-002 — A agenda não tem lista própria de participantes

A participação já tem fonte única, recalculada a cada leitura. Uma lista da agenda seria a segunda
fonte que o Princípio II proíbe, e divergiria na primeira reabilitação. O que a agenda congela é o
par pessoa-horário publicado; a diferença entre ele e a participação aparece como "sem horário" ou
"não participa mais".

### D-003 — Os horários são derivados da configuração

Gravar os horários seria uma segunda fonte, e uma janela mudada exigiria reconciliar linhas. Gravado
é só o agendamento, com as duas unicidades.

### D-004 — A banca é ponto de atendimento, e não grupo de avaliadores

Não existe banca no GPS, e a comissão já tem alocação à Etapa. Fazer da banca um grupo de pessoas
traria disponibilidade e composição, que o pedido põe fora. Duas bancas são duas pessoas atendidas
ao mesmo tempo, e só.

### D-005 — A convocação para vaga não é reusada

A convocação da `019` é de vaga, com espécie, chamada, sucessão e prazo que corre do envio; a agenda
não tem nenhum dos quatro. Reusá-la faria a ocupação enxergar convocados que ninguém chamou para vaga.

### D-006 — Depois da publicação, só ato individual

Republicar a agenda inteira para mudar uma pessoa avisaria todo mundo de novo e reescreveria o que
foi publicado. O ato individual muda uma pessoa, avisa uma pessoa, e guarda o anterior.

### D-007 — O aviso é origem nova do aviso complementar

O app de avisos já tem envio fora da confirmação, deduplicação por pessoa, retentativa, reenvio e a
moldura dos e-mails. Um envio próprio da agenda duplicaria tudo isso. A revisão da FR-084 da `010`
foi decidida pelo usuário (`D-010`).

### D-008 — A agenda publicada tem a natureza da relação de convocados

Decisão do usuário em 14/11/2026, entre a publicação formal (A) e a informativa, sem autoridade (B).
**A.** Os Editais da amostra contam prazo e consequência do horário publicado: no 28/2026 a
justificativa da ausência conta 24 horas do horário marcado "no ato da convocação", e a ausência
indefere. Um horário com esse efeito precisa de ato rastreável, com autoridade. O veículo segue a
`159`, que já distingue publicar no GPS de registrar a publicação feita fora, e por isso o Edital que
publica em outro lugar continua servido. A avaliação da proposta trazida pelo usuário em 14/11
sugeriu que a formalidade dependa do Edital; a decisão não adotou a variante, e o registro fica aqui
como insumo.

### D-009 — Na Etapa por Modalidade, a página pública mostra só o protocolo

Decisão do usuário em 14/11/2026, entre só o protocolo (A) e nome e protocolo, como a `149` (B).
**A.** A agenda de uma Etapa restrita por Modalidade é, por construção, a lista de quem concorre pela
reserva para pretos e pardos; com o nome, ela publicaria a autodeclaração de cada pessoa. O protocolo
basta para cada um achar o próprio horário, e a área do candidato mostra o resto. O estudo recomendou
ouvir o encarregado de dados; a consulta continua recomendada antes da implantação, e não bloqueia a
especificação.

### D-010 — A FR-084 é revista para o aviso de agenda

Decisão do usuário em 14/11/2026, entre revisar a lista fechada (A) e não avisar por e-mail (B).
**A.** Os Editais reagendam por e-mail, e o horário que a pessoa não vê é o que a faz perder a Etapa
(o registro de 09/10). O aviso entra como origem do aviso complementar da `066`, e não como envio
novo: a lista ganha uma situação, e o mecanismo, nenhum. O texto da FR-084 na `010` é revisto na
entrega que implementa os avisos, como a `019` e a `066` fizeram.
