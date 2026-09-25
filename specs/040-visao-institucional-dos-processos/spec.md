# Feature Specification: A visão institucional dos Processos Seletivos

**Feature Branch**: `claude/spec-processos-seletivos-visao-395a64`

**Created**: 2026-09-21

**Status**: Draft

> **Esta spec é o PRIMEIRO INCREMENTO, e os seus `MUST` obrigam só ele.** A revisão de 2026-09-21
> mediu a contradição: os requisitos obrigavam classificados, convocados, ocupação, requerimentos e
> série histórica, e a seção final os adiava — de modo que a implementação mínima **não satisfaria a
> própria spec**. Os indicadores adiados continuam **definidos** na §9, porque defini-los é o
> trabalho de investigação desta spec; eles apenas não são **obrigados** aqui. Ver `D-011`.
>
> **As proibições não são adiáveis, e por isso continuam `MUST`**: nenhum dado pessoal (`FR-584`),
> nenhum *matriculados* (`FR-592`), as quatro grafias de ausência (`FR-594`) e nenhum motor de
> alerta (`FR-603`). Guarda-corpo que sai junto com a capacidade é guarda-corpo que falta quando a
> capacidade volta.

**Input**: *"O sistema opera bem um Processo por vez e não responde como está o conjunto."* Investigação
conduzida contra o código — modelos, migrations, selectors, views, templates, política de papéis —
e contra a auditoria de convergência de 2026-09-20, que classifica a raiz estrutural **`E-6` visão
global** como 🟡 *parcial: reduziu, não fechou*.

> **Faixa de identificadores.** Esta spec abre em **FR-581** e **SC-206**. Teto medido em
> 2026-09-21 sobre `main` (`fa4b5b2`) **e** sobre as worktrees paralelas: `specs/` na `main` termina
> em `FR-567` / `SC-200` / `UX-066`, e a branch `claude/spec-039-alcance` — ainda **não mesclada** —
> toma mais treze requisitos, cinco critérios e dois identificadores de experiência acima desse
> teto. A faixa aberta aqui começa acima das duas, e os números que aquela branch reserva **não são
> citados nominalmente**: identificador ainda não definido em `specs/` derruba
> `tests/test_citacoes_de_requisito.py`, e a reserva é justamente o caso em que ele ainda não
> existe. As **decisões** reiniciam em `D-001`, como a convenção da feature manda.
>
> **Esta spec não define nenhum `UX-`.** O catálogo de sinais de Atenção é fechado por requisito
> (`FR-565` da `038`), e acrescentar espécie a ele seria alterar a `038` de fora. As marcas desta
> página são **aritmética sobre colunas que ela já apresenta**, e não sinais do catálogo — a
> distinção está em `D-007`.

---

## 1. Título e problema

**O sistema conduz um certame e não descreve o conjunto deles.**

Toda superfície de gestão existente pende de um agregado: a lista pende do escopo, o painel e a
Supervisão pendem do **Processo**, e inscrições, classificação, ocupação e convocação pendem do
**Edital**. Não existe nenhuma leitura acima do Processo — e é ali que moram as perguntas de quem
responde pela atividade de seleção da instituição:

> *Quantos Editais tivemos? Quantas vagas ofertamos? Quanta procura recebemos? Onde ela foi baixa?
> Quantas vagas conseguimos ocupar? Estamos ofertando mais ou menos que no ano passado?*

Nenhuma delas é respondível hoje sem abrir Processo por Processo e somar à mão.

---

## 2. Contexto

### 2.1 O que já existe, e que esta feature NÃO reconstrói

| Superfície | Nível | O que responde | Consequência para esta spec |
|---|---|---|---|
| `lista.html` (`/gestao/`) | escopo | quais Processos existem, e quantos Editais em cada situação | é a **vizinha**, e a única que chega perto do agregado — ela conta Editais por situação e nada mais |
| Painel de condução (`038`) | Processo | pulso por Edital + dez espécies de sinal de Atenção | **não duplicar**: ele diz o que está parado *dentro* de um Processo |
| Supervisão (`022`) | Processo | a mesma derivação, no recorte próprio | idem — `interface/supervisao.py` é **uma** derivação, lida por duas views |
| Vitrine do portal (`024`) | público | seleções publicadas, com vagas e prazo | é o precedente técnico da leitura em massa de conteúdo publicado |
| Inscrições recebidas (`009`) | Edital | total, por Perfil, por modalidade | a visão **soma**, e não recalcula |
| Ocupação (`016`) e Convocação (`019`) | recorte | os quatro números do recorte, com estado | a visão soma as apurações vigentes; a leitura por recorte continua lá |

**A frase que governa o corte:** a `022` e a `038` observam **a fronteira entre as features dentro
de um Processo**. Esta feature observa **a fronteira entre os Processos**. São níveis diferentes, e
é a ausência do nível — e não a falta de superfície — que a `E-6` nomeia.

### 2.2 A objeção registrada, e por que ela não alcança esta feature

A auditoria de 20/09 escreve, no §20: *"Não recomendo outro painel. O problema da `038` não é falta
de superfície — é que a superfície existente não é acionável nem honesta sobre o que não mostra."*

**A objeção é sobre acrescentar linhas a uma região de sinais cujo encaminhamento já falha 60% das
vezes**, e ela continua válida: esta spec **não toca** na região de Atenção, não acrescenta espécie
ao catálogo e não cria segundo encaminhamento. O que ela acrescenta é o nível que a mesma auditoria
mede como ausente — e as duas lições dela entram como requisito: **ser honesta sobre o que não
mede** (`FR-596`) e **não oferecer caminho que o ator não abre** (`FR-605`).

---

## 3. Evidências encontradas no código

### 3.1 A terminologia real, reconstruída

| Termo do briefing | Existe? | O que existe de fato |
|---|---|---|
| **Processo Seletivo** | ✅ | `processos.ProcessoSeletivo` — `EM_ELABORACAO` · `ATIVO` · `ENCERRADO` · `CANCELADO`; `institution_scope`, `institutional_code`, `title`, `created_at` |
| **Edital** | ✅ | `processos.Edital` — `EM_ELABORACAO` · `EM_REVISAO` · `HOMOLOGADO` · `PUBLICADO` · `ENCERRADO` · `CANCELADO`; `number`, `year`; FK para o Processo |
| **oferta** | ❌ | **não existe com esse nome.** O que existe é **Perfil de Vaga** (`editais.PerfilVaga`). Usar "oferta" criaria segundo termo para o mesmo conceito — o Princípio I proíbe |
| **Perfil** | ✅ | `PerfilVaga` — `immediate_vacancies`, `reserve_type` (`NONE`/`LIMITED`/`UNLIMITED`), `reserve_limit`, `locality`, `duties`, `workload`, `compensation` |
| **Modalidade** | ✅ | `ModalidadeConcorrencia`, por Perfil; e `LinhaDoQuadroDeVagas`, onde **`modalidade` nula É a ampla concorrência** — não ausência |
| **Vaga** (entidade) | ❌ | **recusa registrada**, com todas as letras, em `convocacao/models.py`: *"Vaga individual não é entidade… o Edital publica quantidade e o sistema conhece conjunto de pessoas"*. Existe **quantidade**, nunca uma vaga numerada |
| **Inscrição** | ✅ | `inscricoes.Inscricao` — **dois estados e nada mais**: `RASCUNHO` e `SUBMETIDA` |
| **Inscrição submetida** | ✅ | `status=SUBMETIDA`, e o estado é **inalcançável** sem `submitted_at`, protocolo, versão aceita e aceite das declarações — `ck_inscricao_submetida_completa` |
| **Inscrição cancelada / invalidada** | ❌ | **o estado não existe no domínio.** O inventário da `022` já registrava: *"Quantas canceladas? — SEM FATO"* |
| **Candidato** | ✅ | `identidade.CandidateIdentity` — `subject` opaco e estável; `cpf_normalizado` **declarado, nunca provado, e não único** |
| **Habilitado** | ⚠️ | existe **só no sorteio** (`sorteios.ParticipanteHabilitado`, `RelacaoDeHabilitados`) e como leitura de Etapa (`habilitadas_na_etapa`). **Não é estado institucional do candidato** |
| **Classificado** | ✅ | `divulgacao.SituacaoDivulgada.CLASSIFICADA` — quem recebeu posição **naquilo que foi divulgado**. Antes da divulgação existe `PosicaoNaOrdem.posicao`, que é ato emitido e ainda não público |
| **Aprovado** | ❌ | **nenhum termo no domínio.** Não há `APROVADO` em modelo, domínio ou template algum |
| **Convocado** | ✅ | `convocacao.Convocacao` — raiz vigente; espécies `VAGA_INICIAL`, `SUPLENCIA`, `PARA_REGULARIZAR`; o campo `chamada` existe porque **a mesma pessoa é legitimamente chamada mais de uma vez** |
| **Ocupação de vaga** | ✅ | `ocupacao.ApuracaoDeOcupacao` — `publicadas`, `efetivas`, `ocupadas`; `faltando` é derivado e **nunca** coluna |
| **Suplente** | ⚠️ | existe como **espécie de convocação** (`SUPLENCIA` — *"para vaga que vagou"*), não como estado de pessoa |
| **Requerimento de matrícula** | ✅ | `requerimentos.RequerimentoDeMatricula`, com rascunho, envio e sucessão. **Só existe onde o Edital declarou `requerimento_momento`** |
| **Matrícula efetivada** | ❌ | **não existe, e a ausência é decisão.** O que existe é `matriculas.GeracaoDeArquivo` — *"O registro de que um arquivo de importação foi gerado — e nada além dele"*. A própria auditoria marca a integração com o Registro Acadêmico como `[NÃO VALIDADO]` |
| **Unidade / campus / polo** | ⚠️ **existe acima, não existe abaixo** | `institution_scope` **é** eixo de unidade, e o portal já o usa como filtro — `portal/views.py` monta `"unidade": versao.edital.institution_scope.upper()`, e a vitrine é cross-scope. Mas a gestão é **confinada a um escopo** (`FR-583`), e ali a unidade é **constante**: o filtro teria sempre uma opção. O que não existe é dimensão **abaixo** do escopo — campus ou polo dentro da mesma unidade —, que é o que `AX-6`/`ACH-60` discutem e o que `PerfilVaga.locality` guarda em texto livre |
| **Tipo / família do Processo** | ❌ | **não existe taxonomia**, e está escrito no modelo: *"O sistema não tem taxonomia de natureza do Processo, e criá-la seria inventar um eixo que nenhuma outra feature consome"* (`Edital.requerimento_momento`) |
| **Ano / semestre de ingresso** | ❌ | não existe nenhum dos dois. `Edital.year` é o ano **do número do Edital** (`66/2026`) |

