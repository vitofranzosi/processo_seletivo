# Feature Specification: A tela do sorteio como a jornada de quem o conduz

**Feature Branch**: `claude/142-jornada-do-sorteio-d8b95f`, sobre a `main` em `daba322f`

**Created**: 2026-11-10

**Status**: Implementada e mergeada (#452). *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Draft

**Nenhuma regra de domínio nova.** Esta spec reorganiza a tela operacional do sorteio. Não há
migration, tabela, coluna, permissão, estado persistido, nem mudança no que um comando aceita ou
recusa. O que cada passo diz de si vem da derivação do andamento da `127`, a mesma que o Centro de
Controle da `136` mostra; os controles aparecem exatamente nas condições de hoje.

**Input**: *"G4: evolução de UI/UX da jornada operacional do sorteio. A tela passa a mostrar o
sorteio como uma sequência pedagógica — 1. Fixar os participantes, 2. Obter a semente pública,
3. Realizar o sorteio, 4. Consultar o resultado —, com as seções nessa ordem: relações e preparação
das listas; semente e ocorrência pública; execução; resultado e encaminhamentos. A sequência não é
máquina de estados: disponibilidade, conclusão e impedimentos vêm das regras existentes. O método sai
do primeiro plano. Várias listas ficam claras, sem misturar a semente do marco com o estado de cada
relação. O resultado mostra a ordem sorteada e diferencia relação, ordem, classificação, corte e
publicação. Avaliar a conferência antes do congelamento. A observação da semente não ganha bloqueio
novo nem confirmação (decisão do usuário de 10/11). O Centro continua coerente."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil e novecentos a quatro mil novecentos e quarenta e nove;
> - os critérios de mil quinhentos e quarenta a mil quinhentos e cinquenta e nove;
> - as regras de experiência de trezentos e cinquenta a trezentos e sessenta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto medido em 10/11/2026 era o da `138` (PR #451, aberto): requisito quatro mil oitocentos e
> setenta e seis, critério mil quinhentos e vinte e seis, regra de experiência trezentos e quarenta e
> seis. A `143`, escrita em paralelo noutra sessão, usa outra faixa; a reserva está nas notas
> compartilhadas das sessões.
>
> **Como esta spec cita outras.** Requisito de outra feature: pelo identificador e pela feature ("a
> FR-2659 da `102`"). Decisão de outra feature ou do estudo: pelo assunto ("a decisão sobre a
> observação da semente, a quinta do estudo de continuidade").
>
> **Origem.** O
> [estudo de continuidade operacional de 10/11/2026](../../doc/estudo-continuidade-operacional-2026-11-10/README.md):
> a jornada A do mapa, as melhorias M-03, M-06, M-12 e M-13 do inventário, o protótipo
> `sorteio-c06-*` e a triagem F-1 a F-3 (`07-triagem-f1-f3.md`), cuja seção 4 registra a decisão do
> usuário sobre a observação da semente.

## Por que esta feature existe

A `139` levou quem conduz até o lugar do ato. A tela em que ele chega continuava organizada pela
estrutura técnica do método, e não pela sequência do trabalho. No C06 dos cenários de treinamento
da `134`, aberta pelo topo a 1440 × 900:

1. **A primeira coisa era o método**: algoritmo, derivação, normalização e resumo criptográfico, sete
   linhas de configuração que quem conduz não decide e não pode mudar.
2. **A semente vinha antes das listas.** "Observar a ocorrência" estava a 887 px; "Publicar e
   congelar a relação", o passo que precisa vir antes, a 1.681 px, abaixo dele.
3. **O corte aparecia antes do sorteio**: "Nenhum corte emitido neste recorte" encabeçava cada lista
   que ainda nem tinha participantes fixados.
4. **Os nomes eram os do GPS** — relação, ocorrência, recorte —, sem a tarefa que eles cumprem.
5. **A ordem sorteada não aparecia.** Depois do sorteio, a tela dizia a semente e o manifesto, e a
   ordem só existia na página pública de verificação.
6. **Nada dizia como as operações se relacionam**: que a semente é uma só para todas as listas, que o
   sorteio é por lista, que a ordem ainda não é a classificação divulgada.

O Centro de Controle (`136`) já fala a língua de quem conduz e já sabe a situação de cada passo em
cada lista. A tela do ato era a única peça da jornada que ainda não sabia.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entender a sequência e achar a tarefa de agora (Priority: P1)

Quem conduz abre a tela do sorteio de um marco e vê, antes de qualquer detalhe técnico, os quatro
passos do sorteio, na ordem: fixar os participantes, obter a semente pública, realizar o sorteio,
consultar a ordem sorteada. Cada passo diz em poucas palavras o que se faz e por quê, e mostra a
situação dele — por lista, ou pelo marco, no caso da semente. O passo em que há algo a fazer agora
se distingue dos outros, e os posteriores não ganham destaque sobre ele.

**Why this priority**: é o defeito central do estudo; sem isso, as outras histórias são detalhe.

**Independent Test**: no C06 recém-carregado, abrir a tela como a presidência e conferir que os
quatro passos aparecem na ordem, que o primeiro está marcado como a tarefa de agora, e que o botão de
fixar vem antes do de obter a semente, na página e na ordem do teclado.

**Acceptance Scenarios**:

1. **Given** um marco com duas listas e nada fixado, **When** quem conduz abre a tela, **Then** vê os
   quatro passos; o primeiro diz "0 de 2 listas fixadas" e é a tarefa de agora; a semente diz que
   espera a primeira lista fixada; sortear e consultar dizem que dependem dos anteriores.
2. **Given** a ampla fixada e a PPP não, **When** a tela abre, **Then** o primeiro passo diz "1 de 2",
   com a situação de cada lista, e continua a tarefa de agora; obter a semente aparece disponível,
   sem destaque e sem bloqueio novo.
3. **Given** as duas listas fixadas e a semente não obtida, **When** a tela abre, **Then** o primeiro
   passo está concluído e o segundo é a tarefa de agora.

---

### User Story 2 - Fixar os participantes sabendo o que se fixa (Priority: P1)

Antes de fixar uma lista, quem conduz vê, no próprio cartão dela, a conferência do ato: que lista,
quantas pessoas, com que número cada uma, que o ato não muda mais e como se corrige, e o que vem
depois. Sem clique a mais.

**Why this priority**: fixar é o primeiro ato irreversível da jornada, e o que mais se faz.

**Independent Test**: no C06, ler o cartão da ampla antes de fixar: a lista, os 10 participantes com
número, a frase do irreversível e o passo seguinte, antes do botão; fixar, e ver o cartão passar a
"fixada", com a tabela recolhida e o resumo.

**Acceptance Scenarios**:

1. **Given** uma lista com participantes e nada fixado, **When** quem conduz lê o cartão, **Then** vê,
   antes do botão, a lista, quantas pessoas participam, a numeração, a consequência e o passo
   seguinte.
2. **Given** a lista fixada, **When** a tela volta do ato, **Then** a mensagem de sucesso e o "Próximo
   nesta lista" da `127` continuam no alto, e o cartão diz quando e por quem foi fixada.
3. **Given** uma lista em que ninguém se inscreveu, **When** a tela abre, **Then** o cartão diz que não
   se aplica e por quê, sem botão.

---

### User Story 3 - Várias listas, uma semente (Priority: P1)

Num marco com ampla e cota, quem conduz vê quantas listas participam, quais estão fixadas, quais
sorteadas, quais esperam e quais estão impedidas — e vê a semente como uma coisa só, do marco, que
vale para todas.

**Why this priority**: é onde o esforço vira erro: publicar duas listas e esquecer a terceira, ou
sortear uma achando que sorteou todas.

**Independent Test**: no C06, depois de sortear a ampla e antes de sortear a PPP: o passo 3 diz
"1 de 2 listas sorteadas", a ampla como feita e a PPP como a fazer, com o botão só na PPP; o passo 2
diz a semente uma vez, sem repeti-la por lista.

**Acceptance Scenarios**:

1. **Given** uma lista sorteada e outra não, **When** a tela abre, **Then** cada passo mostra a
   situação de cada lista, e o botão de sortear aparece só na lista que ainda não foi sorteada.
2. **Given** a semente obtida, **When** a tela abre, **Then** a semente aparece uma vez, no passo 2,
   dizendo que vale para as listas do marco.

---

### User Story 4 - Entender o resultado sem confundir com a divulgação (Priority: P2)

Depois do sorteio, quem conduz vê a ordem sorteada de cada lista — posição, número na relação, nome
e protocolo —, com o acesso à verificação pública, e lê o que a ordem é e o que ainda não é: ela é
o ato gravado; a classificação divulgada é outro ato, de quem publica resultado; o corte é outro.

**Why this priority**: a ordem era invisível na tela, e o passo seguinte dependia de saber que ela
ainda não estava divulgada.

**Independent Test**: no C06 depois dos dois sorteios: o passo 4 mostra as duas ordens, com 10 e 3
posições; diz que nenhuma foi divulgada como resultado; o corte não aparece antes de haver sorteio.

**Acceptance Scenarios**:

1. **Given** uma lista sorteada e nenhum resultado publicado, **When** a tela abre, **Then** o passo 4
   mostra a ordem e diz que ela ainda não foi divulgada como resultado.
2. **Given** a lista que acabou de ser sorteada, **When** a tela volta do ato, **Then** a ordem dela
   aparece aberta.
3. **Given** uma lista ainda não sorteada, **When** a tela abre, **Then** o passo 4 não mostra corte
   nem a frase "Nenhum corte emitido".

---

### User Story 5 - Quem não conduz entende sem poder agir (Priority: P3)

A auditoria e quem só lê a tela veem os mesmos passos e situações, sem nenhum controle, e sabem a
quem pedir o ato.

**Independent Test**: abrir a tela com o papel de Auditor: os quatro passos e as situações; nenhum
formulário de ato; a frase de quem conduz.

**Acceptance Scenarios**:

1. **Given** uma pessoa sem a condução do sorteio, **When** abre a tela, **Then** vê os passos sem
   destaque de "tarefa de agora" e sem botão, e a frase que diz quem conduz.

---

### Edge Cases

- **A semente obtida antes de fixar a última lista** (o F-1 do estudo, na fonte de treinamento que
  publica a hora): a tela continua deixando observar, como hoje — a decisão do usuário é não pôr
  regra, bloqueio nem confirmação na observação. Fixada a lista depois, o sorteio dela é recusado
  pelo serviço, e a tela mostra a recusa como hoje. A correção do diagnóstico da `102` para essa
  fonte está anotada no estudo como "a considerar", e não entra aqui.
- **A relação que nunca sorteará** (FR-2660 da `102`): o diagnóstico fica no cartão da lista, no
  passo 1, onde está a saída (suceder a relação); o passo 3 diz a razão do impedimento e aponta o
  cartão.
- **Inscrições em curso**: o passo 1 diz que aguarda o fim do período, com a frase da recusa, sem
  botão.
- **A lista à espera da Etapa de habilitação**: o passo 1 diz *Depois* com a razão.
- **O marco sem método declarado**: a frase de hoje, fora de qualquer área recolhida, no alto dos
  passos — ela impede tudo.
- **A ocorrência indisponível ou a declaração ilegível**: as frases de hoje, no passo 2.
- **O sorteio obsoleto ou anulável**: a anulação continua no passo 3, recolhida, com os mesmos
  insumos e a mesma ordem de passos de hoje.
- **A derivação indisponível** (o andamento devolve nada, como antes da publicação ou numa falha que
  ele registra no log): os passos aparecem sem situação, e os controles continuam os de hoje.
- **Os registros fora da operação atual** (`122`): continuam no fim, sem botão.
- **Uma lista com centenas de participantes**: as tabelas das listas fixadas e das ordens ficam
  recolhidas, e a tela não cresce além do que já crescia.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-4900**: A tela do sorteio MUST apresentar quatro passos, nesta ordem: "Fixar os
  participantes", "Obter a semente pública", "Realizar o sorteio" e "Consultar a ordem sorteada".
  Os três primeiros MUST usar o nome simples, o nome no GPS e a frase curta que o Centro já usa,
  lidos da mesma fonte, e não uma cópia.
- **FR-4901**: Cada passo MUST dizer, em poucas palavras, o que se faz e por quê, o que precisa estar
  pronto, que listas afeta, o que acontece depois e se o ato é irreversível. O aprofundamento MAY
  ficar recolhido.
- **FR-4902**: A situação de cada passo MUST vir da derivação do andamento da `127` para o Perfil do
  marco — por lista nos passos 1, 3 e 4, e do marco no passo 2 —, com a palavra e o sinal daquela
  derivação. A tela MUST NOT calcular situação por regra própria.
- **FR-4903**: Os formulários de ato MUST aparecer exatamente nas condições de hoje — fixar,
  observar, sortear, suceder a relação e anular —, com os mesmos destinos e campos. Nenhum controle
  MAY ser acrescentado, removido ou habilitado pela reorganização.
- **FR-4904**: As seções MUST seguir a ordem dos passos: as listas e a preparação delas; a semente e
  a ocorrência pública; a execução; o resultado e os encaminhamentos. O Edital, o Perfil, o marco e
  as listas do marco MUST estar visíveis no alto da tela.
- **FR-4905**: Os passos 1, 3 e 4 MUST dizer quantas listas participam e quantas estão em cada
  situação, e MUST mostrar a situação de cada lista pelo nome dela.
- **FR-4906**: A semente MUST aparecer uma vez, no passo 2, como do marco, dizendo que vale para as
  listas dele; MUST NOT aparecer como estado de uma lista.
- **FR-4907**: O método declarado MUST continuar inteiro na tela, recolhido no passo 2, com o
  "Conferir na Caixa" da `116` e o caminho da Retificação. A falta de método MUST continuar dita fora
  de qualquer área recolhida.
- **FR-4908**: Antes do botão de fixar, o cartão da lista MUST mostrar a conferência do ato: a lista,
  quantas pessoas participam, a numeração de cada uma, que o ato não muda mais e como se corrige, e o
  passo seguinte. A conferência MUST NOT exigir clique a mais nem gravar coisa alguma.
- **FR-4909**: A observação da semente MUST continuar com a regra, a disponibilidade e o texto de
  hoje: sem bloqueio, sem confirmação e sem frase nova sobre a ordem entre fixar e observar.
- **FR-4910**: O passo que tem algo a praticar por quem conduz, o primeiro na ordem, MUST ser
  marcado como a tarefa de agora. Os demais MUST NOT ter destaque maior que o dele; um botão de
  passo posterior disponível ao mesmo tempo MUST aparecer como ação secundária.
- **FR-4911**: O passo 3 MUST mostrar, por lista, o botão de sortear quando ele existe hoje, ou a
  razão da derivação quando não existe, e a anulação recolhida da lista já sorteada.
- **FR-4912**: O passo 4 MUST mostrar, por lista sorteada, a ordem que o ato gravou — posição, número
  na relação, nome e protocolo —, o acesso à verificação pública e, a quem publica resultado, o
  caminho de publicar a classificação.
- **FR-4913**: O passo 4 MUST distinguir a relação de participantes, a ordem do sorteio, a
  classificação divulgada e o corte, e MUST dizer se a lista tem resultado divulgado pela leitura da
  derivação. Sem divulgação, MUST NOT haver frase que a sugira.
- **FR-4914**: O estado do corte MUST aparecer só no passo 4, e só na lista que já tem sorteio ou
  corte.
- **FR-4915**: Os destinos da `139` MUST continuar: o id de cada lista no passo 1 e as seções das
  listas e da semente. A execução de cada lista MUST ter destino próprio, e a providência do sorteio
  MUST levar a ele.
- **FR-4916**: A mensagem de cada ato, o "Próximo nesta lista" e a volta ao Centro MUST continuar no
  alto da tela, logo depois do título, como hoje.
- **FR-4917**: Quem não conduz o sorteio MUST ver os passos e as situações, sem controle de ato e sem
  a marca de tarefa de agora, e a frase de quem conduz.
- **FR-4918**: Sem derivação, os passos MUST aparecer sem situação, e a tela MUST continuar
  operando como hoje.

### Experience Rules

- **UX-350**: A situação MUST ser dita por palavra e sinal; a cor acompanha e nunca é a única pista.
- **UX-351**: Os passos MUST ser uma lista ordenada, com título, e cada passo um link para a sua
  seção; a ordem do teclado MUST seguir a dos passos.
- **UX-352**: A 375 px a tela MUST NOT ter rolagem horizontal, e nenhum estilo ou script MAY estar
  escrito no template.

### Key Entities

Nenhuma entidade nova. A tela lê a relação de cada lista, a ocorrência do marco, o sorteio de cada
lista e as posições do ato de ordenação que ele constituiu — todos já existentes —, e a derivação do
andamento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1540**: No C06 recém-carregado, aberto pelo topo a 1440 × 900, o primeiro botão de fixar
  aparece acima do de obter a semente, e antes dele na ordem do teclado.
- **SC-1541**: Nos cenários da validação, a situação de cada passo em cada lista é a mesma que o
  Centro mostra para aquela lista.
- **SC-1542**: Em cada estado capturado antes e depois, o conjunto de formulários de ato da tela —
  destino e lista — é o mesmo.
- **SC-1543**: Depois de sortear uma lista de N participantes, o passo 4 mostra N posições, na ordem
  do ato.
- **SC-1544**: Sem resultado divulgado, a tela não contém frase que diga que a ordem foi publicada ou
  divulgada.
- **SC-1545**: Em todos os estados capturados, a 375 px, a página não tem rolagem horizontal, e o
  console não registra violação de política de conteúdo.
- **SC-1546**: Antes de haver sorteio numa lista, a tela não diz "Nenhum corte emitido" para ela.

## Decisões

### D-001 — A situação vem do andamento, lido para o Perfil do marco

A tela lê o andamento da `127` com o Perfil do marco, e procura as células do marco. É o que o Centro
mostra, por construção. Custa uma derivação do Perfil a cada abertura — o "Próximo nesta lista" já a
pagava depois de cada ato, e passa a reaproveitar a mesma leitura. A alternativa, calcular a situação
dos fatos que a tela já tem, seria a segunda regra que diverge na primeira mudança — a lição da `103`
e da `104`, que a `127` registra.

### D-002 — A execução ganha destino próprio

A `139` fazia a providência do sorteio levar ao cartão da lista, que tinha relação, botão de sortear e
anulação juntos. Com a semente entre as listas e a execução, o cartão da lista fica no passo 1, e o
sorteio, no passo 3. A célula do sorteio passa a levar ao destino da execução daquela lista; a da
relação continua no cartão. As duas listas juntadas numa providência levam à seção da execução.

### D-003 — O resumo de um passo é o da lista mais urgente, e as listas aparecem sempre

Um passo de várias listas mostra a contagem ("1 de 2 listas fixadas") e a situação de cada lista. O
sinal do passo é o da lista que mais pede atenção — o que se pratica, depois o impedido, o que
aguarda, o que vem depois, o feito, o que não se aplica. É ordem de apresentação, e não estado: não
se grava, não decide nada, e a lista de cada situação está ao lado.

### D-004 — A observação continua como está; só a ênfase do botão acompanha o passo

A decisão do usuário de 10/11 (a quinta do estudo, alternativa "não decidir agora") manteve a
observação sem regra nova. A tela não acrescenta bloqueio, confirmação ou frase. O que muda é
apresentação: enquanto o passo 1 tem lista a fixar, o botão de observar aparece como ação secundária,
porque a tarefa de agora é a do passo 1 (FR-4910). Continua clicável, no mesmo formulário. A frase
"uma lista fixada depois da semente não sorteia" era a alternativa de alertar, e não foi adotada.

### D-005 — A conferência do congelamento fica no cartão, sem passo a mais

A `140` pôs uma conferência em dois passos antes de convocar, com resumo do texto conferido. Para
fixar, a tela do sorteio **já é** a prévia sem efeito: a tabela do cartão é a lista e a numeração que
o ato grava, e ela está à vista antes do botão. O que faltava era dizer, ali, a consequência e o passo
seguinte — e é o que o bloco de conferência faz. A conferência em dois passos, com a garantia de que o
universo conferido é o gravado, pediria rota, resumo e recusa novos; fica registrada como achado, para
decisão (ver o plano).

### D-006 — A ordem mostrada é a gravada, depois do ato

A tela continua sem prévia da ordem (a regra do ensaio da `021`). O passo 4 lê as posições do ato de
ordenação que o sorteio constituiu — o mesmo que a verificação pública reproduz. Fica recolhida por
lista; abre sozinha na lista que acabou de ser sorteada.

### D-007 — A tabela da lista fixada fica recolhida

Antes de fixar, a tabela é a conferência e fica aberta. Depois, ela é o registro do compromisso, e
continua a um clique, com o resumo e o link público ao lado. Com três listas e centenas de pessoas,
deixá-la aberta empurrava a semente e a execução para longe.
