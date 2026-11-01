# Feature Specification: Leitura do conteúdo não publicado na gestão

**Feature Branch**: `claude/112-leitura-do-nao-publicado`

**Created**: 2026-11-01

**Status**: Especificada e planejada em 01/11/2026 sobre a `main` em `32097602`. **Não
implementada.** Aguarda a revisão do usuário e as respostas da §Pendências de produto.

**Input**: a pendência P-2 da `111` (Kit de Divulgação), encaminhada pelo usuário em 01/11/2026 a
spec própria, separada daquela: *definir quem pode ler conteúdo não publicado na gestão, com a
verificação no backend*. O papel Comunicação da `111` não é atribuído a ninguém até esta spec estar
mergeada.

> **Faixa de identificadores.** Esta spec abre em **FR-3501** e **SC-1061**. O teto medido em
> 01/11/2026 na `main`, em todas as branches locais e remotas e em todas as worktrees desta máquina
> é o requisito três mil quatrocentos e quarenta e oito e o critério mil e cinquenta e oito, os dois
> da `111`, que ainda não está na `main`. A folga é deliberada. **Nenhum `UX-` é aberto aqui.** As
> decisões técnicas reiniciam em `D-001` e moram no [research.md](research.md); as pendências de
> produto são `P-`; os casos-limite são `EC-`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-017 da `020`"). Decisão de outra feature pelo assunto e pela feature, porque `D-` aqui é só
> desta.

---

## Por que esta feature existe

A gestão confere escopo em toda tela de Edital: ninguém abre Edital de outra unidade. Mas, dentro
da unidade, **quase nenhuma tela de leitura confere capacidade**. O inventário de 01/11 (no
[research.md](research.md), §Inventário) mostra que qualquer pessoa com vínculo na unidade — o
integrante sem permissão nenhuma, o administrador de acessos, o julgador, o exportador — abre:

- na lista, o número, o título e a situação de todo Edital, inclusive os que nunca foram publicados,
  e a marca "Retificação … aguarda …" de cada Retificação em curso;
- o detalhe de qualquer Edital, com pendências, participantes e as Retificações **em curso**, com a
  justificativa e o motivo de devolução;
- a composição inteira do rascunho, etapa por etapa, em modo leitura;
- a prévia do Edital e o PDF dela;
- o detalhe, o conteúdo proposto e a tela de ato de toda Retificação em curso — e uma prorrogação é
  uma Retificação.

Os anexos do rascunho são a exceção: desde a `020` eles exigem uma de três capacidades (a FR-017
daquela feature) e recusam com "não encontrado". A mesma informação, porém, aparece na prévia e na
etapa Anexos, que não exigem nada.

A `111` cria o papel restrito Comunicação, de quem divulga o que já foi publicado. Pela política
vigente, essa pessoa saberia de prorrogação, cancelamento ou Retificação antes do ato — e a
divulgação antecipada de ato não publicado é o risco que a Constituição manda prevenir (Princípio
III: negar por padrão, menor privilégio, impedir acesso por manipulação de identificador).

### O que esta spec cobre, e o que fica fora

**Entra:**

- uma regra única de quem lê o que ainda não foi publicado, em dois níveis — a **existência** do
  ato em preparação e o **conteúdo** dele;
- a verificação dessa regra em toda rota da gestão que exibe Edital sem publicação ou Retificação em
  curso, por acesso direto à URL e não só pela navegação;
- as recusas canônicas, conforme a gramática da `033`, e o inventário das negativas atualizado;
- o efeito sobre cada papel e vínculo existente, com as jornadas atuais preservadas;
- testes de autorização por URL direta, em matriz rota × ator, e um guardião que alcança a rota
  escrita amanhã.

**Fica fora, de propósito:**

- o papel Comunicação e a capacidade `material:gerar` — são da `111`; esta spec só garante que um
  papel sem a capacidade de leitura não enxerga o não publicado;
- uma entrada própria na barra para papel restrito: é complemento de UX, e não substitui a
  verificação (`D-007`);
