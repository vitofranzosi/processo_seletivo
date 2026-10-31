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
| `test-pg` (4 workers, `worksteal`) | **13645 passed, 13 skipped**, 0 falhas, em 595 s; no segundo commit, **13651 passed, 13 skipped**, em 573 s |

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

## Revisão do #345 (segundo commit)

A revisão de `aa7f30d2` pediu dois ajustes, os dois corrigidos com teste de regressão:

1. **O retorno lia `estado`, e o OIDC devolve `state`.** Um provedor convencional recebia 403 sem
   chegar ao adaptador; o simulado mascarava, porque usava `estado` na ida e na volta. A gestão
   passou a ler `state` na fronteira HTTP, e um adaptador de outro protocolo diz onde o estado volta
   por `estado_do_retorno(request)`. O simulado envia e recebe `state`.
   `ENT::test_o_retorno_le_o_state_do_protocolo_e_nao_o_nome_interno` e
   `::test_o_adaptador_pode_dizer_onde_o_estado_volta`.
2. **A primeira administração institucional não era exclusiva sob concorrência.** Trancar só a pessoa
   de destino deixava duas execuções para pessoas diferentes gravarem dois administradores sem
   `--adicional`. A decisão passou a correr sob `pg_advisory_xact_lock` de chave fixa, que não pede
   privilégio de tabela. `seguranca/test_concorrencia.py` põe uma barreira depois da trava: **com a
   trava removida, o teste reprova** (`['concedida', 'concedida']`), conferido antes do commit.
   `seguranca/test_privilegios.py` confere que a role de runtime obtém a trava.

As condições da futura ativação que a revisão listou e o roteiro não tinha — emissor mais `sub` como
identificador, PKCE, suspensão do administrador institucional, a duração de sessão ainda só proposta
— entraram em [`doc/ativacao-do-sso-institucional.md`](../../doc/ativacao-do-sso-institucional.md)
como pendência, sem implementação.

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
