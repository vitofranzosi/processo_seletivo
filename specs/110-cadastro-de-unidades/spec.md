# Feature Specification: Cadastro de unidades administrado pela aplicação

**Feature Branch**: `claude/110-cadastro-de-unidades`

**Created**: 2026-10-31

**Status**: Especificada, planejada e revista em 31/10/2026 sobre a `main` com a `108` e a `109`
integradas; a direção e as decisões revistas foram aprovadas pelo usuário no mesmo dia. Três
incrementos (D-019); a implementação começa pelo A.

**Input**: o pedido de 31/10/2026, "GPS — Spec SDD: Administração institucional do cadastro de
unidades", com as oito decisões de produto aprovadas, sobre a
[revisão arquitetural de 30/10](../../doc/revisao-arquitetural-multiunidade-2026-10-30.md).

> **Faixa de identificadores.** Esta spec abre em **FR-3301** e **SC-1041**. O teto medido em
> 31/10/2026 na `main`, nas branches abertas e nas worktrees é o requisito três mil duzentos e
> vinte e um e o critério mil e trinta e cinco, os dois da `109`. **Nenhum `UX-` é aberto aqui.** As
> decisões técnicas reiniciam em `D-001` e moram no `research.md`; as pendências de produto são
> `P-`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-1108 da `060`"). A `108` e a `109` são citadas pelo assunto porque esta spec foi escrita antes
> do merge delas; desde 31/10 estão na `main`, e a citação pelo assunto continua válida. Decisão de
> outra feature pelo assunto e pelo número por extenso.

---

## Por que esta feature existe

A `060` criou o registro de Unidades e decidiu que ele seria declarado num arquivo versionado,
`unidades.json`, aplicado ao banco por um comando de sincronização. A razão escrita foi que a tela
de administração *"pediria papel central, que não existe"*. A `106` e a `107` criaram esse papel: o
Administrador institucional de acessos, concedido só pela implantação, com sessão institucional e
trilha por pessoa.

A revisão de 30/10 achou dois defeitos no arquivo como fonte oficial:

1. **Entrar um campus é commit, PR e deploy.** O critério de expansão — incorporar unidade sem
   alteração de código específica de cada campus — não se cumpre.
2. **O arquivo sobrescreve o banco.** A sincronização roda em toda subida do contêiner e em todo
   `ps-migrar`, grava no banco o que o arquivo diz e recusa unidade do banco ausente do arquivo. Uma
   correção no banco é desfeita no deploy seguinte; uma unidade criada no banco impede a subida.

A revisão também achou uma lacuna de integridade: o escopo de um Processo ou de um Edital pode ser
mudado depois de criado, por uma alteração direta, sem que nada recuse.

### O que esta spec cobre, e o que fica fora

**Entra:**

- o banco como fonte oficial, e o arquivo como semente que só se aplica a um registro vazio;
- a permissão `unidade:administrar`, no papel institucional que já existe, que passa a se chamar
  Administrador institucional;
- consultar, cadastrar, editar, desativar e reativar unidade pela gestão, com prévia do cabeçalho,
  motivo, confirmação e histórico;
- a proteção, no banco, do escopo de Processo e de Edital;
- testes de isolamento nas áreas que a revisão achou sem segunda unidade;
- uma entrada de homologação, só fora de produção, para que pessoas validem as telas antes do SSO.

**Fica fora, de propósito** (pedido de 31/10, §8):

- SSO real do Ifes; credenciais e servidor de correio; supervisão transversal dos campi;
  Edital de mais de uma unidade; importação em lote; catálogo editável de papéis; chave
  estrangeira no lugar das referências textuais; qualquer alteração de ato publicado;
- o cadastro de autoridades signatárias, que a `060` já entrega e não muda;
- módulo administrativo genérico e o Django Admin;
- as decisões P-1, P-2 e P-7 da `109` (§Pendências de produto).

---

## Decisões de produto (31/10/2026)

Aprovadas pelo usuário no pedido, e tomadas aqui como premissa:

1. O PostgreSQL é a fonte oficial do cadastro de unidades.
2. O `unidades.json` fica só como semente de instalação, sem autoridade sobre registro existente.
3. Quem administra é o Administrador institucional — o papel da `106` e da `107`, renomeado —, pela
   permissão nova `unidade:administrar`.
