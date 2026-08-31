# Fase 0 — Pesquisa e decisões

**Feature**: 008 — Composição Institucional do Edital | **Data**: 2026-08-30

Nenhum `NEEDS CLARIFICATION` restou: as seis decisões que seriam arquiteturais escondidas foram
fechadas **como limite** na spec, antes deste plano, e aparecem aqui **como decisão**, com a
alternativa recusada. É a divisão que a Constituição pede: a spec diz o resultado e o limite, o
plano diz como.

Todo o desenho abaixo cabe em um arquivo de produção, `publicacoes/infrastructure/pdf.py`.

## O ponto de partida — a reconciliação que originou as decisões

*Esta descrição estava na spec e foi movida para cá: é evidência técnica, e a Constituição manda que
a spec fique com resultado e limite. Ela é o que torna cada decisão abaixo contestável com o código
na mão.*

O compositor é artesanal e não tem dependência externa. Ele emite **exclusivamente** operadores de
texto (`BT … Tj ET`), quebra linha contando **caracteres** (`_quebrar`, com um fator médio de largura
de `0,52`), pagina uma lista **plana** de linhas independentes (`Composicao.paginar`) e é função pura
de `(snapshot, content_hash, modo)`.

Disso decorre por que cada fronteira da spec precisou ser escrita:

| Fronteira na spec | O que o compositor não tinha | Decisão |
|---|---|---|
| FR-002 — texto posicionado por largura real | métrica de fonte | D-001 |
| FR-003 — bloco delimitado, colunas separadas | qualquer primitiva gráfica | D-002, D-003 |
| FR-004 — quebra respeita fronteiras do conteúdo | noção de bloco | D-004 |
| FR-034, FR-035 — autoridade no publicado | canal para metadado do ato | D-005 |
| FR-042 — prévia não altera as quebras | marca fora do fluxo | D-011 |

E a autoridade signatária, concretamente: `signatory_name` e `signatory_role` vivem em `Publicacao`,
não no snapshot; o documento é composto **antes** de a `Publicacao` existir; e os dois chamadores já
têm o `signatory` em mãos nesse ponto.

---

## D-001 — Como o compositor passa a medir texto

**Decisão**: uma tabela de larguras declarada em código, indexada pelo **byte cp1252**, para
Helvetica e Helvetica-Bold, em milésimos de em. A largura de uma cadeia é a soma das larguras dos
seus bytes multiplicada pelo corpo tipográfico.

**Racional**: o compositor já codifica todo texto em cp1252 antes de escrevê-lo (`_texto_pdf`),
porque as fontes são declaradas com `WinAnsiEncoding`. Indexar a tabela pelo mesmo byte que já vai
para o fluxo elimina a única fonte de erro possível — medir um caractere e imprimir outro. As
larguras são as métricas AFM padrão das fontes base-14, que são fixas e não dependem de instalação:
é a mesma razão pela qual o documento pode declarar Helvetica sem embutir arquivo de fonte.

**Verificação obrigatória**: um teste que afirma larguras de referência de alguns glifos e que
compõe a linha mais larga possível do cenário-base conferindo que ela não ultrapassa a margem. Sem
esse teste, a tabela é um bloco de números que ninguém sabe se está certo.

**Alternativas recusadas**:

- *Manter o fator médio de 0,52 (`FATOR_LARGURA`) e contar caracteres.* É o defeito, não a solução:
  não permite centralizar, alinhar coluna nem alinhar número, e FR-002 existe por causa disso.
- *Adicionar `reportlab` ou `fontTools` só para ler métricas.* Vedado por FR-005, e desproporcional:
  traria dependência, superfície e — no caso do `reportlab` — a tentação de trocar o compositor
  inteiro, perdendo o controle byte a byte de que a fixture contratual depende.
