# Feature Specification: As atribuições idênticas saem uma vez no documento do Edital

**Feature Branch**: `claude/064-atribuicoes-consolidadas`

**Created**: 2026-10-08

**Status**: Implementado — aguardando a revisão do responsável pelo produto e o merge da `063` (T034)

**Input**: a *Solicitação de análise de melhoria na geração de editais*, da elaboradora do Edital
90/2026, a auditoria de 08/10/2026 feita sobre a `main` `d7d3fe0b`, e os ajustes do responsável pelo
produto na mesma data — aqui citados como 1º a 7º, na ordem em que vieram:

1. os caracteres que o documento não representa (o "?" no lugar do marcador) são correção à parte;
2. só se consolidam conjuntos **integralmente idênticos**, preservando ordem, parágrafos e conteúdo;
   sem consolidação parcial, entidade nova, configuração administrativa nem mudança de modelagem;
3. as atribuições consolidadas vão ao **fim da seção de Perfis**, em subseções numeradas que nomeiam
   os **códigos** dos Perfis abrangidos; a numeração dos Perfis, das seções seguintes e das tabelas
   não muda;
4. para cada Perfil, as atribuições do documento — diretas ou pela remissão — equivalem integralmente
   às da versão composta;
5. documento composto depois da mudança, inclusive o de Retificação, sai no layout novo; os já
   gerados ficam como estão, sem alteração normativa implícita nem remissão quebrada;
6. spec curta, emendando os requisitos da `008` que tratam as atribuições como bloco de cada Perfil;
   nada de requisitos, modalidades, marcos ou outros blocos;
7. as quebras de linha rígidas do texto colado são registro à parte.

> **Faixa de identificadores.** Abre em **FR-1186** e **SC-457**; não há requisito de experiência.
> O teto medido em 08/10/2026 em todas as worktrees, com quatro dígitos, era de mil cento e oitenta e
> cinco para os requisitos funcionais e quatrocentos e cinquenta e seis para os critérios — da `063`,
> então em PR aberto; por isso o número vai por extenso. Esta spec não registra decisão própria com
> identificador: as que a governam são as sete acima, já tomadas.

**A frase que governa:**

> O documento diz uma vez o que é igual, e diz a cada Perfil onde está.

**E a frase que mantém o corte:**

> Esta feature muda a composição, e só ela. Nenhum dado, nenhuma tela, nenhum conteúdo publicado e
> nenhum documento já gerado muda; e só se junta o que é igual por inteiro.

---

## Por que esta feature existe

O Edital 90/2026 tem dez Perfis de Tutor presencial, um por polo, e o mesmo texto de atribuições em
todos — dezesseis itens, perto de meia página cada vez. O documento repete esse texto dez vezes, e
a prévia chega a 44 páginas. A elaboradora pediu o formato do Edital que ela escrevia em editor de
texto: as atividades da função **uma vez**, com a indicação dos Perfis a que se aplicam.

As atribuições são texto livre de cada Perfil. "Associar a outro Perfil" é, no sistema, duplicar o
Perfil ou colar o mesmo texto: o que existe são **cópias independentes**, e nada as liga. Por isso a
igualdade só pode ser a do texto — e por isso a consolidação é da composição do documento, e não do
cadastro.

**O que esta feature emenda na `008`.** O FR-016 da `008` diz que as atribuições "permanecem blocos
próprios" de cada Perfil, e o FR-021 da `008` as põe entre os sub-blocos de cada Perfil na cascata
de quebra de página. Com esta feature, o bloco próprio do Perfil cujas atribuições são idênticas às
de outro passa a ser a **remissão** (FR-1190), e o texto mora na subseção comum (FR-1189), que
obedece à mesma cascata (FR-1193).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem elabora vê, na prévia, as atribuições comuns uma vez só (Priority: P1)

A elaboradora compõe um Edital com vários Perfis de mesmo texto de atribuições e abre a prévia. Cada
Perfil traz, onde antes vinham as atribuições, a indicação do item em que elas estão; depois do
último Perfil, uma subseção numerada traz o texto uma vez, nomeando os códigos dos Perfis a que se
aplica. Perfis com texto próprio continuam como sempre.

**Why this priority**: é o pedido. Sem ela, o documento repete o mesmo texto tantas vezes quantos
forem os polos.

**Independent Test**: compor a prévia de um Edital com Perfis de texto idêntico e Perfis de texto
próprio, e ler onde cada texto aparece.

**Acceptance Scenarios**:

1. **Given** dois Perfis com o mesmo texto de atribuições, **When** a prévia é composta, **Then** o
   texto aparece uma vez, numa subseção ao fim da seção de Perfis cujo título nomeia os dois
   códigos, e cada Perfil remete ao número dela.
