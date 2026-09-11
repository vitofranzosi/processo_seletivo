# Modelo de dados — 014 · Corte e Progressão entre Etapas

Duas entidades novas, um campo novo e um degrau de schema. Nada é removido, nada é reescrito.

---

## 1. A regra, no marco publicado

`MarcoClassificatorio.regra_de_corte` — `JSONField(default=dict, blank=True)`, em
`editais/models/perfis.py`, ao lado de `janela_recursal` e `metodo_do_sorteio`.

**Vazio significa não declarada**, e não "corta por regra padrão": o marco sem regra não corta, e a
Etapa seguinte continua recebendo o que a progressão já entrega hoje (`FR-214`).

### A forma publicada

```json
"cutRule": {
  "targetKind": "FIXED" | "FROM_VACANCY_TABLE",
  "targetCount": 10,
  "surplusCount": 20,
  "tieOutcome": "ADMITS_SURPLUS" | "STRICT"
}
```

| Campo | Regra |
|---|---|
| `targetKind` | obrigatório quando `cutRule` existe |
| `targetCount` | inteiro ≥ 0, obrigatório em `FIXED`, **recusado** em `FROM_VACANCY_TABLE` |
| `surplusCount` | inteiro ≥ 0; ausente lê-se `0`, e zero é valor legítimo |
| `tieOutcome` | obrigatório sempre; a ausência impede a publicação (`FR-182`) |

### Onde ela é validada

| Momento | O que recusa |
|---|---|
| elaboração (`editais/domain/perfis.py`) | forma malformada, `targetCount` nos dois lugares, inteiro negativo |
| publicação (`editais/domain/validation.py`) | `tieOutcome` ausente; `FROM_VACANCY_TABLE` sem linha de quadro para o recorte; dois marcos com regra governando a mesma Etapa |
| Retificação | pela gramática de campo que `appealWindow` já usa, endereçada por identidade do marco |

---

## 2. `Corte` — o ato emitido

Em `classificacao/models.py`, ao lado do `AtoDeOrdenacao`, e append-only pelas três camadas que a
`015` estabeleceu: `save()` que recusa alteração, `delete()` que levanta, privilégio ausente no papel
de runtime e trigger no banco.

| Campo | Tipo | Papel |
|---|---|---|
| `id` | UUID | identidade estável |
| `edital` | FK `PROTECT` | o Edital |
| `perfil_id` | UUID | identidade publicada, não FK — Retificação acrescenta e remove sem tocar no rascunho |
| `marco_id` | UUID | idem |
| `lista_id` | UUID nulo | a lista de concorrência; **nulo é a ampla concorrência**, e não ausência |
| `ato` | FK `PROTECT` para `AtoDeOrdenacao` | a ordem que este corte leu |
| `versao` | FK `PROTECT` para `VersaoConsolidada` | a norma que o governou |
| `universo` | JSON | regra congelada, alvo apurado e sua origem, faixa anterior — ver §4 |
| `corte_anterior` | FK `self` nula | **sucessão**: este substitui aquele |
| `faixa_anterior` | FK `self` nula | **continuação**: este começa onde aquele parou |
| `motivo` | texto | obrigatório em sucessão e em continuação |
| `primeira_posicao` | inteiro | onde a faixa começa — **leitura, não critério** |
| `ultima_posicao` | inteiro nulo | a última posição alcançada; nula quando ninguém foi alcançado |
| `emitido_por` | texto | o ator |
| `emitido_em` | datetime | o instante |

### Constraints

```
uq_corte_raiz_por_marco            UNIQUE(edital, perfil_id, marco_id)
                                   WHERE corte_anterior IS NULL AND faixa_anterior IS NULL
                                     AND lista_id IS NULL
uq_corte_raiz_por_marco_e_lista    UNIQUE(edital, perfil_id, marco_id, lista_id)
                                   WHERE corte_anterior IS NULL AND faixa_anterior IS NULL
                                     AND lista_id IS NOT NULL
uq_corte_sucessor_unico            UNIQUE(corte_anterior) WHERE corte_anterior IS NOT NULL
uq_corte_continuacao_unica         UNIQUE(faixa_anterior) WHERE faixa_anterior IS NOT NULL
ck_corte_sucessao_ou_continuacao   NOT (corte_anterior IS NOT NULL AND faixa_anterior IS NOT NULL)
ck_corte_com_motivo                corte_anterior IS NULL AND faixa_anterior IS NULL
                                     OR motivo <> ''
```

**As duas primeiras não são redundantes**: no PostgreSQL dois `NULL` não colidem, e uma constraint só
deixaria passar duas raízes de ampla concorrência no mesmo marco. É a mesma cirurgia de
`uq_ato_raiz_por_marco`, e pela mesma razão.

