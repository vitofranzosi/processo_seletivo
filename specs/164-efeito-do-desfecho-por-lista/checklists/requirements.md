# Specification Quality Checklist: O efeito do desfecho da Etapa por lista

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-14
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

## Casos-limite como requisitos

Os casos-limite não entram na matriz de FR- e SC-, e nenhuma ferramenta os cobra. Por isso cada um
foi conferido contra o requisito que o resolve:

| Caso-limite | Requisito |
|---|---|
| Não comparecimento | FR-7004, FR-7009 (Q-1) |
| Efeito por motivo | FR-7003; *Achados* |
| Eliminado depois em outra Etapa | FR-7011 |
| Retirada antes da última Etapa do marco, ou nela | FR-7012 |
| Retirada depois da última Etapa do marco | FR-7012; *Achados* |
| Faixa do corte já emitida | FR-7013, FR-7015 |
| Habilitada na Etapa governada pela faixa da ampla | FR-7014 |
| Concorrência concomitante e o 8.9 | FR-7014 |
| Já convocado pela reserva | FR-7016 |
| Recurso que devolve a reserva | FR-7019 |
| Modalidade declarada como ampla, inscrição sem Modalidade | regra de alcance da `163` |
| Etapa restrita a mais de um código | FR-7010 |
| Outra lista reservada | FR-7010, D-006 |
| Retificação que amplia o alcance | FR-7021 |
| Retificação que torna a Etapa não eliminatória | FR-7020 |
| Etapa sem inscrição alcançada | regra da `163` |
| Ato histórico | FR-7008 |
| Prévia da classificação | FR-7026 |
| Painéis e relatórios | FR-7025 |
| Etapa que nenhum marco enumera | FR-7024; risco registrado |

## Notes

- **Uma pergunta ao usuário fica aberta, de propósito: a Q-1**, sobre o efeito do não comparecimento
  (a P-6 do estudo). Ela não é marcador `[NEEDS CLARIFICATION]`. A FR-7004 está escrita com a
  recomendação e diz que depende da Q-1. Responder de outro modo muda só a FR-7004, a UX-741 e a
  D-007.
- **"Sem detalhes de implementação"** foi lido como neste repositório: a spec nomeia conceitos do
  domínio (Resultado da Etapa, consequência, faixa do corte, versão canônica, contrato de
  mutabilidade), e não tabelas, módulos nem funções. O mapa do código que sustentou as premissas
  (`resultados/domain/regra.py`, `resultados/application/prontidao.py`,
  `classificacao/domain/universo_classificavel.py`, `ocupacao/application/selectors.py`,
  `portal/situacao.py`) fica para o plano.
- **A `163` não está na `main`** (PR #542). A spec a cita só pelo assunto, para o guardião de citações
  não acusar identificador inexistente. Se a `163` mudar no merge, a seção *Assumptions* diz o que
  rever.
- Items marked incomplete require spec updates before `$speckit-clarify` or `$speckit-plan`.
