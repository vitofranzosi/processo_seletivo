# Rastreabilidade: O Cronograma — visibilidade no PDF, ordenação e prévia (144)

Cada requisito → a tarefa que o implementa → o teste que o verificará. Os testes ainda não existem:
os nomes são os que as tarefas criam. Caminhos relativos a `backend/tests/`. Abreviações:

- `cv` = `interface/test_cronograma_visibilidade.py` — gravação, travessias, integridade, canais
- `cp` = `interface/test_cronograma_no_pdf.py` — o texto extraído do PDF
- `cd` = `unit/publicacoes/test_cronograma_no_documento.py` — a composição, sem gerar bytes
- `el` = `contract/test_elevacao_degrau_20.py`
- `js` = `javascript/cronograma.test.js` (por `test_javascript.py`)
- `nv` = `navegador/test_jornada_do_cronograma.py`
- `ra` = `integration/editais/test_reaproveitamento.py`

A faixa abre em **FR-5100**, **SC-1580** e **UX-390**. Gastos até FR-5136, SC-1590 e UX-394; o resto
da reserva (até o requisito cinco mil cento e quarenta e nove, o critério mil quinhentos e noventa e
nove e o UX trezentos e noventa e nove) fica livre.

## Os dez cenários do pedido

| Cenário do pedido | Critério |
|---|---|
| 1 — compatibilidade | SC-1580 |
| 2 — ocultação | SC-1581 |
| 3 — associação | SC-1582 |
| 4 — ordenação | SC-1583 |
| 5 — persistência | SC-1584 |
| 6 — prévia | SC-1585 |
| 7 — reaproveitamento | SC-1586 |
| 8 — casos extremos | SC-1587 |
| 9 — PDF real | SC-1588 |
| 10 — integridade | SC-1589 |

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-5100 — atributo, exibido por padrão, inclusive nos novos | T001, T007, T008 | `migrations/test_migrations.py` (Evento antigo exibido); `cv::test_evento_acrescentado_nasce_exibido`; `cv::test_api_sem_a_chave_grava_exibido`; caso da Retificação em T007 |
| FR-5101 — o olho no grupo de ações | T010, T011 | `js::alternar muda campo, aria-pressed, title e marca`; `cv::test_o_cartao_do_evento_tem_o_controle_e_as_outras_linhas_nao` |
| FR-5102 — só o formulário; grava com a etapa; rascunho local | T009, T011 | `js::alternar despacha change e não faz pedido`; `cv::test_ocultar_e_gravar_persiste` |
| FR-5103 — o oculto continua Evento em tudo | T015 | `cv::test_oculto_na_lista_de_eventos_da_etapa`, `cv::test_oculto_conta_entre_os_vencidos`, `cv::test_oculto_recusado_pela_validacao_de_datas`, `cv::test_oculto_como_periodo_abre_as_inscricoes` |
| FR-5104 — todas as travessias | T008, T009 | `cv::test_gravar_outra_etapa_preserva_o_oculto` (Perfis, Etapas, Inscrição), `cv::test_recusa_reexibe_o_oculto`, `cv::test_restaurar_o_rascunho_local_preserva_o_oculto`, `cv::test_api_sem_a_chave_grava_exibido` |
| FR-5105 — no conteúdo publicado; degrau 20 | T002, T003 | `el::test_ausencia_vira_exibido`, `el::test_idempotente`, `el::test_v19_eleva_a_v20`; `cv::test_publicacao_leva_shown_in_pdf_em_todo_evento` |
| FR-5106 — só os exibidos; sem oculto o `order`, com algum 1..k; "Onde" pelos exibidos | T012, T014 | `cd::test_tabela_so_com_os_exibidos_numerados_de_um`, `cd::test_sem_oculto_imprime_o_order_com_zero_e_lacunas`, `cd::test_onde_so_quando_um_exibido_declara`; `cp::test_a_descricao_oculta_nao_sai_na_tabela[plana, por_perguntas]`, `cp::test_order_com_zero_e_lacunas_igual_ao_de_antes[…]` |
| FR-5107 — a remissão do período | T012, T014 | `cd::test_periodo_remete_ao_numero_impresso`, `cd::test_periodo_oculto_sai_sem_remissao`; `cp::test_remissao_do_periodo_no_texto_do_pdf[exibido, oculto]` |
| FR-5108 — a Etapa lê o oculto | T012, T014 | `cd::test_frase_da_etapa_le_o_evento_oculto`; `cp::test_a_etapa_vinculada_ao_oculto_diz_quando_sera_feita` |
| FR-5109 — todos ocultos, nas duas apresentações | T013, T014 | `cd::test_todos_ocultos_sem_secao_na_plana`, `cd::test_todos_ocultos_sem_secao_por_perguntas`, `cd::test_tabelas_do_documento_acompanha`, `cd::test_numeracao_acompanha`, `cd::test_resumo_sem_datas_no_cronograma`; `cp::test_todos_ocultos_no_texto_do_pdf[plana, por_perguntas]` |
| FR-5110 — a Revisão | T006 | `cv::test_revisao_diz_que_nao_sai_no_pdf`, `cv::test_revisao_com_todos_ocultos_diz_que_a_secao_nao_sai`; a partição de `_LIDOS_POR_COLECAO` (teste existente) |
| FR-5111 — reaproveitamento | T017 | `ra::test_reaproveitar_preserva_o_oculto_e_o_vinculo`, `ra::test_origem_v19_chega_toda_exibida` |
| FR-5112 — os seis canais não mudam | T005, T015 | `cv::test_pagina_publica_da_selecao_mostra_o_oculto`, `cv::test_assistente_ve_o_oculto`, `cv::test_agenda_mostra_o_oculto`, `cv::test_kit_de_divulgacao_mostra_o_oculto`, `cv::test_relatorio_do_edital_mostra_o_oculto`, `cv::test_leitura_pela_api_traz_o_oculto`; a cobertura de `duvidas` (teste existente) |
| FR-5113 — retificável; acrescentado nasce exibido | T004, T007 | `interface/test_campos_vem_do_contrato.py` (86); caso de Retificação em T007 |
| FR-5114 — nada publicado se regenera | T014 | `cp::test_pdf_de_edital_antigo_igual_ao_de_antes[plana, por_perguntas]` |
| FR-5120 — o botão de ordenar | T018 | `cv::test_botao_de_ordenar_so_quando_editavel` |
| FR-5121 — reorganiza a sequência efetiva, preservando tudo | T019, T020, T021 | `js::ordena por início e preserva cada cartão`; `cv::test_sequencia_ordenada_grava_com_vinculos` |
| FR-5122 — estável | T019, T020 | `js::empate mantém a ordem anterior` |
| FR-5123 — sem início ao fim, intactos | T019, T020 | `js::sem início vai ao fim sem campo alterado` |
| FR-5124 — nada reordena sozinho | T020 | `js::editar data não reordena` |
| FR-5125 — o anúncio e o foco | T019, T020, T029 | `js::anuncia quantos mudaram`, `js::anuncia que já estavam em ordem`; `nv::test_ordenar_e_as_setas_deixam_o_foco_no_botao` (lido depois do observador) |
| FR-5126 — não grava; setas continuam | T020, T021 | `js::ordenar não faz pedido e as setas continuam`; `cv::test_sequencia_ordenada_grava_com_vinculos` |
| FR-5127 — mover não é acrescentar | T029 | `nv::test_ordenar_e_as_setas_deixam_o_foco_no_botao`, `nv::test_acrescentar_continua_focando_a_linha_nova` |
| FR-5130 — a linha da prévia, Evento · Início · Término · PDF | T022, T023 | `js::a prévia mostra evento, início, término e PDF, nessa ordem` |
| FR-5131 — o cabeçalho com concordância | T023, T025 | `js::cabeçalho conta e concorda` |
| FR-5132 — segue o formulário e o não gravado | T023, T025 | `js::a prévia acompanha os seis gestos` |
| FR-5133 — vazio e todos ocultos | T023, T025 | `js::prévia vazia`, `js::prévia com todos ocultos` |
| FR-5134 — só leitura do formulário | T023, T025 | `js::a prévia não faz pedido`, `js::sem data de início` |
| FR-5135 — em somente leitura | T022, T025 | `js::prévia em somente leitura`; `cv::test_somente_leitura_tem_previa_sem_controles` |
| FR-5136 — sem JavaScript | T022 | `cv::test_previa_e_botoes_saem_com_hidden` |

