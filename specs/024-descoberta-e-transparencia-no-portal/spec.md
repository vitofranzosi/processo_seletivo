# Feature Specification: Descoberta e Transparência no Portal Público

**Feature Branch**: `claude/spec-selecoes-ifrn-ifes-0a59c7`

> **O diretório da worktree carrega o nome da origem** — a comparação com o portal de outra
> instituição que motivou a leitura. A pasta da spec, não: o que a feature entrega é público,
> descoberta e transparência, e não a semelhança com portal nenhum.

> **A numeração é `024` porque a `023` está sendo escrita em paralelo**, noutra worktree
> (`023-criar-a-partir-de-edital-anterior`). Duas features simultâneas não podem descobrir o número
> uma da outra pela pasta: o `speckit` numera pela última existente em `specs/`, e a última que ele
> enxerga é a desta árvore. Os identificadores desta spec foram conferidos contra a `023` paralela
> antes de escritos — ela reinicia em `FR-001`, e não há colisão.

**Created**: 2026-09-09

**Status**: Draft

**Input**: O portal público mostra uma fração do que o sistema já publicou, e não permite encontrar
nada. O cronograma do Edital está no conteúdo publicado e só é renderizado **depois** da
identificação; atribuições, carga horária e remuneração da vaga estão publicados e não aparecem em
lugar nenhum; retificações existem no histórico público e nenhuma tela as menciona — o candidato lê
o conteúdo vigente sem saber que ele mudou. Na vitrine não há busca, filtro nem ordenação, e tudo o
que não está com inscrição aberta cai num grupo só, sem distinguir o que ainda vai abrir do que já
fechou.

> **Frase que governa:** o portal mostra, **antes de qualquer identificação**, tudo o que o ato
> publicado já diz — e deixa encontrar a oportunidade certa sem ler todas.

> **E a frase que mantém o corte:** esta feature **não publica nada**. Cada informação que ela
> acrescenta à tela já é conteúdo normativo vigente; o que muda é que passa a ser legível por quem
> ainda está decidindo.

---

## 1. O achado que organiza a feature

A leitura ingênua deste incremento diz "melhorar a página pública". Ela produziria uma lista de
ajustes de layout.

O que a verificação no código encontrou é outra coisa, e mais séria:

```text
ERRADO   falta informação na página pública
         → e então alguém precisa produzir informação nova

CERTO    a informação está publicada e não é renderizada
         → o ato normativo existe, é imutável, é vigente
           e o público não o enxerga
```

Três exemplos, verificados:

| O que o ato publicado já diz | Onde está | Quem consegue ler hoje |
|---|---|---|
| O cronograma inteiro, com data de cada Evento | `schedule`, no conteúdo publicado | só quem já se identificou, na área do candidato |
| Atribuições, carga horária e remuneração da vaga | `duties`, `workload`, `compensation` no Perfil publicado | ninguém, em nenhuma tela |
| Que houve Retificação, quando, por quê e o que mudou | histórico público de Publicações e Retificações | ninguém, em nenhuma tela |

O renderizador do cronograma **já existe** e serve a área do candidato. A consequência prática é
que quem já se inscreveu vê o calendário, e quem está decidindo se vale a pena, não — exatamente ao
contrário de quem precisa dele.

E a retificação é a mais grave das três, porque não é preferência de leitura: pelo Princípio II, um
Edital publicado só muda por Retificação. Uma pessoa que leu a página na semana passada e volta hoje
lê um conteúdo possivelmente diferente **sem nenhum sinal de que mudou** — e sem caminho para
descobrir o quê.

### 1.1 O segundo eixo: encontrar

Descoberta é problema de outra natureza, e de urgência menor hoje: com um punhado de seleções
publicadas, ler todos os cartões funciona. Ele entra neste incremento porque as duas frentes tocam
as mesmas duas telas, e porque o custo de voltar a elas depois é maior que o de fazer junto.

O que existe hoje é uma ordenação fixa e dois grupos. O grupo "outras" reúne o que ainda vai abrir,
o que já fechou e o que nunca recebeu inscrição por este sistema — três situações que o domínio já
distingue e que a tela funde.

