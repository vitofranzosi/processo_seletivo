# Specification Quality Checklist: O piloto interno do assistente conversacional do Edital (Fase B)

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-12
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — os dois (DP-1, DP-2) decididos pelo usuário em 12/10
      (*Clarifications*; `D-012`, `D-013`)
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

- [x] A `070` é consumida, e não reescrita: as quatro portas, e o efeito de cada ajuste nelas sobre o
      piloto, estão na seção *Como a 070 é consumida*
- [x] A versão da fonte é registrada em cada rodada, e o resultado não atravessa versões (`FR-1515`,
      `D-010`)
- [x] A T046 aparece como dependência da disponibilização pública, e não da preparação (*O estado de
      partida*; *Critérios de conclusão do piloto*)
- [x] Os erros conhecidos do canal da `070` estão registrados com o efeito aqui, e o defeito da fonte
      não conta contra o modelo (`FR-1514`, `CB-08`, DP-6)
- [x] O que o OpenRouter valida e o que só o Ollama na L4 valida estão separados (tabela própria;
      `FR-1516`, `SC-555`)
- [x] Nada sobre o modelo instalado é presumido: a lista do que a infraestrutura responde e a
      verificação de conexão (`FR-1520`, `FR-1521`)
- [x] A indisponibilidade do Ollama não leva ao OpenRouter (`FR-1499`, US4 cenário 1, `SC-548`)
- [x] Nenhum truncamento silencioso: medida em tokens do modelo, ordem do excesso, conferência pela
      contagem do serviço (`FR-1479` a `FR-1483`, `D-003`, `SC-547`)
- [x] A fidelidade entre afirmação e fonte é avaliada por humanos, e a conferência não se apresenta
      como prova (`FR-1513`, `D-007`)
- [x] O isolamento dos workers foi examinado contra a arquitetura, sem presumir fila nem Redis
      (`D-008`)
- [x] O acompanhamento da candidatura está fora, e registrado na spec e no §9 da auditoria
- [x] A faixa de identificadores foi medida na `main`, nas worktrees, nas branches remotas e nos dois
      PRs abertos; a pasta `071` é a seguinte livre
- [x] Nenhuma decisão de outra spec foi alterada; as da `070` são citadas como "a decisão 010 da
      `070`" e "a decisão 011 da `070`"

## O pedido de 12/10/2026 → onde a spec o cumpre

| Ponto do pedido | Requisitos e decisões |
|---|---|
| Pergunta livre e de continuação, linguagem simples, referências verificáveis | US1, US2, `FR-1485` a `FR-1496` |
| As doze perguntas da `070` como referência, e não limite | `FR-1512`, `SC-554` |
| A fonte é a da `070`; sem PDF, sem banco editorial, sem acesso livre ao banco | `FR-1470`, `FR-1471`, `D-002` |
| Fora do escopo: público, situação individual, documentos, decisões, notificações, Ifes Ads, vetorial | *Fora do escopo*; `FR-1462`, `FR-1486`, `D-009` |
| Serviço por configuração, parte comum, adaptadores pequenos, nada de plataforma | `FR-1497`, `FR-1504`, `D-004` |
| Ollama fora do ar não manda ao OpenRouter | `FR-1499`, `SC-548` |
| Credenciais só no servidor | `FR-1502`, `SC-549` |
| Modelo e L4 confirmados, e não presumidos | *Dependências*; `FR-1520`, `FR-1521` |
| Conteúdo completo primeiro; seleção só com necessidade demonstrada | `FR-1472`, `FR-1478`, `D-009` |
| Tokens pelo tokenizer do modelo; contexto efetivo, e não nominal; nada de corte silencioso | `FR-1479` a `FR-1483`, `D-003` |
| Conversa vinculada a uma seleção; versão a cada pergunta; aviso de mudança; histórico sem regra superada | `FR-1465` a `FR-1468`, `FR-1494`, `FR-1495`, `D-006` |
| Explicação, dado e citação literal distinguidos; referências validadas contra as fontes fornecidas | `FR-1485`, `FR-1487`, `FR-1489`, `UX-213` |
| Ausência, ambiguidade, conflito, anexo | `FR-1486`, US3 |
| Conteúdo recuperado é dado, e não instrução | `FR-1477`, `CA-25` |
| Fidelidade entre afirmação e fonte; prompt e temperatura não garantem | `FR-1513`, `D-007` |
| Interface interna existente, restrição no servidor, piloto visível, estados | `FR-1460`, `FR-1461`, `UX-210` a `UX-216` |
| Limite de uso, orçamento, concorrência, sem retentativa | `FR-1505` a `FR-1507`, `SC-560` |
| A forma mais simples de não esgotar os workers | `FR-1500`, `FR-1506`, `D-008`, `SC-557` |
| OpenRouter só com conteúdo público e perguntas sintéticas | `FR-1503`, `UX-211`, `D-005` |
| Registrar só o necessário, sem segredo nem conteúdo pessoal | `FR-1508` a `FR-1510`; DP-2 |
| Matriz da auditoria e da `070` ampliada, com as categorias pedidas | `FR-1512` (`CB-01` a `CB-16`) |
| Três resultados separados; modelo, serviço, parâmetros e versão da fonte por rodada | `FR-1510`, `FR-1511`, `FR-1515` |
| OpenRouter não aprova Ollama; latência, memória e concorrência na L4 | `FR-1516`, `FR-1517`, `SC-555` a `SC-558` |
| Conexão mínima com o Ollama | `FR-1520`, US7 |
| Critérios de conclusão; dependências e decisões pendentes | *Critérios de conclusão do piloto*; *Dependências*; *Decisões pendentes* |
| Acompanhamento da candidatura como evolução posterior | *Fases posteriores*; §9 da auditoria |
| 13º — sessões acompanhadas na máquina da equipe; orientação aos participantes | `FR-1463`, `SC-559`, `D-012` |
| 14º — registro sem identidade, mascaramento simples, exclusão em 90 dias; não é anonimização | `FR-1509`, *Proteção de dados*, `D-013` |
| 15º — controles de acesso existentes; só os metadados de modelo, configuração, fonte e prompt | `FR-1461`, `FR-1510`, `D-001` |
| 16º — sem plataforma de anonimização, painel de conversas, camada de provedores nem serviço novo | `FR-1461`, `FR-1504`, `FR-1509`, `D-004`, `D-008`, `D-013` |

