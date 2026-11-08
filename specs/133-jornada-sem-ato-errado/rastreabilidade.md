# Rastreabilidade: A jornada não aponta o ato errado (133)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `ru` = `unit/classificacao/test_marco_intermediario.py`: a regra e a recusa, sem banco
- `oc` = `integration/ocupacao/test_apuracao_em_marco_intermediario.py`: os comandos da ocupação
- `cv` = `integration/convocacao/test_convocacao_em_marco_intermediario.py`: os comandos da convocação
- `an` = `interface/test_andamento_marco_intermediario.py`: a derivação nas paradas do Edital 900 reduzido
- `tl` = `interface/test_telas_do_marco_intermediario.py`: as telas e o POST direto
- `ec` = `interface/test_espera_do_corte.py`: a espera do corte no cartão e na tela
- `si` = `unit/interface/test_andamento_situacoes.py`: as funções puras da derivação
- `fr` = `unit/publicacoes/test_redacao_das_frases.py`: a frase do corte
- `dg` = `unit/publicacoes/test_documento_da_auditoria_depois_da_133.py`: o guardião da diferença dos documentos
- `cq` = capturas antes (estudo de 07/11) e depois (`capturas/`), e a sonda nos bancos de fase ([verificacao.md](verificacao.md))

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4530 (a definição) | T003, T004 | `ru::test_o_marco_que_governa_a_etapa_que_o_final_le_e_intermediario`; `ru::test_o_marco_final_nao_e_intermediario`; `ru::test_o_sorteio_seguido_de_habilitacao_que_ninguem_le_nao_e_intermediario`; `ru::test_o_sorteio_cuja_etapa_governada_outro_marco_le_e_intermediario`; `ru::test_o_marco_sem_etapa_governada_seguido_de_outro_nao_e_intermediario`; `ru::test_tres_marcos_em_cadeia` |
| FR-4531 (uma regra só) | T004, T005, T014, T015 | os comandos, a condução e as views chamam `classificacao.application.marco_intermediario`; `tl::test_o_gesto_apurar_da_conducao_poe_os_recortes_entre_os_impedidos` usa a mesma frase da recusa |
| FR-4532 (apurar) | T011 | `oc::test_apurar_o_marco_intermediario_e_recusado_sem_gravar`; `oc::test_a_apuracao_do_marco_final_continua_aceita` |
| FR-4533 (acréscimo e faixa por déficit) | T012 | `oc::test_acrescentar_vaga_no_marco_intermediario_e_recusado`; `oc::test_a_faixa_por_deficit_de_uma_apuracao_legada_e_recusada` |
| FR-4534 (convocar, lote, correção) | T013 | `cv::test_convocar_no_marco_intermediario_e_recusado_sem_gravar_nem_comunicar`; `cv::test_o_lote_de_titulares_no_marco_intermediario_e_recusado`; `cv::test_a_correcao_de_convocacao_legada_e_recusada` |
| FR-4535 (encerrar o legado) | T013 | `cv::test_a_convocacao_legada_ainda_recebe_desfecho` |
| FR-4536 (nada gravado, chave livre) | T011 a T013 | `oc::test_apurar_o_marco_intermediario_e_recusado_sem_gravar`; `oc::test_repetir_o_pedido_recusado_recusa_de_novo`; `cv::test_convocar_no_marco_intermediario_e_recusado_sem_gravar_nem_comunicar` |
| FR-4537 (código e frase) | T005 | `ru::test_o_impedimento_nomeia_o_marco_a_etapa_e_o_marco_que_apura`; `ru::test_a_recusa_tem_codigo_proprio` |
| FR-4538 (as telas preveem) | T014, T015 | `tl::test_a_ocupacao_do_marco_intermediario_nao_oferece_ato`; `tl::test_a_convocacao_do_marco_intermediario_nao_oferece_ato`; `tl::test_as_telas_do_marco_final_continuam_iguais`; `tl::test_o_gesto_apurar_da_conducao_poe_os_recortes_entre_os_impedidos`; `cq` |
| FR-4539 (*Não se aplica* no andamento) | T014, T016 | `an::test_depois_da_apuracao_do_marco_final_so_as_convocacoes_dele_sao_providencia`; `an::test_o_resumo_do_perfil_nao_conta_a_apuracao_do_marco_intermediario` |
| FR-4540 (o legado legível) | T008 | `cv::test_a_convocacao_legada_ainda_recebe_desfecho`; `oc::test_a_faixa_por_deficit_de_uma_apuracao_legada_e_recusada` (a apuração legada continua) |
| FR-4541 (quando o corte espera) | T020, T021 | `si::test_sem_recurso_declarado_o_corte_nao_espera`; `si::test_sem_divulgacao_o_corte_espera_sem_data`; `si::test_com_o_prazo_ou_o_recurso_em_aberto_o_corte_espera`; `si::test_prazo_encerrado_sem_pendencia_e_sem_definitiva_o_corte_nao_espera` |
| FR-4542 (recomendação, data, consequência) | T020, T022 | `si::test_o_corte_em_espera_e_recomendacao_e_nao_e_de_ninguem`; `ec::test_o_cartao_mostra_o_corte_em_espera_com_a_marca_de_recomendacao`; `cq` |
| FR-4543 (não é "sua"; o próximo destrava) | T021 | `an::test_depois_da_ordem_o_proximo_e_divulgar_e_o_corte_espera`; `an::test_com_a_preliminar_publicada_o_corte_espera_o_prazo_e_nao_e_seu` |
| FR-4544 (a tela do corte) | T023 | `ec::test_a_tela_do_corte_diz_a_consequencia_antes_do_botao_e_o_botao_continua` |
| FR-4545 (o comando não muda) | T023 | `ec::test_emitir_o_corte_na_espera_continua_aceito` |
| FR-4546 (a mesma aferição) | T020, T021, T023 | `andamento.leitura_da_definitiva` é lida pelo andamento e pela view do corte; `si::test_o_corte_feito_ou_obsoleto_ignora_a_espera` |
| FR-4547 (a conta das vagas sem chamada) | T025 | `an::test_depois_da_desistencia_a_proxima_da_fila_e_providencia`; `an::test_com_chamada_aberta_para_a_vaga_que_vagou_nao_se_chama_outra` |
| FR-4548 (chamar a próxima é sua) | T025 | `an::test_depois_da_desistencia_a_proxima_da_fila_e_providencia` |
| FR-4549 (tela e cartão concordam) | T024 | `an::test_a_tela_da_convocacao_e_o_cartao_apontam_a_mesma_proxima` |
| FR-4550 (ordem obsoleta, publicação feita) | T031 | `si::test_com_a_preliminar_feita_e_a_ordem_obsoleta_a_definitiva_e_depois`; `an::test_com_a_ordem_obsoleta_a_definitiva_nao_e_pendente_para_quem_publica` |
| FR-4551 (corte obsoleto) | T030 | `si::test_com_o_corte_obsoleto_a_definitiva_e_impedida_e_nao_pendente` |
| FR-4552 (nunca *Pendente* do que o comando recusa) | T030, T032 | `an::test_com_a_ordem_obsoleta_a_definitiva_nao_e_pendente_para_quem_publica`; as recusas confirmadas em cópia descartável no estudo, e a sonda depois da mudança (`cq`) |
| FR-4553 (de cada lista) | T026, T028 | `fr::test_o_alvo_fixo_com_reservada_diz_de_cada_lista`; `fr::test_o_alvo_de_um_com_reservada_diz_de_cada_lista_no_singular`; `fr::test_a_lista_reservada_vem_da_derivacao_dos_recortes`; `dg::test_a_diferenca_para_a_096_e_so_o_complemento_de_cada_lista` |
| FR-4554 (só a ampla) | T026 | `fr::test_o_alvo_fixo_so_com_a_ampla_continua_como_era`; `fr::test_o_alvo_do_quadro_nao_muda_com_reservada` |
| FR-4555 (o publicado não muda) | T027 | `integration/publicacoes/test_acervo_da_069.py::test_o_documento_publicado_antes_e_servido_com_os_bytes_gravados` (guardião existente); nenhuma rotina desta feature recompõe documento |
| FR-4556 (a Retificação não acusa a redação) | T027 | por construção: o quadro de alterações vem das mudanças do conteúdo (`publicacoes/domain/alteracoes.py`, `alteracoes_legiveis(conteudo_base, alteracoes)`), e nunca da prosa composta; registrado em [verificacao.md](verificacao.md) |
| FR-4557 (os quatro instantes) | T006, T009, T018, T024, T030 | `an` inteiro; `cq` (a sonda no Edital 900 completo) |
| FR-4558 (recusa direto no comando) | T007, T008 | `oc`, `cv` |
| FR-4559 (a `127` sem mudança) | T033 | suíte completa: os testes da `127` (`unit/interface/test_andamento_*.py`, `interface/test_andamento_do_edital.py`) passam sem mudança de expectativa |

