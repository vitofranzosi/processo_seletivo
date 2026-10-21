# Feature Specification: Cadastro de reserva sem vaga imediata impresso como CR

**Feature Branch**: `claude/cadastro-reserva-zero-cr-45f542`, sobre a `main` em `717fc057`

**Created**: 2026-10-21

**Status**: Draft

**Input**: pedido do usuário em 21/10/2026. O Perfil de cadastro de reserva sem vaga imediata continua
guardando `0` vagas imediatas, mas o documento do Edital deixa de imprimir esse `0`: no lugar dele sai
`CR`, com uma nota que diz o que a sigla quer dizer, como a equipe já faz nos Editais que escreve à mão.
No portal, a oferta continua dita por extenso, e a linha com o zero sai.

**Acréscimo de 21/10/2026, na implementação, por decisão do usuário** (D-012): a nota empurrou o
cenário B uma linha, e a última seção passou a saltar com o fecho do ato só no publicado — um defeito
latente desde a `069`, que a `096` acordou. A prévia passa a reservar o espaço efetivamente
necessário para o fecho, para que o corpo normativo pagine igual nos dois modos (User Story 6).

> **Faixa de identificadores.** Esta spec abre em **FR-2400** e **SC-900**. Na `main` (`717fc057`), e
> nas worktrees e branches remotas medidas em 21/10, o maior FR é o 2345, o maior SC é o 878 e o maior
> UX é o 216. Esta spec não usa UX.

---

## Por que esta feature existe

**Nenhuma decisão escolheu o `0` contra o `CR`.** O `0` impresso é a soma de três decisões que tratavam
de outras coisas:

- A `027` decidiu que o zero é **dado**: *"`0` diz zero — não 'não declarou'"*. É o número que a
  apuração lê, e nenhuma tela pode dizer que o Perfil não declarou quadro. A decisão é sobre o que se
  guarda, e não sobre como o documento o mostra.
- Em 30/09, ao cadastrar o 89/2026 (Mediadores UAB), o usuário mandou tirar a linha "Total 0" da
  tabela de Perfis, porque *"o leitor entendia que o Edital não oferece nada, quando oferece o
  cadastro"*. A célula de cada Perfil continuou dizendo `0`.
- A `067` (ED-12, decisão 003) tirou do documento o quadro de vagas zerado e a frase de reversão do
  Perfil sem vaga, e deixou a tabela de Perfis *"com 'Vagas imediatas: 0'"*. Isso entrou como caso-limite
  herdado. Nenhuma alternativa foi avaliada.

**A prática da equipe é outra, e a amostra mostra isso.** Nenhum Edital de cadastro de reserva da
amostra imprime `0`:

| Edital | O que traz no lugar do número |
|---|---|
| 76/2026, Secretaria Escolar | `CR` nos cinco polos, na coluna "Quantidade de vaga (cadastro de reserva)" |
| 173/2025, Designer Educacional | "Cadastro de Reserva", por extenso, na coluna "Vagas" |
| 140/2025, Tutores Presenciais | nenhum número; o item 4.1 diz que a seleção é para formar cadastro de reserva |

O achado P-2 (`doc/achados-editais-externos.md`) registrou isso em setembro, e ele nunca virou pergunta
de spec.

**O `0` é o mesmo defeito que a linha "Total 0" tinha, uma coluna para dentro.** Quem lê "Vagas: 0"
numa tabela de dezoito Perfis entende que dezesseis deles não oferecem nada, quando oferecem o cadastro.

**O que não muda, e não se negocia aqui:** o número guardado; a validação; a apuração, a ocupação, a
classificação e a convocação; e todo documento já publicado.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O candidato lê a tabela de Perfis de um Edital de cadastro de reserva (Priority: P1)

O candidato abre o Edital de tutores (o cenário B da auditoria de 08/10: dezoito Perfis, dezesseis de
tutor presencial só de cadastro de reserva, dois de tutor a distância com vaga). Na tabela de Perfis,
a coluna de vagas traz `CR` nos dezesseis e o número nos dois. Logo abaixo da tabela, uma nota diz
"CR: cadastro de reserva." A linha de total soma as vagas dos dois Perfis com vaga, como hoje.

**Why this priority**: é o caso que a equipe publica, e a tabela de Perfis é a primeira coisa que o
candidato lê para saber o que o Edital oferece.

