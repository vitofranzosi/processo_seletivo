# Rastreabilidade: Relatório consolidado da unidade

Cada requisito → a tarefa que o implementa → o teste que o verifica. Conferida contra o implementado
em 24/10/2026. As tarefas estão em [tasks.md](tasks.md). Caminhos de teste relativos a `backend/`;
`UNI` é `tests/unit/interface/test_relatorio_consolidado.py`, `INT` é
`tests/integration/relatorio_consolidado/`, `TELA` é `tests/interface/test_relatorio_consolidado.py`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2554 (o relatório a partir da Visão Geral; recusa explicada sem a capacidade) | T016, T017 | `TELA::test_a_visao_geral_oferece_o_relatorio_a_quem_tem_a_porta`, `::test_sem_a_capacidade_a_recusa_diz_o_que_falta` |
| FR-2555 (só o escopo do ator; identificador alheio ignorado) | T014, T022 | `INT/test_conjunto.py::test_escolha_manual_e_identificador_de_outro_escopo`; `TELA::test_outra_unidade_nao_ve_os_editais_do_cefor` |
| FR-2556 (respostas privadas) | T016 | `TELA::test_a_escolha_lista_os_editais_marcados`, `::test_a_pagina_traz_a_camada_executiva_e_a_emissao`; `INT/test_emissao.py::test_cada_emissao_e_numerada_na_unidade_com_o_conjunto` (`no-store`) |
| FR-2557 e FR-2558 (três critérios; padrão; atalhos; primeira publicação) | T014, T020 | `UNI::test_o_criterio_de_publicacao_e_seus_atalhos`, `::test_o_criterio_por_numero_e_o_manual`, `::test_datas_invertidas_sao_recusadas`; `INT/test_conjunto.py::test_os_semestres_particionam_pela_primeira_publicacao`, `::test_ano_do_numero_e_primeira_publicacao_sao_criterios_diferentes` |
| FR-2559 (lista marcada; desmarcar; escolha manual com busca) | T017, T022 | `TELA::test_a_escolha_lista_os_editais_marcados`, `::test_aplicar_outro_criterio_nao_herda_os_marcados`; `INT/test_conjunto.py::test_desmarcar_retira_e_o_relatorio_diz_quais`, `::test_escolha_manual_e_identificador_de_outro_escopo` |
| FR-2560 (só publicados, encerrados ou cancelados; os demais fora, com o motivo) | T014 | `INT/test_conjunto.py::test_edital_nao_publicado_fica_fora_com_o_motivo` |
| FR-2561 (o critério por extenso, retirados e escolha) | T019 | `INT/test_conjunto.py::test_desmarcar_retira_e_o_relatorio_diz_quais`; `UNI::test_o_criterio_*` |
| FR-2562 e FR-2563 (vazio não se emite; limite) | T014 | `UNI::test_conjunto_vazio_e_grande_demais_sao_recusados`; `INT/test_emissao.py::test_conjunto_vazio_nao_e_emitido`; `TELA::test_conjunto_vazio_recusa_a_pagina` |
| FR-2564 (um instante para o conjunto inteiro) | T014 | `INT/test_conjunto.py::test_a_leitura_do_conjunto_ve_um_instante_so` |
| FR-2565 (o critério escolhe Editais; dados do instante; sem reconstituição) | T019 | `INT/test_conjunto.py::test_a_situacao_e_a_do_instante_e_nao_a_do_fim_do_periodo`; `TELA::test_a_pagina_traz_a_camada_executiva_e_a_emissao` |
| FR-2566 e FR-2567 (envio; evento na Unidade com conjunto e resumo; número) | T026 | `INT/test_emissao.py::test_cada_emissao_e_numerada_na_unidade_com_o_conjunto`; `TELA::test_a_emissao_so_aceita_envio` |
| FR-2568 (mesmos fatos, conjunto e instante, mesmos bytes) | T015 | `INT/test_emissao.py::test_mesmos_fatos_conjunto_e_instante_dao_os_mesmos_bytes` |
| FR-2569 (nenhuma regra replicada) | T012 | `INT/test_numeros.py::test_cada_numero_e_a_soma_dos_relatorios_de_cada_edital`; por construção: `relatorio_consolidado.montar` lê `fatos_do_edital` |
| FR-2570 (fatos separados da redação; o documento individual inalterado) | T002 a T005 | composição normalizada comparada nos quatro estados (`research.md`, R-001); `tests/integration/relatorio` inteiro |
| FR-2571 (um universo; cancelado só como Edital) | T012 | `UNI::test_cancelado_conta_como_edital_e_fica_fora_de_todo_numero`, `::test_so_cancelados_nao_produz_numero`; `INT/test_numeros.py::test_cada_numero_e_a_soma_dos_relatorios_de_cada_edital` |
| FR-2572 (razão Σ/Σ recortada, parcial) | T012 | `UNI::test_a_razao_e_soma_sobre_soma_e_nao_media_das_razoes`, `::test_cadastro_de_reserva_fica_fora_dos_dois_termos_da_razao`, `::test_periodo_aberto_marca_inscricoes_e_razao_parciais`; `INT/test_numeros.py::test_vagas_inscricoes_e_razao_sao_as_da_visao_geral` |
| FR-2573 e FR-2574 (ficha, visão geral, os seis números) | T012, T017 | `TELA::test_a_pagina_traz_a_camada_executiva_e_a_emissao`; `UNI::test_a_situacao_no_gps_e_as_providencias_da_ficha`, `::test_cada_numero_e_a_soma_dos_fatos_de_cada_edital` |
| FR-2575 (frases verdadeiras, sem juízo) | T012 | `UNI::test_o_texto_nao_afirma_pessoa_aprovacao_ou_matricula`, `::test_so_cancelados_nao_produz_numero` |
| FR-2576 (três pontos de atenção, nesta ordem) | T012 | `INT/test_providencias.py::test_encerrado_com_convocacao_no_prazo_e_registros_na_trilha`; `UNI::test_pendencias_por_tipo_contam_editais_e_ocorrencias` |
| FR-2577 e FR-2578 (oferta e procura; série por mês do envio, sem "no semestre") | T015, T019 | `INT/test_conjunto.py::test_a_situacao_e_a_do_instante_e_nao_a_do_fim_do_periodo`; `UNI::test_envios_por_mes_no_horario_institucional`, `::test_reservadas_somam_so_no_total`; `INT/test_numeros.py::test_cadastro_de_reserva_e_listas_sobrepostas` |
| FR-2579 (execução e resultados, sem taxas) | T015 | `UNI::test_cada_numero_e_a_soma_dos_fatos_de_cada_edital`, `::test_resultado_incompleto_nao_conta_como_edital_com_todos_os_definitivos`; o PDF demonstrativo |
| FR-2580 (providências por tipo e por Edital) | T024 | `UNI::test_pendencias_por_tipo_contam_editais_e_ocorrencias`; `INT/test_providencias.py::test_encerrado_com_convocacao_no_prazo_e_registros_na_trilha` |
| FR-2581 (a trilha dita pelo que registra, no consolidado e na `099`) | T010, T024 | `UNI::test_registros_posteriores_sao_ditos_como_trilha`; `tests/integration/relatorio/test_correcoes_da_100.py::test_a_trilha_e_dita_pelo_que_registra` |
| FR-2582 (anexo: relação, fora, critério, definições, limitações, emissão) | T015 | `INT/test_conjunto.py::test_desmarcar_retira_e_o_relatorio_diz_quais`; o anexo do PDF demonstrativo |
| FR-2583 e FR-2584 (vocabulário; ausência grafada) | T012 | `UNI::test_o_texto_nao_afirma_pessoa_aprovacao_ou_matricula`, `::test_sem_vaga_imediata_a_razao_nao_se_aplica_e_nunca_e_zero`, `::test_sem_apuracao_e_sem_convocacao_dizem_a_ausencia` |
| FR-2585 e FR-2586 (nada pessoal; nada por Perfil ou lista) | T012, T027 | `INT/test_privacidade.py::test_nenhum_dado_pessoal_nem_fato_nao_publico_por_perfil` |
| FR-2587 e FR-2588 (supressão complementar na `099`) | T007, T008 | `tests/unit/interface/test_relatorio_do_edital.py::test_o_grupo_pequeno_leva_o_menor_dos_demais` e vizinhos; `tests/integration/relatorio/test_correcoes_da_100.py::test_perfil_pequeno_leva_o_outro_e_o_total_continua`, `::test_edital_abaixo_do_limiar_cala_os_totais_nao_publicos`; `tests/integration/relatorio/test_especie.py::test_inscricoes_abertas_e_acompanhamento_com_numeros_parciais` |
| FR-2589 (Perfil sem inscrição não deve resultado) | T009 | `tests/integration/relatorio/test_correcoes_da_100.py::test_perfil_sem_inscricao_nao_deve_resultado`; `INT/test_providencias.py::test_perfil_sem_inscricao_nao_vira_pendencia_no_conjunto` |
| FR-2590 e FR-2591 (forma do PDF; CSP, tabelas, 375 px) | T015, T017, T035 | `test_diagramacao_do_consolidado.py::test_toda_pagina_diz_o_conjunto_a_data_e_a_emissao`; `tests/interface/test_folha_estatica.py`; verificação pelo navegador em 24/10 (375 px sem rolagem horizontal, console sem violação) |
| FR-2592 (Edital pequeno fora dos números não públicos) | T012 | `UNI::test_edital_pequeno_nao_entra_em_numero_nao_publico`, `::test_conjunto_so_de_editais_pequenos_omite_os_totais_nao_publicos`; `INT/test_privacidade.py::test_o_edital_pequeno_nao_muda_numero_nao_publico_entre_emissoes` |
| FR-2593 e FR-2594 (título; primeira página como painel; indicadores em cartões, inteiros) | T035 | `tests/unit/interface/test_diagramacao_do_consolidado.py::test_a_primeira_pagina_e_o_painel_inteiro`, `::test_cartao_e_grupo_nao_se_partem`, `::test_o_titulo_e_o_da_finalidade_institucional` |
| FR-2595 (gráfico da série; frase com um mês; ausência dita) | T035 | `test_diagramacao_do_consolidado.py::test_o_grafico_aparece_quando_ha_meses_para_comparar` |
| FR-2596 (paginação que preserva os grupos; nada fora da área útil) | T035 | `test_diagramacao_do_consolidado.py::test_titulo_nunca_fica_sozinho_no_pe`, `::test_blocos_cabem_na_pagina_e_nao_se_sobrepoem`, `::test_tabela_longa_continua_com_o_cabecalho_repetido`, `::test_poucos_e_muitos_editais_mantem_o_painel_e_o_anexo_em_pagina_propria`; `diagramacao.Tela._conferir` recusa texto fora da área |
| FR-2597 (colunas, tabelas leves, paleta e hierarquia da maquete) | T035 | `test_diagramacao_do_consolidado.py::test_cartao_e_grupo_nao_se_partem` (três pares lado a lado); comparação visual em `doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/comparacao-visual.pdf` |
| FR-2598 (endereço público só quando vale; indisponibilidade dita) | T036 | `test_diagramacao_do_consolidado.py::test_links_so_quando_o_endereco_vale_para_quem_recebe`; `interface/relatorio.py::_host_local` |
| FR-2599 (subconjunto dito junto do número) | T036 | `tests/unit/interface/test_relatorio_consolidado.py::test_edital_pequeno_nao_entra_em_numero_nao_publico`; `INT/test_privacidade.py::test_o_edital_pequeno_nao_muda_numero_nao_publico_entre_emissoes` |
| FR-2600 (PDF marcado) | T035 | `test_diagramacao_do_consolidado.py::test_a4_marcado_e_deterministico`; `pdfinfo -struct-text` do PDF demonstrativo (revisão visual) |
| SC-946 (organização equivalente à da maquete, de 1 a 60 Editais) | T037 | `test_diagramacao_do_consolidado.py` (parametrizado em 1, 5, 12 e 60 Editais); `doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/revisao-visual.md` e `comparacao-visual.pdf` |
| SC-939 (zero divergência com as fontes) | T018 | `INT/test_numeros.py` (os três casos) |
| SC-940 (o documento individual inalterado pela separação) | T005 | composição normalizada idêntica nos quatro estados (`research.md`, R-001) |
| SC-941 (privacidade) | T027 | `INT/test_privacidade.py`; `UNI::test_edital_pequeno_*` |
| SC-942 (consultas por Edital, não por inscrição; tempo no limite) | T029 | `tests/performance/test_relatorio_consolidado.py`; medição de tempo em `research.md`, R-006 |
| SC-943 (emissão registrada; determinismo) | T026 | `INT/test_emissao.py` |
| SC-944 (jornada pelo navegador) | T017, T033 | verificação pelo navegador em 24/10/2026 no banco `ps_demo_100` (entrada `relatorio-100`): Visão Geral → escolha do 1º semestre → desmarcar → página; o PDF demonstrativo emitido pelo endpoint |
| SC-945 (conversa com destinatários) | — | pendente do usuário, no piloto |
