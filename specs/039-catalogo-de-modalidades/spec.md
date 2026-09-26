# Feature Specification: O catálogo de Modalidades do Edital — a lei declarada uma vez

**Feature Branch**: `claude/spec-039-alcance`

**Created**: 2026-09-19 · **Reescrita**: 2026-09-20, depois da auditoria de convergência pós-`038`

**Status**: Draft

**Input**: A conversa de generalidade de 19/09: *"o sistema deve ser genérico o suficiente para permitir editais tanto de alunos quanto de bolsistas"*, *"permitindo que o operador possa configurar o edital se assim desejar"*. Reescrita depois de medir que o modelo barato era o caminho errado.

> **Nota de 26/09/2026, ao mesclar na `main`.** Esta spec foi escrita em 19 e 20/09 e ficou numa
> branch local até esta data. No intervalo, três fatos passaram a pesar contra o centro dela. Ficam
> registrados aqui, e o destino da feature fica com quem governa o backlog:
>
> - **A Constituição** diz que *"Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar
>   modalidade, fundamento, percentual, cálculo, arredondamento, distribuição e vigência"*. Esta spec
>   não discute a cláusula, e o `FR-568` põe fundamento e percentual no Edital.
> - **A decisão de 25/09** ([`doc/decisao-recorte-documental.md`](../../doc/decisao-recorte-documental.md)),
>   aceita pelo usuário, lê a cláusula como impedimento: mover a propriedade da Modalidade para o
>   Edital *"está fora de questão"*. É o contrário da `D-001`.
> - **A `044-recorte-transversal-documental`** foi escrita sobre essa decisão e declara que não move a
>   Modalidade para o Edital. Pelo código da Modalidade (`FR-700`, `FR-701`), ela especifica o que o
>   `FR-571` pede, sem trocar a Modalidade de nível. A implementação estava no PR #173, ainda aberto
>   nesta data.
>
> A decisão de 25/09 **não** alcança a `D-G5`, a Retificação que acrescenta Modalidade (US2). Ela
> segue não executada: a tela da Retificação ainda declara que Modalidades não são definidas ali. E
> esta spec a amarra ao catálogo (`D-003`). Se o catálogo cair, a `D-G5` precisa de outro caminho, e
> essa é a pergunta que fica aberta.
>
> A spec entra na `main` como registro, e para que a faixa que a `040` pulou por reserva — do
> `FR-568` ao `FR-580`, do `SC-201` ao `SC-205`, `UX-067` e `UX-068` — passe a existir.

## O problema

**A Modalidade de Concorrência nasce dentro do Perfil de Vaga.** Um Edital com 16 polos tem
dezesseis PcDs diferentes — não uma PcD oferecida em dezesseis lugares. E como o **fundamento
normativo** é um-para-um com a Modalidade, o elaborador declara a mesma lei uma vez por Perfil:

> Edital de 16 polos com duas reservas → **32 declarações** do mesmo fundamento, percentual, cálculo,
> arredondamento, distribuição e regras de convocação.

**Quatro desses campos não são retificáveis.** Um erro de arredondamento numa das 32 cópias vira
divergência normativa entre polos do mesmo Edital, sem Retificação que conserte, e nada acusa.

Três consequências que quem elabora sente:

| O que ele quer | O que consegue hoje |
|---|---|
| declarar a Lei 12.711 uma vez | declarar uma vez por Perfil, e manter as cópias iguais na mão |
| exigir laudo de todo PcD | exigir 16 vezes, ou exigir de todo mundo |
| acrescentar uma reserva a Edital publicado | **impossível** — a tela diz, com todas as letras, que Modalidades não são definidas ali, e não oferece saída |

O terceiro é a única intenção que a auditoria de convergência de 20/09 classificou no pior nível de
encontrabilidade, e a descreve como *"um Edital publicado sem conserto possível"*.

## O que muda

> **O Edital declara suas Modalidades de Concorrência uma vez, cada uma com seu fundamento
> normativo. Cada Perfil declara quais delas oferece e quantas vagas reserva para cada uma.**

É a ordem em que os Editais reais são escritos: a lei primeiro, o quadro de repartição depois.
Nenhum identificador muda, e nenhum Edital publicado passa a dizer coisa diferente.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A lei declarada uma vez (Priority: P1)

O elaborador abre um Edital com 16 polos. Declara **uma** PcD e **uma** PPI, cada uma com seu
fundamento, percentual e regra de arredondamento. Depois, em cada Perfil, marca quais reservas
aquele polo oferece e quantas vagas destina a cada uma.

**Why this priority**: é a feature. Tudo o mais decorre dela.

