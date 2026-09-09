# Feature Specification: Supervisão do Processo

**Feature Branch**: `claude/spec-022-supervisao-do-processo`

> **A numeração corrige uma proposta que se dizia `014`.** A `014` está reservada no arco aberto
> pela `013` — *012 conclui avaliações; 013 oficializa resultados de Etapa; 014 determina
> progressão; 015 ordena; 016 ocupa vagas* —, e assim também estão a `016` e a `019`. O diretório
> da worktree ainda carrega o nome antigo; a branch e a pasta da spec, não.

**Created**: 2026-09-09

**Status**: Draft

**Input**: A presidência conduz o certame sem um lugar que responda onde ele está. Cada feature
mostra bem o que é dela, e ninguém mostra o que atravessa: quantas pessoas se inscreveram no
Processo — e não neste Edital —, como a procura evoluiu, quanto falta para o prazo, e se existe
alguma condição que impede o próximo ato. Levantamento de origem:
`doc/inventario-supervisao-do-processo.md`, que percorre `001`–`021` feature a feature.

> **Frase que governa:** quem preside abre o Processo e identifica **o que aconteceu**, **o que
> deveria acontecer agora** e **se existe condição que impede o próximo ato**.

> **E a frase que mantém o corte:** a `022` informa que existe um problema; a feature dona do
> domínio é quem permite resolvê-lo. Ela não é uma segunda implementação de nada.

---

## 1. O que já está fechado, e que a 022 consome

### 1.1 A inversão que organiza a feature

A leitura ingênua diz que um painel gerencial reúne os números do certame. Ela produziu uma
proposta com trinta requisitos, dos quais metade já estava implementada e a outra metade descrevia
estados que o domínio não tem.

```text
ERRADO   a supervisão observa "o Processo"
         → e reconstrói, tela a tela, o que cada feature já mostra melhor

CERTO    a supervisão observa a FRONTEIRA entre as features
         → o que nenhuma dona pode mostrar porque não é dela:
           o Processo acima do Edital, e o tempo acima de todos
```

Os dois eixos que sobram depois desse corte são **nível** e **tempo**:

- **nível** — inscrição, Etapa, cronograma e resultado são do **Edital**; comissão e presidência são
  do **Processo**. Nenhuma tela hoje soma o que está abaixo nem nomeia a que Edital pertence;
- **tempo** — o cronograma declara o que deveria acontecer, e os fatos registram o que aconteceu.
  Metade do dado mora no Edital e metade na feature que produziu o fato; ninguém confronta os dois.

### 1.2 O que o repositório já entrega, e que esta feature NÃO constrói

Levantado feature a feature no inventário. Repetir qualquer uma destas telas é defeito, não escopo.

| Já entregue | Onde | Consequência para a 022 |
|---|---|---|
| Trilha de situação do Processo e *O que fazer agora* | `processo_detalhe.html` | a supervisão estende esta página; não cria uma concorrente |
| O conjunto de atos disponíveis, calculado num lugar só | `interface/acoes.py` | a supervisão **não** faz segunda derivação do que se pode fazer |
| Contagem de inscrições recebidas, antes de abrir | rótulo da ação, por Edital | a supervisão soma no Processo; não recalcula por Edital |
| Inscrições por Perfil e por modalidade, com o número como filtro | `inscricoes.html` | a supervisão não repete o recorte |
| Etapas com equipe, sem equipe, membros sem alocação | `alocacoes.html` | a supervisão não replica a matriz |
| Cobertura da distribuição por Etapa, com o número como filtro | `distribuicao.html` | a supervisão sinaliza a existência; a lista continua lá |
| Ato de ordenação vigente marcado como obsoleto, com a divergência | `ordenacao.html` | a supervisão traz o sinal para fora; o diagnóstico continua lá |
| Pendências de publicação com destino, e a razão quando não há destino | `_pendencias.html` | é o modelo de redação dos sinais |
| Resultados da Etapa, recursos, resultados divulgados | telas próprias | destino de encaminhamento |

### 1.3 O que ela acrescenta, e é tudo

1. **O Processo acima do Edital.** Somar inscrições e nomear a que Edital pertence cada data.
2. **O tempo.** Evolução das submissões, prazo do período de inscrições, próximos marcos, e a
   divergência entre o que o cronograma declara e o que os fatos mostram.
3. **Cinco sinais**, e nenhum a mais, que hoje não são formulados por tela nenhuma — ou que só se
   descobrem abrindo N telas, uma a uma.

---

## 2. Decisões fechadas antes do planejamento

### D-001 — Duas regiões, e só duas

**Pulso** é permanente e não precisa ser anomalia: quem preside quer ver o volume de inscritos num
dia em que nada há de errado. **Atenção** é exclusivamente acionável.

A tentação que esta decisão bloqueia é a inversa em cada região: transformar tudo em alerta para
justificar a presença de um número, e manter seções permanentes de "0 pendências" que convertem a
página num menu com contadores. Sinal ausente não ocupa espaço; ausência de sinal é tela curta.

### D-002 — O catálogo de sinais é fechado, e nomeado por identificador verificado

