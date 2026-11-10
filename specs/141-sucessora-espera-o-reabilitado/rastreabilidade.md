# Rastreabilidade: A ordem sucessora e o corte esperam a avaliação do reabilitado (141)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `un` = `unit/interface/test_sucessora_espera_o_reabilitado.py` — as células, puras
- `in` = `integration/treinamento/test_sucessora_espera_o_reabilitado.py` — o C08 da `134`, pelos
  comandos
- `os` = `interface/test_ordem_sem_resultado.py` — a coerência com a `128`, sem mudança
- `es` = `performance/test_andamento_em_escala.py` — o orçamento da `127`, com os tetos de antes
- `nv` = conferência no navegador, em [verificacao.md](verificacao.md)

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4830 (a sucessora com Etapa por fazer é *Depois*) | T002 | `un::test_a_sucessora_com_etapa_por_fazer_e_depois_e_diz_por_que`; `un::test_a_lista_vazia_com_etapa_por_fazer_espera_como_a_primeira_ordem`; `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez`; `nv` |
| FR-4831 (a razão, UX-340) | T002 | `un::test_a_sucessora_com_etapa_por_fazer_e_depois_e_diz_por_que`; `un::test_duas_etapas_por_fazer_vao_ao_plural`; `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez` |
| FR-4832 (sem Etapa por fazer, como antes) | T002 | `un::test_sem_etapa_por_fazer_a_sucessora_e_providencia_como_antes`; `un::test_a_lista_vazia_sem_etapa_por_fazer_continua_com_a_frase_da_135`; `in::test_a_correcao_de_nota_sem_reabilitar_oferece_a_sucessora_na_hora` |
| FR-4833 (o dado; o resultado de antes) | T001, T003 | `un::test_o_resultado_le_a_sucessora_a_espera_como_lia_a_obsoleta`; `un::test_ordem_para_tras`; `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez` (o resultado e o divulgado) |
| FR-4834 (o corte e a apuração de antes) | T001 | `un::test_o_corte_e_a_apuracao_leem_a_sucessora_a_espera_como_a_obsoleta` |
| FR-4845 (no Centro, a fase está em curso) | T017 | `un::test_no_centro_a_fase_com_a_sucessora_a_espera_esta_em_curso`; `nv` |
| FR-4835 (o corte espera o reingresso, pela função da publicação) | T006, T007 | `un::test_com_reingresso_o_corte_a_emitir_espera`; `in::test_com_a_sucessora_parcial_emitida_pela_tela_o_corte_espera_o_reingresso` |
| FR-4836 (as duas formas, UX-341) | T006 | `un::test_com_reingresso_o_corte_a_emitir_espera`; `un::test_com_reingresso_a_geracao_sucessora_tambem_espera`; `un::test_o_reingresso_vem_antes_da_espera_do_prazo` |
| FR-4837 (sem reingresso, como antes) | T006 | `un::test_sem_reingresso_o_corte_e_o_de_antes`; `un::test_o_corte_feito_continua_feito_com_reingresso`; `in::test_a_correcao_de_nota_sem_reabilitar_oferece_a_sucessora_na_hora`; `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez` (o passo 3) |
| FR-4838 (nunca no sorteio) | T007 | a leitura não pergunta em marco por sorteio (`_marco`, `not sorteado`); a suíte do sorteio da `127` e da `136` sem mudança de expectativa |
| FR-4839 (a Etapa governada sem espera nova, D-004) | T010 | `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez` (o primeiro e o último passo); `in::test_o_corte_anterior_ao_recurso_continua_vigente_ate_a_sucessora`; `un::test_o_corte_feito_continua_feito_com_reingresso` |
| FR-4840 (o aviso na tela do corte, UX-342) | T012 | `in::test_a_tela_do_corte_avisa_do_reingresso_e_continua_emitindo`; `nv` |
| FR-4841 (o aviso não impede; sem reingresso, não aparece) | T012, T013 | `in::test_a_tela_do_corte_avisa_do_reingresso_e_continua_emitindo`; `in::test_sem_reingresso_a_tela_do_corte_nao_avisa` |
| FR-4842 (nenhum comando muda) | T009, T013 | `in::test_com_a_sucessora_parcial_emitida_pela_tela_o_corte_espera_o_reingresso` (a parcial é aceita); `in::test_a_tela_do_corte_avisa_do_reingresso_e_continua_emitindo` (o corte é aceito); nenhum comando no diff |
| FR-4843 (custo fixo por marco) | T004, T007 | `es` com os tetos de antes; a pergunta só com o corte obsoleto ou sobre ordem feita (`_marco`) |
| FR-4844 (nunca *Pendente* para o que o comando recusa) | T014 | `os::test_o_andamento_nunca_diz_pendente_para_a_ordem_que_o_comando_recusa` |

## Regras de experiência

| Regra | Testes |
|---|---|
| UX-340 | `un::test_a_sucessora_com_etapa_por_fazer_e_depois_e_diz_por_que`; `un::test_duas_etapas_por_fazer_vao_ao_plural` |
| UX-341 | `un::test_com_reingresso_o_corte_a_emitir_espera`; `un::test_com_reingresso_a_geracao_sucessora_tambem_espera` |
| UX-342 | `in::test_a_tela_do_corte_avisa_do_reingresso_e_continua_emitindo`; `nv` |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1510 | `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez` (o passo 1, para três papéis); `nv` |
| SC-1511 | `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez` (os passos 2 a 4); `nv` |
| SC-1512 | `in::test_a_correcao_de_nota_sem_reabilitar_oferece_a_sucessora_na_hora` |
| SC-1513 | `in::test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez`; `un::test_o_resultado_le_a_sucessora_a_espera_como_lia_a_obsoleta` |
| SC-1514 | `es`, com os tetos de antes |
| SC-1515 | a suíte inteira contra PostgreSQL; `os`; os casos da lista vazia da `135` |
| SC-1516 | `nv` |

As faixas reservadas e não gastas — do requisito quatro mil oitocentos e quarenta e seis ao quatro
mil oitocentos e cinquenta e nove, dos critérios mil quinhentos e dezessete a mil quinhentos e
dezenove e das regras trezentos e quarenta e três a trezentos e quarenta e nove — ficam livres.
