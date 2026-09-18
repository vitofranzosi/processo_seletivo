# Data Model — 033 · Navegação por capacidade

**Nenhuma migration. Nenhuma capacidade nova. Nenhum campo novo.**

Esta feature não acrescenta nada ao que o sistema sabe sobre quem é quem. Ela muda **de onde a tela
deriva o que oferece** e **como a porta apresenta a recusa**. Uma migration aqui seria sinal de que o
escopo escorregou para "criar papel novo", que `FR-483` proíbe.

O que muda de forma é de duas espécies, e nenhuma é persistência.

---

## 1. A taxonomia da recusa — três origens, duas respostas

Hoje as três origens se misturam e produzem respostas inconsistentes. Passam a ser distintas e a
resposta de cada uma passa a ser fixa.

| Origem da negativa | Resposta | Por quê |
|---|---|---|
| **Escopo institucional alheio** | **não encontrado** | O ator não deve sequer saber que aquilo existe. É proteção de dados, e `FR-480` a preserva sem alteração |
| **Objeto inexistente** | **não encontrado** | É a resposta verdadeira |
| **Falta de capacidade** | **recusa explicada** | A recusa é sobre o ator; escondê-la faria a tela mentir sobre por que não abre |
| **Falta de vínculo de comissão** | **recusa explicada** | Mesma natureza da anterior: é sobre o ator, não sobre a existência |

**A ordem de avaliação é normativa, e não detalhe.** O escopo é verificado **primeiro**; só depois
capacidade e vínculo. Inverter faria a recusa de escopo virar recusa explicada e vazar a existência
de Editais de outras unidades — o modo de falha que `FR-480` existe para impedir.

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
| Motivo | "A operação não é permitida." | nomeia **o que falta**: a capacidade, ou o vínculo de presidência daquele Processo |
| A quem pedir | "peça a quem administra o sistema no Cefor" | nomeia quem resolve **aquele** caso |
| Garantia | "Nenhuma alteração foi feita" | igual |

**A fonte do "o que falta" é uma só**: a base de autorização que a porta consultou. Escrever a frase
a partir de outra leitura criaria duas verdades sobre a mesma recusa, que divergiriam na primeira
mudança.

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
- **Base de autorização** — o que responde "por que este ator pode": a permissão sistêmica ou a
  presidência daquele Processo. É ela que sabe nomear o que falta.
- **Marco classificatório e seus atos** — lidos do conteúdo publicado, como hoje.
- **Capacidade** — nenhuma criada, nenhuma alterada, nenhuma redistribuída.
