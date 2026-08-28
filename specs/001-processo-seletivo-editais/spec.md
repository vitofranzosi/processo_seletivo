# Feature Specification: Processo Seletivo e Editais

**Feature Branch**: `main` *(nenhuma branch específica criada; hook Git não configurado)*

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: `doc/prompt/001-fase-1-speckit-clarify.md`

## Clarifications

### Session 2026-08-27

- Q: A ativação e o encerramento do Processo Seletivo devem ocorrer por ato administrativo
  explícito ou ser derivados da situação de seus Editais? → A: Ativação e encerramento são atos
  administrativos explícitos e auditáveis, independentes das transições dos Editais.
- Q: Quando uma Retificação publicada deve começar a produzir o novo conteúdo vigente do Edital?
  → A: Na Publicação, salvo data futura expressamente declarada; nunca antes da Publicação.
- Q: A mesma pessoa pode elaborar, homologar e publicar um Edital quando possuir todas as
  permissões? → A: Quem elaborou pode submeter, mas ao menos outra pessoa deve homologar ou
  publicar o Edital.
- Q: Quais documentos históricos de um Edital devem permanecer disponíveis na consulta pública?
  → A: O Edital original, todas as Retificações e todas as versões consolidadas históricas.
- Q: O que deve acontecer com os Editais ainda não encerrados quando o Processo Seletivo for
  cancelado? → A: O cancelamento do Processo é bloqueado até que cada Edital esteja encerrado ou
  tenha seu próprio cancelamento registrado.
- Q: O Edital pode assumir o estado Encerrado e como ele se distingue de Cancelado? → A: Sim.
  Encerrado representa a conclusão regular após suas etapas; Cancelado representa interrupção
  administrativa antes da conclusão regular.
- Q: Como determinar a precedência de Retificações publicadas com vigências futuras fora da ordem
  de Publicação? → A: Pela data/hora de início da vigência, de forma temporal e cumulativa; em
  empate e conflito sobre o mesmo conteúdo, prevalece a Retificação publicada por último.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Estruturar Processo Seletivo e Edital (Priority: P1)

Como responsável pela gestão administrativa, quero identificar um Processo Seletivo e estruturar
seu primeiro Edital para que o certame possua contexto institucional e regras próprias claramente
separadas.

**Why this priority**: Processo Seletivo e Edital formam a base de todos os demais fluxos e nenhum
dos elementos posteriores possui contexto válido sem esse vínculo.

**Independent Test**: Pode ser testada criando a estrutura institucional, vinculando-lhe um Edital
e consultando ambos separadamente, demonstrando que suas identidades e situações são independentes.

**Acceptance Scenarios**:

1. **Given** que um usuário autorizado informou a identificação institucional do Processo Seletivo
   e os dados obrigatórios do primeiro Edital, **When** confirma a criação, **Then** o sistema cria
   os dois conceitos com identidades distintas e vincula o Edital a exatamente esse Processo.
2. **Given** um Processo Seletivo existente, **When** um usuário autorizado adiciona outro Edital
   válido, **Then** ambos os Editais permanecem vinculados ao mesmo Processo e conservam situações,
   regras e cronogramas independentes.
3. **Given** dados obrigatórios ausentes ou uma identificação institucional já utilizada no mesmo
   contexto, **When** o usuário tenta confirmar, **Then** o sistema rejeita a operação, identifica
   os problemas e não deixa uma estrutura parcialmente criada.
4. **Given** um Processo em elaboração com ao menos um Edital válido, **When** o gestor autorizado
   registra explicitamente sua ativação, **Then** o Processo torna-se Ativo com auditoria do ato,
   sem alterar automaticamente a situação de seus Editais.

---

### User Story 2 - Configurar Perfis, Vagas e Concorrência (Priority: P1)

Como elaborador autorizado, quero configurar os Perfis de Vaga, suas vagas, Cadastro Reserva e
Modalidades de Concorrência para representar fielmente as oportunidades abrangidas pelo Edital.

**Why this priority**: Perfis e regras de vagas constituem conteúdo normativo essencial para
publicar um Edital útil e não podem ser inferidos posteriormente.

