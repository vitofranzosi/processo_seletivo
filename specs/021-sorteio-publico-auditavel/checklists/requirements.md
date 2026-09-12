# Specification Quality Checklist: Sorteio público auditável

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-08
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

- **Sobre "no implementation details".** As §1 e §2 citam modelos, arquivos e linhas do repositório
  de propósito, e é a convenção que a `020` estabeleceu: elas registram o que já está fechado e o
  custo de cada decisão, e são endereçadas a quem vai planejar. As seções obrigatórias — User
  Scenarios, Requirements, Success Criteria — descrevem comportamento observável e não citam
  tecnologia. FR-021 diz "função de resumo criptográfico" e não o algoritmo: qual função e qual
  versão é conteúdo normativo que o Edital publica, e o `/plan` a fixa.
- **Nenhum marcador de clarificação.** As oito decisões que o prompt de origem deixou abertas foram
  fechadas antes desta spec — seis por revisão de código, a 6ª pela leitura dos quatro Editais de
  sorteio, e a 8ª por decisão de escopo do usuário. (A numeração aqui é a das oito perguntas do
  prompt de origem, e não a das decisões `D-0xx` da spec.) Elas viraram, em §2, as decisões D-001 a
  D-012 — a que se somaram D-013 a D-016, tomadas depois do `tasks`.
- **A checagem que esta lista não faz.** Contradição entre requisitos não é detectada por checklist
  — está registrado no projeto que 16/16 convive com FRs que se contradizem. A varredura de
  consistência é do `$speckit-analyze`, depois de `plan` e `tasks`.
- **E foi exatamente o que aconteceu, desta vez também.** Esta lista fechou 16/16 sobre uma spec em
  que a FR-029 exigia num comando o que o desenho fazia em dois; em que a FR-014 chamava de conteúdo
  normativo uma tabela sem versão, signatário nem endereço; e em que a FR-005 proibia no canal
  público o identificador que o resumo da relação cobria. Nenhuma das três é falha de qualidade de
  redação — as três são coerência **entre** artefatos, e só apareceram na análise cruzada, depois do
  `tasks`. A lista não errou; ela mede outra coisa, e isto fica escrito para a próxima leitura não
  confundir 16/16 com prontidão.
- **Fronteira sob pressão.** O item que mais tentará vazar durante o planejamento é a interação
  entre listas do 57/28 (cotista sorteado nas duas fica na de ampla concorrência). Está no Out of
  Scope e em FR-064, e a US4 tem cenário negativo explícito para ele.
