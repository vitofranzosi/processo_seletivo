# Data Model: A ordem por pontuação sem nenhum resultado é recusada (128)

**Nenhuma entidade, tabela, coluna ou estado persistido novo** (FR-4219).

## O que a regra lê

Da proposta que `calcular_ordem` já devolve, sem consulta nova (R-1):

| Campo | De onde | Para quê |
|---|---|---|
| `marco.stages` | conteúdo vigente | as Etapas enumeradas |
| `etapas[id].name` | conteúdo vigente | o nome publicado, na frase |
| `posicoes`, `sem_posicao` | `universo_classificavel.preparar` | o universo considerado do recorte |
| `pontuacoes` de cada linha | os Resultados vigentes lidos | a Etapa com Resultado, com ou sem valor |

## O impedimento (derivado, não gravado)

`ordem_sem_resultado.impedimento(proposta)` → `None` ou:

| Chave | Valor |
|---|---|
| `inscricoes` | quantas inscrições o universo tem |
| `etapas` | `[(id, nome publicado)]` das Etapas enumeradas, na ordem do marco |
| `frase` | a frase da UX-260 |

`recusar(proposta)` levanta `DomainError("ordering_without_stage_results", frase, 422, campo="marco")`
quando há impedimento.

## Estados

Nenhum novo. A ordem continua *Falta* na condução enquanto não emitida; a tela da ordem explica.