Cinco sinais, definidos em `UX-001` a `UX-005`. **Sinal novo exige revisão desta spec.**

O identificador importa por uma razão mecânica: a varredura de citações reconhece `FR-`, `SC-`,
`UX-` e `D-`, e falha quando um deles é citado sem definição. Um rótulo fora desse conjunto —
`S01`, por exemplo — citado num template e definido em lugar nenhum passa em silêncio, que é
exatamente o defeito que a varredura existe para pegar. Com `UX-`, *"sinal novo exige revisão"*
deixa de ser promessa e passa a quebrar o build.

### D-003 — Etapa não ganha ciclo de vida

`EtapaAvaliacao` não tem estado: não existe abrir, encerrar, atrasar nem bloquear. A proposta
original listava sete estados de Etapa e, três seções antes, prometia não introduzir um segundo
estado do Processo.

A supervisão trabalha com o que existe: Evento vinculado ou não, datas do Evento quando há, e
fatos produzidos pelas features. **Se um dia houver necessidade normativa de abrir e fechar Etapa**
— proibir avaliação fora da janela, por exemplo — **isso é feature de domínio, e não tela.**

Consequência direta: *"todo o trabalho está concluído mas a Etapa não foi formalmente encerrada"*
**não é sinal**. É afirmação sobre um estado que o domínio não tem.

### D-004 — O `status` do Evento continua declarado; a divergência é o sinal

`EventoCronograma.status` é preenchido à mão e nasce `PLANEJADO`. Derivar atraso dele produziria um
muro de alarme falso no dia em que ninguém o mantiver; substituí-lo por derivação das datas
apagaria uma declaração que alguém fez de propósito.

A supervisão **não altera essa semântica**. Ela exibe os dois e faz da discordância o sinal:

```text
Evento declarado PLANEJADO · prazo encerrado em 08/09/2026
```

É o mesmo padrão que a `015` já usa para o ato obsoleto: não decidir qual é o verdadeiro, mostrar
que discordam, e deixar o ato para quem tem competência.

### D-005 — Prazo e marco são do Edital; o Processo soma, mas não herda data

`Cronograma` pertence a um Edital. Um Processo com três Editais tem três períodos de inscrição e
três listas de marcos. **O total de inscritos do Processo é a soma; o prazo do Processo não
existe.**

Por isso o desdobramento por Edital não é enfeite: é a forma correta de tudo o que tem data. Com um
Edital — o caso comum — a leitura continua curta, mas a etiqueta permanece.

### D-006 — Percentual só onde o domínio determina um conjunto finito de unidades esperadas

Avaliação tem denominador: a Etapa declara quantas avaliações cada inscrição recebe, e o esperado é
determinável. **Inscrição não tem.** Não existe conjunto de inscrições esperadas, e vaga não serve —
40 vagas e 1.284 candidatos não são 3.210 %.

Para inscrição: contagem, evolução e prazo. Para avaliação: concluído sobre esperado, sempre com
numerador e denominador à vista. E nenhum percentual global do Processo: uma Etapa de três dias com
20 candidatos não pesa o mesmo que uma de quinze dias com 5.000 avaliações, e inventar o peso é
inventar norma.

### D-007 — A supervisão não persiste estado

Nenhum item do Pulso ou da Atenção exige coluna, tabela ou projeção nova: tudo sai de fato já
gravado. Isso não é coincidência — é o teste empírico de que a fronteira foi respeitada.

> A necessidade de persistir estado novo durante a implementação é indício de violação de fronteira
> e **provoca revisão desta spec**, não uma migration.

Não impede cache técnico futuro respaldado por medição; impede que cache vire verdade de domínio, e
impede projeção de eventos, que seria um segundo registro dos mesmos fatos.

### D-008 — Elegibilidade de julgador é pergunta agregada, e não `recurso × membro`

São duas perguntas distintas, e devem continuar sendo:

```text
018:  esta pessoa pode julgar esta peça?      → cinco perguntas, no ato de julgar
022:  existe ao menos uma pessoa elegível?    → conjuntos de membros e de autorias
```

A `018` recusou de propósito a verificação por linha de listagem (`T-006` da `018`), e a supervisão
**não pode reintroduzi-la** iterando o guardião individual sobre o produto de recursos por membros.
A existência de capacidade sai da álgebra sobre as autorias já persistidas.

**E há um limite que o levantamento técnico encontrou, e que estreita o sinal.** Julgar exige
também uma permissão sistêmica, e o sistema **não sabe quem a possui**: papéis chegam declarados na
sessão e não há registro que ligue identidade a papel. O que é determinável é o outro lado — quem
está **impedido** por autoria de ato. Logo o sinal afirma o que os dados sustentam, *"nenhum membro
ativo da comissão está desimpedido"*, e **não** afirma que o julgamento é impossível: alguém de fora
da comissão pode deter a permissão. A diferença entre as duas frases é a diferença entre um fato e
uma inferência que o domínio não autoriza.

### D-009 — Cada sinal conduz à dona, e a supervisão nunca replica a lista

