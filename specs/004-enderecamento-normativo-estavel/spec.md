# Feature Specification: Endereçamento Normativo por Chave Estável

**Feature Branch**: `004-enderecamento-normativo-estavel`

**Created**: 2026-08-29

**Status**: Draft — não iniciada. Depende da `003-integridade-e-prontidao`.

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

### Session pendente

Nenhuma sessão de clarificação foi realizada. As questões abaixo precisam de resposta antes do
planejamento e estão registradas como abertas, não como suposições.

- **Q1**: A forma nova substitui a posicional ou convivem? Substituir quebra clientes existentes;
  conviver mantém a superfície do defeito viva para quem continuar usando índices.
- **Q2**: Qual a sintaxe do caminho por chave? JSON Pointer não tem seleção por atributo, então
  qualquer escolha é extensão local — `/profiles/id=<uuid>/name`, `/profiles[<uuid>]/name` ou um
  campo estruturado ao lado do `targetPath`. A terceira evita inventar dialeto de Pointer.
- **Q3**: O histórico é migrado ou preservado como está? Reescrever caminho de Retificação
  publicada é alterar ato normativo já produzido, o que a Constituição proíbe. Preservar significa
  que a consulta histórica precisa entender as duas formas.
- **Q4**: `ADD` em lista passa a endereçar como? Inserir não tem entidade alvo; precisa de âncora
  relativa (`antes de <uuid>`, `depois de <uuid>`) ou continua só com acréscimo ao fim.
- **Q5**: Entidades sem `id` — os itens de `requirements`, que são texto — passam a ter chave, ou
  continuam endereçadas por posição com a contenção da `003`?

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
- Retificação em curso, elaborada na forma antiga, quando a feature entra em produção.

## Requirements *(mandatory)*

Os requisitos abaixo são preliminares e dependem das clarificações Q1 a Q5.

- **FR-001**: Alterações Normativas DEVEM poder endereçar Perfis, Eventos e Modalidades pela chave
  estável da entidade, independentemente da posição que ela ocupe na coleção.
- **FR-002**: A resolução por chave DEVE recusar explicitamente quando a entidade endereçada não
  existir na versão sobre a qual o ato vigora.
- **FR-003**: A precondição de conteúdo da `003` DEVE continuar valendo sobre o endereçamento novo:
  identificar a entidade certa não dispensa verificar que o conteúdo dela é o que estava à vista.
- **FR-004**: A composição DEVE recusar coleção com chave repetida.
- **FR-005**: Retificações publicadas antes desta feature NÃO DEVEM ter seus caminhos reescritos.
- **FR-006**: A consulta histórica DEVE reproduzir corretamente atos em ambas as formas.
- **FR-007**: A interface administrativa DEVE emitir a forma nova sem exigir conhecimento de
  representação de quem elabora.
- **FR-008**: O contrato público DEVE documentar a forma nova, sua sintaxe e seus erros.
- **FR-009**: A âncora de identidade introduzida pela `003` DEVE ser revista: onde o endereçamento
  já é por chave, ela se torna redundante; onde não for (coleções sem chave), permanece.

## Success Criteria *(mandatory)*

- **SC-001**: Duas Retificações sobre entidades distintas da mesma versão publicam ambas, sem
  reelaboração.
- **SC-002**: Nenhum ato publicado antes desta feature muda de efeito depois dela.
- **SC-003**: A consulta temporal produz, para todo instante, o mesmo conteúdo que produzia antes.
- **SC-004**: Nenhuma Retificação atinge entidade diferente da endereçada, em qualquer composição.

## Assumptions

- As entidades relevantes já carregam identificador estável no snapshot publicado. Isso foi
  verificado: `Perfil`, `Evento` e `Modalidade` têm `id`.
- A contenção da `003` permanece ativa durante e depois desta feature; esta feature reduz a
  frequência com que ela precisa recusar, não a substitui.

## Out of Scope

- Integração com o diretório institucional.
- Qualquer mudança no ciclo de vida da Retificação ou nas regras de vigência.
- Endereçamento de coleções de texto simples, se Q5 decidir mantê-las por posição.

## Dependencies

- `003-integridade-e-prontidao` concluída, incluindo os requisitos hoje abertos.
- Resposta às clarificações Q1 a Q5 antes do planejamento.