**Independent Test**: compor o documento do cenário B pelo fluxo real e contar, no texto extraído, as
células `CR` e as células `0` da tabela de Perfis, e a nota.

**Acceptance Scenarios**:

1. **Given** um Perfil com 0 vaga imediata e cadastro de reserva limitado, **When** o documento é
   composto, **Then** a célula de vagas desse Perfil na tabela de Perfis diz `CR`.
2. **Given** o mesmo Perfil com cadastro de reserva ilimitado, **When** o documento é composto, **Then**
   a célula diz `CR`.
3. **Given** uma tabela de Perfis com pelo menos uma célula `CR`, **When** o documento é composto,
   **Then** logo abaixo dela sai a nota "CR: cadastro de reserva.".
4. **Given** um Edital com Perfis em `CR` e Perfis com vaga, **When** o documento é composto, **Then** a
   linha de total soma só as vagas imediatas, e sai porque a soma é maior que zero.
5. **Given** um Edital em que todo Perfil é `CR`, **When** o documento é composto, **Then** a linha de
   total não sai, como hoje.
6. **Given** um Edital sem nenhum Perfil `CR`, **When** o documento é composto, **Then** a tabela sai
   como hoje, sem a nota.

---

### User Story 2 — O Edital de um Perfil só (Priority: P1)

O Edital de cadastro de reserva de Designer Educacional tem um Perfil só, e o documento o apresenta numa
ficha de pares, sem tabela de Perfis. O par "Vagas imediatas" diz `CR`, o par seguinte diz o cadastro de
reserva ("até 30 classificados" ou "sem limite de classificados"), e a nota sai logo abaixo dos pares.

**Why this priority**: é a outra composição do mesmo dado. Sem ela, o Edital de um Perfil só continuaria
dizendo `0`.

**Independent Test**: compor um Edital de um Perfil só, com 0 vaga e cadastro de reserva, e ler a ficha.

**Acceptance Scenarios**:

1. **Given** um Edital de um Perfil só, com 0 vaga imediata e cadastro de reserva, **When** o documento
   é composto, **Then** o par "Vagas imediatas" diz `CR`, e a nota sai logo abaixo dos pares.
2. **Given** o mesmo Edital com 3 vagas imediatas, **When** o documento é composto, **Then** o par diz
   `3`, e a nota não sai.

---

### User Story 3 — O Edital na apresentação por perguntas (Priority: P2)

Na apresentação por perguntas da `069`, os Perfis sem vaga imediata saem em tabelas por Perfil ou
por grupo de Perfis de mesmo nome, com a coluna "Vagas imediatas". Nos Perfis de cadastro de reserva,
essa coluna diz `CR`, e cada tabela com pelo menos uma célula `CR` traz a nota logo abaixo. O resumo
do começo do documento já diz *"não há vaga imediata; há cadastro de reserva"*, e continua igual.

**Why this priority**: é a apresentação dos Editais novos. É P2 só porque depende da mesma regra da
história 1, e não porque importe menos.

**Independent Test**: compor o cenário B na apresentação por perguntas e contar as células `CR`, as
células `0` e as notas de cada tabela.

**Acceptance Scenarios**:

1. **Given** o cenário B na apresentação por perguntas, **When** o documento é composto, **Then**
   nenhuma tabela de Perfis traz `0` para Perfil com cadastro de reserva, e toda tabela com `CR` traz a
   nota.
2. **Given** o mesmo cenário, **When** o documento é composto, **Then** a tabela de vagas por lista de
   concorrência continua só com os Perfis que têm vaga, como desde a `067`.
3. **Given** o mesmo cenário, **When** o resumo é composto, **Then** ele diz o que diz hoje.

---

### User Story 4 — O candidato no portal (Priority: P2)

A candidata abre a página da seleção no portal. No Perfil de cadastro de reserva, o destaque continua
"Cadastro reserva", com o detalhe ("até 15 classificados, para convocação futura"), como desde a `024`.
A linha secundária *"0 vagas imediatas agora"* sai. Nada de sigla no portal.

**Why this priority**: o portal já dá destaque à oferta. O que sobrava era o zero em posição
secundária, que lê como "não tem nada" logo abaixo de "tem cadastro".

**Independent Test**: abrir a página da seleção de um Edital com Perfis em cadastro de reserva e com
vaga, e ler o bloco de cada Perfil.

**Acceptance Scenarios**:

1. **Given** um Perfil com 0 vaga imediata e cadastro de reserva, **When** a página da seleção é aberta,
   **Then** o bloco do Perfil diz "Cadastro reserva" com o detalhe, e não diz "0 vaga" em lugar nenhum.
2. **Given** um Perfil com vaga imediata, **When** a página é aberta, **Then** o bloco continua como
   hoje, com o número em destaque.
3. **Given** qualquer Perfil, **When** a página é aberta, **Then** a sigla `CR` não aparece.

---

### User Story 5 — A Retificação (Priority: P3)

A Retificação que dá vaga imediata a um Perfil que só tinha cadastro de reserva, ou que zera as vagas de
um Perfil que tem cadastro de reserva, produz um consolidado composto pela regra vigente: o Perfil
passa de `CR` ao número, ou do número a `CR`. A tela de homologação, na gestão, continua dizendo o
antes e o depois do campo com os números.

**Why this priority**: é raro, e o consolidado já é um documento novo, composto pela regra vigente no
momento em que é composto, pelo princípio da `FR-1196` da `064`, como a `067` assumiu.

**Independent Test**: retificar as vagas imediatas de um Perfil de cadastro de reserva e ler o
consolidado e a tela de homologação.

**Acceptance Scenarios**:

1. **Given** uma Retificação que muda as vagas imediatas de um Perfil de cadastro de reserva de 0 para
   2, **When** o consolidado é composto, **Then** a célula do Perfil diz `2`, e a nota só sai se outra
   célula da tabela continuar `CR`.
2. **Given** a mesma Retificação, **When** a tela de homologação a mostra, **Then** ela diz as vagas
   imediatas antes, `0`, e depois, `2`, como hoje.
3. **Given** uma Retificação que zera as vagas de um Perfil com cadastro de reserva, **When** o
   consolidado é composto, **Then** a célula diz `CR`, e a nota sai.

### User Story 6 — Quem revisa a prévia vê a paginação do publicado (Priority: P1)

*Acrescentada na implementação, por decisão do usuário em 21/10/2026 (D-012).*

Quem elabora abre a prévia do Edital de tutores antes de publicar. A última seção, "Disposições
finais", sai na página em que vai sair no publicado, e o sumário diz o mesmo número de página nos
dois. No lugar do fecho, a prévia diz que local, data, autoridade e verificação saem na publicação,
e ocupa o espaço que eles vão ocupar.

**Why this priority**: a prévia existe para que quem revisa veja o documento que vai sair (a `FR-042`
da `008`). Um sumário que diz uma página e um publicado que diz outra é exatamente o que ela promete
não ter. É P1 porque a `096`, sem esta história, deixaria o cenário B nesse estado.

**Independent Test**: compor o cenário B em prévia e em publicado, nas três composições (plana, por
perguntas e a variante) e com autoridades de alturas diferentes, e comparar o corpo normativo página
a página.

**Acceptance Scenarios**:

1. **Given** o cenário B na apresentação plana e uma autoridade com nome, cargo e ato de nomeação,
   **When** a prévia e o publicado são compostos, **Then** os dois têm o mesmo número de páginas, o
   mesmo corpo normativo em cada página e o mesmo sumário.
2. **Given** o mesmo cenário sem a reserva do fecho, **When** os dois são compostos, **Then** eles
   divergem: é o defeito que a história corrige, e o teste o prova.
3. **Given** uma autoridade prevista, **When** a reserva é composta, **Then** ela tem a mesma sequência
   de linhas, alturas, espaços e ligações de paginação do fecho real.
4. **Given** a prévia, **When** ela é lida, **Then** não traz o nome, o cargo, o ato de nomeação, a data
   nem o resumo criptográfico, e diz que o fecho sai na publicação.

### Edge Cases

- **Perfil com 0 vaga imediata e sem cadastro de reserva.** Continua imprimindo `0`. O Perfil não
  oferece nada, e `CR` afirmaria um cadastro que o Edital não declara.
- **Perfil com 0 no total e uma linha do quadro positiva.** É incoerente, e a validação o recusa. Se
  chegar ao documento, continua imprimindo `0`, como a `067` o trata ao imprimir o quadro, para que o
  erro se veja na prévia.
- **Perfil com vaga imediata e cadastro de reserva.** Continua imprimindo o número. O cadastro já está
  na coluna ao lado, e a vaga é a notícia.
