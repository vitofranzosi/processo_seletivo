# Tasks: A providência chega ao ato, e o ato volta ao Centro (139)

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Tests**: pedidos pela spec (SC-1490 a SC-1494); escritos com cada fase. Os puros vão em
`backend/tests/unit/interface/test_chegada_ao_ato.py`; os de cenário em
`backend/tests/integration/treinamento/test_chegada_e_volta_nos_cenarios.py`.

## Phase 1: Setup

- [x] T001 Branch sobre `origin/main` em `4ae78556`; `.specify/feature.json` apontando para `specs/139-chegada-ao-ato-e-volta`; `backend/.env` com `DB_NAME=ps139`; a linha da `139` na tabela de incrementos do `README.md`

## Phase 2: Foundational — as âncoras (R-001, R-002)

- [x] T002 `ancora_do_recorte(lista_id)`, `com_ancora(url, ancora)` e `ancora_comum(a, b)` em `backend/processo_seletivo/interface/andamento.py`, com a tabela das seções comuns (`recorte-` → `titulo-recortes`, `chamada-` → `chamadas`)
- [x] T003 [P] Testes puros das três funções: a ampla tem âncora própria; endereço vazio continua vazio; âncoras iguais se mantêm, de recorte juntam em `titulo-recortes`, de chamada em `chamadas`, de seções diferentes em nada (FR-4762, FR-4766)

## Phase 3: User Story 1 — o sorteio chega ao recorte (P1)

- [x] T004 [US1] `_sorteio.url(lista)` acrescenta a âncora do recorte; a semente vai a `#titulo-ocorrencia`, a semente impedida a `#titulo-recortes`, em `backend/processo_seletivo/interface/andamento.py` (FR-4760, FR-4761)
- [x] T005 [US1] O filtro `ancora_do_recorte` em `backend/processo_seletivo/interface/templatetags/interface_extras.py` e o `id` de cada `article.recorte` em `backend/processo_seletivo/interface/templates/interface/sorteio.html` (FR-4762)
- [x] T006 [US1] `providencias._juntar` compara o endereço sem `?` e sem `#`, e junta as âncoras pela `ancora_comum`, em `backend/processo_seletivo/interface/providencias.py`; os casos com fragmento — duas listas do sorteio, telas diferentes, a mesma seção — em `test_chegada_ao_ato.py`, ao lado dos de `test_providencias.py`, que continuam passando sem mudança (FR-4766)
- [x] T007 [US1] Testes de cenário no C06: a providência de congelar de cada lista leva ao recorte dela, a juntada leva aos recortes, e o id está na tela do sorteio; a situação, o ato, o responsável e a ordem das providências não mudam (SC-1490, SC-1493)

## Phase 4: User Story 2 — a convocação chega às chamadas (P1)

- [x] T008 [US2] `_documentos` devolve a posição da primeira chamada pronta, contando todas as linhas na ordem da leitura do recorte, em `backend/processo_seletivo/interface/andamento.py` (FR-4764)
- [x] T009 [US2] `situacoes_da_convocacao` põe a âncora de cada providência: `titulares`, `pendentes`, `vencidos`, `chamada-N` ou `chamadas`, `chamadas` para conferir e para a resposta aguardada, `fila`; o impedimento e o *Feito* ficam sem fragmento (FR-4763 a FR-4765)
- [x] T010 [P] [US2] Testes puros de `situacoes_da_convocacao` com e sem a posição da pronta, e sem endereço; as expectativas de `backend/tests/unit/interface/test_andamento_situacoes.py` não precisaram mudar (FR-4767)
- [x] T011 [US2] Teste de cenário no C12: a providência de conferir leva a `#chamadas` e a tela tem o id (SC-1491). O desfecho com uma chamada pronta não tem cenário que nasça assim; ficou no navegador (`verificacao.md`)

## Phase 5: User Story 3 — a volta ao Centro e o próximo alcançável (P1)

- [x] T012 [US3] `_proximo_nesta_lista` devolve `centro`, o endereço do Centro do Edital, em `backend/processo_seletivo/interface/views.py` (FR-4768, D-004)
- [x] T013 [US3] O parcial `backend/processo_seletivo/interface/templates/interface/_proximo_nesta_lista.html`: a linha `retorno-ao-centro` no fim do bloco; o item de "Ainda neste marco" com endereço vira link (FR-4768 a FR-4770)
- [x] T014 [US3] A regra `.retorno-ao-centro` em `backend/processo_seletivo/interface/static/interface/gestao/telas.css` (FR-4771, UX-320)
- [x] T015 [US3] Testes de tela em `backend/tests/interface/test_andamento_transicoes.py`: depois do ato, o retorno aparece com o endereço do Centro; abrir a tela sem ato não o mostra; a providência que nasce do ato leva à seção, que a tela tem (SC-1492). O item "sua" de "Ainda neste marco" como link fica no cenário C06

## Phase 6: Polish

- [x] T016 `cd backend && make lint check test-pg` com `DB_NAME=ps139`; os guardiões de citação, de acessibilidade (classe com regra na folha) e do inventário da 033
- [x] T017 Conferir no navegador, no C06 e no C12, a 1440 × 900: a providência chega ao ato dentro da primeira dobra e o retorno volta ao Centro (UX-319); `verificacao.md` com as medidas
- [ ] T018 Commit e PR contra a `main`, sem merge; dizer no PR o trecho de `andamento.py` tocado, por causa da triagem paralela dos achados F-1 a F-3

## Dependencies

- T002 antes de T004, T006 e T009; T005 depende de T002.
- US1, US2 e US3 são independentes entre si depois da Phase 2.
