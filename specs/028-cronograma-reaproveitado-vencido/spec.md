# Feature Specification: Cronograma reaproveitado não nasce publicável

**Feature Branch**: `claude/cronograma-datas-vencidas-196da2`

> **A numeração é `028` porque veio de `--number 28`**, e não da última pasta em `specs/`. A
> varredura de 15/09/2026 percorreu as seis worktrees desta máquina: nenhuma tem `028`, e três já
> têm a `027`.

> **Os identificadores continuam a faixa global**, política aberta pela `024` e confirmada pela
> `025` e pela `027`: duas features simultâneas em worktrees diferentes não descobrem o número uma
> da outra pela pasta. Teto medido em todas elas antes de escrever — `FR-340`, `SC-111`, `UX-046`
> —, e esta spec abre em `FR-341`, `SC-112`, `UX-047`. As **decisões** reiniciam em `D-001`, porque
> são lidas dentro da feature que as produziu.

**Created**: 2026-09-15

**Status**: Draft

**Input**: achado P0 da [auditoria exploratória de UX de 13/09/2026](../../doc/auditoria-exploratoria-ux-2026-09-13.md),
§4 fricção #2 (S3) e §14 — o **último** dos três P0 daquela lista. O do quadro de vagas é a `027`; o
da porta de entrada do recurso já estava fechado pelo PR #113, como a `027` registrou.

> **A frase que governa:** um Edital cujo prazo de inscrição já venceu não é publicável, e um
> cronograma vencido não se anuncia concluído.

> **E a frase que mantém o corte:** esta feature **não move data nenhuma**. O conteúdo continua
> sendo reaproveitado inteiro; o que muda é o que o sistema diz sobre ele.

---

## 1. O achado que organiza a feature

A auditoria criou o **Edital 12/2027 a partir do 90/2026**, que é exatamente a jornada para a qual a
`023` foi construída. O que o sistema disse sobre o Edital recém-nascido:

| Onde o sistema poderia ter dito | O que ele disse |
|---|---|
| As nove etapas do assistente | **todas CONCLUÍDA**, inclusive o Cronograma |
| Etapa 9 · Revisão | **uma única linha** — "AVISO O Edital não possui descrição" |
| O Cronograma copiado | "Período de inscrição — Início: **13/09/2026 08:00** · Término: **13/09/2026 09:00**" |
| Submissão, homologação, publicação | nada |

Uma janela de **uma hora**, do **ano anterior** ao do Edital, **já encerrada** — e o Edital seguia
para a publicação sem uma pendência. Nada na validação fala de evento no passado, de ano divergente
do Edital, nem de janela de uma hora.

**Não é erro de quem digita, e a `023` já o previu por escrito.** O reaproveitamento copia o
conteúdo normativo inteiro, datas inclusive, e avisa isso muito bem em prosa na tela de composição
— *"Datas, vagas e prazos são da oferta anterior até que alguém os revise"*. Mas o **estado** das
etapas não reflete o aviso, e a validação de publicabilidade não conhece "data no passado". A `023`
chegou a nomear os dois resíduos e a deixar cada um para uma spec própria:

- o resíduo do selo, declarado ao decidir que nenhum gate novo entraria: *"Depois da cópia, todas
  aparecem concluídas — e ninguém as compôs para esta oferta"*;
- no Out of Scope, a regra da data: *"Recusar publicação de Edital com período de inscrições
  vencido. É regra de **todo** Edital, e não remendo desta cópia. Se a instituição a quiser, ela
  tem spec própria e protege o acervo inteiro."*

**Esta é a spec própria**, e o recorte dela é o que aquela frase pediu: a regra vale para todo
Edital em elaboração, e não só para o que nasceu de cópia.

### 1.1 Por que é P0 pelo critério da própria auditoria

> *"O que P0 significa aqui: risco operacional — o certame pode sair errado, e o erro só aparece
> quando já não há como desfazê-lo."*

Publicar é ato imutável. Um Edital publicado com o período de inscrições já encerrado publica um
certame que **ninguém pode disputar**, e a correção não é digitar de novo: é Retificar — ato com
signatário, motivo e publicação própria, por um defeito que o sistema poderia ter acusado antes de
custar nada. E o `year` do Edital é **não retificável** pelo contrato da `026`, com razão escrita:
*"ano e número identificam o certame perante terceiros"*. Quem publicou um Edital de 2027 com o
cronograma de 2026 não tem, depois, um caminho que reconcilie os dois pelo lado do ano.

### 1.2 Quem é afetado

Exatamente a persona para quem a `023` foi construída. A amostra real de Editais que originou
aquela feature mede o caso: *"o 78 é o 59 com quatro alterações — título, uma frase, as quantidades
e **o cronograma inteiro**"*. Trocar o cronograma **é** o trabalho principal do reaproveitamento, e
é o único que o sistema não cobra.

---

