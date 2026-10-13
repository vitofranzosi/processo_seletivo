# Research: O Edital oficial em linguagem simples — lote 1

Decisões técnicas da implementação. As de produto são `D-001` a `D-005`, na spec, e aqui são premissa.
A base são três levantamentos feitos em 12/10/2026 sobre a `main` `a79ce463`:

1. **Quem lê as frases** (o inventário do FR-1398, em R-004).
2. **Como o catálogo, a estrutura publicada e a numeração funcionam.**
3. **Que testes afirmam a forma de hoje.**

## R-001 — A estrutura do documento se reconhece pela assinatura do catálogo no snapshot

**Decision**: o catálogo (`editais/domain/secoes.py`) recebe a ordem e os títulos novos, e as chaves
não mudam. O snapshot já copia `title` e `order` de cada seção do catálogo na submissão
(`publicacoes/application/publish_edital.py:72-100`), e a Retificação não pode mudá-los
(`publicacoes/domain/colecoes.py:139-149`). Por isso o snapshot registra sob qual catálogo o Edital
nasceu.

O compositor compara a assinatura do snapshot — o conjunto `(key, title, order)` das seções — com um
**registro explícito de apresentações**:

- a assinatura do catálogo novo → a **apresentação por perguntas** (`D-001`);
- qualquer outra → a **apresentação plana**, a da `068`, já com a redação, a tipografia e a navegação
  novas (`D-003`).

**Rationale**: é a única marca que já existe, que é imutável depois da publicação e que não muda o
hash de conteúdo algum já submetido. O registro é explícito, e não "igual ao catálogo atual", porque
uma mudança futura do catálogo devolveria em silêncio os Editais da `069` à forma plana. O teste
segue o precedente de `tests/integration/publicacoes/test_topologia_do_acervo.py`: publica com o
catálogo anterior e retifica.

**Alternatives considered**:

- **Elevar o `schemaVersion`** — rejeitada. `elevar` reescreve a versão na leitura
  (`publicacoes/domain/elevacao.py:338`), e o consolidado de um Edital antigo chegaria ao compositor
  marcado como novo. Também exigiria um degrau de identidade para não trancar o acervo.
- **Campo marcador no conteúdo** — rejeitada. Muda a forma do conteúdo, entra no contrato de
  mutabilidade, e a spec exclui campo novo.
- **Data da publicação original** — rejeitada. Seria uma constante de implantação, e não existe na
  prévia nem na primeira publicação.

## R-002 — Seções reunidas sob uma pergunta: uma apresentação declarada, sem mudar chaves

**Decision**: ao lado do catálogo, uma declaração `APRESENTACAO`. Cada entrada traz:

- o título apresentado — a pergunta ou o título direto;
- as chaves-membro, na ordem;
- os **lugares do conteúdo gerado** — os requisitos dos Perfis, as regras dos marcos, os dados do
  sorteio, o período, os dados declarados, o teto, o lembrete do Requerimento.

A entrada de um membro só é o título da própria seção. Membros com conteúdo saem como subseções
**N.k**, com o título que têm no catálogo: "Público-alvo", "Atendimento à pessoa com deficiência". A
materialização continua a de hoje: seção textual vazia não sai, a não ser que carregue norma do
sistema (FR-984).

**Rationale**: as chaves são a identidade do texto já escrito em rascunhos (`secoes.identidade`,
uuid5 sobre `edital_id:key`) e a topologia que a Retificação confere
(`editais/domain/validation.py:488-579`). Reunir na apresentação, e não no conteúdo, mantém o snapshot
na forma de hoje.

**Alternatives considered**:

- **Fundir chaves** ("selecao" no lugar de "classificacao" e "verificacao-autodeclaracao") — rejeitada:
  perde a identidade do texto escrito e quebra a topologia.
- **Grupo gravado no snapshot** — rejeitada: forma nova de conteúdo, pelo mesmo motivo da R-001.

