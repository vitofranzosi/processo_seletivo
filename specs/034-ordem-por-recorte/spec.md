# Feature Specification: Ordem por recorte em marco computado

**Feature Branch**: `034-ordem-por-recorte`

**Created**: 2026-09-18

**Status**: Draft

**Input**: Reauditoria exploratória de UX de 2026-09-16 —
[doc/auditoria-exploratoria-ux-2026-09-16.md](../../doc/auditoria-exploratoria-ux-2026-09-16.md) —,
achado **ACH-47** (**S4 / P0**, seções 0 e 5-bis.1), problema estrutural **E-1** (a cauda do certame
não fecha), nomeado na melhoria **13.7** entre as três formas de publicar um Edital que o sistema
não consegue executar. Estado reconferido no código em 18/09/2026, contra a `main` `af97d4c` —
[doc/reavaliacao-ux-2026-09-18.md](../../doc/reavaliacao-ux-2026-09-18.md).

> **Faixa de identificadores.** Esta spec abre em **FR-490** e **SC-169**. O teto foi medido em
> 18/09/2026 em **todas as worktrees desta máquina**, inclusive nas que têm trabalho não comitado, e
> é `FR-489` / `SC-168` / `UX-061`. **Nenhum `UX-` é aberto aqui** — o teto de `UX-` permanece em
> `UX-061`. As **decisões** reiniciam em `D-001`, porque são lidas dentro da feature que as produziu.

## Por que esta feature existe

O sistema deixa declarar as Modalidades de Concorrência, **valida a soma** do Quadro de Vagas,
**publica a reserva com fundamento legal** e **recebe e identifica** inscrições por modalidade. E
então não consegue apurar nem convocar por recorte reservado nenhum.

A cadeia da convocação tem quatro elos — **ordem → corte → ocupação → convocação** — e o primeiro
não existe fora da ampla concorrência. A classificação produz **uma ordem única**, com a modalidade
apenas como coluna. O corte do recorte reservado responde *"Este recorte não tem ordem emitida: não
há o que cortar"*. A ocupação oferecia três botões idênticos, dos quais dois sempre falhavam.

**Não foi descuido.** A `021` tratou cotas no sorteio; a `015` não tratou na classificação pontuada,
e `classificacao/application/emissao.py` diz isso por escrito: *"Um ato computado é sempre o de
ampla concorrência — só o sorteio emite por lista"*. Foi decisão de escopo, e esta feature é a que
a revisita.

**O que a medição de 18/09 mudou na leitura do tamanho.** A auditoria classificou o `ACH-47` como
esforço **G**. A medição contra o código mostra que quase tudo que ele precisa já existe:

| O que a feature precisa | Estado hoje | Onde se conferiu |
|---|---|---|
| Uma raiz de ato **por lista** no modelo | ✅ existe, com restrição de unicidade própria | `classificacao/models.py`, as duas `UniqueConstraint` condicionadas por `lista_id` |
| Precedente de emissão por lista | ✅ o sorteio faz desde a `021`, com uma raiz por lista | confirmado pela interface na auditoria, achado `PP-113`, com quatro recortes |
| Corte, apuração, faixa e reversão por lista | ✅ parametrizados | `ocupacao/models.py`, `causar_faixa.py`, `movimento.py` |
| A doutrina normativa de quem ocupa o quê | ✅ implementada, citando o item 8.9 do 28/2026 | `ocupacao/application/emissao.py` |
| Um ponto único que responde "este marco emite aqui?" | ✅ criado pela `032` **para esta feature** | `editais/domain/marcos.py::emite_ordem_no_recorte` |
| **A emissão da ordem por recorte** | ❌ **não existe** | `classificacao/application/emissao.py`, `lista_id=None` |
| **O cálculo por recorte** | ❌ **não existe** | `classificacao/application/calculo.py::calcular_ordem` não recebe recorte |
| **Navegação entre recortes nas telas** | ❌ **não existe** | a tela de ordenação ignora `?lista=`, testado pela auditoria |