4. Nenhuma unidade altera o próprio cadastro nesta versão.
5. Cadastro, alteração, desativação e reativação exigem motivo e trilha.
6. A Reitoria pode ser cadastrada como unidade emissora. Supervisão transversal fica fora.
7. Unidade não se exclui, e código não muda.
8. As publicações históricas continuam imutáveis.

**A decisão 3 passou por duas revisões em 31/10, e voltou ao papel existente.** Um papel próprio
para o registro foi proposto por menor privilégio e recusado pelo usuário: não há exigência
institucional que peça a separação, e ela custaria um segundo papel e um segundo mecanismo de
designação. O que ficou da revisão é a regra de que **nenhum privilégio real se amplia em
silêncio**: antes do deploy, a migração verifica quem já tem o papel e pede autorização expressa se
houver alguém (D-002). E `sincronizar_unidades` fica, por ora, como apelido compatível.

**Regra fixada pelo usuário para o GPS**: toda abstração, papel, tabela ou mecanismo novo precisa
resolver um problema concreto, e não uma possibilidade futura.

---

## Dependências

| PR | Spec | O que esta feature usa | Estado em 31/10/2026 |
|---|---|---|---|
| #349 | `109` | o campo `atendimento` da Unidade, sua validação, e o resolvedor de identificação, que lê o registro a cada pedido | **integrado** (`81ce6e94`) |
| #348 | `108` | a trilha da unidade, que lê os eventos `REGISTRAR_UNIDADE` e `ALTERAR_UNIDADE` no escopo da unidade, e a tradução deles em palavras, inclusive o canal de atendimento | **integrado** (`cf048007`); o rótulo do canal veio na integração das duas (`25460040`) |

Os contratos foram reconferidos na `main` em `81ce6e94` (§Verificação de dependência no
[plan](plan.md)). A primeira tarefa de cada incremento os reconfere na `main` do dia.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Cadastrar uma unidade pela aplicação (Priority: P1)

O Administrador institucional recebe da Reitoria o pedido de incorporar o Campus Serra. Ele abre
"Unidades", escolhe "Cadastrar unidade", informa código, sigla, nome, as linhas do cabeçalho, o
local, o canal de atendimento e o motivo, confere a prévia do cabeçalho como o documento oficial o
imprimirá e confirma. Na requisição seguinte, ele concede o Administrador de acessos da nova
unidade, e a unidade passa a operar — sem commit, PR ou deploy.

**Why this priority**: é o critério de sucesso do pedido.

**Independent Test**: com o Cefor registrado, cadastrar `serra` pela tela; conceder a ela o
Administrador de acessos; criar um Processo como gestor dela; conferir que o arquivo não mudou.

**Acceptance Scenarios**:

1. **Given** o Administrador institucional, com escopo ativo institucional, **When** ele preenche o
   formulário e pede a conferência, **Then** vê a prévia do cabeçalho, o local, os campos e o aviso
   de que o código não poderá mudar, e nada foi gravado.
2. **Given** a conferência sem erro, **When** ele confirma, **Then** a unidade existe ativa, os três
   modelos iniciais de aviso existem nela, e a trilha da unidade tem um registro com ele, o motivo e
   os valores.
3. **Given** a unidade recém-cadastrada, **When** ele abre a concessão de Administrador de acessos,
   **Then** ela está entre as unidades oferecidas.
4. **Given** o código `institucional`, um código com maiúscula ou espaço, ou um código já
   registrado, **When** ele confere, **Then** recebe a recusa no campo, e nada é gravado.

---

### User Story 2 — Editar sem que a implantação desfaça (Priority: P1)

O Cefor muda o nome de exibição e passa a ter canal de atendimento próprio. O administrador do
registro edita a unidade, confere o antes e o depois e a prévia, e confirma. Uma semana depois
há um deploy: o nome e o canal continuam os novos.

**Why this priority**: sem isto a tela é desfeita na implantação seguinte, que é o defeito central.

**Independent Test**: editar o nome do Cefor pela tela; rodar a semente e o roteiro de inicialização;
conferir os campos e a ausência de evento novo.

**Acceptance Scenarios**:

1. **Given** o Cefor registrado, **When** o administrador muda nome e canal e confere, **Then** vê o
   antes e o depois de cada campo mudado e a prévia com o nome novo.
2. **Given** a edição confirmada, **When** a semente roda, **Then** ela diz que o registro já existe
   e não grava nada, e o nome e o canal continuam os novos.
3. **Given** um Edital publicado antes da edição, **When** alguém abre o documento ou a página do
   ato, **Then** o cabeçalho é o do dia da publicação.
