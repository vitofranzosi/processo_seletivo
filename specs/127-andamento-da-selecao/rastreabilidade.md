# Rastreabilidade: Andamento da seleção (127)

Cada requisito, critério, identificador de UX e caso-limite da spec, com o que o prende. Caminhos
relativos a `backend/`. **B1** está neste PR; **B2** e as transições estão marcados onde entram.

Arquivos de teste, abreviados:

- `sit` = `tests/unit/interface/test_andamento_situacoes.py`
- `comp` = `tests/unit/interface/test_andamento_composicao.py`
- `prov` = `tests/unit/interface/test_providencias.py`
- `ed` = `tests/interface/test_andamento_do_edital.py`
- `coer` = `tests/interface/test_andamento_coerencia.py`
- `esc` = `tests/performance/test_andamento_em_escala.py`
- `sel` = `tests/interface/test_andamento_da_selecao.py`
- `tra` = `tests/interface/test_andamento_transicoes.py`

## Requisitos funcionais

| Requisito | Onde | Prova |
|---|---|---|
| FR-4050 | `interface/andamento.py` (`do_edital`, leitura, sem modelo próprio) | `ed::test_antes_da_publicacao_nada_desta_feature_aparece`; nenhuma migration no diff |
| FR-4051 | `andamento.py` devolve conjunto; `providencias.ordenar` | `prov::test_a_ordem_e_suas_depois_de_outros_papeis_depois_as_que_esperam` |
| FR-4052 | `situacao_*` | `sit` inteiro; `sit::test_toda_situacao_tem_palavra_e_sinal` |
| FR-4053 | `Celula` (situação, responsável, expectativa, razão, url, prazo), `Alcance` | `sit`, `ed::test_s1_o_auditor_le_as_telas_mas_nada_e_dele` |
| FR-4054 | `providencias.Providencia` | `prov`, `ed::test_s1_quem_conduz_le_a_sua_providencia_primeiro_com_link` |
| FR-4055 | `Alcance.de`, `_Leitor._acrescentar` | `ed::test_s1_a_presidencia_conduz_e_le_a_providencia_como_sua`, `ed::test_s1_o_auditor_le_as_telas_mas_nada_e_dele` |
| FR-4056 | `Providencia.da_celula` (url só se sua) | `ed::test_s1_quem_nao_conduz_le_o_papel_e_nao_recebe_link` |
| FR-4057 | `_Leitor._trabalho_da_104`, `situacoes_da_etapa` | `ed::test_p1_a_presidencia_le_distribuir_como_sua_e_a_ordem_nao_e_providencia` |
| FR-4058 | nenhum aviso nem formalização derivados | `ed` (nenhuma providência de aviso nos cenários) |
| FR-4059 | Encerrar fica em `acoes` | `ed::test_s1_com_providencia_da_pessoa_nenhuma_acao_vem_cheia` |
| FR-4060 | `expectativa_das_etapas`, `_consumidas_por_ato` | `comp::test_s1_…`, `comp::test_s2_…`, `comp::test_a_etapa_lida_so_pelo_desempate_e_esperada`, `comp::test_a_progressao_torna_esperada_a_etapa_anterior_que_consolida` |
| FR-4061 | `Atencao`, `providencias.frase_da_atencao` | `ed::test_s1_as_etapas_que_nada_consome_sao_atencao_e_nao_providencia`, `ed::test_p1_a_entrevista_que_nada_consome_e_atencao` |
| FR-4062 | `situacoes_da_etapa` | `sit::test_distribuir_avaliar_e_consolidar_sao_tres_providencias` e vizinhos |
| FR-4063 | `situacoes_da_etapa` (`minhas`) | `sit::test_a_avaliacao_da_pessoa_e_separada_da_dos_outros_avaliadores`, `ed::test_p1_o_avaliador_le_avaliar_como_sua_com_a_mesa` |
| FR-4064 | `nota` e `contagem` | `sit::test_todas_consolidadas_e_feito` |
| FR-4065 | `situacao_da_relacao` | `sit::test_a_relacao_*`, `sit::test_s3_a_relacao_espera_a_etapa_de_habilitacao` |
| FR-4066 | `situacao_da_semente` | `sit::test_a_semente_em_cada_situacao` |
| FR-4067 | `situacao_do_sorteio` | `sit::test_o_sorteio_em_cada_situacao` |
| FR-4068 | `situacao_da_ordem` | `sit::test_a_ordem_*`, `ed::test_p1_a_derivacao_da_ordem_e_depois_com_as_etapas_nomeadas` |
| FR-4069 | `situacao_do_corte`, `situacao_da_apuracao` sobre `indicador_do_marco` | `sit::test_o_corte_depende_da_ordem`, `coer::test_p2_o_corte_depois_da_ordem` |
| FR-4070 | `situacao_da_apuracao` (governada, corte) | `sit::test_p2_a_apuracao_espera_a_etapa_governada`, `sit::test_no_marco_que_corta_a_apuracao_espera_o_corte` |
| FR-4071 | `situacao_do_resultado`, `_Leitor._resultado` | `sit::test_o_preliminar_*`, `coer::test_p2_a_convocacao_e_a_publicacao[publicador]` |
| FR-4072 | `situacao_do_resultado` (sem ordem → *Depois*) | `sit::test_o_resultado_sem_ordem_e_depois_e_nao_falta` |
| FR-4073 | `situacoes_da_convocacao`, `_Leitor._convocacao` | `sit::test_os_quatro_estados_da_convocacao`, `ed::test_p2_depois_da_apuracao_convocar_os_titulares_e_de_quem_conduz` |
| FR-4074 | idem (condicionais) | `sit::test_nova_chamada_e_faixa_seguinte_sao_condicionais` |
| FR-4075 | `_Leitor._documentos` | `sit::test_documentos_a_conferir_e_desfecho_pronto` |
| FR-4076 | idem | `sit::test_sem_vaga_e_sem_convocacao_nao_se_aplica_e_tudo_desfechado_e_feito` |
| FR-4080 | `_providencias.html`, `providencias.contagem` | `ed::test_s1_quem_conduz_le_a_sua_providencia_primeiro_com_link` |
| FR-4081 | `views.detalhe` (todo papel) | `ed::test_s1_quem_nao_conduz_le_o_papel_e_nao_recebe_link` |
| FR-4082 | `providencias.ordenar` | `prov::test_a_ordem_*`, `prov::test_as_suas_com_prazo_*`, `prov::test_as_de_outros_papeis_*` |
| FR-4083 | `Nivel1.mostradas`/`demais`, `details.mais-providencias` | `prov::test_cinco_e_mais_n` |
| FR-4084 | `_providencia.html` | `ed::test_s1_*`, `ed::test_com_as_inscricoes_abertas_congelar_aguarda_com_a_data` |
| FR-4085 | `providencias.agrupar` | `prov::test_o_mesmo_ato_em_varias_listas_do_marco_e_uma_providencia`, `prov::test_o_ato_com_numero_nao_se_junta` |
| FR-4086 | `detalhe.html` (`not nivel_1.suas`), `porque_nada` | `ed::test_s1_quem_conduz_…` (sem "Nenhum ato"), `ed::test_o_perfil_sem_inscricao_nao_e_providencia` |
| FR-4087 | `p.atencao-do-andamento` | `ed::test_s1_as_etapas_que_nada_consome_sao_atencao_e_nao_providencia` |
| FR-4088 | `detalhe.html` (principal secundária) | `ed::test_s1_com_providencia_da_pessoa_nenhuma_acao_vem_cheia` |
| FR-4089 | `views.detalhe` (`trilha` vazia), `p.imutavel.em-uma-linha` | `ed::test_depois_da_publicacao_a_trilha_de_situacao_sai` |
| FR-4090 | `views._proximo_nesta_lista`, `andamento.da_lista`, `_proximo_nesta_lista.html` em corte, ordenação, ocupação, sorteio, convocação e documentos | `tra::test_depois_do_corte_o_proximo_e_a_etapa_governada_e_nao_outro_corte`, `tra::test_depois_de_convocar_o_proximo_e_da_mesma_lista`, `tra::test_abrir_a_tela_nao_mostra_o_proximo` |
| FR-4091 | "Nada mais em aberto nesta lista."; o papel sem link | `tra::test_sem_nada_em_aberto_a_lista_diz_isso` |
| FR-4092 | uma linha a mais abaixo do sucesso; a sucessão da `126` intocada | o diff das transições (uma linha por template); a suíte com a `126` mesclada |
| FR-4100 | `detalhe.html` (`_andamento_da_selecao.html` no lugar do cartão) | `sel::test_o_andamento_toma_o_lugar_do_cartao_classificacao`, `sel::test_quem_nao_via_o_cartao_classificacao_nao_ve_o_andamento` |
| FR-4101 | `resumo_do_perfil`, `linha_das_inscricoes` | `sel::test_o_andamento_toma_o_lugar_do_cartao_classificacao`, `comp::test_o_resumo_conta_feitos_sobre_os_que_se_aplicam`, `comp::test_a_linha_das_inscricoes` |
| FR-4102 | `p.perfil-sem-inscricao` | `sel::test_o_perfil_sem_inscricao_e_uma_linha_so` |
| FR-4103 | `sequencia_do_perfil` | `sel::test_s1_a_matriz_comeca_pela_relacao_…`, `sel::test_p1_a_matriz_comeca_pelas_etapas_…`, `sel::test_p2_a_etapa_governada_…`, `comp` |
| FR-4104 | `PerfilNoAndamento.grupos` (`th scope="colgroup"`) | `sel::test_s1_…` (`Sem efeito no GPS`), `sel::test_p2_…` (`Etapa governada pela faixa`) |
| FR-4105 | `td[data-situacao]`, link só com `url` | `sel::test_quem_so_publica_nao_ve_o_perfil_sem_ordem`; `coer` (as URLs vêm do mesmo `Alcance`) |
| FR-4106 | `.moldura-do-andamento { overflow-x: auto }` | `sel::test_a_matriz_rola_dentro_da_moldura`; `medidas.json` (`rola_de_lado`, aberto e recolhido) |
| FR-4107 | o nível 1 lê as mesmas células | `sel::test_nenhuma_pendencia_so_na_matriz` |
| FR-4108 | `perfil.destinos` de `_marcos_publicados` | `sel::test_os_destinos_do_cartao_classificacao_continuam`; `test_destinos_do_edital.py`, `test_publicar_resultado.py`, `test_recortes_alinhados.py` (suíte) |
| FR-4109 | `matricula_fora` | nota fixa, sem cenário de convocação encerrada nos testes (registrado em `verificacao.md`) |
| FR-4110 | folha enxuta; Perfis só de quem os alcança (D-004) | `capturas/depois-b2/medidas.json` contra `depois-b1` |
| FR-4120 | leituras em lote; `esc` | `esc::test_o_sorteio_nao_cresce_com_as_inscricoes`, `esc::test_a_pontuacao_com_etapas_nao_cresce_com_as_inscricoes` |
| FR-4121 | `ul`, "Sua" em texto, palavra e sinal | `ed::test_s1_quem_conduz_…` (`marca-sua`), `sit::test_toda_situacao_tem_palavra_e_sinal` |
| FR-4122 | `interface/telas/andamento.css`, nada inline | `test_acessibilidade`, `test_estaticos`, CSP (suíte) |
| FR-4123 | nenhuma permissão, tabela, migration | `make check` (`makemigrations --check`); diff |

