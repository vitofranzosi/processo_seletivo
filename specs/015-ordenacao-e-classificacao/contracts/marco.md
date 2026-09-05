# Contrato — o marco classificatório no conteúdo publicado

A coleção normativa nova, sua forma, onde ela é verificada e como a Retificação a alcança.

## 1. Onde ela vive

`/profiles/*/classificationMilestones` — aninhada no Perfil, no molde de `competitionModalities`
(T-007). Emitida por `edital_snapshot` dentro do laço do Perfil
(`publicacoes/application/publish_edital.py:98-148`), ordenada por `code`.

## 2. A forma publicada

```
classificationMilestones: [
  {
    id, code, name,
    stages: [ <uuid da Etapa>, ... ],      # enumeração; a ordem aqui não é normativa
    operation, normalization, rounding,     # como as pontuações se combinam
    tiebreakers: [                          # emitida ordenada por `order`
      { id, order, type, parameters, whenMissing }
    ]
  }
]
```

**Convenções que a casa já fixou e que valem aqui:** texto ausente é `""`, nunca `null` e nunca
chave omitida (`publish_edital.py:137-140`); decimal é canônico de quatro casas via
`_decimal_canonico` (`publish_edital.py:28-35`); **todo campo publicado é obrigatório** — o teste
`test_todo_campo_do_conteudo_publicado_e_obrigatorio`
(`tests/contract/test_forma_publicada.py:109-116`) recusa campo opcional no publicado.

**A ordem é campo, e não posição.** `order` é publicado em cada critério, único dentro do marco, e a
lista é emitida ordenada por ele — como `stages` já faz. A razão é a Retificação: o catálogo endereça
por identidade (`id=`), nunca por índice, e reordenar substituindo a lista inteira perderia as
identidades que a própria Retificação usa. Reordenar é, portanto, alterar `order` de cada critério
por identidade, e os identificadores são preservados (FR-015).

## 2b. Os fatos declarados e o teto (D-2 e D-3)

A mesma elevação carrega mais duas mudanças de forma, e elas são contrato como o marco é.

`/profiles/*/declaredFacts` — aninhada no Perfil, coleção com chave:

```
declaredFacts: [
  { id, code, label, type }          # type: "DATE" | "INTEGER", e nada além
]
```

`maxInscricoesPorCandidato` — campo **da raiz do snapshot**, ao lado de `number`, `year` e `title`,
inteiro ou `null`. É do Edital porque limita o **total** de inscrições da pessoa no certame; no
Perfil ele seria redundante com a unicidade `(identidade, edital, perfil)` que já existe. `null`
significa sem limite, e a ausência da chave não é forma válida, pela convenção de que todo campo
publicado é obrigatório.

Sendo campo de raiz, ele é o **único** dos três que a elevação 6→7 resolve no nível superior — os
outros dois descem para dentro de `profiles`.

**O que a validação recusa:** fato sem `code` único no Perfil; `type` fora dos dois valores; critério
de desempate que aponte fato inexistente no mesmo conteúdo (FR-017); teto negativo ou zero.

**O que a Retificação alcança:** `label` e o teto, por identidade. **`type` não é editável** — mudar
o tipo remove um fato e acrescenta outro (FR-058), porque reinterpretar valor já congelado seria o
sistema decidindo o que a pessoa quis dizer.

## 2c. A forma de `rounding`, exata

```
rounding: { "scale": <inteiro 0..4>, "mode": "MEIO_PARA_CIMA" | "MEIO_PARA_PAR" | "TRUNCAR" }
```

**`scale`** é o número de casas decimais da pontuação combinada. O intervalo é **0 a 4**: zero
porque há Editais que classificam por pontuação inteira, e quatro porque é a precisão que
`ResultadoEtapa.pontuacao` carrega — `decimal_places=4`. Publicar escala maior prometeria precisão
que a entrada não tem.

> Uma redação anterior dizia **0 a 6** e justificava o seis como "a precisão que a pontuação já
> carrega". Era falso: a entrada tem quatro casas. Seis seria um regime de precisão **novo** para o
> valor derivado — decisão legítima, mas que a clarificação não tomou e que obrigaria
> `PosicaoNaOrdem.pontuacao_combinada` a suportar seis. O intervalo segue o regime que existe.

**`mode`** tem três valores canônicos, e a grafia é a publicada, não a da biblioteca:

| Publicado | Significa | No domínio |
|---|---|---|
| `MEIO_PARA_CIMA` | 2,5 vira 3 — o arredondamento que a maioria dos Editais descreve | `ROUND_HALF_UP` |
| `MEIO_PARA_PAR` | 2,5 vira 2 e 3,5 vira 4 — o que não enviesa uma população | `ROUND_HALF_EVEN` |
| `TRUNCAR` | 2,9 vira 2 — corta sem olhar o que vem depois | `ROUND_DOWN` |

