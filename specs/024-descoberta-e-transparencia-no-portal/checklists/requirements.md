# Specification Quality Checklist: Descoberta e Transparência no Portal Público

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-09
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

## Notas da validação

Três observações da passada de revisão, todas resolvidas na spec:

1. **A §1 cita nomes de campo do conteúdo publicado** (`schedule`, `duties`, `workload`,
   `compensation`) e os arquivos onde a verificação foi feita. É evidência do achado, não requisito:
   nenhum FR menciona nome de campo, e a §1 existe justamente para que a feature não seja lida como
   "melhorar a página". Mantido de propósito, como a `022` manteve o inventário de origem.

2. **A contradição que o briefing de origem carregava foi desfeita antes de virar requisito.** Ele
   marcava busca e filtro como prioridade máxima e, no fecho, dizia para não complicar a página antes
   de haver volume. A spec resolve pela D-003 e pela ordem da §8: descoberta é P2, e o sinal que a
   promoveria está nomeado.

3. **Quatro recomendações do briefing não viraram requisito**, e a §7 diz por quê: instrumentação de
   funil (Princípio III), campos que o domínio não tem, renomear "Entrar", e recomendação de vagas.
   Duas outras já estavam entregues — convite por vaga e informação fora do PDF — e viraram linha da
   §2, não escopo.

## Numeração

Identificadores conferidos contra o espaço global antes de escrever: `FR-125`–`FR-152`,
`UX-016`–`UX-019` e `SC-040`–`SC-047` não colidem com nenhuma spec anterior. As decisões `D-001`–
`D-009` são por feature, como o teste de citações verifica.

**Três de sufixo de letra nasceram no `/speckit-analyze`**, e por isso não estão nos intervalos
acima: `FR-131a` (o marcador de vigente é condicional), `FR-140a` (onde a ordenação se aplica) e
`FR-146a` (a lista é única quando há consulta). A matriz de rastreabilidade tem de citá-los **um a
um** — o teste não aceita intervalo cobrindo sufixo de letra.

A conferência foi refeita contra a **`023` em curso noutra worktree**
(`023-criar-a-partir-de-edital-anterior`), que o `specs/` desta árvore não enxerga: ela define
`FR-001`–`FR-020` e `SC-001`–`SC-008`, e nenhum deles cai na faixa desta feature. O teste de
citações só rodará contra as duas depois que ambas estiverem na mesma árvore — vale reconferir no
merge.
