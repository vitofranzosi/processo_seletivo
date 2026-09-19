# Specification Quality Checklist: Instrução do recurso

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

## Notes

### A cessão de "sem detalhe de implementação", e por que só uma

A seção *Por que esta feature existe* cita campos e telas por nome. É a **medição do estado**, e está
ali porque nas três features anteriores foi ela que salvou a spec: a `035` teve a premissa corrigida
pelo Phase 0, e a `034` carregou por três revisões um número que nunca fechou com a própria tabela.

**As `FR-` não citam arquivo nenhum.** O mais perto que chegam é a `FR-523`, que diz *"o registro
histórico da conclusão"* — e isso é conceito do domínio, não estrutura de dados: existe porque
reabrir uma avaliação não pode destruir o que ela havia concluído.

### As três decisões, e o que cada uma custa

| | Onde | Custo dito por escrito |
|---|---|---|
| O parecer acompanha o **prazo**, não a inscrição | `D-001` | encerrado o prazo, o titular perde acesso à razão da própria eliminação. A `FR-524` impede que isso vire defeito silencioso |
| O parecer é o da **avaliação que fundamenta o resultado** | `D-002` | nenhum — é medição, não escolha |
| A prova chega por **referência**, e o alcance **morre com o ato** | `D-003` | uma consulta a mais em vez de uma cópia; e o julgador perde o acesso depois de decidir, o que é o ponto |

**Nenhuma ficou para dentro da implementação.**

### O que esta spec precisa que a revisão não deixe passar

**1. Esta feature concede acesso a dado pessoal.** É a primeira desta série que o faz. Toda revisão
deve perguntar, de cada requisito novo: *quem passa a ver o quê, por quanto tempo, e quem registrou?*
As respostas estão em `FR-528`, `FR-529`, `FR-533` e `FR-534`, e os critérios que as prendem são
`SC-184` e `SC-185`.

**2. A tentação é ampliar o papel de julgar.** Seria uma linha, e resolveria o `ACH-43` na aparência.
É exatamente o que a `FR-105` da `018` proíbe — *"MUST NOT ampliar o acesso a documentos do
candidato"* —, e é por isso que a `FR-530` existe escrita como proibição, e não como silêncio.

**3. A tela do julgador hoje é um beco honesto.** Ela não oferece o que ele não alcança, e diz o que
falta. **Essa garantia é da `033`, e esta feature não pode desfazê-la** ao acrescentar destinos: é a
`FR-532`, e ela é fácil de violar sem perceber, porque a feature inteira existe para acrescentar o
que mostrar.

### Medições a reconferir no `plan`

A tabela de *Por que esta feature existe* inteira, e em especial: que o parecer é **obrigatório** no
caso auditado; que o resultado aponta para **uma** avaliação; que **não existe** conceito de anexo no
recurso hoje; e o alcance exato da `FR-105` da `018`, que é o requisito de outra feature sobre o qual
esta inteira se apoia.
