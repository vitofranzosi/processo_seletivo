# Feature Specification: Edital Institucional

**Feature Branch**: `007-edital-institucional`

**Created**: 2026-08-30

**Status**: Draft

**Input**: Auditoria de UI/UX da jornada de autoria, executada no navegador sobre a `006` recém-integrada
(`specs/006-elaboracao-completa-edital/auditoria-ux.md`), com 26 achados numerados, 6 acertos a
preservar e 6 limitações estruturais. A `006.1` corrigiu os quatro bloqueadores e os resíduos
imediatos; o que resta é produto.

## A frase que governa esta feature

> **A `007` deve ser a última feature dedicada à autoria antes de avançarmos para a jornada do
> candidato. Seu objetivo é aproximar o sistema de um Edital institucional real e eliminar os
> principais atritos restantes da autoria — não maximizar a flexibilidade do editor.**

Todo requisito abaixo responde a uma de duas perguntas: *isto aproxima o documento de um Edital
real?* ou *isto tira atrito da jornada de quem elabora?* O que não responde a nenhuma das duas não
pertence a esta spec, por mais razoável que pareça.

## Contexto

A `006` completou o objeto central do produto — Etapas de Avaliação, modalidades de reserva com
esquema, seções textuais e prévia do documento — e a `006.1` fechou o que a demonstração navegável
revelou: parágrafos achatados no PDF, Revisão incompleta, Retificação sem alcance às coleções novas
e comentário de template impresso na tela. As duas estão na `main`.

O que sobrou da auditoria não é dívida da entrega anterior. São dezesseis achados de duas naturezas
distintas, e a distinção importa para o escopo:

**O documento ainda não se parece com um Edital.** O compositor imprime `Situação: PLANEJADO` no
Cronograma (`publicacoes/infrastructure/pdf.py:203-204`) — um estado interno da máquina, ao lado de
datas destinadas ao candidato. Imprime `percentual: 20.0000%`, `peso: 2.0000` e
`nota mínima: 60.0000` (`:157`, `:235`, `:237`), porque lê o decimal canônico e o escreve como está.
E a seção `INTEGRIDADE` identifica o ato por dois UUIDs — `Identificador do Edital` e
`Processo Seletivo` (`:289-290`) — no corpo do documento que o candidato lê. Nenhum desses três é
defeito de dado: os três são a forma canônica escapando para a apresentação.

**O Edital ainda não diz o que a vaga é.** O Perfil de Vaga carrega código, denominação,
localidade, vagas, cadastro reserva, requisitos e modalidades. Não carrega atribuições, carga
horária nem remuneração — que é o primeiro bloco que qualquer pessoa procura num Edital real. E o
catálogo de seções tem sete entradas (`editais/domain/secoes.py`), das quais faltam três que todo
Edital institucional tem: apresentação, requisitos gerais de participação e critérios de
classificação.

**E a jornada ainda tem becos.** Criado o Processo, a tela seguinte destaca em amarelo por que o
cancelamento está impedido e não oferece elaborar. O detalhe do Edital publicado oferece `Retificar`
a quem não pode retificar, e no mesmo cartão diz que não há ato disponível. Oferece `Submeter`
sabendo que a recusa é certa. Submetido, o Edital fica "aguardando" sem dizer quem deve agir.

Há ainda um achado descoberto durante a própria correção da `006.1` e registrado sem ser corrigido:
criar um Processo cujo primeiro Edital repita número e ano de **qualquer** outro Edital do escopo
falha com "Identificação institucional já utilizada" — porque
`processos/application/commands.py:29-46` envolve os dois `create` num único `except IntegrityError`
que sempre devolve a mensagem do Processo. A identificação está correta; o conflito é do Edital, e o
código de erro certo já existe no mesmo arquivo (`edital_identifier_conflict`, `:92-95`).

Esta feature não constrói mecanismo novo. Ela paga o que separa um sistema que funciona de um
sistema que se pode mostrar a uma banca.

## Precondição de implantação

**A `007` deve ser concluída antes do primeiro Edital de produção. Durante o desenvolvimento, dados
publicados de demonstração podem ser recriados. A feature poderá incrementar diretamente
`SCHEMA_VERSION` e atualizar o catálogo de seções sem mecanismo de retrocompatibilidade.**

Isto não é conveniência: é o que dispensa construir compatibilidade, e foi verificado no código
antes de ser escrito aqui.

- Crescer o catálogo de seções torna Editais **já publicados** irretificáveis. A verificação de
  publicação recusa conteúdo em que uma seção tenha sido acrescentada ou removida em relação ao
  catálogo vigente (FR-041 da `006`); uma Retificação sobre uma Publicação-base de sete seções, num
  sistema cujo catálogo passou a ter dez, falha por topologia.
