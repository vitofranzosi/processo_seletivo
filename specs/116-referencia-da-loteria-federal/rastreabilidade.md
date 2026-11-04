# Rastreabilidade: Referência da Loteria Federal conferida antes do compromisso

Cada requisito → a tarefa que o implementa → o teste que o verifica. As tarefas estão em
[tasks.md](tasks.md). Os caminhos de teste são relativos a `backend/tests/`, e os nomes de caso são
os **finais**, conferidos na T031 (04/11/2026). O que a implementação mediu está em
[verificacao.md](verificacao.md).

## Requisitos

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-3623 (forma: inteiro de 1 a 6 algarismos; zeros normalizados; nada mais transformado) | T005, T023, T024 | `unit/sorteios/test_conferencia.py` (as grafias inválidas); `unit/editais/test_forma_da_referencia.py`; `integration/editais/test_normalizacao_da_referencia.py::test_zeros_a_esquerda_sao_gravados_sem_eles` |
| FR-3624 (no backend, na gravação e na publicação; na Retificação só o introduzido) | T022, T024 | `integration/editais/test_normalizacao_da_referencia.py::test_a_forma_errada_e_recusada_pela_api_e_nada_e_gravado`, `::test_a_forma_errada_e_recusada_pelo_comando_da_tela`; `unit/editais/test_forma_da_referencia.py::test_a_retificacao_do_acervo_nao_reconfere_a_forma`; `integration/publicacoes/test_retificacao_confere_a_referencia.py::test_troca_para_forma_invalida_e_impeditiva`, `::test_acervo_nao_e_reconferido` |
| FR-3625 (forma por fonte; demonstração inalterada) | T008, T024 | `unit/editais/test_forma_da_referencia.py::test_a_fonte_de_demonstracao_aceita_o_que_aceitava` |
| FR-3626 (a recusa diz o valor e a correção) | T006, T024 | `unit/sorteios/test_conferencia.py::test_mensagem_da_referencia_invalida` |
| FR-3627 (quatro situações, separadas da decisão) | T005, T006 | `unit/sorteios/test_conferencia.py` (matriz de situação e matriz de decisão) |
| FR-3628 (evidência principal: o último concurso, com *payload* validado) | T007, T008, T010 | `integration/sorteios/test_consulta_da_fonte.py` (cinco formas inválidas → `None`); `integration/sorteios/test_conferir_referencias.py` |
| FR-3629 (erro da consulta por número nunca decide; realizado sem data) | T005, T007, T010 | `test_consulta_da_fonte.py::test_o_500_da_caixa_nao_e_excecao_nem_estado`; `test_conferir_referencias.py::test_realizado_sem_data_continua_realizado` |
| FR-3630 (sem estimativa, sem limite de distância; distância informada) | T005, T006 | `unit/sorteios/test_conferencia.py::test_o_futuro_distante_informa_a_distancia_e_nao_recusa` |
| FR-3631 (uma principal por ato; uma por realizada; uma tentativa com tempo limite) | T007–T010, T019 | `test_conferir_referencias.py::test_uma_consulta_principal_por_ato`; `test_consulta_da_fonte.py::test_uma_tentativa_com_tempo_limite`; `integration/test_caixa_fora_do_ar.py::test_a_espera_com_a_fonte_que_dorme_nao_passa_de_quinze_segundos`, `::test_a_principal_que_dorme_custa_uma_chamada` |
| FR-3632 (fora da transação; só o conteúdo travado; instante da consulta registrado) | T014, T017 | `integration/publicacoes/test_publicacao_confere_a_referencia.py::test_referencia_travada_sem_consulta_e_inconclusiva`; `unit/sorteios/test_conferencia.py::test_o_registro_responde_as_seis_perguntas_e_nada_da_resposta_crua` |
| FR-3633 (quais referências: marcos por sortear; na Retificação, as introduzidas) | T009, T010, T022 | `test_conferir_referencias.py` (comum uma vez, sorteado fora, `base`) |
| FR-3634 (submissão e publicação: impede, adverte, informa) | T011–T014 | `unit/editais/test_concurso_realizado.py`; `test_publicacao_confere_a_referencia.py` (cenários A e B) |
| FR-3635 (Retificação: a mesma decisão, só no introduzido) | T021, T022 | `integration/publicacoes/test_retificacao_confere_a_referencia.py` |
| FR-3636 (congelamento: recusa o realizado, adverte o inconclusivo, cala a substituta) | T016, T017 | `integration/sorteios/test_congelamento_confere_a_referencia.py::test_realizado_no_congelamento_e_recusado_sem_gravar_relacao`, `::test_inconclusivo_congela_e_devolve_a_advertencia`, `::test_com_a_declarada_indisponivel_a_conferencia_se_cala`, `::test_congela_com_o_registro` |
| FR-3637 (congelamento: forma do acervo adverte) | T016, T017 | `test_congelamento_confere_a_referencia.py::test_forma_do_acervo_congela_com_advertencia` |
| FR-3638 (`102`, precedência, observação, substituição e `metodo_hash` intactos) | T011, T016, T007 | `test_concurso_realizado.py::test_a_102_continua_impeditiva`; `test_congelamento_confere_a_referencia.py` (cenário H); `integration/sorteios/test_falha_de_acesso_a_fonte.py`, `test_recusa_diz_a_saida.py`, `unit/editais/test_extracao_inviavel.py` (intocados) |
| FR-3639 (mensagem de realizado, por ato) | T005, T006 | `unit/sorteios/test_conferencia.py` (contrato, partes obrigatórias) |
| FR-3640 (mensagem de ainda não realizado; nada de "validado") | T005, T006 | `test_conferencia.py::test_ainda_nao_realizado_nunca_diz_validado_confirmado_ou_conferido` |
| FR-3641 (inconclusivo: motivo em palavras de quem opera) | T005, T019 | `test_conferencia.py` (os quatro motivos); `integration/test_caixa_fora_do_ar.py` |
| FR-3642 (fuso institucional) | T005 | `test_conferencia.py::test_instantes_no_fuso_institucional` |
| FR-3643 (o campo continua campo, com rótulo e ajuda) | T025 | `interface/test_metodo_do_marco.py::test_o_campo_pede_so_o_numero` |
| FR-3644 (nenhuma renderização consulta) | T026, T027 | `interface/test_conferencia_sob_demanda.py::test_renderizar_as_tres_telas_nao_consulta_a_fonte` |
| FR-3645 (conferência sob demanda: composição e sorteio; nada gravado) | T026, T027 | `interface/test_conferencia_sob_demanda.py::test_o_botao_esta_no_metodo_do_marco_e_no_comum`, `::test_a_resposta_diz_a_situacao_no_lugar`, `::test_nada_e_gravado`, `::test_vale_as_mesmas_chamadas_do_ato`, `::test_permissao_negada_por_padrao`, `::test_na_tela_do_sorteio_le_o_metodo_publicado` |
| FR-3646 (onde os achados do ato já aparecem) | T015, T018 | `interface/test_desfecho_da_conferencia.py::test_a_informacao_aparece_no_detalhe_depois_de_submeter`, `::test_a_advertencia_aparece_no_detalhe`, `::test_a_recusa_aparece_na_confirmacao`, `::test_a_advertencia_do_congelamento_aparece_na_tela_do_sorteio`, `::test_a_recusa_do_congelamento_aparece_na_tela_do_sorteio` |
| FR-3647 (o registro no `detalhe` do ato) | T014, T017, T022 | `test_publicacao_confere_a_referencia.py::test_o_registro_do_ato_traz_a_conferencia`; `test_congelamento_confere_a_referencia.py::test_congela_com_o_registro` |
| FR-3648 (nada da resposta crua no registro) | T005, T019 | `test_conferencia.py::test_o_registro_responde_as_seis_perguntas_e_nada_da_resposta_crua`; `test_caixa_fora_do_ar.py` |
| FR-3649 (recusa no log estruturado; sem trilha de ato que não houve) | T014 | `test_publicacao_confere_a_referencia.py::test_a_recusa_vai_ao_log_e_nao_a_trilha` |
| FR-3650 (demonstração por tabela, sem rede, fora de produção) | T007, T008 | `test_consulta_da_fonte.py::test_a_demonstracao_responde_pela_tabela`, `::test_em_producao_a_demonstracao_nao_existe` |
| FR-3651 (suíte sem a Caixa; E2E opt-in continua) | T004, T028 | `test_suite_sem_caixa.py::test_a_conexao_com_a_caixa_e_recusada`, `::test_o_adaptador_real_tambem_nao_chega_a_caixa`, `::test_o_padrao_responde_ainda_nao_realizado_ao_que_a_suite_declara`; `interface/test_sorteio_com_a_fonte_de_producao.py` com `SORTEIO_E2E_FONTE_REAL=1`, passo 6 (registro em `verificacao.md`) |
| FR-3652 (nada publicado é alterado; sem migration) | — | por construção: nenhuma migration, e a regra só roda nos quatro atos e na conferência sob demanda. A suíte com o inventário da T002 é a prova (SC-1099) |
| FR-3715 (o reaproveitamento copia o método sem a extração) | T035, T036 | `integration/editais/test_reaproveitamento_sem_a_extracao.py` |
| FR-3716 (a gravação aceita o método sem os dois campos, e só ele) | T034, T036 | `unit/editais/test_metodo_sem_a_extracao.py::test_a_gravacao_admite_o_metodo_sem_a_extracao`, `::test_um_sem_o_outro_continua_pela_metade`, `::test_o_resto_do_metodo_continua_exigido_na_gravacao` |
| FR-3717 (os atos recusam o método sem a extração, dizendo o que declarar) | T034, T035, T036 | `unit/editais/test_metodo_sem_a_extracao.py`; `integration/editais/test_reaproveitamento_sem_a_extracao.py` |
| FR-3718 (a composição e a escolha da origem dizem que a extração não vem) | T037 | `interface/test_reaproveitar.py::test_o_que_nao_vem_inclui_a_extracao_do_sorteio`, `::test_a_composicao_pede_a_extracao_ate_ela_ser_declarada` |
| FR-3719 (a origem intacta e retificável) | T035 | `integration/editais/test_reaproveitamento_sem_a_extracao.py::test_a_origem_continua_consultavel_e_retificavel` |
| FR-3720 (um mecanismo só para reconstituir o acervo; o reaproveitamento pelo comando real) | T033, T035 | `fixtures/legado.py::antes_da_116`; `integration/editais/test_reaproveitamento_sem_a_extracao.py` |
| SC-1094 (zero falso negativo, zero falso positivo, nos quatro atos, tela e API) | T013, T016, T021 | `test_publicacao_confere_a_referencia.py`, `test_congelamento_confere_a_referencia.py`, `test_retificacao_confere_a_referencia.py` |
| SC-1095 (nenhum "validado/confirmado/conferido" no ainda não realizado) | T005 | `test_conferencia.py::test_ainda_nao_realizado_nunca_diz_validado_confirmado_ou_conferido` |
| SC-1096 (oito falhas × quatro atos concluem com advertência; regras locais continuam) | T019 | `integration/test_caixa_fora_do_ar.py::test_a_submissao_conclui_com_a_advertencia`, `::test_a_publicacao_conclui_com_a_advertencia`, `::test_a_retificacao_conclui_com_a_advertencia`, `::test_o_congelamento_conclui_com_a_advertencia`, `::test_a_102_continua_impedindo_com_a_caixa_fora_do_ar` |
| SC-1097 (chamadas contadas; zero em renderização; espera ≤ 15 s) | T009, T019, T026 | `test_conferir_referencias.py`; `test_caixa_fora_do_ar.py::test_a_espera_com_a_fonte_que_dorme_nao_passa_de_quinze_segundos`; `test_conferencia_sob_demanda.py::test_renderizar_as_tres_telas_nao_consulta_a_fonte` |
| SC-1098 (as seis perguntas pelo registro do ato) | T005, T014 | `test_conferencia.py::test_o_registro_responde_as_seis_perguntas_e_nada_da_resposta_crua`; `test_publicacao_confere_a_referencia.py::test_o_registro_do_ato_traz_a_conferencia` |
| SC-1099 (suíte sem conexão; expectativas só nas inventariadas) | T002, T004, T029, T030 | `test_suite_sem_caixa.py`; `verificacao.md` (comparação por lista com a T001) |
| SC-1100 (Retificação que não toca a referência: zero consultas) | T021 | `test_retificacao_confere_a_referencia.py::test_so_o_cronograma_muda_e_nada_e_consultado` |
| SC-1115 (reaproveitar sempre conclui, e nenhum método traz a extração da origem) | T035 | `integration/editais/test_reaproveitamento_sem_a_extracao.py` |
| SC-1116 (sem a extração não submete nem publica; com ela, publica) | T035 | `integration/editais/test_reaproveitamento_sem_a_extracao.py::test_sem_a_extracao_edita_mas_nao_submete_nem_publica`, `::test_com_a_extracao_futura_declarada_o_edital_publica` |

