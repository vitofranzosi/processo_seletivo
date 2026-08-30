# Contrato: Integridade do Snapshot Normativo

**Feature**: `005-integridade-do-snapshot` | **Fase**: 1 | **Data**: 2026-08-29

Este documento descreve **quando** a verificação acontece, **o que** ela confere e **como** a recusa
se apresenta. Ele não substitui o `openapi.yaml` da `001`, que continua sendo a fonte única da API:
a seção final lista o delta a aplicar lá.

A forma exigida em si não é declarada aqui — ela já está no `openapi.yaml`, em `PerfilInput` e
`EventoInput`, e repeti-la criaria uma terceira cópia da mesma verdade. O que está em
[data-model.md](../data-model.md) é a transcrição que o domínio guarda, com o teste que a confere.

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

Quatro dimensões, em cada Perfil e em cada Evento do conteúdo:

| Dimensão | Violação |
| --- | --- |
| Presença | campo declarado obrigatório está ausente |
| Tipo | valor não é do tipo declarado — denominação como lista, vagas como texto |
| Nulabilidade | valor é nulo onde o contrato não admite nulo |
| Formato | valor não satisfaz o formato declarado — `startAt` que não é data-e-hora |

**Valor vazio admissível não é violação** (FR-007). Lista sem elementos continua sendo lista; texto em branco
onde o contrato admite texto continua sendo texto. É o que distingue "não preenchido" de
"malformado".

**Campo desconhecido não é violação** (FR-008). O conteúdo normativo pode crescer, e recusar o que o contrato
não declara tornaria toda evolução de esquema uma quebra.

## O que se decide **não** conferir

O contrato declara `minimum` e `enum` para alguns campos. Esta feature não os verifica: são regra de
negócio, e decidir o que um Perfil deve exigir é discussão normativa e não de integridade.

**Consequência declarada**: depois desta feature, um Perfil com `immediateVacancies: -3` continua
publicável. A garantia é sobre a **forma** do conteúdo, não sobre a admissibilidade dos valores.

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
5. **Nenhuma operação nova, nenhum campo novo.** A superfície da API não cresce; o que cresce é o
   que ela diz sobre o que já fazia.

### Lacuna anterior, registrada e não fechada aqui

`precondition_missing` e `no_effective_change` também não aparecem no `openapi.yaml`. São recusas que
o sistema emite e o contrato não descreve. Não são desta feature — ficam anotadas para quem for
fechar a conformidade de códigos de erro.
