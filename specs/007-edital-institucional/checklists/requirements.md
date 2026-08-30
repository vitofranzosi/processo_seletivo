# Specification Quality Checklist: Edital Institucional

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
**Revalidated**: 2026-08-30, após revisão externa e `$speckit-clarify`
**Feature**: [spec.md](../spec.md)

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [ ] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [ ] No implementation details leak into specification

**Situação: 12/16.** Os quatro itens abertos são todos a mesma coisa vista de quatro ângulos, e são
uma divergência **deliberada e declarada** do template — não uma pendência a resolver antes do
`/plan`. Ver abaixo.

## A divergência deliberada

Quatro itens do template exigem uma spec livre de detalhe técnico e legível por stakeholder não
técnico. Esta spec não é isso, e as anteriores do projeto também não são.

**O que ela contém que o template desaprova:** caminhos de arquivo e linha, `SCHEMA_VERSION`, nomes
de chave canônica (`duties`, `workload`, `compensation`), a fixture de bytes, a exigência de que
duas entregas se integrem juntas, e instruções dirigidas ao `/plan`.

**Por que permanece assim.** O projeto opera sob uma Constituição que exige rastreabilidade entre
especificação, plano, tarefas, implementação e testes, e que proíbe que comportamento acidental vire
regra sem decisão documentada. Numa base madura, a diferença entre um requisito verificável e uma
intenção vaga é justamente a âncora: "o documento não deve expor identificador técnico" é opinião;
"a raiz do snapshot leva `schemaVersion`, `editalId` e `processoId`, e o renderizador é função pura
dela, logo nomear o Processo exige campo novo" é um requisito que se pode contestar com o código na
mão. **Foi exatamente essa âncora que permitiu à revisão externa encontrar a contradição da primeira
redação** — uma spec sem elas teria escondido o defeito atrás de linguagem agradável.

**O que isso custa e como é mitigado.** Custa legibilidade para quem não conhece o repositório. A
mitigação é estrutural: as âncoras vivem em blocos de racional *em itálico*, e o requisito normativo
é sempre a frase antes delas. Lendo só as frases em negrito e ignorando os itálicos, obtém-se uma
spec de negócio.

**O que continua proibido, e é o que o item realmente protege.** A spec não escolhe biblioteca, não
desenha classe, não define assinatura de função, não escolhe estratégia de persistência e não
prescreve estrutura de arquivos. As "Instruções para o `/plan`" declaram limites — o que não pode
ser construído — e não desenho.

**Decisão registrada:** os quatro itens permanecem marcados como não atendidos, com esta
justificativa, em vez de marcados como atendidos com uma nota explicando por que não seriam. O
`/plan` prossegue.

## Notas de validação

**Sobre `SCHEMA_VERSION`, `edital_snapshot` e o catálogo de seções.** São vocabulário de domínio
consolidado do produto, presentes na Constituição e nas specs `004`, `005` e `006`, não escolhas
tecnológicas desta feature.

**Sobre a ausência de `[NEEDS CLARIFICATION]`.** As três decisões abertas foram fechadas por
`$speckit-clarify` e estão registradas em `## Clarifications`: identificação institucional do
Processo no snapshot v3; "concluída" definida por gravação e não por visita; catálogo de autoridades
declarado em código. Duas outras foram resolvidas por decisão registrada seguindo precedente do
próprio `profiles` — forma canônica dos campos novos e formatação decimal pt-BR.

**Trava de escopo declarada.** A seção `Rastreabilidade com a auditoria` fecha o conjunto: dezesseis
achados abertos, todos cobertos, nenhum a mais. A correspondência **não é um-para-um** e a seção diz
isso explicitamente — o achado 11 exige dois requisitos e os achados 18 e 19 se resolvem no mesmo.
O que a tabela garante é cobertura e fechamento, não bijeção.

**Item acrescentado além da lista de entrada.** O achado 17 — a confirmação de ato exibindo a chave
interna (`Ato registrado: submeter`) — não constava da enumeração de escopo recebida. Entrou como
FR-041 por ser da mesma classe que FR-002 (forma interna vazando para o usuário) e por ser o último
resíduo pendente do pacote que a `006.1` começou. É o único acréscimo, e é destacável sem afetar
nenhum outro requisito.

**Requisitos acrescentados nesta revalidação.** FR-044 a FR-048 cobrem a avaliação de LGPD exigida
pelo princípio III da Constituição, ausente na primeira redação. Critérios de acessibilidade
entraram em FR-024, FR-032, FR-033, FR-038 e FR-040, e são verificados por SC-009b.
