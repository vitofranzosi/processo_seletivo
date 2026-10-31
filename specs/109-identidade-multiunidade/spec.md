# Feature Specification: Identidade institucional preparada para mais de uma unidade

**Feature Branch**: `claude/109-identidade-multiunidade`

**Created**: 2026-10-31

**Status**: Implementada nesta branch; merge não autorizado.

**Input**: o pedido de 31/10/2026, "GPS — Evolução da identificação institucional e preparação
multiunidade", e a orientação complementar do mesmo dia: o `unidades.json` e o comando
`sincronizar_unidades` continuam sendo a fonte oficial do cadastro de unidades, sem mecanismo
paralelo, até uma revisão arquitetural específica.

> **Faixa de identificadores.** Esta spec abre em **FR-3201** e **SC-1031**. O teto medido em
> 31/10/2026 na `main` e nas branches abertas é o requisito três mil cento e setenta e um e o
> critério mil e vinte e seis, os dois da `108` (em preparação noutra sessão). **Nenhum `UX-` é
> aberto aqui.** As decisões técnicas reiniciam em `D-001` e moram no `research.md`; as perguntas
> ao usuário são `P-`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-1611 da `072`"); decisão de outra feature pelo assunto e pelo número por extenso.

---

## Por que esta feature existe

A `060` tirou do compositor do PDF o nome, o cabeçalho e o local do Cefor e os pôs num registro de
Unidades. A `106` e a `107` deram à gestão vínculos por unidade, unidade ativa e troca de unidade.
Mas a **moldura** das telas e a **assinatura** das mensagens continuam dizendo "Cefor/Ifes" no
código, e o canal de atendimento ao candidato é uma configuração só para a implantação inteira.
Com um segundo campus, quem atua nele leria "Cefor/Ifes" no título de toda página, e o candidato
do campus receberia mensagem assinada pelo Cefor.

O [inventário](inventario.md) classifica cada ocorrência. O resultado orienta tudo abaixo: nenhuma
regra de negócio depende da string `cefor`; o que depende é a **identidade** — e ela já tem de
onde vir.

### O que esta spec cobre, e o que fica fora

**Entra:**

- a identificação da unidade nas molduras da gestão, do portal, da página de acesso e da 404, e
  nas frases da gestão que dizem a quem pedir acesso;
- a assinatura das mensagens ao candidato;
- o canal de atendimento por unidade, como atributo opcional do registro que já existe, com o canal
  global como recaída;
- testes com duas unidades, o Cefor e o `campus-a` fictício;
- o comentário desatualizado acima do `PAPEIS` e o documento separado das pendências da auditoria
  de 30/10.

**Fica fora, de propósito:**

- a fonte do cadastro: o `unidades.json` e o `sincronizar_unidades` não mudam de papel, nem ganham
  concorrente (orientação de 31/10);
- tela de unidades, tela de configuração, configuração genérica;
- correio por unidade — servidor, remetente, credenciais;
- cadastro de qualquer outra unidade;
- o PDF, que já lê a unidade do ato desde a `060`;
- papéis, permissões, regras de autorização, regras dos Editais;
- os textos explicativos e os valores históricos ou de contrato que o inventário classificou como
  tais.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem atua numa unidade vê a própria unidade na gestão (Priority: P1)

Uma servidora do campus fictício entra na gestão e atua nele. O título das páginas, a marca da
barra e a frase que diz a quem pedir acesso falam do campus, e não do Cefor. Trocando a unidade
ativa para o Cefor, as mesmas telas passam a dizer Cefor.

**Why this priority**: é onde o "Cefor/Ifes" fixo mais aparece, e onde a confusão de contexto faria
alguém agir na unidade errada.

**Independent Test**: com as duas unidades registradas, identificar-se em cada uma e ler o título,
a marca e a frase de acesso.

**Acceptance Scenarios**:

1. **Given** um ator do `campus-a`, **When** abre qualquer página da gestão, **Then** o título
   termina em "Campus A/Ifes" e a marca da barra diz o mesmo.
2. **Given** o mesmo ator sem papel, **When** abre a lista, **Then** a orientação diz a quem
   administra o sistema no campus.
3. **Given** um ator do Cefor pelo seletor de demonstração, **When** abre as mesmas telas,
   **Then** elas dizem exatamente o que diziam antes desta feature.

---

### User Story 2 — O candidato lê a unidade do Edital, e não a de quem está logado (Priority: P1)

O portal lista os Editais de todas as unidades. A página pública de uma seleção diz a unidade que
publicou o ato. Um operador do campus que abre o portal no mesmo navegador não muda o que o
candidato veria.

