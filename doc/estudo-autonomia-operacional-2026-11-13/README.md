# Auditoria de autonomia operacional depois da publicação do Edital

*13/11/2026 · `main` em `0f492bb6` · banco isolado `ps_autonomia`, com o `seed_demo` e os dezessete
cenários de treinamento da `134` (rodada 1) · leitura das telas reais nos papéis de presidência,
avaliador, conferente alocado, Gestor, Publicador e setor de formalização. Nada foi alterado no
código, e nenhuma spec foi aberta.*

A pergunta: uma pessoa que conhece o trabalho institucional, mas não os conceitos do GPS, descobre
o que fazer, quando, por quê, e como saber que terminou?

Cada afirmação abaixo leva uma marca: **[obs]** é o que a tela mostrou, com o texto literal;
**[inf]** é leitura minha; **[nv]** é o que não foi verificado; **[cód]** é o que um levantamento
auxiliar leu no código de `backend/processo_seletivo/interface/` e eu **não** conferi na tela —
vale como pista, com arquivo e linha, e não como observação.

## A. Veredito

**Dentro de um Edital, para quem preside, o GPS já conduz. Entre Editais, entre papéis e na
escolha do que importa primeiro, ele ainda só lista.**

A hipótese de partida — "orienta a execução, mas não a descoberta" — se confirma só em parte, e é
bom dizer onde ela **não** se confirma, para não reabrir o que funciona:

- O Centro de Controle responde, numa tela, "onde estamos", "o que é seu", "o que espera e até
  quando" e "o que está com outro papel". **[obs]** No SIM11: *"2 ações são suas e 2 aguardam prazo
  ou resposta (a primeira até 18/11)"*.
- A espera vem com causa e data. **[obs]** *"O prazo recursal deste marco ainda está aberto: ele se
  encerra em 18/11/2026 às 23h59."*
- O que ainda não cabe diz por quê. **[obs]** Na fase Vagas do SIM09: *"Ainda não começou: só
  participa a faixa do corte, e o corte que a alimenta não foi emitido"*.
- A tela do ato devolve ao passo seguinte. **[obs]** Depois de emitir o corte do SIM09: *"Próximo
  nesta lista: Distribuir 6 inscrições…"*, *"Ainda neste marco: …"*, *"Voltar ao Centro de Controle
  do Edital"*.
- Não reproduzi a evidência citada no contexto, de fase "concluída" com ação pendente. **[obs]** O
  que encontrei foi o defeito inverso (causa 3).

Onde a hipótese se confirma está nas causas da seção C. O resumo: a orientação existe, mas **não é
uma só**, **não tem hierarquia**, **não descreve o momento do Edital** e **se cala nas passagens de
mão**.

**O que este veredito não prova.** Tudo aqui é leitura de tela por um agente que conhece o modelo.
Nenhuma pessoa da equipe foi observada. "Autonomia" continua sem medida até o protocolo da seção E.
Também não foram reexecutados: a cadeia inteira corte → análise documental → apuração → convocação
(parei no corte); a desistência e a vaga reaberta depois das `154`, `155` e `158`; o portal do
candidato; o sorteio; o celular. **[nv]**

## B. Mapa de autonomia

Três níveis: **suficiente** (a tela responde sem ajuda), **parcial** (responde, mas pede
interpretação ou uma segunda tela), **depende** (pede memória, colega ou conhecimento do modelo).

