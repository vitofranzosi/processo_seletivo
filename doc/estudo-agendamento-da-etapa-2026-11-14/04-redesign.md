# 4. Redesign da experiência (14/11, segunda rodada)

*A primeira versão do protótipo acertou o fluxo e errou a forma. Esta rodada redesenha a experiência
sem mudar regra: as R-01 a R-26, a spec `166` e o modelo continuam como estavam. As capturas do antes
e do depois estão em [`prototipo/capturas/`](prototipo/capturas/).*

## 4.1 Diagnóstico crítico do antes

| Tela | O que a fazia parecer ferramenta administrativa antiga |
|---|---|
| Configurar | caixas dentro de caixas (seção › dia › janela › campo); campos pequenos e soltos; a capacidade, que é a resposta que a comissão procura, num painel de texto corrido; "Faltam 11" como frase, e o caminho para resolver no meio do formulário, abaixo da dobra |
| Montar | **cinco números com o mesmo peso** disputando o alto da página; a mensagem e a prévia empurrando a grade para baixo; linha ocupada com três andares (nome, protocolo + origem, dois botões), cerca de **88 px por linha** medidos na captura; a lista lateral e a grade dizendo a mesma coisa sem dividir trabalho |
| Prévia | uma lista numerada de nomes em duas colunas ("e mais 35"): responde "quem vai para onde" antes de "posso aplicar?" |
| Alocar à mão | ao escolher alguém, **cada horário livre vira um botão "Agendar Yago aqui"** — 21 botões iguais num dia; e a escolha morria ao trocar de aba de dia, de modo que **mover alguém para outro dia era impossível** sem liberar e recomeçar |
| Remarcar | uma lista suspensa com todos os horários livres de todos os dias, sem o dia à vista depois de escolhido |
| Conferir | correto, mas a pergunta "posso publicar?" só se respondia lendo a página inteira |
| Publicada | quatro números de mesmo peso para dizer uma coisa: quantos avisos saíram |

O problema não era cor nem ícone. Era **hierarquia** (tudo pesava igual), **lugar da ação** (a ação
se espalhava pela grade) e **ordem das respostas** (a tela mostrava detalhe antes do veredito).

## 4.2 As decisões

1. **Uma superfície por assunto.** Seção branca com borda; nada de caixa dentro de caixa. As
   janelas viraram pares de horas numa linha por dia, com "+ janela" ao lado; as bancas, uma linha
   por banca com o cabeçalho das colunas uma vez só.
2. **Veredito antes do detalhe.** O simulador da configuração abre com "Faltam 11 horários" ou
   "Cabem todas as 43 pessoas", em cor de estado; depois o medidor; depois a conta numa linha. A
   conferência abre com quatro linhas de prontidão (✓ 43 de 43 com horário, ✓ dias no período,
   ✓ salas, · autoridade). A prévia abre com "43 pessoas recebem horário".
3. **A falta se resolve onde é dita.** O simulador oferece "Acrescentar Ter., 24/11 +32",
   "Acrescentar uma banca +32" e "Tirar o intervalo +16", com o ganho de cada um e destaque no que
   resolve sozinho. Um clique, sem rolar.
4. **Um resumo só na montagem.** O medidor real da gestão (`.medidor`, o mesmo do cartão da Etapa
   em Minhas atividades) com "0 de 43 com horário", e ao lado os dois fatos que contam: horários e
   sobra (ou falta), e o link para quem está sem horário.
5. **A grade é o que se vê; o painel é onde se age.** Cada horário é uma linha de **42 px**, e a
   célula inteira é um botão: ocupada mostra quem, livre fica quieta. Clicar abre, no painel à
   direita, **a pessoa** (com os horários livres por dia e banca, "Mudar de horário" e "Liberar") ou
   **o horário livre** (com a lista de quem está sem horário, com busca). Nenhum texto de ação se
   repete pela grade; o escolhido ganha contorno.
6. **O seletor de horário é um componente só**: dia como botões, horários livres como opções
   compactas, agrupados por banca. Serve à alocação à mão e à remarcação, e atravessa dias.
7. **A prévia mora no painel**: veredito, tabela dia × banca, horários que sobram, a regra da
   ordem, e a relação nominal recolhida em "Ver quem vai para cada horário (43)". A grade não se
   mexe enquanto ela está aberta.
8. **A ação principal é a que falta fazer, e as repetidas somem.** "Preencher automaticamente" é
   primária enquanto há gente sem horário e desaparece quando não há; "Conferir e publicar" vira
   primária depois. Nenhum botão aparece duas vezes na mesma tela.
