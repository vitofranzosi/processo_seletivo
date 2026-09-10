# Feature Specification: Quadro de Vagas por Modalidade

**Feature Branch**: `claude/quadro-vagas-modalidade-7b10d4`

> **A numeração é `025` porque veio de `--number 25`**, e não da última pasta em `specs/`. A
> varredura de 10/09/2026 confirmou que nenhuma worktree tem uma `025`, e que `specs/` vai até a
> `024`. Existe, porém, uma worktree paralela (`spec-025-quadro-vagas`) que carrega o **documento de
> entrada** desta spec e nenhuma spec — o número fica tomado por esta árvore.

> **Os identificadores continuam a faixa global**, política que a `024` abriu e que vale desde
> então: duas features simultâneas em worktrees diferentes não descobrem o número uma da outra pela
> pasta. Teto medido em todas as worktrees antes de escrever — `FR-152`, `SC-047`, `UX-019` —, e
> esta spec abre em `FR-153`, `SC-048`, `UX-020`. As **decisões** reiniciam em `D-001`, porque são
> lidas dentro da feature que as produziu.

**Created**: 2026-09-10

**Status**: Draft

**Input**: `doc/prompt/025-quadro-de-vagas-por-modalidade.md`, na redação com as três decisões
fechadas — que, no momento em que esta spec foi escrita, ainda vivia no PR #96 e não na `main`. As
três decisões daquele documento entram aqui **recebidas**, e não reabertas; elas reaparecem abaixo
renumeradas na faixa desta feature, junto com as que a spec precisou tomar para fechar as perguntas
que ele herdou.

> **Os identificadores das decisões do documento de entrada não são reaproveitados**, de propósito: a
> numeração de decisão é lida dentro da feature que a produziu, e um identificador daquele documento
> citado aqui apontaria para o nada.

> **A frase que governa:** o Edital publica quantas vagas existem em cada recorte, em números
> absolutos, legíveis por máquina e alcançáveis por Retificação — e o quadro publicado é a fonte, não
> o percentual que o fundamenta.

> **E a frase que mantém o corte:** esta feature **declara** o quadro. Não o ocupa, não o consome e
> não convoca por ele.

---

## 1. O achado que organiza a feature

O sistema **ordena por lista de concorrência e não sabe dizer quantas vagas cada lista tem.** A
Modalidade de Concorrência ganhou papel operacional — é ela que reparte universo, relação, ato e
publicação do sorteio —, e a outra metade do mesmo quadro nunca teve casa: `ModalidadeConcorrencia`
guarda código, denominação e descrição, e nenhuma quantidade. O total do Perfil existe; a repartição
dele, não.

A consequência é de autoria, e é ela que esta feature fecha: há Editais reais que o sistema conduz
até a ordem do sorteio e **não consegue publicar**, porque o documento que eles publicam diz um
número que o sistema não tem onde escrever.

### 1.1 O quadro real, nas palavras dos próprios Editais

```
57/2026, por curso     AC 56 · PcD 4 · PPI 20                        (total 80)
28/2026, por polo      AC 28 · PcD 2 · PPI 10                        (total 40)
46/2026, um curso      AC 18 · PPI 6 · Q 1 · PCD 1 · EP 1 · …        (total 36)
```

São **absolutos e irregulares**. O de 46 não é gerável por percentual — `Q 1` e `PCD 1` saem de
arredondamento sobre censo —, e ele é a prova de que **percentual não substitui quadro publicado, e
não o gera**. O 46 está fora do alvo do produto por decisão anterior; a prova continua valendo.

### 1.2 A ampla concorrência tem duas grafias, e uma delas é armadilha

O recorte sem lista de concorrência não filtra por Modalidade nenhuma: entram todas as inscrições
submetidas do Perfil. É exatamente o que a cláusula 8.7 do 57 e do 28 manda para a ampla
concorrência — todos os candidatos, inclusive os cotistas, participam do sorteio da ampla
concorrência, e em seguida ocorre o das reservas. **Logo o recorte sem lista é o recorte da ampla
concorrência.**

