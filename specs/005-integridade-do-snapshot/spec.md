# Feature Specification: Integridade do Snapshot Normativo

**Feature Branch**: `005-integridade-do-snapshot`

**Created**: 2026-08-29

**Status**: Draft

**Input**: Limite registrado no *Out of Scope* da `004`, encontrado em revisão adversarial: o
endereçamento garante **de quem** o ato fala, não que o que ele deixa seja um Edital bem formado.

## Contexto

A `003` impediu que uma Retificação sobrescrevesse outra em silêncio. A `004` fez cada Alteração
nomear a entidade de que fala. Nenhuma das duas verifica o que o ato **deixa**.

Duas portas produzem hoje um Perfil mutilado, e nenhuma é recusada:

```
REPLACE /profiles/id=<uuid>   com {"id": "<uuid>", "code": "X"}   ← omite os demais campos
REMOVE  /profiles/id=<uuid>/name                                  ← apaga um campo obrigatório
```

Medido: o Perfil publicado fica com `id` e `code`, a consulta pública devolve **200** e o documento
PDF é gerado nesse estado. Um Perfil normativo sem denominação, sem requisitos e sem vagas passa a
vigorar.

A verificação que existe hoje olha quatro condições na **raiz** do Edital — título, ao menos um
Perfil, ao menos um Evento, descrição — e nada sobre a forma de cada Perfil ou Evento.

**A segunda porta é a que decide o desenho.** `REMOVE` não tem valor a validar, e uma sequência de
alterações individualmente plausíveis também pode terminar inválida. Por isso o que se valida é o
**resultado**, e não cada alteração.

A Constituição já exige isto no princípio IV: *"A operação DEVE validar inconsistências,
classificá-las como informação, aviso ou erro impeditivo e bloquear a publicação diante de erro
impeditivo."* A exigência vale para a Publicação; o que falta é ela alcançar o conteúdo que uma
Retificação faz vigorar, e não só a raiz do Edital.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nenhum Edital malformado passa a vigorar (Priority: P1)

Quem publica uma Retificação não consegue deixar vigente um Edital que a Publicação original jamais
teria aceitado. Se o conteúdo resultante tem Perfil ou Evento incompleto, a Publicação é recusada e
nada é materializado.

**Why this priority**: é a razão de a feature existir. Um Edital é ato administrativo, e um Perfil
sem denominação publicado é defeito que atinge quem se inscreve.

**Independent Test**: elaborar uma Retificação que remova um campo obrigatório de um Perfil, levá-la
até a Publicação e verificar que ela é recusada, que nenhuma Publicação ou versão consolidada é
criada, e que o conteúdo vigente continua o de antes.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com Perfis completos, **When** uma Retificação substitui um Perfil
   inteiro por um objeto que omite campos obrigatórios, **Then** o ato é recusado e o conteúdo
   vigente não muda.
2. **Given** o mesmo Edital, **When** uma Retificação remove um campo obrigatório de um Perfil,
   **Then** o ato é recusado e o conteúdo vigente não muda.
3. **Given** uma Retificação que altera apenas valores, mantendo o conteúdo bem formado, **When**
   ela é publicada, **Then** ela publica normalmente — a verificação nova não recusa ato legítimo.

---

### User Story 2 - Quem elabora descobre antes de submeter (Priority: P2)

Quem compõe a Retificação recebe a recusa na elaboração, com o caminho do que está faltando, em vez
de descobrir depois de a submissão e a homologação já terem consumido o tempo de outras pessoas.

**Why this priority**: não muda o que é impedido, muda quando. Sem ela a garantia da US1 continua de
pé, e por isso é P2; com ela o erro custa uma tela em vez de um ciclo de aprovação.

**Independent Test**: enviar a mesma Retificação malformada na criação e verificar que ela é
recusada ali, com uma mensagem que nomeia o caminho do campo ausente.

**Acceptance Scenarios**:

1. **Given** uma versão base bem formada, **When** alguém elabora uma Retificação cujo resultado
   deixaria um Perfil sem denominação, **Then** a criação é recusada e a mensagem nomeia o caminho
   do campo ausente.
2. **Given** a mesma recusa, **When** quem elabora corrige o conteúdo e reenvia, **Then** o ato é
   aceito sem exigir nenhuma etapa a mais.

---

### Edge Cases

- **O ato encontra o defeito em vez de causá-lo.** Não há conteúdo publicado malformado hoje, e a
  partir desta feature não pode passar a haver. Se ainda assim um existir, a recusa vale: publicar
  um Edital malformado não fica admissível porque outro ato o quebrou antes.
- **Campo desconhecido no conteúdo.** O snapshot pode ganhar campos novos. A verificação exige a
  presença do que é obrigatório e não recusa o que não conhece.
- **Coleção vazia.** Um Perfil sem Modalidades e uma lista de requisitos vazia são estados
  legítimos; ausência do campo é que não é.
- **Alterações que se compensam.** Uma alteração pode remover um campo e outra recriá-lo no mesmo
  ato. O que vale é o resultado, e não os estados intermediários.

## Requirements *(mandatory)*

### A verificação

- **FR-001**: O sistema DEVE verificar o conteúdo normativo **completo** resultante de uma
  Retificação, e não cada alteração isoladamente. `REMOVE` não tem valor a validar, e alterações
  individualmente plausíveis podem compor um resultado inválido.
- **FR-002**: A verificação DEVE acontecer na **elaboração**, sobre o resultado de aplicar todas as
  alterações à versão declarada como base.