**Why this priority**: o portal é público, e a identidade dele não pode depender de sessão
administrativa.

**Independent Test**: publicar um Edital no Cefor e outro no campus; abrir a página pública de cada
um, com e sem um operador da gestão identificado no mesmo navegador.

**Acceptance Scenarios**:

1. **Given** um Edital publicado pelo campus, **When** o candidato abre a página pública da seleção,
   **Then** a moldura diz "Campus A/Ifes".
2. **Given** um operador do campus identificado na gestão, **When** ele abre a página pública de um
   Edital do Cefor, **Then** a moldura diz "Cefor/Ifes".
3. **Given** duas unidades ativas, **When** alguém abre a vitrine, a página de acesso ou um endereço
   que não abre, **Then** a moldura diz "Ifes" e não escolhe uma das unidades.
4. **Given** só o Cefor ativo, **When** alguém abre essas mesmas páginas, **Then** elas dizem
   "Cefor/Ifes", como hoje.

---

### User Story 3 — As mensagens assinam pela unidade do Edital e apontam o atendimento dela (Priority: P1)

O aviso, a convocação e o comprovante de inscrição de um Edital do campus saem assinados pelo campus
e apontam o canal de atendimento declarado para ele. O código de acesso, que é da conta e não de um
Edital, sai com a identificação da implantação e o canal global.

**Why this priority**: a mensagem é o que o candidato guarda, e o canal errado manda a dúvida para a
unidade errada.

**Independent Test**: declarar um canal para o campus no registro; confirmar um aviso, comunicar uma
convocação e enviar uma inscrição em cada unidade; ler o que saiu.

**Acceptance Scenarios**:

1. **Given** o campus com canal declarado, **When** um aviso de um Edital do campus é confirmado,
   **Then** o rodapé assina "Campus A/Ifes — Seleções" e diz "fale com" o canal do campus.
2. **Given** o Cefor sem canal no registro e `PORTAL_ATENDIMENTO` preenchido, **When** um aviso de
   um Edital do Cefor é confirmado, **Then** o rodapé é o de hoje, com o canal global.
3. **Given** um aviso já confirmado, **When** o canal ou a sigla da unidade mudam no registro,
   **Then** o texto que o aviso guarda não muda.
4. **Given** um candidato que pede o código de acesso, **When** a mensagem sai, **Then** ela diz a
   identificação da implantação, e nunca a unidade de um Edital.

---

### User Story 4 — Os documentos publicados não mudam com o registro (Priority: P2)

Renomear a unidade ou mudar o canal dela não reescreve o PDF publicado, o comprovante nem a página
pública de uma seleção já publicada: eles dizem a unidade que o ato registrou.

**Independent Test**: publicar no campus, mudar a sigla e o canal no registro, e comparar o PDF e o
comprovante com o de antes.

**Acceptance Scenarios**:

1. **Given** um Edital publicado no campus, **When** a sigla do campus muda no registro, **Then** o
   PDF publicado é o mesmo, byte a byte, e a página pública continua dizendo a sigla do ato.

---

### User Story 5 — Um campus novo entra pelo registro, sem mudar código (Priority: P2)

A TI acrescenta uma unidade ao `unidades.json`, com ou sem canal, e roda o comando de sempre. A
marca, a assinatura e o canal passam a valer sem nenhuma linha de código nova.

**Independent Test**: os testes desta feature registram o campus só pelo registro, e nenhum deles
muda código-fonte para fazê-lo.

**Acceptance Scenarios**:

1. **Given** o arquivo com uma entrada nova que declara `atendimento`, **When** a sincronização
   roda, **Then** a unidade nasce com o canal, e a trilha registra o canal entre os campos.
2. **Given** o arquivo do Cefor sem `atendimento`, **When** a sincronização roda, **Then** ela relata
   o Cefor sem mudança.

---

### Edge Cases

- **Escopo sem unidade registrada.** A identificação é só a do Ifes, sem sigla de unidade. Não há
  recaída no Cefor.
- **O escopo da administração institucional** (o da `106`) não é unidade: a gestão diz "Ifes".
- **Nenhuma unidade ativa, ou mais de uma**: a implantação é só o Ifes.
- **Unidade desativada** com Edital em curso: a página e as mensagens daquele Edital continuam com a
  unidade dele; a moldura das superfícies globais deixa de contá-la entre as ativas.
