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

## Efeito na Retificação (não persistido) — P2

O mesmo efeito, com o que a Retificação precisa: em vez do valor a gravar, as **Alterações** que ele
produz no destino.

| Campo | Tipo | Regra |
|---|---|---|
| `perfil`, `codigo`, `denominacao`, `efeito`, `motivo` | como acima | `FORA` nomeia o campo quando é o contrato que recusa (`FR-939`) |
| `alteracoes` | lista de `{targetPath, operation, newValue}` | só das espécies que existem (`FR-938`, R-012) |
| `mudancas` | lista de `(coleção, campo, antes, depois)` | o que a conferência diz, com os rótulos da tela |
| `impressao` | SHA-256 das Alterações | o que a assinatura cobre e o registro guarda |

O registro do gesto confirmado na Retificação é uma linha `APLICAR_A_TODOS` com o agregado
Retificação e `detalhe.etapa = "retificacao"` (R-016).

## Transições

Nenhuma. O Edital continua em elaboração antes e depois do gesto; o gesto é uma gravação de rascunho.
Na Retificação, o gesto não cria estado: sai no ato de Retificação em elaboração, e só a publicação
dele muda o conteúdo vigente.