2. **Given** dois Perfis com textos diferentes, **When** a prévia é composta, **Then** nenhuma
   subseção comum é criada e cada Perfil traz o próprio texto, como antes.
3. **Given** dois Perfis cujos textos têm os mesmos itens menos um, **When** a prévia é composta,
   **Then** nada se consolida e os dois textos saem inteiros, cada um no seu Perfil.
4. **Given** dois Perfis de mesma denominação — "Tutor presencial" — e textos diferentes, **When** a
   prévia é composta, **Then** eles não se juntam.
5. **Given** um Edital de um Perfil só, **When** a prévia é composta, **Then** o documento é o de
   antes desta feature.

---

### User Story 2 — O candidato encontra as atribuições do seu Perfil, sem ambiguidade (Priority: P1)

Quem se candidata a um polo lê a subseção do seu Perfil, encontra "Atribuições" no lugar de sempre
e é mandado a um número de item; nesse item, o título diz que aquele texto vale para o seu código.

**Why this priority**: consolidar só serve se ninguém perder as próprias obrigações no caminho — e,
num ato administrativo, a remissão errada é pior que a repetição.

**Independent Test**: para cada Perfil do documento composto, reconstruir as atribuições pelo bloco
próprio ou seguindo a remissão, e comparar com as da versão.

**Acceptance Scenarios**:

1. **Given** um documento com subseções comuns, **When** se segue a remissão de qualquer Perfil,
   **Then** ela leva a uma subseção que existe no mesmo documento, cujo título nomeia o código desse
   Perfil, e cujo texto é integralmente o das atribuições dele.
2. **Given** o mesmo documento, **When** se lê qualquer subseção comum, **Then** todos os Perfis que
   ela nomeia remetem a ela, e nenhum outro remete.
3. **Given** um Edital cujo texto livre cita "item 11.2" ou "Tabela 3", **When** o documento é
   composto com a consolidação, **Then** esses números continuam apontando o mesmo conteúdo de antes.

---

### User Story 3 — O que já foi publicado não muda, e o que se publicar depois é coerente (Priority: P2)

Um Edital publicado antes desta feature conserva o documento que publicou. Se for retificado
depois, o documento consolidado da Retificação sai no layout novo, com as remissões coerentes com a
versão retificada.

**Why this priority**: a Publicação é imutável (Constituição, princípio II); o layout novo não pode
alcançar o passado, e a Retificação não pode herdar remissão que não vale mais.

**Independent Test**: publicar, retificar o texto de atribuições de um Perfil agrupado e comparar os
dois documentos guardados.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** esta feature entra, **Then** o documento guardado dessa
   Publicação continua com os mesmos bytes.
2. **Given** três Perfis agrupados e uma Retificação que altera o texto de um deles, **When** a
   Retificação é publicada, **Then** o documento dela agrupa só os dois que continuam iguais, e o
   terceiro traz o próprio texto.
3. **Given** a mesma Retificação, **When** se lê o que ela mudou, **Then** a alteração continua
   nomeando o Perfil e o campo, e nunca a subseção comum.

---

### Edge Cases

- **Diferença só de espaço.** Espaços repetidos entre palavras, espaço no fim da linha e linha em
  branco entre itens não impedem o agrupamento: o documento não os imprime (FR-1187).
- **Diferença de quebra de linha.** Impede. "Conhecer a proposta; contribuir nas atividades" numa
  linha e o mesmo texto partido em duas são dois parágrafos contra um no documento (FR-1187).
- **Diferença de pontuação, de maiúscula, de acento ou de símbolo.** Impede: é texto diferente, e o
  leitor o vê diferente.
- **Mesmos itens em outra ordem.** Impede. A ordem é parte do texto, e nada no sistema diz que ela é
  indiferente.
- **Subconjunto.** Perfil A com itens 1, 2 e 3 e Perfil B com 1 e 2: não se juntam (2º ajuste).
- **Texto vazio em vários Perfis.** Não forma grupo, e nenhum deles imprime "Atribuições", como hoje.
- **Mesmo texto, denominações diferentes.** Juntam-se: o título nomeia os códigos, e o texto vale
  para os dois. A denominação nunca entra na pergunta.
- **Dois grupos no mesmo Edital.** Duas subseções comuns, na ordem em que o primeiro Perfil de cada
  grupo aparece; cada Perfil remete à sua.