- Subir `SCHEMA_VERSION` (`shared/canonical.py:7`, hoje `2`) torna Editais publicados irretificáveis
  por `canonical_schema_version_mismatch`: a consolidação recusa conteúdo-base cuja versão difira da
  vigente (FR-047 da `006`).

As duas consequências são corretas — são a integridade funcionando. A precondição é o que permite
aceitá-las em vez de construir a máquina de conversão que a `006` proibiu e que não teria nada real
para converter.

## Princípios desta feature

### P-001 — Fidelidade e fluidez, não flexibilidade

Cada requisito aumenta a fidelidade do Edital real ou a fluidez da jornada de autoria. **Encontrar
durante a implementação uma necessidade plausível de uma futura feature não autoriza incluí-la na
`007`.** Um achado novo se registra; não se conserta aqui.

### P-002 — A fronteira canônica é intransponível

**Formatação humana é responsabilidade exclusiva da materialização/apresentação. A forma canônica do
snapshot, inclusive representação decimal, não deve ser alterada.**

`20.0000` continua sendo `20.0000` dentro de `edital_snapshot`, no hash e no endereçamento da
Retificação. Quem escreve "20%" no documento é o compositor, e só ele. A tentação desta feature é
resolver o problema de leitura no lugar errado — e o lugar errado custaria o hash, a
reprodutibilidade e a gramática de endereçamento de uma vez.

### P-003 — O catálogo de seções continua fixo

A `007` acrescenta as três seções institucionais previstas ao catálogo declarado. **Não cria seção
arbitrária, reordenação livre nem engine de documento.** O conjunto e a ordem continuam definidos
pelo sistema; quem elabora edita o texto das textuais. Esta é a mesma decisão da `006`, reafirmada
porque o crescimento do catálogo é exatamente o momento em que ela seria abandonada por descuido.

### P-004 — Passagem de bastão é informação, não motor

Depois de submeter e de homologar, o sistema **informa** a situação atual e o papel responsável pelo
próximo ato. Não cria fila, não cria notificação, não cria atribuição a pessoa, não cria workflow
engine. A informação é derivada do estado do Edital e do mapa de permissões que já existe.

### P-005 — Os mecanismos consolidados são estendidos, nunca redesenhados

Snapshot canônico, hash, publicação imutável, proveniência, endereçamento por chave estável,
consolidação temporal, catálogo declarado e modo de renderização permanecem como estão. Campo novo
em coleção existente entra pelos registros declarativos da `005`/`006`. Qualquer proposta que exija
alterar a gramática de `publicacoes/domain/changes.py` é sinal de que o conceito foi modelado
errado.

### P-006 — Sem sistema de permissões, sem sistema de modelos

Retificar deixa de ser oferecido a quem não pode retificar usando a checagem de permissão que já
existe. Isso não autoriza sistema genérico de permissões, política declarativa nem camada de
autorização de interface. Da mesma forma, nada de biblioteca de modelos, clonagem ou importação.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O documento se lê como um Edital (Priority: P1)

Quem lê o documento — candidato, banca, controle interno — encontra um texto normativo, não um
despejo de dados internos.

**Why this priority**: é a entrega de maior efeito por hora gasta e a única que não toca o snapshot.
São três substituições no compositor, todas do lado da apresentação, todas verificáveis a olho no
PDF. E é o que permite mostrar o sistema antes de qualquer outra coisa desta feature ficar pronta.

**Independent Test**: publicar um Edital com Cronograma, Etapas com peso e nota mínima e modalidade
com percentual; abrir o documento e não encontrar `PLANEJADO`, `20.0000` nem UUID no corpo — e
encontrar a declaração de integridade intacta com o SHA-256.

**Acceptance Scenarios**:

1. **Given** um Cronograma com Eventos, **When** leio o documento, **Then** nenhum estado interno de
   Evento é impresso.
2. **Given** uma modalidade com percentual `20.0000` e uma Etapa com peso `2.0000` e nota mínima
   `60.0000`, **When** leio o documento, **Then** os três aparecem em forma legível, sem casas
   decimais que a informação não tem.
3. **Given** o mesmo Edital, **When** consulto o snapshot publicado, **Then** os três valores
   continuam na forma canônica de quatro casas e o hash do conteúdo não depende de como o documento
   os escreveu.
4. **Given** um Edital publicado, **When** leio a seção de integridade, **Then** o documento se
   identifica pelo Edital e pelo Processo em termos institucionais, declara derivar da versão
   homologada e exibe o SHA-256 do conteúdo — **e** não exibe UUID.
5. **Given** uma Retificação sobre esse Edital, **When** endereço
   `/profiles/id=…/competitionModalities/id=…/normativeRule/percentage`, **Then** o valor
   endereçado e gravado continua sendo o canônico, e a tela de Retificação continua exigindo e
   produzindo a forma canônica.

