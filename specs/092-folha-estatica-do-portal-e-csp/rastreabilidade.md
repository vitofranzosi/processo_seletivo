# Rastreabilidade — 092

Caminhos de teste relativos a `backend/tests/`. "Inventário" é a comparação de
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/` com o antes e os pares de ruído, por
`medidas.py`, `pixels.py` e as regras aplicadas como conjunto (R-006); "equivalência" é o
`equivalencia.py` (R-002); "mutação" é o `mutacoes.py` (R-004). Confirmados na implementação.

| Requisito | Onde é provado |
|---|---|
| FR-2130 | `interface/test_folha_estatica.py` (`test_a_base_do_portal_carrega_a_folha_dele`; a vitrine carrega tokens e depois `portal/portal.css`, com `?v=`) |
| FR-2131 | Equivalência: o arquivo é o `<style>` de antes, byte a byte, menos o cabeçalho, as classes e as sete grafias listadas no R-002; inventário (o mesmo conjunto de regras em todas as telas) |
| FR-2132 | Equivalência (os 124 comentários de antes, no mesmo lugar) |
| FR-2133 | `interface/test_folha_estatica.py` (`portal/portal.css` em `FOLHAS`; `estaticos.E001` acusa a que falta) |
| FR-2134 | `interface/test_politica_de_conteudo.py` (`test_nenhum_modelo_tem_estilo_embutido`, em todos os modelos) |
| FR-2135 | `interface/test_politica_de_conteudo.py` (as 101 classes do portal; a barra com a classe do percentual em cinco casos); `integration/inscricoes/test_envio_de_arquivo.py` (`largura-50`); inventário (os três rascunhos) |
| FR-2136 | `interface/test_politica_de_conteudo.py` (portal, erro do portal e erro na raiz em recusa; `test_o_caminho_nao_decide`); inventário (as 103 respostas com o cabeçalho) |
| FR-2137 | `interface/test_politica_de_conteudo.py` (nenhuma `-Report-Only`); `interface/test_prototipo_do_assistente.py` (`test_o_fundo_do_portal_fica_sob_a_recusa`) |
| FR-2138 | `interface/test_politica_de_conteudo.py` (JSON, PDF, `/health`, depuração com `DEBUG`, resposta que já declara política) |
| FR-2139 | Os guardiões do R-004, repontados; mutação |
| FR-2140 | `interface/test_estaticos.py` (`test_nenhuma_sintaxe_de_template_nas_folhas_estaticas[portal/portal.css]`); mutação 18 |
| FR-2141 | `interface/test_politica_de_conteudo.py` (`TODOS_OS_MODELOS`); mutações 21 e 22 |
| FR-2142 | Inventário: as 103 telas do portal, o protótipo e as bases |
| FR-2143 | Inventário com `IMPRESSAO=1` (o papel de 15 telas, e as páginas do PDF); `integration/portal/test_revisao_e_comprovante.py` |
| FR-2144 | R-005 (`pesar_portal.py`) |
| FR-2145 | Diff do PR (nenhuma view, permissão, endereço, consulta ou texto); `make test-pg` |
| SC-820 | Inventário e bases |
| SC-821 | `interface/test_politica_de_conteudo.py` |
| SC-822 | Inventário (violações por variante no `resultados.json`) |
| SC-823 | `depois-da-092/mutacoes.py` e `mutacoes.txt` |
| SC-824 | `make test-pg` |
| SC-825 | R-005 |
| SC-826 | `interface/test_politica_de_conteudo.py`; inventário |
