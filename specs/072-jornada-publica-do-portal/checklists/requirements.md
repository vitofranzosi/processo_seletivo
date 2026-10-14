# Specification Quality Checklist: A jornada pública do portal

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-12
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

Validação de 12/10/2026, uma iteração:

- **Detalhe de implementação.** A primeira redação citava o nome de uma função na tabela de
  reconciliação; trocado pela decisão que ela implementa. Ficaram, de propósito, "envio de
  formulário" (FR-1624) e "sem execução de script" (FR-1603): são a garantia que a feature preserva —
  a confirmação explícita e a consulta que funciona sem script —, não escolha de técnica.
- **Critérios mensuráveis.** SC-600 e SC-601 citam o script de medição da auditoria como **método**
  de verificação, com as telas definidas por largura e altura; o resultado esperado é independente
  dele. SC-605 tem limite proposto (quatro em cinco), registrado como ajustável nas Assumptions.
- **Escopo.** Os nove recortes do responsável pelo produto (Q1 a Q9) estão na tabela de decisões e na
  seção "O que esta feature não cobre"; duas exclusões vieram da coerência com o registrado — cartão
  compacto de encerradas (contrariaria a UX-016) e contraste do contorno de campo (token compartilhado
  com a gestão).
- **Dependências.** Validação do texto de finalidade de "Seus dados" por quem responde pela proteção de
  dados (FR-1627); custo do resumo de resultados independente do número de cartões (Assumptions, para
  o plano); cenários de vários resultados e prazos exigem dados que o seed não produz (User Story 5).
- **Citações.** `tests/test_citacoes_de_requisito.py` verde: as referências a outras features usam
  identificadores definidos na `main`, e as decisões de outras features são citadas por extenso ("a
  decisão 008 da `024`").
- **Ponto de atenção para a clarificação:** a regra de resumo de vários resultados e prazos (D-004) é
  a decisão de maior risco de leitura errada; vale confirmá-la antes do plano.
