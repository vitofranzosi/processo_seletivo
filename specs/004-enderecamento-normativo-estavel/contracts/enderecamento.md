# Contrato: Gramática do Endereçamento Normativo

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 1 | **Data**: 2026-08-29

Este documento é o contrato da **gramática** de `targetPath` e dos códigos de recusa. Ele não
substitui o `openapi.yaml` da `001`, que continua sendo a fonte única da API: a seção final lista o
delta a aplicar lá.

A gramática mora aqui porque OpenAPI não a expressa — `targetPath` é `string` para o schema, e a
regra que importa (qual forma de segmento vale depende do contêiner) não é capturável por `pattern`.
E ela precisa estar escrita: quem audita um ato publicado tem de saber como o caminho foi resolvido
(FR-001b).

## Esta é uma extensão declarada

O RFC 6901 não tem seleção por atributo. Qualquer forma de endereçar por chave é semântica local —
inclusive usar o identificador como token cru, que **pareceria** padrão e não seria, porque resolver
um identificador dentro de um array também exige regra própria.

A escolha foi declarar a extensão em vez de disfarçá-la. Num campo que fica gravado para sempre no
ato publicado, dialeto que se esconde é pior que dialeto anunciado.

## Gramática

```
caminho    = *( "/" segmento )

segmento   = chave           ; quando o contêiner é objeto
           | indice          ; quando o contêiner é lista — só leitura
           | "-"             ; quando o contêiner é lista — acréscimo ao fim
           | seletor         ; quando o contêiner é lista

seletor    = "id="     valor
           | "before=" valor      ; só em ADD
           | "after="  valor      ; só em ADD

indice     = "0" / ( %x31-39 *DIGIT )
valor      = 1*( %x20-7E )       ; texto exato; "/" e "~" escapados como no RFC 6901
chave      = *( %x20-7E )        ; nome literal, com o mesmo escape
```

**A regra do contêiner é normativa.** Um segmento `id=algo` sobre um **objeto** é nome de chave
literal, não seletor. É o que garante que a extensão não retire expressividade do RFC 6901.

**Comparação**: o `valor` é comparado como texto exato. Sem normalização de caixa, sem interpretação
como UUID — qualquer identificador que a entidade carregue serve.

## Onde cada forma é admitida

| Forma | Escrita de ato novo | Leitura e consolidação |
| --- | --- | --- |
| `chave` em objeto | sim | sim |
| `indice` em coleção **com** chave | **não** — `positional_addressing_refused` | sim, permanentemente |
| `indice` em coleção **sem** chave | não se aplica: a coleção é atômica | sim, permanentemente |
| `-` | sim, em `ADD` | sim |
| `id=` | sim | sim |
| `before=` / `after=` | sim, em `ADD` | — |

A leitura aceita a forma posicional **para sempre**: atos publicados não são reescritos, então ela
permanece no histórico por consequência da imutabilidade, não por escolha.

## Coleções

| Coleção | Endereçamento |
| --- | --- |
| `/profiles` | por chave (`id`) |
| `/schedule` | por chave (`id`) |
| `/profiles/id=…/competitionModalities` | por chave (`id`) |
| `/profiles/id=…/requirements` | **atômica** — `REPLACE` da lista inteira, nunca item a item |

`normativeRule` é objeto e continua endereçada pelo nome da chave, ainda que carregue `id`.

Coleções de controle interno — `applied_publications` — não são endereçáveis.

## Códigos de recusa

No mesmo vocabulário da `003`. Cada um **nomeia o caminho envolvido**, como fazem
`expected_hash_mismatch` e `target_identity_mismatch`.

| Código | HTTP | Quando | Momento |
| --- | --- | --- | --- |
| `positional_addressing_refused` | 422 | Caminho novo usa índice numérico em coleção com chave | Elaboração |
| `target_key_not_found` | 409 | A entidade endereçada não existe | Elaboração e Publicação |
| `position_reference_not_found` | 409 | A referência de um `before=`/`after=` não existe; a posição pretendida deixou de ser determinável | Elaboração e Publicação |
| `duplicate_key_in_collection` | 409 | A coleção resultante teria chave repetida | Elaboração e Publicação |

Os códigos da `003` continuam valendo sem alteração: `expected_hash_mismatch`,
`precondition_missing`, `no_effective_change`, `inconsistent_consolidation`, `blocking_findings`.

`target_identity_mismatch` **sai** junto com a âncora (FR-009): ele respondia "ainda é esta
entidade?", pergunta que o caminho por chave passa a responder sozinho.

## Os dois momentos

Recusar na elaboração e verificar na Publicação são perguntas diferentes, como a `003`
estabeleceu:

- **Elaboração** — contra a versão declarada em `baseSnapshotId`: "existe no que eu vi?"
- **Publicação** — contra o conteúdo vigente no início da vigência declarada: "ainda existe quando
  meu ato passa a valer?"

`positional_addressing_refused` é exceção: só faz sentido na elaboração, porque impede o ato de
nascer.

## Delta a aplicar no `openapi.yaml` da `001`

1. **`ChangeInput.targetPath`** — trocar a descrição para apontar esta gramática, declarando que é
   extensão local do RFC 6901 e que a forma posicional não é aceita na escrita onde há chave.
2. **`ChangeInput.operation`** — documentar que `ADD` admite `-`, `before=` e `after=`, e não admite
   índice numérico.
3. **Respostas de `criarRetificacao`, `atualizarRascunhoRetificacao` e `publicarRetificacao`** —
   acrescentar os quatro códigos novos às respostas `409` e `422` já declaradas.
4. **Nenhuma operação nova, nenhum caminho novo.** A superfície da API não cresce; o que muda é o
   conteúdo admissível de um campo que já existe.