## 2. O que já está entregue, e que esta feature NÃO reconstrói

Repetir qualquer uma destas é defeito, não escopo.

| Já entregue | Consequência para a `024` |
|---|---|
| Convite de inscrição por vaga, com três estados (inscrever-se, continuar, ver comprovante) | o convite, seu destino e seus três estados permanecem; a feature só acrescenta, ao lado dele, o aviso de que inscrever-se exige identificação (FR-137) |
| Requisitos, localidade e modalidades de concorrência na vaga | permanecem; a feature acrescenta os campos que faltam ao lado deles |
| Contagem e lista dos documentos que serão pedidos, antes da identificação | permanece; é o modelo de redação do que se anuncia antes de pedir |
| Período de inscrições com data-limite e prazo relativo | permanece; a feature o torna marca explícita do cartão |
| Anexos do Edital, na ordem editorial | permanecem onde estão |
| Resultados divulgados vigentes, antes dos Perfis | permanecem; o histórico normativo é outra coisa e vive em seção própria |
| Seleção cancelada fora da vitrine e alcançável pelo endereço | inalterado |
| Cronograma renderizado com situação por Evento | **reusado**, não reescrito |

## 3. Decisões fechadas antes do planejamento

### D-001 — Esta feature não escreve

Nenhuma tabela nova, nenhuma migration de dado normativo, nenhuma gravação. Tudo o que a `024`
exibe já é conteúdo publicado ou registro de ato publicado. É o que a torna barata e o que a mantém
dentro do Princípio II.

### D-002 — A consulta vive no endereço

Busca, filtros e ordenação são estado da consulta, não do leitor. Ficam no endereço, e não em
sessão: assim o resultado é compartilhável, o botão *voltar* do navegador funciona, e voltar da
seleção para a lista devolve a pessoa ao que ela tinha filtrado.

Sessão aqui produziria o defeito clássico: duas abas abertas na mesma vitrine mostrando listas
diferentes, e nenhuma explicação na tela.

### D-003 — Filtragem sobre o que já é carregado, e o sinal que muda isso

A vitrine já carrega as versões vigentes de todas as seleções publicadas para montar os cartões.
Filtrar e ordenar sobre esse conjunto não acrescenta consulta nenhuma, e é adequado à ordem de
grandeza de dezenas de seleções simultâneas.

**O sinal que obriga a revisar:** quando o catálogo publicado passar de algumas centenas de
seleções, ou quando a vitrine deixar de responder de imediato num navegador comum. Aí a resposta
não é otimizar o filtro — é uma projeção consultável do conteúdo publicado, que é feature própria e
está fora deste escopo (§7).

Construí-la agora seria inventar um índice para um catálogo que cabe numa tela, contra o
Princípio V.

### D-004 — Quatro situações, e não três

O domínio já distingue quatro, e a tela passa a dizer as quatro:

```text
aberta      recebendo inscrição agora, com prazo correndo
futura      período declarado que ainda não começou
encerrada   período declarado que já terminou
sem prazo   Edital que não recebe inscrição por este sistema
```

A quarta **não é** "encerrada". Chamá-la assim afirmaria um fechamento que Edital nenhum declarou.
Ela aparece como seleção consultável, sem frase de prazo.

### D-005 — O histórico é dito em linguagem do domínio

O registro público de uma Retificação carrega a justificativa, as datas e a identificação do que foi
alterado. A tela mostra **o que mudou em termos do Edital** — a seção, o Perfil, o Evento do
cronograma —, e não o endereçamento interno com que o sistema localiza a alteração.

Escrever caminho de estrutura de dados numa página pública transformaria transparência em ruído: diz
mais ao sistema do que a quem lê.

### D-006 — O que a página mostra é sempre o vigente; o histórico explica como se chegou nele

Não há duas leituras concorrentes do que vale. O conteúdo da página é o consolidado vigente, como já
é hoje. O histórico é registro: cada ato publicado — a abertura e cada Retificação — continua
alcançável pelo próprio documento, com a data em que foi publicado.

