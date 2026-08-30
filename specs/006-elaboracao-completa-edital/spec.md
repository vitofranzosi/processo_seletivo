# Feature Specification: Elaboração Completa do Edital

**Feature Branch**: `006-elaboracao-completa-edital`

**Created**: 2026-08-30

**Status**: Draft

**Input**: Revisão de produto sobre as telas da `002`, verificada contra o repositório: o sistema
amadureceu o que acontece **depois** da publicação antes de fechar a autoria do Edital.

## Contexto

As cinco features anteriores construíram mecanismos corretos na ordem errada. `001` e `002`
entregaram domínio e interface; `003`, `004` e `005` são uma cadeia corretiva em que cada spec
nasceu do limite registrado pela anterior — a `004` ataca a causa que a `003` conteve, a `005`
ataca o que a `004` declarou fora de escopo. Nenhuma das três aprofundou a elaboração.

A medição é direta. A camada de aplicação da Retificação tem 597 linhas
(`publicacoes/application/retificacoes.py`) contra 143 da elaboração
(`editais/application/draft.py`); são 7 endpoints (`publicacoes/api/urls.py:22-28`) contra 1
(`editais/api/urls.py:6`); o domínio do endereçamento nomeia 9 classes de erro
(`publicacoes/domain/changes.py:56-98`), o da elaboração nomeia 2. A elaboração oferece **uma**
operação: `replace_draft`, que apaga e recria todos os Perfis e Eventos a cada gravação
(`editais/application/draft.py:72`, `:109`).

O efeito no produto é que o snapshot normativo conhece exatamente duas coleções de conteúdo —
`profiles` e `schedule` (`publicacoes/application/publish_edital.py:81-90`). Não há etapa
avaliativa, não há cota com significado, não há texto do Edital como dado. O documento que o
sistema produz existe (`publicacoes/infrastructure/pdf.py:220`), é imutável e é servido pela API
pública (`publicacoes/api/views.py:102-116`), mas **nenhuma tela da interface administrativa leva
a ele**, e ele só nasce depois do ato irreversível de publicar.

Há ainda três becos sem saída na jornada, todos verificados:

1. A ação `Novo Processo Seletivo` existe (`interface/urls.py:11`) mas o template só a renderiza
   dentro do bloco `{% empty %}` da lista (`interface/templates/interface/lista.html:68-74`):
   com um Processo cadastrado, ela desaparece.
2. A etapa `Identificação` do assistente é somente leitura, e o próprio código registra o porquê
   — não existe ato de domínio que altere título ou descrição depois da criação
   (`interface/views.py:236-247`, `:275-283`). Uma pendência de título é apresentada como **não
   corrigível**: o sistema aponta um defeito e informa que não há caminho para corrigi-lo.
3. A ordem dos Eventos do Cronograma é persistida (`editais/models/cronograma.py:30-38`) e
   derivada da posição das linhas no POST (`interface/forms.py:97`), mas nenhuma tela permite
   movê-las: só excluir e recriar.

**A fundação não é o problema.** A interface não tem um único `ModelForm`, as views nunca escrevem
em modelos e falam o vocabulário do snapshot canônico, não o das colunas (`interface/views.py:1-6`).
O ponto de extensão da gramática de Retificação é declarativo: uma coleção nova entra acrescentando
sua forma a `COLECOES_COM_CHAVE` (`publicacoes/domain/colecoes.py:18-24`), e a `005` verifica a
coerência estrutural do que está declarado.

Esta feature não conserta a arquitetura. Ela reorienta a arquitetura existente para completar o
objeto central do produto: o Edital em elaboração.

## Clarifications

### Session 2026-08-30

- Q: As Etapas de Avaliação pertencem ao Edital ou a cada Perfil de Vaga? → A: Ao Edital, nesta
  versão. A Constituição admite Perfis com Etapas distintas, mas admitir não é exigir; sem nada
  publicado, mover a coleção depois custa uma migration.
- Q: O conjunto de seções do Edital é fixo ou gerenciável por quem elabora? → A: Fixo. O sistema
  define quais seções existem e em que ordem; quem elabora edita apenas o texto das textuais.
- Q: A prévia fica disponível só na elaboração? → A: Também com o Edital submetido e homologado, com
  origem única de conteúdo — quem homologa e quem publica precisam ver o que decidem.

