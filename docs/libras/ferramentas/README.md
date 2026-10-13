# Ferramentas do estudo de Libras

Scripts de **análise documental** que sustentam o catálogo, as coberturas, as narrativas e as medições. Não
são funcionalidade do sistema: não alteram o backend, não acessam banco (salvo `exportar_corpus.py`, não
reexecutado) e não publicam nada. Versionados na rodada 2 e estendidos na rodada 3 (2026-10-11), para editais
escritos fora do sistema.

## Dependências

| O quê | Para quê |
|---|---|
| Python ≥ 3.9, só a biblioteca padrão | todos os scripts, salvo os dois que rodam pelo backend |
| `pdftotext` (poppler) | extrair o texto dos PDFs (`fatiar.py`, sondagem) |
| ambiente do backend (`cd backend && uv sync`) | `origem_do_texto.py` (importa o compositor) e `exportar_corpus.py` (importa os modelos) |

Lint: `cd docs/libras/ferramentas && uv run --project ../../../backend ruff check .` (configuração em
`ruff.toml`; os arquivos de dados, que são prosa, estão isentos de linha longa).

## Dados (editados à mão)

| Arquivo | Conteúdo |
|---|---|
| `linhas.py` | as âncoras de cobertura de cada edital: começo literal de cada trecho, item, unidade, regras embutidas (`extras`), dependências, riscos; e `IMAGENS`, o texto que um PDF real só tem em imagem, em três registros — transcrição fiel, normalização da comparação e avaliação de equivalência (rodada 4) |
| `unidades.py` | as unidades do catálogo; o bloco da rodada 2 com desdobramentos (`desdobrar`, `filha`), correções (`corrigir`) e tipagem de variáveis; e o da rodada 3, com as unidades dos editais reais (`real`) e as reclassificações |
| `ids.py` | identificadores congelados: `V1` (rodada 1), `V2` (rodada 2) e `V3` (rodada 3, LIB-0155 a LIB-0316). Nunca se renumeram |
| `notas.py` | notas de reuso por edital, escritas à mão |
| `narrativas.py` | a camada comunicativa: enunciados, fontes, ambiguidades, perguntas; no fim, o bloco da rodada 4, com pendências, atos fora da versão inventariada e o estado de cada pergunta (`rev`, `revp`, `novo`, `novap`) |
| `referencia/catalogo-v1.json` | registro da versão 1 do catálogo (unidades, ocorrências, situações, métricas) |
| `referencia/sondagem-entrada.json` | a lista dos 20 PDFs da sondagem, com edital e família |

## Scripts

Todos se executam **da raiz do repositório**.

| Script | Entradas | Saídas | Execução |
|---|---|---|---|
| `fatiar.py` | um PDF e uma lista de âncoras | trechos consecutivos e rodapés; falha se a cobertura não fechar | módulo, usado pelos demais |
| `corpus.py` | `editais/*/fonte/pub1.pdf` (simulados) e o PDF publicado (reais, campo `pdf`), `linhas.py`, `unidades.py`, `ids.py` | linhas, ocorrências e situação de cada uma; `SIMULADOS` e `REAIS` | módulo |
| `gerar.py` | os dados acima e `notas.py` | `catalogo/indice.md`, `catalogo/unidades/*.md`, `editais/*/cobertura.md`, `roteiro-producao.md`, `oportunidades-reuso.md` | `python3 docs/libras/ferramentas/gerar.py` |
| `narrar.py` | os dados acima e `narrativas.py` | `editais/*/narrativas/*.md`; recusa fonte inexistente | `python3 docs/libras/ferramentas/narrar.py` |
| `medir.py` | os dados acima e `referencia/catalogo-v1.json` | métricas da versão 3 ao lado da 1 e da 2: simulados entre si; reais contra o corpus simulado inteiro (dentro da unidade); reais contra as frases que o sistema gera (origem C pura, sem restrição de unidade); reais entre si — cada uma com conjunto, denominador e limites escritos | `python3 docs/libras/ferramentas/medir.py` |
| `comparar_anexos.py` | os anexos publicados à parte (`editais/*/fonte/consulta-2026-10-11/`) e as linhas de cobertura | diferenças de palavras entre o anexo à parte e o de dentro do PDF | `python3 docs/libras/ferramentas/comparar_anexos.py` |
| `comparar_secoes.py` | os PDFs de `comparacao-focalizada/fontes/` | diferenças entre os §3 e §9 do 19/2026 e do 46/2026, sem espaços | `python3 docs/libras/ferramentas/comparar_secoes.py` |
| `rotulos_de_video.js` | a página de um vídeo do Cefor no YouTube, aberta num navegador | instantes em que o rótulo de seção muda na barra lateral | no console da página; ver o cabeçalho do arquivo |
| `comparar_retificacoes.py` | `editais/{91,01}-2026/fonte/pub*.pdf` | trechos com texto ou página diferentes entre original e Retificação | `python3 docs/libras/ferramentas/comparar_retificacoes.py` |
| `origem_do_texto.py` | `editais/*/fonte/pub1-canonico.json` | palavras por origem (redação livre, valores, texto fixo) | `cd backend && DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py shell < ../docs/libras/ferramentas/origem_do_texto.py` |
| `sondagem_editais_reais.py` | os PDFs de `referencia/sondagem-entrada.json`, numa pasta | recorrência de frases entre editais reais | `python3 docs/libras/ferramentas/sondagem_editais_reais.py ~/Downloads` |
| `exportar_corpus.py` | um banco com os editais publicados | PDFs, conteúdo canônico e alterações, em `ferramentas/saida/` | ver o cabeçalho do script |

