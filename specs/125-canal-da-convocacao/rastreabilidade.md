# Rastreabilidade: A convocação segue o canal (125)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos de teste relativos a
`backend/tests/`. Abreviações:

- `vi` = `integration/convocacao/test_visibilidade_ao_candidato.py` — o predicado, a cadeia, as
  superfícies do portal, o Requerimento e o custo
- `ct` = `interface/test_conferencia_do_texto.py` — o aviso e a prévia na condução
- `cg` = `interface/test_canal_da_convocacao_na_gestao.py` — a tela de condução e o histórico, por
  publicação
- `vo` = `unit/convocacao/test_vocabulario_do_canal.py` — a tabela das frases
- `pc` = `interface/test_portal_convocacao.py` — a tela da convocação (a linha da substituída, D-008)
- `ob` = `unit/portal/test_obrigacoes_da_convocacao.py` — a projeção (a linha da substituída)
- `cf` = `interface/test_convocacao_em_fluxo.py` — a condução da `050` (o rótulo do derivado)

A faixa abre em **FR-3981** e **SC-1201**, e as duas foram gastas: nenhuma reserva ficou sem requisito.

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-3981 — o predicado *visível ao candidato* | T001 | `vi::TestOPredicado`, `vi::TestACadeia` |
| FR-3982 — ausente em toda superfície, a mesma convocação nas três | T002 | `vi::TestAsSuperficiesDoPortal::test_a_lista_e_o_acompanhamento_nao_mostram`, `::test_depois_do_registro_todas_mostram` |
| FR-3983 — a tela de quem não tem convocação, sem leitura na trilha | T004 | `vi::TestAsSuperficiesDoPortal::test_a_tela_e_a_de_quem_nao_tem_convocacao_e_nao_registra_leitura` |
| FR-3984 — *houve convocação* só com visíveis | T004 | `vi::TestAsSuperficiesDoPortal::test_outro_inscrito_do_recorte_nao_le_que_o_certame_convocou` |
| FR-3985 — envio e arquivo recusados como inexistentes | T005 | `vi::TestAsSuperficiesDoPortal::test_o_envio_de_documento_e_recusado_como_inexistente`, `::test_o_comando_recusa_o_envio_sem_a_tela`, `::test_o_arquivo_apresentado_antes_da_regra_tambem_some` |
| FR-3986 — o Requerimento da chamada segue a convocação | T003 | `vi::TestORequerimentoDaChamada`, `vi::TestOPredicado::test_publicacao_sem_registro_e_invisivel` |
| FR-3987 — registrada, aparece na leitura seguinte | T002 | `vi::TestAsSuperficiesDoPortal::test_depois_do_registro_todas_mostram` |
| FR-3988 — a mensagem não muda | T001 | `vi::TestOPredicado::test_mensagem_sem_envio_continua_visivel`; a suíte da `118` e da `121`, em K-msg, sem mudança |
| FR-3989 — a gestão vê toda convocação, e diz que o candidato não vê | T001, T017 | `vi::TestOPredicado::test_publicacao_sem_registro_e_invisivel`, `cg::test_sem_registro_a_tela_diz_publicacao_e_que_o_candidato_nao_ve` |
| FR-3990 — o custo não cresce | T001 | `vi::TestOCusto`; `performance/test_lista_com_convocacao.py` e `performance/test_area_do_candidato.py`, sem mudança |
| FR-3991 — o aviso nos sete campos | T010 | `ct::test_cada_campo_diz_que_o_texto_chega_ao_candidato` (titulares e individual); os outros cinco, por leitura do template na verificação |
| FR-3992 — visível, fora de bloco recolhível | T010 | `ct::test_cada_campo_diz_que_o_texto_chega_ao_candidato` |
| FR-3993 — a prévia antes do botão, da mesma composição | T011, T012 | `ct::test_com_complemento_a_previa_vem_antes_e_nao_pratica_nada`, `::test_o_desfecho_passa_sempre_pela_previa`, `::test_a_chamada_individual_com_complemento_tambem_confere` |
| FR-3994 — quantas pessoas | T012 | `ct::test_com_complemento_a_previa_vem_antes_e_nao_pratica_nada` (2), `::test_o_desfecho_passa_sempre_pela_previa` (1) |
| FR-3995 — sem script, e a volta preservada | T011 | `ct::test_a_volta_preserva_o_que_foi_preenchido`; o cliente de teste não roda script |
| FR-3996 — as garantias de hoje, e a prévia não pratica nada | T012 | `ct::test_com_complemento_a_previa_vem_antes_e_nao_pratica_nada`, `::test_texto_editado_na_previa_volta_a_previa`, `::test_sem_complemento_o_gesto_e_direto_como_hoje` |
| FR-3997 — a correção (ajustada, D-004, aceita em 06/11) | T013 | o mesmo caminho de `convocar_view`, coberto por `ct::test_a_chamada_individual_com_complemento_tambem_confere`; o rótulo, na verificação |
| FR-3998 — *"Publicada em ‹referência›"* e *"contado da publicação"* no portal | T016 | `vi::TestAsSuperficiesDoPortal::test_depois_do_registro_todas_mostram` |
| FR-3999 — a frase do prazo não iniciado por canal | T016 | `vo::test_a_frase_do_prazo_nao_iniciado_e_a_de_sempre_na_mensagem` |
| FR-4000 — a gestão na língua da publicação | T017 | `cg` (os três casos) |
| FR-4001 — as recusas por canal | T018 | `vo::test_a_publicacao_nao_fala_de_envio[recusa_*]`, `vo::test_a_mensagem_nao_fala_de_publicacao[recusa_*]` |
| FR-4002 — a mensagem não muda, salvo a linha da substituída | T016 | `vo::test_a_mensagem_nao_fala_de_publicacao`, `pc::TestACorrecaoNoPortal`, `ob::TestASubstituida` |
| FR-4003 — nada afirma que a publicação foi vista | T015 | `vo::test_a_publicacao_nao_fala_de_envio`; `pc::TestAConvocacaoDaPropriaPessoa::test_a_tela_nao_afirma_recebimento_nem_promete_a_vaga` |
| FR-4004 — uma fonte só, varrida nas duas formas | T015, T019 | `vo` (todas as frases, nas duas formas), `cg::test_sem_registro_a_tela_diz_publicacao_e_que_o_candidato_nao_ve` |
| FR-4005 — o prazo, a mensagem individual, os e-mails e os avisos não mudam | — | `envio_de` intocado; a suíte da `019`, da `066` e da `121` sem mudança |
| FR-4006 — sem tabela, coluna, situação nova, e nada apagado | — | `migrations/` sem arquivo novo; `makemigrations --check` no `make check` |

