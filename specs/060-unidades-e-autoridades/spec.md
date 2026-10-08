# Feature Specification: Unidades institucionais e autoridades de publicação

**Feature Branch**: `claude/edital-signature-responsible-60ecf3`

**Created**: 2026-10-06

**Status**: Draft

**Input**: conversa de 06/10/2026 sobre a assinatura do Edital. O produto é institucional do Ifes
— Reitoria, cerca de 25 campi e o Cefor —, e não do Cefor só. O sistema ainda não opera, nem em
teste: não há dado em produção. A identidade documental do Cefor está fixa no código e precisa sair
antes da primeira operação, porque o que se publica é imutável.

> **Faixa de identificadores.** Abre em **FR-1106**, **SC-429** e **UX-148**, contíguos. O teto
> medido em 06/10/2026 em todas as worktrees era mil cento e cinco para os requisitos funcionais,
> quatrocentos e vinte e oito para os critérios de sucesso e cento e quarenta e sete para os de
> experiência, tomados pela `059-acesso-a-convocacao`, ainda noutra worktree e sem merge — por isso
> escritos por extenso. O número da pasta seguiu o mesmo caminho: `059` estava tomado. As decisões
> reiniciam em `D-001`.

> **Uma pergunta continua com o Cefor, e não bloqueia esta feature**: depois de gerado pelo sistema,
> qual artefato é o documento oficial, e onde ele é formalizado e assinado. Esta feature responde
> **quem responde pelo ato**; não responde **como o ato é assinado**.

---

## Clarifications

### Session 2026-10-06

- Q: Qual papel cadastra, corrige e encerra as autoridades da unidade? → A: O **Gestor da própria
  unidade**, sem impedimento adicional e sem papel novo. Manter autoridades é configuração
  administrativa da unidade, não ato de publicação: cadastrar não confere competência de publicar nem
  altera publicação anterior. Se o Ifes determinar gestão centralizada ou segregação dessa função, a
  permissão é destacada para outro papel sem mudar o modelo de dados (`FR-1122`, `D-005`).

---

## Por que esta feature existe

**O sistema sabe separar unidades, e não sabe dizê-las.** O escopo institucional já existe: quem
opera tem um, o Processo Seletivo e o Edital têm um, a trilha de auditoria tem um, a numeração do
Edital é única por escopo, número e ano, e toda leitura da gestão filtra por ele (`033`, FR-487). Mas
o escopo é só um texto — hoje, `"cefor"` —, sem nada por trás. Tudo o que um documento precisa dizer
sobre a unidade está escrito no código, como se só existisse uma:

- **O cabeçalho.** As quatro linhas do órgão — *Ministério da Educação · Instituto Federal do
  Espírito Santo · Centro de Referência em Formação · e em Educação a Distância* — são constantes, e
  saem iguais no Edital, no consolidado da Retificação, no documento de resultado e no comprovante de
  inscrição. Um Edital do Campus Serra sairia com o cabeçalho do Cefor.
- **O local do ato.** *"Vitória (ES)"* é constante desde a `054` (FR-989), que o justificou assim: *o
  Cefor publica de Vitória, e nenhum cadastro de praça é criado*.
- **Quem responde pelo ato.** A autoridade é escolhida num catálogo declarado em código (`007`,
  FR-039), com três entradas — Reitora, Pró-Reitor de Ensino e Diretora-Geral do Cefor —, sem nome,
  sem portaria e com identificadores fictícios. Qualquer pessoa com permissão de publicar escolhe
  qualquer uma das três, de qualquer unidade. Trocar quem responde por uma unidade exige mudar o
  código e implantar de novo.

Cada uma dessas escolhas estava certa para um sistema de uma unidade só, e as três foram registradas
como tal. A premissa mudou.

**E há um prazo.** O documento publicado não se regenera, e a Publicação é imutável: um Edital de
campus publicado com o cabeçalho do Cefor carrega o erro para sempre, e só o corrige por Retificação
pública. Antes da primeira operação, mudar é barato — não há dado a migrar, e o único escopo que
existe vira a primeira unidade. Depois, o catálogo em código tende a crescer uma entrada por campus,
e a solução provisória vira arquitetura por inércia.

