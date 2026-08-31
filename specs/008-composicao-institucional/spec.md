# Feature Specification: Composição Institucional do Edital

**Feature Branch**: `008-composicao-institucional`

**Created**: 2026-08-30

**Status**: Draft

**Input**: Leitura do documento produzido pelo sistema após a integração da `007`
(`documento2.pdf`), comparado com Editais reais do Cefor, e reconciliação dessa leitura com o
compositor existente antes do planejamento. As evidências técnicas dessa reconciliação estão
registradas em [research.md](./research.md).

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

## Decisões fechadas antes do planejamento

*A primeira redação desta spec foi escrita olhando o documento, e não o sistema que o produz. Ela
propôs requisitos já satisfeitos, requisitos que colidiam com garantias vigentes e requisitos cuja
condição de possibilidade não existia. As quatro decisões abaixo fecham isso em termos de
resultado; a evidência técnica que as motivou e o desenho que as cumpre estão em
[research.md](./research.md).*

1. **A autoridade signatária é metadado do ato, não conteúdo normativo.** Ela não passa a integrar o
   conteúdo publicado para que o documento possa exibi-la: chega à materialização como contexto do
   ato, separado do conteúdo, e sua presença é determinada pelo modo do documento (FR-034), não por
   quem o solicita.
2. **A prévia não tem autoridade**, porque não decorre de uma Publicação. Essa é a segunda — e
   última — diferença admitida entre prévia e publicado.
3. **Sem praça, sem data e sem cadastro de pessoas.** Uma linha como "Vitória (ES), 30 de agosto de
   2026" exigiria conceitos que o sistema não tem. A V1 materializa o que existe.
4. **Identidade visual gráfica fica fora da V1.** O reconhecimento institucional é obtido pelo
   cabeçalho tipográfico; imagem é custo desproporcional ao ganho remanescente (FR-007).

## Princípios desta feature

### P-001 — A fronteira canônica é intransponível

**Formatação humana é responsabilidade exclusiva da materialização. A representação canônica do
snapshot, inclusive decimais, não é alterada pela `008`.** Nenhum requisito desta feature toca
o conteúdo publicado, sua versão canônica, o cálculo do hash, a forma publicada ou a gramática de
endereçamento da Retificação. Este é o mesmo guardrail da `007`, reafirmado porque uma feature
puramente visual é exatamente o lugar onde ele seria abandonado por conveniência.

### P-002 — Existe uma fonte normativa só

O conteúdo homologado. A `008` não cria modelo documental paralelo, não persiste versão textual de
nenhuma apresentação estruturada e não guarda no domínio nada que exista apenas para o PDF.

### P-003 — Sem engine de documentos

Não existe editor visual, tema, template builder, linguagem de template, HTML/CSS configurável,
escolha de fonte, cor personalizável, DOCX nem importação. Existe **um layout institucional V1**.

### P-004 — Os limites são nomeados, não deduzidos

Um requisito visual sem limite escrito é aberto por omissão, e uma proibição genérica de "não criar
framework" paralisa o trabalho que ela deveria apenas conter. Por isso FR-002, FR-003 e FR-004
declaram **o resultado exigido e a fronteira de cada um**, e nenhum outro resultado visual é exigido
por esta feature. Como cada fronteira é cumprida é decisão do plano.

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
  materializada, e a numeração é atribuída depois dessa supressão (FR-011).
- **Perfil maior que uma página inteira.** A quebra desce a cascata de FR-021 até a primeira
  alternativa exequível, e o título do Perfil nunca fica sozinho (FR-022).
- **Sub-bloco maior que uma página inteira.** Atribuições, descrição, lista de requisitos ou tabela
  de modalidades que não caibam sozinhas em uma página quebram internamente, por parágrafo, item ou
  linha (FR-021, alternativas 2 e 3). Nenhuma configuração de conteúdo pode tornar a composição
  impossível.
- **Tabela maior que uma página.** O cabeçalho se repete na continuação e nunca fica órfão (FR-026).
- **Texto mais largo que a coluna da tabela.** A célula quebra em mais de uma linha; a linha da
  tabela cresce; a coluna não estoura a margem.