**Independent Test**: declarar um Edital com três Perfis e duas reservas; conferir que o fundamento
foi escrito duas vezes e não seis; conferir que cada Perfil reparte suas vagas entre as reservas que
escolheu; publicar.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** o elaborador declara uma Modalidade com seu fundamento normativo, **Then** ela fica disponível para todos os Perfis do Edital, e o fundamento é escrito uma vez só.
2. **Given** um Edital com duas Modalidades declaradas, **When** um Perfil oferece apenas uma delas, **Then** o Quadro de Vagas daquele Perfil só admite linha para a Modalidade oferecida.
3. **Given** um Edital com quatro Perfis que oferecem a mesma reserva, **When** o elaborador exige um Documento daquela Modalidade, **Then** a exigência alcança os candidatos dos quatro Perfis, escrita uma vez.
4. **Given** um Edital de Perfil único, **When** o elaborador o declara do começo ao fim, **Then** ele não encontra passo novo — declara a Modalidade e a oferece, como hoje.

---

### User Story 2 — Acrescentar reserva a Edital publicado (Priority: P2)

O Edital foi publicado sem a reserva de PPI. Hoje isso não tem conserto: a tela da Retificação
declara honestamente que Modalidades não são definidas ali, e o elaborador fica sem saída.

Ele passa a poder acrescentar a Modalidade ao Edital por Retificação, e fazer os Perfis a oferecerem
com suas linhas no Quadro.

**Why this priority**: é a decisão de governança `D-G5`, e a auditoria de 20/09 a elegeu o terceiro
investimento do produto — a única pendência que descreve Edital publicado sem conserto. Ela **não é
spec própria**: a Retificação já sabe acrescentar Perfil, Cronograma e Anexo, e o que faltava era a
Modalidade ser uma coisa do Edital para entrar nessa lista.

**Independent Test**: publicar um Edital com uma reserva; propor Retificação que acrescenta outra e
faz dois Perfis a oferecerem; conferir que a ordem, a ocupação e a convocação já emitidas não se
alteram.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** uma Retificação acrescenta Modalidade ao Edital, **Then** ela é aceita e a Modalidade passa a existir a partir da publicação da Retificação.
2. **Given** a mesma Retificação, **When** ela faz um Perfil oferecer a Modalidade nova com linha no Quadro, **Then** as duas declarações valem no mesmo ato.
3. **Given** ordem, ocupação ou convocação já emitidas, **When** a Retificação é publicada, **Then** nenhuma delas se altera: o ato histórico continua lendo a norma que citou.
4. **Given** a tela da Retificação, **When** o elaborador procura o que pode acrescentar, **Then** Modalidade aparece ao lado de Perfil, Cronograma e Anexo, e a frase que declarava o beco deixa de existir.

---

### User Story 3 — O Edital de ontem continua dizendo o mesmo (Priority: P3)

Candidato, comissão e auditoria precisam ler um Edital publicado antes desta mudança exatamente como
ele foi publicado. **E o sistema não adivinha**: duas Modalidades chamadas "PcD" em Perfis
diferentes continuam sendo duas, porque afirmar que são a mesma seria inventar declaração que
ninguém fez.

**Why this priority**: é garantia constitucional. Verificável sozinha, e não bloqueia as outras.

**Independent Test**: tomar cada Edital publicado, ler seu conteúdo, e conferir que cada Modalidade
continua com o mesmo identificador, o mesmo fundamento e o mesmo Perfil que a oferece.

**Acceptance Scenarios**:

1. **Given** um Edital publicado antes desta feature, **When** seu conteúdo é lido, **Then** cada Modalidade antiga aparece como Modalidade do Edital oferecida por aquele Perfil, com identificador preservado, sem fusão com nenhuma outra.
2. **Given** inscrições, ordens e convocações que apontam Modalidade, **When** o conteúdo é lido na forma nova, **Then** todas continuam apontando o mesmo identificador.

---

### Edge Cases

- **Modalidade declarada e oferecida por nenhum Perfil**: legítima na elaboração — o elaborador declara a lei antes de repartir —, e recusada na publicação, porque Edital não publica reserva que ninguém oferece.
- **Linha do Quadro apontando Modalidade que o Perfil não oferece**: recusada. É a verificação nova que a mudança de nível torna necessária, e não existia antes porque a Modalidade estava dentro do Perfil.
- **Retificação que remove Modalidade do catálogo**: só se nenhum Perfil a oferecer, pela mesma regra que já protege a linha do Quadro.
- **Retificação que retira a Modalidade de um Perfil**: permanece como hoje — exige declarar, no mesmo ato, o que acontece com a linha do Quadro.
- **Duas grafias da ampla concorrência**: um Edital que declare uma Modalidade de ampla concorrência **e** a linha geral do Quadro está dando dois nomes ao mesmo recorte. Recusado na publicação nova; conteúdo já publicado é lido como está.
- **Perfil acrescentado por Retificação**: escolhe entre as Modalidades já declaradas, e não redeclara lei nenhuma. É o ganho da US1 aparecendo na US2.