**O que não muda.** O escopo institucional continua sendo o que é, e as regras que já dependem dele
— isolamento, numeração, autorização — não são tocadas. A Publicação continua guardando, no ato,
tudo o que diz quem respondeu por ele; a autoridade pode mudar depois, e a Publicação não. Nenhuma
assinatura é criada (`008`, FR-037). Nenhum documento já publicado é regenerado.

---

## User Scenarios & Testing *(mandatory)*

**Atores.** Quem mantém as autoridades de uma unidade; quem publica (Edital, Retificação e
Resultado), que escolhe a autoridade; quem lê o documento publicado — candidato, auditor, cidadão.
Quem mantém o registro de unidades é a equipe que implanta o sistema (`D-002`).

### User Story 1 — O documento diz a unidade que o praticou (Priority: P1)

Um Edital do Campus Serra é publicado. O documento abre com o cabeçalho do Campus Serra e fecha com
o local do Campus Serra. O mesmo vale para a Retificação, o documento de resultado e o comprovante
de inscrição desse Edital. Um Edital do Cefor continua saindo exatamente como sai hoje.

**Why this priority**: é o defeito que se torna permanente na primeira publicação de outra unidade.
Sem ele, nenhuma das outras histórias impede o documento oficial errado.

**Independent Test**: com duas unidades registradas, publicar um Edital em cada e conferir que cada
documento traz o cabeçalho e o local da própria unidade, e nenhum traço da outra; e que o documento
do Cefor é idêntico, byte a byte, ao que a fixture de referência da `054` fixou.

**Acceptance Scenarios**:

1. **Given** um Edital de uma unidade registrada, **When** ele é publicado, **Then** o cabeçalho do
   documento traz as linhas institucionais comuns e as linhas da unidade **and** o local do ato é o
   da unidade.
2. **Given** um Edital do Cefor, **When** ele é publicado, **Then** o documento é idêntico ao que o
   sistema produzia antes desta feature, para o mesmo conteúdo, data e autoridade.
3. **Given** um Edital publicado e uma Retificação dele, **When** a unidade é renomeada entre os dois
   atos, **Then** o documento original continua com o nome do dia em que foi publicado **and** o da
   Retificação traz o nome do dia da Retificação.
4. **Given** uma Inscrição num Edital do Campus Serra, **When** o candidato baixa o comprovante,
   **Then** ele identifica o Campus Serra, como a Publicação da versão que o candidato aceitou o
   identifica.
5. **Given** um resultado divulgado de um Edital do Campus Serra, **When** leio o documento, **Then**
   o cabeçalho é o do Campus Serra.

---

### User Story 2 — Publicar escolhendo só quem pode responder por aquela unidade (Priority: P1)

Quem publica um Edital do Campus Serra vê, na escolha da autoridade, apenas as autoridades
habilitadas para o Campus Serra e vigentes hoje — com cargo, nome e ato de nomeação. Uma autoridade
do Campus Vitória não aparece; e, se chegar ao servidor por manipulação da requisição, é recusada.

**Why this priority**: é a garantia de escopo que falta hoje. Com mais de uma unidade, a lista única
deixaria qualquer operador atribuir o ato a qualquer autoridade do Ifes.

**Independent Test**: com autoridades em duas unidades, abrir a publicação de um Edital de cada e
conferir as opções; enviar à mão a autoridade da outra unidade, e a de vigência encerrada, e
conferir a recusa sem nada gravado.

**Acceptance Scenarios**:

1. **Given** um Edital homologado do Campus Serra, **When** abro o ato de publicar, **Then** a lista
   oferece somente as autoridades habilitadas para o Campus Serra, vigentes na data de hoje.
2. **Given** a mesma tela, **When** envio o identificador de uma autoridade de outra unidade,
   **Then** a publicação é recusada **and** nenhuma Publicação é gravada.
3. **Given** uma autoridade cuja vigência terminou ontem, **When** tento publicar com ela, **Then** a
   recusa diz que a autoridade não está vigente.
