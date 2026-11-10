# Rastreabilidade: a convocação e a conferência documental, pelas perguntas de quem conduz (143)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`. Abreviações:

- `u` = `unit/interface/test_conducao_da_convocacao.py` — passo, aviso e índice, sem banco
- `t` = `integration/treinamento/test_convocacao_pelas_perguntas.py` — C10, C11 e C12 da `134`
- `c` = `interface/test_convocacao.py` — a tela da convocação da `019`
- `p` = `performance/test_conducao_com_documentos.py` e `performance/test_convocacao.py`
- `cv` = `integration/treinamento/test_chegada_e_volta_nos_cenarios.py` — a `139`

A faixa abre em **FR-5000**, **SC-1560** e **UX-370**. Gastos até FR-5028, SC-1566 e UX-374; o resto
da reserva fica livre.

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-5000 — o lugar do recorte no alto | T006, T007 | `t::test_c10`, `t::test_c11` |
| FR-5001 — as perguntas do índice | T004, T007 | `u::test_o_indice_leva_a_primeira_chamada_de_cada_pergunta`, `t::test_c11` |
| FR-5002 — o link para o lugar do ato | T004, T007 | `u::test_o_indice_leva_a_primeira_chamada_de_cada_pergunta`, `t::test_c10` (`#titulares`), `t::test_c11`, `t::test_c12` |
| FR-5003 — o índice não prioriza | T004 | `u::test_a_ordem_do_indice_e_fixa` |
| FR-5004 — sem providência, dito | T004, T007 | `u::test_sem_providencia_quando_ninguem_tem_ato`, `t::test_c10` (PPP sem apuração) |
| FR-5005 — o grupo da apuração, com os mesmos números | T009 | `c::TestOsEstadosDistintos::test_a_tela_mostra_os_quatro_numeros_da_016`, `c::test_a_tela_nao_afirma_numero_de_ocupacao_diferente_do_apurado`, `t::test_c10` |
| FR-5006 — o grupo das chamadas | T009 | `t::test_c10` |
| FR-5007 — a distinção e a explicação | T009 | `t::test_c10` |
| FR-5008 — as três áreas, na ordem | T011 | `t::test_c10` |
| FR-5009 — os ids da `139` | T011 | `t::test_c12`, `cv::test_c12`, `interface/test_conferencia_ao_convocar.py` |
| FR-5010 — a âncora estável | T010 | `t::test_c11`, `t::test_c12` |
| FR-5011 — o passo da chamada | T004, T010 | `u::test_a_precedencia_do_passo`, `u::test_com_desfecho_o_passo_e_a_situacao_e_nao_ha_acao`, `u::test_por_publicacao_o_passo_diz_registrar_a_publicacao`, `t::test_c11` |
| FR-5012 — a ação só a quem pode | T010 | `u::test_quem_so_consulta_nao_tem_trabalho_marcado_nem_titulares`, `t::test_c11` (auditoria) |
| FR-5013 — o desfecho aberto quando é o passo | T010 | `t::test_c12`, `navegador/test_jornada_dos_documentos_da_convocacao.py` |
| FR-5014 — as exceções no cartão, secundárias | T010 | `interface/test_correcao_da_convocacao.py`, `navegador/test_jornada_da_correcao_da_convocacao.py` (os formulários de sempre) |
| FR-5015 — quando a pendência foi registrada | T004, T010 | `u::test_sem_aviso_a_pendencia_nao_e_comunicacao`, `t::test_c11` |
| FR-5016 — a situação do aviso pela `066` | T004 | `u::test_o_aviso_depois_da_pendencia_diz_a_situacao_do_envio`, `t::test_c11` (momentos 2 e 3) |
| FR-5017 — sem aviso: alcança ou por quê | T003, T004 | `u::test_sem_aviso_a_pendencia_nao_e_comunicacao`, `u::test_o_motivo_da_previa_diz_por_que_o_aviso_nao_alcanca`, `u::test_quem_nao_confere_nao_le_sobre_o_gesto`, `t::test_c11` (momento 1) |
| FR-5018 — pendência não é comunicação | T004, T010 | `u::test_sem_aviso_a_pendencia_nao_e_comunicacao`, `t::test_c11` |
| FR-5019 — o contexto nos documentos | T012, T013 | `t::test_c11` |
| FR-5020 — o resumo dos documentos | T013 | `t::test_c12` (passeio: `depois-08`) |
| FR-5021 — a situação nos documentos | T012, T013 | `t::test_c11`, `t::test_c12` |
| FR-5022 — o desfecho pela âncora | T013 | `t::test_c12` |
| FR-5023 — o aviso pela convocação | T013 | `t::test_c11` (antes do aviso, pela tela; passeio `depois-06`) |
| FR-5024 — as pessoas do recorte | T012, T013 | `t::test_c11` |
| FR-5025 — as explicações | T009, T014 | `t::test_c10` (ocupação); corte, sucessão e desfecho no passeio |
| FR-5026 — nenhum comando muda | todas | a suíte inteira; `interface/test_conferencia_ao_convocar.py`, `interface/test_convocacao_em_fluxo.py` |
| FR-5027 — sem consulta por linha | T004 | `p` |
| FR-5028 — sem inline | T008, T013 | `interface/test_estaticos.py`, `interface/test_folha_estatica.py`, `interface/test_acessibilidade.py` |

