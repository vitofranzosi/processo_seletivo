# Feature Specification: Contrato de mutabilidade normativa

**Feature Branch**: `claude/spec-026-contrato-de-mutabilidade-normativa`

**Created**: 2026-09-13

**Status**: Draft

**Input**: decisão registrada em [`doc/decisao-mutabilidade-normativa.md`](../../doc/decisao-mutabilidade-normativa.md),
a partir do anexo 16 da [auditoria exploratória de UX de 13/09/2026](../../doc/auditoria-exploratoria-ux-2026-09-13.md).

---

## 1. O achado que organiza a feature

Toda vez que o conteúdo publicado de um Edital ganha um campo, alguém precisa ter decidido se
aquele campo pode ser corrigido depois da publicação. **Hoje ninguém decide.** A decisão existe
para uns, por acidente de quem lembrou de acrescentá-los a uma lista; para outros, não existe em
lugar nenhum — nem como "sim", nem como "não", nem como "não faz sentido".

O anexo 16 da auditoria mediu, classificando cada campo escalar do conteúdo canônico vigente dos
quatro Editais publicados do ambiente contra o que a tela de Retificação alcança:

| | 26/2026 | 01/2026 | 51/2026 | 90/2026 |
|---|---:|---:|---:|---:|
| Campos publicados | 98 | 96 | 87 | 81 |
| Retificável pela tela | 38 | 42 | 38 | 34 |
| Identidade e estrutura | 24 | 28 | 23 | 22 |
| Derivado (ordem, situação, título de seção) | 5 | 5 | 5 | 5 |
| Exclusão com justificativa escrita | 2 | 2 | 2 | 2 |
| Objeto ausente — a tela não cria a declaração | 6 | 5 | 6 | 5 |
| **Normativo, sem decisão nenhuma** | **23** | **14** | **13** | **13** |

A cobertura bruta — 38 de 98 — **não** é o achado, e lê-la como "56% da Retificação está faltando"
seria errado: o denominador inclui identidade, derivados e ausências deliberadas e documentadas. O
achado é a última linha. **De 13 a 23 campos de norma publicada por Edital sobre os quais ninguém
decidiu nada** — 14% a 23% do conteúdo.

E alguns decidem quem participa ou o resultado calculado: os requisitos de participação, a espécie
do cadastro reserva, o prazo recursal, o arredondamento, a combinação e a normalização das
pontuações, as Etapas que entram na ordem, o critério de desempate, o local da prova, a designação
do período de inscrições e o método do sorteio inteiro.

### 1.1 Duas contradições objetivas, que não dependem de interpretação

**O método do sorteio.** A `021`, FR-014, determina que o método vive no conteúdo canônico
versionado e que *"alterá-lo MUST ser Retificação sobre esse conteúdo, endereçada por identidade do
Perfil e do marco"*. A própria tela do sorteio diz ao operador: *"Este método é conteúdo publicado
do Edital. Alterá-lo é uma Retificação, e não uma decisão desta tela."* **A Retificação não oferece
um único dos seus dez campos** — algoritmo, fonte, ocorrência, instante, derivação, as duas regras
e os dois textos de publicação, e a Etapa habilitante. A tela manda o operador a um caminho que não
existe.

**O local do evento.** A `021` tem como cenário de aceitação: *"Given um Edital publicado, When uma
Retificação altera o local de um evento, Then ela o alcança por identidade"*. `CAMPOS_EVENTO`
oferece descrição, início e término. O local não está lá.

Nos dois casos o domínio alcança e a gramática endereça. O que falta é a decisão registrada e o
caminho pelo canal do ator.

### 1.2 O precedente que o próprio código escreve

`interface/retificacao.py` registra, a propósito de `callForm`, por que este contrato existe:

> *"Declarado aqui **antes da primeira emissão**, pela lição que a `025` registrou como a que não
> teria conserto: endereço de Retificação não se conserta depois, porque publicação é ato imutável.
> O primeiro Edital publicado com a forma declarada nasceria irretificável nela."*

E o teste-guardião da Etapa registra o custo do esquecimento:

> *"A lista da tela ficou para trás uma vez — `maximumScore` e `evaluationsPerRegistration`
> nasceram na 012 e não entraram —, e o efeito foi publicar regra que afeta direito e só se corrige
> pela API. O domínio sempre alcançou: `colecoes.py` lista `/stages`. O que faltava era a tela."*

O mecanismo de falha é conhecido, foi pago duas vezes, e **não tem guarda geral**.

### 1.3 A justificativa técnica das exclusões caiu, e a exclusão sobreviveu a ela

As exclusões deliberadas de hoje são justificadas por um argumento técnico: *"retificá-las por
caixa de texto publicaria regra que o cálculo não interpreta"*. Esse argumento **já não vale**.
`cutRule/tieOutcome` e `callForm` entraram depois como referência, *"porque são dois valores
fechados, e a referência os oferece conferindo a escolha contra a lista"*. `operation`,
`normalization`, `rounding/mode`, `appealWindow/unit`, `tiebreakers/whenMissing` e `reserveType`
são exatamente da mesma natureza.

Uma razão que deixou de ser verdadeira continuou produzindo efeito porque ninguém tinha de
revisitá-la. É esse mecanismo que o contrato interrompe.

---

## 2. O que já existe, e que esta feature NÃO reconstrói

- **A forma publicada é declarada — para seis coleções.** `editais/domain/validation.py` declara
  `PERFIL_PUBLICADO`, `EVENTO_PUBLICADO`, `ETAPA_PUBLICADA`, `SECAO_PUBLICADA`, `ANEXO_PUBLICADO`,
  `DOCUMENTO_EXIGIDO_PUBLICADO` e `LINHA_DO_QUADRO_PUBLICADA`, e `COLECOES_PUBLICADAS` reúne seis
  delas. Não há declaração para modalidade, marco, critério de desempate, fato declarado nem para
  a raiz do Edital — **e é justamente onde mora a maior parte dos campos sem decisão** (o marco
  sozinho responde por dez dos vinte e três do 26/2026).
- **O guardião existe, para uma coleção.** `tests/contract/test_retificacoes_api.py` compara
  `ETAPA_PUBLICADA` com `CAMPOS_ETAPA`, descontando um conjunto `NAO_SAO_NORMA` declarado por
  escrito *"para que excluir um campo novo seja uma decisão escrita e não um esquecimento"*. É o
  molde. Falta generalizá-lo.
- **A gramática de endereçamento alcança tudo.** A `004` endereça por identidade estável, e
  `publicacoes/domain/colecoes.py` conhece as coleções normativas. Nenhuma gramática nova é
  necessária.
- **A tela de composição de Retificação funciona.** `interface/retificacao.py` traduz diferença em
  Alteração Normativa sem expor representação. O que ela oferece é que está incompleto.
- **A conferência já fala português.** A `026` não reconstrói o que o PR #113 entregou: a tela de
  homologação e a de publicação já dizem entidade e campo, no fuso institucional.

---

## 3. Decisões fechadas antes do planejamento

### D-001 — Quatro naturezas, e toda campo publicado tem exatamente uma

| Natureza | Significado |
|---|---|
| **Retificável** | pode ser corrigido administrativamente depois da publicação, e o canal do ator oferece o caminho |
| **Não retificável** | mudá-lo exige outro mecanismo, e a razão é **normativa**, escrita, não técnica |
| **Derivado** | não se retifica diretamente; muda como consequência de outro campo |
| **Identidade / estrutural** | não pertence ao objeto de Retificação |

A partição é total e exclusiva: um campo publicado sem natureza atribuída é defeito, não omissão
tolerável.

### D-002 — "Não retificável" exige razão normativa, e razão técnica não serve

Uma exclusão fundada em limitação de implementação — "caixa de texto publicaria valor não
interpretável" — deixa de valer quando a limitação é removida, e ninguém percebe. Uma exclusão
fundada em norma — "trocar o tipo do fato reinterpretaria valor já congelado" — continua valendo.
Só a segunda espécie é aceita.

Consequência imediata: as exclusões vigentes cuja razão é técnica **precisam ser reexaminadas nesta
feature**, e reclassificadas ou justificadas de novo.

