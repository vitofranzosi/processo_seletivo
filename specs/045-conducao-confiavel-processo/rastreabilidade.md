# Rastreabilidade — 045 · Condução confiável do Processo vivo

**Frase que governa**: *todo sinal exibido é verdadeiro, toda ausência afirmada respeita o alcance
do observador, e todo trabalho pendente que a Supervisão acompanha é visível.*

**Verificação final** (26/09/2026, depois de integrar a `main` com o #183 e o #184): `make lint check
test-pg` — `ruff check` e `ruff format --check` limpos, `manage.py check` sem problemas, **7877
passando e 11 pulados**, zero falhas. O "antes" era 7837 e 11; a diferença é a desta feature mais os
casos que o #183 trouxe.

Cada linha aponta o lugar do código e o teste **pelo nome**. Onde a linha diz *"leitura do diff"*, a
promessa é negativa — algo que não pode ter acontecido — e se confere lendo a mudança.

---

## 1. Requisitos

| `FR-` | Onde entrou | O que o prende |
|---|---|---|
| **FR-730** | `supervisao.frase_de_ausencia`; `views.processo_detalhe` e `views.supervisao` passam `ausencia`; `processo_detalhe.html` e `supervisao.html` a exibem | `test_quem_alcanca_parte_das_especies_le_a_ausencia_relativa` (três papéis), `test_quem_alcanca_todas_as_especies_le_a_ausencia_global`, `test_na_supervisao_a_presidencia_sozinha_le_a_ausencia_relativa` |
| **FR-731** | `frase_de_ausencia` recebe só o dicionário de `alcance`, antes de sinal algum ser montado | `test_a_frase_nao_muda_com_o_que_o_leitor_nao_alcanca` — compara o trecho da Atenção **letra por letra** |
| **FR-732** | `sinais_do_recurso` lê `AGUARDANDO_DECISAO` (admissibilidade e julgamento) numa leitura só; `fase_das_pecas` | `test_recurso_recem_interposto_produz_o_sinal_na_admissibilidade`, `test_admitida_a_peca_o_mesmo_sinal_passa_a_dizer_julgamento`, `test_com_pecas_nas_duas_fases_a_mensagem_diz_as_duas`, `test_na_admissibilidade_a_comissao_impedida_continua_sendo_o_ux_005` |
| **FR-733** | a situação da peça decide; decidida, sai do filtro | `test_peca_inadmitida_ou_julgada_nao_compoe_sinal`, `test_sem_peca_pendente_nenhum_dos_dois_aparece` (038) |
| **FR-734** | `acoes.recursos_aguardando_decisao` — uma consulta com `Exists`; rótulo *"Recursos aguardando decisão (N)"* | `test_a_acao_de_recursos_conta_so_as_pecas_que_aguardam_decisao`, `test_quem_julga_recurso_chega_a_tela_de_recursos` |
| **FR-735** | `calendario.fase`; `supervisao.fase_do_evento` (período pela régua do período, os demais pela do vencido); `Marco.fase`; o corte dos próximos marcos passa a ser *concluído* | `test_com_termino_a_fase_percorre_as_tres`, `test_o_evento_pontual_nunca_fica_em_andamento_para_sempre`, `test_no_instante_exato_a_fase_segue_o_menor_estrito_da_regua`, `test_o_periodo_sem_termino_continua_nos_marcos_em_andamento` |
| **FR-736** | `fase_do_evento` devolve `None` para o cancelado; `validate_event` aceita `CANCELADO` | `test_o_cancelado_nao_aparece_mesmo_com_datas_em_curso`, `test_evento_cancelado_nao_entra_nos_proximos_marcos` (022), `test_o_cancelamento_continua_declaravel` |
| **FR-737** | `editais/domain/cronograma.validate_event` (`STATUS_DECLARAVEIS`); a tela normaliza o herdado em `forms.eventos_persistidos` | `test_a_fase_ordinaria_nao_se_declara` (dois valores), `test_regravar_normaliza_a_fase_que_a_api_gravava_antes_da_045`, `test_regravar_o_cronograma_preserva_o_que_a_tela_nao_oferece` |
| **FR-738** | `UX_002`, `divergencias_temporais`, `posicao_temporal`, `COERENTES` e `DECLARACOES` saíram de `supervisao.py` | `test_cronograma_normal_nao_produz_sinal_algum`, `test_a_enumeracao_tem_exatamente_oito_especies` |
| **FR-739** | `validation._etapa_sem_evento` (`stage_without_schedule_event`, só no ato de publicação); `RESUMO_DAS_REPETIDAS`; `UX_001` saiu do catálogo | `test_a_etapa_sem_evento_e_aviso_na_publicacao`, `test_na_retificacao_o_aviso_nao_aparece`, `test_o_aviso_nunca_impede_e_tem_codigo_proprio`, `test_a_etapa_sem_evento_e_aviso_na_etapa_e_na_revisao`, `test_o_edital_publicado_diz_a_etapa_sem_evento_na_validacao_do_conteudo`, `test_quem_preside_ve_situacao_volume_prazo_e_impedimento_numa_tela_so` |
| **FR-740** | `Sinal.conducao` e `_sinal.html`; `interface/conducao.py` (a frase da Retificação mudou de casa, sem ser redigida de novo); `conducao_para_emitir` no sorteio e na ocupação; `conducao_do_sucessor` na prévia | `test_quem_nao_retifica_recebe_a_quem_pedir`, `test_quem_retifica_recebe_o_caminho_e_nao_a_frase`, `test_quem_le_e_nao_conduz_o_sorteio_sabe_a_quem_pedir`, `test_quem_le_e_nao_apura_sabe_a_quem_pedir`, `test_sem_o_caminho_da_classificacao_a_previa_diz_a_quem_pedir_o_sucessor`, `test_as_conducoes_produzidas_seguem_a_formulacao_canonica` |
| **FR-741** | `supervisao.situacao_admite_retificacao`, separada da permissão; `sinais` só monta o `UX-046` onde ela admite | `test_onde_ninguem_pode_retificar_o_sinal_nao_e_condicao_de_atencao` (encerrado e cancelado), `test_num_processo_em_estado_final_o_sinal_nao_e_condicao_de_atencao` |
| **FR-742** | `resumo_da_etapa` conta participantes — pelo panorama ou por `_so_participantes`; a Supervisão passa o conteúdo; filtro `carente` e ficha *"Participantes desta Etapa"* na distribuição | `test_a_cobertura_conta_so_os_participantes_e_as_duas_formas_concordam`, `test_o_numero_sem_avaliador_suficiente_abre_uma_lista_do_mesmo_tamanho`, `test_inscricao_sem_avaliador_e_carente_e_permanece_no_denominador` (022), `test_o_custo_nao_cresce_com_a_populacao` e `test_a_primeira_etapa_nao_consulta_progressao` (teto intacto) |
| **FR-743** | `Medida.unidade` e `unidade_legivel`, declaradas por espécie; `_sinal.html` | `test_a_medida_diz_o_que_conta`, `test_a_cobertura_conta_so_os_participantes_e_as_duas_formas_concordam` (unidade *inscrições*) |
| **FR-744** | `ESPECIES` com oito; o guarda passa a ler a `FR-744` | `test_a_enumeracao_tem_exatamente_oito_especies`, `test_o_requisito_que_fecha_o_catalogo_nomeia_as_especies_que_o_produto_apresenta` |
| **FR-745** | `022`: `D-004`, `FR-023`, `FR-026`, `FR-027`, `FR-030`, `FR-033`, `UX-001`, `UX-002`, `UX-005`, e a nota no bloco da `FR-024`; `038`: `FR-561`, `FR-565`, `UX-064` | `test_o_requisito_que_fecha_o_catalogo_nomeia_as_especies_que_o_produto_apresenta` confere a cadeia `022` → `038` → `045`; o resto é **leitura do diff** — nenhum texto anterior apagado, só riscado ou anotado |

## 2. Critérios de sucesso

| `SC-` | Como se confere |
|---|---|
| **SC-269** | os testes da `FR-730` e da `FR-731`, e o percurso 1 do [quickstart](quickstart.md) — registrado em [antes-da-conducao.md](antes-da-conducao.md) |
| **SC-270** | os testes da `FR-732` a `FR-734`, e o percurso 2 |
| **SC-271** | `test_cronograma_normal_nao_produz_sinal_algum` e os testes da `FR-735`; percurso 3 |
| **SC-272** | os testes da `FR-740` e da `FR-741`; percurso 4 |
| **SC-273** | `test_o_numero_sem_avaliador_suficiente_abre_uma_lista_do_mesmo_tamanho`, `test_a_cobertura_conta_so_os_participantes_e_as_duas_formas_concordam`, `test_a_medida_diz_o_que_conta` |
| **SC-274** | `test_o_requisito_que_fecha_o_catalogo_nomeia_as_especies_que_o_produto_apresenta` |

## 3. Requisitos de apresentação

| `UX-` | Onde | O que o prende |
|---|---|---|
| **UX-084** | `AUSENCIA_RELATIVA` — a variante da global | `test_quem_alcanca_parte_das_especies_le_a_ausencia_relativa` |
| **UX-085** | `fase_das_pecas` nas mensagens do `UX-005` e do `UX-064` | `test_com_pecas_nas_duas_fases_a_mensagem_diz_as_duas`, `test_admitida_a_peca_o_mesmo_sinal_passa_a_dizer_julgamento` |
| **UX-086** | a mensagem de `_etapa_sem_evento`; *"Aviso"* na lista de pendências | `test_a_etapa_sem_evento_e_aviso_na_publicacao` (sem *atraso*, *aguarda*, *pendente*), `test_a_etapa_sem_evento_e_aviso_na_etapa_e_na_revisao` |
| **UX-087** | `unidade_legivel`; a mensagem do `UX-046` deixou de repetir os números | `test_a_medida_diz_o_que_conta` |
| **UX-088** | `Marco.em_andamento`; os dois templates marcam só o marco em curso | `test_o_periodo_sem_termino_continua_nos_marcos_em_andamento`, `test_o_processo_e_a_supervisao_dizem_a_mesma_coisa_do_mesmo_edital` (conta os marcos sem *"declarado"*) |

## 4. Casos-limite

Não têm identificador, e nenhuma ferramenta os cobra. Cada um tem a sua linha.

| Caso-limite | O que o prende |
|---|---|
| Leitor que acumula todos os papéis | `test_quem_alcanca_todas_as_especies_le_a_ausencia_global` |
| O alcance muda com o estado do Edital | `test_o_edital_parado_nao_torna_parcial_a_leitura_de_quem_alcanca_tudo` |
| Evento sem término | `test_o_evento_pontual_nunca_fica_em_andamento_para_sempre`, `test_o_evento_pontual_sai_dos_marcos_quando_vence` |
| Período de inscrições sem término | `test_o_periodo_sem_termino_continua_nos_marcos_em_andamento` |
| Quatro regras para o Evento sem término | o pulso alinhado às duas réguas (os dois acima); o portal ficou registrado em *Out of Scope* — **nenhum teste**, por decisão |
| Evento sem início | `test_sem_inicio_nao_ha_fase` |
| Edital publicado antes desta feature, com fase declarada | `test_fase_declarada_em_conteudo_ja_publicado_e_lida_como_nao_cancelado` |
| Recurso admitido | `test_admitida_a_peca_o_mesmo_sinal_passa_a_dizer_julgamento` |
| O Julgador impedido nesta peça continua vendo o `UX-064` | comportamento da `038`, sem mudança: a condição é do conjunto — `test_recurso_com_julgador_disponivel_produz_o_sinal` |
| Etapa sem ninguém a avaliar (*"0 de 0"*) | `test_sem_inscricao_submetida_nao_ha_cobertura_a_cobrar` — com todos eliminados antes, a população de participantes é vazia e o caminho é o mesmo: `carentes` zero, sem sinal |
| Inscrição à espera da Etapa anterior, ou fora do corte | `test_a_cobertura_conta_so_os_participantes_e_as_duas_formas_concordam` |
| Participante sem avaliador nenhum | `test_inscricao_sem_avaliador_e_carente_e_permanece_no_denominador`, `test_o_numero_sem_avaliador_suficiente_abre_uma_lista_do_mesmo_tamanho` |
| `UX-046` num Edital que parou por ato | `test_onde_ninguem_pode_retificar_o_sinal_nao_e_condicao_de_atencao` |
| Outra espécie com o mesmo defeito | medido no plano (`research.md`, `R-7`) e registrado na spec; **nenhum teste**, por decisão — é registro, não escopo |

## 5. Os nove testes de regressão da proposta

| # | O que prende | Teste |
|---|---|---|
| 1 | ausência relativa ao alcance | `test_quem_alcanca_parte_das_especies_le_a_ausencia_relativa` |
| 2 | recurso em admissibilidade visível | `test_recurso_recem_interposto_produz_o_sinal_na_admissibilidade` |
| 3 | recurso decidido fora da contagem | `test_peca_inadmitida_ou_julgada_nao_compoe_sinal`, `test_a_acao_de_recursos_conta_so_as_pecas_que_aguardam_decisao` |
| 4 | derivação temporal do Evento | `test_com_termino_a_fase_percorre_as_tres` e os vizinhos em `test_calendario.py` |
| 5 | a exceção `CANCELADO` | `test_o_cancelado_nao_aparece_mesmo_com_datas_em_curso` |
| 6 | nenhum `UX-002` espúrio | `test_cronograma_normal_nao_produz_sinal_algum` |
| 7 | população correta na avaliação | `test_a_cobertura_conta_so_os_participantes_e_as_duas_formas_concordam` |
| 8 | capacidade a pedir no sinal sem destino | `test_quem_nao_retifica_recebe_a_quem_pedir` e os três das telas de destino |
| 9 | nenhum vazamento entre papéis | `test_a_frase_nao_muda_com_o_que_o_leitor_nao_alcanca` |

## 6. Testes alterados, caso a caso

Contra o "antes" de [antes-da-conducao.md](antes-da-conducao.md). **Apagados**:

| Arquivo | Caso | Por quê |
|---|---|---|
| `integration/supervisao/test_sinais.py` | `test_etapa_sem_evento_vinculado_produz_o_sinal`, `test_etapa_com_evento_vinculado_nao_produz_o_sinal` | o `UX-001` saiu do catálogo; sucessores em `test_etapa_sem_evento.py` |
| `integration/supervisao/test_sinais.py` | `test_a_tabela_verdade_inteira_de_ux_002`, `test_ux_002_apresenta_as_duas_informacoes_sem_arbitrar` | o `UX-002` não tem mais o que comparar; o sucessor é `test_cronograma_normal_nao_produz_sinal_algum` |
| `interface/test_supervisao.py` | `test_o_encaminhamento_de_conteudo_publicado_abre_onde_ele_se_corrige`, `test_sem_a_permissao_de_retificar_o_sinal_fica_e_o_caminho_nao`, `test_edital_nao_publicado_nao_recebe_encaminhamento_de_retificacao` | provavam o encaminhamento à Retificação sobre o `UX-001`; a mesma prova vive sobre o `UX-046`, em `test_sinal_do_acervo_sem_quadro.py` |

**Reescritos**:

| Arquivo | Caso | O que mudou |
|---|---|---|
| `integration/supervisao/test_sinais.py` | `test_o_edital_parado_nao_silencia_as_especies_anteriores` | montava a preservação sobre o `UX-001` de brinde; passou a montar o `UX-004` |
| `interface/test_supervisao.py` | `test_os_sinais_do_edital_conduzem_as_telas_donas` | sem `edital_divergente`; confere que não há Retificação oferecida por Cronograma |
| `interface/test_supervisao.py` | `test_o_processo_e_a_supervisao_dizem_a_mesma_coisa_do_mesmo_edital` | conta marcos pela data, e não pela regex `declarado (...)` |
| `interface/test_supervisao.py` | `test_quem_preside_recebe_a_atencao_na_mesma_regiao` | o sinal de prova passou de *"sem marco"* a *"sem avaliador suficiente"* |
| `integration/supervisao/test_autorizacao.py` | `test_processo_cancelado_le_e_nao_oferece_o_que_a_situacao_nao_admite` → `test_processo_cancelado_continua_legivel` | a metade "não oferece" foi para o `UX-046` (`FR-741`) |
| `unit/interface/test_supervisao.py` | `test_a_enumeracao_tem_exatamente_dez_especies` → `…_oito_especies` | o catálogo encolheu |
| `acceptance/test_supervisao_do_processo.py` | o percurso e o guarda do catálogo | o percurso procura a Etapa sem marco na validação; o guarda lê a `FR-744` |
| `interface/test_round_trip_do_rascunho.py` | `EVENTO_DO_PERIODO` e `test_regravar_o_cronograma_preserva_o_que_a_tela_nao_oferece` | o estado preservado passou de `EM_ANDAMENTO` (recusado) a `CANCELADO` |
| `integration/editais/test_reaproveitamento.py` | a origem | o `CONCLUIDO` passou do `PUT` ao ORM, antes da submissão |
| `unit/editais/test_etapas.py` | `_recusas` | filtra impeditivos, e não caminho — o aviso novo não é recusa |
| `interface/test_hardening_pos_auditoria.py` | `test_quem_julga_recurso_chega_a_tela_de_recursos` | o rótulo mudou |
| `interface/test_distribuicao.py` | `test_a_tela_diz_o_que_falta_antes_do_detalhe` | o número leva a `carente` |
| `interface/test_larguras.py` | o controle de cobertura | idem |

**Fixtures**: `conftest.py` (`edital_c`), `test_supervisao.py` (`processo_limpo`) e o percurso de aceitação
perderam o `status_do_periodo="EM_ANDAMENTO"`, que só existia para não disparar o `UX-002`.
`fixtures/publicacao.py::levar_a_publicacao` passou a conferir o `PUT` do rascunho (`T003`).

**Não previsto pela `R-8`**: `test_larguras.py` e `test_hardening_pos_auditoria.py` (o texto do link e o
rótulo), e `unit/editais/test_reaproveitamento.py::test_sem_a_conversao_a_validacao_estoura_em_vez_de_recusar`,
que não mudou — mudou a **ordem** da nova conferência em `validate_event`, que passou a vir depois das
de forma para não mascarar a contraprova.

## 7. O que se confere lendo o diff

- **Nenhuma migration**, nenhuma entidade, nenhuma capacidade de autorização nova.
- **Nenhum valor tirado** do `choices` de `EventoCronograma.status`.
- **Nenhum conteúdo publicado reescrito**: a fase é lida, e `test_fase_declarada_em_conteudo_ja_publicado_e_lida_como_nao_cancelado` confere que o dicionário lido não muda.
- **Nenhuma frase de condução redigida à mão**: as cinco saem de `frase_do_aviso`; o que é escrito nos templates é só *"a presidência não é papel"*, como na ordenação.
- **Nada apagado das specs anteriores**: o que foi substituído está riscado ou anotado, com a data e o ponteiro.