É a diferença entre *preservar* e *anunciar*, a mesma que já governa a seleção cancelada.

### D-007 — Cadastro reserva sem vaga imediata é oferta, não escassez

Um Perfil com zero vagas imediatas e cadastro reserva declarado é uma oportunidade legítima e
frequente. Hoje a tela põe o **zero** em destaque tipográfico e a reserva como legenda, e a leitura
que sobra é de ausência.

A leitura principal passa a ser a oferta que existe. O número de vagas imediatas continua dito, sem
ser o que salta.

### D-008 — Sem instrumentação de comportamento

Nenhuma métrica de navegação, clique ou funil é coletada por esta feature. Observar o percurso de
quem se candidata é decisão de proteção de dados sob o Princípio III, e não subproduto de um
incremento de tela. A verificação dos critérios desta spec é feita por percurso conduzido, como as
features anteriores fizeram.

### D-009 — Ausência nunca vira afirmação

Edital sem cronograma publicado, Perfil sem remuneração declarada, Edital sem retificação: em todos,
a tela **omite a seção**. Não escreve "não informado", "sem retificações" nem "cronograma não
divulgado".

O motivo é normativo, não estético: dizer "não informado" afirma uma omissão do Edital, e o Edital
pode nunca ter tido o que declarar naquele campo.

## 4. Problema

Duas perguntas que o portal não responde a quem ainda não é candidato:

1. **"O que exatamente está sendo oferecido, e quando as coisas acontecem?"** — respondida hoje
   apenas pelo PDF, embora o sistema tenha os dados estruturados e já saiba renderizá-los.
2. **"Esta é a versão que vale?"** — não respondida de forma alguma.

E uma terceira que só piora com o tempo:

3. **"Existe alguma vaga para mim aqui?"** — respondida hoje lendo todos os cartões.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Saber quando as coisas acontecem, antes de decidir (Priority: P1)

Alguém que encontrou uma seleção quer saber o que vem depois da inscrição: quando sai a homologação,
quando é a prova, quando é o resultado. Hoje precisa abrir o PDF e procurar a tabela — ou se
inscrever primeiro, o que é a ordem inversa da decisão.

**Why this priority**: é o dado publicado mais consultado e o mais escondido, e o renderizador já
existe. Maior valor por menor esforço da feature inteira.

**Independent Test**: abrir a página de uma seleção com cronograma publicado, sem sessão, e conferir
que cada Evento aparece com data e situação, na ordem publicada.

**Acceptance Scenarios**:

1. **Given** uma seleção publicada com cronograma, **When** alguém abre a página sem se identificar,
   **Then** vê os Eventos na ordem publicada, cada um com o período declarado e a situação do Evento
   (concluído, em curso, por vir).
2. **Given** um Evento com local declarado, **When** o cronograma é exibido, **Then** o local aparece
   junto do Evento.
3. **Given** uma seleção cujo Edital não publicou cronograma, **When** a página é aberta, **Then**
   nenhuma seção de cronograma aparece, e nenhuma frase de ausência é escrita.
4. **Given** um Evento já terminado, **When** a situação é exibida, **Then** ela descreve o Evento, e
   nunca quem está lendo.

---

### User Story 2 — Saber se o que estou lendo ainda vale (Priority: P1)

Alguém que leu o Edital há duas semanas volta à página. Quer saber se algo mudou — e, se mudou, o
quê e por quê — sem baixar e comparar PDFs.

**Why this priority**: é a única das três que não é conveniência. Um candidato agindo sobre conteúdo
retificado sem saber da retificação é o dano que a imutabilidade do ato existe para evitar.

**Independent Test**: retificar um Edital publicado e abrir a página pública: a retificação aparece
com data e justificativa, e o conteúdo exibido é o vigente.

**Acceptance Scenarios**:

1. **Given** um Edital publicado e depois retificado, **When** alguém abre a página, **Then** vê que
   houve Retificação, em que data, com a justificativa publicada, e o que foi alterado dito em termos
   do Edital.