### 3.2 Os quatro fatos estruturais que decidem o desenho

**a) Tudo o que se quer contar pende do Edital, não do Processo.** `Inscricao`, `AtoDeOrdenacao`,
`ApuracaoDeOcupacao`, `Convocacao`, `PublicacaoResultado` e `GeracaoDeArquivo` têm FK para `Edital`.
O `ProcessoSeletivo` não tem data, não tem vaga e não tem prazo — a `022` já registrou por escrito
que *"não existe marco do Processo"*.

**b) Vaga publicada só existe no conteúdo publicado.** A Retificação *não reescreve o relacional*:
`PerfilVaga.immediate_vacancies` é a linha de elaboração, e o que o Edital **publicou** está na
`VersaoConsolidada.content`, em `profiles[].immediateVacancies`. O portal já lê exatamente assim
(`portal/views.py`), e a `016` também (`ocupacao_do_recorte`).

**c) O projeto já decidiu como se grafa um número que nenhum ato produziu**, e a frase é literal em
`ocupacao/application/selectors.py`:

> *"Quantidade que nenhum ato produziu vem **nula**, e nunca zero. Zero é uma afirmação — «não há
> vaga a ocupar» —, e sem apuração emitida ninguém afirmou isso."*

Esta feature herda a regra inteira. É a diferença entre um painel gerencial e um painel que parece
saber.

**d) O custo de leitura já foi medido, e é linear.** A auditoria registra **~17 consultas por Edital
publicado**, com a nota *"medir antes de um Processo grande"*. Uma visão que percorresse Editais com
o custo de hoje seria inviável na primeira dezena — e é por isso que `FR-582`, `FR-598` e `SC-209`
existem.

### 3.3 Autorização, como o sistema a representa hoje

Sete papéis, em `interface/identidade.py::PAPEIS`, cada um um conjunto fixo de permissões:

| Papel | Permissões |
|---|---|
| `elaborador` | `edital:elaborar`, `edital:submeter`, `retificacao:elaborar`, `retificacao:submeter` |
| `homologador` | `edital:homologar`, `retificacao:homologar` |
| `publicador` | `edital:publicar`, `retificacao:publicar`, `resultado:publicar` |
| `gestor` | `inscricao:consultar`, `processo:*`, `edital:criar|encerrar|cancelar`, `retificacao:cancelar`, `comissao:gerir` |
| `julgador` | `recurso:julgar` |
| `auditor` | `auditoria:consultar` |
| `exportador` | `matricula:exportar` |

**Não existe "Coordenação de Seleção" nem "Diretoria".** A presidência da comissão **não é papel** —
vem do vínculo, objeto a objeto (`comissoes`). E o repositório já registra duas vezes o padrão a
seguir quando uma capacidade é de natureza distinta: `julgador` e `exportador` nasceram como papéis
**próprios**, e nenhum papel existente ganhou a permissão. Ver `D-008`.

---

## 4. O mapa dos dados disponíveis

A matriz que impede esta spec de transformar expectativa gerencial em dado fictício.

| Indicador desejado | Existe hoje? | Fonte canônica | Confiabilidade | Aplicabilidade | Observação |
|---|---|---|---|---|---|
| **Processos** | ✅ | `ProcessoSeletivo` filtrado por `institution_scope` | alta | todos | é contagem de linha |
| **Editais** | ✅ | `Edital` | alta | todos | `Edital.status` distingue os seis estados |
| **Vagas imediatas publicadas** | ✅ | `Σ profiles[].immediateVacancies` da **versão consolidada vigente** | alta | **só Edital com conteúdo publicado** | Perfil com `0` vaga imediata e cadastro reserva é *"oportunidade legítima e frequente"* (`FR-136` da `024`) |
| **Cadastro de reserva** | ✅ | `profiles[].reserveType` / `reserveLimit` | alta | por Perfil | `UNLIMITED` **não tem denominador** |
| **Inscrições submetidas** | ✅ | `Inscricao.status = SUBMETIDA` | **muito alta** — garantida por `CHECK`, não por convenção | todo Edital que recebeu inscrição | é o número institucional |
| **Rascunhos** | ✅ | `Inscricao.status = RASCUNHO` | alta | idem | operacional, nunca no número principal; a tela dona os chama **"Em preenchimento"** |
| **Pessoas distintas** | ⚠️ **parcial** | `COUNT(DISTINCT cpf_normalizado)` sobre submetidas | **média** — o CPF é declarado e nunca provado; `CandidateIdentity.cpf_normalizado` **não é único**; a reconciliação *"relata sem interromper"* grupos com mais de um `subject` | agregado | ver `D-006` |
| **Relação inscrições/vaga** | ✅ derivado | submetidas ÷ vagas publicadas | alta **onde o denominador existe** | ❌ **não aplicável** a Perfil só com cadastro de reserva | nunca `0`, nunca `∞` |
| **Classificados** | ✅ | `SituacaoDivulgada.situacao = CLASSIFICADA`, nas `PublicacaoResultado` **vigentes** (`sucessoras__isnull=True`) | alta | **só após a divulgação** | contar **inscrições distintas**: a mesma pessoa aparece em ampla e em reservada |
| **Ordenados e ainda não divulgados** | ✅ | `PosicaoNaOrdem.posicao IS NOT NULL` no `AtoDeOrdenacao` vigente | alta | após a emissão | **é outra grandeza**, e não entra como "classificados" — o ato emitido não é público |
| **Convocados** | ✅ | `Convocacao` raiz vigente (`convocacao_anterior IS NULL`) | alta | só após a convocação | contar **inscrições distintas**: `chamada` cresce quando a mesma pessoa é chamada de novo |
| **Vagas publicadas / efetivas / ocupadas** | ✅ | `ApuracaoDeOcupacao` **vigente** do recorte | alta | **só recorte apurado** | `efetivas ≠ publicadas` quando houve reversão (`FR-239a`) |
| **Vagas faltando** | ✅ derivado | `efetivas − ocupadas`, nunca negativo | alta | idem | é `@property`, e **não é coluna**, de propósito |
| **Requerimentos de matrícula enviados** | ✅ | `RequerimentoDeMatricula` com `enviado_em` | alta | **só Editais que declaram `requerimento_momento`** | ausência da declaração significa *"este Edital não exige"*, nunca *"faltou"* |
| **Matrículas efetivadas** | ❌ **NÃO EXISTE** | — | — | — | o sistema **gera um arquivo** e não guarda nem o arquivo nem a resposta do destino. Integração `[NÃO VALIDADO]`. **Não apresentar, e declarar a ausência** (`FR-592`, `SC-212`) |
| **Aprovados** | ❌ **NÃO EXISTE** | — | — | — | o termo não está no domínio |
| **Por unidade / campus / polo** | ❌ | — | — | — | não há dimensão; `locality` é texto livre por Perfil |
| **Por tipo / família de Processo** | ❌ | — | — | — | não há taxonomia, e o modelo diz por escrito que criá-la seria inventar eixo |
| **Por ano/semestre de ingresso** | ❌ | — | — | — | *"Processos de 2026/2"* **não é consultável** — ver `G-005` |

### 4.1 As âncoras temporais que o domínio tem

| Data | Onde | Serve de filtro? |
|---|---|---|
| **Ano do Edital** | `Edital.year` — coluna | ✅ **sim, e é a escolhida** (`D-004`): é como a instituição nomeia o Edital (`66/2026`), é coluna indexável, não se move por Retificação e existe em **todo** Edital, inclusive o não publicado |
| Publicação original | `Publicacao.published_at` com `publication_order = 1` | ⚠️ só existe para o publicado; é o instante exato, e entra como **coluna**, não como recorte |
| Período de inscrições | Evento com `isRegistrationPeriod` no conteúdo vigente | ✅ como **situação** (futuro/aberto/encerrado/não designado), não como intervalo de filtro |
| Nascimento do rascunho | `Edital.created_at`, `ProcessoSeletivo.created_at` | ❌ não é fato institucional — é quando alguém abriu a tela |

---

## 5. Objetivo

Uma página institucional — **Processos Seletivos → Visão Geral** — que responda *"como estão os
Processos Seletivos da instituição?"*, servindo à Coordenação de Seleção e à Diretoria pela mesma
tela, com **todo número rastreável à sua fonte de domínio** e **toda ausência declarada como
ausência**.

**O objetivo desta entrega é a camada de dimensão e demanda**: quantos Editais, quantas vagas,
quanta procura, onde ela faltou — e a tabela de onde se chega ao Edital. As camadas de **resultado**
(classificados, convocados, ocupação) e de **histórico** (a série por ano) estão **definidas** na §9
e **registradas** como incremento seguinte (`D-011`), porque a investigação que as define é desta
spec e a obrigação de entregá-las não é.

## 6. Não objetivos

- Não é um segundo painel do Processo: a `022` e a `038` continuam donas daquele nível.
- Não é ferramenta de BI, e não é o caminho para uma.
- Não cria conceito, estado, entidade ou eixo que o domínio não tenha.
- Não apresenta indicador que o sistema não possa sustentar — e **declara** os que não pode.
- Não nomeia pessoa responsável: o produto não liga identidade a papel operacional, e a `038` já
  registrou essa recusa (`FR-564`).

---

## 7. Personas e papéis

| Persona | O que ela pergunta | Como a página responde |
|---|---|---|
| **Coordenação de Seleção** | volume, demanda, onde a procura foi baixa, o que está aberto, o que pede atenção | **a tabela** — é o instrumento dela, e a leitura acontece linha a linha |
| **Diretoria / gestão** | dimensão da atividade, e — no incremento seguinte — evolução e capacidade de ocupação | **os indicadores consolidados** — o topo da página, sem descer à tabela |

**Uma tela, e não duas.** A hierarquia visual faz o trabalho da separação: quem quer dimensão lê e
para; quem quer portfólio desce. Duas telas exigiriam duas derivações do mesmo número — o defeito
que `FR-582` existe para impedir.

---

## User Scenarios & Testing *(mandatory)*

> **Seção acrescentada em 21/09, ao planejar.** A redação anterior desta spec tinha personas (§7),
> critérios (§17) e cenários (§18), e **não tinha as jornadas priorizadas** que o template exige e
> das quais as tarefas se organizam. A lacuna é real e é minha: sem ela, `/speckit-tasks` teria de
> inventar o recorte de entrega, que é exatamente a decisão que não se delega.
>
> As três jornadas abaixo **não acrescentam escopo**: cada uma é um recorte dos `MUST` da §14, e as
> três juntas são exatamente eles.