O defeito é que, quando o Edital declara **também** uma Modalidade chamada "Ampla concorrência" — o
caso normal —, existem dois lugares que dizem a mesma coisa, e o segundo é filtrado a quem
*declarou* ampla concorrência, quase sempre vazio. A correção anterior foi de rótulo, não de
identidade: a tela deixou de mostrar dois blocos homônimos, e as duas grafias continuam de pé.

Para o quadro, isso decide onde mora `AC 56`, e é o ponto em que esta spec erraria sozinha.

## 2. O que já existe, e que esta feature NÃO reconstrói

- **O endereçamento normativo estável.** A gramática de Retificação é genérica e só pergunta se a
  coleção tem chave; declarada a coleção, cada linha passa a ser alcançável por identidade. Não há
  gramática nova a inventar.
- **A cadeia de degraus de schema.** Um degrau por incremento, cada um sabendo só a sua origem e o
  seu destino. O desta feature é mais um.
- **A validação de referência cruzada na elaboração.** Já existe uma coleção de raiz que referencia
  Modalidades aninhadas no Perfil, com a elaboração recusando referência quebrada e com mensagem que
  separa os dois casos — "não pertence ao Perfil declarado" contra "não é de nenhum Perfil deste
  Edital". É o padrão a copiar, inclusive a mensagem.
- **Referência anulável com significado.** Já existe o precedente literal de um identificador que,
  ausente ou nulo, significa alguma coisa em vez de faltar.
- **A trilha append-only e o resumo canônico.**
- **A tela de composição do Perfil.** O quadro é mais uma seção dela, e não uma tela à parte.

## 3. Decisões fechadas antes do planejamento

As três primeiras chegaram decididas pelo usuário em 10/09/2026, e estão aqui pelo texto delas, não
por resumo. As demais fecham as perguntas que o documento de entrada deixou para a spec.

### D-001 — O quadro é conteúdo do documento, nunca anexo

A escolha nunca foi entre duas formas de fazer a mesma coisa: publicado como anexo binário, o quadro
não é legível por máquina, e a feature que depois for ocupar vaga não o alcança. E publicação é ato
imutável — o Edital que publicar o quadro como binário fica assim para sempre. Não seria migração
adiada, e sim **bifurcação permanente do acervo** entre Editais com quadro legível e Editais sem.

O anexo binário continua legítimo para os formulários. Para o quadro de vagas, fica recusado.

### D-002 — O quadro é uma coleção normativa própria do Perfil

Com linhas de identidade estável: uma **linha geral**, sem referência a Modalidade, e **linhas
reservadas** que referenciam Modalidades por identidade.

```
linha geral        AC 56    sem referência a Modalidade
linha reservada    PcD  4   referencia a Modalidade PcD
linha reservada    PPI 20   referencia a Modalidade PPI
                   ─────
                   total 80 = o total de vagas imediatas do Perfil
```

**A linha geral carrega a ampla concorrência (56), e não o total (80).** O total é a soma, e já tem
casa própria no Perfil. Confundir os dois publica um quadro que não fecha.

Guardar a quantidade **na Modalidade** ficou recusado: a ampla concorrência não é Modalidade no
recorte que o sorteio usa, e o Edital teria de pendurar `AC 56` na grafia-armadilha — a que o sorteio
não consulta — ou não publicá-lo. Guardar **na Regra Normativa** também: a ampla concorrência
precisaria de uma Regra, e o fundamento normativo é obrigatório; publicar fundamento inventado para
a ampla concorrência é inventar norma, e a alternativa seria uma segunda grafia — quantidade na
Regra para as cotas, noutro lugar para a ampla —, que é duas respostas para a mesma pergunta.

### D-003 — A quantidade publicada é a fonte; o percentual fundamenta e não calcula

**A quantidade publicada no quadro é a fonte autoritativa. O percentual não pode sobrescrevê-la nem
recalculá-la silenciosamente.** Duas consequências, separadas de propósito:

- **Preservação histórica — obrigatória.** Todo valor já publicado nos campos da Regra Normativa
  permanece intocado no conteúdo em que foi publicado. Esta spec não discute isso.
