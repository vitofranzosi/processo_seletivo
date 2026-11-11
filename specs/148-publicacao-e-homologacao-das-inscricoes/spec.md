# Feature Specification: Publicação e homologação das inscrições

**Feature Branch**: `claude/gps-inscricoes-publicacao-93355f`, sobre a `main` em `d3e98a89`

**Created**: 2026-11-11

**Status**: Spec, plano, tarefas e implementação em 11/11/2026. Seis questões (P-1 a P-6, ao fim)
esperam validação institucional, e nenhuma bloqueia o que foi entregue: cada uma tem um padrão
conservador escrito.

**Input**: *"Evoluir o GPS para contemplar a publicação e homologação das inscrições,
independentemente da modalidade de classificação: relação de inscrições recebidas, resultado
preliminar da análise das inscrições com recurso, e homologação final — aproveitando o que existe,
acrescentando só o necessário, sem motor de workflow, sem estado derivável persistido, sem duplicar
publicação nem recurso, e sem acoplar a relação de inscritos ao congelamento do sorteio."* O pedido
completo e o diagnóstico estão em [research.md](research.md).

> **Faixa de identificadores.** Esta spec usa os requisitos funcionais de cinco mil e quatrocentos a
> cinco mil quatrocentos e cinquenta e nove, os critérios de mil e setecentos a mil setecentos e
> dezenove e os requisitos de experiência de quatrocentos e sessenta a quatrocentos e sessenta e
> nove. Os números não usados ficam livres. As decisões reiniciam em `D-001`, e `D-001` a `D-010`
> respondem, na ordem, às dez questões do §7 do pedido.
>
> O teto foi medido em 11/11/2026, na `main` e em todas as branches remotas: requisito cinco mil
> trezentos e vinte e três, critério mil seiscentos e sessenta e seis, UX quatrocentos e quarenta e
> quatro. A `147` está no PR #466, aberto. Por isso esta é a `148`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature;
> decisão de outra feature, pelo assunto, nunca pelo identificador.

## Por que esta feature existe

Os Editais publicam, antes de classificar, atos sobre as **inscrições**: a relação das que foram
recebidas, o resultado preliminar da análise (deferidas e indeferidas), o prazo de recurso e a
homologação final. O GPS não tem nenhum desses atos, e a comissão os faz fora — numa planilha
copiada da tela de inscrições, num PDF montado à mão, numa lista que ninguém confere contra o
sistema. A `021` publicou a relação de habilitados **do sorteio** e deixou escrito que a relação de
inscritos é *"artefato universal, e é outra feature"*. Esta é ela.

**O diagnóstico mostrou que quase tudo existe** ([research.md](research.md) §2). A análise das
inscrições **já é** uma Etapa decisória e eliminatória: o avaliador abre a inscrição na Mesa, vê os
documentos, conclui *Deferido* ou *Indeferido* com motivo; a consolidação grava o `ResultadoEtapa`;
o recurso contra o resultado de Etapa existe, é julgado, e a correção sucede o resultado; as Etapas
seguintes e o sorteio já leem só quem foi habilitado. **Faltam duas coisas, e só duas:**

1. **o ato coletivo** — a publicação que diz, de uma vez e para todos, quem consta, e que fica
   preservada como foi publicada;
2. **o fato que torna o resultado da análise visível e recorrível** — hoje só a divulgação de um
   marco de classificação o faz, e a Etapa de análise não pertence a marco nenhum.

**Uma regra muda, e as outras ficam.** Nenhum estado novo na inscrição, nenhum segundo recurso,
nenhuma configuração nova no Edital, nenhum vínculo automático com o sorteio.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Publicar a relação de inscrições recebidas (Priority: P1)

Encerrado o período de inscrições, quem publica abre "Publicações das inscrições" no Edital, vê
quantas inscrições serão contempladas por Perfil, confere a prévia, escolhe a autoridade signatária
e publica. A relação passa a ser consultável no portal, em página e PDF.

**Why this priority**: é o ato que todo Edital pode publicar, inclusive o mais simples, e é o que
hoje mais gera planilha paralela. Entrega valor sozinho e não depende de análise.

**Independent Test**: com um Edital de inscrições encerradas, publicar a relação pela gestão e
consultá-la no portal sem conta; conferir que o documento traz protocolo e nome de cada inscrição
recebida e nenhum outro dado pessoal.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com inscrições enviadas e período encerrado, **When** quem publica
   abre a prévia da relação de recebidas, **Then** vê o total e a contagem por Perfil, o que
   acontece ao confirmar, e que nada foi gravado.
