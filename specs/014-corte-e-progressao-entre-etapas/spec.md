# Feature Specification: Corte e Progressão entre Etapas

**Feature Branch**: `claude/spec-014-corte-progressao-b8aa7a`

> **A numeração é `014` porque veio de `--number 14`**, e não da próxima pasta em `specs/` — que
> seria a `026`. O número estava reservado desde o encadeamento aprovado em 10/09/2026, e a
> varredura de 11/09 confirmou que nenhuma das catorze worktrees carrega uma `014`.

> **Os identificadores continuam a faixa global.** Teto medido em todas as worktrees antes de
> escrever — `FR-177`, `SC-054`, `UX-023` —, e esta spec abre em `FR-178`, `SC-055`, `UX-024`. As
> **decisões** reiniciam em `D-001`, porque são lidas dentro da feature que as produziu; decisão de
> outra feature é citada aqui **pelo que ela diz**, nunca pelo número, que apontaria para o nada.

**Created**: 2026-09-11

**Status**: Draft

**Input**: a proposta de próxima feature apresentada pelo usuário em 11/09/2026, lastreada na
avaliação de capacidade de `doc/avaliacao-de-capacidade-editais-2026-09-11.md`. Duas decisões
normativas foram fechadas pelo usuário na abertura desta spec, e entram abaixo **pelo texto delas**:
o desfecho do empate que atravessa o corte, e a fronteira com a `016`.

> **A frase que governa:** a partir da ordem vigente e da regra publicada, o sistema determina de
> forma reproduzível **quem progride** para a Etapa seguinte — preservando quem ficou fora, a causa
> do corte e o efeito de um resultado posteriormente superado.

> **E a frase que mantém o corte:** esta feature **seleciona**. Ela não ocupa vaga, não apura
> déficit, não convoca e **não afirma que as vagas foram preenchidas**.

---

## 1. O achado que organiza a feature

**O sistema produz ordem e não a transforma em universo.** De um lado, o ato de ordenação emitido é
imutável, tem universo declarado, posição com causa legível e a modalidade de cada participante — e
existe tanto computado por Etapas quanto constituído por sorteio. Do outro, a participação na Etapa
seguinte é derivada dos Resultados vigentes: eliminada em qualquer Etapa anterior fica fora de
todas; habilitada na imediatamente anterior entra na seguinte.

Entre os dois há um degrau que nenhum código executa. O Edital não manda a Etapa seguinte receber
**todos os habilitados**: ele manda receber uma **faixa** da ordem — os dez primeiros, os primeiros
até o número de vagas, os vinte suplentes. Hoje, quem consolidou e ordenou tem a lista certa na
tela e nenhuma operação que a transforme no conjunto da Etapa seguinte.

A consequência é de jornada, e alcança **quatro Editais da amostra**: o 14/2026, o 57/2026, o
28/2026 e o 77/2026. Nos quatro, o sistema conduz o certame até a ordem e para exatamente ali.

### 1.1 O corte real, nas palavras dos próprios Editais

```
14/2026,  6.1   "Serão convocados prioritariamente Professores Concursados do Ifes do Grupo 1
                 mais bem classificados na Prova de Títulos, até o limite máximo de 10 (dez)
                 candidatos por código de inscrição. Os candidatos não convocados para a
                 Entrevista, não serão classificados no resultado final."

77/2026,  6.3   "Após o sorteio, serão analisadas as documentações dos primeiros candidatos
                 sorteados até o número limite de vagas ofertadas por este edital. […] haverá a
                 análise da documentação do próximo candidato classificado, respeitando-se a
                 ordem do sorteio, até que se preencha o número total de vagas ofertadas"

77/2026,  6.10  "Haverá a análise dos documentos de até 30 (trinta) suplentes para chamada
                 imediata"

57/2026,  8.13  "Para cada código de vaga, haverá a análise dos documentos de até 20 (vinte)
                 suplentes para chamada imediata"

28/2026,  8.12  "Para cada código de vaga, haverá a análise dos documentos de até 15 (quinze)
                 suplentes"
```

Quatro Editais, três formas de dizer a mesma operação: **tome a ordem vigente e leve adiante uma
faixa dela**.

### 1.2 São duas formas de alvo, e nenhuma delas gera a outra

- **Alvo fixo.** `10` por código de inscrição no 14; `20`, `15` e `30` suplentes no 57, no 28 e no
  77. São números que o Edital publica e que não saem de conta nenhuma — 30 suplentes não é
  derivável de quantidade de vaga alguma.
- **Alvo derivado do quadro.** "até o número limite de vagas ofertadas", do 77, do 57 e do 28. A
  quantidade existe, é publicada e tem casa desde a `025`: é a linha do quadro de vagas do recorte.
  Ela **muda por Retificação**, e um corte emitido sob o quadro anterior tem de saber disso.

Tratar as duas como uma só custaria nos dois sentidos: derivar o alvo fixo de percentual sobre
vagas afirmaria norma que o Edital não publicou, e congelar o alvo derivado como número perderia o
vínculo que a Retificação do quadro precisa alcançar.

**E o recorte do corte não é o Edital.** O 14 corta "por código de inscrição" — que é o Perfil — e
prioriza por Grupo, que é a Modalidade. O 57 e o 28 cortam "para cada código de vaga" e por lista de
concorrência. É exatamente o recorte que o ato de ordenação já tem: Perfil, marco e lista.

### 1.3 Ficar fora do corte não é ser eliminado, e a diferença é do candidato

A cláusula 6.1 do 14 diz a consequência com todas as letras: *"Os candidatos não convocados para a
Entrevista, não serão classificados no resultado final."* Não é reprovação, não é indeferimento e
não é nota abaixo da mínima — é **não ter alcançado a faixa**, com a ordem inteira à vista para
provar por quê.

Gravar isso como Resultado de Etapa eliminaria a distinção e faria o registro afirmar algo falso: a
`018` já recusou, por escrito, declarar por Resultado a não participação numa Etapa que a pessoa
nunca fez. O corte precisa de ato próprio — e é o que a `D-005` fecha.

## 2. O que já existe, e que esta feature NÃO reconstrói

- **A ordem emitida, com universo declarado e sucessão.** Imutável, com posição, causa, empate
  residual e modalidade em cada linha, computada por Etapas ou constituída por sorteio. O corte
  **lê e não recalcula** — foi para isto que a `015` a deixou pronta.
- **A modalidade legível na posição.** A `015` a registrou explicitamente porque "a `014` é
  consciente de modalidade". O corte consome esse fato; não o verifica e não o decide.
- **O quadro de vagas por modalidade.** A `025` deu casa à quantidade por recorte, publicada,
  absoluta e alcançável por Retificação por identidade. O alvo derivado lê aquela linha.
- **A progressão derivada dos Resultados.** A `013` já decide quem participa da Etapa seguinte, com
  a regra assimétrica que ela fechou — eliminação alcança todas as Etapas posteriores, habilitação
  vale sobre a imediatamente anterior e só depois que ela começa a produzir Resultado. O corte é
  **mais uma condição sobre o mesmo conjunto**, resolvida no mesmo lugar e uma vez por listagem.
- **A obsolescência observável.** Comparar universo declarado contra o estado atual, marcar o
  vigente como obsoleto sem alterá-lo e exigir ato novo de quem tem autoridade é mecanismo pronto.
- **A guarda de publicação por reingresso.** Recurso deferido que devolve alguém ao fluxo já impede
  publicar o marco enquanto a pessoa não tiver Resultado. O corte herda a guarda e acrescenta a sua.
- **O endereçamento normativo estável, a trilha append-only, o resumo canônico e o catálogo de
  Retificação.** A regra do corte é conteúdo publicado como qualquer outro, e não inventa gramática.

## 3. Decisões fechadas antes do planejamento

As duas primeiras chegaram decididas pelo usuário em 11/09/2026, na abertura desta spec, e estão
aqui pelo texto delas. As demais fecham o que o recorte deixou em aberto.

### D-001 — O desfecho do empate que atravessa o corte é declarado, e a ausência impede

*Decisão do usuário, 11/09/2026.*

