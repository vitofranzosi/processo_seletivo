# Specification Quality Checklist: Corte e Progressão entre Etapas

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-11
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

## Varredura própria de contradição

A checklist genérica já fechou 16/16 numa feature cujos requisitos se contradiziam, e por isso esta
seção existe. O que foi conferido à mão, par a par:

- [x] **Sucessão contra continuação.** FR-200 (um sucessor no máximo) e FR-202 (faixa seguinte que
      não revoga a anterior) descrevem operações distintas, e FR-202 diz isso explicitamente. IO-1
      fala em cadeia, e FR-208 lê *alguma faixa vigente* — as duas leituras fecham.
- [x] **Efeito do corte contra progressão da 013.** FR-208 soma e FR-209 proíbe revogar; o cenário 4
      da US3 exercita o eliminado que estaria dentro da faixa.
- [x] **Empate.** FR-181 declara, FR-182 impede a ausência, FR-195 recusa sob alvo estrito e FR-196
      admite o excedente. Nenhum dos quatro decide empate por conta própria, e o caso de borda fixa
      que a regra incide sobre a última posição **da faixa emitida**, não do alvo.
- [x] **Alvo derivado.** FR-179 e FR-189 (apuração) contra FR-183 (linha ausente impede) e o caso de
      borda do alvo zero. Linha ausente e linha zerada não são a mesma coisa em lugar nenhum.
- [x] **Obsolescência.** FR-215 lista quatro causas, D-007 lista as mesmas quatro, FR-216 obriga a
      nomeá-las e FR-217 proíbe alterar o vigente. FR-198 não conflita: ele impede **emitir sobre**
      ordem obsoleta, e não altera corte nenhum.
- [x] **Fronteira com a 016.** FR-207 e SC-066 são a mesma proibição vista do lado do requisito e do
      lado da verificação; a Out of Scope repete o corte em prosa. Nenhum requisito apura déficit.
- [x] **Não regressão.** FR-214, IO-10 e SC-069 dizem a mesma coisa em três alturas, e nenhum outro
      requisito a contradiz: nada nesta feature altera Edital sem Regra de Corte.

## Segunda varredura — a revisão cruzada de 11/09

A primeira varredura fechou 16/16 e não pegou três incompatibilidades de domínio. O que a segunda
leitura encontrou, e onde está resolvido:

- [x] **A faixa inicial contra o teto da continuação.** `FR-180` mandava somar o excedente e `FR-204`
      dava à continuação o teto `alvo + excedente`, que a faixa já teria consumido. Fechado pela
      `D-011`: primeira emissão `alvo + excedente`, continuação declarada e sem teto numérico.
- [x] **A Etapa governada derivada.** Num marco de sorteio a Etapa enumerada não é norma. Fechado
      pela `D-012`: declarada, ou `NONE` declarado; nunca inferida.
- [x] **Sucessão de faixa contra sucessão de geração.** Depois de `raiz → continuação` as duas são
      vigentes, e suceder uma deixava a outra governando. Fechado pela `R-010` e pela `FR-227`, com
      `raiz` no modelo e a sucessão ligando raiz a raiz.
- [x] **Obsolescência sem política operacional.** Fechado pela `D-013`: bloqueia trabalho novo na
      Etapa governada até a geração sucessora.
- [x] **Quadro parcial com três listas.** Fechado pela `D-014`: linha exigida para todo recorte que o
      marco ordena.
- [x] **Canonicalização do `cutRule`.** `surplusCount` sempre emitido e uma grafia por espécie para
      `targetCount`, para que a comparação de obsolescência não acuse diferença onde não há.
- [x] **"Nenhum módulo novo"** virou "nenhum app, camada ou serviço novo" — a feature cria três
      módulos, e dizia que não criava nenhum.

## Notes

- As duas decisões normativas — desfecho do empate (D-001) e fronteira com a `016` (D-002) — foram
  fechadas pelo usuário em 11/09/2026, antes da redação, e não são suposição desta spec.
- Faixa de identificadores conferida contra todas as worktrees antes de escrever: abre em `FR-178`,
  `SC-055`, `UX-024`.
