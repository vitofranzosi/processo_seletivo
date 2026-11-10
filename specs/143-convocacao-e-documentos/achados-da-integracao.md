# Achados da validação integrada (10/11)

Encontrados na validação das specs `138`, `142` e `143` juntas, na branch `integracao-138-142-143`
(`122b83ca`). **Nenhum foi corrigido aqui**: são registro para decisão, e não escopo desta spec.

## A-1 — A providência "Conferir os documentos" chega ao título das chamadas, e não à primeira a conferir

A FR-4763 da `139` leva a providência a `#chamadas`. Com a `143`, cada cartão tem âncora estável
(`#convocacao-<id>`), e o índice do alto já leva à primeira chamada com documento a conferir. A
providência do Centro poderia levar direto a ela, como a do desfecho leva à primeira pronta (a
FR-4764 da `139`). Mudaria o fragmento que `andamento.py` monta, e por isso é da `139`, e não desta.
**Impacto:** baixo — a primeira chamada está logo abaixo do título.

## A-2 — Quem só consulta vê o link "Documentos da convocação", e a página recusa

Anterior à `143`: o template da `main` em `daba322f` já mostrava o link a todos os que leem a
condução. A auditoria lê a convocação, e a página dos documentos recusa com 403 — é o predicado da
FR-3595 da `115`, que exclui a auditoria do arquivo (a FR-3598 da `115`). O passo novo da `143` já
esconde o "Conferir os documentos" de quem não confere; a linha antiga dos documentos não.
**Impacto:** baixo — um clique numa recusa explicada. A correção seria mostrar o link só a quem
confere (`confere`, que a view já calcula).

## A-3 — "Chamar uma pessoa da fila" abre sozinho com todas as vagas cobertas

Anterior à `143` (a M-19 do estudo): sem titular a convocar, o formulário da chamada individual vem
aberto, mesmo quando todas as vagas têm chamada em curso. Com a `143` ele mora na área "Fila,
suplentes e regularização", depois das chamadas, e não compete mais com elas. O estudo pede
validar com operadores antes de recolhê-lo, porque a chamada individual também serve a exceções.
