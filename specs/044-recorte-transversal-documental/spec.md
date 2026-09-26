# Feature Specification: Recorte transversal do documento exigido

**Feature Branch**: `claude/044-recorte-transversal-documental`

**Created**: 2026-09-25

**Status**: Draft

**Input**: Decisão do usuário em 25/09/2026, que aceitou as recomendações de
[`doc/decisao-recorte-documental.md`](../../doc/decisao-recorte-documental.md) (D1 a D5). Evidência:
o [estudo de esforço](../../doc/estudo-esforco-de-cadastro-2026-09-21.md) §5.9 e §15, o
[achado do portal](../../doc/achado-documento-condicional-no-portal.md) (#160) e a
[conferência do envio e da análise](../../doc/conferencia-envio-e-analise-documental.md) (#165).

> **Faixa de identificadores.** Abre em **FR-700**, **SC-260** e **UX-080**. O teto medido em
> 2026-09-25, em todas as worktrees (`git worktree list`), era 650 para os requisitos funcionais, 236
> para os critérios de sucesso e 66 para os de interface. Os dois primeiros são da
> `043-duplicar-perfil`, que ainda não está na `main`, e por isso vão escritos por extenso: citados
> como identificador, reprovariam o teste de citações nesta árvore. A faixa **não** começa no número
> seguinte porque a `043` está sendo escrita em paralelo, em outra worktree, e ainda cresce. A folga
> de ~50 requisitos, ~24 critérios e ~14 de interface é para ela não colidir com esta. O teste só
> veria a colisão no merge, quando as duas specs chegassem à mesma árvore. As **decisões** reiniciam
> em `D-001`. As da decisão de 25/09 são citadas como *D1*, *D1a* … *D5*, sem hífen, e não são
> decisões desta feature.

> **Teto proporcional.** São duas capacidades e nenhuma a mais: **uma forma nova de recorte** do
> Documento Exigido e **a lista gravada no envio**. A condição sobre o candidato (sexo, idade,
> vínculo), a aplicação em lote e a submodalidade ficam **fora**, por decisão do usuário (§3).

---

## 1. O problema, medido

**O Edital diz "todo candidato PcD"; o produto só sabe dizer "o PcD deste Perfil".** O recorte do
Documento Exigido aponta uma Modalidade pela identidade, e cada Perfil tem as suas Modalidades. No
140/2025, com 16 Perfis, dizer com fidelidade o item 5.5 custaria **7 × 16 = 112 linhas** de
documento (estudo, §5.9). O operador fez o que a tela permite: deixou "todas as modalidades" e
escreveu a condição na instrução. O documento publicado saiu com **nove obrigatórios marcados
"(facultativo)"**, o laudo médico do PcD entre eles.

**Quando o operador tenta o atalho, o ato publicado e a regra aplicada divergem.** No Edital
903/2026 (conferência, #165), o laudo ficou com o recorte "Todos os Perfis" + "C1 · PcD":

| Onde | O que disse sobre o laudo |
|---|---|
| Documento publicado | *"Dos candidatos concorrentes na modalidade Pessoas com Deficiência"*, sem Perfil |
| Portal, inscrição no C2 como PcD | não pediu; o candidato enviou só com a identidade |
| Mesa, inscrição no C2 | não listou, nem como "não apresentado" |
| Analista que leu o documento publicado | indeferiu **por um documento que o sistema nunca pediu** |

A #161 **conteve** a divergência: esse recorte não se publica mais. Mas o atalho não existe, e as
112 linhas continuam sendo a única forma fiel.

**A análise recalcula a lista, e não lê o que foi pedido.** A Mesa distingue só "com arquivo" de
"não apresentado". O documento que não se aplica **some**, e com ele o que o portal dispensou por
erro. Nada na inscrição enviada registra o que foi pedido. A Mesa refaz o recorte sobre a versão
aceita, e por isso herda o erro. A Constituição pede o contrário: *"O sistema DEVE reproduzir os
documentos exigidos para cada Inscrição."*

**O que o recorte por código resolve, contado no Edital original.** O item 5.5 do 140/2025
condiciona **sete** documentos à modalidade e **dois** a atributos do candidato. Relidos um a um:

| Documento do 5.5 | Condição do Edital | Com esta feature |
|---|---|---|
| h-I laudo médico · h-II autodeclaração PcD | "quem se inscrever como PcD" | **fiel**: PcD em todos os Perfis, obrigatório |
| i-I autodeclaração étnico-racial | "quem se inscrever como PPI" | **fiel**: PPIQ em todos os Perfis, obrigatório |
| k autodeclaração transgênero e travesti | "quem se inscrever como PTT" | **fiel**: PTT em todos os Perfis, obrigatório |
| i-II declaração da comunidade · i-III declaração da Funai | "apenas para candidato autodeclarado indígena" | **mais estreito, não fiel**: PPIQ em todos os Perfis, facultativo com instrução |
| m declaração de pertencimento quilombola | "quem se inscrever como Quilombola" | idem: Quilombola é **submodalidade** de PPIQ |
| e serviço militar · l declaração da chefia | sexo e idade · servidor do Ifes | **fora** (D2): condição sobre o candidato |

**As 112 linhas viram 7**, mas a fidelidade alcança **quatro** dos nove documentos que saíram como
facultativos, e não os sete que o estudo supunha. Os três de submodalidade deixam de ser oferecidos a
todo candidato e passam a ser oferecidos só a quem concorre em PPIQ. Continuam, porém, facultativos,
porque o código de PPIQ não distingue o indígena do quilombola. É o limite E7 do estudo
(submodalidade), e esta feature o registra sem resolvê-lo.

## 2. A decisão que esta feature cumpre

Tomada pelo usuário em 25/09/2026. Esta spec a **cita e não a rediscute**. Os detalhes e as
alternativas pesadas estão no [documento da decisão](../../doc/decisao-recorte-documental.md).

- **D1.** A Modalidade é identificada entre Perfis pelo **código**, que já é único no Perfil e
  estrutural (não se retifica). Um Documento Exigido pode apontar "a Modalidade de código X em todos
  os Perfis". Na publicação, um IMPEDE exige que o mesmo código tenha a **mesma denominação** em
  todos os Perfis. A regra cobre só a identidade, nunca percentual ou fundamento, porque a cota é por
  Perfil.
- **D1a.** O recorte transversal não alcança a ampla concorrência: é proibido para o código da
  Modalidade declarada ampla.
- **D2.** A condição sobre o candidato fica fora. As duas correções pequenas (a instrução chegar à
  Mesa; o facultativo manter a marca na Revisão do portal) vão para a fila das diretas.
- **D3.** O recorte exato Perfil × Modalidade continua existindo como escape, sem exceção negativa.
  A combinação que a #161 recusa continua recusada, e a mensagem ganha a saída "use a modalidade em
  todos os Perfis".
- **D4.** No envio, a inscrição grava a lista dos documentos exigidos, com a razão de cada um. A
  Mesa e a consulta administrativa passam a ler essa lista, em vez de recalculá-la.
- **D5.** Esta spec faz só o recorte transversal e a lista gravada.

## 3. O que esta feature NÃO é

- **Não é condição sobre o candidato.** Sexo, idade e vínculo continuam sem forma estruturada (D2).
  O documento "só para servidores" continua sendo o facultativo com instrução.
- **Não é submodalidade.** "Só para o indígena", dentro de PPIQ, não ganha forma. Ver §1.
- **Não é aplicação em lote.** Nada aqui copia conteúdo para N Perfis. A `043-duplicar-perfil` e as
  specs de propagação em massa são outras.
- **Não move a Modalidade para o Edital.** A Modalidade, o percentual e o fundamento continuam
  sendo de cada Perfil. O recorte transversal diz só **a qual** Modalidade de cada Perfil o documento
  se refere.
- **Não é juízo por documento na Mesa.** A conclusão continua sendo da inscrição inteira. O que muda é
  o que a Mesa **mostra**: cada documento com o estado e a razão.
- **Não corrige o resumo público para o recorte exato.** Hoje o "O que mudou" descarta a mudança de
  Perfil e de Modalidade do Documento Exigido. Esse defeito já existe e está na fila das diretas.
  Aqui se exige só que o campo **novo** não o repita (`FR-721`).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Exigir um documento de toda a modalidade, numa linha só (Priority: P1) 🎯 MVP

Quem compõe o Edital 140/2025 está na etapa de Documentos. Os 16 Perfis já têm as Modalidades AC,
PPIQ, PcD e PTT. Para o laudo médico, em "Exigido apenas da modalidade", a lista oferece, antes dos
pares Perfil × Modalidade, uma opção por código: *"Pessoas com Deficiência (PcD) — em todos os
Perfis que a têm (16 de 16)"*. A pessoa a escolhe e marca o laudo como obrigatório. Faz o mesmo com
os outros seis documentos. São sete linhas, e não 112.

Publicado o Edital, o documento publicado traz um grupo *"Dos candidatos concorrentes na modalidade
Pessoas com Deficiência:"* com o laudo e a autodeclaração, **obrigatórios**. No portal, o cartão de
cada um dos 16 Perfis diz *"Se concorrer em Pessoas com Deficiência, também: Laudo médico…"*, e a
inscrição de um candidato PcD em qualquer Perfil exige o laudo para enviar.

**Why this priority**: é a capacidade que falta. Sem ela, a única forma fiel é repetir o documento
por Perfil, e o operador escolhe entre 112 linhas e publicar um obrigatório como facultativo.

**Independent Test**: pela interface administrativa, compor um Edital com dois Perfis, C1 (AC, PcD,
PPIQ) e C2 (AC, PcD), e o laudo recortado como "PcD em todos os Perfis", obrigatório. Publicar. No
documento publicado, o laudo aparece num grupo só, o da modalidade. No portal, os cartões de C1 e C2
anunciam o laudo para PcD. Um candidato PcD no C2 não consegue enviar sem o laudo, e consegue depois
de anexá-lo.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração cujos Perfis C1 e C2 têm Modalidade de código `PcD` com a mesma
   denominação, **When** quem compõe abre o recorte de um Documento Exigido, **Then** a lista oferece
   "PcD em todos os Perfis", com a denominação, o código e quantos Perfis a têm, separada dos pares
   Perfil × Modalidade.
2. **Given** o laudo recortado como "PcD em todos os Perfis" e o Edital publicado, **When** um
   candidato se inscreve no C2 e escolhe PcD, **Then** a lista de documentos inclui o laudo como
   obrigatório, e o envio é recusado enquanto ele faltar, na tela e no servidor.
3. **Given** o mesmo Edital, **When** um candidato escolhe AC em qualquer Perfil, **Then** o laudo não
   é pedido a ele.
4. **Given** o mesmo Edital, **When** o documento publicado é gerado, **Then** o laudo aparece uma vez,
   sob *"Dos candidatos concorrentes na modalidade Pessoas com Deficiência:"*, sem nome de Perfil.
5. **Given** um Edital cujo C1 declara a Modalidade `AC` como ampla concorrência, **When** quem compõe
   abre o recorte, **Then** a opção "AC em todos os Perfis" não é oferecida. Se o conteúdo a trouxer
   por outro caminho, a gravação é recusada com o motivo.
6. **Given** o C1 com `PcD` denominada "Pessoas com Deficiência" e o C2 com `PcD` denominada "PcD",
   e um documento recortado como "PcD em todos os Perfis", **When** o Edital vai à publicação,
   **Then** a Revisão mostra um IMPEDE que nomeia o código, as duas denominações e os Perfis de cada
   uma.
7. **Given** um documento recortado como "Todos os Perfis" + "C1 · PcD", com `PcD` também no C2,
   **When** o Edital vai à publicação, **Then** o IMPEDE da #161 continua, e a mensagem oferece três
   saídas: declarar o Perfil C1, repetir o documento por Perfil, **ou usar "PcD em todos os
   Perfis"**.

---

### User Story 2 — Quem analisa vê o que foi pedido, e o que não se aplicava (Priority: P1)

O Bruno se inscreve no C2 como PcD e envia com a identidade e o laudo. No envio, a inscrição grava
a lista do que foi pedido a ele: a identidade, *pedida de todos os candidatos*; o laudo, *pedido de
quem concorre em PcD, em todos os Perfis*; a autodeclaração étnico-racial, que **não se aplica**,
porque é *pedida só de quem concorre ao C1 em PPIQ*.

Na Mesa, o analista vê as três linhas, cada uma com o estado e a razão: *apresentado*, *apresentado*,
*não se aplica*. Na inscrição da Ana (C1, AC), o laudo aparece como **não se aplica — pedido só de
quem concorre em PcD**. O analista não precisa conhecer o Edital de cor para saber o que se esperava
de cada um.

**Why this priority**: é o que impede o erro do 903 de chegar ao indeferimento. Sem a lista gravada,
qualquer mudança de recorte, inclusive esta, muda retroativamente a leitura das inscrições enviadas.

**Independent Test**: com o Edital da US1 e duas inscrições enviadas pelo portal (AC no C1, PcD no
C2), abrir cada uma na Mesa e na consulta administrativa. Todo Documento Exigido da versão aceita
aparece em cada inscrição, com um dos três estados e a razão. Depois, publicar uma Retificação que
muda o recorte do laudo e reabrir as duas: nada muda.

**Acceptance Scenarios**:

1. **Given** um candidato que envia a inscrição, **When** o envio é aceito, **Then** a inscrição
   passa a guardar, para **cada** Documento Exigido da versão aceita, se ele foi pedido como
   obrigatório, pedido como facultativo ou não se aplicava, e a razão (o recorte que o incluiu ou o
   excluiu).
2. **Given** uma inscrição enviada, **When** o analista a abre na Mesa, **Then** cada documento
   aparece num de três estados, *apresentado*, *não apresentado* ou *não se aplica*, com a razão, e o
   facultativo não apresentado se distingue do obrigatório.
3. **Given** uma inscrição enviada, **When** uma Retificação posterior muda o recorte de um documento,
   **Then** a Mesa, a consulta administrativa e a inscrição enviada no portal continuam mostrando a
   lista gravada no envio, sem nenhuma diferença.
4. **Given** a consulta administrativa "Inscrições recebidas", **When** o Gestor a abre, **Then** a
   contagem "recebidos de esperados" de cada inscrição enviada sai da lista gravada, e não de recálculo.
5. **Given** uma inscrição ainda em rascunho, **When** o candidato troca de modalidade, **Then** a
   lista de documentos continua sendo a da versão vigente. Nada é gravado antes do envio.

---

### User Story 3 — Retificar o recorte sem perder o que já foi pedido (Priority: P2)

O Edital 140/2025 foi publicado antes desta feature, com o laudo "facultativo" para todos. Uma
Retificação troca o recorte para "PcD em todos os Perfis" e o torna obrigatório. O resumo público "O
que mudou" diz isso em palavras, como diz toda alteração: *Documento exigido "Laudo médico" —
Modalidade em todos os Perfis — alterado*, e o mesmo para a obrigatoriedade. Quem quer o valor abre o
documento da Retificação, que está na mesma linha do histórico. As inscrições já
enviadas continuam com o que lhes foi pedido. As que forem enviadas depois da Retificação já exigem o
laudo.

Mais tarde, alguém tenta renomear "Pessoas com Deficiência" para "Pessoa com Deficiência" só no
Perfil LP03. A Retificação é recusada até a denominação mudar nos 16 Perfis no mesmo ato.

**Why this priority**: o recorte é retificável, e quem mais precisa dele são os Editais já publicados
com o "facultativo com instrução". Mas a US1 e a US2 entregam valor sem esta.

**Independent Test**: sobre um Edital publicado com um documento "facultativo para todos", com a
condição na instrução, publicar pela interface uma Retificação que troca o recorte dele para
transversal e o torna obrigatório. O resumo público nomeia as duas mudanças, e as inscrições enviadas
antes não mudam na Mesa.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** uma Retificação acrescenta, remove ou troca o recorte
   transversal de um Documento Exigido, **Then** o "O que mudou" público lista essa alteração: o
   documento, pelo nome, e o campo, por rótulo do domínio, nunca por identificador interno.
2. **Given** um documento recortado como "PcD em todos os Perfis", **When** uma Retificação muda a
   denominação de `PcD` em um Perfil só, **Then** a Retificação é impedida, e a mensagem nomeia os
   Perfis que ficaram com a denominação antiga.
3. **Given** o mesmo documento, **When** a Retificação muda a denominação de `PcD` em todos os Perfis,
   **Then** ela passa, e o documento publicado da nova versão traz o grupo com a denominação nova.
4. **Given** um documento transversal por `PcD`, **When** uma Retificação declara como ampla, em algum
   Perfil, a Modalidade de código `PcD`, **Then** a Retificação é impedida (D1a).
5. **Given** um documento transversal por `PcD`, **When** uma Retificação remove `PcD` de todos os
   Perfis, **Then** a Retificação é impedida, porque o documento ficaria inalcançável. Se sobrar ao
   menos um Perfil com `PcD`, ela passa.

---

### User Story 4 — Edital e inscrição anteriores à feature (Priority: P2)

O Edital 903/2026 foi publicado antes da #161 e desta feature. O Bruno enviou a inscrição no C2 como
PcD sem o laudo, e não há lista gravada para ela. Quando o analista abre essa inscrição, a Mesa
reconstrói a lista a partir da versão aceita. Ela **diz** que a lista é reconstruída, e não gravada.
E marca o laudo: *não pedido pelo portal nesta inscrição, mas o Edital publicado o exigia de todo
candidato em Pessoas com Deficiência*.

**Why this priority**: as inscrições antigas continuam em análise por meses. Sem uma leitura definida
para elas, a Mesa teria duas regras sem dizer qual está usando.

**Independent Test**: com uma inscrição enviada antes da feature (sem lista gravada), abrir a Mesa e a
consulta administrativa. A lista aparece, marcada como reconstruída. No cenário do 903, o laudo
aparece com a divergência nomeada. O documento publicado do 903 continua byte a byte o mesmo.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada antes desta feature, **When** o analista a abre, **Then** a lista
   é reconstruída a partir da versão aceita pela regra de aplicabilidade, com os três estados e a
   razão, e a tela diz que ela é reconstruída.
2. **Given** essa inscrição sob uma versão com o recorte "Todos os Perfis" + Modalidade de um
   Perfil, com Modalidade de mesma denominação no Perfil da inscrição, **When** a Mesa a mostra,
   **Then** o documento aparece como *não pedido pelo portal, exigido pelo Edital publicado*, e não
   some.
3. **Given** qualquer Edital publicado antes desta feature, **When** o sistema passa a ter o recorte
   transversal, **Then** nenhum documento publicado é regenerado, e nenhuma inscrição antiga ganha
   uma lista escrita depois do envio como se fosse do envio.

---

### Edge Cases

Cada caso abaixo é requisito, e a rastreabilidade o cobra como os `FR-`.

- **Código presente em só alguns Perfis.** O documento vale nos Perfis que têm a Modalidade daquele
  código, e nos outros não se aplica. O grupo publicado *"Dos candidatos concorrentes na modalidade
  X"* continua verdadeiro, porque só alcança quem pode concorrer em X. A opção de recorte diz em
  quantos Perfis ele vale (`UX-080`).
- **Código presente num Perfil só.** É equivalente ao recorte exato, e é permitido. Não se acusa
  nada.
- **Código que nenhum Perfil tem.** O documento seria inalcançável: a gravação é recusada, como já é
  recusado o recorte exato que aponta Modalidade inexistente.
- **Perfil acrescentado depois, por composição, por Retificação ou por duplicação (`043`).** Se ele
  tiver a Modalidade do código, o documento transversal passa a valer nele sem nenhuma linha nova.
  Fica registrado, para a `043`, que um documento transversal não é *restrito ao Perfil de origem*:
  esta spec não cobra nada da outra.
- **"Partir de um Edital anterior".** O recorte transversal é copiado pelo código. Se o Edital novo
  não tiver Perfil com aquele código, a publicação o acusa como inalcançável. Nada é remapeado em
  silêncio.
- **Mesmo código com denominações diferentes, e nenhum documento transversal por ele.** Não é
  acusado (`D-001`). Um Edital que não usa o recorte transversal não afirma identidade nenhuma.
- **Denominação que difere só em maiúscula ou acento.** É diferença, e o IMPEDE acusa (`D-005`). O
  documento publicado imprime uma denominação só no grupo, e não pode escolher entre duas.
- **Recorte transversal com Perfil declarado, ou com Modalidade exata.** É recusado na gravação: o
  recorte tem exatamente uma das cinco formas (`D-006`).
- **Documento transversal facultativo.** É permitido. Sai como *"(facultativo)"* dentro do grupo da
  modalidade, e é oferecido só a quem concorre nela.
- **Candidato sem modalidade escolhida.** O documento transversal não se aplica a ele, como já não se
  aplica o recorte exato.
- **Modalidade declarada ampla em um Perfil e não em outro, com o mesmo código.** O recorte
  transversal por esse código é proibido: basta um Perfil a declarar ampla (D1a).
- **Duas Retificações seguidas sobre o recorte, com inscrições enviadas entre elas.** Cada inscrição
  guarda a lista do seu envio. A Mesa nunca combina duas versões.
- **Envio concorrente com a publicação de uma Retificação.** A lista gravada é a da versão que o
  próprio envio registra como aceita, e nunca a de outra (`FR-714`).
- **Reenvio do mesmo envio (duplo clique).** Não produz segunda lista. A idempotência do envio cobre a
  lista gravada.
- **Inscrição anterior à feature sob recorte que hoje seria recusado.** A Mesa nomeia a divergência
  (`FR-727`), mas **não** decide nada por quem analisa. O parecer continua sendo do analista.

## Requirements *(mandatory)*

### O recorte

- **FR-700**: O Documento Exigido DEVE admitir uma quinta forma de recorte, além das quatro
  existentes (todos; Perfil; Perfil × Modalidade; "Todos os Perfis" + Modalidade de um Perfil, que a
  #161 recusa na publicação): **a Modalidade de um código, em todos os Perfis que a têm**. O código é
  o da Modalidade, único no Perfil e estrutural.
- **FR-701**: Um documento com recorte transversal DEVE se aplicar a uma inscrição se, e somente se, a
  Modalidade escolhida pela inscrição tiver o código do recorte. Perfil e identidade da Modalidade
  não entram na decisão.
- **FR-702**: O recorte transversal DEVE ser exclusivo: um documento que o declara NÃO PODE declarar
  também Perfil nem Modalidade exata. A gravação que os combinar DEVE ser recusada com o motivo
  (`D-006`).
- **FR-703**: O recorte transversal NÃO PODE apontar código que nenhum Perfil do Edital tenha. A
  gravação e a publicação DEVEM recusá-lo como documento inalcançável.
- **FR-704**: O recorte transversal NÃO PODE apontar o código de uma Modalidade declarada como ampla
  concorrência em **qualquer** Perfil do Edital (D1a). A recusa DEVE acontecer na gravação e, porque a
  declaração de ampla é retificável, também na publicação e na Retificação.
- **FR-705**: A regra de aplicabilidade DEVE ser uma só, e todas as leituras DEVEM usá-la: o cartão
  público da vaga, a inscrição em rascunho, o bloqueio do envio, a gravação da lista no envio e a
  reconstrução das inscrições anteriores à feature.

### A publicação

- **FR-706**: A publicação e a Retificação DEVEM ser impedidas quando um código referido por algum
  recorte transversal tiver denominações diferentes entre os Perfis que o têm. O IMPEDE DEVE nomear o
  código, cada denominação e os Perfis de cada uma (D1).
- **FR-707**: A regra de coerência DEVE cobrir **só** a denominação. Percentual, fundamento, descrição
  e demais parâmetros da cota NÃO PODEM ser comparados, porque a cota é por Perfil (D1).
- **FR-708**: O IMPEDE que a #161 emite para "Todos os Perfis" + Modalidade de um Perfil DEVE
  continuar, e a mensagem DEVE oferecer, além das duas saídas atuais, a terceira: usar a Modalidade
  daquele código em todos os Perfis (D3).

### O que o candidato vê

- **FR-709**: O cartão público de cada Perfil DEVE anunciar o documento transversal entre os que
  "cada modalidade acrescenta", na Modalidade daquele código, em todo Perfil que a tenha.
- **FR-710**: A inscrição em rascunho DEVE listar o documento transversal quando a modalidade
  escolhida tiver o código do recorte, com a obrigatoriedade declarada. Trocar a modalidade DEVE
  atualizar a lista, como já atualiza para o recorte exato.
- **FR-711**: O envio DEVE ser recusado no servidor, e não só na tela, enquanto faltar um documento
  transversal obrigatório aplicável.

### O documento publicado

- **FR-712**: O documento publicado DEVE agrupar os documentos transversais **por código**, num grupo
  por modalidade, com o título *"Dos candidatos concorrentes na modalidade {denominação}:"*, sem
  nome de Perfil. Dois documentos transversais do mesmo código DEVEM sair no mesmo grupo. Documentos
  com recorte exato continuam nos grupos que têm hoje.
- **FR-713**: O documento transversal facultativo DEVE sair com a marca *"(facultativo)"* dentro do
  grupo, como sai hoje no grupo "de todos".

### A lista gravada no envio

- **FR-714**: No ato do envio, e na mesma transação, a inscrição DEVE gravar a **lista exigida**: para
  cada Documento Exigido da versão que o envio registra como aceita, (a) a identificação estável do
  documento, (b) o estado, *pedido como obrigatório*, *pedido como facultativo* ou *não se aplica*, e
  (c) a razão, que é o recorte que o incluiu ou o excluiu, legível sem recalcular (`D-003`).
- **FR-715**: A lista exigida DEVE ser imutável depois do envio. Nenhuma operação da aplicação a
  altera ou apaga, e a proteção DEVE ser a mesma das demais tabelas append-only do sistema.
- **FR-716**: O reenvio idempotente do mesmo envio NÃO PODE produzir segunda lista.
- **FR-717**: A lista exigida DEVE conter também os documentos que **não se aplicam**, com a razão.
  "Não se aplica" é informação registrada, e não ausência de linha.

### Quem analisa, e quem consulta

- **FR-718**: A Mesa DEVE ler a lista exigida da inscrição, e não recalculá-la. Cada Documento Exigido
  da versão aceita DEVE aparecer num de três estados: *apresentado*, *não apresentado* ou *não se
  aplica*. Cada um vem com a obrigatoriedade e a razão.
- **FR-719**: A consulta administrativa ("Inscrições recebidas", a lista e o detalhe) DEVE ler a lista
  exigida para a contagem de obrigatórios recebidos e esperados e para a relação de documentos.
- **FR-720**: A página da inscrição enviada, no portal do candidato, DEVE ler a mesma lista. O
  comprovante e o código de verificação NÃO mudam.

### Retificação e mutabilidade

- **FR-721**: O campo do recorte transversal DEVE ser declarado **retificável** na matriz de
  mutabilidade, com a razão escrita (`D-002`). O resumo público "O que mudou" DEVE nomeá-lo: quem
  acrescenta, remove ou troca o recorte transversal produz uma linha legível, com o nome do documento
  e o rótulo do campo, e nunca com identificador interno. Como toda linha desse resumo, ela diz
  **que** o campo mudou, e não o valor: o valor está no documento da Retificação (`D-008`).
- **FR-722**: A tela de Retificação DEVE oferecer o recorte transversal nas mesmas condições da
  composição, inclusive a troca, no mesmo ato, do recorte de um documento existente ("todos", ou
  exato) pelo transversal. Acrescentar e remover Documento Exigido continuam fora da Retificação,
  como já são (`D-009`).
- **FR-723**: Uma Retificação NÃO PODE alterar a lista exigida de inscrição já enviada. As inscrições
  enviadas depois dela DEVEM gravar a lista da versão que aceitaram.
- **FR-724**: Remover de todos os Perfis a Modalidade de um código usado por recorte transversal DEVE
  ser impedido, como documento inalcançável: na gravação do rascunho, na publicação e na
  Retificação. Remover de alguns Perfis DEVE ser permitido. Quando a recusa vem da gravação da etapa
  Perfis, a mensagem DEVE nomear o documento que ficaria inalcançável (`D-010`).

### Antes da feature

- **FR-725**: Documento publicado antes desta feature NÃO PODE ser regenerado nem alterado. A versão
  publicada continua sendo lida como foi publicada.
- **FR-726**: Inscrição enviada antes desta feature não tem lista exigida, e NÃO DEVE ganhar uma
  escrita depois do envio (`D-004`). A Mesa, a consulta administrativa e a inscrição enviada no
  portal DEVEM **reconstruí-la** a partir da versão aceita, pela regra única (`FR-705`). A Mesa e a
  consulta administrativa DEVEM dizer que ela foi reconstruída. O portal lista só os documentos que
  o candidato enviou, e a reconstrução não muda o que ele mostra, por isso ele não traz o aviso.
- **FR-727**: Quando a versão aceita tiver o recorte "Todos os Perfis" + Modalidade de um Perfil, e
  a inscrição concorrer, no seu Perfil, em Modalidade de mesma denominação, a Mesa DEVE mostrar o
  documento como
  *não pedido pelo portal, exigido pelo Edital publicado* (`D-007`). Vale para a lista reconstruída
  **e** para a gravada. Um Edital publicado antes da #161 pode continuar recebendo inscrições depois
  desta feature, e a lista dessas inscrições é gravada sobre a mesma versão ambígua.

### Autorização, dados pessoais e auditoria

- **FR-728**: Quem lê a lista exigida DEVE ser exatamente quem já lê os documentos da inscrição: o
  candidato, a sua; o analista, as que lhe foram distribuídas; o Gestor, pela consulta administrativa.
  Nenhuma permissão nova, nenhum acesso por identificador.
- **FR-729**: A gravação da lista exigida DEVE fazer parte do ato de envio já auditado, sem evento de
  auditoria próprio que repita conteúdo da inscrição.

### Interface

- **UX-080** — **A opção de recorte transversal diz o alcance.** A opção mostra a denominação, o
  código e quantos Perfis têm aquela Modalidade (*"Pessoas com Deficiência (PcD) — em todos os Perfis
  que a têm (16 de 16)"*). Fica separada dos pares Perfil × Modalidade, e antes deles. Os rótulos
  são fixos: na composição, o grupo **"Em todos os Perfis"** vem antes do grupo **"Modalidade de um
  Perfil"**; na Retificação, o campo se chama **"Modalidade em todos os Perfis"**. O resumo público
  usa esse mesmo rótulo.
- **UX-081** — **A razão se lê como frase.** Na Mesa e na consulta administrativa, a razão é escrita
  para quem lê: *"pedido de todos os candidatos"*, *"pedido de quem concorre ao Perfil C1"*, *"pedido
  de quem concorre em Pessoas com Deficiência, em todos os Perfis"*, *"pedido de quem concorre ao
  Perfil C1 em Pretos, Pardos, Indígenas e Quilombolas"*. A Modalidade é nomeada pela
  **denominação**, e nunca pelo código. O "não se aplica" diz a quem o documento era pedido.
- **UX-082** — **"Não se aplica" não compete com o que foi pedido.** Os documentos que não se aplicam
  aparecem depois dos pedidos, e se distinguem deles sem depender só de cor.
- **UX-083** — **A lista reconstruída se anuncia.** Na inscrição anterior à feature, a Mesa diz, uma
  vez e acima da lista, que ela foi reconstruída a partir da versão aceita e não gravada no envio.

### Key Entities

- **Documento Exigido** (existente): ganha o recorte transversal, que é o **código** de uma
  Modalidade, exclusivo com Perfil e Modalidade exata.
- **Modalidade de Concorrência** (existente, por Perfil): nada muda nela. O código continua único no
  Perfil e estrutural. A denominação continua retificável, agora sujeita à coerência de `FR-706`
  quando o código é referido por recorte transversal.
- **Lista exigida da Inscrição** (nova): uma por inscrição enviada, gravada no envio e imutável. Um
  item por Documento Exigido da versão aceita, com a identificação estável, o estado (obrigatório,
  facultativo, não se aplica) e a razão.

## Success Criteria *(mandatory)*

- **SC-260**: Recompondo pela interface os documentos do item 5.5 do 140/2025 condicionados à
  modalidade, com os 16 Perfis, são **7 linhas** de Documento Exigido, contra **112** na única forma
  fiel de hoje: redução de 94%.
- **SC-261**: No documento publicado desse Edital recomposto, dos **nove** documentos que o 140/2025
  publicou como facultativos, **quatro** (h-I, h-II, i-I, k) saem **obrigatórios** no grupo da
  modalidade. **Três** (i-II, i-III, m) saem no grupo de PPIQ, e não mais no de todos. **Dois** (e, l)
  ficam como estão (D2).
- **SC-262**: Recompondo o cenário do 903/2026 com o laudo como "PcD em todos os Perfis", **7 de 7**
  superfícies dizem o mesmo sobre o laudo do PcD: o documento publicado, o cartão do C1, o cartão do
  C2, a inscrição PcD no C1, a inscrição PcD no C2, a Mesa do C1 e a Mesa do C2. **Zero** envios PcD
  sem laudo são aceitos em qualquer Perfil.
- **SC-263**: Em toda inscrição enviada depois da feature, **100%** dos Documentos Exigidos da versão
  aceita aparecem na Mesa com estado e razão. **Zero** somem. O laudo aparece na inscrição AC como
  *não se aplica*, com a razão.
- **SC-264**: Uma Retificação que muda o recorte de um documento, publicada depois de envios,
  produz **zero** diferenças na Mesa, na consulta administrativa e na inscrição enviada no portal
  dessas
  inscrições.
- **SC-265**: Na inscrição do C2 do 903 original (enviada antes da feature), a Mesa mostra o laudo
  como *não pedido pelo portal, exigido pelo Edital publicado*, e anuncia a lista como reconstruída.
  Nenhum documento publicado do 903 muda: o resumo criptográfico é o mesmo antes e depois.
- **SC-266**: Com um documento transversal por `PcD`, renomear a denominação em **1** dos 16 Perfis
  produz **exatamente 1** IMPEDE, que nomeia as duas denominações. Renomear nos **16** produz **zero**.
- **SC-267**: Nas três operações sobre o recorte transversal feitas por Retificação (acrescentar,
  remover, trocar o código), **3 de 3** aparecem no "O que mudou" público, com o nome do documento e
  o rótulo do campo, e com **zero** identificadores internos. A contagem não inclui a mudança do recorte exato,
  cuja omissão é defeito anterior, na fila das diretas (§3).
- **SC-268**: Os cenários das User Stories 1 e 2 são executados de ponta a ponta pelos canais dos
  atores, sem banco, shell ou API: compor e publicar pela interface administrativa; inscrever e
  enviar pelo portal; analisar pela Mesa.

## Assumptions

- **As correções da fila das diretas andam em paralelo.** A instrução do documento chegando à Mesa e
  a marca "(facultativo)" na Revisão do portal estão sendo feitas em outra worktree
  (`claude/instrucao-e-facultativo`). Esta feature mexe na mesma tela da Mesa. Quem chegar depois
  preserva o que a outra entregou.
- **A `043-duplicar-perfil` não depende desta, nem esta dela.** A interação é só a do caso-limite:
  Perfil duplicado herda os documentos transversais sem cópia.
- **Os fatos declarados continuam servindo só ao desempate.** Nada aqui os liga à exigência
  documental (D2).
- **A identidade da inscrição não muda.** `profile_id` e `modality_id` continuam sendo o que a
  inscrição afirma. A lista exigida é derivada deles, no envio, e não os substitui.

### D-001 — a coerência de denominação vale só para código referido por recorte transversal

A regra de D1 existe para que o código **signifique o mesmo** onde o Edital afirma que significa. Um
Edital sem recorte transversal não afirma identidade nenhuma entre Perfis. Estender o IMPEDE a todo
código repetido transformaria em impedimento, na próxima Retificação de um Edital publicado antes da
feature, uma afirmação que ele nunca fez. *Descartado:* coerência universal, e AVISO universal com
IMPEDE só no uso. O segundo pediria um aviso sobre algo que não tem consequência.

### D-002 — o recorte transversal é retificável

O recorte diz **quem deve apresentar**, e é da mesma natureza de `profileId` e `modalityId`, que já
são retificáveis. Uma Retificação pode mudar quem deve apresentar para as inscrições futuras. O que
protege as inscrições enviadas é a **lista gravada** (`FR-723`), e não o congelamento do campo.
Estrutural impediria justamente o caso da US3, que é o maior benefício para os Editais já publicados.
O valor que o recorte aponta, o código, já é estrutural. Por isso o recorte não se desfaz por uma
renomeação acidental.

### D-003 — a lista gravada tem todos os documentos, inclusive os que não se aplicam

Gravar só os aplicáveis deixaria o "não se aplica" para ser **deduzido** na leitura, comparando a
versão aceita com a lista. É outra forma de recálculo, e a Mesa voltaria a depender da regra do dia.
Gravar todos, com a razão, é o que torna a lista uma reprodução, e não uma reinterpretação.

### D-004 — sem preenchimento retroativo

Uma lista escrita hoje para uma inscrição de ontem seria uma reconstrução assinada como registro. O
envio aconteceu sem ela, e o sistema não pode afirmar o contrário. A reconstrução continua existindo,
mas na leitura, e anunciada como tal (`UX-083`).

### D-005 — a denominação se compara como está escrita

Só os espaços das pontas são desconsiderados. Maiúscula e acento contam. O documento publicado
imprime **uma** denominação no título do grupo, e a regra existe para que ele não tenha de escolher
entre duas.

### D-006 — cinco formas, mutuamente exclusivas

"Perfil C1 + PcD em todos os Perfis" diria duas coisas diferentes na mesma linha. A forma exata
(Perfil × Modalidade) já cobre o caso. O recorte continua se lendo pelo campo presente, sem linguagem
de condição, como o domínio já decidiu para as quatro formas atuais.

### D-007 — a reconstrução denuncia a divergência que a #161 fechou

Nas inscrições anteriores à #161, o recorte "Todos os Perfis" + Modalidade de um Perfil fez o
documento publicado e o portal dizerem coisas diferentes. Reconstruir a lista pela regra do portal, e
calar, repetiria na Mesa o que levou ao indeferimento no 903. A Mesa mostra os dois fatos, o que o
portal pediu e o que o Edital publicado dizia. O juízo continua sendo de quem analisa.

### D-008 — o resumo público nomeia o campo, e não o valor

Acrescentada no planejamento. A primeira redação pedia a denominação e o código na linha do "O que
mudou". O resumo, porém, foi desenhado pela `024` para dizer **onde** e **qual campo**, e nunca o
valor: quem quer o texto exato abre o documento da Retificação, na mesma linha do histórico. Pôr o
código só nesta linha abriria uma exceção a esse desenho sem necessidade. O que a decisão de 25/09
pedia, que o campo novo não seja descartado em silêncio, continua garantido.

### D-009 — a Retificação muda o recorte, mas não junta linhas

Acrescentada no planejamento. A tela de Retificação não acrescenta nem remove Documento Exigido, e a
razão já está escrita no código: acrescentar um obrigatório depois de publicado torna incompleta a
inscrição de quem já enviou, e o que fazer com essas pessoas é decisão normativa. Remover segue a
mesma lógica. Esta feature não reabre isso. O caso do 140/2025, um documento "facultativo para
todos" por linha, cabe inteiro, porque é **trocar o recorte da linha que já existe**. Um Edital
publicado com o mesmo documento repetido por Perfil (N linhas exatas) não se reduz a uma linha por
Retificação: pode tornar uma delas transversal, mas as outras ficam. Isso fica em Riscos e lacunas.

### D-010 — a gravação recusa o que tornaria o documento inalcançável, como já faz

Acrescentada na análise de consistência. O rascunho valida os documentos contra os Perfis **de cada
gravação**, e hoje já recusa, em qualquer etapa, o documento cuja Modalidade exata deixou de existir.
O recorte transversal segue o mesmo precedente para o código que nenhum Perfil tem e para o código
declarado ampla (`FR-703`, `FR-704`, `FR-724`). O custo é conhecido: a etapa Perfis pode ser recusada
por causa de um documento. Por isso a mensagem nomeia o documento, e não só o campo. A coerência de
denominação continua só na publicação (`research.md`, R-007): renomear é edição em curso, e travar a
gravação a cada renomeação seria travar o trabalho no meio.

## LGPD

**Nenhum dado pessoal novo é coletado.** A lista exigida deriva do Perfil e da modalidade que a
inscrição já guarda. A modalidade, que pode revelar deficiência, já está na inscrição, e a lista não
a torna mais visível: só quem já vê os documentos da inscrição vê a lista (`FR-728`). A razão
registrada é o recorte do **Edital**, e não um atributo do candidato. A auditoria não repete o
conteúdo da lista (`FR-729`).

Finalidade: reproduzir o que foi exigido de cada inscrição, como a Constituição pede, e dar a quem
analisa a base para decidir. Minimização: a lista guarda referências e estados, e não conteúdo de
documento.

## Riscos e lacunas

- **A consulta administrativa lista muitas inscrições.** Ler a lista exigida de cada uma não pode
  virar uma consulta por inscrição. O plano precisa resolver a contagem por agregação, dentro do
  orçamento de consultas que a listagem já tem.
- **Tabela append-only nova.** Ela entra no provisionamento de papéis e na contagem de tabelas
  protegidas, e a migration entra no guardião de contagem por app. O plano precisa prever os dois.
- **A submodalidade continua sem forma** (§1). Três documentos do 140/2025 seguem facultativos. É o
  limite E7 do estudo, e fica registrado aqui, sem virar escopo.
- **Edital publicado com o documento repetido por Perfil** não se reduz a uma linha por
  Retificação (`D-009`). Tornar uma das N linhas transversal, com as outras N−1 ainda lá, faria o
  candidato daquela modalidade ver o documento duas vezes no Perfil que a linha exata alcança. O
  caso não apareceu na amostra, onde o atalho usado foi o "facultativo para todos". Fica registrado.
- **Filtro de concorrência da consulta administrativa** repete "Pessoas com Deficiência" uma vez por
  Perfil, sem nomeá-lo (conferência, §3). É defeito de tela independente desta feature, e fica
  registrado, sem virar escopo.

## Out of Scope

- Condição sobre o candidato: sexo, idade, vínculo (D2), inclusive o tipo "sim/não" nos fatos
  declarados.
- Submodalidade e ordem de convocação (estudo, E7).
- Juízo por documento na Mesa, ou pendência documental após o envio.
- Aplicação em lote e duplicação de Perfil (D5; `043`).
- O resumo público para o recorte exato, `profileId` e `modalityId` (fila das diretas).
- A instrução na Mesa e a marca "(facultativo)" na Revisão do portal (fila das diretas, D2).
- Regenerar ou anotar documento publicado antes da feature.
