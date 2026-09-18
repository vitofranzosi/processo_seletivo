# Feature Specification: Navegação por capacidade

**Feature Branch**: `033-navegacao-por-capacidade`

**Created**: 2026-09-18

**Status**: Draft

**Input**: Reauditoria exploratória de UX de 2026-09-16 —
[doc/auditoria-exploratoria-ux-2026-09-16.md](../../doc/auditoria-exploratoria-ux-2026-09-16.md) —,
problema estrutural **E-2**, melhoria **13.3**, achados **ACH-40** (S3/P0), **ACH-35** (S2/P1) e
**ACH-38** (S2/P1). Estado reconferido no código em 18/09/2026 —
[doc/reavaliacao-ux-2026-09-18.md](../../doc/reavaliacao-ux-2026-09-18.md).

## Por que esta feature existe

O produto tem **dois eixos de autorização**, e isso é correto: o **papel institucional**
(`resultado:publicar`, `comissao:gerir`, `recurso:julgar`…) e o **vínculo de comissão** — presidir e
avaliar não são papéis, vêm do vínculo.

O defeito é que **a navegação é montada por um eixo e as permissões pelo outro**.

| Achado | O que acontece |
|---|---|
| **ACH-40** · S3/P0 | O Publicador puro **pode** publicar o resultado, a tela de publicar **abre** — e a tela do Edital não mostra caminho nenhum até ela. Ele só chega se souber montar a URL |
| **ACH-35** · S2/P1 | A recusa por vínculo responde **404 mudo**. Em todo o resto o produto explica e indica o próximo passo; aqui, silêncio — e em produção será um 404 genérico |
| **ACH-38** · S2/P1 | O espelho do ACH-40: a presidência é **mandada divulgar**, segue a instrução e encontra *"Você não tem ação disponível sobre este ato"*, sem dizer a quem pedir |

**A regra certa já está implementada neste repositório — para um tipo de pergunta.** Não é só prosa:
a camada de segurança tem uma função que recusa por **uma capacidade nomeada** com "você não tem
permissão", e por **escopo institucional** com "não encontrado". Duas das seis portas da gestão a
usam, e acertam.

**O que não existe é recusa para a pergunta composta.** Boa parte das portas não pergunta por *uma*
capacidade: pergunta por uma **base de autorização** — a permissão de gerir a comissão **ou** a
presidência daquele Processo, cada uma suficiente sozinha —, e há porta que aceita essa base **ou** a
capacidade de consultar auditoria. Para isso a camada de segurança não oferece nada, e **cada porta
que depende de um predicado composto improvisou o seu próprio "não encontrado"**.

A medição de 18/09/2026:

| Porta | Escopo | O que ela pergunta | Recusa hoje |
|---|---|---|---|
| a da divulgação, a do recurso | ✅ | **uma capacidade nomeada** | ✅ recusa explicada |
| a do marco | ✅ | base **ou** capacidade de auditoria | ❌ "não encontrado" |
| a da consulta de Etapa | ✅ | base **ou** capacidade de auditoria | ❌ "não encontrado" |
| a da gestão do Processo | ✅ | **base** | ❌ "não encontrado" |
| **a da distribuição** | ⚠️ na mesma condição da base | **base** | ❌ "não encontrado" |

**Nenhuma das quatro erra no escopo, e nenhuma erra por descuido isolado**: as quatro fazem a mesma
pergunta que a camada de segurança não sabe responder.

**Esta feature não inventa gramática: ela completa a que existe**, dando à base de autorização o
mesmo tratamento que a capacidade nomeada já tem, num ponto único. E há uma peça pronta para isso —
a função que decide a base **já devolve um objeto que nomeia qual delas autorizou**. Falta o espelho:
nomear o que faltou quando não autoriza.

**Esta feature não cria capacidade nenhuma e não afrouxa autorização nenhuma.** O que muda é **de
onde a navegação é derivada** e **como a recusa se apresenta**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O Publicador puro chega à divulgação sem digitar URL (Priority: P1)