| Episódio | Localização | Próxima ação | Por que agora / por que esperar | Quem age | Conclusão e retomada |
|---|---|---|---|---|---|
| **A** Retomar um Edital | parcial — o resumo enumera fases "em aberto", não o momento | suficiente para quem preside | suficiente | parcial — papel, nunca a pessoa | parcial — nada diz o que mudou desde a última visita **[nv: histórico não avaliado]** |
| **B** Da classificação à convocação | suficiente no Centro | parcial — a ação real divide o destaque com um ato residual; o rótulo muda na tela do ato | suficiente | depende — o revezamento com o avaliador não é dito | parcial — parei no corte **[nv]** |
| **C** Convocação em andamento | suficiente — *"Neste recorte, agora"* separa ação, espera e feito, pessoa a pessoa | parcial — dois afazeres só aparecem nesta tela | suficiente | parcial — conferência é "sua" para dois papéis ao mesmo tempo | parcial — as mesmas 3 convocações aparecem como "aguarda" e como "a conferir" (SIM12) |
| **D** Exceções | parcial | parcial — lista sem concorrente vira "ação" em todo Edital | suficiente nos impedimentos lidos | parcial | **[nv]** desistência e vaga reaberta não reexecutadas |
| **E** Passagem entre responsáveis | parcial | depende — setor, Gestor e Publicador não têm lista própria | parcial | depende — ninguém é nomeado nem avisado **[nv: aviso interno não encontrado]** | depende — quem termina não lê "agora está com…" |
| **F** Vários Editais | depende — a lista mostra "Ativo · Publicado" em todos | suficiente só para presidência e alocados | parcial — espera tem data; ação não tem | — | depende — fora da comissão, é abrir Edital por Edital |

## C. Quatro causas estruturais

### 1. Há três respostas para "o que é meu agora", e elas não coincidem

A página inicial, *Minhas atividades* e o Centro de Controle cobrem conjuntos diferentes de atos, e
cada uma fala como se fosse a resposta inteira.

- **[obs]** Presidência, página inicial: *"Nenhum ato de Edital ou de Retificação, recurso ou
  avaliação aguarda você agora."* Um clique depois, *Minhas atividades*: *"Para fazer agora · 22 atos
  em 13 Editais"*.
- **[obs]** Gestor, *Minhas atividades*: *"Nada depende de você agora no que esta página cobre."*
  Centro do SIM14, mesmo Gestor: *"2 ações são suas."* O mesmo no SIM11 e no SIM16.
- **[obs]** Presidência no SIM17: o Centro lista *"Sua · Conclusão — Designar quem recebe os
  documentos"*; *Minhas atividades* conta 1 ato nesse Edital, e não é esse.
- **[obs]** Na convocação do SIM11: *"1 pessoa pode ser avisada agora"* e *"3 convocações comunicadas
  ainda não estão na página pública"*. Nenhum dos dois aparece em "O que fazer agora" — nem da
  presidência, nem do Publicador, nem do Gestor.
- **[obs]** Setor de formalização com 3 pessoas aptas por exportar no SIM16: *Minhas atividades* diz
  *"Nada depende de você agora"*; a área *Formalização* lista o Edital sem dizer quantas faltam.
- **[obs]** A lista de Processos mostra os 19 como *"Ativo · Publicado"*, sem fase nem pendência.
- **[obs]** A própria página admite o limite: *"Nenhuma linha aqui não quer dizer que o Edital não
  tenha outras pendências."*

- **[cód]** A origem é de desenho, e não descuido. O Centro, *Minhas atividades* e o "Próximo nesta
  lista" leem uma conta só (`andamento.py`, ordenada em `providencias.py`). O índice *"Neste
  recorte, agora"* da convocação é outra conta, independente (`conducao_da_convocacao.indice`), e é
  por isso que o aviso de pendência nunca vira providência. As pendências do encerramento são uma
  terceira (`encerramento.py`, `relatorio_do_edital.py`). E *Minhas atividades* **filtra** a
  primeira: setor de formalização, Publicador e quem julga recursos ficam fora por decisão escrita
  (D-004 da `160`).

**[inf]** Cada aviso é verdadeiro no seu recorte, e por isso nenhum teste o acusa. Mas quem lê
"nada depende de você" não lê o recorte. Numa equipe de duas ou três pessoas que acumulam papéis,
quem age por permissão de gestão — e não por presidir — fica sem lista nenhuma, e a conferência
volta a ser abrir cada Edital. É o episódio F inteiro.

### 2. O GPS lista o que é possível, e não o que importa

- **[obs]** O Centro declara: *"Todas já podem ser feitas […] e o GPS não escolhe a ordem entre
  elas."*
