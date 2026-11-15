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

Esperado: 63 casos passando, uma pasta por código, cinco PNG e cinco JSON em cada uma. Um caso que
falha por "estado não alcançado" é defeito do catálogo, e se corrige antes de seguir.

Sem a variável, o módulo pula: `1 skipped`.

## 2. A fotografia "depois" e a comparação

```bash
PILOTO_DS_FOTOGRAFIA=/caminho/de/trabalho/depois PYTEST_ADDOPTS="tests/navegador/test_fotografia_do_piloto.py" make test-pg PYTEST_WORKERS=0
```

```bash
uv run python ../doc/auditoria-design-system-2026-11-14/piloto/scripts/comparar.py /caminho/de/trabalho/antes /caminho/de/trabalho/depois ../doc/auditoria-design-system-2026-11-14/piloto/comparacao
```

Esperado: o `resumo.md` com os 63 estados passando, nas cinco larguras (SC-2600, SC-2601, SC-2603,
SC-2604).

## 3. Nada fora do piloto mudou

Com o servidor `referencia-p0` (porta 8166) servindo a branch sobre o `ps_p0_referencia`:

```bash
sh ../doc/auditoria-design-system-2026-11-14/referencia-p0/scripts/rastrear_tudo.sh /caminho/de/trabalho/rastreio
```

Esperado: comparado com `referencia-p0/telas.csv`, só diferem as linhas das cinco telas do piloto;
vinte capturas de fora, sorteadas, dentro da linha de ruído (SC-2602).

## 4. As duas versões para a equipe

```bash
sh ../doc/auditoria-design-system-2026-11-14/piloto/scripts/montar_banco_da_validacao.sh
```

Depois, as entradas `piloto-antiga` (porta 8167, a `main`, de uma worktree nela) e `piloto-nova`
(porta 8168, a branch) do `.claude/launch.json`, cada uma sobre o seu banco, com
`INTERFACE_SELETOR_IDENTIDADE=true`. Abrir as duas em `/gestao/`, entrar com a identidade de cada
tarefa da `validacao.md` e conferir que os seis estados das tarefas aparecem, nas duas, com registros
diferentes.

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
