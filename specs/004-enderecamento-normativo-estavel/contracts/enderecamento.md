# Contrato: Gramática do Endereçamento Normativo

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 1 | **Data**: 2026-08-29

Este documento é o contrato da **gramática** de `targetPath` e dos códigos de recusa. Ele não
substitui o `openapi.yaml` da `001`, que continua sendo a fonte única da API: a seção final lista o
delta a aplicar lá.

A gramática mora aqui porque OpenAPI não a expressa — `targetPath` é `string` para o schema, e a
regra que importa (qual forma de segmento vale depende do contêiner) não é capturável por `pattern`.
E ela precisa estar escrita: quem audita um ato publicado tem de saber como o caminho foi resolvido
(FR-017).

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
           | indice          ; quando o contêiner é lista — recusado onde há chave
           | "-"             ; quando o contêiner é lista — acréscimo ao fim
           | seletor         ; quando o contêiner é lista

seletor    = "id=" uuid

uuid       = 8HEXDIG "-" 4HEXDIG "-" 4HEXDIG "-" 4HEXDIG "-" 12HEXDIG
indice     = "0" / ( %x31-39 *DIGIT )
chave      = *( %x20-7E )        ; nome literal, com o escape do RFC 6901
```

**A regra do contêiner é normativa.** Um segmento `id=algo` sobre um **objeto** é nome de chave
literal, não seletor. É o que garante que a extensão não retire expressividade do RFC 6901.

**Comparação**: o `uuid` é comparado como texto exato, sem normalização de caixa. O seletor não
aceita identificador de outra natureza.

## Onde cada forma é admitida

| Forma | Admitida |
| --- | --- |
| `chave` em objeto | sim |
| `indice` em coleção **com** chave | **não** — `positional_addressing_refused` |
| `indice` em coleção **sem** chave | não se aplica: a coleção é atômica |
| `-` | sim, e **só** em `ADD` |
| `id=<uuid>` | sim, em `REPLACE` e `REMOVE`; **não** em `ADD` |

**Inserção em posição específica não existe nesta gramática**: acréscimo é ao fim. Em lista, `ADD`
aceita `-` e nada mais — um seletor resolveria a posição de um item existente e inseriria antes
dele, que é justamente a operação que esta feature retirou. A recusa é `invalid_change`, salvo
quando a folha é índice: aí a resposta é `positional_addressing_refused`, porque a forma errada
já tem código próprio.

## A identidade é substrato, não conteúdo

O `id` de uma entidade é o que faz um caminho já publicado nomeá-la sem consultar a versão vigente
(FR-018). Ele não é conteúdo normativo alterável, e três regras decorrem disso. Todas valem sobre o
**resultado** de cada alteração, e não sobre o valor de uma operação em particular — a mesma
entidade sem chave entrava por `ADD`, por `REPLACE` do Perfil inteiro, por `REPLACE` ou `REMOVE` do
campo `id`, e por `REPLACE` de `/profiles` de uma vez.

| Regra | Recusa |
| --- | --- |
| Toda coleção declarada continua sendo uma coleção | `invalid_change` |
| Todo elemento de coleção com chave carrega `id` UUID | `invalid_change` |
| O `id` de um elemento de coleção com chave não é endereçável | `invalid_change` |
| A topologia das identidades só muda onde o ato a endereça | `invalid_change` |

A última é a regra geral, e as anteriores são casos dela vistos de perto. **Uma entidade só
aparece por `ADD /colecao/-` e só desaparece por `REMOVE /colecao/id=<uuid>`**; nenhuma outra
alteração cria ou destrói identidade, nem a da entidade endereçada nem a das que estiverem dentro
dela. Isso recusa trocar `/profiles` inteiro por outras entidades, reescrever um Perfil preservando
o `id` dele mas apagando as Modalidades de dentro, e esvaziar uma coleção aninhada de uma vez.

Reescrever uma entidade inteira continua sendo admitido, desde que as identidades dentro dela
permaneçam. Reordenar uma coleção também: ordem é conteúdo normativo, identidade não.

**A regra vale sobre a coleção, e não sobre a aparência do caminho.** Um segmento `-` ou
`id=<uuid>` sobre um objeto é nome de chave literal (FR-002) e não concede permissão nenhuma de
mexer na topologia.

**Na Publicação, quem recusa é a precondição por hash.** Um `REPLACE` de entidade inteira carrega
o hash do que estava à vista; se outra Retificação acrescentou algo dentro dela no intervalo, o
hash já não confere e a recusa é `expected_hash_mismatch` — precisa, e não um erro genérico de
composição.

**O que esta regra não cobre.** Ela vigia identidades, não a forma dos campos. Duas portas
distintas produzem um Perfil mutilado e nenhuma é recusada:

```
REPLACE /profiles/id=<uuid>   com {"id": "<uuid>", "code": "X"}   ← omite os demais campos
REMOVE  /profiles/id=<uuid>/name                                  ← apaga um campo obrigatório
```

A segunda não tem `newValue`, e por isso **validar o valor de cada alteração não fecharia a
família**. Uma sequência de alterações individualmente plausíveis também pode terminar inválida.
O que fecha é validar o **snapshot resultante** contra o schema canônico: depois de aplicar todas
as alterações, na elaboração, e de novo sobre o conteúdo consolidado, na Publicação. Validar cada
valor contra o subschema do seu caminho continua valendo, para errar cedo e com precisão, mas
como complemento e não como substituto.

Hoje `validate_for_publication` verifica quatro condições na raiz — título, ao menos um Perfil, ao
menos um Evento, descrição — e nada sobre a forma de cada Perfil ou Evento. É defeito anterior a
esta feature e vale para qualquer caminho de escrita.

`normativeRule` tem `id` e **não** é elemento de coleção — o `id` dela é conteúdo comum e continua
endereçável.

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

No mesmo vocabulário da `003`. Cada um **nomeia o caminho envolvido**, como faz
`expected_hash_mismatch`.

| Código | HTTP | Quando | Momento |
| --- | --- | --- | --- |
| `positional_addressing_refused` | 422 | O caminho usa índice numérico em coleção com chave | Elaboração |
| `target_key_not_found` | 409 | A entidade endereçada não existe | Elaboração e Publicação |
| `duplicate_key_in_collection` | 409 | Alguma alteração deixaria chave repetida na coleção | Elaboração e Publicação |

Os códigos da `003` continuam valendo sem alteração: `expected_hash_mismatch`,
`precondition_missing`, `no_effective_change`, `inconsistent_consolidation`, `blocking_findings`.

`target_identity_mismatch` **sai** junto com a âncora (FR-015): ele respondia "ainda é esta
entidade?", pergunta que o caminho por chave passa a responder sozinho.

## Os dois momentos

Recusar na elaboração e verificar na Publicação são perguntas diferentes, como a `003`
estabeleceu:

- **Elaboração** — contra a versão declarada em `baseSnapshotId`: "existe no que eu vi?"
- **Publicação** — contra o conteúdo vigente no início da vigência declarada: "ainda existe quando
  meu ato passa a valer?"

`positional_addressing_refused` é exceção: só faz sentido na elaboração, porque impede o ato de
nascer.

**A unicidade é verificada depois de cada alteração, não só no estado final.** Acrescentar um item
com a chave de outro e remover o original em seguida termina com a coleção íntegra — mas no instante
do acréscimo a chave já existia, e o que se publicou foi a troca de uma entidade por outra sob o
mesmo identificador. A ordem inversa, remover e recriar, é ato declarado e continua admitida.
Repetição que já exista na base não é imputada ao ato que a encontrou: imputá-la travaria inclusive
a Retificação que a corrige.

## Delta a aplicar no `openapi.yaml` da `001`

1. **`ChangeInput.targetPath`** — trocar a descrição para apontar esta gramática, declarando que é
   extensão local do RFC 6901 e que a forma posicional não é aceita onde há chave.
2. **`ChangeInput.operation`** — documentar que `ADD` usa `-`, e não admite índice numérico.
3. **Respostas de `criarRetificacao`, `atualizarRascunhoRetificacao` e `publicarRetificacao`** —
   acrescentar os três códigos novos às respostas `409` e `422` já declaradas, e remover
   `target_identity_mismatch`.
4. **Nenhuma operação nova, nenhum caminho novo.** A superfície da API não cresce; o que muda é o
   conteúdo admissível de um campo que já existe.
