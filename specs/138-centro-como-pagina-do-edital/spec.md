# Feature Specification: O Centro de Controle passa a ser a página do Edital

**Feature Branch**: `claude/138-centro-como-padrao-f6f2a9`, sobre a `main` em `daba322f`

**Created**: 2026-11-10

**Status**: Draft.

**Nenhuma regra de domínio nova.** Esta spec troca a página que a rota do Edital desenha. Não há
migration, tabela, coluna, permissão, estado persistido, regra de disponibilidade nem regra de
autorização nova. A porta continua a do detalhe, e todo botão continua levando à tela real do ato,
que é a que autoriza e a que recusa.

**Input**: *"O Centro de Controle do Edital passa a ser a página do Edital (incremento 3 do plano de
produção de 09/11). A rota do Edital desenha o Centro sempre que há andamento; fora dele, o detalhe
atual. A rota /centro/ redireciona para a do Edital preservando a query. O retorno do ato (?ato=) e a
conferência da 116 aparecem no Centro. Sai a marca de validação (botão, faixa, '› Centro de Controle'
no caminho, 'provisórios' nos conceitos). A página anterior fica acessível por um ciclo numa rota
discreta, por um link só no bloco Administração e histórico. Nenhuma regra nova de disponibilidade,
autorização ou estado."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil oitocentos e sessenta a quatro mil oitocentos e oitenta e
>   nove;
> - os critérios de mil quinhentos e vinte a mil quinhentos e vinte e nove;
> - os requisitos de experiência de trezentos e quarenta e cinco a trezentos e cinquenta e quatro.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 10/11/2026, nas `specs/` da `main`, de todas as branches remotas e de todas as
> worktrees desta máquina: requisito quatro mil oitocentos e quarenta e cinco, critério mil
> quinhentos e dezesseis e UX-342. A faixa começa com folga depois deles, e está anotada nas notas
> compartilhadas das sessões do Centro. A pasta `138` não existia em lugar nenhum; a `137` (o Processo
> agrega os Editais) continua reservada pelo plano, sem pasta, e **não** faz parte desta troca.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-4705 da `136`"); decisão de outra feature ou do estudo, pelo assunto ("a segunda decisão do
> estudo do Centro"), nunca pelo identificador.
>
> **Origem.** O
> [plano de produção do Centro de Controle, de 09/11/2026](../../doc/estudo-centro-de-controle-2026-11-09/08-plano-de-producao.md),
> seção 2, incremento 3; e as decisões do usuário de 10/11, registradas abaixo (D-001).

## Por que esta feature existe

O Centro de Controle do Edital (`136`) foi implantado numa rota própria, ao lado do detalhe, com um
botão "Abrir o Centro de Controle do Edital (em validação)" no detalhe e uma faixa "Em validação" no
topo do Centro. O plano previa trocar o padrão só depois de três coisas: a validação com 3 a 5
operadores, a decisão de onde o Centro mora e a decisão de quem aprova os textos pedagógicos.

Em 10/11/2026 o usuário viu o botão no detalhe e escreveu:

> *"Pensei que o centro de controle já seria aplicado. Não vejo necessidade deste botão para
> validação."*

Depois que as specs `139`, `140` e `141` foram mergeadas, disse *"Siga"*. As três pré-condições
ficam, assim, resolvidas por decisão dele (D-001). O que sobra é a troca em si: hoje quem abre um
Edital publicado cai na página antiga e precisa de um clique a mais para ver onde a seleção está, e o
Centro se apresenta como experimento.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- a rota do Edital desenha o Centro quando há andamento, e o detalhe quando não há;
- a rota do Centro passa a levar à do Edital, preservando o que vem depois do `?`;
- o retorno de um ato do Edital ("Ato registrado: …", e a conferência do concurso da `116`) aparece no
  Centro;
- a marca de validação sai: o botão, a faixa, o "› Centro de Controle" do caminho e o "provisórios"
  dos conceitos;
- o que só o detalhe oferecia ao Edital publicado passa ao Centro (D-005);
- a página anterior fica acessível por um ciclo, numa rota discreta, por um link só.

**Fica fora:**
- a `137` (o Processo agrega os Editais);
- qualquer mudança de nome de fase, de passo ou do critério do destaque — a terceira e a quarta
  decisões do estudo do Centro continuam como a `136` as deixou; os textos só deixam de se dizer
  provisórios;
- a retirada da página anterior, que é de uma spec futura, depois do ciclo;
- o detalhe antes da publicação e no Edital cancelado, que não muda.