**Isso não torna a feature pequena — torna-a delimitada.** O trabalho é ligar duas pontas que já
existem, seguindo um precedente que já está no repositório, em vez de inventar mecanismo.

### O que a medição achou e ninguém tinha escrito

**Existem hoje duas derivações do conjunto de recortes de um marco, e elas discordam.**

| Derivação | Inclui a Modalidade declarada como ampla? | Razão escrita no código |
|---|---|---|
| `sorteios/application/previa.py::recortes_do_marco` | **sim** — todas as modalidades declaradas | e por isso ela precisou desambiguar rótulos: *"a tela mostrava dois blocos homônimos"* |
| `ocupacao/application/selectors.py::recortes_do_marco` | **não** — exclui `generalCompetitionModalityId` | *"a quantidade dela mora na linha geral, e dar-lhe linha declararia duas vezes o mesmo número"* |

Duas funções com **o mesmo nome**, em módulos diferentes, respondendo coisas diferentes para a mesma
pergunta — e a medição do `plan` encontrou ainda um **terceiro** tratamento, no corte, que apelida a
Modalidade declarada como ampla para a linha geral ([research.md](research.md), `R-3`). A feature tem de escolher uma — e escolher errado produz uma ordem emitida para um recorte
que a ocupação não tem linha para consumir: **um ato publicado que não leva a lugar nenhum**, que é
uma versão pior do defeito que esta spec existe para fechar.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A ordem do recorte reservado passa a existir (Priority: P1)

Quem conduz o certame de um Edital com reserva de vagas abre a classificação de um marco computado e
emite a ordem **de cada recorte** — a da ampla concorrência e a de cada Modalidade reservada —, cada
uma com raiz, sucessão e proveniência próprias.

**Why this priority**: é o primeiro elo da cadeia, e os outros três já existem. Sem ele, nada do
resto pode ser demonstrado; com ele, a apuração e a convocação passam a ter do que se alimentar.

**Independent Test**: num Edital com Quadro de Vagas 7/1/2, emitir a ordem do recorte reservado e
conferir que o ato nasce com a lista daquele recorte, que o vigente do outro recorte não foi tocado,
e que a ordem da ampla continua idêntica à que se emitia antes.

**Acceptance Scenarios**:

1. **Given** um Perfil que declara reserva e um marco que não sorteia, **When** quem conduz emite a
   ordem do recorte reservado, **Then** nasce um ato de ordenação **daquele recorte**, e o ato da
   ampla concorrência permanece vigente e inalterado.
2. **Given** o mesmo marco, **When** se lê a ordem da ampla concorrência, **Then** ela contém **todos**
   os inscritos do Perfil, inclusive os autodeclarados da Modalidade reservada.
3. **Given** um Perfil **sem** Modalidade reservada alguma, **When** se emite a ordem, **Then** nada
   muda: uma ordem só, sem lista, exatamente como antes desta feature.
4. **Given** um marco que ordena por sorteio, **When** se abre a classificação, **Then** o caminho
   continua sendo o do sorteio, e esta feature não o alcança.

---

### User Story 2 - As telas levam quem conduz a cada recorte (Priority: P2)

As telas de ordenação e de corte passam a dizer **em qual recorte se está** e a oferecer caminho para
os outros, em vez de mostrarem sempre o da ampla e ignorarem o pedido por outro.

**Why this priority**: uma ordem que existe e que ninguém alcança pela tela é o `ACH-40` outra vez,
com outra roupa — e este projeto acabou de pagar por essa lição na `033`. Mas ela depende da `US1`:
não há recorte a navegar antes de haver recorte.

**Independent Test**: abrir a tela de ordenação de um marco com reserva, conferir que os recortes
aparecem nomeados, e que seguir o caminho oferecido para o recorte reservado abre **aquele** recorte
— com o `href` lido da própria página, sem endereço montado à mão.

