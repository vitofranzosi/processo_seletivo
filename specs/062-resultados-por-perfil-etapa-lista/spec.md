# Feature Specification: Resultados divulgados por Perfil, etapa e lista

**Feature Branch**: `claude/062-resultados-por-perfil-etapa-lista`

**Created**: 2026-10-07

**Status**: Draft

**Input**: a avaliação de 06/10/2026 do bloco "Resultados divulgados" da página pública do Edital,
feita sobre a captura do Edital 72/2026 (2 Perfis × 3 listas de concorrência), e as decisões que o
usuário fechou na mesma conversa. O defeito imediato — seis links de texto idêntico — já foi
corrigido pelo PR #255, que acrescentou o nome da lista ao texto de cada link. Esta feature é a
segunda etapa: reorganizar o bloco.

> **Faixa de identificadores.** Abre em **FR-1148**, **SC-443** e **UX-151**. O teto medido em
> 07/10/2026 em todas as worktrees era o da `061-corte-apos-recurso` para FR e SC (implementada em
> outra worktree, ainda sem PR — por isso os números dela não se citam aqui: a varredura de
> citações só os conhecerá quando ela chegar à `main`), e UX-150, na `main`. As decisões desta spec nascem em `D-001`;
> as nove que o usuário trouxe fechadas são **entrada** e aparecem como "decisões recebidas" (1ª a
> 9ª), sem reaproveitar a numeração.

**A frase que governa:**

> O resultado pertence à vaga. Quem chega pergunta pelo Professor de Matemática, e não pela
> publicação de 23/09.

**E a frase que mantém o corte:**

> Só apresentação. Nenhuma publicação muda, nenhuma cadeia se funde, nenhuma regra do certame é
> tocada.

---

## Por que esta feature existe

A página do Edital lista os resultados vigentes numa sequência única, ordenada pela data de
publicação. Num Edital encerrado com dois Perfis e três listas, isso dá seis linhas no mesmo nível,
cada uma com o seu "Publicações anteriores (1)":

- **O objeto que a pessoa procura não aparece.** A página organiza as vagas por Perfil logo abaixo
  ("Professor Substituto — Matemática", "Técnico de Laboratório — Química"), e os resultados, que
  pertencem a essas mesmas vagas, chegam como lista cronológica. Com todas as publicações no mesmo
  dia, a ordem entre os Perfis é acaso.
- **O histórico concorre com o vigente.** "Publicações anteriores" aparece seis vezes, no mesmo
  nível visual do resultado que vale.
- **Etapa, natureza e lista estão fundidas numa só frase.** "Resultado definitivo — Classificação
  final — Matemática — Pessoas com deficiência" obriga a ler a linha inteira para achar a única
  palavra que distingue uma linha da vizinha.

---

## Decisões recebidas (06/10/2026)

Fechadas pelo usuário antes desta spec. Não se reabrem aqui.

1. **Hierarquia fixa**: Perfil → Etapa (marco) → Lista de concorrência → publicação vigente e
   histórico. Fixa também quando há um Perfil só, uma etapa só ou uma lista só.
2. **Natureza e data sempre por lista**, nunca promovidas para o título da etapa, nem quando todas
   as listas coincidem. Cada lista é uma cadeia própria (decisão do eixo da lista, da `021`) e pode
   estar em fase diferente das vizinhas. Uma regra condicional foi considerada e recusada por deixar
   a página imprevisível.
3. **O texto do link é o nome da lista** ("Pessoas com deficiência"), e nunca um "Ver resultado"
   repetido, que reproduziria o defeito corrigido pelo #255.
4. **A repetição do Perfil no nome da etapa é aceita.** "Professor Substituto — Matemática" seguido
   de "Classificação final — Matemática" fica como está: o nome da etapa é texto livre, escrito por
   quem monta o Edital. Nada de cortar trechos dele, e nada de regra de cadastro nesta spec.
5. **O histórico é consolidado** — um bloco recolhido em vez de um por lista —, preservando a cadeia
   independente de cada lista e dizendo a lista de cada item.
6. **Acesso à situação individual, separado da árvore de publicações**, dentro do bloco:
   "Participou deste processo seletivo? Consulte sua classificação e situação individual." com a
   ação "Entrar para ver minha situação".
