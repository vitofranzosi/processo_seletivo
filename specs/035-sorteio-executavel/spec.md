# Feature Specification: Sorteio executável

**Feature Branch**: `035-sorteio-executavel`

**Created**: 2026-09-18

**Status**: Draft

**Input**: Reauditoria exploratória de UX de 2026-09-16 —
[doc/auditoria-exploratoria-ux-2026-09-16.md](../../doc/auditoria-exploratoria-ux-2026-09-16.md) —,
achados **ACH-55** (S3) e **ACH-51**, problema estrutural **E-1** (a cauda do certame não fecha).
Os cenários **3** e **5** da reauditoria pararam exatamente aqui, e as duas famílias foram escolhidas
**a partir da amostra real** do Cefor — sorteio com cotas é o padrão dominante dela. Estado medido no
código em 18/09/2026, contra a `main` `d30f6d8`.

> **Faixa de identificadores.** Esta spec abre em **FR-507** e **SC-176**. Teto medido em 18/09/2026
> em **todas as worktrees desta máquina**: `FR-506` / `SC-175` / `UX-061`. **Nenhum `UX-` é aberto
> aqui.** As **decisões** reiniciam em `D-001`, porque são lidas dentro da feature que as produziu.

## Por que esta feature existe

O sistema compõe o método do sorteio, publica o Edital, congela o universo — e **não sorteia**. A
tela responde que *"a ocorrência declarada e todas as substitutas previstas pela regra publicada
estão indisponíveis"*, e manda Retificar.

**Não foi a fonte que falhou.** A fonte de demonstração devolve material para qualquer referência.
O que falhou foi a **derivação da referência**: a regra de substituição deriva do **número** da
ocorrência, e quem compôs escreveu a ocorrência em prosa — como um Edital se escreve, e como o rótulo
do campo pede.

### O motor existe, e isso muda o tamanho da feature

A reavaliação de 18/09 classificou o `ACH-55` como *"método do sorteio em prosa, não computável"*, o
que sugere que falta mecanismo. **Falta não.**

| Peça | Estado | Onde |
|---|---|---|
| Material bruto → semente, pela regra publicada | ✅ com **duas** regras de vocabulário fechado, num `select` | `sorteios/domain/normalizacao.py` |
| Derivação da ocorrência seguinte da mesma fonte | ✅ `5900` → `5901`, preservando prefixo e dígitos, com limite de cadeia | `sorteios/domain/substituicao.py` |
| Fonte externa real, e uma de demonstração | ✅ adaptadores, com vocabulário fechado | `sorteios/infrastructure/fontes/` |
| Chave, resumo canônico e manifesto | ✅ com vetores normativos publicados | `sorteios/domain/chave.py`, `manifesto.py` |
| **A forma que a composição pede** | ❌ | três caixas de texto livre |
| **A conferência antes de publicar** | ❌ | a `032` confere presença, não execução |
| **A recusa que diz o que corrigir** | ❌ | ela culpa a fonte externa |

### O defeito, medido: **cinco dos seis campos do método têm guarda, e o sexto não**

A primeira redação desta spec dizia *"três campos de texto livre que nada valida"*. **O `plan`
mediu, e são outros os números** — o que se segue é a medição, e está em
[research.md](research.md), `R-2`.

| Campo do método | Vocabulário | Tem guarda hoje? |
|---|---|---|
| Algoritmo | **fechado**, um elemento | ✅ recusa o que o sistema não executa |
| Fonte | **fechado**, dois nomes | ✅ recusa o que não tem adaptador |
| Instante da ocorrência | livre, exige fuso | ✅ recusa sem fuso |
| Regra de normalização | **fechado** | ✅ |
| Regra de substituição | **fechado** | ✅ |
| **Ocorrência** | **livre, e tem de terminar em número** | ❌ **nenhuma** |

As cinco guardas disparam **ao gravar o rascunho**, e valem tanto para o método próprio do marco
quanto para o método comum do Edital.

**A ocorrência é o único buraco, e é o que quebra o sorteio.** Ela aparece uma única vez no módulo
que valida o método: numa tabela de rótulos, chamada de *"a ocorrência **concreta** que fixará a
semente"*. **O domínio já sabe o que ela é. O formulário não diz.**

### E a tela já sabe ensinar — em dois lugares, para outros campos

