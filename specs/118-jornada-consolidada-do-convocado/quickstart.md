# Quickstart: A jornada consolidada do candidato convocado

Roteiro para demonstrar a feature **depois de implementada**, pelo portal, sem banco nem shell para
ver a tela (Constituição, VI). Os dados são fictícios.

## Preparação

- Ambiente local pelo `make preparar`, com `INTERFACE_SELETOR_IDENTIDADE=true`.
- O código de acesso do portal sai no terminal do servidor, ou em <http://localhost:8025> no compose.
- **Os doze cenários se montam pelo roteiro**, e não à mão:
  `doc/revisao-ux-jornada-do-convocado-2026-11-04/roteiro-de-captura.py` (PR #375), que usa as
  fixtures da `115` e da `059`, num banco de teste próprio contra PostgreSQL. As instruções estão no
  cabeçalho dele.
- Para percorrer à mão, a gestão monta o cenário pelo caminho da `115`: Edital com documentos na
  convocação (e, nos cenários C, com o Requerimento *na convocação*), inscrição, classificação,
  convocação com vencimento, conferência na página **Documentos da convocação**.

## O que olhar em cada cenário

Para cada um, abrir **Acompanhar**, **Ver convocação** e, quando houver, o **Requerimento**, a
375 px e em desktop, e responder às quatro perguntas: *preciso enviar mais alguma coisa? O que está
com a comissão? Qual é o prazo? O que acontece depois?*

| | Cenário | No acompanhamento | Na convocação |
|---|---|---|---|
| A | documentos sem Requerimento | *"Você ainda precisa enviar 4 documentos."* → *"Ver o que falta na convocação"* | bloco *O que fazer agora* na primeira tela, com as quatro âncoras |
| B | Requerimento sem documentos | *"Preencher o Requerimento de Matrícula."*, direto à tela dele (**como hoje**) | estrutura de hoje |
| C1 | os dois, nada enviado | as quatro tarefas e o Requerimento, link à convocação | o Requerimento por último na lista do topo |
| C2 | os dois, só o Requerimento enviado | *"Você ainda precisa enviar 4 documentos."*; *"✓ Requerimento de Matrícula enviado."* como linha secundária | o enviado no bloco *O que você já apresentou* |
| D | aproveitado da inscrição | *"Nada por enquanto."* + frase de conclusão, se não houver outra tarefa | *"Você já enviou este documento na inscrição…"*, selo *"Aguardando conferência"* |
| E | enviados, aguardando | *"Nada por enquanto."* + *"Você não tem mais documentos para enviar agora. A comissão ainda vai concluir a análise."* | sem bloco *O que falta* |
| F | pendente, prazo em curso | *"Você ainda precisa corrigir 1 documento e enviar 1 documento."* → *"Ver e corrigir os documentos pendentes"* | o pendente primeiro, com o motivo; cartão com selo *"Precisa de correção"* |
| G | pendente, prazo vencido | a frase do vencido e o que ficou sem envio | *"O prazo terminou"*; *"Até o prazo, ficou assim"*, com o Requerimento não enviado; abrir o Requerimento: *"O prazo terminou"* e *"Voltar à convocação"* |
| H | tudo conferido, sem desfecho | a mesma frase de E | *"Conferido: de acordo com o Edital."* |
| I1 | aceite | *"Vaga aceita"* e a frase de que o registro não é matrícula, bolsa nem contrato | *"Resultado registrado"*, o mesmo rótulo e a mesma frase; lista só de histórico |
| I2 | indeferido | rótulo e fundamento | *"Não enviado."*; *"Enviado em …; não foi conferido antes do resultado."*; nenhum formulário |
| J | pendência sem envio anterior | *"Você ainda precisa enviar 1 documento."* | *"Precisa de correção: ‹motivo›. Envie o arquivo até…"* |
| K | prazo não iniciado | a frase do prazo não iniciado, sem data como prazo | *"O prazo ainda não começou a correr… Você já pode enviar."*; a data só em *Sobre esta convocação* |
| B2 | Requerimento sem documentos, já enviado | *"Seu Requerimento de Matrícula foi enviado."* com *"Conferir…"* (**como hoje**) | estrutura de hoje |
| L | só um facultativo sem envio | *"Nada por enquanto."* + frase de conclusão + a linha do opcional | bloco *Documentos opcionais*, com o envio; nenhuma contagem |
| M | Processo encerrado, chamada em aberto | *"O envio pelo portal está encerrado"*, sem prazo vencido e sem promessa de conferência | o mesmo título; itens recebidos *"não foi conferido antes do encerramento do Processo"*; sem formulário de documento |
| N | indeferido, Requerimento pedido e nunca enviado | rótulo e fundamento | *"Requerimento de Matrícula: não enviado."* |
| K2 | prazo não iniciado, com pendente, tarefa e opcional | a frase do prazo não iniciado | nenhum cartão nem opcional com *"até ‹data›"* |

## Pelo teclado e pelo leitor de tela

Na convocação de F, a 375 px:

1. Tab desde o topo: o foco passa pelas âncoras do bloco 1, pelo botão *"Ver e corrigir os
   documentos pendentes"* e pelos controles de cada cartão, na ordem visual, sempre com contorno.
2. Ativar a âncora do pendente: o foco chega ao cartão dele.
3. Pela lista de formulários do leitor de tela: cada *"Enviar"* e cada *"Escolher arquivo PDF"* diz o
   nome do documento.

## O que não pode mudar

- "Minhas inscrições": a mesma linha *"Convocação aberta · Ver convocação"* de antes.
- A gestão: condução e documentos da convocação como na `115`.
- Nenhuma mensagem sai por pendência, por conferência ou por vencimento.
- Um Edital sem documento e sem Requerimento: *"Siga as instruções do Edital para esta
  convocação."*, com a estrutura de hoje.
