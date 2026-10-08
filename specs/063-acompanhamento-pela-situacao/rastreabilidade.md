# Rastreabilidade — 063 · Acompanhamento pela situação do candidato

**Frase que governa**: *antes de mostrar documentos e listas, diga à pessoa a situação atual dela,
de onde essa situação decorre e o que ela precisa fazer a seguir.*

Cada linha aponta o lugar do código e o que o prende. **TU** = `tests/unit/portal/test_situacao_da_inscricao.py`;
**TA** = `tests/portal/test_acompanhamento_pela_situacao.py`; **TR** = `tests/portal/test_acompanhamento_resultado.py`;
**TC** = `tests/interface/test_portal_caminho_da_convocacao.py`; **VC** = `tests/test_vocabulario_da_convocacao.py`;
**VR** = `tests/test_vocabulario_do_requerimento.py`; **V** = a seção da [verificação](verificacao.md), medida no navegador.

P = `processo_seletivo/portal/`; S = P`situacao.py`; A = P`templates/portal/acompanhamento.html`;
B = P`templates/portal/base.html`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1166** | A `section.situacao-da-inscricao` logo depois do subtítulo: "Sua situação", "Por quê", "O que fazer" | TA `test_a_situacao_vem_antes_de_qualquer_evidencia`; V 1 |
| **FR-1167** | S `situacao_da_inscricao`, função pura; P`views.py` `acompanhamento` só a chama (D-001) | TU (todos); TA `test_a_situacao_e_os_cartoes_nao_consultam_o_banco` |
| **FR-1168** | S a precedência de sete degraus (D-002) | TU `TestCadaDegrau`, `TestDegrausVizinhos` |
| **FR-1169** | S sem argumento de corte nem de apuração; nenhuma frase de ocupação | TU `test_corte_e_apuracao_nao_sao_entradas`; TA `test_a_apuracao_vigente_nao_muda_a_situacao_de_quem_nao_foi_chamado`, varredura de toda página (`conferir_vocabulario`) |
| **FR-1170** | S `AGUARDANDO_CHAMADA` e `AGUARDANDO_DEFINITIVO`, `PROVISORIAS`; B `.rotulo-da-situacao.provisoria` | TU `test_classificado_em_definitiva_aguarda_chamada`, `test_classificado_so_em_preliminar_aguarda_definitivo`; TA `test_so_preliminar_aguarda_o_definitivo` |
| **FR-1171** | S não recebe o corte; A não o lê | TU `test_corte_e_apuracao_nao_sao_entradas` |
| **FR-1172** | S `DESFECHOS`; `_acao_do_desfecho` mantém a conferência do Requerimento enviado | TU `test_cada_desfecho_tem_o_rotulo_da_tabela`, `test_nenhum_rotulo_afirma_aprovacao`; TA `test_aceite_e_vaga_aceita`, `test_desistencia_nomeia_o_desfecho`, `test_o_indeferimento_e_a_unica_excecao_da_varredura`; TC `test_a_concluida_continua_consultavel`, `test_enviado_ve_a_conferencia_e_nao_o_chamado` |
| **FR-1173** | S `_linha_do_cartao` (com `natureza_do_cartao`), `_linha_da_convocacao`, `nome_da_lista_da_convocacao` (D-003) | TU `test_sem_natureza_no_cabecalho_usa_a_da_publicacao`, `test_lista_da_convocacao_pela_modalidade_do_perfil`, `test_lista_retirada_do_perfil_usa_o_nome_do_cartao`; TA `test_acao_prazo_e_consequencia` |
| **FR-1174** | S uma linha por cartão, sem reordenar; `MAIS_DE_UMA_LISTA` | TU `test_cada_lista_com_a_sua_posicao_oficial`, `test_uma_lista_so_nao_ganha_a_frase_das_listas`; TA `test_o_topo_diz_a_situacao_e_cada_lista_com_a_sua_posicao` |
| **FR-1175** | S `_acao_da_convocacao` (Requerimento pela política da `029`, instrução neutra); `_recurso`, que nomeia a publicação pela lista e pelo marco | TU `TestAcaoDoConvocado`, `test_prazo_aberto_vira_acao_opcional`, `test_o_recurso_de_cada_lista_diz_a_lista`, `test_o_recurso_de_etapa_continua_nomeado_pela_etapa`; TA `test_com_o_prazo_aberto_cada_lista_tem_a_sua_linha`; TA `test_acao_prazo_e_consequencia`, `test_requerimento_enviado`, `test_edital_sem_requerimento_da_a_instrucao_neutra`; TC `TestRequerimentoNaConvocacao` |
| **FR-1176** | S `_acao_da_convocacao`: prazo, `PRAZO_NAO_INICIADO`, aviso do vencimento decorrido | TU `TestConsequenciaDoConvocado`; TA `test_sem_envio_o_prazo_nao_comecou_e_nao_ha_consequencia`, `test_envio_com_falha_nao_inicia_o_prazo`; TC `test_vencimento_decorrido_nao_decide_nada_sozinho`, `test_antes_do_envio_diz_que_o_prazo_nao_comecou` |
| **FR-1177** | S `CONSEQUENCIAS` (as duas frases), a do convocado só com prazo correndo (D-005) | TU `test_prazo_em_curso_com_vencimento`, `test_sem_vencimento_nenhuma_consequencia`, `test_nenhuma_frase_de_consequencia_diz_perder`; TA `test_sem_vencimento_nenhuma_consequencia_de_prazo`, varredura "perderá" |
| **FR-1178** | S `NADA_POR_ENQUANTO` em todo degrau sem ação | TU `test_desfecho_aceite_e_vaga_aceita`, `test_prazo_aberto_vira_acao_opcional`; TA `test_o_topo_diz_a_situacao_e_cada_lista_com_a_sua_posicao` |
| **FR-1179** | S `frase_do_canal`, da frase do PDF (D-004) | TU `test_publicacao`, `test_sem_forma_declarada_nenhum_canal`; TA `test_o_canal_e_o_que_o_perfil_declara` |
| **FR-1180** | S `frase_da_reserva` (D-004) | TU `test_reserva_do_edital`, `test_perfil_retirado_nenhuma_frase`; TA `TestCadastroReserva` |
| **FR-1181** | A `section.cartao-de-lista`; `divulgacao/application/selectors.py` `situacoes_do_candidato` devolve `lista` e `lista_id`; S `ordenar_cartoes` (D-006, D-009) | TA `test_dois_cartoes_de_titulo_distinto_e_posicao_oficial`; TR `test_a_classificada_ve_natureza_posicao_pontuacao_e_o_caminho`, `test_o_caminho_leva_sempre_a_publicacao_vigente`, `test_os_dois_marcos_aparecem_na_ordem_normativa_e_nao_na_de_publicacao`; TU `test_ordem_dos_cartoes_marco_e_depois_lista_do_perfil` |
| **FR-1182** | A "Sem posição nesta lista" com o motivo | TA `test_sem_posicao_em_todas_e_nao_classificado`; TR `test_a_nao_classificada_ve_a_propria_situacao_e_o_motivo` |
| **FR-1183** | A a ordem dos blocos; P`templates/portal/_convocacao_da_inscricao.html` só com os dados (D-008) | TA `test_a_situacao_vem_antes_de_qualquer_evidencia`; TC `test_a_secao_mostra_a_chamada_o_prazo_e_o_caminho` |
| **FR-1184** | P`templates/portal/convocacao.html` com `novas_chamadas`; P`views.py` `convocacao` (D-011) | TA `test_quem_nao_foi_chamado_le_a_frase_neutra` |
| **FR-1185** | A a ausência de resultado sem bloco; a trilha só na tela da convocação; o zero do requerimento | TA `test_recem_enviada_e_inscricao_enviada`; TC `test_so_a_tela_da_convocacao_registra_leitura`; `tests/integration/requerimentos/test_orcamento_de_consulta.py`; TR `test_sem_publicacao_o_acompanhamento_nao_menciona_resultado` |

