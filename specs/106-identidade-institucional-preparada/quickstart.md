# Quickstart: Identidade institucional preparada

## 1. A homologação continua como está

```bash
cd backend && make preparar   # provisionar, migrar, provisionar: espera "44 de 44"
INTERFACE_SELETOR_IDENTIDADE=true make runserver
```

Abra `/gestao/identificar`: a página é a de hoje, com "Acessar ambiente de demonstração". Nenhuma
variável nova é necessária. O passo a passo da homologação está em
[`doc/homologacao-com-o-seletor-de-demonstracao.md`](../../doc/homologacao-com-o-seletor-de-demonstracao.md).

## 2. O modo institucional, pelo provedor simulado

Só nos testes: o provedor simulado mora em `backend/tests/fixtures/provedor_simulado.py` e não é
importável por `production.py`.

```bash
cd backend && PYTEST_ADDOPTS="tests/seguranca" make test-pg PYTEST_WORKERS=0
```

O que deve passar: os doze testes do pedido, nomeados na
[matriz](rastreabilidade.md).

## 3. As recusas de produção

```bash
cd backend && PYTEST_ADDOPTS="tests/test_configuracao_producao.py tests/seguranca/test_ativacao.py" make test-pg PYTEST_WORKERS=0
```

## 4. A verificação inteira

```bash
cd backend && make lint check test-pg
```
