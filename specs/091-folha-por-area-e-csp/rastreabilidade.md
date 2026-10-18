# Rastreabilidade — 091

Caminhos de teste relativos a `backend/tests/`. "Inventário" é a comparação de
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-091/` com o antes e os pares de ruído, por
`comparar.py`, `medidas.py`, `pixels.py` e as regras aplicadas como conjunto; "ordem" é o `ordem.py`
(R-003); "mutação" é a tabela do R-010. Os testes novos são nomeados aqui no plano e confirmados na
implementação.

| Requisito | Onde é provado |
|---|---|
| FR-2090 | `interface/test_folha_estatica.py` (a lista de áreas, cada arquivo achado pelos finders, `gestao.css` ausente); ordem (as regras de antes e de depois são as mesmas, menos as duplicadas listadas) |
| FR-2091 | Ordem: nenhum par que troca de ordem disputa propriedade num elemento do inventário; R-002 lista as que ficaram fora da área |
| FR-2092 | `interface/test_folha_estatica.py` (a base carrega os arquivos da lista, na ordem, cada um com `?v=`; `estaticos.E001` acusa o que falta) |
| FR-2093 | `duplicadas.py` e ordem; R-005 lista cada remoção |
| FR-2094 | Ordem (o número de comentários de antes e de depois, menos os de duplicada movidos) |
| FR-2095 | `interface/test_folha_estatica.py` (nenhum `_estilo_*.html`; os arquivos de grupo existem) |
| FR-2096 | `interface/test_folha_estatica.py` (cada arquivo de `telas/` carregado só por quem o cita; o bloco depois da folha comum; parcial antes do próprio) |
| FR-2097 | `interface/test_politica_de_conteudo.py` (nenhum `<style>` nos modelos da gestão e da página de acesso) |
| FR-2098 | `duplicadas.py`; `interface/test_folha_estatica.py` (as duas telas do assistente carregam o arquivo comum) |
| FR-2099 | `interface/test_folha_estatica.py` (o fragmento carrega a folha dele e não tem `<style>`) |
| FR-2100 | `interface/test_folha_estatica.py` (o `404.html` carrega `shared/erro.css`; nenhum `<style>`) |
| FR-2101 | `interface/test_politica_de_conteudo.py` (nenhum `style=` nos modelos da gestão; as classes de 0 a 100 existem) |
| FR-2102 | R-007 da pesquisa |
| FR-2103 | `interface/test_politica_de_conteudo.py` (o cabeçalho em tela, fragmento, acesso e página de erro sob `/gestao/`; nenhuma diretiva com `unsafe-`) |
| FR-2104 | `interface/test_politica_de_conteudo.py` (portal com `-Report-Only`); D-007 |
| FR-2105 | `interface/test_politica_de_conteudo.py` (JSON, PDF e `/health` sem cabeçalho; a constante é a única fonte); `pyproject.toml` sem dependência nova |
| FR-2106 | `interface/test_politica_de_conteudo.py` (nenhum script embutido, `on*=` ou `javascript:` nos modelos; nenhum script escreve o atributo `style`) |
| FR-2107 | `interface/test_politica_de_conteudo.py` (o `<meta>` do htmx em toda base que leva a tela com htmx); inventário (zero violações nas telas com htmx) |
| FR-2108 | `interface/test_politica_de_conteudo.py` (`DEBUG` com 404 e 500: sem cabeçalho; sem `DEBUG`: com); o guia (R-008) |
| FR-2109 | `interface/test_politica_de_conteudo.py` (`X-Frame-Options` igual ao de antes, a prévia `SAMEORIGIN`); inventário (a prévia e a Mesa sem violação) |
| FR-2110 | Os guardiões do R-010, repontados; mutação |
| FR-2111 | `interface/test_estaticos.py` (a varredura alcança `gestao/`, `telas/` e `shared/erro.css`); mutação |
| FR-2112 | `interface/test_politica_de_conteudo.py`; `interface/test_folha_estatica.py` |
| FR-2113 | Inventário, nos dois estados da barra; `capturar_bases.py` para a identificação, a página de erro e duas telas do portal |
| FR-2114 | `imprimir.py` da `088`, antes e depois |
| FR-2115 | `performance/test_escala_da_mesa.py` (teto intacto); R-012 |
| FR-2116 | Diff do PR (nenhuma view, permissão, endereço, consulta ou texto); `make test-pg` |
| SC-810 | Inventário e bases |
| SC-811 | `interface/test_politica_de_conteudo.py` |
| SC-812 | Inventário (violações por variante no `resultados.json`) |
| SC-813 | `depois-da-091/mutacoes.py` e `mutacoes.txt` |
| SC-814 | `make test-pg` |
| SC-815 | `interface/test_folha_estatica.py` |
| SC-816 | `duplicadas.py` |
| SC-817 | R-012 (`pesar.py`) |
