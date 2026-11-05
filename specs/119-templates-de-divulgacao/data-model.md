# Data Model: Templates de Divulgação por Família e Formato

Nada aqui é tabela. Formato, família e template são declarações no código (D-003); a escolha vai no
evento de exportação que a `111` já grava (D-008); a ficha continua leitura sem estado.

## Formato (FR-3801)

| Campo | Post | Story | Banner |
|---|---|---|---|
| `chave` | `post` | `story` | `banner` |
| `largura × altura` | 1080 × 1350 | 1080 × 1920 | 1500 × 850 (D-007, P-3) |
| `margem` | 80 | 80 nas laterais | 60 |
| `zonas_reservadas` | — | `(0, 0, 1080, 250)` e `(0, 1670, 1080, 1920)` | — |
| `corpo_minimo` | 24 | 24 | 28 |
| `chamada_a_acao` | "Acesse o link na bio" | "Acesse o link na bio" | "Acesse o edital" |

## Família (FR-3802)

| Campo | Tipo | Regra |
|---|---|---|
| `chave` | texto | `institucional`, `pos-lato-sensu`, `fic`, `libras`, `uab`, `aperfeicoamento`, `internos`, `tmd` |
| `nome` | texto | o que a lista mostra |
| `versao` | inteiro | sobe a cada mudança de ativo, frase ou caixa |
| `unidades` | conjunto de códigos de unidade | vazio só na Institucional, que vale para todas (FR-3805) |
| `paleta` | nome → cor | as cores que as caixas citam |
| `fontes` | papel → fonte livre | `titulo`, `corpo`, `destaque` e, quando a família tem uma terceira fonte, `rotulo` (a Space Mono da FIC, no número e na faixa); cada uma com arquivo e resumo (D-005) |
| `ativos` | nome → arquivo com resumo | marca, padrão, balão, ilustração, rodapé (D-004) |
| `imagens` | lista de 0 a 6 `Imagem` | banco curto (FR-3807) |
| `variantes` | lista de `Variante` | vazia, ou Internos: `servidores`, `estudantes` |
| `frases` | nome → texto | chamada do alto, rótulos; passam a FR-3814 |
| `templates` | formato → `Template` | só os formatos desenhados |

**Imagem**: `chave`, `arquivo`, `sha256`, `descricao` (para o alternativo), `licenca`, `origem`.

**Variante**: `chave`, `nome`, `chamada` (frase fixa; FR-3814).

## Template (FR-3803)

| Campo | Regra |
|---|---|
| `identificador` | `<familia>/<formato> · <versao>`; a Institucional mantém `feed-1080x1350 · 1` (D-002) |
| `versao` | inteiro |
| `resumo` | SHA-256 da declaração canônica, dos resumos dos ativos, imagens e fontes usados, e do resumo das referências SVG do template; fixado no módulo por versão, recalculado pela suíte e nomeado na liberação (FR-3833, D-014) |
| `resumo_das_referencias` | SHA-256 dos SVG de referência do template, fixado no módulo e conferido pela suíte |
| `caixas` | lista ordenada de `Caixa` |
| `forma_do_periodo` | `ate` ou `de-a` (FR-3815) |
| `tem_ofertas` | booleano (FR-3817, EC-6) |
| `tem_contato` | booleano (FR-3820) |
| `ativos_posicionados` | ativo → retângulo; contam como obstáculo (D-011), salvo os que `dimensoes["opacos"]` nomeia com a cor de dentro, que recebem texto (a bolha do número da FIC) |
| `area_da_imagem` | retângulo e recorte, quando a família tem banco |

**Caixa**: `campo` (`chamada`, `titulo`, `ofertas`, `periodo`, `selo_prorrogado`, `numero`,
`chamada_a_acao`, `busca`, `contato`, `selo_da_versao`), retângulo, `fonte` (papel), `cor`,
`fundo` (cor lisa; D-011), `corpos` (do máximo ao mínimo, nenhum abaixo do mínimo do formato),
`linhas_maximas`, `alinhamento`, `ao_nao_caber` (`recusar` ou `omitir`; só `contato` e `titulo`, este
pela ordem da FR-3426 da `111`, podem omitir).

## Escolha (FR-3806, D-008)

