# Feature Specification: O Edital do sistema como ato oficial

**Feature Branch**: `claude/nova-spec-053-edital-b7660b`

**Created**: 2026-09-29

**Status**: Draft

**Input**: pedido do usuário de 29/09/2026, que executa a recomendação da
[`DP-20`](../../doc/decisoes-pendentes-da-consolidacao.md#dp-20--o-pdf-do-sistema-vale-como-edital-oficial-o-que-ele-precisa-ter-e-com-quais-seções)
depois das decisões de 28/09: **E10 = B** (transcrição, com conferência na homologação), **E5 = B**
(o catálogo ampliado pelas famílias do piloto, textual opcional, sem redação padrão que afirme norma)
e os dois avisos na Revisão, já entregues pelo PR 220. Os RCs de origem são o RC-23, o RC-24, o RC-25
e o RC-26 da [auditoria de 26/09](../../doc/auditoria-de-consolidacao-2026-09-26.md).

> **Faixa de identificadores.** Abre em **FR-980**, **SC-361** e **UX-130**, contíguos. O pedido
> reservava FR-960, SC-360 e UX-130, e as duas primeiras faixas já tinham sido tomadas pela `053`
> (*Classificação — a visão do conjunto*), mergeada na mesma manhã; o número da pasta seguiu o mesmo
> caminho, de `053` para `054`. O teto medido em 29/09/2026 na `main` e nos PRs abertos era FR-979,
> SC-360 e UX-129. As decisões reiniciam em `D-001`.

> **Duas perguntas continuam com o Cefor**: como o ato é assinado, e o nome de quem assina. Esta
> feature **não depende** das respostas: o fecho funciona hoje com o cargo, e aceita o nome e o ato de
> nomeação quando vierem, sem outra mudança de código além do catálogo de autoridades (`D-005`).

---

## Por que esta feature existe

**Desde 28/09 o PDF do sistema é o documento oficial do Edital no piloto.** O que ele omite, erra ou
inventa passa a ser norma publicada, e só sai por Retificação pública. A `DP-20` comparou o documento
com os quinze Editais do Cefor que têm texto extraível e achou quatro famílias de defeito que nenhuma
correção pontual alcança:

- **A estrutura não cabe.** O catálogo tem 12 entradas fixas desde a `006`. No 28/2026, o Edital do
  teste operacional (`DP-18`), **8 das 15 seções não têm lugar**: Público-alvo, as duas de
  verificação da autodeclaração, Matrícula, Acesso ao curso, Homologação da matrícula, Certificado e
  Entrevista PcD. E a inscrição vem antes dos Perfis, quando nos quinze a oferta vem antes.
- **O documento publica o que ninguém escreveu.** A seção textual não se esvazia, e a intocada vai ao
  ato com a redação padrão — que afirma norma. A de "Critérios de Classificação" diz que a
  classificação *"observará a pontuação obtida nas Etapas de Avaliação"*, falso no 28/2026, que é por
  sorteio.
- **O fecho não é o de um ato.** Os quinze terminam com local, data, nome, cargo e ato de nomeação de
  quem assina. O sistema imprime *"Autoridade responsável pelo ato"* e uma designação de cargo no
  lugar do nome, e a `FR-036` da `008` **proíbe** local e data.
- **O documento cala norma que o sistema executa.** A declaração do Requerimento de Matrícula é
  aceita pelo candidato e não é publicada (`029`, Q-10); o consolidado da Retificação sai igual ao
  original, sem data nem marca, distinguível só pelo SHA-256; e o total de vagas não aparece.

**E há um prazo.** A topologia das seções é conferida também depois de publicado, na Retificação, e
contra o catálogo **vigente**. Mudar o catálogo depois do primeiro Edital real faria a Retificação
dele ser recusada. Antes da primeira publicação real, mudar é barato; depois, pede versão de
catálogo, e o acervo fica com duas formas de documento, porque documento publicado não se regenera.
Esta feature muda o catálogo **agora**, e fecha também a armadilha: a partir dela, a Retificação
confere a topologia contra a do conteúdo que retifica (`D-003`).

**O que não muda.** O corpo normativo continua função pura do conteúdo homologado; local, data,
autoridade, ato de nomeação e histórico de publicações chegam ao compositor como **contexto do ato**,
fora do conteúdo, e o SHA-256 do conteúdo não se altera por eles (`008`, FR-034). Nenhuma assinatura
é criada (`008`, FR-037). Nenhum documento já publicado é regenerado.

---

## Clarifications

### Session 2026-09-29

- Q: O documento publicado deve trazer o total de vagas? → A: Sim, como linha *"Total"* no fim da
  tabela de Perfis, com mais de um Perfil; o cadastro reserva não soma (`FR-997`).
- Q: O que fazer com a redação padrão das seções textuais? → A: Nenhuma fica; toda textual nasce
  vazia, o aviso do PR 220 sai e entra o de Apresentação e Disposições Finais vazias (`FR-983`,
  `FR-986`, `D-002`).
- Q: De onde vem o ato de nomeação de quem assina? → A: Do catálogo de autoridades, declarado em
  código ao lado do nome, copiado para a Publicação; vazio até o Cefor fornecer nome e portaria
  (`FR-991`, `D-005`).
- Q: No consolidado da Retificação, de quem são a data e a autoridade do fecho? → A: Da própria
  Retificação, coerente com a `FR-043` da `008`; a marca abaixo do anúncio dá a data original e a de
  cada Retificação (`FR-995`).
- Q: Qual conjunto de seções o catálogo deve ter? → A: As quatro famílias da amostra, 22 entradas, sem
  as idiossincráticas da família de bolsista (`FR-980`, `D-001`).

---

## User Scenarios & Testing *(mandatory)*

**Atores.** Quem elabora o Edital (etapa Conteúdo), quem homologa (confere a prévia contra o original,
pela E10 = B), quem publica (escolhe a autoridade), e o candidato, que lê o documento publicado. As
permissões são as de hoje.

### User Story 1 — Transcrever o Edital da família sem que norma caia em seção errada (Priority: P1)

Quem elabora transcreve o 28/2026, que tem 15 seções numeradas. Cada seção do original tem uma seção
correspondente no catálogo; as que o Edital não usa ficam vazias e não saem no documento; a oferta
(Perfis de Vaga) sai antes da inscrição.

**Why this priority**: é a E5. Sem lugar, a matrícula do 28/2026 vai para dentro de "Disposições
finais" em caixa alta, e o documento oficial passa a ter a estrutura errada.

**Independent Test**: compor um Edital com a estrutura do 28/2026, preencher as seções que o original
tem, deixar as demais vazias, gerar a prévia e conferir, seção a seção, que as 15 do original têm
lugar, que nenhuma vazia aparece e que a numeração é contínua.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** quem elabora abre a etapa Conteúdo, **Then** vê as
   seções do catálogo ampliado, na ordem do documento, com a oferta antes da inscrição.
2. **Given** uma seção textual vazia, **When** a prévia é gerada, **Then** a seção não aparece e as
   seguintes são numeradas sem salto.
3. **Given** a etapa Conteúdo com seções vazias intercaladas, **When** quem elabora lê a tela,
   **Then** cada seção mostra o número que terá no documento, ou diz que não sai no documento.
4. **Given** um Edital recém-criado, **When** a prévia é gerada sem que ninguém tenha escrito nada,
   **Then** nenhuma seção textual sai com texto que não foi escrito para este Edital.

---

### User Story 2 — O fecho de um ato, sem inventar nome (Priority: P1)

O documento publicado termina como os Editais do Cefor: local e data do ato, e a autoridade. Hoje, sem
o nome próprio fornecido pelo Cefor, sai o cargo; quando o nome e o ato de nomeação entrarem no
catálogo, a publicação seguinte os imprime.

**Why this priority**: local, data e autoridade estão em 15 de 15 Editais. Um ato sem data é o defeito
mais visível do documento oficial, e a designação *"Diretora do Cefor"* no lugar do nome é um nome
que não é nome.

**Independent Test**: publicar um Edital e conferir o fecho (*"Vitória (ES), 29 de setembro de
2026."*, a rubrica e o cargo); acrescentar nome e ato de nomeação à autoridade no catálogo, publicar
outro e conferir que saem, e que a Publicação os registrou.

**Acceptance Scenarios**:

1. **Given** um Edital homologado, **When** é publicado, **Then** o documento traz, depois do
   conteúdo normativo, o local e a data da publicação por extenso, e depois a autoridade.
2. **Given** uma autoridade do catálogo sem nome próprio, **When** o ato é publicado, **Then** o
   fecho imprime o cargo, e nenhuma designação de cargo no lugar do nome.
3. **Given** uma autoridade com nome e ato de nomeação no catálogo, **When** o ato é publicado,
   **Then** a Publicação registra os três, e o fecho imprime nome, cargo e ato de nomeação.
4. **Given** a prévia de um Edital, **When** é gerada, **Then** não traz local, data nem autoridade.
5. **Given** o mesmo conteúdo publicado em dois dias diferentes, **When** se comparam os dois, **Then**
   o SHA-256 do conteúdo é o mesmo e o documento difere só no fecho.

---

### User Story 3 — O consolidado se diz retificado, e de quando (Priority: P1)

O documento que a Retificação produz declara, logo abaixo do anúncio do ato, que é versão
consolidada, com a data da publicação original e a de cada Retificação que incorpora.

**Why this priority**: sem a marca, o candidato que baixa o documento não sabe qual versão tem em
mãos, e os Editais da amostra marcam a retificação no próprio documento.

**Independent Test**: publicar um Edital, publicar uma Retificação, e conferir que o documento da
Retificação traz a marca com as duas datas e que o documento original não traz marca nenhuma.

**Acceptance Scenarios**:

1. **Given** um Edital publicado e uma Retificação homologada, **When** a Retificação é publicada,
   **Then** o documento consolidado diz que é versão consolidada, publicada originalmente em uma data
   e retificada em outra.
2. **Given** duas Retificações publicadas, **When** a segunda é publicada, **Then** a marca lista as
   duas, em ordem.
3. **Given** uma Retificação com vigência posterior à data de publicação, **When** é publicada,
   **Then** a marca diz também a partir de quando vale.
4. **Given** o documento da publicação original, **When** é lido, **Then** não traz marca de
   consolidação.

---

### User Story 4 — O Edital publicado sob o catálogo anterior continua retificável (Priority: P1)

Um Edital publicado antes desta feature, com as 12 seções de antes, é retificado depois dela. A
Retificação é aceita, e o consolidado mantém a forma com que o Edital foi publicado.

**Why this priority**: é a armadilha que a `DP-20` nomeou. Sem isso, mudar o catálogo tranca a
Retificação de todo o acervo, e a próxima mudança de catálogo, depois do piloto, repete o problema.

**Independent Test**: publicar um Edital com o catálogo anterior, trocar o catálogo, retificar o
conteúdo de uma seção textual, e conferir que a Retificação é publicada, sem recusa de topologia, e
que o consolidado tem as 12 seções de antes.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com o catálogo anterior, **When** uma Retificação altera o texto de
   uma seção, **Then** a Retificação é aceita.
2. **Given** qualquer Edital publicado, **When** uma Retificação tenta acrescentar, remover,
   renomear, reordenar ou trocar a espécie de uma seção, **Then** é recusada, como hoje.
3. **Given** um Edital publicado com uma seção textual vazia, **When** a Retificação lhe dá texto,
   **Then** a seção passa a sair no consolidado, na posição do catálogo com que o Edital foi
   publicado.

---

### User Story 5 — O candidato lê o que vai aceitar, e quantas vagas há (Priority: P2)

Quando o Edital exige Requerimento de Matrícula, o documento publica a declaração por extenso e o
momento em que ela será aceita. Com mais de um Perfil, a tabela de Perfis traz o total de vagas.

**Why this priority**: são normas que o sistema executa e o documento cala; menores que as quatro
anteriores, porque a declaração já aparece por extenso na tela em que se aceita.

**Independent Test**: publicar um Edital que exige o Requerimento, com três Perfis, e conferir a
declaração na seção Matrícula, idêntica à que o portal exibe, e a linha de total no quadro.

**Acceptance Scenarios**:

1. **Given** um Edital que exige Requerimento de Matrícula na convocação, **When** é publicado,
   **Then** a seção Matrícula diz que o requerimento é enviado quando o candidato for convocado, e
   traz a declaração por extenso — ainda que quem elabora não tenha escrito nada nessa seção.
2. **Given** um Edital com teto de inscrições e a seção Inscrição vazia, **When** é publicado,
   **Then** a seção sai com a frase do teto.
3. **Given** um Edital com três Perfis, **When** é publicado, **Then** a tabela de Perfis traz uma
   linha de total com a soma das vagas imediatas.
4. **Given** um Edital com um Perfil só, **When** é publicado, **Then** nenhuma linha de total é
   acrescentada.

---

### Edge Cases

- **Edital em elaboração antes da mudança.** Os textos que alguém escreveu continuam onde estavam: as
  chaves das seções existentes não mudam. A seção que dependia da redação padrão passa a estar vazia,
  e o aviso da Revisão sobre seção universal vazia (`FR-986`) a nomeia.
- **Edital homologado antes da mudança e publicado depois.** O conteúdo homologado tem a topologia
  anterior, e o rascunho passa a produzir a nova: a publicação é recusada por divergência da revisão
  homologada, como qualquer mudança do rascunho depois da homologação. É submeter de novo. Aceitável
  porque não há publicação real antes do piloto; fica registrado (`D-003`).
- **Todas as seções textuais vazias.** O documento sai só com as geradas; a Revisão avisa as duas
  seções universais vazias. Não é impeditivo: publicar um Edital só de dados estruturados é legítimo.
- **Seção gerada e textual vazias ao mesmo tempo, intercaladas.** A numeração é contínua; a tela e o
  documento dão o mesmo número à mesma seção.
- **Retificação que esvazia uma seção textual.** É aceita — é mudança normativa legítima — e a seção
  deixa de sair no consolidado; o "O que mudou" a registra como qualquer alteração de conteúdo.
- **A seção Matrícula vazia num Edital sem Requerimento.** Não sai.
- **A autoridade retirada do catálogo depois de publicar.** Nada muda no que foi publicado: a
  Publicação guarda nome, cargo e ato de nomeação do momento do ato (`008`, FR-046).
- **Publicação perto da meia-noite.** A data do fecho é a do fuso do Cefor, e não a do relógio do
  servidor em UTC.
- **Retificação com vigência no mesmo dia da publicação.** A marca não repete a data.
- **Publicações anteriores a esta feature.** Continuam sem ato de nomeação e com o documento que
  tinham; nada é regenerado nem migrado no documento.

## Requirements *(mandatory)*

### O catálogo (E5 = B)

- **FR-980**: O catálogo de seções do Edital MUST passar a ter as seções que se repetem nas famílias da
  amostra do Cefor, nesta ordem: Apresentação (preâmbulo, sem número); Disposições Preliminares;
  Informações Gerais sobre o Curso; Público-Alvo; Requisitos Gerais de Participação; **Perfis de
  Vaga**; Da Inscrição; Documentos Exigidos para a Inscrição; Da Verificação da Autodeclaração; Do
  Atendimento à Pessoa com Deficiência; Etapas de Avaliação; Critérios de Classificação; Cronograma;
  Dos Recursos; Da Convocação; Da Matrícula; Do Acesso ao Curso; Da Homologação da Matrícula; Do
  Certificado; Do Prazo de Validade; Anexos; Disposições Finais. As geradas continuam as cinco de
  hoje. O conjunto e a ordem continuam definidos pelo sistema, e quem elabora continua sem acrescentar,
  remover ou reordenar seção (`006`, FR-034).
- **FR-981**: As seções que já existiam MUST manter a chave, para que o texto já escrito num Edital em
  elaboração continue na seção em que foi escrito.
- **FR-982**: A seção textual MUST poder ficar vazia, e a vazia MUST NOT ser composta no documento —
  nem na prévia, nem no publicado —, como a gerada cuja coleção está vazia. *Emenda a `FR-041` da
  `006`: a seção textual sem conteúdo deixa de ser impeditivo.*
- **FR-983**: Nenhuma seção textual MUST nascer com redação padrão. O Edital novo começa com as seções
  textuais vazias, e o documento só publica texto que alguém escreveu para ele. *Emenda a `FR-037` da
  `006`, que permitia texto inicial institucional.*
- **FR-984**: A seção textual à qual o sistema acrescenta norma que executa — a frase do teto na
  Inscrição (`015`, FR-063) e a declaração do Requerimento na Matrícula (`FR-996`) — MUST ser composta
  quando houver essa norma, ainda que quem elabora a tenha deixado vazia; o texto de quem elabora,
  quando existir, vem primeiro.
- **FR-985**: A numeração das seções MUST ser a mesma na etapa Conteúdo, na Revisão e no documento:
  derivada da mesma regra, sobre o conteúdo que seria publicado; a seção que não sai no documento não
  recebe número em tela nenhuma. *Fecha a parte "numeração" do RC-26.*
- **FR-986**: A Revisão MUST avisar, sem impedir, quando a Apresentação ou as Disposições Finais vão
  ao ato vazias. São as duas seções que os quinze Editais da amostra têm sem exceção — o preâmbulo com
  a autoridade que pratica o ato, e os casos omissos. O aviso da redação padrão sem revisão (PR 220)
  MUST deixar de existir, porque a redação padrão deixa de existir.

### A topologia na Retificação

- **FR-987**: Na elaboração, na submissão e na publicação do Edital, a topologia das seções MUST
  continuar conferida contra o catálogo vigente.
- **FR-988**: Na Retificação, a topologia MUST ser conferida contra a do conteúdo retificado, e não
  contra o catálogo vigente: as mesmas seções, com a mesma chave, título, ordem, espécie e origem.
  Só o texto das seções textuais varia, e pode inclusive ficar vazio. *Emenda a `FR-041` da `006`
  nesse ponto. Um Edital publicado sob um catálogo anterior continua retificável, e o consolidado
  mantém a forma com que foi publicado.*

### O fecho (emenda à FR-036 da 008)

- **FR-989**: O documento **publicado** MUST trazer, depois do conteúdo normativo e antes do bloco de
  autoridade, o local e a data do ato: *"Vitória (ES), 29 de setembro de 2026."*. O local é constante
  do compositor, como a unidade já é. A data é a da Publicação, no fuso do Cefor, por extenso. *Emenda
  a `FR-036` da `008`, que proibia praça e data.*
- **FR-990**: Local e data MUST chegar ao compositor como contexto do ato, fora do conteúdo publicado:
  o SHA-256 do conteúdo não muda por eles, e a prévia não os tem (`008`, FR-034, FR-035 e FR-041).
- **FR-991**: A Publicação MUST registrar o ato de nomeação de quem assina, ao lado do nome e do cargo,
  copiado do catálogo de autoridades no momento do ato e imutável depois, como os outros dois. O ato
  de nomeação pode estar ausente no catálogo, e então a Publicação o registra ausente.
- **FR-992**: O catálogo de autoridades MUST distinguir o nome próprio do cargo: o nome pode estar
  ausente, e nenhuma designação de cargo MUST ocupar o lugar do nome. Enquanto o Cefor não fornecer
  os nomes, as entradas do catálogo têm só o cargo.
- **FR-993**: O bloco de autoridade MUST imprimir o nome, quando registrado; o cargo; e o ato de
  nomeação, quando registrado. Sem nome registrado, imprime o cargo, e nada no lugar do nome. O
  bloco continua anunciando-se como registro, e não como assinatura (`008`, FR-033 e FR-037).
- **FR-994**: Onde o sistema exibe quem assinou uma Publicação — a consulta pública da publicação e a
  escolha da autoridade ao publicar —, a ausência de nome MUST mostrar só o cargo, sem separador
  pendurado nem campo vazio.

### O consolidado da Retificação

- **FR-995**: O documento produzido pela publicação de uma Retificação MUST declarar, logo abaixo do
  anúncio do ato, que é versão consolidada, com a data da publicação original e a de cada Retificação
  que ele incorpora, esta inclusive, em ordem; quando a vigência desta Retificação começar em data
  diferente da de publicação, MUST dizer também a partir de quando vale. O documento da publicação
  original MUST NOT trazer marca. As datas são contexto do ato, como as de `FR-990`, e o fecho do
  consolidado traz local e data da própria Retificação. *Complementa a `FR-043` da `008`: a mesma
  composição, com a marca.*

### A declaração do Requerimento de Matrícula

- **FR-996**: Quando o Edital exigir Requerimento de Matrícula, o documento MUST publicar, na seção Da
  Matrícula, o momento em que ele é enviado — no ato da inscrição, ou quando o candidato for
  convocado — e o texto integral da declaração que o candidato aceitará, idêntico ao que o portal
  exibe. *Fecha a Q-10 da `029`.*

### O total de vagas

- **FR-997**: Com mais de um Perfil de Vaga, a tabela de Perfis do documento MUST terminar com uma
  linha *"Total"*, com a soma das vagas imediatas na coluna de vagas e as demais em branco, como o
  Quadro 2 do 28/2026. O cadastro reserva não é somado. Com um Perfil só,
  nenhuma linha é acrescentada: a vaga dele já é o total.

### A primeira página (emenda da SC-001 da 008)

- **FR-998**: A `SC-001` da `008` MUST passar a dizer o que o documento faz desde a `008`: a primeira
  página apresenta órgão, instituição, unidade, ato e título, **sem o Processo**, que sai só no bloco
  de verificação. Os Editais da amostra não nomeiam Processo algum.

### A evidência

- **FR-999**: A fixture de bytes do documento publicado MUST ser refeita junto desta mudança, com a
  diferença conferida, e tudo de que ela depende — inclusive local, data e ato de nomeação — MUST
  estar versionado ao lado dela (`008`, FR-044).

### A tela Conteúdo

- **UX-130**: Cada seção da etapa Conteúdo MUST mostrar o número que terá no documento, ou, quando não
  sair, dizer *"Vazia — não sai no documento"*, em texto; o número MUST acompanhar o que se digita,
  sem gravar.
- **UX-131**: A tela MUST NOT dizer *"Redação institucional padrão"*; o campo vazio é o estado
  inicial, e a ajuda da etapa diz que só sai no documento a seção que tiver texto.
- **UX-132**: A seção a que o sistema acrescenta norma (`FR-984`) MUST dizer, na tela, o que o
  documento acrescentará a ela — a frase do teto, a declaração do Requerimento —, para que quem
  elabora não a repita.
- **UX-133**: O número e o estado de cada seção MUST ser lidos por tecnologia assistiva junto do
  título da seção.

### Key Entities

- **Catálogo de seções**: declarado em código, como hoje; ganha dez entradas textuais e perde a
  redação padrão. Chave, título, ordem, espécie e origem.
- **Autoridade (catálogo)**: cargo; nome próprio, que pode estar ausente; ato de nomeação, que pode
  estar ausente; identificador de vínculo, como hoje.
- **Publicação**: ganha o ato de nomeação de quem assina, ao lado de nome e cargo; imutável, como é.
- **Contexto do ato**: o que chega ao compositor fora do conteúdo — autoridade, local, data e, na
  Retificação, as datas das publicações que o consolidado incorpora.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-361**: Gerado o PDF de um Edital com a estrutura do 28/2026, **15 de 15** seções numeradas do
  original têm seção correspondente no documento, e os Perfis de Vaga vêm antes da inscrição.
- **SC-362**: Um Edital novo publicado sem que ninguém escreva nas seções textuais tem **0**
  parágrafos de texto que não foram escritos para ele.
- **SC-363**: Em 100% dos casos de teste — incluindo textuais e geradas vazias intercaladas —, o
  número de cada seção na tela Conteúdo é o número que ela tem no documento.
- **SC-364**: 100% dos documentos publicados trazem local e data do ato; publicar o mesmo conteúdo em
  duas datas dá o mesmo SHA-256 de conteúdo.
- **SC-365**: Com a autoridade sem nome no catálogo, **0** documentos publicados trazem uma designação
  de cargo no lugar do nome; acrescentados nome e ato de nomeação ao catálogo, a publicação seguinte
  os imprime sem outra mudança.
- **SC-366**: Um Edital publicado sob o catálogo anterior tem **0** recusas de topologia ao retificar
  o texto de uma seção, e o consolidado tem as mesmas seções da publicação original.
- **SC-367**: 100% dos documentos de Retificação trazem a marca de consolidação com as datas; **0**
  documentos de publicação original a trazem.
- **SC-368**: Em 100% dos Editais que exigem Requerimento de Matrícula, a declaração publicada é
  idêntica, caractere a caractere, à que o portal exibe para aceite.
- **SC-369**: Com mais de um Perfil, a linha de total é igual à soma das vagas imediatas dos Perfis.
- **SC-370**: Os testes que afirmam invariante do documento — determinismo, acentuação, ausência de
  UUID, autossuficiência do corpo normativo, igualdade das quebras entre prévia e publicado — não
  mudam de resultado.

## Assumptions

### D-001 — O catálogo cobre as quatro famílias da amostra, com nomes genéricos

As 22 entradas de `FR-980` são a união das seções que se repetem nas quatro famílias da `DP-20` (FIC;
pós-graduação e aperfeiçoamento; bolsista UAB/FAPES; chamada pública técnica), com títulos que servem a
todas. Onde duas famílias dão nomes diferentes à mesma matéria — *"Informações gerais sobre o curso"*
e *"Sobre o curso"* —, a entrada é uma. As duas verificações do 28/2026 — a da autodeclaração
étnico-racial e a da deficiência — cabem numa entrada: são a mesma matéria, a elegibilidade às vagas
reservadas, para públicos diferentes, e o texto transcrito as separa. As seções idiossincráticas da família de bolsista —
Mobilidade entre perfis, Curso de formação, Pagamento da bolsa — não entram: a família está fora do
piloto (`DP-05`), e cada uma delas caberia num Edital só.

**Por que as quatro, e não só as do piloto.** Mudar o catálogo depois da primeira publicação real
custa uma versão de catálogo. Uma entrada que o piloto não usa custa uma caixa de texto vazia.

### D-002 — Sem redação padrão, e não redação padrão "que não afirme norma"

A E5 pediu *"sem redação padrão que afirme norma"*. Toda redação padrão do catálogo de hoje afirma
alguma: que a inscrição implica aceitação, que os omissos vão à *"autoridade responsável"*, que a
classificação é por pontuação. E, com a E10 = B, o texto nasce no Word do setor e é transcrito: a
redação padrão não economiza nada a ninguém, e só serve para ir ao ato sem revisão. Por isso nenhuma
fica. O aviso do PR 220 perde o objeto e sai; em seu lugar entra o de `FR-986`, que aponta a lacuna
que a amostra mede.

### D-003 — A Retificação confere a topologia contra o conteúdo retificado

É o que torna o catálogo mudável sem trancar o acervo, agora e depois. A regra da `006` existe para
impedir que uma Retificação faça sobre o publicado o que a interface impede na elaboração —
acrescentar, remover, reordenar, renomear seção —, e o conteúdo retificado impede isso tão bem quanto o
catálogo, sem depender de o catálogo não mudar. *A mensagem de "não retificável" de título, ordem e
espécie deixa de afirmar que são "os mesmos em todo Edital do Cefor"*, que passa a ser falso para o
acervo publicado sob o catálogo anterior.

**O custo que fica.** Um Edital homologado antes da mudança e não publicado precisa ser submetido de
novo, porque o rascunho passa a produzir outra topologia. Não há Edital real nessa situação.

### D-004 — Local e data como contexto do ato

A data do ato já existe no momento em que o documento é composto, nos dois fluxos de publicação; ela
chega ao compositor pelo mesmo caminho da autoridade. O local é constante, como a unidade (`ORGAO`):
o Cefor publica de Vitória, e nenhum cadastro de praça é criado. O dia é escrito sem zero à esquerda,
como manda o Manual de Redação da Presidência da República (*"29 de setembro de 2026"*).

### D-005 — O fecho sem depender do Cefor

O catálogo de autoridades passa a ter o cargo como dado obrigatório, e o nome próprio e o ato de
nomeação como opcionais. Hoje as três entradas ficam só com o cargo, e o fecho diz o cargo. Quando o
Cefor fornecer nome e ato de nomeação, eles entram no catálogo, revisados em diff, e a publicação
seguinte os imprime. A rubrica *"Autoridade responsável pelo ato"* continua, porque a pergunta sobre
como o ato é assinado continua aberta: anunciar registro é verdade em qualquer resposta, e simular
assinatura não seria.

### D-006 — A declaração vai à Matrícula, qualquer que seja o momento

O Requerimento é da matrícula, ainda que enviado no ato da inscrição, e é a seção que o candidato
procura para saber o que acontece depois de selecionado. O momento vai na frase. Uma seção só evita
que o mesmo Edital publique a declaração em dois lugares conforme a opção.

### Outras premissas

- **E10 = B não pede código.** A conferência da prévia contra o original, na homologação, é processo
  do Cefor. A lista do item 3 da `DP-20` é o roteiro.
- **O cronograma continua seção.** Doze dos quinze o publicam como anexo; no sistema, anexo é arquivo à
  parte com rótulo do autor (`020`, D-002), e um "Anexo I" gerado colidiria com o que o autor
  escrever. A `DP-20` recomendou mantê-lo como seção.
- **A unidade e o local são constantes.** Nenhuma unidade configurável por Processo é introduzida.
- **Nenhum documento publicado é regenerado.** Para ver o documento novo no banco de demonstração, é
  re-semear.

## Out of Scope

- **Como o ato é assinado**, e o nome próprio de quem assina: perguntas ao Cefor (`DP-20`, itens 4 e
  5). O que entra é o lugar para o nome e o ato de nomeação.
- **Seção acrescentável por quem elabora** (a opção C da E5), tabela, subitem numerado e negrito no
  texto das seções textuais.
- **Filtro do catálogo por família** na tela Conteúdo: o sistema não tem o conceito de família.
- **O cronograma como anexo**, a hora *"às 00h"* (RC-22), o requisito do Perfil × a instrução do
  documento (E2, AX-2) e a conferência assistida da transcrição (E10 = C).
- **Versão de catálogo.** Não é necessária enquanto a Retificação conferir a topologia contra o
  conteúdo retificado (`D-003`).
