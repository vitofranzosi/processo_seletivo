# Rastreabilidade: A confirmação de "Encerrar Processo" adverte as providências em aberto (130)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `un` = `unit/interface/test_advertencia_do_processo.py` — os tipos e o resumo, sem banco
- `te` = `interface/test_advertencia_do_encerramento_do_processo.py` — a tela, o envio e a composição
- `de` = `performance/test_confirmacao_do_encerramento_do_processo.py` — as consultas
- `pr` = `interface/test_processo.py` — o fluxo de hoje (ativar, encerrar, cancelar), com o helper ajustado
- `cq` = capturas em `capturas/`

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4350 (por Edital final publicado) | T005, T006, T009 | `te::test_o_bloco_mostra_a_convocacao_no_prazo_antes_das_consequencias`; `te::test_os_editais_em_ordem_sem_o_nunca_publicado_e_sem_os_que_nada_tem` |
| FR-4351 (a regra e a frase da 113 e da 099) | T004, T006 | `te::test_as_frases_sao_as_da_confirmacao_do_edital_e_do_relatorio`; `te::test_os_editais_em_ordem_sem_o_nunca_publicado_e_sem_os_que_nada_tem` (paridade em cada grupo) |
| FR-4352 (período e Retificação fora) | T005 | `un::test_periodo_e_retificacao_ficam_fora`; `un::test_todo_tipo_de_situacao_foi_decidido_uma_vez`; `te::test_periodo_e_retificacao_nao_aparecem` (Edital encerrado com Retificação em revisão, que a regra da `113` produz) |
| FR-4353 (tudo advertência) | T006, T013 | `te::test_o_recurso_que_impediria_o_edital_e_advertencia_no_processo` |
| FR-4354 (o relatório, sem faltar nem sobrar; o cancelado sem resultado) | T006, T012 | `te::test_as_frases_sao_as_da_confirmacao_do_edital_e_do_relatorio`; `te::test_os_editais_em_ordem_sem_o_nunca_publicado_e_sem_os_que_nada_tem` (o 63 cancelado) |
| FR-4355 (o caminho só a quem a tela aceita) | T006 (por `_item`) | `te::test_o_recurso_que_impediria_o_edital_e_advertencia_no_processo` |
| FR-4356 (sem dado pessoal) | T006, T022 | `te::test_nenhum_dado_pessoal_na_confirmacao` |
| FR-4357 (só quando confirmável) | T009, T021 | `te::test_com_edital_fora_de_estado_final_nada_e_lido`; `te::test_processo_encerrado_por_outra_sessao_nao_mostra_o_bloco`; `te::test_cancelar_processo_nao_tem_o_bloco` |
| FR-4358 (sem os vazios e os nunca publicados; a ordem) | T006 | `te::test_os_editais_em_ordem_sem_o_nunca_publicado_e_sem_os_que_nada_tem` |
| FR-4359 (nada em aberto, sem prometer) | T019 | `te::test_sem_nada_em_aberto_a_frase_nao_promete_conclusao` |
| FR-4360 (relida na reexibição, só se confirmável) | T021 | `te::test_motivo_vazio_volta_com_o_bloco_lido_uma_vez`; `te::test_depois_do_422_a_mudanca_volta_pela_renovacao`; `te::test_processo_encerrado_por_outra_sessao_nao_mostra_o_bloco` |
| FR-4361 (um instante só) | T009 | leitura de `views._situacao_do_ato_processo`, que abre `leitura_consistente()` em volta de `do_processo` e a fecha antes do comando; `de::*` lê dentro do mesmo bloco |
| FR-4362 (o comando não muda) | T015, T017 | `pr` inteiro; `te::test_confirmar_com_a_lista_vista_encerra_e_grava_so_o_ato_de_hoje`; `te::test_processo_encerrado_por_outra_sessao_nao_mostra_o_bloco` (a recusa de hoje); diff sem `finalizacao.py` |
| FR-4363 (nada gravado além do motivo) | T008 | `te::test_confirmar_com_a_lista_vista_encerra_e_grava_so_o_ato_de_hoje`; `te::test_a_lista_mudou_a_confirmacao_volta_sem_encerrar` |
| FR-4364 (o resto não muda) | T012, T014, T023 | `te::test_cancelar_processo_nao_tem_o_bloco`; `te::test_cancelar_processo_sem_resumo_segue_como_hoje`; `de::test_a_lista_e_o_detalhe_nao_leem_a_advertencia`; `interface/test_confirmacao_do_encerramento.py` inteiro (a tela do Edital) |
| FR-4365 (o resumo e a renovação) | T014, T015, T016 | `un::test_a_mesma_lista_da_o_mesmo_resumo` a `un::test_o_caminho_nao_entra_no_resumo`, inclusive `un::test_a_ordem_das_frases_dentro_do_edital_nao_muda_o_resumo`; `te::test_a_lista_mudou_a_confirmacao_volta_sem_encerrar`; `te::test_a_renovacao_vem_antes_do_motivo`; `te::test_o_prazo_que_vence_com_a_tela_aberta_renova_a_confirmacao` |
| FR-4366 (renovação não é barreira; nada gravado; a chave) | T015 | `te::test_confirmar_de_novo_encerra_mesmo_com_providencia_em_aberto`; `te::test_a_lista_mudou_a_confirmacao_volta_sem_encerrar` (mesma chave, nenhum ato) |
| FR-4367 (nenhuma frase promete o que a janela não garante) | T015, T016 | leitura das frases UX-275 a UX-279 no template; o comentário da view nomeia a janela |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1320 | `te::test_o_bloco_mostra_a_convocacao_no_prazo_antes_das_consequencias` |
| SC-1321 | `te::test_as_frases_sao_as_da_confirmacao_do_edital_e_do_relatorio`; `te::test_os_editais_em_ordem_sem_o_nunca_publicado_e_sem_os_que_nada_tem` |
| SC-1322 | `pr` inteiro; `te::test_processo_encerrado_por_outra_sessao_nao_mostra_o_bloco` |
| SC-1323 | `te::test_nenhum_dado_pessoal_na_confirmacao` |
| SC-1324 | `de::test_o_numero_de_consultas_nao_cresce_com_as_inscricoes`; `de::test_cada_edital_a_mais_custa_o_mesmo`; `de::test_a_lista_e_o_detalhe_nao_leem_a_advertencia` |
| SC-1325 | `makemigrations --check` (verificação); `te::test_cancelar_processo_nao_tem_o_bloco` |
| SC-1326 | a suíte inteira (verificação) |
| SC-1327 | `te::test_a_lista_mudou_a_confirmacao_volta_sem_encerrar`; `te::test_confirmar_de_novo_encerra_mesmo_com_providencia_em_aberto`; `te::test_sem_nada_em_aberto_a_frase_nao_promete_conclusao` (sem mudança, encerra na primeira) |

## Experiência

| Requisito | Testes |
|---|---|
| UX-275 | `te::test_o_bloco_mostra_a_convocacao_no_prazo_antes_das_consequencias`; `cq` (a) |
| UX-276 | `te::test_o_bloco_mostra_a_convocacao_no_prazo_antes_das_consequencias`; `un::test_convocado_no_prazo_so_com_convocacao_aguardando`; `te::test_a_lista_mudou_a_confirmacao_volta_sem_encerrar` (some quando a convocação é respondida) |
| UX-277 | `te::test_sem_nada_em_aberto_a_frase_nao_promete_conclusao`; `cq` (c), (e) |
| UX-278 | `te::test_os_editais_em_ordem_sem_o_nunca_publicado_e_sem_os_que_nada_tem` |
| UX-279 | `te::test_a_lista_mudou_a_confirmacao_volta_sem_encerrar`; `cq` (c) |
