# Pesquisa — 092

Caminhos de código relativos a `backend/processo_seletivo/`; de teste, a `backend/tests/`; "a pasta da
prova" é `doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/`. O commit de antes é o da branch do
PR #308 em `2615b738`, por `git archive`; o banco do inventário é `ps_inventario_092`, cópia do
`ps_inventario_091` com os três rascunhos do R-006, copiado de novo para cada passada.

## R-001 — O que o portal tinha de embutido

Medido em `2615b738`, pela varredura dos modelos e pelo inventário (o R-007 da `091` listava o
mesmo):

| Onde | O que | Destino |
|---|---|---|
| `portal/base.html:13–969` | o `<style>` da folha do portal: 65.839 bytes, 954 linhas, 445 regras e blocos, **124 comentários de CSS** e **nenhum** `{% comment %}` dentro dele | `portal/static/portal/portal.css` (D-001) |
| `portal/_documentos.html:21` | `style="width:{% widthratio recebidos total 100 %}%"` na barra de documentos | `.largura-N` (D-004, R-003) |
| `interface/prototipo_do_assistente.py` | a resposta marcada `em_observacao`, porque a página do portal tinha a folha embutida | sai (D-003) |

Os cinco `{% comment %}` que o R-007 da `091` contava no `base.html` estão na marcação, fora do
`<style>` — explicam a identidade do candidato, a porta de entrada e a porta da gestão —, e ficam no
modelo. A folha já estava escrita com `/* */`: foi para o arquivo como estava.

Nenhum script embutido, atributo de evento ou endereço `javascript:` em modelo nenhum do portal (o
guardião da `091` já varria todos). Nenhum script do portal escreve o atributo `style`.

## R-002 — A folha em arquivo, e as sete grafias

A folha vai ao arquivo na ordem do documento, com um comentário de cabeçalho. Sete linhas mudam de
grafia, porque o guardião de sintaxe de modelo vazada (`test_estaticos.py`) acusaria `%}` e `}}` num
arquivo estático — dentro do modelo elas passavam, porque o guardião varre a página renderizada, onde a
folha ia como texto (a mesma armadilha do R-007 da `091`):

| Linha (no `<style>`) | Antes | Depois |
|---|---|---|
| 107 | `max-width:100%}` | `max-width:100%;}` |
| 208 | `.vagas-numero .reserva{flex-basis:100%}` | `…100%;}` |
| 212 | `…line-height:1.3;flex-basis:100%}` | `…100%;}` |
| 213 | `.vagas-numero.reserva-primeiro>span{flex-basis:100%}` | `…100%;}` |
| 397 | `.rotulo-arquivo{…width:100%}` | `…100%;}` |
| 715 | `@media (min-width:520px){.protocolo{…align-items:end}}` | a chave do `@media` na linha seguinte |
| 812 | `.lateral-vaga .principal{width:100%}` | `…100%;}` |

**A prova de que nada mais mudou** é o `equivalencia.py` da pasta da prova: lê o `<style>` do commit de
antes e o arquivo de agora, desfaz no arquivo o cabeçalho, o bloco das classes de percentual e as sete
grafias — cada uma tem de casar exatamente uma vez —, e exige o resto **igual, byte a byte**:

```text
EQUIVALENTE: o <style> de 2615b738 (65839 bytes, 445 chaves de abertura, 124 comentários) é o arquivo
menos o cabeçalho, as 101 classes e 7 grafias
```

E o navegador lê o mesmo: as regras aplicadas, como conjunto (`estilos.py`), são as mesmas em todas as
103 telas do inventário — 440 regras, `81431f1f` na vitrine, antes e depois —, fora as 101 classes de
percentual, que o conjunto declara à parte. A contagem de folhas da vitrine passa de
`link 1, style 395` a `link 1, link 496`: 395 regras do `<style>` mais as 101.

## R-003 — A barra de documentos

`_documentos()` (`portal/views.py`) conta `recebidos` entre os obrigatórios e `total` como o número de
obrigatórios: `recebidos ≤ total`. O `widthratio` arredonda para inteiro, e com `total` zero devolve
`0`. O valor é, portanto, sempre um inteiro de 0 a 100, e `.largura-0` a `.largura-100` cobrem todos.
As classes estão no arquivo do portal, logo depois das regras da barra, terminadas em `%;}` pela razão
do R-002. O nome é o de Minhas Etapas, na gestão (decisão 005 da `091`); as regras não são as mesmas
porque o portal não carrega folha da gestão.