4. **Given** duas pessoas editando a mesma unidade, **When** a segunda confirma depois da primeira,
   **Then** a segunda recebe a recusa de que a unidade mudou desde a conferência, e nada dela é
   gravado.

---

### User Story 3 — Desativar e reativar (Priority: P1)

Um campus deixa de ofertar seleções pelo GPS. O Administrador institucional o desativa, com motivo,
lendo antes as consequências. O certame em curso ali termina normalmente. Um ano depois, o campus
volta, e ele o reativa.

**Why this priority**: é o único modo de retirar uma unidade, porque nada se exclui.

**Independent Test**: com um Processo em curso em `serra`, desativar `serra`; tentar criar Processo e
conceder acesso nela (recusados); conduzir o Edital em curso (aceito); reativar; criar Processo
(aceito).

**Acceptance Scenarios**:

1. **Given** uma unidade ativa, **When** o administrador pede para desativá-la, **Then** a tela diz
   que ela não receberá Processo, Edital nem acesso novo, e que certames, acessos e autoridades
   existentes continuam.
2. **Given** a desativação confirmada, **When** um gestor da unidade tenta criar Processo, **Then**
   recebe a recusa de unidade desativada; **and when** ele conduz um Edital já existente, **Then** o
   ato é aceito.
3. **Given** a unidade desativada, **When** o administrador a reativa com motivo, **Then** a criação
   de Processo volta a ser aceita.
4. **Given** uma unidade já desativada, **When** alguém pede para desativá-la de novo (por envio
   montado à mão), **Then** recebe a recusa, e nada é gravado.

---

### User Story 4 — Consultar o registro e o histórico (Priority: P2)

O Administrador institucional vê todas as unidades, ativas e desativadas, e abre a ficha de uma
para ver os dados, a prévia do cabeçalho e o histórico administrativo — inclusive o que a
implantação gravou antes desta feature.

**Why this priority**: governança e rastreabilidade; depende das histórias 1 a 3 para ter o que
mostrar.

**Independent Test**: com eventos da implantação e de pessoa na trilha, abrir a ficha e conferir a
ordem, os autores ("Implantação" e o nome), os motivos e o antes→depois.

**Acceptance Scenarios**:

1. **Given** duas unidades, uma desativada, **When** o administrador abre "Unidades", **Then** vê as
   duas, com a situação de cada uma.
2. **Given** a ficha do Cefor, **When** ela abre, **Then** o histórico mostra o registro pela
   implantação e as alterações seguintes, mais recentes primeiro.
3. **Given** um código que não está registrado, **When** alguém abre a ficha dele, **Then** recebe a
   página não encontrada.

---

### User Story 5 — A semente: instalação nova e instalação existente (Priority: P1)

A TI instala o GPS num servidor novo: o preparo do banco registra o Cefor a partir do arquivo. Numa
instalação que já tem unidades, o mesmo passo não muda nada e não falha, mesmo com unidades que o
arquivo não conhece.

**Why this priority**: é a transição; sem ela há duas fontes.

**Independent Test**: em banco vazio, rodar o preparo e conferir o Cefor e os três modelos; num banco
com `cefor` editado e `serra` cadastrada pela tela, rodar o preparo e o roteiro de inicialização
duas vezes e conferir que nada mudou e nada falhou.

**Acceptance Scenarios**:

1. **Given** um registro vazio, **When** a semente roda, **Then** registra as unidades do arquivo,
   com trilha da implantação, e cria os modelos iniciais.
2. **Given** um registro com qualquer unidade, **When** a semente roda, **Then** não grava nada e diz
   quantas unidades o registro tem e que a semente não se aplica.
3. **Given** uma unidade no banco ausente do arquivo, **When** o contêiner sobe, **Then** a subida
   termina normalmente.

---

### User Story 6 — Escopo imutável e isolamento comprovado (Priority: P1)

Um Edital nunca muda de unidade. E as áreas da gestão que ainda não tinham teste com segunda unidade
passam a ter.

**Why this priority**: integridade do isolamento, que esta feature torna mais exercitado ao facilitar
a entrada de unidades.

**Independent Test**: tentar mudar o escopo de um Processo e de um Edital por alteração direta, com
a role de runtime; conferir a recusa do banco. Rodar os testes de isolamento novos.

**Acceptance Scenarios**:

1. **Given** um Processo e um Edital do Cefor, **When** algo tenta gravar outro escopo neles, **Then**
   o banco recusa, e os dois continuam do Cefor.
