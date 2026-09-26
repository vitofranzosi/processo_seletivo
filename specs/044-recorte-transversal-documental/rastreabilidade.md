# Rastreabilidade — recorte transversal do documento exigido

**Feature**: `044-recorte-transversal-documental` · **Data**: 2026-09-25

Cada requisito, critério e caso-limite da spec, com onde a garantia mora e onde ela é cobrada.
Onde a coluna diz **navegador**, a verificação foi feita no percurso pela interface desta sessão
(banco `ps044`, porta 8045), descrito ao fim. Onde diz **percurso da Mesa**, no segundo percurso,
de 26/09, que chegou à Mesa com o relógio real (banco `ps044mesa`), descrito logo depois.

Caminhos: `B/` = `backend/processo_seletivo/`, `T/` = `backend/tests/`.

---

## Requisitos funcionais

| Requisito | Onde vive | Onde é cobrado |
|---|---|---|
| **FR-700** — a quinta forma: o código em todos os Perfis | `DocumentoExigido.modalidade_codigo`; `modalityCode` no conteúdo publicado; `recorte_de` em `B/editais/domain/documentos.py` | `T/unit/inscricoes/test_aplicabilidade.py::test_o_recorte_se_le_por_presenca_de_campo`; `T/contract/test_elevacao_degrau_17.py`; **navegador** — gravado pela composição e publicado com `modalityCode: "PPP"` |
| **FR-701** — aplica-se quando a modalidade escolhida, no Perfil da inscrição, tem o código | `aplicabilidade`, `_se_aplica` | `test_o_recorte_por_codigo_vale_em_todo_perfil_que_tem_o_codigo`, `test_o_codigo_e_lido_no_perfil_da_inscricao_e_nao_em_outro` |
| **FR-702** — exclusivo com Perfil e Modalidade exata | `_validate_recorte_por_codigo`; `_recorte_por_codigo` na publicação; `ck_documento_recorte_exclusivo` | `T/unit/editais/test_documentos_recusas.py::test_codigo_junto_de_perfil_ou_modalidade_exata_e_recusado`; `T/unit/editais/test_validacao_inscricao.py::test_codigo_com_perfil_ou_modalidade_exata_e_impeditivo`; `T/interface/test_compor_inscricao.py::test_perfil_com_codigo_e_recusado_preservando_o_digitado` |
| **FR-703** — código que nenhum Perfil tem | idem | `test_codigo_que_nenhum_perfil_tem_e_recusado`; `test_codigo_que_nenhum_perfil_tem_e_impeditivo` |
| **FR-704** — o código da ampla é proibido, em qualquer Perfil | idem; opções sem a ampla em `modalidades_em_todos_os_perfis` e `_codigos_em_todos_os_perfis` | `test_codigo_da_ampla_e_recusado`; `test_codigo_da_ampla_em_um_perfil_so_e_impeditivo`; `test_declarar_ampla_a_modalidade_do_codigo_na_etapa_perfis_e_recusado`; `T/integration/publicacoes/test_retificar_recorte_transversal.py::test_declarar_ampla_a_modalidade_do_codigo_e_impedido`; `test_o_seletor_oferece_o_codigo_antes_dos_pares_e_sem_a_ampla`; **navegador** — o seletor não ofereceu AC |
| **FR-705** — uma regra só | `aplicabilidade` e `aplicaveis(conteudo, …)`; os seis chamadores trocados | `T/unit/inscricoes/test_aplicabilidade.py` inteiro; famílias do rascunho, do portal e do envio verdes sem mudança de expectativa |
| **FR-706** — IMPEDE de denominação, nomeando código, denominações e Perfis | `_denominacoes_do_codigo` em `B/editais/domain/validation.py` | `test_denominacoes_diferentes_para_o_codigo_referido_dao_um_achado_so`; `test_renomear_a_modalidade_num_perfil_so_e_impedido`; **navegador** — um IMPEDE na Revisão, com "'Pessoas negras e indígenas' em TEC-LAB; 'Pessoas pretas, pardas e indígenas' em DOC-INFO" e "Ir para Perfis de Vaga" |
| **FR-707** — só a denominação | idem | `test_percentual_diferente_nao_e_acusado` |
| **FR-708** — a mensagem da #161 com a terceira saída | `_recorte_que_o_documento_publicado_alarga` | `test_a_mensagem_da_161_oferece_as_tres_saidas` |
| **FR-709** — o cartão de todo Perfil com o código anuncia o documento | `_documentos_anunciados` via `aplicaveis` | `T/integration/inscricoes/test_recorte_transversal.py::test_o_cartao_dos_dois_perfis_anuncia_o_documento_da_ppp`; **navegador** — os dois cartões dizem "Se concorrer em Pessoas pretas, pardas e indígenas, também: Autodeclaração étnico-racial" |
| **FR-710** — o rascunho lista o transversal, e a troca de modalidade atualiza | `requisitos_da_inscricao`, `descartes_por_mudanca_de_modalidade` | `test_trocar_de_ppp_para_ampla_descarta_a_autodeclaracao`; **navegador** — escolher PPP no Perfil técnico passou a lista de 1 para 2 obrigatórios |
| **FR-711** — o envio é recusado no servidor | `pendencias_para_enviar` via a regra única | `test_a_ppp_do_perfil_tecnico_nao_envia_sem_a_autodeclaracao`; **navegador** — "Falta enviar: Autodeclaração étnico-racial.", sem botão de envio |
| **FR-712** — um grupo por código no documento publicado | `_documentos_exigidos` e `_titulo_do_grupo` em `B/publicacoes/infrastructure/pdf.py`; `_alcance` em `B/interface/revisao.py` | `T/unit/publicacoes/test_pdf_documentos_exigidos.py::test_documentos_do_mesmo_codigo_saem_num_grupo_so_sem_perfil`, `…_o_grupo_exato_continua_como_estava_ao_lado_do_transversal`; **navegador** — o PDF publicado traz "Dos candidatos concorrentes na modalidade Pessoas pretas, pardas e indígenas:" |
| **FR-713** — "(facultativo)" dentro do grupo | idem | `test_documentos_do_mesmo_codigo_saem_num_grupo_so_sem_perfil` |
| **FR-714** — a lista gravada no envio, da versão aceita, com situação e razão | `gravar_lista_exigida`; chamada em `enviar_inscricao`; gatilho `item_da_lista_exigida_coerente` | `T/integration/inscricoes/test_lista_exigida.py::test_o_envio_grava_um_item_por_documento_inclusive_o_que_nao_se_aplica`, `test_a_lista_e_da_versao_e_do_instante_do_envio`; `T/integration/inscricoes/test_lista_exigida_concorrencia.py`; **navegador** — a inscrição enviada tem as três linhas; **percurso da Mesa** — dois envios pelo portal gravaram três itens cada, inclusive o que não se aplica, com a versão aceita e o instante do envio |
| **FR-715** — imutável, nas duas camadas | `TABELAS_APPEND_ONLY`; gatilho `item_da_lista_exigida_append_only`; guardas do modelo | `T/integration/inscricoes/test_lista_exigida_imutavel.py`; `T/integration/test_database_permissions.py` (parametrizado); `provisionar_papeis` — **34 de 34**; **percurso da Mesa** — no banco do percurso, `UPDATE` pelo papel de execução dá *permission denied*, e pelo superusuário, *required document lists are append-only* |
| **FR-716** — o reenvio não duplica | idempotência do envio; `uq_item_da_lista_por_requisito` | `test_o_reenvio_com_a_mesma_chave_nao_grava_de_novo` |
| **FR-717** — "não se aplica" registrado | idem FR-714 | `test_o_envio_grava_um_item_por_documento_inclusive_o_que_nao_se_aplica` |
| **FR-718** — a Mesa lê a lista, três estados, razão | `inscricao_para_avaliar` em `B/avaliacoes/application/mesa.py`; `mesa_inscricao.html` | `T/interface/test_mesa_lista_exigida.py`; **percurso da Mesa** — as duas inscrições, cada documento com a obrigatoriedade e a razão, e "Não se aplicam a esta inscrição" abaixo |
| **FR-719** — a consulta lê a lista | `_linhas` e `inscricao_para_consulta` em `B/inscricoes/application/consulta.py`; `inscricao_detalhe.html` | `test_quem_le_mostra_a_lista_gravada_e_nao_a_regra_de_hoje`; `T/integration/interface/test_inscricoes_recebidas.py::test_o_detalhe_da_enviada_mostra_a_razao_e_o_que_nao_se_aplica`; `test_inscricoes_em_escala.py` (consultas iguais para 5 e 300); **navegador** — o detalhe do Gestor com a razão e "Não se aplicam a esta inscrição"; **percurso da Mesa** — a lista conta "2 de 2" nas duas inscrições |
| **FR-720** — a inscrição enviada no portal lê a lista; o comprovante não muda | `_requisitos_pedidos` em `B/portal/views.py` | `test_quem_le_mostra_a_lista_gravada_e_nao_a_regra_de_hoje` — desde `6892ea6`, que corrigiu o portal para ler da lista também a obrigatoriedade, o teste confere a obrigatoriedade e o total do portal; antes comparava só ids, que a regra também daria, e não discriminava; `T/integration/portal/test_comprovante_preservado.py` verde sem mudança |
| **FR-721** — retificável; o resumo público nomeia o campo | `CONTRATO` em `B/editais/domain/mutabilidade.py`; `CAMPOS` em `B/publicacoes/domain/alteracoes.py` | `T/contract/test_mutabilidade.py`; `T/unit/publicacoes/test_alteracoes_legiveis.py::test_o_recorte_transversal_vira_linha_com_o_campo_e_sem_valor` |
| **FR-722** — o campo na Retificação, e a troca no mesmo ato | `CAMPOS_DOCUMENTO`, `opcoes_de_aplicabilidade` em `B/interface/retificacao.py` | `T/interface/test_campos_vem_do_contrato.py` (84 com tela); `test_a_tela_oferece_o_codigo_com_o_alcance_e_sem_a_ampla`; `test_trocar_de_exato_para_transversal_no_mesmo_ato_publica`; `test_codigo_fabricado_e_recusado_pela_tela` |
| **FR-723** — a Retificação não altera a lista enviada | a tabela append-only | `test_uma_retificacao_entre_dois_envios_deixa_cada_um_com_o_seu` |
| **FR-724** — tirar o código de todos os Perfis é impedido; de alguns, não | `_validate_recorte_por_codigo`; `_recorte_por_codigo` | `test_remover_o_codigo_de_todos_os_perfis_e_recusado_nomeando_o_documento`; `test_remover_o_codigo_de_alguns_perfis_grava`; `test_codigo_que_nenhum_perfil_tem_e_impeditivo` |
| **FR-725** — nada publicado é regenerado | a elevação só no fluxo de Retificação | `T/contract/test_elevacao_degrau_17.py::test_elevar_nao_toca_o_literal_e_e_idempotente`; `T/integration/publicacoes/test_elevacao_de_versao.py` (o acervo atravessa sem mudar conteúdo nem resumo) |
| **FR-726** — a inscrição antiga é reconstruída, e a Mesa e a consulta dizem | `lista_exigida` com `reconstruida`; os dois templates | `test_inscricao_sem_lista_gravada_e_reconstruida_e_diz_que_foi`; `test_sem_lista_gravada_a_mesa_reconstroi_e_avisa_uma_vez` |
| **FR-727** — a divergência da #161, na reconstruída e na gravada | `perfis_que_o_documento_publicado_alcanca`; `divergente_do_publicado`; `razao_legivel` | `T/unit/inscricoes/test_aplicabilidade.py::test_a_divergencia_da_161_marca_quem_concorre_na_mesma_denominacao_em_outro_perfil`, `test_a_divergencia_nao_marca_quem_nao_concorre_na_denominacao`, `test_a_razao_da_divergencia_diz_o_que_o_edital_publicado_exigia`; `test_a_divergencia_da_161_aparece_na_lista_reconstruida`; `test_a_divergencia_gravada_aparece_sem_aviso_de_reconstrucao` |
| **FR-728** — quem lê é quem já lia | nenhuma rota nova | `test_quem_nao_recebeu_a_inscricao_nao_ve_a_lista`; **percurso da Mesa** — a presidente, a quem a inscrição não foi distribuída, recebe 404 na Mesa dela |
| **FR-729** — sem evento próprio de auditoria | a gravação dentro do ato `SUBMETER` | `test_o_envio_tem_um_evento_so_e_a_auditoria_nao_repete_a_lista` |