- **Depreciação futura — aberta, e não é desta feature.** Se algum desses campos deve sair do modelo
  de autoria, e por qual degrau, decide-se quando houver quem os consuma ou quem declare que ninguém
  os consumirá. Esta spec não deprecia nada e não promete nada sobre eles.

Fica preservado o uso do percentual para **advertir** na elaboração — avisar que `4` não é 20% de
`80` é serviço legítimo — sem transformar cálculo em norma.

### D-004 — A ampla concorrência tem uma grafia no quadro: a linha geral

Uma Modalidade declarada com nome "Ampla concorrência" **não** carrega vagas: ela existe para que um
Documento Exigido possa apontá-la, e é a grafia que o sorteio não usa. Publicar `AC 56` ali seria
publicar o número no lugar onde a feature de ocupação não vai procurar.

### D-005 — Quadro não declarado não é zero

`0` diz *"esta linha tem zero vagas"*; quadro ausente diz *"este Edital não publicou quadro"* — e é o
que **todo** Edital publicado até hoje afirma, porque a capacidade não existia. A conversão de schema
faz a coleção nascer **vazia**, sem inventar número, no precedente já usado por um degrau anterior:
lista vazia é a grafia da ausência.

### D-006 — Quadro parcial é legítimo, e linha ausente nunca significa zero

Um Perfil pode declarar linha para algumas Modalidades e não para outras. A ausência de linha diz que
o Edital não declarou aquela quantidade, e não que ela é zero — pela mesma razão da D-005, um degrau
abaixo. Quem quiser dizer zero declara a linha com `0`.

### D-007 — O total do Perfil e a soma das linhas não se contradizem, e a soma não sobrescreve

O total de vagas imediatas do Perfil continua sendo declarado por quem compõe, e **não passa a ser
calculado** a partir das linhas. Quando o Perfil declara quadro **completo** — linha geral e uma
linha para cada Modalidade declarada —, a soma das linhas e o total são conferidos, e a divergência é
**recusada na submissão**, com a diferença dita em números.

Quando o quadro é parcial (D-006), a conferência não roda: somar linhas incompletas produziria
acusação falsa. Um Edital sem quadro nenhum continua publicável, e todos os publicados até hoje o
são.

Calcular o total a partir das linhas foi recusado porque apagaria o caso em que o Edital publica um
total que a repartição não fecha — que existe, e que o sistema precisa saber recusar em vez de
esconder.

### D-008 — Modalidade referenciada por linha não é removível enquanto a linha existir

Uma Retificação que remova Modalidade referenciada por uma linha do quadro é **recusada**, com
mensagem que diz qual linha a impede. Remover as duas é um ato só, e quem retifica declara os dois
movimentos.

A alternativa — a linha cair junto, em cascata — foi recusada: apagaria quantidade publicada como
efeito colateral de outro movimento, e quem retifica não veria o número sumir.

### D-009 — A ordem das linhas é declarada e preservada; ela é apresentação, não norma

O quadro é publicado na ordem em que foi declarado, e a ordem não é recalculada nem alfabetizada. Ela
**não** carrega significado normativo próprio: não é ordem de convocação nem de precedência entre
listas — isso é da feature de convocação, e prometê-lo aqui seria prometer outra feature. A linha
geral é exibida em primeiro lugar, como os Editais reais a exibem.

### D-010 — O nome da coleção segue a convenção que já existe

Chave em inglês no conteúdo publicado, como as demais coleções do snapshot; vocabulário do domínio em
português no código, como manda a convenção do repositório. O plano fixa os dois nomes; a spec fixa
que eles seguem essa convenção e que a chave **não** muda depois de publicada — mudá-la seria mudar o
endereço de retificação de tudo o que já saiu.

### D-011 — O quadro reparte vagas imediatas, e só elas

O tipo e o limite de cadastro de reserva são hoje do Perfil, com a mesma assimetria do total de vagas
imediatas: existe o total, não existe a repartição. Esta feature **não** reparte o cadastro de
reserva: a linha do quadro carrega uma quantidade, e ela é de vaga imediata.

