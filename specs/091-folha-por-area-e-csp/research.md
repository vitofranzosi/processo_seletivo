# Pesquisa — 091

As decisões de governança estão na spec (D-001 a D-010). Aqui ficam as questões de desenho e de teste,
o levantamento e as medições. Medido em 18/10/2026 na `main` `21e36bd4` (com a `089`), salvo onde se
diz outra coisa; os números da implementação entram depois do merge do PR #307.

## R-001 — O que é embutido hoje, nas três bases e no que elas carregam

O levantamento que o pedido exige antes de propor a política. Varredura de
`processo_seletivo/**/templates/**/*.html`, `**/static/**/*.js` e `**/*.py` fora dos testes.

| Espécie | Gestão (`interface/base.html` e filhas) | Página de acesso (`base_de_acesso.html` e filhas) | Portal (`portal/base.html` e filhas) | Página de erro (`shared/404.html`) |
|---|---|---|---|---|
| `<style>` no documento | o do `{% block estilo_da_pagina %}`, preenchido por 22 telas | o mesmo bloco, com `_estilo_do_acesso.html` (≈ 14 KB) | a folha própria do portal, ≈ 70 KB, 1.023 linhas do modelo | ≈ 1,5 KB |
| `style=""` | 3: o `<svg>` dos símbolos (`base.html:43`), a barra de `minhas_etapas.html:73`, as barras de `_serie_de_inscricoes.html:24` | 1: o `<svg>` dos símbolos (`base_de_acesso.html:21`) | 1: a barra de `_documentos.html:21` | 0 |
| `<script>` embutido | 0 | 0 | 0 | 0 |
| atributo `on*=` | 0 | 0 | 0 | 0 |
| `javascript:` | 0 | 0 | 0 | 0 |
| `<style>` injetado pelo htmx | nas 6 telas que carregam `htmx.min.js` (composição e Retificação) | — | em `inscricao.html` | — |
| script que escreve estilo | `prototipo-do-assistente.js` e `rascunho.js`, por `elemento.style.x =` — CSSOM, que a política não recusa | — | — | — |
| HTML gerado em Python com `style=` | 0 | 0 | 0 | 0 |

**Fora das bases**: `prototipo_do_assistente.html` é um fragmento com `<style>` próprio (≈ 6 KB, prefixo
`pd-`), acrescentado à página pública da seleção — do portal — e, no desenvolvimento, pela própria
página (`074`). A API responde JSON (`DEFAULT_RENDERER_CLASSES` só com o `JSONRenderer`), e `/`,
`/health`, `/readiness` e `/metrics` não são HTML.

**Recursos de outra origem**: nenhum. Nenhum `src`, `href` ou `action` com `http`; nenhum `url()` nas
folhas; nenhuma fonte baixada (a pilha de fontes é de sistema); os dois `fetch` dos scripts
(`prototipo-do-assistente.js`, `portal/cep.js`) vão à própria origem. Dois embutidos de documento,
ambos da própria origem: o `<object>` do PDF na prévia do Edital (`previa.html:32`, a view com
`@xframe_options_sameorigin`) e o `<iframe>` da Mesa, que o `mesa.js` aponta para o `href` do
documento.

**htmx**: a cópia em `interface/static/interface/htmx.min.js` é da série 2. Ela injeta, ao carregar, um
`<style>` com `.htmx-indicator` quando `htmx.config.includeIndicatorStyles` não é `false`; nenhuma
tela usa `htmx-indicator` nem `hx-indicator`. Ela avalia texto como código só em `hx-on`, `hx-vals`/
`hx-vars` com `js:` e filtros `[...]` de `hx-trigger`; nenhum dos três aparece nos modelos (os dois
comentários de `_marco.html` e `_perfil.html` que citam `js:` explicam justamente por que não usá-lo).

**O framework não traz a política**: o projeto está no Django 5.2.17 (`uv.lock`); o middleware de CSP
do próprio Django chega na série 6.0. Daí o middleware do projeto (D-006).

## R-002 — As áreas da folha comum

O `gestao.css` da `089` tem 1.471 linhas, ≈ 930 regras, 162 comentários e um `@media print` (linha 176,
o da `088`). Por trechos, na ordem do arquivo:

| Linhas | Conteúdo dominante | Área |
|---|---|---|
| 1–21 | comentário de topo; `*`, `body`, `a`, salto, foco, cabeçalho do topo | base |
| 22–169 | o shell da `076`: barra, itens, recolhimento, `@media` da barra | moldura |
| 170–180 | o `@media print` da `088` | impressão |
| 181–268 | estrutura de `main`, escala de títulos, medida de leitura, campos, ações em linha, a tabela da Retificação, o PDF da prévia, o quadro de vagas | base, formulários, telas — misturados |
| 269–346 | o cabeçalho do Processo, tabelas, `.tabela-rolavel`, funções da comissão, `.oculto`, paginação, lote | tabelas, componentes |
| 347–1085 | componentes (botões, ações, marcas, cartões, etapas, ajuda, resumo de erros, trilha), a Distribuição, filtros, campos, recursos, controles de formulário | componentes, formulários, telas — misturados |
| 1086–1352 | inscrições recebidas, Mesa, comissão, autoridades, Minha etapa, mesa de trabalho, coincidência de CPF, controle de arquivo, escolha que governa campos, blocos do marco | telas, formulários |
| 1353–1440 | a Retificação | telas |
| 1441–1471 | o sorteio | telas |

Cortar em fatias contíguas daria "base" e "moldura" limpos, e um "componentes" de 900 linhas com
formulário, tabela e tela dentro. A divisão por área exige mover regras — e é aí que entra a prova do
R-003. A tabela de destino de cada regra é um artefato da implementação (`areas.py`, na pasta da
prova), e a pesquisa ganha, depois dela, a lista das regras que ficaram fora da área e por quê.

**Arquivos**: `interface/static/interface/gestao/` com `base.css`, `moldura.css`, `componentes.css`,
`formularios.css`, `tabelas.css`, `telas.css` e `impressao.css`, nessa ordem de carga — da mais geral à
mais específica, e a impressão por último, como a regra de papel que corrige as outras. O `gestao.css`
sai: deixá-lo como entrada que importa os outros é o que o D-002 descarta.

**O comentário de topo** da `089` (linhas 1–8), que explica a folha inteira, vai para `base.css`, com
uma linha que registra a divisão e aponta a lista de carga (R-004).

**Na implementação** (`areas.py`, `ordem.py`, `ordem.json`): a unidade que muda de arquivo é a regra
de primeiro nível — ou o bloco `@media` inteiro —, com os comentários que a precedem. Agrupar por
"comentário e as regras que ele explica" foi tentado e descartado: o comentário explica a primeira
regra, e as seguintes sem comentário são muitas vezes de outro assunto. A área de cada regra sai das
palavras do seletor, da mais específica à mais geral (uma regra que cita uma tela é da tela); a de um
`@media`, das regras de dentro.

**A impressão carrega em terceiro, e não no fim.** O `@media print` da `088` está na linha 180, logo
depois do shell, e disputa propriedade com centenas de regras que vêm depois dele: no fim da folha,
ele passaria a vencê-las no papel. Com a impressão no fim, a prova empurrava 282 regras para o mesmo
arquivo dela. A ordem de carga é base, moldura, impressão, componentes, formulários, tabelas, telas.

**O resultado**: 562 regras — base 13, moldura 44, impressão 1, componentes 81, formulários 62,
tabelas 16, telas 345 —, 20.969 pares de regras trocam de ordem, e nenhum deles disputa. **Sete regras
ficam fora da área**, porque mudá-las de lugar inverteria um par que disputa:

| Linha (antes) | Regra | Área do seletor | Arquivo |
|---|---|---|---|
| 203 | `main>p,main>section>p,.sub,.ajuda,.vazio,legend+p` (medida de leitura) | formulários | componentes |
| 344 | `.paginacao [aria-current]` | tabelas | componentes |
| 443 | `.remover-linha .ajuda` | componentes | telas |
| 545 | `.erro a` | formulários | tabelas |
| 812 | `.alocar-em-lote fieldset,.remover-em-lote fieldset` | telas | formulários |
| 1319 | `fieldset.opcoes>.ajuda` | formulários | telas |
| 1420 | `[hidden]` | base | telas — precisa vencer o `display` de toda regra anterior |

**A área "telas" é a maior** (345 regras, 60 KB): a folha comum ainda guarda muito estilo que cita
uma tela só — a Distribuição, a Mesa, a Retificação, o sorteio. Ficou na folha comum porque estava
lá; levá-lo para os arquivos de tela é o mesmo movimento da parte B, regra a regra, com a mesma prova
— um passo possível, e não desta feature.

## R-003 — A prova de que a ordem não importa

