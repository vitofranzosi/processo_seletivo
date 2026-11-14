# Specification Quality Checklist: O alcance da Etapa por Modalidade

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

- **Nenhum marcador.** A decisão de produto (P-1) é do usuário, de 13/11. A única escolha que o pedido
  delegou — como o alcance se expressa num Edital multiperfil — é a `D-001` (por código, no molde do
  recorte transversal da `044`). As demais decisões (`D-002` a `D-010`) preservam o significado dos
  Editais de hoje e registram a alternativa descartada; estão abertas à revisão do usuário no PR.
- **Nomes de código na spec.** `HABILITADA`, `ELIMINADA` e os códigos de exemplo (`PPI`, `AC`, `PcD`)
  aparecem como vocabulário do domínio, como nas specs anteriores da família (`044`, `146`, `162`).
  Nenhum requisito prescreve a implementação.
- **Casos-limite com requisito.** Os que mudam comportamento têm `FR-` próprio: inscrição sem
  Modalidade (`FR-6968`), concomitância (`FR-6969`), Etapa sem alcançados (`FR-6977`), Retificação
  que amplia (`FR-6979`) e que estreita (`FR-6980`), código inexistente (`FR-6963`), universo do marco
  (`FR-6985`), publicação das inscrições (`FR-6987`).
- **Achado do mapeamento dos consumidores**, conferido no código em 13/11: a regra de habilitação da
  Etapa imediatamente anterior, o universo da ordem (lido na última Etapa enumerada), a Etapa de
  análise da publicação das inscrições e o reingresso pendente travariam a ampla diante de uma Etapa
  restrita. Os quatro viraram `FR-6972`, `FR-6985`, `FR-6987` e `FR-6986`.
- O `SC-2316` é humano e fica pendente.