- *Ler um arquivo `.afm` em tempo de execução.* Acrescenta arquivo a versionar, I/O no caminho de
  publicação e uma forma nova de o documento variar por ambiente. A tabela declarada é o mesmo
  padrão dos catálogos de seções e de autoridades: dado fixo, versionado, revisável em diff.
- *Embutir uma fonte TrueType para ter métricas exatas de qualquer glifo.* FR-002 proíbe, e não há
  requisito que exija glifo fora do cp1252.

---

## D-002 — Como o fio e o contorno entram no fluxo da página

**Decisão**: o item de composição deixa de ser sempre texto e passa a ser união marcada — `Texto` ou
`Traço`. `_fluxo_da_pagina` emite **primeiro** os traços da página, depois os textos.

**Racional**: são operadores diferentes do fluxo PDF, e a ordem importa — o que é emitido depois
cobre o que veio antes. Emitir fio antes de letra garante que nenhum contorno passe por cima de um
glifo, sem precisar de camada, z-index ou qualquer conceito de composição gráfica.

A espessura do fio é constante e única no documento. Não há estilo de linha, cor, tracejado nem
canto arredondado — FR-003 restringe o vocabulário a texto, fio e contorno, e um único fio basta
para quadro de Perfil, separador de tabela e régua de cabeçalho.

**Alternativas recusadas**:

- *Desenhar quadro com caracteres.* Produziria o resultado que os Editais reais não têm e que a
  feature existe para eliminar.
- *Um segundo fluxo de conteúdo por página, só para gráficos.* O PDF permite, mas duplica objeto,
  deslocamento e contagem no `xref` para nada: um fluxo por página já aceita os dois tipos de
  operador.

---

## D-003 — Quando a moldura de um bloco é calculada

**Decisão**: a moldura é **resolvida depois da paginação**, na mesma passada que já converte linhas
em coordenadas. O bloco declara que quer moldura; o compositor observa a primeira e a última linha
daquele bloco **naquela página** e emite o retângulo a partir delas.

**Racional**: a altura de um quadro de Perfil só existe depois que as suas linhas foram colocadas —
ela depende de quantas linhas o texto refluiu, e isso depende de D-001. Calcular a altura antes
significaria medir duas vezes e aceitar que as duas medidas divirjam por arredondamento, que é
exatamente como se produz um quadro desalinhado do conteúdo.

**Consequência declarada**: um bloco que atravessa a quebra de página recebe **uma moldura por
página**, cada uma delimitando o trecho presente naquela página. É o comportamento correto e é o que
os Editais reais fazem quando um quadro continua na página seguinte.

**Alternativa recusada**: *medir a altura do bloco antes e desenhar a moldura junto com a primeira
linha.* Duplica a medição, desalinha por arredondamento e obriga o desenho a antecipar a quebra.

---

## D-004 — Como a paginação passa a enxergar blocos

**Decisão**: a composição ganha **abertura e fechamento de bloco**, com um nível de aninhamento que
reflete a cascata de FR-021: Perfil → sub-bloco → unidade interna. A paginação passa a duas
passadas: mede a altura do bloco aberto e decide se ele cabe no espaço restante antes de começar a
colocá-lo.

A regra de decisão desce a cascata e para na primeira alternativa exequível:

1. o bloco inteiro cabe no espaço restante → coloca;
2. não cabe, mas cabe em uma página inteira → começa na próxima página;
3. não cabe em uma página inteira → abre o bloco e repete a decisão para cada sub-bloco;
4. um sub-bloco isolado não cabe em uma página inteira → repete para suas unidades internas —
   parágrafo, item de lista, linha de tabela;
5. uma unidade interna isolada não cabe em uma página inteira → quebra entre linhas.

**Racional**: cada nível da cascata é o mesmo teste aplicado a um bloco menor, o que mantém a regra
uniforme. E o passo 5 é o que a torna **sempre exequível** — foi a ausência dele que tornou a
primeira redação da spec impossível de cumprir.

