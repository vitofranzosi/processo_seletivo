# Feature Specification: Alcance declarável — a Modalidade que atravessa Perfis, e a Etapa que não vale para todos

**Feature Branch**: `claude/spec-039-alcance`

**Created**: 2026-09-19

**Status**: Draft

**Input**: A conversa de generalidade de 19/09 com quem governa o produto: *"o sistema deve ser genérico o suficiente para permitir editais tanto de alunos quanto de bolsistas que vão atuar no Ifes"*, *"permitindo que o operador possa configurar o edital se assim desejar"*.

## O problema, em uma frase

**O Perfil de Vaga é um muro.** A Modalidade de Concorrência não consegue subir acima dele, e a Etapa
de Avaliação não consegue entrar nele. As duas faltas são a mesma correção aplicada a dois objetos —
**dar alcance declarável ao que hoje tem alcance fixo** —, e é por isso que vêm juntas.

**As duas aparecem idênticas nas duas famílias de Edital**, e é esse o teste que as separa de
particularização:

| A falta | No Edital de bolsista | No Edital de aluno |
|---|---|---|
| A Modalidade não existe acima do Perfil | o laudo de PcD vale para um polo só | a autodeclaração de cotista vale para **um curso** só, quando a lei vale para o Edital inteiro |
| A Etapa não tem alcance | dois Perfis não podem ter fichas de pontuação diferentes | dois cursos não podem ter provas diferentes — um com redação, outro sem |

Particularização apareceria em **uma** família. Estas aparecem nas duas, com a mesma forma.

**O padrão não muda.** Quem tem Edital simples continua declarando como declara hoje: campo novo
vazio significa "vale para todos". É acréscimo de liberdade, não de obrigação.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A Modalidade que atravessa Perfis (Priority: P1)

O operador declara um Edital com quatro cursos. A Lei 12.711 vale para o Edital inteiro, e o
candidato cotista precisa entregar a autodeclaração **concorra ele ao curso que for**. Hoje o
operador só consegue dizer "todos os candidatos" ou "a cota do curso X" — e escreve a mesma
exigência quatro vezes, uma por curso, ou a impõe a quem não é cotista.

Ele passa a poder declarar que as Modalidades de mesmo recorte, nos quatro Perfis, são **a mesma
família de concorrência** — e exigir o documento **da família**, uma vez só.

**Why this priority**: é a mais barata das duas e a que aparece em todo Edital com reserva legal, que
são quase todos. Entrega valor sozinha.

**Independent Test**: declarar um Edital com dois Perfis, cada um com sua Modalidade de cota; declarar
que as duas são a mesma família; exigir um Documento da família; conferir que o candidato de
qualquer dos dois Perfis vê a exigência e que o candidato de ampla concorrência não vê.

**Acceptance Scenarios**:

1. **Given** um Edital com dois Perfis, cada um declarando uma Modalidade de cota, **When** o operador declara que as duas são a mesma família e exige um Documento dessa família, **Then** a exigência alcança os candidatos dos dois Perfis que concorrem por ela, e nenhum outro.
2. **Given** o mesmo Edital, **When** o operador exige um Documento sem restringir Perfil nem família, **Then** a exigência alcança todos os candidatos, como hoje.
3. **Given** um Edital cujo Quadro de Vagas reparte vagas por Modalidade, **When** uma família é declarada, **Then** o Quadro continua declarando vagas por Perfil e por Modalidade **do Perfil**, sem linha nova e sem vaga nova.

---

### User Story 2 — A Etapa que não vale para todos (Priority: P2)

O operador declara um Edital com dois cursos que avaliam de formas diferentes: um exige redação, o
outro não. Hoje isso exige **dois Editais**, porque toda Etapa declarada no Edital vale para todos os
seus candidatos — eles são distribuídos para ela, avaliados nela e eliminados por ela.

