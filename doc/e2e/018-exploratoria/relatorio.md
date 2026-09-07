# T125 — o roteiro percorrido pelo navegador

**Executado em** 07/09/2026, pelas telas, em **quatro bancos independentes** — porque quatro
estados da janela recursal não cabem numa jornada só, e forçá-los no mesmo Edital exigiria mexer no
banco durante o percurso:

| banco | porta | o que ele existe para mostrar |
|---|---|---|
| `ps018_demo` | 8018 | o roteiro inteiro, com janela declarada e **aberta** |
| `ps018_prazo` | 8019 | o mesmo certame semeado **dez dias atrás**: a janela já se encerrou |
| `ps018_antigo` | 8020 | Edital **sem** declaração de janela — o estado de todo Edital anterior ao degrau 8 |
| `ps018_negado` | 8021 | marco que declara **`admits: false`**: não cabe recurso por esta via |

Os quatro nascem do mesmo `seed_demo`, pelos mesmos commands da aplicação. Duas opções novas o
permitem — `--dias-atras`, que roda a demonstração como se ela tivesse ocorrido há N dias, e
`--janela-recursal {declarada,negada,ausente}`. Nenhuma das duas afrouxa regra: o certame percorre
o mesmo caminho, com as mesmas aferições, e o que muda é **quando** ele ocorreu e **o que o Edital
declarou**. Sem elas, um prazo de cinco dias declarado hoje só poderia ser demonstrado aberto — e a
recusa depois do encerramento exigiria esperar cinco dias.

A candidata que o roteiro chama de **Elisa Moraes** é a que os documentos da 017 chamavam de
Helena. O `quickstart` e o `plan` foram alinhados ao nome que o `seed_demo` semeia; os relatórios da
015 e da 017 continuam com o elenco que eles registraram, porque são registro do que aconteceu.

**Como foi percorrido.** Pelas telas, alternando atores, sem shell e sem banco durante a jornada.
Três ressalvas honestas sobre o instrumento, e não sobre o produto:

- os cliques do painel de navegação falhavam de forma intermitente (a aba fica oculta e a página
  não é desenhada). Onde isso ocorreu, o formulário **da própria página** foi submetido por
  `requestSubmit()` — é o mesmo `POST`, com o mesmo `CSRF` e a mesma validação de servidor; o que
  se perde é a prova do clique, não a do fluxo;
- o código de acesso do candidato foi lido do console do servidor, que é onde o *backend* de e-mail
  de desenvolvimento o escreve. É o que qualquer pessoa faria na demonstração;
- **não há capturas de tela.** Esta sessão não consegue gravar imagem em arquivo — as capturas
  voltam para a conversa, não para o disco —, e prometer numeradas como nas auditorias 015 e 017
  seria prometer o que não se entrega. A evidência aqui é **transcrição literal** do que cada tela
  respondeu, com protocolos, instantes e identificadores reais, verificáveis nos bancos acima
  enquanto eles existirem.

---

## O que cada passo mostrou

