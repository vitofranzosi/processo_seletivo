# Modelo — Fase 1

**Feature**: Contrato de mutabilidade normativa

**Nenhuma tabela nova, nenhuma migration.** O contrato é código: revisto em revisão de código e
versionado com ele (R-001). O que segue são as entidades conceituais e a forma que elas tomam.

---

## Entidades

### Campo publicado

Um campo escalar do conteúdo canônico de uma coleção normativa. Existe hoje; a feature não o cria.

| Atributo | Descrição |
|---|---|
| coleção | a coleção que o carrega — `profiles`, `schedule`, `classificationMilestones`… |
| nome | o último segmento do caminho normativo: `endAt`, `requirements`, `targetCount` |
| caminho | onde ele aparece no conteúdo: `/profiles/id=…/classificationMilestones/id=…/rounding/scale` |

**Identidade**: o par `(coleção, nome)`. É a mesma chave que o PR #113 estabeleceu para o rótulo
em português, e pela mesma razão: `name` existe em cinco coleções, `order` em três.

**Campo aninhado** — `cutRule/targetCount`, `normativeRule/percentage`, `appealWindow/unit` —
pertence à coleção da entidade que o carrega, e entra pelo último segmento. Não é coleção própria:
não tem identidade nem item.

---

### Natureza de mutabilidade

Atributo do **campo na forma publicada**, e não do valor num Edital específico. Partição total e
exclusiva: todo campo publicado tem exatamente uma.

| Natureza | Significado | Consequência verificável |
|---|---|---|
| **Retificável** | corrigível administrativamente depois da publicação | a tela de Retificação oferece caminho para ele (FR-304) |
| **Não retificável** | mudá-lo exige outro mecanismo | carrega razão normativa escrita (FR-299); a tela declara a exclusão (FR-312) |
| **Derivado** | muda como consequência de outro campo | não aparece na tela, e não precisa de razão própria |
| **Identidade / estrutural** | não pertence ao objeto de Retificação | idem |

**Transição**: reclassificar é decisão nova e escrita. Não alcança Edital publicado sob a
classificação anterior (FR-314). Não há estado intermediário: um campo nunca está "em revisão".

---

### Razão

O texto que sustenta uma natureza **não retificável**.

**Regra de validade**: normativa, e não técnica (D-002). Uma razão que descreva limitação de
implementação — "caixa de texto publicaria valor que o cálculo não interpreta" — não é aceita,
porque deixa de valer quando a limitação some e ninguém percebe. Uma razão que descreva norma —
"trocar o tipo do fato reinterpretaria valor já congelado" — continua valendo.

As três naturezas restantes não carregam razão: derivado e identidade se explicam pela própria
natureza, e retificável não precisa justificar-se.

---

### Contrato

O conjunto das classificações. Fonte única, lida pelo guardião e pela interface (FR-298).

```text
mutabilidade.py
└── CONTRATO: { (coleção, campo) → (natureza, razão) }
```

**Invariante**: o domínio do contrato é exatamente o conjunto de campos que a travessia do snapshot
encontra. Nem mais — declarar natureza para campo inexistente é a mesma omissão ao contrário
(FR-302) — nem menos (FR-301).

---

### Enumeração

Não é entidade persistida: é a leitura que produz o conjunto de campos publicados.

**Fonte**: travessia recursiva do conteúdo canônico de um Edital publicado a partir de
`rascunho_completo()`. É o que `test_toda_colecao_de_entidades_do_snapshot_esta_declarada` já faz
no nível raiz (R-002).

**Coleções que a travessia precisa alcançar** — doze, e é o mapa do trabalho da fase A:

| Nível | Coleção | Declarada em `COLECOES_PUBLICADAS`? | Esquema no `openapi.yaml`? |
|---|---|---|---|
| raiz | `profiles` | sim | `PerfilPublicado` |
| raiz | `schedule` | sim | `EventoPublicado` |
| raiz | `stages` | sim | `EtapaPublicada` |
| raiz | `sections` | sim | `SecaoPublicada` |
| raiz | `attachments` | sim | `AnexoPublicado` |
| raiz | `documentRequirements` | sim | `DocumentoExigidoPublicado` |
| raiz | *(campos soltos: `title`, `description`, `maxInscricoesPorCandidato`)* | — | — |
| sob `profiles` | `competitionModalities` | não | `ModalidadePublicada` |
| sob `profiles` | `vacancyTable` | não (mas há `LINHA_DO_QUADRO_PUBLICADA`) | `LinhaDoQuadroPublicada` |
| sob `profiles` | `declaredFacts` | não | **não** |
| sob `profiles` | `classificationMilestones` | não | **não** |
| sob o marco | `tiebreakers` | não | **não** |
| objetos aninhados | `cutRule`, `drawMethod`, `appealWindow`, `rounding`, `vacancyReversion`, `normativeRule` | não | parcial |

A coluna da direita é o registro de um limite, não uma tarefa desta feature (R-003).

---

## O que a interface passa a ler

`interface/retificacao.py` mantém as tuplas `CAMPOS_*` como **apresentação** — rótulo, tipo de
controle, opções —, e deixa de ser a fonte de **quais** campos existem. A pergunta "este campo é
retificável?" passa a ter uma resposta só, e ela vem do domínio.

O que isso corrige, concretamente: hoje um campo retificável que ninguém acrescentou à lista
simplesmente não existe para a tela, e nada acusa. Depois, o guardião acusa antes de a ausência
chegar a um Edital publicado.
