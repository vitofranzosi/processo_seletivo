# Quickstart — 077

## Ambiente

O banco do inventário, `ps_inventario_telas`, com o seed da demonstração e os três objetos que o
[inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve. A entrada `telas-077`
do `.claude/launch.json` sobe o servidor na porta 8078, com o seletor de identidade ligado.

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_telas DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8078
```

## Percurso, a 1280 e a 375 px

1. Entrar como `gustavo.gestor`, com o papel Gestor. A lista de Processos tem, acima dos
   Processos, só "Novo Processo Seletivo"; a barra tem Visão Geral, Autoridades da unidade e
   Modelos de aviso. O cabeçalho diz *GPS › Processos Seletivos*.
2. Entrar como `ana.elaboradora`, com o papel Elaborador. A lista não tem faixa de ações.
3. Entrar como `joana.avaliadora`, sem papel. Abrir Minhas Etapas pela barra: o cabeçalho diz
   *GPS › Minhas Etapas*, e o conteúdo começa pelo título.
4. Abrir a Etapa: o cabeçalho diz *GPS › Minhas Etapas › nome da Etapa*, com Minhas Etapas como
   link; o conteúdo não tem trilha.
5. Abrir uma inscrição: *GPS › Minhas Etapas › Minha Mesa › Inscrição …*. Voltar à Etapa pelo
   link "Minha Mesa" do cabeçalho.
6. Fazer 3 a 5 só pelo teclado: o salto leva ao título; a tabulação a partir do topo passa pela
   barra, pela trilha e por "Trocar identidade" antes do conteúdo.
7. A 375 px, abrir as cinco telas que estouravam (os endereços estão no `capturar.py`): nenhuma
   rola para o lado; as tabelas largas rolam dentro da moldura; os resumos do sorteio quebram.

## Inventário

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_telas DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/com-o-shell/resultados.json /caminho/de/saida/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras. O mesmo com
`BARRA=recolhida`, contra `com-o-shell/recolhida/resultados.json`.
