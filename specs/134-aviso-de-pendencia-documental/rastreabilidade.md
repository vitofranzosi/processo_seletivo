# Rastreabilidade: O aviso de pendência documental por e-mail (134)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`. Abreviações:

- `ap` = `integration/avisos/test_aviso_de_pendencia.py` — o gesto, as exclusões, o texto, o
  despacho, a publicação, a chave e as telas
- `tp` = `unit/avisos/test_texto_da_pendencia.py` — o texto como função pura
- `sm` = `test_situacoes_de_mensagem.py` — a guarda da FR-084

A faixa abre em **FR-4601**, **SC-1441** e **UX-311**, e as três foram gastas. A reserva vai
até o requisito quatro mil seiscentos e quarenta e o critério mil quatrocentos e cinquenta; o que passa de FR-4623, SC-1449 e UX-313 não foi gasto.

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-4601 — a quinta situação na FR-084, as redações anteriores ao fim | T001, T002 | `sm::test_a_revisao_da_134_esta_na_norma_escrita` |
| FR-4602 — cinco situações, a data conferida, um módulo só | T003, T004 | `sm::test_sao_cinco_situacoes_e_a_quinta_e_o_aviso_de_pendencia`, `sm::test_nenhum_modulo_envia_fora_das_situacoes_declaradas` |
| FR-4603 — o gesto, para quem confere ou gere | T009, T012 | `ap::test_o_gesto_grava_um_aviso_por_pessoa_com_pendencia_e_nada_sai_no_clique` (alocado), `ap::test_quem_gere_a_comissao_tambem_avisa`, `ap::test_quem_so_le_a_conducao_nao_avisa` |
| FR-4604 — só por gesto | T009 | `ap::test_registrar_a_pendencia_nao_grava_aviso` |
| FR-4605 — a prévia na tela | T012 | `ap::test_a_conducao_oferece_o_gesto_e_o_post_responde_o_ato` |
| FR-4606 — as condições de quem é alcançado | T009 | `ap::test_com_desfecho_nao_ha_aviso`, `ap::test_vencimento_decorrido_nao_ha_aviso`, `ap::test_vale_na_convocacao_por_publicacao` (não comunicada), `ap::test_um_aviso_por_pessoa_por_chamada_por_dia`, `ap::test_quem_nunca_teve_pendencia_nao_entra_nem_na_contagem` |
| FR-4607 — o complementado fica de fora | T009 | `ap::test_item_reenviado_depois_da_pendencia_nao_entra`, `ap::test_so_o_item_ainda_pendente_entra_no_texto` |
| FR-4608 — sem endereço, contado à parte | T009 | `ap::test_sem_endereco_fica_de_fora_contado_a_parte` |
| FR-4609 — ninguém alcançado, recusa sem gravar | T009 | `ap::test_com_desfecho_nao_ha_aviso`, `ap::test_item_reenviado_depois_da_pendencia_nao_entra` |
| FR-4610 — chave desligada e Processo final | T009, T019 | `ap::test_com_a_chave_desligada_nada_se_grava_nem_sai`, `ap::test_processo_em_estado_final_recusa_o_gesto` |
| FR-4611 — trava e idempotência | T009 | `ap::test_o_duplo_clique_devolve_o_primeiro`; a trava é a do Processo, provada pela `066` |
| FR-4612 — também por publicação | T009 | `ap::test_vale_na_convocacao_por_publicacao` |
| FR-4613 — o assunto | T007 | `tp::test_o_assunto_nao_comeca_por_convocacao_e_o_rodape_e_fixo`, `ap::test_o_texto_nomeia_o_documento_e_oculta_o_de_modalidade` |
| FR-4614 — o nome, e o de modalidade como frase | T007 | `tp::test_um_documento_de_modalidade_e_uma_frase_so`, `tp::test_dois_de_modalidade_viram_uma_linha_com_a_contagem`, `ap::test_o_texto_nomeia_o_documento_e_oculta_o_de_modalidade` |
| FR-4615 — o vencimento e o link | T007 | `tp::test_o_prazo_tem_dia_data_e_hora_e_nenhuma_contagem`, `tp::test_sem_vencimento_o_prazo_e_o_da_convocacao`, `ap::test_o_texto_diz_o_vencimento_sem_contagem` |
| FR-4616 — sem motivo, nome, CPF, protocolo, modalidade, anexo | T007 | `ap::test_o_texto_nomeia_o_documento_e_oculta_o_de_modalidade`, `ap::test_o_cpf_nao_vai_ao_texto` |
| FR-4617 — o rodapé fixo | T007 | `tp::test_o_assunto_nao_comeca_por_convocacao_e_o_rodape_e_fixo` |
| FR-4618 — um aviso por pessoa, sem `ComunicacaoEmitida` nem prazo | T005, T006, T009 | `ap::test_o_gesto_grava_um_aviso_por_pessoa_com_pendencia_e_nada_sai_no_clique`, `ap::test_o_despacho_envia_e_a_trilha_registra_o_gesto_e_o_envio` |
| FR-4619 — o despacho da `066` | T010 | `ap::test_o_despacho_envia_e_a_trilha_registra_o_gesto_e_o_envio`, `ap::test_com_a_chave_desligada_o_despacho_nao_envia_o_que_ja_foi_gravado` |
| FR-4620 — a trilha do gesto | T009 | `ap::test_o_despacho_envia_e_a_trilha_registra_o_gesto_e_o_envio` |
| FR-4621 — a trilha de cada envio | T010, T017, T019 | `ap::test_o_despacho_envia_e_a_trilha_registra_o_gesto_e_o_envio`, `ap::test_a_tentativa_orfa_tambem_vai_a_trilha`, `ap::test_a_trilha_que_falha_nao_desfaz_o_resultado` |
| FR-4622 — no histórico, sem reenvio | T011, T012 | `ap::test_o_historico_do_edital_nomeia_a_pendencia`, `ap::test_o_reenvio_da_066_recusa_o_aviso_de_pendencia` |
| FR-4623 — o despacho relê a pendência antes de enviar | T016 | `ap::test_o_despacho_interrompe_o_aviso_cuja_pendencia_foi_resolvida`, `ap::test_o_despacho_interrompe_o_aviso_vencido_antes_do_envio`, `ap::test_o_despacho_interrompe_o_aviso_cuja_lista_mudou`, `ap::test_o_aviso_interrompido_pelo_despacho_nao_conta_no_dia` |