---

### User Story 2 - O Edital tem as seções que um Edital tem (Priority: P1)

Quem elabora encontra no assistente as seções institucionais que hoje precisa espremer dentro de
"Disposições Preliminares", e o documento passa a ter a estrutura que uma banca reconhece.

**Why this priority**: junto da `US3`, é o que a frase de abertura chama de "Edital institucional
real". As duas tocam o conteúdo publicado e, por isso, compartilham um único incremento de versão
canônica.

**Independent Test**: abrir a etapa de Conteúdo de um Edital novo, encontrar dez seções em vez de
sete, editar o texto das três novas, publicar, e retificar o conteúdo de uma delas.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** acesso a etapa de Conteúdo, **Then** vejo o catálogo
   completo em ordem, com as três seções institucionais novas entre as existentes, cada uma com
   redação inicial editável.
2. **Given** uma das seções novas, **When** altero seu texto e visualizo o Edital, **Then** a
   alteração aparece no documento na posição declarada pelo catálogo.
3. **Given** o assistente, **When** procuro acrescentar, remover ou reordenar seções, **Then** não
   existe caminho para isso — o conjunto e a ordem continuam definidos pelo sistema.
4. **Given** um Edital publicado com o catálogo novo, **When** uma Retificação endereça
   `/sections/id=<chave>/content` de uma seção nova, **Then** é aceita pelo mecanismo existente, sem
   alteração da gramática.
5. **Given** o incremento de versão canônica, **When** consulto qualquer conteúdo publicado antes
   dele, **Then** o sistema o recusa explicitamente para consolidação em vez de convertê-lo — e não
   existe caminho de conversão.

---

### User Story 3 - O Edital diz o que a vaga é (Priority: P1)

Quem elabora descreve atribuições, carga horária e remuneração do Perfil de Vaga, e o candidato lê
isso no documento.

**Why this priority**: é a ausência mais visível para quem lê um Edital real. Um Perfil que declara
código, vagas e requisitos mas não diz o que a pessoa vai fazer nem quanto vai receber não é um
Perfil de Edital.

**Independent Test**: preencher os três campos em dois Perfis, salvar, ir a outra etapa, voltar,
publicar e encontrar tudo no documento — e retificar a remuneração depois de publicado.

**Acceptance Scenarios**:

1. **Given** a etapa de Perfis, **When** edito um Perfil, **Then** informo atribuições, carga
   horária e remuneração em campos próprios, todos opcionais.
2. **Given** os três campos preenchidos, **When** salvo outra etapa e recarrego, **Then** continuam
   lá — a mesma preservação de ida e volta que a `006` garantiu para as modalidades.
3. **Given** um Perfil sem os três campos, **When** publico, **Then** a publicação não é impedida e
   o documento simplesmente não imprime seções vazias.
4. **Given** um Perfil com os três campos, **When** leio o documento, **Then** eles aparecem junto
   dos demais dados do Perfil, em texto corrido, com os parágrafos preservados.
5. **Given** um Edital publicado, **When** uma Retificação endereça `/profiles/id=…/<campo novo>`,
   **Then** é aceita pelo mecanismo existente.

---

### User Story 4 - A jornada administrativa não oferece becos (Priority: P2)

Quem administra encontra, em cada tela, o próximo passo real — e não é convidado a caminhos que o
sistema já sabe que vão recusar.

**Why this priority**: são cinco defeitos de exposição sobre capacidades e informações que já
existem. Nenhum deles exige decisão de desenho, e juntos mudam a percepção de que o sistema conhece
o próprio estado.

**Independent Test**: criar um Processo cujo Edital repita número e ano de outro; corrigir; ser
levado direto a elaborar; abrir o detalhe de um Edital vazio e ver `Submeter` desabilitado com o
motivo ao lado; entrar como quem não pode retificar e não encontrar o convite.

**Acceptance Scenarios**:

1. **Given** que criei um Processo Seletivo, **When** chego à tela seguinte, **Then** elaborar o
   Edital é a ação primária, e o impedimento de cancelar não ocupa o destaque.
2. **Given** um Edital 21/2027 já existente no escopo, **When** crio um Processo cujo primeiro
   Edital repete número e ano, **Then** a recusa aponta o número/ano do Edital, e não a
   identificação institucional do Processo.
3. **Given** um Edital sem os dados mínimos, **When** abro seu detalhe, **Then** `Submeter` aparece
   desabilitado com o motivo ao lado — não escondido e não oferecido.
4. **Given** que não tenho permissão de elaborar Retificações, **When** abro o detalhe de um Edital
   publicado, **Then** `Retificar` não é oferecido como ação; **and** se alcanço a tela por URL,
   ela se apresenta em leitura, sem campos de edição nem botão de envio.