### User Story 1 — Quanto ofertamos, e quanta procura recebemos (Priority: P1) 🎯 MVP

Quem responde pela seleção abre uma tela e lê, do ano corrente: quantos Editais houve, quantas vagas
foram publicadas, quantas inscrições chegaram e qual foi a relação por vaga — e desce para a tabela
onde cada Edital se explica e de onde se chega a ele.

**Why this priority**: é a pergunta que dá nome à feature, e a única cuja ausência obriga hoje a
abrir Processo por Processo e somar à mão. Sozinha ela já entra em produção.

**Independent Test**: com o `seed_demo` aplicado, abrir `/gestao/visao-geral` como `gestor` e obter
os quatro números e a tabela, sem tocar em nenhum outro Edital; conferir cada número contra a tela
dona daquele fato.

**Acceptance Scenarios**:

1. **Given** um escopo com Editais do ano corrente e de anos anteriores, **When** a página é aberta
   sem parâmetro, **Then** ela recorta pelo ano corrente e **declara o recorte aplicado**.
2. **Given** um Edital em elaboração, **When** a tabela o apresenta, **Then** Vagas e Inscr./vaga
   saem como `—` com o motivo, e **nunca** como `0`.
3. **Given** um Edital publicado sem nenhuma inscrição, **When** a tabela o apresenta, **Then**
   Submetidas sai como `0`, porque a contagem existe.
4. **Given** um Edital com inscrições abertas, **When** a tabela o apresenta, **Then** Submetidas é
   marcada **parcial** e o consolidado declara quantos somandos são parciais.
5. **Given** um Edital com um Perfil de vagas imediatas e outro só de cadastro de reserva,
   **When** a razão é calculada, **Then** ela usa apenas a demanda do primeiro, e a linha declara a
   população usada.
6. **Given** qualquer linha da tabela, **When** ela é acionada, **Then** chega-se ao Edital
   correspondente.

---

### User Story 2 — Onde a procura faltou (Priority: P2)

A mesma pessoa varre a tabela procurando o que pede atenção: o Edital que encerrou sem ninguém, e o
que encerrou com menos candidatos do que vagas.

**Why this priority**: é a segunda pergunta que a Coordenação faz, e ela **depende** da tabela da
`US1` existir. Custa aritmética sobre colunas já apresentadas — mas sem a `US1` não há sobre o que
operar.

**Independent Test**: semear um Edital com período encerrado e zero submetidas e outro com razão
menor que 1, abrir a página e identificar os dois **sem** usar cor — lendo o texto.

**Acceptance Scenarios**:

1. **Given** um Edital com período encerrado e zero inscrições submetidas, **When** a tabela o
   apresenta, **Then** a linha traz a marca de **sem procura**, legível sem cor.
2. **Given** um Edital com período encerrado e razão menor que 1, **When** a tabela o apresenta,
   **Then** a linha traz a marca de **demanda abaixo da oferta**.
3. **Given** um Edital com período **aberto** e zero submetidas, **When** a tabela o apresenta,
   **Then** **não** há marca: o número ainda vai mudar.
4. **Given** qualquer marca, **When** a página é lida, **Then** ela **não** tem identificador de
   catálogo, destino próprio nem grau de severidade.

---

### User Story 3 — Recortar o período e o portfólio (Priority: P3)

Quem prepara um relatório troca o ano, filtra por situação do Edital ou do período de inscrições,
busca por nome, e ordena a tabela pela coluna que lhe interessa.

**Why this priority**: amplia o alcance da `US1` sem a qual não existe, e é o que torna a página
utilizável fora do ano corrente — inclusive para a comparação histórica que a série, adiada, fará
melhor depois.

**Independent Test**: com Editais de dois anos no acervo, trocar o ano e verificar que consolidado e
tabela mudam **juntos** e concordam; ordenar por Inscr./vaga nos dois sentidos e verificar onde as
ausências ficam.

**Acceptance Scenarios**:

1. **Given** um acervo com dois anos, **When** o outro ano é escolhido, **Then** consolidado e
   tabela mudam juntos e concordam entre si.
2. **Given** um parâmetro de consulta inválido, **When** a página é aberta, **Then** o valor é
   saneado para o padrão e **não** alcança a consulta.
3. **Given** uma coluna com ausências, **When** a ordenação é aplicada em qualquer sentido,
   **Then** as ausências ficam **ao fim**.
4. **Given** o filtro por situação do período, **When** ele é aplicado, **Then** o resultado é
   correto — e o recorte relacional já reduziu o conjunto antes de qualquer snapshot ser aberto.

---

### Edge Cases

> **A seção Edge Cases não entra na matriz de `FR-`/`SC-` e nenhuma ferramenta a cobra** — por isso
> cada caso abaixo aponta o requisito que o governa, e os cenários de teste da §18 os exercitam.

- **Recorte vazio** — nenhum Edital no ano escolhido: a página se explica, e **não** apresenta `0`
  como se fosse resposta sobre o acervo (`FR-594`, `T-10`).
- **Edital cancelado** — continua na tabela: ele consumiu vagas publicadas e recebeu inscrições, e
  escondê-lo faria o agregado mentir sobre o que houve (`R-003`).
- **Edital de ano futuro** — um `01/2027` em elaboração não aparece no padrão, e aparece quando 2027
  é escolhido; o seletor o oferece porque o ano existe na coluna (`FR-599`).
- **Edital retificado** — vagas são as da versão **vigente**, nunca as da publicação original
  (`FR-587`, `T-07`).
- **Perfil com `0` vaga imediata e cadastro de reserva ilimitado** — vagas `0` é zero legítimo, e a
  razão é **não aplicável** (`FR-589`, `T-02`).
- **Todos os Editais do recorte sem denominador** — o consolidado apresenta a razão como não
  aplicável e diz quantos ficaram de fora (`FR-590`).
- **Duas inscrições da mesma pessoa** em Perfis distintos do mesmo Edital — contam **2**: são
  inscrições, e a página não afirma pessoas (`FR-593`, `T-06`).
- **Ator sem a capacidade que monta a URL à mão** — recebe `403` explicado, e não `404` nem `500`
  (`FR-604`, `FR-605`).

---

## 8. Modelo mental da página

```text
  Filtros            ano (padrão: o corrente) · situação do Edital · situação do período · busca
       ↓
  Consolidado        quatro números, com os denominadores ditos abaixo de cada um
       ↓
  Tabela             uma linha por Edital → leva ao Edital

  ── registrado, e não desta entrega ────────────────────────────────
  Por ano            Editais · vagas · submetidas · inscr./vaga  (D-011, D-013)
  Colunas de fase    classificados · convocados · ocupação        (D-011)
```

**A tabela é o centro.** O consolidado é a resposta curta; a tabela é onde a resposta se explica e
de onde se sai para o caso concreto.

---

## 9. Definição formal de cada indicador, e sua fonte canônica

A coluna **Entrega** separa o que esta spec **obriga** do que ela **define e registra**. Definir é o
trabalho da investigação; obrigar é o contrato do plano. Confundi-los foi o defeito que a revisão de
21/09 encontrou.

| # | Indicador | Fórmula | Denominador | Fonte | A partir de quando é confiável | Entrega |
|---|---|---|---|---|---|---|
| 1 | Editais no recorte | contagem de `Edital` | — | `listar_processos` | sempre | **obrigado** |
| 2 | Processos representados | `COUNT(DISTINCT processo_id)` dos Editais do recorte | — | idem | sempre | **obrigado** — como contexto, não como número grande (`D-012`) |
| 3 | Editais com conteúdo publicado | contagem dos que têm `VersaoConsolidada` vigente | indicador 1 | `versoes_vigentes` | sempre | **obrigado** — é o **denominador de 4**, e é assim que aparece. *O denominador de 6 é o 4b, e não este: confundi-los foi um defeito real desta tabela* |
| 4 | Vagas imediatas publicadas | `Σ profiles[].immediateVacancies` | indicador 3 | `VersaoConsolidada.content` | desde a publicação; muda só por Retificação | **obrigado** |
| 4b | Perfis com vaga imediata | contagem de `profiles` com `immediateVacancies > 0` | Perfis publicados | idem | idem | **obrigado** — é o denominador de 6 (`D-012`) |
| 5 | Inscrições submetidas | `COUNT(Inscricao WHERE status=SUBMETIDA)` | — | `Inscricao` | sempre; **definitivo** quando o período encerra | **obrigado** |
| 5b | Em preenchimento | `COUNT(... status=RASCUNHO)` | — | idem | operacional; some quando o período encerra | **obrigado** |
| 6 | Inscrições por vaga | `Σ submetidas em Perfis com vaga imediata ÷ Σ vagas imediatas` | vagas imediatas publicadas | derivado, recortado por `Inscricao.profile_id` | quando o período encerra; **parcial** antes | **obrigado** — com o numerador recortado (`D-012`) |
| 7 | Inscrições classificadas em resultados divulgados | `COUNT(DISTINCT inscricao)` em `SituacaoDivulgada` `CLASSIFICADA` de `PublicacaoResultado` vigente | — | `divulgacao` | a partir da primeira divulgação | **registrado** — e **não** é classificação final (`G-012`) |
| 8 | Inscrições convocadas | `COUNT(DISTINCT inscricao)` em `Convocacao` raiz vigente | — | `convocacao` | a partir da primeira convocação | **registrado** |
| 9 | Vagas efetivas apuradas | `Σ ApuracaoDeOcupacao.efetivas` das vigentes | recortes com apuração | `ocupacao` | a partir da primeira apuração | **registrado** |
| 10 | Vagas ocupadas | `Σ ApuracaoDeOcupacao.ocupadas` das vigentes | indicador 9 | idem | idem | **registrado** |
| 11 | Vagas faltando | indicador 9 − indicador 10, nunca negativo | indicador 9 | derivado | idem | **registrado** |
| 12 | Taxa de ocupação | indicador 10 ÷ indicador 9 | vagas efetivas **apuradas** | derivado | idem — **e o denominador é dito, porque não é o total de vagas publicadas** | **registrado** |
| 13 | Requerimentos enviados | `COUNT(RequerimentoDeMatricula WHERE enviado_em IS NOT NULL)` | Editais que declaram `requerimento_momento` | `requerimentos` | onde a declaração existe | **registrado** |
| 14 | Pessoas distintas | `COUNT(DISTINCT cpf_normalizado)` sobre submetidas | — | `Inscricao` | erro não mensurável — ver `D-006` | **registrado**, e decisão do usuário (`G-003`) |
| — | *Matrículas efetivadas* | **não há fórmula** | — | **não há fonte** | **nunca** | **proibido** — `FR-592` |

