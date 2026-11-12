# Specification Quality Checklist: Conferência com o documento à vista

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-11
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

- **Sem marcador inline, com três questões abertas.** As decisões que são do usuário estão em
  "Questões para o usuário" (Questões 1 a 3); a 4 foi respondida em 11/11, cada uma com a proposta da spec em primeiro lugar; as
  decisões D-005, D-006 e D-007 seguem a proposta até a resposta. O `/speckit-plan` pode partir das
  propostas, mas a FR-6527 e a extensão da FR-6533 mudam com a resposta às Questões 2 e 3.
- **Detalhe de implementação, deliberado.** A spec diz que a rota do arquivo não se deixa emoldurar
  hoje e que a da Mesa sim (FR-6504). É o fato que separa "reaproveitar a Mesa" de "funcionar": sem
  ele, o painel não carrega. A técnica — decorador, cabeçalho, fragmento, biblioteca — fica para o
  plano.
- **"Tela larga"** é a fronteira da Mesa; o número é do plano e da folha comum, e não desta spec.
- **Verificação humana.** SC-2149 (teclado e leitor de tela), SC-2150 (celulares reais) e SC-2151
  (antes e depois, com quem conduz) não se automatizam; o comportamento do PDF dentro da moldura em
  iOS e Android muda entre versões, e só o aparelho responde.
- **Citações.** Só requisitos definidos na `main` (a `154` entrou pelo #479 durante a escrita e é
  citada pela FR-6211); os achados do estudo, como "achado NN".
- **Achado 09, acrescentado em 11/11** a pedido da sessão coordenadora (User Story 7, FR-6534 a
  FR-6538, UX-647, UX-648, SC-2152, SC-2153, D-008, Questão 4). A decisão do usuário de 08/11 na `134`
  — aviso por gesto, nunca por evento — fica intacta nas três opções; a B revê só a letra da FR-4604
  da `134`, e por isso é opção, e não proposta.
- **Questão 4 respondida em 11/11** (D-008): opção A com ajustes do usuário — *"Pedir aviso para
  ‹nome›"*, todas as pendências elegíveis, sem exceção ao limite diário nem agendamento, situação em
  solicitado, enviado e não enviado. A `134` foi revista na FR-4603, na FR-4605 e na FR-4620, com a
  redação anterior preservada; a FR-4604 não muda. Faixa usada: FR-6500 a FR-6543, SC-2140 a SC-2154,
  UX-640 a UX-650.