## R-003 — Uma regra de numeração, consciente da apresentação, lida por todas as telas

**Decision**: `numeracao(snapshot)` passa a devolver o número **apresentado** de cada chave — `"N"` para
a seção e `"N.k"` para o membro de grupo — pela apresentação que a R-001 escolhe. Isso inclui
`numeracao_impressa`, `itens_do_documento`, `tabelas_do_documento` e `plano_de_consolidacao`. Devem
lê-la:

- o compositor;
- a etapa Conteúdo (`interface/forms.py:817-848`, com o template `compor_conteudo.html:53-58`);
- a Revisão (`interface/revisao.py:734-737`, `_secao` :431);
- a tela de Retificação (`interface/retificacao.py:1562-1585`);
- as conferências da `065` (`_secoes_impressas` :3674, `_itens_impressos` :3836).

O `conteudo.js` (`interface/static/interface/conteudo.js:27-34`), que recontava os números no
navegador, passa a ler o número do servidor. O `_DESCRICAO_DO_ITEM` ganha a natureza nova (subseção
textual): hoje uma natureza desconhecida derruba a conferência com `KeyError`.

A regra de conflito da `065` passa a comparar o **prefixo apresentado**. Um "3.1" digitado dentro da
subseção 3.1 não pode passar por coerente.

**Rationale**: "uma regra só" é a FR-985 da `054`, e o Edital antigo, composto pela apresentação plana,
tem de continuar mostrando nas telas os números do PDF dele (FR-1394, FR-1399).

**Alternatives considered**: um mapa de números à parte só para o documento — rejeitada, porque refaz
as três numerações que a `054` unificou (RC-26).

## R-004 — As frases têm versão, e o ato publicado mostra a dele

**Decision**: as frases da regra ficam versionadas por **redação**:

- a 1, de hoje, congelada;
- a 2, desta feature.

As funções públicas (`criterio_por_extenso`, `forma_de_convocacao_por_extenso`, `teto_de_inscricoes`
e as do marco que a Revisão importa) recebem a redação, e por padrão usam a vigente. A `Publicacao`
ganha a coluna `redacao_do_documento`, gravada no ato: 1 para as publicações existentes, pelo padrão
da migration, e 2 para as novas. É o mesmo molde das colunas da Unidade e do ato de nomeação, da
`060`.

O inventário, com a regra de cada leitor:

| Leitor | Exibe ato publicado? | Hoje | Com a feature |
|---|---|---|---|
| Documento do Edital e da Retificação (`DocumentoPublicado.bytes`) | sim | congelado | os bytes publicados não mudam; os novos usam a redação 2 |
| Página do ato de ordenação (`classificacao/application/selectors.py:266-289`, `ato_ordenacao.html:84-100`) | **sim** | reconstruído com o vocabulário do dia | usa a redação da `Publicacao` da versão citada (`ato.versao.source_publication`). **É o leitor que cumpre o FR-1397** |
| Proposta de ordenação (`selectors.py:391-414`, `ordenacao.html:202-205`) | não (é a versão vigente) | reconstruído | redação 2 |
| Portal: canal de convocação (`portal/situacao.py:264-272`) e teto (`portal/views.py:430`, `:2277`) | lê a versão vigente | reconstruído | redação 2 — permitido pelo FR-1397, porque descreve a mesma regra da versão aplicável |
| Revisão, Aplicar a todos, Conteúdo (`interface/revisao.py`, `aplicacao.py`, `forms.py`) | não (rascunho) | reconstruído | redação 2, a mesma do documento que vai ser composto (FR-1364) |
| Retificação, aviso de recurso da `067`, conferências da `065` (`validation.py:1654`, `:3686`, `:3843`) | sim (conteúdo retificado) | reconstruído | número pela apresentação do snapshot (R-003); frase pela redação 2, porque o consolidado sai nela |
| Divulgação de resultado, avisos (`066`), e-mails de convocação, `AtoDeOrdenacao` gravado | — | congelado ou sem frase | nenhuma frase do vocabulário dentro: inalterados |