### 9.1 As três notas que os números adiados não perdem por serem adiados

**Sobre 7 — o número existe e não significa o que um diretor vai ler.** `divulgacao` escreve, com
todas as letras: *"Um Edital pode ter vários marcos classificatórios, e cada um é ato pleno:
publicados o intermediário e o final, a Inscrição tem duas linhas vigentes."* Quem foi classificado
na etapa documental e eliminado na prova seguinte **continua** na contagem, e o rótulo
*"387 classificados"* seria lido como resultado final. Por isso o indicador se chama **inscrições
classificadas em resultados divulgados** e por isso ele não entra no consolidado desta entrega
(`G-012`).

**Sobre 7 e 8 — são inscrições, e não pessoas.** `DISTINCT inscricao` conta inscrições. A mesma
pessoa pode ter **mais de uma inscrição no mesmo Edital** — a restrição
`uq_inscricao_identidade_edital_perfil` é por **Perfil**, e o teto por Edital é opcional
(`Edital.max_inscricoes_por_candidato`, nulo significa sem limite). Contagem de pessoas é o
indicador 14, é outra grandeza, e tem outra confiabilidade.

**Sobre 9, 10 e 12.** A soma é das apurações **vigentes**, e a apuração vigente pode estar obsoleta
por cinco causas que a `016` já nomeia. Esta página **não** recomputa obsolescência — seria
reimplementar `causas_de_obsolescencia` num recorte institucional —, e por isso **declara** que a
Supervisão de cada Processo é quem a reporta (`FR-596`). Declarar o limite é a diferença entre um
número parcial e um número falso.

---

## 10. Filtros

| Filtro | Valores | Por que este | Por que só este |
|---|---|---|---|
| **Ano do Edital** | os anos presentes em `Edital.year` | coluna, estável, é como a instituição nomeia o Edital | ano/semestre de ingresso **não existe** (`G-005`) |
| **Situação do Edital** | os seis valores de `Edital.Status` | vocabulário existente, já usado por `lista.html` | nenhum estado novo |
| **Situação do período** | futuro · aberto · encerrado · não designado | os quatro do domínio da `009`, lidos por `periodo_de_inscricoes` | é a pergunta *"o que está aberto?"*, e ela não é a mesma que a situação do Edital |
| **Busca** | texto sobre título do Processo, código institucional e número do Edital | é como a pessoa já se refere ao certame | nunca sobre dado de candidato |

**Recusados, com a razão:** campus/unidade (não há dimensão), tipo/família (não há taxonomia),
modalidade (existe por Perfil, e um filtro institucional por ela exigiria o catálogo que a `039`
ainda discute), intervalo de datas livre (transformaria a página em construtor de consulta).

### 10.1 O recorte inicial

**Ao abrir sem parâmetro, a página mostra o ano corrente** (`D-013`). Não é preferência de tela: o
custo dominante desta feature é abrir um snapshot por Edital do recorte, e *"todos os anos"* por
omissão faria o custo crescer com a história institucional para sempre — exatamente o risco que
`FR-598` existe para conter.

As opções do seletor saem de `DISTINCT Edital.year` no escopo — uma consulta de uma coluna, sem
snapshot nenhum —, e **"Todos"** é oferecido como escolha explícita. A página declara qual recorte
está aplicado, para que ninguém leia *"12 Editais"* como o acervo inteiro.

**O Edital de ano futuro não desaparece**: um `01/2027` em elaboração aparece quando 2027 é
escolhido, e o seletor o oferece porque o ano existe na coluna.

---

## 11. A tabela principal

**A linha é o Edital** (`D-001`), com o Processo nomeado nela.

### 11.1 As sete colunas desta entrega

| Coluna | Conteúdo | Quando não se aplica |
|---|---|---|
| **Processo / Edital** | título do Processo + `nº/ano`, link para o Edital | — |
| **Situação** | `Edital.status`, no vocabulário de `lista.html` | — |
| **Período** | situação do período + prazo, quando declarado | `—` sem cronograma vigente ou sem Evento designado |
| **Vagas** | vagas imediatas publicadas. *A marca de cadastro de reserva **saiu na `041`**: ela dizia "algum Perfil tem reserva", e a espécie agora é do Perfil, com as três distinguíveis na expansão* | `—` sem conteúdo publicado. `0` é resposta verdadeira num Perfil só de cadastro de reserva |
| **Submetidas** | contagem; marcada **parcial** com o período aberto | `0` é resposta verdadeira — a contagem existe |
| **Em preenchimento** | contagem de rascunhos | idem |
| **Inscr./vaga** | razão, com uma casa, **sobre os Perfis com vaga imediata** | `—` quando nenhum Perfil tem vaga imediata, ou sem conteúdo publicado |

### 11.2 As três colunas registradas, e não obrigadas

Definidas na §9 (indicadores 7 a 12) e entregues no incremento seguinte (`D-011`): **inscrições
classificadas em resultados divulgados**, **inscrições convocadas** e **ocupadas / efetivas**. Entram
como colunas da mesma tabela, sem mudança estrutural — é por isso que adiá-las não gera retrabalho.

### 11.3 A comparabilidade se preserva por não preencher

**Nenhuma coluna é forçada a todas as famílias.** Um Edital de bolsistas ainda tem vagas e demanda;
um Edital só com cadastro de reserva tem demanda e **não tem** relação candidato/vaga. A
comparabilidade se preserva por **não** preencher o que não existe — nunca por preencher com valor
que nenhuma fonte produziu.

---

## 12. Comportamento dos agregados

1. **A soma só soma o que existe**, e **declara o denominador**: *"4.310 vagas em 9 dos 12 Editais
   do recorte — 3 não têm conteúdo publicado."*
2. **Fluxo e estoque não se misturam.** Submetidas é fluxo e continua crescendo enquanto o período
   está aberto; vagas ocupadas é estoque de uma apuração datada. O consolidado **conta quantos dos
   seus somandos são parciais** e o diz: *"inclui 2 Editais com inscrições abertas."*
3. **Razão nenhuma é média de razões.** `inscr./vaga` do recorte é `Σ numerador ÷ Σ vagas`, e não a
   média das razões por Edital — a média daria peso igual a um Edital de 2 vagas e a um de 200.
4. **E o numerador é recortado, nos dois níveis** (`D-012`). Inscrição em Perfil que **não tem vaga
   imediata** não disputa vaga nenhuma, e somá-la ao numerador produz número correto e
   institucionalmente falso. O recorte vale por Edital **e** no consolidado: os dois calculados de
   formas diferentes discordariam, e no consolidado ninguém percebe a olho.
5. **Contagem de inscrições é `DISTINCT` sobre a inscrição; contagem de pessoas é outra coisa.** A
   mesma inscrição aparece em mais de um recorte (ampla e reservada) e recebe mais de uma chamada —
   daí o `DISTINCT`. Mas ele conta **inscrições**: a mesma pessoa pode ter mais de uma inscrição no
   mesmo Edital, porque a unicidade é por **Perfil**. Pessoas é o indicador 14, e tem outra fonte e
   outra confiabilidade.

---

## 13. Dados parciais, indisponíveis e não aplicáveis

**A regra não é "zero não existe". É esta:**

> **Zero é válido quando a fonte canônica produziu zero. Ausência é para quando nenhum fato produziu
> o número, ou quando a métrica não se aplica àquele objeto.**

É a frase da `016` lida inteira: *"Zero é uma afirmação — «não há vaga a ocupar» —, e **sem apuração
emitida ninguém afirmou isso**"*. O defeito não é escrever zero; é escrever zero **no lugar de** um
fato que não existe.

Zeros legítimos, todos produzidos por alguma fonte: `0` inscrições submetidas num Edital publicado;
`0` vagas imediatas num Perfil de cadastro de reserva; `0` ocupadas numa apuração **emitida** que
nada ocupou; `0` classificados num resultado **divulgado** que não classificou ninguém. Apagar
qualquer um deles esconderia justamente o caso que a Coordenação precisa ver.

**Quatro ausências, quatro grafias** — e nenhuma delas se escreve `0`:

| Ausência | O que significa | Grafia |
|---|---|---|
| **Não aplicável** | o indicador não faz sentido aqui — Edital só com cadastro de reserva não tem denominador | `—` com explicação acessível *"não se aplica: cadastro de reserva sem vaga imediata"* |
| **Ainda não disponível** | a fase não chegou — não houve divulgação, não houve apuração | `—` com *"ainda não divulgado"* / *"ocupação ainda não apurada"* |
| **Não publicado** | o Edital não tem conteúdo vigente, e vaga publicada não existe fora dele | `—` com *"sem conteúdo publicado"* |
| **Parcial** | o número existe e ainda vai mudar | o número, com a marca textual **parcial**. O motivo MUST ser legível **na linha**, e MUST NOT ser repetido ao lado do número quando uma coluna vizinha já o disser |

> **Emenda (042).** A redação original mandava escrever *"a marca textual **parcial** e o motivo"*
> ao lado do número, e a tela o fazia: *"parcial — as inscrições ainda estão abertas"*. Medido, essa
> frase ocupava **73 px** numa célula de 108 px — **52%** da altura da linha —, em prosa alinhada à
> direita, para ressalvar um número.
>
> E era redundante por construção, não por acaso: existe **um** único motivo de parcialidade nesta
> tela, e ele é atribuído exatamente quando o período está aberto — que é exatamente quando a coluna
> *Período de inscrições*, duas à esquerda na mesma linha, escreve *"Inscrições abertas até
> DD/MM/AAAA"*. O leitor acabava de ler o motivo quando chegava à repetição dele.
>
> O motivo continua obrigatório **na linha**; o que deixa de ser obrigatório é repeti-lo colado ao
> número. A marca ao lado do número é `parcial`, que é a grafia que a tabela dos Perfis já usava —
> as duas tabelas estavam divergindo, e ninguém havia decidido qual delas estava certa.

**O teste que separa as duas coisas** é sempre o mesmo: *existe ato, publicação ou registro que
produziu este número?* Se existe, escreve-se o número — inclusive quando ele é zero. Se não existe,
escreve-se a ausência que corresponde ao motivo.

---

## 14. Requisitos funcionais

> **Todo `MUST` abaixo é obrigação DESTA entrega** (`D-011`). Os indicadores de resultado e a série
> por ano estão definidos na §9 e registrados na §23 — eles não aparecem como `MUST` aqui, e é essa
> a correção que a revisão de 21/09 exigiu.