- **[obs]** *"Emitir a ordem que declara que ninguém concorreu nesta lista"* aparece em 9 dos 13
  Editais da presidência. No SIM16 ela é a *"Sua próxima ação"*, com botão; o trabalho que encerra
  o certame — *"3 pessoas aptas ainda sem documentos disponibilizados"* — é a última linha, sem
  destaque.
- **[obs]** Em *Para fazer agora*, nenhuma das 22 linhas tem data, e a ordem é a do número do
  Edital. Só a espera tem prazo.
- **[obs]** Nenhuma ação diz o que deixa de acontecer se ela não for feita.
- **[cód]** O motivo de cada ação existe na conta (`razao`), mas o cartão "Suas ações" do Centro não
  o mostra; a espera mostra. E a data não ordena *Minhas atividades* por decisão escrita (D-007 da
  `160`: a data é o fim de uma espera, e não um prazo).

**[inf]** A regra "só o que já pode ser feito" eliminou o beco sem saída, e isso deve ficar. O que
falta é peso: o operador que retoma na segunda-feira recebe uma lista plana em que formalidade e
providência urgente têm a mesma cara.

### 3. O mapa mede atos por lista, e não o momento do Edital

- **[obs]** *"Onde estamos"* do SIM11 (entrega de documentos), do SIM12 (conferência) e do SIM15
  (vagas não preenchidas) é a mesma frase: *"Há algo em aberto em classificação, resultado e
  recursos e convocação."* SIM16 e SIM17, no fim do certame: *"…em classificação, resultado e
  recursos e conclusão."*
- **[obs]** Com uma lista de cota sem inscritos, Classificação, Resultado e Vagas ficam *"Em curso"*
  até alguém emitir a ordem vazia. Quatro ou cinco fases "em curso" ao mesmo tempo.
- **[obs]** SIM16: *"Conclusão — Ainda não começou · Depois das convocações"*, e no detalhe da mesma
  fase, *"Em aberto · Pessoas disponibilizadas: 0 de 3"*, com a marca *"1 de outro papel"*.
- **[obs]** SIM12: *"Aguarda — Resposta de 3 convocações"* (*"ninguém precisa agir até a data"*) ao
  lado de *"Conferir os documentos de 3 convocações"*. São as mesmas três.
- **[obs]** *"Vagas — Em curso · nada a fazer agora."*
- **[cód]** Três casos do mesmo desencontro, que não reproduzi: Edital encerrado mostra Conclusão
  *"Concluída"* e as providências da formalização continuam nela (`centro.py` 545, `andamento.py`
  2636); a célula da convocação fica *"Feito"* com chamada ainda sem desfecho (`andamento.py` 2999);
  e *"Seu papel aqui"* só conhece conduzir, publicar, julgar e retificar, de modo que avaliador e
  conferente leriam *"Você acompanha este Edital sem ato a praticar nele"* ao lado de uma ação sua
  (`centro.py` 895). É o achado "fase concluída com ação pendente" do contexto, por outro caminho.