## Requirements *(mandatory)*

### Functional Requirements

**O catálogo (US1)**

- **FR-568**: O Edital MUST declarar suas Modalidades de Concorrência no próprio Edital, cada uma com seu fundamento normativo declarado uma única vez.
- **FR-569**: Cada Perfil de Vaga MUST declarar quais Modalidades do Edital oferece, e repartir suas vagas entre elas.
- **FR-570**: O sistema MUST recusar a publicação de linha do Quadro de Vagas que aponte Modalidade não oferecida pelo Perfil a que a linha pertence, e de Modalidade que nenhum Perfil ofereça.
- **FR-571**: Um Documento Exigido restrito a uma Modalidade MUST alcançar os candidatos de todos os Perfis que a oferecem.
- **FR-572**: A ampla concorrência MUST continuar sendo o recorte sem Modalidade declarada, e o sistema MUST recusar a publicação de Edital que declare Modalidade de ampla concorrência e linha geral do Quadro como dois nomes do mesmo recorte.
- **FR-573**: A identidade da Modalidade MUST ser preservada: inscrição, ordem, ocupação e convocação continuam apontando o mesmo identificador de hoje.

**Acrescentar a Edital publicado (US2)**

- **FR-574**: A Retificação MUST poder acrescentar Modalidade de Concorrência ao Edital publicado.
- **FR-575**: A Retificação MUST poder fazer um Perfil passar a oferecer Modalidade já declarada, com a respectiva linha no Quadro de Vagas, no mesmo ato.
- **FR-576**: Acrescentar Modalidade MUST NOT alterar ordem, ocupação ou convocação já emitidas; o ato histórico continua lendo a norma que citou.
- **FR-577**: A superfície da Retificação MUST deixar de declarar que Modalidades não são definidas ali, e MUST oferecê-las entre o que se pode acrescentar.

**Continuidade (US3)**

- **FR-578**: Conteúdo publicado antes desta feature MUST continuar afirmando exatamente o que afirmava: cada Modalidade declarada dentro de um Perfil é lida como Modalidade do Edital oferecida por aquele Perfil, com identificador preservado.
- **FR-579**: O sistema MUST NOT fundir Modalidades de Perfis diferentes automaticamente, ainda que compartilhem nome ou código.

**Transversal**

- **FR-580**: Esta feature MUST NOT criar capacidade de autorização nova; quem declara Modalidade é quem já declara Perfil e Quadro de Vagas.

### Key Entities

- **Modalidade de Concorrência**: o recorte de concorrência do Edital — PcD, PPI, uma cota legal —, com seu fundamento normativo, percentual e regras de cálculo. Passa a ser declarada uma vez, no Edital.
- **Oferta do Perfil**: a declaração de que um Perfil concorre por uma Modalidade do Edital, com as vagas que reserva a ela. É o que hoje se lê como "a Modalidade daquele Perfil".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-201**: Num Edital de 16 Perfis com duas reservas, o fundamento normativo é declarado **2 vezes**, contra 32 hoje.
- **SC-202**: Acrescentar Modalidade a Edital publicado deixa de ser impossível — a intenção passa a ter caminho completo pela interface.
- **SC-203**: Nenhum Edital já publicado muda de sentido: a leitura do conteúdo é idêntica à de hoje, em todos eles, com todos os identificadores preservados.
- **SC-204**: O elaborador de um Edital de Perfil único percorre o mesmo número de decisões obrigatórias de hoje.
- **SC-205**: Um erro no fundamento de uma reserva é corrigível **num lugar só**, e a correção alcança todos os Perfis que a oferecem.

### Garantias de interface

- **UX-067**: A tela do Perfil oferece as Modalidades do Edital como escolha, e não como cadastro a repetir; o fundamento normativo é exibido onde foi declarado, não copiado no Perfil.
- **UX-068**: A tela da Retificação lista Modalidade entre o que se pode acrescentar, ao lado de Perfil, Cronograma e Anexo.

## Decisões

### D-001 — A Modalidade é declarada no Edital; o Perfil adere e reparte