A cascata decide entre duas declarações da mesma propriedade, no mesmo elemento, pela origem, pela
importância, pela especificidade e, empatadas as três, pela ordem. Todas as regras da folha comum são
da mesma origem e nenhuma usa `!important` (conferir na implementação). Trocar a ordem de duas regras
só muda o resultado se elas declaram uma mesma propriedade — já expandidos os atalhos: `margin` é
`margin-top` e mais três — **e** alcançam um mesmo elemento **e** têm a mesma especificidade. A prova
(`ordem.py`, novo, na pasta da prova) é conservadora: dispensa a especificidade, e verifica as duas
primeiras condições.

1. **Pares que trocam de ordem.** Da posição de cada regra antes (no `gestao.css` e no estilo da tela)
   e depois (no arquivo da área, na ordem de carga), os pares cuja ordem relativa se inverte.
2. **Propriedades**, sem página nenhuma: o Chrome carrega as folhas de antes e expande cada regra pelo
   CSSOM (`rule.style` enumera as propriedades longas). Par sem propriedade comum: livre.
3. **Elementos**, nas páginas do inventário: para os pares que sobram, cada página do inventário, nos
   dois estados da barra e nas duas larguras, responde se algum elemento casa com os dois seletores
   (`element.matches`, com as pseudoclasses de estado — `:hover`, `:focus`, `:focus-visible`,
   `:active`, `:checked` — removidas, o que só alarga o casamento; pseudoelementos comparados só com o
   mesmo pseudoelemento). Par que se alcança em alguma página: a regra volta para o lugar.
4. **Mídia**: a condição de mídia não entra na conta — duas regras em `@media` diferentes ainda podem
   valer juntas —, de novo do lado conservador.

O que a prova não vê: elemento que só existe fora do inventário — criado por script (o filtro da
Retificação, a caixa de rascunho) ou num fragmento que o inventário não captura. Por isso a parte 3 só
libera par cujos seletores citam alguma classe ou elemento que aparece no inventário; o par cujo
seletor só casa com o que o inventário não tem fica na ordem de antes (suposição da spec).

A mesma prova serve à remoção de duplicadas (R-005): tirar a cópia de baixo é mover a de cima para o
lugar dela, e cada regra entre as duas é um par que troca de ordem.

**Na implementação, duas fontes de evidência a mais**, porque a primeira medida tratava como "casa
com tudo" 87 seletores sem elemento no inventário — a série da supervisão, o lote da Distribuição, a
paginação — e prendia `.campo`, `.ajuda` e `.salvar` depois deles:

1. **O sujeito.** Um seletor sem elemento no inventário é medido também pelo último composto dele
   (`.serie .barra` → `.barra`), mais largo. Se o sujeito casa, o inventário diz com quem ele divide
   elemento.
2. **As classes que os modelos escrevem** (`coocorrencia.py`). Para dois sujeitos alcançarem o mesmo
   elemento, algum elemento de algum modelo da gestão tem de ter as classes dos dois. A leitura abre os
   `{% if %}` do atributo (junta classes), trata `s-{{ x }}` como prefixo, dá às três classes
   inteiramente variáveis (`peso`, `acao.estilo`, `linha.classe`) os valores que o Python lhes dá, e
   conta as classes que os scripts criam (`className`, `classList`) e as que o Python monta. Classe que
   nenhum modelo, script ou módulo da gestão escreve não está em elemento nenhum dela: é regra morta.

Com as duas, os pares de regras em conflito caíram de 4.334 para 281, os "sem saber" — seletor e
sujeito sem elemento, e classes que podem coincidir — para 44, e as regras fora da área, de 105 para 7.
A solução que distribui as regras também mudou: empurrar sempre a regra de baixo para o arquivo da de
cima cumpria a restrição, mas levava componentes inteiros para "telas"; a final minimiza a soma das
distâncias entre a área desejada e o arquivo, sob as mesmas restrições (regressão isotônica, um corte
mínimo por limiar).

**E a prova final é a mesma da `089`**: o resumo das regras aplicadas por página (`estilos.py`),
agora comparado como **conjunto**, e não como sequência — a sequência muda por construção —, mais
medidas e pixels contra o ruído. Uma troca que a prova de ordem deixasse passar e mudasse algo
apareceria como pixel.

## R-004 — Como as bases carregam a folha

**Decisão**: D-002. Uma lista só, `FOLHAS_DA_GESTAO` em `shared/estaticos.py`, na ordem de carga; a
verificação de sistema `estaticos.E001` passa a conferir a lista, os tokens, e cada arquivo de tela
(R-006); e uma tag de inclusão, `{% folhas_da_gestao %}`, escreve um `<link>` por arquivo, cada um
pela `estatico` da `089`. Só o `base.html` a usa: a `base_de_acesso.html` não carrega a folha comum
hoje — só os tokens e o `_estilo_do_acesso` —, e continua assim, com o parcial virando `<link>` (R-006).

