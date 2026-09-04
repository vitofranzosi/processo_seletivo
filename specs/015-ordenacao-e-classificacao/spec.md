# Feature Specification: Ordenação e Classificação

**Feature Branch**: `claude/spec-015-ordenacao-classificacao-4e0ab0`

**Created**: 2026-09-04

**Status**: Draft

**Input**: Dado um conjunto de participantes e uma regra publicada, o sistema produz a ordem entre
eles, de modo reproduzível e auditável — e essa ordem é constituída por ato, não por consulta. A
capacidade é uma só, exercida em marcos classificatórios identificáveis: sobre o resultado de uma
Etapa, como insumo do corte, e sobre a combinação de N Etapas, como classificação final.

## 1. O que a 013 entregou, e que a 015 herda como contrato

Esta feature começa depois da consolidação e não redefine seus conceitos:

- para uma mesma Inscrição × Etapa existe **no máximo um** `ResultadoEtapa` oficial vigente (I-6),
  imutável, com consequência `HABILITADA` ou `ELIMINADA` e o motivo que a nomeia;
- o Resultado guarda a conclusão **conforme a forma** — `PONTUADA` com pontuação, `DECISORIA` com
  sentido —, e a Etapa decisória não produz número nenhum;
- consolidar é ato explícito, autorizado, em lote e idempotente, com trilha, autor e instante;
- `progressao` responde qual é a Etapa anterior a partir do conteúdo publicado; `compatibilidade`
  compara a norma que governou com a vigente onde importa; `prontidao` particiona os participantes
  da Etapa em estados que somam o total;
- a Etapa publicada **já traz** `order`, `weight`, `eliminatory`, `classificatory`, `minimumScore`
  e `maximumScore`, na versão canônica 6. A 015 lê esse conteúdo;
- a 013 excluiu, no §5, exatamente o que esta feature precisa: combinação de avaliações, ponderação
  entre Etapas, classificação global, ordenação, critérios de empate — **e o campo normativo novo
  que os declara, com esquema, elaboração, documento e catálogo de Retificação**. A conta vem
  inteira para cá;
- `ModalidadeConcorrencia` existe com identidade estável por Perfil, viaja no conteúdo publicado
  como `competitionModalities`, é endereçada pela Retificação, restringe Documento Exigido e é
  escolhida pelo candidato na inscrição. Ela é **declarada e não verificada**: nenhuma comissão
  confirmou o fato que a sustenta, e esta feature não inicia essa verificação;
- D-2 das decisões pré-vertical entrega os fatos do candidato que o Edital declara e a inscrição
  congela na submissão. Sem eles não há desempate por idade nem por tempo de experiência;
- D-1 acrescenta `origem` e `versao` ao `ResultadoEtapa`. É extensão da 013, consumida por esta
  feature e não produzida por ela.

> Os Resultados de Etapa existem, são oficiais e imutáveis; falta transformá-los em ordem — e
> transformar em ordem é ato, não consulta.

## 2. Decisões fechadas antes do planejamento

### D-001 — Ordenar é uma capacidade, exercida em marcos identificáveis

Não existem "ranking intermediário" e "classificação de verdade" como coisas de naturezas
diferentes. É o mesmo ato, com regras de origem distintas: sobre uma Etapa, ou sobre a combinação
de N Etapas.

O **marco classificatório** é declarado no conteúdo publicado e tem **identidade estável**, no
padrão da 004 — nunca posição em lista, nunca enum `INTERMEDIARIA`/`FINAL` inventado no domínio.
Sem identidade do marco não há unicidade do ato vigente, não há sucessão entre emissões, não há
obsolescência endereçável e não há sobre o que a 017 publicar ou a 018 recorrer.

Para o mesmo Processo e Perfil pode haver ordenação pós-títulos, outra pós-entrevista e outra
depois de recurso. Há Editais que publicam a ordem intermediária, recebem recurso sobre ela e a
republicam antes de convocar para a Etapa seguinte: os dois marcos são atos plenos.

