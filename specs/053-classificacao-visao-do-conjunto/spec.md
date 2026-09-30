# Feature Specification: Classificação — a visão do conjunto e um Perfil por vez

**Feature Branch**: `claude/053-classificacao-visao-do-conjunto`

**Created**: 2026-09-29

**Status**: Draft

**Input**: pedido do usuário de 29/09/2026, depois do merge da `052`: aplicar à etapa Classificação o
princípio que a `052` aplicou aos Perfis — a visão do conjunto e zero ou um editor à vista, sobre o
**mesmo** formulário. A [análise das coleções repetidas](../../doc/analise-ux-colecoes-repetidas-2026-09-29.md),
§10, já a apontava como a candidata seguinte, *"logo depois dos Perfis e pelo mesmo script"*. O teto
de mil campos continua fora: é a `DP-21`, decisão do usuário ainda pendente, com
[achado próprio](../../doc/achado-etapa-perfis-recusa-acima-de-mil-campos.md).

> **Faixa de identificadores.** Abre em **FR-960**, **SC-354** e **UX-123**, contíguos. O teto medido
> em 29/09/2026 em todas as worktrees e branches remotas era 959, 353 e 122, da `052`, já na `main`.
> As decisões reiniciam em `D-001`.

> **Teto proporcional.** Esta feature muda **o que se vê**, e nada do que se grava: nenhum campo,
> nenhuma rota de gravação, nenhuma regra de validação, nenhuma espécie de Alteração. Duas coisas que
> já existiam em outras etapas passam a existir nesta — o bloco de pendências e o rascunho local —,
> porque sem elas a vista deixaria o operador pior do que hoje (`D-005`, `D-007`). O que não nomear
> uma pergunta que a tela passa a responder, ou um modo de falha que ela passa a evitar, é nota de
> tarefa.

---

## Por que esta feature existe

**A etapa Classificação é a soma dos cartões, e o cartão dela é o mais longo da composição.**
Medido no sistema rodando, a 1280×900, com a `052`, no Edital em elaboração do `seed_demo`
multiplicado para 7 Perfis e composto pelo *"Aplicar aos demais Perfis"* da `051`:

| Marco de cada Perfil | Altura da página | Controles visíveis | Campos enviados |
|---|---:|---:|---:|
| sem critério de desempate | 9,5 mil px | 174 | 238 |
| com 2 critérios (o formato do 140/2025 tem 3) | **12,5 mil px** | 244 | 308 |

Cada Perfil custa 1.635 px — o marco, 1.550; cada critério, 202. O primeiro Perfil começa a 830 px,
**no limite da dobra**, e *Salvar* fica a 12,4 mil px.

**O efeito do "aplicar a todos" não se confere.** A `051` fez o marco de um Perfil valer para os
demais com uma prévia e um gesto. Depois de confirmado, conferir que os sete ficaram iguais — ou qual
ficou de fora — é abrir e ler sete cartões de 1,5 mil px. A Revisão agrupa os marcos e diz de onde
cada um veio, mas está sete telas adiante, e não é onde se corrige.

**E nenhum cartão diz de quem é.** A legenda é *"DOC-INFO-03 — Professor de Informática"*: nos seis
polos de Informática, só o número muda. A localidade, que é o que os distingue, não aparece — ao
contrário da etapa Perfis, que a `052` passou a identificar por ela.

**Três lacunas que a vista tornaria perigosas.**

- A recusa do servidor sobre um marco ou um critério **não aponta campo nenhum**: o resumo mostra o
  texto, sem âncora, e hoje o operador acha o marco rolando a página. Com um cartão à vista por vez,
  ele não acharia.
- A etapa **não mostra as pendências** que se resolvem nela — é a única etapa gravável do assistente
  sem o bloco. Uma linha que dissesse *"1 pendência"* não teria onde a pendência se ler.
- A etapa **não tem rascunho local**, e é a de cartões mais longos. Com a vista, é a única etapa
  mestre-detalhe que perderia tudo numa sessão expirada.

**O que não muda.** A etapa continua sendo **um formulário**, gravado inteiro a cada envio. O gesto da
`051` lê o digitado e grava pela gravação da etapa (`D-001` daquela spec), e os marcos fora de vista
continuam indo em todo envio. É o que a `052` decidiu para os Perfis, pela mesma razão: o
`replace_draft` apaga o que não é reenviado.

