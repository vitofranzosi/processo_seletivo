# Specification Quality Checklist: A correção da convocação pela gestão

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-04
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

Validado em 04/11/2026, numa iteração.

- **Detalhe de implementação.** A spec cita o comando de convocar, a trava e a idempotência porque
  são as garantias que ela preserva, e não como desenho: onde mora a conferência da FR-3843 fica com
  o plano (D-003). Os códigos 403 e 404 são o contrato de recusa que o projeto já fixa (FR-478 da
  `033`), e não escolha desta spec. O caminho do teste de serviço, em *Assumptions*, é evidência de
  que o domínio já reabre, e não requisito.
- **Critérios mensuráveis.** SC-1143, SC-1144, SC-1145 e SC-1149 se medem por contagem de registros;
  SC-1147 por número de consultas com 1 e com 20 cartões; SC-1141, SC-1142, SC-1146 e SC-1148 por
  verificação no navegador.
- **Casos-limite são requisitos.** Os quinze da seção *Edge Cases* não têm identificador, e por isso
  nenhuma ferramenta os cobra: `rastreabilidade.md` tem uma linha para cada um.
- **O que este checklist não detecta.** Ele não acusa contradição entre requisitos. Conferido à mão:
  a FR-3838 (sem ação na chamada sem vencimento) e a FR-3841 (vencimento obrigatório) dizem o mesmo
  pela D-004; a FR-3839 (sem formulário no recorte impedido) e a FR-3850 (recusa no cartão) cobrem
  casos disjuntos — o impedimento que a leitura conhece e o que só a confirmação descobre.
- **Revisão de `4b2bd844` (04/11/2026).** Revalidado depois dos ajustes da FR-3844, da FR-3848, da
  SC-1144 e da FR-3854 e das ampliações (FR-3857, D-010; complemento da D-009): todos os itens
  continuam marcados. A contradição que a revisão apontou — a prévia dizia "prazo estendido" e a
  spec admitia antecipar — é do tipo que este checklist não pega.
- **Para a revisão do usuário.** D-002 a D-009 são propostas desta spec, mantidas na revisão. As
  que mais mudam a implementação são a D-003 (a conferência nova sob a trava), a D-004 (chamada sem vencimento fora) e
  a D-009 (a recusa preserva o que foi digitado).