5. **Given** qualquer situação de qualquer Edital, **When** leio o cartão de ações, **Then** a
   mensagem de "nenhum ato disponível" só aparece quando de fato não há nenhuma ação listada.

---

### User Story 5 - Quem entrega sabe a quem entregou (Priority: P2)

Depois de submeter e de homologar, quem agiu vê a situação atual e qual papel precisa agir a seguir.

**Why this priority**: é a limitação estrutural que a auditoria registrou como "nenhuma noção de
passagem de bastão", e a única delas que cabe nesta feature sem virar produto novo. É informação
derivada, não mecanismo.

**Independent Test**: submeter um Edital como quem elabora, ler a tela e saber quem age agora;
homologar como outra pessoa, ler de novo e saber que falta publicar — sem que nenhuma fila,
notificação ou atribuição exista.

**Acceptance Scenarios**:

1. **Given** um Edital que acabei de submeter, **When** leio a confirmação e o detalhe, **Then**
   ambos dizem em que situação o Edital está e qual papel é responsável pelo próximo ato.
2. **Given** um Edital homologado, **When** o abro como quem publica, **Then** a tela diz que o
   próximo ato é meu.
3. **Given** um Edital homologado por mim, que também elaborei, **When** o abro, **Then** a
   indicação do próximo responsável é compatível com a segregação de funções já avisada — não me
   aponta como quem deve publicar sozinho.
4. **Given** qualquer situação, **When** procuro fila, caixa de entrada, aviso ou designação de
   pessoa, **Then** nada disso existe.

---

### User Story 6 - Os atritos de operação (Priority: P3)

Quem elabora deixa de pagar, em cada volta, o preço de informações que a tela tem e não mostra.

**Why this priority**: cada item é pequeno e nenhum bloqueia. Juntos são a diferença entre um
formulário que se atravessa e um que se aguenta. Vêm por último porque nenhum outro depende deles.

**Independent Test**: percorrer o assistente inteiro observando obrigatoriedade, posição das linhas,
datas nos vínculos, agrupamento do caráter, confirmação ao remover e a mensagem depois de cada ato.

**Acceptance Scenarios**:

1. **Given** qualquer formulário do produto, **When** o leio, **Then** os campos obrigatórios estão
   marcados como tais na etiqueta.
2. **Given** um envio recusado, **When** leio a tela, **Then** há um resumo dos erros no topo com
   âncora para cada campo **e** a indicação junto do campo correspondente.
3. **Given** a criação de um Processo, **When** olho o campo `Ano`, **Then** ele tem a mesma
   aparência dos campos vizinhos.
4. **Given** uma lista ordenável, **When** olho a primeira e a última linha, **Then** os botões
   impossíveis estão desabilitados **and** cada linha diz sua posição.
5. **Given** a linha de uma Etapa, **When** escolho o Evento a que ela se vincula, **Then** a opção
   mostra a data que a Etapa vai herdar.
6. **Given** os campos de caráter de uma Etapa, **When** os leio, **Then** estão agrupados sob uma
   legenda que os nomeia.
7. **Given** uma linha com conteúdo preenchido, **When** aciono removê-la, **Then** o sistema
   confirma antes de descartar.
8. **Given** que vou publicar, **When** informo a autoridade signatária, **Then** a escolho numa
   lista conhecida e não digito identificador nenhum.
9. **Given** um Edital recém-criado, **When** olho o assistente, **Then** a etapa de Conteúdo não se
   declara concluída sem ter sido aberta.
10. **Given** que pratiquei um ato, **When** leio a confirmação, **Then** ela nomeia o ato como a
    trilha de auditoria o nomeia, e não pela chave interna.
11. **Given** quatro gravações de rascunho em etapas diferentes, **When** leio a trilha de
    auditoria, **Then** cada uma diz qual área do Edital foi alterada.

---

### Edge Cases

- Editais publicados antes desta feature: tornam-se irretificáveis por topologia de seções e por
  versão canônica. É o comportamento correto, e a precondição de implantação é o que o admite.
  Dados de demonstração são recriados; nenhum caminho de conversão é construído.
- Percentual, peso e nota mínima com casas decimais significativas (`12.5000`, `7.5000`): a
  formatação humana preserva o que a informação tem e descarta apenas o que ela não tem.
- Perfil com atribuições longas em vários parágrafos: o documento preserva os parágrafos, pelo mesmo
  caminho que a `006.1` abriu para as seções textuais.
- Autoridade signatária que não está na lista conhecida: a lista é configurável e o caminho de
  incluir uma autoridade não pode depender de digitar UUID em formulário de publicação.
- Ato desabilitado por motivo que deixa de valer enquanto a tela está aberta: a recusa continua
  sendo do domínio; a desabilitação é previsão, não autorização.
