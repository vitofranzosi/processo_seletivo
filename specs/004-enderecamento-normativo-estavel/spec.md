# Feature Specification: Endereçamento Normativo por Chave Estável

**Feature Branch**: `004-enderecamento-normativo-estavel`

**Created**: 2026-08-29

**Status**: Clarificada — cinco perguntas respondidas em 2026-08-29. Pronta para `speckit-plan`.
Depende da `003-integridade-e-prontidao`.

**Input**: A `003` conteve o dano do endereçamento por índice, mas registrou que a contenção não é
a cura. Esta feature elimina a causa: Alterações Normativas passam a endereçar Perfis, Eventos e
Modalidades pela chave estável que essas entidades já possuem, em vez da posição que ocupam numa
lista.

## Contexto e Justificativa

Uma Alteração Normativa hoje diz `/profiles/1/name`. O `1` é a posição do Perfil no momento em que
o ato foi elaborado. Posição não é identidade: qualquer Retificação publicada no intervalo que
remova ou insira um Perfil anterior desloca todos os seguintes, e o ato passa a falar de outro
Perfil.

A `003` tornou isso impossível de passar em silêncio — hoje o sistema recusa com `409`. Mas
recusar é o melhor que a contenção alcança. Ela não permite publicar o ato certo: quando a lista
muda de forma, a Retificação precisa ser devolvida e reelaborada, mesmo que o Perfil que ela altera
não tenha sido tocado por ninguém. Duas pessoas trabalhando em Perfis diferentes do mesmo Edital
atropelam uma à outra sem necessidade.

A Constituição já exige o que falta, no princípio I: *"Entidades DEVEM possuir identificadores
estáveis"*. As entidades os possuem — `Perfil`, `Evento` e `Modalidade` carregam `id` no snapshot
publicado. O que não os usa é o endereçamento.

### O que muda de fato

Endereçar por chave é mudança de **contrato público**, de **modelo de dados** e de **histórico**:

- `targetPath` passa a admitir uma forma nova. O `openapi.yaml` muda.
- Retificações já persistidas usam a forma antiga e não podem ser reescritas quando publicadas.
- Versões consolidadas e a proveniência por caminho (`ProvenienciaConteudo.target_path`) guardam
  caminhos posicionais que continuarão a existir no histórico.
- A interface compõe caminhos posicionais em `interface/retificacao.py`.

É por isso que esta é feature própria e não emenda da `003`: acumular uma mudança de contrato com
uma correção emergencial num mesmo ciclo esconderia a segunda dentro da primeira.

## Clarifications

### Session 2026-08-29

- Q: Qual sintaxe uma Alteração Normativa deve usar para apontar um Perfil pela chave dele, em vez
  da posição? → A: Seletor explícito `id=<uuid>` no segmento da coleção — `/profiles/id=<uuid>/name`.

  Descartada a alternativa de usar o UUID como token cru (`/profiles/<uuid>/name`): resolver um
  identificador dentro de um array **também** é semântica customizada, então aquela forma seria um
  dialeto apenas sintaticamente compatível com o RFC 6901 — um dialeto que se esconde. Num campo
  que fica gravado para sempre no ato publicado, a extensão declarada é mais legível para quem
  audita e mais honesta sobre o que é.

- Q: Depois desta mudança, uma Retificação nova ainda poderá endereçar um Perfil pela posição, ou
  o caminho por chave passa a ser obrigatório? → A: Obrigatório na escrita para coleções com
  identidade. Caminhos posicionais permanecem apenas para leitura histórica e para coleções
  genuinamente sem chave.

  Assim nenhum ato novo instável pode ser criado, e nenhum ato já publicado precisa ser reescrito.

- Q: O que acontece com as Retificações em elaboração, em revisão ou homologadas — ainda não
  publicadas — no dia em que a feature entrar em produção? → A: Converter deterministicamente a
  partir de `expected_anchors`, inclusive as homologadas, registrando a migração na auditoria.
  Caso sem resolução inequívoca é devolvido para reelaboração.

  As publicadas não entram: ato produzido não se reescreve.

- Q: Como uma Retificação deve dizer onde inserir um Perfil novo, já que uma inserção não tem
  entidade alvo para nomear pela chave? → A: Âncoras relativas `before=<uuid>` e `after=<uuid>`,
  recusando a operação se a referência não existir. `/profiles/-` continua valendo para acréscimo
  explícito ao fim.

- Q: Como uma Retificação deve alterar os requisitos de um Perfil, já que `requirements` é uma
  lista de texto puro, sem identificador em cada item? → A: Tratar `requirements` como valor
  normativo atômico — substituição integral da lista, com `expectedPreviousHash` calculado sobre a
  coleção completa. Estável por construção, e ainda detecta alteração concorrente.