É o recorte que os Editais do alvo pedem — nenhum dos três que a feature destrava reparte cadastro de
reserva por Modalidade. O `76/2026`, que é cadastro de reserva por polo, continua sem publicar a
repartição dele, e isso é **registro**, não escopo: quando a pergunta voltar, ela volta com o custo
declarado de um segundo degrau de schema.

A forma da linha **não** é preparada de antemão para uma segunda quantidade. Admitir o campo sem
declarar regra que o consuma é construir a estrutura antes de existir quem a use — é o que o próprio
repositório recusou ao modelar os campos descritivos do Perfil, e a razão está escrita lá.

## 4. Problema

Quem compõe um Edital hoje declara as Modalidades de Concorrência de cada Perfil e o total de vagas
imediatas, e não tem onde escrever quantas vagas cabem em cada Modalidade. O documento que o Edital
publica diz esses números; o sistema, não. O resultado é que Editais que o sistema conduz até a ordem
do sorteio **não são publicáveis por ele**, e o número que separa o certame de existir como documento
é um número que ninguém consegue digitar.

Do inventário vigente de capacidade:

```
autoria   — documento publicável inteiro          3 de 6
condução  — o mecanismo produz a ordem            5 de 7
certame   — publicável E conduzível até a ordem   2 de 7
```

Esta feature sozinha leva a terceira linha de 2 para 5: três Editais reais passam a ser publicáveis,
e os três já têm mecanismo. Nenhum deles passa a **ocupar** vaga, convocar ou cortar por causa dela —
eles passam a **existir como documento**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Declarar o quadro que o Edital publica (Priority: P1)

Quem compõe o Edital abre o Perfil de um curso, vê as Modalidades que já declarou e escreve, ao lado
de cada uma, quantas vagas ela tem — mais a linha da ampla concorrência, que não pertence a
Modalidade nenhuma. Ao terminar, o Perfil diz `AC 56`, `PcD 4` e `PPI 20`, e o total de 80 que já
estava declarado continua ali, conferido contra a soma.

**Why this priority**: é a lacuna. Sem ela, nada mais desta feature existe, e os três Editais
continuam impublicáveis.

**Independent Test**: compor um Perfil com três Modalidades, declarar o quadro, e ver as quatro
quantidades gravadas e recuperáveis — sem publicar nada.

**Acceptance Scenarios**:

1. **Given** um Perfil com as Modalidades PcD e PPI declaradas, **When** quem compõe declara a linha
   geral com 56 e as linhas reservadas com 4 e 20, **Then** o Perfil passa a declarar um quadro de
   três linhas, cada uma com identidade própria.
2. **Given** o mesmo Perfil, **When** quem compõe tenta declarar uma segunda linha geral, **Then** o
   sistema recusa, dizendo que a ampla concorrência tem uma linha só.
3. **Given** um Edital com dois Perfis, **When** uma linha do Perfil A referencia uma Modalidade do
   Perfil B, **Then** o sistema recusa dizendo que a Modalidade não pertence ao Perfil declarado.
4. **Given** um Perfil cujo total declarado é 80, **When** o quadro completo soma 79, **Then** a
   submissão é recusada, com a diferença dita em números.
5. **Given** um Perfil sem quadro declarado, **When** o Edital é submetido, **Then** ele é aceito: o
   quadro é opcional, e ausência não é zero.

---

### User Story 2 — Publicar o quadro como conteúdo do Edital (Priority: P1)

O Edital é publicado, e o quadro viaja no conteúdo publicado — legível por máquina, com identidade
por linha —, e não como anexo. O documento publicado exibe o quadro na ordem declarada. Um Edital
publicado antes desta feature continua legível, e não passa a afirmar zero vaga em lugar nenhum.

**Why this priority**: publicar é o que torna o quadro norma. Sem isso, a US1 é rascunho que não sai.

**Independent Test**: publicar um Edital com quadro declarado e ler o quadro no conteúdo publicado e
no documento; publicar um Edital sem quadro e ver a seção omitida.

