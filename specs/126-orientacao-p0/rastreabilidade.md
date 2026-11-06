# Rastreabilidade: Correções de orientação e segurança operacional (126)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `op` = `interface/test_orientacao_p0.py` — as telas (A1, A2, A6)
- `ei` = `interface/test_sorteio_extracao_inviavel.py` — o aviso de congelamento (A5; 102, revisto)
- `cs` = `integration/relatorio/test_convocacao_sem_comunicacao.py` — o rótulo da convocação (A4)
- `co` = `unit/interface/test_conferencia_da_ordem.py` — o resumo da confirmação da ordem (A6)
- `rc` = `unit/interface/test_relatorio_consolidado.py` — a forma do consolidado
- `pr` = `performance/test_relatorio.py` — o orçamento de consultas do relatório
- `cq` = capturas antes e depois em `capturas/`

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4010 (sucessão recolhida, com rótulo) | T005–T008 | `op::test_depois_de_emitir_o_corte_a_sucessao_vem_recolhida_e_a_mensagem_diz_o_que_foi_feito`; `op::test_depois_de_emitir_a_ordem_a_sucessao_vem_recolhida_com_as_contagens`; `op::test_a_apuracao_vigente_traz_a_sucessao_recolhida_e_a_mensagem_nomeia_o_recorte`; `op::test_a_relacao_publicada_nomeia_o_recorte_e_a_sucessao_vem_recolhida`; `cq` a1 |
| FR-4011 (aberta quando obsoleto) | T005–T008 | `op::test_o_corte_obsoleto_abre_a_sucessao`; ordem, apuração e relação por leitura do template (`verificacao.md`) |
| FR-4012 (a sucessão exige o mesmo) | T005–T008 | `ei::test_a_sucessao_de_uma_relacao_que_sorteia_tambem_e_avisada` (o motivo no bloco); `interface/test_corte.py` inteiro, sem mudança |
| FR-4013 (faixa seguinte e citações intactas) | T005, T006 | `interface/test_telas_de_resultado_e_atos.py::test_nenhum_botao_muda_de_rotulo_desenho_ou_lugar`; `interface/test_corte.py::test_a_continuacao_repetida_nao_emite_duas_faixas` |
| FR-4014 (mensagem do corte) | T005 | `op::test_depois_de_emitir_o_corte_a_sucessao_vem_recolhida_e_a_mensagem_diz_o_que_foi_feito`; `cq` a1 |
| FR-4015 (mensagem da ordem) | T006 | `op::test_depois_de_emitir_a_ordem_a_sucessao_vem_recolhida_com_as_contagens` |
| FR-4016 (mensagem da apuração) | T007 | `op::test_a_apuracao_vigente_traz_a_sucessao_recolhida_e_a_mensagem_nomeia_o_recorte` |
| FR-4017 (mensagem da relação) | T008 | `op::test_a_relacao_publicada_nomeia_o_recorte_e_a_sucessao_vem_recolhida` |
| FR-4018 (sem próximo passo) | T005–T008 | leitura das quatro mensagens (`contracts/telas.md`) |
| FR-4019 (o critério de sem inscrito) | T002 | `op::test_o_criterio_e_a_lista_que_ninguem_declarou_com_as_inscricoes_encerradas`; `op::test_com_as_inscricoes_abertas_nada_e_sem_inscrito`; `op::test_relacao_congelada_nao_e_sem_inscrito` |
| FR-4020 (células e totais) | T012 | `op::test_a_conducao_diz_nao_se_aplica_na_lista_sem_inscrito_e_tira_dos_totais`; `cq` a2 |
| FR-4021 (gestos e conferência) | T013 | `op::test_a_conferencia_poe_a_lista_sem_inscrito_fora_e_nao_impedida`; `op::test_marco_sem_inscrito_nenhum_nao_tem_nada_a_conduzir` |
| FR-4022 (nada a conduzir) | T014 | `op::test_marco_sem_inscrito_nenhum_nao_tem_nada_a_conduzir`; `cq` a2 |
| FR-4023 (marco por pontuação intacto) | T017 | `op::test_marco_por_pontuacao_nao_tem_recorte_sem_inscrito`; `interface/test_conducao_do_marco.py::test_o_recorte_em_que_ninguem_concorreu_esta_feito_e_diz_por_que` |
| FR-4024 (convocação sem inscrito) | T015 | `op::test_a_convocacao_da_lista_sem_inscrito_nao_manda_a_lugar_nenhum`; `cq` a2 |
| FR-4025 (faixa só com corte) | T015 | `op::test_sem_corte_a_convocacao_nao_fala_em_faixa`; `interface/test_convocacao.py::TestOsEstadosDistintos::test_a_fila_esgotada_nao_oferece_botao_que_esta_feature_nao_cumpre` |
| FR-4026 (ocupação sem inscrito) | T016 | `op::test_a_ocupacao_da_lista_sem_inscrito_nao_manda_emitir_a_ordem`; `cq` a2 |
| FR-4027 (pelos estados do domínio) | T019–T022 | `cs::test_sem_comunicacao_e_especie_propria_e_nao_aguarda_resposta`; `cs::test_com_a_comunicacao_enviada_ela_aguarda_resposta_ate_o_vencimento`; `pr` (120 consultas) |
| FR-4028 (aguardando só com prazo em curso) | T020 | `cs::test_com_a_comunicacao_enviada_ela_aguarda_resposta_ate_o_vencimento`; `integration/relatorio/test_especie.py` |
| FR-4029 (espécie própria) | T019–T022 | `cs::test_o_encerrar_diz_sem_comunicacao_enviada`; `cs::test_o_consolidado_tem_o_rotulo_proprio`; `rc::test_cada_numero_e_a_soma_dos_fatos_de_cada_edital`; `cq` a4 |
| FR-4030 (sem envio não é vencida) | T020 | `cs::test_sem_comunicacao_com_o_vencimento_passado_nao_e_vencida` |
| FR-4031 (aviso no topo só com relação a congelar) | T025, T026 | `ei::test_com_a_extracao_hoje_o_aviso_vem_antes_do_botao_e_o_botao_continua`; `ei::test_a_sucessao_de_uma_relacao_que_sorteia_tambem_e_avisada`; `cq` a5 |
| FR-4032 (aviso dentro da sucessão) | T026 | `ei::test_a_sucessao_de_uma_relacao_que_sorteia_tambem_e_avisada`; `ei::test_a_lista_sem_inscrito_nao_faz_o_aviso_aparecer`; `cq` a5 |
| FR-4033 (sem inscrito não dispara o aviso) | T025 | `ei::test_a_lista_sem_inscrito_nao_faz_o_aviso_aparecer` |
| FR-4034 (a regra da 102 intacta) | T025, T026 | `ei` inteiro (os demais casos da `102`, sem mudança) |
| FR-4035 (contagem por Etapa) | T029, T030 | `co::test_sem_nenhum_resultado_cada_etapa_tem_a_contagem_e_o_destaque`; `co::test_resultado_parcial_conta_so_quem_falta_e_so_na_etapa_que_falta`; `op::test_a_confirmacao_da_ordem_diz_quem_esta_sem_resultado_e_em_qual_etapa`; `cq` a6 |
| FR-4036 (nenhuma com resultado e a consequência) | T029, T030 | `co::test_sem_nenhum_resultado_cada_etapa_tem_a_contagem_e_o_destaque`; `co::test_universo_vazio_nao_e_nenhuma_com_resultado`; `cq` a6 |
| FR-4037 (grupos por motivo) | T029, T030 | `co::test_os_grupos_juntam_o_mesmo_motivo_na_ordem_em_que_aparecem`; `op::test_a_confirmacao_da_ordem_diz_quem_esta_sem_resultado_e_em_qual_etapa` |
| FR-4038 (eliminada não é sem resultado) | T029 | `co::test_a_eliminada_nao_conta_como_sem_resultado`; `co::test_a_decisoria_com_resultado_sem_pontuacao_conta_como_com_resultado` |
| FR-4039 (a emissão continua possível) | T030 | `op::test_a_confirmacao_da_ordem_diz_quem_esta_sem_resultado_e_em_qual_etapa` |
| FR-4040 (sem migration nem estado) | T031 | `make check` (`makemigrations --check`: nenhuma mudança) |
| FR-4041 (fora: cartões do detalhe e erro da Caixa) | — | `git diff`: `detalhe.html`, `acoes.py`, `trabalho.py` e `ocorrencia.py` intocados |

