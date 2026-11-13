# Feature Specification: Quem faz o quê

**Feature Branch**: `claude/161-quem-faz-o-que`, sobre a `main` em `76ac8ea1`

**Created**: 2026-11-13

**Status**: Especificada e clarificada em 13/11/2026; nada implementado. As quatro decisões de
produto foram tomadas pelo usuário no mesmo dia, todas na alternativa recomendada (ver
*Clarifications*). Pendente: o SC-2297, humano.

**Input**: estudo [`doc/estudo-minhas-atividades-2026-11-12/`](../../doc/estudo-minhas-atividades-2026-11-12/README.md),
rodada 4 (§3, §4, §5 e §6a) e o wireframe 3 ("Presidência: quem faz o quê"). Em 12/11/2026 o usuário
aprovou a direção do estudo, em três entregas:
1. *Minhas atividades*: o que eu executo (a `160`, mergeada);
2. *Quem faz o quê*, no Centro: como a comissão se organiza;
3. responsabilidade por frente, sem conceder permissão: só com evidência da comissão real.

**Esta spec é só a segunda.** Os cenários de treinamento que a exercitam entraram na `main` em
13/11/2026 (o C08 com um recurso admitido, o C12 com uma alocação à conferência).

> **Faixa de identificadores.** Esta spec abre em **FR-6900**, **SC-2290** e **UX-720**. O teto
> medido em 13/11/2026, em todas as branches locais e remotas, era o requisito seis mil oitocentos e
> oitenta e oito, o critério dois mil duzentos e oitenta e um e o requisito de experiência setecentos
> e quinze, todos da `160`. A pasta `160` é a última tomada, e não havia PR aberto. As decisões
> reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-6869 da `160`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> As decisões do estudo são citadas pela ordem ("a 5ª decisão do estudo").

---

## Por que esta feature existe

A visão aceita na rodada 4 do estudo diz: *o presidente organiza quem responde por cada frente e
acompanha o que está feito, em aberto, parado ou sem responsável, sem planilha paralela.* A primeira
entrega respondeu "o que **eu** faço agora". Esta responde a pergunta da presidência:

> **Quem responde por cada frente deste Edital, e o que está sem ninguém?**

O GPS já sabe quase tudo isso, mas em lugares separados:
- **o que está em aberto, e de que papel é**: a derivação do andamento (`127`), que o Centro de
  Controle mostra (`136`, `138`, `139`). Para o que não é da pessoa que olha, o Centro diz só o papel
  ("Quem publica resultado: …"), e nunca quem é;
- **quem tem a base para cada ato**: a presidência e os membros, no vínculo de comissão; os membros
  alocados a cada Etapa; os alocados à conferência (`115`); os designados para a formalização
  (`117`); e os papéis da unidade (`106`, `107`). Cada uma tem a sua tela, e nenhuma é lida junto
  com o andamento.

Para saber se a conferência tem alguém, a presidência abre a tela da alocação à conferência; para a
avaliação, Alocação por Etapa; para a formalização, a designação. E nenhuma delas diz se aquele
trabalho está em aberto agora.

**Esta entrega lê junto, e não grava nada.** Cada linha é uma providência que o Centro já mostra, e
cada nome sai de uma base que já existe. Nada aqui atribui trabalho, marca status ou concede
permissão. A responsabilidade gravada por frente, sem base, é a terceira entrega, e fica fora.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- um bloco "Quem faz o quê neste Edital" no Centro de Controle, recolhido (5ª decisão do estudo, e o
  wireframe 3);
- as frentes do Edital, que são as fases do Centro, sem taxonomia nova;
- em cada frente, o trabalho em aberto que o Centro já mostra, com quem tem a base para praticá-lo,
  pelo nome e pela base;
- em cada frente, as bases designadas mesmo sem trabalho em aberto: quem está alocado a cada Etapa,
  à conferência, e designado para a formalização;
- "sem ninguém", quando a base que o ato pede não tem pessoa nenhuma: é observável;
- a nota de cobertura do bloco.

**Fica fora:**
- **gravar qualquer coisa**: tarefa, status marcado à mão, responsável, marca de visto (§3 da rodada
  4);
- **a responsabilidade sem base** ("João acompanha o sorteio"): é a terceira entrega, condicionada a
  evidência de necessidade real (§6 e §6a da rodada 4);