---

## Clarifications

### Session 2026-09-29

- Q: A linha da tabela é o Perfil ou o marco, quando um Perfil tem mais de um marco? → A: **O
  Perfil** (`D-002`). O marco pertence ao Perfil, o cartão que se abre é o do Perfil e é nele que se
  acrescenta marco; o Perfil sem marco também precisa de linha. Com mais de um marco, cada coluna do
  marco diz um valor por marco, na ordem do Perfil — a mesma comparação *por posição* da Revisão.
- Q: O rascunho local entra nesta spec? → A: **Entra, sem mecanismo novo** (`D-007`). A etapa passa a
  declarar o que as outras quatro já declaram; o servidor já sabe restaurá-la.
- Q: A Situação conta pendências que a etapa não mostra? → A: **Não.** A etapa passa a mostrar o bloco
  de pendências das demais, e a contagem sai dele (`D-005`).
- Q: A partir de quantos Perfis a tabela aparece? → A: **Dois**, como na `052` (`D-002` de lá). O
  cartão da Classificação é mais longo que o dos Perfis, e o argumento só fica mais forte.
- Q: O método do sorteio comum entra na tabela? → A: **Não.** Ele é do Edital e declarado uma vez;
  fica fora da tabela, entre ela e o editor, onde a `052` pôs o controle do Edital (`UX-127`).
- Q: O que a coluna de desempate diz de cada critério — a contagem, ou o que ele compara? → A: **O que
  ele compara, em ordem e com o sentido** (*"maior nota em Prova objetiva"*). A contagem esconderia a
  diferença que se procura, que é a ordem trocada entre dois Perfis.
- Q: A forma da ordem distingue o marco de sorteio que declara método próprio? → A: **Sim**, com a
  frase do resumo do bloco (*"próprio — diverge do comum do Edital"*). O método próprio é o que deixa o
  destino fora do alcance do gesto da `051` (`FR-922` de lá), e é divergência deliberada que precisa
  se ver na comparação.

---

## User Scenarios & Testing *(mandatory)*

**Ator.** Quem elabora o Edital, na etapa Classificação da composição — as mesmas permissões de hoje.
Esta feature não cria papel, permissão nem capacidade.

**Unidade.** O Perfil de Vaga, como linha da tabela e como cartão do editor. O cartão é o de hoje,
inteiro, com todos os marcos do Perfil e o *Acrescentar marco*.

### User Story 1 — Ver o conjunto e trabalhar num Perfil de cada vez (Priority: P1)

Quem elabora abre a etapa Classificação de um Edital de sete polos e vê, antes de qualquer marco, a
tabela dos sete: código, polo, marcos, forma da ordem, corte, critérios de desempate, recurso,
origem e situação. Escolhe *Editar* no polo de Guarapari, troca o prazo do recurso, passa ao seguinte
com *Próximo*, volta à lista e salva uma vez.

**Why this priority**: é a feature. As outras histórias existem para que esta não quebre nada.

**Independent Test**: num Edital em elaboração com 7 Perfis de um marco, abrir a etapa, conferir a
tabela com 7 linhas e nenhum cartão visível; editar o 2º, passar ao 3º por *Próximo*, alterar um
campo em cada, voltar à lista, salvar; conferir que os dois ficaram gravados e os outros cinco
intactos.

**Acceptance Scenarios**:

1. **Given** um Edital com 7 Perfis, **When** quem elabora abre a etapa, **Then** a tabela lista os 7
   na ordem do Edital, e nenhum cartão de Perfil está à vista.
2. **Given** a tabela, **When** quem elabora escolhe *Editar* num Perfil, **Then** o cartão daquele
   Perfil — e só ele — aparece, com o título *"Editando DOC-INFO-04 — Campus Guarapari"*, e a linha
   fica marcada como em edição.
3. **Given** um Perfil em edição com uma alteração, **When** quem elabora escolhe *Próximo*, **Then**
   o cartão seguinte aparece, nada é enviado, nenhuma pergunta é feita, e a linha deixada diz
   *"alterado — não salvo"*.
