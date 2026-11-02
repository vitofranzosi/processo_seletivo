# Cronogramas dos Editais: diagnóstico, POCs e recomendação

**01/11/2026 · estudo exploratório · revisão do estudo do mesmo dia.** Nada da aplicação foi
alterado. A conclusão é heurística: apoia-se no código, em medições automatizadas e em capturas,
não em sessões com usuários.

> **Composição proposta, ainda não testada.** No **Mês**, a lista "Períodos previstos em ‹mês›"
> dá lugar a **L**, a mesma lista reorganizada por Edital, com pontuais, horas e continuidade
> escritas. A comparação entre Editais vai para uma **terceira aba da Agenda, com C+** — a faixa
> por Edital com o nome de cada evento —, entregue depois de L e só se o uso pedir. **Próximos
> marcos** fica como está (`D-003`). A e B, descartados como telas; C revisada e G, referências.
> O ganho sobre a Agenda atual é estreito — simultaneidade e distribuição — e não está
> demonstrado. Primeiro teste: **Atual × L**; a aba de C+, avaliada à parte.

## Por que este estudo foi refeito

A primeira versão, do mesmo dia, está em `doc/estudo-visualizacao-cronogramas-2026-11-01/`, sem
rastreamento git, no checkout principal. Quatro problemas mudavam a conclusão:

1. **A alternativa A desenhava o marco pontual no dia seguinte** sempre que o evento era depois do
   meio-dia: somava a fração do dia à meia coluna de centralização. A clareza temporal era o
   argumento central a favor de A.
2. **A densidade foi testada com doze cronogramas idênticos.** Doze barras iguais empilhadas não
   dizem como a tela se comporta com processos em fases diferentes.
3. **A `D-003` da spec 101 foi ignorada.** A recomendação de B para o celular disputava o lugar de
   uma visão que já existe, já é a do celular por decisão do usuário, e nunca foi comparada.
4. **A recomendação se contradizia.** Recusava duas apresentações por dispositivo pelo custo, e
   propunha três: A, a lista textual como alternativa, e B como modo escolhido.

E dois de processo: a terceira alternativa foi descartada sem ser construída, e a premissa de
"dezenas de editais simultâneos" não foi verificada.

## Diagnóstico

O que o primeiro estudo disse da implementação está correto e não se repete aqui por inteiro:
`interface/agenda.py::ler` lê os Editais publicados e encerrados do escopo, a versão consolidada
vigente no instante da leitura (`versoes_vigentes`) e as Retificações a vigorar; daí deriva, em
memória, `Marco` (o pontual, a abertura, o encerramento) e `Periodo` (o intervalo, dito uma vez).
Fase e espécie saem do backend. Três pontos que faltavam:

**A página já tem três camadas, e cada uma responde a perguntas diferentes.**

| Camada | Responde bem | Não responde |
|---|---|---|
| Grade do mês | onde há concentração de marcos (quantidade e destaque) e quantos períodos abrangem cada dia (FR-2669) | *quais* Editais, e a duração |
| Lista "Períodos previstos" | o intervalo exato de cada período | simultaneidade, duração relativa, a sequência de um Edital (os pontuais não estão nela) |
| "Próximos marcos" (D-003) | o que está em curso, **ordenado pelo término, com "encerra em N dias"**; o que acontece dia a dia nos próximos 7 ou 30 dias | o mês como um todo; a forma de cada cronograma |

A lacuna real é a da segunda linha. É ela que o estudo deve resolver, e não as outras duas.

**A spec 101 já adiou esta decisão.** A revisão de 29/10 registrou: barras atravessando as semanas
*na grade* continuam recusadas, e "a linha do tempo horizontal ficou para outra etapa". Uma faixa
abaixo da grade não contradiz a `D-002` — o período continua um intervalo só, e nada é criado por
dia —, mas é exatamente a etapa que ela deixou para depois, e pede spec própria.