- a trilha de auditoria do Edital (`editais/<id>/auditoria`), que continua sob
  `auditoria:consultar` e mostra o que mostra hoje (`D-005`);
- o conteúdo publicado, o portal do candidato e a API pública, que só servem o publicado;
- qualquer mudança nos atos (elaborar, submeter, homologar, publicar, cancelar), que já exigem
  capacidade para escrever.

---

## Vocabulário desta spec

- **Edital não publicado**: Edital que não tem nenhuma Publicação. Inclui os em elaboração, em
  revisão e homologados, e o cancelado antes de ser publicado. **A situação não basta**: um Edital
  cancelado pode ter sido publicado ou não.
- **Retificação em curso**: Retificação em elaboração, em revisão ou homologada. A Retificação
  cancelada nunca publicada também é não publicada (EC-3).
- **Existência**: saber que o ato em preparação existe — número, título, situação, e, para a
  Retificação, que há uma e em que passo está.
- **Conteúdo**: tudo o que o ato diz ou dirá — o rascunho por etapa, a prévia e o PDF dela, os
  anexos, as pendências de validação, o conteúdo proposto e as alterações de uma Retificação, a
  justificativa e o motivo de devolução, e os participantes do fluxo.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem não prepara o ato não o lê antes da publicação (Priority: P1) 🎯 MVP

Uma pessoa da unidade sem capacidade de preparar, revisar, publicar ou conduzir Editais — o
integrante, o administrador de acessos, o julgador, o exportador, e amanhã a Comunicação — usa a
gestão. Ela vê os Editais publicados como hoje. Ela não vê Edital não publicado, nem Retificação em
curso, nem pela tela nem colando o endereço.

**Why this priority**: é a pendência que bloqueia a atribuição do papel da `111`, e é a exigência
constitucional de negar por padrão.

**Independent Test**: com um Edital em elaboração, um homologado e um publicado com Retificação em
curso, uma identidade só com o vínculo de integrante abre cada URL da matriz e recebe a recusa
canônica em todas; na lista, só o publicado aparece, e sem a marca da Retificação.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração na unidade, **When** o integrante abre a lista, **Then** o
   Edital não aparece, e o resumo por situação não o conta.
2. **Given** o mesmo Edital, **When** o integrante cola o endereço do detalhe, da composição, da
   prévia, do PDF da prévia, de um anexo ou da confirmação de um ato, **Then** recebe "não
   encontrado" — a mesma resposta de um Edital inexistente ou de outra unidade.
3. **Given** um Edital publicado com uma prorrogação em revisão, **When** o integrante abre o
   detalhe do Edital, **Then** vê o Edital e os documentos publicados, e nenhuma menção à
   Retificação em curso.
4. **Given** a mesma prorrogação, **When** o integrante cola o endereço do detalhe, da edição ou de
   um ato da Retificação, **Then** recebe "não encontrado".
5. **Given** um fragmento de composição que lê o rascunho, **When** o integrante o pede pelo
   endereço com `?edital=`, **Then** recebe a mesma recusa.

---

### User Story 2 — Quem prepara, revisa, publica ou conduz continua trabalhando como hoje (Priority: P1)

Elaborador, homologador, publicador e gestor seguem as jornadas atuais sem nenhuma recusa nova:
compor, conferir a Revisão, abrir a prévia e os anexos, homologar, publicar, cancelar, retificar.

**Why this priority**: a correção não pode custar a jornada de quem pratica os atos.

**Independent Test**: a suíte de jornadas existente (`tests/authorization/`, `tests/interface/` e
as de navegador da `107`) continua verde sem alteração de expectativa; a matriz rota × ator afirma
200 para cada papel do fluxo nas rotas que a jornada dele usa.

**Acceptance Scenarios**:

1. **Given** um Edital homologado, **When** o publicador abre o detalhe, a prévia, o PDF e a
   confirmação de publicar, **Then** todas abrem como hoje.