**Resolvidas por verificação, sem pergunta.** A faixa do percentual: opcional, e quando informado
maior que zero e menor ou igual a cem (FR-030). E o `SC-009`: a demonstração envolve ao menos dois
atores, porque a publicação recusa quem elaborou, homologou e publicou sozinho
(`publicacoes/application/publish_edital.py:275-280`).

## Princípios desta feature

### P-001 — Resultado visível antes de sofisticação

Cada fatia desta feature termina com capacidade demonstrável no navegador. Nenhuma fatia termina em
"infraestrutura pronta". Encontrar uma oportunidade de abstração durante a implementação **não**
autoriza incluí-la nesta spec.

### P-002 — O sistema não está em produção

Não há dado publicado a preservar. É permitido incrementar `SCHEMA_VERSION`
(`shared/canonical.py:7`), alterar a forma do snapshot, recriar seed e fixtures e escrever migration
direta. É proibido introduzir mecanismo de compatibilidade, migração de conteúdo ou versionamento
adicional para dados que não existem.

### P-003 — Os mecanismos consolidados são estendidos, nunca redesenhados

Snapshot canônico, hash, publicação imutável, proveniência, endereçamento por chave estável,
consolidação temporal e PDF publicado imutável permanecem como estão. Coleção nova com entidades
identificáveis entra pelo registro declarativo existente. Qualquer proposta que exija alterar a
gramática de `publicacoes/domain/changes.py` é sinal de que o conceito foi modelado errado.

### P-004 — `replace_draft` permanece

O assistente continua gravando o rascunho pelo mecanismo atual. Command próprio só se justifica se
uma operação desta feature tiver semântica que "salvar o formulário" não expressa. Reordenar não
tem: a ordem viaja como campo do próprio formulário e a gravação existente a persiste.

### P-005 — Cotas são declarativas

Nesta feature, ação afirmativa é conteúdo normativo estruturado que aparece corretamente no
documento. Distribuição, arredondamento, ocupação, remanejamento, classificação por modalidade e
convocação pertencem à jornada do candidato, que está fora de escopo — não há o que calcular sem
candidatos.

### P-006 — Sem sistema de modelos

Ficam fora: biblioteca de modelos de cronograma, de etapas ou de Edital; clonagem; importação;
motor de templates. Primeiro um Edital completo; depois se descobre se reutilização é problema real.

## User Scenarios & Testing *(mandatory)*

### User Story 0 - A jornada principal sem becos sem saída (Priority: P0)

Quem elabora consegue iniciar e retomar o trabalho pelo fluxo principal, sem descobrir rotas ocultas
e sem esbarrar em pendências que o sistema declara incorrigíveis.

**Why this priority**: são três defeitos de exposição sobre capacidades que já existem, mais um ato
de domínio pequeno. É a entrega que muda a percepção do sistema em horas, e a única que não depende
de nenhuma decisão de desenho.

**Independent Test**: com dois Processos cadastrados, criar um terceiro pelo painel, alterar o
título de um Edital em elaboração, mover dois Eventos, salvar, recarregar e abrir o documento de um
Edital já publicado — tudo pela interface.

**Acceptance Scenarios**:

1. **Given** a lista com ao menos um Processo Seletivo, **When** acesso o painel, **Then** a ação
   `Novo Processo Seletivo` continua visível para quem tem permissão.
2. **Given** um Edital em elaboração, **When** abro a etapa `Identificação` e altero o título,
   **Then** a alteração é gravada e nenhuma pendência de identificação aparece como incorrigível.
3. **Given** um Cronograma com três Eventos, **When** movo o terceiro para a primeira posição e
   salvo, **Then** ao recarregar a nova ordem persiste e os identificadores dos Eventos são os
   mesmos de antes.
4. **Given** um Edital publicado, **When** abro seu detalhe administrativo, **Then** há acesso
   direto ao documento publicado.

---

### User Story 1 - Ver o Edital antes de publicar (Priority: P1)

Quem elabora visualiza o documento que está construindo, a qualquer momento, sem executar ato
irreversível.

**Why this priority**: é o que faz o sistema deixar de parecer um gerenciador de estados. E é
condição de trabalho para as histórias seguintes: a partir dela, todo conceito novo — Etapa, cota,
seção — aparece no documento no mesmo dia em que nasce. O caminho está verificado como barato:
`render_edital_pdf(snapshot, content_hash)` é função pura do snapshot
(`publicacoes/infrastructure/pdf.py:220`) e `edital_snapshot(edital)` lê o estado atual do Edital
(`publicacoes/application/publish_edital.py:22`), que em elaboração é o próprio rascunho.