## Requisitos de experiência

| Requisito | Tarefa | Teste |
|---|---|---|
| UX-311 — a seção e o que ela diz antes do botão | T012 | `ap::test_a_conducao_oferece_o_gesto_e_o_post_responde_o_ato` |
| UX-312 — a resposta nomeia o ato | T012 | `ap::test_a_conducao_oferece_o_gesto_e_o_post_responde_o_ato` |
| UX-313 — chave desligada, sem botão | T012 | `ap::test_a_conducao_com_a_chave_desligada_nao_oferece_o_botao` |

## Critérios de sucesso

| Critério | Verificação |
|---|---|
| SC-1441 | `ap` — o gesto e as exclusões, um caso por exclusão |
| SC-1442 | `ap::test_um_aviso_por_pessoa_por_chamada_por_dia`, `ap::test_o_limite_e_da_chamada_e_nao_de_quem_foi_avisado` |
| SC-1443 | `ap::test_o_texto_nomeia_o_documento_e_oculta_o_de_modalidade`, `ap::test_o_cpf_nao_vai_ao_texto` |
| SC-1444 | `ap::test_vale_na_convocacao_por_publicacao` |
| SC-1445 | `ap::test_com_a_chave_desligada_nada_se_grava_nem_sai` |
| SC-1446 | `sm::test_sao_cinco_situacoes_e_a_quinta_e_o_aviso_de_pendencia`, `sm::test_a_revisao_da_134_esta_na_norma_escrita` |
| SC-1447 | `ap::test_o_despacho_envia_e_a_trilha_registra_o_gesto_e_o_envio`, `ap::test_vale_na_convocacao_por_publicacao` |
| SC-1448 | A migration `avisos/0002`; `make check` (`makemigrations --check`) e o `N de M` do provisionamento, sem mudança |
| SC-1449 | `ap::test_o_despacho_interrompe_o_aviso_cuja_pendencia_foi_resolvida`, `ap::test_o_despacho_interrompe_o_aviso_vencido_antes_do_envio`, `ap::test_o_despacho_interrompe_o_aviso_cuja_lista_mudou`, `ap::test_o_aviso_interrompido_pelo_despacho_nao_conta_no_dia` |