- **prazo da comissão e "atrasado"**: não existe prazo da comissão (4ª decisão do estudo), e a
  palavra não entra em entrega nenhuma (§6a da rodada 4);
- **"parado há N dias"**: a derivação não tem `desde` depois da publicação (D-007);
- **o trabalho fora do GPS**: nada externo aparece como feito, nem por inferência (§6a da rodada 4);
- **a visão entre Editais** ("onde há acúmulo"): é a terceira entrega;
- a Retificação, que a Lista mostra (a decisão de Retificação da `127`), a publicação das inscrições
  (`148`), os avisos (`066`), o Requerimento de Matrícula e o encerramento, que não é providência.

## Clarifications

### Session 2026-11-13 (decisões do estudo e restrições do pedido, já aceitas)

- Q: Onde mora a visão da comissão? → A: **No Centro de Controle de cada Edital** (5ª decisão do
  estudo, revista na rodada 4 como segunda entrega; wireframe 3). Não é página nova nem faixa da
  Lista.
- Q: O que a visão lê? → A: **Só as bases existentes**: presidência, alocação à Etapa, alocação à
  conferência, designação para a formalização e os papéis da unidade. **Nada novo é gravado** (§4 da
  rodada 4, linha 2).
- Q: Como as frentes se agrupam? → A: **Pelas fases do Centro**, a mesma classificação que o Centro e
  "Minhas atividades" usam (§5 da rodada 4, item 1). Nenhuma taxonomia nova.
- Q: A designação dá permissão? → A: **Não.** O bloco nomeia quem já tem a base; não concede nem
  verifica nada (D-009). A designação que não concede é a terceira entrega.
- Q: "Atrasado", "parado", "sem responsável"? → A: **"Sem responsável" é observável** e entra.
  **"Parado há N dias"** só onde a derivação tem `desde`, e depois da publicação ela não tem: fica
  fora (D-007). **"Atrasado"** nunca aparece (§6a da rodada 4).

### Session 2026-11-13 (decisões do usuário)

- Q: Quem vê o bloco, que nomeia pessoas e diz o que está sem ninguém? → A: **Quem já vê a matriz
  "Onde cada lista está"**: a presidência, quem tem a base de gestão da comissão (o Gestor) e a
  auditoria. Os outros papéis abrem o Centro sem o bloco e sem custo a mais (FR-6901, SC-2296).
- Q: Como aparecem os papéis da unidade (Publicador, Julgador de recursos, administração de
  acessos)? → A: **Pelas pessoas com vínculo vigente do papel na unidade do Edital**, com "sem
  ninguém" quando não há vínculo. Na demonstração, em que o seletor só declara o papel na sessão, o
  bloco diz que nenhum vínculo está registrado (FR-6907).
- Q: Na avaliação, cada membro alocado aparece com quantas inscrições tem pendentes? → A: **Sim, com
  a contagem da Mesa** ("5 pendentes"), a mesma do cartão da Etapa. Só neste Edital; a comparação entre
  Editais é da terceira entrega (FR-6913).
- Q: As linhas repetem "O que fazer agora", ou anotam as providências de lá? → A: **Bloco separado**,
  como o wireframe 3: "O que fazer agora" não muda, e a leitura da comissão fica num lugar só (D-010).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A presidência vê quem responde por cada frente (Priority: P1)

A presidente abre o Centro de Controle do Edital SIM12/2026 e abre "Quem faz o quê neste Edital". Lê
as frentes na ordem do mapa. Em **Convocação**, lê "Conferir os documentos de 3 convocações" e, ao
lado, "Quem pode: você (presidência), treino.avaliacao2 (alocada à conferência, todos os Perfis)".
Em **Avaliação**, lê cada Etapa com quem está alocado. Ela não abre outra tela para saber quem cobre
o quê.

**Why this priority**: é a pergunta da segunda entrega, e hoje a resposta está em quatro telas.

**Independent Test**: no C12, com a identidade da presidência, o bloco nomeia `treino.avaliacao2`
na frente Convocação, com a base "alocada à conferência", e a linha é a mesma providência que o
Centro mostra em "O que fazer agora".

**Acceptance Scenarios**:

1. **Given** um Edital com conferência em aberto e um membro alocado à conferência, **When** a
   presidência abre o bloco, **Then** a frente Convocação tem a linha da conferência com a
   presidência e o membro alocado, cada um com a sua base.
