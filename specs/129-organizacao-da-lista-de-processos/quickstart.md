# Quickstart: validar a organização da lista

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado; `backend/.env` copiado do exemplo.
- `uv sync --extra dev` na worktree.

## Suíte

```bash
cd backend && DB_NAME=ps_129 make lint check test-pg
```

Os casos desta feature, isolados:

```bash
cd backend && DB_NAME=ps_129 PYTEST_ADDOPTS="tests/interface/test_organizacao_da_lista.py tests/integration/processos/test_recorte_dos_processos.py tests/performance/test_lista_em_escala.py" make test-pg PYTEST_WORKERS=0
```

## No navegador

1. Um banco descartável (`ps_129_demo`), preparado (`make preparar`) e com `seed_demo`.
2. Um volume de Processos nas três situações, montado num `manage.py shell` direto no banco — o mesmo
   padrão de `tests/performance/test_visao_institucional.py::publicar_direto` —, com ao menos 25 em
   andamento, um Processo encerrado com recurso aguardando decisão e um cancelado com o Edital 90/2026.
3. O runserver da entrada `lista-129` do `.claude/launch.json`, com `INTERFACE_SELETOR_IDENTIDADE=true`.
4. Conferir, como gestor e como julgador, a 1280 e a 375 px:
   - a aba "Em andamento" marcada e as contagens;
   - a navegação para a página 2 e o voltar do navegador;
   - a busca "90/2026" a partir de "Em andamento", com a frase e o selo "Cancelado";
   - a faixa igual nas quatro abas e na busca;
   - nenhuma rolagem lateral a 375 px (`document.documentElement.scrollWidth <= innerWidth`);
   - nenhuma violação de CSP no console.
5. Capturas em `capturas/`.

## Resultado esperado

Suíte verde; a página padrão do gestor com 20 Processos em ~3 telas no desktop; a busca encontra o
cancelado; a faixa idêntica entre recortes.
