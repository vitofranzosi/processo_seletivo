# Rastreabilidade: A organização da lista de Processos Seletivos (129)

Cada identificador da spec → as tarefas que o implementam → os testes que o verificam. Caminhos
relativos a `backend/tests/`. Abreviações:

- `se` = `integration/processos/test_recorte_dos_processos.py` — o grupo, a busca e a contagem no seletor
- `un` = `unit/interface/test_lista_de_processos.py` — os parâmetros, a página e as frases
- `te` = `interface/test_organizacao_da_lista.py` — a tela
- `ac` = `interface/test_acoes.py` — a lista sem ações e a paridade faixa × detalhe
- `ad` = `interface/test_acoes_disponiveis.py` — a faixa da `104`, que continua
- `li` = `interface/test_lista.py` — a lista desde a `002`
- `es` = `performance/test_lista_em_escala.py` — o custo para todo papel
- `nv` = verificação no navegador, em [verificacao.md](verificacao.md) e `capturas/`

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4300 (abre em "Em andamento") | T006, T008 | `un::test_sem_parametro_e_a_aba_em_andamento_na_primeira_pagina`; `te::test_o_padrao_abre_em_andamento_e_o_selo_diz_a_situacao_real` |
| FR-4301 (o que é "Em andamento") | T004 | `se::test_o_grupo_de_cada_combinacao_de_processo_e_editais`; `te::test_o_padrao_abre_em_andamento_e_o_selo_diz_a_situacao_real` |
| FR-4302 (as abas particionam) | T004 | `se::test_as_tres_abas_particionam_a_unidade_e_todos_e_a_soma` |
| FR-4303 (a contagem de Processos, texto acessível) | T004, T006, T009 | `un::test_as_abas_contam_processos_e_a_busca_nao_marca_nenhuma`; `te::test_o_padrao_abre_em_andamento_e_o_selo_diz_a_situacao_real`; `li::test_a_contagem_diz_o_que_ela_conta` |
| FR-4304 (o selo real) | T009 | `te::test_o_padrao_abre_em_andamento_e_o_selo_diz_a_situacao_real`; `te::test_o_cancelado_e_achado_pelo_numero_a_partir_de_em_andamento` |
| FR-4305 (busca em todas as situações) | T004, T014 | `te::test_o_cancelado_e_achado_pelo_numero_a_partir_de_em_andamento`; `te::test_todo_processo_e_achado_pelo_numero_de_qualquer_edital_de_qualquer_aba` |
| FR-4306 (o que a busca casa) | T004 | `se::test_a_busca_por_numero_e_ano`; `se::test_a_busca_por_titulo_codigo_e_titulo_de_edital_ignora_caixa_e_espacos`; `se::test_barra_incompleta_se_busca_como_texto`; `un::test_busca_sem_espacos_nas_pontas_e_cortada` |
| FR-4307 (só a unidade da sessão) | T004 | `se::test_outra_unidade_nao_aparece_nem_na_busca_nem_na_contagem`; `li::test_lista_nao_revela_processo_de_outro_escopo` |
| FR-4308 (a ordem da busca) | T004 | `se::test_a_busca_ordena_por_grupo_e_depois_pela_ordem_das_abas`; `se::test_a_ordem_e_do_mais_recente_ao_mais_antigo` |
| FR-4309 (a frase da busca, nenhuma aba marcada) | T006, T014 | `un::test_a_frase_da_busca_diz_onde_procurou_e_quantos_sao_finais`; `un::test_as_abas_contam_processos_e_a_busca_nao_marca_nenhuma`; `te::test_o_cancelado_e_achado_pelo_numero_a_partir_de_em_andamento` |
| FR-4310 (busca sem resultado) | T006, T014 | `un::test_a_busca_sem_resultado`; `te::test_a_busca_sem_resultado_mantem_o_texto_e_oferece_limpar` |
| FR-4311 (20 por página, Editais juntos) | T006, T008 | `te::test_61_processos_vinte_por_pagina_com_a_navegacao`; `te::test_a_busca_traz_o_processo_com_todos_os_editais` |
| FR-4312 (a frase do total e a navegação) | T006, T009 | `un::test_a_frase_do_recorte`; `un::test_pagina_alem_da_ultima_e_a_ultima_e_o_intervalo`; `te::test_61_processos_vinte_por_pagina_com_a_navegacao` |
| FR-4313 (o recorte no endereço) | T006, T008 | `te::test_61_processos_vinte_por_pagina_com_a_navegacao`; `nv` (o voltar do navegador) |
| FR-4314 (troca de aba e nova busca voltam à 1) | T006 | `un::test_os_links_de_pagina_preservam_a_aba_e_a_busca`; `te::test_trocar_de_aba_volta_a_pagina_um_e_os_links_preservam_a_aba`; `te::test_a_busca_pagina_e_os_links_preservam_o_termo` |
| FR-4315 (parâmetros inválidos sem erro) | T006 | `un::test_aba_invalida_cai_em_andamento`; `un::test_pagina_invalida_vai_para_a_primeira`; `te::test_61_processos_vinte_por_pagina_com_a_navegacao` |
| FR-4316 (barra e trilha levam ao padrão, sem sessão) | T006, T009 | `te::test_o_processo_sem_edital_e_a_navegacao_sem_memoria` |
| FR-4317 (a linha do Processo) | T016 | `te::test_quem_gere_ve_comissao_e_alocacao_e_quem_nao_gere_nao_ve`; `li::test_o_estado_do_processo_fica_com_o_nome_dele`; `test_oferta_da_comissao.py` e `test_caminho_ate_a_mesa.py`, inalterados |
| FR-4318 (a linha do Edital) | T016 | `te::test_a_linha_do_edital_omite_o_titulo_igual_e_nao_e_tabela`; `ad::test_a_linha_tem_a_marca_e_o_ato_fica_na_faixa`; `ad::test_c_a_devolvida_se_reconhece_e_a_reenviada_tambem` |
| FR-4319 (nenhuma ação na lista) | T016, T017, T018 | `ac::test_a_lista_nao_apresenta_acao_de_edital` (todo papel de `PAPEIS` e todos juntos); `ad::test_d_a_lista_nao_oferece_submeter_que_a_validacao_pode_recusar`; `ad::test_d_quem_submeteu_e_homologou_nao_ve_publicar_como_acao`; `ad::test_os_recursos_que_aguardam_decisao_sao_um_item_por_edital` |
| FR-4320 (não é tabela; 375 px sem rolar) | T016 | `te::test_a_linha_do_edital_omite_o_titulo_igual_e_nao_e_tabela`; `li::test_estrutura_acessivel_da_lista`; `nv` (a 375 px) |
| FR-4321 (sai o resumo por Edital) | T008 | `li::test_a_contagem_diz_o_que_ela_conta` |
| FR-4322 (o nome da Unidade) | T008 | `te::test_o_subtitulo_nomeia_a_unidade_e_a_ordem_de_leitura` |
| FR-4323 (a faixa lê a unidade) | T008, T012 | `te::test_o_recurso_de_processo_encerrado_aparece_na_faixa_em_toda_aba`; `te::test_o_edital_em_elaboracao_da_pagina_dois_esta_na_faixa_da_pagina_um`; `te::test_a_faixa_e_identica_em_toda_aba_busca_e_pagina` |
| FR-4324 (a nota antes dos itens) | T020 | `te::test_a_nota_vem_antes_do_primeiro_item_e_nomeia_as_familias`; `unit/interface/test_trabalho_do_ator.py` |
| FR-4325 (a frase vazia, da mesma fonte) | T020 | `te::test_a_frase_vazia_nomeia_as_mesmas_familias_da_mesma_fonte`; `performance/test_trabalho_em_escala.py::test_a_faixa_em_escala_continua_vazia_para_quem_nao_tem_acao` |
| FR-4326 (a faixa da `104` continua) | T012 | `ad` inteiro (ordem, limite de cinco, "Mostrar os outros", título); `performance/test_trabalho_em_escala.py::test_a_faixa_com_1_5_25_e_100_objetos_mostra_cinco_e_nao_cresce_em_consultas` |
| FR-4327 (consultas constantes, todo papel) | T021 | `es::test_as_consultas_da_lista_nao_crescem_nem_mudam_com_o_recorte` (11 casos: os 10 papéis e todos juntos); `se::test_a_contagem_com_e_sem_busca_custa_uma_consulta` |
| FR-4328 (o que é por Edital, em lote) | T008, T017 | `es::test_as_consultas_da_lista_nao_crescem_nem_mudam_com_o_recorte` (o exportador, com metade dos Editais declarando o Requerimento); leitura da view: os Editais e as Retificações em curso lidos uma vez para a unidade |
| FR-4329 (a paridade na forma nova) | T015, T018 | `ac::test_a_lista_nao_apresenta_acao_de_edital`; `ac::test_o_ato_de_edital_que_a_faixa_nomeia_o_detalhe_tambem_oferece` (elaborar, homologar, publicar) |

