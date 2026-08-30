# Specification Quality Checklist: Elaboração Completa do Edital

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Régua própria desta feature

O princípio VI da Constituição 1.1.1 acrescenta uma exigência que as features anteriores não
tiveram. Ela é verificada aqui, e não só no `plan`.

- [x] Cada entrega termina em capacidade demonstrável pelo canal do ator, e nenhuma termina em
      infraestrutura pronta
- [x] Existe cenário de ponta a ponta declarado — `SC-009`
- [x] O cenário é executável sem manipulação de banco, chamada manual de API ou shell
- [x] O cenário é executável pelos atores que o sistema realmente exige — verificado: a publicação
      recusa quem elabora, homologa e publica sozinho, e a demonstração declara dois atores
- [x] O backlog desta feature deriva da jornada, e não do `Out of Scope` da feature anterior

## Notas da avaliação

### Ressalva ao item "nenhum detalhe de implementação"

O item permanece marcado, com esta ressalva explícita. Dois requisitos são deliberadamente técnicos —
FR-015, que exige modo explícito no renderizador, e FR-045, que fixa o incremento da versão canônica.
Nenhum dos dois escolhe solução para um problema de produto: os dois **protegem mecanismos que já
existem** e cuja violação não seria observável pelo usuário até ser tarde. Um documento de prévia
indistinguível do publicado e duas formas declarando a mesma versão canônica são defeitos que só
aparecem depois de terem causado dano. Onde a spec podia deixar a decisão para o `plan`, deixou.

### Citações de código na especificação

A spec cita `arquivo:linha` em vários requisitos. Isso normalmente seria vazamento de implementação,
e aqui é deliberado: cada citação sustenta uma **afirmação de fato sobre o sistema atual** que
motiva o requisito — o botão que só aparece na lista vazia, a etapa somente leitura, a recusa de
segregação de funções. Sem a citação, o requisito pareceria arbitrário e a revisão não teria como
conferi-lo. A regra que se manteve foi: citar para provar o problema, nunca para prescrever a
solução.

### Reavaliação após `$speckit-clarify` (2026-08-30)

Três decisões de produto foram fechadas por pergunta e duas por verificação no código.

**Etapas por Edital ou por Perfil (Q1).** A spec conflitava com as Restrições e Invariantes do
Domínio, que admitem Perfis com Etapas distintas. Resolvido por decisão registrada: Etapas por
Edital nesta versão, com o custo de reversão declarado e a permissão constitucional não exercida —
não violada.

**Conjunto de seções (Q2).** Fixo. Acrescentar, remover e reordenar seções foi para o `Out of
Scope`, o que separa documento institucional estruturado de construtor de documentos.

**Alcance da prévia (Q3).** Elaboração, submetido e homologado, com origem única de conteúdo.

**Faixa do percentual e `SC-009`**, resolvidos por verificação. O `SC-009` como estava escrito era
**indemonstrável**: a publicação recusa quem elaborou, homologou e publicou sozinho. Foi corrigido
para exigir ao menos dois atores.

### Reavaliação após revisão adversarial do plano (2026-08-30)

A revisão do `plan` encontrou quatro defeitos, todos verificados no código antes de aceitos. Dois
alteraram a spec:

**Topologia das seções depois da publicação.** A forma declarada verifica um campo por vez, de
propósito. Sem verificação própria, uma Retificação poderia acrescentar seção, remover uma do
catálogo, trocar tipo ou ordem, esvaziar uma textual ou dar conteúdo a uma gerada — desmontando o
catálogo fixo exatamente onde ele mais importa. Virou FR-041, e a referência de Etapa a Evento
passou a valer também sobre o conteúdo resultante de Retificação (FR-022).

**Identidade das seções.** A spec falava em "chave estável" sem distinguir identidade de rótulo. O
seletor da gramática só aceita UUID, de modo que a chave textual do catálogo seria recusada e a
coleção ficaria inendereçável. FR-039 passou a exigir identidade estável e a registrar que ela é
UUID, com a chave textual como rótulo legível.

**Uma afirmação foi corrigida por ser falsa.** O `Contexto` e o antigo FR-045 diziam que a `005` já
faz a suíte falhar quando uma coleção do snapshot não está declarada. A `005` cobre a coerência
estrutural do que está declarado, mas a conferência da forma publicada é feita contra uma lista
nomeada item a item (`tests/contract/test_forma_publicada.py:67-70`) — acrescentar coleção e
esquecer de declará-la não falharia nada. Criar essa cobertura virou requisito e tarefa.

### Reavaliação após `$speckit-analyze` (2026-08-30)

A análise encontrou uma violação constitucional e cinco inconsistências altas, todas verificadas no
código antes de aceitas.

**Identidade da Regra Normativa (constitucional).** A correção da identidade das modalidades parava
no meio: `RegraNormativa` também é criada sem o `id` recebido, e esse `id` viaja no conteúdo
publicado. Cada gravação continuaria trocando a identidade de um objeto normativo. Entrou em FR-027 e
FR-029.

**Versão do fundamento.** O formulário oferecia fundamento e percentual, mas `version` é obrigatório
no serializer e no command desde a `001`: nenhuma regra nova seria gravável. Entrou em FR-026.

**Contrato à frente da implementação.** O delta declarava `sections` na entrada do rascunho na
Entrega 3, quando a API só passa a aceitá-la na Entrega 5 — contrato falso por dois PRs. A entrada
foi separada da saída.