Na tela dona vigora a decisão já tomada e escrita: **os números são o filtro**. A supervisão diz que
existem 17 avaliações pendentes e leva à distribuição; ela **não** constrói uma segunda tabela com
aquelas 17 linhas. O número, sim; a lista, não.

### D-010 — A série de submissões é diária, e pelo instante de submissão

**Pelo instante de submissão, nunca pelo de criação.** O instante de criação pertence ao rascunho e
descreve outra coisa; a curva de inscrições recebidas é sobre o que foi entregue. O domínio já
garante a leitura: o estado submetido é inalcançável sem instante de submissão, por restrição
declarativa — a série não tem como sair silenciosamente errada.

**Diária, e não acumulada.** A curva acumulada é monotônica: as duas concentrações esperadas —
abertura e véspera do fecho — aparecem só como mudança de inclinação, que um traço pequeno não
comunica. A série diária mostra as duas pontas diretamente. O acumulado permanece como número dito,
não como desenho.

---

## 3. Contratos herdados e reuso obrigatório

| Contrato | De onde | Como a 022 o usa |
|---|---|---|
| Autorização por presidência do Processo | `011` | mesma base que já governa o detalhe do Processo |
| Resposta uniforme de não encontrado para o que o ator não alcança | convenção desde a `011` | a recusa é a mesma; nunca uma negativa que revele existência |
| Inscrição submetida × rascunho | `009` | grandezas distintas; rascunho nunca soma ao total |
| Avaliações previstas por inscrição, e o que a ausência significa | `012` | leitor único; a supervisão não reimplementa a regra |
| Cobertura da distribuição por Etapa | `012` | a supervisão sinaliza; o recorte continua na dona |
| Obsolescência do ato de ordenação | `015` | o cálculo é o existente; a supervisão só o traz para fora |
| Impedimento do julgador | `018` | consultado de forma agregada (`D-008`) |
| Pendência que aponta para onde se resolve, e diz quando não há onde | `003` | modelo de redação dos sinais |
| Conjunto de atos disponíveis do Edital | `001`/`002` | a supervisão **não** o rederiva |

**A `021` não entra.** Na `main`, em 09/09/2026, ela está especificada e sem nenhuma tarefa
concluída, e portanto não produz fato para supervisionar. **Existe branch paralela em que ela está
implementada**, e é dela que virá o fato — o que não muda esta spec: quando o sorteio chegar à
`main`, ele entra pela porta que a `015` já abriu, porque sorteio constitui uma **ordem**, e ordem
já tem tela, ato e obsolescência. O sinal de ato obsoleto (`UX-004`) passa a cobri-lo sem requisito
novo.

---

## 4. Problema

Quem preside conduz um certame cujos fatos estão todos gravados e cuja leitura está espalhada.

- **Não existe o Processo.** A contagem de inscrições é por Edital, no rótulo da ação. Um Processo
  com três Editais não tem, em lugar nenhum, quantas inscrições recebeu.
- **Não existe o tempo.** O instante de cada submissão está gravado e ninguém o lê como série. A
  pergunta *"o volume aumentou agora que o prazo se aproxima?"* não tem onde ser feita.
- **Não existe o confronto.** O período de inscrições é declarado no cronograma, o volume vive na
  inscrição, e nenhuma tela tem as duas metades.
- **Há condições que travam o próximo ato e ninguém as formula.** A mais grave: com uma comissão de
  duas ou três pessoas acumulando papéis, pode não haver **ninguém elegível** para julgar um
  recurso. A pergunta operacional não é *"quantos recursos pendentes"* — é *"existe quem possa
  julgá-los?"*, e nenhuma tela a faz.
- **Há sinais que existem e estão fundos.** A obsolescência de um ato de ordenação só se descobre
  abrindo o marco; a cobertura insuficiente de uma Etapa, abrindo a distribuição de cada uma.

O custo disso é a reconstrução mental do andamento a partir de planilha, mensagem e memória — que é
precisamente o que o sistema existe para tornar desnecessário.

---

## Clarifications

### Sessão 2026-09-09

- **P: a feature é a `014`?** → **Não. É a `022`.** `014`, `016` e `019` estão reservadas no arco
  aberto pela `013` (progressão entre Etapas, ocupação de vagas, notificação e convocação).
- **P: Etapa passa a ter ciclo de vida?** → **Não nesta feature** (`D-003`). Criar lifecycle para
  alimentar uma tela é inversão de dependência; se houver necessidade normativa, é feature própria.
- **P: o `status` do Evento deixa de ser declarado?** → **Não** (`D-004`). Declarado e temporal
  convivem, e a divergência entre eles é o sinal.
- **P: o painel mostra percentual global do Processo?** → **Não** (`D-006`). *N de M Etapas
  concluídas* mais o progresso da Etapa corrente é interpretável e auditável; um percentual único
  não é.
- **P: a supervisão replica os registros que o sinal conta?** → **Não** (`D-009`). Ela encaminha à
  dona, onde os números já são o filtro.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O pulso do Processo, numa tela (Priority: P1)

