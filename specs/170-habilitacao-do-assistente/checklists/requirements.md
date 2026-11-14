# Specification Quality Checklist: A habilitação do assistente do Edital pela interface

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-14 (revista no mesmo dia, com as respostas do usuário e o recorte da entrega)
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

## O recorte do usuário (revisão de 14/11)

Cada ponto do retorno do usuário aponta o requisito ou critério que o cumpre:

| Pedido | Onde |
|---|---|
| A entrega não termina numa tela de recusa: fora de produção, habilitar pela interface basta | FR-7508, FR-7518, FR-7520; SC-2451 |
| O percurso funciona sem `ASSISTENTE_PILOTO` nem a chave da `074` | FR-7508; SC-2451 |
| Passo 1 — a página diz se a configuração está completa | FR-7501, FR-7502; US1; SC-2450 |
| Passo 2 — habilitar o piloto ou um Edital, com motivo | FR-7514, FR-7517, FR-7528 |
| Passo 3 — quem tem permissão testa pela gestão | FR-7515; US2 |
| Passo 4 — visitante sem login no Edital habilitado; outro Edital sem o assistente | FR-7520; US3 |
| Passo 5 — desabilitar, e nenhuma pergunta nova chega ao modelo | FR-7523, FR-7524; US4 |
| Os requisitos não bloqueiam os testes fora de produção | FR-7518 |
| Produção continua fechando a abertura pública, conferida no backend, pela configuração existente | FR-7518, FR-7519; US5; SC-2453 |
| Os controles de acesso, a credencial e os limites de uso continuam | FR-7500, FR-7511, FR-7521 |
| Os doze requisitos ficam documentados e rastreáveis; o cadastro fica para depois | FR-7533; a tabela dos requisitos |
| A página não afirma disponibilidade e não chama o modelo | FR-7502; UX-810 |
| A exclusão do piloto preservada; a página pública fora de produção como na `074` | FR-7534, FR-7535 |
| A pergunta em curso termina; reabilitar começa conversa nova | FR-7524, FR-7525; SC-2456 |
| Q-3: as sessões acompanhadas ficam | FR-7516; D-008 |
| A demonstração: habilitar, conversar como visitante, desabilitar | SC-2457 |

## Casos-limite como requisitos

A seção *Edge Cases* não entra na matriz de `FR-` e `SC-`, e nenhuma ferramenta a cobra. Por isso
cada caso aponta o requisito que o governa:

| Caso-limite | Requisito |
|---|---|
| Habilitação sem configuração completa, por envio montado à mão | FR-7501, FR-7514, FR-7517 |
| Configuração retirada com uma frente habilitada, e a volta dela | FR-7504 |
| Configuração incompleta não derruba a inicialização | FR-7503 |
| Serviço externo em produção com o piloto desligado | FR-7505; SC-2453 |
| Banco de testes levado para produção com Editais habilitados | FR-7519; SC-2453 |
| Dois administradores ao mesmo tempo | FR-7531 |
| Ato que não muda nada | FR-7530 |
| Edital habilitado que perde a página pública | FR-7520 |
| Pergunta em curso no instante da desabilitação | FR-7524 |
| Chave de demonstração ligada e frente desabilitada | FR-7506, FR-7507 |
| Administrador revogado ou suspenso | FR-7511 |
| Unidade do Edital desativada | FR-7517 |
| Visitante que descarta o cookie | FR-7521 (o limite por visitante é o `RA-8`) |

## Notes

- Os nomes das variáveis `ASSISTENTE_*`, da permissão `assistente:habilitar` e dos pontos do código
  que leem as chaves aparecem na spec de propósito. O pedido mandou decidir o destino de cada
  variável e de cada recusa do `production.py`, e conferir no código cada ponto que lê as chaves. São
  o objeto da revisão, e não escolhas de implementação.
- As quatro perguntas foram respondidas pelo usuário em 14/11. Não há marcador de esclarecimento.
- O SC-2457 é critério humano: a demonstração com o serviço real, feita pela interface.
