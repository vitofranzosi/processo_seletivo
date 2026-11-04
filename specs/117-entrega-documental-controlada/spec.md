# Feature Specification: Entrega documental controlada ao setor da formalização

**Feature Branch**: `claude/gps-entrega-documental-627460`, sobre a `main` em `83cd5863`

**Created**: 2026-11-04 · **Revista**: 2026-11-04, com a revisão final do usuário

**Status**: **Pronta para aprovação.** Nenhum código, migration ou tela foi alterado. Nenhuma regra de
outra spec foi mudada: as revisões da FR-069 da `009` e da FR-3606 da `115` estão **propostas**
(D-016), e não aplicadas. A situação das decisões:

- **Do usuário, aprovadas como premissas:** D-001 a D-006.
- **Propostas revistas a pedido do usuário em 04/11:** D-007 a D-022. As que bloqueiam a implementação
  estão em *Pendências do usuário*.

**O que mudou na revisão**, em relação à primeira versão desta spec:

- **Documentos.** A marca *segue para a formalização* no Documento Exigido da convocação, publicada no
  PDF e retificável, foi trocada por uma **definição interna por Edital**. Ela cobre requisitos de
  qualquer momento e fica fora do conteúdo publicado (D-009 a D-012).
- **Acesso.** O papel e a designação passam a ser concedidos **os dois pela gestão de acessos** da
  `107`, e não pela presidência da comissão (D-013).
- **Exportação.** Há três alcances: por pessoa, por seleção e por recorte autorizado. Nenhum "pacote
  do Edital" (D-014).
- **Rastreabilidade.** Saem *"obtida"* e as quatro situações derivadas. O GPS afirma só o que viu:
  *visualizado*, *download disponibilizado*, *pacote gerado e disponibilizado* (D-015, D-017).
- **Limite.** É derivado da infraestrutura de produção, com concorrência limitada (D-019).

