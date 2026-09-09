# Feature Specification: Sorteio público auditável

**Feature Branch**: `claude/spec-021-sorteio-auditavel`

**Created**: 2026-09-08

**Status**: Draft

**Input**: Quatro dos sete Editais da amostra selecionam por sorteio, e o sistema não tem o fato que
alimenta o resultado. Hoje o sorteio acontece em software de terceiro, cuja lista de entrada ninguém
publicou canonicamente, e a garantia oferecida ao cidadão é uma linha no rodapé: *"observar o campo
'Semente utilizada'"*. Esta feature traz o sorteio para dentro do certame — com o universo
congelado antes da semente, a semente vinda de fora, e a ordem reproduzível por qualquer pessoa.

> **Frase que governa:** publicada e congelada a relação que constitui o universo, uma ocorrência
> futura e previamente determinada de fonte pública externa fixa a semente; com o manifesto público,
> qualquer pessoa reproduz a mesma ordem.

> **E a frase que mantém o corte:** sorteio não habilita, não elimina e não ocupa vaga. Ele
> **constitui uma ordem completa** sobre a relação congelada; corte, cotas, progressão e convocação
> **consomem** essa ordem.

Prompt de origem: `doc/prompt/021-sorteio-publico-auditavel.md`. Evidência: os Editais 77/2026,
76/2026, 57/2026 e 28/2026, lidos em 08/09/2026;
`doc/descoberta-escopo-sorteio-e-anexos.md` §Parte 1; `doc/avaliacao-de-capacidade-editais-2026-09-08.md`.

---

## 1. O que já está fechado, e que a 021 consome

### 1.1 A inversão que organiza a feature

```text
ERRADO   o universo do AtoDeOrdenacao serve de compromisso
         → o ato é append-only e nasce na emissão; ele não prova nada sobre o instante
           anterior à semente

CERTO    Publicação da relação de habilitados        ← compromisso, anterior à semente
                     ↓ identidade + resumo, imutáveis
         AtoDeOrdenacao constituído por sorteio      ← resultado, posterior à semente
```

A relação publicada é o compromisso temporal; o ato é o resultado dele. É por isso que não existe
entidade "lote de sorteio": a relação publicada já ocupa esse lugar.

### 1.2 O que o repositório entrega, e que esta feature não constrói

- **Integridade e resumo canônico** (`shared/canonical.py`): a chave do sorteio e o resumo da
  relação não inventam serialização.
- **Trilha append-only** (`auditoria`): ator, ato, estados anterior e posterior, motivo e correlação.
- **Sucessão de ordem com motivo** (`AtoDeOrdenacao.ato_anterior` + `motivo_da_sucessao`): a
  anulação do sorteio é exatamente esta forma.
- **O contrato de reprodução** (`classificacao/application/reproducao.py`), e a frase que esta spec
  herda: *"A posição gravada nunca é usada como entrada do motor"*. O **mecanismo**, não: a
  implementação atual lê `stageResults` e não entende sorteio.
- **Idempotência por chave** (`emissao.py`), com a ressalva da D-3 desta spec.
- **Publicação de ordem e natureza preliminar/final** (`divulgacao`).
- **Portal público e consulta temporal**: o verificador é uma tela a mais, não um sistema à parte.
- **Retificação por identidade** (`004`): `/schedule/id=…/location` já é alcançável sem gramática
  nova, do jeito que `isRegistrationPeriod` demonstrou.

### 1.3 A prática que esta feature substitui

Os quatro Editais repetem a mesma cláusula (77 6.2; 57 8.2; 28 8.2; 76 5.2): o software é de
terceiro, e a garantia ao cidadão é a semente exibida no rodapé, depois do fato, sobre uma lista de
entrada que ninguém publicou canonicamente. **É contra isto que a feature se mede** — não contra a
ausência de sorteio.

---

## 2. Decisões fechadas antes do planejamento

Não são perguntas para o `/plan`. Reabrir qualquer uma exige evidência nova.

### D-001 — A ordem sorteada é um `AtoDeOrdenacao` constituído por sorteio

Das três formas registradas na descoberta de escopo, vale a **B**. As outras duas ficam recusadas
por escrito:

```text
A · Resultado individual   exigiria que o número sorteado fosse pontuação, com o sentido
                           invertido — o sistema decidindo o que o número significa

C · Critério de desempate  falta o veículo do valor (os três tipos leem pontuação de Etapa ou
                           FatoDeclarado, e fato é o que o Edital exige do candidato), e o
                           alcance é parcial: critério só ordena dentro de grupo já empatado
```

B reaproveita o agregado e **exige o que ele não tem**: discriminador de origem, estratégia de
constituição e proveniência própria na reprodução. O custo é declarado, não escondido.

### D-002 — A relação de habilitados é artefato próprio, e é o compromisso do universo

Ela entra no recorte desta feature **enquanto compromisso do sorteio**. Não entra o artefato
universal — a relação de inscritos que todo Edital publica, com ou sem sorteio — nem o recurso
contra ela (P-4), que a `018` excluiu e que o 76/2026 sequer prevê.

### D-003 — A semente vem de ocorrência futura de fonte pública externa

Declarada antes do congelamento, com regra de substituição mecânica. **Compromisso publicado pela
própria comissão fica recusado:** conhecendo o universo congelado, ela pode moer sementes e publicar
o resumo da conveniente. Transmitir ao vivo impede reexecutar, não impede escolher.

### D-004 — O identificador na chave é o número público da relação

É o que os Editais já fazem: *"cada candidato receberá um número para o sorteio, a ser publicado na
respectiva listagem"* (77, 6.4; 57, 8.4). Não é o protocolo da inscrição, que é do titular; é o
número que a audiência vê e que o verificador de terceiro recebe.

### D-005 — Colisão de chave se desempata pelo número público crescente

Improvável não é impossível, e "improvável" não é regra publicada. Há vetor de teste que a prova.

### D-006 — O recorte do sorteio é (recorte de vaga × lista de concorrência)

Fechada **contra** a hipótese inicial, pela leitura dos quatro Editais. O 57 (8.7) e o 28 (8.7)
dizem, palavra por palavra:

> todos os candidatos (inclusive os cotistas) participem do sorteio da ampla concorrência e em
> sequência haverá o sorteio das reservas de vaga

São sorteios distintos, e não um sorteio filtrado depois. Os cronogramas publicam relação de
habilitados e classificação preliminar *"(AMPLA CONCORRÊNCIA, PPI e PcD)"*, e o cotista aparece em
duas listas, com posição independente em cada.

```text
77/2026   perfil único, sem cotas                     1 ordem
76/2026   polos com cadastro de reserva, sem cotas    1 ordem por polo
57/2026   2 cursos × (AC, PPI, PcD)                   3 ordens por curso
28/2026   7 polos × (AC, PPI, PcD)                    3 ordens por polo — 21 no certame
```

Onde não há cota há uma lista só, e o recorte degenera no Perfil. **A consequência é estrutural:**
`uq_ato_raiz_por_marco` é única por `(edital, perfil_id, marco_id)` entre atos raiz, e três listas
sobre o mesmo marco colidem hoje. A lista entra como **dimensão do ato**, e não como marco próprio:
a janela recursal é do marco (`018`), e os Editais publicam **um** período de recurso para as três
listas.

### D-007 — Corte e progressão ficam fora

Sem eles o 77/2026 não fecha, e a spec diz isso na própria frase de valor em vez de deixar a
expectativa correr solta.

### D-008 — O Cronograma passa a publicar onde o evento acontece

Um campo de texto por Evento, sempre presente e vazio quando ausente. **Um só, e não dois** — o 76
publica naturezas diferentes na mesma coluna LOCAL, e o 77 diz sala física e canal na mesma frase.
**Não é URL** — *"Página da chamada pública"* não é endereço. **Sem valor institucional por
padrão**, pela razão já registrada nos rótulos da Etapa: *"um default institucional aplicaria ao
Edital um rótulo que ele não publicou"*. A conveniência vai para a composição, que sugere e repete;
sugerir é da tela, presumir é do conteúdo publicado.

### D-009 — Ato institucional único, computação livre