4. **Given** uma unidade sem nenhuma autoridade vigente, **When** abro o ato de publicar, **Then** a
   tela diz que não há autoridade vigente para a unidade e qual permissão a cadastra, **and** o ato
   não pode ser confirmado.
5. **Given** os três fluxos que pedem autoridade — Edital, Retificação e Resultado —, **When**
   publico em cada um, **Then** as mesmas regras de escolha e de recusa valem nos três.

---

### User Story 3 — Manter as autoridades da unidade sem mudar o sistema (Priority: P2)

A Diretora-Geral de um campus muda. Quem mantém as autoridades do campus encerra a vigência da
anterior e cadastra a nova — nome, cargo, ato de nomeação e início da vigência. A próxima publicação
já oferece a nova, e nenhuma publicação anterior muda.

**Why this priority**: é o que torna as histórias 1 e 2 sustentáveis em 26 unidades. Sem ela, cada
troca de gestão voltaria a ser mudança de código.

**Independent Test**: cadastrar uma autoridade, publicar com ela, encerrá-la, cadastrar outra e
publicar de novo; conferir que a primeira Publicação continua dizendo a primeira autoridade, que a
segunda diz a segunda, e que a trilha de auditoria registra cadastro e encerramento.

**Acceptance Scenarios**:

1. **Given** a permissão de manter autoridades na minha unidade, **When** cadastro uma autoridade
   com cargo e início de vigência, **Then** ela passa a ser oferecida nas publicações da unidade a
   partir daquele dia.
2. **Given** uma autoridade vigente, **When** encerro a vigência informando a data de fim, **Then**
   ela deixa de ser oferecida a partir do dia seguinte **and** continua listada como encerrada.
3. **Given** uma autoridade já usada numa Publicação, **When** tento corrigir nome, cargo, ato de
   nomeação ou início da vigência, **Then** a correção é recusada e a tela orienta a encerrar e cadastrar outra.
4. **Given** uma autoridade ainda não usada, **When** corrijo o ato de nomeação, **Then** a correção
   é gravada **and** a trilha guarda o valor anterior e o novo.
5. **Given** que tenho a permissão em outra unidade, **When** tento ver ou alterar as autoridades
   desta unidade, **Then** o sistema responde como se elas não existissem.
6. **Given** uma Publicação praticada com uma autoridade, **When** essa autoridade é encerrada ou
   tem outra cadastrada no lugar, **Then** a Publicação, a consulta pública dela e o documento não
   mudam em nada.

---

### User Story 4 — A consulta pública diz a unidade do ato (Priority: P3)

Quem consulta uma Publicação vê, além de quem respondeu pelo ato, a unidade que o praticou, como
estava no dia.

**Why this priority**: completa a rastreabilidade pública, mas o documento publicado já a carrega.

**Independent Test**: consultar a Publicação de um Edital de cada unidade e conferir unidade,
autoridade e ato de nomeação.

**Acceptance Scenarios**:

1. **Given** uma Publicação, **When** a consulto, **Then** vejo a unidade (sigla e nome), a
   autoridade (nome, quando houver, e cargo) e o ato de nomeação, quando houver.

---

### Edge Cases

- **Autoridade de outra unidade que assina por esta.** O Reitor pode responder por um Edital de
  campus. O registro não pergunta onde a pessoa está lotada: pergunta por quais unidades ela pode
  responder. O Reitor é cadastrado como autoridade habilitada naquela unidade, com o fundamento no
  ato de nomeação (`D-003`).
- **Delegação de competência.** É dita no campo do ato de nomeação — *"Portaria nº …, delegação de
  competência para …"*. O sistema a registra e não a interpreta.
- **Duas autoridades vigentes ao mesmo tempo na mesma unidade.** É o caso comum — Diretor-Geral e
  Reitor —, e é permitido. Quem publica escolhe.
- **Vigência que termina no dia da publicação.** O dia de fim é o último dia em que a autoridade
  responde; a data do ato é a da Publicação, no fuso institucional.
- **Vigência futura.** Cadastrada hoje com início na semana seguinte, a autoridade só é oferecida a
  partir do início.
