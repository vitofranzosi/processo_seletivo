# Feature Specification: Relatório consolidado da unidade — um conjunto de Editais, num documento

**Feature Branch**: `claude/relatorio-consolidado-gps-b036c0`, sobre a `main` em `50badd38`

**Created**: 2026-10-24

**Status**: Draft — desenvolvimento autorizado pelo usuário em 24/10/2026 para o MVP; merge e
disponibilização em produção **não** autorizados.

**Input**: autorização do usuário de 24/10/2026 — *"A proposta de Relatório Consolidado de Gestão dos
Processos Seletivos foi avaliada e está aprovada conceitualmente como referência para o MVP"* —, com
escopo funcional, sete refinamentos obrigatórios e dez frentes de teste. A investigação que precede
esta spec está em
[`doc/estudo-relatorio-consolidado-de-gestao-2026-10-24.md`](../../doc/estudo-relatorio-consolidado-de-gestao-2026-10-24.md)
e na [maquete](../../doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/maquete.pdf).

> **Faixa de identificadores.** Esta spec abre em **FR-2554** e **SC-939**. Teto medido em 24/10/2026
> em `specs/` de **todas as worktrees desta máquina** e na `main`: `FR-2553`, `SC-938`, `UX-222`, da
> `099`. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-2524 da `099`"); decisão de outra feature, pelo assunto e pela feature, porque `D-` aqui é só
> desta.

---

## Por que esta feature existe

**A unidade responde pelo conjunto, e o GPS só descreve um Edital por vez.** A Visão Geral (`040`)
reúne os Editais do escopo e diz oferta e procura; o relatório do Edital (`099`) diz, de um Edital,
o que saiu e o que falta. Ninguém junta os dois: o balanço de um semestre exige abrir cada relatório
individual e somar à mão — e a soma à mão é onde a inscrição vira "candidato", a vaga reservada é
contada duas vezes e o Edital cancelado entra no denominador.

**Os números existem, e as regras também.** Vagas, inscrições e razão são da `040`; resultado,
apuração, convocação, recurso, pendência e espécie são da `099`. O que falta é somá-los com regras
escritas, sobre um conjunto que se diz por extenso, num instante só.

**E a `099` precisa de duas correções antes de servir de base.** O estudo encontrou que um número
omitido por privacidade volta por subtração entre o total do Edital e as linhas dos outros Perfis, e
que um Perfil sem nenhuma inscrição gera uma pendência de resultado que nunca se cumpre — o Edital
dele nunca chegaria a "relatório de encerramento". As duas correções são desta feature, por
autorização do usuário.

### O que existe e é reaproveitado

| Peça | Onde |
|---|---|
| Editais do escopo, ano do número, busca, vagas do conteúdo vigente, contagens por Edital e Perfil, razão recortada | `interface/visao_geral.py` (`040`) |
| Resultado, apuração, convocação, recurso, pendências, espécie, registros posteriores | `interface/relatorio_do_edital.py`, `interface/relatorio_trilha.py` (`099`) |
| Instante único (`REPEATABLE READ`), emissão numerada e auditada com resumo, documento determinístico | `interface/relatorio_do_edital.py`, `interface/relatorio.py`, `interface/relatorio_pdf.py` (`099`) |
| Primeira publicação de cada Edital | `publicacoes.Publicacao` (`publication_order = 1`) |
| Desfecho e data do ato | `processos/application/selectors.py` (`desfechos`) |
| Capacidade de ler o panorama institucional | `visao:consultar` (`040`) |
| Motor de PDF determinístico, com links e marcadores | `publicacoes/infrastructure/pdf.py` |

### O que esta spec cobre, e o que fica fora