Para a mesma relação congelada, a mesma ocorrência da fonte e o mesmo **método declarado** — que
fixa algoritmo, versão e recorte —, existe no máximo **um ato raiz**. Recalcular é livre: o algoritmo
precisa poder rodar indefinidamente por terceiros; emitir outra ordem não é. A unicidade é sobre a
tupla inteira, e é o que mantém a anulação legal — o sucessor nasce de outra relação e de outra
ocorrência.

### D-010 — Não existe prévia depois que a semente é conhecida

Obter a semente, calcular e constituir o ato formam um comando **atômico e idempotente**. O fluxo da
`015` — calcular, conferir assinatura, confirmar, emitir — não é herdado literalmente: ele admite
calcular várias vezes antes de decidir emitir, e isso, depois da semente, é o ensaio que a feature
existe para impedir.

### D-011 — O universo é projeção, não digitação

A relação não aceita inclusão, exclusão nem numeração manual arbitrária: é projeção de fatos
oficiais já existentes. Correção posterior segue a cadeia — fato sucedido, nova relação, nova
ocorrência, novo ato —, e semente conhecida sobre relação alterada não se reutiliza.

### D-012 — A transmissão é evidência, não garantia

O canal continua externo. O sistema entrega uma tela que valha a transmissão e uma verificação que
sobreviva ao vídeo.

---

## 3. Problema

O sistema produz `ResultadoEtapa` a partir de avaliação humana e de ocorrência, e nada mais. Onde o
Edital seleciona por sorteio, **não existe o fato que alimenta o resultado** — e são quatro dos sete
Editais da amostra. A consequência prática é que o certame sai do sistema no meio: exporta inscritos,
sorteia num software de terceiro, volta com uma lista que ninguém consegue reproduzir.

O que falta não é aleatoriedade — é **prova**. Reprodutibilidade sozinha não basta: quem escolhe a
semente depois de ver o efeito dela produz resultado perfeitamente reproduzível e ainda assim
escolhido.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A comissão publica e congela a relação de habilitados (Priority: P1)

Encerradas as inscrições, quem conduz o certame publica a relação de quem está habilitado a
participar do sorteio, com o número de cada participante. A relação é projetada dos fatos oficiais —
inscrições submetidas e resultados vigentes aplicáveis — e, publicada, é congelada: passa a ser o
compromisso do universo, anterior a qualquer semente.

**Why this priority**: sem ela não há o que sortear em público nem como reproduzir depois, e é o
artefato que os quatro Editais publicam dois dias antes do sorteio. É também a única perna que
entrega valor sozinha: uma relação numerada e publicada já é mais do que o certame tem hoje.

**Independent Test**: publicar a relação de um Edital com inscrições submetidas, conferir que cada
participante recebeu número, que o resumo canônico foi gravado e que a consulta pública a devolve.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com inscrições submetidas e período encerrado, **When** a comissão
   publica a relação de habilitados de um recorte, **Then** o sistema projeta os participantes dos
   fatos oficiais, atribui a cada um um número público, grava o resumo canônico e publica.
2. **Given** uma relação publicada, **When** alguém tenta incluir, excluir ou renumerar um
   participante à mão, **Then** o sistema recusa: a relação é projeção, não digitação.
3. **Given** uma relação publicada e congelada, **When** um resultado que a alimenta é sucedido,
   **Then** o sistema não altera a relação — exige uma relação nova, e a anterior permanece legível.
4. **Given** um Edital com cotas, **When** a comissão publica as relações, **Then** há uma relação
   por lista de concorrência, e quem se declarou aparece na de ampla concorrência **e** na da sua
   reserva, com numeração própria em cada.

---

### User Story 2 — O sorteio oficial acontece uma vez, e produz a ordem (Priority: P1)

Na data e hora publicadas, com a tela transmitida, a comissão executa o sorteio. O sistema obtém a
semente da ocorrência declarada da fonte externa, calcula a ordem de **todos** os participantes e
constitui o ato — tudo num comando só. Não há prévia, não há "executar de novo".

**Why this priority**: é o ato que o certame precisa e que hoje acontece fora do sistema.