Especificidade: `.progresso-documentos .feito` não declara largura, e nenhuma outra regra do portal
alcança `.feito` com `width`. O atributo valia por ser atributo; a classe vale por ser a única. A
transição de largura da barra não dispara em nenhum dos dois casos: a página e o fragmento do htmx
entregam o elemento novo, já com a medida.

Testado em `test_politica_de_conteudo.py` — 0 de 2, 1 de 2, 2 de 2, 1 de 3 e 0 de 0 dão `largura-0`,
`-50`, `-100`, `-33` e `-0` —, e pelo inventário: os três rascunhos preparados mostram a barra em 0,
50 e 100%, com pixels idênticos antes e depois.

## R-004 — Os guardiões

Varredura de `tests/` por `portal/base.html`, `templates/portal`, `<style`, `</style>`,
`folha_aplicada`, `folha_da_pagina`, e por asserção com cara de CSS em teste que pede tela do portal: 28
arquivos candidatos. O risco é o da `089` e da `091` — afirmação negativa que passa sem ler regra —, e
mais um, que só o portal tinha: **afirmação positiva sobre o corpo da página que casava com a folha
embutida**. Com a folha fora do documento, a suíte apontou 6 falhas — 4 nos arquivos que a varredura já
listava, 2 em `test_detalhe_selecao.py`, que ela não tinha pegado —; a varredura achou as silenciosas.

| Guardião | Lia | Passa a ler | Silencioso sem repontar? |
|---|---|---|---|
| `interface/folha.py` | — | `PORTAL_CSS` e `FOLHA_DO_PORTAL` (o arquivo, com os comentários) | — |
| `interface/test_acessibilidade.py` (`CANAIS`, modificador sem base e classe órfã) | o texto do `base.html` | o arquivo e a base | **sim**: toda classe do portal seria acusada de órfã — alto —, mas o modificador sem base passaria vazio |
| `interface/test_acessibilidade_do_portal.py` (largura em pixel) | o texto do `base.html` | o arquivo e a base | **sim**: `regras == []` sobre a marcação |
| `interface/test_acessibilidade_do_portal.py` (vaga indicada) | o texto do `base.html` | o arquivo | quebrava |
| `interface/test_polish_da_055.py` (`FOLHA_DO_PORTAL`) | o texto do `base.html` | o arquivo | quebrava |
| `interface/test_polish_da_057.py` (envio numa linha) | o texto do `base.html` | o arquivo e a base | **sim**: `".envio .linha{" not in` |
| `integration/portal/test_revisao_e_comprovante.py` (papel, uma página) | o texto do `base.html` | o arquivo | quebrava (`index`) |
| `integration/portal/test_revisao_e_comprovante.py` (`@media print`, `a.principal`) | o corpo da página | a folha aplicada | quebrava |
| `integration/inscricoes/test_envio_de_arquivo.py` (`[hidden]`, campo de arquivo) | o corpo da página | a folha aplicada | quebrava |
| `integration/inscricoes/test_envio_de_arquivo.py` (resumo acima da dobra) | a primeira `resumo-documentos` do corpo | o `id` na marcação, antes da seção "Seus dados" | quebrava — e **revelou que nunca olhou a marcação** (R-007) |
| `integration/inscricoes/test_envio_de_arquivo.py` (barra pela metade) | `style="width:50%"` | `largura-50` | quebrava |
| `portal/test_peso_da_vitrine.py` | o recorte `<style>`…`</style>` | a folha aplicada | quebrava (`index`) |
| `integration/portal/test_detalhe_selecao.py` (PDF secundário, cartão alvo inteiro) | o corpo da página | a folha aplicada | quebrava |
| `integration/portal/test_cronograma_publico.py` (dois casos) | o corpo depois do `</style>` | o corpo depois do `<body` — o mesmo texto | quebrava (`index`) |
| `interface/test_estaticos.py` (sintaxe vazada) | as folhas da gestão, tokens e erro | e o arquivo do portal | sim — ponto cego novo |
| `test_citacoes_de_requisito.py` | `*.py`, `*.html`, `*.js` | e `*.css` | **sim** — as citações da folha saíram da varredura (R-007) |
| `interface/test_politica_de_conteudo.py` (estilo embutido) | os modelos da gestão | todos os modelos | — o portal entra |
| `interface/test_folha_estatica.py` (ordem das folhas da vitrine; `FOLHAS`) | tokens → `<style>` | tokens → `portal.css` | quebrava |

