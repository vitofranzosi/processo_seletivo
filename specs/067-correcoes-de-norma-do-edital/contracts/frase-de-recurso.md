# Contrato — a frase de recurso do marco (`FR-1300` a `FR-1304`, `D-001`, `D-005`)

Uma função compõe a frase; o documento publicado, a prévia, o consolidado de Retificação e a Revisão
a leem.

## Entrada

O marco do conteúdo canônico: `name`, `code` e `appealWindow` (`admits`, `durationDays`, `unit`).

## Saída

| `appealWindow` | Nome resolvido | Frase |
|---|---|---|
| ausente, não objeto, ou `admits` ausente/nulo | — | `""` (nenhuma linha) |
| `admits: false` | `N` | `Não caberá recurso contra o resultado de “N”.` |
| `admits: false` | nenhum | `Não caberá recurso contra o resultado deste marco.` |
| `admits: true`, `durationDays` inteiro > 0 | `N` | `Caberá recurso contra o resultado de “N”, no prazo de {prazo}, contados da divulgação desse resultado.` |
| `admits: true`, `durationDays` inteiro > 0 | nenhum | `Caberá recurso no prazo de {prazo}, contados da divulgação do resultado.` |
| `admits: true`, prazo ausente, zero, negativo ou booleano | — | `""` |

**Nome resolvido**: `name` sem espaços nas pontas; vazio → `code`; vazio → nenhum.

**`{prazo}`** — `prazo_do_recurso(marco)`, que o aviso de conferência também lê:

| `durationDays` | `{prazo}` |
|---|---|
| 1 | `1 (um) dia corrido` |
| 2 | `2 (dois) dias corridos` |
| número na tabela de extenso do compositor | `N (extenso) dias corridos` |
| fora da tabela (ex.: 11) | `11 dias corridos` |

As aspas são “ (U+201C) e ” (U+201D). O nome não é escapado nem normalizado além do que a `grafia`
já faz com todo texto do documento.

## No documento

O rótulo continua "Recurso:", na mesma posição do bloco do marco (depois do sorteio, antes do corte).

## Na Revisão (`D-012`)

A Revisão chama a mesma função com `objeto="deste marco"`: `Caberá recurso contra o resultado deste
marco, no prazo de {prazo}, contados da divulgação desse resultado.` / `Não caberá recurso contra o
resultado deste marco.` A denominação do marco é a linha imediatamente acima.
