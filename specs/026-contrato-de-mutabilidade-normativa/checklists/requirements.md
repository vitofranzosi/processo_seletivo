# Specification Quality Checklist: Contrato de mutabilidade normativa

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-13
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

Três observações da validação, resolvidas no texto:

1. **"Implementation details" e o nome de arquivo.** A spec cita `editais/domain/validation.py`,
   `interface/retificacao.py` e `tests/contract/test_retificacoes_api.py`. Não é vazamento de
   implementação: é a convenção deste repositório, que cita a fonte do achado para que a spec
   seguinte possa conferi-lo — a `021`, a `025` e a `014` fazem o mesmo. O que a spec **não** faz é
   prescrever estrutura de código: onde o contrato mora é decisão do plano.

2. **Princípio VI da Constituição.** A primeira redação entregava só a matriz e o guardião, como a
   decisão registrada descrevia. Isso é trabalho exclusivamente técnico, que a Constituição admite
   mas que **não conclui uma spec**: *"Uma capacidade que o domínio sustenta mas que nenhuma
   interface alcança NÃO DEVE ser considerada entregue"*. Os quatro canários deixaram de ser insumo
   de desenho e passaram a ser as jornadas — e o gate de conclusão exige que um servidor pratique
   as quatro correções pelo canal dele.

3. **Numeração medida na base, e não herdada.** FR a partir de FR-297 (teto global era 296), SC a
   partir de SC-095 (teto 094), D reiniciando em D-001 — que é o que a `024` e a `025` fazem.

**Pendente para `$speckit-clarify` ou para o plano**: nenhuma pergunta bloqueante. A decisão mais
aberta — se alguma coleção precisa de uma quinta natureza — está declarada como achado esperado da
feature (Assumptions), e não como incerteza de escopo.