O alvo é dez, e do nono ao décimo segundo ninguém foi separado pelos critérios publicados. O corte
**não escolhe**. O desfecho é conteúdo publicado do marco, em duas grafias possíveis — *admite
excedente*, e entram todos os empatados na última posição; *alvo estrito*, e o corte para no alvo —,
e enquanto o Edital não declarar nenhuma delas a emissão é **impedida**, com motivo nomeado.

As duas saídas fáceis foram recusadas pela mesma razão. Admitir o excedente por padrão faria o
sistema publicar norma que ninguém escreveu, e entregaria à Etapa seguinte mais gente do que a
comissão dimensionou. Parar no alvo por padrão cortaria alguém por desempate que a norma não previu
— e a `015` já fixou que, esgotada a lista publicada de critérios, o sistema não ordena por UUID,
nome, horário de criação nem pela ordem em que o banco devolveu as linhas.

O custo é conhecido e aceito: mais um campo normativo no conteúdo publicado, com elevação canônica,
caminho de leitura da versão anterior, presença no documento e entrada no catálogo de Retificação.

### D-002 — A fronteira com a `016`: a `014` diz quem progride, a `016` diz quantas vagas faltam

*Decisão do usuário, 11/09/2026, pelo texto dela.*

> A `014` decide quem progride; a `016` decide quantas vagas foram ocupadas e quantas ainda faltam.
> A `014` pode selecionar a próxima faixa da ordem, respeitando o alvo e o limite de suplentes
> publicados. Quando o preenchimento depender dos resultados dessa análise, a `016` calcula o
> déficit e causa uma nova progressão pela `014`. A `014` não afirma sozinha que as vagas foram
> preenchidas, e a `016` não reimplementa a ordem nem escolhe candidatos.
>
> Aplicado às cláusulas:
>
> ```
> "analisar o próximo candidato da ordem"   → 014
> "quantas vagas ainda não foram ocupadas"  → 016
> "convocar e comunicar o candidato"        → 019
> ```
>
> Assim, o ciclo do 77 cruza a fronteira mais de uma vez:
>
> ```
> 014 progride → análise documental → 016 apura déficit
>        ↑                                  |
>        └──────── nova faixa necessária ──┘
> ```
>
> Isso preserva os donos de cada regra e evita usar "quantidade de habilitados" como sinônimo
> incorreto de "vagas ocupadas".

Três consequências diretas, e elas governam requisito por requisito abaixo:

1. **A faixa seguinte é uma capacidade desta feature**, e não da `016`: quem seleciona a próxima
   faixa da ordem é sempre a `014`, porque é ela que sabe ler ordem, alvo e excedente publicado.
2. **A causa da faixa seguinte vem de fora**, e o sistema nunca a emite por conta própria. Enquanto
   a `016` não existir, quem a declara é quem emite — ver `D-003`.
3. **Nenhuma tela, ato ou mensagem desta feature afirma vaga ocupada, vaga preenchida ou déficit.**
   O vocabulário é "progrediu", "dentro da faixa", "fora da faixa" — e a proibição é verificável.

### D-003 — Enquanto a `016` não existir, a causa da faixa seguinte é declarada por quem emite

É o que mantém a jornada completa hoje sem antecipar a `016`. A faixa seguinte exige **motivo
textual obrigatório** e a quantidade pretendida; o sistema confere que a regra publicada a admite e
que ela começa depois da última posição já alcançada, e não confere mais do que isso — porque não
tem, e não deve ter, como saber quantas vagas foram ocupadas.

*A redação anterior mandava conferir também que a continuação "cabe no alvo e no excedente
publicados". Cabia mal: a faixa inicial já consome os dois (`D-011`), e o teto que restaria era zero.*

Quando a `016` existir, ela passa a ser a origem do motivo, sem que o ato mude de forma. O que esta
decisão compra é que o 77/2026 seja conduzível **antes** da `016`, com a operação declarando o que
o sistema ainda não apura, e não com o sistema fingindo apurá-lo.

### D-004 — Cortar é emitir um ato, e ler não corta

```
calcular(ordem vigente, regra publicada)  →  faixa determinística
                                          →  EMITIR (ato autorizado)
                                          →  corte imutável, com universo declarado
```

É o mesmo desenho que a `015` fixou para a ordem, e pela mesma razão: abrir a tela calcula e mostra;
não emite, não grava e não substitui. Um corte regenerado em silêncio quando a tela abre mudaria,
sozinho, quem participa da Etapa seguinte.

### D-005 — Quem fica fora é preservado, com posição, causa e faixa — e não vira Resultado

O ato de corte enumera **todos os participantes considerados**, não apenas os que progrediram. Quem
ficou fora consta com a sua posição na ordem, a faixa que não alcançou e a causa em uma frase.

**O corte não grava Resultado de Etapa e não elimina.** Escrever `ELIMINADA` para quem não alcançou
a faixa confundiria duas coisas que o candidato precisa distinguir — foi reprovado, ou não alcançou
o corte — e faria o registro afirmar o que não aconteceu. A `018` recusou exatamente esse expediente
quando estudou limitar o efeito de um recurso deferido, e a razão vale palavra por palavra aqui.

### D-006 — O efeito é pleno sobre a participação, e a fonte continua única

Existindo corte vigente para o marco que antecede uma Etapa, participa dela quem está **dentro da
faixa** — somado, e não substituído, ao que a `013` já exige: eliminada em Etapa anterior continua
fora, e a habilitação na imediatamente anterior continua valendo.

**Não nasce um segundo lugar onde se pergunta quem participa.** A condição entra no mesmo ponto em
que a progressão já é resolvida, uma vez por listagem, e alcança todas as superfícies que consomem
aquele conjunto — a distribuição, a Mesa do avaliador, a inscrição como instrumento de trabalho, a
entrega de documento e a navegação "próxima pendente". Deixar qualquer uma de fora reabriria a porta
que a `013` fechou.

Atribuição criada antes do corte é preservada como histórico, não autoriza trabalho enquanto a
inscrição estiver fora da faixa, e volta a autorizar se uma faixa seguinte a alcançar.

### D-007 — O corte declara o universo que o delimita, e fica obsoleto — nunca se recorta sozinho

O ato declara o ato de ordenação que leu, a regra na versão normativa sob a qual foi calculado, o
alvo apurado, a linha do quadro lida quando o alvo é derivado e a faixa anterior quando é
continuação. Mudança **nesse** universo o torna obsoleto, não inválido: o corte anterior permanece
legível sob a norma que o governou, e alguém autorizado emite o próximo.

São quatro as causas, e a interface diz qual delas ocorreu: a ordem foi sucedida; a regra do corte
foi retificada; o quadro de vagas foi retificado e o alvo era derivado; um participante reingressou.

**E não se corta sobre ordem obsoleta.** Emitir corte a partir de um ato de ordenação já marcado
como obsoleto é recusado com motivo nomeado: seria selecionar quem progride por uma ordem que o
próprio sistema já sabe estar para trás.

### D-008 — Reingresso por recurso deferido obsoleta o corte e impede o que dele depende

Superado o Resultado que eliminava alguém, a pessoa volta ao fluxo pelas regras derivadas que já
existem — não se cria estado artificial de "reintegrado" e não se cria exceção de corte. O que muda
é o que já tinha sido emitido: o corte vigente do marco alcançado **fica obsoleto**, com a causa
nomeada *participante reingressou*, e a publicação que dele dependa é **impedida** enquanto durar.

A guarda é de bloqueio, e não de recálculo. Impede-se que a instituição divulgue uma faixa que omite
quem teve o direito reconhecido; não se emite ato nenhum por conta própria.

**E a obsolescência é medida no ato de ordenação, não em "o universo do corte"** (`FR-218`,
`FR-230`). Todo participante considerado está no universo do corte, e a redação anterior fazia
**qualquer** reingresso obsoletá-lo — inclusive o de quem já estava dentro da faixa. Somado ao
bloqueio da `D-013`, isso parava o trabalho da Etapa governada para exigir uma geração sucessora
**idêntica à anterior**. Pior: no 77, em que o recurso é julgado na própria Etapa que o corte governa,
esse seria o caso normal, e não a exceção.