**Depende de**: a implementação da `115` (PR vitofranzosi/processo_seletivo#369), **ainda não
mergeada** em 04/11. A sessão de implementação começa conferindo esse merge, e para se ele não
estiver na `main`.

**Input**: o pedido do usuário de 04/11/2026 e a revisão final dele, no mesmo dia; a §10.4 do
[complemento da auditoria de matrícula e dossiê](../../doc/auditoria-matricula-e-dossie-documental-2026-11-03-complemento.md);
e o [diagnóstico desta feature](diagnostico.md), com as referências ao código, as alternativas e a
base do limite.

> **Faixa de identificadores.** Esta spec abre em **FR-3653** e **SC-1101**. O teto foi medido em
> 04/11/2026 em `specs/*/spec.md` de todas as worktrees desta máquina e de todas as branches remotas:
> o requisito funcional três mil seiscentos e cinquenta e dois e o critério mil e cem, os dois da
> `116`, no PR #370 sem merge. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-069 da `009`"). Uma decisão de outra feature é citada pelo assunto e pela feature. Os
> achados e questões das auditorias (`MAT-NN`, `QI-N`) são citados como estão nos documentos de
> origem.

---

## Por que esta feature existe

A `115` completa a convocação: o GPS passa a saber quem está **apto para formalização**. **Falta a
passagem ao setor que formaliza**: secretaria acadêmica, Registro Acadêmico, Coordenação UAB,
coordenação de curso ou outro. Hoje:

- **O setor não tem acesso legítimo.** O único caminho até o arquivo da convocação é o predicado de
  quem **confere** (FR-3595 da `115`). Dá-lo ao setor seria dar competência de seleção.
- **O esforço é proporcional ao número de arquivos.** São cerca de 680 gestos para 40 aptos com 5
  documentos cada (§2.10 do diagnóstico). O arquivo baixado tem o nome que o candidato escolheu.
- **O lote é proibido** pela FR-069 da `009` e pela FR-3606 da `115`.
- **Nada distingue** o documento que serve só à seleção do que o setor precisa.
- **Nada registra** o que foi disponibilizado ao setor.
- **Arquivo ausente vira erro 500 sem registro**, na inscrição e na convocação (§2.9 do diagnóstico).

Sem resposta a isso, alguém da comissão baixa tudo e monta a pasta compartilhada, o circuito que a
`009` quis eliminar.

### O que esta spec cobre

- **A.** A **definição dos documentos para a formalização**, por Edital, pela condução do processo.
- **B.** O acesso do setor: o papel **Formalização** e a **designação** por Edital com Perfis
  opcionais, os dois concedidos e revogados pela gestão de acessos.
- **C.** A página **Documentos para formalização**: os aptos do alcance, a visualização e o download
  individuais registrados.
- **D.** A **exportação controlada**: por pessoa, por seleção ou por recorte. É um ZIP com manifesto,
  prévia, confirmação e limite, num temporário sem nome, nunca guardado.
- **E.** O **registro da exportação** e a trilha.
- **F.** O tratamento de arquivo indisponível e divergente, sem erro 500.

### O que fica fora

- GED, acervo, guarda prolongada, destinação ou descarte (D-001; QI-4 da auditoria).
- Encaminhamento ativo, integração com SIGAA, SIPAC, CAPES ou outro sistema (Alternativa D do
  diagnóstico).
- Confirmação de recebimento (D-021).
- Assinatura digital, protocolo institucional, motor de transferência.
- Exportação de quem não está apto, de documento fora da definição ou de vários Editais.
- Competência nova para o setor: conferir, desfechar, corrigir, ler a inscrição.
- Mudança na conferência, nos desfechos ou no portal da `115`.
- Escopo entre unidades (MAT-09).
- O acesso amplo do papel Gestor ao dossiê de inscrição (§10.5 do complemento).
- **Fica para depois** (§ *MVP e o que fica para depois*): aviso de quem deixou de estar apto depois
  de exportado, geração assíncrona, definição por setor dentro do mesmo Edital.

### Três estados, três fontes

| Termo | Fonte | Quem afirma |
|---|---|---|
| **Apto para formalização** | desfecho vigente que inclui (aceite ou regularização) | o GPS, pelo ato da seleção |
| **Disponibilizado ao setor** | evento ou registro da exportação | o GPS, pelo ato do servidor com acesso |
| **Matrícula efetivada, bolsa concedida, contrato celebrado** | sistema ou setor do vínculo | **nunca o GPS** |

## Clarifications

### Session 2026-11-04

- Q: O GPS guarda o que o setor baixou? → A: Não. Não é GED (D-001).
- Q: O setor pode conferir ou mudar desfecho? → A: Não (D-002).
- Q: Disponibilizar é efetivar o vínculo? → A: Não (D-003).
- Q: O pacote é cópia guardada? → A: Não (D-004).
- Q: O setor recebe tudo o que o candidato enviou? → A: Não. Só o definido para a formalização (D-005).
- Q: Multiunidade? → A: Não fechar o caminho, sem implementar o multicampi (D-006).

### Session 2026-11-04 (revisão final)

- Q: A marca de finalidade fica no Documento Exigido da convocação? → A: Não. Ela é uma definição
  interna por Edital, sobre requisitos de qualquer momento, fora do conteúdo publicado (D-009).
- Q: Mudar a definição exige Retificação ou constar do PDF? → A: Não, porque não muda obrigação do
  candidato. Retificação só se o setor precisar de documento que o Edital não exigiu (D-012).
- Q: Quem concede o acesso do setor? → A: A gestão de acessos (`acesso:gerir`): o papel e a
  designação. A presidência não concede (D-013).
- Q: Existe pacote do Edital inteiro? → A: Não. Há pacote por pessoa, por seleção e por recorte
  autorizado, sempre dentro do alcance do destinatário (D-014).
- Q: O GPS diz "obtido", "encaminhado" ou "recebido"? → A: Não. Só *visualizado*, *download
  disponibilizado* e *pacote gerado e disponibilizado* (D-015).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A condução define quais documentos vão para a formalização (Priority: P1)

Na condução do Edital 72/2026, a presidência abre **Documentos para a formalização** e marca, entre os
requisitos do Edital:

- identidade, CPF e histórico, da convocação;
- o certificado, enviado na inscrição.

Não marca a comprovação de renda (reserva de vagas) nem os títulos (classificação). Ao marcar a renda
por engano, a tela avisa que o documento é exigido só de modalidade de reserva. Ela grava com motivo.

**Why this priority**: é a minimização (D-005). Sem a definição, nada sai.

**Independent Test**: definir num Edital com documentos da inscrição e da convocação, e conferir a
versão gravada e a trilha.

**Acceptance Scenarios**:

1. **Given** um Edital sem definição, **When** qualquer exportação é pedida, **Then** nenhum documento
   está disponível e a página explica por quê.
2. **Given** um requisito com recorte por modalidade, **When** ele é marcado, **Then** a tela mostra o
   aviso, e a gravação continua possível.
3. **Given** uma definição vigente, **When** a presidência grava outra, **Then** a anterior continua
   registrada, a nova vale para as exportações seguintes, e as exportações passadas continuam
   apontando a versão que aplicaram.
4. **Given** a definição gravada, **When** se compara o snapshot, o hash e o PDF do Edital, **Then**
   nada mudou.
5. **Given** o servidor do setor, **When** tenta gravar a definição, **Then** recebe a recusa de
   autorização.

---

### User Story 2 — A gestão de acessos concede ao setor o papel e o Edital (Priority: P1)

O administrador de acessos da unidade concede o papel **Formalização** a Rui, do Registro Acadêmico, e
o designa para o Edital 72/2026. Concede o mesmo papel a Bia, da Coordenação UAB, e a designa para o
146/2025, só no Perfil de tutor. Rui não integra a comissão.

**Why this priority**: é a chave do acesso.

**Independent Test**: conceder, designar, revogar a designação, revogar o papel e suspender a pessoa,
conferindo a página depois de cada passo.

**Acceptance Scenarios**:

1. **Given** Rui com o papel e sem designação, **When** abre a página de um Edital, **Then** recebe a
   recusa de inexistente. A lista de Editais dele está vazia.
2. **Given** a designação de quem não tem o papel, **When** gravada, **Then** é recusada com código
   próprio.
3. **Given** o administrador de acessos, **When** tenta se designar, **Then** é recusado, como na
   autoconcessão da `107`.
4. **Given** a presidência da comissão, **When** tenta designar, **Then** recebe a recusa de
   autorização. Ela vê as designações vigentes do Edital, só para leitura.
5. **Given** Bia, designada só no Perfil de tutor, **When** abre o 146/2025 e depois tenta a URL de
   documento de pessoa de outro Perfil, **Then** vê só os tutores e recebe a recusa de inexistente na
   URL.
6. **Given** Rui designado em três Editais, **When** o papel é revogado, **Then** a próxima requisição
   é recusada nos três, sem revogar as designações uma a uma.
7. **Given** membro alocado à conferência, **When** abre a página da formalização, **Then** recebe a
   recusa. O contrário também vale.

---

### User Story 3 — O setor consulta os documentos dos aptos (Priority: P1)

Rui abre **Formalização** na barra e depois o 72/2026. Vê os aptos por Perfil e, por pessoa, os
documentos definidos para a formalização, com a última exportação de cada um. Visualiza no navegador
ou baixa um a um. No bolsista do 146/2025 (Cenário B), isso basta.

**Why this priority**: resolve o acesso e a minimização, e serve sozinha aos processos pequenos.

**Independent Test**: um Edital com um aceite e dois documentos definidos. Visualizar e baixar, e
conferir a trilha.

**Acceptance Scenarios**:

1. **Given** 3 aceites, 1 indeferimento e 1 sem resposta, **When** Rui abre a página, **Then** vê os 3
   aceites.
2. **Given** uma pessoa com documentos da inscrição e da convocação, dentro e fora da definição,
   **When** Rui a vê, **Then** só os definidos aparecem.
3. **Given** o certificado da inscrição definido, e aproveitado por referência num item da convocação
   também definido, **When** Rui vê a pessoa, **Then** o arquivo aparece uma vez.
4. **Given** um documento, **When** Rui visualiza e depois baixa, **Then** a trilha tem *documento
   visualizado* e *download individual disponibilizado*, sem nome de arquivo nem de pessoa.
5. **Given** a página, **When** a tela tem 375 px, **Then** cabe sem rolagem horizontal.

---

### User Story 4 — O setor exporta por pessoa, por seleção ou pelo recorte autorizado (Priority: P1)

Rui tem 40 aptos no 72/2026 (Cenário A):

1. marca **Selecionar todos** e pede **Exportar selecionados**;
2. a prévia diz o alcance: 40 pessoas, 200 documentos, nenhum arquivo ausente e 290 MB;
3. ele confirma e recebe um ZIP com uma pasta por pessoa e o manifesto.

Na semana seguinte, quem chegou por regularização sai com **Exportar esta pessoa**, num clique.

**Why this priority**: é o que tira o setor da pasta de rede montada à mão, e o que exige a exceção à
FR-069 da `009`.

**Independent Test**: 40 aptos com 5 documentos cada. O pacote tem 40 pastas e 200 arquivos, o
manifesto confere com os hashes, e o registro guarda o hash do pacote. Nada sobra no disco.

**Acceptance Scenarios**:

1. **Given** uma seleção de mais de uma pessoa, **When** Rui pede a exportação, **Then** vê a prévia,
   que não grava nada além da trilha de consulta:
   - o alcance (Edital e Perfis);
   - as pessoas e os documentos de cada uma;
   - os **arquivos ausentes**;
   - o tamanho, total e por pessoa.
2. **Given** a prévia, **When** um desfecho muda antes da confirmação, **Then** a confirmação é
   recusada como prévia defasada, sem gerar nada.
3. **Given** uma pessoa, **When** Rui pede a exportação dela, **Then** a confirmação é um clique, sobre
   a lista de documentos dela.
4. **Given** o recorte *Perfil A*, **When** Rui exporta todos do recorte, **Then** só os aptos do
   Perfil A entram.
5. **Given** uma seleção que inclui id de pessoa fora do alcance, enviada por POST forjado, **When** a
   exportação é pedida, **Then** é recusada inteira como inexistente.
6. **Given** uma exportação de Rui em andamento, **When** Rui pede outra, **Then** a segunda é recusada
   com *"Uma exportação sua já está sendo gerada"*.

---

### User Story 5 — O GPS não declara sucesso que não houve (Priority: P1)

Um arquivo some do disco, ou o hash não confere (Cenário F).

**Why this priority**: declarar disponibilizado o que não foi é o risco que o registro existe para
evitar.

**Independent Test**: num pacote de 5 pessoas, apagar o arquivo de uma e corromper o de outra.

**Acceptance Scenarios**:

1. **Given** uma pessoa com arquivo ausente, **When** o pacote é gerado, **Then**:
   - ela fica **inteira** fora;
   - o manifesto, o registro e a tela a nomeiam como *"não incluída: arquivo indisponível"*;
   - o resultado é **parcial**.
2. **Given** um hash divergente, **When** o pacote é gerado, **Then** a pessoa fica fora como *"não
   incluída: integridade"*, e a trilha grava o evento de integridade.
3. **Given** todas as pessoas com falha, **When** o pacote é gerado, **Then** nada é servido, e o
   registro grava o resultado *sem pacote*.
4. **Given** um arquivo ausente, **When** visualizado ou baixado, nesta página ou nas páginas
   existentes da inscrição e da convocação, **Then** a resposta é *"Arquivo indisponível"* e não 500,
   e a trilha registra.
5. **Given** a seleção acima do limite, **When** confirmada, **Then** é recusada antes de ler qualquer
   arquivo, com a orientação de dividir a seleção.

---

### Edge Cases

- **Desfecho corrigido entre a prévia e a confirmação.** A assinatura muda, e a confirmação é recusada
  (FR-3689).
- **Duas chamadas da mesma inscrição.** Vale a mais recente. O aproveitamento entre chamadas é
  resolvido no arquivo de origem (FR-3670).
- **Item da convocação definido, mas *não se aplica* ou facultativo não apresentado.** Não há arquivo.
  O manifesto diz, e a pessoa conta como completa (FR-3672).
- **Documento da convocação apresentado e não conferido.** Não sai, e aparece como *"não conferido"*
  (FR-3671).
- **Documento da inscrição definido que o candidato não enviou** (facultativo, ou fora do recorte).
  Aparece como *"não apresentado"* (FR-3672).
- **Definição alterada depois de uma exportação.** A exportação passada continua com a versão que
  aplicou. A seguinte usa a nova, inclusive para pessoas de chamadas anteriores (FR-3656).
- **Edital encerrado (`113`).** A página e a exportação seguem o desfecho vigente (FR-3710).
- **Convocação anterior à `115`, sem lista.** Só os documentos da inscrição definidos aparecem
  (FR-3670).
- **Mesma pessoa na comissão e no setor**, numa equipe de duas ou três pessoas. É permitido, com
  acessos independentes, cada um pelo seu predicado (FR-3664).
- **Nome com caracteres que o sistema de arquivos recusa.** É normalizado, e o protocolo garante a
  unicidade (FR-3686).

## Requirements *(mandatory)*

### Functional Requirements

#### A. A definição dos documentos para a formalização

- **FR-3653**: Cada Edital MUST ter uma **definição dos documentos para a formalização**: um conjunto de
  requisitos do próprio Edital, **de qualquer momento** (inscrição ou convocação), **vazio por
  padrão**. Nenhum documento MUST ficar disponível ao setor se o requisito dele não estiver na
  definição vigente.
- **FR-3654**: A definição MUST ser gravada pela base de gerir a comissão do Processo do Edital (a
  presidência, ou a permissão sistêmica de gerir comissão), na unidade do Edital. Quem tem só o acesso
  da formalização MUST NOT gravá-la: o destinatário não escolhe o que recebe.
- **FR-3655**: A definição MUST ser append-only e versionada. Cada versão tem os requisitos, o motivo,
  o autor, a unidade de atuação e o instante. A vigente é a mais recente. Cada exportação MUST gravar a
  versão que aplicou.
- **FR-3656**: Uma versão nova MUST valer para toda consulta e exportação **seguinte**, inclusive de
  pessoas de chamadas anteriores, e MUST NOT alterar o registro de exportações passadas.
- **FR-3657**: A definição MUST NOT ser conteúdo publicado: não entra no snapshot, no hash canônico nem
  no PDF, e não exige Retificação. Ela MUST NOT criar exigência, mudar momento, obrigatoriedade ou
  recorte, nem afetar conferência, desfecho ou classificação.
- **FR-3658**: Ao marcar requisito cujo recorte é por modalidade, a tela MUST mostrar um aviso: *"Este
  documento é exigido só de candidatos de uma modalidade de reserva. Inclua-o só se o setor precisar
  dele para formalizar."* O aviso MUST NOT impedir a gravação. É o único sinal de finalidade derivado
  de dado existente, e não há taxonomia.
- **FR-3659**: Quando um requisito da convocação definido é atendido por referência a um documento da
  inscrição também definido, o arquivo MUST aparecer e sair **uma vez**, pelo item da convocação.
- **FR-3660**: Os Editais existentes MUST começar com a definição vazia. Nenhuma migration MUST criar
  definição.

#### B. O acesso do setor

- **FR-3661**: MUST existir o papel **Formalização** no catálogo da unidade, com uma capacidade só, a de
  **acessar documentos para formalização**. Ele MUST NOT ser concedido por padrão a nenhum papel
  existente, no molde da FR-455 da `031`. É concedido e revogado pela gestão de acessos da `107`, sem
  mudança no modelo de vínculo.
- **FR-3662**: MUST existir a **designação para a formalização**: pessoa, Edital, Perfis opcionais
  (vazio = todos), motivo, quem designou, unidade de atuação e instante. É append-only, com revogação
  append-only e motivo.
- **FR-3663**: Designar e revogar MUST exigir `acesso:gerir` na unidade do Edital. A designação MUST ser
  recusada, com código próprio:
  - se a pessoa não tiver o papel Formalização vigente na unidade do Edital;
  - se a pessoa for quem designa, como a autoconcessão da `107`.
  
  Mudar os Perfis é revogar e designar de novo.
- **FR-3664**: O predicado **pode acessar a documentação da formalização** MUST ser único para a página,
  cada arquivo e cada exportação. Ele é verdadeiro quando, **na mesma requisição**:
  - o ator tem a capacidade do papel Formalização na unidade ativa;
  - a unidade ativa é a do Edital;
  - há designação vigente do ator no Edital, cobrindo o Perfil da pessoa;
  - a pessoa está apta (FR-3669).
- **FR-3665**: Nenhuma outra base MUST alcançar a página, os arquivos ou a exportação:
  - presidência e `comissao:gerir`;
  - alocação à conferência;
  - `inscricao:consultar` e `matricula:exportar`;
  - `acesso:gerir`;
  - auditoria.
  
  O predicado desta spec MUST NOT alcançar a conferência, os desfechos, a condução, a página de
  documentos da convocação da `115` nem o dossiê da inscrição.
- **FR-3666**: As recusas seguem a FR-3599 da `115` e o inventário da `033`:
  - escopo alheio, Edital, pessoa, documento ou exportação inexistente, Perfil fora da designação,
    pessoa não apta e Edital sem designação do ator recebem a **recusa de inexistente**;
  - ator com designação e sem o papel recebe a **recusa de autorização**, nomeando o papel.
- **FR-3667**: A revogação do papel, a revogação da designação e a suspensão da pessoa (`107`) MUST
  cortar o acesso na requisição seguinte. Revogar o papel MUST cortar todas as designações da pessoa
  sem revogá-las uma a uma.
- **FR-3668**: A presidência e `comissao:gerir` MUST ver, na condução do Edital e só para leitura, as
  designações vigentes, com pessoa, Perfis e data. Designação e revogação MUST ir para a trilha da
  unidade, como as concessões da `107`, e para a do Edital.

#### C. População e conjunto documental

- **FR-3669**: A pessoa está **apta para formalização** quando o desfecho vigente da convocação vigente
  da **chamada mais recente** da inscrição, no Edital, é um dos que incluem (aceite ou regularização).
  A leitura MUST ser feita na hora: nenhuma lista guardada, exportação anterior ou desfecho sucedido
  decide quem está apto.
- **FR-3670**: O conjunto de uma pessoa apta MUST ser formado pelos requisitos da definição vigente
  aplicáveis a ela:
  - **da convocação**: o item da lista da chamada mais recente (FR-3573 da `115`), entregue pela
    apresentação julgada na conferência vigente *conforme*, resolvida em um passo (FR-3619 da `115`),
    com o hash conferido como esperado;
  - **da inscrição**: o documento enviado na inscrição (`DocumentoSubmetido`), com o hash do envio como
    esperado.
- **FR-3671**: O documento da convocação sem conferência vigente *conforme* sobre a apresentação
  vigente MUST NOT sair. O documento da inscrição sai sem conferência, e a tela e o manifesto MUST
  dizê-lo: *"enviado na inscrição; sem conferência na convocação"*.
- **FR-3672**: As situações do item são:
  - *incluído*;
  - *não se aplica*;
  - *não apresentado*;
  - *não conferido*;
  - *indisponível*;
  - *integridade*.
  
  Só *indisponível* e *integridade* tornam a pessoa incompleta.
- **FR-3673**: Documento fora da definição, de pessoa não apta, dados do Requerimento de Matrícula,
  notas, pareceres e recursos MUST NOT aparecer na página, no pacote ou no manifesto.
- **FR-3674**: Um **seletor único** MUST compor o conjunto. Página, prévia e pacote MUST mostrar o mesmo
  conjunto para a mesma pessoa.

#### D. A página Documentos para formalização

- **FR-3675**: A barra MUST mostrar **Formalização** a quem tem a capacidade. A página inicial dela
  lista só os Editais com designação vigente do ator.
- **FR-3676**: A página do Edital MUST listar os aptos do alcance, agrupados por Perfil e ordenados pelo
  nome, com:
  - protocolo e nome;
  - chamada e data do desfecho;
  - *"Última exportação: DD/MM, por ‹nome›"*, lido do histórico;
  - por documento: requisito, situação, *Visualizar* e *Baixar*.
  
  Ela MUST NOT mostrar CPF, contato, modalidade, nota ou classificação.
- **FR-3677**: *Visualizar* MUST ser a ação primária, `inline`, sem cache, com a cópia verificada da
  FR-053a da `009`. *Baixar* MUST ser secundária e individual, com nome derivado do sistema,
  `‹protocolo›-‹chave do requisito›.pdf`, nunca o nome enviado.
- **FR-3678**: Edital sem definição ou sem nenhum documento definido aplicável MUST mostrar os aptos e
  dizer por quê não há documento, sem oferecer exportação.
- **FR-3679**: A página MUST mostrar o **histórico de exportações** do Edital no alcance do ator:
  - instante, autor e unidade;
  - alcance;
  - pessoas incluídas e não incluídas;
  - arquivos e tamanho;
  - resultado;
  - hash do pacote.
- **FR-3680**: Os textos MUST seguir a linguagem simples da `069` e caber em 375 px. Nenhum texto MUST
  dizer *obtido*, *encaminhado*, *recebido*, *entregue*, *matriculado*, *matrícula efetivada*, *bolsa
  concedida*, *vinculado* ou *contratado* (FR-3610 da `115`).
- **FR-3681**: A página MUST ter **um** controle de recorte, o Perfil, e só quando o alcance tiver mais
  de um. Não há outro filtro, busca avançada ou painel.

#### E. A exportação controlada

- **FR-3682**: Três alcances, e nenhum outro, **sempre dentro de um Edital e do alcance do ator**:
  - **pessoa**: a partir da linha;
  - **seleção**: as pessoas marcadas na lista;
  - **recorte**: todos os aptos do alcance, com o Perfil opcional.
  
  A seleção MUST ser enviada por POST, nunca na URL. Um id fora do alcance MUST recusar a exportação
  inteira como inexistente.
- **FR-3683**: MUST NOT existir exportação de vários Editais, de quem não está apto, de documento fora
  da definição ou de Edital fora da designação. Nenhum alcance MUST ser pré-selecionado: a lista começa
  sem marcação.
- **FR-3684**: A exportação de **mais de uma pessoa** MUST passar por uma **prévia** que não grava nada
  além da trilha de consulta. Ela mostra:
  - o alcance (Edital, Perfis, quantas pessoas);
  - por pessoa, os documentos e o tamanho;
  - os **arquivos ausentes**, verificados pela existência, sem ler o conteúdo;
  - as pessoas com exportação anterior;
  - o total de arquivos e de bytes.
- **FR-3685**: A exportação de **uma pessoa** MUST ter confirmação única sobre a lista dos documentos
  dela, sem prévia separada.
- **FR-3686**: O pacote MUST ser um ZIP sem compressão, com:
  - uma pasta por pessoa, `‹protocolo› ‹nome normalizado›/`;
  - um arquivo por documento incluído, `‹chave do requisito›.pdf`;
  - o `manifesto.csv` na raiz.
  
  As datas das entradas MUST ser as do envio de cada documento. O nome do arquivo baixado MUST NOT
  conter dado pessoal: `formalizacao-‹edital›-‹AAAAMMDD-HHMM›.zip`.
- **FR-3687**: O manifesto MUST ter:
  - **um cabeçalho**: Edital, alcance, versão da definição, instante, autor, resultado e identificador
    da exportação;
  - **uma linha por documento** de cada pessoa considerada: protocolo, nome, Perfil, chamada,
    requisito, momento, situação, caminho no pacote, SHA-256, instante do envio e, para a convocação,
    da conferência.
  
  Ele MUST NOT ter CPF, contato, modalidade, nome original do arquivo nem motivo da conferência.
- **FR-3688**: O pacote MUST ser montado num temporário **sem nome no sistema de arquivos**, legível só
  pelo processo, e MUST deixar de existir ao fim da resposta, com sucesso ou falha. MUST NOT existir
  URL, cópia, cache ou link para ele depois. É entregue como `attachment`, sem cache.
- **FR-3689**: A confirmação da prévia MUST recompor o alcance e compará-lo com a assinatura dela
  (pessoas, itens e hashes esperados). A divergência MUST ser recusada como prévia defasada, sem gerar
  nada.
- **FR-3690**: Cada arquivo MUST ter o hash reconferido **na mesma leitura** que o escreve no pacote.
- **FR-3691**: A exportação MUST ser recusada **antes de ler qualquer arquivo** quando a soma dos
  tamanhos passar de `EXPORTACAO_DE_FORMALIZACAO_LIMITE_MB`, configurável. O valor proposto é **400**,
  pela base da §5 do diagnóstico. A recusa mostra o tamanho por pessoa para dividir a seleção.
- **FR-3692**: MUST existir no máximo **uma exportação em geração por servidor** de cada vez, por trava
  consultiva no banco. A segunda é recusada com *"Uma exportação sua já está sendo gerada"*.
- **FR-3693**: Exportar MUST NOT alterar apresentação, conferência, desfecho, convocação, inscrição,
  definição ou Edital. A única escrita é o registro da exportação.

#### F. Falhas

- **FR-3694**: A pessoa com documento *indisponível* ou *integridade* MUST ficar **inteira** fora do
  pacote, sem pasta parcial. O manifesto, o registro e a tela MUST nomeá-la com o motivo.
- **FR-3695**: Arquivo ausente ou ilegível MUST ser tratado como *indisponível*, sem erro 500, na
  página desta feature **e** nas views de documento que já existem (inscrição, mesa e convocação). A
  resposta MUST ser *"Arquivo indisponível"*, e a trilha MUST gravar o evento sem nome de arquivo.
- **FR-3696**: Hash divergente MUST gravar o evento de integridade existente e MUST NOT servir o
  arquivo.
- **FR-3697**: O registro MUST ter um **resultado**:
  - **completo**: todas as pessoas do alcance foram incluídas;
  - **parcial**: alguma ficou de fora;
  - **sem pacote**: nenhuma pôde ser incluída, e nada é servido.
  
  A tela MUST dizer o resultado antes de qualquer outra informação.
- **FR-3698**: Falha depois de o pacote começar a ser enviado MUST NOT alterar o registro. O registro
  afirma só que o pacote foi **gerado e disponibilizado para download**.

#### G. Rastreabilidade

- **FR-3699**: Os eventos MUST ser estes, e nenhum outro afirma mais do que a evidência:

  | Evento | Quando | Agregado |
  |---|---|---|
  | **Documento visualizado** | arquivo servido `inline` | a apresentação ou o documento |
  | **Download individual disponibilizado** | arquivo servido como `attachment` | idem |
  | **Prévia de exportação consultada** | prévia mostrada | Edital |
  | **Pacote gerado e disponibilizado para download** | registro gravado e resposta devolvida | Edital |
  | **Exportação sem pacote** | nenhuma pessoa incluída | Edital |
  | **Arquivo indisponível** / **Integridade** | falha | a apresentação ou o documento |
  | **Definição dos documentos gravada** | versão nova | Edital |
  | **Designação concedida** / **revogada** | gestão de acessos | Edital e unidade |
  
  Nenhum evento MUST levar nome de pessoa, nome de arquivo ou motivo de conferência.
- **FR-3700**: Cada exportação MUST gravar um **registro da exportação**, append-only por gatilho e por
  privilégio ausente, com:
  - Edital, designação e versão da definição;
  - alcance e recorte;
  - autor, unidade e instante;
  - resultado;
  - por pessoa: inscrição, convocação e situação;
  - por documento incluído: origem e hash;
  - quantidade, tamanho e SHA-256 do pacote.
  
  Só ids e hashes. A tabela MUST entrar em `TABELAS_APPEND_ONLY`.
- **FR-3701**: MUST NOT existir estado derivado por pessoa além do fato *"última exportação"* (FR-3676),
  lido do histórico. MUST NOT existir *obtida*, *encaminhada*, *recebida* nem máquina de estados de
  transferência.
- **FR-3702**: O auditor MUST ver os eventos e o histórico na trilha do Edital, e MUST NOT abrir arquivo
  nem exportar.
- **FR-3703**: Nenhum log de aplicação, de servidor ou de erro MUST conter nome, CPF, nome de arquivo ou
  conteúdo. As URLs desta feature MUST conter só identificadores opacos.

#### H. Limites e compatibilidade

- **FR-3704**: Esta feature MUST NOT criar cópia persistente de arquivo nem repositório (D-004).
- **FR-3705**: Esta feature MUST NOT mudar a `115` ou a `009`, salvo o tratamento de arquivo
  indisponível (FR-3695).
- **FR-3706**: A exceção à FR-069 da `009` e à FR-3606 da `115` MUST valer só para a exportação desta
  feature, nas condições das FR-3653, FR-3664, FR-3669 a FR-3674 e FR-3682 a FR-3700. A revisão dos
  textos é a da D-016, **e só se aplica com a aprovação do usuário**.
- **FR-3707**: MUST NOT existir confirmação de recebimento, encaminhamento ativo, integração externa
  nem aviso por e-mail ao setor.
- **FR-3708**: Nenhuma coluna, índice ou unicidade nova MUST presumir que a unidade do ator é a do
  Edital. A unidade de atuação vai na linha (FR-3602 da `115`).
- **FR-3709**: A designação e a definição MUST ser por Edital, porque a convocação é do Edital, e não
  por Processo. Um Processo com vários Editais exige uma designação por Edital.
- **FR-3710**: O encerramento do Edital (`113`) MUST NOT fechar a página nem a exportação.

### Matriz de permissões

"404" é a recusa de inexistente; "403", a de autorização no escopo.

| Ator | Página da formalização | Visualizar e baixar | Exportar | Definir documentos | Designar e revogar | Documentos da convocação (`115`) | Conferir e desfechar |
|---|---|---|---|---|---|---|---|
| Papel Formalização + designação, sem restrição | sim | sim, aptos | sim | 403 | 403 | 403 | 403 |
| Papel Formalização + designação no Perfil A, pessoa do B | a pessoa não aparece | 404 | B fora do alcance; seleção forjada: 404 | 403 | 403 | 403 | 403 |
| Papel Formalização, sem designação no Edital | 404 | 404 | 404 | 403 | 403 | 403 | 403 |
| Designação vigente, papel revogado | 403, nomeando o papel | 403 | 403 | 403 | 403 | 403 | 403 |
| `acesso:gerir` (administrador de acessos) | 403 | 403 | 403 | 403 | **sim, exceto a si** | 403 | 403 |
| Presidência da comissão | 403; vê as designações | 403 | 403 | **sim** | 403 | sim (`115`) | sim (`115`) |
| `comissao:gerir` (papel Gestor) | 403; vê as designações | 403 | 403 | **sim** | 403 | sim (`115`) | sim (`115`) |
| Membro alocado à conferência | 403 | 403 | 403 | 403 | 403 | sim, no alcance | confere |
| `inscricao:consultar`, `matricula:exportar` | 403 | 403 | 403 | 403 | 403 | 403 | 403 |
| Auditor | 403; vê a trilha e o histórico | 403 | 403 | 403 | 403 | 403 | 403 |
| Ator de outra unidade | 404 | 404 | 404 | 404 | 404 | 404 | 404 |

**Três funções e três donos.** A condução define **o quê**. A gestão de acessos define **quem**. O
setor **exporta**. Quem acumula papéis, como numa equipe de duas ou três pessoas, tem a união das
linhas, e cada acesso é decidido pelo seu predicado.

### Key Entities

- **Definição dos documentos para a formalização** (nova, append-only, versionada): Edital, requisitos,
  motivo, autor, unidade, instante.
- **Papel Formalização** (entrada nova no catálogo existente): uma capacidade.
- **Designação para a formalização** e **revogação** (novas, append-only): pessoa, Edital, Perfis,
  motivo, autor, unidade, instante.
- **Registro da exportação** (novo, append-only): Edital, designação, versão da definição, alcance,
  resultado, pessoas, documentos com hash, totais, hash do pacote.
- **Documento Exigido, Documento Submetido, Item da lista, Apresentação, Conferência, Convocação e
  Desfecho**: lidos, nunca escritos. **O Documento Exigido não muda.**

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1101**: No Cenário A (40 aptos × 5 documentos), o setor exporta toda a documentação definida em
  **no máximo 4 gestos** a partir da página: selecionar todos, exportar, conferir a prévia, confirmar.
  Hoje são cerca de 680.
- **SC-1102**: Em nenhum teste um documento fora da definição, de pessoa não apta ou de Perfil fora da
  designação aparece na página, no pacote ou no manifesto (Cenários C e E).
- **SC-1103**: O desfecho corrigido de aceite para indeferimento tira a pessoa da próxima página,
  prévia e exportação, sem ação de ninguém (Cenário D).
- **SC-1104**: Toda URL e todo POST desta feature, tentados por cada linha da matriz fora do alcance,
  recebem a recusa da matriz.
- **SC-1105**: Com um arquivo ausente e um divergente num pacote de 5 pessoas, o pacote sai **parcial**
  com 3 pessoas completas. Manifesto, registro e tela nomeiam as 2 excluídas, e nenhuma resposta é 500
  (Cenário F).
- **SC-1106**: Depois de qualquer exportação, com sucesso, recusa, falha ou exceção injetada, nenhum
  arquivo novo existe sob a raiz privada nem no diretório temporário do processo.
- **SC-1107**: O SHA-256 de cada arquivo no pacote é igual ao do manifesto e ao esperado (o conferido,
  ou o do envio). O do pacote é igual ao do registro.
- **SC-1108**: Duas exportações do mesmo alcance, sem mudança, produzem entradas de documento
  idênticas byte a byte.
- **SC-1109**: No Cenário B (bolsista), o setor visualiza e baixa sem exportar, e a trilha distingue
  *visualizado* de *download disponibilizado*.
- **SC-1110**: Revogada a designação ou o papel, ou suspensa a pessoa, a requisição seguinte é recusada.
- **SC-1111**: O pacote do Cenário A (200 arquivos de 1,5 MB) é gerado em menos de 30 s no CI, e o
  número de consultas não cresce com o número de pessoas.
- **SC-1112**: Nenhuma tela desta feature diz *obtido*, *encaminhado*, *recebido*, *entregue*,
  *matriculado*, *bolsa concedida*, *vinculado* ou *contratado*.

## Assumptions

- A `115` está na `main` quando a implementação começar.
- Os arquivos são PDFs de até 10 MiB. ZIP sem compressão é o adequado, porque PDF não comprime bem.
- A geração é síncrona, como a da `031`. Tarefa assíncrona só se a medição da SC-1111 ou a operação
  mostrarem necessidade.
- A infraestrutura de produção é a da implantação recomendada: 5 workers síncronos, 120 s, `/tmp`
  privado no disco do sistema e buffer do nginx no padrão (§5 do diagnóstico). A TI confirma.
- O setor de outra unidade (MAT-09) continua recebendo pelo canal institucional que já usa.

## Proteção de dados (LGPD)

- **Necessidade**: só aptos, só documentos definidos, sem CPF, contato ou modalidade no manifesto, e
  aviso ao definir documento de reserva (FR-3653, FR-3658, FR-3673, FR-3687).
- **Segurança**: papel e designação, prévia, reconferência, temporário sem nome, limite, concorrência,
  seleção por POST (FR-3661 a FR-3692).
- **Responsabilização**: eventos distintos e registro com hash. A definição e o acesso são registrados
  com motivo e autor (FR-3655, FR-3663, FR-3699, FR-3700).
- **Transparência ao titular**: é dever do aviso de privacidade do Edital, e não regra do sistema
  (pendência 6). O registro permite responder ao titular a que setor e quando os documentos dele foram
  disponibilizados.
- **O que sai do controle do GPS**: depois do download, o arquivo está sob custódia do setor (§10.6 do
  complemento).

## Compatibilidade e conflitos com regras anteriores

| Regra | Conflito | Proposta |
|---|---|---|
| **FR-069 da `009`** | proíbe lote e exportação | **Exceção estreita** (D-016), proposta, não aplicada |
| **FR-3606 da `115`** | reafirma a proibição na convocação | Mesma exceção (D-016), proposta, não aplicada |
| **FR-3595 da `115`** | único caminho ao arquivo da convocação | Continua sendo o da seleção. Esta spec cria um predicado disjunto (FR-3664, FR-3665) |
| **FR-3610 da `115`** | veda *encaminhado* | Continua. Esta spec veda também *obtido*, *recebido* e *entregue* (FR-3680) |
| **FR-3615 da `115`** | nada se exclui | Continua. O pacote não é guardado (FR-3688) |
| **FR-455 e FR-456 da `031`** | capacidade própria; arquivo não guardado | Molde seguido (FR-3661, FR-3688) |
| **Decisão da `115` sobre momento e aproveitamento não retificáveis** | a primeira versão desta spec dependia dela para o Cenário B | **Desaparece**: a definição não toca o Documento Exigido (D-009) |
| **Gestão de acessos da `107`** | — | Ganha um papel no catálogo e a tela de designação. O modelo de vínculo não muda |
| **Doutrina "escopo alheio = 404" (`033`)** | — | Mantida; os 404 novos entram no inventário |
| **SC-016 da `009`** | a seleção verifica sem lote | Continua: a exportação não é da seleção |

## Decisões

### D-001 — O GPS não é GED

**Decisão do usuário.** Nada aqui guarda o que foi exportado. A custódia posterior é do setor.

### D-002 — Seleção e formalização são responsabilidades distintas

**Decisão do usuário.** A comissão confere e desfecha. O setor formaliza, sem competência de seleção
(FR-3665).

### D-003 — Aceite não é vínculo efetivado

**Decisão do usuário.** Apto, disponibilizado e efetivado são três fatos com três fontes.

### D-004 — Não duplicar documentos

**Decisão do usuário.** O pacote é montado das fontes e descartado. O registro guarda ids e hashes.

### D-005 — Segurança e minimização

**Decisão do usuário.** Só o necessário à competência do setor. Laudo, documento de reserva,
autodeclaração e títulos não seguem por presunção (FR-3653, FR-3658).

### D-006 — O GPS continua multiunidade

**Decisão do usuário.** A unidade de atuação vai em cada linha nova. O MAT-09 não é implementado
(FR-3708).

### D-007 — Página restrita com exportação controlada (B + C); D como evolução

*Proposta.* A comparação está na §3 do diagnóstico. A Alternativa A não dá acesso legítimo, a B
sozinha deixa 200 downloads, e a D depende de capacidade externa não demonstrada.

### D-008 — População: o desfecho vigente da chamada mais recente, lido na hora

*Proposta.* Sem lista guardada. A população da `031` não serve, porque inclui quem não respondeu
(FR-3669).

### D-009 — A finalidade numa definição interna por Edital, e não no Documento Exigido

*Proposta revista. Bloqueia a implementação.*

**Por que não a marca no Documento Exigido**, que era a proposta da primeira versão. A tabela por
cenário está na §4.2 do diagnóstico. Em resumo:

- **falha o Cenário B**: documento só da inscrição exigiria duplicar a exigência na convocação, e em
  Edital publicado nem isso, porque o aproveitamento não é retificável;
- **mistura obrigação com encaminhamento**, o que obriga a Retificar uma escolha de rota;
- **impede corrigir a favor da minimização** quem já foi convocado.

**A definição** é um conjunto de requisitos do Edital, de qualquer momento, vazio por padrão,
append-only e versionado. Ela fica fora do conteúdo publicado.

**Rejeitados:**

- **atributo no catálogo comum**: o catálogo institucional não existe, porque a QI-3 decidiu que cada
  Edital declara os seus;
- **taxonomia de finalidades** (classificação, reserva, formalização…), que o pedido veda sem
  necessidade comprovada;
- **inferir pelo recorte de modalidade**: heurística sobre dado sensível. Ele vira **aviso** (FR-3658);
- **escolha pelo setor na hora**: o destinatário escolheria o que recebe.

### D-010 — Quem define: a condução do processo

*Proposta.* A presidência ou `comissao:gerir` sabem para que pediram cada documento. Não é competência
de seleção nova: é a mesma base que já aloca à conferência. O setor não define, e a gestão de acessos
também não, porque ela decide quem, e não o quê.

### D-011 — Vigência da definição e chamadas anteriores

*Proposta.* A **obrigação** do candidato fica congelada na lista da `115`, e não muda. O
**encaminhamento** não é congelado na convocação, e cada exportação grava a versão que aplicou. Assim:

- uma correção de minimização vale na hora para todos;
- a história de cada exportação fica intacta.

Congelar na convocação impediria tirar um laudo incluído por engano de quem já foi chamado.

### D-012 — Nem PDF nem Retificação

*Proposta.* A definição não muda o que o candidato deve apresentar, quando nem sob que regra. Por isso
não é conteúdo normativo (FR-3657). A Retificação só é necessária quando o setor precisa de documento
que o Edital **não** exigiu, porque aí muda a obrigação. Isso segue as regras existentes e não é desta
spec. A transparência ao titular é do aviso de privacidade (pendência 6).

### D-013 — Acesso: papel no catálogo existente + designação, os dois pela gestão de acessos

*Proposta revista. Bloqueia a implementação.*

| Opção | Por que sim | Por que não sozinha |
|---|---|---|
| Papel novo | barra sem consulta; revogação de uma vez; usa a `107` | é a unidade inteira: mistura setores |
| Capacidade pelo modelo existente | idem | na `107`, capacidade só se concede por papel, e é o mesmo que acima |
| Designação por Edital e Perfil | recorte preciso | sem papel, a barra precisaria de consulta por requisição, e desligar quem sai do setor seria Edital por Edital |
| **Papel + designação, pela gestão de acessos** | recorte preciso, alavanca institucional, um só administrador, sem mudar o vínculo | — |

**Quem concede e revoga:** `acesso:gerir`, na unidade do Edital, com motivo e sem autodesignação. A
presidência **vê** as designações e não as concede, porque o pedido de revisão pede que ela não
administre sozinha o acesso dos setores, e porque quem conduz a seleção não deve escolher quem recebe
os documentos dos candidatos. **Estrutura nova:** só a designação. O papel é uma entrada no catálogo
que já existe.

**Rejeitado:**

- reusar a alocação à conferência, que dá competência de conferir;
- reusar `matricula:exportar`, que é outro ato, sobre dado e não sobre documento;
- acrescentar Edital ou Perfil ao `Vinculo` da `107`, que mudaria o modelo central de acesso para um
  caso só.

### D-014 — Alcance da exportação: pessoa, seleção, recorte

*Proposta revista.* Não há "pacote do Edital".

- **Pessoa**: o caso de quem chega por regularização ou de uma chamada pequena.
- **Seleção**: o setor escolhe quem já pode formalizar.
- **Recorte**: todos os aptos do alcance, com Perfil opcional, para a chamada inteira de um setor.

Todo alcance é cortado pela designação, e por isso **dois setores no mesmo Edital nunca recebem o
Perfil do outro**. A lista começa sem marcação (FR-3683).

**Limite conhecido:** se dois setores atendem Perfis diferentes e um documento é exigido de todos os
Perfis, cada setor recebe esse documento só das pessoas do próprio alcance. Uma definição por setor
dentro do mesmo Edital fica para depois, se algum Edital real a pedir.

### D-015 — Terminologia dos eventos

*Proposta revista.* O GPS afirma o que ele mesmo fez (FR-3699):

- **visualizado**: serviu `inline`;
- **download individual disponibilizado**: serviu como `attachment`, sem saber se a transferência
  terminou;
- **pacote gerado e disponibilizado para download**: na geração síncrona, gerar e disponibilizar são o
  mesmo ato, na mesma resposta. Uma geração assíncrona os separaria.

*Encaminhamento efetivamente realizado* e *recebimento institucional confirmado* não têm mecanismo
aqui, e por isso não têm evento nem palavra na tela. *Obtido* sai, porque afirmava a recepção pelo
setor.

### D-016 — Revisão proposta da FR-069 da `009` e da FR-3606 da `115`

*Proposta. **Não aplicada.** Bloqueia a implementação.*

**FR-069 da `009`, redação proposta**, preservando a regra:

> **FR-069**: Cada documento DEVE poder ser aberto pela interface, exibido no navegador quando o
> formato permitir; baixar DEVE existir apenas como ação secundária individual. NÃO DEVE existir
> download em lote, exportação, planilha nem painel. ***Exceção única (`117`):*** *a exportação, pelo
> setor responsável pela formalização, com papel próprio e designação no Edital concedidos pela gestão
> de acessos, dos documentos que a condução definiu como necessários à formalização, só de quem está
> apto para formalização e dentro do alcance da designação, com prévia, confirmação, manifesto,
> limite, registro append-only e sem guarda do pacote. A exceção não alcança a consulta de inscrições,
> a seleção nem exportação de todos os inscritos.*

**FR-3606 da `115`, redação proposta:**

> **FR-3606**: A visualização no navegador, sem cache, MUST ser o padrão. Baixar MUST existir só como
> ação secundária individual e registrada. MUST NOT existir download em lote, pacote, ZIP, planilha ou
> exportação de documentos da convocação **na condução e na página de documentos da convocação**. *A
> única exceção é a exportação da formalização da `117`, pela exceção da FR-069 da `009`.*

**Justificativa.** A regra nasceu contra a pasta de rede com todos os inscritos, montada pela própria
seleção. A exceção muda as quatro variáveis que a tornavam perigosa:

- a **população**: só aptos, e só os do alcance;
- o **conteúdo**: só os definidos;
- o **ator**: o setor, com acesso concedido por quem não conduz a seleção;
- a **finalidade**: a custódia institucional, que exige cópia.

A proteção geral contra exportação indiscriminada continua, nas duas regras. Os riscos residuais estão
na §2.8 do diagnóstico.

**Como aplicar, depois da aprovação:** no primeiro commit da implementação, editar os dois arquivos
com a nota *"revista pela `117` em ‹data›, por decisão do usuário"*, como a `115` fez com a FR-402 da
`029`.

### D-017 — Sem estados derivados

*Proposta revista.* O histórico de exportações e a trilha bastam. O único dado por pessoa é o fato
*"última exportação"* (FR-3701). As situações *obtida*, *mudou depois* e *deixou de estar apta* da
primeira versão saem.

### D-018 — Falha: atomicidade por pessoa e resultado explícito

*Proposta.*

- **Recusar o pacote inteiro por um arquivo** bloquearia o setor.
- **Servir a pasta parcial** entregaria dossiê incompleto como se estivesse completo.

A pessoa entra completa ou não entra, e o registro diz **completo**, **parcial** ou **sem pacote**
(FR-3694, FR-3697). O arquivo ausente deixa de ser 500 também nas views existentes (FR-3695): é
defeito conferido no código (§2.9 do diagnóstico), e a página nova o exporia.

### D-019 — Limite de 400 MB e uma exportação por servidor

*Proposta, com base na §5 do diagnóstico.* O limite precisa:

- caber no buffer padrão do nginx (1 GB), para liberar o worker;
- manter o pior caso de disco (5 workers × temporário + buffer) em 4 GB num disco de sistema de 40 GB;
- cobrir o Cenário A, que tem cerca de 300 MB, com folga.

O tempo não é o gargalo. Uma exportação por servidor evita o duplo clique e limita o pior caso. **A TI
confirma o valor na VM real.**

### D-020 — Sem justificativa em texto livre

*Proposta.* A finalidade está fixada pela definição, pelo papel e pela designação, que **têm** motivo.
Pedir motivo a cada pacote viraria texto repetido. O controle está na prévia e no registro.

### D-021 — Confirmação de recebimento fora do MVP

*Proposta.* O GPS só registraria um clique, e não a guarda no ambiente do setor. Se o controle pedir,
cabe numa evolução: ato append-only do setor sobre o registro da exportação, e só então a palavra
*recebido*.

### D-022 — Documento da inscrição sai sem conferência, e diz isso

*Proposta.* O documento da inscrição é imutável depois do envio, e o hash dele é a prova. Exigir
conferência na convocação para entregá-lo seria criar trabalho para a comissão sem pedido do Edital.
O manifesto e a tela o distinguem do conferido (FR-3671).

## MVP e o que fica para depois

**MVP**: as US1 a US5 e o tratamento de arquivo indisponível nas views existentes. O primeiro corte
demonstrável é US1 a US3, que já atende o Cenário B. O Cenário A exige a US4.

**Fica para depois**, cada item com o que o justificaria:

| Item | Quando |
|---|---|
| Aviso de quem deixou de estar apto depois de exportado | se o setor relatar caso real |
| Geração assíncrona, com *gerado* separado de *disponibilizado* | se a SC-1111 ou a operação mostrarem necessidade |
| Definição por setor dentro do mesmo Edital | se um Edital real misturar setores com necessidades distintas |
| Confirmação de recebimento | se o controle interno pedir (D-021) |
| Encaminhamento a sistema externo | se a TI demonstrar capacidade de recebimento |
| Setor de outra unidade | com o MAT-09 |

## Estratégia de testes

| Camada | O quê |
|---|---|
| Unidade | seletor do conjunto: desfechos, sucessões, chamadas múltiplas, inscrição e convocação, deduplicação, situações, versão da definição |
| Integração | definição (quem, versão, aviso); papel e designação (quem concede, autodesignação, revogação, suspensão, append-only por gatilho); registro e resultado |
| Integração | pacote: estrutura, manifesto, hashes, atomicidade, ausente, divergente, limite, prévia defasada, seleção forjada, concorrência, temporário removido (inclusive com exceção injetada) |
| Regressão | arquivo ausente nas views existentes (inscrição, mesa, convocação): sem 500 |
| Interface | matriz inteira por URL e POST; 375 px; vocabulário; CSP sem inline |
| Banco | `TABELAS_APPEND_ONLY` + 4; `make preparar` conta o `M` novo |
| Desempenho | consultas constantes com 5 e 45 pessoas; Cenário A em menos de 30 s |
| Navegador | jornada do setor nos Cenários A e E |
| Guardiões | inventário da `033`, vocabulário, citações, README, migrations por app |

Contra PostgreSQL (`make test-pg`).

## Critérios para homologação

1. A `115` está na `main`, e a FR-069 da `009` e a FR-3606 da `115` foram revistas com aprovação.
2. `make lint check test-pg` verde, com o grupo `navegador`.
3. Demonstração dos seis cenários do quickstart, com capturas a 1280 px e a 375 px.
4. Um servidor do Registro Acadêmico ou da Coordenação UAB exporta num Edital de homologação e
   confirma que pastas e manifesto servem ao setor. Critério **humano**.
5. A TI confirma o limite, o `/tmp` e o buffer do nginx na VM.

## Pendências do usuário

**Bloqueiam a implementação:**

1. **Aprovar a exceção à FR-069 da `009` e à FR-3606 da `115`** (D-016).
2. **Aprovar a definição interna por Edital**, pela condução, fora do PDF e sem Retificação (D-009 a
   D-012).
3. **Aprovar o acesso pela gestão de acessos**: o papel Formalização e a designação por Edital com
   Perfis, os dois concedidos por `acesso:gerir`, com a presidência só vendo (D-013).
4. **Merge do PR #369** (implementação da `115`).

**Decidem detalhe, sem bloquear o plano:**

5. O limite de 400 MB e a concorrência (D-019), a confirmar com a TI.
6. **O aviso de privacidade do Edital**: a instituição diz ao candidato que os documentos necessários
   à formalização são disponibilizados ao setor competente. É texto institucional, e não regra do
   sistema. Cabe à área de proteção de dados.
7. O nome do candidato na pasta e no manifesto. A proposta é sim: o setor precisa identificar a pessoa.
8. Sem justificativa em texto livre (D-020); confirmação de recebimento fora do MVP (D-021).

**Registradas, sem escopo aqui:** MAT-09; QI-4; §10.5 do complemento (o acesso amplo do Gestor ao
dossiê de inscrição); Alternativa D.