2. **Given** o mesmo Edital, **When** a página exibe o conteúdo, **Then** o conteúdo é o vigente, e
   está identificado como tal.
3. **Given** cada ato já publicado, **When** alguém quer o documento daquele ato, **Then** o
   documento continua alcançável, com a data em que foi publicado.
4. **Given** um Edital nunca retificado, **When** a página é aberta, **Then** não há seção de
   histórico nem frase dizendo que não houve retificação.

---

### User Story 3 — Entender a vaga sem abrir o PDF (Priority: P1)

Alguém compara duas vagas e quer saber o que vai fazer, por quantas horas e por quanto — informação
que o Edital publicou e a página não mostra. E, quando não há vaga imediata, quer entender que ainda
assim pode se inscrever.

**Why this priority**: completa a tela que já é a mais próxima da decisão, e corrige uma leitura hoje
enganosa ("0 vagas").

**Independent Test**: abrir a página de uma seleção cujos Perfis declaram atribuições, carga horária
e remuneração, e conferir que os três aparecem; abrir um Perfil com zero vagas imediatas e cadastro
reserva, e conferir que a leitura principal é a oferta.

**Acceptance Scenarios**:

1. **Given** um Perfil com atribuições, carga horária e remuneração declaradas, **When** a vaga é
   exibida, **Then** os três aparecem junto dos requisitos.
2. **Given** um Perfil que declarou apenas parte desses campos, **When** a vaga é exibida, **Then**
   só os declarados aparecem, sem rótulo vazio e sem "não informado".
3. **Given** um Perfil com zero vagas imediatas e cadastro reserva declarado, **When** a vaga é
   exibida, **Then** a leitura principal é a oferta de cadastro reserva, o número de vagas imediatas
   continua dito, e o convite de inscrição continua disponível.
4. **Given** alguém sem sessão diante do convite de inscrição, **When** lê o convite, **Then** sabe,
   antes de acioná-lo, que inscrever-se exige identificação.

---

### User Story 4 — Encontrar a oportunidade certa sem ler todas (Priority: P2)

Alguém procura vaga de uma área específica, ou num campus específico, e não quer ler o catálogo
inteiro para descobrir se ela existe.

**Why this priority**: valor real e crescente, mas hoje contornável pela leitura da lista. Depende de
nada da US1–US3 e pode ser entregue depois delas.

**Independent Test**: com o catálogo de demonstração publicado, localizar uma seleção por termo de
busca e por filtro, e conferir a contagem de resultados.

**Acceptance Scenarios**:

1. **Given** o catálogo publicado, **When** alguém busca por um termo, **Then** vê as seleções cujo
   texto público contém o termo, com a contagem do que foi encontrado.
2. **Given** uma busca em curso, **When** alguém aplica um filtro, **Then** os dois se somam, e a
   tela diz quantos resultados restaram e como limpar a consulta.
3. **Given** uma consulta sem nenhum resultado, **When** a tela é exibida, **Then** ela diz o que foi
   procurado e oferece o caminho de volta ao catálogo completo.
4. **Given** uma consulta aplicada, **When** alguém a compartilha pelo endereço ou usa o *voltar* do
   navegador, **Then** encontra a mesma lista.
5. **Given** alguém que abriu uma seleção vinda de uma consulta, **When** volta à lista, **Then**
   a consulta continua aplicada.

---

### User Story 5 — Distinguir o que abriu, o que vai abrir e o que fechou (Priority: P2)

Alguém abre a vitrine e precisa saber, sem interpretar, em que situação está cada seleção — e chegar
ao Edital ou ao resultado das que já fecharam.

**Why this priority**: barato, e corrige um agrupamento que hoje funde três situações que o domínio
já separa.

**Independent Test**: publicar seleções nas quatro situações e conferir que cada uma é anunciada com
sua marca própria.

**Acceptance Scenarios**:

1. **Given** seleções nas quatro situações, **When** a vitrine é exibida, **Then** cada uma traz a
   sua situação como marca explícita, e as futuras não aparecem misturadas às encerradas.
2. **Given** uma seleção com inscrições abertas, **When** o cartão é exibido, **Then** traz a
   data-limite exata e o prazo restante.