- **Todos os Perfis no mesmo grupo.** Uma subseção comum, que nomeia todos os códigos.
- **Código com espaço, num título longo.** "ADS - P06" não se parte entre duas linhas (FR-1189).
- **Código com vírgula ou com " e ".** "Tutor e Mediador" e "TEC" saem entre aspas, e o título não
  se lê como três Perfis (FR-1189).
- **Três ou mais Perfis no grupo e um Perfil de texto próprio entre eles.** O de texto próprio
  continua com o próprio bloco, no lugar dele; a numeração dos Perfis não muda.
- **Retificação que acrescenta um Perfil com o mesmo texto de um grupo.** Ele entra no grupo, no
  documento da Retificação.
- **Retificação que deixa um grupo com um Perfil só.** O grupo se desfaz e esse Perfil volta a
  trazer o próprio texto.
- **Caractere que o documento não representa.** A igualdade é a do texto registrado, e não a do que
  sai impresso (FR-1187): dois textos que diferem num símbolo que hoje sai como "?" nos dois **não**
  se juntam. A correção desse "?" é outra (1º ajuste).
- **Item partido em duas linhas por quebra rígida de texto colado.** Cada linha continua sendo um
  parágrafo, como hoje; dois textos com as mesmas quebras se juntam, com quebras diferentes não
  (7º ajuste).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1186**: Quando dois ou mais Perfis de um Edital têm atribuições idênticas (FR-1187), o
  documento MUST imprimir esse texto uma única vez, numa subseção comum (FR-1189), com os mesmos
  parágrafos, na mesma ordem e com o mesmo texto que sairiam no bloco de cada Perfil — sem
  acrescentar, suprimir nem reordenar nada.
- **FR-1187**: Atribuições são idênticas quando, no texto registrado na versão que se compõe, têm a
  mesma sequência de parágrafos e cada parágrafo tem as mesmas palavras na mesma ordem. **A quebra de
  linha é fronteira de parágrafo e MUST contar**: um item escrito numa linha e o mesmo item partido em
  duas são textos diferentes, porque o documento os imprime diferentes. Só três coisas MUST NOT
  contar, porque o documento não as distingue: a quantidade de espaço entre palavras, o espaço nas
  pontas de cada linha e a quantidade de linhas em branco entre dois parágrafos — uma ou várias,
  a fronteira é uma só. Letra, maiúscula, acento, pontuação, símbolo e a ordem dos parágrafos MUST
  contar. A comparação MUST ser feita sobre o texto registrado, e nunca sobre o que o documento
  imprime.
- **FR-1188**: Nada além da identidade do FR-1187 MUST agrupar Perfis: nem denominação, nem código,
  nem localidade, nem coincidência parcial — subconjunto, interseção ou os mesmos parágrafos em outra
  ordem. Texto vazio MUST NOT formar grupo. Edital de um Perfil só MUST NOT ter subseção comum.
- **FR-1189**: Cada grupo MUST ter uma subseção comum própria, posta depois do último Perfil, dentro
  da mesma seção, numerada em continuação às subseções dos Perfis — num Edital cuja seção de Perfis é
  a 4 e tem dez Perfis, a primeira é a 4.11. As subseções comuns MUST seguir a ordem em que o
  primeiro Perfil de cada grupo aparece no documento. O título MUST nomear todos os códigos dos
  Perfis do grupo, e só eles, na ordem do documento — *"Atribuições comuns aos Perfis ADS - ALE e
  ADS – BGU"* —, e MUST NOT usar a denominação. Quando o título ocupa mais de uma linha, a quebra
  MUST cair entre dois códigos, e nunca dentro de um. Quando algum código do grupo contém a vírgula
  ou o " e " da enumeração, todos os códigos do grupo MUST ir entre aspas — *"Atribuições comuns aos
  Perfis “Tutor e Mediador” e “TEC”"* —, para que o título não se leia como outra lista.
- **FR-1190**: Cada Perfil agrupado MUST trazer, no lugar e na posição do seu bloco de atribuições,
  o rótulo "Atribuições" seguido da remissão ao número da sua subseção comum — *"as descritas no item
  4.11."* —, e nenhum outro texto de atribuições. Perfil não agrupado MUST continuar trazendo o
  próprio bloco, como antes desta feature.
- **FR-1191**: Para cada Perfil, as atribuições aplicáveis no documento — as do próprio bloco ou as
  da subseção a que ele remete — MUST ser integralmente equivalentes, na forma do FR-1187, às desse
  Perfil na versão composta: os mesmos parágrafos, na mesma ordem, sem nenhum acrescentado, omitido
  ou trocado. Perfil com atribuições MUST ter exatamente uma fonte delas no documento; cada subseção
  comum MUST ser objeto de remissão de todos os Perfis que o título dela nomeia, e de nenhum outro; e
  toda remissão MUST apontar subseção do mesmo documento.
