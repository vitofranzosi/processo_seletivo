# Feature Specification: Desempate pela nota de Etapa que o marco não enumera

**Feature Branch**: `claude/114-desempate-por-etapa-nao-enumerada`, sobre a `main` em `9eaf75fb`

**Created**: 2026-11-01

**Status**: Draft. A direção foi decidida pelo usuário em 01/11/2026: corrigir no cálculo, e não
recusar o critério na validação. A Etapa do desempate ainda sem Resultado também foi decidida por ele
no mesmo dia (FR-3553, D-004). **Revista em 02/11/2026**, a pedido do usuário, sobre o PR aberto:
a pertinência dos recursos passou a seguir a dependência efetiva da ordem (D-005), a prévia ganhou
o caso que mostra a outra Etapa separando (FR-3558), e o percurso do corte que governa a Etapa do
desempate foi demonstrado de ponta a ponta, com o conflito registrado na D-007.

**A capacidade é genérica.** Um marco pode usar a nota de **qualquer** outra Etapa do Edital como
critério de desempate, mesmo que ela não componha a sua nota final. "Entrevista" é o exemplo do
achado e dos testes, e não uma regra: nada no cálculo, na conferência do banco ou na prévia
conhece o nome ou a ordem da Etapa citada.

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

Cobre também, desde a revisão de 02/11: a pertinência ao marco dos recursos, das reavaliações e
das providências sobre a nota que desempata (D-005); o caso demonstrativo da prévia (FR-3558); e o
percurso do corte que governa a própria Etapa do desempate (FR-3562, D-007).

**As três funções de uma Etapa ficam separadas.** Em relação a um marco, uma Etapa pode:

| Função | Quem a tem |
|---|---|
| compor a nota final | só as Etapas que o marco enumera |
| fornecer nota para o desempate | as enumeradas e as que um critério compara |
| determinar participação ou eliminação nesta ordem | só as enumeradas, pela regra de progressão que já existe |

Ser consultada para desempatar não dá, por si só, nenhuma das outras duas (FR-3547, FR-3548).

Fica fora:

- **a validação e a tela de configuração.** Nada passa a ser recusado nem oferecido de outro modo;
- **o que o candidato vê e quando pode recorrer da nota da Etapa do desempate** — a visibilidade do
  próprio Resultado e a janela recursal continuam ligadas aos marcos que **enumeram** a Etapa
  (D-005, pendência do usuário);
- **o critério por fato declarado**, que já funciona e não muda;
- **qualquer tratamento de atos emitidos antes desta feature.** O sistema não está em produção e não
  há acervo a preservar (D-003).

## Clarifications

### Session 2026-11-01

- Q: O que corrige o A11 — ler a nota da Etapa citada, ou recusar o critério? → A: Ler a nota. A Etapa
  desempata sem entrar na nota final (decisão do usuário, registrada no estudo).
- Q: Quando a Etapa do desempate ainda não tem Resultado de quem o critério precisa separar, emite-se
  com o valor ausente — valendo o "quando o valor falta" publicado — ou impede-se a emissão até haver
  Resultado? → A: Emite-se. Vale o "quando o valor falta" publicado; quando as notas chegarem, a ordem
  fica obsoleta e pede sucessora (D-004).

### Session 2026-11-02 (revisão do PR)

- Q: Os recursos sobre a nota que desempata seguram a definitiva da ordem que ela decide? → A: Sim. A
  pertinência ao marco segue a dependência efetiva da ordem — as Etapas enumeradas e as que um
  critério compara —, e não todas as Etapas do Edital (D-005, decisão do usuário no pedido de
  revisão).
- Q: Há tratamento especial para atos emitidos antes desta feature? → A: Não. O sistema não está em
  produção (D-003).

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

---

### User Story 5 — A disputa sobre a nota que desempata segura a definitiva (Priority: P1)

A nota da Entrevista de um dos empatados é contestada por recurso. Enquanto ele não é decidido, a
ordem do marco que desempata pela Entrevista não pode ser publicada como definitiva; o preliminar
continua possível. Se a decisão manda reavaliar a Entrevista, a definitiva espera a reavaliação; se
manda providência a jusante, a definitiva espera o ato que a cita.

**Why this priority**: a nota decide a ordem. Uma definitiva publicada com ela em disputa diria que
acabou o que não acabou — o mesmo motivo pelo qual o recurso contra a nota da Prova já a segurava.