Ele passa a poder declarar **a que Perfis cada Etapa se aplica**. Quem está fora do alcance não é
distribuído, não é avaliado e não é barrado por ela.

**Why this priority**: é a generalidade que falta de verdade — sem ela, um Edital com duas formas de
avaliar é indeclarável. Mas custa mais do que a US1, porque muda *quem é avaliado*, e por isso vem
depois.

**Independent Test**: declarar um Edital com dois Perfis e três Etapas, uma delas restrita a um Perfil;
inscrever candidatos nos dois Perfis; conferir que a distribuição da Etapa restrita só alcança um
deles, e que o candidato do outro Perfil chega à Etapa seguinte sem ser barrado.

**Acceptance Scenarios**:

1. **Given** um Edital com dois Perfis e uma Etapa cujo alcance nomeia apenas o Perfil A, **When** a Etapa é distribuída, **Then** apenas inscrições do Perfil A entram na distribuição.
2. **Given** a mesma Etapa, eliminatória, **When** ela produz Resultado, **Then** nenhum candidato do Perfil B é eliminado por ela nem barrado pela porta da Etapa seguinte.
3. **Given** um Edital em que o Marco Classificatório de um Perfil enumera uma Etapa fora do alcance desse Perfil, **When** o Edital é publicado, **Then** a publicação é recusada com achado impeditivo que nomeia o Perfil, a Etapa e o Marco.
4. **Given** uma Etapa sem alcance declarado, **When** ela é distribuída, **Then** ela alcança todos os Perfis — o comportamento de hoje.

---

### User Story 3 — O Edital de ontem continua dizendo o mesmo (Priority: P3)

Quem lê um Edital publicado antes desta mudança — candidato, comissão, auditoria — precisa ler
exatamente o que ele afirmava no dia da publicação. Nenhum campo novo pode acrescentar afirmação que
o Edital não fez.

**Why this priority**: é garantia constitucional, não conveniência. Mas é verificável sozinha e não
bloqueia as outras duas.

**Independent Test**: tomar Editais publicados antes do degrau, elevá-los, e conferir que a Etapa sem
alcance vale para todos os Perfis e que cada Modalidade é família de si mesma — as duas leituras que
o conteúdo já afirmava por ausência.

**Acceptance Scenarios**:

1. **Given** um Edital publicado antes desta feature, **When** seu conteúdo é lido, **Then** cada Etapa alcança todos os Perfis e cada Modalidade pertence apenas a si, sem divergência em relação à leitura anterior.
2. **Given** um operador que não precisa de nenhuma das duas liberdades, **When** ele declara um Edital do começo ao fim, **Then** ele não encontra campo obrigatório novo nem passo novo.

---

### Edge Cases

- **Etapa com alcance vazio**: declarar que uma Etapa não vale para Perfil nenhum é declarar uma Etapa que ninguém faz. É recusado na publicação — alcance vazio e alcance ausente não podem ser duas grafias da mesma coisa.
- **Retificação que acrescenta Perfil**: um Perfil acrescentado depois passa a fazer as Etapas **sem alcance declarado**, e não as restritas. É por isso que o alcance é lista de inclusão e não de exclusão.
- **Retificação que remove Perfil do alcance de Etapa já avaliada**: recusada. Avaliação produzida não se apaga, e estreitar o alcance depois do Resultado faria o Edital afirmar que um trabalho realizado não existiu.
- **Família declarada por um Perfil só**: legítima. É o Edital de Perfil único, e a família coincide com a Modalidade.
- **Documento que restringe Perfil e família ao mesmo tempo**: legítimo e mais estreito que os dois — alcança quem está naquele Perfil **e** concorre por aquela família.
- **Ampla concorrência**: continua sendo o recorte **sem Modalidade**. Declarar família não cria Modalidade, não cria linha no Quadro e não muda o que o sorteio consulta.
- **Candidato fora do alcance de toda Etapa classificatória do seu Perfil**: o Perfil ficaria sem ordem possível. Recusado na publicação, pelo mesmo motivo do alcance vazio.

