# Tasks: Cinco ajustes de leitura dos Documentos Exigidos

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Caminhos**: `PS` abrevia `backend/processo_seletivo` e `T` abrevia `backend/tests`.

## Phase 1: US1 — a Revisão por momento

- [x] T001 [US1] Em `PS/interface/revisao.py`, trocar o bloco único dos Documentos Exigidos por dois, por momento, o da convocação só quando houver, e tirar a linha "Pedido" do item (FR-4501, FR-4502, FR-4503, D-001)
- [x] T002 [US1] Casos em `T/interface/test_ajustes_dos_documentos.py`; rever os testes que liam a linha "Pedido" ou o título antigo (SC-1401)

## Phase 2: US2 — somente leitura

- [x] T003 [US2] Pôr `somente_leitura` no contexto da composição em `PS/interface/views.py` (D-002)
- [x] T004 [US2] O `fieldset` desabilitado nas etapas Inscrição, Perfis, Cronograma e Etapas, e a regra dele na folha comum (FR-4504, D-003)
- [x] T005 [US2] Na Classificação, `disabled` campo a campo em `compor_classificacao.html`, `_marco.html` e `_criterio.html`, os botões de consulta de fora (FR-4504, FR-4507, D-004)
- [x] T006 [US2] Tirar setas, lixeira, "Acrescentar", "Remover", "Aplicar aos demais" e "Duplicar" em somente leitura (FR-4505)
- [x] T007 [US2] `_navegacao_etapa.html` por link em somente leitura (FR-4506, D-005)
- [x] T008 [US2] `PS/interface/static/interface/somente-leitura.js`, carregado só em somente leitura na Classificação (FR-4507, D-004)
- [x] T009 [US2] Casos: nenhum campo habilitado nas cinco etapas, nenhum controle de lista, Avançar por link, simulação com os valores do cartão, editável inalterada, servidor ainda recusa (SC-1402, SC-1403, FR-4508, FR-4509)

## Phase 3: US3 — a ajuda dos documentos

- [x] T010 [US3] Os quatro itens novos no `details.como-preencher` de "Documentos exigidos" em `compor_inscricao.html` (FR-4510, FR-4511, D-006)
- [x] T011 [US3] Casos: os quatro itens, a frase do campo palavra por palavra, o cartão sem ajuda nova (SC-1404, FR-4512)

## Phase 4: US4 — a página pública

- [x] T012 [US4] Em `PS/portal/views.py`, o anúncio leva a obrigatoriedade de cada documento e conta só os obrigatórios a todos na inscrição (FR-4513, D-007)
- [x] T013 [US4] Em `selecao.html`, a marca "(facultativo)" em todo grupo e os três resumos (FR-4514, FR-4515)
- [x] T014 [US4] Casos em `T/integration/portal/test_anuncio_dos_documentos.py`; rever os que liam "que serão pedidos" (SC-1405)

## Phase 5: US5 — o fundamento

- [x] T015 [US5] Em `PS/convocacao/domain/documentos.py`, o ponto final simples do motivo cede à pontuação da frase (FR-4516, D-008)
- [x] T016 [US5] Casos em `T/unit/convocacao/test_fundamento_das_pendencias.py` (SC-1406)

## Phase 6: Verificação

- [x] T017 `cd backend && make lint check test-pg`, com `DB_NAME` próprio
- [x] T018 Capturas de antes e depois em [capturas/](capturas/), num clone descartável de `gps_docs_demo` (SC-1407), e o registro em [verificacao.md](verificacao.md)
- [x] T019 A linha da `132` na tabela de incrementos do `README.md`
