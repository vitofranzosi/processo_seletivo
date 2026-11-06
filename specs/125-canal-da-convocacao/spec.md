# Feature Specification: A convocação segue o canal

**Feature Branch**: `claude/gifted-elbakyan-1ab054`, sobre a `main` em `250efe97`

**Created**: 2026-11-06

**Status**: Draft, **só documental**. Nenhum código, migration, rota ou tela foi alterado. As
decisões têm duas origens:

- **Do usuário, em 06/11/2026**, sobre os três pontos do quadro *"Atenção"* do capítulo 10 do guia da
  jornada do sorteio: a *1ª*, a *2ª* e a *3ª decisão*, abaixo. Não se reabrem.
- **Propostas de desenho desta spec:** D-001 a D-008, ao fim. Elas resolvem o que as três decisões
  deixaram aberto, ou o que a leitura do código mostrou que elas não alcançavam. **Aceitas pelo
  usuário em 06/11/2026, as oito, como propostas.**

**Input**: o guia de condução
[`doc/guia-jornada-do-sorteio-2026-11-05/`](../../doc/guia-jornada-do-sorteio-2026-11-05/index.html),
capítulo 10 (*"Atenção"*: *"O candidato vê a convocação no portal antes da publicação oficial. O
fundamento digitado pelo operador vai para o candidato como está [...] Na convocação por publicação,
a página diz 'Comunicação enviada em' e 'contado do envio', embora nada tenha sido enviado."*),
reconferido em 06/11/2026 sobre a `main` em `250efe97`, com a `121` já implementada (PR #404).

> **Faixa de identificadores.** Esta spec abre em **FR-3981** e **SC-1201**. O teto foi medido em
> 06/11/2026 em `specs/` de todas as worktrees desta máquina: o requisito funcional três mil
> novecentos e sessenta e oito e o critério mil cento e noventa e dois, da `124` que a worktree do
> sorteio escreve, ainda fora da `main`. As pastas `123` (PR #409) e `124` estão tomadas, e por isso
> esta é a `125`. A folga, até a FR-3981 e a SC-1201, é a mesma que a `124` deixou: duas sessões do
> mesmo dia já colidiram contando do mesmo teto. **Nenhum `UX-` é aberto aqui.** As decisões
> reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3749 da `118`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número.

---

## Por que esta feature existe

**A convocação por publicação existe para o candidato antes de existir para o mundo.** A comissão
pratica a convocação no GPS, publica a lista no site do certame e só então registra a publicação. Entre
o primeiro e o último gesto, que podem distar dias, o portal já mostra *"Você foi convocado!"*, o
fundamento e o caminho para enviar documentos. É o estado *"convocado, prazo não iniciado"* que a
`019` exigiu legível, e a `121` desenhou (cenário K). Nada disso é defeito: as specs previam. Mas,
na convocação por publicação, quem convoca é a publicação, e o portal anuncia o ato antes do ato
oficial.

**O texto que o operador digita chega ao candidato sem que o operador saiba.** O *"Complemento do
fundamento"* entra depois do fundamento derivado, e o fundamento do desfecho aparece como
*"Resultado registrado: ‹desfecho› — ‹fundamento›"*. Nenhum campo diz que o texto será lido pelo
candidato. Um operador que escreva *"vaga aberta pela desistência de ‹nome›"* expõe outra pessoa, e
em lote expõe a todos os convocados do ato. A `120` tirou do portal o motivo da correção pela mesma
razão. Aqui, o usuário decidiu manter os textos visíveis, com aviso e prévia.

**Na convocação por publicação, as telas falam de um envio que não houve.** O registro da publicação
grava uma comunicação com resultado *"enviada"*, e as telas leem dali *"Comunicação enviada em"*,
*"contado do envio da comunicação"* e *"O prazo ainda não começou a correr: ele conta a partir do
envio da comunicação"* — esta, palavra por palavra, exigida pela FR-3749 da `118`. A `121` já
corrigiu um caso, a linha *"Convocação substituída"*, que diz *"Publicada em ‹referência›"*. Esta spec
estende o padrão a todas as telas.

### O que esta spec cobre, e o que fica fora

**Cobre:**

1. A convocação comunicada por publicação fica invisível em todo o portal até o registro da
   publicação: na lista, no acompanhamento, na tela da convocação, no endereço direto, no envio de
   documentos e no Requerimento de Matrícula da chamada. Na mensagem individual, nada muda (1ª
   decisão).
2. O aviso *"Este texto será mostrado ao candidato."* em cada campo de texto livre que chega ao
   candidato, e a prévia antes da confirmação, com o número de pessoas no lote (2ª decisão).
3. O vocabulário da comunicação por canal, no portal e na gestão: *publicada* na publicação, *enviada*
   na mensagem (3ª decisão), com as revisões das specs anteriores escritas e aplicadas.

**Fica fora:**

- O aviso de pendência documental por e-mail (`QI-7` da `115`).
- Os modelos de e-mail da convocação: só existem na mensagem individual, e já dizem *enviamos*.
- A regra do prazo: ele continua começando no registro da comunicação bem-sucedida, nas duas formas.
  Muda o que as telas dizem dele, não quando ele começa.
- Os textos livres que chegam ao candidato fora da convocação e do desfecho, como o motivo da
  conferência de documento: registrados ao fim, para decisão própria.
- O sistema publicar no site do certame. Continua não publicando: quem publica é a comissão.

## Clarifications

### Session 2026-11-06 (decisões do usuário sobre o guia)

- Q: O candidato pode ver a convocação por publicação antes do registro da publicação? → A: **Não.**
  Ela só aparece depois do registro da publicação oficial pela comissão, em todo o portal: o
  acompanhamento, a lista, a tela da convocação, o acesso por endereço direto e o envio de documentos,
  que fica recusado antes do registro. Na mensagem individual, o estado *"convocado, prazo não
  iniciado"* da `019` continua visível. *(1ª decisão)*
- Q: Os textos digitados que chegam ao candidato saem do portal, como o motivo da correção na `120`?
  → A: **Não, continuam visíveis**: o complemento do fundamento e o fundamento do desfecho. Cada campo
  diz *"Este texto será mostrado ao candidato."*; antes da confirmação, a tela mostra a prévia do texto
  como o candidato o verá; no lote, a prévia diz quantas pessoas receberão o mesmo texto. *(2ª
  decisão)*
- Q: Que palavra a tela usa para a comunicação? → A: **A do canal**: *publicada* na convocação por
  publicação, *enviada* na comunicação por mensagem, em todas as telas afetadas, do portal e da
  gestão, com os requisitos revistos explicitamente — inclusive a FR-3749 da `118`. *(3ª decisão)*
- Q: O aviso de pendência por e-mail entra? → A: **Não.** A `QI-7` da `115` continua fora.

## User Scenarios & Testing *(mandatory)*

Os cenários usam o vocabulário da `121`: **K** é a convocação sem comunicação bem-sucedida. Aqui ele se
desdobra em **K-pub**, a comunicada por publicação sem registro, e **K-msg**, a comunicada por
mensagem sem envio bem-sucedido.

### User Story 1 — O candidato só vê a convocação por publicação depois de publicada (Priority: P1)

A comissão convoca os titulares de um recorte cujo Perfil declara a forma *por publicação*. Até
registrar onde e quando publicou a lista, nenhum convocado encontra a convocação no portal, por
caminho nenhum. Registrada a publicação, a convocação aparece em todas as telas ao mesmo tempo, com o
prazo correndo.

**Why this priority**: é a decisão que protege o ato oficial. Antes dela, o portal anuncia o que a
Administração ainda não publicou, e aceita documento de quem nenhum ato público chamou.

**Independent Test**: convocar por publicação, percorrer o portal como o convocado e não achar a
convocação; registrar a publicação e achá-la em todas as superfícies.

**Acceptance Scenarios**:

1. **Given** uma convocação por publicação praticada e sem publicação registrada (K-pub), **When** o
   convocado abre *"Minhas inscrições"*, **Then** o item dele é o de quem não tem convocação: sem
   indicação de convocação aberta, e com *"Acompanhar"* como ação principal.
2. **Given** K-pub, **When** ele abre o acompanhamento, **Then** não há seção *"Convocação"*.
3. **Given** K-pub, **When** ele abre o endereço da convocação da própria inscrição, **Then** a tela é a
   de quem não tem convocação, e ela não diz que o certame chegou a convocar no recorte se só houver
   convocações sem publicação registrada.
4. **Given** K-pub com documento pedido, **When** ele envia um arquivo para um item da lista da
   convocação pelo endereço do envio, **Then** o envio é recusado como o de item inexistente, e nada
   é gravado.
5. **Given** K-pub com o Requerimento de Matrícula pedido *na convocação*, **When** ele abre o
   Requerimento, **Then** o Requerimento está como para quem não foi convocado, e o envio dele é
   recusado.
6. **Given** K-pub, **When** a comissão registra a publicação, **Then** na leitura seguinte a lista, o
   acompanhamento e a tela mostram a mesma convocação, com o prazo correndo e *"Publicada em
   ‹referência›"*.
7. **Given** uma convocação por mensagem cujo envio falhou (K-msg), **When** o convocado abre a
   convocação, **Then** a tela é a de hoje: *"Você foi convocado!"*, o prazo não iniciado e o envio de
   documentos aberto.

---

### User Story 2 — Quem digita sabe que o candidato vai ler, e vê como (Priority: P1)

O operador que convoca, corrige ou registra desfecho lê, em cada campo de texto livre que chega ao
candidato, que o texto será mostrado a ele. Antes de confirmar, vê o texto como o candidato o verá; no
lote, vê também quantas pessoas receberão o mesmo texto.

**Why this priority**: o texto livre é o único caminho por onde dado de terceiro chega ao portal de
alguém, e o lote o multiplica. O aviso e a prévia são o que a decisão pôs no lugar de tirar o texto.

**Independent Test**: em cada formulário com texto livre que chega ao candidato, achar o aviso, digitar
um texto, ver a prévia com o texto composto e, no lote, o número; confirmar e achar no portal o mesmo
texto da prévia.

**Acceptance Scenarios**:

1. **Given** o formulário *"Convocar os titulares"* de um recorte com quatro titulares, **When** o
   operador digita um complemento e pede a confirmação, **Then** a tela mostra, antes do botão que
   pratica o ato, o fundamento como o candidato o lerá — o derivado seguido do complemento — e diz que
   o mesmo texto será mostrado a **4** pessoas.
2. **Given** a prévia de um lote, **When** o operador confirma, **Then** cada um dos quatro convocados
   lê no portal exatamente o texto da prévia.
3. **Given** o formulário de desfecho de uma convocação, **When** o operador escreve o fundamento e
   pede a confirmação, **Then** a prévia mostra a linha que o candidato lerá, com o rótulo do desfecho
   e o fundamento, e diz que ela será mostrada a **1** pessoa.
4. **Given** a prévia de qualquer formulário, **When** o operador volta para corrigir o texto,
   **Then** o texto digitado e as escolhas do formulário continuam preenchidos.
5. **Given** o lote de não atendimento dos vencidos, **When** a lista de vencidos mudou entre a prévia
   e a confirmação, **Then** a confirmação é recusada como hoje, e nada é registrado.
6. **Given** qualquer formulário desses, **When** o operador o abre sem script no navegador, **Then** o
   aviso e a prévia aparecem do mesmo jeito.

---

### User Story 3 — A palavra da comunicação é a do canal (Priority: P2)

Na convocação por publicação, o portal e a gestão dizem *publicada* e citam a referência que a comissão
registrou. Na convocação por mensagem, dizem *enviada*, como hoje.

**Why this priority**: *"enviada"* afirma um fato que não houve. No portal, ensina o candidato a
procurar um e-mail que não existe. Na gestão, mistura dois gestos diferentes, publicar e enviar.

**Independent Test**: percorrer, nas duas formas, as telas do portal e da gestão que falam da
comunicação, e não achar *envio* na publicação nem *publicação* na mensagem.

**Acceptance Scenarios**:

1. **Given** uma convocação por publicação com publicação registrada, **When** o convocado abre a
   convocação ou o acompanhamento, **Then** os dados do ato dizem *"Publicada em ‹referência›"* e
   *"Vencimento registrado: ‹data›, contado da publicação"*, e nenhuma frase fala em envio da
   comunicação.
2. **Given** uma convocação por mensagem enviada, **When** o convocado abre as mesmas telas, **Then**
   elas dizem *"Comunicação enviada em ‹data›"* e *"contado do envio da comunicação"*, como hoje.
3. **Given** o registro da publicação na gestão, **When** ele é confirmado, **Then** a tela diz
   *"Publicação registrada"* e que o candidato já vê a convocação, e não *"Comunicação enviada"*.
4. **Given** a tela de condução de um recorte por publicação, **When** há convocação sem publicação
   registrada, **Then** a pastilha e a situação dela dizem que a publicação não foi registrada e que o
   candidato ainda não a vê.

---

### Edge Cases

Cada caso abaixo é requisito, e entra na verificação como os `FR-`.

- **Correção de convocação já publicada** (D-001). A comissão publicou A, o candidato a viu, e depois
  corrigiu A para B, que aguarda publicação própria. B continua visível: a cadeia já foi comunicada.
  O prazo de B não começou, e a frase é a do canal de B (FR-3999). A escrita continua como hoje para
  o prazo não iniciado.
- **Correção de convocação nunca publicada.** A, sem registro, corrigida para B, também sem registro:
  nenhuma das duas aparece até o registro de B.
- **Forma trocada por Retificação entre A e B.** A, por mensagem, enviada; B, por publicação, pendente.
  B aparece, porque a cadeia já foi comunicada (D-001), e a frase do prazo é a de publicação.
- **Forma não declarada.** O Perfil não declarou forma, e a convocação não pode ser comunicada. Ela se
  comporta como hoje, visível, porque a 1ª decisão alcança só a publicação.
- **Desfecho registrado antes do registro da publicação** (D-002). A desistência dita por telefone, por
  exemplo. A convocação e o desfecho continuam invisíveis até o registro. O não atendimento não chega
  aqui: ele já exige comunicação bem-sucedida.
- **Arquivo enviado antes desta feature.** Na instalação pode haver convocação por publicação sem
  registro com arquivo já apresentado pelo candidato. Nada se apaga: o arquivo continua na gestão e
  na conferência. O candidato volta a vê-lo quando a publicação for registrada.
- **Duas inscrições da mesma pessoa, uma com K-pub e outra com convocação visível.** Cada item da lista
  segue a própria convocação. A K-pub não aparece por estar ao lado de uma visível.
- **O recorte só tem convocações sem publicação registrada.** A tela da convocação de qualquer inscrição
  do recorte não diz que o certame chegou a convocar ali (FR-3984).
- **Complemento vazio.** Não há texto digitado. O formulário confirma direto, como hoje (D-004). O
  fundamento derivado que o candidato lerá já está na tela, sob o rótulo *"O candidato lerá este
  fundamento"*.
- **Fundamento do indeferimento pré-preenchido** pelas pendências de documento. O texto foi composto
  pelo sistema, mas o operador pode editá-lo: o aviso e a prévia valem como para o fundamento digitado.
- **Lote de uma pessoa.** A prévia diz *"1 pessoa"*, sem plural, e não omite o número.
- **Texto longo, ou com quebra de linha.** A prévia o mostra como o portal o mostrará, com as mesmas
  quebras e sem truncar.
- **Referência da publicação vazia em registro antigo.** O comando a exige desde a `019`. Se houver
  registro antigo sem ela, a tela diz *"Publicada"* sem a referência, e não inventa data.

## Requirements *(mandatory)*

### Functional Requirements

#### A. A convocação por publicação só aparece depois do registro

- **FR-3981**: Uma convocação MUST ser **visível ao candidato** quando a forma de comunicar que ela cita
  não for a publicação, **ou** quando alguma convocação da sua cadeia de correções — ela mesma ou uma
  anterior — tiver comunicação bem-sucedida registrada, em qualquer forma. Fora disso, a convocação é
  **invisível ao candidato** (1ª decisão, D-001). A forma é a que a convocação citou, e não a vigente,
  como a `019` já lê.
- **FR-3982**: O portal MUST tratar a convocação invisível como **ausente** em toda superfície: a lista
  (FR-1089 a FR-1091 da `059`, revistas), o acompanhamento (FR-1093 a FR-1095 da `059`, revistas), a
  tela da convocação e o endereço direto dela. A lista, o acompanhamento e a tela MUST continuar
  mostrando a **mesma** convocação, pela regra da FR-1100 da `059`, revista: a vigente mais recente
  entre as visíveis.
- **FR-3983**: Com a convocação invisível, a tela da convocação MUST ser a de quem não tem convocação, e
  MUST NOT registrar a leitura na trilha (FR-288b da `019`): não houve leitura de convocação.
- **FR-3984**: A pergunta *"o certame chegou a convocar neste recorte?"*, que separa *"não há
  convocação"* de *"você não foi chamado"* (US6 da `019`), MUST contar só convocações visíveis. Contar
  as invisíveis diria a todo inscrito do recorte que a convocação começou antes de publicada, e diria
  ao próprio convocado que ele não foi chamado.
- **FR-3985**: O envio de documento da convocação MUST ser recusado com a convocação invisível, no
  comando e não só na tela, com a mesma resposta dada ao item inexistente: a recusa MUST NOT revelar
  que a convocação existe. Ver o arquivo já apresentado segue a mesma regra.
- **FR-3986**: O Requerimento de Matrícula declarado *na convocação* MUST tratar a convocação invisível
  como inexistente: a página dele e o chamado da lista e do acompanhamento MUST ser os de quem não foi
  convocado, e o envio MUST ser recusado no comando (D-003).
- **FR-3987**: Registrada a publicação, a convocação MUST aparecer na leitura seguinte de todas as
  superfícies da FR-3982, sem passo adicional. Nenhuma superfície do portal MUST guardar cópia do
  estado de visibilidade.
- **FR-3988**: Na convocação por mensagem, o comportamento MUST NOT mudar: o estado *"convocado, prazo
  não iniciado"* continua visível, com o envio de documentos aberto (FR-269a e US6 da `019`, FR-3749 da
  `118` revista, cenário K da `121` revisto).
- **FR-3989**: A gestão MUST continuar vendo toda convocação, visível ou não, e MUST dizer, na
  convocação por publicação sem registro, que **o candidato ainda não a vê** (FR-4000).
- **FR-3990**: Decidir a visibilidade MUST NOT aumentar o custo de leitura com o número de inscrições
  na lista nem com o número de convocações (FR-1092 da `059`; o número fixo de consultas da `118`). A
  consulta extra, se houver, só se paga quando há convocação sem comunicação bem-sucedida.

#### B. O texto digitado que chega ao candidato

- **FR-3991**: Todo campo de texto livre cujo conteúdo chega ao candidato MUST dizer, junto do rótulo,
  *"Este texto será mostrado ao candidato."*, e MUST estar ligado a essa frase para quem usa leitor de
  tela. São os campos de: complemento do fundamento na convocação dos titulares, na convocação
  individual, na convocação para regularizar e na correção da convocação; complemento do fundamento no
  não atendimento dos vencidos; fundamento do desfecho; fundamento do indeferimento pelas pendências.
- **FR-3992**: O aviso MUST NOT ficar só na ajuda dos leitores de tela, nem dentro de bloco recolhível:
  ele é visível ao lado do campo, sempre. É aviso de consequência, e não ajuda de preenchimento.
- **FR-3993**: Com texto digitado em algum desses campos, o formulário MUST mostrar, **antes** do botão
  que pratica o ato, a **prévia** do texto como o candidato o verá: na convocação, o fundamento composto
  — o derivado seguido do complemento —, sob o rótulo *"Fundamento"*; no desfecho, a linha
  *"‹rótulo do desfecho›: ‹fundamento›"*, como a tela da convocação a mostra. A prévia MUST usar a
  mesma composição que o ato gravará, e não uma segunda.
- **FR-3994**: A prévia MUST dizer a **quantas pessoas** o mesmo texto será mostrado: *"Este texto será
  mostrado a N pessoas."*, com N igual ao número de convocações ou desfechos que a confirmação
  praticará. Com uma pessoa, *"Este texto será mostrado a 1 pessoa."*
- **FR-3995**: A prévia MUST funcionar sem script (a CSP da `091` e da `092`), e MUST preservar o que o
  operador preencheu ao voltar para corrigir.
- **FR-3996**: A confirmação a partir da prévia MUST manter as garantias de hoje: a chave de
  idempotência, a assinatura do alcance do lote e a recusa quando o alcance mudou. A prévia em si MUST
  NOT praticar ato nem gravar nada.
- **FR-3997**: Na correção da convocação, a prévia de texto MUST entrar na prévia que a `120` já mostra
  (FR-3844 da `120`), e MUST NOT criar um segundo passo.

#### C. A palavra da comunicação é a do canal

- **FR-3998**: Na convocação por publicação, o portal MUST dizer **"Publicada em ‹referência›"** onde hoje
  diz *"Comunicação enviada em ‹data›"*, e **"contado da publicação"** onde hoje diz *"contado do envio
  da comunicação"*. A referência é a que a comissão registrou. O instante do registro MUST NOT
  aparecer como data da publicação.
- **FR-3999**: Com o prazo não iniciado, a frase MUST ser a do canal da convocação: na mensagem, a de
  hoje — *"O prazo ainda não começou a correr: ele conta a partir do envio da comunicação."* —; na
  publicação, *"O prazo ainda não começou a correr: ele conta a partir da publicação da convocação."*
  (FR-3749 da `118`, revista). Pela FR-3981, a segunda só aparece na correção de convocação já
  comunicada.
- **FR-4000**: Na gestão, a convocação por publicação MUST usar o vocabulário da publicação: a
  confirmação do registro diz *"Publicação registrada"*, com a referência, que o prazo corre a partir
  dele e que o candidato já vê a convocação; o cartão da chamada diz *"Publicação registrada em
  ‹instante› — ‹referência›"*, e não *"Enviada em"*; o vencimento, *"contado do registro da
  publicação"*; a pastilha e a situação do prazo não iniciado, *"Publicação não registrada"* e que o
  candidato ainda não vê a convocação; a seção das comunicações pendentes, publicação a registrar, e
  não comunicação que *"ainda não saiu"*; o botão de emitir, *"Registrar a publicação"*; e a convocação
  individual MUST NOT dizer *"A comunicação sai no mesmo ato"* quando a forma é a publicação, porque
  na publicação ela não sai.
- **FR-4001**: As recusas dos comandos que falam da comunicação — o não atendimento antes do envio, o
  vencimento anterior ao envio e as demais que o plano inventaria — MUST dizer o canal da convocação
  recusada.
- **FR-4002**: Na convocação por mensagem, nenhuma frase MUST mudar, salvo uma: a linha *"Convocação
  substituída"* da convocação anterior comunicada por mensagem diz *"Enviada em ‹data›"*, e não
  *"Comunicada em ‹data›"* (FR-3869 da `121`, revista; D-008).
- **FR-4003**: Nenhuma superfície MUST afirmar que a publicação foi lida ou vista pelo candidato
  (FR-288a da `019`, revista): o que o sistema sabe é que a comissão registrou onde e quando publicou.
- **FR-4004**: A palavra MUST sair de uma fonte só por canal, e o teste de vocabulário MUST varrer as
  telas afetadas nas duas formas: *envio* da comunicação na publicação, e *publicação* na mensagem,
  reprovam.

#### D. Limites

- **FR-4005**: Esta feature MUST NOT mudar quando o prazo começa, a regra de visibilidade da mensagem
  individual, os modelos de e-mail da convocação, a autorização de nenhum ato, nem os avisos aos
  candidatos da `066`, que já exigem a publicação registrada.
- **FR-4006**: Esta feature MUST NOT criar tabela, coluna nem situação de comunicação nova, e MUST NOT
  apagar nem alterar registro existente.

### Key Entities

- **Convocação** (`019`): o ato. Ganha uma propriedade **derivada**, e não guardada: *visível ao
  candidato*, pela FR-3981.
- **Comunicação emitida** (`019`): o registro de cada tentativa de comunicar, com forma, resultado,
  instante e, na publicação, a referência. A publicação é registrada com resultado *"enviada"*, e é
  por isso que as telas liam *envio*: o registro não muda, muda a leitura.
- **Desfecho** (`019`): o fundamento dele é texto livre que chega ao candidato.
- **Prévia do texto**: o que o operador vê antes de confirmar. Não é registro: não grava nada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1201**: Em K-pub, **nenhuma** das sete superfícies do portal — lista, acompanhamento, tela da
  convocação, endereço direto, envio de documento, arquivo apresentado e Requerimento da chamada —
  revela a convocação, e o envio de documento e o do Requerimento gravam **zero** registros.
- **SC-1202**: Registrada a publicação, as sete superfícies passam a mostrar a convocação **na leitura
  seguinte**, sem outro gesto.
- **SC-1203**: Em K-msg, a tela da convocação, a lista e o acompanhamento são **idênticos** aos de hoje,
  linha por linha.
- **SC-1204**: O número de consultas da lista e do acompanhamento **não cresce** com o número de
  inscrições nem de convocações, com e sem convocação invisível.
- **SC-1205**: **Todos** os sete campos da FR-3991 trazem o aviso visível, e nenhum outro campo da
  convocação o traz sem chegar ao candidato.
- **SC-1206**: Em **100%** das confirmações com texto digitado, o operador vê a prévia antes do botão
  que pratica o ato, e o texto que o candidato lê no portal é **idêntico** ao da prévia.
- **SC-1207**: Em todo lote, o número da prévia é **igual** ao número de atos praticados.
- **SC-1208**: Nas telas da convocação por publicação, do portal e da gestão, **zero** frases falam em
  envio da comunicação; nas da mensagem, **zero** falam em publicação.
- **SC-1209**: Um operador que lê pela primeira vez a tela de condução de um recorte por publicação,
  com convocações sem registro, consegue dizer **sem ajuda** que o candidato ainda não as vê.

## Assumptions

- A referência da publicação é texto livre da comissão, e já traz o endereço e a data (*"site do
  Cefor, 13/09/2026"*). A tela a mostra como foi registrada.
- O prazo, nas duas formas, continua começando no instante do registro da comunicação bem-sucedida. Na
  publicação, esse instante é o do registro, e não o da publicação no site: a frase *"contado da
  publicação"* fala do ato, e o vencimento continua explícito (FR-269 da `019`).
- O formulário de convocação sem complemento continua com um passo só (D-004).
- O Requerimento de Matrícula *na convocação* faz parte de *"todo o portal"* da 1ª decisão (D-003).

## Proteção de dados (LGPD)

- **A convocação invisível não se revela por diferença de resposta.** O endereço direto, o envio de
  documento e o Requerimento respondem como para a inscrição sem convocação (FR-3983, FR-3985,
  FR-3986), e a tela de qualquer inscrito do recorte não diz que a convocação começou (FR-3984).
- **O texto livre continua chegando ao candidato**, por decisão do usuário. O aviso e a prévia são a
  proteção: o operador sabe quem lê e quantos leem. O motivo da correção continua fora do portal
  (`120`).
- Nenhum dado pessoal novo é coletado, guardado ou exibido.

## Compatibilidade com regras anteriores

| Regra | O que acontece |
|---|---|
| FR-269, FR-269a, FR-269b, FR-287, FR-288, FR-288b da `019` | continuam |
| US6 da `019`, cenário 1 | **revisto**: a convocação por publicação só aparece depois do registro |
| FR-288a da `019` | **revista**: o que o sistema sabe depende do canal |
| FR-1089, FR-1093, FR-1094 e FR-1100 da `059` | **revistas**: valem para a convocação visível |
| FR-1091, FR-1092, FR-1095 da `059` | continuam, e passam a alcançar a convocação invisível como ausente |
| FR-3749 da `118` | **revista**: a frase do prazo não iniciado segue o canal |
| Cenário K da `121` | **revisto**: vale para a mensagem e para a correção de convocação já comunicada |
| FR-3869 da `121` | **revista** só na mensagem: *"Enviada em"* no lugar de *"Comunicada em"* (D-008); o *"Publicada em"* vira o padrão das demais linhas |
| FR-3844 da `120` | continua; a prévia de texto entra na prévia que ela já mostra (FR-3997) |
| Avisos da `066` | continuam: o aviso de chamada já exige a publicação registrada |

## Revisões de requisitos anteriores

As redações abaixo **já estão aplicadas** aos arquivos das specs revistas, neste mesmo PR, com a marca
*"revista pela `125` em 2026-11-06"* e a redação anterior preservada ao fim da alínea, como a `121`
fez. Elas vigoram com a implementação desta spec.

### `019` — a convocação

**User Story 6, cenário 1, nova redação.** *Given* uma convocação vigente **visível ao candidato** — na
publicação, só depois do registro dela (FR-3981 da `125`) —, *When* o candidato abre sua área, *Then*
vê a chamada, o que fazer e o prazo, sem depender de e-mail.

> *Redação anterior:* "**Given** uma convocação vigente, **When** o candidato abre sua área, **Then**
> vê a chamada, o que fazer e o prazo, sem depender de e-mail."
>
> *Por que mudou:* na publicação, quem convoca é a publicação, e o portal anunciava o ato antes dela
> (1ª decisão).

**FR-288a, nova redação.** Nenhuma superfície MUST afirmar que a comunicação foi recebida, lida ou
entregue. O que o sistema sabe, e o que a tela diz, depende do canal: na mensagem, que **enviou**; na
publicação, que a comissão **registrou** onde e quando publicou (FR-3998 a FR-4004 da `125`).

> *Redação anterior:* "Nenhuma superfície MUST afirmar que a comunicação foi recebida, lida ou
> entregue: o que o sistema sabe é que **enviou**."
>
> *Por que mudou:* na publicação, o sistema não envia, e a tela dizia *"Comunicação enviada"* (3ª
> decisão).

**A terceira consequência da decisão sobre a comunicação** (o estado *"convocado, prazo não
iniciado"*) não é reescrita: decisão registrada não se reescreve. Uma nota ao lado dela diz que, desde
a `125`, o estado continua legível na gestão nas duas formas, e no portal só na mensagem e na correção
de convocação já comunicada.

### `059` — o acesso à convocação

**FR-1089, nova redação.** Item de inscrição com convocação **em aberto** — vigente, sem desfecho e
visível ao candidato (FR-3981 da `125`), em qualquer dos estados de prazo — MUST dizer, por texto e por
símbolo, que há convocação aberta.

**FR-1093, nova redação.** Inscrição com convocação vigente **visível ao candidato** — aberta ou
concluída — MUST ter, no acompanhamento, uma seção "Convocação" com a espécie, o prazo quando houver, a
situação e o caminho "Ver convocação".

**FR-1094, nova redação.** A situação MUST distinguir quatro casos, nos termos que a tela da
convocação já usa e no vocabulário do canal (FR-3998 da `125`): comunicação ainda não enviada — ou,
na correção de convocação publicada, publicação da correção ainda não registrada —; prazo correndo;
prazo informado decorrido sem registro; desfecho registrado, com a espécie dele.

**FR-1100, nova redação.** Lista, acompanhamento e tela da convocação MUST apresentar a **mesma**
convocação de uma inscrição: a vigente mais recente **entre as visíveis ao candidato** (FR-3981 da
`125`).

> As redações anteriores ficam preservadas ao fim de cada alínea, no arquivo da `059`. *Por que
> mudaram:* a 1ª decisão.

### `118` — a jornada consolidada do convocado

**FR-3749, nova redação.** Com a comunicação ainda não bem-sucedida, as telas MUST dizer a frase do
canal da convocação — na mensagem, *"O prazo ainda não começou a correr: ele conta a partir do envio
da comunicação."*; na publicação, *"O prazo ainda não começou a correr: ele conta a partir da
publicação da convocação."* (FR-3999 da `125`) —, seguida de *"Você já pode enviar."* **só** quando a
escrita estiver aberta e houver tarefa ou opcional a enviar. Esta regra **prevalece** sobre toda menção
ao prazo: a data do vencimento MUST NOT aparecer como prazo em nenhum bloco, cartão, opcional ou frase
de conclusão; ela fica só no bloco *Sobre esta convocação*.

> *Redação anterior:* "Com a comunicação ainda não enviada, as telas MUST dizer *"O prazo ainda não
> começou a correr: ele conta a partir do envio da comunicação."*, seguido de *"Você já pode
> enviar."* [...]" — o resto, igual.
>
> *Por que mudou:* a 3ª decisão. Na publicação, a frase falava de um envio que não há.

### `121` — a experiência da convocação

**FR-3869, alínea *comunicada*, nova redação** (D-008): *"Enviada em ‹data›, às ‹hora›, com prazo até
‹data›, às ‹hora›. Esse prazo não vale mais."* As demais alíneas e o resto do requisito não mudam.

> *Redação anterior:* *"Comunicada em ‹data›, às ‹hora›, com prazo até ‹data›, às ‹hora›. Esse prazo
> não vale mais."*

**Cenário K, nova redação** (caso-limite *"Prazo não iniciado"*). O título é *"Você foi convocado!"*;
o cartão do prazo diz só a frase da FR-3749 da `118`, revista pela `125`, no canal da convocação, sem
data, sem dia da semana e sem contagem; a consequência não aparece (FR-1177 da `063`). Na mensagem, o
e-mail não existe ainda: ele é o que inicia o prazo. Na publicação, o cenário só existe na correção de
convocação já comunicada: antes do registro da primeira publicação, a convocação não aparece no portal
(FR-3981 da `125`).

> *Redação anterior:* a mesma, sem as duas últimas frases e com *"O e-mail não existe ainda: ele é o
> que inicia o prazo."* valendo para as duas formas.

## Decisões

**Estado em 2026-11-06.** D-001 a D-008 foram propostas por esta spec e **aceitas pelo usuário em 2026-11-06**, as oito, sem alteração.

### D-001 — A cadeia de correções já comunicada continua visível

A 1ª decisão diz que a convocação por publicação só aparece depois do registro da publicação. Na
correção, a `120` faz nascer uma sucessora que aguarda **publicação própria** (FR-3844 da `120`). Lida
ao pé da letra, a regra faria sumir do portal, no dia da correção, uma convocação que o candidato já
via, com documentos já enviados, até a comissão publicar a correção.

**Proposta:** a visibilidade é da cadeia. Se alguma convocação da cadeia teve comunicação
bem-sucedida, em qualquer forma, a vigente continua visível, com o prazo não iniciado na frase do
canal dela e a escrita como hoje. Se nenhuma teve, nenhuma aparece. A alternativa — a sucessora some
até a própria publicação — é a leitura literal, e custa ao candidato o caminho para a própria
convocação no meio do prazo.

### D-002 — Desfecho anterior à publicação não torna a convocação visível

A desistência expressa, o indeferimento ou o aceite registrados pela gestão antes do registro da
publicação são fatos da pessoa, e mostrá-los não anuncia nada ao mundo. Mas mostrá-los é mostrar a
convocação, e a 1ª decisão não tem exceção.

**Proposta:** seguir a regra sem exceção. A convocação e o desfecho aparecem juntos, quando a
publicação for registrada. O caso é raro: o não atendimento, o desfecho mais comum sem resposta da
pessoa, já exige comunicação bem-sucedida.

### D-003 — O Requerimento de Matrícula da chamada segue a convocação

A 1ª decisão enumera o acompanhamento, a lista, a tela, o endereço direto e o envio de documentos, e
diz que a regra vale para *"todo o portal"*. O Requerimento declarado *na convocação* abre com a
chamada em aberto, e a página dele diria *"preencher"* a quem a convocação ainda não aparece.

**Proposta:** ler *"todo o portal"* como incluindo o Requerimento da chamada: a página, o chamado e o
envio tratam a convocação invisível como inexistente (FR-3986). O Requerimento declarado *na
inscrição* não depende de convocação, e não muda.

### D-004 — A prévia é um passo do servidor, e só quando há texto digitado

A CSP recusa script escrito no template, e a prévia precisa funcionar sem script (FR-3995). Uma prévia
ao vivo, por arquivo de script, seria complemento, e não substituto.

**Proposta:** com texto digitado, o primeiro clique leva a um passo *"Conferir o texto"*, renderizado
pelo servidor, com a prévia, o número de pessoas, os mesmos campos ocultos do formulário e o botão que
pratica o ato. Sem texto digitado — complemento vazio —, o formulário confirma direto, como hoje: o
fundamento derivado já está na tela, e passa a ser rotulado *"O candidato lerá este fundamento"*. O
fundamento do desfecho é obrigatório, e por isso o desfecho sempre passa pelo passo. Na correção, a
prévia de texto entra na prévia que a `120` já tem (FR-3997).

### D-005 — A data da publicação é a da referência, e não a do registro

O registro grava o instante em que a comissão o fez, que pode ser dias depois da publicação no site.
Mostrar esse instante como *"publicada em"* seria afirmar uma data que o sistema não conhece.

**Proposta:** no portal, *"Publicada em ‹referência›"*, como a `121` já faz na linha da substituída.
Na gestão, onde o instante do registro importa para conferir o prazo, *"Publicação registrada em
‹instante› — ‹referência›"*.

### D-006 — A frase do prazo não iniciado na publicação

A FR-3749 da `118` precisa de redação para a publicação, e ela só aparece na correção de convocação
já comunicada (D-001).

**Proposta:** *"O prazo ainda não começou a correr: ele conta a partir da publicação da convocação."*
— a mesma forma da frase da mensagem, trocado só o fato que inicia o prazo.

### D-007 — A gestão diz que o candidato ainda não vê

Com a 1ª decisão, *"registrar a publicação"* deixa de ser só o início do prazo e passa a ser o gesto
que mostra a convocação ao candidato. Sem dizer isso, o operador pode esperar que o candidato já esteja
vendo e respondendo.

**Proposta:** a pastilha, a situação e a seção das pendentes, na convocação por publicação sem
registro, dizem que o candidato ainda não a vê; a confirmação do registro diz que agora ele vê
(FR-4000).

### D-008 — Na mensagem, "Enviada", e não "Comunicada"

A `121` escreveu a linha da convocação substituída com *"Comunicada em ‹data›"* para a mensagem e
*"Publicada em ‹referência›"* para a publicação. A 3ª decisão pede *enviada* na mensagem.

**Proposta:** *"Enviada em ‹data›, às ‹hora›, com prazo até [...]"*, revendo a FR-3869 da `121` só nessa
alínea. A alternativa é manter *"Comunicada"*, que não é falsa, e aceitar duas palavras para o mesmo
canal no portal.

## Registrado, sem desenvolver

- **O motivo da conferência de documento chega ao candidato** — *"Precisa de correção: ‹motivo›"*,
  *"Não se aplica: ‹motivo›"* —, e é texto livre do operador. A 2ª decisão nomeou o complemento e o
  fundamento do desfecho. Estender o aviso e a prévia ao motivo da conferência é pergunta ao usuário.
- **Outros textos livres que chegam ao candidato fora da convocação**, como o motivo de admissibilidade
  do recurso e o motivo do resultado de etapa no acompanhamento. Fora do escopo da 2ª decisão.
- **A `QI-7` da `115`**, o aviso de pendência por e-mail, continua fora.