2. **Given** um ator de `campus-a`, **When** ele pede, por identificador, um objeto do Cefor nas
   áreas de ocupação, recurso, requerimento ou API administrativa, **Then** recebe a mesma resposta
   de objeto inexistente, e nada é gravado.

---

### User Story 7 — Validar as telas com pessoas antes do SSO (Priority: P2)

Antes de a feature ser dada por aceita, uma pessoa da equipe opera as telas num ambiente de
homologação funcional, isolado e só com dado sintético: entra pela entrada institucional, como uma
das pessoas que a implantação cadastrou nele, e cadastra, edita, desativa e reativa uma unidade
seguindo um roteiro, sem ajuda.

**Why this priority**: o teste automatizado prova as regras, e não que a tela serve a quem a usa; sem
o SSO, só esta entrada leva uma pessoa às telas (D-017).

**Independent Test**: no ambiente da D-018 — settings de desenvolvimento, o provedor de
homologação, o seletor desligado —, seguir o roteiro G do [quickstart](quickstart.md). É critério de
aceite humano (SC-1048), e não teste automatizado.

**Acceptance Scenarios**:

1. **Given** o ambiente de homologação funcional e uma pessoa cadastrada pela implantação com o
   papel de Administrador institucional, **When** quem valida a escolhe na página do provedor, **Then**
   chega à gestão no escopo institucional e vê "Unidades".
2. **Given** um retorno do provedor repetido, ou sem o estado da ida, **When** ele chega à gestão,
   **Then** a entrada é recusada e nenhuma pessoa é criada, como com qualquer adaptador.
3. **Given** as settings de produção com o provedor de homologação configurado, **When** o serviço
   sobe, **Then** ele recusa subir, nomeando a variável.

---

### Edge Cases

Cada caso aqui é requisito, e tem linha própria na [matriz](rastreabilidade.md).

- **EC-1 — Código com caixa ou espaço.** "Serra", " serra" e "campus serra" são recusados no campo,
  com a regra dita; o sistema não converte por conta própria, porque o código é permanente.
- **EC-2 — Duas pessoas cadastram o mesmo código ao mesmo tempo.** Uma unidade é criada; a outra
  confirmação recebe "código já registrado", e nada dela é gravado.
- **EC-3 — Edição que não muda nada.** Recusada na conferência, sem evento: um evento sem mudança
  diria que algo mudou.
- **EC-4 — Edição que só muda espaços em volta.** Os valores são aparados antes da comparação; se
  aparados forem iguais, é o EC-3.
- **EC-5 — Desativar a única unidade ativa.** Permitido: nada se exclui, e a reativação devolve. A
  moldura passa a dizer só a instituição, pela regra provisória da `109` (P-1).
- **EC-6 — Desativar unidade com Edital publicado e prazo aberto.** Permitido; o certame segue. A
  tela diz quantos Processos não encerrados a unidade tem antes da confirmação.
- **EC-7 — Ato que muda a moldura das superfícies sem unidade.** Cadastrar ou reativar a segunda
  ativa ("Cefor/Ifes" → "Ifes"), desativar até sobrar uma ou nenhuma, e mudar a sigla da única ativa
  mudam o que o portal, a página de acesso, a 404 e o código de acesso dizem (regra provisória da
  `109`). A confirmação diz isso, porque é efeito visível ao candidato.
- **EC-8 — Administrador institucional com escopo ativo numa unidade.** As telas recusam como sem
  permissão: a capacidade é do escopo institucional, como na administração de acessos.
- **EC-9 — Envio forjado com código numa edição.** O código enviado é ignorado; a unidade é a da
  rota. Se o envio tentar outro código por campo extra, nada muda nele.
- **EC-10 — Sessão de demonstração.** Recusada antes de qualquer leitura do registro, mesmo que um
  papel do seletor um dia ganhe a permissão.
- **EC-11 — Arquivo-semente malformado num registro vazio.** A semente recusa sem gravar, com a
  recusa nomeada, e a subida falha — é arquivo do repositório, e a falha alta é a certa. Num
  registro não vazio, o arquivo não é lido.
- **EC-12 — Canal de atendimento apagado na edição.** Permitido: a unidade volta a usar o canal
  institucional, pela regra da `109`.
- **EC-13 — Reitoria cadastrada.** É uma unidade como as outras: código, cabeçalho, local, próprias
  autoridades. Não ganha leitura sobre os campi.
