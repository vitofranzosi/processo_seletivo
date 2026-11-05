# Quickstart: a experiência da convocação, incremento 1

**Plano**: [plan.md](plan.md) · O roteiro de demonstração, depois da implementação.

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado (macOS com Homebrew).
- `uv sync --extra dev --extra navegador` e `uv run playwright install chromium`, para as jornadas.
- Um `DB_NAME` próprio da worktree.

## A suíte

```bash
cd backend && make lint check test-pg DB_NAME=ps_121
```

Os grupos que importam para esta feature, separados:

```bash
cd backend && PYTEST_ADDOPTS="tests/unit/convocacao/test_prazo_apresentado.py tests/unit/convocacao/test_escolha_da_mensagem.py tests/integration/convocacao/test_mensagem_da_convocacao.py tests/authorization/test_convocacao_alheia.py tests/integration/portal/test_destino_da_convocacao.py" make test-pg PYTEST_WORKERS=0 DB_NAME=ps_121
```

```bash
cd backend && make test-navegador DB_NAME=ps_121
```

## A demonstração no navegador

O banco de demonstração é próprio, sem `seed_demo`. Os cenários são os da `118`, montados pelo
roteiro do estudo:

```bash
cd backend && LETRA=C1 uv run python manage.py shell < ../doc/estudo-experiencia-da-convocacao-2026-11-05/roteiro/montar.py
```

```bash
cd backend && LETRA=C1 CORRIGIR=1 uv run python manage.py shell < ../doc/estudo-experiencia-da-convocacao-2026-11-05/roteiro/montar.py
```

| Passo | Onde | O que se vê |
|---|---|---|
| 1 | a mensagem no terminal do `runserver`, ou no coletor do compose (`localhost:8025`) | o assunto com a obrigação e *"até DD/MM"*; HTML e texto; o link *"Acessar minha convocação"* |
| 2 | o link, numa janela sem sessão | o acesso com *"Entre para ver a sua convocação"* e *"Depois do código, você vai direto para a convocação."* |
| 3 | o código, no mesmo terminal | a convocação, sem passar pela lista |
| 4 | a 375 × 812 | o título, a etapa, o cartão do prazo com o dia da semana e a contagem, o resumo e *"Ver o que preciso fazer"*, tudo na primeira tela |
| 5 | escolher um PDF e enviar | o nome do arquivo no cartão; *"Enviando… não feche esta página."*; a volta em `#confirmacao`, com o foco nela |
| 6 | enviar um arquivo que não é PDF | a recusa no cartão do item, com o foco nela |
| 7 | o cenário com `CORRIGIR=1` | *"Convocação corrigida: este é o prazo válido."* no cartão; *"Convocação substituída"* nos dados do ato; a mensagem da correção com o quadro |

A D-008 se demonstra pela suíte, e não pelo navegador: provocar a falha de um envio no meio da cadeia
exige o *backend* de e-mail que recusa, que só a suíte monta.

## Antes do uso real

- A matriz de clientes de e-mail da SC-1164, com uma captura por linha, sobre o SMTP de homologação.
- SPF, DKIM e DMARC conferidos com a TI (8ª decisão do estudo).