2. **Given** a prévia, **When** confirma com a autoridade signatária, **Then** a relação é publicada,
   congelada, com PDF gravado, e aparece na página pública da seleção.
3. **Given** o período de inscrições ainda aberto, **When** abre a tela, **Then** ela diz até quando
   esperar e não oferece a publicação.
4. **Given** a relação publicada, **When** o candidato abre a própria inscrição, **Then** lê que ela
   **consta como recebida** e que recebida não quer dizer aceita.

---

### User Story 2 — Publicar o resultado preliminar da análise e receber recursos (Priority: P1)

A comissão analisa as inscrições pela Etapa decisória que o Edital já declara (por exemplo
"Análise documental — Deferido/Indeferido") e consolida. Quem publica escolhe essa Etapa, escolhe no
Cronograma o período de recurso que o Edital publicou, confere a prévia — deferidas e indeferidas
por Perfil, e as pendências — e publica o resultado preliminar. Cada candidato vê a própria
situação e, se indeferido, o motivo e a ação de recorrer até o fim do prazo.

**Why this priority**: é o ato que transforma a análise em direito exercível — sem ele o indeferido
não sabe que foi indeferido, nem por quê, nem até quando recorrer.

**Independent Test**: com uma inscrição indeferida, publicar o preliminar, entrar como o candidato,
ver o motivo e interpor recurso; entrar como outro candidato deferido e não ver o motivo alheio.

**Acceptance Scenarios**:

1. **Given** inscrições sem conclusão na Etapa de análise, **When** abre a prévia, **Then** ela diz
   quantas faltam e não oferece a publicação.
2. **Given** todas concluídas e consolidadas, **When** publica com o período de recurso escolhido,
   **Then** o ato publica protocolo e nome das deferidas e só a **quantidade** de indeferidas, por
   Perfil, com o prazo de recurso impresso.
3. **Given** o preliminar publicado, **When** o candidato indeferido abre a inscrição, **Then** lê
   "Inscrição indeferida", o motivo, a data-limite e a ação de recorrer.
4. **Given** o prazo encerrado, **When** o mesmo candidato tenta recorrer, **Then** a ação não aparece
   e a interposição direta é recusada.
5. **Given** um recurso deferido com correção, **When** a decisão é gravada, **Then** o resultado da
   inscrição é sucedido pelo mecanismo existente, sem nada específico desta feature.

---

### User Story 3 — Homologar as inscrições (Priority: P1)

Encerrado o prazo e julgados os recursos, quem publica abre a prévia da homologação. O sistema
projeta a situação vigente — já com as correções — e impede a publicação enquanto houver recurso
sem decisão, reavaliação determinada não cumprida ou prazo correndo. Publicada, a homologação é a
relação final das inscrições homologadas, e é dela que a continuidade da seleção parte.

**Why this priority**: fecha o ciclo e é o ato que o cronograma real nomeia; sem ele a comissão
volta à planilha justamente no ato final.

**Independent Test**: depois de um recurso deferido, publicar a homologação e conferir que a
inscrição antes indeferida consta como homologada, que o preliminar continua legível como foi
publicado e que a homologação foi recusada enquanto o recurso estava pendente.

**Acceptance Scenarios**:

1. **Given** recurso pendente contra resultado da Etapa de análise, **When** abre a prévia da
   homologação, **Then** a pendência é nomeada e a publicação não é oferecida.
2. **Given** nenhuma pendência, **When** publica, **Then** a homologação lista as homologadas por
   Perfil, conta as não homologadas e sucede o preliminar, que continua consultável.
3. **Given** a homologação publicada, **When** o candidato abre a inscrição, **Then** lê "Inscrição
   homologada" — ou "Inscrição não homologada", com o motivo.
4. **Given** um Edital cuja análise não prevê recurso, **When** a comissão publica direto a
   homologação, **Then** ela é aceita sem preliminar.

---

### User Story 4 — Corrigir uma publicação e perceber quando ela envelheceu (Priority: P2)