**Independent Test**: emitir a ordem, interpor recurso contra o Resultado da Entrevista e aferir a
publicação definitiva; repetir com reavaliação determinada e com providência a jusante, emitindo o
ato que cita a providência.

**Acceptance Scenarios**:

1. **Given** a ordem emitida e um recurso admitido contra a nota da Entrevista, ainda sem decisão,
   **When** se afere a publicação definitiva, **Then** ela é impedida por recurso pendente, e a
   preliminar continua publicável.
2. **Given** uma reavaliação da Entrevista determinada e não cumprida, **When** se afere a definitiva,
   **Then** ela é impedida por reavaliação pendente.
3. **Given** uma providência a jusante determinada sobre a nota da Entrevista, **When** a tela de
   emissão abre, **Then** ela oferece citar a decisão; **and when** o ato sucessor a cita, **Then** o
   banco aceita a citação e a definitiva desse ato deixa de ser impedida pela providência.
4. **Given** o mesmo Edital **sem** o critério que compara a Entrevista, **When** há recurso pendente
   ou providência sobre a nota dela, **Then** a definitiva do marco não é impedida, e a citação da
   providência por ato deste marco continua recusada no banco.

---

### User Story 6 — A prévia mostra a outra Etapa separando os empatados (Priority: P2)

Quem configura um marco que desempata pela Entrevista escolhe, na prévia, o caso "Desempate pela
nota de outra Etapa". A tabela mostra dois candidatos com a mesma nota final, na última posição do
alvo, separados só pela nota da Entrevista; a explicação do empate mostra a pontuação combinada
igual e a Entrevista separando.

**Why this priority**: sem o caso, os empatados de propósito da prévia são iguais também na nota
fictícia da Entrevista (D-006), e nenhum caso mostra o critério fazendo o que o edital promete.

**Independent Test**: simular o caso, conferir as posições, a nota final e o critério que separou, e
gravar os mesmos candidatos pelo caminho oficial para comparar.

**Acceptance Scenarios**:

1. **Given** um marco que soma só a Prova e desempata pela Entrevista, **When** o caso é simulado,
   **Then** o par tem a mesma nota final, o da linha de baixo fica à frente, e quem separou é o
   critério da Entrevista.
2. **Given** um marco sem critério por Etapa que ele não some, **When** o seletor de candidatos é
   montado, **Then** o caso não é oferecido.
3. **Given** os candidatos do caso gravados pelo caminho normal, **When** a ordem oficial é calculada,
   **Then** ela coincide com a da prévia.

---

### User Story 7 — O corte da ordem governa a Etapa que a desempata (Priority: P2)

A ordem pela Prova decide, pelo corte, quem vai à Entrevista, e a Entrevista desempata essa mesma
ordem. O percurso inteiro funciona quando o empate fica dentro da faixa; quando atravessa a
fronteira, o sistema faz hoje o que a D-007 descreve, e a decisão sobre isso é do usuário.

**Why this priority**: é o caso típico do edital, e a sucessora emitida, sozinha, não prova que ele
funciona — é preciso saber quem continua alcançado pela faixa no fim.

**Independent Test**: percorrer ordem, corte, Entrevista, obsolescência, sucessora e geração
sucessora, perguntando a cada passo quem pode fazer a Entrevista.

**Acceptance Scenarios**:

1. **Given** alvo de dois e dois empatados dentro dele, **When** o percurso é seguido até a geração
   sucessora, **Then** os mesmos dois continuam alcançados, separados pela Entrevista, com a nota
   final da Prova, e nada fica obsoleto nem impedido.
2. **Given** alvo estrito e três empatados para duas posições, **When** o corte é pedido, **Then** ele
   é recusado; sem corte emitido a Entrevista recebe todos os habilitados, e depois das notas a
   sucessora e o corte saem.
3. **Given** alvo que admite excedente e três empatados para duas posições, **When** o percurso é
   seguido, **Then** os três fazem a Entrevista, e a geração sucessora alcança só dois (D-007).

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
- **Recurso contra a nota de Etapa que nenhum critério compara.** Não é pertinente ao marco: a
  definitiva não espera por ele (FR-3561).