**Independent Test**: Pode ser testada em um Edital em elaboração com múltiplos Perfis, cada qual
com requisitos, vagas e modalidades próprias, verificando que não há compartilhamento indevido.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** o elaborador inclui dois Perfis com características
   diferentes, **Then** o sistema mantém separadamente identificação, denominação, requisitos,
   localidade ou modalidade, vagas e informações de classificação de cada Perfil.
2. **Given** um Perfil que admite somente Cadastro Reserva ilimitado, **When** essa configuração é
   registrada, **Then** o sistema não exige quantidade de vagas imediatas nem limite artificial.
3. **Given** Modalidades de Concorrência aplicáveis a um Perfil, **When** o elaborador registra as
   regras normativas vigentes, **Then** o sistema distingue a regra do resultado de sua aplicação e
   não aplica essa configuração a outro Perfil automaticamente.

---

### User Story 3 - Definir Cronograma Independente (Priority: P1)

Como elaborador autorizado, quero montar o Cronograma próprio de cada Edital para comunicar e
controlar seus eventos e períodos sem interferir nos demais Editais do Processo Seletivo.

**Why this priority**: O Cronograma rege a execução do Edital e sua coerência é condição para uma
publicação válida.

**Independent Test**: Pode ser testada configurando cronogramas diferentes em dois Editais do mesmo
Processo e verificando a independência e a validação temporal de ambos.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** o usuário inclui eventos pontuais e períodos com
   identificação, descrição, ordem e situação, **Then** o Cronograma apresenta todos na sequência
   lógica definida e no contexto exclusivo do Edital.
2. **Given** dois Editais do mesmo Processo, **When** seus Cronogramas recebem datas diferentes,
   **Then** a alteração de um não modifica o outro.
3. **Given** um período cujo início ocorre depois do término, **When** o usuário tenta salvá-lo,
   **Then** o sistema rejeita o período e explica a inconsistência.

---

### User Story 4 - Validar e Publicar Edital (Priority: P1)

Como usuário autorizado a publicar, quero revisar as inconsistências e publicar a versão
homologada do Edital para torná-la um documento institucional íntegro e consultável.

**Why this priority**: A Publicação transforma a configuração em ato institucional e estabelece a
referência normativa para os módulos futuros.

**Independent Test**: Pode ser testada submetendo um Edital completo e outro inconsistente à
validação, comprovando que somente o primeiro gera uma Publicação imutável identificada.

**Acceptance Scenarios**:

1. **Given** um Edital homologado e completo, **When** um usuário autorizado solicita a Publicação,
   **Then** o sistema registra versão, conteúdo, responsável, Autoridade Signatária, cargo ou
   função, data e hora, e disponibiliza o documento correspondente.
2. **Given** um Edital com erro impeditivo, **When** a Publicação é solicitada, **Then** o sistema a
   bloqueia e apresenta os erros separadamente de avisos e informações.
3. **Given** uma versão publicada, **When** alguém tenta modificar diretamente seu conteúdo,
   **Then** o sistema rejeita a alteração e orienta o uso de Retificação.
4. **Given** uma Publicação concluída, **When** o documento é consultado, **Then** seu conteúdo
   corresponde integralmente aos dados e ao conteúdo editorial homologados daquela versão.
5. **Given** que uma pessoa elaborou o Edital, **When** ela tenta concluir sozinha elaboração,
   homologação e Publicação, **Then** o sistema bloqueia a conclusão até que outra pessoa autorizada
   realize a homologação ou a Publicação.

---

### User Story 5 - Retificar sem Reescrever o Passado (Priority: P1)

Como elaborador autorizado, quero preparar e publicar Retificações para alterar qualquer conteúdo
vigente do Edital sem destruir Publicações anteriores.

**Why this priority**: Mudanças normativas são inevitáveis e precisam preservar validade histórica,
autoria e ordem cronológica.

**Independent Test**: Pode ser testada publicando um Edital e duas Retificações sequenciais, depois
reconstruindo o conteúdo vigente após cada ato.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** uma Retificação homologada altera Cronograma, Perfil e
   vagas, **Then** o sistema preserva a versão anterior e registra exatamente quais mudanças foram
   produzidas pelo novo ato.
2. **Given** múltiplas Retificações, **When** o usuário consulta a linha histórica, **Then** o sistema
   apresenta sua ordem cronológica, autoria, efeitos e versões consolidadas correspondentes.
