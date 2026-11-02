# Feature Specification: Desempate pela nota de Etapa que o marco não enumera

**Feature Branch**: `claude/114-desempate-por-etapa-nao-enumerada`, sobre a `main` em `9eaf75fb`

**Created**: 2026-11-01

**Status**: Draft. A direção foi decidida pelo usuário em 01/11/2026: corrigir no cálculo, e não
recusar o critério na validação. A Etapa do desempate ainda sem Resultado também foi decidida por ele
no mesmo dia (FR-3553, D-004).

**Input**: achado A11 do estudo da configuração da classificação
(`doc/estudo-configuracao-classificacao-2026-11-01/diario-de-construcao.md`, na branch
`claude/gps-classification-config-ux-294027`), confirmado por teste contra PostgreSQL no commit
`5dc7f420` daquela branch.

> **Faixa de identificadores.** Esta spec abre em **FR-3546** e **SC-1073**. O teto foi medido em
> 01/11/2026 em `specs/` de todas as branches locais e remotas e de todas as worktrees desta máquina:
> o requisito funcional três mil quinhentos e quarenta e cinco, e o critério mil e setenta e dois.
> **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-2233 da `094`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

**O edital diz "em caso de empate, a maior nota na Entrevista", e o GPS não desempata.** Um marco
pode somar só a Prova escrita na nota final e desempatar pela Entrevista. A publicação aceita o
critério, a tela oferece a Entrevista como alvo, e o PDF do Edital o anuncia. Mas o cálculo oficial
lê só os Resultados das Etapas que o marco enumera, e a nota da Entrevista chega vazia ao desempate.
O critério nunca separa ninguém: os empatados ficam empatados, e nada avisa o operador.

O teste do achado reproduz o caso: Prova escrita com 80, 80 e 70; Entrevista com 70 e 90 para os dois
empatados. A ordem oficial põe os dois em 1º, com empate residual e sem critério que separou.

**O usuário escolheu corrigir no cálculo** (01/11/2026): o GPS busca também a nota da Etapa citada
pelo critério de desempate, e essa Etapa desempata **sem entrar na nota final**. A alternativa —
recusar o critério na validação — foi descartada, porque o que o edital escreve é legítimo.

### O que esta spec cobre, e o que fica fora

Cobre: o que o cálculo lê da Etapa do desempate e o que ele ignora dela; o universo gravado no ato e a
obsolescência; a conferência da proveniência no banco; a reprodução do ato; a prévia da
classificação.

Fica fora:

- **a validação e a tela de configuração.** Nada passa a ser recusado nem oferecido de outro modo;
- **a pertinência das decisões de recurso ao marco** (providência a jusante, recurso contra a
  publicação, acompanhamento do candidato), que continua a ser a das Etapas enumeradas (D-005);
- **o critério por fato declarado**, que já funciona e não muda.

## Clarifications

### Session 2026-11-01

- Q: O que corrige o A11 — ler a nota da Etapa citada, ou recusar o critério? → A: Ler a nota. A Etapa
  desempata sem entrar na nota final (decisão do usuário, registrada no estudo).
- Q: Quando a Etapa do desempate ainda não tem Resultado de quem o critério precisa separar, emite-se
  com o valor ausente — valendo o "quando o valor falta" publicado — ou impede-se a emissão até haver
  Resultado? → A: Emite-se. Vale o "quando o valor falta" publicado; quando as notas chegarem, a ordem
  fica obsoleta e pede sucessora (D-004).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O critério publicado separa os empatados pela nota da Etapa citada (Priority: P1)

O Edital soma só a Prova escrita e desempata pela maior nota na Entrevista. Dois candidatos tiram 80 na
Prova; na Entrevista, um tira 70 e o outro 90. Quem emite a ordem vê o de 90 em 1º e o de 70 em 2º, e
o ato registra que a Entrevista os separou, com a nota de cada um.

**Why this priority**: é o defeito do A11. Sem isto, o edital promete um desempate que o GPS não faz.

**Independent Test**: publicar o marco, avaliar e consolidar as duas Etapas, calcular a ordem e conferir
posições, critério que separou e valor gravado na proveniência de cada posição.

**Acceptance Scenarios**:

1. **Given** o marco que enumera só a Prova e desempata pela Entrevista, com Prova 80, 80, 70 e
   Entrevista 70 e 90 para os dois primeiros, **When** a ordem é calculada, **Then** o de 90 fica em 1º,
   o de 70 em 2º e o de 70 na Prova em 3º, sem empate residual.
