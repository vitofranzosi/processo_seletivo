# Rastreabilidade — 056 · Polish do assistente de composição

**Frase que governa**: *quem abre uma etapa do assistente vê o trabalho da etapa na primeira dobra,
e cada item da coleção ocupa a altura do que ele tem a dizer.*

Cada linha aponta o lugar do código e o que o prende. **TP** = `tests/interface/test_polish_da_056.py`;
**TJ** = `tests/javascript/ordenacao.test.js`; **TA** = `tests/interface/test_acessibilidade.py`;
**TE** = `tests/performance/test_escala_da_mesa.py`; **V** = a linha da
[verificação](verificacao.md), medida na página renderizada.

F = `interface/templates/interface/`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1020** | `F/base.html`: `.assistente` em grade `repeat(auto-fit,minmax(7.5rem,1fr))`; o número ao lado do nome (D-002) | TP `test_o_stepper_e_grade_de_colunas_iguais`; V 1, 2 |
| **FR-1021** | a mesma grade: colunas iguais em qualquer largura; sai `flex:1 1 160px` | TP `test_o_stepper_e_grade_de_colunas_iguais`; V "A 375 px" |
| **FR-1022** | `F/base.html`: `.estado` sem caixa-alta; o texto e o marcador vazado ficam | TP `test_a_situacao_da_etapa_continua_em_texto`; V 1 |
| **FR-1023** | `F/base.html`: `fieldset.linha>.acoes-da-linha` na borda de cima; `F/_evento.html`, `_etapa.html`, `_documento.html`, `_modalidade.html`: o grupo logo depois da legenda (D-003) | TP `test_as_acoes_moram_na_linha_da_legenda` (quatro casos), `test_a_folha_leva_o_grupo_para_a_borda_e_o_devolve_em_tela_estreita`; V 8 a 11 |
| **FR-1024** | as quatro legendas em duas vozes, com `[data-ordem]` nas ordenáveis e `.nome` só com identificador (D-004) | TP `test_a_legenda_nomeia_o_item_sem_mudar_a_confirmacao` (quatro casos), `test_o_evento_novo_tem_legenda_sem_nome_e_o_gravado_com_o_tipo`; V 7, 10 |
| **FR-1025** | `static/interface/ordenacao.js`: a posição em `[data-ordem]` | TJ `a posição vai para o lugar dela, e o nome do item continua na legenda`; V 12 |
| **FR-1026** | `F/base.html`: `@media (max-width:60rem)` devolve o grupo ao fluxo | TP `test_a_folha_leva_o_grupo_para_a_borda_e_o_devolve_em_tela_estreita`; V "A 375 px" |
| **FR-1027** | `data-rotulo` igual à categoria; nenhum botão na `legend`; `aria-label` das ações intocado | TP `test_a_legenda_nomeia_o_item_sem_mudar_a_confirmacao`; `tests/javascript/remocao.test.js` |
| **FR-1028** | `F/_evento.html`: Descrição `largo`, "Onde acontece" no fim como `.campo.local`; `F/compor_cronograma.html`: `.campo.local{flex:0 1 20rem}` (D-006) | TP `test_a_faixa_do_evento_poe_as_datas_juntas_e_o_local_no_fim`; `test_medida_dos_campos.py::test_o_evento_cabe_numa_linha`; V 4, 5 |
| **FR-1029** | `F/compor_conteudo.html`: `fieldset.secao` com `max-width` de leitura (D-007) | TP `test_a_secao_gerada_nao_tem_caixa_e_o_caminho_fica_na_frase`; V 15 |
| **FR-1030** | `F/compor_conteudo.html`: `rows` 2 sem conteúdo, 5 com | TP `test_a_secao_vazia_nasce_com_duas_linhas_e_a_escrita_com_cinco`; V 15 |
| **FR-1031** | a marca com o mesmo texto, sem caixa-alta (D-008); `conteudo.js` intocado | TP `test_a_marca_de_secao_vazia_continua_no_nome_do_campo`; `test_conteudo_da_054.py`; `tests/javascript/conteudo.test.js`; V 14, 16 |
| **FR-1032** | a seção gerada sem caixa, o link no fim da frase, o texto de ajuda igual (D-009) | TP `test_a_secao_gerada_nao_tem_caixa_e_o_caminho_fica_na_frase`; V 15 |
| **FR-1033** | `origens.py`: `Rotulada`; `revisao.py` e `origens.campos_definitivos`: as linhas rotuladas; `templatetags/interface_extras.py`: `em_trechos`; `F/_linhas_da_revisao.html` e `F/compor_revisao.html` (D-010) | TP `test_os_trechos_juntam_vizinhos_e_nao_partem_texto_de_quem_elabora`, `test_a_revisao_poe_os_rotulos_numa_coluna`; V 17 |
| **FR-1034** | `Rotulada` é a mesma `str`; `com_origem` a preserva | TP `test_a_linha_rotulada_e_a_mesma_cadeia`; `tests/unit/interface/test_revisao*.py` sem mudança; V 18 |
| **FR-1035** | `F/_perfil.html` (Descrição) e `F/_documento.html` (Instrução) em `textarea` de 2 linhas | TP `test_o_texto_longo_do_compor_e_area_de_texto_com_o_mesmo_nome` (dois casos); V 19, 20 |
| **FR-1036** | `retificacao.py`: `CAMPOS_RAIZ` com `TEXTO_LONGO` nos três; `F/_retificacao_linha.html`: 2 ou 4 linhas (D-011, D-014) | TP `test_os_tres_campos_longos_do_retificar_sao_texto_longo`; V 21, 22 |
| **FR-1037** | `F/base.html`: `.navegacao-etapa{max-width:none}`; `F/compor_anexos.html`: o estado vazio (D-012) | TP `test_a_navegacao_da_etapa_nao_herda_a_medida_de_leitura`; V 23, 24 |
| **FR-1038** | `retificacao.py`: `ORDEM_DO_PERFIL_NO_COMPOR` e `na_ordem_do_compor`; filtro `campos_na_ordem_do_compor` em `F/_retificacao_linha.html` (D-013) | TP `test_o_perfil_se_desenha_na_ordem_do_compor_sem_renomear_campo`; V 25 |
| **FR-1039** | nenhum `name` mudou; o envio capturado antes e depois (D-005, D-015) | V "O envio de 'Salvar rascunho'" |
| **FR-1040** | prosa nova da folha em comentário de Django; estilo de etapa no `estilo_da_pagina`; saem as regras mortas | TE `test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`; TP `test_a_folha_leva_o_grupo_para_a_borda_e_o_devolve_em_tela_estreita`; V "O teto da distribuição" |
| **FR-1041** | nenhuma view de gravação, formulário de domínio, PDF ou texto de ajuda no diff, além da marca de seção vazia (que manteve o texto) | o `git diff` do PR; TA (classes com regra) |
| **FR-1042** | o stepper em grade, o grupo de ações no fluxo abaixo de 60 rem, a seção na medida de leitura | V "A 375 px" |

