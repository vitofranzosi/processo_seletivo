# Feature Specification: Endereçamento Normativo por Chave Estável

**Feature Branch**: `004-enderecamento-normativo-estavel`

**Created**: 2026-08-29

**Status**: Escopo reduzido em 2026-08-29. Implementada e revisada em 2026-08-29.

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

### Redução de escopo — 2026-08-29

O sistema **não está em produção e não há dado persistido a preservar**. Tudo o que a versão
anterior desta especificação previa para atravessar a virada — conversão de caminhos existentes,
compatibilidade entre as duas formas, auditoria da conversão, devolução de Retificações em curso,
relatório por origem e migração baseada em `expected_anchors` — deixou de ter objeto e saiu do
escopo.

O que sobra é a mudança em si: endereçar por chave, emitir a forma nova pela interface, recusar a
forma antiga, e remover `expected_anchors` por migração de esquema simples.

Também saíram, por não haver demanda que os justifique:

- **`before=` e `after=`**: a interface não oferece inserção em posição específica. Acréscimo é
  `/colecao/-`, ao fim.
- **Identificador genérico**: o seletor aceita UUID, que é o que as entidades carregam. Generalizar
  para "qualquer texto" seria construir para um caso que não existe.

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
  o caminho por chave passa a ser obrigatório? → A: Obrigatório na escrita para coleções com chave.

- Q: Como uma Retificação deve alterar os requisitos de um Perfil, já que `requirements` é uma
  lista de texto puro, sem identificador em cada item? → A: Tratar `requirements` como valor
  normativo atômico — substituição integral da lista, com `expectedPreviousHash` calculado sobre a
  coleção completa. Estável por construção, e ainda detecta alteração concorrente.

**Superadas pela redução de escopo**, registradas porque a decisão existiu e alguém pode procurá-la:

- Q: O que acontece com as Retificações não publicadas no dia em que a feature entrar em produção?
  → A à época: converter deterministicamente a partir de `expected_anchors`. **Sem objeto**: não há
  ato a converter.
- Q: Como indicar onde inserir um Perfil novo? → A à época: referências de posição `before=` e
  `after=`. **Fora de escopo**: a interface não oferece inserção em posição, e acréscimo passa a ser
  só `/colecao/-`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retificar sem ser atropelado por trabalho alheio (Priority: P1)

Como elaborador de uma Retificação, quero que meu ato continue válido quando outra Retificação
altera um Perfil diferente do mesmo Edital, para que trabalho concorrente sobre partes distintas
não obrigue nenhum de nós a começar de novo.

**Why this priority**: é o ganho que a contenção da `003` não entrega. Hoje qualquer mudança na
forma da lista invalida atos que não têm relação com ela.

**Independent Test**: elaborar duas Retificações sobre Perfis distintos da mesma versão, publicar
as duas em sequência e verificar que ambas são aceitas e atingem cada uma o seu Perfil.

**Acceptance Scenarios**:

1. **Given** duas Retificações sobre Perfis distintos elaboradas na mesma versão, **When** ambas
   são publicadas, **Then** as duas são aceitas e cada uma altera o Perfil que endereçou.
2. **Given** uma Retificação sobre um Perfil que outra removeu no intervalo, **When** é publicada,
   **Then** é recusada, porque a entidade endereçada deixou de existir.
3. **Given** duas Retificações sobre o mesmo campo do mesmo Perfil, **When** a segunda é publicada,
   **Then** é recusada pela precondição de conteúdo, que continua valendo.
4. **Given** uma Retificação que endereça um Perfil por índice, **When** é elaborada, **Then** é
   recusada ali mesmo — o ato instável não chega a existir.

---

### User Story 2 - Compor a Retificação sem conhecer a representação (Priority: P2)

Como elaborador, quero continuar editando o conteúdo vigente na tela, sem precisar saber que existe
caminho, chave ou índice, para que a mudança de representação não vire trabalho meu.

**Independent Test**: alterar campos de um Perfil pela tela e verificar que as Alterações emitidas
usam a chave, sem que nada tenha mudado para quem usa.

**Acceptance Scenarios**:

1. **Given** a tela de Retificação, **When** a pessoa altera campos de um Perfil, **Then** as
   Alterações Normativas emitidas usam a chave estável, sem qualquer mudança visível na tela.
2. **Given** a mesma tela, **When** a pessoa acrescenta ou remove Perfis, **Then** o ato resultante
   não depende da ordem em que as alterações foram emitidas.
3. **Given** a mesma tela, **When** a página é entregue, **Then** nenhum caminho normativo aparece
   no HTML.

---

### Edge Cases