2. **Given** uma Retificação submetida, **When** o homologador abre o detalhe dela e o ato de
   homologar, **Then** abrem como hoje.
3. **Given** um Edital em elaboração, **When** o gestor abre o detalhe e a confirmação de cancelar,
   **Then** abrem como hoje.
4. **Given** um anexo do rascunho, **When** o publicador ou o gestor o abre, **Then** o arquivo
   abre (P-2: hoje recusam).

---

### User Story 3 — Quem tem vínculo com o Processo sabe que o Edital existe, sem ler o conteúdo (Priority: P2)

A presidência e os membros da comissão de um Processo, e o auditor, precisam saber que um Edital
existe e em que situação está — para constituir a comissão, alocar, auditar —, mas não precisam ler
o rascunho.

**Why this priority**: preserva a jornada da comissão e do auditor sem abrir o conteúdo a eles.

**Independent Test**: a presidente de comissão sem papel sistêmico vê na lista o Edital em
elaboração do seu Processo, abre o detalhe reduzido e recebe a recusa explicada na prévia; não vê o
Edital em elaboração de outro Processo da unidade.

**Acceptance Scenarios**:

1. **Given** a presidente da comissão do Processo A, sem papel sistêmico, e um Edital em elaboração
   em A, **When** abre a lista, **Then** vê número, título e situação do Edital, sem ações de
   conteúdo.
2. **Given** a mesma pessoa, **When** abre o detalhe desse Edital, **Then** vê identificação,
   situação e as ações que já lhe cabem (comissão, alocação), e um aviso de que o conteúdo é de
   quem prepara o ato — sem pendências, participantes nem Retificações em curso.
3. **Given** a mesma pessoa, **When** cola o endereço da prévia, **Then** recebe a recusa explicada
   que nomeia o que falta e a quem pedir.
4. **Given** um Edital em elaboração do Processo B, em que ela não tem vínculo, **When** cola o
   endereço do detalhe, **Then** recebe "não encontrado".
5. **Given** o auditor, **When** abre a lista, **Then** vê os Editais não publicados com o caminho
   para a trilha deles, e a trilha abre como hoje.

---

### Edge Cases

- **EC-1** Edital cancelado sem nunca ter sido publicado: continua não publicado; a regra não muda
  com o cancelamento.
- **EC-2** Edital publicado e depois encerrado ou cancelado: o conteúdo publicado segue aberto a
  toda identidade do escopo; as Retificações dele seguem a regra da Retificação.
- **EC-3** Retificação cancelada sem publicação: o conteúdo dela nunca foi publicado e segue a
  regra do conteúdo; a existência dela continua visível a quem a tinha.
- **EC-4** A prévia de um Edital publicado responde hoje "a prévia existe enquanto…" (409). Para
  quem não tem a existência de um Edital não publicado, a recusa vem **antes** da conferência de
  estado: a ordem é escopo → existência → conteúdo → estado, senão o 409 revelaria a situação.
- **EC-5** POST na composição por quem não tem a capacidade de conteúdo: a mesma recusa do GET, e
  nenhuma mensagem de "não pode editar" que confirme a existência.
- **EC-6** Processo cujo nenhum Edital foi publicado: o detalhe do Processo, a supervisão e a tela
  de ato do Processo seguem a regra da existência do Edital — sem existência, "não encontrado".
- **EC-7** Papel revogado durante a sessão: vale o que a sessão resolveu para a requisição, como em
  toda porta da gestão (a resolução institucional da `106` relê os vínculos a cada requisição).
- **EC-8** Pessoa com dois vínculos — integrante numa unidade, elaboradora noutra: a capacidade vale
  só no escopo ativo.
- **EC-9** Fragmentos que não leem o Edital (evento, fato, quadro, modalidade, remover) não mudam.
- **EC-10** A faixa "Ações disponíveis para você" já filtra por capacidade, e não muda; ela não pode
  passar a oferecer destino que a regra recuse.