**Independent Test**: com uma relação congelada e a ocorrência da fonte disponível, executar o
sorteio e conferir que a ordem cobre todos os participantes, que o ato cita a relação por identidade
e resumo, e que uma segunda execução sobre a mesma tupla é recusada.

**Acceptance Scenarios**:

1. **Given** relação congelada e método declarado, **When** a comissão executa o sorteio depois da
   ocorrência da fonte, **Then** o sistema obtém a semente, calcula a ordem completa e constitui o
   ato numa transação só.
2. **Given** um sorteio já executado, **When** a mesma comissão pede execução de novo sobre a mesma
   relação, ocorrência, versão do algoritmo e recorte, **Then** o sistema recusa — existe no máximo
   um ato raiz para a tupla.
3. **Given** duas requisições concorrentes do mesmo comando, **When** ambas chegam, **Then** exatamente
   um ato nasce, e a segunda devolve o desfecho da primeira.
4. **Given** a fonte da ocorrência indisponível na hora marcada, **When** a comissão tenta executar,
   **Then** o sistema aplica a regra de substituição publicada e **em nenhum caso** oferece digitação
   manual da semente.
5. **Given** uma relação alterada depois de a ocorrência ser conhecida, **When** a comissão tenta
   executar com aquela ocorrência, **Then** o sistema recusa: semente conhecida sobre relação
   alterada não se reutiliza.

---

### User Story 3 — Qualquer pessoa reproduz a ordem por conta própria (Priority: P1)

O cidadão abre a página do sorteio, baixa o manifesto e recalcula a ordem com uma ferramenta sua.
Chega exatamente à mesma sequência, sem depender do vídeo e sem falar com a instituição.

**Why this priority**: é o que separa esta feature de um sorteador com semente no rodapé, e é a
capacidade que a instituição hoje não tem como oferecer.

**Independent Test**: publicar um sorteio, baixar o manifesto e reproduzir a ordem com uma
implementação independente, a partir apenas do que é público.

**Acceptance Scenarios**:

1. **Given** um sorteio publicado, **When** o cidadão consulta a verificação pública, **Then** o
   sistema recalcula a ordem a partir das entradas e informa participantes, integridade da relação,
   integridade da semente e reprodução do resultado.
2. **Given** o manifesto publicado, **When** uma implementação independente aplica a regra publicada,
   **Then** produz a mesma ordem, item a item.
3. **Given** um manifesto adulterado, **When** submetido à verificação, **Then** a adulteração é
   detectada e nomeada.
4. **Given** a verificação pública, **When** ela recalcula, **Then** usa as entradas — nunca as
   posições publicadas — como fonte, que é a regra que a reprodução do sistema já obedece.
5. **Given** o pacote público, **When** examinado, **Then** não contém CPF, identificador interno nem
   dado pessoal além do que a relação publicada já expõe.

---

### User Story 4 — O certame com cotas produz uma ordem por lista (Priority: P2)

Num Edital com reserva de vagas, o sorteio da ampla concorrência alcança todos os inscritos daquele
recorte, e em seguida cada lista de reserva tem o seu próprio sorteio. O candidato que se declarou
tem posição nas duas, e as duas posições são independentes.

**Why this priority**: é o que 57 e 28 exigem, e é metade da amostra de sorteio. Sem isso a feature
atende só os Editais sem cota.

**Independent Test**: compor um Edital com AC, PPI e PcD; publicar as três relações; executar os três
sorteios; conferir que o mesmo cotista tem posições independentes e que cada lista tem ato próprio.

**Acceptance Scenarios**:

1. **Given** um recorte com três listas declaradas, **When** os sorteios são executados, **Then**
   nascem três atos raiz distintos, cada um com a sua relação, a sua ocorrência e a sua ordem.
2. **Given** um cotista habilitado, **When** as ordens são publicadas, **Then** ele aparece nas duas
   listas, e a posição numa não determina a posição na outra.
3. **Given** as ordens publicadas, **When** alguém pergunta quem ocupa as vagas, **Then** o sistema
   **não** responde: ocupação, remanejamento e a regra de quem sai de qual lista são de outra
   capacidade.

---

### User Story 5 — Anulado um sorteio, nasce outro, ligado ao primeiro (Priority: P2)