Os arquivos gerados por `gerar.py` e `narrar.py` **não se editam à mão**: a correção vai nos dados, e os
arquivos se regeneram. Os escritos à mão são `README.md`, `auditoria-sistema.md`, `viabilidade.md`,
`metodo-incremental.md`, `camada-comunicativa.md`, `catalogo/terminologia.md`, `historico/` e, em cada
edital, `manifesto.md` e `retificacoes.md`.

## O que se reproduz e o que não

| Resultado | Reprodução | Conferido na rodada 4 |
|---|---|---|
| cobertura integral e catálogo | integral, a partir do repositório; nos reais, com o `pdftotext` (poppler) — outra versão pode quebrar uma âncora, e `fatiar.py` falha alto | sim |
| métricas do catálogo (`medir.py`) | integral | sim; a parte dos simulados reproduz os números da rodada 2 |
| origem do texto (§1 da auditoria) | integral, **com o compositor do commit `bbc8e04c`**; outro código pode dar outro texto fixo | não reexecutada (rodada 2: 58/10/32, 64/9/27, 33/11/55); não se aplica aos reais, que não saem do compositor |
| comparação das Retificações do 91 e do 01 | integral | não reexecutada (rodada 2: sim) |
| comparação da Retificação do 92 | feita por diferença de texto (`diff` do `pdftotext -layout`): as âncoras das seções renumeradas não casam no consolidado | registrada em `editais/edital-92-2026/retificacoes.md` |
| sondagem nos editais reais | **só com os PDFs**, que não estão no repositório (públicos nos sítios do Cefor e do Ifes) | não reexecutada (rodada 2: 64%, 78%, 66%) |
| metadados dos vídeos em Libras (19, 46 e 28/2026) | páginas públicas, consultadas em 2026-10-11; não há script | — |
| atos e anexos dos reais; editais 19 e 46 | **só com os arquivos**, guardados em `editais/*/fonte/consulta-2026-10-11/` e `comparacao-focalizada/fontes/`, com SHA-256; os links podem mudar (o do 46/2026 já mudou de versão) | sim |
| mapa de seções dos vídeos | **não integral**: depende do navegador, do carregamento e dos anúncios; o método e os pontos de conferência estão em `comparacao-focalizada/videos.md`, e cada fronteira foi conferida lendo o quadro | sim |
| geração do corpus (publicação no banco) | **não byte a byte**: identificadores aleatórios de Processo e de Edital e datas relativas do `seed_demo`. A fonte de verdade são os arquivos de `editais/*/fonte/`, com os hashes dos manifestos | não reexecutada (as rodadas 2 e 3 não publicam) |
| análise jurídica (auditoria, §13) | textos do Planalto consultados em 2026-10-11; não há script | — |