- **Reabilitação por recurso sem nota na Etapa do desempate.** Não é pendência de reingresso: a
  reabilitação continua sendo conferida nas Etapas enumeradas, e a nota que falta no desempate vale
  o "quando o valor falta" (FR-3553).
- **O corte governa a própria Etapa do desempate.** É a US7 e a D-007.
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
- **FR-3552**: A reprodução do ato a partir do que ele gravou MUST devolver as mesmas posições do ato;
  a eliminação na Etapa do desempate MUST NOT virar eliminação na reprodução.
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

- **FR-3558**: A prévia MUST oferecer, só para marco que desempata pela nota de Etapa com nota que ele
  não enumera, um caso-limite em que dois candidatos iguais em tudo o que compõe a nota final e nos
  fatos ficam na última posição do alvo e são separados só pela nota dessa Etapa. A nota final dos
  dois MUST ser a mesma, e os casos que já existem MUST continuar significando o que nomeiam.

#### Os recursos sobre a nota que desempata

- **FR-3559**: Recurso pendente e reavaliação determinada e não cumprida sobre Resultado da Etapa do
  desempate MUST impedir a publicação definitiva da ordem do marco, como já impedem os das Etapas
  enumeradas; a preliminar MUST continuar publicável.
- **FR-3560**: Providência a jusante determinada em recurso contra Resultado da Etapa do desempate MUST
  ser pertinente ao marco: oferecida para citação na emissão, aceita pela conferência da citação no
  banco, e cumprida pelo ato do marco que a cita e é publicado.
- **FR-3561**: A pertinência ao marco MUST seguir a dependência efetiva da ordem — as Etapas
  enumeradas e as que um critério do marco compara —, e MUST NOT alcançar as demais Etapas do Edital.

#### O corte que governa a Etapa do desempate

- **FR-3562**: Quando o corte da ordem governa a própria Etapa do desempate, o percurso — ordem sem a
  nota, corte, avaliação só da faixa, ordem obsoleta, sucessora, corte obsoleto, geração sucessora —
  MUST ser possível sem regra nova, e o comportamento no empate que atravessa a fronteira MUST ser o
  descrito na D-007 até que o usuário decida sobre ele.

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
- **SC-1078**: Com recurso pendente, reavaliação pendente ou providência não cumprida sobre a nota que
  desempata, a definitiva é impedida em 100% dos casos verificados; sem o critério, nenhum deles a
  impede.
- **SC-1079**: No caso demonstrativo da prévia, o par tem a mesma nota final, é separado pela outra
  Etapa, e a ordem coincide com a oficial.
- **SC-1080**: No percurso do corte com o empate dentro da faixa, os mesmos participantes estão
  alcançados no fim, e nenhuma ordem ou faixa fica obsoleta.

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

### D-003 — Nenhum tratamento para atos anteriores à feature

**Revista em 02/11/2026.** A primeira redação discutia o ato emitido antes desta feature, que
apareceria obsoleto. O usuário esclareceu que o sistema não está em produção: não há acervo, e nada
se constrói para ele — nem migração de dados, nem compatibilidade, nem tratamento especial. Os
requisitos e os testes falam dos atos que o cálculo corrigido produz.

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

### D-005 — A pertinência dos recursos segue a dependência efetiva da ordem

**Revista em 02/11/2026, por decisão do usuário.** A primeira redação deixava a pertinência nas Etapas
enumeradas, e a revisão mostrou a lacuna: com recurso pendente contra a nota da Entrevista, a ordem
que ela desempata podia sair como **definitiva**, a reavaliação determinada da Entrevista não a
segurava, e a providência a jusante não tinha marco que a pudesse cumprir — a conferência da citação
no banco recusava o ato.

Agora as Etapas cujas decisões de recurso alcançam o marco são as que a ordem **lê**: as enumeradas
e as que um critério dele compara. É a mesma resposta que o cálculo usa, numa função só
(`etapas_que_a_ordem_le`), e a conferência da citação no banco a repete em SQL. As demais Etapas do
Edital ficam de fora: uma disputa sobre nota que não muda posição nenhuma não pode parar a definitiva
(FR-3561).