- **FR-1192**: Para a mesma versão, o número de cada subseção de Perfil, o número de cada seção do
  documento — inclusive o que as telas de composição, Revisão e Retificação mostram — e a numeração
  das tabelas MUST ser os mesmos com e sem a consolidação. A subseção comum MUST NOT conter tabela.
- **FR-1193**: A subseção comum MUST obedecer à paginação que a `008` dá ao Perfil (FR-020, FR-021 e
  FR-022 da `008`): título nunca sozinho no fim da página; inteira na página seguinte quando couber
  nela; quebrada entre parágrafos quando não couber. A remissão MUST ser parte do bloco do Perfil.
- **FR-1194**: A prévia e o documento publicado MUST consolidar do mesmo modo, e a marca de prévia
  MUST continuar sem alterar as quebras de página (FR-042 da `008`). O documento de Edital de um Perfil
  só MUST sair com os mesmos bytes de antes desta feature.
- **FR-1195**: A consolidação MUST existir só na composição do documento. Ela MUST NOT alterar o
  cadastro dos Perfis, o conteúdo da versão, a impressão digital dela, o conteúdo publicado, as telas
  de composição, Revisão e Retificação, nem o portal — onde o candidato continua lendo as atribuições
  dentro do próprio Perfil.
- **FR-1196**: Documento já gerado — de Publicação original ou de Retificação — MUST NOT ser
  regerado nem alterado. Todo documento composto depois desta feature, inclusive o documento
  consolidado de Retificação de Edital publicado antes dela, MUST sair no layout novo, agrupando pela
  versão que ele compõe. O que a Retificação mudou MUST continuar dito por Perfil e campo, e nenhuma
  remissão MUST apontar número de outro documento.
- **FR-1197**: Requisitos, modalidades, fundamentos, quadros de vagas, marcos de classificação e os
  demais blocos do Perfil MUST continuar impressos em cada Perfil, como antes desta feature.

### Key Entities

- **Perfil de Vaga**: tem código único no Edital, denominação e atribuições em texto livre. Nada
  nele muda.
- **Documento do Edital**: a prévia e o documento publicado, compostos da mesma versão pela mesma
  regra; o publicado é guardado e não se regera.
- **Subseção comum de atribuições**: existe só no documento. Não é registrada, não tem identidade e
  não sobrevive fora da composição que a produziu.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-457**: Num Edital com dez Perfis de mesmo texto de atribuições, como o 90/2026, o texto sai
  **uma** vez no documento, e não dez; cada um dos dez Perfis traz uma remissão, e todas apontam o
  mesmo item.
- **SC-458**: Em todo cenário de teste da feature, reconstruir as atribuições de cada Perfil a partir
  do documento — pelo bloco próprio ou pela remissão — devolve exatamente as da versão; nenhum Perfil
  fica sem fonte ou com duas.
- **SC-459**: Para a mesma versão, as listas de números de subseção de Perfil, de números de seção e
  de legendas de tabela são idênticas com e sem a consolidação.
- **SC-460**: O documento de Edital de um Perfil só continua com os mesmos bytes; num cenário com
  subseção comum, a prévia e o publicado quebram nas mesmas páginas.
- **SC-461**: Os documentos guardados de Publicações anteriores continuam com os mesmos bytes, e a
  suíte completa contra PostgreSQL passa.

### O que esta feature não cobre, deliberadamente

- A troca dos caracteres que o documento não representa por "?" (1º ajuste) — correção própria, que
  decide também o que fazer com o marcador colado do editor de texto.
- As quebras de linha rígidas do texto colado, que partem um item em dois parágrafos (7º ajuste) —
  registro próprio; a dica do campo, sozinha, não é solução.
- Consolidação parcial, agrupamento manual, configuração por Edital ou entidade de atribuição
  (2º ajuste).
- Requisitos, modalidades, fundamentos, marcos e qualquer outro bloco repetido entre Perfis
  (6º ajuste).
- A exibição das atribuições no portal e na Revisão, que juntam os parágrafos num bloco corrido.

---

## Assumptions

- O código do Perfil é único no Edital, e por isso basta para nomear, sem ambiguidade, os Perfis de
  um grupo.
- Os Perfis saem no documento na ordem do código, como hoje; é essa a "ordem do documento" dos
  FR-1189 e FR-1190.
- Quem compõe o documento é uma só função, chamada pela prévia, pela Publicação e pela Retificação;
  a consolidação vale nas três sem caminho próprio.
- O documento do Edital é só PDF; não há outra exportação a manter coerente.
