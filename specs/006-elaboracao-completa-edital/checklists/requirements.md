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

## Itens que permanecem em aberto

Nenhum bloqueia `$speckit-tasks`.

- A redação institucional inicial das seções textuais é genérica nesta versão. Adequá-la ao texto do
  Cefor é trabalho editorial, declarado em `Assumptions`, e não altera requisito.
- A forma decimal canônica de peso e nota mínima é transcrita no plano; se o `openapi.yaml` declarar
  outra, vale a do contrato — a conferência entre transcrição e contrato é teste existente.