2. **Given** um Edital com Etapas de avaliação e membros alocados, **When** o bloco é aberto,
   **Then** a frente Avaliação lista cada Etapa com os membros alocados a ela, ainda que não haja
   inscrição a avaliar agora.
3. **Given** uma pessoa designada para a formalização do Edital, **When** o bloco é aberto, **Then**
   a frente Conclusão a nomeia, com a base "designada para a formalização" e os Perfis que a
   designação alcança.
4. **Given** um ato praticado na tela do ato, **When** o Centro é aberto de novo, **Then** a linha
   não está mais no bloco, sem ação nenhuma nele.

---

### User Story 2 — O que está sem ninguém salta à vista (Priority: P1)

Uma Etapa de títulos não tem membro alocado. A formalização tem pessoas aptas e ninguém designado
para recebê-las. O título recolhido do bloco já diz "2 sem ninguém", e a frente de cada uma diz,
em palavras, que base falta, com o caminho para a tela que a cria, quando a pessoa que olha pode
criá-la.

**Why this priority**: "sem responsável" é a única das três palavras do §6a que o GPS pode dizer
hoje de toda frente, e é o que a presidência precisa ver primeiro.

**Independent Test**: num Edital com uma Etapa sem alocação, o título do bloco conta 1 sem ninguém, a
frente Avaliação diz "Nenhum membro alocado" para aquela Etapa, e o link leva a Alocação por Etapa.

**Acceptance Scenarios**:

1. **Given** uma Etapa sem membro alocado, **When** o bloco é lido, **Then** a Etapa diz "sem
   ninguém alocado" e o título do bloco a conta.
2. **Given** a passagem ao setor com pessoas aptas e nenhuma designação vigente, **When** o bloco é
   lido, **Then** a frente Conclusão diz que ninguém está designado para receber.
3. **Given** a conferência sem membro alocado, **When** o bloco é lido, **Then** a frente
   Convocação diz que ninguém está alocado à conferência e que a presidência confere, e isso **não**
   conta como "sem ninguém" (D-008).
4. **Given** uma comissão sem presidência ativa, **When** o bloco é lido, **Then** ele diz, no alto,
   que a comissão está sem presidência, e cada ato de condução diz "sem ninguém".

---

### User Story 3 — O recurso e o resultado, com quem os pratica na unidade (Priority: P2)

No C08, o recurso da candidata 03 foi admitido por `treino.julgamento` e espera o mérito. Na frente
**Resultado e recursos**, a presidência lê "Decidir 1 recurso" e as pessoas com vínculo de Julgador de recursos na unidade do
Edital, pelo nome (FR-6907).

**Why this priority**: publicar o resultado e julgar recursos não são da comissão; o bloco precisa
dizer de quem são sem fingir que a comissão os distribui.

**Independent Test**: no C08, a frente Resultado e recursos tem a linha do recurso; sem vínculo de
Julgador de recursos na unidade, ela diz que nenhum está registrado, e com o vínculo concedido, nomeia
a pessoa.

**Acceptance Scenarios**:

1. **Given** um recurso admitido esperando o mérito, **When** a presidência abre o bloco, **Then** a
   frente Resultado e recursos tem a linha do recurso, com as pessoas que têm o vínculo de Julgador
   de recursos na unidade, ou "sem ninguém" sem vínculo (FR-6907).
2. **Given** o resultado definitivo esperando o prazo de recurso, **When** o bloco é lido, **Then**
   a linha diz a espera com a data e a origem dela, e não diz "sem ninguém".

---

### User Story 4 — O bloco não diz o que o GPS não observa (Priority: P2)

A sessão pública do sorteio, o contato com o convocado e a conferência em papel acontecem fora do
GPS. O bloco não os mostra como feitos, nem como em aberto. A nota de cobertura diz que o bloco lê
só os atos do GPS e as bases que ele guarda. Nenhuma linha diz "atrasado", "seu prazo" nem "parado".

**Independent Test**: em todos os cenários de treinamento, o texto do bloco não tem "atrasad",
"seu prazo" nem "parado", e a nota de cobertura está presente.

**Acceptance Scenarios**:

1. **Given** qualquer Edital com andamento, **When** o bloco é lido, **Then** a nota diz o que ele
   lê e o que fica fora, com onde está cada coisa.
2. **Given** uma espera com data, **When** o bloco a mostra, **Then** a data vem com a origem, como
   a FR-6869 da `160`, e nunca como prazo de alguém.

