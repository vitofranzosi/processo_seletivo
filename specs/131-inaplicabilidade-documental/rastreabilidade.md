# Rastreabilidade: A inaplicabilidade documental tem fundamento publicado (131)

Cada requisito → a tarefa que o implementa → o teste que o verifica. **Nenhum teste existe ainda**:
a spec não foi implementada, e os nomes abaixo são os previstos. Caminhos relativos a
`backend/tests/`. Abreviações, as de [contracts/cenarios.md](contracts/cenarios.md):

- `ic` = `integration/convocacao/test_inaplicabilidade.py`
- `dd` = `unit/convocacao/test_documentos_dominio.py`
- `ia` = `interface/test_aceite_com_inaplicabilidade.py`
- `fc` = `unit/formalizacao/test_conjunto.py`
- `cp` = `integration/editais/test_condicao_de_exigencia.py`
- `ob` = `unit/portal/test_obrigacoes_da_convocacao.py`

A faixa abre em **FR-4451**, **SC-1371** e **UX-301**, e as três foram gastas.

## Requisitos funcionais

| Requisito | Tarefa | Teste previsto |
|---|---|---|
| FR-4451 — a condição no obrigatório da convocação | T005, T006, T010 | `cp::test_a_condicao_vai_do_rascunho_a_publicacao` |
| FR-4452 — texto declarativo, aparado, vazio é ausência | T009, T012 | `unit/editais::test_condicao_aparada_e_vazia` |
| FR-4453 — impede no facultativo e na inscrição | T009, T010 | `cp::test_condicao_em_facultativo_impede`, `::test_condicao_na_inscricao_impede` |
| FR-4454 — o mesmo texto nas cinco superfícies; PDF byte a byte sem condição | T011, T018, T028 | `cp::test_a_condicao_nas_superficies`, `contract/test_documento_publicado.py` |
| FR-4455 — campo como os demais; reaproveitamento; degrau | T006, T007, T008 | `cp::test_o_reaproveitamento_leva_a_condicao`, `integration/publicacoes/test_elevacao_de_versao.py` |
| FR-4456 — retificável; alcança as chamadas seguintes | T007 | `cp::test_a_retificacao_da_condicao_nao_alcanca_a_chamada_aberta` |
| FR-4457 — *"não se aplica"* só no condicional | T017, T018 | `ic::test_incondicional_nao_se_afasta`, `ia::test_a_opcao_so_no_condicional` |
| FR-4458 — motivo com conteúdo, no *pendente* também | T017 | `dd::test_motivo_tem_conteudo`, `ic::test_motivo_ponto_e_recusado` |
| FR-4459 — fundamento é condição + motivo, sem cópia | T018, T026 | `ia::test_a_pagina_mostra_condicao_e_motivo` |
| FR-4460 — com arquivo, abre antes | T017 | `ic::test_nao_se_aplica_com_arquivo_exige_abertura` |
| FR-4461 — autoria e instante, sem campo novo | T017 | `ic::test_a_conferencia_nao_ganha_campo` |
| FR-4462 — substituição com *"não se aplica"* pede motivo | T017 | `ic::test_trocar_para_nao_se_aplica_sem_arquivo_pede_motivo` |
| FR-4463 — nova versão recusada depois do *"não se aplica"* | T017 | `ic::test_depois_do_nao_se_aplica_o_envio_e_recusado` |
| FR-4464 — fora do recorte é inexistente no comando | T016 | `ic::test_item_fora_do_recorte_nao_se_confere` |
| FR-4465 — o predicado único, alocado incluído | T017 | `ic::test_o_alocado_registra_no_condicional` |
| FR-4466 — contagens separadas, selo próprio | T023, T026 | `ia::test_a_conducao_separa_as_contagens` |
| FR-4467 — o bloco na confirmação | T026 | `ia::test_o_bloco_mostra_cada_inaplicabilidade` |
| FR-4468 — a ciência, assinada e conferida sob a trava | T025, T026 | `ic::test_aceite_sem_ciencia`, `::test_aceite_com_ciencia_superada`, `::test_aceite_com_ciencia` |
| FR-4469 — a trilha do desfecho cita os `id` | T025 | `ic::test_a_trilha_do_aceite_cita_as_conferencias` |
| FR-4470 — a guarda conta o *"não se aplica"* só no condicional | T024 | `dd::test_impede_incluir_incondicional`, `ic::test_p1_chamada_aberta` |
| FR-4471 — no mesmo ato, sem papel novo | T025 | `ic::test_o_alocado_nao_desfecha` (regressão da `115`) |
| FR-4472 — origem derivável sem campo novo | T023, T027 | `ic::test_origem_do_nao_se_aplica` |
| FR-4473 — formalização distingue as origens, sem motivo | T027 | `fc::test_as_duas_origens_do_nao_se_aplica` |
| FR-4474 — o auditor vê a contagem, e só | T026 | `ia::test_o_auditor_ve_a_contagem_separada` |
| FR-4475 — a condição no portal | T028 | `ob::test_condicional_a_apresentar` |
| FR-4476 — nada reescrito | T021 | `ic::test_p1_chamada_decidida_continua` |
| FR-4477 — versões antigas sem condição; nada inferido | T012 | `cp::test_versao_antiga_e_incondicional` |
| FR-4478 — a marca do registrado sem condição | T029 | `ia::test_registrado_sem_condicao_publicada` |