## Experiência

| Requisito | Tarefas | Testes |
|---|---|---|
| UX-270 (abas como navegação, `aria-current`, traço, contagem no nome) | T009, T010 | `te::test_o_padrao_abre_em_andamento_e_o_selo_diz_a_situacao_real`; `li::test_estrutura_acessivel_da_lista`; a regra `.aba-da-lista[aria-current="page"]` com `border-bottom` em `telas/lista.css`; `nv` |
| UX-271 (rótulo visível, Enter e botão, texto mantido) | T014 | `li::test_estrutura_acessivel_da_lista`; `te::test_o_cancelado_e_achado_pelo_numero_a_partir_de_em_andamento`; `te::test_a_busca_sem_resultado_mantem_o_texto_e_oferece_limpar` |
| UX-272 (a ordem de leitura) | T009 | `te::test_o_subtitulo_nomeia_a_unidade_e_a_ordem_de_leitura` |
| UX-273 (a frase antes dos resultados; "Limpar a busca" é link) | T014 | `te::test_o_cancelado_e_achado_pelo_numero_a_partir_de_em_andamento` |
| UX-274 (texto, e não só cor) | T016 | `te::test_o_padrao_abre_em_andamento_e_o_selo_diz_a_situacao_real` (o selo por texto); `ad::test_a_linha_tem_a_marca_e_o_ato_fica_na_faixa` (a marca por texto) |