### A página, o recorte e a fonte única

- **FR-581**: O sistema MUST apresentar uma página institucional de visão geral dos Processos
  Seletivos, **acima do nível do Processo**, alcançável a partir da lista de Processos.
- **FR-582**: Todo número apresentado MUST derivar do selector que já governa a tela dona daquele
  fato, ou de uma abstração extraída dele. A visão MUST NOT conter regra de domínio própria, e
  MUST NOT calcular no template.
- **FR-583**: O recorte MUST ser limitado ao `institution_scope` do ator, aplicado na camada de
  aplicação — como `listar_processos` já o aplica, e pelo mesmo motivo: listagem sem escopo é a
  brecha por onde se enxerga o que não se pode alcançar.
- **FR-584**: A página MUST NOT apresentar dado pessoal de candidato — nome, CPF, e-mail, telefone,
  documento ou qualquer identificador de pessoa —, nem em texto, nem em atributo, nem em URL.

### Os indicadores desta entrega

- **FR-585**: O consolidado MUST apresentar **quatro números**: Editais no recorte, vagas imediatas
  publicadas, inscrições submetidas e inscrições por vaga. Os denominadores — Processos
  representados, Editais com conteúdo publicado, Perfis com vaga imediata — MUST acompanhar o número
  que explicam, como contexto, e MUST NOT ser apresentados como números principais.
- **FR-586**: *Inscrições submetidas* MUST ser `status = SUBMETIDA`. Rascunho MUST NOT compor o
  número principal, MUST aparecer como informação secundária e MUST usar o termo que a tela dona já
  usa — **"Em preenchimento"** —, porque dois termos para o mesmo conceito é o que o Princípio I
  proíbe sem decisão documentada.
- **FR-587**: *Vagas imediatas publicadas* MUST ser a soma de `profiles[].immediateVacancies` da
  **versão consolidada vigente**, e MUST NOT ser lida das linhas de elaboração. Edital sem conteúdo
  vigente MUST NOT contribuir, e MUST ser contado à parte.
- **FR-588**: *Inscrições por vaga* MUST ter, como numerador, **apenas as inscrições submetidas em
  Perfis que publicam vaga imediata**, recortadas por `Inscricao.profile_id`; e como denominador, as
  vagas imediatas desses mesmos Perfis. A regra vale por Edital **e** no consolidado. Onde o Edital
  tiver Perfil fora do numerador, a página MUST declarar a população usada.
- **FR-589**: Edital em que **nenhum** Perfil publica vaga imediata MUST produzir *inscrições por
  vaga* **não aplicável** — nunca `0`, nunca `∞`, nunca omissão silenciosa —, e MUST continuar
  visível na tabela com vagas e demanda legíveis.
- **FR-590**: O consolidado MUST NOT ser contaminado pelo Edital sem denominador: ele não entra no
  numerador nem no denominador da razão, e a contagem de Editais que ficaram de fora MUST ser dita.

### Ausência, parcialidade e honestidade

- **FR-591**: Zero MUST ser apresentado quando a fonte canônica produziu zero — inclusive `0`
  inscrições, `0` vagas imediatas e `0` de qualquer indicador cujo ato existe. Ausência MUST ser
  usada quando nenhum fato produziu o número, ou quando a métrica não se aplica.
- **FR-592**: O sistema MUST NOT apresentar *matriculados*, *taxa de matrícula* ou equivalente, em
  entrega alguma desta feature. Quando o indicador de requerimento for entregue, ele MUST se chamar
  **Requerimentos de matrícula enviados** e MUST ser restrito aos Editais que declaram
  `requerimento_momento` (`FR-368`, `FR-369`).
- **FR-593**: Contagem sobre `Inscricao` MUST ser nomeada **inscrições**, e nunca *pessoas* ou
  *candidatos*. Indicador de pessoas, se algum dia entrar, MUST ser rotulado como apuração por **CPF
  declarado**, MUST NOT ser somado nem comparado a inscrições, e MUST existir apenas no consolidado.
- **FR-594**: As quatro ausências — não aplicável, ainda não disponível, não publicado e parcial —
  MUST ter grafia própria e legível, e nenhuma delas MUST ser apresentada como `0`.
- **FR-595**: Indicador cuja fase ainda corre MUST ser marcado **parcial**, e o agregado que o
  contém MUST declarar quantos dos seus somandos são parciais.
- **FR-596**: A página MUST declarar, em texto visível, **o que ela não mede**: matrícula efetivada,
  obsolescência de apuração, as dimensões que o domínio não tem, e os indicadores que esta entrega
  ainda não apresenta.

### Filtros e recorte

- **FR-597**: Os filtros MUST ser: ano do Edital, situação do Edital, situação do período de
  inscrições e busca textual sobre Processo e Edital. Nenhum filtro MUST ser oferecido sobre
  dimensão que o domínio não possui.
- **FR-598**: Os filtros **relacionais** — escopo, ano do Edital, situação do Edital e busca — MUST
  ser aplicados **antes** da materialização das versões consolidadas. O filtro por **situação do
  período** depende do conteúdo vigente e MUST ser aplicado **depois**, sobre o conjunto já
  reduzido. *A redação anterior exigia todos antes de qualquer leitura de conteúdo, e era contrato
  impossível: a situação do período mora no snapshot.*
- **FR-599**: Sem parâmetro de consulta, a página MUST recortar pelo **ano corrente**, MUST declarar
  o recorte aplicado e MUST oferecer os demais anos e a opção **Todos**. As opções MUST ser obtidas
  de `Edital.year` sem abrir snapshot algum.

### A tabela

- **FR-600**: A linha MUST ser o **Edital**, MUST nomear o Processo a que ele pertence e MUST levar
  à página daquele Edital.
- **FR-601**: As colunas numéricas MUST ser ordenáveis, e a ordenação MUST tratar ausência como
  ausência — agrupada ao fim em qualquer sentido —, nunca como zero.
- **FR-602**: ~~A tabela MUST marcar duas situações, derivadas por aritmética sobre os números que
  ela já apresenta: **período encerrado com zero inscrições submetidas**; e **inscrições por vaga
  menor que 1 com período encerrado**.~~ **Substituída pela `041`** (`FR-616` dela): as mesmas duas
  espécies passam a ser calculadas **no Perfil**, e a linha do Edital as resume — ver `FR-613` e
  `FR-614`. *O conjunto de Editais marcados mudou: um com razão global acima de 1 e um Perfil vazio
  passou a receber marca.* As marcas MUST continuar legíveis sem cor.
- **FR-603**: O sistema MUST NOT criar score de saúde, classificação artificial de Processos, motor
  de alertas, notificação ou regra de risco parametrizável — em entrega alguma desta feature.

### Autorização

- **FR-604**: A página MUST exigir capacidade **explícita e própria**, negada por padrão, e MUST NOT
  reusar permissão concedida para outro ato.
- **FR-605**: Quem não detém a capacidade MUST NOT ver o caminho para a página. O caminho da linha
  para o Edital MUST respeitar a autorização da tela de destino, e MUST NOT oferecer destino que o
  ator não alcança — a garantia da `033`, que esta feature não desfaz.

---

## 15. Requisitos não funcionais

- **Custo de consulta constante no número de Editais.** O número de consultas ao banco MUST NOT
  crescer com a quantidade de Editais do recorte — nem com a de Processos. É o `SC-209`, e é a
  consequência direta das ~17 consultas por Edital que a auditoria mediu.
- **Nenhuma escrita.** O módulo de leitura MUST NOT conter `save`, `create`, `update` ou `delete` —
  a mesma invariante que `interface/supervisao.py` declara e que a `022` fixou em `FR-007`.
- **Sem infraestrutura analítica.** Nenhum data warehouse, ETL, índice de busca, *materialized
  view*, tabela de indicadores, fila ou cache. Se a consulta relacional indexada atender, ela fica.
- **Acessibilidade.** Tabela com cabeçalhos associados; estado nunca comunicado só por cor; a
  ausência dita em texto e não só por símbolo; a página utilizável em largura de telefone.
- **Determinismo.** A leitura MUST aceitar o instante como argumento, como `pulso(processo, agora=)`
  já faz, para que os números sejam reproduzíveis em teste.

---

## 16. Regras de autorização

1. **Uma capacidade nova**, negada por padrão, cobrindo exatamente *ler o panorama institucional*.
2. **Nenhum RBAC novo**: a capacidade entra no mesmo mapa `PAPEIS`, do mesmo modo que
   `recurso:julgar` e `matricula:exportar` entraram.
3. **A concessão inicial é ao `gestor`**, que é quem hoje conduz os Processos do escopo.
4. **"Diretoria" não existe como papel, e criá-la é decisão institucional, não técnica** — ver
   `D-008` e `G-010`. Quando for tomada, custa **uma entrada** no mapa, com essa permissão e nenhuma
   outra: é literalmente o desenho que o `julgador` e o `exportador` já provam.
5. **Nada de escopo ampliado**: a capacidade lê o panorama **do escopo do ator**, e não de outros.
6. **O drill-down não concede nada.** Chegar ao Edital pela visão aplica a mesma autorização de
   chegar por qualquer outro caminho.

---

## 17. Critérios de aceite

> Todos medem **esta entrega**. Os indicadores registrados na §9 terão critérios próprios na spec
> que os obrigar.

- **SC-206**: Quem abre a página responde, **sem abrir Processo nenhum**, quantos Editais houve no
  recorte, quantas vagas foram ofertadas, quanta procura chegou, qual foi a relação por vaga e quais
  ficaram sem ninguém — ou lê, na própria página, por que alguma delas não é respondível. Percorrido
  pela interface, sem shell e sem banco.
- **SC-207**: **Zero** divergências entre o número da visão e o da tela dona, para o mesmo Edital —
  conferido em três Editais em fases distintas: um em elaboração, um com inscrições abertas e um com
  período encerrado.
- **SC-208**: **Zero** ocorrências de ausência grafada como `0`, e **zero** ocorrências de zero
  legítimo grafado como ausência — conferido em um Edital em elaboração (vagas ausentes), num Edital
  publicado sem inscrição (submetidas `0`) e num Perfil de cadastro de reserva (vagas `0`, razão
  ausente).
- **SC-209**: O número de consultas ao banco **não cresce** com o número de Editais do recorte —
  medido com 3 e com 60 Editais, pela mesma contagem determinística que `tests/performance/` já usa.
- **SC-210**: **Zero** dados pessoais na página — nenhum nome, CPF, e-mail, telefone ou identificador
  de pessoa no HTML renderizado, com inscrições submetidas presentes no recorte.