2. **Given** o mesmo cenário, **When** a ordem é emitida, **Then** a pontuação combinada de cada um é a
   da Prova — a Entrevista não muda nenhuma nota final — e a proveniência do desempate de cada posição
   traz a nota da Entrevista como valor do critério.
3. **Given** um marco cujas Etapas enumeradas e critérios não citam Etapa fora da enumeração, **When**
   a ordem é calculada, **Then** o resultado é idêntico ao de antes desta feature.

---

### User Story 2 — Ser eliminado na Etapa do desempate não tira ninguém desta ordem (Priority: P1)

Um candidato é eliminado na Entrevista. Na ordem do marco que só soma a Prova, ele continua classificado
pela nota da Prova; a Entrevista só serve para desempatar.

**Why this priority**: sem esta regra, ler os Resultados da Entrevista mudaria quem é classificado nesta
ordem — que o edital não determina.

**Independent Test**: montar um eliminado na Entrevista, com nota na Prova, e conferir que ele tem
posição, consequência de habilitado e nenhum motivo de eliminação nesta ordem.

**Acceptance Scenarios**:

1. **Given** um candidato com 75 na Prova e eliminado na Entrevista (posterior à Prova), **When** a
   ordem do marco que só soma a Prova é calculada, **Then** ele tem posição pela nota 75, e não aparece
   entre os sem posição.
2. **Given** o mesmo candidato empatado com outro na Prova, **When** a ordem é calculada, **Then** a nota
   que ele recebeu na Entrevista, se houver, é a que desempata; sem nota, vale o "quando o valor falta".

---

### User Story 3 — Recurso deferido na Etapa do desempate torna a ordem obsoleta (Priority: P1)

A nota da Entrevista de um dos empatados é corrigida por recurso. A tela do marco passa a dizer que a
ordem emitida está obsoleta, porque os Resultados oficiais do universo mudaram, e oferece emitir a
sucessora.

**Why this priority**: uma ordem que ignora a correção de uma nota que a decide seria um ato que nada
desatualiza — o defeito que a obsolescência existe para impedir.

**Independent Test**: emitir a ordem, deferir recurso que corrige a nota da Entrevista de um empatado, e
conferir que a comparação do ato com o cálculo de agora acusa "Resultados oficiais do universo
mudaram", e que a sucessora inverte a ordem.

**Acceptance Scenarios**:

1. **Given** uma ordem emitida com a Entrevista desempatando, **When** a nota da Entrevista de um
   empatado é substituída por recurso deferido, **Then** a ordem emitida fica obsoleta, com a diferença
   nomeada como mudança nos Resultados do universo.
2. **Given** a ordem emitida, **When** a reprodução do ato é pedida a partir do que ele gravou, **Then**
   ela devolve as mesmas posições do ato, sem divergência.

---

### User Story 4 — A prévia mostra o mesmo desempate que o cálculo oficial (Priority: P2)

Quem configura o marco na prévia da classificação vê candidatos fictícios com nota também na Etapa do
desempate, e a ordem da prévia é a que o cálculo oficial produziria para os mesmos candidatos.

**Why this priority**: a prévia que mostrasse um desempate diferente do oficial ensinaria errado quem
configura, e a equivalência entre as duas é requisito da `094`.

**Independent Test**: para um marco que desempata por Etapa não enumerada, gravar os candidatos da prévia
pelo caminho normal e conferir que as duas ordens, sem posição e corte coincidem.

**Acceptance Scenarios**:

1. **Given** um marco que enumera só a Prova e desempata pela Entrevista, **When** a prévia é simulada,
   **Then** os candidatos fictícios têm nota na Entrevista e a prévia não acusa falta de declaração.
2. **Given** os candidatos da prévia gravados pelo caminho normal, **When** a ordem oficial é calculada,
   **Then** ela coincide com a da prévia em posição, empate, critério que separou e sem posição.

### Edge Cases

- **A Etapa do desempate é também enumerada.** Nada muda: a nota já chegava ao desempate.
- **A Etapa do desempate é decisória** (não produz nota). O valor falta para todos, e vale o "quando o
  valor falta" publicado — como hoje.
- **A Etapa do desempate vem antes da última Etapa enumerada.** Quem foi eliminado nela já não participa
  desta ordem pela regra de progressão que existe (o eliminado antes da Etapa do marco não chega a ela),
  e isso não muda. A FR-3548 trata só do eliminado que, pela progressão, ainda participaria.
- **A Etapa do desempate vem depois da última enumerada e ainda não tem Resultado.** É a FR-3553.
- **Dois critérios citam Etapas diferentes não enumeradas.** As duas são lidas, cada uma só para o seu
  critério.