Depois de publicada, uma relação pode deixar de corresponder à situação vigente — um recurso
julgado depois, uma Retificação que reabriu o período, um erro da comissão. O sistema não muda o
ato: mostra que ele **difere** da situação atual, diz quantas inscrições mudaram, e permite publicar
um ato sucessor da mesma natureza, com motivo obrigatório. O anterior continua no mesmo endereço e
passa a dizer que foi sucedido.

**Why this priority**: é a garantia de integridade histórica; é rara, e por isso P2.

**Independent Test**: publicar a homologação, julgar depois um recurso que muda uma inscrição, ver o
aviso de divergência na gestão, publicar o sucessor com motivo e conferir os dois no portal.

**Acceptance Scenarios**:

1. **Given** um ato vigente e uma mudança posterior, **When** abre a tela, **Then** lê que o ato
   publicado difere da situação atual e em quantas inscrições.
2. **Given** a correção, **When** tenta publicar a mesma natureza sem motivo, **Then** é recusado.
3. **Given** o sucessor publicado, **When** alguém abre o ato anterior no portal, **Then** lê que ele
   foi sucedido, por qual, e o motivo.

---

### User Story 5 — Edital sem homologação formal (Priority: P2)

Um Edital que não prevê análise de inscrições não precisa configurar nem publicar nada: a seleção
segue como hoje. Se quiser, publica só a relação de recebidas. Se o Edital homologa todas as
recebidas sem análise individual, publica a homologação **sem Etapa** — permitido apenas quando o
Edital não tem Etapa decisória eliminatória, para que um ato não contradiga decisões individuais.

**Independent Test**: Edital só com Etapa pontuada segue de ponta a ponta sem tocar nesta tela;
publicar a homologação sem análise num Edital assim; tentar o mesmo num Edital com Etapa decisória e
ser recusado.

### A jornada inteira

```text
inscrições encerradas ─► relação de recebidas  (opcional)
                         │
análise pela Mesa ──────►├─► resultado preliminar ─► recursos (mecanismo existente) ─► homologação
(Etapa decisória)        │                                                              │
                         └─────────────────────────── homologação direta ───────────────┤
                                                                                        ▼
                                     Etapas seguintes, marcos, sorteio — lendo o mesmo ResultadoEtapa
```

### Edge Cases

- **Candidato com duas inscrições** (dois Perfis): aparece uma vez em cada Perfil, cada uma com o
  seu protocolo; a situação de uma não alcança a outra.
- **Cotista**: a inscrição é uma só, e aparece uma vez — a lista de concorrência não divide a
  inscrição (`D-009`).
- **Inscrição enviada depois da relação publicada** — só possível se uma Retificação reabriu o
  período: a relação vigente passa a divergir; a correção é um sucessor.
- **Inscrição alterada depois da publicação**: impossível — a enviada é imutável por gatilho (A-03);
  o teste o prende.
- **Retificação que renomeia o Perfil**: o ato publicado conserva o nome que publicou; os bytes são
  congelados.
- **Resultado sucedido por recurso depois da homologação**: o ato não muda; a gestão mostra a
  divergência; a correção é um sucessor com motivo (US4).
- **Nenhuma inscrição deferida num Perfil**: o Perfil aparece com "Nenhuma inscrição deferida" e a
  contagem de indeferidas.
- **Edital sem inscrição enviada**: nada a publicar — a prévia diz e não oferece.
- **Período de recurso escolhido já encerrado**: recusado — publicar com prazo vencido suprimiria o
  recurso.
- **Preliminar sem prazo de recurso**: permitido, declarando que o Edital não prevê recurso contra a
  análise; a homologação deixa de esperar prazo.
- **Duas abas publicando ao mesmo tempo**: a segunda é recusada pela prévia assinada ou pela
  unicidade do sucessor.
- **Etapa de análise também enumerada num marco de classificação**: as janelas se somam e vale a
  mais generosa, como a `018` já faz entre marcos.
- **Regressão de natureza** (preliminar depois da homologação, recebidas depois do preliminar):
  recusada.

## Requirements *(mandatory)*

### Functional Requirements

#### O ato

- **FR-5400**: O sistema MUST permitir publicar, por Edital, a **Publicação das inscrições** em uma
  de três naturezas: *relação de inscrições recebidas*, *resultado preliminar da análise das
  inscrições* e *homologação das inscrições*.
- **FR-5401**: A publicação MUST ser opcional: nenhum fluxo existente — avaliação, classificação,
  sorteio, convocação, encerramento — MUST passar a exigi-la.
