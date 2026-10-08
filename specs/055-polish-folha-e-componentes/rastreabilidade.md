# Rastreabilidade — 055 · Polish da folha e dos componentes

**Frase que governa**: *mesma informação, mesmo desenho, mesma altura — e nenhuma mudança que não se
possa medir.*

Cada linha aponta o lugar do código e o que o prende. **TP** = `tests/interface/test_polish_da_055.py`;
**TA** = `tests/interface/test_acessibilidade.py`; **TL** = `tests/interface/test_larguras.py`;
**TE** = `tests/performance/test_escala_da_mesa.py`; **V** = a linha da
[verificação](verificacao.md), medida na página renderizada.

F = `interface/templates/interface/`; P = `portal/templates/portal/`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1000** | `F/ocupacao.html`: a `section` sem `.resumo`; os quatro números em `ul.resumo` | TP `test_os_numeros_vao_para_o_bloco_da_convocacao[ocupacao.html]`, `test_a_ocupacao_apurada_mostra_os_quatro_blocos`; V 2 |
| **FR-1001** | `F/ocupacao.html`: "Publicadas" sozinha em `ul.resumo` no recorte não apurado | TP `test_sem_apuracao_so_a_publicada_vai_ao_bloco`; `test_ocupacao.py::test_sem_apuracao_a_tela_diz_que_nao_apurou_e_nao_mostra_zero` |
| **FR-1002** | `F/corte.html` e `F/corte_historico.html`: a faixa e a regra em `ul.resumo`; a proveniência em `dl.participantes` (D-020) | TP `test_a_faixa_calculada_poe_cada_numero_no_bloco_do_seu_rotulo`, `test_o_historico_do_corte_separa_numeros_de_proveniencia`, `test_os_numeros_vao_para_o_bloco_da_convocacao[corte.html]`, `[corte_historico.html]`; V 1 |
| **FR-1003** | `F/ocupacao_historico.html`: a `section` sem `.resumo`; os números de cada apuração em `ul.resumo` | TP `test_os_numeros_vao_para_o_bloco_da_convocacao[ocupacao_historico.html]` |
| **FR-1004** | `F/base.html`: `th,td` com `.5rem .75rem`; saem as duas declarações iguais (D-010) | TP `test_a_celula_tem_o_preenchimento_do_portal`; V 3 |
| **FR-1005** | `F/ordenacao.html`: `table.tabela` e `numero` na Pontuação combinada (D-011) | TP `test_a_pontuacao_da_ordem_fica_a_direita`; V 31 |
| **FR-1006** | `F/base.html`: a caixa partilhada de `.botao`; borda transparente; `.secundario` com `border-color`; `.perigoso` sem `border:none` (D-002, D-003) | TP `test_principal_e_secundario_tem_a_mesma_caixa`; V 4, 5 |
| **FR-1007** | `F/base.html`: `:is(.navegacao-etapa,.salvar,.filtros) .acao` na mesma caixa (D-004) | TP `test_principal_e_secundario_tem_a_mesma_caixa`, `test_fora_da_barra_a_acao_de_linha_continua_pequena`; V 4, 6, 7, 8 |
| **FR-1008** | `F/inscricoes.html`, `F/distribuicao.html`, `F/comissao.html`, `F/matriculas.html`: `acao` → `botao` (D-005) | TP `test_a_acao_principal_nao_tem_o_desenho_de_acao_de_linha` (quatro casos); V 9, 10 |
| **FR-1009** | `P/requerimento.html`: `class="secundario"`; a guarda estendida ao portal (D-017) | TA `test_todo_botao_de_envio_declara_o_seu_peso[portal/…]`; V 11 |
| **FR-1010** | `F/base.html`: `h3{font-size:1rem}` e `h1,h2,h3{font-weight:600}` | TP `test_a_escala_dos_tres_niveis`; V 12, 13 |
| **FR-1011** | `F/base.html`: sai o tamanho de `.cartao h2`, `.pendencias h2`, `.consequencias h2`, `.conferencia h3`; e tamanho e caixa-alta de `.secao-da-retificacao>h2` (D-008) | TP `test_nenhum_conteiner_poe_h2_no_tamanho_de_h3`, `test_o_titulo_da_secao_da_retificacao_nao_grita`; V 14, 15 |
| **FR-1012** | `F/base.html`: `select,input:not(…){height:2.5rem}` (D-009); `P/base.html`: `height:2.625rem` nos controles de `.campo` (D-016) | TP `test_uma_altura_por_folha_para_os_controles_de_uma_linha`; V 16 a 19 |
| **FR-1013** | `F/base.html`: `.filtro,.filtros` por `flex-start`; margem do rótulo em `.filtro .salvar`, `.filtros .acoes` e `.filtro .escolha` (D-006) | TP `test_a_barra_de_filtro_alinha_pelo_topo_e_o_botao_desce_a_altura_do_rotulo`; V 20 a 23 |
| **FR-1014** | a ajuda dos filtros continua no `span.ajuda` ligado por `aria-describedby` | TP `test_a_ajuda_do_filtro_continua_ligada_ao_campo` (dois casos); V 20 |
| **FR-1015** | `P/base.html`: a grade larga sem a área `sorteio`, e com ela por `:has(>.sorteio-da-selecao)` (D-012) | TP `test_a_selecao_sem_sorteio_nao_reserva_a_area_dele`; V 24, 25 |
| **FR-1016** | `P/base.html`: `auto-fill` e `max-width:40rem` no largo (D-013); `F/comissao.html`: `type="text"` e o teto do identificador (D-014); `F/base.html`: `.arquivo` com `width:auto` (D-015) | TP `test_o_campo_curto_do_requerimento_nao_estica_a_linha`, `test_os_campos_da_comissao_tem_largura_pelo_conteudo`, `test_o_campo_de_arquivo_nao_herda_a_largura_da_linha`; V 26 a 30 |
| **FR-1017** | o saldo de −69 caracteres na folha da gestão e no `distribuicao.html`; prosa nova em comentário de Django (D-001) | TE `test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`; V "O teto da distribuição" |
| **FR-1018** | as disposições novas quebram em coluna em tela estreita | TL (as larguras nos tokens, sem `max-width` em px); V "A 375 px" |
| **FR-1019** | nenhum texto de interface, view, formulário, domínio ou PDF no diff; nenhum token novo | o `git diff` do PR; TL `test_as_duas_larguras_vivem_nos_tokens` |

