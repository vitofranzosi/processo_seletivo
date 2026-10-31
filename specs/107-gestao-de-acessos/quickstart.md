# Quickstart: Gestão de acessos pela interface

Dois roteiros, e eles não se confundem (`FR-3133`). O primeiro é o de sempre, à mão, no ambiente de
homologação; o segundo é o único que mostra as telas desta feature, e é do ambiente de testes.

## Roteiro A — homologação manual, com o seletor (nada mudou)

Pré-requisito: `INTERFACE_SELETOR_IDENTIDADE=true`, `make preparar` (**46 de 46** tabelas
append-only — o incremento 1 da `107` não acrescentou nenhuma; o incremento 2, as duas da suspensão).

1. `/gestao/identificar` → "Acessar ambiente de demonstração" → escolher a identidade e os papéis.
2. A barra mostra o identificador escolhido, como antes, e **não** mostra "Acessos da unidade",
   "Administração de acessos" nem o seletor de unidade.
3. `/gestao/acessos` montado à mão responde a recusa (403), com o seletor ligado e qualquer papel.

O que este roteiro **não** mostra: as telas de acesso, a tela sem acesso, a troca de unidade e o
prazo da sessão. Elas são do modo institucional, e não há provedor institucional em execução —
nem real, nem de mentira. Não existe demonstração manual delas até haver um provedor de
homologação do Ifes.

## Roteiro B — as jornadas no navegador, no ambiente de testes

Pré-requisito, uma vez por máquina:

```bash
cd backend
uv sync --extra dev --extra navegador
uv run playwright install chromium
```

Com o PostgreSQL de pé e o `.env` da execução nativa (o `POSTGRES_USER` é o superusuário que cria o
banco de teste):

```bash
make test-navegador
```

Abre um Chromium na tela e desacelera cada passo. Sem janela, é o mesmo teste que o `test-pg` roda:
`make test-navegador NAVEGADOR_VISIVEL=0`. Para guardar uma captura em cada passo marcado:
`make test-navegador NAVEGADOR_CAPTURAS=/tmp/capturas`. Se houver outra suíte no mesmo cluster,
passe um `DB_NAME` próprio.

Cada jornada tem três partes, separadas no código
(`backend/tests/navegador/test_jornadas_de_acesso.py`):

| Jornada | Preparação (o ambiente) | Ações (só o navegador) | Verificações (depois) |
|---|---|---|---|
| US1 — sem acesso | uma pessoa sem vínculo, preparada na página do provedor | página de acesso → "Entrar com a conta institucional" → "Continuar" no provedor | a tela "Sem acesso vigente" com o nome; nenhum vínculo; a entrada na trilha |
| US2 — troca de unidade | Gestora no Cefor, Elaboradora no campus A | entrar; "Atuando em" → Cefor → "Trocar" | a barra com "Autoridades da unidade" e o papel do Cefor; a troca na trilha |
| US3 — conceder e revogar | o administrador de acessos do Cefor; a Beatriz, que já entrou uma vez | entrar; "Acessos da unidade" → "Conceder acesso" → buscar "beatriz" → Elaborador → "Conferir" → motivo → "Confirmar a concessão"; a Beatriz entra; o administrador revoga com motivo; a Beatriz clica num item da barra | a Beatriz cai na tela sem acesso; o vínculo, a revogação e os dois eventos de trilha; o histórico com os dois motivos |
| US4 — administração institucional | a administradora institucional, como o comando de implantação a deixaria; a Beatriz | entrar; "Administração de acessos" → "Conceder acesso" → buscar → unidade → "Conferir" → motivo → confirmar; a Beatriz entra | a Beatriz vê "Acessos da unidade"; o vínculo de Administrador de acessos no campus A |
| US5 — inatividade | uma pessoa com acesso; o relógio do ambiente | entrar; (o relógio avança 31 minutos); clicar em "Agenda" | a página de acesso diz que a sessão terminou por inatividade; a saída na trilha, com o motivo |
| US6 e US7 — suspender e reativar | a administradora institucional; a Beatriz, Elaboradora no Cefor | a Beatriz entra; a administradora: "Administração de acessos" → "Suspender ou reativar pessoas" → buscar → "Suspender" → motivo → confirmar; a Beatriz clica em "Agenda"; a administradora reativa, conferindo o que volta; a Beatriz entra de novo | a sessão dela caiu na suspensão; volta com Elaborador; nenhum vínculo revogado; a suspensão e a reativação na trilha |

**Como o provedor responde sem o Ifes.** O adaptador é o provedor simulado da `106`, que mora em
`backend/tests/` e que produção recusa. A ida ao provedor manda o navegador a uma página servida
pelo próprio teste (`tests/navegador/provedor.py`), que mostra quem o ambiente preparou e um botão
"Continuar". O botão volta ao retorno da gestão com o `state` da ida e um bilhete que só o provedor
simulado resolve. O navegador não escolhe quem é, e nada do que ele enviar vira identidade.

## Os comandos de implantação (incremento 2)

Não há tela para eles, de propósito (decisões P1 e P3): suspender e reativar quem tem
administração institucional, e retirar ou substituir essa administração.

```bash
uv run python manage.py suspender_pessoa --provedor <nome> --identificador <id> --motivo "…"
uv run python manage.py reativar_pessoa --provedor <nome> --identificador <id> --motivo "…"
uv run python manage.py retirar_administracao_institucional --provedor <nome> --identificador <id> --motivo "…"
uv run python manage.py substituir_administracao_institucional --de-provedor <nome> --de-identificador <id> --para-provedor <nome> --para-identificador <id> --motivo "…"
```

A retirada da última administração institucional pede `--sem-administracao`. No ambiente de
testes, os comandos são exercitados por `tests/seguranca/test_suspensao.py` e
`tests/seguranca/test_administracao_por_implantacao.py`.

## O que as jornadas não cobrem

- **O provedor real.** Nada aqui fala com AD, LDAP, OIDC ou SAML.
- **Os comandos de implantação**, que não têm tela: cobertos pelos testes de cliente, e não pelo
  navegador.
