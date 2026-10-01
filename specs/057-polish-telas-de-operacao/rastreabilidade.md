# Rastreabilidade — 057 · Polish das telas de operação

**Frase que governa**: *em cada tela, a ação que se pratica todo dia é a mais visível, a
excepcional é a mais discreta, e a destrutiva nunca é a mais forte.*

Cada linha aponta o lugar do código e o que o prende. **TP** = `tests/interface/test_polish_da_057.py`;
**TA** = `tests/interface/test_acessibilidade.py`; **TV** = `tests/test_vocabulario_da_composicao.py`;
**TE** = `tests/performance/test_escala_da_mesa.py`; **V** = a linha da [verificação](verificacao.md),
medida na página renderizada; **AÇ** = o diff das listas de destinos
([acoes-antes.json](acoes-antes.json) × [acoes-depois.json](acoes-depois.json)).

F = `interface/templates/interface/`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1043** | `acoes.py`: `hierarquia` e `PREFERENCIA_DA_PRINCIPAL`; `views.detalhe`: `grupo`; `F/detalhe.html` e `F/_acao_do_edital.html` (D-002) | TP `test_a_hierarquia_reparte_sem_perder_acao`, `test_o_ato_que_avanca_e_a_principal_e_o_retrocesso_nao`, `test_o_homologado_tem_publicar_como_unica_cheia`; V 1 |
| **FR-1044** | `acoes.TERMINAIS`; `F/detalhe.html`: `ul.terminais` por último; `F/base.html`: `.lista-acoes.em-linha`, `.terminais`, `.terminais .botao` (D-003) | TP `test_o_detalhe_desenha_as_terminais_por_ultimo_e_so_contornadas`, `test_o_homologado_tem_publicar_como_unica_cheia`; V 1, 2 |
| **FR-1045** | `hierarquia` não promove outra quando a preferida tem motivo; `F/_acao_do_edital.html` mantém o motivo à vista | TP `test_a_preferida_impedida_nao_e_substituida` |
| **FR-1046** | `Hierarquia.__bool__`; a frase de ausência em `F/detalhe.html` | TP `test_sem_acao_o_grupo_e_vazio`, `test_o_detalhe_desenha_as_terminais_por_ultimo_e_so_contornadas` |
| **FR-1047** | `F/detalhe.html`: `.colunas.ao-topo`; `F/base.html`: `align-items:flex-start` | TP `test_o_detalhe_desenha_as_terminais_por_ultimo_e_so_contornadas`; V 3 |
| **FR-1048** | `F/marco.html`: o primeiro gesto `botao`, os demais `botao secundario`, `.gestos` no estilo da página (D-008) | TP `test_a_conducao_destaca_so_o_primeiro_gesto`; V 4 |
| **FR-1049** | `acoes.da_linha` e `FREQUENTES`; `views.lista`; `F/lista.html` e `F/_acao_de_linha.html`; a coluna de ações de 24 para 30 rem (D-004, D-007) | TP `test_a_lista_poe_as_frequentes_primeiro_e_as_terminais_no_fim`; V 5, 6 |
| **FR-1050** | `Acao.quantidade`; `.acao.zerada`; os rótulos presos por teste ficaram (D-005, D-006) | TP `test_o_contador_zero_esmaece_sem_perder_o_rotulo`; `test_inscricoes_recebidas.py` e `test_hardening_pos_auditoria.py` sem mudança |
| **FR-1051** | o `p.definicoes` dentro de `details.como-preencher` em oito templates; `F/base.html`: o seletor de `.como-preencher dl` estendido (D-009) | TP `test_o_glossario_fica_recolhido_e_a_garantia_a_vista` (oito casos); TV; V 7, 8 |
| **FR-1052** | `F/convocacao_historico.html` e `F/ocupacao_historico.html` intocados (D-010) | o `git diff` do PR |
| **FR-1053** | a faixa `.imutavel` fora do `details`; `F/compor_perfis.html` intocado | TP `test_o_glossario_fica_recolhido_e_a_garantia_a_vista`, `test_o_glossario_do_assistente_fica_como_esta` |
| **FR-1054** | `F/base.html`: `.sinais` com a faixa âmbar, `.sinal` sem moldura, filete entre sinais (D-011) | TP `test_a_atencao_e_lista_com_faixa_ambar`; V 9, 10 |
| **FR-1055** | `F/base.html`: `.auditoria li` sem cartão, cabeça e corpo numa linha, motivo embaixo (D-012) | TP `test_o_evento_de_auditoria_nao_e_cartao`; V 11 |
| **FR-1056** | `F/inscricao_detalhe.html` em `ul.documentos`; saem `.requisitos-apresentados`, `.requisito-nome`, `.acoes-do-documento`; o resumo do arquivo no estilo da página (D-013) | TP `test_os_documentos_da_inscricao_seguem_a_mesa`; `test_inscricoes_recebidas.py`; V 12 |
| **FR-1057** | `dl.ficha.curta` em `F/distribuicao.html` e `F/minha_etapa.html`; `.ficha.curta{width:fit-content}` (D-014) | TP `test_a_ficha_curta_tem_a_largura_do_conteudo`; V 13, 14 |
| **FR-1058** | `revisao.py`: `pontuacao` no percentual, Peso, Nota mínima e Pontuação máxima; `_versao`; `_vagas`; "nesse recorte" (D-015) | TP `test_a_revisao_escreve_numeros_datas_e_plurais_como_gente`; `test_revisao.py` e outros quatro ajustados (ver o registro); V 15 |
| **FR-1059** | `supervisao.py` e `conducao_do_marco.py`: `plural` | `test_sinal_do_acervo_sem_quadro.py`; `test_conducao_do_marco.py` |
| **FR-1060** | `retificacao.objeto_legivel`, `editais/domain/validation.py` e os campos numéricos intocados; registro em `doc/achado-f8-textos-que-saem-da-tela.md` | TP `test_o_que_sai_da_tela_fica_como_estava` |
| **FR-1061** | `F/alocacoes.html`: `regroup` e `th[scope=colgroup]`; os três controles numa faixa; `F/base.html`: o cabeçalho compacto (D-016) | TP `test_a_matriz_agrupa_por_edital_e_fixa_o_cabecalho`; V 16, 17 |
| **FR-1062** | `.distribuicao thead{position:sticky}`; `.distribuicao-moldura{overflow-x:visible}` mantido | TP `test_a_matriz_agrupa_por_edital_e_fixa_o_cabecalho`; TA `test_o_cabecalho_da_matriz_nao_e_fixado_dentro_de_um_contentor_de_rolagem` |
| **FR-1063** | `portal/_documentos.html`: "Enviar" dentro de `.escolher`; sai `.envio .linha` (D-018) | TP `test_o_envio_de_documento_e_uma_linha`; `tests/javascript/` sem mudança; V 18 |
| **FR-1064** | nenhum `href`, `action` ou botão mudou (D-017) | AÇ: zero diferenças em 62 telas de `ana.gestora` e 49 de `joana.avaliadora`; o portal, idem |
| **FR-1065** | nenhuma view, rota, permissão ou recusa nova; `views.py` só monta contexto | o `git diff` do PR; o inventário de negativas da `033` na suíte |
| **FR-1066** | prosa nova em `{% comment %}`; regras mortas fora; estilo de tela no bloco dela | TE; V 19 |
| **FR-1067** | o PDF, o conteúdo publicado, o `seed_demo` e o assistente (fora da Revisão) intocados | o `git diff` do PR |
| **FR-1068** | a coluna de ações e a matriz medidas a 375 px | V "A 375 px" |