- **FR-5402**: A publicação MUST ser recusada enquanto o período de inscrições estiver em curso ou
  não tiver começado, dizendo até quando esperar.
- **FR-5403**: A publicação MUST ser recusada quando não houver inscrição enviada no Edital.
- **FR-5404**: O universo de toda natureza MUST ser o das inscrições enviadas do Edital; rascunho
  MUST NOT constar.
- **FR-5405**: As naturezas MUST ter ordem de sentido único — recebidas, preliminar, homologação —,
  e o sistema MUST recusar natureza anterior à do ato vigente.
- **FR-5406**: Cada Edital MUST ter uma única cadeia de publicações das inscrições: uma raiz e, para
  cada publicação, no máximo uma sucessora.
- **FR-5407**: Publicar a **mesma** natureza do ato vigente MUST exigir motivo escrito, gravado no
  ato (correção); publicar natureza seguinte MUST NOT exigi-lo.

#### A análise

- **FR-5408**: O preliminar e a homologação com análise MUST basear-se numa Etapa do Edital
  **decisória e eliminatória** da versão vigente, escolhida por quem publica; havendo uma só, MUST
  vir escolhida.
- **FR-5409**: Toda publicação da cadeia que tenha Etapa MUST usar a mesma Etapa da primeira que a
  teve.
- **FR-5410**: A situação de cada inscrição MUST ser lida do `ResultadoEtapa` **vigente** daquela
  Etapa: habilitada é deferida, eliminada é indeferida. O sistema MUST NOT admitir situação digitada.
- **FR-5411**: O sistema MUST recusar o preliminar e a homologação com análise enquanto houver
  inscrição enviada sem resultado vigente na Etapa, dizendo quantas.
- **FR-5412**: A homologação **sem** análise MUST ser permitida apenas quando o Edital não tiver
  Etapa decisória eliminatória, e MUST contemplar todas as inscrições enviadas como homologadas.

#### O recurso

- **FR-5413**: Ao publicar o preliminar, quem publica MUST escolher entre um Evento do Cronograma da
  versão vigente como período de recurso, ou declarar que o Edital não prevê recurso contra a
  análise. A escolha MUST ficar congelada no ato, com o nome e o término do Evento.
- **FR-5414**: O sistema MUST recusar Evento cujo término já passou.
- **FR-5415**: Publicado o preliminar, o titular MUST passar a ver o próprio resultado vigente da
  Etapa de análise, com o motivo, pelo mecanismo de resultados visíveis existente.
- **FR-5416**: O recurso contra o indeferimento MUST ser o recurso existente contra resultado de
  Etapa; esta feature MUST NOT criar alvo, peça, julgamento ou trilha de recurso.
- **FR-5417**: A janela desse recurso MUST ir do instante da publicação do preliminar ao término do
  Evento escolhido; declarado "não prevê recurso", a interposição MUST ser recusada por esta via; e,
  havendo outra janela pertinente (marco que enumere a mesma Etapa), MUST valer a mais generosa.
- **FR-5418**: A homologação com análise MUST ser recusada enquanto houver, contra resultado da
  Etapa de análise, recurso sem decisão e não inadmitido, reavaliação determinada não cumprida, ou
  prazo de recurso do preliminar correndo — cada impedimento nomeado, com o instante quando houver.

#### Conteúdo, documento e histórico

- **FR-5419**: O conteúdo público MUST ser agrupado por Perfil, com o nome publicado na versão que o
  ato cita, e MUST expor, por inscrição contemplada, **somente** protocolo e nome.
- **FR-5420**: Na relação de recebidas MUST constar toda inscrição enviada; no preliminar e na
  homologação MUST constar nominalmente só a deferida (homologada), e a indeferida MUST ser apenas
  **contada** por Perfil.
- **FR-5421**: O conteúdo público MUST NOT expor CPF, e-mail, telefone, identificador interno,
  modalidade declarada, motivo do indeferimento nem resultado de outra Etapa.
- **FR-5422**: A ordem das inscrições dentro do Perfil MUST ser determinística: nome sem distinção
  de caixa e acento, depois protocolo.
- **FR-5423**: O sistema MUST congelar, no instante da publicação, os bytes canônicos do conteúdo e o
  seu resumo SHA-256, e MUST gravar uma linha por inscrição do universo com a situação publicada e o
  `ResultadoEtapa` de onde ela veio.
