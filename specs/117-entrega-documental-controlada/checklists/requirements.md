# Specification Quality Checklist: Entrega documental controlada

**Purpose**: Validate specification completeness and quality before approval
**Created**: 2026-11-04 · **Revised**: 2026-11-04 (revisão final) · **Consolidated**: 2026-11-04
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Focused on user value and business needs
- [x] All mandatory sections completed
- [ ] No implementation details. **Parcial, e deliberado:** o ZIP, o `manifesto.csv`, o limite e a trava
      estão na spec porque são o contrato com o setor e com a TI

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable: cada FR tem linha na Estratégia de testes e tarefa em `tasks.md`
- [x] Success criteria are measurable (SC-1101 a SC-1114)
- [x] All acceptance scenarios are defined (US1 a US5; os Cenários A a F no quickstart)
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified (PR #369; a VM não ensaiada, §5 do diagnóstico)

## Decisões aprovadas pelo usuário em 04/11

- [x] D-009 a D-012: definição interna, versionada, por Edital, sem Documento Exigido, PDF ou Retificação
- [x] D-013: papel e designação pela gestão de acessos
- [x] D-016: exceção à FR-069 da `009` e à FR-3606 da `115`, registrada com o texto aprovado e aplicada
      na T002
- [x] D-019: 400 MB como limite inicial configurável, a validar na VM
- [x] D-020, D-021; nome e protocolo no pacote, sem CPF nem contato

## Ajustes da consolidação

- [x] **Download síncrono × resultado** (D-018):
  - a verificação mostra *completo* ou *parcial*, os excluídos e o motivo **antes** do download;
  - o ZIP é sempre exatamente o verificado (FR-3684, FR-3689, SC-1105, SC-1113);
  - nada assíncrono.
- [x] **Limite** (D-019, FR-3691, SC-1111):
  - o limite inicial ficou separado da capacidade da VM (homologação, item 5; §5.4 do diagnóstico);
  - nada se presume do nginx.
- [x] **Limite excedido, tempo-limite, concorrência, exceção e temporários**: tabela de ciclo de vida no
      plano; FR-3688, FR-3692, FR-3698, FR-3714; SC-1106.
- [x] **Trava**: de transação, por servidor, cobrindo verificação e montagem e não a transferência,
      liberada no commit, no rollback ou na conexão fechada (FR-3692).
- [x] **Definição**: vazia por padrão, motivo obrigatório por constraint, histórico visível à condução
      e ao auditor (FR-3653, FR-3655, FR-3711), avisos de reserva e de inscrição (FR-3658). O risco
      residual está registrado na LGPD. Não há catálogo nem classificador.
- [x] **Pacote**:
  - nomes só do sistema, normalizados, com um nível e colisões com sufixo (FR-3712);
  - manifesto neutralizado contra fórmula (FR-3713);
  - atomicidade por pessoa (FR-3694).
- [x] **Consistência**: as decisões, os FR, a matriz (com a coluna do histórico da definição), as US,
      os SC, a Estratégia de testes e as tarefas foram conferidos entre si.

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] **Pronta para merge do PR documental**
- [ ] **Pronta para implementar**: não, até o PR #369 estar na `main`
