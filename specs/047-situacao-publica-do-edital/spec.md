# Feature Specification: Situação pública e histórico oficial do Edital em execução

**Feature Branch**: `claude/spec-047-public-projection-8dd4b1`

**Created**: 2026-09-26

**Status**: Draft

**Input**: proposta do usuário de 26/09/2026, *"SPEC 047 — Projeção pública confiável do Processo"*,
com a instrução de **não** aceitar a hipótese sem antes confrontá-la com a
[auditoria de consolidação](../../doc/auditoria-de-consolidacao-2026-09-26.md), com as specs
anteriores e com o código da `main` em `ee894ab`. O confronto confirmou a hipótese **em parte**
(cenário B da proposta): a maior parte do que ela pede já existe, entregue pela `017`, pela `021` e
pela `024`, e o que sobra é um recorte menor, mais preciso e coeso. Esta spec é esse recorte.

> **Faixa de identificadores.** Abre em **FR-760** e **SC-282**. O teto medido em 26/09/2026 em
> todas as worktrees (`git worktree list`) é 759 para os requisitos funcionais e 281 para os
> critérios de sucesso, ambos da `046` (PR #188, aberto). Os números vão por extenso porque a `046`
> ainda não está na `main`, e a varredura de citações não os encontraria nesta árvore. A faixa da
> `046` fica reservada. Esta spec **não cria** identificador `UX-`, porque nenhum sinal novo nasce
> aqui. As decisões reiniciam em `D-001`. Decisão de outra feature é citada pelo nome e pela spec
> de origem, e nunca pelo número.

> **Teto proporcional.** A proposta listava vinte e seis frentes. Treze já estão atendidas pelo
> código, e esta spec **não escreve requisito para elas** (ver *O que já existe e fica como está*).
> O que sobra cabe em **cinco histórias** e **dezesseis requisitos**.

---

## Por que esta feature existe

### A pergunta da proposta, respondida pelo código

> *Depois que um Processo é publicado e começa a acontecer, existe uma representação pública
> autoritativa e coerente do seu estado?*

**Existe para o período de inscrições, e para quase nada depois dele.** A página pública do Edital
(`portal/<edital>/`) deriva do conteúdo publicado vigente, e **nenhum** texto dela é mantido à mão.
A proposta temia uma segunda fonte manual de verdade, e ela não existe (ver §*O que já existe*).
O defeito é outro: **a única situação que a página calcula é a do período de inscrições**, e ela
continua sendo dita depois de deixar de ser a situação relevante, ou mesmo verdadeira.

Quatro fatos verificados no código sustentam a feature:

| | O que a página pública diz hoje | O que o domínio sabe | Onde |
|---|---|---|---|
| **1** | Edital **cancelado** dentro do período: marca *"Aberta"* e *"Faltam N dias"*, só sem o botão, e sem nenhuma palavra sobre o cancelamento. Edital **encerrado**, ou de Processo encerrado: nada. | o desfecho é ato de domínio, append-only, com data (`AtoAdministrativo`) | `portal/views.py:381-389, 418`; `inscricoes/domain/periodo.py:83-86`; `processos/models.py:130-148` |
| **2** | Evento do cronograma com fase calculada por **regra própria do portal**: compara só o dia, sem a zona institucional, e não conhece `CANCELADO`. Um Evento cancelado aparece *"Acontecendo agora"* ou *"por vir"*. | a `045` derivou a fase numa régua única (`FR-735`) e deixou o portal **registrado, e fora** | `portal/leitura.py:62-89` × `editais/domain/calendario.py:74-104`; `specs/045-…/spec.md`, *Out of Scope* |
| **3** | A página pública do resultado **não diz o prazo recursal**. Só quem já se identificou o vê, no acompanhamento. | a janela é calculável da norma do marco e da primeira publicação do ato, e é essa conta que decide se o sistema recebe o recurso | `portal/templates/portal/resultado.html`; `acompanhamento.html:155-160`; `recursos/domain/janela.py:123-150` |
| **4** | Um resultado preliminar **sucedido** pelo definitivo **some** da página do Edital. A página do definitivo diz *"este é o vigente"*, e não oferece caminho às anteriores. O endereço antigo continua respondendo, mas só quem o guardou chega a ele. | a cadeia de sucessão está inteira, e a leitura dela já existe na gestão (`historico_do_marco`) | `divulgacao/application/selectors.py:54, 121-135`; `portal/views.py:2205-2250` |

Os quatro têm a mesma natureza. **O fato existe no domínio, é autoritativo, e a projeção pública o
omite ou o contradiz.** Não há regra de negócio nova em nenhum deles, e nenhum pede dado novo.

### Por que a `045` e a `046` não resolvem

- **A `045` garante que a gestão enxergue o Processo vivo.** Ela derivou a fase do Evento e aplicou
  a derivação ao pulso da gestão. Deixou o portal de fora **por escrito** (*"alinhá-lo… fica
  fora"*; achados *"O portal do candidato tem regra própria de fase"* e *"O portal e o documento
  publicado não filtram `CANCELADO`"*). A 047 consome a régua da 045 e não a reescreve.
- **A `046` garante que o que entra em produção possa ser executado.** Ela vale no ato de publicar,
  e tira da tela do Edital publicado a validação de publicabilidade (RC-32). Declara fora de escopo
  o *"redesign da página pública, da área do candidato ou do documento publicado"*. A 047 não cria
  guarda estrutural nenhuma, nem a montante nem a jusante.

> **046 garante que aquilo que entra em produção pode ser executado. 047 garante que aquilo que
> ocorre durante a execução seja dito publicamente de forma derivada, vigente e rastreável.** O
> código atual sustenta essa separação. As duas specs não tocam a mesma superfície: a 046 fica na
> gestão e no ato de publicar, a 047 no portal.

### Por que é uma unidade, e não quatro diretas

Os quatro fatos respondem à **mesma** pergunta de quem está de fora, *"o que vale agora, e como se
chegou aqui?"*, sobre a **mesma** página, e com a **mesma** regra: derivar no instante da leitura, de
registro existente, sem gravar nada. Feitos separados, repetiriam quatro vezes a decisão de como a
página escolhe o que dizer quando fatos concorrem (desfecho × período, cancelado × fase, vigente ×
histórico). Esta spec toma essa decisão uma vez (`D-002`, `D-003`).

**A jornada** (Constituição, §VI): uma pessoa de fora, candidata ou não, abre o endereço de um Edital
— de um e-mail, de um compartilhamento, da vitrine — e sabe, sem se identificar e sem abrir o PDF,
se ele ainda está valendo, o que está acontecendo, o que vem depois, que resultados saíram, quais
valem, e até quando se pode recorrer. Hoje ela sabe só a primeira metade disso, e às vezes errado.

---

## Clarifications

### Session 2026-09-26

- Q: O Evento pontual, sem término, é concluído a partir do instante de início ou dura o dia inteiro
  na zona institucional? → A: A partir do instante de início, a régua da `037` e da `045` (`D-004`).
  O usuário aceitou a recomendação ("pode seguir").
- Q: O motivo registrado no ato de encerramento ou de cancelamento é exibido publicamente? → A: Não.
  A página diz o desfecho e a data (`D-006`, `FR-764`). O usuário aceitou a recomendação.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O Edital que acabou diz que acabou (Priority: P1)

Quem abre a página de um Edital encerrado ou cancelado, ou de um Edital cujo Processo foi encerrado
ou cancelado, lê o desfecho e a data dele, e nunca lê que as inscrições estão abertas.

**Why this priority**: é o único dos quatro fatos em que a página **afirma o falso**. Um Edital
cancelado anuncia *"Aberta — faltam 3 dias"*. A pessoa chega pelo endereço, que continua
respondendo por decisão da `024` e da `009` (preservar ≠ anunciar), e encontra um convite sem
botão e sem explicação.

**Independent Test**: publicar um Edital com o período de inscrições aberto, cancelá-lo pela gestão
e abrir o endereço público. Repetir com um Edital encerrado, e com um Edital publicado cujo Processo
foi encerrado.

**Acceptance Scenarios**:

1. **Given** um Edital cancelado com o período declarado ainda em curso, **When** alguém abre a
   página pública, **Then** lê que o Edital foi cancelado, com a data do ato, e não lê *"Aberta"*
   nem prazo restante.
2. **Given** um Edital encerrado, **When** alguém abre a página ou vê o cartão na vitrine, **Then**
   lê que o Edital foi encerrado, com a data, distinto de *"inscrições encerradas"*.
3. **Given** um Edital publicado cujo Processo foi encerrado, **When** alguém abre a página,
   **Then** lê o encerramento do Processo, com a data.
4. **Given** qualquer dos três, **When** alguém lê o restante da página, **Then** cronograma,
   documentos, resultados e histórico continuam lá, como registro.
5. **Given** um Edital cancelado, **When** alguém consulta a vitrine, **Then** ele continua fora
   dela, como hoje.

---

### User Story 2 - O cronograma público diz a fase que a gestão diz (Priority: P1)

A fase de cada Evento no portal — página pública e acompanhamento do candidato — é a mesma que a
gestão lê, e um Evento cancelado é dito cancelado.

**Why this priority**: são duas verdades sobre o mesmo dado publicado, e a divergência já está
registrada na `045`. Com a gestão e o portal lendo regras diferentes, o operador vê *"concluído"*
onde o candidato lê *"acontecendo agora"*. Pior: um Evento cancelado continua anunciado com data.

**Independent Test**: com um Edital cujo cronograma tenha um Evento com término, um Evento pontual
já iniciado, um Evento cancelado e o período de inscrições, comparar a fase de cada Evento na página
pública, no acompanhamento e no pulso da gestão, no mesmo instante.

**Acceptance Scenarios**:

1. **Given** um Evento com término, em curso, **When** portal e gestão são abertos no mesmo
   instante, **Then** os dois dizem *em andamento*.
2. **Given** um Evento cancelado no conteúdo vigente, **When** alguém abre a página pública ou o
   acompanhamento, **Then** lê que ele foi cancelado, e não lê fase nenhuma.
3. **Given** o período de inscrições sem término declarado, **When** alguém lê o cronograma,
   **Then** a linha dele não contradiz a marca de inscrições abertas.
4. **Given** um Evento pontual, **When** o instante da leitura atravessa o início dele, **Then** ele
   passa a *concluído* no instante do início (`D-004`), igual nas três superfícies.

---

### User Story 3 - A página diz o que acontece agora e o que vem depois (Priority: P2)

Quem abre a página de um Edital sem desfecho lê, derivado do cronograma vigente, o que está em
andamento e qual é o próximo Evento, com a data dele.

**Why this priority**: responde a *"em que momento estamos?"* sem que a pessoa tenha de varrer o
cronograma inteiro. Não é defeito, e por isso é P2. Mas é o que torna a página útil depois de
encerradas as inscrições, que é quando hoje ela não diz nada além de *"Encerrada"*.

**Independent Test**: com um Edital de inscrições encerradas e três Eventos futuros, abrir a página
e conferir que o próximo nomeado é o de início mais próximo. Avançar o relógio para dentro de um
deles e conferir que ele passa a *em andamento* e o seguinte vira o próximo.

**Acceptance Scenarios**:

1. **Given** inscrições abertas até uma data, **When** alguém abre a página, **Then** lê o período
   aberto e o próximo Evento depois dele, se houver.
2. **Given** inscrições encerradas e um Evento de resultado preliminar planejado, **When** alguém
   abre a página, **Then** lê que o próximo é esse Evento, com a descrição publicada e a data.
3. **Given** nenhum Evento em andamento nem planejado, **When** alguém abre a página, **Then** a
   página não diz nada sobre agora nem sobre próximo, e em nenhum caso diz *"em análise"* nem outra
   fase que nenhum fato registrou.
4. **Given** um Edital com desfecho, **When** alguém abre a página, **Then** não lê próximo Evento.

---

### User Story 4 - Quem chega ao resultado sabe até quando pode recorrer (Priority: P2)

A página pública de um resultado divulgado diz o período de interposição de recurso quando a norma
do marco o declara, e se ele está aberto ou encerrado. É o mesmo período que o sistema aplica a quem
recorre.

**Why this priority**: é o RC-48, e a auditoria o põe na onda do candidato. Quem chega pelo
endereço público, de um e-mail ou da lista de resultados, hoje não sabe que há prazo correndo.
Só quem se identifica descobre. O prazo é público por natureza: é norma do Edital aplicada a um ato
público.

**Independent Test**: divulgar um resultado preliminar num marco que declara janela de cinco dias
corridos, abrir a página pública do resultado e a do Edital, e conferir as datas contra as do
acompanhamento de um inscrito.

**Acceptance Scenarios**:

1. **Given** um resultado vigente cujo marco declara janela, com o prazo em curso, **When** alguém
   abre a página pública do resultado, **Then** lê o período de interposição, com abertura e
   encerramento, e que ele está aberto.
2. **Given** o mesmo, depois do encerramento, **When** alguém abre a página, **Then** lê que o prazo
   encerrou, e em que data.
3. **Given** a definitiva que republica o mesmo ato, **When** alguém abre a página dela, **Then** o
   prazo dito é o que a primeira publicação do ato abriu, e não um prazo novo.
4. **Given** um marco sem janela declarada, **When** alguém abre o resultado, **Then** a página não
   diz nada sobre recurso: nem prazo, nem *"não cabe recurso"*.
5. **Given** qualquer dos casos, **When** alguém lê a página, **Then** não encontra ação de recorrer.

---

### User Story 5 - Todo resultado divulgado continua alcançável pela página do Edital (Priority: P3)

A partir da página do Edital, a pessoa chega a toda publicação de resultado já divulgada: as
vigentes em destaque, as sucedidas como histórico, cada uma no marco e na lista a que pertence.

**Why this priority**: a `017` preservou o endereço de toda publicação sucedida, e a página de uma
sucedida já aponta para a vigente. Falta a direção inversa. Hoje o preliminar que o definitivo
sucedeu só é alcançável por quem guardou o endereço. É P3 porque o registro existe e responde, e o
que falta é caminho até ele.

**Independent Test**: divulgar um preliminar, depois o definitivo do mesmo marco e da mesma lista,
e partir da página do Edital até o preliminar sem digitar endereço.

**Acceptance Scenarios**:

1. **Given** um marco com preliminar sucedido por definitivo, **When** alguém abre a página do
   Edital, **Then** vê o definitivo como vigente e encontra o preliminar como histórico daquele
   marco e daquela lista, com natureza e data.
2. **Given** a página do definitivo, **When** alguém a abre, **Then** encontra o caminho para as
   publicações anteriores da mesma cadeia.
3. **Given** uma cadeia de três publicações, **When** alguém percorre o histórico, **Then** as três
   aparecem em ordem, e só a última é dita vigente.
4. **Given** um definitivo que corrigiu outro em razão de recurso, **When** alguém lê o histórico,
   **Then** a causa continua dita como hoje, sem natureza nova.

---

### Edge Cases

Cada item é requisito. A matriz de rastreabilidade da implementação MUST ter uma linha para cada
um, como tem para os `FR-`.

- **Cancelado com período ainda por abrir.** A página diz o cancelamento, e não *"Em breve"* nem
  *"inscrições começam em…"*.
- **Encerrado antes do fim do período declarado.** O encerramento prevalece sobre o período (`D-003`).
  A linha do período no cronograma continua com as datas publicadas.
- **Processo cancelado.** O domínio só o cancela depois de todos os seus Editais estarem em estado
  final (`processos/domain/finalizacao.py:41-55`). A página diz o desfecho **do Edital**, que é o
  mais específico.
- **Processo encerrado com Edital ainda publicado.** O encerramento do Processo é permitido sem
  exigir estado final dos Editais. A página diz o encerramento do Processo, porque a partir dele
  nenhum Edital dele muda (`D-003`).
- **Edital com desfecho e janela recursal ainda aberta.** A página do resultado continua dizendo o
  prazo. O desfecho administrativo não apaga a norma aplicada a um ato já publicado, e a decisão de
  receber ou não a peça continua com o domínio de recursos, que esta spec não toca.
- **Período de inscrições marcado como cancelado.** Fora do escopo, e registrado (ver *Achados*):
  a régua do período ignora o cancelamento e o sistema continua recebendo inscrição. Esta spec não
  muda o que o sistema recebe, e a projeção não pode contradizê-lo. A linha do período segue a régua
  do período, e a exceção do `FR-766` vale para ela.
- **Evento sem início** no conteúdo publicado: não recebe fase e não é candidato a próximo Evento.
- **Dois Eventos com o mesmo início** como próximos: os dois são ditos, na ordem publicada.
- **Retificação publicada com vigência futura.** O cronograma que vale para *agora* e *próximo* é o
  da versão vigente no instante da leitura, e não o da Retificação que ainda não vale. O histórico
  de atos continua como a `024` o deixou.
- **Resultado divulgado e depois sucedido em outra lista do mesmo marco.** Sucessão é por marco e por
  lista (decisão do eixo da lista, da `021`). O histórico de uma lista não mistura o de outra.
- **Edital publicado antes desta feature.** Não há o que migrar: os fatos usados existem desde que
  cada tipo de ato existe. Onde o registro antigo não tem o dado, por exemplo um marco publicado sem
  `appealWindow`, a página omite a informação, e não a infere (`FR-775`).
- **Processo publicado antes de 04/09 sem ato de ativação.** Irrelevante: a projeção não lê o estado
  *Ativo*, e sim os desfechos, que têm ato desde o primeiro dia.

---

## Requirements *(mandatory)*

### O desfecho do Edital

- **FR-760**: Quando o Edital tiver sido encerrado ou cancelado, ou o Processo dele tiver sido
  encerrado ou cancelado, a página pública do Edital, e todo cartão que mostre a situação dele, MUST
  dizer esse desfecho e a data do ato que o registrou. A data MUST vir do registro imutável do ato,
  e nunca de campo que muda a cada transição.
- **FR-761**: Em Edital com desfecho, a página MUST NOT afirmar inscrições abertas, prazo restante
  nem início futuro de inscrições. As datas do período continuam legíveis como Evento do
  cronograma.
- **FR-762**: Havendo desfecho do Edital e do Processo, a página MUST dizer o do Edital. Havendo só
  o do Processo, MUST dizer o do Processo (`D-003`).
- **FR-763**: A vitrine MUST continuar excluindo o Edital cancelado e MUST continuar listando o
  encerrado, que passa a ser distinguido, no cartão, do Edital apenas com inscrições encerradas.
- **FR-764**: A página pública MUST NOT exibir o motivo registrado no ato de encerramento ou de
  cancelamento. Diz o desfecho e a data, e nada além (`D-006`).

### O cronograma numa régua só

- **FR-765**: A fase de cada Evento mostrada no portal — página pública do Edital e acompanhamento
  do candidato — MUST ser a mesma que a gestão lê para o mesmo Evento no mesmo instante: a régua da
  `045` (`FR-735`), que lê a da `037` (`FR-545` a `FR-547`), com a exceção do período de inscrições,
  que segue a régua do período (`FR-347`). O portal MUST NOT manter régua própria.
- **FR-766**: Um Evento declarado cancelado no conteúdo vigente MUST ser dito cancelado, MUST NOT
  receber fase ordinária e MUST NOT ser candidato a próximo Evento. A exceção é o período de
  inscrições, que segue o edge case correspondente.

### Agora e próximo

- **FR-767**: A página pública de um Edital sem desfecho MUST dizer, derivados do cronograma vigente
  no instante da leitura, os Eventos em andamento e o próximo Evento planejado, com a descrição
  publicada e a data de início. Nenhum texto de *"próximo passo"* MUST ser digitado por alguém.
- **FR-768**: Sem Evento em andamento nem planejado, a página MUST NOT dizer nada sobre agora ou
  próximo. Em nenhum caso MUST dizer uma fase do Edital que nenhum fato registrou, como *"em
  análise"* ou *"resultado final disponível"* (`D-002`).

### O prazo recursal na página pública

- **FR-769**: A página pública de uma publicação de resultado **vigente**, cujo marco declare janela
  recursal computável, MUST dizer o período de interposição — abertura e encerramento — e se ele
  está aberto ou encerrado no instante da leitura. O período MUST ser **o mesmo que a interposição
  aplica** àquela publicação: a mesma regra da janela da `018`, sobre a mesma norma, ancorado na
  primeira publicação do mesmo ato (`D-005`). A página de uma publicação sucedida não diz prazo: ela
  leva à vigente, como já faz.
- **FR-770**: Na lista de resultados vigentes da página do Edital, o resultado cujo prazo estiver
  aberto MUST vir acompanhado da data de encerramento.
- **FR-771**: Sem janela declarada, ou com janela não computável, a página MUST NOT dizer nada
  sobre recurso. A página MUST NOT oferecer ação de recorrer (`FR-055` da `017`, que continua valendo nessa
  parte). Ela MAY dizer que a interposição é feita pela área do candidato.

### O histórico dos resultados

- **FR-772**: A partir da página pública do Edital, toda publicação de resultado já divulgada MUST
  ser alcançável sem digitar endereço. As vigentes continuam em destaque, e as sucedidas aparecem
  como histórico do marco e da lista a que pertencem, cada uma com natureza, data e a indicação de
  que foi sucedida (`D-007`).
- **FR-773**: A página de uma publicação que sucedeu outra MUST oferecer o caminho às publicações
  anteriores da mesma cadeia, do mesmo marco e da mesma lista.

### Transversais

- **FR-774**: Tudo o que esta spec projeta MUST ser derivado, no instante da leitura, de registros
  que já existem. MUST NOT nascer estado, campo ou texto de situação mantido à mão, e MUST NOT ser
  reescrito conteúdo publicado nem registro de ato.
- **FR-775**: Fato que o registro de um Edital anterior não contém MUST ser omitido, e nunca
  inferido ou fabricado. Nenhum Edital hoje consultável MUST deixar de sê-lo.
- **FR-776**: A projeção pública MUST NOT expor dado individual — situação de candidato, Resultado
  de Etapa, convocação, recurso de alguém — nem a identidade de quem registrou um ato
  administrativo.

### Key Entities

Nenhuma entidade nova. A spec lê:

- **Ato administrativo de desfecho** do Edital e do Processo: operação, data e motivo. É
  append-only.
- **Versão consolidada vigente** do Edital: o cronograma publicado, com a declaração de
  cancelamento de cada Evento, e a norma dos marcos, incluindo a janela recursal.
- **Publicação de resultado**: natureza, data, marco, lista e a cadeia de sucessão.
- **Régua do calendário e régua do período**: as funções que já decidem vencido, fase e período
  aberto.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-282**: Num percurso conduzido pelos seis estados-tipo — inscrições futuras, abertas,
  encerradas com resultado divulgado, Edital cancelado dentro do período, Edital encerrado e Edital
  de Processo encerrado —, **zero** afirmações da página pública contrariam os registros do
  domínio, conferidas pelas perguntas do §*A jornada*.
- **SC-283**: Para um cronograma com Evento com término, Evento pontual, Evento cancelado e período
  de inscrições, a fase de **100%** dos Eventos é igual no portal e na gestão, em três instantes: antes,
  durante e depois. **Nenhum** Evento cancelado aparece com fase ordinária.
- **SC-284**: Quem parte da página pública de um resultado chega ao prazo recursal **sem se
  identificar**, e a data de encerramento é igual à do acompanhamento do candidato em **100%** das
  publicações conferidas.
- **SC-285**: A partir da página do Edital, toda publicação de resultado já divulgada, vigente ou
  sucedida, é alcançável em até **duas** navegações, sem digitar endereço.
- **SC-286**: A feature entrega **zero** campos novos de situação, **zero** migrations de dado e
  **zero** linhas de conteúdo publicado alteradas. **Todos** os Editais consultáveis antes continuam
  abrindo.
- **SC-287**: Numa página de Edital com inscrições encerradas, uma pessoa de fora responde *"o que
  acontece agora ou depois?"* sem abrir o PDF e sem rolar até o cronograma.

---

## Decisões

### D-001 — A unidade pública é o Edital, e o Processo é contexto

A proposta fala da *"página pública do Processo"*. Ela não existe, e esta spec não a cria. O portal
publica **Editais** (`portal/<edital>/`), e a Constituição dá a cada Edital cronograma próprio e
independente. Um Processo com dois Editais tem duas situações, dois cronogramas e dois conjuntos de
resultados. Uma página agregada seria superfície nova sem evidência de necessidade (Princípio V). O
Processo entra onde já entra: como título e código, e, pelo `FR-762`, como fonte de desfecho.

### D-002 — Nenhuma fase agregada do Edital além do período e do desfecho

A proposta pergunta se uma *"situação pública derivada"* com estados como *"em análise"*,
*"resultado preliminar disponível"* e *"resultado final disponível"* é calculável. **Não é, de
forma determinística, no nível do Edital:**

- um Edital tem vários Perfis, cada Perfil vários marcos, e cada marco várias listas;
- o Perfil A pode ter resultado definitivo enquanto o B está no preliminar;
- *"em análise"* só se deduziria da **ausência** de resultado, e a ausência não é fato.

Os estados agregados que **são** determinísticos já existem ou nascem aqui: o período de inscrições
(`periodo.py`) e o desfecho (`FR-760`). O resto da pergunta *"em que momento estamos?"* é respondido
por fatos, cada um no seu nível: o Evento em andamento e o próximo (`FR-767`), os resultados
vigentes por marco, com natureza (já existe), e o prazo recursal de cada um (`FR-769`). Nenhum
enum de situação é persistido nem calculado.

### D-003 — O desfecho prevalece sobre o período, e o mais específico sobre o mais geral

O período de inscrições descreve a norma. O desfecho descreve o que aconteceu com ela. Quando os dois
concorrem, o desfecho vence, porque dizer *"Aberta"* de um Edital cancelado é afirmar o falso. Entre
o desfecho do Edital e o do Processo, vence o do Edital. Sem ele, vale o do Processo encerrado: a
partir dele nenhum Edital do Processo muda (`processos/domain/finalizacao.py:70-75`), e a página não
pode continuar sugerindo execução em curso.

### D-004 — Uma régua de fase para o portal, a da gestão

O portal passa a ler a fase pela régua da `045`. Hoje são quatro leituras do Evento sem término, e a
`045` alinhou duas delas. A que sobra no portal compara o **dia**, e não o instante, e o faz **sem a
zona institucional**: entre as 21h e a meia-noite de Vitória a data em UTC já é a do dia seguinte, e
um Evento marcado para aquele dia é dado como concluído com horas de antecedência. Isso contradiz o
Princípio II (instantes na zona institucional), independentemente de qual régua prevaleça.

**O Evento pontual, sem término, é concluído a partir do instante de início** — a régua da `037` e
da `045`, como já vale na gestão. A alternativa, fazê-lo durar o dia inteiro na zona institucional,
exigiria mudar a régua das duas specs, porque a fase delas **é** o vencido, e com ela a conferência
de publicação da `028`. Uma régua só vale mais do que a leitura mais generosa do dia: a gestão e o
portal param de discordar, e nada muda fora do portal. Decidido em 26/09/2026 (ver
*Clarifications*).

### D-005 — O prazo recursal público é exatamente o que a interposição aplica

O prazo mostrado é calculado pela regra que já existe, e não por outra:

- dias corridos;
- exclui-se o dia do começo;
- fecha ao fim do último dia, na zona institucional;
- ancorado na primeira publicação do mesmo ato.

**A norma é a que a interposição lê, e não outra.** Hoje a interposição, o acompanhamento e a
conferência da divulgação leem a janela do marco na **versão vigente** do Edital
(`recursos/application/interpor.py`, `_janelas_pertinentes`; `divulgacao/domain/publicabilidade.py`,
`_janela_aberta`). A primeira versão desta spec mandava ler a versão que o ato citou, e a revisão do
plano a corrigiu: a página pública anunciaria uma data e o sistema aceitaria recurso até outra. A
projeção diz o que a operação faz. Se a regra da operação estiver errada, o conserto é dela, e a
página acompanha sem mudar de requisito (ver *Achados*). É por isso que as superfícies não podem
discordar (`SC-284`). A `FR-055` da `017`
permitia apresentar o prazo (MAY). Esta spec o torna obrigatório na página pública do resultado, e
mantém a outra metade: nenhuma ação transacional.

### D-006 — O motivo do desfecho não é público

O ato de encerramento e o de cancelamento registram um motivo (`AtoAdministrativo.reason`). Ele foi
escrito como registro administrativo interno, sem expectativa de publicação, e todos os atos
passados foram escritos assim. Publicá-lo agora exporia, retroativamente, texto que ninguém redigiu
para o público. Por outro lado, o cancelamento de uma seleção é ato que interessa a quem se
inscreveu.

**O motivo não é exibido**: a página diz o desfecho e a data (`FR-764`). Um motivo público exigiria
campo redigido para isso, no ato, e só daqui para frente, o que é decisão de outra feature.
Decidido em 26/09/2026 (ver *Clarifications*).

### D-007 — O histórico dos resultados é anunciado como histórico, abaixo do vigente

É a distinção *preservar × anunciar* que a `024` fixou para a seleção cancelada e para o histórico
normativo, aplicada aos resultados:

- a página continua levando primeiro ao vigente;
- as sucedidas ficam alcançáveis e rotuladas, sem nunca aparecer como o que vale.

Uma linha do tempo única, que misturasse atos normativos, resultados e sorteio numa só lista, foi
considerada e **descartada** nesta feature. Não existe registro unificado de atos por Edital, e
compô-la duplicaria na mesma página três listas que já existem, criando uma segunda representação
dos mesmos atos. Ver *Out of Scope*.

---

## O que já existe e fica como está

Verificado no código. Repetir qualquer destes itens é defeito, e não escopo.

| Pergunta da proposta | Já respondida por | Evidência |
|---|---|---|
| Inscrições abertas, encerradas ou por vir? | período derivado do cronograma publicado, com marca e prazo | `inscricoes/domain/periodo.py:45-63`; `portal/leitura.py:124-166` |
| Existe segunda fonte manual de status? | **não**: Processo e Edital não têm campo livre de situação, e a página lê só o conteúdo publicado | `processos/models.py:13-115`; `portal/views.py:115-135` |
| Cronograma paralelo? | **não**: a mesma função serve página pública e acompanhamento | `portal/views.py:405, 1381` |
| Houve retificação? O que mudou? Desde quando vale? | aviso e histórico normativo inline, com justificativa e *"vigente desde"* (`024`) | `selecao.html:47-51`; `_documentos_do_edital.html` |
| Qual documento está vigente? | a página mostra sempre o consolidado vigente, e o PDF é o da publicação de origem | `publicacoes/application/selectors.py:26-41` |
| Resultado preliminar ou definitivo? | natureza no título e na lista | `resultado.html:4`; `divulgacao/application/selectors.py:121-135` |
| O resultado ainda vale? | *"sucedido"* com caminho para o vigente, ou *"este é o vigente"* (`017`) | `resultado.html:12-27` |
| Retificado por recurso? | causa derivada da cadeia, sem natureza nova (`018`) | `resultado.html:29-42` |
| Sorteio: aguardando, realizado, verificável | seção própria, relação, verificação e manifesto (`021`) | `selecao.html:236-272`; `portal/views.py:2271-2398` |
| Identidade e URL estável dos atos | publicação do Edital, Retificação (PDF e JSON), versão, anexo, resultado, relação e manifesto, por UUID | `portal/urls.py`; `publicacoes/api/public_views.py` |
| Encerrado continua consultável; cancelado sai da vitrine e continua pelo endereço | `FR-017` da `009`; decisão *preservar × anunciar* da `024` | `publicacoes/application/selectors.py:316-364` |
| *"Ativo"* sem consequência (E2E-005) | resolvido: a primeira publicação ativa o Processo (`c6d2187`). A projeção não lê *Ativo*, e não precisa | anexo 1 da auditoria, E2E-005 |
| Área do Candidato separada | acompanhamento, pareceres, convocação e requerimento só para o titular | `portal/views.py:1361-1427` |

---

## Correlação com a auditoria de consolidação

**Auditoria → decisão → SPEC anterior → implementação → resíduo → requisito da 047.**

| Achado | Situação na auditoria | Decisão / SPEC posterior | Código atual | Resíduo | Entra na 047? |
|---|---|---|---|---|---|
| RC-48 (13/09 QW12 · ACH-41 parte executável) | NÃO IMPLEMENTADO · B (B-8) | `017` `FR-055` (MAY) | `resultado.html` sem prazo; `acompanhamento.html:155-160` com prazo | prazo recursal invisível ao público | **sim**: `FR-769` a `FR-771` |
| RC-80 (N-05, N-06) — a parte do portal | RC-80 inteiro A | **`045`** derivou a fase (DP-01, opção A) e **registrou** o portal fora | `calendario.py:74-104` × `portal/leitura.py:62-89` | duas réguas; `CANCELADO` ignorado no portal | **sim**: `FR-765`, `FR-766`. O RC-80 da gestão está **resolvido** pela 045 |
| E2E-005 | RESOLVIDO (`c6d2187`) | — | `publish_edital.py:798-850` | *Ativo* continua sem consequência pública, **mas o desfecho também não tinha** | **sim, o desfecho**: `FR-760` a `FR-763`. O *Ativo* não entra (`D-002`) |
| Resultado sucedido sem caminho público de volta | **não registrado** na auditoria; achado desta investigação | `017` `FR-043`/`FR-048` preservam o endereço, e não a descoberta | `vigentes_do_edital`; `historico_do_marco` só na gestão | histórico preservado e inalcançável | **sim**: `FR-772`, `FR-773` |
| Edital cancelado anunciado *"Aberta"* | **não registrado**; achado desta investigação | `009` `FR-017` e a `024` (preservar × anunciar) | `portal/views.py:381-389, 418` | a página afirma o falso | **sim**: `FR-760`, `FR-761` |
| RC-76 (ACH-41) | NÃO IMPLEMENTADO · B | recomendação original inexecutável: sem vínculo Evento ↔ marco | `_evento.html:19-20` (tipo em texto livre) | confronto janela × Evento de recurso | **não**: exige modelar o vínculo. A parte viável é a `FR-769` |
| RC-111 | NÃO IMPLEMENTADO · A | `024` `FR-130`; o #185 corrigiu o RC-39 | `alteracoes.py` cala 45 de 84 campos | o *"O que mudou"* público omite mudanças | **não**: dicionário e guardião, sem spec (auditoria); a 047 consome o que ele produzir |
| RC-47 | NÃO IMPLEMENTADO · B (B-8) | — | `selecao.html:2,23,144` | `h1` com o título do Processo; vagas sem quantidade | **não**: identificação e oferta, não situação. Direta |
| RC-49 | NÃO IMPLEMENTADO · B (B-8) | — | rascunho e *"Minhas inscrições"* | prazo acabado na área do candidato | **não**: Área do Candidato |
| RC-37, RC-38 | NÃO IMPLEMENTADO · A | D-G5; `026` | `retificacao.py:1054` | a Retificação não acrescenta | **não**: B-4. A 047 mostra o que a Retificação produzir |
| RC-40 | PARCIALMENTE RESOLVIDO · C | `024` (decisão de vocabulário) | duas tabelas de rótulos | deriva gestão × portal | **não**: polish |
| RC-29, RC-30, RC-32, RC-72 | A / B | **`046`** (PR #188) | gate da publicação | — | **não**: a 047 não cria guarda estrutural |
| RC-78, RC-79, RC-81, RC-82 | A / B | **`045`** (PR #187) | pulso e Atenção | — | **não** |
| RC-12 | NÃO IMPLEMENTADO · B | `015` | teto executado e não publicado | norma sem publicação | **não**: B-9, conteúdo do documento |

---

## Impacto sobre Editais já publicados

- **Nenhum registro muda.** Não há migration, backfill nem Retificação. O conteúdo publicado e os atos
  são lidos, e nunca escritos (`FR-774`).
- **Os desfechos têm data desde o primeiro dia.** O ato administrativo existe e é append-only desde
  29/08. Todo Edital encerrado ou cancelado no acervo passa a dizer o desfecho com a data real.
- **Snapshots anteriores a 07/09 não têm `appealWindow`.** Os resultados deles não ganham prazo
  (`FR-771`, `FR-775`). Isso é verdadeiro, e não lacuna: a norma daquele ato não declarou janela
  computável.
- **Evento cancelado no acervo** só existe se veio pela API, único canal que o declara hoje. Passa a
  ser dito cancelado.
- **Cadeias de resultado anteriores** passam a ter o histórico alcançável. Nada muda no conteúdo de
  nenhuma publicação.
- **O que muda de verdade é a leitura do Evento pontual no portal** (`D-004`). Hoje ele é *"acontecendo
  agora"* até a meia-noite em UTC. Passa a *concluído* no instante do início, como a gestão já o lê.
  Uma prova marcada para as 9h deixa de ser anunciada como em curso às 14h do mesmo dia.

---

## Assumptions

- A página pública do Edital e o acompanhamento do candidato continuam sendo as superfícies do
  portal que mostram cronograma. A API pública não ganha situação derivada nesta feature (ver *Out of
  Scope*).
- O volume é o da `024`: dezenas de seleções simultâneas. Nenhuma projeção materializada é
  necessária, e nenhum requisito de desempenho novo nasce aqui.
- Rótulos públicos seguem o vocabulário que o portal já usa. Esta spec fixa **o que** é dito, e não
  a redação final.
- *"Data do ato"* é exibida em dia, mês e ano, na zona institucional, como as demais datas públicas.

---

## Out of Scope

- **Página pública do Processo** agregando seus Editais (`D-001`).
- **Enum ou estado de situação pública** persistido ou calculado para o Edital (`D-002`).
- **Linha do tempo unificada** de atos (`D-007`). Pode voltar se houver evidência de que as três
  listas não bastam, e aí como leitura, nunca como registro novo.
- **Publicação do ato de encerramento ou de cancelamento como documento**, e motivo redigido para o
  público (`D-006`).
- **Resultado de recursos como ato agregado publicado.** Não existe no domínio: o efeito de um
  recurso é uma publicação sucessora, que a página já explica.
- **Convocação pública.** O sistema não publica convocação: registra onde a instituição a publicou.
- **Vínculo entre Evento do cronograma e marco, ato ou janela** (RC-76).
- **Retificação que acrescenta** (RC-37, RC-38) e **dicionário do *"O que mudou"*** (RC-111).
- **Título do Edital e vagas por Modalidade na página** (RC-47), e **prazo no rascunho** (RC-49).
- **Situação derivada na API pública.**
- **Linguagem simples do Edital**, sumarização, versão cidadã.
- Redesign visual, identidade, SEO, CMS, analytics, notificações, personalização, chatbot, painel
  institucional.
- Qualquer guarda de publicação ou de execução (`046`) e qualquer sinal de condução (`045`).

---

## Achados registrados, fora do escopo

Encontrados nesta investigação. São reais, e nenhum pertence a esta feature.

- **Período de inscrições cancelado continua recebendo inscrição.** `periodo_de_inscricoes` e
  `recebe_inscricoes` ignoram o `status` do Evento (`inscricoes/domain/periodo.py`). Só a API declara
  `CANCELADO`, e o campo não é retificável (é *derivado* no contrato da `026`). Decidir se um período
  cancelado fecha o recebimento é regra de domínio da inscrição, e não projeção.
- **O cancelamento do Edital não gera Publicação.** A Constituição pede que o cancelamento preserve
  *"Publicações e histórico"*, e o domínio registra ato administrativo e auditoria, sem documento
  público. Se o Cefor precisa do ato de cancelamento publicado pelo sistema, é spec própria.
- **A docstring de `portal/views.py:8-10`** diz que *"ainda não existe… situação das inscrições"*, e
  ela existe. É higiene (RC-103).
- **A janela de um ato já divulgado segue a norma vigente, e não a que o ato citou.** A janela é
  retificável (`editais/domain/mutabilidade.py:357-359`), e a interposição a lê da versão vigente.
  Uma Retificação que mude a duração da janela depois de um resultado divulgado muda, portanto, o
  prazo de recurso desse resultado. Pode ser a intenção, já que conceder prazo é menos grave do que
  retirá-lo, como o próprio contrato registra (`mutabilidade.py:527-530`). Mas não há decisão escrita
  para o caso de **encurtar**. É pergunta do domínio de recursos (`018`), e a 047 projeta o que ele
  aplicar (`D-005`).
- **A API pública de histórico** (`/api/v1/public/editais/<id>/historico`) não é linkada pelo portal.
  Não é defeito, e fica registrado para quem for tratar a API.