- **Encerramento retroativo.** Recusado (FR-1120). Uma autoridade cadastrada por engano e nunca
  usada se corrige (FR-1121) ou se encerra com o fim de hoje.
- **Escopo sem unidade registrada.** Um operador cujo escopo não tem unidade registrada não cria
  Processo Seletivo nem Edital; a recusa diz que a unidade não está registrada no sistema.
- **Unidade desativada.** Não recebe Processo Seletivo novo. O que já existe nela continua operando
  até o fim — interromper um certame em curso seria efeito que ninguém decidiu —, e as Autoridades
  dela continuam sendo mantidas por quem tem a permissão naquele escopo, para que o certame tenha
  quem responda pelos atos que faltam.
- **Unidade renomeada.** O nome novo vale para os atos seguintes. Os documentos e as Publicações
  anteriores ficam com o nome do dia.
- **Prévia do documento antes de publicar.** Usa a unidade do Edital como está registrada no
  momento da prévia; o que vale é o que a Publicação congela.
- **Resultado divulgado antes desta feature.** Não há dado em produção; no banco de demonstração, o
  acervo é re-semeado, e nenhum caminho de conversão é construído.

## Requirements *(mandatory)*

### Unidade

- **FR-1106**: O sistema MUST registrar **Unidades** institucionais, cada uma com: código estável,
  sigla, nome por extenso, as linhas que o nome ocupa no cabeçalho dos documentos (uma ou duas), o
  local do ato (cidade e UF) e a situação (ativa ou desativada).
- **FR-1107**: O código da Unidade MUST ser o valor do escopo institucional que já existe nos
  operadores, nos Processos Seletivos, nos Editais e na auditoria. A Unidade **materializa** esse
  escopo; NÃO o substitui. As regras de isolamento, autorização e numeração que leem o escopo MUST
  continuar como estão.
- **FR-1108**: O código da Unidade MUST ser imutável depois de registrado. Nome, sigla, linhas do
  cabeçalho, local e situação MAY mudar, e cada mudança MUST ser registrada com o valor anterior, o
  novo, quem e quando.
- **FR-1109**: Nenhuma Unidade MUST ser excluída. Retirar uma unidade de uso é desativá-la.
- **FR-1110**: Criar Processo Seletivo ou Edital MUST ser recusado quando o escopo do operador não
  corresponder a Unidade registrada e ativa. Atos sobre Processos e Editais que já existem numa
  Unidade desativada MUST continuar possíveis, e manter as Autoridades dela — cadastrar, corrigir e
  encerrar — também, com as mesmas exigências de permissão e de escopo (FR-1122): sem elas, o
  certame em curso não teria quem respondesse pelos seus atos.
- **FR-1111**: A primeira Unidade registrada MUST ser o Cefor, com o código `cefor`, as linhas de
  cabeçalho e o local que o sistema imprime hoje.

### O documento diz a unidade

- **FR-1112**: O cabeçalho de todo documento que hoje imprime o órgão — o Edital publicado e a sua
  prévia, o consolidado da Retificação, o documento de resultado e o comprovante de inscrição — MUST
  ser composto pelas linhas institucionais comuns (*Ministério da Educação* e *Instituto Federal do
  Espírito Santo*) seguidas das linhas da Unidade do Edital.
- **FR-1113**: O local do ato no fecho do documento publicado MUST ser o local da Unidade do Edital.
  *Emenda a `FR-989` da `054`, que o fixava como constante do compositor.*
- **FR-1114**: Para o Cefor, o documento produzido MUST ser idêntico, byte a byte, ao que o sistema
  produz antes desta feature para o mesmo conteúdo, data e autoridade. A fixture de bytes da `054`
  MUST continuar passando sem ser refeita.
- **FR-1115**: O comprovante de inscrição MUST identificar a Unidade como a registrou a Publicação
  que originou **a versão do Edital aceita pelo candidato** — e não como o registro de Unidades
  estiver no momento do download, nem como a Publicação mais recente a registrar. O comprovante
  prova o que o candidato aceitou.

### Autoridade