- **Publicação anterior à `060`**, sem unidade gravada: a página pública recai na unidade do
  registro pelo escopo do Edital — o que o comprovante já faz com o vazio.
- **Canal declarado vazio ou em branco** no arquivo: recusado na sincronização; para não ter canal,
  a entrada omite o campo.
- **Canal com quebra de linha**: recusado — ele entra no meio de uma frase da mensagem.
- **A 404 de um Edital de outra unidade** não diz a unidade do Edital: diria que ele existe.
- **Sessão da gestão e sessão do candidato no mesmo navegador**: o portal ignora a da gestão.

## Requirements *(mandatory)*

### Functional Requirements

#### A identificação

- **FR-3201**: A identificação de uma unidade MUST sair do registro de Unidades e ser composta da
  sigla da unidade e da sigla do Ifes ("Cefor/Ifes"). Um escopo sem unidade registrada MUST ter só a
  identificação do Ifes ("Ifes"), sem recair em unidade nenhuma.
- **FR-3202**: A identificação da implantação MUST ser a da unidade ativa quando houver exatamente
  uma, e só a do Ifes quando houver nenhuma ou mais de uma — a regra do título da vitrine (FR-1611
  da `072`), estendida às demais superfícies sem unidade de contexto.
- **FR-3203**: A identidade comum do Ifes — a sigla, o nome por extenso, o brasão — MUST continuar
  fixa e separada da identidade da unidade.

#### Onde cada superfície acha a unidade

- **FR-3204**: Na gestão, o título das páginas e a marca da barra MUST dizer a identificação da
  unidade em que o ator atua; sem ator, a da implantação.
- **FR-3205**: As frases da gestão que dizem a quem pedir acesso ou ampliação de limite MUST nomear a
  unidade em que o ator atua.
- **FR-3206**: O portal, a página de acesso à gestão e a página de endereço não encontrado MUST dizer
  a identificação da implantação, e nunca a unidade ativa de uma sessão da gestão.
- **FR-3207**: A página pública de uma seleção MUST dizer a unidade que a Publicação da versão
  vigente registrou; sem unidade registrada no ato, a do registro pelo escopo do Edital.
- **FR-3208**: A página de endereço não encontrado MUST NOT dizer a unidade do objeto pedido.

As demais páginas do portal — a área do candidato numa inscrição, o resultado, o sorteio — ficam
com a moldura da implantação, como a vitrine. O conteúdo delas já diz o Edital; a moldura por
unidade nelas é a P-7.

#### As mensagens e o atendimento

- **FR-3209**: O aviso aos candidatos e a mensagem de convocação MUST assinar com a identificação da
  unidade do Edital. O comprovante de inscrição por e-mail MUST assinar com a unidade que a
  Publicação da versão aceita registrou, a mesma do comprovante em papel.
- **FR-3210**: O código de acesso e o aviso de mudança de credencial MUST assinar com a
  identificação da implantação.
- **FR-3211**: O registro de Unidades MUST aceitar, para cada unidade, um canal de atendimento ao
  candidato opcional: texto de uma linha, de até 255 caracteres, declarado no `unidades.json` e
  aplicado pelo comando de sincronização de sempre, com trilha, como os demais campos. Ausente no
  arquivo, o canal da unidade é vazio.
- **FR-3212**: Onde a comunicação é de um Edital — o rodapé do aviso, o rodapé que o editor mostra,
  a mensagem e a tela da convocação —, o canal MUST ser o da unidade do Edital; vazio, o
  `PORTAL_ATENDIMENTO`; vazio também, o texto que cada lugar já usa hoje.
- **FR-3213**: O assistente de dúvidas MUST encaminhar ao canal do Edital, depois ao da unidade do
  Edital, depois ao `PORTAL_ATENDIMENTO`.
- **FR-3214**: As telas e as mensagens da conta do candidato MUST usar só o `PORTAL_ATENDIMENTO`.
- **FR-3215**: Produção MUST continuar exigindo o `PORTAL_ATENDIMENTO`. Nenhuma configuração de
  envio — servidor, porta, remetente, credencial — MUST ser aceita por unidade.

#### O que não muda

- **FR-3216**: O texto que um aviso guarda ao ser confirmado — assinatura e canal incluídos — MUST
  NOT mudar quando o registro muda. O PDF, o comprovante e a página pública de uma seleção publicada
  MUST NOT mudar quando a unidade muda no registro.
- **FR-3217**: Com o registro de hoje — só o Cefor, sem canal —, toda superfície MUST dizer
  exatamente o que dizia antes desta feature, e a sincronização MUST relatar o Cefor sem mudança.
