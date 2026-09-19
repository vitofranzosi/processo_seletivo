# Varredura da amostra real — como cada Edital declara a ocorrência que fixa a semente

**Tarefa `T028`, critério `SC-180`.** Leitura por extração de texto (`pdftotext -layout`) dos
Editais de sorteio da amostra de
[doc/avaliacao-de-capacidade-editais-2026-09-12.md](../../doc/avaliacao-de-capacidade-editais-2026-09-12.md),
em 18/09/2026.

**O critério mudou de pergunta antes desta varredura**, e a razão está no `research.md` `R-7`: a
primeira redação contava *quantos Editais seriam impedidos* pela guarda nova, e a leitura de quatro
deles mostrou que a contagem devolveria zero **por ausência de declaração**, e não por declaração
correta. O que a varredura precisa produzir é **o que a ajuda da `FR-508` tem de ensinar a quem
parte de um Edital real**.

## O que foi lido

O `R-7` lera **quatro**. Esta varredura cobre **dez** — toda a amostra que sorteia, incluindo os
dois anteriores a 2026 —, e mais dois que **não** sorteiam, como contraprova de que a busca acha o
que existe.

| Edital | Cláusula do sorteio | Declara ocorrência de fonte externa? | O que publica no lugar |
|---|---|---|---|
| **57/2026** aperfeiçoamento, unificado | 8.2 | **não** | *"Semente utilizada: xxxxxxxxxxxxx", ao fim da página do sorteio* |
| **58/2026** FIC, unificado | 6.2 | **não** | idem, palavra por palavra |
| **59/2026** Libras A1 | 6.2 | **não** | idem |
| **69/2026** Multimeios Didáticos | 4.2 | **não** | idem |
| **76/2026** Secretaria Escolar | 5.2 | **não** | idem |
| **77/2026** FIC Acessibilização | 6.2 | **não** | idem |
| **78/2026** Libras A1, remanescentes | 6.2 | **não** | idem |
| **28/2026** pós-graduação Informática na Educação | 8.2 | **não** | idem |
| **158/2024** FIC Educação Especial | 6.2 | **não** | idem |
| **125/2024** FIC, unificado | 6.2 | **não** | idem |
| 14/2026 orientador de TFC | — | — | **não sorteia** — nenhuma ocorrência de "sorteio" no texto |
| 46/2026 técnicos integrados | — | — | **não sorteia**, e está fora do alvo do produto por decisão |

**Dez de dez.** A cláusula é a mesma nos dez, e a redação não mudou em dois anos:

> *"O Software usado pelo Cefor já é utilizado por outros institutos federais. Este programa
> sorteia aleatoriamente a ordem dos números através de algoritmos e cálculos matemáticos. Para
> fins de auditoria, observar o campo 'Semente utilizada: xxxxxxxxxxxxx', localizado ao fim da
> página do sorteio. Ela é que garante a aleatoriedade do processo."*

E a busca por **Loteria Federal**, **Caixa Econômica**, **concurso ⟨número⟩** e **extração de** nos
dez devolve **zero** em todos. Não há fonte pública externa citada em nenhum ponto de nenhum deles.

## O que isso confirma, e o que muda

**Confirma o `R-7`, e o estende de quatro para dez** — inclusive para os dois de 2024, que são a
mesma família textual dois anos antes. O modelo real do Cefor é: *o software gera a semente e a
publica depois*.

**O modelo deste sistema é deliberadamente mais forte**, e a `021` o escolheu por escrito: semente
derivada de fonte pública externa, **declarada antes** e verificável por terceiro. Uma semente
publicada **depois** não prova nada a quem não estava lá — ela é exatamente o que um software mal
intencionado publicaria. É essa diferença que entrega a auditabilidade que os dez Editais prometem
e não cumprem.

## O que alguém teria de escrever no campo, ao compor a partir de cada um

**Nada do texto de origem serve.** Em nenhum dos dez existe frase que possa ser copiada para o
campo da ocorrência: a referência que o sistema pede simplesmente não está lá.

Quem compõe a partir de qualquer um deles precisa **escolher uma extração de fonte pública** e
declará-la — por exemplo, o concurso da Loteria Federal imediatamente anterior à data do sorteio
publicada no cronograma —, escrevendo no campo **só o número**: `6100`, ou `Concurso 6100`.

E aqui está o achado que mais importa para a ajuda da `FR-508`. **A forma natural de escrever é a
que não roda.** Quem tem o Edital real na mão escreveria `concurso 6100 da Loteria Federal` — que é
como uma pessoa escreve, e é literalmente a forma das três fixtures que este próprio projeto tinha
— porque o texto de origem não separa a fonte da referência, e repetir a fonte no fim parece
completar a frase. A fonte já é um campo à parte; repeti-la depois do número põe o número no meio,
onde a regra de substituição não o procura.

É por isso que a ajuda diz **três** coisas, e não duas: a forma, o exemplo, e que ali vai **só a
referência** porque a fonte está declarada acima.

## A pergunta de governança que esta varredura confirma e **não** responde

O sistema exige uma declaração que **nenhum** Edital corrente do Cefor faz. Ou eles passam a
fazê-la — e é ganho de auditabilidade, a ser combinado com quem os redige —, ou existe uma família
de sorteio que o modelo atual não representa: a do software que semeia a si mesmo e publica a
semente depois.

**Esta feature não decide, e não deve.** Ela ensina a declarar o que o modelo pede. A decisão é de
quem governa o backlog, e está registrada na `spec.md`, em *Uma pergunta de governança que esta
feature registra e não responde*.
