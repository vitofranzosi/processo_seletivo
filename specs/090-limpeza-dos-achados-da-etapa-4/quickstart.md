# Quickstart — 090

## Ambiente

Um banco de inventário próprio, cópia do mais recente (o seed da demonstração com os objetos que o
[inventário](../../doc/inventario-visual-da-gestao-2026-10-16.md) descreve), para não mexer no de
outra feature:

```bash
createdb -T ps_inventario_089 ps_inventario_090
```

O servidor, numa porta livre, com o seletor de identidade ligado (sem entrada nova no
`.claude/launch.json`):

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_090 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8290
```

## Percurso, a 1280 e a 375 px

1. **A marca.** Como `gustavo.gestor`, o detalhe do Processo PS-DEMO-2026: na árvore de
   acessibilidade, "Encerrar Processo" e "Cancelar Processo" têm "irreversível" como descrição; "Ver
   a supervisão" e os demais, nenhuma. O mesmo no detalhe do Edital 51/2026 ("Encerrar", "Cancelar") e
   do 76/2027 como `ana.elaboradora` (os atos indisponíveis seguem com o motivo). Como
   `ana.elaboradora`, o detalhe da Retificação publicada do 01/2026.
2. **A trilha das consultas.** Como `paulo.presidente`, os Resultados, a Trilha da avaliação e as
   Conclusões preservadas da Prova objetiva do Edital 51/2026: a trilha tem quatro links. Como
   `inventario.auditora`, as mesmas três: "Alocação por Etapa" e "Prova objetiva" são texto; seguir
   "Processos Seletivos" e o Processo abre as duas telas.
3. **O rodapé.** A 375 px, a conferência da interrupção de um aviso, a edição de um modelo de aviso e
   a conferência de um ato do Processo: os botões do rodapé têm o rótulo numa linha, e o segundo vem
   abaixo do primeiro quando os dois não cabem. A 1280 px, lado a lado, como antes.
4. **A prévia pelo marco.** Neste banco o resultado do marco FINAL do Edital 51/2026 já foi avisado (o
   `AVISO` do inventário), e os Resultados divulgados dizem "Não há publicação vigente ainda não avisada
   neste marco", sem o link "Avisar candidatos" — que, com resultado pendente, leva a porta no endereço
   (`test_os_resultados_divulgados_abrem_a_previa_pela_porta_deles`). Abra a prévia direto pelo
   endereço do link, como `paula.publicadora`:
   `/gestao/editais/af86be76-27f3-4e6a-b621-2b0771c323b2/marcos/00000000-0000-0000-0051-0000000000a1/avisos/novo?de=marco`.
   A trilha termina em "… › Classificação › Resultados divulgados › Avisar candidatos", com a
   Classificação em texto (a publicadora não a abre), e "Cancelar" volta aos Resultados divulgados. Sem
   `de=marco`, a trilha é a de antes, dos Avisos aos candidatos.

## Inventário

O mesmo roteiro, antes e depois da mudança, com a barra expandida e recolhida:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_090 DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 BARRA=expandida PORTA=8197 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py /caminho/de/saida
```

```bash
python3 doc/inventario-visual-da-gestao-2026-10-16/medidas.py doc/inventario-visual-da-gestao-2026-10-16/depois-da-090/antes/resultados.json doc/inventario-visual-da-gestao-2026-10-16/depois-da-090/resultados.json
```

Esperado: nenhum problema; `estouram na nova` vazio nas duas larguras; a 1280 px, nenhuma variante
diferente (a de `aviso-do-resultado-pelo-marco` muda a trilha na mesma linha, e não de medida); a 375
px, só variantes com o rodapé comum, e só de altura — medido em 18/10/2026: `aviso-interromper`,
`ato-encerrar`, `ato-cancelar` e `processo-ato-ativar`. O mesmo com `BARRA=recolhida`, contra
`depois-da-090/antes/recolhida/`.