3. **Given** uma Retificação ainda não publicada, **When** o público consulta o Edital, **Then** a
   versão pública vigente permanece inalterada.
4. **Given** uma Retificação publicada com data futura de vigência, **When** uma consulta ocorre
   antes dessa data, **Then** o conteúdo anterior permanece vigente; a partir da data declarada, a
   nova versão passa a vigorar.
5. **Given** que a Retificação A foi publicada antes com vigência posterior à Retificação B,
   **When** a vigência de B começa, **Then** B compõe a versão vigente; quando a vigência de A
   começa, A também passa a compor a consolidação, preservadas as alterações vigentes não
   substituídas.
6. **Given** duas Retificações com o mesmo início de vigência, **When** ambas alteram o mesmo
   conteúdo de formas conflitantes, **Then** prevalece nesse conteúdo a que foi publicada por
   último; alterações não conflitantes de ambas compõem a versão consolidada.

---

### User Story 6 - Consultar Conteúdo Vigente e Histórico (Priority: P2)

Como usuário interno ou consulente público, quero consultar a versão vigente e as Publicações
históricas para verificar as regras aplicáveis em uma data relevante.

**Why this priority**: A consulta garante transparência e reprodutibilidade, embora dependa das
capacidades de publicação e retificação.

**Independent Test**: Pode ser testada informando datas anteriores, intermediárias e posteriores a
Retificações e comparando o conteúdo apresentado com cada Publicação preservada.

**Acceptance Scenarios**:

1. **Given** um Edital original e Retificações publicadas, **When** o usuário consulta a versão
   vigente, **Then** o sistema apresenta a última versão consolidada e identifica os atos que a
   compõem.
2. **Given** uma data em que uma versão anterior vigorava, **When** o usuário solicita o conteúdo
   naquela data, **Then** o sistema reproduz essa versão sem usar regras posteriores.
3. **Given** uma pessoa sem permissão administrativa, **When** consulta informações públicas,
   **Then** ela acessa o Edital original, todas as Retificações e versões consolidadas históricas,
   sem conteúdo de elaboração, revisão ou auditoria restrita.

---

### User Story 7 - Cancelar ou Encerrar com Preservação (Priority: P2)

Como gestor autorizado, quero cancelar ou encerrar Processo Seletivo ou Edital conforme as regras
aplicáveis para registrar seu desfecho sem excluir seus atos e documentos.

**Why this priority**: O desfecho formal é necessário para a gestão institucional, mas ocorre após
as capacidades essenciais de estruturação e Publicação.

**Independent Test**: Pode ser testada cancelando um Edital publicado e encerrando um Processo com
Editais históricos, verificando preservação, motivo, responsável e impedimento de novas operações
incompatíveis.

**Acceptance Scenarios**:

1. **Given** um Edital publicado que pode ser cancelado, **When** o gestor registra o ato, motivo e
   responsável, **Then** o sistema altera sua situação sem apagar Publicações ou histórico.
2. **Given** um Processo encerrado, **When** alguém consulta seus Editais, **Then** o histórico
   permanece disponível e novas alterações incompatíveis são rejeitadas.
3. **Given** que todos os Editais de um Processo atingiram estados finais, **When** nenhum ato de
   encerramento do Processo foi registrado, **Then** o Processo conserva sua situação atual até
   que um gestor autorizado pratique o ato explícito e auditável.
4. **Given** um Processo com ao menos um Edital que não esteja Encerrado nem Cancelado, **When** o
   gestor tenta cancelar o Processo, **Then** o sistema bloqueia a operação e identifica os Editais
   que ainda precisam de encerramento ou cancelamento próprio.
5. **Given** um Edital Publicado cujas etapas terminaram regularmente, **When** o gestor autorizado
   registra explicitamente sua conclusão, **Then** o Edital passa a Encerrado sem ser tratado como
   Cancelado e todo o histórico permanece disponível.

### Edge Cases

- A tentativa de estabelecer um Processo Seletivo sem o primeiro Edital não deixa um Processo
  formalmente constituído nem dados parciais; a preparação pode ser retomada antes da confirmação.
- Um Processo pode conter vários Editais em situações e cronogramas diferentes sem que a mudança
  de um altere automaticamente os demais.
