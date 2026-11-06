# Data Model: A convocação segue o canal

**Nenhuma tabela, coluna ou migration** (FR-4006). O que esta feature acrescenta é derivado do que já
está gravado.

## Convocação (`019`) — propriedade derivada

| Propriedade | Origem | Regra |
|---|---|---|
| `visivel_ao_candidato` | comunicações da convocação e da cadeia (`convocacao_anterior`), forma citada (`versao.content.profiles[].callForm`) | FR-3981 com a D-001: visível se a forma citada não é a publicação, ou se alguma convocação da cadeia tem comunicação com `resultado="ENVIADA"` e `enviado_em` |
| `forma_lida` (em memória) | `forma_declarada`, só para as sem comunicação | lida uma vez por conjunto (R-002), reusada pelo vocabulário |

**Transição relevante:** o registro da publicação (`ComunicacaoEmitida` com `forma="PUBLICATION"`)
leva a convocação de invisível a visível. Nenhum outro ato faz isso, e nenhum a torna invisível de
novo.

| Situação | Forma citada | Cadeia comunicada | Visível |
|---|---|---|---|
| K-msg (falha de envio) | mensagem | não | **sim** (como hoje) |
| Mensagem enviada | mensagem | sim | sim |
| K-pub | publicação | não | **não** |
| Publicação registrada | publicação | sim | sim |
| Correção de publicada, aguardando a própria | publicação | sim (a anterior) | **sim** (D-001) |
| Forma não declarada | nenhuma | não | sim (como hoje) |
| K-pub com desfecho | publicação | não | **não** (D-002) |

## Comunicação emitida (`019`) — leitura nova

`comunicacao_de(convocacao)` devolve `(forma, instante, referencia)` da última comunicação
bem-sucedida, ou a forma lida sem instante. `envio_de` continua sendo a fonte do prazo.

## Prévia do texto (gestão) — não é registro

Viaja nos campos do formulário da etapa de conferência, e nada se grava:

| Campo | Conteúdo |
|---|---|
| `etapa` | `conferir` → `confirmar` |
| `texto_conferido` | resumo do texto composto mostrado na prévia |
| `alcance`, `chave`, `lista`, escolhas | os mesmos de hoje, repassados |

Na confirmação, o texto é recomposto. Divergindo do resumo, a confirmação recusa e mostra a prévia nova.
