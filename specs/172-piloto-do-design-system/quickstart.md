# Quickstart: fotografar, comparar e validar o piloto

*Guia de execução. Os comandos rodam de `backend/`, com as variáveis do `make test-pg` (o par
`TEST_DB_ENGINE=postgresql` e o usuário do `POSTGRES_USER`) e um `DB_NAME` próprio da worktree.*

## Pré-requisitos

```bash
uv sync --extra dev --extra navegador && uv run playwright install chromium
```

- O banco `ps_p0_referencia` no cluster local, intocado, e a cópia `ps_p0_referencia.dump` na pasta de
  notas das sessões deste trabalho.
- `LC_ALL` exportado, no macOS com o PostgreSQL do Homebrew.

## 1. A fotografia "antes"

Sobre a branch, **antes** de qualquer mudança de template ou de folha (só o catálogo e a jornada
escritos):

```bash
PILOTO_DS_FOTOGRAFIA=/caminho/de/trabalho/antes PYTEST_ADDOPTS="tests/navegador/test_fotografia_do_piloto.py" make test-pg PYTEST_WORKERS=0
```

Esperado: 64 casos passando, uma pasta por código, cinco PNG e cinco JSON em cada uma. Um caso que
falha por "estado não alcançado" é defeito do catálogo, e se corrige antes de seguir.

Sem a variável, o módulo pula: `1 skipped`.

## 2. A fotografia "depois" e a comparação

```bash
PILOTO_DS_FOTOGRAFIA=/caminho/de/trabalho/depois PYTEST_ADDOPTS="tests/navegador/test_fotografia_do_piloto.py" make test-pg PYTEST_WORKERS=0
```

```bash
uv run python ../doc/auditoria-design-system-2026-11-14/piloto/scripts/comparar.py /caminho/de/trabalho/antes /caminho/de/trabalho/depois ../doc/auditoria-design-system-2026-11-14/piloto/comparacao
```

Esperado: o `resumo.md` com os 64 estados passando, nas cinco larguras (SC-2600, SC-2601, SC-2603,
SC-2604).

## 3. Nada fora do piloto mudou

O `ps_p0_referencia` ficou para trás das migrations da `main` e não se migra. Com
`REFERENCIA_DUMP=<dump> montar_banco_da_validacao.sh referencia` e as duas entradas do §4 no ar, o rastreio roda nas duas
(`PORTA=8172` e `PORTA=8173`), sem o passo do portal, e os dois `telas.csv` se comparam:

```bash
sh ../doc/auditoria-design-system-2026-11-14/referencia-p0/scripts/rastrear_tudo.sh /caminho/de/trabalho/rastreio
```

Esperado: só diferem as linhas das telas do piloto; vinte capturas de fora, sorteadas, sem diferença
de métrica (SC-2602).

## 4. As duas versões para a equipe

Os bancos são um por tarefa (o roteiro está em `validacao.md`, *Antes da sessão*):

```bash
PILOTO_DS_BANCO=/caminho/bancos PYTEST_ADDOPTS="tests/navegador/test_banco_da_validacao_do_piloto.py" make test-pg PYTEST_WORKERS=0
```

```bash
sh ../doc/auditoria-design-system-2026-11-14/piloto/scripts/montar_banco_da_validacao.sh v3 /caminho/bancos
```

Depois, as entradas `piloto-antiga` (porta 8172, a `main`, de uma worktree destacada que o roteiro
cria) e `piloto-nova` (porta 8173, a branch) do `.claude/launch.json`, as duas sobre
`ps_piloto_validacao`. O mesmo roteiro, com `referencia` no lugar da tarefa, restaura a cópia da
referência da P0, migrada, para o rastreio do §3.

## 5. A conferência manual

Em cada uma das cinco telas, na versão nova: tabulação do começo ao fim, foco visível, nada coberto
pela barra; 320 px; zoom de 200% e 400%; a recusa com o foco. O resultado vai para o `relatorio.md`
(SC-2605).

## 6. A suíte

```bash
make lint check test-pg
```

Esperado: verde, com um pulado a mais que a medição anterior (o módulo da fotografia, sem a variável),
e nenhum guardião afrouxado (SC-2608).
