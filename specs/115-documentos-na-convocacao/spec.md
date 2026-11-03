# Feature Specification: Documentos e conferência na convocação

**Feature Branch**: `claude/nice-zhukovsky-0b4397`, sobre a `main` em `6137f1c4`

**Created**: 2026-11-03

**Status**: Draft, **revista em 03/11/2026 sobre o PR, com as decisões do usuário**. Nenhum código,
migration ou tela foi alterado. Cada grupo de decisões tem uma situação:

- **Do usuário, do pedido original:** D-001 a D-007.
- **Aprovadas pelo usuário na revisão do PR:**
  - a capacidade opcional por documento, em qualquer tipo de Edital (QI-2′);
  - a D-010 (quem confere e quem desfecha);
  - a D-012 (abertura antes do "conforme");
  - a D-018 (revisão da FR-402 da `029`), já aplicada no arquivo da `029`.
- **Ajustadas a pedido dele:** a D-011 (prazo alinhado ao do Requerimento) e a D-013 (aproveitamento
  entre chamadas).
- **Demais (D-008, D-009, D-014 a D-017):** propostas de desenho que a revisão não contestou.

O que ainda pede aprovação explícita é o texto da revisão da FR-374 da `029` (D-019). O merge deste
PR é a aprovação da spec.

**Input**: a [auditoria de matrícula e dossiê documental](../../doc/auditoria-matricula-e-dossie-documental-2026-11-03.md)
e o [complemento](../../doc/auditoria-matricula-e-dossie-documental-2026-11-03-complemento.md), de
03/11/2026. A §10 do complemento (decisão de fronteira do GPS) prevalece. Os dois estão no PR
vitofranzosi/processo_seletivo#367 (branch `claude/gps-audit-enrollment-docs-253134`), **ainda não
mergeado**; os links acima só resolvem depois do merge dele. Foram lidos integralmente daquela
branch, em `25ff20d7`.

> **Faixa de identificadores.** Esta spec abre em **FR-3563** e **SC-1081**. O teto foi medido em
> 03/11/2026 em `specs/` de todas as branches locais e remotas e de todas as worktrees desta máquina:
> o requisito funcional três mil quinhentos e sessenta e dois, e o critério mil e oitenta (os dois da
> `114`). **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-402 da `029`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> Os achados das auditorias (`MAT-NN`, `A-NN`) e as questões institucionais (`QI-N`) são citados como
> estão nos documentos de origem.

---

## Por que esta feature existe

**O GPS só sabe pedir documento na inscrição.** O Documento Exigido não tem momento
(`editais/models/documentos.py`). O documento só é recebido enquanto a inscrição é rascunho, e o
banco recusa inserir arquivo em inscrição enviada (`inscricoes/migrations/0007`). A FR-402 da `029`
fixou que *"documento específico de matrícula continua sendo Documento Exigido do Edital"*. Somados,
os três fatos fazem o **dado** de matrícula poder esperar a convocação (o Requerimento `AT_CALL` da
`029`), mas não o **documento**.

Daí duas práticas, ambas lidas em Editais reais:

- **pedir a todos os inscritos** o que só os convocados precisam apresentar: identidade, certidão,
  quitação eleitoral, diploma (77, 57, 28 e 76/2026);
- **mandar o convocado ao balcão**, mesmo em Edital composto no próprio GPS. O 72/2026 (item 8)
  pede a presença no Cefor *"para apresentação dos documentos de matrícula (ANEXO I)"*, e reclassifica
  quem não comparece.

A mesma necessidade aparece fora da matrícula:

- o 89/2026 (11.1–11.2) e o 146/2025 (16.1–16.2) exigem **na convocação** o certificado de curso que
  não veio na inscrição. Quem não o apresenta *"será desclassificado"*;
- o 140/2025 (10.3) e o 173/2025 (9.3) verificam requisitos *"no ato da vinculação"*;
- a Ficha de Cadastramento/Termo de Compromisso do Bolsista UAB é entregue depois da convocação (89,
  13.3; 146, 20.4).

**O GPS já tem o resto do ciclo**, e esta spec não o refaz:

- a convocação da `019`, com espécies, vencimento, chamadas sucessivas e sete desfechos com efeito na
  ocupação;
- o Requerimento de Matrícula `AT_CALL` da `029`;
- a exportação da `031`;
- a tela da convocação no portal, da `059`;
- a condução da convocação na gestão (`019`, `050`).

Falta pedir o documento na convocação, recebê-lo ali, conferi-lo item a item e fazer o desfecho
existente enxergar a conferência.

### O que esta spec cobre, e o que fica fora

Cobre, para qualquer Edital que o declare (aluno, bolsista, professor formador, colaborador):

- **A.** o momento do Documento Exigido, a seção do PDF e o contrato de mutabilidade;
- **B.** a lista exigida congelada na convocação e a apresentação pelo portal, com versões e
  aproveitamento por referência;
- **C.** a conferência por documento e a relação dela com os desfechos;
- **D.** a complementação até o vencimento da chamada;
- **E e F.** a evolução da tela da convocação no portal e da condução da convocação na gestão;
- **G.** autorização, trilha, unidade de atuação e o A-07 (abrir o dossiê não gera trilha).

**Fica fora, por decisão do usuário (§10 do complemento) ou por limite do pedido:**

- **GED, acervo, consulta longitudinal ou guarda prolongada.** O GPS conserva o que é do certame e
  não elimina nada nesta fase (FR-3615).
- **Entrega documental ao setor competente.** É lacuna registrada para uma segunda spec provável, que
  depende de revisar a FR-069 da `009`. Esta spec só preserva o que ela vai precisar (FR-3602).
- **Download em lote, ZIP ou exportação de documentos.** A FR-069 da `009` **não muda** (FR-3606).
- **Recurso contra o desfecho.** A decisão da `019` que tira a convocação e os desfechos do recurso
  continua valendo.
- **Aviso de pendência por e-mail.** Seria a quinta situação da FR-084 da `010` (FR-3614).
- **Multicampi**, ou seja, a designação de pessoa de outra unidade (MAT-09). Esta spec só não o
  fecha (FR-3602).
- **Editais de bolsista de cadastro de reserva.** Dependem do que a `097` registrou como ausente.
- **Desligamento depois do vínculo, taxonomia de natureza do vínculo, formulário estruturado de
  bolsista, dados bancários e requerimento genérico.**
- **Integração com SIGAA, CAPES, Fapes ou SIPAC.**
- **Varredura de malware** (MAT-08). A decisão fica registrada sem ampliar o escopo (D-016).

### Três responsabilidades, cada uma com um dono

| Quem | O que faz | Onde |
|---|---|---|
| Seleção (comissão do Processo) | pede, recebe, confere, decide e registra o desfecho | GPS, nesta spec |
| GPS | registra cada ato, conserva o que é do certame | GPS, nesta spec |
| Setor competente | formaliza (matrícula, vinculação, contrato) e custodia | fora do GPS |

Três termos, cada um com **uma** fonte só (§10.3 do complemento):

| Termo | Fonte | Quem pode afirmá-lo |
|---|---|---|
| **Apto para formalização** | desfecho vigente que inclui na ocupação: aceite ou regularização | o GPS, por ato da seleção |
| **Encaminhado** | registro de entrega, **que esta spec não cria** | ninguém, nesta spec |
| **Matrícula efetivada, bolsa concedida, contrato celebrado** | sistema ou setor do vínculo | **nunca o GPS** |

## Clarifications

### Session 2026-11-03

Decisões do usuário trazidas no pedido, que não se reabrem:

- Q: A funcionalidade é de matrícula? → A: Não. É transversal e opcional, para alunos, bolsistas,
  professores formadores e colaboradores (D-001).
- Q: Quem confere e decide? → A: A seleção, isto é, a comissão do Processo, com o modelo de
  competências existente. Nenhum papel de secretaria ou de conferente sem necessidade demonstrada, e
  sem presumir que todo membro tem as mesmas competências (D-002).
- Q: Quando o documento é pedido? → A: Na inscrição **ou** na convocação, conforme o Edital. O que a
  classificação usa continua na fase da seleção (D-003).
- Q: A conferência tem estados próprios? → A: Não. Ela alimenta os desfechos existentes da `019`
  (D-004).
- Q: O que o aceite afirma? → A: "Apto para formalização", nunca vínculo efetivado. "Encaminhado" só
  com registro de encaminhamento, que esta spec não cria (D-005).
- Q: O GPS guarda o dossiê? → A: Não é GED. Nada de armazenamento permanente, consulta longitudinal ou
  infraestrutura arquivística (D-006).
- Q: Vencimento ou pendência produzem efeito? → A: Nada é automático. Não há indeferimento, perda de
  vaga nem nova convocação sem gesto humano (D-007).

### Session 2026-11-03 (revisão do PR #368)

- Q: Em quais tipos de Edital o documento pode ir para a convocação (QI-2′)? → A: Em qualquer um,
  como recurso opcional por documento, independentemente da natureza do processo.
- Q: A revisão da FR-402 da `029`? → A: Aprovada no texto da D-018, e aplicada.
- Q: Quem confere e quem desfecha (D-010)? → A: Aprovada: presidência e quem tem a autorização atual
  de gerir a comissão conferem e desfecham; o membro alocado só confere; as restrições por Perfil se
  preservam.
- Q: Exigir a abertura antes do "conforme" (D-012)? → A: Aprovada, vinculada ao documento, à versão e
  a quem confere. Abrir uma versão anterior não autoriza conferir a atual.
- Q: O prazo do documento e o do Requerimento podem divergir (D-011)? → A: Não, quando os dois estão
  submetidos à mesma chamada. Alinhar, preservar a conferência depois do vencimento, sem prazo novo e
  sem indeferimento automático. Se a `029` mudar, registrar a revisão e os testes (D-019).