Cinco perguntas, cinco respostas. Nenhuma decisão desta feature ficou por suposição.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retificar sem ser atropelado por trabalho alheio (Priority: P1)

Como elaborador de uma Retificação, quero que meu ato continue válido quando outra Retificação
altera um Perfil diferente do mesmo Edital, para que trabalho concorrente sobre partes distintas
não obrigue nenhum de nós a começar de novo.

**Why this priority**: É o ganho que a contenção da `003` não entrega. Hoje qualquer mudança na
forma da lista invalida atos que não têm relação com ela.

**Independent Test**: Elaborar duas Retificações sobre Perfis distintos da mesma versão, publicar
as duas em sequência e verificar que ambas são aceitas e atingem cada uma o seu Perfil.

**Acceptance Scenarios**:

1. **Given** duas Retificações sobre Perfis distintos elaboradas na mesma versão, **When** ambas
   são publicadas, **Then** as duas são aceitas e cada uma altera o Perfil que endereçou.
2. **Given** uma Retificação sobre um Perfil que outra removeu no intervalo, **When** é publicada,
   **Then** é recusada, porque a entidade endereçada deixou de existir.
3. **Given** duas Retificações sobre o mesmo campo do mesmo Perfil, **When** a segunda é publicada,
   **Then** é recusada pela precondição de conteúdo, que continua valendo.

---

### User Story 2 - Ler o histórico sem ambiguidade (Priority: P1)

Como auditor, quero que a trilha de um Edital identifique sem ambiguidade qual Perfil cada ato
alterou, inclusive nos atos anteriores a esta mudança, para que a reconstrução histórica não dependa
de recalcular posições.

**Acceptance Scenarios**:

1. **Given** uma Retificação publicada antes desta feature, **When** o histórico é consultado,
   **Then** o ato continua legível e a entidade que ele alterou é identificável.
2. **Given** uma Retificação publicada depois, **When** o histórico é consultado, **Then** a
   entidade é nomeada pela chave, sem depender da forma da lista naquele instante.
3. **Given** as duas formas no mesmo Edital, **When** a versão vigente é materializada, **Then** o
   resultado é o mesmo que a composição sempre produziu.

---

### User Story 3 - Compor a Retificação sem conhecer a representação (Priority: P2)

Como elaborador, quero continuar editando o conteúdo vigente na tela, sem precisar saber que existe
caminho, chave ou índice, para que a mudança de representação não vire trabalho meu.

**Acceptance Scenarios**:

1. **Given** a tela de Retificação, **When** a pessoa altera campos de um Perfil, **Then** as
   Alterações Normativas emitidas usam a chave estável, sem qualquer mudança visível na tela.
2. **Given** a mesma tela, **When** a pessoa acrescenta ou remove Perfis, **Then** o ato resultante
   não depende da ordem em que as alterações foram emitidas.

---

### Edge Cases

- Entidade endereçada por chave que não existe na versão vigente: recusa explícita, distinta de
  "caminho inexistente".
- Duas entidades com a mesma chave na mesma coleção: estado impossível que precisa ser rejeitado na
  composição, não descoberto na Publicação.
- `ADD` de entidade cuja chave já existe: é substituição disfarçada e deve ser recusada.
- `ADD` cuja âncora `before=`/`after=` aponta para entidade removida no intervalo: a posição
  pretendida não é mais determinável, e o ato é recusado em vez de cair no fim da lista.
- Retificação em curso cuja conversão não resolve de forma inequívoca: devolução explícita, com
  motivo, em vez de conversão por aproximação.
- `requirements` substituída por lista vazia: é ato admissível, porque a validação de publicação
  não exige requisitos — diferente da remoção do último Perfil, que é erro impeditivo.
- Duas alterações do mesmo ato inserindo com `before=` na mesma referência: a ordem entre elas é a
  ordem em que foram declaradas, que é a mesma regra que a `003` já aplica à sequência.
- Alteração que remove uma entidade e outra, no mesmo ato, que a usa como referência de posição: a
  referência é resolvida contra o conteúdo que a alteração encontra, então a ordem de declaração
  decide — e a recusa é explícita se a referência já não existir naquele ponto.

## Requirements *(mandatory)*

- **FR-001**: Alterações Normativas DEVEM poder endereçar Perfis, Eventos e Modalidades pela chave
  estável da entidade, independentemente da posição que ela ocupe na coleção. A sintaxe é o seletor
  explícito `id=<identificador>` no segmento da coleção, como em `/profiles/id=<uuid>/name`.
- **FR-001a**: O seletor `id=` DEVE ser interpretado **apenas** quando o contêiner do segmento for
  uma lista. Em objeto, o segmento continua sendo nome de chave literal, de modo que uma chave
  chamada `id=algo` permanece endereçável e a extensão não retira expressividade do RFC 6901.
