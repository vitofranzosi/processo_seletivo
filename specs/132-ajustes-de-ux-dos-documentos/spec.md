# Feature Specification: Cinco ajustes de leitura dos Documentos Exigidos

**Feature Branch**: `claude/funny-benz-83fc71`, sobre a `main` em `cd1d46d9`

**Created**: 2026-11-07

**Status**: Implementada (07/11), sem merge.

**Input**: a seção C ("diagnóstico de UX") do guia `doc/guia-documentos-no-gps-2026-11-06/`,
mergeado no PR #423, reconferida na `main` em `cd1d46d9` em 07/11/2026. Os cinco pontos estavam
abertos. A `131` acrescentou a condição publicada ao documento, no PDF e na página pública, e não
tratou deles.

> **Faixa de identificadores.** Esta spec abre em **FR-4501** e **SC-1401**. O teto foi medido em
> 07/11/2026 em `specs/` da `main`: o requisito funcional quatro mil quatrocentos e setenta e oito e
> o critério mil trezentos e setenta e oito, ambos da `131`. A outra sessão aberta no mesmo dia (o
> estudo da concorrência concomitante) não tomou numeração. A folga é a de costume. **Nenhum `UX-` é
> aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3594 da `115`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número.

## Por que esta feature existe

Nenhum dos cinco muda regra de negócio. Todos fazem uma tela dizer menos, ou outra coisa, do que o
sistema decide:

1. **A Revisão lia os documentos numa fila só.** Oito documentos, cada um com a linha "Pedido: na
   inscrição" ou "Pedido: na convocação". Quem homologa precisava contar de cabeça quantos são de
   cada momento — o que o PDF já mostra separando a seção "Documentos exigidos na convocação"
   (a FR-3569 da `115`).
2. **"Somente leitura" com cara de editável.** Com o Edital fora de elaboração, ou sem a permissão
   de elaborar, o aviso aparece no topo, mas os cartões de Inscrição, Perfis, Cronograma, Etapas e
   Classificação mantêm campos, setas e lixeira ativos. O servidor recusa o salvar; a tela não dizia
   isso a tempo. E **"Avançar" em somente leitura não avança**: o botão envia o formulário, e a
   resposta é "Não foi possível salvar: Este Edital não está em elaboração…" — a pessoa que só lia
   fica presa na etapa (comprovado no Edital 90/2026 do banco de demonstração, 07/11).
3. **O "Como preencher" dos documentos não falava do que a `115` acrescentou.** Explicava chave,
   instrução, recorte e modelo. Momento, aproveitamento, obrigatoriedade e condição só tinham
   explicação escondida, sob cada campo, para o leitor de tela.
4. **A página pública contava errado.** "4 documentos que serão pedidos" somava os facultativos e
   os que só uma modalidade pede, e nenhum facultativo vinha marcado. Quem lê antes de se inscrever
   tomava o facultativo por obrigatório e a soma por sua.
5. **O fundamento do indeferimento saía com "..".** A frase pré-redigida (a FR-3594 da `115`) junta
   "nome: motivo" e põe o ponto final. Os motivos registrados costumam terminar em ponto — os dois
   do banco de demonstração terminam —, e o texto saía com ".." no fim e ".;" no meio.

## Clarifications

### Session 2026-11-07

- Q: O veículo? → A: **Uma spec pequena só** para os cinco, como a `124` fez com os textos do
  sorteio (decisão do usuário, registrada pela sessão que abriu esta).
- Q: A contagem da página pública? → A: **Só os obrigatórios pedidos a todos do Perfil na
  inscrição.** Os facultativos aparecem na lista com "(facultativo)" e ficam fora da conta; os de
  modalidade e os da convocação continuam listados à parte, também fora dela (decisão do usuário,
  07/11/2026).
- Q: O somente leitura vai além da etapa Inscrição? → A: **Todas as etapas afetadas**: Inscrição,
  Perfis, Cronograma, Etapas de Avaliação e Classificação (decisão do usuário, 07/11/2026).
- Q: Na Classificação, a simulação e a conferência na Caixa leem os valores da tela, e campo
  desabilitado não vai no pedido. → A: **Preservar a simulação** — quem homologa continua
  simulando o Edital submetido (decisão do usuário, 07/11/2026).

## User Scenarios & Testing

### User Story 1 — A Revisão separa os documentos por momento (Priority: P1)

Quem homologa abre a Revisão do Edital 90/2026 e encontra dois blocos: "Documentos Exigidos na
inscrição (5)" e "Documentos Exigidos na convocação (3)". Cada documento aparece uma vez, no bloco
do seu momento, sem a linha "Pedido".