## 2. Experiência e linguagem

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-155** | A o rótulo como texto em `p.rotulo-da-situacao`; B borda tracejada no provisório | TU `test_nenhum_rotulo_afirma_aprovacao`; TA `test_o_topo_diz_a_situacao_e_cada_lista_com_a_sua_posicao` |
| **UX-156** | S frases sem termo técnico; nomes das listas por extenso | TA `conferir_vocabulario` (TECNICOS no topo, em todo cenário) |
| **UX-157** | A `h1` → `h2` → `h3`; B `overflow-wrap` no título do cartão | TA `test_titulos_sem_salto`; TC `test_sem_tabela_e_sem_estilo_embutido`; V 2 |
| **UX-158** | S e A sem as palavras proibidas | TA `conferir_vocabulario` (PROIBIDAS, em todo cenário), `TestAVarredura`; VC e VR com S e A nas listas literais |

## 3. Critérios de sucesso

| Identificador | Como se mede | Onde |
|---|---|---|
| **SC-450** | as três partes em todo estado | TU `TestCadaDegrau`; TA `test_a_situacao_vem_antes_de_qualquer_evidencia` |
| **SC-451** | títulos distintos e posição oficial por cartão | TA `test_dois_cartoes_de_titulo_distinto_e_posicao_oficial`; V 1 |
| **SC-452** | zero palavras proibidas no HTML renderizado | TA `conferir_vocabulario` em todo cenário |
| **SC-453** | só as constantes de consequência; nenhuma perda | TU `test_nenhuma_frase_de_consequencia_diz_perder`; TA varredura "perderá"; VR `test_a_excecao_e_so_a_cadeia_exata` |
| **SC-454** | a derivação roda com zero consultas | TA `test_a_situacao_e_os_cartoes_nao_consultam_o_banco` (achado A-1) |
| **SC-455** | os cinco casos pelo portal | V 1 |
| **SC-456** | 375 px sem rolagem horizontal | V 2 |
