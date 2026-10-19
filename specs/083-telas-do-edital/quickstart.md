# Quickstart — 083

## Ambiente

O banco `ps_inventario_083`, cópia do `ps_inventario_telas` (o seed da demonstração com os objetos que
o [inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), feita para não mexer no
banco do inventário:

```bash
createdb -T ps_inventario_telas ps_inventario_083
```

O servidor, com o seletor de identidade ligado, pelas variáveis na linha de comando — sem entrada no
`.claude/launch.json`, que três incrementos paralelos disputariam:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_083 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8083
```

## Percurso, a 1280 e a 375 px, pelo teclado

1. Entrar como `gustavo.gestor` (papel gestor) e abrir o detalhe do Processo PS-DEMO-2026. Em
   "Novo Edital", o cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026 › Novo Edital*; voltar ao
   Processo pela trilha.
2. Abrir o Edital 76/2027, em elaboração. Pela composição, "Partir de um Edital anterior": *… ›
   Edital 76/2027 › Compor › Partir de um Edital anterior*; "Filtrar" tem o desenho de ação
   principal, e, depois de uma busca, "Limpar" o de secundária. Abrir a Prévia: *… › Edital 76/2027 ›
   Prévia*.
3. Abrir o Edital 01/2026, retificado. "Retificar": *… › Edital 01/2026 › Retificar*. A Retificação
   publicada: *… › Edital 01/2026 › Retificação*, com "O que fazer agora" antes de "Vigência". A
   conferência de um ato (pelo endereço `…/retificacoes/<id>/atos/publicar`): *… › Retificação ›
   Publicar*.
4. Abrir o Edital 51/2026 e a Condução do marco: *… › Edital 51/2026 › nome do marco*. A Prévia de
   publicação e os Resultados divulgados: o nível da classificação é link para quem a alcança. Como
   `inventario.auditora`, a Auditoria do Edital: *… › Edital 51/2026 › Auditoria*.
5. A Supervisão do PS-DEMO-2026 continua com o cabeçalho da `076` e a trilha no conteúdo.
6. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível; a 375 px, a trilha quebra a
   linha dentro do cabeçalho e nada rola para o lado.

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_083 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8383 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só as variantes do escopo —
`edital-criar`, `retificar`, `retificacao-detalhe`, `retificacao-ato-*`, `previa`, `reaproveitar`,
`marco`, `previa-de-publicacao`, `publicacoes-do-marco` e `auditoria` — com altura diferente, e
nenhuma largura, título ou `h1` diferente. O mesmo com `BARRA=recolhida`, contra
`depois-da-083/antes/recolhida/resultados.json`.
