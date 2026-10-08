# Achado — a Matrículas põe `.resumo` numa `section`, como a Ocupação punha

Encontrado em 30/09/2026, na `055` (*Polish da folha e dos componentes*), ao corrigir o G1 da
[auditoria de polish](auditoria-polish-ui-2026-09-30.md).

> **Não vira escopo por estar escrito aqui.** A `055` recebeu uma lista fechada de telas para o G1 —
> Ocupação e Corte —, e a Matrículas não estava nela. Decidir se, quando e com que lote corrigir é do
> usuário.

## O que se observou

Em `matriculas.html`, a seção "O que sairá vazio, e por quê" é `<section class="resumo">`. A classe é
a dos **blocos de números** (`display:flex;flex-wrap:wrap`), e na `section` ela faz de cada filho um
item de fileira. Medido a 1280 × 900, no banco da auditoria, com a população dos convocados do marco
do Edital 51/2026:

| Filho | Largura | Posição |
|---|---:|---|
| `h2` "O que sairá vazio, e por quê" | 236 px | x = 24 |
| `p.nota` | 600 px | x = 268, **ao lado do título** |
| `dl.meta` | 1.232 px | linha seguinte |
| `form.confirmar` | 343 px | linha seguinte |

O título e a nota que o explica ficam lado a lado, e o resto quebra para baixo — o mesmo defeito que a
auditoria mediu na Ocupação, com menos dano, porque aqui não há números a separar dos rótulos.

## O que resolveria

O que a `055` fez na Ocupação: tirar a classe da `section`. Nenhuma regra nova; a seção volta a ser
bloco, e o título, a nota e a lista se empilham. Não há `ul.resumo` a criar, porque a seção não tem
números em bloco.

## Custo

Uma linha de template, e a medida de conferência. Sem efeito na folha, portanto sem efeito no teto de
caracteres da tela de distribuição.

## Situação em 01/10/2026 — resolvido pela `058`

A `058` tirou a classe da `section` (FR-1074), como a `055` fez na Ocupação, sem regra nova. Medido
no mesmo banco, a 1280 × 900: a seção é bloco, o título fica em y = 560 e a nota em y = 600, os dois
em x = 24 — antes, a nota estava em x = 268, ao lado do título. Medidas em
`specs/058-polish-residuos/verificacao.md`.