- Q: Uma chamada nova da mesma inscrição exige reenvio (D-013)? → A: Não por padrão. Lista própria e
  histórico próprio, mas aproveitamento por referência do que o GPS já tem na mesma inscrição, sem
  transportar a conferência.

## User Scenarios & Testing *(mandatory)*

Os três primeiros cenários são os **cenários demonstráveis** da Constituição, VI. Todos são de
**vaga imediata**, percorridos pelo portal e pela gestão, sem banco nem shell.

### User Story 1 — Aluno apresenta os documentos de matrícula pelo portal, no molde do 72/2026 (Priority: P1)

O Edital do curso técnico exige a identificação na inscrição. A certidão, o histórico, o certificado
do ensino médio e o comprovante de residência são exigidos **na convocação**. O sorteio classifica
quem tem vaga e quem convoca registra a chamada. A convocada vê no portal, na tela da convocação, o
que apresentar e até quando. Ela envia três dos quatro documentos.

A comissão abre cada um. Marca dois como *conforme* e o histórico como *pendente*, com o motivo
*"histórico sem a página 2"*. A convocada vê a pendência e o motivo, e envia outro arquivo antes do
vencimento. A comissão confere a nova versão como *conforme* e registra o aceite. A tela da gestão
mostra *"Apto para formalização"*.

**Why this priority**: é a lacuna MAT-20, de um Edital composto no próprio GPS que manda o candidato
ao balcão. É o caso de uso imediato.

**Independent Test**: publicar o Edital com quatro Documentos na convocação, inscrever três
candidatos, classificar, convocar um e percorrer o portal e a gestão até o aceite. Conferir que
nenhum dos três foi chamado a enviar os documentos da convocação na inscrição.

**Acceptance Scenarios**:

1. **Given** um Edital com a identidade na inscrição e quatro documentos na convocação, **When**
   alguém se inscreve, **Then** só a identidade é pedida e só ela conta para o envio da inscrição.
2. **Given** a convocação registrada, **When** a convocada abre a tela da convocação, **Then** ela vê
   os quatro documentos com instrução, obrigatoriedade, prazo e o estado *"Falta enviar"*.
3. **Given** um documento enviado, **When** a comissão abre a página de documentos da convocação,
   **Then** vê o item como *"Recebido, aguardando conferência"*, com instante e versão, e o abre no
   navegador.
4. **Given** o histórico marcado como *pendente* com motivo, **When** a convocada abre a tela,
   **Then** vê o motivo e pode enviar outro arquivo até o vencimento. A versão anterior continua
   registrada.
5. **Given** um documento obrigatório ainda sem conferência *conforme*, **When** a comissão tenta
   registrar o aceite, **Then** o aceite é recusado, a recusa nomeia o documento, e nada é gravado.
6. **Given** todos os obrigatórios *conformes*, **When** o aceite é registrado, **Then** a linha
   mostra *"Apto para formalização"* e nenhuma tela desta feature diz "matriculado" ou "encaminhado".

---

### User Story 2 — Bolsista devolve a Ficha/Termo assinada, no molde do 146/2025 (Priority: P1)

O Edital de assistente pedagógico tem uma vaga imediata. A Ficha de Cadastramento/Termo de
Compromisso do Bolsista é Documento Exigido **na convocação**, com o modelo como anexo do Edital.
O selecionado baixa o modelo no portal, preenche, assina, apresenta e é conferido. O aceite é
registrado.

**Why this priority**: demonstra que a capacidade não é de matrícula (D-001) e que o modelo anexo
cobre o formulário da agência sem formulário estruturado novo.

**Independent Test**: o mesmo percurso da US1, com um único documento com modelo anexo. Conferir que
nenhuma tela da gestão ou do portal desta feature afirma bolsa concedida, vínculo ou cadastro na
agência.

**Acceptance Scenarios**:

1. **Given** um Documento na convocação com modelo anexo, **When** o convocado abre a tela da
   convocação, **Then** pode baixar o modelo publicado ali mesmo.
2. **Given** a Ficha apresentada e conferida *conforme*, **When** o aceite é registrado, **Then** a
   gestão mostra *"Apto para formalização"* e o portal mantém a frase atual de que nenhum ato do GPS
   confirma matrícula ou contratação.
3. **Given** um Edital de bolsista **sem** Requerimento de Matrícula, **When** o convocado abre a
   tela, **Then** ela mostra só os documentos, e nada de requerimento.

---

### User Story 3 — O certificado enviado na inscrição atende a convocação sem reenvio, no molde do 89/2026 (Priority: P1)

O Edital tem dois Documentos Exigidos:

- na inscrição, o *Certificado do curso de formação*, **facultativo**, que serve à seleção;
- na convocação, o mesmo certificado, **obrigatório**, que declara aproveitar o da inscrição.

A candidata que o enviou na inscrição é convocada. O item aparece como *"Atendido pelo documento
enviado na inscrição em DD/MM"*, e ela não envia nada. Outro convocado, que não o enviou, vê o item
como *"Falta enviar"*. A comissão confere os dois.

**Why this priority**: é a regra do "sem reenvio" (FR-402 da `029`) fora da matrícula, e o caso que
testa o desenho (§3 do complemento).

**Independent Test**: inscrever dois candidatos, um com e outro sem o certificado. Convocar os dois
e conferir:

- que o item da primeira nasce atendido por **referência** ao arquivo da inscrição, com o mesmo hash
  e sem arquivo novo no armazenamento;
- que o do segundo nasce *"Falta enviar"*.

**Acceptance Scenarios**:

1. **Given** o certificado enviado na inscrição, **When** a convocação é registrada, **Then** o item
   da convocação nasce atendido por referência àquele documento, e nenhum arquivo é copiado.
2. **Given** o item atendido por referência, **When** a comissão o abre, **Then** vê o arquivo da
   inscrição, com a data do envio original, e a entrega reconfere o hash.
3. **Given** o item atendido por referência, **When** a convocada envia outro arquivo, **Then** ele
   vira a versão vigente, e a referência fica como versão anterior.
4. **Given** um convocado sem o certificado na inscrição, **When** a convocação é registrada,
   **Then** o item nasce *"Falta enviar"*.
5. **Given** a seleção, **When** a ordem é calculada, **Then** ela continua lendo só o que a
   inscrição trouxe. Nenhum documento da convocação entra na classificação (FR-3571).

---

### User Story 4 — A complementação acontece até o vencimento, e o que vem depois é decisão de quem conduz (Priority: P1)

A pendência marcada antes do vencimento pode ser complementada pelo portal até o vencimento. Depois
dele, o portal recusa novo envio, diz o prazo e diz que a comissão vai decidir. A comissão continua
podendo conferir o que chegou no prazo e registra o desfecho que couber: aceite, se tudo ficou
conforme; não atendimento, indeferimento com fundamento ou reclassificação, se o Edital assim prevê.

Se a comissão quiser dar mais prazo, corrige a convocação por sucessão, com motivo e novo
vencimento. É o mecanismo que já existe. A lista e as versões apresentadas continuam com a chamada.

Na chamada que também abre o Requerimento de Matrícula, o prazo é um só para os dois. Depois do
vencimento, nem documento nem requerimento se escrevem. Os dois continuam legíveis, e a correção da
convocação reabre os dois juntos (FR-3622).

**Why this priority**: é onde o risco de automatismo e de prazo inventado mora (D-007), e onde o
candidato não pode receber duas respostas diferentes sobre o mesmo prazo.

**Independent Test**: marcar pendência, deixar o vencimento passar, tentar enviar pelo portal,
conferir e desfechar. Repetir com a correção da convocação por sucessão antes do vencimento.

**Acceptance Scenarios**:

1. **Given** a chamada com vencimento decorrido, **When** a convocada tenta enviar, **Then** o envio é
   recusado com o prazo e a frase de que a comissão decide, e nada é gravado.
2. **Given** o vencimento decorrido e pendência não sanada, **When** nenhum gesto acontece, **Then**
   nenhum desfecho, perda de vaga ou nova chamada é produzido, e a convocação continua sem desfecho.
3. **Given** o vencimento decorrido, **When** a comissão registra *indeferimento*, **Then** a tela
   oferece o fundamento pré-redigido com os itens pendentes e seus motivos. O texto é editável e
   continua obrigatório.
4. **Given** a convocação corrigida por sucessão com vencimento novo, **When** a convocada abre a tela,
   **Then** vê o mesmo item pendente, com o prazo novo, e pode complementar.
5. **Given** uma chamada com documentos e com o Requerimento na convocação, e o vencimento decorrido,
   **When** a convocada tenta enviar ou atualizar o requerimento, **Then** o envio é recusado com a
   mesma frase dos documentos. O requerimento continua legível, e o rascunho não se perde.
6. **Given** uma chamada **sem** documento na convocação e com o Requerimento, e o vencimento
   decorrido, **When** a convocada envia o requerimento, **Then** ele é aceito, como hoje (FR-374 da
   `029`).

---

### User Story 5 — Quem confere é a comissão, pela competência que já existe ou pela alocação à conferência (Priority: P1)

A presidência da comissão do Processo, ou quem tem a permissão sistêmica de gerir comissão, confere e
desfecha como hoje desfecha. A presidência pode alocar um membro ativo da comissão **à conferência
dos documentos da convocação** daquele Edital, e opcionalmente restringir a alocação a Perfis. O
membro alocado abre e confere os documentos dos convocados dos Perfis que lhe cabem, mas **não**
registra o desfecho.

O membro só alocado a uma Etapa não vê documento algum da convocação. O auditor vê o estado e a
trilha, mas não abre arquivo. O candidato de outra inscrição recebe a mesma recusa que receberia para
inscrição inexistente.

**Why this priority**: sem isso, ou a comissão inteira vê tudo, contrariando a regra de não presumir
competências iguais (D-002), ou só a presidência trabalha numa chamada de dezenas de pessoas.

