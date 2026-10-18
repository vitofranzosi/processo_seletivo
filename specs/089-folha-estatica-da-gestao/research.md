# Pesquisa — 089

As decisões de governança estão na spec (D-001 a D-006). Aqui ficam as questões de desenho e de teste,
as medições e os achados. Medido em 18/10/2026 na `main` `c97ff8af`, salvo onde se diz outra coisa.

## R-001 — O que é a folha comum, e para onde vai cada parte

**Medido**: o `<style>` do `interface/base.html` vai da linha 7 à 1479. Dentro dele:

| Parte | Linhas | Bytes | Destino |
|---|---|---|---|
| `{% include "shared/_tokens.css.html" %}` | 8 | (o parcial: 28 linhas) | `<link>` para `shared/tokens.css` |
| regras | — | 53.383 (sem comentários) | `interface/gestao.css`, na ordem |
| 162 `{% comment %}` entre as regras | — | 51.884 | `/* */` em `gestao.css`, no mesmo lugar (R-002) |
| o `{% comment %}` do ponto de extensão (040) | 1463–1477 | — | fica no modelo, junto do bloco |
| `{% block estilo_da_pagina %}` | 1478 | — | fica, num `<style>` só dele (D-004) |

Nenhuma outra sintaxe de modelo aparece entre as regras — nem `{{`, nem `{%` fora dos comentários —, e
nenhum comentário divide uma linha com uma regra: a conversão é mecânica, linha a linha.

**Os tokens** são incluídos em quatro páginas, e não três: `interface/base.html`,
`interface/base_de_acesso.html`, `portal/base.html` e `shared/templates/404.html` — a página de erro
que o Django monta para `Http404` nos dois canais. As quatro passam a carregar `shared/tokens.css`.

**Onde mora `shared/tokens.css`**: `shared/` não é app — os modelos dela entram por `TEMPLATES.DIRS`.
Os estáticos entram do mesmo jeito, por `STATICFILES_DIRS = [BASE_DIR / "processo_seletivo" /
"shared" / "static"]`, e o arquivo fica em `processo_seletivo/shared/static/shared/tokens.css`,
servido em `/static/shared/tokens.css`. Descartado: pôr os tokens em `interface/static/` — o portal
passaria a depender de um diretório da gestão, o que o `shared/` existe para evitar.

