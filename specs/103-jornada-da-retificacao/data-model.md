# Data Model: Jornada operacional da Retificação

**Nenhuma migration.** Nenhuma tabela, coluna, índice, situação ou transição nova.

## Retificação (existente, `publicacoes.Retificacao`)

| Campo | Uso nesta feature |
|---|---|
| `status` | `EM_ELABORACAO`, `EM_REVISAO`, `HOMOLOGADA` formam o conjunto **em curso**; `PUBLICADA` e `CANCELADA` são finais. |
| `revision` | viaja no formulário de edição (R-007) e é a revisão esperada do comando. |
| `created_by`, `created_at` | "criada por, em" na lista em curso e em "Quem atuou". |
| `prepared_by`, `submitted_at` | quem submeteu; a segregação lê este campo (FR-021 da `001`). |
| `homologated_by`, `homologated_at` | quem homologou; esvaziado na devolução, como hoje. |
| `return_reason` | o motivo da última devolução, em destaque quando em elaboração. |
| `justification`, `effective_at` | pré-preenchidos na edição. |
| `base_snapshot` | a base preservada pela edição. |

## Transições (inalteradas)

```text
EM_ELABORACAO --submeter--> EM_REVISAO --homologar--> HOMOLOGADA --publicar--> PUBLICADA
EM_REVISAO --devolver--> EM_ELABORACAO        HOMOLOGADA --devolver--> EM_ELABORACAO
EM_ELABORACAO --cancelar--> CANCELADA
EM_ELABORACAO --editar (mesma situação, revisão + 1)--> EM_ELABORACAO
```

## Derivações (nada persistido)

| Derivação | Fonte | Valor |
|---|---|---|
| próximo responsável | `status` | `EM_ELABORACAO` → quem elabora (submeter); `EM_REVISAO` → quem homologa (homologar); `HOMOLOGADA` → quem publica (publicar); finais → nenhum |
| é você | ofertas do ator | o ato principal da situação está entre as ofertas sem motivo |
| segregação antecipada | `prepared_by`, `homologated_by`, ator | `impede_por_segregacao` do Edital |
| aviso de homologação | `prepared_by`, ator | `homologar_fecharia_a_publicacao` do Edital |

## Trilha (`auditoria.RegistroAuditoria`, existente)

Evento novo para a Retificação, com operação já conhecida da trilha: `ALTERAR_RASCUNHO`, permissão
`retificacao:elaborar`, `previous_state` = `new_state` = `EM_ELABORACAO`, `previous_revision` = a
esperada, `new_revision` = a gravada.
