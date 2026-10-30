# Data Model: Ações disponíveis

**Nenhuma migration.** Nenhuma tabela, coluna, situação ou transição nova.

## Objeto de trabalho (derivado, `interface/trabalho.ObjetoDeTrabalho`)

| Campo | Origem |
|---|---|
| `natureza` | `edital`, `retificacao`, `recursos`, `avaliacao` |
| `chave` | `(natureza, id do objeto)`; para recursos, o id do Edital; para avaliação, `(edital, etapa)` |
| `titulo` | "Retificação do Edital 26/2026", "Edital 76/2027 — <título>", "Recursos do Edital 01/2026", "<Etapa> — Edital 51/2026" |
| `ato` | rótulo do ato principal: "Analisar a Retificação", "Publicar a Retificação", "Corrigir a Retificação devolvida", "Concluir a Retificação", "Continuar a elaboração", "Homologar o Edital", "Publicar o Edital", "Decidir recursos (n)", "Avaliar (n pendentes)" |
| `situacao` | rótulo da situação do objeto (não do Edital, quando o objeto é outro) |
| `detalhe` | justificativa da Retificação; motivo da devolução; título do Edital |
| `desde` | `Retificacao.submitted_at`/`homologated_at`; `RevisaoEdital.submitted_at`; `Homologacao.homologated_at`; ausente nos demais |
| `url` | página do ato: detalhe da Retificação, detalhe do Edital, composição, recursos, mesa da Etapa |
| `edital` | o Edital do objeto, para ordenar |

## Campos lidos (existentes)

- `Retificacao`: `status`, `return_reason`, `submitted_at`, `homologated_at`, `prepared_by`,
  `homologated_by`, `justification`, `created_by`, `created_at`.
- `Edital`: `status`, `number`, `year`, `title`, `institution_scope`.
- `RevisaoEdital`: `edital`, `prepared_by`, `submitted_at`; `Homologacao`: `revisao`,
  `homologated_by`, `homologated_at`, `revoked_at`.
- `Inscricao.status`, `Recurso` com `JuizoDeAdmissibilidade` e `DecisaoRecurso`.
- `AlocacaoEtapa`, `Atribuicao`, `Avaliacao.estado`.
