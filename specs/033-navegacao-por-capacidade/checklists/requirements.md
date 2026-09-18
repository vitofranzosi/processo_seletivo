# Specification Quality Checklist: Navegação por capacidade

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

**Nenhum marcador de clarificação, e a ausência é achado.** Ao contrário da `032`, aqui não havia
decisão de governança a tomar: a doutrina certa **já está escrita no repositório**, por extenso, na
porta da divulgação — *"sem a capacidade é 403, e não 404 … o 404 fica para o que o ator não
alcança"*. A feature aplica o que o produto decidiu e não cumpriu. Onde não há escolha aberta, não se
fabrica pergunta.

**O escopo foi medido, não estimado.** A interface administrativa tem 76 pontos que respondem "não
encontrado", e prometer varrer os 76 seria escopo que ninguém sustenta. A superfície real são as
**quatro portas de autorização nomeadas**, e a que erra a gramática governa **23 telas** — o que
torna `SC-165` verificável. O plano deve confirmar caso a caso que os demais são objeto inexistente,
e registrar o que encontrar; a spec já assume isso por escrito.

**A garantia mais importante é `SC-168`**, e ela existe porque a feature toca superfície de
segurança: o conjunto de pares (ator, tela) que abre tem de ser **idêntico** antes e depois. Sem ela,
"melhorar a navegação" é indistinguível de "afrouxar autorização". `FR-482` e `FR-483` são as duas
metades da mesma promessa — a verificação continua no servidor, e retirar um link nunca substitui a
recusa.

**Uma tensão declarada, e não escondida:** trocar 404 por recusa explicada **revela** que o objeto
existe. Isso é aceitável precisamente porque `FR-480` mantém o "não encontrado" para outro escopo
institucional — quem recebe a recusa explicada já está dentro do escopo, e já sabe que o Edital
existe por outras telas. Se na implementação aparecer um caso em que a existência não deveria ser
revelada nem dentro do escopo, ele é achado para registrar, não para resolver em silêncio.

**Faixa de identificadores medida em todas as worktrees, em 18/09/2026:** teto `FR-472 / SC-163 /
UX-061`, ocupado pela `032`. Esta spec abre em **FR-473** e **SC-164**, e não define `UX-`.

**Citações externas conferidas contra o código, não assumidas:** `_edital_para_publicar` e
`_edital_para_classificar` foram lidas nesta sessão, e é a contradição entre os dois docstrings que
dá à feature a sua espinha. `RecusaDoDominioMiddleware` e `interface/recusa.html` também — é por
existirem que `FR-478` não precisa construir mecanismo nenhum.