4. **Given** alterações em dois Perfis, nenhum à vista, **When** quem elabora salva, **Then** os dois
   são gravados, pelo mesmo envio de hoje, e a tela volta com a tabela e nenhum cartão aberto.
5. **Given** um Perfil em edição, **When** quem elabora escolhe *Voltar à lista*, **Then** nenhum cartão
   fica à vista, o digitado continua no formulário, e o foco volta ao *Editar* daquela linha.
6. **Given** um Edital com um Perfil só, **When** a etapa abre, **Then** não há tabela, e o cartão
   aparece aberto, como hoje.
7. **Given** um Perfil em edição, **When** quem elabora troca a forma da ordem, o corte, o recurso ou
   um critério, ou acrescenta ou remove um marco ou um critério, **Then** a linha dele acompanha, sem
   envio.

---

### User Story 2 — Conferir o "aplicar a todos" sem abrir cartão (Priority: P1)

Quem elabora compõe o marco do primeiro polo, aplica-o aos demais, confirma a prévia e volta à etapa.
A tabela mostra, em cada linha, a mesma ordem, o mesmo corte, os mesmos critérios e o mesmo recurso, e
diz, nas seis linhas alcançadas, *"aplicado a partir do Perfil DOC-INFO"*, por quem e quando. O polo
que ficou de fora — ou que foi editado depois — se vê na hora, porque a linha dele não diz isso.

**Why this priority**: é o ganho que a `051` deixou sem tela. O gesto custa um clique; conferir o
resultado custa hoje sete cartões.

**Independent Test**: com 7 Perfis, só o primeiro com marco, aplicar o marco dele aos demais,
confirmar; conferir na tabela as 7 linhas com os mesmos valores e a origem nas 6 alcançadas; editar
e salvar o marco de uma delas; conferir que a origem saiu só daquela linha.

**Acceptance Scenarios**:

1. **Given** o marco de um Perfil aplicado aos demais e confirmado, **When** a tela volta, **Then** a
   tabela está à vista, nenhum cartão está aberto, e cada linha alcançada diz a origem com a frase da
   Revisão.
2. **Given** um marco aplicado e depois editado e gravado, **Then** a linha dele não diz mais a origem.
3. **Given** um marco aplicado e depois alterado na tela, sem salvar, **Then** a linha diz a origem e
   *"alterado — não salvo"*: a origem é do que está gravado.
4. **Given** *Aplicar aos demais Perfis* num marco do Perfil em edição, **When** a prévia volta,
   **Then** ela está no alto da etapa, como hoje, alcança os Perfis fora de vista tanto quanto o
   visível, e o Perfil de origem volta aberto abaixo dela.
5. **Given** a prévia cancelada, **Then** nada é gravado, a tela volta com o digitado, e o Perfil de
   origem volta aberto.

---

### User Story 3 — Nunca travar em silêncio, nunca perder o lugar (Priority: P1)

Quem elabora apaga o código do marco do polo 5, passa ao polo 6 e clica *Salvar*. Em vez de nada
acontecer, o polo 5 abre, com o foco no campo vazio e a mensagem do navegador junto dele. Da mesma
forma, a recusa do servidor sobre um critério do polo 3 volta com o polo 3 aberto e o resumo da
recusa apontando o critério.

**Why this priority**: esconder um cartão que tem campo obrigatório é o modo de falha mais provável
desta feature, e o mais silencioso. O marco tem até oito campos obrigatórios, e o critério, quatro.

**Independent Test**: com 3 Perfis, esvaziar o código do marco do 1º, abrir o 3º, clicar *Salvar*;
conferir, num navegador real, que o 1º abriu, que o foco está no campo e que nada foi enviado.

**Acceptance Scenarios**:

1. **Given** um campo obrigatório vazio num Perfil fora de vista — do marco ou de um critério —,
   **When** quem elabora salva ou avança, **Then** aquele Perfil passa a ser o visível, o foco vai ao
   campo, e a mensagem de validação aparece junto dele.
2. **Given** um campo inválido dentro de um bloco fechado do marco (o prazo do recurso, o alvo do
   corte), **Then** o Perfil e o bloco abrem, e o mesmo acontece.
