# Contrato — a forma de cada campo do método, e onde ela é conferida

**O que este contrato prende**: que a composição e o motor respondam **a mesma coisa** à pergunta
*"este método roda?"*, e que a tela **ensine** a forma em vez de descobri-la por recusa
(`FR-507`, `FR-508`, `FR-512`, `FR-515`).

---

## A regra do lugar

```
forma de um campo          ──► conferida ao gravar, junto das outras cinco
executabilidade do conjunto ──► já coberta: não há conjunto inexecutável cujos campos sejam válidos
```

**A sexta guarda vai para junto das cinco, e não para uma família nova de achados.** A razão é
verificável: cinco campos irmãos já são conferidos ali, para o método próprio do marco **e** para o
comum do Edital. Pôr o sexto noutro lugar criaria duas gramáticas para o mesmo tipo de erro — e a
pessoa descobriria metade dos problemas ao gravar e a outra metade na Revisão, sem que nada
explicasse a diferença.

## As três obrigações

### 1. Uma regra, duas leituras, a mesma resposta

A conferência da composição MUST aplicar **a regra que o motor aplica**, e não uma cópia dela.

**Por que isto precisa estar escrito**: a regra é pequena — *termina em número* — e reimplementá-la
custa uma linha. Duas linhas que dizem a mesma coisa hoje divergem na primeira vez que uma das duas
mudar, e a divergência aparece do pior jeito: a composição aceitando o que o sorteio recusa, com o
Edital já publicado.

O `SC-177` verifica isso comparando **as duas respostas**, e não lendo as duas implementações.

### 2. O acervo não fica preso

A guarda MUST NOT tornar irretificável nenhum Edital publicado (`FR-514`).

Há conteúdo publicado que **nunca passou por esta conferência**, porque ela não existia. Se o lugar
natural da guarda impedir a Retificação desse conteúdo, **o lugar está errado** — e a saída não é
afrouxar a regra, é conferir onde a regra se aplica.

**Isto é medição, não suposição**: quantos Editais do acervo têm ocorrência fora da forma é um número
a levantar antes de escolher o lugar, e está como tarefa.

### 3. A tela ensina antes de recusar

| Espécie do campo | O que a tela faz | Precedente que ela segue |
|---|---|---|
| vocabulário **fechado** | **oferece a escolha**, montada do próprio vocabulário | a tela de Retificação, com o algoritmo |
| forma **restrita** | **diz a forma, o exemplo e a consequência** | o campo do instante da ocorrência |
| **prosa normativa** | não interfere | — |

**Nenhum dos dois padrões é novo**, e é isso que torna a obrigação barata. Criar uma terceira maneira
de ensinar a mesma coisa é o que `FR-509` proíbe.

---

## O que o contrato **não** manda

- **Não** manda transformar a ocorrência em vocabulário fechado. A referência é do Edital e da fonte.
- **Não** manda tocar a derivação em prosa. Ela é a frase que diz a norma, nenhum caminho de execução
  a lê, e trocá-la por um código removeria do Edital o que o Edital existe para dizer (`FR-510`).
- **Não** manda alargar vocabulário nenhum. Algoritmo e fonte crescem por publicação de código.
