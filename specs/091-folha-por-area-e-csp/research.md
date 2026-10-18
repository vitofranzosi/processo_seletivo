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
seletores numa lista. A varredura (`duplicadas.py`, na pasta da prova) roda sobre a folha comum mais
os estilos de tela, e a lista vai para esta seção na implementação, com a prova de ordem de cada
remoção.

**As duas telas do assistente** (`assistente.html`, 977 bytes de regras, e `duvidas.html`, 1.020):
o pedido as aponta como quase iguais. As regras iguais vão para `telas/assistente-e-duvidas.css`
(nome provisório), carregado pelas duas; as que diferem ficam em `telas/assistente.css` e
`telas/duvidas.css`, depois do comum — a ordem relativa entre uma regra comum e uma própria passa
pela prova do R-003.

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

**Destino**: `interface/static/interface/telas/` — um arquivo por parcial, com o nome do grupo
(`acesso.css`, `terminais.css`, `vista.css`, `lista-exigida.css`, `aviso.css`), e um por tela com
regras próprias, com o nome da tela (`visao-geral.css`, `retificar.css`, …). O bloco continua com o
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
| HTML de status 404 ou 500 com `DEBUG` ligado (as páginas de depuração do Django) | nenhum (D-010) |
| resposta que já traz uma política | não é tocada |

"HTML" é `Content-Type` começando por `text/html`. Com `DEBUG` ligado, todo `Http404` e toda exceção
viram a página de depuração do framework, e por isso o status basta para reconhecê-la; um modelo do
próprio sistema servido com 404 sob `DEBUG` também fica sem política — só no servidor local, e o mesmo
modelo é testado com ela na suíte, que roda sem `DEBUG`.

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
`FOLHA_COMUM`, `folha_aplicada`): 31 arquivos. A classificação um a um — o que lê, se fica silencioso
sem repontar, a mutação — é a primeira tarefa da implementação, no formato do R-005 da `089`, com
`mutacoes.py` novo na pasta da prova. Guardiões novos:

- nenhum `<style>`, `style=`, `<script>` sem `src`, `on*=` ou `javascript:` nos modelos (FR-2097,
  FR-2101, FR-2106), e nenhum `setAttribute("style"` nem `style=` em marcação montada pelos scripts;
- cada arquivo de `telas/` é citado só pelos modelos que o usam, e toda tela que tinha bloco carrega o
  arquivo correspondente (SC-815);
- o cabeçalho nos dois modos, a ausência fora do HTML e na depuração (FR-2112);
- os arquivos novos varridos pelo guardião de sintaxe de modelo da `089` (FR-2111).

## R-011 — A prova no navegador

O inventário da `089` (`capturar.py` com `ESTILOS=1`, `capturar_bases.py`, `comparar.py`, `medidas.py`,
`pixels.py`, `imprimir.py` da `088`) é refeito antes e depois, numa pasta `depois-da-091/`, com vários
pares de ruído. Duas mudanças nas ferramentas:

- `estilos.py` compara as regras aplicadas como conjunto (R-003);
- o `capturar.py` lê, de cada variante, as mensagens de violação da política — o evento
  `securitypolicyviolation` do documento, registrado antes de a página carregar, e o console — e as
  grava no `resultados.json`; o `comparar.py` acusa qualquer uma na gestão e na página de acesso, e
  compara com a lista prevista no portal.

## R-012 — O peso

A medir na implementação, antes e depois, no mesmo banco, pelo `pesar.py` da `089`: Distribuição,
lista, Minhas Etapas e visão geral; o `len(corpo)` do guardião de escala; e o tamanho de cada arquivo
novo. Esperado: a visão geral perde ≈ 12 KB; as outras três ganham os `<link>` (SC-817).

## R-013 — Entrega

Um PR, se couber. A ordem de trabalho é A, B, C e D, e D depende de B e C (a política recusaria o que
eles tiram). Se D crescer — a prova de console achar o que este levantamento não achou —, A–C sai num
PR e D num segundo, da mesma spec, aberto a partir do primeiro.