- **Autoridade cujo nome registrado é uma designação de cargo.** O documento imprime o que a
  Publicação registrou, sem inventar nome próprio (FR-033 e Assumptions).
- **Prévia de Edital ainda incompleto.** Continua compondo o que existe, sem assinatura e sem
  afirmação de integridade.
- **Publicação já existente.** Conserva seus bytes e seu `document_hash`; a composição nova vale
  para publicações novas (invariante de não regressão).

## Requirements *(mandatory)*

### Fronteiras da materialização

*Este bloco declara **resultados e limites observáveis**. Como cada limite é cumprido — e a
evidência que o motivou — pertence a [research.md](./research.md) e [plan.md](./plan.md).*

- **FR-001**: **Formatação humana é responsabilidade exclusiva da materialização. A representação
  canônica do snapshot, inclusive decimais, não é alterada pela `008`.** Nenhum requisito desta
  feature altera o conteúdo publicado, sua versão canônica, o cálculo do hash, a forma publicada ou
  o endereçamento da Retificação.
- **FR-002**: Texto centralizado DEVE ficar visualmente centralizado, coluna alinhada DEVE ficar
  alinhada e nenhuma linha DEVE ultrapassar a margem — em qualquer conteúdo do Edital, inclusive com
  acentuação. **Limites**: o documento não hifeniza, não justifica, não introduz tipografia nova e
  mantém as duas famílias que já usa.
- **FR-003**: Um bloco DEVE ser visualmente delimitado e as colunas de uma tabela DEVEM ser
  visualmente separadas. **Limites**: o vocabulário visual do documento é **texto, fio e contorno**,
  preto sobre branco; ficam fora ícone, sombra, cartão, gradiente, imagem, fundo e paleta. Nada
  disso DEVE ser generalizado para outros tipos de documento.
- **FR-004**: A quebra de página DEVE respeitar as fronteiras do conteúdo, e não apenas o fim do
  espaço disponível. **Limites**: as únicas fronteiras que o documento reconhece são as de FR-020,
  FR-021, FR-022, FR-026 e FR-030; nenhuma outra regra de composição tipográfica é exigida por esta
  feature.

### Identidade institucional e hierarquia (US1)

- **FR-005**: A primeira página DEVE abrir com cabeçalho institucional tipográfico composto por
  `MINISTÉRIO DA EDUCAÇÃO`, `INSTITUTO FEDERAL DO ESPÍRITO SANTO` e a denominação da unidade
  responsável, seguidos do ato, do Processo Seletivo e do título do Edital. *Órgão, instituição e
  unidade são constantes do compositor — a unidade já é hoje, escrita em linha única. Ato, Processo
  e título vêm do snapshot, que desde a `007` carrega `processoCode` e `processoTitle`.*
- **FR-006**: O ato — `EDITAL Nº <número>/<ano>` — DEVE ser destacado por **peso, caixa alta e
  centralização**, e não por corpo tipográfico grande. *Correção calibrada contra os alvos: nos
  Editais 62 e 73 o ato é negrito, maiúsculo e centralizado, em corpo próximo ao do texto — a
  hierarquia vem da forma, não do tamanho. A primeira redação exigia "o maior destaque
  tipográfico", que produziria um título fora do padrão institucional.*
- **FR-007**: O título/objeto do Edital DEVE aparecer imediatamente associado ao ato, e a descrição
  curta NÃO DEVE competir tipograficamente com ele.
- **FR-008**: Brasão, logotipo e qualquer elemento gráfico de identidade visual ficam **fora da V1**.
  Nenhuma imagem é embutida no documento, nenhum recurso binário é acrescentado ao repositório e
  nenhum sistema de branding é criado. *O cabeçalho tipográfico entrega a maior parte do
  reconhecimento institucional a uma fração do custo de embutir imagem. Se a diferença continuar
  incomodando depois desta feature, ela se trata especificamente.*
- **FR-009**: A materialização DEVE definir apenas os níveis tipográficos necessários:
  identificação institucional, título do ato, título de seção, subseção/bloco, corpo e
  nota/metadado. Nenhum design system de documentos é criado.
