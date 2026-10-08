# Quickstart — como repetir a medição

## Preparar

```bash
createdb -T ps_polish_audit ps_058_polish
cd backend && DB_NAME=ps_058_polish DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py migrate --check
```

Se `ps_polish_audit` não existir: `createdb ps_058_polish`, `migrate` e `seed_demo`. Os Editais de
trabalho são o **51/2026** (concluído: Resultados, Matrículas, Ocupação, Condução), o **01/2026**
(publicado) e o **76/2027** (em elaboração: Etapas e Revisão).

Servidor nativo com o seletor de identidade, numa entrada **acrescentada** ao `.claude/launch.json`
e revertida antes do commit. Entrar como `ana.gestora` com todos os papéis. Janela de
**1280 × 900**; a Lista e a Condução também a **375 px** (viewport emulado, medindo
`document.documentElement.scrollWidth` **e** `innerWidth`).

## As provas

- **destinos por papel** ([D-010](research.md)): o script `capturas/acoes.py`, no
  `manage.py shell`, com `ana.gestora` e `joana.avaliadora`, grava `acoes-antes.json` e
  `acoes-depois.json`; `diff` dos dois;
- **envio de "Salvar rascunho"**: `new FormData(form, botão)` nas etapas Etapas e Revisão, sem o
  token, com o `ruleId` mascarado;
- **rascunho gravado** ([D-005](research.md)): o script `capturas/rascunho.py` salva as Etapas do
  76/2027 com o envio da tela e imprime as linhas e o último registro.

## O teto da distribuição

```bash
cd backend && make test-pg DB_NAME=<banco-próprio> PYTEST_ADDOPTS="-q -s tests/performance/test_escala_da_mesa.py -k distribuicao"
```

com um `print(len(corpo))` temporário antes da asserção, revertido depois.

## A suíte

```bash
cd backend && make lint check test-pg DB_NAME=<banco-próprio>
```