## Critérios de sucesso

| Critério | Como se mede | Onde |
|---|---|---|
| SC-1310 (telas a 900 px e a 375 px) | altura da página padrão do gestor no banco de demonstração de 200 Processos | `nv` |
| SC-1311 (todo Processo achado pelo "N/AAAA") | `te::test_todo_processo_e_achado_pelo_numero_de_qualquer_edital_de_qualquer_aba` | automático |
| SC-1312 (a faixa idêntica) | `te::test_a_faixa_e_identica_em_toda_aba_busca_e_pagina` (quatro combinações de papéis, sete recortes); `te::test_o_recurso_de_processo_encerrado_aparece_na_faixa_em_toda_aba` | automático |
| SC-1313 (crescimento zero) | `es::test_as_consultas_da_lista_nao_crescem_nem_mudam_com_o_recorte` | automático |
| SC-1314 (nenhum "Nenhuma ação" nem contador zerado) | `ac::test_a_lista_nao_apresenta_acao_de_edital` | automático |
| SC-1315 (validação com pessoas) | sessão com duas pessoas da equipe | **pendente, humano** |

## Decisões

| Decisão | Onde vive |
|---|---|
| D-001 (o recorte pelo Processo) | `selectors.grupo_do_processo`; `se::test_o_grupo_de_cada_combinacao_de_processo_e_editais` |
| D-002 (quatro abas) | `lista_de_processos.ABAS`; `un::test_as_abas_contam_processos_e_a_busca_nao_marca_nenhuma` |
| D-003 (a linha só diz fatos) | `lista.html`; `ac::test_a_lista_nao_apresenta_acao_de_edital`; o código que só a coluna usava saiu (R-6) |
| D-004 (a busca ignora a aba) | `selectors.listar_processos`; `te::test_todo_processo_e_achado_pelo_numero_de_qualquer_edital_de_qualquer_aba` |
| D-005 (20 por página, endereço, sem sessão) | `lista_de_processos.POR_PAGINA`; `te::test_o_processo_sem_edital_e_a_navegacao_sem_memoria` |
| D-006 (a faixa lê a unidade) | `views.lista`, `selectors.editais_da_unidade`; os casos de FR-4323 |
| D-007 (o custo do exportador) | `es::test_as_consultas_da_lista_nao_crescem_nem_mudam_com_o_recorte` |
| D-008 (o que a página não decide) | nenhuma mudança em encerramento, arquivamento ou na confirmação de "Encerrar Processo" (o diff não toca `processo_detalhe.html` nem `finalizacao.py`) |