**Acceptance Scenarios**:

1. **Given** um marco com três recortes, **When** se abre a ordenação, **Then** a tela nomeia o
   recorte em que se está e oferece caminho para os outros dois.
2. **Given** um recorte que ainda não tem ordem emitida, **When** se abre a tela dele, **Then** ela
   diz **o que falta e como emitir**, em vez de *"não há o que cortar"*.
3. **Given** um recorte cujo identificador não corresponde a Modalidade alguma do Perfil, **When**
   se pede aquele recorte, **Then** a resposta é a de objeto inexistente.

---

### User Story 3 - O produto para de avisar sobre um problema que deixou de existir (Priority: P3)

A Revisão deixa de avisar que a reserva não tem via de apuração onde a via passou a existir, a tela
de ocupação volta a oferecer a apuração naquele recorte — e o guarda que respondia àquela pergunta
sai, em vez de ficar respondendo sempre sim.

**Why this priority**: é a menor em código e a maior em coerência. A `032` entregou três requisitos
que existem **porque** a emissão por lista não existia; deixá-los de pé depois desta feature faz o
produto afirmar duas coisas contraditórias sobre o mesmo fato — e a que mente é a que o operador lê
primeiro.

**Independent Test**: no mesmo Edital 7/1/2, conferir que a Revisão não produz mais o aviso da
reserva, e que a tela de ocupação do recorte reservado oferece a apuração em vez da frase que manda
apurar fora do sistema.

**Acceptance Scenarios**:

1. **Given** um Edital com reserva em marco computado, **When** se abre a Revisão antes de publicar,
   **Then** o aviso `reserved_row_without_ordering` **não** é produzido.
2. **Given** o mesmo Edital publicado e com a ordem do recorte emitida, **When** se abre a ocupação
   daquele recorte, **Then** a ação de apurar é oferecida, e ela funciona.
3. **Given** um Edital **do acervo**, publicado antes desta feature, **When** se abre qualquer tela
   dele, **Then** o conteúdo publicado e o documento não mudaram.
4. **Given** a feature entregue, **When** se procura o predicado que respondia *"este marco emite
   ordem neste recorte?"*, **Then** ele **não existe mais** — nem o campo derivado dele, nem o teste
   que provava o espelho igual à fonte (`FR-501a`). Se a medição tiver mostrado que ele ainda varia,
   **Then** ele existe **e a razão está escrita**.

---

### Edge Cases

- **Recorte reservado sem nenhum autodeclarado** — **decidido**, `FR-492a`. A ordem vazia é
  emitível e nunca automática. A ausência de ato é indistinguível de "ainda não emitiram", e a tela
  precisa poder dizer que ninguém concorreu ali.
- **A Modalidade declarada como ampla concorrência.** É a grafia-armadilha: tem nome de modalidade,
  não tem vagas próprias, e a quantidade dela mora na linha geral. Ela **não** é recorte reservado, e
  tratá-la como tal declararia duas vezes o mesmo número.
- **Edital já publicado com reserva e ordem única emitida.** Publicação é ato imutável e ordem
  emitida não se reescreve. O que a tela mostra para ele?
- **Retificação que acrescenta uma Modalidade depois de a ordem da ampla já ter sido emitida** —
  **decidido**, `FR-494a`. O recorte novo nasce sem ordem; a ordem da ampla **continua vigente**.
- **Empate residual que atravessa a fronteira do alvo em dois recortes ao mesmo tempo.** O mesmo
  candidato pode estar empatado nas duas ordens, e o julgamento do empate vale para as duas.
- **Marco que sorteia.** Já emite por lista desde a `021`, e esta feature **não o toca**: a
  obrigação é de **não interferência**, e não de convergência. O caminho computado não pode alterar o
  que o sorteio deriva, emite ou apresenta — e a divergência já conhecida entre as duas derivações
  **permanece registrada** (`FR-491a`), em vez de ser corrigida de passagem.
  *A redação anterior dizia que nada podia fazê-las divergir, o que contradizia a própria `FR-491a`.
  Era voz da versão em que a `FR-491` ainda alcançava o sorteio.*