Havendo nulidade, a comissão não "refaz" o sorteio: constitui um novo, com relação nova e ocorrência
nova, ligado ao anterior e com motivo. O primeiro continua legível para sempre.

**Why this priority**: é o caminho que impede "executar de novo" de existir como botão, e sem ele a
unicidade do ato vira um beco sem saída operacional.

**Independent Test**: anular um sorteio publicado, constituir o sucessor e conferir que os dois
coexistem, com motivo gravado e o anterior íntegro.

**Acceptance Scenarios**:

1. **Given** um sorteio publicado, **When** a comissão o anula com motivo, **Then** o ato anterior
   permanece íntegro e legível, e nenhum dado dele é alterado.
2. **Given** um sorteio anulado, **When** o sucessor é constituído, **Then** ele cita o anterior, traz
   o motivo da sucessão e nasce de outra relação e outra ocorrência.
3. **Given** um sorteio sem motivo informado, **When** a anulação é tentada, **Then** o sistema recusa.

---

### User Story 6 — O Edital publica onde o sorteio acontece (Priority: P3)

Quem elabora informa, no evento do Cronograma, onde ele ocorre — o canal da transmissão, a página do
processo, a sala física. O documento publicado passa a dizer o que hoje só existe em prosa ou em
evento improvisado.

**Why this priority**: é lacuna de autoria que o sorteio torna aguda, e é a menor das seis histórias.

**Independent Test**: compor um evento com local preenchido, publicar e conferir que a seção do
Cronograma o exibe e que a Retificação o alcança.

**Acceptance Scenarios**:

1. **Given** um evento em elaboração, **When** quem elabora informa o local, **Then** ele viaja no
   conteúdo publicado e aparece no Cronograma publicado.
2. **Given** um evento sem local informado, **When** o Edital é publicado, **Then** o campo significa
   "não declarado" — e o sistema não inventa canal, sala nem página.
3. **Given** um Edital publicado, **When** uma Retificação altera o local de um evento, **Then** ela o
   alcança por identidade, e a versão anterior permanece consultável.

---

### Edge Cases

- **Relação com um participante só, ou com nenhum.** A ordem de um é legítima; a de nenhum é
  recusada — não há universo a comprometer.
- **Colisão de chave.** Improvável, previsto e testado: desempata pelo número público crescente.
- **Ocorrência da fonte que não existe, atrasa, bifurca ou vem inválida.** A regra publicada decide,
  sem escolha humana no momento.
- **Retificação do Cronograma depois do congelamento.** Muda a data publicada do evento; não altera
  relação congelada nem ato constituído.
- **Participante que deixa de ser habilitado depois da publicação da relação.** Não sai da relação:
  entra na cadeia de sucessão, que produz relação nova.
- **Edital sem cota.** Uma lista só, e o recorte degenera no Perfil — nenhuma configuração extra.
- **Edital que não declara o próprio recorte** — o 76 é o caso real. Quem elabora declara na
  composição; o sistema não infere recorte de quadro de vagas.
- **Tentativa de executar antes da ocorrência declarada.** Recusada: a semente é posterior ao
  congelamento por construção.

## Requirements *(mandatory)*

### Functional Requirements

#### A relação de habilitados

- **FR-001**: O sistema MUST permitir que a comissão publique, para um recorte, a relação dos
  participantes habilitados ao sorteio.
- **FR-002**: A relação MUST ser projetada de fatos oficiais já existentes — inscrições submetidas e
  resultados vigentes aplicáveis — e MUST NOT admitir inclusão, exclusão ou alteração manual de
  participante.
- **FR-003**: O sistema MUST atribuir a cada participante um **número público** estável dentro da
  relação, e MUST NOT admitir numeração digitada.
- **FR-004**: A numeração MUST ser própria de cada relação: o participante que figura em duas listas
  recebe número em cada uma.
- **FR-005**: A relação publicada MUST expor, no canal público, ao menos o número público e a
  identificação que o Edital já publica dos seus candidatos, e MUST NOT expor CPF nem identificador
  interno.