| O que existe | Onde |
|---|---|
| **A escolha** entre os valores publicados, montada a partir do próprio vocabulário | na tela de **Retificação**, para **quatro** campos — algoritmo, fonte, normalização e substituição —, por uma função que já existe |
| **A ajuda** com forma, exemplo e consequência | na tela de **composição**, para o instante da ocorrência |

Os dois padrões que esta feature precisa **já são praticados pelo produto**. Nenhum deles alcança os
campos em que errar impede o sorteio de rodar.

### Uma correção à leitura da auditoria

A reauditoria escreveu que *"os campos são texto livre mas precisam ser dado computável"*, citando
**dois**: *"Ocorrência que fixará a semente"* e *"Como a ocorrência decorre da data programada"*.

**O segundo é prosa por desenho, e está certo assim.** Ele é carregado pelo formulário, sai no
documento publicado com o rótulo *Derivação* — e **nenhum caminho de execução o lê**. Quem deriva de
fato é a **regra de substituição**, que já é uma seleção de vocabulário fechado.

Pedir forma computável a ele seria trocar por um código a frase que diz a norma em português, que é
exatamente a função dele. A spec o deixa como está, e registra por quê.

### O que sobra, então

Três coisas, e as três são menores do que a primeira redação desta spec supôs:

1. **A sexta guarda.** A ocorrência ganha a conferência de forma que os outros cinco campos já têm,
   no mesmo lugar e no mesmo momento.
2. **A tela ensina.** Escolha onde o vocabulário é fechado, ajuda onde a forma é livre mas restrita
   — generalizando o que a Retificação e o campo do instante já praticam.
3. **A recusa do dia do sorteio distingue duas causas.** Hoje *"a fonte não publicou"* e *"a
   declaração não pôde ser lida"* caem na mesma frase, e a frase é falsa na segunda. A frase certa
   **já existe**, específica e correta, e é descartada a uma linha de onde seria exibida.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A composição ensina a forma que o motor exige (Priority: P1)

Quem compõe o método do sorteio **escolhe** o algoritmo e a fonte, em vez de digitá-los, e lê, ao
lado da ocorrência, qual forma ela precisa ter.

**Why this priority**: é o elo que faltava, e é o mais barato dos três. Sem ele, os outros dois
tratam o sintoma: a validação recusaria o que a tela acabou de convidar a escrever, e a recusa
explicaria um erro que a tela não ajudou a evitar.

**Independent Test**: compor um marco de sorteio inteiro pela interface, sem saber de antemão que a
ocorrência precisa terminar em número, e chegar a um método que roda.

**Acceptance Scenarios**:

1. **Given** a etapa de Classificação com um marco que ordena por sorteio, **When** se compõe o
   método, **Then** o algoritmo e a fonte são **escolhidos entre os que o sistema executa**, e não
   digitados.
2. **Given** o campo da ocorrência, **When** se chega nele, **Then** a tela diz **a forma** que ele
   precisa ter e **por quê** — que a substituição deriva do número da ocorrência.
3. **Given** um rascunho **criado a partir de Edital anterior** cujo método traz valor fora do
   vocabulário de hoje, **When** se abre a composição dele, **Then** o valor continua legível e
   identificado como o que veio da origem — e **não** aparece como escolha válida.

---

### User Story 2 - A ocorrência ganha a guarda que os outros cinco campos já têm (Priority: P2)

Quem declara uma ocorrência que o motor não consegue derivar é recusado **no mesmo momento** em que
já é recusado por declarar um algoritmo que o sistema não executa — e lê o que precisa corrigir.

**Why this priority**: é a rede. A `US1` faz o erro ficar difícil; esta faz ele ficar impossível de
atravessar a composição. E o lugar dela não é escolha de estilo: **cinco campos irmãos já são
conferidos ali**, e pôr o sexto noutro lugar criaria duas gramáticas para o mesmo tipo de erro.

**Independent Test**: declarar a ocorrência em prosa, gravar, e ser recusado com uma frase que nomeia
o campo e a forma — sem precisar chegar à Revisão para descobrir.

**Acceptance Scenarios**:

1. **Given** um marco de sorteio cuja ocorrência não termina em número, **When** se grava,
   **Then** a composição recusa, nomeando **o campo, a forma e por quê**.