---

## Requirements *(mandatory)*

### Functional Requirements

#### A ordem por recorte

- **FR-490**: Marco classificatório que **não** ordena por sorteio, em Perfil que declara Modalidade
  de Concorrência reservada, MUST emitir **uma ordem por recorte** — a da ampla concorrência e a de
  cada Modalidade reservada —, cada uma com raiz, sucessão e proveniência próprias. É o mesmo desenho
  que a `021` já aplica ao sorteio, e não um mecanismo novo.
- **FR-491**: O conjunto de recortes de um marco MUST ser derivado em **um lugar só**, e a
  classificação e a ocupação MUST obter o conjunto desse mesmo lugar. Uma ordem emitida para recorte
  que a ocupação não consome é um ato publicado que não leva a lugar nenhum.
  *O recorte é o da classificação e o da ocupação porque são os dois lados de um mesmo ato — quem
  emite e quem apura.* A medição encontrou **três** tratamentos do mesmo fato, e não dois: a ocupação
  não considera recorte a Modalidade declarada como ampla, o corte a considera e a **apelida** para a
  linha geral, e o sorteio lhe dá **recorte próprio**. Os dois primeiros são compatíveis — o corte
  aceita o apelido e nunca o oferece. O terceiro não é.
- **FR-491a**: A divergência do sorteio MUST ser **registrada**, com a medição que a demonstra, e
  MUST NOT ser corrigida por esta feature.
  > **Ratificado em 18/09/2026 por quem governa o backlog** (`D-004`). O escopo estreito é decisão
  > tomada, e não proposta: a `034` alinha **classificação e ocupação**, e o sorteio permanece como
  > está, com a divergência registrada. Alinhá-la mudaria telas de uma feature que funciona, e o
  tamanho da mudança é decisão de quem governa o backlog — não de quem implementa. Ampliar a
  `FR-491` para alcançar o sorteio foi a pergunta que a parada de escopo fez, e a resposta está em
  `D-004`: **não**, e por causa das cadeias históricas da `021`, não por causa do tamanho do código.
- **FR-492**: O universo do recorte reservado MUST ser quem se autodeclarou naquela Modalidade, **e
  essas mesmas pessoas MUST permanecer no universo da ampla concorrência** (`D-001`). A cota preenche
  o que a ampla não preencheu; quem classifica pela ampla apenas não é computado no preenchimento da
  reservada, que é o que `ocupacao/application/emissao.py` já implementa citando o item 8.9 do
  Edital 28/2026.
- **FR-492a**: Recorte sem nenhum autodeclarado MUST admitir **ordem vazia**, emitida por quem
  conduz e **nunca automaticamente**, e a tela dele MUST dizer que ninguém concorreu ali — em vez de
  parecer pendência. Emitir continua sendo ato: o que muda é que passa a existir um ato que declara a
  ausência, que é fato normativo e é publicável. Sem ele, *"ninguém se inscreveu por esta cota"* e
  *"ainda não emitiram"* são indistinguíveis na tela, e a diferença entre as duas é quem tem trabalho
  a fazer.
- **FR-493**: A ordem da ampla concorrência MUST continuar sendo o universo inteiro do Perfil, e
  Perfil que não declara reserva MUST produzir exatamente a mesma ordem que produzia antes desta
  feature. É requisito de **não-regressão**, e é o que impede a feature de mudar resultado de Edital
  que ela não deveria alcançar.
- **FR-494**: Emitir a ordem de um recorte MUST NOT constituir ato sobre os demais. Cada recorte tem
  vigência e sucessão próprias, e a obsolescência de um MUST NOT obsoletar os outros.
