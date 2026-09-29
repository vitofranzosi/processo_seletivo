# Rastreabilidade — 051 · Padrões do Edital e "aplicar a todos"

**Frase que governa**: *o que o Edital declara uma vez é pedido uma vez, e materializado Perfil a
Perfil com a prévia do alcance; o que o sistema sabe vira padrão que só preenche o vazio; e a Revisão
diz de onde veio cada valor.*

**Entrega**: este PR leva a P1 — US1 a US4. A US5 (Retificação, P2) fica para o PR seguinte, por
decisão do plano (`research.md`, R-009); as linhas dela estão marcadas **PR seguinte**.

**Verificação final**: 8763 passando, 11 pulados, zero falhas — ver a seção 4.

Cada linha aponta o lugar do código e o teste **pelo nome**. Onde a linha diz *"leitura do diff"*, a
promessa é negativa — algo que não pode ter acontecido — e se confere lendo a mudança. Os testes novos
estão em `tests/unit/editais/test_aplicacao.py` (**TA**), `tests/unit/editais/test_quadro_sugerido.py`
(**TQ**), `tests/interface/test_aplicar_a_todos.py` (**TT**),
`tests/interface/test_padroes_da_composicao.py` (**TP**) e
`tests/interface/test_revisao_origem_e_definitivos.py` (**TR**).

---

## 1. Requisitos