3. **Given** um envio que o servidor recusa por um marco ou um critério, **When** a tela volta,
   **Then** o resumo da recusa aponta o campo, ou o cartão do marco quando a recusa não tem campo na
   tela, e o Perfil dele está aberto.
4. **Given** um endereço que aponta um campo ou o cartão de um marco, **When** a etapa abre por ele,
   **Then** aquele Perfil está aberto e o elemento apontado, à vista.
5. **Given** um envio sem validação — *Aplicar aos demais Perfis*, cancelar a prévia —, **Then** nada
   muda em relação a hoje.

---

### User Story 4 — Ver onde está o problema sem abrir cada Perfil (Priority: P1)

Quem elabora olha a tabela e vê que o polo de Linhares tem uma pendência de publicação no marco, e
que dois polos foram alterados e não salvos. A pendência está escrita no alto da etapa, e a linha
diz de quem ela é.

**Why this priority**: detectar anomalia é o que a tabela existe para responder, e a etapa hoje não
diz nenhuma das pendências que se resolvem nela.

**Independent Test**: com 7 Perfis gravados, um deles com um marco que a publicação recusa; conferir
o bloco de pendências da etapa com o achado, a linha daquele Perfil com *"1 pendência"* e as outras
com *"sem pendência"*.

**Acceptance Scenarios**:

1. **Given** pendências de publicação que se resolvem nesta etapa, **Then** a etapa as lista no alto,
   como as demais etapas do assistente.
2. **Given** pendências cujo objeto é um Perfil ou um marco dele, **Then** a linha daquele Perfil diz
   quantas, em texto; as demais dizem *"sem pendência"*.
3. **Given** um Perfil cujo marco na tela difere do gravado — digitado agora, acrescentado, removido,
   ou devolvido pelo servidor sem gravar —, **Then** a linha diz *"alterado — não salvo"*, junto da
   contagem de pendências.
4. **Given** uma pendência que não nomeia Perfil, **Then** ela fica no bloco da etapa, e não em linha
   nenhuma.

---

### User Story 5 — Não perder o digitado da etapa mais longa (Priority: P2)

Quem elabora ajusta os marcos de quatro polos, a sessão expira, e o envio não chega. Ao voltar à
etapa, a tela diz que há preenchimento não enviado neste navegador e oferece restaurá-lo — como já
faz nos Perfis, no Cronograma, nas Etapas e na Inscrição.

**Why this priority**: com um cartão por vez, o operador passa por mais Perfis entre uma gravação e a
seguinte, e o que ele alterou fica fora de vista. É a única etapa mestre-detalhe que ficaria sem a
proteção.

**Independent Test**: alterar marcos de dois Perfis, recarregar a etapa sem salvar, restaurar;
conferir os dois marcos de volta, as duas linhas com *"alterado — não salvo"*, e nada gravado.

**Acceptance Scenarios**:

1. **Given** alterações não enviadas, **When** a etapa é aberta de novo no mesmo navegador, **Then** a
   tela oferece restaurar ou descartar, e diz de quando é.
2. **Given** a restauração, **Then** a tela volta montada pelo servidor com o digitado, nada é
   gravado, e as linhas que diferem do gravado dizem *"alterado — não salvo"*.
3. **Given** uma gravação bem-sucedida, **Then** o guardado da etapa deixa de existir.

---

### Edge Cases

- **Perfil sem marco.** A linha aparece com *"sem marco"*, os valores de marco vazios, e *Editar*
  abre o cartão onde se acrescenta o marco.
- **Perfil com dois marcos** (o 14/2026: sete Perfis, catorze marcos). Uma linha só; cada coluna de
  marco diz um valor por marco, na ordem do Perfil, cada um identificado pelo código do marco.
- **Marco sem código.** A coluna do marco diz *"sem código"*, e a linha continua editável. É o caso do
  marco recém-acrescentado.
- **Critério sem alvo escolhido.** A coluna diz o critério pelo tipo, sem o alvo; a validação de hoje
  continua recusando o envio.
- **Pendência de Perfil alterado.** A pendência vem do que está gravado; a linha diz as duas coisas.
- **Origem de marco alterado.** A origem vem do que está gravado; a linha diz as duas coisas.
- **Perfil com dois marcos e origem.** O gesto da `051` deixa fora do alcance o destino com dois
  marcos, e a Revisão só atribui origem a Perfil de um marco; a linha segue a mesma regra.