**Acceptance Scenarios**:

1. **Given** um Perfil com quadro declarado, **When** o Edital é publicado, **Then** o quadro está no
   conteúdo publicado, com uma identidade estável por linha, e o documento o exibe na ordem
   declarada.
2. **Given** o mesmo conteúdo publicado duas vezes, **When** o resumo canônico é calculado, **Then**
   os dois resumos são iguais.
3. **Given** um Edital publicado antes desta feature, **When** ele é lido agora, **Then** ele
   permanece legível, sem quadro, e nenhuma tela afirma que ele tem zero vagas.
4. **Given** um Edital sem quadro declarado, **When** o documento é gerado, **Then** a seção do
   quadro é omitida inteira, sem frase de ausência.
5. **Given** um quadro cujas quantidades não são deriváveis de percentual algum — `Q 1`, `PCD 1` —,
   **When** ele é publicado, **Then** ele sai exatamente como entrou.

---

### User Story 3 — Retificar o quadro por identidade (Priority: P1)

O Edital publicado precisa mudar `PPI 20` para `PPI 18`. Quem retifica alcança **aquela linha**, pela
identidade dela, altera o número, e as demais linhas não são tocadas. O quadro anterior continua
legível sob a norma que o governou.

**Why this priority**: é o caso comum — Editais reais retificam quadro de vagas com frequência —, e é
o passo que separa esta feature de uma coluna a mais numa tabela.

**Independent Test**: retificar uma linha de um Edital publicado e verificar que só ela mudou, e que
a versão anterior permanece legível.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com três linhas, **When** uma Retificação altera a quantidade de uma
   delas por identidade, **Then** só aquela linha muda, e o conteúdo anterior permanece legível.
2. **Given** o mesmo Edital, **When** uma Retificação acrescenta uma linha nova, **Then** ela nasce
   com identidade própria, alcançável na Retificação seguinte.
3. **Given** uma linha que referencia a Modalidade PPI, **When** uma Retificação tenta remover a
   Modalidade PPI sem remover a linha, **Then** a Retificação é recusada, dizendo qual linha a
   impede.
4. **Given** um quadro publicado, **When** qualquer caminho tenta endereçar uma linha por posição,
   **Then** ele não existe: o endereçamento é sempre por identidade.

---

### User Story 4 — Declarar quadro em Edital com muitos Perfis (Priority: P2)

O Edital do 28/2026 tem 7 polos, cada um com as mesmas 3 Modalidades. Quem compõe declara o quadro
dos sete sem redigitar rótulo nenhum: as linhas nascem das Modalidades já declaradas no Perfil, e só
a quantidade é digitada.

**Why this priority**: a pressão de autoria do Edital grande está registrada, e a feature de copiar de
um Edital para o seguinte **não** a alivia — ela copia entre Editais, não entre Perfis do mesmo
Edital. Sem isto a US1 é possível e insuportável.

**Independent Test**: compor um Edital com 7 Perfis de 3 Modalidades e declarar os 7 quadros,
contando quantos campos exigiram digitação.

**Acceptance Scenarios**:

1. **Given** um Perfil com 3 Modalidades declaradas, **When** quem compõe abre a seção do quadro,
   **Then** as linhas já estão oferecidas — a geral e uma por Modalidade —, e o que falta é a
   quantidade.
2. **Given** uma Modalidade declarada que não deve ter linha, **When** quem compõe deixa a quantidade
   em branco, **Then** o quadro é gravado sem aquela linha, e a ausência não vira zero.

---

### Edge Cases

- **Linha geral com quantidade e nenhuma linha reservada.** É quadro legítimo: Edital sem reserva de
  vaga publica só a ampla concorrência.
- **Quadro só de reservadas, sem linha geral.** É quadro parcial (D-006), aceito; a conferência
  contra o total não roda.
- **Modalidade declarada com nome "Ampla concorrência".** Ela existe, pode ser apontada por Documento
  Exigido, e **não** carrega linha reservada (D-004). Quem tentar declará-la precisa ser advertido de
  que o número da ampla concorrência mora na linha geral.