- Editais podem conter um ou vários Perfis; um Perfil pode ter vagas imediatas, somente Cadastro
  Reserva limitado ou ilimitado, conforme sua regra.
- Quantidades ou regras de Modalidades de Concorrência inválidas são rejeitadas antes da
  homologação, sem inventar cálculo não previsto na regra normativa vigente.
- Eventos pontuais e períodos coexistem; período invertido, evento no contexto de outro Edital ou
  sequência logicamente impossível é rejeitado quando a inconsistência for determinável.
- Retificação pode alterar Cronograma, vagas, Perfil ou qualquer outro conteúdo, mas somente sua
  Publicação altera o conteúdo vigente.
- Retificações sequenciais preservam a ordem e permitem reconstruir o estado após cada uma.
- Retificação sem data futura expressa vigora na Publicação; data de vigência anterior à Publicação
  é rejeitada e não produz alteração retroativa.
- Retificações publicadas fora da ordem de suas vigências futuras são aplicadas cumulativamente
  pelo início de vigência; a ordem de Publicação isoladamente não determina a versão vigente.
- Retificações com início de vigência idêntico compõem conjuntamente a consolidação; se alterarem o
  mesmo conteúdo de modo conflitante, prevalece nesse conteúdo a publicada por último.
- Tentativa de edição direta de Publicação é rejeitada, inclusive após cancelamento ou encerramento.
- Consultas por data anterior à primeira Publicação ou em intervalo sem versão vigente informam
  claramente que não havia conteúdo vigente, sem substituir pela versão atual.
- Ações simultâneas sobre uma versão obsoleta não podem sobrescrever mudança posterior nem publicar
  conteúdo diferente do homologado.
- Cancelamento preserva motivo, responsável, data, ato correspondente e todos os documentos
  anteriores; não equivale a exclusão.
- Cancelamento do Processo é rejeitado enquanto existir Edital que não esteja Encerrado ou
  Cancelado; não ocorre propagação automática de cancelamento.
- Encerrado representa conclusão regular do Edital após suas etapas; Cancelado representa sua
  interrupção administrativa antes da conclusão e não pode ser apresentado como encerramento.
- Encerramento do Processo não elimina Editais históricos e não força Editais a terem percorrido
  estados simultaneamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir que usuário autorizado estruture um Processo Seletivo com
  identificação institucional própria e primeiro Edital, preservando identidades distintas.
- **FR-002**: Cada Edital DEVE pertencer a exatamente um Processo Seletivo, e um Processo DEVE
  admitir um ou vários Editais.
- **FR-003**: O sistema DEVE impedir a constituição formal de Processo Seletivo sem ao menos um
  Edital válido e impedir criação parcial caso a operação conjunta falhe.
- **FR-004**: O sistema DEVE manter separadamente o ciclo de vida do Processo e de cada Edital.
- **FR-005**: O Processo DEVE admitir as situações Em elaboração, Ativo, Encerrado e Cancelado. O
  fluxo ordinário DEVE ser Em elaboração -> Ativo -> Encerrado; ativação e encerramento DEVEM ser
  atos administrativos explícitos, autorizados e auditáveis, sem decorrer automaticamente das
  situações dos Editais. O Cancelamento DEVE ser possível a partir de Em elaboração ou Ativo
  quando autorizado, e estados finais NÃO DEVEM retornar a estados anteriores.
- **FR-006**: O Edital DEVE admitir as situações Em elaboração, Em revisão, Homologado, Publicado,
  Encerrado e Cancelado. O fluxo ordinário DEVE ser Em elaboração -> Em revisão -> Homologado ->
  Publicado -> Encerrado; Encerrado DEVE representar a conclusão regular após o término das etapas.
  Antes da Publicação, a revisão PODE devolver o Edital a Em elaboração e a homologação PODE ser
  revogada para Em revisão. Após Publicação, correções DEVEM ocorrer por Retificação. Cancelado
  DEVE representar interrupção administrativa anterior à conclusão regular e ser estado final;
  Encerrado e Cancelado NÃO DEVEM ser tratados como sinônimos.
- **FR-007**: Cada Edital DEVE registrar número, ano, título, descrição quando aplicável, vínculo,
  situação, datas relevantes, regras, Cronograma e histórico.
