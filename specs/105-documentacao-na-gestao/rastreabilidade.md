# Rastreabilidade: A Visão do Sistema dentro da gestão

Cada requisito → a tarefa que o implementa → o teste que o verifica. Conferida contra o implementado
em 30/10/2026. Caminhos de teste relativos a `backend/`: `DOC` é
`tests/interface/test_documentacao_do_sistema.py`, `SHELL` é `tests/interface/test_shell_da_gestao.py`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2901 (item para toda identidade, grupo próprio, ícone único) | T003 | `SHELL::test_os_itens_sao_exatamente_os_destinos_que_abrem`, `::test_montar_a_barra_nao_consulta_o_banco`, `::test_cada_item_tem_icone_decorativo_e_nome_acessivel` |
| FR-2902 (toda identidade lê; sem identidade, identificação com volta) | T001, T002 | `DOC::test_toda_identidade_le_o_manual_sob_a_politica`, `::test_sem_identidade_leva_a_identificacao_e_volta_ao_manual` |
| FR-2903 (lista literal com tipo; o resto é 404) | T002, T007 | `DOC::test_arquivo_fora_da_lista_e_inexistente`, `::test_todo_arquivo_que_o_manual_pede_esta_na_lista_e_abre`; `tests/test_gramatica_das_portas.py::test_o_inventario_cobre_toda_funcao_que_responde_inexistente` |
| FR-2904 (sob a política, sem conteúdo embutido) | T004 | `DOC::test_toda_identidade_le_o_manual_sob_a_politica`, `::test_nada_no_manual_e_embutido` |
| FR-2905 (Voltar relativo ao início da gestão) | T005 | `DOC::test_o_voltar_do_manual_leva_ao_inicio_da_gestao` |
| FR-2906 (manual na imagem e no compose) | T006 | por construção; o job `compose` do CI sobe a imagem |
| SC-991 (todo arquivo pedido está na lista e abre) | T008 | `DOC::test_todo_arquivo_que_o_manual_pede_esta_na_lista_e_abre` |
| SC-992 (nada embutido) | T008 | `DOC::test_nada_no_manual_e_embutido` |
| SC-993 (fora da lista, inclusive `..`, é 404) | T008 | `DOC::test_arquivo_fora_da_lista_e_inexistente` |