## Critérios de sucesso

| Critério | Teste |
|---|---|
| SC-1201 — as sete superfícies em K-pub, e zero registros | `vi::TestAsSuperficiesDoPortal`, `vi::TestORequerimentoDaChamada` |
| SC-1202 — registrada, na leitura seguinte | `vi::TestAsSuperficiesDoPortal::test_depois_do_registro_todas_mostram`, `vi::TestORequerimentoDaChamada` |
| SC-1203 — K-msg idêntico ao de hoje | `vi::TestOPredicado::test_mensagem_sem_envio_continua_visivel`; a suíte da `118`/`121` em K-msg, sem asserção alterada salvo a linha da substituída |
| SC-1204 — o custo não cresce | `vi::TestOCusto` |
| SC-1205 — o aviso nos sete campos | `ct::test_cada_campo_diz_que_o_texto_chega_ao_candidato`; verificação |
| SC-1206 — a prévia sempre, e o texto do portal igual ao dela | `ct::test_confirmada_a_previa_o_candidato_le_o_mesmo_texto`, `::test_a_chamada_individual_com_complemento_tambem_confere` |
| SC-1207 — o número igual ao de atos | `ct::test_confirmada_a_previa_o_candidato_le_o_mesmo_texto` |
| SC-1208 — zero frases de envio na publicação, e de publicação na mensagem | `vo`, `cg` |
| SC-1209 — o operador diz sem ajuda que o candidato não vê | `cg::test_sem_registro_a_tela_diz_publicacao_e_que_o_candidato_nao_ve`; **validação humana pendente** |

## Casos-limite

| Caso | Teste |
|---|---|
| Correção de convocação já publicada (D-001) | `vi::TestACadeia::test_correcao_de_publicada_continua_visivel` |
| Correção de convocação nunca publicada | `vi::TestACadeia::test_correcao_de_nao_publicada_continua_invisivel` |
| Cadeia de três elos | `vi::TestACadeia::test_tres_elos_com_a_raiz_publicada` |
| Forma trocada por Retificação entre A e B | o predicado olha qualquer comunicação bem-sucedida da cadeia, em qualquer forma (R-002); sem teste próprio |
| Forma não declarada | `vi::TestOPredicado::test_a_forma_do_perfil_nao_declarada_e_none` |
| Desfecho antes da publicação (D-002) | `vi::TestOPredicado::test_desfecho_antes_da_publicacao_nao_a_torna_visivel` |
| Arquivo enviado antes desta feature | `vi::TestAsSuperficiesDoPortal::test_o_arquivo_apresentado_antes_da_regra_tambem_some` |
| Duas inscrições da mesma pessoa | o seletor escolhe por inscrição; `integration/convocacao/test_vigentes_por_inscricao.py` |
| O recorte só com convocações sem registro | `vi::TestAsSuperficiesDoPortal::test_outro_inscrito_do_recorte_nao_le_que_o_certame_convocou` |
| Complemento vazio | `ct::test_sem_complemento_o_gesto_e_direto_como_hoje` |
| Fundamento do indeferimento pré-preenchido | o mesmo caminho do desfecho, `ct::test_o_desfecho_passa_sempre_pela_previa` |
| Lote de uma pessoa | `ct::test_o_desfecho_passa_sempre_pela_previa` (*"a 1 pessoa"*) |
| Texto longo ou com quebra de linha | a prévia mostra o texto como o portal, sem filtro de quebra; verificação |
| Referência vazia em registro antigo | `_comunicacao_da_convocacao.html` diz *"referência não registrada"*; sem teste próprio |