- **FR-5424**: O sistema MUST gerar o PDF do ato **uma vez**, a partir dos mesmos bytes que a página
  lê, gravá-lo com o seu resumo, e servi-lo dos bytes gravados.
- **FR-5425**: A publicação, as suas linhas e o documento MUST ser imutáveis: a aplicação, o gatilho
  de banco e o privilégio ausente da role de runtime recusam alteração e exclusão.
- **FR-5426**: O ato MUST registrar quem publicou, quando, a versão do Edital citada, a autoridade
  signatária (nome, cargo, ato de nomeação) e a unidade, congelados.
- **FR-5427**: O sistema MUST derivar, para o ato vigente, se ele **difere** da situação atual — e em
  quantas inscrições —, sem alterar o ato.
- **FR-5428**: A consulta pública MUST oferecer cada ato da cadeia, inclusive os sucedidos, dizendo
  qual é o vigente, por qual cada um foi sucedido e o motivo.

#### Operação

- **FR-5429**: Publicar MUST exigir a capacidade de publicar resultado (`resultado:publicar`) e o
  Edital no escopo institucional do ator; consultar a tela MUST admitir também a auditoria.
- **FR-5430**: A publicação MUST ser idempotente pela chave do pedido, serializada com os demais
  comandos do Processo, e MUST recusar a confirmação quando a projeção ou a cadeia mudaram desde a
  prévia.
- **FR-5431**: A publicação MUST gravar a trilha de auditoria com ator, operação, ato, versão citada
  e sucessão, sem dado pessoal.
- **FR-5432**: A tela da gestão MUST mostrar, antes da confirmação: a natureza, a Etapa, o prazo, o
  total e a contagem por Perfil, as pendências que impedem, o aviso de sucessão, o que acontece ao
  confirmar e qual documento ficará disponível.
- **FR-5433**: A tela MUST oferecer só as naturezas permitidas no estado atual, e dizer por que as
  demais não estão.

#### Candidato

- **FR-5434**: A situação da inscrição no portal MUST distinguir: inscrição enviada (nada publicado);
  inscrição **recebida** (consta na relação de recebidas); inscrição **deferida** (preliminar);
  inscrição **indeferida** (preliminar, com motivo); inscrição **homologada**; inscrição **não
  homologada** (com motivo) — cada uma com a data e o caminho até o ato publicado.
- **FR-5435**: A ação de recorrer MUST aparecer para o indeferido enquanto o prazo correr, com a
  data-limite, e MUST NOT aparecer depois.
- **FR-5436**: A situação das etapas posteriores — classificação, convocação — MUST continuar
  prevalecendo sobre a das inscrições, pela precedência existente.

#### Compatibilidade

- **FR-5437**: Editais já publicados MUST continuar operáveis sem nenhuma publicação das inscrições,
  e nenhuma migration MUST alterar dado existente.
- **FR-5438**: A relação de habilitados do sorteio MUST continuar projetada e congelada pelas regras
  da `021`, sem ler nem exigir a publicação das inscrições.

### Requisitos de experiência

- **UX-460**: A tela da gestão MUST ser uma só — "Publicações das inscrições" —, alcançável da tela
  de Inscrições do Edital, com o histórico, o próximo ato possível e a prévia no mesmo lugar.
- **UX-461**: O termo "homologação" MUST aparecer sempre qualificado — "homologação das inscrições"
  — para não se confundir com a homologação do Edital.
- **UX-462**: A tela MUST dizer, em uma frase, a diferença entre recebida, deferida e homologada.
- **UX-463**: O candidato MUST ler a própria situação sem jargão: "recebida não quer dizer aceita";
  "pode mudar até a homologação"; "você pode recorrer até …".
- **UX-464**: A página pública do ato MUST ser legível a 375 px sem rolagem horizontal da página.
- **UX-465**: Nenhum estilo ou script inline (CSP); toda classe nova com regra na folha.

### Key Entities

- **Publicação das inscrições**: ato público por Edital, com natureza, Etapa de análise (quando há),
  período de recurso congelado (no preliminar), versão citada, autoridade e unidade, conteúdo
  canônico, resumo, documento e sucessão com motivo.
- **Inscrição na publicação**: uma linha por inscrição enviada do universo, com a situação publicada
  (recebida, deferida, indeferida) e o resultado de origem; é a projeção individual, nunca pública.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1700**: A comissão publica as três naturezas pela interface, sem shell, sem banco e sem
  planilha, num Edital com análise e recurso.