- **Envio que volta sem gravar** (recusa, prévia, cancelamento, restauração). O Perfil que estava
  aberto volta aberto, salvo quando a recusa aponta outro, que tem precedência. A notícia do alto — a
  prévia, a recusa — continua sendo o que se vê primeiro.
- **Salvar com um Perfil aberto.** A tela volta com nenhum aberto; o *"Rascunho salvo"* de hoje é o
  que diz que gravou.
- **Endereço que aponta o título da etapa** (o *Ir para* da Revisão). Nenhum Perfil abre.
- **Sem script.** A etapa é a de hoje — todos os cartões à vista, sem tabela —, com a legenda que
  identifica cada Perfil e o bloco de pendências.
- **Tela estreita.** A tabela não provoca rolagem horizontal da página.
- **Edital que não está em elaboração.** A etapa é leitura; a tabela e o editor valem igual, sem os
  gestos de escrita, como hoje.
- **Mais de mil campos.** A etapa continua recusada pelo servidor acima do teto (`DP-21`); esta feature
  não o altera, e o rascunho local passa a guardar o que a recusa perderia.

---

## Requirements *(mandatory)*

### O cartão diz de quem é

- **FR-960**: A legenda do cartão de cada Perfil na etapa Classificação MUST identificá-lo como a etapa
  Perfis o identifica (`FR-944` da `052`): pelo código e pela localidade, ou pela denominação sem
  localidade declarada. Isto MUST valer também sem script.

### A vista do conjunto

- **FR-961**: Com dois ou mais Perfis, a etapa MUST apresentar, antes de qualquer cartão, uma tabela com
  **uma linha por Perfil**, na ordem do Edital, sem reordenação pela tabela — inclusive o Perfil sem
  marco e o Perfil com mais de um. Com um Perfil, MUST NOT haver tabela, e o cartão MUST estar à vista.
- **FR-962**: Cada linha MUST trazer: o código do Perfil; a denominação e a localidade; os marcos, pelo
  código; a forma da ordem, dizendo, no marco de sorteio, se ele usa o método comum ou declara o
  próprio; o corte; os critérios de desempate, em ordem, cada um pelo sentido e pelo que compara; o
  recurso; a origem (`FR-964`); a situação (`FR-965`); e a ação *Editar*. Com mais de um marco, cada
  coluna de marco MUST dizer um valor por marco, na ordem do Perfil; sem marco, a linha MUST dizer
  *"sem marco"*.
- **FR-963**: A linha MUST refletir o que está nos campos do cartão, inclusive o que ainda não foi
  gravado, e MUST acompanhar a digitação e a reconstrução do cartão sem envio. A linha MUST NOT
  calcular regra de domínio — combinação, completude, impeditivo —: o que é regra chega pela
  situação. As frases MUST ser as que o cartão já usa nos resumos dos blocos.
- **FR-964**: A origem MUST dizer, quando o marco gravado do Perfil é o que um gesto de aplicar gravou,
  de onde, por quem e quando, com a mesma frase e pela mesma regra da Revisão (`FR-934` e `FR-935` da
  `051`); editado e gravado depois, MUST deixar de dizer. A origem é do que está gravado.
- **FR-965**: A situação MUST dizer, em texto, dois fatos independentes: quantas pendências da etapa têm
  por objeto aquele Perfil ou um marco dele (*"sem pendência"*, *"1 pendência"*, *"N pendências"*); e
  se o conteúdo na tela difere do gravado (*"alterado — não salvo"*). Pendência que não nomeia Perfil
  MUST NOT ser atribuída a linha nenhuma.
- **FR-966**: A etapa MUST mostrar, no alto, as pendências de publicação que se resolvem nela, como as
  demais etapas do assistente, e a contagem da `FR-965` MUST sair dessa mesma lista.
- **FR-967**: *"Alterado — não salvo"* MUST valer sempre que os marcos do Perfil na tela diferirem dos
  gravados: digitados depois de a tela abrir, marco ou critério acrescentado ou removido, ou devolvidos
  pelo servidor sem gravação (recusa, prévia, cancelamento, restauração). A devolução do formulário
  sem mudança MUST NOT acusar Perfil nenhum.