**[inf]** O mapa é fiel ao modelo — cada lista anda no seu ritmo — e a legenda explica isso. Mas a
pessoa pergunta "em que pé está este Edital?", e a resposta honesta ("convocação em andamento: 3
chamados, 1 a conferir, 2 dentro do prazo") está só na tela da convocação, três cliques abaixo.

### 4. A passagem de mão é anônima e silenciosa, e o vocabulário muda no caminho

- **[obs]** O outro é sempre um papel: *"Os avaliadores alocados: avaliar 5 inscrições"*, *"O setor
  da formalização: exportar…"*, *"Quem conduz ou confere documentos"*. Nunca o nome, mesmo quando há
  uma pessoa só.
- **[obs]** Depois do corte do SIM09, o próximo passo é *"Distribuir 6 inscrições sem avaliador
  suficiente"*. A tela que abre é a "Análise documental": a presidência distribui, outra pessoa
  avalia, a presidência volta e consolida, e só então apura. Nada na tela diz que é um revezamento,
  nem que o passo seguinte é de outro.
- **[obs]** Conferência do SIM12: é *"sua"* para a presidência e para o membro alocado, ao mesmo
  tempo, sem dizer quem começa.
- **[obs]** O Centro fala *"Definir até onde se chama"*, *"lista"*, *"Distribuir as vagas entre as
  listas"*. A tela do ato fala *"Corte e progressão"*, *"recorte"*, *"faixa"*, *"alvo declarado"*,
  *"alvo apurado"*, *"geração vigente"*. A ponte (*"no GPS: emitir o corte"*) existe só no Centro.
- **[obs]** A convocação precisa de dois parágrafos para explicar por que *"2 consideradas ocupadas
  na apuração"* convive com *"0 pessoas convocadas"*.
- **[obs]** *Minhas atividades* usa o nome cru do ato — *"Emitir o corte"*, *"Congelar a relação"*,
  *"Observar a extração"* — onde o Centro diz *"Definir até onde se chama"*. **[cód]** Ela lê
  `providencia.ato`, sem a tradução do Centro.
- **[nv]** Não encontrei aviso ao avaliador, ao conferente ou ao setor quando o trabalho chega. O
  levantamento do código também não achou, mas não o procurou de propósito.

**O estado das exceções (episódio D), pelo que está na `main`.** A `155` tem 27 tarefas feitas e 28
abertas: a situação da vaga e a vaga não preenchida existem; a passagem entre cotas, a destinação
por esgotamento e a lista vazia, não. A `156` (comunicação do desfecho) tem 0 de 54 tarefas, e a
`158` (passagem entre cotas) é só spec em rascunho, com oito perguntas abertas. Parte do que o
operador sente como "não sei a saída" nas exceções é capacidade que ainda não existe, e nenhuma
orientação de tela resolve isso.

**[inf]** Em equipe pequena o colega está na sala ao lado, e é ele quem hoje fecha essa lacuna. É
exatamente a "orientação externa" que a pergunta quer eliminar.

**Uma nota lateral.** **[obs]** O guia da equipe, no C09, manda concluir a "Análise documental" e
*depois* emitir o corte; o GPS só admite a ordem contrária. O material de apoio contradiz a tela
justamente no trecho mais difícil.

## D. Três intervenções

Nenhuma pede tela nova. As três mexem no que o Centro e *Minhas atividades* já calculam. Onde há
requisito escrito no caminho, está dito: a decisão é sua.

### 1. Uma só resposta para "o que é meu agora", em todos os Editais e papéis

*Minhas atividades*, a frase do topo da página inicial e a linha de cada Edital na lista passam a
ler a mesma conta do Centro, incluindo o que é do leitor por papel da unidade. A lista de Processos
ganha o momento e a marca do Edital (*"Convocação · 1 sua · espera até 13/12"*).

- **Resolve:** causa 1; episódios E e F.
- **Evidência:** as cinco contradições da causa 1.
- **A decidir:** contraria a D-004 da `160` ("só as bases de vínculo, mesmo nos Editais
  presididos") e o FR-6862, que manda a presidente com permissão de publicar **não** ver "Publicar
  o resultado" ali. É reabrir uma decisão sua de dias atrás, e não um ajuste. A parte que não
  conflita com nada: a frase do topo da página inicial e a linha de cada Edital na lista.
- **Validar:** tarefa 1 do protocolo. Critério: a pessoa aponta o Edital que mais precisa dela sem
  abrir nenhum.

### 2. Peso e momento em "O que fazer agora"

Separar o que faz o Edital andar do que é regularização (lista sem concorrente, relação pública,
aviso de pendência); dar prazo ou consequência a cada ação; trocar o resumo "há algo em aberto em…"
pela frente mais avançada do Edital; e não mostrar "Ainda não começou" em fase com ação disponível.

- **Resolve:** causas 2 e 3; episódios A e D.
- **Evidência:** SIM16, em que a "próxima ação" é a ordem vazia e a exportação é rodapé.
- **A decidir:** não proponho mudar a regra da lista sem concorrente — o ato continua exigido. É só
  a posição dele na tela. Se o Centro pode escolher ordem, contraria a frase que hoje diz que não
  escolhe; e pôr data à frente esbarra na D-007 da `160`.
- **Validar:** tarefas 2 e 5. Critério: a primeira coisa que a pessoa diz que faria é a que move o
  Edital.

### 3. Passagem de mão dita por extenso

Nomear a pessoa quando há uma só; dizer, na tela que inicia um revezamento, quem age depois e
quando o leitor volta; dizer a quem termina que a parte dela acabou e com quem ficou; e levar à
tela do ato o nome que o Centro usou para chegar nela.

- **Resolve:** causa 4; episódios B e E.
- **Evidência:** o passo depois do corte do SIM09.
- **A decidir:** avisar a pessoa por e-mail é hipótese, e não proposta — tem custo de LGPD e de
  ruído, e o teste humano diz se o texto na tela já basta.
- **Validar:** tarefa 3. Critério: a pessoa diz, sem perguntar, quem age em seguida.

**Fora das três, de propósito:** reescrever o vocabulário das telas de ato. É a mudança mais cara e
a que mais depende de ouvir pessoas; o protocolo abaixo registra cada termo que travar alguém.

## E. Protocolo de validação humana

**Quem.** Duas ou três pessoas da equipe de seleção que não participaram do desenvolvimento.
Uma por vez, 45 minutos, com um observador que não responde perguntas sobre o sistema.

**Onde.** Homologação com os cenários restaurados na véspera (`verificar_cenarios_de_treinamento`).
Como a equipe acumula papéis, a pessoa entra com a combinação que terá de verdade, pelas opções
avançadas da página de demonstração — e não com a identidade do roteiro.

**Como.** Objetivo em uma frase, sem nome de tela nem de ato. Pensar em voz alta. O guia da equipe
fica fechado. O observador só intervém depois de dois minutos de impasse, e a intervenção conta
como ajuda.

| # | Objetivo dado à pessoa | Episódio | Acerto observável |
|---|---|---|---|
| 1 | "É segunda-feira. Diga quais Editais precisam de você hoje, e qual primeiro." | F | Lista certa, sem abrir Edital por Edital; justifica a ordem |
| 2 | "Você não vê o SIM11 há uma semana. Em que pé ele está, e o que cabe a você?" | A | Diz "convocação em andamento", quantos responderam, e a ação dela |
| 3 | "O resultado do SIM09 saiu. Leve-o até poder chamar as pessoas." | B | Emite o corte; diz quem age em seguida e quando ela volta |
| 4 | "No SIM12, deixe resolvido o que já pode ser resolvido hoje." | C | Confere, registra desfecho onde cabe, e diz o que fica esperando e até quando |
| 5 | "No SIM15, quantas vagas vão ficar sem ocupante, e o que se faz com elas?" | D | Número certo e destino certo, lidos na tela |
| 6 | "No SIM16, o seu trabalho acabou? Se não, o que falta e de quem é?" | E | Diz que falta a exportação, que é do setor, e que a ordem vazia é formalidade |

**O que registrar, por tarefa:**

- **Ajuda:** 0 nenhuma · 1 pediu confirmação · 2 pediu o caminho · 3 o observador fez.
- **Hesitação:** cada pausa acima de 30 segundos, com a tela em que ocorreu.
- **Interpretação errada:** o que a pessoa disse que a tela significava, ao pé da letra.
- **Erro de decisão:** ato que ela faria e não cabia, ou ato devido que ela não faria.
- **Abandono:** onde desistiu ou disse "aqui eu perguntaria a alguém".
- **Termo que travou:** a palavra exata.

**Leitura do resultado.** Uma tarefa conta como autônoma quando a pessoa chega ao acerto com ajuda
0 ou 1 e sem erro de decisão. O GPS conduz, no sentido desta auditoria, quando ao menos duas das
três pessoas são autônomas em cinco das seis tarefas. Abaixo disso, as tarefas que falharam dizem
qual das três intervenções vem primeiro — e é essa a utilidade do teste, mais do que a nota.

## Ambiente

Banco `ps_autonomia` no PostgreSQL local, servidor na porta 8196 com
`INTERFACE_SELETOR_IDENTIDADE=true` e `SORTEIO_FONTE_DE_DEMONSTRACAO=true`. A única escrita feita
pela interface foi o corte da ampla concorrência do SIM09. Todos os nomes são fictícios.