**Independent Test**: a matriz de permissões (§ Matriz de permissões), percorrida ator por ator
contra a página de documentos da convocação, a entrega do arquivo, o registro da conferência e o
registro do desfecho.

**Acceptance Scenarios**:

1. **Given** um membro alocado à conferência só do Perfil A, **When** abre a página de um convocado
   do Perfil B, **Then** recebe a recusa de inexistente.
2. **Given** um membro alocado, **When** tenta registrar o aceite, **Then** é recusado, porque o
   desfecho continua com a base atual.
3. **Given** um servidor com papel na unidade e fora da comissão, **When** abre a URL de um documento
   da convocação, **Then** é recusado. Abrir o dossiê da inscrição, pela permissão de consulta de
   inscrição, não leva aos documentos da convocação.
4. **Given** um ator de outra unidade, **When** tenta qualquer dessas rotas, **Then** recebe a recusa
   de inexistente.

---

### User Story 6 — Cada ato deixa rastro com ator e unidade, inclusive abrir o dossiê (Priority: P2)

Apresentar, conferir, alocar, revogar alocação, abrir documento da convocação e abrir o dossiê da
inscrição registram quem, quando, em que unidade e sobre o quê. Nada disso grava o nome original do
arquivo nem o conteúdo do documento. O A-07 fica resolvido.

**Why this priority**: o dossiê passa a concentrar mais dado pessoal, e a auditoria pôs o A-07 como
pré-requisito.

**Independent Test**: percorrer a US1 e conferir na trilha do Edital um registro por ato, com ator e
unidade. Abrir o dossiê de uma inscrição e conferir o registro de consulta.

**Acceptance Scenarios**:

1. **Given** um gestor que abre o dossiê de uma inscrição, **When** a página renderiza, **Then** um
   registro de consulta é gravado com ator, unidade e inscrição, e sem conteúdo do dossiê.
2. **Given** uma conferência registrada, **When** se lê a trilha do Edital, **Then** ela aparece com
   autor, unidade de atuação e instante.

---

### User Story 7 — Quem elabora declara o momento, e o PDF o anuncia numa seção neutra (Priority: P2)

Na elaboração, cada Documento Exigido ganha o campo *"Quando é pedido"* (na inscrição ou na
convocação) e, para os da convocação, *"Atendido pelo documento da inscrição"*, opcional. O PDF do
Edital ganha a seção *"Documentos exigidos na convocação"*, derivada dos dados, sem dizer matrícula,
bolsa ou contratação no título. A seção dos documentos da inscrição passa a listar só os da
inscrição.

**Why this priority**: é o dado de que todo o resto depende, e o PDF é o ato legal (Constituição, II).

**Independent Test**: compor o Edital da US3, publicar e ler o PDF. Conferir as duas seções, o
aproveitamento escrito e a forma publicada. Publicar um Edital sem nenhum documento na convocação e
conferir que o PDF é o de antes.

**Acceptance Scenarios**:

1. **Given** um rascunho sem campo de momento gravado, **When** é lido, **Then** todo documento é da
   inscrição.
2. **Given** um Edital com documentos dos dois momentos, **When** é publicado, **Then** o PDF tem as
   duas seções, e a da convocação diz *"Quem enviou X na inscrição não precisa enviá-lo de novo"*.
3. **Given** um Edital publicado, **When** se abre a Retificação, **Then** os campos retificáveis dos
   documentos da convocação são oferecidos, e o momento e o aproveitamento não.

---

### User Story 8 — A chamada nova aproveita o que a chamada anterior já recebeu (Priority: P2)

O candidato reclassificado é convocado de novo, ou é convocado para regularizar. A chamada nova grava
a sua própria lista. Cada item que a chamada anterior da mesma inscrição já tinha recebido, e cuja
conferência vigente lá não era *pendente*, nasce **aproveitado por referência**, sem arquivo novo. O
estado é *recebido, aguardando conferência*: a conferência anterior não vem junto.

A comissão abre o arquivo e confere de novo. Se o documento venceu ou não serve mais, marca
*pendente*, e o candidato envia outro.

**Why this priority**: não pedir de novo prova que o GPS já tem (Lei 14.129, art. 3º, XIII), sem
transferir deferimento sem análise.

**Independent Test**: convocar, apresentar, conferir e desfechar com reclassificação. Convocar de
novo a mesma inscrição e conferir:
- que os itens aproveitados apontam o mesmo arquivo, com o mesmo hash, e nenhum arquivo novo existe;
- que nenhum está *conforme*;
- que o "conforme" exige abrir o arquivo de novo nesta chamada.

**Acceptance Scenarios**:

1. **Given** um item *conforme* na chamada anterior, **When** a chamada nova é registrada, **Then** o
   item nasce aproveitado por referência, *recebido, aguardando conferência*.
2. **Given** um item *pendente* na chamada anterior, **When** a chamada nova é registrada, **Then** o
   item nasce *a apresentar*.
3. **Given** um item aproveitado, **When** a comissão tenta o "conforme" sem abrir o arquivo nesta
   chamada, **Then** é recusada, mesmo que a mesma pessoa o tenha aberto na anterior.
4. **Given** um item aproveitado cuja exigência foi retificada entre as chamadas, **When** a comissão
   abre a página, **Then** vê a indicação de que a exigência mudou desde a apresentação.
5. **Given** um item aproveitado, **When** o candidato envia outro arquivo, **Then** ele vira a
   apresentação vigente, e a referência fica como anterior.

---

### Edge Cases

Cada caso-limite aponta o requisito que o rege, e entra na rastreabilidade como requisito.

- **Convocação sem exigência documental.** Edital sem documento na convocação, ou convocado a quem
  nenhum se aplica: lista vazia, telas e desfecho como hoje (FR-3574).
- **Convocação registrada antes da feature.** Sem lista retroativa; tratada como sem exigência
  (FR-3575, D-013).
- **Convocação corrigida por sucessão** (vencimento, fundamento). Usa a lista e as apresentações da
  chamada que corrige (FR-3573, D-009).
- **Nova chamada da mesma inscrição** (reclassificado reconvocado, convocação para regularizar). Grava
  lista nova. O que a chamada anterior recebeu e não estava *pendente* é aproveitado por referência,
  sem conferência (FR-3619 a FR-3621, D-013).
- **Item aproveitado entre chamadas, que na anterior era ele mesmo uma referência.** A referência nova
  aponta o arquivo de origem, e nunca outra referência (FR-3619).
- **Item que não existia na chamada anterior** (documento novo por Retificação). Nasce *a
  apresentar*, ou pelo aproveitamento da inscrição, se declarado (FR-3619).
- **Requerimento e documentos na mesma chamada, depois do vencimento.** Os dois se fecham; sem
  documento na chamada, só o requerimento fica aberto, como hoje (FR-3622).
- **Retificação depois da convocação.** Não altera a lista congelada; vale para as chamadas seguintes
  (FR-3573).
- **Envio duplicado.** Mesma requisição repetida, mesmo arquivo de novo ou duplo clique (FR-3581).
- **Arquivo inválido.** Foto, extensão trocada, vazio, acima do limite (FR-3582).
- **Envio depois do vencimento** (FR-3582, FR-3622, D-011).
- **Envio antes do envio da comunicação** (prazo não iniciado). É aceito (FR-3578, D-011).
- **Convocação sem vencimento** (Edital sem prazo publicado e vencimento não informado). O envio é
  aceito enquanto a chamada estiver em aberto (FR-3578).
- **Conferência sobre versão superada.** O candidato enviou outra enquanto o conferente olhava
  (FR-3587).
- **Conferência depois do desfecho** (FR-3588).
- **"Conforme" sem ter aberto o arquivo** (FR-3611, D-012).
- **Obrigatório marcado "não se aplica"** com motivo. Conta como atendido para o aceite (FR-3592).
- **Facultativo apresentado e não conferido.** Adverte e não impede (FR-3592).
- **Documento da inscrição aproveitado e o titular ausente** (inscrição sem o arquivo). O item nasce a
  apresentar (FR-3576).
- **Divergência de hash na entrega** (FR-3605).
- **Membro alocado à conferência e depois inativado na comissão.** Perde o alcance na hora (FR-3597).
- **Edital encerrado com convocação em aberto.** Apresentação e conferência seguem a chamada em
  aberto, como o desfecho segue hoje (FR-3616).
- **Candidato com duas inscrições em Editais distintos.** Cada convocação tem a sua lista; nada se
  aproveita entre Editais (FR-3576).
- **Documento pendente e desfecho de aceite tentado** (FR-3592).
- **Acesso indevido**, por qualquer dos atores da matriz (FR-3595 a FR-3600).

## Requirements *(mandatory)*

### Functional Requirements

#### A. O momento do Documento Exigido (configuração)

- **FR-3563**: Todo Documento Exigido MUST declarar o momento em que é pedido: **na inscrição** ou **na
  convocação**. A ausência do campo, em rascunho ou em forma publicada anterior a esta feature, MUST
  ser lida como "na inscrição". Nenhum Edital existente, rascunho ou publicado, muda de comportamento.
- **FR-3564**: O momento MUST ser declarado na elaboração, gravado no rascunho, levado à forma
  publicada e ao PDF. MUST ter natureza declarada no contrato de mutabilidade (FR-297 da `026`) como
  **não retificável**, com razão normativa: mudar o momento muda a exigência a que o candidato se
  submeteu ao se inscrever. É a mesma razão do momento do Requerimento na `029` (D-014).
- **FR-3565**: O Documento na convocação MUST ter os mesmos atributos e validações do Documento na
  inscrição: nome, instrução, obrigatoriedade, recorte por Perfil, modalidade ou código de modalidade
  transversal (`044`) e modelo anexo. Os atributos retificáveis hoje continuam retificáveis.