- **Ato emitido antes desta feature, em marco que já desempatava por Etapa não enumerada.** Ao abrir o
  marco, o cálculo de agora cita os Resultados da Etapa do desempate, que o ato não cita: o ato aparece
  obsoleto, com a diferença nos Resultados do universo. É o comportamento correto — o ato foi emitido
  com o critério sem efeito — e a sucessora pede motivo (D-003).
- **Recorte reservado.** A Etapa do desempate é lida para os participantes do recorte, como as
  enumeradas.

## Requirements *(mandatory)*

### Functional Requirements

#### O que o cálculo lê

- **FR-3546**: O critério de desempate "maior pontuação numa Etapa" MUST comparar a pontuação vigente de
  cada participante na Etapa que ele cita, **seja ela enumerada pelo marco ou não**. Etapa citada por
  critério e não enumerada pelo marco é, nesta spec, a **Etapa do desempate**.
- **FR-3547**: A pontuação da Etapa do desempate MUST NOT entrar na pontuação combinada, na decisão de
  quem tem pontuação em todas as Etapas enumeradas, nem no motivo de quem fica sem posição por falta
  de pontuação. A nota final de todo participante é a mesma que seria sem o critério.
- **FR-3548**: A consequência registrada na Etapa do desempate (inclusive eliminação) MUST NOT tirar o
  participante da ordem do marco, nem lhe dar consequência ou motivo nela. Quem tem posição e quem não
  tem continua sendo decidido só pelas Etapas enumeradas e pela regra de participação que já existe.

#### O universo do ato e a obsolescência

- **FR-3549**: Os Resultados da Etapa do desempate lidos pelo cálculo MUST entrar no universo gravado
  pelo ato, ao lado dos das Etapas enumeradas, com a mesma identidade completa.
- **FR-3550**: Mudança nos Resultados vigentes da Etapa do desempate dos participantes — Resultado novo,
  ou Resultado substituído por recurso deferido — MUST tornar a ordem emitida obsoleta, com a diferença
  descrita como mudança nos Resultados oficiais do universo, como já acontece com Etapa enumerada.
- **FR-3551**: A conferência da proveniência do ato no banco MUST aceitar, no universo, Resultados das
  Etapas enumeradas e das Etapas citadas por critério "maior pontuação numa Etapa" do mesmo marco, e
  MUST continuar recusando Resultado de qualquer outra Etapa.
- **FR-3552**: A reprodução do ato a partir do que ele gravou MUST devolver as mesmas posições do ato,
  para os atos emitidos depois desta feature e para os emitidos antes dela; a eliminação na Etapa do
  desempate MUST NOT virar eliminação na reprodução.
- **FR-3553**: Quando a Etapa do desempate ainda não tem Resultado de um participante, o cálculo MUST
  tratar o valor como ausente e aplicar o "quando o valor falta" publicado no critério, e a emissão
  MUST NOT ser impedida por isso. O Resultado que chegar depois obsoleta a ordem (FR-3550).
- **FR-3554**: A proveniência do desempate de cada posição MUST gravar, como valor do critério, a nota
  da Etapa do desempate que o cálculo comparou.

#### A prévia

- **FR-3555**: Os candidatos fictícios da prévia da classificação MUST receber nota na Etapa do desempate
  de todo critério que a cite, e a prévia MUST tratá-la como o cálculo oficial trata: desempata, não
  entra na nota final, não elimina.
- **FR-3556**: A equivalência entre a prévia e o caminho oficial (a FR-2233 da `094`) MUST ser verificada
  também para um marco que desempata por Etapa não enumerada.

#### O que não muda

- **FR-3557**: Marco cujos critérios só citam Etapas enumeradas ou fatos MUST produzir a mesma ordem, o
  mesmo universo e a mesma assinatura de confirmação que produzia antes desta feature.

### Key Entities

- **Etapa do desempate**: Etapa publicada citada por um critério "maior pontuação numa Etapa" de um marco
  que não a enumera. Contribui só com a pontuação, e só para o desempate.
- **Universo do ato de ordenação**: o que o ato declara ter lido — participantes e Resultados. Passa a
  incluir os Resultados da Etapa do desempate.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1073**: No cenário do achado (80, 80, 70; Entrevista 70 e 90), a ordem oficial põe o de 90 em 1º
  e o de 70 em 2º, e o teste do achado passa sem marca de falha esperada.
- **SC-1074**: Um candidato eliminado na Etapa do desempate, com nota nas Etapas enumeradas, tem posição
  na ordem do marco em 100% dos casos verificados.