7. **O destaque do bloco se preserva** quando o Edital não recebe inscrições (`FR-050` e `SC-018`
   da `017`, e o destaque introduzido pela `024`).
8. **O prazo de recurso continua por lista** (`FR-770`).
9. **Mobile-first e acessível**: 375 px sem rolagem horizontal da página, links de nome distinto,
   hierarquia de títulos correta.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Achar o resultado da própria vaga (Priority: P1)

Quem concorreu a Professor Substituto de Matemática abre a página do Edital encerrado e encontra,
sob o título do Perfil, a etapa e as três listas, cada uma com natureza e data. Abre a lista em que
concorreu sem precisar ler nenhuma outra linha.

**Why this priority**: é a pergunta com que a pessoa chega, e hoje ela precisa decifrar seis linhas
para respondê-la.

**Independent Test**: com um Edital de dois Perfis e três listas por Perfil, todas com resultado
definitivo vigente, abrir a página pública e conferir: um grupo por Perfil, na ordem da seção Vagas;
dentro dele, a etapa; dentro dela, as três listas, cada uma com natureza e data, e o nome da lista
como texto do link.

**Acceptance Scenarios**:

1. **Given** um Edital com dois Perfis e três listas cada, **When** a página é aberta, **Then** o
   bloco mostra dois grupos, um por Perfil, na mesma ordem da seção Vagas, e nenhum resultado de um
   Perfil aparece no grupo do outro.
2. **Given** um grupo de Perfil, **When** lido, **Then** a etapa aparece como título dentro dele, e
   cada lista aparece abaixo com o próprio nome como link, a natureza ("Resultado definitivo") e a
   data de publicação.
3. **Given** três listas da mesma etapa, todas no definitivo e publicadas no mesmo dia, **When** a
   página é aberta, **Then** cada lista mostra a sua natureza e a sua data, sem que nada suba para o
   título da etapa (decisão recebida 2).
4. **Given** a lista "Ampla concorrência", gravada sem nome, **When** a página é aberta, **Then**
   ela aparece com esse nome, como no documento oficial.

---

### User Story 2 — Listas em fases diferentes (Priority: P1)

Quem abre a página de um Edital em que a lista PPI ainda está no preliminar, com prazo de recurso
aberto, e as outras duas já estão no definitivo vê cada lista dizer a própria fase e o próprio
prazo.

**Why this priority**: é o caso que a regra condicional erraria, e a razão da decisão recebida 2.
Uma página que dissesse "Resultado definitivo" no título da etapa estaria afirmando algo falso
sobre a PPI.

**Independent Test**: publicar o definitivo de duas listas e só o preliminar da terceira, com prazo
recursal aberto; conferir a natureza, a data e o prazo de cada lista.

**Acceptance Scenarios**:

1. **Given** duas listas no definitivo e uma no preliminar, **When** a página é aberta, **Then**
   cada lista diz a sua natureza, e nenhuma natureza aparece fora da linha da lista.
2. **Given** uma lista com prazo de recurso aberto, **When** a página é aberta, **Then** só essa
   lista mostra "recurso até", com data e hora, como hoje (`FR-770`).

---

### User Story 3 — O histórico, consolidado e ainda separado por lista (Priority: P2)

Quem quer ler o resultado preliminar que o definitivo sucedeu abre um único bloco recolhido de
publicações anteriores e encontra cada uma com a lista, a natureza, a data e a marca de sucedida.

**Why this priority**: o histórico tem de continuar alcançável (`FR-772`), mas hoje ocupa seis
linhas no nível do vigente.

**Independent Test**: com três listas, cada uma com preliminar sucedido por definitivo, contar os
blocos de histórico na página e conferir, em cada item, a lista, a natureza, a data, a marca de
sucedido e o link.

**Acceptance Scenarios**:

1. **Given** uma etapa com três listas, cada uma com uma publicação anterior, **When** a página é
   aberta, **Then** há um único bloco recolhido de publicações anteriores para a etapa, com a
   contagem total no resumo, e não um por lista.
2. **Given** o bloco aberto, **When** lido, **Then** cada item diz a lista a que pertence, a
   natureza, a data e que foi sucedido, e leva à página da publicação.
3. **Given** a cadeia da PPI com três publicações e a da PcD com uma, **When** o bloco é aberto,
   **Then** nenhuma publicação da PPI aparece como histórico da PcD, e vice-versa.
