# Quickstart — como repetir a medição

## Preparar

```bash
createdb -T ps_polish_audit ps_057_polish
cd backend && DB_NAME=ps_057_polish DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py migrate --check
```

Se `ps_polish_audit` não existir: `createdb ps_057_polish`, `migrate` e `seed_demo`. Os Editais de
trabalho são o **51/2026** (concluído), o **01/2026** (publicado, inscrições abertas) e o
**76/2027** (em elaboração, para a Revisão).

Servidor nativo com o seletor de identidade (`INTERFACE_SELETOR_IDENTIDADE=true`) e a identidade de
demonstração do portal (`PORTAL_IDENTIDADE_DEMO=true`), numa entrada **acrescentada** ao
`.claude/launch.json` e revertida antes do commit. Entrar como `ana.gestora` com todos os papéis, e
depois como `joana.avaliadora`. Janela de **1280 × 900**.

## Medir

Pelo console de cada página:

- **lista de destinos** ([D-017](research.md)): `href` de todo link no `main`, `action` de todo
  formulário, `formaction` e `name=value` de todo botão — ordenada e sem repetição;
- **Detalhe do 01/2026**: ações preenchidas, a posição de `.terminais`, a altura de "Quem atuou";
- **Lista**: altura da linha do 01/2026;
- **telas de marco e matrículas**: `top` do primeiro controle ou tabela depois do glossário;
- **Auditoria do 51/2026**: altura do `ol.auditoria` dividida pelo número de `li`;
- **Revisão do 76/2027**: o texto da página, procurando "2.0000", "(s)" e datas aaaa-mm-dd;
- **Alocação**: `document.documentElement.scrollWidth` e a altura do `thead`;
- **portal**: o `top` do rótulo do seletor e o de "Enviar" num documento.

E a **375 px** (viewport emulado): Lista, Detalhe, Alocação e o envio do portal sem controle cortado.

## O teto da distribuição

```bash
cd backend && make test-pg DB_NAME=<banco-próprio> PYTEST_ADDOPTS="-q -s tests/performance/test_escala_da_mesa.py -k distribuicao_nao_cresce"
```

com um `print(len(corpo))` temporário antes da asserção, revertido depois.

## A suíte

```bash
cd backend && make lint check test-pg DB_NAME=<banco-próprio>
```
