# Feature Specification: A verificação da autodeclaração por vídeo, só em desenvolvimento

**Feature Branch**: `claude/166-verificacao-por-video`, sobre a `claude/165-regras-de-deliberacao-9f8a47`
em `09443456`, que tem a `165` implementada sobre a `164` e a `163`

**Created**: 2026-11-14

**Status**: Draft — fluxo completo do Spec Kit pedido na mesma sessão (specify, clarify, plan, tasks,
analyze e implementação). Nada aqui ativa o vídeo fora do desenvolvimento.

**Input**: as entregas 5 a 8 do plano do estudo da verificação da autodeclaração
(`doc/estudo-verificacao-da-autodeclaracao-2026-11-13/`, PR #541): o lado do candidato, o lado da
comissão, a retenção do arquivo e a porta do piloto. É a **camada B** do estudo — o vídeo gravado pelo
candidato, **opcional, que só confirma** —, atrás da chave `VERIFICACAO_POR_VIDEO`, recusada em
produção.

> **Faixa de identificadores.** Esta spec abre em **FR-7100**, **SC-2370** e **UX-770**. Os tetos
> medidos em 14/11/2026, na branch de que ela parte, eram o requisito sete mil e oitenta e três, o
> critério dois mil trezentos e cinquenta e seis e o requisito de experiência setecentos e cinquenta e
> quatro, todos da `165`. A faixa até o requisito sete mil cento e noventa e nove fica reservada. As
> decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-015 da `013`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> **A `163`, a `164` e a `165` são citadas só pelo assunto**, porque não estão na `main`. As regras do
> estudo (`R-1` a `R-24`) e as pendências (`P-0` a `P-12`) são locais ao estudo, e se citam por extenso.

---

## Por que esta feature existe

A heteroidentificação de pretos e pardos entrou no GPS pela **camada A** do estudo: a Etapa alcança
só quem declarou a Modalidade (`163`), o desfecho desfavorável tem efeito por lista (`164`) e a
comissão delibera pela regra que o Edital escolheu, com pareceres às cegas (`165`). O meio continua o
de hoje: a entrevista ao vivo, presencial ou por videoconferência, cujo desfecho a comissão registra
na Mesa.

A **camada B** é um meio a mais de a comissão ver o candidato: um vídeo curto, gravado por ele na
página do GPS, que a comissão assiste quando puder. Ela reduz o esforço das entrevistas — quem o vídeo
confirma não precisa de horário marcado — sem tirar nada de ninguém, porque **o vídeo só confirma**:
quem ele não confirma vai à entrevista ao vivo, como teria ido sem ele (regra R-11 do estudo, no
modelo da UFC).

**Nenhuma norma do Ifes autoriza hoje o vídeo assíncrono.** A Res. CS 61/2019 prevê entrevista
presencial; o Ofício MEC 3/2025 pede, fora do presencial, entrevista síncrona. Por isso esta spec
entrega a camada B **inteira e desligada**: ela roda em desenvolvimento, atrás de uma chave que a
produção recusa, e a porta do piloto é descrita, e não aberta.

### O que esta spec cobre, e o que fica fora

**Cobre:**

- como o Edital admite o vídeo numa Etapa colegiada da `165`, e por que só com a chave ligada;
- o lado do candidato: escolher, gravar com roteiro, revisar, regravar, enviar em partes retomáveis,
  receber o comprovante com resumo criptográfico, assistir ao próprio vídeo e trocá-lo antes que a
  comissão o abra;
- o lado da comissão: abrir o vídeo na Mesa como ato registrado, assistir com saltos por passo, dar o
  parecer "Confirmo" ou "Não dá para confirmar pelo vídeo";
- a deliberação do vídeo: ou confirma, ou encaminha à entrevista ao vivo — **nunca** "não
  confirmada";
- a retenção do arquivo de vídeo, com o prazo como parâmetro sem valor;
- a porta do piloto, descrita e fechada.

**Fica fora**, como registro e não como escopo:

- a **orientação** da entrega 4 do estudo: o degrau "falta um passo seu" no acompanhamento, a natureza
  "verificação da autodeclaração" no Centro e em Minhas atividades, e o aviso por e-mail. Esta spec
  oferece ao candidato **só o acesso** à página, no detalhe da inscrição; o degrau, quando vier,
  o substitui (ver *Dependências*);
- a **agenda individual** da entrevista ao vivo. A comissão marca fora e registra o desfecho, como na
  camada A;
- o **relato de falha técnica** como registro: quem não consegue gravar simplesmente fica no ao vivo,
  que é o padrão, e não há leitor do relato sem a natureza do Centro (entrega 4);
- o **roteiro por unidade**, editável: o roteiro desta entrega é um só, versionado (P-8);
- o **comprovante em PDF**: o comprovante é uma página, que o navegador imprime;
- transcodificação, miniatura, marca-d'água, player próprio e qualquer análise automática do vídeo;
- a **ativação** do vídeo: o ato do Conselho Superior, o protocolo da CPVA e o Edital que o cite
  (P-0).

---

## Clarifications

### Session 2026-11-13 (decisões do usuário, no estudo)

- **P-1, P-2 e P-3** são a `163`, a `164` e a `165`, das quais esta parte.
- **P-0** (o ato que autoriza o vídeo), **P-7** (o menor de idade), **P-8** (o roteiro) e **P-10**
  (a guarda do vídeo) continuam **abertas**. Esta spec não as decide: adota, onde precisa de um
  comportamento, a recomendação do estudo como padrão provisório e reversível, e o diz.

### Session 2026-11-14 (restrições do pedido)

- Nada de ativação oficial: a chave não se libera em produção, a recusa não sai, e a P-0 não se marca
  resolvida.
- Nenhum vídeo real: a suíte e a verificação usam fonte sintética ou arquivos gerados pela suíte.
- Proibida a inferência racial por IA, em qualquer forma.
- Sem estrutura paralela: o parecer é a Avaliação da `012`, a deliberação é a da `165`, o encaminhamento
  usa a reabertura da `012`.

### Session 2026-11-14 (/speckit-clarify)

Esta sessão foi aberta por outra, e não pelo usuário. Cada resposta abaixo é a **recomendação** do
`/speckit-clarify`, adotada para o fluxo seguir, e fica **aberta à revisão do usuário**. A pergunta da
P-10 não tem resposta: ela é da instituição, e a spec a deixa como parâmetro sem valor.

- Q: Como o GPS sabe que o candidato é menor de idade, se a inscrição não guarda a data de nascimento?
  → A: **Pela declaração do próprio candidato, antes da câmera**: "Tenho 18 anos ou mais" ou "Tenho menos
  de 18 anos". O GPS não passa a pedir a data de nascimento: seria dado pessoal novo, coletado só para
  isto (LGPD, art. 6º, III). Quem declara ter menos de 18 não vê o vídeo e fica no ao vivo, e a declaração
  falsa aparece na própria verificação, porque a comissão vê a pessoa. A resposta é guardada com o vídeo,
  e não à parte. Alternativas descartadas: pedir a data de nascimento (coleta nova); ler um fato
  declarado do Edital (acopla a camada B a um campo que poucos Editais declaram); não perguntar
  (contraria a R-22). É o padrão provisório da P-7, que continua aberta (FR-7109, D-003).
- Q: Qual é o prazo de retenção do arquivo de vídeo, e contado de quando? → A: **Sem resposta: é a
  P-10.** O prazo é parâmetro do ambiente sem valor padrão, e sem ele o comando de eliminação recusa. O
  marco da contagem é o encerramento do Edital, por ser o único fim de certame que o sistema registra;
  se a P-10 escolher outro marco, ele entra como parâmetro (FR-7146, FR-7147, D-008).
- Q: Quem encaminha à entrevista ao vivo, e o que a tela mostra ao fazê-lo? → A: **A presidência, em
  ato explícito, na conferência da consolidação, sem a contagem dos sentidos.** A tela mostra só a lista
  das inscrições que o vídeo não confirmou, e o alcance antes da confirmação. A contagem diria aos
  membros, depois, como os colegas votaram, e a entrevista ao vivo seria dada sem a independência que a
  `165` protege; e o encaminhamento automático tiraria a autoria de um ato que muda o caminho do
  candidato (FR-7138, FR-7140, D-005).
- Q: O titular que assiste ao próprio vídeo deixa registro na trilha? → A: **Sim, um evento por
  abertura, pela mesma mecânica da comissão**, e essa abertura **não** conta como "primeira abertura"
  para a troca: só a de um membro conta. Leitura de dado sensível é registrada em todo o sistema, e o
  titular não pode perder a troca por ter conferido o que enviou (FR-7124, FR-7127, FR-7151).
- Q: O titular pode desistir do vídeo já enviado e voltar ao ao vivo sem gravar outro? → A: **Não nesta
  entrega.** Antes da abertura, ele troca o vídeo; depois, a análise já começou, e o caminho para o ao
  vivo é o encaminhamento da comissão. A desistência pediria um registro e um leitor que só a entrega 4
  traz (a natureza no Centro), e sem eles seria um pedido que ninguém lê (Edge Cases).

---

## User Scenarios & Testing *(mandatory)*

Os cenários usam o **Edital 90/2026**, de desenvolvimento, com o Perfil "Técnico em Informática" e
três Modalidades: ampla concorrência, `L2` (pretos e pardos de escola pública) e `L6` (pessoa com
deficiência). A Etapa **"Verificação da autodeclaração"** é decisória, alcança só `L2` (`163`), tem
efeito *retirada da reserva* (`164`), três avaliações por inscrição e a regra **confirma só por
unanimidade** (`165`). O período dela é o Evento "Verificação da autodeclaração", de 01/12 a 05/12. Ana,
Bruno e Carla são os membros alocados. Maria e João se inscreveram em `L2`.

### User Story 1 — Quem elabora admite o vídeo, e só onde ele pode existir (Priority: P1)

Quem compõe a Etapa marca "Admite vídeo gravado pelo candidato". A marcação só existe numa Etapa
decisória e colegiada, com alcance declarado e período, e só quando a chave está ligada. Com a chave
desligada, o campo aparece desabilitado, com a razão: falta o protocolo institucional.

**Why this priority**: sem a declaração no Edital, o vídeo seria um direito que nenhuma norma publicada
concede. A Constituição exige uma fonte só para regra de avaliação.

**Independent Test**: compor a Etapa com e sem a chave; publicar; ler o campo no conteúdo publicado e
no documento.

**Acceptance Scenarios**:

1. **Given** a chave ligada e a Etapa colegiada do Edital 90, **When** quem elabora marca "Admite vídeo"
   e publica, **Then** o conteúdo publicado diz que a Etapa admite o vídeo, e o documento o anuncia na
   descrição da Etapa.
2. **Given** a chave desligada, **When** quem elabora abre a Etapa, **Then** o campo aparece
   desabilitado, com a frase "O vídeo depende de protocolo institucional que ainda não existe", e a
   publicação de um rascunho que o marcou é recusada pelo mesmo motivo.
3. **Given** uma Etapa pontuada, ou decisória com uma avaliação só, ou sem alcance, ou sem período,
   **When** quem elabora marca o vídeo, **Then** a publicação o recusa, nomeando o que falta.

---

### User Story 2 — O candidato grava, revisa e envia (Priority: P1)

Maria abre a inscrição no portal e vê "Verificação da autodeclaração: você pode gravar um vídeo curto
ou fazer a entrevista ao vivo. As duas formas valem igual." Escolhe gravar. Lê o acolhimento — o que a
comissão olha, quem vê o vídeo —, confirma ter 18 anos ou mais, testa a câmera com o oval de
enquadramento, grava seguindo os quatro passos do roteiro, avança pelo toque, assiste, regrava uma vez
e envia. A rede cai no meio do envio; a página retoma de onde parou. O comprovante mostra número, data,
duração e o resumo do arquivo.

**Why this priority**: é a jornada que a camada B existe para oferecer.

**Independent Test**: no navegador, com fonte sintética de imagem e som, percorrer da escolha ao
comprovante, com uma queda simulada no envio.

**Acceptance Scenarios**:

1. **Given** Maria alcançada, dentro do período e sem parecer concluído, **When** ela abre a inscrição,
   **Then** vê as duas opções com o mesmo peso e a frase "as duas formas valem igual".
2. **Given** Maria na gravação, **When** ela toca "Parar e recomeçar", **Then** a tomada inteira é
   descartada e nada sai do aparelho.
3. **Given** Maria na revisão, **When** ela grava de novo, **Then** a tomada anterior é descartada no
   aparelho e o servidor nunca a recebe.
4. **Given** o envio interrompido na terceira parte, **When** a conexão volta, **Then** o envio
   continua da terceira parte, e não do começo.
5. **Given** o envio completo, **When** o servidor confere o arquivo, **Then** ele reconhece o
   contêiner, confere o tamanho e a duração, calcula o resumo e emite o comprovante; o resumo do
   comprovante é o mesmo que o aparelho calculou.
6. **Given** João, que declarou ter menos de 18 anos, **When** ele abre a verificação, **Then** a opção
   do vídeo não aparece, e a página diz que a entrevista ao vivo é o caminho dele e por quê.
7. **Given** Pedro, inscrito só na ampla concorrência, **When** ele abre a inscrição, **Then** nada
   sobre a verificação aparece.

---

### User Story 3 — A comissão abre o vídeo e dá o parecer (Priority: P1)

Ana abre a Mesa da Etapa. A inscrição de Maria tem vídeo. O painel do documento mostra "Abrir o vídeo".
Abrir é ato: a trilha registra **uma** abertura, por mais que o vídeo avance e volte. Ana usa os saltos
por passo do roteiro, recua 10 segundos, assiste em 0,5×, e registra "Confirmo". Bruno abre e registra
"Não dá para confirmar pelo vídeo", com o motivo "a iluminação não deixa ver".

**Why this priority**: sem a Mesa, o vídeo seria guardado sem leitor.

**Independent Test**: com o vídeo sintético de Maria, Ana abre, assiste e conclui; a trilha tem um
evento de abertura; Bruno tenta concluir sem abrir e é recusado.

**Acceptance Scenarios**:

1. **Given** Ana alocada com a Atribuição de Maria, **When** ela abre o vídeo e o assiste avançando e
   voltando, **Then** a trilha tem **um** evento de abertura, com o resumo reconferido.
2. **Given** Bruno, que ainda não abriu o vídeo, **When** ele tenta concluir o parecer, **Then** a
   conclusão é recusada: "Abra o vídeo antes de dar o parecer."
3. **Given** Davi, membro da comissão sem a Atribuição de Maria, ou a presidência sem Atribuição,
   **When** pede o vídeo por endereço direto, **Then** a resposta é a de recurso inexistente, e nada se
   entrega.
4. **Given** Bruno marcando "Não dá para confirmar pelo vídeo", **When** ele não escreve o motivo,
   **Then** a conclusão é recusada.
5. **Given** a Mesa, **When** Ana registra o parecer, **Then** ela não vê o de Bruno nem o de Carla
   (`165`), e a tela não oferece baixar o vídeo.

---

### User Story 4 — O vídeo só confirma: ou confirma, ou encaminha ao vivo (Priority: P1)

Com os três pareceres de Maria — dois "Confirmo" e um "Não dá para confirmar" — a regra da
unanimidade não confirma. A conferência da consolidação **não** oferece "não confirmada": mostra Maria
em "Encaminhar à entrevista ao vivo". A presidência encaminha. Os três pareceres pelo vídeo ficam
preservados, e as Avaliações voltam à Mesa para o parecer da entrevista ao vivo, que a comissão marca
fora e registra como na camada A. Só esse parecer pode produzir "não confirmada".

**Why this priority**: é a regra que dá segurança jurídica ao experimento — ninguém perde a reserva
sem ter sido visto ao vivo.

**Independent Test**: as três regras × as combinações de três pareceres pelo vídeo; nenhuma produz
Resultado desfavorável; o encaminhamento reabre as Avaliações e a deliberação seguinte, ao vivo, pode
produzi-lo.

**Acceptance Scenarios**:

1. **Given** três "Confirmo" sobre o vídeo de Maria, **When** a presidência consolida, **Then** o
   Resultado é o favorável da `165`, citando os três pareceres.
2. **Given** dois "Confirmo" e um "Não dá para confirmar", sob unanimidade, **When** a presidência
   consolida, **Then** Maria não é consolidada; ela aparece em "Encaminhar à entrevista ao vivo", sem a
   contagem dos sentidos.
3. **Given** Maria encaminhada, **When** a comissão registra os três pareceres da entrevista ao vivo,
   **Then** a deliberação segue a regra publicada, e o desfavorável, se houver, tem o efeito da `164`.
4. **Given** qualquer caminho — consolidação, recurso, chamada direta ao serviço —, **When** se tenta
   gravar um Resultado desfavorável sobre pareceres pelo vídeo, **Then** a gravação é recusada.
5. **Given** Maria encaminhada, **When** ela abre a inscrição, **Then** lê "A comissão quer conversar
   com você ao vivo. Isso não é reprovação." e não pode mais enviar vídeo.

---

### User Story 5 — O titular vê o próprio vídeo, e troca antes da abertura (Priority: P2)

Maria abre o comprovante, assiste ao vídeo que enviou e percebe que cortou a fala. Como nenhum membro
abriu o vídeo ainda, ela grava outro. O novo substitui o anterior; os dois ficam registrados. Depois da
primeira abertura pela comissão, a troca não existe mais.

**Why this priority**: o titular vê a própria gravação (IN 261, art. 25, por analogia; R-24), e a troca
desfaz o medo de errar. Não é o caminho principal.

**Independent Test**: enviar, assistir, trocar; abrir pela comissão; tentar trocar de novo.

**Acceptance Scenarios**:

1. **Given** o vídeo de Maria recebido, **When** ela abre o comprovante, **Then** assiste ao vídeo pela
   entrega mediada, e a página não oferece baixar.
2. **Given** nenhum membro abriu o vídeo, **When** Maria envia outro, **Then** o novo é o vigente, o
   anterior continua registrado, e a comissão só vê o novo.
3. **Given** Ana já abriu o vídeo, **When** Maria tenta trocá-lo, **Then** a troca é recusada, e a
   página diz que a comissão já começou a análise.

---

### User Story 6 — O arquivo de vídeo tem retenção, e o prazo não é inventado (Priority: P3)

Quem opera o sistema roda o comando de eliminação dos vídeos de um Edital. Sem o prazo definido pela
instituição, o comando recusa, dizendo que o prazo é decisão pendente. Com o prazo definido no
ambiente, o comando confere que ele passou desde o encerramento do Edital, elimina o arquivo e guarda
o resumo, a duração e a trilha.

**Why this priority**: o prazo depende da P-10, que não está decidida. A entrega existe para que,
decidida, a retenção seja um parâmetro, e não um projeto.

**Independent Test**: o comando sem prazo recusa; com prazo e Edital encerrado há mais tempo, elimina e
registra; o resumo sobrevive.

**Acceptance Scenarios**:

1. **Given** o prazo não definido, **When** o comando roda, **Then** recusa, sem eliminar nada.
2. **Given** o prazo definido e o Edital encerrado há menos tempo, **When** o comando roda, **Then**
   recusa, dizendo a data a partir da qual a eliminação cabe.
3. **Given** o prazo vencido, **When** o comando roda com a confirmação explícita, **Then** cada arquivo
   é eliminado, cada eliminação é registrada, e o comprovante, a Mesa e a trilha passam a dizer
   "arquivo eliminado em …, conforme o prazo de retenção", preservando o resumo e a duração.

---

### User Story 7 — A porta do piloto existe, e está fechada (Priority: P3)

A produção recusa subir com a chave ligada. O caminho para um piloto é escrito: ato do Conselho
Superior, protocolo da CPVA e Edital que o cite; depois, um PR revisado que libere a chave para aquele
Edital. Nada disso acontece aqui.

**Why this priority**: é a entrega 8 do estudo, que só pode ser descrita.

**Independent Test**: subir as settings de produção com a chave ligada falha; a documentação da porta
existe.

**Acceptance Scenarios**:

1. **Given** as settings de produção, **When** a chave está ligada, **Then** a aplicação recusa subir,
   como recusa as outras chaves de desenvolvimento.

---

### Edge Cases

- **A chave desligada depois de publicado um Edital que admite o vídeo** (só em desenvolvimento): a
  página de gravação e as rotas de envio respondem como inexistentes; os vídeos já recebidos continuam
  na Mesa, porque o parecer sobre eles é ato do certame; a deliberação continua aplicando a R-11.
- **O período termina no meio de um envio**: o envio iniciado dentro do período pode ser concluído até
  uma hora depois do fim; depois disso, o envio incompleto é descartado e o candidato fica no ao vivo
  (R-12: não enviar não é ausência).
- **O candidato que não enviou nada**: fica no ao vivo, sem registro novo. A Mesa mostra a inscrição sem
  vídeo, e a comissão registra o parecer da entrevista ao vivo, como na camada A.
- **Um parecer ao vivo concluído antes de qualquer vídeo**: o vídeo deixa de ser aceito para aquela
  inscrição — a comissão já a está vendo ao vivo.
- **O vídeo chega depois de um rascunho de parecer**: o rascunho continua; a conclusão passa a exigir a
  abertura do vídeo.
- **Autor exposto aos pareceres alheios** (`165`): o encaminhamento reabre a Avaliação, e a `165` recusa
  reabrir a de quem foi exposto. O encaminhamento é então recusado por inteiro para aquela inscrição,
  com a mesma explicação da `165`, e a presidência redistribui antes de encaminhar.
- **Recurso contra o Resultado favorável pelo vídeo**: não há interesse do titular; um terceiro não
  recorre de Resultado alheio. Nada muda.
- **Recurso contra o Resultado desfavorável da entrevista ao vivo**: segue a `165`; a autoridade
  recursal vê os pareceres pelo vídeo preservados, e o vídeo, pela instrução da `018`, se a instrução
  o pedir — o vídeo não entra automaticamente.
- **Formato**: o aparelho grava MP4 quando pode, e WebM quando não. O servidor aceita os dois pela
  assinatura do contêiner, e recusa o resto, inclusive um MP4 que só tenha a extensão.
- **Duração**: o teto técnico é de três minutos, declarado antes de começar. Não há mínimo nem
  cronômetro por passo. Um arquivo cuja duração no contêiner passe do teto é recusado.
- **Tamanho**: cada parte tem no máximo 8 MiB; o vídeo inteiro tem um teto próprio, que é parâmetro
  e não muda os limites dos outros envios do sistema.
- **Parte repetida ou fora de ordem**: a parte cujo deslocamento não é o recebido até ali é recusada,
  com o deslocamento certo na resposta, para o aparelho retomar.
- **Resumo divergente**: o resumo que o aparelho calculou e o que o servidor calculou diferem; o envio
  é recusado, e o candidato envia de novo.
- **Arquivo alterado no disco depois de recebido**: a abertura confere o resumo; divergindo, a entrega
  é recusada e o fato vai à trilha, como na entrega mediada de hoje.
- **Tela oculta no meio da gravação**: a tomada é descartada, com a frase "A gravação parou porque a
  tela saiu do navegador". A frequência disso em celulares é medida da matriz do estudo (A-3), e não
  desta spec.
- **Câmera ou permissão negada**: a página explica como reconceder, por sistema, e lembra que a
  entrevista ao vivo continua disponível. Nunca vira ausência.
- **Menor de idade**: quem declara ter menos de 18 anos não vê a opção do vídeo. A declaração falsa
  aparece na própria verificação: a comissão vê a pessoa.
- **Desistir do vídeo enviado**: não existe nesta entrega. Antes da primeira abertura, o titular troca
  o vídeo; depois, o caminho para o ao vivo é o encaminhamento da comissão.
- **O titular assiste ao próprio vídeo antes da comissão**: a abertura dele é registrada, e a troca
  continua possível, porque só a abertura de um membro encerra a troca.
- **A Etapa retificada para não admitir mais o vídeo depois de um vídeo recebido**: a Retificação é
  recusada; antes do primeiro vídeo, ela cabe.
- **Duas abas enviando ao mesmo tempo**: o segundo envio iniciado descarta o primeiro incompleto; dois
  envios concluídos ao mesmo tempo não produzem dois vídeos vigentes.

## Requirements *(mandatory)*

### Functional Requirements

#### A chave e a declaração no Edital

- **FR-7100**: A camada B DEVE ficar atrás da chave `VERIFICACAO_POR_VIDEO`, desligada por padrão. Com
  ela desligada, a página de gravação, as rotas de envio e a opção na composição DEVEM se comportar
  como inexistentes ou desabilitadas, conforme o canal.
- **FR-7101**: As settings de produção DEVEM recusar subir com a chave ligada, pelo mesmo mecanismo das
  outras chaves de desenvolvimento. Esta spec NÃO DEVE remover nem abrandar a recusa.
- **FR-7102**: A Etapa DEVE poder declarar que **admite o vídeo gravado pelo candidato**. A declaração
  é conteúdo normativo publicado, com classificação de mutabilidade, e um Edital publicado antes desta
  spec é lido como "não admite".
- **FR-7103**: A publicação e a Retificação DEVEM recusar a admissão do vídeo numa Etapa que não seja
  decisória e colegiada (`165`), que não declare alcance (`163`) ou que não tenha período (Evento do
  cronograma com início e fim). A recusa DEVE nomear o que falta.
- **FR-7104**: A publicação e a Retificação DEVEM recusar a admissão do vídeo com a chave desligada.
- **FR-7105**: A Retificação que retira a admissão do vídeo DEVE ser recusada depois do primeiro vídeo
  recebido naquela Etapa.
- **FR-7106**: O documento do Edital DEVE anunciar, na descrição da Etapa que admite o vídeo, que o
  candidato alcançado pode escolher entre o vídeo e a entrevista ao vivo, que as duas valem igual e
  que o vídeo só confirma.

#### Quem pode gravar, e quando

- **FR-7107**: O vídeo DEVE estar disponível só ao titular de uma inscrição enviada, alcançada pela
  Etapa que admite o vídeo, dentro do período da Etapa, com a chave ligada, enquanto não houver
  parecer concluído, Resultado nem encaminhamento ao vivo para aquela inscrição naquela Etapa.
- **FR-7108**: O vídeo NUNCA DEVE ser o único caminho. A página DEVE oferecer o vídeo e a entrevista ao
  vivo com o mesmo peso, e não escolher DEVE equivaler a ficar na entrevista ao vivo, sem registro
  novo (R-10, R-12).
- **FR-7109**: Antes da câmera, o candidato DEVE declarar se tem 18 anos ou mais. Quem declara ter
  menos NÃO DEVE ver a opção do vídeo, e a página DEVE dizer que o caminho dele é a entrevista ao vivo
  e por quê (R-22; padrão provisório da P-7). O sistema NÃO DEVE pedir a data de nascimento para
  isso, e a declaração DEVE ser guardada com o vídeo enviado.
- **FR-7110**: Quem não é titular da inscrição DEVE receber a resposta de recurso inexistente em toda
  rota da verificação por vídeo, sem distinguir "não existe" de "não é seu".

#### A gravação

- **FR-7111**: O vídeo DEVE nascer na página, pela câmera e pelo microfone, numa tomada contínua. A
  página NÃO DEVE oferecer envio de arquivo da galeria, corte, pausa nem edição, e "parar e
  recomeçar" DEVE descartar a tomada inteira (R-13).
- **FR-7112**: A página DEVE conduzir a gravação por um roteiro versionado de passos, avançados pelo
  toque ou pelo teclado, sem tempo mínimo e sem cronômetro por passo, e com um teto técnico de duração
  declarado antes de começar (R-14). O roteiro desta entrega é o de referência do estudo: documento
  de identidade, perfil esquerdo, perfil direito e frente com a fala de uma frase sem o CPF (padrão
  provisório da P-8).
- **FR-7113**: O vídeo DEVE guardar a versão do roteiro exibida e os instantes em que o candidato passou
  de um passo a outro.
- **FR-7114**: O guia de enquadramento DEVE ser desenhado por cima da prévia e NÃO DEVE entrar na
  gravação.
- **FR-7115**: A tomada DEVE ser descartada quando a página deixa de estar visível durante a gravação,
  com a explicação ao candidato.
- **FR-7116**: Antes do envio, o candidato DEVE poder assistir à tomada e regravar sem limite. As tomadas
  não enviadas NÃO DEVEM sair do aparelho (R-15).
- **FR-7117**: A exceção de política de conteúdo que a revisão local exige (mídia de origem local do
  navegador) e a permissão de câmera e microfone DEVEM valer **só** na página de gravação.

#### O envio e o comprovante

- **FR-7118**: O envio DEVE ser autenticado pela sessão do portal e pela titularidade, e acontecer em
  partes de no máximo 8 MiB, cada uma aceita só no deslocamento que o servidor já recebeu.
- **FR-7119**: Um envio interrompido DEVE poder retomar do último deslocamento recebido, consultando o
  servidor, sem reenviar o que já chegou.
- **FR-7120**: Ao concluir o envio, o servidor DEVE conferir: o tamanho declarado; a assinatura do
  contêiner (MP4 ou WebM), recusando o resto; a duração, quando o contêiner a declara, contra o teto;
  e o resumo SHA-256, que DEVE ser igual ao que o aparelho calculou.
- **FR-7121**: O vídeo aceito DEVE ser guardado no armazenamento privado dos arquivos dos candidatos,
  sem endereço público, associado à inscrição e à Etapa, com o resumo, o tamanho, a duração, o
  formato, a versão do roteiro e as marcas dos passos. Nenhum serviço de terceiros DEVE recebê-lo.
- **FR-7122**: O teto do vídeo inteiro DEVE ser parâmetro próprio, e o envio do vídeo NÃO DEVE alterar
  os limites dos demais envios de arquivo do sistema.
- **FR-7123**: O comprovante DEVE mostrar o número do envio, a data e a hora, a duração, o formato e o
  resumo, e dizer o que acontece depois, incluindo que o encaminhamento à entrevista ao vivo não é
  reprovação.
- **FR-7124**: Enquanto nenhum membro da comissão tiver aberto o vídeo, o titular DEVE poder enviar
  outro, que passa a ser o vigente. O anterior DEVE continuar registrado. Depois da primeira abertura,
  a troca DEVE ser recusada (R-16).
- **FR-7125**: Um envio iniciado e não concluído NÃO DEVE produzir vídeo; o envio seguinte do mesmo
  titular para a mesma Etapa o descarta.
- **FR-7126**: O envio iniciado dentro do período DEVE poder ser concluído até uma hora depois do fim do
  período; nenhum envio novo DEVE começar fora do período.
- **FR-7127**: O titular DEVE poder assistir ao vídeo vigente que enviou, pela entrega mediada, sem
  opção de baixar oferecida pela tela, e sem ver os pareceres individuais (R-24). Cada abertura do
  titular DEVE gerar um evento na trilha, e NÃO DEVE contar como abertura da comissão.

#### A Mesa

- **FR-7128**: Na Mesa da Etapa que admite o vídeo, a inscrição com vídeo vigente DEVE mostrar, no
  painel do documento, a ação "Abrir o vídeo".
- **FR-7129**: Só DEVE abrir o vídeo quem está alocado à Etapa e tem a Atribuição ativa daquela
  inscrição. Qualquer outra pessoa, inclusive a presidência sem Atribuição, DEVE receber a resposta de
  recurso inexistente.
- **FR-7130**: Abrir o vídeo DEVE ser ato registrado: **um** evento de trilha por abertura, com o
  resumo reconferido, e não um por pedaço entregue. Os pedaços que o reprodutor pede dentro daquela
  abertura NÃO DEVEM gerar evento.
- **FR-7131**: A entrega DEVE atender pedidos de intervalo de bytes, para que o reprodutor avance e
  volte em qualquer navegador, e DEVE conferir o resumo do arquivo antes de entregar.
- **FR-7132**: A Mesa DEVE oferecer saltos para o instante de cada passo do roteiro, recuo e avanço de
  10 segundos e velocidade de 0,5×, e NÃO DEVE oferecer baixar o vídeo.
- **FR-7133**: Na inscrição com vídeo vigente e sem encaminhamento, os dois sentidos do parecer DEVEM se
  apresentar como **"Confirmo"** e **"Não dá para confirmar pelo vídeo"**, este com motivo obrigatório.
- **FR-7134**: A conclusão do parecer sobre uma inscrição com vídeo vigente e sem encaminhamento DEVE
  exigir que aquele membro tenha aberto aquele vídeo.
- **FR-7135**: O parecer às cegas da `165` DEVE valer sem mudança: o vídeo não altera o que cada membro
  vê dos pareceres alheios.

#### A deliberação do vídeo

- **FR-7136**: Os pareceres concluídos sobre uma inscrição com vídeo vigente e sem encaminhamento são
  **pareceres pelo vídeo**. A deliberação deles DEVE aplicar a regra publicada da Etapa, lendo
  "Não dá para confirmar pelo vídeo" no lugar do sentido desfavorável.
- **FR-7137**: Se a deliberação pelo vídeo for favorável, a consolidação DEVE produzir o Resultado
  deliberado da `165`, sem diferença.
- **FR-7138**: Se a deliberação pelo vídeo não for favorável, a inscrição NÃO DEVE ser consolidada: a
  conferência DEVE mostrá-la em "Encaminhar à entrevista ao vivo", sem a contagem dos sentidos (R-11).
- **FR-7139**: Nenhum caminho DEVE gravar Resultado desfavorável sobre pareceres pelo vídeo — nem a
  consolidação, nem o recurso, nem chamada direta ao serviço. A recusa DEVE estar no domínio.
- **FR-7140**: O encaminhamento à entrevista ao vivo DEVE ser ato explícito da presidência, com o
  alcance visível antes da confirmação, e registrado com autoria e instante.
- **FR-7141**: O encaminhamento DEVE reabrir as Avaliações da inscrição naquela Etapa pela reabertura da
  `012`, com o motivo "encaminhada à entrevista ao vivo", preservando as conclusões pelo vídeo. Se a
  `165` recusar alguma reabertura, o encaminhamento daquela inscrição DEVE ser recusado por inteiro.
- **FR-7142**: Depois do encaminhamento, os pareceres seguintes daquela inscrição são da entrevista ao
  vivo, com os rótulos publicados da Etapa, e a deliberação deles segue a `165` e a `164` sem a
  restrição da FR-7139.
- **FR-7143**: O encaminhamento DEVE ser único por inscrição e Etapa, e não se desfaz.
- **FR-7144**: Encaminhada, a inscrição NÃO DEVE mais aceitar vídeo, e o titular DEVE ler "A comissão
  quer conversar com você ao vivo. Isso não é reprovação."

#### O que o titular lê

- **FR-7145**: O detalhe da inscrição no portal DEVE mostrar a situação da verificação por vídeo da
  inscrição alcançada: pode gravar (com o fim do período), vídeo recebido (com o acesso ao
  comprovante), em análise (depois da primeira abertura), encaminhada ao vivo, ou entrevista ao vivo.
  É acesso, e não o degrau de orientação da entrega 4, que o substitui quando existir.

#### Retenção

- **FR-7146**: O prazo de retenção do arquivo de vídeo DEVE ser parâmetro do ambiente **sem valor
  padrão**. Sem ele, o comando de eliminação DEVE recusar, dizendo que o prazo é decisão pendente da
  instituição (P-10).
- **FR-7147**: O comando de eliminação DEVE exigir o Edital e a confirmação explícita, conferir que o
  prazo passou desde o encerramento do Edital, e recusar o Edital não encerrado ou dentro do prazo,
  dizendo a data a partir da qual a eliminação cabe.
- **FR-7148**: A eliminação DEVE remover só o arquivo, e preservar o resumo, o tamanho, a duração, as
  marcas, as aberturas e a trilha. Cada eliminação DEVE ser registrada, com autoria, instante e prazo
  aplicado.
- **FR-7149**: Eliminado o arquivo, a Mesa, o comprovante e a entrega DEVEM dizer "arquivo eliminado em
  …, conforme o prazo de retenção", sem erro.

#### Garantias

- **FR-7150**: O sistema NÃO DEVE analisar o vídeo de nenhuma forma: nada de detecção de rosto, de tom
  de pele ou de qualidade, de miniatura gerada ou de transcrição. A única verificação automática é
  técnica: contêiner, tamanho, duração e resumo (R-19). Um teste guardião DEVE recusar dependência de
  visão computacional ou de reconhecimento facial no projeto.
- **FR-7151**: A trilha DEVE registrar o recebimento, a troca, cada abertura, o encaminhamento e a
  eliminação, **nunca** o conteúdo do vídeo.
- **FR-7152**: Envio, abertura e encaminhamento concorrentes DEVEM produzir no máximo um vídeo vigente
  por inscrição e Etapa e no máximo um encaminhamento, e a troca concorrente com a primeira abertura
  DEVE ser serializada: ou a troca chega antes da abertura, ou é recusada.

#### A porta do piloto

- **FR-7153**: A documentação DEVE descrever a porta do piloto: o ato do Conselho Superior que altere a
  Res. CS 61/2019, o protocolo da CPVA, o Edital que o cite, e só então um PR revisado que libere a
  chave para aquele Edital. Esta spec NÃO DEVE executar nenhum desses passos nem marcar a P-0 como
  resolvida.

### Requisitos de experiência

- **UX-770**: A linguagem do candidato é a do estudo: "verificação da autodeclaração", "a comissão olha
  só a sua aparência", "não confirmada", "a comissão quer conversar com você", "enviar", "assistir". A
  palavra "heteroidentificação" fica nas telas da gestão.
- **UX-771**: No celular, coluna única, botões de largura cheia, câmera frontal em retrato, e os botões
  da gravação dentro da primeira tela, sem rolagem lateral a 375 px.
- **UX-772**: Toda instrução existe em texto e é anunciada ao leitor de tela; os passos avançam por
  toque ou teclado; o link "Não consigo usar a câmera" está em todas as telas da gravação e leva à
  explicação de que a entrevista ao vivo continua disponível.
- **UX-773**: A revisão diz "só o vídeo que você enviar chega à comissão", e o comprovante diz "Se ela
  precisar ver você ao vivo, isso não é reprovação."
- **UX-774**: Na Mesa, o vídeo fica no painel do documento, com os saltos por passo identificados pelo
  nome do passo; o parecer fica ao lado, com "Registrar e ir para a próxima".

### Key Entities

- **Admissão do vídeo na Etapa**: declaração normativa publicada da Etapa.
- **Envio do vídeo**: o envio em partes em andamento, de um titular para uma Etapa — deslocamento
  recebido, tamanho declarado, instante de início. Transitório: não é ato do certame.
- **Vídeo da verificação**: o arquivo recebido, imutável — inscrição, Edital, Etapa, resumo, tamanho,
  duração, formato, versão do roteiro, marcas dos passos, instante e o vídeo que ele substituiu.
- **Abertura do vídeo**: o fato de um membro ter aberto um vídeo, com o instante. Imutável.
- **Encaminhamento à entrevista ao vivo**: o ato da presidência sobre uma inscrição e uma Etapa, com o
  vídeo e os pareceres pelo vídeo que ele cita. Imutável.
- **Eliminação do vídeo**: o fato de o arquivo ter sido eliminado, com o prazo aplicado. Imutável.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2370**: Um candidato percorre da escolha ao comprovante, no celular, com fonte sintética, sem
  rolagem lateral e sem nenhuma violação de política de conteúdo no console.
- **SC-2371**: Um envio interrompido em qualquer parte retoma daquela parte, e o resumo final é igual ao
  do aparelho em 100% das execuções da suíte.
- **SC-2372**: Assistir a um vídeo inteiro, avançando e voltando, gera exatamente um evento de abertura.
- **SC-2373**: Nas três regras e em todas as combinações de três e de cinco pareceres pelo vídeo, o
  número de Resultados desfavoráveis produzidos é zero.
- **SC-2374**: Nenhuma pessoa sem a Atribuição alocada recebe um byte do vídeo, em todas as rotas
  testadas.
- **SC-2375**: Sem o prazo de retenção definido, o comando de eliminação elimina zero arquivos.
- **SC-2376**: Com a chave desligada, nenhuma rota da camada B responde com conteúdo, e a produção
  recusa subir com ela ligada.
- **SC-2377**: A matriz de navegadores do estudo, com câmera real em quatro navegadores, está preenchida
  antes de qualquer piloto. *(Humano; fora da suíte.)*

## Assumptions

- A `165` está implementada na branch de que esta parte, com a deliberação, a exposição ao parecer e a
  reabertura recusada de quem foi exposto. Se ela mudar antes do merge, esta spec acompanha.
- O período da Etapa é o do Evento do cronograma que a Etapa aponta, como para toda Etapa.
- O encerramento do Edital é o marco do início da contagem da retenção, por ser o fim do certame que o
  sistema já registra. Se a P-10 escolher outro marco, ele entra como parâmetro.
- A taxa de bits real e o tamanho por minuto saem da matriz com câmera real (A-5 do estudo). O teto do
  vídeo inteiro é parâmetro com folga para três minutos.
- Ninguém grava ninguém: a verificação no navegador usa a imagem sintética da prova de conceito.

## Out of Scope

- A orientação da entrega 4 (degrau, natureza no Centro e em Minhas atividades, aviso por e-mail).
- A agenda individual da entrevista ao vivo, o relato de falha técnica como registro, o roteiro por
  unidade e o comprovante em PDF.
- O recurso colegiado e a nova entrevista síncrona na instância recursal (P-5).
- Qualquer ativação, liberação da chave em produção ou Edital publicado com o vídeo fora do
  desenvolvimento.

## Dependências

- **`163`, `164` e `165`**, nos PRs #542, #543 e #545, empilhados e sem merge. Esta spec os pressupõe.
- **A entrega 4 do estudo (orientação)**, que não existe. Esta spec **não** a constrói: oferece só o
  acesso no detalhe da inscrição (FR-7145). O degrau, a natureza e o aviso são da spec da entrega 4.
- **P-0, P-7, P-8 e P-10**, abertas. A P-0 trava o piloto; a P-7 e a P-8 têm padrão provisório; a P-10
  deixa a retenção como parâmetro sem valor.
- **A matriz de navegadores com câmera real** (critério de saída da entrega 0), aberta (SC-2377).

## Achados (registro, e não escopo)

*(preenchidos ao longo do fluxo)*

## Decisões

O detalhe e as alternativas descartadas estão em [research.md](research.md).

### D-001 — A admissão do vídeo é declaração publicada da Etapa

Coluna de elaboração e campo do conteúdo publicado; o Edital anterior se lê "não admite"
(FR-7102).

### D-002 — Só na Etapa colegiada, com alcance e período, e com a chave

Sem colegiado não há regra a aplicar ao vídeo; sem alcance, a ampla gravaria; sem fim, a R-12 não
tem quando valer (FR-7103, FR-7104).

### D-003 — A maioridade é declarada pelo candidato

Sem data de nascimento nova; padrão provisório da P-7 (FR-7109).

### D-004 — O parecer pelo vídeo é a Avaliação da `012`, e o meio é derivado

Em modo vídeo = vídeo vigente e sem encaminhamento. Nenhuma coluna nova na Avaliação (FR-7136).

### D-005 — O encaminhamento é ato da presidência, sem contagem, pela reabertura da `012`

(FR-7138, FR-7140, FR-7141).

### D-006 — A R-11 mora no plano da consolidação e no ato que grava

(FR-7138, FR-7139).

### D-007 — Abrir é ato; a entrega em intervalos não registra

(FR-7130, FR-7131).

### D-008 — Retenção sem valor, contada do encerramento do Edital

(FR-7146, FR-7147).

### D-009 — A desistência do vídeo enviado não existe nesta entrega

(Edge Cases).
