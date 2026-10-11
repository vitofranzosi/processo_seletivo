# Editais em Libras — corpus, catálogo, narrativas e roteiros

Estudo documental para responder a uma pergunta: **existe recorrência suficiente, com unidades
semanticamente reutilizáveis, para justificar uma biblioteca audiovisual de Libras integrada ao sistema
de processo seletivo?**

A inspiração são os sistemas de narração esportiva, que recompõem apresentações novas a partir de trechos
gravados. A diferença é a língua: Libras tem estrutura própria, espacial, com expressões não manuais, e não
se monta concatenando sinais. Por isso o estudo trabalha em duas camadas — um **inventário** de unidades
semânticas, para cobertura e rastreabilidade, e **narrativas** por situação do candidato, para preparar a
tradução —, e todo reaproveitamento depende de validação por profissional de Libras.

> **Estado:** rodada 4, 2026-10-11 (consolidação). **Nenhuma tradução foi produzida nem avaliada** pelo estudo.
> Nenhuma unidade tem vídeo, tradutor responsável ou validação. Nada foi implementado no sistema. Cinco editais
> inventariados — três **simulados**, publicados pelo sistema, e dois **reais**, do Cefor (28/2026 e 59/2026) —, e dois
> editais técnicos do Ifes (19/2026 e 46/2026) numa **comparação focalizada**, sem inventário integral. Três vídeos
> institucionais em Libras foram observados só no que mostram por escrito — o rótulo de seção na tela —, sem avaliação
> da tradução.
>
> **Três estados que o estudo não confunde:** *cobertura documental* (toda linha de cada edital inventariado está na
> matriz), *narrativa preparada* (protótipo, sem validação) e *tradução validada* (nenhuma). O estudo focalizado não
> substitui a tradução integral do edital e das retificações, onde ela é exigida.

## Leia nesta ordem

| Documento | Para quê |
|---|---|
| [`viabilidade.md`](viabilidade.md) | a resposta à pergunta: métricas de coincidência literal (com o que medem e o que não medem), as versões reais reconstruídas, os três níveis de reaproveitamento, o piloto e a próxima rodada |
| [`comparacao-focalizada/`](comparacao-focalizada/README.md) | Eliminação e Inscrição comparadas por situação comunicativa (19, 46, 28 e 59/2026), o mapa de seções dos vídeos e o protocolo para os profissionais de Libras |
| [`camada-comunicativa.md`](camada-comunicativa.md) | o modelo das narrativas, os quinze protótipos, um exemplo completo de antes e depois e as pendências para validação humana |
| [`auditoria-sistema.md`](auditoria-sistema.md) | de onde vem cada parte do texto de um edital, no código; e o contexto legal por tipo de certame (§13) |
| [`catalogo/indice.md`](catalogo/indice.md) | as unidades, por família, com classificação, ocorrências por edital e os desdobramentos da rodada 2 |
| [`catalogo/terminologia.md`](catalogo/terminologia.md) | os termos que pedem decisão de sinal antes de qualquer gravação |
| [`metodo-incremental.md`](metodo-incremental.md) | como incorporar um edital novo — do sistema ou escrito fora dele —, e uma Retificação, sem refazer o catálogo |
| [`ferramentas/`](ferramentas/README.md) | os scripts que sustentam a cobertura e as medições, e o que deles se reproduz |
| `historico/` | as análises de viabilidade das rodadas [1](historico/viabilidade-rodada-1.md), [2](historico/viabilidade-rodada-2.md) e [3](historico/viabilidade-rodada-3.md), preservadas, e o [histórico das alterações da rodada 4](historico/alteracoes-rodada-4.md), com as pendências e os responsáveis |

## Os editais