## Interface

| Requisito | Onde vive | Onde é cobrado |
|---|---|---|
| **UX-080** — a opção diz o alcance; rótulos fixos | `_documento.html` (dois `optgroup`); `_codigos_em_todos_os_perfis` | `test_o_seletor_oferece_o_codigo_antes_dos_pares_e_sem_a_ampla`; `test_a_tela_oferece_o_codigo_com_o_alcance_e_sem_a_ampla`; **navegador** — "Pessoas pretas, pardas e indígenas (PPP) — em todos os Perfis que a têm (2 de 2)" |
| **UX-081** — a razão em frase, pela denominação | `razao_legivel` | `test_a_razao_se_le_como_frase_pela_denominacao`; `test_a_razao_do_perfil_nomeia_o_perfil` |
| **UX-082** — "não se aplica" depois, sem depender só de cor | título e lista próprios em `mesa_inscricao.html` e `inscricao_detalhe.html` | `test_a_mesa_mostra_os_tres_estados_com_a_razao` (ordem no documento); **navegador** — seção própria, título e texto "Não se aplica:"; **percurso da Mesa** — na Mesa, abaixo dos pedidos, com borda tracejada e o texto "Não se aplica:" |
| **UX-083** — a lista reconstruída se anuncia uma vez | `aviso-da-lista` nos dois templates | `test_sem_lista_gravada_a_mesa_reconstroi_e_avisa_uma_vez` (`count == 1`) |