### D-002 — Calcular não é emitir

```
calcular(entradas, regra_versionada)  →  proposta determinística
                                      →  EMITIR (ato autorizado)
                                      →  snapshot oficial imutável
```

A computação é pura, reproduzível e pode ser executada quantas vezes for necessário. O artefato é
histórico, versionado e emitido por quem tem autoridade — **nunca regenerado em silêncio quando a
tela abre**. Abrir a tela calcula e mostra; não emite, não grava e não substitui.

### D-003 — O universo classificável delimita a obsolescência

Entrada nova torna o snapshot vigente **obsoleto, não inválido**. Alguém autorizado emite o
próximo; o anterior permanece legível sob a norma que o governou.

Nem todo Resultado novo obsoleta toda ordem emitida. O ato declara o universo sobre o qual foi
produzido — Processo, Edital, Perfil, marco, participantes considerados, Resultados antecedentes
que entraram **e a regra do marco na versão normativa sob a qual foi calculada** —, e só mudança
**nesse** universo o desatualiza.

A regra faz parte do universo pelo mesmo motivo que as entradas: uma Retificação que altera a
operação, os pesos que ela lê ou a ordem dos critérios de desempate muda o que o cálculo produz sem
tocar em Resultado algum. Os casos que forçam a regra são três: Resultado tardio, Retificação que
alcança a regra do marco e Perfis distintos no mesmo Edital. Resultado revisto entra quando a 018
existir.

### D-004 — Desempate é lista ordenada de critérios parametrizados

O desempate não é uma sequência hardcoded nem um único campo da Etapa: é conteúdo normativo
estruturado, composto por critérios **ordenados e parametrizados**, aplicados na ordem declarada,
que viajam no snapshot e são retificáveis.

O motor conhece tipos executáveis de critério — não há como executar o que não se sabe interpretar.
O que ele **não** pode é decidir quais critérios existem, em que ordem se aplicam ou qual parâmetro
cada um recebe. Os critérios consomem pontuação de Etapa específica, endereçada por identidade
estável do conteúdo publicado, e fatos do candidato congelados na inscrição (D-2).

**Valor ausente é declarado, nunca inferido.** Inscrição submetida antes de o Edital declarar um
fato não o congelou, e Etapa decisória não produz número: o critério que os consome precisa dizer o
que fazer quando o valor não existe. O silêncio não vira zero, não vira último lugar e não vira
critério pulado — ele impede a publicação da regra.

### D-005 — Empate residual tem desfecho explícito, e o sistema não inventa ordem

Esgotada a lista publicada de critérios, o sistema **não** ordena por UUID, nome, horário de
criação ou ordem em que o banco devolveu as linhas. O empate residual é declarado como tal, e a
interface mostra que ele existe.

### D-006 — Proveniência é reprodução, não registro

Toda ordem emitida identifica os Resultados de Etapa que entraram nela, a regra normativa vigente
que a governou e os valores usados em cada critério de desempate, **de modo que a mesma ordem seja
reproduzível a partir deles** (I-2). Registrar o que foi usado e chegar de novo ao mesmo resultado
são coisas distintas, e a Constituição pede a segunda.

Disso decorre uma proibição, e não uma máquina de versões: mudança futura na implementação não pode
alterar silenciosamente a reprodução de classificações históricas.

### D-007 — A autoridade é consumida, não inventada

Emitir é ato explícito, autorizado e auditável (I-5, Princípio III). A 015 registra quem emitiu,
sob qual autoria e em que instante, pelo caminho que `resultado:consolidar` já percorre. Ela **não**
define quem é a autoridade competente: isso vem das capacidades já constituídas.

### D-008 — A regra de classificação é conteúdo publicado, com a conta que isso implica

A regra do marco e os critérios de desempate são conteúdo normativo publicado. Logo: esquema
canônico com elevação de `SCHEMA_VERSION` e caminho de leitura das versões anteriores, elaboração
na interface administrativa, presença no documento publicado e entrada no catálogo de Retificação
endereçada por identidade estável.

