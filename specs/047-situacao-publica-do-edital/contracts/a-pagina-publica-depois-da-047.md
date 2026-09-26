# Contrato — o que a página pública do Edital diz, depois da 047

A tabela é o contrato de leitura. Cada linha é uma afirmação que a página faz, a condição em que ela
é feita e o que a página **nunca** diz no lugar dela. Os rótulos são indicativos: a redação final é
do vocabulário do portal, e o que o contrato fixa é o fato dito.

## Marca de situação (página e cartão da vitrine)

| Condição (em ordem de precedência) | A marca diz | Nunca diz |
|---|---|---|
| Edital cancelado | cancelado, com a data do ato | *Aberta*, *Em breve*, prazo restante |
| Edital encerrado | encerrado, com a data do ato | *Aberta*, *Em breve*, prazo restante |
| Processo encerrado, Edital publicado | Processo encerrado, com a data do ato | *Aberta*, *Em breve*, prazo restante |
| sem desfecho | a marca do período, como hoje: *Aberta*, *Em breve*, *Encerrada* ou *Consulta* | — |

Ato sem data encontrada: o desfecho é dito sem data. O motivo e o autor **nunca** são ditos.

## Vitrine

| Edital | Aparece? | Grupo |
|---|---|---|
| cancelado | não (inalterado) | — |
| encerrado, ou de Processo encerrado | sim | *Inscrições encerradas*, qualquer que seja o período |
| sem desfecho | sim | pelo período (inalterado) |

## Agora e próximo (cabeçalho da página)

| Condição | A página diz |
|---|---|
| há desfecho | nada |
| há Eventos em andamento | cada um, com a descrição publicada |
| há Evento planejado | o de início mais próximo (e os que empatam), com descrição e data |
| nenhum dos dois | nada — nunca *"em análise"* |

O período de inscrições em curso já é dito pela marca e pela faixa do período, e não se repete aqui.

## Cronograma (página pública e acompanhamento)

| Evento | Classe | Rótulo |
|---|---|---|
| `status` cancelado | `cancelado` | *cancelado*, em texto |
| período de inscrições | pela régua do período | *Acontecendo agora* quando aberto |
| com término | pela régua da `045` | *Acontecendo agora* entre início e término |
| sem término | pela régua da `045`: *concluído* a partir do instante de início | — |
| sem início | nenhuma fase | — |

## Resultado divulgado

| Onde | Condição | A página diz |
|---|---|---|
| página da publicação **vigente** | janela computável, aberta | período de interposição, com as duas datas, aberto |
| página da publicação **vigente** | janela computável, encerrada | que o prazo encerrou, e quando |
| página da publicação **vigente** | sem janela, não computável ou `admits: false` | nada sobre recurso |
| página da publicação **sucedida** | qualquer | nada sobre prazo; leva à vigente (inalterado) |
| lista de vigentes, na página do Edital | janela aberta | *recurso até* a data de encerramento |
| qualquer | — | **nunca** uma ação de recorrer (`FR-055` da `017`) |

A janela é **a mesma** que a interposição aplica àquela publicação (`R-5`).

## Histórico dos resultados

| Onde | A página oferece |
|---|---|
| página do Edital, sob cada marco e lista com publicação sucedida | *Publicações anteriores*, recolhido: natureza, data, sucedida, e o endereço de cada uma |
| página de uma publicação que sucedeu outra | as anteriores da mesma cadeia, em ordem |

## O que não muda

- os endereços;
- a API pública;
- o PDF;
- o histórico normativo da `024`;
- o sorteio da `021`;
- a sucessão e a causa de correção da `017` e da `018`;
- o acompanhamento, exceto a régua do cronograma.
