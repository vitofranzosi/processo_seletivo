# Data Model: O barema da Etapa (146)

Uma tabela nova, três colunas JSON em tabelas que já existem, um degrau canônico. Nenhuma tabela
append-only nova: o `M` do provisionamento continua 53.

## `CriterioAvaliacao` (nova, `editais`)

Elaboração — muda até publicar, como `EtapaAvaliacao`. Não é append-only.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | recebido e preservado na gravação (molde `CriterioDesempate`) |
| `etapa` | FK `EtapaAvaliacao`, `CASCADE` | a Etapa recriada pelo `replace_draft` recria os critérios |
| `ordem` | inteiro ≥ 0 | posição no formulário; único por Etapa |
| `nome` | texto ≤ 200 | obrigatório; único por Etapa |
| `descricao` | texto | opcional |
| `maxima` | `decimal(7,4)` | > 0 (CHECK) |
| `pontos_por_unidade` | `decimal(7,4)`, nulo | nulo = pontuação direta; > 0 e ≤ `maxima` (CHECK) |
| `unidade` | texto ≤ 60 | obrigatório se `pontos_por_unidade` (CHECK); vazio caso contrário |
| `documento` | UUID, nulo | `id` de `DocumentoExigido` do mesmo Edital, momento inscrição — UUID e não FK, porque o `replace_draft` apaga e recria os documentos |

Migration `editais/0027`. `test_migrations.py` passa a `editais: 27`.

## Conteúdo canônico — degrau 21

Cada item de `stages` ganha `criteria`:

```json
{"id": "…", "name": "Diploma de Doutorado", "description": "…", "maximumScore": "20.0000",
 "pointsPerUnit": "20.0000", "unitLabel": "diploma", "documentRequirementId": "…"}
```

Ordem da lista = ordem do critério. Ausência (versões ≤ 20) = `[]`, em `DEGRAUS[21]` de
`publicacoes/domain/elevacao.py` e em `diz_o_mesmo_que_a_ausencia`.

## Detalhamento (JSON)

Lista ordenada como o barema da versão:

```json
[{"criterionId": "…", "quantidade": 3, "pontos": null, "parcela": "10.0000",
  "limitada": true, "justificativa": ""}]
```

- `quantidade` (inteiro 0–9999) **xor** `pontos` (decimal), conforme a forma do critério; ambos nulos
  = pendente (só no rascunho).
- `parcela` e `limitada` são calculados pelo servidor e gravados, para que leitura antiga não dependa
  de recalcular sob regra que pode mudar.

| Onde | Coluna | Vazio (`[]`) quando |
|---|---|---|
| `avaliacoes.Avaliacao` | `criterios` JSON, default `[]` | Etapa sem barema |
| `avaliacoes.ConclusaoAvaliacao` | `criterios` JSON, default `[]` | idem; append-only como a linha |
| `recursos.DecisaoRecurso` | `criterios` JSON, default `[]` | espécie diferente de correção fixada, ou Etapa sem barema |

**Gatilho.** A migration `avaliacoes/0005` recria `reject_concluded_evaluation_mutation()` com
`AND NEW.criterios IS NOT DISTINCT FROM OLD.criterios` na lista da reabertura. Sem isso, um `UPDATE`
que reabre poderia trocar o detalhamento no mesmo ato.

**Invariante** (domínio, não banco — o banco não lê a versão): com barema, `pontuacao` = soma das
`parcela`; sem barema, `criterios = []`.

**Leitura.** O detalhamento guarda só `criterionId`, e não nome nem descrição. Quem o mostra lê os
critérios do conteúdo da versão que o ato cita — `ConclusaoAvaliacao.versao`, `ResultadoEtapa.versao`,
`DecisaoRecurso.versao`, as três já existentes —, e o rascunho lê os da vigente (D-011). `justificativa`
é sempre opcional (D-008).

## O que **não** muda

`ResultadoEtapa` (copia o total; o detalhamento se lê pela `avaliacao` ou pela `decisao` que ele já
referencia), `AtoDeOrdenacao`, `PosicaoNaOrdem`, `PublicacaoResultado`, `Recurso`, `DocumentoExigido`,
`DocumentoSubmetido`, permissões.