D-2 e D-3 das decisões pré-vertical elevam a mesma versão. Planejadas juntas, é uma elevação;
separadas, são três, cada uma com seu caminho de leitura.

### D-009 — Modalidade é lida, não decidida

A ordem registra a modalidade declarada de cada participante, porque a 014 é consciente de
modalidade e a 016 ocupará vagas por ela. Esta feature **não** verifica elegibilidade, não separa
listas por modalidade e não aplica percentual ou reserva. Ela torna o fato legível na ordem.

## 3. Problema

Os Resultados de Etapa são oficiais, imutáveis e auditáveis, e ainda assim ninguém consegue dizer
quem ficou em primeiro. A ordem é produzida fora do sistema, em planilha, e volta como número
digitado — sem regra publicada que a governe, sem proveniência que a reproduza e sem ato que a
constitua. É a mesma apuração paralela que o projeto existe para eliminar, um degrau acima.

E, sem ordem, o corte da 014 não tem sobre o que operar e a ocupação da 016 não tem quem alocar.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Declarar a regra do marco e o desempate no Edital (Priority: P1)

Quem elabora o Edital declara, para um Perfil, um marco classificatório: qual é a regra que produz
a ordem, quais Etapas entram nela e qual é a lista ordenada de critérios de desempate, cada um com
seu parâmetro. Publica, e a regra passa a viajar no documento e a responder pela mesma cadeia de
vigência que peso e nota mínima.

**Why this priority**: sem conteúdo publicado não há o que executar. Nenhuma outra história existe
antes desta, e é ela que impede a regra de nascer escondida no código.

**Independent Test**: elaborar um marco com dois critérios de desempate, publicar o Edital e
verificar que a regra aparece no documento publicado e no conteúdo canônico, endereçada por
identidade estável.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração com Etapas classificatórias, **When** quem elabora declara um
   marco com a regra e dois critérios de desempate em ordem, **Then** o marco recebe identidade
   estável e é publicado com o Edital.
2. **Given** um marco publicado, **When** uma Retificação reordena os critérios de desempate,
   **Then** a nova ordem vale da vigência em diante e a publicação anterior permanece íntegra.
3. **Given** um marco cujo critério aponta uma Etapa, **When** essa Etapa é endereçada, **Then** o
   endereçamento é por identidade e sobrevive à inserção de outra Etapa antes dela.

---

### User Story 2 — Emitir a ordem de um marco (Priority: P1)

A presidência abre o marco, vê a ordem calculada a partir dos Resultados oficiais e da regra
vigente, confere, e **emite**. O que fica gravado é um snapshot imutável, com autor, instante,
universo, entradas e os valores usados em cada critério de desempate.

**Why this priority**: é a capacidade que a feature existe para entregar, e a única que produz o
insumo do corte da 014.

**Independent Test**: com Resultados consolidados numa Etapa, calcular e emitir a ordem do marco, e
verificar que o snapshot emitido é imutável e traz posição, participante e proveniência.

**Acceptance Scenarios**:

1. **Given** Resultados oficiais de uma Etapa e regra vigente, **When** a presidência abre o marco,
   **Then** vê a ordem calculada e nada foi gravado.
2. **Given** a ordem calculada, **When** quem tem autoridade emite, **Then** o snapshot passa a
   existir com autor, instante e a versão normativa que o governou.
3. **Given** um snapshot emitido, **When** qualquer ator tenta alterá-lo, **Then** a alteração é
   recusada sem efeito e o snapshot permanece idêntico.
4. **Given** quem não tem autoridade para emitir, **When** tenta emitir, **Then** a operação é
   recusada e o ato não acontece.
5. **Given** um marco que combina duas Etapas em que um participante não tem Resultado em uma
   delas, **When** a ordem é calculada, **Then** o participante é nomeado como não classificável,
   com o motivo, e não recebe posição arbitrária.

---

### User Story 3 — Enxergar que a ordem vigente ficou para trás (Priority: P2)