- **FR-1116**: O sistema MUST registrar **Autoridades habilitadas** por Unidade, cada uma com:
  Unidade, cargo (obrigatório), nome (opcional, como na `054`, FR-992), ato de nomeação ou
  fundamento (opcional, texto livre), início de vigência (obrigatório) e fim de vigência (opcional).
  O registro MUST conter só isso — sem CPF, matrícula, contato ou foto (`007`, FR-044).
- **FR-1117**: Cada Autoridade MUST ter identificador gerado pelo sistema, nunca digitado nem exibido
  ao operador. Os identificadores fictícios do catálogo declarado MUST deixar de existir.
- **FR-1118**: A Autoridade habilitada numa Unidade responde **pelos atos daquela Unidade**,
  independentemente de onde a pessoa esteja lotada. A mesma pessoa MAY estar habilitada em mais de
  uma Unidade, por registros distintos.
- **FR-1119**: Uma Autoridade MUST ser considerada **vigente** numa data quando a data não for
  anterior ao início nem posterior ao fim, contados no fuso institucional.
- **FR-1120**: Encerrar a vigência MUST ser a única forma de retirar uma Autoridade de uso. Nenhuma
  Autoridade MUST ser excluída. O fim de vigência NÃO PODE ser anterior ao início **nem anterior ao
  dia do encerramento**, no fuso institucional: o registro não pode passar a dizer que uma
  autoridade não estava vigente no dia em que praticou um ato. O fim é **inclusivo** — encerrar com
  fim hoje mantém a autoridade disponível hoje e a retira das opções a partir de amanhã.
- **FR-1121**: Nome, cargo, ato de nomeação e início de vigência de uma Autoridade MAY ser
  corrigidos enquanto ela não tiver sido usada em nenhum ato. Depois do primeiro uso, MUST ser
  recusados, e a recusa MUST dizer que a correção se faz encerrando esta e cadastrando outra. A
  Unidade de uma Autoridade nunca muda.
- **FR-1122**: Cadastrar, corrigir e encerrar Autoridade MUST exigir permissão própria, concedida ao
  **Gestor** e limitada ao escopo do operador: Autoridades de outra Unidade MUST ser indistinguíveis
  de inexistentes. Nenhum papel novo é criado (`D-005`). Ter a permissão NÃO concede competência de
  publicar, e publicar NÃO concede a de manter Autoridades.
- **FR-1123**: Cadastro, correção e encerramento de Autoridade MUST gerar evento de auditoria com
  ator, Unidade, Autoridade, valores anterior e posterior, data e hora.
- **FR-1124**: O catálogo declarado em código (`007`, FR-039) MUST deixar de existir.
  *Revoga a `FR-039` da `007` e a parte da decisão 005 da `054` que mantinha nome e ato de nomeação
  no catálogo.* O registro inicial das Autoridades do Cefor — as três que o catálogo tem hoje, com
  o cargo que têm, enquanto o Cefor não fornecer nome e portaria — é **passo de implantação**, feito
  pela tela por quem tem a permissão (quickstart §7), e não migração de dados: Autoridade é dado
  operacional (`D-005`).

### Publicar com a autoridade da unidade

- **FR-1125**: Ao publicar Edital, Retificação ou Resultado, a escolha MUST oferecer somente as
  Autoridades habilitadas na Unidade do Edital e vigentes na data do ato.
- **FR-1126**: A verificação MUST ser do domínio, na mesma transação que grava a Publicação:
  autoridade de outra Unidade, fora de vigência ou inexistente MUST ser recusada, e nada MUST ser
  gravado. Uma autoridade encerrada entre a abertura da tela e a confirmação MUST ser recusada.
- **FR-1127**: Sem nenhuma Autoridade vigente na Unidade, o ato de publicar MUST ficar indisponível,
  e a tela MUST dizer por quê e qual permissão cadastra autoridades, no padrão das recusas que nomeiam
  a permissão (`037`, FR-543).

### A Publicação continua autocontida

- **FR-1128**: Toda Publicação de Edital, de Retificação e de Resultado MUST congelar, no ato, a
  autoridade — identificador, nome, cargo e ato de nomeação — e a Unidade — código, sigla, nome,
  linhas do cabeçalho e local — tal como estavam no momento. A Publicação de Resultado MUST passar a
  congelar também o ato de nomeação, que hoje não guarda.