- Remoção de linha vazia: confirmar não pode virar atrito onde não há trabalho a perder.

## Requirements *(mandatory)*

### Materialização humana do documento (US1)

- **FR-001**: **Formatação humana é responsabilidade exclusiva da materialização/apresentação. A
  forma canônica do snapshot, inclusive representação decimal, não deve ser alterada.** Nenhum
  requisito desta feature altera `edital_snapshot`, o cálculo do hash, a forma publicada ou o
  endereçamento da Retificação por motivo de legibilidade.
- **FR-002**: O documento NÃO DEVE imprimir estados internos de entidade. O estado do Evento de
  Cronograma (`PLANEJADO` e demais) sai do documento. *Existe precedente no próprio compositor: o
  tipo de cadastro reserva já é traduzido por um mapa antes de ser escrito
  (`publicacoes/infrastructure/pdf.py:37-41`). O estado do Evento é a exceção que ficou de fora — e,
  diferentemente do cadastro reserva, ele é informação de gestão, não de edital.*
- **FR-003**: Percentual, peso e nota mínima DEVEM ser escritos em forma legível no documento,
  preservando as casas significativas e descartando as que a informação não tem. A conversão vive no
  compositor.
- **FR-004**: O corpo normativo destinado ao candidato NÃO DEVE expor identificadores técnicos.
  A declaração de integridade DEVE ser preservada: continua afirmando derivação da versão homologada
  e continua exibindo o SHA-256 do conteúdo, mas identifica o Edital e o Processo em termos
  institucionais. *O SHA-256 permanece porque é o que a declaração prova; o UUID sai porque não
  prova nada a quem lê e é a forma interna vazando para a apresentação.*
- **FR-005**: A distinção entre prévia e documento publicado permanece um modo explícito do
  renderizador (FR-015 da `006`); esta feature NÃO DEVE acrescentar condicionais de modo espalhadas
  pela composição.
- **FR-006**: A fixture de bytes do documento publicado DEVE ser regenerada uma vez, cobrindo todas
  as mudanças de composição desta feature. *É o caso legítimo de regeneração: a fixture guarda o
  documento correto, e o documento mudou por decisão declarada.*

### Conteúdo institucional (US2)

- **FR-007**: O catálogo declarado de seções (`editais/domain/secoes.py`) DEVE passar a incluir três
  seções textuais institucionais — **Apresentação**, **Requisitos Gerais de Participação** e
  **Critérios de Classificação** — cada uma com chave estável, título, ordem e redação inicial.
- **FR-008**: As três DEVEM ocupar posições coerentes com a leitura de um Edital: a apresentação
  antes dos Perfis, os requisitos gerais antes da inscrição, os critérios de classificação depois
  das Etapas de Avaliação.
- **FR-009**: O conjunto e a ordem das seções permanecem definidos pelo sistema. NÃO DEVE existir
  caminho para acrescentar, remover ou reordenar seções, nem na interface nem na Retificação.
- **FR-010**: As três novas DEVEM ser textuais, editáveis na etapa de Conteúdo, presentes na prévia
  e no documento publicado, e retificáveis por identidade estável pelo mecanismo existente.
- **FR-011**: A identidade das seções continua determinística sobre `(edital, chave)`; o catálogo
  cresce sem introduzir persistência de estrutura.

### Perfil de Vaga institucional (US3)

- **FR-012**: O Perfil de Vaga DEVE passar a registrar **atribuições**, **carga horária** e
  **remuneração** como texto descritivo opcional.
- **FR-013**: Os três DEVEM ser texto livre descritivo. NÃO DEVE ser introduzido objeto de moeda,
  tabela salarial, regime de trabalho, jornada estruturada nem unidade de medida modelada. *Um
  Edital descreve remuneração em prosa — "R$ 4.200,00 mensais, acrescidos de auxílio-alimentação" —
  e modelar isso agora seria construir a estrutura antes de existir a regra que a consome.*
- **FR-014**: Os três DEVEM ser preenchíveis na etapa de Perfis, preservados na ida e volta da
  gravação do rascunho como os demais campos do Perfil, e integrar a coleção `profiles` do snapshot.
- **FR-015**: Os três DEVEM aparecer no documento quando informados, com parágrafos preservados, e
  ser omitidos quando ausentes.
- **FR-016**: Os três DEVEM ser retificáveis pelo caminho já existente do Perfil, sem coleção nova
  no snapshot e sem alteração da gramática.

### Versão canônica

- **FR-017**: A feature incrementa `SCHEMA_VERSION` **uma única vez** (`2` → `3`), cobrindo
  simultaneamente as seções novas do catálogo e os campos novos do Perfil. *Pelo mesmo motivo que a
  `006` declarou: subir a versão com uma parte e acrescentar a outra depois produziria snapshots de
  versão 3 com e sem as propriedades, e a versão canônica deixaria de identificar uma forma.*