**Custo do `@import`, que o D-002 descarta**: o navegador acha os `@import` só depois de baixar o
arquivo que os contém — com a primeira visita sem cache, uma ida e volta a mais antes do primeiro
desenho; os `<link>` do `<head>` são descobertos pelo leitor antecipado do navegador e baixados em
paralelo. E o endereço dentro de um `.css` não passa pela tag: os importados viriam sem `?v=`, e o
nginx do guia, que só dá `immutable` a quem tem `?v=`, os revalidaria a cada página — ou, sem
revalidar, serviria folha velha.

**Custo dos `<link>`**: sete em vez de um, ≈ 80 bytes cada, em toda resposta HTML da gestão (SC-817);
na primeira visita, sete pedidos em paralelo (o guia serve por HTTP/2); depois, nenhum, pelo
`immutable`.

## R-005 — Duplicadas

"Duplicada" é o D-003: seletor, declarações e mídia iguais, depois de normalizar espaço e a ordem dos
seletores numa lista. A varredura (`equivalencia.py`, na pasta da prova) roda sobre a folha comum mais
os estilos de tela, e a lista vai para esta seção na implementação, com a prova de ordem de cada
remoção.

**Medido** (`equivalencia.py` na pasta da prova, sobre o que cada página carrega — a folha comum e os
arquivos de tela e de grupo):

- **Dentro da folha comum, nenhuma** regra idêntica a outra.
- **Entre as duas telas do assistente, seis**: `.versao`, `.tipo`, `.natureza`, `.literal`, `.origem`
  e `.referencia`. Foram para `grupos/assistente.css`, carregado pelas duas antes da folha própria de
  cada uma. Elas sobem acima de regras próprias que as precediam (`.piloto`, `.turno`, `.trecho`;
  `.perguntas`, `.resposta`, `.explicacao`); nenhum elemento dos modelos tem uma classe comum e uma
  própria juntas (`coocorrencia.py`), e a ordem não muda o vencedor de nada. As regras quase iguais —
  `.turno` × `.resposta`, `.turno h2:focus` × `.resposta h2:focus` — têm seletores diferentes e ficam
  em cada tela.
- **Entre a folha comum e a da página de acesso, seis** (`*`, `a`, `.pular:focus`, `main:focus`,
  `.oculto`, `.simbolos`). As duas nunca carregam na mesma página (D-003): não são duplicadas na
  cascata, e ficam.

## R-006 — O estilo das telas

**Medido**: 27 modelos preenchem o `{% block estilo_da_pagina %}` (fora o `base.html`, que o define, e
contando o `base_de_acesso.html`, que o define preenchido); o fragmento do protótipo tem um `<style>`
próprio com um bloco de mesmo nome.

| Modelo | Bytes do bloco | Sem comentários | Parcial incluído |
|---|---|---|---|
| `visao_geral.html` | 12.000 | 11.997 | — |
| `prototipo_do_assistente.html` | 6.112 | 6.110 | — (fragmento) |
| `retificar.html` | 1.872 | 1.870 | — |
| `duvidas.html` | 1.237 | 1.020 | — |
| `assistente.html` | 1.173 | 977 | — |
| `inscricao_detalhe.html` | 1.065 | 527 | `_estilo_da_lista_exigida` |
| `alocacoes.html` | 851 | 353 | — |
| `compor_conteudo.html` | 518 | 516 | — |
| `lista.html` | 380 | 139 | — |
| `sorteio.html` | 304 | 38 | — |
| `marco.html` | 243 | 104 | — |
| `compor_revisao.html` | 118 | 116 | — |
| `mesa_inscricao.html` | 55 | 55 | `_estilo_da_lista_exigida` |
| `detalhe.html`, `processo_detalhe.html`, `retificacao_detalhe.html` | 52 | 52 | `_estilo_das_terminais` |
| `compor_classificacao.html`, `compor_perfis.html` | 48 | 47 | `_estilo_da_vista` (e regras próprias) |
| `base_de_acesso.html`, `identificar.html`, `identificar_demonstracao.html`, `sem_autenticacao.html` | 48 | 48 | `_estilo_do_acesso` |
| `aviso.html`, `aviso_previa.html`, `modelo_de_aviso.html` | 47 | 47 | `_estilo_do_aviso` |
| `compor_anexos.html` | 36 | 36 | — |
| `comissao.html` | 34 | 34 | — |
| `compor_cronograma.html` | 28 | 28 | — |