2. **Given** o **método comum do Edital** com a mesma ocorrência, **When** se grava, **Then** a
   recusa é a mesma: a conferência não distingue o método próprio do comum.
3. **Given** um marco que **não** sorteia, ou um Edital sem método algum, **When** se grava,
   **Then** nada desta família dispara.
4. **Given** um Edital **do acervo** cuja ocorrência publicada não tem a forma exigida, **When** se
   pratica uma Retificação sobre ele, **Then** a Retificação **não** é impedida — nem por esta
   guarda, nem por efeito dela.
5. **Given** a mesma ocorrência, **When** o motor tenta derivá-la, **Then** ele recusa **pela mesma
   regra** que a composição aplicou: a composição não aceita o que o sorteio recusaria, nem o
   contrário.

---

### User Story 3 - A recusa do dia do sorteio para de culpar a fonte (Priority: P3)

Quando o sorteio não pode ser observado, a tela distingue **a fonte não publicou** de **a declaração
não pode ser lida**, e na segunda diz o que corrigir.

**Why this priority**: é a menor das três em alcance — depois da `US2`, quase nenhum Edital novo
chega aqui — e a maior para quem já publicou. É a única das três que ajuda o Edital do acervo.

**Independent Test**: com um Edital cuja ocorrência não é derivável, abrir a tela do sorteio e ler
uma frase que nomeia a declaração, e não a indisponibilidade da fonte.

**Acceptance Scenarios**:

1. **Given** um marco cuja ocorrência não termina em número, **When** se abre a tela do sorteio,
   **Then** a frase nomeia **a declaração** como causa, diz qual campo e o que ele precisa ter.
2. **Given** um marco cuja ocorrência é derivável mas cuja fonte está de fato indisponível, **When**
   se abre a tela, **Then** a frase continua dizendo **o que diz hoje** — a causa é outra, e a
   mensagem de hoje está certa para ela.
3. **Given** a cadeia de substituição esgotada por indisponibilidade real, **When** se abre a tela,
   **Then** a frase distingue *esgotou a cadeia* de *não soube derivar*.

---

### Edge Cases

- **Edital do acervo com valor fora do vocabulário.** O valor publicado é norma e não se reescreve.
  A tela de Retificação precisa **mostrá-lo** sem oferecê-lo como escolha válida, e sem parecer que o
  campo está vazio.
- **Vocabulário que cresce.** Quando um algoritmo ou uma fonte é acrescentada, os Editais publicados
  antes continuam citando o que citaram. A escolha nova aparece na composição; nada muda no acervo.
- **Ocorrência que termina em número mas cuja fonte não a reconhece.** A forma está certa e a
  execução falha mesmo assim. É a `US3`, cenário 2: a causa é a fonte, e a frase de hoje está certa.
- **Marco que usa o método comum do Edital.** A conferência é do método **que governa o marco** — o
  próprio, quando declarado; o comum, quando não. Conferir só o declarado deixaria passar o Edital
  que herda um método comum inexecutável.
- **Método comum declarado e nenhum marco que sorteia.** Não há o que executar, e a regra não
  dispara.

---

## Requirements *(mandatory)*

### Functional Requirements

#### A forma, na composição

- **FR-507**: Os campos do método cujo valor pertence a **vocabulário fechado** — o algoritmo e a
  fonte — MUST ser oferecidos na composição como **escolha entre os valores que o sistema executa**,
  e MUST NOT ser digitados livremente. **Isto generaliza o que a tela de Retificação já faz** — ela
  oferece **quatro** campos fechados como escolha, por uma função única que lê os vocabulários de
  quem os executa. A composição MUST reusar essa função, e MUST NOT montar uma segunda lista: duas
  origens para o mesmo vocabulário divergem quando ele muda. Hoje a composição deixa digitar e **recusa ao gravar** — a guarda existe, o ensino não,
  e a pessoa descobre o vocabulário por tentativa.
- **FR-508**: O campo da **ocorrência** MUST declarar, no ponto de uso, **a forma que precisa ter e a
  razão dela** — que a regra de substituição deriva do número da ocorrência. Ele MUST NOT virar
  vocabulário fechado: a referência é do Edital e da fonte, e enumerá-la seria enumerar o futuro.
