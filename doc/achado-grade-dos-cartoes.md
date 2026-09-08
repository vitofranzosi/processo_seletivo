# Achado — as linhas de campo não compartilham colunas

Encontrado em 08/09/2026, ao encurtar os cartões de Identificação e de Perfil de Vaga
([PR #60](https://github.com/vitofranzosi/processo_seletivo/pull/60)).

> **Não é defeito, e não vira escopo por estar escrito aqui.** O que se registra é o que o arranjo
> atual não consegue fazer, quanto custaria fazer, e o que a mudança alcançaria. Priorizar é do
> usuário.

## O que se observou

Depois do polish, o cartão de Perfil não deixa mais vão nenhum: cada linha reparte a largura antes
do teto de leitura morder, e **toda linha chega à borda direita do cartão**. Mas as divisões
*internas* de uma linha não coincidem com as da linha de cima:

```
identidade     Código ·······195   Denominação ·······775   Localidade ·······1355
o trabalho     Descrição ····471   Carga horária ·····913   Remuneração ······1355
o texto longo  Atribuições ··692   Requisitos ········1355
a quantidade   Vagas ········195   Cadastro Reserva ··1355
```

As bordas 195, 471, 692, 775, 913 não se repetem entre linhas. O olho percebe isso como
irregularidade mesmo quando nenhuma linha está errada.

## Por que acontece

`.campos` é uma linha `flex`, e **cada linha reparte a própria largura sem saber das outras**:

```css
.campos{display:flex;gap:1rem;flex-wrap:wrap}
.campo{flex:1 1 200px}
.campo.curto{flex:0 1 150px}
.campo.largo{flex:2 1 320px}
```

Uma linha de três com um `curto` na frente divide o resto em dois; uma linha de três iguais divide
em três; uma de dois divide ao meio. As três repartições são corretas e **nenhuma delas cai nos
mesmos pontos**.

Não é ajustável por classe: enquanto a repartição for por linha, colunas coincidirem entre linhas é
coincidência, e some assim que alguém acrescenta um campo.

## O que resolveria

Uma grade no lugar da linha — `.campos` como `grid` de um número fixo de colunas, e cada `.campo`
declarando quantas ocupa:

```css
.campos{display:grid;grid-template-columns:repeat(12,1fr);gap:1rem}
.campo{grid-column:span 4}
.campo.curto{grid-column:span 2}
.campo.largo{grid-column:span 6}
```

As divisões passariam a ser as mesmas em todas as linhas de todos os cartões, e o vocabulário
`curto`/`largo` continuaria descrevendo a mesma coisa — só que em colunas, e não em pixels de base.

## O que custaria

`.campos` não é do cartão de Perfil: são **24 linhas de campo em 13 templates** — Perfil,
Modalidade, Fato, Etapa, Evento, Documento, Marco, Critério, as três telas de Retificação, a
criação de Processo e o formulário de retificar. Toda linha do produto mudaria de arranjo ao mesmo
tempo.

O trabalho não é a folha, que é curta: é decidir o *span* de cada um dos **107 campos** já
escritos, conferir as 13 telas em desktop e em 375 px, e resolver o que fazer com os quatro campos
que hoje usam classes de outro propósito (`escolha`, `caracter`) dentro de `.campos`.

Também há uma decisão de conteúdo embutida: com grade, um campo sozinho numa linha volta a poder
deixar vão — a grade reserva as colunas mesmo vazias. Ou se aceita isso, ou se declara que campo
sozinho ocupa a linha inteira, e aí o teto de `68ch` volta a cortá-lo. É a mesma tensão que o
emparelhamento resolveu por outro caminho.

## O que não muda por enquanto

Nada. Os cartões estão sem vão e sem campo cortado, que era o defeito relatado. O que fica é
irregularidade entre linhas — perceptível, e não errada.

Ver também [[achado-anexo-sem-destinatario]] para o outro achado registrado sem virar escopo.