**Os que ficam como estão**, lidos e conferidos: `portal/test_resultado_publico.py` e
`interface/test_larguras.py` já liam a folha aplicada, que passa a incluir o arquivo — e as mutações 15
a 17 provam que o alcançam. Os que tiram o `<style>` para ler o resto
(`test_portal_caminho_da_convocacao.py`, `test_portal_requerimento_convocacao.py`) e os que leem só o
`<main>` (`test_rascunho_depois_do_prazo.py`, `test_acompanhamento_resultado.py`,
`test_prazo_recursal_publico.py`, `test_vocabulario_das_telas_publicas.py`) ficam corretos e mais
estritos. Negativas sobre o corpo inteiro (`test_adicionar_credencial.py`, `test_portal_requerimento.py`)
ficam mais estritas. Os de vocabulário com lista literal não incluíam o `base.html`.

**Guardiões novos**: a barra pela classe do percentual, nos cinco casos do R-003; as 101 classes do
portal; a base do portal carrega o arquivo, e ele está em `FOLHAS`; todo HTML em recusa, com o caminho
fora da decisão; nenhuma resposta com o cabeçalho de observação; o protótipo em recusa.

**A mutação** (`mutacoes.py`, saída em `mutacoes.txt`): 34 mutações, uma ou mais por guardião
repontado ou novo — 22 no arquivo do portal, 9 nos modelos, 2 na política e 1 no protótipo. **Todas
reprovam**; sem mutação, os 565 casos dos mesmos testes passam. As que plantam no arquivo do portal o
que um guardião de texto procurava no modelo (1 a 9) são as que provam o repontar: sem ele, as
negativas (1, 3, 7) passariam vazias, e as positivas quebrariam por não achar a regra.

## R-005 — O peso

Medido em 18/10/2026 por `pesar_portal.py`, uma tela de cada forma de endereço da lista de rotas; antes
pela árvore de `2615b738`, depois pela da branch, sobre cópias do mesmo banco:

| Tela | Antes | Depois | Diferença |
|---|---|---|---|
| Vitrine (`/selecoes/`) | 72.765 | 6.041 | −66.724 |
| Entrada (`/selecoes/acesso`) | 68.144 | 1.420 | −66.724 |
| Página da seleção | 77.354 | 10.630 | −66.724 |
| Resultado publicado | 70.037 | 3.313 | −66.724 |
| Minhas inscrições | 68.860 | 2.136 | −66.724 |
| Inscrição | 69.305 | 2.581 | −66.724 |
| Acompanhamento | 71.982 | 5.258 | −66.724 |
| Comprovante | 71.740 | 5.016 | −66.724 |
| Requerimento | 72.053 | 5.329 | −66.724 |

A mesma diferença em todas: o `<style>` com as marcas e a indentação, menos o `<link>` com a versão. O
arquivo tem 70.653 bytes — os 65.839 da folha, o cabeçalho e as 101 classes — e vem uma vez por
versão.

## R-006 — A política, e a prova no navegador

**A regra** (D-003): `recebe_a_politica(resposta)` — HTML, sem política declarada, e não a página de
depuração com `DEBUG` — e, se recebe, `Content-Security-Policy` com a mesma constante da `091`. Sai
`EM_RECUSA`, o cabeçalho de observação, `cabecalho_para` e `em_observacao`. O caminho deixa de entrar
na decisão, e com ele a preocupação com `path_info` sob um prefixo.

**O que fica fora**, como antes: resposta que não é HTML; a página de depuração com `DEBUG`; e a
resposta que já declara política, que nenhuma view do sistema faz hoje. **A página de falha de CSRF**
do Django, com `<style>` embutido, sai sem desenho em recusa — no portal também, desde esta feature,
como já saía na gestão (achado da `091`).

