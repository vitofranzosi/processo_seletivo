# Data Model: Prévia interativa da classificação — fatia 2

Nenhuma entidade é persistida. Tudo abaixo existe na resposta do fragmento e é descartado com ela
(FR-2341). As entidades da `094` — cenário, prévia, universo classificável, população estável, ponto
da jornada, mudança — continuam como são; aqui ficam só as que mudam ou nascem.

## Recorte da prévia

| Campo | Origem | Regra |
|---|---|---|
| `lista_id` | `recortes_do_perfil(snapshot, perfil_id)` | `None` é a ampla; a Modalidade apontada como ampla não aparece (FR-2301) |
| `rotulo` | a mesma derivação | o rótulo do recorte, como as telas de ordenação e ocupação o mostram |
| `linha` | `linha_do_quadro(snapshot, perfil_id, lista_id)` | `None` quando o recorte não tem linha: corte do quadro não apurável, ocupação não avaliada (FR-2308, FR-2322) |

Ordem: a da derivação — ampla primeiro, reservadas na ordem declarada. Limite: 6 reservadas (R-006).

## Candidato fictício *(estendido)*

| Campo | Regra |
|---|---|
| `modalidade_id` | `None` ou o id de **uma** Modalidade reservada do Perfil (FR-2333); atribuído pela população estável ou pelo caso-limite, nunca lido de inscrição real (FR-2342) |
| `nome` | fictício, sem marca da Modalidade |

As notas, os fatos e as consequências por Etapa são os da `094`. A atribuição de Modalidade não muda
nota nem posição na ampla (D-003).

## Prévia de um recorte

| Campo | Conteúdo |
|---|---|
| `recorte` | o Recorte da prévia |
| `ordem`, `sem_posicao`, `corte` | os da `094`, calculados sobre o recorte |
| `posicao_na_ampla` | por linha, nas reservadas (FR-2314) |
| `ocupa_pela_ampla` | conjunto de ids, nas reservadas: quem está entre os titulares da ampla (FR-2317, FR-2318) |
| `tomadas_pela_ampla` | quantas posições da faixa do recorte são de quem ocupa pela ampla (FR-2319) |
| `alem_da_faixa` | quantos do recorte têm posição e ficaram fora da faixa (FR-2319) |
| `ocupacao` | `{publicadas, efetivas, ocupadas, faltando}` ou `{avaliada: False, motivo}` |
| `reversao` | `{especie, ha_quem_ocupar, pessoas_com_posicao, cederia}`, só nas reservadas; `None` sem declaração |

**Estados da ocupação de um recorte**: `avaliada`; `sem_linha` (FR-2322); `corte_nao_emitido`
(FR-2324); `parou_na_fronteira` com posição e tamanho do empate (FR-2323); `depende_da_ampla`, quando
a ampla não foi avaliada (FR-2323, FR-2324).

## Rodada de ocupação

| Campo | Conteúdo |
|---|---|
| `hipoteses` | as quatro da FR-2320, em texto fixo |
| `recortes` | as Prévias de recorte, na ordem |
| `cedido_total` | soma de `cederia` das reservadas |
| `efetivas_da_proxima_ampla` | `publicadas da ampla + cedido_total`, quando `cedido_total > 0` (FR-2321) |
| `especie_lida_de` | "passo Perfis, rascunho gravado" (FR-2326) |

**Invariantes**: `ocupadas ≤ efetivas`; `faltando = efetivas − ocupadas ≥ 0` (FR-2325); nenhuma
quantidade quando o estado não é `avaliada` (SC-874); `cederia = 0` em todo recorte quando não há
espécie declarada (SC-875).

## Participantes da Etapa seguinte

| Campo | Conteúdo |
|---|---|
| `uniao` | tamanho da união, por pessoa, das faixas (R-008) |
| `so_pela_ampla` | tamanho da faixa da ampla |
| `acrescentados_pelas_reservadas` | `uniao − so_pela_ampla` |
| `depende_de` | recortes cujo corte não seria emitido; com algum, o número é dito como dependente (FR-2311) |

## Mudança *(estendida)*

A diferença da `094` ganha, por recorte, a situação do corte, o número dos que avançam, as quatro
quantidades e `cederia`, e o total da Etapa seguinte (FR-2334). Continua existindo só dentro da mesma
população.