- **FR-3566**: Um Documento na convocação MAY declarar **aproveitamento** de um Documento na inscrição
  do mesmo Edital: *"atendido pelo documento X da inscrição, se enviado"*. A validação da publicação
  MUST recusar:
  - aproveitamento que aponte documento da convocação, documento de outro Edital ou o próprio
    documento;
  - mais de um aproveitamento por documento.
  
  O aproveitamento MUST ser publicado e MUST ser não retificável, pela mesma razão da FR-3564 (D-014).
- **FR-3567**: A obrigatoriedade do documento na inscrição e a do documento na convocação MUST ser
  independentes. O caso do 89/2026 (facultativo na inscrição, obrigatório na convocação) é expresso
  por **dois** Documentos Exigidos ligados pelo aproveitamento, e não por um documento com dois
  momentos (D-008).
- **FR-3568**: A lista exigida da inscrição (FR-714 da `044`) MUST conter só documentos da inscrição.
  O documento da convocação:
  - MUST NOT ser pedido na inscrição, nem aparecer nela como "não se aplica";
  - MUST NOT contar para o envio da inscrição;
  - MUST NOT aparecer na Mesa da Etapa (FR-718 da `044`).
- **FR-3569**: O PDF do Edital MUST ganhar uma seção própria e neutra, *"Documentos exigidos na
  convocação"* (no catálogo de seções em forma de pergunta da `069`, a pergunta equivalente). A seção:
  - MUST ser derivada dos dados e só existir quando houver ao menos um documento da convocação;
  - MUST seguir o agrupamento por recorte que já existe;
  - MUST escrever o aproveitamento em linguagem simples;
  - MUST NOT dizer "matrícula", "bolsa", "vinculação" ou "contratação" no título.
  
  A seção atual MUST listar só os documentos da inscrição. Edital já publicado MUST NOT ser
  regenerado.
- **FR-3570**: A Retificação MUST oferecer, para o documento da convocação, os mesmos campos
  retificáveis que oferece para o da inscrição, e MUST NOT oferecer o momento nem o aproveitamento.
  Ela continua sem acrescentar nem remover Documento Exigido, como hoje.
- **FR-3571**: Nada do que a classificação, o desempate, o corte, a Etapa ou a Mesa leem MUST passar a
  ler documento, apresentação ou conferência da convocação (D-003).

#### B. A lista exigida da convocação

- **FR-3572**: Ao registrar a **raiz de uma chamada**, individualmente ou no lote de titulares da
  `050`, o sistema MUST gravar, na mesma transação, a **lista exigida da convocação**. A raiz é a
  convocação que não corrige outra, de qualquer espécie: vaga inicial, suplência ou para regularizar.
  - A lista tem um item por documento da convocação da versão consolidada vigente.
  - Cada item tem situação **obrigatório**, **facultativo** ou **não se aplica** para aquela inscrição,
    pela mesma regra de aplicabilidade da inscrição (Perfil e modalidades da inscrição).
  - Cada item tem identificação estável do requisito e a versão que o fundamentou.
  
  A gravação MUST NOT ter evento de trilha próprio: faz parte do ato da convocação (molde da FR-729 da
  `044`).
- **FR-3573**: A lista MUST ser imutável e MUST pertencer à **chamada**:
  - a convocação que corrige outra por sucessão MUST usar a lista, as apresentações e as conferências
    da chamada que corrige, e MUST NOT gravar outra;
  - a Retificação posterior MUST NOT alterar a lista gravada;
  - cada chamada nova da mesma inscrição MUST gravar a sua lista pela versão então vigente. Ela tem
    histórico próprio de apresentações e conferências, e o que já foi recebido se aproveita por
    referência pela FR-3619 (D-009, D-013).
- **FR-3574**: Sem documento da convocação aplicável, a lista MUST ficar sem itens obrigatórios ou
  facultativos. A tela do portal, a condução e o desfecho MUST se comportar exatamente como antes
  desta feature, sem elemento novo visível.
- **FR-3575**: A convocação registrada antes desta feature MUST NOT ganhar lista retroativa e MUST ser
  tratada como sem exigência documental (D-013).
- **FR-3576**: Quando o item declara aproveitamento e a mesma inscrição tem documento enviado para o
  requisito aproveitado, o item MUST nascer **atendido por referência** àquele documento:
  - MUST NOT haver cópia de arquivo;
  - o hash é o do envio da inscrição;
  - a referência é a primeira apresentação do item, de autoria do ato da convocação.
  
  Sem o documento na inscrição, o item nasce a apresentar. Nada se aproveita entre inscrições nem
  entre Editais. Entre chamadas da mesma inscrição, vale a FR-3619, que tem precedência sobre esta.
- **FR-3619**: Ao gravar a lista de uma chamada nova, o sistema MUST aproveitar **por referência**,
  para cada item obrigatório ou facultativo, a apresentação vigente do mesmo requisito na chamada
  anterior mais recente da mesma inscrição, quando houver uma e a conferência vigente dela lá não for
  *pendente*. A referência:
  - aponta o arquivo de origem: o documento da inscrição, ou a apresentação que guarda o arquivo.
    Nunca aponta outra referência, e nunca copia o arquivo;
  - leva o hash da origem, e é de autoria do ato da convocação.
  
  Item pendente na anterior, ou sem apresentação, ou requisito que não existia, segue a FR-3576.
- **FR-3620**: A conferência da chamada anterior MUST NOT ser transportada. O item aproveitado nasce
  *recebido, aguardando conferência*. A chamada nova só fica *pronta para decidir* depois de conferida
  nela mesma (FR-3592).
- **FR-3621**: A página de documentos da convocação MUST mostrar, no item aproveitado entre chamadas:
  - a chamada e o instante da apresentação de origem;
  - a conferência que ela teve lá, só como leitura;
  - a indicação de que a exigência mudou, quando a versão do item difere da versão em que a origem
    foi apresentada.

#### C. A apresentação pelo portal

- **FR-3577**: O titular da inscrição MUST ver a lista na tela da convocação da `059`, para a
  convocação vigente. Cada item mostra:
  - nome, instrução e obrigatoriedade;
  - o modelo anexo, para baixar, quando houver;
  - o vencimento e o estado (FR-3590).
  
  Os itens que não se aplicam MUST NOT ser mostrados.
- **FR-3578**: O titular MUST poder apresentar um arquivo por item enquanto a chamada estiver **em
  aberto** (convocação vigente sem desfecho) e o vencimento **não tiver decorrido**. Isso inclui a
  convocação cujo prazo ainda não começou a correr e a convocação sem vencimento (D-011). "Decorrido"
  MUST ser lido pela mesma regra que a `019` usa para admitir o não atendimento, e nunca por contagem
  própria. O arquivo MUST passar por:
  - a mesma validação da inscrição: PDF por assinatura e extensão, limite de tamanho e recusa que
    orienta quem mandou foto;
  - o mesmo armazenamento privado e sem URL;
  - nome físico imprevisível, sem o nome original;
  - o mesmo resumo SHA-256.
- **FR-3579**: Cada envio MUST ser uma **apresentação** nova, append-only, numerada no item. A vigente
  é a mais recente. As anteriores continuam legíveis por quem pode conferir. Nada é sobrescrito, nada
  é removível pelo candidato, e o vínculo da apresentação MUST impedir a exclusão do que ela aponta.
- **FR-3580**: O titular MUST poder apresentar arquivo novo para item atendido por referência, da
  inscrição ou de chamada anterior. A referência fica como apresentação anterior.
- **FR-3581**: Envio duplicado MUST NOT produzir apresentação duplicada:
  - a mesma requisição repetida (idempotência) devolve o resultado da primeira;
  - arquivo com o mesmo hash da apresentação vigente do item não cria versão, e responde que o arquivo
    já foi recebido;
  - envios concorrentes para o mesmo item são serializados, e nunca há duas apresentações com o mesmo
    número.
- **FR-3582**: As recusas da apresentação MUST NOT gravar nada:
  - inscrição alheia, chamada sem lista, item que não se aplica ou item de outra convocação MUST
    receber a recusa de inexistente (FR-1101 da `059`);
  - chamada desfechada ou sucedida MUST receber recusa que o diga;
  - vencimento decorrido MUST receber recusa que diz o prazo e que a comissão decide, sem prometer
    reabertura;
  - arquivo inválido MUST receber as mesmas recusas da inscrição.
- **FR-3583**: A inscrição enviada MUST continuar imutável. A apresentação na convocação MUST NOT
  alterar, acrescentar nem substituir documento da inscrição, nem a lista exigida dela. O Requerimento
  de Matrícula MUST NOT mudar nem passar a depender dos documentos da convocação (FR-395 da `029`).
- **FR-3584**: O portal MUST mostrar o resultado da conferência vigente de cada item (conforme,
  pendente com o motivo, não se aplica com o motivo) e MUST NOT mostrar quem conferiu.

#### D. A conferência por documento

- **FR-3585**: Quem pode conferir (FR-3595) MUST poder registrar, por item, uma **conferência**:
  - **conforme**, que exige apresentação;
  - **pendente**, com motivo obrigatório, visível ao candidato;
  - **não se aplica**, com motivo obrigatório.
  
  A conferência MUST citar a apresentação julgada e o hash dela. Item sem apresentação só pode ser
  conferido como pendente ou não se aplica.
- **FR-3586**: A conferência MUST ser append-only. A mais recente do item prevalece, e as anteriores
  continuam legíveis. Uma conferência que substitui outra sobre a **mesma** apresentação MUST exigir
  motivo.
- **FR-3587**: A conferência sobre apresentação que deixou de ser a vigente MUST ser recusada, com a
  indicação de que há versão nova, e nada é gravado.
- **FR-3588**: A conferência MUST ser aceita enquanto a chamada estiver em aberto, inclusive depois do
  vencimento, e MUST ser recusada depois do desfecho.
- **FR-3589**: "Conforme" MUST significar *conforme ao exigido pelo Edital*, nunca *autêntico* ou
  *original*. O arquivo é cópia simples enviada pelo interessado, e nenhuma tela desta feature MUST
  dizer o contrário.
