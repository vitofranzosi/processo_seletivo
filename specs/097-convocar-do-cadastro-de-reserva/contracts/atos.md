# Contrato: os atos do acréscimo

**Feature**: [spec.md](../spec.md) · **Modelo**: [data-model.md](../data-model.md)

Dois comandos e uma leitura em `ocupacao/application/acrescimo.py`. Os dois comandos rodam em
`comando_de_comissao` (`T-007`): transação, Processo travado, autoridade da comissão, idempotência pela
chave.

## `previa_do_acrescimo(edital, perfil_id, marco_id, lista_id, quantidade, at)`

Leitura pura, sem gravar nada (`FR-2456`). Devolve:

| Chave | O que é |
|---|---|
| `apuracao` | a vigente, ou `None` |
| `acrescimos` | os do recorte, cada um com espécie, quantidade, origem, fundamento, referência, autor, instante, e o que resta dele (só acréscimo) |
| `publicadas`, `acrescidasLiquidas`, `efetivasDepois` | as vagas publicadas, o saldo atual dos acréscimos, e as efetivas depois do ato |
| `alcancados` | as pessoas que a ordem vigente alcança para as vagas efetivas depois do ato, na ordem — `{id, nome, posicao}` |
| `faltamPessoas` | quantas vagas ficariam sem pessoa na ordem alcançada (`0` no caso comum) |
| `emissao` | `"emitida_pelo_ato"` ou, com outra causa de obsolescência presente, `{codigo, causas}` |
| `assinatura` | `canonical_sha256` de `(apuracao_id, ids dos acréscimos, quantidade)` |

## `acrescentar_vagas(...)`

| Argumento | Regra |
|---|---|
| `actor`, `processo_id`, `edital_id`, `perfil_id`, `marco_id`, `lista_id` | o recorte |
| `quantidade` | inteiro `>= 1` |
| `origem`, `fundamento` | texto não vazio depois de `strip()` |
| `referencia` | opcional |
| `leitura_confirmada` | a `assinatura` da prévia |
| `idempotency_key`, `correlation_id` | |

**Ordem das recusas** — a mais específica primeiro:

| Código | Status | Quando | Requisito |
|---|---|---|---|
| `quantidade_invalida` | 422 | não inteiro, ou `< 1` | `FR-2450` |
| `origem_obrigatoria` | 422 | origem vazia | `FR-2451` |
| `fundamento_obrigatorio` | 422 | fundamento vazio | `FR-2451` |
| `acrescimo_sem_cadastro_de_reserva` | 409 | o Perfil, na versão vigente, tem `reserveType` fora de `LIMITED`/`UNLIMITED` | `FR-2463` |
| `acrescimo_fora_da_linha_geral` | 409 | o quadro tem linha de Modalidade, o Perfil declara reversão, ou o recorte não lê a linha geral | `FR-2464` |
| `ordem_nao_vigente` | 409 | o recorte não tem ordem vigente | `FR-2459` |
| `sem_quadro_publicado` | 409 | o recorte não tem linha no quadro | `FR-2459` |
| `leitura_do_recorte_mudou` | 409 | a assinatura recalculada sob a trava difere da confirmada | `FR-2457` |
| `idempotency_conflict` | 409 | a mesma chave com outro conteúdo | `FR-2458` |

**Efeito**: grava um `AcrescimoDeVagas` `ACRESCIMO`. Se as causas de obsolescência da apuração vigente,
depois da gravação, forem só `acrescimo_posterior` — ou se não houver apuração —, emite a apuração
seguinte num *savepoint*, com o autor do ato e o motivo *"Vaga acrescida: N, origem …"*. A recusa da
emissão não desfaz o acréscimo (`T-004`).

**Declarado** (o que volta à tela e à repetição idempotente):

```json
{
  "acrescimo": "<uuid>",
  "quantidade": 1,
  "apuracaoSeguinte": {"apuracao": "<uuid>", "efetivas": 1, "ocupadas": 1, "faltando": 0},
  "apuracaoPendente": null
}
```

Com outra causa presente, `apuracaoSeguinte` é `null` e `apuracaoPendente` é `{codigo, detalhe}` —
`outra_causa_de_obsolescencia`, ou o código da recusa da emissão.

**Trilha**: `OCUPACAO_ACRESCENTAR_VAGAS`, agregado o acréscimo, razão com recorte, quantidade,
origem, apuração anterior e seguinte. A apuração emitida tem a própria linha, `OCUPACAO_APURAR`, como
na emissão pela tela.

## `desfazer_acrescimo(...)`

| Argumento | Regra |
|---|---|
| `actor`, `processo_id`, `edital_id`, `acrescimo_id` | o acréscimo a desfazer; o recorte vem dele |
| `quantidade` | inteiro `>= 1` |
| `motivo` | texto não vazio |
| `pessoas_chamadas` | função `(edital, perfil_id, marco_id, lista_id, at) -> int`, avaliada sob a trava (`T-005`) |
| `leitura_confirmada`, `idempotency_key`, `correlation_id` | |

| Código | Status | Quando | Requisito |
|---|---|---|---|
| `quantidade_invalida` | 422 | | `FR-2460` |
| `motivo_obrigatorio` | 422 | | `FR-2460` |
| `acrescimo_inexistente` | 404 | o id não é `ACRESCIMO` deste Edital | `FR-2460` |
| `desfazimento_alem_do_acrescimo` | 409 | quantidade maior que o que resta do acréscimo | `FR-2462` |
| `desfazimento_com_pessoas_chamadas` | 409 | `efetivas − quantidade < pessoas_chamadas(...)` | `FR-2462` |
| `leitura_do_recorte_mudou` | 409 | | `FR-2457` |

**Efeito**, **declarado** e **trilha** como no acréscimo, com `OCUPACAO_DESFAZER_ACRESCIMO`.

## `pessoas_chamadas(...)` (nova, `convocacao/application/selectors.py`)

O número de inscrições do recorte com convocação vigente **em aberto** ou **atendida** — os conjuntos
`emAberto` e `servidos` de `_situacoes`. Quem encerrou (indeferimento, desistência, não atendimento,
inércia) e o reclassificado não contam: nenhum deles espera a vaga.
