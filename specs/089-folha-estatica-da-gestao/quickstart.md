# Quickstart — 089

Caminhos de roteiro relativos a `doc/inventario-visual-da-gestao-2026-10-16/`; comandos a partir de
`backend/`. `$DEV` abrevia o ambiente do inventário:

```bash
export LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_089 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900
```

## Ambiente

O banco do inventário, numa cópia própria; o de teste, `DB_NAME=ps_089`:

```bash
createdb -T ps_inventario_088 ps_inventario_089
```

```bash
uv sync --extra dev --extra assistente
```

## A equivalência das regras

Contra o commit de antes da mudança (`41cf1b4c`, a `main` com a `088`):

```bash
uv run python ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/equivalencia.py 41cf1b4c
```

Esperado: `IGUAIS`, 818 linhas de regra dos dois lados, 163 comentários.

## O inventário, antes e depois

O código de antes sai de um `git archive`, e o roteiro roda de dentro dele com o ambiente do projeto:

```bash
git archive 41cf1b4c backend | tar -x -C /tmp/codigo-antes
```

Em cada lado (`backend/` da worktree, ou `/tmp/codigo-antes/backend`), com a barra expandida e
recolhida, e com o resumo das regras ligado:

```bash
ESTILOS=1 BARRA=expandida PORTA=8189 uv run --project <worktree>/backend --with playwright --with pillow python <worktree>/doc/inventario-visual-da-gestao-2026-10-16/capturar.py <saída>
```

```bash
uv run --project <worktree>/backend --with playwright --with pillow python <worktree>/doc/inventario-visual-da-gestao-2026-10-16/capturar_bases.py <saída>/bases
```

Uma segunda passada de cada lado dá os pares de ruído. A comparação:

```bash
python3 medidas.py antes/resultados.json depois/resultados.json
```

```bash
uv run --with pillow python pixels.py <antes> <depois> <antes> <antes-2ª> <depois> <depois-2ª>
```

Esperado: `variantes que mudaram: 0` no `medidas.py`, com o campo `estilos` comparado; nenhuma
`REPROVA` no `pixels.py`; o mesmo com a barra recolhida e para as bases. Os `resultados.json` e a saída
do `pixels.py` estão em `depois-da-089/`.

## O peso

```bash
uv run python ../doc/inventario-visual-da-gestao-2026-10-16/pesar.py
```

E o número do guardião da Distribuição: trocar à mão `< 120_000` por `< 0` em
`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`, rodar, ler o `len(corpo)` da
mensagem, e desfazer (`git checkout`).

## A impressão

O `imprimir.py` da `088`, antes (de `/tmp/codigo-antes/backend`) e depois; `impressao.json` igual, os
`--papel.png` iguais pelo `pixels.py`, o texto dos PDF igual por `pdftotext -layout`.

## No navegador

O runserver da worktree, à mão e sem recarga automática, na porta 8189 — o `.claude/launch.json` não
ganha entrada:

```bash
uv run python manage.py runserver 8189 --noreload
```

1. Identificar-se como gestor e abrir a lista e depois a Visão Geral. Em
   `performance.getEntriesByType('resource')`, na segunda página, a `gestao.css` tem `decodedBodySize`
   0: veio do cache, só revalidada.
2. **Edição sem reiniciar.** Acrescentar `h1{color:rgb(255, 0, 0)}` ao fim de `gestao.css` e
   recarregar: o `?v=` do `<link>` muda e o `h1` fica vermelho. Desfazer e recarregar: o `?v=` volta.
3. A 375 px, a lista sem rolagem horizontal; `document.styleSheets` com 1 regra em `tokens.css`, 561 em
   `gestao.css` e as da página.

## Mutação dos guardiões

```bash
LC_ALL=pt_BR.UTF-8 TEST_DB_ENGINE=postgresql DB_USER=$USER DB_RUNTIME_USER=$USER DB_NAME=ps_089 DJANGO_SETTINGS_MODULE=config.settings.test uv run python ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/mutacoes.py
```

Esperado: todas as linhas `REPROVA`, e `sem mutação: passa`. O script restaura cada arquivo depois de
cada mutação; não rode a suíte ao mesmo tempo.

## Suíte

```bash
LC_ALL=pt_BR.UTF-8 make lint check test-pg DB_NAME=ps_089 POSTGRES_USER=$USER
```
