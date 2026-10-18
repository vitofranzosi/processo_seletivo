# Quickstart — 088

## Ambiente

O banco `ps_inventario_088`, cópia do `ps_inventario_telas` (o seed da demonstração com os objetos
que o [inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), migrado até a
`main` com as features de que esta depende:

```bash
createdb -T ps_inventario_telas ps_inventario_088
```

O servidor sobe por linha de comando, sem entrada nova no `.claude/launch.json`, numa porta que
nenhuma outra sessão usa (8288), com o seletor de identidade ligado:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_088 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8288
```

## Percurso

1. **A trilha no papel.** Abrir, com a mídia de impressão emulada no navegador, a inscrição da Mesa
   (como quem avalia), um Ato de classificação (como `paulo.presidente`), uma Inscrição recebida
   (como `gustavo.gestor`) e um Recurso (como `inventario.julgadora`). Em cada um, a trilha do cabeçalho vem antes do título; a barra lateral e
   "Trocar identidade" não aparecem. Sem a emulação, a tela é a de antes.
2. **A mesma coisa em papel de verdade.** O `imprimir.py` do inventário faz o percurso das quatro,
   da recusa e de um aviso, cada uma com a identidade que a abre: emula a mídia de impressão, lê o
   que fica visível do cabeçalho e da barra, e imprime em A4 pelo Chrome sem interface:

   ```bash
   cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_088 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 PORTA=8298 uv run --with playwright python ../doc/inventario-visual-da-gestao-2026-10-16/imprimir.py /caminho/de/saida
   ```

   ```bash
   pdftotext -layout /caminho/de/saida/ato-de-ordenacao.pdf - | head -3
   ```

   Esperado: a trilha inteira (*GPS … › Edital NN/AAAA › …*) antes do título, sem "Trocar
   identidade". O "antes" se tira do mesmo jeito, rodando o script de dentro de um `git archive` da
   `main` (o `cd` vai para o `backend` extraído, e `uv run --project` aponta para o desta worktree).
3. **A hora do aviso.** Abrir o histórico de um aviso, a conferência da interrupção dele e a prévia
   de reenviá-lo: nas três, o rótulo do aviso na trilha é *Aviso de DD/MM/AAAA às HH:MM*, o texto do
   título.
4. **O recorte do Ato.** Num Edital com reserva, abrir o Ato de classificação da lista PPI e seguir
   "Classificação" na trilha: a tela que abre nomeia a lista PPI como recorte atual. No ato da ampla
   concorrência, o link leva à Classificação sem recorte, como antes.

## Inventário

O mesmo roteiro da `080`, antes e depois, com `BARRA=expandida` e `BARRA=recolhida`, guardado em
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/` (com `antes/`), e comparado por
`comparar.py` e por `medidas.py`.

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; só `aviso`,
`aviso-interromper` e `aviso-reenviar` podem mudar, e só de altura (o rótulo mais longo pode quebrar
a linha da trilha a 375 px). A regra de impressão não muda medida nenhuma na tela.
