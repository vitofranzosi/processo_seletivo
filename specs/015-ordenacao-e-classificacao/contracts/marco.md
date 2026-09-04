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
    tiebreakers: [                          # a ORDEM aqui É normativa
      { id, type, parameters, whenMissing }
    ]
  }
]
```

**Convenções que a casa já fixou e que valem aqui:** texto ausente é `""`, nunca `null` e nunca
chave omitida (`publish_edital.py:137-140`); decimal é canônico de quatro casas via
`_decimal_canonico` (`publish_edital.py:28-35`); **todo campo publicado é obrigatório** — o teste
`test_todo_campo_do_conteudo_publicado_e_obrigatorio`
(`tests/contract/test_forma_publicada.py:109-116`) recusa campo opcional no publicado.

`tiebreakers` é a única lista do conteúdo publicado cuja **posição significa**. Isso é declarado
aqui e no `openapi.yaml`, e não presumido: aplicar critérios fora da ordem publicada é aplicar outra
regra.

## 3. Endereçamento

Entra em `COLECOES_COM_CHAVE` (`publicacoes/domain/colecoes.py:18-30`):

```
"/profiles/*/classificationMilestones"
"/profiles/*/classificationMilestones/*/tiebreakers"
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
| dois critérios com a mesma ordem | data-model, `uq_criterio_marco_ordem` |

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