O que obsoleta é o reingresso que alcança **a ordem**: ali a posição muda, a faixa pode mudar, e a
geração sucessora tem o que dizer. O reingresso que só devolve alguém à Etapa governada não move
posição nenhuma — e um ato que não muda nada não é ato, é cerimônia.

### D-009 — A regra do corte é conteúdo publicado, com a conta que isso implica

Esquema canônico com elevação de versão e caminho de leitura das anteriores, elaboração na interface
administrativa, presença no documento publicado e entrada no catálogo de Retificação endereçada por
identidade estável. É o mesmo preço que a regra de classificação e o quadro de vagas já pagaram, e
pagá-lo junto com o campo de desfecho de empate da `D-001` é **uma** elevação, não duas.

### D-010 — A autoridade é consumida, não inventada

Emitir corte é ato explícito, autorizado e auditável, pela mesma cadeia que já autoriza emitir a
ordem. Esta feature registra quem emitiu, sob qual autoria e em que instante; ela **não** define
quem é a autoridade competente. Ler o corte para conduzir a Etapa não confere autorização de emitir.

### D-011 — A primeira emissão alcança o alvo **e** o excedente; a continuação é declarada

*Decisão do usuário, 11/09/2026, depois da revisão cruzada.*

A cláusula 6.10 do 77, a 8.13 do 57 e a 8.12 do 28 mandam analisar os documentos dos suplentes **para
chamada imediata**. Analisar depois é exatamente o que a palavra *imediata* existe para evitar. Logo
a faixa da primeira emissão é `alvo + excedente`: no 77, 40 mais até 30, setenta pessoas analisadas
de uma vez.

**A continuação passa a ser outra coisa**, e é a 6.3 que a descreve: *"haverá a análise da
documentação do próximo candidato classificado… até que se preencha o número total de vagas"*. Ela
vai **além** da faixa publicada, e por isso não pode ser silenciosa: a regra declara se aquele Edital
a admite, e a ausência de declaração impede a publicação. No 14 a resposta é não — a 6.1 diz que quem
não foi convocado não será classificado, e continuar ali contrariaria o Edital.

**Admitida, a continuação não tem teto numérico publicado**, porque o Edital não publica nenhum: ele
diz "até que se preencha", e quantas vagas foram preenchidas é conta da `016`. O que a limita é o
motivo declarado, a autorização, a auditoria e o fim da ordem — e essa é a forma honesta de escrever
uma regra cujo limite mora fora desta feature.

*A redação anterior dizia as duas coisas ao mesmo tempo — `FR-180` mandava a faixa inicial somar o
excedente, e `FR-204` dava à continuação o teto `alvo + excedente`, que a faixa inicial já teria
consumido. Implementada ao pé da letra, a primeira emissão do 77 progredia setenta e a `US4` ficava
sem razão de existir.*

### D-012 — A Etapa governada é declarada, e a ausência dela também

*Decisão do usuário, 11/09/2026, depois da revisão cruzada.*

A Regra de Corte declara, por identidade estável, **qual Etapa aquele corte alimenta** — ou declara
explicitamente que não alimenta nenhuma. Não há inferência: nem da ordem das Etapas, nem das que o
marco enumera.

**A razão é que num marco de sorteio a Etapa enumerada não significa nada.** O domínio exige que todo
marco enumere ao menos uma, porque sem Etapa não há pontuação a combinar; num marco que ordena por
sorteio, porém, a ordem nasce da semente, e a Etapa está ali para satisfazer a validação. Derivar
dela quem progride seria derivar de um campo preenchido para publicar, não para dizer alguma coisa —
e mudar qual Etapa o marco enumera, por qualquer razão, moveria em silêncio quem continua no certame.

**Ausência declarada é um valor, e não um vazio.** O marco terminal existe, e o corte dele é
legítimo: ele não produz efeito de participação, e a regra diz isso com todas as letras em vez de
deixar o sistema concluí-lo.

### D-013 — Corte obsoleto bloqueia trabalho novo na Etapa governada

*Decisão do usuário, 11/09/2026, depois da revisão cruzada.*

O corte obsoleto **continua definindo quem está dentro** — a `FR-217` proíbe alterá-lo —, e enquanto
a geração sucessora não é emitida, distribuir e concluir avaliação na Etapa governada ficam
**bloqueados**, com motivo nomeado. O trabalho já registrado é preservado, e a leitura continua.

É negar por padrão, e é o caso do reingresso que obriga: deferido o recurso que devolve alguém ao
universo, continuar trabalhando sob a faixa antiga é justamente excluir quem teve o direito
reconhecido — e o sistema já sabe disso, porque foi ele que marcou a obsolescência.

As duas alternativas foram recusadas. Seguir sem bloquear deixa a operação construir, sobre uma faixa
que o próprio sistema já sabe estar para trás, trabalho que a sucessão vai invalidar. Derrubar o gate
— admitir todos os habilitados enquanto durar a obsolescência — readmite sem ato quem a norma cortou.

### D-014 — Alvo derivado exige linha para todo recorte que o marco ordena

*Decisão do usuário, 11/09/2026, depois da revisão cruzada.*

A `025` admite quadro **parcial**, e a Regra de Corte é do **marco**, que pode ordenar três listas.
Declarado alvo derivado, a publicação passa a exigir linha de quadro para a linha geral e para cada
Modalidade que terá lista própria; faltando uma, o Edital é recusado nomeando o recorte.

A alternativa — deixar publicar e recusar na emissão — descobriria o defeito no dia em que alguém vai
cortar, com o cronograma correndo e a correção dependendo de Retificação. Regra publicada que é
inexequível para uma das listas é regra que não devia ter publicado.

*Tornar a regra uma coleção por lista foi considerado e recusado nesta feature: resolveria Editais
heterogêneos que ninguém leu ainda, ao custo de identidade por lista, catálogo de Retificação próprio
e uma tela muito maior.*

**E a exigência só se sustenta porque o Perfil passa a declarar qual Modalidade é a ampla
concorrência** (`FR-231`). A implementação tentou primeiro exigir linha de **toda** Modalidade, e
isso tornava impublicável o Edital no formato normal: a `R-006` da `025` registrou que ele declara
*também* uma Modalidade chamada "Ampla concorrência", cuja quantidade mora na linha geral e a quem a
`FR-176` daquela feature proíbe dar linha reservada. A saída **não** é enfraquecer a conferência —
seria deixar publicar regra derivada inexequível numa das listas — nem casar o nome, que é o que
aquela pesquisa recusou por escrito. É o Edital **dizer qual é**: uma identidade declarada, alcançável
por Retificação, que o sistema lê em vez de adivinhar.

## 4. Problema

Um Edital publica que a entrevista é dos dez primeiros de cada código, e o sistema conduz os
concorrentes todos até a ordem — e para. A presidência tem a lista certa na tela, a regra certa no
documento publicado, e nenhuma operação que ligue uma à outra. O que resta é planilha: alguém copia
a ordem, conta dez, avisa a comissão quem chamar, e a decisão que define quem continua no certame
passa a viver fora do sistema que a deveria provar.

O prejuízo tem três faces. **Para o candidato**, não há onde ler por que ficou fora nem sob qual
ordem — e ficar fora do corte não tem sequer nome no sistema. **Para a instituição**, a seleção de
quem prossegue é o ato mais contestável do certame e é o único sem trilha, sem autoria e sem
reprodução. **Para a operação**, a Etapa seguinte continua contando gente que o Edital já excluiu, e
a prontidão nunca fecha.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Declarar a regra de corte no Edital (Priority: P1)

Quem elabora abre o marco classificatório do Perfil e declara como aquele Edital corta: o alvo — um
número, ou "o que o quadro de vagas do recorte publicar" —, o excedente de suplentes quando houver,
e o que acontece com o empate que atravessa a última posição. A regra entra no documento publicado.

**Why this priority**: sem regra publicada não há corte legítimo, e todo o resto desta feature ficaria
apoiado em decisão de tela.

