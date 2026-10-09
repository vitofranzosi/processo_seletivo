# Feature Specification: O que se repete por Perfil sai uma vez no Edital em PDF

**Feature Branch**: `claude/068-consolidacao-por-perfil` — criada sobre a `main` `2b698592`, que já
tem a `065` (PR #266) e a `067` (PR #268), as duas que mexeram nas mesmas funções do compositor.

**Created**: 2026-10-09

**Status**: Draft — decisões fechadas pelo responsável pelo produto em 09/10/2026 (ver *Decisões*)

**Input**: os achados **ED-04** e **ED-11** da [auditoria do Edital em PDF de
08/10/2026](../../doc/auditoria-edital-pdf-2026-10-08.md) (§6.2, §6.3, §9, §11, §12.2) e o pedido do
responsável pelo produto, de 09/10/2026, aqui citado como 1º a 6º:

1. estender a técnica da `064` — identidade do texto impresso, subseção comum e remissão em cada
   Perfil — à regra de classificação, ao método do sorteio, às frases e, se ele decidir, aos
   requisitos;
2. uma tabela única Perfil × lista de concorrência no lugar do quadro de vagas e da tabela de
   modalidades de cada Perfil, o que resolve também o ED-11 (as modalidades saem em ordens
   diferentes nas duas tabelas do mesmo Perfil);
3. **nenhuma regra muda**: o documento diz exatamente o mesmo, com menos repetição, e cada Perfil
   continua tendo, por remissão ou na tabela, toda a regra que tinha — e isso se prova;
4. Edital publicado não se regenera nem é reavaliado; só os documentos compostos depois mudam, e a
   Retificação compõe o consolidado pela mesma regra;
5. ficam fora, cada um para spec própria: ED-05 (linguagem das frases), ED-07 e ED-08 (navegação e
   acessibilidade) e o sumário; achado novo vira registro, não escopo;
6. a numeração das tabelas muda com a tabela única, e a spec diz isso.

E as respostas do responsável pelo produto às três perguntas desta spec, na mesma data — a origem de
`D-001` a `D-003`:

7. **Posição:** as subseções comuns vão **depois do último Perfil**, junto das atribuições comuns da
   `064`, numeradas em continuação; os números dos Perfis não mudam;
8. **Tabela única:** **matriz** Perfil × lista, no lugar do quadro de cada Perfil, e as tabelas de
   modalidades **uma vez** (uma por grupo de Perfis de tabela idêntica), na mesma ordem das colunas;
9. **Requisitos:** os idênticos **se consolidam**, e o critério de identidade de todos os blocos é o
   da `064` — o texto impresso.

> **Faixa de identificadores.** Abre em **FR-1340**, **SC-510** e **UX-200**. O teto medido em
> 09/10/2026 na `main` e em todas as worktrees era o da `067` (mil trezentos e vinte e oito para os
> requisitos funcionais, quinhentos e sete para os critérios de sucesso, cento e noventa e três
> para a experiência); a `066-avisos-complementares`, em PR aberto (#269), fica abaixo disso. O
> número da pasta, `068`, é o seguinte livre: a `066` está tomada pelo PR aberto e a `067` foi
> mergeada. As decisões desta spec nascem em `D-001`.

**A frase que governa:**

> O documento diz uma vez o que é igual, diz a cada Perfil onde está — e nunca deixa um Perfil sem
> a regra que tinha.

**E a frase que mantém o corte:**

> Esta feature muda a composição do documento, e só ela. Nenhuma frase muda de texto, nenhuma regra
> é acrescentada ou tirada, e nenhum documento já publicado muda.

---

## Por que esta feature existe

### O problema

O PDF do sistema **é o ato oficial do piloto** desde 28/09/2026. Ele compõe a seção de Perfis por
entidade: cada Perfil imprime, inteiros, o quadro de vagas, a frase de reversão, a de convocação, a
tabela de modalidades, os requisitos e os marcos classificatórios — mesmo quando esses blocos são,
letra por letra, os do Perfil anterior. A `064` tirou só as atribuições repetidas; o resto continuou.

O custo é o que a auditoria mediu: a regra de classificação aparece **4 vezes** em A e **18** em B,
e o candidato que procura "como serei classificado" a encontra repetida, longe das seções
"Critérios de Classificação" e "Dos Recursos". Para saber "quantas vagas PPI no polo X" ele cruza
duas tabelas do Perfil, em ordens diferentes (ED-11).

### As evidências

Medidas em 09/10/2026 sobre os conteúdos congelados da auditoria
(`doc/auditoria-edital-pdf-2026-10-08/snapshots/`), compostos pela `main` `2b698592` — os mesmos bytes
de `specs/067-…/demonstracao/`.

| # | Evidência | Onde se verifica |
|---|---|---|
| 1 | Cenário A (4 polos): 9 páginas; a seção de Perfis vai da p. 2 à p. 6 (**5 páginas**). Os 4 Perfis imprimem o mesmo quadro (28/10/2), a mesma reversão, a mesma convocação, a mesma tabela de modalidades, os mesmos 2 requisitos e o mesmo marco por sorteio de 15 linhas, com as 9 linhas do método comum. | `specs/067-…/demonstracao/A-publicado-067.pdf` |
| 2 | Cenário B (18 Perfis): 36 páginas; a seção de Perfis vai da p. 2 à p. 31 (**30 páginas**). Os 18 marcos são idênticos; as 18 tabelas de modalidades são idênticas; os 16 Perfis de tutor presencial têm os mesmos requisitos e (pela `064`) as mesmas atribuições, numa subseção comum na p. 31. | `specs/067-…/demonstracao/B-publicado-067.pdf` |
| 3 | No mesmo Perfil, o quadro de vagas lista AC, PPI, PcD (ordem declarada) e a tabela de modalidades lista AC, PcD, PPI (ordem do código) — ED-11. | A, p. 2 |
| 4 | **Cota inferior** do ganho, medida tirando o bloco repetido de todos os Perfis menos o primeiro, sem pôr nada no lugar: só os marcos — A 7 páginas / Perfis 4; B 21 / 16. Mais quadro, modalidades e frases — A 6 / 3; B 17 / 11. Mais os requisitos — A 6 / 2; B 13 / 8. | roteiro `medir.py` da sessão, registrado em `verificacao.md` |
| 5 | A `064` reduziu 134 linhas em B e o documento continuou com 44 páginas: o espaço liberado virou branco, porque cada bloco coeso seguinte salta inteiro para a página seguinte, e a remissão mandava o leitor da p. 7 à p. 39. | auditoria §9 |
| 6 | Um Edital real da amostra, o **28/2026** (Informática na Educação, 7 polos), publica as vagas num quadro só — "Quadro 2 – Demonstrativo de distribuição de vagas", polo a polo, com as listas — e diz o percentual e o fundamento das reservas **uma vez**, em texto (itens 4.2 e 4.3). | `~/Downloads/Edital 28.2026 …retificado em 24.08.2026.pdf`, item 4 |

### O que "o mesmo" significa aqui, e por que a regra do marco precisa de uma frase

O marco classificatório é **de cada Perfil**: cada Perfil tem o seu, com a sua ordem, o seu corte, o
seu resultado e o recurso contra esse resultado. Quando quatro Perfis imprimem o mesmo texto de
marco, o texto é igual, mas as regras são **quatro**, aplicadas a quatro conjuntos de inscrições.
Impresso uma vez sob "comuns aos Perfis INF-BJN, INF-IUN, …", sem mais nada, ele se leria como
**uma** classificação conjunta — e em B, "os 10 primeiros" passaria a valer para os 18 Perfis
somados, em vez de para cada um. Isso seria regra nova. Por isso a subseção comum dos marcos diz,
antes do texto, que eles se aplicam a cada Perfil separadamente (FR-1347). As atribuições da `064`
não tinham esse risco, porque atribuição não se soma.

---

## User Scenarios & Testing *(mandatory)*

**Atores.** Quem elabora o Edital (prévia), quem publica e quem retifica, com as permissões de
hoje. O candidato é o beneficiário: lê um documento mais curto em que a regra do seu Perfil está
inteira, dita uma vez.

### User Story 1 — O candidato encontra as vagas do seu Perfil numa tabela só (Priority: P1)

O candidato ao polo de Iúna quer saber quantas vagas há para pretos, pardos e indígenas. Na seção de
Perfis, logo depois da tabela de Perfis, encontra a tabela de vagas por lista de concorrência: a
linha "INF-IUN" e a coluna "PPI" dão 10. Na tabela de modalidades, na mesma ordem das colunas, lê
que PPI é reserva de 25% pela Resolução CS nº 10/2017. Não precisa abrir a subseção do polo.

**Why this priority**: é a pergunta mais comum do candidato a um Edital de vários polos, e hoje ela
exige cruzar duas tabelas do Perfil, em ordens diferentes (ED-11).

**Independent Test**: compor o cenário A e ler, na tabela única, a célula INF-IUN × PPI; conferir
que a ordem das listas é a mesma na tabela de vagas e na de modalidades.

**Acceptance Scenarios**:

1. **Given** um Edital com mais de um Perfil e quadro de vagas declarado, **When** o documento é
   composto, **Then** as vagas de todos os Perfis saem numa tabela única, conforme `D-002`, e nenhum
   Perfil imprime o próprio quadro de vagas.
2. **Given** o cenário A, **When** se compara a ordem das listas, **Then** ela é a mesma na tabela de
   vagas e na de modalidades (ED-11).
3. **Given** um Perfil sem vaga imediata (só cadastro de reserva), **When** o documento é composto,
   **Then** ele não tem linha na tabela de vagas e nenhum zero é impresso por ele — a regra da `067`
   (D-003 dela) — e continua presente na tabela de modalidades.
4. **Given** um Edital de um Perfil só, **When** o documento é composto, **Then** ele sai com os
   mesmos bytes de antes desta feature.

---

### User Story 2 — O candidato lê a regra de classificação uma vez, sabendo que vale para o seu Perfil (Priority: P1)

A candidata ao polo de Vargem Alta lê a subseção do seu Perfil e encontra "Marcos classificatórios:
os descritos no item N.k". No item N.k, o título diz que os marcos são comuns aos quatro polos, e a
primeira frase diz que se aplicam a cada polo separadamente. Abaixo, o marco por sorteio, o método e
o corte, uma vez.

**Why this priority**: é o bloco que mais se repete (4× em A, 18× em B) e o que mais páginas custa
(evidência 4). E é o único em que a consolidação, malfeita, mudaria a regra.

**Independent Test**: compor A e B; para cada Perfil, seguir a remissão e conferir que o texto dos
marcos da subseção é, linha a linha, o que o Perfil imprimia antes, e que a subseção diz que a regra
vale para cada Perfil separadamente.

**Acceptance Scenarios**:

1. **Given** dois ou mais Perfis cujos marcos imprimem o mesmo texto, **When** o documento é
   composto, **Then** os marcos saem uma vez, numa subseção comum que nomeia os códigos desses
   Perfis, e cada um deles remete a ela, no lugar dos seus marcos.
2. **Given** a subseção comum de marcos, **When** é lida, **Then** antes dos marcos está a frase que
   os aplica a cada Perfil separadamente (FR-1347).
3. **Given** dois Perfis cujos marcos diferem numa linha — outro corte, outro prazo de recurso, outro
   critério de desempate —, **When** o documento é composto, **Then** eles não se juntam, e cada um
   imprime os próprios.
4. **Given** marcos por sorteio governados pelo método comum do Edital, **When** o documento é
   composto, **Then** as linhas do método comum saem **uma vez** no documento, e todo outro lugar que
   as imprimiria remete a elas (FR-1349).

---

### User Story 3 — As frases e os requisitos iguais saem uma vez (Priority: P2)

O candidato lê, uma vez, que "havendo ausência de candidatos aprovados na reserva de vagas, o
quantitativo será destinado à respectiva ampla concorrência" e que "a convocação dos classificados
será feita por publicação no endereço eletrônico do certame" — logo abaixo das tabelas que essas
frases governam, e não quatro ou dezoito vezes, coladas à grade de cada quadro. Os requisitos
idênticos, conforme `D-003`.

**Why this priority**: são linhas curtas, mas repetidas em todo Perfil; e a reversão é regra sobre o
quadro, que deixa de estar no Perfil (US1).

**Independent Test**: compor A e conferir que cada frase sai uma vez; compor um Edital em que só
dois de três Perfis têm reversão e conferir que a frase nomeia esses dois.

**Acceptance Scenarios**:

1. **Given** todos os Perfis da tabela de vagas com a mesma espécie de reversão, **When** o documento
   é composto, **Then** a frase sai uma vez, abaixo da tabela de vagas, sem nomear Perfil.
2. **Given** Perfis com espécies diferentes, ou algum sem reversão, **When** o documento é composto,
   **Then** sai uma frase por espécie, iniciada pelos códigos dos Perfis a que se aplica.
3. **Given** a forma de convocação, **When** o documento é composto, **Then** vale a mesma regra: uma
   frase sem nomear Perfil quando todos os Perfis do Edital a declaram igual; senão, uma por forma,
   com os códigos.

---

### User Story 4 — O que já foi publicado não muda, e a Retificação compõe pela mesma regra (Priority: P2)

Um Edital publicado antes desta feature conserva o documento que publicou. Retificado depois, o
documento consolidado da Retificação sai no layout novo, agrupando pela versão retificada.

**Why this priority**: a Publicação é imutável (Constituição, II); o layout novo não pode alcançar o
passado, e a Retificação não pode herdar agrupamento que não vale mais.

**Independent Test**: publicar, retificar o marco de um dos Perfis agrupados e comparar os dois
documentos guardados.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** esta feature entra, **Then** o documento guardado continua
   com os mesmos bytes.
2. **Given** quatro Perfis com os mesmos marcos e uma Retificação que muda o prazo de recurso de um
   deles, **When** a Retificação é publicada, **Then** o documento dela agrupa os três que continuam
   iguais, e o quarto imprime os próprios marcos.
3. **Given** um Edital cujo texto livre cita "Tabela 4", publicado antes desta feature e retificado
   depois, **When** o consolidado da Retificação é composto, **Then** "Tabela 4" pode designar outra
   tabela — consequência conhecida desta feature, dita em *Consequências na numeração*.

---

### Edge Cases

- **Edital de um Perfil.** Nada muda: sem tabela de Perfis, sem tabela única, sem subseção comum, e
  os mesmos bytes (FR-1356).
- **Dois Perfis, marcos diferentes.** Nenhuma subseção comum de marcos; cada Perfil imprime os seus.
  A tabela única e as frases consolidam do mesmo jeito.
- **Dois grupos de marcos.** Duas subseções comuns, na ordem do primeiro Perfil de cada grupo.
- **Diferença só no título "Marcos classificatórios — INF-BJN".** Não conta: o título nomeia o
  Perfil, e não é regra. Tudo abaixo dele conta, inclusive o código e o nome do marco.
- **Mesmo marco, método próprio idêntico em cada Perfil.** Imprime "Método: próprio deste marco" em
  todos; o texto é igual, e se juntam. O método próprio não é o comum, e não remete a ele.
- **Marco que diverge do método comum.** Imprime o próprio, como hoje; não se junta a quem segue o
  comum.
- **Método comum em marcos de grupos diferentes.** As linhas do método comum saem na primeira vez em
  que o documento as imprimiria; nos demais lugares, "Método: o comum a este Edital, descrito no item
  N.k" (FR-1349).
- **Perfil sem marco.** Não remete a nada e não entra em grupo.
- **Perfil sem quadro de vagas** (Edital anterior à `025`) ou **sem vaga imediata** (`067`). Não tem
  linha na tabela de vagas; continua na tabela de modalidades.
- **Nenhum Perfil com quadro.** Nenhuma tabela de vagas e nenhuma frase de reversão; a numeração das
  tabelas segue sem lacuna.
- **Perfis com conjuntos diferentes de modalidades.** A tabela de vagas tem uma coluna por lista que
  algum Perfil declara; a célula da lista que o Perfil não tem sai "—", e não "0". As tabelas de
  modalidades se agrupam pela identidade do texto impresso, como os marcos (FR-1344).
- **Muitas listas** (as dez sublistas da Lei nº 12.711). A tabela de vagas usa o código da lista no
  cabeçalho, e o nome está na tabela de modalidades; se ainda assim não couber na largura da página,
  a tabela sai na forma longa (FR-1342) — nunca corta coluna.
- **Modalidade sem percentual ou sem fundamento.** A coluna que nenhuma linha preenche não sai, como
  hoje; a linha "AC — Ampla concorrência" continua com "—" (ED-05, fora de escopo).
- **Código com vírgula ou " e ".** Os títulos e as frases que enumeram códigos seguem a regra da `064`:
  todos entre aspas, e a quebra de linha nunca dentro de um código.
- **Retificação que desfaz um grupo.** O Perfil que ficou diferente volta a imprimir o próprio bloco;
  o grupo de um Perfil só se desfaz.
- **Caractere que a grafia normaliza.** Dois textos que só diferem nisso imprimem igual e se juntam,
  como na `064`.

---

## Requirements *(mandatory)*

### Functional Requirements

**Identidade**

- **FR-1340**: Dois blocos de Perfis diferentes são **idênticos** quando o documento os imprimiria com
  o mesmo texto, linha a linha, na mesma ordem e com a mesma hierarquia — a regra da `064` (FR-1187
  dela), estendida do texto de atribuições ao bloco impresso. O título que nomeia o Perfil não entra
  na comparação; nada mais fica de fora. Nada além dessa identidade MUST agrupar Perfis: nem
  denominação, nem código, nem localidade, nem coincidência parcial.
  (`D-003`)
- **FR-1341**: A consolidação MUST existir só com dois ou mais Perfis, e só na composição do
  documento: não altera o cadastro, o conteúdo da versão, a impressão digital, o conteúdo publicado,
  as telas de composição, Revisão e Retificação, nem o portal.

**Vagas e modalidades (ED-04, ED-11)**

- **FR-1342**: Com dois ou mais Perfis, as vagas por lista de concorrência de todos os Perfis com
  quadro de vagas MUST sair numa tabela única, logo depois da tabela de Perfis — uma linha por Perfil,
  identificado pelo código, e uma coluna por lista, identificada pelo código da modalidade e
  "Ampla concorrência" para a linha geral (`D-002`) —, e nenhum Perfil MUST imprimir o próprio quadro
  de vagas nem a própria tabela de modalidades. Se as colunas não couberem na largura da página, a
  tabela única MUST sair na forma longa — uma linha por Perfil e lista, com as vagas —, e nunca com
  coluna cortada.
- **FR-1343**: A tabela única MUST conter, para cada Perfil com quadro e com vaga imediata, exatamente
  os números do quadro dele, cada um na lista a que pertence; lista que o Perfil não declara MUST sair
  "—". Perfil sem quadro ou sem vaga imediata MUST NOT ter linha (`067`, D-003 dela).
- **FR-1344**: As tabelas de modalidades MUST se agrupar pela identidade do FR-1340: uma tabela por
  grupo de Perfis de tabela idêntica, com legenda que nomeia os códigos do grupo — ou nenhum, quando o
  grupo é o Edital inteiro —, logo depois da tabela de vagas.
- **FR-1345**: A ordem das listas MUST ser uma só no documento (ED-11): a linha geral primeiro, depois
  as listas reservadas na ordem declarada no quadro; as modalidades que nenhum quadro declara, depois,
  na ordem de hoje. A tabela de vagas e as de modalidades MUST seguir essa ordem.

**Marcos classificatórios e método do sorteio (ED-04)**

- **FR-1346**: Quando dois ou mais Perfis têm marcos classificatórios idênticos (FR-1340), os marcos
  MUST sair uma vez, numa subseção comum cujo título nomeia os códigos desses Perfis, na posição de
  `D-001`; e cada um desses Perfis MUST trazer, no lugar dos seus marcos, o rótulo "Marcos
  classificatórios" seguido da remissão ao número da subseção.
- **FR-1359**: As subseções comuns MUST ficar depois do último Perfil, dentro da seção de Perfis,
  numeradas em continuação, na ordem dos blocos dentro do Perfil — atribuições (`064`), requisitos,
  marcos — e, dentro de cada matéria, na ordem do primeiro Perfil de cada grupo (`D-001`). Os números
  dos Perfis e os das subseções de atribuições comuns da `064` MUST ser os mesmos com e sem esta
  feature; os títulos MUST seguir a regra de enumeração de códigos da `064` (FR-1189 dela).
- **FR-1347**: A subseção comum de marcos MUST dizer, antes dos marcos, que eles se aplicam a cada um
  dos Perfis nomeados **separadamente** — cada um com a sua ordem, o seu corte e o seu resultado.
  Essa frase não é regra nova: é o que a posição do marco dentro do Perfil dizia, e que a
  consolidação tira dele.
- **FR-1348**: O texto dos marcos na subseção comum MUST ser, linha a linha, o que cada Perfil do grupo
  imprimiria — sem acrescentar, suprimir, reordenar ou reescrever nada.
- **FR-1349**: As linhas do método comum do sorteio (algoritmo, fonte, ocorrência, quando, derivação,
  semente, se faltar) MUST sair uma vez no documento, no primeiro lugar em que seriam impressas; todo
  outro marco governado pelo método comum MUST imprimir "Método: o comum a este Edital, descrito no
  item N.k" e as linhas que são dele — a habilitação. O método próprio de um marco MUST continuar
  impresso no marco.

**Frases e requisitos**

- **FR-1350**: A frase de reversão MUST sair abaixo da tabela de vagas, e não no Perfil: uma vez, sem
  nomear Perfil, quando todos os Perfis da tabela declaram a mesma espécie; senão, uma por espécie,
  iniciada pelos códigos dos Perfis a que se aplica. Perfil fora da tabela de vagas MUST NOT ser
  alcançado por frase de reversão.
- **FR-1351**: A frase de forma de convocação MUST sair uma vez, logo depois das tabelas de vagas e de
  modalidades, sem nomear Perfil quando todos os Perfis do Edital declaram a mesma forma; senão, uma
  por forma, iniciada pelos códigos dos Perfis. Perfil sem forma declarada MUST NOT ser alcançado.
- **FR-1352**: Quando dois ou mais Perfis têm requisitos idênticos (FR-1340), os requisitos MUST sair
  uma vez, numa subseção comum cujo título nomeia os códigos desses Perfis, na posição de `D-001`; e
  cada um desses Perfis MUST trazer, no lugar dos seus, o rótulo "Requisitos" seguido da remissão ao
  número da subseção (`D-003`). Lista vazia MUST NOT formar grupo.

**Equivalência e numeração**

- **FR-1353**: Para cada Perfil, toda frase normativa que o documento imprimia no bloco dele antes
  desta feature MUST continuar no documento, aplicável a ele por um destes caminhos, e por um só: no
  próprio bloco; na subseção comum a que ele remete; na linha ou na legenda de tabela que o nomeia; ou
  na frase que o nomeia ou que vale para todos. Nenhuma frase MUST ser alcançada por Perfil a que não
  se aplicava.
- **FR-1354**: Toda remissão MUST apontar subseção do mesmo documento cujo título nomeia o Perfil que
  remete; e cada subseção comum MUST ser objeto de remissão de todos os Perfis que nomeia, e de nenhum
  outro.
- **FR-1355**: As funções que dizem quais itens e quantas tabelas o documento imprime — usadas pela
  conferência de remissões da `065` (D-004 dela) — MUST continuar sendo a mesma regra da composição,
  com as subseções comuns novas e a contagem nova de tabelas.
- **FR-1356**: O documento de Edital de um Perfil só MUST sair com os mesmos bytes de antes desta
  feature; a prévia e o publicado MUST consolidar do mesmo modo e quebrar nas mesmas páginas.

**Paginação**

- **FR-1357**: As subseções comuns MUST obedecer à paginação do Perfil (FR-020 a FR-022 da `008`),
  como a da `064`; a tabela única MUST repetir o cabeçalho quando atravessa a página, como as demais.

**Publicação e Retificação**

- **FR-1358**: Documento já gerado MUST NOT ser regerado nem alterado. Todo documento composto depois
  desta feature — prévia, Publicação e consolidado de Retificação, inclusive de Edital publicado antes
  dela — MUST sair no layout novo, agrupando pela versão que compõe.

### Consequências na numeração

A tabela única substitui, com dois ou mais Perfis, as duas tabelas de cada Perfil. **A numeração
"Tabela N" muda**: em A, o Cronograma deixa de ser a Tabela 10. Uma remissão "Tabela N" digitada pelo
gestor no texto livre pode passar a apontar outra tabela. Isso alcança:

- o Edital composto depois desta feature — a conferência de remissões da `065` lê a contagem nova
  (FR-1355), e o gestor vê na prévia o número com que cada tabela sai;
- o **consolidado de Retificação de Edital publicado antes desta feature**: o texto livre foi escrito
  contra a numeração antiga, e o consolidado sai na nova. A conferência da `065` só acusa "Tabela N"
  **sem destino**; a que passa a designar outra tabela não é acusada.

Os números das seções, dos Perfis e das subseções de atribuições comuns da `064` não mudam (`D-001`,
FR-1359); as subseções comuns novas vêm depois delas.

### Key Entities

- **Perfil de Vaga**: nada nele muda.
- **Documento do Edital**: a prévia, o documento publicado e o consolidado de Retificação, compostos
  pela mesma regra; o publicado não se regera.
- **Tabela única de vagas, subseção comum, frase consolidada**: existem só no documento; não são
  registradas e não sobrevivem fora da composição que as produziu.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

As metas partem da evidência 4 (cota inferior medida, sem o que entra no lugar) com a folga da
tabela única, das remissões e das subseções comuns. Medidas pelo **fluxo real** de publicação, nos
cenários da auditoria.

- **SC-510**: No cenário A, a seção de Perfis cai de **5 para no máximo 3 páginas**, e o documento de
  9 para no máximo **7**.
- **SC-511**: No cenário B, a seção de Perfis cai de **30 para no máximo 12 páginas**, e o documento de
  36 para no máximo **18**.
- **SC-512**: Nos dois cenários, o texto dos marcos sai **uma** vez; a tabela de modalidades, uma vez;
  as frases de reversão e de convocação, uma vez cada; as 9 linhas do método comum, uma vez.
- **SC-513**: Para cada Perfil dos dois cenários e de todo caso de teste, reconstruir pelo documento
  de depois as frases normativas aplicáveis a ele (FR-1353) devolve exatamente as que o documento de
  antes imprimia no bloco dele — nenhuma a menos, nenhuma a mais, nenhuma com outro texto.
- **SC-514**: A soma das alturas em branco no pé das páginas da seção de Perfis, nos dois cenários, é
  menor depois que antes; as páginas afetadas são renderizadas e olhadas.
- **SC-515**: O documento de Edital de um Perfil e os documentos guardados de Publicações anteriores
  continuam com os mesmos bytes, e a suíte completa contra PostgreSQL passa.

### O que esta feature não cobre, deliberadamente

- A linguagem das frases (ED-05): nenhuma frase gerada muda de texto, salvo as aberturas que a
  consolidação exige (FR-1347, FR-1349, FR-1350, FR-1351).
- Navegação e acessibilidade (ED-07, ED-08), sumário, links nas remissões.
- A frase na margem zero (ED-15): as frases saem do Perfil, e o recuo delas segue o da seção; o ajuste
  fino de espaçamento não é escopo.
- Aviso para "Tabela N" que passa a designar outra tabela na Retificação de Edital anterior a esta
  feature: registrado em *Consequências na numeração*, sem tratamento.
- Consolidação na Revisão, na tela de Retificação e no portal, que continuam por Perfil.

---

## Decisões

Tomadas pelo responsável pelo produto em 09/10/2026, sobre as opções apresentadas com a medição da
evidência 4.

- **D-001 — As subseções comuns ficam depois do último Perfil.** Junto das atribuições comuns da
  `064`, numeradas em continuação. *Alternativas descartadas:* antes dos Perfis — leitura do geral
  para o particular, mas uma Retificação que desfizesse um grupo renumeraria todos os Perfis, e o
  "item 3.5" digitado no texto livre passaria a ser outro Perfil sem aviso; na primeira ocorrência —
  nenhum número novo, mas quem lê o primeiro Perfil não sabe que a regra é comum, e a Retificação
  desse Perfil mudaria a "casa" da regra. O custo de navegação da `064` (remissão da p. 7 à p. 39 em
  B) cai com a própria consolidação, que encolhe a seção.
- **D-002 — Tabela única em matriz, e modalidades uma vez.** Uma linha por Perfil, uma coluna por
  lista, no lugar do quadro de cada Perfil; as tabelas de modalidades, com percentual e fundamento,
  uma por grupo de Perfis de tabela idêntica — uma só quando todos são iguais —, na ordem das colunas
  (ED-11). *Alternativas descartadas:* tabela longa com percentual e fundamento em cada linha —
  repetiria o fundamento por linha, até 72 linhas em B; consolidar só as modalidades — o quadro de
  cada Perfil continuaria, e a pergunta "quantas vagas PPI no polo X" continuaria pedindo o Perfil.
- **D-003 — Requisitos idênticos se consolidam, e "idêntico" é o texto impresso.** O critério da `064`
  vale para todos os blocos: requisitos, tabelas de modalidades e marcos. *Alternativa descartada:*
  manter os requisitos em cada Perfil — são curtos, mas 16 vezes os mesmos em B.

---

## Assumptions

- Os Perfis saem na ordem do código, como hoje (ED-19, fora de escopo); é essa a "ordem do documento".
- O marco classificatório é de cada Perfil, e por isso a frase do FR-1347 é necessária e suficiente.
- Quem compõe o documento é uma só função, chamada pela prévia, pela Publicação e pela Retificação.
- Os cenários A e B da auditoria são reproduzíveis pelo fluxo real (`cenario_a.py` e
  `cenario_b_corrigido.py`), em bancos de validação novos, com dados fictícios.