- **FR-509**: A ajuda de `FR-508` MUST seguir a formulação que a tela **já pratica** no campo do
  instante da ocorrência — forma, exemplo e consequência —, e MUST NOT criar uma segunda maneira de
  ensinar a mesma coisa.
- **FR-510**: O campo que diz **como a ocorrência decorre da data programada** MUST permanecer texto
  livre. Ele é prosa normativa, sai no documento e **nenhum caminho de execução o lê**; quem deriva é
  a regra de substituição, que já é vocabulário fechado. Trocá-lo por um código removeria do Edital a
  frase que diz a norma em português.
- **FR-511**: Valor que **não** esteja entre os oferecidos MUST continuar legível **na composição**,
  identificado como o que veio do conteúdo de origem, e MUST NOT desaparecer nem ser apresentado como
  escolha válida.
  *A tela é a da composição, e não a da Retificação:* a Retificação **já** oferece os quatro campos
  fechados como escolha, e esta feature não a toca. A escolha **nova** é a da composição, e o caminho
  por onde um valor de fora do vocabulário chega a ela é o rascunho **criado a partir de Edital
  anterior** — se o vocabulário encolheu desde a publicação de origem, um `select` que só oferece o
  de hoje faria o campo parecer **vazio** num Edital que o declarou.

#### A sexta guarda

- **FR-512**: A ocorrência MUST ser recusada quando **não tiver a forma que a regra de substituição
  consome** — hoje, terminar em número. A recusa MUST acontecer **no mesmo lugar e no mesmo momento**
  em que os outros cinco campos do método já são conferidos, e MUST valer tanto para o método próprio
  do marco quanto para o comum do Edital. *Uma sexta guarda ao lado de cinco é mais barata e mais
  honesta do que uma família nova de achados ao lado delas* (`D-001`).
- **FR-513**: A recusa MUST nomear **o campo**, **a forma esperada** e **por que ela é exigida** — que
  a substituição deriva do número da ocorrência —, na mesma gramática das outras cinco. *"O método
  não é executável"* descreve o sintoma.
- **FR-514**: A recusa MUST NOT tornar **irretificável** nenhum Edital do acervo. Há conteúdo
  publicado que nunca passou por esta conferência, porque ela não existia; se o lugar natural da
  guarda impedir a Retificação desse conteúdo, **o lugar está errado** — publicação é ato imutável, e
  um Edital do qual não se sai é pior do que um método que não roda.
- **FR-515**: A conferência MUST reutilizar a regra que o motor já aplica, e MUST NOT reimplementá-la.
  Duas respostas para *"esta referência é derivável?"* divergiriam na primeira mudança, e a
  divergência apareceria como a composição aceitando o que o sorteio recusa.

#### A recusa, no dia

- **FR-516**: A recusa da tela do sorteio MUST distinguir **a fonte não publicou** de **a declaração
  não pôde ser lida**, e MUST NOT atribuir à fonte externa uma falha que é da declaração.
- **FR-517**: Quando a causa é a declaração, a frase MUST dizer **qual campo** e **o que ele precisa
  conter**, e só então que corrigir exige Retificação — porque o Edital está publicado.
- **FR-518**: Quando a causa é indisponibilidade real, a frase MUST continuar dizendo o que diz hoje.
  Esta feature **não** mexe no que já está certo.

#### O que não muda

- **FR-519**: Nenhum conteúdo publicado MUST ser reescrito, e nenhum vocabulário MUST ser alargado
  por esta feature. Acrescentar algoritmo ou fonte continua sendo **publicar implementação, vetores e
  contrato**.
- **FR-520**: A feature MUST NOT criar capacidade nova, papel novo nem regra de autorização nova, e
  MUST NOT alterar o resultado de sorteio algum já realizado.
- **FR-521**: A direção de dependência entre sorteio e classificação MUST permanecer como a `021` a
  declarou por escrito. Esta feature não a inverte.

### Key Entities

- **Método do sorteio**: a declaração normativa que governa um marco — algoritmo, fonte, ocorrência,
  instante, derivação em prosa, regra de substituição e regra de normalização. Vive no conteúdo
  publicado.
- **Ocorrência da fonte**: o evento externo que fixa a semente, identificado por uma referência que a
  regra de substituição sabe incrementar.
