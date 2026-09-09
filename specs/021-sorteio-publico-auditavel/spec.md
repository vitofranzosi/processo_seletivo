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
- **Idempotência por chave** (`emissao.py`), com a ressalva da D-010 desta spec.
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

Onde não há cota há uma lista só, e o recorte degenera no Perfil.

**Uma precisão de vocabulário, que a D-013 tornou necessária.** "Recorte" nomeia o par
(recorte de vaga × lista) — é o que varia dentro de um marco. O **marco** é o terceiro eixo, e
sempre esteve lá: o `AtoDeOrdenacao` é por marco desde a `015`, e é o marco que passa a declarar o
método. Onde este documento diz "recorte" sem qualificar, o marco está subentendido; onde a
identidade importa — chaves de unicidade, `metodo_hash`, endereçamento normativo —, os três eixos
aparecem escritos.

**A consequência é estrutural:**
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

Para a mesma relação congelada e a mesma ocorrência da fonte existe no máximo **um ato raiz**.
Recalcular é livre: o algoritmo precisa poder rodar indefinidamente por terceiros; emitir outra ordem
não é. A unicidade é sobre a tupla inteira, e é o que mantém a anulação legal — o sucessor nasce de
outra relação e de outra ocorrência.

**O método ficou fora da tupla porque deixou de ser escolha.** A D-014 fez a relação citá-lo no
congelamento: dada a relação, o método está determinado, e acrescentá-lo à chave de unicidade não
restringiria nada — sugeriria, ao contrário, que um sorteio pudesse rodar sob método diferente do que
a sua própria relação comprometeu.

### D-010 — Não existe prévia depois que a semente é conhecida

Calcular a ordem e constituir o ato formam um comando **atômico e idempotente**, e é ele que a
proibição alcança. O fluxo da `015` — calcular, conferir assinatura, confirmar, emitir — não é
herdado literalmente: ele admite calcular várias vezes antes de decidir emitir, e isso, depois da
semente, é o ensaio que a feature existe para impedir.

**Observar a ocorrência é ato anterior e distinto**, e não é ensaio: ele busca o material na fonte e
o registra, sem calcular chave nenhuma e sem criar ato nenhum. A fronteira está no que o comando
produz, e não em quantas chamadas o compõem — fundir a ida à rede com a transação de banco não
acrescentaria garantia, e trocaria uma falha de rede por uma transação longa.

### D-011 — O universo é projeção, não digitação

A relação não aceita inclusão, exclusão nem numeração manual arbitrária: é projeção de fatos
oficiais já existentes. Correção posterior segue a cadeia — fato sucedido, nova relação, nova
ocorrência, novo ato —, e semente conhecida sobre relação alterada não se reutiliza.

### D-012 — A transmissão é evidência, não garantia

O canal continua externo. O sistema entrega uma tela que valha a transmissão e uma verificação que
sobreviva ao vídeo.

> As quatro decisões seguintes foram tomadas **depois** do `tasks.md`, na análise cruzada dos
> artefatos. Estão aqui, e não numa errata, porque governam modelo e requisito como as doze
> anteriores — e porque a spec que as escondesse num apêndice mentiria sobre a própria ordem.

### D-013 — O método do sorteio é conteúdo versionado do Edital

A FR-014 sempre disse que o método é conteúdo normativo publicado e que alterá-lo é ato da classe da
Retificação. **Uma tabela própria não entrega isso**: não tem versão consolidada, não tem autoridade
signatária, não entra no snapshot e não é alcançada pela gramática de endereçamento. Dizer "classe
da Retificação" sobre um registro operacional é analogia, não garantia.

O método passa a ser objeto do **marco de classificação**, no conteúdo canônico:
`/profiles/id=…/classificationMilestones/id=…/drawMethod`. É o mesmo lugar e a mesma forma da
`appealWindow` da `018` — objeto aninhado no marco, elevado por degrau, `null` significando "não
declarado" —, e a Retificação o alcança **sem gramática nova**, porque em objeto o caminho já
resolve por chave literal.

**O método é do marco, e não da lista.** Um sorteio é um evento: a mesma extração da mesma fonte
semeia as três listas do recorte, e é o `relationHash` que as separa — é exatamente o que o vetor
`mesma-semente-recortes-distintos` prova. Declarar método por lista abriria de novo a porta que a
D-014 fecha, e não atenderia Edital nenhum da amostra.

### D-014 — Uma relação vigente por recorte, e é ela que cita o método

Duas frestas restavam entre o congelamento e a semente, e as duas tinham a mesma forma — escolher
depois de saber:

1. **duas relações raiz vivas.** A sucessão dizia qual era a vigente pela cadeia, mas nada impedia
   duas raízes coexistirem no mesmo recorte, cada uma sem sucessora e portanto ambas "vigentes";