- **Cadastro de reserva limitado em 0.** O domínio aceita o limite zero, e `CR` sai porque o tipo
  declarado é de cadastro. A incoerência de um cadastro limitado a ninguém não é desta feature, e fica
  registrada como achado.
- **Edital já publicado.** Seu documento não muda: a publicação é imutável, e o documento publicado não
  se recompõe. Só os documentos compostos depois desta feature saem com `CR`.
- **Prévia do documento na gestão.** Sai pela mesma composição, então diz `CR` antes da publicação.
- **Telas da gestão** (composição, Revisão, visão institucional). Continuam dizendo `0`: ali se lê e se
  edita o campo, que é numérico, e quem compõe precisa ver o número que vai guardar.
- **Numeração das tabelas e conferência de remissões** (a `065`). A nota não é tabela, não ganha número
  e não entra na lista de itens que a conferência usa.
- **Extração de texto e leitura em voz alta.** `CR` sai como texto comum. A nota logo abaixo é o que
  diz a sigla por extenso, a quem lê o documento e a quem o ouve.
- **Várias autoridades vigentes, de alturas diferentes.** A prévia não sabe qual será escolhida no
  ato, e reserva a mais alta (FR-2420). Com a mais alta, a paginação é a mesma; com outra, a prévia
  pode mostrar a última seção uma página adiante do publicado. Hoje cada unidade tem uma autoridade
  vigente, e o limite fica registrado.
- **Nenhuma autoridade vigente.** A publicação é recusada até haver uma; a prévia reserva o fecho sem
  nome nem cargo.
- **O assistente de dúvidas** (a `071` e a `074`). Ele lê o conteúdo publicado, em que o campo continua
  `0`, e pode responder "0 vagas". Isso fica fora desta feature e registrado como achado.

## Requirements *(mandatory)*

### Functional Requirements

#### O dado

- **FR-2400**: As vagas imediatas do Perfil MUST continuar guardadas como número inteiro, com `0` para
  o Perfil sem vaga. Nenhum campo, tipo ou valor novo MUST ser criado, e o conteúdo publicado MUST
  continuar levando o número (D-001).
- **FR-2401**: Validação, apuração, ocupação, classificação e convocação MUST NOT mudar de
  comportamento.

#### O documento do Edital

- **FR-2402**: **Perfil de cadastro de reserva sem vaga imediata** MUST significar o Perfil com 0 vaga
  imediata, nenhuma linha do quadro de vagas com quantidade positiva e cadastro de reserva limitado ou
  ilimitado. Esta regra MUST ser a única que decide entre o
  número e `CR`, nas duas redações e nas duas apresentações do documento, a plana e a por perguntas.
- **FR-2403**: Na tabela de Perfis, a célula de vagas de um Perfil de cadastro de reserva sem vaga
  imediata MUST dizer `CR`, nas duas redações da apresentação plana.
- **FR-2404**: Na ficha do Edital de um Perfil só, o valor do par "Vagas imediatas" de um Perfil de
  cadastro de reserva sem vaga imediata MUST dizer `CR`.
- **FR-2405**: Na apresentação por perguntas da `069`, as tabelas de Perfis por Perfil e por grupo de
  Perfis de mesmo nome MUST dizer `CR` na coluna de vagas imediatas de todo Perfil de cadastro de
  reserva sem vaga imediata.
- **FR-2406**: Logo abaixo de toda tabela ou ficha que imprimir pelo menos um `CR`, o documento MUST
  imprimir a nota "CR: cadastro de reserva.". Tabela ou ficha sem `CR` MUST NOT trazer a nota (D-002).
- **FR-2407**: A linha de total da tabela de Perfis MUST somar só as vagas imediatas, sem contar as
  células `CR`, e MUST continuar saindo só quando a soma for maior que zero, como pede a `FR-997` da
  `054`.
- **FR-2408**: O Perfil com 0 vaga imediata e sem cadastro de reserva MUST continuar imprimindo `0`. O
  Perfil com vaga imediata MUST continuar imprimindo o número, tenha ou não cadastro de reserva.
- **FR-2409**: Um Edital sem nenhum Perfil de cadastro de reserva sem vaga imediata MUST sair com o
  mesmo texto que sairia antes desta feature.
- **FR-2410**: A nota MUST NOT ser numerada como tabela, nem entrar na lista de itens que a conferência
  de remissões da `065` usa.

#### A Retificação

- **FR-2411**: O consolidado da Retificação MUST aplicar as regras de FR-2402 a FR-2410 ao estado
  vigente de cada Perfil.