| Pacote | Edital | Tipo de certame | Configuração | Versões |
|---|---|---|---|---|
| [`edital-91-2026/`](editais/edital-91-2026/manifesto.md) | 91/2026 — Pós-graduação EaD | ingresso em curso (LBI, art. 30) | 4 polos, cotas, sorteio, 13 seções textuais | original + 1 Retificação |
| [`edital-92-2026/`](editais/edital-92-2026/manifesto.md) | 92/2026 — Tutores UAB | seleção de bolsistas | 18 Perfis, cadastro de reserva, prova de títulos, numeração digitada | original + 1 Retificação |
| [`edital-01-2026/`](editais/edital-01-2026/manifesto.md) | 01/2026 — Professor e técnico (`seed_demo`) | contratação de professor substituto e técnico | 2 Perfis, duas Etapas pontuadas, sem seções textuais | original + 2 Retificações (uma com vigência futura) |
| [`edital-28-2026/`](editais/edital-28-2026/manifesto.md) | **28/2026 — Pós-graduação em Informática na Educação, EaD (real)** | ingresso em curso (LBI, art. 30) | 7 polos, cotas, sorteio, heteroidentificação, 6 anexos no PDF; **vídeo em Libras do Cefor** | consolidada inventariada; Retificação nº 01 e Comunicado reconstruídos — a consolidada **não traz** a Retificação de vagas |
| [`edital-59-2026/`](editais/edital-59-2026/manifesto.md) | **59/2026 — Curso FIC de Libras A1, presencial (real)** | ingresso em curso | 2 turmas, sem reserva, sorteio, 1 anexo no PDF | consolidada inventariada; Retificação e Comunicado reconstruídos — a consolidada **não traz** o início retificado |

Os três primeiros são **simulados** (marcados como tal em todo arquivo); os dois últimos, **reais**.

> **Atenção à numeração.** O número do 91/2026 simulado é o de um ato real do Cefor, de outro objeto: o Edital
> 91/2026 real seleciona professores regentes para os cursos da UAB. O pacote simulado não tem relação com ele.
> Os números dos simulados foram escolhidos pela auditoria do PDF e podem colidir com outros atos reais; citá-los
> sempre com “(simulado)”.

Cada pacote tem `manifesto.md` (identificação, versões, contexto legal), `cobertura.md` (o mapa integral),
`roteiro-producao.md` (o documento de trabalho, na ordem do edital), `oportunidades-reuso.md`,
`retificacoes.md`, `narrativas/` (as três narrativas e o mapa da cobertura por intenção) e `fonte/` (os
PDFs publicados e o conteúdo canônico de cada versão).

## Rodada 4: o que mudou

Rodada curta de consolidação, depois de uma revisão das conclusões e das narrativas. Sem ampliar o catálogo.

- **Fidelidade:** o texto em imagem passou a ter três registros separados — transcrição fiel (linha a linha, conferida
  contra a página renderizada), normalização usada na comparação e avaliação de equivalência. As notas de localização
  estavam erradas; o cabeçalho em imagem da página 9 do 59/2026 não tinha linha e passou a ter (E59-090a). A rodada 3
  ajustara a transcrição para casar com o cabeçalho do sistema; o ajuste está registrado.
- **Métricas:** a medida “idêntico a simulado” comparava os reais com **todo** o texto simulado, dentro da unidade; a
  atribuição foi corrigida, e há uma medida nova, restrita às frases que o sistema gera, com conjunto, denominador e
  limites explícitos. Nenhuma conclusão sobre tradução ou gravação sai delas.
- **Conclusões:** retiradas as frases que excediam as métricas ([`viabilidade.md`](viabilidade.md)).
- **Versões:** baixados, com autorização, os atos e anexos do 28 e do 59, com origem, data e hash. A versão consolidada
  de cada um **não é a soma dos atos**.
- **Narrativas:** as pendências passaram aos enunciados e às respostas esperadas; cada pergunta tem estado (21
  definitivas, 13 com pendência).
- **Comparação focalizada:** Eliminação e Inscrição, por situação comunicativa, com os editais técnicos 19/2026 e
  46/2026 e os seus vídeos, e o protocolo para a análise profissional — com uma condição que testa gravações de blocos
  de mesmo sentido escritos de outro modo.

## Rodada 3: o que mudou

- **Dois editais reais** do Cefor inventariados por inteiro, com os anexos que estão no PDF: 207 e 107 linhas de
  cobertura, 162 unidades novas (LIB-0155 a LIB-0316) e uma família nova, **ANX** (formulários, declarações e
  termos). Nenhum dado pessoal: os anexos são campos em branco.
- **O texto do sistema não reaparece no texto real**: 0% e 1% das palavras com texto idêntico, mesmo no 28/2026, em
  que a simulação do 91/2026 foi calibrada. 21 unidades anteriores passaram a `SEMELHANTE` ou `PARAMETRIZÁVEL`.
- **O texto da casa se repete**: 30% das palavras do 59/2026 estão em linhas idênticas às do 28/2026 (40% sem contar
  caixa e pontuação).
- **Seis narrativas reais**, com 85 enunciados, 30 ambiguidades — 13 delas defeitos do texto oficial, registrados
  sem correção — e 33 perguntas de verificação.