**Isto é um algoritmo de layout, e chamá-lo de outra coisa esconderia risco.** Ele é estreito por
construção — cinco regras de quebra, três níveis, nenhuma restrição declarativa, nenhum motor de
caixas —, mas medição, duas passadas, aninhamento, linha de tabela fragmentável, repetição de
cabeçalho e moldura por continuação interagem entre si. As interações que as tarefas precisam cobrir
explicitamente:

| Interação | Onde falha silenciosamente |
|---|---|
| Medir com uma métrica e colocar com outra | linha estoura a margem só em texto acentuado |
| Bloco que cabe medido e não cabe colocado | erro de acumulação de `antes` entre sub-blocos |
| Cabeçalho de tabela repetido conta como altura na medição do resto | tabela entra em laço de quebra |
| Moldura por continuação sobre bloco que termina exatamente na quebra | retângulo de altura zero na página seguinte |
| Cascata sobre bloco vazio | recursão sem progresso |
| Unidade interna maior que a página **e** indivisível | passo 5 é a saída; sem ele, laço |

Cada uma vira teste antes de virar código.

**Alternativas recusadas**:

- *Marcar linhas com um rótulo "não separar da próxima" e paginar em uma passada.* Resolve título
  órfão (FR-030) e não resolve "o Perfil inteiro cabe na página seguinte" (FR-020), porque decidir
  isso exige conhecer a altura total antes de começar.
- *Motor de layout genérico com caixas, fluxos e restrições.* É precisamente o que FR-004 proíbe, e
  cinco regras de quebra não justificam.

---

## D-005 — Como a autoridade chega ao compositor

**Decisão**: um valor congelado chamado `AutoridadeSignataria`, com **nome e cargo**, recebido como
parâmetro nomeado do renderizador, separado do snapshot.

*O nome importa. `Assinatura` — que era como este documento o chamava — descreveria um mecanismo
que a feature explicitamente não constrói (FR-037: sem certificado, sem imagem, sem ICP), e
colidiria com a linguagem ubíqua. `Autoridade Signatária` é o termo que a Constituição já usa para
exatamente isto: quem praticou o ato, com nome e cargo.* A presença é validada **pelo modo**: publicado exige e recusa se
faltar; prévia recusa se for oferecida.

**Racional**: é a única forma possível, e o código decide sozinho. Nos dois fluxos de publicação o
documento é composto **antes** de a `Publicacao` existir — `publish_edital.py:364` e
`retificacoes.py:580` chamam o renderizador e só depois executam `Publicacao.objects.create` —,
então o compositor não tem o que consultar mesmo que quisesse. Os dois já têm o `signatory` em mãos
nesse ponto: o custo da decisão é passar um argumento.

Validar pelo modo, e não confiar no chamador, é o mesmo desenho que a `007` deu ao hash da prévia,
pela mesma razão registrada lá: *"se a garantia dependesse de o chamador lembrar de esvaziá-lo, ela
estaria com quem não a tem"*. Aqui a consequência de esquecer seria pior — um ato administrativo
publicado sem quem o praticou.

**Alternativas recusadas**:

- *Pôr a autoridade no snapshot.* Viola FR-001 e FR-034, muda `SCHEMA_VERSION`, muda o hash, torna
  Editais publicados irretificáveis e faz a Retificação poder endereçar quem assinou. Um custo
  enorme por um bloco de duas linhas no rodapé do documento.
- *O compositor consultar a `Publicacao`.* Impossível pela ordem de criação, e quebraria a pureza
  que `test_o_snapshot_basta_para_compor_o_documento` guarda.
- *Um segundo renderizador para o publicado.* Viola FR-041 e recria a divergência silenciosa que o
  parâmetro de modo existe para impedir.
- *Parâmetro opcional sem validação por modo.* Era a primeira redação, e admitia publicar sem
  autoridade. A opcionalidade do argumento na interface interna não é a mesma coisa que a
  opcionalidade da informação no documento.

---