- **SC-211**: Quem não detém a capacidade **não vê o caminho** e **não alcança a rota** — conferido
  com um ator de cada um dos outros papéis.
- **SC-212**: A página declara, em texto visível, que **matrícula efetivada não é medida**, que a
  obsolescência de apuração é reportada pela Supervisão do Processo, e **quais indicadores ainda não
  apresenta**.
- **SC-213**: Num Edital com um Perfil de vagas imediatas e outro exclusivamente de cadastro de
  reserva, *inscrições por vaga* usa **apenas** a demanda do primeiro, a página declara a população
  usada, e o consolidado concorda com a linha.
- **SC-214**: A página aberta sem parâmetro recorta pelo **ano corrente**, declara o recorte, e abre
  **apenas** os snapshots dos Editais daquele ano — conferido com um acervo de anos anteriores
  presente.

---

## 18. Cenários de teste

### Domínio de leitura (sem requisição)

| # | Cenário | Espera |
|---|---|---|
| T-01 | Edital em elaboração no recorte | vagas e razão **ausentes** (*não publicado*); submetidas conta normalmente; nenhuma exceção |
| T-02 | Perfil com `immediateVacancies = 0` e `reserveType = UNLIMITED` | vagas `0` — **zero legítimo** — e razão **não aplicável** |
| T-03 | Edital com dois Perfis, ambos com vaga imediata | vagas é a soma dos dois; numerador é a demanda dos dois |
| T-03b | **Edital misto**: Perfil A com 40 vagas e 80 submetidas, Perfil B só cadastro de reserva com 200 submetidas | **Submetidas `280`**; **razão `2,0`** — `80 ÷ 40`, e nunca `7,0`; a linha declara a população usada |
| T-03c | O mesmo Edital misto dentro do consolidado | o consolidado soma `80` ao numerador e `40` ao denominador, e **concorda** com a linha |
| T-04 | Edital publicado, período aberto, 40 submetidas e 12 rascunhos | submetidas `40` **parcial**; rascunhos `12` em campo próprio; a soma `52` não existe em lugar nenhum |
| T-05 | Edital publicado sem nenhuma inscrição, período encerrado | submetidas `0` (zero legítimo) e marca de atenção |
| T-06 | Duas inscrições da **mesma pessoa** em Perfis distintos do mesmo Edital | submetidas conta **2** — são duas inscrições, e a página não afirma pessoas |
| T-07 | Edital retificado que muda as vagas | vagas é a da versão **vigente**, e não a da publicação original |
| T-08 | Recorte com Editais em fases diferentes | o consolidado declara os três: quantos **publicaram conteúdo** (`FR-585`), quantos somandos são **parciais** (`FR-595`) e quantos ficaram **fora da razão** (`FR-590`) |
| T-09 | Ordenação por *Inscr./vaga* com ausências | as ausências vão ao fim em ambos os sentidos |
| T-10 | Nenhum Edital no recorte | a página se explica, e não apresenta `0` como se fosse resposta sobre o acervo |

### Interface

| # | Cenário | Espera |
|---|---|---|
| T-11 | `gestor` abre a página sem parâmetro | recorte do ano corrente, declarado; quatro números; tabela |
| T-12 | `elaborador` tenta a rota | recusa, e nenhum caminho oferecido |
| T-13 | Filtro por outro ano | consolidado e tabela mudam **juntos** e concordam |
| T-14 | Filtro por *situação do período* = aberto | aplicado **depois** da materialização, sobre o conjunto já reduzido pelos filtros relacionais |
| T-15 | Clicar na linha | chega ao Edital daquela linha |
| T-16 | Varredura do HTML com inscrições submetidas presentes | nenhum nome, CPF, e-mail ou telefone |
| T-17 | Leitura sem cor | as duas marcas de atenção continuam legíveis |
| T-18 | Leitura da declaração da página | nomeia matrícula efetivada, obsolescência de apuração e os indicadores ainda não apresentados |

### Autorização e desempenho

| # | Cenário | Espera |
|---|---|---|
| T-19 | Ator de outro `institution_scope` | não vê Processo algum do escopo alheio |
| T-20 | 3 Editais × 60 Editais no recorte | mesma contagem de consultas |
| T-21 | Recorte de um ano com 3 Editais, num acervo de 60 | abre **3** conteúdos publicados, e não 60 (`FR-598`, `FR-599`) |
| T-22 | Seletor de anos com acervo de 6 anos | as opções saem de `Edital.year` sem abrir snapshot algum |

---

## 19. Decisões de UX

1. **Progressão, e não dois painéis.** Filtros → consolidado → tabela. Quem quer dimensão para no
   segundo bloco; quem quer portfólio desce. A série, quando vier, entra entre os dois e não muda a
   ordem.
2. **Quatro números grandes, e os denominadores embaixo deles.** *"Vagas publicadas · **4.310** ·
   em 9 dos 12 Editais do período"* lê melhor que dois cartões — *"12 Editais"* e *"9 publicados"* —
   porque o segundo número existe para explicar o primeiro, e não para competir com ele. É o que faz
   *"uma página, quatro números"* ser literalmente verdade.
3. **Nenhum gauge, donut, velocímetro ou medidor.** E, nesta entrega, **nenhum gráfico**: a série
   por ano é registrada (`D-013`), e quando vier usará a técnica que o repositório já tem — barra
   proporcional em CSS, sem JavaScript, como `_serie_de_inscricoes.html` — **com o número sempre
   escrito ao lado**.
4. **A ausência é escrita.** `—` sozinho é enigma; `—` com *"sem conteúdo publicado"* é informação.
5. **A marca de atenção é texto**, e a cor é reforço. Nenhum estado é comunicado só por cor.
6. **O prazo se escreve de um jeito só.** A auditoria mediu **três renderizações** do mesmo prazo em
   três telas; esta página adota a do portal e não cria a quarta.
7. **A tabela cabe no telefone.** Em largura estreita, período, em preenchimento e razão recolhem;
   Processo/Edital, situação, vagas e submetidas ficam. As colunas de fase, quando vierem, recolhem
   primeiro.
8. **O recorte aplicado é dito na própria página**, e não só no seletor: *"Editais de 2026"* acima
   dos números evita que alguém leia o recorte como o acervo.

---

## 20. Impactos de banco, consultas e índices

**Nenhuma migration de esquema é prevista.** A feature é leitura.

Consultas previstas, todas em número **fixo**:

| # | Leitura | Forma | Índice que a sustenta |
|---|---|---|---|
| 1 | Processos e Editais do escopo | `filter(institution_scope=…)` + `prefetch` | `uq_processo_scope_institutional_code`; `ix` de `(processo, status)` no Edital |
| 2–3 | Versão vigente por Edital | duas consultas, pelo padrão de `selecoes_publicas`: a primeira decide a vencedora sem carregar `content`, a segunda materializa só as vencedoras | `(edital, valid_from, materialized_at)` em `VersaoConsolidada` |
| 0 | Anos disponíveis para o seletor | `values_list("year", flat=True).distinct()` no escopo — **uma coluna, nenhum snapshot** (`FR-599`) | varredura barata; nenhum índice novo |
| 4 | Inscrições por Edital, **Perfil** e estado | `values("edital_id","profile_id","status").annotate(Count)` | `(edital, status)` em `Inscricao` |
| 5 | Classificados | `filter(publicacao__edital__in=…, publicacao__sucessoras__isnull=True, situacao=CLASSIFICADA)` agrupado por Edital, `Count(distinct)` | `(edital, perfil_id, marco_id)` em `PublicacaoResultado`; `(inscricao)` em `SituacaoDivulgada` |
| 6 | Convocados | `filter(edital__in=…, convocacao_anterior__isnull=True)` agrupado, `Count(distinct)` | `ix_convocacao_recorte` |
| 7 | Ocupação | `filter(edital__in=…, sucessoras__isnull=True)` agrupado, `Sum` | `ix_apuracao_recorte` |
| 8 | Requerimentos | `filter(inscricao__edital__in=…, enviado_em__isnull=False)` agrupado | `(inscricao)` em `RequerimentoDeMatricula` |

**A consulta 4 agrupa por Perfil, e a razão é `D-012`.** O numerador da razão é recortado aos Perfis
com vaga imediata, e isso exige saber a que Perfil cada inscrição pertence. Continua sendo **uma**
consulta; o que cresce é o número de linhas devolvidas, limitado por `Editais × Perfis × 2` — e o
índice `(edital, status)` continua servindo. A coluna *Submetidas* da tabela é a soma das linhas do
Edital, de modo que o total e o numerador saem da **mesma** leitura, e não podem divergir.

**O custo real não está nas consultas; está nos snapshots.** A leitura de vagas abre
`VersaoConsolidada.content` de cada Edital do recorte — é o que o portal já faz na vitrine, e a
`024` registrou em `D-003` o limiar que obriga a revisar: *"quando o catálogo passar de algumas
centenas"*. Daí o par que contém o custo: `FR-598` **filtra antes de materializar**, e `FR-599`
**limita o recorte inicial ao ano corrente** — sem o segundo, o primeiro não impede nada quando
ninguém escolhe filtro.

**Índices a avaliar no plano, não aqui.** `Inscricao` não tem índice em `submitted_at`; ele não é
necessário para esta feature — a série é por `Edital.year` —, e criá-lo agora seria índice sem
consulta que o use. Fica registrado como `G-008`.

**Uma extração compartilhada, e não uma cópia.** `selecoes_publicas` já resolve *"a versão vigente
de cada Edital"* e mistura isso com *"o que é público"* — que exclui cancelado. O plano MUST extrair
o resolvedor (`versoes_vigentes(editais, at=)`) e fazer as **duas** leituras consumirem-no. Copiar a
lógica criaria a segunda verdade que `FR-582` proíbe.

---

## 21. Dependências com features existentes

| Feature | O que esta consome | Direção |
|---|---|---|
| `001` / `002` | `ProcessoSeletivo`, `Edital`, `listar_processos`, o escopo institucional | só leitura |
| `007` / `026` / `027` | conteúdo publicado, versão consolidada, quadro de vagas | só leitura |
| `009` | estados da Inscrição e `periodo_de_inscricoes` | só leitura |
| `015` / `017` | ato de ordenação vigente e situação divulgada | só leitura |
| `016` | apuração de ocupação vigente, e a **regra de grafia da ausência** | só leitura |
| `019` | convocação raiz vigente | só leitura |
| `022` / `038` | **fronteira**: elas conduzem o Processo; esta descreve o conjunto | nenhuma alteração |
| `024` | o padrão de leitura em massa de conteúdo publicado | **extração compartilhada** |
| `029` / `031` | requerimento enviado; e a recusa de afirmar matrícula | só leitura |
| `033` | nenhum caminho oferecido a quem não o abre | invariante preservada |
| `039` (em curso) | se o catálogo de Modalidades mudar a forma do quadro, esta leitura acompanha | **registrada, não medida** |