- **FR-018**: Em consequência de FR-017, as entregas de `US2` e `US3` DEVEM integrar-se juntas ao
  ramo principal.
- **FR-019**: NÃO DEVE ser introduzido mecanismo de migração, conversão ou compatibilidade entre
  versões de esquema, nem de catálogo. A recusa de conteúdo-base com versão divergente
  (FR-047 da `006`) permanece como está e é o comportamento esperado.
- **FR-020**: A cobertura declarativa da `006` permanece: coleção nova de entidades identificáveis é
  declarada nos registros existentes, e a suíte falha quando uma coleção presente no snapshot não
  estiver declarada. Esta feature não acrescenta coleção-raiz.

### Fluxo administrativo (US4)

- **FR-021**: A tela seguinte à criação de um Processo Seletivo DEVE oferecer elaborar o Edital como
  ação primária, nomeando o Edital. O impedimento de cancelar NÃO DEVE ocupar o destaque de uma
  tela cujo próximo passo é outro.
- **FR-022**: A recusa por conflito de unicidade na criação de Processo com primeiro Edital DEVE
  apontar a entidade e o campo responsáveis pelo conflito. Violação de `(escopo, número, ano)` do
  Edital DEVE ser apresentada como conflito do número/ano do Edital, e não como conflito da
  identificação institucional do Processo. *O código de erro correspondente já existe
  (`processos/application/commands.py:92-95`); o que falta é separar os dois `create` no tratamento
  da exceção (`:29-46`).*
- **FR-023**: O conjunto de ações disponíveis num Edital DEVE ser calculado **uma única vez** e a
  mensagem de ausência de ações DEVE derivar desse mesmo conjunto. NÃO PODE haver duas regras
  independentes produzindo a lista e o vazio.
- **FR-024**: Ato cuja recusa é previsível pela informação já apresentada na tela DEVE aparecer
  **desabilitado com o motivo**, e não oferecido nem escondido. *A previsão já existe na tela de
  confirmação; o requisito é usá-la também onde o ato é oferecido.*
- **FR-025**: A desabilitação é previsão de interface e NÃO substitui a verificação de domínio. A
  recusa autoritativa continua no backend, inalterada.
- **FR-026**: A ação de retificar NÃO DEVE ser oferecida a quem não tem a permissão de elaborar
  Retificações, pela mesma checagem que a listagem já faz. Alcançada por URL, a tela DEVE
  apresentar-se em leitura, sem campos de edição nem envio.
- **FR-027**: FR-026 NÃO autoriza sistema genérico de permissões, política declarativa nem camada
  nova de autorização de interface.

### Passagem de bastão (US5)

- **FR-028**: Depois da submissão e depois da homologação, o sistema DEVE informar a situação atual
  do Edital e o **papel** responsável pelo próximo ato, no detalhe do Edital e na confirmação do ato
  praticado.
- **FR-029**: A informação DEVE ser derivada do estado do Edital e do mapa de papéis e permissões já
  existente. NÃO DEVE ser persistida como atribuição nem duplicada como dado.
- **FR-030**: NÃO DEVEM ser criados fila, caixa de entrada, notificação, e-mail, designação a pessoa
  específica, prazo, lembrete ou workflow engine.
- **FR-031**: A indicação DEVE ser coerente com a segregação de funções já verificada na publicação:
  não pode apontar como próximo responsável alguém que o domínio recusaria.

### Atritos de operação (US6)

- **FR-032**: Campos obrigatórios DEVEM ser identificados como tais na etiqueta, em todo o produto.
- **FR-033**: Recusa de envio DEVE ser apresentada em resumo no topo, com âncora para cada campo, e
  também junto do campo correspondente. *O resumo sozinho obriga a procurar; a marca junto do campo
  sozinha obriga a rolar até achar.*
- **FR-034**: Os campos da criação de Processo DEVEM ter a mesma aparência dos demais campos do
  produto, incluindo os que não são de texto simples.
- **FR-035**: Em listas ordenáveis, os botões de mover DEVEM estar desabilitados onde a operação é
  impossível, e cada linha DEVE exibir sua posição na coleção.
- **FR-036**: O seletor de Evento vinculado a uma Etapa DEVE exibir a data que a Etapa herda.
- **FR-037**: As marcações de caráter eliminatório e classificatório DEVEM estar agrupadas sob
  legenda que as nomeie.
- **FR-038**: Remover uma linha com conteúdo preenchido DEVE exigir confirmação. Linha vazia NÃO
  DEVE exigir.