- **FR-001b**: O contrato DEVE declarar a extensão como extensão, e não como JSON Pointer padrão.
  Ela é semântica local em ambas as formas possíveis; anunciá-la explicitamente é o que permite a
  quem audita um ato publicado saber como o caminho foi resolvido.
- **FR-001c**: Alterações Normativas **novas** NÃO DEVEM endereçar por posição uma coleção cujos
  elementos tenham identificador. A recusa acontece na elaboração, não na Publicação: um ato que
  nasce instável não deve chegar a existir.
- **FR-001d**: A **leitura** — consolidação, consulta histórica, proveniência — DEVE continuar
  aceitando caminhos posicionais indefinidamente. Atos publicados não são reescritos, então a forma
  antiga permanece no histórico para sempre.
- **FR-001e**: `ADD` em coleção com identidade DEVE indicar a posição por **referência de
  posição** — `/profiles/before=<uuid>` ou `/profiles/after=<uuid>` —, ou por `/profiles/-` quando
  a intenção for acrescentar ao fim. Índice numérico NÃO DEVE ser admitido: é a forma que desloca,
  e `ADD` é o caso em que a contenção da `003` protege pior, por não haver conteúdo anterior a
  comparar.

  O termo **âncora** fica reservado ao mecanismo da `003` que esta feature aposenta (FR-009).
  Chamar as duas coisas de âncora confundiria o que sai com o que entra.
- **FR-001f**: Coleção aninhada com identidade DEVE ser endereçável pela forma composta, como em
  `/profiles/id=<uuid>/competitionModalities/id=<uuid>/name`. Cada segmento de lista resolve pela
  chave do seu próprio nível.
- **FR-001g**: `normativeRule` é objeto, não item de lista, e DEVE continuar sendo endereçada pelo
  nome da chave — `/profiles/id=<uuid>/competitionModalities/id=<uuid>/normativeRule/percentage`.
  Ter `id` não a torna elemento de coleção.
- **FR-001h**: O identificador no seletor DEVE ser comparado como texto exato, sem normalização de
  caixa. Identificador que contenha `/` ou `~` DEVE usar o escape do RFC 6901 (`~1` e `~0`), que a
  extensão não altera.
- **FR-002**: A resolução por chave DEVE recusar explicitamente quando a entidade endereçada não
  existir. A verificação acontece nos **dois** momentos que a `003` estabeleceu: na elaboração,
  contra a versão declarada em `baseSnapshotId`, e na Publicação, contra o conteúdo vigente no
  início da vigência declarada. São perguntas distintas — "existe no que eu vi?" e "ainda existe
  quando meu ato passa a valer?" — e ambas precisam de resposta.
- **FR-002a**: As recusas DEVEM ter código próprio, no mesmo vocabulário da `003`:
  `target_key_not_found` quando a entidade endereçada não existe; `position_reference_not_found`
  quando a referência de um `before=`/`after=` não existe, caso em que a posição pretendida deixou
  de ser determinável; `duplicate_key_in_collection` para chave repetida;
  `positional_addressing_refused` para endereçamento por índice em coleção com identidade. Cada
  código DEVE nomear o caminho envolvido, como fazem os da `003`.
- **FR-003**: A precondição de conteúdo por hash da `003` NÃO DEVE ser aposentada e DEVE continuar
  valendo sobre o endereçamento novo. Ela responde a outra pergunta — se o conteúdo ainda é o que
  estava à vista —, e identificar a entidade certa não dispensa verificá-lo. Continua sendo a única
  defesa contra duas Retificações que alterem o mesmo campo da mesma entidade.
- **FR-004**: A composição DEVE recusar coleção com chave repetida, **na elaboração e na
  Publicação**. Descobrir o estado impossível ao materializar a versão consolidada seria descobrir
  tarde: o ato já teria sido homologado.
- **FR-004a**: Coleção cujos elementos não tenham identificador — hoje apenas `requirements` — DEVE
  ser tratada como valor normativo atômico: alterada por `REPLACE` da lista inteira, nunca item a
  item. O `expectedPreviousHash` incide sobre a coleção completa, de modo que alteração concorrente
  continua sendo detectada sem que exista índice para deslocar.
- **FR-005**: Retificações publicadas antes desta feature NÃO DEVEM ter seus caminhos reescritos.
- **FR-005a**: Retificações **não publicadas** DEVEM ter seus caminhos convertidos para a forma por
  chave, por migração determinística que parta de `AlteracaoNormativa.expected_anchors` — a
  identidade de cada índice atravessado, que a `003` já persiste. A conversão não adivinha: onde a
  resolução não for inequívoca, a Retificação DEVE ser devolvida para reelaboração.
