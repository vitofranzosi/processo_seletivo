# Contrato visual — as telas de operação

Cada linha diz o que o elemento garante e a medida que o prende. Medido a 1280 × 900 no banco
`ps_057_polish`, salvo quando dito.

## Detalhe do Edital — "O que fazer agora"

| Garantia | Medida |
|---|---|
| No máximo uma ação preenchida | contagem de `.botao` sem `.secundario` nem `.desabilitado`, fora de `.terminais` ≤ 1 |
| Destrutivas por último, separadas e contornadas | `.terminais` é o último filho do grupo; nenhum `.botao` dentro dele tem fundo vermelho |
| Marcador "irreversível" | `.marca-irreversivel` ao lado de Encerrar, Cancelar e Publicar |
| Secundárias em linha | as secundárias dividem topos (não uma por linha) a 1280 px |
| "Quem atuou" na altura do conteúdo | altura do cartão = altura do conteúdo + preenchimento, ±2 px |

## Condução do marco

| Garantia | Medida |
|---|---|
| Um gesto preenchido | um `button.botao` sem `.secundario` na seção dos gestos |

## Lista de Editais

| Garantia | Medida |
|---|---|
| Linha baixa | altura da `tr` ≤ 90 px |
| Terminais no fim, separadas | `.terminais` último filho de `.acoes` |
| Zerada esmaecida | `.acao.zerada` quando o contador é 0 |

## Glossário

| Garantia | Medida |
|---|---|
| Fechado, no lugar | `details.como-preencher` sem `open`, com o `p.definicoes` inteiro dentro |
| A faixa à vista | `p.imutavel` fora de qualquer `details` |
| O termo definido no primeiro uso | `test_vocabulario_da_composicao` verde |

## Atenção, Auditoria, documentos, fichas

| Garantia | Medida |
|---|---|
| Sinal sem moldura | `.sinal` sem borda própria; `.sinais` com `border-left` âmbar |
| Evento sem cartão | `.auditoria li` sem fundo nem borda lateral; altura média ≤ 70 px |
| Documento no desenho da mesa | `ul.documentos` com um `li` por requisito |
| Ficha curta | largura de `dl.ficha.curta` < 50% da coluna |

## Matriz de Alocação

| Garantia | Medida |
|---|---|
| Cabe na janela | `document.documentElement.scrollWidth` ≤ 1.280 |
| Cabeçalho compacto | altura do `thead` ≤ 130 px |
| Fixo à janela | `thead` com `position:sticky`; moldura `overflow-x:visible` em tela larga |
| O Edital uma vez | um `th[scope=colgroup]` por Edital; nenhum `.codigo` nos `th` das Etapas |

## Portal — envio de documento

| Garantia | Medida |
|---|---|
| Uma linha de controles | o rótulo-botão do seletor e "Enviar" com o mesmo topo a 1280 px |