3. **Given** uma seleção encerrada, **When** o cartão é exibido, **Then** há caminho visível para
   consultar a seleção, mesmo sem convite de inscrição.
4. **Given** um Edital que não recebe inscrição por este sistema, **When** o cartão é exibido,
   **Then** ele não é anunciado como encerrado, e nenhuma frase de prazo é escrita.

---

### Edge Cases

- **Cronograma com Evento sem término declarado**: o Evento é exibido com o início, e a situação não
  o declara concluído — é o mesmo tratamento que o período de inscrições já recebe.
- **Retificação publicada com vigência futura**: aparece no histórico como ato já publicado, com a
  data em que passa a valer, e o conteúdo da página continua sendo o que vale **hoje**. Publicar e
  entrar em vigor são instantes distintos, e a tela não pode fundi-los — é o caso que o próprio seed
  de demonstração produz.
- **Retificação que altera algo que a página não exibe**: o registro da alteração continua aparecendo
  no histórico; o que a página mostra é o vigente, e não só o que ela renderiza.
- **Muitas retificações**: o histórico continua legível sem esconder a mais recente, que é a que
  interessa a quem chega.
- **Termo de busca que casa com o texto de uma seleção cancelada**: canceladas continuam fora da
  vitrine, e por isso fora dos resultados; o endereço direto continua funcionando.
- **Filtro por perfil ou unidade que não existe no catálogo**: resultado vazio tratado como consulta
  sem resultado, e não como erro.
- **Consulta com termo muito longo, vazio ou só com espaços**: tratada como ausência de busca.
- **Seleção sem Perfil publicado**: o cartão não inventa linha de vagas, como já não inventa hoje.
- **Duas seleções com o mesmo título de processo**: continuam distinguíveis pelo número do Edital e
  pela unidade, que o cartão já mostra.

## Requirements *(mandatory)*

### Functional Requirements

#### Cronograma público

- **FR-125**: A página pública da seleção MUST exibir o cronograma publicado do Edital, na ordem
  publicada, sem exigir identificação.
- **FR-126**: Cada Evento do cronograma MUST ser exibido com o período declarado e com a situação do
  **Evento** — concluído, em curso ou por vir —, e a situação nunca descreve quem lê.
- **FR-127**: O local do Evento MUST ser exibido quando o Edital o declarou, e a linha MUST ser
  omitida quando não declarado.
- **FR-128**: Edital sem cronograma publicado MUST omitir a seção inteira, sem frase de ausência.

#### Histórico normativo público

- **FR-129**: Quando houver mais de um ato publicado, a página pública da seleção MUST exibir todos
  eles — a publicação de abertura e cada Retificação — com a data de publicação de cada um, sem
  exigir identificação.
- **FR-130**: Cada Retificação exibida MUST trazer a justificativa publicada e a identificação do
  que foi alterado, dita em termos do Edital.
- **FR-131**: O conteúdo exibido na página MUST ser o consolidado vigente.
- **FR-131a**: Havendo mais de um ato publicado, o conteúdo exibido MUST estar identificado como
  vigente. Com ato único não há o que contrastar, e o rótulo responderia pergunta que ninguém fez.
- **FR-132**: O documento de cada ato publicado MUST permanecer alcançável, identificado pela data
  em que foi publicado.
- **FR-133**: Edital com um único ato publicado MUST omitir a seção de histórico — o documento
  daquele ato já está na página —, sem frase de negação.

#### A vaga

- **FR-134**: A vaga MUST exibir atribuições, carga horária e remuneração quando declaradas no
  conteúdo publicado, junto dos requisitos já exibidos.
- **FR-135**: Campo do Perfil não declarado MUST ser omitido, sem rótulo vazio e sem "não
  informado".
- **FR-136**: Perfil com cadastro reserva declarado e nenhuma vaga imediata MUST ser lido, na
  leitura principal, como oferta de cadastro reserva; o número de vagas imediatas continua dito, sem
  ser o elemento em destaque.
