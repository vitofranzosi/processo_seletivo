# Rastreabilidade — 088

Caminhos de teste relativos a `backend/tests/`; `decisoes` é `interface/test_decisoes_da_etapa_4.py`.
"Impressão" é a conferência do passo 2 do [quickstart](quickstart.md) — o `imprimir.py`, com a mídia
de impressão emulada e o PDF em A4, antes e depois, guardada em
[`depois-da-088/impressao/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/impressao/);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-088/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/antes/), pelo
`comparar.py` e pelo `medidas.py`.

| Requisito | Onde é provado |
|---|---|
| FR-2000 | `decisoes` (`test_no_papel_sai_o_cabecalho_sem_trocar_identidade_e_sem_a_barra`; `test_impresso_o_ato_diz_de_que_edital_e`, `test_impressa_a_inscricao_recebida_diz_de_que_edital_e`, `test_impresso_o_recurso_diz_de_que_edital_e`, `test_impressa_a_inscricao_da_mesa_diz_de_que_mesa_e`); impressão |
| FR-2001 | `decisoes` (`test_no_papel_sai_o_cabecalho_sem_trocar_identidade_e_sem_a_barra`; `no_papel`, que só deixa "Trocar identidade" fora da trilha); impressão |
| FR-2002 | `decisoes` (`test_a_regra_de_impressao_e_uma_so`) |
| FR-2003 | Inventário — nenhuma variante muda por causa da regra de impressão |
| FR-2004 | `decisoes` (`test_no_papel_a_trilha_quebra_a_linha`); impressão — a trilha do Ato quebra no A4, sem nível cortado |
| FR-2005 | `interface/test_telas_de_uso_diario.py` (`test_na_raiz_da_secao_a_trilha_tem_um_nivel`), sem mudança |
| FR-2010 | `decisoes` (`test_o_rotulo_do_aviso_tem_a_hora_de_brasilia`); `interface/test_telas_dos_avisos.py` (`rotulo_do_aviso`, ajustado) |
| FR-2011 | `decisoes` (`test_o_rotulo_do_aviso_tem_a_hora_de_brasilia`, na interrupção e no reenvio); `interface/test_telas_dos_avisos.py` (`ate_o_aviso`, ajustado) |
| FR-2012 | `interface/test_telas_dos_avisos.py` (os níveis das três trilhas, em ordem, sem mudança além do rótulo) |
| FR-2020 | `decisoes` (`test_do_ato_de_uma_lista_a_classificacao_e_a_dessa_lista`, `test_do_ato_da_ampla_a_classificacao_e_a_de_antes`) |
| FR-2021 | `decisoes` (`test_do_ato_de_uma_lista_a_classificacao_e_a_dessa_lista`: o mesmo endereço da conferência da emissão do mesmo recorte) |
| FR-2022 | `decisoes` (`test_do_ato_da_ampla_a_classificacao_e_a_de_antes`); `interface/test_telas_de_resultado_e_atos.py` (`test_o_ato_de_classificacao_ganha_o_edital_na_trilha`), sem mudança |
| FR-2025 | `make test-pg` — nenhum teste de regra de negócio ou de permissão ajustado |
| FR-2026 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, os testes de trilha da `077` à `087`; o único ajuste, em `interface/test_telas_dos_avisos.py`, com o porquê no `rotulo_do_aviso` |
| SC-780 | `decisoes` (as quatro telas); impressão das quatro, da recusa e de um aviso |
| SC-781 | Inventário: estouram a 375 e a 1280 px, zero; só `aviso-reenviar` a 1280, com a barra expandida, muda (1405 → 1419) |
| SC-782 | `decisoes` (`test_dois_avisos_do_mesmo_dia_tem_rotulos_diferentes`) |
| SC-783 | `decisoes` (`test_do_ato_de_uma_lista_a_classificacao_e_a_dessa_lista`: seguido o link, a PPI é o recorte atual) |
| SC-784 | `make test-pg` |

## Casos-limite

| Caso | Onde é provado |
|---|---|
| Tela sem trilha, impressa | `decisoes` (`test_impressa_a_recusa_sai_com_o_caminho_da_secao`); impressão da recusa |
| "Trocar identidade" no papel | `decisoes` (`test_no_papel_sai_o_cabecalho_sem_trocar_identidade_e_sem_a_barra`); impressão |
| A trilha longa no papel | `decisoes` (`test_no_papel_a_trilha_quebra_a_linha`); impressão do Ato |
| Links no papel | Impressão — o PDF não traz endereço depois dos níveis |
| A tela, na tela | Inventário (FR-2003) |
| Dois avisos no mesmo minuto | Aceito (D-007); sem teste |
| Aviso perto da meia-noite em UTC | `decisoes` (`test_o_rotulo_do_aviso_tem_a_hora_de_brasilia`: 01:30 UTC, 22:30 do dia anterior em Brasília) |
| A lista de avisos | `interface/test_telas_dos_avisos.py`, sem mudança |
| Ato de um recorte que a Retificação tirou | Aceito (D-006); o destino responde pela `FR-499` da `034`, já provada lá |
| Ato sucedido | Pelo desenho: o endereço sai de `ato.lista_id`, do próprio ato; sem teste próprio |
| Quem audita | `decisoes` (`test_quem_audita_segue_o_mesmo_link`) |