Uma servidora com o papel de Publicador, **sem vínculo de comissão nenhum**, precisa divulgar o
resultado de um certame. Ela abre o Edital, vê os marcos classificatórios e os atos emitidos, e
chega à divulgação clicando. Ela não precisa saber que existe uma URL, nem pedir a alguém da
comissão que faça por ela.

**Why this priority**: é o achado P0 desta família, e é o que torna executável a **segregação de
papéis que o próprio produto recomenda**. Hoje, na configuração segregada, o resultado só é
publicado por quem também pertence à comissão — o que anula a segregação.

**Independent Test**: entrar como Publicador puro, abrir a tela de um Edital com ato de classificação
emitido, e chegar à divulgação sem digitar URL.

**Acceptance Scenarios**:

1. **Given** um ator que tem `resultado:publicar` e nenhum vínculo de comissão, **When** ele abre a
   tela de um Edital publicado com marcos e atos emitidos, **Then** ele vê os marcos e, para cada
   ato, o caminho até a divulgação.
2. **Given** o mesmo ator, **When** ele segue esse caminho, **Then** a tela de divulgação abre — sem
   recusa, porque a capacidade dele sempre bastou.
3. **Given** um ator que preside a comissão e **não** tem `resultado:publicar`, **When** ele abre a
   mesma tela, **Then** ele continua vendo os destinos que alcança hoje — ordenação, sorteio, corte,
   ocupação —, e **nenhum a menos**.
4. **Given** um ator que preside **e** publica, **When** ele abre a tela, **Then** ele vê os destinos
   dos dois eixos, sem duplicação confusa.
5. **Given** um ator sem nenhuma das duas coisas — nem capacidade sobre o resultado, nem vínculo —,
   **When** ele abre a tela, **Then** ele **não** vê caminho que não alcança.

---

### User Story 2 - A recusa se explica, e o 404 volta a significar uma coisa só (Priority: P2)

Um ator abre uma tela que a autorização não lhe dá. Em vez de um "não encontrado" que o faz duvidar
do link, ele lê que não tem permissão, o que falta e a quem pedir. O "não encontrado" fica reservado
ao que é de outro escopo institucional — e aí ele é proteção de dados, não inconsistência.

**Why this priority**: é o que torna o produto coerente consigo mesmo. E a medição mostra que o
buraco é **um só, e tem nome**: a camada de segurança sabe recusar **uma capacidade nomeada** e
**escopo institucional**, e duas das seis portas a usam. O que ela não sabe recusar é o **predicado
composto** — "esta capacidade **ou** aquele vínculo" — que é o que as outras quatro perguntam. Cada
uma improvisou o seu `raise Http404`, e improvisaram igual porque o buraco é o mesmo.

**Independent Test**: entrar como Publicador puro e abrir a tela de **distribuição** do mesmo Edital
— cuja porta é `_etapa_para_distribuir`. Hoje responde "não encontrado"; deve responder recusa
explicada.

**Acceptance Scenarios**:

1. **Given** um ator do mesmo escopo institucional que não tem a capacidade exigida por uma tela,
   **When** ele a abre, **Then** o sistema responde **recusa explicada**, e não "não encontrado".
2. **Given** um ator do mesmo escopo que não satisfaz **nenhuma** das bases que a tela aceita —
   nem a capacidade, nem o vínculo —, **When** ele a abre, **Then** o sistema responde recusa
   explicada, nomeando **as duas** bases que teriam servido, e não apenas uma.
3. **Given** um ator de **outro escopo institucional**, **When** ele abre a tela de um Edital que não
   é do escopo dele, **Then** o sistema responde **"não encontrado"** — e isso não muda.
4. **Given** um identificador que não corresponde a objeto nenhum, **When** a tela é aberta, **Then**
   o sistema responde "não encontrado" — que é a resposta verdadeira.
5. **Given** qualquer uma das recusas acima, **When** ela acontece, **Then** **nada foi alterado**, e
   a tela diz isso.

---