- **FR-3590**: O estado de cada item MUST ser **derivado** das apresentações e conferências, e não
  gravado em coluna. Os estados são:

  | Estado | Quando |
  |---|---|
  | *a apresentar* | nenhuma apresentação |
  | *recebido, aguardando conferência* | apresentação vigente sem conferência |
  | *pendente* | conferência vigente pendente sobre a apresentação vigente |
  | *complementado, aguardando conferência* | conferência pendente sobre apresentação anterior, e apresentação nova |
  | *conforme* | conferência vigente conforme sobre a apresentação vigente |
  | *não se aplica* | conferência vigente não se aplica |

  Não há máquina de estados nem transição gravada (D-004).
- **FR-3591**: O estado documental da convocação MUST ser derivado dos itens:

  | Estado | Quando |
  |---|---|
  | *sem exigência* | nenhum item obrigatório ou facultativo |
  | *aguardando documentação* | algum obrigatório *a apresentar* |
  | *para conferir* | algum item *recebido* ou *complementado* |
  | *com pendência* | algum *pendente* |
  | *pronta para decidir* | todo obrigatório *conforme* ou *não se aplica* |
  | *decidida* | há desfecho vigente |

  Os estados se aferem nesta ordem, e vale o primeiro que se aplicar: *decidida*, *sem exigência*,
  *para conferir*, *com pendência*, *aguardando documentação*, *pronta para decidir*.

#### E. O desfecho

- **FR-3592**: O **aceite** e a **regularização**, os desfechos que incluem na ocupação, MUST ser
  recusados enquanto algum item obrigatório não tiver conferência vigente *conforme* ou *não se
  aplica* sobre a apresentação vigente. A recusa:
  - nomeia os itens;
  - não grava nada;
  - tem código próprio.
  
  Facultativo apresentado e não conferido MUST gerar advertência na tela e MUST NOT impedir.
- **FR-3593**: Os demais desfechos MUST NOT depender do estado documental. As guardas da `019` MUST
  continuar como estão: não atendimento só depois do vencimento, inércia só com atestado, regularização
  só com Resultado sucessor. Nenhum desfecho, perda de vaga, prazo novo ou chamada nova MUST nascer do
  estado documental ou do decurso (D-007; FR-274 da `019`).
- **FR-3594**: Ao registrar **indeferimento** numa convocação com pendência, a tela MUST oferecer o
  fundamento pré-redigido com os itens pendentes e seus motivos. O texto é editável, continua
  obrigatório e é de quem registra.
- **FR-3618**: Dar mais prazo MUST ser feito pela correção da convocação por sucessão, com motivo e
  vencimento novo, que já existe. MUST NOT existir prazo de complementação próprio do item (D-011).
- **FR-3622**: Na chamada em que o Edital declara o Requerimento de Matrícula *na convocação* **e** a
  lista da convocação tem ao menos um item obrigatório ou facultativo, o requerimento MUST seguir o
  mesmo prazo dos documentos:
  - decorrido o vencimento (a mesma leitura da FR-3578), o preenchimento, o envio e o sucessor do
    requerimento MUST ser recusados, com a mesma frase dos documentos;
  - o requerimento MUST continuar legível, e o rascunho MUST NOT ser apagado nem convertido em
    enviado;
  - a correção da convocação por sucessão, com vencimento novo, MUST reabrir os dois juntos;
  - antes de o prazo começar a correr, e na convocação sem vencimento, os dois continuam abertos.
  
  Na chamada **sem** item documental, o requerimento MUST continuar regido pela FR-374 da `029`, sem
  mudança. A regra depende da revisão da FR-374 e da FR-408 da `029` proposta na D-019. A conferência
  continua depois do vencimento (FR-3588), e nenhum desfecho nasce do decurso (FR-3593).

#### F. Autorização

- **FR-3595**: Toda leitura de documento da convocação, entrega de arquivo e registro de conferência
  na gestão MUST passar por um **predicado único**, *pode conferir esta convocação*. Ele é verdadeiro
  para:
  - a base atual do desfecho: a presidência da comissão do Processo, ou a permissão sistêmica de gerir
    comissão;
  - o membro ativo da comissão do Processo **alocado à conferência** daquele Edital, sem restrição ou
    restrito a Perfis que incluem o da convocação.
  
  Em todos os casos, a unidade do Edital é a unidade ativa do ator (D-010).
- **FR-3596**: O registro do desfecho MUST continuar com a base atual. A alocação à conferência MUST
  NOT conceder desfecho.
- **FR-3597**: A alocação à conferência MUST ser registrada por quem tem a base atual, por membro
  ativo, Edital e Perfis opcionais, com autor e instante, no molde da alocação à Etapa. MUST ser
  revogável. O membro inativado na comissão MUST perder o alcance no mesmo instante.
- **FR-3598**: O auditor (permissão de consulta à auditoria) MUST ver, na condução, o estado
  documental e a trilha, e MUST NOT abrir arquivo da convocação. A permissão de consulta de inscrição,
  sozinha, MUST NOT alcançar documento da convocação. A alocação a Etapa, sozinha, MUST NOT alcançar
  documento da convocação (D-015).
- **FR-3599**: Escopo alheio, Edital, convocação, inscrição ou item inexistente, e convocação de Perfil
  fora da alocação MUST receber a mesma recusa de inexistente. Ator no escopo sem nenhuma base MUST
  receber a recusa de autorização do padrão atual.
- **FR-3600**: No portal, só o titular da inscrição MUST alcançar a lista, as apresentações e os
  arquivos dela. Inscrição alheia é indistinguível de inexistente.
- **FR-3601**: Esta feature MUST NOT criar papel no catálogo da unidade, nem capacidade nova concedida
  por padrão a papel existente (D-002).

#### G. Trilha, unidade de atuação e integridade

- **FR-3602**: Cada apresentação, conferência e alocação MUST gravar, na própria linha, ator, instante
  e **unidade de atuação**: a unidade ativa da sessão para o servidor, a unidade do Edital para o
  candidato. Nenhuma coluna, índice ou unicidade MUST presumir que a unidade do ator é a do Edital
  (§7 do complemento). O desfecho continua com a unidade que a trilha já grava (D-017).
- **FR-3603**: A trilha MUST registrar a apresentação, a conferência, a alocação e a revogação, a
  consulta a documento da convocação e a recusa por integridade. Cada registro tem ator, unidade,
  agregado e instante. MUST NOT gravar o nome original do arquivo nem o texto do motivo. Esses atos
  entram na trilha do Edital, entre os atos da condução, e não na trilha da unidade (FR-3159 da `108`).
- **FR-3604**: Abrir o dossiê da inscrição na gestão MUST gravar um registro de consulta, com ator,
  unidade e inscrição, sem conteúdo do dossiê. Resolve o A-07. Abrir a página de documentos de uma
  convocação MUST gravar registro equivalente.
- **FR-3605**: Cada entrega de arquivo da convocação na gestão, apresentado ou referenciado, MUST
  reconferir o hash. A divergência MUST gravar o evento de integridade e recusar a entrega, como a
  entrega da inscrição faz hoje.
- **FR-3606**: A visualização no navegador, sem cache, MUST ser o padrão. Baixar MUST existir só como
  ação secundária individual e registrada. MUST NOT existir download em lote, pacote, ZIP, planilha ou
  exportação de documentos da convocação: a FR-069 da `009` não muda.

#### H. A condução na gestão

- **FR-3607**: A tela de condução da convocação MUST mostrar, por linha, o estado documental (FR-3591),
  as contagens (recebidos, pendentes, complementados, conformes e obrigatórios) e o caminho para os
  documentos daquela convocação. Ela MUST oferecer a ordem *vencimento mais próximo, depois estado*:
  *para conferir*, *complementado*, *com pendência*, *aguardando*, *pronta para decidir*, *decidida*.
  Linha sem exigência MUST aparecer como hoje.
- **FR-3608**: A página **Documentos da convocação**, filha da condução, MUST listar:
  - os itens, com o estado;
  - por item, as apresentações, com versão e instante;
  - a referência aproveitada, com a data do envio na inscrição;
  - as conferências, com autor, unidade, instante e motivo.
  
  Ela MUST permitir abrir cada apresentação e registrar a conferência, e MUST marcar as apresentações
  *abertas por você*.
- **FR-3609**: MUST NOT existir conferência em lote nem "conferir todos". O aceite continua
  individual (FR-881 da `050`).
- **FR-3610**: A linha cujo desfecho vigente inclui na ocupação MUST mostrar *"Apto para
  formalização"*. As telas desta feature MUST NOT dizer *encaminhado*, *matriculado*, *matrícula
  efetivada*, *bolsa concedida*, *vinculado* nem *contratado*.
- **FR-3611**: A conferência *conforme* MUST ser recusada se o próprio conferente não abriu, **nesta
  chamada**, a apresentação vigente daquele item, inclusive a apresentação por referência (D-012). A
  abertura vale só para a apresentação aberta e para quem a abriu. Ela MUST NOT autorizar o "conforme"
  de outra apresentação do mesmo item, nem o da referência ao mesmo arquivo em outra chamada.

#### I. O portal

- **FR-3612**: Os textos do portal MUST seguir a linguagem simples da `069` e caber em 375 px sem rolagem
  horizontal:
  - *"Falta enviar"*;
  - *"Recebido em DD/MM, às HH:MM, aguardando conferência"*;
  - *"Pendente: ‹motivo›. Envie outro arquivo até ‹vencimento›"*;
  - *"Conforme"*;
  - *"Atendido pelo documento enviado na inscrição em DD/MM"*;
  - *"Aproveitado da chamada anterior, enviado em DD/MM. A comissão vai conferir de novo"*;
  - e, depois do vencimento, *"O prazo terminou em ‹vencimento›. A comissão vai decidir."*
  
  Nenhum texto diz matrícula, bolsa ou contratação.
