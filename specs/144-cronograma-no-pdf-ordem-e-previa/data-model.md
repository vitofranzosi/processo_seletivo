# Modelo de dados: O Cronograma — visibilidade no PDF (144)

Uma coluna, uma chave publicada, um campo de formulário. Nada mais muda de forma.

## `EventoCronograma` (editais)

| Campo | Tipo | Padrão | Novo? | Observação |
|---|---|---|---|---|
| `shown_in_pdf` | `BooleanField` | `True` | **sim** | Se a linha do Evento sai na tabela do Cronograma do PDF. Não é estado: o `status` e a fase continuam os de hoje (D-001). |

Migration `editais/0026_visibilidade_do_evento_no_pdf`: `AddField` com padrão verdadeiro. Todo Evento
existente fica exibido (SC-1580). A tabela não é append-only, e a migration não apaga nada.

Nenhuma constraint nova. O período de inscrições pode estar oculto (D-003), e a unicidade de `order`
continua a de hoje — a ordenação muda a sequência, e o servidor renumera 1..n como já faz.

## Conteúdo publicado — `schedule[]`

| Chave | Tipo | Presença | Ausência (versão ≤ 19) |
|---|---|---|---|
| `shownInPdf` | booleano | sempre presente, nunca `null` | `true` — degrau 20 (D-001) |

`SCHEMA_VERSION` 19 → 20. Mutabilidade: `retificavel()` (P-1).

## Formulário da etapa Cronograma

| Campo | Valores | Lido como |
|---|---|---|
| `evento-N-shownInPdf` (oculto) | `"true"` / `"false"` | `"false"` → oculto; qualquer outro, inclusive ausente → exibido |

A ordem continua em `evento-N-order`, reescrita pelo `ordenacao.js` a cada mutação da lista.

## API do rascunho

`EventSerializer.shownInPdf`: `BooleanField(required=False, default=True)`.