### User Story 3 - Quem trava sabe a quem pedir (Priority: P3)

Um ator chega a uma tela onde não tem ação disponível. Em vez de um beco, ele lê **qual capacidade
resolve** e que deve pedir a alguém que a tenha — exatamente como a tela do Edital já faz quando
diz *"Peça a alguém com a permissão de publicar que conclua o ato."*

**Why this priority**: é a de menor esforço das três e a que o próprio relatório chamou de "mudança
de maior retorno por linha alterada". Depende das outras duas apenas para não repetir texto.

**Independent Test**: entrar como presidência sem `resultado:publicar`, abrir a tela do ato de
classificação e ler o que hoje é *"Você não tem ação disponível sobre este ato"*.

**Acceptance Scenarios**:

1. **Given** um ator na tela de um ato sobre o qual não tem ação, **When** a tela é desenhada,
   **Then** ela nomeia a capacidade que resolve e diz para pedir a quem a tem.
2. **Given** um ator que trava por falta de **vínculo**, e não de papel, **When** a tela é desenhada,
   **Then** ela nomeia o **vínculo** — presidência da comissão —, e não um papel que não existe.
3. **Given** qualquer das frases acima, **When** ela é escrita, **Then** ela segue o padrão que a
   tela do Edital já pratica, sem inventar uma segunda formulação para a mesma coisa.

---

### Edge Cases

- **Escopo institucional continua sendo 404, e é deliberado.** É proteção de dados: o ator não deve
  sequer saber que o Edital existe. Trocar isso por recusa explicada vazaria a existência de Editais
  de outras unidades.
- **Objeto inexistente continua sendo 404.** Um identificador que não corresponde a nada não é
  recusa de autorização, e não pertence a esta família.
- **Ator com `auditoria:consultar`.** Lê sem emitir, hoje e depois. Esta feature não muda o que ele
  alcança — muda que ele veja apenas o que alcança.
- **Edital ainda não publicado.** Não há marcos publicados a listar, e o bloco não aparece para ator
  nenhum. A ausência não é recusa.
- **Ato ainda não emitido.** Quem publica não tem o que divulgar; a tela do Edital diz isso, em vez
  de oferecer um caminho que termina em nada.
- **Ator que acumula papéis.** É o caso normal numa equipe de duas ou três pessoas. A tela oferece a
  união do que ele alcança, sem repetir o mesmo destino duas vezes.

## Requirements *(mandatory)*

### Functional Requirements

#### A navegação derivada da capacidade

- **FR-473**: A tela do Edital MUST oferecer a cada ator os destinos que **aquele ator** alcança,
  derivados das capacidades e dos vínculos dele — e não de uma única porta escolhida de antemão.
- **FR-474**: Ator que detém `resultado:publicar` MUST ver, na tela do Edital, os marcos
  classificatórios e os atos emitidos deles, com o caminho até a divulgação.
- **FR-475**: Ator que preside a comissão MUST continuar vendo **todos** os destinos que vê hoje.
  Esta feature MUST NOT retirar caminho de ninguém.
- **FR-476**: Nenhuma tela MUST oferecer caminho que o ator não alcança. É o princípio que o produto
  já declara — *oferecer o que se vai recusar é pior do que não oferecer* — aplicado por capacidade,
  e não por uma porta só. **Como princípio ele vale para o produto inteiro; como requisito desta
  feature, ele é verificado nas telas que ela alcança** — a do Edital e a do ato. Escrevê-lo como
  obrigação universal o tornaria impossível de fechar, e um requisito que não fecha não é requisito.
- **FR-477**: Texto que instrui o operador a ir a outra tela MUST levar ao destino que **aquele**
  ator alcança, ou declarar que aquele caminho não é dele.

#### A gramática da recusa

- **FR-478**: Recusa por **capacidade** MUST ser apresentada como recusa explicada, e MUST NOT ser
  apresentada como "não encontrado".
