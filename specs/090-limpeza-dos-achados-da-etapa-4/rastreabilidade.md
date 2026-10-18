# Rastreabilidade — 090

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em `depois-da-090/antes/`, pelo
`comparar.py` e pelo `medidas.py`. O módulo dos testes novos é
`interface/test_limpeza_dos_achados_da_etapa_4.py` (abaixo, "090").

| Requisito | Onde é provado |
|---|---|
| FR-2060 | 090 — a marca descreve cada ato irreversível nos três detalhes, e só eles; navegador |
| FR-2061 | 090 — rótulo, destino e desenho iguais; o ato indisponível com o motivo |
| FR-2062 | 090 — a trilha das três consultas com presidência, gestão sistêmica e auditoria |
| FR-2063 | 090 — cada link da trilha, seguido pela mesma pessoa, responde 200 |
| FR-2064 | 090 — consultas iguais às de antes, nas três telas e com as duas bases |
| FR-2065 | 090 — a regra comum do rodapé quebra a linha; inventário a 375 px |
| FR-2066 | Inventário: nenhuma variante com o rodapé muda a 1280 px; a 375, só de altura |
| FR-2067 | 090 — a trilha e "Cancelar" da prévia aberta pelos Resultados divulgados, com e sem a Classificação |
| FR-2068 | 090 — a porta depois de "Usar este modelo" e da recusa do envio; porta desconhecida e porta que quem lê não abre |
| FR-2069 | 090 — o aviso confirmado pelas duas portas; `interface/test_telas_dos_avisos.py`, sem mudança |
| FR-2070 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` |
| FR-2071 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `test_gramatica_das_portas.py` |
| FR-2072 | As anotações na spec da `080` (`FR-1800`, `FR-1804`, a decisão 003) e na da `086` (`FR-1942`, `FR-1946`) |
| SC-800 | A tabela de decisões da [spec](spec.md): quatro achados, quatro destinos |
| SC-801 | 090 — sete atos irreversíveis nos três detalhes, cada um descrito pela marca |
| SC-802 | 090 — zero links da trilha que recusam quem só audita; quatro para quem preside |
| SC-803 | Inventário: `aviso-interromper` a 375 px |
| SC-804 | 090 — a trilha e "Cancelar" da prévia pelos Resultados divulgados |
| SC-805 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente; nada muda a 1280 px além da variante nova |
| SC-806 | `make test-pg` |
