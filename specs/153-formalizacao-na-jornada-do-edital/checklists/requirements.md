# Specification Quality Checklist: A formalização na jornada guiada do Edital

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-11
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

- **Sem marcador de esclarecimento, por desenho.** A governança é do usuário: as sete perguntas
  ficam na seção "Perguntas para o usuário" (P-1 a P-7), cada uma com a recomendação que a spec adota
  provisoriamente e o efeito da alternativa. Nenhuma bloqueia o `/speckit-plan`. A P-1, o nome
  "Encaminhar" ou "Disponibilizar", reabre a decisão de terminologia da `117` se a resposta for
  "Encaminhar", e deveria ser respondida antes do plano.
- **Rotas e nomes de tela aparecem só nas Assumptions e no "Por que"**, como referência às evidências
  do estudo e às telas de destino que já existem. Não são decisão de implementação.
- **SC-1955** fala em "consultas" e "armazenamento": é o critério de custo da leitura do Centro,
  que o projeto mede por orçamento de consultas. Fica como está, porque é verificável sem conhecer a
  implementação.
- O `rastreabilidade.md` nasce no `/speckit-plan`. Ele precisa de uma linha para cada identificador
  em negrito da spec, de FR-6100 a FR-6130, de UX-560 a UX-563 e de SC-1950 a SC-1956.