- **SC-1701**: Um Edital sem Etapa decisória atravessa avaliação, classificação e publicação de
  resultado sem abrir a tela desta feature.
- **SC-1702**: Nenhum documento publicado contém CPF, e-mail, telefone, identificador interno,
  modalidade ou motivo — verificado por teste sobre os bytes e sobre o PDF.
- **SC-1703**: Alterar, excluir ou renumerar a publicação, suas linhas ou seu documento é recusado
  pela aplicação e pelo banco.
- **SC-1704**: O candidato indeferido vê o motivo e interpõe recurso pela própria área; outro
  candidato não alcança o resultado alheio.
- **SC-1705**: A homologação reflete a correção por recurso e o preliminar continua legível com o
  conteúdo original, byte a byte.
- **SC-1706**: Para o mesmo Edital, o conjunto de inscrições habilitadas que a relação do sorteio
  projeta pela Etapa de análise é o conjunto homologado — mesma fonte, sem acoplamento.
- **SC-1707**: A publicação repetida com a mesma chave devolve o mesmo ato; a confirmação com prévia
  obsoleta é recusada.
- **SC-1708**: A tela pública do ato e a da gestão funcionam a 375 px e não violam a CSP.

## Decisões

### D-001 — Um agregado, três naturezas

**Pergunta 1 do pedido: quais atos precisam ser entidades próprias.** Um só agregado novo,
`PublicacaoDasInscricoes`, no app `divulgacao`, com natureza `RECEBIDAS`, `PRELIMINAR` ou
`HOMOLOGACAO`, e a sua projeção individual `InscricaoNaPublicacao`. A decisão sobre cada inscrição
**não** é entidade nova: é o `ResultadoEtapa` da Etapa decisória. O ato é próprio porque nenhum
existente serve: `PublicacaoResultado` divulga um ato de ordenação, por marco e lista, e a 017 recusou
o publicável genérico; a `RelacaoDeHabilitados` é compromisso do sorteio; o aviso da 066 aponta para
um ato e não é um. Mora em `divulgacao` porque é divulgação e lê `resultados`; em `inscricoes`
criaria ciclo de importação.

**Vocabulário.** "Homologação" já nomeia, no código e na tela, o ato sobre a revisão do Edital. Aqui
é sempre "homologação **das inscrições**" (UX-461), e a natureza se chama `HOMOLOGACAO` dentro de um
agregado cujo nome já diz de quê.

### D-002 — O cronograma se cita no ato, não se configura

**Pergunta 2.** O Cronograma do GPS governa só o período de inscrições, e o tipo do Evento é texto
livre que nada lê. Tipá-lo reinterpretaria conteúdo publicado. A ligação é feita **no ato**: o
período de inscrições é a trava (FR-5402), e o período de recurso do preliminar é um Evento que
quem publica escolhe e que fica congelado (FR-5413). Nenhuma configuração nova no Edital, e o
Evento continua sendo a fonte normativa da data.

### D-003 — O recurso é o que existe, com duas adaptações

**Pergunta 3.** O alvo é o `ResultadoEtapa`, que o recurso já aceita. As adaptações mínimas, ambas
de leitura: (a) o preliminar ou a homologação vigente **autoriza** a visibilidade do resultado da
Etapa de análise ao titular, ao lado da divulgação de marco que já autoriza (`resultados_visiveis`);
(b) a janela pertinente ao resultado da Etapa de análise inclui a do preliminar (`_janelas_pertinentes`).
Peça, admissibilidade, instrução, julgamento, correção e trilha ficam intocados.

### D-004 — A homologação é projeção dos vigentes, e espera a disputa acabar

**Pergunta 4.** A homologação não consolida nada: ela **publica** a situação vigente da Etapa, que o
recurso já corrigiu por sucessão. O que ela acrescenta é a recusa enquanto a disputa não acabou —
recurso sem decisão, reavaliação não cumprida, prazo correndo —, com as mesmas funções que impedem
a definitiva de um marco.

### D-005 — A homologação e a relação do sorteio leem a mesma fonte, e não se tocam