- **FR-008**: O sistema DEVE separar a identidade interna estável do número ou código institucional
  e validar a unicidade deste no contexto institucional aplicável.
- **FR-009**: Usuários autorizados DEVEM poder incluir um ou vários Perfis de Vaga em um Edital.
- **FR-010**: Cada Perfil DEVE manter identificação, denominação, descrição, requisitos, quantidade
  de vagas, modalidade ou localidade quando aplicável e informações de classificação e convocação.
- **FR-011**: Vagas e Modalidades de Concorrência DEVEM pertencer ao Perfil correspondente e NÃO
  DEVEM ser propagadas para outro Perfil sem ação explícita.
- **FR-012**: O sistema DEVE representar Cadastro Reserva inexistente, limitado ou ilimitado e NÃO
  DEVE exigir vagas imediatas quando as regras admitirem apenas Cadastro Reserva.
- **FR-013**: O sistema DEVE manter separadas a Regra Normativa de cotas e o resultado de sua
  aplicação, incluindo fundamento e vigência necessários à reprodução.
- **FR-014**: Regras de cotas, distribuição, arredondamento e convocação DEVEM ser configuráveis
  conforme o fundamento vigente e NÃO DEVEM alterar retroativamente Publicações.
- **FR-015**: Cada Edital DEVE possuir Cronograma próprio composto por quantidade aberta de Eventos
  de Cronograma.
- **FR-016**: Cada Evento DEVE admitir identificação, descrição, data pontual ou período, ordem ou
  sequência lógica e situação, conforme sua natureza.
- **FR-017**: O sistema DEVE validar que início não seja posterior ao término e que cada Evento
  pertença ao Edital correto, rejeitando inconsistências determináveis.
- **FR-018**: Alterar o Cronograma de um Edital NÃO DEVE alterar Cronogramas de outros Editais do
  mesmo Processo.
- **FR-019**: Antes da Publicação, o sistema DEVE validar a completude e consistência do Edital e
  classificar achados como informação, aviso ou erro impeditivo.
- **FR-020**: Erros impeditivos DEVEM bloquear Publicação; avisos DEVEM permanecer visíveis ao
  responsável durante a decisão de prosseguir.
- **FR-021**: Somente usuário explicitamente autorizado DEVE poder homologar ou publicar, e toda
  autorização DEVE ser verificada na operação solicitada. Quem elaborou o Edital PODE submetê-lo,
  mas ao menos uma segunda pessoa autorizada DEVE realizar a homologação ou a Publicação; uma única
  pessoa NÃO PODE concluir sozinha as três etapas.
- **FR-022**: A Publicação DEVE registrar conteúdo homologado, versão, responsável pela operação,
  Autoridade Signatária, cargo ou função, data e hora e documento publicado.
- **FR-023**: O documento publicado DEVE corresponder integralmente aos dados estruturados e ao
  conteúdo editorial homologado e possuir identificação de integridade verificável.
- **FR-024**: Toda Publicação DEVE permanecer imutável e não poder ser substituída, editada ou
  excluída por operações comuns.
- **FR-025**: O sistema DEVE permitir preparar, revisar, homologar e publicar uma ou várias
  Retificações vinculadas a um Edital publicado.
- **FR-026**: A Retificação DEVE poder alterar qualquer conteúdo futuro do Edital e DEVE identificar
  o conteúdo anterior, as mudanças, autoria, ordem cronológica, efeitos e data de vigência. Ela
  DEVE vigorar na Publicação, salvo data futura expressamente declarada, e NÃO PODE vigorar antes
  da própria Publicação.
- **FR-027**: A Retificação DEVE admitir as situações Em elaboração, Em revisão, Homologada,
  Publicada e Cancelada, com retornos para correção permitidos somente antes da Publicação e
  Cancelamento final. Somente a Publicação DEVE alterar o conteúdo normativo vigente.
- **FR-028**: O sistema DEVE gerar e preservar versão consolidada após cada Publicação de
  Retificação e a cada início de vigência que altere o conteúdo aplicável, sem reescrever versões
  anteriores. A consolidação DEVE ser temporal e cumulativa.
- **FR-029**: Usuários DEVEM poder consultar a versão vigente, cada Publicação e Retificação e o
  conteúdo que vigorava em uma data informada, considerando separadamente data de Publicação e
  eventual data futura de vigência e aplicando todas as Retificações cuja vigência já tenha
  iniciado naquele instante.