- **Vocabulário executável**: o conjunto de algoritmos e de fontes que o sistema **implementa**.
  Cresce por publicação de código, nunca por texto de Edital.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-176**: Os cenários **3** e **5** da reauditoria chegam ao fim — congelamento do universo,
  semente, execução, ordem sorteada, manifesto e verificação pública —, com o Edital composto pela
  interface e **sem que ninguém precise saber de antemão** que a ocorrência tem de terminar em
  número.
- **SC-177**: **Zero** Editais chegam à publicação com método de sorteio que o sistema não executa —
  e a conferência que o garante é **a mesma** que o motor aplica na hora de derivar, verificada por
  comparação direta das duas respostas.
- **SC-178**: **100%** das recusas desta guarda nomeiam **o campo, a forma esperada e a razão da
  forma** — e nenhuma delas descreve o sintoma. *A redação anterior pedia "etapa de correção" e falava
  em "achados desta família": as duas vieram da versão em que a conferência era uma família nova na
  publicação, e a revisão a trocou por **uma** guarda, ao lado das cinco que já existem.*
- **SC-179**: Nenhum valor publicado no acervo deixa de ser legível, e **nenhum** sorteio já
  realizado muda de resultado — conferido por comparação de conteúdo, resumo e manifesto.
- **SC-180**: A varredura contra os Editais de sorteio da amostra real registra, um a um, **como
  cada um declara — ou não declara — a ocorrência que fixa a semente**, e o que alguém teria de
  escrever no campo ao compor a partir dele.
  *O critério mudou de pergunta, e a razão está medida:* a primeira redação contava **quantos seriam
  impedidos**, e a leitura de quatro Editais que sorteiam — 57, 58, 69 e 78/2026 — mostrou que
  **nenhum declara ocorrência de fonte externa**. A contagem devolveria zero por ausência de
  declaração, e não por declaração correta. O que a varredura precisa produzir é **o que a ajuda da
  `FR-508` tem de ensinar a quem parte de um Edital real** ([research.md](research.md), `R-7`).
- **SC-181**: **Nenhuma migration**, e nenhum vocabulário alargado.

---

## Assumptions

### As decisões tomadas antes do planejamento

Elas estão declaradas aqui, e não no `research.md`, porque foram fechadas antes dele.

### D-001 — o método inexecutável **impede** a publicação, e não avisa

Decidido em 18/09/2026 por quem governa o backlog.

É a mesma resposta que a `032` deu ao caso vizinho: publicar marco que sorteia **sem** método
publicável já é impedido. Método **presente e ilegível pelo motor** é a mesma falha um degrau
adiante, e o custo de descobrir tarde é idêntico — o dia do sorteio, com o cronograma correndo.

**O que torna a decisão barata**: com `FR-507`, os dois campos de vocabulário fechado deixam de
admitir erro de digitação, e o impedimento passa a atuar quase só sobre a ocorrência — o único em que
alguém ainda pode escrever o que quiser. **A alternativa descartada**, avisar, preservaria o Edital
que declara fonte ainda não adaptada; o próprio código argumenta contra, porque o manifesto
publicaria uma fonte que nunca foi consultada.

**O que a medição do `plan` mudou, e o que não mudou.** A decisão — *impedir* — está de pé. O
**lugar** dela mudou: a primeira redação previa uma família nova de achados na validação da
publicação, e a medição mostrou que **cinco campos irmãos já são conferidos ao gravar o rascunho**,
para o método próprio e para o comum. A sexta guarda vai para junto das cinco. Onde a conferência
vive é engenharia; que ela impeça é governança, e essa parte é sua.

`FR-514` é o que impede a decisão de alcançar o acervo.

### D-002 — o vocabulário vira escolha, e não texto validado

As duas formas recusam o valor inválido. A escolha, além disso, **impede que ele seja escrito** — e
o custo de um valor inválido aqui não é um formulário recusado: é um manifesto publicando o nome de
um algoritmo que ninguém implementa, de modo que quem reimplementasse a partir do publicado chegaria
a outra ordem e concluiria, corretamente, que o sorteio não confere.

`FR-511` é o preço a pagar por ela: o acervo tem valores que a escolha não oferece, e eles precisam
continuar legíveis.

### D-003 — a derivação em prosa fica como está

Registrada porque contraria a leitura da auditoria, que a citou junto com a ocorrência. Medição:
nenhum caminho de execução lê esse campo; quem deriva é a regra de substituição, que já é vocabulário
fechado. Ele é a frase que diz a norma em português, e é assim que um Edital se escreve.