**Independent Test**: alterar o rascunho, visualizar, encontrar a alteração no documento, voltar e
continuar editando — sem que nenhuma Publicação, Revisão ou Documento seja criado.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** aciono `Visualizar Edital` na etapa de Revisão,
   **Then** recebo o documento renderizado a partir do rascunho gravado.
2. **Given** um Edital submetido ou homologado, **When** abro seu detalhe como quem homologa ou
   quem publica, **Then** consigo visualizar o documento antes de decidir.
3. **Given** que visualizei o documento, **When** consulto o estado do Edital, **Then** ele
   permanece no mesmo estado em que estava e nenhuma `Publicacao`, `RevisaoEdital`,
   `VersaoConsolidada` ou `DocumentoPublicado` foi criada.
4. **Given** o documento visualizado, **When** o comparo com o documento publicado logo em seguida
   sem alterações intermediárias, **Then** o conteúdo normativo é equivalente.
5. **Given** o documento visualizado, **When** o examino, **Then** ele se identifica
   inequivocamente como prévia e não exibe declaração de integridade que sugira ato publicado.

---

### User Story 2 - Definir as Etapas de Avaliação (Priority: P1)

Quem elabora define as etapas pelas quais os candidatos serão avaliados, e essa estrutura passa a
compor formalmente o Edital.

**Why this priority**: é a maior ausência do domínio — hoje não existe nenhum vestígio de etapa,
peso ou caráter eliminatório no backend. E é a repetição limpa do padrão que já funciona
(`PerfilVaga` → snapshot → coleção registrada → retificável), o que a torna previsível e valida a
receita que a `US4` reutiliza.

**Independent Test**: criar duas Etapas, reordená-las, salvar, visualizar o documento e encontrá-las
na ordem definida com suas propriedades.

**Acceptance Scenarios**:

1. **Given** o assistente, **When** acesso a etapa `Etapas de Avaliação`, **Then** posso acrescentar,
   editar, remover e reordenar Etapas.
2. **Given** duas Etapas gravadas, **When** movo a segunda para a primeira posição e salvo, **Then**
   a ordem persiste e as chaves estáveis das duas permanecem as mesmas.
3. **Given** uma Etapa vinculada a um Evento do Cronograma, **When** consulto a Etapa, **Then** as
   datas vêm do Evento e não são digitadas outra vez.
4. **Given** Etapas definidas, **When** visualizo o Edital, **Then** elas aparecem no documento na
   ordem definida, com peso, caráter e nota mínima quando informados.
5. **Given** um Edital publicado com Etapas, **When** uma Retificação endereça
   `/stages/id=<chave>/<campo>`, **Then** o mecanismo existente a aceita sem alteração da gramática.

---

### User Story 3 - Declarar as modalidades de reserva de vagas (Priority: P2)

Quem elabora declara as modalidades de concorrência previstas e seu fundamento normativo, e elas
aparecem formalmente no documento.

**Why this priority**: a estrutura de dados já existe inteira — `ModalidadeConcorrencia` e sua
`RegraNormativa` (`editais/models/perfis.py:47-78`) já estão no snapshot com `foundation` e
`percentage` (`publicacoes/application/publish_edital.py:31-49`), `/profiles/*/competitionModalities`
já é coleção com chave declarada (`publicacoes/domain/colecoes.py:18-24`) e o documento **já imprime
fundamento e percentual** (`publicacoes/infrastructure/pdf.py:109-129`). Nada disso precisa nascer.

**Mas a gravação atual destrói o que se configurar, e isso é o miolo desta história.** Três defeitos
encadeados, todos verificados:

1. A modalidade é criada **sem identidade preservada** — `ModalidadeConcorrencia.objects.create` não
   recebe `id`, ao contrário de Perfil e Evento (`editais/application/draft.py:87-92` contra `:72`
   e `:110`). Toda gravação do rascunho troca a identidade das modalidades.
2. Ao salvar **outra** etapa, os Perfis são relidos do banco e reenviados, mas a serialização de
   preservação leva apenas `code` e `name` (`interface/forms.py:166-169`). A `RegraNormativa` some.
