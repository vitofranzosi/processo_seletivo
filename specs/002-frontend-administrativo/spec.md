# Feature Specification: Interface Administrativa de Processos Seletivos e Editais

**Feature Branch**: `002-frontend-administrativo`

**Created**: 2026-08-28

**Status**: Draft

**Input**: Interface administrativa para os servidores do Cefor conduzirem Processos Seletivos e Editais, cobrindo os requisitos diferidos da feature `001-processo-seletivo-editais` (FR-037 e SC-002/009/010). Autenticação por LDAP institucional. A consulta pública permanece fora deste incremento.

## Clarifications

### Session 2026-08-28

- Q: O frontend atende quem? → A: Somente o público administrativo. A consulta pública de Editais
  permanece atendida pela API e será objeto de especificação futura, se houver decisão nesse
  sentido. Candidatos seguem fora do produto.
- Q: Como será a autenticação institucional? → A: Diretório LDAP do Ifes.
- Q: Qual norma de acessibilidade vincula a interface? → A: Ambas — eMAG 3.1, por ser órgão público
  federal, e WCAG 2.1 nível AA, por ser a referência corrente. Onde divergirem, prevalece a
  exigência mais restritiva.
- Q: O LDAP também autoriza, ou é preciso gestão de papéis nesta feature? → A: A opção mais simples:
  grupos do LDAP correspondem a papéis de responsabilidade, e cada papel reúne um conjunto fixo de
  permissões definido na configuração do sistema. Não há tela de gestão de papéis neste incremento.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entrar e Enxergar o Próprio Trabalho (Priority: P1)

Como servidor do Cefor, quero entrar com minha conta institucional e ver imediatamente os Processos
e Editais sob minha responsabilidade, com a situação de cada um e o que depende de mim, para saber
onde continuar sem procurar.

**Why this priority**: Sem identificação e sem lista não existe interface — todo o resto depende de
saber quem é a pessoa e o que ela pode alcançar. É também o único item que substitui o adaptador de
desenvolvimento hoje em uso, onde qualquer pessoa se declara quem quiser.

**Independent Test**: Pode ser testada autenticando duas pessoas com permissões diferentes e
verificando que cada uma enxerga apenas o que lhe cabe, e que ações sem permissão não são oferecidas.

**Acceptance Scenarios**:

1. **Given** um servidor com conta institucional válida, **When** informa suas credenciais,
   **Then** o sistema o identifica, apresenta seu nome e escopo institucional e lista os Processos
   Seletivos do seu escopo com a situação de cada um.
2. **Given** credenciais inválidas ou conta inativa, **When** a pessoa tenta entrar, **Then** o
   acesso é negado com mensagem compreensível, sem revelar se o usuário existe.
3. **Given** um servidor autenticado sem permissão de publicar, **When** visualiza um Edital
   homologado, **Then** a ação de publicar não é oferecida e, se tentada por outro caminho, é
   recusada com explicação.
4. **Given** um servidor autenticado, **When** sua sessão expira, **Then** o sistema informa a
   expiração, preserva o que estava sendo preenchido e permite reautenticar sem perder o trabalho.

---

### User Story 2 - Montar um Edital sem Assistência (Priority: P1)

Como elaborador autorizado, quero criar o Processo Seletivo com seu primeiro Edital e preencher
Perfis de Vaga e Cronograma numa sequência guiada, para produzir um Edital completo sem precisar
consultar quem já conhece o sistema.

**Why this priority**: É o trabalho mais volumoso e mais sujeito a erro do fluxo, e o que SC-002 e
SC-009 mediram como critério de sucesso da interface.

**Independent Test**: Pode ser testada pedindo a alguém que nunca usou o sistema que monte um Edital
com dois Perfis e três Eventos, sem ajuda, medindo o tempo e os erros.

**Acceptance Scenarios**:

1. **Given** um servidor com permissão de criar, **When** informa a identificação institucional do
   Processo e os dados do primeiro Edital, **Then** ambos são criados e a interface conduz ao passo
   seguinte, indicando o que ainda falta.
2. **Given** um Edital em elaboração, **When** o servidor adiciona um Perfil de Vaga, **Then** pode
   informar denominação, requisitos, vagas imediatas, Cadastro Reserva e Modalidades de
   Concorrência, com as opções incompatíveis impedidas antes do envio.
3. **Given** um Perfil que admite somente Cadastro Reserva ilimitado, **When** essa opção é
   escolhida, **Then** a interface deixa de exigir quantidade de vagas imediatas.
