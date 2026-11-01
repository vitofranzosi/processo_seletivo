# Rastreabilidade: Encerramento seguro do Edital

Cada requisito → a tarefa que o implementa → o teste que o verifica. As tarefas estão em
[tasks.md](tasks.md); os caminhos de teste são relativos a `backend/tests/`. **Os nomes de teste são os
planejados**; a T028 os troca pelos reais depois da implementação.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-3528 (recusa com a lista, sem gravar nada; tela e serviço) | T012, T013, T015 | `integration/processos/test_encerramento_seguro.py`; `contract/test_finalizacao_api.py`; `interface/test_confirmacao_do_encerramento.py` |
| FR-3529 (período com término em curso ou por abrir; sem término não impede) | T011 | `unit/processos/test_pendencias_do_edital.py` (casos do período) |
| FR-3530 (prazo recursal declarado e computável em curso) | T003, T011 | `unit/processos/test_pendencias_do_edital.py` (casos do prazo) |
| FR-3531 (recurso aguardando admissibilidade ou julgamento) | T002, T011 | `unit/processos/test_pendencias_do_edital.py` (casos do recurso) |
| FR-3532 (reavaliação ou providência pendente) | T004, T011 | `unit/processos/test_pendencias_do_edital.py` (reavaliação, providência) |
| FR-3533 (Retificação homologada) | T011 | `unit/processos/test_pendencias_do_edital.py` (homologada, vigência futura, duas) |
| FR-3534 (as advertências) | T019, T020 | `interface/test_confirmacao_do_encerramento.py` (advertências) |
| FR-3535 (a mesma regra da `099`) | T020 | `interface/test_confirmacao_do_encerramento.py` (SC-1069) |
| FR-3536 (cancelar nunca recusa; "Serão atingidos") | T013, T024 | `integration/processos/test_encerramento_seguro.py` (cancelamento); `interface/test_confirmacao_do_encerramento.py` (cancelar) |
| FR-3537 (impedimentos antes, sem confirmar) | T015, T016 | `interface/test_confirmacao_do_encerramento.py` |
| FR-3538 (caminho só a quem a tela aceita) | T014 | `interface/test_confirmacao_do_encerramento.py` (permissões) |
| FR-3539 (advertências à parte) | T021 | `interface/test_confirmacao_do_encerramento.py` |
| FR-3540 (sem dado pessoal) | T014, T020 | `interface/test_confirmacao_do_encerramento.py` (SC-1071) |
| FR-3541 ("Nenhuma pendência registrada no GPS…") | T021 | `interface/test_confirmacao_do_encerramento.py` |
| FR-3542 (consequências sem "conclusão regular") | T022 | `interface/test_confirmacao_do_encerramento.py` |
| FR-3543 (no instante do ato; concorrência; reexibe a lista) | T013 | `integration/processos/test_encerramento_concorrente.py`; `interface/test_confirmacao_do_encerramento.py` (POST com impedimento) |
| FR-3544 (Retificação parada) | T026 | `interface/test_retificacao_parada.py` |
| FR-3545 (nada posterior muda; A-09 intacto; Processo intacto) | T008, T029 | `integration/processos/test_encerramento_concorrente.py` (ato posterior aceito); `integration/publicacoes/test_retificacao_de_edital_encerrado.py` (inalterado); `acceptance/test_us7_finalizacao.py` (inalterado) |
| SC-1067 (cada impedimento recusa, sem mudança) | T007, T009, T010 | `integration/processos/test_encerramento_seguro.py`; `contract/test_finalizacao_api.py`; `interface/test_confirmacao_do_encerramento.py` |
| SC-1068 (cancelamento com tudo junto) | T023 | `integration/processos/test_encerramento_seguro.py` |
| SC-1069 (providências do relatório exibidas antes) | T018 | `interface/test_confirmacao_do_encerramento.py` |
| SC-1070 (concorrência) | T008 | `integration/processos/test_encerramento_concorrente.py` |
| SC-1071 (contagem a quem não julga; sem dado pessoal) | T010, T017 | `interface/test_confirmacao_do_encerramento.py` |
| SC-1072 (< 1 s com 400 inscrições) | T017, T030 | `performance/test_confirmacao_do_encerramento.py` (orçamento de consultas fixo); a medição isolada em `verificacao.md` |

## Casos-limite

| Caso-limite | Tarefa | Teste |
|---|---|---|
| Sem período designado | T011 | `unit/processos/test_pendencias_do_edital.py` |
| Período cancelado por Retificação | T011 | idem |
| Período sem término declarado (D-008) | T011, T019 | idem; `interface/test_confirmacao_do_encerramento.py` (advertência) |
| Período prorrogado (vale o vigente) | T011 | `unit/processos/test_pendencias_do_edital.py` |
| Retificação homologada com vigência futura | T011 | idem |
| Várias Retificações em curso | T011, T019 | idem |
| Marco que não admite recurso | T011 | idem |
| Prazo de recurso não declarado ou não computável (D-002) | T011, T019 | idem; `interface/test_confirmacao_do_encerramento.py` |
| Recurso não admitido | T011 | `unit/processos/test_pendencias_do_edital.py` |
| Recurso julgado com reavaliação determinada | T011 | idem |
| Ato concorrente entre abrir a tela e confirmar | T013 | `integration/processos/test_encerramento_concorrente.py`; `interface/test_confirmacao_do_encerramento.py` |
| Rascunho com o período encerrado (D-007) | T011 | `unit/processos/test_pendencias_do_edital.py` |
| Quem encerra sem permissão de julgar | T014 | `interface/test_confirmacao_do_encerramento.py` |
| Repetição do pedido já concluído | T013 | `integration/processos/test_encerramento_seguro.py` |
| Edital ainda não publicado | — | inalterado: `acceptance/test_us7_finalizacao.py` |
