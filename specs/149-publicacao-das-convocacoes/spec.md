# Feature Specification: A publicação das convocações no GPS

**Feature Branch**: `claude/gps-public-convocacoes-db0f9b`, sobre a `main` em `d3e98a89`

**Created**: 2026-11-11

**Status**: Em implementação. As decisões têm duas origens:

- **Do usuário, em 11/11/2026**, sobre quatro perguntas feitas depois do diagnóstico, todas na
  alternativa recomendada: a *1ª* a *4ª decisão*, abaixo. Não se reabrem.
- **Propostas de desenho desta spec:** D-001 a D-013, no [research](research.md). As dez primeiras
  respondem, na ordem, às dez perguntas de arquitetura do pedido.

**Input**: pedido do usuário de 11/11/2026, *"GPS — Spec: Publicação pública das convocações"*: a
comissão prepara e confere a chamada no GPS, publica a lista em outro site e volta ao GPS para
registrar onde publicou. O pedido é publicar no próprio GPS quando ele for o veículo oficial admitido
pelo Edital, sem mudar a semântica das formas de comunicar da `019` e da `125`.

> **Faixa de identificadores.** Esta spec abre em **FR-5701** e **SC-1851**. **Nasceu como `148`,
> com FR a partir de 5401 e SC a partir de 1701**, medidos em 11/11/2026 sobre as worktrees desta
> máquina e os PRs abertos. No mesmo dia, a publicação e homologação das inscrições entrou na `main`
> (#469) também como `148`, com FR-5400 a 5438 e SC-1700 a 1708 — a mesma pasta e uma faixa
> sobreposta, que nenhuma das duas sessões via. Esta foi renumerada para a `149`, e cada identificador
> deslocado por um valor fixo (FR + 300, SC + 150), para não haver erro de transcrição. O teto, então,
> era o requisito cinco mil seiscentos e catorze e o critério mil oitocentos e cinco, da `150` (PR #471).
> **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-288 da `019`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número.

---

## Por que esta feature existe

**Na convocação por publicação, a comissão faz o mesmo ato duas vezes.** Ela convoca no GPS, confere
quem foi chamado, monta à mão a lista que o GPS já tem, publica a lista em outro site e volta ao GPS
para registrar *"onde e quando a lista foi publicada"* — o campo de texto livre que a `019` criou
porque o sistema não publicava (`R-007` da `019`, o comentário de `ComunicacaoEmitida`). O prazo de
cada convocado corre desse registro, e o candidato só vê a convocação depois dele (1ª decisão da
`125`). Entre a convocação e o registro podem passar dias.

**O GPS já sabe produzir ato público imutável.** A divulgação do resultado (`017`) tem página pública
de endereço estável, bytes canônicos congelados, documento PDF gerado uma vez, sucessão sem
reescrita, autoridade signatária e três tabelas append-only. A relação de habilitados do sorteio
(`021`) também. Falta a convocação.

**Mas publicar não é só mostrar uma lista.** Na forma *por publicação*, a publicação é o ato que
convoca: é dela que o prazo corre. Uma página que aparecesse por efeito colateral de uma prévia, ou
que pudesse ser regenerada a partir do estado de hoje, poria em dúvida o prazo de todo convocado.

### O que esta spec cobre, e o que fica fora

**Cobre:**

1. **O ato.** A comissão publica pelo GPS a relação das convocações de um Edital, num ato numerado
   por Edital que reúne um ou mais recortes. Para as convocações por publicação ainda não
   comunicadas, a publicação **é** o ato oficial de convocação: grava, na mesma transação, a
   comunicação de cada uma, e o prazo começa a correr. Para as já comunicadas — por mensagem
   individual, ou por publicação registrada fora do GPS —, a relação é **informativa**, e nenhum
   prazo muda.
2. **A página pública** de cada publicação, sem autenticação, e o documento PDF, ambos dos mesmos
   bytes congelados; e a seção *Convocações* na página pública da seleção.
3. **A gestão**: a página de publicação do Edital, com a prévia do que será público e o efeito da
   confirmação, e o caminho a partir da tela do recorte.
4. **A área do candidato**: a convocação publicada no GPS leva à página pública dela. As
   providências continuam só ali.

**Fica fora:**

- Notificação nova. Os avisos aos convocados de uma chamada publicada (`066`) já existem, e alcançam a
  publicação nativa pela referência que ela grava.
- Qualquer mudança no motor de convocação (`019`, `050`), na correção (`120`), na entrega documental
  (`115`, `117`), na classificação e na publicação das inscrições, que é outro ato.
- Declarar o veículo da publicação no conteúdo publicado do Edital (1ª decisão): a comissão declara
  no ato.
- Assinatura digital. A autoridade signatária é a da `060`, nome e cargo impressos.
- Listar, na página pública, as publicações feitas fora do GPS. A referência é texto livre da
  comissão, e publicá-la é decisão própria (registrada no fim).
- Retificar a publicação em si. A publicação é imutável; corrige-se a **convocação** (`120`), e a
  correção sai na publicação seguinte (D-006).

## Clarifications

### Session 2026-11-11 (decisões do usuário depois do diagnóstico)

- Q: Hoje o Edital declara só a forma da convocação por Perfil. Como o GPS sabe que a página pública
  dele é veículo oficial admitido? → A: **Declaração no ato.** Ao publicar, a comissão declara e cita
  o item do Edital que admite o GPS. Fica gravado no ato e na trilha. O conteúdo publicado do Edital
  não muda; sem a declaração, segue o registro externo de hoje. *(1ª decisão)*
- Q: Nas convocações por mensagem individual e por publicação externa já registrada, o GPS também
  deve poder divulgar a relação na página pública? → A: **Sim, no mesmo gesto.** A mesma publicação
  reúne os recortes e diz, em cada grupo, se é o ato oficial ou divulgação informativa, citando o
  envio ou a referência externa. Nenhuma comunicação nova, nenhum prazo mexido. *(2ª decisão)*
- Q: Quais dados de cada convocado vão para a página pública e o documento? → A: **Nome, protocolo,
  vaga e lista**, mais o vencimento. O mesmo que a divulgação do resultado e a relação do sorteio já
  publicam. Sem CPF, contato, fundamento digitado, espécie da convocação nem documentos. *(3ª
  decisão)*
- Q: O documento leva autoridade signatária escolhida no ato, como a divulgação do resultado? → A:
  **Sim, como o resultado**, pela autoridade habilitada da unidade (`060`). *(4ª decisão)*

## User Scenarios & Testing *(mandatory)*

Vocabulário desta spec: a **publicação de convocados** é o ato; cada pessoa nela tem efeito
**convoca** (a publicação é o ato oficial da convocação dela) ou **divulga** (a convocação já foi
comunicada por outro caminho, e a relação é informativa). A palavra *chamada* não nomeia a
publicação: no GPS ela já é a convocação de uma pessoa (D-011).

### User Story 1 — A comissão publica a convocação no GPS (Priority: P1)

A comissão convocou os titulares de dois recortes cujo Perfil declara a forma *por publicação*. Ela
abre a publicação das convocações do Edital, vê quantas pessoas, de quais vagas e listas, o que será
público e o efeito; escolhe a autoridade, declara o item do Edital que admite o GPS e confirma. O
GPS grava a 1ª publicação de convocados, o prazo de cada convocado começa a correr no mesmo instante,
e o candidato passa a ver a convocação.

**Why this priority**: é a descontinuidade que o pedido quer eliminar, e a única parte que mexe em
prazo.

**Independent Test**: convocar por publicação, publicar pela página do Edital e conferir a
comunicação gravada, o prazo em curso, a página pública e a convocação no portal.

**Acceptance Scenarios**:

1. **Given** quatro convocações por publicação sem comunicação, em dois recortes, **When** a comissão
   abre a publicação das convocações, **Then** a prévia mostra os dois grupos, as quatro pessoas com
   nome, protocolo, vaga, lista e vencimento, e diz que a confirmação inicia o prazo das quatro e as
   torna visíveis ao candidato.
2. **Given** a prévia, **When** a comissão confirma sem declarar o item do Edital que admite o GPS,
   **Then** a confirmação é recusada pedindo a declaração, e nada é gravado.
3. **Given** a prévia, **When** a comissão confirma com autoridade e declaração, **Then** existe a 1ª
   publicação de convocados do Edital, com o instante, a autoridade, quem publicou e as quatro
   pessoas; cada convocação tem comunicação *publicada* com o instante da publicação; o prazo está em
   curso; e cada candidato vê a convocação, com *"Publicada em"* levando à página pública.
4. **Given** a confirmação, **When** a comissão repete o envio do formulário (duplo clique, voltar e
   reenviar), **Then** o GPS devolve a mesma publicação e não grava outra.
5. **Given** a prévia aberta, **When** outra pessoa convoca mais alguém do recorte antes da
   confirmação, **Then** a confirmação é recusada porque o alcance mudou, e nada é gravado.

---

### User Story 2 — Qualquer pessoa consulta as convocações publicadas (Priority: P1)

Na página pública da seleção, sem entrar, qualquer pessoa vê a seção *Convocações*, com as
publicações da mais recente para a mais antiga, abre a relação de uma delas e baixa o documento.

**Why this priority**: é o que torna a publicação pública — e o que o Edital, quando admite o GPS,
promete ao candidato.

**Independent Test**: com duas publicações, abrir a página da seleção sem sessão, achar as duas na
ordem certa, abrir a relação e o PDF, e conferir que dizem o mesmo.

**Acceptance Scenarios**:

1. **Given** um Edital sem publicação de convocados, **When** alguém abre a página da seleção,
   **Then** não há seção *Convocações*.
2. **Given** um Edital com a 1ª e a 2ª publicação, **When** alguém abre a página da seleção sem
   sessão, **Then** a seção mostra a 2ª antes da 1ª, cada uma com data, natureza, quantas pessoas e
   vagas, e os caminhos para a relação e para o documento; e diz uma vez onde estão as providências
   individuais e que estar convocado não é ter a documentação aceita nem a matrícula concluída.
3. **Given** a relação de uma publicação, **When** alguém a abre sem sessão, **Then** vê o
   cabeçalho da unidade, o Edital, o número da publicação, a data e a hora, a autoridade, e as
   pessoas agrupadas por vaga e lista, com o prazo e as orientações gerais.
4. **Given** a relação, **When** alguém baixa o documento, **Then** o PDF tem as mesmas pessoas, o
   mesmo número, a mesma data e os mesmos prazos.
5. **Given** um celular de 375 px, **When** a seção e a relação abrem, **Then** nada exige rolagem
   horizontal.

---

### User Story 3 — A relação informativa não mexe no prazo (Priority: P2)

Num Edital cujo Perfil convoca por mensagem individual, a comissão divulga na página pública a
relação de quem já recebeu a mensagem. Num Perfil por publicação já registrada fora do GPS, divulga o
espelho da publicação externa. Em nenhum dos dois o prazo de alguém muda.

**Why this priority**: amplia a transparência sem tocar no ato oficial; é o caso de todo Edital que
não admite o GPS como veículo.

**Independent Test**: publicar com convocações já comunicadas e conferir que nenhuma comunicação nova
foi gravada e que o instante de onde o prazo corre é o mesmo.

**Acceptance Scenarios**:

1. **Given** convocações por mensagem enviada, **When** a comissão as publica, **Then** a relação diz
   que é informativa e que a convocação oficial foi feita por mensagem individual, e nenhuma
   comunicação nova é gravada.
2. **Given** convocações por publicação registrada fora do GPS, **When** a comissão as publica,
   **Then** a relação diz que é informativa e cita a referência registrada; o prazo continua contado
   do registro.
3. **Given** uma publicação só com efeito *divulga*, **When** a comissão confirma, **Then** a
   declaração do veículo não é pedida, porque a publicação não convoca ninguém.
4. **Given** uma convocação por mensagem cujo envio falhou, **When** a comissão abre a prévia,
   **Then** ela não aparece: a publicação não substitui o envio individual.

---

### User Story 4 — A correção depois da publicação (Priority: P2)

A comissão publicou a convocação de Ana na 1ª publicação. Depois corrigiu o vencimento dela (`120`).
A correção sai na 2ª publicação, marcada como correção da convocação divulgada na 1ª. A 1ª continua
como foi publicada, e diz que uma convocação dela foi corrigida depois.

**Why this priority**: é o caso que o pedido destaca, e o único em que o histórico e o vigente se
separam na página.

**Independent Test**: publicar, corrigir, publicar de novo, e conferir a 1ª (bytes do PDF iguais, aviso
na página), a 2ª (marca de correção) e o prazo de Ana (contado da 2ª).

**Acceptance Scenarios**:

1. **Given** a convocação de Ana publicada na 1ª e corrigida depois, **When** a comissão abre a prévia,
   **Then** a correção aparece marcada *"corrige a convocação divulgada na 1ª publicação"*, sem o
   motivo da correção.
2. **Given** a 2ª publicação confirmada, **When** alguém abre a 1ª, **Then** a página diz que uma
   convocação dela foi corrigida na 2ª, com o caminho para a 2ª; a linha de Ana diz o mesmo; e o PDF
   da 1ª tem os mesmos bytes de antes.
3. **Given** a 2ª publicação, **When** Ana abre a convocação no portal, **Then** o vencimento é o da
   correção, e *"Publicada em"* leva à 2ª.

---

### User Story 5 — A comissão parte do recorte (Priority: P3)

Na tela de convocação de um recorte por publicação, a seção das comunicações pendentes oferece
publicar no GPS, e mantém o registro da publicação feita fora como alternativa nomeada.

**Why this priority**: é onde a comissão já está quando acaba de convocar.

**Independent Test**: da tela do recorte, seguir *"Publicar no GPS"* e chegar à prévia com aquele
recorte; e registrar uma publicação externa pelo formulário de sempre.

**Acceptance Scenarios**:

1. **Given** convocações pendentes por publicação num recorte, **When** a comissão abre a tela do
   recorte, **Then** a seção oferece *"Publicar no GPS"* e, à parte, *"Publicada fora do GPS?"* com o
   formulário da referência.
2. **Given** uma convocação publicada no GPS, **When** a comissão abre o cartão dela, **Then** ele diz
   em qual publicação ela saiu, com o caminho para a página pública.

---

### Edge Cases

Cada caso abaixo é requisito, e entra na verificação como os `FR-`.

- **Vencimento anterior ao instante da publicação.** A convocação fica fora da prévia, com o motivo
  e o caminho para corrigi-la; publicá-la iniciaria um prazo já vencido (a FR-269b da `019`).
- **Emissão em estado indeterminado.** Fica fora, com o motivo, como no gesto das pendentes.
- **Forma não declarada.** A convocação não pode ser comunicada, e não entra como *convoca*; sem
  comunicação, também não entra como *divulga*.
- **Recorte com pendentes das duas formas** (Retificação no meio). Só as por publicação entram como
  *convoca*; as por mensagem pendentes ficam fora, com o motivo: o envio delas é outro gesto.
- **Convocação com desfecho registrado.** Como *convoca*, fica fora (a mensagem diria *"você foi
  convocada"* a quem já respondeu). Já comunicada, entra como *divulga*: o desfecho não é público, e
  a relação diz quem foi convocado, e não o que respondeu.
- **Convocação sucedida (corrigida) antes de publicar.** Só a vigente entra.
- **Correção de convocação nunca publicada no GPS.** Entra sem marca de correção: não há publicação
  anterior a corrigir.
- **Mesma pessoa em dois recortes.** Aparece nos dois grupos, uma linha por convocação.
- **Sem vencimento** (o Edital não publica prazo). A linha e o grupo dizem que o prazo é o do Edital,
  sem inventar data.
- **Vencimentos diferentes num mesmo grupo.** O prazo vai na linha de cada pessoa, e não no grupo.
- **Nada a publicar.** A página de publicação diz isso, e não oferece confirmação.
- **Nenhuma autoridade vigente na unidade.** A confirmação é recusada como na divulgação do resultado.
- **Edital cancelado ou Processo encerrado.** A publicação feita continua consultável; publicar de
  novo segue o que o comando da comissão já recusa para o certame encerrado.
- **Duas abas, chaves diferentes, mesmo alcance.** A segunda confirmação encontra o alcance mudado (as
  pessoas já foram publicadas) e é recusada; o banco recusa por constraint o que passar.
- **Publicação anterior a esta feature** (registro externo). Continua como está; a convocação pode
  entrar numa publicação do GPS como *divulga*.

## Requirements *(mandatory)*

### Functional Requirements

#### A. O ato

- **FR-5701**: A comissão MUST poder publicar pelo GPS a relação das convocações de um Edital, num
  **ato único**, a *publicação de convocados*, numerado por Edital (1ª, 2ª, …) na ordem das
  confirmações, que reúne as convocações dos recortes escolhidos.
- **FR-5702**: Uma convocação vigente, sem desfecho, que cita a forma *por publicação* e não tem
  comunicação bem-sucedida MUST entrar com efeito **convoca**: a confirmação MUST gravar, **na mesma
  transação** do ato, a comunicação dela — forma publicação, resultado *enviada*, instante igual ao
  da publicação, e referência que identifica a publicação no GPS. O prazo MUST correr desse instante,
  como corre do registro externo (a FR-288 da `019`), e a convocação MUST ficar visível ao candidato
  pela regra da FR-3981 da `125`, sem regra nova.
- **FR-5703**: Uma publicação com efeito *convoca* MUST exigir a **declaração do veículo**: o texto em
  que a comissão diz onde o Edital admite a página pública do GPS como veículo da convocação (por
  exemplo, *"item 7.2 do Edital"*). Sem ela, a confirmação MUST ser recusada (`veiculo_nao_declarado`)
  sem gravar nada. A declaração MUST ser gravada no ato e na trilha, e MUST NOT ser pedida nem gravada
  quando nenhuma pessoa tiver efeito *convoca* (1ª decisão).
- **FR-5704**: MUST NOT entrar como *convoca* a convocação: com desfecho; com emissão em estado
  indeterminado; cuja forma citada não seja a publicação; ou cujo vencimento preceda o instante da
  publicação. A prévia MUST dizer quantas ficaram fora e por quê, com o caminho de cada correção.
- **FR-5705**: Uma convocação vigente com comunicação bem-sucedida, em qualquer forma, ainda não
  divulgada por publicação do GPS, MAY entrar com efeito **divulga**: nenhuma comunicação é gravada e
  nenhum instante de prazo muda. A página e o documento MUST dizer, no grupo, que a relação é
  informativa e como a convocação oficial foi feita — *"por mensagem individual"* ou *"publicada em
  ‹referência registrada›"* (2ª decisão).
- **FR-5706**: Uma convocação sem comunicação bem-sucedida cuja forma não seja a publicação — a
  mensagem que falhou ou ainda não saiu — MUST NOT entrar com efeito nenhum: a publicação não
  substitui o envio individual.
- **FR-5707**: Cada convocação MUST aparecer em **no máximo uma** publicação de convocados, garantido
  pelo banco. A repetição com a mesma chave MUST devolver o ato original sem gravar outro; uma
  segunda confirmação com outra chave MUST ser recusada antes da gravação.
- **FR-5708**: A confirmação MUST carregar a assinatura do alcance da prévia — quem entra, com que
  efeito, e a comunicação citada no *divulga* — e MUST ser recusada sem gravar nada
  (`publicacao_previa_obsoleta`) quando o alcance de agora for outro. Abrir a página de publicação,
  mudar a escolha de recortes ou ver a prévia MUST NOT gravar nada.
- **FR-5709**: O ato MUST levar a autoridade signatária escolhida, habilitada na unidade do Edital e
  vigente na data do ato, conferida pela mesma regra da divulgação do resultado (a FR-1125 da `060`);
  nome, cargo e ato de nomeação MUST ficar congelados no ato (4ª decisão).
- **FR-5710**: O ato MUST registrar o número, o instante, quem publicou, a declaração do veículo, a
  unidade como estava no dia, o **conteúdo público congelado** (bytes canônicos e o resumo deles) e o
  vínculo com cada convocação publicada, o efeito dela e a comunicação que a convocou. O documento PDF
  MUST ser gerado uma vez, na confirmação, a partir dos mesmos bytes. As três tabelas MUST ser
  append-only nas três camadas (aplicação, gatilho e privilégio ausente).
- **FR-5711**: A trilha MUST registrar o ato (número, quantas pessoas com cada efeito, a declaração do
  veículo) e, para cada comunicação gravada, o registro da publicação dela, na frase da publicação
  registrada da `125`.

#### B. O que é público

- **FR-5712**: Por pessoa, o conteúdo público MUST ter **só**: nome, protocolo da inscrição, vaga
  (Perfil), lista de concorrência nomeada — inclusive a ampla — e o vencimento registrado. MUST NOT
  ter CPF, inteiro ou parcial, endereço eletrônico, telefone, endereço, data de nascimento, arquivo
  ou documento, fundamento digitado, espécie da convocação, motivo de correção, desfecho ou situação
  documental (3ª decisão). A página e o documento MUST ler os mesmos campos.
- **FR-5713**: O cabeçalho MUST identificar a unidade (o cabeçalho do ato, como estava no dia), o
  Edital por número e ano, o título do Processo, o número da publicação, a data e a hora, e a
  autoridade signatária.
- **FR-5714**: As pessoas MUST vir agrupadas por vaga e, dentro dela, por lista, na ordem em que o
  Edital publicado declara vagas e listas; dentro do grupo, na ordem em que foram convocadas, com o
  protocolo desempatando. *(Explicitada em 12/11/2026, depois da demonstração no cenário C10.)* As
  convocadas num mesmo gesto nascem no mesmo instante, e a ordem entre elas é a da fila — a posição
  na classificação que a convocação citou —, antes do protocolo.
- **FR-5715**: O vencimento MUST ser dito uma vez no grupo quando for o mesmo para todos, e na linha de
  cada pessoa quando não for. Sem vencimento, MUST dizer que o prazo é o estabelecido no Edital, sem
  data.
- **FR-5716**: As orientações gerais MUST ser texto do sistema, ditas uma vez por publicação, e não
  texto livre da comissão: as providências — documentos, envio e acompanhamento — estão na Área do
  candidato; estar na relação não significa documentação aceita nem matrícula concluída; e, quando o
  Edital pede o Requerimento de Matrícula na convocação, que ele também está lá.
- **FR-5717**: A convocação que corrige outra já divulgada numa publicação anterior MUST vir marcada
  *"corrige a convocação divulgada na ‹N›ª publicação"*, sem o motivo da correção.

#### C. A página pública

- **FR-5718**: Cada publicação MUST ter página pública, sem autenticação, em endereço estável pela
  identidade do ato, e o documento PDF num endereço irmão, entregue como arquivo, com o resumo dos
  bytes como `ETag`.
- **FR-5719**: A página MUST ler o conteúdo do ato dos bytes congelados, e MUST NOT recompô-lo a partir
  do estado atual das convocações, inscrições ou do Edital.
- **FR-5720**: Quando uma convocação da publicação tiver sido corrigida por convocação divulgada numa
  publicação posterior, a página MUST dizer isso no topo e na linha, com o caminho para a posterior.
  É leitura da cadeia, fora do ato: o documento PDF não muda.
- **FR-5721**: A página pública da seleção MUST ter a seção **Convocações** quando houver publicação de
  convocados, depois dos *Resultados divulgados*, com as publicações da mais recente para a mais
  antiga. Cada uma MUST dizer: o número, a data, a natureza — *"Convocação oficial"*, *"Divulgação
  informativa"* ou as duas —, quantas pessoas, as vagas, o prazo quando for um só, se traz correção, e
  os caminhos para a relação e para o documento. As três mais recentes MUST ficar à vista; as
  anteriores, recolhidas em *"Publicações anteriores (N)"*.
- **FR-5722**: A seção MUST dizer **uma vez**, e não em cada publicação, onde estão as providências
  individuais (a Área do candidato, com o caminho) e que estar convocado não é ter a documentação
  aceita nem a matrícula concluída.
- **FR-5723**: Sem publicação de convocados, a seção MUST NOT aparecer.
- **FR-5724**: A seção e a página da publicação MUST funcionar sem script, sob a CSP da `091` e da
  `092`, sem tabela, e em 375 px sem rolagem horizontal; e MUST NOT ficar mais estreitas que o
  conteúdo pede em telas largas, nem esticar linhas de texto além da medida legível.

#### D. A área do candidato

- **FR-5725**: Na convocação publicada no GPS, o *"Publicada em ‹referência›"* da área do candidato
  MUST levar à página pública da publicação. A convocação, os documentos, o Requerimento e o
  acompanhamento continuam ali, como hoje.
- **FR-5726**: Os textos da área do candidato e da página pública MUST concordar: a mesma data da
  publicação, o mesmo vencimento e o mesmo número da publicação.

#### E. A gestão

- **FR-5727**: A gestão MUST ter, por Edital, a página **Publicação das convocações**, com: as
  publicações feitas (número, data, natureza, quantas pessoas, caminhos para a página pública e para
  o documento); a escolha dos recortes que entram, todos marcados por padrão; e a prévia do que será
  público.
- **FR-5728**: A prévia MUST dizer, antes do botão: quantas pessoas, com cada efeito; quais vagas e
  listas; o canal de cada grupo; quem ficou de fora e por quê; e o efeito da confirmação — *"o prazo
  de N convocações começa a correr agora, e cada candidato passa a ver a sua"* no *convoca*, e
  *"nenhum prazo muda"* no *divulga*. O conteúdo da prévia MUST sair da mesma composição que a
  confirmação grava.
- **FR-5729**: O botão MUST nomear o ato e o número: *"Publicar a ‹N›ª publicação de convocados"*,
  com quantas pessoas. A declaração do veículo e a autoridade MUST estar no mesmo formulário, sem
  passo a mais.
- **FR-5730**: Depois da confirmação, a página MUST dizer qual publicação foi feita, quantas pessoas
  ela convocou e quantas divulgou, e levar à página pública e ao documento.
- **FR-5731**: Na tela do recorte, a seção das comunicações pendentes por publicação MUST oferecer
  *"Publicar no GPS"*, levando à página de publicação com aquele recorte escolhido, e MUST manter o
  registro da publicação externa como alternativa nomeada (*"Publicada fora do GPS?"*). O cartão da
  convocação publicada no GPS MUST dizer em qual publicação ela saiu, com o caminho para a página
  pública.
- **FR-5732**: Ler a página de publicação MUST seguir a porta da condução da convocação (presidência e
  auditoria leem); publicar MUST exigir a base de gestão da comissão. Quem lê vê as publicações e a
  prévia, sem o formulário.

#### F. Compatibilidade

- **FR-5733**: Os registros anteriores MUST ficar como estão: nenhuma migração de dados, nenhuma
  comunicação reescrita. Convocação comunicada antes desta feature MAY entrar numa publicação como
  *divulga*.
- **FR-5734**: O registro da publicação externa (o gesto das pendentes e a comunicação individual da
  `050` e da `125`) e a mensagem individual MUST continuar funcionando como hoje.
- **FR-5735**: O aviso aos convocados de uma chamada publicada (`066`) MUST alcançar a publicação
  nativa, pela referência que ela grava em cada comunicação.
- **FR-5736**: O custo de consulta da página de publicação MUST NOT crescer com o número de recortes
  nem de convocações, e o da página pública e da seção MUST NOT crescer com o número de pessoas.

#### G. O caminho até a publicação *(acrescentado em 12/11/2026)*

- **FR-5737**: A gestão MUST levar à página de publicação em qualquer forma de comunicar, e não só
  pelas pendentes por publicação: a tela de convocação do recorte MUST dizer quantas convocações
  comunicadas ainda não estão na página pública e oferecer *"Publicar no GPS"*; e o Centro de Controle
  do Edital MUST levar à *Publicação das convocações* quando a fase Convocação tiver começado. Na
  demonstração de 12/11/2026, com o cenário C10 por mensagem individual, nenhuma tela levava até ela.

### Key Entities

- **Publicação de convocados**: o ato. Edital, número, instante, quem publicou, autoridade e unidade
  congeladas, declaração do veículo, conteúdo público congelado e o resumo dele. Append-only.
- **Convocação publicada**: o vínculo de uma convocação com a publicação que a divulgou, o efeito
  (*convoca* ou *divulga*) e a comunicação que a convocou — gravada pela publicação no *convoca*,
  anterior a ela no *divulga*. Uma por convocação. Append-only.
- **Documento da publicação**: os bytes do PDF e o resumo deles. Append-only.

Nenhuma entidade existente muda de forma. A comunicação continua sendo a `ComunicacaoEmitida` da
`019`, gravada pela publicação na forma de sempre.

## Success Criteria *(mandatory)*

### Measurable Outcomes

Os doze casos de validação do pedido estão mapeados no fim da [rastreabilidade](rastreabilidade.md).

- **SC-1851**: Numa convocação por mensagem enviada, publicada com efeito *divulga*, o número de
  comunicações, o instante de envio e o estado do prazo são os mesmos antes e depois da publicação.
- **SC-1852**: Numa convocação por publicação pendente, publicada com efeito *convoca*, há exatamente
  uma comunicação *enviada*, com instante igual ao da publicação; o estado passa a prazo em curso; e
  a convocação aparece no portal do candidato.
- **SC-1853**: Numa convocação com publicação registrada fora do GPS, a referência registrada continua
  a única comunicação, e a relação informativa a cita.
- **SC-1854**: Duas confirmações sucessivas num mesmo Edital produzem a 1ª e a 2ª publicação, e a
  seção *Convocações* as lista da mais nova para a mais antiga.
- **SC-1855**: Uma publicação com convocações de duas vagas, ou de duas listas da mesma vaga, mostra um
  grupo para cada uma, na página e no documento.
- **SC-1856**: A convocação de suplente para vaga que vagou, praticada depois da 1ª publicação, entra
  na 2ª com efeito *convoca*, e a 1ª não muda.
- **SC-1857**: Depois da correção de uma convocação publicada e da publicação da correção, os bytes do
  documento da 1ª publicação são idênticos aos de antes, a página da 1ª avisa da correção, e a 2ª
  marca a linha como correção.
- **SC-1858**: A mesma chave repetida devolve a mesma publicação; outra chave sobre o mesmo alcance é
  recusada; e a inserção direta de uma convocação já publicada é recusada pelo banco.
- **SC-1859**: A seção, a página da publicação e o documento respondem 200 sem sessão; a página de
  publicação da gestão não abre sem identificação.
- **SC-1860**: Nenhum CPF, endereço eletrônico, telefone, fundamento digitado ou espécie de convocação
  dos convocados aparece no texto da página nem do documento, conferido com dados que os contêm.
- **SC-1861**: Um Edital só com publicações externas, de antes desta feature, abre a página da seleção
  sem a seção, e o portal do candidato continua dizendo *"Publicada em ‹referência›"* sem caminho.
- **SC-1862**: O nome, o protocolo, o número da publicação, a data e o vencimento de uma pessoa são os
  mesmos na página pública, no texto do documento e na área do candidato.
- **SC-1863**: Em navegador real, a seção e a página da publicação, a 375 px, 1280 px e 1920 px, não
  têm rolagem horizontal, e o texto corrido não passa da medida legível; a página de publicação da
  gestão, idem a 375 px e 1280 px.
- **SC-1864**: Abrir a página de publicação, mudar os recortes escolhidos e ver a prévia não grava
  linha nenhuma, em tabela nenhuma.
- **SC-1866**: Num Perfil por mensagem individual, depois de convocar os titulares, a tela de
  convocação e o Centro de Controle levam à página de publicação; e a relação lista as pessoas na ordem
  da classificação.
- **SC-1865**: O número de consultas da página de publicação não muda de um para três recortes, e o
  da página pública não muda de uma para cinco pessoas.

## Assumptions

- **O veículo é do Edital, e quem o declara é a comissão, no ato** (1ª decisão). O GPS não infere do
  texto do Edital se a página dele é o *"endereço eletrônico do certame"*: é a mesma recusa que a
  `R-006` da `025` escreveu para a ampla concorrência.
- **O prazo continua correndo da comunicação bem-sucedida**, nas duas formas. Esta spec muda quem
  grava a comunicação da publicação — o ato no GPS, além da comissão que registra a externa —, e não
  quando o prazo começa.
- **Nome é o da inscrição**, o mesmo que a divulgação do resultado publica. Nome social, se um dia a
  inscrição o tiver, entra pela mesma leitura.
- **A lista de concorrência é pública** porque a divulgação do resultado já a publica, por lista e com
  nome; esconder aqui o que está lá não protegeria ninguém e tiraria a conferência da ordem (3ª
  decisão; D-008).

## Registros para decisão própria

Achados do diagnóstico que esta spec **não** resolve — governança é do usuário:

- **Publicar no conteúdo do Edital o veículo da convocação.** A declaração no ato resolve o caso de
  hoje; um campo no Perfil publicado tornaria a regra verificável e impressa no Edital, com o custo de
  um degrau de schema.
- **Listar as publicações externas na página pública.** A referência registrada é texto livre; se ela
  passar a ser pública, convém que a comissão saiba disso ao digitá-la, como na 2ª decisão da `125`.
- **Orientações livres da comissão na publicação.** Ficaram fixas (FR-5716) pela mesma razão do texto
  livre da `125`; se forem necessárias, pedem aviso e prévia.
