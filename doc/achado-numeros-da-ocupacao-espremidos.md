# Achado — os quatro números da ocupação saem espremidos numa coluna estreita

Encontrado em 28/09/2026, no preview do PR 221 (RC-137), contra a `main` em `28b3815b`.

> **Não virou escopo por estar escrito aqui.** É registro; decidir se e quando corrigir é do
> usuário.

## O que se observou

Em `interface/templates/interface/ocupacao.html`, cada recorte é uma `section.resumo`, e a folha a
desenha como `flex` em linha. Os quatro números — Publicadas, Efetivas, Ocupadas, A ocupar — vão num
`dl.meta` que ocupa **70px** de largura, e cada rótulo fica sobre o seu valor numa coluna estreita, ao
lado dos links do recorte. Medido pelo navegador numa janela de 1024px: `DL.meta` com 70px, os
`p.acoes` à direita, e o formulário da nova apuração na linha seguinte.

## Por que não é deste PR

A largura é a mesma com e sem o link *"Abrir a convocação deste recorte"*: medida escondendo o link
novo, o `dl` continua com 70px, e o recorte não apurado, que não tem link nenhum, também. O defeito é
anterior ao RC-137 e é da folha de estilo da tela, não do link.

## O que se vê por causa dele

A `UX-031` da `016` pede os quatro números juntos, e eles estão juntos — mas lidos como uma coluna de
oito linhas curtas, e não como o quadro que a tela anuncia. Em tela estreita isso pode ser o desejado;
em 1024px, não parece ser.
