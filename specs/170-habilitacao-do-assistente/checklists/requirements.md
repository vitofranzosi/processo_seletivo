# Specification Quality Checklist: A habilitação do assistente do Edital pela interface

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

A seção *Edge Cases* não entra na matriz de `FR-` e `SC-`, e nenhuma ferramenta a cobra. Por isso
cada caso aponta o requisito que o governa. A conferência foi feita caso a caso:

| Caso-limite | Requisito |
|---|---|
| Habilitação sem capacidade, por envio montado à mão | FR-7501, FR-7512 |
| Capacidade retirada com o piloto habilitado, e a volta dela | FR-7504 |
| Capacidade incompleta não derruba a inicialização | FR-7503 |
| Serviço externo em produção com o piloto desligado | FR-7502, SC-2455 |
| Dois administradores ao mesmo tempo | FR-7532 |
| Ato que não muda nada | FR-7531 |
| Retificação depois do registro dos requisitos do Edital | FR-7519, SC-2454 |
| Edital habilitado que perde a página pública | FR-7521 |
| Retirada de requisito institucional com Editais abertos | FR-7518 |
| Pergunta em curso no instante da desabilitação | FR-7525 |
| Chave de demonstração e registro ao mesmo tempo | FR-7505, FR-7506 |
| Registro do relatório final não dispara a exclusão | FR-7534, SC-2457 |
| Administrador revogado ou suspenso | FR-7509 |
| Unidade do Edital desativada | FR-7520 |

## Notes

- Os nomes das variáveis `ASSISTENTE_*`, da permissão `assistente:habilitar` e dos pontos do código
  que leem as chaves aparecem na spec de propósito. O pedido mandou decidir o destino de cada
  variável e de cada recusa do `production.py`, e conferir no código cada ponto que lê as chaves. São
  o objeto da revisão, e não escolhas de implementação. As tabelas do registro e a forma da
  serialização ficam para o plano.
- Nenhum marcador de esclarecimento. As quatro decisões do usuário estão como Q-1 a Q-4, cada uma com
  recomendação, e a spec adota a recomendação até a resposta, como fizeram a `164` e a `166`. O
  `/speckit-clarify` pode revisitá-las.
- O SC-2453 mede um resultado que hoje é uma recusa. É deliberado: a spec não abre o assistente ao
  público, e o critério prova que a interface não dispensa requisito.