## 2. O que já existe, e que esta feature NÃO reconstrói

- **A conferência de conteúdo com três severidades** — informação, advertência e erro impeditivo —,
  que já bloqueia a publicação diante do impeditivo e já encaminha cada pendência para a etapa do
  assistente que a resolve. Esta feature acrescenta **casos**, e não mecanismo.
- **A distinção entre os dois atos que conferem conteúdo** — `ATO_DE_PUBLICACAO` e
  `ATO_DE_RETIFICACAO` —, que a `027` introduziu em `validation.py` com a razão escrita: uma
  exigência impeditiva sem esse recorte *"bloquearia toda Retificação de todo Edital do acervo —
  inclusive as que corrigem uma data e nada têm com vagas"*. Esta feature usa a distinção que já
  está lá, e não a altera.
- **A zona temporal institucional**, declarada uma vez no domínio, com a razão escrita: *"os prazos
  de um Edital do Cefor correm em Vitória, qualquer que seja o servidor"*.
- **O reaproveitamento inteiro** (`023`): a fonte é a versão vigente, a escrita entra por
  `replace_draft`, o Evento copiado nasce `PLANEJADO`, a identificação não é copiada. Nada disso
  muda.
- **Os achados que o período de inscrições já tem** — nenhum Evento marcado (advertência) e mais de
  um marcado (impeditivo). Esta feature não os toca e não os reusa.
- **O selo derivado das etapas do assistente**, com os três estados que a `006` fixou. Esta feature
  muda o **critério de um** deles, e de nenhum outro.
- **O contrato de mutabilidade** (`026`), que governa esta feature em vez de ser alterado por ela.

---

## 3. Decisões fechadas antes do planejamento

### D-001 — O conteúdo continua sendo reaproveitado inteiro

A cópia não muda: nem o que ela copia, nem como. A `023` decidiu a cópia **integral** do que a
composição desenha, e continua valendo. O que esta feature entrega é o que o sistema **diz** sobre o
que foi copiado.

> **As decisões da `023` são citadas aqui pelo que dizem, e não pelo número delas**, como a `027`
> fixou. A numeração de decisão é lida dentro da feature que a produziu, e esta feature reinicia em
> `D-001`: um `D-004` escrito nesta página aponta para a decisão desta página, e não para a
> daquela.

Reaproveitar sem datas seria a tentação óbvia e é a saída errada: o cronograma anterior é a melhor
referência que existe para o novo — a estrutura dos Eventos, a ordem, as durações relativas, os
locais. Apagá-lo obrigaria a redigitar o que estava certo para consertar o que estava velho.

### D-002 — Data nenhuma é corrigida ou deslocada automaticamente, em nenhuma hipótese

Quem declara prazo é quem assina o Edital. Deslocar a data de outra pessoa — somar um ano, empurrar
para amanhã, "ajustar" a janela de uma hora — é a mesma classe de erro que a Constituição proíbe no
conteúdo publicado: o sistema decidindo norma.

A recusa alcança o automático **e** o sugerido-preenchido. Um botão de deslocamento em bloco, se
algum dia existir, é decisão de quem opera e tem spec própria; aqui ele fica fora de escopo, dito
por extenso, para que ninguém o acrescente achando que é conveniência inofensiva.

### D-003 — O selo do Cronograma passa a considerar validade, e só ele

Hoje o selo é derivado de `eventos.exists()`: **existe Evento, logo está concluída**. É a forma
literal do achado P2 da auditoria — *"CONCLUÍDA significa 'apertei Avançar'"* —, e esta feature o
fecha **para esta etapa**.

O Cronograma que carrega Evento no passado **não se exibe concluído**. Os oito selos restantes ficam
como estão: generalizar o critério é outra feature, com outro custo, e cada etapa tem uma noção
própria de "válida" que precisa ser decidida uma a uma.

> **Pendente não é impedimento.** O selo orienta quem retoma o trabalho; ele não fecha porta. Quem
> impede é o achado impeditivo da D-004, e ele é um só.

### D-004 — Três achados novos, e a severidade de cada um tem razão

| Achado | Severidade | Por quê |
|---|---|---|
| Evento com início **ou** término no passado | **ADVERTÊNCIA** | há Edital legítimo com evento vencido — a Retificação que corrige o cronograma parcial, o Edital que registra o que já ocorreu |
| Evento cujo ano diverge do ano do Edital | **ADVERTÊNCIA** | um Edital publicado em dezembro marca eventos do ano seguinte, e isso é normal |
| Período de inscrições **já encerrado** | **ERRO IMPEDITIVO** | publicar um Edital cujas inscrições já fecharam é publicar um certame que ninguém pode disputar |

O terceiro é o único que fecha porta, e fecha porque não existe leitura em que ele seja legítimo: o
Edital publicado assim não recebe inscrição nenhuma, e a única saída é Retificar um ato que acabou
de nascer.