## Notes

- **Validação em duas iterações.** Na primeira, só os dois marcadores de clarificação ficaram
  abertos; o usuário os decidiu em 12/10, e a segunda passou inteira.
- **Nomes de serviço não são escolha técnica da spec.** OpenRouter, Ollama, a L4, "tokens" e
  "tokenizer" vêm do pedido do usuário, como restrição institucional — a Constituição admite na spec a
  restrição institucional permanente. Os nomes de campo das APIs ficam fora dos requisitos, em
  *Assumptions*, como insumo a reconferir no plano.
- **Termos de arquitetura só como exame ou exclusão.** "Fila", "Redis", "worker", "processo" e
  "travas consultivas" aparecem no `D-008`, que registra o exame que o pedido exigiu, e na exclusão de
  escopo. O `FR-1506` exige o teto em termos de comportamento.
- **Os SC de qualidade dependem da DP-3.** Os limiares são os da auditoria, como proposta; o de 10% do
  `SC-557` é proposta desta spec.
- **Para o plano decidir, sem mudar o que a spec exige:**
  - como montar as fontes completas a partir da leitura da `070` sem duplicá-la (`FR-1470`,
    `FR-1472`), e como estender a cobertura (`FR-1473`);
  - o tokenizer, e se ele pede dependência nova (`FR-1479`);
  - a forma estruturada em cada serviço, e a tolerância da contagem (`FR-1482`, `FR-1485`);
  - a normalização de números, datas e contatos da conferência (`FR-1487`);
  - onde a conversa vive no servidor (`FR-1494`);
  - o teto, os limites e os orçamentos por configuração (`FR-1506`, `FR-1507`);
  - o formato do relatório das rodadas e das medições (`FR-1510`, `FR-1518`).
- **Verificado nesta rodada.** `tests/test_citacoes_de_requisito.py` e
  `tests/test_readme_acompanha_o_codigo.py` — resultado no relatório da sessão.
- **Plano de 12/10/2026.** `plan.md`, `research.md` (R-001 a R-021), `data-model.md`, `contracts/` e
  `quickstart.md`. `tasks.md` com 67 tarefas.
- **Análise de consistência de 12/10/2026, primeira rodada.** Aplicados, por decisão do usuário: I1 (a
  Retificação futura como fonte calculada à parte, `FR-1472`, `FR-1475`), I2 (a) (sem tokens, tempo e
  custo por troca no `rodada.json`; totais no resumo), I3 (a) (orçamento diário só da tela; a avaliação
  pelo `--max-chamadas` e pelo total da DP-4; sem valor, nenhuma chamada externa, `FR-1507`); e os
  MEDIUM U1, U2, G1, G2, G3, D1, T1, T2, S1, G4, G5. **A I4 ficou como decisão pendente, a DP-7**, com a
  emenda do `FR-1521` proposta e não aplicada. Segunda rodada da análise sem CRITICAL nem HIGH; N1, N4 e N5 aplicados, e a DP-7 decidida pela opção
  (b), com o `FR-1521` emendado. Próximo passo: `/speckit-implement`.
