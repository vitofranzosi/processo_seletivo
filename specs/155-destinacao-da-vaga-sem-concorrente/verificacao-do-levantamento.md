# Verificação do levantamento — o que o código fazia, medido

**Pedido pelo usuário em 11/11/2026**: confirmar por teste os comportamentos que o levantamento da
spec tinha tirado só da leitura do código. Medido em 11/11/2026, sobre `f43c7216` (a `main` em
`d1ec1e0a` com a spec), contra PostgreSQL, num arquivo de teste exploratório que **não foi
commitado**: ele prende o comportamento de antes da `155`, que a implementação muda.

O cenário é o certame de sorteio das fixtures da `016` (`tests/fixtures/ocupacao_sorteada.py`), com
regra de corte, quadro com 1 vaga na PPI e a reversão declarada em cada caso. A desistência é o
efeito de exclusão que o desfecho de convocação registra (`registrar_efeito`, espécie de exclusão),
gravado direto, como `tests/integration/ocupacao/test_obsolescencia.py` já faz.

| # | Cenário | Esperado pela leitura | Medido | Leitura |
|---|---|---|---|---|
| V-1 | **Por esgotamento**, um só autodeclarado na PPI, habilitado, ocupando a vaga; ele desiste e a apuração seguinte é emitida | não esgota | antes: 1 de 1 ocupada; depois: **0 ocupadas, 1 a ocupar, nada cedido**; nenhum movimento | **Confirmado.** Quem saiu por desfecho continua com posição na ordem e conta como "quem ocupar". A reserva sem mais ninguém nunca esgota. |
| V-2 | **Por esgotamento**, um só autodeclarado na PPI, **sem habilitação** na Etapa governada | não estava no levantamento | **0 ocupadas, 1 a ocupar, nada cedido** | **Fato novo.** Inabilitado com posição também conta como "quem ocupar". |
| V-3 | **Por saldo**, três autodeclarados na PPI, todos habilitados e na faixa (alvo 1, excedente 2); o ocupante desiste | não estava no levantamento | **a apuração seguinte cede 1 vaga à ampla**; as efetivas da PPI vão a 0 | **Fato novo, e o mais grave.** Os dois autodeclarados habilitados da faixa, que a fila chamaria, perdem a vaga para a ampla. É o caso do Edital 57/2026 e do 35/2026, que declaram reversão por saldo. |
| V-4 | **Por esgotamento**, o único autodeclarado ocupa pela ampla | não esgota (pendência da `095`) | **0 ocupadas, 1 a ocupar, nada cedido** | **Confirmado** no caminho oficial; o teste unitário `test_a_reservada_toda_ocupando_pela_ampla_nao_esgota` já o prendia na função pura. |
| V-5 | **Por esgotamento**, todos **eliminados** antes da ordem (sem posição) | esgota | não medido de ponta a ponta: o sorteio não elimina | **Confirmado pela função e pela emissão.** `tests/unit/ocupacao/test_ha_quem_ocupar.py::test_sem_posicao_nao_conta` prende que a posição vazia não conta, e a emissão da ordem grava os sem posição com a posição vazia (`classificacao/application/emissao.py`). |

## O que a medição muda na spec

- A **N-3** do levantamento deixa de ser "a verificar": está medida (V-1).
- A **V-2** entra na decisão do usuário sobre o esgotamento: inabilitação é eliminação, e conta como
  ausência quando não cabe mais recurso.
- A **V-3** é o que dá corpo à condição própria da reversão por saldo (FR-6305): a vaga que a faixa
  da própria reserva ainda pode preencher não é saldo. Antes da `155`, era.

## Como reproduzir

O arquivo usava as funções `apurar`, `emitir_cortes` e `habilitar` de
`tests/integration/ocupacao/test_concomitancia.py`, e `certame_sorteado_com_quadro` com
`reversao=`, `quantos=`, `geral=`, `cotistas_ppi=` e `excedente=`. Cada cenário emite os cortes,
habilita, apura a ampla e a PPI, registra a exclusão quando o cenário pede, e apura a PPI de novo com
motivo. A leitura é o dicionário que `emitir_apuracao` devolve (`ocupadas`, `faltando`, `reverteu`) e
os `MovimentoDeVaga` com origem na PPI. Os quatro casos passaram em 8,8 s, com `-n 0`.

A implementação da `155` transforma V-1 a V-4 em testes de integração com o resultado **novo** — e é
por isso que este arquivo registra o antigo.
