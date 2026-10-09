# Verificação — 065, conflitos de numeração

## Ponto de partida (T002)

Medido em 2026-10-08 sobre `75dd66df` (spec, plano e tarefas, sem código), contra PostgreSQL, com
`DB_NAME=ps065` e `pytest` chamado direto (a worktree não tem `.env`):

```text
tests/unit/editais tests/unit/publicacoes tests/contract
tests/interface/test_caractere_sem_grafia.py tests/integration/publicacoes
1908 passed in 89.39s
```