## D-006 — Onde a numeração das seções é atribuída

**Decisão**: a composição das seções passa a ter dois passos — primeiro seleciona a lista das seções
que **serão** materializadas, depois enumera essa lista. As subseções numeram a partir do índice da
seção-mãe já resolvido.

**Racional**: o compositor já suprime seção gerada cuja coleção está vazia. Numerar durante a
iteração produziria `5.`, `7.`, `8.` num Edital sem Etapas de Avaliação — um defeito que **não
aparece no cenário-base**, porque ele tem tudo preenchido, e que só se manifestaria no primeiro
Edital real incompleto. Por isso FR-011 é explícito e por isso o teste é obrigatório.

**Alternativa recusada**: *numerar no catálogo de seções.* Poria numeração de apresentação no
domínio, violaria FR-012 e faria o número sobreviver à supressão.

---

## D-007 — Como as colunas de uma tabela recebem largura

**Decisão**: largura medida a partir do conteúdo (D-001), com mínimo por coluna, e a folga
distribuída na coluna de texto livre. Célula que ainda assim não couber quebra em mais de uma linha
e a linha da tabela cresce.

**Racional**: proporção fixa quebra no primeiro dado real — uma localidade longa ou um fundamento
normativo por extenso estoura a coluna ou deixa metade da página vazia.

**Esta decisão não introduz capacidade nova.** Ela é aplicação direta de FR-002, já entregue em
D-001: medir uma célula é a mesma operação de medir uma linha. Por isso a tabela de ordem de entrega
da spec não registra capacidade nova na entrega 3 — não há nenhuma.

**Alternativas recusadas**:

- *Proporções fixas por tipo de tabela.* Frágil exatamente onde o documento é institucional.
- *Medir só o cabeçalho.* O cabeçalho é a cadeia mais curta da coluna quase sempre.
- *Truncar com reticências.* Um Edital não pode omitir parte de um fundamento normativo por motivo
  de largura.

---

## D-008 — De onde vem o cabeçalho institucional

**Decisão**: órgão, instituição e unidade são **constantes do compositor**; ato, Processo e título
vêm do snapshot. A centralização usa D-001.

**Racional**: a unidade já é constante hoje, escrita em linha única — a mudança é de forma, não de
origem. E o snapshot passou a carregar `processoCode` e `processoTitle` na `007` exatamente para que
o documento possa nomear o Processo sem UUID; o cabeçalho é o segundo consumidor desse campo.

**Alternativas recusadas**:

- *Unidade configurável por Processo.* Fora de escopo, e criaria dado de domínio por motivo visual.
- *Brasão como imagem.* FR-008 põe fora da V1: exigiria XObject, compressão e recurso binário
  determinístico num compositor que hoje só escreve texto, para um ganho que o cabeçalho tipográfico
  entrega em boa parte.

---

## D-009 — Como a fixture de bytes sobrevive a cinco entregas que mudam a composição

**Decisão**: a fixture é regenerada **no mesmo commit** de cada entrega que muda a composição, pelo
script existente, com o diff do documento revisado. Ela conserva o nome; o que muda é o conteúdo. E
o gerador passa a receber uma **autoridade fixa, versionada** ao lado do snapshot de referência, em
`tests/contract/fixtures/autoridade_publicada.json`.

**Racional**: a fixture prova ausência de mudança **desde a última mudança intencional** — não
ausência de mudança para sempre. O nome do arquivo é o do contrato do documento publicado, não o da
versão da composição, e renomeá-lo a cada entrega criaria cinco arquivos binários e nenhuma
informação nova.

A autoridade fixa é obrigatória por D-005: depois de FR-035, compor em modo publicado sem autoridade
é recusado, então o gerador não roda sem ela. Versioná-la ao lado do snapshot é a mesma razão pela
qual o snapshot é versionado — *"sem ele a fixture seria um arquivo binário que ninguém consegue
reproduzir, e a comparação viraria fé"*.

