# Specification Quality Checklist: Convocar do cadastro de reserva, na ordem publicada e dentro da validade

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-21
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — as duas perguntas foram respondidas em 21/10: nenhum
  limite no tempo (`D-005`), e a quantidade acrescida só na gestão (`FR-2468`)
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

- **Nomes do domínio já existentes aparecem de propósito** — apuração, recorte, linha geral, causa de
  obsolescência, o código `reserve_only_convocation_external` e a recusa `sem_deficit`. São o
  vocabulário que a equipe vê na tela e que as specs `016`, `019` e `050` definem; nenhum nomeia
  tecnologia.
- **Os casos-limite que mudam comportamento viraram requisito** (`FR-2452`, `FR-2457`, `FR-2462`,
  `FR-2463`, `FR-2474`): a seção Edge Cases não entra na matriz de rastreabilidade.
- **Esta spec revisa a `FR-889` da `050`** na medida da `FR-2455`. A rastreabilidade da `050` precisa
  registrar a revisão quando o plano for escrito.
- **A `096` toca a mesma validação** (`reserve_only_convocation_external`). O plano parte do que ela
  tiver mergeado.
- O guardião de citações (`tests/test_citacoes_de_requisito.py`) e os demais testes que varrem
  `specs/` passaram depois da linha nova na tabela de incrementos do README.