Um Resultado novo entra no universo de um marco já emitido. Quem administra vê, na própria tela do
marco, que o vigente **está obsoleto** e em que ele difere do computado agora — e decide emitir o
próximo ato, ou não.

**Why this priority**: capacidade que o domínio sustenta e nenhuma interface alcança não está
entregue (Princípio VI). Sem isso, a obsolescência é invisível e o vigente mente em silêncio.

**Independent Test**: emitir uma ordem, consolidar um Resultado tardio no mesmo universo e
verificar que a tela marca o vigente como obsoleto e mostra a diferença.

**Acceptance Scenarios**:

1. **Given** ordem vigente e um Resultado novo no mesmo universo, **When** a tela do marco é
   aberta, **Then** o vigente aparece como obsoleto, com a diferença em relação ao computado.
2. **Given** ordem vigente e um Resultado novo em **outro** universo — outro Perfil, outro marco —,
   **When** a tela é aberta, **Then** o vigente continua atual e nada é marcado.
3. **Given** um vigente obsoleto, **When** ninguém emite, **Then** ele continua sendo o vigente,
   permanece consultável e não é substituído por efeito colateral de leitura.

---

### User Story 4 — Auditar e reproduzir uma ordem emitida (Priority: P2)

Auditoria abre um ato emitido, vê quais Resultados entraram, sob qual versão normativa, e quais
valores cada critério de desempate usou para separar dois participantes — e obtém de novo a mesma
ordem a partir disso.

**Why this priority**: é o que distingue esta feature de uma planilha versionada. Sem reprodução, a
proveniência é decorativa.

**Independent Test**: reproduzir um ato emitido a partir de sua proveniência e comparar posição a
posição com o snapshot.

**Acceptance Scenarios**:

1. **Given** um ato emitido, **When** auditoria consulta sua proveniência, **Then** identifica em
   uma jornada as entradas, a versão normativa e os valores de desempate usados.
2. **Given** a proveniência de um ato antigo, **When** a ordem é reproduzida a partir dela,
   **Then** o resultado é idêntico ao snapshot, posição a posição.
3. **Given** dois participantes separados por um critério de desempate, **When** auditoria consulta
   a posição, **Then** vê qual critério os separou e com quais valores.

---

### User Story 5 — Suceder um ato por outro no mesmo marco (Priority: P3)

Um Resultado tardio entra no universo, ou uma Retificação alcança a regra do marco. A presidência
emite um novo ato no mesmo marco: o anterior não é apagado — deixa de ser o vigente e continua
consultável, com o motivo da sucessão.

Revisão ou superação de Resultado não é caminho desta feature: a 013 admite um único Resultado
imutável por Inscrição × Etapa, e superá-lo é da 018. A sucessão aqui nasce compatível com ela, e
não a pressupõe.

**Why this priority**: é o que torna a feature compatível com publicação (017) e recurso (018) sem
reescrevê-la depois.

**Independent Test**: emitir dois atos no mesmo marco e verificar que há exatamente um vigente e
que o anterior permanece íntegro e consultável.

**Acceptance Scenarios**:

1. **Given** um ato vigente num marco, **When** um Resultado tardio entra no universo e outro ato é
   emitido, **Then** passa a haver exatamente um vigente e o anterior permanece legível sob a norma
   que o governou.
2. **Given** um ato vigente, **When** uma Retificação altera a ordem dos critérios de desempate e
   um novo ato é emitido, **Then** o novo reflete a regra vigente e o anterior permanece calculado
   sob a anterior.
3. **Given** dois atos no mesmo marco, **When** alguém consulta o histórico, **Then** vê a sucessão
   com autor, instante e motivo de cada um.

---

### Edge Cases

- Marco cujo universo não tem nenhum participante classificável: a ordem emitida é vazia, e o
  motivo aparece — não é erro, e não é ausência de ato.