**Independent Test**: declarar a regra num Edital em elaboração, publicar, e verificar que ela consta
do documento, do conteúdo canônico e do catálogo de Retificação, alcançável por identidade.

**Acceptance Scenarios**:

1. **Given** um marco declarado, **When** quem elabora declara alvo fixo de dez, desfecho de empate
   *alvo estrito*, a Etapa governada e que aquele Edital **não** admite continuação, **Then** a regra
   é aceita e viaja no conteúdo publicado.
1a. **Given** uma regra sem Etapa governada declarada — nem uma Etapa, nem a ausência explícita —,
   **When** alguém tenta publicar, **Then** a publicação é impedida, e a mensagem diz que a Etapa
   governada não é inferida de lugar nenhum.
1b. **Given** uma regra que não declara se admite continuação, **When** alguém tenta publicar,
   **Then** a publicação é impedida, nomeando o marco.
2. **Given** um marco com alvo derivado que ordena três listas, **When** falta linha de quadro para
   **qualquer** um dos três recortes, **Then** a publicação é recusada com achado impeditivo que
   nomeia o recorte sem linha — e linha zerada não é linha ausente.
3. **Given** uma regra de corte sem desfecho de empate declarado, **When** alguém tenta publicar o
   Edital, **Then** a publicação é impedida, e a mensagem diz qual marco não declarou o desfecho.
4. **Given** um Edital publicado com regra de corte, **When** uma Retificação altera o alvo,
   **Then** a alteração é endereçada por identidade e não reescreve a publicação anterior.

---

### User Story 2 — Emitir o corte de um marco (Priority: P1)

A presidência abre o marco, vê a ordem vigente com a faixa calculada — quem progride, quem fica
fora, onde a linha cai —, confere, e **emite**. O que fica gravado é um ato imutável com autor,
instante, ordem citada, regra e versão, alvo apurado e cada participante considerado.

**Why this priority**: é a capacidade que a feature existe para entregar.

**Independent Test**: com uma ordem vigente e regra publicada, calcular e emitir o corte, e verificar
que o ato é imutável, enumera todos os considerados e reproduz a mesma faixa a partir do universo
declarado.

**Acceptance Scenarios**:

1. **Given** ordem vigente e regra publicada, **When** a presidência abre o corte, **Then** vê a
   faixa calculada — **alvo mais excedente** —, o alvo apurado e a última posição alcançada, e nada
   foi gravado.
2. **Given** a faixa calculada, **When** quem tem autoridade emite, **Then** o ato passa a existir
   com autor, instante e a versão normativa que o governou.
3. **Given** alvo derivado, **When** o corte é emitido, **Then** o ato registra a quantidade lida do
   quadro **e** a identidade da linha de onde ela veio.
4. **Given** empate atravessando a última posição e desfecho *alvo estrito* declarado, **When**
   alguém tenta emitir, **Then** a emissão é recusada e a mensagem nomeia as posições empatadas.
5. **Given** o mesmo empate com desfecho *admite excedente*, **When** o corte é emitido, **Then**
   todos os empatados progridem e o ato registra quantos entraram além do alvo.
6. **Given** um ato de ordenação já obsoleto, **When** alguém tenta emitir o corte, **Then** a
   emissão é recusada com a causa da obsolescência.
7. **Given** um corte emitido, **When** qualquer ator tenta alterá-lo, **Then** a alteração é
   recusada, em qualquer caminho.

---

### User Story 3 — Conduzir a Etapa seguinte só com quem progrediu (Priority: P1)

A comissão abre a Etapa seguinte e encontra apenas quem está dentro da faixa. Quem ficou fora
aparece nomeado como tal, com a posição e a faixa que não alcançou — não some da tela, e não conta
como pendência.

**Why this priority**: é o efeito pelo qual o corte existe; sem ele a feature é um relatório.

**Independent Test**: emitir um corte e verificar que a distribuição, a Mesa, a prontidão e a
navegação "próxima pendente" da Etapa seguinte alcançam exatamente quem progrediu.

**Acceptance Scenarios**:

1. **Given** corte vigente, **When** a comissão abre a Etapa seguinte, **Then** participam apenas as
   inscrições dentro da faixa, e as demais aparecem como *fora do corte*, com posição e causa.
2. **Given** inscrição fora da faixa, **When** alguém tenta distribuí-la ou avaliá-la, **Then** a
   operação é recusada, e a recusa diz que ela está fora do corte — não que não existe.
3. **Given** Atribuição criada antes do corte, **When** o corte deixa a inscrição fora, **Then** a
   Atribuição é preservada e não autoriza trabalho.
4. **Given** eliminada em Etapa anterior que apareceria dentro da faixa, **When** o corte é emitido,
   **Then** ela não participa da Etapa seguinte — o corte soma à regra anterior e não a revoga.
5. **Given** um marco sem corte declarado, **When** a comissão abre a Etapa seguinte, **Then** o
   conjunto é exatamente o de hoje, sem alteração de comportamento.

---

### User Story 4 — Emitir a faixa seguinte quando a anterior não bastou (Priority: P2)

Analisada a documentação da primeira faixa — o alvo **e** os suplentes —, parte dela foi indeferida.
Onde o Edital publicou que admite continuação, quem tem autoridade abre o marco, declara o motivo e
quantos, e emite a **faixa seguinte**, que começa depois da última posição já alcançada. A faixa
anterior não é revogada, e as duas ficam na mesma geração.

**Why this priority**: é o ciclo do 77, do 57 e do 28, e é o que torna esta feature suficiente antes
da `016` existir.

**Independent Test**: emitir uma primeira faixa, depois uma segunda com motivo declarado, e verificar
que as duas coexistem, que a segunda começa na posição certa e que ninguém é alcançado duas vezes.

**Acceptance Scenarios**:

1. **Given** uma faixa emitida, **When** quem tem autoridade emite a faixa seguinte com motivo,
   **Then** ela começa depois da última posição alcançada e ambas permanecem vigentes.
2. **Given** uma faixa seguinte sem motivo declarado, **When** alguém tenta emiti-la, **Then** a
   emissão é recusada.
3. **Given** um Edital cuja regra **não** admite continuação, **When** alguém tenta emitir a faixa
   seguinte, **Then** a emissão é recusada, e a mensagem diz que aquele Edital não a publicou.
4. **Given** qualquer estado do certame, **When** ninguém emite nada, **Then** o sistema não emite
   faixa seguinte por conta própria, em nenhuma circunstância.

---

### User Story 5 — Enxergar que o corte vigente ficou para trás (Priority: P2)

A presidência abre o marco e vê, sem procurar, que o corte vigente foi produzido sob uma ordem que
não é mais a vigente, sob uma regra que foi retificada, sob um quadro que mudou, ou antes de alguém
reingressar por recurso deferido. A causa aparece nomeada, e o corte vigente continua o que era.

**Why this priority**: um corte silenciosamente desatualizado decide, sem que ninguém saiba, quem
está no certame.

**Independent Test**: emitir um corte, suceder a ordem, e verificar que a obsolescência aparece com a
causa certa e que o corte vigente não mudou.

**Acceptance Scenarios**:

1. **Given** corte emitido, **When** a ordem do recorte é sucedida, **Then** o corte aparece obsoleto
   com a causa *ordem sucedida*, e continua vigente e imutável.
2. **Given** corte com alvo derivado, **When** uma Retificação altera a linha do quadro,
   **Then** o corte aparece obsoleto com a causa *quadro alterado*.
3. **Given** corte emitido, **When** um recurso deferido devolve alguém ao universo, **Then** a causa
   exibida é *participante reingressou*, e não uma divergência genérica.
4. **Given** corte obsoleto, **When** alguém tenta publicar resultado que dele dependa, **Then** a
   publicação é impedida, com o caminho a seguir.
5. **Given** corte obsoleto e geração sucessora ainda não emitida, **When** alguém tenta distribuir
   ou concluir avaliação na Etapa governada, **Then** a operação é recusada dizendo que a faixa está
   para trás e que o caminho é emitir a geração sucessora — e o trabalho já registrado continua
   íntegro e legível.
6. **Given** uma geração com faixa inicial e continuação, **When** ela é sucedida, **Then**
   **nenhuma** das duas faixas continua autorizando participante.