- **FR-137**: O convite de inscrição MUST anunciar, antes de ser acionado, que inscrever-se exige
  identificação.

#### Descoberta na vitrine

- **FR-138**: A vitrine MUST aceitar busca textual sobre o texto público das seleções — título do
  processo, título e número do Edital, unidade e nomes dos Perfis.
- **FR-139**: A vitrine MUST oferecer filtro por unidade, por situação das inscrições e por Perfil,
  combináveis entre si e com a busca.
- **FR-140**: A vitrine MUST oferecer ordenação por prazo terminando primeiro e pela vigência mais
  recente do conteúdo exibido, sendo a primeira o padrão. Ordena-se pelo instante do que o cartão
  mostra — e não pelo do ato que o produziu, que pode ser anterior à vigência dele.
- **FR-140a**: A ordenação MUST valer dentro de cada grupo quando há agrupamento, e sobre a lista
  inteira quando há consulta.
- **FR-141**: A vitrine MUST informar quantos resultados a consulta produziu — um número só, do
  total encontrado — e MUST oferecer caminho para limpá-la.
- **FR-142**: Consulta sem resultado MUST dizer o que foi procurado e oferecer o caminho de volta ao
  catálogo completo, sem tratar a ausência como erro.
- **FR-143**: A consulta MUST estar inteiramente no endereço, de modo que seja compartilhável e que
  o histórico do navegador a reproduza.
- **FR-144**: Voltar da página da seleção para a vitrine MUST preservar a consulta aplicada.

#### Situação na vitrine

- **FR-145**: Cada cartão MUST anunciar a situação da seleção como marca explícita, entre as quatro
  situações que o domínio distingue: aberta, futura, encerrada e sem inscrição por este sistema.
- **FR-146**: Sem consulta ativa, a vitrine MUST agrupar as seleções pelas quatro situações, sem
  fundir futuras, encerradas e sem inscrição por este sistema num grupo só.
- **FR-146a**: Com consulta ativa, a vitrine MUST apresentar uma lista única ordenada, sem
  cabeçalhos de grupo — a marca de situação de cada cartão (`FR-145`) é o que mantém as quatro
  distinguíveis. Agrupar quatro cabeçalhos sobre um cartão cada é ruído, não organização.
- **FR-147**: Cartão de seleção com inscrições abertas MUST trazer a data-limite exata e o prazo
  restante.
- **FR-148**: Cartão de seleção sem inscrições abertas MUST oferecer caminho visível para consultar
  a seleção.
- **FR-149**: Edital que não recebe inscrição por este sistema MUST NOT ser anunciado como
  encerrado, e nenhuma frase de prazo MUST ser escrita para ele.

#### Alcance

- **FR-150**: Nenhuma tela ou recurso desta feature MUST exigir identificação.
- **FR-151**: Esta feature MUST NOT gravar dado algum: nenhuma tabela nova, nenhuma alteração de
  conteúdo publicado, nenhum registro de navegação.
- **FR-152**: Seleção cancelada MUST permanecer fora da vitrine e dos resultados de consulta, e
  alcançável pelo endereço.

### Requisitos de apresentação

- **UX-016**: A mesma informação MUST ocupar a mesma posição em todos os cartões da vitrine, de modo
  que duas oportunidades sejam comparáveis sem releitura.
- **UX-017**: A consulta — busca, filtros e ordenação — MUST funcionar sem depender de execução de
  script no navegador.
- **UX-018**: As telas MUST permanecer legíveis e operáveis em 375 px de largura, como as demais
  telas do portal.
- **UX-019**: Situação e prazo MUST ser distinguíveis sem depender de cor.

### Key Entities

- **Seleção publicada**: a versão consolidada vigente de um Edital, com o conteúdo normativo que a
  página lê. Já existe; a feature não a altera.
- **Evento do cronograma**: o marco declarado pelo Edital, com período, ordem, descrição e local
  eventual. Já publicado; passa a ser público na tela.
- **Ato publicado**: a publicação de abertura ou uma Retificação, com data e documento próprio. Já
  registrado; passa a ser visível.