**Acceptance Scenarios**:

1. **Given** um Edital com documentos nos dois momentos, **When** a Revisão abre, **Then** há um
   bloco por momento, na ordem inscrição → convocação, cada um com a contagem no título e com o
   "Revisar" que volta à etapa Inscrição.
2. **Given** um Edital sem documento da convocação, **When** a Revisão abre, **Then** há um bloco
   só, o da inscrição.
3. **Given** qualquer documento, **When** ele é lido na Revisão, **Then** as demais linhas —
   exigência, a quem se aplica, condição, aproveitamento, instruções — continuam as mesmas.

### User Story 2 — Somente leitura de verdade (Priority: P1)

Quem abre a composição do Edital publicado vê os valores, sem campo que pareça aceitar digitação,
sem setas nem lixeira, e anda de etapa em etapa sem mensagem de recusa. Na Classificação, quem
homologa continua simulando a classificação e o sorteio.

**Acceptance Scenarios**:

1. **Given** o Edital fora de elaboração, **When** qualquer das cinco etapas abre, **Then** todo
   campo sai desabilitado, e nenhum controle de subir, descer, remover, acrescentar, duplicar ou
   aplicar aos demais aparece.
2. **Given** a mesma tela, **When** a pessoa clica em "Avançar", **Then** chega à etapa seguinte,
   sem formulário enviado e sem mensagem.
3. **Given** o Edital submetido, aberto por quem não elabora, **When** "Simular classificação" é
   acionado num marco, **Then** a prévia responde com os valores exibidos no cartão.
4. **Given** a composição editável, **When** qualquer etapa abre, **Then** nada muda.

### User Story 3 — A ajuda da etapa explica o momento (Priority: P2)

Quem elabora abre "Como preencher estes campos" sob "Documentos exigidos" e encontra o que é o
momento, o aproveitamento, a obrigatoriedade e a condição — com as mesmas frases que o leitor de
tela ouve em cada campo.

**Acceptance Scenarios**:

1. **Given** a etapa Inscrição, **When** a ajuda dos documentos abre, **Then** ela tem os itens
   "Quando é pedido", "Atendido pelo documento da inscrição", "Obrigatório" e "Exigido somente
   quando".
2. **Given** o cartão do documento, **When** ele é renderizado, **Then** ele não ganha ajuda
   visível nova.

### User Story 4 — A página pública conta o que é de todos e marca o facultativo (Priority: P1)

Quem lê o Perfil antes de se inscrever vê "1 documento obrigatório na inscrição", a lista com
"Currículo (facultativo)", e as modalidades e a convocação à parte.

**Acceptance Scenarios**:

1. **Given** um Perfil com um obrigatório e um facultativo para todos, e um documento só de uma
   modalidade, **When** a página abre, **Then** o resumo diz "1 documento obrigatório na
   inscrição".
2. **Given** um facultativo em qualquer grupo, **When** a lista é lida, **Then** ele leva
   "(facultativo)" depois do nome e da condição.
3. **Given** um Perfil sem obrigatório para todos na inscrição, **When** a página abre, **Then** o
   resumo não diz zero.

### User Story 5 — O fundamento sem ".." (Priority: P3)

Quem registra o indeferimento recebe a frase pré-redigida com a pontuação de uma frase só.

**Acceptance Scenarios**:

1. **Given** dois itens pendentes com motivos terminados em ponto, **When** a tela oferece o
   fundamento, **Then** ele termina com um ponto só, e os itens se separam por "; " sem ponto
   antes.

### Edge Cases

- **Edital anterior à `115`.** Todo documento sem momento é da inscrição (a FR-3563 da `115`): a
  Revisão mostra um bloco só, como antes, com o título novo.
- **Edital sem documento algum.** A Revisão mostra o bloco da inscrição com "Nada declarado.", como
  o bloco único mostrava.
- **Composição sem a permissão de elaborar, com o Edital em elaboração.** É somente leitura pelo
  mesmo aviso, e vale o mesmo que fora de elaboração.
- **Fragmento acrescentado.** O cartão novo que o htmx traz só é pedido na composição editável, e
  continua editável.
- **Motivo que termina em reticências, "?" ou "!".** Só o ponto final simples cede; a pontuação que
  diz algo fica.
- **Facultativo com condição.** Não existe: a condição só se publica no obrigatório (a FR-4453 da
  `131`).

## Requirements

### Functional Requirements

#### A Revisão por momento

- **FR-4501**: A conferência da Revisão MUST mostrar os Documentos Exigidos em **dois blocos**,
  "Documentos Exigidos na inscrição" e "Documentos Exigidos na convocação", nessa ordem, cada um
  com a contagem no título e com o caminho de volta à etapa Inscrição. É a separação que o PDF já
  faz (a FR-3569 da `115`).
