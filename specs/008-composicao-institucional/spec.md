# Feature Specification: Composição Institucional do Edital

**Feature Branch**: `008-composicao-institucional`

**Created**: 2026-08-30

**Status**: Draft

**Input**: Leitura do documento produzido pelo sistema após a integração da `007`
(`documento2.pdf`), comparado com Editais reais do Cefor, e reconciliação dessa leitura com o
compositor real (`publicacoes/infrastructure/pdf.py`) antes do planejamento.

## A frase que governa esta feature

> **A `008` é a última feature dedicada ao Edital antes de a jornada mudar de ator. Ela muda como o
> conteúdo já homologado se apresenta — não o que ele contém. Uma deficiência encontrada no
> conteúdo ou no domínio não autoriza ampliar a `008` para corrigi-la, salvo se ela impedir
> materializar corretamente dado que já existe.**

Todo requisito abaixo responde a uma pergunta só: *isto aproxima a materialização de um ato
administrativo do Ifes?* O que não responde a ela não pertence a esta spec.

## Contexto

A `007` fechou a camada de conteúdo. O documento gerado já traz Apresentação, Disposições
Preliminares, Requisitos Gerais, Inscrição, Perfis, Etapas, Classificação, Cronograma, Recursos e
Disposições Finais; já não imprime estado interno de Evento, decimal canônico nem UUID no corpo; e
já preserva os parágrafos que a pessoa escreveu. O conteúdo chegou.

**A materialização não.** O documento ainda se lê como relatório técnico bem organizado: a primeira
página é uma sequência de títulos e parágrafos sem cabeçalho institucional reconhecível; as seções
não têm numeração normativa; Perfis e Cronograma são prosa onde deveriam ser quadro e tabela; um
Perfil começa no fim de uma página e continua na seguinte; não há fechamento de autoridade; e o
bloco técnico de integridade — inclusive `Versão do schema: 3` — compete visualmente com o conteúdo
normativo. Os Editais 62 e 73 do Cefor resolvem isso já na primeira página: identificação do órgão,
unidade, ato, título e hierarquia documental reconhecível, e quadros para o que é naturalmente
tabular.

Esta feature é a distância entre as duas coisas, e só ela.

## Reconciliação com o compositor real

*Esta seção existe porque a primeira redação desta spec foi escrita olhando o PDF, e não o código.
Ela produziu requisitos já satisfeitos, requisitos que colidiam com invariantes vigentes e
requisitos cuja pré-condição técnica não existe. As decisões abaixo estão fechadas: o `/plan` as
executa, não as negocia.*

O compositor é artesanal e não tem dependência externa (`publicacoes/infrastructure/pdf.py`). Ele
emite **exclusivamente** operadores de texto (`BT … Tj ET`), quebra linha contando **caracteres**
(`_quebrar`, com um fator médio de largura de `0,52`), pagina uma lista **plana** de linhas
independentes (`Composicao.paginar`) e é uma função pura de `(snapshot, content_hash, modo)`.

Disso decorrem seis decisões, e elas são o núcleo desta spec:

1. **A autoridade signatária é metadado do ato, não conteúdo normativo.** `signatory_name` e
   `signatory_role` vivem em `Publicacao`, não no snapshot. O snapshot **não** ganha autoridade
   signatária para que o PDF possa desenhá-la: ela chega ao compositor como contexto do ato,
   separado do conteúdo, e os dois fluxos de publicação já o têm em mãos no momento em que chamam o
   renderizador. A presença é **determinada pelo modo** (FR-036), não pelo chamador.
2. **Prévia não tem assinatura.** Ela não decorre de uma Publicação. Essa é a segunda — e última —
   diferença admitida entre prévia e publicado.
3. **Sem praça, sem data, sem cadastro de pessoas.** "Vitória (ES), 30 de agosto de 2026" exigiria
   um conceito que o sistema não tem. A V1 materializa o que existe.
4. **Brasão fica fora da V1.** Embutir imagem num PDF artesanal significa XObject, recurso binário
   e compressão — muita mecânica para um ganho que o cabeçalho tipográfico entrega em boa parte.
5. **Métrica de fonte e primitivas gráficas são autorizadas explicitamente.** Não se pode exigir
   centralização, colunas e tabelas de um compositor proibido de medir texto e de desenhar linha.
6. **A paginação evolui de linha para bloco.** Não se pode exigir "Perfil não partido no meio" de
   um paginador que só conhece linhas independentes.

## Princípios desta feature

### P-001 — A fronteira canônica é intransponível

**Formatação humana é responsabilidade exclusiva da materialização. A representação canônica do
snapshot, inclusive decimais, não é alterada pela `008`.** Nenhum requisito desta feature toca
`edital_snapshot`, `SCHEMA_VERSION`, o cálculo do hash, a forma publicada ou a gramática de
endereçamento da Retificação. Este é o mesmo guardrail da `007`, reafirmado porque uma feature
puramente visual é exatamente o lugar onde ele seria abandonado por conveniência.

### P-002 — Existe uma fonte normativa só

O conteúdo homologado. A `008` não cria modelo documental paralelo, não persiste versão textual de
nenhuma apresentação estruturada e não guarda no domínio nada que exista apenas para o PDF.

### P-003 — Sem engine de documentos

Não existe editor visual, tema, template builder, linguagem de template, HTML/CSS configurável,
escolha de fonte, cor personalizável, DOCX nem importação. Existe **um layout institucional V1**.