- **FR-010**: As seções normativas DEVEM ser numeradas na materialização, na ordem institucional já
  definida pelo conteúdo publicado — `1. APRESENTAÇÃO`, `2. DAS DISPOSIÇÕES PRELIMINARES`, e assim
  por diante até a última.
- **FR-011**: A numeração DEVE ser atribuída **depois** de determinadas quais seções serão
  efetivamente materializadas. *O compositor já suprime seção gerada cuja coleção está vazia; numerar
  antes da supressão produziria `5.`, `7.`, `8.` num Edital sem Etapas — um defeito que só apareceria
  em produção, no Edital que não tem tudo.*
- **FR-012**: A numeração NÃO DEVE ser persistida como parte do texto da seção. Alterar a ordem ou o
  catálogo no futuro DEVE produzir numeração coerente sem edição de conteúdo.
- **FR-013**: Subseções — Etapas de Avaliação, e Perfis quando couber — DEVEM ser numeradas a partir
  do número da seção-mãe (`6.1`, `6.2`), sob a mesma regra de FR-011.

### Perfil de Vaga como quadro (US2)

- **FR-014**: Cada Perfil DEVE ser materializado como bloco visualmente delimitado, distinguível do
  Perfil seguinte sem que o leitor precise reler.
- **FR-015**: A identificação do Perfil — código, denominação, localidade, vagas imediatas e
  cadastro reserva — DEVE usar disposição tabular curta, e não uma sequência de linhas
  `rótulo: valor`.
- **FR-016**: NÃO DEVE ser criada uma tabela única contendo todos os campos do Perfil. Descrição,
  atribuições, requisitos e modalidades permanecem blocos próprios.
- **FR-017**: Requisitos permanecem em lista.
- **FR-018**: Modalidades de concorrência DEVEM ser apresentadas em tabela simples com modalidade,
  percentual e fundamento. Versão e vigência da Regra Normativa, quando existirem, DEVEM permanecer
  no documento — em coluna ou em linha secundária —, e a frase técnica atual
  `Regra Normativa — fundamento: …; versão: …; percentual: …` deixa de ser composta. *Tabular não
  pode virar perder: o estado atual imprime esses dois campos, e a composição nova os mantém.*
- **FR-019**: Nenhuma célula DEVE ser preenchida com informação inexistente. Modalidade sem
  percentual apresenta a célula vazia ou o traço de ausência já usado no documento, nunca um valor
  construído nem uma frase técnica.
- **FR-020**: Um Perfil que não couber no espaço restante da página, mas couber inteiro na página
  seguinte, DEVE ser movido integralmente.
- **FR-021**: Um Perfil grande demais para uma página DEVE quebrar segundo esta cascata, na ordem,
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
- **FR-022**: O título de um Perfil NÃO DEVE ficar isolado no fim de uma página.

### Cronograma e Etapas (US3)

- **FR-023**: O Cronograma DEVE ser apresentado em tabela, com ordem, evento, início e término.
- **FR-024**: Evento pontual NÃO DEVE apresentar término. A ausência é apresentada como ausência.
- **FR-025**: A descrição do Evento PODE permanecer junto do evento quando curta, ou em linha
  secundária quando longa.
- **FR-026**: O cabeçalho de uma tabela NÃO DEVE ser separado de sua primeira linha, e DEVE ser
  repetido quando a tabela atravessar a quebra de página. *Com FR-004 isso deixa de ser custoso, e
  por isso a spec o exige em vez de deixá-lo como evolução posterior.*
- **FR-027**: As Etapas de Avaliação DEVEM apresentar caráter, peso e nota mínima em pares
  rótulo-valor alinhados, substituindo a frase corrida
  `caráter: …; peso: …; nota mínima: …`. Cada um continua omitido quando não existe.
- **FR-028**: A referência da Etapa ao Cronograma continua derivada do vínculo existente. Datas NÃO
  DEVEM ser duplicadas no domínio nem no snapshot.

