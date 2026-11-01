# Cronogramas dos Editais: diagnóstico, três POCs e recomendação

**01/11/2026 · estudo exploratório · revisão do estudo do mesmo dia.** Nada da aplicação foi
alterado. A conclusão é heurística: apoia-se no código, em medições automatizadas e em capturas,
não em sessões com usuários.

> **Recomendação.** Substituir a lista "Períodos previstos em ‹mês›", abaixo da grade, por **uma
> faixa por Edital** (alternativa **C**): uma linha por Edital, numa régua diária comum, com a
> situação na referência em texto e a sequência completa ao abrir. A mesma estrutura serve ao
> desktop e ao celular. **Manter "Próximos marcos" como está** — ela já responde, melhor que
> qualquer das três, a "quem encerra inscrições primeiro" e "o que começa nesta semana", e a
> `D-003` já a fez a forma do celular. **Descartar A e B** como telas próprias.

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
confirmar com quem coordena. O cenário de 23 Editais deste estudo está nessa faixa, e não acima.

## Dados

- **7 Editais do banco `ps_demo_101`** (101 a 107), a demonstração existente da agenda, com a
  Retificação real do 106 (prova de 21/11 para 23/11, vigente em 04/11).
- **16 casos de teste (T01 a T16)**, só em memória, nunca gravados. Têm a **forma** de cronogramas
  públicos do Cefor — quais eventos, em que ordem, com que duração — e datas deslocadas para
  setembro a dezembro, de modo que novembro tenha processos começando, no meio e terminando:
  seleção de pessoal (forma do 89/2026, sete eventos), chamada com sorteio (69 e 78/2026, seis),
  curso com inscrição longa (28/2026, cinco), inscrição de um dia (72/2026: abre às 07h20, fecha às
  9h do dia seguinte) e um cadastro sem término declarado. T02 tem uma descrição de 120 caracteres.
- Os casos passam pelas mesmas `marcos_do_conteudo` e `periodos_do_conteudo` da agenda, e as telas
  atuais foram renderizadas pelo próprio `agenda.ler` e pelos templates de produção, com os 23
  Editais — a comparação é contra a interface real, e não contra uma imitação.

## As três alternativas

Todas leem a mesma projeção e usam o mesmo motor de régua: **colunas em porcentagem, por dia**. Um
período vai da coluna do primeiro dia à do último, inclusive — a pertinência de `Periodo.abrange`,
a mesma que dá o número da grade. Um pontual fica no centro da coluna do seu dia. A primeira A
fixava 960 px de régua e deixava 51 px visíveis no celular; aqui a régua cabe em qualquer largura.

