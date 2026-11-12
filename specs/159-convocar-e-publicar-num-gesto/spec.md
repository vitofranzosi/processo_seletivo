# Feature Specification: Convocar e publicar num gesto só

**Feature Branch**: `claude/convocar-e-publicar`, sobre `claude/demonstracao-publicacao-convocados`
(PR #503), que sai da `main` em `fe86f6d0`

**Created**: 2026-11-12

**Status**: Em implementação. Evolução deliberada da `149`, pedida pelo usuário em 12/11/2026 depois
da demonstração no cenário C10. As decisões de desenho estão no [research](research.md), de D-001 a
D-010; a D-001 lista o que esta spec substitui da `149`, da `140` e da `125`.

**Input**: pedido do usuário de 12/11/2026, *"unificar o gesto de convocar e publicar a relação na
página pública do GPS, inclusive quando o próprio GPS for o veículo oficial da convocação"*: a
comissão confere uma vez, confirma uma vez e encontra a relação publicada.

> **Faixa de identificadores.** Esta spec abre em **FR-6801** e **SC-2251**. O teto medido em
> 12/11/2026, na `main`, nas worktrees desta máquina e nos PRs abertos, era o requisito seis mil
> setecentos e vinte e nove e o critério dois mil duzentos e doze. A pasta `158` é a última tomada.
> **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-5703 da `149`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

A `149` fez a publicação de convocados um ato próprio, com autoridade, prévia e confirmação, separado
de convocar. Na homologação de 12/11/2026, a comissão convocou os titulares do C10 por mensagem
individual — as três mensagens saíram, os candidatos já viam a convocação — e a lista não foi para a
página pública: faltava um segundo percurso, que nenhuma tela oferecia naquela forma. A demonstração
está em [`doc/demonstracao-publicacao-de-convocados-2026-11-12/`](../../doc/demonstracao-publicacao-de-convocados-2026-11-12/roteiro.md).

**O usuário decidiu que a publicação deixa de exigir um segundo percurso.** O ato aconteceu, as
mensagens foram encaminhadas, os candidatos já têm acesso: a relação pública é consequência da mesma
confirmação. E quando o GPS é o veículo oficial, convocar e publicar são o mesmo ato.

### O que esta spec cobre, e o que fica fora

**Cobre:** a conferência e a confirmação únicas nos gestos que convocam — os titulares num ato só, a
chamada individual (suplente, regularização) e a correção (`120`) — e no registro da publicação
externa; o comportamento diante de falha parcial; e o caminho para concluir o que ficou pendente
sem repetir atos.

**Fica fora:** mudar a semântica dos prazos (`019`, `125`, `149`); o desfecho; os documentos; a
conferência antes de chamar uma pessoa da `152`, que está em PR (#502) e se compõe com esta pelos
mesmos campos (D-009); e retirar a página *Publicação das convocações*, que continua para o que
ficou pendente e para convocações anteriores a esta feature.

## Clarifications

### Session 2026-11-12 (pedido do usuário)

- Q: Convocar deve publicar? → A: **Sim, na mesma confirmação**, nas três formas: por mensagem
  individual, publica a relação informativa das comunicadas com sucesso; por publicação no GPS,
  convoca e publica oficialmente, com a comunicação e o prazo no instante da publicação e a
  declaração do veículo na mesma conferência; por publicação externa, o caminho de hoje é preservado,
  e o registro da publicação externa também divulga a relação informativa no GPS.
- Q: A forma "por publicação" basta para publicar no GPS? → A: **Não.** Ela não autoriza presumir
  que o veículo seja o GPS: a comissão escolhe o veículo na conferência.
- Q: Pode haver segunda confirmação para publicar? → A: **Não.** Uma conferência, um botão, que diz
  as consequências.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Por mensagem: convocar, enviar e publicar numa confirmação (Priority: P1)

A comissão confere os titulares de um Perfil por mensagem individual. A conferência mostra quem será
convocado, as mensagens, o prazo — contado do envio —, o que será público, a natureza (relação
informativa), a autoridade e quem fica de fora. Um botão: *"Convocar, enviar mensagens e publicar a
relação"*. Ao confirmar, as convocações nascem, as mensagens saem e a relação das comunicadas com
sucesso vai para a página pública.

**Independent Test**: no C10, convocar os três titulares e encontrar a 1ª publicação na página
pública, sem abrir a página de publicação.

**Acceptance Scenarios**:

1. **Given** três titulares por mensagem, **When** a comissão confirma a conferência com a
   autoridade escolhida, **Then** há três convocações, três comunicações enviadas e uma publicação
   informativa com as três, e a página pública mostra a seção *Convocações*.
2. **Given** que uma das três mensagens falha, **When** a confirmação termina, **Then** a relação
   publicada tem as duas que saíram; a tela diz que uma falhou, que o prazo dela não começou e que ela
   não está na relação; e o reenvio, pelas pendentes, envia e publica numa confirmação só.
3. **Given** a confirmação repetida com a mesma chave (duplo clique), **Then** nada é praticado de
   novo: nem convocação, nem mensagem, nem publicação.

---

### User Story 2 — Por publicação no GPS: convocar e publicar oficialmente (Priority: P1)

Num Perfil por publicação, a conferência pede o veículo. Escolhido *"Na página pública do GPS"*, ela
pede a declaração do item do Edital que o admite, mostra a relação que será publicada como **ato
oficial**, diz que o prazo começa no instante da publicação, e o botão diz *"Convocar e publicar no
GPS"*. Ao confirmar, convocações, comunicações e publicação nascem juntas, num instante só.

**Acceptance Scenarios**:

1. **Given** dois titulares por publicação, **When** a comissão escolhe o GPS, declara o item e
   confirma, **Then** há duas convocações, uma publicação oficial, e cada comunicação tem o instante
   da publicação; o prazo está em curso e o candidato vê a convocação.
2. **Given** a mesma conferência sem a declaração, **When** a comissão confirma, **Then** é recusado
   e nada é gravado — nem convocação.
3. **Given** a confirmação, **When** a publicação não pode ser gravada (autoridade fora de vigência,
   por exemplo), **Then** nada é gravado: convocar e publicar no GPS é um ato só.

---

### User Story 3 — Por publicação externa: o caminho de hoje, mais a relação no GPS (Priority: P2)

Escolhido *"Fora do GPS"*, a conferência diz que a convocação aguardará o registro da publicação, e o
botão diz *"Convocar (a publicação será registrada depois)"*. Ao registrar onde publicou, na seção das
pendentes, o mesmo gesto registra a comunicação de cada um e publica no GPS a relação informativa,
citando a referência.

**Acceptance Scenarios**:

1. **Given** convocações aguardando publicação externa, **When** a comissão registra a referência com
   a autoridade, **Then** cada uma tem a comunicação registrada, como hoje, e há uma publicação
   informativa no GPS que cita a referência.
2. **Given** o mesmo registro, **Then** o prazo corre do registro, e não da publicação no GPS.

---

### User Story 4 — Suplente, regularização e correção (Priority: P2)

A chamada individual e a correção da convocação seguem a mesma regra pela forma e pelo veículo, com a
autoridade no próprio formulário e o que será público dito antes do botão. A correção de convocação
já publicada sai marcada como correção da publicação anterior, e a anterior a aponta.

**Acceptance Scenarios**:

1. **Given** uma suplente chamada por mensagem, **When** a comissão confirma, **Then** ela é
   convocada, a mensagem sai, e há uma publicação com ela.
2. **Given** a correção do vencimento de uma convocação publicada no GPS como ato oficial, **When** a
   comissão confirma escolhendo o GPS, **Then** a correção é publicada oficialmente, marcada *"corrige
   a convocação divulgada na ‹N›ª publicação"*, e o prazo novo corre dela.

### Edge Cases

- **Todas as mensagens falham.** Nenhuma publicação é feita, e a tela o diz.
- **A publicação informativa falha depois dos envios** (por exemplo, alguém publicou ao mesmo tempo).
  As convocações e mensagens ficam como estão; a tela diz que a relação não foi publicada e por quê, e
  a seção *"Na página pública da seleção"* da tela do recorte oferece concluir.
- **Repetir a confirmação depois de uma falha parcial**, com a mesma chave: as convocações e as
  mensagens já praticadas não se repetem; o que não começou se completa; a publicação que não saiu sai.
- **Sem autoridade vigente na unidade.** A conferência não oferece o botão: o ato publicaria, e não há
  quem assine.
- **Perfil sem forma declarada.** Como hoje: a convocação nasce e não é comunicada, e não há o que
  publicar.
- **Convocações anteriores a esta feature.** Continuam pela página de publicação da `149`.

## Requirements *(mandatory)*

### Functional Requirements

#### A. A conferência e a confirmação únicas

- **FR-6801**: Os gestos que convocam — os titulares num ato só, a chamada individual, a convocação
  para regularizar e a correção — MUST praticar a publicação da relação na **mesma confirmação**, sem
  segunda conferência nem segundo botão.
- **FR-6802**: Antes da confirmação, a conferência MUST apresentar: as pessoas e os dados que ficarão
  públicos (os da FR-5712 da `149`); o veículo e a natureza da publicação (*ato oficial* ou *relação
  informativa*); o prazo e o momento em que começa; a autoridade signatária, escolhida ali; e quem fica
  de fora e por quê.
- **FR-6803**: O botão MUST expressar as consequências: *"Convocar, enviar mensagens e publicar a
  relação"* na mensagem individual; *"Convocar e publicar no GPS"* na publicação no GPS; *"Convocar (a
  publicação será registrada depois)"* na publicação externa.
- **FR-6804**: Sem autoridade vigente na unidade do Edital, a conferência MUST NOT oferecer a
  confirmação que publicaria, e MUST dizer por quê.

#### B. Por mensagem individual

- **FR-6805**: A confirmação MUST convocar, enviar as mensagens e, depois dos envios, publicar a
  relação **informativa** das convocações deste gesto **comunicadas com sucesso**. A publicação MUST
  NOT alterar prazo nenhum: o prazo corre do envio, como na `019`.
- **FR-6806**: A convocação cujo envio falhou MUST NOT entrar na relação publicada, e a tela do
  resultado MUST dizer quantas falharam, que o prazo delas não começou e que não estão na relação.
- **FR-6807**: O reenvio das que falharam, pelo gesto das comunicações pendentes, MUST publicar na
  mesma confirmação as que saírem, numa publicação nova.

#### C. Por publicação

- **FR-6808**: Na forma por publicação, a conferência MUST pedir o veículo — *na página pública do
  GPS* ou *fora do GPS* —, sem presumir nenhum dos dois.
- **FR-6809**: No GPS, a confirmação MUST convocar e publicar oficialmente **numa transação só**: as
  convocações, a publicação, a comunicação de cada uma — com o instante da publicação — e o documento
  nascem juntos, ou nada nasce. A declaração do item do Edital que admite o GPS (a FR-5703 da `149`)
  MUST estar na mesma conferência, e sem ela a confirmação MUST ser recusada sem gravar nada.
- **FR-6810**: Fora do GPS, a confirmação MUST convocar como hoje, e a convocação MUST aguardar o
  registro da publicação externa (a 1ª decisão da `125`).
- **FR-6811**: O registro da publicação externa, pelo gesto das pendentes, MUST, na mesma
  confirmação, registrar a comunicação de cada convocação e publicar no GPS a relação **informativa**
  das registradas, citando a referência. O prazo MUST correr do registro, como hoje.

#### D. Falhas parciais e conclusão do pendente

- **FR-6812**: A publicação informativa (mensagem, publicação externa) MUST acontecer depois dos
  envios ou registros, numa transação própria; sua falha MUST NOT desfazer convocações nem
  comunicações, e a tela MUST dizer que a relação não foi publicada e o motivo.
- **FR-6813**: Repetir a confirmação com a mesma chave MUST completar o que não começou — envios e
  publicação — e MUST NOT repetir convocação, mensagem ou publicação já praticadas.
- **FR-6814**: O que ficou de fora da publicação de um gesto MUST continuar alcançável pela seção *"Na
  página pública da seleção"* da tela do recorte e pela página de publicação da `149`.
- **FR-6815**: A publicação de um gesto MUST conter só convocações daquele gesto; se alguma já tiver
  sido publicada por outro caminho no meio, ela MUST ficar fora, e não impedir as demais.

#### E. Suplente, regularização e correção

- **FR-6816**: A chamada individual, a convocação para regularizar e a correção MUST seguir as regras
  B a D, com a autoridade, o veículo, a declaração e o que será público no próprio formulário.
- **FR-6817**: A correção de convocação já publicada MUST sair marcada como correção da publicação
  anterior (a FR-5717 da `149`), e a anterior MUST apontá-la (a FR-5720 da `149`).

#### F. O que se preserva

- **FR-6818**: Atos imutáveis, autoria, permissões, minimização de dados e a proteção contra
  duplicidade (a FR-5707 da `149`) MUST continuar valendo; a publicação de um gesto MUST usar a trava
  do Processo e a idempotência do gesto.

### Key Entities

Nenhuma entidade nova. A publicação continua sendo a `PublicacaoDeConvocados` da `149`.

## Success Criteria *(mandatory)*

- **SC-2251**: No C10, uma confirmação na conferência dos titulares deixa as três convocações
  comunicadas e a relação na página pública, sem abrir a página de publicação.
- **SC-2252**: Com uma mensagem falhando, a relação publicada tem as demais, a falha é dita na tela,
  e o reenvio publica a que saiu.
- **SC-2253**: Por publicação no GPS, convocação, publicação e comunicação têm o mesmo instante, e a
  recusa da publicação não deixa convocação gravada.
- **SC-2254**: O registro da publicação externa deixa a comunicação de cada uma e uma relação
  informativa no GPS que cita a referência, sem mudar o instante de onde o prazo corre.
- **SC-2255**: A confirmação repetida com a mesma chave não grava convocação, comunicação nem
  publicação novas.
- **SC-2256**: A suplente chamada por mensagem e a correção publicada no GPS saem na página pública,
  a correção marcada.

## Assumptions

- **A autoridade é escolhida em cada confirmação**, como na página de publicação da `149` (4ª decisão
  do usuário da `149`).
- **Uma publicação por gesto.** Cada confirmação que publica gera uma publicação numerada; a seção da
  página pública mostra as três mais recentes e recolhe as demais (a FR-5721 da `149`).
