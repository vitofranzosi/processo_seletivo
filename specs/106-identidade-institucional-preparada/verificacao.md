# Verificação e relatório de regressões: Identidade institucional preparada

Medido em 30/10/2026, na worktree desta branch, sobre a `main` em `4d93c1f8`, com `DB_NAME`
próprio (`ps_106_identidade`) e sem o grupo `assistente` instalado.

## A verificação inteira

```bash
cd backend && make lint check test-pg
```

| Passo | Resultado |
|---|---|
| `ruff check` | All checks passed |
| `ruff format --check` | 1666 files already formatted |
| `manage.py check` | no issues |
| `test-pg` (4 workers, `worksteal`) | **13645 passed, 13 skipped**, 0 falhas, em 595 s |

Os 13 pulados são os mesmos que o `CLAUDE.md` descreve para uma suíte sem o grupo `assistente`.
Nenhum teste novo pula contra PostgreSQL.

## A preparação do banco

`make preparar` num banco vazio:

```text
Papéis provisionados. 0 de 44 tabelas append-only estão sem UPDATE nem DELETE para o runtime.
Papéis provisionados. 44 de 44 tabelas append-only estão sem UPDATE nem DELETE para o runtime.
Unidades: 1 criadas, 0 alteradas, 0 sem mudança.
Modelos de aviso: 3 criados.
```

## Regressões

**Nenhum resultado esperado de comportamento mudou** (SC-1001). Os testes existentes alterados são
só guardiões que existem para subir com a justificativa:

| Arquivo | O que mudou | Por quê |
|---|---|---|
| `tests/migrations/test_migrations.py` | `seguranca` entra em `APPS` e em `TRIGGERS_POR_APP`, com os cinco gatilhos | o app ganhou a primeira migration; os testes de grafo, reversão e gatilhos passam a exercê-la |
| `tests/test_configuracao_producao.py` | quatro casos novos, nenhum caso existente tocado | as recusas do provedor institucional (`FR-3026`, `FR-3027`) |

`TABELAS_APPEND_ONLY` cresceu de 41 para 44, e o teste parametrizado de
`test_database_permissions.py` ganhou os três casos sozinho.

**Achados durante a implementação:**

1. **A revogação trancava o vínculo, e falharia em produção.** `SELECT ... FOR UPDATE` exige o
   privilégio de `UPDATE`, que a role de runtime não tem nas tabelas append-only. A suíte roda como
   superusuário e não o via; foi achado à mão, com `psql` como runtime no banco preparado. A trava
   passou para a pessoa, e `seguranca/test_privilegios.py` prende as duas metades — o que a runtime
   pode trancar, e que o código só tranca isso.
2. **A primeira rodada da suíte reprovou a tabela de incrementos do README**, que não listava a
   `106`. Acrescentada.

## Os doze testes do pedido

Todos existem e passam; cada um está nomeado na [matriz](rastreabilidade.md#os-doze-testes-do-pedido).
Rodados à parte:

```bash
cd backend && PYTEST_ADDOPTS="tests/seguranca tests/test_configuracao_producao.py" make test-pg PYTEST_WORKERS=0
```

## O que não foi verificado

- **O provedor real.** Não existe; o adaptador só foi exercido pelo simulado.
- **A página de acesso no navegador.** Com o seletor ligado e sem provedor, ela é a de antes, letra
  por letra no que se lê, e os testes de tela confirmam o texto; não houve captura.
- **O modo institucional como role de runtime de ponta a ponta.** As travas e os privilégios de que
  ele depende foram conferidos como runtime; a entrada inteira, não — a suíte não conecta como ela.