- **FR-3613**: Mostrar a lista e os estados MUST NOT mover prazo nem registrar leitura além da que a
  tela da convocação já registra (FR-1103 da `059`).
- **FR-3614**: Apresentação, conferência e pendência MUST NOT disparar mensagem. A FR-084 da `010`
  continua com quatro situações.

#### J. Limites

- **FR-3615**: Apresentações, referências, conferências e alocações MUST NOT ser excluídas. O arquivo
  apresentado MUST NOT ser removido nesta feature. MUST NOT existir rotina de retenção, descarte ou
  destinação; isso é pendência da QI-4, que bloqueia o uso em produção com dado real.
- **FR-3616**: Esta feature MUST NOT mudar o encerramento da `113`. Em Edital encerrado com convocação
  em aberto, a apresentação e a conferência seguem a chamada em aberto, como o desfecho segue hoje.
- **FR-3617**: MUST NOT existir formulário estruturado de vinculação, requerimento genérico, coleta de
  dados bancários nem desfecho novo. A Ficha/Termo da agência é Documento Exigido com modelo anexo.

### Matriz de permissões

Lida contra as autorizações reais: `pode_gerir_comissao` (`comissoes/domain/autorizacao.py:65-81`),
escopo pelo filtro da consulta (`seguranca/application/authorization.py`) e titularidade
(`inscricoes/domain/titularidade.py`). "Recusa 404" é a recusa de inexistente; "403" é a recusa de
autorização no escopo.

| Ator | Vê estado na condução | Abre arquivo da convocação | Confere | Aloca à conferência | Registra desfecho | Apresenta |
|---|---|---|---|---|---|---|
| Presidência da comissão do Processo | sim | sim | sim | sim | sim | — |
| Permissão sistêmica de gerir comissão (papel Gestor) | sim | sim | sim | sim | sim | — |
| Membro alocado à conferência, sem restrição | sim | sim | sim | não (403) | não (403) | — |
| Membro alocado à conferência do Perfil A, sobre convocação do Perfil B | a linha não aparece | 404 | 404 | 403 | 403 | — |
| Membro só alocado a Etapa | não (recusa atual da condução) | 403 | 403 | 403 | 403 | — |
| Auditor (consulta à auditoria) | sim, só leitura | 403 | 403 | 403 | 403 | — |
| Servidor da unidade sem base (por exemplo, só com consulta de inscrição) | não (recusa atual da condução) | 403 | 403 | 403 | 403 | — |
| Qualquer ator de outra unidade | 404 | 404 | 404 | 404 | 404 | — |
| Titular da inscrição, no portal | os próprios estados | os próprios arquivos | — | — | — | sim, com chamada em aberto e prazo não decorrido |
| Outro candidato, no portal | 404 | 404 | — | — | — | 404 |

A linha do membro alocado, que vê o estado na condução, é o único alcance novo. Ele se limita à
leitura das linhas que a alocação cobre. A regra das recusas é a da FR-3599: objeto fora do alcance
(escopo alheio, inexistente, Perfil fora da alocação) é **404**; ator no escopo sem nenhuma base é
**403**, como a condução já responde hoje.

### Key Entities

- **Documento Exigido** (existe; ganha dois atributos): **momento** (inscrição ou convocação) e
  **aproveitamento** (referência opcional a outro Documento Exigido do mesmo Edital, da inscrição).
- **Item da lista da convocação** (novo, append-only): para uma chamada, um requisito com a situação
  (obrigatório, facultativo, não se aplica), o recorte e a versão que o fundamentou.
- **Apresentação** (nova, append-only): uma versão numerada do item. É **arquivo** (nome físico,
  tamanho, hash, instante) **ou referência**, nunca os dois. A referência aponta um documento da
  inscrição ou a apresentação, de chamada anterior da mesma inscrição, que guarda o arquivo. Tem ator
  e unidade de atuação.
- **Conferência** (nova, append-only): o juízo sobre um item (conforme, pendente, não se aplica), com
  a apresentação julgada e o hash dela, motivo, autor, unidade de atuação, instante e, quando
  substitui outra, motivo da substituição.
- **Alocação à conferência** (nova, no molde da alocação à Etapa): membro ativo, Edital, Perfis
  opcionais, quem alocou, quando, e revogação.
- **Convocação** e **Desfecho** (existem, não mudam de forma): a lista pertence à raiz da chamada; o
  desfecho que inclui ganha a guarda da FR-3592.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1081**: O cenário do aluno (US1) é percorrido de ponta a ponta pelo portal e pela gestão, sem
  banco nem shell: envio, pendência, complementação, conformidade e aceite, terminando em *"Apto para
  formalização"*.
- **SC-1082**: O cenário do bolsista (US2) é percorrido de ponta a ponta. A varredura das telas desta
  feature não encontra nenhum termo da FR-3610.
- **SC-1083**: No cenário do aproveitamento (US3), o item da candidata que enviou o certificado na
  inscrição nasce atendido sem nenhum arquivo novo no armazenamento e com o mesmo hash. O do candidato
  que não o enviou nasce *a apresentar*.
- **SC-1084**: Num Edital com documentos movidos para a convocação, 100% das inscrições são enviadas
  sem esses documentos, e nenhum inscrito não convocado é chamado a apresentá-los.
- **SC-1085**: Nenhum Edital sem documento da convocação muda: as formas publicadas e os PDFs dos
  cenários existentes são idênticos aos de antes, e os testes de inscrição, convocação e desfecho
  passam sem edição de expectativa, salvo contagens nomeadas no plano.
- **SC-1086**: O aceite e a regularização são recusados em 100% dos casos verificados com obrigatório
  não conforme. Com vencimento decorrido e pendência aberta, zero desfechos nascem sem gesto.
- **SC-1087**: Todas as linhas da matriz de permissões são verificadas por teste, e cada recusa é a
  prevista (inexistente ou de autorização).
- **SC-1088**: 100% dos atos da FR-3603 e da FR-3604 deixam registro com ator e unidade, e nenhum grava
  nome original de arquivo nem motivo.
- **SC-1089**: As jornadas dos três cenários passam num navegador de verdade, a 375 px e em desktop,
  sem violação de CSP no console.
- **SC-1090**: As três tabelas append-only novas recusam alteração e exclusão pelas duas camadas
  (gatilho e privilégio ausente). O provisionamento passa a proteger 49 tabelas.
- **SC-1091**: Abrir um documento e registrar a conferência dele, a partir da página de documentos da
  convocação, cabe em três interações, sem sair da página.
- **SC-1092**: Na chamada nova da mesma inscrição (US8), zero arquivos novos são gravados para os
  itens aproveitados, e zero itens nascem *conformes*.
- **SC-1093**: Numa chamada com documentos e Requerimento, depois do vencimento, as duas recusas têm
  a mesma frase em 100% dos casos verificados. Numa chamada sem documento, o comportamento do
  Requerimento é idêntico ao de antes desta feature.

## Assumptions

- O Edital de vaga imediata já se conduz pela `019` e pela `050`: o sorteio ou a classificação, a
  apuração e a convocação existem. Esta spec não depende da `097`.
- O modelo da Ficha/Termo é publicado como anexo do Edital. O *"disponibilizada no momento oportuno"*
  do 146/2025 vira, no GPS, *publicada com o Edital*. O modelo que só existir depois exige Retificação
  que acrescente o anexo.
- A identidade do membro da comissão continua sendo a do provedor (`identity_subject`). O SSO não é
  pré-requisito: a alocação usa o membro, e não um papel novo.
- O sistema não está em produção. Não há convocação real a migrar, e por isso não se cria lista
  retroativa (FR-3575).
- O volume esperado por chamada é de dezenas de convocados e poucos documentos por pessoa. As
  contagens da condução saem de consulta agregada, sem leitura por linha.
- A conferência acontece na unidade do Edital. O multicampi fica fora (MAT-09).

## Proteção de dados (LGPD)

Avaliação exigida pelo princípio III da Constituição.

- **Dado tratado.** Os documentos que o Edital pedia na inscrição passam a ser pedidos só a quem é
  convocado. O dado novo é o motivo da pendência, que é texto da comissão sobre o documento.
- **Necessidade e minimização.** É a medida principal desta feature: coleta só de convocados. O
  documento da convocação não chega à Mesa nem ao avaliador da Etapa (FR-3568, FR-3598), nem a quem só
  consulta inscrições.
- **Finalidade e base legal.** Execução de política pública e cumprimento de atribuição legal (LGPD,
  art. 7º, III; art. 11, II, b; art. 23, I). Nenhum termo de consentimento é pedido pelo sistema. O
  aviso de privacidade do portal continua pendente (A-33).
- **Acesso.** Predicado único, escopo do Edital, titularidade e recusa indistinguível (FR-3595 a
  FR-3600).
- **Registros.** A trilha não grava o nome original do arquivo nem o motivo (FR-3603). O motivo não vai
  a log nem a e-mail.
- **Download.** A visualização é o padrão, o download é individual e registrado, e não há lote
  (FR-3606).
- **Retenção.** Nada é excluído nesta feature, e guardar indefinidamente também é decisão. Por isso a
  QI-4 bloqueia o uso em produção com dado real (FR-3615).

## Compatibilidade e conflitos com regras anteriores

Cada linha nomeia a regra, o conflito e o que esta spec propõe. As revisões de texto de outra spec
são **propostas**: só se aplicam ao arquivo daquela spec depois da aprovação do usuário (tarefa
própria em `tasks.md`).

