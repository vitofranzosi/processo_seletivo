# Specification Quality Checklist: Integridade do Snapshot Normativo

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-29
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

## Notas da avaliação

### Reavaliação após `$speckit-clarify` (2026-08-29)

A revisão da spec apontou quatro problemas, todos verificados antes de aceitar. Três viraram
clarificação; o quarto e um erro editorial foram corrigidos direto.

**Alcance do esquema (Q1).** A spec exigia presença e não dizia nada sobre tipo. Medido: `name = []`,
`immediateVacancies = "muitas"`, `immediateVacancies = None`, `startAt = {}` e `requirements = "texto"`
atravessam a validação atual sem achado impeditivo. A decisão foi conferir presença, tipo,
nulabilidade e formato — o que `PerfilInput` e `EventoInput` já declaram no contrato da `001` —,
aceitando campo desconhecido e sem regra de negócio nova (FR-009).

**Portão da Publicação (Q2).** O teste independente da US1 era inalcançável: a US2 recusa o ato na
elaboração, então ele nunca chega à Publicação. Reescrito para partir de um ato malformado já
homologado e gravado direto, que é o padrão da `003` para a linha que chega por fora da borda. Virou
também FR-013, para que a razão de o portão não ser redundante fique escrita.

**Fronteiras temporais (Q3).** `FR-003` dizia "o conteúdo consolidado", no singular, e a Publicação
materializa uma versão por fronteira de vigência. O singular permitia implementar só a primeira e
deixar a seguinte vigorar malformada semanas depois. Passou a exigir toda fronteira materializada.

**`SC-006` saiu dos critérios funcionais.** Cobertura com ramos é métrica de entrega, não resultado
observável por quem usa. Fica registrada aqui para o plano recolher: **a suíte deve permanecer verde
nas duas execuções — SQLite e PostgreSQL — e o código escrito nesta feature deve ter cobertura com
ramos integral.**

**Avaliação de LGPD acrescentada.** O princípio III da Constituição exige que cada especificação
avalie os requisitos aplicáveis, e **nenhuma das cinco specs do projeto havia feito isso** — não é
lacuna só desta. A avaliação é "não aplicável", com as quatro razões escritas.

**Erro editorial no relato anterior.** Eu disse "cinco exclusões" e depois "acrescentei um sexto"; o
*Out of Scope* tem cinco itens no total — quatro vieram da definição de escopo e um foi meu.

Numeração reconciliada depois das inserções: 15 requisitos e 5 critérios contíguos, todos mapeados
na rastreabilidade nos dois sentidos.

Duas passagens foram necessárias.

**O que a primeira encontrou.** Três requisitos citavam nomes de função e de módulo —
`validate_for_publication`, `apply_changes` — e um critério media cobertura de arquivo. Eram
detalhe de implementação em seção que não os admite, e foram reescritos pelo comportamento:
"a verificação que existe hoje olha quatro condições na raiz" no Contexto, e a exigência em si
formulada como o que o sistema deve fazer, não onde. `SC-006` fala em "código escrito nesta
feature", que é verificável sem nomear arquivo.

**Códigos HTTP são contrato, não implementação.** `FR-009` diz `422`, e `FR-010` cita a forma de
caminho `/profiles/id=<uuid>/name`. Ambos são superfície observável, fixada pelo contrato público
da `001` e pela gramática da `004`; descrevê-los como "recusa apropriada" tornaria o requisito
menos testável sem torná-lo menos técnico. Mantidos deliberadamente.

**Nenhuma clarificação ficou pendente.** Quatro pontos admitiam mais de uma leitura e foram
resolvidos como suposição declarada, por existir padrão razoável em cada um: o alcance da
verificação aos dois caminhos de Publicação, o que conta como campo obrigatório, o tratamento de
base já malformada e o reaproveitamento da classificação de severidade. Estão na seção Assumptions,
onde `$speckit-clarify` pode contestá-los.

**Escopo.** O *Out of Scope* nomeia cinco exclusões e diz por que cada uma sai — incluindo a razão
técnica de a validação por valor não substituir a validação do resultado, que é o que distingue
esta feature de uma versão mais barata dela.
