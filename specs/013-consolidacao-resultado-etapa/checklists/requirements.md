# Specification Quality Checklist: Consolidação do Resultado da Etapa

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-02
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

- Validation iteration 1: all items pass; no clarification marker or unresolved placeholder.
- Names such as `avaliacoes_elegiveis`, `resumo_da_etapa` and `comando_de_comissao` identify
  contracts already delivered by the 012, as required by the input review. They do not prescribe a
  new language, framework, API shape or persistence design.
- Validation iteration 2: four defects found by review of the spec against the 012 code were
  corrected; all items still pass. Requirement count is now 42 (`FR-029` was inserted and the
  requirements after it renumbered); success criteria remain 10.
  1. **D-001 × D-003 cancelled each other.** A stage requiring two evaluations is never
     consolidated in V1, so under the original wording the *next* stage would have had zero
     participants forever — breaking a flow the 012 supports today, and contradicting the spec's
     own assumption that such an Edital stays fully evaluable. The progression filter now only
     takes effect once the previous stage has produced its first Result.
  2. **Closing reopening and impediment created an absorbing state.** Refusing the impediment
     outright meant the system refusing to record a conflict of interest discovered after
     consolidation, with no remedy in V1. The impediment is now always recordable; what is refused
     is the inactivation of the source Evaluation, named item by item in the outcome. The absent
     remedy is now stated as an explicit assumption instead of being implied.
  3. **D-005 compared fields that cannot change a Result.** Name, schedule link, weight,
     classificatory character and order were dropped from the comparison — a typo fix in the stage
     name would otherwise have blocked every pending consolidation — and the order clause no longer
     contradicts the edge case about reordering stages.
  4. **The progression filter collided with the 012 scale invariant** forbidding per-row
     authorization in listings. The set-based mechanism is now stated in D-003 and required by
     `FR-004`.
- Validation iteration 3: the requirements block no longer carries code identifiers. Contract and
  field names moved out of `FR-002`, `FR-005`, `FR-012`, `FR-015` and `FR-017` into §6, which now
  names every inherited contract the plan must start from. What remains inside requirements is
  domain vocabulary — the aggregate, its consequences, and the canonical act `resultado:consolidar`.
  This follows the 012's own placement: it names inherited contracts (including
  `pode_atuar_na_etapa(ator, edital, etapa_id)`) in its inherited-contract section, in narrative and
  in its guidance for planning, but never inside a functional requirement. §1 and §2 of this spec
  keep the same freedom.