- **EC-14 — Autoridade de unidade desativada.** Continua editável pelo gestor da unidade, como a
  `060` decidiu: o certame em curso precisa de quem assine.
- **EC-15 — Teste que precisa de Edital de outra unidade.** Cria-o com um ator da outra unidade; não
  move um existente (é o que o gatilho passa a recusar).
- **EC-16** — *retirado em 31/10/2026, com o papel próprio que o motivava (D-002). O número fica
  reservado.*
- **EC-17 — Roteiro instalado com o nome anterior do comando.** O `ps-migrar` ou o `entrypoint.sh`
  de uma cópia antiga chama `sincronizar_unidades`: a semente roda, a subida termina, e o aviso do
  nome anterior fica no *log*.
- **EC-18 — Tentativa de conceder o papel institucional pela tela.** Recusada como papel que só a
  implantação concede, como a `106` já faz, e nada é gravado: a permissão nova não abre esse
  caminho.

---

## Requirements *(mandatory)*

### Functional Requirements

**Fonte oficial e semente**

- **FR-3301**: O registro de Unidades no banco MUST ser a fonte oficial dos dados das unidades.
  Nenhum passo de preparo, migração, inicialização ou implantação MUST alterar ou recusar uma
  unidade registrada.
- **FR-3302**: A semente de instalação MUST registrar as unidades do arquivo somente quando o
  registro estiver vazio. Com qualquer unidade registrada, MUST NOT gravar unidade nem evento de
  unidade, e MUST dizer na saída quantas unidades o registro tem e que a semente não se aplica.
- **FR-3303**: A semente MUST NOT falhar, nem impedir a inicialização, porque o banco tem unidade
  ausente do arquivo, ou porque os valores do arquivo diferem dos do banco.
- **FR-3304**: Quando se aplica, a semente MUST validar o arquivo inteiro pela mesma regra do
  cadastro pela aplicação antes de gravar qualquer coisa, e MUST gravar cada unidade com trilha da
  implantação, como hoje.
- **FR-3305**: A semente MUST ser idempotente, e MUST continuar garantindo os modelos iniciais de
  aviso de cada unidade registrada que nunca os teve.
- **FR-3306**: O preparo local, a inicialização do contêiner e o roteiro de migração de produção MUST
  chamar a semente pelo nome novo. O comportamento de sincronização MUST deixar de existir: não há
  segundo caminho que escreva no registro. O nome anterior do comando MUST continuar aceito, como
  apelido da semente, com o mesmo efeito e o mesmo código de saída, e MUST avisar, fora da saída
  que o guia ensina a ler, que é o nome anterior.
- **FR-3307**: A documentação operacional MUST descrever a semente, a linha que ela imprime, que
  editar o arquivo depois da instalação não tem efeito, o apelido e o critério para retirá-lo, e como
  que a administração de unidades é do Administrador institucional, designado pela implantação.

**Permissão e governança**

- **FR-3308**: A permissão `unidade:administrar` MUST pertencer ao papel institucional que já existe,
  o `administrador-institucional`, e só a ele, que passa a se chamar "Administrador institucional".
  MUST NOT pertencer a papel de unidade, nem a papel do seletor de demonstração. Nenhum papel,
  modelo, tabela, tela de designação ou mecanismo de concessão novo MUST ser criado.
- **FR-3309**: Todo ato e toda leitura do registro por esta feature MUST exigir
  `unidade:administrar` com o escopo ativo institucional, conferidos na camada de aplicação; a tela
  é a segunda barreira, e não a primeira.
- **FR-3310**: `unidade:administrar` MUST NOT conferir nenhuma outra capacidade — Processo, Edital,
  Publicação, autoridades, modelos de aviso, acessos de unidade. O papel continua concedido,
  retirado e substituído só pelos comandos de implantação que já existem (FR-3029 da `106`, FR-3147
  e FR-3148 da `107`), sem mudança neles. Antes do deploy, todo vínculo vigente desse papel MUST ser
  identificado, e a ampliação MUST NOT chegar a quem o tem sem autorização expressa do usuário.
- **FR-3311**: Ator com escopo ativo de unidade, com qualquer papel, MUST receber a recusa em todo
  ato sobre o registro, inclusive sobre a própria unidade.
- **FR-3312**: Só a entrada institucional MUST alcançar as telas desta feature; a sessão de
  demonstração MUST receber a recusa antes de qualquer leitura, como na gestão de acessos
  (FR-3127 da `107`).