## Critérios de sucesso

| Critério | Como foi verificado |
|---|---|
| **SC-260** — 7 linhas contra 112 no 140/2025 | **Não recomposto no navegador.** Os sete documentos condicionados à modalidade cabem em sete linhas por construção: cada um recorta por um código, e o código vale nos 16 Perfis (`FR-701`). O cenário C do quickstart fica como roteiro |
| **SC-261** — 4 obrigatórios nos grupos, 3 no grupo de PPIQ, 2 no de todos | Pelo mesmo motivo, **não recomposto**. O agrupamento que o sustenta está provado em `test_documentos_do_mesmo_codigo_saem_num_grupo_so_sem_perfil` |
| **SC-262** — as superfícies dizem o mesmo; nenhum envio sem o documento | **navegador**, com a PPP no lugar do PcD: PDF, os dois cartões, a inscrição no Perfil técnico (recusada, depois enviada) e o detalhe do Gestor. A Mesa foi percorrida depois, em 26/09 (*O percurso da Mesa*): a autodeclaração pedida no Perfil técnico em PPP, e "não se aplica" no docente em AC, com a razão nas duas. `T/integration/inscricoes/test_recorte_transversal.py` cobre o envio nos dois Perfis |
| **SC-263** — todo documento da versão aceita aparece, com estado e razão | `test_o_envio_grava_um_item_por_documento_inclusive_o_que_nao_se_aplica`; `test_a_mesa_mostra_os_tres_estados_com_a_razao`; **navegador** — o diploma aparece como "Não se aplica: pedido de quem concorre ao Perfil DOC-INFO"; **percurso da Mesa** — os três documentos nas duas inscrições, nenhum sumido |
| **SC-264** — zero diferenças depois de uma Retificação | `test_uma_retificacao_entre_dois_envios_deixa_cada_um_com_o_seu`; `test_quem_le_mostra_a_lista_gravada_e_nao_a_regra_de_hoje` (o que discrimina) |
| **SC-265** — a inscrição antiga mostra a divergência; o publicado não muda | `test_a_divergencia_da_161_aparece_na_lista_reconstruida`; `test_elevar_nao_toca_o_literal_e_e_idempotente`; `test_elevacao_de_versao.py`. O banco do estudo, com o 903 original, não foi aberto nesta sessão |
| **SC-266** — exatamente um IMPEDE com um Perfil renomeado; zero com todos | `test_denominacoes_diferentes_para_o_codigo_referido_dao_um_achado_so`; `test_renomear_nos_dois_perfis_passa`; **navegador** — um IMPEDE na Revisão, zero depois de restaurar |
| **SC-267** — as três operações no "O que mudou" | `test_o_recorte_transversal_vira_linha_com_o_campo_e_sem_valor` (as três chegam como `REPLACE` e se leem igual) |
| **SC-268** — de ponta a ponta pelos canais dos atores | **navegador**: compor (etapa Documentos), revisar, submeter, homologar e publicar pela gestão; inscrever e enviar pelo portal; conferir pela consulta do Gestor. Perfis e cronograma entraram pela API de rascunho, canal de quem elabora, porque a feature não os muda. Analisar pela Mesa, no *percurso da Mesa*: distribuir pela presidência e abrir cada inscrição como o analista |

