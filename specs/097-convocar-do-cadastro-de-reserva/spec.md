# Feature Specification: Convocar do cadastro de reserva, na ordem publicada

**Feature Branch**: `claude/convocacao-cadastro-reserva-69e8a2`, sobre a `main` em `717fc057`

**Created**: 2026-10-21

**Status**: Draft

**Input**: pedido do usuário em 21/10/2026. É a volta da opção **A** da `DP-05`
([decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md), seção *DP-05*), que em 26/09
ficou em **B** para o piloto e mandou que esta spec nascesse *"quando houver um Edital de cadastro de
reserva escolhido para operação, e não antes"*. Agora há: o Edital de vagas remanescentes do Técnico
Subsequente em Multimeios Didáticos (TMD), o primeiro caso real do piloto, cujo modelo é o 69/2026.

> **Faixa de identificadores.** Abre em **FR-2450**, **SC-920** e **UX-220**. Na `main` (`717fc057`) o
> maior FR é o 2345, o maior SC o 878 e o maior UX o 216. A `096`, que corre em worktree irmã sem PR,
> usa de 2400 a 2417 para os requisitos funcionais e 900 para os critérios de sucesso; a folga entre
> as duas é deliberada. As decisões reiniciam em `D-001`.

---

## Por que esta feature existe

**O Edital de remanescentes do TMD publica sem quantidade, e a quantidade chega aos poucos.** O
69/2026 nasceu de *"vagas não preenchidas pelo Edital Multicampi Nº 20/2026"*; o seguinte é publicado
antes de se saber quantas sobrarão, porque as matrículas do Edital regular se efetivam, ou não, ao
longo de semanas. Cada matrícula que não se efetiva lá libera uma vaga aqui, e a equipe chama o
próximo da ordem do sorteio: *"em caso de vagas não ocupadas, os candidatos suplentes serão
convocados por meio de publicação no site do Cefor, respeitando o prazo máximo permitido no
calendário acadêmico do campus"* (7.2 do 69/2026).

**Hoje o sistema faz tudo isso menos a parte que importa.** A conferência de 26/09 mostrou que
configurar, publicar, sortear, classificar, apurar e divulgar já funcionam com 0 vagas imediatas e
cadastro de reserva. O que falha é a convocação: chamar exige vaga faltante apurada, e com zero vagas
publicadas a apuração nunca tem déficit — toda chamada é recusada com `sem_deficit`. A `FR-889` da
`050` fixou isso como regra, e a Revisão avisa desde então que a convocação dessa família é feita fora
do sistema.

**O contorno disponível é o errado.** Retificar as vagas imediatas a cada matrícula que não se
efetiva usaria um ato normativo público — com versão, PDF e aviso aos candidatos — para registrar um
fato operacional de outro Edital. A `DP-05` já o recusou, e esta spec não o reabre.

**O Edital regular não roda aqui.** O Multicampi é conduzido fora deste sistema, e cada Processo deste
é uma ilha (P-6 dos [achados de Editais externos](../../doc/achados-editais-externos.md)). Não há de
onde derivar quantas vagas sobraram: alguém competente constata o fato lá e o declara aqui, com autoria
— o mesmo desenho do atestado de fato externo da `019` (a decisão 004 daquela spec).

**O que já existe e não muda.** A ordem do sorteio, a apuração de ocupação e a convocação da `019` e
da `050` — titular, suplente, reclassificado no fim da fila (`FR-283`), comunicação por publicação com
o prazo correndo do registro de onde se publicou (`FR-876`), desfechos com efeito na ocupação. Esta
feature acrescenta **uma entrada de quantidade** à apuração, e o resto é o que o sistema já faz para
um Edital com vagas.

**O nome que a `DP-05` deu a esta spec terminava em "e dentro da validade", e o fim saiu.** O prazo
final das convocações fica com a equipe, e não com o sistema (`D-005`).

---

## Clarifications

### Session 2026-10-21