- **FR-494a**: Retificação que **acrescenta** uma Modalidade depois de a ordem da ampla já ter sido
  emitida MUST NOT obsoletar essa ordem. O recorte novo nasce **sem ordem**; o da ampla segue
  vigente.
  *A razão é a `FR-492`, e não uma escolha nova:* o universo da ampla é **todo mundo**, e acrescentar
  uma Modalidade não retira nem acrescenta ninguém a ele — a ordem que foi emitida continua sendo a
  ordem daquele universo, sob a norma que o ato citou. O que **pode** ficar obsoleto é a **apuração
  da ocupação**, porque o Quadro de Vagas mudou de números, e para isso já existe detecção de
  obsolescência: ela não precisa desta feature e não deve ser reinventada por ela.
- **FR-495**: A confirmação do cálculo — a assinatura que impede emitir sobre leitura vencida — MUST
  ser **do recorte**. Uma assinatura comum deixaria emitir no recorte B uma leitura feita no A.
- **FR-496**: O cálculo MUST continuar sendo leitura pura fora do comando transacional: abrir a tela
  de qualquer recorte, quantas vezes for, MUST NOT constituir ato algum.

#### As telas

- **FR-497**: As telas de ordenação e de corte MUST nomear o recorte em que se está e MUST oferecer
  caminho para os demais recortes do mesmo marco.
- **FR-498**: Recorte sem ordem emitida MUST dizer **o que falta e onde se faz**, e MUST NOT
  responder apenas que não há o que cortar. A ausência de ordem é um estado do percurso, não um erro.
- **FR-499**: Pedido por recorte que não corresponde a Modalidade alguma do Perfil MUST responder
  como objeto inexistente — e não como recorte vazio.

#### A coerência com a `032`

- **FR-500**: **Enquanto a pergunta *"este marco emite ordem neste recorte?"* tiver resposta que
  varia**, ela MUST ser respondida por **um ponto só** — o que a `032` criou exatamente para isto —,
  esse ponto MUST ser **espelho** da regra real, que vive na emissão, e MUST existir teste que prove
  que os dois dizem a mesma coisa. A validação da publicação e a tela de ocupação consomem o espelho;
  **a emissão é a fonte, e não o consome** — pedir que ela pergunte ao próprio reflexo seria circular.
  Espelho que se descola da fonte é a Revisão avisando sobre um recorte que a tela oferece, que é o
  defeito que o ponto único existe para impedir.
  *A condicional do início não é decoração:* a `FR-501a` encerra a pergunta quando ela deixa de
  variar, e as duas seriam contraditórias sem ela — uma mandando manter o ponto e testá-lo, a outra
  mandando removê-lo. **A `FR-500` governa a travessia; a `FR-501a` governa o destino.** Enquanto o
  predicado existir, o teste de igualdade existe com ele, e sai junto.
  *E uma correção anterior, que fica registrada:* a primeira redação dizia que a emissão também
  consumiria o predicado. Não é o caso — o `research.md` `R-4` já contava dois consumidores.
- **FR-501**: O aviso de reserva sem via de apuração é **aposentado**, e não estreitado. A redação
  anterior dizia *"ou deixa de existir, ou passa a nomear um caso estritamente menor"*, e uma spec que
  oferece duas saídas não está determinada: a escolha mudaria quais testes mudam, e ela estava sendo
  adiada para dentro da implementação. **Não sobra caso.** Todo marco ou sorteia — e o sorteio sempre
  emitiu por lista — ou é computado, e o computado passa a emitir. Perfil com reserva e sem marco
  algum já é impedimento da `032`, por outra regra.
- **FR-501a**: O predicado que passar a responder **sempre a mesma coisa** MUST ser removido, junto
  com o campo derivado dele e com o teste de igualdade que a `FR-500` exige enquanto ele existe — e
  não deixado no lugar respondendo sempre *sim*. **Quando remover é a `FR-502` que diz**, e ela não é
  repetida aqui de propósito: duas fontes para a mesma regra divergem na primeira edição, que é o que
  a `FR-500` existe para impedir — e cometê-lo entre dois requisitos vizinhos seria o mesmo defeito
  com outra roupa. É consequência direta
  da `FR-501`: um guarda que nunca reprova é pior do que guarda nenhum, porque o próximo a ler o
  código confia nele. Se a medição mostrar que ele **ainda varia** por alguma razão não prevista
  aqui, a razão MUST ser escrita antes de ele ficar.
