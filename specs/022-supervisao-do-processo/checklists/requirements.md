# Specification Quality Checklist: Supervisão do Processo

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-09
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

## Verificação própria desta feature

Além do checklist padrão, três conferências que esta spec precisa passar por causa do que ela é.

- [x] **Nenhum requisito fora do inventário.** Cada `FR` e cada `UX` remete a uma linha de
      `doc/inventario-supervisao-do-processo.md`. O inventário é a fonte; a spec não acrescentou
      capacidade que ele não tenha levantado.
- [x] **Nenhum requisito duplica tela dona.** Os vereditos **JÁ MOSTRA** do inventário não viraram
      requisito. Os que viraram são **TRANSVERSAL** (`FR-028`, `FR-029`) ou **AUSENTE**
      (`FR-010` a `FR-022`, `FR-026`, `FR-027`, `FR-030`), e o motivo está escrito.
- [x] **Nenhum estado inventado.** Conferido contra o código: `EtapaAvaliacao` sem ciclo de vida,
      `Inscricao` com dois estados e sem instante de última edição, `Cronograma` por Edital,
      vínculo Etapa–Evento anulável. Nenhum requisito pressupõe estado que o domínio não tem.
- [x] **Catálogo de sinais fechado e verificável.** Os cinco usam prefixo `UX-`, reconhecido pela
      varredura de citações. `tests/test_citacoes_de_requisito.py` passa com a spec no lugar.

## Notes

**Sobre "no implementation details".** A spec fixa uma restrição de desenho — não persistir estado
próprio (`D-007`, `SC-014`) — e cita nomes de entidade do domínio. É deliberado e segue o que nove
das specs anteriores já fazem: neste projeto a fronteira entre features **é** requisito de produto,
porque é ela que impede o painel de virar segunda fonte de verdade. A restrição é verificável sem
conhecer a implementação: basta conferir se a entrega acrescentou estrutura persistente.

**Sobre `SC-014`.** É o critério menos "agnóstico" da lista, e foi mantido de propósito: ele é o
teste empírico de `D-007`. Uma supervisão que precisa persistir andamento está, quase por definição,
inventando estado — e é melhor descobrir isso por um critério de sucesso do que por uma migration
que já foi escrita.

**Pendente de governança, e fora desta feature.** Dois achados do inventário aguardam decisão do
usuário e estão registrados na seção *Achados registrados* da spec: a rota de recursos inalcançável
por qualquer tela, e o conflito de vocabulário "em preenchimento" × "rascunho".
