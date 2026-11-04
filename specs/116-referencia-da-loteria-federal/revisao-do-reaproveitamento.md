# Revisão: o reaproveitamento de Editais históricos sob a 116

Revisão bloqueante pedida pelo usuário em 04/11/2026, antes do merge do #370 e do #372. O que ela
decidiu está na spec: *Session 2026-11-04*, US7, FR-3715 a FR-3720, SC-1115, SC-1116 e D-009.

## 1. Diagnóstico do impacto atual

O reaproveitamento (`editais/application/reaproveitamento.py::reaproveitar_edital`) lê a versão
vigente da origem, gera identidades novas (`mapa_de_identidades`, `remapear`), monta as coleções do
rascunho (`payload_do_conteudo`) e grava por `replace_draft`, a porta única das invariantes do
rascunho. O método do sorteio atravessa esse caminho **inteiro**: o comum vai como está
(`payload_do_conteudo`, "copia-se, e não se remapeia"), e o de cada marco viaja dentro do Perfil, só
com a Etapa de habilitação remapeada.

A gravação exige o método inteiro — os sete campos —, inclusive no rascunho
(`perfis._validar_metodo_de_sorteio`, a FR-013 da `021`). Com a forma da 116 nessa mesma função,
cada origem cai num de dois defeitos:

| Origem | Antes da 116 | Com a 116, antes desta revisão |
|---|---|---|
| `6010` (forma válida) | copiado em silêncio | **copiado em silêncio**: o novo Edital nasce com o concurso já sorteado, e só a submissão o recusa, como "já realizado" |
| `Concurso 6010` (acervo) | copiado em silêncio | **a cópia inteira é recusada** na gravação, e quem reaproveita não tem como corrigir antes de copiar |
| sem sorteio | nada | nada |

O primeiro é o incidente que a 116 existe para prevenir, transportado pelo reaproveitamento. O
segundo tira do acervo o uso mais comum que ele tem. Nenhum dos dois altera a origem: ela continua
íntegra e retificável, porque a Retificação não reconfere a forma do que não toca (FR-3624).

**O corpus da suíte.** `tests/fixtures/corpus.py` passou a republicar o 91/2026 com a forma e a
conferência desligadas. A exceção é adequada **só** à reconstituição do acervo: o corpus é conteúdo
publicado antes da 116, e reescrevê-lo mudaria o que outros casos comparam. Ela não pode servir ao
reaproveitamento operacional, que cria um Edital novo e precisa das regras de hoje. Antes desta
revisão o patch morava ad hoc em três lugares (o corpus e dois casos da 116); passa a morar num só,
`tests/fixtures/legado.py::antes_da_116()`, ao lado do `sem_as_regras_da_046()` que já faz o mesmo
papel para a `046` (FR-3720).

## 2. Alternativas

| | Como | O que custa | Veredito |
|---|---|---|---|
| A | Copiar como está | leva o `6010` em silêncio; recusa o `Concurso 6010` | é o defeito |
| B | Desligar a forma no reaproveitamento, como no corpus | leva o concurso antigo, de qualquer grafia | proibido pela diretriz (4) |
| C | Não copiar o método | redeclarar até dez campos por marco; perde a regra que é o valor do reaproveitamento; o marco por sorteio fica sem método | correto, mas perde a diretriz (preservar a estrutura) |
| D | Copiar sem `occurrence` e `occurrenceAt`; o rascunho admite o método sem os dois; o ato os exige | um parâmetro na validação do rascunho, uma mensagem, uma linha na cópia | **recomendada** |
| E | Valor de marcação ("A DEFINIR") | dado inventado; a forma o recusa; um descuido o publica | descartada |
| F | Estado ou indicador "extração pendente" | coluna, migração ou chave nova para o que a ausência já diz | descartada: infraestrutura paralela |

## 3. Recomendação arquitetural mínima (D)

1. **Na cópia**, `payload_do_conteudo` tira `occurrence` e `occurrenceAt` do método comum e do método
   de cada marco. É o mesmo lugar e a mesma razão por que o `status` do Evento reinicia: é o que
   *aconteceu* na oferta anterior (a FR-008a da `023`). Algoritmo, fonte, derivação, normalização,
   substituição e Etapa de habilitação passam.
2. **Na gravação**, `_validar_metodo_de_sorteio` ganha `exigir_a_extracao`, ligado por padrão. Só a
   gravação do rascunho o desliga — `validate_classification_milestones` (chamada só pela gravação e
   pelo serializer do rascunho) e `validate_common_draw_method` a partir de `replace_draft`. A
   admissão é estreita: **os dois** campos ausentes. Um sem o outro continua método pela metade.
3. **Nos atos**, nada muda de lugar: `validate_for_publication` chama a função direto, com o padrão,
   e a submissão, a publicação e a Retificação continuam recusando. A ausência dos dois tem mensagem
   própria: o que declarar, onde, e que o Edital reaproveitado não herda a extração (FR-3717).