- **FR-005b**: A conversão DEVE ser registrada na auditoria, inclusive nas Retificações já
  homologadas, com o caminho antes, o caminho depois, o momento e a identificação da migração que
  a produziu — não uma pessoa, porque não houve ato humano. O efeito do ato é idêntico por construção, mas a representação que a autoridade
  homologou muda — e mudança silenciosa em ato homologado é exatamente o que a trilha existe para
  impedir.
- **FR-006**: A consulta histórica DEVE reproduzir corretamente atos em ambas as formas.
- **FR-007**: A interface administrativa DEVE emitir a forma nova sem exigir conhecimento de
  representação de quem elabora.
- **FR-008**: O contrato público DEVE documentar a forma nova, sua sintaxe e seus erros.
- **FR-009**: A âncora de identidade introduzida pela `003` DEVE ser aposentada quando a conversão
  de FR-005a estiver concluída. **Concluída** é condição verificável, e não a migração ter rodado:
  nenhuma Retificação em estado não final possui `expected_anchors` preenchido. Depois dela, todo caminho gravável ou nomeia a entidade (`id=`,
  `before=`, `after=`) ou é atômico (FR-004a) — em nenhum dos dois casos há índice a deslocar, que
  era a única pergunta que a âncora respondia. Atos já publicados na forma antiga não precisam
  dela: a precondição só é verificada na Publicação, e a deles já ocorreu.
- **FR-010**: A proveniência por caminho (`ProvenienciaConteudo.target_path`) DEVE registrar o
  caminho na forma em que o ato o declarou, sem convertê-lo. Ela é evidência de qual Publicação
  originou cada trecho: reescrevê-la faria o registro divergir do ato que ele documenta.
- **FR-011**: A devolução prevista em FR-005a DEVE informar a quem elaborou qual alteração não
  resolveu e por quê, pelo mesmo caminho das demais devoluções — `return_reason` e a trilha de
  auditoria. Devolução sem motivo transfere para a pessoa o trabalho de descobrir o que houve.

## Success Criteria *(mandatory)*

- **SC-001**: Duas Retificações sobre entidades distintas da mesma versão publicam ambas, sem
  reelaboração.
- **SC-002**: Nenhum ato publicado antes desta feature muda de efeito depois dela. Verificável
  comparando o hash canônico de cada Versão Consolidada existente antes e depois da migração: os
  conjuntos precisam ser idênticos.
- **SC-003**: A consulta temporal produz o mesmo conteúdo que produzia antes, verificada sobre um
  conjunto definido de instantes: cada limite de vigência do Edital, mais um segundo antes e um
  segundo depois de cada um. "Todo instante" não é verificável; as fronteiras são onde o resultado
  muda, e é nelas que um erro apareceria.
- **SC-004**: Nenhuma Retificação atinge entidade diferente da endereçada, em qualquer composição.
- **SC-005**: Nenhum ato novo é criado endereçando por posição uma coleção com identidade — a
  recusa acontece na elaboração e é verificável por tentativa.
- **SC-006**: Ao fim da migração, toda Retificação em estado não final ou está na forma por chave,
  ou foi devolvida com motivo registrado. Nenhuma permanece em curso na forma antiga.
- **SC-007**: Concluída a conversão, nenhuma Retificação em estado não final tem `expected_anchors`
  preenchido — que é a condição de FR-009 e o que autoriza remover o mecanismo.

## Assumptions

- As entidades relevantes já carregam identificador estável no snapshot publicado. Isso foi
  verificado: `Perfil`, `Evento` e `Modalidade` têm `id`.
- A precondição de conteúdo da `003` permanece ativa durante e depois desta feature. O que sai é a
  âncora de identidade, tornada redundante pelo endereçamento por chave (FR-009); o hash fica, e
  continua sendo o que impede sobrescrita silenciosa entre atos concorrentes (FR-010).
- `requirements` é a única coleção normativa sem identificador. Verificado em `edital_snapshot`:
  `profiles`, `schedule`, `competitionModalities` e `normativeRule` carregam `id`.
- A ordem do array é normativamente visível: o PDF publicado renderiza `profiles` e `schedule` na
  ordem em que estão, sem reordenar. É por isso que inserir em posição precisa continuar
  expressável, e por âncora estável.

## Out of Scope

- Integração com o diretório institucional.
- Qualquer mudança no ciclo de vida da Retificação ou nas regras de vigência.
- Endereçamento item a item de coleções sem identificador: a Q5 decidiu tratá-las como valor
  atômico (FR-004a), então dar identidade a linhas de texto está fora deste incremento.
- Requisitos de desempenho da resolução por chave: as coleções normativas têm dezenas de elementos,
  não milhares, e nenhuma meta própria se justifica antes de haver medida.

## Dependencies

- `003-integridade-e-prontidao` concluída — 71 tarefas, nenhum requisito aberto.
- Clarificações concluídas em 2026-08-29; nenhuma decisão pendente bloqueia o planejamento.