---

## 22. Riscos e lacunas descobertas

| # | Lacuna | Consequência | O que esta spec faz |
|---|---|---|---|
| **G-001** | **Matrícula efetivada não tem fonte canônica.** O sistema gera arquivo e não guarda nem o arquivo nem a resposta do destino; a integração é `[NÃO VALIDADO]` | *"taxa de matrícula"* seria número inventado | **não apresenta**, e declara (`FR-592`, `SC-212`) |
| **G-002** | **"Aprovado" não existe no domínio** | um indicador com esse rótulo não teria fórmula | não usa o termo |
| **G-003** | **Pessoas distintas só por CPF declarado**; ele nunca é provado e não é único | contagem de pessoas tem erro não mensurável | rotula e não promove a principal (`FR-593`, `D-006`) |
| **G-004** | **Não há dimensão de campus ou polo abaixo do escopo** | *"diferenças entre polos"* não é respondível; `locality` é texto livre por Perfil | não oferece o filtro; a pergunta segue aberta em `AX-6`/`ACH-60` |
| **G-014** | **A unidade existe como `institution_scope`, e esta página não a vê.** O portal a usa como eixo porque a vitrine é cross-scope; a gestão é confinada a um escopo por princípio constitucional | *"diferenças entre unidades"* fica sem superfície se a instituição vier a ter mais de um escopo | registra a decisão: **visão cross-scope é outra feature**, com outra autorização — não é filtro a acrescentar aqui |
| **G-005** | **Não há ano/semestre de ingresso.** *"Processos de 2026/2"* **não é consultável** | o recorte por edição letiva não existe | usa `Edital.year` e **declara a diferença** (`D-004`) |
| **G-006** | **Não há taxonomia de tipo/família do Processo** | *"desempenho por tipo"* não é respondível | não oferece o filtro; o modelo já registra por que criá-la seria inventar eixo |
| **G-007** | **Vaga publicada só sai do snapshot** | o custo é linear nos Editais do recorte | `FR-598` + limiar herdado da `024` |
| **G-008** | `Inscricao` sem índice em `submitted_at` | série **diária** institucional não é barata | não há série diária nesta feature; registrado |
| **G-009** | **A apuração vigente pode estar obsoleta** por cinco causas já nomeadas, e recomputá-las no recorte institucional seria caro | a soma de ocupação pode estar defasada | **declara o limite** (`FR-596`) e aponta a Supervisão |
| **G-010** | **Não existe papel de Diretoria** | a persona não tem representação no sistema | registra a decisão (`D-008`), sem criar a entidade |
| **G-011** | **O vocabulário "rascunho" × "Em preenchimento"** já divergia entre inventário e tela | dois termos para um conceito | adota o da tela (`FR-586`) |
| **G-012** | **Não há definição inequívoca de "classificação final".** A noção *existe* — `Corte.etapa_governada_id` é nulo quando a regra declara `NONE`, e o comentário o chama de *"marco terminal"* — mas **não é universal**: marco sem regra de corte não emite Corte, e o acervo publicado tem `cutRule` nulo | *"387 classificados"* seria lido como resultado final, contando quem foi classificado num marco intermediário e eliminado depois | mantém o indicador **fora** desta entrega, com o nome que ele de fato tem — *inscrições classificadas em resultados divulgados* — e nomeia o caminho: a spec que o obrigar decide se usa o marco terminal e o que faz com o acervo |
| **G-013** | **A série por ano e o filtro por ano se anulam.** Filtrar 2026 faz a "série histórica" ter um ponto | a visualização perde sentido no recorte mais usado | a série sai desta entrega (`D-013`), e a decisão de como ela se relaciona com o filtro fica registrada na §23 |

---

## 23. Decisões ainda necessárias — governança do usuário

> Registradas, e **não tomadas** nesta spec.

- **`G-010`** — **Criar o papel `diretoria`?** Uma entrada no mapa `PAPEIS`, com a capacidade desta
  feature e nenhuma outra. Alternativa: manter a concessão ao `gestor` e tratar a Diretoria como
  gestora do escopo.
- **`G-005`** — **O eixo temporal institucional é o ano do Edital ou a data de publicação?** Esta
  spec decide `Edital.year` por `D-004`; se a instituição entende *"processos de 2026"* como *"os
  publicados em 2026"*, a decisão muda o recorte e precisa ser tomada antes do plano.
- **`G-003`** — **"Pessoas distintas" entra na v1?** É computável e tem erro não mensurável.
- **`G-011`** — **Confirmar "Em preenchimento"** como o termo único, ou decidir a troca **nas duas
  telas** — nunca em uma só.
- **`G-004`** — **Polo como eixo** segue aberta desde 19/09, e continua precisando de um Edital
  real de múltiplos polos antes de qualquer abstração.
- **`G-014`** — **Existe visão institucional cross-scope?** Descoberto ao planejar (`research.md`,
  `R-005`): a unidade **é** `institution_scope`, e o portal já filtra por ela. Se a instituição vier
  a ter mais de um escopo, *"diferenças entre unidades"* passa a ser pergunta legítima — e **não é
  desta página**, que é escopada por `FR-583`. Seria feature própria, com autorização própria.
  *Registrar agora evita que alguém a resolva acrescentando um filtro que fura o escopo.*
- **`G-013`** — **Como a série por ano se relaciona com o filtro por ano?** Três saídas, e a escolha
  é do usuário: a série **ignora** o filtro e mostra sempre a história; a série **some** quando um
  ano único é selecionado; ou o filtro passa a aceitar **intervalo ou múltiplos anos**. A terceira é
  a mais útil e a mais cara. *Decidir antes de obrigar a série, e não depois.*
- **`G-012`** — **"Classificação final" vale a pena definir?** Se sim, o marco terminal
  (`governedStage: NONE`) é o ponto de partida, e o acervo com `cutRule` nulo é o problema a
  resolver. Se não, o indicador permanece *inscrições classificadas em resultados divulgados*, com
  o rótulo dizendo o que ele é.

---

## 24. Itens explicitamente fora de escopo

Construtor de relatórios · relatórios customizáveis · dashboards por usuário · widgets configuráveis
· envio periódico · **PDF, Excel e CSV** · API pública de indicadores · notificações · metas ·
projeção · *benchmarking* · IA · recomendação automática · score de saúde · motor de alertas ·
*drill-down* que liste pessoas · qualquer dimensão que o domínio não possua · qualquer alteração no
catálogo de sinais da `022`/`038`.

**Exportar a tabela**: o repositório **não** tem infraestrutura genérica de exportação — a única que
existe é o arquivo de matrícula da `031`, que é específico, tem papel próprio (`matricula:exportar`)
e **não guarda o artefato** (`FR-456`). Exportar aqui custaria arquitetura nova, e por isso fica
registrado como **melhoria futura**, nunca como razão para ampliar esta feature.

---

## Assumptions

### D-001 — a granularidade da tabela é o Edital

Tudo o que se quer contar pende do Edital: inscrição, ato de ordenação, apuração, convocação,
publicação de resultado e geração de arquivo têm FK para ele. O `ProcessoSeletivo` não tem data, não
tem vaga e não tem prazo — a `022` registrou, em `D-005`, que *"não existe marco do Processo"*, e
Editais do mesmo Processo têm cronogramas independentes por invariante da Constituição.

**O Processo não some**: ele nomeia a linha e agrupa a leitura. Mas a linha que soma é a do Edital,
porque é a do Edital que tem denominador.

### D-002 — a visão é institucional, e não duplica a `022`/`038`

A `022` e a `038` observam a fronteira entre features **dentro de um Processo**; esta observa a
fronteira **entre Processos**. As duas leituras são de níveis distintos e não competem.

**Nenhuma das duas ganha cópia**, e esta não recalcula o que elas calculam: onde o número já existe
numa delas, é o selector delas que o produz (`FR-582`). *A auditoria de 20/09 recusou "outro painel"
— e recusou acrescentar linhas à região de Atenção, que esta feature não toca.*

### D-003 — vaga publicada sai do conteúdo publicado, e o custo é do recorte

A Retificação não reescreve o relacional: `PerfilVaga.immediate_vacancies` é elaboração, e o que o
Edital publicou está na `VersaoConsolidada`. Ler a linha de elaboração seria mais barato e **estaria
errado** depois da primeira Retificação — e a Constituição é explícita: a fonte é o publicado.

A consequência é o custo: abrir um snapshot por Edital do recorte. Por isso o filtro antecede a
leitura (`FR-598`), e por isso o limiar que obriga a revisar é o mesmo que a `024` já fixou.

### D-004 — o eixo temporal é o **ano do Edital**

`Edital.year` é coluna, existe em todo Edital — inclusive no não publicado —, não se move por
Retificação e é como a instituição nomeia o certame (`66/2026`).

**A data de publicação não serve de recorte** porque só existe para o publicado, e o eixo precisa
enxergar o Edital em elaboração para responder *"o que temos em andamento"*. Ela entra como coluna,
não como agrupador.

**E a diferença é dita, não escondida**: *ano do Edital* não é *ano de ingresso*. A pergunta
*"processos de 2026/2"* **não é respondível**, e a página não finge que é.

### D-005 — zero produzido pelo domínio não é ausência

A regra **não** é *"zero só existe para inscrições"* — a primeira redação dizia isso, e se
contradizia três parágrafos depois, ao aceitar `0` vagas num Perfil de cadastro de reserva.

A regra é a da `016`, lida inteira: *"Zero é uma afirmação — «não há vaga a ocupar» —, e **sem
apuração emitida ninguém afirmou isso**"*. O defeito nunca foi escrever zero; foi escrever zero **no
lugar de** um fato que não existe.

> **Zero quando a fonte canônica produziu zero. Ausência quando nenhum fato produziu o número, ou
> quando a métrica não se aplica.**

Zeros legítimos e todos produzidos por alguma fonte: `0` submetidas num Edital publicado, `0` vagas
imediatas num Perfil de cadastro de reserva, `0` ocupadas numa apuração **emitida**, `0` classificados
num resultado **divulgado**. Apagar qualquer um esconderia o caso que a Coordenação precisa ver.

