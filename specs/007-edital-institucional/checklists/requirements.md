# Specification Quality Checklist: Edital Institucional

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
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

## Notas de validação

**Sobre referências a arquivo e linha.** A spec cita caminhos do repositório dentro de blocos de
racional em itálico. Não são decisão de implementação: são a evidência de que o defeito descrito
existe e onde foi verificado, no mesmo padrão da `006`. A decisão de *como* corrigir permanece com
o `/plan` — e as "Instruções para o `/plan`" declaram limites, não desenho.

**Sobre `SCHEMA_VERSION` (FR-017).** É vocabulário de domínio consolidado do produto, presente na
Constituição e nas specs `005` e `006`, não escolha tecnológica desta feature.

**Sobre a ausência de `[NEEDS CLARIFICATION]`.** As três decisões que seriam candidatas foram
fechadas na entrada da feature e estão declaradas: a precondição de implantação dispensa
retrocompatibilidade; a fronteira canônica define onde vive a formatação humana; o catálogo de
seções permanece fixo. As demais lacunas foram resolvidas por decisão registrada em `Assumptions`
— texto descritivo para os campos do Perfil (FR-013) e origem da lista de autoridades (FR-039).

**Trava de escopo declarada.** A seção `Rastreabilidade com a auditoria` fecha o conjunto: dezesseis
achados abertos, dezesseis requisitos, nenhum a mais. Um achado novo descoberto durante a
implementação registra-se; não se corrige aqui (P-001).

**Item acrescentado além da lista de entrada.** O achado 17 — a confirmação de ato exibindo a chave
interna (`Ato registrado: submeter`) — não constava da enumeração de escopo recebida. Entrou como
FR-041 por ser da mesma classe que FR-002 (forma interna vazando para o usuário), por ser o último
resíduo pendente do pacote que a `006.1` começou, e por custar um mapa de rótulos que já existe na
trilha de auditoria. É o único acréscimo, e é destacável sem afetar nenhum outro requisito.
