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

Verificação cruzada de `spec.md`, `plan.md` e `tasks.md`, executada sobre os arquivos.

| Verificação | Resultado |
| --- | --- |
| Requisitos funcionais | 32 |
| Critérios de sucesso | 7 |
| Histórias de usuário | 7 |
| Requisitos sem tarefa correspondente | nenhum |
| Tarefas citando requisito inexistente | nenhuma |
| Requisitos duplicados ou renumerados | nenhum |
| Tarefas | 58 — 27 concluídas, 31 abertas |
| Requisitos com alguma implementação | 22 |
| Requisitos inteiramente abertos | 10 — FR-019 a FR-028 |

A numeração é contínua e não desloca em fases posteriores; cada tarefa concluída registra o commit
em que foi implementada, para que a reconstrução retroativa da lista seja auditável em vez de
declarativa.

### Conferência das lacunas declaradas

Os requisitos declarados abertos foram verificados no código, e não apenas assumidos:

- **FR-019** — as triggers existentes cobrem `auditoria`, `publicacao`, `documento_publicado` e
  `versao_consolidada`; não há script versionado de `GRANT` para os papéis.
- **FR-020** — `targetPath` e `expectedPreviousHash` são `CharField` sem `max_length` em
  `publicacoes/api/serializers.py`; o excesso chega às colunas menores do banco.
- **FR-021** — `public_views.py` usa `parse_datetime` e aceita instante sem fuso, sem
  `is_naive`.
- **FR-022** — `rascunho.js` remove o rascunho por comparação de conteúdo, nunca por prazo.
- **FR-023** — `Retificacao`, `AlteracaoNormativa`, `AtoAdministrativo` e `RevisaoEdital` não têm
  trigger de imutabilidade.

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
