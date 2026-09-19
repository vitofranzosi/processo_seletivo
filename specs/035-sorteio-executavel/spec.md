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

### O defeito, medido: três campos do caminho executável são texto livre

Cada um deles **tem forma determinada em algum lugar do código**, e a tela não a declara em lugar
nenhum.

| Campo, como a tela o chama | A forma que o motor exige | O que a tela oferece hoje |
|---|---|---|
| **Algoritmo e versão** | vocabulário **fechado** de um elemento; acrescentar algoritmo é publicar versão nova, com implementação, vetores e contrato | caixa de texto, com um `placeholder` |
| **Fonte pública externa da semente** | vocabulário **fechado** de dois nomes, cada um ligado ao adaptador que o executa; acrescentar fonte é publicar adaptador | caixa de texto, **sem ajuda nenhuma** |
| **Ocorrência que fixará a semente** | livre, mas **tem de terminar em número** — a substituição deriva dele | caixa de texto, **sem ajuda nenhuma** |

**O contraexemplo está na mesma tela, três linhas acima.** *"Quando a ocorrência acontece"* é o mesmo
tipo de campo, e a tela **ensina** a forma: *"Com fuso, como `2026-11-20T20:00:00-03:00`. É este
instante que separa 'a fonte ainda não publicou' de 'a fonte não publicará'."*

O padrão a generalizar já existe. Ele só não foi aplicado aos três campos em que errar impede o
sorteio de rodar.

### Uma correção à leitura da auditoria

A reauditoria escreveu que *"os campos são texto livre mas precisam ser dado computável"*, citando
**dois**: *"Ocorrência que fixará a semente"* e *"Como a ocorrência decorre da data programada"*.

**O segundo é prosa por desenho, e está certo assim.** Ele é carregado pelo formulário, sai no
documento publicado com o rótulo *Derivação* — e **nenhum caminho de execução o lê**. Quem deriva de
fato é a **regra de substituição**, que já é uma seleção de vocabulário fechado.

Pedir forma computável a ele seria trocar por um código a frase que diz a norma em português, que é
exatamente a função dele. A spec o deixa como está, e registra por quê.

### E nada disso é dito antes de publicar

A `032` entregou que marco que sorteia **sem** método publicável não publica. Ela confere
**presença**; esta confere **execução**. Um Edital com algoritmo inventado, fonte fora do vocabulário
ou ocorrência que não termina em número atravessa a Revisão, é homologado e publicado sem uma
palavra — e a falha aparece no dia do sorteio, quando corrigir já depende de Retificação.

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
3. **Given** um método já declarado em Edital do acervo, **When** se abre a Retificação dele,
   **Then** o valor publicado continua legível, mesmo que não esteja entre os que o sistema executa.

---

### User Story 2 - A publicação recusa o método que não roda (Priority: P2)

A Revisão impede publicar um marco cujo método o sistema não consegue executar, nomeando **o campo, a
forma esperada e a etapa em que se corrige**.

**Why this priority**: é a rede. A `US1` faz o erro ficar difícil; esta faz ele ficar impossível de
publicar. E é a mesma família da `032` — descobrir antes, e não no dia.

**Independent Test**: compor um marco com ocorrência em prosa, abrir a Revisão, e ser impedido com
uma frase que diz o que corrigir e onde.

**Acceptance Scenarios**:

1. **Given** um marco de sorteio cuja ocorrência não termina em número, **When** se abre a Revisão,
   **Then** a publicação é **impedida**, e o achado nomeia o campo, a forma e a etapa.
2. **Given** o mesmo Edital, **When** se tenta submeter assim mesmo, **Then** a submissão é recusada
   com a **mesma frase** da Revisão.
3. **Given** um marco que **não** sorteia, **When** se abre a Revisão, **Then** nada desta família é
   produzido.