- **FR-479**: Recusa por **base de autorização** — o predicado composto que aceita uma capacidade
  **ou** um vínculo, cada um suficiente sozinho — MUST seguir a mesma gramática da recusa por
  capacidade nomeada, e MUST ter **um ponto único**, ao lado do que a camada de segurança já oferece.
  Cada porta improvisar o seu é o que produziu a divergência atual, e é o que produziria a próxima.
  A recusa MUST nomear **as bases que teriam servido**, e não apenas uma delas.
- **FR-480**: "Não encontrado" MUST ficar reservado a duas situações, e apenas a elas: objeto que não
  existe, e objeto de **outro escopo institucional**. A segunda é proteção de dados e MUST NOT mudar.
- **FR-481**: Toda recusa desta família MUST nomear **o que falta** — a capacidade ou o vínculo — e
  MUST declarar que nada foi alterado.
- **FR-482**: A verificação de autorização MUST continuar no servidor. Retirar um link da tela MUST
  NOT substituir a recusa: quem montar a URL à mão continua recebendo a mesma resposta.
- **FR-483**: Nenhuma capacidade nova MUST ser criada, e nenhuma regra de autorização MUST ser
  afrouxada. O conjunto de pares (ator, tela) que abre depois desta feature MUST ser exatamente o
  que abre antes dela.
- **FR-487**: O que garante `FR-480` MUST ser o **filtro por escopo na própria consulta** que busca
  o objeto, de modo que objeto fora de escopo seja **indistinguível** de objeto inexistente. Buscar
  o objeto sem filtrar por escopo e decidir depois MUST NOT acontecer — é a única ordem que vaza, e
  nenhuma porta a pratica hoje.
- **FR-488**: Porta que hoje decide escopo e vínculo na **mesma condição** MUST separá-las antes de
  mudar de gramática. Trocar a resposta sem separar responderia recusa explicada também para objeto
  de outra unidade.

#### Quem trava sabe a quem pedir

- **FR-484**: Tela em que o ator não tem ação disponível MUST nomear a capacidade que resolve e
  instruir a pedir a quem a detém.
- **FR-485**: Quando o que falta é **vínculo**, a frase MUST nomear o vínculo, e MUST NOT nomear um
  papel que não concede aquilo.
- **FR-486**: As frases desta família MUST seguir a formulação que a tela do Edital já pratica, sem
  criar uma segunda gramática para a mesma coisa.

### Key Entities

- **Ator**: quem está usando o sistema. Carrega escopo institucional, capacidades de papel e vínculos
  de comissão. Os três eixos são independentes.
- **Capacidade**: o que um papel institucional concede — `resultado:publicar`, `comissao:gerir`,
  `auditoria:consultar`, `recurso:julgar` e as demais.
- **Vínculo de comissão**: presidência e avaliação. Não é papel, vem da composição da comissão, e é
  por isso que a navegação não pode derivar só dele.
- **Escopo institucional**: a fronteira que separa o que o ator pode ver do que ele não deve saber
  que existe. É o único eixo cuja negativa é "não encontrado".
- **Porta de autorização**: o ponto onde uma tela decide se abre. Hoje são quatro na gestão, e elas
  discordam entre si sobre a gramática da negativa.
- **Destino**: para onde a tela do Edital leva. Hoje é um só por marco; passa a ser o que cada ator
  alcança.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-164**: Um Publicador puro, sem vínculo de comissão, vai da tela do Edital até a divulgação do
  resultado com **zero URLs digitadas**.
- **SC-165**: Nenhuma porta de autorização da gestão responde "não encontrado" para recusa de
  capacidade ou de vínculo. As duas únicas origens de "não encontrado" passam a ser objeto
  inexistente e outro escopo institucional. **E o critério é verificado por varredura, não caso a
  caso**: uma porta acrescentada depois desta feature, com a gramática antiga, tem de ser recusada
  pela suíte — senão o critério vale para o dia em que foi conferido e não para os seguintes.
- **SC-166**: 100% das recusas desta família nomeiam a capacidade ou o vínculo que as resolve, e a
  varredura de `SC-165` também cobre esta contagem.
