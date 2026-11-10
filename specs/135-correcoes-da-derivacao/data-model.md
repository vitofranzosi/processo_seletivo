# Data Model: O andamento diz o que cada providência é (135)

**Nada é persistido.** Nenhuma migration, tabela, coluna, permissão ou estado (SC-1466). Os campos
abaixo são de leitura, em objetos que a derivação da `127` monta a cada requisição.

## Célula da publicação na condução do marco (`conducao_do_marco._celula_da_publicacao`)

| Campo | Antes | Depois |
|---|---|---|
| `estado`, `nota`, `url` | como hoje | como hoje |
| `natureza` | — | `"PRELIMINAR"`, `"DEFINITIVA"` ou `""`: a natureza da publicação vigente que o público lê nesta lista — a do ato vigente em *feito*, a da defasada mais recente em *obsoleto*, vazio sem publicação |

## `andamento.Celula`

| Campo | Tipo | Onde vale | Significado |
|---|---|---|---|
| `lista_vazia` | `bool` | ordem por pontuação | nenhuma inscrição concorre pela lista reservada, pelo critério da tela da ordenação (FR-4670) |
| `divulgado` | `str` | resultado | `NADA` (`"nada"`), `PRELIMINAR` (`"preliminar"`) ou `DEFINITIVO` (`"definitivo"`): o que o público lê hoje (FR-4677). Vazio nas outras células |

**Regras.**
- `lista_vazia` nunca muda a `situacao` (FR-4676). Com `lista_vazia`, a célula *Pendente* ou
  *Obsoleta* ganha a nota "lista em que ninguém concorre" e o ato com a frase da R-002.
- `divulgado` nunca muda a `situacao` (FR-4678): o preliminar continua *Pendente*, *Aguarda* ou
  *Impedido* conforme a aferição do definitivo (D-002).

## `providencias.Providencia`

| Campo | Tipo | Significado |
|---|---|---|
| `lista_vazia` | `bool` | copiado da célula (FR-4673); entra na chave do agrupamento (FR-4674) |

## O resumo do Perfil (`andamento.resumo_do_perfil`)

A última parte passa de "N providências em aberto" a "N providências em aberto nos marcos". A parte
do resultado é decidida por `divulgado` (R-003, R-006).