9. **Reuso, e não linguagem nova.** `.medidor`, `.largura-N`, `.situacao`, `.botao`, `.acao`,
   `.aviso`, `.vazio`, `.tabela`, a moldura da conferência da `140`, e os tokens de
   `shared/tokens.css`. As peças novas — controle segmentado, linha de dia, seletor de horário,
   painel de ação, veredito — usam só os tokens e a escala de espaçamento que a gestão já pratica.

## 4.3 Antes e depois, por tarefa

Cenário A (43 pessoas, uma banca), medido no protótipo em 14/11. "Cliques" conta o que a pessoa
faz, sem digitar.

| Tarefa | Antes | Depois |
|---|---|---|
| 1. Configurar para 43 | formulário + painel de texto; ler a frase para saber se cabe | o veredito em cor diz se cabe; mesmo número de campos |
| 2. Resolver a falta de 11 | rolar até "Acrescentar o dia seguinte", 1 clique, voltar ao painel para conferir | **1 clique** em "Acrescentar Ter., 24/11 +32", no painel que já está à vista; o ganho aparece antes |
| 3. Distribuir automaticamente | 2 cliques; a prévia empurra a grade e mostra 8 nomes + "e mais 35" | 2 cliques; a prévia abre no painel com veredito e tabela dia × banca; a grade não se mexe |
| 4. Alocar à mão (mover alguém para outro dia) | **impossível** sem liberar e recomeçar; no mesmo dia, 2 cliques, com 21 botões "Agendar Yago aqui" na tela | **4 cliques** (pessoa, dia, horário, confirmar), em qualquer dia; **0** botões de ação repetidos na grade |
| 5. Remarcar | lista suspensa longa com todos os dias misturados | dia + horário em 2 cliques, com "Seg., 23/11, 09:30 → Terça-feira, 24/11, 14:30" à vista antes de confirmar |
| 6. Conferir e publicar | ler as seções para saber se está pronto | quatro linhas de prontidão no topo; o resto como antes |

| Medida da montagem | Antes | Depois |
|---|---|---|
| Altura de uma linha ocupada | ~88 px (medido na captura) | **42 px** (medido no navegador) |
| Linhas que cabem em 768 px de altura (só a conta, sem o cabeçalho da página) | ~8 | **18** |
| Indicadores no alto | 5 caixas de mesmo peso | 1 medidor + 3 fatos |
| Botões de ação na grade de um dia (32 horários) | 2 por pessoa agendada, ou 21 "Agendar … aqui" durante a escolha | **0**: a célula é o botão |

## 4.4 Validação

No Chromium do painel, sob a CSP de produção, sem erro no console:

- **desktop** 1440 × 900 e **notebook** 1366 × 768: configurar, simulador com atalho, montar,
  prévia, mover entre dias, horário livre → pessoa, conferir, publicar, remarcar;
- **celular** 375 × 812: a montagem vira coluna (resumo, painel, grade) e a grade, lista de
  horários com nome e protocolo; **sem rolagem horizontal** (largura do documento = 375);
- **duas bancas** (cenário B): grade com duas colunas, prévia com a tabela dia × banca, atalhos do
  simulador com o ganho certo (+16 pelo dia, +8 pela banca, +8 sem intervalo).

## 4.5 Limitações do design system, registradas e não resolvidas aqui

O redesign esbarrou em quatro faltas da gestão, que valem para outras telas e **não** são escopo da
`166`. Ficam como registro, na linha de "achado não vira escopo":

1. **Não há escala de espaçamento como token.** Os valores se repetem (.5, .75, 1, 1.5rem) por
   costume, e não por regra; cada folha nova os reescreve.
2. **Não há componente de controle segmentado nem de seletor de horário/opção compacta.** O
   protótipo os criou com tokens; se a agenda for implementada, eles vão para `componentes.css`, e
   não para uma folha de tela.
3. **Não há padrão de painel de ação lateral** (o "onde se age" ao lado do "o que se vê"). A
   Distribuição e a Mesa resolveriam a mesma tensão do mesmo jeito.
4. **Campos de formulário têm altura fixa de 2.5rem** (`formularios.css`), o que obriga a sobrescrever
   em campos compactos, como as horas dentro de uma janela.

## 4.6 O que não mudou

As regras, a spec e o modelo. A página pública, a área do candidato e o e-mail, que a avaliação não
apontou, ficaram como estavam.
