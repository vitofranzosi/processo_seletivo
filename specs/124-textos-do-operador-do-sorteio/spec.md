# Feature Specification: Os textos que o operador do sorteio lê

**Feature Branch**: `claude/elegant-bohr-422170`, sobre a `main` em `250efe97`

**Created**: 2026-11-06

**Status**: Implementada (06/11), sem merge.

**Input**: três achados do guia de condução da jornada do sorteio do Edital 35/2026
(`doc/guia-jornada-do-sorteio-2026-11-05/`, quadro "Atenção" do capítulo 5 e item P3 do
diagnóstico), conferidos no código da `main` em 06/11/2026: a falha de acesso à Caixa chega crua à
tela do sorteio; o "não antes de 04/11/2026 00:00" parece a hora da extração; e a explicação do
campo da ocorrência só existe para leitor de tela.

> **Faixa de identificadores.** Esta spec abre em **FR-3961** e **SC-1191**. O teto foi medido em
> 06/11/2026 em `specs/` de todas as worktrees desta máquina: o requisito funcional três mil
> novecentos e cinquenta e o critério mil cento e oitenta e dois, da `123` que outra worktree
> escreve e que ainda não está na `main`. A pasta `123` está tomada por ela, e por isso esta é a
> `124`. A folga de dez números é de propósito: duas sessões abertas no mesmo dia já colidiram
> contando a partir do mesmo teto. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3641 da `116`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

## Por que esta feature existe

As três afirmações são de texto, e nenhuma muda o que o sistema decide. Mas a tela do sorteio é a
que a transmissão mostra, e os três textos erram justamente diante de quem conduz ao vivo:

1. **A falha de acesso à Caixa chegava crua.** O adaptador guardava
   `Última falha: URLError: <urlopen error timed out>` na evidência, e a recusa `source_unreachable`
   a concatenava na mensagem que a tela imprime. A mesma mensagem trazia `**nada foi registrado**`
   com os asteriscos, porque a tela não interpreta Markdown. A `116` já tinha decidido o princípio
   para a conferência da mesma fonte — a FR-3641 e a FR-3648 dela: motivo em palavras de quem opera,
   nada de nome de exceção nem código HTTP —, e a observação ficou fora porque a FR-3638 da `116`
   a declarava intocada.
2. **"Aconteceu não antes de 04/11/2026 00:00 — é o que a fonte publica"** é inexato. A Loteria
   Federal publica só a data; o 00h00 é o limite inferior que o sistema deduz (a FR-2649 da `102`).
   Quem conduz lê 00h00 como a hora da extração.
3. **A explicação do campo "Ocorrência que fixará a semente" só existe para leitor de tela.** Ela
   mora num `span.oculto` apontado por `aria-describedby`, no método do marco e no comum, e o bloco
   "Como preencher estes campos" da etapa não fala de ocorrência nem de concurso.

## Clarifications

### Session 2026-11-06

- Q: O veículo é a correção sob requisitos já existentes (FR-3641 e FR-3648 da `116`, FR-509 da
  `035`) ou uma spec pequena? → A: **Spec pequena** (decisão do usuário, 06/11/2026). Os
  requisitos existentes cobrem os três achados só em parte: os da `116` são da conferência, e não
  da observação.

## User Scenarios & Testing

### User Story 1 — A falha de acesso dita nas palavras de quem conduz (Priority: P1)

Com a transmissão aberta, a presidência clica em "Observar a ocorrência" e a Caixa não responde. A
tela diz por que não deu certo com a mesma frase que a conferência da publicação usaria, diz que
nada foi registrado e que observar de novo é o próximo passo — sem nome de exceção, sem código
HTTP, sem asteriscos.

**Acceptance Scenarios**:

1. **Given** a Caixa sem resposta a tempo, **When** a ocorrência é observada, **Then** a mensagem
   diz "a Caixa não respondeu a tempo", e não traz `URLError` nem `<urlopen`.
2. **Given** a Caixa respondendo com erro HTTP, **When** a ocorrência é observada, **Then** a
   mensagem diz "a Caixa respondeu com um erro", sem o código.
3. **Given** qualquer falha de acesso, **When** a mensagem é exibida, **Then** ela não contém `**`.

### User Story 2 — O limite inferior não se passa por hora da extração (Priority: P2)

Com a ocorrência observada numa fonte que publica só o dia, a tela mostra o dia e diz que a fonte
não publica a hora, e que 00h00 é o limite que o sistema conta. Numa fonte que publica a hora, a
tela continua dizendo que o instante é o que a fonte publica.

**Acceptance Scenarios**:

1. **Given** a ocorrência da Loteria Federal observada, **When** a tela do sorteio abre, **Then** o
   campo "Aconteceu não antes de" mostra a data sem hora ao lado e diz que 00h00 é o limite
   inferior, e não a hora da extração.
2. **Given** uma fonte que publica a hora, **When** a tela abre, **Then** ela mostra data e hora e
   diz que é o instante que a fonte publica.

### User Story 3 — Quem enxerga também aprende o que é a ocorrência (Priority: P3)

Quem compõe a Classificação abre "Como preencher estes campos" e encontra o que é a ocorrência,
por que ela precisa ser posterior ao congelamento e o que vai no campo, com as mesmas frases que o
leitor de tela anuncia no campo.

**Acceptance Scenarios**:

1. **Given** um marco que ordena por sorteio, **When** a etapa de Classificação abre, **Then** o
   bloco de ajuda tem o item "Ocorrência que fixará a semente", com link para o cartão.
2. **Given** o mesmo marco, **When** se comparam a ajuda da etapa e a descrição do campo, **Then**
   as frases da forma e da consequência são as mesmas, palavra por palavra.

