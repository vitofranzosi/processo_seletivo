# Specification Quality Checklist: Ocupação de Vagas entre Listas de Concorrência

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-12
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

**Nota sobre nomes técnicos.** A spec cita `vacancyTable`, `percentage`, `distribution`,
`callRules` e `generalCompetitionModalityId`. **Não são detalhe de implementação**: são nomes de
campo do **conteúdo normativo publicado**, e a Constituição trata o conteúdo publicado como
domínio. A `025` e a `014` citam os mesmos nomes nas specs delas, pela mesma razão. O que a spec
evita é dizer *como* se calcula, onde se grava e com qual tecnologia — e disso não há nada.

## Requirement Completeness

- [x] **No [NEEDS CLARIFICATION] markers remain** — os três foram respondidos em 12/09/2026
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

**As três foram respondidas pelo usuário em 12/09/2026**, e estão registradas como `D-006`,
`D-007` e `D-008`. O que cada resposta mudou na spec:

| Decisão | Resposta | O que mudou |
|---|---|---|
| `D-006` cascata do 14/2026 | é **alvo derivado da `014`** | o 14/2026 saiu da amostra desta feature; §1.1 passou de quatro Editais para três, §1.2 de quatro mecanismos para três, e a §8 deixou de prometê-lo |
| `D-007` gatilho da reversão | **duas espécies declaradas** | `FR-249`, `FR-250` e `FR-251` — a espécie é conteúdo publicado, e a ausência recusa a publicação em vez de virar padrão |
| `D-008` ato ou projeção | **ato append-only por recorte** | `FR-261` a `FR-263` — sucessão e três causas de obsolescência; a §8 passou a pôr entidade e privilégio **antes** da primeira tela |

**A `D-006` alcançou um artefato entregue, e a emenda foi autorizada.** O *Out of Scope* da `014`
mandava a cascata para a `016` e ficou contradito por decisão mais nova. Aquela feature está
mesclada, então corrigi-la é ato de governança: o usuário autorizou em 12/09/2026, e a emenda foi
feita no mesmo dia — registrando a redação anterior, no estilo que aquela spec já usa, e dizendo
que a capacidade é da linha dela e **não está construída**.

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Verificação executada

| O que | Resultado |
|---|---|
| `tests/test_citacoes_de_requisito.py` | **5 passando** — depois de três reparos, abaixo |
| faixa de identificadores | `FR-239`–`FR-263` mais `FR-239a` (26), `SC-078`–`SC-084`, `UX-031`–`UX-034`; teto anterior medido em `daded41` |
| margem de 100 colunas | nenhuma linha de prosa acima |

**Os dois primeiros a varredura forçou, e o segundo era de escrita.** A primeira execução reprovou
com `D-001, D-002, D-003, D-004, D-005, D-014` ausentes. Duas causas distintas:

1. os títulos das decisões locais estavam com acento grave (`#### \`D-001\` — …`), e
   `DECISAO_DEFINIDA` exige `^#{2,4} (D-\d+)` — eram **citadas e não definidas**;
2. a spec citava `D-002`, `D-003`, `D-004` e `D-014` querendo dizer as da `014`, **enquanto
   definia** `D-002` a `D-005` com outros sentidos. A varredura resolve `D-` **dentro** de cada
   feature, então `D-014` não existia aqui — e, pior que o teste, um `D-002` que significa duas
   coisas no mesmo arquivo engana quem lê.

A correção foi trocar toda citação de decisão **alheia** por prosa que nomeia a feature e o assunto
("a decisão de fronteira da `014`"), reservando o token `D-NNN` para as decisões desta feature.

**O terceiro reparo foi meu, ao incorporar as decisões.** Os requisitos novos entraram como
`FR-249a` e `FR-249b`, e sufixo neste repositório é para requisito acrescentado **depois** a uma
spec entregue — numa spec nova é só marca de edição. A renumeração para a faixa contígua
`FR-239`–`FR-263` foi feita por posição no documento, com as citações internas reapontadas e
conferidas uma a uma.

## Notes

- A spec está **pronta para `$speckit-plan`**: as três questões que o precediam foram respondidas,
  e a `D-008` já fixou que há entidade nova. `$speckit-clarify` não é necessário.
- Achado citado e não resolvido aqui:
[`achado-igualdade-da-soma-sem-a-ampla-declarada.md`](../../../doc/achado-igualdade-da-soma-sem-a-ampla-declarada.md).
  A feature lê a **linha** do quadro e não o total do Perfil, e por isso não herda a divergência —
  está registrado em Edge Cases.