- **FR-006**: O sistema MUST gravar o resumo canônico da relação no momento da publicação.
- **FR-007**: A relação publicada MUST ser imutável: nem a aplicação nem a role de runtime alteram
  participante, número ou resumo.
- **FR-008**: O sistema MUST registrar quem publicou a relação, quando, e sob qual versão do Edital.
- **FR-009**: O sistema MUST recusar a publicação de relação vazia.
- **FR-010**: O sistema MUST permitir publicar relação nova para o mesmo recorte quando um fato de
  origem for sucedido, preservando integralmente a anterior.
- **FR-011**: A consulta pública MUST devolver a relação publicada e o seu resumo.
- **FR-012**: A relação MUST identificar o recorte a que pertence — recorte de vaga e lista de
  concorrência.

#### O método declarado e a semente

- **FR-013**: O Edital ou o ato do sorteio MUST declarar, **antes do congelamento**: o algoritmo e a
  sua versão, o recorte, a fonte da semente, a ocorrência que a fixará, a regra de derivação da
  ocorrência a partir da data programada, a representação dos bytes, a regra de normalização e a
  regra de substituição em caso de indisponibilidade, atraso, bifurcação ou dado inválido.
- **FR-014**: O método declarado MUST ser conteúdo normativo publicado; alterá-lo MUST ser ato da
  classe da Retificação, e MUST NOT ser efeito de implantação de software.
- **FR-015**: A regra de substituição MUST ser mecânica: aplicada sem escolha humana no momento da
  execução.
- **FR-016**: A ocorrência que fixa a semente MUST ser posterior ao congelamento da relação.
- **FR-017**: O sistema MUST NOT admitir semente digitada, colada ou escolhida por qualquer ator.
- **FR-018**: O sistema MUST NOT admitir compromisso de semente produzido pela própria instituição
  como substituto da fonte externa.
- **FR-019**: O sistema MUST registrar o material bruto obtido da fonte, a semente normalizada e o
  instante da obtenção.
- **FR-020**: Sendo a relação alterada depois de a ocorrência ser conhecida, o sistema MUST recusar
  aquela ocorrência para o sorteio seguinte.

#### A ordem, e como ela é produzida

- **FR-021**: O sistema MUST calcular, para cada participante, uma chave derivada por função de
  resumo criptográfico sobre a serialização canônica de: separador de domínio, resumo da relação,
  identidade do recorte, semente normalizada e número público.
- **FR-022**: A ordem MUST ser a das chaves em ordem crescente do resumo binário completo.
- **FR-023**: Havendo chaves idênticas, o sistema MUST desempatar pelo número público crescente.
- **FR-024**: Nenhum valor escolhido por qualquer ator depois do congelamento MUST entrar na chave.
- **FR-025**: A ordem MUST cobrir **todos** os participantes da relação, e MUST NOT ser truncada pelo
  número de vagas.
- **FR-026**: O sistema MUST NOT depender de gerador pseudoaleatório de linguagem, runtime ou
  biblioteca para produzir a ordem.
- **FR-027**: A regra de composição da chave MUST ser publicada com detalhe suficiente para
  reimplementação independente.
- **FR-028**: O repositório MUST publicar vetores de teste normativos com entrada, bytes canônicos,
  resumo e ordem esperada, incluindo um caso de colisão.

#### O ato, e a sua unicidade

- **FR-029**: Obter a semente, calcular a ordem e constituir o ato MUST acontecer num comando único,
  atômico e idempotente.
- **FR-030**: O sistema MUST NOT oferecer cálculo prévio, simulação ou pré-visualização da ordem
  depois de a semente ser conhecida.
- **FR-031**: Para a mesma relação congelada, a mesma ocorrência e o **mesmo método declarado** — que
  é o que fixa algoritmo, versão e recorte —, o sistema MUST admitir no máximo um ato raiz. O método
  é a unidade porque é ele que existe como declaração publicada; "versão do algoritmo" descreve o
  conteúdo dele, e duas declarações distintas de mesma versão são dois métodos.
- **FR-032**: Requisições concorrentes do mesmo comando MUST produzir exatamente um ato, devolvendo
  às demais o desfecho do primeiro.
