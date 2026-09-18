# Specification Quality Checklist: Executabilidade antes de publicar

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

**Houve um marcador, e ele era de governança — resolvido pelo usuário em 18/09/2026.** `FR-470`, o
tratamento da reserva de vagas em marco que produz ordem única. As duas leituras razoáveis tinham
consequências opostas e nenhuma era padrão seguro: impedir tornaria três Editais da amostra real
(57/2026, 28/2026, 173/2025) impublicáveis até a emissão por lista existir; avisar preserva a
publicação e deixa o achado S4 alcançável. **Escolhido: aviso não impeditivo**, e o porquê está
escrito na própria história P3, junto com a consequência que ele não resolve.

**Esta spec é a única das quatro em que o achado não fecha.** Vale dizê-lo alto: `ACH-49`, `ACH-50` e
`ACH-46` saem fechados; `ACH-47` sai **nomeado**, não resolvido. A resolução depende da feature de
emissão por lista, que está em *Out of Scope*.

**Faixa de identificadores conferida em todas as worktrees**, em 18/09/2026, e não só na árvore
local — a medição local sozinha já produziu colisão inteira na `030`:

```
FR teto: FR-456 · SC teto: SC-156 · UX teto: UX-061
```

O teto veio da `031-exportacao-de-matriculas`, que vive numa worktree paralela, sem branch remota e
invisível para `git branch -r`. Esta spec abre em **FR-457** e **SC-157**, e não define `UX-`.

**Duas citações externas foram conferidas contra as specs que as definem**, e não assumidas:
`FR-224` da `014` (a regra de corte pode declarar que não governa Etapa alguma — é o que separa o
aviso legítimo do falso positivo, e o caso do Edital 69/2026) e `FR-429`/`FR-432` da `030` (método
comum do Edital, e marco de sorteio sem Etapa).

**O Princípio VI foi tratado como tensão, e não como formalidade.** Uma feature de validação corre o
risco de ser exatamente o que o princípio recusa — rigor sem jornada. Por isso as três histórias
foram escritas como capacidade observável, e a P2 entrega capacidade nova a quem está fora da
instituição. A seção *Conformidade com a Constituição* declara isso por escrito.

**`FR-469` é conferência, não construção.** O documento publicado é gerado no ato e guardado, então
"nada muda no acervo" já é verdade pelo desenho existente; o requisito existe para que a feature
prove que não o contrariou.