---

### User Story 5 — Quem não vê a condução não vê o bloco (Priority: P2)

O bloco nomeia pessoas e diz o que está sem ninguém: é leitura de quem organiza a comissão. Quem
não está entre os que o veem (FR-6901) abre o Centro como hoje.

**Independent Test**: com a identidade de um papel que não vê o bloco, o Centro não o tem e não paga
consulta nenhuma por ele.

**Acceptance Scenarios**:

1. **Given** uma pessoa fora de quem vê o bloco, **When** ela abre o Centro, **Then** o bloco não
   aparece, e o número de consultas da página é o de hoje.

### Edge Cases

- **A mesma pessoa em várias bases** (preside e está alocada à conferência). Um nome, com as bases
  juntas ("presidência; alocada à conferência").
- **A pessoa que olha está na lista.** Ela aparece como "você", com a base, como a marca SUA do
  Centro.
- **Gestor.** Pode intervir em toda comissão da unidade por permissão de gestão. Não é listado pelo
  nome em cada ato de condução: uma nota única diz que os Gestores da unidade também podem (D-004).
- **Processo encerrado ou cancelado.** A comissão não pratica mais nada (`Alcance.ativo`). O bloco
  diz isso uma vez, e não diz "sem ninguém" em ato nenhum da comissão. A formalização continua, como
  a FR-3710 da `117` manda, e a frente Conclusão continua nomeando quem a recebe.
- **Alocação, vínculo ou designação inativos, ou pessoa suspensa.** Não contam: a base é a que a
  tela do ato aceita hoje, pelo mesmo predicado (FR-6915).
- **Etapa governada pela faixa.** Fica na frente Vagas, como no Centro, com os alocados a ela.
- **Alocação a uma Etapa que a versão vigente não tem mais** (a Retificação a removeu). Não aparece:
  a frente lê as Etapas da versão vigente.
- **Espera sem data.** Dita pela frase da derivação, sem data inventada.
- **A derivação não pôde ser lida.** O Centro não abre (volta o detalhe), e o bloco não existe: não
  há segunda leitura.
