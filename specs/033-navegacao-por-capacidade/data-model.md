# Data Model — 033 · Navegação por capacidade

**Nenhuma migration. Nenhuma capacidade nova. Nenhum campo novo.**

Esta feature não acrescenta nada ao que o sistema sabe sobre quem é quem. Ela muda **de onde a tela
deriva o que oferece** e **como a porta apresenta a recusa**. Uma migration aqui seria sinal de que o
escopo escorregou para "criar papel novo", que `FR-483` proíbe.

O que muda de forma é de duas espécies, e nenhuma é persistência.

---

## 1. A taxonomia da recusa — quatro origens, duas respostas

Hoje as origens se misturam e produzem respostas inconsistentes. **Nas portas desta feature** elas
passam a ser distintas, e a resposta de cada uma passa a ser fixa.

O recorte é medição, e não modéstia: o inventário de `T003` contou **onze** recusas de autorização
em `interface/views.py`, e sete delas ficam fora — pela decisão de governança de 2026-09-18, que
[o inventário](./inventario-das-negativas.md) registra com o porquê. A taxonomia abaixo é a
doutrina; o que ela ainda não tem é alcance universal.

| Origem da negativa | Resposta | Por quê |
|---|---|---|
| **Escopo institucional alheio** | **não encontrado** | O ator não deve sequer saber que aquilo existe. É proteção de dados, e `FR-480` a preserva sem alteração |
| **Objeto inexistente** | **não encontrado** | É a resposta verdadeira |
| **Falta de capacidade nomeada** | **recusa explicada** | A recusa é sobre o ator; escondê-la faria a tela mentir sobre por que não abre |
| **Falta de base de autorização** | **recusa explicada** | Mesma natureza: é sobre o ator, não sobre a existência |

**A quarta origem é a que não tinha tratamento, e ela é composta.** Boa parte das portas não pergunta
por *uma* capacidade: pergunta por uma **base** — a permissão sistêmica de gerir a comissão **ou** a
presidência daquele Processo, cada uma suficiente sozinha. Há ainda porta que aceita essa base **ou**
a capacidade de consultar auditoria.

A camada de segurança sabe recusar **uma capacidade nomeada**. Não sabe recusar um predicado
composto — e é por isso que cada porta que depende de um improvisou o seu próprio "não encontrado".

**O que protege o escopo não é a ordem de avaliação — é o filtro.** Uma versão anterior deste
documento afirmava que o escopo tinha de ser verificado **primeiro**. A medição desmentiu: a porta da
divulgação verifica capacidade antes, devolve recusa explicada sem tocar no banco, e não vaza, porque
quem não tem a capacidade recebe a mesma resposta para tudo.

A invariante real, já uniforme nas seis portas, é que **a consulta que busca o objeto filtra por
escopo institucional** — de modo que objeto de outra unidade e objeto inexistente caiam no mesmo
`is None` e sejam indistinguíveis (`FR-487`). A ordem que vazaria é buscar o objeto **sem** o filtro e
decidir depois; nenhuma porta faz isso hoje.

**E uma porta decide escopo e base na mesma condição** (`FR-488`). Enquanto compartilharem um `if`,
mudar o status responde recusa explicada também para objeto de outra unidade: separar vem primeiro.

**O canal do candidato não entra nesta tabela.** Lá o 404 é **uniforme** de propósito, para que
ninguém descubra pela resposta se a inscrição não existe ou é de outra pessoa. As duas doutrinas
estão certas, cada uma no seu canal.

---

## 2. A recusa explicada — o que ela carrega

A recusa já é apresentada como página, com título, motivo e a declaração de que nada foi alterado.
O que esta feature acrescenta é **conteúdo**, não estrutura.

| Elemento | Hoje | Depois |
|---|---|---|
| Título | "Você não tem permissão para isto" | igual |
| Motivo | "A operação não é permitida." | nomeia **o que falta naquela chamada**: a capacidade nomeada, ou **todas** as bases que teriam servido ali |
| A quem pedir | "peça a quem administra o sistema no Cefor" | nomeia quem resolve **aquele** caso |
| Garantia | "Nenhuma alteração foi feita" | igual |

**A fonte do "o que falta" é uma só, e ela já existe pela metade.** `pode_gerir_comissao` devolve uma
**`Base`** que **nomeia o que autorizou** — a permissão sistêmica ou a presidência. O que falta é o
espelho: nomear o que **faltou** quando ela devolve `None`. Escrever a frase a partir de uma segunda
leitura criaria duas verdades sobre a mesma recusa, que divergiriam na primeira mudança.

---

## 3. O destino — o que a tela do Edital oferece

Hoje cada marco rende **um** destino, escolhido antes de saber quem está olhando. Passa a render os
destinos que **aquele ator** alcança.

| Destino | Quem alcança |
|---|---|
| Ordenação ou sorteio do marco | quem gere a comissão ou preside o Processo; quem consulta auditoria, para ler |
| Corte | os mesmos, e apenas quando o marco declara regra de corte — condição da `032`, **não** alterada aqui |
| Ocupação | os mesmos |
| **Divulgação do ato emitido** | **quem detém a capacidade de publicar resultado** — o destino que hoje não existe na tela |

**Invariantes:**

- ator que alcança mais de um destino vê mais de um, **sem repetir o mesmo destino**;
- ator que não alcança nenhum **não vê o bloco** — e a ausência do bloco não é recusa, é ausência;
- ator que preside **continua vendo tudo o que vê hoje** (`FR-475`): esta feature acrescenta destino,
  nunca retira;
- Edital sem ato emitido não oferece divulgação a ninguém — oferecer caminho que termina em nada é o
  mesmo defeito, com outra roupa.

---

## Entidades que a feature **lê** e não muda

- **Ator** — escopo institucional, capacidades de papel, vínculos de comissão. Os três eixos já
  existem e continuam independentes.
- **Base de autorização** — o que responde "por que este ator pode": a permissão sistêmica **ou** a
  presidência daquele Processo, cada uma suficiente sozinha. Já é um objeto que **nomeia** a base
  quando autoriza; é dele que sai o nome do que faltou quando não autoriza.
- **Marco classificatório e seus atos** — lidos do conteúdo publicado, como hoje.
- **Capacidade** — nenhuma criada, nenhuma alterada, nenhuma redistribuída.