### Um editor por vez

- **FR-968**: Com a tabela presente, **no máximo um** cartão de Perfil MUST estar à vista. Os cartões
  fora de vista MUST continuar no formulário, com todo o conteúdo, e MUST ser enviados em **todo**
  envio da etapa, exatamente como hoje; o conjunto de campos enviados MUST ser o mesmo com e sem a
  vista.
- **FR-969**: *Editar* MUST pôr à vista o cartão daquele Perfil, com um título que o identifique pelo
  código e pela localidade ou denominação, e MUST marcar a linha como em edição.
- **FR-970**: O editor MUST oferecer *Anterior* e *Próximo*, na ordem da tabela, e *Voltar à lista*.
  Nenhum dos três MUST enviar o formulário, perguntar confirmação ou descartar conteúdo.
- **FR-971**: Ao abrir a etapa, nenhum cartão MUST estar à vista, salvo: (a) o Perfil único; (b) o
  Perfil do primeiro campo recusado pelo servidor; (c) o Perfil que o endereço aponta; (d) quando a
  tela volta de um envio que não gravou, o Perfil que estava à vista. Nessa ordem de precedência.
  Depois de uma gravação bem-sucedida, nenhum.
- **FR-972**: Quando um envio for barrado pela validação do navegador por um campo de um Perfil fora
  de vista, ou dentro de um bloco fechado do marco, esse Perfil e esse bloco MUST passar a estar à
  vista **antes** de a mensagem ser apresentada, de modo que o campo receba o foco e a mensagem
  apareça junto dele.
- **FR-973**: A recusa do servidor sobre um marco ou um critério MUST apontar, no resumo da recusa, o
  controle do campo recusado, ou o cartão do marco quando o campo não tem controle na tela — como as
  demais etapas já fazem com a linha recusada (`FR-033` da `007`).
- **FR-974**: Sem script, a etapa MUST ser a de hoje, com todos os cartões à vista e sem tabela.

### Os gestos existentes

- **FR-975**: *Acrescentar marco*, *Acrescentar critério*, os dois *Remover* e a reconstrução do cartão
  pela forma da ordem e pelas Etapas MUST fazer o que fazem hoje, dentro do cartão à vista, e a linha
  MUST acompanhar o resultado.
- **FR-976**: *Aplicar aos demais Perfis* MUST produzir a prévia no alto da etapa e alcançar os Perfis
  fora de vista tanto quanto o visível; confirmado, a tela MUST voltar com a tabela e nenhum cartão
  aberto, e a linha de cada destino alcançado MUST mostrar os valores aplicados e a origem.
- **FR-977**: O método do sorteio comum ao Edital MUST continuar declarado uma vez, fora da tabela, com
  o mesmo comportamento e a mesma gravação de hoje.
- **FR-978**: O gesto da `051` — prévia, confirmação, impressão do que foi mostrado, registro na trilha
  — e os padrões da composição — corte padrão, sorteio sem empate, instante do Evento, prosa gerada
  — MUST produzir o mesmo resultado gravado que produzem hoje, para o mesmo conteúdo.

### O digitado protegido

- **FR-979**: A etapa MUST oferecer o rascunho local que as etapas Perfis, Cronograma, Etapas e
  Inscrição oferecem — guardar no navegador o que não foi enviado, oferecer restaurá-lo ou descartá-lo,
  e remontar a tela restaurada pelo servidor —, pelo mesmo mecanismo, sem mecanismo novo, e só para
  quem pode compor o Edital.

### A tela

- **UX-123**: A tabela MUST ter cabeçalho de coluna, e o código do Perfil MUST ser o cabeçalho de cada
  linha. O número de Perfis MUST estar no título dela.
- **UX-124**: O nome acessível de cada *Editar* MUST incluir o código do Perfil (*"Editar DOC-INFO-03"*).
- **UX-125**: A linha em edição MUST ser marcada por texto visível e pelo estado de item atual para
  tecnologia assistiva, e nunca só por cor. A situação e a origem MUST NOT depender de cor ou ícone.
- **UX-126**: *Editar*, *Anterior* e *Próximo* MUST levar o foco ao título do editor; *Voltar à lista*
  MUST devolvê-lo ao *Editar* da linha de onde saiu.
