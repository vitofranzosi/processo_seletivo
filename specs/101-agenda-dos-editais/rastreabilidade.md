# Rastreabilidade: Agenda dos Editais

Cada requisito → a tarefa que o implementa → o teste que o verifica. Conferida contra o implementado
em 29/10/2026. As tarefas estão em [tasks.md](tasks.md). Caminhos de teste relativos a `backend/`:
`UNI` é `tests/unit/interface/test_agenda.py`, `INT` é `tests/integration/agenda/test_fonte.py`,
`TELA` é `tests/interface/test_agenda.py`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2609 (toda identidade, pela barra, sem papel novo) | T011, T012 | `tests/interface/test_shell_da_gestao.py::test_os_itens_sao_exatamente_os_destinos_que_abrem` (todo papel, inclusive nenhum); `TELA::test_sem_edital_publicado_a_pagina_diz_e_nao_desenha_a_grade` (identidade sem papel) |
| FR-2610 (só o escopo; identificador alheio ignorado sem distinção) | T008, T022 | `INT::test_edital_de_outro_escopo_nao_aparece_nem_pelo_filtro`; `TELA::test_identificador_alheio_e_ignorado_sem_recusa` |
| FR-2611 (só leitura) | T011, T013 | `TELA::test_so_leitura_o_unico_formulario_e_o_dos_filtros`; por construção: `interface/agenda.py` não grava |
| FR-2612 (versão vigente; nunca elaboração nem submissão) | T008 | `INT::test_edital_publicado_entra_e_em_elaboracao_nao` |
| FR-2613 (Retificação vigente na leitura seguinte; Evento acrescentado) | T008 | `INT::test_retificacao_vigente_muda_a_data_na_leitura_seguinte`, `::test_evento_acrescentado_por_retificacao_aparece` |
| FR-2614 (vigência futura anunciada, não aplicada) | T008, T013 | `INT::test_retificacao_de_vigencia_futura_e_anunciada_e_nao_aplicada`; `TELA::test_o_aviso_da_retificacao_a_vigorar` |
| FR-2615 (publicado e encerrado; cancelado fora; encerrado só o que passou) | T004, T008 | `INT::test_edital_cancelado_some_e_encerrado_so_mostra_o_que_passou`; `UNI::test_edital_encerrado_mostra_so_o_evento_que_ja_passou` |
| FR-2616 (dia na zona institucional) | T004 | `UNI::test_o_dia_e_o_da_zona_institucional_e_nao_o_de_utc` |
| FR-2617 (fase pela régua existente) | T004 | `UNI::test_a_fase_e_dita_sem_afirmar_execucao`, `::test_periodo_de_inscricoes_sem_termino_segue_em_curso_pela_regua_do_periodo`, `::test_marcos_de_periodo_tem_a_posicao_do_proprio_instante` |
| FR-2618 (pontual: um marco, com hora; meia-noite sem hora) | T004 | `UNI::test_evento_sem_termino_e_um_marco_no_seu_dia_com_a_hora`, `::test_termino_no_mesmo_dia_e_pontual_com_as_duas_horas`, `::test_meia_noite_sem_termino_nao_inventa_hora`, `::test_evento_comum_sem_termino_e_pontual_e_nao_periodo_aberto` |
| FR-2619 (período: abertura e encerramento, nada no meio) | T004, T013 | `UNI::test_periodo_lanca_abertura_e_encerramento_e_nada_entre_eles`; `TELA::test_o_periodo_nao_ocupa_os_dias_do_meio_e_aparece_uma_vez_na_lista` |
| FR-2620 (sem término, sem encerramento presumido) | T004 | `UNI::test_periodo_de_inscricoes_sem_termino_so_abre` |
| FR-2621 (cancelado: na lista, fora da grade e dos números) | T004, T006, T010, T016 | `UNI::test_cancelado_e_marcado_e_continua_na_projecao`, `::test_dia_so_com_cancelado_nao_tem_contagem`, `::test_sintese_conta_o_exibido_sem_os_cancelados`; `TELA::test_o_mes_conta_destaca_e_nomeia_dois_sem_o_cancelado`, `::test_o_dia_lista_todos_os_marcos_com_os_dois_destinos`, `::test_a_sintese_de_proximos_nao_conta_o_cancelado` |
| FR-2622 (nome publicado; nenhuma classificação por palavra) | T004 | `UNI::test_o_nome_e_a_descricao_publicada_ou_a_especie`, `::test_especie_vem_das_marcas_estruturais_e_o_periodo_prevalece` |
| FR-2623 (mês inicial e navegação) | T008, T013 | `TELA::test_o_dia_de_um_marco_so_nao_e_destacado_e_hoje_e_marcado`, `::test_mes_invalido_cai_no_corrente_e_a_navegacao_leva_aos_vizinhos` |
| FR-2624 (domingo a sábado, 4 a 6 semanas, tabela) | T009, T010, T013 | `UNI::test_a_grade_tem_as_semanas_que_o_mes_ocupa`, `::test_a_semana_comeca_no_domingo_e_os_dias_de_fora_ficam_vazios`; `TELA::test_o_mes_conta_destaca_e_nomeia_dois_sem_o_cancelado` |
| FR-2625 (contagem, destaque a partir de dois, data por extenso, hoje) | T009, T010, T013, T014 | `UNI::test_a_celula_conta_destaca_e_nomeia_dois_na_ordem_do_dia`; `TELA::test_o_mes_conta_destaca_e_nomeia_dois_sem_o_cancelado`, `::test_o_dia_de_um_marco_so_nao_e_destacado_e_hoje_e_marcado`, `::test_o_acesso_ao_dia_diz_a_data_por_extenso` |
| FR-2626 (até dois nomes na ordem do dia, em até duas linhas; só a contagem no estreito) | T010, T014, T030 | `UNI::test_a_celula_conta_destaca_e_nomeia_dois_na_ordem_do_dia`; `TELA::test_o_mes_conta_destaca_e_nomeia_dois_sem_o_cancelado`; 375 px no navegador (quickstart) |
| FR-2627 (períodos do mês, uma vez; cancelado fora; aberto toca os meses seguintes) | T006, T013 | `UNI::test_periodos_ditos_uma_vez_sem_os_cancelados`, `::test_periodo_toca_e_contem_um_dia`, `::test_periodo_aberto_sem_termino_toca_todo_mes_depois_do_inicio`; `TELA::test_o_periodo_nao_ocupa_os_dias_do_meio_e_aparece_uma_vez_na_lista` |
| FR-2628 (o dia: todos os marcos, períodos em curso nele, volta ao mês) | T016, T017 | `TELA::test_o_dia_lista_todos_os_marcos_com_os_dois_destinos`, `::test_dia_invalido_e_ignorado`; `UNI::test_periodo_toca_e_contem_um_dia` |
| FR-2629 (conteúdo do item e os dois destinos; *Edital encerrado*) | T016 | `TELA::test_o_dia_lista_todos_os_marcos_com_os_dois_destinos`, `::test_o_marco_de_edital_encerrado_se_diz_encerrado` |
| FR-2630 (mais de oito, agrupados por Edital) | T006, T016 | `UNI::test_dia_com_mais_de_oito_marcos_agrupa_por_edital_e_ate_oito_nao` |
| FR-2631 (7 e 30 dias, desde o começo de hoje) | T006, T019 | `UNI::test_janela_proxima_comeca_no_comeco_do_dia_de_hoje`, `::test_o_marco_de_hoje_que_ja_passou_continua_na_janela`; `TELA::test_proximos_sete_dias_com_o_periodo_em_curso_uma_vez`, `::test_trinta_dias_alcanca_mais_e_nao_tudo` |
| FR-2632 (por dia, com a quantidade e os cancelados; ordem instante → Edital → nome) | T006, T019, T031 | `UNI::test_ordem_do_dia_e_instante_depois_edital_depois_nome`, `::test_o_dia_conta_os_cancelados_a_parte`; `TELA::test_o_dia_lista_todos_os_marcos_com_os_dois_destinos`; `TELA::test_o_mes_conta_destaca_e_nomeia_dois_sem_o_cancelado` (a ordem na célula) |
| FR-2633 (bloco *em curso*, uma vez, com o tempo que falta) | T006, T019 | `UNI::test_o_tempo_que_falta_e_em_dias_corridos`; `TELA::test_proximos_sete_dias_com_o_periodo_em_curso_uma_vez` |
| FR-2634 (os quatro números da janela, sem cancelados) | T006, T013 | `UNI::test_sintese_conta_o_exibido_sem_os_cancelados`, `::test_sem_dia_com_mais_de_um_marco_nao_ha_dia_mais_carregado`; `TELA::test_a_sintese_de_proximos_nao_conta_o_cancelado`, `::test_o_filtro_segue_nas_abas_nos_dias_e_na_sintese` |
| FR-2635 (soma das células = síntese do mês) | T009, T010 | `UNI::test_a_soma_das_celulas_e_a_sintese_do_mes`; `TELA::test_a_soma_das_celulas_e_a_sintese` |
| FR-2636 (síntese sem linguagem de trabalho) | T013, T018 | `TELA::test_nenhuma_visualizacao_afirma_execucao` |
| FR-2637 (filtros de Edital e espécie; opções; mesma aplicação nas telas) | T006, T008, T021 | `UNI::test_filtros_de_edital_e_de_especie`; `INT::test_edital_publicado_entra_e_em_elaboracao_nao` (opções); `TELA::test_o_filtro_segue_nas_abas_nos_dias_e_na_sintese`, `::test_janela_vazia_nomeia_o_proximo_marco_com_os_filtros` |
| FR-2638 (filtros preservados; estado no endereço) | T008, T021 | `TELA::test_o_filtro_segue_nas_abas_nos_dias_e_na_sintese` |
| FR-2639 (sem filtro de unidade, modalidade ou categoria) | T021 | `TELA::test_nao_ha_filtro_de_unidade_modalidade_ou_categoria` |
| FR-2640 e FR-2641 (previsto; o efetivo pode diferir e não é exibido) | T013 | `TELA::test_nenhuma_visualizacao_afirma_execucao` |
| FR-2642 (*data passada*, nunca executado) | T004, T018 | `UNI::test_a_fase_e_dita_sem_afirmar_execucao`; `TELA::test_nenhuma_visualizacao_afirma_execucao`, `::test_o_marco_de_edital_encerrado_se_diz_encerrado` |
| FR-2643 (instante da leitura) | T013 | `TELA::test_nenhuma_visualizacao_afirma_execucao` (o "lido em") |
| FR-2644 (os três estados vazios; o próximo marco) | T008, T013, T019 | `TELA::test_sem_edital_publicado_a_pagina_diz_e_nao_desenha_a_grade`, `::test_janela_vazia_nomeia_o_proximo_marco_com_os_filtros`, `::test_identificador_alheio_e_ignorado_sem_recusa` |
| FR-2645 (WCAG e eMAG; 375 px) | T013, T014, T026 | `tests/interface/test_acessibilidade.py`, `test_politica_de_conteudo.py`, `test_larguras.py`, `test_folha_estatica.py` (todos varrem `agenda.html` e os parciais); `TELA::test_o_acesso_ao_dia_diz_a_data_por_extenso`, `::test_o_filtro_segue_nas_abas_nos_dias_e_na_sintese` (aba ativa); 375 px medido no navegador (quickstart) |
| FR-2646 (consultas fixas, iguais nas visualizações) | T008, T023 | `TELA::test_as_consultas_nao_crescem_com_os_editais` |
| SC-948 (sessão observada) | — | **pendente**: depende de pessoa que gere Processos; não verificável por teste |
| SC-949 (nenhum marco de rascunho, cancelado ou outra unidade) | T008 | `INT::test_edital_publicado_entra_e_em_elaboracao_nao`, `::test_edital_cancelado_some_e_encerrado_so_mostra_o_que_passou`, `::test_edital_de_outro_escopo_nao_aparece_nem_pelo_filtro` |
| SC-950 (custo constante) | T023, T025 | `TELA::test_as_consultas_nao_crescem_com_os_editais` (1 × 5); medição com 1, 10 e 30 no quickstart |
| SC-951 (soma = síntese; todo marco da célula no dia) | T009, T017 | `UNI::test_a_soma_das_celulas_e_a_sintese_do_mes`; `TELA::test_a_soma_das_celulas_e_a_sintese`, `::test_o_dia_lista_todos_os_marcos_com_os_dois_destinos` |
| SC-952 (Retificação vigente e futura) | T007 | `INT::test_retificacao_vigente_muda_a_data_na_leitura_seguinte`, `::test_retificacao_de_vigencia_futura_e_anunciada_e_nao_aplicada` |
| SC-953 (guardiões e 375 px) | T014, T015, T026 | os guardiões de FR-2645; 375 px sem rolagem medido no mês, no dia e em Próximos marcos (quickstart) |