- Q: Como o Edital publica o limite das convocações do cadastro de reserva — Evento do Cronograma,
  campo do Perfil, data informada em cada acréscimo, ou nenhum? → A: **Nenhum.** O sistema não trava
  acréscimo nem convocação por prazo; a equipe é responsável por não chamar depois do calendário
  acadêmico (`D-005`). A história de usuário do prazo final, os quatro requisitos dela (os números de
  2470 a 2473 ficaram sem uso), a tela do limite e o critério de sucesso dele saíram da spec.
- Q: A quantidade acrescida aparece também na página pública da seleção, ou só na gestão? → A: **Só na
  gestão.** O público vê a lista de convocados que a equipe já publica, como no 69/2026 (`FR-2468`).

---

## User Scenarios & Testing *(mandatory)*

O ator é quem conduz a ocupação e a convocação do Edital — no TMD, o Setor de Seleção do Cefor. O
candidato não ganha tela nova: ele vê a convocação como vê hoje.

### User Story 1 - Registrar a vaga que o Edital regular liberou, e chamar o próximo (Priority: P1)

A matrícula de um aprovado do Edital regular não se efetivou. Quem conduz abre a ocupação do Perfil
de remanescentes, declara *"1 vaga acrescida"*, de onde ela veio (*"Edital Multicampi nº 20/2026,
matrícula não efetivada no Campus Vitória"*) e por quê, vê antes de confirmar quem a ordem do sorteio
alcança, e confirma. A apuração seguinte sai do próprio ato, e o primeiro da ordem passa a ser
chamável pela convocação que já existe.

**Why this priority**: é a capacidade inteira. Sem ela o Edital do TMD volta para a planilha, como a
Revisão avisa hoje.

**Independent Test**: num Edital publicado com um Perfil de 0 vagas imediatas, cadastro de reserva e
ordem do sorteio vigente, registrar 1 vaga acrescida pela tela da ocupação e convocar o primeiro
classificado pela tela da convocação, sem Retificação, sem shell e sem banco.

**Acceptance Scenarios**:

1. **Given** um Perfil publicado com 0 vagas imediatas, cadastro de reserva sem limite, ordem do
   sorteio vigente com 20 pessoas e nenhuma vaga acrescida, **When** quem conduz registra 1 vaga
   acrescida com origem e fundamento, **Then** a apuração vigente passa a dizer 0 publicadas e 1
   efetiva, o primeiro da ordem é titular, e a tela da convocação oferece convocá-lo.
2. **Given** o mesmo Perfil, **When** a pessoa abre o registro do acréscimo, **Then** antes da
   confirmação a tela diz quantas vagas o recorte terá depois do ato, quem a ordem alcança para elas,
   e que a apuração seguinte será emitida pelo próprio ato, com o autor e o motivo que levará.
3. **Given** 2 vagas acrescidas em dias diferentes, **When** alguém lê a ocupação, **Then** cada
   acréscimo aparece com quantidade, origem, fundamento, autor e instante, e a soma deles explica a
   diferença entre vagas publicadas e efetivas.
4. **Given** um titular convocado que não entrega os documentos, **When** o desfecho é registrado,
   **Then** a vaga volta a faltar e o próximo da ordem é chamável como suplente, exatamente como num
   Edital com vagas publicadas — o acréscimo não muda nada no que vem depois dele.
5. **Given** uma pessoa sem a permissão do acréscimo, **When** ela tenta registrá-lo, **Then** o ato é
   recusado e nada é gravado.

---

### User Story 2 - A Revisão diz a verdade sobre essa família (Priority: P1)

Quem elabora o próximo Edital do TMD publica um Perfil com 0 vagas imediatas e cadastro de reserva. A
Revisão deixa de dizer que a convocação será feita fora do sistema e passa a dizer como ela acontece
aqui: a cada vaga acrescida, registrada na ocupação.

**Why this priority**: o aviso de hoje é verdadeiro e vai deixar de ser. Frase verdadeira que vira
falsa é defeito maior do que frase ausente — quem a lê acredita nela e vai convocar por planilha um
recorte que o sistema convoca (o comentário da `034` em `ocupacao.html` registra o mesmo caso).

**Independent Test**: levar à Revisão um rascunho com Perfil só de reserva e ler o aviso.

**Acceptance Scenarios**:

1. **Given** um rascunho com Perfil de 0 vagas imediatas e reserva `LIMITED` ou `UNLIMITED`, **When** a
   Revisão roda no ato de publicação, **Then** o aviso diz que a convocação depende de vagas
   acrescidas depois da publicação e não diz que ela é feita fora do sistema.
2. **Given** o mesmo Perfil com Modalidade reservada no quadro de vagas, **When** a Revisão roda,
   **Then** ela diz que o acréscimo desta feature só alcança a ampla concorrência (`D-003`).

---

### User Story 3 - O acréscimo errado se desfaz por outro ato (Priority: P2)

Quem conduz registrou 2 vagas quando eram 1, ou registrou a vaga de uma matrícula que acabou se
efetivando. O acréscimo não se apaga: um ato contrário, com motivo e autor, devolve a quantidade, e a
apuração seguinte sai dele.

**Why this priority**: o erro vai acontecer — a informação vem de outro setor, por e-mail ou
telefone —, e sem a saída correta a equipe usaria a Retificação, que é exatamente o que esta spec
existe para evitar. Não é P1 porque o caso feliz não precisa dela.

**Independent Test**: registrar 2 vagas acrescidas, desfazer 1 com motivo, e conferir na ocupação que
as duas linhas continuam lá e a efetiva diz 1.

**Acceptance Scenarios**:

1. **Given** 2 vagas acrescidas e ninguém convocado para elas, **When** quem conduz desfaz 1 com
   motivo, **Then** a efetiva passa a 1, e a ocupação mostra o acréscimo e o desfazimento, cada um com
   autor e instante.
2. **Given** 1 vaga acrescida e o titular dela já convocado, **When** alguém tenta desfazê-la, **Then**
   o ato é recusado e a recusa diz que alguém já foi chamado para ela, e o desfecho a registrar antes.
3. **Given** 1 vaga acrescida e o titular dela ainda não convocado, **When** quem conduz a desfaz,
   **Then** o ato é aceito, e o 1º do sorteio deixa de ser titular.
4. **Given** um desfazimento sem motivo, **When** alguém confirma, **Then** o ato é recusado.

---

### Edge Cases

Os que mudam comportamento viraram requisito (`FR-2452`, `FR-2457`, `FR-2462`, `FR-2463`, `FR-2474`);
os demais são consequência do que já existe.

- **Mais vagas acrescidas do que pessoas na ordem.** O acréscimo é aceito — é um fato do outro Edital,
  e não uma promessa de chamada —, e a prévia diz que a ordem alcança menos pessoas do que as vagas.
  A convocação, ao chegar ao fim da ordem, recusa como recusa hoje.
- **A faixa publicada não alcança a reserva.** Um corte de alvo fixo pequeno, sem continuação
  admitida, deixa de fora classificados que o cadastro de reserva declara. A prévia do acréscimo diz
  quantos a faixa alcança, e a Revisão avisa antes de publicar (`FR-2474`).
- **Dois acréscimos simultâneos para a mesma matrícula do Edital regular.** O sistema não sabe que é a
  mesma matrícula. A prévia mostra os acréscimos anteriores com a origem de cada um, e a confirmação
  carrega a identidade da apuração vigente: o segundo, confirmado sobre a apuração que o primeiro já
  sucedeu, é recusado e reapresentado.
- **Perfil com vagas imediatas e reserva**, no formato do próprio 69/2026: as 6 vagas publicadas
  seguem como hoje, e uma sétima que o Edital regular libere depois entra por acréscimo.
- **Perfil sem cadastro de reserva.** O acréscimo é recusado: sem reserva publicada, não há norma que
  autorize chamar além das vagas (`D-002`).
- **Retificação do quadro depois de um acréscimo.** A apuração passa a obsoleta pela causa que a `016`
  já nomeia, e a emissão seguinte soma o quadro retificado e os acréscimos — o acréscimo não se perde
  nem se duplica.
- **Ordem sucedida depois de um acréscimo** (o desempate julgado, um recurso deferido). O acréscimo é do
  recorte, e não da ordem: continua valendo sobre a ordem nova.

## Requirements *(mandatory)*

### A vaga acrescida

- **FR-2450**: O sistema MUST permitir registrar, num Perfil publicado, uma **vaga acrescida depois da
  publicação**: um ato append-only com quantidade inteira positiva, recorte, origem, fundamento, autor
  e instante. Ele MUST NOT alterar o conteúdo publicado do Edital, nem produzir Publicação, versão,
  documento ou aviso aos candidatos.
- **FR-2451**: A origem MUST dizer de onde a vaga veio em texto obrigatório (no TMD, o número do Edital
  regular e o campus), e o fundamento MUST dizer por quê (a matrícula não efetivada, a desistência).
  Uma referência ao processo administrativo MAY acompanhá-los. O ato sem origem ou sem fundamento MUST
  ser recusado.
- **FR-2452**: A apuração de ocupação MUST somar as vagas acrescidas do recorte às vagas efetivas,
  além do que publicou e do que os movimentos de vaga já movem, e MUST congelar quais acréscimos leu,
  para que a reprodução de uma apuração antiga devolva o número que ela apurou (`FR-244`). O
  acréscimo é do recorte, e não da ordem nem da versão: ordem sucedida e quadro retificado depois dele
  não o desfazem nem o duplicam, e a emissão seguinte o soma ao que a versão vigente publica.
- **FR-2453**: Acréscimo posterior à apuração vigente MUST torná-la obsoleta com causa própria,
  nomeada na leitura do recorte ao lado das que a `016` e a `019` já nomeiam (`FR-263`).
- **FR-2454**: O próprio ato do acréscimo MUST emitir a apuração seguinte do recorte quando o
  acréscimo for a única causa de obsolescência, pela mesma conta que a emissão da ocupação e o
  desfecho de convocação usam; com qualquer outra causa presente, MUST gravar o acréscimo, deixar a
  apuração obsoleta e dizer qual ato falta (`FR-882`, `FR-884`).
- **FR-2455**: A convocação MUST tratar a vaga acrescida como trata a vaga publicada: quem a apuração
  conta como titular é chamável pelo gesto da `050`, o suplente pela chamada individual, e a recusa
  `sem_deficit` continua valendo quando nenhuma vaga, publicada ou acrescida, falta. Esta spec revisa
  a `FR-889` da `050` nessa medida, e só nela.
- **FR-2456**: Antes da confirmação, a tela MUST declarar a apuração vigente, os acréscimos
  anteriores do recorte com a origem de cada um, quantas vagas o recorte terá depois do ato, quem a
  ordem vigente alcança para elas — nominalmente, na ordem — e que a apuração seguinte será emitida
  pelo ato, com o autor e o motivo que levará.
- **FR-2457**: A confirmação MUST carregar a identidade da apuração vigente que a prévia mostrou; se ela
  tiver sido sucedida entre a prévia e a confirmação, o ato MUST ser recusado sem gravar nada, e a
  tela MUST mostrar a prévia nova (`FR-863`).
- **FR-2458**: O ato MUST ser idempotente pela chave da requisição: a mesma confirmação reenviada
  devolve o acréscimo já gravado e não grava um segundo.
- **FR-2459**: O ato MUST ser recusado quando o recorte não tiver ordem vigente ou não tiver linha no
  quadro de vagas, com as recusas que a emissão da apuração já dá para esses casos.

### Desfazer o acréscimo

- **FR-2460**: O sistema MUST permitir desfazer, no todo ou em parte, uma vaga acrescida por um ato
  append-only contrário, com quantidade, motivo obrigatório, autor e instante, que cita o acréscimo
  desfeito. Nenhum dos dois MUST ser alterado ou excluído.
- **FR-2461**: A apuração MUST descontar o desfazimento das vagas efetivas pelas mesmas regras de
  congelamento, obsolescência e emissão da `FR-2452` à `FR-2454`.
- **FR-2462**: O desfazimento MUST ser recusado quando deixaria o recorte com menos vagas efetivas do
  que pessoas com convocação em aberto ou atendida nele, e a recusa MUST dizer qual desfecho registrar
  antes. Quem só está entre os titulares que a apuração conta, sem ter sido chamado, MUST NOT impedir o
  desfazimento: sai da conta, e ninguém lhe disse nada. Ele MUST ser recusado também quando a quantidade exceder o que resta do
  acréscimo citado.

### Quem pode, e onde

- **FR-2463**: O acréscimo MUST ser recusado em Perfil cujo conteúdo vigente não declare cadastro de
  reserva (`LIMITED` ou `UNLIMITED`), com recusa que diga que, sem reserva publicada, chamar além das
  vagas exige Retificação (`D-002`).
- **FR-2464**: O acréscimo MUST alcançar só a linha geral do quadro — a ampla concorrência — e vale
  no recorte em que foi registrado. Em Perfil cujo quadro tenha qualquer linha de Modalidade, com vaga
  ou sem, ou que declare reversão, ele MUST ser recusado, com recusa que diga que a repartição entre
  modalidades está fora desta feature (`D-003`).
- **FR-2465**: Registrar e desfazer acréscimo MUST exigir a mesma autorização e a mesma verificação de
  escopo que a emissão da apuração de ocupação já exige — a gestão da comissão do Processo —, e MUST
  NOT criar autoridade nova (`D-004`).
- **FR-2466**: Acréscimo e desfazimento MUST entrar na trilha de auditoria do Processo com ator, ação,
  recorte, quantidade, origem ou motivo, apuração anterior e seguinte, instante e correlação.
- **FR-2467**: A tela MUST orientar que origem e fundamento não identifiquem pessoas do outro Edital:
  basta o número do Edital, o campus e a natureza do fato. O sistema MUST NOT exibir origem e fundamento
  fora da gestão: nem no portal, nem no documento do Edital, nem na página pública, nem no aviso aos
  candidatos. O fundamento derivado da convocação, que o convocado lê no portal, MUST continuar citando
  a apuração que registrou a vaga, e MUST NOT reproduzir o texto de origem ou de fundamento do
  acréscimo.
- **FR-2468**: A quantidade acrescida MUST aparecer só na gestão. A página pública da seleção, o
  documento do Edital e o portal MUST continuar dizendo as vagas que o Edital publicou; o que o público
  vê da chamada é a lista de convocados que a equipe publica, como no 69/2026.

### A Revisão

- **FR-2474**: O aviso `reserve_only_convocation_external` MUST deixar de dizer que a convocação é feita
  fora do sistema, e MUST passar a dizer que ela depende de vagas acrescidas depois da publicação,
  registradas na ocupação. Ele MUST continuar advertência, e só no ato de publicação. Quando a regra de corte
  do marco não admitir continuação, o aviso MUST dizer quantos classificados a faixa publicada poderá
  alcançar — o alvo fixo mais o excedente, ou só o excedente quando o alvo é o do quadro, que neste
  Perfil é zero.
- **FR-2475**: Em Perfil só de reserva com Modalidade reservada no quadro, a Revisão MUST avisar que o
  acréscimo desta feature não alcança aquele Perfil (`FR-2464`).
- **FR-2476**: Editais já publicados MUST NOT ser reavaliados nem republicados: a advertência é da
  publicação, e o acervo continua dizendo o que disse.

### A tela

- **UX-220** — **O acréscimo mora na ocupação, ao lado do número que ele muda.** O recorte mostra
  publicadas, acrescidas e efetivas em linhas separadas, e *"acrescidas"* é um link para a lista dos
  atos. Nunca um número só que esconda de onde veio.
- **UX-221** — **A prévia fala de pessoas, não de posições.** *"1 vaga acrescida: a ordem alcança
  Maria S., 1ª do sorteio"*; com mais vagas do que pessoas, *"3 vagas acrescidas; a ordem alcança só
  mais 2 pessoas"*.
- **UX-222** — **O botão diz o número.** *"Acrescentar 1 vaga"*, *"Desfazer 1 vaga"*: nenhum ato desta
  feature tem botão sem quantidade (o mesmo da `UX-100`).

### Key Entities

- **Vaga acrescida**: quantidade que entra num recorte depois da publicação, por fato de fora do
  Edital. Recorte (Edital, Perfil, marco, linha geral), quantidade, origem, fundamento, referência
  opcional, autor, instante. Append-only. Lida e congelada pela apuração.
- **Desfazimento de vaga acrescida**: quantidade que sai, citando o acréscimo desfeito, com motivo,
  autor e instante. Append-only.
- **Apuração de ocupação** (existe, `016`): ganha os acréscimos lidos e a causa de obsolescência nova.
- **Convocação** (existe, `019`/`050`): não muda; passa a ter vaga para a qual chamar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-920**: O cenário do TMD fecha pela interface administrativa, sem shell, banco nem Retificação:
  publicar um Perfil com 0 vagas e reserva, sortear, divulgar a ordem, acrescentar 1 vaga, convocar o
  primeiro por publicação, registrar o não atendimento, e convocar o seguinte.
- **SC-921**: Da vaga liberada no Edital regular à convocação publicada, quem conduz faz no máximo
  dois atos confirmados — o acréscimo e a convocação — e nenhuma apuração à mão.
- **SC-922**: Para toda apuração de um recorte com acréscimos, a diferença entre efetivas e publicadas
  é igual à soma dos acréscimos lidos menos os desfazimentos lidos, mais os movimentos de vaga; a
  conferência vale também para a apuração antiga relida.
- **SC-923**: Nenhum Edital só de reserva publicado depois desta feature mostra, na Revisão, a frase
  de que a convocação é feita fora do sistema.
- **SC-924**: Leitura do recorte, prévia e ato do acréscimo têm custo de consulta que não cresce com
  o número de acréscimos registrados nem com o tamanho da ordem.

## Assumptions

### D-001 — O acréscimo é fato operacional, e não norma

A quantidade publicada continua sendo a do Edital; o acréscimo é o registro de que um fato de fora o
completou. É a recomendação da `DP-05` (*"a necessidade superveniente de convocação como fato
operacional auditável e append-only, e não como Retificação das vagas"*). A Retificação continua
sendo o caminho para mudar o que o Edital diz — inclusive para publicar uma quantidade nova, se a
equipe preferir.

### D-002 — Só Perfil com cadastro de reserva aceita acréscimo

O cadastro de reserva publicado é a norma que autoriza chamar além das vagas; o acréscimo diz
quando. Sem reserva, a chamada além das vagas não tem fundamento no Edital, e a recusa manda à
Retificação.

### D-003 — Só a linha geral

O TMD não tem cotas, e a repartição de uma vaga superveniente entre modalidades é a ordem de chamada
entre modalidades (P-1 dos achados), que a `DP-05` listou e esta spec não decide. Recusar é mais
honesto do que escolher um recorte.

### D-004 — A autoridade de quem apura, e nenhuma nova

O acréscimo muda o número que decide quem é chamado, e o Princípio III pede autorização específica
para isso. A autorização específica já existe: é a gestão da comissão do Processo, que a emissão da
apuração, a do corte e a convocação exigem — o gestor, ou a presidência daquele Processo. Uma
capacidade nova seria concedida por papel, e a presidência, que hoje apura e convoca, deixaria de
poder acrescentar a vaga do próprio certame. É a regra que a ocupação já registra no código, *"a
autoridade é consumida, não inventada"*, e a que a `FR-887` da `050` repetiu para os gestos dela.

*Revista ao planejar, em 21/10/2026.* A primeira redação pedia permissão própria, concedida por padrão
aos papéis de quem apura; o mapeamento mostrou que a ocupação não é autorizada por papel, e sim pela
comissão (`research.md`, T-007).

### D-005 — O prazo final das convocações é da equipe, e não do sistema

Decisão do usuário em 21/10/2026, entre quatro formas: Evento do Cronograma, campo do Perfil, data em
cada acréscimo, ou nenhuma. **Nenhuma**: o sistema não recusa acréscimo nem convocação por prazo, e a
equipe responde por não chamar depois do calendário acadêmico (7.2 do 69/2026), como já responde hoje.
Pesou contra as outras: o 69/2026 não escreve a data, só remete ao calendário, e as duas formas
publicadas obrigariam a equipe a escrevê-la; a data em cada acréscimo seria lembrete, e não limite, e
não alcançaria o suplente chamado depois de um desfecho; e a validade dos Editais de bolsista é regra
(*"2 anos a partir da homologação, prorrogável uma única vez"*), e não data, de modo que escolher agora
uma forma de data arriscaria a spec seguinte ter de desfazê-la. A Revisão também não avisa da
ausência: o aviso sairia em todo Edital desta família, e viraria ruído.

### Outras premissas

- **O Edital regular fica fora do sistema.** A origem é texto declarado, e não referência a outro
  Processo daqui. Quando o regular rodar aqui, derivar a vaga dele é outra spec.
- **O limite da reserva continua sem efeito.** O `reserveLimit` e o alvo do corte são duas declarações
  da mesma norma (segunda pergunta da `DP-05`); esta spec não as une. Quem governa quantos o sistema
  alcança continua sendo o corte publicado, e a `FR-2474` faz a Revisão dizer quantos são.
- **O candidato não ganha tela.** A convocação aparece no portal como hoje, e o aviso *"Nova chamada
  publicada"* da `066` vale para ela como para qualquer outra.
- **A `096` muda a mesma vizinhança.** Ela imprime `CR` no lugar do `0` e toca a validação desta
  família; o plano desta spec precisa partir do que ela tiver mergeado.

## Out of Scope

- Ordem de chamada entre modalidades e acréscimo em Modalidade reservada (`D-003`).
- Semântica do limite da reserva e sua relação com o alvo do corte.
- Qualquer prazo final das convocações, data ou regra de validade, publicado ou informado (`D-005`); a
  validade de seis meses prorrogável e o suplente convocável para a turma seguinte (P-3).
- Derivar a vaga acrescida de um Edital regular que rode neste sistema.
- **Os Editais de bolsista de cadastro de reserva** (140/2025, 173/2025, 89/2026, 90/2026), por
  decisão do usuário em 21/10/2026: spec própria, depois desta. Eles reusam o acréscimo — a origem é a
  demanda da Administração com bolsa disponível, e não outro Edital —, mas dependem de três coisas que
  esta não tem: a **sequência de convocação entre modalidades** publicada como dado (*"1ª AC, 2ª PcD,
  3ª PPIQ…"*, item 10.5 do 140), que cada acréscimo consumiria em ordem; a vaga que volta à ampla na
  falta de candidato da modalidade (4.5 do 140, 7.6 do 89); e a **validade de 2 anos prorrogável uma
  vez** (14.1 do 140). O desligamento do bolsista depois da vinculação, que libera vaga sem ser
  desfecho de convocação, é pergunta dela.
- Retificar as vagas imediatas como meio de convocação.