### D-003 — A decisão pertence ao desenho do campo, e não a uma correção posterior

Publicação é ato imutável, e endereço de Retificação não se conserta depois. Por isso a decisão é
tomada quando o campo entra no conteúdo publicado — não quando alguém repara que falta.

### D-004 — O guardião falha por omissão, e não por divergência de lista

O guardião de hoje compara duas listas e falha quando divergem. O generalizado falha quando um
campo publicado **não tem natureza declarada**. A diferença importa: divergência é corrigível
escolhendo qualquer um dos lados; omissão obriga alguém a decidir.

### D-005 — Não se classifica o que o conteúdo publicado não carrega

Um campo só recebe natureza se a travessia do conteúdo canônico de um Edital publicado o encontra.
A enumeração sai do que se publica de verdade, e não de uma lista que alguém mantém — é o que faz
a omissão ser impossível de esconder e a classificação fantasma ser impossível de escrever.

**O gate não é a declaração de forma em `validation.py`.** Ela cobre seis coleções entre doze, e
esperar pelas outras seis atrasaria esta feature por um trabalho que tem razão escrita para não ter
sido feito (015, T-009). Enumerar um campo e declarar o tipo dele são coisas diferentes: o contrato
precisa da primeira.

### D-006 — O escopo não é "fazer todos os campos aparecerem na tela"

Ausência deliberada continua ausência. O nome "completude da Retificação" foi abandonado
justamente porque induzia o erro oposto. O que a feature exige é que **toda** ausência seja
deliberada, justificada por norma e protegida por teste.

### D-007 — Objeto ausente no conteúdo é caso próprio, e não uma quinta natureza

`cutRule: None`, `drawMethod: None`, `vacancyReversion: None`, `normativeRule: None`: endereçar
caminho inexistente é recusado pela gramática, e a Retificação que **cria** a declaração é
acréscimo de campo, não alteração dele. A natureza continua sendo a do campo quando ele existe; o
que a feature precisa declarar é se o acréscimo é admitido, e por qual caminho.

### D-008 — O contrato não decide a natureza de nenhum campo sozinho

Nenhuma heurística atribui natureza. Cada campo é decidido nominalmente, e a decisão viaja com a
razão. Uma classificação inferida por regra geral seria a mesma omissão de hoje, com aparência de
método.

### D-009 — A feature entrega jornada, e não apenas o contrato

O princípio VI da Constituição é explícito: *"Uma capacidade que o domínio sustenta mas que nenhuma
interface alcança NÃO DEVE ser considerada entregue"*, e *"Demonstrar por chamada manual aquilo que
o canal do ator não oferece NÃO satisfaz esta exigência"*.

Uma feature que entregasse só a matriz e o guardião seria trabalho exclusivamente técnico — que a
Constituição admite, desde que declare qual capacidade desbloqueia, mas que **não conclui uma
spec**. Por isso os quatro canários não são só insumo de desenho: eles são as jornadas que provam
que o contrato é real. Cada um é uma correção administrativa legítima que hoje só se faz por
chamada de API.

**A implementação campo a campo do resto não entra.** Os quatro canários são escolhidos por
natureza distinta, e existem para obrigar o desenho a generalizar — não para esgotar a lista.

### D-010 — O quarto canário é o método do sorteio, e não a regra classificatória

A decisão de origem — `doc/decisao-mutabilidade-normativa.md`, seção *Os quatro canários* — elege
como quarto canário **a regra classificatória** (`rounding/{mode, scale}` e `operation`), e trata o
método do sorteio como *"o quinto candidato natural, e o mais desconfortável"*. Esta spec troca um
pelo outro. A troca veio do enunciado desta feature, e não do desenho; registrá-la aqui é o que
faltava.

**Por que a troca se sustenta**: a contradição do método é objetiva e já está escrita no produto —
a `021` determina que alterá-lo é Retificação, e a própria tela do sorteio manda retificá-lo,
enquanto a Retificação não oferece um único dos seus dez campos. A regra classificatória não tem
contradição equivalente: ela está **excluída com razão registrada**, e a razão é técnica.