## Casos-limite

| Caso | Onde é cobrado |
|---|---|
| Código presente em só alguns Perfis | `test_codigo_presente_num_perfil_so_equivale_ao_recorte_exato` (vale onde há, não se aplica onde não há) |
| Código presente num Perfil só | idem |
| Código que nenhum Perfil tem | `test_codigo_que_nenhum_perfil_tem_e_recusado`; `…_e_impeditivo` |
| Perfil acrescentado depois | `test_perfil_acrescentado_depois_com_o_codigo_recebe_o_documento_sem_linha_nova` |
| "Partir de um Edital anterior" | `T/unit/editais/test_reaproveitamento.py::test_o_recorte_transversal_atravessa_o_remapeamento_sem_mudar` |
| Mesmo código, denominações diferentes, sem documento transversal | `test_codigo_repetido_sem_documento_transversal_nao_e_acusado` |
| Denominação que difere em maiúscula ou acento | `test_a_denominacao_se_compara_como_esta_escrita` |
| Recorte transversal com Perfil ou Modalidade exata | `test_codigo_junto_de_perfil_ou_modalidade_exata_e_recusado` |
| Documento transversal facultativo | `test_documentos_do_mesmo_codigo_saem_num_grupo_so_sem_perfil` |
| Candidato sem modalidade | `test_o_recorte_por_codigo_vale_em_todo_perfil_que_tem_o_codigo` (caso `None`) |
| Ampla em um Perfil e não em outro | `test_codigo_da_ampla_em_um_perfil_so_e_impeditivo` |
| Duas Retificações com envios entre elas | `test_uma_retificacao_entre_dois_envios_deixa_cada_um_com_o_seu` (uma Retificação entre dois envios; a segunda repetiria o mesmo mecanismo) |
| Envio concorrente com a Retificação | `T/integration/inscricoes/test_lista_exigida_concorrencia.py` (três execuções seguidas verdes) |
| Reenvio do mesmo envio | `test_o_reenvio_com_a_mesma_chave_nao_grava_de_novo` |
| Inscrição anterior sob recorte que hoje seria recusado | `test_a_divergencia_da_161_aparece_na_lista_reconstruida` — a Mesa nomeia, e não decide |

