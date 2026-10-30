# Roteiro de compreensão com quem conduz o certame: a saída da extração inviável

**Para quê**: verificar a SC-958 com pessoas. Os testes provam que a recusa e o diagnóstico trazem a
frase certa; não provam que quem os lê sabe o que fazer. O operador do Edital 72/2026 leu a recusa de
29/10 e foi investigar um horário que a Caixa nunca publicou. A pergunta aqui é se, com o texto novo,
a pessoa chega sozinha aos dois atos da saída e à ordem entre eles. **Só pessoas cumprem este
roteiro**, e a aplicação é do usuário. A T023 entrega o roteiro e a folha; o relato fecha a SC-958.

## Quem

Pessoas que presidem ou secretariam comissão de sorteio, ou que já conduziram a transmissão de um.
Cinco é o mínimo da SC-958. Ninguém que tenha lido a spec ou o achado.

## O ambiente

O banco de demonstração da `102`, preparado pelo cenário 2 do [quickstart](quickstart.md): um Edital
com a `Fonte de demonstração (só a data)`, as inscrições encerradas, a extração retificada para hoje e
a relação congelada. Há duas telas a mostrar:

- **A.** A recusa de "Realizar o sorteio", que aparece no topo da tela do sorteio depois do clique
  (seção 5 de [contracts/mensagens.md](contracts/mensagens.md)).
- **B.** O diagnóstico da relação congelada, antes do botão de sortear (seção 4 do mesmo contrato).

Prepare as duas antes de cada pessoa. A tela A se reproduz clicando de novo: a recusa não grava nada.

## As rodadas

Uma pessoa de cada vez, sem explicação prévia além de: *"Você conduz o sorteio deste Edital e está
nesta tela."*

1. **Mostre só a tela A**, com o restante da página rolado para fora da vista. Pergunte: **"O que
   aconteceu, e o que você faz agora?"**
2. **Mostre só a tela B.** Pergunte: **"Esta relação vai poder ser sorteada? Se não, o que precisa
   acontecer, e em que ordem?"**
3. Em seguida, sem mostrar nada: **"Publicar uma relação nova resolveria?"**

## O gabarito

- Na rodada 1 ou na 2, a pessoa diz que é preciso **retificar o método** (declarar uma extração de
  dia posterior) **e depois publicar relação nova, sucedendo a atual**. A ordem conta: retificar
  primeiro.
- Na rodada 3: **não, sozinha não**. A relação nova seria congelada ainda mais tarde, diante da mesma
  extração.
- Acerto parcial, que se registra como erro: dizer só "retificar", só "publicar relação nova", ou os
  dois na ordem inversa.
- Sinal de que a granularidade não chegou, que se registra à parte: a pessoa diz que a fonte
  "informou" um horário.

## Como registrar

| Pessoa | Rodada 1 (frase dita) | Rodada 2 (frase dita) | Rodada 3 | Retificar → suceder, na ordem? | Falou de horário da fonte? | Onde olhou |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

A SC-958 pede ao menos 4 de cada 5 dizendo os dois atos na ordem, sem ajuda. Uma pergunta que ninguém
acerta é achado de tela, e não de pessoa: registre a frase que a pessoa leu em voz alta, e onde ela
parou de ler.