4. **Given** uma etapa em que nenhuma lista foi sucedida, **When** a página é aberta, **Then**
   nenhum bloco de histórico aparece para ela.

---

### User Story 4 — Ir direto à situação individual (Priority: P2)

Quem participou do processo e quer saber se foi classificado encontra, no bloco de resultados e
separado dos documentos públicos, o caminho para a própria situação.

**Why this priority**: "fui aprovado?" não se responde lendo um documento público; o portal já
calcula a situação de cada inscrição. Hoje o único caminho é o "Entrar" do topo da página, sem
relação visível com os resultados.

**Independent Test**: abrir a página com resultados divulgados sem estar conectado, conectado sem
inscrição enviada no Edital e conectado com uma inscrição enviada; conferir o texto e o destino em
cada caso.

**Acceptance Scenarios**:

1. **Given** uma pessoa não conectada, **When** abre a página de um Edital com resultado divulgado,
   **Then** o bloco mostra "Participou deste processo seletivo?", a explicação e a ação "Entrar para
   ver minha situação", e a identificação devolve a pessoa ao Edital.
2. **Given** uma pessoa conectada com inscrição enviada no Edital, **When** abre a página, **Then**
   a ação leva direto à inscrição, onde a situação é mostrada, sem pedir nova identificação.
3. **Given** uma pessoa conectada sem inscrição enviada no Edital, **When** abre a página, **Then**
   o convite não aparece.
4. **Given** qualquer um dos casos, **When** a página é lida, **Then** o convite não fica dentro de
   nenhum Perfil, etapa ou lista.

---

### Edge Cases

- **Um Perfil, uma etapa e uma lista.** A hierarquia continua (decisão recebida 1): título do
  Perfil, título da etapa e a linha "Ampla concorrência". É mais alto que hoje, e é previsível.
- **Várias etapas no mesmo Perfil** (resultado da prova escrita e classificação final, por exemplo).
  As etapas aparecem na ordem do certame, e não na ordem em que foram divulgadas — a mesma ordem que
  a Área do Candidato já usa para as situações da pessoa.
- **Perfil renomeado por Retificação.** O título do grupo é o nome do Perfil no Edital vigente — o
  mesmo da seção Vagas, logo abaixo. As publicações continuam dizendo, na página delas e no
  documento oficial, o nome que tinham quando foram publicadas.
- **Perfil retirado por Retificação depois de ter resultado divulgado.** O grupo continua, com o
  nome gravado na publicação mais recente dele: um resultado publicado não deixa de ser alcançável
  porque a vaga mudou.
- **Publicação anterior à `021`**, sem lista. É a ampla concorrência, e aparece com esse nome.
- **Edital que ainda recebe inscrições e já tem resultado divulgado** (uma etapa intermediária, por
  exemplo). O bloco aparece sem destaque, como hoje, e com a mesma hierarquia.
- **Pessoa conectada com mais de uma inscrição enviada no Edital** (quando o Edital permite). A ação
  leva à lista de inscrições da pessoa, e não a uma escolhida pelo sistema.

---

## Requirements *(mandatory)*

### A hierarquia

- **FR-1148**: O bloco "Resultados divulgados" da página pública do Edital MUST agrupar as
  publicações vigentes por Perfil, e dentro de cada Perfil por etapa, e dentro de cada etapa por
  lista de concorrência (decisão recebida 1).
- **FR-1149**: Os Perfis MUST aparecer na mesma ordem da seção Vagas da página. Um Perfil que já não
  existe no Edital vigente e tem resultado divulgado MUST aparecer depois dos outros.
- **FR-1150**: As etapas de um Perfil MUST aparecer na ordem do certame, e não na ordem de
  divulgação.
- **FR-1151**: As listas de uma etapa MUST aparecer com a ampla concorrência primeiro e as demais na
  ordem em que o Edital as declara.
- **FR-1152**: O título do grupo de Perfil MUST ser o nome do Perfil no Edital vigente; para Perfil
  ausente do vigente, o nome gravado na publicação mais recente dele.
- **FR-1153**: O título da etapa MUST ser o nome do marco gravado na publicação, sem corte nem
  reescrita (decisão recebida 4).

### Cada lista

- **FR-1154**: Cada lista MUST mostrar, na própria linha, o nome dela como texto do link para a
  publicação vigente, a natureza dessa publicação e a data em que ela foi publicada (decisões
  recebidas 2 e 3).