- **Duas linhas reservadas para a mesma Modalidade.** Recusadas: uma Modalidade tem no máximo uma
  linha.
- **Retificação que remove a única linha geral.** Aceita — o quadro passa a ser parcial —, e a
  conferência contra o total deixa de rodar.
- **Perfil com total de vagas imediatas igual a zero e quadro declarado.** A conferência vale igual: a
  soma das linhas de um quadro completo tem de dar zero, ou é recusada.
- **Edital publicado antes do degrau de schema, lido depois dele.** Coleção vazia, que significa "não
  publicou quadro" e nunca "zero vagas".
- **Quantidade negativa ou não inteira.** Recusada na elaboração.

## Requirements *(mandatory)*

### Functional Requirements

#### Declaração do quadro

- **FR-153**: O Perfil de Vaga MUST poder declarar um quadro de vagas composto de linhas, cada uma
  com identidade própria e uma quantidade de vagas.
- **FR-154**: O quadro MUST admitir no máximo uma **linha geral** por Perfil, identificada pela
  ausência de referência a Modalidade, e ela MUST carregar a quantidade da ampla concorrência.
- **FR-155**: Cada **linha reservada** MUST referenciar, por identidade, uma Modalidade de
  Concorrência declarada no mesmo Perfil, e MUST haver no máximo uma linha por Modalidade.
- **FR-156**: A quantidade de cada linha MUST ser um número inteiro absoluto maior ou igual a zero,
  declarado por quem compõe.
- **FR-157**: Nenhum caminho desta feature MUST derivar, calcular ou recalcular quantidade de vaga a
  partir de percentual, fundamento normativo ou qualquer campo da Regra Normativa.
- **FR-158**: O sistema MUST recusar linha que referencie Modalidade de outro Perfil ou de Perfil
  nenhum, com mensagem que diga qual dos dois casos é.
- **FR-159**: A ausência de linha para uma Modalidade MUST significar quantidade não declarada, e
  nunca zero; declarar zero MUST exigir uma linha com `0`.
- **FR-160**: O quadro MUST ser opcional: um Perfil sem quadro declarado MUST permanecer submetível e
  publicável.
- **FR-161**: Quando o quadro é **completo** — linha geral e uma linha para cada Modalidade declarada
  no Perfil —, a soma das quantidades MUST ser conferida contra o total de vagas imediatas do Perfil,
  e a divergência MUST recusar a submissão dizendo a diferença em números.
- **FR-162**: O total de vagas imediatas do Perfil MUST permanecer declarado por quem compõe, e MUST
  NOT ser sobrescrito pela soma das linhas.
- **FR-163**: O sistema MAY advertir, na elaboração, que uma quantidade declarada diverge do
  percentual publicado na Regra Normativa da Modalidade — e a advertência MUST NOT bloquear a
  gravação nem alterar a quantidade.

#### Publicação

- **FR-164**: A publicação MUST emitir o quadro como conteúdo do Edital publicado, em coleção própria
  do Perfil, com identidade estável por linha.
- **FR-165**: O quadro de vagas MUST NOT ser publicável como anexo binário; anexos permanecem
  legítimos para os demais documentos do Edital.
- **FR-166**: A publicação MUST reverificar a integridade das referências do quadro antes de publicar,
  recusando a publicação onde uma linha aponte Modalidade que não exista no Perfil.
- **FR-167**: O conteúdo publicado MUST passar a ser emitido na versão de schema seguinte à atual, e a
  conversão MUST fazer a coleção do quadro nascer **vazia** para todo conteúdo publicado antes,
  **sem** inventar quantidade.
- **FR-168**: Dois conteúdos publicados idênticos MUST produzir o mesmo resumo canônico, com o quadro
  incluído nele.
- **FR-169**: O documento publicado MUST exibir o quadro na ordem declarada, com a linha geral em
  primeiro lugar, e MUST omitir a seção inteira quando não houver quadro, sem frase de ausência.

#### Retificação