| Cobre | Fora |
|---|---|
| Conjunto por primeira publicação ou por ano do número, com atalhos de ano e semestre, e escolha manual | Visão de atividades do período (atos contados pela data em que ocorreram) |
| Página de gestão com a camada executiva; PDF com camada executiva e anexo técnico | Comparação entre unidades; escopo acima da unidade; papel novo |
| Números somados da derivação por Edital da `099`, sem regra replicada | Taxonomia de curso, programa, polo ou tipo de processo; somas por modalidade entre Editais |
| Emissão auditada, numerada por unidade, com o conjunto e o resumo do arquivo | Guarda dos bytes; envio periódico; CSV; painel |
| Separação, na `099`, entre fatos e redação, com o PDF individual inalterado | Mudança de regra de negócio dos processos seletivos |
| Duas correções da `099`: supressão complementar e Perfil sem inscrição | Texto por modelo de linguagem; juízo, causa, previsão ou recomendação |

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O balanço do semestre num documento (Priority: P1) 🎯 MVP

A gestão da unidade abre a Visão Geral, pede o relatório consolidado, escolhe "1º semestre de 2026"
e vê quais Editais entram. A página mostra a camada executiva do conjunto; ela baixa o PDF e o envia
à direção, que lê, numa página, quantos Editais, o que foi oferecido, quanta procura houve, o que
saiu e o que ainda está em curso.

**Why this priority**: é o valor aprovado; sem ela, a feature não existe.

**Independent Test**: com um cenário de vários Editais publicados em datas conhecidas, escolher o
semestre, conferir a relação dos Editais incluídos e os números da camada executiva contra a soma dos
relatórios individuais, e baixar o PDF.

**Acceptance Scenarios**:

1. **Given** Editais publicados no 1º e no 2º semestre, **When** a gestão escolhe o 1º semestre,
   **Then** só os publicados pela primeira vez entre 01/01 e 30/06 entram, e a página diz quantos e
   quais.
2. **Given** o conjunto escolhido, **When** a página é aberta, **Then** ela mostra a ficha do conjunto,
   as duas situações, a visão geral, os seis números com a base escrita e os pontos de atenção, e
   oferece "Baixar PDF".
3. **Given** a página, **When** a gestão baixa o PDF, **Then** o arquivo traz a camada executiva nas
   primeiras páginas e o anexo técnico depois, com o conjunto e o instante dos dados em toda página.

---

### User Story 2 — Saber exatamente o que foi analisado, e de quando são os dados (Priority: P1)

Quem lê entende que o período **escolheu os Editais**, e que os números são de cada Edital **no dia
da emissão**: um relatório do 1º semestre emitido em outubro mostra convocações de setembro.

**Why this priority**: é o primeiro refinamento obrigatório, e sem ele o documento é lido errado.

**Independent Test**: emitir o relatório de um semestre já encerrado com um ato registrado depois do
fim do semestre, e conferir que o ato aparece, e que a ficha e o anexo dizem por quê.

**Acceptance Scenarios**:

1. **Given** um conjunto escolhido pelo 1º semestre, **When** o relatório é lido, **Then** a ficha diz
   "Editais com primeira publicação entre 01/01/2026 e 30/06/2026" e "a situação de cada Edital é a de
   DD/MM/AAAA, HHhMM", e não a do fim do semestre.
2. **Given** inscrições enviadas em julho a um Edital publicado em junho, **When** o relatório do 1º
   semestre mostra os envios por mês, **Then** julho aparece, e o título não diz "no semestre".
3. **Given** um Edital de número 48/2025 publicado em 08/01/2026, **When** o critério é a primeira
   publicação em 2026, **Then** ele entra; **When** o critério é o ano do número 2026, **Then** ele
   não entra; e o anexo diz qual critério foi usado.

---

### User Story 3 — Escolher os Editais à mão (Priority: P2)

Um responsável quer o balanço de cinco Editais específicos — os de um curso, por exemplo. Ele parte
do critério, retira os que não quer, ou escolhe a lista inteira à mão entre os Editais da unidade.

**Why this priority**: cobre o coordenador de curso sem inventar entidade de curso.

**Independent Test**: escolher cinco Editais à mão, emitir, e conferir que só eles entram e que o
relatório diz que a escolha foi manual.

**Acceptance Scenarios**:

1. **Given** o conjunto de um critério, **When** a gestão desmarca dois Editais, **Then** o relatório
   os deixa fora e o anexo diz quais foram retirados.