- **UX-127**: A etapa MUST vir nesta ordem: as ajudas e as pendências da etapa, a tabela, o método do
  sorteio comum, o editor. O método é declaração sobre o conjunto, e a tabela é o conjunto.
- **UX-128**: Em tela estreita a tabela MUST NOT provocar rolagem horizontal da página.
- **UX-129**: Nenhum cartão MUST passar a trazer ajuda visível (`FR-428` da `030`); os blocos do marco
  que fecham e dizem no resumo o que há dentro continuam como estão, e o que a tabela e o editor dizem
  mora fora do cartão.

### Key Entities

- **Linha do Perfil**: o resumo da classificação de um Perfil na tabela — identificação, os valores de
  cada marco, a origem, a situação e a ação. Não é gravada: é leitura do cartão, mais o que só o
  servidor sabe.
- **Origem do marco**: o gesto de aplicar que gravou o marco do Perfil, enquanto o gravado for o que ele
  gravou. Lida da trilha, como na Revisão; nada é gravado por esta feature.
- **Situação do Perfil**: a contagem de pendências da etapa que o têm por objeto e o fato de o marco na
  tela diferir do gravado.
- **Perfil em edição**: o único cartão à vista, ou nenhum. É estado da tela, e não do rascunho.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-354**: Com 7 Perfis de um marco com 2 critérios, a 1280×900, a tabela começa na primeira tela, e
  a página com um cartão aberto mede **no máximo um terço** dos 12,5 mil px de hoje; com nenhum aberto,
  cabe em duas telas.
- **SC-355**: Depois de um *"Aplicar aos demais Perfis"* confirmado, conferir em quais Perfis o marco
  aplicado está gravado custa **zero** cliques e nenhuma rolagem além de uma tela, com 7 Perfis — hoje,
  abrir e ler sete cartões ao longo de 12 mil px.
- **SC-356**: Em 100% dos casos de teste num navegador real, o envio barrado por campo de Perfil fora de
  vista abre esse Perfil e põe o foco no campo — nos campos obrigatórios do marco e do critério, e num
  campo inválido dentro de bloco fechado.
- **SC-357**: Em 100% das recusas do servidor sobre um marco ou um critério nos testes, o resumo da
  recusa aponta um elemento que existe na tela devolvida, e o Perfil dele volta aberto.
- **SC-358**: Para o mesmo conteúdo, o conjunto de campos que a etapa envia é **idêntico** com a vista e
  sem ela, em Salvar, Avançar, na prévia, no cancelamento e na restauração.
- **SC-359**: 100% das linhas se identificam e dizem a situação e a origem sem cor, e a tabela é
  percorrível por cabeçalho de linha e de coluna na árvore de acessibilidade.
- **SC-360**: Nenhum teste da `030`, da `043`, da `051` e do rascunho local muda de resultado, e
  nenhum conteúdo gravado por esses gestos muda.

---

## Assumptions

### D-001 — A vista não é formulário, e o que a `052` decidiu vale aqui

O editor é o cartão de hoje, e *"estar em edição"* é **estar à vista**: os demais continuam no mesmo
formulário e em todo envio (`D-001` da `052`). Não há *"Salvar e editar próximo"*, nem pergunta ao
trocar de Perfil, nem *Cancelar* por Perfil (`D-005` da `052`): nada se perde ao trocar, e gravar é da
etapa inteira. A tabela é montada pela tela, lendo o formulário, e o servidor entrega só o que a tela
não sabe (`D-004` da `052`).

### D-002 — A linha é o Perfil, e a medição é esta

O marco pertence ao Perfil, e a linha poderia ser qualquer um dos dois. Nos Editais que o projeto já
compôs:

| Edital | Perfis | Marcos por Perfil | Linhas por Perfil | Linhas por marco |
|---|---:|---:|---:|---:|
| 28/2026 | 7 | 1 | 7 | 7 |
| 140/2025 | 16 | 1 | 16 | 16 |
| 78/2026 | 2 | 1 (sorteio) | 2 | 2 |
| 14/2026 | 7 | 2 (o corte e a ordem final) | **7** | **14** |
| Edital em composição, antes do primeiro marco | N | 0 | N | **0** |

