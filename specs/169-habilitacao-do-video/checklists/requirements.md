# Specification Quality Checklist: A habilitação da verificação por vídeo pela interface

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

A seção *Edge Cases* não entra em matriz nenhuma, e nenhuma ferramenta a cobra. Por isso cada caso
aponta o requisito que o cobre, e esta tabela confere que o requisito existe e diz o comportamento.

| Caso-limite | Requisito | Conferido |
|---|---|---|
| Capacidade desligada com base vigente e Editais em curso | FR-7424, FR-7425 | [x] |
| Revogação no meio de um envio, inclusive na tolerância de uma hora | FR-7431 | [x] |
| Revogação no meio do período, candidato sem gravar | FR-7431 (e Q-3) | [x] |
| Base alterada entre a Revisão e a confirmação | FR-7421 | [x] |
| Base alterada depois da publicação | FR-7423, FR-7426, FR-7427 | [x] |
| Prazo de guarda alterado depois de vídeos recebidos | FR-7429, FR-7432 (e Q-2) | [x] |
| Retirada de uma unidade do alcance | FR-7424, FR-7431, FR-7432 | [x] |
| Base nova depois de uma revogada | FR-7423, FR-7424 | [x] |
| Rascunho que marcou o vídeo, base revogada antes da publicação | FR-7418, FR-7422 | [x] |
| Edital de unidade não alcançada | FR-7418 | [x] |
| Edital da `166` publicado em desenvolvimento sem citação | FR-7419, FR-7424, FR-7425 | [x] |
| Atos concorrentes sobre a base | FR-7412 | [x] |
| Retificação que acrescenta o vídeo a outra Etapa | FR-7423 | [x] |
| Alteração sem mudança, revogação repetida, registro com vigente | FR-7408, FR-7409 | [x] |
| Protocolo que aprova roteiro ou regra não implementados | FR-7407 | [x] |
| Revogação com a capacidade desligada | FR-7411 | [x] |
| Escopo de unidade ativo e sessão de demonstração | FR-7414 | [x] |
| Variável de nome antigo e variável do prazo no ambiente | FR-7400, FR-7402 | [x] |
| Data futura, prazo não positivo | FR-7406 | [x] |
| Edital encerrado com base revogada | FR-7429, FR-7433 | [x] |
| Recurso num Edital de base revogada | FR-7433 | [x] |

## Notes

- Os nomes de variável de ambiente, a permissão `verificacao-por-video:habilitar` e o limite de 8 MiB
  da `166` aparecem nos requisitos porque são o contrato com quem implanta e a fronteira que a spec
  revê, e não escolhas de implementação. O plano decide as tabelas, o degrau do conteúdo publicado e o
  mecanismo da trilha.
- Nenhum marcador de esclarecimento. As quatro perguntas que dependem do usuário estão em *Perguntas
  ao usuário* (Q-1 a Q-4), cada uma com recomendação adotada como comportamento provisório. As
  pendências P-0, P-7, P-8 e P-10 são da instituição, e a spec **não** lhes dá valor: cria o lugar
  onde elas se registram.
- O que a `166` deixa de valer está na tabela de *Por que esta feature existe*, requisito a requisito.
- Revisão contra a Constituição: Princípio II (a citação é conteúdo publicado e imutável, a norma de um
  ato é a que ele citou), III (negar por padrão, menor privilégio, trilha com antes e depois, nada se
  exclui, prazo de guarda informado ao titular) e IV (alcance visível antes do ato, reconferência sob
  trava, regra no domínio, uma resposta só).