3. A leitura da interface tem a mesma perda de origem: as modalidades vêm de uma caixa de texto livre
   no formato `CÓDIGO — Nome` (`interface/forms.py:54-65`,
   `interface/templates/interface/_perfil.html:57-59`).

Na prática: configurar cotas, salvar, ir ao Cronograma e salvar apaga as regras. A história não é
"trocar a caixa de texto por um formulário" — é fechar o ciclo de ida e volta do rascunho sem perda.
O trabalho continua local e pequeno, mas precisa estar declarado.

**Independent Test**: configurar duas modalidades com percentual e fundamento, salvar, ir a outra
etapa, salvar de novo, visualizar o Edital e encontrar tudo intacto com as mesmas identidades — sem
que nenhuma coleção nova entre no snapshot.

**Acceptance Scenarios**:

1. **Given** um Perfil de Vaga, **When** edito suas modalidades de concorrência, **Then** informo
   código, nome, percentual e fundamento normativo em campos próprios, não em texto livre.
2. **Given** modalidades com regra configurada, **When** salvo o Cronograma em seguida e recarrego,
   **Then** as regras continuam lá e as identidades das modalidades são as mesmas de antes.
3. **Given** modalidades configuradas, **When** visualizo o Edital, **Then** elas aparecem no
   documento com percentual e fundamento.
4. **Given** um percentual fora da faixa admissível, **When** salvo pela interface, **Then** a
   gravação é recusada com mensagem que indica onde corrigir — e a recusa vale também para a API,
   porque a interface chama o command sem passar pelo serializer.
5. **Given** um Edital publicado, **When** uma Retificação endereça
   `/profiles/id=<perfil>/competitionModalities/id=<modalidade>/normativeRule/percentage`, **Then**
   o mecanismo existente a aceita sem alteração da gramática.

---

### User Story 4 - Estruturar o conteúdo textual do Edital (Priority: P2)

Quem elabora revisa e complementa as seções textuais do Edital sem redigir do zero aquilo que o
sistema já conhece.

**Why this priority**: é a única história que exige decisão de desenho, e por isso vem por último —
quando o preview já existe e o padrão de conceito novo já foi exercitado duas vezes. É também o que
transforma o resultado de "relatório de configurações" em documento normativo.

**Independent Test**: alterar o texto de uma seção institucional, salvar, visualizar e encontrar a
alteração no documento junto das seções geradas a partir dos dados estruturados.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** acesso a etapa de conteúdo, **Then** vejo as seções
   do Edital em ordem, distinguindo as geradas pelo sistema das editáveis.
2. **Given** uma seção editável, **When** altero seu texto e salvo, **Then** a alteração aparece no
   documento visualizado.
3. **Given** que alterei o Cronograma, **When** visualizo o documento, **Then** a seção
   correspondente reflete o Cronograma atual sem que eu precise sincronizar texto algum.
4. **Given** um Edital publicado, **When** uma Retificação endereça o conteúdo de uma seção
   editável, **Then** é aceita; **When** endereça o conteúdo de uma seção gerada, **Then** é
   recusada, porque aquele conteúdo se retifica no dado que o origina.

---

### Edge Cases

- Reordenar Eventos ou Etapas em duas abas abertas ao mesmo tempo: a gravação continua sob o
  controle de concorrência atual (`editais/application/draft.py:69-70`); a segunda gravação é
  recusada por revisão divergente, não sobrescreve em silêncio.
- Etapa vinculada a um Evento que é removido na mesma gravação: o vínculo não pode sobreviver ao
  Evento.
- Visualizar um Edital sem Perfis, sem Etapas ou sem seções preenchidas: a prévia é gerada assim
  mesmo, exibindo o que existe — visualizar não exige estar pronto para publicar.
- Percentual de modalidade informado com casas decimais além do que a persistência comporta
  (`perfis.py:63-78`, `Decimal(7,4)`).
- Modalidade que hoje perde a identidade a cada gravação passa a preservá-la: rascunhos e seeds
  existentes têm modalidades cujos identificadores nunca foram estáveis, e são regenerados.
- Seção gerada cuja fonte está vazia (nenhuma Etapa definida): a seção não aparece no documento em
  vez de aparecer vazia.

## Requirements *(mandatory)*

### Fluxo principal (US0)

