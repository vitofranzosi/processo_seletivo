# Data Model: A habilitação do assistente

## `HabilitacaoDoAssistente` (nova, append-only)

Tabela `duvidas_habilitacao_do_assistente`.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro sequencial | a ordem dos atos (R-2) |
| `frente` | texto: `PILOTO` ou `PAGINA_PUBLICA` | — |
| `edital` | referência a `processos.Edital`, `PROTECT`, opcional | obrigatória com `PAGINA_PUBLICA`, e vazia com `PILOTO` (constraint de banco) |
| `habilitada` | booleano | `True` habilita, `False` desabilita |
| `motivo` | texto | não vazio depois de aparado (constraint de banco e FR-7528) |
| `autor` | texto | o `subject` da pessoa institucional; o nome se resolve como na trilha da `108` |
| `criado_em` | instante | o do `command_context` |

- **Índice**: `(frente, edital, id)`.
- **Gatilho**: `habilitacao_do_assistente_append_only`, `BEFORE UPDATE OR DELETE`. Entra em
  `TABELAS_APPEND_ONLY`, e o `M` do provisionamento sobe de 65 para 66 (FR-7527).
- **Exclusão**: nenhuma. Não há comando que apague atos.

### Estado

O estado de uma frente é o último ato dela: o do piloto, ou o da página pública daquele Edital.
Sem ato nenhum, a frente está desabilitada (negar por padrão).

```text
(nenhum ato) ──habilitar──▶ HABILITADA ──desabilitar──▶ DESABILITADA ──habilitar──▶ HABILITADA …
                               │  ▲                          │
                               └──┘ habilitar: recusado (nada muda)
```

## A regra de quem atende

É uma função só, lida a cada requisição (FR-7523).

| Frente | Atende quando |
|---|---|
| Piloto | (último ato habilitado **ou** `ASSISTENTE_PILOTO` fora de produção) **e** o alcance do Edital **e** a permissão `assistente:piloto` |
| Página pública | **não** `AMBIENTE_DE_PRODUCAO` **e** (último ato do Edital habilitado **ou** `ASSISTENTE_NA_PAGINA_DO_EDITAL`) **e** o Edital tem seleção pública agora |

A configuração completa não entra na regra (FR-7504). Ela é exigida no ato. Sem ela, a pergunta
livre termina no estado explícito de hoje, sem chamada.

## A marca da conversa (R-5)

A chave da conversa na sessão é `edital_id:marca`. A marca é o `id` do ato de habilitação vigente,
ou `demonstracao` com o atalho. Nenhuma coluna muda na `TrocaDoPiloto`.

## Os requisitos da abertura

`RA-1` a `RA-12` são uma constante em `duvidas/domain/nomes.py`, com o rótulo e a espécie de cada
um, usada pela página e pela recusa de produção (FR-7533). Não são gravados.

## O evento na trilha

São duas operações: `HABILITAR_ASSISTENTE` e `DESABILITAR_ASSISTENTE`. O evento leva a permissão
`assistente:habilitar`, o motivo, o estado anterior e o posterior, e no detalhe a frente e o Edital.
O escopo é o institucional para o piloto e o da unidade do Edital para a página pública (R-8).