**O que a troca custa, e onde isso é pago**: `rounding` e `operation` deixam de ter jornada
própria. Eles não saem do escopo — são duas das exclusões por razão técnica que a FR-310 obriga a
reexaminar, e estão nomeadas na tarefa que faz esse reexame. O que muda é o estatuto: de canário
que conduz o desenho, para exclusão que precisa de razão normativa ou de reclassificação.

**O que a troca perde**: as quatro naturezas cobertas pelos canários passam a ser escalar de texto,
coleção de texto, objeto composto com valor fechado e objeto composto grande. **Valor fechado que
muda a pontuação combinada** — que era o que `rounding` e `operation` traziam de distinto — deixa
de ter jornada, e passa a depender só do reexame da FR-310.
### D-011 — A classificação vigente governa os atos futuros, e não é congelada por Publicação

A natureza de um campo **não viaja com o Edital**. Ela é norma sobre o que se pode corrigir, e uma
Retificação é ato praticado hoje, sob a norma de hoje.

**A alternativa foi considerada e recusada.** Congelar a classificação em cada Publicação faria o
contrato deixar de ser código e virar dado versionado — contra R-001 e contra a própria forma que
D-001 escolheu —, obrigaria o guardião a guardar toda classificação histórica, e prenderia cada
Edital à classificação do dia em que foi publicado. Que é exatamente o precedente do `callForm`
outra vez: *"o primeiro Edital publicado com a forma declarada nasceria irretificável nela"*.

**O que a decisão preserva**: o conteúdo publicado continua imutável, porque a Constituição já o
torna — reclassificar não reescreve nada do que foi publicado. O que muda é o que um ato **novo**
pode fazer.

**O que ela deixa aberto, e a FR-315 fecha**: a direção retificável → não retificável retira
capacidade de quem já publicou. Ela continua admissível — é decisão normativa como qualquer outra —
mas precisa dizer, por escrito, que fecha um caminho que existia.

---

## 4. Problema

O sistema publica conteúdo normativo cuja corrigibilidade nunca foi decidida. O efeito não aparece
na publicação: aparece semanas depois, quando alguém precisa corrigir um prazo recursal, um
requisito de participação ou o local de uma prova, e descobre que o único caminho é uma chamada de
API — o que a Constituição não admite como jornada concluída, e que nenhum servidor do Cefor tem
como praticar.

Sem contrato, cada feature nova repete a decisão por acidente, e o acidente só é descoberto por
auditoria.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Corrigir o local de uma prova publicada (Priority: P1)

O Edital publicou que a prova acontece no Campus Vitória. A sala mudou. Quem elabora abre a
Retificação, altera o local do Evento, submete; quem homologa confere em português; quem publica
assina. O Cronograma público passa a exibir o novo local, e a versão anterior continua consultável.

**Why this priority**: é a contradição mais limpa entre o que a `021` declara como critério de
aceitação e o que a tela oferece. Não depende de interpretação, e o campo é escalar simples — é o
canário que valida o caminho inteiro com o menor custo de desenho.

**Independent Test**: publicar um Edital com local declarado, retificá-lo pela interface, e
verificar o Cronograma público e a versão anterior. Entrega valor sozinha.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com local declarado num Evento, **When** uma Retificação altera o
   local pela tela de composição, **Then** a alteração é aceita, a conferência a exibe em português
   e a Publicação passa a vigorar com o novo local.
2. **Given** um Evento sem local declarado, **When** a Retificação informa um local, **Then** o
   acréscimo é admitido ou recusado conforme o contrato declara para o caso de campo ausente — e a
   tela diz qual dos dois é.

---

### User Story 2 — Corrigir um requisito de participação publicado (Priority: P1)

O Edital publicou "Ter concluído a disciplina de Redes de Computadores" e a exigência estava
errada. Quem elabora corrige a lista de requisitos do Perfil por Retificação; a página pública
passa a exibir a lista corrigida sob REQUISITOS, e quem já se inscreveu continua sob a versão que
aceitou.

**Why this priority**: é o campo que **decide quem pode concorrer**, e hoje só se corrige por API.
É também o primeiro canário de coleção de texto, e não de escalar.