- Etapa decisória dentro de um marco que combina pontuação: não há número a somar, e a regra
  precisa dizer se ela participa como filtro ou não participa; o silêncio não vira zero.
- Participante com Resultado em todas as Etapas do marco, mas eliminado em uma delas.
- Empate que sobrevive a todos os critérios declarados.
- Critério de desempate que aponta Etapa removida por Retificação posterior à emissão.
- Critério que consome fato do candidato que aquela inscrição não congelou — porque foi submetida
  antes de o fato ser declarado.
- Dois atos emitidos concorrentemente no mesmo marco.
- Resultado consolidado **durante** o cálculo, entre a leitura e a emissão.
- Participante cuja modalidade declarada foi alterada por Retificação de conteúdo.
- Marco declarado sobre Etapa que ainda não produziu Resultado nenhum.

## Requirements *(mandatory)*

### Functional Requirements

#### Marco classificatório e universo

- **FR-001**: O sistema MUST permitir que o Edital declare marcos classificatórios por Perfil, cada
  um com identidade estável no conteúdo publicado.
- **FR-002**: O sistema MUST endereçar marco, Etapa e critério por identidade, nunca por posição,
  no padrão da 004.
- **FR-003**: Cada ato emitido MUST declarar seu universo: Processo, Edital, Perfil, marco,
  participantes considerados, Resultados antecedentes que entraram e a regra do marco na versão
  normativa sob a qual foi calculada.
- **FR-004**: O sistema MUST determinar o conjunto de participantes de um marco a partir das
  inscrições submetidas do Perfil, subtraindo quem foi eliminado em Etapa anterior conforme a regra
  de progressão já entregue pela 013.
- **FR-005**: O sistema MUST registrar, para cada participante do universo, a modalidade declarada
  na inscrição, sem verificar elegibilidade e sem separar a ordem por modalidade.
- **FR-006**: O sistema MUST nomear, com motivo, todo participante do universo que não recebeu
  posição — e MUST NOT atribuir posição arbitrária a quem não é classificável.
- **FR-007**: Participante eliminado na própria Etapa do marco MUST permanecer no snapshot como
  participante considerado, **sem posição**, com sua consequência e o motivo dela; o sistema MUST
  NOT lhe atribuir posição classificatória.

#### Regra publicada e critérios de desempate

- **FR-008**: O marco MUST **enumerar** as Etapas que entram na ordem, por identidade estável.
- **FR-009**: O peso de cada Etapa MUST ser lido do `weight` já publicado na própria Etapa, que
  permanece a fonte autoritativa; o marco MUST NOT declarar peso próprio.
- **FR-010**: Somente Etapa publicada como classificatória MUST poder integrar um marco, e o
  sistema MUST recusar a publicação de marco que enumere Etapa não classificatória.
- **FR-011**: O marco MUST declarar a **operação** que combina as pontuações — e, com ela, a
  normalização e o arredondamento aplicados.
- **FR-012**: O sistema MUST NOT exigir que os pesos das Etapas enumeradas somem 1, e MUST aplicar
  a normalização declarada pela operação.
- **FR-013**: O marco MUST declarar o desempate como lista **ordenada** de critérios, cada um com
  tipo e parâmetros.
- **FR-014**: O sistema MUST aplicar os critérios de desempate na ordem declarada, e MUST NOT
  alterar essa ordem por decisão do código.
- **FR-015**: Os critérios MUST poder consumir pontuação de Etapa específica e fatos do candidato
  congelados na inscrição (D-2).
- **FR-016**: O sistema MUST recusar a publicação de marco cujo critério aponte Etapa ou fato
  inexistente no mesmo conteúdo.
- **FR-017**: Cada critério MUST declarar o comportamento quando o valor que ele consome não
  existe — fato não congelado naquela inscrição, ou Etapa sem pontuação —, e o sistema MUST recusar
  a publicação da regra quando algum critério não o declarar.
- **FR-018**: A regra do marco e seus critérios MUST ser retificáveis pelo catálogo de Retificação,
  com vigência, autoria e efeito, sem reescrever publicação anterior.