2. **Given** a escolha manual, **When** a gestão marca cinco Editais de anos diferentes, **Then** o
   relatório traz os cinco, e a ficha diz "cinco Editais escolhidos".
3. **Given** um identificador de Edital de outra unidade enviado no formulário, **When** o relatório é
   gerado, **Then** ele é ignorado como inexistente.

---

### User Story 4 — Ver o que ainda está em curso no conjunto (Priority: P2)

A direção quer saber onde agir: quantos Editais encerrados ainda têm providência, de que tipo, e em
quais Editais.

**Why this priority**: é o que distingue o balanço gerencial de uma soma de números.

**Independent Test**: num conjunto com convocação aguardando resposta, recurso pendente e resultado
só preliminar, conferir a contagem por tipo e a lista por Edital.

**Acceptance Scenarios**:

1. **Given** dois Editais encerrados com convocação no prazo, **When** o relatório é gerado, **Then** o
   primeiro ponto de atenção diz "2 Editais estão encerrados no GPS, mas ainda têm providência
   registrada", e a seção de providências os lista com o tipo.
2. **Given** um Edital com um Perfil sem nenhuma inscrição e período encerrado, **When** o relatório é
   gerado, **Then** o marco daquele Perfil não é pendência, e diz "não se aplica: nenhuma inscrição
   enviada".

---

### User Story 5 — Emissão rastreável e privacidade preservada (Priority: P2)

Cada PDF baixado fica registrado com o conjunto e o resumo do arquivo; e nenhum número do documento
permite descobrir fato não público de um grupo pequeno, nem por subtração.

**Why this priority**: o PDF sai do sistema; sem rastro e sem guarda-corpo, não pode circular.

**Independent Test**: baixar duas vezes e conferir dois eventos; montar um Edital com um Perfil de
três inscrições e conferir que nenhuma conta entre os números mostrados recupera o fato omitido.

**Acceptance Scenarios**:

1. **Given** a primeira emissão da unidade, **When** o PDF é baixado, **Then** a trilha ganha um evento
   com o critério, os Editais, o instante e o resumo, e o documento diz "emissão nº 1".
2. **Given** um Edital de dois Perfis, um com três inscrições, **When** o relatório do Edital é
   gerado, **Then** os fatos não públicos dos **dois** Perfis são omitidos, e o total do Edital
   continua dito.
3. **Given** um Edital com quatro inscrições enviadas no conjunto, **When** o consolidado é gerado com
   e sem ele, **Then** os números não públicos das duas emissões são iguais, e a base diz que um
   Edital ficou fora deles.

---

### Edge Cases

- **Conjunto vazio.** A página diz o critério e que nenhum Edital o satisfaz; não há botão de emissão,
  e o envio direto é recusado.
- **Edital em elaboração, em revisão ou homologado.** Não entra: não há fato público antes da
  publicação. A relação diz quantos do critério ficaram fora por isso.
- **Edital cancelado.** Entra na relação e na contagem de Editais, com a espécie *de interrupção*, e
  fica fora de **todo** número, tabela e série; cada base diz "fora o Edital cancelado" quando houver.
- **Conjunto só de cancelados.** Os números dizem "não se aplica: todos os Editais do conjunto foram
  cancelados".
- **Edital com período de inscrições aberto.** Inscrições e razão marcadas *parcial*; resultados
  "ainda não disponível".
- **Perfil só de cadastro de reserva.** Fora do numerador e do denominador da razão; contado como
  Perfil só de cadastro de reserva; nunca 0 nem infinito.
- **Mesma inscrição em ampla e reservada.** Conta uma vez no Edital; a soma entre Editais é soma de
  inscrições distintas por Edital.
- **Resultado preliminar sucedido pelo definitivo.** Conta só o vigente.
- **Registros depois do encerramento.** Contados como registros da trilha de auditoria, sem dizer que
  a trilha é completa.