- **FR-001**: A ação `Novo Processo Seletivo` DEVE permanecer disponível a quem tem permissão,
  independentemente de a lista estar vazia.
- **FR-002**: O detalhe administrativo de um Edital publicado DEVE dar acesso ao documento já
  gerado, reutilizando o recurso existente.
- **FR-003**: Eventos do Cronograma DEVEM poder ser movidos para cima e para baixo na interface,
  preservando a identidade de cada Evento.
- **FR-004**: A nova ordem DEVE ser persistida pelo mecanismo atual de gravação do rascunho.
- **FR-005**: NÃO DEVE ser criado endpoint ou command de reordenação enquanto a operação for
  corretamente expressa pela gravação existente.
- **FR-006**: Título e descrição do Edital DEVEM poder ser alterados enquanto o Edital estiver em
  elaboração, por ato de domínio auditável.
- **FR-007**: Nenhuma pendência de publicação DEVE ser apresentada como não corrigível quando a
  etapa correspondente do assistente permitir corrigi-la.

### Prévia do documento (US1)

- **FR-008**: A etapa de Revisão DEVE oferecer ação visível `Visualizar Edital`. A mesma ação DEVE
  estar disponível no detalhe do Edital enquanto ele estiver submetido ou homologado, para que quem
  homologa e quem publica vejam o documento antes de decidir. *A publicação exige ao menos dois
  atores (`publicacoes/application/publish_edital.py:275-280`); decidir sobre um documento sem
  poder lê-lo esvaziaria a segregação de funções.*
- **FR-009**: A prévia DEVE ser produzida a partir do estado gravado do Edital, em qualquer dos três
  estados. NÃO DEVE existir uma segunda origem de conteúdo: depois da submissão o rascunho não é
  editável e a publicação já recusa divergência entre rascunho e revisão homologada
  (`publicacoes/application/publish_edital.py:282-285`), de modo que a origem única basta.
- **FR-010**: A prévia DEVE reutilizar o pipeline de composição e renderização já existente; NÃO
  DEVE existir um segundo layout independente para prévia e publicado.
- **FR-011**: Visualizar NÃO PODE alterar o estado do Edital nem criar Publicação, Revisão, Versão
  Consolidada ou Documento Publicado.
- **FR-012**: O usuário DEVE poder retornar da prévia e continuar editando.
- **FR-013**: Publicar imediatamente após a prévia, sem alterações intermediárias, DEVE produzir
  documento com conteúdo normativo equivalente ao visualizado.
- **FR-014**: A prévia DEVE se identificar inequivocamente como prévia, em **todas as páginas**, e
  NÃO PODE exibir declaração de integridade — hash, número de publicação, afirmação de derivação de
  versão homologada ou equivalente — que a faça passar por documento publicado. O arquivo entregue
  DEVE ser nomeado como prévia. *Não se impede alguém de imprimir; impede-se que o impresso passe
  por edital. O renderizador hoje afirma derivação de versão homologada e carimba o SHA-256 no
  rodapé de cada página (`publicacoes/infrastructure/pdf.py:220-230`): é essa afirmação que não pode
  sair de uma prévia.*
- **FR-015**: A distinção entre prévia e documento publicado DEVE ser um modo explícito do
  renderizador, e não condicionais espalhadas pela composição. *Um único parâmetro; a exigência é
  que exista um lugar onde a diferença esteja declarada.*

### Etapas de Avaliação (US2)

- **FR-016**: O assistente DEVE ter uma etapa própria para Etapas de Avaliação.
- **FR-017**: DEVE ser possível acrescentar, editar, remover e reordenar Etapas.
- **FR-018**: Cada Etapa DEVE possuir chave estável, independente da posição.
- **FR-019**: Uma Etapa DEVE registrar nome, ordem, caráter eliminatório e caráter classificatório,
  podendo ter ambos quando a regra do certame permitir.
- **FR-020**: Peso e nota mínima DEVEM ser opcionais.
- **FR-021**: Uma Etapa PODE referenciar um Evento existente do Cronograma; quando referencia, suas
  datas vêm do Evento e NÃO DEVEM ser digitadas de novo.
