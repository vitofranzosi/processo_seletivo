# Specification Quality Checklist: Ordenação e Classificação

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-04
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

**Histórico da validação.** A primeira passagem fechou em **13/16**, e não em 15/16: além dos três
marcadores [NEEDS CLARIFICATION], "requirements are testable and unambiguous" e "all functional
requirements have clear acceptance criteria" também falhavam, porque um requisito com pergunta
aberta dentro não é testável. A segunda passagem, depois das respostas, fecha em **16/16**.

**O que as três respostas fixaram:**

1. **Combinação (FR-008 a FR-012).** O marco enumera as Etapas; `weight` continua sendo a fonte
   autoritativa do peso; só Etapa classificatória participa; a operação nova declara também
   normalização e arredondamento; os pesos não precisam somar 1.
2. **Empate residual (FR-023 a FR-026).** Emite com posições compartilhadas, e o ato registra que
   dentro do grupo empatado não existe ordem normativa. O corte que atravessar o grupo é problema
   da 014.
3. **Eliminado na Etapa do marco (FR-007).** Permanece no snapshot como participante considerado,
   sem posição, com consequência e motivo — fechando com FR-003, FR-006 e SC-016.

**Dois ajustes que não vieram das perguntas:**

- a **regra do marco entrou no universo** (D-003, FR-003, FR-034, IO-7, SC-013): Retificação que
  alcance operação, enumeração, pesos ou critérios obsoleta o ato sem que nenhuma entrada mude;
- **valor ausente virou requisito** (FR-017), e não suposição: critério sem comportamento declarado
  para valor inexistente impede a publicação da regra.

**Sessão de clarificação (2026-09-04).** Cinco perguntas, cinco respostas, todas integradas: a
emissão concorrente é recusada e suceder exige recálculo com confirmação explícita (FR-029,
FR-030); a numeração segue a classificação padrão, `1, 1, 3` (FR-025, IO-9, SC-017); reprodução é
garantia interna testável e a jornada expõe a proveniência inteira (FR-039 a FR-041); ato cuja
regra deixou de ser computável fica obsoleto **e não recomputável**, dito na tela (FR-037, FR-038,
SC-014); e a tela do marco abre em até 3 segundos a 1.000 participantes (SC-002). Os 16 itens
permanecem passando depois das integrações.

A US5 deixou de depender de "Resultado revisto" — a 013 admite um Resultado imutável por Inscrição
× Etapa, e superá-lo é da 018. A sucessão passa a nascer de Resultado tardio ou de Retificação da
regra, e permanece compatível com a 018 sem pressupô-la.

Nomes citados no corpo — `SCHEMA_VERSION`, `weight`, `classificatory`, `ResultadoEtapa`,
`competitionModalities` — são referências a conteúdo normativo e a contratos já entregues,
verificados no código em 04/09/2026, e não escolha de implementação desta feature.
