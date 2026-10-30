# Rastreabilidade: Ações disponíveis

Requisito → tarefa → teste. Caminhos de teste relativos a `backend/tests/`. `acoes` é
`interface/test_acoes_disponiveis.py`; `escala` é `performance/test_trabalho_em_escala.py`;
`unit` é `unit/interface/test_trabalho_do_ator.py`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2801 (derivação de leitura, sem autorizar nem persistir) | T009 | `acoes` (todos os casos leem `trabalho.do_ator` pela Lista); nenhuma migration (FR-2829) |
| FR-2802 (um objeto, um item, ato principal) | T009 | `acoes::test_e_quem_acumula_papeis_ve_um_item_por_objeto`, `::test_g_varios_procedimentos_ordenados_e_sem_duplicidade` |
| FR-2803 (sem ato que o domínio recusaria; pendência só no detalhe) | T009, T006 | `acoes::test_e_a_publicacao_que_a_segregacao_recusa_nao_entra`, `::test_d_quem_submeteu_e_homologou_nao_ve_publicar_como_acao`, `::test_d_a_lista_nao_oferece_submeter_que_a_validacao_pode_recusar` |
| FR-2804 (cobertura: Edital, Retificação, recursos, avaliação) | T009 | `acoes::test_d_…` (Edital), `::test_a_…` (Retificação), `::test_os_recursos_que_aguardam_decisao_sao_um_item_por_edital`, `::test_a_etapa_com_inscricoes_a_avaliar_e_um_item_e_conta_o_que_falta` |
| FR-2805 (escopo) | T009 | `acoes::test_i_outra_unidade_nao_ve_item_nem_marca` |
| FR-2806 (consultas não crescem com Editais) | T003, T004, T009 | `escala::test_a_derivacao_nao_cresce_com_o_numero_de_editais` |
| FR-2807 (faixa antes do inventário, depois dos avisos) | T011 | `acoes::test_a_o_homologador_ve_a_retificacao_na_primeira_tela_e_ela_some_para_todos` (ordem no HTML) |
| FR-2808 (sem faixa nem zero quando não há ação) | T011 | `acoes::test_f_sem_acao_nao_ha_faixa_nem_zero`; `escala::test_a_faixa_em_escala_continua_vazia_para_quem_nao_tem_acao` |
| FR-2809 (natureza, Edital, situação, desde, ato, destino) | T009, T011 | `acoes::test_a_…` (url e `desde`), `::test_d_quem_submeteu…` (Edital homologado com `desde`), `::test_os_recursos…`, `::test_a_etapa…` (urls) |
| FR-2810 (cinco e "Mostrar os outros") | T011 | `unit::test_a_faixa_mostra_cinco_e_guarda_o_resto`; `acoes::test_g_…` ("Mostrar os outros 1") |
| FR-2811 (sem atribuição nominal) | T011 | rótulos em `unit::test_os_rotulos_distinguem_a_devolvida_e_a_reenviada`; texto da faixa em [verificacao.md](verificacao.md) |
| FR-2812 (diz o que não cobre) | T009, T011 | `unit::test_a_faixa_diz_o_que_nao_cobre` |
| FR-2813 (lista, 375 px, teclado, sem cor) | T011, T019 | `interface/test_acessibilidade.py` (classes com regra); navegador em [verificacao.md](verificacao.md) |
| FR-2814 (ato da Retificação na coluna, sem "Nenhuma ação") | T007, T008 | `acoes::test_a_coluna_tem_o_ato_e_nao_diz_nenhuma_acao` |
| FR-2815 ("Conferir e…" no lugar de submeter e publicar) | T006 | `acoes::test_d_a_lista_nao_oferece_submeter_que_a_validacao_pode_recusar`; `interface/test_acoes.py::test_listagem_e_detalhe_nao_divergem` (mesmas chaves) |
| FR-2816 (segregação desabilitada na Lista) | T003, T007 | `acoes::test_d_quem_submeteu_e_homologou_nao_ve_publicar_como_acao` |
| FR-2817 (situação do Edital e da Retificação separadas) | T008 | `acoes::test_f_…` ("Retificação em revisão · aguarda quem homologa"), `::test_e_a_publicacao_que_a_segregacao_recusa_nao_entra` |
| FR-2818 (contagens em lote) | T004 | `escala::test_a_lista_inteira_nao_cresce_com_editais_publicados`; `interface/test_hardening_pos_auditoria.py::test_a_acao_de_recursos_conta_so_as_pecas_que_aguardam_decisao` (o número continua certo) |
| FR-2819 (detalhe nomeia a Retificação que espera a pessoa) | T012 | `acoes::test_o_detalhe_do_edital_nomeia_a_retificacao_que_espera_a_pessoa` |
| FR-2820 (sem ato: quem age a seguir) | T012 | `acoes::test_o_detalhe_do_edital_nomeia…` (publicadora lê "aguarda quem homologa") |
| FR-2821 (devolvida com motivo, levando à edição) | T005, T013 | `acoes::test_c_a_devolvida_se_reconhece_e_a_reenviada_tambem`; `unit::test_os_rotulos_…` |
| FR-2822 (reenviada) | T005, T013 | `acoes::test_c_…` ("Reenviada depois de devolvida.") |
| FR-2823 (sem situação nova) | T005 | `unit::test_os_rotulos_…` (lidos de `return_reason`); nenhuma migration |
| FR-2824 (tabela de alterações em homologar e devolver) | T014 | `acoes::test_a_…` ("O que esta Retificação altera (2)") |
| FR-2825 (avisos que já valiam recolhidos) | T014 | `acoes::test_a_confirmacao_separa_os_avisos_que_ja_valiam` |
| FR-2826 (publicar sem mudança de regra) | T014 | `interface/test_auditoria_passagem_da_retificacao.py`, `interface/test_jornada_da_retificacao.py` (publicação de ponta a ponta) |
| FR-2827 (Minhas Etapas diz o que cobre) | T015 | `acoes::test_i_minhas_etapas_diz_o_que_cobre_e_a_agenda_e_a_visao_seguem_de_pe`; `authorization/test_acesso_a_etapa.py` (frase preservada) |
| FR-2828 (Minhas Etapas, Agenda e Visão Geral sem mudança de função) | T016 | `acoes::test_i_minhas_etapas…`; suítes da Agenda e da Visão Geral inalteradas |
| FR-2829 (nada de permissão, estado, tabela, fila) | T021 | `makemigrations --check` sem mudança; por construção |
| SC-981 (todo homologador vê; depois, ninguém) | T016 | `acoes::test_a_…` (Bruno e Beatriz); 375 px em [verificacao.md](verificacao.md) |
| SC-982 (faixa = objetos com ato habilitado no detalhe) | T016 | `acoes::test_a_…`, `::test_b_…`, `::test_d_…`, `::test_e_…`, `::test_f_…` |
| SC-983 (nenhuma linha nega ação ao lado de ação) | T016 | `acoes::test_a_coluna_tem_o_ato_e_nao_diz_nenhuma_acao` |
| SC-984 (derivação constante com 0, 3, 30, 300) | T017 | `escala::test_a_derivacao_nao_cresce_com_o_numero_de_editais` |
| SC-985 (Lista constante) | T017 | `escala::test_a_lista_inteira_nao_cresce_com_editais_publicados` |
| SC-986 (um item por objeto para quem acumula) | T016 | `acoes::test_e_quem_acumula_papeis_ve_um_item_por_objeto` |
| SC-987 (devolvida, reenviada e rascunho distinguíveis) | T016 | `acoes::test_c_…` (os dois), `unit::test_os_rotulos_…` |
| SC-988 (sem regressão) | T018, T021 | [verificacao.md](verificacao.md) |
| SC-989 (nada rola para o lado a 375 px) | T019 | [verificacao.md](verificacao.md) |
| SC-990 (roteiro com pessoas) | T020 | pendente: roteiro em [quickstart.md](quickstart.md) |