- **Edital com menos de cinco inscrições enviadas.** O relatório individual dele omite os totais não
  públicos; no consolidado, ele não contribui com fato não público a número nenhum, e as bases dizem
  quantos Editais ficaram fora por isso. Vagas, inscrições e razão continuam a contá-lo.
- **Perfil pequeno num Edital grande.** O relatório do Edital omite o detalhe do Perfil e, se os
  omitidos não chegam a cinco inscrições, também o do Perfil de menor procura seguinte; os totais do
  Edital continuam ditos.
- **Conjunto acima do limite.** A emissão é recusada com o limite dito e o tamanho do conjunto.
- **Registro gravado durante a leitura.** A leitura inteira vê o banco num instante só; o registro
  entra na emissão seguinte.
- **Duas emissões simultâneas.** Recebem números diferentes.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Acesso

- **FR-2554**: A Visão Geral MUST oferecer o "Relatório consolidado" a quem tem a capacidade de
  consultar a visão institucional (`040`), e a página do relatório MUST recusar quem não a tem, com a
  recusa explicada da `033`.
- **FR-2555**: O conjunto MUST conter só Editais do escopo do ator. Identificador de Edital de outro
  escopo, ou inexistente, enviado no formulário MUST ser ignorado, sem distinção entre os dois.
- **FR-2556**: A página e o PDF MUST ser respostas privadas, sem armazenamento em cache compartilhado.

#### Conjunto

- **FR-2557**: O critério do conjunto MUST ser um de três: **primeira publicação** entre duas datas;
  **ano do número** do Edital; **escolha manual** entre os Editais do escopo. O padrão MUST ser a
  primeira publicação no ano corrente.
- **FR-2558**: O critério de primeira publicação MUST oferecer atalhos para o ano, o 1º semestre e o
  2º semestre, além de datas livres, e MUST usar a data da primeira publicação do Edital no GPS, e não
  a das Retificações.
- **FR-2559**: A página MUST listar os Editais que o critério alcança, marcados para entrar, e MUST
  permitir desmarcá-los; na escolha manual, MUST listar os Editais do escopo, com busca por número,
  título e Processo, para marcar.
- **FR-2560**: Só Editais publicados, encerrados ou cancelados MUST entrar. Os demais Editais que o
  critério alcança MUST ser contados como fora do conjunto, com o motivo.
- **FR-2561**: O relatório MUST dizer o critério por extenso, as datas ou o ano, e — quando houve
  escolha — os Editais retirados do critério ou a escolha manual inteira.
- **FR-2562**: Conjunto vazio MUST NOT ser emitido, e a página MUST dizer por quê.
- **FR-2563**: Conjunto acima do limite de Editais por emissão MUST ser recusado com o limite e o
  tamanho dito.

#### Instante e emissão

- **FR-2564**: A leitura do conjunto inteiro MUST ver os dados de um instante só, e esse instante MUST
  aparecer como "dados até DD/MM/AAAA, HHhMM" no topo da página e em toda página do PDF.
- **FR-2565**: O relatório MUST dizer, na ficha e no anexo, que o critério escolhe os Editais e que a
  situação de cada um é a do instante dos dados, e não a do fim do período. Ele MUST NOT reconstituir
  estado passado.
- **FR-2566**: Baixar o PDF MUST ser um envio de formulário. Cada emissão MUST gravar um evento de
  auditoria na unidade do ator com o critério, os Editais incluídos, os retirados e os fora do
  conjunto, o instante, o ator, o número da emissão e o resumo SHA-256 dos bytes entregues.
- **FR-2567**: O número da emissão MUST ser a quantidade de emissões consolidadas anteriores da unidade
  mais um, e emissões simultâneas MUST receber números diferentes. O documento MUST dizer o número.
- **FR-2568**: Mesmos fatos, mesmo conjunto e mesmo instante MUST produzir o mesmo documento, byte a
  byte.

#### Uma derivação, sem regra replicada

- **FR-2569**: Cada número de resultado, apuração, convocação, recurso, pendência, espécie e registro
  posterior MUST vir da derivação por Edital da `099`. O consolidado MUST NOT reimplementar regra de
  pendência, espécie, vigência, vaga, razão ou ausência.