**C — Uma faixa por Edital** (nova). Uma linha por Edital: à esquerda, número, processo e a
situação na referência em uma linha ("Em curso: Período de inscrições, até 06/11 · Próximo:
Análise documental, 08/11"); à direita, todos os eventos do mês na régua — períodos como barras com
o nome dentro, empilhados em faixas quando se sobrepõem; pontuais como losangos. Ao abrir, a
sequência completa em texto, com datas, fase e o botão de detalhe. Ordem padrão: pelo próximo
marco (o término do período em curso ou o próximo início, o que vier antes).
[Desktop](capturas/c-desktop.jpg) · [celular](capturas/c-celular.jpg) ·
[aberto no celular](capturas/c-aberto-celular.jpg) · [dezembro](capturas/c-dezembro.jpg).

**A — Gantt por evento.** Uma linha por evento, agrupadas por Edital.
[Desktop](capturas/a-desktop.jpg) · [celular](capturas/a-celular.jpg).

**B — Timeline em cartões.** Um cartão por Edital, eventos em lista vertical, duração e distância
até o seguinte em texto. Sem a faixa horizontal de largura fixa da primeira versão, que parecia
proporcional e não era. [Desktop](capturas/b-desktop.jpg) · [celular](capturas/b-celular.jpg).

**Atual.** [Mês, 23 Editais](capturas/atual-mes-denso-desktop.jpg) ·
[Próximos, 23 Editais, celular](capturas/atual-proximos-denso-celular.jpg).

## Medições

Novembro, 23 Editais, 68 eventos, referência 01/11 às 12h. Altura é a do painel, em px; foco é
quantos pontos o Tab atravessa até o fim da lista. Nenhuma das telas rola de lado em nenhuma das
quatro larguras. Medidas em `capturas/medidas.json`, por `capturar.py`.

| Tela | Desktop 1440 | Notebook 1024 | Tablet 768 | Celular 375 | Focos | px por dia (desktop → celular) |
|---|---:|---:|---:|---:|---:|---|
| **C** faixa por Edital | **1.620** | 1.620 | 1.620 | **2.655** | **23** | 36,6 → 10,6 |
| A Gantt por evento | 4.898 | 4.898 | 4.940 | 7.985 | 91 | 36,6 → 10,6 |
| B cartões | 2.978 | 3.742 | 5.044 | 8.362 | 68 | — |
| Atual · Mês (grade + lista) | 2.732 | — | — | 4.700 | 33 | — |
| Atual · Próximos 7 dias | 3.701 | — | — | 5.131 | 44 | — |

C usa um terço da altura de A e metade da de B no desktop, e um terço das duas no celular. A
diferença não é de compactação à custa de informação: a linha de C diz a situação do Edital em
texto e mostra todos os eventos do mês; o nome dos pontuais é o que fica para o clique.

**O defeito do marco foi verificado, e não só corrigido.** `capturar.py` confere a posição de cada
losango e de cada barra contra a célula da régua do mesmo dia, em C e A, nas quatro larguras e em
outubro, novembro e dezembro: 15 conferências, 0 fora da coluna. O console ficou limpo em todas as
páginas.

## As perguntas do critério de sucesso

Avaliação pela leitura das capturas, não por tempo de tarefa medido.

| Pergunta | Melhor resposta hoje | C | A | B |
|---|---|---|---|---|
| Quais Editais estão com inscrições abertas? | **Próximos**: bloco "em curso", em texto | Filtro *inscrições + em curso*: [8 linhas ordenadas pelo término](capturas/c-inscricoes-em-curso.jpg) | Igual a C, uma linha por evento | Ler os cartões |
| Quais etapas ocorrem simultaneamente? | Nenhuma: a lista exige comparar datas | **Alinhamento vertical na régua** | Idem, mas espalhado em 4.900 px | Não responde |
| Qual Edital está próximo de encerrar inscrições? | **Próximos**: "encerra em N dias" | Ordem pelo próximo marco + "até dd/mm" | Exige varrer | Exige ler |
| Como se distribuem as etapas de um Edital? | Partida entre lista e grade | **Uma linha** | Um bloco de 3 a 7 linhas | Lista vertical, sem escala |
| O que começa na próxima semana? | **Próximos 7 dias** | Colunas 2 a 8 | Idem, com mais rolagem | Ler |
| Quais períodos atravessam meses? | Lista (datas completas) | ‹ › na borda da barra | Idem | Texto |
| Onde há concentração? | **Grade** (marcos e indicador de períodos) | Colunas carregadas, visíveis num quadro | Não cabe num quadro | Não responde |

Dois resultados. C é a única que responde por forma às duas perguntas que nenhuma camada atual
responde — simultaneidade e distribuição. E três das sete já têm resposta melhor em Próximos e na
grade: uma visão nova não precisa competir com elas, e por isso **C entra no lugar da lista de
períodos, e não no lugar da página**.

## Comparação

| Dimensão | C faixa por Edital | A Gantt por evento | B cartões |
|---|---|---|---|
| Clareza temporal | Régua comum, dia exato no losango e na borda da barra | Igual a C | Datas em texto; sem escala |
| Duração | Comprimento da barra | Comprimento da barra | "N dias" em texto |
| Comparabilidade | **Num quadro** cabem 12 a 14 Editais | 3 a 4 Editais por quadro | Fraca: altura não é data |
| Progressão de um Edital | Uma linha; sequência em texto ao abrir | Um bloco | Boa, mas por leitura |
| Densidade | 1.620 px para 23 Editais | 4.898 px | 2.978 px |
| Esforço cognitivo | Ler a régua; a situação vem em texto | Ler a régua, em mais linhas | Ler tudo |
| Responsividade | Mesma estrutura; identidade sobe e a régua usa a largura toda | Idem, com 3× a altura | Refluxo natural |
| Teclado | 23 focos; Enter abre a sequência | 91 focos | 68 focos |
| Complexidade | Média-baixa (ver abaixo) | Média | Baixa |
| Coerência com o GPS | Lista de linhas, tokens e estados existentes | Convenção de Gantt | Cartões existentes |

**Limitações de C.** No celular a régua tem 10,6 px por dia: serve à visão geral, e o nome do
evento curto some na barra (o texto da linha e a sequência aberta o dizem). Dois pontuais em dias
vizinhos se tocam (104/2026, 14 e 15/11). A situação é sempre a da referência, mesmo navegando para
dezembro, e o cabeçalho da coluna precisa dizê-lo. O desenho é `aria-hidden`: quem usa leitor de
tela ouve a situação de cada Edital, mas precisa abrir a linha para ouvir os eventos — o mesmo que
quem enxerga faz para ler o nome de um pontual.

**Por que não A.** Tudo o que A mostra, C mostra na linha ou ao abrir; o que A acrescenta é uma
linha por evento sempre aberta, que custa três vezes a altura e quatro vezes os focos de teclado e
tira a comparação do quadro.

**Por que não B.** No celular, B disputa o papel que a `D-003` deu a Próximos e responde pior às
perguntas de prazo. No desktop, a sequência de um Edital que B oferece é a mesma que C mostra ao
abrir a linha. Uma terceira apresentação do mesmo dado sem pergunta própria é custo sem retorno.

**Por que não combinar por dispositivo.** C não precisa: a mesma marcação reflui. A primeira A só
precisava de B no celular porque fixava a largura em pixels.

## Restrições para quem for especificar

- **CSP.** A gestão recusa `style=""` (091/092). A POC posiciona pelo CSSOM em JavaScript, o que a
  CSP permite; o produto **não deveria** depender disso. Uma trilha em `display:grid` com
  `grid-column: <início> / span <dias>` faz o mesmo só com classes — 31 de início e 31 de extensão
  na folha da agenda — e funciona sem JavaScript, renderizada no servidor.
- **Pertinência única.** A barra deve usar `Periodo.abrange`, para que o comprimento da barra e o
  número da grade não tenham como divergir — a lógica do `SC-959`.
- **Faixas.** Períodos que se sobrepõem no mesmo Edital vão a faixas distintas; o empacotamento é
  uma função pura, testável, no backend.
- **Contraste não textual (WCAG 1.4.11).** A barra de data passada precisa de borda: o cinza
  claro sozinho dava 1,4:1 contra o branco. Corrigido na POC com `#767676` (4,5:1).
- **Sem estado novo.** "Em curso", "ainda não começou" e "data passada" são os rótulos da 101.
  Nada de atraso, conclusão ou percentual.
- **Consultas.** O orçamento de consultas da agenda é fixo
  (`FR-2646`); C não acrescenta consulta, porque usa os `Periodo` e `Marco` que `ler` já produz.

## MVP proposto, a decidir

Entra: a faixa por Edital no lugar da lista de períodos do mês; régua diária com fim de semana e
dia de referência; barras por `abrange` e pontuais no centro do dia; ‹ › para o que continua em
outro mês e barra aberta para o período sem término; situação na referência em texto; ordem pelo
próximo marco; sequência textual ao abrir, com os links que a lista já tem (Edital e cronograma
publicado); os filtros existentes (Edital e espécie).

Fica para depois, se as tarefas medidas pedirem: filtro por fase, ordem alternativa, rótulo de
pontuais na régua, escala semanal.

Descartado: A e B como telas próprias; troca de apresentação por dispositivo; agrupamento de
cronogramas semelhantes; arrastar, editar, dependências, percentual de execução.

## O que este estudo não fez

Não houve sessão com usuários, ensaio com leitor de tela, nem ampliação real a 200% e 400% (o
celular de 375 px é o mais próximo do refluxo a 400%). O volume de Editais simultâneos é estimado
pela numeração, não medido. Próximo passo sugerido, antes de qualquer spec: as sete perguntas acima
como tarefas, com duas ou três pessoas que acompanham editais, comparando **a página atual** com
**a página atual com C no lugar da lista** — no desktop e no celular.