**Vigente é o corte que ninguém sucedeu** — não há coluna de vigência, porque uma coluna assim exigiria
`UPDATE` numa tabela que o papel de runtime não pode atualizar. Uma **continuação não sucede**: as
duas ficam vigentes ao mesmo tempo, e é disso que a `FR-202` depende.

---

## 3. `ItemDoCorte` — o participante considerado

Uma linha por participante do ato de ordenação, e não apenas pelos que progrediram (`FR-194`).
Append-only pelas mesmas três camadas.

| Campo | Tipo | Papel |
|---|---|---|
| `id` | UUID | identidade |
| `corte` | FK `CASCADE` | o ato |
| `inscricao` | FK `PROTECT` | quem |
| `posicao` | inteiro nulo | a posição que tinha na ordem; nula para quem não a tinha |
| `consequencia` | texto | `PROGREDIU` \| `FORA_DA_FAIXA` — **duas**, e só duas |
| `motivo` | texto | a causa em linguagem legível |
| `excedente_por_empate` | booleano | entrou além do alvo por `ADMITS_SURPLUS` |

```
uq_item_por_corte_inscricao   UNIQUE(corte, inscricao)
ix_item_corte_consequencia    INDEX(corte, consequencia)
ix_item_inscricao             INDEX(inscricao)          -- a junção da prontidão
```

**Quem não tinha posição na ordem não ganha uma terceira consequência.** Eliminado na própria Etapa
do marco, ou não classificável, ele entra como `FORA_DA_FAIXA` com `posicao` nula e o `motivo` que a
ordem já dizia — *"considerado sem posição na ordem"*. A `FR-194` enumera duas consequências, e um
terceiro valor aqui faria o modelo contradizer a spec; o que distingue o caso é a posição nula, que
já é dado, e não um enum a mais.

**As duas posições não são o critério da faixa.** O alvo conta **pessoas**, e a numeração pula as
posições que um grupo empatado consome (`1, 1, 3`) — "os dez primeiros" pode terminar na posição nove
com dez pessoas dentro. Quem decide quem está na faixa é o conjunto de itens com `PROGREDIU`; as duas
colunas existem para que a leitura do ato não precise contá-los.

---

## 4. O universo declarado

O que o corte congela, e contra o que a obsolescência compara:

```json
{
  "editalId": "…", "profileId": "…", "milestoneId": "…", "listId": null,
  "orderingActId": "…", "versionId": "…",
  "cutRule": { "targetKind": "…", "targetCount": 10, "surplusCount": 20, "tieOutcome": "STRICT" },
  "target": { "count": 10, "source": "FIXED" },
  "surplus": 20,
  "previousCutId": null
}
```

Em alvo derivado, `target` carrega a origem inteira:

```json
"target": { "count": 40, "source": "VACANCY_TABLE_ROW", "rowId": "…" }
```

**`rowId` não é decoração.** Sem ele, retificado o quadro, não há como dizer se **aquele** corte ficou
para trás: a quantidade sozinha não identifica a linha de onde veio. É o mesmo motivo pelo qual o ato
de ordenação guarda a versão e não só a regra.

---

## 5. O degrau 13

```python
DEGRAUS_DE_MARCO = {
    8: {"appealWindow": None},
    10: {"drawMethod": None},
    13: {"cutRule": None},
}
```

`SCHEMA_VERSION` 12 → 13. `None` é **verdade** sobre todo Edital publicado antes: a capacidade não
existia, e nenhum deles declarou regra de corte. Conversão sem invenção, como nos dois degraus
anteriores do mesmo objeto.

---

## 6. As transições

O corte não tem máquina de estados, e a ausência é decisão: vigência e obsolescência são **derivadas**,
e gravá-las exigiria `UPDATE` numa tabela append-only.

```
(nada)  ──emitir──▶  raiz vigente
                        │
                        ├──suceder (motivo)──▶  sucessor vigente; a raiz fica sucedida
                        │
                        └──continuar (motivo)─▶  continuação vigente; a anterior CONTINUA vigente
```

| Pergunta | Como é respondida |
|---|---|
| este corte é vigente? | ninguém aponta para ele em `corte_anterior` |
| este corte é obsoleto? | comparação do `universo` com o estado atual — as quatro causas da `R-011` |
| esta inscrição progrediu? | existe `ItemDoCorte` com `PROGREDIU` em algum corte vigente do marco |

---

## 7. Invariantes persistidos

| Invariante | Onde é garantido |
|---|---|
| um corte raiz por recorte | constraint parcial, em duas metades |
| um sucessor por corte, uma continuação por faixa | duas constraints parciais |
| sucessão e continuação não coexistem na mesma linha | `CheckConstraint` |
| sucessão e continuação têm motivo | `CheckConstraint` |
| um item por inscrição em cada corte | `UNIQUE` |
| nada é alterado nem apagado | `save()`, `delete()`, privilégio ausente e trigger |
| o corte cita uma ordem que existe | `FK PROTECT` para `AtoDeOrdenacao` |
