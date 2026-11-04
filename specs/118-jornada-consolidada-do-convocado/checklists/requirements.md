# Specification Quality Checklist: A jornada consolidada do candidato convocado

**Purpose**: Validate specification completeness and quality before proceeding to implementation
**Created**: 2026-11-04
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

## Pedido da sessão de origem (04/11/2026)

- [x] Projeção derivada, sem armazenamento, sobre `LeituraDocumental`, a política do Requerimento,
      `estado_de`/`prazo_decorrido` e o desfecho (FR-3721)
- [x] Distingue: fazer, aguardando conferência, conforme, aproveitado, Requerimento (não enviado,
      enviado, prazo encerrado), facultativo, prazo (não iniciado, em curso, vencido) e desfecho
      (FR-3722, FR-3725, FR-3737, FR-3749)
- [x] Sem segunda contagem nem decisão automática (FR-3721, FR-3729)
- [x] Facultativo não conta; com a comissão não é tarefa; aproveitado nunca reenviado (FR-3723,
      FR-3724)
- [x] A precedência da FR-3591 não serve ao candidato; a pendência vem primeiro (FR-3726)
- [x] Acompanhamento: ação do conjunto, à convocação mesmo com o Requerimento enviado; enviado como
      linha secundária; sem documento, como está; vencido sem ação recusável (FR-3730 a FR-3733)
- [x] Convocação na ordem pedida, com âncoras; botão de navegação sem "Enviar…" (D-004); pós-desfecho
      só histórico (FR-3735 a FR-3742)
- [x] Linguagem: os textos da §5 do relatório, com a correção da frase de conclusão (D-005); prazo
      num formato; o fim do prazo não decide nada sozinho (FR-3746 a FR-3750)
- [x] Os seis ajustes de polish: destaque (FR-3744), "Envie o arquivo" (FR-3746), "Voltar à
      convocação" (FR-3752), "se você for convocado" (FR-3752), nome acessível (FR-3745), sem
      "Envie até" depois do desfecho (FR-3742)
- [x] Revisões da FR-1175 a FR-1178 da `063`, da FR-3612, da FR-3577 e da User Story 2 da `115`, da
      FR-1090, da FR-1096 e da FR-1097 da `059` e das mensagens da `029`, com as redações anteriores
- [x] Conflitos resolvidos explicitamente (tabela de compatibilidade)
- [x] Validação planejada: cenários A–K com C2 e I2, testes por camada, capturas, critérios, e os
      testes que prendem os textos atuais (plan.md)
- [x] QI-7 registrada com recomendação, sem desenvolver
- [x] Correção por sucessão verificada; achado em `doc/`, separado da spec

## Revisão do PR #376 (04/11/2026)

- [x] Opcionais alcançáveis sem tarefa; facultativo em uma categoria só (D-018)
- [x] Fechamento pelo Processo distinto do vencimento; nada promete conferência (D-015)
- [x] Requerimento pedido e não enviado preservado depois do desfecho (D-016)
- [x] Prazo não iniciado prevalece sobre cartões, opcionais e conclusão (FR-3749)
- [x] Sem documento, a ação de hoje, inclusive o enviado (D-017); spec, plano e SC-1123 alinhados
- [x] FR-3756 restringe efeito, não arquivo; garantias de escrita, titularidade e privacidade com
      teste (T025a)
- [x] Lista explícita dos textos que saem e dos que ficam (plano)
- [x] Cenários de controle B2, L, M, N e K2 (SC-1127)
- [x] Revisão independente das precedências (04/11): dez achados aplicados — FR-3721, FR-3725,
      FR-3726, FR-3730, FR-3736, FR-3741, FR-3748, FR-3754, D-007 e o plano; a lacuna do Requerimento
      não enviado sem documento, registrada

## Notes

- **Detalhe de implementação na spec, de propósito.** A spec cita funções (`estado_de`,
  `LeituraDocumental`) e arquivos na FR-3721 e nas decisões, no padrão do repositório (`115`, `117`):
  a projeção precisa ser lida contra as fontes reais, para provar que não há segunda contagem. Os
  demais requisitos falam de comportamento e de texto.
- **Textos literais nos requisitos.** Como a FR-3612 da `115` e a FR-1177 da `063`, os textos são o
  requisito: a falha que a spec corrige é de redação.
- **Nenhum marcador [NEEDS CLARIFICATION].** As decisões do usuário estão em D-001 a D-006; as
  propostas de desenho, em D-007 a D-014, para a revisão do PR.
- **Contradição não se detecta por checklist.** Conferido à mão: a frase de conclusão (FR-3728) não
  aparece com tarefa (FR-3730, linha 3); o núcleo do vencido (FR-3748) é o mesmo nas recusas
  (FR-3622 da `115`); a estrutura sem documento (FR-3743) não contradiz a FR-3574 da `115` (tabela de
  compatibilidade).