## Matriz de cobertura dos tipos de trabalho

| Trabalho | Na faixa | Derivação | Teste |
|---|---|---|---|
| Edital em elaboração | sim, "Continuar a elaboração" | `ator.can("edital:elaborar")` e situação | `acoes::test_d_a_lista_nao_oferece_submeter…` |
| Edital em revisão | sim, "Homologar o Edital" | `atos.disponiveis` | por construção, mesmo caminho do homologado; `test_listagem_e_detalhe_nao_divergem` |
| Edital homologado | sim, "Publicar o Edital", sem segregação | `atos.disponiveis` + `participantes_em_lote` + `impede_por_segregacao` | `acoes::test_d_quem_submeteu_e_homologou_nao_ve_publicar_como_acao` |
| Retificação em elaboração / devolvida | sim, "Concluir e submeter" / "Corrigir … devolvida" | `atos_retificacao.resumo` | `acoes::test_c_…` |
| Retificação em revisão / reenviada | sim, "Analisar a Retificação" | idem | `acoes::test_a_…`, `::test_c_…` |
| Retificação homologada | sim, "Publicar a Retificação", sem segregação | `ofertas` | `acoes::test_b_…`, `::test_e_a_publicacao…` |
| Recursos aguardando decisão | sim, um por Edital | `acoes.recursos_por_edital` | `acoes::test_os_recursos_que_aguardam_decisao_sao_um_item_por_edital` |
| Avaliação em Etapa | sim, um por Etapa com pendentes | `minhas_etapas` + `carga_nas_etapas` | `acoes::test_a_etapa_com_inscricoes_a_avaliar_e_um_item_e_conta_o_que_falta` |
| Classificação (conduzir marco, emitir, corte, convocação) | não (D-002) | — | acesso preservado no detalhe do Edital; suítes da classificação inalteradas |
| Divulgação de resultado | não (D-002) | — | idem |
| Avisos aos candidatos | não (D-002) | — | idem |