| # | passo | evidência |
|---|---|---|
| 1 | **Elisa vê o próprio Resultado** | *"Prova objetiva — Eliminada · pontuação 4,0000 — pontuação inferior à nota mínima da Etapa (4,0000 < 6,0000)"*. Ela está **fora do universo do ato** e vê assim mesmo. Fecha o E2E17-004 |
| 2 | **Elisa recorre** | protocolo `REC-2026-PQ6BRQ2F`, instante, situação *"Aguardando análise de admissibilidade"* e objeto nomeado pela Etapa — *"o meu resultado da Prova objetiva"* |
| 3 | **Quem produziu o ato não julga** | como `paulo.presidente`, que consolidou: *"Você não pode julgar este recurso. Você consolidou o resultado atacado."* — e **os botões não são oferecidos** |
| 4 | **A admissibilidade** | como `julia.julgadora`: admitida com motivo escrito, e o formulário de julgamento aparece com as quatro espécies e a Etapa alcançada |
| 5 | **Deferir fixando a correção** | sucessor **HABILITADA · 6,5000**, com a consequência **derivada** da mínima 6,0 — o formulário não tem campo de consequência. O atacado permanece **ELIMINADA · 4,0000** |
| 6 | **A cadeia a jusante reage** | a tela do marco diz *"O ato vigente está obsoleto"* e nomeia as **duas** causas: *"participante reingressou"* e *"resultado superado por recurso"*. Nada foi emitido nem publicado automaticamente |
| 7 | **A progressão retroativa** | na Mesa da Etapa 2: *"Reabilitada por recurso: decisão de 07/09/2026 no recurso REC-2026-PQ6BRQ2F."* |
| — | **O que a candidata lê ao fim** | *"Habilitada · pontuação 6,5000"*, com *"Resultado corrigido em cumprimento da decisão de 07/09/2026 no recurso REC-2026-PQ6BRQ2F. O resultado anterior permanece registrado."*, e o recurso listado em **Seus recursos** |
| — | **A janela declarada** | a lista administrativa mostra **"Dentro do prazo"** — o degrau 8 computando a janela de 5 dias que o `seed_demo` declara no marco |

### Passo 6 e 7 — a cascata de bloqueio, e o desbloqueio

| o que se fez | o que a tela respondeu |
|---|---|
| como `paula.publicadora`, abrir a prévia com a pendência aberta | *"Este ato não pode ser divulgado — Há inscrição reabilitada por recurso cujo resultado ainda não foi consolidado numa Etapa que este marco enumera. Consolide o resultado dessa inscrição na Etapa e emita o ato sucessor antes de divulgar."* |
| como `paulo.presidente`, distribuir a reabilitada na Etapa 2 | *"1 atribuída."* — a inscrição reaberta é distribuível pelas operações que já existem |
| como `otavio.avaliador`, concluir a avaliação | a Mesa passa a mostrar `1 de 1` concluída |
| voltar à Mesa como presidência | a linha diz **"pronta para consolidar"**, e continua nomeada: *"Reabilitada por recurso: decisão de 07/09/2026 no recurso REC-2026-PQ6BRQ2F."* |
| consolidar | *"1 consolidada(s), 0 recusada(s)."* |
| reabrir a prévia como `paula.publicadora` | **a recusa por reingresso desapareceu sozinha** e deu lugar à de ato obsoleto: *"A regra ou o universo mudaram desde a emissão deste ato… Emita o ato sucessor na tela de classificação do marco e publique o ato vigente."* |

A troca de uma recusa pela outra é o ponto: a pendência reaberta é **derivada**, e some quando o
fato que a produzia deixa de existir — ninguém deu baixa em nada.

### Passo 2 — os subcenários da interposição

| o que se fez | o que a tela respondeu |
|---|---|
| Ana, **dentro** do universo do ato, abre o formulário | três objetos atacáveis: *"Classificação final"*, *"Prova objetiva"*, *"Análise de títulos"* — a publicação **e** os dois Resultados (D-001) |
| Ana recorre da **publicação** | `REC-2026-UQMBSGYA`, objeto *"o resultado divulgado da Classificação final"* — nomeado pelo Marco |
| reabrir o formulário | a publicação **sumiu da lista**: o que já foi recorrido não é oferecido de novo (FR-013) |
| submeter a mesma página **duas vezes**, sem recarregar | um recurso só. A segunda submissão cai no redirecionamento de "nada a contestar", **antes** de chegar à reserva de idempotência |
| Bruno recorre da Prova objetiva e depois força o mesmo objeto | *"Você já recorreu deste mesmo resultado, pelo recurso REC-2026-CRKD55KV."* |

**Uma observação sobre o duplo clique, e vale registrá-la.** Pela tela, quem já recorreu de tudo é
barrado pelo redirecionamento da FR-013 — a reserva de idempotência é a **segunda** linha, e só é
alcançada por quem chega por outro caminho. As duas garantias existem e as duas funcionam; o que a
caminhada mostra é qual delas responde primeiro.

