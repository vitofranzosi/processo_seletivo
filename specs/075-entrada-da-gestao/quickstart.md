# Quickstart — 075

## Preparar

Um banco próprio com o `seed_demo`, que traz comissão (`paulo.presidente`, `joana.avaliadora`,
`otavio.avaliador`) e uma trilha com quem exerceu cada papel:

```bash
cd backend && createdb ps_redesign_acesso
LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_redesign_acesso DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py migrate
LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_redesign_acesso DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py sincronizar_unidades
LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_redesign_acesso DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py seed_demo
```

E subir pela entrada `redesign-acesso` do `.claude/launch.json` (porta 8076).

## Percorrer

1. Abrir `http://localhost:8076/`. O cabeçalho diz "Gestão de Processos Seletivos" e traz "Minhas
   inscrições" e "Área de gestão".
2. "Área de gestão" → a página de acesso, com a coluna institucional e "Bem-vindo à gestão".
3. "Acessar ambiente de demonstração" → *Comissões* e *Responsabilidades da unidade*, sem código de
   permissão. Entrar por "Gestor" → a lista de Processos, com `gustavo.gestor — Gestor` no
   cabeçalho.
4. Sair → a página de acesso.
5. Sem identidade, abrir o endereço de um Edital (`/gestao/editais/<id>/`) → a página de acesso;
   escolher "Gestor" → o Edital.
6. A 375 px, repetir 2 e 3: a coluna vira faixa, nada rola na horizontal.
7. Subir sem `INTERFACE_SELETOR_IDENTIDADE`: `/gestao/identificar` responde 503 com a mensagem de
   entrada não configurada; a vitrine não traz "Área de gestão".

## Automatizado

```bash
cd backend && make lint check && make test-pg DB_NAME=ps_redesign_teste POSTGRES_USER=$USER
```