**Cópias da mesma frase fora do vocabulário**, que mudam junto para não haver segunda redação
(FR-1364):

- os rótulos de `callForm` em `editais/models/perfis.py:88-89` — mudança de `choices`, que gera
  migration sem efeito no banco;
- `interface/retificacao.py:353-356`;
- `compor_perfis.html:135-136`, `_perfil.html:265-266` e `convocacao.html:138`.

Os rótulos de formulário da equipe ("Corte", "Continuação", "Quantos progridem") são rótulos de campo, e
não frases do ato. A FR-1366 governa só o documento, e eles ficam.

**Rationale**: o ato de ordenação não guarda texto, só identificadores e valores
(`classificacao/application/emissao.py:293-303`), mas guarda a versão que citou, e a versão leva à
Publicação. A coluna torna a redação **identificável**, e não só reconstruível por data.

**Alternatives considered**:

- **Corte por data** (`published_at` contra uma constante de implantação) — rejeitada: frágil entre
  ambientes, e a prévia não tem data.
- **Ler os bytes publicados** para descobrir a redação — rejeitada: é heurística sobre um artefato.
- **Não versionar**, e aceitar a página do ato com a redação nova — rejeitada pelo clarify.

## R-005 — O escritor do Edital se separa; comprovante e divulgação não mudam um byte

**Decision**: `render_documento`, a tabela de larguras da Helvetica, `largura` e `_quebrar` ficam como
estão para o comprovante e para a divulgação. O Edital passa a usar um **perfil de arquivo** próprio,
com:

- a fonte embutida (objetos `/TrueType` com `/FontFile2`), mantidos os nomes de recurso `F1` e `F2`;
- a medição pelas larguras dela;
- `/Info` (título e autor, **sem data**) e `/Lang`;
- `/Outlines` e anotações de link;
- sem `/ID` no trailer.

A composição recebe a **métrica** como parâmetro (`Composicao(metrica=…)`). O padrão continua a
Helvetica de hoje.

**Antes de tocar o escritor**, a feature prende os bytes do comprovante e do documento de divulgação
em fixtures novas. Hoje nenhum dos dois tem fixture, só determinismo no mesmo processo, e a página do
comprovante promete ao candidato o SHA-256 do arquivo a cada download
(`portal/templates/portal/comprovante.html:133-137`).

**Rationale**: a FR-1383, e a promessa do comprovante (FR-063a da `009`).

**Alternatives considered**: mudar a fonte de todos os documentos — rejeitada: muda o SHA-256 de todo
comprovante já emitido, que se regenera a cada download.

## R-006 — Os streams de página continuam sem compactação

**Decision**: só o arquivo da fonte é compactado, com `/Filter /FlateDecode` e `/Length1` no
dicionário. Os fluxos de página continuam com dicionário `<< /Length N >>` e texto literal
`(…) Tj` em cp1252. A caixa de fundo é desenhada no próprio fluxo, e não como Form XObject.

**Rationale**: os extratores de texto dos testes (`test_pdf.py:76-110`,
`contract/test_documento_publicado.py:94-125`, `interface/test_fluxo.py:30-47`) leem só stream de
dicionário exatamente `<< /Length N >>`. Com conteúdo compactado, eles devolvem texto vazio, e **todo
teste negativo ("não contém X") passaria sem testar nada**. Um stream novo sem `/Filter` seria contado
como página. A Helvetica se reproduz em TrueType com `/WinAnsiEncoding`, então as strings continuam de
um byte.

**Alternatives considered**: compactar tudo e reescrever os extratores — rejeitada: o ganho de tamanho
não paga o risco. Fica como guarda nova um teste que falha se o extrator devolver texto vazio para um
documento composto.

## R-007 — A fonte: Liberation Sans 2.x, OFL, em subconjunto fixo

