# Rastreabilidade — 047 · Situação pública e histórico oficial do Edital em execução

Uma linha por requisito, critério de sucesso, caso-limite e decisão, com o teste ou o percurso que
o prende. Caminhos de teste relativos a `backend/tests/`.

## Faixa de identificadores

| Identificador | Situação |
|---|---|
| **FR-760** | aberto no cabeçalho da spec e gasto como primeiro requisito (linha abaixo) |
| **SC-282** | aberto no cabeçalho da spec e gasto como primeiro critério (linha abaixo) |

## Requisitos funcionais

| Requisito | Onde se implementa | Teste que o prende |
|---|---|---|
| FR-760 | `processos/application/selectors.py` (`desfechos`); `portal/leitura.py` (`situacao_publica`); `_periodo.html` | `integration/portal/test_desfecho_publico.py`: `test_cancelado_dentro_do_periodo_diz_o_cancelamento_e_nao_aberta`, `test_encerrado_diz_encerrado_na_pagina_e_no_cartao_distinto_da_encerrada`, `test_processo_encerrado_com_edital_aberto_diz_o_fato_e_continua_recebendo`, `test_com_desfecho_o_registro_continua_na_pagina` |
| FR-761 | `_periodo.html`; `views.selecao`, `views._selecao_da_vitrine` (`dias_restantes`) | `test_desfecho_publico.py`: `test_cancelado_dentro_do_periodo_…`, `test_cancelado_com_periodo_por_abrir_nao_diz_em_breve` |
| FR-762 | `desfechos` (precedência); `Desfecho.do_edital`; `_periodo.html` | `test_desfecho_publico.py`: `test_processo_encerrado_com_edital_aberto_diz_o_fato_e_continua_recebendo`, `test_o_desfecho_do_edital_vence_o_do_processo`; `unit/processos/test_desfechos.py`: `test_o_edital_vence_o_processo`, `test_sem_desfecho_do_edital_vale_o_do_processo` |
| FR-763 | `leitura.estado_na_vitrine`, `agrupar_por_situacao`, `filtrar`; `_cartao_da_selecao.html` | `test_desfecho_publico.py`: `test_encerrado_diz_…_distinto_da_encerrada`, `test_encerrado_com_periodo_em_curso_fica_entre_as_encerradas`, `test_encerrado_com_periodo_por_abrir_nunca_vai_para_as_proximas`, `test_o_filtro_de_abertas_nao_devolve_o_encerrado`, `test_cancelado_continua_fora_da_vitrine_e_alcancavel_pelo_endereco` |
| FR-764 | `Desfecho` não carrega o motivo | `test_desfecho_publico.py::test_nem_o_motivo_nem_o_autor_do_ato_aparecem` |
| FR-765 | `editais/domain/fase_do_evento.py`; `leitura.cronograma` | `integration/portal/test_fase_do_cronograma.py`: `test_portal_e_gestao_dizem_a_mesma_fase_para_cada_evento`, `test_o_pontual_iniciado_ha_uma_hora_ja_e_concluido`, `test_o_evento_com_termino_em_curso_e_acontecendo_agora`, `test_o_acompanhamento_le_a_mesma_regua`; `unit/editais/test_fase_do_evento.py` |
| FR-766 | `leitura.situacao_do_evento`; `_cronograma.html` (classe `cancelado`) | `test_fase_do_cronograma.py::test_o_cancelado_e_dito_cancelado_e_nao_tem_fase`; `test_fase_do_evento.py::test_cancelado_nao_tem_fase`; `integration/portal/test_agora_e_proximo.py::test_o_cancelado_nunca_e_proximo` |
| FR-767 | `leitura.agora_e_proximo` sobre `marcos_pendentes`; `selecao.html` | `test_agora_e_proximo.py`: `test_o_proximo_e_o_de_inicio_mais_proximo`, `test_o_evento_em_curso_aparece_como_acontecendo_agora`, `test_os_empatados_no_inicio_aparecem_todos_na_ordem_publicada` |
| FR-768 | `agora_e_proximo` devolve listas vazias; o template omite o bloco | `test_agora_e_proximo.py`: `test_sem_evento_pendente_o_bloco_some_e_nada_e_inventado`, `test_edital_com_desfecho_nao_tem_bloco`; `unit/test_legado_da_projecao.py::test_cronograma_vazio_nao_inventa_agora_nem_proximo` |
| FR-769 | `recursos/application/selectors.py` (`janela_da_publicacao_divulgada`); `views.resultado`; `resultado.html` | `portal/test_prazo_recursal_publico.py`: `test_prazo_aberto_na_pagina_do_resultado_e_na_lista_do_edital`, `test_prazo_encerrado_diz_quando_e_some_da_lista`, `test_a_definitiva_do_mesmo_ato_diz_o_prazo_da_primeira_publicacao`, `test_a_sucedida_nao_diz_prazo` |
| FR-770 | `views.selecao` (`recurso_ate`); `selecao.html` | `test_prazo_recursal_publico.py`: `test_prazo_aberto_…_e_na_lista_do_edital`, `test_prazo_encerrado_diz_quando_e_some_da_lista` |
| FR-771 | `janela_da_publicacao_divulgada` devolve `None`; nenhum formulário | `test_prazo_recursal_publico.py`: `test_sem_janela_declarada_nada_se_diz_sobre_recurso`, `test_com_admits_false_nada_se_diz_sobre_recurso`, `test_nenhuma_acao_de_recorrer_em_caso_algum`; `portal/test_resultado_publico.py::test_a_pagina_nao_oferece_acao_de_recurso` |
| FR-772 | `divulgacao/application/selectors.py` (`historico_publico_do_edital`); `selecao.html` | `portal/test_historico_de_resultados.py`: `test_o_preliminar_sucedido_esta_a_um_clique_da_pagina_do_edital`, `test_a_cadeia_de_tres_aparece_em_ordem_e_so_a_ultima_e_vigente`, `test_o_historico_de_uma_lista_nao_aparece_sob_outra`; `test_resultado_publico.py::test_a_vitrine_do_edital_anuncia_so_a_vigente` |
| FR-773 | `anteriores_da_cadeia`; `resultado.html` | `test_historico_de_resultados.py`: `test_a_pagina_do_definitivo_leva_as_anteriores`, `test_a_publicacao_sem_anterior_nao_desenha_historico` |
| FR-774 | nenhuma escrita, migration ou campo novo | `integration/portal/test_leitura_sem_escrita.py` (3); T033: `migrate --check`, `makemigrations --check` sem mudança, `make preparar` em 34 de 34 |
| FR-775 | omitir o que falta | `unit/test_legado_da_projecao.py` (5); `test_desfechos.py::test_sem_ato_encontrado_o_desfecho_vem_sem_data`; `test_prazo_recursal_publico.py::test_sem_janela_declarada_…` |
| FR-776 | `Desfecho` sem autor; `historico_publico_do_edital` sem ato | `test_desfecho_publico.py::test_nem_o_motivo_nem_o_autor_do_ato_aparecem`; `test_historico_de_resultados.py::test_nenhum_identificador_de_ator_aparece`; `test_resultado_publico.py::test_a_pagina_nao_emite_consulta_as_tabelas_de_dado_individual` |