- **FR-502**: A ação de apurar a ocupação MUST voltar a ser oferecida no recorte reservado que passou
  a ter ordem, **e MUST NOT deixar de ser oferecida em nenhum instante da travessia**. A tela ramifica
  hoje num campo derivado do predicado, e o mecanismo de template deste produto trata **variável
  ausente como falsa**: remover o campo antes de a tela deixar de consultá-lo esconderia a ação e
  exibiria, para todos, a frase que manda apurar fora do sistema — o **inverso** da feature, sem erro
  e sem teste vermelho. A ordem é **tela primeiro, campo depois** — e a frase que hoje diz que a apuração acontece fora do sistema MUST sair de lá, porque
  deixou de ser verdade.

#### O que não muda

- **FR-503**: A ampla concorrência MUST continuar sendo o recorte **sem lista**, a mesma grafia que a
  ordem, o corte, a apuração e o Quadro de Vagas já usam. A Modalidade declarada como ampla MUST NOT
  ser tratada como recorte reservado.
- **FR-504**: Nenhum conteúdo publicado MUST ser reescrito, e nenhuma ordem já emitida MUST ser
  alterada. Edital que já emitiu ordem única com reserva MUST continuar exibindo o que emitiu, e a
  tela MUST dizer o que aquilo é — sem oferecer uma correção que a imutabilidade não permite.
- **FR-505**: A feature MUST NOT criar capacidade nova, papel novo nem regra de autorização nova, e
  MUST NOT exigir migration — o modelo já tem a raiz por lista e a restrição de unicidade que ela
  precisa. Se a necessidade aparecer, é sinal de escopo escorregando, e é conversa de spec.
- **FR-506**: O documento publicado do ato de ordenação MUST dizer **de qual recorte** ele é. Um
  documento que não nomeia o recorte é indistinguível do de outro recorte do mesmo marco.

### Key Entities

- **Recorte**: o par (Perfil, Modalidade de Concorrência) sobre o qual se ordena, se corta, se apura
  e se convoca. O recorte **sem lista** é a ampla concorrência.
- **Ato de Ordenação**: o ato imutável que constitui a ordem de **um** recorte, com raiz e cadeia de
  sucessão próprias.
- **Modalidade de Concorrência**: a declaração normativa do Perfil. A declarada como ampla é rótulo
  da linha geral, e não recorte próprio.
- **Quadro de Vagas**: onde a quantidade de cada recorte é publicada; a da ampla mora na linha geral.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-169**: Um Edital com Quadro de Vagas **7/1/2** e reserva com fundamento legal vai da
  classificação até a convocação **pelos três recortes**, sem que etapa alguma aconteça fora do
  sistema. É o cenário 4 da reauditoria, que parou na convocação.
- **SC-170**: **Zero** ações oferecidas que sempre falham: toda ação de apurar ocupação que a tela
  apresenta conclui, e todo recorte sem ação apresenta a razão em lugar do botão.
- **SC-171**: Edital **sem** Modalidade reservada produz ordem **idêntica** à que produzia antes da
  feature — conferido por comparação da ordem e da proveniência, e não por contagem de linhas.
- **SC-172**: **100%** dos recortes que a classificação deriva coincidem com os que a ocupação deriva,
  para o mesmo marco — verificado por comparação direta das duas listas, e não por inspeção. **São
  duas listas, e não três, porque a `FR-491` obriga duas**: a do sorteio está registrada como
  divergente em `FR-491a`, e medi-la aqui reprovaria a feature por um defeito que ela não causou e
  não tem mandato para corrigir.
