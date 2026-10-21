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

## Ordem dos testes

**A US1 não teve a fase vermelha que as tarefas pedem.** O módulo `ocupacao/application/acrescimo.py`
foi escrito antes de os testes de T014 e T015 rodarem pela primeira vez, e eles já rodaram verdes.
Os da Phase 2 e o de convocação (T016) falharam primeiro pelas razões esperadas — `ImportError` e,
em T016, a recusa `fundamento_obrigatorio` da convocação individual, que levou o teste a conferir o
fundamento pela prévia do gesto. Registrado por honestidade: a cobertura é a mesma, mas não houve
prova de que cada teste reprovaria sem o código.
