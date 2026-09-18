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

**Três observações sobre como esta spec passou na validação, porque nenhuma delas é gratuita.**

1. **"Sem detalhe de implementação" foi o item mais difícil, e a spec cede em um lugar de
   propósito.** A seção *Por que esta feature existe* cita arquivos e funções por nome. Isso não é
   desenho da solução: é a **medição do estado**, e ela está ali porque a `033` produziu três
   medições erradas seguidas por ter descrito a superfície de memória. O que a spec **não** faz é
   dizer como a emissão por recorte deve ser construída — e as `FR-` não citam arquivo nenhum.

2. **`FR-491` é requisito sobre o código, e é o caso em que isso é legítimo.** Ele exige uma
   derivação única do conjunto de recortes. A razão é observável pelo usuário — ordem emitida para
   recorte que a ocupação não consome é ato publicado que não leva a lugar nenhum —, e o critério que
   o prende, `SC-172`, se verifica comparando duas listas, sem saber como elas são produzidas.

3. **Uma decisão normativa foi tomada com quem governa o backlog, e não presumida.** O `D-001` — o
   autodeclarado ordenado nas duas listas — foi perguntado e respondido em 18/09/2026. A evidência
   que sustentou a recomendação está registrada nas *Assumptions*, e a alternativa descartada também.

**O que fica em aberto para o `plan`, e está nomeado na spec:**

- O recorte reservado **sem nenhum autodeclarado** — ordem vazia publicável ou ausência de ato? É o
  primeiro *Edge Case*, e a diferença é de significado, não de forma.
- O destino exato do aviso da `032` (`FR-501`): some ou estreita. A spec obriga a decidir e a
  registrar; não decide por antecipação.
- A Retificação que acrescenta Modalidade depois de a ordem da ampla já ter sido emitida.

**Medições a reconferir no `plan`, e não a assumir** — a tabela de *Por que esta feature existe*
inteira, e em especial a ausência de migration (`FR-505`) e a divergência entre as duas derivações
homônimas de `recortes_do_marco`.
