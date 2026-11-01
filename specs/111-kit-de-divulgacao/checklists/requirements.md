# Specification Quality Checklist: Kit de Divulgação do Edital

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-31
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

- **Detalhe técnico na spec, de propósito.** A tabela "O que existe e é reaproveitado" e os nomes de
  função dos requisitos de reaproveitamento (FR-3407, a lista `PROIBIDAS` na FR-3414) seguem o padrão
  das specs do repositório (`099`, `110`). A regra do pedido é "não criar segunda interpretação", e
  ela só se verifica nomeando a primeira. Os critérios de sucesso ficam livres de tecnologia.
- **As pendências P-1 a P-9 não são marcadores de esclarecimento.** Cada uma tem comportamento
  padrão declarado. Nenhuma impede o início; a P-3 e a P-4 impedem a liberação da peça.
- **Varredura de contradições** feita à mão, porque este checklist não a faz:
  - o modo "sem material" (FR-3410) contra a ação "indisponível com motivo" (FR-3401);
  - "copiar não registra" (FR-3435) contra a desatualização (FR-3439). Coerente: só a exportação é
    referência, e a P-5 está aberta;
  - "manchete só na peça" (FR-3427) contra "peça ⊂ ficha" (FR-3423). Coerente: a manchete vem de
    lista fechada derivada da ficha;
  - "nunca truncado" (FR-3426) contra "recusa" (FR-3429);
  - total de vagas (FR-3425) contra "oferta por Perfil" (FR-1607 da `072`): resolvido pela exceção declarada;
  - determinismo (FR-3438) contra os instantes do manifesto (FR-3437): resolvido pelos dois níveis.
- **A [revisão crítica independente](../revisao-critica.md)** encontrou três contradições que esta
  varredura não pegou: o determinismo, o total e a manchete "controlada" com texto livre. Todas foram
  corrigidas.
