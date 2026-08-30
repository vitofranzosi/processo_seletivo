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

## Clarifications

### Session 2026-08-29

- Q: O que a verificação deve conferir em cada Perfil e Evento do snapshot resultante? → A: Presença,
  tipo, nulabilidade e formato — o que o contrato da `001` já declara. Campo desconhecido é aceito, e
  nenhuma regra de negócio nova entra.
- Q: Como o portão da Publicação deve ser demonstrado, se a recusa na elaboração torna o caminho
  normal inalcançável? → A: Com o ato malformado já homologado, gravado diretamente — o mesmo padrão
  que a `003` usa para a linha que chega por fora da elaboração.
- Q: Uma Publicação pode materializar várias versões consolidadas, uma por fronteira de vigência.
  Sobre quais delas a verificação incide? → A: Toda fronteira materializada; uma só malformada recusa
  o ato inteiro.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nenhum Edital malformado passa a vigorar (Priority: P1)

Quem publica uma Retificação não consegue deixar vigente um Edital que a Publicação original jamais
teria aceitado. Se o conteúdo resultante tem Perfil ou Evento incompleto, a Publicação é recusada e
nada é materializado.

**Why this priority**: é a razão de a feature existir. Um Edital é ato administrativo, e um Perfil
sem denominação publicado é defeito que atinge quem se inscreve.

**Independent Test**: partir de uma Retificação malformada **já homologada, gravada diretamente**,
publicá-la e verificar que ela é recusada, que nenhuma Publicação, documento ou versão consolidada é
criada, e que o conteúdo vigente continua o de antes.

O caminho normal não serve para testar este portão: a US2 recusa o ato na elaboração, e ele não
chega à Publicação. A linha gravada direto é o que a `003` já usa para o mesmo tipo de cinto — o
caso da Retificação restaurada de backup ou criada por importação, que nunca passou pela borda.

**Acceptance Scenarios**:

1. **Given** uma Retificação homologada que substitui um Perfil inteiro por um objeto que omite
   campos obrigatórios, **When** alguém a publica, **Then** a Publicação é recusada e o conteúdo
   vigente não muda.
2. **Given** uma Retificação homologada que remove um campo obrigatório de um Perfil, **When** alguém
   a publica, **Then** a Publicação é recusada e o conteúdo vigente não muda.
3. **Given** um Edital com uma Retificação de vigência futura já publicada, e portanto com mais de
   uma fronteira a materializar, **When** um ato homologado deixaria malformada apenas a fronteira
   posterior, **Then** a Publicação é recusada — verificar só a primeira faria o Edital vigorar
   malformado semanas depois, sem ninguém ter publicado nada nesse dia.
4. **Given** o mesmo Edital, **When** uma Retificação troca o tipo de um campo — denominação como
   lista, vagas como texto, instante como objeto —, **Then** o ato é recusado como se o campo
   estivesse ausente: um Perfil cuja denominação é `[]` chega à consulta pública e ao PDF tão
   malformado quanto um sem denominação.
5. **Given** uma Retificação que altera apenas valores, mantendo o conteúdo bem formado, **When**
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

- **O ato que não passou pela elaboração.** Uma Retificação restaurada de backup ou criada por
  importação nunca atravessou a recusa da US2. O portão da Publicação é o que a alcança, e é por isso
  que ele não é redundante.
- **O ato encontra o defeito em vez de causá-lo.** Não há conteúdo publicado malformado hoje, e a
  partir desta feature não pode passar a haver. Se ainda assim um existir, a recusa vale: publicar
  um Edital malformado não fica admissível porque outro ato o quebrou antes.
- **Campo desconhecido no conteúdo.** O snapshot pode ganhar campos novos. A verificação exige o que
  o contrato declara e não recusa o que ele não conhece.
- **Coleção vazia.** Um Perfil sem Modalidades e uma lista de requisitos vazia são estados
  legítimos; ausência do campo, ou um valor que não seja lista, é que não é.
- **Nulo onde o contrato o admite.** `reserveLimit` e `endAt` admitem nulo declaradamente; nulo ali
  não é violação, e é o que distingue "não preenchido" de "malformado".
- **Fronteira posterior malformada.** Um ato pode deixar íntegra a versão que passa a vigorar hoje e
  malformada a que vigora na semana seguinte, porque a composição naquela fronteira inclui outros
  atos. A recusa alcança o ato inteiro, e não só a fronteira defeituosa: publicar metade produziria
  linha do tempo com buraco.
- **Alterações que se compensam.** Uma alteração pode remover um campo e outra recriá-lo no mesmo
  ato. O que vale é o resultado, e não os estados intermediários.

## Requirements *(mandatory)*

### A verificação

- **FR-001**: O sistema DEVE verificar o conteúdo normativo **completo** resultante de uma
  Retificação, e não cada alteração isoladamente. `REMOVE` não tem valor a validar, e alterações
  individualmente plausíveis podem compor um resultado inválido.
- **FR-002**: A verificação DEVE acontecer na **elaboração**, sobre o resultado de aplicar todas as
  alterações à versão declarada como base.
- **FR-003**: A verificação DEVE acontecer de novo na **Publicação**, sobre **cada versão
  consolidada que o ato materializa** — uma por fronteira de vigência, e não apenas a que passa a
  vigorar de imediato. Uma única fronteira malformada DEVE recusar o ato inteiro. São dois momentos e
  duas perguntas, como a `003` estabeleceu: o que eu vi ficaria bem formado, e tudo o que vai vigorar
  fica bem formado.