## Critérios de sucesso

| Critério | Tarefa | Teste |
|---|---|---|
| SC-1580 — compatibilidade | T001, T012, T014 | `migrations/test_migrations.py`; `cp::test_pdf_de_edital_antigo_igual_ao_de_antes[…]`, `cp::test_order_com_zero_e_lacunas_igual_ao_de_antes[…]` |
| SC-1581 — ocultação | T014 | `cp::test_a_descricao_oculta_nao_sai_na_tabela`; `cv::test_ocultar_e_gravar_persiste` |
| SC-1582 — associação | T014, T015, T017 | `cp::test_a_etapa_vinculada_ao_oculto_diz_quando_sera_feita`; `cv::test_oculto_na_lista_de_eventos_da_etapa`; `ra::test_reaproveitar_preserva_o_oculto_e_o_vinculo` |
| SC-1583 — ordenação | T020, T021 | `js::ordena por início e preserva cada cartão`; `cv::test_sequencia_ordenada_grava_com_vinculos` |
| SC-1584 — persistência | T009, T021 | `cv::test_gravar_outra_etapa_preserva_o_oculto`; `cv::test_sequencia_ordenada_grava_com_vinculos` |
| SC-1585 — prévia | T025 | `js::a prévia acompanha os seis gestos` |
| SC-1586 — reaproveitamento | T017 | `ra::*` |
| SC-1587 — casos extremos | T013, T020, T025 | ver "Casos-limite" abaixo |
| SC-1588 — PDF real | T014 | `cp::*`, cada um nas duas apresentações — um oculto, todos ocultos, a remissão exibida e oculta; todo afirmar sobre o documento passa por `texto_de_pdf_bytes` |
| SC-1589 — integridade | T015 | `cv::test_oculto_*` |
| SC-1590 — a jornada no navegador | T026, T029 | `nv::test_a_jornada_do_cronograma` (1440 e 375 px, sem violação de CSP, todos os scripts da etapa juntos); `nv::test_ordenar_e_as_setas_deixam_o_foco_no_botao` |