**Pergunta 5.** A relação de habilitados já filtra pelo `ResultadoEtapa` habilitado da Etapa que o
método declara. Declarando ali a Etapa de análise, as duas respondem igual (SC-1706). Acoplar —
exigir a homologação antes de congelar, ou congelar ao homologar — mudaria a regra de congelamento
da 021 e tornaria a homologação obrigatória para Editais que sorteiam sem analisar. O que a operação
deve fazer — homologar antes de congelar — é ordem de trabalho, e o Cronograma do Edital a diz.

### D-006 — Bytes congelados, linhas por inscrição, sucessão com motivo

**Pergunta 6.** O ato congela conteúdo canônico, resumo e PDF, e grava uma linha por inscrição com o
resultado de origem. Corrigir é suceder: mesma natureza exige motivo; o anterior continua no mesmo
endereço, dizendo por qual foi sucedido. A **divergência** entre o ato vigente e a situação atual é
derivada pela comparação das linhas com a projeção de agora (FR-5427), e nunca gravada. Publicação
equivocada se trata assim; não há despublicar.

### D-007 — Editais sem deferimento individual

**Pergunta 7.** Três caminhos, nenhum obrigatório: não publicar nada; publicar só a relação de
recebidas; ou publicar a homologação sem análise, que contempla todas as recebidas — permitida só
sem Etapa decisória eliminatória no Edital, para que o ato coletivo não contradiga decisão
individual (FR-5412).

### D-008 — Escopo e compatibilidade

**Pergunta 8.** O comando filtra o Processo e o Edital pelo escopo institucional do ator, como a
divulgação de resultado; fora dele, 404. A capacidade é `resultado:publicar`, a do mesmo papel que já
divulga resultados (P-4). Nada é exigido de Editais existentes; a migration só cria tabelas.

### D-009 — Por Perfil; a lista não divide a inscrição

**Pergunta 9.** A análise é por inscrição, e a inscrição é uma, num Perfil, com no máximo uma
modalidade. O ato agrupa por Perfil e não reparte por lista: o cotista consta uma vez. Repartir por
lista, como o sorteio faz, publicaria a modalidade declarada — dado que pode ser sensível (PcD) — sem
necessidade para a finalidade do ato.

### D-010 — O que é público

**Pergunta 10.** Público: protocolo e nome de quem consta (recebida; deferida; homologada), a
contagem de indeferidas por Perfil, Etapa, prazo, autoridade e resumo. Só do titular: a própria
situação, o motivo, a modalidade e o recurso. Nunca: CPF, e-mail, telefone, identificador interno. É
a regra da divulgação de resultado (017), que não nomeia publicamente quem foi eliminado; publicar
os indeferidos nominalmente é escolha institucional (P-1).

## Questões para validação institucional

- **P-1 — Indeferidos nominalmente?** Padrão: só contados. Alternativa: listar por protocolo, sem
  nome. Custo: uma coluna no ato e uma decisão de LGPD.
- **P-2 — Modalidade na relação?** Padrão: não publicada. Alternativa: coluna "concorre também em".
  Custo: dado potencialmente sensível no ato público.
- **P-3 — Prazo pelo Evento ou por dias?** Padrão: o Evento do Cronograma. Alternativa: declaração
  em dias na Etapa, como o marco faz. Custo: campo normativo novo.
- **P-4 — Capacidade própria?** Padrão: `resultado:publicar`. Alternativa: `inscricoes:publicar`.
  Custo: papel, treinamento e mapa de acessos.
- **P-5 — Aviso por e-mail ao publicar?** Padrão: não nesta feature. Alternativa: origem nova nos
  avisos da 066.
- **P-6 — Recurso contra a relação de recebidas** (inscrição que o candidato diz ter enviado e não
  consta)? Padrão: fora — a enviada consta por construção; o caso é de suporte, não de recurso.

## Assumptions

- A análise das inscrições, quando o Edital a prevê, é declarada como Etapa decisória eliminatória —
  o que o `seed_demo` e o caso real de 07/11 já fazem.
- O Cronograma publicado contém o período de recurso contra a análise quando o Edital o prevê.
- O protocolo da inscrição é identificador público, como a 017 e a 021 já o tratam.

## Fora do escopo

- Cancelamento ou desistência de inscrição — não existe no sistema e não nasce aqui.
- Aviso por e-mail ao publicar (P-5).
- Tipar Eventos do Cronograma ou fazê-lo governar atos.
- Publicação coletiva do resultado de Etapa **pontuada** — continua sendo a do marco.
- Exportação da relação em planilha.
- Recurso contra a relação de recebidas (P-6).
