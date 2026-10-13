# Feature Specification: O Edital oficial em linguagem simples — redação, organização, tipografia e navegação (lote 1)

**Feature Branch**: `claude/edital-linguagem-simples-79eec9` — worktree criada sobre a `main`
`a79ce463` (PR #273), que já tem a `064`, a `065`, a `066`, a `067` e a `068`.

**Created**: 2026-10-12

**Status**: Draft

**Input**: a [análise de linguagem simples de 12/10/2026](../../doc/analise-edital-linguagem-simples-2026-10-12.md),
em três rodadas com o responsável pelo produto, e a amostra que ela produziu
([`doc/analise-edital-linguagem-simples-2026-10-12/`](../../doc/analise-edital-linguagem-simples-2026-10-12/):
`proposta-A.pdf`, `proposta-B.pdf`, `proposta-B-variante-de-teste.pdf`, `equivalencia.md`, `proposta.py`).
Também os achados ainda abertos da [auditoria do Edital em PDF de 08/10/2026](../../doc/auditoria-edital-pdf-2026-10-08.md):
ED-05 (linguagem das frases geradas, L1–L17), ED-07 parte P e ED-08 (navegação), ED-14 (fonte não
embutida), ED-16 (listas sem recuo pendente), ED-18 (Requerimento fora da lista de documentos), ED-22
(nome do arquivo), ED-24 (siglas em caixa alta) e ED-25 (descrição no ato).

O que o responsável pelo produto decidiu ou pediu, citado aqui como 1º a 10º:

1. **A linguagem simples vai no próprio ato oficial**, em PDF, gerado pelo compositor atual. Não há
   versão complementar.
2. **O lote é: redação das frases geradas, organização das seções, agrupamento seguro, tipografia,
   navegação e paginação.**
3. **Ordem e títulos (a D2 da análise):** a ordem e os títulos da amostra são o padrão inicial,
   adaptado às seções que cada Edital tem. Títulos em pergunta onde ajudam o candidato, diretos onde
   funcionam melhor.
4. **Fonte (a D8 da análise):** uma fonte embutida, regular e negrito, com a licença da versão
   efetivamente distribuída verificada e os arquivos dos dois estilos incluídos.
5. **Menos linguagem interna.** O resumo diz "160 vagas em quatro localidades: …"; "Cadastro de
   reserva" por extenso; a seleção descrita em poucas palavras, sem reproduzir nome longo de Etapa,
   que fica completo na seção. Sem campo novo.
6. **Paginação flexível.** Exigem-se: ausência de título órfão, linhas de tabela preservadas,
   cabeçalho repetido, e blocos relacionados juntos quando couberem — permitindo dividir os maiores.
   Item de lista maior que uma página pode se partir. Os limites da amostra (45%, 60%) são heurística,
   não requisito. Equilibrar continuidade e espaço: evitar página quase vazia e última página com
   pouco conteúdo. Número de páginas não é meta.
7. **Problemas herdados ficam fora**, como achados próprios: o comprovante de residência exigido só do
   TP-01 ([achado](../../doc/achado-requisito-sem-comprovante-correspondente.md)) e o sorteio
   condicionado no texto e incondicional no sistema ([achado](../../doc/achado-sorteio-condicionado-no-texto-e-incondicional-no-sistema.md)).
   A feature reproduz o dado como está declarado, sem ampliar nem corrigir regra.
8. **A conferência semântica por enunciado faz parte da validação**, e não só a contagem de fatos —
   foi ela que encontrou, na amostra, uma condição acrescentada, uma frase falsa num dos cenários e
   uma dependência partida entre frases.
9. **A acessibilidade completa fica fora**, como limitação explícita: o documento continua sem
   marcação para tecnologia assistiva, e o lote não promete conformidade.
10. **Fica fora também:**
    - troca de motor e HTML→PDF;
    - PDF marcado;
    - versão complementar;
    - Libras;
    - LLM;
    - portal;
    - "o que mudou" na Retificação (ED-06);
    - tipo do Evento do cronograma;
    - endereço do certame gerado (domínio congelado e rota legível);
    - guia de redação como funcionalidade do produto (ele pode existir como documento).

> **Faixa de identificadores.** Abre em **FR-1360** e **SC-516**. Não há requisito de experiência
> nesta spec, e a faixa de experiência não é usada. O teto medido em 12/10/2026 na `main` e em
> todas as worktrees era o da `068`: mil trezentos e cinquenta e nove para os requisitos funcionais,
> quinhentos e quinze para os critérios de sucesso, cento e noventa e três para a experiência. O
> número da pasta, `069`, é o seguinte livre em todas as worktrees. As decisões desta spec nascem em
> `D-001`.

**A frase que governa:**

> O candidato encontra a regra pela pergunta que tem, lê-a em palavras dele, num documento que é o
> mesmo em qualquer leitor — e a regra continua sendo exatamente a que a comissão homologou.

**E a frase que mantém o corte:**

> Esta feature muda como o Edital é escrito pelo sistema e composto na página, e só isso. Nenhuma
> regra é acrescentada, retirada ou corrigida, nenhum documento já publicado muda, e o texto livre de
> quem elabora sai como foi escrito.

## Clarifications

### Session 2026-10-12

- Q: Quando um Edital publicado antes deste lote for retificado depois, como o consolidado deve ser
  composto? → A: **A**, com ressalvas. O consolidado recebe a redação, a tipografia e a navegação
  novas, compatíveis com a sua estrutura, e mantém a **ordem, os títulos, a numeração e a divisão das
  seções** do original. Editais novos usam a estrutura nova. As mudanças editoriais **não modificam
  documentos publicados** e **não podem quebrar remissões numéricas ou textuais**. O módulo de frases
  é compartilhado, e cada leitor tem tratamento próprio:
  - o documento original publicado fica preservado;
  - o novo consolidado recebe as melhorias compatíveis com a sua estrutura;
  - o portal e a Revisão podem apresentar a redação mais clara, desde que reflitam a versão
    aplicável;
  - a redação histórica do ato de ordenação já publicado permanece identificável e preservada.

  A implementação começa verificando o que já está congelado na publicação e o que hoje é
  reconstruído na exibição.
- Q: Num Edital ainda em elaboração e publicado depois do lote, quando o texto livre cita uma seção
  pelo título antigo ("na seção Perfis de Vaga"), o que o sistema deve fazer? → A: **Aviso de
  conferência na Revisão, não impeditivo, que confere o destino da remissão, e não só o título.** A
  seção antiga pode ter sido repartida: o método do sorteio saiu de "Perfis de Vaga" e foi para "Como
  será a seleção?", e trocar um título pelo outro pode continuar errado. O aviso:
  - mostra o trecho encontrado;
  - pede ao Elaborador que confira a seção correta;
  - sugere um destino só quando a correspondência é confiável, e nos demais casos diz que há dúvida.

  O sistema não reescreve o texto. A conferência fica explícita na Revisão, antes da homologação.
- Q: Qual título deve ter a seção `informacoes-gerais`, que serve às quatro famílias de Edital, inclusive
  seleção de bolsista? → A: **"Informações gerais"**, para todo Edital, sem campo para variar o título.
  Dentro da seção, um subtítulo como "Sobre o curso" ou "Sobre a função" pode tornar o conteúdo mais
  específico quando fizer sentido.

---

## Por que esta feature existe

### O problema

O PDF do sistema é o ato oficial do piloto desde 28/09/2026. A auditoria de 08/10 deu a ele nota
**4** em clareza de linguagem, **4** em organização, **3** em navegação e **2** em acessibilidade. As
specs `065`, `067` e `068` corrigiram as normas erradas e a repetição por Perfil. Ficaram de fora:

- **As frases que o próprio sistema escreve falam a língua do sistema.** "Corte: Progridem para
  Análise documental os primeiros desta ordem, até o número de vagas ofertadas no recorte";
  "Continuação"; "Semente"; "Normalização: nenhuma"; "menor valor declarado em Data de nascimento";
  "inscrições submetidas". O Elaborador não tem como mudar essas frases, e o candidato não as entende.
- **A regra está espalhada.** A de recurso está em três lugares; a de seleção, em quatro (o marco
  dentro da seção de Perfis, as Etapas, os critérios, a verificação). O Cronograma vem na seção 11
  de 17.
- **A aparência depende do leitor.** O documento declara Helvetica sem embuti-la. No poppler —
  Linux, LibreOffice e muitos leitores —, o negrito sai regular, com o espaçamento do negrito, e os
  títulos perdem a hierarquia. O compositor ainda mede "í", "ì", "î", "ï" (e "ª", "º" no negrito)
  menores do que são, e a linha justificada que os tem passa da margem.
- **Não há navegação.** Não há sumário, marcadores, links, título nem idioma no arquivo, e o
  download não tem nome.

### As evidências

A amostra compôs os cenários A (pós-graduação, 4 polos, sorteio) e B (tutores, 18 Perfis, pontuação)
com as primitivas do compositor atual, por um roteiro sem nada escrito para um cenário:

| | A hoje | A proposta | B hoje | B proposta |
|---|---|---|---|---|
| Páginas | 6 | 7 | 14 | 10 |
| Fatos do documento de hoje presentes | — | 27 de 27 | — | 85 de 85 |
| Regras conferidas por enunciado | — | 43 | — | 44 |
| Mesma aparência em CoreGraphics, poppler e PDFium | não (negrito perdido no poppler) | sim | não | sim |
| Sumário, marcadores, links, título, idioma | não | sim | não | sim |
| Bytes determinísticos | sim | sim | sim | sim |

O responsável pelo produto aprovou a estrutura e a direção tipográfica, com os ajustes 5º a 7º acima,
que a amostra ainda não reflete.

---

## User Scenarios & Testing *(mandatory)*

Os atores são o **candidato**, que lê o Edital publicado, e a **comissão** — Elaborador e Homologador —,
que prepara e confere o documento antes de publicá-lo, pela prévia e pela Revisão.

### User Story 1 — O candidato lê a regra em palavras dele, e a regra é a mesma (Priority: P1)

O candidato que lê como será classificado encontra "Passam para a Etapa “Análise documental” os
primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista,
mais 15 (quinze) suplentes", e não "Corte: Progridem para Análise documental os primeiros desta
ordem, até o número de vagas ofertadas no recorte". O desempate diz "data de nascimento mais antiga,
informada na inscrição", e não "menor valor declarado em Data de nascimento". Cada
frase nova diz o mesmo que a anterior: as mesmas condições, exceções, alcance e consequências.

**Why this priority**: é onde está o jargão (origem C da auditoria), e só o sistema pode corrigi-lo. O
ganho alcança todo Edital publicado depois, com uma revisão só.

**Independent Test**: compor os cenários A e B. Conferir que nenhum termo interno da lista do
FR-1366 aparece, e que a conferência por enunciado não acha regra acrescentada, retirada ou mudada.

**Acceptance Scenarios**:

1. **Given** um marco por sorteio com corte pelo quadro de vagas, 15 suplentes e continuação
   admitida, **When** o documento é composto, **Then** ele diz quem participa do sorteio, quantos
   passam à Etapa seguinte por lista, os 15 suplentes e que outros poderão ser chamados na mesma
   ordem — **sem** acrescentar condição que a norma não tem (por exemplo, "se sobrarem vagas").
2. **Given** um marco por pontuação com três critérios de desempate (data de nascimento, meses de
   experiência, pontuação na Etapa), **When** o documento é composto, **Then** cada critério sai em
   palavras do candidato, na mesma ordem, com o mesmo efeito para quem não informou o dado.
3. **Given** um Edital em que nenhum Perfil tem cadastro de reserva e o corte prevê suplentes,
   **When** o documento é composto, **Then** ele explica que os suplentes são chamados, na ordem, para
   as vagas deste Edital que não forem preenchidas. **Given** um Edital com cadastro de reserva,
   **Then** essa explicação **não** sai.
4. **Given** a mesma regra, **When** a comissão a vê na Revisão e no ato de ordenação, **Then** a frase
   é a mesma do documento.

---

### User Story 2 — O candidato acha a resposta pela pergunta que tem (Priority: P1)

O candidato abre o Edital e encontra, logo no início, um resumo:

- quantas vagas há, e onde;
- se há cadastro de reserva;
- quando se inscrever;
- quantas inscrições pode enviar;
- como será a seleção;
- onde estão as datas.

Cada linha remete ao item. Depois vem um sumário. As seções seguem a ordem das perguntas — quem pode
se inscrever, quantas vagas há, o cronograma, como se inscrever, que documentos enviar, como será a
seleção, como recorrer, como será a convocação e a matrícula. Cada regra gerada pelo sistema está na
seção que trata dela.

**Why this priority**: a regra espalhada em três ou quatro lugares é o que mais dificulta as tarefas
de classificação e recurso, as piores do teste heurístico da auditoria.

**Independent Test**: compor A e B. Conferir:

- o resumo, linha a linha, contra o snapshot;
- o sumário contra as páginas;
- que a regra de recurso gerada está na seção de recursos, a de convocação na de convocação e os
  requisitos dos Perfis na seção de quem pode se inscrever.

**Acceptance Scenarios**:

1. **Given** quatro Perfis com vagas em quatro localidades, **When** o documento é composto, **Then** o
   resumo diz "160 vagas em quatro localidades: …", com os nomes, e "Cadastro de reserva: não há".
2. **Given** uma Etapa de nome longo ("Prova de títulos, conforme a Ficha de Avaliação do Anexo IV —
   …"), **When** o resumo descreve a seleção, **Then** ele a descreve em poucas palavras, e o nome
   completo aparece na seção da seleção.
3. **Given** um Edital sem uma das seções do catálogo (sem matrícula, sem certificado), **When** o
   documento é composto, **Then** a seção não aparece, e a numeração e o sumário seguem as que existem.
4. **Given** 18 Perfis, 16 deles de mesmo nome e sem vaga imediata, **When** a seção de vagas é
   composta, **Then** os 16 saem numa tabela própria, com o nome na legenda e sem repeti-lo por linha.
   O que é igual em todos os Perfis — carga horária, remuneração, cadastro — sai uma vez.
5. **Given** dois grupos de Perfis com regras de classificação diferentes, **When** a seleção é
   composta, **Then** o que é igual nos grupos sai uma vez, e cada grupo traz só o que é dele.
   Corte, empate, suplentes e continuação nunca se separam entre a parte comum e a de um grupo.

---

### User Story 3 — O documento é o mesmo em qualquer leitor (Priority: P1)

Quem abre o Edital no Preview, no Chrome, no Edge, no LibreOffice ou num leitor de Linux vê os mesmos
títulos em negrito, o mesmo espaçamento e as mesmas quebras de linha. Nenhuma linha justificada passa
da margem.

**Why this priority**: o ato oficial não pode mudar de aparência conforme quem o abre. A hierarquia
tipográfica é a primeira navegação do documento.

**Independent Test**: renderizar a mesma página em três motores diferentes e comparar. Medir a linha
mais larga de cada página contra a margem.

**Acceptance Scenarios**:

1. **Given** o documento composto, **When** é aberto em três motores de renderização diferentes,
   **Then** os títulos saem em negrito e as quebras de linha são as mesmas nos três.
2. **Given** um parágrafo justificado com muitos "í", **When** é composto, **Then** nenhuma linha passa
   da margem direita.
3. **Given** um item de lista longo, **When** é composto, **Then** as linhas de continuação alinham com
   o texto do item, e não com o marcador.

---

### User Story 4 — O candidato navega no arquivo (Priority: P2)

No computador ou no celular, o candidato vê o título do Edital na aba e salta de seção pelos
marcadores ou pelo sumário. O e-mail de dúvidas e os endereços escritos no texto são clicáveis, e o
arquivo baixado tem nome que identifica o Edital.

**Why this priority**: a navegação torna o documento longo consultável sem mudar uma palavra do ato.
Vem depois de P1 porque não muda o que o documento diz.

**Independent Test**: abrir o documento num leitor, conferir título, idioma, marcadores e links, e baixar
o publicado pelo endereço público.

**Acceptance Scenarios**:

1. **Given** o documento publicado, **When** é aberto, **Then** a janela mostra o título do Edital, e os
   marcadores listam as seções e subseções, em dois níveis.
2. **Given** um item do sumário, **When** é clicado, **Then** o leitor vai à seção.
3. **Given** o documento publicado, **When** é baixado, **Then** o arquivo tem nome com o número e o ano
   do Edital — e, no consolidado, com a data da Retificação.

---

### User Story 5 — A paginação não separa o que vai junto (Priority: P2)

As páginas não terminam com um título sozinho, nem partem uma linha de tabela. A tabela que continua na
página seguinte repete o cabeçalho. A frase que explica uma tabela fica junto dela, e a frase que
anuncia uma declaração fica junto da declaração. O fecho não fica sozinho numa página. Quando um bloco
é grande demais para ficar junto, ele se divide num ponto seguro, sem deixar página quase vazia.

**Why this priority**: é a continuidade da leitura. A amostra mostrou os dois erros possíveis — separar
demais e juntar demais — e a regra precisa equilibrá-los.

**Independent Test**: compor A, B e a variante de B, e varrer as páginas atrás dos defeitos listados no
FR-1390 e no FR-1391.

**Acceptance Scenarios**:

1. **Given** um cronograma de 18 linhas que não cabe numa página, **When** é composto, **Then** ele
   quebra entre linhas, com o cabeçalho repetido, e nenhuma linha se parte.
2. **Given** uma tabela de 16 linhas que cabe inteira numa página, **When** sobra pouco espaço na
   página corrente, **Then** ela não deixa uma linha só na página seguinte.
3. **Given** a última seção curta, **When** o fecho não cabe na página, **Then** a última seção e o fecho
   vão juntos, e nenhuma página contém só o fecho.

---

### User Story 6 — O que foi publicado não muda, e o resto do sistema também não (Priority: P1)

O Edital publicado antes desta feature continua com os mesmos bytes. A Retificação dele publica o
consolidado com a nova redação, tipografia e navegação, mas com a ordem e os títulos de seção do
original. O comprovante de inscrição e o documento de divulgação de resultado não mudam um byte.

**Why this priority**: o documento publicado é ato imutável. O comprovante publica o resumo do arquivo
e precisa conferir na segunda emissão (FR-063a).

**Independent Test**:

- servir um documento publicado antes e comparar os bytes;
- compor o consolidado de uma Retificação sobre um Edital publicado antes e conferir a ordem e os
  títulos;
- emitir o mesmo comprovante antes e depois e comparar os bytes.

**Acceptance Scenarios**:

1. **Given** um Edital publicado antes desta feature, **When** o documento é servido, **Then** os bytes
   são os gravados na publicação.
2. **Given** uma Retificação publicada depois desta feature, sobre esse Edital, **When** o consolidado é
   composto, **Then** ele usa a redação, a tipografia e a navegação novas, e as seções saem com a ordem,
   os títulos, a numeração e a divisão do snapshot original — sem resumo nem reunião de seções.
5. **Given** um ato de ordenação publicado antes desta feature, **When** a tela dele é exibida, **Then**
   a redação do desempate é a da publicação, e não a nova (FR-1397).
3. **Given** o mesmo comprovante de inscrição, **When** é emitido antes e depois desta feature, **Then**
   os bytes são idênticos.
4. **Given** o mesmo snapshot, **When** é composto duas vezes, **Then** os bytes são idênticos, e o hash
   do conteúdo não muda.

---

### Edge Cases

- **Edital de um Perfil só.** Sem "Em todos os Perfis", sem agrupamento, sem faixa de códigos; o
  resumo diz as vagas da localidade dele.
- **Todos os Perfis sem vaga imediata** (só cadastro de reserva). O resumo diz que não há vaga
  imediata e que há cadastro de reserva, sem explicar como a reserva se aplica (a pendência DP-05 e
  o RC-58 continuam abertos).
- **Lista de concorrência sem percentual** (PTT no cenário B). A tabela de reserva sai com "—" no
  percentual e o fundamento inteiro.
- **Códigos não contíguos** (TP-01, TP-03, TP-04). Saem enumerados, nunca como faixa.
- **Dois marcos no mesmo Perfil.** Cada um com as suas frases. A partilha parcial compara por marco, e
  as unidades do corte não se separam.
- **Método de sorteio próprio de um marco, diferente do comum.** Os dados de conferência do sorteio
  saem para cada método, inteiros, com o alcance dito.
- **Marco que declara não caber recurso.** A negativa sai ("Não caberá recurso contra o resultado de
  “…”"). Marco que nada declara não imprime frase de recurso — o silêncio não vira negativa.
- **Nome de marco sem gênero conhecido.** O resultado é citado entre aspas e sem artigo ("contra o
  resultado de “…”"), como decidiu a decisão 001 da `067`.
- **Texto livre que cita uma seção pelo título antigo** ("conforme o método publicado na seção Perfis de
  Vaga", no cenário A). O documento sai com o texto como está. A Revisão avisa que a seção foi
  repartida e lista os destinos possíveis — entre eles "Como será a seleção?", onde está o método do
  sorteio —, sem trocar o texto (FR-1400).
- **Termo interno escrito pelo Elaborador** ("conforme os marcos classificatórios do item 5"). Sai literal
  (FR-1395); a FR-1366 governa só a redação gerada.
- **Remissão gerada na apresentação plana.** "Marcos classificatórios: os descritos no item 5.6" passa a
  "Regras de classificação: as descritas no item 5.6" — o mesmo número e o mesmo destino (FR-1366,
  FR-1399).
- **Texto livre que repete uma regra gerada** ("Após o sorteio, serão analisados os documentos…").
  Sai como foi escrito; o sistema não apaga texto do Elaborador.
- **Texto livre que diverge do comportamento do sistema** (o sorteio condicionado). Sai como foi
  escrito; é o achado próprio, fora desta feature.
- **Requisito sem comprovante correspondente** (residência de TP-01 a TP-16, comprovante só de TP-01).
  O documento reproduz o que está declarado; é o achado próprio, fora desta feature.
- **Caractere sem grafia na fonte embutida.** Recusado na publicação, como hoje
  (`caractere_sem_grafia`). A prévia mostra o código, como hoje.
- **Prévia.** Tem a mesma composição do publicado — resumo, sumário, tipografia e marcadores —, com a
  marca de prévia, sem autoridade e sem integridade, como hoje.
- **Item de lista maior que uma página.** Pode se partir; é a única exceção à regra de item inteiro.
- **Sigla no título do Edital.** A sigla da Unidade e palavras com maiúscula depois de minúscula
  ("EaD") saem como escritas no anúncio em caixa alta.
- **Endereço eletrônico escrito no texto livre.** Vira link; o sistema não acrescenta endereço que o
  Elaborador não escreveu.

## Requirements *(mandatory)*

### Functional Requirements

#### Redação das frases geradas

- **FR-1360**: Toda frase que o sistema escreve no documento a partir do dado estruturado MUST ser
  reescrita na voz do candidato, conforme a tabela *Texto alvo das frases geradas*, abaixo. O plano
  completa a tabela com **todas** as variantes de cada regra que o compositor conhece. A amostra
  cobriu as dos cenários A e B; ficam por cobrir, por exemplo, a média ponderada, a normalização
  pela soma dos pesos, o truncamento, o meio para par, a habilitação por Etapa e o método próprio.
- **FR-1361**: Cada frase reescrita MUST preservar a condição, a exceção, o alcance e a consequência
  da frase que substitui. Nenhuma frase pode acrescentar condição que a norma declarada não tem, nem
  omitir uma que ela tem. A equivalência MUST ser demonstrada **por variante**, e não por amostra.
- **FR-1362**: A frase que explica os suplentes — "os suplentes são chamados, na ordem, para as vagas
  deste Edital que não forem preenchidas pelos primeiros classificados" — MUST sair só quando o marco
  prevê suplentes **e** nenhum Perfil do Edital tem cadastro de reserva. Com cadastro de reserva, ela
  não sai.
- **FR-1363**: A frase de recurso gerada MUST nomear o resultado de que se recorre, como hoje (o nome do
  marco entre aspas, sem artigo), e o prazo. Ela MUST NOT dizer o canal: o canal é o que o Elaborador
  escreve.
- **FR-1364**: Nos documentos e telas compostos depois desta feature, a mesma regra MUST ser dita pela
  mesma frase em todo lugar onde o sistema a diz: no documento, na prévia, na Revisão, no portal e no
  ato de ordenação. Não pode haver duas redações **novas** da mesma regra. O que já foi publicado
  segue o FR-1397.
- **FR-1365**: O Perfil MUST ser referido pelo **código** — impresso em toda tabela de Perfis — e a sua
  localidade pelo rótulo **Localidade**. O sistema MUST NOT escrever "polo", "turma" ou "curso" que
  não estejam no dado. Os títulos gerados são genéricos ("Quantas vagas há, e onde?"). Nenhum campo é
  acrescentado para isso.
- **FR-1366**: O documento MUST NOT conter os termos internos que a auditoria apontou:
  - "Marcos classificatórios", "recorte" e "inscrições submetidas";
  - os rótulos "Corte:", "Continuação:", "Normalização:", "Combinação:", "Habilitação:" e "Ordem:";
  - "valor declarado em";
  - o tipo de dado entre parênteses ("(número inteiro)", "(data)").

  A regra vale para **toda redação gerada pelo sistema**, nas duas apresentações: frases, rótulos, títulos
  de subseção e remissões. Na apresentação plana, os títulos e as remissões gerados que dizem "Marcos
  classificatórios" passam a dizer "Regras de classificação", e o número e o destino de cada um não
  mudam (FR-1399). O **texto livre** do Elaborador continua literal (FR-1395): um termo da lista que ele
  tenha escrito sai como foi escrito. A lista é verificada por teste sobre todo documento composto, nas
  duas apresentações, e só na parte gerada.

#### Organização

- **FR-1367**: As seções MUST seguir a ordem e os títulos do *Catálogo apresentado*, abaixo (o 3º),
  como padrão para todo Edital publicado depois desta feature. Só sai a seção que o Edital tem. As
  chaves das seções, e com elas a identidade do texto já escrito em rascunhos, MUST NOT mudar.
- **FR-1368**: As seções que respondem à mesma pergunta MUST sair reunidas sob ela, como subseções, cada
  uma com o seu texto:
  - **"Quem pode se inscrever?"** — público-alvo, requisitos gerais e os requisitos dos Perfis;
  - **"Como se inscrever?"** — a inscrição e o atendimento à pessoa com deficiência;
  - **"Como será a seleção?"** — os critérios de classificação, as regras de classificação dos marcos,
    os dados para conferir o sorteio, as Etapas e a verificação da autodeclaração.

  A numeração das seções e subseções MUST continuar calculada (065).
- **FR-1369**: Cada regra gerada MUST sair na seção que trata dela:
  - o recurso do marco, em "Como recorrer?";
  - a forma de convocação, em "Como será a convocação?";
  - os requisitos dos Perfis, em "Quem pode se inscrever?";
  - o período de inscrições, gerado do Evento marcado como inscrição, em "Como se inscrever?";
  - os dados que o candidato declara na inscrição, uma vez, em "Como se inscrever?" — com a indicação
    de que são usados no desempate, quando o são;
  - o lembrete do Requerimento de Matrícula, quando enviado no ato da inscrição, em "Quais documentos
    enviar?" e em "Como se inscrever?" (ED-18).
- **FR-1370**: O documento MUST abrir, depois do preâmbulo, com um **resumo** composto só de dado
  estruturado:
  - as vagas e as localidades;
  - o cadastro de reserva;
  - o período de inscrições;
  - o teto de inscrições;
  - a forma da seleção;
  - onde estão as datas.

  Cada linha MUST remeter ao item, e o resumo MUST declarar que repete o Edital e não substitui as
  seções.
- **FR-1371**: O resumo MUST usar palavras do candidato:
  - "N vagas em K localidades: …", com os nomes quando forem poucos;
  - "Cadastro de reserva" por extenso;
  - a seleção descrita pela forma — sorteio ou pontuação — e pela natureza das Etapas, sem reproduzir
    nome longo de Etapa. O nome curto pode ser usado; o nome completo fica na seção.

  O plano fixa o que é "poucas localidades" e "nome curto", sem campo novo.
- **FR-1372**: O documento MUST trazer um **sumário** das seções, com o número da página de cada uma.
- **FR-1373**: A seção de vagas MUST ser composta pelo dado:
  - **Todo Perfil com vaga imediata:** uma tabela única, Perfil × lista de concorrência × total, com
    linha de total.
  - **Senão:** as tabelas de Perfis e, à parte, a de vagas imediatas por lista dos Perfis que as têm.
  - **Perfis de mesmo nome:** saem numa tabela própria, com o nome na legenda.
  - **Tabela de reserva:** só as listas reservadas, com percentual e fundamento.
  - **Reversão:** a frase diz a que Perfis se aplica.
- **FR-1374**: O que é **igual em todos os Perfis** — nome, descrição, carga horária, remuneração,
  cadastro de reserva — MUST sair uma vez, numa frase "Em todos os Perfis: …", e deixar de ocupar coluna
  ou subseção por Perfil.
- **FR-1375**: Todo agrupamento MUST ser por **identidade** — do dado e da frase impressa —, nunca por
  semelhança. A partilha parcial MUST imprimir o que é comum uma vez e o que é de cada grupo depois.
  - **Unidades que não se separam:** o corte, o empate no corte, a explicação dos suplentes e a
    continuação são uma; os critérios de desempate de um marco são outra. Quando um elemento da unidade
    difere entre grupos, a unidade inteira sai em cada grupo.
  - **Faixa de códigos** ("TP-01 a TP-16"): só quando os códigos são contíguos e sem lacuna.
- **FR-1376**: Os dados que permitem conferir o sorteio — o método, o algoritmo, a fonte, o concurso e
  a data, como o concurso é escolhido, a semente e a substituição — MUST sair inteiros e sempre
  visíveis, num bloco destacado com frase de abertura. Saem uma vez quando o método é comum, e uma vez
  por método quando há método próprio (FR-465).
- **FR-1377**: O anúncio do ato MUST preservar, na caixa alta, a sigla da Unidade e as palavras com
  maiúscula depois de minúscula (ED-24).
- **FR-1378**: A descrição administrativa do Edital MUST NOT ser impressa no ato (ED-25). Ela continua
  no portal.
- **FR-1379**: A verificação de integridade MUST dizer "Autenticidade — este documento corresponde
  integralmente à versão homologada do Edital identificada abaixo" (L17), com os mesmos dados de hoje.

#### Tipografia

- **FR-1380**: O documento do Edital MUST embutir a fonte, regular e negrito, em subconjunto, de modo que
  a aparência não dependa do leitor.
  - A fonte MUST ter métricas compatíveis com as de hoje, para que a quebra de linha não mude de
    natureza.
  - A licença da versão **efetivamente distribuída** MUST ser verificada e registrada, e os arquivos
    dos dois estilos MUST acompanhar o sistema.
- **FR-1381**: O compositor MUST medir o texto do Edital com as larguras da fonte embutida, de modo que
  nenhuma linha justificada passe da margem. Isso inclui os caracteres hoje subestimados: "í", "ì", "î",
  "ï" e, no negrito, "ª" e "º".
- **FR-1382**: A hierarquia MUST ser:
  - título de seção em corpo maior, com fio abaixo;
  - subseção distinta do texto;
  - rótulos de grupo em negrito;
  - listas com recuo pendente (ED-16);
  - o resumo, os dados do sorteio e a declaração do Requerimento em bloco destacado de fundo claro.

  Nenhuma informação MUST depender de cor.
- **FR-1383**: O comprovante de inscrição, o documento de divulgação de resultado e qualquer outro
  documento composto pelo mesmo escritor MUST continuar byte a byte o mesmo. A fonte, a medição e a
  composição novas são do Edital.

#### Navegação

- **FR-1384**: O arquivo MUST declarar o título do Edital, para que a janela o mostre, e o idioma
  português do Brasil.
- **FR-1385**: O arquivo MUST trazer marcadores das seções e subseções, em dois níveis.
- **FR-1386**: Os itens do sumário MUST levar à seção correspondente. O e-mail e os endereços web
  escritos no texto MUST ser clicáveis. O sistema MUST NOT acrescentar endereço que o texto não tem.
- **FR-1387**: O documento publicado, ao ser baixado, MUST ter nome de arquivo com o número e o ano do
  Edital. O consolidado de uma Retificação MUST trazer também a data dela (ED-22).
- **FR-1388**: O documento MUST NOT ser apresentado como acessível nem como conforme a qualquer padrão
  de acessibilidade. Ele continua sem marcação para tecnologia assistiva, e essa limitação MUST ficar
  registrada na documentação da feature.

#### Paginação

- **FR-1389**: Nenhum título — de seção, de subseção, de grupo ou legenda de tabela — MUST terminar uma
  página sem pelo menos a primeira linha do conteúdo que ele anuncia.
- **FR-1390**: Nenhuma linha de tabela MUST se partir entre páginas. A tabela que continua na página
  seguinte MUST repetir o cabeçalho, e MUST NOT deixar na página seguinte uma linha só quando couber
  inteira na página.
- **FR-1391**: Blocos relacionados MUST ficar juntos quando couberem na página. São eles:
  - a tabela e a frase que a explica;
  - a frase que anuncia e o que ela anuncia;
  - um item de lista;
  - uma seção curta;
  - a última seção e o fecho.

  Bloco maior que o espaço MAY se dividir em ponto seguro: entre parágrafos, entre itens, entre
  linhas de tabela. Item de lista maior que uma página MAY se partir.
- **FR-1392**: A composição MUST equilibrar continuidade e espaço:
  - nenhuma página MUST conter só o fecho;
  - manter um bloco junto MUST NOT deixar mais de metade da área útil de uma página em branco quando
    ele puder ser dividido em ponto seguro.

  Os limites numéricos são do plano, e o número de páginas não é meta.

#### Integridade e não regressão

- **FR-1393**: O conteúdo **já submetido, homologado ou publicado** MUST manter o snapshot e o hash.
  - O Edital novo leva no snapshot os títulos e a ordem do *Catálogo apresentado*, que vêm do catálogo,
    como desde a `054`. Isso muda o snapshot de rascunhos ainda não submetidos, e é o que identifica a
    apresentação por perguntas (D-003).
  - O mesmo snapshot MUST produzir os mesmos bytes.
  - A prévia MUST compor como o publicado, com as diferenças de hoje: marca, sem autoridade, sem
    integridade.
- **FR-1394**: O documento já publicado MUST NOT ser regenerado.
  - Todo documento composto depois desta feature MUST usar a nova redação, tipografia e navegação.
  - O consolidado de Retificação sobre um Edital publicado antes MUST manter a **ordem, os títulos, a
    numeração e a divisão das seções** do original. Ele recebe só o que é compatível com essa
    estrutura: a redação das frases e dos rótulos gerados (inclusive "Regras de classificação" no lugar
    de "Marcos classificatórios", com o mesmo número e o mesmo destino), a tipografia e a navegação. A
    reunião de seções sob uma pergunta (FR-1368), a nova posição das regras geradas (FR-1369) e o
    resumo (FR-1370) são da apresentação por perguntas.
- **FR-1395**: O texto livre do Elaborador MUST sair como foi escrito. A feature MUST NOT inferir,
  corrigir, ampliar ou apagar regra — inclusive a que diverge do comportamento do sistema ou deixa
  requisito sem comprovante, que são achados próprios.
- **FR-1396**: A entrega MUST incluir, para os cenários A e B da auditoria e para a variante de B, a
  **conferência por enunciado**: cada regra do documento de hoje, com a sua forma no novo, e a
  classificação de cada uma — igual, reescrita com o mesmo efeito, movida, ou frase nova a aprovar. A
  conferência MUST ser refeita sobre o texto final, e não sobre a amostra.
- **FR-1397**: A redação de um ato **já publicado** MUST permanecer preservada e identificável onde quer
  que ele seja exibido. Isso vale para o documento do Edital, gravado em bytes, e também para o ato
  de ordenação e qualquer outra tela que hoje reconstrói a frase do vocabulário na hora de exibir. O
  portal e a Revisão MAY usar a redação nova para Editais publicados antes, desde que ela reflita a
  versão aplicável e não altere o que o ato publicado diz.
- **FR-1398**: Antes de mudar qualquer frase compartilhada, o plano MUST inventariar cada leitor do
  vocabulário e das frases do compositor e classificá-lo:
  - **congelado na publicação** — os bytes do documento e o texto gravado no ato;
  - **reconstruído na exibição** — a tela do ato de ordenação, o portal, a Revisão, os avisos.

  Para cada leitor reconstruído, o plano MUST dizer como o FR-1397 é cumprido.
- **FR-1399**: Nenhuma mudança desta feature MUST quebrar uma remissão numérica ("item 8.1") ou
  textual ("na seção Perfis de Vaga") de um documento publicado ou de um consolidado.
- **FR-1400**: Quando o texto livre de um Edital a publicar cita uma seção pelo título que ela não tem
  no documento — título do catálogo anterior, ou de seção que não sai —, a Revisão MUST mostrar um
  **aviso de conferência, não impeditivo**. O aviso:
  - traz o trecho encontrado;
  - pede ao Elaborador que confira o destino da remissão;
  - sugere a seção de destino **só** quando a matéria citada tem lugar único no documento novo;
  - quando a seção antiga foi repartida — "Perfis de Vaga" virou vagas em "Quantas vagas há, e
    onde?", requisitos em "Quem pode se inscrever?" e regras de classificação em "Como será a
    seleção?" —, diz que há dúvida e lista os destinos possíveis.

  O sistema MUST NOT reescrever o texto. A remissão numérica continua com o tratamento da `065`.

### Texto alvo das frases geradas

Ponto de partida, da amostra e da auditoria (L1–L17). O plano completa as variantes (FR-1360) e
registra a equivalência de cada uma (FR-1361).

| Regra | Hoje | Alvo |
|---|---|---|
| Separação por Perfil | "Os marcos abaixo se aplicam a cada um desses Perfis separadamente, sobre as inscrições do próprio Perfil: …" | "A classificação é feita separadamente em cada Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado." |
| Habilitação ao sorteio | "Habilitação: participam todas as inscrições submetidas" | "Participam do sorteio todas as inscrições enviadas." |
| Habilitação por Etapa | "participam apenas as inscrições habilitadas na Etapa X" | "Participam do sorteio só as inscrições habilitadas na Etapa “X”." |
| Corte pelo quadro | "Corte: Progridem para [Etapa] os primeiros desta ordem, até o número de vagas ofertadas no recorte, mais N suplentes." | "Passam para a Etapa “[Etapa]” os primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista, mais N (extenso) suplentes." |
| Corte fixo | "Corte: Progridem para [Etapa] os N primeiros desta ordem, mais M suplentes." | "Passam para a Etapa “[Etapa]” os N (extenso) primeiros classificados, mais M (extenso) suplentes." |
| Empate admite excedente | "Empate no corte: Havendo empate na última posição, progridem todos os empatados, ainda que excedam essa quantidade." | "Se houver empate na última posição, passam todos os empatados, mesmo que ultrapassem esse número." |
| Empate estrito (pontuação) | "Havendo empate na última posição, essa quantidade não é excedida." | "Se houver empate na última posição, esse número não é ultrapassado." |
| Continuação admitida | "Continuação: Poderá haver chamada, nesta ordem, além dos que este corte publicar." | "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem." — **sem** condição |
| Continuação vedada | "Não haverá chamada além dos que este corte publicar." | "Não serão chamados candidatos além desses." |
| Suplentes (só sem cadastro de reserva) | — | "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas pelos primeiros classificados." (frase nova, D-004) |
| Nota de uma Etapa | "Ordem: pela pontuação combinada das Etapas / Combinação: soma ponderada da Etapa X (peso 1) / Normalização: nenhuma" | "A nota final é a pontuação obtida na Etapa “X”." |
| Arredondamento | "Arredondamento: 2 casas decimais, meio para cima" | "A nota final é arredondada para 2 casas decimais; a partir da metade, arredonda-se para cima." |
| Desempate por data (menor) | "menor valor declarado em Data de nascimento; sem o valor, fica por último neste critério" | "data de nascimento mais antiga, informada na inscrição; quem não a informar fica em último lugar neste critério" — a forma genérica "«f» mais antiga", sem deduzir "idade" do rótulo |
| Desempate por número (maior) | "maior valor declarado em Meses de experiência…; sem o valor, fica por último neste critério" | "maior número de meses de experiência…, informado na inscrição; quem não o informar fica em último lugar neste critério" |
| Desempate pela Etapa | "maior pontuação na Etapa X; sem o valor, o critério não se aplica" | "maior pontuação na Etapa “X”; para quem não a tiver, o critério não se aplica" |
| Recurso | "Recurso: Caberá recurso contra o resultado de “X”, no prazo de N (extenso) dias corridos, contados da divulgação desse resultado." | "Contra o resultado de “X”: no prazo de N (extenso) dias corridos, contados da divulgação desse resultado." — em "Como recorrer?", sem canal |
| Recurso vedado | "Não caberá recurso contra o resultado de “X”." | idem, em "Como recorrer?" |
| Sorteio, abertura | bloco "Sorteio / Método / Algoritmo / Fonte / Ocorrência / Quando / Derivação / Semente / Se faltar" | "A ordem será definida a partir do resultado do [concurso] da [fonte], de [data]. Com os dados abaixo, qualquer pessoa pode refazer o sorteio e conferir o resultado." + Método · Qual concurso · Semente ("o número usado no sorteio: …") · Se faltar |
| Reversão por esgotamento | "Havendo ausência de candidatos aprovados na reserva de vagas, o quantitativo será destinado à respectiva ampla concorrência." | "Se não houver candidatos aprovados para as vagas reservadas de um código, essas vagas passam para a ampla concorrência do mesmo código." |
| Reversão por saldo | "Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não preenchido será destinado à respectiva ampla concorrência." | "As vagas reservadas de um código que não forem preenchidas passam para a ampla concorrência do mesmo código." |
| Convocação por publicação | "A convocação dos classificados será feita por publicação no endereço eletrônico do certame." | "A convocação dos classificados será feita por publicação." (o lugar é texto do Elaborador) |
| Convocação individual | "A convocação dos classificados será feita por mensagem individual à pessoa convocada." | "A convocação será feita por mensagem individual à pessoa convocada." |
| Teto | "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital." | "Cada candidato pode enviar apenas 1 (uma) inscrição neste Edital." |
| Dados declarados | "Dados exigidos na inscrição • Data de nascimento (data) • …" (por Perfil) | "Na inscrição, informe também: • a data de nascimento; • o número de …. Esses dados são usados no desempate (item N)." (uma vez) |
| Etapa decisória | "Caráter: eliminatória / Resultado: Deferida ou Indeferida / Realização: 17/11/2026, às 08h a 24/11/2026, às 17h" | "Etapa eliminatória: o resultado é “Deferida” ou “Indeferida”. Será feita de 17/11/2026, às 08h, a 24/11/2026, às 17h." |
| Etapa pontuada | "Caráter / Peso / Pontuação máxima / Avaliações por inscrição / Realização" | "Etapa classificatória, com pontuação máxima de 100 e peso 1. Cada inscrição recebe 1 (uma) avaliação. Será feita de … a …." |
| Período no Cronograma | Início e Término em colunas | "Quando": "de … a …" numa coluna |
| Grupo de documentos | "Dos candidatos concorrentes na modalidade X:" | "Também, de quem concorre às vagas para x (SIGLA):" |
| Integridade | "Verificação de integridade — este documento deriva integralmente…" | "Autenticidade — este documento corresponde integralmente…" |

A hora mantém dois dígitos ("às 08h"): é a paridade com o portal decidida em `humano.instante`, e a
L14 da auditoria a contrariava.

### Catálogo apresentado

O padrão inicial (o 3º). Cada linha diz de que seções do catálogo de hoje a seção vem. As chaves não
mudam (FR-1367).

| # | Título | Vem de |
|---|---|---|
| — | (preâmbulo, sem número) | `apresentacao` |
| — | Resumo deste Edital; Sumário (sem número) | gerados (FR-1370, FR-1372) |
| 1 | Disposições preliminares | `disposicoes-preliminares` |
| 2 | Informações gerais | `informacoes-gerais` |
| 3 | Quem pode se inscrever? | `publico-alvo`, `requisitos-gerais` e os requisitos dos Perfis |
| 4 | Quantas vagas há, e onde? | `perfis` (vagas, reserva, reversão, atributos comuns, atribuições) |
| 5 | Cronograma | `cronograma` |
| 6 | Como se inscrever? | `inscricao`, `atendimento-pcd` (subseção), período, dados declarados, teto |
| 7 | Quais documentos enviar? | `documentos-exigidos` |
| 8 | Como será a seleção? | `classificacao`, regras dos marcos, dados do sorteio, `etapas`, `verificacao-autodeclaracao` |
| 9 | Como recorrer? | `recursos` e o recurso de cada marco |
| 10 | Como será a convocação? | `convocacao` e a forma de convocação |
| 11 | Como será a matrícula? | `matricula`, `acesso-ao-curso`, `homologacao-matricula`, o Requerimento |
| 12 | Certificado | `certificado` |
| 13 | Prazo de validade | `prazo-de-validade` |
| 14 | Anexos | `anexos` |
| 15 | Disposições finais | `disposicoes-finais`, seguidas do fecho |

O número de cada seção é o calculado sobre as que existem: um Edital sem certificado não tem a seção
12, e as seguintes sobem.

### Key Entities

- **Snapshot homologado**: o conteúdo canônico do Edital. É a única fonte do documento, e não muda.
- **Apresentação**: a forma como o documento organiza as seções. Há duas, e são estes os nomes usados
  em todos os artefatos:
  - **apresentação por perguntas** — a estrutura nova, do *Catálogo apresentado*, dos Editais cujo
    snapshot traz o catálogo desta feature;
  - **apresentação plana** — a estrutura do original, de hoje, dos Editais publicados antes e dos
    consolidados deles.

  As duas usam a redação 2, a fonte, a hierarquia, a paginação e a navegação.
- **Seção apresentada**: a seção do documento, com título e posição do *Catálogo apresentado*.
  Agrupa seções do catálogo de hoje sem mudar as suas chaves. Nos Editais publicados antes, ordem e
  título vêm do snapshot original.
- **Frase gerada**: o texto que o sistema escreve a partir de um valor declarado. Tem uma redação só,
  compartilhada entre o documento, a prévia, a Revisão e o ato de ordenação.
- **Grupo de Perfis**: os Perfis que têm o mesmo valor ou a mesma frase impressa. Tem código, faixa
  quando contígua, e a parte comum e a própria.
- **Fonte embutida**: os arquivos regular e negrito, com a licença registrada e as larguras que o
  compositor usa para medir o Edital.
- **Versão da redação**: o conjunto de frases com que um documento foi composto. É registrada na
  Publicação e lida por quem exibe um ato publicado, para mostrar a redação dele (FR-1397).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-516**: Nos cenários A e B da auditoria, **100%** dos fatos do documento de hoje — datas, horas,
  números com extenso, percentuais, documentos, fundamentos, códigos, localidades, anexos, e-mail e
  hash — estão no documento novo.
- **SC-517**: Na conferência por enunciado de A, B e da variante de B, **nenhuma** regra é acrescentada,
  retirada ou tem condição, exceção, alcance ou consequência mudada. Toda frase nova é aprovada pelo
  responsável pelo produto antes da publicação do primeiro Edital real.
- **SC-518**: **Zero** ocorrências dos termos internos do FR-1366 na redação gerada de todo documento
  composto nos testes, nas duas apresentações. Na plana, as remissões geradas trocadas apontam para o
  mesmo número de antes.
- **SC-519**: A mesma página, renderizada por três motores diferentes, tem os títulos em negrito e as
  mesmas quebras de linha nos três. **Nenhuma** linha justificada passa da margem direita.
- **SC-520**: **100%** das seções estão no sumário e nos marcadores, e o número de página de cada item
  do sumário é o da página em que a seção começa.
- **SC-521**: Em A, B e na variante: **zero** títulos órfãos, **zero** linhas de tabela partidas,
  **zero** continuações de tabela sem cabeçalho, **zero** páginas só com o fecho e **zero** tabelas
  que caberiam inteiras deixando uma linha só na página seguinte.
- **SC-522**: O comprovante de inscrição e o documento de divulgação de resultado são **byte a byte**
  idênticos antes e depois desta feature, para o mesmo conteúdo.
- **SC-523**: O mesmo snapshot composto duas vezes produz **os mesmos bytes**. O hash do conteúdo de
  todo Edital já submetido, homologado ou publicado é o mesmo de antes.
- **SC-524**: Em B, a tabela de Perfis não repete o nome comum aos Perfis do grupo: o nome sai **uma**
  vez por grupo, e os atributos iguais em todos os Perfis saem **uma** vez no documento.

**Demonstração pelo canal dos atores** (Constituição, Princípio VI): a entrega inclui a jornada pelo
navegador. O Elaborador compõe e confere a prévia, vê o aviso de remissão na Revisão, e o Edital é
homologado e publicado pela interface. O candidato baixa o documento pelo portal, conferindo o nome do
arquivo. A página do ato de ordenação é aberta. As evidências ficam em `demonstracao/jornada/`; os
roteiros de comandos medem, mas não substituem essa demonstração.

### O que esta feature não cobre, deliberadamente

- **Acessibilidade completa.** O documento continua sem marcação (`Tagged: no`). Título, idioma,
  marcadores, links e fonte embutida são recursos estruturais favoráveis, e não conformidade
  (FR-1388).
- **O endereço do certame gerado.** Domínio congelado na publicação e rota legível são outra feature.
- **O teste com candidatos.** É validação do piloto (Lei nº 15.263/2025, art. 5º, XVIII), feita com o
  primeiro Edital real composto por esta feature, e não condição de entrega.
- **Os dois achados herdados**, a Retificação que diz o que mudou, o tipo do Evento, o portal, HTML,
  Libras e LLM.

## Decisões

Fechadas pelo responsável pelo produto em 12/10/2026, na terceira rodada da análise, salvo onde dito.

### D-001 — A ordem e os títulos da amostra são o padrão inicial

A ordem do *Catálogo apresentado* e os seus títulos — em pergunta onde ajudam, diretos onde funcionam
melhor — passam a ser o padrão do documento, adaptado às seções que cada Edital tem (o 3º). As chaves
não mudam. Mudar o catálogo depois da primeira publicação real deixa o acervo com duas formas de
documento; é o preço aceito, e a razão de fazê-lo cedo no piloto.

### D-002 — Fonte embutida, com a licença da versão distribuída verificada

O documento do Edital embute uma fonte de métricas compatíveis com as de hoje, regular e negrito (o
4º). A amostra usou a Liberation Sans 1.07.4, de licença GPL com exceção para fontes. A série 2.x é
OFL 1.1. O plano escolhe a versão, verifica a licença do arquivo que vai ser distribuído e o inclui no
sistema com o texto da licença.

### D-003 — Editais publicados antes mantêm a estrutura do original

Decidido pelo responsável pelo produto no clarify de 12/10/2026 (opção A, com ressalvas). O consolidado
de uma Retificação composto depois desta feature, sobre um Edital publicado antes, mantém a **ordem,
os títulos, a numeração e a divisão das seções** do original, que o snapshot guarda (decisão 003 da
`054`). Ele ganha só o que é compatível com essa estrutura: a redação das frases geradas, a tipografia
e a navegação. Assim as remissões do texto livre continuam certas sem manter dois compositores
completos.

**A redação histórica é preservada onde o ato publicado é exibido** (FR-1397). O módulo de frases é
compartilhado com telas que as reconstroem na exibição, e o plano começa pelo inventário do FR-1398.

### D-004 — A frase que explica os suplentes é nova e condicionada

Ela descreve a regra do sistema — suplente só é chamado para vaga imediata não preenchida — e torna
compreensível "não há cadastro de reserva" ao lado de "mais 15 suplentes". Com cadastro de reserva, a
relação entre suplentes e cadastro é a pendência DP-05, e o documento não a explica (FR-1362). Por ser
frase nova num ato, depende da aprovação do SC-517.

### D-005 — O resumo é derivado e não substitui as seções

O resumo dentro do ato só repete dado estruturado e remete ao item. A análise registrou que o estatuto
de um resumo dentro do ato deve ser confirmado pela área jurídica. A estrutura aprovada o inclui, e a
confirmação não bloqueia o plano.

### D-006 — O desempate por data usa sempre a forma genérica

Decidido pelo responsável pelo produto na análise dos artefatos, em 12/10/2026. A frase do desempate
por data diz "«f» mais antiga" ou "«f» mais recente, informada na inscrição", com o nome do fato em
minúscula: "data de nascimento mais antiga, informada na inscrição". O sistema **não** deduz "maior
idade" ou "menor idade" comparando o rótulo do fato com "Data de nascimento". Um rótulo é texto do
Elaborador, e a dedução trocaria a regra declarada por outra que o sistema supõe equivalente. Fica nas
frases T1 e T2 do contrato de redação.

### D-007 — Na apresentação plana, os rótulos gerados dizem "Regras de classificação"

Decidido pelo responsável pelo produto na análise dos artefatos, em 12/10/2026. A FR-1366 vale para
toda redação gerada, também no consolidado de Edital publicado antes. Por isso, os títulos e as
remissões que o sistema gera com "Marcos classificatórios" passam a dizer "Regras de classificação",
com **o mesmo número e o mesmo destino** (FR-1399), nas frases G1 a G3 do contrato de redação. A troca
alcança só o rótulo gerado. O texto livre do Elaborador continua literal (FR-1395), e as remissões que
ele escreveu continuam apontando para o mesmo item.

## Assumptions

- O compositor atual comporta a feature: a amostra foi composta com as primitivas dele, mais seis
  extensões pequenas — caixa de fundo, recuo pendente, sumário por duas passadas, metadados e
  marcadores, fonte embutida, medição pela fonte.
- O subconjunto da fonte cobre todos os caracteres que a grafia do Edital admite. Ele é fixo, e não
  depende do documento; por isso pode ser gerado uma vez e distribuído pronto.
- O ato de ordenação e a Revisão já leem as frases do mesmo módulo que o documento. Reescrevê-las ali
  muda os três de uma vez, e é o que se quer (FR-1364).
- **Subtítulo dentro de uma seção textual** ("Sobre o curso", "Sobre a função") é texto do Elaborador.
  As seções textuais não têm marcação de título, e o lote não a cria. Se o subtítulo precisar sair
  com hierarquia própria, isso é outra decisão, parente do ED-20 (tabelas nas seções textuais).
- A amostra (`proposta.py`) é evidência, e não implementação. Ela não reflete ainda os ajustes 5º e 6º,
  e o plano não a reusa como código.
- **Nenhum campo novo no Edital, nenhum dado reescrito.** Duas mudanças persistentes são consequência
  das decisões, e não escopo próprio:
  - o snapshot dos Editais **novos** leva os títulos e a ordem do catálogo novo;
  - a `Publicacao` passa a registrar a **versão da redação** com que o documento foi composto, como
    registra a Unidade e o signatário (060). As publicações anteriores ficam com a primeira versão, e é
    isso que torna a redação histórica identificável (FR-1397).
- **Edital submetido ou homologado antes da implantação e publicado depois** volta à elaboração: a
  publicação refaz o snapshot, que agora traz os títulos novos, e recusa a diferença com o homologado
  (`homologated_revision_changed`). Foi o custo aceito na decisão 003 da `054`. Ele tem uma vantagem: o
  Homologador vê a redação nova antes de homologar de novo.