O caminho barato — manter a Modalidade dentro do Perfil e acrescentar um rótulo de família — foi
medido e descartado. Ele resolveria o sintoma do documento e deixaria **as 32 cópias do fundamento
no lugar**, colando uma etiqueta por cima: exatamente a segunda verdade que este repositório passou
semanas removendo. A medição mostrou que o modelo honesto é mais barato do que aparentava, porque
**nada deduz o Perfil a partir da Modalidade** e a espinha do produto guarda o identificador em par
com o Perfil.

### D-002 — A elevação preserva identidade e não funde nada

Cada Modalidade declarada dentro de um Perfil é lida como Modalidade do Edital, com o identificador
que já tinha, oferecida por aquele Perfil. Duas PcDs de Perfis diferentes continuam sendo duas.
Fundi-las seria afirmar uma declaração que o elaborador não fez, e o ganho da feature é para quem
declara de agora em diante.

### D-003 — A `D-G5` entra aqui, e não em spec própria

A Retificação já acrescenta Perfil, Cronograma e Anexo — o que faltava à Modalidade era **ser uma
coisa do Edital** para caber nessa lista. Entregar o catálogo sem a Retificação reproduziria, na
forma nova, o único beco sem saída que a auditoria de 20/09 mediu.

### D-004 — A grafia dupla da ampla concorrência é recusada daqui para a frente

A auditoria mediu um Edital real com **três nomes para duas coisas**: a Modalidade de ampla
concorrência declarada e sem vagas, a linha geral do Quadro, e o recorte nulo que o sorteio
ordenou. Esta feature é onde o catálogo nasce, e portanto é onde a duplicidade se recusa. Recusa-se
a publicação **nova**; conteúdo publicado é ato imutável e continua sendo lido como está.

## Assumptions

- Medido em 20/09/2026 contra a `main` `b97cc0d`: **nenhum lugar do produto ou dos testes deduz o Perfil a partir da Modalidade**. Inscrição, classificação, ocupação e convocação guardam o identificador como valor, sempre em par com o Perfil — e o da inscrição deliberadamente não é chave estrangeira.
- Medido na mesma data: a elevação do conteúdo publicado é **leitura**, não reescrita — o ato guardado permanece intocado. O mapa de mutabilidade indexa por coleção e campo, indiferente ao nível, e suas entradas da Modalidade continuam valendo.
- Medido na mesma data: `SECOES_QUE_ACRESCENTAM` são hoje Perfis, Cronograma e Anexos; Modalidade está entre os tipos desenhados **aninhados** sob o Perfil.
- Medido na mesma data: o fundamento normativo é um-para-um com a Modalidade, e quatro de seus campos não são retificáveis.
- A faixa desta spec abre em **FR-568**, **SC-201** e **UX-067**. Teto medido em 20/09/2026 na `main` e em todas as worktrees: FR-567 / SC-200 / UX-066.
- Esta feature seria o **primeiro degrau de elevação que move uma coleção de nível**, em vez de acrescentar campo — mecanismo novo, e o plano deve tratá-lo como tal.
- O trabalho é **largo e raso**: concentra-se na camada de elaboração e nas fixtures de teste, e não na espinha do produto.

## Fora de escopo

- **O alcance da Etapa de Avaliação** — a Etapa vale hoje para todos os candidatos do Edital, e quem está fora do interesse dela é avaliado e pode ser eliminado por ela. Estava nesta spec e **saiu por medição**, como a redação anterior previa: com a `D-G5` incorporada, a Modalidade passou a ser mudança de modelo e as duas não cabem juntas. Fica registrada como a candidata seguinte, e o defeito é mais grave para o candidato do que para o elaborador.
- **O vocabulário** — "Perfil de Vaga" serve mal ao Edital de aluno. Discussão legítima, spec própria.
- **Polo como eixo** (`ACH-60`, `AX-6`) — a auditoria de 20/09 recomenda não abstrair polo antes de ter o Edital real de múltiplos polos em mãos. Esta feature não abstrai polo: move a Modalidade.
- Os quatro defeitos da `038`; as sete recusas da `D-G2`; a `FR-461` impeditiva (`D-G1`); a ocorrência externa do sorteio (`D-G3`); o renderizador normativo único (`E-3`); e o restante da validação cruzada entre fontes (`E-4`), de que a `D-004` fecha apenas um caso.

## Nota de sequenciamento

A auditoria de 20/09 ordena os próximos investimentos assim: **(1)** fechar os quatro defeitos da
`038` — um deles, `N-03`, é regressão que oferece a todo papel um caminho que a autorização recusa;
**(2)** derivar o campo declarado derivado; **(3)** esta feature. Executá-la antes das duas primeiras
é decisão de quem governa o backlog, e está registrada aqui para que a escolha seja consciente e não
esquecimento.