- **FR-022**: A referência a Evento DEVE apontar para Evento existente do mesmo Edital.
- **FR-023**: As Etapas pertencem ao Edital e valem para todos os seus Perfis; DEVEM integrar o
  snapshot canônico publicado como coleção única. *A Constituição admite que Perfis possuam Etapas
  distintas, e admitir não é exigir. Nada está publicado, então mover a coleção para dentro do
  Perfil depois custa uma migration e um caminho de snapshot — preço que se paga quando houver um
  Edital real que precise disso, e não antes.*
- **FR-024**: A coleção de Etapas DEVE ser declarada como coleção com chave estável no registro
  existente, e ser endereçável pela Retificação sem alteração da gramática.
- **FR-025**: As Etapas DEVEM aparecer na prévia e no documento publicado.

### Modalidades de reserva (US3)

- **FR-026**: O assistente DEVE permitir configurar zero ou mais modalidades de concorrência por
  Perfil de Vaga, em campos próprios — código, nome, percentual e fundamento normativo — e NÃO DEVE
  continuar exigindo texto livre com separador convencionado.
- **FR-027**: A gravação do rascunho DEVE preservar a identidade de cada modalidade, como já
  preserva a de Perfis e Eventos.
- **FR-028**: A gravação de qualquer etapa DEVE preservar integralmente as modalidades e suas regras
  normativas; salvar o Cronograma NÃO PODE apagar o que foi configurado nos Perfis.
- **FR-029**: Identificador de modalidade recebido na gravação DEVE ser recusado quando pertencer a
  outro Perfil ou a outro Edital, pela mesma verificação que hoje protege Perfis e Eventos.
- **FR-030**: Percentual é opcional; quando informado, DEVE ser maior que zero e menor ou igual a
  cem. *Modalidade sem reserva percentual exprime-se pela ausência da regra, não por zero por
  cento — que afirmaria uma reserva de nenhuma vaga.* A faixa DEVE ser validada **no domínio**, não
  apenas no serializer da API nem no formulário: a interface chama o command diretamente e não
  atravessa o serializer. NÃO DEVE ser validada soma de percentuais entre modalidades — modalidades
  de reserva não somam cem por cento, e a regra de composição pertence à jornada do candidato.
- **FR-031**: A configuração DEVE aparecer na prévia e no documento publicado. *O renderizador já
  imprime fundamento e percentual; o requisito é de cobertura, não de trabalho novo.*
- **FR-032**: A configuração DEVE permanecer endereçável pela Retificação pelo caminho já existente,
  sem coleção nova no snapshot.
- **FR-033**: NENHUMA consequência operacional sobre candidatos DEVE ser implementada. Os campos de
  cálculo, arredondamento, distribuição e convocação hoje existentes e não utilizados permanecem
  intocados e fora da interface.

### Conteúdo textual (US4)

- **FR-034**: O Edital DEVE possuir uma estrutura ordenada de seções, cada uma com chave estável,
  título, ordem e tipo. **O conjunto de seções e a ordem entre elas são definidos pelo sistema**;
  quem elabora edita o texto das seções textuais e NÃO acrescenta, remove nem reordena seções. *É o
  que separa um documento institucional estruturado de um construtor de documentos.*
- **FR-035**: DEVEM existir exatamente dois tipos nesta versão: seção **gerada**, cujo conteúdo vem
  dos dados estruturados, e seção **textual**, cujo conteúdo é redigido por quem elabora.
- **FR-036**: Conteúdo gerado NÃO PODE ser persistido como texto duplicado; a seção gerada declara
  a que dado corresponde e é renderizada a partir dele.
- **FR-037**: O sistema PODE fornecer texto inicial institucional para as seções textuais, por seed
  ou padrão, e quem elabora DEVE poder alterá-lo antes da publicação.
- **FR-038**: As seções DEVEM integrar o snapshot publicado e a prévia e o documento DEVEM respeitar
  sua ordem.
- **FR-039**: Seções textuais DEVEM ser retificáveis por identidade estável. *A identidade é um
  UUID, e não a chave textual do catálogo: o seletor da gramática só aceita UUID
  (`publicacoes/domain/changes.py:101-113`). A chave textual viaja no item, legível, mas não
  endereça.*
