# Specification Quality Checklist: Alcance declarável

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

## O que esta passada conferiu, e com que resultado

**Vocabulário de domínio não é detalhe de implementação.** "Quadro de Vagas", "Marco Classificatório",
"conteúdo publicado" e "recorte sem Modalidade" são termos normativos deste domínio, escritos na
Constituição e nos Editais reais — não são tecnologia. A única frase que descia ao mecanismo foi
reescrita: onde dizia "degrau de elevação" passou a dizer "versão nova do conteúdo publicado".

**As três decisões estão declaradas como título**, e não como item de lista. O guardião de citações
cobra `D-NNN` em `^#{2,4}` dentro de `spec.md` ou `research.md`; a primeira redação as escrevia em
negrito numa lista, e teria quebrado o CI sem quebrar nada em execução.

**As citações foram varridas antes de existir PR.** `FR-461` (da `032`), `FR-567`, `SC-200` e
`UX-066` (da `038`) estão definidas. `D-G1` a `D-G5`, `ACH-60`, `ACH-10/05`, `E-3` e `E-4` não casam
com nenhum dos padrões do guardião e são citações de governança, não de requisito.

**Teto proporcional respeitado sem truque**: 3 histórias, 13 requisitos, 5 critérios, 2 garantias de
interface, 3 decisões. Nenhum requisito existe para impedir a leitura errada de outro — os avisos
desse tipo estão nos casos-limite e nas decisões, que é onde nota de tarefa mora.

## Notas para o planejamento

- **A US2 é a que pode não caber**, e a spec já diz o que fazer se não couber. O Phase 0 decide por
  medição, não por gosto: quantos lugares decidem quem entra numa Etapa.
- **Duas medições desta passada encolhem a feature** e precisam ser reconfirmadas: a classificação já
  é por Perfil (o Marco mora no Perfil e soma os pesos das Etapas que **ele** enumera), e o código da
  Modalidade já é único por Perfil — o recorte compartilhado já se repete de fato, sem estatuto.