2. **dois métodos declarados.** Relação e método chegavam ao sorteio como escolhas independentes, e
   métodos apontam ocorrências diferentes — logo, sementes diferentes.

A correção é uma só, e é a mesma dos atos: **unicidade de raiz por recorte**, mais a relação
**citando o método** por resumo no instante em que congela. Depois disso o sorteio não recebe método:
ele consome o que a relação comprometeu, sob a versão que ela cita.

### D-015 — A publicação de resultado ganha a dimensão da lista

A D-006 fez o ato admitir três raízes por marco e parou aí. `PublicacaoResultado` continua única por
`(Edital, Perfil, marco)`, e três atos exigem três publicações: a segunda lista bate na constraint e
o certame com cotas não publica. A dimensão da lista **atravessa** o ato e alcança a divulgação, e a
cirurgia é a mesma já aceita para `AtoDeOrdenacao` — a constraint parte em duas parciais, e a de
hoje sobrevive palavra por palavra para a publicação sem lista.

Junto vem a leitura: `ato_vigente` procura um ato por marco, e `estado_do_marco` recomputa a
classificação por Etapas para aferir obsolescência. Nenhum dos dois foi escrito para uma ordem que
não vem de Etapa. **Ato de sorteio não se afere recomputando** — a sua obsolescência é a da relação
que o originou, e não a de um cálculo que jamais o produziu.

### D-016 — A semente normalizada é do sorteio, não da ocorrência

Normalizar é regra do método; observar é registrar o que a fonte publicou. Guardar a semente
normalizada na ocorrência — única por `(fonte, referência)` — congelaria a normalização do primeiro
método que passasse por ali e a imporia a todos os demais, em silêncio. A ocorrência guarda **o
material bruto**; a semente derivada é do `Sorteio`, que é onde método e ocorrência se encontram.

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
5. **Given** um marco cujo Edital publicado declara o método do sorteio, **When** a comissão publica
   a relação, **Then** a relação grava o resumo daquele método — de modo que o compromisso do
   universo e o compromisso do método nascem no mesmo instante, antes de a semente existir.
6. **Given** um marco cujo Edital **não** declara método, **When** a comissão tenta publicar a
   relação, **Then** o sistema recusa e diz o que falta: congelar sob método indefinido seria
   escolher o método depois.
7. **Given** um recorte que já tem relação vigente, **When** alguém publica outra relação para o
   mesmo recorte sem suceder a primeira, **Then** o sistema recusa: duas relações vivas seriam duas
   escolhas possíveis depois de a semente ser conhecida.

---

### User Story 2 — O sorteio oficial acontece uma vez, e produz a ordem (Priority: P1)

Na data e hora publicadas, com a tela transmitida, a comissão observa a ocorrência declarada da
fonte externa — que registra o material bruto e nada mais — e executa o sorteio: o sistema deriva a
semente pela regra do método, calcula a ordem de **todos** os participantes e constitui o ato, tudo
numa transação só. Não há prévia, não há "executar de novo". **São dois comandos, e a fronteira é
proposital**: o que a proibição alcança é calcular e constituir, e ir à rede não produz ordem
nenhuma.

**Why this priority**: é o ato que o certame precisa e que hoje acontece fora do sistema.

**Independent Test**: com uma relação congelada e a ocorrência da fonte disponível, executar o
sorteio e conferir que a ordem cobre todos os participantes, que o ato cita a relação por identidade
e resumo, e que uma segunda execução sobre a mesma tupla é recusada.

**Acceptance Scenarios**:

1. **Given** relação congelada e ocorrência já observada e registrada, **When** a comissão executa o
   sorteio, **Then** o sistema lê o método pela versão que a relação cita, confere o resumo dele
   contra o que a relação comprometeu, deriva a semente, calcula a ordem completa e constitui o ato
   numa transação só — sem ir à fonte durante a transação.
2. **Given** um sorteio já executado, **When** a mesma comissão pede execução de novo sobre a mesma
   relação e a mesma ocorrência, **Then** o sistema recusa — existe no máximo um ato raiz para a
   tupla.
3. **Given** duas requisições concorrentes do mesmo comando, **When** ambas chegam, **Then** exatamente
   um ato nasce, e a segunda devolve o desfecho da primeira.
4. **Given** a fonte da ocorrência indisponível na hora marcada, **When** a comissão tenta executar,
   **Then** o sistema aplica a regra de substituição publicada e **em nenhum caso** oferece digitação
   manual da semente.
5. **Given** uma relação alterada depois de a ocorrência ser conhecida, **When** a comissão tenta
   executar com aquela ocorrência, **Then** o sistema recusa: semente conhecida sobre relação
   alterada não se reutiliza.
