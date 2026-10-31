# Rastreabilidade: Trilha da unidade

Caminhos relativos a `backend/`. `TI` = `tests/interface/test_trilha_da_unidade.py`;
`TS` = `tests/seguranca/test_trilha_da_unidade_acessos.py`.

| Requisito | Onde | Teste |
|---|---|---|
| FR-3152 | `processo_seletivo/interface/trilha_da_unidade.py` (`trilha_da_unidade`, só `GET`); `interface/urls.py` | TI `test_so_a_leitura_e_aceita_e_ela_nao_grava_nada` |
| FR-3153 | `trilha_da_unidade.py` (`require_authorization_base`) | TI `test_sem_a_permissao_a_recusa_diz_o_que_falta` |
| FR-3154 | `auditoria/selectors.py` (`trilha_da_unidade`, escopo do `actor`) | TI `test_nada_de_outra_unidade_de_escopo_vazio_ou_da_trilha_do_certame_aparece`, `test_o_escopo_vem_do_ator_e_nao_do_pedido`, `test_no_escopo_institucional_a_pagina_recusa_e_a_barra_nao_a_oferece`; TS `test_o_administrador_institucional_sem_unidade_nao_le` |
| FR-3155 | `interface/navegacao.py` (`SECOES`, `pode_ver_trilha_da_unidade`); `base.html` (`i-trilha`) | `tests/interface/test_shell_da_gestao.py` (`test_os_itens_sao_exatamente_os_destinos_que_abrem`, `test_cada_item_tem_icone_decorativo_e_nome_acessivel`) |
| FR-3156 | sem mudança no `PAPEIS` | `test_shell_da_gestao.py` (o Auditor alcança o destino); roteiro A do quickstart |
| FR-3157 | `auditoria/selectors.py` (`ASSUNTOS_DA_UNIDADE`) | TI `test_o_cadastro_e_o_encerramento_…`, `test_a_sincronizacao_…`, `test_os_modelos_…`, `test_o_aviso_confirmado_…`, `test_a_exclusao_do_piloto_…`; TS `test_a_concessao_e_a_revogacao_…` |
| FR-3158 | `auditoria/selectors.py` (a condição institucional do vínculo) | TS `test_a_concessao_institucional_do_administrador_da_unidade_aparece_e_a_de_outra_nao`, `test_o_filtro_de_acessos_traz_os_dois_escopos` |
| FR-3159 | `auditoria/selectors.py` | TI `test_nada_de_outra_unidade_…`; TS (entrada e suspensão fora) |
| FR-3160 | `trilha_da_unidade.py` (`_linha`); `trilha_da_unidade.html` | TI casos de leitura |
| FR-3161 | `trilha_da_unidade.html` (`nome_de_pessoa`, "Implantação") | TI `test_a_sincronizacao_…`, `test_os_modelos_…`; TS `test_a_concessao_e_a_revogacao_…` |
| FR-3162 | `trilha_da_unidade.py` (`linhas`, `_linha`, `_editais_dos_avisos`) | TI `test_o_aviso_confirmado_…`, `test_os_modelos_…`; TS (pessoa e papel) |
| FR-3163 | `trilha_da_unidade.py` (`_mudancas`, `CAMPOS_LEGIVEIS`) | TI `test_o_cadastro_e_o_encerramento_…`, `test_a_sincronizacao_…` |
| FR-3164 | `trilha_da_unidade.py` (só as chaves de `D-005`) | TI `test_os_modelos_…` (sem assunto nem corpo), `test_o_aviso_confirmado_…` (sem `@`); TS (sem `pessoa-`, sem e-mail) |
| FR-3165 | `interface/views.py` (`OPERACOES`); `trilha_da_unidade.py` (`SITUACOES`, `_rotulo_da_operacao`) | TI `test_toda_operacao_dos_assuntos_tem_rotulo_…`, `test_a_lista_literal_e_a_do_codigo` |
| FR-3166 | `auditoria/selectors.py` (`_paginar`) | TI `test_a_paginacao_nao_repete_nem_pula`, `test_atos_no_mesmo_instante_ficam_em_ordem_estavel`, `test_o_cursor_adulterado_e_recusado` (inclusive o bem formado por fora) |
| FR-3167 | `trilha_da_unidade.py` (`assunto`); `trilha_da_unidade.html` (filtro) | TI `test_cada_assunto_mostra_so_os_seus_atos_…`, `test_filtro_sem_atos_e_filtro_desconhecido` |
| FR-3168 | `trilha_da_unidade.py` (`_editais_dos_avisos`) | TI `test_o_custo_da_pagina_nao_cresce_com_as_linhas` |
| FR-3169 | só leitura | TI `test_so_a_leitura_e_aceita_e_ela_nao_grava_nada` |
| FR-3170 | `interface/static/interface/telas/trilha-da-unidade.css` | `tests/interface/test_folha_estatica.py` (`QUEM_CARREGA`); guardiões de classe e de CSP da suíte |
| FR-3171 | `doc/implantacao-em-producao-ubuntu.md`, §20.3 | leitura |
| SC-1021 | — | TI e TS: cada ato produzido pelo comando aparece, e a contagem confere |
| SC-1022 | — | TI `test_nada_de_outra_unidade_…`; TS |
| SC-1023 | — | TI `test_o_custo_da_pagina_nao_cresce_com_as_linhas` |
| SC-1024 | — | TI `test_os_modelos_…`, `test_o_aviso_confirmado_…`; TS |
| SC-1025 | — | roteiro A do quickstart, executado em 30/10/2026 (verificação) |
| SC-1026 | — | `make lint check test-pg` (verificação) |
