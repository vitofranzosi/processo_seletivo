# Specification Quality Checklist: Quem faz o quê

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-13
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

## Notes

- **Primeira passada (13/11)**: três marcadores, os três decisões de produto, que vão ao usuário pelo
  `/speckit-clarify`: quem vê o bloco (FR-6901), como aparecem os papéis da unidade (FR-6907) e se a
  avaliação mostra a contagem por pessoa (FR-6913).
- **Nomes de código na spec.** `MembroComissao`, `Alcance.ativo` e `desde` aparecem nas entidades, num
  caso-limite e numa decisão, como nas specs anteriores desta família (`127`, `160`): são o vocabulário
  com que o estudo e o código nomeiam as bases. Nenhum requisito prescreve a implementação.
- **Clarify (13/11)**: os três marcadores e uma quarta pergunta (bloco separado ou anotações em
  "O que fazer agora") foram respondidos pelo usuário, todos na alternativa recomendada; nenhum
  marcador resta. A quarta virou a D-010.
- O SC-2297 é humano e fica pendente, como o SC-2281 da `160`.
