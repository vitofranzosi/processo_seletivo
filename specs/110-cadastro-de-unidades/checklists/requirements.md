# Specification Quality Checklist: Cadastro de unidades administrado pela aplicação

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-31
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

- **Nomes técnicos que ficam na spec, de propósito.** `unidades.json`, `ps-migrar`, a permissão
  `unidade:administrar` e o PostgreSQL aparecem porque são decisões de produto do pedido de 31/10
  (o banco como fonte oficial, o nome da permissão) ou nomes operacionais que a equipe usa — não
  escolhas de implementação. Como a `107`, a spec não diz tabela, gatilho, view nem framework; o
  "banco recusa" da FR-3333 é a garantia exigida, e o gatilho é do plano.
- **Nenhum marcador de esclarecimento.** As oito decisões do pedido cobrem escopo, autorização e
  segurança. O que continua aberto é decisão de produto que não bloqueia esta feature — P-1 a P-6,
  §Pendências de produto —, com o comportamento provisório dito.
- **Casos-limite são requisitos.** Os dezoito `EC-` têm linha própria na matriz de rastreabilidade,
  porque nenhuma ferramenta os cobra pelo identificador.
- **Contradição não se detecta por checklist.** Conferido à mão: FR-3302 (semente só em registro
  vazio) e FR-3305 (modelos iniciais garantidos) não se contradizem — a semente sempre garante os
  modelos, e só o registro de unidade depende do registro vazio. FR-3309 (toda leitura exige a
  permissão) e a trilha da unidade, que o auditor da unidade lê sem ela, também não: a trilha é da
  `108`, e esta feature só grava o que ela lê.
- Validação: uma iteração; todos os itens passam.
- **Revisão independente (31/10)**, por um revisor que não escreveu os artefatos, contra o código e o
  pedido. Achados acolhidos: a tela não existe sem entrada institucional (D-017); a `108` não rotula
  o canal (D-009); os modelos iniciais gravariam a implantação como autora (D-006); a semente de
  registro vazio não se testava com a fixture `autouse` (T010); mais três citações da sincronização
  (D-003); o formato da exportação (D-016); leituras na aplicação (D-006); ordem da recusa como na
  `107`; a FR-3330 em três situações; a sigla e a linha longa na prévia (D-010); os gatilhos em
  `TRIGGERS_POR_APP`; versão em desativar e reativar (D-007); savepoint no cadastro concorrente; a
  ampliação silenciosa do papel (P-5). Nenhum ficou de fora.
- **Revisão final (31/10)**, sobre a `main` com a `108` e a `109` integradas, a pedido do usuário,
  em cinco pontos. Homologação antes do SSO: o teste automatizado e a validação por pessoas
  separados; a validação usa um adaptador de homologação só no código de teste, recusado em
  produção por quatro camadas (D-017, D-018, US7, FR-3342, FR-3343, SC-1048). Permissão: papel
  institucional próprio, em vez de ampliar o de acessos — o deploy não muda privilégio de ninguém
  (D-002, FR-3308, FR-3310, FR-3339 a FR-3341); **revê a decisão de produto 3, confirmada pelo
  usuário no mesmo dia**. Comando: o nome anterior fica como apelido (D-003, EC-17). Ordem: três PRs, e a troca
  da fonte no mesmo PR que as telas (D-019). Integração: o rótulo do canal já veio com a integração
  das duas, e a tarefa que o acrescentaria saiu. Todos os itens continuam passando.
- **Comparação das estratégias de homologação (31/10)**, pedida pelo usuário antes do PR B: seletor
  de demonstração em homologação × provedor institucional de testes. Ficou o provedor, como
  subclasse do simulado da `106`, sem criptografia própria, num ambiente separado da VM de
  homologação, que não muda (D-017, D-018). A validação por pessoas é a T051, critério de aceite
  humano em seção própria, e não teste.