### D-005 — Janela curta não é achado, e a de uma hora já é acusada por outro motivo

A auditoria mediu uma janela de inscrição de **uma hora** e a nomeou como parte da evidência. Esta
feature **não** cria regra de duração mínima: duração é decisão normativa, e uma hora é janela
legítima para um sorteio, uma sessão de prova, uma audiência. Declarar um mínimo seria o sistema
escrevendo norma de calendário que nenhum Edital lhe pediu.

A janela do 12/2027 é acusada porque estava **encerrada**, e é só o que ela precisa que se diga.

### D-006 — O ano do Edital adverte e nunca recusa

Um Edital de 2027 publicado em dezembro de 2026 marca legitimamente eventos dos dois anos. Recusar a
divergência transformaria um Edital correto em impublicável.

E há a segunda razão, que é o contrato: o `year` é **não retificável** (`026`). A divergência não se
resolve mudando o ano do Edital — resolve-se mudando as datas, ou não se resolve. Um impedimento
aqui apontaria para um campo que ninguém pode mexer.

### D-007 — Os três achados são condicionados ao ato, e nenhum deles existe na Retificação

No ato de Retificação, evento no passado é a **condição normal do acervo**: todo Edital publicado
tem cronograma que vence com o tempo. Produzir advertência ali faria toda Retificação de todo Edital
antigo — inclusive a que corrige uma vírgula — carregar uma advertência por Evento vencido, e o que
se repete a cada ato deixa de ser lido. Recusar prenderia o acervo inteiro.

É a mesma forma que a `027` já pratica em `_linha_geral_exigida` e `_acervo_sem_quadro`, e pela mesma
razão. Os códigos desta feature são **próprios**, e não reusam nenhum existente: um código é o que a
tela, o teste e a trilha usam para dizer de que achado se trata, e reaproveitá-lo faria dois defeitos
diferentes responderem pelo mesmo nome.

### D-008 — A referência temporal é o instante do ato, lido na zona institucional

O Princípio II é literal: *"Regras de calendário DEVEM usar a zona temporal institucional definida
pelo domínio; operações relacionadas DEVEM compartilhar referência temporal consistente na mesma
transação."*

Duas consequências que não são detalhe:

- **O ano do Evento é o ano que a zona institucional lê.** Um Evento em 31/12/2026 às 23:30 em
  Vitória é 01/01/2027 em UTC. Lido em UTC, ele divergiria do ano de um Edital de 2026 que o declara
  corretamente — advertência inventada, e só de madrugada. É exatamente a classe registrada em
  [doc/achado-teste-com-data-em-utc.md](../../doc/achado-teste-com-data-em-utc.md), e ela já cobrou
  uma vez.
- **O instante é um só por ato.** Conferir cada Evento contra um relógio lido de novo faria dois
  Eventos do mesmo cronograma serem julgados contra instantes diferentes.

### D-009 — A conferência roda no ponto mais cedo em que existe o que conferir, e de novo antes de publicar

Não é conferência nova: é a mesma, chamada mais cedo. Assim que existe Cronograma com Evento —
inclusive imediatamente depois do reaproveitamento, sem que ninguém tenha gravado nada —, o que esta
feature acusa já é acusável, e é onde a correção custa zero.

E de novo na publicação, porque a Revisão pode não ter sido aberta e porque o tempo passa entre um
ponto e outro: um período que estava aberto quando a Revisão foi lida pode estar encerrado quando a
publicação é confirmada. **A publicação é onde o impedimento é final.**

### D-010 — A demonstração passa a conter o caso, e o Edital dele fica em elaboração

`seed_demo` ganha um **quarto** Edital, criado por reaproveitamento de um dos três existentes, com o
cronograma da oferta anterior. Ele **não é publicado** — não pode ser, e é esse o ponto: ele é a
demonstração de um Edital que o sistema segura.

Os três Editais existentes não mudam. A demonstração continua contando a jornada inteira; ela ganha
o caso em que a jornada **para**, com o motivo dito.

### D-011 — Nada entra no conteúdo publicado

Nenhum campo novo, nenhuma marca, nenhum estado persistido. Os achados são **leitura** do conteúdo
que já existe, contra um instante. A forma publicada do Evento não muda, o contrato de mutabilidade
não muda, e nenhum Edital já publicado passa a afirmar coisa diferente do que afirmava.

---

## 4. Problema

Quem reaproveita um Edital anterior — a persona para quem a `023` existe — recebe um Edital novo com
todas as nove etapas marcadas CONCLUÍDA, uma Revisão que lista uma pendência cosmética e um
cronograma do ano passado, já vencido. Segue para a publicação sem que nada o detenha, e publica um
certame que ninguém pode disputar. A partir daí, a correção é uma Retificação.

O estado medido em 13/09/2026:

```
Etapas marcadas CONCLUÍDA no Edital recém-copiado         9 de 9
Linhas na Revisão sobre o cronograma vencido              0
Achados da validação sobre data no passado                0
Achados da validação sobre ano divergente do Edital       0
Achados da validação sobre inscrição já encerrada         0
Editais que o sistema impediria de publicar assim         0
```

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O cronograma copiado não se anuncia pronto (Priority: P1)

Quem cria o Edital 12/2027 a partir do 90/2026 abre a composição e vê a etapa Cronograma **pendente**
— não concluída —, com a frase que diz por quê: o cronograma veio da oferta anterior e carrega
eventos que já passaram. Nenhuma data foi mexida.

**Why this priority**: é o sinal que chega **antes** de qualquer outro, sem que ninguém precise abrir
a Revisão, e é o que fecha o resíduo que a `023` declarou na D-006.

**Independent Test**: reaproveitar um Edital cujo cronograma esteja no passado e abrir a composição —
a etapa Cronograma aparece pendente na primeira abertura, sem nenhuma gravação.

**Acceptance Scenarios**:

1. **Given** um Edital criado por reaproveitamento cujo Cronograma carrega Evento no passado,
   **When** a composição é aberta pela primeira vez, **Then** a etapa Cronograma exibe-se
   **pendente**, e não concluída.
2. **Given** o mesmo Edital, **When** a etapa Cronograma é aberta, **Then** ela diz, em texto visível
   a quem enxerga, por que está pendente e quais Eventos já passaram.
3. **Given** o mesmo Edital, **When** as datas de todos os Eventos passam a ser futuras, **Then** a
   etapa volta a exibir-se concluída, sem exigir nenhuma gravação além da própria correção.
4. **Given** o mesmo Edital, **When** a composição é aberta, **Then** nenhuma data do Cronograma
   difere daquela que a cópia trouxe.
5. **Given** um Edital cujo Cronograma está inteiro no futuro, **When** a composição é aberta,
   **Then** a etapa exibe-se concluída, como hoje, e as demais oito etapas mantêm o critério que já
   tinham.

---

### User Story 2 — Publicar um certame que ninguém pode disputar é impedido (Priority: P1)

Quem submete o Edital 12/2027 com o período de inscrições encerrado é **recusado**, na Revisão e na
publicação, com o instante do encerramento dito e a consequência nomeada. Nenhuma data é ajustada por
ele.

**Why this priority**: é o que impede o dano irreversível. Sem isto, tudo o mais é aviso que se pode
ignorar.

**Independent Test**: compor um Edital cujo Evento marcado como período de inscrições termina no
passado e tentar publicá-lo — a publicação é recusada, e a mensagem diz quando o prazo venceu.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração cujo período de inscrições terminou ontem, **When** a Revisão é
   aberta, **Then** há erro impeditivo dizendo quando as inscrições se encerraram e que o Edital
   publicado assim não receberá inscrição alguma.
2. **Given** o mesmo Edital, **When** a publicação é tentada sem que a Revisão tenha sido aberta,
   **Then** ela é recusada pelo mesmo impedimento.
3. **Given** o mesmo Edital, **When** as datas do período são corrigidas para o futuro, **Then** o
   impedimento desaparece e a publicação prossegue.
4. **Given** um Edital cujo período de inscrições **começou** e ainda não terminou, **When** a
   publicação é tentada, **Then** ela **não** é impedida — há advertência pelo início no passado, e
   nada mais.
5. **Given** um Edital cujo Evento marcado como período de inscrições não declara término, **When** a
   publicação é tentada, **Then** ela não é impedida por esta feature: sem término declarado não há
   encerramento.
6. **Given** um Edital que não marca Evento algum como período de inscrições, **When** a Revisão é
   aberta, **Then** o que se lê é a advertência que já existia, e nenhum achado novo.
7. **Given** qualquer um dos casos acima, **When** a conferência roda, **Then** o conteúdo do
   rascunho é idêntico ao que era antes dela.

---

### User Story 3 — Advertir sem recusar o Edital de dezembro (Priority: P1)

Quem compõe, em dezembro de 2026, um Edital 12/2027 cujos eventos correm em 2027, lê uma advertência
que nomeia a divergência de ano — e publica. Quem compõe o mesmo Edital com as datas de 2026 lê a
mesma advertência **e** a de evento no passado, e continua podendo publicar se as inscrições ainda
não fecharam.

**Why this priority**: é o que separa esta feature de um bloqueio que tornaria impublicável o Edital
mais comum do fim do ano.

**Independent Test**: compor um Edital de ano seguinte com eventos futuros e ver a advertência sem
impedimento; compor o cenário do 12/2027 e ver as três coisas ao mesmo tempo.

**Acceptance Scenarios**:

1. **Given** um Edital de 2027 cujos Eventos correm em 2027, sendo hoje dezembro de 2026, **When** a
   Revisão é aberta, **Then** há advertência de ano divergente e nenhum impedimento, e a publicação
   prossegue.