- **FR-1129**: Nenhuma mudança posterior na Unidade ou na Autoridade MUST alterar Publicação,
  documento publicado ou consulta pública de ato já praticado.
- **FR-1130**: O consolidado da Retificação MUST usar a Unidade e a autoridade congeladas na própria
  Retificação, coerente com a `FR-043` da `008`.
- **FR-1131**: A consulta pública de uma Publicação MUST exibir a Unidade congelada (sigla e nome)
  ao lado de quem respondeu pelo ato, com a regra de exibição sem nome da `054` (FR-994).

### Experiência

- **UX-148**: Cada opção da escolha da autoridade MUST dizer cargo, nome quando houver e ato de
  nomeação quando houver — o bastante para distinguir duas autoridades do mesmo cargo.
- **UX-149**: A lista de Autoridades da Unidade MUST separar as vigentes das encerradas e das de
  vigência futura, e cada uma MUST dizer o período.
- **UX-150**: O documento, a tela e a recusa MUST chamar a Unidade pelo nome registrado, nunca pelo
  código.

### Key Entities

- **Unidade**: a unidade institucional do Ifes que pratica atos — Reitoria, campus, Cefor. Tem código
  (o escopo institucional), sigla, nome, linhas de cabeçalho, local e situação. Não tem hierarquia
  nem relação com outra Unidade.
- **Autoridade habilitada**: quem pode responder pelos atos de uma Unidade num período. Tem cargo,
  nome, ato de nomeação e vigência. **Não** é pessoa, cargo nem mandato — é a resposta à única
  pergunta que esta feature faz: *quem pode ser escolhido para os atos desta unidade nesta data?*
- **Publicação** (Edital, Retificação) e **Publicação de Resultado**: já existem e já congelam a
  autoridade. Passam a congelar também a Unidade, e a de Resultado, o ato de nomeação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-429**: Num documento publicado de um Edital de unidade diferente do Cefor, **zero**
  ocorrências do nome, da sigla ou do local do Cefor — nos quatro tipos de documento.
- **SC-430**: Para o Cefor, os documentos produzidos depois desta feature são **idênticos** aos de
  antes, para o mesmo conteúdo, data e autoridade.
- **SC-431**: **100%** das tentativas de publicar com autoridade de outra unidade, fora de vigência
  ou inexistente são recusadas, nos três fluxos, sem Publicação gravada.
- **SC-432**: Trocar a autoridade de uma unidade não exige mudança no sistema: quem tem a permissão
  encerra uma e cadastra outra em **menos de três minutos**, e a publicação seguinte já a oferece.
- **SC-433**: Depois de encerrar uma autoridade e renomear a unidade, **todas** as Publicações
  anteriores — documento, consulta pública e registro — continuam idênticas ao que eram.
- **SC-434**: Nenhuma Unidade e nenhuma Autoridade pode ser excluída por nenhum caminho do sistema.

## Decisões

### D-001 — A Unidade materializa o escopo; não o substitui

O escopo institucional já faz três trabalhos — isola, autoriza e numera —, e os faz bem. A Unidade
usa o mesmo valor como código e acrescenta o que faltava: o que o documento diz. Trocar o texto do
escopo por uma referência à Unidade mexeria em cada uma dessas regras para não ganhar nada que o
código não dê.

### D-002 — Unidades são registradas na implantação, e não por tela

São cerca de 26, e mudam raramente — um campus novo em anos, um nome em décadas. As linhas do
cabeçalho são decisão editorial de documento oficial, e se revisam melhor em diff do que num
formulário. O registro de Unidades é mantido pela equipe que implanta o sistema, versionado, e cada
mudança fica registrada (FR-1108). O argumento contra o catálogo de autoridades em código — mudança
frequente — não vale aqui. *Alternativa descartada*: tela de administração de Unidades, que pediria
papel central, inexistente num modelo em que cada operador tem uma unidade só.

### D-003 — Autoridade é habilitação na unidade, não lotação