**Continua ligado às Etapas enumeradas**, e é pendência do usuário: o que o candidato **vê** do
próprio Resultado e **quando pode recorrer** dele. Exemplo concreto: um Edital cujo único marco soma a
Prova e desempata pela Entrevista, sem marco que enumere a Entrevista. Publicado o resultado, o
candidato vê a sua nota da Prova e pode recorrer dela; a da Entrevista — que decidiu a posição dele —
ele não vê no acompanhamento, e não tem janela para contestá-la isoladamente; resta o recurso contra
a publicação do marco. Abrir a nota e a janela é decisão sobre acesso e prazo, e não foi tomada aqui.
No caso típico, em que um marco seguinte enumera a Entrevista, a nota aparece e a janela abre pela
publicação dele.

### D-006 — Na prévia, a nota fictícia do desempate acompanha as notas enumeradas

**Complementada em 02/11/2026 pela FR-3558.** A regra abaixo continua valendo para todos os casos, e por
isso eles continuam significando o que nomeiam. Como consequência, nenhum deles mostrava o critério
separando alguém; o caso "Desempate pela nota de outra Etapa" existe para isso. Ele é oferecido só
quando o marco desempata por Etapa com nota que não enumera, como os casos de reserva só quando há
reservada, e planta o par sobre a classificação sem empate, para que seja o único empate da tabela.

Os candidatos fictícios empatados de propósito (o trio que só os fatos separam, o par igual em tudo)
precisam continuar empatados até o critério que o caso exercita. Por isso a nota fictícia na Etapa do
desempate é derivada das notas fictícias das Etapas enumeradas: candidatos iguais nelas são iguais nela,
e os casos da `094` e da `095` continuam significando o que nomeiam.

### D-007 — O corte que governa a Etapa do desempate: o conflito no empate da fronteira

Quando o corte desta ordem decide quem vai à Etapa que a desempata, a nota que separa os empatados só
existe depois do corte que os empatados decidem. Com o empate **dentro** da faixa, o percurso funciona
inteiro (US7, cenário 1). Com o empate **atravessando** a fronteira, há conflito entre duas regras
publicadas — "o corte decide quem vai à Entrevista" e "a Entrevista desempata esta ordem". O exemplo
dos testes: alvo de dois, Prova 80, 80 e 80.

- **Alvo estrito.** O corte é recusado: o sistema não escolhe entre empatados. Sem corte emitido, a
  regra dorme (a dormência da `014`), e a Entrevista recebe **todos** os habilitados. Os três são
  entrevistados, a sucessora os separa, o corte sai e o terceiro fica fora pela nota da Entrevista.
  Ninguém fica impedido; o custo é que a restrição "só a faixa vai à Entrevista" não se aplica a
  esses três.
- **Admite excedente.** O corte deixa os três entrarem, e os três fazem a Entrevista. A sucessora já
  não tem empate; a faixa fica obsoleta ("a ordem que este corte leu foi sucedida") e segura trabalho
  novo na Entrevista, e a geração sucessora aplica o alvo de dois à ordem nova: **o terceiro, que
  entrou pela regra do edital e foi entrevistado, sai da faixa**.
- **Admite excedente, com a sucessora emitida antes da última nota.** A tela oferece a sucessora assim
  que a primeira nota é consolidada. Com `ULTIMO_NO_CRITERIO`, o terceiro, ainda sem nota, fica atrás;
  a faixa obsoleta segura a Entrevista dele, e a geração sucessora o deixa fora: **ele fica impedido
  da Etapa cuja nota poderia tê-lo posto à frente**. Com `CRITERIO_NAO_SE_APLICA` a sucessora parcial
  mantém os três empatados, e o conflito só reaparece com todas as notas, como no item anterior.

**A decisão necessária**, que é do usuário: no empate que atravessa a fronteira de um corte que
governa a própria Etapa do desempate, a faixa da primeira geração — com o excedente que o edital
admitiu — vale até o fim daquela Etapa, ou a geração sucessora pode estreitá-la depois que a Etapa
desempatou? Nenhuma restrição genérica foi criada: os testes prendem o comportamento de hoje
(`test_desempate_pela_etapa_que_o_corte_governa.py`), para que a decisão, quando vier, mude um teste
nomeado.

## Pendências do usuário

- **D-005**: se o candidato passa a ver a própria nota da Etapa do desempate, e a poder recorrer
  dela, pela publicação do marco que só desempata por ela.
- **D-007**: no empate que atravessa a fronteira de um corte que governa a própria Etapa do
  desempate, se a geração sucessora pode estreitar a faixa que o excedente admitiu.
