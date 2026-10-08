# Rastreabilidade — 062 · Resultados divulgados por Perfil, etapa e lista

**Frase que governa**: *o resultado pertence à vaga.*

Cada linha aponta o lugar do código e o que o prende. **TR** = `tests/portal/test_resultados_por_perfil.py`;
**TH** = `tests/portal/test_historico_de_resultados.py`; **TP** = `tests/portal/test_prazo_recursal_publico.py`;
**TO** = `tests/portal/test_resultado_publico.py`; **TA** = `tests/interface/test_acessibilidade_do_portal.py`;
**V** = a seção da [verificação](verificacao.md), medida no navegador.

P = `processo_seletivo/portal/`; S = P`templates/portal/selecao.html`; B = P`templates/portal/base.html`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1148** | P`leitura.py` `resultados_por_perfil`; P`views.py` `selecao`; S o bloco em `div.resultados-do-perfil` › `div.resultados-da-etapa` › `li.lista-divulgada` (D-005) | TR `test_um_grupo_por_perfil_na_ordem_da_secao_vagas`, `test_a_etapa_e_titulo_e_cada_lista_traz_natureza_e_data_na_linha`; V 1 |
| **FR-1149** | P`leitura.py`: posição em `profiles`; ausentes por último | TR `test_os_perfis_seguem_a_ordem_da_secao_vagas_e_nao_a_da_publicacao`, `test_o_perfil_retirado_vem_por_ultimo_com_o_nome_gravado`, `test_um_grupo_por_perfil_na_ordem_da_secao_vagas` |
| **FR-1150** | P`leitura.py`: etapas por `marco_codigo` (D-010) | TR `test_as_etapas_seguem_a_ordem_do_certame_e_nao_a_da_divulgacao`, `test_so_a_etapa_com_sucedida_tem_historico` |
| **FR-1151** | P`leitura.py` `_chave_da_lista` (D-008) | TR `test_a_ampla_vem_primeiro_e_as_listas_na_ordem_declarada_pelo_perfil` |
| **FR-1152** | P`leitura.py`: nome vigente, congelado de reserva; `divulgacao/application/selectors.py` `_rotulos` devolve `perfil` (D-009) | TR `test_o_nome_do_perfil_e_o_vigente_e_nao_o_gravado`, `test_o_perfil_retirado_vem_por_ultimo_com_o_nome_gravado` |
| **FR-1153** | P`leitura.py` `_etapa`: o marco da vigente mais recente; S `h4` | TR `test_o_titulo_da_etapa_e_o_da_vigente_mais_recente`, `test_a_etapa_e_titulo_e_cada_lista_traz_natureza_e_data_na_linha` |
| **FR-1154** | S o link com o nome da lista e `span.oculto` " — etapa — Perfil"; B `.oculto` (D-006) | TR `test_a_etapa_e_titulo_e_cada_lista_traz_natureza_e_data_na_linha`, `test_os_dois_ampla_concorrencia_se_distinguem_pelo_nome_acessivel`; TH `test_as_ordens_de_um_mesmo_marco_tem_links_que_se_distinguem`; V 1 |
| **FR-1155** | S natureza e data só em `span.meta` da linha | TR `test_listas_em_fases_diferentes_dizem_cada_uma_a_sua`, `test_mesmo_com_todas_iguais_a_natureza_fica_na_linha` |
| **FR-1156** | S `span.prazo-recursal` dentro de `li.lista-divulgada`; B `.lista-divulgada .prazo-recursal` | TP `test_prazo_aberto_na_pagina_do_resultado_e_na_lista_do_edital`, `test_prazo_encerrado_diz_quando_e_some_da_lista` |
| **FR-1157** | S um `details.publicacoes-anteriores` por etapa, com o total; nenhum sem sucedida (D-001) | TR `test_um_historico_por_etapa_com_a_lista_de_cada_item`, `test_so_a_etapa_com_sucedida_tem_historico`, `test_a_etapa_sem_publicacao_sucedida_tem_historico_vazio`; V 1 |
| **FR-1158** | S o item do histórico: nome da lista, `span.oculto` com natureza, data, etapa e Perfil, `span.meta` com "sucedido" | TR `test_um_historico_por_etapa_com_a_lista_de_cada_item`; TO `test_a_vitrine_do_edital_anuncia_so_a_vigente`; TH `test_o_preliminar_sucedido_esta_a_um_clique_da_pagina_do_edital` |
| **FR-1159** | P`leitura.py` `_etapa`: anteriores na ordem das listas, cada cadeia inteira | TR `test_o_historico_da_etapa_junta_as_listas_sem_misturar_as_cadeias`; TH `test_o_historico_de_uma_lista_nao_aparece_sob_outra`, `test_a_cadeia_de_tres_aparece_em_ordem_e_so_a_ultima_e_vigente` |
| **FR-1160** | S `aside.convite-da-situacao` depois dos Perfis; P`views.py` `_convite_da_situacao` (D-002) | TR `test_sem_sessao_o_convite_leva_a_entrada_com_volta_ao_edital`; V 1 |
| **FR-1161** | P`views.py` `_convite_da_situacao` (sem sessão), `_de_volta_a_vaga` reconhece `portal:selecao`, `_entrar` só pede o núcleo a caminho de vaga (D-007) | TR `test_sem_sessao_o_convite_leva_a_entrada_com_volta_ao_edital`, `test_o_destino_na_pagina_do_edital_volta_ao_bloco_de_resultados`, `test_voltar_ao_edital_nao_pede_nome_e_cpf_e_a_vaga_continua_pedindo`; V 3 |
| **FR-1162** | P`views.py` `_convite_da_situacao`: uma enviada → acompanhamento; mais → lista (D-003) | TR `test_com_uma_enviada_o_convite_leva_direto_ao_acompanhamento`, `test_com_duas_enviadas_o_convite_leva_a_lista`; V 3 |
| **FR-1163** | P`views.py` `_convite_da_situacao` devolve `None` | TR `test_conectado_sem_enviada_nao_ha_convite` |
| **FR-1164** | S `section.resultados` com `em-destaque` quando não recebe inscrições, como antes | TR `test_o_destaque_segue_o_recebimento_de_inscricoes` |
| **FR-1165** | Nenhum modelo, migration, documento ou página de publicação tocados; `_rotulos` só acrescenta chave | TO (a página da publicação, inteira, verde sem mudança); TH `test_a_pagina_do_definitivo_leva_as_anteriores` |

