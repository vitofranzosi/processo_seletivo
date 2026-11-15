# Specification Quality Checklist: A orientação da verificação da autodeclaração

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

A seção *Edge Cases* não entra na matriz de `FR-`/`SC-`, e nenhuma ferramenta a cobra. Por isso cada
caso-limite cita, na própria linha, o requisito que o resolve. Conferido um a um:

| Caso-limite | Requisito |
|---|---|
| Etapa restrita sem Evento | FR-7305 |
| Evento retificado depois do aviso | FR-7305, FR-7319 |
| Duas Etapas restritas na mesma inscrição | FR-7309 |
| Convocada com o passo pendente | FR-7303 |
| Eliminada antes, ou não aceita | FR-7303 |
| Deixou de participar pela progressão | FR-7302, FR-7318 |
| Resultado deliberado e ainda não visível | FR-7306 |
| Etapa depois da última que o marco enumera | FR-7306 (e o achado A-6) |
| Ocorrência de ausência registrada | FR-7306 |
| Recurso contra o Resultado | FR-7307 |
| Inscrição que sai do universo antes do despacho | FR-7318 |
| Aviso depois do fim do período | FR-7323 |
| Nenhuma inscrição alcançada | FR-7322 |
| Membro exposto aos pareceres alheios | FR-7321 |
| Presidência que também é membro | FR-7321, FR-7326 |
| Etapa restrita não colegiada | FR-7321 |
| Nome da Etapa com termo técnico | FR-7336 |
| Candidato sem e-mail válido | FR-7300, FR-7318 |
| Chave do vídeo desligada depois de vídeos | FR-7313, FR-7325 |
| Acompanhamento sem Etapa restrita | FR-7311 |

## Notes

- `VERIFICACAO_POR_VIDEO`, `AVISOS_AOS_CANDIDATOS` e os nomes das telas existentes (Centro, Minhas
  atividades, Mesa, distribuição) aparecem nos requisitos porque são restrições do pedido e pontos de
  integração com o que já existe, e não escolhas de implementação.
- Nenhum marcador de esclarecimento: as cinco perguntas (Q-1 a Q-5) foram decididas pelo usuário em
  14/11, pelas recomendações, com dois ajustes registrados em *Clarifications*: o link para o Edital e
  a advertência de nome valem para qualquer Etapa restrita (FR-7304, FR-7336), e o degrau depois do
  prazo só afirma o que os dados permitem (FR-7306).
- O pedido pediu "a natureza 'verificação da autodeclaração'" no Centro. A spec a entrega como as
  pendências da Etapa restrita, lida pelo nome publicado, e não como natureza nova, porque o GPS não
  tem — e a `163` e a `164` recusaram — marcador semântico de "cota racial" (Q-1, D-001).
- `test_citacoes_de_requisito.py` verde em 14/11 (6 casos).