4. **Given** um Edital **do acervo**, publicado antes desta feature com método não executável,
   **When** se pratica uma Retificação sobre ele, **Then** a Retificação **não** é impedida por esta
   regra.

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
  fonte — MUST ser oferecidos como **escolha entre os valores que o sistema executa**, e MUST NOT ser
  digitados livremente. A razão está escrita no próprio código: acrescentar fonte é **publicar
  adaptador**, e não escrever uma linha no Edital; um Edital que declarasse uma fonte sem adaptador
  faria o manifesto publicar uma fonte que nunca foi consultada.
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
- **FR-511**: Valor publicado que **não** esteja entre os oferecidos MUST continuar legível na
  Retificação, identificado como o que foi publicado, e MUST NOT desaparecer nem ser apresentado como
  escolha válida.

#### A conferência, antes de publicar

- **FR-512**: Marco que ordena por sorteio cujo método **não pode ser executado** MUST impedir a
  publicação. É a mesma resposta que a `032` deu ao caso vizinho — marco que sorteia sem método
  publicável —, e a razão é a mesma: o custo de descobrir tarde é o dia do sorteio, com o cronograma
  correndo e a correção já dependendo de Retificação (`D-001`).
- **FR-513**: O achado MUST nomear **o campo**, **a forma esperada** e **a etapa em que se corrige**,
  na mesma gramática da família da `032`. *"O método não é executável"* descreve o sintoma; a pessoa
  precisa de qual campo e do que ele tem de conter.
- **FR-514**: A conferência MUST ser feita sobre o método **que governa o marco** — o próprio quando
  declarado, o comum do Edital quando não. Conferir apenas o declarado deixaria passar o marco que
  herda um método comum inexecutável.
- **FR-515**: O impedimento MUST valer **somente no ato de publicação**. Gravar rascunho continua
  possível, e **Retificação de Edital do acervo continua aceita** — impedir ali criaria um Edital
  publicado do qual não se sai.
- **FR-516**: A conferência MUST reutilizar as regras que o motor já aplica, e MUST NOT reimplementar
  nenhuma delas. Duas respostas para *"este método roda?"* divergiriam na primeira mudança, e a
  divergência apareceria como a Revisão aprovando o que o sorteio recusa.

#### A recusa, no dia

- **FR-517**: A recusa da tela do sorteio MUST distinguir **a fonte não publicou** de **a declaração
  não pôde ser lida**, e MUST NOT atribuir à fonte externa uma falha que é da declaração.
- **FR-518**: Quando a causa é a declaração, a frase MUST dizer **qual campo** e **o que ele precisa
  conter**, e só então que corrigir exige Retificação — porque o Edital está publicado.
- **FR-519**: Quando a causa é indisponibilidade real, a frase MUST continuar dizendo o que diz hoje.
  Esta feature **não** mexe no que já está certo.

#### O que não muda

- **FR-520**: Nenhum conteúdo publicado MUST ser reescrito, e nenhum vocabulário MUST ser alargado
  por esta feature. Acrescentar algoritmo ou fonte continua sendo **publicar implementação, vetores e
  contrato**.
- **FR-521**: A feature MUST NOT criar capacidade nova, papel novo nem regra de autorização nova, e
  MUST NOT alterar o resultado de sorteio algum já realizado.
- **FR-522**: A direção de dependência entre sorteio e classificação MUST permanecer como a `021` a
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
- **SC-177**: **Zero** Editais chegam à publicação com método de sorteio que o sistema não executa.
- **SC-178**: **100%** dos achados desta família nomeiam campo, forma esperada e etapa de correção.
- **SC-179**: Nenhum valor publicado no acervo deixa de ser legível, e **nenhum** sorteio já
  realizado muda de resultado — conferido por comparação de conteúdo, resumo e manifesto.
- **SC-180**: A varredura contra os **doze** Editais da amostra real registra, um a um, quais
  passariam a ser impedidos e por qual campo — e **nenhum** deles é impedido por motivo que a
  composição de hoje não permitisse evitar.
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

`FR-515` é o que impede a decisão de alcançar o acervo.

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
