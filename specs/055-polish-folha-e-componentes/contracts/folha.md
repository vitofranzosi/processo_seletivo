# Contrato da folha — 055

O que cada componente promete a quem o usa num template, e a medida que prova a promessa. Medidas a
1280 × 900, pelo `getBoundingClientRect` da página renderizada.

## Bloco de números — `ul.resumo`

```html
<ul class="resumo" aria-label="…">
  <li><strong>2</strong>Alvo apurado</li>
</ul>
```

- Cada `li` é uma caixa com borda; o `strong` é o número, em bloco, acima do rótulo.
- **Prova**: nenhum `strong` fica fora do `li` do seu rótulo; o contêiner da seção do recorte não é
  `display:flex`.

## Botões — `.botao` e `.acao` em barra

- `.botao`, `.botao.secundario`, `.botao.perigoso`, `.botao.desabilitado`: **40 px** de altura
  externa, seja `button` ou `a`.
- `.acao` dentro de `.navegacao-etapa`, `.salvar` ou `.filtros`: **40 px**.
- `.acao` em qualquer outro lugar: a caixa pequena de antes (~25 px).
- **Prova**: na barra do assistente, `max(altura) − min(altura) = 0`.

## Controles

- Gestão: todo `input` de uma linha e todo `select` com **40 px**. `textarea`, `checkbox`, `radio` e
  `file` fora.
- Portal: os mesmos controles, dentro de `.campo`, com **42 px** — a altura da consulta da Vitrine.
- **Prova**: na mesma linha, `input` e `select` com diferença de 0 px.

## Barra de filtro — `.filtro`, `.filtros`

- Rótulos no topo; os controles começam todos na mesma altura; o botão tem a altura do controle e
  começa onde o controle começa.
- A ajuda do campo continua depois do controle, ligada a ele por `aria-describedby`.
- **Prova**: na Distribuição, `top(select) = top(input) = top(Filtrar)`.

## Títulos

- `h1` 1,6 rem, `h2` 1,15 rem, `h3` 1 rem, todos com peso 600.
- **Prova**: em nenhuma tela auditada um `h3` renderiza maior que o `h2` da mesma página.

## Corpo da seleção (portal)

- Sem `.sorteio-da-selecao` como filho, a coluna lateral começa no Cronograma, no topo das Vagas.
- **Prova**: `top(cronograma) = top(vagas)` na seleção sem sorteio; o sorteio acima do Cronograma na
  seleção com sorteio.