4. **Given** um Cronograma em preenchimento, **When** o servidor informa um período cujo início é
   posterior ao término, **Then** a inconsistência é apontada no próprio campo, antes do envio.
5. **Given** um Edital em elaboração com dados incompletos, **When** o servidor interrompe o
   trabalho e retorna depois, **Then** encontra o que havia preenchido e o que ainda falta.

---

### User Story 3 - Conduzir o Edital até a Publicação (Priority: P1)

Como servidor participante do fluxo, quero submeter, homologar e publicar um Edital enxergando em
cada etapa quem já atuou, o que está pendente e o que a próxima ação provoca, para que o ato
institucional seja praticado com consciência das suas consequências.

**Why this priority**: É onde a interface deixa de ser conveniência e passa a ter efeito jurídico.
FR-037 nasceu exatamente aqui: operações irreversíveis exigem confirmação e consequências
inequívocas.

**Independent Test**: Pode ser testada percorrendo o fluxo com três pessoas distintas e verificando
que cada uma vê o estado correto, que a confirmação precede cada ato irreversível e que a segregação
de funções é comunicada antes de ser imposta.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração completo, **When** o elaborador o submete, **Then** a interface
   apresenta os avisos e informações produzidos pela validação, separados dos erros impeditivos, e
   permite prosseguir ciente deles.
2. **Given** um Edital com erro impeditivo, **When** a submissão é tentada, **Then** os erros são
   apresentados de forma acionável, cada um ligado ao campo ou seção correspondente.
3. **Given** um Edital homologado, **When** um servidor autorizado solicita a Publicação, **Then** a
   interface apresenta, antes de confirmar, o que será publicado, quem assina, e o aviso de que o
   ato é irreversível e só admite correção por Retificação.
4. **Given** que a mesma pessoa elaborou e homologou o Edital, **When** ela tenta publicar, **Then**
   a interface explica a exigência de segregação de funções antes da tentativa, e não apenas depois
   da recusa.
5. **Given** um Edital publicado, **When** o servidor o abre, **Then** a interface deixa evidente que
   o conteúdo é imutável e oferece a Retificação como caminho de correção.

---

### User Story 4 - Retificar com Clareza do Efeito (Priority: P2)

Como elaborador autorizado, quero preparar uma Retificação enxergando o conteúdo vigente ao lado da
alteração proposta e a data em que passará a valer, para não publicar mudança diferente da pretendida.

**Why this priority**: A Retificação é a operação mais difícil de compreender do domínio — altera
conteúdo por caminho, tem vigência própria e compõe cumulativamente com outras. Sem apoio visual, o
risco de erro é alto; mas ela só é alcançada depois que existe Edital publicado.

**Independent Test**: Pode ser testada preparando uma Retificação sobre um Edital publicado e
verificando que a interface mostra o antes e o depois de cada alteração e o instante em que passa a
vigorar.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** o servidor inicia uma Retificação, **Then** a interface
   apresenta o conteúdo vigente e permite indicar o que muda, exibindo o valor anterior ao lado do
   novo.
2. **Given** uma Retificação com data futura de vigência, **When** o servidor a revisa, **Then** a
   interface informa explicitamente a partir de quando o novo conteúdo passa a valer e o que
   continua vigente até lá.
3. **Given** uma Retificação cujo conteúdo base foi alterado por outra publicada no intervalo,
   **When** a publicação é tentada, **Then** a interface explica o conflito e oferece retomar a
   elaboração sobre a versão atual.
4. **Given** uma Retificação que não altera nada, **When** o servidor tenta submetê-la, **Then** a
   interface aponta a ausência de efeito antes da submissão.

---

### User Story 5 - Registrar o Desfecho (Priority: P2)

Como gestor autorizado, quero encerrar ou cancelar Processos e Editais informando o motivo, e
enxergar o que impede um desfecho quando ele não é possível, para concluir formalmente sem
tentativa e erro.

**Why this priority**: Completa o ciclo de vida e é operação irreversível, mas de frequência baixa e
posterior às demais.

**Independent Test**: Pode ser testada tentando cancelar um Processo com Edital em aberto e
verificando que a interface identifica quais Editais impedem o ato e conduz a resolvê-los.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com etapas concluídas, **When** o gestor registra o encerramento
   com motivo, **Then** a interface distingue visualmente o encerramento regular do cancelamento e
   confirma que o histórico permanece disponível.
2. **Given** um Processo com Editais ainda não finalizados, **When** o gestor tenta cancelá-lo,
   **Then** a interface lista os Editais que impedem o ato e permite alcançá-los diretamente.