- **FR-040**: Cada conteúdo normativo DEVE ter uma única fonte. Uma seção gerada NÃO PODE carregar
  conteúdo próprio no snapshot: carrega chave, título, ordem e a indicação do dado que a origina.
  *A razão é semântica, não de restrição de banco — a proveniência é única por `(versão, caminho)`
  (`publicacoes/models_retificacao.py:93-104`) e dois caminhos distintos não a violariam. O que se
  evita é a divergência: retificar `/schedule/id=…/startAt` deixaria `/sections/id=…/content`
  desatualizado, e não haveria como dizer qual dos dois vigora. **A regra não precisa de recusa
  nova na gramática**: sem campo de conteúdo, endereçá-lo já falha pelo erro de caminho inexistente
  que a `004` implementou.*

- **FR-041**: A topologia das seções DEVE ser preservada depois da publicação. A verificação de
  publicação DEVE recusar conteúdo em que uma seção tenha sido acrescentada ou removida, em que
  `type`, `order`, `title`, `key` ou origem divirjam do catálogo, em que uma seção textual esteja
  sem conteúdo, ou em que uma seção gerada tenha conteúdo. *Só o texto das seções textuais varia.
  A forma declarada não alcança isto — ela verifica um campo por vez — e sem a verificação o
  catálogo fixo valeria na elaboração e deixaria de valer exatamente onde mais importa, depois de
  publicado.*

### Revisão e publicação

- **FR-042**: A Revisão DEVE consolidar o que está pronto e o que está pendente, indicando para cada
  pendência a etapa onde ela se resolve e oferecendo acesso direto.
- **FR-043**: As validações de publicação existentes DEVEM ser ampliadas apenas para os novos dados
  obrigatórios; NÃO DEVE ser criado framework de regras.
- **FR-044**: A publicação DEVE permanecer disponível somente quando as invariantes já definidas
  forem satisfeitas.

### Snapshot e versão canônica

- **FR-045**: A feature incrementa `SCHEMA_VERSION` uma única vez, cobrindo as coleções novas.
- **FR-046**: Toda coleção nova de entidades identificáveis DEVE ser declarada nos registros
  existentes de coleções com chave e de forma publicada. A suíte DEVE falhar quando uma coleção
  presente no snapshot não estiver declarada nos dois — *essa cobertura não existe hoje: a
  conferência da forma publicada é feita contra uma lista nomeada item a item
  (`tests/contract/test_forma_publicada.py:67-70`), e criá-la é trabalho desta feature.*
- **FR-047**: A versão canônica registrada em uma materialização DEVE corresponder à versão do
  conteúdo materializado. Hoje a Publicação de Retificação carimba a constante global
  (`publicacoes/application/retificacoes.py:564`) sobre conteúdo consolidado a partir de uma
  Publicação-base, que carrega sua própria `schemaVersion`
  (`publicacoes/application/publish_edital.py:84`); depois do incremento as duas podem divergir. A
  consolidação DEVE recusar conteúdo-base cuja versão difira da vigente. *Isto é uma verificação e
  uma recusa, não uma estratégia: uma comparação e um teste.*
- **FR-048**: NÃO DEVE ser introduzido mecanismo de migração, conversão ou compatibilidade entre
  versões de esquema. Não há conteúdo publicado a preservar; seeds e fixtures são regenerados. *A
  alternativa — converter v1 em v2 — construiria, para um único registro de demonstração, a máquina
  que a `P-002` proíbe.*

### Key Entities

- **Etapa de Avaliação**: fase pela qual os candidatos passam. Chave estável, nome, ordem, caráter
  eliminatório, caráter classificatório, peso opcional, nota mínima opcional, referência opcional a
  Evento do Cronograma. Pertence ao Edital; sua forma no domínio — entidade do agregado Edital, à
  maneira de `PerfilVaga` — é decisão do `plan`, não desta spec.
- **Seção do Edital**: unidade ordenada do documento normativo. Chave estável, título, ordem, tipo
  (gerada ou textual) e, quando textual, conteúdo. Seção gerada referencia o dado estruturado que a
  origina e não guarda cópia dele.
- **Modalidade de Concorrência** e **Regra Normativa**: já existem. Esta feature lhes dá esquema,
  interface e presença no documento; não cria conceito paralelo.

## Success Criteria *(mandatory)*

- **SC-001**: Um usuário inicia um novo Processo Seletivo pelo painel mesmo quando já existem
  outros.
- **SC-002**: Um usuário elabora e salva um Edital com identificação, perfis, cronograma, Etapas,
  modalidades e conteúdo textual sem sair do assistente.
- **SC-003**: Um usuário altera a ordem de Eventos e de Etapas sem excluir e recriar itens, e as
  identidades são preservadas.
