# Contrato: Integridade do Snapshot Normativo

**Feature**: `005-integridade-do-snapshot` | **Fase**: 1 | **Data**: 2026-08-29

Este documento descreve **quando** a verificação acontece, **o que** ela confere e **como** a recusa
se apresenta. Ele não substitui o `openapi.yaml` da `001`, que continua sendo a fonte única da API:
a seção final lista o delta a aplicar lá.

A forma exigida não é declarada aqui: ela passa a estar no `openapi.yaml`, em `PerfilPublicado` e
`EventoPublicado`, esquemas de **saída** que esta feature acrescenta. Repeti-la aqui criaria uma
terceira cópia da mesma verdade. O que está em [data-model.md](../data-model.md) é a transcrição que
o domínio guarda, com o teste que a confere contra o contrato.

**Os esquemas de entrada não servem.** `PerfilInput` exige 5 dos 12 campos que o Perfil publicado
carrega; usá-lo deixaria `requirements`, `description`, `locality` e outros sem verificação — e um
Perfil reduzido aos cinco é exatamente o que a feature existe para impedir.

## Os dois momentos

| Momento | Sobre o quê | Pergunta |
| --- | --- | --- |
| Elaboração | O resultado de aplicar todas as alterações à versão declarada em `baseSnapshotId` | O que eu vi ficaria bem formado? |
| Publicação | **Cada** versão consolidada que o ato materializa, uma por fronteira de vigência | Tudo o que vai vigorar fica bem formado? |

A Publicação verifica de novo, e não por precaução: um ato pode chegar lá sem ter passado pela
elaboração — restaurado de backup, criado por importação, gravado direto. É a mesma razão pela qual
a `003` exige a precondição de conteúdo na Publicação mesmo tendo-a derivado na elaboração.

**Uma só fronteira malformada recusa o ato inteiro.** Publicar as fronteiras íntegras e omitir a
defeituosa produziria uma linha do tempo com buraco.

## O que se confere

Cinco dimensões, em cada Perfil e em cada Evento do conteúdo. Todas as violações são **erro
impeditivo** (FR-006):

| Dimensão | Violação |
| --- | --- |
| Presença | campo declarado obrigatório está ausente |
| Tipo | valor não é do tipo declarado — denominação como lista, vagas como texto, requisitos como texto |
| Nulabilidade | valor é nulo onde não se admite nulo |
| Formato | valor não satisfaz o formato declarado — `startAt` fora da forma canônica do instante |
| Restrição declarada | valor fora do que o contrato já escreve — vagas negativas, tipo de reserva fora da enumeração |

**Valor vazio admissível não é violação** (FR-007). Lista sem elementos continua sendo lista; texto em branco
onde o contrato admite texto continua sendo texto. É o que distingue "não preenchido" de
"malformado".

**Campo desconhecido não é violação** (FR-008). O conteúdo normativo pode crescer, e recusar o que o contrato
não declara tornaria toda evolução de esquema uma quebra.

## O que se decide **não** conferir

**Coerência entre campos.** `reserveLimit` compatível com o tipo de reserva, `endAt` posterior a
`startAt`, soma de vagas por modalidade — nenhuma dessas regras está escrita em lugar nenhum, e
escrevê-las aqui seria decidir por antecipação o que um Edital admissível é.

**A forma das Modalidades de Concorrência.** Conferidas como lista de objetos e nada mais. A
Publicação original também não as verifica, então a garantia desta feature não regride por isso —
mas ela também não as alcança, e isso está dito.

A linha entre aplicar e inventar é esta: **o que o contrato já escreve, aplica-se; o que ele não
escreve, não se escreve aqui.** Faixa e enumeração declaradas entram; coerência cruzada, não.

## A recusa

| Código | HTTP | Quando |
| --- | --- | --- |
| `blocking_findings` | 422 | O conteúdo resultante tem Perfil ou Evento malformado |

**Nenhum código novo no sistema, mas um a declarar no contrato.** `blocking_findings` já é a recusa
por erro impeditivo na Publicação do Edital e da Retificação, emitida em nove pontos do código —
mas o `openapi.yaml` nunca o nomeou. Como esta feature passa a produzi-lo num momento novo, ela o
declara. A natureza da recusa não mudou; mudaram o momento e o alcance.

A recusa **nomeia o caminho de cada campo em falta**, na gramática que a `004` estabeleceu:

```
/profiles/id=00000000-0000-0000-0000-000000000501/name
/schedule/id=00000000-0000-0000-0000-000000000521/startAt
```

Quem recebe identifica a entidade a corrigir sem consultar a versão vigente. Quando o item não tem
identificador utilizável — caso que a `004` já recusa na origem —, o caminho recua para a posição.

## O que a recusa na Publicação não deixa para trás

Nem Publicação, nem documento, nem versão consolidada (FR-012). Vale o que já vale para os demais erros
impeditivos: a operação é transacional e a recusa não produz efeito parcial.

## Delta a aplicar no `openapi.yaml` da `001`

1. **`criarRetificacao` e `atualizarRascunhoRetificacao`** — acrescentar à descrição que a resposta
   `422 blocking_findings` passa a alcançar o conteúdo resultante do ato, e não apenas a forma de
   cada alteração.
2. **`publicarRetificacao`** — acrescentar que a verificação incide sobre cada versão consolidada
   materializada, uma por fronteira de vigência, e que uma só malformada recusa o ato.
3. **`PerfilInput` e `EventoInput`** — acrescentar à descrição que estes esquemas passam a valer
   também como forma exigida do conteúdo **publicado**, nas dimensões de presença, tipo,
   nulabilidade e formato; `minimum` e `enum` seguem valendo apenas na entrada.
4. **Declarar `blocking_findings`** nas respostas `422` das operações que o produzem. O contrato
   nomeia `expected_hash_mismatch`, `target_already_present`, `inconsistent_consolidation` e os três
   da `004`, mas nunca nomeou este — e esta feature passa a emiti-lo num momento novo.
5. **Acrescentar `PerfilPublicado` e `EventoPublicado`** aos esquemas, com os campos canônicos, os
   tipos, a nulabilidade e as restrições. Reaproveitam o que `PerfilInput` e `EventoInput` declaram e
   completam o resto; os de entrada continuam descrevendo entrada.
6. **Nenhuma operação nova, nenhum campo novo em requisição ou resposta.** A superfície da API não
   cresce; o que cresce é o que ela diz sobre o conteúdo que já publicava.

`precondition_missing` e `no_effective_change` também não aparecem no `openapi.yaml` — lacuna
anterior, anotada aqui e não fechada por esta feature.