**Decision**: Liberation Sans **2.1.x**, Regular e Bold, do release oficial do projeto
`liberation-fonts`, sob a **SIL Open Font License 1.1**.

- O subconjunto cobre os caracteres WinAnsi que a grafia do Edital admite. É gerado **uma vez** por um
  roteiro de desenvolvimento, `uv run --with fonttools`, sem `fontTools` como dependência do produto.
- O subconjunto é versionado no repositório, junto do texto da licença e do resumo SHA-256 do arquivo
  de origem.
- Um teste confere que o subconjunto cobre todo caractere que `grafia` aceita.

**Determinismo**: o roteiro salva com `recalcTimestamp=False`, sem o qual cada execução muda a data do
`head` e os bytes. O próprio subconjunto é um arquivo fixo, então os bytes do documento não dependem
de ferramenta.

**Rationale**:

- A licença é a pedida pelo 4º. A amostra usou a 1.07.4, de licença GPL com exceção para fontes; a 2.x
  é OFL, mais simples de distribuir.
- As métricas são as da Arial e da Helvetica nos caracteres que o compositor conhece. A amostra mediu:
  as únicas divergências estão onde o `pdf.py` estava errado ("í", "ì", "î", "ï", "ª", "º", hífen
  suave).
- Embutida, a fonte acaba com a substituição do negrito no poppler (o ED-14 da auditoria).

**O download** do arquivo de origem é uma tarefa com aprovação explícita do usuário.

**Alternatives considered**:

- **Arimo** — métricas iguais, Apache 2.0. Fica como reserva se a Liberation 2.x não estiver
  disponível.
- **DejaVu Sans** — métricas diferentes: a quebra de linha mudaria de natureza.
- **Manter a Helvetica não embutida** — o defeito que a terceira rodada pediu para corrigir.

## R-008 — As frases: uma tabela por variante, com a equivalência escrita

**Decision**: o contrato [`contracts/redacao.md`](contracts/redacao.md) lista **toda** variante que o
compositor conhece, com a frase de hoje, a frase nova e a nota de equivalência:

- forma da ordem, combinação, normalização, arredondamento;
- habilitação, corte, empate, continuação, suplentes;
- os três tipos de desempate, cada um com os dois tipos de dado e as duas ausências;
- recurso admitido e vedado;
- método comum, próprio e divergente;
- reversão, convocação, teto, Requerimento, Etapas, grupos de documentos, dados declarados;
- integridade.

Um teste por variante prende a frase nova. A conferência por enunciado da entrega (FR-1396) é feita
sobre o texto final, no molde do `equivalencia.md` da amostra.

**Rationale**: a FR-1361 pede a equivalência por variante. A amostra cobriu as variantes de A e B e
errou três vezes — a condição acrescentada, a frase falsa com cadastro, a unidade partida —, e por isso
a tabela é escrita antes do código.

**T1 e T2 (desempate por data) usam sempre a forma genérica** "«f» mais antiga/recente, informada na
inscrição". A primeira versão deste contrato derivava "maior idade" comparando o rótulo do fato com
"Data de nascimento"; a análise apontou a inferência, e o usuário decidiu pela forma genérica (D-006).

## R-009 — Agrupamento: identidade dos itens compostos, com unidades e partilha parcial

**Decision**: a regra de identidade da `068`, que compara os itens que a composição escreveria, ganha
três coisas:

- **unidades indivisíveis** — o corte com empate, suplentes e continuação; os critérios de desempate de
  um marco;
- **partilha parcial** — o comum a todos os grupos sai uma vez, depois o próprio de cada grupo, e uma
  unidade que difere sai inteira em cada grupo;
- **faixa de códigos** — só quando os códigos são contíguos, com o mesmo prefixo e a mesma largura
  numérica.

Os Perfis de mesmo nome saem numa tabela própria. Os atributos iguais em todos os Perfis saem numa
frase.

**Rationale**: o achado 3 da conferência da amostra ("esse número" sem o número) e a FR-1375.