**Independent Test**: publicar, retificar a lista, conferir a página pública e o acompanhamento de
uma inscrição anterior à Retificação.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com dois requisitos num Perfil, **When** uma Retificação altera o
   texto de um deles, **Then** a página pública exibe a lista corrigida e o comprovante da inscrição
   anterior continua apontando a versão aceita.
2. **Given** a mesma Retificação, **When** quem homologa a confere, **Then** a tela nomeia o Perfil
   e o requisito alterado, sem caminho normativo em primeiro plano.

---

### User Story 3 — Corrigir o prazo recursal publicado (Priority: P1)

O Edital publicou três dias de prazo recursal e a norma institucional exige cinco. Quem elabora
corrige o prazo por Retificação, e o candidato que abrir a tela de recurso depois da vigência lê a
data nova.

**Why this priority**: governa um **direito com prazo**, e é objeto composto, com um valor de lista
fechada (`unit`) e dois escalares. É o canário que obriga o desenho a tratar objeto aninhado e
valor fechado — as duas formas que a justificativa técnica vencida usava como motivo de exclusão.

**Independent Test**: publicar um resultado, retificar o prazo, e verificar o que a tela de recurso
do candidato passa a dizer.

**Acceptance Scenarios**:

1. **Given** um marco com janela recursal publicada de 3 dias corridos, **When** uma Retificação a
   altera para 5, **Then** a nova janela vale para o que vier, e a janela gravada num recurso já
   interposto permanece intacta.
2. **Given** a mesma Retificação, **When** ela tenta declarar unidade que o cálculo não interpreta,
   **Then** é recusada com a razão, e não gravada.

---

### User Story 4 — Corrigir o método do sorteio publicado (Priority: P2)

O Edital publicou a ocorrência que fixará a semente e a data estava errada. Quem elabora corrige o
método por Retificação — que é o que a `021` determina e o que a tela do sorteio manda fazer.

**Why this priority**: é a contradição mais grave, porque a família dominante da amostra real é
discente com sorteio. Fica em P2, e não P1, porque o método é objeto de dez campos com
interdependência entre si — o desenho precisa dos três primeiros canários antes de enfrentá-lo.

**Independent Test**: publicar um Edital de sorteio, retificar a ocorrência antes do congelamento
da relação, e verificar o que a tela do sorteio e a verificação pública passam a exibir.

**Acceptance Scenarios**:

1. **Given** um marco de sorteio com método publicado e relação **não** congelada, **When** uma
   Retificação altera a ocorrência, **Then** o método vigente passa a ser o novo.
2. **Given** um sorteio cuja relação já foi congelada, **When** uma Retificação altera o método,
   **Then** ela vale para o que vier e **não** alcança a relação congelada nem o sorteio realizado.

---

### User Story 5 — Um campo novo sem decisão quebra a suíte (Priority: P1)

Alguém acrescenta um campo ao conteúdo publicado. A suíte falha nomeando o campo e dizendo que ele
não tem natureza declarada. Quem o acrescentou decide, escreve a razão, e a suíte volta ao verde.

**Why this priority**: é o que impede a regressão estrutural. Sem ele, o contrato é prosa: os
vinte e três campos de hoje seriam corrigidos e o vigésimo quarto nasceria sem decisão, exatamente
como `maximumScore` nasceu na `012`.

**Independent Test**: acrescentar um campo à forma publicada de qualquer coleção e verificar que a
suíte falha com a mensagem que nomeia o campo.

**Acceptance Scenarios**:

1. **Given** a forma publicada e o contrato em acordo, **When** um campo novo entra na forma
   publicada sem natureza declarada, **Then** a suíte falha nomeando o campo e a coleção.
2. **Given** o contrato declara natureza para um campo que a forma publicada não tem, **When** a
   suíte roda, **Then** ela falha nomeando o campo — declarar natureza para campo inexistente é a
   mesma omissão ao contrário.

---

### User Story 6 — A tela diz o que não alcança (Priority: P2)

Quem abre a Retificação procurando corrigir o arredondamento não encontra o campo, e a tela diz por
quê — em vez de deixar a pessoa varrer a página e concluir que o sistema esqueceu.