- **FR-2412**: A tela de homologação da Retificação, na gestão, MUST continuar dizendo o antes e o
  depois das vagas imediatas com os números, inclusive o `0` (D-003). O documento da Retificação e o
  histórico do portal não listam valores alterados, e continuam sem listar.

  *Corrigido na implementação (21/10):* esta exigência falava num "quadro de alterações" com
  valores. O antes e o depois só existem na tela de homologação (`interface/views.py`,
  `_alteracoes_legiveis`); o histórico do portal diz onde e qual campo, sem valor
  (`publicacoes/domain/alteracoes.py`), e o documento não tem quadro de alterações.

#### Os documentos já publicados

- **FR-2413**: Nenhum documento já publicado MUST mudar. Esta feature só alcança documentos compostos
  depois dela.

#### O portal

- **FR-2414**: No portal, o bloco do Perfil de cadastro de reserva sem vaga imediata MUST continuar
  dizendo a oferta de cadastro de reserva por extenso, em destaque, e MUST NOT dizer o número de vagas
  imediatas. Isso revisa a `FR-136` da `024` no trecho *"o número de vagas imediatas continua dito"*, e
  mantém o resto dela (D-004).
- **FR-2415**: O portal MUST NOT usar a sigla `CR`.
- **FR-2416**: O bloco do Perfil com vaga imediata e os cartões das seleções MUST continuar como hoje.

#### A gestão

- **FR-2417**: As telas da gestão MUST continuar mostrando as vagas imediatas como número, inclusive o
  `0`. A prévia do documento MUST seguir a composição do documento.

#### A paginação da prévia (D-012)

- **FR-2418**: A prévia MUST paginar o corpo normativo como o publicado: o mesmo número de páginas, as
  mesmas linhas em cada página e o mesmo sumário, com a última seção junto do fecho nos dois modos,
  como pede a `FR-1391` da `069`.
- **FR-2419**: No lugar do fecho, a prévia MUST reservar o espaço efetivamente necessário para ele: o
  fecho composto com a autoridade prevista, linha a linha, com a mesma altura, o mesmo espaço antes e
  a mesma ligação de paginação de cada linha. Um aviso de altura menor MUST NOT bastar.
- **FR-2420**: As autoridades previstas MUST ser as vigentes da unidade do Edital na data da prévia.
  Com várias, a reserva MUST ser a do fecho mais alto; sem nenhuma, a do fecho sem nome nem cargo.
- **FR-2421**: A prévia MUST NOT imprimir a autoridade prevista, o local, a data nem o resumo
  criptográfico, e MUST dizer, na primeira linha do espaço reservado, que o fecho sai na publicação. O
  documento publicado MUST recusar autoridade prevista, e continua a compor o fecho como hoje.

### Key Entities

- **Perfil de Vaga**: já existe. As vagas imediatas e o tipo e o limite do cadastro de reserva continuam
  como estão. Esta feature não muda o Perfil; muda só como o documento e o portal o apresentam.

## Decisões

### D-001 — Guardar o 0 e mostrar CR

O `0` é o dado que a apuração, o déficit e a ocupação leem, e a `027` existe para que ele queira dizer
zero. `CR` é a forma de apresentar esse zero quando o Perfil declara cadastro de reserva, e por isso
nasce na composição, e não no Perfil. **Descartadas:** um campo de texto que aceitasse `CR` no lugar do
número, que misturaria texto num número e quebraria a conta; e um tipo novo de oferta, "só cadastro",
que duplicaria o que o par vagas e cadastro já diz, contra a fonte única do Princípio II.

### D-002 — A sigla, com uma nota em toda tabela que a usa

`CR` é como a equipe escreve (o 76/2026), e cabe na coluna de vagas, que é estreita: o cenário B tem
dezoito linhas, e "Cadastro de reserva" por extenso em cada uma quebraria a coluna em três linhas e
repetiria o que a coluna ao lado já diz. A nota vai abaixo de **cada** tabela que usa a sigla, e não
uma vez só no documento: quem procura o seu Perfil salta direto para a tabela, e uma nota que estivesse
em outra página não seria lida. **Descartadas:** a sigla sem nota, que o candidato de primeira viagem não
conhece; e uma tabela de siglas no começo do documento, longe do lugar onde a sigla aparece.

### D-003 — A homologação guarda o número

