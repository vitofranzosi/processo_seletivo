# Rastreabilidade: Conferência antes de convocar os titulares (140)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`. Abreviações:

- `cc` = `interface/test_conferencia_ao_convocar.py` — a conferência, a confirmação e a porta
- `cf` = `interface/test_convocacao_em_fluxo.py` — a tela da convocação da `050`
- `ct` = `interface/test_conferencia_do_texto.py` — a conferência de texto da `125`
- `lg` = `integration/convocacao/test_lista_da_chamada_no_gesto.py` — o comando do gesto

A faixa abre em **FR-4800**, **SC-1500** e **UX-330**. Gastos até FR-4819, SC-1505 e UX-332; o resto
da reserva (até o requisito quatro mil oitocentos e vinte e nove, o critério mil quinhentos e nove e
o UX trezentos e trinta e nove) fica livre.

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-4800 — sempre a conferência, com ou sem complemento | T004 | `cc::test_a_conferencia_nao_envia_nao_convoca_e_nao_grava_nada`, `cc::test_confirmar_sem_o_resumo_abre_a_conferencia`, `ct::test_sem_complemento_o_gesto_passa_pela_conferencia_da_140` |
| FR-4801 — pessoas, ordem e espécie com a origem | T003, T005 | `cc::test_a_conferencia_diz_quem_o_texto_o_prazo_e_quem_fica_de_fora` |
| FR-4802 — o fundamento como o portal o mostra | T003, T005 | `cc::test_a_conferencia_diz_quem_o_texto_o_prazo_e_quem_fica_de_fora`, `ct::test_com_complemento_a_previa_vem_antes_e_nao_pratica_nada`, `ct::test_confirmada_a_previa_o_candidato_le_o_mesmo_texto` |
| FR-4803 — a mensagem do modelo do envio | T002 | `cc::test_a_mensagem_conferida_e_a_que_sai` |
| FR-4804 — por publicação, sem mensagem | T003, T005 | `cc::test_por_publicacao_a_conferencia_nao_promete_envio` |
| FR-4805 — o prazo, ou a falta dele | T003, T005 | `cc::test_a_conferencia_diz_quem_o_texto_o_prazo_e_quem_fica_de_fora`, `cc::test_sem_vencimento_a_conferencia_diz_a_falta_e_o_que_a_mensagem_dira` |
| FR-4806 — quem fica de fora e por quê | T003, T005 | `cc::test_a_conferencia_diz_quem_o_texto_o_prazo_e_quem_fica_de_fora` |
| FR-4807 — a prévia não grava nada | T003, T004 | `cc::test_a_conferencia_nao_envia_nao_convoca_e_nao_grava_nada` (convocação, comunicação, mensagem, trilha, chave e sessão) |
| FR-4808 — a chave e o alcance da tela, intactos | T004, T007 | `cc::test_a_confirmacao_carrega_a_chave_e_o_alcance_da_tela`, `ct::test_a_volta_preserva_o_que_foi_preenchido`, `cc::test_a_confirmacao_repetida_nao_duplica_nada` |
| FR-4809 — o resumo do texto conferido | T004, T007 | `cc::test_o_texto_que_mudou_volta_a_conferencia_sem_ato`, `ct::test_texto_editado_na_previa_volta_a_previa` |
| FR-4810 — alcance mudado recusa com a razão | T003, T007 | `cc::test_o_alcance_que_mudou_depois_da_conferencia_recusa_com_a_razao`, `cf::test_a_recusa_por_alcance_mudado_mostra_o_alcance_de_agora` |
| FR-4811 — as recusas do comando, antes do botão, de uma função só | T001, T003 | `cc::test_vencimento_no_passado_recusa_antes_do_botao`, `cc::test_sem_titular_a_chamar_a_conferencia_recusa`; o comando continua coberto por `lg` e `integration/convocacao/test_titulares_em_lote.py` |
| FR-4812 — a confirmação repetida vai ao comando | T003, T007 | `cc::test_a_confirmacao_repetida_nao_duplica_nada` |
| FR-4813 — a autorização de hoje | T004, T008 | `cc::test_quem_nao_pode_convocar_continua_recusado` (auditor e elaborador, na conferência e na confirmação) |
| FR-4814 — o complemento editável, o vencimento não | T005 | `cc::test_o_texto_que_mudou_volta_a_conferencia_sem_ato`, `ct::test_a_volta_preserva_o_que_foi_preenchido` |
| FR-4815 — Cancelar e voltar ao mesmo recorte | T005 | `cc::test_cancelar_volta_a_tela_do_mesmo_recorte` |
| FR-4816 — o botão e a ajuda da tela | T009 | `cc::test_o_botao_da_tela_leva_a_conferencia_e_a_ajuda_nao_promete_o_que_nao_ha`, `cf::test_a_previa_declara_o_alcance_antes_do_botao_e_nao_pratica_nada` |
| FR-4817 — a chamada individual, a regularização e a correção como estão | T010 | `ct::test_a_chamada_individual_com_complemento_tambem_confere`, `cf::test_a_chamada_individual_nao_pergunta_a_especie_e_ja_comunica`, a suíte da `120` sem alteração |
| FR-4818 — sem script e sem estilo no template | T005 | `test_politica_de_conteudo.py` e os guardiões de folha (`test_acessibilidade.py`, `test_estaticos.py`) sobre o template novo; no navegador, nenhuma violação de CSP (verificação manual, `quickstart` abaixo) |
| FR-4819 — a ajuda da correção, condicional | T009 | verificação de leitura do `_correcao_da_convocacao.html`; a frase é a mesma família da FR-4816 |