## Experiência

| Requisito | Onde | Testes |
|---|---|---|
| UX-223 | `corte.html`, `ordenacao.html`, `ocupacao.html`, `sorteio.html`; `.sucessao` em `telas.css` | os de FR-4010 |
| UX-224 | `marco.html`, `convocacao.html`, `ocupacao.html` | os de FR-4020, FR-4024, FR-4026 |
| UX-225 | `relatorio_do_edital.py`, `relatorio_consolidado.py`, `relatorio_consolidado_pdf.py` | os de FR-4029 |
| UX-226 | `sorteio.html` | os de FR-4032 |
| UX-227 | `ordenacao_confirmar.html` | os de FR-4035 a FR-4037 |

## Critérios de sucesso

| Critério | Como se verifica |
|---|---|
| SC-1210 | os testes de FR-4010; `cq` a1 |
| SC-1211 | os testes de FR-4014 a FR-4017 |
| SC-1212 | `op::test_marco_sem_inscrito_nenhum_nao_tem_nada_a_conduzir`; `cq` a2 (35 Polo Vitória) |
| SC-1213 | `op::test_sem_corte_a_convocacao_nao_fala_em_faixa`; `op::test_a_convocacao_da_lista_sem_inscrito_nao_manda_a_lugar_nenhum`; `cq` a2 |
| SC-1214 | `cs::test_o_encerrar_diz_sem_comunicacao_enviada`; `cq` a4 (no Edital 51; ver `verificacao.md`) |
| SC-1215 | `ei::test_a_lista_sem_inscrito_nao_faz_o_aviso_aparecer`; `cq` a5 (35 Cefor) |
| SC-1216 | `op::test_a_confirmacao_da_ordem_diz_quem_esta_sem_resultado_e_em_qual_etapa`; `cq` a6 (91) |
| SC-1217 | `interface/test_conducao_do_marco.py::test_o_recorte_em_que_ninguem_concorreu_esta_feito_e_diz_por_que`; `op::test_marco_por_pontuacao_nao_tem_recorte_sem_inscrito` |
| SC-1218 | `make check`; a suíte contra PostgreSQL (`verificacao.md`) |
