# Specification Quality Checklist: Documentos e conferência na convocação

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-03
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

- **Detalhe de implementação na spec, de propósito.** A spec cita caminhos de código
  (`editais/models/documentos.py`, `comissoes/domain/autorizacao.py`) na matriz de permissões, nas
  decisões e na tabela de conflitos. Segue o padrão do repositório (`113`, `114`): a matriz precisa
  ser lida contra as autorizações reais, como pediu o usuário. Os requisitos (FR-) em si falam de
  comportamento.
- **Nenhum marcador [NEEDS CLARIFICATION].** As questões em aberto estão em *Pendências do usuário*,
  cada uma com o comportamento proposto até a decisão, pela convenção do projeto (governança é do
  usuário; achado vira registro).
- **SC-1089 e SC-1090 citam navegador e tabelas.** São verificações exigidas pelo pedido (estratégia
  de testes com navegador) e pela Constituição, I (append-only em duas camadas). Mantidos como estão.
- **Casos-limite** apontam, cada um, o requisito que os rege, para entrarem na rastreabilidade.
- **Revalidado em 03/11/2026, depois da revisão do PR #368.** Entraram a US8, as FR-3619 a FR-3622, as
  SC-1092 e SC-1093 e as decisões D-011, D-013 e D-019 reescritas ou novas. Os itens continuam
  marcados.
- **Revalidado de novo em 03/11/2026, na segunda rodada.** A D-019 e a FR-3622 passaram à regra única de
  prazo, aplicada à `029`. Nenhuma aprovação pendente para o merge.
