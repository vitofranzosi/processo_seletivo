# Verificação: 061

**Feature**: [spec.md](spec.md) · **Matriz**: [rastreabilidade.md](rastreabilidade.md)

## Estado de partida (T001, T007), medido em 06/10/2026 sobre a `main` `1d2c26ff`

**No teste**, `tests/integration/classificacao/test_corte_apos_recurso.py` contra PostgreSQL:

| Caso | Contra a `main` |
|---|---|
| corte sobre a ordem sucessora, estado | falha — `obsoleto`, `participante_reingressou` |
| Etapa governada, impedimento | falha — `corte-obsoleto` |
| geração sucessora sobre o mesmo ato, estado | falha — `obsoleto`, `participante_reingressou` |
| publicação do ato vigente | falha — `publication_cut_stale` |
| corte → recurso, publicação | passa — `publication_cut_stale`, `participante_reingressou` |

**No banco de demonstração** `ps_apresentacao_grafico`, Edital 72/2026, com `estado_do_corte` e
`impedimento_do_corte` pelo shell, só leitura:

| Marco | Lista | Estado |
|---|---|---|
| MAT | ampla | obsoleto — `participante_reingressou` |
| MAT | duas reservadas | em dia |
| TEC | ampla | obsoleto — `participante_reingressou` |
| TEC | reservada | em dia |
| Etapa governada pelos dois | — | `corte-obsoleto` |

Os sucessores acusados nas duas listas de ampla são exatamente os que o ato lido já cita no
`stageResults`: 2 de 2 no MAT, 1 de 1 no TEC.

## Depois (T010, T014)

**No teste**: os seis casos do arquivo novo passam, mais o de custo — uma consulta. As pastas
`tests/integration/classificacao/` e `tests/integration/divulgacao/`, mais
`tests/interface/test_reabilitacao.py` e `tests/integration/resultados/test_progressao_retroativa.py`:
232 passando. `test_corte_obsoleto.py` sem edição.

**No banco de demonstração**, o mesmo shell: as cinco listas em dia, e nenhum impedimento na Etapa
governada. Nenhum ato emitido no meio — os cortes de 01/10 ficaram em dia pela leitura (`D-003`).

## A suíte completa (T015), 06/10/2026

```bash
cd backend && make lint check test-pg POSTGRES_USER=$USER POSTGRES_PASSWORD= DB_USER=$USER DB_RUNTIME_USER=$USER DB_NAME=ps_sweet_faraday
```

- `ruff check` e `ruff format --check`: limpos (1268 arquivos).
- `manage.py check`: sem problemas. `makemigrations --check --dry-run`: *No changes detected*; o
  aviso de histórico que o acompanha é da worktree sem `.env` — não há banco de desenvolvimento com
  o `DB_NAME` passado —, e não do diff.
- `test-pg`: **9202 passando e 11 pulados**, em 987 s. São os 9195 da `059` mais os 7 desta; os onze
  pulados são os mesmos.

**Medido sobre a `main` anterior à `060`.** A `060` foi mergeada durante esta suíte, e a branch não
foi atualizada localmente: o merge traria um arquivo protegido do app (`.claude/launch.json`), que
ele só aceita de origem confirmada. O `AGENTS.md` fica com o total da `060` (9313), e o desta sobre
a `main` atual — esperado 9320, os 9313 mais os 7 — é o que o CI mede no PR.
