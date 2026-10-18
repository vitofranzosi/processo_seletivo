# Quickstart — 089

## Ambiente

O banco do inventário, numa cópia própria, para não mexer no das features anteriores:

```bash
createdb -T ps_inventario_087 ps_inventario_089
```

O teste, num banco próprio: `DB_NAME=ps_089`. Uma vez por worktree:

```bash
cd backend && uv sync --extra dev --extra assistente
```

## Antes: três capturas

Na `main` com o PR #305, antes de qualquer mudança desta feature. Duas passadas com a barra expandida
— a segunda é a **linha de ruído**, o quanto duas capturas do mesmo código já diferem — e uma com ela
recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_089 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8189 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py ../doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/antes
```

O mesmo para `depois-da-089/ruido` e, com `BARRA=recolhida`, para `depois-da-089/antes/recolhida`.
As bases fora da gestão — a página de acesso já está no inventário (`identificar`), e o roteiro
`capturar_bases.py` captura a vitrine e o acesso do portal e a página de erro, a 1280 e a 375 px —
para `depois-da-089/bases/antes` e `depois-da-089/bases/ruido`.

O peso das respostas, antes (R-008):

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_089 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python ../doc/inventario-visual-da-gestao-2026-10-16/pesar.py
```

## Depois

As mesmas capturas para `depois-da-089/` (expandida), `depois-da-089/recolhida/` e
`depois-da-089/bases/`, e o mesmo `pesar.py`. A comparação:

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/resultados.json
```

```bash
uv run --with pillow python doc/inventario-visual-da-gestao-2026-10-16/pixels.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/antes doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/ruido doc/inventario-visual-da-gestao-2026-10-16/depois-da-089
```

Esperado: nenhum problema; nenhuma variante com medida diferente; e, pixel a pixel, nenhuma variante
cuja diferença antes→depois saia da faixa de ruído antes→ruído (mesmas regiões, intensidade máxima
não maior). O mesmo com a barra recolhida e para as bases.

## No navegador

O runserver da worktree, à mão, porta 8189 — o `.claude/launch.json` não ganha entrada:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_089 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8189
```

1. A 1280 e a 375 px: a lista, Minhas Etapas, a Distribuição, a página de acesso, a vitrine do portal.
   Iguais às capturas.
2. **Cache da segunda página.** Abrir a lista e depois Minhas Etapas; em
   `performance.getEntriesByType('resource')`, a `gestao.css` da segunda tem `transferSize` de
   cabeçalho só (revalidada) ou zero.
3. **Edição sem reiniciar.** Mudar uma cor em `gestao.css`, recarregar: o `?v=` do `<link>` muda e a
   cor nova aparece. Desfazer e recarregar: o `?v=` volta ao de antes.
4. **Impressão.** Emular mídia de impressão numa tela com trilha no cabeçalho: a barra some e a
   trilha sai como a `088` decidiu, igual ao antes (`imprimir.py` da `088`).

## Mutação dos guardiões

Para cada linha do R-005 da pesquisa: plantar no arquivo estático a violação indicada, rodar o teste
indicado, ver reprovar; desfazer, ver passar. O registro está na própria tabela do R-005.

## Suíte

```bash
cd backend && LC_ALL=pt_BR.UTF-8 make lint check test-pg DB_NAME=ps_089 POSTGRES_USER=$USER
```
