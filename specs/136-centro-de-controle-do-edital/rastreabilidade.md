# Rastreabilidade: Centro de Controle do Edital (136)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`. Abreviações:

- `cc` = `unit/interface/test_centro_composicao.py` — as regras puras
- `ce` = `interface/test_centro_do_edital.py` — a rota, a porta, os links e os casos-limite
- `cn` = `integration/treinamento/test_centro_nos_cenarios.py` — C06, C08 e C12 com quatro papéis
- `es` = `performance/test_centro_em_escala.py` — o orçamento de consultas
- `nv` = `navegador/test_jornada_do_centro.py` — a dobra, 375 px, a CSP e o teclado
- `gp` = `test_gramatica_das_portas.py` — o inventário das negativas

A faixa abre em **FR-4700**, **SC-1470** e **UX-314**. Gastos até FR-4748, SC-1480 e UX-318; o resto
da reserva (até o requisito quatro mil setecentos e cinquenta e nove, o critério mil quatrocentos e
oitenta e nove e o UX trezentos e vinte e nove) fica livre.

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-4700 — a página na rota própria | T006 | `ce::test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele` |
| FR-4701 — a porta do detalhe | T006, T007 | `ce::test_o_edital_de_outra_unidade_e_inexistente`, `ce::test_sem_identidade_pede_identificacao`, `gp::test_o_inventario_cobre_toda_funcao_que_responde_inexistente` |
| FR-4702 — sem andamento, o detalhe | T006 | `ce::test_antes_da_publicacao_o_centro_leva_ao_detalhe` |
| FR-4703 — o detalhe só ganha o link | T019 | `ce::test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele`, `ce::test_antes_da_publicacao_o_centro_leva_ao_detalhe`; a suíte do detalhe sem alteração |
| FR-4704 — o link de volta | T008 | `ce::test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele` |
| FR-4705 — a fonte das situações | T004, T006 | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` (a coerência, `conferir_coerencia`) |
| FR-4706 — nenhuma regra nova; o link do ato | T011 | `cn::test_c06` (o link do destaque é o da providência) |
| FR-4707 — quem não pratica não recebe o link | T012 | `cn::test_c06` (`c06_quem_nao_pratica_nao_recebe_o_link_e_a_tela_real_recusa`) |
| FR-4708 — oito fases em três grupos | T004, T008 | `cc::test_o_mapa_tem_oito_fases_em_tres_grupos`, `ce::test_o_mapa_tem_oito_fases_e_uma_so_consultada` |
| FR-4709 — a fase de cada ponto | T004 | `cc::test_cada_ponto_tem_a_sua_fase` |
| FR-4710 — o andamento numa lista | T004 | `cc::test_agregar_segue_a_tabela`, `cc::test_concluida_se_e_so_se_tudo_feito_ou_nao_se_aplica_com_algum_feito` |
| FR-4711 — o andamento no Edital | T004 | `cc::test_juntar_segue_a_tabela`, `cc::test_varias_fases_em_curso_ao_mesmo_tempo` |
| FR-4712 — a fase Edital | T004 | `cc::test_a_retificacao_em_curso_poe_o_edital_em_curso`, `ce::test_a_retificacao_em_curso_aparece_e_poe_o_edital_em_curso` |
| FR-4713 — a fase Inscrições | T004 | `cc::test_a_fase_inscricoes_segue_o_periodo` |
| FR-4714 — a Conclusão não diz que se pode encerrar | T004 | `cc::test_a_conclusao_nunca_diz_que_o_edital_pode_ser_encerrado`, `cc::test_selecao_concluida_por_fixture` |
| FR-4715 — o que a fase oferece, separado | T004, T008 | `cc::test_a_fase_em_curso_sem_providencia_diz_nada_a_fazer`, `cn::test_c12` |
| FR-4716 — cada providência numa fase só | T004 | `cc::test_toda_natureza_da_127_tem_fase_propria`, `cc::test_a_providencia_da_etapa_governada_e_de_vagas_pelo_id_e_nao_pelo_nome`, `cc::test_cada_providencia_esta_numa_fase_so_e_a_marca_sua_segue_as_providencias`, `cn::test_c06` |
| FR-4717 — a marca "sua" se, e só se | T004, T008 | `cc::test_cada_providencia_esta_numa_fase_so_e_a_marca_sua_segue_as_providencias`, `cn::test_c06`, `cn::test_c08`, `cn::test_c12` |
| FR-4718 — "Onde estamos" nomeia as fases | T004, T008 | `cc::test_onde_estamos_nomeia_as_fases_e_diz_de_quem_e`, `cc::test_nada_em_aberto_diz_o_que_esta_em_curso`, `cc::test_selecao_concluida_por_fixture` |
| FR-4719 — de quem é | T004 | `cc::test_onde_estamos_nomeia_as_fases_e_diz_de_quem_e`, `cn::test_c12` |
| FR-4720 — três estados | T008 | `ce::test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele` |
| FR-4721 — o papel em palavras | T004 | `cc::test_o_papel_em_palavras` |
| FR-4722 — as três regras do destaque | T004 | `cc::test_c06_destaca_fixar_os_participantes_e_diz_o_que_espera_por_ela`, `cc::test_uma_acao_so_e_destacada_por_ser_a_unica`, `cc::test_duas_acoes_independentes_nao_tem_destaque`, `cc::test_o_destaque_e_sempre_uma_providencia_sua` |
| FR-4723 — "Por que esta" | T011 | `cn::test_c06`, `cn::test_c08` |
| FR-4724 — sem destaque, o GPS não escolhe | T011 | `cc::test_duas_acoes_independentes_nao_tem_destaque`, `cn::test_c12` |
| FR-4725 — a paralela | T004 | `cc::test_a_etapa_que_o_sorteio_nao_le_e_paralela`, `cc::test_com_etapa_de_habilitacao_nao_ha_paralela`, `cc::test_com_um_perfil_de_pontuacao_a_etapa_nao_e_paralela`, `cc::test_sem_etapa_nao_ha_paralela` |
| FR-4726 — a ordem do cartão | T011 | `cn::test_c06` ("Também sua" depois do destaque), `cn::test_c12` |
| FR-4727 — "Nenhuma ação é sua", "Nada em aberto" | T011 | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` (`conferir_papel`), `ce::test_o_edital_sem_inscricao_nao_tem_nada_em_aberto`, `cc::test_sem_acao_sua_nao_ha_destaque_nem_frase` |
| FR-4728 — as Retificações em curso | T011 | `ce::test_a_retificacao_em_curso_aparece_e_poe_o_edital_em_curso` |
| FR-4729 — o nome simples antes do jargão | T004, T011 | `cc::test_c06_destaca_fixar_os_participantes_e_diz_o_que_espera_por_ela`, `cn::test_c06` |
| FR-4730 — uma fase consultada | T004 | `cc::test_a_fase_consultada_e_a_pedida_ou_a_do_destaque`, `cc::test_sem_destaque_a_paralela_vem_por_ultimo`, `cc::test_sem_providencia_a_consultada_e_a_primeira_em_curso` |
| FR-4731 — `aria-current` só na consultada | T008, T014 | `cn::test_c12`, `ce::test_o_mapa_tem_oito_fases_e_uma_so_consultada` |
| FR-4732 — o que o detalhe da fase diz | T013 | `cn::test_c06` (a razão do passo da semente), `ce::test_a_fase_por_lista_traz_o_roteiro_e_o_porque_recolhido` |
| FR-4733 — o roteiro e a tabela por lista | T013 | `cc::test_o_roteiro_diz_por_que_o_passo_ainda_nao_comecou`, `ce::test_a_fase_por_lista_traz_o_roteiro_e_o_porque_recolhido`, `cn::test_c06` |
| FR-4734 — sem a matriz, sem tabela | T013 | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` (`conferir_papel`) |
| FR-4735 — o detalhe das fases do Edital | T013 | `ce::test_as_fases_do_edital_tem_detalhe_proprio` |
| FR-4736 — o porquê recolhido | T013 | `ce::test_a_fase_por_lista_traz_o_roteiro_e_o_porque_recolhido` |
| FR-4737 — onde cada lista está | T015 | `cn::test_c12` (`c12_a_lista_ppp_aparece_com_o_que_falta_nela`) |
| FR-4738 — a matriz da `127` recolhida | T015 | `cn::test_c06` (`conferir_papel`: a seção e as tabelas para quem vê a matriz) |
| FR-4739 — sem a matriz, sem a seção | T015 | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` (`conferir_papel`) |
| FR-4740 — administração e histórico | T017 | `ce::test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele` |
| FR-4741 — Encerrar e Cancelar recolhidos | T017 | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` (`conferir_papel`) |
| FR-4742 — os conceitos num módulo, provisórios | T003 | `cc::test_os_conceitos_se_declaram_provisorios`, `cc::test_nenhum_texto_dos_conceitos_usa_termo_que_a_tela_nao_define` |
| FR-4743 — o conceito completo de cada passo | T003 | `cc::test_todo_tipo_de_ponto_tem_conceito_completo` |
| FR-4744 — o orçamento | T021 | `es::test_o_sorteio_nao_cresce_com_as_inscricoes`, `es::test_a_pontuacao_com_etapas_nao_cresce_com_as_inscricoes` |
| FR-4745 — CSP | T009, T022 | `nv::test_o_c06_na_primeira_dobra_sem_rolagem_e_sem_violacao`; os guardiões de estáticos e de acessibilidade |
| FR-4746 — 375 px | T009, T022 | `nv::test_o_c06_na_primeira_dobra_sem_rolagem_e_sem_violacao` |
| FR-4747 — o teclado | T022 | `nv::test_o_tab_percorre_o_mapa_antes_das_providencias` |
| FR-4748 — sinal com palavra | T008 | `ce::test_o_mapa_tem_oito_fases_e_uma_so_consultada` |

## Experiência

| Requisito | Tarefa | Teste |
|---|---|---|
| UX-314 — andamento na borda, providências nas marcas, legenda | T008, T009 | `cn::test_c06` (marcas por fase), conferência no navegador (`verificacao.md`) |
| UX-315 — o realce da consultada | T009 | `cn::test_c12`, conferência no navegador |
| UX-316 — o bloco da ação destacada | T011 | `cn::test_c06` |
| UX-317 — a grade e os pontos de quebra | T009 | `nv::test_o_c06_na_primeira_dobra_sem_rolagem_e_sem_violacao` |
| UX-318 — a linha de validação | T008 | `ce::test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele` |

## Critérios de sucesso

| Critério | Teste |
|---|---|
| SC-1470 — a primeira dobra | `nv::test_o_c06_na_primeira_dobra_sem_rolagem_e_sem_violacao`; C08 e C12 na conferência do navegador |
| SC-1471 — os destaques do C06, C08 e C12 | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` |
| SC-1472 — consultada × em curso no C12 | `cn::test_c12` |
| SC-1473 — a coerência | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` (`conferir_coerencia`), `cc::test_concluida_se_e_so_se_tudo_feito_ou_nao_se_aplica_com_algum_feito` |
| SC-1474 — os quatro papéis | `cn::test_c06`, `cn::test_c08`, `cn::test_c12` (`conferir_papel`) |
| SC-1475 — o link e a recusa | `cn::test_c06` |
| SC-1476 — o orçamento | `es::test_o_sorteio_nao_cresce_com_as_inscricoes`, `es::test_a_pontuacao_com_etapas_nao_cresce_com_as_inscricoes` |
| SC-1477 — 375 px e a CSP | `nv::test_o_c06_na_primeira_dobra_sem_rolagem_e_sem_violacao` |
| SC-1478 — o detalhe e os dois links | `ce::test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele`; a suíte do detalhe sem alteração |
| SC-1479 — os guardiões | `make test-pg` (ver `verificacao.md`) |
| SC-1480 — os casos-limite | `ce::test_o_edital_sem_inscricao_nao_tem_nada_em_aberto`, `ce::test_a_retificacao_em_curso_aparece_e_poe_o_edital_em_curso`, `cc::test_dois_perfis_no_mesmo_edital_por_fixture`, `cc::test_selecao_concluida_por_fixture`, `cc::test_o_impedimento_fica_na_espera_com_quem_resolve`, `cn::test_c08` (prazo) |