- **FR-2570**: A derivação da `099` MUST expor os fatos de cada Edital — números por Perfil,
  pendências como tipos com quantidade, espécie — separados da redação; o relatório do Edital MUST
  continuar a produzir o mesmo documento, byte a byte, para os mesmos fatos e instante.

#### Universos

- **FR-2571**: Todo número, tabela e série do consolidado MUST ser calculado sobre o mesmo universo:
  os Editais do conjunto que não foram cancelados. O Edital cancelado MUST aparecer só na contagem de
  Editais, na situação e na relação, e cada base afetada MUST dizê-lo.
- **FR-2572**: Inscrições por vaga MUST ser a soma das inscrições enviadas nos Perfis com vaga imediata
  dividida pela soma dessas vagas, com uma casa; MUST NOT ser média de razões; MUST ser marcada parcial
  quando algum Edital do universo tiver período de inscrições aberto.

#### Camada executiva

- **FR-2573**: A camada executiva MUST trazer: a ficha do conjunto (critério, unidade, instante,
  situação no GPS e situação das providências), a visão geral factual, seis números com a base escrita
  e os pontos de atenção.
- **FR-2574**: Os seis números MUST ser: vagas imediatas; inscrições enviadas; inscrições por vaga;
  Editais com todos os resultados definitivos, sobre os Editais com resultado previsto; vagas com
  inscrição classificada e habilitada, sobre as vagas apuradas; convocações aceitas, sobre as
  realizadas.
- **FR-2575**: A visão geral MUST ser composta só de frases cuja condição é verdadeira no instante dos
  dados, e MUST NOT conter juízo, causa, previsão, recomendação nem comparação de desempenho entre
  Editais.
- **FR-2576**: Os pontos de atenção MUST ser no máximo três, nesta ordem: Editais encerrados com
  providência registrada; Editais com registros na trilha depois do encerramento; ausência de
  matrícula no GPS.

#### Seções

- **FR-2577**: **Oferta e procura** MUST trazer as vagas imediatas desdobradas em ampla concorrência e
  listas reservadas só no total, os Perfis só de cadastro de reserva, as inscrições enviadas por mês do
  envio, a tabela por Edital (vagas, inscrições, inscrições por vaga) sem ordenação por razão, e os
  Perfis com procura menor que a oferta, sem causa.
- **FR-2578**: O título da série de envios MUST dizer que ela é por mês do envio, e a nota MUST dizer
  que os meses podem passar do período que escolheu os Editais.
- **FR-2579**: **Execução e resultados** MUST trazer os Editais por espécie, as Retificações publicadas,
  os Editais com prazo de inscrição prorrogado, os recursos por situação, os resultados previstos e
  vigentes, as vagas por situação de apuração e as convocações pela cadeia. MUST NOT trazer taxa de
  deferimento, taxa de aceite nem cumprimento de cronograma.
- **FR-2580**: **Providências** MUST contar as pendências por tipo, com quantos Editais e quantas
  ocorrências, e listá-las por Edital.
- **FR-2581**: Os registros depois do encerramento MUST ser ditos como registros da trilha de
  auditoria do GPS, por Edital, e o texto MUST dizer que a contagem cobre os atos que a trilha
  registra, e não todo acontecimento. O relatório do Edital (`099`) MUST dizê-los do mesmo modo.

#### Anexo técnico

- **FR-2582**: O anexo MUST trazer a relação dos Editais do conjunto — número/ano, título, primeira
  publicação, situação no GPS, espécie e o endereço público da página da seleção —, os Editais fora do
  conjunto com o motivo, o critério, a definição de cada número (fonte, unidade de contagem, regra de
  soma, limitação), o que o GPS não registra, e os dados da emissão.

#### Vocabulário

- **FR-2583**: O relatório MUST distinguir inscrição, cadastro de candidato, inscrição classificada,
  convocação, convocação aceita e matrícula, e MUST NOT dizer "candidatos por vaga", "pessoas",
  "aprovado", "vaga ocupada", "vaga preenchida" nem "matriculados". Matrícula MUST aparecer só como
  fato não registrado pelo GPS.