## Casos-limite

Nenhuma ferramenta cobra esta seção: cada caso tem linha própria.

| Caso-limite | Teste |
|---|---|
| Concurso muito distante | `unit/sorteios/test_conferencia.py::test_o_futuro_distante_informa_a_distancia_e_nao_recusa` |
| O mesmo concurso em dois marcos, ou no comum e num marco | `test_conferir_referencias.py`; `test_publicacao_confere_a_referencia.py` (cenário G) |
| Método comum com marcos sorteados e por sortear | `test_conferir_referencias.py::test_o_comum_e_conferido_enquanto_houver_marco_por_sortear` |
| Realizado entre a consulta e a gravação | por construção: o instante da consulta registrado (FR-3632) e a precedência na constituição (`integration/sorteios/test_ocorrencia_declarada.py`, intocado) |
| Conteúdo travado com referência não consultada | `test_publicacao_confere_a_referencia.py::test_referencia_travada_sem_consulta_e_inconclusiva` |
| Principal conclusiva e consulta por número falha | `test_conferir_referencias.py::test_realizado_sem_data_continua_realizado` |
| A Caixa muda a resposta depois (cenário H) | `test_congelamento_confere_a_referencia.py::test_a_caixa_muda_a_resposta_e_nada_gravado_muda` |
| Acervo com grafia fora da forma | `test_congelamento_confere_a_referencia.py::test_forma_do_acervo_congela_com_advertencia`; `test_retificacao_confere_a_referencia.py::test_acervo_nao_e_reconferido` |
| Reaproveitar Edital do acervo com grafia fora da forma | `integration/editais/test_reaproveitamento_sem_a_extracao.py` (origem do corpus) |
| Reaproveitar Edital sem sorteio | `integration/editais/test_reaproveitamento_sem_a_extracao.py` |
| Rascunho com só um dos dois campos da extração | `unit/editais/test_metodo_sem_a_extracao.py` |
| Fonte de demonstração | `test_consulta_da_fonte.py::test_a_demonstracao_responde_pela_tabela` |
| Repetição idempotente | `test_publicacao_confere_a_referencia.py::test_a_repeticao_nao_consulta_de_novo`; `test_congelamento_confere_a_referencia.py::test_a_repeticao_nao_consulta_de_novo` |
| Ato recusado por outro impeditivo | `test_publicacao_confere_a_referencia.py::test_a_recusa_vai_ao_log_e_nao_a_trilha` |

