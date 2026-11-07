# Rastreabilidade: A inaplicabilidade documental tem fundamento publicado (131)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`. Abreviações:

- `ic` = `integration/convocacao/test_inaplicabilidade.py` — a conferência, o aceite com ciência, a
  transição e as telas (página, condução, POST do desfecho)
- `ue` = `unit/editais/test_condicao_de_exigencia.py` — a condição na composição, na publicação, no
  PDF e no reaproveitamento
- `fc` = `unit/formalizacao/test_conjunto.py` — a situação na formalização
- `ob` = `unit/portal/test_obrigacoes_da_convocacao.py` — o texto do portal
- `dc` = `integration/convocacao/test_documentos_da_convocacao.py` — os testes da `115`, um revisto

A faixa abre em **FR-4451**, **SC-1371** e **UX-301**, e as três foram gastas. Onde um requisito
**não** tem teste próprio, a linha diz.

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-4451 — a condição no obrigatório da convocação | T005, T006, T010 | `ue::test_o_obrigatorio_da_convocacao_admite_condicao`; `ic::test_a_condicao_se_le_da_versao_da_lista` (do rascunho ao publicado, pela composição do cenário) |
| FR-4452 — texto, aparado, vazio é ausência | T009, T012 | `ue::test_a_condicao_e_o_campo_aparado_e_o_vazio_e_ausencia` |
| FR-4453 — recusada no facultativo e na inscrição, no rascunho e na publicação | T009 | `ue::test_a_condicao_fora_do_lugar_e_recusada_no_rascunho`, `ue::test_a_publicacao_impede_a_condicao_no_facultativo`, `ue::test_a_publicacao_aceita_a_condicao_no_obrigatorio_da_convocacao` |
| FR-4454 — o mesmo texto nas superfícies; PDF igual sem condição | T011, T018, T028 | `ue::test_o_pdf_escreve_a_condicao_depois_do_nome`, `ue::test_o_documento_sem_condicao_sai_no_pdf_como_antes`; `ic::test_a_pagina_so_oferece_o_nao_se_aplica_no_condicional`; `unit/interface/test_revisao.py::test_o_que_a_conferencia_diz_ler_aparece_na_tela`; `unit/publicacoes/test_pdf_grafia.py::test_todo_texto_impresso_passa_pela_validacao` |
| FR-4455 — campo como os demais; reaproveitamento; degrau 19 | T006, T007, T008 | `ue::test_o_reaproveitamento_leva_a_condicao`; `integration/publicacoes/test_elevacao_de_versao.py::test_a_032_nao_acrescenta_degrau_de_elevacao`; `contract/test_mutabilidade.py`, `contract/test_forma_publicada.py` |
| FR-4456 — retificável; a lista lê a versão em que nasceu | T007 | `interface/test_campos_vem_do_contrato.py::test_a_conta_fecha_com_a_matriz`; `ic::test_a_condicao_se_le_da_versao_da_lista` |
| FR-4457 — "não se aplica" só no condicional | T017, T018 | `ic::test_incondicional_nao_se_afasta`, `ic::test_a_pagina_so_oferece_o_nao_se_aplica_no_condicional`; `dc::test_nao_se_aplica_sem_apresentacao_com_motivo` (revisto) |
| FR-4458 — motivo com palavra, também no pendente | T017 | `ic::test_motivo_sem_palavra_e_recusado`, `ic::test_nao_se_aplica_sem_motivo_e_recusado` |
| FR-4459 — fundamento é condição + motivo, sem cópia | T018, T026 | `ic::test_a_conducao_separa_as_contagens_e_mostra_o_bloco`, `ic::test_a_pagina_so_oferece_o_nao_se_aplica_no_condicional` |
| FR-4460 — com arquivo, abre antes | T017 | `ic::test_com_arquivo_o_nao_se_aplica_pede_a_abertura_e_depois_tranca` |
| FR-4461 — autoria e instante, sem campo novo | T017 | `ic::test_o_alocado_registra_o_nao_se_aplica_no_condicional` |
| FR-4462 — substituição com "não se aplica" pede motivo | T017 | `ic::test_trocar_para_nao_se_aplica_sem_arquivo_pede_motivo`, `ic::test_sair_do_nao_se_aplica_tambem_pede_motivo`, `ic::test_a_pendencia_sem_arquivo_continua_sem_motivo_de_revisao` |
| FR-4463 — nova versão recusada depois do "não se aplica" | T017 | `ic::test_com_arquivo_o_nao_se_aplica_pede_a_abertura_e_depois_tranca` |
| FR-4464 — fora do recorte é inexistente no comando | T016 | `ic::test_item_fora_do_recorte_nao_se_confere` (a abertura: sem teste próprio, porque não há apresentação nesse item) |
| FR-4465 — o predicado único, alocado incluído | T017 | `ic::test_o_alocado_registra_o_nao_se_aplica_no_condicional` |
| FR-4466 — contagens separadas, selo próprio | T023, T026 | `ic::test_a_leitura_separa_conformes_e_nao_se_aplica`, `ic::test_a_conducao_separa_as_contagens_e_mostra_o_bloco` |
| FR-4467 — o bloco na confirmação | T026 | `ic::test_a_conducao_separa_as_contagens_e_mostra_o_bloco` |
| FR-4468 — a ciência, assinada e conferida sob a trava | T025, T026 | `ic::test_aceite_sem_ciencia`, `ic::test_aceite_com_ciencia_superada`, `ic::test_aceite_com_ciencia`, `ic::test_o_post_do_desfecho_leva_a_ciencia`, `ic::test_sem_inaplicabilidade_o_aceite_e_o_de_antes` |
| FR-4469 — a trilha do desfecho cita os `id`, sem motivo | T025 | `ic::test_aceite_com_ciencia` |
| FR-4470 — o "não se aplica" atende só no condicional | T024 | `ic::test_p1_chamada_aberta_o_antigo_nao_atende`, `ic::test_tres_incondicionais_afastados_nao_chegam_ao_aceite` |
| FR-4471 — no mesmo ato, sem papel novo | T025 | `ic::test_aceite_com_ciencia`; `interface/test_permissoes_dos_documentos_da_convocacao.py::test_o_membro_alocado_confere_e_nao_desfecha` (regressão da `115`) |
| FR-4472 — origem derivável sem campo novo | T023, T027 | `fc::test_a_conferencia_nao_se_aplica_e_situacao_nao_se_aplica`, `ic::test_p1_chamada_decidida_continua` |
| FR-4473 — formalização distingue as origens, sem motivo | T027 | `fc::test_a_conferencia_nao_se_aplica_e_situacao_nao_se_aplica` (revisto), `fc::test_nao_se_aplica_e_nao_apresentado_deixam_a_pessoa_completa` |
| FR-4474 — o auditor vê a contagem, e só | T026 | **sem teste próprio**: a contagem é a mesma linha da condução que o auditor lê (FR-3598 da `115`) |
| FR-4475 — a condição no portal | T028 | `ob::test_condicional_a_apresentar_orienta_e_nao_manda_enviar`, `ob::test_condicional_fechada_a_chamada_vale_o_texto_de_antes`, `ob::test_incondicional_a_apresentar_continua_falta_enviar` |
| FR-4476 — nada reescrito | T021 | `ic::test_p1_chamada_aberta_o_antigo_nao_atende` (o registro continua), `ic::test_p1_chamada_decidida_continua` |
| FR-4477 — versões antigas sem condição; nada inferido | T012 | `ue::test_a_versao_sem_o_campo_e_incondicional_e_nada_se_infere_da_instrucao` |
| FR-4478 — a marca do registrado sem condição | T029 | `ic::test_p1_chamada_aberta_o_antigo_nao_atende`, `ic::test_p1_chamada_decidida_continua` |