## Critérios de sucesso

| Critério | Como |
|---|---|
| SC-1560 | passeio (`verificacao.md`): no C12, o índice a y=430 e as respostas na primeira tela |
| SC-1561 | passeio: o `select` do desfecho a y=557 depois do link dos documentos |
| SC-1562 | `t::test_c10`, `c::test_a_tela_nao_afirma_numero_de_ocupacao_diferente_do_apurado` |
| SC-1563 | `t::test_c11` e passeio do C12 (`depois-06-*`) |
| SC-1564 | `p` |
| SC-1565 | a suíte inteira; nenhuma rota nova; `csp=0` em todos os passos do passeio |
| SC-1566 | passeio a 375 px (`verificacao.md`) |

## Requisitos de experiência

| Requisito | Como |
|---|---|
| UX-370 | passeio: `depois-05-c12-dobra.png` |
| UX-371 | `convocacao.css` (`.passo-da-chamada`, `.chamada.tom-*`); a palavra "Próximo passo"/"Situação" |
| UX-372 | `convocacao.css` (`.grupo-de-numeros.calculado` tracejado, `.praticado` contínuo) |
| UX-373 | passeio a 375 px |
| UX-374 | `convocacao.css` (`.outras-acoes`, `details[open]` com a largura toda) |

## Casos-limite

| Caso | Teste |
|---|---|
| Recorte que ninguém declarou | `u::test_lista_que_ninguem_declarou_nao_tem_perguntas` |
| Marco intermediário | `interface/test_convocacao_em_fluxo.py` e `integration/convocacao/test_convocacao_em_marco_intermediario.py` (as seções de hoje); o índice não conta titulares (`indice`, `marco_intermediario`) |
| Ordem por documentos | `u::test_o_indice_leva_a_primeira_chamada_de_cada_pergunta` (âncora pela convocação, e não pela posição) |
| Convocação corrigida | `avisos_por_raiz` sobe a raiz nas convocações do recorte; coberto pela leitura da `134` |
| Aviso anterior à pendência | `u::test_aviso_anterior_a_pendencia_nao_a_cobre` |
| Envio de avisos desabilitado | `u::test_envio_desabilitado_e_dito` |
| Chamada sem documento pedido | `u::test_a_precedencia_do_passo` (último caso) |
| Vencimento decorrido com documento a conferir | `u::test_a_precedencia_do_passo` (segundo caso) |
| Quem só confere | `u::test_quem_nao_confere_nao_le_sobre_o_gesto`; o desfecho como passo de quem conduz no template |
| Auditoria | `t::test_c11` |