---

### User Story 6 — Auditar e reproduzir um corte emitido (Priority: P3)

Meses depois, alguém precisa responder por que a pessoa de posição onze não foi à entrevista. Abre o
corte, lê a ordem citada, a regra na versão que a governou, o alvo apurado e a origem dele, e chega
de novo à mesma faixa.

**Why this priority**: é a prova que sustenta o ato administrativo mais contestável do certame.

**Independent Test**: a partir do universo declarado de um corte emitido, recalcular e obter
exatamente a mesma faixa, com a mesma última posição alcançada.

**Acceptance Scenarios**:

1. **Given** um corte emitido, **When** a reprodução roda a partir do universo declarado,
   **Then** produz faixa idêntica.
2. **Given** um corte de faixa seguinte, **When** alguém o audita, **Then** encontra a faixa anterior
   citada e o motivo declarado da continuação.
3. **Given** um corte antigo, **When** ele é lido depois de uma Retificação que renomeou a
   modalidade, **Then** ele é lido com os nomes da versão que congelou.

---

### Edge Cases

- **Ordem com menos participantes que o alvo.** Alvo de dez e sete classificáveis: todos progridem,
  o corte é emitido e o ato registra que o alvo não foi alcançado. Não é erro, e não é recusa — o
  14/2026 prevê literalmente esse caso.
- **Alvo derivado igual a zero.** Recorte cuja linha do quadro publica zero vagas imediatas:
  ninguém progride, e o ato o diz explicitamente. Quadro **ausente** para o recorte é outra coisa —
  linha ausente nunca significa zero, e impede a publicação (US1, cenário 2).
- **Participante sem posição na ordem.** Quem consta no ato de ordenação como considerado e sem
  posição — eliminado na própria Etapa do marco, ou não classificável — nunca entra na faixa, e o
  corte registra a causa que a ordem já registrava.
- **Empate residual longe do corte.** Empate nas posições dois e três, com alvo dez: não atravessa a
  última posição, não impede nada, e o desfecho declarado não é consultado.
- **Empate exatamente na última posição do excedente.** A regra do empate incide sobre a última
  posição **da faixa emitida**, alvo ou alvo mais excedente — e não sobre a última posição do alvo
  quando há suplentes declarados.
- **Marco com três listas.** O corte é por lista: três atos de ordenação raiz, três cortes, um marco.
  O alvo derivado lê a linha do quadro daquela modalidade; a lista sem modalidade lê a linha geral.
- **Faixa seguinte depois de a ordem ser sucedida, ou da geração sucedida.** Recusada nos dois casos,
  e eles são distintos: no primeiro a continuação se apoia numa ordem que não é mais a vigente; no
  segundo a ordem está intacta e quem foi sucedido é a geração — o que acontece quando a Retificação
  alcança a regra. O caminho é o mesmo: continuar a partir da geração vigente.
- **Sucessão de geração que já tem continuação.** A sucessão alcança a geração inteira: a faixa
  inicial e todas as continuações deixam de ser efetivas no mesmo ato. Suceder uma faixa isolada não
  é operação que exista — seria deixar metade da geração anterior governando a Etapa.
- **Marco que declara não governar Etapa alguma.** O corte é emitido, é auditável e não tem efeito de
  participação. É legítimo, e é declarado — nunca concluído do fato de o marco ser o último.
- **Corte emitido e Etapa seguinte já com Avaliação registrada.** O trabalho registrado é preservado
  como histórico; deixa de autorizar quem ficou fora, e volta a autorizar se uma faixa seguinte o
  alcançar.
- **Dois cortes concorrentes no mesmo recorte.** A segunda emissão simultânea é recusada: um recorte
  tem uma cadeia de cortes, e a corrida não produz duas.
- **Edital sem marco antes da Etapa.** Nada muda: sem marco não há ordem, sem ordem não há corte, e
  a participação continua sendo a que a `013` entrega.
- **Retificação que remove a regra de corte de um marco que já tem corte emitido.** O ato emitido
  permanece legível sob a versão que o governou; o corte aparece obsoleto com a causa *regra
  alterada*, e a Etapa seguinte volta a admitir todos os habilitados enquanto não houver corte
  vigente sob a regra nova.

## Requirements *(mandatory)*

### Functional Requirements

**A regra publicada**

- **FR-178**: O conteúdo publicado MUST admitir declarar, por marco classificatório, uma **Regra de
  Corte** com identidade estável, e um marco MUST ter no máximo uma.
- **FR-179**: A Regra de Corte MUST declarar o alvo em uma de duas formas, e apenas uma por regra:
  **quantidade fixa**, absoluta e publicada; ou **derivada do quadro de vagas** do recorte.
- **FR-180**: A Regra de Corte MUST admitir um **excedente** declarado — os suplentes —, em
  quantidade absoluta. O excedente MUST ser somado ao alvo para formar a faixa **da primeira
  emissão**: quem o Edital manda analisar para chamada imediata é analisado junto, e não depois.
- **FR-181**: A Regra de Corte MUST declarar o desfecho do empate que atravessa a última posição da
  faixa, entre *admite excedente* e *alvo estrito*.
- **FR-182**: Regra de Corte sem desfecho de empate declarado MUST impedir a publicação do Edital,
  com achado impeditivo que nomeia o marco. A ausência MUST NOT ser resolvida por padrão.
- **FR-183**: Regra com alvo derivado MUST exigir linha no quadro de vagas para **todo recorte que o
  marco ordena** — a linha geral e cada Modalidade, **exceto** a que o Perfil declarar como ampla
  concorrência. Faltando qualquer uma, a publicação MUST ser impedida com achado que nomeia o
  recorte. Linha ausente MUST NOT ser lida como zero, e linha **zerada** MUST ser aceita.
- **FR-184**: A Regra de Corte MUST ser alcançável por Retificação, endereçada por identidade
  estável, e MUST NOT reescrever publicação anterior.
- **FR-185**: A Regra de Corte MUST viajar no conteúdo canônico publicado e MUST constar do
  documento gerado, na seção do marco a que pertence.
- **FR-186**: O sistema MUST ler as versões canônicas anteriores à que introduz a Regra de Corte, e
  Edital publicado antes dela MUST permanecer legível e conduzível.
- **FR-224**: A Regra de Corte MUST declarar **qual Etapa o corte governa**, por identidade estável,
  ou declarar explicitamente que não governa Etapa alguma. A Etapa governada MUST NOT ser inferida
  das Etapas que o marco enumera, e a ausência de declaração MUST impedir a publicação.
- **FR-225**: Etapa governada declarada que não exista na versão publicada MUST impedir a
  publicação, com achado que nomeia o marco e a Etapa.
- **FR-229**: Em marco cuja ordem é **computada a partir de Etapas**, Etapa governada que esteja
  entre as que alimentam a própria ordem MUST impedir a publicação: o universo da ordem passaria a
  depender do corte que ela mesma produz. Em marco cuja ordem é **constituída por sorteio** essa
  restrição MUST NOT ser aplicada — a ordem não vem de Etapa nenhuma, e governar a Etapa que o marco
  enumera é o caso normal.
- **FR-226**: A Regra de Corte MUST declarar se admite **continuação**, e a ausência de declaração
  MUST impedir a publicação. Regra que não a admite MUST recusar toda faixa seguinte.

**Cálculo**

- **FR-187**: O sistema MUST calcular a faixa a partir do **ato de ordenação vigente** do recorte —
  Perfil, marco e lista — e da Regra de Corte na versão normativa vigente.
- **FR-188**: O cálculo MUST NOT reordenar, recalcular pontuação, aplicar critério de desempate novo
  ou alterar posição. Ele lê a ordem como ela foi emitida.
- **FR-189**: O cálculo MUST apurar o alvo: a quantidade publicada, na forma fixa; a quantidade da
  linha do quadro de vagas do recorte, na forma derivada. O alvo apurado MUST ser exibido ao lado do
  alvo declarado.
- **FR-190**: Abrir qualquer tela MUST NOT emitir, gravar ou substituir corte.
- **FR-191**: Participante sem posição na ordem MUST NOT integrar a faixa, qualquer que seja o alvo.