2. **Given** o cenário medido pela auditoria — Edital 12/2027, Evento "Período de inscrição" de
   13/09/2026 08:00 a 13/09/2026 09:00, conferido depois disso —, **When** a Revisão é aberta,
   **Then** ela exibe **três** achados desta feature: a advertência de evento no passado, a
   advertência de ano divergente e o impedimento de inscrições encerradas.
3. **Given** o mesmo cenário, **When** a Revisão é aberta, **Then** ela **não** afirma que nada está
   pendente.
4. **Given** um Evento que está no passado **e** cujo ano diverge, **When** a conferência roda,
   **Then** cada uma das duas advertências aparece **uma vez** para aquele Evento, e cada uma nomeia
   o Evento e o instante de que fala.
5. **Given** um Edital em 31/12/2026 com Evento às 23:30 do horário de Vitória, **When** a
   conferência roda, **Then** o ano lido é 2026, e nenhuma advertência de divergência é produzida.
6. **Given** qualquer advertência desta feature, **When** ela é exibida, **Then** ela mostra a data
   em forma legível na zona institucional, e nunca texto ISO cru nem instante em UTC.
7. **Given** um Edital composto do zero, sem reaproveitamento, cujo Cronograma tem Evento no passado,
   **When** a Revisão é aberta, **Then** os mesmos achados aparecem: a regra é de todo Edital.

---

### User Story 4 — Retificar um Edital antigo não vira enxurrada (Priority: P1)

Quem retifica o Edital 01/2026 para corrigir uma frase não lê uma advertência por Evento vencido do
cronograma inteiro, e não é recusado porque as inscrições daquele Edital fecharam há meses.

**Why this priority**: sem este recorte, a feature que protege o Edital novo inutiliza a Retificação
de todo o acervo — o mesmo erro que a `027` já teve de nomear para não cometer.

**Independent Test**: abrir a conferência de uma Retificação sobre um Edital publicado com cronograma
inteiramente vencido e contar os achados desta feature: zero.

**Acceptance Scenarios**:

1. **Given** um Edital publicado cujo cronograma inteiro já passou, **When** uma Retificação é
   conferida, **Then** nenhum dos três achados desta feature é produzido.
2. **Given** o mesmo Edital, **When** a Retificação é publicada, **Then** ela não é recusada por esta
   feature.
3. **Given** uma Retificação que antecipe o encerramento das inscrições para um instante já passado —
   ato normativo legítimo —, **When** ela é conferida, **Then** ela não é recusada por esta feature.
4. **Given** a mesma Retificação, **When** ela é conferida, **Then** os achados que já existiam sobre
   o período de inscrições continuam sendo produzidos como antes, sem alteração.

---

### User Story 5 — A demonstração contém o caso (Priority: P2)

Quem abre a demonstração encontra, além dos três Editais que já existiam, um **quarto** criado por
reaproveitamento: cronograma da oferta anterior, etapa Cronograma pendente, Revisão com os três
achados, publicação recusada.

**Why this priority**: é a jornada demonstrável de que o Princípio VI depende, e é o que impede a
feature de ser verdadeira só em teste.

**Independent Test**: semear a demonstração e percorrer o quarto Edital, da composição até a recusa
da publicação.

**Acceptance Scenarios**:

1. **Given** a demonstração recém-semeada, **When** o quarto Edital é aberto na composição, **Then**
   a etapa Cronograma exibe-se pendente.
2. **Given** o mesmo Edital, **When** a Revisão é aberta, **Then** ela exibe a advertência de evento
   no passado, a advertência de ano divergente e o impedimento de inscrições encerradas.
3. **Given** o mesmo Edital, **When** a publicação é tentada, **Then** ela é recusada, e ele
   permanece em elaboração.
4. **Given** a demonstração recém-semeada, **When** os três Editais anteriores são lidos, **Then**
   eles estão exatamente como estavam.

---

### Edge Cases

- **Evento sem término declarado.** O passado se mede pelo início; a ausência de término não é
  término no passado, e nunca encerra o período de inscrições.
- **Evento em curso** — começou e não terminou. Início no passado produz a advertência; nada impede.
  É o caso do Edital que abre inscrições e é publicado no mesmo dia.
- **Término exatamente igual ao instante do ato.** Não está encerrado. O encerramento é
  **estritamente** anterior, porque o prazo que termina agora ainda é prazo.
- **Cronograma com Eventos no passado e no futuro.** Basta um no passado para a etapa ficar pendente
  e para a advertência existir; ela nomeia cada Evento afetado.
- **Edital cujo ano é o corrente e cujos Eventos são do ano corrente, mas já passaram.** Advertência
  de passado, e nenhuma de ano: são achados distintos porque dizem coisas distintas.
- **Edital que não marca período de inscrições.** A advertência que já existe continua sendo a única;
  esta feature não a duplica nem a agrava.
