# Specification Quality Checklist: Painel de condução do Processo vivo

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-19
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

## O teto proporcional, conferido

| | Alvo | Real |
|---|---|---|
| Linhas de spec | ~400 | **249** |
| Histórias | ≤ 3 | **3** |
| Requisitos | ~15 | **12** |
| Passadas de `analyze` previstas | **1** | — |

**Nenhum requisito existe para impedir a leitura errada de outro.** Os avisos dessa espécie — *ler a
mensagem do `UX-005` em vez da condição*, *não fazer dois sinais dispararem pelo mesmo fato* — estão
em **casos de borda** e em **itálico dentro do requisito que já existia**, não como requisito próprio.

## O que a medição corrigiu antes de a spec ser escrita

| Afirmação de partida | O que a medição achou |
|---|---|
| "o `UX-005` cobre recursos pendentes" | cobre **comissão inteira impedida**; a mensagem engana, a condição não |
| "o `UX-003` cobre avaliação em aberto" | cobre **cobertura**; Etapa bem coberta com trabalho parado não sinaliza |
| "a lista de sinais é fechada" | é fechada por requisito que diz **cinco**, e o produto tem **seis** |
| "o painel mostra quem precisa agir" | **não é entregável** — o produto não liga identidade a papel, e o `UX-005` já registra isso |

## Notas

- As quatro medições acima **devem ser reconferidas pelo Phase 0**. Eu errei duas delas em cinco
  minutos lendo mensagem em vez de condição.
- A `037` está em CI e altera três superfícies que esta spec **deliberadamente não mediu**. A
  dependência está registrada no fim da spec.