- **FR-170**: Cada linha do quadro publicado MUST ser alcançável por identidade própria, e MUST NOT
  ser alcançável por posição.
- **FR-171**: A Retificação MUST poder acrescentar, alterar e remover linhas do quadro.
- **FR-172**: A Retificação que remova uma Modalidade referenciada por uma linha do quadro MUST ser
  recusada enquanto a linha existir, com mensagem que diga qual linha a impede.
- **FR-173**: Todo valor publicado sob um quadro anterior MUST permanecer legível sob a norma que o
  governou, e a Retificação MUST NOT reescrever conteúdo já publicado.

#### Preservação e alcance

- **FR-174**: Todo valor já publicado nos campos da Regra Normativa MUST permanecer intocado no
  conteúdo em que foi publicado, e esta feature MUST NOT depreciar, remover ou alterar nenhum deles.
- **FR-175**: Esta feature MUST NOT ocupar vaga, atribuir candidato a linha, remanejar, convocar nem
  cortar por quadro.
- **FR-176**: A ampla concorrência MUST ser declarada exclusivamente pela linha geral, e uma
  Modalidade que o Edital use como ampla concorrência MUST NOT carregar linha reservada.

### Requisitos de apresentação

- **UX-020**: O quadro MUST ser uma seção da tela de composição do Perfil, e não uma tela à parte.
- **UX-021**: Declarar o quadro MUST exigir digitar apenas quantidades: as linhas são oferecidas a
  partir das Modalidades já declaradas no Perfil, sem redigitar rótulo algum.
- **UX-022**: A linha geral MUST ser distinguível das linhas reservadas sem depender de cor, e MUST
  dizer na tela que ela é a da ampla concorrência.
- **UX-023**: A divergência entre a soma das linhas e o total do Perfil MUST ser dita em números — o
  que soma, o que foi declarado e a diferença —, e nunca só sinalizada.

### Key Entities

- **Quadro de vagas**: a repartição publicada das vagas imediatas de um Perfil, composta de linhas.
  Coleção própria do Perfil no conteúdo publicado, com chave estável.
- **Linha do quadro**: uma quantidade de vagas com identidade própria. Sem referência a Modalidade, é
  a **linha geral** — a da ampla concorrência; com referência, é **linha reservada**.
- **Modalidade de Concorrência**: já existe, e não muda. Continua com código, denominação e descrição,
  e passa a ser referenciável por linha do quadro.
- **Perfil de Vaga**: já existe. O total de vagas imediatas continua sendo dele, e passa a ser
  conferido contra a soma das linhas quando o quadro é completo.
- **Regra Normativa**: já existe, e não muda. Fundamenta a Modalidade; não calcula quantidade.

## 5. Invariantes observáveis

Verificáveis a qualquer momento, em qualquer estado do acervo:

1. Nenhuma quantidade de vaga é derivada de percentual.
2. A ampla concorrência aparece uma vez por Perfil, na linha geral.
3. Toda linha reservada referencia uma Modalidade do próprio Perfil.
4. Toda linha publicada é alcançável por identidade, e nenhuma por posição.
5. Quadro ausente nunca significa zero vaga.
6. Nenhum valor publicado é reescrito por esta feature.
7. Nenhuma tela desta feature atribui pessoa a linha do quadro.

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-048**: Quem compõe declara o quadro completo de um Perfil de três Modalidades digitando
  **apenas as quatro quantidades**, sem redigitar rótulo, código ou denominação.
- **SC-049**: O ciclo completo do 57/2026 — declarar `AC 56`, `PcD 4` e `PPI 20`, publicar, e
  retificar `PPI 20` para `PPI 18` — é percorrido sem que nenhuma outra linha mude e sem que nenhuma
  quantidade seja recalculada.
- **SC-050**: 100% dos Editais publicados antes desta feature permanecem legíveis depois dela, e
  nenhum passa a afirmar zero vaga.
- **SC-051**: Um quadro cujas quantidades nenhum percentual gera — `Q 1`, `PCD 1` — é publicado e
  lido de volta idêntico ao declarado.