- **SC-173**: O acervo publicado atravessa a feature sem mudar **conteúdo, resumo nem documento** —
  nenhum degrau de elevação de versão é acrescentado.
- **SC-174**: **Nenhum** aviso da família da `032` dispara sobre recorte que passou a ter via de
  apuração, e a varredura contra os doze Editais da amostra real registra quais avisos restam.
- **SC-175**: **Nenhuma migration** é criada.

---

## Assumptions

As três decisões abaixo foram fechadas **antes** do planejamento, e por isso são declaradas aqui e
não no `research.md`. Decisão é lida no contexto que a produziu, e a numeração reinicia a cada
feature.

### D-001 — o autodeclarado é ordenado nas duas listas

Decidido em 18/09/2026 por quem governa o backlog.

A ocupação **já depende disso**: ela precisa saber quem ocupou pela ampla para não computá-lo no
preenchimento da reservada, o que só faz sentido se a pessoa estiver nas duas ordens. É também a
prática normativa corrente — a cota preenche o que a ampla não preencheu — e é a leitura favorável ao
candidato, que não perde a chance de classificar pela ampla com nota melhor.

**Alternativas descartadas.** Tirá-lo da ampla simplificaria a apuração, e tornaria a reversão de
vaga sem sentido. Deixar o Edital escolher, por Perfil, acrescentaria decisão à composição — que é o
que a `030` passou uma feature inteira retirando de lá — e dobraria o caso de teste em toda a cauda.

### D-002 — a regra nova vale para quem ainda não emitiu

Publicação é ato imutável e ordem emitida não se reescreve (Princípio II). Edital que já emitiu ordem
única com reserva continua exibindo o que emitiu; o que a tela ganha é dizer **o que aquilo é**, e
não uma correção que a imutabilidade não permite.

É `FR-504`, e a spec **não** oferece migração de acervo.

### D-003 — a coerência com a `032` passa por um ponto só

A `032` escreveu `emite_ordem_no_recorte` como *"uma função só, consumida pela validação e pelo
selector"*, e registrou no próprio docstring que ela **não muda** a decisão de escopo — apenas a
torna perguntável antes da publicação, em vez de descoberta no dia da apuração.

Esta feature muda a **resposta** dela. O aviso da Revisão e a tela de ocupação seguem atrás, sem que
nenhuma segunda pergunta seja criada. É `FR-500`.

### D-004 — o sorteio fica fora, e a razão não é o tamanho do helper

**Ratificado em 18/09/2026 por quem governa o backlog.** A `034` alinha a derivação de recortes da
**classificação** e da **ocupação**. O sorteio permanece como está.

**O que pesou, e não foi a medição.** A medição só mostrou que a derivação do sorteio inclui a
Modalidade declarada como ampla e as outras duas não. Se ampliar fosse trocar um helper, seria barato
e teria entrado. Não é: a `021` construiu, sobre o recorte por lista, **decisões próprias, telas,
relações publicadas, verificadores e cadeias históricas**. Retirar o recorte excedente obriga a
responder **como os atos já emitidos nele continuam alcançáveis** — e ato publicado não se apaga nem
se reescreve, de modo que a resposta não é uma migração, é um desenho.

**Isso é análise própria, e entrar em silêncio na `034` seria exatamente o que a parada de escopo
existe para impedir.** A divergência fica registrada como achado, com o risco nomeado, para a spec
que a tratar — e registrá-la **não** a torna automaticamente a próxima feature.

### As demais premissas

- A derivação única de `FR-491` é **uma escolha entre três que existem**, não uma quarta: a da
  ocupação é a que exclui a Modalidade declarada como ampla, e é a que a cauda consome. A primeira
  redação desta spec dizia *"duas"*, porque a medição ainda não tinha sido feita — está corrigido
  aqui e medido em [research.md](research.md), `R-3`.
- O marco que ordena por sorteio continua com o caminho que tem, **inclusive a derivação de recortes
  dele**. A feature não o toca; ela registra a divergência (`FR-491a`).
