# Quickstart — 086

## Ambiente

O banco `ps_inventario_086`, cópia do `ps_inventario_telas` (o seed da demonstração com os objetos que
o [inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve, inclusive o aviso
`c1841d6c-924b-41a8-8d9a-99a17aacb900`), feita para não mexer no banco do inventário:

```bash
createdb -T ps_inventario_telas ps_inventario_086
```

Servidor local com o seletor de identidade ligado (sem entrada nova no `.claude/launch.json`):

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_086 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8286
```

## Percurso, a 1280 e a 375 px, pelo teclado

1. Entrar como `gustavo.gestor` (papel gestor). Abrir o detalhe do Edital 51/2026 e "Ver e enviar
   avisos". O cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026 › Avisos aos
   candidatos*; o conteúdo começa pelo título.
2. Abrir o aviso confirmado. A trilha termina em *Aviso de DD/MM/AAAA*, com os Avisos aos candidatos
   como link. "Interromper o envio" leva à conferência: *… › Avisos aos candidatos › Aviso de
   DD/MM/AAAA › Interromper*; os botões vêm no rodapé, separados do motivo. "Voltar sem interromper",
   sem interromper.
3. No aviso, "Reenviar, com justificativa…" (se oferecido) ou, pelos Avisos aos candidatos, "Avisar
   candidatos — resultado …": na primeira, a trilha passa pelos Avisos aos candidatos e pelo aviso;
   na segunda, pelos Avisos aos candidatos. A frase de que é uma prévia é a primeira coisa depois do
   título. Cancelar, sem enviar.
4. Pela barra, Modelos de aviso: *GPS › Modelos de aviso*, sem link; "Novo modelo" na faixa de ações.
   Abrir um modelo: *GPS › Modelos de aviso › nome*; "Salvar o modelo" e "Cancelar" no rodapé.
   Cancelar, sem salvar.
5. Num Edital sem resultado publicado (76/2027), os Avisos aos candidatos dizem "Nenhum resultado…" e
   "Nenhum aviso…" na caixa do estado vazio.
6. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível; a 375 px, a trilha quebra a
   linha dentro do cabeçalho e nada rola para o lado.

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_086 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8286 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só `avisos-do-edital`,
`avisos-do-edital-antes`, `aviso`, `aviso-interromper`, `aviso-do-resultado`, `aviso-reenviar`,
`modelos-de-aviso`, `modelo-de-aviso` e `modelo-de-aviso-novo` com altura diferente, e nenhuma
largura, título ou `h1` diferente. O mesmo com `BARRA=recolhida`, contra
`depois-da-086/antes/recolhida/resultados.json`.
