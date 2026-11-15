# A migração do design system para toda a gestão: o antes e o depois

*15/11/2026, na branch `claude/173-migracao-ds-antes-e-depois`, que parte da branch do piloto
(`claude/172-piloto-implementacao`, PR #564, em `d6705ce5`). O "antes" é a `main` em `499491be`. A
medição veio antes da spec, a pedido do usuário; a spec é a
[`175`](../../../specs/175-migracao-do-design-system/spec.md), escrita depois da revisão de código.*

> **Depois da revisão de código (15/11, aprovada pelo usuário).** Os dois-pontos que a folha gerava
> depois do rótulo das listas de definição saíram (escreviam "Volta atrás?:" nos rótulos do Sorteio
> que são pergunta), e com eles a classe `rotulo-com-dois-pontos` da Revisão; a folha do piloto deixou
> de repetir as regras que a migração levou à comum; e `grupos/confirmacao-de-ato.css`, que ficou sem
> regra, foi retirada. As medidas abaixo são da branch antes dessas correções, que não mudam a
> composição de nenhuma tela além do sinal de pontuação.

## O resultado

**O HTML com as telas lado a lado é [`antes-e-depois.html`](antes-e-depois.html)** (13 MB,
autocontido, fora do git, como o do piloto; remonta-se pelos scripts). Lado a lado, cortina e
alternar, as medidas de cada tela, e a captura do celular nas dez telas que cresceram nele. A tabela
tela a tela está em [`telas-comparadas.csv`](telas-comparadas.csv).

**Mudaram 110 das 123 telas, e todas são da gestão.** As 13 iguais são as oito do portal público, as
quatro de acesso e o guia incorporado, que não carregam a folha comum da gestão (uma tela de acesso
difere em 0,02% dos pixels, e é dado: a sugestão de quem mais exerceu cada papel cresce com o próprio
rastreio).

**As páginas ficaram mais baixas: −3,4% na altura somada a 1440 px** (221.200 → 213.786 px). 72 telas
ficaram mais baixas, 37 com a mesma altura (quase todas já cabiam na janela de 900 px) e **uma ficou
mais alta**: a configuração da agenda da etapa, **+12 px**, porque as ações pequenas ("+ janela",
"+ Acrescentar banca") passaram a ter 32 px, como pede o padrão do botão. As que mais baixaram foram
as Novidades (−600 px), o histórico da Ocupação (−512 px), o sorteio e a convocação (−280 px).

| Família | Telas | Mudaram | Altura somada a 1440 px | Mais altas no celular |
|---|---:|---:|---|---:|
| P2.1 · Confirmação de ato | 19 | 19 | 23.809 → 22.667 px (-4,8%) | 0 |
| P2.2 · Lista, registro e histórico | 24 | 24 | 29.228 → 28.414 px (-2,8%) | 2 |
| P2.4 · Formulário de configuração | 20 | 20 | 50.041 → 49.469 px (-1,1%) | 2 |
| P2.5 · Central de trabalho e página de entidade | 17 | 17 | 31.498 → 30.601 px (-2,8%) | 2 |
| P2.6 · Operação, avaliação e conferência | 22 | 22 | 34.626 → 32.755 px (-5,4%) | 3 |
| Acesso (só tokens) | 4 | 0 | 6.806 → 6.806 px (+0,0%) | 0 |
| Guia incorporado (P3.5) | 1 | 0 | 11.336 → 11.336 px (+0,0%) | 0 |
| Outras telas da gestão | 8 | 8 | 21.581 → 19.463 px (-9,8%) | 1 |
| Público | 8 | 0 | 12.275 → 12.275 px (+0,0%) | 0 |

**Quebrou uma, na primeira passada, e foi corrigida.** A regra das listas de definição pôs em grade
de duas colunas o cartão "Quem atuou" do Centro do Edital, que agrupa cada par num `div`: os grupos
caíram um em cada coluna, e a página do Edital passou a rolar de lado a 768 px. A regra ganhou o
caso (`dl:has(>div)` fica em bloco, e o par fica na linha dentro do grupo), o lado "depois" foi
rastreado de novo, e o HTML é dessa segunda passada. Nela, nenhuma tela rola de lado a 375 nem a
768 px, nenhum elemento novo passa da borda, e nenhum nó caiu abaixo do contraste.

## Para decidir antes da spec

1. **No celular, os indicadores ficam um por linha.** Com o mínimo de 9rem por caixa, dois não cabem
   lado a lado a 375 px, e cada número ocupa a largura inteira: dez telas cresceram mais de 40 px no
   celular, até +182 px na Ocupação e +124 px nos documentos da convocação (antes, iam dois ou três
   por linha). A Ocupação do piloto já fazia isso, e o usuário a aprovou na largura de desktop. A
   saída mais simples é um mínimo menor no estreito (duas colunas a 375 px), e é decisão do padrão.
2. **As fichas com rótulo em caixa alta acima do valor** (o Centro do Edital, a peça do recurso)
   mantiveram o desenho delas: a regra comum tem a especificidade de um elemento, e não desfaz lista
   com desenho próprio. Ou elas também passam a "rótulo e valor" na linha (uma regra por ficha), ou
   ficam como estão (P-2 da spec).
3. **Ainda há medidas de leitura fora de `--leitura`**: 80ch em `conducao-do-recorte.css` saiu, mas
   ficam larguras de coluna em rem que limitam texto (`.conducao` em 72rem, `.definicao-da-formalizacao`
   e `.lista-da-mesa` em 44rem, as da entrada em `acesso.css`). São colunas, e não prosa: a branch
   não as tocou.
4. **A folha do piloto continua**, com as regras da Ocupação e da Lista, que são de tela; as regras
   genéricas dela agora repetem as comuns. Na spec, ela se desfaz: o que é de tela vai para
   `telas/ocupacao` e `telas/lista`, e a classe `.piloto-ds` sai.
5. **O que esta medição não cobre**: o portal autenticado (fora do rastreio, e fora da migração), os
   64 estados da fotografia do piloto, que exigem montar cenários um a um, e o conteúdo (o rastreio
   compara pixels e medidas, e não texto). A spec deve pedir a fotografia e a comparação de conteúdo
   do piloto para as telas que tiverem estado.

## Verificação

`tests/interface` passou inteiro (5984 passando, 1 pulado). Cinco guardiões prendiam as medidas
antigas e foram reescritos para prender as novas, sem afrouxar o que exigem do portal:
`test_larguras.py` (o texto da gestão sem `--leitura`, o campo na largura do formulário, o portal
ainda com a medida, e a consulta estreita da Visão Geral achada pelo conteúdo, e não por ser o primeiro
bloco de 40rem), `test_polish_da_056.py` (a seção gerada sem a medida; a lista da Revisão com a classe
nova), `test_polish_da_058.py` (o motivo da sucessão continua o mesmo controle, sem a medida) e duas
classes que perderam a única regra entraram em `CLASSES_SEM_DESENHO`.

`cd backend && make lint check test-pg`, em 15/11: `lint` e `check` verdes, e a suíte em **21 380
passando e 15 pulados, sem falha** (787 s, 4 workers), os mesmos números do piloto.

## O que a branch faz

Leva para todas as telas da gestão os cinco padrões que o usuário aprovou no piloto, sem a classe de
escopo `.piloto-ds`. A folha do piloto continua carregada pelas cinco telas dele, como estava.

| Padrão | Onde |
|---|---|
| **O texto ocupa a largura do conteúdo.** Saem as 52 declarações `max-width:var(--leitura)` das folhas da gestão — `main>p`, `.sub`, `.ajuda`, `legend+p`, a medida da P0 nas confirmações e as das folhas de grupo e de tela —, e os 44rem de `.ajuda` e `.explicacao` | `gestao/componentes.css`, `gestao/telas.css`, `grupos/*.css`, `telas/*.css` |
| **Os indicadores de um grupo dividem a linha em partes iguais** (`.resumo` em grade `repeat(auto-fit,minmax(9rem,1fr))`) | `gestao/componentes.css` |
| **O campo de texto, a área de texto e a seleção ocupam a largura do formulário**; número e data continuam do tamanho do que recebem | `gestao/formularios.css` |
| **A lista de definição põe o rótulo e o valor na mesma linha**, o rótulo em peso maior e sem dois-pontos gerados; no celular o valor desce. Pelo `:where(main)`, toda lista com desenho próprio continua com o dela; a que agrupa cada par num `div` fica em linha dentro do grupo | `gestao/telas.css` |
| **Os componentes**: cartão (`.consequencias`) com `--linha`, `--raio` e `--sombra-1`; aviso com o raio da escala; `.botao` e `.acao` de altura única (40 e 32 px); respiro menor na barra de gravação e no subtítulo | `gestao/telas.css` |

O portal do candidato não muda: ele não carrega as folhas da gestão, e a varredura confirma (as 13
telas públicas e de acesso saíram idênticas pixel a pixel).

## Como foi medido

O instrumento do estudo (`referencia-p0/scripts/rastrear_tudo.sh`, sem o passo do portal, em
[`scripts/rastrear_gestao.sh`](scripts/rastrear_gestao.sh)) rodou contra a `main` (entrada
`piloto-antiga`, 8172) e contra esta branch (entrada `migracao-ds`, 8175), as duas sobre o mesmo
`ps_piloto_validacao`: a cópia da referência da P0, migrada (`piloto/scripts/montar_banco_da_validacao.sh
referencia`). Mesmas identidades, mesmos papéis, as mesmas 123 telas visitadas nos dois lados.

[`scripts/comparar_telas.py`](scripts/comparar_telas.py) recorta cada captura de 1440 px na coluna do
`main`, compara os pixels e junta as medidas do `telas.csv` e das larguras;
[`scripts/montar_html.py`](scripts/montar_html.py) monta o HTML autocontido, no modelo do antes e
depois do piloto (lado a lado, cortina, alternar e as medidas por tela).

```bash
cd backend && uv run --no-project --with pillow python ../doc/auditoria-design-system-2026-11-14/migracao/scripts/comparar_telas.py <antes> <depois> comparacao.json img
```

```bash
python3 ../doc/auditoria-design-system-2026-11-14/migracao/scripts/montar_html.py comparacao.json img ../doc/auditoria-design-system-2026-11-14/medicoes/gerar_inventario.py antes-e-depois.html
```

**Uma tela "quebrou"** quando passou a rolar de lado a 375 ou 768 px, quando um elemento novo passou
da borda nessas larguras, quando ganhou nó abaixo do contraste, ou quando a leitura das capturas
achou defeito de composição. **"Mais alta"** é a altura da página a 1440 px.
