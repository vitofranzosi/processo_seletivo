# Quickstart — 085

## Ambiente

O banco `ps_inventario_085`, cópia do `ps_inventario_080` (o seed da demonstração com os objetos que
o [inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve, inclusive os dois
recursos criados para ele), feita para não mexer no banco das outras sessões:

```bash
createdb -T ps_inventario_080 ps_inventario_085
```

O servidor, na porta 8285, com o seletor de identidade ligado — sem entrada no `.claude/launch.json`:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_085 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8285
```

## Percurso, a 1280 e a 375 px, pelo teclado

1. Entrar como `gustavo.gestor` (papel gestor) e abrir o Edital 51/2026; pela região das inscrições,
   abrir "Inscrições recebidas". O cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026 › Edital
   51/2026 › Inscrições*; o conteúdo começa pelo título.
2. Abrir a inscrição de Ana Silva. O cabeçalho acrescenta *› Inscrições › protocolo*; o nome está no
   título, e não na trilha. Voltar às Inscrições pelo link da trilha, e ao Processo.
3. Entrar como `inventario.julgadora` (papel julgador) e abrir os Recursos do Edital 51/2026:
   *… › Edital 51/2026 › Recursos*. Abrir o recurso pendente: *… › Recursos › protocolo*; "Admitir" e
   "Não admitir" no lugar de antes, e o bloco "Conferir o que se contesta" sem os documentos da
   inscrição. Voltar aos Recursos pela trilha.
4. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível; a 375 px, a trilha quebra a
   linha dentro do cabeçalho e nada rola para o lado.

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_085 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8285 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só `inscricoes`,
`inscricao-recebida`, `recursos`, `recurso-pendente` e `recurso-admitido` com altura diferente, e
nenhuma largura, título ou `h1` diferente. O mesmo com `BARRA=recolhida`, contra
`depois-da-085/antes/recolhida/resultados.json`.