- **FR-039**: A autoridade signatária DEVE ser escolhida em lista configurável de autoridades
  conhecidas; NENHUM identificador DEVE ser digitado no ato de publicação. *A lista pode nascer
  pequena e por configuração. Integração com diretório institucional está fora de escopo.*
- **FR-040**: O assistente DEVE distinguir uma etapa **pronta para revisar** de uma etapa
  **concluída** — uma etapa cujo conteúdo nasceu de padrão do sistema não pode declarar-se
  concluída antes de ser aberta.
- **FR-041**: A confirmação de ato praticado DEVE nomear o ato pelo rótulo humano, o mesmo que a
  trilha de auditoria já usa, e não pela chave interna.
- **FR-042**: A auditoria de gravação de rascunho DEVE registrar qual área do Edital foi alterada.
  *A trilha existe para responder questionamento; quatro registros idênticos de "alteração do
  rascunho" não respondem nenhum. O sistema conhece a etapa gravada e descarta a informação.*
- **FR-043**: FR-042 NÃO autoriza diff de conteúdo, versionamento de rascunho nem histórico
  editorial. Registra-se a área, não a diferença.

### Key Entities

- **Seção do Edital**: já existe. Esta feature acrescenta três entradas textuais ao catálogo
  declarado; não altera a forma da entidade nem a natureza do catálogo.
- **Perfil de Vaga**: já existe. Esta feature acrescenta três atributos textuais descritivos —
  atribuições, carga horária e remuneração — e nenhuma relação nova.
- **Autoridade Signatária**: já é registrada na Publicação. Esta feature acrescenta a origem
  conhecida de onde ela é escolhida; sua forma — configuração, seed ou catálogo declarado — é
  decisão do `plan`, não desta spec, e não pode introduzir integração externa.

## Success Criteria *(mandatory)*

- **SC-001**: Um leitor do documento publicado não encontra estado interno de entidade, decimal de
  quatro casas nem identificador técnico no corpo normativo, e encontra a declaração de integridade
  com o SHA-256.
- **SC-002**: O snapshot publicado do mesmo Edital continua em forma canônica, e o hash do conteúdo
  não muda em função de como o documento foi escrito.
- **SC-003**: Um usuário edita as dez seções previstas no catálogo e não encontra caminho para
  acrescentar, remover ou reordenar nenhuma.
- **SC-004**: Um usuário descreve atribuições, carga horária e remuneração de um Perfil, salva outra
  etapa, retorna e encontra tudo preservado.
- **SC-005**: As seções novas e os campos novos do Perfil são endereçáveis pela Retificação pelo
  mecanismo existente, sem alteração da gramática.
- **SC-006**: Criar um Processo cujo primeiro Edital repita número e ano existente produz recusa que
  aponta o número/ano do Edital.
- **SC-007**: Em nenhuma tela o mesmo cartão oferece uma ação e afirma que não há ação.
- **SC-008**: Um ato cuja recusa é certa aparece desabilitado com o motivo, e quem não pode retificar
  não é convidado a retificar.
- **SC-009**: Depois de submeter e depois de homologar, quem agiu lê na tela qual papel age a seguir
  — e não existe fila, notificação nem atribuição no sistema.
- **SC-010**: A jornada completa da `SC-009` da `006` — **Painel → Novo Processo → Identificação →
  Perfis → Cronograma → Etapas → Modalidades → Conteúdo → Revisão → Prévia → Submissão →
  Homologação → Publicação → documento publicado** — permanece demonstrável pela interface
  administrativa, com dois atores, e agora produz um documento que se lê como Edital. Este é o
  critério emblemático da feature.

## Assumptions

- A interface permanece server-rendered com fragmentos; nenhuma dependência nova de frontend é
  introduzida.
- A redação institucional inicial das três seções novas pode ser genérica nesta versão, como a das
  sete existentes; adequá-la à redação do Cefor é trabalho editorial.
- "Carga horária" e "remuneração" são texto descritivo por decisão declarada em FR-013, não por
  falta de definição.
- A lista de autoridades signatárias nasce pequena e configurável; quantas e de onde é decisão do
  `plan`, limitada por FR-039 a não introduzir integração externa.
- Papéis e permissões existentes bastam; nenhum papel novo é criado.
- O incremento de `SCHEMA_VERSION` invalida os dados de demonstração publicados, que são recriados
  pela seed.

## Out of Scope

Desta feature inteira, e sem exceção:

- inscrição, candidato, comissão, banca, avaliação, lançamento de notas, recursos, classificação
  operacional e convocação;
- anexos e documentos anexos ao Edital;
- editor rico, blocos arbitrários, listas, incisos, ênfase, histórico editorial e colaboração;
- criação arbitrária de seções, reordenação livre, macros, templates genéricos e engine de
  documento;
