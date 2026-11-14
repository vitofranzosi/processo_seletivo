# Specification Quality Checklist: O efeito do desfecho da Etapa por lista

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
| Não comparecimento | FR-7004, FR-7009 |
| Recurso contra ausência que elimina, desfavorável que retira | FR-7028, FR-7029 |
| Efeito por motivo | FR-7003; *Achados* |
| Eliminado depois em outra Etapa | FR-7011 |
| Retirada antes da última Etapa do marco, ou nela | FR-7012 |
| Retirada entre a última enumerada e o horizonte | FR-7012 a FR-7014, FR-7017 |
| Retirada depois do horizonte | FR-7027; *Achados* |
| Retificação depois de todo desfavorável superado | FR-7020 |
| Faixa do corte já emitida | FR-7013, FR-7015 |
| Habilitada na Etapa governada pela faixa da ampla | FR-7014 |
| Concorrência concomitante e o 8.9 | FR-7014 |
| Já convocado pela reserva | FR-7016 |
| Recurso que devolve a reserva | FR-7019 |
| Modalidade declarada como ampla, inscrição sem Modalidade | regra de alcance da `163` |
| Etapa restrita a mais de um código | FR-7010 |
| Outra lista reservada | FR-7010, D-006 |
| Retificação que amplia o alcance | FR-7021 |
| Retificação que torna a Etapa não eliminatória | FR-7020 |
| Etapa sem inscrição alcançada | regra da `163` |
| Ato histórico | FR-7008 |
| Prévia da classificação | FR-7026 |
| Painéis e relatórios | FR-7025 |
| Etapa que nenhum marco enumera | FR-7024; risco registrado |

## Revisão do usuário de 14/11 (PR #543)

A primeira versão deste checklist marcava tudo como cumprido com uma pergunta aberta, a Q-1, fora do
formato `[NEEDS CLARIFICATION]`. A revisão apontou que isso não tornava o requisito inequívoco, e
achou mais duas ambiguidades. As três foram resolvidas na spec:

- [x] **Quais marcos a retirada alcança.** A FR-7012 dizia que a Etapa posterior ao marco não muda a
  ordem, e a FR-7014 proibia a ocupação reservada sem dizer até onde. Agora cada regra diz quais
  Resultados considera, pelo horizonte do marco (FR-7011 a FR-7014, FR-7017, FR-7027).
- [x] **"Primeiro Resultado" × "Resultado vigente".** A D-008 dizia o primeiro, e a FR-7020 dizia o
  vigente. Ficou o primeiro, com cenário de recurso que supera todos (FR-7020, SC-2334, D-008).
- [x] **Q-1 e o contrato recursal.** Fechada pelo usuário: o efeito da ausência é declarado à parte, e
  o padrão é "o mesmo efeito". O recurso ganhou a ordem de gravidade e a regra da reavaliação contra
  ausência (FR-7019, FR-7028, FR-7029). A resposta também mexeu na FR-7009, na FR-7023, na UX-741, nos
  cenários das histórias 4 e 6 e na D-007.

## Notes

- **Nenhuma pergunta aberta.** A Q-1 foi fechada pelo usuário em 14/11.
- **"Sem detalhes de implementação"** foi lido como neste repositório: a spec nomeia conceitos do
  domínio (Resultado da Etapa, consequência, faixa do corte, versão canônica, contrato de
  mutabilidade), e não tabelas, módulos nem funções. O mapa do código que sustentou as premissas
  (`resultados/domain/regra.py`, `resultados/application/prontidao.py`,
  `classificacao/domain/universo_classificavel.py`, `ocupacao/application/selectors.py`,
  `portal/situacao.py`) fica para o plano.
- **A `163` não está na `main`** (PR #542). A spec a cita só pelo assunto, para o guardião de citações
  não acusar identificador inexistente. Se a `163` mudar no merge, a seção *Assumptions* diz o que
  rever.
- Items marked incomplete require spec updates before `$speckit-clarify` or `$speckit-plan`.