## Requirements *(mandatory)*

### Functional Requirements

**A Modalidade que atravessa Perfis (US1)**

- **FR-568**: O Edital MUST poder declarar que Modalidades de Concorrência de Perfis diferentes pertencem à mesma **família de concorrência**, sem que a identidade da Modalidade deixe de ser do Perfil.
- **FR-569**: Um Documento Exigido MUST poder restringir-se a uma família, alcançando os candidatos de todos os Perfis que a declaram.
- **FR-570**: A família MUST NOT alterar o Quadro de Vagas: a linha continua sendo do Perfil e continua apontando a Modalidade daquele Perfil.
- **FR-571**: A ampla concorrência MUST continuar sendo o recorte sem Modalidade declarada; nenhuma família pode criar Modalidade, linha ou vaga.

**A Etapa que não vale para todos (US2)**

- **FR-572**: Uma Etapa de Avaliação MUST poder declarar a quais Perfis se aplica. Alcance **ausente** significa **todos os Perfis**.
- **FR-573**: Inscrição de Perfil fora do alcance de uma Etapa MUST NOT ser distribuída para ela nem avaliada nela.
- **FR-574**: Etapa fora do alcance de um Perfil MUST NOT eliminar candidato desse Perfil nem condicionar sua entrada na Etapa seguinte.
- **FR-575**: O sistema MUST recusar a publicação quando o Marco Classificatório de um Perfil enumerar Etapa fora do alcance desse Perfil, nomeando Perfil, Etapa e Marco.
- **FR-576**: O sistema MUST recusar a publicação de Etapa cujo alcance declarado esteja vazio, e de Perfil que não alcance Etapa classificatória alguma.

**Continuidade (US3)**

- **FR-577**: Conteúdo publicado antes desta feature MUST continuar afirmando exatamente o que afirmava: Etapa sem alcance vale para todos os Perfis, e cada Modalidade é família de si mesma. A elevação afirma apenas o que a ausência já dizia.
- **FR-578**: Declarar um Edital sem usar nenhuma das duas liberdades MUST NOT exigir passo, campo obrigatório ou decisão nova.

**Transversais**

- **FR-579**: Esta feature MUST NOT criar capacidade de autorização nova; quem declara alcance é quem já declara Etapa, Modalidade e Documento Exigido.
- **FR-580**: Alcance de Etapa e família de Modalidade MUST ser retificáveis, e a Retificação que estreita o alcance de Etapa que já produziu Resultado MUST ser recusada.

### Key Entities

- **Família de concorrência**: o recorte que um conjunto de Modalidades de Perfis diferentes compartilha — "cotista", "pessoa com deficiência". Não tem vagas, não entra no Quadro e não é declarada pelo candidato: quem o candidato escolhe continua sendo a Modalidade do seu Perfil.
- **Alcance da Etapa**: os Perfis a que uma Etapa se aplica. Ausente significa todos. É lista de inclusão, para que Perfil acrescentado depois entre nas Etapas gerais e não nas restritas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-201**: Um Edital com quatro Perfis e uma exigência documental de cota é declarável escrevendo a exigência **uma vez**, contra quatro hoje.
- **SC-202**: Um Edital em que dois Perfis são avaliados de formas diferentes é declarável como **um** Edital, contra dois hoje.
- **SC-203**: Nenhum Edital já publicado muda de sentido: a leitura do conteúdo elevado é idêntica à leitura anterior, em todos eles.
- **SC-204**: O operador que não usa nenhuma das duas liberdades percorre a declaração do Edital com o mesmo número de decisões obrigatórias de hoje.
- **SC-205**: Candidato fora do alcance de uma Etapa não aparece na distribuição dela, não recebe Resultado dela e não é barrado pela Etapa seguinte por causa dela.

### Garantias de interface