**Why this priority**: é a diferença entre ausência deliberada e ausência que parece defeito. Fica
em P2 porque depende de o contrato existir: sem a razão escrita, não há o que a tela diga.

**Independent Test**: abrir a Retificação de um Edital com marco declarado e verificar que o bloco
do marco nomeia o que não se corrige ali e por quê.

**Acceptance Scenarios**:

1. **Given** um Edital publicado cujo marco tem campos classificados como não retificáveis, **When**
   quem elabora abre a Retificação, **Then** o bloco do marco declara quais campos não se corrigem
   por ali e a razão normativa de cada exclusão.

---

### Edge Cases

- **Campo que existe no conteúdo de um Edital antigo e não na forma publicada de hoje.** A forma
  evoluiu por degraus; o contrato classifica a forma vigente, e conteúdo histórico permanece legível
  sob a norma que o governou.
- **Campo cuja natureza muda.** Reclassificar é decisão nova e escrita, e alcança os atos
  praticados dali em diante — inclusive sobre Edital publicado antes dela (D-011). O que ela nunca
  alcança é o conteúdo publicado, que a Constituição já torna imutável.
- **Objeto ausente no conteúdo publicado.** `cutRule: None` não é campo sem natureza: é declaração
  que não foi feita, e o contrato diz se ela pode passar a existir por Retificação.
- **Coleção nova inteira.** Uma coleção que nasça no conteúdo publicado é encontrada pela travessia
  com todos os seus campos, e cada um deles derruba a suíte até receber natureza — mesmo que a
  coleção não tenha forma declarada em `validation.py`.
- **Campo declarado em `validation.py` que nunca aparece no conteúdo.** Não deveria existir: a
  declaração de forma é conferida como presença obrigatória em todo Edital publicado. Se existir,
  a travessia não o encontra, ele não é classificado, e classificá-lo derruba a suíte por FR-302 —
  que é a resposta certa, porque um campo que ninguém publica não é norma de ninguém.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-297**: Todo campo da forma publicada de toda coleção normativa MUST ter exatamente uma
  natureza de mutabilidade declarada — retificável, não retificável, derivado, ou
  identidade/estrutural. A grafia é essa nas quatro, em spec, matriz e código (`ESTRUTURAL` é
  só o valor da enumeração).
- **FR-298**: A declaração de natureza MUST viver em local único e autoritativo, e MUST ser lida
  pelo guardião e por quem monta a tela de Retificação — duas fontes divergiriam na primeira
  mudança.
- **FR-299**: Natureza "não retificável" MUST carregar razão escrita, e a razão MUST ser normativa.
  Razão fundada em limitação de implementação NÃO DEVE ser aceita.
- **FR-300**: **Toda** coleção normativa do conteúdo canônico MUST estar enumerada pelo contrato
  de mutabilidade — incluindo modalidade de concorrência, marco classificatório, critério de
  desempate, fato declarado, linha do quadro de vagas e a raiz do Edital —, e a enumeração NÃO DEVE
  depender de a coleção ter forma declarada em `validation.py`. Declarar a forma das coleções
  aninhadas é outro trabalho, com razão escrita para não ter sido feito (015, T-009: o que vai
  dentro do marco depende do conteúdo inteiro e não cabe numa forma de campo); esta feature
  registra o limite e não o fecha.
- **FR-301**: O guardião MUST falhar quando existir campo na forma publicada sem natureza
  declarada, nomeando o campo e a coleção.
- **FR-302**: O guardião MUST falhar quando existir natureza declarada para campo que a forma
  publicada não possui.
- **FR-303**: O guardião MUST cobrir todas as coleções normativas, e NÃO DEVE depender de alguém
  lembrar de acrescentar a coleção nova à sua lista.
- **FR-304**: Todo campo classificado como retificável MUST ser alcançável pelo canal do ator —
  a tela de Retificação — e não apenas pela API.