| `FR-` | Onde entrou | O que o prende |
|---|---|---|
| **FR-910** | `editais/domain/aplicacao.py` — cada destino recebe cópia com identidade própria; nenhum campo novo no conteúdo publicado (leitura do diff) | TA `test_a_copia_e_independente_da_origem`, `test_nasce_onde_falta_com_identidade_do_destino_e_o_fato_do_destino` |
| **FR-911** | `aplicacao.efeitos_do_marco`, `efeitos_da_modalidade`, `efeitos_do_campo_do_perfil` | TA `test_substitui_os_campos_e_mantem_identidade_codigo_e_denominacao`, `test_nunca_remove_nem_toca_o_quadro`, `test_reversao_fica_fora_sem_lista_reservada` |
| **FR-912** | `efeitos_do_marco`: 0 marco → nasce, 1 → substitui, ≥2 → fora | TA `test_dois_marcos_no_destino_ficam_fora`; TT `test_a_previa_declara_cada_perfil_e_nao_grava_nada` |
| **FR-913** | `_marco_no_destino` mantém `id`/`code`/`name` do destino; `identidade_derivada` no que nasce | TA `test_substitui_os_campos_e_mantem_identidade_codigo_e_denominacao`, `test_nasce_onde_falta_com_identidade_do_destino_e_o_fato_do_destino`, `test_substitui_os_campos_e_nunca_o_codigo_nem_a_identidade` |
| **FR-914** | `_criterios_no_destino` (código e tipo do fato) | TA `test_fato_ausente_deixa_fora_e_nomeia_o_fato`, `test_fato_de_mesmo_codigo_e_outro_tipo_nao_corresponde` |
| **FR-915** | os padrões nascem no fragmento do cartão novo (`views._marco_novo`, `fragmento_etapa`) ou no vazio do leitor (`forms._metodo_de_sorteio`); nenhum na Retificação (leitura do diff: `interface/retificacao.py` intocado) | TP `test_o_segundo_marco_na_tela_nasce_sem_corte`, `test_a_prosa_vazia_e_gerada_da_regra_e_a_digitada_vale` |
| **FR-916** | `interface/aplicacao.previa`; `_previa_da_aplicacao.html` | TT `test_a_previa_declara_cada_perfil_e_nao_grava_nada`, `test_a_modalidade_nasce_nos_demais_pelo_codigo_e_nao_toca_o_quadro` |
| **FR-917** | `aplicacao._quantidade_fixa`; linha própria na prévia | TA `test_quantidade_fixa_e_destacada` |
| **FR-918** | caixas `aplicar_destino`; `aplicacao.alcancados` | TA `test_aplicar_toca_so_os_incluidos_e_aplicaveis`; TT `test_o_destino_fora_do_alcance_nao_e_tocado_mesmo_forjado`, `test_sem_destino_marcado_nada_e_gravado` |
| **FR-919** | `aplicacao.assinatura`; `views._gesto` confere antes de gravar | TA `test_a_assinatura_e_estavel_e_muda_quando_o_efeito_muda`; TT `test_a_confirmacao_sobre_tela_que_mudou_e_recusada_sem_gravar` |
| **FR-920** | `editais/application/aplicacao.gravar_aplicacao` — `replace_draft` e trilha em `transaction.atomic` | TT `test_a_confirmacao_grava_o_marco_no_destino_e_registra_o_gesto`, `test_a_confirmacao_sobre_tela_que_mudou_e_recusada_sem_gravar` |
| **FR-921** | `RegistroAuditoria.detalhe` (migration `auditoria/0003`); `interface/aplicacao.registro`, `razao`; `OPERACOES["APLICAR_A_TODOS"]` | TT `test_a_confirmacao_grava_o_marco_no_destino_e_registra_o_gesto`, `test_a_modalidade_nasce_nos_demais_pelo_codigo_e_nao_toca_o_quadro` |
| **FR-922** | `aplicacao.unidade_do_marco`, `metodo_proprio` | TA `test_ausencia_na_origem_e_aplicada_como_ausencia`, `test_metodo_proprio_de_sorteio_deixa_fora`, `test_metodo_guardado_em_marco_de_pontuacao_nao_e_proprio_e_fica_com_o_destino`, `test_metodo_guardado_sai_quando_a_origem_faz_o_destino_sortear` |
| **FR-923** | `efeitos_do_marco` — lista inteira; idêntica fica com a identidade do destino | TA `test_a_lista_de_criterios_e_substituida_inteira`, `test_substitui_os_campos_e_mantem_identidade_codigo_e_denominacao` |
| **FR-924** | `efeitos_da_modalidade`, `aplicar_modalidades`; botão em `_modalidade.html` | TA `test_nasce_onde_o_codigo_falta_e_lista_o_que_o_destino_tem`, `test_nunca_remove_nem_toca_o_quadro`; TT `test_a_modalidade_nasce_nos_demais_pelo_codigo_e_nao_toca_o_quadro` |
| **FR-925** | `efeitos_da_modalidade` — `ampla` antes → depois | TA `test_a_ampla_da_origem_substitui_a_do_destino`, `test_a_origem_que_nao_e_a_ampla_desmarca_o_destino_que_a_apontava` |
| **FR-926** | controle *"Declarado uma vez para todos os Perfis"* em `compor_perfis.html`; `views._comuns`; `fragmento_perfil` com `valor_comum` | TA `test_forma_de_convocacao_nasce_substitui_e_nao_muda`, `test_valor_comum_so_quando_todos_concordam`; TT `test_a_forma_de_convocacao_declarada_uma_vez_vai_a_todos`, `test_o_perfil_novo_nasce_com_a_forma_que_todos_declaram`, `test_a_reversao_deixa_fora_o_perfil_sem_lista_reservada`; a escolha pendente (`interface/aplicacao.escolhas_pendentes`): TT `test_salvar_com_a_escolha_do_edital_pendente_nao_grava`, `test_as_duas_escolhas_pendentes_sao_ditas_cada_uma_no_seu_controle`, `test_o_controle_intocado_nao_impede_mudar_um_perfil_no_cartao`, `test_a_escolha_que_os_cartoes_ja_declaram_nao_esta_pendente`, `test_confirmar_uma_escolha_nao_apaga_a_outra`, `test_o_botao_do_controle_diz_que_confere`, `test_a_reversao_que_so_falta_onde_nao_cabe_nao_esta_pendente` |
| **FR-927** | `marcos.CORTE_PADRAO`; `views._marco_novo(marcos_na_tela=)`; `hx-include` do botão | TP `test_o_marco_unico_nasce_com_o_corte_padrao`, `test_o_segundo_marco_na_tela_nasce_sem_corte` |
| **FR-928** | `validation._regra_de_corte_do_marco`; `_marco.html` oculta a pergunta sob sorteio | TP `test_o_marco_de_sorteio_publica_sem_o_empate`, `test_o_marco_de_pontuacao_continua_exigindo_o_empate`, `test_o_empate_declarado_fora_do_vocabulario_continua_recusado_no_sorteio`, `test_o_cartao_de_sorteio_nao_pergunta_o_empate_e_preserva_o_declarado` |
| **FR-929** | `views.eventos_do_sorteio`; `occurrenceEvent` em `forms._metodo_de_sorteio`; filtro `instante_de_evento` | TP `test_o_instante_escolhido_no_cronograma_e_gravado_e_o_digitado_vale`, `test_a_classificacao_oferece_os_eventos_do_cronograma` |
| **FR-930** | `sorteios/domain/prosa.py`; `forms._metodo_de_sorteio` | TP `test_a_prosa_vazia_e_gerada_da_regra_e_a_digitada_vale` |
| **FR-931** | `_etapa.html` (caixa por forma); `forms.ler_etapas`; `fragmento_etapa` com `nova` | TP `test_a_etapa_nova_traz_a_decisoria_eliminatoria`, `test_a_leitura_usa_a_caixa_da_forma_escolhida` |
| **FR-932** | `editais/domain/quadro.sugestao`; `placeholder` e conta em `_linha_do_quadro.html`; `aplicacao.preencher_quadro` | TQ (6 casos); TP `test_o_arredondamento_e_gravado_e_volta_na_tela`, `test_preencher_pelo_percentual_poe_a_sugestao_e_nao_grava` |
| **FR-933** | `rounding` em `_modalidade.html` e `forms._modalidades`; `views._preservando_a_regra`; comentário de `mutabilidade.OPACOS` | TP `test_gravar_os_perfis_preserva_os_campos_da_regra_que_a_tela_nao_desenha`, `test_o_arredondamento_fora_da_lista_e_preservado`; TQ `test_fora_da_lista_e_preservado_e_nao_sugere` |
| **FR-934** | `interface/origens.py` (comparação); `revisao._leitura_do_marco`, `_perfil`, `_etapa`, `_classificacao` | TR `test_o_marco_aplicado_aparece_com_a_origem_e_o_autor`, `test_a_forma_de_convocacao_aplicada_pelo_edital_aparece_com_a_origem` |
| **FR-935** | `origens.gestos_por_destino`, `gesto_do_marco`, `gesto_da_modalidade`, `gesto_do_campo` | TR `test_o_marco_editado_depois_deixa_de_ser_atribuido_ao_gesto`, `test_a_modalidade_aplicada_aparece_com_a_origem`; TA `test_o_percentual_do_formulario_e_o_do_conteudo_publicado_tem_a_mesma_impressao` |
| **FR-936** | `origens.campos_definitivos`; `revisao.definitivos`; `compor_revisao.html` | TR `test_os_campos_definitivos_aparecem_antes_de_submeter`, `test_o_bloco_dos_definitivos_cobre_o_contrato` |
| **FR-937** | nenhum cartão ganhou texto sobre isso (leitura do diff) | TR `test_nenhum_cartao_da_composicao_ganhou_o_aviso`; `tests/interface/test_medida_dos_campos.py::test_nenhum_cartao_do_assistente_carrega_ajuda_visivel` |
| **FR-938** | **PR seguinte** (US5) | — |
| **FR-939** | **PR seguinte** (US5) | — |
| **FR-940** | **PR seguinte** (US5) | — |
| **FR-941** | **PR seguinte** (US5) | — |
| **FR-942** | **PR seguinte** (US5). A leitura da `FR-802` da `048` está escrita na spec e no `research.md` | — |
| **FR-943** | `validation._perfil_que_corta_sem_forma_de_convocacao`; fixtures canônicas declaram a forma | TP `test_perfil_que_corta_sem_forma_de_convocacao_nao_publica`, `test_com_a_forma_declarada_publica`, `test_a_retificacao_do_acervo_sem_forma_nao_e_recusada_por_isso` |