## 2. Critérios de sucesso

| Identificador | Como se mede | Resultado |
|---|---|---|
| **SC-371** | V 1 | atendido |
| **SC-372** | V 2 | atendido |
| **SC-373** | V 3 | **parcial**: 39,5 px sem a marca de CPF repetido, 62,8 px com ela (D-021) |
| **SC-374** | V 4 | atendido |
| **SC-375** | V 9, 10 | atendido |
| **SC-376** | V 11 | atendido |
| **SC-377** | V 12, 13 | atendido |
| **SC-378** | V 16, 17, 18 | atendido |
| **SC-379** | V 20 | atendido |
| **SC-380** | V 24 | atendido |
| **SC-381** | V 26 | atendido |
| **SC-382** | V 27 | atendido |
| **SC-383** | V 31 | atendido |
| **SC-384** | a suíte e TE | ver o PR |
| **SC-385** | V "A 375 px" | atendido |

## 3. Requisitos de experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-134** | o G1 inteiro (**FR-1000** a **FR-1003**) | TP os testes do G1; V 1, 2 |
| **UX-135** | **FR-1006** a **FR-1008** | TP os testes de botão; V 4 a 10 |
| **UX-136** | **FR-1014** | TP `test_a_ajuda_do_filtro_continua_ligada_ao_campo` |