- **FR-305**: O local do Evento do Cronograma MUST ser retificável pela tela.
- **FR-306**: Os requisitos de participação do Perfil MUST ser retificáveis pela tela.
- **FR-307**: A janela recursal declarada no marco — admissão, prazo e unidade — MUST ser
  retificável pela tela, e a unidade MUST ser oferecida como escolha entre os valores que o cálculo
  interpreta.
- **FR-308**: O método do sorteio declarado no marco MUST ser retificável pela tela, campo a campo.
- **FR-309**: Retificação do método do sorteio NÃO DEVE alcançar relação já congelada nem sorteio já
  realizado; ela vale para o que vier.
- **FR-310**: As exclusões vigentes cuja razão registrada é técnica MUST ser reexaminadas, e cada
  uma MUST ser reclassificada ou receber razão normativa.
- **FR-311**: Campo de valor fechado NÃO DEVE ser oferecido como texto livre; a escolha MUST ser
  conferida contra a lista que o cálculo interpreta.
- **FR-312**: A tela de Retificação MUST declarar, junto do bloco da entidade, quais campos daquela
  entidade não se corrigem por ali e a razão normativa de cada exclusão.
- **FR-313**: O contrato MUST declarar, para objeto normativo ausente no conteúdo publicado, se a
  declaração pode passar a existir por Retificação e por qual caminho.
- **FR-314**: Reclassificar a natureza de um campo NÃO DEVE alterar **conteúdo** já publicado. A
  classificação vigente governa os **atos futuros**, inclusive sobre Edital publicado antes dela:
  uma Retificação é ato novo, praticado hoje, sob a norma de hoje (D-011).
- **FR-315**: Reclassificar de "retificável" para "não retificável" MUST carregar, além da razão
  normativa, o registro de que um caminho de correção foi fechado — é a única direção de
  reclassificação que retira capacidade de quem já publicou.

### Key Entities

- **Forma publicada**: nesta spec, a forma que o conteúdo canônico de um Edital publicado tem de
  fato — a que a travessia encontra. **São 123 campos**, medidos em `publish_edital.py` e
  enumerados em [matriz.md](matriz.md). Os 81 a 98 que a auditoria contou são outra conta:
  ocorrências num Edital concreto, e não a união do que pode aparecer. Não é sinônimo de "declarada em `validation.py`": a declaração
  cobre seis coleções entre doze, e a forma publicada é maior do que ela (FR-300, D-005).
- **Campo publicado**: um campo escalar da forma publicada de uma coleção normativa. Tem nome, tipo
  e, a partir desta feature, natureza de mutabilidade e razão. Identificado pelo par
  `(coleção, campo)`, e não pelo nome sozinho — `name` existe em cinco coleções e `order` em três.
- **Natureza de mutabilidade**: uma das quatro de D-001. É atributo do campo na forma publicada, não
  do valor num Edital específico.
- **Razão**: o texto que sustenta uma natureza "não retificável". Normativa, e não técnica.
- **Guardião**: a verificação que compara a forma publicada com a forma classificada e falha por
  omissão em qualquer dos dois sentidos.

---

## 5. Invariantes observáveis

- Nenhum campo da forma publicada existe sem natureza declarada.
- Nenhuma natureza declarada aponta campo que a forma publicada não tem.
- Toda natureza "não retificável" tem razão escrita, e nenhuma razão escrita menciona limitação de
  implementação como fundamento.
- Todo campo classificado como retificável tem caminho pela tela.
- Retificação sobre método de sorteio não altera relação congelada nem sorteio realizado.
- Edital publicado permanece legível sob a classificação vigente quando ele foi publicado.

---

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-095**: Zero campos da forma publicada sem natureza declarada, verificável por execução da
  suíte.
- **SC-096**: Um campo novo acrescentado à forma publicada sem decisão faz a suíte falhar, nomeando
  o campo — verificável por tentativa.
- **SC-097**: Um servidor corrige o local de uma prova publicada pela interface administrativa, sem
  chamada de API e sem manipulação de banco, e o Cronograma público passa a exibir o novo local.
- **SC-098**: Um servidor corrige um requisito de participação publicado pela interface, e a página
  pública passa a exibir a lista corrigida enquanto a inscrição anterior continua apontando a
  versão que aceitou.
