# Respostas gravadas da Caixa (116)

O que a API da Loteria Federal devolveu em **03/11/2026**, capturado pelo estudo
[`doc/estudo-extracao-da-loteria-federal-2026-11-03.md`](../../../../doc/estudo-extracao-da-loteria-federal-2026-11-03.md)
e copiado daqui de `doc/estudo-extracao-da-loteria-federal-2026-11-03/respostas/`, sem edição.

Cada arquivo é `{"status": ..., "capturada_em": ..., "corpo": ...}`. O nome diz o pedido:
`federal_ultimo.json` é `/federal`, e `federal_N.json` é `/federal/N`.

**O recorte feito na captura**, e não aqui: as respostas 200 perderam as listas de lotéricas
ganhadoras e o rateio de prêmios, e as 500 perderam o `stackTrace` do servidor. Nada disso é lido
pelo sistema, e o rateio é justamente o campo que o adaptador recusa como semente
(`loteria_federal._bilhetes_premiados`).

O que elas mostram, e que os testes da `116` conferem:

- `federal_ultimo.json`: o último realizado era o **6114**, de 01/11/2026, e o próximo anunciado,
  o 6115;
- `federal_6115.json`, `federal_0.json`, `federal_-1.json` e `federal_99999.json`: o concurso que
  ainda não aconteceu e o que nunca acontecerá recebem a **mesma** resposta HTTP 500 — por isso a
  consulta pelo número não decide nada (FR-3629);
- `federal_abc.json`: o texto é recusado com HTTP 400, como seria `6106-9` (FR-3623).

A suíte nunca chama a Caixa (FR-3651): o vigia de `tests/conftest.py` recusa a conexão.