### P-004 — Capacidade técnica estreita, autorizada nominalmente

Os requisitos visuais desta feature exigem três capacidades que o compositor não tem: medir texto,
desenhar linha e paginar por bloco. As três estão autorizadas em FR-002, FR-003 e FR-004, **e
nenhuma outra está**. Autorizar nominalmente é o que impede tanto a paralisia ("§ diz para não criar
framework, então finjo tabela com espaço") quanto a expansão ("já que vou mexer no paginador…").

### P-005 — Estruturado vira apresentação estruturada

Quando o sistema já entende semanticamente a informação, a materialização pode exibi-la como ela é:
Perfis viram quadro, Cronograma vira tabela, Etapas viram pares rótulo-valor. Isso não cria dado
novo nem persiste apresentação.

### P-006 — Resultado visual a cada entrega

Cada entrega termina com um PDF real gerado e inspecionado. **Uma entrega não se considera concluída
porque a suíte ficou verde**, e nenhuma entrega pode ser apenas preparatória: não existe "a entrega 1
cria a abstração e a mudança visual vem na 2".

## Invariantes de não regressão

*Estes comportamentos já existem e têm teste. Não são requisitos da `008` — são o que ela não pode
quebrar. Estavam na primeira redação como requisitos novos, o que teria feito o `/plan` reespecificar
código pronto.*

A `008` DEVE preservar:

- os parágrafos digitados pela pessoa, na forma que a `006.1` estabeleceu;
- a marca de prévia e a ausência de qualquer afirmação de integridade na prévia;
- o compositor único, parametrizado por modo, para prévia e publicado;
- a identificação do Edital e a paginação `Página N de M` no rodapé de toda página;
- o SHA-256 abreviado no rodapé;
- a ausência de identificador técnico no corpo normativo;
- a omissão de rótulo cujo dado não existe — inclusive ampla concorrência sem percentual;
- o determinismo da composição e a acentuação do português;
- a imutabilidade do que já foi publicado: documentos já emitidos conservam seus bytes e seu hash de
  documento, a composição nova vale para publicações novas e **nenhuma rematerialização retroativa é
  executada**. *Publicação é imutável; regerar documento publicado seria reescrever ato praticado.
  Este item estava na primeira redação como requisito novo; é invariante, e está aqui pelo mesmo
  critério dos demais.*

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O documento se identifica como ato institucional (Priority: P1)

Quem abre o documento reconhece, na primeira página e sem ler o corpo, qual instituição praticou o
ato, qual unidade responde por ele, que ato é esse e sobre o que ele dispõe. E, percorrendo o
documento, encontra uma estrutura normativa numerada, não uma sequência de títulos soltos.

**Why this priority**: é o maior ganho por hora gasta e o que separa "relatório" de "Edital" à
primeira vista. É também a entrega que carrega a única pré-condição técnica das demais — a métrica
de fonte —, e por isso vem primeiro mesmo tendo um requisito de aparência.

**Independent Test**: gerar o documento do cenário-base e comparar a primeira página com a do Edital
62 do Cefor; conferir que o sumário implícito das seções é numerado e contínuo.

**Acceptance Scenarios**:

1. **Given** um Edital homologado, **When** abro a primeira página, **Then** leio o órgão, a
   instituição, a unidade responsável, o ato com sua numeração institucional, o Processo Seletivo e
   o título do Edital, em hierarquia decrescente de destaque.
2. **Given** o mesmo documento, **When** percorro as seções, **Then** cada uma é numerada, e a
   numeração é contínua de 1 até a última seção materializada.
3. **Given** um Edital sem Etapas de Avaliação, cuja seção correspondente não é materializada,
   **When** leio a numeração, **Then** ela não tem lacuna.
4. **Given** o texto de uma seção, **When** consulto o conteúdo homologado, **Then** o número não
   está lá: ele é atribuído na materialização.

---

### User Story 2 - O Perfil de Vaga se lê como quadro de vaga (Priority: P1)

Quem procura uma vaga encontra cada Perfil como um bloco visualmente delimitado, com a identificação
em disposição tabular, e não como uma sequência indiferenciada de linhas `rótulo: valor`. E nenhum
Perfil pequeno aparece partido entre duas páginas.

**Why this priority**: depois do cabeçalho, é onde o documento mais se afasta de um Edital real — e
é a informação que o candidato de fato procura. É também a entrega que precisa da paginação por
bloco, e por isso a traz.

**Independent Test**: gerar um cenário com dois Perfis dimensionado para que o segundo não caiba no
espaço restante da página, e verificar que ele passa inteiro para a página seguinte em vez de
começar no rodapé. *A referência versionada tem um Perfil só e não exibe a quebra; o cenário de dois
Perfis é montado para a demonstração desta entrega, e o comportamento defeituoso foi observado no
`documento2.pdf`.*

**Acceptance Scenarios**:

1. **Given** um Edital com dois Perfis, **When** abro o documento, **Then** cada Perfil é um bloco
   delimitado, com código, denominação, localidade, vagas e cadastro reserva em disposição tabular.
2. **Given** um Perfil que não cabe no espaço restante da página mas cabe inteiro na seguinte,
   **When** o documento é composto, **Then** ele é movido integralmente.
3. **Given** um Perfil maior que uma página, **When** o documento é composto, **Then** a quebra
   ocorre entre sub-blocos — identificação, descrição, atribuições, requisitos, modalidades.
4. **Given** um sub-bloco que sozinho não cabe em uma página inteira, **When** o documento é
   composto, **Then** a quebra desce para dentro dele, por parágrafo, item ou linha de tabela, e a
   composição conclui.
5. **Given** uma modalidade de ampla concorrência sem percentual, **When** leio o quadro de
   modalidades, **Then** não encontro célula inventada nem frase tecnicamente estranha.

---

### User Story 3 - Cronograma e Etapas se leem como informação estruturada (Priority: P1)

Quem precisa saber quando e como concorrer encontra o Cronograma em tabela e as Etapas com caráter,
peso e nota mínima em pares rótulo-valor — não em prosa com ponto e vírgula.

**Why this priority**: é informação naturalmente tabular apresentada como parágrafo, e é o que o
Edital 73 resolve com quadro. Custo baixo depois que a métrica de fonte e as primitivas existem.

**Independent Test**: gerar o cenário-base e conferir que os três Eventos aparecem em uma tabela com
início e término, e que a Etapa exibe caráter, peso e nota mínima sem a frase
`caráter: …; peso: …; nota mínima: …`.

**Acceptance Scenarios**:

1. **Given** um Cronograma com três Eventos, **When** leio a seção, **Then** encontro uma tabela com
   ordem, evento, início e término.
2. **Given** um Evento pontual sem término, **When** leio sua linha, **Then** o término está
   explicitamente ausente e nenhuma data falsa é apresentada.
3. **Given** uma tabela que atravessa a quebra de página, **When** leio a página seguinte, **Then**
   o cabeçalho da tabela está repetido, e ele nunca aparece isolado no fim da página anterior.
4. **Given** uma Etapa com peso e nota mínima, **When** leio a subseção, **Then** os valores estão
   em pares rótulo-valor alinhados, e a data continua vindo do Evento vinculado.

---

### User Story 4 - O documento se lê sem acidentes editoriais (Priority: P2)

Quem lê o documento inteiro não encontra título órfão no rodapé, linha longa demais, espaço vazio
acidental nem bloco colado ao seguinte sem distinção.

**Why this priority**: é refinamento, e só faz sentido depois que os blocos das três primeiras
entregas existem. Mas é o que distingue "estruturado" de "bem composto", e é barato ao final.

**Independent Test**: percorrer todas as páginas do cenário-base e do cenário longo procurando
título sozinho no pé de página e espaço vertical sem causa.

**Acceptance Scenarios**:

1. **Given** um título de seção que cairia no fim da página, **When** o documento é composto,
   **Then** ele desce junto com ao menos a primeira parte do conteúdo da seção.
2. **Given** um documento composto, **When** comparo o espaço vertical antes de uma seção, antes de
   um bloco e antes de um parágrafo, **Then** o primeiro é maior que o segundo, e o segundo maior
   que o terceiro.
3. **Given** um parágrafo longo, **When** leio a linha, **Then** ela não estoura a margem nem fica
   curta demais, porque a quebra usa a largura real do texto.

---

### User Story 5 - O documento termina como ato, não como relatório (Priority: P1)

Quem chega ao fim do documento publicado encontra a autoridade que praticou o ato, e depois — de
forma discreta — o bloco de verificação de integridade. Não encontra `Versão do schema: 3` como se
fosse seção normativa.

**Why this priority**: é o que fecha a impressão de ato administrativo, e é a entrega que carrega a
única mudança de contrato do compositor. Vem por último porque depende de todo o resto estar
composto para que o fechamento tenha onde ficar.

**Independent Test**: publicar um Edital escolhendo a autoridade signatária e conferir que ela
aparece ao final do documento; gerar a prévia do mesmo Edital e conferir que não aparece.

**Acceptance Scenarios**:

1. **Given** uma Publicação com autoridade signatária escolhida, **When** leio o fim do documento,
   **Then** encontro o nome e o cargo registrados naquele ato.
2. **Given** uma tentativa de compor documento publicado sem autoridade, **When** o compositor é
   chamado, **Then** a composição é recusada.
3. **Given** a prévia do mesmo Edital, **When** leio o fim do documento, **Then** não encontro bloco
   de autoridade, e a única marca distintiva continua sendo a de prévia.
4. **Given** o documento publicado, **When** leio o bloco de verificação, **Then** ele está após a
   assinatura, é tipograficamente discreto e contém o que o mecanismo exige — sem que a versão do
   schema figure como seção do Edital.
5. **Given** o mesmo snapshot e a mesma autoridade, **When** o documento é composto duas vezes,
   **Then** os bytes são idênticos.

---

### Edge Cases

- **Seção materializada vazia.** Uma seção gerada cuja coleção está vazia continua não sendo
  materializada, e a numeração é atribuída depois dessa supressão (FR-012).
- **Perfil maior que uma página inteira.** A quebra desce a cascata de FR-022 até a primeira
  alternativa exequível, e o título do Perfil nunca fica sozinho (FR-023).
- **Sub-bloco maior que uma página inteira.** Atribuições, descrição, lista de requisitos ou tabela
  de modalidades que não caibam sozinhas em uma página quebram internamente, por parágrafo, item ou
  linha (FR-022, alternativas 2 e 3). Nenhuma configuração de conteúdo pode tornar a composição
  impossível.
- **Tabela maior que uma página.** O cabeçalho se repete na continuação e nunca fica órfão (FR-027).
- **Texto mais largo que a coluna da tabela.** A célula quebra em mais de uma linha; a linha da
  tabela cresce; a coluna não estoura a margem.
- **Autoridade cujo nome registrado é uma designação de cargo.** O documento imprime o que a
  Publicação registrou, sem inventar nome próprio (FR-034 e Assumptions).
- **Prévia de Edital ainda incompleto.** Continua compondo o que existe, sem assinatura e sem
  afirmação de integridade.
- **Publicação já existente.** Conserva seus bytes e seu `document_hash`; a composição nova vale
  para publicações novas (invariante de não regressão).

## Requirements *(mandatory)*

### Capacidades técnicas autorizadas

*Este bloco declara **resultados e limites**, não desenho. Ele existe porque a diretriz "não crie
framework" — correta — precisa de um limite escrito para não virar proibição de fazer o trabalho, e
porque um requisito visual sem limite declarado é aberto por omissão.*

*As decisões técnicas que fecham cada limite — como medir texto, como a composição representa um
fio, como o paginador reconhece um bloco — **pertencem ao `research.md`/`plan.md`**, e o `/plan` DEVE
registrá-las lá com a alternativa considerada e a razão da escolha. O que aparece abaixo em itálico
é a evidência que motivou o limite, não a solução.*

- **FR-001**: **Formatação humana é responsabilidade exclusiva da materialização. A representação
  canônica do snapshot, inclusive decimais, não é alterada pela `008`.** Nenhum requisito desta
  feature altera `edital_snapshot`, `SCHEMA_VERSION`, o cálculo do hash, a forma publicada ou o
  endereçamento da Retificação.
- **FR-002**: A materialização DEVE posicionar texto pela largura real que ele ocupa, e não por
  estimativa: linha centralizada fica centralizada, coluna alinhada fica alinhada e nenhuma linha
  estoura a margem. Esta capacidade é limitada ao necessário para esta feature — **sem hifenização,
  sem justificação, sem fonte nova e sem fonte embutida**; as fontes continuam sendo as duas que o
  documento já usa. *A quebra atual conta caracteres e assume um fator médio de largura de 0,52
  (`_quebrar`), o que é conservador para refluxo e inservível para centralizar ou alinhar coluna.
  Sem esta autorização, os requisitos de cabeçalho e de tabela seriam cumpridos com espaço em
  branco, que é o defeito que esta feature existe para corrigir.*
- **FR-003**: A materialização DEVE poder delimitar visualmente um bloco e separar as colunas de
  uma tabela. O vocabulário visual do documento está limitado a **texto, fio e contorno**: ficam
  fora ícone, sombra, cartão, gradiente, imagem, fundo e paleta — o documento é preto sobre branco.
  Essa capacidade NÃO DEVE ser generalizada para outros tipos de documento nem resultar em framework
  de layout. *Hoje a composição só sabe escrever texto; quadro e tabela são impossíveis sem isto.*
- **FR-004**: A paginação DEVE decidir onde quebrar considerando o conteúdo como blocos com
  fronteiras conhecidas, e não como linhas independentes. **Somente** as regras de FR-021, FR-022,
  FR-023, FR-027 e FR-031 justificam essa capacidade, e nenhum algoritmo geral de composição
  tipográfica DEVE ser construído. *Hoje a paginação percorre uma lista plana de linhas, e por isso
  "não partir o Perfil" e "não deixar título órfão" são inexprimíveis.*
- **FR-005**: Nenhuma outra capacidade nova é autorizada. O mecanismo de geração do documento NÃO
  DEVE ser substituído e nenhuma dependência de renderização DEVE ser introduzida, salvo impedimento
  concreto e demonstrado para cumprir um requisito desta spec — caso em que o impedimento se
  registra no `research.md` antes de a substituição começar.

### Identidade institucional e hierarquia (US1)

- **FR-006**: A primeira página DEVE abrir com cabeçalho institucional tipográfico composto por
  `MINISTÉRIO DA EDUCAÇÃO`, `INSTITUTO FEDERAL DO ESPÍRITO SANTO` e a denominação da unidade
  responsável, seguidos do ato, do Processo Seletivo e do título do Edital. *Órgão, instituição e
  unidade são constantes do compositor — a unidade já é hoje, escrita em linha única. Ato, Processo
  e título vêm do snapshot, que desde a `007` carrega `processoCode` e `processoTitle`.*
- **FR-007**: O ato — `EDITAL Nº <número>/<ano>` — DEVE ser o elemento de maior destaque
  tipográfico da primeira página.
- **FR-008**: O título/objeto do Edital DEVE aparecer imediatamente associado ao ato, e a descrição
  curta NÃO DEVE competir tipograficamente com ele.
- **FR-009**: Brasão, logotipo e qualquer elemento gráfico de identidade visual ficam **fora da V1**.
  Nenhuma imagem é embutida no documento, nenhum recurso binário é acrescentado ao repositório e
  nenhum sistema de branding é criado. *Embutir imagem exigiria XObject, compressão e recurso
  binário determinístico num compositor que hoje só escreve texto; o cabeçalho tipográfico entrega a
  maior parte do reconhecimento institucional a uma fração do custo. Se a diferença continuar
  incomodando depois desta feature, ela se trata especificamente.*
- **FR-010**: A materialização DEVE definir apenas os níveis tipográficos necessários:
  identificação institucional, título do ato, título de seção, subseção/bloco, corpo e
  nota/metadado. Nenhum design system de documentos é criado.
- **FR-011**: As seções normativas DEVEM ser numeradas na materialização, na ordem institucional já
  definida pelo conteúdo publicado — `1. APRESENTAÇÃO`, `2. DAS DISPOSIÇÕES PRELIMINARES`, e assim
  por diante até a última.
- **FR-012**: A numeração DEVE ser atribuída **depois** de determinadas quais seções serão
  efetivamente materializadas. *O compositor já suprime seção gerada cuja coleção está vazia; numerar
  antes da supressão produziria `5.`, `7.`, `8.` num Edital sem Etapas — um defeito que só apareceria
  em produção, no Edital que não tem tudo.*
- **FR-013**: A numeração NÃO DEVE ser persistida como parte do texto da seção. Alterar a ordem ou o
  catálogo no futuro DEVE produzir numeração coerente sem edição de conteúdo.
- **FR-014**: Subseções — Etapas de Avaliação, e Perfis quando couber — DEVEM ser numeradas a partir
  do número da seção-mãe (`6.1`, `6.2`), sob a mesma regra de FR-012.

### Perfil de Vaga como quadro (US2)

- **FR-015**: Cada Perfil DEVE ser materializado como bloco visualmente delimitado, distinguível do
  Perfil seguinte sem que o leitor precise reler.
- **FR-016**: A identificação do Perfil — código, denominação, localidade, vagas imediatas e
  cadastro reserva — DEVE usar disposição tabular curta, e não uma sequência de linhas
  `rótulo: valor`.
- **FR-017**: NÃO DEVE ser criada uma tabela única contendo todos os campos do Perfil. Descrição,
  atribuições, requisitos e modalidades permanecem blocos próprios.
- **FR-018**: Requisitos permanecem em lista.
- **FR-019**: Modalidades de concorrência DEVEM ser apresentadas em tabela simples com modalidade,
  percentual e fundamento. Versão e vigência da Regra Normativa, quando existirem, DEVEM permanecer
  no documento — em coluna ou em linha secundária —, e a frase técnica atual
  `Regra Normativa — fundamento: …; versão: …; percentual: …` deixa de ser composta. *Tabular não
  pode virar perder: o estado atual imprime esses dois campos, e a composição nova os mantém.*
- **FR-020**: Nenhuma célula DEVE ser preenchida com informação inexistente. Modalidade sem
  percentual apresenta a célula vazia ou o traço de ausência já usado no documento, nunca um valor
  construído nem uma frase técnica.
- **FR-021**: Um Perfil que não couber no espaço restante da página, mas couber inteiro na página
  seguinte, DEVE ser movido integralmente.
- **FR-022**: Um Perfil grande demais para uma página DEVE quebrar segundo esta cascata, na ordem,
  parando na primeira alternativa exequível:
  1. entre seus sub-blocos — identificação, descrição, atribuições, requisitos, modalidades —,
     mantendo cada sub-bloco inteiro;
  2. quando um sub-bloco isolado não couber em uma página inteira, dentro dele, em suas unidades
     internas seguras: parágrafo para descrição e atribuições, item para requisitos, linha para a
     tabela de modalidades;
  3. quando uma unidade interna isolada não couber em uma página inteira, entre linhas dessa
     unidade.
  *A primeira redação exigia "nenhum sub-bloco partido" sem ressalva, o que é inexequível: um campo
  de texto livre não tem limite de tamanho, e atribuições de três páginas tornariam a regra
  impossível de cumprir. A cascata preserva a intenção — quebrar no lugar menos ruim disponível — e
  termina sempre em uma alternativa que existe.*
- **FR-023**: O título de um Perfil NÃO DEVE ficar isolado no fim de uma página.

### Cronograma e Etapas (US3)

- **FR-024**: O Cronograma DEVE ser apresentado em tabela, com ordem, evento, início e término.
- **FR-025**: Evento pontual NÃO DEVE apresentar término. A ausência é apresentada como ausência.
- **FR-026**: A descrição do Evento PODE permanecer junto do evento quando curta, ou em linha
  secundária quando longa.
- **FR-027**: O cabeçalho de uma tabela NÃO DEVE ser separado de sua primeira linha, e DEVE ser
  repetido quando a tabela atravessar a quebra de página. *Com FR-004 isso deixa de ser custoso, e
  por isso a spec o exige em vez de deixá-lo como evolução posterior.*
- **FR-028**: As Etapas de Avaliação DEVEM apresentar caráter, peso e nota mínima em pares
  rótulo-valor alinhados, substituindo a frase corrida
  `caráter: …; peso: …; nota mínima: …`. Cada um continua omitido quando não existe.
- **FR-029**: A referência da Etapa ao Cronograma continua derivada do vínculo existente. Datas NÃO
  DEVEM ser duplicadas no domínio nem no snapshot.

### Tipografia, espaçamento e paginação (US4)

- **FR-030**: O texto normativo DEVE ter largura de linha adequada, entrelinha consistente,
  distância previsível entre parágrafos e alinhamento coerente com documento institucional.
- **FR-031**: Um título de seção NÃO DEVE terminar sozinho no rodapé; ele desce junto de ao menos
  parte do primeiro conteúdo da seção. A regra vale igualmente para subtítulos de Perfil e de Etapa.
- **FR-032**: O espaçamento DEVE distinguir seção nova, bloco dentro da seção, parágrafo e tabela.
  O objetivo é espaço semântico, não compactação.
- **FR-033**: A quebra de linha DEVE passar a usar a largura real do texto (FR-002), substituindo a
  contagem de caracteres.

### Autoridade e integridade (US5)

- **FR-034**: Após o conteúdo normativo, o documento **publicado** DEVE exibir bloco de autoridade
  signatária com o nome e o cargo **registrados na própria Publicação**, sem consulta a catálogo e
  sem transformação. *O que a Publicação registrou é o que o ato afirma; o catálogo é a origem da
  escolha, não a fonte de verdade do que foi assinado.*
- **FR-035**: A autoridade signatária NÃO DEVE entrar no snapshot. Ela DEVE chegar ao compositor
  como **contexto do ato, explícito e separado do conteúdo normativo**. O corpo normativo continua
  sendo função pura do snapshot; o bloco de autoridade é o único elemento derivado de metadado do
  ato. *Os dois fluxos de publicação — o do Edital (`publicacoes/application/publish_edital.py`) e o
  da Retificação (`publicacoes/application/retificacoes.py`) — já têm a autoridade em mãos no
  momento em que chamam o renderizador; nenhum deles precisa de consulta nova.*
- **FR-036**: A presença da autoridade é **determinada pelo modo**, e não pelo chamador:
  - em modo publicado ela é **obrigatória**, e compor sem ela DEVE ser recusado;
  - em modo prévia ela é **proibida**, e ainda que seja oferecida NÃO DEVE ser composta.

  *Este é o mesmo desenho que a `007` deu ao hash: a garantia não pode depender de o chamador
  lembrar. A primeira redação chamava o contexto de "opcional" e admitia um publicado sem
  autoridade, o que tornava possível emitir um ato administrativo sem quem o praticou — e a
  opcionalidade do parâmetro na interface interna não é a mesma coisa que opcionalidade da
  informação no documento.*
- **FR-037**: O bloco de autoridade NÃO DEVE conter praça nem data. *Praça não existe no sistema, e
  a data do ato não é conteúdo normativo. Introduzir qualquer um dos dois para poder escrever a
  linha "Vitória (ES), 30 de agosto de 2026" seria criar conceito por motivo tipográfico.*
- **FR-038**: NÃO DEVEM ser criados assinatura digital, imagem de assinatura, certificado,
  ICP-Brasil, gov.br, QR code nem carimbo eletrônico. Esta é a representação documental da
  autoridade que já praticou o ato, e nada além.
- **FR-039**: A declaração de integridade DEVE ser deslocada para bloco discreto **após** o bloco de
  autoridade, tipograficamente subordinado ao conteúdo normativo, sem perder nenhuma informação
  necessária ao mecanismo. Nenhuma página nova e nenhum serviço novo são criados para isso.
- **FR-040**: `Versão do schema` NÃO DEVE aparecer como seção normativa do Edital. Ela permanece no
  mecanismo e no snapshot; o que muda é o que se imprime como corpo do ato.
- **FR-041**: O SHA-256 completo permanece no bloco de verificação e o abreviado permanece no
  rodapé. A afirmação de derivação da versão homologada permanece.

### Prévia e publicado

- **FR-042**: Prévia e publicado DEVEM utilizar o mesmo compositor e a mesma composição normativa.
  As diferenças admitidas são **exclusivamente** a identificação de prévia e os metadados próprios
  do ato de Publicação — autoridade signatária e declaração de integridade. Nenhuma regra visual
  DEVE existir só na prévia.
- **FR-043**: A marca de prévia NÃO DEVE alterar as quebras de página do conteúdo normativo: para
  o mesmo snapshot, o conjunto de quebras do corpo normativo é o mesmo na prévia e no publicado.
  *"Não alterar significativamente" era inverificável e deixava a decisão para quem implementa. O
  corpo normativo é a parte comum aos dois modos, e por isso é sobre ele que a igualdade se afirma —
  a assinatura e o bloco de verificação existem só no publicado e naturalmente ocupam espaço a
  mais, depois do conteúdo.*

### Retificação

- **FR-044**: Todo documento consolidado produzido após Retificação DEVE usar exatamente a mesma
  composição institucional definida nesta feature, e recebe a autoridade signatária da própria
  Publicação da Retificação. Nenhum caminho visual paralelo é criado.

### Fixture documental

- **FR-045**: Cada entrega que alterar intencionalmente a composição DEVE regenerar a fixture
  contratual do documento publicado pelo script existente, **no mesmo commit** da alteração do
  compositor, com o diff do documento gerado revisado como parte da implementação. Alterar a fixture
  sem alteração intencional da composição continua sendo erro. A partir de FR-036, o gerador da
  fixture e os testes do modo publicado DEVEM passar uma **autoridade fixa e versionada** ao lado do
  snapshot de referência, pela mesma razão que o snapshot é versionado: sem ela a fixture deixaria
  de ser reproduzível. *A fixture compara bytes e existe para acusar mudança não intencional; sem
  esta regra, toda entrega desta feature pareceria estar apagando a evidência que a fixture guarda.*

### Key Entities

Nenhuma. A `008` não cria, altera nem remove entidade, campo, estado, transição, migration ou
permissão. Ela altera exclusivamente a materialização documental e a assinatura interna do
compositor, que ganha um parâmetro de contexto do ato.

## Success Criteria *(mandatory)*

- **SC-001**: A primeira página apresenta, nesta ordem e antes de qualquer conteúdo normativo,
  órgão, instituição, unidade, ato, Processo e título; o ato tem o maior corpo tipográfico da
  página; e a descrição tem corpo menor que o do título.
- **SC-002**: Todas as seções normativas materializadas são numeradas, e a numeração é contínua —
  inclusive num Edital em que alguma seção gerada não é materializada.
- **SC-003**: Nenhum número de seção aparece no conteúdo homologado; alterar a ordem produz
  numeração coerente sem editar texto.
- **SC-004**: Cada Perfil é um bloco delimitado com identificação tabular, e não uma sequência
  indiferenciada de linhas.
- **SC-005**: Um Perfil que caberia inteiro na página seguinte não aparece partido, e nenhum título
  de Perfil aparece isolado no fim de página.
- **SC-006**: O Cronograma é uma tabela; Evento pontual não exibe término; o cabeçalho da tabela se
  repete na continuação e nunca fica órfão.
- **SC-007**: As Etapas exibem caráter, peso e nota mínima em pares rótulo-valor, e a data continua
  vindo do Evento vinculado.
- **SC-008**: Nenhum título de seção, de Perfil ou de Etapa fica sem conteúdo abaixo de si na
  página, e o espaço vertical antes de uma seção é maior que o de um bloco, que por sua vez é maior
  que o de um parágrafo.
- **SC-009**: O documento publicado termina com a autoridade signatária registrada naquela
  Publicação, sem praça, sem data e sem nome inventado.
- **SC-010**: A prévia não exibe autoridade nem afirmação de integridade, e continua identificada
  como prévia — e essas são as **únicas** diferenças em relação ao publicado.
- **SC-011**: `Versão do schema` não figura como seção normativa; o bloco de verificação está após a
  assinatura e é tipograficamente discreto; o SHA-256 completo e o abreviado permanecem onde o
  mecanismo os exige.
- **SC-012**: Nenhuma alteração de `edital_snapshot`, `SCHEMA_VERSION`, forma canônica, cálculo de
  hash ou gramática de endereçamento é necessária para cumprir a feature.
- **SC-013**: O mesmo snapshot com a mesma autoridade produz os mesmos bytes em modo publicado; o
  mesmo snapshot produz os mesmos bytes em modo prévia; compor um publicado sem autoridade é
  recusado; e o corpo normativo continua composto sem consulta ao banco.
- **SC-014**: O documento consolidado de uma Retificação apresenta a mesma composição institucional
  do documento de Publicação.
- **SC-015**: A fixture contratual foi regenerada em cada entrega que mudou a composição, sempre no
  commit da mudança, com autoridade fixa versionada ao lado do snapshot de referência, e os
  documentos publicados anteriores conservam seus bytes.

## Demonstração visual obrigatória

*Este é o critério emblemático da feature, e é uma demonstração — não uma métrica. A qualidade
editorial de um documento não se afirma por asserção automatizada, e tentar fazê-lo produziria teste
frágil e caro.*

Ao final de cada entrega, gerar o documento do **cenário-base** — reproduzível pela seed — e
inspecionar as páginas, comparando com `referencias/estado-inicial-apos-007.pdf`. Ao final da feature, o
percurso completo deve ler-se como documento institucional coerente:

> cabeçalho institucional → ato → conteúdo numerado → Perfis estruturados → Etapas → Cronograma
> tabular → paginação coerente → autoridade → integridade discreta

### Rubrica de inspeção

A inspeção NÃO é impressão geral: cada item abaixo é observável e responde sim ou não. Uma entrega
não é aceita com item da sua faixa respondido "não".

| # | Observável na página | Faixa |
|---|---|---|
| R-01 | Órgão, instituição e unidade abrem a página 1, antes de qualquer conteúdo normativo | 1 |
| R-02 | O ato é o texto de maior corpo da página 1 | 1 |
| R-03 | Toda seção exibe número, e a sequência vai de 1 até a última sem lacuna | 1 |
| R-04 | Cada Perfil está delimitado por fio e separado do seguinte | 2 |
| R-05 | Nenhum Perfil que caberia inteiro na página seguinte aparece partido | 2 |
| R-06 | Nenhum título — de seção, Perfil ou Etapa — fecha uma página sem conteúdo abaixo | 2, 4 |
| R-07 | O Cronograma é uma grade com colunas alinhadas; nenhuma coluna estoura a margem | 3 |
| R-08 | Evento sem término exibe ausência, não data | 3 |
| R-09 | Cabeçalho de tabela repetido na continuação e nunca isolado no fim da página | 3 |
| R-10 | Caráter, peso e nota mínima aparecem como pares rótulo-valor alinhados | 3 |
| R-11 | Nenhuma linha estoura a margem e nenhum espaço vertical existe sem causa | 4 |
| R-12 | O publicado termina com autoridade e, depois dela, o bloco de verificação discreto | 5 |
| R-13 | `Versão do schema` não aparece como seção do Edital | 5 |
| R-14 | A prévia do mesmo Edital não exibe autoridade nem integridade | 5 |

### Referências visuais

A comparação com Editais reais é parte da demonstração e, para ser repetível, precisa de referência
disponível no repositório.

O **estado inicial** está versionado em `referencias/estado-inicial-apos-007.pdf` — o documento que
o sistema produz hoje, depois da `007`. O **alvo** — ao menos um Edital oficial do Cefor — DEVE ser
versionado no mesmo diretório **antes da entrega 1**, que ele bloqueia. Não sendo possível
versioná-lo, ele DEVE ser identificado por fonte, número, ano e página, com a lista das
características observáveis que se está comparando.

*Sem isso a demonstração é reproduzível apenas por quem já viu os documentos, e o critério
emblemático da feature vira memória.*

**Sem teste pixel-perfect e sem screenshot test.** Os testes automatizados verificam propriedades
semânticas: o conteúdo está presente, as páginas existem e são numeradas, o hash é preservado,
nenhum texto desapareceu, o compositor concluiu, a numeração é contínua, o bloco de autoridade
existe no publicado e não existe na prévia.

## Assumptions

- **O nome registrado na Publicação pode ser uma designação de cargo.** O catálogo declarado hoje
  traz entradas como `Reitora do Ifes — Reitora`, e é isso que a V1 materializa. Corrigir a redação
  do catálogo é trabalho editorial, e está **fora** desta feature: a `008` não inventa nome próprio
  nem cria cadastro de pessoas.
- A unidade responsável continua sendo constante do compositor, como já é hoje. Nenhuma unidade
  configurável por Processo é introduzida.
- O cenário-base de demonstração é reproduzível pela seed; nenhum dado publicado precisa ser
  preservado para a feature.
- Papéis, permissões e fluxos existentes bastam. Nenhuma tela nova é criada.
- A suíte existente do compositor descreve o comportamento a preservar; os testes que hoje afirmam a
  forma antiga da apresentação são atualizados junto da mudança que os torna falsos, e os que
  afirmam invariante — determinismo, acentuação, ausência de UUID, autossuficiência do corpo
  normativo — permanecem.

## Out of Scope

Desta feature inteira, e sem exceção:

- **Edital**: anexos, editor WYSIWYG, Markdown configurável, HTML livre, subseção arbitrária, tipo
  novo de seção, template, clone, biblioteca de documentos, reordenação livre;
- **Exportação**: DOCX, ODT, LaTeX, HTML público alternativo;
- **Assinatura**: certificado, ICP-Brasil, gov.br, QR code, carimbo eletrônico, imagem de
  assinatura;
- **Identidade visual**: brasão, logotipo, tema, branding por campus, editor de cabeçalho, escolha
  de fonte, personalização de cor;
- **Domínio**: Processo, estados, homologação, publicação, Retificação, snapshot, hash, Perfis,
  Cronograma, Etapas, modalidades, conteúdo textual, catálogo de seções, regras de submissão;
- **Produto**: candidato, inscrição, documentos do candidato, comissão, avaliação.

E, literalmente:

> **Esta feature melhora a apresentação do conteúdo que já existe. Uma deficiência encontrada no
> conteúdo ou no domínio não autoriza ampliar a `008` para corrigi-la, salvo se ela impedir
> materializar corretamente dado que já existe.**

## Ordem de entrega

Cada linha é uma diferença visível no PDF. A condição de merge é o documento gerado e inspecionado,
não a contagem de testes.

| Entrega | O que muda visivelmente | Capacidade que carrega |
|---|---|---|
| 1 (US1) | Cabeçalho institucional, hierarquia do ato e seções numeradas | Métrica de fonte (FR-002) |
| 2 (US2) | Perfis em quadro e Perfil que não parte no meio | Primitivas gráficas (FR-003) e paginação por bloco (FR-004) |
| 3 (US3) | Cronograma em tabela e Etapas em pares rótulo-valor | — |
| 4 (US4) | Órfãos, quebras, espaçamento e refinamento tipográfico | — |
| 5 (US5) | Autoridade signatária e integridade discreta ao final | Contexto de publicação no compositor (FR-035) |

**A entrega 1 precisa mudar visivelmente a primeira página.** Não é aceitável uma primeira entrega
que introduza capacidade sem resultado visual — a métrica de fonte viaja *dentro* do cabeçalho
centralizado, não antes dele.

## Instruções para o `/plan`

**Objetivo: chegar à implementação pelo menor caminho.** O compositor atual funciona; esta feature o
evolui incrementalmente. Havendo uma solução simples específica para o Edital e uma solução genérica
para documentos futuros, usar a específica.

Seis avisos derivados do que esta spec verificou no código:

1. **As três capacidades de FR-002, FR-003 e FR-004 são autorizadas e necessárias.** Não as evite
   por causa de "não crie framework": tabela fingida com espaço, cabeçalho centralizado por
   contagem de caractere e Perfil partido no meio são o resultado de evitá-las. O que continua
   proibido é generalizar para outros tipos de documento, criar camada de abstração para documento
   futuro e construir design system.
2. **A assinatura entra por parâmetro, nunca pelo snapshot.** Qualquer proposta que acrescente
   autoridade signatária a `edital_snapshot` viola P-001, FR-001 e FR-035 — e quebraria hash,
   reprodutibilidade e endereçamento de Retificação de uma vez. Os dois chamadores já têm o dado.
3. **A numeração é atribuída depois da filtragem.** É o único defeito desta feature que não
   aparece no cenário-base: ele só se manifesta num Edital sem Etapas de Avaliação. Cubra-o com
   teste.
4. **A fixture de bytes vai mudar, e isso é previsto.** Regenerá-la é parte da entrega, no mesmo
   commit, com diff revisado (FR-045). O que continua sendo erro é regenerá-la para fazer um teste
   passar.
5. **Três chamadores, uma composição.** Publicação, Retificação e prévia usam o mesmo compositor.
   A Retificação é fácil de esquecer porque não tem tela própria de prévia.
6. **Nada aqui é migration.** Se aparecer campo persistido, tabela, migration ou permissão nova, o
   requisito foi lido errado.

Não há questão de desenho aberta. As seis decisões da seção "Reconciliação com o compositor real"
foram fechadas antes desta redação justamente para que o `/plan` não as renegocie a cada retângulo.