## 2. Critérios de sucesso

| Identificador | O que o prende |
|---|---|
| **SC-443** | TR `test_um_grupo_por_perfil_na_ordem_da_secao_vagas`, `test_os_dois_ampla_concorrencia_se_distinguem_pelo_nome_acessivel` |
| **SC-444** | TR `test_os_dois_ampla_concorrencia_se_distinguem_pelo_nome_acessivel`; TH `test_as_ordens_de_um_mesmo_marco_tem_links_que_se_distinguem`; V 1 (13 links, 13 nomes) |
| **SC-445** | TR `test_listas_em_fases_diferentes_dizem_cada_uma_a_sua` |
| **SC-446** | TR `test_um_historico_por_etapa_com_a_lista_de_cada_item`, `test_so_a_etapa_com_sucedida_tem_historico` |
| **SC-447** | TR `test_com_uma_enviada_o_convite_leva_direto_ao_acompanhamento`; V 3 |
| **SC-448** | TR `test_o_custo_da_pagina_nao_cresce_com_as_publicacoes`; TP `test_a_lista_do_edital_nao_consulta_a_cadeia_degrau_por_degrau` (D-011) |
| **SC-449** | V 2 (`scrollWidth` 375); TA `test_nada_no_portal_fixa_largura_em_pixel` |

## 3. Apresentação e acessibilidade

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-151** | S `h2` › `h3` › `h4`; B pesos dos títulos (V 1) | TR `test_a_etapa_e_titulo_e_cada_lista_traz_natureza_e_data_na_linha`; V 1 |
| **UX-152** | S `span.oculto` depois do texto visível | TR `test_os_dois_ampla_concorrencia_se_distinguem_pelo_nome_acessivel`; V 1 |
| **UX-153** | B `.lista-divulgada` com `flex-wrap`, prazo em linha própria | V 2; TA `test_nada_no_portal_fixa_largura_em_pixel` (com a exceção de 0 e 1 px, escrita no próprio teste) |
| **UX-154** | S "sucedido" em texto no item do histórico | TR `test_um_historico_por_etapa_com_a_lista_de_cada_item`; TH `test_o_preliminar_sucedido_esta_a_um_clique_da_pagina_do_edital` |
