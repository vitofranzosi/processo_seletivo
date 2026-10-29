# Quickstart: Agenda dos Editais

## Pré-requisitos

- `backend/.env` com `DB_NAME` próprio da worktree e o superusuário local em `POSTGRES_USER`.
- `cd backend && uv sync --extra dev`.

## Verificar

```bash
cd backend && make lint check test-pg DB_NAME=ps101
```

Só a feature, em série:

```bash
cd backend && PYTEST_ADDOPTS="tests/unit/interface/test_agenda.py tests/integration/agenda tests/interface/test_agenda.py tests/interface/test_shell_da_gestao.py -q" make DB_NAME=ps101 test-pg PYTEST_WORKERS=0
```

## Ver pelo navegador

1. Banco de demonstração com Editais publicados cujos cronogramas se concentram no mês corrente e no
   seguinte — inclusive um dia com vários marcos, um período que atravessa o mês, um Evento
   cancelado e uma Retificação de vigência futura:

   ```bash
   cd backend && createdb -h /tmp ps_demo_101 && make preparar DB_NAME=ps_demo_101
   set -a; source .env; set +a
   DB_NAME=ps_demo_101 DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py shell \
     < ../doc/estudo-calendario-institucional-2026-10-29/semear_demonstracao.py
   ```
2. Servidor: a entrada `agenda-101` do `.claude/launch.json` (porta 8101, seletor de identidade
   ligado, banco `ps_demo_101`).
3. Abrir `http://localhost:8101/gestao/identificar`, entrar com qualquer nome e sem papel nenhum, e
   seguir *Agenda* na barra.

## O que conferir

| Cenário | Esperado | Requisitos |
|---|---|---|
| Abrir a Agenda | o mês corrente, grade de domingo a sábado, hoje marcado | FR-2623, FR-2624 |
| Dia com vários marcos | contagem em texto, destaque, até dois nomes e *mais N* em tela larga | FR-2625, FR-2626 |
| Escolher esse dia | todos os marcos, com Edital, Processo, local, *Abre*/*Encerra* e os dois links | FR-2628, FR-2629 |
| Período que atravessa o mês | só a abertura e o encerramento na grade; uma linha em *Períodos no mês* | FR-2619, FR-2627 |
| Evento cancelado | fora da grade e da síntese; *Cancelado* no dia e em Próximos marcos | FR-2621 |
| Retificação de vigência futura | aviso com o Edital e a data; datas antigas na grade | FR-2614 |
| Filtrar um Edital e trocar de aba | o filtro segue, e a síntese conta só ele | FR-2637, FR-2638 |
| *Cronograma publicado* | abre a página pública do Edital na seção do cronograma | FR-2629 |
| 375 px | grade de sete colunas sem nomes, sem rolagem horizontal | FR-2626, FR-2645 |

## Desempenho

Preenchido na implementação (research R-004): consultas e tempo da página com 1 e com N Editais, e o
volume do conteúdo materializado.
