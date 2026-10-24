# Rastreabilidade: Relatório do Edital

Cada requisito → a tarefa que o implementa → o teste que o verifica. Conferida contra o implementado
em 24/10/2026. As tarefas estão em [tasks.md](tasks.md). Caminhos de teste relativos a `backend/`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2513 (a ação no detalhe, indisponível com motivo antes da publicação) | T010 | `tests/interface/test_relatorio.py::test_a_gestao_ve_a_acao_e_a_pagina_com_a_camada_executiva`, `::test_edital_nao_publicado_tem_a_acao_indisponivel_e_recusa` |
| FR-2514 (404 fora da unidade; recusa explicada sem a base) | T010, T012 | `test_relatorio.py::test_outra_unidade_recebe_nao_encontrado`, `::test_quem_e_da_unidade_sem_a_base_recebe_a_recusa_explicada`, `::test_a_presidencia_do_processo_tambem_alcanca`; `tests/test_gramatica_das_portas.py` (inventário) |
| FR-2515 (a página e o envio que emite) | T010, T011 | `test_relatorio.py::test_a_gestao_ve_a_acao_e_a_pagina_com_a_camada_executiva`, `::test_a_emissao_so_aceita_envio` |
| FR-2516 e FR-2517 (evento com resumo; número da emissão) | T021 | `tests/integration/relatorio/test_emissao.py::test_cada_emissao_e_numerada_e_registrada_com_o_resumo_do_que_saiu` |
| FR-2518 (resposta privada) | T010 | `test_emissao.py::test_cada_emissao_*` e `test_relatorio.py::test_a_gestao_ve_*` (`no-store`) |
| FR-2519 (um instante só) | T003 | `test_emissao.py::test_a_leitura_inteira_ve_um_instante_so` |
| FR-2520 (mesmos fatos, mesmos bytes) | T009 | `test_emissao.py::test_mesmos_fatos_e_mesmo_instante_dao_os_mesmos_bytes` |
| FR-2521 (não reconstitui o passado) | T003, T009 | por construção: a derivação lê o vigente no instante; o anexo H o diz (`relatorio_pdf._anexo`); `test_especie.py::test_prazo_encerrado_sem_resposta_*` lê o mesmo cenário em dois instantes |
| FR-2522 a FR-2525 (duas situações, espécie, pendências, o limite do encerramento) | T017 | `tests/integration/relatorio/test_especie.py` (os cinco casos) |
| FR-2526 (registros posteriores ao desfecho) | T018 | `test_especie.py::test_encerrado_com_convocacao_no_prazo_e_acompanhamento` |
| FR-2527 (visão geral por regras) | T008 | `test_especie.py` (frases de cada final); `test_conteudo.py::test_a_camada_executiva_nao_usa_termo_interno` |
| FR-2528 a FR-2533 (os seis indicadores, a razão, cadastros e não pessoas, habilitadas, cadeia da convocação, matrícula) | T004 | `tests/integration/relatorio/test_numeros.py::test_os_indicadores_sao_os_da_maquete_e_os_das_telas_donas`, `::test_a_tabela_por_perfil_une_as_listas_e_nao_soma_os_marcos`; `tests/unit/interface/test_relatorio_do_edital.py` |
| FR-2534 (pontos de atenção, no máximo três) | T018 | `test_especie.py::test_encerrado_com_convocacao_no_prazo_e_acompanhamento` |
| FR-2535 (tabela por perfil de vaga) | T004 | `test_numeros.py::test_a_tabela_por_perfil_une_as_listas_e_nao_soma_os_marcos`; `test_relatorio.py::test_a_gestao_ve_*` |
| FR-2536 (procura por semana, prorrogação) | T005 | `test_numeros.py::test_procura_recursos_e_retificacao`; `test_relatorio_do_edital.py::test_semanas_marcam_o_termino_original_e_o_periodo_acrescentado` |
| FR-2537 (retificações com antes e depois; recursos) | T006 | `test_numeros.py::test_procura_recursos_e_retificacao`; `test_conteudo.py::test_retificacao_nao_descrita_e_dita_assim` |
| FR-2538 (datas com a natureza) | T006 | `test_relatorio.py::test_a_gestao_ve_*`; a tabela de datas no PDF de demonstração |
| FR-2539 (endereços públicos clicáveis, sem resumo no executivo) | T006, T009 | `test_conteudo.py::test_documentos_com_resumo_endereco_e_frase_de_integridade` |
| FR-2540 (etapas por Perfil, sem presença) | T009 | `test_numeros.py::test_as_etapas_contam_avaliadas_e_ocorrencias_sem_presenca` |
| FR-2541 (listas que não se somam) | T009 | `test_numeros.py::test_a_tabela_por_perfil_une_as_listas_e_nao_soma_os_marcos` |
| FR-2542 (cronograma em três colunas) | T009 | a seção D do PDF de demonstração; `relatorio_do_edital._cronograma` |
| FR-2543 (resumos e a frase de integridade) | T009 | `test_conteudo.py::test_documentos_com_resumo_endereco_e_frase_de_integridade` |
| FR-2544 (definições, o que não é registrado, espécie e emissão) | T009 | seções F, G e H do PDF de demonstração; `test_conteudo.py::test_a_camada_executiva_nao_usa_termo_interno` (lê o anexo) |
| FR-2545 (rótulos do produto; o aceite é "convocação aceita") | T004 | `test_numeros.py::test_os_indicadores_*` ("convocações aceitas"); `relatorio_do_edital.ROTULOS_DOS_DESFECHOS` importa `portal/situacao.DESFECHOS` |
| FR-2546 (termos proibidos) | T015 | `test_conteudo.py::test_a_camada_executiva_nao_usa_termo_interno` |
| FR-2547 (nomes publicados; texto livre não decide situação) | T004 | `test_numeros.py::test_as_etapas_*` (nomes das Etapas); `test_especie.py` (situação pelo estado e pelas pendências) |
| FR-2548 (grafias de ausência, nunca 0) | T003 | `test_relatorio_do_edital.py::test_ausencia_nunca_vira_zero`; `test_especie.py::test_inscricoes_abertas_e_acompanhamento_com_numeros_parciais` |
| FR-2549 (nenhum dado pessoal) | T015 | `test_conteudo.py::test_nenhum_dado_pessoal_de_candidato` |
| FR-2550 (fato não público só por Perfil) | T007 | `test_conteudo.py::test_fato_nao_publico_nao_cruza_com_a_lista` |
| FR-2551 (Perfil com menos de cinco, omitido) | T007 | `test_conteudo.py::test_perfil_com_menos_de_cinco_inscricoes_omite_o_que_nao_e_publico` |
| FR-2552 (rodapé, natureza, marcadores) | T009 | `test_conteudo.py::test_documentos_com_resumo_*` (anotações); o rodapé no PDF de demonstração |
| FR-2553 (CSP, tabelas, 375 px) | T011 | `tests/interface/test_politica_de_conteudo.py`, `test_acessibilidade.py`, `test_folha_estatica.py`; a medida a 375 px na verificação pelo navegador (24/10) |
| SC-932 (compreensão por destinatários) | T028 | conversa com destinatários reais — **do usuário** |
| SC-933 (zero divergência com as telas donas) | T014 | `tests/integration/relatorio/test_numeros.py` |
| SC-934 (nenhum dado pessoal; nada não público por lista) | T015 | `tests/integration/relatorio/test_conteudo.py` |
| SC-935 (a espécie em todos os estados) | T019 | `tests/integration/relatorio/test_especie.py` |
| SC-936 (consultas constantes) | T023 | `tests/performance/test_relatorio.py` (119 nas escalas 1 e 10) |
| SC-937 (emissão registrada; bytes idênticos) | T022 | `tests/integration/relatorio/test_emissao.py` |
| SC-938 (cenário demonstrável) | T027 | verificação pelo navegador de 24/10 (`quickstart.md`): a ação no detalhe, a página e o PDF pelo formulário |

