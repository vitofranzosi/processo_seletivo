# Feature Specification: O alcance da Etapa por Modalidade

**Feature Branch**: `claude/distracted-visvesvaraya-1dc305`, sobre a `main` em `37ed0ad0`

**Created**: 2026-11-13

**Status**: Draft

**Input**: a lacuna **L-2** da avaliação de capacidade de 11/09
(`doc/avaliacao-de-capacidade-editais-2026-09-11.md`, *"As lacunas de autoria"*) e a decisão **P-1**
do usuário em 13/11/2026, no estudo da verificação da autodeclaração
(`doc/estudo-verificacao-da-autodeclaracao-2026-11-13/`, PR #541): *a Etapa ganha alcance por
Modalidade*. É a primeira entrega da camada A desse estudo, e a nota de 13/11 na DP-10
(`doc/decisoes-pendentes-da-consolidacao.md`) a registra como precondição da família
"heteroidentificação".

> **Faixa de identificadores.** Esta spec abre em **FR-6960**, **SC-2310** e **UX-730**. O teto
> medido em 13/11/2026, na `main` e nas worktrees locais, era o requisito seis mil novecentos e
> cinquenta e um e o critério dois mil trezentos e quatro, da `162`, e o requisito de experiência
> setecentos e vinte e sete. O intervalo deixado é de propósito: as specs seguintes da camada A podem
> nascer em paralelo a esta. A pasta `163` estava livre na `main` e no único PR aberto (#541). As
> decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature. Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

A Etapa de avaliação é do Edital e **vale para toda inscrição enviada**. A docstring do modelo
registra a escolha e adia a mudança para *"quando houver um Edital real que precise disso"*.

Esse Edital existe. A heteroidentificação do Ifes (Res. CS 61/2019; Editais 28/2026 e 57/2026)
alcança só quem se inscreveu numa Modalidade reservada a pretos e pardos. Composta hoje no GPS, ela
faria três coisas erradas:

1. **A distribuição criaria Atribuição para todo inscrito**, inclusive para quem concorre só pela
   ampla e nunca será convocado para ela.
2. **A prontidão esperaria avaliação de quem não passa por ela**, e a Etapa nunca ficaria
   consolidável.
3. **A progressão travaria a Etapa seguinte.** Quem vem depois exige habilitação na imediatamente
   anterior. Se a heteroidentificação ficar antes da Análise documental, o candidato da ampla, que
   não tem Resultado nela, ficaria *"aguardando a Etapa anterior"* para sempre.

Por isso o Ifes faz a heteroidentificação **fora** do sistema, por videoconferência ou presencialmente,
e o GPS só recebe a autodeclaração como documento. O estudo de 13/11 mostrou que nenhuma peça da
camada A (pareceres, deliberação, consequência por lista, recurso à CPVA) tem onde morar enquanto a
Etapa não souber a quem se aplica.

O mesmo vale, em outra dimensão, para o barema por curso: a `146` deixou fora o barema por Perfil
porque *"depende de a Etapa poder variar por Perfil"*. Esta spec resolve a dimensão da Modalidade, e
deixa a do Perfil para a spec que a pedir (D-009).

### O que esta spec cobre, e o que fica fora

**Cobre:** a declaração do alcance na Etapa, a publicação dele como norma, a Retificação dele, e
o efeito dele em tudo o que hoje enumera "as inscrições da Etapa" — distribuição, avaliação,
Ocorrência, consolidação, prontidão, progressão, painéis da gestão, acompanhamento do candidato e
documento do Edital.

**Fica fora, e cada uma é spec seguinte da camada A:**

- o **efeito por lista** do desfecho desfavorável (R-2 do estudo, decisão P-2): hoje `ELIMINADA` tira
  a pessoa de todas as listas, e continua tirando depois desta spec;
- a **regra de combinação** dos pareceres (R-4, decisão P-3): hoje mais de uma avaliação por
  inscrição numa Etapa decisória continua sem regra que as combine;
- a **visibilidade e a recorribilidade** da Etapa fora de marco (R-8): a Etapa que nenhum marco
  enumera continua invisível ao titular e irrecorrível;
- a **orientação** no Centro, em Minhas atividades e no portal (a natureza "verificação da
  autodeclaração" e o degrau "falta um passo seu");
- o **vídeo** (camada B), bloqueado por norma (P-0);
- o **alcance por Perfil**, que o barema por curso pede (D-009);
- os **"dez primeiros de cada código"**: a metade da L-2 que depende da ordem. Ela já se exprime pela
  faixa do corte da `014`, que se soma ao alcance (FR-6974), e não é refeita aqui.

---

## Clarifications

### Session 2026-11-13 (decisões do usuário)

- **P-1 — A Etapa ganha alcance por Modalidade?** Sim. *(Estudo da verificação da autodeclaração,
  13/11/2026; DP-10, nota de 13/11.)* É o objeto desta spec.
- **P-2 e P-3** foram decididas no mesmo dia, e são das specs seguintes. Esta spec não as antecipa:
  o desfecho de uma Etapa restrita produz, nesta entrega, exatamente o efeito que produz hoje
  (D-010).

### Session 2026-11-13 (decisões desta spec, abertas à revisão do usuário)

O pedido que originou a spec delegou uma escolha: *como o alcance se expressa num Edital
multiperfil*. Ela é a D-001. As demais decisões (D-002 a D-010) são as que a redação exigiu, e cada
uma registra a alternativa descartada. Nenhuma toma decisão normativa do Ifes: todas preservam o que
o Edital de hoje significa.

---

## User Scenarios & Testing *(mandatory)*

Os exemplos usam o caso que motivou a spec: um Edital de três Perfis (C1, C2 e C3), cada um com as
Modalidades `AC`, `PPI` e `PcD`, e quatro Etapas na ordem — Prova (pontuada, classificatória, para
todos), **Heteroidentificação** (decisória, eliminatória, só `PPI`), Análise documental (decisória,
para todos, governada pelo corte) e Entrevista (pontuada, para todos).

### User Story 1 — Quem elabora declara a quem a Etapa se aplica (Priority: P1)

Quem elabora o Edital abre a Etapa "Heteroidentificação" e escolhe *"Só as inscrições destas
Modalidades"*. A tela lista os códigos de Modalidade do Edital, cada um com a denominação e os Perfis
que o têm. Marca `PPI`. A Revisão e o documento passam a dizer que a Etapa se aplica aos candidatos
inscritos em "Pretos e pardos" (`PPI`), nos três Perfis. As outras três Etapas continuam como
estavam, sem que ninguém precisasse tocá-las.

**Why this priority**: sem a declaração, nada do resto existe. É também a única parte que muda o
documento oficial.

**Independent Test**: compor o Edital acima, publicar, e conferir no conteúdo publicado, na Revisão e
no documento que a Etapa declara `PPI` e as outras três não declaram nada.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração com a Etapa "Heteroidentificação" sem alcance declarado,
   **When** quem elabora a abre, **Then** a opção marcada é *"Todas as inscrições"*.
2. **Given** a mesma Etapa, **When** quem elabora escolhe *"Só as inscrições destas Modalidades"* e
   marca `PPI`, **Then** a gravação passa, e a tela diz que a Etapa alcança `PPI` em C1, C2 e C3.
3. **Given** a escolha *"Só as inscrições destas Modalidades"* sem nenhum código marcado, **When**
   quem elabora grava, **Then** a gravação é recusada com a mensagem de que é preciso marcar ao menos
   uma Modalidade ou voltar a *"Todas as inscrições"*.
4. **Given** o Edital composto, **When** é publicado, **Then** o documento diz, na Etapa
   "Heteroidentificação", a quem ela se aplica, pela denominação e pelo código; e as outras três
   Etapas saem com o mesmo texto que sairiam antes desta feature.
5. **Given** um Edital em que `PPI` se chama "Pretos e pardos" em C1 e "Pretos, pardos e indígenas"
   em C2, **When** quem elabora tenta publicar com o alcance `PPI`, **Then** a publicação é impedida,
   e a mensagem nomeia os Perfis com a denominação divergente.

---

### User Story 2 — Só as inscrições alcançadas passam pela Etapa (Priority: P1)

Encerradas as inscrições, a presidência distribui a Heteroidentificação. Só as inscrições `PPI` dos
três Perfis entram na distribuição e no rodízio. A Mesa da comissão mostra só elas. A prontidão conta
só elas, e a Etapa fica consolidável quando todas elas têm conclusão. A consolidação produz Resultado
só para elas.

**Why this priority**: é o defeito que a L-2 descreve, e o que hoje obriga o Ifes a fazer a
verificação fora do sistema.

**Independent Test**: com 30 inscrições (10 por Perfil, das quais 4 `PPI` em cada), distribuir,
concluir as 12 avaliações e consolidar. Conferir que nenhuma Atribuição, estado de prontidão ou
Resultado da Etapa existe para as outras 18.

**Acceptance Scenarios**:

1. **Given** o Edital publicado e as inscrições encerradas, **When** a presidência abre a
   distribuição da Heteroidentificação, **Then** a tela oferece as 12 inscrições `PPI`, e diz
   *"12 inscrições alcançadas, de 30"*.
2. **Given** uma tentativa de atribuir uma inscrição `AC` à Heteroidentificação, por qualquer
   caminho, **When** ela chega ao servidor, **Then** é recusada, e o motivo diz que a Modalidade da
   inscrição está fora do alcance da Etapa.
3. **Given** as 12 avaliações concluídas, **When** a presidência abre o painel da Etapa, **Then** o
   total é 12, todas *prontas*, e a Etapa está consolidável.
4. **Given** a consolidação, **When** ela termina, **Then** existem 12 Resultados da Etapa, e nenhum
   para as 18 inscrições fora do alcance.
5. **Given** uma Ocorrência (ausência) registrada para uma inscrição `AC` na Heteroidentificação,
   **When** ela chega ao servidor, **Then** é recusada pelo mesmo motivo.

---

### User Story 3 — Quem não é alcançado atravessa a Etapa sem esperar por ela (Priority: P1)

Uma candidata da ampla em C2 foi habilitada na Prova. A Heteroidentificação, que vem logo depois, não
a alcança. Ela entra na Análise documental como se a Heteroidentificação não existisse para ela: não
espera Resultado nela, não é eliminada por ela e não aparece como *"aguardando a Etapa anterior"*.
Um candidato `PPI` do mesmo Perfil, ao contrário, só entra na Análise documental depois de habilitado
na Heteroidentificação, como hoje.

**Why this priority**: sem isso, a primeira Etapa restrita antes de uma Etapa universal trava o
certame inteiro para quem ela não alcança.

**Independent Test**: no Edital acima, com a Prova consolidada e a Heteroidentificação ainda sem
Resultado, conferir que a candidata `AC` participa da Análise documental e o candidato `PPI` não.

**Acceptance Scenarios**:

1. **Given** a Prova consolidada e a Heteroidentificação sem Resultado, **When** a presidência abre
   a Análise documental, **Then** as inscrições fora do alcance da Heteroidentificação que foram
   habilitadas na Prova participam, e as `PPI` aparecem como aguardando a Etapa anterior.
2. **Given** a Heteroidentificação consolidada com um `PPI` desfavorável, **When** a Análise
   documental é distribuída, **Then** esse `PPI` não participa dela — o efeito de hoje de um desfecho
   eliminatório —, e os `AC` e `PcD` continuam participando.
3. **Given** uma Etapa restrita a `PcD` logo depois da Heteroidentificação restrita a `PPI`, **When**
   uma inscrição `AC` chega à Análise documental, **Then** a exigência de habilitação é lida na
   Prova, que é a última Etapa anterior que a alcança.

---

### User Story 4 — O candidato vê só os passos que são dele (Priority: P2)

No acompanhamento, a candidata da ampla não vê a Heteroidentificação entre os passos dela, nem
pendente, nem concluída. O candidato `PPI` a vê como vê hoje qualquer Etapa que o portal mostra.

**Why this priority**: mostrar a quem não é alcançado uma Etapa que nunca acontecerá para ele é dizer
que falta algo que não falta. A orientação própria da verificação é de spec seguinte; esta só impede
o passo errado.

**Independent Test**: abrir o acompanhamento das duas inscrições no mesmo Edital e comparar os
passos.

**Acceptance Scenarios**:

1. **Given** as duas inscrições, **When** cada titular abre o acompanhamento, **Then** a Etapa
   restrita aparece só para o titular `PPI`.
2. **Given** um Edital sem nenhuma Etapa restrita, **When** qualquer titular abre o acompanhamento,
   **Then** ele vê exatamente o que via antes desta feature.

---

### User Story 5 — A Retificação muda o alcance sem desfazer o que já foi avaliado (Priority: P2)

Depois de publicado, o Edital é retificado para incluir `PcD` no alcance da Heteroidentificação, por
erro de composição. A Retificação passa: as inscrições `PcD` passam a ser alcançadas e entram como
pendentes na distribuição. Em outro Edital, uma Retificação tenta tirar `PPI` do alcance depois de a
comissão concluir avaliações: ela é recusada, e a mensagem diz quantas inscrições já têm Atribuição
ou Resultado na Etapa.

**Why this priority**: o alcance é norma, e norma publicada só muda por Retificação. O risco é a
Retificação apagar, em silêncio, avaliação já feita.

**Independent Test**: retificar um Edital publicado nos dois sentidos, antes e depois de haver
Atribuição na Etapa.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com a Etapa restrita a `PPI`, **When** uma Retificação acrescenta
   `PcD`, **Then** ela passa, e a partir da publicação as inscrições `PcD` participam da Etapa.
2. **Given** o mesmo Edital, sem nenhuma Atribuição na Etapa, **When** uma Retificação tira `PPI` e
   põe `PcD`, **Then** ela passa.
3. **Given** o mesmo Edital com Atribuições de inscrições `PPI` na Etapa, **When** uma Retificação
   tira `PPI` do alcance, **Then** ela é recusada, e a mensagem nomeia a Etapa, o código e quantas
   inscrições seriam excluídas tendo Atribuição ou Resultado.
4. **Given** a Etapa com alcance "todas" e Atribuições de inscrições `AC`, **When** uma Retificação a
   restringe a `PPI`, **Then** ela é recusada pela mesma razão: restringir é excluir as `AC`.
5. **Given** a Etapa restrita a `PPI`, **When** uma Retificação a devolve a *"Todas as inscrições"*,
   **Then** ela passa, e todas as inscrições passam a participar.

---

### Edge Cases

- **Inscrição sem Modalidade.** É a ampla concorrência, na grafia que o sorteio, a ordem e o quadro
  de vagas já usam. Uma Etapa restrita **nunca** a alcança; uma Etapa com *"Todas as inscrições"*
  sempre (FR-6968).
- **A Modalidade chamada "Ampla concorrência".** Quando o Edital a cadastra como Modalidade com
  código, ela é um código como os outros, e pode ser marcada. O sistema não sabe o que o código
  significa, e não equipara o código `AC` à inscrição sem Modalidade (FR-6968).
- **Concorrência concomitante.** O candidato `PPI` também concorre pela ampla na ocupação. O alcance
  lê a Modalidade **declarada** na inscrição, e não as listas em que ela concorre: o `PPI` é
  alcançado, e o `AC` não passa a ser por concorrer na mesma lista que ele (FR-6969).
- **Etapa sem nenhuma inscrição alcançada.** Restrita a `PcD`, e ninguém se inscreveu em `PcD`. A
  Etapa não espera nada: o painel diz *"nenhuma inscrição alcançada"*, ela não bloqueia o que vem
  depois e não exige consolidação (FR-6977).
- **Código que só existe em alguns Perfis.** `PcD` existe em C1 e C2, e não em C3. O alcance `PcD`
  vale onde o código existe, e a tela diz em quais Perfis (UX-731). Nenhum Perfil sem o código ganha
  Modalidade por isso.
- **Código que não existe em Perfil nenhum.** Possível no rascunho, depois de quem elabora renomear
  ou remover a Modalidade. A gravação avisa, e a publicação impede (FR-6963).
- **Perfil acrescentado por Retificação.** Um Perfil novo com `PPI` é alcançado pela Etapa restrita a
  `PPI` desde a publicação da Retificação, sem que o alcance mude: é o que *"Só as inscrições `PPI`"*
  diz.
- **Retificação que amplia depois de consolidada a Etapa.** As inscrições que passam a ser
  alcançadas entram como pendentes. A Etapa deixa de estar inteiramente consolidada até que elas
  tenham Resultado, e os Resultados já consolidados não mudam (FR-6979).
- **Retificação que estreita depois de avaliações feitas.** Recusada enquanto alguma inscrição que
  sairia do alcance tiver Atribuição ou Resultado vigente na Etapa (FR-6980). Para estreitar, a
  presidência remove antes as Atribuições abertas, com motivo; a Atribuição concluída e o Resultado
  não se removem, e por isso o estreitamento fica impossível depois deles.
- **Etapa restrita que o corte governa, ou que habilita ao sorteio.** Impedida na publicação: o
  `HABILITADA` dessas Etapas é o que a ocupação, a convocação e a relação do sorteio contam para
  **todas** as listas, e a Etapa restrita não habilita quem não alcança (FR-6964, D-005).
- **Etapa restrita classificatória, com peso, ou comparada por critério de desempate.** Impedida na
  publicação: a ordem compararia candidatos sob regras diferentes, um com a nota da Etapa e outro sem
  ela (FR-6964, D-005).
- **Etapa restrita como última enumerada pelo marco.** A Heteroidentificação, decisória, pode ser a
  última Etapa que o marco enumera. Para a inscrição da ampla, quem decide se ela concorre é a Prova,
  a última enumerada que a alcança; sem isso, o universo da ordem perderia toda a ampla (FR-6985).
- **Publicação das inscrições (148).** A Heteroidentificação é decisória e eliminatória, como a
  Análise documental, e seria candidata a Etapa de análise da publicação das inscrições. Ela não é
  oferecida: o deferimento publicado vale para todos, e a Etapa restrita deixaria a ampla pendente
  para sempre (FR-6987).
- **Ato histórico.** Um Resultado consolidado sob uma versão do Edital continua lido com o alcance
  daquela versão, ainda que uma Retificação posterior o tenha ampliado (FR-6981).
- **Recurso deferido que muda a Modalidade.** Não existe: a Modalidade da inscrição enviada é
  imutável. O alcance não cria caminho para mudá-la.

## Requirements *(mandatory)*

### Functional Requirements

#### A declaração

- **FR-6960**: A Etapa de avaliação DEVE declarar o seu alcance de uma de duas formas: **todas as
  inscrições** do Edital, ou **só as inscrições de um conjunto não vazio de códigos de Modalidade**.
  O código é o mesmo em todos os Perfis que o têm (D-001).
- **FR-6961**: *"Todas as inscrições"* DEVE ser o padrão, e DEVE ser o que significa toda Etapa que
  existe hoje, em rascunho ou publicada, sem que nenhuma precise ser regravada (D-002).
- **FR-6962**: A gravação DEVE recusar a forma restrita sem nenhum código, com mensagem que diga
  como corrigir. Conjunto vazio não é alcance: é contradição, pela mesma razão que zero avaliações
  por inscrição já é recusado.
- **FR-6963**: A gravação do rascunho DEVE aceitar código que não exista em Perfil nenhum, com aviso;
  a **publicação** e a **Retificação** DEVEM ser impedidas enquanto houver um, com mensagem que
  nomeie a Etapa e o código.
- **FR-6964**: A publicação e a Retificação DEVEM ser impedidas quando uma Etapa restrita for
  **classificatória**, tiver **peso**, for a Etapa comparada por um **critério de desempate**, for
  **pontuada e enumerada por um marco**, for a Etapa **governada pelo corte** de um marco, ou for a **Etapa de habilitação ao sorteio** (D-005). A
  mensagem DEVE nomear a Etapa e a regra que ela contraria.
- **FR-6965**: O código referido pelo alcance de uma Etapa DEVE estar sujeito à mesma coerência de
  denominação que a `044` impõe ao código referido por recorte transversal de Documento Exigido: o
  mesmo código com denominações diferentes em Perfis diferentes impede a publicação e a Retificação
  (D-007).

#### A norma publicada

- **FR-6966**: O alcance DEVE fazer parte do conteúdo normativo publicado do Edital, num degrau novo
  da versão canônica. O conteúdo publicado antes desse degrau DEVE ser lido como *"todas as
  inscrições"*, sem invenção, e o resumo canônico de toda Publicação existente DEVE continuar o
  mesmo (D-002).
- **FR-6967**: O alcance DEVE ser classificado no contrato de mutabilidade como **retificável**, e o
  guardião do contrato DEVE cobri-lo como cobre os demais campos da Etapa (D-006).

#### Quem é alcançado

- **FR-6968**: Uma inscrição DEVE ser alcançada por uma Etapa restrita **se e somente se** ela
  declarar uma Modalidade cujo código esteja no alcance. A inscrição sem Modalidade NÃO DEVE ser
  alcançada por Etapa restrita nenhuma, e a Modalidade cadastrada com código para a ampla DEVE ser
  tratada como qualquer outro código (D-003).
- **FR-6969**: O alcance DEVE ser lido da Modalidade declarada na inscrição, e não das listas em que a
  inscrição concorre por concorrência concomitante.
- **FR-6970**: A versão da norma que decide o alcance DEVE ser a vigente no momento de cada ato
  (distribuir, concluir, registrar Ocorrência, consolidar), como já é para as demais regras da
  Etapa; e o ato já praticado DEVE continuar lido com a versão que citou (FR-6981).

#### A operação

- **FR-6971**: A inscrição fora do alcance de uma Etapa NÃO DEVE participar dela. Esta regra DEVE se
  somar às regras de participação que já existem (eliminação em Etapa anterior, habilitação na
  anterior, faixa do corte), sem revogar nenhuma (D-004).
- **FR-6972**: Para a inscrição que uma Etapa não alcança, essa Etapa NÃO DEVE existir na
  progressão: ela não a elimina, não a habilita, e não é a *"Etapa anterior"* cuja habilitação a
  Etapa seguinte exige. A exigência de habilitação da anterior DEVE ser lida na **última Etapa
  anterior que alcança a inscrição** (D-004).
- **FR-6973**: A distribuição, o rodízio e a atribuição individual DEVEM oferecer só inscrições
  alcançadas, e DEVEM recusar, no servidor, a atribuição de inscrição fora do alcance, com motivo que
  o diga.
- **FR-6974**: Quando a Etapa restrita for governada por uma faixa, a inscrição DEVE participar só se
  for alcançada **e** estiver dentro da faixa. As duas condições são independentes, e nenhuma
  substitui a outra.
- **FR-6975**: O registro de Ocorrência e a conclusão de avaliação DEVEM recusar inscrição fora do
  alcance da Etapa.
- **FR-6976**: A prontidão, o panorama da Etapa e a consolidação DEVEM contar e processar como
  participantes só as inscrições alcançadas. A inscrição fora do alcance DEVE ocupar um estado
  próprio, *"fora do alcance"*, no molde do *"fora do corte"* da `014`, para que a partição continue
  somando todas as inscrições enviadas; e a recusa de tratá-la DEVE dizer esse motivo. Nenhum
  Resultado da Etapa DEVE ser criado para inscrição fora do alcance.
- **FR-6977**: A Etapa restrita sem nenhuma inscrição alcançada DEVE ser apresentada como *"nenhuma
  inscrição alcançada"*, NÃO DEVE exigir consolidação e NÃO DEVE bloquear Etapa, marco, ordem,
  apuração ou convocação que dependa dela.
- **FR-6978**: Os painéis da gestão que contam inscrições por Etapa — o andamento do Edital, o
  Centro, Minhas atividades, a Mesa da comissão e o relatório do Edital — DEVEM contar, para uma
  Etapa restrita, só as inscrições alcançadas.

- **FR-6985**: No universo da ordem de um marco, a Etapa enumerada que não alcança a inscrição NÃO
  DEVE decidir se ela concorre: a participação DEVE ser lida na última Etapa enumerada que a alcança,
  e, quando nenhuma a alcança, como se o marco não enumerasse Etapa (D-004).
- **FR-6986**: Nenhuma pendência de Resultado DEVE ser cobrada de inscrição fora do alcance da
  Etapa — nem na publicação das inscrições, nem no reingresso por recurso, nem na publicação do
  marco.
- **FR-6987**: A Etapa restrita NÃO DEVE ser oferecida nem aceita como a Etapa de análise da
  publicação das inscrições, cujo deferimento vale para todas as inscrições; e, quando ela for
  descartada, a escolha automática da Etapa de análise DEVE continuar como se ela não existisse.

#### A Retificação

- **FR-6979**: A Retificação que **amplia** o alcance — acrescenta código, ou devolve a Etapa a
  *"todas as inscrições"* — DEVE ser aceita. As inscrições que passam a ser alcançadas DEVEM
  participar da Etapa a partir da publicação dela, como pendentes, e os Resultados já consolidados
  NÃO DEVEM mudar.
- **FR-6980**: A Retificação que **estreita** o alcance — tira código, ou restringe uma Etapa que
  alcançava todas — DEVE ser impedida enquanto alguma inscrição que sairia do alcance tiver
  Atribuição ou Resultado vigente nessa Etapa. A mensagem DEVE nomear a Etapa, os códigos e quantas
  inscrições impedem, e DEVE dizer que as Atribuições abertas se removem pela distribuição (D-006).
- **FR-6981**: Todo ato já praticado numa Etapa — Atribuição, avaliação, Ocorrência, Resultado e
  recurso contra ele — DEVE continuar válido e legível pela versão da norma que citou, ainda que uma
  Retificação posterior mude o alcance.

#### O que o candidato e o público leem

- **FR-6982**: O acompanhamento do candidato NÃO DEVE mostrar como passo dele a Etapa que não alcança
  a sua inscrição. Para a inscrição alcançada, e para todo Edital sem Etapa restrita, ele DEVE
  continuar como é hoje.
- **FR-6983**: O documento do Edital DEVE dizer, na Etapa restrita, a quem ela se aplica, pela
  denominação e pelo código de cada Modalidade do alcance, em todas as redações em que o documento
  descreve a Etapa. A Etapa com *"todas as inscrições"* DEVE sair com o texto que sairia antes desta
  feature (D-008).
- **FR-6984**: A Revisão, a página pública do Edital e a tela de Retificação DEVEM dizer o alcance da
  Etapa restrita, com as mesmas palavras do documento.

### Requisitos de experiência

- **UX-730**: A escolha do alcance DEVE ser apresentada como duas opções exclusivas — *"Todas as
  inscrições"* e *"Só as inscrições destas Modalidades"* —, e a lista de códigos DEVE aparecer só com
  a segunda.
- **UX-731**: Cada código oferecido DEVE trazer a denominação e os Perfis que o têm, e a Etapa
  restrita gravada DEVE dizer em que Perfis ela alcança alguém e em quais não alcança ninguém, antes
  da publicação.
- **UX-732**: Os painéis da Etapa restrita DEVEM dizer o recorte junto do número — *"12 inscrições
  alcançadas, de 30"* —, para que o total menor não pareça perda de inscrição.

### Key Entities

- **Etapa de avaliação**: ganha o **alcance** — *todas as inscrições*, ou um conjunto não vazio de
  códigos de Modalidade. É norma publicada, retificável, e vale para todos os Perfis do Edital.
- **Modalidade de concorrência**: continua do Perfil, com código livre. O código passa a ser
  referido também pelo alcance da Etapa, e por isso sujeito à coerência de denominação entre Perfis.
- **Inscrição**: continua declarando uma Modalidade ou nenhuma, imutável depois do envio. É essa
  declaração que o alcance lê.
- **Participação na Etapa**: o conjunto de inscrições que a Etapa trata. Ganha a quarta regra, o
  alcance, ao lado da eliminação anterior, da habilitação na anterior e da faixa do corte.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2310**: **Todo** Edital publicado antes desta feature, recomposto depois dela, produz o mesmo
  resumo canônico e o mesmo documento, byte a byte.
- **SC-2311**: No Edital de três Perfis com a Heteroidentificação restrita a `PPI`, **zero**
  Atribuições, estados de prontidão, Resultados e passos de acompanhamento existem para as inscrições
  fora do alcance, em cada uma das superfícies listadas na FR-6978 e na FR-6982.
- **SC-2312**: No mesmo Edital, a inscrição da ampla habilitada na Prova participa da Análise
  documental com a Heteroidentificação ainda sem Resultado: **zero** inscrições fora do alcance
  ficam *"aguardando a Etapa anterior"* por causa de uma Etapa que não as alcança.
- **SC-2313**: **100%** das Retificações que estreitariam o alcance sobre inscrição com Atribuição ou
  Resultado na Etapa são recusadas, e nenhuma linha de Atribuição, avaliação ou Resultado muda.
- **SC-2314**: O guardião do contrato de mutabilidade não acusa **nenhuma** omissão com o campo novo
  publicado.
- **SC-2315**: Quem elabora declara o alcance de uma Etapa num Edital de 16 Perfis com **uma**
  escolha por código, e não uma por Perfil, em menos de um minuto.
- **SC-2316**: *(humano)* Uma pessoa da CPS ou da comissão de heteroidentificação, lendo só o
  documento publicado do Edital de exemplo, responde corretamente quem passa pela Heteroidentificação
  e quem não passa.

## Assumptions

- **Uma Modalidade por inscrição.** A inscrição declara uma Modalidade ou nenhuma, e a concorrência
  concomitante é da ocupação, e não da inscrição. Se isso mudar, a FR-6969 é o lugar a rever.
- **A Etapa continua do Edital.** O alcance restringe a Etapa existente, e não cria Etapa por Perfil
  nem por Modalidade.
- **O sistema não sabe o que o código significa.** Não há marcador semântico de "cota racial" (a
  `039` não seguiu), e esta spec não cria um: `PPI` é o código que o Edital escolheu.
- **A remoção de Atribuição aberta já existe**, com motivo e trilha. É o caminho que a FR-6980 indica
  para quem precisa estreitar o alcance antes de qualquer conclusão.
- **O efeito do desfecho não muda** até a spec da R-2. Um Edital publicado com Heteroidentificação
  restrita e eliminatória antes dela elimina o candidato desfavorável de todas as listas, como
  qualquer Etapa eliminatória de hoje (D-010).

## Out of Scope

- O efeito por lista do desfecho desfavorável (R-2; decisão P-2) — **spec seguinte**, que depende
  desta.
- A regra de combinação dos pareceres (R-4; decisão P-3) — **spec seguinte**.
- A visibilidade e a recorribilidade da Etapa fora de marco (R-8).
- A orientação no Centro, em Minhas atividades e no portal; a natureza e o degrau novos.
- O vídeo assíncrono (camada B), bloqueado pela P-0.
- O alcance por Perfil, que o barema por curso da `146` pede (D-009).
- A convocação para Etapa e a agenda individual da entrevista.
- Qualquer marcador semântico de Modalidade.

## Dependências

- **Desta spec dependem**: a da R-2 (efeito por lista), a da R-4 (regra de combinação), a da
  orientação e, quando vier, a do alcance por Perfil — todas leem "quem a Etapa alcança" pela regra
  daqui.
- **Esta spec depende de**: a participação na Etapa da `012` e a faixa do corte da `014`, que ela
  estende; o recorte transversal da `044`, cuja coerência de denominação ela reaproveita; a
  vigência do Resultado da `018`, que ela respeita.

## Decisões

### D-001 — O alcance se expressa por código de Modalidade, transversal aos Perfis

A Modalidade é do Perfil e tem código livre, e um Edital multiperfil tem tantas Modalidades `PPI`
quantos Perfis. O alcance diz **códigos**, e alcança a Modalidade daquele código em todo Perfil que a
tem. É a forma que a `044` deu ao recorte transversal do Documento Exigido, pelo mesmo motivo: o que
a Modalidade `PPI` do C1 e a do C2 têm em comum é o código, que é estrutural depois de publicado.

*Descartados:*
- **Pares Perfil × Modalidade.** Multiplicaria a declaração no caso comum — 16 Perfis, 16 marcações
  para dizer uma coisa — e não acompanharia o Perfil acrescentado por Retificação, que a norma
  ("os candidatos `PPI`") alcança.
- **Marcador semântico na Modalidade** ("esta é cota racial"). Seria decidir o significado do código
  no lugar do Edital, que é a decisão que a `039` não tomou.

### D-002 — "Todas as inscrições" é a ausência, e não uma lista

O padrão não se escreve: é a ausência de alcance declarado. Assim todo Edital de hoje significa,
depois desta spec, exatamente o que significava, e o degrau novo da versão canônica é conversão sem
invenção, no molde dos degraus que acrescentaram campos à Etapa e ao Documento Exigido. *Descartado:*
gravar em toda Etapa a lista de todos os códigos — mudaria o significado quando uma Retificação
acrescentasse Modalidade, e mudaria o resumo canônico do acervo.

### D-003 — A inscrição sem Modalidade nunca é alcançada por Etapa restrita

A ausência de Modalidade é a ampla concorrência, e a heteroidentificação, que motiva a spec, nunca a
alcança. O alcance não oferece "ampla concorrência" como opção, porque não há Edital na amostra com
Etapa só para a ampla, e a Constituição recusa estrutura antes da regra. A Modalidade cadastrada com
código para a ampla é só um código: o sistema não sabe o que ele significa.

### D-004 — A Etapa que não alcança a inscrição não existe na progressão dela

O alcance é uma quarta regra de participação, e se soma às três que existem. A consequência que mais
importa está na habilitação da anterior: lida literalmente, ela pediria à inscrição da ampla um
Resultado numa Etapa que nunca a avaliará, e a deixaria parada para sempre. A anterior que conta é a
última que a alcança. *Descartado:* tratar a inscrição não alcançada como **habilitada** na Etapa —
o sistema registraria um juízo que ninguém fez, e o `HABILITADA` é o que a ocupação conta.

### D-005 — A Etapa restrita não decide nada que valha para todas as listas

Uma Etapa restrita não pode compor a ordem (classificatória, com peso, comparada por desempate,
pontuada e enumerada por marco), nem ser a Etapa cujo `HABILITADA` a ocupação, a convocação ou o
sorteio contam (governada pelo corte, habilitação ao sorteio), nem a Etapa cujo deferimento a
publicação das inscrições publica para todos. Nesses papéis ela decidiria por todos com um juízo que só alguns receberam.
A heteroidentificação dos Editais lidos não ocupa nenhum deles: é decisória, e a Etapa governada é a
Análise documental. *Descartado:* admitir e definir o que vale para quem não é alcançado — seria
inventar regra que nenhum Edital escreveu.

### D-006 — O alcance é retificável, e o que protege a avaliação feita é a recusa de estreitar

O alcance diz **quem passa pela Etapa**, da mesma natureza do recorte do Documento Exigido, que a
`044` deixou retificável. Ampliar não desfaz nada: acrescenta pendentes. Estreitar sobre inscrição já
atribuída ou avaliada tiraria da Etapa um ato praticado sob a norma publicada, e é recusado. É a
razão que a `048` já deu para recusar a regra de corte que nasce sobre Etapa com Resultado, aplicada
ao alcance. *Descartados:* **não retificável** — deixaria sem correção o erro de composição mais
provável, esquecer um código; e **estreitar encerrando as Atribuições em silêncio** — a Constituição
pede que o efeito sobre múltiplos objetos seja explícito antes do ato.

### D-007 — A coerência de denominação vale para o código que o alcance refere

A `044` impede a publicação quando um código referido por recorte transversal tem denominações
diferentes entre Perfis, porque o recorte afirma que o código significa o mesmo em todos. O alcance
afirma o mesmo, e herda a regra, sem estendê-la a código que nada refere.

### D-008 — O documento fala do alcance só quando ele restringe

A Etapa para todos sai com o texto de hoje, e por isso o acervo se recompõe idêntico. A Etapa
restrita ganha uma frase com a denominação e o código, nas redações que descrevem a Etapa. Um Edital
que diz *"Etapa de heteroidentificação"* sem dizer a quem se aplica é o defeito de leitura que esta
spec existe para fechar.

### D-009 — O alcance por Perfil fica para a spec que o pedir

O barema por curso varia por Perfil, e não por Modalidade. Esta spec não o especifica, e não fecha o
caminho: a forma do alcance admite, depois, uma segunda dimensão sem reescrever a primeira.

### D-010 — O desfecho da Etapa restrita produz o efeito de hoje

A spec não toca a progressão além da FR-6972. O `ELIMINADA` de uma Etapa restrita tira o candidato de
todas as listas, como hoje, até a spec da R-2. Não se impede a publicação por isso: o usuário decidiu
a R-2 em 13/11, e ela é a próxima entrega. O risco fica registrado aqui e nas *Assumptions*.