- **FR-019**: O sistema MUST elevar a versão do conteúdo canônico ao introduzir o marco, e MUST
  preservar a leitura das versões anteriores.

#### Cálculo determinístico

- **FR-020**: O sistema MUST calcular a ordem a partir das entradas e da regra vigente, de forma
  determinística: mesmas entradas e mesma regra produzem sempre a mesma ordem.
- **FR-021**: O cálculo MUST NOT gravar, emitir ou substituir ato algum.
- **FR-022**: O sistema MUST tratar ausência de pontuação conforme a regra publicada, e MUST NOT
  converter ausência em zero.
- **FR-023**: Esgotados os critérios declarados, o sistema MUST declarar o empate residual e MUST
  NOT desempatar por identificador técnico, nome, instante de criação ou ordem de retorno do
  armazenamento.
- **FR-024**: O empate residual MUST NOT impedir a emissão: os participantes empatados MUST
  receber a **mesma posição**, e o ato MUST registrar que dentro daquele grupo não existe ordem
  normativa.
- **FR-025**: A consulta e a interface MUST identificar o grupo empatado como tal, para que quem
  lê a ordem não infira precedência onde o Edital não a declarou.

#### Emissão, autoridade e imutabilidade

- **FR-026**: Emitir MUST ser operação explícita, autorizada e auditável, com autor, instante e
  motivo — nunca efeito colateral de abrir tela ou de consolidar Resultado.
- **FR-027**: O sistema MUST recusar a emissão a quem não tem a autorização específica, e MUST
  reavaliá-la depois de obter o bloqueio da operação.
- **FR-028**: Um ato emitido MUST ser imutável: 100% das tentativas de alteração são recusadas sem
  efeito.
- **FR-029**: Para um mesmo marco MUST existir no máximo um ato vigente; emissões concorrentes MUST
  ser serializadas, e a segunda MUST suceder a primeira ou ser recusada, nunca produzir dois
  vigentes.
- **FR-030**: Ato sucedido MUST permanecer consultável, com o motivo da sucessão e sob a norma que
  o governou.

#### Obsolescência e divergência observável

- **FR-031**: O sistema MUST marcar o ato vigente como **obsoleto** quando houver mudança relevante
  no universo que ele declarou, e MUST NOT marcá-lo por mudança fora desse universo.
- **FR-032**: A comparação de obsolescência MUST incluir a regra do marco: Retificação que alcance
  a operação, a enumeração de Etapas, os pesos que ela lê ou a lista de critérios de desempate MUST
  tornar obsoleto o ato calculado sob a versão anterior, ainda que nenhum Resultado tenha mudado.
- **FR-033**: Obsoleto MUST NOT significar inválido: o ato continua vigente, consultável e
  produzindo efeito até que outro seja emitido.
- **FR-034**: A interface administrativa MUST exibir a divergência entre o computado agora e o
  vigente, posição a posição.
- **FR-035**: O sistema MUST NOT regenerar, substituir ou emitir ato como efeito de uma leitura.

#### Proveniência e reprodução

- **FR-036**: Todo ato emitido MUST identificar os Resultados de Etapa que entraram nele, a versão
  normativa vigente que o governou e os valores usados em cada critério de desempate.
- **FR-037**: O sistema MUST permitir reproduzir a ordem de um ato a partir de sua proveniência,
  obtendo resultado idêntico posição a posição.
- **FR-038**: Mudança na implementação MUST NOT alterar silenciosamente a reprodução de atos
  históricos; divergência entre o reproduzido e o snapshot MUST ser detectável.
- **FR-039**: A consulta MUST mostrar, para duas posições vizinhas separadas por desempate, qual
  critério as separou e com quais valores.

#### Jornada e proteção de dados

- **FR-040**: A jornada MUST ser executável de ponta a ponta pela interface administrativa —
  declarar o marco, calcular, conferir, emitir, consultar e ver a obsolescência — sem banco, shell
  ou chamada manual.