**O volume justifica uma visão comparativa.** A numeração dos Editais do Cefor é sequencial no ano:
o 173/2025 existe; em 2026, o 14 é de 05/02, o 28 de 07/04, o 69 de 03/07, o 78 de 05/08 e o 89 de
24/09 — cerca de dez por mês. Os cronogramas de amostra duram de três semanas (chamada com sorteio,
69/2026) a dois meses e meio (seleção de pessoal, 89/2026). Dez por mês, vivendo de um a dois
meses e meio, dão algo entre **10 e 25 Editais com cronograma vivo ao mesmo tempo**. É estimativa
grosseira — nem todo número é processo seletivo, e nem todo processo entraria no GPS no piloto —, a
confirmar com quem coordena. O cenário de 25 Editais deste estudo está nessa faixa, e não acima.

## Dados

- **7 Editais do banco `ps_demo_101`** (101 a 107), a demonstração existente da agenda, com a
  Retificação real do 106 (prova de 21/11 para 23/11, vigente em 04/11).
- **18 casos de teste (T01 a T18)**, só em memória, nunca gravados. T17 e T18 repetem o cronograma do T08, para o caso de cronogramas idênticos. Têm a **forma** de cronogramas
  públicos do Cefor — quais eventos, em que ordem, com que duração — e datas deslocadas para
  setembro a dezembro, de modo que novembro tenha processos começando, no meio e terminando:
  seleção de pessoal (forma do 89/2026, sete eventos), chamada com sorteio (69 e 78/2026, seis),
  curso com inscrição longa (28/2026, cinco), inscrição de um dia (72/2026: abre às 07h20, fecha às
  9h do dia seguinte) e um cadastro sem término declarado. T02 tem uma descrição de 120 caracteres.
- Os casos passam pelas mesmas `marcos_do_conteudo` e `periodos_do_conteudo` da agenda, e as telas
  atuais foram renderizadas pelo próprio `agenda.ler` e pelos templates de produção, com os 23
  Editais — a comparação é contra a interface real, e não contra uma imitação.

## Segunda rodada: o parecer externo sobre C

Um parecer externo, feito sobre o briefing em PDF e sobre capturas da agenda real, concordou com C
como direção e apontou problemas de legibilidade. A maior parte procedia, inclusive contra este
relatório:

- **"Tudo o que A mostra, C mostra na linha ou ao abrir" era um argumento fraco.** Informação atrás
  de um clique não se compara de relance. A primeira C também deixava os losangos sem nome e
  cortava a situação ("Em curso: … ·…") justamente na próxima etapa.
- **Dois marcos no mesmo dia viravam um losango só** (T07, sorteio e resultado em 01/11). A
  primeira versão deste relatório registrou só os "dias vizinhos que se tocam".
- **A captura das inscrições em curso dependia do filtro por fase**, que o MVP adiava. E a tela não
  dizia se o filtro escolhia Editais ou escondia eventos.
- **A comparação de altura misturava escopos**: C como painel, contra calendário mais lista.
- A legenda era um parágrafo; "›" não distinguia "continua em dezembro" de "sem término"; a data
  da situação não ficava separada do mês exibido; a hora do prazo não aparecia.

O que **não** foi adotado: *nomes curtos para exibição*. A descrição do evento é texto do Edital
publicado; encurtá-la pede campo novo (persistência que o estudo não cria) ou abreviação automática
(o sistema reescrevendo o ato). O nome sai inteiro, fora da barra, com quebra de linha. E *régua
com rolagem horizontal* na visão geral repete o que derrubou a primeira A no celular.

## As alternativas

Todas leem a mesma projeção e usam o mesmo motor de régua: **colunas em porcentagem, por dia**. Um
período vai da coluna do primeiro dia à do último, inclusive — a pertinência de `Periodo.abrange`,
a mesma que dá o número da grade. Um pontual fica no centro da coluna do seu dia. A primeira A
fixava 960 px de régua e deixava 51 px visíveis no celular; aqui a régua cabe em qualquer largura.