Os cinco parciais: `_estilo_do_acesso` (13.978 bytes), `_estilo_das_terminais` (1.780), `_estilo_da_vista`
(1.715), `_estilo_da_lista_exigida` (849), `_estilo_do_aviso` (549).

**Destino**: `interface/static/interface/grupos/` — um arquivo por parcial, com o nome do grupo
(`acesso.css`, `terminais.css`, `vista.css`, `lista-exigida.css`, `aviso.css`), mais `serie.css` e
`assistente.css`, da 091 —, e `interface/static/interface/telas/`, um por tela com regras próprias, com
o nome da tela (`visao-geral.css`, `retificar.css`, …): 16, contando o do fragmento do protótipo e o de
Minhas Etapas. Dois diretórios, e não um, para o nome do grupo não colidir com o de uma tela. A
conversão é do `converter_telas.py`, na pasta da prova. O bloco continua com o
nome `estilo_da_pagina`, agora fora do `<style>` e no `<head>`, com `<link>`s pela `estatico`; o
`<style>` vazio sai da base. O comentário da `040` sobre o ponto de extensão fica no modelo, com a nota
da mudança. Os `{% comment %}` de dentro dos blocos viram `/* */` no arquivo (D-002 da `089`); os que
ficam fora do bloco, explicando o modelo, ficam no modelo.

**O fragmento do protótipo** carrega a folha dele por um `<link>` no próprio fragmento — permitido no
corpo do documento para folhas —, pela `estatico`. Quem o acrescenta à página pública não muda.

**A página de erro**: o `<style>` do `404.html` vai para `shared/static/shared/erro.css`, ao lado dos
tokens, e entra na verificação de sistema.

**A verificação de sistema** passa a conferir, além da lista da folha comum, todo caminho citado por
`{% estatico '…' %}` nos modelos — varrendo o texto dos modelos, como os guardiões já fazem —, e não só
os que estão na lista. Um `<link>` de tela para arquivo ausente vira erro de `check`, e não 500 numa
tela só.

## R-007 — Os atributos `style`

| Onde | O que | Destino |
|---|---|---|
| `base.html:43`, `base_de_acesso.html:21` | `style="position:absolute"` no `<svg>` dos símbolos, com `width="0" height="0"` | uma classe com a regra, na `base.css` (gestão) e na `acesso.css` (acesso) |
| `minhas_etapas.html:73` | `style="width:{{ item.carga.percentual }}%"` — inteiro de 0 a 100, de `avaliacoes/application/selectors.py:480` (`round`) | classe `largura-N` |
| `_serie_de_inscricoes.html:24` | `style="height:{% widthratio … 100 %}%"` — inteiro de 0 a 100 | classe `altura-N` |
| `portal/_documentos.html:21` | `style="width:{% widthratio … 100 %}%"` | fica (D-007): listada para o passo do portal |

**As classes por valor** são 101 regras de largura e 101 de altura. Cada uma termina em `%;}`, e não em
`%}`: a memória "Varredura lê o comentário" e o comentário da linha 652 do `gestao.css` registram que
`%}` numa folha reprova o guardião de sintaxe de modelo vazada (`test_estaticos.py`). Um guardião novo
confere que o valor do modelo é sempre inteiro de 0 a 100 — o `round` e o `widthratio` garantem hoje —,
e que as 101 de cada existem. **O valor aplicado é o mesmo**: `width:37%` pelo atributo e pela classe.

**A mesma armadilha numa folha de tela.** A visão geral tinha sete regras terminadas em `%}` —
`width:26%}` e `max-width:100%}` —, que dentro do modelo passavam porque nenhum guardião varria aquele
bloco. Fora dele, o guardião de sintaxe vazada as acusou; ganharam `;` antes da chave, com um
comentário, e o `test_larguras` que conta as larguras da tabela passou a aceitar o `;`.

**O que o portal tem, para o passo dele (FR-2102)**: a folha de `portal/base.html` (≈ 70 KB, 5
`{% comment %}`), o `style=""` de `_documentos.html:21`, e o `<style>` do fragmento do protótipo
quando acrescentado à página pública — este sai já nesta feature (R-006).

## R-008 — A política

**O cabeçalho**, uma constante em `shared/politica_de_conteudo.py`:

```text
default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self';
connect-src 'self'; object-src 'self'; frame-src 'self'; base-uri 'self'; form-action 'self'
```

- `style-src 'self'` e `script-src 'self'`, sem `'unsafe-inline'` nem `'unsafe-eval'`: o pedido.
- `object-src 'self'` e `frame-src 'self'`: o PDF da prévia e o documento da Mesa (R-001). O padrão
  recomendado é `object-src 'none'`; aqui o objeto é o próprio visualizador da prévia.