- **FR-003**: A verificação DEVE acontecer de novo na **Publicação**, sobre o conteúdo consolidado
  que passará a vigorar. São dois momentos e duas perguntas, como a `003` estabeleceu: o que eu vi
  ficaria bem formado, e o que vai vigorar fica bem formado.
- **FR-004**: A verificação DEVE alcançar cada Perfil e cada Evento do conteúdo, e não apenas a raiz
  do Edital.

### O que conta como bem formado

- **FR-005**: A forma exigida DEVE ser a que o próprio sistema produz ao montar um snapshot
  publicado. Uma segunda descrição do que é um Perfil divergiria da primeira.
- **FR-006**: A ausência de um campo obrigatório DEVE ser **erro impeditivo**, na classificação que
  o sistema já usa — informação, aviso e erro impeditivo.
- **FR-007**: Campo presente com valor vazio admissível — lista sem elementos, texto opcional em
  branco — NÃO DEVE ser tratado como ausência.
- **FR-008**: Campo que o sistema não conhece NÃO DEVE ser recusado. O conteúdo normativo pode
  crescer, e recusar o desconhecido tornaria toda evolução de esquema uma quebra.

### A recusa

- **FR-009**: A recusa DEVE responder `422`, coerente com a recusa por erro impeditivo que já existe
  na Publicação.
- **FR-010**: A recusa DEVE nomear o **caminho** de cada campo ausente, na mesma forma que a `004`
  estabeleceu — `/profiles/id=<uuid>/name` —, para que quem recebe saiba qual entidade corrigir sem
  consultar a versão vigente.
- **FR-011**: A recusa na Publicação NÃO DEVE deixar Publicação, documento ou versão consolidada
  materializados, como já vale para os demais erros impeditivos.

### Limites

- **FR-012**: Uma Retificação bem formada DEVE continuar publicável sem etapa nova, sem campo novo
  no contrato e sem mudança no que quem elabora precisa preencher.
- **FR-013**: A verificação NÃO DEVE alterar o endereçamento, as precondições de conteúdo nem as
  invariantes de identidade que a `003` e a `004` estabeleceram.

### Key Entities

- **Snapshot normativo**: o conteúdo canônico de um Edital publicado — título, descrição, Perfis e
  Cronograma. É sobre ele que a verificação incide.
- **Achado de validação**: já existe, com severidade de informação, aviso ou erro impeditivo. Esta
  feature acrescenta achados, não uma segunda maneira de reportá-los.

## Success Criteria *(mandatory)*

- **SC-001**: Uma Retificação que substitua um Perfil inteiro omitindo campos obrigatórios é
  recusada, tanto na elaboração quanto na Publicação, e o conteúdo vigente permanece inalterado.
- **SC-002**: Uma Retificação que remova um campo obrigatório de um Perfil é recusada nos mesmos dois
  momentos, com o mesmo resultado sobre o conteúdo vigente.
- **SC-003**: A mensagem de recusa permite identificar qual entidade corrigir e qual campo falta, sem
  consultar a versão vigente.
- **SC-004**: Uma Retificação bem formada — alteração de valores, acréscimo e remoção de entidades —
  continua publicando, e o número de etapas para publicá-la não muda.
- **SC-005**: Depois desta feature, não existe caminho pelo qual uma Retificação deixe vigente um
  Edital que a Publicação original recusaria.
- **SC-006**: A suíte permanece verde nas duas execuções — SQLite e PostgreSQL — e a cobertura com
  ramos do código escrito nesta feature é integral.

### Rastreabilidade

| Requisito | Critério |
| --- | --- |
| FR-001, FR-002 | SC-001, SC-002 |
| FR-003, FR-011 | SC-001, SC-002, SC-005 |
| FR-004, FR-005 | SC-005 |
| FR-006, FR-007, FR-008 | SC-004, SC-005 |
| FR-009, FR-010 | SC-003 |
| FR-012, FR-013 | SC-004, SC-006 |

## Out of Scope

- **Validação isolada de cada `newValue`.** Ela não alcança `REMOVE`, que não tem valor, nem a
  sequência de alterações que só é inválida no conjunto. Pode entrar depois, para errar mais cedo e
  com mais precisão, mas como complemento e nunca como substituto de FR-001.
- **Resolução de subschema por `targetPath`.** Exigiria mapear cada caminho ao pedaço de esquema que
  ele endereça; a verificação do resultado completo não precisa disso.
- **Infraestrutura de múltiplas versões de esquema.** Há uma versão canônica; construir o
  versionamento antes de existir a segunda seria decidir por antecipação.
- **Migração de conteúdo histórico.** O sistema não está em produção e não há ato publicado a
  corrigir.
- **Ampliar o que é obrigatório.** Esta feature faz valer a forma que o sistema já produz; discutir
  se um Perfil deveria exigir mais campos é decisão normativa, e não de integridade.

## Assumptions

- **A verificação vale para todo caminho de Publicação**, e não só para a Retificação. O portão é o
  mesmo, e o conteúdo produzido pela composição original já é bem formado por construção — de modo
  que aplicá-la aos dois caminhos não muda o comportamento do original e evita duas regras para a
  mesma pergunta.
- **Obrigatório é o que o sistema sempre produz.** Um campo que o montador de snapshot emite para
  toda entidade é obrigatório; um que ele emite às vezes, não.
- **Um conteúdo base já malformado bloqueia o ato que não o corrige.** Não há como isso existir hoje,
  e a partir desta feature não passa a haver. Preferir o bloqueio mantém a garantia de SC-005 sem
  exceção, ao custo de um caso que não ocorre.
- **A classificação de severidade existente basta.** Erro impeditivo já bloqueia a Publicação e já é
  reportado; a feature acrescenta achados a esse mecanismo.