### Passo 3 — o impedimento, nos dois ramos

| ator | o que a tela respondeu |
|---|---|
| `paulo.presidente`, que consolidou o Resultado | *"Você não pode julgar este recurso. Você consolidou o resultado atacado."* — e **nenhum botão** |
| `paula.publicadora`, no recurso contra a publicação que ela praticou | *"Você não pode julgar este recurso. Você praticou a publicação atacada."* — e nenhum botão |
| `joana.avaliadora`, sem `recurso:julgar` | **403** na peça e **403** na lista de recursos do Edital |

### Passo 4 — julgar antes de admitir

Forçando o julgamento de uma peça ainda não apreciada: **409**, com
*"Este recurso não foi admitido, ou ainda não teve a admissibilidade apreciada."* Receber a peça
não é admiti-la.

### Passo 5 — o histórico do par

No painel da Etapa, o par superado abre em **Histórico deste par — 2 resultados**:

```text
ELIMINADA · 4,0000 — pontuação inferior à nota mínima da Etapa (4,0000 < 6,0000)
                     paulo.presidente em 07/09/2026 10:23
HABILITADA · 6,5000 — pontuação igual ou superior à nota mínima da Etapa (6,5000 ≥ 6,0000)
                     julia.julgadora em 07/09/2026 10:25, por decisão no recurso REC-2026-PQ6BRQ2F
                     — vigente
```

O superado aparece **como ele afirmou**: pontuação, consequência e motivo intactos.

### Passo 8 — a tentativa de piora

Com o recurso de Ana admitido, o formulário oferece *"Prova objetiva — Habilitada, 8,5000"*.
Fixando **5,0000**:

> **422** — *"A correção proposta pioraria a situação de quem recorreu, e o recurso não pode
> agravá-la. Nenhum resultado sucessor foi criado."*

O Resultado dela permanece **HABILITADA · 8,5000**, e nenhuma decisão foi gravada.

### Passo 9 — reavaliação determinada, e a porta dos fundos

| o que se fez | o que a tela respondeu |
|---|---|
| deferir determinando reavaliação | a decisão nasce e o efeito diz *"Nenhum — este recurso não produziu resultado sucessor."*; o vigente segue **HABILITADA · 8,5000** |
| abrir a Mesa da Etapa | a linha diz **"reavaliação determinada por recurso, ainda não cumprida"** — e não "já consolidada" |
| distribuir a reavaliação a `otavio.avaliador` | *"1 atribuída."* — a vaga extra da reavaliação, sem a qual o teto do Edital recusaria |
| `otavio` conclui com **6,0** — pior que os 8,5 protegidos | a avaliação é gravada normalmente |
| a presidência tenta consolidar | *"0 consolidada(s), 1 recusada(s)"* — *"a reavaliação produziu resultado pior que o protegido pela decisão, e o recurso não pode agravar a situação de quem recorreu; a avaliação fica registrada e o resultado não é superado"* |

A *non reformatio in pejus* **não é contornável pela reavaliação ordenada**, e o juízo do avaliador
não é apagado para consegui-lo.

### Passos 10 e 11 — a definitividade ganha lastro, e a janela é aplicada

Os fatos foram alcançados **em cascata**, um de cada vez, resolvendo o anterior — que é como a
instituição os encontra:

| fato | o que a tela respondeu ao pedido de `DEFINITIVA` |
|---|---|
| **1 · recurso pendente** | *"Há recurso pendente de julgamento sobre este marco: chamar de definitivo o que ainda está em disputa afirma o que não aconteceu. Aguarde o julgamento, ou publique como resultado preliminar."* |
| **1 · a preliminar passa** | com o **mesmo** recurso pendente: *"Resultado publicado. Ele já pode ser consultado publicamente."* — a assimetria da FR-083 |
| **2 · reavaliação não cumprida** | *"Há reavaliação determinada por recurso e ainda não cumprida numa Etapa que este marco enumera. Conclua a reavaliação, consolide o resultado e emita o ato sucessor."* |
| **3 · providência não cumprida** | *"Há decisão de recurso que determinou providência a jusante e ainda não cumprida neste marco. Emita o ato sucessor **citando a decisão** e publique aquele ato."* |
| **4 · janela aberta** | *"O prazo recursal deste marco ainda está aberto: ele se encerra em 12/09/2026 às 23h59. Aguarde o encerramento, ou publique como resultado preliminar."* |

