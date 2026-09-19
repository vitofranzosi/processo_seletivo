# Specification Quality Checklist: Sorteio executável

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-18
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

### As duas cessões de "sem detalhe de implementação", e por que cada uma

1. **A seção *Por que esta feature existe* cita módulos e campos por nome.** É a **medição do
   estado**, não o desenho da solução, e está ali porque a `033` produziu três medições erradas
   seguidas por descrever a superfície de memória, e a `034` carregou por três revisões um número que
   nunca fechou com a própria tabela. As `FR-` não citam arquivo nenhum.
2. **A `FR-516` é requisito sobre o código**: a conferência da publicação e a execução do sorteio têm
   de responder pela mesma regra. A razão é observável por quem usa — a Revisão aprovando o que o
   sorteio recusa —, e não depende de saber como a regra é escrita.

### As três decisões tomadas, em vez de adiadas

| | Onde |
|---|---|
| Método inexecutável **impede** a publicação — perguntado a quem governa o backlog | `D-001` |
| Vocabulário fechado vira **escolha**, e não texto validado | `D-002` |
| A derivação em prosa **fica como está** — contraria a leitura da auditoria, e a medição sustenta | `D-003` |

**Nenhuma ficou para dentro da implementação.**

### A correção que esta spec faz na auditoria, e que precisa sobreviver à revisão

A reauditoria citou **dois** campos como "texto livre que precisa ser dado computável". Só **um** é.
O outro — *como a ocorrência decorre da data programada* — é prosa por desenho: nenhum caminho de
execução o lê, e quem deriva é a regra de substituição, que já é vocabulário fechado.

Se alguém, no `plan` ou na implementação, "corrigir" esse campo, a feature terá removido do Edital a
frase que diz a norma em português. A `FR-510` existe para impedir isso, e é o requisito mais fácil
de perder de vista, porque ele manda **não fazer** uma coisa que a auditoria parecia pedir.

### Medições a reconferir no `plan`, e não a assumir

A tabela de *Por que esta feature existe* inteira, e em especial: que os três campos são mesmo texto
livre hoje; que o vocabulário de algoritmos tem um elemento e o de fontes dois; que a regra de
substituição exige referência terminada em número; e que **nenhum** caminho de execução lê a
derivação em prosa — esta última é a que sustenta a `FR-510`, e é a que mais custa se estiver errada.
