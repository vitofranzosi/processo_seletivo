# Specification Quality Checklist: Ordem por recorte em marco computado

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

**Revisto em 18/09/2026, depois de quatro passadas de `analyze`.** A primeira redação destas notas
descrevia a spec do dia em que ela nasceu, e três levas de correção a deixaram para trás — ela ainda
listava como "em aberto" três decisões que já eram requisito. Checklist que descreve uma spec que não
existe mais é pior do que checklist nenhum, porque alguém o lê para decidir se pode começar.

### As três cessões de "sem detalhe de implementação", e por que cada uma

1. **A seção *Por que esta feature existe* cita arquivos e funções por nome.** Não é desenho da
   solução: é a **medição do estado**, e está ali porque a `033` produziu três medições erradas
   seguidas por ter descrito a superfície de memória.
2. **A `FR-491` é requisito sobre o código**, e é o caso em que isso é legítimo: ela exige uma
   derivação única do conjunto de recortes. A razão é observável pelo usuário — ordem emitida para
   recorte que a ocupação não consome é ato publicado que não leva a lugar nenhum —, e o critério que
   a prende, a `SC-172`, compara duas listas sem saber como elas são produzidas.
3. **A `FR-502` cita mecânica de template** — *"variável ausente é tratada como falsa"*. Esta é a
   cessão mais funda das três, e foi deliberada: sem ela, a ordem *tela primeiro, campo depois* fica
   sendo preferência de quem escreveu a tarefa, e tarefa se reordena por conveniência. Com ela, é
   obrigação. O defeito que ela impede não deixa rastro — a ação de apurar some, a frase errada
   aparece para todos, e a suíte fica verde.

### As decisões que esta spec tomou, em vez de adiar

| | Onde |
|---|---|
| O autodeclarado é ordenado **nas duas** listas — perguntado a quem governa o backlog | `D-001` |
| A regra nova vale **adiante**; não há migração de acervo | `D-002` |
| A coerência com a `032` passa pelo ponto único que ela criou | `D-003` |
| Recorte sem autodeclarado tem **ordem vazia**, emitível e nunca automática | `FR-492a` |
| Retificação que acrescenta Modalidade **não obsoleta** a ordem da ampla | `FR-494a` |
| O aviso da `032` é **aposentado**, e não estreitado | `FR-501` |
| Predicado que deixa de variar é **removido**, não deixado dizendo sempre sim | `FR-501a` |

**Nenhuma delas ficou para dentro da implementação**, que era como as três primeiras estavam na
redação anterior deste arquivo.

### A única coisa que continua aberta, e é de governança

**Ampliar a `FR-491` para alcançar o sorteio, ou manter a divergência registrada?** É a `T004`, é
parada de escopo, e a `FR-491`/`FR-491a` está marcada como **proposta provisória** até ela fechar.
A medição encontrou **três** tratamentos da Modalidade declarada como ampla — não dois, como a
primeira redação desta nota dizia.

### Medições a reconferir na implementação

A tabela de *Por que esta feature existe* inteira, e em especial: a ausência de migration (`FR-505`),
a divergência entre as três derivações, e **a contagem dos casos de teste alterados** — que nasceu
errada, dizia "11 em 4 arquivos" quando a própria tabela somava **8 em 3**, e atravessou três
passadas de `analyze` antes de alguém somar.
