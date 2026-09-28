# Decisão — a SC-273 da 045 é estreitada, e não as telas alargadas

Tomada pelo usuário em 28/09/2026, sobre o `D4` da revisão da `045`
([anexo 8 da auditoria de consolidação](auditoria-de-consolidacao-2026-09-26/anexo-8-revisao-045.md)),
que a auditoria agrupou no RC-127. A validação desse dia o deixou para decisão
([`validacao-de-unidades-pre-piloto-2026-09-28.md`](validacao-de-unidades-pre-piloto-2026-09-28.md)).
Isto é registro: a spec da `045` não foi editada.

## O que estava em jogo

A `SC-273` diz: *"Para cada sinal com medida, o denominador coincide com o número de linhas da tela
de destino — **zero** divergências —, e **100%** das medidas nomeiam a unidade."* Das três espécies
com medida, só uma cumpre a primeira metade:

| Sinal | Denominador | Tela de destino | Coincide? |
|---|---|---|---|
| `UX-003` cobertura | participantes da Etapa | a distribuição, com o mesmo filtro | sim |
| `UX-063` avaliação parada | inscrições completas | a distribuição inteira — não há filtro para esse conjunto | não |
| `UX-064` recursos | peças que aguardam decisão | a tela de recursos, que lista **todas**, por decisão da própria `FR-734` | não |

A matriz dava a `SC-273` como fechada com testes que só olham o `UX-003`. Havia duas saídas:
alargar as telas de destino, com um filtro de "paradas" na distribuição e um de pendentes na tela
de recursos, ou estreitar o critério. **Foi escolhido estreitar.**

## A decisão

**A exigência de o denominador coincidir com as linhas da tela de destino vale só onde a tela de
destino lista o mesmo conjunto que o sinal mede — hoje, o `UX-003`.** Para o `UX-063` e o `UX-064`,
o destino é o lugar de trabalho, e não a lista da medida. Isso já é assim por decisão escrita no
caso do `UX-064`: a `FR-734` manda a tela de recursos continuar listando todas as peças.

A segunda metade não muda: **100% das medidas nomeiam a unidade.** Desde 28/09 ela é conferida por
teste para as três espécies (RC-127, `D7`), e não só para o `UX-003`.

Uma redação possível para a emenda, a confirmar por quem a aplicar:

> **SC-273**: Para o sinal cuja tela de destino lista o conjunto medido — o `UX-003` —, o
> denominador coincide com o número de linhas dela: **zero** divergências. Nos demais, a tela de
> destino é o lugar do trabalho, e não a lista da medida (`FR-734`). **100%** das medidas nomeiam a
> unidade.

## O que ela não decide

**A `FR-742` pede o mesmo para o `UX-063`, por texto próprio.** Ela diz que, para a cobertura
(`UX-003`) **e** para a avaliação parada (`UX-063`), *"o número e a lista para onde ele leva MUST
contar o mesmo conjunto — mesma população e mesmo filtro"*. Estreitar a `SC-273` não muda essa
frase, e o `UX-063` continua sem cumpri-la. Se a leitura que vale para a `SC-273` vale também para
a `FR-742`, a emenda precisa alcançar as duas. Se não vale, falta o filtro de "paradas" na
distribuição. **Isso fica em aberto**, e é do usuário.

## Consequências

- A emenda da `SC-273`, e da `FR-742` se for o caso, é texto de spec da `045`. Deve entrar com a
  marca de substituição datada, no formato das que a `022` recebeu em 28/09, e com a linha da
  `SC-273` na `rastreabilidade.md` da `045` passando a dizer que cobre o `UX-003`.
- Nenhuma tela muda. A distribuição continua sem filtro de "paradas", e a tela de recursos
  continua listando todas as peças.