- **Mais de um Evento marcado como período de inscrições.** O impeditivo que já existe responde
  primeiro; esta feature não empilha um segundo relato sobre a mesma causa.
- **O Evento do período encerrado produz advertência *e* impedimento.** Um período encerrado é,
  necessariamente, um Evento no passado: o mesmo Evento recebe a advertência da FR-343 e o
  impedimento da FR-346, e as duas coisas convivem. Não é contradição com o "MUST NOT impedir" da
  FR-343 — a advertência continua não impedindo nada; quem impede é o outro achado, que fala de
  outra coisa. Uma diz *"esta data já passou"*; a outra diz *"este Edital não receberá inscrição
  alguma"*, e suprimir qualquer uma delas esconderia metade do que a pessoa precisa saber para
  decidir o que corrigir.
- **Edital composto do zero com data no passado.** Mesmos achados. A regra é de todo Edital, como a
  `023` escreveu ao deixá-la fora do escopo dela.
- **Edital publicado antes desta feature cujo cronograma venceu.** Nada muda: não se recusa o que já
  foi publicado, e a Retificação dele não ganha achado novo (D-007).
- **Evento com início posterior ao término.** Já é impossível pela restrição do banco, e não é
  assunto desta feature.
- **Cronograma cujos Eventos estão fora de ordem cronológica entre si.** Fora de escopo: é coerência
  de sequência, não de vencimento.

---

## Requirements *(mandatory)*

### Functional Requirements

#### A referência temporal

- **FR-341**: A conferência MUST comparar cada Evento contra **um** instante por ato — o instante em
  que o ato é conferido —, e MUST NOT ler o relógio mais de uma vez dentro do mesmo ato.
- **FR-342**: O ano de um Evento MUST ser o ano que a **zona temporal institucional** lê do instante
  declarado, e NÃO DEVE ser lido em UTC nem no fuso do servidor (Princípio II).

#### Os três achados

- **FR-343**: Evento cujo início **ou** término seja estritamente anterior ao instante do ato MUST
  produzir **advertência**, uma por Evento, nomeando o Evento e o instante vencido, e MUST NOT
  impedir a submissão nem a publicação.
- **FR-343a**: Quando início **e** término já passaram, a advertência MUST nomear o **término** —
  e o início apenas quando não houver término declarado. *É o instante mais tardio, e é o que diz
  que o Evento inteiro acabou: nomear o início faria a mensagem falar de um prazo que ainda podia
  estar correndo quando a pessoa o leu. A precedência é declarada porque, sem ela, "o instante
  vencido" admite duas leituras e cada implementação escolheria uma.*
- **FR-344**: Evento cujo ano divirja do ano do Edital MUST produzir **advertência própria**,
  distinta da anterior, e MUST NOT impedir a submissão nem a publicação (D-006).
- **FR-345**: Um Evento que satisfaça as duas condições MUST produzir as duas advertências, cada uma
  **uma vez**, e cada uma MUST nomear o instante de que fala.
- **FR-346**: O Evento marcado como período de inscrições cujo término seja estritamente anterior ao
  instante do ato MUST produzir **erro impeditivo**, que MUST impedir **a submissão e a publicação**.

  > **"Submissão", e não "avanço".** Nesta spec *avanço* tem um sentido só — passar de uma etapa do
  > assistente para a seguinte —, e é o da FR-362. O que este achado fecha é o ato que leva o Edital
  > à publicação, e não o botão que muda de tela: quem o lê como travamento da navegação prende a
  > pessoa justamente na etapa onde ela corrigiria a data.
- **FR-347**: O impedimento da FR-346 MUST NOT ser produzido quando o Evento marcado não declara
  término, quando o término é futuro, ou quando o término é exatamente o instante do ato.
- **FR-348**: Os três achados MUST ter códigos próprios e MUST NOT reusar nem alterar os códigos já
  existentes sobre o período de inscrições — ausência de marca e marca ambígua permanecem como estão.
- **FR-349**: Cada achado MUST encaminhar quem o lê à etapa **Cronograma**, que é onde a data se
  corrige, e NÃO DEVE encaminhar à etapa de Inscrição, que é onde se resolve a **designação** do
  período e não o instante dele.
- **FR-350**: Esta feature MUST NOT alterar, remover nem reordenar nenhum achado já existente.

#### O que a conferência não faz

- **FR-351**: A conferência MUST NOT alterar, deslocar, sugerir como valor preenchido, nem propor
  automaticamente qualquer data do Cronograma, em nenhuma hipótese (D-002).
- **FR-352**: A conferência MUST NOT criar regra de duração de Evento — mínima, máxima ou típica
  (D-005).
- **FR-353**: Esta feature MUST NOT acrescentar campo, marca ou estado ao conteúdo publicado, e MUST
  NOT alterar a forma publicada do Evento nem a natureza declarada de campo algum no contrato de
  mutabilidade (`026`, FR-297).

#### O ato