## Critérios de sucesso

| Critério | Como se verifica |
|---|---|
| SC-282 | Percurso pela tela (abaixo), percursos 1 e 2, contra o "antes" de `antes-da-047.md`; `test_desfecho_publico.py` |
| SC-283 | `test_fase_do_cronograma.py::test_portal_e_gestao_dizem_a_mesma_fase_para_cada_evento`; os três instantes em `test_fase_do_evento.py` |
| SC-284 | `test_prazo_recursal_publico.py::test_prazo_aberto_…`: a data da página é a de `objetos_recorriveis` para a mesma publicação |
| SC-285 | `test_historico_de_resultados.py::test_o_preliminar_sucedido_esta_a_um_clique_da_pagina_do_edital` |
| SC-286 | T033: nenhuma migration, 34 de 34 e nenhuma escrita; a suíte inteira passa sem nenhum Edital antigo deixar de abrir |
| SC-287 | `test_agora_e_proximo.py::test_o_proximo_e_o_de_inicio_mais_proximo` (o bloco vem antes do cronograma); percurso 4 |

## Casos-limite da spec

| Caso-limite | Teste |
|---|---|
| Cancelado com período ainda por abrir | `test_desfecho_publico.py::test_cancelado_com_periodo_por_abrir_nao_diz_em_breve` |
| Encerrado antes do fim do período declarado | `test_desfecho_publico.py::test_encerrado_com_periodo_em_curso_fica_entre_as_encerradas`; `test_com_desfecho_o_registro_continua_na_pagina` |
| Processo cancelado | `test_desfecho_publico.py::test_o_desfecho_do_edital_vence_o_do_processo` |
| Processo encerrado com Edital ainda publicado | `test_desfecho_publico.py::test_processo_encerrado_com_edital_aberto_diz_o_fato_e_continua_recebendo`: o fato e a data, sem *"não recebe inscrições"*, com *Aberta*, o prazo, *"Inscrever-se nesta vaga"*, o grupo das abertas e o filtro por abertas (regressão da revisão do #193) |
| Edital com desfecho e janela recursal ainda aberta | `test_prazo_recursal_publico.py::test_edital_encerrado_com_prazo_em_curso_continua_dizendo_o_prazo` |
| Período de inscrições marcado como cancelado | `test_fase_do_cronograma.py::test_o_periodo_marcado_como_cancelado_segue_a_regua_do_periodo`; `test_fase_do_evento.py::test_periodo_cancelado_a_gestao_le_o_cancelamento_e_o_portal_le_o_periodo` |
| Evento sem início | `test_fase_do_evento.py::test_sem_inicio_nao_tem_fase`; `test_legado_da_projecao.py::test_evento_sem_inicio_nao_tem_fase_nem_e_proximo` |
| Dois Eventos com o mesmo início | `test_agora_e_proximo.py::test_os_empatados_no_inicio_aparecem_todos_na_ordem_publicada` |
| Retificação publicada com vigência futura | `test_agora_e_proximo.py::test_retificacao_com_vigencia_futura_nao_muda_o_proximo_de_agora` |
| Resultado sucedido em outra lista do mesmo marco | `test_historico_de_resultados.py::test_o_historico_de_uma_lista_nao_aparece_sob_outra` |
| Edital publicado antes desta feature | `test_legado_da_projecao.py` (5); a suíte inteira |
| Processo publicado antes de 04/09 sem ato de ativação | por construção: `desfechos` lê só os estados finais e os atos `ENCERRAR`/`CANCELAR`, e nunca o *Ativo* (`test_desfechos.py::test_editais_publicados_nao_consultam_os_atos`) |

## Decisões

| Decisão | Onde se verifica |
|---|---|
| D-001 | nenhum endereço novo; a página continua por Edital (`portal/urls.py` inalterado) |
| D-002 | `agora_e_proximo` e `situacao_publica` não calculam fase agregada; `test_sem_evento_pendente_…` afirma a ausência de *"em análise"* |
| D-003 | `desfechos` (precedência); `test_o_desfecho_do_edital_vence_o_do_processo` |
| D-004 | `fase_publica_do_evento` lê a régua da 045; `test_o_pontual_iniciado_ha_uma_hora_ja_e_concluido` |
| D-005 | `janela_da_publicacao_divulgada` é a função da interposição (`interpor._janelas_pertinentes` a chama); `test_prazo_aberto_…` compara com `objetos_recorriveis` |
| D-006 | `test_nem_o_motivo_nem_o_autor_do_ato_aparecem` |
| D-007 | `test_a_vitrine_do_edital_anuncia_so_a_vigente` (a sucedida só no histórico recolhido) |
| D-008 | `test_resultado_publico.py::TABELAS_PROIBIDAS` sem a versão consolidada, com as três de dado individual mantidas |

## Percurso pela tela (T035)

Servidor local na porta 8047, banco `ps047` com o `seed_demo`, em 26/09/2026. A gestão foi usada
com a identidade Gestor pelo seletor de identidade. Os atos foram praticados pelas telas de
Cancelar e de Encerrar.

| Percurso | O que se fez | O que a página pública disse |
|---|---|---|
| 1 — cancelado | Edital 01/2026, com inscrições abertas, cancelado pela gestão (o "antes" está gravado em `antes-da-047.md`) | antes: *"ABERTA · Inscrições abertas… Faltam 19 dias"*. Depois: *"EDITAL CANCELADO · Edital cancelado em 26/09/2026. Não recebe inscrições."* O Edital saiu da vitrine |
| 2 — encerrado e Processo encerrado | Edital 51/2026 encerrado pela gestão; depois o Processo PS-DEMO-2026 encerrado pela gestão | 51/2026: *"EDITAL ENCERRADO · Edital encerrado em 26/09/2026."* 26/2026, ainda publicado e com o período já encerrado: *"PROCESSO ENCERRADO · Processo seletivo encerrado em 26/09/2026."* **A revisão do #193 corrigiu esta leitura**: o desfecho do Processo passou a ser dito como fato, sem marca própria e sem *"não recebe inscrições"*, porque o Edital publicado continua recebendo dentro do período (`D-003`). O caso com o período aberto é a regressão `test_processo_encerrado_com_edital_aberto_…` |
| 3 — fase do cronograma | página do 26/2026 antes do encerramento do Processo | as fases conferem com a régua; o Evento cancelado só nasce pela API e fica provado por `test_fase_do_cronograma.py` |
| 4 — agora e próximo | página do 26/2026 com inscrições encerradas | *"Próximo, em 01/10/2026: Aplicação da prova no Campus Vitória, em turno único."* O percurso achou e corrigiu a pontuação dobrada (`b27d0459`) |
| 5 — prazo recursal | resultado preliminar do 51/2026, seed com janela de cinco dias | página do resultado: *"Prazo de recurso aberto, de 26/09/2026 até 01/10/2026 às 23h59. Quem se inscreveu recorre pela própria área do candidato."* Lista do Edital: *"recurso até 01/10/2026 às 23h59"* |
| 6 — histórico | o seed não sucede nenhuma publicação | provado por `test_historico_de_resultados.py` |
| 7 — nada escrito | T033 | nenhuma migration, 34 de 34, `test_leitura_sem_escrita.py` verde |

O painel do navegador estava oculto (viewport zero), e por isso não há capturas: o texto de cada
página foi lido do DOM, e os atos pela resposta do servidor e pelo banco.