**Alternativas recusadas**:

- *Congelar a fixture só ao final da feature.* Deixaria as quatro primeiras entregas sem a rede que
  a fixture é, justo enquanto a composição está mudando mais.
- *Autoridade embutida no código do gerador.* Ficaria fora do diretório de fixtures e invisível a
  quem tenta reproduzir a comparação.
- *Suspender o teste de bytes durante a feature.* Apaga a evidência exatamente quando ela é mais
  útil.

---

## D-010 — O que acontece com os testes que afirmam a forma antiga

**Decisão**: separar a suíte existente em duas naturezas e tratá-las de forma oposta.

| Natureza | Exemplo | O que acontece |
|---|---|---|
| **Invariante** | determinismo, acentuação, ausência de UUID no corpo, corpo normativo suficiente a partir do snapshot, prévia sem afirmação de integridade, parágrafos preservados | **Permanece intocado.** Se falhar, a entrega está errada |
| **Forma da apresentação** | a Etapa imprime `caráter: …; peso: …`, o Cronograma imprime `Início: …` em parágrafo, a integridade imprime `Versão do schema` | **Atualizado junto da entrega que o torna falso**, nunca antes e nunca depois |

**Racional**: é a distinção que impede os dois erros simétricos — quebrar um invariante achando que
era forma, e preservar uma forma achando que era invariante. O teste
`test_etapas_aparecem_com_caracter_peso_e_nota_minima` é o caso limite: o **fato** que ele afirma
continua verdadeiro e obrigatório (FR-027); a **frase** que ele procura deixa de existir. Ele é
reescrito, não removido.

**Alternativa recusada**: *marcar os testes de forma como `xfail` durante a feature.* Transformaria
cinco entregas em uma dívida silenciosa e esconderia regressão real atrás de falha esperada.

---

## D-011 — Onde a marca de prévia é composta

**Decisão**: a marca de prévia **sai do fluxo normativo** e passa a ser emitida em posição fixa da
página, na mesma passada que já emite o rodapé — em toda página, e não apenas na primeira.

**Racional**: FR-042 exige que o conjunto de quebras do corpo normativo seja idêntico entre prévia e
publicado. Hoje a marca é escrita **dentro** do fluxo, entre o cabeçalho e as seções
(`pdf.py:353`), e portanto empurra todo o conteúdo para baixo: a prévia e o publicado quebram em
lugares diferentes, e quem revisa a prévia não vê a paginação que vai publicar. Reservar espaço
equivalente no publicado "para compensar" seria pior — poria um vazio inexplicável num ato
administrativo.

Tirar a marca do fluxo cumpre FR-042 **por construção**, e não por coincidência de medida: se ela
não participa da geometria do fluxo, não há como ela alterá-la. O ganho colateral é que a marca
passa a aparecer em todas as páginas, que é o comportamento correto para um documento sem valor de
publicação — hoje a página 2 de uma prévia não se identifica como prévia em lugar nenhum do corpo.

**Consequência**: a região fixa é a mesma nos dois modos, ocupada na prévia e vazia no publicado.
Nenhuma regra visual passa a existir só na prévia (FR-041); o que existe só na prévia é o **texto**
da marca.

**Alternativas recusadas**:

- *Manter no fluxo e aceitar a diferença de quebra.* Viola FR-042 e derrota o propósito da prévia:
  revisar um documento cuja paginação não é a que será publicada.
- *Manter no fluxo e reservar espaço equivalente no publicado.* Cumpre a letra de FR-042 e produz um
  espaço em branco sem causa no documento oficial — o oposto de FR-031.
- *Marca d'água diagonal atrás do texto.* Exigiria estado gráfico e transparência, fora do
  vocabulário de FR-003, e prejudicaria a leitura da prévia.
- *Marca só na primeira página, fora do fluxo.* Cumpre FR-042 e mantém o defeito de a página 2 de
  uma prévia não se identificar.