- **Demonstração.** No seletor de identidade, os papéis da unidade são declarados na sessão, e não
  são vínculo: a forma que lê pessoas por vínculo não acha ninguém. O bloco diz o que leu ("nenhum
  vínculo de Julgador de recursos registrado na unidade"), e não "ninguém pode julgar".
- **Comissão só com a presidência.** Toda Etapa sem alocação diz "sem ninguém alocado". É o caso da
  equipe inicial de 2–3 pessoas, e é verdade: presidir não atribui avaliação (a FR-6887 da `160`).
- **Edital encerrado.** Lê-se como hoje no Centro; a formalização continua.
- **Julgador na demonstração.** No C08, `treino.julgamento` admitiu o recurso pelo seletor, sem
  vínculo: a linha do recurso diz que nenhum vínculo de Julgador de recursos está registrado. Quem
  admitiu não é listado como quem decide, porque a FR-6907 não lê a trilha.
- **Impedimento de julgador.** O bloco não o calcula: a tela do recurso o nomeia antes do botão
  (D-005).

## Requirements *(mandatory)*

### Functional Requirements

#### A. O lugar e quem vê

- **FR-6900**: O Centro de Controle do Edital MUST ter um bloco **"Quem faz o quê neste Edital"**,
  recolhido por elemento nativo, depois de "O que fazer agora" e antes do detalhe da fase consultada.
  Nenhuma página, rota ou item de barra novos (D-001).
- **FR-6901**: O bloco MUST aparecer só para quem já vê a matriz "Onde cada lista está": a
  presidência ativa da comissão, quem tem a base de gestão da comissão e quem tem a capacidade de
  auditoria. Para os demais (quem só elabora, homologa, publica ou julga, e o membro que só avalia ou
  confere), ele MUST NOT ser montado.
- **FR-6902**: O bloco MUST existir só onde o Centro existe: Edital publicado ou encerrado, com o
  andamento lido.

#### B. As frentes

- **FR-6903**: O bloco MUST se organizar pelas oito fases do Centro, na ordem do mapa e com os mesmos
  nomes. Cada providência MUST cair na fase pela mesma classificação que o Centro usa, e cada Etapa
  pela mesma regra de Etapa governada. Nenhuma taxonomia nova (D-003).
- **FR-6904**: Cada frente MUST dizer o andamento da fase, com a palavra e o sinal do mapa. A frente
  sem trabalho em aberto e sem base designada MUST ser nomeada numa linha só, junto das outras nas
  mesmas condições, para que nenhuma fique em silêncio.

#### C. O trabalho em aberto, e quem tem a base

- **FR-6905**: As linhas de trabalho de cada frente MUST ser as providências em aberto (*Pendente*,
  *Obsoleto*, *Aguarda*, *Impedido*) que o Centro mostra à mesma pessoa no mesmo instante, sejam
  dela ou de outro papel, com o mesmo ato e o mesmo lugar. O bloco MUST NOT escrever frase própria
  para um ato da derivação, e MUST NOT rodar a derivação de novo (D-002).
- **FR-6906**: Toda linha *Pendente* ou *Obsoleto* MUST dizer **quem tem a base** para praticá-la,
  pela base que a tela do ato aceita:
  - condução: a presidência ativa da comissão;
  - avaliar: os membros alocados àquela Etapa;
  - conferir os documentos: a presidência e os membros alocados à conferência cujo alcance cobre o
    Perfil;
  - definir os documentos da formalização: a presidência;
  - designar para a formalização: a presidência, e as pessoas com vínculo vigente de administração
    de acessos na unidade (FR-6907);
  - receber os documentos da formalização: as pessoas com designação vigente que cobre o Perfil;
  - publicar o resultado e decidir recursos: as pessoas com vínculo vigente de Publicador e de
    Julgador de recursos na unidade do Edital (FR-6907).
- **FR-6907**: Os papéis da unidade (Publicador, Julgador de recursos, administração de acessos)
  MUST aparecer pelas **pessoas com vínculo vigente daquele papel na unidade do Edital**, e por nenhuma
  outra fonte: nem a trilha de quem já atuou, nem o papel declarado no seletor de demonstração. Sem
  vínculo, a linha MUST dizer "sem ninguém", com o que foi lido ("nenhum vínculo de Julgador de
  recursos registrado na unidade"), e não "ninguém pode julgar".
- **FR-6908**: Cada nome MUST vir com a base, em texto: "presidência", "alocado à Etapa", "alocado à
  conferência", "designado para a formalização", ou o nome do papel na unidade. A pessoa que olha
  MUST aparecer como "você", com a base.
- **FR-6909**: Quando a base que o ato pede não tem pessoa nenhuma, a linha MUST dizer **"sem
  ninguém"** e qual base falta ("nenhum membro alocado a esta Etapa", "ninguém designado para
  receber"). Se a pessoa que olha pode criar a base, a linha MUST levar à tela que a cria (Alocação
  por Etapa, a alocação à conferência, a designação); a tela verifica, pela porta de sempre.
- **FR-6910**: As linhas *Aguarda* e *Impedido* MUST dizer o que esperam, com a razão da derivação e
  quem resolve o impedimento, e MUST NOT dizer "quem pode" nem "sem ninguém": ninguém age agora. A
  data MUST vir com a origem, como a FR-6869 da `160`.
- **FR-6911**: Nos atos de condução, o bloco MUST NOT listar os Gestores pelo nome. Uma nota única
  MUST dizer que os Gestores da unidade também podem intervir, por permissão de gestão (D-004).

#### D. As bases designadas, com ou sem trabalho em aberto

- **FR-6912**: O alto do bloco MUST dizer quem preside a comissão. Sem presidência ativa, MUST dizer
  "Comissão sem presidência", e essa ausência MUST contar como "sem ninguém".
- **FR-6913**: A frente Avaliação (e a frente Vagas, para a Etapa governada) MUST listar cada Etapa
  da versão vigente com os membros alocados a ela, cada um com **quantas inscrições tem pendentes na
  Mesa daquela Etapa** ("5 pendentes"; "nada pendente"). O número MUST ser o da Mesa, o mesmo do
  cartão da Etapa e de "Minhas atividades" (a decisão de contagem pela Mesa da `160`), e MUST ficar
  neste Edital: o bloco MUST NOT somar a carga da pessoa em outros Editais. A Etapa sem alocação MUST dizer "sem ninguém
  alocado" e contar como "sem ninguém", tenha ou não inscrição a avaliar agora.
- **FR-6914**: A frente Convocação MUST listar as alocações à conferência, com os Perfis que cada uma
  alcança. Sem alocação, MUST dizer que ninguém está alocado e que a presidência confere; isso MUST
  NOT contar como "sem ninguém" (D-008).
- **FR-6915**: A frente Conclusão MUST listar as designações vigentes para a formalização, com os
  Perfis de cada uma. "Ninguém designado" MUST contar como "sem ninguém" só quando a derivação tem a
  providência de designar, isto é, quando há pessoa apta à espera de quem a receba.
- **FR-6916**: Uma base MUST contar só se a tela do ato a aceita hoje: vínculo de comissão ativo,
  alocação ativa, designação sem revogação, pessoa não suspensa, papel vigente. O bloco MUST ler
  esses predicados de onde as telas os leem, e MUST NOT copiá-los.

#### E. O que o bloco não diz

- **FR-6917**: Nenhuma linha do bloco MUST dizer "atrasado", "seu prazo" ou "prazo da comissão", e
  nenhuma data MUST ser apresentada como prazo de quem age.
- **FR-6918**: O bloco MUST NOT dizer "parado" nem "há N dias" (D-007).
- **FR-6919**: O bloco MUST NOT mostrar como feito, nem como em aberto, trabalho que o GPS não
  observa.
- **FR-6920**: O bloco MUST ter uma nota de cobertura: uma frase à vista (ele lê os atos do GPS e as
  bases que o GPS guarda, e não registra responsabilidade) e uma lista recolhida do que fica fora, com
  onde está cada coisa: a Retificação, na Lista; a publicação das inscrições, os avisos, o
  Requerimento de Matrícula e o encerramento, no próprio Centro; e o trabalho feito fora do GPS, que
  ele não vê.

#### F. Nada se grava, nada se concede

- **FR-6921**: Abrir o bloco MUST NOT gravar nada: nem tarefa, nem status, nem responsável, nem marca
  de visto, nem evento de trilha.
- **FR-6922**: O bloco MUST NOT conceder nem verificar permissão nova. Nomear uma pessoa não lhe dá
  acesso a nada, e todo link leva à tela que já decide (D-009).

#### G. O custo

- **FR-6923**: O bloco MUST reaproveitar o andamento que o Centro já leu. O número de consultas que
  ele acrescenta MUST ser constante: MUST NOT crescer com o número de membros, alocações, designações,
  vínculos, Perfis, Etapas ou providências. O teto é fixado no plano a partir da medição.
- **FR-6924**: Para quem não vê o bloco (FR-6901), o Centro MUST custar o mesmo número de consultas
  de hoje.

#### H. As coberturas em aberto do estudo

- **FR-6925**: A publicação das convocações (`149`) MUST entrar pela providência que a derivação já
  emite, "Registrar a publicação de N convocações", na frente Convocação, com a presidência como base
  (a porta da publicação é a da condução, pela FR-5732 da `149`). A relação informativa, que não é
  providência, MUST NOT virar linha (D-006).
- **FR-6926**: Publicar o resultado e decidir recursos MUST entrar pela providência que a derivação
  já emite, com quem os pratica na forma da FR-6907.

#### I. O que se preserva para a terceira entrega

- **FR-6927**: O bloco MUST se organizar por Edital × frente, o grão da responsabilidade que a
  terceira entrega gravaria, e MUST nomear cada pessoa pela base, para que "responsável pela frente"
  se acrescente como mais uma base, sem mudar as existentes.

#### J. Treinamento

- **FR-6928**: A seção "Quem faz o quê nos cenários" do guia da equipe MUST apontar para o bloco, e o
  quickstart MUST percorrer o C08, o C12 e o C16 com ele.

### Requisitos de experiência

- **UX-720**: O título recolhido MUST dizer quantas frentes têm trabalho em aberto e quantas linhas
  estão "sem ninguém" ("Quem faz o quê neste Edital · 4 frentes com trabalho · 2 sem ninguém"), para
  que a ausência se veja sem abrir o bloco. Sem "sem ninguém", o título MUST NOT dizer "0 sem
  ninguém".
- **UX-721**: Cada linha MUST ter o ato como texto principal e, abaixo, "Quem pode:" seguido dos
  nomes e das bases. "Sem ninguém" MUST ser palavra, com sinal, e não só cor.
- **UX-722**: O sinal e a palavra de situação MUST ser os do Centro.
- **UX-723**: A 375 px, o bloco MUST caber sem rolagem horizontal: é lista, e não tabela de várias
  colunas.
- **UX-724**: Toda pessoa MUST aparecer pelo nome legível, nunca pelo identificador interno.

### Key Entities

Nenhuma entidade nova, nenhuma tabela, nenhuma migration. O bloco lê:
- **Vínculo de comissão** (`MembroComissao`): a presidência e os membros ativos;
- **Alocação à Etapa**: quem avalia cada Etapa;
- **Alocação à conferência** (`115`): quem confere, e que Perfis;
- **Designação para a formalização** (`117`): quem recebe, e que Perfis;
- **Vínculo de papel na unidade** (`106`, `107`): Publicador, Julgador de recursos, administração de
  acessos, na forma da FR-6907;
- **Providência** (`127`): o trabalho em aberto, com o papel de quem age.

A **frente** é a fase do Centro: não é entidade, é a classificação que já existe.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2290**: **Uma fonte só**: nos cenários de treinamento, para a presidência, 100% das linhas de
  trabalho do bloco são providências em aberto do Centro daquele Edital, com o mesmo texto, e 100%
  das providências em aberto do Centro estão no bloco, na fase que o Centro lhes dá.
- **SC-2291**: **As bases dos cenários**: no C05 o bloco nomeia `treino.avaliacao1` alocado à Etapa;
  no C12, `treino.avaliacao2` alocada à conferência; no C16, `treino.formalizacao` designada; no C17,
  a frente Conclusão diz que ninguém está designado para receber; no C08, a linha do recurso diz
  que nenhum vínculo de Julgador de recursos está registrado na unidade (o seletor não grava
  vínculo), e, num banco com o vínculo concedido, nomeia a pessoa.
- **SC-2292**: **Sem ninguém**: num Edital montado com uma Etapa sem alocação, uma passagem ao setor
  sem designação e uma comissão sem presidência, cada ausência aparece na sua frente, e o título do
  bloco as conta; num Edital sem ausência, o título não fala em "sem ninguém".
- **SC-2293**: **Vocabulário**: em todos os cenários de treinamento, o bloco não contém "atrasad",
  "seu prazo", "prazo da comissão", "parado" nem "há N dias".
- **SC-2294**: **Custo constante**: o número de consultas que o bloco acrescenta ao Centro é o mesmo
  com 1 e com 10 membros alocados, e com 1 e com 5 designações; para quem não vê o bloco, o Centro
  custa o de hoje.
- **SC-2295**: **Nada gravado**: abrir o Centro com o bloco não acrescenta linha a tabela nenhuma.
- **SC-2296**: **Quem vê**: a presidência, o Gestor e a auditoria veem o bloco; o Elaborador, o
  Homologador, o Publicador, o Julgador de recursos e o membro que só avalia ou só confere abrem o
  Centro sem ele.
- **SC-2297**: **Validação com pessoas**, humana e pendente: com os cenários de treinamento e, quando
  houver, a comissão real, a tarefa "diga quem responde por cada frente deste Edital, e o que está sem
  ninguém" é cumprida sem abrir outra tela, pelo método de tarefas do estudo do Centro de Controle.

## Assumptions

- **A derivação da `127` não muda.** O bloco filtra, agrupa e anota o que ela emite; nenhuma regra de
  "sua" é reescrita, e nenhuma natureza ganha papel novo.
- **As células *Depois* e *Feito* não dizem o papel de quem age.** Por isso a frente sem trabalho em
  aberto mostra só as bases designadas, e não "quem fará": dizê-lo exigiria um mapa de frente para
  papel fora da derivação, que seria a segunda fonte (D-002).
- **Equipe inicial de 2–3 pessoas, acumulando papéis.** Na operação real, a maior parte das linhas
  terá a presidência; o bloco vale sobretudo pelo "sem ninguém" das Etapas e da formalização.
- **Os cenários de treinamento já cobrem a entrega** (#513, #518): o C08 com recurso admitido por
  `treino.julgamento`, o C12 com `treino.avaliacao2` alocada à conferência, o C16 e o C17 com a
  formalização. No seletor, `treino.julgamento` é papel declarado na sessão, e não vínculo.
- **Achado de 12/11, fora do escopo**: o cartão de `treino.avaliacao2` na página de acesso da
  demonstração diz só "Avaliação · 33 Etapas alocadas", sem a alocação à conferência. Fica
  registrado, e não é corrigido aqui.

## Decisões

### D-001 — O bloco mora no Centro, recolhido

A 5ª decisão do estudo pôs "Quem faz o quê" no Centro, e a rodada 4 a manteve como segunda entrega. O
wireframe 3 o desenha recolhido, abaixo das providências. Recolhido, ele não empurra "O que fazer
agora", que é o que a pessoa abre o Centro para ver; aberto, responde a pergunta da presidência sem
outra tela. Uma página própria duplicaria o Centro.

### D-002 — A linha é a providência; os nomes saem das bases

A pergunta "quem faz o quê" tem duas metades, e cada uma já tem fonte. O que está em aberto é da
derivação, e o bloco não escreve frase própria; quem tem a base é das tabelas de vínculo, alocação e
designação, lidas pelos predicados das telas. As células *Depois* e *Feito* não carregam o papel de
quem age: um mapa estático de frente para papel, escrito aqui, divergiria da derivação na primeira
natureza nova. Por isso a frente sem trabalho em aberto mostra só as bases designadas.

### D-003 — As frentes são as fases do Centro

O §5 da rodada 4 pediu que a responsabilidade, quando existir, se prenda a Edital × frente, e que a
taxonomia de frentes seja a das fases do Centro. A `160` já rotula por ela. Uma lista de frentes
própria criaria a segunda taxonomia que o estudo recusou.

### D-004 — O Gestor é nota, e não nome

O Gestor pode intervir em toda comissão da unidade, e isso não faz dele quem responde pela condução
de cada Edital. Listá-lo em cada ato de condução esconderia a presidência atrás de nomes que, na
prática, não conduzem; omiti-lo esconderia que ele pode. Uma nota única diz as duas coisas. É a
mesma leitura que a `160` fez para "Minhas atividades".

### D-005 — O impedimento do julgador não é calculado no bloco

O impedimento de julgar é decidido peça a peça, com cinco perguntas por ato, e a regra dele recusa
pagá-lo por linha de listagem. A tela do recurso o nomeia antes do botão. O bloco não o antecipa, e
por isso nunca diz que um julgador "pode" julgar uma peça específica: diz quem tem o papel.

### D-006 — A publicação das convocações já está coberta

O estudo listou a publicação das convocações (`149`) como cobertura em aberto. A parte que é ato
devido, publicar as convocações por publicação ainda não comunicadas, já é a providência "Registrar a
publicação de N convocações", de quem conduz, e a porta da publicação no GPS é a mesma da condução. A
relação informativa, das já comunicadas, é opcional e não é providência: virar linha seria inventar
trabalho.

### D-007 — "Parado há N dias" fica fora

A derivação depois da publicação não tem `desde`: tem o fim de uma espera (`ate`), que é outra coisa.
Só os objetos de trabalho da `104` têm `desde`, e só para a pessoa que pratica; usá-lo no bloco
diria "parado" de umas linhas e silenciaria das outras, sem que a pessoa soubesse por quê. Acrescentar
`desde` à derivação é a lacuna que a 5ª decisão do estudo já registrou, e é mudança da `127`, com spec
própria.

### D-008 — A conferência sem alocado não está sem ninguém

A presidência confere e desfecha por si; a alocação à conferência só acrescenta quem confere. Contar
"ninguém alocado" como ausência faria toda conferência de comissão pequena aparecer como problema,
quando não é.

### D-009 — Nomear não é designar

Toda base que o bloco lê já concede o ato, e o bloco não cria nenhuma. Uma pessoa nomeada aqui não
ganha acesso a nada, e um link para a tela da alocação não aloca: a tela verifica. A designação que
não concede é a terceira entrega, em registro próprio, com trilha e revogação, e sem reusar as
tabelas de alocação (§5 da rodada 4, item 4).

### D-010 — Um bloco separado, e não anotações em "O que fazer agora"

Decidido pelo usuário em 13/11/2026. As linhas do bloco repetem as providências que "O que fazer
agora" já mostra. A alternativa era anotar "Quem pode" em cada providência de lá e deixar no bloco só
as bases: não repetiria nada, mas mudaria a seção que todos os papéis leem primeiro, para responder
uma pergunta que é só de quem organiza a comissão. Separado, o bloco responde a pergunta inteira num
lugar, e "O que fazer agora" continua igual para todos.