- **FR-033**: O ato MUST citar a relação por identidade e por resumo.
- **FR-034**: O ato MUST declarar que foi **constituído por sorteio**, e não computado a partir de
  Etapas.
- **FR-035**: O ato MUST identificar o recorte, incluindo a lista de concorrência.
- **FR-036**: O sistema MUST admitir atos distintos para listas distintas do mesmo recorte de vaga e
  do mesmo marco.
- **FR-037**: O ato MUST ser append-only: nem posição, nem ordem, nem proveniência se alteram depois
  de constituídos.
- **FR-038**: O sistema MUST registrar ator, instante, versão do Edital e correlação na trilha de
  auditoria ao constituir o ato.

#### A reprodução

- **FR-039**: O sistema MUST reproduzir um ato constituído por sorteio a partir da sua própria
  proveniência congelada, sem consultar conteúdo vigente.
- **FR-040**: A reprodução MUST usar como entrada a relação, a semente e o método, e MUST NOT usar as
  posições gravadas.
- **FR-041**: A reprodução MUST preservar o contrato já existente para atos computados, acrescentando
  estratégia própria para os constituídos por sorteio.

#### O manifesto e a publicação

- **FR-042**: O sistema MUST produzir, para cada sorteio, um manifesto público contendo: processo,
  Edital e versão; identidade do sorteio e do recorte; algoritmo e versão; quantidade de
  participantes; resumo da relação; fonte, ocorrência e semente normalizada; instantes de
  congelamento e de execução; e, por participante, número público, chave e posição obtida.
- **FR-043**: O manifesto MUST ter resumo próprio, publicado com ele.
- **FR-044**: O manifesto MUST NOT conter CPF, identificador interno nem dado pessoal além do que a
  relação publicada já expõe.
- **FR-045**: O sistema MUST publicar a ordem completa, e MUST identificar a lista de concorrência a
  que ela pertence.
- **FR-046**: O documento publicado do resultado MUST exibir identidade do sorteio, algoritmo,
  semente e resumos de integridade.
- **FR-047**: O manifesto MUST estar disponível para download em formato legível por máquina.

#### A verificação pública

- **FR-048**: O sistema MUST oferecer, no canal público e sem autenticação, a verificação de um
  sorteio publicado.
- **FR-049**: A verificação MUST recalcular a ordem a partir das entradas e informar, em linguagem
  compreensível, o que foi conferido e o que resultou.
- **FR-050**: A verificação MUST detectar e nomear divergência entre manifesto, relação e ordem
  publicada.
- **FR-051**: A verificação MUST funcionar sem depender de gravação de vídeo ou de qualquer canal
  externo.

#### A anulação

- **FR-052**: O sistema MUST NOT oferecer "refazer" um sorteio.
- **FR-053**: A anulação MUST constituir novo sorteio, ligado ao anterior, com motivo obrigatório.
- **FR-054**: O sorteio sucessor MUST nascer de relação nova e ocorrência nova.
- **FR-055**: O sorteio anulado MUST permanecer íntegro, legível e consultável.

#### O local do evento

- **FR-056**: O Evento do Cronograma MUST admitir a declaração de onde ele acontece, em campo de
  texto único.
- **FR-057**: O campo MUST estar sempre presente no conteúdo publicado, com valor vazio significando
  "não declarado".
- **FR-058**: O sistema MUST NOT atribuir valor institucional por padrão ao campo.
- **FR-059**: A interface de composição MAY sugerir valores — repetir o do evento anterior, oferecer o
  canal habitual —, e a sugestão MUST NOT preencher conteúdo publicado sem ato de quem elabora.
- **FR-060**: A Retificação MUST alcançar o campo por identidade do Evento, sem gramática nova.
- **FR-061**: O campo MUST NOT ser validado como endereço eletrônico.

#### Autorização, e o que a feature recusa

- **FR-062**: Publicar relação, congelar universo, executar sorteio e anular MUST exigir permissão
  explícita e verificação de escopo institucional.
- **FR-063**: Quem executa o sorteio MUST estar vinculado à condução daquele certame.
- **FR-064**: O sistema MUST NOT decidir quem ocupa vaga, quem é suplente, quem sai de qual lista nem
  até onde a análise documental desce.