A pergunta é *quem pode responder pelos atos desta unidade*, e não *onde esta pessoa trabalha*.
Habilitar o Reitor no Campus Serra é um registro a mais; modelar a hierarquia para inferir que o
Reitor responde por todos os campi seria organograma, delegação e competência — tudo fora de escopo.
O custo é aceito: uma pessoa habilitada em várias unidades aparece em vários registros.

### D-004 — Corrigir só antes do primeiro uso

Depois que uma Publicação congela a autoridade, o identificador dela liga o ato ao registro. Mudar o
nome do registro faria o identificador apontar para outra pessoa, e a auditoria responderia errado a
*quem assinou*. Antes do primeiro uso não há ligação a proteger, e corrigir um erro de digitação não
precisa de dois registros.

### D-005 — O Gestor mantém as autoridades da própria unidade

Decisão do usuário em 06/10/2026. Manter autoridades é configuração administrativa da unidade, e o
Gestor é quem já conduz os Processos do escopo. A permissão é **própria**, e não efeito de outra —
o mesmo cuidado que a `040` teve com o panorama —, para que destacá-la para outro papel custe uma
linha no mapa de papéis e nenhuma mudança no modelo. *Alternativas descartadas*: papel novo de
administração da unidade, que acrescentaria um papel a uma equipe de duas ou três pessoas; e impedir
quem cadastrou uma autoridade de publicar com ela, regra de segregação que a operação pequena
travaria e que o Ifes não pediu.

## Fora de escopo

- **Assinatura eletrônica**, e qualquer simulação dela.
- **Qual artefato é o documento oficial** e onde ele é formalizado — pergunta ao Cefor.
- **Integração** com protocolo, SIPAC, SUAP ou diretório institucional.
- **Delegação, substituição, afastamento, organograma e cadeia hierárquica** como modelo; a
  delegação aparece apenas como texto no ato de nomeação.
- **Operador com mais de uma unidade**, e papel de visão institucional entre unidades.
- **Mudança nas regras atuais** de autorização, isolamento e numeração.
- **A marca do sistema**: *"Cefor/Ifes"* no título das páginas, no topo das telas, nos e-mails e nas
  mensagens que mandam pedir acesso *"a quem administra o sistema no Cefor"*; e a vitrine do portal,
  que não diz a unidade de cada seleção. Ficam registradas como pendência — mudam o que o produto diz
  de si, e não o que o documento oficial diz.

## Assumptions

- **Não há dado em produção.** Nenhuma conversão de Publicação existente é construída; no banco de
  demonstração, o acervo é re-semeado.
- **Cada operador tem um escopo só**, como hoje. Quem mantém autoridades o faz na própria unidade.
- **As linhas institucionais comuns** — *Ministério da Educação* e *Instituto Federal do Espírito
  Santo* — e o brasão são os mesmos para todas as unidades.
- **A data do ato** é a da Publicação, no fuso institucional, como na `054`.
- **LGPD.** Nome, cargo e ato de nomeação de quem responde por um ato administrativo são dados
  pessoais de agente público no exercício da função, e **continuam sujeitos à LGPD**: a publicidade
  do ato não dispensa finalidade, necessidade e base legal (art. 6º), e o tratamento de dado de
  acesso público considera a finalidade, a boa-fé e o interesse público que justificaram a
  disponibilização (art. 7º, § 3º). A base legal **indicada** é o cumprimento de obrigação legal
  (art. 7º, II) — o ato administrativo identifica a autoridade responsável (Lei nº 9.784/1999,
  art. 22, § 1º) e se publica (Constituição Federal, art. 37) — no tratamento pelo poder público
  para finalidade pública (art. 23). **A confirmação é do encarregado de dados do Ifes**, e fica como
  pendência de implantação. A necessidade está em FR-1116: o registro guarda só esses três, sem
  CPF, matrícula, contato ou foto. Esta feature não toca dado de candidato.
- **O seed de demonstração** registra o Cefor e as autoridades que usa; os testes registram as
  suas, e os que publicam em mais de uma unidade registram a segunda. Nenhum dos dois reproduz as
  três do catálogo, que entram na implantação (FR-1124).