## Clarifications

Nenhuma pergunta aberta. As três condições que o plano punha antes desta troca foram resolvidas pelo
usuário em 10/11 (D-001); as escolhas que esta spec faz por conta própria estão em *Decisões* e em
*Assumptions*.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem abre o Edital publicado vê onde a seleção está (Priority: P1)

A presidência da comissão abre o Edital 01/2026, publicado, pela lista de Processos. Hoje cai no
detalhe, com o cartão "O que fazer agora" e um botão para o Centro. Depois desta spec, cai direto no
Centro: "Onde estamos", o mapa e a primeira providência, na mesma rota de sempre.

**Why this priority**: é a troca pedida. Sem ela, nada mais desta spec tem efeito.

**Independent Test**: abrir a rota do Edital de um Edital publicado e conferir que a página é o
Centro, sem faixa de validação; abrir a de um Edital em elaboração e conferir que é o detalhe.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com andamento, **When** a pessoa abre a página do Edital, **Then** vê
   o Centro — "Onde estamos", o mapa, "O que fazer agora" e "Administração e histórico" —, e o
   caminho de navegação termina em "Edital N/AAAA".
2. **Given** um Edital encerrado com andamento, **When** a pessoa abre a página do Edital, **Then** vê
   o Centro.
3. **Given** um Edital em elaboração, em revisão, homologado ou cancelado, **When** a pessoa abre a
   página do Edital, **Then** vê o detalhe de sempre, com a trilha e o bastão.
4. **Given** um Edital publicado cuja derivação do andamento falha, **When** a pessoa abre a página do
   Edital, **Then** vê o detalhe de sempre, e não um erro.
5. **Given** um Edital de outra unidade, ou um identificador inexistente, **When** a pessoa abre a
   página do Edital, **Then** recebe o mesmo 404, como hoje.

---

### User Story 2 — Depois de um ato do Edital, o retorno aparece onde a pessoa chega (Priority: P1)

O Publicador publica o Edital. A tela do ato o devolve à página do Edital com o ato no endereço.
Hoje o detalhe diz "Ato registrado: Publicação" e, quando houve conferência do concurso na Caixa, o
que ela disse. Depois da troca, a página do Edital publicado é o Centro — e o Centro precisa dizer o
mesmo, ou o ato fica sem retorno.

**Why this priority**: sem isso a troca quebra o retorno de Publicar e de Encerrar, que são os dois
atos do Edital cuja chegada tem andamento.

**Independent Test**: praticar cada ato do conjunto do Edital pela interface e conferir, na página de
chegada, a frase "Ato registrado" com o nome do ato.

**Acceptance Scenarios**:

1. **Given** um Edital homologado, **When** o Publicador publica, **Then** chega ao Centro com "Ato
   registrado: Publicação" e, se a conferência do concurso prosseguiu com advertência ou com nota, a
   mesma lista que o detalhe mostrava.
2. **Given** um Edital publicado em condições de encerrar, **When** a presidência encerra, **Then**
   chega ao Centro com "Ato registrado: Encerramento".
3. **Given** um Edital publicado, **When** alguém o cancela, **Then** chega ao detalhe (o cancelado
   não tem andamento) com "Ato registrado: Cancelamento", como hoje.
4. **Given** um Edital antes da publicação, **When** alguém submete, homologa, devolve ou revoga a
   homologação, **Then** chega ao detalhe com o retorno de sempre.

---

### User Story 3 — Os endereços do Centro continuam levando ao Centro (Priority: P2)

Quem guardou o endereço `/centro/` do Edital, ou segue o "Voltar ao Centro de Controle do Edital" da
`139` a partir de uma tela de ato, chega ao Centro, agora na rota do Edital — com a fase que tinha
escolhido.

**Why this priority**: links salvos e o retorno da `139` não podem quebrar; mas a troca funciona sem
eles.

**Independent Test**: abrir `/centro/?fase=classificacao` e conferir um único redirecionamento para a
rota do Edital com `?fase=classificacao`.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** a pessoa abre o endereço do Centro com ou sem parâmetros,
   **Then** é levada à página do Edital com os mesmos parâmetros, num redirecionamento só.
2. **Given** a tela de um ato com o bloco "Próximo nesta lista", **When** a pessoa segue "Voltar ao
   Centro de Controle do Edital", **Then** o link já aponta para a página do Edital.
