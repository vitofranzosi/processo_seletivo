# Feature Specification: Os mesmos recortes no sorteio, na divulgação, na ocupação e na Supervisão

**Feature Branch**: `claude/classification-links-review-bade10`, sobre a `main` em `de5df85c`

**Created**: 2026-11-05

**Status**: Implementada e mergeada (#398). T040 é validação humana. *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Draft, **só documental**. Nenhum código, migration, rota ou tela foi alterado. As
decisões têm duas origens:

- **Do usuário, em 05/11/2026, nesta sessão:** a avaliação dos links de divulgação da página do
  Edital, a proposta de escopo, os três acréscimos, as duas precisões e o critério de aceite da
  jornada, resumidos em *Clarifications*. Não se reabrem.
- **Propostas de desenho desta spec:** D-001 a D-007, abaixo. Elas resolvem o que a conversa deixou
  aberto. **Aprovadas pelo usuário em 05/11/2026**, a D-004 no caminho mais simples (11ª decisão).

**Input**: *"Alinhar sorteio, divulgação, ocupação e Supervisão pelos mesmos recortes (a Modalidade
apontada como ampla deixa de ter recorte próprio no sorteio), com transição explícita para o acervo
de atos excedentes e um caminho único e nomeado para divulgar na página do Edital."*

