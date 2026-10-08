# Rastreabilidade — 061 · O corte emitido depois do recurso não nasce obsoleto

**Frase que governa**: *o recurso que a ordem já considerou não torna obsoleto o corte que leu essa
ordem.*

Cada linha aponta o lugar do código e o que o prende. **TR** =
`tests/integration/classificacao/test_corte_apos_recurso.py`; **TO** =
`tests/integration/classificacao/test_corte_obsoleto.py`, da `014`, sem edição; **V** = a
[verificação](verificacao.md), no banco de demonstração.

C = `backend/processo_seletivo/classificacao/application/corte.py`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1140** | C`_reingressou`: o filtro de sempre, mais `.exclude(id__in=citados)` (D-001) | TR `test_o_recurso_deferido_depois_do_corte_continua_impedindo_a_publicacao`; TO `test_o_reingresso_no_ato_de_ordenacao_e_nomeado_e_nao_vira_divergencia_generica` |
| **FR-1141** | o mesmo `.exclude` | TR `test_corte_emitido_sobre_a_ordem_sucessora_nao_nasce_obsoleto` (que confere também que o ato cita o sucessor); V |
| **FR-1142** | `citados` sai do `stageResults`; nenhuma comparação de `consolidado_em` nem de `emitido_em` (D-001) | revisão do diff; TR `test_corte_emitido_sobre_a_ordem_sucessora_nao_nasce_obsoleto` |
| **FR-1143** | nenhuma mudança em `resultados/application/prontidao.py` nem em `divulgacao/domain/publicabilidade.py`: os dois leem `estado_do_corte` | TR `test_corte_emitido_sobre_a_ordem_sucessora_nao_bloqueia_a_etapa_governada`, `test_a_publicacao_da_ordem_sucessora_nao_e_impedida_pelo_corte_emitido_depois`, `test_o_recurso_deferido_depois_do_corte_continua_impedindo_a_publicacao`; TO `test_o_corte_obsoleto_bloqueia_trabalho_novo_e_diz_o_caminho` |
| **FR-1144** | consequência do `.exclude`: a sucessora lê o mesmo ato | TR `test_a_geracao_sucessora_que_a_recusa_indica_nasce_em_dia` |
| **FR-1145** | as outras três causas e o filtro de Etapa da ordem, intocados em C | TO inteiro, sem edição — inclusive `test_o_deferimento_na_etapa_governada_nao_obsoleta_o_corte`, `test_a_ordem_sucedida_e_nomeada_e_o_corte_vigente_nao_muda`, `test_a_regra_retificada_e_nomeada` |
| **FR-1146** | nenhuma migration, nenhum comando; `git diff main --stat` | `make check` (`migrate --check`); V: os cortes do 72/2026, emitidos antes da correção, ficam em dia pela leitura (D-003) |
| **FR-1147** | a exclusão entra na mesma consulta; os ids vêm do universo já carregado | TR `test_a_comparacao_por_identidade_nao_acrescenta_consulta` |

## 2. Critérios de sucesso

| Identificador | O que o prende |
|---|---|
| **SC-440** | TR, os quatro casos da cronologia *recurso → ordem sucessora → corte*: falhavam os quatro contra a `main` `1d2c26ff` e passam com a correção (V) |
| **SC-441** | TO sem edição; TR `test_o_recurso_deferido_depois_do_corte_continua_impedindo_a_publicacao`, que passava contra a `main` e continua passando |
| **SC-442** | `make lint check test-pg` com banco próprio; o total em V |