- **Retificação**: o ato que altera um Edital publicado, com justificativa e identificação do que
  alterou. Já registrada; passa a ser visível.
- **Consulta da vitrine**: os termos de busca, filtros e ordenação em vigor. Não é entidade
  persistida — vive no endereço (D-002).

## 5. Invariantes observáveis

Verificáveis a qualquer momento, em qualquer estado do catálogo:

1. Nenhuma tela desta feature pede identificação.
2. Nada que a feature exibe foi produzido por ela: cada informação tem origem num ato publicado.
3. O conteúdo exibido é sempre o vigente, e nunca há duas leituras concorrentes do que vale.
4. Nenhuma ausência de dado publicado gera afirmação sobre o Edital.
5. A situação exibida descreve a seleção ou o Evento, nunca a pessoa que lê.
6. Toda consulta é reproduzível pelo endereço.
7. Seleção cancelada não aparece em lista nem em resultado de consulta.

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-040**: Quem abre a página de uma seleção com cronograma publicado identifica a data do
  próximo marco sem abrir o documento e sem se identificar.
- **SC-041**: Todo campo do Perfil publicado que descreve o trabalho — atribuições, carga horária,
  remuneração — aparece na página pública sempre que declarado, e em nenhuma hipótese quando não
  declarado.
- **SC-042**: Diante de um Edital retificado, quem lê a página percebe que houve Retificação,
  quando e por quê, sem baixar documento algum.
- **SC-043**: Num catálogo com o dobro das seleções publicadas hoje, localizar as oportunidades de
  um cargo específico exige no máximo uma busca e um filtro, e a tela informa quantas são.
- **SC-044**: Nenhum recurso desta feature exige identificação, e o percurso inteiro da vitrine à
  vaga é percorrível sem sessão.
- **SC-045**: Uma consulta aplicada, compartilhada pelo endereço, produz a mesma lista para outra
  pessoa.
- **SC-046**: Perfil com cadastro reserva e nenhuma vaga imediata é lido como oportunidade
  disponível por quem percorre a tela, e não como ausência de vaga.
- **SC-047**: Nenhum dado de navegação, clique ou percurso de candidato é registrado por esta
  feature.

### A revisão de leitura, e o que ela mudou de forma

Fechada a implementação, a página da seleção foi lida inteira — não requisito a requisito, mas como
alguém que chega para saber se há vaga. Ela reprovava, e o diagnóstico foi que **cada bloco passava
no seu teste e o conjunto não funcionava**: sete seções de peso idêntico, o histórico ocupando um
terço da altura, e o mesmo layout servindo um certame com inscrições correndo e outro encerrado há
um mês — este último abrindo por vagas que já não se pode pleitear.

O que mudou, e que não altera requisito nenhum:

- **a página se adapta ao momento**: recebendo inscrição, a vaga é a manchete; não recebendo, o
  resultado divulgado ganha destaque, porque é o que traz alguém a um Edital encerrado;
- **cabeçalho de identidade** com a marca da situação, no lugar de quatro blocos soltos;
- **o Cronograma vira coluna lateral** em tela larga: ele é referência, não argumento, e ocupava
  largura total para dizer três datas;
- **os documentos viram uma lista só e datada** — abertura, Retificações e Anexos —, no lugar de
  três seções separadas e de três cartões grandes com o mesmo rótulo de 45 caracteres.

**A última contraria uma decisão da `020`**, que pôs os Anexos em seção própria logo abaixo do
Edital "porque é onde o leitor os procura". A razão dela é preservada — os Anexos continuam junto do
Edital —, e o que muda é que "junto do Edital" passou a significar *na lista de documentos do
Edital*, e não *num bloco de botões de largura total logo abaixo dele*. O teste da `020` que prende
o rótulo do link e a nomeação da seção continua de pé, apontando para a seção nova.

## 7. Out of Scope

Fora deste incremento, e por decisão:

- **Projeção consultável do conteúdo publicado (índice de busca).** Só se justifica quando o
  catálogo crescer para além do que a vitrine carrega de imediato — D-003 nomeia o sinal.