## Requisitos de experiência

| Requisito | Tarefa | Teste |
|---|---|---|
| UX-301 — selo e contagens | T018, T026 | `ic::test_a_conducao_separa_as_contagens_e_mostra_o_bloco`; jornada em `verificacao.md` |
| UX-302 — o texto da condição e do motivo | T010, T018 | `ic::test_a_pagina_so_oferece_o_nao_se_aplica_no_condicional`, `ue::test_o_pdf_escreve_a_condicao_depois_do_nome` |
| UX-303 — o bloco da confirmação | T026 | `ic::test_a_conducao_separa_as_contagens_e_mostra_o_bloco` |
| UX-304 — o portal no condicional | T028 | `ob::test_condicional_a_apresentar_orienta_e_nao_manda_enviar` |

## Critérios de sucesso

| Critério | Tarefa | Verificação |
|---|---|---|
| SC-1371 — nenhum aceite com incondicional afastado | T015, T021 | `ic::test_incondicional_nao_se_afasta`, `ic::test_tres_incondicionais_afastados_nao_chegam_ao_aceite`, `ic::test_p1_chamada_aberta_o_antigo_nao_atende` |
| SC-1372 — o bloco e a ciência | T021, T022 | `ic::test_aceite_sem_ciencia`, `::test_aceite_com_ciencia_superada`, `::test_o_post_do_desfecho_leva_a_ciencia`; jornada |
| SC-1373 — zero conferências fora do recorte | T015 | `ic::test_item_fora_do_recorte_nao_se_confere` |
| SC-1374 — as duas origens na formalização | T027 | `fc::test_a_conferencia_nao_se_aplica_e_situacao_nao_se_aplica` |
| SC-1375 — o mesmo texto nas superfícies | T011, T018, T028 | PDF, página dos documentos, revisão e portal por teste; a página pública do Edital usa a mesma função do PDF (`nome_com_a_condicao`), **sem teste próprio** |
| SC-1376 — nada anterior muda | T021, T032 | suíte completa, com as tabelas append-only; `ic::test_p1_chamada_decidida_continua` |
| SC-1377 — consultas constantes | T031 | **sem teste próprio de orçamento**: a condição sai do conteúdo que a leitura já traz, e os orçamentos existentes da condução passaram. O bloco do aceite chama `nome_de_pessoa` por inaplicabilidade, como a página dos documentos já faz |
| SC-1378 — o conferente entende sem ajuda | T033 | **humana, pendente** |