## Critérios de sucesso

| Critério | Teste |
|---|---|
| SC-1500 — sem o resumo, nada acontece | `cc::test_a_conferencia_nao_envia_nao_convoca_e_nao_grava_nada`, `cc::test_confirmar_sem_o_resumo_abre_a_conferencia` |
| SC-1501 — a conferência do C10, a 1440 e a 375 px | verificação no navegador (`verificacao.md`) |
| SC-1502 — duas confirmações, uma convocação e uma mensagem por pessoa | `cc::test_a_confirmacao_repetida_nao_duplica_nada` |
| SC-1503 — mudança de alcance ou de texto não convoca | `cc::test_o_alcance_que_mudou_depois_da_conferencia_recusa_com_a_razao`, `cc::test_o_texto_que_mudou_volta_a_conferencia_sem_ato` |
| SC-1504 — quem não pode continua recusado | `cc::test_quem_nao_pode_convocar_continua_recusado` |
| SC-1505 — a mensagem conferida é a enviada | `cc::test_a_mensagem_conferida_e_a_que_sai` |

## Requisitos de experiência

| Requisito | Teste |
|---|---|
| UX-330 — o desenho das conferências da gestão | `cc::test_a_conferencia_diz_quem_o_texto_o_prazo_e_quem_fica_de_fora` (`consequencias irreversivel`, "Cancelar e voltar") |
| UX-331 — o botão repete pessoas e mensagens | `cc::test_a_conferencia_diz_quem_o_texto_o_prazo_e_quem_fica_de_fora`, `cc::test_por_publicacao_a_conferencia_nao_promete_envio` |
| UX-332 — a recusa diz a razão e a volta, sem formulário | `cc::test_o_alcance_que_mudou_depois_da_conferencia_recusa_com_a_razao`, `cc::test_sem_titular_a_chamar_a_conferencia_recusa` |

## Casos-limite

| Caso | Teste |
|---|---|
| Nada a convocar (impedimento, intermediário, sem titular, Processo final) | `cc::test_sem_titular_a_chamar_a_conferencia_recusa`; as demais recusas são as da `verificar_titulares`, a mesma função do comando, cujos testes (`integration/convocacao/test_convocacao_em_marco_intermediario.py`, `test_titulares_em_lote.py`) continuam verdes |
| Vencimento inválido | `cc::test_vencimento_no_passado_recusa_antes_do_botao` |
| A conferência recarregada | `cc::test_a_conferencia_nao_envia_nao_convoca_e_nao_grava_nada` (o segundo pedido, com `etapa=conferir`) |
| Formulário antigo ou forjado com "confirmar" | `cc::test_confirmar_sem_o_resumo_abre_a_conferencia` |
| A virada do dia | o resumo inclui a frase do prazo e o corpo da mensagem (`_texto_conferido_dos_titulares`); coberto pelo mecanismo de `cc::test_o_texto_que_mudou_volta_a_conferencia_sem_ato` |
| Duas mensagens diferentes no mesmo gesto | `previa_das_mensagens` agrupa por variante; o cenário de teste tem uma variante só — sem teste próprio, registrado |
| Quem só lê a convocação | `cc::test_quem_nao_pode_convocar_continua_recusado` |