- **FR-354**: Os três achados MUST ser produzidos no ato de publicação e MUST NOT ser produzidos no
  ato de Retificação (D-007).
- **FR-355**: A Retificação que declare término de inscrições já passado MUST NOT ser recusada por
  esta feature: antecipar ou encerrar prazo é ato normativo de quem assina.

#### Quando a conferência roda

- **FR-356**: A conferência MUST rodar assim que existir Cronograma com ao menos um Evento —
  inclusive imediatamente depois do reaproveitamento, sem gravação alguma — e a cada gravação do
  Cronograma.
- **FR-357**: A conferência MUST rodar de novo na publicação, e o impedimento da FR-346 MUST recusar
  a publicação ainda que a Revisão nunca tenha sido aberta.
- **FR-358**: O resultado da conferência MUST refletir o instante em que ela roda: um período aberto
  na Revisão e encerrado na publicação MUST impedir a publicação.

#### O selo da etapa

- **FR-359**: O selo da etapa Cronograma MUST NOT exibir-se concluído enquanto o Cronograma carregar
  Evento no passado; o critério passa a considerar **validade**, e não apenas existência de Evento
  (D-003).
- **FR-360**: O selo MUST voltar a exibir-se concluído assim que nenhum Evento estiver no passado,
  sem exigir gravação além da própria correção.
- **FR-361**: Esta feature MUST NOT alterar o critério de nenhum dos demais selos do assistente.
- **FR-362**: O estado pendente do Cronograma MUST NOT, por si, impedir o avanço entre etapas nem a
  submissão; quem impede é o achado impeditivo da FR-346.

#### Aplicabilidade

- **FR-363**: Os achados MUST valer para todo Edital em elaboração, tenha ele nascido de
  reaproveitamento ou não (`023`, Out of Scope).
- **FR-364**: Esta feature MUST NOT alterar o que o reaproveitamento copia nem como ele copia
  (`023`, FR-006 e FR-008a).
- **FR-365**: Esta feature MUST NOT recusar, alterar nem reescrever conteúdo já publicado
  (Princípio II).

#### A demonstração

- **FR-366**: A demonstração oficial MUST conter um Edital criado por **reaproveitamento** cujo
  Cronograma exercite o cenário medido: Evento no passado, ano divergente do Edital e período de
  inscrições encerrado.
- **FR-367**: Esse Edital MUST permanecer **em elaboração**, porque o sistema o impede de publicar, e
  a demonstração MUST NOT alterar os Editais que ela já produzia.

### Requisitos de apresentação

- **UX-047**: Toda advertência desta feature MUST nomear o Evento e exibir o instante em forma
  legível na **zona institucional**, e NÃO DEVE apresentar texto ISO cru, JSON Pointer nem instante
  em UTC.
- **UX-048**: O impedimento MUST dizer **quando** as inscrições se encerraram e **o que acontece** se
  o Edital for publicado assim — nenhuma inscrição será recebida —, e MUST nomear a etapa onde a data
  se corrige.
- **UX-049**: A etapa Cronograma MUST explicar, em texto visível a quem enxerga, por que está
  pendente e quais Eventos a mantêm assim; a explicação NÃO DEVE depender de conteúdo oculto a quem
  enxerga.
- **UX-050**: A Revisão MUST NOT afirmar que nada está pendente enquanto houver achado desta feature.
- **UX-051**: A tela que apresenta o Edital reaproveitado MUST continuar dizendo que datas, vagas e
  prazos vieram da oferta anterior (`023`, FR-014), e o novo sinal MUST somar-se a esse aviso em vez
  de substituí-lo.

### Key Entities

- **Evento do Cronograma**: já existe, e não muda. Ganha três leituras contra um instante — início
  vencido, término vencido, ano divergente.
- **Período de inscrições**: já existe como marca no Evento. Ganha a leitura de encerramento, que é o
  único impedimento desta feature.
- **Achado de conferência**: já existe, com três severidades e destino por etapa. Ganha três casos e
  a condição por ato que a `027` introduziu.
- **Selo da etapa do assistente**: já existe, com três estados. O critério do Cronograma passa a
  considerar validade.

---

## 5. Invariantes observáveis

Verificáveis a qualquer momento, em qualquer estado do acervo:

1. Nenhuma data do Cronograma é alterada, deslocada ou preenchida pelo sistema.
2. Nenhum Edital é publicado por esta interface com o período de inscrições já encerrado.
3. Nenhum Cronograma com Evento no passado se exibe concluído.
4. Nenhum achado desta feature é produzido num ato de Retificação.
5. Nenhum conteúdo publicado muda, nem passa a afirmar coisa diferente da que afirmava.
6. Nenhuma leitura de calendário desta feature usa fuso que não o institucional.
7. Nenhuma das advertências desta feature impede avanço entre etapas, submissão ou publicação.
8. Nenhum selo do assistente além do Cronograma muda de critério.