## Casos-limite

| Caso | Teste |
|---|---|
| Condição preenchida com espaços | `ue::test_a_condicao_e_o_campo_aparado_e_o_vazio_e_ausencia` |
| Condição em documento que aproveita o da inscrição | **sem teste próprio**: a regra de abertura é a mesma do *conforme*, que a `115` prova para a referência |
| Condição em documento com recorte por modalidade | **sem teste próprio**: a regra lê só a condição, e não o recorte |
| Facultativo apresentado e sem sentido | **sem teste próprio**: o facultativo recebe `nao_se_aplica_sem_condicao` pela mesma regra do incondicional |
| "Não se aplica" depois do vencimento | **sem teste próprio**: a conferência depois do vencimento é a da `115` (`dc::test_a_conferencia_continua_depois_do_vencimento`) |
| Duas pessoas ao mesmo tempo | `ic::test_aceite_com_ciencia_superada` |
| Correção da convocação pela `120` | `ic::test_a_correcao_herda_condicao_e_conferencia` |
| Nova chamada da mesma inscrição | **sem teste próprio**: a conferência não viaja (a `115` prova em `test_aproveitamento_entre_chamadas.py`), e a condição se lê da versão do item |
| Retificação que muda ou retira a condição | `ic::test_a_condicao_se_le_da_versao_da_lista`; a Retificação real não foi exercitada |
| Edital reaproveitado; Perfil duplicado | `ue::test_o_reaproveitamento_leva_a_condicao` (a duplicação não copia documento) |
| Regularização | **sem teste próprio**: a guarda é a mesma função do aceite (`DESFECHOS_QUE_INCLUEM`) |
| Desfecho que não inclui | `ic::test_indeferimento_sem_ciencia` |
| Convocação sem lista | a guarda da FR-4401 da `115` vem antes, sem teste novo |

## As decisões do usuário

| Decisão | Requisitos |
|---|---|
| 1ª — as quatro figuras | FR-4457, FR-4464, D-003 |
| 2ª — sem dispensa | D-003; nenhum requisito cria a operação |
| 3ª — sem motor, papel ou fluxo | FR-4452, FR-4465, FR-4471 |
| 4ª — a inaplicabilidade legítima se preserva | FR-4451, FR-4457 |
| 5ª — o arquivo, sozinho, não decide | FR-4460 |
| 6ª — `"."` não é fundamento | FR-4458, FR-4459 |
| 7ª — quem desfecha vê | FR-4466, FR-4467, FR-4468 |
| 8ª — nada se reinterpreta | FR-4476, FR-4477, FR-4478 |
| 9ª — o domínio recusa o fora do recorte | FR-4464 |
| 10ª — o desenho mínimo aprovado | FR-4451 a FR-4478 |
| 11ª — o antigo incondicional não atende | FR-4470, FR-4478 |
| 12ª — a dispensa sem pendência própria; a P-3 pendente | D-003; FR-4473 |