- **FR-1155**: A natureza e a data MUST NOT aparecer no título da etapa nem no do Perfil, mesmo
  quando todas as listas da etapa coincidem (decisão recebida 2).
- **FR-1156**: O prazo de recurso aberto MUST continuar aparecendo na linha da lista a que se
  aplica, com data e hora, nas mesmas condições de hoje (`FR-770`, `FR-771`).

### O histórico

- **FR-1157**: As publicações sucedidas de uma etapa MUST ficar num único bloco recolhido por etapa,
  com a contagem total no resumo; uma etapa sem publicação sucedida MUST NOT mostrar o bloco.
- **FR-1158**: Cada item do histórico MUST dizer a lista, a natureza, a data de publicação e que foi
  sucedido, e levar à página da publicação (`FR-772`, decisão recebida 5).
- **FR-1159**: O histórico MUST manter as cadeias separadas: uma publicação MUST aparecer só sob a
  lista e a etapa a que pertence, e dentro de cada lista da mais recente para a mais antiga.

### O acesso à situação individual

- **FR-1160**: Quando houver resultado divulgado, o bloco MUST oferecer, separado da árvore de
  publicações e fora de qualquer Perfil, etapa ou lista, o convite "Participou deste processo
  seletivo? Consulte sua classificação e situação individual." (decisão recebida 6).
- **FR-1161**: Para quem não está conectado, a ação MUST ser "Entrar para ver minha situação" e,
  depois da identificação, MUST devolver a pessoa à página do Edital.
- **FR-1162**: Para quem está conectado com exatamente uma inscrição enviada no Edital, a ação MUST
  levar direto a essa inscrição; com mais de uma, à lista de inscrições da pessoa.
- **FR-1163**: Para quem está conectado sem inscrição enviada no Edital, o convite MUST NOT
  aparecer.

### O que não muda

- **FR-1164**: O bloco MUST manter o destaque visual quando o Edital não recebe inscrições, e a
  ausência dele quando recebe (decisão recebida 7).
- **FR-1165**: Esta feature MUST NOT alterar publicação, conteúdo publicado, documento oficial,
  cadeia de sucessão, classificação ou regra do certame. A página de cada publicação MUST continuar
  como está.

### Apresentação e acessibilidade

- **UX-151**: Os títulos MUST formar uma hierarquia sem saltos: o do bloco, abaixo dele o de cada
  Perfil, abaixo o de cada etapa.
- **UX-152**: Nenhum par de links do bloco MUST ter o mesmo texto e destinos diferentes.
- **UX-153**: A 375 px, o bloco MUST caber sem rolagem horizontal da página, e a natureza, a data e
  o prazo de recurso MUST quebrar para baixo do nome da lista em vez de alargar a linha.
- **UX-154**: A distinção entre vigente e sucedido MUST continuar dita em texto, e não só por cor
  (`FR-052` da `017`).

### Key Entities

- **Publicação de resultado**: já existe. Tem Perfil, marco, lista, natureza, data de publicação e
  publicação anterior; o conteúdo gravado traz os nomes do Perfil, do marco e da lista do dia da
  publicação. Nada nela muda.
- **Cadeia**: as publicações de um mesmo marco e uma mesma lista, ligadas pela sucessão. A vigente
  é a que ninguém sucedeu. Continua sendo a unidade do histórico.
- **Inscrição enviada**: já existe; decide o destino da ação de situação individual.

---

## Success Criteria *(mandatory)*

- **SC-443**: Na página de um Edital com dois Perfis e três listas cada, a pessoa encontra o link
  da lista em que concorreu lendo só o título do próprio Perfil, o da etapa e o nome da lista — sem
  ler nenhuma linha de outro Perfil.
- **SC-444**: Em nenhum dos cenários de aceitação desta spec dois links do bloco têm o mesmo texto e
  destinos diferentes.
- **SC-445**: Numa etapa em que as listas estão em fases diferentes, a página diz a fase certa de
  cada lista em 100% dos casos.
- **SC-446**: O número de blocos de histórico na página é no máximo o número de etapas com
  publicação sucedida — numa etapa com três listas sucedidas, um bloco, e não três.