- **FR-030**: A consulta histórica DEVE identificar qual ato produziu cada alteração e NÃO DEVE
  aplicar retroativamente regras ou conteúdo posteriores.
- **FR-031**: A consulta pública DEVE exibir somente conteúdo publicado e destinado à divulgação;
  ela DEVE disponibilizar o Edital original, todas as Retificações publicadas e todas as versões
  consolidadas históricas. Materiais de elaboração, revisão e auditoria restrita DEVEM exigir
  autorização.
- **FR-032**: Operações de criação, alteração, homologação, Publicação, Retificação, mudança de
  Cronograma, cancelamento e mudança relevante de situação DEVEM ser auditadas com ator, ação,
  objeto, data e hora, estados anterior e posterior, motivo, versão e contexto quando aplicável.
- **FR-033**: O sistema DEVE negar por padrão operações sem autorização e impedir acesso ou alteração
  apenas pela manipulação de identificadores.
- **FR-034**: Cancelar Processo, Edital ou Retificação DEVE exigir autorização, motivo, responsável,
  data e ato correspondente quando aplicável, sem excluir Publicações ou histórico. O cancelamento
  do Processo DEVE ser bloqueado enquanto qualquer de seus Editais não estiver Encerrado ou
  Cancelado e NÃO DEVE cancelar Editais automaticamente.
- **FR-035**: Encerramento e cancelamento DEVEM impedir novas transições incompatíveis, mantendo
  disponíveis as consultas históricas autorizadas.
- **FR-036**: Operações concorrentes DEVEM impedir perda de atualização, alteração baseada em versão
  obsoleta e Publicação de conteúdo diferente da versão homologada.
- **FR-038**: O sistema DEVE fornecer mensagens claras e acessíveis para validações, operações
  negadas, estados vazios e consultas sem versão vigente.
- **FR-039**: A precedência normativa de Retificações DEVE ser determinada pelo início de vigência,
  não apenas pela ordem de Publicação. Retificações vigentes DEVEM compor cumulativamente a versão
  consolidada. Quando duas ou mais tiverem o mesmo início de vigência, todas as alterações não
  conflitantes DEVEM compor a versão; em conflito sobre o mesmo conteúdo, DEVE prevalecer a
  Retificação publicada por último. O resultado vigente DEVE ser sempre determinístico.

### Key Entities *(include if feature involves data)*

- **Processo Seletivo**: iniciativa institucional de seleção, com identidade e ciclo de vida
  próprios; agrega um ou vários Editais sem sincronizar seus estados.
- **Edital**: conjunto normativo pertencente a um Processo, com identificação institucional,
  conteúdo, situação, Perfis, Cronograma e Publicações próprios.
- **Perfil de Vaga**: oportunidade ou especialidade abrangida por um Edital, com requisitos, vagas,
  Cadastro Reserva, modalidades e informações próprias.
- **Vaga**: disponibilidade vinculada a um Perfil, distinguindo vagas imediatas das condições de
  Cadastro Reserva.
- **Modalidade de Concorrência**: forma de concorrência ou reserva aplicável a um Perfil, associada
  à Regra Normativa vigente sem se confundir com o resultado calculado.
- **Regra Normativa**: definição configurável, fundamentada e temporal das regras que orientam
  cotas e outros conteúdos sujeitos a legislação.
- **Cronograma**: organização temporal exclusiva de um Edital, composta por Eventos.
- **Evento de Cronograma**: marco ou período do Cronograma, com identidade, descrição, temporalidade,
  sequência e situação adequadas à sua natureza.
- **Publicação**: registro imutável de uma versão homologada, de seu documento, autoria, autoridade,
  momento e integridade.
- **Retificação**: ato vinculado a um Edital publicado que descreve mudanças normativas e, quando
  publicado, origina nova versão vigente sem apagar as anteriores.
- **Versão de Edital**: representação consolidada e reproduzível do conteúdo vigente após uma
  Publicação original ou início de vigência de Retificação; resulta da composição temporal e
  cumulativa dos atos já vigentes, com precedência determinística em conflitos.