| `UX-` | Onde | O que o prende |
|---|---|---|
| **UX-110** | botões em `_marco.html` e `_modalidade.html`, só com `quantos_perfis > 1` | TT `test_o_botao_diz_quantos_perfis_alcanca`, `test_edital_de_um_perfil_nao_oferece_o_gesto` |
| **UX-111** | `_previa_da_aplicacao.html`: ordem dos Perfis, caixa marcada, *fora* sem caixa | TT `test_a_previa_declara_cada_perfil_e_nao_grava_nada` |
| **UX-112** | `interface/aplicacao._mudancas_do_marco` usa `revisao._leitura_do_marco` | TT `test_a_previa_declara_cada_perfil_e_nao_grava_nada` (o código e as frases do documento) |
| **UX-113** | `_frase_do_alcance`; o número no botão | TT `test_a_previa_declara_cada_perfil_e_nao_grava_nada`, `test_a_modalidade_nasce_nos_demais_pelo_codigo_e_nao_toca_o_quadro` |
| **UX-114** | a origem entre parênteses ou na linha *"Origem"*, em texto | TR `test_o_marco_aplicado_aparece_com_a_origem_e_o_autor` |
| **UX-115** | seção antes de `.navegacao-etapa` em `compor_revisao.html` | TR `test_os_campos_definitivos_aparecem_antes_de_submeter` |

## 2. Critérios de sucesso