3. **Given** um Edital de outra unidade, **When** a pessoa abre o endereço do Centro dele, **Then** o
   redirecionamento leva à página do Edital, que responde 404 — a mesma resposta para o Edital que
   não existe.

---

### User Story 4 — O Centro deixa de se apresentar como experimento (Priority: P2)

A faixa "Em validação. Os nomes e os textos desta página são provisórios" sai do topo; o botão "(em
validação)" sai do detalhe; o caminho de navegação não acrescenta mais "› Centro de Controle"; o
módulo dos conceitos deixa de se declarar provisório.

**Why this priority**: o usuário dispensou a validação; a faixa passou a dizer algo falso.

**Independent Test**: varrer o HTML do Centro e do detalhe atrás de "em validação" e "provisórios", e
as folhas atrás das regras que perderam a classe.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** a pessoa abre a página do Edital, **Then** não há faixa de
   validação nem a palavra "provisórios".
2. **Given** o detalhe de um Edital, **When** ele é desenhado em qualquer rota, **Then** não há o botão
   para o Centro.

---

### User Story 5 — A página anterior, por um ciclo (Priority: P3)

Quem se acostumou ao detalhe do Edital publicado ainda o encontra, por um link discreto no bloco
"Administração e histórico" do Centro. A página anterior é a de antes, sem mudança de comportamento,
numa rota própria; o caminho de navegação dela leva de volta ao Centro.

