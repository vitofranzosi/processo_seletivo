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
- Validation iteration 4: a review of the Phase 0/1 artifacts against the 012 code found four
  consistency defects and two smaller ones; all were corrected in `spec.md`, `research.md`,
  `data-model.md`, `contracts/resultado.md`, `quickstart.md` and `plan.md`. All checklist items
  still pass. Requirement count is now 45 and success criteria 11 (`FR-005`, `FR-006`, `FR-007` and
  `SC-009` were inserted and the items after them renumbered; every cross-artifact FR citation was
  remapped).
  1. **Progression was not transitive.** The spec promised elimination excludes from "any following
     stage", but the rule consulted only the immediately-previous stage: eliminated in stage 1, with
     stage 2 not yet consolidated, an inscription reappeared in stage 3. D-003 now carries two
     distinct rules — elimination excludes transitively with no gate; the habilitation requirement
     applies to the immediately-previous stage and only once it has produced a Result.
  2. **The impediment preserved the access it exists to remove.** Keeping the source Atribuição
     active kept the newly-impeded person's access to the inscription and its documents, because the
     authorization chain does not consult Impedimento — it relies on the impediment having
     deactivated the Atribuição. The impediment now applies in full; the Result survives untouched
     and declares the supervening challenge. Invariant 2 changed from "the source is still eligible"
     to "the source was eligible when consolidated".
  3. **The Result could be born self-contradictory and frozen that way.** The claim that divergence
     was impossible because rows are immutable does not hold — immutability only makes a wrong row
     incorrigible. `versao` was dropped (reachable via the source in the same query) and a
     `BEFORE INSERT` trigger now checks inscription, stage, edital and score against the source.
  4. **The surface touched by progression was understated.** Six places, not three: distribution,
     the individual authorization route, the Mesa listing, the working inscription with its
     documents, the "next pending" navigation and the Minhas Etapas counts. The contract now also
     classifies a distribution request carrying an excluded inscription as a request error.
  5. `progressao.py` was described as pure while prescribing `exists`/`values_list`; it was split
     into a pure domain function and a selector.
  6. The quickstart's anticipated-Atribuição step was unreachable in the order given, and the scale
     figures now read 1.000 consistently across spec, plan, contract and quickstart.