4. **Na conferência**, o método sem referência sai de `referencias_a_conferir`: não há o que
   perguntar à Caixa, e o impeditivo já é do método.
5. **Na tela**, o desfecho do reaproveitamento diz quantos métodos esperam a extração, com o caminho
   para a etapa Classificação; a escolha da origem a lista em "O que não vem" (FR-3718).

Por que é suficiente: a ausência dos dois campos é, ela mesma, o estado "a extração ainda não foi
declarada" — não há o que guardar além dela. E por que não enfraquece nada: nenhum método sem a
extração chega a ser publicado, então a constituição do sorteio, o resumo do método na relação, a
precedência e a conferência da 116 continuam valendo sobre o que é publicado.

## 4. Requisitos ajustados na spec

- **FR-3715**: a cópia sem a extração, para qualquer fonte e grafia.
- **FR-3716**: a gravação admite os dois campos ausentes, e só eles.
- **FR-3717**: os atos recusam, com a indicação do que declarar.
- **FR-3718**: a indicação na composição e na escolha da origem.
- **FR-3719**: a origem intacta e retificável.
- **FR-3720**: um mecanismo só para reconstituir o acervo na suíte, e o reaproveitamento testado pelo
  comando real.
- **SC-1115** e **SC-1116**: a cópia sempre conclui sem trazer a extração; sem ela não submete, com
  ela publica.
- **D-009**, a decisão e as alternativas; a conta do 9999 nos *Edge Cases* corrigida (3885, e não
  5885).

## 5. Testes adicionais

Em `backend/tests/integration/editais/test_reaproveitamento_sem_a_extracao.py`, pelo comando real e
com a forma e a conferência ligadas no destino, separados dos de compatibilidade histórica:

| Caso pedido | Caso |
|---|---|
| histórico com `Concurso 6010` | a origem é o 91/2026 do corpus, reconstituído por `antes_da_116()` |
| número antigo válido, `6010` | origem publicada hoje |
| método comum | o comum vem sem a extração; os marcos continuam sem método próprio |
| métodos próprios nos marcos | cada um sem a extração, com os outros campos iguais |
| sem sorteio | nenhum método aparece |
| editar antes de configurar | grava outra etapa pelo `PUT /rascunho` |
| submeter e publicar sem a referência | a submissão recusa com a indicação; a validação de publicação tem o impeditivo |
| referência futura e publicação | declara, submete, homologa e publica |
| origem consultável e retificável | o conteúdo vigente da origem continua com a referência dela; uma Retificação de outro campo publica |
| identificadores e etapas | a Etapa de habilitação e as Etapas do marco existem no destino, e nenhuma é da origem |

Em `backend/tests/unit/editais/test_metodo_sem_a_extracao.py`, a regra da gravação e dos atos; e em
`backend/tests/interface/test_reaproveitar.py`, a indicação na tela.

Os de compatibilidade histórica continuam onde estão — a republicação do corpus, o congelamento do
acervo (`test_forma_do_acervo_congela_com_advertencia`), a Retificação do acervo
(`test_acervo_nao_e_reconferido`) — e passam a usar `antes_da_116()`.

## 6. Riscos de regressão

- **O rascunho sem a extração deixa de ser recusado também fora do reaproveitamento.** Quem compõe à
  mão pode gravar o método com os dois campos vazios. A submissão recusa com a mesma indicação, e
  nada se publica assim. É o comportamento certo para trabalho em curso, mas é mudança.
- **A derivação em prosa vem da origem**, e pode citar o concurso antigo ("concurso 6010: a extração
  de sábado…"). É regra, e é de quem compõe revisá-la; a indicação da FR-3718 pede conferir a
  derivação junto.
- **Testes que comparam o método copiado inteiro.** Os de `test_reaproveitamento.py` leem a Etapa de
  habilitação, e não a ocorrência; a suíte inteira é o que confirma.
- **A prévia do documento de um rascunho sem a extração** imprime a linha do método sem o concurso.
  O compositor já trata campo vazio.

## 7. Critério objetivo de liberação para merge

1. `make lint check test-pg` verde, sem falha, com a lista de pulados igual à da T030.
2. Os dez casos da seção 5 verdes, e cada um visto falhando antes da implementação.
3. Nenhum teste de reaproveitamento usa `antes_da_116()` para o Edital de destino; o único uso fora
   do corpus é reconstituir uma origem ou um caso de acervo (conferido por `grep`).
4. O E2E com `SORTEIO_E2E_FONTE_REAL=1` continua passando.
5. `tests/test_citacoes_de_requisito.py` verde com FR-3715 a FR-3720 na rastreabilidade.
6. O merge é do usuário.
