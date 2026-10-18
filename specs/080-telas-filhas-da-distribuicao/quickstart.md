# Quickstart — 080

## Ambiente

O banco `ps_inventario_080`, cópia do `ps_inventario_telas` (o seed da demonstração com os objetos que
o [inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), feita para não mexer no
banco do inventário:

```bash
createdb -T ps_inventario_telas ps_inventario_080
```

A entrada `telas-080` do `.claude/launch.json` sobe o servidor na porta 8082, com o seletor de
identidade ligado.

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_080 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8082
```

## Percurso, a 1280 e a 375 px, pelo teclado

1. Entrar como `paulo.presidente`, sem papel — presidir é vínculo com a comissão. Abrir a Distribuição
   da Prova objetiva do Edital 51/2026.
2. Pela faixa, abrir Impedimentos. O cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026 ›
   Alocação por Etapa › Prova objetiva › Impedimentos*; o conteúdo começa pelo título; a seção
   "Registrar um impedimento" vem antes de "Avaliações fora do conjunto elegível". Voltar à Etapa
   pelo link da trilha.
3. O mesmo em Registrar ocorrência, Resultados e Trilha; da Trilha, abrir as conclusões preservadas
   pelo link do texto. Na Trilha e nas Conclusões, "Filtrar" tem o desenho de ação principal.
4. Na Distribuição, marcar uma atribuição em "Quem está alocado" e "Retirar as selecionadas". A
   conferência diz *… › Prova objetiva › Conferir*. "Cancelar e voltar", sem retirar — no banco do
   inventário, as atribuições estão concluídas, e a conferência diz que nada pode ser retirado.
5. Entrar como `inventario.auditora` (papel auditor) e abrir a Auditoria da comissão do PS-DEMO-2026:
   *GPS › Processos Seletivos › PS-DEMO-2026 › Auditoria da comissão*, e "Filtrar" como ação
   principal. A Auditoria do Edital 51/2026 continua com a trilha no conteúdo.
6. Em todos os passos: o salto leva ao título; a tabulação a partir do topo passa pela barra, pela
   trilha e por "Trocar identidade" antes do conteúdo; o foco é visível; a 375 px, a trilha quebra a
   linha dentro do cabeçalho e nada rola para o lado.

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_080 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8197 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só `impedimentos`,
`registrar-ocorrencia`, `resultados-da-etapa`, `trilha-da-avaliacao`, `conclusoes-preservadas` e
`auditoria-comissao` com altura diferente, e nenhuma largura, título ou `h1` diferente. O mesmo com
`BARRA=recolhida`, contra `depois-da-080/antes/recolhida/resultados.json`.