- **FR-041**: O sistema MUST registrar auditoria da emissão com ator, ação, entidade, instante,
  motivo e versão.
- **FR-042**: A ordem MUST expor apenas os dados necessários à finalidade; fatos do candidato
  usados em desempate MUST ter acesso restrito a quem administra e audita, e MUST NOT ser expostos
  a outros candidatos por esta feature.

#### Limites e não regressão

- **FR-043**: A 015 MUST NOT alterar conclusão, consequência ou motivo de `ResultadoEtapa` algum.
- **FR-044**: A 015 MUST NOT aplicar corte, alvo, vaga, percentual, reserva ou remanejamento.
- **FR-045**: A 015 MUST NOT publicar a ordem para candidato ou público.

### Key Entities

- **Marco Classificatório**: o ponto do certame em que uma ordem é produzida, declarado no conteúdo
  publicado com identidade estável, a regra que o governa e a lista ordenada de critérios de
  desempate. Pertence a um Perfil.
- **Critério de Desempate**: item ordenado e parametrizado do marco, com tipo executável, que
  consome pontuação de Etapa específica ou fato congelado da inscrição.
- **Ato de Ordenação**: o snapshot emitido — imutável, com autor, instante, universo declarado,
  posições, proveniência e estado vigente ou sucedido.
- **Posição**: o lugar de um participante no ato, com o valor que o colocou ali, os valores de
  desempate usados e a modalidade declarada.
- **Universo Classificável**: o recorte que o ato declara e que delimita sua obsolescência.

## 4. Invariantes observáveis

- **IO-1**: para um marco existe no máximo um ato vigente, e ele é imutável.
- **IO-2**: nenhuma leitura produz, substitui ou emite ato.
- **IO-3**: toda posição tem causa legível: o valor que a produziu, ou o critério que a separou da
  vizinha.
- **IO-4**: nenhuma ordem é produzida por regra que não esteja publicada.
- **IO-5**: a mesma proveniência reproduz a mesma ordem.
- **IO-6**: obsolescência é observável na interface, e não altera o vigente.
- **IO-7**: mudança da regra publicada obsoleta o ato calculado sob a versão anterior, sem que
  nenhuma entrada tenha mudado.
- **IO-8**: participante empatado até o fim compartilha posição; participante não classificável não
  tem posição alguma.

## 5. Out of Scope

- corte por alvo e progressão (014);
- vagas, cotas, reserva, remanejamento, ocupação e concorrência entre modalidades (016);
- verificação de elegibilidade a modalidade — heteroidentificação, spec própria;
- publicação de resultado, preliminar ou definitivo, e consulta pelo candidato ou pelo público
  (017);
- recurso, anulação e superação de atos (018);
- convocação, chamadas e suplência (019);
- barema estruturado, pontuação por critério ou item (D-4);
- **ordem produzida fora do sistema e importada — o sorteio.** Não por escolha de escopo, mas por
  dependência: o mecanismo sorteio não existe na 013, que só produz `ResultadoEtapa` a partir de
  Avaliação, e D-1 acrescenta apenas a Ocorrência. Não há Resultado de sorteio para ordenar. A
  consequência fica escrita: **o Edital 57/2026 não é executável por esta feature enquanto o
  mecanismo sorteio não existir**;
- desempate por sorteio executado dentro do sistema.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Para um marco com até 1.000 participantes, quem administra obtém a ordem calculada em
  uma única visão, com 100% dos participantes do universo classificados ou nomeados com motivo.
- **SC-002**: 100% dos atos emitidos identificam entradas, versão normativa e valores de desempate,
  e 100% deles reproduzem a mesma ordem posição a posição a partir dessa proveniência.
- **SC-003**: Abrir a tela de um marco produz zero atos, zero gravações e zero eventos de emissão,
  em 100% das aberturas.
- **SC-004**: 100% das tentativas de alteração de ato emitido são recusadas sem efeito.
- **SC-005**: 100% das tentativas de emissão sem autorização específica são recusadas, e nenhuma
  delas produz ato.
