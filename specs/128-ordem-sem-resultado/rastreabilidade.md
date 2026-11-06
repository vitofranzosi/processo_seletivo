# Rastreabilidade: A ordem por pontuação sem nenhum resultado é recusada (128)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `un` = `unit/classificacao/test_ordem_sem_resultado.py` — a regra, sobre a proposta
- `co` = `integration/classificacao/test_ordem_sem_resultado.py` — o comando, sob a trava
- `te` = `interface/test_ordem_sem_resultado.py` — a tela da ordem e o gesto da condução
- `cq` = capturas antes e depois em `capturas/`

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4200 (a regra) | T004, T005, T007 | `un::test_ninguem_com_resultado_e_recusado`; `co::test_sem_nenhum_resultado_a_emissao_e_recusada_e_nada_e_gravado` |
| FR-4201 (o que é Resultado) | T004 | `un::test_a_porta_sem_pontuacao_conta_como_resultado`; `un::test_a_eliminacao_conta_como_resultado`; `co::test_a_ocorrencia_que_elimina_e_resultado` |
| FR-4202 (o desempate não conta) | T004 | `un::test_resultado_so_na_etapa_do_desempate_nao_conta`; `co::test_resultado_so_na_etapa_do_desempate_nao_basta` |
| FR-4203 (o universo do cálculo) | T005, T007 | `co::test_o_recorte_reservado_com_autodeclarados_e_sem_resultado_e_recusado`; `co::test_universo_vazio_continua_emitindo_a_ordem_vazia` (o recorte reservado vazio e a ampla do mesmo Edital); leitura de `ordem_sem_resultado.impedimento`, que lê só a proposta |
| FR-4204 (a ordem parcial) | T007 | `un::test_um_resultado_basta_ordem_parcial`; `co::test_com_um_resultado_a_ordem_parcial_e_emitida`; `te::test_a_ordem_parcial_continua_com_formulario_e_confirmacao` |
| FR-4205 (universo vazio) | T007, T013 | `un::test_universo_vazio_nao_e_recusado`; `co::test_universo_vazio_continua_emitindo_a_ordem_vazia`; `te::test_o_recorte_em_que_ninguem_concorreu_continua_a_praticar` |
| FR-4206 (no comando, sob a trava, antes da assinatura) | T007 | `co::test_sem_nenhum_resultado_a_emissao_e_recusada_e_nada_e_gravado`; `co::test_a_recusa_vem_antes_da_assinatura`; `te::test_o_formulario_antigo_e_recusado_pelo_comando` |
| FR-4207 (a sucessão) | T007 | `co::test_a_sucessao_de_uma_ordem_do_acervo_sem_resultado_e_recusada` |
| FR-4208 (o gesto) | T007, T013 | `te::test_a_confirmacao_do_gesto_recusa_no_comando` |
| FR-4209 (a repetição) | T007 | `co::test_a_repeticao_de_um_pedido_atendido_devolve_o_desfecho` |
| FR-4210 (nada é gravado) | T007 | `co::test_sem_nenhum_resultado_a_emissao_e_recusada_e_nada_e_gravado`; `co::test_depois_que_o_resultado_chega_a_mesma_emissao_e_aceita_com_a_mesma_chave` |
| FR-4211 (código e frase) | T005 | `un::test_a_frase_no_plural_com_uma_etapa`; `un::test_a_frase_no_singular_e_com_varias_etapas_na_ordem_do_marco`; `un::test_recusar_levanta_o_codigo_proprio_com_a_frase` |
| FR-4212 (sem formulário) | T009, T010 | `te::test_a_tela_nao_oferece_emitir_e_leva_a_distribuicao`; `te::test_a_ordem_do_acervo_nao_traz_o_bloco_de_sucessao`; `cq` |
| FR-4213 (os links e o pedido) | T009, T010 | `te::test_a_tela_nao_oferece_emitir_e_leva_a_distribuicao`; `te::test_quem_nao_gere_le_a_frase_sem_link_nem_pedido` |
| FR-4214 (a prévia continua) | T010 | `te::test_a_tela_nao_oferece_emitir_e_leva_a_distribuicao` |
| FR-4215 (a confirmação não abre) | T009 | `te::test_a_confirmacao_nao_abre` |
| FR-4216 (o impedido na conferência) | T013 | `te::test_a_conferencia_do_gesto_poe_o_recorte_entre_os_impedidos` |
| FR-4217 (uma regra só) | T005, T011 | `unit/interface/test_conferencia_da_ordem.py` inteiro, sem mudança; leitura: as quatro chamadas são a `ordem_sem_resultado` ou a `nenhuma_com_resultado` |
| FR-4218 (a `127`) | T015 | leitura de `andamento.situacao_da_ordem` (`verificacao.md`); a `127` não está na `main` |
| FR-4219 (acervo, sem migration) | T006, T016 | `co::test_a_sucessao_de_uma_ordem_do_acervo_sem_resultado_e_recusada`; `manage.py makemigrations --check` |
| FR-4220 (testes de conveniência) | T014 | `verificacao.md`, seção dos ajustes |

## Experiência

| Requisito | Tarefas | Testes |
|---|---|---|
| UX-260 (a frase) | T005 | `un::test_a_frase_no_plural_com_uma_etapa`; `un::test_a_frase_no_singular_e_com_varias_etapas_na_ordem_do_marco` |
| UX-261 (o bloco da tela) | T010 | `te::test_a_tela_nao_oferece_emitir_e_leva_a_distribuicao`; `cq` |
| UX-262 (a linha do impedido) | T013 | `te::test_a_conferencia_do_gesto_poe_o_recorte_entre_os_impedidos` |

## Critérios de sucesso

| Critério | Verificação |
|---|---|
| SC-1300 | `co::test_sem_nenhum_resultado_a_emissao_e_recusada_e_nada_e_gravado`; `co::test_a_sucessao_de_uma_ordem_do_acervo_sem_resultado_e_recusada`; `te::test_a_confirmacao_do_gesto_recusa_no_comando` |
| SC-1301 | `co::test_com_um_resultado_a_ordem_parcial_e_emitida`; `co::test_universo_vazio_continua_emitindo_a_ordem_vazia`; `co::test_a_ocorrencia_que_elimina_e_resultado`; todos eliminados: `un::test_todos_eliminados_e_ordem_emissivel` |
| SC-1302 | `te::test_a_tela_nao_oferece_emitir_e_leva_a_distribuicao`; `te::test_a_confirmacao_nao_abre` |
| SC-1303 | `te::test_a_conferencia_do_gesto_poe_o_recorte_entre_os_impedidos` |
| SC-1304 | `co::test_a_sucessao_de_uma_ordem_do_acervo_sem_resultado_e_recusada`; `makemigrations --check` |
| SC-1305 | a suíte contra PostgreSQL (`verificacao.md`) |
| SC-1306 | leitura (`verificacao.md`); teste quando a `127` estiver na `main` |
