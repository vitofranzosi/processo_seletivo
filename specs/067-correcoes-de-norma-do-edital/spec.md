# Feature Specification: Correções de norma do Edital em PDF — recurso com objeto, sorteio sem conta e Perfil sem vaga imediata

**Feature Branch**: `claude/067-correcoes-de-norma-do-edital` — criada sobre a `main` `99d32e16`, que
já tem a `065` (PR #266) e a auditoria que fundamenta esta feature.

**Created**: 2026-10-09

**Status**: Draft — decisões fechadas pelo responsável pelo produto em 09/10/2026 (ver *Decisões*)

**Input**: os achados **ED-02**, **ED-03** e **ED-12** da [auditoria do Edital em PDF de
08/10/2026](../../doc/auditoria-edital-pdf-2026-10-08.md) (§11, §12.1, §5.2 L7 e L10, §8 C1 a C4) e o
pedido do responsável pelo produto, de 09/10/2026, de tratá-los juntos como a próxima feature, com
estes limites — aqui citados como 1º a 5º:

1. a frase de recurso gerada no marco passa a dizer de **qual** resultado se recorre, e a Revisão
   passa a dizer algo quando Cronograma e marcos tratam de recurso (ED-02, P0);
2. sob marco de classificação por sorteio não se exige nem se imprime arredondamento, e não se
   imprime empate no corte — validação e compositor mudam juntos (ED-03, P1);
3. Perfil só de cadastro de reserva, sem vaga imediata, não imprime quadro de vagas zerado nem frase
   de reversão; a regra de reserva no cadastro (RC-58) é decisão do responsável pelo produto (ED-12,
   P1);
4. Edital publicado não se regenera nem é reavaliado: a mudança vale só para os documentos
   compostos depois;
5. ficam fora a repetição por Perfil (ED-04), a linguagem das demais frases (ED-05) e a
   acessibilidade; achado novo vira registro, não escopo.

E as respostas do responsável pelo produto às três perguntas desta spec, na mesma data — a origem de
`D-001` a `D-003`:

6. **Frase:** o resultado é nomeado pelo **nome do marco entre aspas**, na afirmativa e na negativa;
7. **Divergência:** **aviso de conferência**, nunca impeditivo, sempre que algum marco publicar
   regra de recurso — com os prazos dos marcos e os Eventos de recurso do Cronograma lado a lado;
8. **Reserva:** sem vaga imediata, o documento **omite o quadro e a reversão**, mantém a tabela de
   Modalidades como está e não declara regra nova sobre a reserva no cadastro.

> **Faixa de identificadores.** Abre em **FR-1300**, **SC-500** e **UX-190**. O teto medido em
> 09/10/2026 em todas as worktrees era o da `066-avisos-complementares`, ainda em outra worktree e
> sem PR (mil duzentos e oitenta e três para os requisitos funcionais, quatrocentos e oitenta e oito
> para os critérios de sucesso, cento e setenta e oito para a experiência). A folga existe porque a
> `066` ainda pode crescer. **O número da pasta também:** o pedido chegou como "spec 066", e a `066`
> estava tomada por aquela worktree; esta é a `067`. As decisões desta spec nascem em `D-001`.

**A frase que governa:**

> O documento só afirma a regra que o Edital tem — dizendo a que ela se aplica, e só onde ela se
> aplica.

**E a frase que mantém o corte:**

> Esta feature tira do ato o que não é norma e dá objeto ao que é. Ela não cria regra nova, não
> reescreve as demais frases e não toca documento já publicado.

---

## Por que esta feature existe

### O problema

Desde 28/09/2026 o PDF do sistema **é o ato oficial do piloto**: o que ele imprime é norma
publicada, e só sai por Retificação. A auditoria de 08/10 classificou quatro correções como
obrigatórias antes do primeiro Edital real; a ED-01 foi feita pela `065`. As três restantes têm a
mesma natureza — o documento afirma uma regra **sem objeto** ou **onde ela não se aplica**:

- **ED-02 (P0).** O marco imprime *"Caberá recurso no prazo de 2 (dois) dias corridos, contados da
  divulgação do resultado."* — sem dizer de qual resultado. No mesmo documento, o Cronograma tem um
  período de recurso e a seção textual fala de outro objeto, e nada os relaciona. O recurso que o
  sistema processa é contra a publicação do resultado **daquele marco**
  (`doc/decisao-018-escopo-institucional-do-recurso.md`, §1), mas o candidato não tem como saber.
- **ED-03 (P1).** Sob um marco cuja ordem é **sorteada**, o documento imprime "Arredondamento: 2
  casas decimais, meio para cima" e "Empate no corte: …". Não há nota a arredondar nem empate
  possível: a ordem sorteada é total. O arredondamento sai porque a validação o **exige** de todo
  marco, e a tela o preenche com um padrão; o empate sai porque a tela o grava. Corrigir só o
  compositor deixaria a exigência sem sentido; corrigir só a validação deixaria a impressão.
- **ED-12 (P1).** Um Perfil só de cadastro de reserva, sem vaga imediata, imprime um quadro de vagas
  inteiro com zeros e a frase *"Na hipótese do não preenchimento total das vagas reservadas…"* — sobre
  vagas reservadas que não existem. Lê-se reserva de vaga onde não há vaga.

### As evidências

| # | Evidência | Onde se verifica |
|---|---|---|
| 1 | No cenário A (pós-graduação EaD, 4 polos), cada um dos 4 marcos "SORTEIO — Classificação por sorteio eletrônico" imprime "Recurso: Caberá recurso no prazo de 2 (dois) dias corridos, contados da divulgação do resultado." O resultado do sorteio sai em 16/11; o único período de recurso do Cronograma é 26/11 a 27/11, depois do "Resultado preliminar da análise documental"; e a seção "Dos Recursos" diz que só cabe recurso contra a análise documental. | `doc/auditoria-edital-pdf-2026-10-08/pdf/A-publicado.pdf`, pp. 3 a 6 e 8; §8 C1 |
| 2 | No cenário B (cadastro de reserva de tutores, 18 Perfis), cada marco "FINAL" imprime um prazo único de 3 dias; o Cronograma tem **quatro** períodos de recurso — contra a homologação das inscrições (3 dias), o resultado preliminar da prova de títulos (3), a heteroidentificação (2) e a análise documental (3). Três deles são contra atos que o sistema não modela como marco, e são legítimos. | `pdf/B-publicado.pdf`, pp. 4 e 41 a 43; snapshot `B-conteudo-publicado.json` |
| 3 | Nos 4 marcos por sorteio de A sai "Arredondamento: 2 casas decimais, meio para cima" e "Empate no corte: Havendo empate na última posição, essa quantidade não é excedida." | `pdf/A-publicado.pdf`, p. 3 e seguintes; §8 C2 e C3 |
| 4 | A montagem do cenário A foi recusada sem arredondamento no marco por sorteio: "O arredondamento do marco deve declarar `scale` como inteiro." | auditoria §3.3 |
| 5 | A tela do marco mostra e marca como obrigatórios "Casas decimais" e "Arredondamento" para todo marco, e todo marco novo nasce com 2 casas, meio para cima. A pergunta do empate, ao contrário, já fica oculta sob sorteio, e a validação já não a exige ali (`FR-928`). | tela de composição do marco; validação da publicação |
| 6 | Nos 16 Perfis de tutor presencial de B (0 vaga imediata, cadastro limitado a 15), sai uma tabela "Quadro de vagas" com as quatro listas em 0 e a frase de reversão "Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não preenchido será destinado à respectiva ampla concorrência." | `pdf/B-publicado.pdf`, pp. 8 a 38; §8 C4 |
| 7 | A Revisão repete, sob sorteio, o arredondamento e o empate que o documento imprime — ela lê as mesmas frases do compositor. | Revisão do rascunho de A |

### Por que agora, e por que só isto

São os três P0/P1 de norma que a auditoria pediu antes do primeiro Edital real, e todos mudam o
documento **só dos Editais publicados depois** (`FR-091`) — o que é argumento para fazê-los antes do
piloto. Os três são pequenos e localizados; a repetição por Perfil (ED-04) e a linguagem das demais
frases (ED-05) mudariam o documento inteiro e ficam para specs próprias.

---

## User Scenarios & Testing *(mandatory)*

**Atores.** Quem elabora o Edital (composição e Revisão), quem homologa e quem publica, com as
permissões de hoje. O candidato é o beneficiário: ele lê o documento em que o recurso tem objeto e em
que não há regra sem objeto.

### User Story 1 — O candidato sabe de qual resultado recorre (Priority: P1)

A candidata lê, sob o marco de classificação por sorteio do seu polo, *"Caberá recurso contra o
resultado de “Classificação por sorteio eletrônico”, no prazo de 2 (dois) dias corridos, contados da
divulgação desse resultado."* Ela sabe que o prazo de dois dias é contra a ordem do sorteio, e não
contra a análise documental; e pode procurar no Cronograma a divulgação desse resultado.

**Why this priority**: é o ED-02 do lado do candidato, e o único P0 restante da auditoria. O prazo de
um direito sem objeto é norma que o candidato não consegue exercer com segurança.

**Independent Test**: publicar o cenário A pelo fluxo real e conferir, no texto do documento, que os
4 marcos trazem a frase com o nome do marco e que nenhuma frase de recurso de marco termina em
"contados da divulgação do resultado".

**Acceptance Scenarios**:

1. **Given** um marco "Classificação por sorteio eletrônico" que admite recurso em 2 dias corridos,
   **When** o documento é composto, **Then** a linha de recurso do marco diz *"Caberá recurso contra
   o resultado de “Classificação por sorteio eletrônico”, no prazo de 2 (dois) dias corridos,
   contados da divulgação desse resultado."*
2. **Given** um marco que admite recurso em 1 dia, **When** o documento é composto, **Then** a frase
   diz "no prazo de 1 (um) dia corrido".
3. **Given** um marco que declara que não cabe recurso, **When** o documento é composto, **Then** a
   linha diz *"Não caberá recurso contra o resultado de “Nome do marco”."*
4. **Given** um marco que nada declara sobre recurso, **When** o documento é composto, **Then**
   nenhuma linha de recurso sai — como hoje.
5. **Given** o mesmo rascunho, **When** quem elabora abre a Revisão ou a prévia, **Then** lê a mesma
   frase que o documento publicado imprimirá.

---

### User Story 2 — Quem elabora confere os prazos de recurso dos marcos contra o Cronograma (Priority: P1)

Ao abrir a Revisão do cenário A, quem elabora vê um aviso: os marcos publicam recurso de 2 dias
contra "Classificação por sorteio eletrônico", nos 4 Perfis; o Cronograma tem um Evento de recurso,
"Prazo para interposição de recurso", de 26/11/2026 a 27/11/2026. O aviso pede que ela
confira se o Cronograma tem o período de recurso de cada resultado de marco, e se os demais períodos
são de outros atos, ditos assim no texto. Ela percebe que o período do Cronograma é o da análise
documental e que falta o do sorteio — e corrige o Cronograma ou o marco antes de submeter.

**Why this priority**: é o ED-02 do lado de quem elabora. O sistema não tem como provar a
correspondência — o tipo do Evento é texto livre e nada liga Evento a marco —, mas pode pôr os dois
lados na frente de quem decide, antes do ato irreversível (`D-002`).

**Independent Test**: compor o rascunho do cenário A e o do cenário B, abrir a Revisão de cada um e
conferir que o aviso aparece uma vez, com os marcos e os Eventos de recurso, e que a submissão segue
possível.

**Acceptance Scenarios**:

1. **Given** o rascunho do cenário A, **When** a Revisão é aberta, **Then** há um aviso de
   conferência de recurso que nomeia o marco "Classificação por sorteio eletrônico", os Perfis em que
   ele está, o prazo de 2 dias corridos, e o Evento "Prazo para interposição de recurso" com o seu
   período.
2. **Given** o rascunho do cenário B, **When** a Revisão é aberta, **Then** o aviso lista o marco
   "Classificação final pela prova de títulos" com 3 dias, nos 18 Perfis, e os **quatro** Eventos de
   recurso do Cronograma, na ordem do Cronograma.
3. **Given** um marco que admite recurso e um Cronograma sem nenhum Evento de recurso, **When** a
   Revisão é aberta, **Then** o aviso diz que o Cronograma não tem período de recurso.
4. **Given** um Edital em que nenhum marco declara regra de recurso, **When** a Revisão é aberta,
   **Then** não há aviso de conferência de recurso, ainda que o Cronograma tenha Eventos de recurso.
5. **Given** qualquer um dos casos acima, **When** quem elabora submete, quem homologa homologa e
   quem publica publica, **Then** o aviso não impede nenhum dos três atos.
6. **Given** uma Retificação de Edital publicado cujo consolidado tenha marco com regra de recurso,
   **When** quem retifica confere, **Then** o mesmo aviso aparece, e também não impede.

---

### User Story 3 — Marco por sorteio sem arredondamento e sem empate no corte (Priority: P1)

Quem elabora um marco "por sorteio" não vê mais os campos de arredondamento, e a submissão não exige
arredondamento desse marco. No documento, sob o marco por sorteio, saem "Ordem: por sorteio", o bloco
do sorteio, o recurso, o corte e a continuação — e não saem "Arredondamento" nem "Empate no corte". Um
marco por pontuação continua exigindo e imprimindo o arredondamento, e imprimindo o empate no corte.

**Why this priority**: é o ED-03 inteiro, com os dois lados que a auditoria pediu juntos.

**Independent Test**: compor um marco por sorteio sem arredondamento, submeter, homologar e publicar
sem achado impeditivo; e conferir no documento e na Revisão que nem "Arredondamento" nem "Empate no
corte" aparecem sob ele. Compor um marco por pontuação sem arredondamento e conferir que a submissão
continua recusada.

**Acceptance Scenarios**:

1. **Given** um marco que declara ordem por sorteio e nenhum arredondamento, **When** o Edital é
   submetido e publicado, **Then** nenhum achado sobre arredondamento é emitido.
2. **Given** um marco que declara ordem por pontuação, ou que não declara a forma da ordem, sem
   arredondamento, **When** o Edital é submetido, **Then** a recusa por arredondamento continua a de
   hoje.
3. **Given** um marco por sorteio que **declara** arredondamento e desfecho de empate — um rascunho
   antigo, ou uma Retificação de Edital publicado antes desta feature —, **When** o documento é
   composto, **Then** nem "Arredondamento" nem "Empate no corte" saem sob ele.
4. **Given** um marco por pontuação com corte e desfecho de empate, **When** o documento é composto,
   **Then** "Arredondamento" e "Empate no corte" saem como hoje.
5. **Given** a tela de composição de um marco por sorteio, **When** quem elabora a abre, **Then** os
   campos de arredondamento não aparecem nem são exigidos, e salvar o marco não grava arredondamento.
6. **Given** um marco por sorteio sem arredondamento que enumera Etapas, **When** alguém tenta emitir
   a classificação dele pelo caminho da ordenação por pontuação, **Then** recebe a recusa que já
   existe para marco por sorteio — e nunca um erro interno.

---

### User Story 4 — Perfil sem vaga imediata não imprime quadro zerado nem reversão (Priority: P2)

No Edital de cadastro de reserva de tutores, os 16 Perfis de tutor presencial — sem vaga imediata,
com cadastro limitado a 15 — deixam de imprimir a tabela "Quadro de vagas" com quatro zeros e a frase
de reversão sobre vagas reservadas. Continuam a imprimir o que é verdade: na tabela de Perfis, 0 vaga
imediata e o cadastro de reserva; a tabela de Modalidades, com percentual e fundamento; a forma de
convocação; os marcos. Os 2 Perfis de tutor a distância, que têm vaga imediata, continuam com quadro
e reversão — inclusive a linha "Pessoas transgênero e travestis (PTT): 0".

**Why this priority**: é o ED-12. P2 aqui porque a família está fora do piloto pela `DP-05` (o
cadastro de reserva não é convocável pelo sistema), mas o Edital de reserva é publicável e o
documento dele afirma hoje reserva de vaga onde não há vaga.

**Independent Test**: publicar o cenário B pelo fluxo real e contar, no texto do documento, as
tabelas "Quadro de vagas" (2, uma por Perfil com vaga) e as frases de reversão (2).

**Acceptance Scenarios**:

1. **Given** um Perfil com 0 vaga imediata, cadastro de reserva limitado e quadro com todas as listas
   em 0, **When** o documento é composto, **Then** a tabela "Quadro de vagas" desse Perfil não sai, a
   frase de reversão não sai, e as tabelas seguintes são numeradas sem lacuna.
2. **Given** um Perfil com 6 vagas imediatas cujo quadro tem uma lista em 0, **When** o documento é
   composto, **Then** o quadro sai inteiro, com a linha em 0, e a frase de reversão sai.
3. **Given** o Perfil do cenário 1, **When** o documento é composto, **Then** a tabela de Modalidades
   dele sai como hoje, com percentual e fundamento, e nenhuma frase nova sobre reserva no cadastro é
   acrescentada (`D-003`).
4. **Given** o mesmo Perfil, **When** quem elabora abre a Revisão, **Then** a linha da reversão
   declarada continua visível, e diz que ela não sai no documento porque o Perfil não tem vaga
   imediata.
5. **Given** uma Retificação que dá vagas imediatas a um Perfil que não tinha, **When** o consolidado
   é composto, **Then** o quadro e a reversão desse Perfil passam a sair; e, na Retificação que zera
   as vagas de um Perfil, deixam de sair.

---

### User Story 5 — O que já foi publicado não muda (Priority: P2)

Um Edital publicado antes desta feature continua com o documento que publicou: os mesmos bytes, o
mesmo resumo, servido como antes. Ele não é recomposto nem revalidado, e a página dele na gestão não
passa a exibir o aviso de recurso. Se for retificado depois, o documento consolidado da Retificação é
um documento novo, e sai pelas regras novas.

**Why this priority**: Princípio II da Constituição — Publicação é histórica e imutável. Uma regra
de composição nova não pode alcançar o ato já praticado.

**Independent Test**: publicar o cenário A antes da mudança, aplicar a mudança e conferir que o
documento servido tem os mesmos bytes; retificá-lo e conferir que o consolidado sai sem
"Arredondamento" e com a frase de recurso nova.

**Acceptance Scenarios**:

1. **Given** um Edital publicado antes desta feature, **When** a feature entra em produção, **Then**
   o documento publicado tem os mesmos bytes e o mesmo resumo criptográfico de antes.
2. **Given** o mesmo Edital, **When** alguém abre a página dele na gestão, **Then** nenhum aviso de
   conferência de recurso é exibido.
3. **Given** uma Retificação desse Edital publicada depois da feature, **When** o consolidado é
   composto, **Then** ele sai pelas regras desta feature — sem arredondamento nem empate sob sorteio,
   com o recurso nomeado e sem quadro zerado —, e o documento original continua intocado.

---

### Edge Cases

*Os casos abaixo são requisitos, e não ilustração (ver a nota em Assumptions).*

**Frase de recurso**

- **Marco sem nome** (só numa prévia de rascunho; a gravação exige nome): a frase nomeia o resultado
  pelo código do marco entre aspas; sem nome e sem código, sai a frase sem objeto de hoje — a prévia
  não inventa nome.
- **Nome do marco com aspas** ("Classificação “final”"): o nome sai como foi escrito, entre as aspas
  da frase; nada é escapado nem trocado.
- **Nome longo** (até 255 caracteres): a frase quebra como as demais, sem truncar o nome.
- **Prazo fora da tabela de números por extenso** (por exemplo, 11 dias): sai só o algarismo, como
  hoje.
- **Unidade do prazo**: o sistema só publica prazo em dias corridos; a frase não muda de unidade.
- **Dois marcos no mesmo Perfil**: cada um nomeia o seu resultado.
- **O mesmo marco (mesmo nome) em vários Perfis**: cada Perfil imprime a frase com o mesmo nome — a
  repetição é o ED-04, fora desta feature.

**Aviso de conferência de recurso**

- **Evento de recurso** é o Evento do Cronograma cujo tipo ou descrição tem uma palavra iniciada por
  "recurs" (recurso, recursos, recursal), sem distinguir maiúsculas. "Prazo recursal" conta;
  "Concurso" e "percurso" não contam.
- **Evento cancelado** continua listado, sem marca: o aviso mostra o Cronograma como o documento o
  imprime, e o documento não marca o cancelado.
- **Evento de um instante** (sem término) é listado com a data e a hora de início.
- **Marcos com o mesmo nome e o mesmo prazo em vários Perfis** são uma linha só do aviso, com os
  Perfis enumerados; mesmo nome e prazos diferentes são linhas diferentes.
- **Marco que declara que não cabe recurso** entra no aviso como "não cabe recurso": é regra de
  recurso publicada, e um período de recurso no Cronograma contra o mesmo resultado a contradiria.
- **Nenhum marco declara regra de recurso**: não há aviso, mesmo com Eventos de recurso — recursos
  contra atos fora dos marcos (homologação, heteroidentificação) são legítimos.
- **Retificação**: o aviso é calculado sobre o consolidado, como aviso; nunca impede.
- **Edital publicado**, fora de uma Retificação em curso: o aviso não é calculado nem exibido.

**Sorteio**

- **Marco que não declara a forma da ordem** (acervo anterior à `030`) continua exigindo e imprimindo
  arredondamento e empate, como sempre saiu — mesmo que tenha método de sorteio. A regra desta feature
  depende da forma **declarada**.
- **Marco por sorteio com arredondamento malformado** (escala fora da faixa, modo desconhecido),
  vindo pela API: a forma do valor declarado continua conferida, como o desfecho de empate declarado
  sob sorteio já é (`FR-928`); só a **ausência** deixa de ser recusada.
- **Retificação que muda um marco de pontuação para sorteio**: o arredondamento declarado deixa de
  sair no consolidado; o que a Retificação mudou continua dito pelo quadro de alterações de hoje.
- **Retificação que muda de sorteio para pontuação** sem declarar arredondamento: a validação recusa,
  como recusa todo marco por pontuação sem arredondamento.
- **Troca da forma da ordem na tela**: ao passar de sorteio para pontuação, os campos de
  arredondamento voltam, preenchidos com o padrão de marco novo e visíveis antes de salvar; ao passar
  de pontuação para sorteio, somem, e o arredondamento não é gravado.

**Perfil sem vaga imediata**

- **Perfil sem vaga imediata** é o que tem 0 vaga imediata **e** todas as linhas do quadro em 0. Um
  Perfil com 0 no total e alguma linha positiva é incoerente, a validação de hoje o recusa, e o
  compositor o trata como Perfil com vaga — imprime o quadro, para que o erro se veja.
- **Perfil sem vaga imediata e sem cadastro de reserva**: o compositor aplica a mesma regra; se a
  validação deixar passar, nada de quadro e de reversão sai.
- **Perfil sem quadro declarado** (acervo anterior à `025`): nada muda — o quadro já não sai.
- **Tabela de Perfis** do Edital: continua com "Vagas imediatas: 0" e o cadastro de reserva; a linha
  de total continua omitida quando o total do Edital é 0, como hoje.
- **Numeração das tabelas**: as tabelas seguintes avançam sem lacuna, e a lista de itens que a
  conferência de remissões da `065` usa ("Tabela N") segue a mesma regra do documento.
- **Validação**: nada muda — a reversão declarada continua aceita, e o aviso de que a convocação do
  Perfil só de reserva é feita fora do sistema continua o mesmo.

---

## Requirements *(mandatory)*

### Functional Requirements

**Frase de recurso do marco (ED-02, `D-001`)**

- **FR-1300**: A frase de recurso de marco que admite recurso com prazo declarado MUST nomear o
  resultado pelo nome do marco entre aspas tipográficas: *"Caberá recurso contra o resultado de
  “{nome}”, no prazo de {N} ({por extenso}) {dias corridos | dia corrido}, contados da divulgação
  desse resultado."* O número por extenso e o singular seguem a regra de hoje (`FR-030`).
- **FR-1301**: A frase de marco que declara que não cabe recurso MUST ser *"Não caberá recurso contra
  o resultado de “{nome}”."*
- **FR-1302**: O nome é o do marco, na grafia publicada; sem nome, o código; sem os dois — o que só
  uma prévia de rascunho pode ter —, a frase MUST sair como hoje, sem objeto, e a negativa como "Não
  caberá recurso contra o resultado deste marco." O documento não inventa nome.
- **FR-1303**: Marco que nada declara sobre recurso MUST continuar sem frase de recurso (`FR-028`,
  `FR-113`).
- **FR-1304**: A frase MUST ser uma só para o documento publicado, a prévia, o consolidado de
  Retificação e a Revisão — composta num único lugar e lida pelos quatro.

**Aviso de conferência de recurso (ED-02, `D-002`)**

- **FR-1305**: É **Evento de recurso** o Evento do Cronograma cujo tipo ou descrição contém uma
  palavra iniciada por "recurs", sem distinguir maiúsculas de minúsculas.
- **FR-1306**: Quando ao menos um marco do Edital declarar regra de recurso — que cabe, com prazo, ou
  que não cabe —, a validação do Edital MUST emitir **um** aviso de conferência de recurso, que
  enumera: (a) cada regra de recurso de marco — nome do marco, Perfis em que está e o prazo, ou "não
  cabe recurso" —, agrupando numa linha marcos de mesmo nome e mesma regra; e (b) cada Evento de
  recurso, na ordem do Cronograma, como o documento o imprime — a descrição (ou o tipo, sem
  descrição), o início e o término —, ou a afirmação de que o Cronograma não tem Evento de recurso.
- **FR-1307**: O aviso MUST pedir que quem elabora confira se o Cronograma tem o período de recurso
  de cada resultado de marco, e se os demais períodos de recurso são contra outros atos, ditos assim
  no texto do Edital. Ele MUST NOT afirmar que algum Evento corresponde a algum marco, nem que falta
  ou sobra período.
- **FR-1308**: Sem regra de recurso declarada em marco algum, o aviso MUST NOT ser emitido, ainda que
  o Cronograma tenha Eventos de recurso.
- **FR-1309**: O aviso MUST ter severidade de aviso na submissão, na homologação, na publicação e na
  Retificação, e MUST NOT impedir nenhum desses atos.
- **FR-1310**: O aviso MUST NOT mudar o documento, o conteúdo publicado nem o Cronograma.

**Sorteio sem arredondamento e sem empate no corte (ED-03)**

- **FR-1311**: A validação do Edital MUST NOT exigir arredondamento de marco que declara ordem **por
  sorteio**. Marco que declara ordem por pontuação, ou que não declara a forma, MUST continuar
  exigindo-o como hoje.
- **FR-1312**: Arredondamento **declarado** em marco por sorteio MUST continuar conferido na forma
  (escala e modo válidos), como o desfecho de empate declarado sob sorteio (`FR-928`).
- **FR-1313**: O documento MUST NOT imprimir "Arredondamento" sob marco que declara ordem por sorteio,
  ainda que o arredondamento esteja declarado.
- **FR-1314**: O documento MUST NOT imprimir "Empate no corte" sob marco que declara ordem por
  sorteio, ainda que o desfecho de empate esteja declarado. A validação do desfecho sob sorteio fica
  como está (`FR-928`).
- **FR-1315**: A Revisão MUST seguir `FR-1313` e `FR-1314`: sob marco por sorteio, não lista
  arredondamento nem empate no corte.
- **FR-1316**: A tela de composição do marco MUST NOT mostrar nem exigir os campos de arredondamento
  de marco por sorteio, e salvar um marco por sorteio pela tela MUST NOT gravar arredondamento. Ao
  passar para ordem por pontuação, os campos MUST voltar, preenchidos com o padrão de marco novo.
- **FR-1317**: A tela da Retificação MUST NOT anunciar, para o arredondamento ausente de marco por
  sorteio, que a publicação será impedida.
- **FR-1318**: Emitir a classificação de um marco por sorteio pelo caminho da ordenação por pontuação
  MUST resultar na recusa que já existe para marco por sorteio, também quando o marco não declara
  arredondamento e enumera Etapas — e nunca em erro interno.
- **FR-1319**: A ordem sorteada, a divulgação do resultado e a reprodução do sorteio MUST continuar
  as mesmas: nenhuma delas lê arredondamento.

**Perfil sem vaga imediata (ED-12, `D-003`)**

- **FR-1320**: É **Perfil sem vaga imediata** o que declara 0 vaga imediata e cujo quadro de vagas
  tem todas as linhas em 0.
- **FR-1321**: Para Perfil sem vaga imediata, o documento MUST NOT imprimir a tabela "Quadro de vagas"
  nem a frase de reversão. As tabelas seguintes MUST ser numeradas sem lacuna, e a lista de itens do
  documento usada pela conferência de remissões (`FR-1205`) MUST seguir a mesma regra.
- **FR-1322**: O restante do Perfil sem vaga imediata MUST sair como hoje — a linha dele na tabela de
  Perfis, a tabela de Modalidades com percentual e fundamento, a forma de convocação e os marcos — e
  nenhuma frase nova sobre a reserva no cadastro MUST ser acrescentada.
- **FR-1323**: Perfil com ao menos uma vaga imediata MUST continuar com quadro e reversão como hoje,
  inclusive as linhas em 0.
- **FR-1324**: A validação do Perfil sem vaga imediata MUST continuar a de hoje: a reversão declarada
  é aceita, e o aviso de convocação feita fora do sistema não muda.

**O que já foi publicado (Princípio II)**

- **FR-1325**: Documento já gerado — de Publicação original ou de Retificação — MUST NOT ser
  recomposto, regenerado nem revalidado; os bytes servidos e o resumo continuam os mesmos.
- **FR-1326**: Documento composto depois desta feature — publicação, prévia e consolidado de
  Retificação, inclusive de Edital publicado antes dela — MUST sair pelas regras desta feature, como o
  `FR-1196` fez com o layout das atribuições.
- **FR-1327**: Esta feature MUST NOT mudar a forma do conteúdo canônico publicado nem a versão do seu
  esquema: o arredondamento continua um campo do marco, que pode estar vazio sob sorteio.
- **FR-1328**: O aviso de conferência de recurso MUST NOT ser calculado nem exibido para Edital já
  publicado, salvo sobre o consolidado de uma Retificação em composição.

### Requisitos de experiência

- **UX-190**: O aviso de conferência de recurso MUST usar a linguagem de quem elabora — "marco",
  "Perfil", "prazo", "Cronograma", "Evento" —, com o nome do marco e o Evento como o documento o
  imprime; nenhum código interno, caminho ou nome de campo.
- **UX-191**: O aviso MUST levar à etapa do Cronograma, onde se corrige o período, e nomear os Perfis
  dos marcos, onde se corrige a regra.
- **UX-192**: Na Revisão, a reversão declarada de Perfil sem vaga imediata MUST continuar visível,
  acompanhada da informação de que não sai no documento porque o Perfil não tem vaga imediata.
- **UX-193**: A ajuda da tela do marco MUST dizer que o arredondamento se aplica só à ordem por
  pontuação.

### Exemplos de mensagem e de frase

Exemplos normativos do tom e do conteúdo; a redação final é do plano, desde que cumpra `FR-1300` a
`FR-1308` e `UX-190` a `UX-193`. Os dois primeiros são do cenário A; o terceiro, do cenário B.

| Onde | Texto |
|---|---|
| Documento, marco que admite recurso | Recurso: Caberá recurso contra o resultado de “Classificação por sorteio eletrônico”, no prazo de 2 (dois) dias corridos, contados da divulgação desse resultado. |
| Revisão, aviso (cenário A) | **Prazos de recurso a conferir.** Os marcos publicam recurso: “Classificação por sorteio eletrônico” (INF-BJN, INF-IUN, INF-SMT, INF-VAL) — 2 (dois) dias corridos, contados da divulgação desse resultado. O Cronograma tem 1 Evento de recurso: Prazo para interposição de recurso — de 26/11/2026, às 00h, a 27/11/2026, às 23h59. O sistema não relaciona o Cronograma aos marcos: confira se há período de recurso para o resultado de cada marco e se os demais períodos são contra outros atos, ditos assim no texto. |
| Revisão, aviso (cenário B, resumido) | **Prazos de recurso a conferir.** Os marcos publicam recurso: “Classificação final pela prova de títulos” (18 Perfis) — 3 (três) dias corridos… O Cronograma tem 4 Eventos de recurso: Recurso contra a homologação preliminar das inscrições — de 31/10/2026, às 00h, a 02/11/2026, às 23h59; Recurso contra o resultado preliminar da prova de títulos — …; … |
| Revisão, sem Evento de recurso | … O Cronograma não tem Evento de recurso: o resultado destes marcos não tem período de recurso publicado no Cronograma. … |
| Revisão, reversão de Perfil sem vaga imediata | Reverter vaga reservada não preenchida para a ampla concorrência: a quantidade que ficou sem preencher — não sai no documento: o Perfil não tem vaga imediata. |

### Severidade

| Achado | Severidade | Base |
|---|---|---|
| Conferência de recurso entre marcos e Cronograma | **Aviso**, no Edital e na Retificação | `D-002`; o tipo do Evento é texto livre, e a correspondência não é provável pelo sistema |
| Arredondamento ausente em marco por sorteio | **Nenhum** (deixa de ser impeditivo) | ED-03; não há nota a arredondar |
| Arredondamento ausente em marco por pontuação ou sem forma declarada | **Impeditivo**, como hoje | `FR-068` |
| Arredondamento ou desfecho de empate malformado, sob sorteio | **Impeditivo**, como hoje | `FR-928`, `FR-1312` |

### Key Entities

Nenhuma entidade nova, nenhum campo novo, nenhuma migration. A feature lê:

- **Marco classificatório** — nome, forma da ordem declarada, regra de recurso, arredondamento,
  regra de corte e desfecho de empate.
- **Evento do Cronograma** — tipo, descrição, início, término e fase, como o documento os imprime.
- **Perfil** — vagas imediatas, quadro de vagas, cadastro de reserva e reversão declarada.
- **Documento publicado** — os bytes gravados no ato de publicar, que não mudam.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-500**: No cenário A republicado pelo fluxo real, os 4 marcos trazem a frase de recurso que
  nomeia “Classificação por sorteio eletrônico”, e **nenhuma** linha "Arredondamento" nem "Empate no
  corte" sai sob eles.
- **SC-501**: No cenário B republicado pelo fluxo real, saem **2** tabelas "Quadro de vagas" e **2**
  frases de reversão (os Perfis de tutor a distância), contra 18 e 18 hoje; os 16 Perfis de tutor
  presencial continuam com a tabela de Modalidades, e o documento fica mais curto.
- **SC-502**: A diferença de texto entre os documentos dos cenários A e B compostos depois da feature
  e os PDFs da auditoria contém **só** as mudanças pretendidas — as frases de recurso, as linhas de
  arredondamento e de empate sob sorteio, os quadros e as reversões dos Perfis sem vaga imediata — e
  as consequências delas na numeração das tabelas, na paginação e no total de páginas.
- **SC-503**: Um marco por sorteio sem arredondamento é submetido, homologado e publicado sem achado
  impeditivo; um marco por pontuação sem arredondamento continua recusado na submissão.
- **SC-504**: A Revisão dos rascunhos de A e de B mostra o aviso de conferência de recurso uma vez,
  com os marcos e os Eventos de recurso, e os dois Editais são submetidos e publicados com ele.
- **SC-505**: O documento da fixture de contrato — Edital sem sorteio, sem regra de recurso e sem
  Perfil sem vaga imediata — sai com **os mesmos bytes** de antes da feature.
- **SC-506**: Um Edital publicado antes da feature é servido, depois dela, com os mesmos bytes e o
  mesmo resumo.
- **SC-507**: A verificação do repositório — lint, checagens e a suíte contra PostgreSQL — passa.

### O que esta feature não cobre, deliberadamente

- **A regra de reserva no cadastro (RC-58)**: como os percentuais se aplicam às convocações do
  cadastro de reserva continua não declarado pelo sistema, e a convocação desses Perfis continua fora
  dele (`DP-05`). Fica registrado, não decidido.
- **Relacionar Evento do Cronograma a marco** estruturalmente (um campo que diga "este período é o
  recurso deste marco"); e **impedir** a publicação por divergência entre os dois.
- **A repetição por Perfil** (ED-04), inclusive da frase de recurso e do bloco do sorteio.
- **A linguagem das demais frases geradas** (ED-05): "Corte", "Continuação", "recorte", "Semente",
  "submetidas" e as outras de L1 a L17, exceto a de recurso (L10) e a omissão do arredondamento (L7).
- **Acessibilidade e leitura digital** (ED-07, ED-08, ED-13, ED-14), o endereço do certame (ED-09) e a
  autoridade sem nome (ED-10).
- **Recompor, regenerar ou reavaliar** documento já publicado.

---

## Decisões

Fechadas pelo responsável pelo produto em 09/10/2026, antes do plano (6º a 8º do cabeçalho). As
alternativas descartadas ficam escritas, porque são a razão da escolha.

#### D-001 — O resultado é nomeado pelo nome do marco entre aspas

*"Caberá recurso contra o resultado de “Classificação por sorteio eletrônico”, no prazo de 2 (dois)
dias corridos, contados da divulgação desse resultado."*; na negativa, *"Não caberá recurso contra o
resultado de “…”."* **Por quê:** o nome do marco é o que o liga ao Cronograma e ao texto, e as aspas
dispensam o artigo — o nome não tem gênero conhecido, e "da Classificação…", a sugestão L10 da
auditoria, não se gera com segurança. **Descartadas:** acrescentar o código do Perfil — mais preciso,
e repetitivo dentro da própria subseção do Perfil —; e "contra o resultado desta classificação", sem
o nome — mais curta, mas não se cita isolada. Atende `FR-1300` a `FR-1302`.

#### D-002 — Aviso de conferência, nunca impeditivo, sempre que algum marco publicar regra de recurso

**Por quê:** o tipo do Evento é texto livre e nada liga Evento a marco; uma regra de direito apoiada
em texto livre é o que o próprio modelo do Cronograma desaconselha. Nos dois cenários da auditoria os
prazos coincidem em duração, e o B tem três recursos legítimos contra atos fora dos marcos — uma
detecção "só da divergência" não dispararia em nenhum dos dois casos que a auditoria cita.
**Descartadas:** aviso só quando a divergência é detectável (marco com recurso e Cronograma sem
Evento de recurso; nenhum Evento com a duração do prazo) — silencioso em A e em B —; e impeditivo
quando o marco admite recurso e o Cronograma não tem Evento de recurso — regra de direito sobre texto
livre. **Consequência aceita:** o aviso aparece em todo Edital cujo marco publica recurso, e só a
conferência humana resolve a divergência de objeto. Atende `FR-1305` a `FR-1310`.

#### D-003 — Sem vaga imediata, o documento omite o quadro e a reversão, e não declara regra nova

**Por quê:** é a sugestão literal da auditoria, e tira do ato a afirmação de reserva de vaga onde não
há vaga sem criar norma que o sistema não executa — a convocação desses Perfis é feita fora dele
(`DP-05`). **Descartadas:** trocar a reversão por uma frase gerada que declare a regra no cadastro
("aplicam-se os percentuais da Tabela N…") — norma nova, executada fora do sistema —; e omitir também
o percentual — o documento deixaria de afirmar reserva que a lei de cotas pode exigir para as vagas
que surgirem. **Consequência aceita:** como a reserva se aplica ao cadastro continua dependendo do
texto do gestor, e o RC-58 continua aberto. Atende `FR-1320` a `FR-1324`.

## Limitações remanescentes

- O aviso de conferência **mostra**, e não **prova**: no cenário A, o único período de recurso do
  Cronograma é o da análise documental, e o do sorteio falta — o aviso põe os dois lados na tela, mas
  só quem elabora conclui que falta um.
- O aviso aparece sempre que um marco publica recurso, inclusive quando tudo está certo; não há como
  dispensá-lo (`D-002`).
- Evento de recurso cujo tipo e descrição não usam a palavra ("Prazo para contestação") não entra no
  aviso.
- O Perfil sem vaga imediata continua sem regra publicada para a reserva no cadastro, salvo o que o
  gestor escrever (`D-003`).
- Os Editais já publicados continuam com a frase sem objeto, o arredondamento sob sorteio e o quadro
  zerado até uma Retificação.

## Assumptions

- O consolidado da Retificação é um documento novo e segue a composição vigente no momento em que é
  composto, pelo mesmo princípio do `FR-1196` da `064`; o que a Retificação mudou continua dito pelo
  quadro de alterações de hoje, e as diferenças de composição que esta feature introduz no
  consolidado de um Edital antigo não são alterações da Retificação.
- O marco por sorteio continua sem consumidor de arredondamento: a ordem sorteada é total e a posição
  é única; a divulgação formata pontuação com escala padrão quando o marco não a declara, e o marco por
  sorteio não tem pontuação a formatar.
- Os dois cenários da auditoria (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`) representam os dois
  casos-alvo — sorteio com recurso, e cadastro de reserva com Perfis sem vaga — e são executados pelo
  fluxo real em bancos de validação novos, com dados fictícios.
- Os casos-limite desta spec são requisitos e entram na matriz de rastreabilidade com teste próprio,
  como os `FR-` e os `SC-`.
