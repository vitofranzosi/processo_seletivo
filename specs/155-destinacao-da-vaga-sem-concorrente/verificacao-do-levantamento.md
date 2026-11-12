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
- A **V-3** mostra o comportamento de hoje, e não o que o Edital autoriza: o usuário devolveu a
  primeira leitura que a spec tirou dela (a faixa como critério). O confronto com o 57/2026 e o
  35/2026 está na D-015 da spec, e os cenários que o tornam reproduzível estão abaixo.

## Como reproduzir

O arquivo usava as funções `apurar`, `emitir_cortes` e `habilitar` de
`tests/integration/ocupacao/test_concomitancia.py`, e `certame_sorteado_com_quadro` com
`reversao=`, `quantos=`, `geral=`, `cotistas_ppi=` e `excedente=`. Cada cenário emite os cortes,
habilita, apura a ampla e a PPI, registra a exclusão quando o cenário pede, e apura a PPI de novo com
motivo. A leitura é o dicionário que `emitir_apuracao` devolve (`ocupadas`, `faltando`, `reverteu`) e
os `MovimentoDeVaga` com origem na PPI. Os quatro casos passaram em 8,8 s, com `-n 0`.

A implementação da `155` transforma V-1 a V-4 em testes de integração com o resultado **novo** — e é
por isso que este arquivo registra o antigo.

## Os cenários da D-015 — reversão por saldo, como o 57/2026 e o 35/2026 a declaram

**Pedidos pelo usuário em 11/11/2026**, para fundamentar a condição da reversão por saldo antes de
fechá-la. Mesma fixture, com `reversao=` por saldo, `quantos=8`, `geral=1`, uma vaga na PPI e três
autodeclarados PPI, todos habilitados. **Hoje** foi medido em 11/11/2026, sobre `666e01d1`, contra
PostgreSQL, num arquivo exploratório não commitado, do mesmo jeito da V-3. As colunas das opções são o
resultado esperado de cada opção da D-015; a implementação transforma a coluna da opção escolhida em
teste de integração.

| # | Cenário | Cláusula | Hoje (medido) | A2 (recomendada) | A1 | B | C |
|---|---|---|---|---|---|---|---|
| S-1 | Faixa com alvo 1 e excedente 2 (os três analisados); o titular desiste | 8.8 e 8.12 do 57/2026; 8.8 e 8.11 do 35/2026 | **cede 1 à ampla** (efetivas da PPI: 0) | nada cedido; o 2º autodeclarado é chamado | o mesmo | cede | nada cedido |
| S-2 | Faixa com alvo 1 e excedente 0 (só o titular analisado); o titular desiste; os outros dois estão fora da faixa | 8.8; 8.13 e 8.14.1 do 57/2026 (8.12 e 8.13.1 do 35/2026) | **cede 1 à ampla** | nada cedido; o caminho é a chamada de suplentes, que os alcança | o mesmo | cede | **cede** |
| S-3 | O S-2, e a administração encerra a chamada de suplentes da PPI por ato fundamentado no 8.14.1 (8.13.1) | 4.3 e 8.14.1 (4.3 e 8.13.1) | não há o ato | a destinação é oferecida, com o encerramento citado | não é oferecida enquanto houver autodeclarado na ordem | — | — |
| S-4 | Um só autodeclarado, titular; ele desiste, e ninguém mais está na ordem da reserva | 4.3 | não medido; pela mesma conta do S-1, cede 1 à ampla na apuração seguinte, sem ato próprio | a destinação é oferecida por ato próprio | o mesmo | o mesmo | o mesmo |

**Requisitos que sustentam o resultado esperado de A1 e A2**: FR-6304 (quem ainda pode ocupar pela
reserva, dentro ou fora da faixa), FR-6305 (a condição do saldo, à espera da D-015), FR-6306 (a chamada
em curso impede), FR-6307 (as espécies não se fundem) e FR-6308 a FR-6310 (o ato com fundamento e
registro). O S-3 só existe na A2, e o ato de encerramento ganha requisito próprio quando ela for
escolhida.

**Medidos: S-1 e S-2.** O S-3 não tem ato hoje, e o S-4 segue a conta do S-1.

**Como reproduzir S-1 e S-2**: os passos da V-3, com `cotistas_ppi=3` e `excedente=2` (S-1) ou
`excedente=0` (S-2); a desistência é a exclusão do primeiro da ordem da PPI, que é quem a ocupa. Os dois
passaram em 9,0 s, com `-n 0`; em ambos, a apuração seguinte devolveu `efetivas=0` e `reverteu=1`.

