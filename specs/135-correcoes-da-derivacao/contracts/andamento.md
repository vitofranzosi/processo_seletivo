# Contrato: o que o andamento diz, antes e depois (135)

O contrato das telas da `127` (`specs/127-andamento-da-selecao/contracts/telas.md`) continua valendo.
Aqui está só o que muda, nos três lugares em que o andamento aparece — o nível 1 ("O que fazer
agora"), a matriz do "Andamento da seleção" e o "Próximo nesta lista".

## 1. A ordem de lista sem inscritos (FR-4670 a FR-4676)

| Lugar | Antes | Depois |
|---|---|---|
| Nível 1, da pessoa | Sua **Emitir a ordem** — Cefor · PPP | Sua **Emitir a ordem da lista sem inscritos, que declara que ninguém concorreu** — Cefor · PPP |
| Nível 1, de outro papel | Quem conduz a seleção: emitir a ordem — Cefor · PPP | Quem conduz a seleção: emitir a ordem da lista sem inscritos, que declara que ninguém concorreu — Cefor · PPP |
| Matriz, célula da ordem | ● Pendente | ● Pendente *lista sem inscritos* |
| Próximo nesta lista | Próximo nesta lista: **Emitir a ordem**. | Próximo nesta lista: **Emitir a ordem da lista sem inscritos, que declara que ninguém concorreu**. |

Duas listas vazias do mesmo marco: "Emitir as ordens das listas sem inscritos, que declaram que
ninguém concorreu — Cefor · PPP e PcD". Uma vazia e uma com inscritos: duas linhas.

**Sem mudança**: a lista com inscritos; a ordem vazia emitida (*Feito*, "ninguém concorreu"); a ordem
*Depois* ou *Impedida*; o sorteio.

## 2. O que foi divulgado (FR-4677 a FR-4680)

Nada muda na tela. A célula do resultado carrega `divulgado`, que a apresentação nova pode ler.

| Publicação vigente da lista | Situação (como hoje) | `divulgado` |
|---|---|---|
| nenhuma | *Pendente*, *Impedido*, *Depois* ou *Não se aplica* | `nada` |
| preliminar do ato vigente | *Pendente*, *Aguarda* ou *Impedido* (pela aferição do definitivo) | `preliminar` |
| preliminar, com a ordem obsoleta | *Depois* | `preliminar` |
| definitivo do ato vigente | *Feito* | `definitivo` |
| de um ato anterior | *Obsoleto* | a natureza dessa publicação |

## 3. A razão da espera do definitivo (FR-4681 a FR-4683)

Só com o preliminar do ato vigente publicado:

| Código da aferição | Razão no andamento, antes | Depois |
|---|---|---|
| `publication_window_open` | O prazo recursal deste marco ainda está aberto: ele se encerra em 14/11/2026 às 18h00. Aguarde o encerramento, ou publique como resultado preliminar | O prazo recursal deste marco ainda está aberto: ele se encerra em 14/11/2026 às 18h00. O resultado preliminar já está publicado, e o definitivo vem depois do encerramento |
| `publication_appeal_pending` | Há recurso pendente de julgamento sobre este marco: chamar de definitivo o que ainda está em disputa afirma o que não aconteceu. Aguarde o julgamento, ou publique como resultado preliminar | … afirma o que não aconteceu. O resultado preliminar já está publicado, e o definitivo vem depois do julgamento |

A prévia de publicação e a recusa do comando continuam com a mensagem de antes, palavra por palavra.
As outras razões não mudam.

## 4. A contagem do Perfil (FR-4684, FR-4685)

| Lugar | Antes | Depois |
|---|---|---|
| Resumo do Perfil | … · 1 providência em aberto | … · 1 providência em aberto nos marcos |
| Cartão "O que fazer agora" | 2 providências em aberto · 2 são suas | sem mudança |