3. **Given** qualquer ato de encerramento ou cancelamento, **When** o gestor confirma, **Then** a
   interface exige o motivo e apresenta as consequências antes de efetivar.

---

### User Story 6 - Consultar a Trilha de Auditoria (Priority: P3)

Como servidor autorizado a auditar, quero consultar quem praticou cada ato, quando e por quê, para
responder questionamentos internos e externos sobre um Processo Seletivo.

**Why this priority**: Necessária para a responsabilização institucional, mas de uso pontual e
independente do fluxo de trabalho diário.

**Independent Test**: Pode ser testada filtrando a trilha por um Edital e verificando que cada ato
registrado aparece com ator, instante, situação anterior e posterior e motivo.

**Acceptance Scenarios**:

1. **Given** um servidor com permissão de auditoria, **When** consulta a trilha de um Edital,
   **Then** vê os atos em ordem cronológica com ator, momento, transição e motivo.
2. **Given** um servidor sem essa permissão, **When** tenta alcançar a trilha, **Then** o acesso é
   negado e a funcionalidade não é oferecida na navegação.

### Edge Cases

- Sessão expira durante o preenchimento de um Edital longo: o trabalho não preenchido ainda não é do
  domínio e não pode ser perdido silenciosamente.
- Duas pessoas editam o mesmo rascunho simultaneamente: a segunda precisa ser informada de que
  trabalha sobre versão obsoleta, sem perder o que digitou.
- A pessoa perde uma permissão enquanto tem uma tela aberta: a ação deixa de ser oferecida e a
  tentativa é recusada com explicação, não com erro genérico.
- Conexão cai no meio de um ato irreversível: a interface precisa deixar claro se o ato ocorreu,
  sem induzir a repetição que produziria efeito duplicado.
- Um Edital com dezenas de Perfis e Eventos: a interface precisa permanecer navegável e permitir
  encontrar um item específico.
- Servidor autenticado sem nenhuma permissão administrativa: recebe orientação sobre a quem
  solicitar acesso, em vez de uma tela vazia.
- Conteúdo com acentuação, aspas e parênteses em campos livres: precisa ser preservado em tela e no
  documento publicado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A interface DEVE autenticar servidores contra o diretório institucional LDAP e
  identificar a pessoa autenticada em toda a sessão.
- **FR-002**: A interface DEVE obter as permissões da pessoa autenticada e oferecer somente as
  ações que ela pode praticar, sem que a ocultação substitua a verificação no backend.
- **FR-003**: A interface DEVE apresentar a lista de Processos Seletivos e Editais do escopo
  institucional da pessoa, com situação atual e identificação institucional visíveis.
- **FR-004**: A interface DEVE permitir criar um Processo Seletivo com seu primeiro Edital numa
  única operação, deixando claro que ambos são criados juntos.
- **FR-005**: A interface DEVE permitir compor Perfis de Vaga com denominação, descrição,
  requisitos, vagas imediatas, Cadastro Reserva e Modalidades de Concorrência.
- **FR-006**: A interface DEVE impedir, antes do envio, combinações que o domínio recusa, como
  Cadastro Reserva limitado sem quantidade ou período com início posterior ao término.
- **FR-007**: A interface DEVE permitir compor o Cronograma com eventos pontuais e períodos,
  apresentando as datas na zona temporal institucional.
- **FR-008**: A interface DEVE indicar, a qualquer momento da elaboração, o que ainda falta para o
  Edital poder ser submetido.
- **FR-009**: A interface DEVE apresentar os achados de validação classificados em erro impeditivo,
  aviso e informação, ligando cada um ao ponto do Edital a que se refere.
- **FR-010**: A interface DEVE apresentar confirmação explícita, com as consequências do ato, antes
  de submissão, homologação, revogação de homologação, Publicação, Retificação, encerramento e
  cancelamento. *(atende FR-037 diferido da feature 001)*
- **FR-011**: A confirmação de ato irreversível DEVE identificar o que será afetado e declarar que a
  operação não pode ser desfeita.
- **FR-012**: A interface DEVE apresentar, em cada Edital, quem elaborou, quem homologou e quem
  publicou, e comunicar a exigência de segregação de funções antes da tentativa de um ato vedado.
- **FR-013**: A interface DEVE tornar evidente que um Edital publicado é imutável e oferecer a
  Retificação como caminho de correção.
- **FR-014**: A interface DEVE permitir compor uma Retificação apresentando o conteúdo vigente ao
  lado da alteração proposta.
