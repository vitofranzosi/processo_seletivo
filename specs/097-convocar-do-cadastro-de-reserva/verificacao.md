# Verificação: Convocar do cadastro de reserva, na ordem publicada

**Feature**: [spec.md](spec.md) · **Tarefas**: [tasks.md](tasks.md)

## Ponto de partida

Medido em 21/10/2026 sobre `1671a749` (a `main` em `717fc057` mais os artefatos desta spec), contra
PostgreSQL com `DB_NAME=ps_097` e 4 workers:

```text
tests/unit/ocupacao tests/integration/ocupacao tests/integration/convocacao
tests/interface/test_ocupacao.py tests/interface/test_convocacao_em_fluxo.py
tests/unit/editais/test_reserva_convocada_fora.py tests/test_vocabulario_da_ocupacao.py
tests/test_dependencia_da_convocacao.py

413 passed in 27.71s
```
