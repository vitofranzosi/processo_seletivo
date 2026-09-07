# Specification Quality Checklist: Anexos do Edital

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-07
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

- **Sobre "no implementation details"**: a spec nomeia entidades do domínio já existentes —
  `DocumentoExigido`, `DocumentoSubmetido`, `DocumentoPublicado`, `SecaoEdital`, `EtapaAvaliacao`,
  `AlteracaoNormativa` — e cita specs anteriores por número. É a convenção da casa (a `018` faz o
  mesmo) e é o que o princípio I da Constituição exige: linguagem ubíqua única entre especificação,
  código e testes. Nenhuma tecnologia, framework, biblioteca, rota ou esquema de banco entra; a
  única expressão de framework da primeira redação (`OneToOneField`, na D-001) foi substituída pelo
  fato de domínio que ela expressava.
- **Varredura própria de contradições**, feita além do checklist porque o checklist não a detecta:
  - operações da Retificação (D-008/FR-031) × rótulo (D-006): "alterar rótulo" é operação porque o
    rótulo é campo versionado. Sem contradição — foi exatamente esta a incoerência corrigida no
    prompt antes do `/specify`;
  - FR-039 × FR-043: a redundância "sem autenticação" foi removida do FR-039; o regime de acesso
    ficou num requisito só;
  - FR-045 (modelo vigente no rascunho) × FR-048 (resolução pela versão aceita): perguntas
    distintas — o que se oferece agora, e o que estava valendo então;
  - FR-013 (limite é da aplicação) × Out of Scope (limite declarado pelo Edital): coerentes, o
    segundo registra a pressão sem incorporá-la;
  - FR-051 (nenhuma máquina de avaliação) × US4 (banca abre o modelo): mostrar o modelo não é
    conferir conformidade; FR-047 e FR-049 seguram a fronteira.
- **Decisão de escopo registrada, não tomada aqui**: o teste de aceitação cobre os
  anexos-formulário do 173/2025, e não os nove. Está em Assumptions, com o preço do caminho
  alternativo. Reverter isso é decisão do produto, e muda SC-005.
