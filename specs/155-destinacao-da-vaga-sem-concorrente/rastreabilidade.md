# Rastreabilidade: Destinação da vaga reservada sem ocupante

Cada requisito da [spec](spec.md) e onde ele é verificado. Caminhos relativos a `backend/`.

**Esta entrega é a mínima** (ver *Esta entrega*, na spec). O que diz *próxima entrega* está
implementado e testado na branch `claude/155-destinacao-completa` (tag `155-destinacao-completa`), e
não aqui.

| Requisito | Onde é verificado | Observação |
|---|---|---|
| FR-6300 a FR-6303 | `tests/unit/ocupacao/test_destinacao_dominio.py`, `tests/interface/test_destinacao_na_ocupacao.py`, `tests/unit/interface/test_andamento_situacoes.py` | uma conta só para ocupação, Centro e convocação; onde a vaga não sai, a frase diz por quê, sem botão |
| FR-6304 | `tests/unit/ocupacao/test_destinacao_dominio.py`, `tests/integration/ocupacao/test_condicao_do_esgotamento.py` | V-1, V-2, V-4 e V-5 da verificação, no Edital silente |
| FR-6305 | — | **próxima entrega**, e bloqueada pela D-015: nenhuma regra do saldo foi escrita |
| FR-6306 e FR-6307 | `tests/unit/ocupacao/test_destinacao_dominio.py`, `tests/integration/ocupacao/test_condicao_do_esgotamento.py` | resultado provisório, recurso, chamada em curso, ampla sem aceite, apuração obsoleta |
| FR-6308 a FR-6314 | — | **próxima entrega**: o ato de destinação |
| FR-6315 e FR-6316 | — | **próxima entrega**. Nesta, a emissão cede como antes da `155`, nas duas espécies: `tests/integration/ocupacao/test_condicao_do_esgotamento.py` (a V-1 por esgotamento não cede) e `tests/test_gravacao_da_destinacao.py` |
| FR-6317 a FR-6319 | — | **próxima entrega**: a passagem entre cotas |
| FR-6320 a FR-6327 | `tests/integration/ocupacao/test_nao_preenchida.py`, `tests/interface/test_destinacao_na_ocupacao.py`, `tests/unit/ocupacao/test_apuracao_com_nao_preenchida.py`, `tests/unit/ocupacao/test_vaga_nao_preenchida_append_only.py` | Edital silente, linha geral, fundamento obrigatório, recusa onde o Edital declara a reversão; o relatório e a página pública da FR-6326 são da próxima entrega |
| FR-6328 a FR-6333 | — | **próxima entrega**: a lista vazia e o sorteio sem relação |
| FR-6334 a FR-6336 | `tests/integration/ocupacao/test_desfazimento_da_nao_preenchida.py`, `tests/interface/test_destinacao_na_ocupacao.py` | o desfazimento da declaração, com e sem chamada dependente; o da destinação é da próxima entrega |
| FR-6337 a FR-6340 | — | **próxima entrega**: a página pública, o relatório e o fundamento na chamada |
| FR-6341 e FR-6342 | `tests/integration/ocupacao/test_nao_preenchida.py`, `tests/interface/test_destinacao_na_ocupacao.py` | permissão e reprodução da declaração |
| FR-6343 | — | **próxima entrega**: as prévias |
| FR-6344 | `tests/test_vocabulario_da_ocupacao.py` | |
| UX-600 a UX-602 | `tests/interface/test_destinacao_na_ocupacao.py`, `tests/unit/interface/test_andamento_situacoes.py` | a conferência da UX-601 é a da declaração e do desfazimento dela |
| UX-603 | — | **próxima entrega**: a limitação da passagem entre cotas |
| SC-2100 | `tests/interface/test_destinacao_na_ocupacao.py` | a declaração, com uma confirmação, tira a providência da PPP |
| SC-2101 | `tests/interface/test_destinacao_na_ocupacao.py` | |
| SC-2102 | `tests/integration/ocupacao/test_nao_preenchida.py` | a declaração; a destinação é da próxima entrega |
| SC-2103 | `tests/test_gravacao_da_destinacao.py` | |
| SC-2104 a SC-2107 | — | **próxima entrega** |
| SC-2108 | — | roteiro com pessoas, pendente; a página pública é da próxima entrega |

A tabela nova é append-only nas duas camadas: `tests/seguranca/test_homologacao_preservada.py` (59
tabelas), `tests/integration/test_database_permissions.py` (percorre `TABELAS_APPEND_ONLY`) e
`tests/unit/ocupacao/test_vaga_nao_preenchida_append_only.py`.