- **Instrumentação de funil, analytics, mapa de calor ou qualquer registro de comportamento.**
  Princípio III; é decisão de proteção de dados, e não subproduto de tela (D-008).
- **Campos que o domínio não tem**: taxa de inscrição, isenção, modalidade presencial/EaD, duração de
  vínculo. Inventá-los aqui seria criar requisito sem evidência.
- **Renomear o convite "Entrar" do cabeçalho.** A escolha atual é deliberada e está registrada onde
  foi feita; o portal é do candidato, e com sessão o cabeçalho já leva às inscrições.
- **Recomendação ou personalização de vagas**, e alerta por e-mail de novas seleções.
- **Redesenho da identidade visual do portal.**
- **Alteração de qualquer fluxo de inscrição.** O convite por vaga, o destino dele e os três estados
  dele permanecem como estão; o que a `024` acrescenta é o aviso de que inscrever-se exige
  identificação (FR-137), e nada mais.

### Achados registrados, e que não são escopo desta feature

- A vitrine carrega o conteúdo publicado de todas as seleções para montar os cartões. É adequado ao
  catálogo atual e é o que D-003 assume; vira problema no volume que D-003 nomeia.
- **A `FR-128` descreve um estado que o canal de publicação não alcança.** `schedule_required` é
  achado **impeditivo**: um Edital sem Evento é recusado na submissão, antes da homologação. O
  guarda continua valendo — conteúdo publicado antes de a regra existir continua legível, e é a ele
  que a `FR-128` atende —, mas o percurso do quickstart não consegue produzir o caso, e o teste que
  o cobre renderiza o template em vez de publicar. Descoberto durante a implementação, em
  2026-09-10.
- Títulos de processo repetidos entre Editais diferentes ("Processo Seletivo Simplificado 2026")
  tornam a lista difícil de varrer. É conteúdo de quem elabora, não defeito de tela: a feature
  garante que número do Edital e unidade continuem distinguindo os dois, e não renomeia nada.

## Assumptions

- O catálogo publicado do Cefor/Ifes fica na ordem de dezenas de seleções simultâneas. É a premissa
  que sustenta D-003, e o incremento a declara para que a revisão futura saiba o que mudou.
- Quem chega ao portal pode nunca ter aberto um Edital antes, e frequentemente lê no celular — é a
  premissa que a base do portal já assume.
- O conteúdo publicado é a única fonte da página, como já é hoje: nenhuma tela desta feature consulta
  tabela de elaboração.
- O registro público de Publicações e Retificações já expõe justificativa, datas e identificação do
  que foi alterado — a feature o renderiza, não o estende.
- O renderizador de cronograma existente serve à página pública sem mudar o que já entrega à área do
  candidato.
- A verificação desta feature é feita por percurso conduzido contra o servidor real, com catálogo
  semeado nas quatro situações e ao menos um Edital retificado.

## 8. Ordem de implementação sugerida

1. **Cronograma público** (US1) — reuso do que existe; entrega valor sozinha.
2. **Campos da vaga e cadastro reserva** (US3) — renderização direta do conteúdo publicado.
3. **Histórico normativo** (US2) — a de maior peso normativo, e a que exige mais tradução de dado
   para linguagem do domínio.
4. **Situação explícita e separação das futuras** (US5) — o domínio já calcula; é redação de tela.
5. **Busca, filtros, ordenação e preservação da consulta** (US4) — a única que acrescenta um eixo
   novo à vitrine.

Cada uma é demonstrável isoladamente, e nenhuma depende da seguinte.

## 9. Gate de conclusão

A feature está pronta quando, num catálogo semeado com seleções nas quatro situações e ao menos um
Edital retificado, um percurso conduzido sem sessão alcança, do começo ao fim:

- localizar uma vaga por busca e filtro, com a contagem correta;
- abrir a seleção e ler cronograma, atribuições, carga horária e remuneração;
- perceber a retificação, sua data e sua justificativa;
- voltar à lista com a consulta preservada;
- alcançar uma seleção encerrada e o documento de cada ato publicado dela.

E quando os sete invariantes da §5 forem verificáveis por teste.