## Cenários do usuário (03/11/2026) e do estudo

| Cenário | Onde |
|---|---|
| A — publicação com concurso histórico | US1; `test_publicacao_confere_a_referencia.py` |
| B — futuro sem data confirmada | US1; `test_publicacao_confere_a_referencia.py`, `test_conferencia.py` (SC-1095) |
| C — válida na publicação, realizada no congelamento | US2; `test_congelamento_confere_a_referencia.py` |
| D — Caixa indisponível | US3; `integration/test_caixa_fora_do_ar.py` |
| E — Retificação de outro elemento | US4; `test_retificacao_confere_a_referencia.py::test_so_o_cronograma_muda_e_nada_e_consultado` |
| F — acesso direto ao backend | US1; `test_publicacao_confere_a_referencia.py` (pela API) |
| G — múltiplos marcos ou métodos | US1; `test_publicacao_confere_a_referencia.py`, `test_conferir_referencias.py` |
| H — a Caixa muda uma resposta | US2; `test_congelamento_confere_a_referencia.py` |
| CA-1 a CA-18 do estudo | absorvidos: CA-1–4 e CA-14–16 em `test_conferencia.py`; CA-8–9 em `test_caixa_fora_do_ar.py`; CA-10 fica fora (aviso de divergência na observação não entra nesta spec); CA-6–7 são a `102` (intocada); CA-11–13 e CA-17 nos testes de integração acima; CA-18 na T032 |
