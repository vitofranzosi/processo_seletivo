# Data Model: Sorteio viável desde a publicação

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

**Nenhuma tabela, coluna, migration nem linha append-only nova.** O que esta feature acrescenta são
declarações no código e valores derivados que não se gravam. O `M` das tabelas protegidas que o
`provisionar` informa continua 41.

## Granularidade da fonte (declarada no código)

| Fonte publicada | Adaptador | Publica só a data | Onde existe |
|---|---|---|---|
| `Loteria Federal` | `LoteriaFederal` | sim | todo ambiente |
| `Fonte de demonstração` | `FonteDeTeste` | não | só com `SORTEIO_FONTE_DE_DEMONSTRACAO` |
| `Fonte de demonstração (só a data)` | `FonteDeTesteSoData` (nova) | sim | só com `SORTEIO_FONTE_DE_DEMONSTRACAO` |

- Atributo de classe do adaptador, lido sem instanciá-lo (R-001).
- Invariante, verificada por teste (FR-2649): o adaptador que diz publicar só a data devolve
  `ocorrida_nao_antes_de` à meia-noite, no fuso institucional; o que diz publicar a hora devolve o
  instante que a fonte informou.

## Limite previsto da ocorrência (derivado, não gravado)

Entradas: `drawMethod/occurrenceAt` (RFC 3339 com fuso, já validado pela forma) e a granularidade da
fonte declarada em `drawMethod/source`.

| Granularidade | Limite previsto |
|---|---|
| só a data | 00h00 em `America/Sao_Paulo` do dia de `occurrenceAt` convertido para esse fuso |
| data e hora | nenhum: a regra não se aplica (D-006) |

## Inviabilidade (derivada, não gravada)

`inviável ⇔ limite previsto ≤ congelamento mais cedo`

| Onde se pergunta | Congelamento mais cedo | Método conferido | Efeito |
|---|---|---|---|
| Publicação do Edital | fim do período de inscrições da versão conferida (R-003) | comum do Edital e próprio de cada marco | achado impeditivo |
| Retificação | o mesmo, na versão que vai vigorar | os mesmos, menos os marcos já sorteados em todos os recortes (R-005) | advertência |
| Tela do sorteio, recorte não congelado | o instante em que a tela é montada | o vigente, que a relação comprometeria | aviso, e o botão continua |
| Tela do sorteio, recorte congelado | `publicada_em` da relação | o da versão que a relação cita | diagnóstico e saída em três passos |
| Recusa `occurrence_precedes_freeze` | `publicada_em` da relação (comparação inalterada, FR-2664) | o comprometido | frases acrescentadas à mensagem |

## Códigos novos

| Código | Severidade | Ato | Caminho |
|---|---|---|---|
| `draw_occurrence_not_after_registration` | impeditivo | publicação | `/drawMethod` ou `/profiles/id=…/classificationMilestones/id=…/drawMethod` |
| `draw_occurrence_not_after_registration_on_retification` | advertência | Retificação | o mesmo |

O código da Retificação é diferente de propósito (R-004).
