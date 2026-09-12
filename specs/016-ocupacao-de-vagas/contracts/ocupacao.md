# Contrato — a ocupação e a declaração que a governa

Dois contratos. O primeiro não é novo: a declaração da reversão entra no `openapi.yaml` da `001`,
nos **dois** lugares em que o Perfil aparece, como `vacancyTable` e `generalCompetitionModalityId`
já estão. O segundo é a leitura da apuração.

---

## 1. `vacancyReversion` no Perfil

### `PerfilInput` — o rascunho

```yaml
vacancyReversion:
  type: object
  nullable: true
  required: [kind]
  properties:
    kind:
      type: string
      enum: [ON_EXHAUSTION, ON_BALANCE]
      description: >
        Gatilho da reversão de vaga reservada para a ampla concorrência (016, D-007).
        ON_EXHAUSTION reverte só quando a lista reservada não tem mais ninguém a ocupar;
        ON_BALANCE reverte a quantidade não preenchida, ainda que a lista tenha gente.
```

### `PerfilOutput` — o publicado

A mesma forma. **Objeto `null` significa "este Edital não declara reversão"** — e portanto não
reverte. Não existe objeto pela metade: declarar reversão sem `kind` é recusado na publicação
(`FR-251`).

### Erros

| Código | Quando | Severidade |
|---|---|---|
| `vacancy_reversion_kind_required` | objeto presente sem `kind` | impeditivo |
| `vacancy_reversion_kind_unknown` | `kind` fora do enum | impeditivo |
| `vacancy_reversion_sem_quadro` | reversão declarada em Perfil sem `vacancyTable` | impeditivo |

O terceiro merece a razão: reverter pressupõe quantidade por recorte. Declarar reversão num Perfil
que não publicou quadro é regra inexequível — e regra publicada inexequível é o que a `014` já
recusou a publicar, ao exigir linha de quadro para todo recorte que o marco ordena.

### Degrau canônico 14

`SCHEMA_VERSION` 13 → 14. A conversão escreve `vacancyReversion: null` em todo Perfil de Edital
publicado antes do degrau, e a afirmação é verdadeira sobre todos eles: a capacidade não existia,
não havia onde declarar o gatilho. **Conversão sem invenção**, como os degraus 12 e 13.

### Retificação

Entrada em `CAMPOS_PERFIL` (`interface/retificacao.py:51`) com tipo **`REFERENCIA`** e uma lista
de opções — **não** caixa de texto. É o precedente literal do `cutRule/tieOutcome` da `014`
(`retificacao.py:113`), cujo comentário dá a razão: são valores fechados, e `REFERENCIA` *"os
oferece conferindo a escolha contra a lista"*, enquanto texto livre publicaria valor que o
cálculo não interpreta. As opções vão com as mesmas palavras da tela de composição:

```python
ESPECIES_DE_REVERSAO = (
    ("ON_EXHAUSTION", "Só quando a lista reservada esgota"),
    ("ON_BALANCE", "A quantidade que ficou sem preencher"),
)
```

E o rótulo do vazio precisa dizer o que o vazio provoca, como o do desfecho do empate já diz: sem
espécie, a reversão declarada não publica.

**Declarada antes da primeira emissão do snapshot**, pela lição que a `025` registrou em letras:
endereço de retificação não se conserta depois, porque publicação é ato imutável.

---

## 2. A leitura da apuração

### `GET /api/editais/{id}/ocupacao`

Devolve, por recorte, os três números e o estado da apuração vigente.

```yaml
OcupacaoPorRecorte:
  type: object
  required: [profileId, milestoneId, listId, published, occupied, remaining, state]
  properties:
    profileId:   { type: string, format: uuid }
    milestoneId: { type: string, format: uuid }
    listId:
      type: string
      format: uuid
      nullable: true
      description: "null = ampla concorrência, a mesma grafia da ordem e do corte"
    published:   { type: integer, minimum: 0, description: "da linha do quadro, nunca do total do Perfil" }
    occupied:    { type: integer, minimum: 0 }
    remaining:   { type: integer, minimum: 0 }
    movements:
      type: array
      items: { $ref: "#/components/schemas/MovimentoDeVaga" }
    state:
      type: string
      enum: [CURRENT, OBSOLETE, NOT_APPRAISED, NO_VACANCY_TABLE]
    obsolescenceCauses:
      type: array
      items: { type: string }
      description: "causas nomeadas, nunca 'divergências' (016, FR-263)"
```

**`state` tem quatro valores, e dois deles não são erro.** `NOT_APPRAISED` é recorte que ainda não
teve apuração emitida; `NO_VACANCY_TABLE` é Edital publicado antes do degrau 12, que **não** tem
quadro — e a `UX-032` proíbe exibir zero ali. Colapsar os dois em "0 vagas" é o defeito que esta
distinção existe para impedir.

```yaml
MovimentoDeVaga:
  type: object
  required: [kind, quantity, cause]
  properties:
    kind:            { type: string, enum: [QUOTA_REVERSION, CONCURRENT_RELEASE] }
    fromListId:      { type: string, format: uuid, nullable: true }
    toListId:        { type: string, format: uuid, nullable: true }
    quantity:        { type: integer, minimum: 1 }
    cause:           { type: string }
```

### `POST /api/editais/{id}/ocupacao/apuracoes`

Emite a apuração de um recorte. **Command explícito e idempotente**: exige
`Idempotency-Key`, como todo command irreversível deste sistema.

```yaml
EmitirApuracaoCommand:
  type: object
  required: [profileId, milestoneId]
  properties:
    profileId:   { type: string, format: uuid }
    milestoneId: { type: string, format: uuid }
    listId:      { type: string, format: uuid, nullable: true }
    reason:      { type: string, description: "obrigatório quando sucede uma apuração anterior" }
```

| Erro | Quando |
|---|---|
| `ordem_nao_vigente` | a ordem do recorte foi sucedida (`FR-243`) |
| `sem_quadro_publicado` | o Edital não publicou quadro (`FR-242`) |
| `recorte_sem_linha` | a lista ordena e não tem linha no quadro |
| `motivo_da_sucessao_obrigatorio` | há apuração anterior e falta o motivo |

### `POST /api/editais/{id}/ocupacao/faixa-seguinte`

Entrega o déficit apurado à `014` como causa da faixa seguinte (`FR-255`). **Este endpoint não
seleciona ninguém**: ele chama a emissão do corte da `014`, que é quem lê ordem e escolhe.

| Erro | Quando |
|---|---|
| `deficit_zero` | o déficit apurado é zero (`FR-256`) |
| `apuracao_obsoleta` | a apuração vigente está obsoleta (`FR-263`) |

### O que estes contratos deliberadamente não expõem

- **Nenhum campo de convocação, aceite, matrícula ou desistência.** Não existem antes da `019`
  (`FR-258`), e o vocabulário é verificado por varredura (`UX-034`).
- **Nenhum endpoint que ordene, desempate ou selecione** (`FR-257`).
- **Nenhuma entidade de persistência como contrato**, conforme a Constituição: `published`,
  `occupied` e `remaining` são DTO, e não colunas expostas.
