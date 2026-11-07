# Feature Specification: A inaplicabilidade documental tem fundamento publicado

**Feature Branch**: `claude/nostalgic-gagarin-492fdc`, sobre a `main` em `5fcbfa54`

**Created**: 2026-11-07

**Status**: Em implementação, desde 07/11/2026. As decisões têm duas origens:

- **Do usuário, em 07/11/2026**, em duas rodadas: no pedido desta spec, a *1ª* à *9ª decisão*; na
  revisão do PR #426, a *10ª* à *12ª*. Estão em *Clarifications* e não se reabrem.
- **Propostas de desenho desta spec:** D-001 a D-016, ao fim. Elas fecham o que as decisões deixaram
  aberto. **O comportamento que descrevem foi aprovado pelo usuário em 07/11/2026** (10ª decisão),
  sem aprovação individual de cada uma. As escolhas técnicas compatíveis com ele ficam para a
  implementação. Continua pendente só a P-3, que não impede implementar.

**Input**: o estudo [`doc/estudo-nao-se-aplica-2026-11-07.md`](../../doc/estudo-nao-se-aplica-2026-11-07.md)
(commit `8ed8d28d`), reconferido no código e nas specs em 07/11/2026. Ver a
[pesquisa](research.md), que separa o que foi comprovado por teste, por execução e por leitura.

> **Faixa de identificadores.** Esta spec abre em **FR-4451**, **SC-1371** e **UX-301**. O teto foi
> medido em 07/11/2026 em `specs/` de todas as worktrees desta máquina: o requisito funcional quatro
> mil quatrocentos e um e o critério mil trezentos e quarenta e um, da correção da `115` no PR #425,
> ainda fora da `main`, e o requisito de experiência duzentos e setenta e nove. A pasta `130` é a
> última da `main`, e por isso esta é a `131`. A folga é a de costume: duas sessões do mesmo dia já
> colidiram contando do mesmo teto. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3592 da `115`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número.

---

## Por que esta feature existe

**O GPS chama de "não se aplica" duas coisas diferentes.** O item da lista que o recorte publicado
exclui (Perfil, modalidade) é derivado na gravação da lista, e ninguém o decide. A conferência
*"não se aplica"* é um juízo manual sobre um item que a lista diz que **se aplica**. A primeira é
inaplicabilidade. A segunda, como está, é qualquer coisa que o motivo disser.

**O contrato atual permite afastar qualquer obrigatório.** A FR-3585 da `115` oferece o resultado em
todo item. A FR-3592 da `115` o conta como atendido para o aceite. O motivo só precisa não ser
vazio. No banco descartável do estudo, um conferente só alocado marcou os três obrigatórios de uma
convocação, inclusive o laudo de quem concorre como PcD, com motivo `"."` num deles e sem abrir o
arquivo apresentado. O gestor registrou o aceite lendo *"Pronta para decidir — 3 de 4 conferidos"*.
Nenhuma decisão registrada da `115` fundamenta essa abrangência: o complemento da auditoria de
03/11 propunha o aceite *"só com os obrigatórios conformes"*.

**O sistema não tem como distinguir o afastamento legítimo do arbitrário.** Há inaplicabilidade
legítima fora do recorte: os Editais da amostra publicam obrigatórios condicionados a fatos da
pessoa, como o alistamento militar *"no caso de candidatos do sexo masculino"* e documentos *"quando
for o caso"*. A `044` deixou essas condições fora do recorte estruturado, pela decisão sobre a
condição do candidato. Mas o GPS não sabe **quais** documentos o Edital condicionou. Para ele, o
alistamento militar e o laudo médico são o mesmo obrigatório, e a conferência pode afastar os dois.
Mostrar melhor o "não se aplica" o tornaria visível, e não impossível onde ele é arbitrário.

**A correção mínima é o Edital dizer o que é condicional.** O Documento Exigido da convocação ganha
um texto: a condição de exigência, como o Edital a publica. O sistema não a avalia, e só a usa como
âncora. O "não se aplica" da conferência passa a existir **só** onde o Edital publicou uma condição.
O aceite mostra cada um deles a quem decide. O documento incondicional não pode mais ser afastado
pela conferência, por ninguém.

### O que esta spec cobre, e o que fica fora

**Cobre:**

1. A **condição de exigência** do Documento Exigido da convocação: composição, revisão, publicação,
   PDF, versionamento, Retificação, cópia e duplicação.
2. A **conferência**: quando o *"não se aplica"* existe, quem o registra, o fundamento, a autoria, o
   arquivo recebido, a nova versão, a substituição e a recusa sobre item excluído pelo recorte.
3. O **aceite e a regularização**: a apresentação separada na condução e na confirmação, e a ciência
   de quem desfecha.
4. A **rastreabilidade**: o que já está gravado, o que falta nas projeções, a trilha do desfecho e a
   situação na formalização.
5. A **transição** dos Editais e das convocações existentes.

**Fica fora:**

- A **dispensa excepcional**, como estado, permissão ou operação (2ª decisão).
- **Condição estruturada** sobre a pessoa: campos de sexo, idade, vínculo, expressões, regras,
  formulário dinâmico, autodeclaração do candidato (3ª decisão; a decisão sobre a condição do
  candidato da `044` continua de pé).
