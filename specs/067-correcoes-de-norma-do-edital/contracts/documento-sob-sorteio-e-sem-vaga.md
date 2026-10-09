# Contrato — o documento sob sorteio e sem vaga imediata (`FR-1311` a `FR-1324`)

## Marco

`declara_sorteio(marco)` é verdadeiro se, e só se, `marco.orderProduction == "POR_SORTEIO"`
(`D-004`).

| Linha do bloco do marco | Ordem por sorteio declarada | Ordem por pontuação declarada | Forma não declarada (acervo) |
|---|---|---|---|
| Ordem | sai | sai | não sai |
| Combinação, Normalização | não sai (como hoje) | sai | sai |
| **Arredondamento** | **não sai**, declarado ou não | sai | sai |
| Sorteio (bloco do método) | sai | não sai | como hoje |
| Recurso | sai, com o nome (`frase-de-recurso.md`) | idem | idem |
| Corte, Continuação | saem | saem | saem |
| **Empate no corte** | **não sai**, declarado ou não | sai | sai |
| Critérios de desempate | como hoje | como hoje | como hoje |

A Revisão segue a mesma tabela nas linhas em negrito.

## Validação do arredondamento

| Forma declarada | `rounding` ausente ou `{}` | `rounding` bem formado | `rounding` malformado |
|---|---|---|---|
| `POR_SORTEIO` | aceito | aceito | `milestone_rounding_invalid` (impeditivo) |
| `POR_PONTUACAO` ou ausente | `milestone_rounding_invalid` | aceito | `milestone_rounding_invalid` |

"Ausente ou `{}`" é: `rounding` ausente, nulo, ou objeto sem `scale` e sem `mode` (ambos nulos ou
ausentes).

## Perfil

`sem_vaga_imediata(perfil)` é verdadeiro se, e só se, `immediateVacancies` é o inteiro 0 (não
booleano), `vacancyTable` é lista não vazia, e toda linha tem `immediateVacancies` igual a 0
(`D-007`).

| Peça do Perfil | Sem vaga imediata | Com vaga imediata |
|---|---|---|
| linha na tabela de Perfis | sai, com 0 e o cadastro | sai |
| Tabela "Quadro de vagas" | **não sai** | sai, inclusive linhas em 0 |
| Frase de reversão | **não sai** | sai, se declarada |
| Forma de convocação | sai | sai |
| Tabela de Modalidades | sai, com percentual e fundamento | sai |
| Marcos | saem | saem |

`tabelas_do_documento(snapshot)` conta o quadro de um Perfil só quando ele sai.

## Revisão do Perfil sem vaga imediata

A linha "Reverter vaga reservada não preenchida para a ampla concorrência" continua, com o valor
escolhido, seguida de `— não sai no documento: o Perfil não tem vaga imediata` (`UX-192`).
