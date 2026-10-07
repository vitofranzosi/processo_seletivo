# Feature Specification: Acompanhamento pela situação do candidato

**Feature Branch**: `claude/063-acompanhamento-pela-situacao`

**Created**: 2026-10-07

**Status**: Draft

**Input**: a pesquisa `doc/pesquisa-divulgacao-de-resultados-2026-10-07.md` (PR #261), na seção
"Revisão de 07/10/2026" e no bloco "Princípios fechados para a spec do acompanhamento", que
prevalecem sobre as recomendações antigas do relatório. O defeito que motiva: no Edital 72/2026 do
banco de demonstração, Edson Ferreira da Silva (Técnico de Laboratório de Química) lê "8º lugar" e
"2º lugar" em dois cartões idênticos, sem saber de que lista é cada um, nem o que isso significa para
ele.

> **Faixa de identificadores.** Abre em **FR-1166**, **SC-450** e **UX-155**. O teto medido em
> 07/10/2026 em todas as worktrees era o da `062-resultados-por-perfil-etapa-lista`, já na `main`
> (FR-1165, SC-449, UX-154). As decisões desta spec nascem em `D-001`; os princípios que o usuário
> trouxe fechados são **entrada** e aparecem como "princípios recebidos" (1º a 8º), sem reaproveitar
> a numeração.

**A frase que governa:**

> Antes de mostrar documentos e listas, diga à pessoa a situação atual dela, de onde essa situação
> decorre e o que ela precisa fazer a seguir.

**E a frase que mantém o corte:**

> A tela lê atos. Ela não decide ocupação, convocação, eliminação, direito à vaga nem posição na fila
> — e quando nenhum ato disse, ela diz que ainda não foi dito.

---

## Por que esta feature existe

O acompanhamento (`/selecoes/inscricoes/<id>/acompanhamento`) é hoje uma sequência de blocos na
ordem em que as features foram chegando: a convocação (059), a participação (010), o resultado de
cada Etapa (018), o resultado divulgado (017), os recursos (018) e o cronograma (010). Cada bloco está
certo em si, e o conjunto não responde à pergunta com que a pessoa chega:

- **A mesma pessoa vê duas posições sem saber qual é qual.** Quem concorre pela ampla e por uma
  reserva tem uma `SituacaoDivulgada` por lista (a decisão do eixo da lista, da `021`), e a tela
  intitula cada bloco só pelo marco: "Classificação final — Técnico de Laboratório", duas vezes, com
  "8º lugar" num e "2º lugar" no outro.
- **Ninguém diz a situação.** O que aparece é a posição ("2º lugar"), e a pessoa a lê como
  aprovação — ou como reprovação, se for 8º. O sistema não sabe se ela está dentro das vagas: isso é
  efeito da ocupação e da convocação, e não da posição.
- **O que fazer está espalhado ou ausente.** Para quem foi convocado, o prazo está no bloco da
  convocação; para quem pode recorrer, no fim de cada resultado; para quem só espera, em lugar
  nenhum, e o cronograma risca a data da convocação sem dizer nada da pessoa.
- **Evidência vem antes da conclusão.** Etapas, notas e motivos aparecem antes da classificação
  divulgada, e a classificação antes de qualquer frase sobre a pessoa.

---

## Princípios recebidos (07/10/2026)

Fechados pelo usuário em três rodadas de revisão da pesquisa. Não se reabrem aqui.

1. **Topo sempre Situação → Por quê → O que fazer.** "Nada por enquanto" é resposta válida. Etapas,
   notas, pesos e publicações vêm depois, como evidência.
2. **Cada lista mantém a sua posição oficial, natureza e data.** A classificação é imutável: quem é
   2º continua 2º, mesmo depois de a vaga ser ocupada pelo 1º. Nada de "melhor classificação", nada
   de "1º da fila".
3. **A situação deriva só de atos existentes** — corte (`014`), ocupação (`016`), convocação
   (`019`/`059`), requerimento de matrícula (`029`). A tela nunca infere ocupação, convocação,
   eliminação, direito à vaga nem posição na fila de chamada a partir da posição. A situação
   divulgada só conhece *classificada* e *sem posição*.
4. **Estado provisório distinto do definitivo.** "Aguardando chamada", e não "Classificado", que a
   pessoa lê como aprovado.
5. **Ação, prazo e consequência vêm do Edital ou do ato de convocação**, nunca de frase fixa da tela.
   Sem isso, a frase neutra: "novas chamadas, se houver, serão publicadas conforme o Edital"; "você
   perderá esta convocação".
6. **O vocabulário é o do Edital** ("cadastro reserva" × "lista de espera"; matrícula × contratação).
   O domínio informa situação, ação esperada, prazo e consequência, e a tela não decide por tipo de
   certame — nenhum `if curso / else servidor`.
7. **Não prometer canal que o Edital não usa.** Convocação por publicação não manda e-mail.
8. **Linguagem simples** (Lei 15.263/2025), com siglas por extenso na primeira ocorrência.

**Fora deste incremento** (decisão do usuário): a página pública da publicação (vagas por lista,
desempate, tabela no celular); a frase do `REC-…` na publicação, que a FR-088 da `018` exige; e a
governança da exposição da modalidade de cota.

---

## O que o domínio já fornece, ato por ato

Levantado no código e nas specs em 07/10/2026. É a matéria-prima da situação. O que **não** está
aqui não pode aparecer na tela como fato sobre a pessoa.

| Ato | O que registra **por pessoa** | O que **não** registra |
|---|---|---|
| Resultado de Etapa (`013`, exibido pela `018`) | Habilitada ou eliminada, pontuação, motivo, parecer (`036`), correção por recurso | — |
| Ordem e publicação (`015`, `017`, `021`) | Por lista: `SituacaoDivulgada` *classificada* (posição, empate, pontuação) ou *sem posição* (motivo); natureza (preliminar/definitivo), data, cadeia de sucessão | Se a posição está dentro das vagas |
| Corte (`014`, `061`) | `ItemDoCorte`: *progrediu* ou *fora da faixa*, posição, excedente por empate, motivo | Não é publicado nem consultável pelo candidato (fora de escopo da `014`); não elimina ninguém (FR-212) |
| Apuração de ocupação (`016`) | **Nada por pessoa.** Registra contagens (publicadas, efetivas, ocupadas) e o universo lido; titulares e ocupantes são **calculados** | Quem ocupa a vaga; quem está em cadastro reserva |
| Convocação (`019`, `050`, `059`) | Espécie (vaga inicial, vaga que vagou, para regularizar), chamada, vencimento, fundamento, comunicação emitida (forma: publicação ou mensagem individual; enviada em) | Ação esperada estruturada; consequência estruturada; origem do vencimento (digitado ou do Cronograma) |
| Desfecho da convocação (`019`) | Aceite, regularização, indeferimento, desistência expressa, não atendimento, cancelamento de matrícula por inércia, reclassificação — com fundamento | — |
| Requerimento de Matrícula (`029`) | Rascunho ou enviado, quando o Edital o declara (`requerimento_momento`) | Deferimento, matrícula efetivada (UX-058 proíbe as palavras) |
| Edital | Por Perfil: tipo de cadastro reserva (nenhum, limitado, ilimitado) e limite; forma de convocação; regra de corte; janela recursal; Cronograma (eventos de texto livre) | Tipo de certame; vocabulário (matrícula × contratação; "lista de espera"); ação e consequência da convocação em forma estruturada (`call_information` é JSON opaco, sem consumidor) |

**Nenhum ato confirma matrícula ou contratação.** A `040` registrou a ausência como decisão (G-001);
o mais próximo é o desfecho *Aceite*, que inclui a pessoa na contagem de ocupantes (`019`, R-006).

---

## Lacunas explícitas

O que o domínio não fornece e esta feature **não** inventa. Cada uma vira, na tela, ausência de
afirmação — e, fora dela, registro para decisão do usuário (governança).

- **L-1 · A ocupação não registra quem ocupa.** A apuração guarda contagens; quem é titular sai de
  cálculo. Entre a apuração e a convocação, a pessoa não tem ato que diga "dentro das vagas".
  *Decidido em 07/10* (Clarifications): até haver convocação, "Aguardando chamada".
- **L-2 · O corte não chega ao candidato.** O `ItemDoCorte` é ato interno da gestão; a `014` deixou
  a consulta pelo candidato fora de escopo. *Decidido em 07/10*: o corte não aparece na tela.
- **L-3 · Não há ato de matrícula ou contratação confirmada.** O desfecho *Aceite* é da convocação.
  A tela não diz "matriculado" nem "contratado". *Decidido em 07/10*: o *Aceite* aparece como
  "Vaga aceita".
- **L-4 · O Edital não estrutura ação nem consequência da convocação.** O fundamento da convocação
  sai de modelo fixo por espécie, mais complemento do operador; `call_information` é opaco. A única
  ação estruturada é o Requerimento de Matrícula, quando o Edital o declara.
- **L-5 · Não há vocabulário do Edital para a fila.** "Lista de espera" não existe no domínio;
  "cadastro reserva" existe só como atributo do Perfil, sem pertença individual. A tela não diz
  "lista de espera" e não diz que a pessoa "está no cadastro reserva".
- **L-6 · Não há tipo de certame.** A tela não distingue curso de servidor; o que muda o texto é o
  que o Edital declarou (Requerimento de Matrícula, forma de convocação, cadastro reserva).
- **L-7 · A origem do vencimento não fica na convocação.** A tela diz "prazo desta convocação", e
  não "prazo do Edital".

---

## Clarifications

### Session 2026-10-07

- Q: A apuração de ocupação só guarda contagens; entre a apuração e a convocação, o que a tela pode
  dizer a quem o cálculo poria entre os titulares? → A: **Só a convocação muda a situação.** Até
  haver convocação, a situação é "Aguardando chamada"; a lacuna L-1 fica registrada para decisão
  futura sobre a apuração registrar quem ocupa. Sem migration.
- Q: O corte registra *progrediu* / *fora da faixa* por pessoa, mas não é publicado; o acompanhamento
  pode usá-lo? → A: **Não.** O corte não entra na situação nem no porquê; cada lista mostra só a sua
  posição oficial. A lacuna L-2 fica registrada.
- Q: Como a situação nomeia o desfecho *Aceite*, já que nenhum ato confirma matrícula ou
  contratação? → A: **"Vaga aceita"**, com o fundamento e a data do registro; os demais desfechos
  seguem a mesma regra de linguagem simples (tabela da FR-1172); nunca "matriculado" nem
  "contratado". A lacuna L-3 fica registrada.

**Consequência das três respostas para o princípio 3.** Dos quatro atos que o princípio nomeia, a
convocação (com o desfecho) e o Requerimento de Matrícula alimentam a situação nesta feature; o
corte e a ocupação **não**, porque um não é divulgado ao candidato e a outra não registra a pessoa.
A situação também lê os dois atos que já chegavam à tela e que a tabela acima mostra — a situação
divulgada por lista e o Resultado de Etapa visível.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A pessoa em duas listas entende onde está (Priority: P1)

Edson concorre à vaga de Técnico de Laboratório pela ampla concorrência e pela reserva para pessoas
pretas, pardas e indígenas. Ao abrir o acompanhamento, ele lê primeiro a situação dele, de onde ela
vem e o que fazer. Abaixo, encontra um cartão por lista, cada um com o nome da lista, a etapa, a
natureza, a data e a posição oficial daquela lista.

**Why this priority**: é o defeito que motivou a feature, e o caso mais comum depois da `021`: toda
pessoa que optou por uma reserva aparece em duas listas.

**Independent Test**: no banco de demonstração, entrar como Edson (Edital 72/2026) e conferir que a
primeira coisa depois do título é a situação, e que os dois cartões se distinguem pelo nome da lista.

**Acceptance Scenarios**:

1. **Given** uma inscrição classificada na ampla (8º) e na PPI (2º), as duas publicações vigentes,
   sem convocação, **When** a pessoa abre o acompanhamento, **Then** o topo diz "Aguardando chamada",
   o porquê cita as duas classificações com o nome de cada lista, e o que fazer é "Nada por
   enquanto", com a frase neutra sobre novas chamadas.
2. **Given** a mesma inscrição, **When** a pessoa lê os cartões, **Then** há um cartão por lista,
   cada um intitulado pelo nome da lista e pela etapa, com natureza, data de publicação, posição e
   pontuação, e nenhum cartão tem título igual a outro.
3. **Given** a mesma inscrição, **When** a pessoa lê a página inteira, **Then** em nenhum lugar ela
   lê "Classificado", "Aprovado", "Dentro das vagas", "lista de espera", "direito à vaga" ou uma
   posição diferente da oficial ("1º da fila").

---

### User Story 2 — Classificação registrada, ocupação ainda não definida (Priority: P1)

A pessoa foi classificada, e nenhum ato ainda disse se ela ocupa vaga. A tela diz isso como "ainda
não", e não como "não": o estado é provisório, nomeado como tal, e o que fazer é esperar, com o
canal pelo qual o Edital diz que as convocações chegam.

**Why this priority**: é o estado em que mais gente fica mais tempo, e é onde a tela atual mais
engana — "2º lugar" lido como aprovação.

**Independent Test**: inscrição classificada sem convocação; conferir o rótulo provisório, o porquê,
e que o canal citado é o que o Perfil declara.

**Acceptance Scenarios**:

1. **Given** uma inscrição classificada só em resultado **preliminar**, **When** a pessoa abre a
   tela, **Then** a situação diz que a classificação é preliminar e pode mudar, e o que fazer
   mostra o prazo de recurso quando ele está aberto.
2. **Given** um Perfil que declara convocação **por publicação**, **When** a pessoa está aguardando
   chamada, **Then** o que fazer diz que as convocações são publicadas no endereço do certame, e a
   tela não promete e-mail nem mensagem.
3. **Given** um Perfil que não declara forma de convocação, **When** a pessoa está aguardando,
   **Then** a tela usa só a frase neutra, sem nomear canal.

---

### User Story 3 — Cadastro reserva sem pertença inventada (Priority: P2)

O Edital prevê cadastro reserva para o Perfil. A tela pode dizer que o Edital prevê, e com que
limite, porque isso é do Edital. Ela não diz que a pessoa está no cadastro reserva, porque nenhum ato
o registra (L-5).

**Why this priority**: o caso (c) da demonstração. É onde a tentação de deduzir da posição é maior
("12 vagas + 10 de reserva, você é 15º, logo está na reserva").

**Independent Test**: inscrição classificada num Perfil com cadastro reserva limitado; conferir a
frase do Edital e a ausência de pertença individual.

**Acceptance Scenarios**:

1. **Given** um Perfil com cadastro reserva limitado a N pessoas, **When** a pessoa classificada
   aguarda chamada, **Then** o porquê ou o que fazer pode dizer "o Edital prevê cadastro reserva de
   até N pessoas para este Perfil", e não diz "você está no cadastro reserva".
2. **Given** um Perfil sem cadastro reserva, **When** a pessoa aguarda chamada, **Then** a tela não
   menciona cadastro reserva.

---

### User Story 4 — Convocação aberta: ação, prazo e consequência (Priority: P1)

A pessoa foi convocada. O topo diz "Convocado", por qual lista e em que chamada, e o que fazer: a
ação que o Edital declara (preencher o Requerimento de Matrícula, quando o Edital o exige), o prazo
desta convocação e a consequência neutra de não atender.

**Why this priority**: é o único estado com prazo correndo contra a pessoa (059, decisão 005 da
`059`). Perder a data é perder a vaga.

**Independent Test**: no Edital 72/2026, uma convocada com Requerimento em rascunho e vencimento
futuro; conferir ação, prazo e consequência no topo.

**Acceptance Scenarios**:

1. **Given** uma convocação vigente sem desfecho, com vencimento e Requerimento de Matrícula
   disponível, **When** a pessoa abre a tela, **Then** o topo diz "Convocado", o porquê cita a
   espécie, a lista e a data da convocação, e o que fazer traz "Preencher o Requerimento de
   Matrícula", o prazo com data e hora e "se você não atender no prazo, você perderá esta
   convocação".
2. **Given** a comunicação da convocação ainda não enviada, **When** a pessoa abre a tela, **Then**
   o que fazer diz que o prazo ainda não começou a correr, como a `059` já diz.
3. **Given** o vencimento decorrido sem desfecho, **When** a pessoa abre a tela, **Then** a tela não
   diz que ela perdeu a vaga: diz que o prazo passou, que isso não decide nada sozinho e que procure
   o atendimento se atendeu (FR-274).
4. **Given** o Requerimento já enviado, **When** a pessoa abre a tela, **Then** o que fazer diz que
   o requerimento foi enviado e quando, sem "deferido", "homologado" nem "matrícula efetivada"
   (UX-058).
5. **Given** uma convocação de um Edital que não declara Requerimento de Matrícula, **When** a pessoa
   abre a tela, **Then** a ação é "siga as instruções do Edital para esta convocação", e a tela não
   diz "matrícula" nem "contratação".

---

### User Story 5 — O desfecho registrado (Priority: P2)

A instituição registrou o desfecho da convocação. O topo diz o desfecho como o domínio o registra,
com o fundamento, e a tela não o promove a "matriculado" ou "contratado" (L-3).

**Why this priority**: o caso (e) da demonstração. Fecha a jornada para quem foi chamado.

**Independent Test**: Ana Silva no Edital 51 (`seed_demo`), com desfecho registrado pela gestão;
conferir rótulo e fundamento no topo.

**Acceptance Scenarios**:

1. **Given** uma convocação com desfecho *Aceite*, **When** a pessoa abre a tela, **Then** a
   situação é "Vaga aceita", o porquê traz o fundamento e a data do registro, e o que fazer é "nada
   por enquanto" — sem "matriculado" nem "contratado".
2. **Given** um desfecho excludente (não atendimento, desistência, indeferimento, inércia,
   reclassificação), **When** a pessoa abre a tela, **Then** a situação nomeia o desfecho, o porquê
   traz o fundamento, e o que fazer mostra o recurso quando o domínio o oferece, ou "nada por
   enquanto".

---

### User Story 6 — Eliminada, sem posição, ou ainda sem resultado (Priority: P2)

Quem foi eliminado numa Etapa, quem não recebeu posição numa lista, e quem ainda não tem resultado
algum também abre a tela pela situação.

**Why this priority**: completa o conjunto finito de estados; sem isso, o topo some para quem mais
precisa de explicação.

**Independent Test**: três inscrições — eliminada numa Etapa com publicação vigente, sem posição em
todas as listas, e recém-enviada —, cada uma com o seu topo.

**Acceptance Scenarios**:

1. **Given** um Resultado de Etapa *eliminada* visível (018), **When** a pessoa abre a tela, **Then**
   a situação diz "Eliminado na etapa X", o porquê traz o motivo, e o que fazer mostra o prazo de
   recurso quando aberto, ou "nada por enquanto".
2. **Given** *sem posição* em todas as listas vigentes, **When** a pessoa abre a tela, **Then** a
   situação diz "Não classificado", com o motivo de cada lista.
3. **Given** uma inscrição enviada sem nenhum resultado divulgado, **When** a pessoa abre a tela,
   **Then** a situação diz "Inscrição enviada", o porquê traz a data do envio, e o que fazer é "nada
   por enquanto; o resultado será publicado conforme o Edital".

---

### Edge Cases

- **Classificada numa lista e sem posição noutra.** A situação é a da classificação ("Aguardando
  chamada"); o cartão da lista sem posição mostra o motivo daquela lista.
- **Convocada por uma lista e classificada noutra.** A situação é "Convocado", e o porquê nomeia a
  lista da convocação; o cartão da outra lista continua com a posição oficial dela, sem "não precisa
  mais" nem "liberou a vaga".
- **Vários marcos classificatórios.** Um cartão por lista **e** por marco, na ordem normativa dos
  marcos (FR-058); a situação considera só os vigentes.
- **Publicação sucedida.** O cartão mostra a vigente; a sucedida não entra na situação.
- **Convocação sucedida, ou desfecho sucedido** (inércia depois de aceite). Vale o vigente.
- **Chamada sucessiva** (a mesma pessoa chamada de novo, FR-283). A situação cita a chamada vigente
  e o número dela.
- **Recurso em andamento.** Não muda a situação, que só muda por ato; o porquê pode acrescentar que
  há recurso em análise, com link para ele.
- **Edital retificado depois do envio.** O aviso da FR-079 continua, abaixo do topo.
- **Pontuação zero.** Aparece como nota ("0,00"), e não some (comportamento já preso).
- **Inscrição em rascunho.** Continua redirecionando para a inscrição, como hoje.

---

## Requirements *(mandatory)*

### Functional Requirements

**A situação**

- **FR-1166**: O acompanhamento DEVE abrir, logo após o título e o nome do processo, por um bloco de
  situação com três partes, nesta ordem e sempre presentes: **Situação** (um rótulo curto),
  **Por quê** (o ato ou os atos de que a situação decorre, com data) e **O que fazer** (a ação, o
  prazo e a consequência — ou "Nada por enquanto").
- **FR-1167**: A situação DEVE ser derivada num único lugar fora do template, a partir dos atos
  vigentes da inscrição, e o template só a apresenta. A mesma derivação DEVE ser a que os testes
  consultam.
- **FR-1168**: O conjunto de situações DEVE ser finito e fechado, com esta precedência (a primeira
  que se aplica vence): desfecho da convocação vigente; convocação vigente sem desfecho; eliminação
  em Etapa visível; classificação em ao menos uma lista vigente ("Aguardando chamada"); sem posição
  em todas as listas vigentes ("Não classificado"); inscrição enviada sem resultado ("Inscrição
  enviada").
- **FR-1169**: Nenhuma situação DEVE ser derivada da posição. A tela NÃO DEVE afirmar ocupação,
  convocação, eliminação, direito à vaga, pertença a cadastro reserva ou posição na fila de chamada
  que nenhum ato registrou. A apuração de ocupação NÃO DEVE ser consultada para a situação: ela não
  registra quem ocupa (L-1), e só a convocação tira a pessoa de "Aguardando chamada".
- **FR-1170**: O estado posterior à classificação e anterior a qualquer convocação DEVE ser
  "Aguardando chamada", identificado como provisório, e NÃO DEVE ser "Classificado" nem "Aprovado".
  Quando todas as classificações vigentes da inscrição forem preliminares, a situação DEVE dizer que
  a classificação é preliminar e pode mudar.
- **FR-1171**: O resultado individual do corte (`014`) NÃO DEVE aparecer na tela — nem na
  situação, nem no porquê, nem nos cartões —, porque o corte não é ato divulgado ao candidato (L-2).
- **FR-1172**: Quando a situação vier de desfecho da convocação vigente, o rótulo DEVE ser o desta
  tabela, e o porquê DEVE trazer o fundamento e a data do registro. A tela NÃO DEVE dizer
  "matriculado", "contratado", "matrícula confirmada" nem "contratação confirmada", porque nenhum ato
  o registra (L-3).

  | Desfecho registrado | Situação |
  |---|---|
  | Aceite | Vaga aceita |
  | Regularização | Regularização registrada |
  | Indeferimento | Indeferido na convocação |
  | Desistência expressa | Desistência registrada |
  | Não atendimento à convocação | Convocação não atendida |
  | Cancelamento de matrícula por inércia | Matrícula cancelada por inércia |
  | Reclassificação | Reclassificado |

  O sexto rótulo diz "matrícula" porque é o nome que o domínio dá ao desfecho (`019`, decisão 011
  da `019`), e não escolha da tela por tipo de certame.

**Por quê**

- **FR-1173**: O porquê DEVE nomear cada ato pela lista e pela etapa a que pertence, com a natureza
  (preliminar ou definitivo) e a data de publicação — ou, para convocação e desfecho, pela espécie,
  a lista, o número da chamada e a data.
- **FR-1174**: Quando a pessoa estiver em mais de uma lista, o porquê DEVE citar cada uma com a
  própria posição oficial, sem escolher a "melhor", sem somar e sem reordenar, e DEVE dizer em frase
  simples que cada lista tem a sua classificação.

**O que fazer**

- **FR-1175**: A ação DEVE vir do Edital ou do ato: o Requerimento de Matrícula, quando a política
  da `029` disser que ele está disponível, em preenchimento ou enviado; o recurso, quando houver
  objeto recorrível com prazo aberto (com data e hora de encerramento); e, na convocação sem
  Requerimento, "siga as instruções do Edital para esta convocação".
- **FR-1176**: O prazo da convocação DEVE ser o vencimento registrado nela, com data e hora, e DEVE
  ser chamado "prazo desta convocação". Sem comunicação enviada, a tela DEVE dizer que o prazo não
  começou; com vencimento decorrido sem desfecho, DEVE dizer que isso não decide nada sozinho
  (FR-274).
- **FR-1177**: A consequência DEVE vir do Edital ou do ato quando ele a declarar; enquanto nenhum
  dos dois a declarar em forma estruturada (L-4), a tela DEVE usar só as duas frases neutras dos
  princípios recebidos: "Novas chamadas, se houver, serão publicadas conforme o Edital." (aguardando)
  e "Se você não atender no prazo, você perderá esta convocação." (convocado). Nenhuma outra frase de
  consequência DEVE existir na tela.
- **FR-1178**: "Nada por enquanto" DEVE ser a ação quando nenhum ato pede algo da pessoa.
- **FR-1179**: O canal citado DEVE ser o que o Perfil declara na forma de convocação ("por
  publicação no endereço eletrônico do certame" ou "por mensagem individual"); sem declaração, a
  tela NÃO DEVE nomear canal. A tela NÃO DEVE prometer e-mail quando a forma for publicação.
- **FR-1180**: Quando o Perfil declarar cadastro reserva, a tela PODE dizer que o Edital o prevê, e
  com que limite, como fato do Edital; NÃO DEVE dizer que a pessoa está nele (L-5). "Lista de espera"
  NÃO DEVE aparecer.

**As listas, como evidência**

- **FR-1181**: Abaixo da situação, a tela DEVE mostrar um cartão por lista e por marco com
  `SituacaoDivulgada` vigente, intitulado pelo nome da lista (o mesmo `nome_da_lista` da página
  pública, "Ampla concorrência" incluída) e pelo nome da etapa, com natureza, data de publicação,
  posição oficial (com "posição compartilhada" quando houver), pontuação, prazo de recurso quando
  aberto e o caminho para a publicação vigente.
- **FR-1182**: Para a lista sem posição, o cartão DEVE dizer "Sem posição nesta lista" com o motivo,
  e não "Você não foi classificado neste marco".
- **FR-1183**: A ordem da página abaixo da situação DEVE ser: aviso de Edital retificado (quando
  houver); convocação, quando houver; os cartões das listas; o resultado das Etapas; os recursos;
  a participação; o cronograma; "Ver o que enviei". O detalhe da convocação NÃO DEVE repetir o que
  o topo já disse com outra redação.

**A tela vizinha**

- **FR-1184**: A tela da convocação, para quem não foi chamado num recorte com convocações, DEVE
  trocar "quem está na lista pode ser chamado quando uma vaga vagar" pela frase neutra da FR-1177,
  porque a primeira promete consequência que nenhum ato declarou.

**Preservado**

- **FR-1185**: Ficam como estão: a ausência de bloco de resultado quando nada foi divulgado
  (FR-056) — o topo diz "Inscrição enviada"; a leitura sem registro na trilha (decisão 008 da
  `059`); o zero de consultas ao requerimento sem convocação (decisão 006 da `059`); o parecer do
  titular (`036`); o aviso de retificação (FR-079); a resposta privada; e a titularidade.

### Experiência e linguagem

- **UX-155**: A situação DEVE ser texto, nunca só cor ou ícone, e o rótulo DEVE ser adjetivo ou
  substantivo curto, consistente entre a situação e os cartões.
- **UX-156**: Siglas DEVEM vir por extenso na primeira ocorrência da página, e nenhuma frase do topo
  DEVE exigir termo técnico sem explicação ("homologação", "marco", "faixa", "apuração").
- **UX-157**: A hierarquia de títulos DEVE ser `h1` (Acompanhar) → `h2` (Sua situação; Classificação
  por lista; …) → `h3` (cada cartão), e a 375 px a página NÃO DEVE ter rolagem horizontal.
- **UX-158**: Varredura de vocabulário DEVE reprovar, nos templates desta tela, "Classificado",
  "Aprovado", "Dentro das vagas", "lista de espera", "direito à vaga", "matriculado", "contratado" e
  "da fila".

### Key Entities

- **Situação da inscrição**: projeção de leitura, sem persistência. Tem rótulo (de um conjunto
  fechado), natureza do estado (provisório ou registrado), os atos de origem (cada um com lista,
  etapa, natureza ou espécie e data) e o que fazer (ação, prazo, consequência, canal).
- **Cartão de lista**: projeção de uma `SituacaoDivulgada` vigente — lista, etapa, natureza, data,
  posição ou motivo, pontuação, prazo recursal, publicação.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-450**: Nas seis situações do conjunto fechado, o primeiro conteúdo depois do título é o bloco
  de situação com as três partes; em 100% dos casos de teste as três estão presentes.
- **SC-451**: Na inscrição em duas listas (Edson, Edital 72/2026), os cartões têm títulos distintos
  e cada posição aparece ao lado do nome da sua lista; a posição exibida é igual à oficial em 100%
  dos cartões.
- **SC-452**: Zero ocorrências, na tela, das palavras proibidas da UX-158, em todos os cenários de
  teste.
- **SC-453**: Para cada situação, a frase de consequência é uma das duas neutras ou uma declarada
  por ato; nenhuma outra frase de consequência existe nos templates da tela.
- **SC-454**: O número de consultas do acompanhamento não cresce com o número de listas e de marcos
  da inscrição.
- **SC-455**: A demonstração percorre, pelo portal, os cinco casos — duas listas, classificação sem
  ocupação, cadastro reserva, convocação aberta com ação e prazo, desfecho registrado —, sem shell
  para ver a tela.
- **SC-456**: A 375 px, nenhuma das telas dos cinco casos tem rolagem horizontal.

---

## Assumptions

- O universo é o da inscrição aberta na tela: um Perfil. Quem tem inscrição em dois Perfis abre dois
  acompanhamentos, como hoje.
- "Vigente" é o que ninguém sucedeu, em publicação, convocação e desfecho — as regras de cada feature
  de origem.
- O Edital 72/2026 do banco de demonstração declara Requerimento de Matrícula na convocação para
  Perfis de servidor. A tela mostra o Requerimento porque o Edital o declarou (princípio 6); o nome
  do documento é da `029`, e corrigir o dado de demonstração não é desta feature.
- O desfecho, para a demonstração, é registrado pela gestão no fluxo da `050`, que é o canal do ator
  que o registra; a tela do candidato é só lida.
- Nenhuma migration. Nenhum ato novo. Nenhuma mudança na página pública da publicação.

## Out of Scope

- A página pública da publicação: vagas por lista, desempate, tabela no celular, linha "Você".
- A frase do `REC-…` na publicação que sucede outra (FR-088 da `018`).
- A exposição da modalidade de cota nas listas públicas (governança).
- E-mail a cada nova publicação.
- Mostrar "último convocado" ou posição na fila de chamada.
- Ato de matrícula ou contratação confirmada (L-3), vocabulário do Edital para a fila (L-5), tipo de
  certame (L-6), ação e consequência estruturadas da convocação (L-4) — registros para o usuário.
- O item da lista "Minhas inscrições" (059), que continua dizendo só se há convocação aberta.