- Entidade endereçada por chave que não existe: recusa explícita, distinta de "caminho inexistente".
- Duas entidades com a mesma chave na mesma coleção: estado impossível, rejeitado na composição.
- `ADD` de entidade cuja chave já existe: é substituição disfarçada e deve ser recusada.
- Identificador que apareça em mais de uma coleção do mesmo snapshot: irrelevante, porque a
  resolução é escopada à coleção nomeada no caminho. Unicidade global NÃO é pressuposta.
- `requirements` substituída por lista vazia: ato admissível — a validação de publicação não exige
  requisitos, diferente da remoção do último Perfil, que é erro impeditivo.

## Requirements *(mandatory)*

### Endereçamento

- **FR-001**: Alterações Normativas DEVEM endereçar Perfis, Eventos e Modalidades pela chave estável
  da entidade, independentemente da posição que ela ocupe na coleção. A sintaxe é o seletor
  explícito `id=<uuid>` no segmento da coleção, como em `/profiles/id=<uuid>/name`.
- **FR-002**: O seletor `id=` DEVE ser interpretado **apenas** quando o contêiner do segmento for
  uma lista. Em objeto, o segmento continua sendo nome de chave literal, de modo que uma chave
  chamada `id=algo` permanece endereçável e a extensão não retira expressividade do RFC 6901.
- **FR-003**: O valor do seletor DEVE ser um UUID, comparado como texto exato e sem normalização de
  caixa. Identificador de outra natureza NÃO É admitido: as entidades endereçáveis carregam UUID, e
  generalizar seria construir para um caso que não existe.
- **FR-004**: Coleção aninhada DEVE ser endereçável pela forma composta, como em
  `/profiles/id=<uuid>/competitionModalities/id=<uuid>/name`. Cada segmento de lista resolve pela
  chave do seu próprio nível.
- **FR-005**: `normativeRule` é objeto, não item de lista, e DEVE continuar sendo endereçada pelo
  nome da chave. Ter `id` não a torna elemento de coleção.
- **FR-006**: `ADD` em coleção com chave DEVE usar `/colecao/-`, que acrescenta ao fim. Inserção em
  posição específica NÃO faz parte desta feature: a interface não a oferece.

### Recusas

- **FR-007**: Alterações Normativas NÃO DEVEM endereçar por posição uma coleção com chave. A recusa
  acontece na **elaboração**, com `positional_addressing_refused`: um ato que nasce instável não
  deve chegar a existir.
- **FR-008**: A resolução por chave DEVE recusar, com `target_key_not_found`, quando a entidade
  endereçada não existir. A verificação acontece nos dois momentos que a `003` estabeleceu: na
  elaboração, contra a versão declarada em `baseSnapshotId`, e na Publicação, contra o conteúdo
  vigente no início da vigência declarada.
- **FR-009**: A composição DEVE recusar, com `duplicate_key_in_collection`, coleção que ficaria com
  chave repetida — na elaboração e na Publicação.
- **FR-010**: Cada código de recusa DEVE nomear o caminho envolvido, como fazem os da `003`.

### Coleções

- **FR-011**: Coleção cujos elementos não tenham identificador — hoje apenas `requirements` — DEVE
  ser tratada como valor normativo atômico: alterada por `REPLACE` da lista inteira, nunca item a
  item. O `expectedPreviousHash` incide sobre a coleção completa.
- **FR-012**: As coleções com chave DEVEM ser declaradas explicitamente, e a declaração DEVE ser
  verificada por teste contra o snapshot real. Sem a verificação, uma migration futura acrescentaria
  coleção sem identificador em silêncio e o pressuposto de FR-011 passaria a ser falso.
- **FR-013**: O endereçamento normativo alcança apenas o conteúdo do snapshot do Edital. Listas de
  controle interno — `applied_publications`, por exemplo — NÃO SÃO endereçáveis.

### O que fica e o que sai da `003`

- **FR-014**: A precondição de conteúdo por hash NÃO DEVE ser aposentada. Ela responde a outra
  pergunta — se o conteúdo ainda é o que estava à vista — e continua sendo a única defesa contra
  duas Retificações que alterem o mesmo campo da mesma entidade.
- **FR-015**: A âncora de identidade da `003` DEVE ser removida por completo: derivação,
  verificação, o código `target_identity_mismatch` e a coluna `expected_anchors`. Com todo caminho
  nomeando a entidade ou sendo atômico, não sobra índice para deslocar — que era a única pergunta
  que ela respondia.
- **FR-016**: A remoção da coluna DEVE ser migração de **esquema**, sem conversão de dados e sem
  condição a comprovar. Não há ato a preservar.

### Contrato e interface

