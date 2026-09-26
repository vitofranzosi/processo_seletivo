# Modelo — nada persiste, três coisas mudam de sentido

## Nenhuma entidade, nenhuma migration, nenhum conteúdo reescrito

A feature não cria tabela, não muda coluna e não toca linha. O total do `make preparar` continua
**`N de 34`**. O conteúdo canônico não ganha campo: as quatro declarações que a verificação lê —
`eliminatory`, `classificationMilestones[].stages`, `cutRule.governedStage` e
`drawMethod.qualifyingStageId` — já estão nele desde a `012`, a `014`, a `015` e a `021`.

**Os achados não são estado.** A validação continua sendo função pura do conteúdo, do ato e do
instante; nada dela é gravado, e o hash do conteúdo não muda.

## O que muda de sentido

| Onde | Antes | Depois |
|---|---|---|
| Etapa que a regra da consolidação recusa (`resultados/domain/regra.py`) | publicável sem achado; a recusa aparecia só na Mesa, depois do ato | **impeditivo** se o Resultado é exigido; **aviso** se não é; **advertência** na Retificação (`FR-746`, `FR-748`, `FR-751`) |
| Ausência de `cutRule` em todos os marcos de um Perfil | um aviso por marco (`032`, `FR-461`) | **impeditivo** por Perfil, sem os avisos por marco (`FR-752`, `FR-753`) |
| Pendências de publicação de um Edital fora da elaboração | calculadas sobre o relacional e exibidas | **não calculadas** (`FR-755`) |
| Vocabulário de fontes do sorteio | fixo, com a demonstração, em todo ambiente | **por ambiente**: sem a demonstração em produção (`FR-757`) |

## A configuração nova

| Nome | Onde | Valor |
|---|---|---|
| `SORTEIO_FONTE_DE_DEMONSTRACAO` | `config/settings/base.py` | lido do ambiente; **falso** se ausente |
| | `config/settings/development.py`, `config/settings/test.py` | `True`, fixo |
| | `config/settings/production.py` | verdadeiro **recusa o boot** (`FR-758`) |

Não entra no `.env.example`: desenvolvimento a liga pelo módulo (`R-6`).

## O acervo

Nenhum Edital publicado muda. Os impeditivos novos só existem no ato de publicação. O único efeito
sobre o acervo é o da fonte de demonstração, e só em produção: um Edital que a declare deixa de
sortear e de ser retificável sem trocar a fonte — ver *Impacto sobre Editais já publicados*, na spec.
A consulta que responde se existe algum, a rodar na base de produção antes da implantação:

```sql
SELECT e.id, e.number, e.year
  FROM processos_edital e
  JOIN publicacoes_versaoconsolidada v ON v.edital_id = e.id
 WHERE v.content::text LIKE '%"Fonte de demonstração"%';
```

Os nomes de tabela são os do Django por convenção e devem ser conferidos contra `\dt` antes de rodar;
a consulta só lê.
