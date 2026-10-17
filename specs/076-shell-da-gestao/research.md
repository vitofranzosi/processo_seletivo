# Pesquisa — 076

## R-001 — Onde a barra se monta

**Decisão**: um processador de contexto próprio, `interface/navegacao.py::contexto_da_navegacao`,
ao lado do de identidade, que devolve os grupos e os itens já filtrados e a seção atual.

**Por quê**: o `base.html` não recebe nada das views — a identidade chega pelo processador de
`identidade.py` —, e é assim que a barra alcança as 59 telas sem tocar nenhuma. `identidade.py` é a
fronteira de autenticação, o módulo que muda quando o diretório chegar; navegação não é
autenticação, e não entra nele.

**Alternativas**: uma tag de template que lê o ator — esconderia a regra num lugar que os testes de
autorização não visitam; montar em cada view — 59 edições.

## R-002 — O mesmo critério da lista, por construção

**Decisão**: os predicados de cada item moram em `navegacao.py`, e a view da lista passa a ler os
seus `pode_*` deles. A lista e a barra deixam de poder divergir.

**Por quê**: `FR-1714` pede "o mesmo critério que hoje condiciona os botões da lista". Copiar as
três condições seria criar a segunda grafia que a `033` existe para impedir. A tela da lista não
muda: a view entrega as mesmas chaves, com os mesmos valores.

## R-003 — A seção atual sai do endereço

**Decisão**: a seção de cada tela é a do prefixo mais longo do caminho entre os itens: `/gestao/minhas-etapas…`
é Minhas Etapas, `/gestao/visao-geral` a Visão Geral, `/gestao/autoridades` as Autoridades,
`/gestao/modelos-de-aviso…` os Modelos; todo o resto da gestão é Processos Seletivos. Na própria
página da seção o item é marcado como a página atual; abaixo dela, como a seção atual.

**Por quê**: as rotas já são hierárquicas — as da Mesa pendem de `minhas-etapas` de propósito
(`urls.py`) —, e decidir pelo endereço não exige marcação nas telas.

**Alternativa**: um bloco `secao` em cada template — 59 edições, e um esquecimento vira seção errada
em silêncio.

## R-004 — O caminho do topo para na seção

**Decisão**: o cabeçalho de contexto diz *GPS › seção*, em texto, e não como navegação. O resto
do caminho é a trilha que a tela já tem, e o link da seção é o da barra. Na primeira versão a seção
era link, e a revisão do PR mostrou o efeito: nas telas com trilha, "Processos Seletivos" aparecia
como link três vezes seguidas — barra, caminho, trilha — para quem percorre os marcos.

**Por quê**: 54 das 59 telas já abrem com `nav.trilha` ("Trilha de navegação"), com o código do
Processo, o número do Edital e a Etapa — mais do que o topo saberia dizer sem tocar a view. Repetir
o título da tela no topo poria o mesmo nome três vezes em sequência (topo, trilha, `h1`), e dois
guardiões (`test_acessibilidade_da_012.py`, `test_compor.py`) prendem a trilha onde está.

**Alternativas**: renderizar de novo o bloco `titulo` por uma tag — funciona, mas duplica a
trilha; levar a trilha das 54 telas para o topo — é mexer no conteúdo, e é a etapa 4 do estudo.

## R-005 — Recolher no celular sem script

**Decisão**: abaixo de 64rem, as seções e o pé moram num elemento com o atributo `popover`, e o
botão "Seções" o abre por `popovertarget`. Na tela larga, a folha o mostra sempre, como coluna. Num
navegador sem suporte a `popover`, `@supports not selector(:popover-open)` esconde o botão — e a
barra, que nenhuma regra do navegador esconde, fica aberta.

**Por quê**: `tests/interface/test_visao_geral.py` afirma que a Visão Geral não carrega script
nenhum, e qualquer `script` no `base.html` iria a ela. O comportamento nativo dá de graça o que
o script daria: o estado aberto anunciado à tecnologia assistiva, Esc para fechar, o toque fora
para fechar, e a próxima tabulação depois do botão entrando no painel.

**Alternativas**: link para `#secoes` com `:target` — funciona sem script, mas mexe no endereço e
não anuncia o estado; `details`/`summary` — na tela larga ele teria de estar sempre aberto, e o
servidor não sabe a largura; um script estático — reprova o guardião da Visão Geral; a caixa de
marcação com rótulo — a palavra está proibida na tela de identificação por um guardião de
substring.

## R-006 — A estrutura

```
link de salto
.barra            marca (sigla GPS) · controle de recolher · botão Seções · #secoes (popover) [ nav Seções da gestão (Trabalho, Unidade) · avatar, pessoa e Sair ]
.area             header.contexto [ GPS › seção · Trocar identidade ] · main#conteudo (intacto)
```