- **EC-11** A Visão Geral exige `visao:consultar`, que hoje só o gestor tem, e lista Editais não
  publicados. Ela passa a aplicar a mesma regra, para que um papel futuro com a visão e sem a
  leitura não os veja.
- **EC-12** A Agenda só mostra cronograma publicado e não muda; um teste prende isso.

---

## Requirements *(mandatory)*

### A regra

- **FR-3501**: O sistema DEVE tratar como não publicado o Edital sem nenhuma Publicação, qualquer
  que seja a situação, e a Retificação que não foi publicada, qualquer que seja a situação.
- **FR-3502**: O sistema DEVE ter uma capacidade própria de **leitura do conteúdo não publicado**,
  distinta das capacidades de praticar atos, e DEVE concedê-la, no catálogo de papéis, ao
  elaborador, ao homologador, ao publicador e ao gestor — e a nenhum outro papel, de unidade ou
  institucional.
- **FR-3503**: O conteúdo de Edital não publicado e de Retificação em curso (vocabulário acima) DEVE
  ser lido só por quem tem a capacidade da FR-3502 no escopo do ato.
- **FR-3504**: A existência de Edital não publicado DEVE ser conhecida só por quem tem a capacidade
  da FR-3502, por quem tem `auditoria:consultar`, ou por quem tem vínculo de comissão vigente no
  Processo do Edital (P-3).
- **FR-3505**: A existência de Retificação em curso DEVE ser conhecida só por quem tem a capacidade
  da FR-3502, e pelo auditor apenas na trilha de auditoria (P-4).
- **FR-3506**: A regra DEVE ser uma só, consultável fora das views, e toda tela, fragmento e
  documento que exibe o não publicado DEVE perguntá-la a ela — nenhuma rota decide por lista
  própria de capacidades.
- **FR-3507**: A leitura dos anexos do rascunho DEVE passar a seguir a FR-3503, substituindo o
  conjunto de três capacidades da FR-017 da `020` (P-2).

### A verificação, rota a rota

- **FR-3508**: A lista de Processos DEVE omitir, para quem não tem a existência, o Edital não
  publicado, inclusive das contagens por situação; e DEVE omitir a marca de Retificação em curso a
  quem não tem a existência dela.
- **FR-3509**: O detalhe do Edital não publicado DEVE recusar quem não tem a existência; a quem tem a
  existência sem o conteúdo, DEVE mostrar só identificação, situação, as ações que a pessoa pode
  praticar e o aviso de que o conteúdo é de quem prepara o ato — sem pendências, participantes nem
  Retificações em curso.
- **FR-3510**: O detalhe do Edital publicado DEVE omitir a seção de Retificações em curso, e o cartão
  "O que fazer agora" a respeito delas, a quem não tem a existência da Retificação.
- **FR-3511**: A composição (todas as etapas, em leitura ou edição, por GET ou POST), a prévia, o
  PDF da prévia, os anexos do rascunho, a confirmação de ato de Edital não publicado e os
  fragmentos que leem o rascunho DEVEM exigir o conteúdo.
- **FR-3512**: O detalhe, a edição e a confirmação de ato de Retificação em curso DEVEM exigir o
  conteúdo; a tela de retificar DEVE omitir a lista das Retificações em curso a quem não tem a
  existência delas.
- **FR-3513**: O detalhe do Processo, a supervisão e a confirmação de ato do Processo DEVEM omitir os
  Editais não publicados a quem não tem a existência deles, e DEVEM recusar o Processo cujo nenhum
  Edital a pessoa alcança e no qual ela não tem vínculo (EC-6).
- **FR-3514**: A Visão Geral DEVE aplicar a FR-3504 aos Editais que lista.
- **FR-3515**: A verificação DEVE acontecer no backend, a cada requisição, antes de qualquer leitura
  do conteúdo e antes da conferência de estado (EC-4).