**Emissão**

- **FR-192**: Emitir corte MUST ser ato explícito e autorizado, e o corte emitido MUST ser imutável,
  com autor e instante.
- **FR-193**: O corte MUST declarar seu universo: o ato de ordenação citado, a Regra de Corte e a
  versão normativa que a governou, o alvo apurado, a identidade da linha do quadro quando o alvo for
  derivado, e a faixa anterior quando for continuação.
- **FR-194**: O corte MUST enumerar **todos os participantes considerados** do ato de ordenação, cada
  um com a sua posição, a consequência — progrediu, ou fora da faixa — e a causa em linguagem legível.
- **FR-195**: Empate que atravesse a última posição da faixa, sob desfecho *alvo estrito*, MUST
  recusar a emissão, nomeando as posições empatadas.
- **FR-196**: Empate que atravesse a última posição da faixa, sob desfecho *admite excedente*, MUST
  fazer progredir todos os empatados naquela posição, e o corte MUST registrar quantos entraram além
  do alvo.
- **FR-197**: Emitir corte sobre recorte sem ato de ordenação vigente MUST ser recusado, com motivo.
- **FR-198**: Emitir corte a partir de ato de ordenação **obsoleto** MUST ser recusado, e a recusa
  MUST dizer qual é a causa da obsolescência.
- **FR-199**: O mesmo universo declarado MUST reproduzir exatamente a mesma faixa.
- **FR-200**: Uma **geração de cortes** — a faixa inicial e todas as suas continuações — MUST poder
  ser sucedida por outra no mesmo recorte, com motivo obrigatório. A sucedida MUST permanecer
  legível, e uma geração MUST ter no máximo uma sucessora.
- **FR-227**: Sucedida a geração, **nenhuma** faixa dela MUST continuar efetiva: nem a inicial, nem
  qualquer continuação. Suceder faixa isolada MUST NOT ser possível.
- **FR-201**: Emissões concorrentes no mesmo recorte MUST resultar em uma única cadeia; a segunda
  MUST ser recusada e não produzir ato.

**A faixa seguinte**

- **FR-202**: Onde a regra publicada admitir continuação, o sistema MUST admitir emitir uma **faixa
  seguinte** sobre a mesma ordem, que começa depois da última posição alcançada pela faixa anterior e
  não a revoga. Continuação MUST NOT ser sucessão: as duas ficam vigentes na mesma geração, e a
  faixa anterior não é sucedida por ela.
- **FR-203**: A faixa seguinte MUST exigir motivo textual declarado por quem a emite e a quantidade
  pretendida.
- **FR-204**: A faixa seguinte MUST ser recusada quando a regra publicada não admitir continuação, e
  a recusa MUST dizer que aquele Edital não a publicou. Admitida, ela **não tem teto numérico
  publicado** — o que a limita é o motivo declarado, a autorização, a auditoria e o fim da ordem.
- **FR-205**: A faixa seguinte MUST ser recusada quando a ordem citada pela faixa anterior não for
  mais a vigente, **ou quando a geração a que ela pertence já tiver sido sucedida**. As duas não são
  a mesma coisa: a sucessão também acontece por Retificação da regra sobre a mesma ordem.
- **FR-206**: O sistema MUST NOT emitir faixa seguinte por conta própria, em nenhuma circunstância.
- **FR-207**: O sistema MUST NOT afirmar, em ato, tela, mensagem ou documento desta feature, que
  vagas foram ocupadas, que vagas foram preenchidas ou que existe déficit de vagas — o vocabulário é
  *progrediu*, *dentro da faixa* e *fora da faixa*.

**O efeito sobre a Etapa seguinte**

- **FR-208**: Existindo corte vigente cuja Regra declara governar uma Etapa, participam dela as
  inscrições alcançadas por alguma faixa da **geração vigente** daquele corte.
- **FR-209**: A condição do corte MUST somar-se às regras de progressão já vigentes, e MUST NOT
  revogá-las: inscrição eliminada em Etapa anterior continua fora, ainda que dentro da faixa.
- **FR-210**: Inscrição fora da faixa MUST NOT ser distribuída, avaliada, contada como pendente nem
  entregue pela navegação "próxima pendente", e MUST aparecer nomeada como *fora do corte*, com a
  posição e a faixa que não alcançou.
- **FR-211**: Atribuição criada antes do corte MUST ser preservada, MUST NOT autorizar trabalho
  enquanto a inscrição estiver fora da faixa, e MUST voltar a autorizar se uma faixa seguinte a
  alcançar.
- **FR-212**: O corte MUST NOT gravar Resultado de Etapa, MUST NOT eliminar e MUST NOT alterar
  Resultado existente.
- **FR-213**: A resolução do conjunto MUST ocorrer uma vez por listagem, e MUST NOT introduzir
  verificação por linha em listagem alguma.
- **FR-214**: Marco sem Regra de Corte declarada, ou com regra e sem corte emitido, MUST preservar
  exatamente o conjunto de participantes de hoje.

**Obsolescência, reingresso e publicação**

- **FR-215**: O corte vigente MUST aparecer como obsoleto quando o ato de ordenação citado for
  sucedido, quando a Regra de Corte for retificada, quando a linha do quadro lida for retificada, ou
  quando um participante reingressar no universo **daquele ato de ordenação**.
- **FR-216**: A obsolescência MUST nomear a causa ocorrida, e MUST NOT ser apresentada como
  divergência genérica.
- **FR-217**: Obsolescência MUST NOT alterar, substituir ou revogar o corte vigente.
- **FR-218**: Inscrição que reingresse por decisão recursal deferida no universo do **ato de
  ordenação** que o corte cita MUST tornar aquele corte obsoleto com a causa *participante
  reingressou*.
- **FR-230**: Reingresso que **não** alcance o ato de ordenação citado MUST NOT tornar o corte
  obsoleto — o caso do recurso julgado na própria Etapa governada, que não move posição nenhuma.
  Obsoletá-lo bloquearia trabalho para exigir uma geração sucessora idêntica à anterior.
- **FR-231**: O Perfil MUST poder declarar **qual das suas Modalidades é a ampla concorrência**. A
  declarada corresponde à **linha geral** do quadro, MUST NOT ter linha própria, e MUST NOT ser
  exigida pela conferência da `FR-183`. Declaração que aponte Modalidade que o Perfil não publica, e
  Modalidade declarada com linha própria, MUST impedir a publicação.
- **FR-232**: A condição do corte MUST ser correlacionada ao **recorte da inscrição** — Perfil e
  lista. Corte emitido num Perfil MUST NOT alcançar inscrições de outro, e corte emitido numa lista
  MUST NOT alcançar inscrições de outra: um marco de cotas tem três atos raiz e três cortes,
  emitidos em instantes diferentes, e enquanto só um existir os demais recortes MUST permanecer
  dormentes. Corte **sem lista** alcança o Perfil inteiro, porque é o recorte da ampla concorrência.
- **FR-233**: A faixa seguinte MUST alcançar a quantidade declarada por quem a emite, e MUST NOT
  herdar o alvo nem o excedente da primeira emissão como teto. Quantidade menor que um MUST ser
  recusada, e a faixa MUST NOT partir grupo empatado ao aplicá-la.
- **FR-234**: A condição do corte MUST ficar dormente quando a norma **vigente** não declarar mais
  regra governando aquela Etapa. Faixa emitida sob regra que a Retificação removeu MUST NOT
  continuar governando.
- **FR-235**: O cálculo MUST ler a regra e o quadro da versão normativa **vigente**, e as posições
  do ato de ordenação citado. Ler a norma da versão do ato faria a geração sucessora nascer obsoleta
  sempre que a Retificação alcançasse o quadro sem tocar no marco.
- **FR-236**: O universo declarado MUST citar como sua versão normativa a **mesma** que o ato
  guarda — a vigente no instante da emissão. A versão do ato de ordenação MUST viajar ao lado, com
  nome próprio: ela é proveniência do que foi lido, e não da norma que decidiu a faixa.
