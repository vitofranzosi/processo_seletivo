# Specification Quality Checklist: Avisos complementares aos candidatos, vinculados a ato oficial

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-09
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

- **Detalhes de implementação, na convenção do repositório.** A spec nomeia entidades do domínio
  (`SituacaoDivulgada`, `ComunicacaoEmitida`) e o systemd como mecanismo, como a `063` e a `019`
  fazem. Neste projeto, o vocabulário do código é o do domínio. O systemd é decisão recebida do
  usuário (decisão 6), e não escolha da spec. Linguagem, framework e estrutura de código ficam para
  o plano.
- **Contradição achada e corrigida na validação.** A `FR-1252` dizia que a única ausência admitida
  era a falta de endereço, enquanto a `FR-1251` exclui convocações pelo estado do ato. A redação
  passou a nomear as duas. O checklist não detecta contradição, e por isso a varredura foi feita à
  mão.
- **Casos-limite com consequência estão também em FR.** A seção Edge Cases não entra na matriz de
  rastreabilidade.
- **Revisão do usuário, de 09/10/2026, aplicada.**
  - `D-003` separa o universo histórico do ato da elegibilidade atual para o aviso.
  - `D-006` passou a conferir a interrupção antes de cada tentativa e a avisar que o que foi aceito
    não volta.
  - `D-007` trocou o bloqueio por varredura de texto por assunto neutro por construção.
  - `D-008` passou a ter três modelos iniciais criados uma vez.
  - O limite de envio virou parâmetro, e um requisito novo proíbe teste contra servidor real.
- **Validação de consistência, segunda rodada.** A varredura manual achou a contagem "excluídas pelo
  ato" na `FR-1259`, sobra da redação anterior da `D-003`, e ela foi trocada por "não elegíveis".
  `/speckit-analyze` só se aplica com plano e tarefas, e roda depois de `/speckit-tasks`.