## Requisitos de experiência

| Requisito | Tarefa | Teste previsto |
|---|---|---|
| UX-301 — selo e contagens | T018, T026 | `ia::test_a_conducao_separa_as_contagens` |
| UX-302 — o texto da condição e do motivo | T010, T018 | `cp::test_a_condicao_nas_superficies` |
| UX-303 — o bloco da confirmação | T026 | `ia::test_o_bloco_mostra_cada_inaplicabilidade` |
| UX-304 — o portal no condicional | T028 | `ob::test_condicional_a_apresentar` |

## Critérios de sucesso

| Critério | Tarefa | Verificação |
|---|---|---|
| SC-1371 — nenhum aceite com incondicional afastado | T015, T021 | `ic`, cenários 1 e 10 |
| SC-1372 — o bloco e a ciência em 100% | T021, T022 | `ic`, `ia`, cenário 9 |
| SC-1373 — zero conferências fora do recorte | T015 | `ic`, cenário 11 |
| SC-1374 — as duas origens na formalização | T027 | `fc`, cenário 13 |
| SC-1375 — o mesmo texto nas cinco superfícies | T011, T018, T028 | `cp::test_a_condicao_nas_superficies` |
| SC-1376 — nada anterior muda | T021, T032 | suíte das tabelas append-only; `ic::test_p1_chamada_decidida_continua` |
| SC-1377 — consultas constantes | T031 | orçamento de consultas da condução e da página |
| SC-1378 — o conferente entende sem ajuda | T033 | humana, em `verificacao.md` |

## Casos-limite

| Caso | Teste previsto |
|---|---|
| Condição preenchida com espaços | `unit/editais::test_condicao_aparada_e_vazia` |
| Condição em documento que aproveita o da inscrição | `ic::test_condicional_aproveitado_pede_abertura_da_referencia` |
| Condição em documento com recorte por modalidade | `ic::test_condicional_com_recorte_de_modalidade` |
| Facultativo apresentado e sem sentido | `ic::test_facultativo_nao_tem_nao_se_aplica` |
| *"Não se aplica"* depois do vencimento | `ic::test_nao_se_aplica_depois_do_vencimento_so_no_condicional` |
| Duas pessoas ao mesmo tempo | `ic::test_aceite_com_ciencia_superada` |
| Correção da convocação pela `120` | `ic::test_a_correcao_herda_condicao_e_conferencia` |
| Nova chamada da mesma inscrição | `ic::test_nova_chamada_le_a_condicao_vigente_e_nao_herda_a_conferencia` |
| Retificação que muda ou retira a condição | `cp::test_a_retificacao_da_condicao_nao_alcanca_a_chamada_aberta` |
| Edital reaproveitado; Perfil duplicado | `cp::test_o_reaproveitamento_leva_a_condicao` (a duplicação não copia documento: sem teste novo) |
| Regularização | `ic::test_regularizacao_pede_ciencia` |
| Desfecho que não inclui | `ic::test_indeferimento_sem_ciencia` |
| Convocação sem lista | `ic::test_lista_incompleta_vem_antes_da_ciencia` |

## As nove decisões do usuário

| Decisão | Requisitos |
|---|---|
| 1ª — as quatro figuras | FR-4457, FR-4464, D-003 |
| 2ª — sem dispensa | D-003; nenhum requisito cria a operação |
| 10ª — o desenho mínimo aprovado | FR-4451 a FR-4478 |
| 11ª — o antigo incondicional não atende | FR-4470, FR-4478 |
| 12ª — a dispensa sem pendência própria; a P-3 pendente | D-003; FR-4473 |
| 3ª — sem motor, papel ou fluxo | FR-4452, FR-4465, FR-4471 |
| 4ª — a inaplicabilidade legítima se preserva | FR-4451, FR-4457 |
| 5ª — o arquivo, sozinho, não decide | FR-4460 |
| 6ª — `"."` não é fundamento | FR-4458, FR-4459 |
| 7ª — quem desfecha vê | FR-4466, FR-4467, FR-4468 |
| 8ª — nada se reinterpreta | FR-4476, FR-4477, FR-4478 |
| 9ª — o domínio recusa o fora do recorte | FR-4464 |