> **O primeiro é o que a feature inteira protege.** Todos os outros descrevem o que o sistema passa a
> dizer; esse descreve o que ele continua a **não** fazer — e é o único que, quebrado, reproduz por
> dentro o defeito que a Constituição proíbe do lado de fora.

---

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-112**: Zero Editais compostos por esta interface são publicados com o período de inscrições já
  encerrado — hoje a operação é possível e nada a acusa.
- **SC-113**: 100% dos Editais criados por reaproveitamento cujo Cronograma carrega Evento no passado
  exibem a etapa Cronograma como pendente já na primeira abertura, sem nenhuma gravação — hoje são
  0%, e as nove etapas aparecem concluídas.
- **SC-114**: O cenário medido pela auditoria — Edital 12/2027 a partir do 90/2026, janela de
  13/09/2026 08:00 a 09:00 — produz exatamente três achados desta feature, e a publicação é recusada.
- **SC-115**: A conferência de uma Retificação sobre Edital publicado com cronograma inteiramente
  vencido produz **zero** achados desta feature.
- **SC-116**: O conteúdo do rascunho depois de qualquer conferência desta feature é idêntico ao que
  era antes dela — nenhuma data, campo ou ordem alterada.
- **SC-117**: Quem reaproveita descobre o cronograma vencido **antes de submeter**, e não depois de
  publicar, sem consultar documentação — verificável por percurso de composição.
- **SC-118**: Os achados desta feature produzem o mesmo resultado em qualquer fuso de servidor,
  inclusive de madrugada — verificável por teste que fixe o instante do ato.
- **SC-119**: A demonstração oficial contém o Edital reaproveitado que exercita o cenário, e ele é
  percorrível da composição até a recusa da publicação.

---

## 7. Out of Scope

Fora deste incremento, e cada item com a razão:

- **Qualquer remodelagem de `PerfilVaga`.** Depende da decisão de modelagem registrada na issue do
  achado [das atribuições repetidas por polo](../../doc/achado-atribuicoes-repetidas-por-polo.md),
  que é do usuário e não desta feature.
- **Deslocar datas em bloco** — somar um ano ao cronograma inteiro, empurrar tudo para a frente,
  oferecer a data corrigida como valor preenchido. D-002. Quem declara prazo é quem assina o Edital.
- **Regra de duração de Evento**, mínima ou máxima. D-005.
- **Coerência de sequência entre Eventos** — o evento B marcado antes do evento A. É outro achado,
  com outra severidade a decidir.
- **O quarto estado do assistente (*reaproveitada*)**, que a `023` deixou mapeado ao decidir não
  criar gate novo. Esta feature fecha o P2 do selo **para o Cronograma**, por validade; o estado
  novo continua sendo evolução.
- **O critério dos demais oito selos.** Cada etapa tem uma noção própria de "válida", e decidi-las em
  bloco é o que produz regra que ninguém revisou.
- **A microcópia invisível como classe** (P1 sistêmico da auditoria). Esta feature exige texto
  visível na etapa que ela toca, e não reescreve a decisão de template.
- **Recusar ou marcar Edital já publicado cujo cronograma venceu.** Publicação é ato imutável, e
  vencer é o destino normal de todo cronograma publicado.
- **Alterar o que o reaproveitamento copia** (`023`, FR-006). D-001.
- **Alterar o contrato de mutabilidade** (`026`). Esta feature o obedece.
- **Os demais achados abertos da auditoria de 13/09/2026** — a microcópia invisível, o segundo Edital
  no mesmo Processo, as trinta decisões da Classificação, a pendência de marco roteada para a tela
  errada. São registro, e o Princípio VI proíbe derivar deles automaticamente a prioridade da spec
  seguinte.

---

## Assumptions

- A `023` está entregue: o reaproveitamento copia a versão vigente da origem, o Evento copiado nasce
  `PLANEJADO`, a identificação não é copiada, e a tela avisa em prosa que datas e prazos vieram da
  oferta anterior.
- A `027` está entregue, e `validation.py` distingue `ATO_DE_PUBLICACAO` de `ATO_DE_RETIFICACAO` com
  a publicação como padrão de propósito — o padrão que erra pelo lado que recusa.
- A zona temporal institucional já existe declarada no domínio, importável por ele, e é a mesma que a
  interface usa para apresentar instantes.
- A conferência já classifica achados em informação, advertência e erro impeditivo, e já encaminha
  cada um à etapa do assistente que o resolve, por caminho e por código.
- O `year` do Edital é não retificável pelo contrato da `026`, e `startAt`/`endAt` do Evento são
  retificáveis.
- O Edital 12/2027 da auditoria não existe no repositório: ele foi criado no ambiente auditado, e o
  cenário é **reconstruído** em teste e na demonstração a partir do que a auditoria registrou.
- A restrição de banco que impede término anterior ao início continua valendo, de modo que esta
  feature não precisa conferi-la.