- **FR-015**: A interface DEVE apresentar a data de vigência de uma Retificação e o que permanece
  vigente até ela.
- **FR-016**: A interface DEVE explicar conflitos de concorrência — versão obsoleta, conteúdo
  alterado no intervalo, ato sem efeito prático — em linguagem compreensível, oferecendo o caminho
  de correção.
- **FR-017**: A interface DEVE permitir registrar encerramento e cancelamento com motivo, e
  distinguir visualmente conclusão regular de interrupção administrativa.
- **FR-018**: Quando um desfecho for impedido, a interface DEVE identificar o que o impede e
  permitir alcançar diretamente cada pendência.
- **FR-019**: A interface DEVE permitir consultar a trilha de auditoria por Edital a quem tiver
  autorização, apresentando ator, instante, transição e motivo.
- **FR-020**: A interface DEVE preservar o conteúdo em preenchimento diante de expiração de sessão
  ou falha de comunicação, permitindo retomar sem redigitação.
- **FR-021**: A interface DEVE informar o resultado de todo ato praticado, distinguindo sucesso,
  recusa por regra de domínio e falha de comunicação.
- **FR-022**: A interface NÃO DEVE apresentar detalhes internos de falha, identificadores técnicos
  sem significado institucional, nem credenciais.
- **FR-023**: Todos os fluxos DEVEM ser concluíveis por teclado, com ordem de navegação lógica e
  mensagens de erro associadas programaticamente aos campos. *(atende SC-010 diferido)*
- **FR-024**: A interface DEVE atender simultaneamente ao eMAG 3.1 e ao WCAG 2.1 nível AA. Onde
  as normas divergirem, DEVE prevalecer a exigência mais restritiva.
- **FR-025**: A conformidade de acessibilidade DEVE ser verificável por avaliação automatizada nos
  fluxos críticos e por inspeção manual dos critérios que a automação não cobre, como ordem de
  leitura, texto alternativo significativo e comportamento com leitor de tela.
- **FR-026**: As permissões da pessoa autenticada DEVEM ser derivadas dos grupos que ela possui no
  diretório institucional, por meio de papéis de responsabilidade que reúnem conjuntos fixos de
  permissões. A interface NÃO DEVE oferecer gestão de papéis neste incremento.
- **FR-027**: Um papel DEVE representar responsabilidade, não cargo: a mesma pessoa PODE acumular
  papéis, e nenhum papel DEVE ser inferido de função ou lotação.
- **FR-028**: Quando a pessoa autenticada não possuir nenhum papel reconhecido, a interface DEVE
  informar isso de forma compreensível e orientar a quem solicitar acesso, em vez de apresentar uma
  área vazia.

### Key Entities *(include if feature involves data)*

Esta feature não introduz conceitos novos de domínio. Ela apresenta os conceitos já estabelecidos em
[`001-processo-seletivo-editais`](../001-processo-seletivo-editais/spec.md): Processo Seletivo,
Edital, Perfil de Vaga, Vaga, Modalidade de Concorrência, Regra Normativa, Cronograma, Evento de
Cronograma, Publicação, Retificação, Versão de Edital e Registro de Auditoria.

Dois conceitos são próprios da interface:

- **Sessão do Servidor**: a identificação autenticada e suas permissões durante o uso, com validade
  própria e encerramento explícito.
- **Rascunho Local**: o conteúdo digitado que ainda não foi enviado ao domínio. Não é fonte
  normativa e não substitui o rascunho estruturado do Edital; existe apenas para que trabalho em
  andamento não se perca.
- **Papel de Responsabilidade**: conjunto nomeado e fixo de permissões, correspondente a um grupo do
  diretório institucional. Representa responsabilidade assumida, não cargo ou lotação. As
  responsabilidades que o fluxo da feature 001 já distingue são: elaborar, homologar, publicar,
  gerir o ciclo de vida de Processos e Editais, auditar e operar. Uma pessoa pode acumular papéis,
  e a segregação de funções continua sendo imposta pelo domínio, não pelo papel.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um servidor autorizado conclui a estruturação de um Processo Seletivo com primeiro
  Edital e ao menos um Perfil, sem assistência externa, em até 15 minutos. *(SC-002 diferido da
  feature 001)*
- **SC-002**: Ao menos 90% dos representantes administrativos concluem corretamente, na primeira
  tentativa, os cenários de criar Edital, configurar Perfil e Cronograma e submeter à validação.
  *(SC-009 diferido)*