Quem preside abre o Processo e, sem navegar, sabe quantas pessoas se inscreveram no Processo
inteiro, como isso se reparte entre os Editais, quantos rascunhos existem, quando o período de
inscrições encerra em cada Edital e quais são os próximos marcos.

**Why this priority**: é a leitura que a presidência faz todo dia, é a que hoje não existe em
nenhum nível, e é a única que entrega valor sozinha — mesmo que nenhum sinal de atenção fosse
implementado.

**Independent Test**: com um Processo com dois Editais publicados e inscrições recebidas, abrir a
supervisão e conferir que a soma, o desdobramento por Edital e as datas de cada Edital conferem com
o que as telas de inscrições e o cronograma de cada Edital dizem separadamente.

**Acceptance Scenarios**:

1. **Given** um Processo com dois Editais publicados, com 814 e 327 inscrições submetidas,
   **When** quem preside abre a supervisão, **Then** o total do Processo é 1.141, e cada Edital
   aparece nomeado com o seu número.
2. **Given** um Edital cujo período de inscrições encerra em dois dias, **When** a supervisão é
   aberta, **Then** o prazo é apresentado **nomeando o Edital**, e não como se fosse do Processo.
3. **Given** um Processo cujos Editais ainda não foram publicados, **When** a supervisão é aberta,
   **Then** ela declara que não há período de inscrições em curso, em vez de exibir zero sem
   explicação.
4. **Given** rascunhos e submissões coexistindo, **When** a supervisão é aberta, **Then** as duas
   grandezas aparecem separadas, e o rascunho **não** é somado ao total de inscrições.

---

### User Story 2 — Acompanhar a procura enquanto o prazo corre (Priority: P1)

Com as inscrições abertas, quem preside acompanha a evolução das submissões ao longo do período e
lê o volume recente contra o prazo que resta.

**Why this priority**: é a informação nova de maior valor e menor custo — o dado já está gravado —,
e é a que responde à pergunta que hoje leva a equipe a exportar planilha.

**Independent Test**: submeter inscrições em dias distintos dentro do período e conferir que a série
diária reflete a distribuição, que o volume das últimas 24 horas confere, e que nenhuma delas conta
rascunho.

**Acceptance Scenarios**:

1. **Given** submissões distribuídas ao longo de oito dias, **When** a supervisão é aberta,
   **Then** a série diária apresenta a distribuição por dia dentro do período do Edital.
2. **Given** rascunhos criados há dez dias e nunca submetidos, **When** a série é lida, **Then**
   nenhum deles aparece nela.
3. **Given** a série apresentada graficamente, **When** ela é lida por tecnologia assistiva,
   **Then** existe equivalente textual com os mesmos valores.
4. **Given** qualquer volume de inscrições, **When** a supervisão é aberta, **Then** nenhum
   percentual de avanço é apresentado para inscrição.

---

### User Story 3 — Saber o que impede o próximo ato (Priority: P1)

Quem preside vê, num bloco só, as condições que travam o avanço do Processo — e apenas elas.

**Why this priority**: é a diferença entre uma página informativa e uma página de supervisão. O
sinal de recurso sem julgador elegível é, para uma comissão pequena, mais importante do que
qualquer contagem.

**Independent Test**: montar cada uma das cinco condições, uma por vez, e conferir que a supervisão
a nomeia; desfazê-la e conferir que o sinal desaparece sem deixar seção vazia.

**Acceptance Scenarios**:

1. **Given** uma Etapa sem Evento de cronograma vinculado, **When** a supervisão é aberta,
   **Then** ela aparece como **sem marco no cronograma** — e não como atrasada, aguardando ou 0 %.
2. **Given** um Evento declarado `PLANEJADO` cujo prazo já encerrou, **When** a supervisão é aberta,
   **Then** o sinal apresenta **as duas informações**, sem afirmar qual delas é a verdadeira.
3. **Given** uma Etapa com inscrições sem avaliador suficiente, **When** a supervisão é aberta,
   **Then** o sinal nomeia a Etapa e a quantidade, com numerador e denominador.
4. **Given** um ato de ordenação vigente tornado obsoleto por entrada nova, **When** a supervisão é
   aberta, **Then** o sinal aparece sem que seja preciso abrir o marco.
5. **Given** recursos aguardando julgamento e todos os membros ativos impedidos por autoria de
   ato, **When** a supervisão é aberta, **Then** o sinal nomeia a condição — e não apenas a
   quantidade pendente —, sem afirmar que o julgamento é impossível.
6. **Given** nenhuma das cinco condições presente, **When** a supervisão é aberta, **Then** a região
   de atenção declara ausência em uma linha, sem seções vazias por sinal.

---

### User Story 4 — Do sinal ao lugar onde se resolve (Priority: P2)

Cada sinal leva à tela da feature dona, já no ponto em que a situação se resolve.

**Why this priority**: sem o encaminhamento a supervisão vira aviso sem remédio; com ele, deixa de
haver razão para replicar qualquer lista.

**Independent Test**: acionar o encaminhamento de cada sinal e conferir que ele chega à tela dona, e
que a supervisão não apresenta em si mesma os registros contados.

