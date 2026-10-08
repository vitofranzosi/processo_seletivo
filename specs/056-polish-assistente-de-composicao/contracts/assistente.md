# Contrato visual — os elementos do assistente

Cada linha diz o que o elemento garante e a medida que o prende. Medido a 1280 × 900 no Edital
76/2027, salvo quando dito.

## Stepper (`ol.assistente`)

| Garantia | Medida |
|---|---|
| Nove etapas numa linha a partir de 1280 px | um único topo entre os nove `li`; altura ≤ 80 px |
| Colunas de largura igual em qualquer largura | um único valor de largura entre os `li` |
| Situação em texto, e a atual marcada | `.estado` com texto em todo `li`; `aria-current="step"` na atual |
| A etapa começa na primeira dobra | h2 de Perfis em y ≤ 440 |

## Cartão de item (`fieldset.linha` de Evento, Etapa, Documento, Modalidade)

| Garantia | Medida |
|---|---|
| As ações ficam na linha da legenda | o grupo de ações é o filho seguinte à `legend`; nenhum campo do cartão divide faixa vertical só com ele |
| A legenda nomeia o item | `.categoria` com a posição em `[data-ordem]` (coleções ordenáveis) e `.nome` com o identificador, quando houver |
| A confirmação não muda | `data-rotulo` da legenda igual à categoria de antes |
| O grupo não se chama pelas ações | nenhum botão dentro da `legend` |
| Em tela estreita não há sobreposição | abaixo de 60 rem, o grupo volta ao fluxo, abaixo da legenda |

## Faixa do Evento

| Garantia | Medida |
|---|---|
| Início e Término na mesma linha | mesmo `top` |
| Descrição maior que "Onde acontece" | largura do campo de Descrição > largura do de "Onde acontece" |
| Uma faixa só | um único `div.campos` no fragmento do Evento |

## Seção do Conteúdo (`fieldset.secao`)

| Garantia | Medida |
|---|---|
| Largura da leitura | cartão com a medida de leitura mais o preenchimento dele |
| Vazia pequena, preenchida como antes | `rows="2"` sem conteúdo; `rows="5"` com conteúdo |
| Gerada sem caixa | sem borda nem preenchimento |
| A marca continua | " (vazia — não sai no documento)" na legenda de toda seção vazia |
| A página cabe | ≤ 3.000 px |

## Linha da Revisão

| Garantia | Medida |
|---|---|
| Rótulos em coluna | toda linha rotulada num `dt`, o valor no `dd` ao lado |
| Texto de quem elabora não é partido | linha não rotulada continua `span.detalhe` |
| Mesmo conteúdo, mesma ordem | o texto de cada item igual ao de antes |
| Não cresce mais de 10% | altura ≤ 8.791 px |

## Envio

| Garantia | Medida |
|---|---|
| Nada muda no que a etapa grava | conjunto de pares (chave, valor) de "Salvar rascunho" igual antes e depois, em toda etapa |