## 2. Critérios de sucesso

| Identificador | Como se mede | Resultado |
|---|---|---|
| **SC-386** | V 1 | atendido: 66 px, uma linha |
| **SC-387** | V 2 | atendido: y = 416 |
| **SC-388** | V 4, 5 | atendido |
| **SC-389** | V 6 | **fora de alcance**: 215 → 216 px (D-006; justificativa na verificação) |
| **SC-390** | V 7 a 11 | atendido |
| **SC-391** | V 13, 14 | atendido: 2.908 px |
| **SC-392** | V 17 | atendido: +4,2% |
| **SC-393** | V 19 a 21 | atendido |
| **SC-394** | V 23 | atendido |
| **SC-395** | V "O envio" | atendido: diff vazio |
| **SC-396** | a suíte e TE | ver o PR |
| **SC-397** | V "A 375 px" | atendido |

## 3. Requisitos de experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-137** | **FR-1020** a **FR-1022** | TP os testes do stepper; V 2, 3 |
| **UX-138** | **FR-1023**, **FR-1030**, **FR-1032** | TP os testes dos cartões e do Conteúdo; V 8 a 10, 15 |
| **UX-139** | **FR-1024** | TP `test_a_legenda_nomeia_o_item_sem_mudar_a_confirmacao`; V 7, 10 |