A ausência grafada como `0` é o que a `UX-032` chama de colapso de estados, e num painel
institucional é pior: a soma passa a afirmar o que ninguém apurou. O erro simétrico — ausência onde
há fato — esconde o Edital sem procura. `FR-591` cobra os dois lados.

### D-006 — pessoa e inscrição são grandezas diferentes, e a página só conta inscrições

**Contagem sobre `Inscricao` conta inscrições, e nunca pessoas.** `DISTINCT inscricao` existe porque
a mesma inscrição aparece em mais de um recorte e recebe mais de uma chamada — não porque ele
resolva identidade. A mesma pessoa pode ter **duas inscrições no mesmo Edital**: a restrição
`uq_inscricao_identidade_edital_perfil` é por **Perfil**, e o teto por Edital é opcional e
frequentemente nulo. Chamar o número de *"candidatos"* faria alguém implementar
`COUNT(DISTINCT cpf)` por engano — que é outro número, com outro erro.

**Pessoas distintas, se algum dia entrar, é apuração por CPF declarado.**

A contagem é computável — `cpf_normalizado` é garantido por `CHECK` em toda inscrição submetida, e é
a mesma chave que a reconciliação da `010` usa para agrupar. Mas o CPF é **declarado e nunca
provado**, `CandidateIdentity.cpf_normalizado` **não é único**, e a reconciliação *"relata sem
interromper"* os grupos com mais de um `subject`.

O número, portanto, existe e tem erro **não mensurável**. Ele pode ser apresentado, rotulado pelo
que é, e **jamais** misturado com inscrições. Se entra na v1 é `G-003`.

### D-007 — as marcas da tabela não são sinais do catálogo da `022`

O catálogo de Atenção é fechado por requisito (`FR-565`), tem destino por espécie e tem identificador
próprio. As três marcas desta página são **aritmética sobre colunas que ela já mostra** — sem
espécie, sem identificador, sem encaminhamento próprio: o destino da linha é o Edital, como o de
qualquer outra linha da tabela.

Misturá-las com o catálogo criaria a décima primeira espécie sem tela que a resolva — exatamente o
que a auditoria mede como o defeito da `038`.

### D-008 — a autorização é capacidade nova em papel existente; "Diretoria" é decisão institucional

*Negar por padrão* é princípio constitucional, e reusar `inscricao:consultar` ou `auditoria:consultar`
concederia o panorama por efeito colateral de outro ato — que é exatamente o que a `031` recusou por
escrito ao criar `matricula:exportar` em vez de pendurá-la no Gestor.

Capacidade nova, concedida ao `gestor`, que hoje é quem conduz os Processos do escopo. **Criar o
papel `diretoria` é decisão do usuário** (`G-010`), e quando vier custa uma entrada no mapa — o
`julgador` e o `exportador` já provam o desenho. Inventá-la aqui seria criar ator institucional numa
spec de leitura.

### D-009 — quando a série vier, é barra com o número escrito, e não um gráfico

*Esta entrega não tem série* (`D-013`). A decisão de forma fica tomada de antemão, porque ela é
barata e porque decidi-la depois, sob pressão de entrega, é como aparece uma biblioteca de gráficos
num repositório que não tem nenhuma.

Um gráfico só entra se responder pergunta gerencial real. A pergunta — *"estamos ofertando mais ou
menos, e a procura acompanhou?"* — é real, e a tendência se lê melhor em barra que em coluna de
números.

Mas a barra **não substitui o número**: o repositório já tem a técnica, em CSS puro e sem
JavaScript, em `_serie_de_inscricoes.html`, e ela escreve o valor ao lado. É isso, e nada além —
sem biblioteca, sem eixo configurável, sem segunda visualização.

### D-010 — nenhuma dimensão que o domínio não tenha, e a unidade não é exceção

Campus, polo, tipo de Processo e semestre de ingresso **não existem**. Derivá-los de texto
livre — `locality`, `title`, `institutional_code` — seria decidir uma classificação institucional
lendo o que alguém digitou, que é precisamente o que `EventoCronograma.is_registration_period`
existe para não fazer.

**A unidade é o caso que merece precisão, e o planejamento a corrigiu** (`research.md`, `R-005`).
Ela **existe** — é `institution_scope`, e o portal a oferece como filtro na vitrine, que é
cross-scope. Mas esta página é confinada ao escopo do ator por `FR-583`, e dentro dele a unidade é
constante: o filtro teria sempre uma opção. Não é ausência de dado; é consequência do recorte. A
visão cross-scope, se for querida, é feature própria (`G-014`).

As perguntas que dependem dessas dimensões ficam **registradas como lacuna** (`G-004`, `G-005`,
`G-006`, `G-014`), e a página declara que não as responde.

### D-011 — a `040` é o primeiro incremento, e os `MUST` obrigam só ele

A primeira redação desta spec obrigava, em `MUST`, classificados, convocados, ocupação,
requerimentos e série histórica — e a seção final os adiava. **Normativamente, a implementação
mínima não satisfaria a própria spec**, e o `/speckit-plan` leria as vinte e cinco obrigações como
uma entrega só.

**Definir não é obrigar.** Os indicadores adiados continuam integralmente definidos na §9, com
fórmula, denominador, fonte e momento de confiabilidade — esse é o trabalho de investigação desta
spec, e perdê-lo para caber num recorte seria trocar rigor por brevidade. O que muda é a coluna
*Entrega*.

**Três proibições e duas garantias não são adiáveis**, e por isso continuam `MUST` aqui: nenhum dado
pessoal (`FR-584`), nenhum *matriculados* (`FR-592`), nenhum motor de alerta (`FR-603`), as quatro
grafias de ausência (`FR-594`) e a declaração do que não se mede (`FR-596`). Guarda-corpo que sai
junto com a capacidade é guarda-corpo que falta quando a capacidade volta.

### D-012 — o numerador da razão é recortado, nos dois níveis

Um Edital com Perfil A — 40 vagas, 80 inscrições — e Perfil B — só cadastro de reserva, 200
inscrições — produziria `280 ÷ 40 = 7,0` pela fórmula ingênua. O número é aritmeticamente correto e
**institucionalmente falso**: as 200 inscrições do Perfil B não disputam as 40 vagas do Perfil A. Os
Perfis são competições separadas, e a `009` já amarra cada inscrição a um deles — `profile_id`, a
identidade **publicada** do Perfil, estável sob Retificação.

**Por isso o numerador é recortado**: só entram as inscrições cujo `profile_id` está entre os Perfis
que publicam vaga imediata. E **por isso vale nos dois níveis**: calcular o Edital de um jeito e o
consolidado de outro faria os dois discordarem, e no consolidado a discordância não é perceptível a
olho.

**A demanda total não some** — ela continua na coluna *Submetidas*, que é o número do Edital inteiro.
O que se recorta é a **razão**, porque razão exige que numerador e denominador falem do mesmo
conjunto.

### D-013 — o recorte inicial é o ano corrente, e a série fica para depois

**O custo dominante desta feature é abrir um snapshot por Edital do recorte.** Um padrão *"todos os
anos"* faria esse custo crescer com a história institucional para sempre, e a página chegaria lenta
na primeira dezena de Editais — que é precisamente o risco que a auditoria de 20/09 mandou medir
antes de um Processo grande.

Ano corrente por omissão, os demais anos e **Todos** como escolha explícita, e o recorte aplicado
dito na página. As opções saem de `DISTINCT Edital.year` — uma coluna, sem snapshot.

**E é por isso que a série por ano sai desta entrega.** Ela tem necessidade de recorte **oposta** à
da tabela: a tabela quer um ano, a série quer todos. Com o filtro aplicado a ambas, selecionar 2026
deixa a "série histórica" com um ponto — e a visualização perde sentido exatamente no recorte mais
usado. Isso é decisão de produto (`G-013`), e obrigá-la antes de tomá-la produziria um gráfico que
ninguém sabe ler.

---

## A menor versão que já entrega valor

**Esta spec É essa versão** — depois da revisão de 21/09, a seção deixou de descrever um recorte
futuro e passou a descrever o que os `MUST` da §14 obrigam. *"Uma página, quatro números, uma
tabela"*, literalmente.

**O que esta entrega é:**

1. **Filtros**: ano do Edital — **o corrente por padrão** (`D-013`) —, situação do Edital, situação
   do período e busca. Os três primeiros são colunas; o de período é aplicado depois, sobre o
   conjunto já reduzido (`FR-598`).
2. **Quatro números**, com os denominadores **abaixo** de cada um e não ao lado dele como números
   concorrentes: **Editais** · **Vagas publicadas** · **Inscrições submetidas** · **Inscr./vaga**.
3. **A tabela**, com sete colunas: Processo/Edital · Situação · Período · Vagas · Submetidas ·
   Em preenchimento · Inscr./vaga. Linha clicável até o Edital.
4. **Duas marcas de atenção**: período encerrado com zero submetidas; e razão menor que 1 com
   período encerrado. As duas são aritmética sobre colunas já apresentadas — sem espécie, sem
   catálogo, sem encaminhamento próprio (`D-007`).
5. **A gramática dos números que não existem**: as quatro grafias de ausência, o zero legítimo
   distinguido delas, e a **declaração do que a página não mede**. Não é acessório — é o que separa
   esta página de um painel que parece saber.

**O que fica registrado, definido e não obrigado** (§9, `D-011`): inscrições classificadas em
resultados divulgados · inscrições convocadas · ocupação · requerimentos de matrícula · pessoas
distintas · a série por ano.

**Por que adiá-los não gera retrabalho.** Esta entrega já obriga as quatro coisas estruturais da
feature: **o recorte por escopo**, **a extração compartilhada do resolvedor de versão vigente**, **o
recorte do numerador por `profile_id`** e **a gramática da ausência**. Cada indicador adiado é mais
uma consulta agregada e mais uma coluna sobre uma estrutura já decidida — e três deles ganharam, na
investigação, a definição que impede de entregá-los errado depois.

**Três deles, aliás, não estavam prontos para entrar**, e a revisão foi quem mostrou: *classificados*
não tem definição inequívoca de classificação final (`G-012`); a série por ano não tem decisão sobre
como conviver com o filtro por ano (`G-013`); e *pessoas distintas* depende de decisão do usuário
sobre um número com erro não mensurável (`G-003`). Adiá-los não foi só dimensionamento — foi não
obrigar o que ainda não se sabe definir.

**E o que entra já responde**, com dado que o sistema tem e sem inventar nenhum:

> *Quantos Editais tivemos em 2026? Quantas vagas ofertamos? Quanta procura recebemos? Quais
> ficaram sem ninguém?*