- **FR-2584**: Ausência MUST ser grafada como na `040` e na `099`, e zero só quando a fonte produziu
  zero.

#### Privacidade

- **FR-2585**: O relatório MUST NOT conter nome, CPF, e-mail, telefone, protocolo ou identificador de
  candidato.
- **FR-2586**: Fatos não públicos — eliminação, ocorrência, recurso, convocação, apuração, rascunho —
  MUST aparecer no consolidado só no total do universo e por Edital, nunca por Perfil ou por lista.
- **FR-2587**: No relatório do Edital, um Perfil com menos de cinco inscrições enviadas MUST ter os
  fatos não públicos omitidos com o motivo, e continuar nos totais do Edital. Quando os Perfis
  omitidos somarem menos de cinco inscrições enviadas, MUST ser omitido também o Perfil de menor
  procura entre os demais, e assim por diante, até que somem cinco; se nem todos juntos chegarem a
  cinco, os totais não públicos do Edital MUST ser omitidos.
- **FR-2588**: A regra da FR-2587 MUST substituir, no relatório do Edital (`099`), a regra de Perfil
  único da FR-2551 da `099`.
- **FR-2592**: No consolidado, o Edital cujo relatório individual omite os totais não públicos MUST
  NOT contribuir com fato não público a número nenhum — nem por Edital, nem no total —, e cada base
  afetada MUST dizer quantos Editais ficaram fora por isso. O consolidado MUST NOT mostrar fato não
  público que o relatório individual do Edital esconda.

#### Pendência que não se cumpre

- **FR-2589**: Marco de classificação de um Perfil sem nenhuma inscrição enviada, com o período de
  inscrições encerrado e sem resultado publicado nem ato emitido, MUST NOT ser pendência, nem entrar
  na contagem de resultados previstos, no relatório do Edital e no consolidado; a linha MUST dizer
  "não se aplica: nenhuma inscrição enviada".

#### Forma

- **FR-2590**: O PDF MUST ter, em toda página, o conjunto, o instante dos dados, a natureza gerencial,
  o número da emissão e a paginação; e marcadores para as seções.
- **FR-2591**: A página MUST seguir a política de conteúdo vigente, ter tabelas com cabeçalho
  associado e não exigir rolagem horizontal do corpo a 375 px.

#### Qualidade editorial do documento (revisão visual de 24/10/2026)

> Acrescentados depois da revisão do usuário sobre o PDF da primeira entrega: os números estavam
> certos e o documento tinha virado uma exportação de tabelas. A maquete aprovada é a referência
> de organização e qualidade, e não de valores.

- **FR-2593**: O documento MUST se chamar "Relatório Consolidado de Gestão dos Processos Seletivos",
  e a primeira página MUST trazer, juntos, a identificação institucional compacta, o título, o
  período ou critério, a ficha do conjunto (critério, data dos dados, situação no GPS e das
  providências), a visão geral, os seis indicadores em cartões e os pontos de atenção.
- **FR-2594**: Os indicadores MUST ser cartões — o número em destaque, o rótulo e a base embaixo —,
  e MUST NOT ser tabela; nenhum cartão MUST ser deslocado sozinho para outra página.
- **FR-2595**: A procura por mês MUST ser gráfico de barras com o número escrito ao lado de cada
  barra, gerado dos dados da consolidação; com um mês só, MUST ser uma frase; sem envio, a
  ausência dita.
- **FR-2596**: A paginação MUST preservar os grupos: cartões, faixa de atenção, ficha e blocos lado a
  lado não se partem; título de seção ou subtítulo não fica sozinho no pé da página; tabela longa
  continua na página seguinte com o cabeçalho repetido, e linha de tabela não se parte; o anexo
  técnico abre página própria. Nenhum texto MUST sair da área útil da página.
- **FR-2597**: As seções MUST pôr lado a lado o que se lê junto (oferta e procura; situação e
  alterações; resultados e apuração), com tabelas sem grade pesada, e MUST seguir a paleta e a
  hierarquia tipográfica da maquete, com o brasão em tamanho que não dispute com o título.