- **SC-167**: Percorrendo os seis papéis que o seletor de identidade oferece, **nenhum** deles vê, na
  tela do Edital, um caminho que não consegue abrir — e nenhum deixa de ver um que conseguia.
- **SC-168**: O conjunto de pares (ator, tela) que abre é **idêntico** antes e depois da feature.
  Nenhuma tela passa a abrir para quem não abria.

## Assumptions

- A tela de recusa e o mecanismo que a produz **já existem** e alcançam toda a gestão: uma recusa do
  domínio com status 403 vira página com título, motivo e a frase de que nada foi alterado. Esta
  feature usa o que existe; não constrói um segundo mecanismo.
- **A superfície autorizativa desta feature não está medida, e a spec não a estima.** O único número
  conferido é que a interface administrativa tem **75** pontos que respondem "não encontrado". A
  repartição entre *objeto inexistente*, *escopo institucional* e *recusa de autorização* sai do
  inventário, que é a primeira coisa que o plano manda fazer.
  O que se sabe é o bastante para escrever os requisitos e não para declarar o tamanho: a porta que
  erra a gramática está identificada e governa **23 telas**, e nem toda função que responde "não
  encontrado" é porta — `_ato_para_publicar`, por exemplo, não recebe ator nenhum e apenas busca o
  ato dentro de um Edital já autorizado.
  **Se o inventário encontrar recusa de autorização fora das portas já identificadas, o tamanho da
  feature mudou** — e isso é conversa de escopo com quem governa o backlog, não decisão de quem
  implementa.
- O seletor de identidade, usado para percorrer os papéis em `SC-167`, é recurso de demonstração e
  não existe em produção. Ele serve à verificação, não ao requisito.
- A equipe real deste sistema tem duas ou três pessoas, que acumulam papéis. A feature é escrita para
  o caso segregado **e** para o acumulado, porque os dois acontecem.

## Out of Scope

Cada item abaixo tem spec própria a abrir, e nenhum é escopo desta.

- **Renderizador normativo único das telas de ato** — `ACH-39`, `ACH-31`, `ACH-45`, melhoria 13.4.
  As telas continuam com UUID e vocabulário de máquina; o que muda aqui é **quem chega** a elas.
- **Ato de instrução do recurso e o parecer que chega ao candidato** — `ACH-43`, `ACH-42`,
  melhoria 13.2.
- **Validação cruzada entre fontes normativas** — melhoria 13.5.
- **Painel de condução do Processo vivo** — `ACH-25`, melhoria 13.6.
- **Executabilidade antes de publicar** — já especificada na `032`. Em particular, o link do corte na
  tela do Edital continua condicionado à regra de corte declarada; esta feature **não** o altera.
- **Caminho da raiz pública para a gestão** — `ACH-01`. É encontrabilidade, não capacidade.

## Conformidade com a Constituição

**Princípio III — Segurança, Proteção de Dados e Auditoria.** É o princípio que governa esta feature,
e o que a torna delicada: ela muda **como a negativa se apresenta**, e negativa é superfície de
segurança. Três garantias respondem por isso: `FR-482` mantém a verificação no servidor, `FR-483`
proíbe afrouxar qualquer regra, e `FR-480` preserva o "não encontrado" para outro escopo
institucional — que é onde ele protege, e não onde ele confunde. `SC-168` é o critério que prende as
três.

**Princípio I — Linguagem Ubíqua.** A feature não inventa vocabulário: ela **estende** a formulação
que a tela do Edital já pratica, e a gramática de negativa que a porta da divulgação já documenta.
Criar uma segunda maneira de dizer a mesma coisa é justamente o que `FR-486` proíbe.

**Princípio VI — Completude de Jornada e Valor Demonstrável.** A capacidade entregue é observável e
é de jornada: o Publicador puro passa a **conseguir divulgar o resultado** pela interface, o que hoje
só acontece por URL montada à mão ou por acúmulo de papéis. É a segregação de papéis que o produto
recomenda passando a ser executável.