- `base-uri 'self'` e `form-action 'self'`: as duas diretivas que não herdam de `default-src`; sem
  elas, uma marcação injetada poderia trocar a base dos endereços ou mandar um formulário para fora.
- **Sem `frame-ancestors`**: quem impede outra origem de emoldurar a gestão é o `X-Frame-Options`
  (`DENY` em produção), com a exceção `SAMEORIGIN` da prévia por view. Repetir a regra na política
  exigiria espelhar a exceção, e `frame-ancestors` vence o `X-Frame-Options` nos navegadores atuais —
  um erro ali derrubaria a prévia ou abriria a gestão. Fica registrado como passo possível.
- **Sem `report-uri`/`report-to`**: não há endereço que receba relatório; as violações do modo de
  observação vão para o console (suposição da spec).

**Quem recebe o quê** (middleware `PoliticaDeConteudoMiddleware`, o primeiro da lista, para que a
resposta de todo middleware de dentro — a recusa de envio grande, a recusa do domínio — passe por ele):

| Resposta | Cabeçalho |
|---|---|
| HTML com caminho sob `/gestao/` — telas, fragmentos do htmx, página de acesso, recusas, página de erro do sistema | `Content-Security-Policy` |
| outro HTML — portal, página pública da seleção, página de erro fora da gestão | `Content-Security-Policy-Report-Only` |
| não HTML — JSON, PDF, arquivo, estático, `/health` | nenhum |
| a página de depuração do Django, com `DEBUG` ligado | nenhum (D-010) |
| resposta que já traz uma política | não é tocada |

"HTML" é `Content-Type` começando por `text/html`. **A página de depuração é reconhecida pela marca, e
não pelo status**: os modelos de depuração do Django (`technical_404.html`, `technical_500.html`) trazem
`<meta name="robots" content="NONE,NOARCHIVE">` no `<head>`, e os do sistema, não. O plano era o
status — 404 ou 500 com `DEBUG` —, e o inventário de impressão mostrou por que não: a gestão serve as
próprias recusas com 404 ("Recurso não encontrado"), na moldura dela, e com `DEBUG` elas ficariam sem
política no servidor local.

**No runserver e em produção** (FR-2108): o cabeçalho sai da aplicação nos dois; o `staticfiles` do
runserver e o nginx de produção servem as folhas e os scripts da própria origem, e os dois casam com
`'self'`. O guia ganha, no bloco de cabeçalhos, a nota de que o nginx não acrescenta política — duas
políticas se somam e a mais restrita vence em silêncio — e, na lista de verificação, um `curl -I` de
uma tela da gestão com o cabeçalho.

## R-009 — O htmx sob a política

Um `<meta name="htmx-config" content='{"includeIndicatorStyles":false,"allowEval":false}'>` no
`<head>` das bases que carregam telas com htmx — a da gestão e a do portal. O htmx 2 lê essa
configuração ao iniciar; o `<meta>` não é script, e a política não o recusa. Sem estilo de indicador
não há regra a perder: nenhuma tela usa o indicador. Sem avaliação, os três usos que avaliariam
continuam proibidos, agora também pela biblioteca. Um guardião confere o `<meta>` em toda base que leva
a uma tela com `htmx.min.js`.

## R-010 — Os guardiões

Os que leem a folha comum já leem por `tests/interface/folha.py` (`FOLHA_COMUM`, `TOKENS`,
`folha_aplicada`). Com a divisão, `FOLHA_COMUM` passa a ser a concatenação dos arquivos da lista, na
ordem de carga, e `folha_aplicada` já lê qualquer `<link>` do `<head>` — os de tela inclusive. O risco
da `089` se repete onde um guardião lê o **texto do modelo** de uma tela ou de um parcial para achar
regra: depois da mudança, o modelo não tem regra, e a afirmação negativa passa vazia.

**Candidatos** (varredura de `tests/` por `_estilo_`, `estilo_da_pagina`, `<style`, `gestao.css`,
`FOLHA_COMUM`, `folha_aplicada`, e por asserção com cara de CSS em teste que lê um dos 29 modelos que
tinham estilo): 31 arquivos. **Na implementação**, a suíte apontou 12 falhas, todas de guardião que lia
estilo no texto do modelo; a varredura das asserções achou os demais. Como cada um passou a ler:

