# Specification Quality Checklist: A Retificação acrescenta o que o contrato já permite

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-26
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

- **Referências a código são evidência, e não desenho.** As tabelas *Por que esta feature existe*,
  *Inventário* e *Correlação com a auditoria* citam arquivo e linha, que é a convenção da casa desde a
  `046`: é o que torna o achado reproduzível. Os requisitos não prescrevem implementação.
- **Três decisões foram tomadas pelo usuário antes da escrita** (26/09): o corte nasce com guarda
  (`D-002`), a janela nasce só concedendo (`D-003`) e o critério de desempate entra (`D-004`).
- **A `D-001` foi decidida pelo usuário em 26/09**: qualquer Modalidade, inclusive cota.
- **Varredura de contradições** feita à mão, cruzando cada FR com os que falam do mesmo objeto noutro
  bloco. Um par foi corrigido: a `FR-781` prometia que corte e apuração de outro recorte nunca ficariam
  obsoletos, e alterar o quadro no mesmo ato os torna obsoletos. A promessa passou a ser sobre o
  acréscimo da Modalidade, por si. Dois casos-limite prometiam comportamento da conferência sem FR, e
  foram reescritos como limites.
- `tests/test_citacoes_de_requisito.py`: 5 de 5 passando.
- **`/speckit-analyze` de 26/09**: nenhum crítico. Corrigidos, com a opção (a) escolhida pelo usuário:
  - I1: a spec prometia recusa *na conferência*, e as tarefas só a faziam na confirmação. As funções
    extraídas passam a correr ao conferir e de novo no ato, e a spec distingue as duas fases;
  - I2: o cenário da janela *"não admite"* pela tela não era executável. Ele passou a ser da API;
  - I3: o documento da Modalidade nova vai para a Retificação seguinte, e não para o mesmo ato;
  - C1 e C2: dois casos a mais na T031 e na T033;
  - S1: linha longa na FR-781.
- **Parecer de 26/09, depois do analyze**: a `D-001` decidida (qualquer Modalidade). A guarda genérica de
  objeto inteiro saiu, com os números 783 e 293 sem uso, e virou o achado A-6. O protótipo de medição
  também saiu. A página pública da seleção, a linha do quadro no PDF e o resumo *antes → depois*
  entraram nas tarefas.