> **Faixa de identificadores.** Esta spec abre em **FR-3893** e **SC-1165**. O teto foi medido em
> 05/11/2026 em `specs/` de todas as worktrees desta máquina e da `main` em `de5df85c`: o requisito
> funcional três mil oitocentos e noventa e dois e o critério mil cento e sessenta e quatro, os dois
> da `121`. A pasta `122` não existe em nenhuma delas, e o único PR aberto (#397) é só da Visão do
> Sistema. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-491 da `034`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número.

## Por que esta feature existe

Em 05/11/2026, no Edital 35/2026 da instalação do Cefor, a seção *Classificação* da página do Edital
mostrava, para o marco "Classificação final" de um Perfil com sorteio:

> conduzir o marco · corte · ocupação · convocação · divulgar o resultado · divulgar o resultado ·
> divulgar o resultado · divulgar o resultado
>
> Recortes: 3 · com ordem 3 · com corte 0 · apurados 0 · publicados 1

Quatro links iguais, sem nome, e um resumo que contava três recortes. Abrir os quatro mostrou quatro
listas: a ampla concorrência (onze participantes, todos os inscritos do Perfil), a reserva PcD (dois),
a reserva PPI e **uma quarta, só de quem declarou a Modalidade "Ampla Concorrência (AC)"** (seis).

A leitura do código explica as duas coisas.

1. **Os links não têm nome.** A página do Edital desenha um destino por ato vigente do marco, com o
   rótulo fixo *"divulgar o resultado"*, na ordem de emissão. O ato sabe o recorte; o rótulo não o
   diz. Desde a `033` (FR-474) a página precisava dar ao Publicador puro um caminho até a
   divulgação, e o deu ato a ato. O selector que ela lê já registrava que *"três listas de
   concorrência produzem três atos raiz no mesmo marco"*. Ninguém deu nome a eles.
2. **O quarto ato é de um recorte que a operação não usa.** O Perfil aponta a Modalidade AC como a
   ampla concorrência. A classificação e a ocupação tratam essa Modalidade como **apelido** da ampla,
   sem recorte próprio (FR-491 da `034`). O sorteio não: a derivação dele lista o recorte geral **e**
   cada Modalidade declarada, inclusive a apontada como ampla. Daí sai uma relação, um sorteio e um
   ato de ordenação que **a ocupação não consome** e que o resumo da página, que já usa a derivação
   canônica, não conta.

A divergência não é nova. A `034` a mediu e a deixou fora **de propósito**, na decisão de escopo do
sorteio ratificada em 18/09/2026: *"Retirar o recorte excedente obriga a responder como os atos já
emitidos nele continuam alcançáveis — e ato publicado não se apaga nem se reescreve, de modo que a
resposta não é uma migração, é um desenho."* Esta spec é esse desenho.

### O que a divergência produz hoje, além dos links

A avaliação de 05/11 encontrou o mesmo defeito em mais quatro lugares, e eles pesam mais que o rótulo:

- **A Supervisão cobra a lista excedente.** Para marcos por sorteio, a lista de recortes que ela
  percorre é a do sorteio, por escolha registrada na própria função (*"os atos já emitidos nela
  precisam continuar alcançáveis"*). O ato excedente gera, então, o sinal de ato não divulgado
  (`UX-066` da `038`), com destino na prévia, e o de recorte sem apuração (`UX-065` da `038`), que
  nunca se apaga, porque a ocupação não tem linha para esse recorte.
- **Quatro portas oferecem divulgar o ato excedente:** a página do Edital, a tela do sorteio
  (*"Publicar a classificação deste sorteio"*, por recorte), a tela do ato (*"Publicar resultado"*) e
  o destino do sinal da Supervisão. Nenhuma o distingue dos outros.
- **O comando de divulgação aceita.** Nada no backend separa o recorte excedente dos demais. Uma
  publicação dele seria imutável (Princípio II).
- **O comando do sorteio aceita.** A publicação da relação não confere se a lista pedida é recorte
  da operação, e o sorteio constitui o ato sobre qualquer relação vigente.

### O que se descarta

- **Só nomear os links.** Corrige o rótulo e deixa a causa ativa: o sorteio continua produzindo a
  lista, a Supervisão continua cobrando e as portas continuam oferecendo.
- **Converter os atos excedentes para a ampla** (`lista_id` nulo). As tabelas são append-only, e a
  conversão seria impossível de qualquer modo; mas ela também seria falsa: atribuiria à ampla uma
  ordem sorteada para outro universo.
- **Identificar a Modalidade excedente pelo texto "AC" ou "Ampla".** O apontamento existe no Perfil
  (*"Modalidade que é a ampla concorrência"*), e é ele que decide. Um Edital pode chamar a Modalidade
  de outra coisa, e outro pode ter uma Modalidade "AC" que **não** é a ampla.

### O que esta spec cobre, e o que fica fora

**Cobre:**

- uma derivação de recortes só para sorteio, classificação, ocupação, divulgação, Supervisão e
  relatório do Edital;
- a recusa, nos comandos, de relação, sorteio e divulgação no recorte excedente;
- o acervo excedente existente: preservado, consultável e explicado, sem competir com o trabalho;
- a regra temporal: a versão vigente decide o que é operacional, e a versão de origem explica o
  registro;
- um caminho de divulgação por marco na página do Edital, até o quadro de recortes da condução.

**Fica fora** (ver *Registrado, sem desenvolver*):

- o Edital que declara uma Modalidade chamada "Ampla concorrência" **sem** apontá-la como a ampla;
- o que o candidato vê de uma publicação excedente já feita;
- a Modalidade que uma Retificação remove do Perfil.

## Clarifications

### Session 2026-11-05 (avaliação dos links e proposta de escopo)

Decisões do usuário nesta sessão. Não se reabrem.

- **1ª — Um caminho único para divulgar.** A página do Edital oferece um caminho por marco, que leva
  ao quadro de recortes de "conduzir o marco", onde já aparecem os nomes, os estados e os caminhos
  individuais. O Publicador puro continua chegando lá.
- **2ª — O sorteio novo usa a derivação canônica.** A Modalidade apontada pelo Perfil como a ampla
  deixa de gerar relação, sorteio e ato próprios. A identificação vem do apontamento, nunca do texto.
- **3ª — O acervo excedente se preserva.** Identidade, conteúdo, documentos e verificadores ficam como
  estão, consultáveis no histórico, com a explicação de que a lista não é usada na ocupação. O
  recorte deles **não** se converte para a ampla.
- **4ª — Divulgar o excedente é recusado no backend**, com a mesma explicação na prévia e na tela do
  sorteio. Publicações anteriores ficam preservadas.
- **5ª — A Supervisão entra no escopo.** Ela deixa de sinalizar o recorte excedente.
- **6ª — Todas as portas de divulgação entram no escopo**, e não só a prévia e a tela do sorteio.
- **7ª — A regra é temporal.** A versão vigente define os recortes operacionais; a versão de origem
  explica o registro histórico.
- **8ª — Retificação não reabilita ato antigo por si.** Se o apontamento da ampla mudar, a
  possibilidade de usar um ato anterior passa pelas verificações de compatibilidade e obsolescência;
  ela nunca é automática.
- **9ª — A relação excedente já congelada não produz sorteio.** O comando recusa; retirar a relação
  das pendências e dos botões não basta. Ela continua consultável, com a explicação do impedimento.
- **10ª — O critério de aceite da jornada** é o da SC-1165, nas palavras do usuário.

### Session 2026-11-05 (parecer do usuário sobre a spec)

- **11ª — D-001 a D-007 aprovadas.** Na D-004 fica o caminho mais simples: quando o papel do recorte
  muda, o trabalho segue por relação, sorteio e ato novos, sem reaproveitamento.
- **12ª — A explicação do acervo distingue as duas origens.** Um registro pode ter nascido excedente
  ou ter se tornado excedente por Retificação (FR-3913), e a frase de cada um sai da versão que ele
  cita (FR-3911). A FR-3903 foi reescrita para isso.
- **13ª — O que o portal diz de publicação excedente não entra por si.** Se o levantamento da
  instalação encontrar publicação excedente, os números vão ao usuário, que decide; o escopo não se
  amplia automaticamente.
- **14ª — O levantamento na instalação foi dispensado** (*"esquece a VM"*). A implementação segue sem
  ele; o portal continua fora (FR-3915), e o roteiro fica no quickstart.
- **Ressalva aceita ao diagnóstico:** posições diferentes da mesma pessoa na ampla e na lista
  excedente não provam, sozinhas, classificações contraditórias, porque os universos são diferentes.
  O defeito comprovado é oferecer como resultado operacional uma lista que a ocupação não consome.

## User Scenarios & Testing *(mandatory)*

Os cenários usam um Edital publicado com um Perfil que declara três Modalidades: AC, apontada pelo
Perfil como a ampla, PPI e PcD, e um marco classificatório por sorteio. Os **recortes operacionais**
desse marco são três: a ampla (todos os inscritos), PPI e PcD.

### User Story 1 — Quem conduz o sorteio trabalha nos três recortes, e só neles (Priority: P1)

A presidência da comissão congela as relações, constitui os sorteios e confere a ordem. A tela do
sorteio mostra os três recortes operacionais. A Modalidade AC não aparece como recorte a congelar
nem a sortear, e a tela diz por quê numa frase: a ampla concorrência já inclui todos os inscritos.

**Why this priority**: é a origem do defeito. Sem ela, todo o resto é remendo de uma lista que
continua nascendo.

**Independent Test**: num Edital novo como o acima, sem acervo, conduzir o sorteio do marco até o fim
e contar recortes em cada tela.

**Acceptance Scenarios**:

1. **Given** o marco sem relação congelada, **When** a presidência abre a tela do sorteio, **Then** vê
   três recortes, a ampla primeiro e as reservas na ordem do Perfil, e nenhum bloco da Modalidade AC.
2. **Given** um pedido de congelar a relação da Modalidade AC, feito por formulário antigo ou chamada
   direta, **When** o comando o recebe, **Then** recusa com a explicação da FR-3897 e não grava
   relação nem trilha de ato.
3. **Given** os três recortes sorteados, **When** a tela do sorteio, a prévia do sorteio e a
   Retificação perguntam se o marco ainda tem sorteio a fazer, **Then** a resposta é "não", sem
   esperar pela Modalidade AC.

---

### User Story 2 — Quem divulga encontra cada recorte pelo nome e sabe o que já saiu (Priority: P1)

Na página do Edital, cada marco com ato emitido oferece **um** caminho de divulgação. Ele leva ao
quadro de recortes da condução do marco, onde cada recorte aparece pelo nome que o Edital publica,
com o estado da divulgação (não divulgado, divulgado como preliminar, divulgado como definitivo,
divulgação defasada) e o caminho para a prévia dele.

**Why this priority**: é o defeito que o operador viu. Também é o que a `033` prometeu ao Publicador
puro, e precisa continuar valendo.

**Independent Test**: com o Publicador puro, sem vínculo de comissão, abrir a página do Edital e
divulgar os três recortes do marco sem digitar endereço.

**Acceptance Scenarios**:

1. **Given** um marco com três atos vigentes, um deles já divulgado, **When** qualquer ator que
   divulga abre a página do Edital, **Then** vê um único caminho de divulgação para o marco, e não
   três.
2. **Given** o Publicador puro, **When** segue esse caminho, **Then** chega ao quadro de recortes,
   vê os três pelo nome, o divulgado marcado como tal, e abre a prévia de cada um dos outros dois.
3. **Given** um marco sem ato emitido, **When** o Publicador puro abre a página do Edital, **Then**
   não vê caminho de divulgação para ele (FR-476 da `033`).

---

### User Story 3 — A Supervisão cobra só o que existe para fazer (Priority: P1)

Os sinais de trabalho pendente sobre ordem, apuração e divulgação de um marco por sorteio percorrem os
mesmos três recortes que a ocupação apura.

**Why this priority**: um sinal que não se resolve ensina o operador a ignorar a Supervisão inteira.

**Independent Test**: num Edital com acervo excedente (US4), divulgar e apurar os três recortes
operacionais e conferir que a Supervisão fica sem sinal daquele marco.

**Acceptance Scenarios**:

1. **Given** um ato excedente vigente e nunca divulgado, **When** a Supervisão é aberta por quem
   divulga, **Then** não há sinal de divulgação pendente sobre ele.
2. **Given** o mesmo ato, **When** a Supervisão é aberta pela presidência, **Then** não há sinal de
   apuração pendente nem de ordem obsoleta sobre ele.
3. **Given** um recorte operacional com ato não divulgado, **When** a Supervisão é aberta, **Then** o
   sinal continua como hoje, com o nome do recorte e destino na prévia daquele ato.

---

### User Story 4 — O acervo excedente continua consultável e explicado (Priority: P2)

Editais que sortearam antes desta feature têm relações, sorteios, atos e, talvez, publicações no
recorte da Modalidade apontada como ampla. Eles continuam como estão. Quem os consulta entende de
onde vieram e por que não participam da operação atual, e não recebe botão para continuar o trabalho
neles.

**Why this priority**: preservar é obrigação constitucional; explicar é o que impede o registro antigo
de competir com o trabalho atual. Vem depois de US1 a US3 porque, sem elas, a explicação seria sobre
uma lista que ainda nasce.

**Independent Test**: com um banco que tenha relação, sorteio, ato e publicação excedentes gravados
antes da implementação, percorrer as telas da gestão e as páginas públicas de verificação e comparar
com o estado anterior.

**Acceptance Scenarios**:

1. **Given** um ato excedente, **When** alguém que alcança o marco abre a tela do sorteio, **Then** o
   registro aparece numa seção separada dos recortes operacionais, com a frase da FR-3903, sem botão
   de congelar, sortear ou divulgar.
2. **Given** a prévia de divulgação do ato excedente, aberta por endereço antigo, **When** carrega,
   **Then** mostra a mesma explicação no lugar do botão de publicar; e um envio do formulário antigo é
   recusado pelo comando (FR-3899).
3. **Given** uma publicação excedente feita antes desta feature, **When** alguém consulta os
   resultados divulgados do marco ou a página pública de verificação dela, **Then** ela continua lá,
   com o mesmo conteúdo, o mesmo documento e o mesmo verificador; na gestão, marcada como fora da
   operação atual.
4. **Given** uma relação excedente congelada e ainda sem sorteio, **When** a presidência abre a tela
   do sorteio, **Then** a relação aparece no histórico com o impedimento explicado; e um pedido direto
   de sortear sobre ela é recusado (FR-3898).

---

### User Story 5 — Uma Retificação do apontamento não reabilita nem condena em silêncio (Priority: P2)

A Retificação pode criar, retirar ou trocar o apontamento da Modalidade que é a ampla. Depois dela,
os recortes operacionais são os da versão vigente, e cada ato emitido antes é julgado contra eles.

**Why this priority**: é o caso raro, mas é o que faria um ato produzido para um universo virar, sem
ninguém decidir, o resultado de outro.

**Independent Test**: retificar o apontamento nos três sentidos, cada um num Edital, e conferir o
estado de cada ato anterior na condução do marco e na Supervisão.

**Acceptance Scenarios**:

1. **Given** um Edital sem apontamento, em que a Modalidade AC é recorte operacional e tem ato
   divulgado, **When** uma Retificação passa a apontá-la como a ampla, **Then** aquele ato vira
   registro excedente: fora do quadro operacional, sem sinal na Supervisão, com publicação e
   verificador preservados, e com a frase de quem se tornou excedente pela Retificação, nomeada pelo
   número; um registro nascido excedente no mesmo marco mantém a frase dele.
2. **Given** um Edital em que a Modalidade AC é apontada como a ampla e tem ato excedente, **When** uma
   Retificação retira o apontamento, **Then** a Modalidade AC volta a ser recorte operacional e o ato
   antigo **não** vira o ato vigente dela por isso: o recorte aparece com o ato obsoleto e a causa
   nomeada (D-004).
3. **Given** um ato emitido em qualquer versão, **When** a tela de histórico o mostra, **Then** a
   explicação de origem é a da versão que o ato cita, e não a da vigente.

---

### Edge Cases

Cada caso-limite é requisito, e o plano dá a cada um um teste na matriz de rastreabilidade.

- **Perfil sem apontamento.** Nenhum recorte é excedente. A Modalidade "AC" que o Perfil declara é
  recorte operacional como qualquer outra, na operação inteira. Esta spec não muda esse Edital.
- **Apontamento para Modalidade sem inscrito.** Não há relação a recusar nem acervo a explicar; a
  tela do sorteio continua sem o bloco e com a frase da FR-3895.
- **Marco por classificação computada, e não por sorteio.** Já usa a derivação canônica desde a
  `034`. Nada muda nele, além do caminho de divulgação da página do Edital (FR-3906).
- **Pedido repetido com a mesma chave de idempotência** de uma relação ou sorteio excedente aceito
  antes desta feature. Devolve o desfecho anterior, como hoje. Não é ato novo, e a recusa não se
  aplica.
- **Sucessão de ato excedente.** Emitir um ato sucessor no recorte excedente é recusado, como emitir o
  primeiro. Corrigir um registro excedente não tem sentido operacional, e o histórico dele fica como
  está.
- **Ato excedente obsoleto e ato excedente vigente.** Os dois são registro e nenhum é trabalho: nenhum
  produz sinal, nenhum entra no quadro operacional.
- **Ato do recorte excedente já divulgado como definitivo.** A publicação fica; a recusa vale só para
  divulgação nova (FR-3899).
- **Edital sem marco por sorteio.** Nenhum registro excedente pode existir nele, e a seção de histórico
  da FR-3903 não aparece.
- **Ator que não alcança o marco.** Não vê o registro excedente em lugar nenhum da gestão, como não vê
  o marco. A página pública de verificação continua aberta a quem tem o endereço, como hoje.
- **Edital encerrado ou cancelado.** Continua sem produzir sinal de trabalho pendente; o acervo
  continua consultável.

## Requirements *(mandatory)*

### Functional Requirements

#### A. Uma derivação de recortes

- **FR-3893**: O conjunto de **recortes operacionais** de um marco MUST ser o da derivação canônica que
  a classificação e a ocupação usam desde a `034` (FR-491 da `034`): a ampla concorrência, que reúne
  todos os inscritos do Perfil, e cada Modalidade declarada, **exceto** a que o Perfil aponta como a
  ampla. O sorteio, a divulgação, a condução do marco e a Supervisão MUST obter o conjunto desse mesmo
  lugar, e nenhum deles MUST manter derivação própria.
- **FR-3894**: A Modalidade excedente MUST ser identificada **só** pelo apontamento do Perfil
  (*"Modalidade que é a ampla concorrência"*), e MUST NOT ser inferida de nome, código ou texto.
- **FR-3895**: A tela do sorteio e a prévia do sorteio (`098`) MUST mostrar só os recortes
  operacionais. Quando o Perfil aponta uma Modalidade como a ampla, as duas MUST dizer, numa frase,
  que aquela Modalidade não tem sorteio próprio, porque a ampla concorrência já reúne todos os
  inscritos, inclusive quem a declarou. A frase da prévia que hoje diz que a Modalidade *"ganha uma
  lista própria no sorteio do certame"* MUST deixar de dizê-lo.
- **FR-3896**: A pergunta "o marco ainda tem sorteio a fazer" (`102`) MUST considerar só os recortes
  operacionais.

#### B. Os comandos recusam o recorte excedente

- **FR-3897**: O comando de congelar a relação MUST recusar, antes de gravar, o pedido cujo recorte é
  excedente na versão vigente. A recusa MUST ser nomeada, MUST dizer que a Modalidade é apontada como
  a ampla e que a relação da ampla já a inclui, e MUST NOT gravar relação nem trilha de ato.
- **FR-3898**: O comando de constituir o sorteio MUST recusar a relação cujo recorte é excedente na
  versão vigente, **mesmo que ela esteja congelada e vigente**, com a mesma explicação.
- **FR-3899**: O comando de divulgar o resultado MUST recusar o ato cujo recorte é excedente na versão
  vigente, com a mesma explicação. Publicações feitas antes desta feature MUST NOT ser alteradas,
  sucedidas nem invalidadas pela recusa.
- **FR-3900**: Nenhum caminho MUST gravar ato de ordenação, inclusive o sucessor, no recorte excedente
  da versão vigente. A classificação computada continua como a `034` a deixou: o pedido do apelido é
  **normalizado** para a ampla, e não recusado, porque ele não grava no recorte excedente. O caminho
  do sorteio, que grava o ato a partir da relação, fica fechado pela recusa da FR-3898.
  *Redação corrigida no plano (05/11/2026): a primeira dizia que a classificação "recusava".*
- **FR-3901**: Nenhuma tela MUST oferecer congelar, sortear, emitir ou divulgar no recorte excedente.
  As portas de divulgação que existem hoje são quatro, e todas MUST seguir a regra: a página do
  Edital, a tela do sorteio, a tela do ato e o destino do sinal da Supervisão. A prévia aberta por
  endereço direto MUST mostrar a explicação da FR-3899 no lugar do botão.

#### C. O acervo excedente

- **FR-3902**: Relações, sorteios, atos de ordenação e publicações gravados no recorte excedente
  MUST continuar com a identidade, o conteúdo, os documentos e os verificadores que têm. Nenhum MUST
  ter o recorte convertido para a ampla, nem ser sucedido, anulado ou ocultado por esta feature.
- **FR-3903**: A tela do sorteio MUST mostrar os registros excedentes do marco numa seção própria,
  depois dos recortes operacionais, sem ação nenhuma além de consultar. Cada registro MUST trazer a
  frase da **origem dele**, decidida pela versão que ele cita (FR-3911):
  - **nascido excedente** — na versão de origem, a Modalidade já era apontada como a ampla: o registro
    foi produzido quando o sorteio dava lista própria à Modalidade apontada como a ampla concorrência;
    a ocupação das vagas não usa essa lista; ele fica preservado como foi feito;
  - **tornado excedente por Retificação** — na versão de origem, a Modalidade era recorte próprio: o
    registro foi produzido quando esta Modalidade tinha recorte próprio; a Retificação que passou a
    apontá-la como a ampla concorrência, nomeada pelo número, o tirou da operação; ele fica
    preservado como foi feito.
- **FR-3904**: A tela do ato, a lista de resultados divulgados do marco e a prévia de um registro
  excedente MUST identificar o registro como fora da operação atual, com a frase da origem dele
  (FR-3903).
- **FR-3905**: As páginas públicas de verificação de relação, sorteio e resultado MUST continuar
  respondendo para os registros excedentes exatamente como antes desta feature (D-005).

#### D. A página do Edital

- **FR-3906**: A seção *Classificação* da página do Edital MUST oferecer **no máximo um** caminho de
  divulgação por marco, e não um por ato. O caminho MUST levar ao quadro de recortes da condução do
  marco, na parte da divulgação, e MUST aparecer para quem divulga sempre que o marco tiver ao menos
  um ato vigente em recorte operacional.
- **FR-3907**: O Publicador puro, que detém a capacidade de divulgar e nenhum vínculo de comissão,
  MUST alcançar por esse caminho o quadro de recortes e a prévia de cada recorte operacional com ato
  vigente. A garantia da FR-474 da `033` continua inteira; muda a forma.
- **FR-3908**: No quadro de recortes da condução do marco, cada recorte operacional MUST aparecer pelo
  nome que o Edital publica, com o estado da divulgação e, para quem divulga, o caminho até a prévia
  do ato vigente dele. Recorte já divulgado no ato vigente MUST aparecer como divulgado, e não como
  pendente.

#### E. A Supervisão

- **FR-3909**: Os sinais de ordem obsoleta, de recorte sem apuração e de ato sem divulgação (`038`)
  MUST percorrer só os recortes operacionais, também nos marcos por sorteio. Nenhum registro
  excedente MUST produzir sinal.
- **FR-3910**: O destino de cada sinal de divulgação pendente MUST continuar sendo a prévia do ato
  daquele recorte, como hoje.

#### F. A regra temporal

- **FR-3911**: O que é recorte operacional MUST ser decidido pela **versão vigente** do Edital no
  instante da operação. A explicação de um registro MUST ser composta da **versão que ele cita**.
- **FR-3912**: Uma Retificação que cria, retira ou troca o apontamento da ampla MUST NOT tornar
  vigente, por si, ato emitido antes dela num recorte cujo papel mudou. Um ato assim MUST aparecer, no
  recorte operacional correspondente, como **obsoleto**, com a causa nomeada (*o papel do recorte
  mudou na Retificação nº N*), e o recorte segue o caminho de sucessão que já existe (D-004).
- **FR-3913**: Uma Retificação que passa a apontar como a ampla uma Modalidade que tinha registros
  operacionais MUST transformar esses registros em acervo excedente, com tudo o que as FR-3902 a
  FR-3905 garantem, e a Supervisão MUST deixar de sinalizá-los.

#### G. Limites

- **FR-3914**: Esta feature MUST NOT criar tabela, coluna nem situação nova para marcar registro
  excedente. Ser excedente é uma pergunta feita ao registro e à versão (D-002).
- **FR-3915**: Esta feature MUST NOT mudar o que o candidato vê no portal, nem os avisos já
  despachados (`066`).

#### H. O relatório do Edital

*Acrescentada no plano, em 05/11/2026: a pesquisa (`R-7`) encontrou no relatório do Edital uma
sexta superfície que monta linhas por lista a partir dos atos e das publicações.*

- **FR-3916**: O relatório do Edital (`099`, `100`) MUST montar as linhas de lista de cada marco a
  partir dos recortes operacionais, e o estado do marco (*definitivo em todas*, pendência) MUST
  considerar só eles. Uma publicação excedente já feita MUST aparecer identificada como fora da
  operação atual, sem contar para o estado do marco; um ato excedente não divulgado MUST NOT
  aparecer como pendência.

### Key Entities

- **Recorte operacional**: um par marco × lista sobre o qual se congela, sorteia, ordena, apura e
  divulga. A ampla concorrência (lista nula) e cada Modalidade declarada, exceto a apontada como a
  ampla, na versão vigente.
- **Recorte excedente**: a lista da Modalidade que o Perfil aponta como a ampla. Na versão vigente,
  não é recorte operacional. Numa versão antiga, pode ter sido.
- **Registro excedente**: relação, sorteio, ato de ordenação ou publicação cujo recorte é excedente na
  versão vigente. Preservado e consultável; nunca trabalho.
- **Versão de origem**: a versão consolidada que o registro cita. Explica o registro; não decide a
  operação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1165**: O operador realiza o sorteio e divulga os resultados dos três recortes válidos,
  identifica o que já foi publicado e conclui o trabalho sem receber cobrança sobre a lista excedente.
  Se consultar um registro antigo dessa lista, entende sua origem e por que ele não participa da
  operação atual. *(Critério de aceite da jornada, nas palavras do usuário; verificado por percurso
  humano num Edital de demonstração com o apontamento e acervo excedente, e por teste de jornada no
  navegador.)*
- **SC-1166**: Num Edital com o apontamento e acervo excedente, a tela do sorteio, a condução do marco,
  o resumo da página do Edital, a ocupação, a Supervisão e o relatório do Edital mostram **o mesmo
  número** de recortes operacionais: três, nas seis superfícies.
- **SC-1167**: A seção *Classificação* da página do Edital mostra **no máximo um** caminho de
  divulgação por marco, e o Publicador puro chega à prévia de qualquer recorte operacional em **dois
  cliques** a partir dela.
- **SC-1168**: **Zero** sinais da Supervisão sobre registro excedente, depois de divulgados e apurados
  os recortes operacionais.
- **SC-1169**: Os três comandos (congelar, sortear, divulgar) recusam o recorte excedente em **100%**
  dos pedidos diretos, sem gravar nada, e a emissão computada continua normalizando-o para a ampla; e **nenhuma** das quatro portas de divulgação oferece
  o botão para ele.
- **SC-1170**: **100%** dos registros excedentes gravados antes da implementação continuam
  consultáveis, e as páginas públicas de verificação deles devolvem o mesmo conteúdo de antes,
  comparado byte a byte depois de normalizar o que muda a cada resposta.
- **SC-1171**: Depois de uma Retificação que mexe no apontamento, **nenhum** ato emitido antes dela num
  recorte cujo papel mudou aparece como vigente operacional sem um ato novo.

## Assumptions

- **A instalação do Cefor tem acervo excedente.** O Edital 35/2026 tem ao menos um ato no recorte
  excedente. *A medição abaixo foi dispensada pelo usuário em 05/11/2026 (14ª decisão).* O plano MUST medir, antes de implementar, quantas relações, sorteios, atos e publicações
  excedentes existem lá, com uma consulta só de leitura, e dizer se algum foi divulgado.
- **O Publicador puro abre a condução do marco** desde a `049` (FR-830 da `049`), porque abre a prévia
  de divulgação, que é tela de recorte do marco. O plano confere isso com o papel exato antes de
  contar com ele.
- **A causa de obsolescência da FR-3912 cabe no mecanismo de causas nomeadas que já existe.** Se não
  couber sem tabela nova, o plano diz por quê, antes de propor coluna (FR-3914).
- **O texto das frases** da FR-3895 e da FR-3903 é proposta; o plano o leva ao vocabulário da
  varredura de vocabulário antes de fixá-lo.

## Compatibilidade com regras anteriores

| Regra | O que acontece |
|---|---|
| FR-491 da `034` (uma derivação para classificação e ocupação) | **estendida**: sorteio, divulgação, condução e Supervisão passam a usá-la (FR-3893) |
| FR-491a da `034` e a decisão de escopo do sorteio da `034` | cumpridas: a divergência registrada é a que esta spec trata |
| FR-504 da `034` (ordem emitida não se reescreve) | continua: nenhum registro é convertido (FR-3902) |
| FR-473 e FR-476 da `033` | continuam: o caminho só aparece para quem o alcança |
| FR-474 da `033` | continua, com outra forma: um caminho por marco, e não um por ato (FR-3906, FR-3907) |
| FR-830 e FR-831 da `049` | continuam: a condução do marco é o destino, e as telas por recorte seguem existindo |
| sinais `UX-004`, `UX-065` e `UX-066` da `038` | continuam, sobre os recortes operacionais (FR-3909) |
| a frase da Modalidade apontada como a ampla, na prévia do sorteio da `098` | **muda** (FR-3895) |

Nenhum requisito anterior é revisto nesta spec: as mudanças estendem regras vigentes a superfícies que
ficaram fora delas.

## Decisões

Propostas desta spec, **aprovadas pelo usuário em 05/11/2026** (11ª decisão).

### D-001 — O destino do caminho único é a condução do marco

O caminho único da página do Edital leva ao quadro de recortes de "conduzir o marco", na parte da
divulgação, e não a uma tela nova. O quadro já tem nome, estado e caminho por recorte, e um gesto em
lote. Uma tela nova de divulgação repetiria o quadro.

O rótulo do caminho continua *"divulgar o resultado"*, uma vez por marco. Quando o ator também alcança
"conduzir o marco", os dois links levam ao mesmo lugar, e o plano decide se o segundo se funde ao
primeiro.

### D-002 — Ser excedente é uma pergunta, e não uma marca

Nada se grava para dizer que um registro é excedente. A resposta vem do recorte do registro, da
versão vigente e do apontamento do Perfil. Uma marca gravada envelheceria na primeira Retificação
do apontamento, e o append-only impediria corrigi-la.

### D-003 — A recusa é a mesma frase nos três comandos e nas telas

Congelar, sortear e divulgar recusam com o mesmo código e a mesma explicação, e a tela que
deixa de oferecer o botão diz a mesma frase. Frases diferentes para o mesmo fato divergiriam na primeira
edição. A emissão computada fica fora da lista porque não recusa: normaliza (FR-3900).

### D-004 — Mudança de papel por Retificação torna o ato obsoleto, e não excedente nem vigente

O ato emitido num recorte cujo papel mudou não é reaproveitado automaticamente (8ª decisão do usuário).
O desenho proposto: no recorte que **passa a ser operacional**, o ato antigo aparece obsoleto, com a
causa nomeada, e o trabalho segue pela sucessão que já existe — relação nova, sorteio novo, ato novo.

A alternativa considerada era reaproveitá-lo quando o universo fosse o mesmo, já que a lista de quem
declarou a Modalidade não muda com o apontamento. Ela foi descartada por ora porque exige comparar
universos, método e versão num caminho novo, e o caso é raro. Se o usuário preferir a alternativa, a
FR-3912 muda, e o plano mede o custo.

### D-005 — A página pública de verificação não ganha explicação

A verificação pública confirma que o registro é o que foi publicado. Ela não o qualifica. Acrescentar
a ela a frase da FR-3903 mudaria uma página que o candidato e terceiros já consultaram, e a explicação
é devida a quem opera. O que o candidato vê fica registrado sem desenvolver.

### D-006 — A sucessão no recorte excedente também é recusada

Emitir um ato sucessor, constituir um sorteio que anula o anterior ou suceder uma relação no recorte
excedente são recusados como o primeiro gesto. Um registro excedente não tem uso operacional a
corrigir, e a sucessão dele produziria trabalho que nenhuma tela cobra.

### D-007 — Os sinais da Supervisão seguem os recortes, e não os atos

A Supervisão continua perguntando recorte a recorte, como desde a `034`. Ela só deixa de tratar o
marco por sorteio como exceção. Perguntar ato a ato acharia o registro excedente de novo.

## Registrado, sem desenvolver

- **Modalidade "Ampla concorrência" sem apontamento.** Um Perfil pode declarar uma Modalidade com esse
  nome e não apontá-la como a ampla. Ela é, então, recorte operacional na operação inteira, e a tela
  mostra dois blocos de ampla. A regra pelo apontamento, e não pelo texto, é a certa; esse Edital fica
  como está. Avisar na composição é decisão de outra feature.
- **O que o candidato vê de uma publicação excedente já feita.** O acompanhamento (`063`) e os avisos
  (`066`) continuam mostrando o que foi publicado. Se a medição da instalação (Assumptions) encontrar
  publicação excedente, o usuário decide se o portal precisa de explicação.
- **Modalidade removida por Retificação.** Os registros dela ficam fora da derivação canônica pela
  mesma regra. Esta spec não mede nem muda o que as telas mostram deles hoje.
