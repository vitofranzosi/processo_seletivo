# Specification Quality Checklist: Recursos e Superação de Resultados

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-06
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

**Sobre "no implementation details".** A spec cita nomes de agregados e de contratos existentes —
`ResultadoEtapa`, `AtoDeOrdenacao`, `PublicacaoResultado`, `Impedimento`, `exigir_titularidade` — e
isso é deliberado, no padrão que a 013, a 015 e a 017 já adotam neste repositório: são termos da
linguagem ubíqua exigida pelo Princípio I, e a §3 (Contratos herdados) existe justamente para
impedir que o planejamento construa infraestrutura paralela. Nenhuma escolha de linguagem,
framework, biblioteca, esquema de banco ou desenho de API foi feita aqui — a spec deliberadamente
não decide se o objeto atacado será representado por duas chaves opcionais ou por outra forma, que
é a pergunta que o plano responde.

**Cinco questões de governança foram levadas ao usuário e decididas**, em duas rodadas, e estão
registradas em Clarifications. As duas primeiras (unidade de contagem da janela; anexos na peça)
foram absorvidas em D-004 e D-011. As três da segunda rodada — janela após correção de definitiva;
fato que encerra a providência a jusante; vocabulário da quarta espécie — foram absorvidas em D-008,
D-009 e FR-089. Nenhum marcador de clarificação permanece.

**Rastreabilidade das sete decisões institucionais** (`doc/decisao-018-escopo-institucional-do-recurso.md`, §11):

| decisão institucional | onde a spec a consome |
|---|---|
| 1 — dois objetos de recurso | D-001, D-003, FR-001 a FR-003, FR-014 a FR-019 |
| 2 — só o titular | D-002, FR-004, FR-005 |
| 3 — janela declarada por marco, degradando para juízo humano | D-004, FR-020 a FR-030, FR-033, FR-034 |
| 4 — capacidade própria, impedimento que bloqueia | D-005, FR-037 a FR-043 |
| 5 — *non reformatio in pejus*, alcançando a reavaliação | D-006, FR-070 a FR-074 |
| 6 — progressão retroativa plena, com guarda e avisos | D-007, FR-075 a FR-080 |
| 7 — definitividade verificada e declarada, nome pela causa | D-008, FR-081 a FR-091 |

**Decisão C** (`doc/descoberta-018-decisao-c-superacao-de-resultado.md`, §1): consumida em §1.1 e
nos FR-051 a FR-064; a spec não reabre nenhuma das três escolhas.

**Um ponto de desenho que a spec acrescenta com evidência, e que merece atenção na análise de
consistência**: a quarta espécie de decisão — deferimento com providência a jusante (D-009). Ela não
está nomeada no documento institucional, e é derivada do mapa da §4 da descoberta: três das seis
linhas daquele mapa têm remédio fora do `ResultadoEtapa`. Sem essa espécie, um recurso procedente
contra a norma ou a forma da divulgação obrigaria o julgador a indeferir um recurso procedente ou a
fabricar sucessor de Resultado para um erro que não está lá. **O cumprimento dela é fato derivado
com vínculo causal**: o ato de ordenação publicado **cita** a decisão que a determinou (FR-089), e a
citação é proveniência do próprio ato, gravada por quem o emite. A spec recusa explicitamente ato de
cumprimento com autoridade própria, espécie estruturada de providência e ato de impossibilidade.

**A revisão do plano corrigiu a redação anterior desta regra**, que dava a pendência por cumprida
quando a publicação divulgasse "ato diferente" do reconhecido viciado: isso a quitaria **por
acidente** — um ato sucessor emitido por razão alheia encerraria a pendência sem que ninguém tivesse
corrigido o vício. A FR-089 e a D-009 passaram a exigir a citação.

**Três resíduos encontrados na varredura de contradições da segunda rodada, e corrigidos:**

1. **FR-055 × FR-068** — a primeira dizia que a consolidação cria apenas raízes, a segunda mandava a
   consolidação da reavaliação criar sucessor. A FR-055 passa a falar em consolidação **ordinária** e
   a nomear a exceção única; a FR-068 passa a declarar-se essa exceção e a limitá-la ao par que tem
   decisão dessa espécie não cumprida. A IR-003 enumera os dois caminhos, e só os dois.
2. **FR-033 × FR-035** — a primeira impedia a intempestividade na interposição quando há janela
   estruturada, a segunda listava "janela declarada encerrada" entre as causas de inadmissibilidade.
   A FR-035 passa a dizer que toda recusa automática incide na interposição, antes de a peça
   existir, e que ao juízo de admissibilidade só chega matéria humana e motivada.
3. **FR-011 × FR-012** — "no máximo um recurso **em curso**" sugeria que, decidido o primeiro, um
   segundo contra o mesmo objeto seria admissível, o que a FR-012 proíbe. O qualificador saiu, na
   FR-011, na D-011 e no cenário 5 da User Story 2.

**A FR-089 mudou de conteúdo, e não de número.** Ela deixou de excepcionar a regra da janela — a
exceção era inalcançável — e passa a definir o fato derivado que encerra a providência a jusante.
A contagem de requisitos permanece 111, contígua.
