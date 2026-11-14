# Specification Quality Checklist: As regras de deliberação dos pareceres

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-14
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

## Casos-limite como requisitos

Os casos-limite não entram na matriz de FR- e SC-, e nenhuma ferramenta os cobra. Por isso cada um
foi conferido contra o requisito que o resolve:

| Caso-limite | Requisito |
|---|---|
| O empate | FR-7052, D-003 |
| O desfecho inevitável antes do último parecer | FR-7062, D-005 |
| Uma avaliação por inscrição | FR-7053, FR-7068 |
| Etapa pontuada com mais de uma avaliação | FR-7053; *Achados* |
| Etapa decisória não eliminatória com regra | FR-7064 (FR-047 da `013`) |
| O acervo publicado | FR-7054, D-002 |
| Pareceres a menos | FR-7062 |
| Pareceres a mais | FR-7062, FR-7073 (FR-092 da `012`) |
| A reavaliação na Etapa colegiada | FR-7071, D-007; *Achados* (condição para a P-5) |
| Membro impedido depois de concluir | FR-7061, FR-7062 (FR-092 da `012`) |
| Pareceres sob versões diferentes | FR-7063, FR-7065, FR-7074 |
| Retificação da regra antes de qualquer Resultado | FR-7073, FR-7074 |
| Retificação da regra ou do número depois do primeiro Resultado | FR-7073, D-008 |
| Presidência ou auditoria que também é membro | FR-7056 |
| Leu como presidência e recebeu atribuição depois | FR-7082, D-010 |
| Concluiu, leu como presidência, e o parecer é reaberto | FR-7083 |
| A conferência da consolidação | FR-7056, FR-7067 |
| A reabertura | FR-7058 |
| O membro que leu antes de concluir | FR-7056, FR-7057, FR-7082 |
| Às cegas não é anonimização do candidato | FR-7059 |
| A trilha | FR-7060 |
| O não comparecimento | FR-7064 |
| Motivos diferentes no mesmo sentido | FR-7061; *Achados* |
| O recurso | FR-7069 a FR-7072, FR-7081 |
| A Etapa restrita | FR-7076; regra de alcance da `163` |
| A parte pública | FR-7078 |
| A prévia da classificação | FR-7080 |
| Rótulos ausentes | FR-7066, FR-7075 |

## Notas da validação

- **Iteração 1.** A primeira redação da FR-7060 prometia que a trilha não permitiria inferir o sentido
  de um parecer. Sob uma regra de unanimidade, a consequência do Resultado às vezes basta para deduzi-lo,
  como hoje a de uma avaliação única basta. A FR-7060 foi reescrita para o que é verificável: a trilha
  da conclusão sem sentido nem texto, e a da consolidação sem regra nem contagem.
- **Iteração 2, revisão do PR #545.** Seis achados corrigidos: a contagem no cumprimento da
  reavaliação (FR-7062, FR-7071, caso-limite novo), a revisão declarada da invariante de proveniência da
  `013` (FR-7065, D-006), o julgador com parecer pendente (FR-7069), a saída de "pareceres a mais"
  (FR-7062, FR-7073), a autoria só para a gestão (FR-7081, cenário 5 da US3) e a base sobre a correção da
  `164` (FR-7066, FR-7072). A faixa usada passa a ir até a FR-7081.
- **Iteração 3, `/speckit-clarify`.** Pergunta 1 respondida pelo usuário (opção B): na Etapa colegiada,
  o recurso corrige por correção fixada, e a reavaliação determinada é recusada antes de gravar. Revistos
  a US5, os casos-limite do recurso, a FR-7062 (sai a contagem do cumprimento), as FR-7070 a FR-7072, a
  entidade da decisão de recurso, a D-007 e *Achados*.
- **Iteração 4, `/speckit-clarify`.** Pergunta 2 respondida pelo usuário (opção A): o titular lê a regra,
  a contagem e o texto de cada parecer desfavorável, sem autoria, nas condições da `036`. Revistos a US4
  (seis cenários), a FR-7066 (motivo sem texto de parecer), as FR-7076 e FR-7077, a FR-7081 (a autoridade
  recursal vê tudo), a D-009, e acrescido o UX-754 (orientação de preenchimento).
- **Iteração 5, `/speckit-clarify`.** Pergunta 3 respondida pelo usuário (opção A): a restrição é do
  servidor, alcança a revelação indireta e vale por inscrição × Etapa. A FR-7056 foi reescrita, a US2
  ganhou quatro cenários (6 a 9), o SC-2352 passou a cobrir link direto, exportação e resposta do
  servidor, e o caso "leu como presidência e recebeu atribuição depois", que o usuário pediu para
  fechar, virou a exposição: FR-7082, FR-7083, a entidade nova e a D-010.
- **Nenhum marcador de esclarecimento.** A única escolha normativa aberta, qual regra os Editais do Ifes
  usarão, é da CPVA e não bloqueia a spec: a spec oferece as três e não marca nenhuma (D-002).
- **Vocabulário de implementação.** "Degrau da versão canônica", "contrato de mutabilidade" e "guardião"
  são o vocabulário de domínio do projeto, e as specs `163` e `164` os usam do mesmo modo.
- **Citações.** A `163` e a `164` são citadas só pelo assunto, porque não estão na `main`. Os requisitos
  citados de outras features (`012`, `013`, `018`, `036`) foram conferidos na spec de cada uma.