| `SC-` | Como se mede | Resultado |
|---|---|---|
| **SC-340** | percurso no preview, estrutura do 28/2026, antes (`main`) e depois (este branch) — seção 3 | **81 → 16** na Classificação (−80%) |
| **SC-341** | TA `test_aplicar_toca_so_os_incluidos_e_aplicaveis`: aplicar custa o gesto e a confirmação, qualquer que seja N | curva plana |
| **SC-342** | TA `test_aplicar_toca_so_os_incluidos_e_aplicaveis`, `test_nada_fora_da_unidade_muda_no_destino`; TT `test_o_destino_fora_do_alcance_nao_e_tocado_mesmo_forjado`, `test_perfis_intocados_fora_da_unidade` | coberto |
| **SC-343** | TT `test_a_confirmacao_sobre_tela_que_mudou_e_recusada_sem_gravar`, `test_sem_destino_marcado_nada_e_gravado` | coberto |
| **SC-344** | a suíte inteira, que confere o conteúdo, o documento e a validação dos Editais publicados; TP `test_a_retificacao_do_acervo_sem_forma_nao_e_recusada_por_isso` | ver a seção 4 |
| **SC-345** | percurso no preview: o marco de sorteio pede 6 respostas contra 10 (empate, espécie do alvo, Etapa governada e a abertura do bloco do corte saíram); o método comum, 8 contra 10 | −4 por marco, −2 no método |
| **SC-346** | TR `test_o_bloco_dos_definitivos_cobre_o_contrato` | coberto |
| **SC-347** | **PR seguinte** (US5) | — |

## 3. O percurso no preview — a estrutura do 28/2026

Dois bancos semeados pelo mesmo roteiro (`scratchpad/semear_28.py` da sessão): 7 polos idênticos de 40
vagas com PPI 25% e PcD 5%, quadro 28/10/2, a Etapa decisória *Análise documental* e o Evento
*Sorteio eletrônico* no Cronograma. O **antes** rodou a `main` em `850e00b6`; o **depois**, este branch.
Contou-se cada clique, escolha ou campo preenchido, do Edital sem marco ao marco gravado nos 7 polos.

| Passo | Antes | Depois |
|---|---:|---:|
| Método comum do sorteio | 10 (abrir + 9 campos, instante e duas prosas digitados) | 8 (abrir + 7; o instante é escolhido no Cronograma, as prosas saem da regra) |
| Marco do POLO01 | 10 (acrescentar, forma, abrir recurso, admite, prazo, abrir corte, alvo, empate, Etapa governada, faixa) | 6 (acrescentar, forma, abrir recurso, admite, prazo, faixa; o corte já nasce declarado e o empate não é perguntado) |
| Marcos dos POLO02 a POLO07 | 60 (6 × 10) | 2 (*Aplicar aos demais Perfis (6)* e confirmar) |
| Gravar | 1 | 0 (a confirmação grava) |
| **Classificação** | **81** | **16** |
| Forma de convocação nos 7 polos | 8 (7 escolhas + gravar) | 3 (escolher no controle do Edital, aplicar, confirmar) |
| **Total** | **89** | **19** |

A Revisão do **depois** mostra o grupo dos 7 marcos com *"Origem: POLO02 … POLO07 — aplicado a partir
do Perfil POLO01, por ana.elaboradora"*, o corte e o arredondamento com *"padrão do sistema"*, o
instante *"do Evento Sorteio eletrônico"*, as prosas *"gerada da regra escolhida"* e o bloco dos 13
campos que não se corrigem depois de publicados.

**Dois defeitos que só o navegador achou, corrigidos no mesmo PR**: a Revisão quebrava ao ler o gesto
do controle do Edital (um renome incompleto), e o bloco dos definitivos colava o valor na razão. O
primeiro ganhou teste (`test_a_forma_de_convocacao_aplicada_pelo_edital_aparece_com_a_origem`).

## 4. Verificação

`cd backend && make lint check test-pg DB_NAME=ps_051`, em 29/09/2026, depois da escolha pendente, sobre a `main` em `850e00b6`
mesclada: `ruff check` e `ruff format --check` limpos, `check` sem pendência nem migration por fazer, e
a suíte contra PostgreSQL com **8763 passando e 11 pulados**, zero falhas — os mesmos 11 pulados
deliberados que o `CLAUDE.md` descreve.

**O que a suíte achou no caminho, e onde foi corrigido.** A `FR-943` recusou a publicação de todo
construtor de fixture que publica Perfil com corte e sem forma — 201 falhas e 779 erros na primeira
rodada, todos pela mesma causa. A regra ficou; mudaram as fixtures: os construtores canônicos
(`complete_draft`, `rascunho_de_selecao`, `rascunho_com_periodo`, `rascunho_publicavel`, o
construtor do snapshot), o `seed_demo` e os roteiros pela tela declaram a forma; o acervo publica no
instante do acervo (`tests/fixtures/legado.py`), que passou a neutralizar também a regra da `051`; e o
cenário *"sem forma"* da `019` é esse acervo. Dois guardiões pegaram coisa real: o cartão do marco
novo passava dos dez controles da SC-138 da `030` (o bloco do corte padrão nasce fechado desde então),
e a spec citava decisões de outras features pelo número local.
