# Data model — 051

Nenhuma entidade normativa nova e nenhum campo novo no conteúdo publicado. O que existe:

## Efeito (não persistido)

A prévia. Calculado a cada envio, nunca gravado.

| Campo | Tipo | Regra |
|---|---|---|
| `perfil` | identidade do Perfil destino | um por Perfil do Edital, exceto a origem |
| `codigo`, `denominacao` | texto | para a tela |
| `efeito` | `NASCE` · `SUBSTITUI` · `SEM_MUDANCA` · `FORA` | exatamente um (`FR-916`) |
| `motivo` | texto | só em `FORA` |
| `mudancas` | lista de `(rótulo, antes, depois)` | só em `SUBSTITUI`; rótulos da Revisão (`UX-112`) |
| `quantidade_fixa` | `(antes, depois)` ou nulo | quando a unidade traz corte de quantidade fixa (`FR-917`) |
| `valor` | a unidade como será gravada no destino | identidades do destino (marco existente) ou novas (nasce) |
| `impressao` | SHA-256 da unidade normalizada | o que o registro guarda (`FR-935`) |

## Unidades

| Unidade | Chave de correspondência | O que entra | O que nunca entra |
|---|---|---|---|
| Marco | *"o marco do Perfil"*: 0 → nasce, 1 → substitui, ≥2 → fora | forma da ordem, Etapas, combinação, normalização, arredondamento, janela, corte, critérios | `id`, `code`, `name`; método próprio (marco com ele fica fora) |
| Critérios | a lista do marco | a lista inteira, com o fato achado por código e tipo | — |
| Modalidade | código | denominação, descrição, regra (fundamento, versão, percentual, arredondamento) e a declaração da ampla | `id`, `code`, a linha do quadro, as demais Modalidades |
| Forma de convocação | o Perfil | `callForm` | — |
| Reversão | o Perfil com lista reservada | `vacancyReversion` | Perfil sem lista reservada fica fora |

## `RegistroAuditoria.detalhe` (coluna nova, JSON, nula)

Só preenchida em `operation = "APLICAR_A_TODOS"`. Ver [contrato](contracts/registro-do-gesto.md).

## `normativeRule.rounding` (campo existente, forma nova lida)

`{"mode": "PARA_CIMA" | "MEIO_PARA_CIMA" | "PARA_BAIXO"}` ou `{}`. Qualquer outra forma é preservada e
lida como *"declarado fora da lista"*. Não retificável, como o contrato já diz.

## Transições

Nenhuma. O Edital continua em elaboração antes e depois do gesto; o gesto é uma gravação de rascunho.