## Critérios

| Critério | Prova |
|---|---|
| SC-1230 | `coer` inteiro (gestor, presidência, avaliador, publicador) |
| SC-1231 | `ed::test_s1_*` (o 35 é S1); capturas `35-*` no banco do estudo |
| SC-1232 | captura `57-gestor`: "Congelar a relação" sua e "Observar a extração" *Aguarda* (`verificacao.md`) |
| SC-1233 | `ed::test_p1_*`; captura `91-arodrigues` |
| SC-1234 | `ed::test_s1_quem_conduz_…`, `ed::test_p1_*` |
| SC-1235 | `sit` |
| SC-1236 | `coer::test_convocar_troca_convocar_por_emitir_a_comunicacao`, `coer::test_avaliar_e_consolidar_libera_a_ordem` |
| SC-1237 | `comp` (S1, S2, S3, P1, P2, P3, CR, mista), `ed` (S1, P1, P2), `coer` |
| SC-1238 | `tra::test_depois_do_corte_o_proximo_e_a_etapa_governada_e_nao_outro_corte` |
| SC-1239 | `esc` |
| SC-1240 | capturas `depois-b1/medidas.json` (`fim_das_suas`) |
| SC-1241 | `medidas.json` (`rola_de_lado`) |
| SC-1242 | `capturas/depois-b2/medidas.json`: recolhido, de 16 a 42 px mais baixo que o cartão antigo a 1280 px |
| SC-1243 | `comp`; `sel::test_s1_…`, `sel::test_p1_…` |
| SC-1244 | `make check`; suíte completa (`verificacao.md`) |
| SC-1245 | validação com pessoas — espera o usuário (`quickstart.md`) |