## Critérios de sucesso

| Critério | Como se verifica |
|---|---|
| SC-1420 | `oc`, `cv` e `tl::test_o_post_direto_a_apuracao_e_recusado_e_nada_e_gravado`, `tl::test_o_post_direto_a_convocacao_e_recusado_e_nada_e_gravado` |
| SC-1421 | `an::test_depois_da_apuracao_do_marco_final_so_as_convocacoes_dele_sao_providencia`; a sonda em `ps_conv_t5` e `ps_conv_ux` (`cq`) |
| SC-1422 | `an::test_com_a_preliminar_publicada_o_corte_espera_o_prazo_e_nao_e_seu`; `ec`; a sonda em `ps_conv_t2` |
| SC-1423 | `an::test_depois_da_desistencia_a_proxima_da_fila_e_providencia`; a sonda em `ps_conv_t6` |
| SC-1424 | `an::test_com_a_ordem_obsoleta_a_definitiva_nao_e_pendente_para_quem_publica`; a sonda em `ps_conv_t3` |
| SC-1425 | FR-4555 |
| SC-1426 | FR-4556 |
| SC-1427 | suíte completa contra PostgreSQL ([verificacao.md](verificacao.md)) |
| SC-1428 | `makemigrations --check --dry-run`: *No changes detected* |
