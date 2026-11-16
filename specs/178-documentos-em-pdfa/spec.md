# Feature Specification: Os documentos que o GPS compõe nascem em PDF/A

**Feature Branch**: `claude/pdfa-documentos-gerados-6d77eb`, nascida da `main` em `619a4ae0` (o merge
do #579)

**Created**: 2026-11-16

**Status**: Especificada, planejada e implementada em 16/11, no mesmo PR, sem merge. O merge é do
usuário.

**Input**: a decisão do usuário de 16/11, depois do estudo de viabilidade do PDF/A
(`doc/estudo-pdf-a-preservacao-documental-2026-11-16.md`): *"A minha recomendação é adotar o PDF/A só
em parte. Os PDFs que o próprio GPS gera devem passar a sair em PDF/A, o que é barato."* As quatro
decisões que a especificação pedia foram tomadas pelo usuário no mesmo dia (D-001 a D-004).

> **Faixa de identificadores.** Esta spec abre em **FR-8150** e **SC-2820**, e reserva até o requisito
> oito mil cento e noventa e nove e o critério dois mil oitocentos e trinta e nove. Os tetos medidos em
> 16/11/2026, na `main` e em todas as worktrees, eram a reserva da `177`: o requisito oito mil cento e
> quarenta e nove e o critério dois mil oitocentos e dezenove. Nenhum requisito de experiência. As
> decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-1383 da `069`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

Os documentos que o GPS compõe são, quase todos, os de guarda permanente: o Edital, as Retificações,
o resultado, a lista dos convocados. O estudo de 16/11 mediu o que falta a eles para serem PDF/A, o
formato que a Orientação Técnica nº 4 da CTDE/CONARQ recomenda para documento arquivístico, e achou
pouco:

- O Edital e os relatórios descumprem só quatro regras da ISO 19005-2, todas sobre o **arquivo**, e
  nenhuma sobre o que a página desenha: o identificador do arquivo, os metadados que declaram a
  conformidade, o perfil de cor de saída e a marca de "imprimível" nas anotações de link. Com os quatro
  acrescentados por fora, o Edital passou no validador em PDF/A-2b, 2u e 1b, e o relatório em 2u e 2a.
- O comprovante e a família da divulgação descumprem os mesmos quatro e um quinto: **não embutem a
  fonte**. Declaram a Helvetica, e cada leitor desenha com a que tiver — foi o defeito do negrito
  desenhado como regular, corrigido só no Edital pela `069`. Daqui a vinte anos, "a fonte que o leitor
  tiver" é uma incógnita.

E o caminho caro está descartado: a conversão de PDF pronto produziu, na prova de conceito, PDF/A
"válido" a partir de arquivo ilegível, apagou assinatura e perdeu acentos sem que o validador
acusasse. Gerar já conforme não tem nenhum desses riscos — o escritor é do GPS, e os objetos que
faltam são objetos que ele escreve.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora, e por quê |
|---|---|
| O Edital publicado e o documento consolidado de cada Retificação | os documentos que os candidatos enviam: não são convertidos, por decisão do usuário (a conversão automática destrói assinatura e produz conformidade sem fidelidade) |
| O relatório do Edital e o relatório consolidado de gestão | a conferência periódica de fixidez dos arquivos recebidos: tarefa de operação separada |
| O resultado divulgado, a publicação das inscrições, a dos convocados e a da agenda | a representação de preservação na destinação arquivística, que espera a decisão de retenção (B-2) |
| O comprovante de inscrição das inscrições enviadas a partir da implantação | assinatura digital, certificado e carimbo: a FR-037 da `008` continua valendo |
| A emenda da FR-1383 e do SC-522 da `069` | PDF/UA e qualquer acessibilidade além da que o documento já tem |
| A verificação por validador independente no CI | converter, recompor ou regravar qualquer documento já gravado |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O Edital e a Retificação publicados são PDF/A (Priority: P1)

A autoridade publica o Edital, ou uma Retificação. O documento gravado como ato é um PDF/A-2u: carrega
a fonte, o perfil de cor e os metadados que o descrevem, e qualquer leitor conforme o desenha igual
daqui a décadas. Nada do que a pessoa vê muda — a página, o sumário clicável, os marcadores, o idioma,
os endereços clicáveis continuam os mesmos.

**Why this priority**: o Edital é o documento de guarda permanente por excelência, e é o mais barato:
quatro acréscimos e nenhum compromisso de bytes com terceiros (D-001).

**Independent Test**: compor o Edital do cenário fixo de contrato e validá-lo em PDF/A-2u; comparar o
conteúdo de cada página com o de antes desta feature.

**Acceptance Scenarios**:

1. **Given** um Edital pronto para publicar, **When** a autoridade publica, **Then** o documento
   gravado declara PDF/A-2 nível U e passa no validador nesse nível.
2. **Given** o mesmo Edital composto antes e depois desta feature, **When** se compara o que cada
   página desenha, **Then** é idêntico; só o arquivo ganhou os objetos da conformidade.
3. **Given** uma Retificação de Edital publicado antes da implantação, **When** ela é publicada,
   **Then** o documento consolidado dela nasce PDF/A, e o documento do ato original continua o arquivo
   que foi.
4. **Given** a prévia do Edital, **When** a gestão a abre, **Then** ela não declara PDF/A (D-003).

---

### User Story 2 — Os relatórios são PDF/A-2a (Priority: P1)

A gestão emite o relatório do Edital ou o relatório consolidado. O arquivo já é marcado (título,
parágrafo, lista, tabela e figura na árvore de estrutura), e por isso declara o nível mais alto, o A,
que o validador confirma.

**Why this priority**: vai junto com o Edital, pelo mesmo motivo, e reaproveita o mesmo escritor de
arquivo.

**Independent Test**: compor um relatório de cada espécie a partir dos fatos de teste e validá-los em
PDF/A-2a.

**Acceptance Scenarios**:

1. **Given** fatos de um Edital, **When** o relatório é emitido, **Then** o arquivo declara PDF/A-2
   nível A e passa no validador nesse nível.
2. **Given** o mesmo conjunto de fatos, **When** o relatório é emitido duas vezes, **Then** os bytes
   são os mesmos, e o resumo que vai à trilha confere.

---

### User Story 3 — A família da divulgação nasce PDF/A, com a fonte embutida (Priority: P2)

A gestão publica o resultado de um marco, as inscrições, os convocados ou a agenda. O documento
gravado embute a Edital Sans, que o Edital já embute, e é PDF/A-2u. O texto e a ordem são os de
antes; a quebra de linha pode cair em outro ponto, porque as larguras da fonte embutida diferem das da
Helvetica declarada em poucos caracteres ("í", "ª", "º").

**Why this priority**: depende de emendar a FR-1383 da `069`, e por isso vem no segundo incremento
(D-001).

**Independent Test**: compor o documento de divulgação do conteúdo fixo de contrato e validá-lo em
PDF/A-2u; comparar o texto extraído com o de antes.

**Acceptance Scenarios**:

1. **Given** um resultado a divulgar, **When** a gestão o publica, **Then** o documento gravado embute
   as fontes que desenha e passa no validador em PDF/A-2u.
2. **Given** o mesmo conteúdo composto antes e depois, **When** se extrai o texto, **Then** são as
   mesmas palavras, na mesma ordem.
3. **Given** um resultado publicado antes da implantação, **When** alguém o baixa, **Then** recebe os
   bytes gravados no dia, sem mudança.

---

### User Story 4 — O comprovante não quebra a promessa feita ao candidato (Priority: P2)

O comprovante de inscrição não é gravado: é composto a cada download, e a página dele mostra o SHA-256
do arquivo, que o candidato pode ter anotado. Quem enviou a inscrição antes da implantação continua
recebendo, para sempre, o comprovante de hoje, byte a byte. Quem envia depois recebe o comprovante em
PDF/A, e o resumo mostrado na página é o desse arquivo (D-002).

**Why this priority**: é o único documento da feature que se regenera, e o único em que mudar o escritor
quebraria uma promessa já feita a uma pessoa.

**Independent Test**: emitir o comprovante de uma inscrição enviada antes da implantação e de uma
enviada depois; o primeiro confere com a fixture de hoje, o segundo passa no validador.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada antes da implantação, **When** o candidato baixa o comprovante,
   **Then** os bytes são os de antes da feature, e o resumo que a página mostra é o mesmo de sempre.
2. **Given** uma inscrição em rascunho criada antes da implantação, **When** o candidato a envia depois,
   **Then** o comprovante dela é PDF/A — nenhum resumo tinha sido mostrado antes do envio.
3. **Given** uma inscrição enviada depois da implantação, **When** a página do comprovante calcula o
   resumo e o candidato baixa o arquivo, **Then** os dois conferem.

---

### User Story 5 — A conformidade é verificada a cada mudança (Priority: P3)

Quem muda o escritor de PDF sabe, no próprio PR, se algum tipo de documento deixou de ser conforme. Um
validador independente roda no CI sobre um exemplar de cada tipo; produção não ganha nada.

**Why this priority**: sem ela, a conformidade é afirmação, e a primeira mudança no escritor a desfaz
em silêncio (Rec. 13 da Orientação Técnica nº 4).

**Independent Test**: tirar de um exemplar um dos acréscimos e ver o job reprovar.

**Acceptance Scenarios**:

1. **Given** um PR qualquer, **When** o CI roda, **Then** um exemplar de cada um dos nove tipos é
   validado no nível que declara, numa execução só do validador.
2. **Given** um exemplar não conforme, **When** o CI roda, **Then** o job reprova e diz qual arquivo e
   qual regra.

---

### Edge Cases

- **Retificação de Edital publicado antes da implantação.** O documento consolidado é novo e nasce
  PDF/A; o do ato original não muda. Um mesmo Edital passa a ter documentos dos dois tipos, e isso é o
  esperado.
- **Inscrição reaproveitada** (`010`, reaproveitamento da inscrição): é inscrição nova, e o envio dela
  decide o escritor como o de qualquer outra.
- **Caractere sem grafia** nos documentos da família: o tratamento continua o de hoje (`estrito` só no
  Edital); a fonte embutida tem os mesmos caracteres WinAnsi que a Helvetica declarava.
- **Documento sem link nem marcador** (comprovante, divulgação): não declara título nem autor, e os
  metadados declaram só a conformidade — o que existe no dicionário de informação, e só isso, se repete
  nos metadados.
- **O relatório se emite de novo** a cada pedido: os bytes mudam uma vez, na implantação, e daí em
  diante o mesmo conjunto de fatos dá os mesmos bytes.
- **Documento gravado antes da implantação, baixado depois**: sai como foi gravado. Ele não declara
  PDF/A, e nada o converte.

## Requirements *(mandatory)*

### Functional Requirements

#### O que nasce PDF/A

- **FR-8150**: Todo documento destes tipos, composto depois da implantação, MUST ser arquivo PDF/A-2
  conforme, no mínimo no nível B: o Edital publicado; o documento consolidado de Retificação; o
  resultado divulgado; a publicação das inscrições; a publicação dos convocados; a agenda publicada; o
  comprovante das inscrições a que a FR-8163 atribui o escritor novo; o relatório do Edital; o relatório
  consolidado de gestão.
- **FR-8151**: O nível declarado MUST ser o U (texto extraível em Unicode) em todos, salvo nos dois
  relatórios, que MUST declarar o nível A, porque já são marcados.
- **FR-8152**: O arquivo MUST declarar, nos metadados XMP, a parte e o nível, e MUST cumprir o que
  declara. A declaração é a mesma para todo documento do mesmo tipo.

#### Os acréscimos ao arquivo

- **FR-8153**: Os metadados XMP MUST repetir o título e o autor que o dicionário de informação declara,
  e só eles; MUST NOT trazer data de criação, de modificação, nem produtor ou ferramenta.
- **FR-8154**: O arquivo MUST trazer o identificador do arquivo derivado do próprio conteúdo: o mesmo
  conteúdo dá o mesmo identificador.
- **FR-8155**: O mesmo conteúdo composto duas vezes MUST produzir os mesmos bytes, em todo tipo da
  FR-8150. Preserva a FR-063a da `009` e o SC-523 da `069`.
- **FR-8156**: O arquivo MUST declarar como condição de saída o espaço sRGB, com um perfil ICC
  versionado no repositório. O perfil MUST ter licença que permita a redistribuição, escrita no próprio
  repositório, e a origem e o resumo dele MUST estar registrados ao lado, conferidos por teste — como a
  fonte embutida da `069`.
- **FR-8157**: Toda anotação de link MUST ser marcada como imprimível. Os links do sumário, os endereços
  clicáveis, os marcadores, o idioma, o título exibido na janela e a marcação lógica dos relatórios MUST
  continuar como estão.
- **FR-8158**: Todo documento da FR-8150 MUST embutir as fontes que desenha. Os documentos da família da
  divulgação e o comprovante novo passam a embutir a Edital Sans da `069` e MUST medir o texto pelas
  larguras dela, como o Edital mede (a FR-1381 da `069`).

#### O que não muda

- **FR-8159**: No Edital, na Retificação e nos dois relatórios, o que cada página desenha MUST ser
  idêntico ao de antes desta feature, para o mesmo conteúdo: os acréscimos são do arquivo, e não da
  página.
- **FR-8160**: Nos documentos da família da divulgação e no comprovante novo, o texto MUST continuar o
  mesmo, na mesma ordem. A quebra de linha e a paginação podem mudar pelas larguras da fonte embutida, e
  isso é aceito.
- **FR-8161**: Documento já gravado MUST NOT ser convertido, recomposto nem regravado. A conformidade
  vale para o que se compõe depois da implantação.
- **FR-8162**: A prévia do Edital MUST NOT declarar PDF/A: ela não é ato (D-003). Ela continua como é
  hoje.
- **FR-8167**: Nenhum acréscimo desta feature MUST criar assinatura digital, certificado ou carimbo. A
  FR-037 da `008` continua valendo.

#### O comprovante

- **FR-8163**: A inscrição MUST registrar, no envio, qual escritor compõe o comprovante dela: a
  inscrição enviada antes da implantação fica com o escritor de hoje; a enviada depois, com o escritor
  PDF/A. O registro é feito uma vez, no envio, e não muda (D-002, D-005).
- **FR-8164**: O comprovante da inscrição com o escritor de hoje MUST continuar byte a byte o mesmo,
  para sempre: o resumo que a página já mostrou ao candidato continua conferindo.
- **FR-8165**: A página do comprovante e o arquivo que ela oferece MUST usar o mesmo escritor: o resumo
  publicado na página confere com o arquivo baixado, nos dois escritores (a FR-063a da `009`).

#### A emenda da `069`

- **FR-8166**: A FR-1383 e o SC-522 da `069` MUST ser revistos, com a redação anterior preservada na
  própria `069`: o comprovante das inscrições enviadas antes da implantação continua byte a byte o
  mesmo; o documento de divulgação de resultado e os demais compostos pelo mesmo escritor passam a ser
  PDF/A com a fonte embutida, e são presos byte a byte por novas fixtures.

#### A verificação

- **FR-8168**: O CI MUST validar, num validador de conformidade independente do GPS, um exemplar de
  cada tipo da FR-8150, no nível que o exemplar declara. Exemplar não conforme MUST reprovar o job, com
  o nome do arquivo e as regras descumpridas.
- **FR-8169**: A validação MUST rodar em lote — uma execução do validador para todos os exemplares.
- **FR-8170**: Produção MUST NOT ganhar dependência de execução: nem validador nem conversor roda no
  servidor, e a composição continua sem biblioteca de PDF.
- **FR-8171**: A suíte MUST conferir, sem o validador, que cada tipo da FR-8150 traz os acréscimos das
  FR-8152 a FR-8158 — para que a regressão apareça em qualquer ambiente, e não só no CI.

### Key Entities

- **Inscrição**: ganha o registro de qual escritor compõe o comprovante dela (FR-8163). Ausente nas
  inscrições enviadas antes da implantação, o que as identifica.
- **Perfil de cor de saída**: arquivo versionado, com licença, origem e resumo registrados (FR-8156).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2820**: Os **nove** tipos da FR-8150 passam no validador independente, cada um no nível que
  declara — os relatórios em 2a, os demais em 2u —, em todo PR.
- **SC-2821**: O mesmo conteúdo composto duas vezes dá **os mesmos bytes** nos nove tipos.
- **SC-2822**: No Edital e nos dois relatórios, **zero** diferenças no que as páginas desenham, para o
  mesmo conteúdo, entre antes e depois desta feature.
- **SC-2823**: O comprovante de uma inscrição enviada antes da implantação é **byte a byte** idêntico ao
  de antes: **zero** resumos já mostrados deixam de conferir.
- **SC-2824**: Nos documentos da família e no comprovante novo, o texto extraído é **o mesmo**, palavra a
  palavra e na mesma ordem, do de antes.
- **SC-2825**: **Zero** documentos já gravados mudam.
- **SC-2826**: **Zero** dependências novas de execução em produção.
- **SC-2827**: O Edital e os relatórios conservam **todos** os links, marcadores e elementos de
  estrutura: as mesmas contagens antes e depois.

## Decisões

### D-001 — Todos os documentos, o Edital primeiro

*Decisão do usuário, 16/11.* A spec cobre os nove tipos, em dois incrementos: o Edital, a Retificação e
os relatórios primeiro, porque custam quatro acréscimos e nenhum compromisso de bytes com terceiros; a
família da divulgação e o comprovante depois, porque exigem emendar a FR-1383 da `069` (FR-8166).

### D-002 — O comprovante já emitido mantém o escritor antigo

*Decisão do usuário, 16/11.* A alternativa era aceitar que o resumo do comprovante mudasse e avisar o
candidato. Ficou a outra: a inscrição enviada antes da implantação recebe, para sempre, o comprovante
de hoje. O custo é manter vivo o escritor antigo, congelado, só para ela.

### D-003 — A prévia fica sem PDF/A

*Decisão do usuário, 16/11, na sugestão do estudo.* A prévia não é ato, não se grava e não se guarda.

### D-004 — Esta é a spec 178

*Decisão do usuário, 16/11.* O número seguinte à `177`.

### D-005 — O corte é gravado na inscrição, e não lido de uma data

O escritor do comprovante é escolhido pelo que a inscrição registrou no envio, e não pela comparação
da data de envio com uma data de corte. A data da implantação não é conhecida quando o código é
escrito, e uma constante errada por um dia trocaria o comprovante de quem enviou naquele dia. O
registro é feito na mesma escrita que muda a inscrição para enviada, e a enviada é imutável por
gatilho desde a `009`.

### D-006 — PDF/A-2, e não PDF/A-1

A Rec. 1 da Orientação Técnica nº 4 prefere o PDF/A-1; a Rec. 2 manda o PDF/A-2 quando houver
assinatura PAdES. Se a instituição vier a assinar o PDF publicado com certificado, fora do GPS, é o
PDF/A-2 que aceita, e o custo aqui é o mesmo. O nível U porque o Edital de vinte anos atrás precisa ter
texto pesquisável, e o validador em 2u é o que pega a perda de acentos que o 2b deixa passar.

## Assumptions

- A data de implantação é a do primeiro deploy com esta feature; não há janela de transição.
- O validador é o veraPDF, na imagem oficial, só no CI. A partida da máquina virtual dele leva ~10 s, e
  por isso a validação é em lote (FR-8169).
- A fonte embutida é a Edital Sans da `069`, sob a OFL 1.1, já versionada: a Rec. 5 da Orientação
  Técnica nº 4 (licença da fonte) está atendida.
- O nível U basta com a codificação WinAnsi da fonte TrueType não simbólica, como o estudo mediu no
  Edital.
- Os relatórios não são gravados; o resumo deles vai à trilha. Mudar os bytes deles na implantação não
  quebra compromisso nenhum.
