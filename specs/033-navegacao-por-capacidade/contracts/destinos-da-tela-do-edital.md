# Contrato — os destinos da tela do Edital

O bloco de marcos classificatórios da tela do Edital passa a ser derivado **por destino**, e não por
uma porta escolhida de antemão.

## A regra que governa tudo abaixo

**Um destino aparece se, e só se, o ator o alcança.** É o princípio que o próprio código já declara
— *oferecer o que se vai recusar é pior do que não oferecer* —, aplicado a cada destino em vez de à
lista inteira.

E o recíproco, que é o achado: **um destino que o ator alcança não pode deixar de aparecer.** Era o
que acontecia com a divulgação.

---

## A matriz

| Destino | Quem alcança | Estado |
|---|---|---|
| Ordenação do marco | gere a comissão, ou preside o Processo | como hoje |
| Sorteio do marco | idem, quando o marco ordena por sorteio | como hoje |
| Corte | idem, **e** apenas quando o marco declara regra de corte | como hoje — condição da `032`, não alterada aqui |
| Ocupação | idem | como hoje |
| Leitura por auditoria | detém a capacidade de consultar auditoria | como hoje |
| **Divulgação do ato emitido** | **detém a capacidade de publicar resultado** | **novo** |

---

## Os casos que a matriz produz

| Ator | O que vê |
|---|---|
| Presidência sem capacidade de publicar | ordenação/sorteio, corte quando houver, ocupação. **O mesmo de hoje** |
| Publicador puro, sem vínculo | **a divulgação de cada ato emitido**, e nada além |
| Preside **e** publica | a união dos dois, **sem repetir destino** |
| Auditoria | o que lê hoje, para leitura |
| Nenhuma das coisas | **o bloco não aparece** |
| Julga recursos | o bloco não aparece — é o caso que o código já corrigiu, e que esta feature não pode regredir |

---

## Duas ausências que **não** são recusa

| Situação | O que a tela faz |
|---|---|
| Edital ainda não publicado | não há marcos publicados; o bloco não existe para ninguém |
| Marco sem ato emitido | não há o que divulgar; o destino de divulgação **não** aparece para o Publicador |

O segundo é o mesmo princípio de novo: oferecer um caminho que termina em nada é oferecer o que se
vai recusar, com outra roupa.

---

## O texto que instrui, e para quem ele vale

A tela de ordenação diz hoje, três vezes, que a divulgação *"sai de lá — em Consultar ato e
proveniência, acima"*. Quem lê aquela tela é a presidência, que é justamente quem **não** publica na
configuração segregada.

O contrato: **texto que manda o operador a outra tela vale para quem alcança aquela tela.** Onde o
leitor pode não alcançar, o texto diz de quem é o ato — e não apenas onde ele mora.

---

## O que este contrato **não** toca

- **A condição do corte.** O link do corte continua governado pela regra de corte declarada. É
  escopo da `032`, e mexer nele aqui criaria duas features editando a mesma condição.
- **O conteúdo das telas de destino.** UUID e vocabulário de máquina nas telas de ato são
  `ACH-39`/`ACH-31`/`ACH-45`, com spec própria. Aqui muda **quem chega**, não o que se lê ao chegar.
- **A autorização de cada destino.** Cada tela continua verificando o que já verifica. A matriz
  acima descreve o que a navegação **oferece**; ela não concede nada.