- **FR-237**: A Retificação que alcance **apenas** a regra de corte MUST NOT tornar obsoleto o ato
  de ordenação. A regra de corte MUST NOT integrar o recorte normativo comparado pela ordem: o corte
  lê a ordem e não a produz, e incluí-la tornaria inalcançável a sucessão que a `FR-205` descreve —
  exigiria emitir uma ordem nova que sairia idêntica à anterior.
- **FR-238**: A declaração de qual Modalidade é a ampla concorrência MUST atravessar o assistente
  inteiro — leitura, persistência, reenvio e reexibição —, MUST constar do contrato de entrada e da
  forma publicada conferida, e MUST ser alcançável por Retificação. Declarada e não reenviada ao
  gravar outra etapa, ela MUST NOT ser apagada.
- **FR-219**: Corte obsoleto MUST impedir a publicação de resultado que dele dependa, com motivo
  nomeado e o caminho a seguir.
- **FR-228**: Enquanto o corte estiver obsoleto e a geração sucessora não for emitida, o sistema MUST
  bloquear **trabalho novo** na Etapa governada — distribuir, concluir avaliação **e consolidar
  Resultado** —, com motivo nomeado. Os três, e não dois: consolidar sob a faixa que o sistema já
  sabe estar para trás oficializaria o desfecho de quem talvez não devesse estar ali, e é o mais
  irreversível dos três. O trabalho já registrado MUST ser preservado, e a leitura MUST continuar
  disponível.

**Autorização e auditoria**

- **FR-220**: Emitir, suceder ou continuar corte MUST exigir autorização explícita, verificada no
  backend, pela cadeia que já autoriza emitir a ordem do marco.
- **FR-221**: Ler o corte MUST NOT conferir autorização de emiti-lo, e identificador conhecido MUST
  NOT conceder acesso a corte de Edital fora do escopo do ator.
- **FR-222**: Emissão, sucessão e continuação MUST gerar auditoria com ator, ação, recorte, ato de
  ordenação citado, alvo apurado, quantidade alcançada, instante e motivo quando houver.
- **FR-223**: O sistema MUST NOT apagar corte, item de corte ou qualquer registro que esta feature
  produza, por operação alguma.

### Requisitos de apresentação

- **UX-024**: A tela do corte MUST apresentar, antes do detalhe: alvo declarado, alvo apurado e sua
  origem, excedente, quantos progridem, quantos ficam fora e a última posição alcançada.
- **UX-025**: Toda recusa MUST dizer o que falta na linguagem da norma — qual marco não declarou o
  desfecho do empate, quais posições empataram, qual recorte não tem linha de quadro — e nunca por
  identificador interno.
- **UX-026**: A inscrição fora da faixa MUST aparecer nomeada como tal nas telas da Etapa seguinte,
  e MUST NOT simplesmente desaparecer da listagem.
- **UX-027**: O corte obsoleto MUST ser visível ao abrir o marco, com a causa, sem que ninguém
  precise comparar nada manualmente.
- **UX-028**: A emissão MUST apresentar confirmação com consequências inequívocas, declarando que o
  ato é imutável e que ele define quem prossegue.
- **UX-029**: Edital com muitos Perfis e listas MUST permitir enxergar o estado do corte de todos os
  recortes sem uma visita por recorte.
- **UX-030**: O bloqueio por corte obsoleto MUST dizer, onde o trabalho é recusado, que a faixa está
  para trás e qual é o caminho — emitir a geração sucessora —, e nunca aparecer como indisponibilidade
  sem causa.

### Key Entities

- **Regra de Corte**: como aquele marco corta — forma e quantidade do alvo, excedente e desfecho do
  empate na última posição. Conteúdo normativo publicado, com identidade estável, pertencente ao
  marco classificatório do Perfil.
- **Corte**: o ato emitido — imutável, com autor, instante, universo declarado, alvo apurado,
  motivo quando é sucessão ou continuação, e estado vigente ou sucedido.
- **Item do Corte**: o participante considerado, com a posição que tinha na ordem, a consequência
  — progrediu ou fora da faixa — e a causa legível.
- **Faixa**: o intervalo da ordem que um corte alcança; a primeira começa na primeira posição, e a
  seguinte começa depois da última posição alcançada pela anterior.
- **Alvo apurado**: a quantidade efetivamente usada no cálculo, com a sua origem — a quantidade
  publicada, ou a linha do quadro de vagas lida e a identidade dela.

## 5. Invariantes observáveis

- **IO-1**: para um recorte existe uma única cadeia de cortes, e cada corte emitido é imutável.
- **IO-2**: nenhuma leitura produz, substitui ou emite corte.
- **IO-3**: todo participante considerado tem, no corte, posição e causa legíveis — inclusive quem
  ficou fora.
- **IO-4**: nenhuma faixa é produzida por regra que não esteja publicada.
- **IO-5**: o mesmo universo declarado reproduz a mesma faixa.
- **IO-6**: obsolescência é observável, nomeia a causa e não altera o vigente.
- **IO-7**: nenhum corte grava, altera ou apaga Resultado de Etapa.
- **IO-8**: quem está fora da faixa não é alcançado por nenhuma superfície de trabalho da Etapa
  seguinte, e continua visível como fora dela.
- **IO-9**: o sistema nunca afirma vaga ocupada, vaga preenchida ou déficit.
- **IO-10**: marco sem corte emitido conduz a Etapa governada exatamente como hoje.
- **IO-11**: sucedida uma geração, nenhuma faixa dela autoriza participante — nem a inicial, nem
  qualquer continuação.
- **IO-12**: a Etapa que um corte governa é sempre lida da regra publicada, e nunca inferida.
- **IO-14**: o universo de um ato de ordenação nunca depende de um corte derivado dele.
- **IO-15**: a faixa de um Perfil nunca alcança inscrição de outro.
- **IO-16**: nenhuma faixa emitida governa Etapa que a norma vigente já não lhe atribui.
- **IO-13**: nenhum trabalho novo é criado na Etapa governada enquanto o corte que a governa estiver
  obsoleto.

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-055**: Um Edital que publica "os dez primeiros de cada código" é conduzido da ordem até a
  Etapa seguinte inteiramente pela interface administrativa, sem planilha, sem shell e sem banco.
- **SC-056**: Emitido o corte, a Etapa seguinte apresenta exatamente os participantes dentro da
  faixa — a contagem confere com o alvo apurado e com o excedente, sem diferença de uma unidade.
- **SC-057**: Quem ficou fora é localizável em uma tela, com posição, faixa não alcançada e causa,
  sem consultar a ordem em outro lugar.
- **SC-058**: Nenhum corte é emitido sem que a regra esteja publicada: a tentativa em Edital sem
  regra é recusada em 100% dos casos, com mensagem que nomeia o que falta.
- **SC-059**: Empate atravessando a última posição, sob *alvo estrito*, nunca produz corte — e a
  recusa nomeia as posições empatadas.
- **SC-060**: Empate atravessando a última posição, sob *admite excedente*, produz faixa que contém
  todos os empatados, e o excedente é legível no ato.
- **SC-061**: Um corte emitido é reproduzido a partir do seu universo declarado com resultado
  idêntico, inclusive meses depois e depois de Retificação que renomeie modalidade.
- **SC-062**: Sucedida a ordem, o corte aparece obsoleto com a causa certa em até uma abertura de
  tela, e o corte vigente permanece byte a byte o mesmo.
- **SC-063**: Reingresso por recurso deferido torna o corte obsoleto e impede a publicação que dele
  dependa, com motivo nomeado — sem que ninguém precise comparar listas.
- **SC-064**: A faixa seguinte é emitida sem revogar a anterior, e nenhuma inscrição é alcançada
  duas vezes pela mesma cadeia de cortes.
- **SC-065**: O sistema não emite faixa seguinte por conta própria em nenhum cenário exercitado.
- **SC-066**: Nenhuma superfície desta feature exibe as palavras "vaga ocupada", "vaga preenchida"
  ou "déficit", e a ausência é verificada por teste.
- **SC-067**: Abrir o corte de um marco com 1.000 participantes apresenta a faixa calculada em até
  3 segundos, e o número de consultas não cresce com o número de participantes.
