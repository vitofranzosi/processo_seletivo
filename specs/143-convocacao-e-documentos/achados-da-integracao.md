# Achados da validação integrada (10/11)

Encontrados na validação das specs `138`, `142` e `143` juntas, na branch `integracao-138-142-143`
(`122b83ca`). A-1 e A-3 ficam registrados, sem correção; o A-2 foi corrigido na revisão do #453
(achado 4 dela).

**A suíte inteira sobre a integração** (`make lint check test-pg`, 4 workers, `122b83ca`):
**17.904 passando, 12 pulados, sem falha**, em 1.216 s. A jornada percorrida: Centro do C12 →
"Conferir os documentos de 3 convocações" (chega a `#chamadas`, a FR-4763 da `139`) → cartão →
documentos → dois "conforme" → "Pronta para o desfecho" → formulário aberto a y=557 → aceite pela
conferência do texto da `125` → "Voltar ao Centro de Controle do Edital" → o Centro, com "Conferir os
documentos de 2 convocações". O reenvio pelo portal, com o código lido do terminal do servidor e só
cliques depois dele: o C11-02 corrigiu o diploma, e a gestão passou a ler "Conferir de novo: o
candidato reenviou 1 documento" e o Centro, "Conferir os documentos de 2 convocações". A conferência
da `140` (C10) e a tela do sorteio da `142` (C06) abriram pelo Centro, sem violação de CSP; nenhuma
página rolou de lado a 375 px. Capturas em `capturas/integracao/`.

## A-1 — A providência "Conferir os documentos" chega ao título das chamadas, e não à primeira a conferir

A FR-4763 da `139` leva a providência a `#chamadas`. Com a `143`, cada cartão tem âncora estável
(`#convocacao-<id>`), e o índice do alto já leva à primeira chamada com documento a conferir. A
providência do Centro poderia levar direto a ela, como a do desfecho leva à primeira pronta (a
FR-4764 da `139`). Mudaria o fragmento que `andamento.py` monta, e por isso é da `139`, e não desta.
**Impacto:** baixo — a primeira chamada está logo abaixo do título.

## A-2 — Quem só consulta vê o link "Documentos da convocação", e a página recusa (corrigido)

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