## R-010 — O resumo: só dado, com as palavras do 5º

**Decision**:

- **Vagas:** "N vagas em K localidades: …" quando todos os Perfis têm vaga imediata. Os nomes saem
  quando são até 5 localidades distintas; acima disso, só a contagem.
- **Sem vaga imediata em parte dos Perfis:** as vagas imediatas e os códigos desses Perfis, e "os
  demais formam cadastro de reserva".
- **"Cadastro de reserva":** por extenso — "não há", "até N classificados por Perfil" ou "sem limite".
- **Seleção:** pela forma ("sorteio eletrônico" ou "pontuação") e pelas Etapas. Uma Etapa sai pelo nome
  quando o nome é **curto** — até 40 caracteres, sem vírgula nem travessão —; senão, pela natureza:
  "uma etapa classificatória", "uma etapa eliminatória".

Exemplos: em A, "sorteio eletrônico, com Análise documental"; em B, "pontuação em uma etapa
classificatória, com uma etapa eliminatória".

**Rationale**: o 5º, sem campo novo. Os limites são do plano, e não da spec.

## R-011 — Paginação: regras objetivas, limites como parâmetros

**Decision**: as regras da FR-1389 à FR-1392, com os limites como constantes nomeadas do compositor:

| Regra | Parâmetro |
|---|---|
| Título nunca termina a página | o `junto` de hoje, estendido a subseções, rótulos de grupo e legendas |
| Linha de tabela nunca se parte | a de hoje |
| Cabeçalho repetido | o de hoje |
| Tabela que cabe numa página não deixa uma linha só na seguinte | tabela até 60% da área útil é coesa; acima disso, no mínimo 2 linhas de cada lado da quebra |
| Bloco relacionado junto | até 45% da área útil; acima disso, divide-se entre parágrafos, itens ou linhas |
| Item de lista inteiro | salvo se maior que a área útil |
| Última seção com o fecho | sempre que couberem juntas numa página |
| Equilíbrio | se manter um bloco junto deixa mais de 50% da área útil em branco e o bloco pode ser dividido, divide-se |

**Rationale**: o 6º. Os limites vieram da amostra e se calibram nos cenários A, B e na variante, com o
SC-521 como medida. A primeira página quase vazia de A e a última com pouco conteúdo são os casos que
a regra de equilíbrio corrige.

## R-012 — Navegação e arquivo

**Decision**:

- **`/Info`:** `/Title` com o anúncio do ato em caixa mista ("Edital nº 91/2026 — …") e
  `/Author` "Ifes — <sigla da Unidade>". Sem data, para manter o determinismo.
- **Visualização:** `/Lang (pt-BR)`, `/ViewerPreferences << /DisplayDocTitle true >>` e
  `/PageMode /UseOutlines`.
- **Marcadores:** das seções e subseções, pela mesma lista de itens que numera o documento.
- **Links:** do sumário para a seção; do e-mail (`mailto:`) e dos endereços `http(s)` que o texto
  impresso contém. Nenhum endereço é acrescentado.
- **Sumário:** composto em duas passadas — a primeira descobre as páginas, a segunda as imprime. Se o
  sumário mudar a paginação, uma terceira passada converge, e o teste confere.
- **Download:** `Content-Disposition: inline` com `edital-<número>-<ano>.pdf`; no consolidado,
  `edital-<número>-<ano>-retificado-<AAAA-MM-DD>.pdf`, com a data de `Publicacao.published_at` no fuso
  institucional (FR-1387).

## R-013 — O aviso de remissão textual (FR-1400)

**Decision**:

- **Leitor:** um leitor puro em `editais/domain/numeracao_digitada.py`, que acha citações de seção por
  título — "na seção X", "no item X", título entre aspas ou em caixa alta.
- **Destinos:** um mapa congelado dos títulos do catálogo anterior para os destinos novos, marcando os
  repartidos — `perfis` → vagas, requisitos e seleção.