**Acceptance Scenarios**:

1. **Given** o sinal de cobertura insuficiente, **When** quem preside o aciona, **Then** chega à
   distribuição da Etapa nomeada, onde o recorte já existe.
2. **Given** o sinal de ato obsoleto, **When** acionado, **Then** chega à ordenação do marco, onde a
   divergência é diagnosticada.
3. **Given** qualquer sinal, **When** a supervisão é lida, **Then** ela **não** apresenta a lista dos
   registros que o sinal conta.
4. **Given** um ator que não alcança a tela dona de um sinal, **When** a supervisão é aberta,
   **Then** aquele sinal não lhe é apresentado.

---

### Edge Cases

- **Processo com um único Edital.** É o caso comum. O desdobramento por Edital continua nomeando o
  Edital, e a leitura permanece curta — a etiqueta não some porque só há um.
- **Processo com Editais em situações diferentes** — um publicado com inscrições abertas, outro em
  elaboração. O Pulso soma o que existe e não inventa período para quem não o tem.
- **Edital sem cronograma, ou cronograma sem período de inscrições marcado.** Dito explicitamente,
  em vez de prazo em branco.
- **Etapa sem Evento vinculado.** É publicável e legítimo: a validação de publicação recusa
  referência a Evento inexistente, mas **admite ausência de referência**. Vira sinal, não erro.
- **Evento sem data de término.** Existe no domínio. Não produz divergência temporal; o sinal exige
  as duas datas.
- **Evento declarado `CONCLUIDO` com prazo ainda em curso.** É divergência no sentido inverso, e o
  sinal a trata do mesmo modo: dois fatos, nenhum arbitrado.
- **Evento `CANCELADO`.** Não produz divergência temporal nem entra nos próximos marcos.
- **Nenhuma inscrição submetida, com período aberto.** Zero é resposta, e é apresentado como tal.
- **Todas as condições de atenção ausentes.** A região encolhe a uma linha; não há seção por sinal.
- **Processo cancelado.** A supervisão continua legível — os fatos permanecem e alguém responde por
  eles —, e nenhum encaminhamento oferece ato que a situação não admite.
- **Ator sem alcance a uma das telas donas.** O sinal correspondente não aparece, e a ausência não é
  anunciada: anunciar que existe algo que não se pode ver é vazamento por agregação.
- **Comissão de uma pessoa só, que também preside e avalia.** Estado previsto e testado. Nenhum
  sinal decorre do tamanho da comissão; o de recurso sem julgador decorre de **autoria de atos**.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Alcance, autorização e fronteira

- **FR-001**: O sistema MUST oferecer, a partir do Processo Seletivo, uma visão de supervisão que
  reúna o Pulso e a Atenção definidos nesta spec.
- **FR-002**: O acesso MUST ser autorizado por **uma de duas bases, cada uma suficiente sozinha** —
  a presidência ativa **deste** Processo, ou a permissão sistêmica de gerir comissão no mesmo escopo
  institucional. São as bases que já governam a página do Processo, e o sistema MUST NOT introduzir
  papel, permissão ou vínculo novo. *Exigir as duas faria a presidência depender do papel de gestor;
  aceitar qualquer papel global faria a presidência valer em todo Processo.*
- **FR-003**: A recusa MUST usar a resposta uniforme de não encontrado já adotada para tudo o que o
  ator não alcança, e MUST NOT distinguir entre inexistência e falta de autorização.
- **FR-004**: Cada **sinal** MUST ser apresentado apenas a quem alcança a tela dona do seu destino,
  e a supressão MUST ser silenciosa.
- **FR-004a**: Os agregados do Pulso MUST NOT ser suprimidos por alcance, e a razão é que eles não
  têm destino nem dado pessoal: são contagens e nomes de Edital, Etapa e marco, e a base que
  autoriza a leitura é a do próprio Processo (`FR-002`). O Pulso MUST NOT apresentar nome, CPF,
  protocolo ou qualquer identificação de candidato — é essa proibição que sustenta a anterior.
- **FR-005**: Todo número apresentado MUST ser reproduzível a partir dos registros oficiais das
  features donas, e a supervisão MUST NOT constituir fonte de verdade de estado algum.
- **FR-006**: A supervisão MUST NOT alterar distribuição, avaliação, Resultado, Etapa, cronograma,
  ato de ordenação, publicação ou recurso, nem oferecer ato que a corrija automaticamente.
- **FR-007**: A supervisão MUST NOT introduzir estado persistente próprio para representar
  andamento, progresso, sinal ou situação derivada (`D-007`).
- **FR-008**: A supervisão MUST NOT constituir segunda derivação do conjunto de atos disponíveis de
  um Edital, que já é calculado num lugar só.
- **FR-009**: A supervisão MUST apresentar o instante da leitura dos indicadores.

#### Pulso — inscrições

- **FR-010**: O sistema MUST apresentar o total de inscrições **submetidas** no Processo, somando
  seus Editais.