### Tipografia, espaçamento e paginação (US4)

- **FR-029**: O texto normativo DEVE ter largura de linha adequada, entrelinha consistente,
  distância previsível entre parágrafos e alinhamento coerente com documento institucional.
- **FR-030**: Um título de seção NÃO DEVE terminar sozinho no rodapé; ele desce junto de ao menos
  parte do primeiro conteúdo da seção. A regra vale igualmente para subtítulos de Perfil e de Etapa.
- **FR-031**: O espaçamento DEVE distinguir seção nova, bloco dentro da seção, parágrafo e tabela.
  O objetivo é espaço semântico, não compactação.
- **FR-032**: A quebra de linha DEVE passar a usar a largura real do texto (FR-002), substituindo a
  contagem de caracteres.

### Autoridade e integridade (US5)

- **FR-033**: Após o conteúdo normativo, o documento **publicado** DEVE exibir bloco de autoridade
  signatária com o nome e o cargo **registrados na própria Publicação**, sem consulta a catálogo e
  sem transformação. *O que a Publicação registrou é o que o ato afirma; o catálogo é a origem da
  escolha, não a fonte de verdade do que foi assinado.*
- **FR-034**: A autoridade signatária NÃO DEVE entrar no snapshot. Ela DEVE chegar ao compositor
  como **contexto do ato, explícito e separado do conteúdo normativo**. O corpo normativo continua
  sendo função pura do snapshot; o bloco de autoridade é o único elemento derivado de metadado do
  ato. *Os dois fluxos de publicação — o do Edital e o da Retificação — já dispõem da autoridade no
  momento em que o documento é materializado.*
- **FR-035**: A presença da autoridade é **determinada pelo modo**, e não pelo chamador:
  - em modo publicado ela é **obrigatória**, e compor sem ela DEVE ser recusado;
  - em modo prévia ela é **proibida**, e ainda que seja oferecida NÃO DEVE ser composta.

  *Este é o mesmo desenho que a `007` deu ao hash: a garantia não pode depender de o chamador
  lembrar. A primeira redação chamava o contexto de "opcional" e admitia um publicado sem
  autoridade, o que tornava possível emitir um ato administrativo sem quem o praticou — e a
  opcionalidade do parâmetro na interface interna não é a mesma coisa que opcionalidade da
  informação no documento.*
- **FR-036**: O bloco de autoridade NÃO DEVE conter praça nem data. *Praça não existe no sistema, e
  a data do ato não é conteúdo normativo. Introduzir qualquer um dos dois para poder escrever a
  linha "Vitória (ES), 30 de agosto de 2026" seria criar conceito por motivo tipográfico.*
- **FR-037**: NÃO DEVEM ser criados assinatura digital, imagem de assinatura, certificado,
  ICP-Brasil, gov.br, QR code nem carimbo eletrônico. Esta é a representação documental da
  autoridade que já praticou o ato, e nada além.
- **FR-038**: A declaração de integridade DEVE ser deslocada para bloco discreto **após** o bloco de
  autoridade, tipograficamente subordinado ao conteúdo normativo, sem perder nenhuma informação
  necessária ao mecanismo. Nenhuma página nova e nenhum serviço novo são criados para isso.
- **FR-039**: `Versão do schema` NÃO DEVE aparecer como seção normativa do Edital. Ela permanece no
  mecanismo e no snapshot; o que muda é o que se imprime como corpo do ato.
- **FR-040**: O SHA-256 completo permanece no bloco de verificação e o abreviado permanece no
  rodapé. A afirmação de derivação da versão homologada permanece.

### Prévia e publicado

- **FR-041**: Prévia e publicado DEVEM utilizar o mesmo compositor e a mesma composição normativa.
  As diferenças admitidas são **exclusivamente** a identificação de prévia e os metadados próprios
  do ato de Publicação — autoridade signatária e declaração de integridade. Nenhuma regra visual
  DEVE existir só na prévia.
