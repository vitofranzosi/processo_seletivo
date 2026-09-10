# 025 — Quadro de vagas por modalidade

**Prompt do `/speckit-specify`.** Nasceu como prompt decisório em 10/09/2026, foi revisado uma vez
no mesmo dia — a revisão derrubou a recomendação de desenho da primeira redação — e as **três
decisões foram aprovadas pelo usuário em 10/09/2026**. Base: `main` em `3fafc87`, com a `023`, a
`024` e a Q-2 reenquadrada (PR #92) integradas. Histórico decisório em
[`decisao-encadeamento-l1-e-o-arco-operacional.md`](../decisao-encadeamento-l1-e-o-arco-operacional.md)
§5 e em [`descoberta-escopo-sorteio-e-anexos.md`](../descoberta-escopo-sorteio-e-anexos.md) §216.

**A frase que governa:**

> O Edital publica quantas vagas existem em cada recorte, em números absolutos, legíveis por máquina
> e alcançáveis por Retificação — e o quadro publicado é a fonte, não o percentual que o fundamenta.

**E a frase que mantém o corte:**

> Esta feature **declara** o quadro. Não o ocupa, não o consome e não convoca por ele. Ocupação é
> `016`; convocação é `019`.

---

## O QUE ESTA FEATURE DESTRAVA — a medida, e o que ela não é

Do [inventário vigente](../avaliacao-de-capacidade-editais-2026-09-09.md):

```
autoria   — documento publicável inteiro          3 de 6
condução  — o mecanismo produz a ordem            5 de 7
certame   — publicável E conduzível até a ordem   2 de 7
```

> *"A L-1 sozinha leva a terceira linha de 2 para 5. Fechada ela, 57, 28 e 173 passam a ser
> publicáveis, e os três já têm mecanismo. Nenhuma outra lacuna aberta tem esse rendimento, e
> nenhuma delas depende da 014, 016 ou 019."*

A L-1 é **o único bloqueio de autoria** dos três. E o que ela **não** faz: nenhum dos três passa a
ocupar vaga, convocar ou cortar por causa dela. Eles passam a **existir como documento**.

**A anomalia que a `021` deixou à mostra, e que esta feature fecha:** a modalidade já tem papel
operacional — é o `lista_id` que reparte universo, relação, ato e publicação. O sistema hoje
**ordena por lista de concorrência e não sabe dizer quantas vagas cada lista tem.** As duas metades
do mesmo quadro deixaram de estar no mesmo lugar.

## O QUADRO REAL, NAS PALAVRAS DOS PRÓPRIOS EDITAIS

```
57/2026, por curso     AC 56 · PcD 4 · PPI 20                        (total 80)
28/2026, por polo      AC 28 · PcD 2 · PPI 10                        (total 40)
46/2026, um curso      AC 18 · PPI 6 · Q 1 · PCD 1 · EP 1 · …        (total 36)
```

São **absolutos e irregulares**. O de 46 nem sequer é gerável por percentual — `Q 1` e `PCD 1` saem
de arredondamento sobre censo, e o quadro publicado é o que vale. O 46 está fora do alvo do produto
por decisão, mas ele é a prova, e a prova continua valendo: **percentual não substitui quadro
publicado, e não o gera.**

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- `doc/decisao-encadeamento-l1-e-o-arco-operacional.md` §4 e §5 — a tese que põe a L-1 antes da
  `016`, e a Q-2 na formulação reenquadrada
- `doc/descoberta-escopo-sorteio-e-anexos.md` §"A ressalva sobre publicar quadro e ficha como
  binário" — a fundamentação da D-1, e ela vale por inteiro
- `doc/avaliacao-de-capacidade-editais-2026-09-07.md` §L-1 — o diagnóstico original, com os quadros
- `doc/avaliacao-de-capacidade-editais-2026-09-09.md` — o inventário vigente
- `backend/…/editais/models/perfis.py:56` — `ModalidadeConcorrencia`: `code`, `name`, `description`,
  e **nenhuma quantidade**
- `backend/…/editais/models/perfis.py:217` — `RegraNormativa`: `OneToOne` com a Modalidade,
  `foundation` **obrigatório** (`:222`), `percentage` (`:224`) e quatro JSONField que ninguém consome
- `backend/…/editais/models/perfis.py:21` — `PerfilVaga.immediate_vacancies`, o **total** do Perfil;
  e `reserve_type`/`reserve_limit` (`:22`, `:25`), com a mesma assimetria
- `backend/…/sorteios/domain/projecao.py:42` — `elegiveis()`, e é aqui que o recorte se decide
- `backend/…/sorteios/application/previa.py:33-49` — os recortes que a tela oferece, e o comentário
  que registra a colisão de nomes
- `backend/…/editais/domain/documentos.py:65-93` — **o precedente de integridade**: uma coleção que
  referencia Modalidades, com a elaboração recusando referência quebrada
- `backend/…/editais/api/serializers.py:212` — o precedente de referência **anulável com
  significado**
- `backend/…/publicacoes/domain/colecoes.py` — quais coleções têm chave estável, e por que a
  declaração precede a emissão
- `backend/…/publicacoes/domain/elevacao.py` e `shared/canonical.py:105` — os degraus e o
  `SCHEMA_VERSION`, hoje em **11**
- `specs/021-sorteio-publico-auditavel/spec.md` — a D-006 e a dimensão `lista_id`
- `CLAUDE.md` e a Constituição

---

## AS TRÊS DECISÕES FECHADAS

| | Decisão | Escolha |
|---|---|---|
| **D-1** | Q-2: estruturada ou binária | **Forma estruturada.** O quadro é conteúdo do snapshot. O caminho binário fica **recusado** para o quadro de vagas, e continua legítimo para os formulários |
| **D-2** | Onde mora a quantidade | **Coleção normativa própria do Perfil**, com linhas de identidade estável: uma **linha geral** associada ao recorte `NULL` e **linhas reservadas** que referenciam Modalidades. Guardar na Modalidade (A) e guardar na Regra (B) ficam recusadas **por escrito**, com os custos abaixo |
| **D-3** | Quadro contra percentual | **A quantidade publicada no quadro é a fonte autoritativa; o percentual não pode sobrescrevê-la nem recalculá-la silenciosamente.** Preservação histórica e depreciação futura ficam separadas |

## D-1, FECHADA CONTRA O CAMINHO BINÁRIO

A escolha nunca foi entre duas formas de fazer a mesma coisa:

```
forma estruturada    o quadro é conteúdo do snapshot; a 016 depois o lê
caminho binário      o quadro é um anexo publicado; NÃO SE ENTREGA A L-1
```

**Escolhido o binário, não se entrega a L-1.** Publica-se um arquivo que a `016` não consegue
consumir. A fundamentação, da §216, vale por inteiro porque é a razão da decisão:

> *"Ele é seguro para os **formulários** e caro para o **quadro de vagas**, e a razão é a
> imutabilidade: conteúdo publicado não se remodela. O Edital que publicar o quadro como binário
> fica assim para sempre. Não é migração adiada — é **bifurcação do acervo** entre Editais com
> quadro legível por máquina e Editais sem, permanente, e a `016` depois só alcança a metade nova.
> Vale como escolha consciente. Não vale como consequência não vista."*

**Publicação é ato imutável**, logo o binário não posterga a decisão: ele a toma, uma vez por Edital
publicado, e sem volta.

E vale registrar que a avaliação de 09/09 **vinha respondendo a Q-2 por antecipação** ao contar 57,
28 e 173 como impublicáveis. A presunção era defensável; a D-1 é o ato que a converte em norma.

## D-2, FECHADA CONTRA A PREMISSA DE QUE "MODALIDADE É A LISTA"

A primeira redação recomendava guardar a quantidade na `ModalidadeConcorrencia`, com o argumento de
que *"a Modalidade **é** a lista que `lista_id` endereça"*. **A premissa é falsa**, e derrubá-la é o
que produziu a D-2.

### O que `lista_id` faz, verificado

```python
# sorteios/domain/projecao.py:42 — elegiveis()
if lista_id is None or str(inscricao.modality_id or "") == str(lista_id)
```

`lista_id is None` **não filtra por modalidade nenhuma**: entram todas as inscrições submetidas do
Perfil. E é isto que a cláusula dos Editais manda para a ampla concorrência — 57 (8.7) e 28 (8.7),
palavra por palavra:

> *"todos os candidatos (inclusive os cotistas) participem do sorteio da ampla concorrência e em
> sequência haverá o sorteio das reservas de vaga"*

**Logo o recorte `NULL` é o recorte da ampla concorrência**, e não um recorte "geral" à parte dele.
O que a primeira redação afirmou — que o comentário de `classificacao/models.py:34` estaria
simplesmente errado — era forte demais: ele acerta a função.

**O defeito é outro, e é pior.** Quando o Edital declara uma Modalidade chamada "Ampla
concorrência" — que é o caso normal, e o que o `seed_demo.py:383` grafa —, `previa.py:33-49` oferece
**dois** recortes para a mesma coisa: o `NULL`, com todo mundo, e o da Modalidade AC, filtrado a
quem *declarou* AC, quase sempre vazio. O comentário do próprio arquivo registra o estrago:

> *"a tela mostrava dois blocos homônimos, um com o sorteio feito e outro vazio, e quem conduz o
> certame não tinha como saber em qual publicar"*

A `021` corrigiu **o rótulo, não a identidade**. Existem duas grafias para a ampla concorrência, e
uma delas é armadilha.

### A consequência para o quadro, e é ela que fecha a D-2

O quadro do 57 publica `AC 56`. Esses 56 são as vagas disputadas pelo recorte cujo universo é
**todo mundo** — o `NULL`. Portanto:

```
linha geral        AC 56    associada ao recorte NULL          modalityId: null
linha reservada    PcD  4   referencia a Modalidade PcD        modalityId: <uuid>
linha reservada    PPI 20   referencia a Modalidade PPI        modalityId: <uuid>
                   ─────
                   total 80 = PerfilVaga.immediate_vacancies
```

**A linha geral carrega a ampla concorrência (56), e não o total (80).** O total é a soma, e já tem
casa em `immediate_vacancies`. Confundir os dois publica um quadro que não fecha.

> Esta precisão foi obtida **depois** da aprovação, ao conferir a D-006 da `021` contra a cláusula
> 8.7 dos Editais. Ela não altera a D-2 aprovada — a linha geral continua associada ao recorte
> `NULL` —, mas fixa **qual número** ela carrega, que era o ponto em que a spec erraria sozinha.

### Por que A e B ficaram recusadas

**A — quantidade na `ModalidadeConcorrencia`.** Perde o argumento que a sustentava e expõe o buraco
que ele escondia: **o recorte `NULL` não é Modalidade e não tem onde guardar número.** Um Edital com
`AC 56` teria de pendurá-lo na Modalidade AC — que é a grafia-armadilha, a que o sorteio não usa — ou
não publicá-lo. A alternativa A não representa a ampla concorrência: só a ignora.

**B — quantidade na `RegraNormativa`.** A ampla concorrência quebra. Para carregar `AC 56` ela
precisaria de uma Regra, e `foundation` é obrigatório no modelo (`perfis.py:222`, `TextField()` sem
`blank`) e no serializer (`min_length=1`). Publicar fundamento inventado para a ampla concorrência é
inventar norma; a saída seria uma segunda grafia — quantidade na Regra para as cotas, noutro lugar
para AC —, que é duas respostas para a mesma pergunta. E o 46 acrescenta: se a quantidade **não é**
derivável do percentual, guardá-la ao lado dele sugere uma derivação que não existe.

### E a objeção de integridade, que também caiu

A primeira redação recusava a coleção própria dizendo que seria *"uma coleção que nada garante que
concorde"*. **Falso, e o repositório prova.** `editais/domain/documentos.py:65-93` já é uma coleção
de raiz que referencia Modalidades aninhadas, e a **elaboração recusa** a referência quebrada, com
mensagem que separa os dois casos — *"não pertence ao Perfil declarado"* contra *"não é de nenhum
Perfil deste Edital"*. E `modalityId` anulável **com significado** tem docstring própria
(`serializers.py:212`): *"ausentes ou nulos significam 'não restringe' — é a ausência que produz as
combinações, e por isso os dois são anuláveis em vez de obrigatórios com valor especial"*.

É exatamente a forma da linha geral.

## D-3, FECHADA SEPARANDO PRESERVAÇÃO DE DEPRECIAÇÃO

A redação anterior afirmava que remover os campos da `RegraNormativa` estaria *"fechado pela
Constituição"*. **Está errado, e o erro importa:** a Constituição obriga a preservar **valor
histórico publicado**; ela não obriga a manter indefinidamente **campo no modelo de autoria futuro**.
Juntar as duas transforma decisão de engenharia em impedimento normativo que não existe.

A norma que fica:

> **A quantidade publicada no quadro é a fonte autoritativa. O percentual não pode sobrescrevê-la
> nem recalculá-la silenciosamente.**

Duas consequências, separadas de propósito:

- **Preservação histórica — obrigatória, e não é escolha.** Todo valor já publicado em `percentage`,
  `calculation`, `rounding`, `distribution` e `call_rules` permanece intocado no conteúdo em que foi
  publicado. A `025` não discute isso.
- **Depreciação futura — aberta, e não é da `025`.** Se algum desses campos deve sair do modelo de
  autoria, e por qual degrau, decide-se quando houver quem os consuma ou quem declare que ninguém os
  consumirá — o que é da `016`. A `025` não deprecia nada e não promete nada sobre eles.

A formulação preserva o uso futuro do percentual para **validação ou sugestão** na elaboração —
avisar que `4` não é 20% de `80` é serviço legítimo — sem transformar cálculo em norma.

---

## O QUE ESTA SPEC JÁ RECEBE TOMADO

### T-1 · O quadro é conteúdo do documento, nunca anexo

D-1. Um Edital pode ter anexos — a `020` os entrega —, e o quadro não é um deles.

### T-2 · A ampla concorrência tem **uma** grafia no quadro: a linha geral

`modalityId` nulo, associada ao recorte `NULL`. Uma Modalidade declarada com nome "Ampla
concorrência" **não** carrega vagas: ela existe para que `DocumentoExigido` possa apontá-la, e é a
grafia que o sorteio não usa. A spec precisa dizer isso e recusar a segunda grafia — senão publica
`AC 56` no lugar em que a `016` não vai procurar.

### T-3 · A quantidade é absoluta, e o percentual não a gera

É a leitura dos Editais, e o 46 é a prova. Nenhum caminho da feature pode derivar quantidade de
`percentage`.

### T-4 · Cada linha tem identidade estável, e a Retificação a alcança por `id=`

Nunca por posição. A coleção entra em `COLECOES_COM_CHAVE` (`colecoes.py`) **antes** de o snapshot a
emitir — a nota da `015` diz por quê, com todas as letras (015, T-007). Fora de ordem, o caminho só
resolveria por índice, que é o que o sistema proíbe.

### T-5 · A integridade é garantida nos três pontos, e há precedente para cada um

**Elaboração** (`draft.py:192`, no padrão de `validate_document_requirements`), **publicação**
(`publish_edital.py`) e **Retificação** (a verificação de topologia sobre o caminho). Linha apontando
Modalidade de outro Perfil, ou de Perfil nenhum, é recusada — como `documentos.py:65-93` já recusa.

### T-6 · Degrau 12, e a ausência não é zero

`SCHEMA_VERSION` vai de 11 para 12 (`shared/canonical.py:105`). É degrau de **Perfil**
(`DEGRAUS_DE_PERFIL`, `elevacao.py:57`), com a coleção nascendo **vazia** — precedente exato do
degrau 7 da `015`, cuja nota já registra que lista vazia é a grafia da ausência.

`0` diz *"esta linha tem zero vagas"*; quadro não declarado diz *"este Edital não publicou quadro"* —
e é o que **todo** Edital publicado até hoje afirma, porque a capacidade não existia. Conversão sem
invenção.

### T-7 · Retificar o quadro é retificar norma, e é o caso comum

Os Editais reais retificam quadro de vagas com frequência. O congelado sob o quadro anterior
permanece legível sob a norma que o governou.

### T-8 · A feature declara; não ocupa, não consome, não convoca

A frase que mantém o corte. O caso mais tentador de violá-la são as cláusulas 8.8 e 8.9 do 57 —
cotista sorteado nas duas listas fica na de ampla concorrência, e a vaga reservada passa ao próximo
autodeclarado. **Isso é `016`**, e a `021` já as deixou fora pela mesma razão.

---

## AS PERGUNTAS QUE A SPEC PRECISA RESPONDER

Nenhuma é de ocupação; todas são de publicar o quadro.

1. **O quadro reparte só as vagas imediatas, ou também o cadastro de reserva?**
   `reserve_type`/`reserve_limit` (`perfis.py:22,25`) são do Perfil, com a mesma assimetria de
   `immediate_vacancies`. O 76 é o Edital que força a pergunta: ele é cadastro de reserva por polo.
2. **`immediate_vacancies` passa a ser soma verificada das linhas, ou permanece independente?**
   Verificada, um Edital sem quadro continua legítimo — e todos os publicados até hoje o são.
   Independente, dois números podem discordar sem que nada acuse.
3. **Um Edital pode publicar quadro parcial** — algumas Modalidades com linha, outras sem? E o que
   isso significa: zero vaga, ou não declarado?
4. **O que acontece quando uma Retificação remove uma Modalidade** que uma linha referencia? A linha
   cai junto, ou a Retificação é recusada enquanto houver linha apontando?
5. **A ordem das linhas no documento publicado** — é norma, como a ordem dos critérios de desempate,
   ou apresentação?
6. **O nome da coleção.** `vacancyTable` é provisório; o snapshot usa inglês
   (`competitionModalities`, `declaredFacts`, `documentRequirements`) e o código Django usa
   português.

## O QUE JÁ EXISTE E NÃO DEVE SER REINVENTADO

- **Endereçamento normativo estável** (`colecoes.py`, `changes.py`) — a gramática de Retificação é
  genérica e só pergunta se a coleção tem chave. Não há gramática nova a inventar.
- **A cadeia de degraus** (`elevacao.py`) — um degrau por incremento, cada um sabendo só a sua origem
  e o seu destino.
- **A validação de referência cruzada na elaboração** (`documentos.py:42-93`) — o padrão a copiar,
  inclusive a mensagem que separa os dois casos.
- **Referência anulável com significado** (`serializers.py:212`).
- **A trilha append-only** (`auditoria`) e o resumo canônico (`shared/canonical.py`).
- **A tela de composição do Perfil** (`interface/_perfil.html`, `_modalidade.html`) — o quadro é mais
  uma seção dela, não uma tela à parte.

## FORA DE ESCOPO — cada um é feature própria

- **Ocupação de vagas, cotas, remanejamento e concorrência concomitante** (`016`) — inclusive as
  cláusulas 8.8 e 8.9 do 57;
- **Convocação, chamada e suplência** (`019`);
- **Corte e progressão entre Etapas** (`014`);
- **A Q-1** — a fronteira entre `016` e `019` —, que **continua fora da `025`** por confirmação do
  usuário: as duas leituras em disputa concordam que ocupar não é declarar;
- **Ordem computada por lista de concorrência** — a assimetria que a avaliação de 09/09 registra
  (`emissao.py` não tem a dimensão que o sorteio tem);
- **Depreciar os campos da `RegraNormativa`** — D-3, e é da `016`;
- **Reconciliar as duas grafias da ampla concorrência no domínio do sorteio.** A `025` declara o
  quadro com **uma** grafia (T-2) e não reescreve `AtoDeOrdenacao`, nem corrige o comentário de
  `classificacao/models.py:34` para além do que o quadro exigir. Se a divergência merecer correção
  própria, é registro — governança é do usuário.

## O TESTE QUE A SPEC PRECISA PASSAR

Descrever, sem lacuna, o ciclo de autoria do **57/2026** até o quadro publicado e retificado — e
**parar ali**, dizendo por que para:

1. quem compõe declara, no Perfil de cada um dos dois cursos, as Modalidades que o Edital publica —
   como já faz hoje;
2. e declara o quadro: **uma linha geral** com `AC 56` e **duas linhas reservadas**, `PcD 4` e
   `PPI 20`, cada uma referenciando a sua Modalidade por identidade;
3. o sistema recusa a linha que referencie Modalidade de outro Perfil, ou de Perfil nenhum, com
   mensagem que diz qual dos dois casos é;
4. o Edital é publicado, e o quadro viaja no snapshot em `schemaVersion` **12**, com resumo canônico
   estável — dois snapshots do mesmo conteúdo produzem os mesmos bytes;
5. o documento publicado **exibe** o quadro, e um Edital publicado antes do degrau 12 continua
   legível, com a coleção vazia significando *"não publicou quadro"* e nunca *"zero vagas"*;
6. uma **Retificação** altera `PPI 20` para `PPI 18`, alcançando a linha por
   `/profiles/id=…/…/id=…` — por identidade, nunca por posição — e o quadro anterior permanece
   legível sob a norma que o governou;
7. o percentual publicado na `RegraNormativa` do PPI **não muda nada** disso: ele fundamenta, não
   calcula, e nenhum caminho da feature deriva quantidade a partir dele;
8. o 46 é o contraexemplo que a spec precisa suportar como forma, ainda que ele esteja fora do alvo:
   um quadro com `Q 1` e `PCD 1`, que percentual nenhum gera, entra e sai igual.

E mais quatro, que valem tanto quanto os oito:

9. `AC 56` aparece **uma** vez, na linha geral — e não também numa Modalidade "Ampla concorrência"
   declarada no mesmo Perfil (T-2);
10. a soma das linhas e `immediate_vacancies` não se contradizem, pela regra que a pergunta 2
    fechar;
11. um Edital que não declara quadro nenhum continua publicável — é o que todos os publicados até
    hoje são;
12. o 28/2026, com 7 polos × 3 modalidades, é declarável sem que a autoria vire trabalho braçal
    insuportável — a pressão do Edital grande está registrada e a `023` **não** a alivia: ela copia
    de um Edital para o seguinte, e não de um Perfil para os outros sessenta e nove do mesmo Edital.

O passo 6 é o emblemático: é ele que separa esta feature de uma coluna a mais numa tabela. O passo 9
é o que impede a spec de publicar o número no lugar em que a `016` não vai procurar.

E o que o teste **não** cobre, deliberadamente: quem ocupa as 56 vagas de ampla concorrência do 57,
o que acontece com o cotista sorteado nas duas listas, e quem é convocado primeiro. Isso é `016` e
`019`, e a spec que prometer isso está prometendo outra feature.

---

## ARMADILHAS OPERACIONAIS

**O número é `025`**, e vem de **`--number 25`**. Varredura refeita em 10/09/2026: nenhuma `025` em
worktree nenhuma, e `specs/` vai até a `024`. `SPECIFY_FEATURE_DIRECTORY` **não** numera — ele guia
`plan`, `tasks` e `analyze`; e o `.specify/feature.json` é estado por checkout, ignorado pelo git,
ainda apontando para `specs/002-frontend-administrativo` no checkout principal.

**As faixas de `FR-`/`SC-`/`UX-`: a `024` mudou a política.** Até a `023`, cada spec reiniciava em
`FR-001`. A `024` numera em **continuação global** — abriu em `FR-125` —, e o cabeçalho dela explica
por quê: duas features simultâneas em worktrees diferentes não descobrem o número uma da outra pela
pasta. Teto medido nesta árvore:

```
FR-152      SC-047      UX-019
```

A `025` começa em **FR-153, SC-048, UX-020**. As **decisões** seguem reiniciando em **D-001**:
`tests/test_citacoes_de_requisito.py` varre `D-` **dentro** de cada feature e `FR-`/`SC-`/`UX-`
contra a **união de todas** — é essa assimetria que faz a colisão de FR ser invisível ao teste e
visível só na leitura. **Remeça o teto antes de escrever**, porque outra worktree pode ter avançado.

**As três decisões deste documento são `D-1`, `D-2` e `D-3` — e não são as da spec.** As da spec
nascem em `D-001`, no `research.md` ou na `spec.md`, e não devem reaproveitar estes números.

**A suíte, e ela não é opcional num PR de documentação:**

```bash
cd backend && make lint check test-pg
```

`test-pg` e não `test`; `lint` são dois passos; `DB_NAME` próprio da worktree. Numa worktree recém
criada, sem `backend/.env`, o alvo `check` morre com `permission denied for table django_migrations`
— é ambiente, não o diff, e o passo roda com o superusuário.

## O PRÓXIMO PASSO

`/speckit-specify --number 25`, com este documento como entrada. **Uma spec por sessão** — e as três
decisões acima entram como recebidas, não como perguntas a reabrir.