- **FR-4502**: O bloco da convocação MUST existir só quando houver ao menos um documento da
  convocação, como a seção do PDF. O da inscrição MUST existir sempre, e vazio diz "Nada
  declarado.".
- **FR-4503**: O item MUST NOT trazer mais a linha "Pedido": o bloco a diz. As demais linhas e o
  número do item — a ordem declarada na composição — MUST continuar como estão.

#### Somente leitura

- **FR-4504**: Com a composição somente leitura — o Edital fora de elaboração ou o ator sem
  `edital:elaborar`, as duas condições do aviso que já existe —, todo campo das etapas Inscrição,
  Perfis, Cronograma, Etapas de Avaliação e Classificação MUST sair desabilitado. É a FR-002 da
  `002` (oferecer só o que a pessoa pode fazer) aplicada ao campo.
- **FR-4505**: Na mesma condição, os controles que mudam a lista — subir, descer, remover,
  acrescentar, duplicar o Perfil, aplicar aos demais Perfis, preencher pelo percentual — MUST NOT
  aparecer.
- **FR-4506**: Em somente leitura, "‹ Voltar" e "Avançar ›" MUST ser links para a etapa vizinha, em
  toda etapa que tem formulário: não há o que enviar, e o envio terminava em recusa.
- **FR-4507**: Na Classificação, "Simular classificação", "Simular sorteio" e "Conferir na Caixa"
  MUST continuar disponíveis em somente leitura e MUST receber os valores que o cartão exibe. É a
  prévia da FR-2234 da `094`, que só lê e calcula.
- **FR-4508**: A recusa da gravação no servidor MUST continuar como está. A tela deixa de oferecer
  a edição; quem decide se grava continua sendo o servidor.
- **FR-4509**: Na composição editável, e nos fragmentos que a composição editável pede, nada MUST
  mudar.

#### A ajuda dos documentos

- **FR-4510**: O "Como preencher estes campos" de "Documentos exigidos" MUST ter os itens
  **Quando é pedido**, **Atendido pelo documento da inscrição**, **Obrigatório** e **Exigido
  somente quando**, explicando o momento e o aproveitamento da `115` (FR-3563, FR-3566 e FR-3567
  dela) e a condição da `131` (a FR-4451 dela).
- **FR-4511**: Cada item MUST conter, palavra por palavra, a descrição que o campo já tem — a
  escondida, apontada por `aria-describedby`, ou a da marcação de obrigatório. Ele pode dizer mais;
  uma segunda redação da mesma frase, não.
- **FR-4512**: O cartão do documento MUST NOT ganhar ajuda visível. As descrições escondidas MUST
  continuar onde estão.

#### A página pública

- **FR-4513**: O resumo dos documentos de cada Perfil MUST contar só os **obrigatórios pedidos na
  inscrição a todos** do Perfil, e dizer isso: "N documento(s) obrigatório(s) na inscrição". Revisa
  a contagem que o anúncio dos documentos fazia (a FR-709 da `044` e a FR-1628 da `072` mantêm o
  anúncio; muda a conta).
- **FR-4514**: Todo documento facultativo, em qualquer grupo do anúncio — todos, cada modalidade, a
  convocação —, MUST levar "(facultativo)" depois do nome e da condição (a FR-4454 da `131`), com a
  mesma marca que a inscrição já usa.
- **FR-4515**: Sem obrigatório para todos na inscrição, o resumo MUST NOT dizer zero: diz
  "Documentos que podem ser pedidos na inscrição" quando a inscrição pede algum (facultativo ou de
  modalidade), e "Documentos pedidos só na convocação" quando só a convocação pede.

#### O fundamento do indeferimento

- **FR-4516**: O fundamento pré-redigido do indeferimento (a FR-3594 da `115`) MUST NOT conter "..";
  o ponto final de cada motivo MUST ceder à pontuação da frase — "; " entre os itens e um ponto no
  fim. O início da frase e a ordem dos itens MUST continuar os mesmos.

### Fora do escopo — registrado, e não corrigido

- **O anúncio do assistente de dúvidas.** `duvidas/domain/catalogo.py` faz as mesmas leituras da
  página pública para responder perguntas; ele não conta nem lista facultativo com marca, e esta
  spec não o toca.
- O aviso de pendência, a formalização, o Registro Acadêmico, a concorrência concomitante, o "não se
  aplica", o catálogo de documentos e o visualizador, pela abertura desta spec.

## Success Criteria

