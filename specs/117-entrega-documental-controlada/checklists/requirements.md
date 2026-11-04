# Specification Quality Checklist: Entrega documental controlada

**Purpose**: Validate specification completeness and quality before approval
**Created**: 2026-11-04 · **Revised**: 2026-11-04 (revisão final do usuário)
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Focused on user value and business needs: o setor exporta o necessário com esforço razoável
- [x] All mandatory sections completed
- [ ] No implementation details. **Parcial, e deliberado:** o ZIP, o `manifesto.csv` e o limite em MB
      estão na spec porque são o contrato com o setor e com a TI

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain. As escolhas abertas estão em *Pendências do usuário*,
      com proposta
- [x] Requirements are testable: cada FR tem teste na Estratégia de testes ou em `tasks.md`
- [x] Success criteria are measurable (SC-1101 a SC-1112)
- [x] All acceptance scenarios are defined (US1 a US5; os Cenários A a F no quickstart)
- [x] Edge cases are identified
- [x] Scope is clearly bounded (*O que fica fora*; *MVP e o que fica para depois*)
- [x] Dependencies and assumptions identified (PR #369; a infraestrutura da §5 do diagnóstico)

## Revisão final pedida pelo usuário

- [x] **Documentos**:
  - os quatro cenários (A a D) foram avaliados contra os dois modelos (§4.2 do diagnóstico);
  - a obrigação do candidato ficou separada do encaminhamento interno (D-009 a D-012);
  - não há taxonomia nem motor de regras.
- [x] **Permissões**:
  - as quatro opções foram comparadas (D-013);
  - quem concede é a gestão de acessos, não a presidência;
  - servidor fora da comissão pode ser designado;
  - o modelo de vínculo da `107` não muda.
- [x] **Exportação**:
  - os alcances são pessoa, seleção e recorte;
  - não há pacote do Edital;
  - não há mistura de alcances;
  - a prévia mostra pessoas, documentos, ausentes e alcance (FR-3682 a FR-3684).
- [x] **Rastreabilidade**:
  - os eventos afirmam só o que o GPS fez;
  - não há *obtido*, *encaminhado* nem *recebido*;
  - não há estados derivados (D-015, D-017).
- [x] **Falhas**:
  - o comportamento atual foi conferido no código (500 sem evento);
  - atomicidade por pessoa, com resultado completo, parcial ou sem pacote;
  - concorrência e limpeza de temporários;
  - limite justificado pela infraestrutura (§5 do diagnóstico, D-019).
- [x] **UX**:
  - uma página, um seletor de Perfil, nenhum painel;
  - uma confirmação para uma pessoa, prévia para mais de uma.
- [x] **FR-069 da `009` e FR-3606 da `115`**: exceção proposta e justificada, não aplicada, com a
      proteção geral preservada (D-016)
- [x] **Faixa de identificadores** medida em todas as worktrees e branches remotas

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [ ] **Pronta para implementar**: não. Depende das pendências bloqueantes 1 a 4