## Casos-limite

| Caso | Teste |
|---|---|
| Edital publicado e com inscrições abertas | `test_especie.py::test_inscricoes_abertas_e_acompanhamento_com_numeros_parciais` |
| Edital em elaboração, em revisão ou homologado | `test_relatorio.py::test_edital_nao_publicado_tem_a_acao_indisponivel_e_recusa` |
| Marco sem resultado publicado | `test_especie.py::test_inscricoes_abertas_*` (pendência "ainda não divulgado") |
| Lista reservada sem inscrição e sem ato | por construção: só listas com ato ou publicação entram (`_ocupacao` ignora recorte sem vaga); coberto pela leitura do cenário v1 no estudo |
| Apuração vigente desatualizada | `relatorio_do_edital._ocupacao` (estado `OBSOLETO` vira ausência e pendência) — sem cenário próprio nesta entrega |
| Convocação com prazo vencido e sem desfecho | `test_especie.py::test_prazo_encerrado_sem_resposta_e_pendencia_e_nao_desfecho` |
| Resultado preliminar sucedido pelo definitivo | `test_numeros.py::test_o_resultado_substituido_conta_so_o_vigente` |
| Ato de ordenação sucedido | por construção: `AtoDeOrdenacao` com `sucessores__isnull=True` |
| Perfil com menos de cinco inscrições | `test_conteudo.py::test_perfil_com_menos_de_cinco_*` |
| Mesma pessoa em dois Perfis | `test_numeros.py::test_os_indicadores_*` (38 inscrições; 36 cadastros no anexo) |
| Retificação não descrita automaticamente | `test_conteudo.py::test_retificacao_nao_descrita_e_dita_assim` |
| Edital sem Retificação, recurso ou convocação | `test_especie.py::test_cancelado_*` (nenhuma convocação: ausência dita) |
| Registro gravado durante a leitura | `test_emissao.py::test_a_leitura_inteira_ve_um_instante_so` |
| Caractere sem grafia | `test_emissao.py::test_texto_sem_grafia_recusa_a_emissao` |