- **UX-067**: O cartão da Etapa exibe o alcance declarado e, quando não há alcance, exibe que ela vale para todos os Perfis — a ausência é afirmação visível, não campo em branco.
- **UX-068**: O cartão do Documento Exigido oferece a família como alcance, com rótulo que nomeia o recorte e não um Perfil — de modo que "cotista" seja escolhível sem que o operador escolha o curso de alguém.

## Decisões

### D-001 — A família é atributo declarado na Modalidade, e não objeto novo no topo

Mover a Modalidade para o nível do Edital quebraria a linha do Quadro de Vagas, que é do Perfil e aponta a Modalidade do Perfil, e mexeria na grafia da ampla concorrência — o recorte sem Modalidade, que é o que a apuração consulta. A identidade continua sendo do Perfil; o que passa a existir é o **nome do recorte compartilhado**.
### D-002 — O alcance da Etapa é lista de Perfis incluídos, e a ausência significa todos

Lista de exclusão mudaria de sentido quando uma Retificação acrescentasse Perfil, e a ausência tem de significar "todos" porque é isso que todo Edital publicado até hoje afirma. Segue o precedente do Documento Exigido, que já é coleção de topo com Perfil anulável.
### D-003 — Alcance e família são retificáveis, mas não para trás

Estreitar o alcance de Etapa que já produziu Resultado é recusado: avaliação realizada não se apaga, e o Edital não pode passar a afirmar que ela não deveria ter existido.

## Assumptions

- Medido em 19/09/2026 contra a `main` `4b00002`, e a confirmar no Phase 0: a Etapa vale hoje para **todos** os candidatos submetidos do Edital, estreitada apenas pela progressão — quem foi eliminado numa Etapa anterior —, nunca pelo Perfil.
- Medido na mesma data: a **classificação já é por Perfil**. O Marco Classificatório mora dentro do Perfil e enumera as Etapas que entram na pontuação, e a soma dos pesos é a das Etapas que **aquele** Marco enumera. Portanto esta feature **não** muda a combinação de notas; ela muda quem é avaliado.
- Medido na mesma data: cada Modalidade pertence a um Perfil e seu código é único **dentro** do Perfil — de modo que o recorte compartilhado já se repete de fato entre os Perfis, sem estatuto declarado.
- Medido na mesma data: o Documento Exigido já admite restringir-se a Perfil ou a Modalidade, e já aceita Modalidade sem Perfil. A falta não é o campo: é não haver objeto que signifique a família.
- A faixa desta spec abre em **FR-568**, **SC-201** e **UX-067**. Teto medido em 19/09/2026 na `main` e em todas as worktrees: FR-567 / SC-200 / UX-066.
- Esta feature acrescenta declaração nova ao conteúdo publicado, e portanto uma versão nova dele. **A versão não é o custo**: o custo da US2 é quem é avaliado, distribuído e progredido.

## Fora de escopo

Cada um destes tem spec própria e não entra aqui: a Retificação que acrescenta Modalidade (D-G5); as
sete recusas com a fronteira 403/404 (D-G2); a validação cruzada entre fontes normativas (E-4); o
renderizador normativo único das telas de ato (E-3); a organização do trabalho por Perfil ou polo
(ACH-60); a FR-461 impeditiva (D-G1); a exigência de ocorrência externa do sorteio (D-G3); a
densidade da Classificação (ACH-10/05); e o **vocabulário** — renomear "Perfil de Vaga" para um termo
que sirva igualmente ao Edital de aluno é discussão real, e é outra spec.

## Se não couber

Se o Phase 0 medir que a **US2 não cabe no teto proporcional** — porque o alcance da Etapa alcança
mais lugares de decisão do que o plano comporta —, ela sai desta feature **com registro**, e a
entrega é a US1 mais a US3. É o padrão que a `038` firmou: preferir uma spec que entrega o que
prometeu a uma que promete duas liberdades e entrega uma e meia. A decisão é da medição.
