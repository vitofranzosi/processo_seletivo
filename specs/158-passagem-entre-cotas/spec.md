# Feature Specification: Passagem da vaga reservada entre cotas antes da ampla concorrência

**Feature Branch**: `claude/158-passagem-entre-cotas`, sobre a `claude/elegant-robinson-e66ed2` (#482, a
`155`, ainda sem merge) em `666e01d1`

**Created**: 2026-11-11

**Status**: Draft — só a spec, sem plano nem código. Oito perguntas ao usuário (P-1 a P-8) estão
abertas, e a regra não fecha sem elas. Os requisitos que dependem de uma pergunta estão escritos com a
recomendação desta spec e dizem de qual pergunta dependem.

**Input**: a decisão do usuário de 11/11/2026, registrada na `155`, de que a passagem entre cotas tem
spec própria; e o pedido da sessão que coordena o estudo: *"Escrever a spec da passagem da vaga
reservada entre cotas antes da ampla, a partir do encaminhamento e da `155`, respondendo as seis
perguntas do encaminhamento; as que dependem de norma entram como perguntas numeradas ao usuário."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de seis mil e seiscentos a seis mil seiscentos e quarenta e nove;
> - os critérios de dois mil cento e sessenta a dois mil cento e setenta e nove;
> - os requisitos de experiência de seiscentos e sessenta a seiscentos e setenta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`. A reserva está nas notas
> compartilhadas das sessões do estudo, ao lado das da `155`, da `156` e da `157`; os tetos foram
> medidos em 11/11 na `main`, em todas as branches remotas e nas pastas `specs/` das worktrees.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-246 da `016`"); decisão de outra feature, pelo assunto, nunca pelo identificador. Achado de estudo,
> como "achado NN".
>
> **Origem.** O [encaminhamento](../../doc/encaminhamento-passagem-entre-cotas.md) que a `155`
> registrou ao decidir que a passagem entre cotas teria spec própria, e as FR-6304, FR-6305 e FR-6317
> a FR-6319 da `155`.

## Por que esta feature existe

Três Editais do Cefor e um do IFFluminense mandam que a vaga reservada sem ocupante passe **por outras
cotas antes de chegar à ampla**. O GPS só sabe levá-la à linha geral do mesmo Perfil (FR-246 da
`016`). Desde a `155`, o Perfil pode dizer *"Passa antes por outras cotas, na ordem do Edital"*, e com
essa resposta nenhum ato move a vaga: a tela diz que o GPS ainda não aplica a ordem (FR-6318 da
`155`). É honesto, e é o beco que a `155` tirou do Edital silente, agora no Edital que fala.

A leitura dos quatro Editais, feita para esta spec, mostra que a resposta única por Perfil da `155`
**não basta nem para o Edital que a motivou**:

- No 173/2025, a mesma seção manda a vaga de um subgrupo de PPIQ às **demais** subgrupos e, depois, à
  ampla (9.5.1), e manda a vaga da PcD **direto** à ampla (9.5.6). Um Perfil desse Edital precisa dizer
  as duas coisas, e a resposta por Perfil diz uma.
- A terceira resposta da `155` não diz **quando** a vaga sai da origem: ela ocupa o lugar do gatilho
  ("por esgotamento" ou "por saldo"), e o Edital tem gatilho — o 173/2025 fala em *"inexistência de
  candidatos habilitados em determinado subgrupo"*.
- O 33/2026 (Anexo 7) declara, para cada uma das oito cotas da Lei nº 12.711/2012, a **sua** sequência
  de sete destinos, e as sequências não são rotações umas das outras.

## O que os Editais declaram

Lidos com `pdftotext -layout` a partir dos PDFs de origem em `~/Downloads`.

| Edital | Cláusula | O que manda |
|---|---|---|
| 173/2025 (cadastro de reserva de designer educacional, Cefor) | 9.5.1 | *"Na hipótese de inexistência de candidatos habilitados em determinado subgrupo (pretos/pardos, indígenas ou quilombolas), as vagas serão revertidas aos demais subgrupos de PPIQ e, persistindo a ausência, à Ampla Concorrência, conforme previsto no Decreto nº 12.536/2025."* |
| 173/2025 | 9.5.6 | Ausência de aprovados na reserva (PPIQ e PcD): o quantitativo vai à ampla. Para a PcD, é o único destino. |
| 173/2025 | 9.5 | Uma **ordem de convocação** de trinta posições, cada uma com a Modalidade de onde sai a pessoa: 1ª AC, 2ª PCD, 3ª PPIQ (Pretos/Pardos), …, 9ª PPIQ (Indígenas), …, 26ª PPIQ (Quilombolas). |
| 140/2025 (cadastro de reserva de tutor presencial, Cefor) | 10.5 e 10.5.1 | A mesma cascata entre submodalidades de PPIQ, e uma ordem de cinquenta posições que acrescenta a PPT (50ª). Nada sobre a PcD ou a PPT sem ocupante. |
| 90/2026 (tutoria, Cefor) | 11.2 e 11.3 | O mesmo texto do 140/2025 (PTT na 50ª). Nada sobre a PcD ou a PTT sem ocupante. Parágrafo único do item de reserva: as reservas não se acumulam, e o candidato escolhe **uma** Modalidade. |
| 33/2026 (cursos técnicos integrados, IFFluminense) | 2.4 e Anexo 7 | *"As vagas de cotas não preenchidas pelos classificados serão redirecionadas seguindo o estabelecido no Anexo 7"*. O Anexo dá, para cada cota de origem, sete destinos "pela ordem", com *"restando vagas"* entre eles, e termina: *"As vagas que restarem após a aplicação do disposto nos incisos I a VIII deste Anexo serão ofertadas aos demais candidatos, classificados na Ampla Concorrência."* |
| 33/2026 | item da prioridade de convocação | Quem se inscreve em **mais de uma** cota é convocado pela ordem de prioridade LI_EP, LI_PCD, LI_Q, LI_PPI, LB_EP, LB_PCD, LB_Q, LB_PPI. |
| 33/2026 | Anexo 2 | Há cota com **zero** vagas em vários cursos (LI_Q, por exemplo), e ela é destino em seis das oito sequências. |

**Três irregularidades no Anexo 7 do 33/2026**, registradas porque o GPS precisa compor o que o Edital
publicou, e não o que ele quis dizer:

1. No inciso V (origem LB_Q), o destino *f* é *"Cota PCD 8"*, que não é nome de cota nenhuma do Edital.
   Pelo padrão dos outros incisos seria LI_PCD, mas isso é leitura.
2. No inciso VII (origem LI_Q), LB_Q aparece em quinto, depois de LI_PPI, quando nos demais incisos as
   cotas LB vêm todas antes das LI.
3. Os incisos não são rotações de uma ordem só: a ordem por origem é a única forma que reproduz o
   Anexo.

**A lei, como o corpus a cita.** Os Editais do Cefor citam o Decreto nº 12.536/2025 e a Lei nº
15.142/2025; o do IFFluminense, a Lei nº 12.711/2012. Como na `155`, **esta spec não interpreta lei**:
o que o sistema aplica é a ordem que o Edital publicou. Onde a ordem publicada é incompleta — os
"demais subgrupos" do Cefor, sem ordem entre eles —, a lacuna é pergunta ao usuário (P-5), e não
inferência.

## O que existe no GPS

| # | O quê | Onde |
|---|---|---|
| E-1 | A reversão tem um destino só: a linha geral do mesmo Perfil. | FR-246 da `016` |
| E-2 | O gatilho é do Perfil, uma espécie para todas as reservadas dele: por esgotamento ou por saldo. | FR-249 da `016`; o campo da espécie no Perfil |
| E-3 | Desde a `155`, a terceira resposta, *"Passa antes por outras cotas, na ordem do Edital"*, sem gatilho e sem aplicação. | FR-6317 a FR-6319 da `155` |
| E-4 | A destinação à ampla é ato próprio, com "Confira antes", fundamento e registro, e o desfazimento por ato contrário. | FR-6308 a FR-6316 e FR-6334 a FR-6336 da `155` |
| E-5 | O movimento de vaga tem origem, destino e quantidade, e o destino pode ser uma lista reservada; o banco recusa origem igual ao destino. A reversão sempre gravou a linha geral. | o movimento de vaga da `016` |
| E-6 | A inscrição concorre por **uma** Modalidade, além da ampla. | a inscrição da `010` |
| E-7 | A linha do quadro pode ter zero vagas; linha ausente não é zero. | a `025` |
| E-8 | A ordem das linhas do quadro é apresentação, e não ordem de convocação nem precedência entre listas. | a decisão da `025` sobre a ordem das linhas |
| E-9 | Os Editais do Cefor compostos no GPS têm **uma** Modalidade de PPIQ por Perfil, e não os subgrupos: o teste de aceitação do 173/2025 usa a PPP só, e o estudo da `043` mediu quatro Modalidades por Perfil no 140/2025. | `tests/acceptance/test_ciclo_do_173.py`; a `043` |

O E-9 importa: **a passagem entre subgrupos só existe se os subgrupos forem Modalidades distintas do
Perfil**, cada uma com a sua linha no quadro e a sua lista. Composto com uma PPIQ só, um Edital do
Cefor não tem para onde passar a vaga entre subgrupos, e a cascata do 9.5.1 se reduz à destinação à
ampla da `155`. Como compor é a P-8.

## O que esta spec cobre, e o que fica fora

**Cobre** as seis perguntas do encaminhamento:

1. a **declaração** da ordem no Perfil, por Modalidade de origem (P-1);
2. o **gatilho** em cada degrau: quando a vaga sai da origem e quando um destino é saltado (P-2);
3. o **destino intermediário** que também não tem quem ocupar, e a vaga recebida que depois fica sem
   ocupante (P-3);
4. a **concomitância** no destino: quem já ocupa pela ampla e é da cota de destino;
5. a **prévia** da `095` e da `098`: os degraus e a equivalência com o caminho oficial;
6. o **documento do Edital** — a frase de cada ordem — e a entrada no catálogo de Retificação (P-7).

E ainda: duas origens que disputam o mesmo destino (P-6), a passagem na página pública e no relatório,
e as revisões das specs afetadas.

**Fica fora:**

- a **ordem de convocação por posição** dos Editais do Cefor (a 9ª posição sai dos Indígenas, a 26ª dos
  Quilombolas): o GPS não a representa (E-8), e ela é outra feature. Aqui a passagem move
  **quantidade** entre Modalidades, como a `016` move para a ampla;
- a inscrição em **mais de uma** cota, com prioridade entre elas (33/2026): o GPS admite uma Modalidade
  por inscrição (E-6), e mudar isso é outra feature;
- o remanejamento entre Perfis, que a FR-246 da `016` continua recusando;
- a interpretação do Decreto nº 12.536/2025 ou da Lei nº 12.711/2012;
- um documento PDF da passagem (como a `155` decidiu para a destinação).

## User Scenarios & Testing *(mandatory)*

O **cenário mínimo** do encaminhamento atravessa as histórias: um Perfil com três subgrupos de PPIQ —
Pretos e Pardos (PP), Indígenas (I) e Quilombolas (Q) — e a ampla, uma vaga em cada, e **um único
habilitado**, em I. A ordem declarada, pela recomendação da P-5, é a do texto do Edital: PP, I, Q.

### User Story 1 — Quem elabora declara para onde vai a vaga de cada cota (Priority: P1)

No passo Perfis, cada Modalidade reservada responde para onde vai a vaga dela que ficar sem ocupante:
*"Não passa a lugar nenhum"*, *"Direto à ampla concorrência"* ou *"Pela ordem: …"*, com a sequência de
Modalidades do mesmo Perfil e, ao fim, se o que restar vai à ampla. O gatilho continua do Perfil, como
hoje. O documento do Edital imprime a frase de cada origem.

**Why this priority**: sem declaração não há passagem (a `016` não infere), e a declaração por Perfil
da `155` não representa nem o 173/2025 (9.5.1 e 9.5.6 juntos).

**Independent Test**: compor um Perfil do 173/2025 com PP, I, Q e PcD; declarar PP, I e Q "pela ordem"
e PcD "direto à ampla"; publicar; conferir que o documento traz quatro frases, cada uma com a sua
origem, e que a publicação recusa uma ordem que cita Modalidade de outro Perfil ou a própria origem.

**Acceptance Scenarios**:

1. **Given** um Perfil com reversão por esgotamento e as quatro Modalidades, **When** quem elabora
   declara I "pela ordem: PP, Q; restando, à ampla", **Then** a revisão mostra a frase de I com os
   nomes das Modalidades, e não códigos.
2. **Given** uma ordem que inclui a própria origem, uma Modalidade repetida ou a ampla no meio da
   sequência, **When** quem elabora tenta publicar, **Then** a publicação é recusada, com a razão dita
   na Modalidade.
3. **Given** uma Modalidade reservada sem resposta, num Perfil com gatilho declarado, **When** quem
   elabora tenta publicar, **Then** a publicação é recusada — a ausência não vira "direto à ampla".
4. **Given** as oito sequências do Anexo 7 do 33/2026, **When** quem elabora as compõe, **Then** cada
   uma é reproduzível exatamente, inclusive a do inciso VII, com LB_Q depois de LI_PPI.
5. **Given** o destino *"Cota PCD 8"* do inciso V, **When** quem elabora compõe a sequência, **Then** o
   GPS só aceita um destino que seja Modalidade do Perfil: quem elabora escolhe uma, e a escolha fica
   dele.

---

### User Story 2 — A presidência passa a vaga à primeira cota que tem quem a ocupe (Priority: P1)

No cenário mínimo, PP e Q não têm quem ocupar. A ocupação diz, para PP: *"1 vaga dos Pretos e Pardos
sem quem a ocupe. O Edital manda passá-la, pela ordem, aos Indígenas e aos Quilombolas e, restando, à
ampla concorrência."* O "Confira antes" mostra cada degrau e por que ele é saltado — *"Indígenas: a
única pessoa habilitada ocupa a vaga dos Indígenas"*, *"Quilombolas: ninguém concorre"* — e o destino
final: a ampla. Confirmado, um registro diz a origem, o destino, a quantidade, os degraus saltados com a
razão de cada um, o gatilho e a versão do Edital.

**Why this priority**: é o caso do encaminhamento, e o que hoje fica parado na limitação da `155`.

**Independent Test**: o cenário mínimo leva as vagas de PP e Q à ampla com **uma** confirmação cada; a
variação com dois habilitados em I leva a vaga de PP aos Indígenas, e a ocupação de I passa a ter duas
vagas efetivas e a chamada da segunda pessoa como próximo passo.

**Acceptance Scenarios**:

1. **Given** o cenário mínimo com o resultado definitivo e nenhum impedimento, **When** a presidência
   abre a ocupação de PP, **Then** a tela diz a situação, a ordem publicada e um ato: "Passar a vaga
   pela ordem do Edital".
2. **Given** o mesmo, **When** ela confirma, **Then** a vaga vai à ampla, e o registro nomeia os dois
   degraus saltados e a razão de cada um.
3. **Given** a variação com dois habilitados em I, **When** ela confirma a passagem de PP, **Then** a
   vaga vai a I, e não à ampla; a apuração de I fica obsoleta pelo movimento, e o Centro leva à chamada
   da segunda pessoa de I.
4. **Given** duas vagas de PP sem ocupante e um excedente só em I, **When** ela confirma, **Then** uma
   vaga vai a I e a outra segue a ordem: Q, e depois a ampla — dois movimentos, um ato.
5. **Given** a PcD do 173/2025 declarada "direto à ampla", **When** a presidência abre a ocupação da
   PcD, **Then** o ato é o "Destinar à ampla concorrência" da `155`, sem degrau.

---

### User Story 3 — Nenhum degrau é saltado sob dúvida (Priority: P1)

O destino só é saltado quando **certamente** não tem quem ocupar a vaga recebida. Se alguém do destino
tem chamada em curso, prazo recursal aberto, ou ocupa a ampla sem aceite registrado, a passagem não é
oferecida, e a tela diz qual degrau a impede e até quando.

**Why this priority**: saltar um degrau tira a vaga de uma cota que o Edital mandou atender antes; a
`155` já recusou afirmar esgotamento sob situação reversível, e o mesmo vale em cada degrau.

**Independent Test**: no cenário mínimo, abrir prazo recursal sobre a eliminação de alguém de Q e
conferir que a passagem de PP não é oferecida enquanto ele corre; encerrado, sem recurso, ela é.

**Acceptance Scenarios**:

1. **Given** a variação com dois habilitados em I, e a segunda pessoa de I com chamada em curso para
   outra vaga, **When** a presidência abre a ocupação de PP, **Then** a passagem não é oferecida, e a
   tela diz que o degrau dos Indígenas depende do desfecho daquela chamada.
2. **Given** alguém de Q eliminado com prazo recursal aberto, **When** ela abre a ocupação de PP,
   **Then** a passagem não é oferecida, e a tela diz até quando cabe o recurso no degrau dos Quilombolas.
3. **Given** a segunda pessoa de I ocupa a ampla com aceite registrado, **When** ela abre a ocupação de
   PP, **Then** o degrau de I é saltado por isso, e a razão diz que ela ocupa pela ampla.
4. **Given** a segunda pessoa de I é titular da apuração da ampla sem aceite, **When** ela abre a
   ocupação de PP, **Then** a passagem não é oferecida, e a tela diz que a ocupação pela ampla ainda
   pode mudar.

---

### User Story 4 — A vaga recebida que fica sem ocupante segue a ordem da origem (Priority: P2)

A vaga de PP foi passada a I. A segunda pessoa de I desiste. A vaga não volta a PP, que já não tinha
ninguém, nem segue a ordem de I: ela continua a ordem de PP **a partir do degrau seguinte** — Q, e
depois a ampla. A tela diz *"vaga dos Pretos e Pardos recebida pelos Indígenas"*.

**Why this priority**: sem a regra, as sequências do 33/2026 devolvem a vaga a uma cota já percorrida
(a ordem de LB_Q começa por LB_PPI), e a vaga circula; depende da P-3.

**Independent Test**: passar a vaga de PP a I, registrar a desistência da pessoa de I e conferir que a
passagem seguinte oferece Q e a ampla, e nunca PP nem I de novo.

**Acceptance Scenarios**:

1. **Given** a vaga de PP em I e a desistência da pessoa que a ocupava, sem mais ninguém em I, **When**
   a presidência abre a ocupação de I, **Then** a tela distingue a vaga própria de I da vaga recebida de
   PP, e oferece passar a recebida pela ordem de PP, a partir de Q.
2. **Given** a mesma, **When** a passagem é confirmada, **Then** o registro cita a passagem anterior, e
   a página pública mostra o caminho inteiro da vaga.
3. **Given** a vaga própria de I sem ocupante, **When** a presidência abre a ocupação, **Then** ela
   segue a ordem declarada para I, como qualquer origem.

---

### User Story 5 — A prévia mostra o caminho da vaga (Priority: P2)

Na prévia da classificação e na do sorteio, cada reservada com vaga sem ocupante mostra a ordem
publicada, os degraus e por que cada um seria saltado, e o destino final — como o que a passagem
**faria**, e não como fato.

**Why this priority**: a `095` e a `098` mostram hoje a cessão à ampla e recusam mostrar cessão a outra
Modalidade (FR-2329 da `095`); sem esta história, a prévia contradiria o caminho oficial.

**Independent Test**: para o cenário mínimo e as variações das US2 a US4, a prévia e o caminho oficial
dão o mesmo destino e os mesmos degraus saltados, sobre as mesmas entradas.

**Acceptance Scenarios**:

1. **Given** o cenário mínimo na prévia da classificação, **When** quem elabora a abre, **Then** PP e Q
   mostram "iria à ampla, saltando Indígenas (ocupada pela própria lista) e Quilombolas (ninguém
   concorre)".
2. **Given** a prévia do sorteio com muitas rodadas, **When** o painel resume, **Then** ele diz em
   quantas rodadas a vaga de PP iria a cada destino.

---

### User Story 6 — A ordem se retifica, e a passagem errada se desfaz (Priority: P3)

A ordem é conteúdo publicado: muda por Retificação, nos limites da P-7, e a passagem já feita fica
lida contra a versão que citou. A passagem confirmada por engano se desfaz pelo ato contrário da
`155`, enquanto nenhuma chamada depender dela.

**Why this priority**: raro, mas sem ele a correção de uma ordem mal composta não tem caminho.

**Independent Test**: passar, desfazer e conferir que os dois registros existem e a vaga voltou à
origem; retificar a ordem depois de uma passagem e conferir que a passagem feita não muda.

**Acceptance Scenarios**:

1. **Given** uma passagem sem chamada dependente, **When** a presidência a desfaz com motivo, **Then**
   a vaga volta à origem, e os dois registros ficam.
2. **Given** a ordem retificada depois de uma passagem, **When** a presidência abre a ocupação,
   **Then** a passagem feita aparece com a versão que citou, e a nova ordem vale para a vaga que ainda
   não passou.
3. **Given** um Perfil publicado com a terceira resposta da `155`, **When** a presidência abre a
   ocupação, **Then** a tela continua a dizer a limitação, e diz que o caminho é retificar a declaração
   na forma desta spec.

---

### User Story 7 — O candidato vê por onde a vaga passou (Priority: P3)

Na página pública da seleção e no relatório do Edital: *"1 vaga reservada aos Pretos e Pardos foi
passada à ampla concorrência em 11/11/2026, conforme o item 9.5.1 do Edital; os Indígenas e os
Quilombolas não tinham quem a ocupasse."*

**Why this priority**: transparência, como a `155` decidiu para a destinação; depende das US2 e US4.

**Independent Test**: depois de uma passagem com dois degraus saltados, a página pública e o relatório
mostram origem, degraus, destino, quantidade e fundamento, sem nome de candidato.

**Acceptance Scenarios**:

1. **Given** uma passagem registrada, **When** alguém abre a página pública sem login, **Then** vê o
   caminho e nenhum nome nem protocolo.

---

### Edge Cases

- **Destino com zero vagas próprias** (LI_Q no 33/2026): todo concorrente dele é excedente, e ele
  recebe a vaga se tiver quem ainda possa ocupá-la.
- **Destino sem nenhuma inscrição**: saltado, com "ninguém concorre" como razão — desde que a ausência
  esteja comprovada como a `155` exige para a lista vazia (FR-6332 e FR-6333 da `155`); dado que falta
  não é ausência, e impede.
- **Excedente fora da faixa do destino**: a faixa da reservada costuma ter o tamanho das vagas dela, e o
  excedente fica fora. Pela FR-6304 da `155`, só é alcançável se o Edital admite continuação; sem ela,
  o degrau seria sempre saltado. É a P-2.
- **Duas origens, um excedente**: PP e Q sem ocupante, um excedente só em I. É a P-6.
- **Destino que é também origem**: Q sem ninguém é origem da vaga própria e destino da de PP; o degrau
  Q é saltado para PP, e a vaga própria de Q segue a ordem de Q.
- **Sequência sem a ampla ao fim**: o que restar não vai a lugar nenhum, e a declaração de não
  preenchida da `155` passa a caber para a vaga que chegou ao fim da ordem.
- **Gatilho por saldo**: a vaga sai da origem pela condição da FR-6305 da `155`; os degraus seguem a
  mesma regra de salto (P-2).
- **Perfil publicado com a terceira resposta da `155`**: continua sem aplicação até ser retificado.
- **Edital encerrado**: nenhum ato desta spec é oferecido.
- **Ator sem permissão**: a recusa é a de qualquer ato da comissão sobre o Processo.

## Requirements *(mandatory)*

### Functional Requirements

**A declaração da ordem** *(P-1)*

- **FR-6600**: O passo Perfis MUST perguntar, para **cada** Modalidade reservada de um Perfil que
  declara gatilho, para onde vai a vaga dela sem ocupante, com três respostas: *"Não passa a lugar
  nenhum"*, *"Direto à ampla concorrência"* e *"Pela ordem: …"*.
- **FR-6601**: A resposta *"Pela ordem"* MUST trazer uma sequência de Modalidades reservadas do
  **mesmo** Perfil, sem a própria origem e sem repetição, e MUST dizer se o que restar ao fim vai à
  ampla do mesmo Perfil.
- **FR-6602**: A publicação MUST ser recusada, com a razão dita na Modalidade, quando: uma reservada de
  Perfil com gatilho não tem resposta; a sequência está vazia, repete Modalidade, inclui a origem, a
  ampla no meio ou Modalidade de outro Perfil; ou uma resposta é dada num Perfil sem gatilho. A
  ausência MUST NOT virar resposta padrão.
- **FR-6603**: O gatilho — por esgotamento ou por saldo — MUST continuar declarado no Perfil (FR-249 da
  `016`), e MUST valer para a saída de cada origem.
- **FR-6604**: A declaração MUST ser conteúdo publicado, com elevação de versão canônica, caminho de
  leitura das versões anteriores e presença no documento, como a espécie (FR-250 da `016`).
- **FR-6605**: Duplicar um Perfil (`043`) ou reaproveitar um Edital (`023`) MUST levar a declaração
  junto, com as Modalidades de destino trocadas pelas correspondentes do novo Perfil.
- **FR-6606**: A terceira resposta da `155`, *"Passa antes por outras cotas, na ordem do Edital"*, MUST
  deixar de ser oferecida em composição nova; o Perfil publicado com ela MUST continuar legível e sem
  aplicação, e a tela MUST dizer que o caminho é retificar a declaração na forma da FR-6600.

**O gatilho em cada degrau** *(P-2)*

- **FR-6607**: A vaga MUST sair da origem pela condição do gatilho do Perfil — a da FR-6304 da `155`
  por esgotamento, a da FR-6305 por saldo — e sob os impedimentos da FR-6306 da `155`.
- **FR-6608**: Um destino MUST ser saltado só quando não houver nele ninguém que ainda possa ocupar
  **além das vagas próprias dele ainda a ocupar**, pelos critérios da FR-6304 da `155` aplicados à
  ordem do destino: com posição, sem desfecho excludente, sem ocupar a ampla com aceite registrado e
  alcançável.
- **FR-6609**: A passagem MUST ser impedida, e não o degrau saltado, quando o destino tiver qualquer dos
  impedimentos da FR-6306 da `155`: resultado do marco não definitivo, prazo recursal aberto ou
  recurso pendente sobre alguém da ordem dele, chamada em curso para ele, alguém dele ocupando a ampla
  sem aceite registrado, ou apuração vigente obsoleta.
- **FR-6610**: A condição de salto MUST ser a mesma em todo degrau, qualquer que seja o gatilho do
  Perfil: o gatilho governa a vaga própria de cada lista, e não a vaga que ela recebe.
- **FR-6611**: Alcançável, no destino, MUST significar o que a FR-6304 da `155` diz — dentro da faixa
  vigente, ou fora dela quando o Edital admite continuação —, salvo decisão diferente do usuário na
  P-2.

**O ato de passagem** *(P-3)*

- **FR-6612**: A passagem MUST ser aplicada por ato próprio, "Passar a vaga pela ordem do Edital",
  praticado por quem pode emitir a apuração do recorte de origem, e MUST NOT ser efeito de nenhum
  outro ato.
- **FR-6613**: Num só ato, o sistema MUST percorrer a ordem degrau a degrau e levar cada vaga ao
  primeiro destino que tem quem a ocupe, até o limite do excedente dele; o que restar MUST seguir a
  ordem; e, chegado o fim, MUST ir à ampla quando a declaração o diz.
- **FR-6614**: Nenhum movimento MUST ser gravado para um destino saltado: o ato grava um movimento por
  destino que recebe, da origem direto a ele.
- **FR-6615**: Antes da confirmação, o sistema MUST mostrar a origem, a ordem publicada, cada degrau com
  o resultado — recebe, saltado com a razão, ou impede —, o destino final de cada vaga, a quantidade, o
  gatilho, a versão do Edital e o efeito em cada destino.
- **FR-6616**: O ato MUST registrar ator, instante, origem, cada destino e a quantidade dele, cada
  degrau saltado com a razão, o gatilho, a declaração e a versão do Edital lidas, as apurações lidas e
  a correlação.
- **FR-6617**: A quantidade passada MUST NOT exceder o saldo da origem, a recebida por um destino MUST
  NOT exceder o excedente dele, e a soma das vagas efetivas por recorte do Perfil MUST ser a mesma
  antes e depois (FR-247 da `016`).
- **FR-6618**: Recebida a vaga, a apuração vigente do destino MUST aparecer obsoleta pela causa do
  movimento (FR-263 da `016`), e o Centro MUST levar à emissão seguinte dele.
- **FR-6619**: Duas confirmações do mesmo ato, simultâneas ou repetidas, MUST produzir um registro só.
- **FR-6620**: Com a declaração *"Direto à ampla concorrência"*, o ato MUST ser o "Destinar à ampla
  concorrência" da `155`, sem degrau; com *"Não passa a lugar nenhum"*, MUST valer o que a `155` diz
  para o Edital silente, inclusive a declaração de não preenchida.
- **FR-6621**: Com qualquer degrau impedido, o ato MUST ser recusado inteiro, e a tela MUST nomear o
  degrau, o impedimento e, quando houver, a data em que ele pode acabar; MUST NOT haver passagem parcial
  que salte o degrau impedido.

**A vaga recebida que fica sem ocupante** *(P-3)*

- **FR-6622**: A vaga recebida MUST conservar a origem: o destino MUST mostrar, separadas, as vagas
  próprias e as recebidas, cada recebida com a sua origem.
- **FR-6623**: Ficando sem ocupante, a vaga recebida MUST seguir a ordem **da origem**, a partir do
  degrau seguinte ao destino em que estava, e MUST NOT voltar a degrau já percorrido nem à origem.
- **FR-6624**: Essa passagem MUST citar a anterior, e o caminho inteiro da vaga MUST ser legível de uma
  vez, da origem ao destino atual.

**Duas origens, um destino** *(P-6)*

- **FR-6625**: Quando duas origens disputam o excedente de um mesmo destino, a precedência MUST ser a
  que a P-6 decidir, e MUST NOT depender de quem confirma primeiro.

**A concomitância no destino**

- **FR-6626**: Quem é da Modalidade de destino e ocupa pela ampla com aceite registrado MUST NOT contar
  como quem pode ocupar a vaga recebida (FR-252 da `016`); a vaga própria dele continua no destino
  (FR-253 da `016`).
- **FR-6627**: Quem ocupa pela ampla sem aceite registrado MUST impedir a passagem pelo degrau dele
  (FR-6609), e a tela MUST dizer que a ocupação pela ampla ainda pode mudar.
- **FR-6628**: Quem ocupa a vaga recebida MUST ser computado nela, e não nas vagas próprias do destino;
  quem ocupa uma vaga própria do destino MUST NOT ser computado na recebida.
- **FR-6629**: A recepção MUST NOT alterar a ordem do destino: a vaga recebida é ocupada pelo próximo da
  ordem do destino, depois das vagas próprias.

**A prévia**

- **FR-6630**: A prévia da classificação (`095`) e a do sorteio (`098`) MUST mostrar, por reservada com
  vaga sem ocupante, a ordem publicada, cada degrau com o resultado e a razão, e o destino final, como o
  que a passagem faria, pela mesma conta do caminho oficial.
- **FR-6631**: A prévia MUST NOT simular desfecho nem recurso: o degrau que no caminho oficial seria
  impedido MUST aparecer como "dependeria do que estiver pendente", e não como saltado.
- **FR-6632**: A prévia do sorteio MUST resumir, com muitas rodadas, em quantas a vaga iria a cada
  destino.
- **FR-6633**: A equivalência das duas prévias com o caminho oficial MUST continuar verificada, agora
  com os degraus.

**O documento do Edital e a Retificação** *(P-7)*

- **FR-6634**: O documento do Edital MUST imprimir, por Modalidade de origem, a frase da declaração:
  para *"Pela ordem"*, *"As vagas reservadas a ‹origem› não preenchidas serão ofertadas, pela ordem, a
  ‹destino 1›, ‹destino 2› … e, restando vagas, à ampla concorrência do mesmo código"*; para *"Direto à
  ampla"*, a frase da espécie que já existe; para *"Não passa"*, que a vaga não passa a outra lista.
- **FR-6635**: Origens com a mesma declaração MUST poder ser impressas numa frase só, e Perfis com a
  mesma declaração, uma vez para o grupo, como o documento já faz com os marcos.
- **FR-6636**: A declaração MUST ter entrada no catálogo de Retificação, com o rótulo do passo Perfis,
  e a regra de mutabilidade que a P-7 decidir.
- **FR-6637**: Retificada a ordem, a passagem feita MUST continuar lida contra a versão que citou, e a
  nova ordem MUST valer só para a vaga que ainda não passou.

**A correção**

- **FR-6638**: A passagem MUST poder ser desfeita pelo ato contrário da `155` (FR-6334 e FR-6335 da
  `155`), que devolve cada vaga à origem e cita o ato que desfaz, enquanto nenhuma chamada depender
  dela.
- **FR-6639**: Desfazer uma passagem posterior (FR-6623) MUST devolver a vaga ao destino anterior, e não
  à origem primeira.

**A publicidade**

- **FR-6640**: A página pública da seleção e o relatório do Edital MUST mostrar cada passagem com a
  origem, os degraus saltados e a razão em palavras, o destino, a quantidade e o fundamento, e MUST
  NOT mostrar nome nem protocolo de candidato.
- **FR-6641**: Esta entrega MUST NOT exigir documento PDF novo.
- **FR-6642**: A chamada de quem ocupa uma vaga recebida MUST citar a passagem no fundamento.

**Registro, permissão e equivalência**

- **FR-6643**: Todo ato desta spec MUST exigir a mesma permissão e o mesmo escopo da emissão da apuração
  da origem, MUST ser negado por padrão a quem não os tem, e MUST entrar na trilha com correlação.
- **FR-6644**: Todo ato desta spec MUST ser reproduzível: relido depois, MUST devolver os degraus, as
  razões, a quantidade e a declaração que leu, e não as de hoje.
- **FR-6645**: As telas e os registros desta spec MUST NOT dizer que alguém foi convocado, aceitou ou se
  matriculou (como a FR-258 da `016`).

### Requisitos de experiência

- **UX-660**: A ordem MUST ser dita com os nomes das Modalidades, em palavras, nunca com código; o
  degrau saltado, com a razão em uma frase ("a única pessoa habilitada ocupa a vaga dos Indígenas",
  "ninguém concorre").
- **UX-661**: O "Confira antes" da passagem MUST seguir o da destinação da `155`, com os degraus numa
  lista na ordem do Edital e o destino final destacado.
- **UX-662**: No passo Perfis, a sequência MUST ser composta escolhendo Modalidades do próprio Perfil,
  sem digitar nome, e MUST mostrar a frase que o documento imprimirá.
- **UX-663**: A vaga recebida MUST ser dita como tal em toda tela que a mostra: *"vaga dos Pretos e
  Pardos recebida pelos Indígenas"*.

### Key Entities

- **Declaração de destino da Modalidade**: por Modalidade reservada de um Perfil, uma de três
  respostas; para *"Pela ordem"*, a sequência de Modalidades do mesmo Perfil e se o que restar vai à
  ampla. Conteúdo publicado.
- **Passagem de vaga**: ato append-only que leva quantidade de uma origem a um ou mais destinos, com os
  degraus saltados e as razões, gatilho, declaração e versão lidas, ator e instante. O movimento de vaga
  da `016`, que já admite destino reservado, é o candidato natural para os movimentos; a escolha é do
  plano.
- **Vaga recebida**: a quantidade que um destino tem por passagem, com a origem e o degrau em que está.
- **Degrau saltado**: o destino percorrido sem receber, com a razão.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2160**: No cenário mínimo, as vagas de PP e Q chegam à ampla com **uma** confirmação cada, e
  cada registro nomeia os dois degraus saltados e a razão de cada um.
- **SC-2161**: Na variação com dois habilitados em I, a vaga de PP vai a I, e o Centro leva à chamada da
  segunda pessoa de I; zero movimentos para a ampla.
- **SC-2162**: Nenhum degrau saltado sob impedimento: zero, conferido por um cenário para cada
  impedimento da FR-6609.
- **SC-2163**: As oito sequências do Anexo 7 do 33/2026 compõem-se e publicam-se como estão, e o
  documento as reproduz na ordem: 8 de 8.
- **SC-2164**: Nos cenários desta spec, a prévia e o caminho oficial dão o mesmo destino e os mesmos
  degraus: 100%.
- **SC-2165**: Nas sequências do 33/2026, com desistência em cada destino, nenhuma vaga volta a degrau
  já percorrido nem à origem: zero.
- **SC-2166**: A soma das vagas efetivas por recorte de um Perfil é a mesma antes e depois de toda
  passagem e todo desfazimento.
- **SC-2167**: Num Perfil do 140/2025 com a declaração feita, duplicá-lo leva a declaração inteira, sem
  interação a mais por Perfil duplicado.
- **SC-2168**: Num roteiro com a presidência de treinamento, a pessoa diz, sem ajuda e lendo só a
  ocupação, por onde a vaga de PP passou e por quê; e um leitor sem login diz o mesmo pela página
  pública.

## Assumptions

- A `155` estará implementada antes desta: a destinação à ampla, o desfazimento, a lista vazia e os
  impedimentos são dela, e esta spec os reaproveita.
- O ato é de quem pode emitir a apuração da origem; não há papel novo.
- A passagem move quantidade entre listas do mesmo Perfil, como a reversão move à ampla; a ordem de
  convocação por posição do Cefor fica fora.
- O cenário mínimo e as variações entram na `134` como cenário de treinamento, se não houver.
- A inscrição continua a concorrer por uma Modalidade, além da ampla.

## Compatibilidade com regras anteriores

As revisões abaixo serão escritas nas próprias specs, com a redação anterior preservada, quando as
perguntas forem respondidas, e vigoram com a implementação desta.

| Regra | O que acontece |
|---|---|
| FR-245 e FR-247 da `016` | continuam |
| FR-246 da `016` (o destino é a linha geral) | **a rever**: o destino pode ser outra Modalidade do mesmo Perfil, na ordem declarada; nunca outro Perfil |
| FR-249 da `016` (as espécies e a terceira resposta) | **a rever**: o gatilho fica no Perfil, e a passagem vai para a declaração por Modalidade (FR-6600, FR-6603) |
| FR-252 e FR-253 da `016` | continuam, e valem em cada degrau (FR-6626) |
| FR-6317 da `155` (a terceira resposta) | **a rever**: deixa de ser oferecida; o Perfil publicado com ela continua legível (FR-6606) |
| FR-6318 e FR-6319 da `155` (a limitação) | **a rever**: valem só para o Perfil publicado com a terceira resposta |
| FR-6309 e FR-6312 da `155` | **a rever**: o lembrete e a recusa passam a ler a declaração da Modalidade |
| FR-6327 da `155` | **a rever**: a declaração de não preenchida cabe à vaga que chegou ao fim de uma ordem sem a ampla |
| FR-6334 e FR-6335 da `155` | continuam, estendidas à passagem (FR-6638) |
| FR-2327 e FR-2329 da `095` | **a rever**: a prévia mostra a cessão a outra Modalidade, com os degraus (FR-6630) |
| FR-2507 da `098` | **a rever**: a prévia do sorteio mostra os degraus (FR-6632) |

## Perguntas ao usuário

As oito perguntas abaixo dependem de norma ou de governança. Cada uma traz a recomendação desta spec,
que os requisitos já seguem.

### P-1 — Como o Perfil declara a ordem

O 173/2025 manda os subgrupos de PPIQ em cascata (9.5.1) e a PcD direto à ampla (9.5.6), no mesmo
Perfil; o 33/2026 dá uma sequência própria a cada uma das oito cotas.

| Opção | Resposta | Implicação |
|---|---|---|
| **A** *(recomendada)* | Por Modalidade de origem: cada reservada declara "não passa", "direto à ampla" ou "pela ordem", com a sua sequência; o gatilho fica no Perfil | Reproduz os quatro Editais. Custa uma pergunta por reservada no passo Perfis; a duplicação da `043` leva junto |
| B | Uma ordem única por Perfil, que toda reservada percorre sem a própria origem | Mais barato; não reproduz o 33/2026 nem a PcD do 173/2025 |
| C | A ordem única, com exceções por Modalidade | Cobre os casos, com duas formas de dizer a mesma coisa |

Inclui: a terceira resposta da `155` deixa de ser oferecida (FR-6606)?

### P-2 — O gatilho em cada degrau, e o excedente fora da faixa

A saída da origem segue o gatilho do Perfil (FR-6607). Em cada destino, a recomendação é saltar só
quando ninguém mais pode ocupar além das vagas próprias (FR-6608), a mesma condição em todo degrau
(FR-6610). Duas questões:

- **(a)** O gatilho do destino importa? *Recomendação: não* — ele governa a vaga própria, e o 173/2025
  ("persistindo a ausência") e o 33/2026 ("restando vagas") falam do destino só como quem tem ou não
  tem quem ocupar.
- **(b)** O excedente do destino costuma estar fora da faixa dele. Pela FR-6304 da `155`, só é
  alcançável se o Edital admite continuação, e sem ela o degrau seria sempre saltado — o que esvazia a
  cascata. As opções: **(i)** manter a FR-6304 como está; **(ii)** *(recomendada)* a vaga recebida
  amplia a faixa do destino na quantidade recebida, porque o Edital que manda passar a vaga manda
  chamar quem a ocupe; **(iii)** exigir que o Edital publique continuação para declarar a ordem.

### P-3 — O destino que também não tem quem ocupar, e a vaga recebida que fica sem ocupante

- **(a)** *Recomendação:* um ato só percorre a ordem e leva a vaga ao primeiro destino que tem quem a
  ocupe, registrando os saltados (FR-6613, FR-6614). Alternativa: um ato por degrau, com movimento a cada
  um — mais confirmações, e movimentos para listas que não podiam receber.
- **(b)** *Recomendação:* a vaga recebida que fica sem ocupante segue a ordem **da origem**, a partir
  do degrau seguinte (FR-6623). Alternativa: segue a ordem do destino, como se fosse dele — no 33/2026,
  a vaga de LB_PPI recebida por LB_Q voltaria a LB_PPI, primeira da ordem de LB_Q.

### P-4 — A passagem impedida por um degrau

*Recomendação:* qualquer degrau impedido recusa o ato inteiro (FR-6621), mesmo que o degrau seguinte
tenha quem ocupe. Alternativa: passar a vaga ao degrau seguinte e reavaliar depois — o que entregaria a
vaga a uma cota que o Edital mandou atender depois, enquanto a anterior ainda podia ocupá-la.

### P-5 — Os "demais subgrupos" do Cefor, sem ordem entre eles

O 140/2025, o 173/2025 e o 90/2026 mandam a vaga aos "demais subgrupos de PPIQ", sem dizer em que ordem
entre os dois que sobram. A spec não interpreta o Decreto nº 12.536/2025.

| Opção | Resposta | Implicação |
|---|---|---|
| **A** *(recomendada)* | Quem elabora declara a ordem, e o documento a publica; para os Editais já publicados, a ordem em que o texto os enumera (pretos/pardos, indígenas, quilombolas) | A ordem fica explícita e pública; a escolha nos Editais já publicados é leitura, e é do usuário |
| B | Os dois subgrupos restantes concorrem juntos, pela classificação | Outra regra de ocupação, sem ordem; não cabe no modelo de degraus |
| C | Recusar a passagem até o Edital declarar a ordem | Fiel ao texto; deixa os três Editais sem passagem |

### P-6 — Duas origens disputando o mesmo excedente

PP e Q sem ocupante e um excedente só em I. O 33/2026 e o Cefor não dizem qual origem tem precedência;
a ordem das linhas do quadro é apresentação, e não norma (E-8).

| Opção | Resposta | Implicação |
|---|---|---|
| **A** *(recomendada)* | A ordem em que as origens são declaradas no Perfil é a precedência, e o documento o diz | Explícita e publicada; a ordem do Anexo 7 (incisos I a VIII) já é uma |
| B | A primeira posição da ordem de convocação do Edital (no Cefor, 9ª Indígenas antes de 26ª Quilombolas) | Exige a ordem por posição, que está fora |
| C | Impedir até a comissão escolher, com fundamento | Decisão caso a caso, sem regra publicada |

### P-7 — A Retificação da ordem

Declarar onde não havia é acréscimo, como a espécie (o catálogo de Retificação admite o acréscimo da
espécie porque dizer como a vaga reverte "não retira nada de quem concorre"). Mudar uma ordem
publicada pode retirar: a cota que era o primeiro degrau passa a ser o terceiro.

| Opção | Resposta | Implicação |
|---|---|---|
| **A** *(recomendada)* | Acréscimo admitido sempre; alteração admitida até a primeira passagem do Perfil, e recusada depois | A passagem feita não perde fundamento; corrige a ordem mal composta antes de ela produzir efeito |
| B | Acréscimo e alteração admitidos sempre, com a passagem feita lida pela versão que citou (FR-6637) | Mais flexível; duas passagens do mesmo Perfil podem seguir ordens diferentes |
| C | Acréscimo admitido; alteração só antes das inscrições | Mais rígida; trava a correção do Perfil já publicado com a terceira resposta |

### P-8 — Os subgrupos do Cefor como Modalidades

Os Editais do Cefor compostos no GPS têm uma PPIQ por Perfil (E-9), e a passagem entre subgrupos só
existe com os subgrupos separados, cada um com a sua quantidade. O 173/2025 os separa na ordem de
convocação (posições de Pretos/Pardos, de Indígenas e de Quilombolas).

| Opção | Resposta | Implicação |
|---|---|---|
| **A** *(recomendada)* | Compor os subgrupos como Modalidades distintas nos próximos Editais, com a quantidade de cada um no quadro; os já publicados seguem com uma PPIQ e a destinação à ampla da `155` | Nada se retroage; a cascata vale do próximo Edital em diante |
| B | Retificar os Editais em curso para separar os subgrupos | Muda quadro publicado, com efeito sobre inscrições já feitas |
| C | Manter uma PPIQ e tratar a cascata como inaplicável no Cefor | Esta spec vale só para Editais como o 33/2026 |

## Decisões

### D-001 — A passagem segue o que o Edital publicou, e não infere

Herdada da regra da `016` de que ausência de declaração não move, e da orientação da `155` de não
interpretar lei. Onde a ordem publicada tem lacuna (P-5) ou erro (o destino "Cota PCD 8" do 33/2026),
a decisão é de quem compõe, publicada, e não do sistema.

### D-002 — Um degrau só se salta com certeza

Saltar um degrau tira a vaga de uma cota que o Edital mandou atender antes. Por isso a condição de
salto é a ausência certa de quem ocupe, e toda situação reversível — chamada, recurso, ocupação pela
ampla sem aceite — impede em vez de saltar, como a `155` decidiu para o esgotamento.

### D-003 — Só recebe quem pode ocupar

Nenhum movimento vai a uma lista saltada: o ato grava da origem direto a quem recebe. Um movimento por
degrau registraria vaga numa lista que não podia ocupá-la, e cada um pediria apuração e passagem
próprias para sair dali.

### D-004 — A vaga recebida conserva a origem

A ordem é da vaga da origem, e não do destino. Sem isso, as sequências do 33/2026 devolvem a vaga a
uma cota já percorrida, e a passagem circula.

## Achados fora do escopo (registro)

- **O Anexo 7 do 33/2026 tem um destino que não é cota** (*"Cota PCD 8"*, inciso V) e uma ordem fora
  do padrão no inciso VII. É questão do Edital do IFFluminense, e não do sistema; o GPS só compõe
  destino que seja Modalidade do Perfil.
- **O 140/2025 e o 90/2026 não dizem o que acontece com a vaga da PcD e da PPT ou PTT sem ocupante**,
  mas o gatilho é do Perfil e valeria para elas. Com a declaração por Modalidade (P-1, A), elas podem
  ser declaradas "não passa"; o que os Editais em curso já publicaram é leitura do usuário.
- **A ordem de convocação por posição** do Cefor (9.5 do 173/2025, 10.5 do 140/2025, 11.2 do 90/2026)
  não é representada no GPS, e define de qual lista sai cada pessoa chamada.
- **A inscrição em mais de uma cota**, com prioridade entre elas (33/2026), não é representada.
- **A terceira resposta da `155` não tem gatilho.** Um Perfil publicado com ela não diz quando a vaga
  sai da origem; esta spec propõe que ela deixe de ser oferecida (FR-6606).
