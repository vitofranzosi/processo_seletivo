# Specification Quality Checklist: A fonte de consulta do Edital vigente (Fase A do assistente de dúvidas)

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

## Itens próprios desta feature

- [x] O que poderá ser validado ao concluir a Fase A, o que fica para o piloto com LLM e o que fica
      para a disponibilização pública estão explícitos (seção *O que esta fase entrega, e o que fica
      para depois*)
- [x] O piloto com LLM e a disponibilização pública estão registrados como fases posteriores (seção
      *Fases posteriores*; o repositório não tem arquivo de roadmap, e o registro está também no §9 da
      auditoria)
- [x] A compatibilidade com a `069` foi conferida e o conflito remanescente está registrado (seção
      *Compatibilidade com a 069*)
- [x] A divergência do link "Edital completo" foi reproduzida antes de a spec decidir sobre ele, e a
      correção ficou como dependência, e não como escopo (achado; `D-004`)
- [x] A faixa de identificadores foi medida em todas as worktrees e nos PRs abertos; a pasta `070` é a
      seguinte livre
- [x] Nenhuma decisão de outra spec foi alterada

## Decisões do usuário de 12/10/2026 → onde a spec as cumpre

| Decisão ou ponto obrigatório | Requisitos e decisões |
|---|---|
| Uma spec para a Fase A, interna, sem FAQ independente, plataforma de IA ou interface pública | `FR-1419`, `FR-1445`, `FR-1447`, `UX-205`, `D-001`, `D-002` |
| Piloto e público como fases posteriores | *Fases posteriores* |
| Cartões com informação, versão e links; sem leitura integral em HTML | `FR-1411`, `FR-1437`, `FR-1438`, `UX-201` |
| Literal, dado e explicação distinguidos | `FR-1432` a `FR-1436`, `UX-200`, `SC-534`, `D-003` |
| Frase recomposta pelo código não é citação do PDF | `FR-1434`, `D-003` |
| Compatibilidade com a `069` | *Compatibilidade com a 069* |
| Canal do Edital primeiro; o da implantação só na falta | `FR-1439`, `FR-1441`, `D-005` |
| Não escolher entre instruções contraditórias; registrar | `FR-1440`, `FR-1443`, `SC-539` |
| "Exclusivamente" como questão antes da abertura pública, sem bloquear a Fase A | `FR-1442`, `FR-1443` |
| Versão vigente a cada consulta, inclusive com vigência futura | `FR-1410`, `FR-1414`, `FR-1451`, `D-009`, User Story 2 |
| Resposta e referências da mesma versão | `FR-1411`, `SC-531` |
| Sem rascunho nem dado administrativo fora do publicado vigente | `FR-1412`, `FR-1413`, `SC-532` |
| Não responder pelo histórico quando a versão mudou | `FR-1415`; `CA-18`, `CA-19` |
| Condições e exceções, inclusive em descrição de Evento | `FR-1420`, `FR-1426`, `D-007`; `CA-14` |
| Ausente, ambígua e conflitante distinguidas | `FR-1421` a `FR-1424`, `D-008` |
| Perguntas que dependem de anexo | `FR-1430`; `CA-13` |
| Vagas de ampla concorrência | `FR-1427`; `CA-03` |
| Reaproveitar a matriz da auditoria | `FR-1450`, `SC-530` |
| Reproduzir o "Edital completo" antes de depender dele | achado de 12/10; `FR-1437`, `FR-1443`, `SC-535`, `D-004` |
| Fase A sem modelo; isolamento futuro sem infraestrutura antecipada | `FR-1447`, `FR-1448`, `SC-536` |
| Alcance da tela sem capacidade nova — análise de 12/10, item C1 | `FR-1445`, `D-010` |
| "Respondida" exige cobertura do enunciado; anexo no núcleo é "Depende da leitura" — validação de 12/10 | `FR-1421`, `FR-1430`, `D-011` |

## Notes

- **Validação em uma iteração.** Todos os itens passaram, e não houve marcador de clarificação.
- **Termos que parecem implementação, mas não são escolha técnica.** "rota", "API", "fila", "worker"
  e "servidor" aparecem só como **exclusão de escopo**, que vem da decisão 7º do usuário, e não como
  escolha de implementação (`FR-1445`, `FR-1447`).
- **Caminhos de arquivo.** O caminho `docs/libras/editais/*/fonte/` em `FR-1450` identifica os dados
  de referência da avaliação, e não uma estrutura de código.
- **Vocabulário do domínio.** "Versão consolidada", "vigência" e "Retificação" são linguagem ubíqua do
  domínio (princípio I), e não detalhe técnico.
- **Para o plano decidir, sem mudar o que a spec exige:**
  - a lista fechada de termos de dúvida e de exclusividade (`FR-1439`, `FR-1442`);
  - a revisão da tabela de pertinência com o setor (`D-007`);
  - a confirmação de que o alcance da tela é o da página do Edital (*Assumptions*);
  - como reproduzir o corpus em ambiente de teste (`FR-1450`).
- **Verificado nesta rodada.** `tests/test_citacoes_de_requisito.py` e
  `tests/test_sem_dado_pessoal_da_amostra.py` passam com a spec nova.
- **Análise de consistência de 12/10/2026.** Aplicados C1 (`D-010`), I1 (`FR-1450` e `SC-530` em
  duas camadas), A1 (lista literal é dado, no `R-013` e no contrato), G1 (zero chamadas externas em
  T028), G2 (determinismo em T015) e U1 (leitura da versão-base em T010 e no data-model). Ficaram
  abertos, como baixos: G3, G4, G5, U2 e O1.
- **Próximo passo possível.** `/speckit-clarify` é opcional, porque não há marcador. `/speckit-plan`
  pode seguir.
