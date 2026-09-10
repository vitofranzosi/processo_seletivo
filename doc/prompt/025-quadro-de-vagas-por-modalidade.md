# 025 — Quadro de vagas por modalidade

**Prompt decisório, e não spec.** Primeira redação em 10/09/2026; **revisado no mesmo dia**, depois
de leitura crítica do usuário, contra a `main` em `853059c` — com a `023`, a `024` e a Q-2
reenquadrada (PR #92) já integradas. Ele não abre feature: leva à mesa a **Q-2**, formulada em
[`decisao-encadeamento-l1-e-o-arco-operacional.md`](../decisao-encadeamento-l1-e-o-arco-operacional.md)
§5, e enfrenta o desenho que a resposta arrasta — para que a decisão seja tomada sabendo o que
custa, e não depois.

**A pergunta que este documento leva à mesa:**

> A L-1 se entrega **estruturada** — o quadro de vagas como conteúdo do snapshot, legível por
> máquina, retificável por identidade —, ou se **adia** em favor da publicação binária que a `020`
> já permite?

**E a pergunta de desenho que a primeira resposta abre, e que não se responde sozinha:**

> Onde mora a quantidade de vagas de cada recorte? E qual é a relação normativa entre o quadro
> publicado e o percentual que já viaja no snapshot?

**A frase que governa o recorte:**

> Esta feature publica o quadro. Não o ocupa, não o consome e não convoca por ele.

---

## O que esta revisão corrigiu

Escrito porque a fundamentação de uma recomendação inclui o que a derrubou.

1. **A advertência de abertura ficou obsoleta, e saiu.** A primeira redação avisava que a §5
   reenquadrada vivia numa branch sem merge. O **PR #92** a integrou; a `main` já traz a Q-2 sob o
   título *"Entregar a L-1 estruturada, ou adiá-la por publicação binária"*
   (`decisao-encadeamento-l1-e-o-arco-operacional.md:115`), e é essa que este documento lê.

2. **A recomendação pela alternativa A repousava numa premissa falsa.** Ela dizia que *"a
   Modalidade **é** a lista que `lista_id` endereça"*. Não é — não ainda. O sistema opera **dois
   recortes distintos** no mesmo Perfil, e a §"O que `lista_id = NULL` realmente é" abaixo mostra
   onde. A alternativa A cai para o mesmo patamar das outras, e a decisão 2 volta a ser genuinamente
   aberta.

3. **A decisão 3 confundia duas coisas diferentes.** Ela afirmava que remover os campos da
   `RegraNormativa` estava *"fechado pela Constituição"*. Está errado: a Constituição obriga a
   **preservar valor histórico publicado** — e obriga —, mas não obriga a manter indefinidamente
   **campo no modelo de autoria futuro**. São duas questões, e juntá-las transformava uma decisão de
   engenharia em impedimento normativo que não existe. A decisão 3 foi reescrita separando as duas.

---

## Parte 1 · A decisão de construir, ou não

### A escolha não é entre duas formas de fazer a mesma coisa

É o que a reformulação da §5 corrigiu, e precisa estar na frente de quem decide:

```
forma estruturada    o quadro é conteúdo do snapshot; a 016 depois o lê
caminho binário      o quadro é um anexo publicado; NÃO SE ENTREGA A L-1
```

**Escolhido o binário, não se entrega a L-1.** Publica-se um arquivo que a `016` não consegue
consumir. A alternativa real é *construir* contra *adiar* — e o adiamento tem preço que não é o de
adiar.

### A fundamentação, que é a §216 e vale por inteiro

De [`descoberta-escopo-sorteio-e-anexos.md`](../descoberta-escopo-sorteio-e-anexos.md), §"A ressalva
sobre publicar quadro e ficha como binário":

> *"Ele é seguro para os **formulários** e caro para o **quadro de vagas**, e a razão é a
> imutabilidade: conteúdo publicado não se remodela. O Edital que publicar o quadro como binário
> fica assim para sempre. Não é migração adiada — é **bifurcação do acervo** entre Editais com
> quadro legível por máquina e Editais sem, permanente, e a `016` depois só alcança a metade nova.
> Vale como escolha consciente. Não vale como consequência não vista."*

A cadeia é curta e não tem escapatória: **publicação é ato imutável** (Constituição), logo um quadro
publicado como binário não se remodela depois, logo cada Edital que sair por esse caminho entra — em
definitivo — na metade que a `016` nunca alcança. O binário não posterga a decisão; ele a toma, uma
vez por Edital publicado, e sem volta.

### A recomendação: **forma estruturada**

Não por elegância. Por coerência com a prioridade já aprovada na §4: se a L-1 é **entrada normativa
da `016`**, entregá-la como binário é não entregá-la.

E porque o rendimento é medido. Do inventário vigente
([avaliação de 09/09](../avaliacao-de-capacidade-editais-2026-09-09.md)):

```
autoria   — documento publicável inteiro          3 de 6
condução  — o mecanismo produz a ordem            5 de 7
certame   — publicável E conduzível até a ordem   2 de 7
```

> *"A L-1 sozinha leva a terceira linha de 2 para 5. Fechada ela, 57, 28 e 173 passam a ser
> publicáveis, e os três já têm mecanismo. Nenhuma outra lacuna aberta tem esse rendimento, e
> nenhuma delas depende da 014, 016 ou 019."*

A L-1 é **o único bloqueio de autoria** dos três, verificado linha a linha na tabela de lacunas.

### A tensão que a recomendação não dissolve

O repositório tem **duas posições** sobre o binário para o quadro, e ninguém as conciliou:

| Fonte | Posição |
|---|---|
| `descoberta-escopo-sorteio-e-anexos.md` §216 | o binário *"vale como escolha consciente"*, com o custo declarado |
| [avaliação de 09/09](../avaliacao-de-capacidade-editais-2026-09-09.md) | conta 57, 28 e 173 como **impublicáveis** — recusa o anexo binário como forma de publicar o quadro |

**A avaliação vem respondendo a Q-2 por antecipação.** Os três Editais são contados como
impublicáveis porque se presume que o quadro é conteúdo estruturado do documento, e não anexo. A
presunção é defensável, é a que sustenta a recomendação acima — **mas é presunção**, e aprová-la é o
ato que a converte em norma.

### O que a recomendação custa, dito sem maquiagem

- **Um degrau de schema**, o 12, com conversão e comentário — trabalho pequeno e irreversível.
- **Uma decisão de desenho difícil**, que é a Parte 2 e não é dispensável: errá-la publica conteúdo
  que fica errado para sempre, pela mesma imutabilidade que sustenta a recomendação.
- **Autoria mais cara no Edital grande.** A pressão já registrada — no 46, nove modalidades
  repetidas em cerca de setenta ofertas — piora quando cada linha ganhar um número a digitar. A
  `023` não alivia isso: ela copia de um Edital para o seguinte, e não de um Perfil para os outros
  sessenta e nove do mesmo Edital.

---

## Parte 2 · O desenho, que é onde está a dificuldade real

### O estado verificado, hoje, com a linha

| O que | Onde | Estado |
|---|---|---|
| `ModalidadeConcorrencia` | `editais/models/perfis.py:56` | `code`, `name`, `description`. **Quantidade não existe** |
| `RegraNormativa` | `editais/models/perfis.py:217` | `OneToOne` com a Modalidade; `foundation` (`:222`, obrigatório), `version`, `percentage` (`:224`), `calculation` (`:225`), `rounding` (`:226`), `distribution` (`:227`), `call_rules` (`:228`) |
| os cinco viajam no snapshot | `publicacoes/application/publish_edital.py:118-122` | e **ninguém os consome** |
| a interface escreve **três** deles | `interface/forms.py:91` | só `foundation`, `version` e `percentage`. `calculation`, `rounding`, `distribution` e `callRules` **não têm entrada em tela alguma** |
| e a API escreve os cinco | `editais/api/serializers.py:29`, `editais/application/draft.py:259` | opcionais, e na prática sempre vazios |
| `PerfilVaga.immediate_vacancies` | `editais/models/perfis.py:21` | o **total do Perfil**, não a repartição. `reserve_type`/`reserve_limit` (`:22`, `:25`) são do Perfil pela mesma assimetria |
| o recorte do sorteio | `classificacao/models.py:34`, `divulgacao/models.py:56` | `lista_id`, e o comentário diz *"`NULL` = ampla concorrência"* — **e é essa frase que a §seguinte desmente** |
| `SCHEMA_VERSION` | `shared/canonical.py:105` | **11** |
| a Modalidade já é retificável por identidade | `publicacoes/domain/colecoes.py:24` | `/profiles/*/competitionModalities` está em `COLECOES_COM_CHAVE` |
| e há precedente de coleção que referencia Modalidade | `editais/domain/documentos.py:65-93` | `/documentRequirements` aponta `modalityId`, e a **elaboração recusa** referência a modalidade de outro Perfil ou de Perfil nenhum |
| e de referência anulável com significado | `editais/api/serializers.py:212` | *"`profileId` e `modalityId` ausentes ou nulos significam 'não restringe'"* |

**A L-1 ficou mais estranha depois da `021`**, e a avaliação de 09/09 diz por quê: a modalidade
ganhou papel operacional. O sistema hoje **ordena por lista de concorrência e não sabe dizer quantas
vagas cada lista tem.**

### O que `lista_id = NULL` realmente é — e por que a alternativa A perdeu seu melhor argumento

O comentário em `classificacao/models.py:34` diz *"`NULL` = ampla concorrência"*. **O comportamento
diz outra coisa**, e o comportamento é o que vale:

```python
# sorteios/domain/projecao.py:42 — elegiveis()
if lista_id is None or str(inscricao.modality_id or "") == str(lista_id)
```

`lista_id is None` não filtra por modalidade nenhuma: entram **todas** as inscrições submetidas do
Perfil. `NULL` é o **recorte geral**, e não a lista de ampla concorrência.

E os dois coexistem. `sorteios/application/previa.py:33-49` monta os recortes como *o sem lista* **mais**
*cada modalidade declarada* — inclusive uma Modalidade AC, quando o Edital declara uma, que é o caso
normal:

```python
listas = [(None, "Todos os inscritos do recorte de vaga (sem lista de concorrência)")] + [
    (str(modalidade.get("id")), …) for modalidade in perfil.get("competitionModalities") or []
]
```

O comentário logo acima registra o defeito que isso já produziu: *"a tela mostrava dois blocos
homônimos, um com o sorteio feito e outro vazio, e quem conduz o certame não tinha como saber em
qual publicar"*. **A correção da `021` foi de rótulo, não de identidade** — o recorte `NULL` passou a
se chamar "Todos os inscritos do recorte de vaga", e a ambiguidade estrutural continua de pé.

**A consequência para a decisão 2 é direta.** A primeira redação recomendava a alternativa A dizendo
que *"a Modalidade é a lista que `lista_id` endereça"*. Não é: o sistema acaba com **dois** recortes
— o geral e o da Modalidade AC —, e "Modalidade é a lista" ainda **não é identidade segura**. Sem
essa premissa, A perde o argumento que a sustentava, e a decisão volta a ser aberta.

### As alternativas, reabertas

#### A — quantidade na `ModalidadeConcorrencia`

Um campo de quantidade ao lado de `code`, `name`, `description`.

**A favor.** Retificação já alcança `/profiles/*/competitionModalities/id=<uuid>` (`colecoes.py:24`):
nenhuma coleção nova a declarar, só um campo em `CAMPOS_MODALIDADE` (`retificacao.py:73`).

**Contra.** O argumento principal caiu com a §anterior. E resta o buraco que ele escondia: **o
recorte geral (`NULL`) não é Modalidade e não tem onde guardar quantidade.** Um Edital que publique
`AC 56` teria de escolher entre pendurá-lo na Modalidade AC — deixando o recorte `NULL` sem número —
ou não publicá-lo. A alternativa A não representa o recorte geral: só o ignora.

#### B — quantidade na `RegraNormativa`

Um campo ao lado de `percentage`.

**A favor.** A quantidade da cota é consequência da norma; guardá-la junto do fundamento mantém o par
*quanto* e *por quê*. E a Retificação já grafa campos aninhados por esse caminho —
`normativeRule/percentage` está em `CAMPOS_REGRA` (`retificacao.py:74-78`).

**Contra, e é forte.** **A ampla concorrência quebra.** Para carregar `AC 56`, ela precisaria de uma
Regra — e `foundation` é obrigatório no modelo (`perfis.py:222`, `TextField()` sem `blank`) e no
serializer (`min_length=1`). Publicar fundamento inventado para a ampla concorrência é inventar
norma; a saída seria uma segunda grafia — quantidade na Regra para as cotas, noutro lugar para AC —,
que é duas respostas para a mesma pergunta.

E há o argumento do 46: se a quantidade **não é** derivável do percentual, guardá-la ao lado dele
sugere uma derivação que não existe.

#### C revisada — o quadro como coleção normativa própria do Perfil

**É a inclinação técnica registrada pelo usuário nesta revisão, e o desenho mudou por causa dela.**

Uma coleção sob `/profiles/*/vacancyTable` — nome provisório, a spec o fixa —, com linhas de
identidade estável:

```
linha geral       { id, modalityId: null, … }   o recorte NULL, explicitamente
linha reservada   { id, modalityId: <uuid>, … } referencia a Modalidade
```

**A favor.**

- **É a única que representa o recorte `NULL`.** A linha geral existe como linha, com identidade
  própria, e associada de forma explícita ao recorte que `projecao.elegiveis` já opera. A ambiguidade
  descrita na §anterior deixa de ser implícita: o quadro diz qual linha é qual.
- **`modalityId` anulável com significado tem precedente literal.** `DocumentRequirementSerializer`
  já o faz, e a docstring explica a escolha: *"ausentes ou nulos significam 'não restringe' — é a
  ausência que produz as combinações, e por isso os dois são anuláveis em vez de obrigatórios com
  valor especial"* (`serializers.py:212`).
- **A objeção de integridade da primeira redação era falsa, e o repositório prova.** Ela dizia que
  seria *"uma coleção que nada garante que concorde"*. `editais/domain/documentos.py:65-93` já é uma
  coleção de raiz que referencia Modalidades aninhadas, e a **elaboração recusa** a referência
  quebrada com mensagem que separa os dois casos — *"não pertence ao Perfil declarado"* contra *"não
  é de nenhum Perfil deste Edital"*. A integridade pode e deve ser garantida nos três pontos:
  **elaboração** (`draft.py:192`, no padrão de `validate_document_requirements`), **publicação**
  (`publish_edital.py`) e **Retificação** (a verificação de topologia que já roda sobre o caminho).
- **Reparte o cadastro de reserva sem tocar a Modalidade**, e não obriga toda Modalidade a ter número
  — uma Modalidade declarada só para que um `DocumentoExigido` possa apontá-la (o caso do
  `seed_demo.py:383`) fica sem linha, corretamente.

**Contra, e o que a spec terá de resolver.**

- Duas coleções que precisam concordar são, de fato, mais superfície do que uma coluna: a garantia
  existe, mas alguém tem de escrevê-la nos três pontos, e o custo é real.
- `colecoes.py` **precisa** declarar a coleção antes de o snapshot a emitir — a nota da `015` diz por
  quê, com todas as letras (015, T-007). Fora de ordem, o caminho só resolveria por posição, que é o
  que o sistema proíbe.
- A relação entre a linha geral e `PerfilVaga.immediate_vacancies` passa a exigir resposta: são o
  mesmo número dito duas vezes, ou coisas diferentes?

#### Onde este documento fica

A primeira redação recomendava A com um argumento que não se sustenta. **Não há recomendação nesta
revisão**: a C revisada é a única das três que representa o recorte `NULL`, e é a inclinação
registrada do usuário — mas ela é também a que mais trabalho novo cria, e a escolha entre "representar
o recorte geral" e "não abrir coleção nova" é de produto, não de engenharia.

### O degrau 12

`SCHEMA_VERSION` vai de 11 para 12 (`shared/canonical.py:105`), com conversão em
`publicacoes/domain/elevacao.py` e o parágrafo de comentário que os degraus 10 e 11 já têm.

**Onde ele mora depende da decisão 2.** Em A, é o primeiro degrau dentro da Modalidade — um
`DEGRAUS_DE_MODALIDADE` e um `elevar_modalidade`, simétricos aos quatro que existem. Em C, é degrau
de **Perfil** (`DEGRAUS_DE_PERFIL`, `elevacao.py:57`), com a coleção nascendo **vazia** — precedente
exato do degrau 7 da `015`, cuja nota já registra que lista vazia é a grafia da ausência.

**A ausência precisa de grafia própria, e ela não é zero.** `0` diz *"esta lista tem zero vagas"*;
quadro não declarado diz *"este Edital não publicou quadro"* — e é o que **todo** Edital publicado
até hoje afirma, porque a capacidade não existia. Conversão sem invenção, portanto.

### A Retificação alcança o quadro por identidade, no padrão da `004`

Não há gramática nova em nenhuma das três: a Retificação endereça por `id=` toda coleção declarada em
`COLECOES_COM_CHAVE`. Em A, `/profiles/*/competitionModalities` já está lá (`colecoes.py:24`) e falta
só o campo entrar em `CAMPOS_MODALIDADE` (`retificacao.py:73`). Em C, a coleção nova entra na mesma
declaração, e cada linha do quadro passa a ser alcançável por identidade própria.

**Retificar o quadro é retificar norma, e é o caso comum**: os Editais reais retificam quadro de vagas
com frequência. A spec precisa garantir que alterar um número seja alcançável por identidade — nunca
por posição —, e que o congelado sob o quadro anterior permaneça legível sob a norma que o governou.

### As perguntas que a spec herda, e que este documento **não** responde

Nenhuma é de ocupação; todas são de publicar o quadro.

1. **O quadro reparte só as vagas imediatas, ou também o cadastro de reserva?**
   `reserve_type`/`reserve_limit` (`perfis.py:22,25`) são do Perfil, com a mesma assimetria de
   `immediate_vacancies`.
2. **`immediate_vacancies` passa a ser soma verificada das linhas, ou permanece independente?**
   Verificada, um Edital sem quadro continua legítimo — e todos os publicados até hoje o são.
   Independente, dois números podem discordar sem que nada acuse.
3. **A ordem das linhas no documento publicado** — e se ela é norma ou apresentação.

A pergunta sobre `NULL` contra Modalidade AC **saiu desta lista**: ela deixou de ser subordinada e
virou o eixo da decisão 2.

---

## FORA DE ESCOPO, e a lista é curta de propósito

- **Ocupação de vagas** (`016`) — quem cabe em qual linha, remanejamento, concorrência concomitante.
- **Convocação e suplência** (`019`).
- **Corte e progressão** (`014`).
- **A Q-1** — a fronteira entre `016` e `019`. É a outra questão aberta da §5, e **continua fora da
  `025`**, por confirmação do usuário nesta revisão.
- **Ordem computada por lista de concorrência** — a assimetria que a avaliação de 09/09 registra
  (`classificacao/application/emissao.py` não tem a dimensão que o sorteio tem). É vizinha, e não é
  desta.
- **A reconciliação do recorte `NULL` no domínio do sorteio.** Esta feature **declara** o quadro,
  inclusive a linha geral; ela não reescreve `AtoDeOrdenacao`, nem corrige o comentário de
  `classificacao/models.py:34` para além do que o quadro exigir. Se a divergência entre comentário e
  comportamento merecer correção própria, é registro, e não escopo desta.

Esta feature **publica o quadro**. Nada mais.

---

## Armadilhas operacionais, verificadas nesta revisão

**O número é `025`.** Varredura refeita em 10/09/2026 sobre todas as worktrees: nenhuma `025` em
lugar nenhum, e a `024` já está na `main`. Quando a spec for aberta, o número vem de
**`--number 25`**.

**`SPECIFY_FEATURE_DIRECTORY` não numera.** Ele guia `plan`, `tasks` e `analyze`. E o
`.specify/feature.json` **não existe nesta worktree** — é estado por checkout, ignorado pelo git; o
que existe é o do checkout principal, ainda apontando para `specs/002-frontend-administrativo`.

**As faixas de `FR-`/`SC-`/`UX-`: a `024` mudou a política, e é a que vale.** Até a `023`, cada spec
reiniciava em `FR-001`. A `024` numera em **continuação global** — abriu em `FR-125`, `SC-040`,
`UX-016` —, e o cabeçalho dela explica por quê: duas features simultâneas em worktrees diferentes não
descobrem o número uma da outra pela pasta. Como ela está na `main`, o teto é:

```
FR-152      SC-047      UX-019
```

A `025` começa, portanto, em **FR-153, SC-048, UX-020**. As **decisões** seguem reiniciando em
**D-001**: `tests/test_citacoes_de_requisito.py` varre `D-` **dentro** de cada feature, e
`FR-`/`SC-`/`UX-` contra a **união de todas** — é essa assimetria que faz a colisão de FR ser
invisível ao teste e visível só na leitura.

**PR de documentação quebra o CI.** A varredura lê `specs/**/*.md` e `backend/**/*.{py,html,js}` —
`doc/` não entra —, mas a verificação é a mesma de sempre:

```bash
cd backend && make lint check test-pg
```

`test-pg` e não `test`, com `DB_NAME` próprio desta worktree, e `lint` são dois passos.

---

## A DECISÃO, formulada para aprovação

**Decisão 1 — a Q-2.** *Anuência preliminar registrada em 10/09/2026: "bem fundamentada e coerente
com a imutabilidade da publicação e com a futura `016`".*

> A L-1 se entrega na **forma estruturada**: o quadro de vagas passa a ser conteúdo do snapshot,
> legível por máquina, retificável por identidade e sujeito ao degrau 12 de schema. O caminho binário
> fica recusado para o quadro de vagas — e continua legítimo para os formulários, como a §216 já
> dizia.
>
> `( ) aprovo     ( ) recuso, e o quadro segue por anexo binário     ( ) adiar`

**Decisão 2 — onde mora a quantidade, e como o recorte geral é representado.** *Reaberta nesta
revisão: a recomendação anterior pela alternativa A repousava na premissa, falsa, de que a Modalidade
já é a lista.*

> O quadro é **uma coleção normativa própria do Perfil**, com linhas de identidade estável: uma
> **linha geral** explicitamente associada ao recorte `NULL` — `modalityId` nulo, no precedente de
> `DocumentRequirementSerializer` — e **linhas reservadas** que referenciam Modalidades por
> `modalityId`. A integridade entre as duas coleções é garantida na **elaboração**, na **publicação**
> e na **Retificação**, no padrão que `editais/domain/documentos.py:65-93` já executa.
>
> `( ) C revisada, como acima`
> `( ) A, na Modalidade — e o recorte geral fica sem número declarado`
> `( ) B, na Regra Normativa — e a ampla concorrência exige tratamento próprio`

**Decisão 3 — a relação entre o quadro e o percentual.** *Reescrita nesta revisão: a redação anterior
tratava preservação histórica e depreciação futura como a mesma questão.*

> **A quantidade publicada no quadro é a fonte autoritativa. O percentual não pode sobrescrevê-la nem
> recalculá-la silenciosamente.**
>
> Duas consequências, e elas são separadas de propósito:
>
> - **Preservação histórica — obrigatória, e não é escolha.** Todo valor já publicado em
>   `percentage`, `calculation`, `rounding`, `distribution` e `call_rules` permanece intocado no
>   conteúdo em que foi publicado. Isto é a Constituição, e a `025` não o discute.
> - **Depreciação futura — questão aberta, e não é da `025`.** Se algum desses campos deve sair do
>   modelo de autoria, e por qual degrau, decide-se quando houver quem os consuma ou quem declare que
>   ninguém os consumirá — o que é da `016`. A `025` não deprecia nada e não promete nada sobre eles.
>
> A formulação acima preserva o uso futuro do percentual para **validação ou sugestão** na
> elaboração — avisar que `4` não é `20%` de `80` é serviço legítimo — sem transformar cálculo em
> norma.
>
> `( ) aprovo     ( ) outra formulação: ______`

**Aprovadas as três, o próximo passo é `/speckit-specify --number 25`** — noutra sessão, porque uma
spec por sessão. As três perguntas da §"As perguntas que a spec herda" entram como questões da spec,
e não como decisões deste documento.