**C — Uma faixa por Edital, revisada.** **Fechada**, uma linha por Edital: número, processo e a
situação em até duas linhas, com hora — "Em curso: Período de inscrições — encerra 06/11 às 18h" e
"Próximo: Análise documental — começa 08/11 às 9h" —, um controle que diz o que faz ("Ver os 4
eventos do mês" / "Ocultar os eventos"), e à direita a régua com os eventos do mês. Pontuais no
mesmo dia ou em dias vizinhos vão a faixas próprias. **Aberta**, uma linha por evento daquele
Edital, alinhada à mesma régua — é a linha de A: nome inteiro, datas com hora, fase e, quando é o
caso, "começou em 24/10", "continua até 06/12" ou "sem término definido". Ordem padrão: pelo
próximo marco.
[Desktop](capturas/c-desktop.jpg) · [aberto](capturas/c-aberto-desktop.jpg) ·
[celular](capturas/c-celular.jpg) · [aberto no celular](capturas/c-aberto-celular.jpg) ·
[dezembro](capturas/c-dezembro.jpg).

**Agenda completa com C.** A grade real do produto, renderizada pelo template de produção, e C no
lugar da lista, com título próprio ("Cronogramas dos Editais em novembro") e um atalho do topo da
página. [Desktop](capturas/agenda-completa-desktop.jpg) ·
[celular](capturas/agenda-completa-celular.jpg).

**A — Gantt por evento.** Uma linha por evento, agrupadas por Edital.
[Desktop](capturas/a-desktop.jpg) · [celular](capturas/a-celular.jpg).

**B — Timeline em cartões.** Um cartão por Edital, eventos em lista vertical, duração e distância
até o seguinte em texto, sem a faixa de largura fixa da primeira versão.
[Desktop](capturas/b-desktop.jpg) · [celular](capturas/b-celular.jpg).

**Atual.** [Mês, 25 Editais](capturas/atual-mes-denso-desktop.jpg) ·
[Próximos, 25 Editais, celular](capturas/atual-proximos-denso-celular.jpg).

**Legenda.** Quatro amostras — período, evento pontual, dia da situação, continua em outro mês — e
uma linha secundária: o preenchimento acompanha a fase, que também vem escrita em cada linha.

**Filtros.** Espécie e fase, e o alcance explícito: "os Editais, com todos os eventos" (padrão) ou
"só os eventos filtrados". A contagem diz qual está valendo.
[Inscrições em curso, Editais inteiros](capturas/c-inscricoes-em-curso.jpg) ·
[só os eventos](capturas/c-inscricoes-so-eventos.jpg).

## Medições

Novembro, 25 Editais, 80 eventos, situação em 01/11 às 12h. Medidas em `capturas/medidas.json`,
por `capturar.py`. Nenhuma tela rola de lado em nenhuma largura.

**A comparação que decide: a Agenda inteira, do título do calendário ao fim.**

| Página | Desktop 1440 | Celular 375 |
|---|---:|---:|
| Atual: calendário + lista de períodos | 2.780 px | 4.929 px |
| **Calendário + C** | **3.828 px** (+38%) | **5.779 px** (+17%) |
| Calendário + C+ (nomes visíveis) | 3.744 px (+35%) | 11.654 px (+136%) |

**C revisada é mais alta que a lista que substitui.** É o preço da legibilidade que o parecer
pediu: a situação em duas linhas, com hora, e o controle de abertura ocupam três a quatro linhas
por Edital, contra uma linha por período na lista. A primeira C media 1.620 px de painel, com
23 Editais; a revisada, 2.316 px com os mesmos 23 e 2.531 px com os 25 de agora. A troca é de altura por compreensão — a lista atual é curta porque não diz a
sequência nem a simultaneidade —, e só tarefas com usuários dizem se compensa.

Os painéis isolados, para comparar as alternativas entre si:

| Painel | Desktop | Notebook | Tablet | Celular | Focos (fechado) | px por dia |
|---|---:|---:|---:|---:|---:|---|
| **C** revisada | 2.531 | 2.967 | 3.189 | 4.252 | 25 | 33,4 → 10,6 |
| C+ nomes visíveis | 2.312 | 2.599 | 2.898 | 8.636 | 68 | 33,4 → 10,6 |
| L lista melhorada | 4.959 | 4.959 | 5.068 | 8.072 | 68 | — |
| A Gantt por evento | 6.091 | 6.830 | 7.761 | 9.899 | 105 | 33,4 → 10,6 |
| B cartões | 3.370 | 4.184 | 5.679 | 9.631 | 80 | — |

Os 23 focos de C são de linhas fechadas: abrir um Edital acrescenta os eventos dele. Menos focos
não é, sozinho, menos trabalho para consultar etapas.

**Geometria verificada.** `capturar.py` confere cada losango e cada barra visível contra a célula
da régua do mesmo dia — em C fechada, em C aberta, em A, nas quatro larguras e em outubro,
novembro e dezembro: 26 conferências, com C+, nenhuma fora da coluna, console limpo. Na revisão, a
conferência **pegou um defeito**: o recuo das linhas abertas deslocava a trilha delas em relação à
régua do cabeçalho. O recuo saiu; a indicação de que a linha pertence ao Edital ficou no "↳" e no
fundo. Isto é correção geométrica; a facilidade de leitura continua por medir.

## Terceira rodada: nomes visíveis (C+) e o estudo D–G

Um terceiro estudo, `doc/estudo-organizacao-agenda-2026-11-01/` (sem commit, no checkout
principal), reabriu a organização da Agenda e propôs um mapa semanal por Edital, com o nome dos
eventos em cada célula (D, e G com o calendário recolhido). Ele recomendou testar G contra C
revisada e a Agenda atual. A crítica a esse estudo, registrada nesta sessão:

- **O mapa compra os nomes com repetição.** Nas capturas dele, os Editais 01, 91 e 901 a 903
  repetem o mesmo cartão em quatro semanas, e o término (22/11 contra 27/11) fica num texto
  pequeno. É o mecanismo que a `D-002` recusou, por semana em vez de por dia, e a própria tela
  precisa de um aviso permanente de que "mesma coluna não é simultaneidade".
- **O concorrente estava em desvantagem.** G foi comparado com a C revisada, que corta os nomes
  das barras. Nomes visíveis não exigem agrupar por semana.
- **Os dados não testam densidade nem o produto.** São 10 Editais e 19 eventos; quatro dos seis
  Editais dos prints são clones de demonstração; e, sem horário na transcrição, a tarefa de prazo
  tem um gabarito ("empate, hora indisponível") que o produto, que tem os instantes, não daria.
- **A consulta do dia já existe** (FR-2628) e responde a "o que continua numa semana sem
  marcos". E é essa consulta estendida à semana; F, Próximos marcos com um destaque. São
  melhorias de telas existentes, a decidir à parte.

**C+ é a resposta à primeira e à segunda crítica**: a faixa por Edital com o nome de cada evento
escrito **uma vez**, inteiro, sem abrir nada, sobre a mesma régua diária.

- O nome vai dentro da barra quando cabe; senão, acima dela, começando no início da barra ou
  terminando no fim quando passaria do mês. Rótulos que colidem descem para outra faixa. A
  disposição usa a largura real da trilha e de cada nome, e se refaz quando a janela muda.
- **Cronogramas idênticos viram uma linha só** — "Editais 901, 902 e 903/2026 · 3 Editais com o
  mesmo cronograma" —, cada um com seu detalhe. Decisão do usuário, 01/11/2026, depois de ver o
  esboço. É regra de apresentação nova: nenhum estudo anterior a propunha.
- No celular a régua tem 10 px por dia e os nomes não cabem nela: cada evento vira uma linha,
  como C aberta, sem recolher.
- Cada nome é um botão com nome, datas com hora e fase; o teclado chega a todos os eventos.

[Desktop, 25 Editais](capturas/n-desktop.jpg) · [celular](capturas/n-celular.jpg) ·
[Editais dos prints, 22/11](capturas/n-074-desktop.jpg) ·
[os mesmos, no celular](capturas/n-074-celular.jpg) · [dezembro](capturas/n-dezembro.jpg) ·
[Agenda completa com C+](capturas/agenda-completa-com-nomes-desktop.jpg).

**Os Editais dos prints, com horário.** O cenário `demo074` lê, somente leitura, o banco local
`ps_074_local`, que tem publicados os seis Editais que aparecem nos prints (01, 91, 901, 902, 903
e 92), com os mesmos nomes de evento. **As datas não são as do print**: as sementes geram as
datas a partir do dia em que rodam, e nenhum dos bancos locais conferidos reproduz as do print.
Servem pelo formato — o 92 tem dezessete eventos, alguns com mais de cento e cinquenta
caracteres, e 901 a 903 são idênticos — e pelos instantes, que a transcrição não tem.

**O que as medições dizem (25 Editais, novembro):**

| | Agenda inteira, desktop | Agenda inteira, celular | Focos |
|---|---:|---:|---:|
| Atual: calendário + lista | 2.780 | 4.929 | 33 |
| Calendário + C revisada | 3.828 (+38%) | 5.779 (+17%) | 25 + os abertos |
| Calendário + C+ | 3.744 (+35%) | 11.654 (+136%) | 68 |

No desktop, C+ mostra todos os nomes na mesma altura que C revisada — os rótulos acima das barras
ocupam o espaço que a situação em duas linhas já ocupava. **No celular, C+ custa mais que o dobro
da Agenda atual**: sem os nomes na régua, cada evento é uma linha. É o mesmo preço de A e B no
celular, e é onde C revisada, que recolhe, leva vantagem. A conferência geométrica pegou um
defeito novo: no celular, o recuo do contêiner somava-se ao das linhas e as deslocava da régua.

**Limitações de C+.** Um Edital com muitos eventos no mês ocupa muitas faixas (o 92, cinco). A
linha da situação atravessa os rótulos. A regra do rótulo é heurística: com muitos nomes longos,
as faixas crescem sem limite. O agrupamento depende de identidade exata — uma hora diferente
separa os Editais, e é o certo.

**Direção para o teste com usuários, ainda aberta:** **Atual × C+ × G**, nos mesmos dados com
instantes reais e com um cenário denso. C revisada fica como referência de recolhimento,
sobretudo no celular. E e F, em decisão separada, como melhorias da consulta do dia e de
Próximos marcos.

## Quarta rodada: a lista melhorada (L), o concorrente sem régua

Nenhum dos estudos tinha construído o concorrente mais barato das faixas: **a lista atual,
melhorada, sem régua**. L é isso. Um bloco por Edital, com a situação em texto e hora; os
eventos do mês em ordem de início, **períodos e pontuais juntos**; datas com hora; nome inteiro;
fase escrita; "começou em", "continua até" e "sem término definido" escritos; cronogramas
idênticos numa linha só, como em C+. Nada para aprender: é a lista de hoje, reorganizada.
L responde ao que o parecer apontava no print — "Período de inscrições" repetido, as etapas do 92
espalhadas entre outros Editais, a continuidade para dezembro sem destaque — **e não mostra
simultaneidade**, que é exatamente o que o teste precisa separar.

[Desktop, 25 Editais](capturas/l-desktop.jpg) · [celular](capturas/l-celular.jpg) ·
[Editais dos prints, 22/11](capturas/l-074-desktop.jpg) · [os mesmos, no celular](capturas/l-074-celular.jpg) ·
[Agenda completa com L](capturas/agenda-completa-lista-desktop.jpg).

| 25 Editais, novembro | Agenda inteira, desktop | Agenda inteira, celular | Focos |
|---|---:|---:|---:|
| Atual: calendário + lista | 2.780 | 4.929 | 33 |
| Calendário + C revisada | 3.828 (+38%) | 5.779 (+17%) | 25 + abertos |
| Calendário + C+ | 3.744 (+35%) | 11.654 (+136%) | 68 |
| Calendário + L | 6.187 (+123%) | 9.170 (+86%) | 68 |

**Resultado que contraria a hipótese de que L seria a opção enxuta.** No desktop, L é a mais
alta de todas — 2,1× o painel de C+ (4.959 contra 2.312 px). A régua é o que compacta: numa
faixa, oito eventos de um Edital cabem em duas ou três linhas; numa lista, são oito linhas. A
altura de L vem de mostrar os pontuais, que a lista atual não mostra (80 eventos contra cerca de
45 períodos), e de um cabeçalho por Edital. Recolher os eventos com data passada a encurtaria;
não foi construído, para não esconder parte da sequência sem teste. No celular, L fica entre C
revisada e C+.

**O que isso diz sobre a pergunta "houve melhoria?".** As capturas sugerem que L é a mais fácil
de ler para **um** Edital — a sequência do 92, com horas e fases, sai linha a linha — e a mais
difícil para **comparar** Editais, porque a simultaneidade continua em datas para cruzar de
cabeça. C+ é o oposto. A troca entre as duas é a pergunta central que sobrou, e só tarefas
respondem.

**Direção para o teste, ainda aberta, em duas comparações em vez de uma de quatro:**

1. **Atual × L × C+**, nos mesmos dados com instantes reais e com o cenário denso. Pergunta: a
   régua compensa o que custa? Se L empatar com C+ nas tarefas de comparação, L vence — é a
   mudança menor. Se C+ ganhar só em simultaneidade, pesar a frequência real dessa tarefa.
2. Se C+ ganhar, **C+ × G**: régua diária com nomes contra mapa semanal com nomes.

C revisada fica como referência de recolhimento no celular. E e F, em decisão separada.

## Composição proposta: L no Mês, C+ como aba à parte

Proposta do usuário em 01/11/2026, avaliada nesta sessão: **L sob o calendário, no lugar da
lista de períodos, e C+ numa visão própria**. É coerente com o que as rodadas encontraram — L
venceu na leitura de um Edital, C+ na comparação entre Editais —, e separar por tarefa, com a
pessoa escolhendo, é diferente da troca automática por dispositivo recusada antes, em que a mesma
informação mudava de forma sem ser pedida. Quatro condições:

1. **C+ como terceira aba da Agenda, e não como item novo no menu da gestão.** A Agenda já tem
   "Mês" e "Próximos marcos" (`D-003`). Uma aba "Linha do tempo" herda os mesmos filtros, a mesma
   navegação de mês e o mesmo escopo da unidade. Um item próprio no menu seria uma segunda porta
   para os mesmos dados, menos descobrível e com filtros que podem divergir.
2. **L primeiro; C+ depois, condicionada.** L é a mudança menor e não pede aprendizado. C+ traz o
   código mais delicado do estudo — a disposição dos rótulos, recalculada pela largura. Com equipe
   de duas ou três pessoas e o volume de Editais simultâneos ainda estimado, C+ só entra se o teste
   ou o uso mostrarem que comparar Editais é tarefa frequente. Sem essa condição, vira a visão a
   mais que serve para não escolher, contra o que o estudo D–G alertou.
3. **O custo de L sob o calendário continua.** A Agenda cresce +123% no desktop, e os pontuais
   aparecem duas vezes, na grade e na lista. O alívio mais simples, sem esconder nada do mês:
   recolher, em cada Edital, os eventos com data passada, dizendo quantos ("4 eventos
   anteriores"). Não foi construído nem medido.
4. **Duas specs, em sequência.** L muda o conteúdo da lista da 101 — passa a ter pontuais e a
   agrupar cronogramas idênticos, regra de apresentação nova — e cabe numa spec curta. C+ é a
   linha do tempo horizontal que a 101 deixou "para outra etapa", e sua spec espera a evidência.

**Teste que decorre dessa composição**, mais simples que os anteriores: **Atual × L**, para
validar a primeira entrega, com as tarefas de leitura e de prazo; e a **aba de C+ avaliada à
parte**, só com quem acompanha vários Editais, nas tarefas de simultaneidade e distribuição. G e
C revisada ficam como referências, não como candidatos à primeira entrega.

Não é resultado: nenhuma das quatro condições foi testada com usuários.

## As perguntas do critério de sucesso

Avaliação pela leitura das capturas, não por tempo de tarefa medido.

| Pergunta | Melhor resposta hoje | C revisada | A | B |
|---|---|---|---|---|
| Quais Editais estão com inscrições abertas? | **Próximos**: bloco "em curso" | Linha "Em curso: …" em cada Edital; ou filtro de fase | Igual, em mais linhas | Ler os cartões |
| Quais etapas ocorrem simultaneamente? | Nenhuma: a lista exige comparar datas | **Alinhamento vertical na régua** | Idem, em 5.200 px | Não responde |
| Qual Edital está próximo de encerrar inscrições? | **Próximos**: "encerra em N dias" | Ordem pelo próximo marco + "encerra dd/mm às hh" | Exige varrer | Exige ler |
| Como se distribuem as etapas de um Edital? | Partida entre lista e grade | **Uma linha; aberta, um evento por linha, na régua** | Um bloco de 3 a 7 linhas | Lista sem escala |
| O que começa na próxima semana? | **Próximos 7 dias** | Colunas 2 a 8; "Próximo: … começa" | Idem | Ler |
| Quais períodos atravessam meses? | Lista (datas completas) | ‹ › na barra; "continua até 06/12" na linha aberta | Idem | Texto |
| Onde há concentração? | **Grade** (marcos e indicador de períodos) | Colunas carregadas | Não cabe num quadro | Não responde |

C é a única que responde por forma às duas perguntas que nenhuma camada atual responde —
simultaneidade e distribuição. Três das sete já têm resposta melhor em Próximos e na grade, e por
isso **C entra no lugar da lista de períodos, e não no lugar da página**. Concentração de marcos
num dia (grade) e períodos que abrangem um dia (indicador, barras) são fenômenos diferentes, e
nenhum dos dois mede carga de trabalho.

## Comparação

| Dimensão | C revisada | A Gantt por evento | B cartões |
|---|---|---|---|
| Clareza temporal | Régua comum; hora do prazo em texto | Igual a C | Datas em texto; sem escala |
| Duração | Comprimento da barra | Comprimento da barra | "N dias" em texto |
| Comparabilidade | Editais vizinhos na mesma régua; cerca de 8 por quadro no desktop | 3 a 4 por quadro | Fraca: altura não é data |
| Identificação dos eventos | Fechada: só o em curso e o próximo, e os nomes que cabem na barra; aberta: todos | Todos, sempre | Todos, sempre |
| Densidade | Mais alta que a lista atual (+38% na Agenda) | 2,4× C | 1,3× C |
| Responsividade | Mesma estrutura; identidade sobe | Idem, com 2× a altura de C | Refluxo natural |
| Complexidade | Média: faixas, régua, duas linhas de situação | Média | Baixa |

**Limitações de C que continuam.** Fechada, o nome dos pontuais e das barras curtas não aparece —
é preciso abrir; isso é deliberado, mas é custo. No celular a régua tem 10,6 px por dia: serve à
visão geral, não à leitura de um dia exato. O desenho é `aria-hidden`: o leitor de tela lê a
situação de cada Edital e, ao abrir, cada evento com datas; não há ensaio real com leitor.

**Por que não A como painel.** A identifica todos os eventos sem clique — essa vantagem é real —,
mas afasta os Editais entre si (3 a 4 por quadro) e custa 2,4× a altura de C. C passou a usar a
linha de A ao abrir: a qualidade de A fica, no detalhe de um Edital.

**Por que não B.** No celular, B disputa o papel que a `D-003` deu a Próximos e responde pior às
perguntas de prazo. No desktop, a sequência que B oferece é a de C aberta, com a régua a mais.

**Por que não combinar por dispositivo.** C reflui sozinha. A primeira A só precisava de B no
celular porque fixava a largura em pixels.

## Restrições para quem for especificar

- **Spec própria.** A 101 adiou a linha do tempo horizontal para "outra etapa"; esta é ela.
- **CSP.** A gestão recusa `style=""` (091/092). A POC posiciona pelo CSSOM em JavaScript, o que a
  CSP permite; o produto **não deveria** depender disso. Uma trilha em `display:grid` com
  `grid-column: <início> / span <dias>` faz o mesmo só com classes — 31 de início e 31 de extensão
  na folha da agenda — e funciona sem JavaScript, renderizada no servidor.
- **A linha aberta precisa da mesma grade que o cabeçalho.** Qualquer recuo desloca a trilha — a
  própria POC errou nisso. A conferência geométrica do `capturar.py` vale como teste de regressão.
- **Pertinência única.** A barra deve usar `Periodo.abrange`, para que o comprimento da barra e o
  número da grade não tenham como divergir — a lógica do `SC-959`.
- **Faixas.** Períodos que se sobrepõem, e pontuais no mesmo dia ou vizinhos, vão a faixas
  distintas; o empacotamento é uma função pura, testável, no backend.
- **Data da situação.** No produto é o instante da leitura; ao navegar para outro mês, a tela deve
  dizer "Situação hoje" separado de "Período exibido".
- **Contraste não textual (WCAG 1.4.11).** A barra de data passada precisa de borda: o cinza claro
  sozinho dava 1,4:1 contra o branco. Corrigido na POC com `#767676` (4,5:1).
- **Sem estado novo.** "Em curso", "ainda não começou" e "data passada" são os rótulos da 101.
  Nada de atraso, conclusão ou percentual.
- **Consultas.** C não acrescenta consulta ao orçamento fixo da agenda (`FR-2646`): usa os
  `Periodo` e `Marco` que `ler` já produz.

## MVP proposto, a decidir

Escrito antes da composição L + aba C+, para C revisada; vale como lista de itens da futura aba. Se a aba for de C+, mudam três itens: o nome de cada evento na
régua em vez do controle de abertura, o agrupamento de cronogramas idênticos, e, no celular, a
lista de eventos por Edital sempre aberta.

Entra: C no lugar da lista de períodos do mês, com título próprio e atalho do topo da página;
régua diária com fim de semana e dia da situação; barras por `abrange`, pontuais no centro do dia
e em faixas próprias quando coincidem; situação em texto com hora; "Período exibido" separado de
"Situação hoje"; controle de abertura que diz o que faz; linha por evento ao abrir, com nome
inteiro, datas com hora e continuidade escrita; ordem pelo próximo marco; legenda por amostras;
filtros de Edital, espécie **e fase** — a fase vem pronta do backend e o custo é pequeno —, com o
alcance do filtro explícito.

Fica para depois, se as tarefas medidas pedirem: ordem alternativa, rótulo dos pontuais na régua
fechada, escala semanal, régua ampliada no detalhe de um Edital.

Descartado: A e B como telas próprias; troca de apresentação por dispositivo; nomes curtos de
exibição; agrupamento de cronogramas semelhantes; arrastar, editar, dependências, percentual.

## O que este estudo não fez

Não houve sessão com usuários, ensaio com leitor de tela, nem ampliação real a 200% e 400%. O
volume de Editais simultâneos é estimado pela numeração. A grade da página completa foi extraída
dos fragmentos já renderizados (o PostgreSQL local estava parado na segunda rodada); o exportador
grava a mesma coisa quando o banco está disponível.

**Próximo passo sugerido, antes de qualquer spec:** tarefas com duas ou três pessoas que acompanham
Editais, na **Agenda atual** e na **Agenda com C**, no desktop e no celular — de preferência sobre
a agenda real, com as tarefas do parecer: encontrar a inscrição que termina primeiro; comparar
quatro Editais com inscrições simultâneas; localizar o recurso de um Edital; identificar a etapa
que avança para o mês seguinte; distinguir "continua" de "sem término". Registrar acerto, tempo,
aberturas e consultas à legenda.
