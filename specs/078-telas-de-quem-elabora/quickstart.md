# Quickstart — 078

## Ambiente

O banco do inventário, `ps_inventario_telas`, com o seed da demonstração e os objetos que o
[inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve. A entrada `telas-078`
do `.claude/launch.json` sobe o servidor na porta 8079, com o seletor de identidade ligado.

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_telas DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8079
```

## Percurso, a 1280 e a 375 px, só pelo teclado

1. Entrar como `ana.elaboradora`, com o papel Elaborador. Na lista, abrir o Processo
   PS-DEMO-2026-R. O cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026-R*, com Processos
   Seletivos como link; o conteúdo começa pelo título; "O que fazer agora", com "Elaborar o Edital
   76/2027", vem antes da tabela dos Editais.
2. Abrir o Edital 76/2027 pela tabela. O cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026-R ›
   Edital 76/2027*; "O que fazer agora" vem antes de "Quem atuou" — à esquerda na tela larga,
   primeiro no celular.
3. Abrir "Elaborar o Edital". O cabeçalho diz *… › Edital 76/2027 › Compor*; passar por duas etapas
   pela navegação das etapas; a trilha não muda. Voltar ao Processo pelo código na trilha.
4. Entrar como `gustavo.gestor`, com o papel Gestor, e abrir PS-DEMO-2026. "O que fazer agora", com
   Encerrar e Cancelar contornados e o impedimento, vem antes dos Editais, e os dois antes de "Onde
   cada Edital está".
5. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível.
6. A 375 px, abrir as conclusões preservadas, reaproveitar Edital e os anexos da composição (os
   endereços estão no `capturar.py`): nenhuma rola para o lado, agora sem a regra da própria tela.

## Inventário

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_telas DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-077/resultados.json /caminho/de/saida/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só as telas desta feature e as
três da `077` com largura ou altura diferente. O mesmo com `BARRA=recolhida`, contra
`depois-da-077/recolhida/resultados.json`.