- **FR-3313**: Todo ato MUST exigir motivo preenchido, e MUST registrar quem o praticou (pelo
  identificador interno da pessoa), quando, o motivo, e o valor anterior e o posterior de cada campo
  mudado.

**Consultar**

- **FR-3314**: A lista de unidades MUST mostrar todas as unidades registradas, ativas e desativadas,
  com sigla, nome, código, local e situação, por sigla.
- **FR-3315**: A ficha de uma unidade MUST mostrar todos os campos, a prévia do cabeçalho e o
  histórico administrativo dela — registros, alterações, desativações e reativações —, mais recentes
  primeiro, com quem (pelo nome, ou "Implantação"), quando, o motivo e o antes e o depois.
  Código não registrado MUST responder como página não encontrada.

**Cadastrar**

- **FR-3316**: Cadastrar MUST pedir código, sigla, nome, uma ou duas linhas de cabeçalho, local,
  canal de atendimento opcional e motivo. A unidade MUST nascer ativa.
- **FR-3317**: O código MUST ter só letras minúsculas, dígitos e hífen, sem hífen nas pontas nem
  duplo; MUST NOT ser o código reservado ao escopo institucional; e MUST ser único. A conferência
  MUST dizer que o código não poderá ser mudado depois.
- **FR-3318**: Sigla, nome e local MUST ser preenchidos; o cabeçalho MUST ter uma ou duas linhas
  preenchidas; o canal, quando informado, MUST ser uma linha só, no limite que a `109` fixou. A
  mesma regra MUST valer para o cadastro, a edição e a semente — uma regra só.
- **FR-3319**: O cadastro MUST criar, no mesmo ato, os modelos iniciais de aviso da unidade, uma vez
  só.
- **FR-3320**: A unidade cadastrada MUST estar disponível, na requisição seguinte e sem reinício,
  para: a concessão do Administrador de acessos dela; a criação de Processo e Edital por quem atue
  nela; o cadastro de autoridades pelo gestor dela; e a identificação nas molduras e mensagens.

**Editar**

- **FR-3321**: Editar MUST permitir mudar sigla, nome, cabeçalho, local e canal de atendimento, e
  MUST NOT oferecer nem aceitar mudança do código.
- **FR-3322**: Edição sem nenhuma mudança, depois de aparados os espaços das pontas, MUST ser
  recusada sem gravar.
- **FR-3323**: Editar MUST NOT alterar publicação, documento, página de ato ou mensagem já
  confirmada; o próximo ato da unidade é que sai com os dados novos.

**Prévia e confirmação**

- **FR-3324**: Antes de confirmar cadastro ou edição, a tela MUST mostrar o cabeçalho nas linhas
  que o documento oficial imprime — as da instituição e as da unidade —, a sigla como o anúncio do
  ato a imprime, o local do fecho, e, na edição, o antes e o depois de cada campo mudado; e MUST
  avisar quando uma linha do cabeçalho não couber numa linha do documento. Nada MUST ser gravado
  antes da confirmação.
- **FR-3325**: A confirmação MUST reconferir, na camada de aplicação e sob trava da unidade, a
  permissão, a validação e que a unidade não mudou desde a conferência. Se mudou, MUST recusar sem
  gravar e dizer que outra pessoa a alterou.

**Desativar e reativar**

- **FR-3326**: Desativar MUST exigir motivo e uma confirmação que diga as consequências: a unidade
  não recebe Processo, Edital nem acesso novo; Processos, Editais, acessos e autoridades existentes
  continuam; e quantos Processos não encerrados ela tem.
- **FR-3327**: Reativar MUST exigir motivo e devolver à unidade a criação de Processo e Edital e a
  concessão de acesso.
- **FR-3328**: Desativar unidade desativada e reativar unidade ativa MUST ser recusados sem gravar.
- **FR-3329**: Nenhum ato MUST excluir unidade, e nenhuma tela MUST oferecer exclusão.
- **FR-3330**: Quando o ato vai mudar a identificação das telas sem unidade — o número de unidades
  ativas passa a ser, ou deixa de ser, exatamente um; ou muda a sigla da única ativa —, a
  confirmação MUST dizer como ela fica.

**Trilha**

- **FR-3331**: Cada ato MUST gravar um evento no escopo da unidade afetada, sobre a própria unidade,
  com as operações que o registro já usa — registro e alteração, e a desativação e a reativação como
  alteração da situação —, de modo que a trilha da unidade os mostre sem mudança nela.