- **SC-1401**: Na Revisão de um Edital com documentos nos dois momentos, cada documento aparece
  exatamente uma vez, no bloco do seu momento, e a soma das duas contagens é o total de documentos.
- **SC-1402**: Em somente leitura, nas cinco etapas, nenhum campo do formulário da etapa sai
  habilitado, nenhuma seta, lixeira ou "Acrescentar" aparece, e "Avançar ›" leva à etapa seguinte
  sem mensagem.
- **SC-1403**: Em somente leitura, a simulação de um marco responde com a prévia calculada a partir
  dos valores do cartão, e não com "sem marco".
- **SC-1404**: A ajuda dos documentos tem os quatro itens, cada um com a frase do campo; o cartão
  continua com as mesmas descrições escondidas e sem ajuda visível nova.
- **SC-1405**: Na página pública, o número do resumo é o de obrigatórios a todos na inscrição, e
  todo facultativo listado leva "(facultativo)".
- **SC-1406**: O fundamento pré-redigido de pendências com motivos terminados em ponto não contém
  ".." nem ".;".
- **SC-1407**: As capturas de antes e depois das quatro telas estão em [capturas/](capturas/),
  tiradas de um banco descartável clonado de `gps_docs_demo`.

## Decisões

### D-001 — Dois blocos, e o número do item é o da composição

O título do item continua "6. Comprovante de escolaridade", com o número da ordem declarada, e não
reinicia em cada bloco como as alíneas do PDF. O "Revisar" do bloco leva à etapa Inscrição, onde os
cartões são "Documento exigido 6 de 8": recomeçar a numeração na Revisão faria a conferência e a
correção falarem de números diferentes para o mesmo documento.

### D-002 — Uma bandeira que só a tela da composição liga

Os cartões são os mesmos que os fragmentos htmx e a Retificação renderizam, e `editavel` não está
no contexto de todos eles — ausente, ele desabilitaria o cartão que o "Acrescentar" acabou de
pedir. A condição é `somente_leitura`, que só a view da composição põe no contexto: ausente, o
cartão é o de sempre (FR-4509).

### D-003 — Um `fieldset disabled` em volta da etapa, salvo na Classificação

Nas etapas Inscrição, Perfis, Cronograma e Etapas, o conteúdo do formulário — tudo menos a
navegação — vai para dentro de um `fieldset` desabilitado. Um atributo desabilita todo campo e todo
botão de dentro, inclusive os que nascerem amanhã num cartão; marcar campo a campo deixaria o
próximo campo de fora. A Identificação e o Conteúdo já marcavam os seus campos, e ficam como estão.

### D-004 — Na Classificação, campo a campo, e a simulação recebe o que a tela mostra

A simulação e a conferência na Caixa são botões dentro dos cartões. Dentro de um `fieldset`
desabilitado eles também ficariam desabilitados, e o htmx não leva campo desabilitado no pedido. Na
Classificação, então, cada campo leva o `disabled` próprio, os botões de consulta ficam de fora, e
um script pequeno (`somente-leitura.js`, carregado só em somente leitura) devolve ao pedido desses
botões os valores dos campos desabilitados que o `hx-include` deles alcança. A alternativa de
ler o marco do rascunho gravado mudaria a prévia da `094`, que lê o digitado por desenho.

### D-005 — O "Avançar" vira link, como na etapa Anexos

A etapa Anexos já navega por link, porque não tem o que enviar, e a Identificação já trocava o
botão por link quando não é editável — pela mesma razão, escrita no template dela. As demais etapas
somente leitura também não têm o que enviar: a navegação delas passa a ser a dos Anexos, e o envio
que terminava em recusa deixa de existir. A da Identificação fica como estava.

### D-006 — A ajuda repete a frase do campo e acrescenta

Como na `124`, a descrição escondida fica inteira no campo, e o item da ajuda a repete palavra por
palavra antes de acrescentar o que a ajuda pode dizer e o campo não: que o documento da convocação
não conta para o envio da inscrição, que o aproveitamento fica de fora quando o documento não foi
enviado, que facultativo e obrigatório nos dois momentos são independentes.

### D-007 — "Obrigatório na inscrição", e não "que serão pedidos"

O resumo que conta só os obrigatórios a todos precisa dizer isso, ou a conta parece errada de novo
a quem vê a lista mais longa ao abrir. "N documentos obrigatórios na inscrição" diz o critério da
conta; a lista aberta mostra o resto, com as marcas.

### D-008 — Só o ponto final simples cede

O motivo é texto de quem conferiu. Reticências, "?" e "!" dizem algo e ficam; o ponto final simples
é pontuação de fim de frase, e a frase do fundamento tem a sua.