Uma linha por marco dobraria a tabela do 14/2026 com dois *Editar* por Perfil que abrem **o mesmo
cartão**, e sumiria com o Perfil sem marco, que é exatamente o que falta compor. Uma linha por Perfil
mantém o que a `052` fixou — a linha é leitura do cartão, e o cartão é o do Perfil — e faz a
comparação que a Revisão já faz, *por posição*: o 1º marco de um Perfil ao lado do 1º dos outros.

### D-003 — A situação são dois fatos, e *"em edição"* não é um deles

Como na `052` (`D-003` de lá): as pendências que o servidor já calcula para a etapa, atribuídas ao
Perfil pelo caminho do achado, e a diferença entre a tela e o gravado. O caminho da pendência de marco
é `/profiles/id=<Perfil>/classificationMilestones/id=<marco>/…` — ele nomeia o Perfil antes do marco, e
é ao Perfil que ela vai.

### D-004 — A origem é a da Revisão, e não uma segunda

A Revisão já decide quando um marco foi aplicado e por quem, lendo o registro do gesto e comparando a
impressão do gravado (`D-002` da `051`). A linha usa a mesma função e a mesma frase: duas leituras da
mesma origem divergiriam na primeira mudança. Por isso a origem é do gravado, e só para Perfil de um
marco — a regra que a Revisão já segue.

### D-005 — A etapa passa a mostrar as pendências

As demais etapas graváveis mostram, no alto, as pendências que se resolvem nelas; a Classificação não
mostrava, e um achado de marco só se lia na Revisão. Com a tabela, a linha diria *"1 pendência"* sem
que a pendência estivesse escrita em lugar nenhum da tela — e a `052` fixou que a linha não diz o que o
bloco não diz. O bloco é o mesmo das outras etapas, com a mesma seleção.

### D-006 — A recusa do servidor passa a apontar o campo

Com todos os cartões à vista, a recusa sem âncora custava rolar a página; com um por vez, custaria não
achar o marco. **Medido na implementação**: a validação do marco na composição recusava **sem** dizer
de que marco ou critério, e em que campo — ao contrário da validação que a `048` escreveu para a
Retificação (`validar_criterio`), que já os dizia com as mesmas frases. A recusa passa a levar os dois,
com a mesma mensagem e a mesma regra; eles não atravessam a API, e existem para a tela ancorar. A tela
os traduz no controle, como nas demais etapas, e quando o campo recusado não tem controle próprio na
tela, a âncora recua para o cartão do marco, que sempre tem.

### D-007 — O rascunho local entra, pelo mecanismo que existe

O mecanismo tem duas metades, e a do servidor já atende esta etapa: a restauração é um envio que
devolve o digitado sem gravar, e a etapa já sabe reexibi-lo, porque é o que ela faz depois de uma
recusa. Falta só a tela declarar o que as outras declaram. É o menor escopo que não deixa o operador
pior do que hoje: com um cartão por vez ele passa por mais Perfis entre uma gravação e outra, e o que
alterou fica fora de vista.

### Outras premissas

- **O teto de mil campos continua**: esconder cartões não reduz o envio (`DP-21`). O rascunho local
  passa a guardar o que a recusa do teto perderia, e isso não o corrige.
- **O código comum com a `052` se extrai agora**, porque a segunda tela entrou (a `052` o previu em
  *Out of Scope*). O mínimo: o que as duas telas fazem igual — tabela, um cartão por vez, `invalid`,
  endereço, foco. Sem componente genérico de coleção: cada tela declara o que a linha lê.
- **Mesmo vocabulário**: as frases da linha — forma da ordem, corte, recurso — são as dos resumos dos
  blocos do cartão e da Revisão, e não o nome do campo no conteúdo canônico.

---

## Out of Scope

- Gravar por Perfil, mudar a gravação da etapa, e o teto de mil campos (`DP-21`).
- Editar na própria linha; filtro, busca e ordenação pela tabela.
- *Aplicar aos demais* a partir da linha; o gesto continua no cartão do marco (`UX-110` da `051`).
- O *Ir para* da Revisão apontando o marco, e não o título da etapa.
- As demais etapas: Cronograma, Inscrição, Retificação.
- Componente genérico de coleção.