**A janela, no instante exato.** Cinco dias corridos contados da publicação de 07/09, fechando ao
**fim** do dia 12 — o dia do começo excluído, o do vencimento incluído (FR-023). Nenhum teste de
unidade prova isso tão bem quanto ver a data escrita na recusa.

**A declaração expressa não é pedida aqui, e é o comportamento certo** (FR-086): o formulário de
publicação **não tem** o campo, porque este marco declara janela computável — o sistema verifica, e
pedir que a pessoa afirme o que a máquina sabe reintroduziria a afirmação sem lastro do E2E17-005.

**O cumprimento da providência, por citação.** A tela de emissão ofereceu a decisão pendente —
*"Recurso REC-2026-UQMBSGYA — Emita-se novo ato de ordenação do marco, corrigindo a soma dos
títulos."* — e o ato emitido sem citá-la deixou a pendência aberta; o emitido citando-a a fechou.

**Como se cumpriu a reavaliação, e o que isso revelou.** A reavaliação de Ana produziu 6,0, pior
que os 8,5 protegidos, e a consolidação recusou. Para cumpri-la foi preciso **reabrir** a avaliação
— ato da presidência, com motivo — e concluí-la de novo com 9,0. Vale registrar: sem a reabertura, a
pendência ficaria sem saída, porque a unicidade de conclusão por pessoa impede o mesmo avaliador de
concluir duas vezes e o único outro elegível já havia concluído. O caminho existe e é o correto —
mas ele não é óbvio para quem opera, e o roteiro não o nomeia.

**Tudo resolvido → permitido**, e as duas metades que faltavam. Elas foram percorridas no
`ps018_antigo`, onde o marco não declara janela: julgado o único recurso pendente, a definitiva
passou — e o sistema **exigiu a declaração expressa** antes de deixar passar.

```text
sem declaração   "Este marco não declara prazo recursal computável: para publicar como definitivo
                  é preciso declarar expressamente, com fundamento escrito, que o prazo se
                  encerrou."                                                            (422)
com declaração   publicada · Vigente · Resultado definitivo · 07/09/2026 às 11h07
                  por paula.publicadora · Reitora do Ifes
```