A tela de homologação da Retificação diz que campo mudou, de quanto para quanto. Ela registra o ato, e
o campo é numérico: "de CR para 2" diria uma mudança de tipo que não aconteceu. O consolidado, que é o
que o candidato lê como o Edital vigente, é que usa `CR`.

### D-004 — No portal, por extenso e sem o zero

Decisão do usuário em 21/10/2026. O portal já dá destaque à oferta de cadastro de reserva desde a `024`
(a decisão 007 dela). O que sobrava era o zero em posição secundária, *"0 vagas imediatas agora"*, que
lê como ausência logo abaixo da oferta. A web não tem legenda de tabela para explicar a sigla, então o
portal continua por extenso. **Descartadas:** a sigla `CR` também no portal, para o portal e o documento
dizerem o mesmo; e deixar o portal como está.

### D-012 — A prévia reserva o espaço do fecho

Decisão do usuário em 21/10/2026, na implementação. A nota da sigla empurrou o cenário B uma linha, e a
última seção, que terminava a uma linha do pé da página, passou a não caber com o fecho: no publicado
ela salta para a página seguinte com ele (a `FR-1391` da `069`); na prévia, que não tem fecho, ela
ficava. O sumário da prévia dizia "15", o do publicado "16", e o guardião da `FR-042` da `008`
reprovou. O defeito existe desde a `069`: qualquer linha a mais ou a menos perto do fim o acorda.

A prévia passa a reservar, no lugar do fecho, o espaço **efetivamente necessário**: o fecho é composto
de verdade, com a autoridade que pode responder pelo ato, e cada linha passa à prévia com a mesma
geometria; só o texto muda. O escopo é só a paginação do corpo normativo: o publicado não muda, e os
documentos já publicados também não. Como a reserva é feita está em `research.md` (D-013).

**Descartadas:** declarar no teste da `008` que a última seção pode saltar só no publicado, o que
deixaria a prévia mostrando uma página a menos; parar a `096` e registrar o achado, com a suíte
vermelha; e um aviso de uma linha no lugar do fecho, que só trocaria um acaso por outro, porque o
salto depende da altura.

## Success Criteria *(mandatory)*

- **SC-900**: No documento do cenário B composto nas duas apresentações, **zero** células `0` de vagas
  imediatas em Perfis com cadastro de reserva, **16** células `CR` em cada apresentação, e a nota em **toda**
  tabela que tiver `CR`.
- **SC-901**: Um Edital sem Perfil de cadastro de reserva sem vaga imediata sai, nas duas apresentações, com
  o texto extraído **idêntico** ao composto antes desta feature.
- **SC-902**: Na página da seleção do portal, **zero** ocorrências de "0 vaga" e de `CR` nos blocos de
  Perfil de cadastro de reserva sem vaga imediata.
- **SC-903**: A suíte contra PostgreSQL continua sem falhas, e **nenhum** teste de apuração, ocupação,
  classificação ou convocação muda.
- **SC-904**: No cenário B, nas três composições (plana, por perguntas e a variante) e com **três**
  autoridades de alturas diferentes, prévia e publicado têm o **mesmo** número de páginas e o **mesmo**
  corpo normativo página a página; sem a reserva, o B plano diverge, e o teste o acusa.

## Assumptions

- `CR` sai em maiúsculas e sem ponto, como no 76/2026.
- A nota é uma linha de texto, no corpo das notas do documento, e não uma tabela nem um par.
- O cenário B da auditoria (`doc/auditoria-edital-pdf-2026-10-08/cenarios/cenario_b_corrigido.py`)
  representa o Edital de cadastro de reserva com Perfis sem vaga e com vaga, e é composto pelo fluxo
  real num banco de validação novo, com dados fictícios.
- O documento de um Edital continua sendo composto uma vez, na publicação, e guardado. Rever o documento
  de um Edital publicado pede re-semear o banco de demonstração.
- Os casos-limite desta spec são requisitos e entram na matriz de rastreabilidade com teste próprio, como
  os `FR-` e os `SC-`.

## Fora do escopo

- **Convocar do cadastro de reserva**, que a `DP-05` deixou fora do piloto em 26/09.
- **O cadastro de reserva limitado em 0**, que o domínio aceita e o documento imprime como cadastro.
- **O assistente de dúvidas**, que lê o `0` do conteúdo publicado.
- **Repartir o cadastro de reserva por Modalidade**, que a `025` deixou fora com razão escrita.