Na tela larga, `.barra` é uma coluna fixa de 15rem, presa ao rolar, com o pé no fim da altura da
janela; `.area` leva o resto, com `minmax(0,1fr)`. Sem identidade, o `base.html` mostra o
`header.topo` de hoje, só com a marca.

Os guardiões que a varredura achou e que a estrutura respeita: `a.marca` com `href` logo depois de
`class` (`test_visao_geral.py`); nenhuma regra `.marca` solta (`test_larguras.py`); nenhum
`max-width` em px, nenhum `@media (max-width:40rem)`, cada `@media` fechando em linha própria
(`test_larguras.py`, `test_polish_da_058.py`, `test_estaticos.py`); o item atual sem classe
modificadora — o seletor é `[aria-current]` —, porque `.x.atual` faria de `atual` um modificador
cobrado em toda tela (`test_acessibilidade.py`); o botão com `type="button"` e classe; nenhum
`h1` fora do `main`; a barra e o caminho fora do `main`, que vários testes recortam.

## R-008 — O que a revisão do PR acrescentou

- **A barra se monta só quando lida.** O processador entrega um objeto preguiçoso sob o nome
  `navegacao`; os fragmentos do htmx, que não estendem o `base.html`, não pagam a montagem.
- **No celular a barra do topo fica presa à janela**, com `scroll-padding-top` para não cobrir o
  alvo das âncoras; na Alocação, não, porque ali quem se prende à janela é o cabeçalho da matriz.
- **Navegador sem `popover`**: a barra quebra a linha e o painel toma a largura toda.
- **Painel aberto no celular e janela alargada**: ele ocupa a largura da coluna, sem escurecer a
  página, até ser fechado — o painel aberto mora na camada de cima, e a folha não o devolve ao fluxo.

## R-009 — A barra retrátil (US5)

**Decisão**: o estado é `data-barra` na própria `.shell`, posto por `static/interface/shell.js`,
carregado **sem `defer`** de dentro da `.shell`, logo depois de ela abrir. Dali o script acha a
`.shell` por `document.currentScript.parentElement`, lê a escolha do `localStorage` e põe o atributo
antes de o navegador ler a barra — que, por isso, já nasce no estado certo. O controle, escondido no
HTML, é ligado no `DOMContentLoaded`.

**Revisão do PR, segunda rodada.** O controle saiu do topo, ao lado da marca, para a última linha da
barra: no topo, a faixa recolhida não comportava a sigla e o controle lado a lado, o topo crescia
ao recolher e empurrava todos os itens para baixo — e o controle saía de baixo do ponteiro de quem
recolhe e expande em seguida. Todo ícone tem o centro a 34px da borda nos dois estados, e o
separador ocupa a altura do título que substitui: ao recolher, nada anda, e só os nomes saem. O
controle perdeu `aria-expanded`: recolhida, a barra continua inteira à vista, e o anúncio de
"recolhido" desmentiria o que vem a seguir; o nome do controle já diz o que ele fará. E a tela de
toque começa expandida, porque a dica depende de ponteiro. A coluna da barra passou a ser pintada
na própria `.shell`, para que uma captura de página inteira não mostre a barra parando no primeiro
quadro.

**Por quê**: a regra do projeto é script em arquivo estático, sem script inline; no `head` o atributo
teria de ir ao `html`, e cada regra do estado recolhido precisaria excluir a Alocação por `:not()`. De
dentro da `.shell`, a Alocação simplesmente não carrega o script (`FR-1730`). A transição só existe
com `data-animar`, que o clique põe: no carregamento não há do que transitar.

**O nome é o texto, e a dica é o mesmo texto.** Cada item tem o ícone (decorativo) e um `span` com
o nome. Expandida, o `span` está à vista; recolhida, ele vira a dica ao lado do ícone, com opacidade
zero até o ponteiro ou o foco chegarem — e continua sendo o nome acessível. Sem `aria-label`, sem
segundo texto a manter.

**Alternativas**: cookie lido pelo servidor — exigiria requisição para gravar e misturaria
preferência de apresentação com a sessão; `details`/`summary` — não lembra nada; um `aria-label`
por item — duas grafias do mesmo nome.

## R-007 — Medir antes de afirmar

O teto da distribuição (`tests/performance/test_escala_da_mesa.py`, 120 000) estava em **83 781**
na `main` `31268896`, medido nesta sessão — a folga de 116 bytes registrada em 30/09 não vale mais.
A moldura custa cerca de 3 KB por página, e a distribuição é medida de novo depois dela.

A tela larga perde 15rem para a barra. As telas que hoje cabem a 1280 com pouca folga são o risco;
a comparação do inventário (`SC-662`) é o que decide, e não a estimativa.
