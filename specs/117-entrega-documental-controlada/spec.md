# Feature Specification: Entrega documental controlada ao setor da formalização

**Feature Branch**: `claude/gps-entrega-documental-627460`, sobre a `main` em `83cd5863`

**Created**: 2026-11-04 · **Revista**: 2026-11-04 (revisão final) · **Consolidada**: 2026-11-04 ·
**Ajustada**: 2026-11-04, depois da revisão independente

**Status**: **Aprovada quanto ao desenho pelo usuário em 04/11/2026**, com os ajustes da
consolidação. Nenhum código, migration ou tela foi alterado. Situação das decisões:

- **Premissas do usuário:** D-001 a D-006.
- **Aprovadas pelo usuário em 04/11:**
  - D-009 a D-012: definição interna, versionada, por Edital;
  - D-013: papel e designação pela gestão de acessos;
  - D-016: exceção à FR-069 da `009` e à FR-3606 da `115`;
  - D-019: limite inicial de 400 MB, a validar na VM;
  - D-020: sem justificativa por exportação;
  - D-021: confirmação de recebimento fora do MVP;
  - nome e protocolo dentro do pacote, sem CPF nem contato.
- **Propostas de desenho que a revisão não contestou:** D-007, D-008, D-014, D-015, D-017, D-018,
  D-022.
- **Ajustadas na consolidação:**
  - **D-018**: o resultado aparece antes do download, por uma verificação que precede o pacote;
  - **D-019**: o limite inicial ficou separado da capacidade da VM, e a trava e o tempo-limite
    ganharam ciclo de vida explícito;
  - **D-023**: novo, sobre a segurança dos nomes, dos caminhos e do manifesto.
- **Ajustadas depois da revisão independente (04/11):**
  - a FR-3705, que contradizia a FR-3706 e a T002;
  - a verificação passa a ter **comprovante assinado pelo servidor** (D-024, FR-3689a);
  - a **correspondência integral** entre a verificação e o pacote, inclusive as pessoas excluídas e os
    motivos (FR-3689, FR-3689b);
  - a medição separada de verificação, montagem e transferência (SC-1111).
  
  Nenhum número novo foi aberto: o PR #372, da implementação da `116`, já usa os números seguintes aos
  desta spec.

**A revisão da FR-069 da `009` e da FR-3606 da `115` está aprovada, e não aplicada.** Ela se aplica
aos dois arquivos na T002, primeira tarefa da implementação (D-016).