- importação de DOCX ou PDF;
- assinatura eletrônica real e ICP;
- integração com diretório institucional;
- biblioteca de modelos, clonagem e reutilização entre Editais;
- fila, notificação, e-mail, atribuição a pessoa e workflow engine;
- sistema genérico de permissões;
- busca e filtro no painel;
- recolher, resumir ou navegar dentro de uma etapa do assistente;
- event sourcing, diff de rascunho e versionamento editorial;
- refatoração geral e otimização de desempenho sem evidência;
- retrocompatibilidade de esquema ou de catálogo.

## Rastreabilidade com a auditoria

A `006.1` corrigiu os achados 01, 02, 03, 04, 05, 06, 15, 16, 20 e 21. Restaram dezesseis, e os
dezesseis estão cobertos aqui — nenhum a mais:

| Achado | Requisito |
|---|---|
| 07 · `Retificar` abre para quem não pode | FR-026 |
| 08 · Oferece ação e diz que não há ação | FR-023 |
| 09 · Oferece `Submeter` sabendo da recusa | FR-024 |
| 10 · Quatro edições de rascunho idênticas | FR-042 |
| 11 · Nenhum campo obrigatório é marcado | FR-032, FR-033 |
| 12 · Publicar exige digitar UUID | FR-039 |
| 13 · Remover apaga sem perguntar | FR-038 |
| 14 · O campo `Ano` sem estilo | FR-034 |
| 17 · A confirmação mostra a chave interna | FR-041 |
| 18 · Subir na primeira linha não faz nada | FR-035 |
| 19 · A posição de cada linha é invisível | FR-035 |
| 22 · O vínculo com Evento esconde a data | FR-036 |
| 23 · Caráter são duas caixas soltas | FR-037 |
| 24 · Conteúdo nasce "concluída" | FR-040 |
| 25 · O próximo passo não é oferecido | FR-021 |
| 26 · A recusa culpa o campo errado | FR-022 |

Das seis limitações estruturais registradas, esta feature encerra **uma** — "nenhuma noção de
passagem de bastão" (`US5`) — e mexe no perímetro de outra sem mudar sua natureza: o conjunto de
seções cresce e continua fixo (P-003). As quatro restantes — escala do formulário, texto sem
estrutura, ausência de busca e autenticação por seletor — permanecem registradas e fora de escopo.

Os requisitos de `US1`, `US2` e `US3` não vêm da lista de achados: vêm da frase de abertura. São o
que separa um documento correto de um Edital institucional, e são a razão de esta feature existir
em vez de ser um lote de correções.

## Ordem de entrega

Cada linha é uma entrega demonstrável no navegador. A condição de merge é a demonstração, não a
contagem de testes.

| Entrega | O que se abre no navegador |
|---|---|
| 1 | O documento sem `PLANEJADO`, sem `20.0000` e sem UUID no corpo |
| 2 | As três seções institucionais no assistente e no documento, e os três campos do Perfil — juntas, por FR-018 |
| 3 | O fluxo administrativo sem becos, incluindo a recusa que aponta o campo certo |
| 4 | A passagem de bastão depois de submeter e de homologar |
| 5 | Os atritos de operação |

A entrega 1 não toca o snapshot e pode começar imediatamente.

## Instruções para o `/plan`

**Objetivo: chegar à implementação pelo menor caminho.** Não introduzir repositório, serviço, DTO,
value object, command ou interface adicional se a capacidade puder ser implementada de forma
coerente com a arquitetura existente. Não refatorar código que os cenários acima não exijam. Não
generalizar mecanismo introduzido para um único caso. Não implementar extensibilidade para
requisitos fora de escopo. Havendo uma solução simples que atende integralmente os requisitos e uma
mais genérica, usar a simples. Preferir migration direta e regeneração de seed a mecanismo de
compatibilidade.

Três avisos específicos, derivados do que esta spec verificou:

1. **A formatação humana tem um lugar só.** FR-003 e FR-002 vivem no compositor
   (`publicacoes/infrastructure/pdf.py`). Qualquer proposta que resolva legibilidade alterando o
   snapshot, o serializer da forma publicada ou o valor persistido viola P-002 e FR-001.
2. **O catálogo cresce, a natureza dele não.** FR-007 é acrescentar três `Secao` a uma tupla
   declarada. Se a implementação precisar de tabela, migration de estrutura ou tela de gestão de
   seções, o requisito foi lido errado.
3. **Passagem de bastão é uma função de leitura.** FR-028 é derivar um texto do estado e do mapa de
   permissões. Se aparecer modelo, campo persistido ou tabela, P-004 foi violado.

Não há questão de desenho verdadeiramente aberta nesta feature. Todas as capacidades são extensão
de padrões já exercitados no repositório, e é isso que a torna a última da autoria.
