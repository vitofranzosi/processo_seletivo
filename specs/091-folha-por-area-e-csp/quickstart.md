# Quickstart — 091

Caminhos de roteiro relativos a `doc/inventario-visual-da-gestao-2026-10-16/`; comandos a partir de
`backend/`. O ambiente do inventário é o da `089`, com banco próprio (`ps_inventario_091`, cópia do
`ps_inventario_089`); o banco de teste é `ps_091`. O commit de antes é a `main` depois do merge do PR
#307 — `<antes>` abaixo.

```bash
export LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_091 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900
```

```bash
createdb -T ps_inventario_089 ps_inventario_091
```

```bash
uv sync --extra dev --extra assistente
```

## A ordem e as duplicadas (A)

Na pasta da prova (`depois-da-091/`), sobre o `gestao-antes-da-divisao.css` guardado ali:

```bash
uv run --project ../../../backend --with playwright python ordem.py preparar gestao-antes-da-divisao.css
```

```bash
CONFLITOS=$PWD/candidatos.json PORTA=8192 uv run --with playwright python ../capturar.py elementos
```

(o segundo de `backend/`, com o ambiente do inventário e o caminho do `capturar.py`)

```bash
uv run --with networkx python ordem.py resolver gestao-antes-da-divisao.css elementos/conflitos.json <destino>
```

Esperado: `ordem.json` com 281 pares de regras em conflito, nenhum invertido na distribuição, e as sete
regras fora da área do R-002.

```bash
python3 equivalencia.py
```

Esperado: `EQUIVALENTE: 562 regras e 162 comentários` e zero duplicadas no que uma página carrega.

## O estilo das telas e os atributos (B, C)

```bash
grep -rnE '<style|[[:space:]]style="' processo_seletivo/interface/templates processo_seletivo/shared/templates
```

Esperado: nada. O `grep` equivalente no portal lista só o que o R-007 prevê.

## A política (D)

No runserver da worktree (`DEBUG=True`), uma tela da gestão e uma do portal:

```bash
curl -sI http://localhost:<porta>/gestao/ | grep -i content-security
```

Esperado: `Content-Security-Policy: default-src 'self'; …`. No portal, `…-Report-Only`. Num PDF ou no
`/health`, nenhum. Num endereço inexistente sob `/gestao/` com `DEBUG`, nenhum (página de depuração).

## O inventário, antes e depois, com o console

Como na `089` — `git archive <antes>` para o lado de antes, as duas barras, `ESTILOS=1`, vários pares
de ruído —, agora com a leitura das violações ligada:

```bash
ESTILOS=1 VIOLACOES=1 BARRA=expandida PORTA=8191 uv run --project <worktree>/backend --with playwright --with pillow python <worktree>/doc/inventario-visual-da-gestao-2026-10-16/capturar.py <saída>
```

```bash
python3 medidas.py antes/resultados.json depois/resultados.json
```

```bash
uv run --with pillow python pixels.py <antes> <depois> <antes> <antes-2ª> <depois> <depois-2ª>
```

Esperado: zero diferença fora do ruído, zero estouros, nenhum `status` diferente, as mesmas regras
aplicadas (como conjunto) em cada variante, e zero violações na gestão e na página de acesso. As bases
(`capturar_bases.py`) e a impressão (`imprimir.py` da `088`) da mesma forma.

## O navegador, à mão

Com o servidor da worktree, abrir a visão geral, a Mesa com um documento aberto, a prévia do Edital com
o PDF, uma tela da composição com htmx e a página de identificação; o console sem nenhuma mensagem de
política. Plantar, pelo inspetor, `<div style="color:red">` numa tela: o navegador recusa e acusa.

## A mutação

```bash
uv run python ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-091/mutacoes.py
```

Esperado: todas `REPROVA`, e `sem mutação: passa`.

## O peso

```bash
uv run python ../doc/inventario-visual-da-gestao-2026-10-16/pesar.py
```

Antes e depois: Distribuição, lista, Minhas Etapas e visão geral (R-012).

## A suíte

```bash
make lint check test-pg DB_NAME=ps_091 POSTGRES_USER=$USER
```