| Guardião (`tests/interface/…`) | Lia | Passa a ler | Silencioso sem repontar? |
|---|---|---|---|
| `folha.py` (`FOLHA_COMUM`) | `gestao.css` | os sete arquivos, somados na ordem de carga | sim — todos os 23 da `089` |
| `folha.py` (`estilo_do_bloco`, novo) | — | os arquivos que o bloco `estilo_da_pagina` de um modelo carrega | — |
| `test_acessibilidade.py` (`_estilo_proprio`) | o bloco, com o `include` resolvido | `estilo_do_bloco` | sim: as classes de tela seriam acusadas de órfãs, ou nenhuma lida |
| `test_polish_da_055.py` (Comissão) | o texto exato do bloco | o arquivo da tela | quebrava |
| `test_polish_da_056.py` (conteúdo, cronograma, revisão, anexos) | o texto do modelo | o arquivo da tela | quebrava |
| `test_polish_da_057.py` (condução) e `058` (pelo `da_pagina`) | o texto do modelo | o arquivo da tela | quebrava / sim |
| `test_telas_de_uso_diario.py` (sorteio) | o bloco | o arquivo da tela | quebrava; a negação sobre a comum, sim |
| `test_completude_das_etapas.py` | `width:40%` no corpo | `largura-40` no corpo | quebrava |
| `test_medida_dos_campos.py` | o corpo menos o `<style>` | o corpo menos qualquer `<style>` (não há) | quebrava (`index`) |
| `test_telas_de_quem_elabora.py` (molduras que rolam) | modelos + `gestao.css` | modelos + os sete + os de tela e grupo | **sim**: o estilo das telas saiu dos modelos |
| `test_estaticos.py` (sintaxe vazada) | `gestao.css`, tokens | todas as folhas estáticas | sim |
| `test_larguras.py` (larguras da visão geral) | `%}` na regra | aceita `%;}` | quebrava |
| `test_folha_estatica.py` (089) | a ordem tokens → `gestao.css` → `<style>` | tokens → sete → arquivo da tela | quebrava |

**Guardiões novos** (`test_politica_de_conteudo.py`, e em `test_folha_estatica.py`):

- nenhum `<style>`, `style=`, `<script>` sem `src`, `on*=` ou `javascript:` nos modelos (FR-2097,
  FR-2101, FR-2106), e nenhum `setAttribute("style"` nem `style=` em marcação montada pelos scripts;
- cada arquivo de `telas/` é citado só pelos modelos que o usam, e toda tela que tinha bloco carrega o
  arquivo correspondente (SC-815);
- o cabeçalho nos dois modos, a ausência fora do HTML e na depuração (FR-2112);
- os arquivos novos varridos pelo guardião de sintaxe de modelo da `089` (FR-2111).

**A mutação** (`mutacoes.py`, saída em `mutacoes.txt`): as 28 da `089`, repontadas para o arquivo de
área onde a regra mora agora, mais 29 dos guardiões repontados e novos — o estilo das telas, a carga
por tela, as classes por valor, os modelos, os scripts, o `<meta>` do htmx, a política, a página de
depuração e o protótipo. **Todas reprovam**; sem mutação, os mesmos testes passam. Uma, na primeira
rodada, não reprovou — e era a mutação que estava errada: renomear `.filtros-da-visao{` não tira a
classe da folha, que tem outras regras dela; a refeita, numa classe que só uma regra define, reprova.

## R-011 — A prova no navegador

**Resultado** (18/10/2026, `depois-da-091/`; antes de `69c6ac1c` + spec, depois de `002359f8`, os dois
por `git archive`, banco `ps_inventario_091`, cópia do `ps_inventario_090`):

- **Medidas**: nos dois estados da barra, 85 de 86 variantes capturadas (a `aviso-da-chamada` segue
  sem captura, como desde o inventário de 16/10), **nenhum** `status` diferente, **zero** estouros a
  375 e a 1280, nenhuma largura, altura, título ou `h1` diferente.
- **Regras aplicadas, como conjunto**: iguais em 79 telas. Nas seis telas com htmx — composição e
  Retificação —, três a menos, que são as do indicador que o htmx deixou de injetar (D-009): o resumo
  delas depois é o mesmo de uma tela sem htmx. Nas da barra, uma a mais declarada à parte, `.simbolos`;
  na supervisão e em Minhas Etapas, as classes de percentual.
- **Pixels** (`pixels.py`, com um par de ruído de cada lado): 160 e 155 variantes idênticas, 2 e 7
  dentro do ruído, e 8 em cada estado acima dele — visão geral, supervisão, detalhe do Processo e
  dúvidas, a 1280 e a 375. **As oito são a hora na tela** ("14h20" antes, "14h51" depois, recortes
  conferidos): o par de ruído é da mesma passada, e não a pega. As bases (vitrine, entrada do portal,
  as duas páginas de erro): idênticas.
