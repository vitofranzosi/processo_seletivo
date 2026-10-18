# Quickstart — 081

## Ambiente

O banco `ps_inventario_081`, cópia do `ps_inventario_080` (o seed da demonstração com os objetos que o
[inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), feita para não mexer no
banco de outra feature:

```bash
createdb -T ps_inventario_080 ps_inventario_081
```

A entrada `telas-081` do `.claude/launch.json` sobe o servidor na porta 8083, com o seletor de
identidade ligado.

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_081 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8083
```

## Percurso, a 1280 e a 375 px

1. Entrar como `paulo.presidente`, sem papel, e abrir a Distribuição da Prova objetiva do Edital
   51/2026.
2. Abaixo da tabela das inscrições: "Distribuir as selecionadas" é o botão cheio; "Consolidar as
   selecionadas" é o secundário, contornado e da mesma altura, com a marca "irreversível" logo depois,
   centrada na linha. A frase "Consolidar é transformar…" continua antes dos dois.
3. A 375 px, a linha quebra dentro da largura, e a marca não estica.
4. Marcar uma inscrição e apertar "Consolidar as selecionadas": abre a conferência de dois passos, como
   antes. Voltar sem confirmar.
5. A Alocação sem presidência não está no banco do inventário; o aviso "Designe a presidência antes de
   alocar." é provado pelos testes (`test_alocacoes.py`, `test_achados_das_revisoes.py`).

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_081 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8197 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/comparar.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/resultados.json
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; nenhuma variante com largura,
título ou `h1` diferente, e no máximo a `distribuicao` com altura diferente. O mesmo com
`BARRA=recolhida`, contra `depois-da-081/antes/recolhida/resultados.json`.