- **SC-099**: Um servidor corrige o prazo recursal publicado pela interface, e o candidato lê a data
  nova na tela de recurso.
- **SC-100**: Um servidor corrige o método do sorteio publicado pela interface, e a verificação
  pública de um sorteio já realizado continua conferindo contra o método que vigorava quando a
  relação foi congelada.
- **SC-101**: Toda exclusão registrada no contrato tem razão escrita, e nenhuma delas se funda em
  limitação de implementação.
- **SC-102**: Quem abre a Retificação de um Edital com marco declarado lê, no bloco do marco, o que
  não se corrige ali e por quê — sem precisar varrer a página para concluir que o campo não existe.

---

## 7. Out of Scope

- **Implementar a retificabilidade de todos os campos classificados.** Os quatro canários provam o
  desenho; o resto é backlog derivado do contrato, por natureza.
- **A spec estrutural de vagas.** Ela vem depois, e vem obrigada a obedecer este contrato.
- **A tela de composição do Edital.** Nada aqui muda a elaboração; o contrato é sobre o que acontece
  depois da publicação.
- **Os três itens deixados fora do PR #113** — adjacência × duplicação nas dicas do Perfil, prazo
  recursal na página pública do resultado, e o AVISO ligando "vagas imediatas" à linha do quadro.
  Continuam backlog de design e de regra.
- **Retroatividade.** Nenhuma reclassificação alcança Edital publicado sob classificação anterior.
- **Mudar a gramática de endereçamento.** A `004` já alcança tudo por identidade.

---

## Assumptions

- A travessia recursiva do conteúdo canônico de um Edital publicado é a fonte autoritativa do que
  se classifica (D-005). `editais/domain/validation.py` continua sendo a autoridade sobre a **forma**
  — tipo, nulabilidade, restrição — das seis coleções que declara, e esta feature não acrescenta
  declaração de forma nenhuma.
- O conjunto `NAO_SAO_NORMA` do guardião da Etapa é o precedente da natureza "identidade/estrutural"
  e "derivado", e será absorvido pelo contrato em vez de conviver com ele.
- As quatro naturezas de D-001 são suficientes para a forma publicada de hoje. Se algum campo não
  couber em nenhuma, isso é achado da feature e vira decisão registrada, não uma quinta natureza
  inventada em implementação.
- O ator das jornadas 1 a 4 é quem elabora — papel `retificacao:elaborar` —, com homologação e
  publicação pelos papéis próprios, como qualquer Retificação.
- A amostra real de Editais permanece a base de evidência para julgar se uma exclusão é normativa:
  um campo que nenhum Edital da amostra jamais corrigiu é candidato legítimo a "não retificável".

---

## 8. Ordem de implementação sugerida

1. **Enumerar pela travessia** — percorrer recursivamente o conteúdo canônico de um Edital
   publicado até o campo escalar, nas doze coleções. Sem isto não há o que classificar (D-005).
2. **Escrever o contrato** — natureza e razão para cada campo, nominalmente (D-008), reexaminando
   as exclusões de razão técnica (FR-310).
3. **Generalizar o guardião** — falha por omissão nos dois sentidos, cobrindo todas as coleções
   sem lista a manter à mão (FR-301 a FR-303).
4. **Canário 1: local do evento** — escalar simples, contradição limpa com a `021`.
5. **Canário 2: requisitos de participação** — coleção de texto.
6. **Canário 3: janela recursal** — objeto aninhado com valor fechado.
7. **Canário 4: método do sorteio** — objeto de dez campos, com a fronteira do congelamento.
8. **A tela declara o que não alcança** (FR-312), que só é possível depois de 2.

---

## 9. Gate de conclusão

A feature está concluída quando, **sem chamada de API e sem manipulação de banco**:

- um servidor corrige, pela interface administrativa, o local de uma prova, um requisito de
  participação, o prazo recursal e o método do sorteio de Editais publicados;
- o candidato lê, pelo portal, o efeito de cada uma dessas correções;
- acrescentar um campo à forma publicada sem decisão de natureza faz a suíte falhar nomeando o
  campo;
- e toda exclusão do contrato tem razão normativa escrita.
