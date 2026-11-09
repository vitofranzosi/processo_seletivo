# Research: Centro de Controle do Edital

As decisões de produto desta spec estão na [spec](spec.md), de `D-001` a `D-009`. Aqui ficam as
questões técnicas, em `R-NNN`. Nenhuma decisão de produto nova.

## R-001 — A composição é pura, e recebe o `Andamento`

**Decisão.** `interface/centro.py` expõe `compor(edital, andamento, *, documentos, em_curso, alcance)`
e as funções `agregar`, `juntar`, `destaque`, `onde_estamos`, `fase_consultada`, todas sem acesso ao
banco. A view é a única que lê.

**Por quê.** É a mesma divisão da `127` (as `situacao_*` são puras e a leitura é uma só). Permite
provar as regras de agregação e do destaque com pontos e células montados à mão — inclusive a fixture
da seleção concluída e os dois Perfis, que nenhum cenário da `134` tem.

**Alternativa descartada.** Calcular as macrofases dentro de `andamento.py`. Mexeria no arquivo que a
`135` está editando, e misturaria derivação com apresentação.

## R-002 — A ordem das fases, os grupos e os nomes vêm de `conceitos.py`

**Decisão.** `conceitos.py` guarda: as oito fases (chave, nome, pergunta), os três grupos, os quatro
andamentos (rótulo e sinal), e os conceitos por tipo de passo (`simples`, `termo`, `curta`,
`porque`, `ao_confirmar`), mais as frases fixas da página ("Por que esta", "o GPS não escolhe a
ordem"). O cabeçalho do módulo diz que os textos são provisórios, à espera da terceira e da sétima
decisões do estudo. `centro.py` só conhece as chaves.

**Por quê.** D-006: trocar um nome é editar uma tabela. O teste de conceitos prende que todo tipo de
ponto da `127` tem conceito e que nenhum texto usa «recorte», «faixa» ou «geração» — a varredura de
vocabulário não alcança texto que chega por variável.

**Diferença do protótipo.** O texto do corte e do resultado dizia "faixa"; foi reescrito ("até onde
se chama"), para não introduzir na página um termo que ela não define.

## R-003 — A view chama as funções do detalhe, importadas

**Decisão.** `centro_do_edital.py` importa de `views` `obter_edital`, `participantes_do_edital`,
`impede_por_segregacao`, `_pendencias`, `_documentos_publicados`, `_marcos_publicados`,
`_pode_ver_avisos`, e chama `acoes.do_edital`/`hierarquia`, `atos_retificacao.em_curso`,
`andamento.do_edital`, `andamento.Alcance.de`, `andamento.linha_das_inscricoes`,
`providencias.porque_nada`, na mesma ordem e com os mesmos argumentos do detalhe.

**Por quê.** FR-4705. Uma segunda leitura divergiria da primeira na próxima mudança — é a lição da
`103` e da `104` que a `127` já cita. Importar funções privadas de `views` é o que o protótipo fazia, e
o que outros módulos de view já fazem (`views_formalizacao` importa de `views`).

**Custo.** `Alcance.de` roda duas vezes (uma dentro de `do_edital`). São poucas consultas, fixas por
Edital; o orçamento do teste as inclui.

## R-004 — A fase da providência

**Decisão.** Pela natureza: relação, semente, sorteio e ordem → Classificação; corte e apuração →
Vagas; resultado e recurso → Resultado e recursos; convocação e conferir → Convocação; distribuir,
avaliar, consolidar, reavaliar e etapa → Avaliação, **salvo** a Etapa governada pela faixa, que vai a
Vagas. A Etapa de uma providência é o segundo elemento da chave (`("etapa", eid, …)`), comparado com
o `id` das Etapas dos pontos do grupo governado (D-004). Natureza desconhecida → Classificação, com
teste que prende que nenhuma natureza da `127` cai nesse caso.

## R-005 — A paralela ao sorteio

**Decisão.** D-008: há paralela quando existe ao menos um Perfil com marco, todos os marcos de todos
os Perfis são por sorteio (`andamento.por_sorteio`), nenhum declara `drawMethod.qualifyingStageId`, e
há ponto de Etapa fora do grupo governado. Lê só `Ponto.marco`, que o `Andamento` já carrega.

## R-006 — O destaque e o que ele destrava

**Decisão.** Regras de D-005, sobre as providências **suas** (grupo `sua` da `127`). O que a ação
destrava são os passos da **mesma fase**, do **mesmo Perfil**, que vêm depois do primeiro passo com
ação e ainda não começaram. Sem passos a destravar, a regra 2 não se aplica.

**Diferença do protótipo.** O protótipo juntava os roteiros de todos os Perfis; aqui o roteiro do
Perfil da providência (`perfil_id`) é o que conta, e a providência sem Perfil (Etapa) olha todos.

## R-007 — A fase consultada

**Decisão.** `?fase=<chave>`; chave inválida ou ausente → a regra fixa da spec (US3, cenário 1). O
cartão da fase consultada leva `aria-current="true"` no link, um texto visualmente oculto "fase
consultada", e a classe `consultada`. Nenhuma fase em curso leva `aria-current`.

**Por quê `true` e não `step`.** `step` diria "este é o passo atual do processo", que é justamente a
leitura que a primeira decisão do estudo recusa. `true` marca o item corrente de um conjunto de
links, que é o que a fase consultada é.

## R-008 — Encerrar e Cancelar

**Decisão.** Saem de `acoes.hierarquia(conjunto).terminais`, desenhados pelo mesmo
`_acao_do_edital.html`, dentro de um `<details>` fechado em "Administração e histórico". Quem não os
tem não os recebe, porque o conjunto não os traz.

## R-009 — A folha

**Decisão.** `interface/telas/centro.css`, carregada pelo bloco `estilo_da_pagina`, junto de
`grupos/terminais.css` e `telas/andamento.css` (as situações da `127` e as molduras de tabela). As
classes novas têm prefixo `cc-` e regra nessa folha; o guardião de classes lê `interface/telas/`.
Nenhuma regra fecha `}}` na mesma linha (o guardião de estáticos).

## R-010 — Os testes de papel nos cenários da `134`

**Decisão.** Os cenários são montados pelo comando de carga, como em
`tests/integration/treinamento/`, com a chave ligada por fixture. Os papéis entram pelo seletor:
`treino.presidencia` e `treino.avaliacao1` sem papel (o vínculo com a comissão dá o resto), o Gestor
com `gestor`, o Publicador com `publicador`. Um cenário por caso de teste — os cenários não se
somam no mesmo banco sem colisão — e o parametrizado por papel lê a mesma página com quatro
identidades.