- **FR-011**: O sistema MUST desdobrar esse total por Edital, **nomeando cada Edital**.
- **FR-012**: O sistema MUST apresentar a quantidade de inscrições em rascunho como grandeza
  distinta, e MUST NOT somá-la ao total de submetidas.
- **FR-013**: Havendo período de inscrições em curso em algum Edital, o sistema MUST apresentar a
  quantidade de inscrições submetidas nas últimas 24 horas **no Processo**, somando seus Editais.
  Encerrados todos os períodos, o número MUST NOT ser apresentado: fora da janela ele é sempre zero,
  e zero apresentado como notícia é ruído — a ausência de período já é dita por `FR-018`.
- **FR-014**: O sistema MUST apresentar a evolução das submissões em série **diária**, **por
  Edital**, ao longo do período de inscrições declarado por aquele Edital (`D-010`).

  *Os dois níveis são deliberadamente distintos, e a razão é `D-005`: a leitura recente é uma
  contagem, e contagem soma; a série é recortada por um período, e período é do Edital. Um Processo
  com três Editais tem **três séries** e **um** número de 24 horas.*
- **FR-015**: A série MUST ser construída exclusivamente sobre o instante de submissão, e MUST NOT
  usar o instante de criação da inscrição.
- **FR-016**: Qualquer apresentação gráfica da série MUST possuir equivalente textual com os mesmos
  valores, e MUST NOT provocar rolagem horizontal do corpo da página.
- **FR-017**: O sistema MUST NOT apresentar percentual de avanço para inscrição, por ausência de
  denominador normativo (`D-006`).
- **FR-018**: Quando não houver Edital com período de inscrições em curso, o sistema MUST declarar
  essa condição, e MUST NOT apresentar zero sem qualificação.

#### Pulso — cronograma

- **FR-019**: O sistema MUST apresentar, para cada Edital, o período de inscrições declarado e
  quanto falta para o seu encerramento.
- **FR-020**: Toda data apresentada MUST nomear o Edital a que pertence, e o sistema MUST NOT
  apresentar prazo ou marco como sendo do Processo (`D-005`).
- **FR-021**: O sistema MUST apresentar os próximos marcos de cada Edital, em ordem cronológica.
- **FR-022**: Edital sem cronograma, e cronograma sem período de inscrições marcado, MUST ser
  declarados como tais.
- **FR-023**: O sistema MUST NOT alterar a semântica declarada do estado de um Evento de cronograma
  (`D-004`).

#### Atenção — catálogo fechado

- **FR-024**: O sistema MUST apresentar exclusivamente os sinais definidos em `UX-001` a `UX-005`, e
  MUST NOT apresentar sinal fora desse catálogo (`D-002`).
- **FR-025**: Sinal ausente MUST NOT ocupar espaço; a ausência de todos MUST ser declarada em uma
  única linha, e o sistema MUST NOT manter seção permanente por sinal (`D-001`).
- **FR-026**: O sistema MUST identificar Etapa sem Evento de cronograma vinculado, e MUST NOT
  atribuir a ela situação temporal, progresso ou atraso.
- **FR-027**: O sistema MUST identificar Evento cujo estado declarado seja incompatível com sua
  posição temporal observável, apresentando **as duas informações** sem arbitrar entre elas.
- **FR-028**: O sistema MUST identificar a existência de Etapa cuja cobertura de avaliação seja
  insuficiente, nomeando a Etapa e o Edital.
- **FR-029**: O sistema MUST identificar ato de ordenação vigente marcado como obsoleto, usando o
  cálculo já existente na feature dona.
- **FR-030**: O sistema MUST identificar a existência de recurso aguardando julgamento para o qual
  nenhum membro ativo da comissão do Processo esteja desimpedido.
- **FR-030a**: A mensagem MUST se limitar ao impedimento verificável e MUST NOT afirmar que o
  julgamento é impossível, porque a titularidade da permissão de julgar não é determinável pelo
  sistema (`D-008`).
- **FR-031**: A verificação de `FR-030` MUST ser calculada de forma agregada sobre os conjuntos de
  membros e de autorias já persistidas, e MUST NOT iterar o guardião individual de impedimento
  sobre o produto de recursos por membros (`D-008`).
- **FR-032**: Todo percentual apresentado MUST vir acompanhado de numerador e denominador.
- **FR-033**: Unidade de trabalho esperada e não distribuída MUST ser apresentada como pendente, e
  MUST NOT ser retirada do denominador.
- **FR-034**: O sistema MUST NOT classificar, ordenar ou qualificar o desempenho de membros da
  comissão, nem apresentar carga individual de trabalho.

#### Encaminhamento

- **FR-035**: Cada sinal apresentado MUST conduzir à tela da feature dona correspondente.
- **FR-036**: O encaminhamento MUST obedecer às regras de autorização da tela de destino. A
  supervisão decide **se oferece** o destino (`FR-004`); quem **recusa** continua sendo a tela de
  destino, e a supervisão MUST NOT antecipar essa recusa como autorização.
- **FR-037**: A supervisão MUST NOT apresentar a lista dos registros que um sinal conta (`D-009`).

### Requisitos de apresentação