## UX

| Identificador | Prova |
|---|---|
| UX-230 | `sit::test_toda_situacao_tem_palavra_e_sinal`; `_providencia.html` |
| UX-231 | `ed::test_s1_quem_conduz_…` (`<span class="marca-sua">Sua</span>`), `ed::test_s1_quem_nao_conduz_…` (`Quem conduz a seleção:`) |
| UX-232 | `medidas.json` (`fim_das_providencias`, `fim_das_suas`) |
| UX-233 | `sel::test_o_andamento_toma_o_lugar_do_cartao_classificacao` (`details` fechado), `sel::test_a_matriz_rola_dentro_da_moldura` |

## Casos-limite

| Caso | Prova |
|---|---|
| Perfil sem inscrito | `ed::test_o_perfil_sem_inscricao_nao_e_providencia` |
| Lista não constituída | `sit::test_a_relacao_sem_ninguem_nao_se_aplica`, `sit::test_o_sorteio_em_cada_situacao` |
| Dependência futura | `sit::test_a_semente_em_cada_situacao` (extração futura), `sit::test_a_etapa_governada_sem_corte_e_depois`, `sit::test_a_ordem_espera_as_etapas_que_le` |
| Operação bloqueada | `sit::test_a_relacao_que_condenaria_o_sorteio_e_impedida`, `sit::test_a_etapa_com_regra_insuficiente_*`, `sit::test_a_convocacao_sem_forma_declarada_e_impedida` |
| Concurso indisponível | `situacao_da_semente` não lê falha de acesso (nada gravado); `sit::test_a_semente_em_cada_situacao` |
| Ato obsoleto | `sit::test_o_sorteio_em_cada_situacao`, `sit::test_a_ordem_em_cada_situacao`, `sit::test_o_definitivo_e_feito_e_o_defasado_e_obsoleto` |
| Retificação | frases da `104` mantidas (D-017); `test_acoes_disponiveis.py` (suíte) |
| Resultado ainda não publicável | `sit::test_o_preliminar_na_janela_recursal_aguarda` |
| Convocação com prazo futuro | `sit::test_os_quatro_estados_da_convocacao` |
| Listas em estágios diferentes | captura `57-gestor`; `coer::test_p2_o_corte_depois_da_ordem` |
| Nova chamada | `sit::test_nova_chamada_e_faixa_seguinte_sao_condicionais` |
| Inscrições em curso | `ed::test_com_as_inscricoes_abertas_congelar_aguarda_com_a_data`, `coer::test_s1_com_as_inscricoes_abertas_a_tela_diz_a_mesma_espera` |
| Mais de cinco | `prov::test_cinco_e_mais_n` |
| Mesmo ato em várias listas | `prov::test_o_mesmo_ato_em_varias_listas_do_marco_e_uma_providencia` |
| Segregação | não há segregação nos atos depois da publicação (R-009); a da Retificação segue a `104` |
| Pessoa de outro escopo | a porta do detalhe (404) não muda; `test_acoes_disponiveis.py` |
| Edital encerrado | `ESTADOS_COM_ANDAMENTO`; `porque_nada` |
| Antes da publicação | `ed::test_antes_da_publicacao_nada_desta_feature_aparece` |
| Etapa enumerada pelo sorteio que não consolida | `comp::test_s2_a_etapa_enumerada_pelo_sorteio_conta_so_se_consolida` |
| Etapa só de desempate | `comp::test_a_etapa_lida_so_pelo_desempate_e_esperada` |
| Avaliador sem inscrição atribuída | `sit::test_a_avaliacao_da_pessoa_e_separada_da_dos_outros_avaliadores` (carga zero não vira providência) |