- **SC-068**: Nenhuma listagem da Etapa seguinte passa a decidir participação linha a linha; a
  contagem de consultas por listagem é a mesma de hoje.
- **SC-069**: Edital sem Regra de Corte tem comportamento idêntico ao anterior a esta feature, e a
  ausência de regressão é verificada por teste.
- **SC-070**: Todo corte emitido tem auditoria com ator, instante, recorte, ordem citada e alvo
  apurado, recuperável sem acesso ao banco.
- **SC-071**: Um Edital que publica alvo **e** suplentes tem os dois alcançados pela **mesma**
  emissão — no recorte de 40 vagas com 30 suplentes e sem empate na fronteira, a primeira faixa
  contém exatamente 70 pessoas; havendo empate sob *admite excedente*, contém mais, e nunca menos.
- **SC-072**: Sucedida uma geração que tinha continuação, nenhum participante alcançado por qualquer
  faixa dela continua participando da Etapa governada.
- **SC-073**: Com o corte obsoleto, nenhuma distribuição e nenhuma conclusão de avaliação nova
  acontece na Etapa governada, e a recusa nomeia a causa e o caminho.
- **SC-074**: Nenhuma faixa de uma geração alcança quem outra faixa dela já alcançou, em nenhuma
  sequência de continuações — inclusive depois de uma faixa que não alcançou ninguém.
- **SC-075**: Num Edital de sete Perfis em que apenas um emitiu corte, os outros seis conduzem a
  Etapa governada exatamente como antes desta feature — e o mesmo vale entre listas do mesmo Perfil.
- **SC-076**: O mesmo pedido de emissão, repetido pela tela, produz **uma** faixa.
- **SC-077**: Retificada apenas a regra de corte, a geração sucessora é emitida sobre a **mesma**
  ordem, sem que nenhuma ordem nova precise existir.

## 7. Out of Scope

- **Ocupação de vagas, cotas, reserva, remanejamento e concorrência entre modalidades** — é a `016`,
  e a fronteira está em `D-002`. Esta feature seleciona quem progride; não apura quantas vagas foram
  ocupadas nem quantas faltam.
- **Convocação, chamada, comunicação ao candidato, aceite, suplência, posse e matrícula** — é a
  `019`.
- **Heteroidentificação e verificação de elegibilidade a modalidade** — spec própria, e dependente
  da aplicabilidade da Etapa por modalidade, que esta feature não abre.
- **Qualquer alteração no cálculo da ordem** — pesos, combinação, critérios de desempate, empate
  residual e proveniência continuam como a `015` os entregou. O corte lê.
- **Transparência editorial adicional do sorteio** — o rito, a relação de habilitados e a exibição
  pública do sorteio continuam como a `021` os entregou.
- **Publicação do corte como resultado e consulta pelo candidato** — a divulgação é da `017` e do
  portal; o que esta feature entrega é o impedimento de publicar sobre corte obsoleto.
- **Recurso contra o corte** — os objetos atacáveis continuam sendo os que a `018` definiu.
- **Cascata entre recortes** — o "caso o número de classificados deste grupo seja menor que dez,
  serão convocados os do Grupo 2 e do Grupo 3" do 14/2026 continua fora do que esta feature
  entregou. Esta feature corta **dentro** de cada recorte.

  *A redação anterior mandava a cascata para a `016`, tratando-a como concorrência entre
  modalidades. Por decisão do usuário de 12/09/2026, tomada ao especificar a `016` e registrada na
  spec dela, a cascata é **alvo derivado desta feature** — uma segunda espécie, que lê `callRules`
  e alcança o recorte seguinte. O que decidiu foi o gatilho: "número de classificados menor que
  dez" é contagem de classificados, e não vaga ocupada, e a fronteira fixada na `D-002` proíbe com
  estas palavras usar "quantidade de habilitados" como sinônimo de "vagas ocupadas". A capacidade
  é da linha desta feature e **não está construída**: é trabalho de incremento próprio, e a `016`
  deixou de prometê-la.*
- **Aplicabilidade da Etapa a um subconjunto de inscrições** — a Etapa continua sendo do Edital e
  alcançando todos os Perfis; a metade desta lacuna que depende de ordem é servida pelo corte, e a
  outra metade não é aberta aqui.
- **Alvo derivado de percentual** — o percentual fundamenta a cota e não a calcula, decisão que a
  `025` já fechou. O alvo derivado lê quantidade publicada.
- **Barema estruturado e autopontuação** — continuam onde estão.

## Assumptions

- O corte opera sobre o recorte que o ato de ordenação já tem — Perfil, marco e lista —, porque é
  esse o recorte que os Editais usam para cortar: "por código de inscrição" e "para cada código de
  vaga".
- A lista sem modalidade é a ampla concorrência, e o alvo derivado dela lê a linha geral do quadro.
  É a mesma grafia que o sorteio, a posição e o quadro de vagas já usam.
- A autoridade competente para emitir corte é a mesma cadeia que autoriza emitir a ordem do marco,
  até que as capacidades constituídas digam outra coisa.
- O volume de referência é o mesmo da ordem: até 1.000 participantes por recorte.
- A Etapa alcançada pelo corte é **sempre a que a regra publicada declara** (`FR-224`), e nunca
  inferida. Um marco pode declarar que não governa Etapa alguma: o corte é legítimo e não tem efeito
  de participação.
- O corte de suplentes **não** é caso de marco terminal, e a redação anterior desta seção errava
  nisso: no 77, no 57 e no 28 os suplentes são a parte excedente da **mesma** faixa que alcança o
  alvo, no mesmo marco e na mesma emissão (`D-011`).
- Regra de Corte, desfecho de empate, Etapa governada e admissão de continuação entram na **mesma**
  elevação de versão canônica. São campos de um objeto só, e separá-los seriam quatro elevações e
  quatro caminhos de leitura para uma decisão só.
- A guarda de publicação desta feature se soma às que já existem; ela não redefine o que torna uma
  publicação definitiva. O bloqueio de trabalho novo da `FR-228` é operacional e independente dela:
  um impede divulgar, o outro impede construir sobre faixa que já se sabe para trás.
- Nenhum Edital hoje publicado declara Regra de Corte, e portanto nenhum corte existe: a feature
  nasce sem migração de dado normativo, e o caminho de leitura das versões anteriores é o que
  preserva os publicados.

## 8. Ordem de implementação sugerida

1. **A regra publicada** — esquema canônico, elevação de versão, caminho de leitura das anteriores,
   elaboração na interface, documento e catálogo de Retificação. Sem ela nada mais é legítimo.
2. **O cálculo** — ler ordem vigente e regra, apurar alvo, formar faixa, resolver o empate na última
   posição. Puro, reproduzível e sem gravar.
3. **A emissão** — ato imutável, universo declarado, itens de todos os considerados, autorização e
   auditoria.
4. **O efeito na participação** — a condição somada no mesmo ponto em que a progressão já é
   resolvida, e a linha *fora do corte* nas superfícies que consomem o conjunto.
5. **A obsolescência e o reingresso** — as quatro causas nomeadas e a guarda de publicação.
6. **A faixa seguinte** — continuação onde a regra a admite, com motivo e recusa sobre ordem
   sucedida.

Os passos 1 a 4 entregam o 14/2026 inteiro até a entrevista. O passo 6 é o que fecha o ciclo do 77,
do 57 e do 28 antes de a `016` existir.

## 9. Gate de conclusão

A feature está concluída quando, pela interface administrativa e sem manipulação de banco, for
possível: declarar a regra de corte de um marco e publicá-la no documento; emitir o corte a partir da
ordem vigente; abrir a Etapa seguinte e encontrar exatamente quem progrediu, com quem ficou fora
nomeado e sua causa legível; suceder a ordem e ver o corte aparecer obsoleto com a causa certa; e
emitir a faixa seguinte com motivo declarado, sem que a anterior seja revogada.

E quando a suíte contra PostgreSQL fechar verde, com cobertura específica para publicação,
retificação, autorização, concorrência, obsolescência e não regressão do Edital sem regra de corte.