**Quando se aplica:** uma vez, **depois** da operação e da normalização, sobre a pontuação
combinada final. Nunca sobre as parcelas (FR-069). A diferença não é teórica — arredondar parcelas
e arredondar o total dão resultados distintos, e num lugar onde a pontuação decide quem passa.

**O que a validação recusa na publicação, e não no cálculo:**

- marco cuja operação não declare `rounding`;
- `scale` ausente, não inteiro, ou fora de 0..4;
- operação que divide pela soma dos pesos quando essa soma é **zero** — regra sem divisor não é
  regra incompleta do participante, é regra inválida do Edital, e o lugar de recusá-la é a
  publicação;
- `mode` ausente ou fora dos três valores canônicos.

Recusar aqui é o que impede o cálculo de escolher um padrão. Um marco sem arredondamento declarado
publicaria uma regra que só fica completa no dia em que alguém a executa — e aí o padrão seria do
código, não do Edital (FR-068).

## 3. Endereçamento

Entra em `COLECOES_COM_CHAVE` (`publicacoes/domain/colecoes.py:18-30`):

```
"/profiles/*/classificationMilestones"
"/profiles/*/classificationMilestones/*/tiebreakers"
"/profiles/*/declaredFacts"
```

Sem a declaração, `changes.py:144-149` recusa endereçamento por `id=` e o caminho só resolveria por
posição — que é exatamente o que o sistema proíbe. O guarda que pega o esquecimento é
`tests/integration/publicacoes/test_enderecamento.py:249-250`, sobre um snapshot realmente publicado.

## 4. Verificação na publicação

Função dedicada registrada em `validate_for_publication`, no molde de `_faixa_do_percentual`
(`editais/domain/validation.py:441-481`, registrada em `:627-633`). **Não** cabe em
`COLECOES_PUBLICADAS`, que só percorre coleções de raiz (T-009).

| Recusa | Requisito |
|---|---|
| marco que enumera Etapa inexistente no mesmo conteúdo | FR-016 |
| marco que enumera Etapa não classificatória | FR-010 |
| critério que aponta Etapa ou fato inexistente | FR-016 |
| critério sem `whenMissing` declarado | FR-017 |
| dois critérios do mesmo marco com a mesma `order` | FR-015, `uq_criterio_marco_ordem` |
| Retificação que remove Etapa enumerada sem ajustar o marco | FR-043 — é aqui que o critério pendurado é impedido, e por isso ele não é estado a tratar depois |

Os pesos **não** são verificados quanto a somar 1 (FR-012): a normalização declarada pela operação é
que responde por isso.

## 5. Elevação de versão

`SCHEMA_VERSION` 6 → 7 (`shared/canonical.py:71`), com o incremento registrado no bloco de história
do próprio arquivo, no formato que a 012 usou.

`elevacao.DEGRAUS` ganha:

```
7: {"classificationMilestones": []}
```

com o significado declarado: **Edital publicado antes desta feature não declarou marco nenhum, e um
Edital sem marco não classifica.** É legítimo pela mesma régua que recusou 2→3 e 3→4
(`elevacao.py:8-14`).

**A parte que não é rotina:** `elevar()` hoje só reescreve `conteudo["stages"]`
(`elevacao.py:101-112`). Esta é a primeira elevação que precisa descer para dentro de `profiles`.
Enquanto isso não funcionar, todo conteúdo v6 publicado fica irretificável por
`canonical_schema_version_mismatch` (`publicacoes/application/retificacoes.py:542-543`).

## 6. Retificação

`CAMPOS_MARCO` e `CAMPOS_CRITERIO` em `interface/retificacao.py:41-100`, com laço aninhado dentro do
laço de Perfil (`retificacao.py:232-253`), montando
`f"{caminho}/classificationMilestones/id={marco['id']}"`. O caminho normativo não aparece no HTML —
`_referenciar` (`retificacao.py:203-219`) o troca por referência opaca, e o POST reconstrói.

Reordenar critérios é Retificação como outra qualquer: vale da vigência em diante, e zero atos
emitidos antes dela mudam (SC-012).

## 7. O que este contrato não cria

- regra de chamamento — `RegraNormativa.call_rules` continua reservado e não consumido; é da 016;
- percentual, reserva ou matriz de vagas;
- barema, critério ou item de pontuação (D-4);
- qualquer campo em `stages`: `weight`, `order` e `classificatory` já existem e são lidos como estão.
