# Rastreabilidade — 088

Caminhos de teste relativos a `backend/tests/`. "Impressão" é a conferência do passo 1 e 2 do
[quickstart](quickstart.md) — emulação da mídia de impressão e `--print-to-pdf`; "inventário" é a
comparação com a linha de base de antes, em
[`depois-da-088/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/antes/), pelo
`comparar.py` e pelo `medidas.py`.

| Requisito | Onde é provado |
|---|---|
| FR-2000 | `interface/test_decisoes_da_etapa_4.py` (a regra de impressão lida da folha; a trilha dentro do cabeçalho nas quatro telas); impressão |
| FR-2001 | `interface/test_decisoes_da_etapa_4.py` (a barra lateral e "Trocar identidade" fora do papel, lidos da folha); impressão |
| FR-2002 | `interface/test_decisoes_da_etapa_4.py` (uma regra só, no `@media print` de `base.html`; nenhum template com `@media print` próprio para a trilha) |
| FR-2003 | Inventário — nenhuma variante fora das três telas dos avisos muda de medida |
| FR-2004 | Impressão — a trilha longa do Ato e do Recurso quebra a linha, sem nível cortado |
| FR-2005 | `interface/test_telas_de_uso_diario.py`, sem mudança (a trilha da lista e de Minhas Etapas como navegação nomeada) |
| FR-2010 | `interface/test_decisoes_da_etapa_4.py` (o histórico de um aviso, com a hora de America/Sao_Paulo); `interface/test_telas_dos_avisos.py`, ajustado |
| FR-2011 | `interface/test_decisoes_da_etapa_4.py` (a conferência da interrupção e a prévia do reenvio); `interface/test_telas_dos_avisos.py`, ajustado |
| FR-2012 | `interface/test_telas_dos_avisos.py` (os demais níveis das três trilhas, sem mudança) |
| FR-2020 | `interface/test_decisoes_da_etapa_4.py` (o Ato da lista PPI e o da ampla concorrência) |
| FR-2021 | `interface/test_decisoes_da_etapa_4.py` (o link do Ato é o mesmo endereço que "Cancelar e voltar" da conferência do mesmo recorte) |
| FR-2022 | `interface/test_decisoes_da_etapa_4.py`; `interface/test_telas_de_resultado_e_atos.py`, sem mudança (o rótulo e os demais níveis da trilha do Ato) |
| FR-2025 | `make test-pg` — nenhum teste de regra de negócio ou de permissão ajustado |
| FR-2026 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, os testes de trilha da `077` à `087`; o único ajuste, em `interface/test_telas_dos_avisos.py`, comentado |
| SC-780 | `interface/test_decisoes_da_etapa_4.py`; impressão das quatro telas |
| SC-781 | Inventário: estouram a 375 e a 1280 px, zero; fora de `aviso`, `aviso-interromper` e `aviso-reenviar`, nenhuma variante muda de medida |
| SC-782 | `interface/test_decisoes_da_etapa_4.py` (dois avisos do mesmo dia) |
| SC-783 | `interface/test_decisoes_da_etapa_4.py` (seguir o link do Ato da lista PPI) |
| SC-784 | `make test-pg` |

## Casos-limite

| Caso | Onde é provado |
|---|---|
| Tela sem trilha, impressa | Impressão — uma tela com o cabeçalho da `076` imprime o caminho até a seção |
| "Trocar identidade" no papel | `interface/test_decisoes_da_etapa_4.py`; impressão |
| A trilha longa no papel | Impressão (FR-2004) |
| Links no papel | Impressão — o PDF não traz endereço depois dos níveis |
| A tela, na tela | Inventário (FR-2003) |
| Dois avisos no mesmo minuto | Aceito (D-007); sem teste |
| Aviso perto da meia-noite em UTC | `interface/test_decisoes_da_etapa_4.py` (o aviso das 22:30 de Brasília) |
| A lista de avisos | `interface/test_telas_dos_avisos.py`, sem mudança |
| Ato de um recorte que a Retificação tirou | Aceito (D-006); o destino responde pela `FR-499` da `034`, já provada lá |
| Ato sucedido | `interface/test_decisoes_da_etapa_4.py` (o recorte lido do próprio ato) |
| Quem audita | `interface/test_decisoes_da_etapa_4.py` (o mesmo link para presidência e auditoria) |