- **FR-042**: A marca de prévia NÃO DEVE alterar as quebras de página do conteúdo normativo: para
  o mesmo snapshot, o conjunto de quebras do corpo normativo é o mesmo na prévia e no publicado.
  *"Não alterar significativamente" era inverificável e deixava a decisão para quem implementa. O
  corpo normativo é a parte comum aos dois modos, e por isso é sobre ele que a igualdade se afirma —
  a assinatura e o bloco de verificação existem só no publicado e naturalmente ocupam espaço a
  mais, depois do conteúdo.*

### Retificação

- **FR-043**: Todo documento consolidado produzido após Retificação DEVE usar exatamente a mesma
  composição institucional definida nesta feature, e recebe a autoridade signatária da própria
  Publicação da Retificação. Nenhum caminho visual paralelo é criado.

### Fixture documental

- **FR-044**: A evidência de que o documento publicado não mudou por acidente DEVE ser refeita
  **apenas junto de uma mudança intencional de composição, na mesma revisão que a produz**, com a
  diferença resultante conferida. Refazê-la para calar um teste que falhou continua sendo erro. Essa
  evidência DEVE permanecer reproduzível por quem não participou da mudança — o que exige que tudo
  de que ela depende, inclusive a autoridade signatária exigida por FR-035, esteja versionado ao
  lado dela.

### Key Entities

Nenhuma. A `008` não cria, altera nem remove entidade, campo, estado, transição, migration ou
permissão. Ela altera exclusivamente a materialização documental e a assinatura interna do
compositor, que ganha um parâmetro de contexto do ato.

## Success Criteria *(mandatory)*

- **SC-001**: A primeira página apresenta, nesta ordem e antes de qualquer conteúdo normativo,
  órgão, instituição, unidade, ato, Processo e título; órgão, instituição e unidade estão
  centralizados em corpo menor que o do texto; o ato está em negrito, caixa alta e centralizado; e a
  descrição não excede o título em peso nem em corpo.
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
- **SC-012**: Nenhuma alteração do conteúdo publicado, da sua versão canônica, da forma canônica,
  do cálculo de hash ou da gramática de endereçamento é necessária para cumprir a feature.
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
| R-02 | O ato está em negrito, caixa alta e centralizado, destacado do texto ao redor | 1 |
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

**Estado inicial**: `referencias/estado-inicial-apos-007.pdf` — o documento que o sistema produz
hoje, depois da `007`.

**Alvos**: `referencias/alvo-edital-62-2026.pdf` e `referencias/alvo-edital-73-2026.pdf` — Editais
oficiais do Cefor. As características observáveis contra as quais a rubrica é conferida:

| Observado nos dois alvos | Consequência para a `008` |
|---|---|
| Brasão centralizado no topo | **Diferença aceita** — FR-008 põe imagem fora da V1 |
| Órgão, instituição e unidade centralizados, em corpo menor que o do texto | FR-005 |
| Ato em negrito, caixa alta e centralizado, em corpo próximo ao do texto | FR-006, corrigido por esta calibração |
| Parágrafo de preâmbulo não numerado, antes da seção 1 | Já existe como seção de Apresentação |
| Seções `1. DAS DISPOSIÇÕES PRELIMINARES`, negrito e caixa alta | FR-010 |
| Itens numerados `1.1`, `2.1`, `3.2.1` dentro da seção | **Diferença aceita** — o conteúdo das seções textuais é texto livre, e numerar parágrafo automaticamente seria engine normativa, vedada por P-003 |
| Corpo **justificado** nos dois alvos | **Diferença aceita e declarada** — FR-002 exclui justificação da V1. É a maior diferença remanescente depois do brasão |

*As três diferenças aceitas são deliberadas e estão declaradas nos requisitos que as excluem. O
critério emblemático não é identidade de diagramação (§3): é reconhecer os dois documentos como da
mesma organização.*

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
| 5 (US5) | Autoridade signatária e integridade discreta ao final | Contexto de publicação no compositor (FR-034) |

**A entrega 1 precisa mudar visivelmente a primeira página.** Não é aceitável uma primeira entrega
que introduza capacidade sem resultado visual — a métrica de fonte viaja *dentro* do cabeçalho
centralizado, não antes dele.