- **Validação:** `_remissao_a_secao_pelo_titulo`, só no ato de publicação, com `Severity.WARNING` e
  código novo, apontando para `/sections/id=…/content`, chamada junto das conferências da `065`.
- **Telas:** o código entra em `CODIGOS_DO_TEXTO_DA_SECAO` e no conjunto de âncoras de
  `interface/views.py`.

Destino único sugere a seção; destino repartido diz que há dúvida e lista os destinos.

## R-014 — Os testes que mudam, e como

**Decision**, pelas regras que os próprios testes escrevem:

- **A fixture de contrato** `documento_publicado_v1.pdf` se regenera nesta entrega, que muda a
  composição de propósito, com o diff revisado (docstring de `test_documento_publicado.py`).
- **Os bytes esperados dos cenários da auditoria** passam de `specs/068-…/demonstracao/` para
  `specs/069-…/demonstracao/`. Os anteriores ficam como evidência. Nasce
  `test_documento_da_auditoria_depois_da_069.py`, que prende o que mudou e só isso.
- **Os testes de equivalência e de texto da 067 e da 068** que reconstroem frases pelo caminho de hoje
  passam a usar a redação 1 explicitamente: eles provam a história, e a redação 1 continua existindo.
- **As asserções sobre frases** (cerca de 120 a 160 em 18 arquivos de PDF, cerca de 20 na Revisão, no
  portal e na página do ato) passam a afirmar a frase nova **com a mesma força**. Nunca se afrouxa uma
  asserção, e cada caso fica em `verificacao.md`.
- **Auxiliares que a forma nova quebra sem defeito de produto:**
  - a contagem `texto.count("EDITAL") == 1` (`test_pdf.py:633`), que o resumo e o `/Title` afetam;
  - a busca de `b"Do"` no fluxo das páginas 2 em diante (`test_pdf.py:1500`), que um título em caixa
    mista ("Dos …") dispara;
  - as buscas por título no texto, que o sumário duplica — passam a procurar a partir do fim do
    sumário;
  - `_titulos_numerados` (`test_catalogo_da_054.py`), que filtrava pela caixa alta;
  - o literal `"F2"` (`test_pdf.py:642`), que se mantém porque os nomes de recurso se mantêm.
- **Testes de largura** recebem a métrica do documento que medem: Helvetica para o comprovante, a fonte
  embutida para o Edital.
- **Edital de um Perfil:** a fixture de contrato tem um Perfil, e muda com a feature, porque a redação e
  a tipografia mudam também para ele.

## R-015 — Migrations

**Decision**:

- `publicacoes/0011` — a coluna `redacao_do_documento` em `Publicacao`, `PositiveSmallIntegerField`,
  padrão 1. A tabela é append-only (gatilho e privilégio); acrescentar coluna com padrão não é UPDATE,
  como na `0010` da `060`.
- `editais/00NN` — o `AlterField` dos rótulos de `callForm`, sem efeito no banco.

O guardião de contagem de migrations da `022` recebe as duas justificativas.

## R-016 — Retificação de Edital publicado antes: plana, com a redação nova

**Decision**: o consolidado de um Edital cuja assinatura de catálogo não é a da `069` usa a
**apresentação plana** (R-001), com a redação 2 — inclusive os rótulos gerados G1–G3, "Regras de
classificação" no lugar de "Marcos classificatórios", com o mesmo número e o mesmo destino (D-007) —, a
tipografia e a navegação. Ficam como no original:

- a ordem, os títulos e a numeração;
- a seção de Perfis com marcos, recurso e convocação no lugar de hoje;
- sem resumo.

O sumário entra, porque é navegação e não muda numeração nem remissão.

**Rationale**: `D-003` e o clarify: "melhorias compatíveis com a sua estrutura". O sumário não move
nada, e por isso é compatível.

**Alternatives considered**: sem sumário no consolidado antigo — também compatível, mas tira do
candidato a navegação sem razão. Fica registrado, se o usuário preferir.
