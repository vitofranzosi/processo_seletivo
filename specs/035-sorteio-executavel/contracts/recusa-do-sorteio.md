# Contrato — a recusa no dia do sorteio

**O que este contrato prende**: que a tela distinga **a fonte não publicou** de **a declaração não
pôde ser lida**, e que na segunda diga o que corrigir (`FR-516`, `FR-517`, `FR-518`).

---

## As duas causas, que hoje são uma

Hoje as duas caem no mesmo tratamento de erro, e a tela diz a mesma frase para as duas:

> *"A ocorrência declarada e todas as substitutas previstas pela regra publicada estão
> indisponíveis. Prosseguir exige Retificação que declare outro método…"*

| Causa | O que aconteceu | A frase de hoje |
|---|---|---|
| **A cadeia esgotou** | a fonte esteve indisponível tantas vezes quanto a regra encadeia | ✅ **verdadeira** |
| **A regra não soube derivar** | a referência declarada não tem a forma que a regra consome | ❌ **falsa**, e culpa quem não errou |

**A frase certa já existe.** A regra de substituição levanta a segunda causa com uma mensagem
específica e correta — que ela deriva do número da ocorrência, e que aquela referência não termina em
número — e essa mensagem é **descartada** a uma linha de onde seria exibida.

O trabalho não é escrever a frase. É **parar de jogá-la fora**.

## As três obrigações

1. **A tela MUST distinguir as duas.** Atribuir à fonte externa uma falha da declaração manda a
   pessoa esperar por algo que não vai acontecer, e depois Retificar sem saber o quê.
2. **Quando a causa é a declaração**, a frase MUST dizer **qual campo** e **o que ele precisa
   conter** — e só então que corrigir exige Retificação, porque o Edital está publicado. A ordem
   importa: quem lê precisa saber **o que** antes de saber **como**.
3. **Quando a causa é indisponibilidade real**, a frase MUST continuar a de hoje. Ela está certa, e
   esta feature não mexe no que está certo.

## O que a distinção custa, e por que vale

Depois da `US1` e da `US2`, **quase nenhum Edital novo chega aqui**: a forma é ensinada e conferida
na composição.

Esta história é para o **acervo** — o Edital que já foi publicado com a ocorrência em prosa, e cuja
única saída é a Retificação. É a única das três que ajuda quem já publicou, e é por isso que ela
existe mesmo sendo a de menor alcance.
