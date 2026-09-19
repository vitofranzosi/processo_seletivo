# Feature Specification: Instrução do recurso

**Feature Branch**: `036-instrucao-do-recurso`

**Created**: 2026-09-19

**Status**: Draft

**Input**: Reauditoria exploratória de UX de 2026-09-16 —
[doc/auditoria-exploratoria-ux-2026-09-16.md](../../doc/auditoria-exploratoria-ux-2026-09-16.md) —,
achados **ACH-43** (S3/**P0**, o último `P0` aberto) e **ACH-42** (S3/P1), melhoria **13.2**, raiz
`E-2` mais a `FR-105` da `018`. Estado medido no código em 19/09/2026, contra a `main` `dd71d46`.

> **Faixa de identificadores.** Esta spec abre em **FR-522** e **SC-182**. Teto medido em
> 19/09/2026 em todas as worktrees desta máquina: `FR-521` / `SC-181` / `UX-061`. **Nenhum `UX-` é
> aberto aqui.** As **decisões** reiniciam em `D-001`.

## Por que esta feature existe

O recurso é uma caixa-preta **dos dois lados**.

**O candidato eliminado não sabe por quê.** Ele abre o acompanhamento e lê *"Eliminada · pontuação
30"* e *"30,0000 < 40,0000"*. O avaliador escreveu, obrigatoriamente, um parecer explicando o que
faltou — e esse texto nunca sai da tela interna.

**Quem julga decide sem a prova.** Para quem tem apenas a capacidade de julgar recursos, a tela do
recurso traz a fundamentação de quem recorreu e mais nada: nem o parecer atacado, nem o documento
citado.

### O que a medição mostra, e ela é mais desconfortável do que a auditoria

| | Medido |
|---|---|
| O parecer **existe** | `parecer` é campo de texto na Avaliação |
| Ele é **obrigatório** exatamente no caso auditado | Etapa eliminatória com nota **abaixo da mínima** — que é o *"30 < 40"* da tela |
| A regra diz **por que** é obrigatório | *"é exatamente contra o parecer que um recurso é respondido. Sem ele, a instituição não teria o que dizer"* |
| A spec que o exigiu diz **para quem** | *"o desfavorável é justamente o caso em que o candidato mais precisará da fundamentação para recorrer, e é contra o parecer que o recurso responderá"* |
| O candidato **não o recebe** | no portal, a única ocorrência da palavra *parecer* é o **verbo**, dentro de comentários de folha de estilo |

**O sistema exige o texto pela razão de servir ao candidato, guarda o texto, e não o entrega a ele.**
Não é omissão de quem escreveu a regra — é a regra cumprida pela metade.

### O candidato não está no escuro absoluto, e a distinção importa

A tela de acompanhamento **já exibe um motivo** — *"pontuação inferior à nota mínima da Etapa
(45,0000 < 60,0000)"* —, obrigatório por constraint desde a `013`.

| | O que é | Quem escreve |
|---|---|---|
| **motivo** | a regra aplicada ao número | a máquina, a partir da norma |
| **parecer** | a razão da avaliação | **a pessoa que avaliou** |

**O motivo diz que a nota não bastou. O parecer diz o que faltou.** É no segundo que está *"o
currículo não comprova os seis meses"*, e é contra ele que um recurso se escreve — não contra a
aritmética, que ninguém contesta.

*Esta distinção está aqui porque sem ela a primeira revisão pergunta "mas já não há um motivo?", e a
resposta é sim — e ele não substitui o outro.*

### E a tela de quem julga é um beco **honesto**, o que muda o alvo

A tela do recurso **não** oferece caminho que o julgador não alcança: os destinos são guardados, e o
comentário do bloco registra a intenção — *"quem não alcança nenhum lê o que falta, e não um espaço
vazio"*. Quem só julga lê:

> *"Para abrir o resultado atacado, a avaliação que o produziu e os documentos da inscrição é
> preciso presidir este Processo, ter a permissão de auditoria ou a de consultar inscrições. **Julgar
> não as concede.**"*

**A `033` já resolveu a parte enganosa desta família.** O que resta não é uma tela que mente: é um
beco que não precisaria existir. E a frase acima é o produto declarando o próprio limite com
precisão — o que torna a correção mais fácil, e não menos necessária.

### Por que a saída não é ampliar o papel

Seria mais simples dar ao julgador acesso ao que ele precisa ver. **A `FR-105` da `018` proíbe**, e
na cláusula exata: *"…e MUST NOT ampliar o acesso a documentos do candidato."*

A separação entre quem avalia e quem julga é deliberada, e ampliá-la apagaria o contraditório que ela
protege. O caminho é **um ato**: alguém com autoridade decide anexar **aquela** prova **àquele**
recurso, e isso fica registrado. A regra continua de pé, e a prova chega.

**Não existe hoje conceito de anexo, instrução ou prova no recurso** — há a peça, o juízo de
admissibilidade e a decisão, e nada entre eles.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O candidato lê a razão da própria eliminação (Priority: P1)

Quem foi eliminado por resultado desfavorável passa a ler, no acompanhamento, o parecer que o
avaliador escreveu — enquanto o prazo de recurso estiver aberto.

**Why this priority**: é o que devolve a possibilidade de recorrer com fundamento, e é a metade da
feature que não depende de ninguém praticar ato nenhum. Sem ela, a `US2` melhora a qualidade da
decisão sobre um recurso que a pessoa escreveu no escuro.

**Independent Test**: eliminar uma inscrição por nota abaixo da mínima, divulgar o resultado, e
conferir pelo portal que o titular lê a frase do avaliador enquanto o prazo corre.

**Acceptance Scenarios**:

1. **Given** uma inscrição eliminada por nota abaixo da mínima e o prazo recursal aberto, **When** o
   titular abre o acompanhamento, **Then** ele lê **o parecer**, identificado como a fundamentação
   daquele resultado.
2. **Given** o prazo recursal **encerrado**, **When** o titular abre o acompanhamento, **Then** o
   parecer **não** é exibido, e a tela diz que o prazo se encerrou — e não fica em silêncio.
3. **Given** um resultado **favorável**, **When** o titular abre o acompanhamento, **Then** nada
   muda: esta feature alcança o desfavorável, que é o recorte que a regra do parecer já descreve.
4. **Given** qualquer pessoa que não seja o titular, **When** ela tenta alcançar o parecer, **Then**
   a resposta é a mesma que ela receberia se o recurso não existisse.

---

### User Story 2 - Quem julga recebe a prova, por ato e não por permissão (Priority: P2)

A presidência pratica um **ato de instrução** que anexa, àquele recurso, o parecer atacado e o
documento citado. Quem julga passa a ver o que foi instruído.

**Why this priority**: é o que fecha o `ACH-43`, o último `P0`. Vem depois da `US1` porque a ordem
importa para quem usa: primeiro o candidato recorre sabendo contra o quê, depois quem julga decide
vendo o quê.

**Independent Test**: com um recurso interposto, praticar a instrução como presidência e conferir,
entrando como alguém que **só** julga recursos, que a prova aparece — sem que nenhuma permissão tenha
mudado.

**Acceptance Scenarios**:

1. **Given** um recurso interposto e nenhuma instrução praticada, **When** quem só julga abre a tela,
   **Then** ela diz **o que falta e a quem pedir**, na formulação que o produto já pratica.
2. **Given** a presidência na tela do recurso, **When** ela pratica a instrução, **Then** o ato é
   registrado na auditoria, com quem instruiu, quando, e o que foi anexado.
3. **Given** a instrução praticada, **When** quem só julga abre a tela, **Then** ele lê o parecer
   atacado e alcança o documento citado — **e nada além daquele recurso**.
4. **Given** a instrução praticada num recurso, **When** o mesmo julgador abre **outro** recurso da
   mesma Etapa, **Then** ele não alcança nada por causa da instrução anterior.
5. **Given** o recurso **decidido**, **When** quem julgou volta à tela, **Then** o registro de que a
   instrução houve permanece, e o **acesso** que ela concedia terminou.

---

### User Story 3 - A instituição sabe o que foi mostrado a quem (Priority: P3)

Todo acesso concedido por instrução é registrado, e a auditoria consegue responder *quem viu o quê,
quando, e por decisão de quem*.

**Why this priority**: é o que torna o ato defensável. Sem o registro, a instrução seria uma
ampliação de acesso sem rastro — exatamente o que a `FR-105` existe para impedir, com outro nome.

**Independent Test**: praticar uma instrução, abrir a auditoria e encontrar o ato, o autor, o
alcance e o instante.

**Acceptance Scenarios**:

1. **Given** uma instrução praticada, **When** se consulta a auditoria, **Then** o ato aparece com
   autor, instante, recurso alcançado e o que foi anexado.
2. **Given** um acesso exercido pelo julgador sobre o que foi instruído, **When** se consulta a
   auditoria, **Then** o acesso está registrado.

---

### Edge Cases

- **Avaliação reaberta depois do resultado.** O parecer de hoje pode não ser o que fundamentou o
  resultado contestado. O que o candidato lê e o que se instrui MUST ser o parecer que o resultado
  **citou** — é a mesma doutrina que o projeto já aplica a ato histórico.
- **Mais de uma avaliação na mesma inscrição.** Duas análises podem afirmar sentidos opostos, e a
  consolidação resolve isso. O parecer exibido é o da avaliação que **fundamenta o resultado**, e não
  a união de todas.
- **Resultado desfavorável sem parecer.** Existe: a obrigatoriedade depende do caráter da Etapa e da
  forma. A tela precisa dizer que não há parecer — e não parecer que há e sumiu.
- **Prazo que fecha com o recurso da pessoa ainda em julgamento.** Era o buraco da primeira redação:
  a exibição pendia só do prazo, e a pessoa perdia de vista o texto que o **próprio recurso dela**
  contesta. Resolvido pela segunda condição da `FR-522` (`D-001`).
- **Recurso sem resultado atacado.** Há recurso contra publicação, e não contra resultado individual.
  Ali não há parecer a instruir, e a tela precisa dizer isso.
- **Instrução praticada duas vezes.** O ato é append-only; instruir de novo acrescenta, e não
  substitui.
- **Prazo que fecha com o julgador no meio da leitura.** O acesso pende do estado do recurso, e não
  da sessão de quem lê.

---

## Requirements *(mandatory)*

### O parecer chega a quem foi avaliado

- **FR-522**: O titular MUST ler, no canal do candidato, o **parecer** que fundamenta um resultado
  desfavorável a ele, **enquanto o prazo de recurso estiver aberto — ou enquanto houver recurso dele
  ainda não decidido** (`D-001`).
  *A segunda condição não é generosidade:* quem recorreu decide se insiste, escreve réplica ou aceita
  a decisão, e fazer isso sem poder reler o texto que está contestando é o defeito que esta feature
  existe para fechar, acontecendo um passo adiante. **E foi o sistema que o obrigou a recorrer contra
  aquele texto.**
- **FR-523**: O parecer exibido MUST ser o que **fundamenta o resultado contestável** — o da avaliação
  que o produziu, e não o estado atual de uma avaliação reaberta depois. O registro histórico da
  conclusão existe para isso e MUST ser a fonte quando houver reabertura.
- **FR-524**: Encerradas **as duas** condições da `FR-522` — o prazo fechou **e** não há recurso
  pendente —, o parecer MUST deixar de ser exibido, **e a tela MUST dizer por quê**. Desaparecer em silêncio faria a pessoa pensar que perdeu algo que nunca teve.
- **FR-525**: Resultado desfavorável **sem** parecer MUST ser dito como tal. A ausência é possível —
  a obrigatoriedade depende do caráter da Etapa e da forma da avaliação —, e calar sobre ela é pior
  do que declará-la.
- **FR-525a**: O parecer MUST ser exibido **ao lado do motivo já existente, e não no lugar dele**.
  São coisas diferentes — o motivo é a regra aplicada ao número, o parecer é a razão que a pessoa
  escreveu —, e substituir um pelo outro tiraria da tela a aritmética que hoje sustenta a
  contestação.
- **FR-526**: O parecer MUST NOT alcançar ninguém além do titular, da autoridade julgadora instruída
  e da auditoria. Identificador MUST NOT conceder acesso.

### A prova chega a quem julga, por ato

- **FR-527**: MUST existir um **ato de instrução** pelo qual a autoridade competente anexa, **a um
  recurso**, o parecer atacado e o documento citado. É ato, e não configuração: tem autor, instante e
  registro.
- **FR-528**: O alcance do que se instrui MUST ser **daquele recurso**. Instruir um recurso MUST NOT
  conceder nada sobre outro, ainda que da mesma Etapa, do mesmo Edital ou do mesmo candidato.
- **FR-529**: O acesso concedido pela instrução MUST terminar quando o recurso é decidido. **O
  registro de que a instrução houve MUST permanecer** — nada é apagado; o que se encerra é o alcance.
- **FR-530**: A feature MUST NOT criar capacidade nova nem ampliar nenhuma existente. Ampliar o papel
  de julgar é exatamente o que a `FR-105` da `018` proíbe, e é o motivo de a saída ser um ato.
- **FR-531**: O documento citado MUST ser alcançado **por referência**, e MUST NOT ser copiado para o
  recurso. Copiar multiplicaria a superfície do dado pessoal e criaria uma segunda cópia que a
  Constituição depois proíbe apagar.
- **FR-531a**: O documento alcançado por referência MUST NOT ser copiado para dentro do recurso, e a
  **ausência da cópia MUST ser verificável** — não basta o caminho apontar para o original; nada pode
  ter sido duplicado no caminho.

### O rastro

- **FR-532**: A tela de quem julga MUST distinguir **três** estados, e não dois:

  | Estado | O que a tela diz |
  |---|---|
  | nada foi instruído | **o que falta e a quem pedir**, na formulação que o produto já pratica |
  | há instrução, e o recurso não foi decidido | a prova |
  | **houve instrução, e o acesso terminou com a decisão** | **que houve, e que o alcance se encerrou** |

  O terceiro é o que a primeira redação não tinha: sem ele, a tela diria *"nada foi instruído"* a
  quem viu a prova ontem — e isso é falso sobre um ato que aconteceu.
  Em nenhum dos três a tela MUST oferecer caminho que aquele ator não alcança, que é a garantia
  deixada pela `033`.
- **FR-533**: O ato de instrução MUST ser registrado na auditoria, com autor, instante, recurso
  alcançado e o que foi anexado.
- **FR-534**: O **acesso exercido** sobre o que foi instruído MUST ser registrado. Saber que a prova
  foi anexada não responde quem a viu.

### O que não muda

- **FR-535**: Nenhum dado de outro candidato MUST atravessar as superfícies do recurso, em nenhuma
  das telas que esta feature toca.
- **FR-536**: Escopo institucional divergente MUST continuar recebendo a resposta uniforme de recurso
  não encontrado.
- **FR-537**: Nada do conteúdo publicado MUST ser reescrito, e nenhum parecer já escrito MUST ser
  alterado por esta feature.

### Key Entities

- **Parecer**: o texto que o avaliador escreve para fundamentar o que afirmou. Obrigatório quando a
  avaliação elimina.
- **Ato de instrução**: o ato pelo qual a autoridade anexa prova a um recurso, para que ele seja
  julgado com o que se contesta à vista. Append-only.
- **Alcance da instrução**: o par (recurso, prova). Nasce com o ato e termina com a decisão.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-182**: Um candidato eliminado por nota abaixo da mínima **lê a frase que o avaliador escreveu**,
  no portal, enquanto o prazo corre — percorrido pelo canal do candidato, sem shell e sem banco.
- **SC-183**: Um julgador com **apenas** a capacidade de julgar recursos decide com o parecer atacado
  à vista, **sem que nenhuma permissão tenha sido ampliada** — conferido por comparação das
  capacidades antes e depois.
- **SC-184**: **100%** dos acessos concedidos por instrução são registrados, com autor, alcance e
  instante.
- **SC-185**: **Zero** acessos sobrevivem à decisão do recurso — verificado tentando alcançar o que
  foi instruído depois de decidido.
- **SC-186**: **Zero** dados de outro candidato aparecem em qualquer tela que esta feature toca.
- **SC-187**: Nenhuma capacidade nova, nenhum papel novo e **nenhum parecer alterado**.

---

## Assumptions

### D-001 — o parecer acompanha o prazo, e não a inscrição

Decidido em 19/09/2026 por quem governa o backlog.

O parecer aparece **enquanto houver prazo recursal — ou enquanto houver recurso dele ainda não
decidido**. A primeira condição é o recorte da melhoria 13.2 e o que a `012` descreve ao exigir o
texto: ele serve para recorrer, e aparece enquanto recorrer for possível.

**A segunda foi acrescentada em 19/09/2026, depois que o `analyze` mostrou o que a primeira sozinha
custava.** Prender só ao prazo tirava o parecer justamente de quem recorreu, enquanto o recurso dele
corria — a pessoa que a feature existe para servir, no momento em que ela mais precisa. Quem recorreu
já alcança a própria peça e a decisão; o parecer é o terceiro documento do mesmo processo que ela
moveu, e não uma superfície nova.

*Fica registrado que a decisão foi tomada duas vezes*: a primeira com o custo dito de forma genérica,
a segunda com o caso na mesa. A diferença entre as duas é o que uma passada de `analyze` produz.

**O custo que permanece, dito por escrito:** encerradas as duas condições, a pessoa perde acesso à
razão da própria eliminação, e ela continua sendo a titular daquele dado. **A `FR-524` é o que impede
esse custo de virar defeito** — a tela diz **por quê**, em vez de calar. Se a decisão for revista um
dia, é esta linha que muda.

**Alternativas descartadas**: exibir **sempre** ao titular, que é mais coerente com direito do
titular e deixa a superfície permanente; e exibir até o resultado virar **definitivo**, que é mais
simples de explicar e mantém a superfície aberta por todo o certame.

### D-002 — o parecer é o da avaliação que fundamenta o resultado

Medição, e não escolha: o resultado aponta para **uma** avaliação, e é o parecer dela que responde
pelo que foi decidido. O outro registro de parecer no sistema é **histórico de reaberturas**,
append-only, e existe para que *"o que aquela pessoa havia concluído antes"* seja consulta e não
arqueologia — é ele a fonte quando houve reabertura (`FR-523`).

### D-003 — a prova chega por referência, e o alcance morre com o ato

Copiar o documento para o recurso multiplicaria a superfície do dado pessoal e criaria uma segunda
cópia que a Constituição depois proíbe apagar. E alcance que sobrevive ao ato vira acesso permanente
pela porta dos fundos, que é a `FR-105` violada com outro nome.

Por isso: **referência** (`FR-531`), e **fim na decisão** (`FR-529`) — com o registro permanecendo,
porque nada se apaga.

### As demais premissas

- As medições de *Por que esta feature existe* são de 19/09/2026 contra `dd71d46`. **Reconfira-as no
  `plan`, e não as assuma** — nas três features anteriores, a medição corrigiu a spec duas vezes.
- Esta feature **não** depende da `035`, que está em PR aberto. Elas não se tocam.
- A faixa de identificadores deve ser **medida de novo** ao escrever a spec seguinte.

---

## Out of Scope

Cada um com spec própria:

- **O painel de condução do Processo vivo** — `ACH-25`, `E-6`. É a próxima da fila, e a nota mais
  baixa do relatório.
- **As duas datas-limite contraditórias do recurso** — `ACH-41`, `E-4`. É vizinho desta feature e
  tem causa própria: validação cruzada entre fontes normativas.
- **O pacote de microcópia e navegação** — o link do corte condicionado à regra de corte, mais
  `ACH-02`, `ACH-30`, `ACH-08` e `ACH-16`.
- **As sete recusas de autorização fora das portas** — registradas no inventário da `033`.
- **O renderizador normativo único das telas de ato** — `E-3`.
- **A derivação de recortes do sorteio** — achado registrado pela `034`.
- **O Perfil que declara cotas sem apontar a ampla** e por isso não recebe inscrição de não-cotista —
  achado registrado pela implementação da `034`, em
  [achado-percurso-ampla-sem-inscricao.md](../034-ordem-por-recorte/achado-percurso-ampla-sem-inscricao.md).

---

## Conformidade com a Constituição

**Princípio III — Segurança, Proteção de Dados e Auditoria.** É o princípio que governa esta feature,
e o que a torna delicada: ela **concede acesso a dado pessoal**. Quatro garantias respondem por isso —
`FR-528` limita o alcance a um recurso, `FR-529` o encerra com a decisão, `FR-531` evita a cópia, e
`FR-533`/`FR-534` registram o ato **e** o acesso. `SC-184` e `SC-185` são os critérios que os prendem.

**Princípio II — Imutabilidade e Temporalidade.** `FR-529` diz a distinção que o princípio exige: o
**registro** de que a instrução houve permanece; o **alcance** que ela concedia termina. Nada se
apaga. E `FR-523` aplica ao parecer a mesma doutrina que o projeto já aplica a ato histórico — vale o
que o ato citou, não o estado de hoje.

**Princípio VI — Completude de Jornada.** A jornada do recurso passa a ser percorrível com o que ela
precisa dos dois lados: `SC-182` pelo canal do candidato, `SC-183` pela interface administrativa.

**Princípio I — Linguagem Ubíqua.** *Parecer*, *recurso*, *instrução* e *prazo recursal* são do
domínio normativo. `FR-532` reusa a formulação de pedido que o produto já pratica, em vez de criar
uma segunda.