- As medições citadas em *Por que esta feature existe* são de 18/09/2026 contra `af97d4c`. **Elas
  devem ser reconferidas no `plan`, e não assumidas** — três medições erradas seguidas na spec `033`
  vieram de ler definição de função em vez de medir.
- A faixa de identificadores deve ser **medida de novo** na hora de escrever a spec seguinte,
  inclusive em worktrees com trabalho não comitado. Este projeto já produziu duas colisões por medir
  só a árvore local.

---

## Out of Scope

Cada um com spec própria:

- **A derivação de recortes do sorteio** — achado **registrado por esta feature**, e não herdado.
  `sorteios/application/previa.py::recortes_do_marco` dá **recorte próprio** à Modalidade declarada
  como ampla; a ocupação não lhe dá linha. O sorteio pode, hoje, emitir para um recorte que a apuração
  não consome — o mesmo defeito que a `FR-491` fecha do lado computado, vivo do lado sorteado, e
  anterior a esta spec.
  **O risco que torna isso spec própria, e não conserto:** a `021` tem decisões, telas, relações
  publicadas, verificadores e cadeias históricas por lista. Retirar o recorte excedente exige definir
  **como os atos históricos dele continuam acessíveis**, e ato publicado não se apaga. Ver `D-004`.
- **O sorteio executável** — `ACH-55` e `ACH-51`. Causa própria: a derivação da ocorrência não é
  computável e a fonte da semente é texto livre onde o valor é criado. O sorteio **já** emite por
  lista; o que falta nele é outra coisa.
- **O renderizador normativo único das telas de ato** — `E-3`, `ACH-39`, `ACH-31`, `ACH-45`,
  melhoria 13.4.
- **O ato de instrução do recurso e o parecer que chega ao candidato** — `ACH-43`, `ACH-42`,
  melhoria 13.2.
- **A validação cruzada entre fontes normativas** — `E-4`, melhoria 13.5.
- **O painel de condução do Processo vivo** — `ACH-25`, melhoria 13.6.
- **As sete recusas de autorização fora das portas** — registradas em
  [inventario-das-negativas.md](../033-navegacao-por-capacidade/inventario-das-negativas.md), com a
  decisão de 18/09/2026 de mantê-las fora.
- **O pacote de microcópia e navegação** — o link do corte que continua condicionado à regra de corte
  (a parte **(c)** da melhoria 13.1), mais `ACH-02`, `ACH-30`, `ACH-08` e `ACH-16`.

---

## Conformidade com a Constituição

**Princípio II — Integridade Normativa, Imutabilidade e Temporalidade.** É o princípio que governa
esta feature. Ela cria **atos**, e ato publicado não se corrige: `FR-504` fixa que nada do acervo é
reescrito, `D-002` declara que a regra nova vale adiante, e `SC-173` é o critério que prende as duas.
`FR-494` garante que a sucessão de um recorte não atravessa para os outros — o que seria alterar por
efeito colateral um ato que ninguém decidiu suceder.

**Princípio VI — Completude de Jornada e Valor Demonstrável.** A capacidade entregue é de jornada e é
observável: um Edital com reserva passa a **chegar à convocação** pelos recortes reservados, o que
hoje não acontece de maneira nenhuma dentro do sistema. `SC-169` é a jornada inteira, e não um passo
dela.

**Princípio IV — Regras Explícitas e Consistência Operacional.** `FR-491` existe por causa deste
princípio: duas derivações homônimas do mesmo conceito, discordando em silêncio, é exatamente a
inconsistência que ele proíbe. `FR-500` é a mesma exigência aplicada ao predicado da `032`.

**Princípio I — Linguagem Ubíqua.** A feature não inventa vocabulário: **recorte**, **lista de
concorrência**, **ampla concorrência** e **ordem** já são do domínio, e `FR-503` fixa que a grafia da
ampla continua sendo a que o resto do sistema usa.