- **SC-447**: Quem está conectado com uma inscrição enviada chega à própria situação com um clique a
  partir do bloco.
- **SC-448**: O custo da página não cresce com o número de publicações: o mesmo Edital com o dobro
  de publicações abre com o mesmo número de leituras ao banco.
- **SC-449**: A 375 px, a largura de rolagem da página é a largura da tela.

---

## Decisões

### D-001 — Um bloco de histórico por etapa, e não por Perfil

A decisão recebida 5 pede o histórico consolidado; restava dizer em que nível. Por etapa: é o menor
nível que ainda junta as três listas, e mantém o histórico perto do vigente que ele explica. Um
bloco por Perfil misturaria, num Perfil com prova escrita e classificação final, publicações de
etapas diferentes numa só contagem. Dentro do bloco, os itens se agrupam por lista, para que a
cadeia de cada uma continue legível (decisão do eixo da lista, da `021`).

### D-002 — O convite vem depois da árvore de publicações

A decisão recebida 6 deixou aberto se acima ou abaixo. Depois: o bloco existe para levar à
publicação oficial (`FR-050` da `017`), e a 375 px a ordem de leitura começa pelo que a página
publica. O convite é a segunda tarefa, e por ser separado da árvore não disputa o nível de nenhum
Perfil.

### D-003 — O convite conhece a pessoa conectada

A página já lê as inscrições da pessoa conectada naquele Edital para desenhar o convite de cada vaga
(nenhuma leitura nova). Mandar "Entrar" a quem já entrou seria um passo inútil, e oferecer "ver
minha situação" a quem não se inscreveu seria uma promessa vazia — daí os três casos de
`FR-1161` a `FR-1163`. Com mais de uma inscrição enviada, o destino é a lista, e não uma inscrição
escolhida pelo sistema.

### D-004 — O nome do Perfil vem do Edital vigente

O título do grupo serve para a pessoa achar a vaga, e a vaga está escrita na seção Vagas com o nome
vigente. Usar o nome gravado na publicação faria o mesmo Perfil aparecer com dois nomes na mesma
página depois de uma Retificação que o renomeasse. A publicação continua dizendo o nome do dia em
que foi publicada, na página dela e no documento oficial — é o ato. Perfil retirado do Edital
vigente cai para o nome gravado, porque não há outro.

---

## O que já existe e fica como está

- A página de cada publicação, o documento oficial e a ligação entre sucedida e vigente
  (`FR-773`).
- O nome "Ampla concorrência" para a lista gravada sem nome, que o #255 pôs num ponto só e que o
  documento oficial também usa.
- A seção do sorteio, a seção Vagas e o cronograma.
- O agrupamento das cadeias por marco e lista, que já existe na leitura das publicações; esta
  feature acrescenta o Perfil por cima dele e muda a apresentação.

---

## Assumptions

- O Perfil de cada publicação está registrado na própria publicação; agrupar por ele não exige
  leitura nova ao banco.
- A ordem do certame entre etapas é a que as publicações já gravam e que a Área do Candidato já
  usa.
- A ordem das listas declarada no Edital pode ser lida do Edital vigente, que a página já carrega.
  Uma lista que já não existe no vigente vai para o fim da etapa, com o nome gravado.
- A identificação do portal já aceita um destino de volta, conferido contra o próprio host.

---

## Out of Scope

- **A Área do Candidato** (`portal/acompanhamento.html`): quem está em mais de uma lista vê uma
  seção por publicação, com o mesmo título de marco e a mesma natureza, sem dizer a lista. É a mesma
  forma de defeito, e fica registrada em *Achados registrados*.
- **Orientação no cadastro do marco** ("informe só o nome da etapa; o Perfil já aparece
  separado"). Pode voltar se a repetição incomodar depois de vista a tela (decisão recebida 4).
- **A página de cada publicação**: continua com a mesma composição.
- **Linha do tempo unificada** de atos do Edital, já descartada pela decisão 007 da `047`.

---

## Achados registrados, fora do escopo

- **A Área do Candidato não diz a lista** (`portal/acompanhamento.html`). Encontrado em 06/10/2026
  ao corrigir o rótulo da página pública (#255). A pessoa classificada em duas listas vê duas
  seções "Classificação final — Matemática / Resultado definitivo" com posições diferentes, e não
  sabe qual posição é de qual lista. A decisão de escopo é do usuário.