- **Impressão** (`imprimir.py` da `088`): `impressao.json` igual, os PNG do papel idênticos, o texto
  dos PDF igual.
- **Violações da política**: **zero** em todas as variantes da gestão e da página de acesso, nos dois
  estados. Na vitrine e na entrada do portal, uma em observação cada — o `<style>` da folha do portal,
  a prevista. No protótipo do painel (a página do portal sob a gestão), uma em observação, a mesma.
  **Na primeira passada**, o protótipo acusou uma violação em **recusa**: a view sob `/gestao/` serve a
  página do portal, com a folha dele no documento. Corrigido com `em_observacao` (FR-2104), e a passada
  final já não a tem.

O inventário da `089` (`capturar.py` com `ESTILOS=1`, `capturar_bases.py`, `comparar.py`, `medidas.py`,
`pixels.py`, `imprimir.py` da `088`) é refeito antes e depois, numa pasta `depois-da-091/`, com vários
pares de ruído. Duas mudanças nas ferramentas:

- `estilos.py` compara as regras aplicadas como conjunto (R-003);
- o `capturar.py` lê, de cada variante, as mensagens de violação da política — o evento
  `securitypolicyviolation` do documento, registrado antes de a página carregar, e o console — e as
  grava no `resultados.json`; o `comparar.py` acusa qualquer uma na gestão e na página de acesso, e
  compara com a lista prevista no portal.

## R-012 — O peso

**Medido em 18/10/2026**, pelo `pesar.py` da `089` (estendido com a visão geral e a contagem de
`style=`), no banco `ps_inventario_091`; antes, um `git archive` da branch com a `main` em `69c6ac1c`;
depois, o da branch em `002359f8`:

| Página | Antes | Depois | Diferença | `style=` |
|---|---|---|---|---|
| Distribuição | 18.358 | 18.931 | +573 | 1 → 0 |
| Lista de Processos | 10.995 | 11.505 | +510 | 1 → 0 |
| Minhas Etapas | 7.264 | 7.903 | +639 | 4 → 0 |
| Visão geral | 30.663 | 19.108 | −11.555 | 1 → 0 |

O ganho das três primeiras são os seis `<link>` a mais da folha comum, cada um com a versão (≈ 85
bytes), e, em Minhas Etapas, o `<link>` da folha da tela. O teto de 120.000 da Distribuição segue com
folga. A folha comum tem 108.984 bytes nos sete arquivos (o `gestao.css` tinha 106.964; a diferença
são os cabeçalhos de cada arquivo e o comentário dos símbolos); as de tela e de grupo, 51.179 —
das quais ≈ 5 KB são as 202 classes de percentual.

## R-013 — Entrega

Um PR, se couber. A ordem de trabalho é A, B, C e D, e D depende de B e C (a política recusaria o que
eles tiram). Se D crescer — a prova de console achar o que este levantamento não achou —, A–C sai num
PR e D num segundo, da mesma spec, aberto a partir do primeiro.

**Coube**: o levantamento do R-001 não errou — nenhum script embutido, nenhum atributo de evento —, e D
é um middleware, um `<meta>` e os testes. Um PR, com B e C, A e D em commits separados.

## Achados

- **Duas regras mortas na folha comum.** `.trilha` (e `.trilha a`) é classe do portal, que tem folha
  própria; `.organizacao-etapas` não aparece em modelo, script ou módulo nenhum. Ficaram — tirar regra
  sem uso não é duplicada, e é decisão do usuário.
- **A área "telas" da folha comum tem 345 regras (60 KB)** que citam uma tela só. Levá-las para os
  arquivos de tela é o mesmo movimento da parte B, com a mesma prova; reduziria a folha comum à metade.
- **Sete regras terminadas em `%}` numa folha de tela** (a visão geral), que o guardião de sintaxe
  vazada só passou a ver fora do modelo (R-007).
- **A primeira prova de ordem era conservadora a ponto de não dividir nada**: tratar seletor sem
  elemento no inventário como "casa com tudo" prendia 105 regras fora da área. O inventário não tem a
  série, o lote, a paginação; a leitura das classes dos modelos tem (R-003).
- **A gestão serve página do portal** no protótipo do painel: a política por caminho não basta, e a
  view declara a da página que serve.
- **Os números da suíte** (`make test-pg`, 4 workers, `ps_091`): 12.178 passando, 11 pulados.
