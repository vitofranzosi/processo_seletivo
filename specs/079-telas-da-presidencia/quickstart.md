# Quickstart — 079

## Ambiente

O banco do inventário, `ps_inventario_telas`, com o seed da demonstração e os objetos que o
[inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve. A entrada `telas-079`
do `.claude/launch.json` sobe o servidor na porta 8081, com o seletor de identidade ligado.

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_telas DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8081
```

## Percurso, a 1280 e a 375 px, só pelo teclado

1. Entrar como `paulo.presidente`, sem papel — presidir é vínculo com a comissão. Em Minhas Etapas,
   abrir "Gerir comissão" do PS-DEMO-2026. O cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026 ›
   Comissão*; o conteúdo começa pelo título; a seção "Membros (3)" traz o filtro e os cartões.
2. Filtrar por "joana": o título continua "Membros (3)", e a linha diz "1 de 3 membros.". Limpar.
3. Abrir "Alocação por Etapa" pela faixa. A barra fica no topo; o cabeçalho diz *… › PS-DEMO-2026 ›
   Alocação por Etapa*; a matriz cabe sem rolar na tela larga. Marcar uma caixa e salvar por "Salvar
   alocação": "Alocação salva.". Desmarcar e salvar de novo, para deixar o banco como estava.
4. Abrir "Distribuir" da Prova objetiva do Edital 51/2026. O cabeçalho diz *… › Alocação por Etapa ›
   Prova objetiva*; logo abaixo do título e do Edital, a faixa com Impedimentos, Registrar ocorrência,
   Resultados e Trilha. Subir à Alocação pelo link da trilha.
5. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível; a 375 px, nada rola para o
   lado.
6. A conferência da inclusão: em "Adicionar membro", digitar um identificador e "Continuar". O
   cabeçalho diz *… › Comissão › Conferir*; "Cancelar e voltar", sem confirmar.

## Inventário

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_telas DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-078/resultados.json /caminho/de/saida/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só `comissao`, `alocacoes` e
`distribuicao` com largura ou altura diferente. O mesmo com `BARRA=recolhida`, contra
`depois-da-078/recolhida/resultados.json`. O `comparar.py` só acusa `status` e estouro: a comparação
de largura, altura, título e `h1`, variante a variante, é a do `medidas.py` desta pasta.
