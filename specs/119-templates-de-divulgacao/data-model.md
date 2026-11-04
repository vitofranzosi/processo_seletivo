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
| `fontes` | papel → fonte livre | `titulo`, `corpo`, `destaque`; cada uma com arquivo e resumo (D-005) |
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
| `caixas` | lista ordenada de `Caixa` |
| `forma_do_periodo` | `ate` ou `de-a` (FR-3815) |
| `tem_ofertas` | booleano (FR-3817, EC-6) |
| `tem_contato` | booleano (FR-3820) |
| `ativos_posicionados` | ativo → retângulo; contam como obstáculo (D-011) |
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
| `impressao_v1` | a impressão versão 1 dos mesmos dados (D-009) |

## Evento de exportação (FR-3828)

O evento da `111`, com o `detalhe` acrescido de: `familia`, `familia_versao`, `variante`,
`formato_da_peca`, `template`, `template_versao`, `imagem`, `imagem_sha256`. A `versao_da_impressao`
passa a ser `2`. Exportação de texto não leva os campos da peça.