- **FR-3332**: O ato e o evento MUST ser gravados na mesma transação: sem evento, nada muda.

**Integridade**

- **FR-3333**: O banco MUST recusar a mudança do escopo de Processo Seletivo e de Edital depois de
  criados, inclusive por alteração direta e por qualquer papel, sem retirar privilégio que hoje
  exista.
- **FR-3334**: O banco MUST continuar recusando mudar o código e excluir a unidade (FR-1108 e
  FR-1109 da `060`).
- **FR-3335**: Os testes que simulam objeto de outra unidade MUST criá-lo na outra unidade, e não
  mover um existente.

**Isolamento**

- **FR-3336**: MUST existir teste com duas unidades em cada uma destas áreas: apuração de ocupação e
  acréscimo de vagas; admissibilidade e decisão de recurso; requerimentos de matrícula na gestão; e a
  API administrativa. Em cada uma, o ator de uma unidade, pedindo por identificador um objeto da
  outra, MUST receber a mesma resposta de objeto inexistente, e nada MUST ser gravado.

**Compatibilidade**

- **FR-3337**: Instalação existente MUST conservar o registro exatamente como está, sem migração de
  dado; o Cefor MUST funcionar sem nenhuma ação depois da atualização.
- **FR-3338**: O seletor de demonstração e o `seed_demo` MUST continuar como estão, e a homologação
  com eles MUST continuar funcionando.

**Papel institucional**

- **FR-3339**: A tela MUST continuar recusando conceder ou revogar o papel institucional, como a
  `106` decidiu: a permissão nova não abre esse caminho.
- **FR-3340** — *retirada em 31/10/2026 com o papel próprio (D-002); a suspensão do Administrador
  institucional continua só pela implantação, pela FR-3136 da `107`, sem mudança. O número fica
  reservado.*
- **FR-3341** — *retirada em 31/10/2026 com o papel próprio (D-002). O número fica reservado.*

**Validação antes do SSO**

- **FR-3342**: MUST existir um provedor de homologação para o contrato de autenticação
  institucional da `106`, só no código de teste, construído sobre o provedor simulado e declarado
  de teste, que produção MUST recusar no *boot* e em execução, pelas recusas que já existem
  (FR-3026 da `106`). MUST NOT haver mecanismo criptográfico próprio.
- **FR-3343**: O provedor MUST oferecer só as pessoas cuja identidade externa é dele — as que a
  implantação cadastrou — e MUST devolver à gestão só o bilhete de uso único do provedor simulado;
  a gestão MUST continuar lendo a identidade só do que o adaptador devolve (FR-3022 da `106`) e
  conferindo o estado da ida (FR-3023 da `106`).

### Key Entities

- **Unidade** (existe, `060`): código permanente; sigla, nome, cabeçalho, local, canal de atendimento
  (`109`) e situação, editáveis por esta feature. Nada novo no modelo.
- **Evento da trilha** (existe): o ato, no escopo da unidade, com a pessoa, a permissão, o motivo e o
  antes e o depois.
- **Papel institucional** (existe, `106`): o `administrador-institucional` ganha a permissão
  `unidade:administrar` e passa a se chamar Administrador institucional.
- **Provedor de homologação** (novo, só no código de teste): subclasse do provedor simulado da
  `106`, com uma página que oferece as pessoas cadastradas pela implantação; só fora de produção.
- **Ambiente de homologação funcional** (configuração, não código): separado da VM de homologação,
  com settings de desenvolvimento, dado sintético e perímetro restrito (D-018).
- **Semente** (substitui a sincronização): o arquivo do repositório, lido só para registro vazio.

---

## Pendências de produto

Ficam identificadas, e **não** se resolvem por suposição aqui. Nenhuma bloqueia a implementação.
P-1 a P-4 precisam de resposta antes da entrada efetiva da segunda unidade ativa; P-5, antes do
deploy do incremento C num ambiente em que alguém já tenha o papel; P-6, antes de uma sessão de
validação fora de `localhost`.

