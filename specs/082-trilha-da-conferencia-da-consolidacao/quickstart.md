# Quickstart — 082

## Ambiente

O banco `ps_inventario_082`, cópia do `ps_inventario_081` (o seed da demonstração com os objetos que o
[inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), feita para não mexer no
banco da `081`:

```bash
createdb -T ps_inventario_081 ps_inventario_082
```

O servidor, na porta 8084, com o seletor de identidade ligado:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_082 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8084
```

## Percurso, a 1280 e a 375 px

1. Entrar como `paulo.presidente`, sem papel — presidir é vínculo com a comissão. Pela Alocação por
   Etapa, abrir a Distribuição da Prova objetiva do Edital 51/2026.
2. Marcar duas inscrições e apertar "Consolidar as selecionadas". A conferência abre: o cabeçalho diz
   *GPS › Processos Seletivos › PS-DEMO-2026 › Alocação por Etapa › Prova objetiva › Conferir*, com os
   quatro níveis do meio como links; o conteúdo começa por "Confira antes de consolidar"; não há outra
   trilha na página.
3. No banco da demonstração as duas já têm Resultado: a tela lista as duas em "O que ficará de fora",
   não oferece o botão que consolida e mostra "Cancelar e voltar". **Não** confirmar nada.
4. Pelo teclado: o salto leva ao conteúdo, e o Tab seguinte vai a "Cancelar e voltar", com foco
   visível. A tabulação a partir do topo passa pela barra, pela trilha e por "Trocar identidade" antes
   do conteúdo.
5. A 375 px: a trilha quebra em duas linhas dentro do cabeçalho, "Trocar identidade" fica abaixo dela,
   e nada rola para o lado (`scrollWidth` igual a `clientWidth`).

Medido em 17/10/2026: a 1280, uma trilha só, quatro links (lista, Processo, Alocação, Distribuição),
o `main` começando pelo `h1`, 1280 = 1280; a 375, a trilha em duas linhas de 24 a 351 px, nenhum
elemento além da largura.
Pelo teclado, medido em 18/10/2026 com um registro de `focusin`, a partir do topo: o salto, os cinco
itens da barra (a marca, Processos Seletivos, Minhas Etapas, Sair, Recolher a barra lateral), os
quatro links da trilha, "Trocar identidade" e, só então, "Cancelar e voltar" — todos com contorno de
foco.

O caso com inscrições prontas — a tabela do alcance e "Consolidar N inscrições" — não existe no banco
da demonstração (achado registrado na pesquisa) e é provado por
`tests/interface/test_trilha_da_conferencia_da_consolidacao.py`, pela seleção e pelo alcance de todas
as prontas.