6. **Given** uma tentativa de passar método ao comando do sorteio, por qualquer rota, formulário ou
   parâmetro, **When** ela chega, **Then** não há onde ela entre: o método vem da relação, e a
   superfície não o aceita.

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
- **Colisão de chave.** Improvável ao ponto de não ser construtível, e ainda assim previsto e
  testado: o desempate por número público crescente é exercitado por um vetor de **ordenação**, que
  entrega as chaves já iguais. Nenhuma entrada válida do sistema produz duas chaves iguais, e um
  vetor que prometesse colisão de SHA-256 prometeria o que ninguém constrói.
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
- **Retificação do método depois do congelamento.** Vale para o que vier; **não** alcança relação
  congelada nem ato constituído, porque a relação cita a versão e o resumo do método sob os quais
  congelou. Sortear passa a ser recusado quando a versão citada não contém mais aquele método.
- **Ocorrência já observada que nenhum sorteio consome.** Fica registrada e visível: é o controle
  que torna o descarte de ocorrência auditável, e não um rascunho a limpar.
- **Marco com três listas, no momento de divulgar.** Três atos, três publicações, cada uma com a sua
  cadeia de sucessão. Suceder a publicação de uma lista não toca as outras duas.

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
- **FR-005**: A relação publicada MUST expor, no canal público, exatamente três dados por
  participante — número público, nome e protocolo da inscrição —, que são os que a divulgação de
  resultado da `017` já publica, e MUST NOT expor CPF, identificador interno de inscrição nem
  qualquer outro dado pessoal.
- **FR-006**: O sistema MUST gravar o resumo canônico da relação no momento da publicação, e esse
  resumo MUST cobrir **apenas** dados publicados — de modo que qualquer pessoa o recalcule a partir
  da relação que lê no portal, sem pedir nada à instituição.
- **FR-007**: A relação publicada MUST ser imutável: nem a aplicação nem a role de runtime alteram
  participante, número ou resumo.
- **FR-008**: O sistema MUST registrar quem publicou a relação, quando, e sob qual versão do Edital.
- **FR-009**: O sistema MUST recusar a publicação de relação vazia.
- **FR-010**: O sistema MUST permitir publicar relação nova para o mesmo recorte quando um fato de
  origem for sucedido, preservando integralmente a anterior.
- **FR-011**: A consulta pública MUST devolver a relação publicada e o seu resumo.
- **FR-012**: A relação MUST identificar o recorte a que pertence — recorte de vaga, marco de
  classificação e lista de concorrência.
- **FR-067**: A relação MUST citar, no instante em que é publicada, a versão do Edital sob a qual foi
  projetada e o **resumo do método declarado** naquela versão para o seu marco; e o ato do sorteio
  MUST consumir esse método, sem receber método como parâmetro em caminho algum.
- **FR-070**: Para o mesmo recorte, o sistema MUST admitir no máximo **uma relação raiz** e, a cada
  sucessão, no máximo uma sucessora — de modo que "a relação vigente" seja única por construção, e
  não por convenção de leitura. Publicar segunda relação raiz para recorte que já tem uma MUST ser
  recusado pelo banco, e não apenas pela aplicação.
- **FR-071**: O sistema MUST recusar sortear relação que já tenha sucessora.

#### O método declarado e a semente

- **FR-013**: O conteúdo publicado do Edital MUST declarar, no marco de classificação e **antes do
  congelamento**: o algoritmo e a sua versão, a fonte da semente, a ocorrência que a fixará, a regra
  de derivação da ocorrência a partir da data programada, a representação dos bytes, a regra de
  normalização e a regra de substituição em caso de indisponibilidade, atraso, bifurcação ou dado
  inválido. O recorte **não** é campo do método: o método é do marco, e a identidade do marco é o
  recorte a que ele se aplica (D-013).
- **FR-014**: O método MUST viver no conteúdo canônico versionado, sob o marco que o declara, e
  alterá-lo MUST ser Retificação sobre esse conteúdo, endereçada por identidade do Perfil e do
  marco, sem gramática nova. MUST NOT ser efeito de implantação de software, e MUST NOT existir
  caminho que o altere fora do ato normativo.
- **FR-066**: O marco que não declara método MUST publicar o campo com valor nulo, significando
  "método não declarado", e o sistema MUST recusar congelar relação em marco sem método declarado.
- **FR-015**: A regra de substituição MUST ser mecânica: aplicada sem escolha humana no momento da
  execução.
- **FR-016**: A ocorrência que fixa a semente MUST ser posterior ao congelamento da relação.
- **FR-017**: O sistema MUST NOT admitir semente digitada, colada ou escolhida por qualquer ator.
- **FR-018**: O sistema MUST NOT admitir compromisso de semente produzido pela própria instituição
  como substituto da fonte externa.
