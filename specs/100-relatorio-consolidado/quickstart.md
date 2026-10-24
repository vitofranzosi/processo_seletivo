# Quickstart: Relatório consolidado da unidade

## Pré-requisitos

- `backend/.env` com `DB_NAME` próprio da worktree e o superusuário local em `POSTGRES_USER`.
- `cd backend && uv sync --extra dev`.

## Verificar

```bash
cd backend && make lint check test-pg DB_NAME=ps100
```

Só a feature, em série:

```bash
cd backend && PYTEST_ADDOPTS="tests/unit/interface/test_relatorio_consolidado.py tests/integration/relatorio_consolidado tests/integration/relatorio tests/interface/test_relatorio_consolidado.py tests/performance/test_relatorio_consolidado.py -q" make DB_NAME=ps100 test-pg PYTEST_WORKERS=0
```

## Ver pelo navegador

1. Banco de demonstração com Editais do cenário coerente, publicados em datas diferentes:
   `roteiro/semear_demonstracao.py` da pasta do estudo, executado por `manage.py shell` com o `DB_NAME`
   de demonstração (o roteiro está em `doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/roteiro/`).
2. Servidor com `INTERFACE_SELETOR_IDENTIDADE=true` e `DB_NAME` daquele banco.
3. Entrar como Gestor do Cefor; **Visão Geral** → **Relatório consolidado**.
4. Escolher "1º semestre" de 2026, conferir a lista, desmarcar um Edital, **Ver relatório**.
5. Conferir a ficha (conjunto e data dos dados), os seis números e os pontos de atenção.
6. **Baixar PDF**; conferir "emissão nº 1" e a trilha da Unidade.

## O que conferir no documento

- O período aparece como critério de escolha, e a data dos dados como o instante da emissão.
- Nenhum cancelado em número; a base diz "fora o Edital cancelado".
- "Inscrições por vaga" com a base Σ/Σ, e nenhuma ordenação por ela.
- "Convocação aceita", nunca "vaga preenchida"; matrícula só como fato não registrado.
- Registros posteriores ditos como registros da trilha.