Não persistida. Vem do formulário e é validada contra as listas do instante:

| Campo | Validação |
|---|---|
| `familia` | na lista da FR-3805 |
| `variante` | entre as da família; obrigatória se houver |
| `imagem` | entre as da família; obrigatória se houver banco |
| `formato_da_peca` | entre os templates liberados da família (FR-3808) |
| `manchete` | índice na lista da FR-3427 da `111` |

Fora da lista: recusa sem gerar e sem registrar (EC-9).

## Ficha, versão 2 (FR-3809–FR-3811)

Acréscimos à `Ficha` da `111`:

| Campo | Origem |
|---|---|
| `Oferta.carga_horaria` | `workload` do Perfil no conteúdo vigente, aparado; `""` = não declarada |
| `contato` | `Unidade.atendimento` da unidade do ato, aparado; `""` = não declarado |
| `impressao` | versão 2: os campos da versão 1, mais `carga_horaria` em cada oferta e `contato` |
| `campos_v1` | os campos da versão 1 dos mesmos dados, sem carga horária nem contato |
| `impressao_v1` | a impressão versão 1 dos mesmos dados (D-009); a diferença de uma exportação v1 se calcula entre os `campos` gravados e os `campos_v1` |

## Evento de exportação (FR-3828)

O evento da `111`, com a `versao_da_impressao` em `2`. Os campos que já existem continuam com o mesmo
nome e sentido. O `detalhe` é acrescido conforme o tipo de arquivo:

| Exportação | Acréscimo ao `detalhe` |
|---|---|
| `md`, `txt` | nada: texto não tem família |
| `png`, `svg` | `familia`, `familia_versao`, `variante`, `imagem`, `imagem_sha256`, `formato_da_peca`, `template`, `template_versao`, `template_resumo` |
| `zip` da Institucional | o da `111`, sem mudança |
| `zip` de família da comunicação | `familia`, `familia_versao`, `variante`, `imagem`, `imagem_sha256` e `pecas`: lista com uma entrada por formato da família (ver o manifesto) |

Os campos singulares da `111` — `template`, `manchete` e `sem_peca` no evento, e `peca` no manifesto —
continuam significando a Institucional; no ZIP de família vêm nulos, e quem lê usa `pecas`.

**Ordem dos arquivos no ZIP de família**: `kit.md`, `kit.txt`; para `post`, `story` e `banner`, nesta
ordem, `peca-<formato>.png`, `peca-<formato>.svg`, `peca-<formato>-alternativo.txt`; `ficha.json`;
`manifesto.json`. O ZIP da Institucional mantém os nomes e a ordem da `111`; a ficha e a impressão
nele passam a ser as da versão 2.

## Manifesto do ZIP de família (FR-3829, D-015)

Os campos do manifesto da `111` continuam (`kit`, `edital`, `instantes`, `versao`, `impressao`,
`rasterizador`, `endereco_publico`, `notas`, `arquivos`), mais:

| Campo | Conteúdo |
|---|---|
| `versao_do_manifesto` | `2` (o da `111`, sem o campo, é a versão 1) |
| `familia` | `{chave, versao, variante}` |
| `imagem` | `{chave, sha256}` ou nulo |
| `pecas` | lista ordenada por formato (`post`, `story`, `banner`), uma entrada por formato que a família declara |
| `fontes`, `ativos` | `{arquivo: sha256}` dos usados pelos templates incluídos |

Cada entrada de `pecas`:

| Campo | Conteúdo |
|---|---|
| `formato_da_peca` | `post`, `story` ou `banner` |
| `template`, `template_versao`, `template_resumo` | os do código |
| `incluida` | booleano |
| `motivo` | nulo se incluída por inteiro; `sem_rasterizador` com `incluida: true` quando só o PNG falta; senão, com `incluida: false`, `nao_liberado`, `versao_divergente` (versão ou resumo), `recusa` (com o texto) |
| `manchete` | a usada naquele formato, ou nula |
| `arquivos` | `[{nome, sha256}]` dos arquivos daquele formato no ZIP |

A lista `arquivos` do topo continua cobrindo todo arquivo do ZIP; a de cada entrada só repete os
daquele formato, para que a recusa de um não se confunda com a de outro. O evento leva a mesma lista
`pecas`.
