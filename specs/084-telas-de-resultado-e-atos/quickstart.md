# Quickstart — 084

## Ambiente

O banco `ps_inventario_084`, cópia do `ps_inventario_telas` (o seed da demonstração com os objetos que
o [inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), feita para não mexer no
banco do inventário:

```bash
createdb -T ps_inventario_telas ps_inventario_084
```

O servidor, com o seletor de identidade ligado, sem entrada nova no `.claude/launch.json`:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_084 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8084
```

## Percurso, a 1280 e a 375 px, pelo teclado

1. Entrar como `paulo.presidente`, sem papel — presidir é vínculo com a comissão. Abrir o detalhe do
   Edital 51/2026.
2. Abrir a Classificação do marco final. O cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026 ›
   Edital 51/2026 › nome do marco*; o conteúdo começa pelo título. Pelo link "Consultar ato e
   proveniência", abrir o Ato: *… › Edital 51/2026 › Classificação › Ato …*. Voltar ao Edital pela
   trilha.
3. O mesmo no Corte, na Ocupação de vagas e no histórico dela, na Convocação e no histórico dela; e,
   no Edital 26/2026, no Sorteio. Nos históricos, a tela de origem fica antes de "Histórico".
4. Na Classificação, "Emitir ordem" abre a conferência: *… › nome do marco › Conferir*, com "Emitir a
   ordem" no desenho de perigo. "Cancelar e voltar", sem emitir.
5. Entrar como `inventario.exportadora` (papel exportador) e abrir Exportar para matrícula do Edital
   51/2026: *… › Edital 51/2026 › Exportar para matrícula*. Entrar como `inventario.auditora` e abrir a
   Ocupação: a mesma trilha da presidência.
6. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível; a 375 px, a trilha quebra a
   linha dentro do cabeçalho e nada rola para o lado.

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_084 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8184 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só as dez telas do escopo que
o inventário abre com altura diferente, e nenhuma largura, título ou `h1` diferente. O mesmo com
`BARRA=recolhida`, contra `depois-da-084/antes/recolhida/resultados.json`.