- **FR-2598**: O endereço público de cada seleção MUST aparecer só quando vale para quem recebe o
  documento; emitido em ambiente local, o documento MUST dizer que os endereços não estão
  disponíveis, em vez de imprimir endereço local.
- **FR-2599**: Número calculado sobre parte do universo — por privacidade — MUST dizer, junto dele,
  quantos Editais entram e quantos ficam fora (e as vagas deles, quando for número de vagas), sem
  nomeá-los.
- **FR-2600**: O PDF MUST ser marcado (estrutura de títulos, parágrafos, listas, tabelas e a figura
  com texto alternativo; faixa, fios e fundos como artefatos), com o idioma declarado.

### Key Entities

- **Conjunto**: critério (primeira publicação, ano do número ou escolha manual), datas ou ano, Editais
  incluídos, retirados e fora do conjunto com o motivo. Não é persistido; viaja no formulário e fica
  no evento da emissão.
- **Fatos do Edital**: a parte estruturada da derivação da `099` — números por Perfil, pendências por
  tipo, espécie, registros posteriores. Não persistido.
- **Relatório consolidado**: instante, conjunto, somas, pendências por tipo e por Edital, frases,
  relação. Não persistido.
- **Emissão consolidada**: evento de auditoria na unidade — conjunto, instante, ator, número, resumo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-939**: Em todo conjunto de teste, cada número do consolidado é igual à soma do mesmo número nos
  relatórios individuais dos Editais do universo, e vagas, inscrições e razão são iguais às da Visão
  Geral para o mesmo universo (zero divergência).
- **SC-940**: O relatório individual do cenário coerente da `099` produz o mesmo resumo SHA-256 antes e
  depois da separação entre fatos e redação.
- **SC-941**: Nenhum documento gerado nos testes contém nome, CPF, e-mail ou protocolo de candidato,
  nem fato não público por Perfil ou lista; e, em todo cenário de teste com grupo pequeno, nenhuma
  diferença entre números mostrados recupera um fato omitido.
- **SC-942**: O número de leituras ao banco de uma emissão cresce na proporção do número de Editais e
  não do de inscrições, e um conjunto do tamanho do limite é emitido sem exceder o tempo de resposta
  da gestão.
- **SC-943**: Toda emissão deixa um evento com o conjunto e o resumo dos bytes entregues, e duas
  composições com os mesmos fatos, conjunto e instante são idênticas.
- **SC-944**: Pelo navegador, a gestão escolhe o semestre, retira um Edital, vê a camada executiva e
  baixa o PDF, sem banco nem shell (princípio VI).
- **SC-945**: Antes da liberação ampla, ao menos três destinatários de fora da operação dizem, só com a
  primeira página, quantos Editais, o que foi oferecido, o que saiu e o que falta, sem ajuda.
- **SC-946**: O PDF emitido pelo sistema, renderizado página a página e posto ao lado da maquete
  aprovada, tem a mesma organização executiva — painel na primeira página, cartões, gráfico,
  colunas, anexo em página própria —, com conjuntos de 1, 5, 12 e 60 Editais.

## Assumptions

- **Os destinatários recebem o PDF de quem conduz.** Não há papel novo; a porta é a da Visão Geral.
- **O volume é de dezenas de Editais por emissão.** O limite e o tempo são fixados pela medição do
  plano, com cenário de estrutura realista, e não por base de demonstração.
- **A circulação é interna à instituição**, como a do relatório do Edital.
- **A validação com destinatários (SC-945) acontece no piloto**, e é condição para a liberação ampla,
  não para o merge.

## Decisões

### D-001 — Um consolidado é a soma dos fatos de cada Edital, e não uma segunda derivação

O consolidado chama a derivação da `099` Edital a Edital e soma os fatos. Ler o banco de outro jeito
para ganhar consultas criaria a segunda verdade que a `040` e a `099` proíbem; o custo linear é
medido e limitado (FR-2563) em vez de evitado. Se a medição reprovar, a troca é para leituras em lote
**sob** as mesmas regras, e não para regras novas.