- **FR-004**: A verificação DEVE alcançar cada Perfil e cada Evento do conteúdo, e não apenas a raiz
  do Edital.

### O que conta como bem formado

- **FR-005**: A forma exigida DEVE ser a que o contrato público já declara para Perfil e Evento —
  quais campos são obrigatórios, de que tipo, quais admitem nulo e que formato têm. Descrever a forma
  uma segunda vez criaria duas autoridades sobre a mesma pergunta, e elas divergiriam.
- **FR-006**: DEVEM ser **erro impeditivo**, na classificação que o sistema já usa — informação,
  aviso e erro impeditivo — as quatro violações: campo obrigatório ausente, valor de tipo diferente
  do declarado, nulo onde o contrato não o admite, e valor que não satisfaz o formato declarado.
- **FR-007**: Valor vazio admissível NÃO DEVE ser tratado como ausência nem como tipo errado. Lista
  sem elementos continua sendo lista, e texto em branco onde o contrato admite texto continua sendo
  texto.
- **FR-008**: Campo que o contrato não declara NÃO DEVE ser recusado. O conteúdo normativo pode
  crescer, e recusar o desconhecido tornaria toda evolução de esquema uma quebra.
- **FR-009**: A verificação NÃO DEVE acrescentar regra de negócio — faixa de valores, enumeração
  admissível ou coerência entre campos. Decidir o que um Perfil *deveria* exigir é discussão
  normativa, e não de integridade.

### A recusa

- **FR-010**: A recusa DEVE responder `422`, coerente com a recusa por erro impeditivo que já existe
  na Publicação.
- **FR-011**: A recusa DEVE nomear o **caminho** de cada campo ausente, na mesma forma que a `004`
  estabeleceu — `/profiles/id=<uuid>/name` —, para que quem recebe saiba qual entidade corrigir sem
  consultar a versão vigente.
- **FR-012**: A recusa na Publicação NÃO DEVE deixar Publicação, documento ou versão consolidada
  materializados, como já vale para os demais erros impeditivos.
- **FR-013**: A verificação na Publicação DEVE valer para o ato que chega por fora da elaboração —
  restaurado de backup, criado por importação, gravado direto. É a razão de o portão existir depois
  de a US2 já recusar na borda: sem ela, a garantia dependeria de todo ato ter passado por lá.

### Limites

- **FR-014**: Uma Retificação bem formada DEVE continuar publicável sem etapa nova, sem campo novo
  no contrato e sem mudança no que quem elabora precisa preencher.
- **FR-015**: A verificação NÃO DEVE alterar o endereçamento, as precondições de conteúdo nem as
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
  Edital que a Publicação original recusaria — em nenhuma das fronteiras de vigência que ela
  materializa.

### Rastreabilidade

| Requisito | Critério |
| --- | --- |
| FR-001, FR-002 | SC-001, SC-002 |
| FR-003, FR-012, FR-013 | SC-001, SC-002, SC-005 |
| FR-004, FR-005 | SC-005 |
| FR-006, FR-007, FR-008 | SC-004, SC-005 |
| FR-009 | SC-004 |
| FR-010, FR-011 | SC-003 |
| FR-014, FR-015 | SC-004 |

## Avaliação de Proteção de Dados (LGPD)

**Não aplicável.** O princípio III da Constituição exige que cada especificação avalie os requisitos
da LGPD; a avaliação desta é curta porque a feature não os alcança:

- **Nenhum dado pessoal.** O conteúdo verificado é normativo — título, descrição, Perfis, Cronograma
  e Modalidades de um Edital. Dados de pessoas inscritas não existem neste conteúdo e não são
  tocados.
- **Nenhum acesso novo.** A feature não cria endpoint, permissão, papel ou consulta. Ela acrescenta
  uma recusa a operações que já exigem `retificacao:elaborar` e `retificacao:publicar`.
- **Nenhuma superfície nova de exposição.** As mensagens de recusa nomeiam caminho de campo
  normativo e identificador de entidade do Edital — o mesmo vocabulário que a consulta pública já
  publica.
- **Nenhuma retenção nova.** Nada é persistido que já não fosse; a verificação decide e não guarda.

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
- **Ampliar o que é obrigatório, e regras de negócio.** Esta feature faz valer a forma que o
  contrato já declara. Faixas de valor, enumerações admissíveis e coerência entre campos —
  `reserveLimit` compatível com o tipo de reserva, `endAt` depois de `startAt` — são decisão
  normativa, e não de integridade (FR-009).

## Assumptions

- **A verificação vale para todo caminho de Publicação**, e não só para a Retificação. O portão é o
  mesmo, e o conteúdo produzido pela composição original já é bem formado por construção — de modo
  que aplicá-la aos dois caminhos não muda o comportamento do original e evita duas regras para a
  mesma pergunta.
- **A autoridade é o contrato, não o montador de snapshot.** `PerfilInput` e `EventoInput` já
  declaram obrigatoriedade, tipo, nulabilidade e formato. O montador produz também campos que o
  contrato não declara; esses seguem aceitos, e não exigidos.
- **Um conteúdo base já malformado bloqueia o ato que não o corrige.** Não há como isso existir hoje,
  e a partir desta feature não passa a haver. Preferir o bloqueio mantém a garantia de SC-005 sem
  exceção, ao custo de um caso que não ocorre.
- **A classificação de severidade existente basta.** Erro impeditivo já bloqueia a Publicação e já é
  reportado; a feature acrescenta achados a esse mecanismo.