- **FR-3527**: Toda rota da gestão que recebe identificador de Edital, de Retificação ou de Processo
  DEVE responder "não encontrado" a quem não tem a existência do ato não publicado — inclusive as
  rotas que só operam sobre Edital publicado e hoje recusariam por estado —, antes de qualquer
  conferência de estado.
- **FR-3516**: A Agenda, a trilha da unidade, o relatório do Edital, as alocações e a faixa de ações
  NÃO DEVEM passar a exibir nada não publicado, e o que exibem hoje DEVE ser preso por teste.

### As recusas

- **FR-3517**: A quem não tem a existência, toda rota DEVE responder "não encontrado", a mesma
  resposta de objeto inexistente e de outra unidade — a doutrina dos anexos da `020` e da `022`, que
  o inventário da `033` registrou como deliberada.
- **FR-3518**: A quem tem a existência e não tem o conteúdo, toda rota de conteúdo DEVE responder a
  recusa explicada da `033` — pelo ponto único, nomeando a capacidade que falta e a quem pedi-la, na
  formulação canônica da FR-486 da `033`.
- **FR-3519**: Cada `raise Http404` novo ou reclassificado DEVE entrar no inventário das negativas da
  `033`, com a classe "recusa de autorização — existência de ato não publicado", e o detector de
  `tests/test_gramatica_das_portas.py` DEVE continuar verde.
- **FR-3520**: Nenhuma recusa DEVE dizer a situação, o número, o título nem o autor do ato a quem não
  tem a existência dele.

### Papéis

- **FR-3521**: O efeito sobre cada papel e vínculo DEVE ser o da tabela da §Efeito sobre os papéis,
  e nenhum outro.
- **FR-3522**: A descrição dos papéis na tela de entrada (`DESCRICOES`) e no catálogo de acessos da
  `107` NÃO DEVE mudar de sentido; a capacidade nova não aparece como papel.
- **FR-3523**: Um papel acrescentado ao catálogo depois desta feature (como a Comunicação da `111`)
  NÃO DEVE receber a capacidade da FR-3502 sem decisão explícita, e um guardião DEVE reprovar a
  concessão a papel fora da lista da FR-3502.

### Testes

- **FR-3524**: Uma matriz rota × ator DEVE exercitar, por URL direta, toda rota do inventário desta
  spec contra: integrante sem vínculo, integrante com vínculo de comissão, presidência, auditor,
  administrador de acessos, julgador, exportador, elaborador, homologador, publicador, gestor e uma
  identidade de outra unidade.
- **FR-3525**: Um guardião DEVE reprovar rota da gestão que receba identificador de Edital, de
  Retificação ou de Processo e que não esteja classificada no inventário desta spec — a rota escrita
  amanhã não escapa calada.
- **FR-3526**: A lista NÃO DEVE ganhar consulta por linha por causa da regra: a existência sai das
  capacidades da sessão e dos vínculos que a lista já lê.

### Efeito sobre os papéis

| Papel ou vínculo | Existência do Edital não publicado | Conteúdo dele | Retificação em curso | Muda o quê hoje |
|---|---|---|---|---|
| Elaborador | sim | sim | sim | nada |
| Homologador | sim | sim | sim | nada |
| Publicador | sim | sim | sim | passa a abrir anexo do rascunho (P-2) |
| Gestor | sim | sim | sim | passa a abrir anexo do rascunho (P-2) |
| Auditor | sim | não | só na trilha | perde composição, prévia, pendências e Retificação em curso fora da trilha |
| Presidência e membros da comissão (vínculo no Processo) | do próprio Processo | não | não (P-4) | perde conteúdo e Edital não publicado de outros Processos |
| Julgador de recursos | não | não | não | perde todo o não publicado |
| Exportador de matrículas | não | não | não | idem |
| Participante do piloto do assistente | não | não | não | idem |
| Integrante sem vínculo de comissão | não | não | não | idem |
| Administrador de acessos da unidade | não | não | não | idem |
| Administrador institucional | não | não | não | nada (o escopo institucional já não alcança Edital) |
| Comunicação (`111`, ainda não atribuível) | não | não | não | — |