- **Uma tradução institucional existe**: o vídeo do 28/2026 (75 min, 05/05/2026), anterior à Retificação e ao
  Comunicado. Registrados os metadados; o vídeo não foi assistido.
- **Os atos de Retificação reais não foram lidos**: baixá-los pede autorização (lista em
  [`viabilidade.md`](viabilidade.md), §10).

## Rodada 2: o que mudou

A revisão crítica da rodada 1 mostrou que a decomposição e os roteiros eram guiados demais pela forma do
documento em português. A rodada 2:

- **corrigiu o catálogo**: 12 unidades desdobradas por agruparem regras diferentes (destinatário,
  modalidade, condição ou consequência), 3 regras embutidas em descrições de Evento ganharam unidade, 6
  diferenças só de redação passaram a equivalências a confirmar, orientações que decidiam a solução
  linguística foram retiradas, e as variáveis passaram a ser de **valor** ou de **condição**. Os
  identificadores foram preservados; cada correção está no histórico da unidade;
- **verificou as fontes legais** e registrou o contexto por tipo de certame, distinguindo ausência de
  cláusula, proibição expressa e direito previsto fora do edital;
- **criou a camada comunicativa**: três narrativas por edital (inscrição válida, classificação e
  progressão, contestar cada decisão), com 86 enunciados, 35 ambiguidades para a área e 44 perguntas de
  verificação;
- **recalculou as métricas**, com os valores da versão 1 identificados, e separou o reaproveitamento em
  roteiro, solução tradutória e gravação;
- **versionou os scripts** e documentou o que deles se reproduz.

## Convenções

- **Fato, Hipótese, Lacuna** nos documentos de análise.
- **Unidade documental não é vídeo**, e **narrativa não é tradução**: as duas camadas preparam o trabalho do
  profissional de Libras; não o substituem nem decidem por ele.
- **Marcas da simulação não se traduzem** (“(DEMONSTRAÇÃO)”, “[DOCUMENTO DE DEMONSTRAÇÃO …]”, “(fictícia)”).
- **Origem do texto** (A gerada, B estruturada, C frase do sistema, D redação livre, E outra entidade) segue a
  auditoria do PDF de 08/10/2026 (`doc/auditoria-edital-pdf-2026-10-08.md`, §3.2).

## Como a cobertura foi construída

1. Os três editais simulados foram publicados na rodada 1 pelo fluxo real (`create_process_with_first_edital` →
   `replace_draft` → `submit_edital` → `homologate_edital` → `publish_edital`, e `create_retification` →
   `publish_retification`), num banco isolado, a partir do commit `bbc8e04c`.
2. Os bytes de cada `DocumentoPublicado` e o conteúdo canônico de cada `Publicacao` estão em `fonte/`. O
   SHA-256 do conteúdo confere com o que cada PDF imprime. Dos editais reais, `fonte/` guarda o PDF publicado pelo
   Cefor, identificado pelo SHA-256 do arquivo.
3. O texto de cada PDF é cortado em trechos consecutivos por âncoras, e a concatenação é conferida contra o
   texto inteiro: **nenhum caractere fica fora da matriz**. Os rodapés têm linha própria; o texto que o PDF só tem
   em imagem (o cabeçalho dos editais reais) entra transcrito, em linha marcada.
4. Cada trecho tem uma unidade (e, se contém outra regra, unidades adicionais); a situação de cada
   ocorrência é calculada na ordem 91 → 92 → 01 → 28 → 59, e a coerência entre classificação e corpus é conferida.
5. As narrativas citam linhas de cobertura, e toda linha do edital fica ligada a ao menos uma intenção.

Tudo se regenera com os scripts de [`ferramentas/`](ferramentas/README.md).

## Restrições desta rodada

Não se implementou funcionalidade, não se alterou modelo, API, interface ou gerador de PDF, não se criou
migration nem dependência do sistema, não se produziram novas publicações no banco, não se usou IA de
tradução nem avatar, não se acessou dado pessoal de candidato e nenhum edital oficial foi modificado: os PDFs
reais em `fonte/` são cópias sem alteração, e os seus defeitos estão registrados, não corrigidos. Na rodada 3, nenhum documento foi baixado; na rodada 4, com autorização, os atos, anexos e editais listados em
`editais/*/retificacoes.md` e em [`comparacao-focalizada/fontes.md`](comparacao-focalizada/fontes.md), todos públicos.
Nenhum vídeo foi baixado, recortado ou republicado.
