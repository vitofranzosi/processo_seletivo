# Rastreabilidade — 089

Caminhos de teste relativos a `backend/tests/`. "Inventário" é a comparação de
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/` com o `antes/` e o `ruido/` da mesma pasta,
por `comparar.py`, `medidas.py` e `pixels.py`; "equivalência" é o script de equivalência das regras
(R-001); "mutação" é a tabela do R-005.

| Requisito | Onde é provado |
|---|---|
| FR-2030 | Equivalência: as regras de antes e de depois iguais byte a byte, na ordem |
| FR-2031 | `interface/test_folha_estatica.py` (a ordem tokens → folha comum → estilo da página; nenhuma regra comum no modelo) |
| FR-2032 | `interface/test_folha_estatica.py` (as quatro bases carregam os tokens antes de todo `<style>`; o parcial não existe; um lugar só define os tokens) |
| FR-2033 | Equivalência (o número de comentários convertidos é o de antes, menos o do ponto de extensão, que fica no modelo; nenhum fecha antes do fim) |
| FR-2034 | `interface/test_folha_estatica.py` (endereço estável e endereço novo com conteúdo novo); navegador, a edição no runserver (quickstart) |
| FR-2035 | `interface/test_folha_estatica.py` (os finders acham os dois arquivos com a configuração do projeto); o guia de implantação (R-006) |
| FR-2036 | `interface/test_folha_estatica.py` (os parciais `_estilo_*` e o bloco por página continuam no documento); diff do PR |
| FR-2037 | R-005: a contagem dos `style="`; nenhum cabeçalho de CSP no diff |
| FR-2038 | Os guardiões do R-005, repontados; mutação |
| FR-2039 | Os guardiões do R-005 que descontam `/* */`; mutação com violação dentro e fora de comentário |
| FR-2040 | `performance/test_escala_da_mesa.py` (`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`, teto intacto); R-008 |
| FR-2041 | Inventário, nos dois estados da barra; `capturar_bases.py` + `pixels.py` |
| FR-2042 | Impressão emulada antes e depois (quickstart) |
| FR-2043 | `interface/test_estaticos.py` (guardião novo: nenhuma sintaxe de modelo em `gestao.css` e `tokens.css`); mutação |
| SC-790 | Inventário e bases: zero diferença fora do ruído, zero estouros, nenhum `status` diferente |
| SC-791 | R-008: Distribuição, lista e Minhas Etapas antes e depois |
| SC-792 | Navegador: `transferSize` da folha na segunda página |
| SC-793 | Mutação, guardião a guardião |
| SC-794 | `make test-pg` |
| SC-795 | `interface/test_folha_estatica.py`; equivalência |