**A conversão é por script, e a equivalência também.** Um script lê o modelo, separa as linhas da
folha, troca `{% comment %}`/`{% endcomment %}` por `/*`/`*/` e grava os dois arquivos; outro extrai as
regras (sem comentários de nenhum dos dois tipos, espaços normalizados só no fim de linha) do modelo de
antes e dos `.css` de depois e exige igualdade byte a byte, na ordem. Os dois ficam em
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/`, com a saída.

## R-002 — Os comentários como `/* */`

**Decisão**: D-002. Cada `{% comment %}…{% endcomment %}` vira `/* … */` com o mesmo texto, nas mesmas
linhas.

**O comentário que fala de comentário.** Um único comentário contém `/*` e `*/` — o que explica por que
os comentários eram de modelo: "escrito com `/* */`, este bloco estourou em 40 bytes o teto de 120.000".
Copiado como está, o `*/` dele encerraria o comentário no meio e deixaria o resto da prosa como regra
inválida — o navegador a descartaria em silêncio, e a regra seguinte poderia ser engolida. A cópia troca
a expressão pela descrição dela — "escrito como comentário de CSS" —, sem caractere invisível
(a memória "Write grava escape Unicode literal" registra a armadilha), e ganha uma linha que diz que a
premissa deixou de valer com a `089`. O script de equivalência verifica que nenhum
comentário convertido contém `*/` antes do fim.

**O custo**: `gestao.css` fica com ≈ 105 KB, o dobro das regras. Viaja na primeira página da sessão;
depois, o nginx do guia responde `no-cache` e o navegador revalida (304, sem corpo). Descartado: tirar
os comentários na entrega (minificar) — exigiria passo de construção, que o projeto não tem, e é
otimização para depois de medir.

## R-003 — A versão no endereço

**Decisão**: D-003. A tag `{% estatico 'interface/gestao.css' %}`, numa biblioteca de modelos de
`shared/` registrada em `TEMPLATES.OPTIONS.libraries` (como `estaticos`), devolve
`{% static %}` + `?v=` + os 12 primeiros dígitos hexadecimais do SHA-256 do conteúdo. O arquivo é
achado pelos *finders* do `staticfiles` (`django.contrib.staticfiles.finders.find`), os mesmos que o
runserver usa para servi-lo; arquivo ausente é erro (`ImproperlyConfigured`), e não `<link>` quebrado
em silêncio. O resumo é memorizado por `(arquivo, st_mtime_ns, st_size)`: a página paga um `stat`, e
só relê o arquivo quando ele mudou. **Na revisão do PR**, a primeira versão — recalcular a cada página
com `DEBUG`, uma vez por processo sem ele — foi trocada por esta, que faz as duas coisas sem ramo e não
lê 108 KB por página no runserver.

**E a falta da folha é verificação de sistema** (`estaticos.E001`, registrada pelo `ready` da
`interface`): o `check` e o `migrate` da implantação recusam seguir sem as duas folhas. Sem ela, a
implantação subiria, passaria no `/health`, e todo pedido das quatro bases viraria 500 — o da página de
erro inclusive, que também carrega os tokens.

**Como funciona em cada lugar:**

| Onde | Quem serve | Resumo | Efeito |
|---|---|---|---|
| runserver | `staticfiles`, pelos finders | relido quando a data ou o tamanho mudam | editou a folha, a próxima página pede um endereço novo — o cache do navegador não serve a folha velha (a armadilha da memória "Preview reusa script em cache", com a `shell.js`, na `053`) |
| testes | o test client não pede a folha | idem | os guardiões leem o arquivo, não o endereço |
| produção (guia) | nginx, por `alias` para os diretórios da release; com `?v=`, `max-age` de um ano e `immutable` | idem, por processo do gunicorn | a folha nova tem endereço novo; o navegador guarda a folha sem revalidar, e cada página deixa de esperar duas idas e voltas |

**Descartados**: o `ManifestStaticFilesStorage` — exige `STATIC_ROOT` e `collectstatic` na
implantação, e o guia serve os diretórios da release sem coletar (lacuna I-3, aberta); fechar a lacuna é
mudar a implantação. A data de modificação do arquivo — muda num `git checkout` sem o conteúdo mudar. O
número da versão do sistema — muda a cada implantação, mesmo sem a folha mudar.

**Fora do escopo**: os scripts (`shell.js` e os demais) continuam com `{% static %}` sem versão. Usar a
mesma tag neles é um passo possível, e registrado.

## R-004 — A ordem no `<head>`

```text
<link rel="stylesheet" href="{% estatico 'shared/tokens.css' %}">
<link rel="stylesheet" href="{% estatico 'interface/gestao.css' %}">
<style>{% block estilo_da_pagina %}{% endblock %}</style>
```

Folhas externas e `<style>` entram na cascata na ordem do documento; com a mesma especificidade, vence
a que vem depois — exatamente como quando os três estavam no mesmo `<style>`. As duas folhas externas
bloqueiam a renderização, como o `<style>` bloqueava: não há desenho sem estilo na primeira visita.
Na página de acesso, no portal e no 404, o `<link>` dos tokens entra antes do `<style>` que já existia,
no lugar do `{% include %}`.

## R-005 — Os guardiões que leem a folha

**Medido** (18/10, `c97ff8af`): **22 arquivos de teste** leem a folha comum ou os tokens — não os 14
que o pedido estimava. O merge da `088` trouxe o 23º (`test_decisoes_da_etapa_4.py`, a regra de
impressão), achado pela suíte e não pela varredura, que tinha sido feita antes dele. A folha comum renderizada tem 53.381 bytes; os tokens, 1.326. Fora destes, ~30
arquivos citam `<style>` ou o modelo só para tirar o estilo do texto que examinam, ou leem só marcação;
ficam iguais ou mais estritos, e estão listados no fim desta seção.

**O risco não é o teste que quebra — é o que passa.** Hoje, `corpo[corpo.index("<style>"):…]` devolve a
folha inteira. Depois da mudança, toda tela ainda tem um `<style>`, só com o bloco da página — na lista,
duas regras; na Comissão, uma. Uma afirmação negativa (`regra(x) is None`, `x not in folha`) sobre esse
resto passa sem examinar nada. **Em 14 dos 23 arquivos há pelo menos uma verificação assim.**

### Como cada um lê, e como passa a ler

Três formas, e um apoio comum para cada (T013):

- **Texto do modelo** (`FONTE`, `FOLHA`, `base.read_text()`): passa a ler `gestao.css`, com os
  comentários — como antes lia o modelo com os `{% comment %}`. Os que descontavam comentário
  (`sem_prosa`, `sem_comentarios`) já descontam `/* */` e `{% comment %}`; os que não descontavam
  continuam vendo a prosa que já viam. A exposição à prosa é a mesma de antes.
- **Folha renderizada** (o primeiro `<style>` da resposta): passa a ler a folha que a página aplica — as
  folhas externas do `<head>`, achadas pelos *finders*, **sem os `/* */`** delas, seguidas dos `<style>`
  do documento como estão. Sem comentários porque a folha renderizada de antes não os tinha (os de
  modelo não saem na resposta): é o mesmo texto, na mesma ordem.
- **Tamanho da resposta**: não muda de forma; o número muda (R-008, D-006).

`FONTE` em `test_acessibilidade.py` serve a dois papéis — marcação (o salto para o conteúdo e o
`<main>`) e folha. Vira dois nomes: o modelo continua sendo o modelo, e a folha passa a ser
`gestao.css`. `TOKENS` lê `shared/static/shared/tokens.css`; com o parcial apagado e o nome velho, o
módulo e os quatro `test_polish_da_05x` que o importam quebrariam na coleta.

### Os 23, por risco

"Silencioso" é a verificação que passaria sem examinar a folha comum; a mutação planta, no `.css`, a
violação que essa verificação existe para pegar. Rodado em 18/10/2026 por
[`mutacoes.py`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-089/mutacoes.py), com a
saída em `mutacoes.txt` ao lado: **28 mutações, 28 reprovam**; sem mutação, os 509 casos dos mesmos
testes passam.

| # | Arquivo (`tests/…`) | Lê | Silencioso hoje se não repontado | Mutação planejada | Resultado |
|---|---|---|---|---|---|
| 1 | `interface/test_acessibilidade.py` | texto (`FONTE`, `TOKENS`, `sem_prosa`, `folha_da_pagina`) | `test_nenhum_modificador_fica_sem_a_base_que_o_usa` (as bases nunca são achadas) | 4 mutações: `.marca-irreversivel{` → `.zzmut.marca-irreversivel{` (modificador sem a base); `.oculto{` → `.ocultx{` (classe órfã); `--texto` a `#bbbbbb` em `tokens.css` (contraste); `.distribuicao-moldura` com `overflow-x:auto` | reprova |
| 2 | `interface/test_polish_da_057.py` | texto (`sem_prosa(FONTE)`, `regra`) | `test_o_detalhe_desenha_as_terminais…`, `test_os_documentos_da_inscricao_seguem_a_mesa` inteiros; L321 | `.terminais .botao{color:red}`; `.requisitos-apresentados{color:red}` | reprova |
| 3 | `interface/test_polish_da_058.py` | texto (o `regra` da 057) | `test_as_terminais_moram_num_parcial_das_duas_telas` inteiro; L137 | `.colunas.ao-topo{color:red}` | reprova |
| 4 | `interface/test_telas_de_uso_diario.py` | texto (`base.html`) | `test_cada_correcao_vale_so_na_sua_tela` (L194) | `.imutavel code{overflow-wrap:anywhere}` acrescentada | reprova |
| 5 | `interface/test_larguras.py` | renderizada (`folha`) | gestão de `test_nenhuma_das_bases_crava_largura_em_pixel`; `test_a_marca_de_atencao_nao_alcanca…`; L115, L261 | `main .zzmut{max-width:600px}` | reprova |
| 6 | `interface/test_campos_que_a_escolha_governa.py` | renderizada (`folha`) | `test_a_folha_nunca_esconde_por_padrao` | `.so-admite{display:none}` | reprova |
| 7 | `interface/test_polish_da_056.py` | texto (`sem_prosa(FONTE)`) | L42, L51, L162–163 | `text-transform:uppercase` na regra existente de `.assistente .estado` | reprova |
| 8 | `interface/test_achados_das_revisoes.py` | texto (`base.html`, `^` multilinha) | L142 | `.acoes .marca-irreversivel{align-self:center}` | reprova |
| 9 | `interface/test_alocacoes.py` | renderizada (`folha_de_estilo`) | L254 | `.distribuicao thead th .codigo{display:block}` | reprova |
| 10 | `interface/test_lista.py` | renderizada (`folha`) | L206 | `.acao.desabilitado` com `color:var(--verde)` | reprova |
| 11 | `interface/test_comissao.py` | renderizada (`folha_de_estilo`) | — (só positivas) | `.s-PRESIDENTE{` → `.s-PRESIDENTX{` | reprova |
| 12 | `performance/test_escala_da_mesa.py` | tamanho da resposta | o teto ganha ≈ 54 KB de folga (D-006) | — (o teto não muda; R-008) | — |
| 13 | `interface/test_estaticos.py` | página renderizada | nenhum, mas ganha ponto cego: `gestao.css` não é renderizado nem varrido, e um `{% comment %}` esquecido na conversão iria como CSS quebrado | `{% comment %}` plantado em `gestao.css` | reprova |
| 14 | `portal/test_resultado_publico.py` | renderizada do portal | `"--pagina" in folha` casava com o `var(--pagina)` — já antes da 089; apertado para `--pagina:` | `--pagina:96rem` tirado de `tokens.css` (reprova também `test_larguras`) | reprova |
| 15 | `interface/test_polish_da_055.py` | texto (`sem_prosa(FONTE)`) | — (quebra alto) | `th,td` com `padding:.4rem .75rem` | reprova |
| 16 | `interface/test_medida_dos_campos.py` | renderizada (`folha`, `regras()`) | — | `--leitura:70ch` em `tokens.css` | reprova |
| 17 | `interface/test_shell_da_gestao.py` | texto (`base.html`, divide em `@media`/`\n}`) | — | o gradiente da barra recolhida `to left` | reprova |
| 18 | `interface/test_telas_de_quem_elabora.py` | texto (`FOLHA`, `sem_comentarios`) e varredura de `templates/*.html` | — mas a varredura de molduras que rolam não alcança `gestao.css`: passa a incluí-lo | `.zzmoldura{overflow-x:auto}` sem posição | reprova |
| 19 | `interface/test_acessibilidade_da_classificacao.py` | texto (substring) | — | `.tabela-rolavel{overflow-x:scroll}` | reprova |
| 20 | `interface/test_visao_dos_perfis.py` | corpo inteiro (regex) | — | `.tabela-rolavel` fora da regra de `position:relative` | reprova |
| 21 | `interface/test_visao_da_classificacao.py` | corpo inteiro (regex) | — | idem | reprova |
| 22 | `integration/interface/test_inscricoes_recebidas.py` | corpo inteiro (substring) | — | `.tabela-rolavel{overflow-x:scroll}` | reprova |
| 23 | `interface/test_decisoes_da_etapa_4.py` (da `088`) | texto (`base.html`, sem `{% comment %}`, o `@media print`) | — (quebra alto: o `index` não acha a regra) | o `>a` tirado do esconder do papel; `white-space:nowrap` no cabeçalho impresso | reprova |

Os três de corpo inteiro (20–22) procuram a regra comum no HTML da página; passam a procurá-la na
folha que a página aplica, que é onde ela está.

### O que a conversão não pode fazer, por causa deles

- **Linha a linha, sem minificar.** Vários guardiões ancoram no formato: `^` multilinha (achados,
  quem elabora), `(?:^|[}\n])` (o `regra` dos polish, larguras), `\n}` no fim de `@media` (shell,
  larguras, polish 058). A conversão preserva quebras e espaços.
- **O comentário com `*/`** (R-002): sem a correção, o resto da prosa entraria no seletor da regra
  genérica dos campos de texto, o navegador descartaria a regra, e os removedores não gulosos de
  `/* */` deixariam a sobra no mesmo lugar — `test_larguras::test_todo_campo…` continuaria passando.
  Falso negativo duplo; daí a verificação no script de equivalência.
- **Prosa com chave**: dois comentários citam regras (`thead th>*{display:block}`, `.campos{display:flex}`)
  e um cita `@media`. Já estavam lá como `{% comment %}` e os guardiões de texto que não descontam
  comentário já os viam; a folha renderizada, não — por isso o apoio desconta `/* */` das externas.

### Os que não mudam

Tiram o `<style>` para examinar o resto e ficam corretos (redundantes): `test_visao_geral.py`,
`test_minha_etapa.py`, `test_avisos.py`, `test_portal_caminho_da_convocacao.py`,
`test_portal_requerimento_convocacao.py`, `integration/avaliacoes/test_documento.py`,
`integration/supervisao/test_autorizacao.py`, `acceptance/test_supervisao_do_processo.py`,
`interface/test_supervisao.py` e três do portal que leem só o `<main>`. Negativas sobre o corpo inteiro,
que ficam mais estritas: `authorization/test_visao_institucional.py`, `test_ocupacao.py`,
`test_portal_requerimento.py`, `integration/identidade/test_adicionar_credencial.py`. Só do portal,
cuja folha própria fica no documento: `portal/test_peso_da_vitrine.py` (não mede tamanho, apesar do
nome), `integration/portal/test_revisao_e_comprovante.py`, `test_acessibilidade_do_portal.py` (varre o
texto do modelo do portal, que nunca cobriu os tokens), `test_cronograma_publico.py`,
`test_detalhe_selecao.py`, `test_envio_de_arquivo.py`. Só marcação ou só o caminho do modelo: os de
vocabulário, `test_paineis_e_telas_de_apoio.py`, `test_gramatica_das_portas.py`, e os três que
importam `GESTAO` do `test_polish_da_055` — estes quebrariam na coleta pela cadeia de importação se
`TOKENS` não fosse repontado. Os roteiros do inventário servem os estáticos pelo `StaticFilesHandler`
(`capturar.py`), e os de comparação leem JSON.

### Atributos `style=""` que restam (FR-2037)

**5** nos modelos: 4 na `interface` (o `<svg>` dos símbolos em `base.html` e em `base_de_acesso.html`,
`minhas_etapas.html`, `_serie_de_inscricoes.html`) e 1 no `portal` (`_documentos.html`); nenhum em
`shared`. Com os 30 blocos `estilo_da_pagina`, os 5 parciais `_estilo_*`, a folha do portal e a do 404,
é o que uma CSP sem `'unsafe-inline'` para estilo ainda recusaria — o passo 2.

## R-006 — O guia de implantação

O nginx do guia (§14) serve só `/static/interface/` e `/static/portal/`, e responde 404 ao resto de
`/static/`. Sem um `location` para `/static/shared/`, os tokens não carregariam em produção e as quatro
páginas perderiam a paleta inteira. O guia ganha:

- o `location ^~ /static/shared/` com `alias` para `processo_seletivo/shared/static/shared/`, os mesmos
  cabeçalhos dos outros dois;
- na tabela do §15.1 e na lista de componentes, "JS" passa a "JS e CSS";
- um `map $arg_v` no topo do site: o que vem com `?v=` (as folhas) recebe `max-age` de um ano e
  `immutable`; o resto (os scripts, sem versão) continua `no-cache`. Na primeira versão as folhas
  ficavam `no-cache`, e cada página revalidava as duas antes de desenhar; a revisão do PR trocou;
- na lista de verificação (§ final), `curl` de `/static/interface/gestao.css` e
  `/static/shared/tokens.css` com 200 e `text/css`.

## R-007 — A prova visual pixel a pixel

O `comparar.py` acusa `status` e estouro; o `medidas.py`, largura, altura, título e `h1`. Nenhum dos dois
vê cor ou fonte — e uma folha que não carregasse, ou um token perdido, mudaria cor sem mudar medida.
Daí o `pixels.py`, novo na pasta do inventário: para cada PNG de mesmo nome em duas pastas, conta os
pixels diferentes e a intensidade máxima da diferença (`ImageChops.difference`), e classifica a
variante comparando a diferença antes→depois com a diferença antes→ruído (duas capturas do mesmo
código; a memória "Pixel a pixel precisa de linha de ruído" registra o que muda sozinho: hora, cantos,
cursor, suavização em moldura que rola). Uma variante passa quando a contagem antes→depois não é maior
que a antes→ruído **ou** quando as duas são zero.

**Na implementação, um par de ruído não bastou** (ver os achados): a suavização muda de lugar a cada
passada. O `pixels.py` toma vários pares de capturas do mesmo código — antes × segunda passada,
antes × captura do `git archive`, depois × segunda passada — e a linha de ruído de cada variante é o
maior deles. E entrou uma terceira prova, sem ruído nenhum: o resumo das regras que a página aplica,
como o Chrome as interpretou (`estilos.py`, `ESTILOS=1` no `capturar.py`), comparado pelo
`medidas.py`.

As bases fora da gestão não estão no inventário, salvo a página de acesso. `capturar_bases.py` captura
a vitrine e a entrada do portal e a página de erro (com `DEBUG=False`, para o 404 do sistema, e não a
página de depuração), a 1280 e a 375 px, no mesmo formato.

## R-008 — O peso das páginas

**Medido em 18/10/2026**, antes sobre `41cf1b4c` (a `main` com a `088`) e depois sobre a branch, no
mesmo banco (`ps_inventario_089`) e no mesmo banco de teste (`ps_089`):

| Página | Antes | Depois | Diferença |
|---|---|---|---|
| Distribuição com 500 conclusões — o `len(corpo)` que o teto de 120.000 prende | 95.385 | 40.796 | −54.589 |
| Distribuição (`pesar.py`, bytes da resposta) | 72.967 | 18.358 | −54.609 |
| Lista de Processos | 65.604 | 10.995 | −54.609 |
| Minhas Etapas | 61.873 | 7.264 | −54.609 |

O `<style>` da resposta caiu de 54.760 bytes para 3 (a Distribuição e Minhas Etapas não preenchem o
bloco) e 145 (a lista, com as duas regras dela). O guardião da Distribuição mede caracteres
(`len` do texto decodificado), e por isso a diferença dele é 20 menor que a dos bytes.

| Arquivo | Bytes | Sem comentários | Comprimido (gzip) |
|---|---|---|---|
| `interface/static/interface/gestao.css` | 106.280 | 53.430 | 32.516 |
| `shared/static/shared/tokens.css` | 1.704 | 386 | — |

A primeira página da sessão baixa ≈ 108 KB de folhas (≈ 33 KB se o servidor comprimir); da segunda em
diante, nada além da revalidação. Antes, cada página levava ≈ 55 KB de folha no próprio HTML: a conta
empata na segunda página e ganha daí em diante.

## Achados

- **A revisão do PR achou oito pontos, e os oito foram corrigidos no mesmo PR**: o apoio dos guardiões
  passou a ler qualquer `<link rel="stylesheet">` e qualquer `<style>`, com os atributos em qualquer
  ordem; o nginx do guia guarda as folhas versionadas por um ano (`immutable`), e o `no-cache` fica para
  os scripts; a falta de uma folha é verificação de sistema (`estaticos.E001`); o resumo é memorizado
  por data e tamanho, sem ramo por `DEBUG`; o comentário da escala de títulos que ainda dizia "prosa em
  comentário de Django" ganhou a mesma nota da `089` do outro; a fonte única dos tokens passou a ser
  conferida por todos os nomes, e não só por `--verde`; os seis invólucros `folha()` deram lugar a
  `folha_da_pagina`; e as quatro remoções de comentário, a `sem_comentarios`.

- **Uma mutação que não reprovou era mutação errada, não guardião fraco.** A primeira versão da do
  `test_polish_da_056` acrescentava `.assistente .estado{text-transform:uppercase}` no fim da folha; o
  `regra()` dos polish devolve a **primeira** regra do seletor, a que já existia. Refeita na regra
  existente, reprova. Vale para quem escrever mutação contra esses guardiões.
- **O `"--pagina" in folha` do resultado público nunca pegou a declaração.** Casava também com o
  `var(--pagina)` da folha do portal, antes e depois da 089 — tirar a declaração de `tokens.css` não o
  reprovava. Apertado para `--pagina:`, reprova; o `test_larguras` já pegava o mesmo defeito.
- **O estilo computado não serve de prova de "nada mudou".** O resumo dos estilos computados de cada
  elemento diferiu entre duas passadas do **mesmo** código em 44 e 50 das 168 variantes — larguras
  usadas, transições. A sequência de regras do CSSOM, como o Chrome as interpretou, é estável e foi a
  prova adotada (`estilos.py`).
- **A linha de ruído de um par só reprova telas sem defeito.** Com um par (antes × ruído), quatro
  variantes da barra recolhida acusavam diferenças de 1 a 15 de intensidade — e as mesmas apareceram
  entre duas passadas do código novo. O `pixels.py` passou a tomar o maior de vários pares.
- **O teto da Distribuição passou a sobrar 79 mil caracteres** (40.796 de 120.000). O crescimento da
  folha comum deixa de ser cobrado por ele; se a folha deve ganhar teto próprio é decisão do usuário
  (D-006).
- **Próximos passos possíveis, fora do escopo**: os 30 blocos `estilo_da_pagina` e os 5 parciais
  `_estilo_*` em arquivos (passo 2); a mesma tag `estatico` nos scripts, que continuam sem versão; a CSP
  (passo 3), que ainda esbarraria nos 5 `style=""` e nos `<style>` que ficam.