## 2. Critérios de sucesso

| Identificador | Como se mede | Resultado |
|---|---|---|
| **SC-398** | V 1 a 3 | atendido |
| **SC-399** | V 4 | atendido |
| **SC-400** | V 5 | atendido: 118 → 82 px |
| **SC-401** | V 7, 8; TV | **parcial**: glossário fechado, faixa à vista, TV verde; o ganho é de 32 a 53 px, e não 120 (fora de alcance; justificativa na verificação) |
| **SC-402** | V 9, 10 | atendido |
| **SC-403** | V 11 | atendido |
| **SC-404** | V 12 a 14 | atendido |
| **SC-405** | V 15 | atendido |
| **SC-406** | V 16, 17 | atendido |
| **SC-407** | V 18 | atendido |
| **SC-408** | AÇ | atendido: diff vazio |
| **SC-409** | a suíte e TE | ver a verificação e o PR |
| **SC-410** | V "A 375 px" | atendido: nada piorou; o corte da Lista e a rolagem da Condução são anteriores, e viraram registro |

## 3. Requisitos de experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-140** | **FR-1043**, **FR-1044**, **FR-1048**, **FR-1049** | TP os testes da hierarquia; V 1, 4, 5 |
| **UX-141** | **FR-1051**, **FR-1053** | TP `test_o_glossario_fica_recolhido_e_a_garantia_a_vista` |
| **UX-142** | **FR-1054** a **FR-1057** | TP os testes de T3; V 9 a 14 |