- **SC-006**: Entrada nova no universo de um marco emitido faz o vigente aparecer como obsoleto em
  100% das aberturas seguintes; entrada fora do universo produz zero marcações.
- **SC-007**: Duas emissões concorrentes no mesmo marco produzem exatamente um ato vigente, em 100%
  das execuções.
- **SC-008**: Em 100% dos empates resolvidos, a consulta nomeia o critério que separou as posições
  e os valores usados; em 100% dos empates residuais, o desfecho aparece explicitamente.
- **SC-009**: Nenhum `ResultadoEtapa` muda de conclusão, consequência ou motivo por causa desta
  feature, e todo teste da 013 continua existindo e passando.
- **SC-010**: A jornada demonstrável é executada pela interface administrativa: declarar o marco,
  publicar, calcular, emitir, consultar a proveniência e ver a obsolescência — sem banco, shell ou
  chamada manual.
- **SC-011**: Reordenar os critérios de desempate por Retificação altera a ordem calculada a partir
  da vigência, e zero atos emitidos antes dela mudam.
- **SC-012**: Retificação que alcance a regra de um marco faz o ato vigente aparecer como obsoleto
  em 100% das aberturas seguintes, mesmo sem nenhum Resultado novo.
- **SC-013**: 100% das tentativas de publicar marco com critério sem comportamento declarado para
  valor ausente, ou com Etapa não classificatória enumerada, são recusadas com o motivo.
- **SC-014**: Em 100% dos atos, a soma das posições atribuídas e dos participantes considerados sem
  posição é igual ao total do universo declarado.

## Assumptions

- A ordem é produzida **por Perfil**, em lista única, com a modalidade declarada visível em cada
  posição. Separar listas por modalidade é da 016, e a lista única não impede o corte da 014 de
  filtrar por modalidade.
- Participante eliminado em Etapa anterior não entra no universo do marco seguinte, pela regra de
  progressão que a 013 já entregou. O eliminado **na própria Etapa** do marco permanece no snapshot
  como participante considerado, sem posição (FR-007): a proveniência registra o universo inteiro,
  e a ordem contém apenas os classificáveis.
- Empate é possível e frequente: os Editais em vista o preveem explicitamente, e a existência de
  critérios ordenados pressupõe que a primeira comparação empata.
- A autoridade competente para emitir é a mesma cadeia que autoriza consolidar Resultado, até que
  as capacidades constituídas digam outra coisa.
- Os fatos do candidato consumidos por desempate chegam por D-2, congelados na submissão contra a
  `versao_aceita`. Inscrição submetida antes de o fato ser declarado não o possui — e o que fazer
  nesse caso deixou de ser suposição: é FR-017, e sem essa declaração a regra não publica.
- Etapa decisória não produz número; sua participação num marco que soma pontuação é filtro, não
  parcela. Como Etapa decisória pode ser publicada como classificatória, o comportamento para valor
  ausente (FR-017) é o que a mantém honesta dentro de um marco.
- O volume de referência é o mesmo da 013: até 1.000 participantes por marco.

## 6. Dependências e direção para o planejamento

**Depende de D-2** — fatos declarados pelo Edital, congelados na submissão. Sem eles não há
desempate por idade nem por tempo de experiência, e a feature nasce inexecutável para os Editais em
vista. A coleta é território da 009.

**Consome D-1** — `origem` e `versao` no `ResultadoEtapa`, que é extensão da 013 e precisa cair
antes ou junto, sob pena de o Resultado por Ocorrência ficar fora de qualquer ordem.

**Custo de esquema, a planejar em conjunto**: esta feature, D-2 e D-3 elevam a mesma versão
canônica. Feitas na mesma leva, é uma elevação; separadas, são três, cada uma com seu caminho de
leitura das versões anteriores.

**O que esta feature deixa pronto para a 014**: a ordem, o universo declarado e a modalidade
legível em cada posição. O corte lê e não recalcula.
