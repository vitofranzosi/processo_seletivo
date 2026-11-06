# Tasks: Os textos que o operador do sorteio lê

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Caminhos**: `PS` abrevia `backend/processo_seletivo` e `T` abrevia `backend/tests`.

## Phase 1: US1 — a falha de acesso nas palavras de quem conduz

- [x] T001 [US1] Extrair a tradução da falha de `_uma_chamada` para `_motivo_da_falha` em `PS/sorteios/infrastructure/fontes/loteria_federal.py`, com o `ValueError` como erro da Caixa (D-001, D-002)
- [x] T002 [US1] Em `LoteriaFederal.observar`, guardar o motivo na evidência e mandar ao log, num registro só, as falhas de cada tentativa (FR-3961, FR-3962)
- [x] T003 [US1] Tirar os asteriscos da recusa `source_unreachable` em `PS/sorteios/application/ocorrencia.py` (FR-3963)
- [x] T004 [US1] Em `T/integration/sorteios/test_falha_de_acesso_a_fonte.py`, acertar o falso e as asserções antigas e acrescentar os casos das cinco falhas, pela observação e pela recusa, e o do log (SC-1191)

## Phase 2: US2 — o limite inferior

- [x] T005 [US2] Pôr `fonte_publica_so_a_data` no contexto da tela do sorteio, em `PS/interface/views.py`, e as três frases em `PS/interface/templates/interface/sorteio.html` (FR-3964, FR-3965)
- [x] T006 [US2] Em `T/interface/test_tela_do_sorteio.py`, um caso para a fonte que publica só o dia e um para a que publica a hora

## Phase 3: US3 — a ocorrência na ajuda da etapa

- [x] T007 [US3] Acrescentar o item "Ocorrência que fixará a semente" a `PS/interface/templates/interface/_como_preencher_o_marco.html`, com as frases da descrição do campo (FR-3966, FR-3967, D-003, D-004)
- [x] T008 [US3] Em `T/interface/test_metodo_do_marco.py`, provar o item, o link e as frases idênticas nas três ocorrências

## Phase 3b: Achados da revisão do PR

- [x] T012 Levar o log da falha de acesso para `PS/sorteios/application/ocorrencia.py`, com a correlação, e o detalhe técnico para `Observacao.falhas`; trocar a primeira frase da recusa, que dizia "não foi possível falar com a fonte" mesmo quando a Caixa respondeu com erro (FR-3962, FR-3963, D-005)

## Phase 4: Verificação

- [x] T009 `cd backend && make lint check test-pg`
- [x] T010 Conferir as três telas no navegador, com a fonte inacessível para a recusa (SC-1192), e registrar em [verificacao.md](verificacao.md)
- [x] T011 Acrescentar a linha da `124` à tabela de incrementos do `README.md`