- **SC-003**: 100% dos fluxos críticos são concluíveis exclusivamente por teclado, com erros
  textuais compreensíveis e sequência lógica de navegação. *(SC-010 diferido)*
- **SC-004**: 100% das operações irreversíveis apresentam confirmação com consequências antes de
  serem efetivadas. *(FR-037 diferido)*
- **SC-005**: 100% das recusas do domínio são apresentadas em linguagem compreensível, sem
  identificador técnico nem detalhe interno de falha.
- **SC-009**: Os fluxos críticos não apresentam violação de eMAG 3.1 nem de WCAG 2.1 nível AA em
  avaliação automatizada, e passam em inspeção manual de ordem de leitura, texto alternativo e
  operação por leitor de tela.
- **SC-006**: Nenhuma ação para a qual a pessoa não tem permissão é oferecida na interface, e 100%
  das tentativas por caminho alternativo são recusadas pelo backend.
- **SC-007**: Em teste com trabalho em andamento, 100% do conteúdo preenchido é recuperável após
  expiração de sessão ou queda de conexão.
- **SC-008**: Nenhum fluxo crítico exige mais de uma tentativa por causa de mensagem ambígua, medido
  por observação de uso com representantes do Cefor.

## Assumptions

- **A autenticação usa o diretório LDAP do Ifes.** Foi a decisão informada para esta feature. O
  backend hoje usa um adaptador de desenvolvimento — `Bearer <pessoa>|<escopo>|<permissões>` — que
  **não** é fronteira de segurança e precisa ser substituído por esta integração.
- **A autorização deriva de grupos do diretório, agrupados em papéis.** Foi escolhido o caminho mais
  simples que funciona: um punhado de grupos, e não dezessete, porque pedir ao administrador do
  diretório que mantenha um grupo por permissão seria operacionalmente custoso e propenso a erro. O
  mapa de papel para permissões vive na configuração do sistema e é versionado com ele.
- **Consequência aceita dessa escolha**: conceder ou revogar acesso passa a depender do
  administrador do diretório, sem autoatendimento na interface. É adequado enquanto o número de
  servidores envolvidos for pequeno; se a operação crescer ou exigir delegação, uma gestão de papéis
  própria deverá ser especificada em incremento futuro.
- Esta feature atende **somente o público administrativo**: servidores do Cefor que conduzem
  Processos e Editais. A consulta pública de Editais permanece disponível apenas pela API e será
  objeto de especificação futura, se houver decisão institucional nesse sentido.
- Candidatos não são usuários desta interface. Inscrição, envio de documentos, recursos e
  acompanhamento de resultado seguem fora do escopo do produto, como na feature 001.
- O backend da feature 001 é a única fonte de verdade normativa. A interface não reimplementa regra
  de domínio, não decide autorização e não persiste conteúdo normativo por conta própria; validação
  em tela existe para prevenir erro, nunca como fronteira de segurança.
- Os contratos administrativos existentes em `001-processo-seletivo-editais/contracts/openapi.yaml`
  atendem às necessidades desta interface. Lacunas identificadas durante o planejamento serão
  tratadas como evolução daquele contrato, não como regra nova na interface.
- O uso ocorre em computador institucional com navegador atual. Uso em dispositivo móvel não é
  requisito deste incremento.
- O idioma da interface é o português do Brasil, e as datas seguem a zona temporal institucional
  `America/Sao_Paulo`, como já ocorre no domínio.

## Out of Scope

- Consulta pública de Editais por cidadãos, que hoje é atendida pela API pública.
- Qualquer funcionalidade destinada a candidatos.
- Gestão de contas e de senhas, que pertence ao diretório institucional.
- Tela de gestão de papéis e atribuição de permissões a pessoas. A concessão de acesso ocorre no
  diretório institucional, por decisão registrada nas clarificações.
- Assinatura eletrônica real do documento publicado, mantida fora de escopo como na feature 001.
- Relatórios gerenciais e indicadores sobre Processos Seletivos.

## Dependencies

- Feature `001-processo-seletivo-editais` implantada e acessível, incluindo os endpoints
  administrativos e a trilha de auditoria.
- Acesso ao diretório LDAP institucional e criação dos grupos correspondentes aos papéis de
  responsabilidade, acordada com quem administra o diretório. Sem esses grupos, nenhuma pessoa
  possui permissão e o sistema fica inutilizável — ver FR-028.
- Substituição do adaptador de autenticação de desenvolvimento do backend por autenticação
  institucional. **Esta dependência bloqueia a entrega em produção**, ainda que não bloqueie o
  desenvolvimento das telas.