E a declaração **volta na tela**, junto da publicação que a exigiu, com autor, instante e texto —
que é o que a SC-018 pede por "consultáveis". Ver [o que a caminhada encontrou](#o-que-a-caminhada-encontrou):
até esta rodada ela era gravada e nunca lida.

### A definitiva retificada, apresentada pela causa

Ainda no `ps018_antigo`, sobre a definitiva já publicada: Bruno recorre do próprio Resultado da
Análise de títulos, o recurso é admitido — com a tempestividade decidida como **juízo humano
motivado**, porque não há prazo computável —, deferido com correção fixada em 10,0000, o ato
sucessor é emitido e a nova divulgação é publicada como definitiva, com **nova** declaração expressa.

O que a página pública passa a dizer:

> Resultado definitivo
> Este é o resultado vigente deste marco.
> **Resultado definitivo, retificado em 07/09/2026 em razão do julgamento do recurso
> REC-2026-H7YZ4WW9.**

Sem natureza nova no vocabulário — `DEFINITIVA` nas duas —, e a vigente dizendo que é a vigente
(FR-087, FR-088, FR-090, SC-019).

### Passo 11 — a jornada da janela recursal, nos três estados

**Declarada e aberta** (`ps018_demo`). O formulário de interposição nomeia o instante ao lado de
cada objeto — *"Classificação final — até 12/09/2026 às 23h59"* —, e a peça interposta grava e
mostra os dois:

> Prazo recursal
> De 07/09/2026 às 10h48 até 12/09/2026 às 23h59 · **Dentro do prazo**

Cinco dias corridos: o dia da publicação excluído, o do vencimento incluído, fechando ao fim dele na
zona institucional (FR-023, FR-024, SC-014).

**Declarada e encerrada** (`ps018_prazo`, publicado em 28/08). O acompanhamento **não oferece** a
ação, e o endereço do formulário devolve a pessoa ao acompanhamento em vez de mostrar um botão que
sempre recusaria (FR-013). A recusa nominal — a norma, a abertura e o encerramento — é o que a
tentativa de publicar definitiva exibiu no `ps018_demo`: *"O prazo recursal deste marco ainda está
aberto: ele se encerra em 12/09/2026 às 23h59."*

**Não declarada** (`ps018_antigo`). Três objetos oferecidos, **zero datas** em qualquer tela, e a
tempestividade aparecendo na lista administrativa como *"Sem prazo computável"* — e sendo decidida,
por escrito, no juízo de admissibilidade:

> Tempestivo: o Edital 54/2026 não declara janela recursal, e a peça foi interposta dez dias após a
> divulgação, prazo razoável à falta de norma expressa.

O documento publicado desse Edital não imprime frase nenhuma sobre prazo no marco — escrever "não
cabe recurso" ali afirmaria norma que ninguém publicou (FR-028, SC-015, SC-016).

**Negada** (`ps018_negado`). O marco declara `admits: false`, e o documento publicado escreve a
norma: *"Recurso: **Não caberá recurso contra o resultado deste marco.**"* Na tela do candidato a
ação **não é oferecida**, e o endereço do formulário devolve ao acompanhamento — a negativa não vira
"cabe para sempre" (FR-113).

**A frase normativa do prazo, no documento** (`ps018_prazo`, Edital 03/2026):

> Recurso: Caberá recurso no prazo de 5 (cinco) dias corridos, contados da divulgação do resultado.

**A declaração, no assistente de elaboração.** Composto um Edital novo pela tela, o passo
*Classificação* oferece a escolha em três — *"Admite recurso, no prazo abaixo"*, *"Não admite
recurso por esta via"*, *"Não declarar nada sobre recurso"* — com o prazo em dias (*"Contados do dia
seguinte ao da divulgação, incluindo o do vencimento"*) e a unidade (*"Dias úteis exigiriam o
calendário de dias sem expediente, que o Edital não publica"*). Salvo e reaberto, o rascunho devolve
os três estados como três. Ver [o que a caminhada encontrou](#o-que-a-caminhada-encontrou): a
escolha era uma **caixa de marcação**, e o terceiro estado era inalcançável.

---

## O que a caminhada encontrou

**O roteiro não era percorrível, e a razão não estava no produto.** Dois defeitos do
`seed_demo`, os dois corrigidos:

1. **as inscrições semeadas eram inalcançáveis pelo próprio dono.** Elas nasciam com
   `identity_subject` sintético, e nenhum login produz esse valor: quem entrasse com o e-mail da
   Elisa criava uma identidade nova e vazia, e a inscrição dela respondia 404 — corretamente, e
   para ninguém. O seed passa a criar a identidade e a credencial verificada, que são exatamente as
   linhas que o produto cria quando alguém prova o controle do e-mail;
2. **quem consolidava não era a presidência.** O `seed_demo` consolidava e emitia como
   `gustavo.gestor`, que o seletor de identidade nem oferece — e o passo 3 ficava indemonstrável,
   porque não havia como entrar como quem produziu o ato atacado. Os dois atos passam a ser
   praticados por `paulo.presidente`, que é quem os pratica no certame e quem o roteiro nomeia.

Nenhuma das duas correções é atalho de demonstração: as duas aproximam o seed do que o produto faz.

### E seis defeitos do produto, que nenhum teste alcançava

Todos corrigidos nesta rodada, e **cada um com teste que falha sem a correção**.

| # | o que a tela mostrou | o que estava errado |
|---|---|---|
| **A1** | o formulário de recorrer não dizia **até quando** | a janela era computada, gravada na peça e aplicada na recusa — e nenhuma tela do candidato a exibia. A FR-024 manda exibir, e não só registrar. Corrigido no formulário (por objeto, porque dois marcos alcançando a mesma Etapa têm prazos diferentes) e na peça (*"De … até … · Dentro do prazo"*) |
| **A2** | a declaração de encerramento sumia depois de escrita | gravada com autor, instante e texto, e lida por tela nenhuma. Afirmação de que o prazo se encerrou, guardada onde ninguém lê, não é ato auditável (SC-018). Passa a aparecer junto da publicação que a exigiu |
| **A3** | a negativa da FR-113 era inalcançável pelo assistente | a declaração era **caixa de marcação**, e os estados são três. `admits: false` só nascia se a pessoa desmarcasse a caixa **e** digitasse um prazo — o que ninguém digita para um marco que não admite recurso. Virou escolha de três, e `{}` voltou a ser lido como silêncio, não como negativa |
| **A4** | o documento calava sobre a negativa | imprimia a frase da janela declarada e silenciava nos outros dois casos, tratando `admits: false` como ausência. Mas a recusa **cita a norma**, e o candidato tem direito de conferi-la: agora o documento escreve *"Não caberá recurso contra o resultado deste marco."* O silêncio do Edital continua sem frase |
| **A5** | erro 500 ao julgar, digitando a nota com vírgula | as telas imprimem "8,5000" e "26,00"; o campo da correção recebia a vírgula e estourava em `InvalidOperation` — sem recusa, sem motivo, apagando a motivação já escrita. A interface passa a traduzir o separador, e o domínio recusa o que não é número com motivo em vez de 500 |
| **A6** | a definitiva retificada não dizia que retificava | a causa era derivada da `CitacaoDeDecisao`, que só a **providência a jusante** produz: correção fixada e reavaliação determinada corrigiam o ato sem citar nada, e a retificação ficava anônima. E o documento nunca a trazia, embora a FR-088 diga "na página **e** no documento". A causa passa a ser derivada também pela cadeia — o que **entrou** no universo do ato sucessor e carrega decisão — e é congelada no conteúdo publicado, que é o que a página e o documento leem |

**O padrão entre elas.** Cinco das seis são a mesma falha em lugares diferentes: o domínio distingue
estados que a **borda** colapsa. Silêncio e negativa viram a mesma caixa desmarcada; providência e
correção viram a mesma ausência de citação; janela computada vira nenhuma data na tela. A parte
difícil estava certa; o que faltava era a parte que a pessoa lê.

### E uma contradição no documento, que a FR-113 tornou possível

O texto padrão da seção *Dos Recursos* dizia *"Caberá recurso contra os resultados divulgados, nos
prazos do Cronograma"* — e, num Edital cujo marco declara que **não** cabe recurso, as duas frases
passaram a conviver no mesmo ato publicado. O padrão passa a **remeter**: *"nos casos e prazos que
este Edital declara para cada marco classificatório"*, verdadeiro nos três estados. A seção continua
textual, e o elaborador segue podendo escrever o que precisar.

### Duas observações, que não viraram correção

- **um Edital antigo não ganha janela pela tela de Retificação.** O catálogo de campos retificáveis
  do marco oferece só a denominação; `appealWindow` é endereçável pela **gramática** de alterações,
  e o `test_elevacao_degrau_8` prova que o caminho resolve — mas não há campo no formulário. Foi
  isso que a T109 pediu, e é o que existe. Registrado como o que é: uma lacuna de ergonomia, não de
  norma;
- **entrar como `paulo.presidente` digitando o nome não funciona; pelo botão da sugestão, sim.** O
  formulário livre exige ao menos um papel marcado, e a presidência não é papel — vem do vínculo
  com a comissão. O seletor oferece a identidade certa logo acima, e é por ali que se entra.