- **SC-004**: Um usuário visualiza o documento antes da publicação.
- **SC-005**: A prévia reflete o estado gravado do rascunho.
- **SC-006**: Publicar logo após a prévia, sem alterações, produz documento de conteúdo normativo
  equivalente.
- **SC-007**: O documento publicado permanece imutável e a prévia não produz nenhum registro
  publicado.
- **SC-008**: Etapas, modalidades e seções textuais publicadas são endereçáveis pelo mecanismo
  existente de Retificação, sem alteração da gramática de endereçamento.
- **SC-009**: A jornada completa é demonstrável pela interface administrativa, sem manipulação de
  banco, chamada manual de API ou shell: **Painel → Novo Processo → Identificação → Perfis →
  Cronograma → Etapas → Modalidades → Conteúdo → Revisão → Prévia → Submissão → Homologação →
  Publicação → documento publicado.** A demonstração envolve **ao menos dois atores**, porque a
  publicação é recusada quando uma única pessoa elabora, homologa e publica
  (`publicacoes/application/publish_edital.py:275-280`); dois bastam, já que a recusa exige a
  coincidência das três funções. Este é o critério emblemático da feature.

## Assumptions

- A interface permanece server-rendered com fragmentos, como na `002`; nenhuma dependência nova de
  frontend é introduzida.
- Geração síncrona do documento é suficiente no volume atual; não há trabalho em segundo plano.
- A ordem das Etapas, como a dos Eventos, é derivada da posição das linhas na gravação do rascunho.
- O texto institucional inicial das seções pode ser genérico nesta versão; adequá-lo à redação do
  Cefor é trabalho editorial, não desta feature.
- Papéis e permissões existentes bastam; nenhum fluxo novo de autorização é criado.

## Out of Scope

Desta feature inteira, e sem exceção:

- inscrição, candidato, comissão, banca, avaliação, lançamento de notas, recursos, classificação e
  convocação;
- motor de cotas — distribuição, arredondamento, ocupação, remanejamento;
- critérios, rubricas, planilhas de avaliação, fórmulas e dependência entre Etapas;
- Etapas distintas por Perfil de Vaga, admitidas pela Constituição e adiadas nesta versão;
- acrescentar, remover ou reordenar seções do Edital;
- modelos reutilizáveis, clonagem, importação e engine de templates;
- criar Edital adicional em Processo já existente, que permanece disponível apenas pela API;
- editor rico, blocos arbitrários, histórico editorial, comentários, colaboração simultânea;
- assinatura eletrônica real;
- substituição geral de `replace_draft` e qualquer refatoração não exigida pelos cenários acima;
- otimização de desempenho sem evidência;
- retrocompatibilidade com dados de produção inexistentes.

## Ordem de entrega

Cada linha é uma entrega demonstrável no navegador. A condição de merge é a demonstração, não a
contagem de testes.

| Entrega | O que se abre no navegador |
|---|---|
| 1 | `Novo Processo` sempre visível, identificação editável, reordenar Eventos, link para o documento publicado |
| 2 | `Visualizar Edital` antes da publicação |
| 3 | Etapas de Avaliação no assistente e no documento |
| 4 | Modalidades de reserva com esquema, ida e volta sem perda, e presença no documento |
| 5 | Seções textuais, jornada completa do `SC-009` |

A entrega 1 não depende de nenhuma decisão de desenho e deve começar antes que a `US4` esteja
resolvida.

## Instruções para o `/plan`

**Objetivo: chegar à implementação pelo menor caminho.** Não introduzir repositório, serviço, DTO,
value object, command ou interface adicional se a capacidade puder ser implementada de forma
coerente com a arquitetura existente. Não refatorar código que os cenários acima não exijam. Não
generalizar mecanismo introduzido para um único caso. Não implementar extensibilidade para
requisitos fora de escopo. Havendo uma solução simples que atende integralmente os requisitos e uma
mais genérica, usar a simples. Preferir migration direta e regeneração de seed a mecanismo de
compatibilidade. As tarefas preservam a ordem das entregas acima e cada conjunto termina em cenário
navegável.

A única questão de desenho verdadeiramente aberta é a `US4`: como o Edital é simultaneamente dado
estruturado e documento legível. As demais são replicação de padrões já exercitados no repositório.
