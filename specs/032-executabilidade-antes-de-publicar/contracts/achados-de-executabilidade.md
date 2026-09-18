# Contrato — achados de executabilidade

A validação de conteúdo é lida por três consumidores: a etapa de Revisão do assistente, a recusa da
submissão e o relatório de publicabilidade da API. Este contrato registra os quatro achados novos.

## Regra que governa tudo abaixo

**A forma do achado não muda.** `severity`, `code`, `message`, `path` — os quatro campos são os de
sempre, e a classificação continua sendo a do Princípio IV: informação, aviso, erro impeditivo.
Consumidor que hoje lê a lista continua lendo, e ganha itens.

**Nenhum código existente muda de severidade.** Um achado que hoje é aviso e amanhã impede quebraria
Edital em elaboração de terceiros sem que requisito nenhum peça isso.

---

## Os quatro achados

### `profile_without_milestone` — `BLOCKING_ERROR` · `FR-457`

```jsonc
{
  "severity": "BLOCKING_ERROR",
  "code": "profile_without_milestone",
  "message": "O Perfil 'Professor de Informática' não declara marco classificatório algum: sem marco ninguém é classificado por ele. Declare ao menos um na etapa Classificação.",
  "path": "/profiles/id=…/classificationMilestones"
}
```

Emitido **somente** quando `ato == "publicacao"`.

### `milestone_without_cut_rule` — `WARNING` · `FR-461`

```jsonc
{
  "severity": "WARNING",
  "code": "milestone_without_cut_rule",
  "message": "O marco CLASS-TUT não declara regra de corte. Sem corte não há geração, sem geração não há faixa, e sem faixa não há convocação: este marco classifica e não convoca. Declare a regra na etapa Classificação — ela pode declarar que não governa Etapa alguma.",
  "path": "/profiles/id=…/classificationMilestones/id=…/cutRule"
}
```

**Não é emitido** quando `cutRule` existe e declara não governar Etapa alguma (`FR-224` da `014`).
Essa declaração é legítima e produz faixa; cobrá-la seria falso positivo no Edital 69/2026.

### `drawn_milestone_without_method` — `BLOCKING_ERROR` · `FR-467`

```jsonc
{
  "severity": "BLOCKING_ERROR",
  "code": "drawn_milestone_without_method",
  "message": "O marco SORT-X ordena por sorteio e não publica método — nem próprio, nem comum a este Edital. Sem o método publicado ninguém consegue conferir o sorteio contra a norma. Declare-o na etapa Classificação.",
  "path": "/profiles/id=…/classificationMilestones/id=…/drawMethod"
}
```

Emitido **somente** quando `ato == "publicacao"`. É distinto de `draw_method_invalid`, que já existe
e trata do método **declarado pela metade**; este trata da **ausência**.

### `reserved_row_without_ordering` — `WARNING` · `FR-470`

```jsonc
{
  "severity": "WARNING",
  "code": "reserved_row_without_ordering",
  "message": "O Perfil 'Professor de Informática' publica 1 vaga(s) para 'Pessoas com deficiência' e 2 para 'Negros', e o marco CLASS-TUT produz uma ordem única: só a ordem sorteada é emitida por recorte. A ocupação e a convocação desses recortes acontecerão fora do sistema.",
  "path": "/profiles/id=…/vacancyTable"
}
```

**É aviso, e não impedimento** — decisão registrada na `spec.md`, história P3. É irmão de
`vacancy_reserved_list_without_row`, que trata do caso em que **falta a linha**; este trata do caso
em que a linha existe e o que falta é a ordem.

---

## O que a Revisão faz com cada um

O destino é resolvido pelo `path`, de trás para frente, contra o mapa que já existe. Nenhum dos
quatro precisa de exceção por código.

| Achado | Etapa | Âncora |
|---|---|---|
| `profile_without_milestone` | Classificação | `#titulo-classificacao` |
| `milestone_without_cut_rule` | Classificação | `#titulo-classificacao` |
| `drawn_milestone_without_method` | Classificação | `#titulo-classificacao` |
| `reserved_row_without_ordering` | Perfis de Vaga | a âncora do quadro |

---

## Leitura da ocupação — dois campos aditivos

O recorte, na leitura da tela e do contrato da `016`, ganha dois booleanos. **Nenhum valor novo em
`estado`**: quem lê os quatro continua lendo os quatro.

```jsonc
{
  "listaId": "…",
  "estado": "NOT_APPRAISED",
  "publicadas": 2, "efetivas": 2, "ocupadas": 0, "faltando": 2,
  "apuravel": false,          // NOVO — o marco não emite ordem neste recorte (FR-472)
  "faixaDisponivel": false    // NOVO — o marco não declara regra de corte (FR-463)
}
```

Consumidor que não conhece os campos novos vê exatamente o que via. O que muda é a tela: onde o
booleano é falso, **a razão ocupa o lugar do botão**.