- **UX-001** — **Etapa sem marco no cronograma.** A Etapa é nomeada com o seu Edital, e a ausência
  é dita nesses termos — nunca como *aguardando*, *atrasada* ou percentual zero.
- **UX-002** — **Divergência entre estado declarado e posição temporal.** As duas informações
  aparecem juntas, na forma *declarado X · prazo encerrado em D*, sem que a tela afirme qual vale.
- **UX-003** — **Cobertura de avaliação insuficiente.** A Etapa e o Edital são nomeados, com
  numerador e denominador, e o encaminhamento leva à distribuição daquela Etapa.
- **UX-004** — **Ato de ordenação vigente obsoleto.** O marco é nomeado, e o encaminhamento leva à
  ordenação, onde a divergência já é diagnosticada.
- **UX-005** — **Recurso sem membro desimpedido.** A mensagem nomeia a condição — *todos os
  membros da comissão estão impedidos de julgar estes recursos* — e não a quantidade pendente
  isolada; o encaminhamento leva aos recursos daquele Edital.
- **UX-006** — Pulso e Atenção são regiões visualmente distintas. A Atenção não mantém seção por
  sinal: sinal ausente não ocupa espaço, e a ausência de todos é **uma linha declarada** — a região
  encolhe, mas não some. Sumir não distinguiria *nada a sinalizar* de *a página não carregou*
  (`FR-025`).
- **UX-007** — Toda contagem do Pulso nomeia a que Edital pertence quando a informação for do
  Edital, mesmo havendo um só.
- **UX-008** — A série de submissões é legível sem cor e sem imagem, com equivalente textual.

### Key Entities

**Nenhuma entidade nova.** A supervisão lê o que as features donas já persistem:

- **Processo Seletivo** e **Edital** — identidade, situação e pertencimento.
- **Cronograma** e **Evento de Cronograma** — datas, ordem, estado declarado e a marca do período de
  inscrições. Pertencem ao Edital.
- **Etapa de Avaliação** — ordem, avaliações previstas por inscrição, e o vínculo **opcional** com
  um Evento.
- **Inscrição** — estado (rascunho ou submetida), instante de submissão, Edital e Perfil.
- **Atribuição** e **Avaliação** — o que foi distribuído, iniciado e concluído.
- **Membro da Comissão** — vínculo com o Processo, e as autorias que determinam impedimento.
- **Ato de Ordenação** — vigência e obsolescência.
- **Recurso** — existência, situação e objeto atacado.

---

## 5. Invariantes observáveis

1. **O total do Processo é a soma dos Editais**, e nenhuma data do Processo existe sem Edital que a
   sustente.
2. **Rascunho nunca soma a inscrição.** As duas grandezas aparecem separadas em toda leitura.
3. **Todo percentual mostra numerador e denominador**, e inscrição não recebe percentual.
4. **Unidade esperada e não distribuída aparece como pendente**, e permanece no denominador.
5. **Nenhum estado é criado pela supervisão.** O que ela mostra existe antes dela e sobrevive a ela.
6. **A supervisão não corrige o que detecta.**
7. **Sinal fora do catálogo não existe.** Acrescentá-lo é revisar esta spec.
8. **O que a supervisão conta, a dona lista.** Nunca as duas.

---

## 6. Out of Scope

Explicitamente fora, e cada item pelo motivo registrado:

- **Tabela de produtividade ou carga por membro** — a operação é de duas ou três pessoas acumulando
  papéis, e a presidência avalia; a tabela mediria a presidência contra si mesma.
- **Feed de atividade recente** — duplicaria a trilha de auditoria, que já é a fonte imutável.
- **Read model, projeção materializada, event sourcing ou cache como requisito** — `D-007`.
- **Estado de Etapa** (aberta, em andamento, encerrada, atrasada, bloqueada) — `D-003`.
- **Etapa concluível ainda não encerrada** — pressupõe um ato de encerramento que não existe.
- **Percentual global do Processo** — `D-006`.
- **Tempo real como requisito arquitetural** — o contrato é o instante da leitura (`FR-009`), não a
  tecnologia de atualização.
- **Inscrição cancelada** — o estado não existe no domínio.
- **Alerta por ausência de movimentação** ("nenhuma avaliação concluída em 24 h") — exigiria
  definição de abandono que o domínio não sustenta.
- **Separar rascunho ativo de rascunho abandonado** — a inscrição não guarda instante de última
  edição; o fato é derivável da trilha de auditoria, e usá-la como fonte de indicador operacional é
  decisão de fronteira que esta feature não toma.
- **Ato de ordenação emitido e não divulgado** — computável, mas a espera pode ser legítima, e
  transformá-la em alerta é o modo de falha que o catálogo fechado existe para evitar. Candidato
  registrado, semântica a definir.
- **Sinais originados na `021`** — a feature não produz fato na `main`; quando produzir, ela é
  consumida como ordem pela porta da `015`, e não por sinal próprio.
- **Qualquer visão entre Processos distintos**, catálogo institucional ou histórico comparativo.

### Achados registrados, e que não são escopo desta feature

Levantados durante o inventário. Governança é do usuário; ficam como registro, não como escopo:

- **A tela de recursos não é alcançável por nenhuma outra tela.** Não há caminho até a listagem de
  recursos de um Edital senão digitando a URL. A correção cabe em poucas linhas, no mesmo padrão da
  contagem de inscrições recebidas — e não deveria esperar esta spec.
- **Conflito de vocabulário.** A tela de inscrições chama os rascunhos de *em preenchimento*; a
  supervisão precisa do mesmo termo ou de uma mudança decidida que valha para as duas telas. Dois
  termos para o mesmo conceito sem justificativa documentada é o que a linguagem ubíqua proíbe.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quem preside identifica, em uma única tela e sem navegar, o volume de inscritos do
  Processo, o prazo mais próximo e a existência ou não de condição que impeça o próximo ato.
- **SC-002**: O total de inscrições submetidas apresentado é igual à soma dos totais que as telas de
  inscrição de cada Edital apresentam separadamente.
- **SC-003**: Nenhum rascunho é contado como inscrição submetida em qualquer leitura da supervisão.
- **SC-004**: 100 % dos percentuais apresentados exibem numerador e denominador verificáveis.
- **SC-005**: Nenhum percentual é apresentado para inscrição.
- **SC-006**: Uma unidade de trabalho esperada e não distribuída aparece como pendência e não
  desaparece do denominador.
- **SC-007**: Toda data apresentada nomeia o Edital a que pertence, inclusive quando o Processo tem
  um único Edital.
- **SC-008**: Uma Etapa sem Evento vinculado é apresentada como sem marco no cronograma, e nunca
  como atrasada, aguardando ou com progresso zero.
- **SC-009**: Um Evento declarado como planejado com prazo encerrado produz um sinal que apresenta
  as duas informações, sem que a tela afirme qual delas vale.
- **SC-010**: Existindo recurso pendente e nenhum membro ativo desimpedido, a supervisão nomeia a
  condição; bastando um membro desimpedido, ela não a apresenta.
- **SC-011**: Com todas as condições de atenção ausentes, a região de atenção ocupa uma linha e não
  apresenta seção por sinal.
- **SC-012**: Um ator sem autorização sobre o Processo recebe a mesma resposta que receberia para um
  Processo inexistente, e não consegue inferir a existência dele.
- **SC-013**: Um ator que não alcança a tela dona de um sinal não vê aquele sinal nem menção à sua
  supressão.
- **SC-014**: A entrega não acrescenta nenhuma estrutura de dados persistente ao sistema.
- **SC-015**: A série de submissões é integralmente legível por tecnologia assistiva, com os mesmos
  valores do gráfico.

---

## Assumptions

- **A operação é pequena.** Duas ou três pessoas acumulando papéis, dezenas a poucos milhares de
  inscrições por Edital. É o que dispensa projeção materializada e o que torna a pergunta agregada
  de elegibilidade barata.
- **O caso comum é um Edital por Processo.** O desdobramento existe para o caso de vários, e não o
  penaliza: com um só, a etiqueta permanece e a leitura continua curta.
- **A supervisão estende a página do Processo**, e não a substitui. O cartão de atos disponíveis
  continua sendo a fonte do que se pode fazer.
- **O período de inscrições é o Evento marcado como tal no cronograma**, e não um Evento inferido
  por texto — a marca existe no domínio e é única por cronograma.
- **A `021` não produz fato na `main`.** Há branch paralela que a implementa; quando ela chegar,
  entra pela porta da `015`, sem requisito novo aqui.
- **Nenhum requisito desta spec exige coluna, tabela ou migration nova.** A restrição é verificável
  na implementação, e a necessidade de violá-la provoca revisão da spec.

---

## 7. Ordem de implementação sugerida

Cada faixa entrega valor sozinha e pode ser demonstrada de ponta a ponta.

1. **Pulso das inscrições** — total do Processo, desdobramento por Edital, rascunhos, últimas 24 h.
   Entrega a `US1` parcialmente e já responde à pergunta que hoje leva a equipe à planilha.
2. **Tempo** — período de inscrições, próximos marcos, série diária. Fecha `US1` e `US2`.
3. **Atenção, os cinco sinais** — na ordem `UX-001`, `UX-002`, `UX-003`, `UX-004`, `UX-005`. Os três
   primeiros só dependem de cronograma e distribuição; o quarto reusa cálculo pronto; o quinto é o
   único que exige desenho de consulta agregada.
4. **Encaminhamento** — fecha `US4`, e é o que impede a tentação de listar na supervisão.

## 8. Gate de conclusão

A feature está concluída quando, e apenas quando:

- quem preside abre o Processo e obtém `SC-001` sem navegar para outra área;
- as cinco condições de atenção podem ser montadas e desfeitas uma a uma, e a supervisão as nomeia e
  as retira sem deixar seção vazia;
- nenhuma migration foi criada, e nenhuma estrutura persistente foi acrescentada;
- nenhum registro contado por um sinal é listado pela supervisão;
- a demonstração ocorre pela interface administrativa, com o papel exato de quem preside, sem
  manipulação de banco e sem shell.
