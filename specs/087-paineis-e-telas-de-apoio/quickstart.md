# Quickstart — 087

## Ambiente

O banco `ps_inventario_087`, cópia do `ps_inventario_080` (o seed da demonstração com os objetos que
o [inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), feita para não mexer no
banco do inventário:

```bash
createdb -T ps_inventario_080 ps_inventario_087
```

O servidor, à mão — o `.claude/launch.json` não ganhou entrada para esta feature —, na porta 8087,
com o seletor de identidade e o piloto do assistente ligados:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_087 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true uv run python manage.py runserver 8087
```

## Percurso, a 1280 e a 375 px, pelo teclado

1. Entrar como `inventario.piloto` (gestor e participante do piloto). Pela barra, abrir a Visão
   Geral: o cabeçalho diz *GPS › Visão Geral*, a seção como página atual; os quatro indicadores e "O
   que esta página não mede" são os de antes. O mesmo nas Autoridades da unidade.
2. Abrir o PS-DEMO-2026 e, dele, a Supervisão: *GPS › Processos Seletivos › PS-DEMO-2026 ›
   Supervisão*; o conteúdo começa pelo título. Voltar ao Processo pelo link da trilha e abrir
   "Encerrar Processo": *… › PS-DEMO-2026 › Encerrar Processo*. "Cancelar e voltar", sem
   praticar.
3. Abrir o Edital 01/2026 e, dele, as Respostas do assistente de dúvidas: *GPS › Processos Seletivos
   › PS-DEMO-2026 › Edital 01/2026 › Respostas do assistente de dúvidas*. "Ver a resposta" é o único
   botão principal. Voltar ao Edital pela trilha e abrir "Conversar com o assistente (piloto)": o
   Assistente do Edital diz *… › Edital 01/2026 › Assistente do Edital (piloto)*, e "Perguntar" tem
   o desenho de ação principal — sem perguntar, porque a pergunta chama o modelo. O link do pé do
   Assistente leva de volta às Respostas.
4. Do Edital 01/2026, abrir "Encerrar": *… › Edital 01/2026 › Encerrar*, e "Cancelar e
   voltar".
5. Na lista, "Novo Processo Seletivo": *GPS › Processos Seletivos › Criar*; "Cancelar".
6. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível; a 375 px, a trilha quebra a
   linha dentro do cabeçalho e nada rola para o lado.

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_087 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8187 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só `supervisao`, `duvidas`,
`assistente`, `processo-criar`, `processo-ato-*` e `ato-*` com altura diferente, e nenhuma largura,
título ou `h1` diferente. O mesmo com `BARRA=recolhida`, contra
`depois-da-087/antes/recolhida/resultados.json`.

## A contagem do fechamento

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/trilhas_no_cabecalho.py
```

Lista os modelos que estendem `interface/base.html` sem o bloco `caminho_do_contexto`, e à parte os
que têm uma variante com o cabeçalho da `076` (R-005).