### Edge Cases

- **Falhas diferentes nas três tentativas.** A evidência traz o motivo da última; o log traz as
  três.
- **Uma tentativa em que a fonte respondeu sem a extração.** O desfecho continua o de sempre —
  indisponibilidade, com a evidência dela —, e esta feature não o toca.
- **Fonte fora do vocabulário deste ambiente.** A tela do sorteio não afirma nem que ela publica só
  o dia nem que publica a hora: mostra o instante e diz só que é o limite inferior.
- **A resposta que não se lê como JSON.** É a Caixa respondendo com algo que não é a extração: o
  motivo é o do erro da Caixa, e não o da rede.

## Requirements

### Functional Requirements

#### A falha de acesso

- **FR-3961**: A evidência da observação que termina em **falha de acesso** MUST dizer o motivo com
  os mesmos quatro motivos da conferência da mesma fonte (a FR-3641 da `116`), pela mesma tradução.
  Ela MUST NOT trazer nome de exceção, código HTTP nem corpo da resposta.
- **FR-3962**: O detalhe técnico de cada tentativa malsucedida MUST ir ao log estruturado, num
  registro só por observação, com a fonte e a referência. Ele MUST NOT ir à mensagem nem a registro
  nenhum do banco — nada se grava na falha de acesso.
- **FR-3963**: A mensagem da recusa `source_unreachable` MUST ser texto sem marcação. A tela a
  imprime como texto, e marcação escrita nela chega literal a quem lê.

#### O limite inferior da ocorrência

- **FR-3964**: Na tela do sorteio, para fonte que publica **só a data** (a FR-2647 da `102`), o
  campo "Aconteceu não antes de" MUST mostrar a data sem hora e MUST dizer que a fonte publica só o
  dia e que 00h00 é o limite inferior que o sistema conta, e não a hora da extração.
- **FR-3965**: Para fonte que publica a hora, o campo MUST mostrar data e hora e dizer que é o
  instante que a fonte publica. Para fonte fora do vocabulário do ambiente, MUST NOT afirmar nada
  sobre o que a fonte publica.

#### A ocorrência na ajuda da etapa

- **FR-3966**: O bloco "Como preencher estes campos" da Classificação MUST ter um item sobre a
  ocorrência que fixará a semente — o que ela é, por que precisa ser posterior ao congelamento e o
  que vai no campo —, com link para o cartão do marco. A descrição escondida do campo MUST
  continuar onde está e apontada por `aria-describedby` (a FR-508 da `035`).
- **FR-3967**: As frases da forma e da consequência no item MUST ser as da descrição do campo,
  palavra por palavra. Uma segunda redação é o que a FR-509 da `035` proíbe.

#### O que não muda

- **FR-3968**: O número de tentativas, os dois desfechos negativos da observação, a ausência de
  gravação na falha de acesso, a regra de substituição e a comparação com o congelamento MUST
  continuar como estão (a FR-3638 da `116`). Muda o texto, e só ele.

### Fora do escopo — registrado, e não corrigido

- **Os asteriscos das recusas da anulação.** `sorteios/application/sorteio.py` escreve
  `relação **nova**` e `ocorrência **nova**` nas mensagens do sorteio sucessor, que a mesma tela
  imprime como texto. É o defeito da FR-3963 em outra recusa, e corrigi-lo é decisão do usuário.
- **A falha de leitura que não é `URLError`.** A observação apanha `URLError`, `TimeoutError` e
  `ValueError`. Uma conexão que cai **durante** a leitura do corpo (`ConnectionResetError`,
  `http.client.IncompleteRead`) escapa e responde 500, em vez de falha de acesso. É comportamento,
  e não texto, e a FR-3968 o deixa como está.

## Success Criteria

- **SC-1191**: Nas cinco falhas simuladas — tempo esgotado na conexão e na leitura, rede fora,
  erro HTTP, resposta que não é JSON —, a mensagem da recusa não contém nome de exceção, `<urlopen`,
  código HTTP nem `**`, e contém o motivo nas palavras da conferência.
- **SC-1192**: As três telas foram conferidas no navegador: a recusa com a fonte inacessível, o
  campo "Aconteceu não antes de" numa fonte que publica só o dia, e a ajuda da etapa de
  Classificação.

## Decisões

#### D-001 — Uma tradução da falha, para a conferência e para a observação

A tradução que morava em `_uma_chamada` saiu para `_motivo_da_falha`, e as duas chamadas a usam.
Duas traduções da mesma falha divergiriam na primeira mudança, e a mesma rede caída chegaria à
publicação com uma frase e ao sorteio com outra.

#### D-002 — A resposta que não se lê como JSON é erro da Caixa

Na observação, o `ValueError` vem da resposta que não é JSON. A Caixa respondeu, e não com a
extração: o motivo é "a Caixa respondeu com um erro". O da conferência para o mesmo caso, "a Caixa
respondeu sem o último concurso", fala do último concurso, que a observação não pergunta.

#### D-003 — A descrição escondida não encolhe

O pedido sugeria deixar na descrição escondida só o que decide o campo. Ela fica inteira: a FR-508
da `035` pede a forma **e a razão** no ponto de uso, e o leitor de tela não abre o bloco da etapa
para ouvir a razão. O item novo repete as frases dela em vez de dividi-las, e a repetição palavra
por palavra é o que a FR-509 da `035` admite.

#### D-004 — O link do item vai ao cartão

Como o item "Método do sorteio", e pela mesma razão: o campo da ocorrência só existe depois de a
primeira pergunta do cartão responder "por sorteio", e um link para âncora ausente não leva a lugar
nenhum.
