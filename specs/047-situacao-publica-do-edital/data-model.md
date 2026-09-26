# Data model — 047

**Nenhuma entidade nova, nenhum campo novo e nenhuma migration.** O total do `make preparar`
continua **`N de 34`**. Esta feature só lê.

## O que é lido, e de onde

| Fato projetado | Fonte autoritativa | Camadas de imutabilidade | Requisito |
|---|---|---|---|
| Há desfecho | `Edital.status`, `ProcessoSeletivo.status` em `ENCERRADO`/`CANCELADO` (terminais, CAS) | estado final não admite transição (`processos/domain/finalizacao.py`) | `FR-760`, `FR-762` |
| Data do desfecho | `AtoAdministrativo(aggregate_type, aggregate_id, operation ∈ {ENCERRAR, CANCELAR}).occurred_at` | gatilho + privilégio + guarda de modelo | `FR-760` |
| Motivo do desfecho | `AtoAdministrativo.reason` | idem | **não é lido** (`FR-764`) |
| Autor do desfecho | `AtoAdministrativo.actor_subject` | idem | **não é lido** (`FR-776`) |
| Período de inscrições | Evento `isRegistrationPeriod` da versão vigente → `periodo_de_inscricoes` | conteúdo publicado | inalterado |
| Fase do Evento | `startAt`, `endAt`, `status == CANCELADO` da versão vigente → `fase_do_evento` | conteúdo publicado | `FR-765`, `FR-766` |
| Agora e próximo | a mesma leitura, filtrada e ordenada → `marcos_pendentes` | conteúdo publicado | `FR-767`, `FR-768` |
| Janela recursal | `appealWindow` do marco na versão vigente + âncora na cadeia de `PublicacaoResultado` → `janela_da_publicacao_divulgada` | conteúdo publicado + cadeia append-only | `FR-769` a `FR-771` |
| Histórico de resultados | `PublicacaoResultado` do Edital, com `publicacao_anterior`/`sucessoras`, por `(marco_id, lista_id)` | append-only | `FR-772`, `FR-773` |

## Estruturas de leitura (não persistidas)

**Desfecho.** Mora no selector de `processos`.
- `alcance`: `EDITAL` ou `PROCESSO`
- `operacao`: `ENCERRADO` ou `CANCELADO`
- `em`: instante, ou `None` quando o ato não existe (`R-2`)

**Situação pública.** Mora na leitura do portal.
- `chave`: classe da marca
- `rotulo`: texto da marca
- `desfecho`: `Desfecho` ou `None`

**Fase do Evento.** Em `editais/domain/fase_do_evento.py`, pode valer:
- `PLANEJADO`, `EM_ANDAMENTO` ou `CONCLUIDO`, da régua da `045`;
- `None`, para o cancelado e para o Evento sem início.

O portal traduz para `futuro`, `em_curso`, `concluido` e `cancelado` (`R-1`).

**Janela divulgada.** Mora nos selectors de `recursos`: `(abre, fecha)` ou `None`.

## Precedência (`D-003`)

```text
Edital CANCELADO ─┐
Edital ENCERRADO ─┴─► desfecho do Edital
                  └─ senão: Processo ENCERRADO/CANCELADO ─► desfecho do Processo
                           └─ senão: marca do período (inalterada)
```

Processo `CANCELADO` implica todos os Editais finais (`ensure_processo_can_be_cancelled`), e por isso
o desfecho do Edital sempre vence nesse caso.