## Requisitos de experiência

| Requisito | Tarefa | Teste |
|---|---|---|
| UX-390 — botão de alternância, nome constante, `aria-pressed`, `title` | T010, T011 | `js::alternar muda campo, aria-pressed, title e marca`; `cv::test_o_cartao_do_evento_tem_o_controle_e_as_outras_linhas_nao` |
| UX-391 — a marca em texto e o cartão atenuado | T010 | `cv::test_cartao_oculto_diz_oculto_do_pdf`; `test_acessibilidade` (regra na folha); captura do quickstart |
| UX-392 — o botão secundário, na linha da contagem, desabilitado com menos de dois | T018, T019 | `js::desabilitado com menos de dois`; captura do quickstart |
| UX-393 — a tabela compacta, 1440 e 375 px | T024 | `nv::test_a_jornada_do_cronograma` (largura da página); captura do quickstart |
| UX-394 — "Oculto" em texto; prévia não é região viva | T023, T024 | `js::linha oculta diz Oculto`; `js::a prévia não tem aria-live` |

## Casos-limite

| Caso | Tarefa | Teste |
|---|---|---|
| Nenhum Evento | T019, T023 | `js::prévia vazia`, `js::desabilitado com menos de dois` |
| Um Evento só | T019 | `js::anuncia que já estavam em ordem` |
| Todos ocultos | T013, T014, T023 | `cd::test_todos_ocultos_*`; `cp::test_todos_ocultos_no_texto_do_pdf[…]`; `js::prévia com todos ocultos`; `cv::test_revisao_com_todos_ocultos_diz_que_a_secao_nao_sai` |
| O período de inscrições oculto | T012, T015 | `cd::test_periodo_oculto_sai_sem_remissao`; `cv::test_oculto_como_periodo_abre_as_inscricoes` |
| Mesmo início | T020 | `js::empate mantém a ordem anterior` |
| Ordem gravada com `0` ou com lacunas | T012, T014 | `cd::test_sem_oculto_imprime_o_order_com_zero_e_lacunas`; `cp::test_order_com_zero_e_lacunas_igual_ao_de_antes[…]` |
| Foco depois de mover | T029 | `nv::test_ordenar_e_as_setas_deixam_o_foco_no_botao` |
| Início incompleto ou vazio | T020, T025 | `js::sem início vai ao fim sem campo alterado`; `js::sem data de início` |
| Término vazio | T025 | `js::a prévia mostra evento, início, término e PDF, nessa ordem` (caso pontual) |
| Evento recém-acrescentado | T009, T025 | `cv::test_evento_acrescentado_nasce_exibido`; `js::a prévia acompanha os seis gestos` |
| Recusa na gravação | T009 | `cv::test_recusa_reexibe_o_oculto` |
| Rascunho local restaurado | T009 | `cv::test_restaurar_o_rascunho_local_preserva_o_oculto` |
| Somente leitura | T016, T025 | `js::somente leitura sem botão`; `cv::test_somente_leitura_tem_previa_sem_controles` |
| Sem JavaScript | T022 | `cv::test_previa_e_botoes_saem_com_hidden` |
| Edital publicado antes desta feature | T002, T014 | `el::test_v19_eleva_a_v20`; `cp::test_pdf_de_edital_antigo_igual_ao_de_antes` |
