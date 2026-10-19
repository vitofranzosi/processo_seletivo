# Quickstart — 092

Caminhos de roteiro relativos a `doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/`; comandos a
partir de `backend/`. O banco do inventário é `ps_inventario_092`, cópia do `ps_inventario_091`; o banco
de teste é `ps_092`. `<antes>` é o commit de partida (`2615b738`, a branch do PR #308).

```bash
export LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true
```

```bash
createdb -T ps_inventario_091 ps_inventario_092
```

## Os rascunhos com a barra de documentos

```bash
DB_NAME=ps_inventario_092 uv run python manage.py shell < ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/preparar_rascunhos.py
```

Esperado: Clara com 0 de 2, Daniel com 1 de 2, Elisa com 2 de 2. Depois, uma cópia por passada:
`createdb -T ps_inventario_092 ps_inv_092_<passada>`.

## A equivalência

```bash
python3 ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/equivalencia.py <antes>
```

Esperado: `EQUIVALENTE: o <style> de <antes> (65839 bytes, 445 chaves de abertura, 124 comentários) …`.

## O inventário do portal, antes e depois

O lado de antes por `git archive <antes>`, rodado de dentro do `backend/` do arquivo, com
`uv run --project <worktree>/backend`; o de depois, da worktree. A primeira passada rastreia e grava
`rotas.json`; as outras o recebem:

```bash
DB_NAME=ps_inv_092_antes PORTA=8921 uv run --with playwright python capturar_portal.py <saída-antes>
```

```bash
DB_NAME=ps_inv_092_depois PORTA=8923 uv run --with playwright python capturar_portal.py <saída-depois> <saída-antes>/rotas.json
```

Mais um par de ruído de cada lado, num banco copiado à parte. Então:

```bash
MEDIDAS_CAMPOS=scrollWidth,altura,titulo,h1,conjunto python3 ../medidas.py <antes>/resultados.json <depois>/resultados.json
```

```bash
uv run --with pillow python ../pixels.py <antes> <depois> <antes> <antes-2ª> <depois> <depois-2ª>
```

Esperado: nenhuma variante mudou; nenhum `status` diferente; zero estouros; pixels idênticos ou dentro do
ruído, salvo o dado na tela do comprovante (porta, hora, resumo do PDF — R-006); zero violações depois,
e `content-security-policy` em todas as respostas.

O papel, com a mesma porta nas quatro passadas: `IMPRESSAO=1 SO='comprovante|/selecoes/inscricoes/[^/]+/$'`.
As bases: `capturar_bases.py` da `089`, nos mesmos bancos.

## O navegador, à mão

Com o servidor da worktree, abrir a vitrine, a página de uma seleção, um rascunho com a barra de
documentos e um comprovante; o console sem nenhuma mensagem de política, e o cabeçalho em recusa:

```bash
curl -sI http://localhost:<porta>/selecoes/ | grep -i content-security
```

## A mutação

Sem outra suíte desta worktree em curso:

```bash
uv run python ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/mutacoes.py
```

Esperado: todas `REPROVA`, e `sem mutação: passa`.

## O peso

```bash
DB_NAME=ps_inv_092_depois uv run python ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/pesar_portal.py <antes>/rotas.json
```

## A suíte

```bash
make lint check test-pg DB_NAME=ps_092 POSTGRES_USER=$USER
```
