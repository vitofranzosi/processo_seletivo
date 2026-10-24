# Quickstart: Relatório do Edital

## Ver pelo navegador

Num banco próprio e migrado (`DB_NAME=ps_099`), monte o cenário coerente e suba o servidor com o
seletor de identidade ligado:

```bash
cd backend
uv run python manage.py shell < ../doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/roteiro/cenario_coerente.py
INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver
```

1. Em `/gestao/`, identifique-se como gestão (papel `gestor`) ou como `paulo.presidente`.
2. Abra o Edital 61/2026 e escolha **Relatório do Edital**.
3. Confira: *Relatório de acompanhamento*, *Encerrado em 20/10/2026*, *1 convocação aguardando
   resposta, até 30/10/2026*, seis indicadores e três pontos de atenção.
4. **Baixar PDF**. O arquivo traz a emissão nº 1; a trilha do Edital ganha o evento.

Para o cenário **sem pendência**, rode o roteiro com `FINAL=sem-pendencia`: a convocação da vaga
reservada recebe aceite antes do encerramento, e o relatório passa a ser *de encerramento*.

## Validar pela suíte

```bash
cd backend
make test-pg PYTEST_WORKERS=0 PYTEST_ADDOPTS="tests/integration/relatorio tests/interface/test_relatorio.py tests/unit/interface/test_relatorio_do_edital.py tests/performance/test_relatorio.py"
make lint check test-pg
```