| Regra | Conflito | Proposta |
|---|---|---|
| **FR-402 da `029`** | A leitura literal ("documento específico de matrícula continua sendo Documento Exigido do Edital"), somada à coleta só no rascunho, impede pedir o documento na convocação. A segunda frase ("MUST NOT criar um segundo acervo") pode ser lida contra a tabela de apresentações | **Revisão de texto (D-018)**: o catálogo continua um só; muda o momento; o apresentado na convocação vai ao mesmo armazenamento, ligado à chamada, e não é segundo acervo; o "sem reenvio" passa a ser o aproveitamento por referência |
| **FR-069 da `009`** | Nenhum: a entrega continua individual, sem lote | **Sem mudança.** A entrega controlada ao setor competente é lacuna futura e exige revisá-la |
| **Exclusões da `009`** ("versões posteriores ao envio"; "substituição de documento pelo candidato após o envio") | Valem para a inscrição, e continuam valendo: esta spec não substitui documento da inscrição. As versões são da convocação | **Sem mudança**; nomeado para que a leitura da exclusão não se estenda à convocação |
| **FR-084 da `010`** | Avisar pendência por e-mail seria a quinta situação | **Sem mudança**; a pendência é estado visível no portal (FR-3614) |
| **FR-395 e FR-400 da `029`** | Nenhum: o requerimento não depende do documento, e a leitura do requerimento continua no dossiê | **Sem mudança** |
| **FR-374 e FR-408 da `029`** | O requerimento continua aberto depois do vencimento, e o documento fecha: duas respostas sobre o mesmo prazo | **Revisão de texto proposta (D-019)**: exceção só na chamada com item documental, pela mesma leitura do prazo da `019` (FR-3622). FR-373 e FR-411 sem mudança |
| **FR-714, FR-715, FR-718 e FR-723 da `044`** | A lista da inscrição passa a excluir os documentos da convocação | Compatível: a regra de aplicabilidade é a mesma, filtrada pelo momento (FR-3568) |
| **FR-297, FR-299 e FR-304 da `026`** | Dois campos novos precisam de natureza; não retificável exige razão normativa | Momento e aproveitamento não retificáveis, com razão (D-014). A conta de campos retificáveis não muda |
| **FR-273, FR-274 e FR-277 da `019`** | O aceite passa a ter guarda nova | Compatível: guarda é recusa, não desfecho; nenhum desfecho novo nem automático (FR-3592, FR-3593) |
| **Decisão da `019` que tira convocação e desfechos do recurso** | Nenhum nesta spec | **Sem mudança**; recurso contra o indeferimento é pendência (QI-6) |
| **FR-881 e FR-887 da `050`** | Nenhum: o aceite continua individual e a autoridade do desfecho não muda | **Sem mudança** |
| **FR-1101 e FR-1103 da `059`** | Nenhum | Seguidas pelas FR-3600 e FR-3613 |
| **FR-3159 da `108`** | Nenhum: os atos novos são da condução | Vão à trilha do Edital (FR-3603) |
| **FR-3534 da `113`** | Nenhum | Convocação em aberto continua só advertência no encerramento (FR-3616) |
| **Constituição, I** (nada se exclui) | Nenhum | FR-3615 |
| **Constituição, III** (negar por padrão) | Um alcance novo: o membro alocado | Explícito, revogável, restrito a Edital e Perfis, sem papel novo (FR-3595 a FR-3601) |
| **Constituição, IV** (ato em lote mostra alcance) | Nenhum lote é criado | FR-3609 |
| **Constituição, V** (necessidade demonstrável) | Cada entidade nova precisa de regra que a consuma | A lista é consumida pela guarda do desfecho; a apresentação, pela conferência; a conferência, pelo desfecho; a alocação, pela D-002 do usuário (não presumir competências iguais). Nenhuma outra |
| **Constituição, VI** (cenário demonstrável) | — | US1, US2 e US3 |
| **Gatilho da `inscricoes/0007`** (recusa documento em inscrição enviada) | Nenhum: a apresentação é outra tabela, e a referência não insere documento da inscrição | Sem mudança no gatilho |
| **MAT-16** (`DocumentoSubmetido` com `CASCADE` para a inscrição) | Se copiado, o documento da convocação seria apagável com a inscrição | As tabelas novas apontam com proteção contra exclusão (FR-3579) |
| **Entrega documental controlada** (segunda spec provável, §10.4 do complemento) | Nenhum agora; o risco era esta spec fechar o caminho dela | Ela vai ler, sem nada novo: os aptos (desfecho que inclui), a apresentação vigente de cada item *conforme*, com requisito, hash, chamada, Edital e Perfil, e o arquivo em um passo (a referência nunca aponta outra referência, FR-3619). Nenhum arquivo duplicado, nada guardado em pacote |

## Decisões

### D-001 — A capacidade é transversal e opcional

**Decisão do usuário (03/11/2026).** Serve a alunos, bolsistas, professores formadores e
colaboradores. Nenhum nome de modelo, permissão, seção ou tela desta feature diz matrícula. O
Requerimento de Matrícula continua acadêmico e não vira genérico.

### D-002 — A seleção confere e decide, pelo modelo de comissão existente

**Decisão do usuário (03/11/2026).** Preserva comissão, competências e autorização. Nenhum papel de
secretaria ou de conferente sem necessidade demonstrada, e sem presumir que todo membro tem as mesmas
competências. A forma concreta é a D-010.

### D-003 — O documento é pedido na inscrição ou na convocação, conforme o Edital

**Decisão do usuário (03/11/2026).** O que a classificação usa continua na fase da seleção. É a
FR-3571.

### D-004 — Nenhuma segunda máquina de estados

**Decisão do usuário (03/11/2026).** A conferência alimenta os desfechos existentes da `019`. O estado
do item e o da convocação são derivados (FR-3590, FR-3591), e a única consequência da conferência é a
guarda do aceite e da regularização (FR-3592).

### D-005 — Aceite é "apto para formalização"

**Decisão do usuário (03/11/2026).** Nunca vínculo efetivado. "Encaminhado" só com registro de
encaminhamento, que esta spec não cria (FR-3610).

### D-006 — O GPS não é GED

**Decisão do usuário (03/11/2026).** Nada de armazenamento permanente, consulta longitudinal ou
infraestrutura arquivística. Esta spec usa o armazenamento que existe e não elimina nada (FR-3615).

### D-007 — Nada automático

**Decisão do usuário (03/11/2026).** Vencimento ou pendência não produz indeferimento, perda de vaga
nem nova convocação (FR-3593).

### D-008 — Dois Documentos Exigidos ligados pelo aproveitamento, e não um documento com dois momentos

*Proposta de desenho.* O caso do 89/2026 poderia ser um documento com dois momentos. Cada exigência,
porém, tem obrigatoriedade, recorte e consequência próprias:

- facultativo na inscrição, porque desempata;
- obrigatório na convocação, porque *"será desclassificado"*.

Além disso, a lista exigida da inscrição já está congelada e não deve ganhar semântica de convocação.
Dois registros com aproveitamento mantêm cada lista com um dono só, e o aproveitamento é explícito no
Edital e no PDF. **Descartado:** aproveitar qualquer documento de mesmo nome por inferência, porque
juntaria finalidades sem ato que o diga.

### D-009 — A lista pertence à chamada, e não à convocação corrigida

*Proposta de desenho.* A correção por sucessão existe para corrigir vencimento e fundamento sem fechar
a chamada (`convocar.py`, sucessão com motivo). Se a sucessora gravasse lista nova, uma Retificação
intermediária mudaria a exigência no meio da chamada, e as apresentações ficariam presas à convocação
anterior. A lista, as apresentações e as conferências se ligam à **raiz** da chamada. A sucessora as
herda por construção, e não por cópia.

### D-010 — Quem confere: a base atual do desfecho, mais a alocação à conferência

**Aprovada pelo usuário na revisão do PR (03/11/2026)**, com a restrição por Perfil preservada. O
alocado confere e não desfecha. Hoje só há duas bases na comissão:

- a de gestão (presidência e `comissao:gerir`), que conduz e desfecha;
- a alocação à Etapa, que dá à Mesa e a nada mais.

Três alternativas foram pesadas:

| Opção | Contra |
|---|---|
| Só a base atual confere | numa chamada de dezenas de pessoas, só a presidência trabalha; não separa conferir de desfechar |
| Todo membro ativo confere | presume competências iguais, contra a D-002 |
| **Base atual + alocação à conferência, com Perfis opcionais (recomendada)** | uma peça a mais, no molde de uma que já existe |

A alocação:

- separa *conferir* de *desfechar* desde já. Juntá-las e separá-las depois exigiria migrar autorizações
  concedidas;
- admite restrição por Perfil, a mesma peça que o multiunidade vai usar (§7 do complemento);
- é da comissão, e não papel na unidade. Atende à §10.2 ("quem confere é a comissão do Processo").

O alocado **não** desfecha: é a decisão do usuário, e fecha a QI-1′ no que é do GPS.

### D-011 — Um prazo só para a chamada: documentos e Requerimento fecham juntos, e a conferência continua

**Ajustada a pedido do usuário (03/11/2026).** A primeira versão fechava o documento no vencimento e
deixava o Requerimento aberto, pela FR-374 da `029`. Na mesma tela da convocação, o candidato
receberia duas respostas sobre o mesmo prazo.

**O que a FR-374 protegia, e por que o alinhamento não o contraria.** O argumento da `029` é que
*"duas contagens do mesmo prazo divergiriam"*. Em setembro, a convocação tinha uma leitura só do
prazo: a que admite o não atendimento (`convocacao/domain/prazo.py`, `decorrido`), que só conta
depois do envio da comunicação. O alinhamento usa **essa** leitura, para documentos e Requerimento.
Não há segunda contagem.