- **FR-065**: O sistema MUST NOT transmitir, gravar ou integrar canal de vídeo.

### Key Entities

- **Relação de Habilitados**: o universo comprometido de um recorte, com participantes numerados,
  resumo canônico, instante e ator da publicação. Imutável depois de publicada; sucedida, nunca
  editada.
- **Participante da Relação**: a inscrição que figura na relação, com o seu número público. É o que a
  chave do sorteio endereça.
- **Método do Sorteio**: algoritmo, versão, recorte, fonte da semente, ocorrência, derivação,
  normalização e regra de substituição. Conteúdo normativo publicado.
- **Ocorrência da Fonte**: o evento externo, futuro e previamente determinado, cujo valor fixa a
  semente. Guarda material bruto, semente normalizada e instante.
- **Ato de Ordenação constituído por sorteio**: a ordem emitida, com proveniência própria — relação,
  ocorrência, método —, sucessão e motivo.
- **Manifesto do Sorteio**: o pacote público que torna a ordem reproduzível por terceiro.
- **Local do Evento**: onde o evento do Cronograma acontece, como texto publicado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma pessoa fora da instituição, com o manifesto publicado e uma ferramenta própria,
  reproduz a ordem de um sorteio real **item a item**, sem contato com o Ifes e sem assistir ao
  vídeo.
- **SC-002**: Duas implementações independentes, escritas em linguagens diferentes a partir apenas da
  regra publicada, produzem a mesma ordem para todos os vetores normativos.
- **SC-003**: Nenhum ator do sistema consegue, em nenhum caminho, escolher, digitar ou substituir a
  semente do sorteio oficial — verificado por tentativa em todos os caminhos oferecidos.
- **SC-004**: Um sorteio de 300 participantes vai do congelamento à ordem publicada, ao vivo, em
  menos de um minuto de operação — o tempo de uma tomada de transmissão.
- **SC-005**: 100% dos sorteios publicados passam na própria verificação pública, e a verificação
  aponta divergência em 100% dos manifestos adulterados usados como controle.
- **SC-006**: Os quatro Editais de sorteio da amostra têm o seu mecanismo de seleção executável no
  sistema — um deles, o 77/2026, do congelamento à ordem publicada; nenhum deles, ainda, até a
  ocupação de vagas.
- **SC-007**: Nenhum dado pessoal além do que o Edital já publica aparece no pacote público,
  verificado por inspeção do manifesto de um certame real.

## Assumptions

- O certame que sorteia publica a relação de habilitados antes do sorteio; é o que os quatro Editais
  fazem, com dois dias de antecedência.
- A fonte pública externa da semente é escolhida institucionalmente e declarada no Edital ou no ato
  do sorteio. A spec fixa as propriedades exigidas dela, não a sua identidade.
- A transmissão continua acontecendo em canal externo, operado por quem hoje o opera.
- O recorte é declarado por quem elabora; o sistema não o infere do quadro de vagas, e o 76/2026
  mostra por quê.
- Editais publicados antes desta feature não declaram local de evento, e a ausência significa "não
  declarado" — o que é verdadeiro sobre todos eles.
- A relação de habilitados desta feature é a do sorteio. A relação de inscritos que todo Edital
  publica é artefato universal, e é outra feature.

## Out of Scope

Cada item é feature própria, e nenhum deriva automaticamente desta.

- **Ocupação de vagas, cotas, remanejamento e concorrência concomitante** — inclusive a regra de que
  o cotista sorteado nas duas listas fica na de ampla concorrência e libera a vaga reservada.
- **Convocação, chamada e suplência.**
- **Corte e progressão entre Etapas** — sem elas o 77/2026 não fecha, e a spec diz isso.
- **Recurso ou impugnação contra a relação de habilitados.**
- **Relação de inscritos como artefato universal de todo Edital.**
- **Heteroidentificação** e **aplicabilidade da Etapa por modalidade**.
- **Integração com API de transmissão** — o campo de local guarda o que o Edital publica; o canal
  continua externo.
- **Prova objetiva e importação de notas produzidas fora do sistema.**
- **Quadro de vagas estruturado por modalidade.**