**Depende de**: a implementação da `115`, **mergeada na `main` em 04/11/2026** (PR
vitofranzosi/processo_seletivo#369, merge `f563b5a3`). A dependência está resolvida.

**Input**: os pedidos do usuário de 04/11/2026 (o inicial, a revisão final e a consolidação); a §10.4
do [complemento da auditoria de matrícula e dossiê](../../doc/auditoria-matricula-e-dossie-documental-2026-11-03-complemento.md);
e o [diagnóstico desta feature](diagnostico.md).

> **Faixa de identificadores.** Esta spec abre em **FR-3653** e **SC-1101**. O teto foi medido em
> 04/11/2026 em `specs/*/spec.md` de todas as worktrees desta máquina e de todas as branches remotas:
> o requisito funcional três mil seiscentos e cinquenta e dois e o critério mil e cem, os dois da
> `116`, no PR #370 sem merge. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`. Os
> requisitos acrescentados na consolidação vêm depois do último já publicado no PR, para não
> renumerar o que já foi revisto. **Os ajustes da revisão independente não abrem número**: usam sufixo
> de letra (FR-3689a, FR-3689b), como a FR-053a da `009`. Em 04/11, a implementação da `116` (PR #372)
> passou a usar o requisito três mil setecentos e quinze em diante e o critério mil cento e quinze em
> diante, logo depois desta faixa.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-069 da `009`"). Uma decisão de outra feature, pelo assunto e pela feature. Os achados
> e questões das auditorias (`MAT-NN`, `QI-N`) são citados como estão nos documentos de origem.

---

## Por que esta feature existe

A `115` completa a convocação: o GPS passa a saber quem está **apto para formalização**. **Falta a
passagem ao setor que formaliza.** Hoje:

- **O setor não tem acesso legítimo.** O único caminho até o arquivo da convocação é o predicado de
  quem **confere** (FR-3595 da `115`).
- **O esforço é proporcional ao número de arquivos.** São cerca de 680 gestos para 40 aptos com 5
  documentos (§2.10 do diagnóstico).
- **O lote é proibido** pela FR-069 da `009` e pela FR-3606 da `115`.
- **Nada distingue** o documento que serve só à seleção do que o setor precisa.
- **Nada registra** o que foi disponibilizado ao setor.
- **Arquivo ausente vira erro 500 sem registro** (§2.9 do diagnóstico).

### O que esta spec cobre

- **A.** A **definição dos documentos para a formalização**, por Edital, feita pela condução.
- **B.** O acesso do setor: o papel **Formalização** e a **designação** por Edital, com Perfis
  opcionais, os dois concedidos pela gestão de acessos.
- **C.** A página **Documentos para formalização**: os aptos do alcance, a visualização e o download
  individuais.
- **D.** A **exportação controlada**, por pessoa, por seleção ou por recorte. Um ZIP com manifesto é
  montado depois de uma verificação que mostra o resultado, num temporário sem nome, e nunca é
  guardado.
- **E.** O registro da exportação e a trilha.
- **F.** O tratamento de arquivo indisponível, de divergência, de falha inesperada e de tempo-limite.

### O que fica fora

- GED, acervo, guarda prolongada, destinação ou descarte (D-001; QI-4).
- Encaminhamento ativo e integração com SIGAA, SIPAC, CAPES ou outro sistema.
- Confirmação de recebimento (D-021).
- Geração assíncrona: só por decisão do usuário, se a validação na VM o pedir (D-019).
- Exportação de quem não está apto, de documento fora da definição ou de vários Editais.
- Competência nova para o setor.
- Mudança na `115` além do tratamento de arquivo ausente.
- Escopo entre unidades (MAT-09).
- O acesso amplo do Gestor ao dossiê de inscrição (§10.5 do complemento).
- **Catálogo institucional de documentos, taxonomia de finalidades ou motor de classificação
  documental.**

### Três estados, três fontes

| Termo | Fonte | Quem afirma |
|---|---|---|
| **Apto para formalização** | desfecho vigente que inclui | o GPS, pelo ato da seleção |
| **Disponibilizado ao setor** | evento ou registro da exportação | o GPS, pelo próprio ato de servir o arquivo |
| **Matrícula efetivada, bolsa concedida, contrato celebrado** | sistema ou setor do vínculo | **nunca o GPS** |

## Clarifications

### Session 2026-11-04

- Q: O GPS guarda o que o setor baixou? → A: Não (D-001).
- Q: O setor pode conferir ou desfechar? → A: Não (D-002).
- Q: Disponibilizar é efetivar o vínculo? → A: Não (D-003).
- Q: O pacote é cópia guardada? → A: Não (D-004).
- Q: O setor recebe tudo? → A: Só o definido para a formalização (D-005).
- Q: Multiunidade? → A: Não fechar o caminho (D-006).

### Session 2026-11-04 (revisão final)

- Q: Onde fica a finalidade? → A: Numa definição interna por Edital, de qualquer momento, fora do
  conteúdo publicado (D-009).
- Q: PDF ou Retificação? → A: Não, porque a obrigação não muda (D-012).
- Q: Quem concede o acesso? → A: A gestão de acessos (D-013).
- Q: Pacote do Edital inteiro? → A: Não. Por pessoa, seleção ou recorte (D-014).
- Q: "Obtido", "encaminhado", "recebido"? → A: Não (D-015).

### Session 2026-11-04 (consolidação)

- Q: O operador baixa um ZIP direto. Como ele sabe que o pacote é parcial, quem ficou de fora e por
  quê? → A: Pela **verificação**, que lê e confere todos os arquivos antes do pacote e mostra o
  resultado na tela, com as pessoas excluídas e os motivos. O botão de baixar diz quantas pessoas
  entram. O ZIP baixado é exatamente o verificado. O nome do arquivo, o manifesto e o histórico repetem
  o resultado (D-018).
- Q: E se o arquivo mudar entre a verificação e o download? → A: A geração reconfere, e qualquer
  diferença recusa o download como verificação defasada, sem servir nada (FR-3689).
- Q: O limite de 400 MB é a capacidade da VM? → A: Não. É o valor inicial. A capacidade é medida na
  VM, na homologação, e a primeira resposta a uma medição ruim é reduzir o limite (D-019).
- Q: A trava segura a transferência? → A: Não. Ela vive na transação da verificação ou da geração e
  sai no commit, no rollback ou no fechamento da conexão (FR-3692).

### Session 2026-11-04 (revisão independente)

- Q: Um resumo SHA-256 dos dados prova que a verificação foi feita pelo servidor? → A: Não. Quem
  reconstruir os valores fabrica o resumo. A verificação devolve um **comprovante assinado pelo
  servidor** (`django.core.signing`, HMAC com a chave do sistema), válido por 15 minutos e vinculado ao
  ator, à unidade, ao Edital, à designação, ao alcance, à versão da definição, ao resultado e ao
  resumo do conteúdo verificado. Não há tabela (D-024, FR-3689a).
- Q: O que precisa coincidir entre a verificação e o download? → A: Tudo o que a verificação mostrou:
  as pessoas incluídas com os documentos e hashes, as **excluídas com o motivo codificado**, a
  definição, a designação e o resultado. O download relê também os arquivos das excluídas (FR-3689b).
- Q: O comprovante pode ser usado duas vezes? → A: Sim, dentro da validade e pelo mesmo ator, e cada
  uso gera um registro. Uso único exigiria guardar o comprovante, o que a decisão de não criar tabela
  descarta. Repetir equivale a clicar de novo.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A condução define quais documentos vão para a formalização (Priority: P1)

Na condução do 72/2026, a presidência abre **Documentos para a formalização**. A lista começa sem
nenhuma marcação. Ela marca:

- identidade, CPF e histórico, da convocação;
- o certificado, da inscrição.

Ao marcar a comprovação de renda, a tela avisa que é documento de modalidade de reserva, e ela
desmarca. Ao marcar os títulos, a tela avisa que é documento da inscrição e pergunta, em texto, se o
setor precisa dele para formalizar. Ela desmarca. Grava com motivo, e o histórico mostra a versão
nova.

**Why this priority**: é a minimização (D-005). Sem a definição, nada sai.

**Independent Test**: definir num Edital com documentos dos dois momentos e conferir a versão, o
histórico e a trilha.

**Acceptance Scenarios**:

1. **Given** um Edital sem definição, **When** a página do setor é aberta, **Then** nenhum documento
   está disponível, e a página diz que a condução ainda não definiu os documentos.
2. **Given** a gravação sem motivo, **When** enviada, **Then** é recusada, e nada é gravado.
3. **Given** um requisito com recorte por modalidade, ou da inscrição, **When** marcado, **Then** a tela
   mostra o aviso correspondente, e a gravação continua possível.
4. **Given** duas versões, **When** a presidência, o Gestor ou o auditor abrem o histórico, **Then**
   veem cada versão com autor, data, motivo e os documentos acrescentados e retirados.
5. **Given** a definição gravada, **When** se comparam o snapshot, o hash e o PDF do Edital, **Then**
   nada mudou.
6. **Given** o servidor do setor, **When** tenta gravar ou ver o histórico, **Then** recebe a recusa de
   autorização.

---

### User Story 2 — A gestão de acessos concede ao setor o papel e o Edital (Priority: P1)

O administrador de acessos concede o papel **Formalização** a Rui, do Registro Acadêmico, e o designa
para o 72/2026. Faz o mesmo com Bia, da Coordenação UAB, no 146/2025, só no Perfil de tutor. Rui não
integra a comissão.

**Why this priority**: é a chave do acesso.

**Independent Test**: conceder, designar, revogar a designação, revogar o papel e suspender a pessoa,
conferindo a página depois de cada passo.

**Acceptance Scenarios**:

1. **Given** Rui com o papel e sem designação, **When** abre a página de um Edital, **Then** recebe a
   recusa de inexistente.
2. **Given** a designação de quem não tem o papel, **When** gravada, **Then** é recusada com código
   próprio.
3. **Given** o administrador de acessos, **When** tenta designar a si mesmo, **Then** é recusado.
4. **Given** a presidência, **When** tenta designar, **Then** recebe a recusa de autorização. Ela vê as
   designações vigentes, só para leitura.
5. **Given** Bia, só no Perfil de tutor, **When** tenta a URL de documento de outro Perfil, **Then**
   recebe a recusa de inexistente.
6. **Given** Rui designado em três Editais, **When** o papel é revogado, **Then** a próxima requisição é
   recusada nos três.
7. **Given** membro alocado à conferência, **When** abre a página da formalização, **Then** recebe a
   recusa. O contrário também vale.

---

### User Story 3 — O setor consulta os documentos dos aptos (Priority: P1)

Rui abre **Formalização** e depois o 72/2026. Vê os aptos por Perfil, os documentos definidos de cada
um e a data da última exportação. Visualiza ou baixa um a um. No bolsista (Cenário B), isso basta.

**Why this priority**: resolve o acesso e a minimização, e serve sozinha aos processos pequenos.

**Independent Test**: um aceite com dois documentos definidos; visualizar, baixar e conferir a trilha.

**Acceptance Scenarios**:

1. **Given** 3 aceites, 1 indeferimento e 1 sem resposta, **When** Rui abre a página, **Then** vê os 3
   aceites.
2. **Given** documentos dentro e fora da definição, **When** Rui vê a pessoa, **Then** só os definidos
   aparecem.
3. **Given** o certificado da inscrição aproveitado por referência num item da convocação, os dois
   definidos, **When** Rui vê a pessoa, **Then** o arquivo aparece uma vez.
4. **Given** um documento, **When** Rui visualiza e depois baixa, **Then** a trilha tem *documento
   visualizado* e *download individual disponibilizado*.
5. **Given** a tela de 375 px, **When** a página abre, **Then** cabe sem rolagem horizontal.

---

### User Story 4 — O setor exporta, sabendo antes o que vai receber (Priority: P1)

Rui tem 40 aptos no 72/2026 (Cenário A). O fluxo é este:

1. Marca *Selecionar todos* e pede **Verificar e exportar**.
2. A verificação lê e confere os 200 arquivos e mostra *"Pacote completo: 40 pessoas, 200 documentos,
   290 MB"*.
3. Ele clica **Baixar pacote (40 pessoas)** e recebe o ZIP.

Se a verificação acha dois arquivos com problema, a tela diz, antes de qualquer download:

> *"Pacote parcial: 38 de 40 pessoas. Não incluídas: ‹protocolo› ‹nome› — arquivo indisponível;
> ‹protocolo› ‹nome› — arquivo diferente do conferido."*

Nesse caso, o botão diz **Baixar pacote parcial (38 pessoas)**.

**Why this priority**: tira o setor da pasta de rede montada à mão, e é o que exige a exceção à
FR-069 da `009`.

**Independent Test**: 40 aptos com 5 documentos. A verificação diz *completo*, o ZIP tem 40 pastas e
200 arquivos, o manifesto confere com os hashes, o registro guarda o hash do pacote, e nada sobra no
disco.

**Acceptance Scenarios**:

1. **Given** uma seleção de mais de uma pessoa, **When** Rui pede a verificação, **Then** a tela mostra:
   - primeiro o resultado (*completo* ou *parcial*);
   - o alcance (Edital, Perfis, pessoas);
   - por pessoa, os documentos e o tamanho;
   - as pessoas não incluídas, com o motivo;
   - o total.
   
   Nada é gravado além da trilha.
2. **Given** a verificação *parcial*, **When** Rui baixa, **Then** o ZIP contém exatamente as pessoas
   verificadas como incluídas. O nome do arquivo termina em `-parcial.zip`, e o manifesto traz o
   resultado no cabeçalho e uma linha por documento das pessoas não incluídas, com o motivo.
3. **Given** a verificação, **When** muda antes do download qualquer um destes, **Then** o download é
   recusado como verificação defasada, sem servir nada, e a tela oferece verificar de novo:
   - o desfecho de uma pessoa;
   - a designação do operador;
   - a versão da definição;
   - um arquivo ou hash;
   - a população excluída ou o motivo de uma exclusão.
   
   A revogação do papel ou da designação dá a recusa de autorização da matriz.
4. **Given** um comprovante adulterado, fabricado sem a chave do servidor, expirado ou emitido para
   outro servidor, **When** apresentado ao download, **Then** é recusado sem ler nenhum arquivo.
5. **Given** uma verificação sem nenhuma pessoa incluível, **When** termina, **Then** a tela explica, e
   não há botão de baixar.
6. **Given** uma pessoa só, **When** Rui pede **Exportar esta pessoa**, **Then**:
   - com tudo íntegro, o ZIP sai num clique;
   - com falha, a resposta é uma página com o motivo, e não um ZIP.
7. **Given** o recorte *Perfil A*, **When** exportado, **Then** só os aptos do Perfil A entram.
8. **Given** um POST com id de pessoa fora do alcance, **When** enviado, **Then** a operação inteira é
   recusada como inexistente.
9. **Given** uma verificação ou geração de Rui em andamento, **When** Rui pede outra, **Then** a segunda
   é recusada com *"Uma exportação sua já está em andamento"*.

---

### User Story 5 — O GPS não declara o que não aconteceu (Priority: P1)

Arquivo ausente, divergência, limite excedido, falha inesperada ou tempo-limite (Cenário F).

**Why this priority**: declarar disponibilizado o que não foi é o risco que o registro existe para
evitar.

**Independent Test**: num Edital de 5 aptos, apagar o arquivo de uma pessoa, corromper o de outra,
injetar uma exceção na geração e simular o tempo-limite.

**Acceptance Scenarios**:

1. **Given** um arquivo ausente, **When** visualizado ou baixado, nesta página ou nas páginas existentes
   da inscrição, da mesa e da convocação, **Then** a resposta é *"Arquivo indisponível"* e não 500, e a
   trilha registra.
2. **Given** a seleção acima do limite, **When** verificada, **Then** é recusada antes de ler qualquer
   arquivo, com o tamanho por pessoa para dividir.
3. **Given** uma exceção inesperada durante a geração, **When** ela ocorre, **Then**:
   - nada é servido;
   - nenhum registro de exportação é gravado;
   - o temporário deixa de existir, e a trava é liberada;
   - a tela diz *"A exportação não foi concluída. Nada foi baixado nem registrado."*;
   - a trilha grava *exportação interrompida*.
4. **Given** o worker morto pelo tempo-limite **durante a geração**, **When** isso ocorre, **Then** não
   há registro, a trava sai com a conexão, e o temporário some com o processo.
5. **Given** o worker morto **durante a transferência**, **When** isso ocorre, **Then**:
   - o registro, já gravado, continua dizendo só *"gerado e disponibilizado para download"*;
   - o ZIP recebido é inválido;
   - o operador pode exportar de novo.

---

### Edge Cases

- **Desfecho corrigido entre a verificação e o download.** É verificação defasada (FR-3689).
- **Arquivo trocado no disco entre a verificação e o download.** A geração reconfere o hash, e é
  verificação defasada (FR-3689, FR-3690).
- **Duas chamadas da mesma inscrição.** Vale a mais recente (FR-3670).
- **Item definido, mas *não se aplica* ou facultativo não apresentado.** A pessoa conta como completa
  (FR-3672).
- **Documento da convocação não conferido.** Não sai (FR-3671).
- **Definição alterada depois de uma exportação.** A exportação passada mantém a versão que aplicou
  (FR-3656).
- **Edital encerrado (`113`).** Segue o desfecho vigente (FR-3710).
- **Convocação anterior à `115`.** Só os documentos da inscrição definidos aparecem (FR-3670).
- **Mesma pessoa na comissão e no setor.** É permitido, com predicados independentes (FR-3664).
- **Nome com `/`, `..`, caracteres de controle, nome reservado do Windows ou acima de 80 caracteres.**
  É normalizado (FR-3712).
- **Duas chaves de requisito que viram o mesmo nome de arquivo depois da normalização.** Recebem sufixo
  determinístico (FR-3712).
- **Nome de pessoa começando com `=`, `+`, `-` ou `@`.** É neutralizado no manifesto (FR-3713).
- **Duas abas do mesmo operador.** A segunda operação é recusada (FR-3692).
- **A pessoa excluída por arquivo ausente tem o arquivo restaurado entre a verificação e o download.**
  O resultado mudou, e é verificação defasada (FR-3689b).
- **Designação revogada e concedida de novo entre os dois passos.** A designação é outra, e é
  verificação defasada (FR-3689b).
- **Chave do sistema trocada entre os dois passos.** O comprovante deixa de valer, e o operador
  verifica de novo (FR-3689a).

## Requirements *(mandatory)*

### Functional Requirements

#### A. A definição dos documentos para a formalização

- **FR-3653**: Cada Edital MUST ter uma **definição dos documentos para a formalização**: um conjunto de
  requisitos do próprio Edital, **de qualquer momento**, **vazio por padrão**. Nenhum documento MUST
  ficar disponível ao setor se o requisito dele não estiver na definição vigente.
- **FR-3654**: A definição MUST ser gravada pela base de gerir a comissão do Processo do Edital (a
  presidência, ou `comissao:gerir`), na unidade do Edital. Quem tem só o acesso da formalização MUST
  NOT gravá-la.
- **FR-3655**: A definição MUST ser append-only e versionada, com requisitos, **motivo obrigatório**
  (constraint e validação), autor, unidade de atuação e instante. A vigente é a mais recente. Cada
  exportação MUST gravar a versão que aplicou.
- **FR-3656**: Uma versão nova MUST valer para toda consulta e exportação **seguinte**, inclusive de
  pessoas de chamadas anteriores, e MUST NOT alterar o registro de exportações passadas.
- **FR-3657**: A definição MUST NOT ser conteúdo publicado: não entra no snapshot, no hash nem no PDF, e
  não exige Retificação. Ela MUST NOT criar exigência nem mudar momento, obrigatoriedade, recorte,
  conferência, desfecho ou classificação.
- **FR-3658**: A tela da definição MUST mostrar um aviso, sem impedir a gravação, ao marcar:
  - requisito com **recorte por modalidade**: *"Este documento é exigido só de candidatos de uma
    modalidade de reserva. Inclua-o só se o setor precisar dele para formalizar."*;
  - requisito **da inscrição**: *"Este documento foi pedido na inscrição. Se ele serve só à
    classificação, não o inclua."*
  
  Os dois avisos saem de dados que já existem (o recorte e o momento). Não há taxonomia nem
  classificação nova.
- **FR-3659**: Quando um item da convocação definido é atendido por referência a um documento da
  inscrição também definido, o arquivo MUST sair **uma vez**, pelo item da convocação.
- **FR-3660**: Os Editais existentes MUST começar com a definição vazia. Nenhuma migration MUST criar
  definição.
- **FR-3711**: O **histórico da definição** MUST ser visível, na tela da definição, a quem pode gravá-la
  e ao auditor. Ele mostra cada versão com autor, unidade, data, motivo e os requisitos acrescentados e
  retirados em relação à anterior. O servidor do setor MUST NOT vê-lo. Ele vê só os documentos
  disponíveis a ele.

#### B. O acesso do setor

- **FR-3661**: MUST existir o papel **Formalização** no catálogo da unidade, com uma capacidade só, a de
  acessar documentos para formalização. Ele MUST NOT ser concedido por padrão a nenhum papel existente,
  e é concedido e revogado pela gestão de acessos da `107`, sem mudança no modelo de vínculo.
- **FR-3662**: MUST existir a **designação para a formalização**, com pessoa, Edital, Perfis opcionais
  (vazio = todos), motivo, quem designou, unidade de atuação e instante. Ela é append-only, com
  revogação append-only e motivo.
- **FR-3663**: Designar e revogar MUST exigir `acesso:gerir` na unidade do Edital. A designação MUST ser
  recusada, com código próprio, sem o papel Formalização vigente na unidade do Edital, ou para quem
  designa (autodesignação). Mudar os Perfis é revogar e designar de novo.
- **FR-3664**: O predicado **pode acessar a documentação da formalização** MUST ser único para a página,
  cada arquivo, a verificação e a exportação. É verdadeiro quando, **na mesma requisição**:
  - o ator tem a capacidade do papel na unidade ativa;
  - a unidade ativa é a do Edital;
  - há designação vigente do ator no Edital, cobrindo o Perfil da pessoa;
  - a pessoa está apta (FR-3669).
- **FR-3665**: Nenhuma outra base MUST alcançar a página, os arquivos ou a exportação: presidência,
  `comissao:gerir`, alocação à conferência, `inscricao:consultar`, `matricula:exportar`,
  `acesso:gerir` ou auditoria. O predicado desta spec MUST NOT alcançar a conferência, os desfechos, a
  condução, a página de documentos da convocação da `115` nem o dossiê da inscrição.
- **FR-3666**: As recusas seguem a FR-3599 da `115` e o inventário da `033`:
  - escopo alheio, objeto inexistente, Perfil fora da designação, pessoa não apta e Edital sem
    designação do ator recebem a **recusa de inexistente**;
  - designação sem o papel recebe a **recusa de autorização**, nomeando o papel.
- **FR-3667**: A revogação do papel, a revogação da designação e a suspensão da pessoa MUST cortar o
  acesso na requisição seguinte. Revogar o papel MUST cortar todas as designações da pessoa.
- **FR-3668**: A presidência e `comissao:gerir` MUST ver, na condução, as designações vigentes, só para
  leitura. A designação e a revogação MUST ir para a trilha da unidade e para a do Edital.

#### C. População e conjunto documental

- **FR-3669**: A pessoa está **apta para formalização** quando o desfecho vigente da convocação vigente
  da **chamada mais recente** da inscrição, no Edital, é um dos que incluem (aceite ou regularização).
  A leitura MUST ser feita na hora.
- **FR-3670**: O conjunto de uma pessoa apta MUST ser formado pelos requisitos da definição vigente
  aplicáveis a ela:
  - **da convocação**: o item da lista da chamada mais recente (FR-3573 da `115`), pela apresentação
    julgada na conferência vigente *conforme*, resolvida em um passo (FR-3619 da `115`), com o hash
    conferido como esperado;
  - **da inscrição**: o documento enviado na inscrição, com o hash do envio como esperado.
- **FR-3671**: O documento da convocação sem conferência vigente *conforme* sobre a apresentação
  vigente MUST NOT sair. O da inscrição sai sem conferência, e a tela e o manifesto MUST dizê-lo:
  *"enviado na inscrição; sem conferência na convocação"*.
- **FR-3672**: As situações do item são *incluído*, *não se aplica*, *não apresentado*, *não
  conferido*, *indisponível* e *integridade*. Só as duas últimas tornam a pessoa incompleta.
- **FR-3673**: Documento fora da definição, de pessoa não apta, dados do Requerimento de Matrícula,
  notas, pareceres e recursos MUST NOT aparecer na página, na verificação, no pacote ou no manifesto.
- **FR-3674**: Um **seletor único** MUST compor o conjunto. Página, verificação e pacote MUST mostrar o
  mesmo conjunto.

#### D. A página Documentos para formalização

- **FR-3675**: A barra MUST mostrar **Formalização** a quem tem a capacidade. A página inicial lista só
  os Editais com designação vigente do ator.
- **FR-3676**: A página do Edital MUST listar os aptos do alcance, por Perfil e por nome, com:
  - protocolo e nome;
  - chamada e data do desfecho;
  - *"Última exportação: DD/MM, por ‹nome›"*, lida do histórico;
  - por documento: requisito, situação, *Visualizar* e *Baixar*.
  
  Ela MUST NOT mostrar CPF, contato, modalidade, nota ou classificação.
- **FR-3677**: *Visualizar* MUST ser a ação primária, `inline`, sem cache, com a cópia verificada da
  FR-053a da `009`. *Baixar* MUST ser secundária e individual, com o nome `‹protocolo›-‹requisito›.pdf`
  normalizado pela FR-3712, nunca o nome enviado.
- **FR-3678**: Edital sem definição, ou sem documento definido aplicável, MUST mostrar os aptos e dizer
  por quê não há documento, sem oferecer exportação.
- **FR-3679**: A página MUST mostrar o **histórico de exportações** do Edital no alcance do ator, com:
  - instante, autor e unidade;
  - alcance e resultado;
  - pessoas incluídas e não incluídas, com o motivo;
  - arquivos e tamanho;
  - hash do pacote.
- **FR-3680**: Os textos MUST seguir a linguagem simples da `069` e caber em 375 px. Nenhum texto MUST
  dizer *obtido*, *encaminhado*, *recebido*, *entregue*, *matriculado*, *matrícula efetivada*, *bolsa
  concedida*, *vinculado* ou *contratado* (FR-3610 da `115`).
- **FR-3681**: A página MUST ter **um** controle de recorte, o Perfil, e só com mais de um Perfil no
  alcance. Não há outro filtro, busca avançada ou painel.

#### E. A exportação controlada

- **FR-3682**: Três alcances, e nenhum outro, **sempre dentro de um Edital e do alcance do ator**:
  - **pessoa**;
  - **seleção** das pessoas marcadas;
  - **recorte**: todos os aptos do alcance, com Perfil opcional.
  
  A seleção MUST ir por POST, nunca na URL. Um id fora do alcance MUST recusar a operação inteira como
  inexistente.
- **FR-3683**: MUST NOT existir exportação de vários Editais, de quem não está apto, de documento fora
  da definição ou de Edital fora da designação. A lista MUST começar sem marcação.
- **FR-3684**: A exportação de **mais de uma pessoa** MUST começar por uma **verificação**. Ela lê cada
  arquivo do conjunto e confere o hash **sem montar pacote**, e mostra, nesta ordem:
  - o **resultado**: *completo* ou *parcial*, com quantas pessoas entram de quantas;
  - as pessoas **não incluídas**, com o motivo (*arquivo indisponível* ou *arquivo diferente do
    conferido*);
  - o alcance;
  - por pessoa, os documentos e o tamanho;
  - o total.
  
  A verificação MUST NOT gravar nada além da trilha. O botão de download MUST dizer *"Baixar pacote
  (N pessoas)"* ou *"Baixar pacote parcial (N pessoas)"*. Sem nenhuma pessoa incluível, não há botão.
- **FR-3685**: A exportação de **uma pessoa** MUST ser um clique sobre a lista dos documentos dela, sem
  verificação separada. Com tudo íntegro, a resposta é o ZIP. Com qualquer falha, a resposta MUST ser
  uma página com o motivo, e não um ZIP, e nenhum registro de exportação é gravado.
- **FR-3686**: O pacote MUST ser um ZIP sem compressão, com:
  - uma pasta por pessoa;
  - um arquivo por documento incluído;
  - o `manifesto.csv` na raiz.
  
  Os nomes seguem a FR-3712. As datas das entradas MUST ser as do envio. O arquivo baixado MUST se
  chamar `formalizacao-‹edital›-‹AAAAMMDD-HHMM›.zip`, ou `…-parcial.zip` quando parcial, sem dado
  pessoal.
- **FR-3687**: O manifesto MUST ter:
  - **um cabeçalho**: Edital, alcance, versão da definição, instante, autor, identificador da
    exportação e **resultado**, com *"N de M pessoas incluídas"*;
  - **uma linha por documento** de cada pessoa considerada, **incluídas e não incluídas**: protocolo,
    nome, Perfil, chamada, requisito, momento, situação, caminho no pacote (vazio se não incluído),
    SHA-256, instante do envio e, na convocação, da conferência.
  
  Ele MUST NOT ter CPF, contato, modalidade, nome original do arquivo nem motivo da conferência. A
  codificação segue a FR-3713.
- **FR-3688**: O pacote MUST ser montado num temporário **sem nome no sistema de arquivos**, legível só
  pelo processo. Ele MUST deixar de existir ao fim da resposta, na desconexão do cliente, na exceção ou
  na morte do processo. MUST NOT existir URL, cópia, cache ou link para ele depois. É servido como
  `attachment`, sem cache.
- **FR-3689**: O download de mais de uma pessoa MUST exigir o **comprovante da verificação**
  (FR-3689a) e MUST recompor a verificação inteira antes de servir (FR-3689b). Qualquer diferença MUST
  recusar o download como **verificação defasada**, sem servir nada e sem registro de exportação, e
  oferecer verificar de novo. **O ZIP servido é sempre exatamente o verificado.** O pacote não é
  guardado entre os dois passos (D-004).
- **FR-3689a**: O comprovante MUST ser **assinado pelo servidor**, com o mecanismo de assinatura do
  framework (HMAC com a chave do sistema e sal próprio da feature), e não um resumo simples.
  
  **O que ele vincula**:
  - versão do formato;
  - sujeito do ator e unidade ativa;
  - Edital e designação usada;
  - alcance, recorte e pessoas pedidas;
  - versão da definição;
  - resultado (*completo* ou *parcial*, N de M);
  - **resumo canônico do conteúdo verificado** (FR-3689b);
  - instante da emissão.
  
  **Validade: 15 minutos**, o tempo de ler o resultado e decidir. Ele não leva nome, CPF nem nome de
  arquivo, e vai no corpo do POST, nunca na URL.
  
  **No download, antes de ler qualquer arquivo**, MUST ser recusado:
  - o comprovante de assinatura inválida (adulterado ou fabricado), como *verificação inválida*;
  - o expirado, como *verificação expirada*;
  - o emitido para outro ator ou outra unidade, como *verificação inválida*.
  
  As autorizações MUST ser revalidadas por inteiro, pelo predicado da FR-3664, para cada pessoa. O
  comprovante prova que a verificação aconteceu, e não autoriza nada. Dentro da validade, ele pode ser
  usado mais de uma vez pelo mesmo ator, e cada uso é uma exportação registrada. Não há tabela de
  comprovantes.
- **FR-3689b**: O **resumo do conteúdo verificado** MUST cobrir o resultado inteiro:
  - as **pessoas incluídas**, com inscrição, convocação e chamada, e, por documento, a origem, o
    identificador e o hash esperado;
  - as **pessoas excluídas**, com inscrição, o documento causador e o **motivo codificado**
    (`INDISPONIVEL` ou `INTEGRIDADE`);
  - a versão da definição e a designação.
  
  No download, o servidor MUST reler os arquivos de **todas** as pessoas do alcance, inclusive das
  excluídas, recalcular o mesmo resumo e compará-lo. É defasada qualquer mudança:
  - no desfecho;
  - na designação, inclusive revogada e concedida de novo;
  - na versão da definição;
  - num arquivo ou hash;
  - na população excluída ou no motivo de uma exclusão.
- **FR-3690**: Cada arquivo MUST ter o hash conferido **na mesma leitura** que o copia, na verificação e
  na montagem.
- **FR-3691**: A verificação e a montagem MUST ser recusadas **antes de ler qualquer arquivo** quando a
  soma dos tamanhos gravados passar de `EXPORTACAO_DE_FORMALIZACAO_LIMITE_MB`. **Esse é um limite
  inicial, configurável, de 400 MB** (D-019), e não a capacidade da VM, que se valida na homologação. A
  recusa mostra o tamanho por pessoa, para dividir a seleção.
- **FR-3692**: MUST existir no máximo **uma verificação ou montagem em andamento por servidor**. A
  **trava consultiva de transação** do PostgreSQL usa uma classe fixa da feature e o resumo do
  identificador do servidor, e:
  - é tomada no início da transação da verificação ou da montagem, sem espera; ocupada, a operação é
    recusada com *"Uma exportação sua já está em andamento"*;
  - é liberada no commit, no rollback ou no fechamento da conexão, inclusive com o worker morto;
  - **não** cobre a transferência do ZIP, que acontece depois do commit;
  - não segura linha de tabela.
  
  Uma colisão do resumo entre dois servidores pode recusar sem motivo. É rara, o texto é o mesmo, e
  repetir resolve.
- **FR-3693**: Exportar MUST NOT alterar apresentação, conferência, desfecho, convocação, inscrição,
  definição ou Edital. A única escrita é o registro da exportação.

#### F. Falhas

- **FR-3694**: A pessoa com documento *indisponível* ou *integridade* MUST ficar **inteira** fora do
  pacote, sem pasta parcial. A verificação, o manifesto, o registro e o histórico MUST nomeá-la com o
  motivo.
- **FR-3695**: Arquivo ausente ou ilegível (`FileNotFoundError`, `OSError`) MUST ser tratado como
  *indisponível*, sem erro 500, na página desta feature **e** nas views de documento que já existem
  (inscrição, mesa e convocação). A resposta MUST ser *"Arquivo indisponível"*, e o evento vai para a
  trilha sem nome de arquivo.
- **FR-3696**: Hash divergente MUST gravar o evento de integridade existente e MUST NOT servir o
  arquivo.
- **FR-3697**: O registro da exportação existe só para pacote gerado, e o **resultado** é *completo* ou
  *parcial*. Verificação sem pessoa incluível, pessoa única com falha, verificação defasada e
  interrupção MUST NOT gravar registro de exportação. Elas aparecem na trilha (FR-3699).
- **FR-3698**: O registro MUST ser gravado depois de o pacote estar montado e antes de a resposta
  começar. Falha ou tempo-limite **durante a transferência** MUST NOT alterá-lo: ele afirma só que o
  pacote foi **gerado e disponibilizado para download**. Um ZIP truncado é inválido por construção, e o
  operador exporta de novo.
- **FR-3714**: Exceção inesperada na verificação ou na montagem MUST:
  - desfazer a transação, sem registro de exportação;
  - fechar o temporário e liberar a trava;
  - responder com a página *"A exportação não foi concluída. Nada foi baixado nem registrado."*, e não
    com erro 500 genérico;
  - gravar o evento *exportação interrompida* em transação própria, sem dado pessoal.
  
  A morte do worker pelo tempo-limite nessas fases tem o mesmo efeito no banco e no disco, sem a
  página.

#### G. Rastreabilidade

- **FR-3699**: Os eventos MUST ser estes, e nenhum outro afirma mais do que a evidência:

  | Evento | Quando | Agregado |
  |---|---|---|
  | **Documento visualizado** | arquivo servido `inline` | apresentação ou documento |
  | **Download individual disponibilizado** | arquivo servido como `attachment` | idem |
  | **Verificação de exportação** | verificação concluída, com resultado e contagens | Edital |
  | **Pacote gerado e disponibilizado para download** | registro gravado, antes da resposta | Edital |
  | **Exportação recusada** | verificação defasada, limite ou pessoa única com falha | Edital |
  | **Exportação interrompida** | exceção na verificação ou na montagem | Edital |
  | **Arquivo indisponível** / **Integridade** | falha | apresentação ou documento |
  | **Definição dos documentos gravada** | versão nova | Edital |
  | **Designação concedida** / **revogada** | gestão de acessos | Edital e unidade |
  
  Nenhum evento MUST levar nome de pessoa, nome de arquivo ou motivo de conferência.
- **FR-3700**: Cada pacote gerado MUST ter um **registro da exportação**, append-only por gatilho e por
  privilégio ausente, com:
  - Edital, designação e versão da definição;
  - alcance e recorte;
  - autor, unidade e instante;
  - resultado;
  - por pessoa: inscrição, convocação e situação, com motivo se não incluída;
  - por documento incluído: origem e hash;
  - quantidade, tamanho e SHA-256 do pacote.
  
  Só ids e hashes. A tabela MUST entrar em `TABELAS_APPEND_ONLY`.
- **FR-3701**: MUST NOT existir estado derivado por pessoa além do fato *"última exportação"*. Não há
  *obtida*, *encaminhada*, *recebida* nem máquina de estados de transferência.
- **FR-3702**: O auditor MUST ver os eventos, o histórico de exportações e o da definição, e MUST NOT
  abrir arquivo nem exportar.
- **FR-3703**: Nenhum log de aplicação, de servidor ou de erro MUST conter nome, CPF, nome de arquivo ou
  conteúdo. As URLs desta feature MUST conter só identificadores opacos.

#### H. Segurança do pacote

- **FR-3712**: Os nomes dentro do ZIP MUST ser montados **só com valores do sistema**: protocolo, nome
  da pessoa e chave do requisito. Nunca com o nome enviado pelo candidato. Cada componente MUST ser
  normalizado:
  - NFC;
  - sem caracteres de controle;
  - sem `/ \ : * ? " < > |`;
  - sem `.` ou `..` como componente;
  - sem ponto ou espaço inicial ou final;
  - sem nome reservado do Windows (`CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`);
  - no máximo 80 caracteres;
  - vazio vira `sem-nome`.
  
  O caminho de cada entrada MUST ter exatamente `‹protocolo› ‹nome›/‹requisito›.pdf`, relativo, com
  `/` como único separador e a marca UTF-8 do ZIP. **Colisões**:
  - entre pastas, são impossíveis, porque o protocolo é único;
  - entre arquivos da mesma pessoa, depois da normalização ou do corte, recebem `-2`, `-3`… na ordem
    do identificador do requisito.
  
  O manifesto registra o caminho final.
- **FR-3713**: O `manifesto.csv` MUST ser UTF-8 com BOM, RFC 4180. Toda célula que comece com `=`, `+`,
  `-`, `@`, tabulação ou retorno MUST ser prefixada com apóstrofo, contra injeção de fórmula ao abrir
  em planilha.

#### I. Limites e compatibilidade

- **FR-3704**: Esta feature MUST NOT criar cópia persistente de arquivo nem repositório (D-004).
- **FR-3705**: Esta feature MUST NOT mudar o comportamento nem os requisitos da `115` ou da `009`,
  com **duas exceções, e só elas**:
  - **revisão normativa**: a FR-069 da `009` e a FR-3606 da `115` recebem o texto aprovado da D-016,
    na T002 (FR-3706);
  - **correção funcional**: o tratamento de arquivo indisponível nas views existentes (FR-3695).
  
  Qualquer outra mudança nessas features é escopo novo, e não desta spec.
- **FR-3706**: A exceção à FR-069 da `009` e à FR-3606 da `115` MUST valer só para a exportação desta
  feature, nas condições das FR-3653, FR-3664, FR-3669 a FR-3674, FR-3682 a FR-3700, FR-3689a,
  FR-3689b e FR-3712 a FR-3714. A revisão dos textos, **aprovada em 04/11**, é a da D-016 e se aplica na T002.
- **FR-3707**: MUST NOT existir confirmação de recebimento, encaminhamento ativo, integração externa,
  aviso por e-mail ao setor nem geração assíncrona.
- **FR-3708**: Nenhuma coluna, índice ou unicidade nova MUST presumir que a unidade do ator é a do
  Edital (FR-3602 da `115`).
- **FR-3709**: A designação e a definição MUST ser por Edital, e não por Processo.
- **FR-3710**: O encerramento do Edital (`113`) MUST NOT fechar a página nem a exportação.

### Matriz de permissões

"404" é a recusa de inexistente; "403", a de autorização no escopo.

| Ator | Página da formalização | Visualizar e baixar | Verificar e exportar | Definir documentos | Histórico da definição | Designar e revogar | Documentos da convocação (`115`) | Conferir e desfechar |
|---|---|---|---|---|---|---|---|---|
| Formalização + designação, sem restrição | sim | sim, aptos | sim | 403 | 403 | 403 | 403 | 403 |
| Formalização + designação no Perfil A, pessoa do B | a pessoa não aparece | 404 | 404 | 403 | 403 | 403 | 403 | 403 |
| Formalização, sem designação no Edital | 404 | 404 | 404 | 403 | 403 | 403 | 403 | 403 |
| Designação vigente, papel revogado | 403, nomeando o papel | 403 | 403 | 403 | 403 | 403 | 403 | 403 |
| `acesso:gerir` | 403 | 403 | 403 | 403 | 403 | **sim, exceto a si** | 403 | 403 |
| Presidência da comissão | 403; vê as designações | 403 | 403 | **sim** | **sim** | 403 | sim (`115`) | sim (`115`) |
| `comissao:gerir` (Gestor) | 403; vê as designações | 403 | 403 | **sim** | **sim** | 403 | sim (`115`) | sim (`115`) |
| Membro alocado à conferência | 403 | 403 | 403 | 403 | 403 | 403 | sim, no alcance | confere |
| `inscricao:consultar`, `matricula:exportar` | 403 | 403 | 403 | 403 | 403 | 403 | 403 | 403 |
| Auditor | 403; vê a trilha e o histórico de exportações | 403 | 403 | 403 | **sim, só leitura** | 403 | 403 | 403 |
| Ator de outra unidade | 404 | 404 | 404 | 404 | 404 | 404 | 404 | 404 |

**Três funções, três donos:** a condução define **o quê**, a gestão de acessos define **quem**, e o
setor **exporta**. Quem acumula papéis tem a união das linhas, e cada acesso é decidido pelo seu
predicado.

### Key Entities

- **Definição dos documentos para a formalização** (nova, append-only, versionada): Edital, requisitos,
  motivo obrigatório, autor, unidade, instante.
- **Papel Formalização** (entrada nova no catálogo existente).
- **Designação para a formalização** e **revogação** (novas, append-only).
- **Registro da exportação** (novo, append-only): só para pacote gerado; resultado *completo* ou
  *parcial*.
- **Documento Exigido, Documento Submetido, Item da lista, Apresentação, Conferência, Convocação e
  Desfecho**: lidos, nunca escritos. **O Documento Exigido não muda.**

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1101**: No Cenário A, o setor exporta toda a documentação definida em **no máximo 4 gestos**:
  selecionar todos, verificar, ler o resultado e baixar. Hoje são cerca de 680.
- **SC-1102**: Em nenhum teste um documento fora da definição, de pessoa não apta ou de Perfil fora da
  designação aparece na página, na verificação, no pacote ou no manifesto.
- **SC-1103**: O desfecho corrigido de aceite para indeferimento tira a pessoa da próxima página,
  verificação e exportação, sem ação de ninguém.
- **SC-1104**: Toda URL e todo POST desta feature, tentados por cada linha da matriz fora do alcance,
  recebem a recusa da matriz.
- **SC-1105**: Com um arquivo ausente e um divergente em 5 pessoas:
  - a verificação diz *"Pacote parcial: 3 de 5 pessoas"* e nomeia as 2, com o motivo, **antes do
    download**;
  - o ZIP baixado tem as 3 e se chama `…-parcial.zip`;
  - o manifesto e o histórico repetem o resultado;
  - nenhuma resposta é 500.
- **SC-1106**: Depois de qualquer operação, com sucesso, recusa, exceção injetada, cliente desconectado
  ou processo encerrado, nenhum arquivo novo existe sob a raiz privada nem no temporário do processo, e
  a trava está livre.
- **SC-1107**: O SHA-256 de cada arquivo no pacote é igual ao do manifesto e ao esperado. O do pacote é
  igual ao do registro.
- **SC-1108**: Duas exportações do mesmo alcance, sem mudança, produzem entradas de documento
  idênticas byte a byte.
- **SC-1109**: No Cenário B, o setor visualiza e baixa sem exportar, e a trilha distingue os dois atos.
- **SC-1110**: Revogada a designação ou o papel, ou suspensa a pessoa, a requisição seguinte é recusada.
- **SC-1111**: **No CI**, a verificação e a montagem do Cenário A (200 arquivos de 1,5 MB) são
  **medidas e relatadas separadamente**. Cada uma termina em menos de 30 s, e o número de consultas não
  cresce com o número de pessoas. A **transferência não é medida no CI**, porque não há rede real. Este
  critério mede o código, e **não** a VM, que mede os três tempos (*Critérios para homologação*,
  item 5).
- **SC-1112**: Nenhuma tela desta feature diz *obtido*, *encaminhado*, *recebido*, *entregue*,
  *matriculado*, *bolsa concedida*, *vinculado* ou *contratado*.
- **SC-1113**: Em nenhum caso o operador recebe um ZIP cujo conteúdo difira do que a verificação lhe
  mostrou. Cada uma das cinco mudanças da FR-3689b entre os dois passos dá *verificação defasada*.
  Comprovante adulterado, fabricado, expirado, de outro ator ou apresentado depois da revogação é
  recusado sem ler arquivo (FR-3689a).
- **SC-1114**: Com nomes de pessoa e chaves de requisito hostis, como `../x`, `CON`, `=1+1`, controle,
  300 caracteres e duas chaves iguais depois da normalização:
  - nenhuma entrada do ZIP sai da pasta da pessoa;
  - nenhum nome se repete;
  - nenhuma célula do manifesto começa com caractere de fórmula.

## Assumptions

- A `115` está na `main` quando a implementação começar.
- PDFs de até 10 MiB. ZIP sem compressão.
- A geração é síncrona. O tempo-limite do gunicorn (120 s) vale para a requisição inteira, inclusive a
  transferência. O desenho **não** presume buffering do nginx nem liberação antecipada do worker
  (§5.2 do diagnóstico).
- A infraestrutura de produção é a da implantação recomendada, que ainda não foi ensaiada em VM.

## Proteção de dados (LGPD)

- **Necessidade**:
  - definição vazia por padrão, com motivo e histórico;
  - avisos para documento de reserva e da inscrição;
  - só aptos;
  - manifesto sem CPF, contato ou modalidade.
- **Segurança**:
  - papel e designação;
  - verificação antes do download;
  - reconferência;
  - temporário sem nome, limite, trava;
  - nomes saneados e manifesto neutralizado;
  - seleção por POST.
- **Responsabilização**: eventos distintos; registro com hash; definição e acesso com motivo e autor.
- **Transparência ao titular**: é dever do aviso de privacidade do Edital (pendência 3).
- **Risco residual aceito**: a condução pode incluir documento desnecessário. Ele é mitigado pelo
  padrão vazio, pelos avisos, pelo motivo obrigatório, pelo histórico visível ao auditor e pela versão
  gravada em cada exportação. Não é eliminado sem um catálogo ou classificador, que a decisão do
  usuário veda.
- **O que sai do controle do GPS**: depois do download, a custódia é do setor.

## Compatibilidade e conflitos com regras anteriores

| Regra | Conflito | Situação |
|---|---|---|
| **FR-069 da `009`** | proíbe lote e exportação | **Exceção estreita aprovada** (D-016); aplica-se na T002 |
| **FR-3606 da `115`** | reafirma a proibição | Mesma exceção aprovada; aplica-se na T002 |
| **FR-3595 da `115`** | único caminho ao arquivo da convocação | Continua sendo o da seleção. O predicado desta spec é disjunto |
| **FR-3610 da `115`** | veda *encaminhado* | Continua, e esta spec veda mais termos (FR-3680) |
| **FR-3615 da `115`** | nada se exclui | Continua. O pacote não é guardado |
| **FR-455 e FR-456 da `031`** | capacidade própria; arquivo não guardado | Molde seguido |
| **Gestão de acessos da `107`** | — | Ganha um papel e a tela de designação. O vínculo não muda |
| **Doutrina "escopo alheio = 404" (`033`)** | — | Mantida |
| **SC-016 da `009`** | a seleção verifica sem lote | Continua |

## Decisões

### D-001 — O GPS não é GED

**Decisão do usuário.** Nada guarda o que foi exportado.

### D-002 — Seleção e formalização são responsabilidades distintas

**Decisão do usuário.** O setor não confere nem desfecha (FR-3665).

### D-003 — Aceite não é vínculo efetivado

**Decisão do usuário.** Apto, disponibilizado e efetivado são fatos distintos.

### D-004 — Não duplicar documentos

**Decisão do usuário.** O pacote é montado das fontes e descartado.

### D-005 — Segurança e minimização

**Decisão do usuário.** Só o necessário à competência do setor.

### D-006 — O GPS continua multiunidade

**Decisão do usuário.** A unidade de atuação vai em cada linha nova.

### D-007 — Página restrita com exportação controlada (B + C); D como evolução

*Proposta.* A comparação está na §3 do diagnóstico.

### D-008 — População: o desfecho vigente da chamada mais recente, lido na hora

*Proposta.* A população da `031` não serve, porque inclui quem não respondeu (FR-3669).

### D-009 — A finalidade numa definição interna por Edital

**Aprovada pelo usuário em 04/11.** A marca no Documento Exigido foi descartada por três motivos (§4.2
do diagnóstico):

- falhava no documento só da inscrição;
- misturava obrigação com encaminhamento;
- impedia corrigir a favor da minimização.

**Rejeitados:** atributo num catálogo institucional (não existe, pela QI-3); taxonomia de finalidades;
inferir pelo recorte, que vira aviso; escolha pelo setor.

### D-010 — Quem define: a condução do processo

**Aprovada pelo usuário em 04/11.** A presidência ou `comissao:gerir`, que sabem para que pediram cada
documento.

### D-011 — Vigência da definição e chamadas anteriores

**Aprovada pelo usuário em 04/11.** A obrigação fica congelada na lista da `115`. O encaminhamento é
registrado em cada exportação, e uma correção de minimização vale na hora para todos.

### D-012 — Nem PDF nem Retificação

**Aprovada pelo usuário em 04/11.** A Retificação só cabe quando o setor precisa de documento que o
Edital não exigiu, porque aí muda a obrigação.

### D-013 — Acesso: papel no catálogo + designação, os dois pela gestão de acessos

**Aprovada pelo usuário em 04/11.** O papel dá:

- a barra sem consulta;
- a revogação de uma vez;
- o "negar por padrão".

A designação dá o recorte por Edital e Perfil. Os dois são concedidos por `acesso:gerir`, sem
autodesignação, e a presidência só vê. A única estrutura nova é a designação. O vínculo da `107` não
muda.

### D-014 — Alcance da exportação: pessoa, seleção, recorte

*Proposta.* Não há pacote do Edital, e a designação corta todo alcance. **Limite conhecido:** um
documento exigido de todos os Perfis, com setores distintos por Perfil, sai para cada setor só das
pessoas do alcance dele. Uma definição por setor fica para depois.

### D-015 — Terminologia dos eventos

*Proposta.* O GPS afirma só o que ele mesmo fez (FR-3699). Na geração síncrona, *gerado* e
*disponibilizado* são o mesmo ato. *Encaminhamento efetivo* e *recebimento confirmado* não têm
mecanismo, e por isso não têm palavra.

### D-016 — Revisão da FR-069 da `009` e da FR-3606 da `115`

**Aprovada pelo usuário em 04/11. Aplica-se na T002**, a primeira tarefa da implementação, e não
neste PR:

- a regra não deve anunciar uma exceção antes de existir o código que a cumpre;
- este PR atualiza só os artefatos da `117`, por pedido do usuário.

O motivo inicial, o conflito com o #369 ainda aberto, deixou de existir com o merge dele.

**FR-069 da `009`, redação aprovada:**

> **FR-069**: Cada documento DEVE poder ser aberto pela interface, exibido no navegador quando o
> formato permitir; baixar DEVE existir apenas como ação secundária individual. NÃO DEVE existir
> download em lote, exportação, planilha nem painel. ***Exceção única (`117`):*** *a exportação, pelo
> setor responsável pela formalização, com papel próprio e designação no Edital concedidos pela gestão
> de acessos, dos documentos que a condução definiu como necessários à formalização, só de quem está
> apto para formalização e dentro do alcance da designação, com verificação prévia, manifesto, limite,
> registro append-only e sem guarda do pacote. A exceção não alcança a consulta de inscrições, a
> seleção nem exportação de todos os inscritos.*

**FR-3606 da `115`, redação aprovada:**

> **FR-3606**: A visualização no navegador, sem cache, MUST ser o padrão. Baixar MUST existir só como
> ação secundária individual e registrada. MUST NOT existir download em lote, pacote, ZIP, planilha ou
> exportação de documentos da convocação **na condução e na página de documentos da convocação**. *A
> única exceção é a exportação da formalização da `117`, pela exceção da FR-069 da `009`.*

**Justificativa.** A exceção muda as quatro variáveis que tornavam o lote perigoso: a população, o
conteúdo, o ator e a finalidade. A proteção geral continua (§2.8 do diagnóstico). Cada arquivo leva a
nota *"revista pela `117` em ‹data da T002›, por decisão do usuário de 04/11/2026"*.

### D-017 — Sem estados derivados

*Proposta.* O histórico e a trilha bastam. O único dado por pessoa é *"última exportação"*.

### D-018 — Resultado visível antes do download, por verificação

*Ajustada na consolidação.*

**O problema.** A resposta HTTP do download é o ZIP: o navegador baixa o arquivo e não mostra página.
Dizer *parcial* só depois, no manifesto ou no histórico, deixaria o operador descobrir as exclusões ao
abrir o arquivo, se descobrir.

**A solução, sem assincronia: dois passos síncronos.**

- **A verificação** lê e confere todos os arquivos, sem montar pacote e sem guardar nada, e mostra o
  resultado na tela. Isso inclui as pessoas excluídas e o motivo.
- **O download** apresenta o comprovante assinado da verificação (D-024), remonta, reconfere e só
  serve se o resultado inteiro for o mesmo, inclusive as exclusões (FR-3689 a FR-3689b). Assim o
  operador sabe o que vai receber antes de receber, e o ZIP é sempre exatamente o que ele viu.

O resultado se repete no nome do arquivo (`-parcial`), no cabeçalho e nas linhas do manifesto e no
histórico.

**Custo.** Os arquivos são lidos duas vezes, em duas requisições, cada uma dentro do tempo-limite e do
limite de tamanho.

**Para uma pessoa só**, a verificação seria um passo a mais sem ganho: ou ela está completa e o ZIP
sai, ou não está e a resposta é uma página com o motivo (FR-3685).

**A atomicidade por pessoa continua.** Uma pasta incompleta nunca é servida (FR-3694).

**Rejeitados:**

- **recusar o pacote inteiro por um arquivo**, que bloquearia o setor por uma pessoa;
- **servir primeiro e avisar depois**, porque o operador não veria o aviso;
- **guardar o pacote entre os passos**, que contraria a D-004;
- **geração assíncrona**, que não é necessária para isso.

### D-019 — Limite inicial de 400 MB, a validar na VM; uma operação por servidor

**Aprovada pelo usuário em 04/11, ajustada na consolidação.** São dois números distintos:

- **o limite inicial**, configurável, 400 MB (FR-3691), que cobre o Cenário A (cerca de 300 MB);
- **a capacidade real da VM**, que só se mede nela (§5.4 do diagnóstico; homologação, item 5).

O desenho supõe o pior caso: o worker fica ocupado durante toda a transferência, e o tempo-limite de
120 s pode cortá-la. Não supõe buffering do nginx. **Se a medição não couber**, reduz-se o limite. Se
isso não bastar, a TI ajusta o proxy. **Geração assíncrona só por decisão nova do usuário.**

A trava (FR-3692) é **de transação**, e não de sessão. Assim ela não sobrevive a uma conexão
reaproveitada nem depende de liberação explícita. Ela cobre a verificação e a montagem, e não a
transferência.

### D-020 — Sem justificativa em texto livre

**Aprovada pelo usuário em 04/11.** O motivo fica na definição e na designação.

### D-021 — Confirmação de recebimento fora do MVP

**Aprovada pelo usuário em 04/11.**

### D-022 — Documento da inscrição sai sem conferência, e diz isso

*Proposta.* O documento da inscrição é imutável depois do envio, e o hash dele é a prova (FR-3671).

### D-023 — Nomes, caminhos e manifesto seguros

*Nova na consolidação.* O ZIP será aberto no computador do setor e o manifesto, numa planilha. Por
isso:

- os nomes vêm só de valores do sistema, normalizados, sem o nome enviado pelo candidato;
- todo caminho tem exatamente um nível;
- colisões recebem sufixo determinístico;
- células com caractere de fórmula são neutralizadas (FR-3712, FR-3713).

O nome e o protocolo da pessoa ficam na pasta e no manifesto, **aprovados pelo usuário**, e o CPF e o
contato não.

### D-024 — Comprovante da verificação assinado pelo servidor

*Ajuste da revisão independente (04/11).*

**O problema.** O plano devolvia um SHA-256 dos dados da verificação num campo oculto. Isso prova
consistência, e não origem: quem reconstruísse os valores fabricaria o resumo e pularia a verificação.

**A decisão: `django.core.signing`**, com HMAC sobre a chave do sistema e sal próprio da feature.

**Por que ele:**
- já está no framework;
- não exige tabela nem serviço;
- dá validade com `max_age`.

**O conteúdo e a validade** (15 minutos) estão na FR-3689a. O comprovante carrega o **resumo**, e não o
conteúdo verificado: o servidor recompõe tudo no download e compara (FR-3689b). Assim o campo é
pequeno, e nada que o cliente mande é tomado como dado.

**O comprovante prova que a verificação aconteceu, e não autoriza.** As autorizações são revalidadas no
download.

**Rejeitados:**
- **resumo simples**: fabricável;
- **tabela de verificações**: daria uso único, mas é mais uma tabela append-only e mais um estado,
  quando repetir um download válido equivale a clicar de novo;
- **guardar o pacote entre os passos**: contraria a D-004.

**Efeito colateral aceito.** Trocar a chave do sistema invalida os comprovantes em aberto. O operador
verifica de novo.

## MVP e o que fica para depois

**MVP**: as US1 a US5, com o tratamento de arquivo indisponível nas views existentes. O primeiro corte
demonstrável é US1 a US3, que atende o Cenário B. O Cenário A exige a US4.

| Fica para depois | Quando |
|---|---|
| Aviso de quem deixou de estar apto depois de exportado | se o setor relatar caso real |
| Geração assíncrona | só por decisão do usuário, se a validação na VM não couber reduzindo o limite |
| Definição por setor no mesmo Edital | se um Edital real misturar setores |
| Confirmação de recebimento | se o controle pedir (D-021) |
| Encaminhamento a sistema externo | se a TI demonstrar capacidade |
| Setor de outra unidade | com o MAT-09 |

## Estratégia de testes

| Camada | O quê | Requisitos |
|---|---|---|
| Unidade | seletor do conjunto: desfechos, sucessões, chamadas, momentos, deduplicação, situações, versão da definição | FR-3653, FR-3659, FR-3669 a FR-3674 |
| Unidade | normalização de nomes e caminhos, colisões, neutralização do CSV | FR-3712, FR-3713, SC-1114 |
| Integração | definição: vazia, motivo, versões, avisos, histórico, snapshot intacto | FR-3653 a FR-3658, FR-3660, FR-3711 |
| Integração | acesso: papel, designação, autodesignação, presidência recusada, revogações, suspensão, append-only | FR-3661 a FR-3668 |
| Integração | verificação e download: resultado, parcial, defasada, pessoa única, recorte, POST forjado, limite | FR-3682 a FR-3691, FR-3694, FR-3697, SC-1105, SC-1113 |
| Integração | trava: segunda operação recusada; liberada no commit, no rollback e na conexão fechada | FR-3692 |
| Integração | comprovante: adulterado, fabricado (resumo sem assinatura, outro sal), expirado, de outro ator ou unidade, depois da revogação do papel e da designação, reusado dentro da validade | FR-3689a, SC-1113 |
| Integração | correspondência: desfecho, designação, definição, arquivo ou hash, excluído restaurado, motivo trocado | FR-3689b, SC-1113 |
| Integração | falhas: ausente, divergente, exceção injetada, temporário removido, registro intacto | FR-3688, FR-3695, FR-3696, FR-3698, FR-3714, SC-1106 |
| Regressão | arquivo ausente nas views de inscrição, mesa e convocação | FR-3695 |
| Interface | matriz inteira por URL e POST; 375 px; vocabulário; CSP | SC-1104, SC-1112 |
| Banco | `TABELAS_APPEND_ONLY` + 4 | FR-3655, FR-3662, FR-3700 |
| Desempenho | consultas constantes; verificação e montagem do Cenário A medidas e relatadas separadamente, menos de 30 s cada, no CI; transferência só na VM | SC-1111 |
| Navegador | Cenários A, E e F | — |

Contra PostgreSQL (`make test-pg`). **O tempo-limite e a transferência na VM não são testes de CI**:
são o item 5 da homologação.

## Critérios para homologação

1. A FR-069 da `009` e a FR-3606 da `115` foram revistas na T002. A `115` está na `main` desde 04/11.
2. `make lint check test-pg` verde, com o grupo `navegador`.
3. Demonstração dos seis cenários do quickstart, com capturas a 1280 px e a 375 px.
4. Um servidor do Registro Acadêmico ou da Coordenação UAB exporta num Edital de homologação e confirma
   que pastas e manifesto servem ao setor. Critério **humano**.
5. **Validação de capacidade na VM** (§5.4 do diagnóstico), pela TI. Ela mede, com um pacote no limite
   configurado:
   - a verificação, a montagem e a transferência, **cada uma em separado**, esta a um operador da rede
     do setor;
   - o uso do `/tmp` e do disco do nginx com duas exportações simultâneas;
   - o tempo-limite forçado.
   
   O limite de produção é o que a medição sustentar, e não necessariamente 400 MB.

## Pendências do usuário

**Bloqueia a implementação:** nada. O PR #369 foi mergeado em 04/11.

**Bloqueia o uso em produção, e não a implementação:**

1. A validação de capacidade na VM (homologação, item 5).
2. A homologação humana com um setor (item 4).
3. **O aviso de privacidade do Edital**, que diz ao candidato que os documentos necessários à
   formalização são disponibilizados ao setor competente. É texto institucional, da área de proteção de
   dados.

**Registradas, sem escopo aqui:** MAT-09; QI-4; §10.5 do complemento; Alternativa D.