**Dependência entre histórias.** O grafo dizia US2 e US3 independentes da US1, mas os critérios de
aceite delas exigem a prévia. A dependência passou a ser declarada.

**Recusa de identificador alheio.** O contrato dizia 422; a recusa existente é 409 e já tem teste.
Prevaleceu o código.

**Forma decimal.** "Padrão no molde de `INSTANTE`" era insuficiente: o padrão só é avaliado quando há
formato declarado, e o formato exige leitor registrado. Ficou explícito, e o padrão sem sinal recusa
nota mínima negativa sem verificação adicional.

### Segunda passada do `$speckit-analyze` (2026-08-30)

Duas críticas e duas menores, todas verificadas.

**A identidade parava na porta da API.** A correção anterior fechou o command e a interface, mas
`CompetitionModalitySerializer` e `NormativeRuleSerializer` não declaram `id`
(`editais/api/serializers.py:7-22`), ao contrário de `ProfileSerializer`. O identificador nunca
chegaria ao command pela API, e o teste de recusa de identificador alheio não teria o que recusar.
Virou tarefa própria, no mesmo PR da história.

**"Publicação vigente" era conceito inexistente.** Uma Retificação pode ser publicada com vigência
futura (`publicacoes/application/retificacoes.py:546-548`), e a vigência pertence à Versão
Consolidada (`publicacoes/application/selectors.py:26`), que **não tem documento próprio**. O
detalhe passa a oferecer o documento de cada Publicação, identificado pelo ato, sem rotular nenhum
como vigente. FR-002 registra por quê, para que a ideia não volte como feature.

**Forma decimal.** `^\d+(\.\d{1,4})?$` não descrevia `decimal(7,4)`: aceitava inteiro de qualquer
tamanho e casas de menos. Passou a `^\d{1,3}\.\d{4}$`. E a proibição de sinal impunha peso não
negativo sem que a regra existisse: agora FR-020 declara que o peso informado é maior que zero, pelo
mesmo raciocínio do percentual — a ausência é que exprime "não pondera".

**Documentação residual.** Cenários da US3, resumo da Entrega 4 no plano e o comando do quickstart
mencionavam só fundamento e a identidade da modalidade. Os três passaram a provar exatamente o que a
correção fez.

### Terceira passada do `$speckit-analyze` (2026-08-30)

Uma crítica e três menores. A crítica é a terceira aparição do mesmo defeito, agora um nível abaixo.

**A verificação de identidade parava um nível acima do contêiner.** `RegraNormativa` é `OneToOne` com
`ModalidadeConcorrencia` (`editais/models/perfis.py:63-66`), mas a recusa que eu tinha escrito só
alcançava outro Perfil ou outro Edital. Duas Modalidades irmãs do mesmo Perfil poderiam trocar a
identidade das suas Regras sem que nada acusasse, e a identidade estável passaria a designar outra
relação normativa. FR-029 passou a exigir a verificação **no nível do contêiner de cada entidade**.

**Identidade da linha nova na interface.** A gravação preserva o `id` recebido, mas nada mandava
gerá-lo: uma modalidade criada pela tela nasceria sem identidade, e não haveria o que preservar. A
geração dos dois UUID na view do fragmento entrou em T056, e a forma publicada da Regra em T058.

**Forma decimal, terceira versão.** `^\d{1,3}\.\d{4}$` ainda aceitava `001.0000`, que o sistema
nunca escreve — e uma Retificação semanticamente nula poderia alterar o hash. Passou a
`^-?(0|[1-9]\d{0,2})\.\d{4}$`. O sinal voltou de propósito: o padrão descreve **forma**, e a faixa
é regra de domínio. Deixar o padrão recusar o sinal foi exatamente como uma invariante não declarada
entrou por uma expressão regular, na passada anterior.

**Resíduos documentais.** Numeração dos cenários da US3, o resumo da Entrega 1 no plano e a linha do
contrato sobre `profiles`.

### Quarta passada do `$speckit-analyze` (2026-08-30)

Um único elo, e ele foi encontrado pela pergunta que fecha a classe inteira: *para cada entidade que
o snapshot identifica, quem é o contêiner dela, e a gravação preserva e verifica a identidade nesse
nível?*

**Etapa contra Edital.** A coleção nova repetia, por omissão, o defeito que as três passadas
anteriores corrigiram nas outras entidades: o `id` era preservado e nunca recusado quando já
pertencesse a outro Edital, e nada mandava gerá-lo na linha nova. Entrou em FR-018, T037, T039, T040
e T044.

**A topologia ficou declarada por inteiro** em `data-model.md`, e não como uma sequência de
correções pontuais: Perfil, Evento e Etapa contra o Edital; Modalidade contra o Perfil; Regra contra
a Modalidade; Seção com identidade determinística, sem identificador externo. É o que permite
verificar a completude de uma vez, em vez de descobrir o elo seguinte a cada revisão.

## Itens que permanecem em aberto

Nenhum bloqueia a implementação.

- A redação institucional inicial das seções textuais é genérica nesta versão. Adequá-la ao texto do
  Cefor é trabalho editorial, declarado em `Assumptions`, e não altera requisito.
- A forma decimal canônica de peso e nota mínima é transcrita no plano; se o `openapi.yaml` declarar
  outra, vale a do contrato — a conferência entre transcrição e contrato é teste existente.