Quem acumula papéis recebe a união. A identidade de outra unidade não alcança nada, como hoje.

### Key Entities

- **Capacidade de leitura do não publicado**: permissão do catálogo, sem dado próprio. Não é ato:
  não gera trilha.
- **Regra de leitura do não publicado**: função de (ator, Edital ou Retificação) → nenhum acesso,
  existência ou conteúdo.
- **Inventário das rotas do não publicado**: o artefato da spec que classifica cada rota (FR-3525),
  lido pelo guardião.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1061**: Em 100% das combinações da matriz rota × ator (FR-3524), quem não tem a existência
  recebe "não encontrado", quem tem a existência sem o conteúdo recebe a recusa explicada, e quem
  tem o conteúdo recebe a tela. Verificação automática.
- **SC-1062**: Zero alterações de expectativa nos testes de jornada existentes do elaborador, do
  homologador, do publicador, do gestor, da comissão e do auditor, exceto as listadas na
  rastreabilidade como efeito desta spec. Verificação automática.
- **SC-1063**: Uma pessoa só com o vínculo de integrante, navegando e colando endereços, não descobre
  número, título, situação nem conteúdo de nenhum Edital não publicado nem de nenhuma Retificação em
  curso da unidade. Verificação automática (matriz) e manual (quickstart).
- **SC-1064**: Uma rota de Edital, Retificação ou Processo acrescentada sem classificação no
  inventário reprova a suíte. Verificação automática (o guardião testa a si mesmo).
- **SC-1065**: A lista de Processos faz o mesmo número de consultas antes e depois, para um ator com
  e sem a capacidade. Verificação automática.
- **SC-1066**: O usuário confirma, numa sessão de homologação, que a presidência de comissão sem
  papel sistêmico segue constituindo a comissão e alocando, e que o publicador segue publicando.
  Validação humana.

---

## Pendências de produto

Nenhuma bloqueia o início do planejamento. **Todas bloqueiam o merge**, porque mudam o que cada papel
vê. Cada uma tem o comportamento que esta spec adota enquanto não for respondida.

| # | Pergunta | Comportamento enquanto não respondida |
|---|---|---|
| **P-1** | A leitura do não publicado é uma **capacidade própria** concedida a quatro papéis, ou o conjunto das capacidades de ato (elaborar, submeter, homologar, publicar, cancelar) já basta? | Capacidade própria (FR-3502, `D-001`) |
| **P-2** | O publicador e o gestor passam a abrir os anexos do rascunho? É emenda à FR-017 da `020`, que nomeou só elaboração, revisão e homologação. | Passam, por uma regra só (FR-3507). Se recusada, a FR-3507 sai e a prévia do publicador continua mostrando o que o anexo não abre — o defeito fica registrado |
| **P-3** | A presidência e os membros da comissão sabem que o Edital do próprio Processo existe antes da publicação? | Sabem, sem o conteúdo (FR-3504) |
| **P-4** | A presidência sabe de Retificação em curso (por exemplo, uma prorrogação que muda o cronograma da comissão)? E o auditor, fora da trilha? | Não; o auditor só pela trilha (FR-3505) |

---

## Assumptions

- A trilha de auditoria do Edital (`auditoria:consultar`) é pergunta própria, e já mostra as
  Retificações não publicadas ao auditor; esta spec não a muda (`D-005`).
- O avaliador chega ao trabalho por Minhas Etapas e pela Mesa, que só tratam Edital publicado; o
  link da Mesa para o detalhe aponta Edital publicado.
- As capacidades vêm da sessão, sem consulta, e os vínculos de comissão já são lidos pela lista.
- O conteúdo publicado já é público pelo portal; o detalhe do Edital publicado continua aberto a
  toda identidade do escopo.
- A entrada "Processos Seletivos" continua para toda identidade: a lista mostra o publicado e diz a
  quem não tem papel o que falta (`D-007`).