### Uma pergunta de governança que esta feature registra e **não** responde

**Os Editais correntes do Cefor não declaram ocorrência de fonte externa.** Li quatro dos que
sorteiam — 57, 58, 69 e 78/2026 — e os quatro trazem a mesma cláusula: *o software sorteia e publica
a semente usada, para auditoria*. Nenhum menciona fonte pública, concurso ou extração.

O modelo deste sistema é **deliberadamente mais forte**, e a `021` o escolheu por escrito: semente
derivada de fonte pública externa, **declarada antes**, verificável por terceiro. É o que entrega a
auditabilidade que aqueles Editais prometem e não cumprem — semente publicada **depois** não prova
nada a quem não estava lá.

**Mas o sistema exige uma declaração que os Editais de hoje não fazem.** Ou eles passam a fazê-la, e
isso é ganho de auditabilidade a ser combinado com quem os redige, ou existe uma família de sorteio
que o modelo atual não representa. **Esta spec não decide, e não deve**: ela ensina a declarar o que
o modelo pede, e registra a pergunta para quem governa o backlog.

### As demais premissas

- As medições de *Por que esta feature existe* são de 18/09/2026 contra `d30f6d8`. **Reconfira-as no
  `plan`, e não as assuma** — a `033` produziu três medições erradas seguidas por descrever a
  superfície de memória, e a `034` carregou um número que nunca fechou com a própria tabela.
- Esta spec é **independente da `034`**, que está especificada e não implementada. As duas tocam
  `editais/domain/validation.py`, em funções diferentes e por razões diferentes; não há colisão de
  premissa. A ordem de implementação é conveniência de quem conduz.
- A faixa de identificadores deve ser **medida de novo** ao escrever a spec seguinte, inclusive em
  worktrees com trabalho não comitado.

---

## Out of Scope

Cada um com spec própria:

- **A derivação de recortes do sorteio** — achado registrado pela `034`, e decidido lá: fica fora,
  com a divergência registrada. *(A decisão tem identificador dentro da `034`; não o cito aqui porque
  decisão se lê no contexto que a produziu, e citá-la de fora é o que o guardião de citações
  impede.)*
  A correção obriga a definir **como os atos históricos do recorte excedente continuam alcançáveis**,
  e ato publicado não se apaga. Juntar as duas faria esta spec carregar um redesenho de acesso a ato
  publicado.
- **A ordem por recorte em marco computado** — é a `034`, já especificada.
- **O renderizador normativo único das telas de ato** — `E-3`, `ACH-39`, `ACH-31`, `ACH-45`.
- **O ato de instrução do recurso e o parecer ao candidato** — `ACH-43`, `ACH-42`.
- **A validação cruzada entre fontes normativas** — `E-4`.
- **O painel de condução do Processo vivo** — `ACH-25`.
- **O pacote de microcópia e navegação** — o link do corte condicionado à regra de corte, mais
  `ACH-02`, `ACH-30`, `ACH-08` e `ACH-16`.

---

## Conformidade com a Constituição

**Princípio II — Integridade Normativa, Imutabilidade e Temporalidade.** O método é conteúdo
publicado, e o que já foi publicado não se corrige: `FR-511`, `FR-515` e `FR-520` fixam que o acervo
continua legível, retificável e intocado, e `SC-179` é o critério que prende os três.

**Princípio IV — Regras Explícitas e Consistência Operacional.** `FR-516` existe por causa dele: a
conferência da Revisão e a execução do sorteio MUST responder pela mesma regra. Duas respostas para
*"este método roda?"* apareceriam como a Revisão aprovando o que o sorteio recusa — e quem lê a
Revisão acredita nela.

**Princípio VI — Completude de Jornada e Valor Demonstrável.** A capacidade entregue fecha uma
jornada que hoje não termina: o `SC-176` é o sorteio inteiro, do congelamento à verificação pública,
e não um passo dele.

**Princípio I — Linguagem Ubíqua.** Nenhum vocabulário novo: algoritmo, fonte, ocorrência, semente,
normalização e substituição já são do domínio. `FR-509` proíbe inventar uma segunda maneira de
ensinar a forma de um campo, e `FR-510` protege a frase em português que diz a norma.
