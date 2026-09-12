# Specification Quality Checklist: Convocação, Chamada e Suplência

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-12
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — os oito foram fechados pelo `$speckit-clarify` de
      12/09/2026, e as cinco questões da §3.0 viraram `D-006` a `D-010`, cada uma citando o texto da
      decisão do usuário.
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Verificação feita nesta sessão

- **Cláusulas lidas nos documentos originais**, não deduzidas: seis Editais (`77`, `58`, `59`, `69`,
  `28`, `158`) por `pdftotext -layout`, com cláusula e número na §1.1.
- **Citações**: `tests/test_citacoes_de_requisito.py` verde — nenhum `FR-`, `SC-`, `UX-` ou `D-`
  aponta para identificador inexistente. As decisões de outras features são citadas **por nome**, e
  não por número, porque `D-NNN` é por feature.
- **Faixa**: `FR-264`–`FR-296` (com as alíneas `269a`, `269b`, `278a`–`278d`, `286a`, `288a`,
  `288b`, `292a`–`292c`), `SC-085`–`SC-094`, `UX-035`–`UX-039`. Teto anterior medido em `c746adf`:
  `FR-263`, `SC-084`, `UX-034`.
- **Fronteira**: nenhum requisito desta spec conta vaga, ordena ou emite faixa; a `SC-092` exige a
  varredura que prova o simétrico da `UX-034` da `016`.

## Notes

**16 de 16.** As seis decisões do usuário (`D-006` a `D-011`) estão na spec com o texto dele, e
três delas alcançam feature já entregue — o que o plano tem de orçar explicitamente:

1. **`D-006` + `D-011`** — a `016` passa a contar **titulares iniciais** e ganha porta append-only
   de **exclusão e inclusão**, definida por ela para não inverter a seta de dependência. A exclusão
   sozinha era inócua: medido, o número só se movia na **28ª** desistência (§1.0 da spec).
2. **`D-008`** — a `018` ganha origem de sucessor que não é recurso: linha nova no conjunto de
   formas legítimas do Resultado, com migration de constraint e gatilho conferidos.
3. **`D-009`** — a `FR-084` da `010` tem de ser revisada por escrito antes de existir mensagem
   individual de convocação; a própria regra manda.

Nenhuma delas é implementável sem o `$speckit-plan`, e nenhuma decorre automaticamente desta spec.

**A `SC-093` é o teste de regressão desta correção**: uma desistência tem de mover o número em
exatamente um, e o aceite da suplente convocada tem de devolvê-lo. Qualquer contagem que sature
reprova ali.