- **SC-052**: Os 7 Perfis do 28/2026, com 3 Modalidades cada, têm quadro declarado em uma sessão de
  composição, com no máximo 28 campos digitados no total.
- **SC-053**: Os três Editais que hoje o sistema conduz e não publica passam a ser publicáveis como
  documento inteiro, sem anexo binário para o quadro.
- **SC-054**: Toda tentativa de publicar quadro cuja soma contradiga o total declarado é recusada
  antes da publicação, e a mensagem diz a diferença em números.

## 7. Out of Scope

Fora deste incremento, e por decisão:

- **Ocupação de vagas, cotas, remanejamento e concorrência concomitante.** Inclusive as cláusulas 8.8
  e 8.9 do 57 — cotista sorteado nas duas listas fica na de ampla concorrência, e a vaga reservada
  passa ao próximo autodeclarado. É a feature de ocupação, e é o caso mais tentador de violar o
  corte.
- **Convocação, chamada e suplência.**
- **Corte e progressão entre Etapas.**
- **A fronteira entre ocupar e convocar**, que continua aberta e fora desta feature: as duas leituras
  em disputa concordam que ocupar não é declarar.
- **Ordem computada por lista de concorrência** — a assimetria entre o que o sorteio reparte e o que a
  emissão de ordem computada reparte. É vizinha, e não é desta.
- **Depreciar os campos da Regra Normativa** (D-003).
- **Reconciliar as duas grafias da ampla concorrência no domínio do sorteio.** Esta feature declara o
  quadro com **uma** grafia (D-004) e não reescreve o ato de ordenação. Se a divergência entre o
  comentário e o comportamento merecer correção própria, é registro — governança é do usuário.
- **Repartir o cadastro de reserva por Modalidade** (D-011). O `76/2026` é o Edital que a pedirá, e
  ele fica registrado como achado — a repartição dele é feature própria, com degrau próprio.

## Assumptions

- O documento de entrada desta spec — a redação com as três decisões fechadas — chega à `main` pelo
  PR #96. Esta spec foi escrita contra o conteúdo daquele PR, e nada aqui depende de o merge ter
  acontecido antes.
- As quantidades de um quadro real cabem em dezenas por linha e em algumas dezenas de linhas por
  Edital; o 28/2026, com 7 polos × 3 Modalidades, é o maior caso do alvo.
- Quem compõe o Edital tem o quadro à mão, em números absolutos, no momento da composição: ele vem do
  documento normativo que originou o Edital, e não é produzido pelo sistema.
- O total de vagas imediatas já declarado nos Editais existentes é confiável, e a conferência da
  FR-161 não invalida nenhum deles — porque nenhum tem quadro, e a conferência só roda com quadro
  completo.
- A verificação desta feature é feita por percurso conduzido contra o servidor real, com o quadro do
  57/2026 declarado, publicado e retificado.

## 8. Ordem de implementação sugerida

1. **Declaração e integridade na elaboração** (US1) — é a lacuna, e demonstra valor sem publicar.
2. **Publicação, degrau de schema e documento** (US2) — o que torna o quadro norma.
3. **Retificação por identidade** (US3) — o passo emblemático, e o que exige a coleção declarada
   antes da emissão.
4. **Composição sem digitação supérflua** (US4) — o que torna o Edital grande suportável.

Cada uma é demonstrável isoladamente. A US3 depende da US2; a US4 depende só da US1.

## 9. Gate de conclusão

A feature está pronta quando, num Edital semeado com dois Perfis e três Modalidades cada, um percurso
conduzido alcança, do começo ao fim:

- declarar o quadro de um Perfil e ver a linha do outro Perfil recusada, com a mensagem que separa os
  dois casos;
- ver a divergência entre soma e total recusada na submissão, com a diferença em números;
- publicar, e ler o quadro no conteúdo publicado e no documento, na ordem declarada;
- retificar uma linha por identidade, e ver as demais intactas e o quadro anterior legível;
- abrir um Edital publicado antes do degrau e não encontrar afirmação de zero vaga em lugar nenhum.

E quando os sete invariantes da §5 forem verificáveis por teste.