| # | Origem | Pergunta | Comportamento enquanto não respondida |
|---|---|---|---|
| **P-1** | P-1 da `109` | Com mais de uma unidade ativa, o que portal, página de acesso, 404 e código de acesso dizem? | "Ifes" sozinho; a confirmação avisa (FR-3330) |
| **P-2** | P-2 da `109` | Qual é a política de atendimento — o Cefor declara canal no registro, que forma ele tem, quem atende a conta do candidato? | o canal é opcional, e a recaída é o institucional |
| **P-3** | P-7 da `109` | A área do candidato numa inscrição, o resultado e o sorteio trocam a moldura pela unidade do Edital? | a moldura da implantação |
| **P-4** | P1 da `108` | Quem audita o nível institucional? | os atos desta feature ficam no escopo da unidade, e o auditor de cada unidade os lê; o ator institucional não tem quem o leia como conjunto |
| **P-5** | esta feature (D-002) | Num ambiente em que já haja Administrador institucional designado, essas pessoas devem passar a administrar também as unidades? | o deploy do incremento C não se faz ali sem a resposta; em 31/10 nenhum banco local tinha o papel, produção não estava instalada e a VM de homologação estava por conferir |
| **P-6** | esta feature (D-017, D-018) | O ambiente de homologação funcional, com settings de desenvolvimento, pode ser acessível além da máquina de quem conduz — numa rede fechada, com o perímetro da D-018? É a decisão que o §10.3 do guia de produção nomeia | só `localhost` |

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1041**: Uma unidade nova passa de inexistente a operável — cadastrada, com administrador de
  acessos, com um Processo criado por quem atua nela — com zero alterações no repositório, zero
  deploys e zero comandos no servidor.
- **SC-1042**: Em 100% dos casos exercitados, rodar a semente e o roteiro de inicialização depois de
  cadastrar e de editar pela aplicação deixa o registro idêntico, campo a campo, e não grava evento
  de unidade.
- **SC-1043**: Zero caminhos — tela, envio montado à mão, chamada direta ao caso de uso — pelos quais
  quem não tem `unidade:administrar` no escopo institucional altere o registro.
- **SC-1044**: 100% dos atos sobre o registro têm evento com a pessoa, o motivo e o antes e o depois;
  zero atos sem evento.
- **SC-1045**: Zero publicações anteriores a uma edição com qualquer byte mudado no documento ou no
  conteúdo publicado.
- **SC-1046**: Cadastrar uma unidade se faz em até três telas — lista, formulário, conferência —, e
  editar, desativar ou reativar, em até três a partir da lista.
- **SC-1047**: A suíte existente passa contra PostgreSQL sem mudar resultado esperado, com três
  exceções nomeadas: os testes da sincronização, substituídos pelos da semente; o teste da agenda
  que movia um Edital de unidade, que passa a criá-lo na outra; e o teste de vínculos que importa a
  validação da sincronização, que passa a importá-la do domínio. Os testes dos comandos de
  implantação e da suspensão da `107` passam sem mudança.
- **SC-1048** *(critério de aceite humano, não teste automatizado)*: Na validação funcional, uma
  pessoa da equipe que não escreveu a feature cadastra, edita, desativa e reativa uma unidade no
  ambiente de homologação funcional, seguindo o roteiro G, sem ajuda; e confirma que a prévia
  corresponde ao cabeçalho de um documento gerado depois. Registrado no `verificacao.md` com a data,
  quem validou e o que estranhou; a feature não é dada por aceita sem ele, e nenhum resultado de
  suíte o substitui.

---

## Assumptions

- A `109` e a `108` entram na `main` antes da implementação, com os contratos descritos em
  §Dependências.
- A equipe inicial é de duas a três pessoas, e não há exigência institucional de separar quem
  administra acessos de quem administra unidades: as duas responsabilidades são do Administrador
  institucional (D-002).
- Os dados de unidade são institucionais e públicos — aparecem em todo documento oficial. O canal
  de atendimento deve ser um canal institucional, e não o contato pessoal de um servidor; a tela o
  diz na ajuda do campo (avaliação de LGPD no [research](research.md), D-012).
- O código da unidade é escolhido por quem cadastra, a partir de orientação institucional; o sistema
  só confere o formato e a unicidade.
- A homologação com o seletor de demonstração continua como está, e não alcança esta feature, como
  não alcança a gestão de acessos. A prova automatizada é a jornada no navegador dos testes
  (`make test-navegador`); a validação por pessoas é a da instância controlada com a entrada de
  homologação (D-017, D-018).
- **A VM de homologação e a produção não têm a tela até o SSO**, porque rodam as settings de
  produção e a gestão inteira responde 503 lá (§10.3 do guia). Nenhuma unidade nova pode ser usada
  nelas antes disso, e por isso a troca da fonte não lhes tira nada (D-019).