- **Registro de Auditoria**: evidência inviolável de operação relevante, seus responsáveis,
  contexto e efeitos, com acesso compatível com a sensibilidade das informações.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em testes de aceitação, 100% dos Processos formalmente constituídos possuem ao menos
  um Edital, e 100% dos Editais pertencem a exatamente um Processo.
- **SC-003**: Em 100% dos cenários com vários Editais, alterações de Perfil ou Cronograma de um
  Edital não modificam dados de outro Edital.
- **SC-004**: 100% das tentativas de publicar Edital com erro impeditivo são bloqueadas e apresentam
  a causa; 100% das Publicações válidas correspondem ao conteúdo homologado.
- **SC-005**: Para uma sequência de até 20 Retificações de referência, usuários autorizados
  recuperam a versão vigente e qualquer versão histórica solicitada, com identificação de todos os
  atos que a compõem, em até 10 segundos por consulta.
- **SC-006**: 100% das tentativas de edição ou exclusão direta de Publicações preservadas são
  rejeitadas sem alteração do histórico.
- **SC-007**: 100% das operações críticas previstas em FR-032 produzem registro de auditoria com os
  dados obrigatórios aplicáveis e sem exposição desnecessária de dados sensíveis.
- **SC-008**: Nos testes de autorização, 100% das operações sem permissão explícita são negadas e
  nenhum identificador manipulado concede acesso adicional.

## Deferred Frontend Requirements

Os itens abaixo preservam seus identificadores para rastreabilidade, mas **não integram o escopo de
implementação nem os critérios de aceite deste incremento backend**. Eles deverão ser refinados e
ratificados numa futura especificação da interface administrativa acessível:

- **FR-037 (deferred)**: apresentar confirmação e consequências antes de Publicação, cancelamento
  ou outra operação irreversível ou juridicamente relevante.
- **SC-002 (deferred)**: permitir que usuários autorizados concluam a estruturação de um Processo
  com primeiro Edital e ao menos um Perfil, sem assistência externa, em até 15 minutos.
- **SC-009 (deferred)**: permitir que pelo menos 90% dos representantes administrativos concluam
  corretamente, na primeira tentativa, os cenários de criar Edital, configurar Perfil e Cronograma
  e submeter à validação.
- **SC-010 (deferred)**: permitir a conclusão dos fluxos críticos por teclado, com erros textuais
  compreensíveis e sequência lógica de navegação.

## Assumptions

- Identificações institucionais seguem regras definidas pelo Cefor/IFES; sua forma exata poderá ser
  configurada sem transformar o identificador público em identidade interna ou autorização.
- A preparação de Processo e primeiro Edital ocorre como uma unidade de trabalho; o Processo só é
  formalmente constituído quando a invariável de ao menos um Edital é satisfeita.
- Os estados descritos nesta especificação constituem o conjunto mínimo desta feature; etapas
  administrativas adicionais só serão incluídas mediante requisito institucional explícito.
- As regras legais aplicáveis, incluindo cotas, serão fornecidas e homologadas pela instituição; a
  feature registra e aplica regras informadas, mas não cria interpretação jurídica autônoma.
- A assinatura eletrônica real do PDF não integra este escopo inicial; permanecem obrigatórios os
  registros de Autoridade Signatária, autoria, integridade e versão.
- Consulta pública abrange o Edital original, todas as Retificações publicadas e todas as versões
  consolidadas históricas; conteúdo preparatório e auditoria detalhada permanecem restritos.
- Eventos posteriores como Inscrição, Avaliação, Recurso, Classificação, Resultado e Convocação
  consumirão futuramente versões normativas preservadas, mas não são executados nesta feature.

## Out of Scope

- Interface gráfica administrativa e pública, incluindo confirmação visual de atos, navegação por
  teclado e métricas de usabilidade; esses itens serão tratados em especificação futura de frontend.
- Inscrição de Candidatos, envio e análise de documentos e pagamento.
- Recursos de Candidatos, provas, avaliações, pontuação e classificação.
- Resultado final, convocação, contratação e demais efeitos posteriores do certame.
- Definição de matriz completa de papéis e permissões institucionais.
- Escolha de linguagem, framework, banco de dados, infraestrutura, APIs, bibliotecas, classes ou
  arquitetura física.
- Integração com serviço de assinatura eletrônica real.
