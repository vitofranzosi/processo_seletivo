# Contrato: a preparação do universo classificável e a ordem com trajetória

Funções puras de `classificacao/domain`. Nenhuma toca banco, relógio ou modelo. É o contrato que o
caminho oficial e a prévia compartilham (D-004, D-011, FR-2230 a FR-2232).

## `universo_classificavel.preparar`

```text
preparar(marco, etapas, inscritos, *, recorte=None) -> (classificaveis, sem_posicao)
```

| Parâmetro | Forma |
|---|---|
| `marco` | o marco do conteúdo canônico (`stages`, `operation`, `normalization`, `rounding`, `tiebreakers`) |
| `etapas` | `{etapa_id: etapa}` do conteúdo, com `weight`, `forma`, `order`, `name` |
| `inscritos` | lista de `{inscricao_id, protocolo, nome, identity_subject, modalidade_id, pontuacoes, fatos, resultados}` — `resultados` com `etapa_id`, `pontuacao`, `consequencia`, `motivo`; a lista vem **na ordem que o chamador deu**, e a função a preserva |
| `recorte` | `None` (ampla, universo inteiro) ou id de Modalidade; filtra por `modalidade_id` |

**Comportamento** — o laço de `calcular_ordem` de hoje, sem mudança:

1. Fora do recorte → ignorado.
2. Eliminação mais recente entre os Resultados (pela `order` da Etapa) → `sem_posicao`, com a
   `consequencia` e o `motivo` daquele Resultado.
3. `combinar(marco, etapas, pontuacoes)` devolve `SEM_PONTUACAO` → `sem_posicao`, com o motivo que nomeia
   as Etapas sem nota.
4. Senão → `classificaveis`, com `pontuacao`, `consequencia="HABILITADA"`, `motivo=""`.

**Levanta** `RegraIncompleta` quando `combinar` levanta — sem captura: o caminho oficial já a deixa subir.

**Garantias** (testes da T003 e da T004):

- `calcular_ordem` antes e depois da extração devolve `posicoes`, `sem_posicao` e `universo` iguais, campo
  a campo, sobre os mesmos dados.
- `preparar(..., recorte=r)` sobre inscritos já filtrados por `r` é igual a `preparar(..., recorte=None)`
  sobre os mesmos inscritos.
- O número de consultas de `calcular_ordem` não muda.

## `desempate.ordenar_com_trajetoria`

```text
ordenar_com_trajetoria(participantes, criterios) -> lista
```

Cada item é o de `ordenar` mais:

| Chave | Forma |
|---|---|
| `trajetoria` | lista de `(passo, criterio, grupo)`, na ordem em que os critérios foram oferecidos ao grupo do item; `passo` é `"separou"` ou `"nao_separou"` |
| `grupo_da_pontuacao` | os participantes com a mesma pontuação combinada |

**Garantia**: `ordenar(p, c) == [sem(item, "trajetoria", "grupo_da_pontuacao") for item in
ordenar_com_trajetoria(p, c)]` para toda entrada da tabela-verdade de `tests/unit/classificacao/test_desempate.py`
e para todo cenário da prévia — a igualdade é teste, e não comentário.

## `cenarios_da_previa.gerar`

```text
gerar(chave, *, etapas_com_nota, portas, etapa_do_marco, fatos, alvo, suplentes, vagas, corta)
    -> (inscritos, ancora)
```

Devolve inscritos na forma de `preparar`. Determinística (FR-2205): duas chamadas com os mesmos
argumentos devolvem listas iguais, e nenhum argumento além destes a influencia.