- **FR-017**: O contrato DEVE declarar a extensão como extensão, e não como JSON Pointer padrão, e
  documentar a sintaxe e os códigos de recusa. Anunciá-la é o que permite a quem audita um ato
  publicado saber como o caminho foi resolvido.
- **FR-018**: Um caminho publicado DEVE permitir identificar a entidade que o ato alterou **sem
  consultar a versão vigente**. É a condição que torna a auditabilidade verificável em vez de
  adjetivo.
- **FR-019**: A interface administrativa DEVE emitir a forma nova sem expor representação a quem
  elabora. Verificável por duas condições: nenhum caminho normativo aparece no HTML da tela de
  Retificação, e as alterações que ela emite usam a forma por chave.

## Success Criteria *(mandatory)*

- **SC-001**: Duas Retificações sobre entidades distintas da mesma versão publicam ambas, sem
  reelaboração.
- **SC-002**: Nenhuma Retificação atinge entidade diferente da endereçada, em qualquer composição.
- **SC-003**: Nenhum ato é criado endereçando por posição uma coleção com chave — a recusa acontece
  na elaboração e é verificável por tentativa.
- **SC-004**: A tela de Retificação não expõe caminho normativo algum no HTML que entrega, e as
  alterações que ela emite usam a forma por chave.
- **SC-005**: O contrato publicado descreve a extensão, os três códigos de recusa e a forma de
  `ADD`. Um cliente que leia apenas o contrato consegue montar um caminho válido e prever cada
  recusa.
- **SC-006**: O conjunto de coleções normativas sem identificador é verificado por teste. Uma
  coleção nova sem chave, acrescentada por migration futura, aparece na execução da suíte.
- **SC-007**: Depois da migração, `expected_anchors` não existe no esquema e nenhum código a
  referencia.

### Rastreabilidade

| Requisito | Verificado por |
|---|---|
| FR-001 | SC-001, SC-002, SC-005 |
| FR-002 | SC-002 |
| FR-003 | SC-002 |
| FR-004 | SC-002 |
| FR-005 | SC-002 |
| FR-006 | SC-002, SC-005 |
| FR-007 | SC-003 |
| FR-008 | SC-002 |
| FR-009 | SC-002 |
| FR-010 | SC-005 |
| FR-011 | SC-002 |
| FR-012 | SC-006 |
| FR-013 | SC-002 |
| FR-014 | SC-002 |
| FR-015 | SC-007 |
| FR-016 | SC-007 |
| FR-017 | SC-005 |
| FR-018 | SC-005 |
| FR-019 | SC-004 |

## Assumptions

- As entidades endereçáveis carregam UUID no snapshot publicado. Verificado em `edital_snapshot`:
  `profiles`, `schedule`, `competitionModalities` e `normativeRule` têm `id`.
- `requirements` é a única coleção normativa sem identificador, também verificado. FR-012 existe
  para que isso deixe de ser pressuposto e passe a ser guarda.
- **Não há dado persistido a preservar.** É o que autoriza remover toda conversão e compatibilidade
  histórica. Se essa condição mudar antes da implementação, a feature volta a precisar de estratégia
  de migração e esta especificação precisa ser revista.
- A precondição de conteúdo da `003` permanece ativa. O que sai é a âncora de identidade, tornada
  redundante pelo endereçamento por chave.

## Out of Scope

- Conversão de caminhos existentes, compatibilidade entre as duas formas, auditoria de conversão,
  devolução de Retificações e relatório por origem — sem objeto, porque não há dado a preservar.
- Inserção em posição específica (`before=`, `after=`): a interface não a oferece.
- Identificador que não seja UUID.
- Endereçamento item a item de coleções sem identificador — FR-011 as trata como valor atômico.
- Requisitos de desempenho da resolução por chave: as coleções normativas têm dezenas de elementos,
  e nenhuma meta se justifica antes de haver medida.
- Validação de forma do conteúdo alterado. O endereçamento garante **de quem** o ato fala, não que
  o que ele deixa seja um Edital bem formado: `REMOVE` de um campo obrigatório e `REPLACE` de uma
  entidade inteira omitindo campos passam pelas verificações desta feature e pelas quatro
  condições de raiz de `validate_for_publication`. Fechar isso pede validar o snapshot resultante
  contra o schema canônico, na elaboração e na Publicação — defeito anterior à `004`, registrado
  aqui para quem for pegá-lo.
- Integração com o diretório institucional.

## Dependencies

- `003-integridade-e-prontidao` concluída — 71 tarefas, nenhum requisito aberto.
- Clarificações concluídas em 2026-08-29; nenhuma decisão pendente bloqueia a implementação.
