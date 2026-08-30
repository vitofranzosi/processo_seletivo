# Specification Quality Checklist: Integridade Normativa e Prontidão para Produção

**Purpose**: Validate specification completeness and quality before proceeding to planning

**Created**: 2026-08-29

**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## Análise de consistência entre artefatos

Verificação cruzada de `spec.md`, `plan.md` e `tasks.md`, executada sobre os arquivos após a
revisão de fechamento.

| Verificação | Resultado |
| --- | --- |
| Requisitos funcionais | 34 |
| Critérios de sucesso | 7 |
| Histórias de usuário | 7 |
| Requisitos sem tarefa correspondente | nenhum |
| Tarefas citando requisito inexistente | nenhuma |
| Requisitos duplicados ou renumerados | nenhum |
| Tarefas | 71 — todas concluídas |
| Tarefas sem rastro | nenhuma; T070 e T071 são marcadas `[rito]` por tratarem dos artefatos, não do produto |
| Artefatos de Fase 0 e 1 | `research.md`, `data-model.md` e `quickstart.md` presentes |

A numeração é contínua e não desloca em fases posteriores; cada tarefa concluída registra o commit
ou a evidência correspondente, para que a reconstrução retroativa da lista seja auditável em vez de
declarativa.

### Conferência das lacunas, refeita

Todas as lacunas declaradas na primeira análise foram fechadas, e cada uma foi conferida no código
em vez de assumida:

- **FR-019** — `seguranca/papeis.py` e `manage.py provisionar_papeis`, verificados contra banco
  criado do zero: provisionar, migrar como o papel de migração, provisionar de novo, `6 de 6`.
- **FR-020** — limites no `ChangeSerializer` e, na tela de criação, derivados de
  `_meta.get_field(...).max_length`.
- **FR-021** — `public_views._instant` recusa instante sem fuso, e o `openapi.yaml` documenta o
  deslocamento obrigatório.
- **FR-022** e **FR-026** — verificados executando os scripts em `node --test`, não por busca de
  texto no fonte.
- **FR-023** — quatro triggers novas, condicionais ou absolutas conforme a tabela.
- **FR-025**, **FR-027**, **FR-028** — implementados; a pendência sem onde ser corrigida deixou de
  oferecer caminho.

### O que a revisão de fechamento encontrou

Dois requisitos estavam marcados como concluídos e não funcionavam em banco novo:

- **FR-019** falhava com `relation "auditoria_registroauditoria" does not exist` porque o `REVOKE`
  nominal pressupunha tabelas que só existem depois das migrations. O teste de conformidade não
  pegou porque rodava contra o banco de teste, que já tinha as tabelas — verificava a política,
  nunca a ordem de implantação.
- **SC-006** foi lido por arredondamento: 88,564% aparecia como "89%". A régua passou a exigir três
  casas e as duas execuções.

Além disso, um teste escrito para fechar a cobertura descobriu que o `seed_demo` estava quebrado
desde o commit `41e8173` — caminho documentado no README, a 0% de cobertura, e ninguém percebeu.

## Notes

### Divergências resolvidas durante a especificação

- **A primeira contenção era parcial e a revisão provou.** A precondição por hash de conteúdo
  protege o valor, não a identidade da entidade: dois Perfis de denominação idêntica tornam o hash
  indistinguível depois do deslocamento de índice, e `ADD` posicional não tem valor anterior a
  comparar. A especificação ganhou FR-002a e FR-002b, e SC-002 passou a exigir explicitamente esses
  dois cenários.
- **O backfill não era dispensável.** A suposição original — "reenviar o rascunho regulariza" — não
  vale para Retificação já homologada, que precisaria ser devolvida antes. A precondição é função
  determinística da base declarada, então há backfill exato. FR-002c.
- **Âncora não supre hash.** Aceitar `REPLACE`/`REMOVE` só por ter âncora deixaria passar a
  sobrescrita silenciosa de outra Retificação que alterou o mesmo campo da mesma entidade. As duas
  peças respondem a perguntas diferentes e as duas são exigidas. FR-002c.
- **A barreira de produção foi descrita além do que faz.** README e spec afirmavam que não havia
  valor admissível para `API_AUTHENTICATION_CLASSES` enquanto a autenticação institucional não
  existisse. Há vários. FR-017 passou a dizer o alcance real e a proibir a afirmação inversa.

### Exceção constitucional registrada

O fluxo constitucional exige especificação e plano antes de implementação substancial, salvo
correção emergencial justificada. As fases 1 a 3 invocaram essa cláusula: um dos defeitos publicava,
sem erro nem aviso, alteração normativa que nenhuma autoridade homologou. A especificação foi
escrita junto da correção, não depois, e cada defeito tem teste de regressão que falha no código
anterior. O desvio está em `plan.md`, Complexity Tracking.

### Conformidade constitucional pendente

O princípio I exige identificadores estáveis, e o endereçamento normativo por índice não honra
isso. Esta feature contém o dano; não o elimina. A conformidade plena depende de
`004-enderecamento-normativo-estavel`, que altera modelo de dados, contrato público e exige
migração de Retificações existentes — razão pela qual não cabe aqui.