- **FR-3218**: Esta feature MUST NOT cadastrar unidade, criar tela, papel ou permissão, mudar regra
  de autorização, de Edital ou de publicação, nem mudar o seletor de demonstração. O `unidades.json`
  e o `sincronizar_unidades` MUST continuar sendo o único caminho de manutenção das unidades.
- **FR-3219**: A identificação de um ator MUST NOT dizer unidade em que ele não atua, e a troca de
  unidade ativa MUST continuar sem levar permissão de uma unidade a outra.

#### Documentação

- **FR-3220**: O comentário acima do `PAPEIS` MUST dizer o que a `106` decidiu: o diretório só
  autentica, e os vínculos ficam no GPS.
- **FR-3221**: Um documento separado da auditoria de 30/10/2026 MUST dizer quais pendências dela a
  `106` e a `107` resolveram e quais continuam abertas, citando a nota de 31/10 em vez de repeti-la.
  A auditoria MUST NOT ser reescrita.

### Key Entities

- **Unidade** (`060`): ganha o **canal de atendimento ao candidato**, opcional. Os demais campos —
  sigla, nome, cabeçalho, local, ativa — não mudam.
- **Identificação**: não é entidade gravada. É o par *sigla da unidade (ou nenhuma) + sigla do Ifes*,
  mais o canal da unidade, lido do registro no momento em que a página ou a mensagem se monta.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1031**: Com o registro de hoje, as superfícies que diziam "Cefor/Ifes" — as molduras da
  gestão, do portal, do acesso e da 404, as quatro frases de acesso e as cinco mensagens — saem
  idênticas às de antes da feature, comparadas texto a texto contra a `main`.
- **SC-1032**: Os oito cenários da §6 do pedido passam com duas unidades, o Cefor e o `campus-a`,
  registradas só pelo registro, sem nenhum teste mudar código-fonte para registrar o campus.
- **SC-1033**: Em nenhum dos cenários uma página ou mensagem de uma unidade mostra a sigla ou o canal
  da outra.
- **SC-1034**: A suíte inteira fecha verde contra PostgreSQL. Cada teste existente que mudar é
  listado na verificação, com o motivo.
- **SC-1035**: Incluir uma unidade nova exige mudar só o `unidades.json`: nenhuma constante, template
  ou configuração cita a sigla de uma unidade para montar marca, assinatura ou canal.

## Proteção de dados (LGPD)

- **Nenhum dado pessoal novo.** O canal de atendimento é da unidade, e não de uma pessoa; o arquivo
  versionado o publica no diff, e por isso ele MUST ser um canal institucional — a recusa de nome
  próprio não é verificável por máquina, e fica na revisão do diff, como as linhas do cabeçalho.
- **A identificação não vaza o que se nega.** A 404 diz só a implantação (FR-3208); a moldura da
  gestão diz só a unidade em que o ator atua (FR-3219).
- **As mensagens não ganham dado.** A assinatura troca a sigla; o canal troca o texto de contato. O
  que a mensagem diz da inscrição continua o mínimo da `010` e da `019`.

## Cenário demonstrável

Pelo canal de cada ator, sem `shell` nem banco à mão — o [quickstart](quickstart.md):

1. a TI acrescenta o campus fictício a uma cópia do `unidades.json`, num banco descartável, e roda o
   comando de sempre;
2. a operadora entra pelo seletor de demonstração no Cefor e vê "Cefor/Ifes", como hoje;
3. o candidato abre a vitrine e a página de uma seleção, e lê a moldura que a FR-3206 e a FR-3207
   dizem.

Os oito cenários da §6 do pedido são os testes automatizados (SC-1032).

## Assumptions

- A sigla do registro é a forma que a unidade usa ao lado de "/Ifes". O nome por extenso fica para o
  documento oficial, como na `060`.
- "Fale com {canal}" e "quem administra o sistema no {sigla}" funcionam para siglas de unidade no
  masculino, como o Cefor e os campi. A concordância de outras formas é a P-6.
- O canal do Cefor continua no `PORTAL_ATENDIMENTO` de produção: o valor não está no repositório, e
  copiá-lo para o registro seria inventar o dado (P-2).
- Uma consulta a mais ao registro por página montada é aceitável: a tabela tem uma linha por unidade,
  e a leitura é pela chave.

## Decisões pendentes do usuário

As perguntas estão no [`research.md`](research.md), §Perguntas ao usuário. Nenhuma bloqueia esta
feature: cada uma tem a resposta provisória que preserva o Cefor.
