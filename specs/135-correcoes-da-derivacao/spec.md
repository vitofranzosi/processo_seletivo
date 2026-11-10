# Feature Specification: O andamento diz o que cada providência é

**Feature Branch**: `claude/135-correcoes-da-derivacao`, sobre a `main` em `0254fb91`

**Created**: 2026-11-09

**Status**: Draft, para revisão antes do plano.

**Nenhuma regra de domínio nova.** Esta spec corrige a derivação e o texto do andamento da `127`. Não
há migration, tabela, coluna, permissão, estado persistido nem regra de disponibilidade nova.

**Input**: *"Correções da derivação do andamento reveladas pelo estudo do Centro de Controle (C3 do
plano): (1) a providência de ordem de lista sem inscritos diz que a lista é vazia e o que o ato
declara; (2) a célula do resultado diz de forma estruturada o que já foi divulgado
(preliminar/definitivo) sem mudar a situação, que segue a D8a do estudo de 06/11 adotada pela 127;
(3) a espera do definitivo não oferece publicar como preliminar quando o preliminar do ato vigente já
está publicado; (4) as contagens de providências do Perfil e do Edital dizem o seu escopo. Nenhuma
regra de disponibilidade nova, nenhuma tabela, orçamento de consulta da 127 preservado."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil seiscentos e setenta a quatro mil seiscentos e noventa e
>   nove;
> - os critérios de mil quatrocentos e sessenta a mil quatrocentos e sessenta e nove.
>
> Os números não usados ficam livres, e a folga é de propósito. **Nenhum `UX-` é aberto aqui.** As
> decisões reiniciam em `D-001`.
>
> O teto foi medido em 09/11/2026, nas `specs/` de todas as worktrees desta máquina e de todas as
> branches remotas: requisito quatro mil seiscentos e cinquenta e seis, critério mil quatrocentos e
> cinquenta e seis, e UX-313. A pasta `135` não existia em lugar nenhum.
>
> **O número da spec e as faixas foram escolhidos nesta sessão, sem consulta.** A escolha é do
> usuário, e pode mudar antes do plano.
>
> **Como esta spec cita outras.**
> - Requisito de outra feature: pelo identificador e pela feature ("a FR-4071 da `127`").
> - Decisão de outra feature: pelo assunto e pela feature.
>
> **Origem.** O
> [estudo do Centro de Controle do Edital, de 09/11/2026](../../doc/estudo-centro-de-controle-2026-11-09/README.md)
> (PR #439):
> - achados A-07, A-08 e A-09;
> - lacunas G-1, G-3 e G-7.
>
> É a spec C3 do plano do estudo, a primeira do MVP recomendado. É também a única que não depende das
> oito decisões de produto listadas no README do estudo — **que seguem pendentes e não são tomadas
> aqui**.

## Por que esta feature existe

O estudo de 09/11 leu os 15 cenários de treinamento (`134`) pela derivação da `127`. Sobre ela,
desenhou um protótipo que destaca a ação do operador quando ela é uma só.

No C08, o destaque caiu em **"Emitir a ordem — PPP"**. Ninguém concorre pela PPP naquele Edital. O ato
é legítimo: emitir a ordem vazia declara que ninguém concorreu ali. Mas a providência não diz isso, e
quem a lê entende que há uma classificação a fazer.

O mesmo estudo achou mais três pontos em que o andamento diz menos do que sabe, ou diz outra coisa.

1. **A lista sem inscritos não é dita antes do ato** (A-09, G-1).
   - Nos C08, C12 e C14, a lista PPP está vazia, e a providência é "Emitir a ordem", idêntica à de uma
     lista com inscritos.
   - A tela do ato explica: *"a ordem vazia é um fato normativo, e emiti-la declara que ninguém
     concorreu ali"*. O andamento, não.
   - Depois de emitida, a célula ganha a nota "ninguém concorreu". Antes da emissão, não há nada.
2. **O que foi divulgado é lido do texto da nota** (G-3).
   - Com o preliminar publicado, a célula do resultado fica *Aguarda* ou *Pendente* (o definitivo), e
     não *Feito*. **Isso é decisão, e esta spec a preserva**: a D8a do estudo de 06/11, adotada pela
     `127`, faz o preliminar seguir a pendência do definitivo.
   - O problema é outro. A informação "o preliminar está publicado" existe só como a palavra
     "preliminar" dentro da nota.
   - Duas funções decidem por esse texto: a da situação do resultado e a do resumo do Perfil
     ("resultado publicado em 1 de 2 listas"). Mudar a redação da nota mudaria o comportamento, e
     nenhum teste de regra perceberia.
3. **A espera do definitivo oferece o que já foi feito** (A-08).
   - No C08 e no C12, a espera diz: *"O prazo recursal deste marco ainda está aberto … Aguarde o
     encerramento, **ou publique como resultado preliminar**"*. O preliminar do ato vigente já está
     publicado.
   - A frase é a mensagem da aferição da publicabilidade. Ela foi escrita para a tela de publicação,
     onde a escolha entre preliminar e definitivo faz sentido. O andamento a lê sem olhar o que já está
     publicado.
   - A mensagem do recurso pendente tem o mesmo final.
4. **Duas contagens com as mesmas palavras e escopos diferentes** (A-07).
   - No C06, o cartão "O que fazer agora" diz *"2 providências em aberto · 2 são suas"*. Na mesma
     página, o resumo do Perfil diz *"1 providência em aberto"*.
   - As duas estão certas. As providências das Etapas são do Edital e, por decisão do código, ficam
     fora da contagem do Perfil, que as resume em "Etapas X de Y".
   - O defeito é que nenhum dos dois números diz o seu escopo.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- a informação de lista em que ninguém concorre na célula e na providência da ordem por pontuação,
  antes da emissão;
- a natureza do que foi divulgado, como dado da célula do resultado;
- a razão da espera do definitivo no andamento;
- a redação das duas contagens.

**Fica fora:**
- a reorganização do detalhe do Edital, a trilha de macrofases e o destaque de "Sua próxima ação".
  São as specs C1 e C2 do estudo, que dependem das quatro primeiras decisões de produto de lá;
- a situação da célula do resultado com o preliminar publicado, que fica como está (D-002);
- a lista vazia no sorteio, que já é *Não se aplica* pela `126`;
- as mensagens da aferição da publicabilidade na tela de publicação e nas recusas do comando;
- o achado A-03 do estudo (observar a extração antes do congelamento), que depende da decisão de
  produto sobre o rito do sorteio, de lá;
- qualquer mudança no que o comando aceita ou recusa.

## Clarifications

Nenhuma pergunta aberta. As escolhas que esta spec faz por conta própria estão em *Decisões* e em
*Assumptions*, e o usuário pode revê-las antes do plano.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A lista sem inscritos é dita antes da ordem (Priority: P1)

Quem conduz uma seleção por pontuação abre o Edital. Entre as providências está a ordem de uma lista
pela qual ninguém concorreu. Hoje essa providência é igual à de qualquer outra lista, e a pessoa só
descobre na tela do ato que não há classificação a fazer, e sim uma declaração.

**Why this priority**: é o defeito que torna inseguro destacar uma ação — a C1 do estudo depende dele.
É também o que mais induz a uma leitura errada: "há uma classificação a fazer na PPP".

**Independent Test**: no C08 (PPP sem inscritos), como a presidência, três lugares dizem que ninguém
concorre pela lista e que o ato declara que ninguém concorreu:
- o cartão "O que fazer agora";
- o "Andamento da seleção";
- o "Próximo nesta lista".

No C04 (PPP com inscritos), nada muda.

**Acceptance Scenarios**:

1. **Given** um Edital por pontuação, com uma lista pela qual nenhuma inscrição concorre e a ordem
   dessa lista não emitida, **When** quem conduz abre o detalhe do Edital, **Then** a providência da
   ordem dessa lista:
   - diz que ninguém concorre pela lista e que emitir declara que ninguém concorreu;
   - continua sendo providência de quem conduz, com o link para a mesma tela.
2. **Given** o mesmo Edital, **When** a pessoa abre a matriz do "Andamento da seleção", **Then** a
   célula da ordem da lista vazia continua *Pendente* e traz a nota de que ninguém concorre.
3. **Given** a ordem vazia já emitida, **When** a pessoa abre o detalhe, **Then** a célula fica
   *Feito*, com a nota "ninguém concorreu", como hoje.
4. **Given** uma lista com ao menos uma inscrição, **When** a pessoa abre o detalhe, **Then** a
   providência e a célula são as de hoje, sem menção a lista vazia.
5. **Given** quem publica resultado, ou quem só acompanha, **When** abre o detalhe, **Then** a
   providência de outro papel ("Quem conduz a seleção: …") também diz que ninguém concorre.

---

### User Story 2 — O que foi divulgado é dado, e não texto (Priority: P2)

Quem lê o andamento — e quem o programa — precisa saber, de cada lista, se o público lê nada, um
preliminar ou um definitivo. Hoje essa informação mora dentro da nota.

**Why this priority**: não muda o que a pessoa vê hoje. Mas é a base de qualquer apresentação nova
que diga "preliminar publicado" (o estudo precisou ler a nota para isso), e protege o comportamento
atual contra uma mudança de redação.

**Independent Test**: num teste com a redação das notas trocada, a situação das células do resultado e
o resumo do Perfil continuam os mesmos em todos os casos de divulgação existentes.

**Acceptance Scenarios**:

1. **Given** uma lista com o preliminar do ato vigente publicado e o prazo recursal aberto, **When** o
   andamento é derivado, **Then** a célula do resultado é *Aguarda*, como hoje, **e** informa, como
   dado próprio, que o divulgado é o preliminar.
2. **Given** uma lista com o definitivo publicado, **When** o andamento é derivado, **Then** a célula é
   *Feito*, como hoje, e informa que o divulgado é o definitivo.
3. **Given** uma lista sem divulgação, **When** o andamento é derivado, **Then** a célula informa que
   nada foi divulgado.
4. **Given** uma lista cuja divulgação vigente lê um ato anterior (*Obsoleto*), **When** o andamento é
   derivado, **Then** a célula informa a natureza do que o público lê hoje.
5. **Given** qualquer dos casos acima, **When** a redação da nota muda, **Then** a situação da célula e
   o resumo do Perfil não mudam.

---

### User Story 3 — A espera do definitivo não oferece o que já foi feito (Priority: P2)

Na espera do definitivo, quem conduz ou publica lê por que esperar e até quando. Hoje lê também "ou
publique como resultado preliminar", quando o preliminar já está publicado.

**Why this priority**: a frase sugere um ato já praticado e faz a pessoa duvidar do que está
publicado.

**Independent Test**: no C08 e no C12 (preliminar publicado, prazo recursal aberto até 14/11), a
espera do definitivo diz o prazo e o motivo, e não oferece publicar como preliminar. Na tela de
publicação do mesmo marco, a mensagem continua a de hoje.

**Acceptance Scenarios**:

1. **Given** o preliminar do ato vigente publicado e o prazo recursal aberto, **When** a pessoa lê a
   espera do definitivo no andamento, **Then** a razão diz que o prazo está aberto e até quando, e não
   oferece publicar como preliminar.
2. **Given** o preliminar publicado e um recurso pendente de julgamento, **When** a pessoa lê a espera,
   **Then** a razão diz que há recurso pendente, e não oferece publicar como preliminar.
3. **Given** os mesmos casos, **When** a pessoa abre a tela de publicação do marco, **Then** a
   mensagem da aferição é a de hoje, palavra por palavra.
4. **Given** qualquer outra razão de espera ou de impedimento do definitivo, **When** a pessoa a lê,
   **Then** ela é a de hoje.

---

### User Story 4 — Cada contagem diz o que conta (Priority: P3)

Quem abre o detalhe do Edital vê um número de providências no cartão "O que fazer agora" e outro no
resumo de cada Perfil. Precisa entender por que os dois são diferentes.

**Why this priority**: as duas contagens estão certas; o custo é a desconfiança. A correção é só de
texto.

**Independent Test**: no C06, o cartão diz o total do Edital, e o resumo do Perfil diz que conta só as
providências dos marcos. Nenhum dos dois números muda.

**Acceptance Scenarios**:

1. **Given** um Edital com uma providência de Etapa e uma de marco, **When** a pessoa lê o resumo do
   Perfil, **Then** a contagem diz que é das providências dos marcos do Perfil.
2. **Given** o mesmo Edital, **When** a pessoa lê o cartão "O que fazer agora", **Then** a contagem é a
   de hoje, do Edital inteiro.
3. **Given** um Perfil sem providência de marco, **When** a pessoa lê o resumo, **Then** a contagem não
   aparece, como hoje.

---

### Edge Cases

- **A lista fica vazia por Retificação** (a modalidade deixa de existir, ou a inscrição deixa de
  concorrer por ela). A contagem é a do conteúdo vigente na data da leitura, a mesma que a tela do
  ato usa.
- **A lista vazia com a ordem obsoleta.** A célula é *Obsoleto*, como hoje. Se a lista seguir vazia, a
  nota de que ninguém concorre acompanha.
- **A lista que tinha inscritos e ficou sem nenhum que concorra** (desistência antes da ordem, por
  exemplo). Vale a contagem da leitura: a providência diz que ninguém concorre pela lista.
- **A lista cujas inscrições foram todas eliminadas numa Etapa anterior à do marco.** Ninguém
  concorre por ela no marco, pelo critério da tela da ordenação, e a lista é vazia. Por isso a
  frase diz que **ninguém concorre**, e não que a lista não tem inscritos: houve inscrição, e quem
  lesse "sem inscritos" entenderia que ninguém se inscreveu (a revisão do PR #441).
- **A ordem que o comando recusa por falta de resultado** (`128`). A recusa continua prevalecendo
  sobre a lista vazia: a célula é a de hoje (*Depois* ou *Impedido*), e a lista vazia não a transforma
  em *Pendente*.
- **A lista vazia no sorteio.** *Não se aplica*, pela `126`, sem mudança.
- **O Edital que não pede definitivo** (o preliminar basta). A célula segue a regra de hoje, e o dado
  da divulgação diz "preliminar".
- **Preliminar publicado e ordem obsoleta** (FR-4550 da `133`). A célula é *Depois*, como hoje, e o
  dado diz o que o público lê.
- **Vários marcos no Perfil.** A contagem do Perfil é a de todos os marcos dele, como hoje.
- **Quem não vê a matriz** (a decisão da `127` sobre quem vê o nível 2). Vê o resumo do Perfil com a contagem rotulada, e as
  providências com a menção à lista vazia. Não ganha acesso a nada novo.
- **Duas listas vazias no mesmo marco.** A providência agrupada (a decisão da `127` de uma providência
  por ato) diz quais listas são,
  e que ninguém concorre em nenhuma. Uma lista vazia e uma em que alguém concorre, no mesmo ato,
  não se agrupam como se fossem iguais.

## Requirements *(mandatory)*

### Functional Requirements

**A lista em que ninguém concorre (A-09, G-1)**

- **FR-4670**: Para cada lista de um marco por pontuação cuja ordem ainda não foi emitida, a derivação
  do andamento MUST saber se alguma inscrição concorre por ela. O critério MUST ser o mesmo que a tela
  da ordenação usa para dizer "ninguém concorreu por este recorte".
- **FR-4671**: Para lista em que ninguém concorre, a célula da ordem:
  - MUST continuar *Pendente*, de quem conduz, com o mesmo link de hoje;
  - MUST trazer a nota de que ninguém concorre pela lista.
- **FR-4672**: A providência dessa célula MUST dizer, na própria frase do ato, que ninguém concorre
  pela lista e que emitir declara que ninguém concorreu, em linguagem simples e sem identificador
  interno. MUST NOT dizer que a lista não tem inscritos, que é falso quando as inscrições dela foram
  eliminadas numa Etapa anterior. O texto exato é do plano.
- **FR-4673**: A providência MUST carregar a informação de lista vazia também como dado, além do texto,
  para que a apresentação possa tratá-la sem ler a frase.
- **FR-4674**: O agrupamento das providências (a decisão da `127` de uma providência por ato) MUST NOT juntar num mesmo item a ordem
  de lista vazia e a de lista com inscritos.
- **FR-4675**: Quando a próxima providência for a ordem de lista vazia, as transições "Próximo nesta
  lista" (FR-4090 da `127`) MUST mostrar a mesma frase da providência.
- **FR-4676**: A FR-4671 MUST NOT mudar a situação de nenhuma célula. A recusa da `128` e a
  obsolescência continuam decidindo como hoje.

**O que foi divulgado (G-3)**

- **FR-4677**: A célula do resultado MUST informar, como dado próprio, a natureza do que o público lê
  hoje naquela lista: nada, o preliminar ou o definitivo.
- **FR-4678**: A situação da célula do resultado MUST continuar a de hoje em todos os casos. O
  preliminar publicado MUST NOT virar *Feito* (D-002).
- **FR-4679**: A situação do resultado e o resumo do Perfil MUST ser decididos pelo dado da FR-4677, e
  não pelo texto da nota.
- **FR-4680**: A nota da célula MUST continuar dizendo o que diz hoje.

**A razão da espera do definitivo (A-08)**

- **FR-4681**: Com o preliminar do ato vigente publicado e o definitivo à espera do prazo recursal ou do
  julgamento de recurso, a razão mostrada no andamento (nível 1, matriz e "Próximo nesta lista"):
  - MUST dizer o motivo e, quando houver, até quando;
  - MUST NOT oferecer publicar como preliminar.
- **FR-4682**: As mensagens da aferição da publicabilidade MUST continuar as de hoje na tela de
  publicação e nas recusas do comando (D-003).
- **FR-4683**: As outras razões de espera e de impedimento do definitivo MUST continuar as de hoje.

**As contagens (A-07, G-7)**

- **FR-4684**: A contagem de providências no resumo de cada Perfil MUST dizer, em palavras, que conta
  as providências dos marcos daquele Perfil.
- **FR-4685**: Os números das duas contagens MUST continuar os de hoje. As providências das Etapas
  continuam fora da contagem do Perfil (D-004).

**Restrições**

- **FR-4686**: O custo de leitura do detalhe do Edital MUST continuar fixo por Edital (FR-4120 da
  `127`). Se a FR-4670 exigir leitura nova, ela MUST ter custo fixo por Edital ou por marco, e nunca
  crescer com as inscrições.
- **FR-4687**: Nenhuma mudança MUST alterar o que um comando aceita ou recusa, quem vê o quê, ou
  qualquer documento já publicado.

### Key Entities

- **Célula do andamento** (`127`). Ganha dois dados de leitura: lista em que ninguém concorre (na ordem) e
  natureza do divulgado (no resultado). Nada é persistido.
- **Providência** (`127`). Ganha o dado de lista vazia, herdado da célula.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1460**: Nos C08, C12 e C14 da `134` (PPP sem inscritos), **zero** providências de ordem da PPP
  sem a menção de que ninguém concorre pela lista, para qualquer papel que veja a providência.
- **SC-1461**: No C04 (PPP com inscritos), **zero** menções a lista vazia.
- **SC-1462**: No C08 e no C12:
  - **zero** razões de espera do definitivo, no andamento, que ofereçam publicar como preliminar;
  - na tela de publicação do mesmo marco, a mensagem é idêntica à de antes.
- **SC-1463**: Num teste com a redação das notas do resultado trocada, **100%** dos casos de
  divulgação existentes na suíte da `127` e da `133` mantêm a situação da célula e o resumo do Perfil.
- **SC-1464**: No C06, o resumo do Perfil diz o escopo da contagem, e os dois números são os de
  antes.
- **SC-1465**: Nos testes de orçamento da `127`, o número de consultas do detalhe do Edital não cresce
  com o número de inscrições.
- **SC-1466**: **Zero** migrations, tabelas, colunas, permissões ou estados persistidos novos. A suíte
  contra PostgreSQL fecha sem falha nova em relação à linha de base da branch.

## Assumptions

- O estudo de 09/11 (PR #439) é a evidência. Os cenários da `134` são o roteiro da verificação no
  navegador: C04, C06, C08, C12 e C14.
- "Inscrição que concorre pela lista" é o critério que a tela da ordenação já usa. A spec não define
  critério novo.
- O texto exato das frases (lista vazia, contagem, razão da espera) é do plano, em linguagem simples.
- A demonstração no navegador e `make lint check test-pg` fazem parte da verificação da entrega.

## Compatibilidade com regras anteriores

| Regra | O que esta spec faz com ela |
|---|---|
| D8a do estudo de 06/11, adotada pela `127` (o preliminar segue o definitivo) | Mantém (D-002). Só acrescenta o dado |
| "Ninguém concorreu é nota, e não estado" (condução do marco) | Mantém, e estende a nota para antes da emissão |
| *Não se aplica* da lista vazia no sorteio (`126`) | Intocado |
| A recusa da ordem sem resultado (`128`) | Prevalece sobre a lista vazia (FR-4676) |
| FR-4071 e FR-4090 da `127` | A célula do resultado ganha um dado; as transições leem a frase nova |
| Uma providência por ato, e não por célula (decisão da `127`) | Mantém, sem juntar lista vazia com lista com inscritos (FR-4674) |
| FR-4120 da `127` (custo fixo) | Mantém (FR-4686) |
| As mensagens da publicabilidade (`099`/`113`) | Intocadas na tela de publicação e no comando (D-003) |

## Achado fora do escopo (registro)

- **A-03 do estudo.** A tela do sorteio oferece "Observar a ocorrência" antes de congelar as relações
  do marco, enquanto a derivação diz *Depois*. Depende da decisão de produto sobre o rito do sorteio,
  listada no estudo, que é do usuário.
- **A-10 do estudo.** "Próximos marcos", na página do Processo, lê só o cronograma declarado. É da C5
  do estudo.

## Decisões

### D-001 — A lista vazia continua providência, e não *Não se aplica*

**Alternativas.**
- (a) *Não se aplica*, como no sorteio.
- (b) *Pendente*, dizendo que a lista é vazia.

**Escolha: (b).** Na pontuação, a ordem vazia é ato normativo: emiti-la declara que ninguém concorreu.
A condução do marco já trata "ninguém concorreu" como nota de um ato feito, e não como estado. Tirar
a providência faria o ato sumir do andamento sem ter sido praticado.

O sorteio é diferente, porque ali não há relação a congelar, e a `126` já decidiu esse caso.

### D-002 — O preliminar publicado continua sem ser *Feito*

A D8a do estudo de 06/11, adotada pela `127`, faz o preliminar seguir a pendência do definitivo. Esta
spec acrescenta o dado do que foi divulgado e não muda a situação. Mudá-la seria outra decisão, do
usuário.

### D-003 — Muda a razão no andamento, e não a mensagem da publicabilidade

A mensagem da aferição foi escrita para dois lugares:
- a tela de publicação, onde escolher entre preliminar e definitivo faz sentido;
- a recusa do comando.

Nos dois, ela continua a mesma. Só muda a razão que o andamento mostra quando o preliminar do ato
vigente já está publicado: essa deixa de oferecer a alternativa. É uma segunda mensagem, e não uma
edição da primeira.

### D-004 — A contagem do Perfil diz o escopo, e não soma as Etapas

As providências das Etapas são do Edital, e o resumo do Perfil as diz em "Etapas X de Y" — decisão
registrada no código do resumo. Somá-las:
- mudaria essa decisão;
- contaria duas vezes a mesma providência num Edital com dois Perfis.

Dizer o escopo resolve a desconfiança sem mudar número nenhum.