- A **condição em documento da inscrição** (D-004).
- Papel novo, homologação documental, segunda aprovação (3ª decisão).
- A correção da convocação em lote (PR #425), o aviso de pendência por e-mail (QI-7 da `115`), o
  Registro Acadêmico, a OCR, o visualizador, a fila global.
- O auditor abrir o arquivo da convocação, que continua pendente na `115`.

## Clarifications

### Session 2026-11-07 (decisões do usuário no pedido desta spec)

- Q: Quantas figuras a conferência precisa distinguir? → A: **Quatro.** *A*, o documento excluído
  pelo recorte, derivado e sem decisão manual. *B*, o obrigatório incondicional, que o "não se
  aplica" não pode afastar. *C*, o obrigatório condicional, que admite inaplicabilidade com
  fundamento verificável na regra publicada. *D*, a dispensa excepcional. *(1ª decisão)*
- Q: O GPS oferece a dispensa excepcional? → A: **Não.** Nenhum estado *"Dispensado"*, nenhuma
  permissão genérica de dispensar. Exceção juridicamente justificada é objeto de decisão
  institucional específica. *(2ª decisão)*
- Q: Até onde vai a solução? → A: **Sem motor de regras pessoais, sem papel novo e sem fluxo de
  várias aprovações.** *(3ª decisão)*
- Q: O que se preserva? → A: **A inaplicabilidade legítima**, e ela não pode funcionar como dispensa
  arbitrária. *(4ª decisão)*
- Q: O arquivo recebido decide alguma coisa? → A: **Não, sozinho.** Ele não impede nem justifica a
  inaplicabilidade. *(5ª decisão)*
- Q: Basta um tamanho mínimo de motivo? → A: **Não.** `"."`, ou equivalente sem conteúdo, não é
  fundamento. A prioridade é a vinculação à condição publicada e a rastreabilidade. *(6ª decisão)*
- Q: O aceite pode continuar tratando o "não se aplica" como conferido? → A: **Não.** Quem desfecha
  vê, antes do aceite, cada obrigatório considerado não aplicável, o fundamento e quem registrou,
  sem novo fluxo de homologação. *(7ª decisão)*
- Q: As decisões já tomadas se reinterpretam? → A: **Não automaticamente.** Decisão documental
  encerrada fica como está; transição de dados vai como alternativa para decisão. *(8ª decisão)*
- Q: A conferência sobre item excluído pelo recorte se corrige na tela? → A: **Não basta.** O domínio
  rejeita operação documental incompatível com a aplicabilidade do item. *(9ª decisão)*

### Session 2026-11-07 (revisão do PR #426)

- Q: O desenho se aprova? → A: **Sim, a opção 2, com o desenho mínimo:**
  - a condição como texto publicado, sem interpretar os fatos da pessoa;
  - o *"não se aplica"* só no obrigatório condicional, com motivo;
  - o aceite mostrando as inaplicabilidades e exigindo ciência do conjunto atual;
  - a reutilização do mecanismo da `120` para detectar o conjunto desatualizado, que não prova
    leitura e evita confirmar o que mudou;
  - nenhuma tabela de ciência, papel, aprovação, rota ou serviço novo.

  O comportamento das D-001 a D-016 fica aprovado, sem rodada individual. *(10ª decisão)*
- Q: O *"não se aplica"* já gravado em obrigatório incondicional, numa chamada aberta, ainda atende? →
  A: **Não** (a P-1, alternativa *a*). Os registros e os desfechos encerrados se preservam. Sem
  calendário de transição nem compatibilidade especial para os bancos de demonstração. *(11ª
  decisão)*
- Q: A dispensa excepcional precisa de pendência própria? → A: **Não.** Ela já está fora pela 2ª
  decisão; a redação corrigida da antiga P-2 passa para a D-003. A P-3 continua pendente, sem
  aceitação implícita. *(12ª decisão)*

## User Scenarios & Testing *(mandatory)*

O cenário é o 72/2026 em miniatura, o mesmo das fixtures da `115`, com dois documentos novos na
convocação:

- **Alistamento** — *"Certificado de alistamento militar ou de reservista"*, obrigatório, com a
  condição *"no caso de candidatos do sexo masculino, maiores de 18 anos"* (molde dos Editais 28, 35,
  69 e 77/2026);
- **Laudo** — o laudo médico, obrigatório por recorte à modalidade PcD, **sem** condição.

E os documentos incondicionais de todos: certidão, histórico, certificado do ensino médio,
comprovante de residência. As pessoas: **Ana** (PcD), **Bia** (ampla concorrência), **Caio** (ampla
concorrência, maior de 18 anos).

### User Story 1 — O Edital diz o que é condicional, e só isso se afasta (Priority: P1)

Quem compõe o Edital declara, no Documento Exigido da convocação, que ele é obrigatório só sob uma
condição publicada, e escreve a condição como o Edital a publica. A revisão, o PDF e o portal mostram
a condição junto do documento. Na conferência, o *"não se aplica"* existe só para esse documento.

**Why this priority**: é o que separa a figura C da figura B. Sem o Edital dizer o que é
condicional, nenhuma regra de conferência consegue impedir o afastamento arbitrário sem impedir
também o legítimo.

**Independent Test**: compor e publicar o Edital com o Alistamento condicional, convocar a Ana e o
Caio, e verificar que a conferência oferece *"não se aplica"* no Alistamento e recusa no Laudo e na
certidão, pela tela e pelo comando.

**Acceptance Scenarios**:

1. **Given** um Documento Exigido da convocação obrigatório, **When** quem compõe preenche *"Exigido
   somente quando"* com *"no caso de candidatos do sexo masculino, maiores de 18 anos"* e publica,
   **Then** o PDF imprime o item como os Editais da amostra o escrevem — *"Certificado de alistamento
   militar ou de reservista, no caso de candidatos do sexo masculino, maiores de 18 anos"* —, e a
   revisão, o portal e a gestão mostram *"Condição publicada: no caso de candidatos do sexo
   masculino, maiores de 18 anos."*
2. **Given** a condição preenchida num documento facultativo ou num documento da inscrição, **When**
   quem compõe pede a publicação, **Then** a publicação é impedida, com a razão.
3. **Given** a Ana convocada, **When** o conferente abre os documentos dela, **Then** o Alistamento
   oferece *conforme*, *pendente* e *não se aplica*; o Laudo, a certidão e os outros oferecem só
   *conforme* e *pendente*.
4. **Given** a Ana convocada, **When** um formulário forjado envia *"não se aplica"* para o Laudo,
   **Then** o comando recusa com `nao_se_aplica_sem_condicao`, e nada é gravado.

---

### User Story 2 — A inaplicabilidade se registra com o fato e com a condição (Priority: P1)

O conferente alocado, ao conferir a Ana, registra que o Alistamento não se aplica: o fato que a põe
fora da condição publicada (*"Candidata do sexo feminino, conforme o documento de identidade."*). A
tela mostra a condição publicada junto do campo. Se havia arquivo, o conferente o abre antes.

**Why this priority**: é a figura C funcionando, pelo papel que já confere, sem burocracia nova.

**Independent Test**: registrar o *"não se aplica"* do Alistamento da Ana pelo alocado, com e sem
arquivo, e verificar as recusas do motivo sem conteúdo e do arquivo não aberto.

**Acceptance Scenarios**:

1. **Given** o Alistamento da Ana a apresentar, **When** o alocado registra *"não se aplica"* com o
   motivo *"Candidata do sexo feminino, conforme o documento de identidade."*, **Then** o item fica
   *não se aplica após análise*, com o autor, a unidade e o instante, e o portal diz *"Não se aplica:
   Candidata do sexo feminino, conforme o documento de identidade."*
2. **Given** o mesmo item, **When** o motivo é `"."`, `"-"`, `"   "` ou só pontuação, **Then** o
   comando recusa com `motivo_sem_conteudo`, e nada é gravado.
3. **Given** a Ana apresentou um arquivo no Alistamento, **When** o alocado registra *"não se
   aplica"* sem ter aberto o arquivo, **Then** o comando recusa com `nao_se_aplica_sem_abertura`;
   depois de abrir, aceita, citando a versão e o hash julgados.
4. **Given** o Alistamento da Ana *não se aplica*, **When** ela tenta enviar um arquivo novo, **Then**
   o envio é recusado como o do documento já conferido (FR-3582 da `115`).
5. **Given** o Alistamento da Ana *não se aplica*, **When** o conferente o muda para *pendente*,
   **Then** o comando exige o motivo da substituição, haja ou não arquivo.

---

### User Story 3 — Quem registra o aceite vê cada inaplicabilidade e dá ciência (Priority: P1)

Na condução, a linha da Ana diz *"2 conformes · 1 não se aplica após análise · …"*, e não *"3
conferidos"*. Ao registrar o aceite, o gestor vê, antes do botão, o Alistamento: a condição
publicada, o motivo, quem registrou e quando. Ele marca a ciência e registra. Se outra pessoa mudou
uma conferência no meio, o aceite é recusado e a tela mostra a lista nova.

**Why this priority**: é a 7ª decisão. O aceite é o único ato irreversível do percurso, e hoje ele se
apoia numa leitura que não diferencia o conforme do afastado.

**Independent Test**: com o Alistamento *não se aplica* e os outros *conformes*, registrar o aceite
sem a ciência (recusa), com a ciência (aceita), e com a ciência de um conjunto superado (recusa).

**Acceptance Scenarios**:

1. **Given** a Ana com dois conformes e o Alistamento *não se aplica após análise*, **When** o gestor
   abre a condução, **Then** a linha diz os dois números separados, e o selo do *não se aplica* não é
   o do *conforme*.
2. **Given** o mesmo, **When** o gestor abre *Registrar desfecho*, **Then** o formulário mostra o
   bloco *"Documentos obrigatórios considerados não aplicáveis"* com o Alistamento, a condição, o
   motivo, o conferente e o instante.
3. **Given** o mesmo, **When** o gestor escolhe *Aceite* sem marcar a ciência, **Then** o comando
   recusa com `ciencia_das_inaplicabilidades`, e nada é gravado.
4. **Given** o gestor marcou a ciência, **When** outra pessoa registra um *"não se aplica"* novo antes
   do clique, **Then** o comando recusa com `inaplicabilidades_mudaram`, e a tela mostra o conjunto
   novo.
5. **Given** a ciência válida, **When** o aceite é registrado, **Then** a trilha do desfecho cita as
   conferências de que houve ciência, por identificador, sem o motivo.
6. **Given** a convocação sem nenhum *"não se aplica"* de obrigatório, **When** o gestor registra o
   aceite, **Then** nada muda em relação a hoje: não há bloco nem ciência.

---

### User Story 4 — O fora do recorte não se confere, e a formalização distingue as origens (Priority: P2)

O Laudo da Bia não se aplica pelo recorte. Nenhuma operação documental o alcança. Na formalização, o
Laudo da Bia aparece como *"não se aplica"*, e o Alistamento da Ana como *"não se aplica após
análise"*, com o instante da conferência. O manifesto continua sem o motivo.

**Why this priority**: fecha o achado lateral do estudo (9ª decisão) e o rastro que chega a quem
recebe a pessoa, sem ampliar o que a `117` expõe.

**Independent Test**: tentar conferir o Laudo da Bia pelo comando (recusa de inexistente); exportar a
Ana e a Bia e conferir as duas situações no manifesto.

**Acceptance Scenarios**:

1. **Given** o Laudo da Bia excluído pelo recorte, **When** um formulário forjado envia qualquer
   resultado para ele, **Then** o comando responde como recurso inexistente (404), e nada é gravado.
2. **Given** a Ana aceita com o Alistamento *não se aplica após análise*, **When** a formalização
   verifica e exporta, **Then** a página e o manifesto dizem *"não se aplica após análise"* para o
   Alistamento, com o instante da conferência na coluna que já existe, e *"não se aplica"* para o
   Laudo da Bia; o manifesto não tem o motivo.

---

### User Story 5 — O que já existe fica como está (Priority: P2)

O Edital publicado antes desta feature não tem condição: os obrigatórios dele são incondicionais.
Convocações abertas desse Edital seguem a regra nova; as encerradas não se reabrem nem se
reclassificam.

**Why this priority**: é a 8ª decisão, e é o que torna a mudança segura de aplicar.

**Independent Test**: com uma convocação aberta e outra decidida, ambas com *"não se aplica"*
registrado antes da feature num obrigatório incondicional, verificar que a decidida continua como
estava, e que a aberta deixa de atender ao aceite (11ª decisão).

**Acceptance Scenarios**:

1. **Given** uma convocação decidida com *"não se aplica"* num obrigatório incondicional, **When**
   qualquer tela a lê, **Then** ela continua decidida, e o item aparece como *"não se aplica após
   análise — registrado sem condição publicada"*.
2. **Given** uma convocação aberta no mesmo caso, **When** o gestor tenta o aceite, **Then** o item não
   conta como atendido, e a recusa diz *"registrado sem condição publicada"* (11ª decisão).
3. **Given** um Edital publicado sem condição, **When** se retifica para acrescentar a condição ao
   Alistamento, **Then** a condição vale para as chamadas seguintes, e a chamada aberta continua
   lendo a versão em que nasceu (FR-3573 da `115`).

---

### Edge Cases

- **Condição preenchida com espaços.** É condição ausente: o documento é incondicional.
- **Condição num documento que aproveita o da inscrição.** Vale: o aproveitamento é do arquivo, e a
  condição é da exigência. O item nasce *recebido* por referência, e o *"não se aplica"* pede a
  abertura da referência, como o *"conforme"*.
- **Condição num documento com recorte por modalidade.** Vale: é a submodalidade que a `044` não
  representa (a declaração da Funai só para o indígena, dentro de PPIQ). O que não tem condição, como
  o laudo do PcD, não se afasta.
- **Facultativo apresentado e sem sentido.** Não há *"não se aplica"* no facultativo. O conferente o
  marca *pendente*, com motivo, ou o deixa sem conferência, que adverte e não impede (FR-3592 da
  `115`).
- **"Não se aplica" depois do vencimento.** Continua aceito na chamada aberta (FR-3588 da `115`), mas
  só no condicional.
- **Duas pessoas conferindo ao mesmo tempo.** A conferência já é serializada pela trava do Processo e
  da inscrição; a ciência do aceite é conferida sob a mesma trava (FR-4468).
- **Correção da convocação pela `120`.** A sucessora usa a lista, as apresentações e as conferências
  da chamada (FR-3573 da `115`): a condição é a da versão da raiz, e o *"não se aplica"* continua
  valendo.
- **Nova chamada da mesma inscrição.** A lista nova lê a versão vigente, com a condição dela. O *"não
  se aplica"* da chamada anterior não viaja (decisão sobre aproveitamento entre chamadas da `115`):
  é juízo novo.
- **Retificação que muda o texto da condição.** Vale para as chamadas seguintes. A conferência
  registrada continua citando a versão da lista em que nasceu.
- **Retificação que retira a condição.** O documento volta a ser incondicional nas chamadas
  seguintes; as abertas não mudam.
- **Edital reaproveitado de anterior (`023`).** A condição vai junto, como os demais campos do
  Documento Exigido (FR-4455). A versão de origem anterior a esta feature chega sem condição, pelo
  degrau de elevação.
- **Perfil duplicado (`043`).** Nada muda: a duplicação não copia Documento Exigido (FR-645 da
  `043`).
- **Regularização.** Segue o aceite em tudo (FR-3592 da `115`).
- **Desfecho que não inclui.** Indeferimento, desistência e os demais não leem o estado documental
  (FR-3593 da `115`): não há bloco nem ciência.
- **Convocação sem lista**, do gesto de titulares antes da correção do PR #425. A recusa da lista
  incompleta vem antes de tudo o que esta spec acrescenta.

## Requirements *(mandatory)*

### Functional Requirements

#### A. A condição de exigência, na composição

- **FR-4451**: O Documento Exigido **da convocação** e **obrigatório** MAY declarar uma **condição de
  exigência**: um texto, como o Edital o publica, que diz em que caso ele é exigido. Sem condição, o
  documento é **incondicional**. Com condição, é **condicional** (D-001, D-002).
- **FR-4452**: A condição MUST ser texto declarativo. O sistema MUST NOT avaliá-la, decompô-la nem
  derivar dela campo, critério ou pergunta ao candidato. O texto é aparado, e o vazio depois de
  aparado é ausência (D-002).
- **FR-4453**: A condição em documento **facultativo** ou em documento **da inscrição** MUST ser
  recusada pela mesma regra em dois pontos: a gravação do rascunho recusa, e a conferência da
  publicação impede, com a razão. A segunda existe porque a Retificação alcança o documento sem passar
  pela tela (o molde é o do momento incoerente, FR-3566 da `115`) (D-004). A composição mostra o campo
  em todo documento, com a ajuda do UX-302: a tela não tem script (CSP), e a regra é do domínio.
  *Revista em 07/11/2026, na análise de consistência: a redação anterior mandava a composição esconder
  o campo, o que a tela sem script não faz.*
- **FR-4454**: A condição MUST aparecer, com o mesmo texto e junto do nome do documento, em toda
  superfície que apresenta o Documento Exigido da convocação: a revisão antes da publicação, o PDF
  oficial, a página pública do Edital, a tela da convocação no portal e a página dos documentos na
  gestão (UX-302). No PDF, ela segue o nome depois de vírgula, como os Editais a escrevem; o documento
  sem condição sai **byte a byte** como hoje.
- **FR-4455**: A condição MUST ser campo do Documento Exigido como os demais: persistida no
  rascunho, presente em todo Documento Exigido publicado (nula quando não há), no conteúdo canônico e
  no hash da versão, e levada pelo reaproveitamento de Edital anterior (`023`) sem tratamento próprio.
  O conteúdo publicado antes desta feature MUST ganhar a condição nula por um **degrau de elevação**,
  aditivo e sem invenção, no molde dos degraus do Documento Exigido da `044` e da `115`; o literal
  publicado não muda (D-012).
- **FR-4456**: A condição MUST ser **retificável**, como a obrigatoriedade e o recorte, na
  classificação do contrato de mutabilidade. A Retificação MUST alcançar só as chamadas seguintes: a
  lista gravada continua lendo a versão em que nasceu (FR-3573 da `115`; D-013).

#### B. A conferência

- **FR-4457**: O resultado *"não se aplica"* MUST estar disponível **só** em item da lista com
  situação **obrigatório** cujo requisito, **na versão da lista da chamada**, declara condição. Em
  item incondicional ou facultativo, a tela MUST NOT oferecê-lo, e o comando MUST recusá-lo com o
  código `nao_se_aplica_sem_condicao`, sem gravar nada (1ª e 4ª decisões; D-003, D-005). Revê a
  FR-3585 da `115`.
- **FR-4458**: O *"não se aplica"* MUST trazer o **motivo**, que diz o fato da pessoa que a põe fora
  da condição publicada. O motivo MUST ter conteúdo: ao menos uma palavra, isto é, uma sequência de
  letras ou algarismos. Motivo só de espaço, pontuação ou símbolo MUST ser recusado com
  `motivo_sem_conteudo`. A mesma regra vale para o motivo do *pendente*. O piso não é a salvaguarda:
  a salvaguarda é a condição publicada (FR-4457) e a ciência no aceite (FR-4468) (6ª decisão; D-006).
- **FR-4459**: O **fundamento** do *"não se aplica"* MUST ser o par **condição publicada + motivo**.
  A condição se lê da versão do item, e não se copia para a conferência. Toda superfície que mostra o
  fundamento a quem decide MUST mostrar os dois juntos: a página dos documentos e a confirmação do
  aceite (D-007).
- **FR-4460**: Com apresentação vigente no item, o *"não se aplica"* MUST exigir que o próprio
  conferente a tenha aberto **nesta chamada**, inclusive a apresentação por referência, pela mesma
  regra da FR-3611 da `115`. Sem a abertura, o comando MUST recusar com `nao_se_aplica_sem_abertura`.
  A conferência continua citando a apresentação e o hash julgados (FR-3585 da `115`) (5ª decisão;
  D-008).
- **FR-4461**: Autoria, unidade de atuação e instante MUST ser os que a conferência já grava. Esta
  spec MUST NOT acrescentar campo à conferência (D-011).
- **FR-4462**: A conferência que **substitui** uma conferência vigente *"não se aplica"*, e a que
  **registra** *"não se aplica"* sobre uma conferência vigente qualquer, MUST exigir o motivo da
  substituição, **haja ou não apresentação**. As demais substituições seguem a FR-3586 da `115` como
  estão (D-009).
- **FR-4463**: Com o item *"não se aplica"*, a apresentação de arquivo novo MUST continuar recusada
  como a do documento já conferido (FR-3582 da `115`). Para receber arquivo, a conferência se
  substitui primeiro (FR-4462).
- **FR-4464**: Toda operação documental da gestão sobre item com situação *não se aplica* **na lista**,
  isto é, excluído pelo recorte, MUST ser recusada **no comando** como recurso inexistente (FR-1101
  da `059`), sem gravar: conferência de qualquer resultado e abertura de apresentação. É a recusa que
  a apresentação já faz (FR-3582 da `115`) (9ª decisão; D-010).
- **FR-4465**: Quem registra o *"não se aplica"* MUST ser quem pode conferir, pelo predicado único da
  FR-3595 da `115`, sem mudança: a presidência, a permissão de gerir a comissão e o membro alocado à
  conferência (3ª decisão; D-005).

#### C. O aceite e a regularização

- **FR-4466**: A condução MUST mostrar as contagens de cada linha separadas em **conformes**, **não se
  aplica após análise**, **pendentes**, **para conferir** e **a apresentar**, e os facultativos à
  parte. O *"não se aplica"* MUST NOT ser somado aos conformes. O selo do item *"não se aplica após
  análise"* MUST ter apresentação própria, diferente da do *conforme*, na condução e na página dos
  documentos (UX-301). Revê a FR-3607 da `115`.
- **FR-4467**: O formulário de desfecho de uma convocação com ao menos um obrigatório *"não se
  aplica"* vigente MUST mostrar, antes do botão, o bloco **"Documentos obrigatórios considerados não
  aplicáveis"**, com, por item: o nome do documento, a condição publicada, o motivo, quem registrou,
  o instante e, se houver, a versão julgada (7ª decisão; UX-303).
- **FR-4468**: O **aceite** e a **regularização** de uma convocação com ao menos um obrigatório *"não
  se aplica"* vigente MUST exigir a **ciência expressa** de quem desfecha. O formulário carrega a
  assinatura do conjunto mostrado; o comando a recalcula **sob a trava do desfecho**, e recusa sem
  gravar:
  - com `ciencia_das_inaplicabilidades`, quando a ciência falta;
  - com `inaplicabilidades_mudaram`, quando o conjunto mudou desde a tela.

  Sem *"não se aplica"* de obrigatório, nada muda (D-014).
- **FR-4469**: O registro do aceite e da regularização na trilha MUST citar as conferências de que
  houve ciência, pelo identificador, e MUST NOT conter o motivo (FR-3603 da `115`; D-011).
- **FR-4470**: A guarda da FR-3592 da `115` MUST contar o *"não se aplica"* como atendido **só** em
  item condicional, pela versão da lista. O *"não se aplica"* vigente em item incondicional MUST NOT
  contar como atendido, e a recusa do aceite MUST dizer *"registrado sem condição publicada"* (11ª
  decisão; D-015).
- **FR-4471**: A ciência MUST ser parte do mesmo ato de desfecho, pela mesma base (FR-3596 da `115`).
  MUST NOT existir aprovação documental separada, segunda assinatura nem papel novo (3ª decisão).

#### D. Rastreabilidade, auditoria e formalização

- **FR-4472**: A origem da inaplicabilidade MUST ser derivável sem campo novo:
  - **pelo recorte**: a situação *não se aplica* do item na lista, gravada no ato de convocar;
  - **após análise**: a conferência vigente *"não se aplica"*, com autor, unidade, instante,
    apresentação e hash julgados, motivo, e a condição pela versão do item.

  O contrato completo está em [data-model.md](data-model.md) (D-011).
- **FR-4473**: A formalização MUST distinguir as duas origens na página, na verificação e no
  manifesto: *"não se aplica"*, pelo recorte, e *"não se aplica após análise"*, pela conferência. A
  segunda MUST trazer o instante da conferência na coluna que o manifesto já tem. O manifesto MUST
  continuar sem o motivo (FR-3687 da `117`). Nenhuma das duas torna a pessoa incompleta. Revê a
  FR-3672 da `117` (D-016).
- **FR-4474**: O auditor MUST ver na condução a contagem separada da FR-4466, pela base que a
  FR-3598 da `115` já lhe dá. Esta spec MUST NOT ampliar o acesso dele à página dos documentos nem ao
  motivo.

#### E. O portal

- **FR-4475**: No item obrigatório condicional, o portal MUST mostrar a condição publicada junto do
  nome. Enquanto o item estiver *a apresentar* e a chamada aberta, o texto MUST dizer que a comissão
  registra quando a condição não se aplica à pessoa, sem pedir o envio a quem a condição não alcança
  (UX-304). O texto do *"não se aplica"* conferido continua o da FR-3746 da `118`.

#### F. Transição

- **FR-4476**: Nenhuma conferência, desfecho, lista ou exportação já registrados MUST ser reescritos,
  reclassificados ou apagados. A convocação decidida continua decidida (8ª decisão).
- **FR-4477**: As versões publicadas antes desta feature MUST ser lidas como sem condição: todos os
  obrigatórios delas são incondicionais. Nenhuma condição MUST ser inferida das instruções do
  documento (D-012).
- **FR-4478**: O *"não se aplica"* registrado em item incondicional MUST aparecer, em toda leitura da
  gestão, como *"não se aplica após análise — registrado sem condição publicada"*.

### Requisitos de experiência

- **UX-301** — **O "não se aplica" não se parece com o "conforme".** Rótulo do item *"Não se aplica
  após análise"*, com selo próprio. Na condução, as contagens em frase única, na ordem: *"2 conformes
  · 1 não se aplica após análise · 1 pendente · 1 para conferir · 1 a apresentar"*, omitidos os
  zeros. Os facultativos vêm depois, à parte. O registrado em item incondicional, antes desta
  feature, leva o complemento *"— registrado sem condição publicada"* (FR-4478).
- **UX-302** — **A condição tem o mesmo texto em toda parte, e só onde existe.** Na composição, o
  campo *"Exigido somente quando"*, com a ajuda *"Só para documento obrigatório pedido na convocação.
  Escreva como o Edital publica: 'no caso de candidatos do sexo masculino, maiores de 18 anos'. O
  sistema não confere a condição: quem confere os documentos decide se ela alcança a pessoa."* No
  PDF, *"‹nome›, ‹condição› — ‹instrução›"*. Nas telas, a linha *"Condição publicada: ‹condição›."*
  logo abaixo do nome. Na conferência, a mesma linha fica junto da opção *"Não se aplica"*, e o campo
  do motivo diz *"Que fato da pessoa a põe fora da condição? A pessoa convocada lê este texto."*
- **UX-303** — **O bloco da confirmação diz o que está sendo aceito.** Título *"Documentos
  obrigatórios considerados não aplicáveis"*. Um item por documento, com *"‹nome› — condição
  publicada: ‹condição›. Motivo: ‹motivo›. Registrado por ‹pessoa› em ‹data e hora›"*, e *"(versão
  ‹n›)"* quando houve arquivo. A caixa da ciência diz *"Vi os documentos acima e registro o desfecho
  com eles considerados não aplicáveis."* Sem inaplicabilidade, o bloco não existe.
- **UX-304** — **No portal, a condição orienta e não manda enviar.** O item condicional *a
  apresentar*, com a chamada aberta, diz *"Obrigatório ‹condição›. Se for o seu caso, envie até
  ‹prazo›. Se não for, você não precisa enviar: a comissão registra."* Ele continua entre as tarefas,
  porque a comissão pode precisar do arquivo. Fechada a chamada, vale a coluna correspondente da
  FR-3746 da `118`.

### Key Entities

- **Documento Exigido** (`009`, `044`, `115`): ganha a **condição de exigência**, texto opcional, só
  no obrigatório da convocação.
- **Item da lista da convocação** (`115`): não muda. A condição se lê da versão que ele cita.
- **Conferência de documento** (`115`): não muda o registro. Muda quando o *"não se aplica"* é
  admitido, o piso do motivo e a exigência de abertura.
- **Desfecho da convocação** (`019`): não muda o registro. A ciência é verificada no comando e
  registrada na trilha do ato.
- **Ciência das inaplicabilidades**: a assinatura do conjunto de conferências *"não se aplica"*
  vigentes de obrigatórios que a tela mostrou. Não é registro: é conferida e citada na trilha.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1371**: Nos treze cenários da [matriz de cenários](contracts/cenarios.md), **nenhum** aceite
  nem regularização é registrado com um obrigatório incondicional atendido só por *"não se aplica"*.
- **SC-1372**: Em **100%** das confirmações de aceite com obrigatório *"não se aplica"*, quem desfecha
  vê cada um com a condição, o motivo, o autor e o instante antes do botão, e o aceite sem ciência,
  ou com ciência de um conjunto superado, grava **zero** registros.
- **SC-1373**: **Zero** conferências e **zero** aberturas são gravadas sobre item excluído pelo
  recorte, por qualquer caminho, inclusive o formulário forjado.
- **SC-1374**: Na formalização, as duas origens do *"não se aplica"* são distintas em **100%** das
  linhas da página e do manifesto, e o manifesto continua **sem** motivo de conferência.
- **SC-1375**: Num Edital com documento condicional, as **cinco** superfícies da FR-4454 mostram o
  **mesmo** texto da condição.
- **SC-1376**: **Nenhuma** linha de conferência, desfecho, lista ou exportação anterior à feature muda,
  e a suíte das tabelas append-only continua verde sem exceção nova.
- **SC-1377**: O número de consultas da condução e da página dos documentos **não cresce** com o número
  de convocações nem de itens, com e sem documento condicional.
- **SC-1378**: Um conferente que vê pela primeira vez a página dos documentos de uma pessoa com um
  documento condicional consegue dizer, **sem ajuda**, por que o *"não se aplica"* aparece num item e
  não nos outros.

## Assumptions

- O sistema não está em produção: não há acervo de convocações reais a transicionar (o mesmo
  pressuposto da decisão sobre lista retroativa da `115`). Os bancos de demonstração têm *"não se
  aplica"* gravados em itens incondicionais, e é deles que a 11ª decisão trata.
- A condição é escrita por quem compõe, como o Edital a publica. Ela é norma do Edital, e não dado
  pessoal: o texto é igual para todos.
- O motivo continua texto livre que o candidato lê (FR-3584 da `115`). Esta spec não muda o aviso
  sobre o texto livre que chega ao candidato.

## Proteção de dados (LGPD)

- **Nada de dado novo sobre a pessoa.** A condição é texto do Edital. O motivo já existia, com o mesmo
  alcance.
- **A trilha continua sem o motivo** (FR-3603 da `115`): a ciência cita identificadores (FR-4469).
- **O manifesto continua sem o motivo** (FR-3687 da `117`). A situação *"não se aplica após análise"*
  revela tanto quanto o *"não se aplica"* do recorte já revela: que a exigência não alcançou a
  pessoa, sem o porquê. Para o documento condicional, a condição publicada permite inferir o fato
  (*"não é do sexo masculino ou não é maior de 18 anos"*). Esse é o mesmo grau de inferência que o
  recorte por modalidade já produz para o laudo. O risco fica **registrado e pendente**, na P-3: não
  foi aceito.
- **O auditor não ganha acesso** (FR-4474).

## Compatibilidade com regras anteriores

| Spec | O que muda | O que fica |
|---|---|---|
| `044` | Nada no recorte. A decisão sobre a condição do candidato continua: a condição publicada não é forma estruturada, não se avalia e não entra na aplicabilidade. O *"facultativo com instrução"* continua disponível, e passa a ter uma alternativa no documento da convocação | A lista gravada da inscrição, o recorte transversal |
| `115` | FR-3585 (quando o *"não se aplica"* existe), FR-3586 (substituição que envolve o *"não se aplica"*), FR-3592 (o que atende, pela 11ª decisão), FR-3607 (contagens), o caso-limite *"Obrigatório marcado 'não se aplica'"* | A lista congelada (FR-3573), o predicado único (FR-3595), o alocado que não desfecha (FR-3596), a trilha sem motivo (FR-3603), o *"conforme"* com abertura (FR-3611) |
| `117` | FR-3672 (sétima situação) | O manifesto sem motivo (FR-3687), o alcance de quem formaliza |
| `118` | A tela da convocação mostra a condição no item condicional (FR-4475), com uma linha nova na tabela de textos da FR-3746 | A categoria *conferido* do *"não se aplica"* (FR-3722), o texto *"Não se aplica: ‹motivo›."* |
| `120` | Nada | A sucessora herda lista, apresentações e conferências |
| `125` | Nada | O aviso de texto que chega ao candidato |
| `026` | Uma linha nova na matriz dos campos do Documento Exigido: a condição, retificável | O contrato e a regra de toda natureza declarada |
| `001` | O esquema publicado `DocumentoExigidoPublicado` ganha a condição | Os demais campos |
| `023` | Nada: o reaproveitamento já leva toda chave do documento | O remapeamento de identificadores |
| `043` | Nada: a duplicação não copia documento | — |
| `070` | A tabela de cobertura das dúvidas classifica o campo novo, e a versão do esquema sobe | O assistente não responde sobre a condição sem classificá-la |

## Revisões de requisitos anteriores

As revisões são escritas nos arquivos das specs afetadas na implementação, com a marca *"revista pela
`131`"*, e listadas aqui (T007, T019 e T030 em [tasks.md](tasks.md)):

- **FR-3585 da `115`**: *"não se aplica, com motivo obrigatório"* passa a *"não se aplica, só no
  obrigatório condicional (FR-4457 da `131`), com motivo que tem conteúdo (FR-4458 da `131`)"*.
- **FR-3586 da `115`**: acrescenta a exceção da FR-4462 da `131`.
- **FR-3592 da `115`**: *"conforme ou não se aplica"* passa a *"conforme, ou não se aplica em item
  condicional (FR-4470 da `131`)"*, e o aceite com *"não se aplica"* pede a ciência da FR-4468 da
  `131`.
- **FR-3607 da `115`**: as contagens da FR-4466 da `131`.
- **Caso-limite *"Obrigatório marcado 'não se aplica'"* da `115`**: *"Conta como atendido para o
  aceite"* passa a *"Conta como atendido só no condicional, com ciência no aceite"*.
- **FR-3672 da `117`**: a sétima situação, *não se aplica após análise* (FR-4473 da `131`).
- **FR-3746 da `118`**: a linha do obrigatório condicional *a apresentar* (FR-4475 da `131`).

## Decisões

Propostas de desenho desta spec, com o comportamento **aprovado pelo usuário em 07/11/2026** (10ª
decisão). As alternativas descartadas estão na
[pesquisa](research.md).

### D-001 — A condicionalidade se representa no Edital (opção 2), e não só na conferência (opção 1)

O Documento Exigido da convocação ganha a condição de exigência, e o *"não se aplica"* da conferência
existe só onde ela foi publicada. A opção 1 (motivo vinculado, permissão, ciência, sem mudar a
composição) torna o afastamento arbitrário **visível**, mas não **impossível**: sem o Edital dizer
o que é condicional, o comando não tem como recusar o *"não se aplica"* do laudo do PcD sem recusar
também o do alistamento militar. Visibilidade depende de quem desfecha ler com atenção cada aceite. A
regra no comando não depende. A comparação completa está em R-001.

### D-002 — A condição é texto publicado, não regra

Um campo de texto, e nada mais: sem tipo, sem lista de condições, sem campos da pessoa, sem avaliação.
É o que a decisão sobre a condição do candidato da `044` admite, porque não é forma estruturada. O
sistema usa o campo para três coisas: publicá-lo, congelá-lo pela versão da lista e decidir se o
*"não se aplica"* existe. Ele não sabe o que a condição diz.

### D-003 — As quatro figuras, e onde cada uma mora

| Figura | Onde mora | Quem decide |
|---|---|---|
| A — excluído pelo recorte | situação do item na lista | ninguém: é derivada (FR-3572 da `115`) |
| B — obrigatório incondicional | Documento Exigido sem condição | ninguém o afasta: só *conforme* atende |
| C — obrigatório condicional | Documento Exigido com condição | quem confere, com o motivo; quem desfecha dá ciência |
| D — dispensa excepcional | **em lugar nenhum** | decisão institucional, fora do sistema (2ª decisão) |

**O GPS não oferece substituto para a dispensa.** As operações que já existem não são respostas
intercambiáveis a um caso excepcional, e esta spec não as recomenda como tal:

- a correção da convocação com prazo novo (FR-3618 da `115`);
- o indeferimento;
- a Retificação.

Cada uma continua exigindo o fundamento próprio, na regra que a rege. Em particular, **a limitação do
GPS não fundamenta indeferimento**: o sistema não ter como registrar uma exceção não é razão para
indeferir quem dela trataria.

### D-004 — Só o obrigatório da convocação tem condição

- **Facultativo:** a condição não muda nada, porque o facultativo não impede o aceite. Admiti-la
  criaria um *"não se aplica"* sem efeito na guarda, mas com efeito na formalização.
- **Inscrição:** o obrigatório da inscrição impede o **envio** da inscrição, sem conferência
  humana antes. Uma condição ali exigiria que o candidato declarasse o fato, e isso é a pergunta ao
  candidato que a 3ª decisão exclui.

### D-005 — O alocado registra o "não se aplica" do condicional

É uma das sete decisões do estudo (a 2ª, ver R-008). A âncora agora é a condição publicada, e não a
discricionariedade de quem confere. O alocado faz o mesmo juízo de fato que faz no *conforme*: a
pessoa está ou não no caso descrito. Restringir à base de gestão deixaria a presidência conferindo
cada mulher no alistamento militar de uma chamada de dezenas, que é o que a decisão sobre quem confere
da `115` quis evitar. O controle está no aceite (D-014).

### D-006 — O motivo tem piso de conteúdo, e o piso não é a salvaguarda

Recusar o que não tem palavra nenhuma (`"."`, `"-"`, `"..."`) é barato e fecha o caso que o estudo
reproduziu. Ir além (tamanho mínimo, lista de frases proibidas, motivo diferente da condição) só
produz textos mais longos sem conteúdo (*"Não se aplica ao caso."*). A 6ª decisão pede vinculação, e
ela vem da FR-4457 e da FR-4459. O piso vale também para o *pendente*, cujo motivo o candidato lê
para corrigir.

### D-007 — O fundamento não se copia

A condição está na versão consolidada citada pelo item, que é imutável. Copiá-la para a conferência
seria um segundo lugar para o mesmo texto, e as duas cópias poderiam divergir numa leitura errada da
versão. A conferência cita o item, o item cita a versão, e a versão tem a condição.

### D-008 — Com arquivo, abre antes

É a 4ª das decisões do estudo (ver R-008). O arquivo pode ser a prova de que a condição **se**
aplica: o homem maior de 18 anos que mandou o certificado de reservista. Afastar sem olhar é decidir
contra a evidência que está no processo. A regra é a do *conforme* (FR-3611 da `115`), e a razão que
a decisão sobre a abertura da `115` deu para dispensar o *"não se aplica"* — *"o documento pode nem ter
sido apresentado"* — não cobre o caso em que ele foi. Sem arquivo, nada muda: a 5ª decisão diz que o
arquivo, sozinho, não decide.

### D-009 — Mudar um "não se aplica", ou chegar a um, sempre pede motivo

A FR-3586 da `115` compara versões, e por isso o item sem arquivo trocava *pendente* por *não se
aplica* sem motivo de substituição. O estudo reproduziu isso. O teste
`test_a_pendencia_sem_arquivo_nao_pede_motivo_de_revisao` prende essa liberdade para a pendência, e
ela continua: a exceção é só a que envolve o *"não se aplica"*, que mexe na guarda do aceite.

### D-010 — O fora do recorte é inexistente para a gestão, como já é para o candidato

A causa do achado é uma linha ausente. `apresentar` recusa o item *não se aplica* da lista
(`convocacao/application/documentos.py:482`), e `conferir` nunca olha a situação do item. A recusa
nova é a mesma, no mesmo ponto do comando, com a mesma resposta de inexistente: o item fora do
recorte não é pedido, e não há o que conferir.

### D-011 — Rastreabilidade sem campo novo

Tudo o que o contrato da tarefa pede já está gravado: o resultado, o motivo, o autor, a unidade, o
instante, a apresentação e o hash na conferência; a origem automática na situação do item; a condição
na versão. O que falta está nas **projeções**: a contagem da condução, o selo, a confirmação do
aceite, a formalização. E falta a **ciência**, que vai para a trilha do desfecho por identificador. A
tabela está em [data-model.md](data-model.md).

### D-012 — O que já foi publicado não tem condição, e nenhuma se infere

Ler a condição das instruções (*"apenas para candidatos do sexo masculino"*) seria o sistema
interpretando texto livre, contra a D-002, e transformaria a instrução de todos os Editais publicados
em regra sem que ninguém a tenha publicado como regra.

### D-013 — A condição é retificável, e a Retificação não alcança a chamada aberta

A condição muda a quem a exigência se aplica, como a obrigatoriedade e o recorte, que a `115` já
classificou como retificáveis com efeito nas chamadas seguintes (decisão sobre momento e
aproveitamento da `115`). A chamada aberta continua lendo a versão em que nasceu (FR-3573 da `115`).
Antecipar a Retificação na chamada aberta pelo *"não se aplica"* é a 5ª das decisões do estudo, e a
recomendação é não fazê-lo (R-008).

### D-014 — A ciência é a assinatura do que se viu, conferida sob a trava

É o padrão da prévia assinada da correção pela `120`: a tela leva a assinatura do conjunto que
mostrou, e o comando a recalcula com o que o ato vai usar. A ciência não é estado, não tem tabela e
não é aprovação: é a prova, no próprio ato, de que quem desfecha viu o que está decidindo. Uma caixa
de seleção sem assinatura provaria só que alguém marcou a caixa, inclusive diante de um conjunto que
mudou depois.

### D-015 — A guarda conta o "não se aplica" só no condicional

Sem isto, o *"não se aplica"* gravado antes da feature num obrigatório incondicional continuaria
abrindo o aceite, e a regra nova valeria só para conferências novas. A guarda lê a versão da lista,
como a FR-4401 da `115` lê. As linhas antigas em chamadas abertas deixam de atender (P-1, 11ª
decisão).

### D-016 — Na formalização, a origem vai e o motivo fica

A FR-3687 da `117` tirou o motivo do manifesto por minimização, e a razão continua. O setor que
recebe a pessoa precisa saber que um obrigatório não veio **por decisão** da comissão, e quando, para
perguntar a ela se precisar. Não precisa do texto. O estudo de 07/11 recomendava levar o motivo, e
esta spec o corrige: a FR-3687 da `117` o proíbe.

## Pendências do usuário

**Decididas em 07/11/2026:**

- **P-1** — o *"não se aplica"* já gravado em obrigatório incondicional, numa chamada aberta, **não**
  atende ao aceite (11ª decisão; FR-4470). As alternativas descartadas eram contá-lo com a ciência,
  ou adiar a regra para uma data.
- A antiga **P-2** foi absorvida pela 2ª decisão (12ª decisão); a redação está na D-003.

**Não impedem:**

- **P-3** — O grau de inferência da situação *"não se aplica após análise"* no manifesto (LGPD).
  Pendente. O que esta spec recomenda é aceitar o risco, pelo mesmo grau de inferência que o recorte já
  produz. A alternativa é omitir do manifesto a linha do documento condicional não aplicável. Enquanto
  o usuário não decidir, a FR-4473 vale como está escrita, e o risco não conta como aceito.
- **P-4** — O fato já comprovado ao Ifes (Lei 14.129/2021, art. 3º, XIII). Recomendação: o Edital o
  publica como condição (*"exceto para quem concluiu o ensino médio no Ifes"*), e a conferência o
  aplica. A aplicação da lei ao caso continua sendo da Procuradoria.

## Registrado, sem desenvolver

- O auditor abrir a página dos documentos e o motivo (a pendência sobre o auditor da `115`).
- O texto do motivo que chega ao candidato, que a `125` registrou para decisão própria.
- O *"não se aplica"* do recorte aparecer no manifesto revela a modalidade por exclusão, o que a
  FR-3687 da `117` proíbe dizer por extenso. Não é desta spec, mas a P-3 o toca.