**Why this priority**: é a opção conservadora do próprio plano ("a vista anterior fica acessível por
um ciclo"), que o usuário não vetou. A troca funciona sem ela.

**Independent Test**: seguir o link do bloco "Administração e histórico" e conferir que a página é o
detalhe de antes, com o mesmo conteúdo para o mesmo papel.

**Acceptance Scenarios**:

1. **Given** o Centro de um Edital publicado, **When** a pessoa procura a página anterior, **Then**
   encontra **um** link, no bloco "Administração e histórico", sem aparência de botão.
2. **Given** a página anterior, **When** ela abre, **Then** desenha o detalhe de antes — andamento da
   seleção, "Quem atuou", documentos, Retificações em curso, ações —, e o caminho termina em "Edital
   N/AAAA › Página anterior", com "Edital N/AAAA" levando ao Centro.
3. **Given** um Edital de outra unidade ou inexistente, **When** a pessoa abre a página anterior dele,
   **Then** recebe o mesmo 404 da página do Edital.

### Edge Cases

- **Derivação indisponível.** O andamento que falha não derruba a página: a rota do Edital desenha o
  detalhe, exatamente como o Centro já levava ao detalhe nesse caso.
- **Ato com `?ato=` desconhecido.** O retorno diz o que a tabela de rótulos devolve para a chave, como
  o detalhe já fazia; não há recusa nova.
- **`?fase=` na página anterior.** É ignorado, como no detalhe.
- **`?ato=` e `?fase=` juntos.** O Centro mostra o retorno e abre a fase pedida; nenhum anula o outro.
- **O Edital encerrado.** Tem andamento e abre no Centro; Encerrar e Cancelar já não estão no conjunto
  de ações, e o bloco recolhido some, como na `136`.
- **Papel sem nenhuma ação.** O Centro diz "Nenhuma ação é sua agora" ou "Nada em aberto", como na
  `136`; o link da página anterior continua, porque não é ação.

## Requirements *(mandatory)*

### Functional Requirements

**A rota do Edital escolhe a composição**

- **FR-4860**: A página do Edital MUST desenhar o Centro de Controle sempre que a derivação do
  andamento devolver andamento para o Edital e a pessoa; caso contrário — antes da publicação, no
  cancelado, ou com a derivação indisponível —, MUST desenhar o detalhe de sempre.
- **FR-4861**: As duas composições MUST partir de uma leitura só do Edital: a porta, os participantes,
  as pendências, a segregação, o conjunto de ações, as Retificações em curso, o andamento e os
  destinos dos marcos, lidos uma vez, na ordem da FR-4705 da `136`. A rota MUST NOT ler o andamento
  duas vezes para decidir e para desenhar.
- **FR-4862**: A porta MUST continuar a do detalhe: sem identidade, a identificação; Edital
  inexistente ou de outra unidade, o mesmo 404.

**O endereço do Centro**

- **FR-4863**: O endereço do Centro MUST levar à página do Edital por um redirecionamento, com os
  mesmos parâmetros de consulta, e MUST NOT ter porta própria: a resposta é a mesma para qualquer
  identificador, e a página de destino aplica a dela.
- **FR-4864**: Todo link interno que levava ao endereço do Centro — entre eles o "Voltar ao Centro de
  Controle do Edital" do bloco do próximo passo (a FR-4768 da `139`) — MUST apontar para a página do
  Edital.

**O retorno do ato**

- **FR-4865**: Chegando com o ato no endereço, o Centro MUST dizer "Ato registrado: «nome do ato»",
  com o mesmo nome que o detalhe usa, e MUST mostrar o que a conferência do concurso disse naquele ato
  (a FR-3646 da `116`), com o mesmo texto do detalhe.
- **FR-4866**: Para cada ato do conjunto do Edital — submeter, homologar, devolver, revogar a
  homologação, publicar, encerrar e cancelar —, a página em que o ato chega MUST mostrar o retorno.

**A marca de validação**

- **FR-4867**: O Centro MUST NOT mostrar a faixa de validação, e o detalhe MUST NOT mostrar o botão
  para o Centro.
- **FR-4868**: O caminho de navegação do Centro MUST terminar em "Edital N/AAAA", marcado como a
  página atual, e o título da janela MUST ser o do Edital.
- **FR-4869**: O módulo dos conceitos MUST NOT se declarar provisório. Os textos não mudam.
- **FR-4870**: Nenhuma folha MUST guardar regra de classe que nenhum template use mais.

**O que só o detalhe oferecia**

- **FR-4871**: O bloco "Administração e histórico" do Centro MUST oferecer o que o detalhe oferecia ao
  Edital publicado e o Centro não tinha, nas mesmas condições: as respostas do assistente de dúvidas
  (a FR-1413 da `070`); a conversa com o assistente, só para quem participa do piloto e só com o
  piloto ligado; e o aviso de conteúdo imutável com a condução da `037`, que cala para quem pode
  retificar.
- **FR-4872**: O cartão "Quem atuou" do Centro MUST mostrar as datas de cada ato e a unidade da
  autoridade signatária, no lugar do link para o detalhe, que passaria a levar à própria página.

**A página anterior**

- **FR-4873**: A página anterior MUST existir numa rota própria do Edital, desenhando o detalhe de
  sempre, com a mesma porta, para qualquer situação do Edital.
- **FR-4874**: O Centro MUST oferecer **um** link para a página anterior, no bloco "Administração e
  histórico", e nenhum outro lugar do sistema MUST levar a ela.
- **FR-4875**: Na página anterior, o caminho de navegação MUST terminar em "Edital N/AAAA › Página
  anterior", com "Edital N/AAAA" levando à página do Edital.

**O que não muda**

- **FR-4876**: Nenhuma regra de disponibilidade, de autorização ou de estado MUST mudar: o conjunto de
  ações, as providências, a porta e as telas dos atos são os de antes.

### Requisitos de experiência

- **UX-345**: O link da página anterior é texto comum, no rodapé do bloco "Administração e histórico",
  em tom fraco, e diz que ela fica disponível por um ciclo. Nunca botão, nunca no topo.
- **UX-346**: O retorno do ato aparece no Centro no mesmo lugar e com a mesma aparência que no detalhe:
  logo abaixo do título, antes de "Onde estamos" ser lido.

### Key Entities

- **Leitura do Edital**: o que a porta e as funções do detalhe leem do Edital para a pessoa, uma vez,
  e de onde as duas composições saem. Não é persistida.
- **Página anterior**: o detalhe de sempre, numa rota própria, acessível por um ciclo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1520**: Nos cenários publicados da `134` que abrem no Centro (C06, C08 e C12, como
  presidência), a página do Edital abre no Centro em **zero** cliques a mais (antes, um).
- **SC-1521**: Os sete atos do conjunto do Edital mostram "Ato registrado" na página em que chegam:
  sete de sete.
- **SC-1522**: Nenhuma ocorrência de "em validação" ou de "provisórios" no HTML da página do Edital,
  publicada ou não, e no texto do módulo dos conceitos.
- **SC-1523**: O endereço do Centro leva à página do Edital em **um** redirecionamento, com os mesmos
  parâmetros.
- **SC-1524**: O número de consultas da página do Edital publicado continua fixo por Edital, no mesmo
  orçamento do Centro na `136`.
- **SC-1525**: A página anterior responde, para os mesmos papéis e Editais, o mesmo conteúdo que o
  detalhe respondia antes desta spec; as asserções dos testes do detalhe não mudam, só o endereço.
- **SC-1526**: Nenhuma violação de CSP, e os guardiões de citação, de inventário de negativas, de
  vocabulário, de estáticos e de acessibilidade passam.

## Assumptions

- **"Um ciclo"** é até a spec que retirar a página anterior, decisão do usuário. Esta spec não marca
  data.
- O link "Autoridade, unidade e datas" do Centro levava ao detalhe; com as datas e a unidade no próprio
  cartão (FR-4872), ele deixa de ser preciso, e a página anterior fica com um link só (FR-4874).
- O endereço do Centro guarda o fragmento: o navegador o reaplica depois do redirecionamento, sem que
  o servidor o veja.
- A validação com operadores não acontece antes da troca. Os ajustes que ela pediria (a terceira e a
  quarta decisões do estudo) ficam para quando houver uso real a observar.

## Compatibilidade com regras anteriores

- **`136`**: a composição do Centro é a mesma, com três acréscimos (o retorno do ato, o que só o detalhe
  oferecia e o link da página anterior) e uma retirada (a faixa). A primeira decisão da `136` — rota
  própria, ao lado do detalhe — é a que esta spec substitui; a segunda (fora do andamento, o detalhe)
  passa a ser a regra da própria rota do Edital.
- **`127`**: o detalhe continua desenhando o andamento da seleção; só deixa de ser a página padrão do
  Edital publicado.
- **`139`**: o retorno ao Centro do bloco do próximo passo passa a apontar para a página do Edital.
- **`141`**: a contagem do Centro (o *Depois* com ato vigente conta como em curso) não muda.
- **Inventário de negativas (`033`)**: a página anterior entra com a mesma classe do detalhe (escopo
  institucional ∪ inexistente); o Centro deixa de ter 404 próprio.

## Decisões

### D-001 — As decisões do usuário em 10/11

Em 10/11/2026, ao ver o botão "Abrir o Centro de Controle do Edital (em validação)", o usuário
escreveu: *"Pensei que o centro de controle já seria aplicado. Não vejo necessidade deste botão para
validação."* Depois do merge da `139`, da `140` e da `141`, disse *"Siga"*. Ficam registradas como
decisões dele:

1. **A validação com operadores fica dispensada** como pré-condição da troca. A seção 5 do plano de
   produção continua descrevendo como fazê-la, se e quando for útil.
2. **A segunda decisão do estudo do Centro — onde ele mora — fica decidida: o Centro mora na rota do
   Edital.**
3. **Os textos deixam de ser provisórios.** Corresponde à sétima decisão do estudo (quem aprova os
   textos pedagógicos): o usuário os aprova como estão.

A `135`, a terceira condição do plano para a liberação geral, já está mergeada.

### D-002 — A rota escolhe, e a leitura é uma só

A página do Edital lê o Edital uma vez e escolhe qual composição desenhar. Duas views que lessem por
conta própria divergiriam na próxima mudança — é a lição da `103` e da `104` que a `136` registrou ao
ler o detalhe "nas mesmas funções, na mesma ordem". Um redirecionamento da rota do Edital para uma
rota do Centro manteria duas portas e custaria uma ida a mais ao servidor em toda abertura.

### D-003 — O endereço do Centro redireciona sem porta própria

O redirecionamento é o mesmo para qualquer identificador; quem decide 404 é a página de destino. Uma
porta no redirecionamento leria o Edital duas vezes, e a resposta para o Edital de outra unidade
seria a mesma de qualquer forma.

### D-004 — A página anterior, por um ciclo, com um link só

É a opção conservadora do plano ("a vista anterior fica acessível por um ciclo"), que o usuário não
vetou: registrada como premissa, e não como decisão dele. O link é um, discreto, e mora no bloco de
administração, para que a página anterior não dispute com o Centro a atenção de quem chega. A rota é
a do detalhe sem nenhuma mudança de comportamento além do caminho de navegação, que precisa levar de
volta.

### D-005 — O que só o detalhe oferecia passa ao Centro

Para que a página anterior possa sair depois do ciclo sem levar consigo um destino, o Centro recebe o
que só o detalhe oferecia ao Edital publicado: as respostas do assistente de dúvidas, a conversa com o
assistente do piloto, o aviso de conteúdo imutável e as datas de "Quem atuou". São links e textos que
o detalhe já mostrava, nas mesmas condições: nenhuma regra nova.

### D-006 — O título é o do Edital

Com o Centro na rota do Edital, o título da janela e o fim do caminho de navegação são "Edital
N/AAAA". "Centro de Controle" deixa de nomear um lugar à parte; a página é a do Edital.