## O percurso pelo navegador

Banco `ps044`, preparado com `make preparar` e papéis próprios (`ps044_owner`, `ps044_runtime`);
servidor na porta 8045 (entrada `recorte-044` do `launch.json`).

1. Processo e rascunho pela API de rascunho: DOC-INFO e TEC-LAB, cada um com AC (ampla) e PPP; a
   autodeclaração restrita à PPP do DOC-INFO.
2. Composição, etapa Inscrição: o seletor ofereceu "Pessoas pretas, pardas e indígenas (PPP) — em
   todos os Perfis que a têm (2 de 2)" antes dos pares, e nenhuma opção para AC. Escolhida, com
   Perfil "Todos": gravou `modalidade_codigo = 'PPP'`.
3. Revisão: nenhum IMPEDE; o bloco do documento diz "candidatos concorrentes na modalidade Pessoas
   pretas, pardas e indígenas, em todos os Perfis".
4. Etapa Perfis: a PPP do TEC-LAB renomeada → **um** IMPEDE na Revisão, com as duas denominações e
   o caminho para Perfis. Restaurada → zero.
5. Submeter, homologar e publicar, cada ato com a sua identidade.
6. PDF publicado: "Dos candidatos concorrentes na modalidade Pessoas pretas, pardas e indígenas: a)
   Autodeclaração étnico-racial".