### D-002 — A derivação da `099` se separa em fatos e redação

As pendências da `099` saíam como frases. Somar frases é ler texto para decidir situação, que a
FR-2547 da `099` proíbe. A separação mantém a regra num lugar só, e a prova de que nada mudou é o
documento individual idêntico byte a byte (SC-940).

### D-003 — O critério escolhe Editais; os dados são do dia da emissão

Uma partição — primeira publicação, ou ano do número — impede que dois relatórios de períodos
diferentes contem o mesmo Edital. Reconstituir o estado no fim do período exigiria dar instante a
cada regra de vigência, e misturaria o cronograma daquele dia com os números de hoje. Quem precisa do
retrato de 30/06 emite em 30/06: a emissão registrada é o retrato.

### D-004 — O padrão é a primeira publicação

É o que a unidade lançou no período. O ano do número fica disponível, porque é o recorte da Visão
Geral e enxerga o que ainda está em elaboração — mas, para o balanço, o que não foi publicado não
entra (FR-2560).

### D-005 — Cancelado conta como Edital e não entra em número nenhum

Um universo só para números, tabelas e séries: os não cancelados. Somar as inscrições de um Edital
cancelado à razão ou à série faria a procura de uma seleção que não aconteceu disputar vagas que
existiram.

### D-006 — Supressão complementar no Perfil; exclusão no Edital

Omitir só o Perfil pequeno deixava o fato voltar por subtração, no mesmo documento, entre o total do
Edital e as linhas dos outros Perfis. A supressão se estende ao Perfil de menor procura até que os
omitidos somem cinco, e os totais do Edital somem quando nem todos chegam a cinco.

No consolidado a mesma regra não basta: o conjunto é escolhido por quem emite, e duas emissões — com
e sem um Edital pequeno — revelariam por diferença o que o relatório individual dele esconde. Por
isso o Edital pequeno não entra em número não público nenhum do consolidado. O limiar é o da `099`,
revisável pelo usuário e pelo encarregado de dados.

### D-007 — Perfil sem inscrição não deve resultado

Sem inscrição enviada e com o período encerrado, não há o que classificar nem divulgar. Contar o
marco como pendência impedia o Edital de chegar ao relatório de encerramento, e nenhum ato o
resolveria. A regra é da apresentação do relatório: nada muda no que a comissão pode emitir.

### D-008 — A trilha conta o que registra

Os registros depois do encerramento são os da trilha de auditoria dos agregados do Edital. A frase
diz isso, e não "tudo o que aconteceu": ato que o GPS não audita não está ali.

### D-009 — A porta é a da Visão Geral

O gestor tem `visao:consultar` e passa na porta do relatório do Edital em todo Processo do escopo:
tudo o que ele consolida, ele já poderia abrir Edital a Edital. A presidência de comissão, que só
alcança o próprio Processo, fica sem consolidado nesta entrega.

### D-010 — O documento gerencial tem compositor próprio

A primeira entrega compôs o relatório pelo escritor do Edital, que é um paginador de texto corrido:
sem posição livre, sem colunas, sem cor além de um cinza, sem cartão nem barra. O resultado perdeu a
organização da maquete (revisão visual de 24/10/2026). Imprimir HTML pelo navegador reproduziria a
maquete, mas exigiria Chrome ou WeasyPrint no servidor — dependência nova — e o Chrome grava data e
identificador no arquivo, o que desfaz a FR-2568. O compositor de blocos (`interface/diagramacao.py`)
reaproveita a fonte embutida, a métrica, a recusa de caractere sem grafia, o brasão e a montagem
determinística do arquivo do Edital, sem tocar no escritor dele, e acrescenta o que o painel pede.

## Pendências do usuário

- **SC-945** espera a conversa com destinatários reais, no piloto.
- **D-006**: o limiar de cinco inscrições continua pedindo manifestação do encarregado de dados.
- **D-009**: consolidado para a presidência sobre os próprios Processos.