- **SC-1075**: Um recurso deferido que substitui a nota da Etapa do desempate torna a ordem emitida
  obsoleta, e a sucessora reflete a nota corrigida.
- **SC-1076**: A prévia e o caminho oficial concordam em 100% dos casos da matriz de equivalência,
  acrescida do marco que desempata por Etapa não enumerada.
- **SC-1077**: Nenhum resultado oficial muda para marco sem critério por Etapa não enumerada: as tabelas
  absolutas da equivalência da `094` continuam passando sem edição.

## Assumptions

- O critério já publicado declara o "quando o valor falta" — a validação o exige desde a `015`.
- A Etapa do desempate é uma Etapa publicada do mesmo Edital; o cálculo lê o Resultado vigente dela como
  lê o das enumeradas, incluindo a âncora da versão que o fundamentou.
- O volume de Resultados lidos cresce no máximo uma Etapa por critério; o orçamento de consultas do
  cálculo não ganha consulta nova.

## Decisões

### D-001 — A Etapa do desempate contribui com a nota, e só com ela

É a decisão do usuário: desempatar sem entrar na nota final. A consequência da Etapa do desempate fica
de fora porque o edital que diz "desempata pela Entrevista" não diz "elimina quem foi eliminado na
Entrevista desta lista". Incluir os Resultados ingenuamente — como se a Etapa fosse enumerada — mudaria
quem é classificado, e essa mudança ninguém decidiu. A regra de progressão, que já exclui quem foi
eliminado antes da Etapa do marco, não é tocada.

### D-002 — O universo cita o que o cálculo leu, e a conferência no banco acompanha

O universo gravado é a proveniência: uma nota que decide a ordem e não está no universo é uma entrada que
nada desatualiza. Por isso os Resultados da Etapa do desempate entram nele, e a conferência no banco — que
hoje recusa Resultado de Etapa não enumerada — passa a aceitar os das Etapas citadas por critério do
mesmo marco. Ela continua recusando qualquer outra: afrouxar para "qualquer Etapa do Edital" desfaria o
que a `015` fechou.

### D-003 — Ato antigo de marco afetado fica obsoleto

Um ato emitido antes desta feature, num marco que desempata por Etapa não enumerada com Resultados já
consolidados nela, passa a aparecer obsoleto. Não é efeito colateral a evitar: o ato foi emitido com o
critério sem efeito, e a obsolescência é o caminho regular para o corrigir, com sucessora e motivo. A
reprodução desse ato continua íntegra (FR-3552), porque ela lê só o que o ato gravou.

### D-004 — A Etapa do desempate sem Resultado: emite-se

Acontece quando a Etapa do desempate vem depois da última Etapa enumerada — o caso típico: a ordem pela
Prova decide quem vai à Entrevista, e a Entrevista desempata. As duas respostas possíveis:

- **Emitir com o valor ausente.** Vale o "quando o valor falta" publicado; quando as notas chegarem, o
  universo muda e a ordem fica obsoleta (FR-3550), pedindo sucessora. Não trava quando a Etapa do
  desempate depende do corte desta mesma ordem.
- **Impedir a emissão até haver Resultado.** A ordem só sai com as notas; mas, se a Etapa do desempate
  só recebe quem o corte desta ordem manda, nenhuma das duas chega a acontecer.

**O usuário escolheu a primeira em 01/11/2026.** É também o que o domínio já faz com qualquer valor
ausente: ele é declarado no critério, e não inferido — e a emissão nunca esperou por Resultado.

### D-005 — A pertinência das decisões de recurso não muda

A providência a jusante, o recurso contra a publicação e as Etapas que o candidato acompanha continuam
ligados às Etapas **enumeradas** do marco. A correção de nota na Etapa do desempate chega a esta ordem
pela obsolescência (FR-3550), que é o caminho que já leva qualquer correção de Resultado a uma ordem.
Estender a pertinência é decisão institucional sobre recurso, e fica registrada em *Pendências*.

### D-006 — Na prévia, a nota fictícia do desempate acompanha as notas enumeradas

Os candidatos fictícios empatados de propósito (o trio que só os fatos separam, o par igual em tudo)
precisam continuar empatados até o critério que o caso exercita. Por isso a nota fictícia na Etapa do
desempate é derivada das notas fictícias das Etapas enumeradas: candidatos iguais nelas são iguais nela,
e os casos da `094` e da `095` continuam significando o que nomeiam.

## Pendências do usuário

- **D-005**: se uma providência a jusante determinada por recurso contra a nota da Etapa do desempate
  deve ser citada pela ordem do marco que só desempata por ela.