7. Portal: os dois cartões anunciam a autodeclaração para a PPP.
8. Inscrição no TEC-LAB como PPP: 2 obrigatórios; só com a identidade, a Revisão recusa ("Falta
   enviar: Autodeclaração étnico-racial."); com os dois, envia — `INS-2026-2Y33TCWU`, com a lista
   gravada: identidade e autodeclaração obrigatórias, diploma "não se aplica".
9. Consulta do Gestor: cada documento com a razão; "Não se aplicam a esta inscrição — Diploma de
   graduação — Não se aplica: pedido de quem concorre ao Perfil DOC-INFO".

## O percurso da Mesa

O primeiro percurso parou antes da Mesa, que exige o período de inscrição encerrado — e não há
cadastro retroativo de Edital. O término do período tem **hora e minuto**, e por isso este percurso
publicou um Edital com as inscrições encerrando 35 minutos depois, enviou as inscrições nesse
intervalo e esperou. Nenhum relógio foi deslocado.

Banco `ps044mesa`, preparado com `make preparar` e papéis próprios (`ps044mesa_owner`,
`ps044mesa_runtime`); servidor na porta 8046, conectado pelo papel de execução, com o código da
`main` depois do #173.

1. Processo, rascunho, submissão, homologação e publicação pela API administrativa: o rascunho de
   `rascunho_com_ppp_nos_dois_perfis` (DOC-INFO e TEC-LAB, cada um com AC declarada ampla e PPP; a
   identidade de todos, o diploma do DOC-INFO, a autodeclaração pedida de quem concorre em PPP em
   todos os Perfis), com a Etapa "Análise documental", decisória, de uma avaliação por inscrição.
   Comissão (presidente e um membro) e alocação do membro na Etapa pelos commands.
2. Portal, Perfil técnico: escolhida a PPP, a lista passou a pedir 2 de 2 obrigatórios; com os dois
   anexos, enviada — `INS-2026-SSUEVQT8`.
3. Portal, Perfil docente: escolhida a AC, a lista pediu identidade e diploma, e não a
   autodeclaração; enviada — `INS-2026-P6GSF5BM`.
4. A lista gravada dos dois envios, lida no banco: três itens em cada, com a versão aceita e o
   instante do envio; a autodeclaração `OBRIGATORIO` na PPP do Perfil técnico e `NAO_SE_APLICA` na
   AC do docente, as duas com a forma `MODALIDADE_EM_TODOS_OS_PERFIS`.
5. Consulta do Gestor: "2 de 2" nas duas; no detalhe, a razão de cada documento e "Não se aplicam a
   esta inscrição".
6. Distribuição, antes do término: recusada — "As inscrições ficam abertas até 26/09/2026 às
   07:13". Depois dele, a presidente propôs e confirmou as duas para o membro.
7. Mesa, como o membro:

   | Inscrição | Identidade | Autodeclaração étnico-racial | Diploma de graduação |
   |---|---|---|---|
   | PPP no Perfil técnico | obrigatório, "pedido de todos os candidatos" | obrigatório, "pedido de quem concorre em Pessoas pretas, pardas e indígenas, em todos os Perfis" | "Não se aplica: pedido de quem concorre ao Perfil DOC-INFO" |
   | AC no Perfil docente | obrigatório, "pedido de todos os candidatos" | "Não se aplica: pedido de quem concorre em Pessoas pretas, pardas e indígenas, em todos os Perfis" | obrigatório, "pedido de quem concorre ao Perfil DOC-INFO" |

   Nenhum aviso de lista reconstruída; nenhum erro no console. A presidente, sem a inscrição
   distribuída, recebe 404 na Mesa dela.

A Mesa avisa que a avaliação é registrada "fora do período previsto para a Etapa" porque a Etapa do
cenário aponta o evento de inscrição. É do cenário, e não da feature.

**Continua sem percurso**: o 140/2025 recomposto (`SC-260`, `SC-261`, T065) e a inscrição do 903
original, anterior à feature (`SC-265`).