**O alcance é o da chamada que submete os dois ao mesmo prazo**, isto é, a que tem Requerimento *na
convocação* e ao menos um item documental. Na chamada sem documento, o Requerimento continua aberto
depois do vencimento, como hoje. É o limite do pedido ("Editais sem documento na convocação mantêm o
comportamento atual"). Estender a regra a todo Requerimento *na convocação* é decisão própria, e fica
registrada (§ Pendências).

**O que continua:**
- a conferência depois do vencimento, porque a comissão julga o que chegou no prazo (FR-3588);
- a exceção fundamentada, pela correção da convocação por sucessão com vencimento novo, que reabre os
  dois (FR-3618, FR-3622);
- nenhum prazo novo e nenhum desfecho pelo decurso (FR-3593).

**Alternativa descartada: aceitar documentos depois do vencimento**, como o Requerimento, e deixar a
tempestividade à comissão. Seria o alinhamento sem revisar a `029`. Mas o sistema daria recibo de
entrega a quem o Edital diz que perde a vaga (*"será desclassificado"*, 89/2026, 11.2; *"será
reclassificado"*, 72/2026, item 8). A disputa do "o sistema aceitou" cairia sobre a comissão.

### D-012 — "Conforme" exige ter aberto o arquivo

**Aprovada pelo usuário na revisão do PR (03/11/2026)**, vinculada ao documento, à versão e a quem
confere. A abertura de uma versão anterior, ou de outra chamada, não autoriza o "conforme" da atual
(FR-3611).

A auditoria (§L) aponta a avaliação em massa sem conferência como o risco a
evitar. O padrão da Mesa ("1 de 2 abertos por você") já existe. Exigir a abertura pela própria pessoa,
registrada na trilha, faz o "conforme" significar juízo sobre o arquivo. Pendente e não se aplica não
exigem abertura: o documento pode nem ter sido apresentado.

### D-013 — Nenhuma lista retroativa; a chamada nova aproveita por referência, e confere de novo

**A primeira parte é proposta de desenho; a segunda foi ajustada a pedido do usuário (03/11/2026).**

**Sem lista retroativa.** O sistema não está em produção, que é a mesma razão da decisão sobre atos
anteriores da `114` (FR-3575).

**Entre chamadas da mesma inscrição**, a primeira versão pedia tudo de novo, o que contraria a vedação
de exigir prova de fato já comprovado (Lei 14.129, art. 3º, XIII). A versão ajustada separa três
coisas que a primeira juntava:

| O quê | Entre chamadas | Por quê |
|---|---|---|
| A lista | própria de cada chamada (FR-3573) | a exigência é a da versão vigente na chamada nova |
| O arquivo | aproveitado por referência, sem cópia (FR-3619) | identidade e integridade: o hash é o da origem |
| A conferência | **não** se transporta (FR-3620) | a decisão é de cada chamada; o documento pode ter vencido, ou a exigência mudado |

O item *pendente* na anterior não se aproveita: aproveitá-lo seria pedir à comissão que julgasse de
novo o que ela já disse que não serve. A referência aponta sempre o arquivo de origem, e nunca outra
referência. Assim a rastreabilidade não vira corrente, e a futura entrega encontra o arquivo num passo.

**Alternativa descartada: oferecer o aproveitamento como escolha do candidato** ("usar o documento da
chamada anterior"). Daria mais um gesto a quem já apresentou. O aproveitamento automático é
favorável, não decide nada, e o candidato continua podendo enviar outro (FR-3580).

### D-014 — Momento e aproveitamento não são retificáveis

*Proposta de desenho.* Mover um documento da inscrição para a convocação, ou criar aproveitamento,
depois da publicação, muda a quem e quando a exigência se aplica a candidatos que já se inscreveram
sob outra regra. É a razão que a `029` deu para o momento do Requerimento. O que continua
retificável (nome, instrução, obrigatoriedade, recorte, modelo) chega às chamadas seguintes, e não às
listas já gravadas.

### D-015 — Quem não pode conferir não abre o arquivo da convocação

*Proposta de desenho.* A §10.5 do complemento registra que o Gestor lê o dossiê de qualquer inscrito
da unidade sem prazo, e que o acesso amplo deixou de ter justificativa de "acervo". Esta spec não
mexe nesse acesso (não é dela), mas não o estende: o documento da convocação só se abre pelo
predicado da FR-3595. O auditor fiscaliza pelo estado e pela trilha. Abrir o arquivo pelo auditor
fica como pendência, se o controle o pedir.

### D-016 — MAT-08: sem varredura de malware nesta spec

*Proposta de desenho, sem ampliar o escopo.* O risco cresce, porque a comissão passa a abrir PDFs de
convocados como rotina. Esta spec mantém as defesas atuais:

- assinatura PDF e limite de tamanho;
- entrega inline, com `Content-Type` fixo e sem cache;
- CSP restritiva;
- nome físico imprevisível.

A decisão entre varredura no envio e visualização rasterizada no servidor é **da TI**, e, como a
QI-4, bloqueia o uso em produção com dado real, mas não a implementação.

### D-017 — A unidade de atuação nas linhas novas; o desfecho pela trilha que já existe

*Proposta de desenho.* O §7 do complemento pede a unidade em cada ato. Nas três tabelas novas e na
alocação, ela vai na linha (FR-3602). No desfecho, a trilha já grava o escopo do ator
(`RegistroAuditoria.institution_scope`). Acrescentar coluna à tabela append-only do desfecho seria
mudança de forma de um ato da `019` sem regra que a consuma agora.

### D-018 — Revisão da FR-402 da `029`

**Aprovada pelo usuário na revisão do PR (03/11/2026), e aplicada** em
`specs/029-requerimento-de-matricula/spec.md`, com a marca "revisada pela `115`" e a redação anterior
preservada, como na revisão da FR-084. O texto:

> **FR-402** (revisada pela `115`): Esta feature MUST NOT pedir reenvio de documento que a Inscrição
> já recebeu, e MUST NOT criar um segundo acervo de documentos. Documento específico de matrícula
> continua sendo Documento Exigido do Edital: do mesmo catálogo, exigível **na inscrição ou na
> convocação** (`115`). O apresentado na convocação vai ao mesmo armazenamento, ligado à chamada, e o
> já enviado na inscrição é aproveitado **por referência**, sem cópia.

O teste que prende a FR-402 (`test_convivencia_com_o_anexo.py`) continua válido como está: ele
proíbe arquivo no Requerimento, e não no Edital.

### D-019 — Texto proposto para a revisão da FR-374 e da FR-408 da `029`

**Proposta, pedida pelo usuário na D-011 ajustada, e não aplicada.** O único texto desta spec que ainda
pede aprovação explícita. Redação sugerida, para aplicar na `029` com a marca "revisada pela `115`" e
a redação anterior preservada:

> **FR-374** (revisada pela `115`): **Do prazo, e só dele.** O vencimento do prazo da convocação MUST
> NOT, por si, encerrar o preenchimento, fechar a leitura nem apagar o que houver: quem decide a
> consequência do prazo é a convocação, e duas contagens do mesmo prazo divergiriam. Chamada vencida
> **sem** desfecho continua em aberto; o que a encerra é o desfecho, cujo efeito a FR-411 descreve.
> **Exceção, da `115`:** na chamada cuja lista da convocação tem item documental, o requerimento e os
> documentos têm um prazo só. Decorrido o vencimento, pela mesma leitura que admite o não atendimento,
> o preenchimento, o envio e o sucessor se encerram; a leitura e o rascunho se preservam; e a
> correção da convocação com vencimento novo os reabre (FR-3622).
>
> **FR-408** (revisada pela `115`): Um requerimento sucessor MUST ser admitido somente quando existir
> chamada em aberto para aquela Inscrição, **e, na chamada da exceção da FR-374, com o vencimento não
> decorrido**, e MUST citar a convocação que o autorizou. Fora disso, MUST ser recusado.

**Testes que a revisão pede** (tarefas T052 a T054):
- a política de disponibilidade (`requerimentos/domain/disponibilidade.py`) com e sem item documental,
  antes e depois do vencimento, com prazo não iniciado e sem vencimento;
- o envio e o sucessor recusados na exceção, e aceitos sem ela;
- a frase única no portal;
- a correção da convocação reabrindo os dois.

O teste da FR-402 (`test_convivencia_com_o_anexo.py`) não muda.

## Pendências do usuário

Revistas em 03/11/2026, depois das decisões do usuário sobre o PR.

**Para aprovar a spec (o merge deste PR):**

1. **D-019**: o texto da revisão da FR-374 e da FR-408 da `029`. Pode ser aprovado com o merge, ou
   destacado num PR próprio, se o usuário preferir.

**Resolvidas na revisão do PR:** a QI-2′ (opcional por documento, em qualquer Edital), a FR-402
(D-018, aplicada), a D-010, a D-011 (ajustada), a D-012 e a D-013 (ajustada).

**Registradas, sem bloquear a implementação:**

2. **Estender o prazo único (D-011) a todo Requerimento *na convocação***, inclusive na chamada sem
   documento. Hoje fica como a FR-374 da `029` manda.
3. **MAT-18**: o rótulo *"Cancelamento de matrícula por inércia"*, oferecido a qualquer Edital. Esta
   spec não o muda. A decisão (rótulo neutro ou restrição a Editais com Requerimento de Matrícula) é
   do usuário.
4. **MAT-09**: escopo entre unidades. Os Perfis do 89 e do 90/2026 são do Campus de Alegre. Esta spec
   grava a unidade de atuação e passa a autorização por um predicado só, sem mudar a doutrina de
   *escopo alheio = recusa de inexistente*.
5. **D-015**: o auditor abre ou não o arquivo da convocação.
6. **Entrega documental controlada** (segunda spec provável), que depende de revisar a FR-069 da
   `009`.
7. **QI-6**: recurso contra o indeferimento.
8. **QI-7**: aviso de pendência por e-mail, que revisaria a FR-084 da `010`.

**Antes do uso em produção com dado real (não da spec):**

9. **QI-3**: quais documentos são exigíveis (Procuradoria).
10. **QI-4**: guarda e destinação do que o certame conserva.
11. **MAT-08**: varredura de PDF (TI), D-016.