**O inventário** (18/10/2026, pasta da prova; antes por `git archive` de `2615b738`, depois a árvore da
branch, cada passada num banco copiado de `ps_inventario_092`):

- **As telas**: o `capturar_portal.py` rastreia os links da vitrine sem sessão e da área de Ana,
  Bruno, Clara, Daniel, Elisa e Amanda, até três telas de cada forma de endereço — **103 telas**, com o
  protótipo do painel; a lista da passada de antes (`rotas.json`) é a da passada de depois. Para a
  barra de documentos aparecer, o `preparar_rascunhos.py` abriu, pela função da view `inscrever`,
  rascunhos de Clara, Daniel e Elisa numa seleção aberta que pede dois documentos, com nenhum, um e os
  dois registrados.
- **Medidas**: **nenhum** `status` diferente, **zero** estouros a 375 e a 1280, nenhuma largura,
  altura, título, `h1` ou conjunto de regras diferente.
- **Pixels** (`pixels.py`, com um par de ruído de cada lado): 206 variantes; 191 idênticas, 7 dentro do
  ruído e 8 acima dele — todas no comprovante. **As oito são dado na tela**, conferido nos recortes: o
  endereço do servidor, que leva a porta da passada (`localhost:8921` antes, `:8923` depois), a hora de
  emissão (`15h30` e `15h39`) e o SHA-256 do PDF, que muda com a hora. O par de ruído é da mesma
  passada e não pega essa diferença. O papel do mesmo comprovante, com a mesma porta, é idêntico.
- **As bases** (`capturar_bases.py` da `089`): vitrine, entrada, erro do portal e erro da gestão — 8 de
  8 idênticas, as mesmas regras.
- **O papel** (`IMPRESSAO=1`, a mídia de impressão emulada): os 6 comprovantes e as 9 inscrições da
  lista — 15 de 15 idênticos, o mesmo número de páginas do PDF que o navegador gera.
- **Violações da política**: antes, em observação, uma em cada tela (`style-src-elem`, o `<style>` da
  base) e duas em cada rascunho (o atributo da barra também); depois, **zero** em todas — e as 103
  respostas trazem `Content-Security-Policy`, e nenhuma `-Report-Only`. Nas bases, o mesmo: uma em
  observação na vitrine e na entrada antes, nenhuma depois.

## R-007 — Achados

- **Um guardião que nunca olhou a marcação.** `test_quantos_documentos_faltam_aparece_junto_ao_cabecalho`
  comparava a posição da primeira `resumo-documentos` com a de "Seus dados". A primeira era a regra da
  folha embutida, no `<head>` — antes de qualquer marcação —, e a comparação passava sempre. Na
  marcação, "Seus dados" aparece antes, no indicador de etapas. O caso agora compara o `id` do resumo
  com o título da seção, que é o que ele dizia medir, e passa: o resumo está acima da seção. O defeito
  era do teste, desde a `010`, e não da tela.
- **As citações das folhas fora da varredura.** `test_citacoes_de_requisito.py` varria `*.py`,
  `*.html` e `*.js`. Quando a folha da gestão saiu do modelo, na `089`, as citações dos comentários dela
  (`FR-079`, `SC-UX-005` e outras) saíram da varredura sem ninguém notar; esta feature levaria as do
  portal pelo mesmo caminho. A varredura passa a incluir `*.css`, e as citações das folhas da gestão
  voltam a ser conferidas — todas apontam para requisito que existe.
- **A página de falha de CSRF**, sem desenho em recusa, agora também no portal (R-006). Trocá-la por uma
  página do sistema (`CSRF_FAILURE_VIEW`) continua registrado, e não feito.
- **A folha do portal não foi dividida** (D-001). Ela tem a mesma ordem de chegada que a da gestão
  tinha, e uma divisão por área pediria a prova de ordem da `091`. Passo possível, registrado.
- **O inventário do portal é por rastreamento.** Telas que só se alcançam por formulário (o envio de
  um documento, a recusa de um código) ficam fora dele; as regras que elas usam estão no mesmo arquivo,
  provado igual byte a byte (R-002).
- **Os números da suíte** (`make lint check test-pg`, 4 workers, `ps_092`, 18/10/2026): **12.267
  passando, 11 pulados**, nenhuma falha — os 12.212 da `091` mais os casos novos e parametrizados desta.