- **FR-019**: O registro da ocorrência MUST guardar o material bruto obtido da fonte e o instante da
  obtenção, e MUST NOT guardar a semente normalizada: normalizar é regra do método, e a mesma
  ocorrência pode ser lida por métodos que normalizam diferente. A semente normalizada MUST ser
  gravada no sorteio, que é onde método e ocorrência se encontram (D-016).
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
  resumo e ordem esperada, e MUST publicar, à parte, um vetor de **ordenação** cujas chaves são dadas
  já iguais, provando que o desempate da FR-023 executa. O vetor de desempate MUST NOT ser
  apresentado como colisão de SHA-256: colisão real não é produzível, e entradas válidas do sistema
  não a produzem — números públicos iguais em relações distintas têm resumos de relação distintos, e
  na mesma relação são recusados pela unicidade da numeração.

#### O ato, e a sua unicidade

- **FR-029**: Calcular a ordem e constituir o ato MUST acontecer num comando único, atômico e
  idempotente, que consome uma ocorrência **já observada e registrada** e MUST NOT ir à fonte durante
  a transação. Observar a ocorrência MUST ser comando anterior e distinto, que registra material
  bruto e MUST NOT calcular chave, ordem ou ato (D-010).
- **FR-030**: O sistema MUST NOT oferecer cálculo prévio, simulação ou pré-visualização da ordem
  depois de a semente ser conhecida.
- **FR-031**: Para a mesma relação congelada e a mesma ocorrência, o sistema MUST admitir no máximo
  um ato raiz. O método não entra na tupla porque não é escolha: a relação o cita no congelamento
  (FR-067), e dada a relação ele está determinado.
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
- **FR-068**: A publicação de resultado MUST admitir a dimensão da lista de concorrência, de modo que
  as ordens das listas distintas de um mesmo marco sejam publicadas cada uma no seu ato de
  divulgação, e MUST preservar, para a publicação sem lista, a unicidade que hoje vale por
  `(Edital, Perfil, marco)`.
- **FR-069**: A leitura do ato vigente e a aferição de publicabilidade MUST distinguir ato computado
  de ato constituído por sorteio, e MUST NOT declarar obsoleto um ato de sorteio por divergir de uma
  classificação recomputada a partir de Etapas, que não é a regra que o produziu.
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

- **FR-062**: Os comandos desta feature MUST exigir permissão explícita e verificação de escopo
  institucional, e são **quatro**, porque publicar a relação **é** congelá-la: declarar o método,
  observar a ocorrência, publicar a relação e constituir o sorteio — a anulação sendo a constituição
  de um sorteio sucessor, e não comando à parte. Declarar o método MUST seguir a autorização do ato
  normativo que o carrega, e não a dos comandos do sorteio.
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
- **Método do Sorteio**: algoritmo, versão, fonte da semente, ocorrência, derivação, normalização e
  regra de substituição. **Não é entidade própria**: é objeto do marco de classificação no conteúdo
  canônico versionado do Edital, retificável por identidade e sem gramática nova (D-013).
- **Ocorrência da Fonte**: o evento externo, futuro e previamente determinado, cujo valor fixa a
  semente. Guarda material bruto e instante — e só isso.
- **Ato de Ordenação constituído por sorteio**: a ordem emitida, com proveniência própria — relação,
  ocorrência, método —, sucessão e motivo.
- **Manifesto do Sorteio**: o pacote público que torna a ordem reproduzível por terceiro.
- **Local do Evento**: onde o evento do Cronograma acontece, como texto publicado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma pessoa fora da instituição, com o manifesto publicado e uma ferramenta própria,
  reproduz a ordem de um sorteio real **item a item** — e, querendo, recalcula o resumo da relação a
  partir da relação publicada, em vez de aceitá-lo —, sem contato com o Ifes e sem assistir ao vídeo.
- **SC-002**: Duas implementações independentes, escritas em linguagens diferentes a partir apenas da
  regra publicada, produzem a mesma ordem para todos os vetores normativos.
- **SC-003**: Nenhum ator do sistema consegue, em nenhum caminho, escolher, digitar ou substituir a
  semente do sorteio oficial, **nem escolher, depois de a semente ser conhecida, qual relação ou qual
  método o sorteio usa** — verificado por tentativa em todos os caminhos oferecidos. As três frestas
  são a mesma fresta: decidir uma entrada depois de conhecer o efeito dela.
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
- A fonte pública externa da semente é escolhida institucionalmente e declarada **no Edital**, junto
  com o resto do método, no marco de classificação. A spec fixa as propriedades exigidas dela, não a
  sua identidade. A redação anterior admitia "no Edital ou no ato do sorteio"; a segunda metade caiu
  com a D-013, e era ela que deixava o método fora do conteúdo versionado.
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
