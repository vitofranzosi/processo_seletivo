# Polish da tela da convocação do candidato — 12/11/2026

Intervenção localizada em `portal/convocacao.html` (ramo com documento pedido), nos parciais
`_obrigacoes_da_convocacao.html` e `_cartao_do_documento_da_convocacao.html`, e em
`portal/static/portal/portal.css`. Nenhuma regra, projeção (`portal/obrigacoes.py`), view, modelo ou
script mudou: toda frase de estado continua vindo da projeção. Uma decisão do usuário revisou o
rótulo do reenvio — a FR-3739 da `118` e, por consequência, a FR-5601 da `150` (redação anterior
preservada nas duas).

## Diagnóstico confirmado

Medido nos cenários da jornada do convocado (`tests/fixtures/jornada_do_convocado.py`), a 390, 768,
1280, 1440 e 1920 px.

1. **Coluna estreita.** Todo bloco tinha a medida de leitura (68ch ≈ 600 px); a 1280 px a metade
   direita ficava vazia, e o cenário E tinha 2083 px de altura.
2. **Andamento em lista com marcadores**: "A enviar: 0" pesava o mesmo que "Aguardando conferência:
   4".
3. **Cartões**: "Ver o arquivo recebido" era uma faixa verde do tamanho do cartão — o elemento mais
   forte da tela para a ação menos urgente —, e "Enviar outro arquivo" ficava solto embaixo. O selo
   ocupava uma linha própria.
4. **"Sobre esta convocação"**: seis pares rótulo/valor em coluna única.
5. **O resumo do estado** ("Você não tem mais documentos para enviar agora…") era uma linha em
   negrito igual às vizinhas, e o cartão do prazo tinha o mesmo destaque verde com ou sem tarefa.

## O que mudou

- **Moldura única** de até 76rem; o texto corrido continua na medida de leitura. A partir de 64rem
  o andamento sobe para o lado da chamada. A ordem do documento (FR-3859) não muda — é a do Tab e do
  leitor de tela.
- **Andamento em indicadores**: âmbar para o que é da pessoa (a corrigir, a enviar) quando há o que
  fazer; neutro para o que é da comissão; o zero apagado. O texto lido é o mesmo "Rótulo: N".
- **Resumo do estado com moldura**: âmbar com tarefa (seguido da ação), verde sem tarefa. Sem
  tarefa, o cartão do prazo perde o verde e fica neutro — continua visível, com a data no maior
  texto (FR-3861).
- **Cartões**: nome e selo na mesma linha; ações no pé do cartão; duas colunas a partir de 640 px
  quando há mais de um cartão, da mesma altura por linha.
- **"Ver o arquivo recebido"** deixou de ser a faixa verde do tamanho do cartão: é um botão de
  contorno, de consulta.
- **"Enviar outro arquivo" virou "Substituir o arquivo enviado"** (decisão do usuário, FR-3739
  revista). Fica abaixo de "Ver o arquivo recebido", como link recolhido — menos destaque, com alvo
  de toque de 44 px e acesso por teclado. Aberto, antes da escolha do arquivo: *"Envie um PDF
  completo. Ele substituirá o arquivo atual na conferência. O anterior continuará registrado."*, e o
  botão final diz *"Enviar novo arquivo"*. É o que o comando `apresentar`
  (`convocacao/application/documentos.py`) faz — FR-3579 da `115`: cada envio é uma apresentação
  nova, a vigente é a mais recente, nada se apaga; o mesmo arquivo repetido não vira versão; e o
  envio é recusado depois de conferido, com resultado registrado ou com o prazo vencido. A permissão
  não mudou: só o que a tela diz dela. Mostrar a substituição só depois de pendência foi descartado —
  tiraria a correção espontânea, e o servidor continuaria aceitando.
- **"Sobre esta convocação" em grade de pares**; fundamento e convocação substituída tomam a linha.

## O que não mudou, e por quê

- **O título e a mensagem do estado "tudo enviado"** ("Você foi convocado!" e a frase de
  consequência com tudo enviado) são o objeto da spec `154`, já decidida e em implementação na
  branch `claude/154-implementacao` (título *"Acompanhe sua convocação"*, consequência só com
  providência pendente). Este polish não toca nessas linhas, para não colidir com ela.
- **A ordem prazo → resumo** é a da FR-3859 da `121`; o destaque foi para o resumo, sem reordenar.
- **Seção expansível em "Sobre esta convocação"**: a FR-3740 da `118` exige o bloco visível, sem
  `details`. Ficou compacto, e não recolhido.
- **Envio de vários documentos**: já é o comportamento implementado (`150`, mergeada no #496): com
  dois ou mais arquivos escolhidos, cada botão diz "Enviar os N documentos escolhidos" e envia um por
  requisição. Nada mudou ali.

## Achados para registro

- **"o atendimento institucional"** no campo Atendimento é o texto de reserva de
  `_atendimento.html` quando a unidade do Edital não tem canal registrado
  (`identificacao.da_unidade(...).canal()` vazio). Com canal, aparece o endereço — como nos cenários
  daqui (`selecao@exemplo.test`). Em produção o valor é obrigatório; o que se vê no ambiente da
  equipe é falta de cadastro, não defeito da tela. Não foi inventado texto substituto.
- **No celular a página ficou um pouco mais alta** (cenário E, 390 px: 2350 → ~2500 px), pelos
  indicadores em linhas e pelo alvo de toque das ações; no desktop caiu 38 % (2083 → ~1280 px).
- **"Se você não atender no prazo…" logo depois de "você não tem mais documentos para enviar"** gera
  dúvida sobre obrigação restante. É o achado 20 do estudo da jornada final, resolvido pela spec
  `154` (consequência só com providência pendente), em implementação noutra branch.

## Capturas

`‹cenário›-‹largura›-antes.jpg` e `-depois.jpg`. Cenários: **A** nada enviado; **E** todos
recebidos, aguardando conferência (o da tela original); **F** uma correção pedida e um a enviar;
**J** pendência sobre item que nunca recebeu arquivo; **G** prazo vencido; **I1** resultado
registrado. Os demais (D envio parcial com aproveitado, H conferidos, K prazo não iniciado, L só
opcional) foram capturados nas cinco larguras e conferidos sem rolagem horizontal; não estão aqui
para não pesar o repositório.
