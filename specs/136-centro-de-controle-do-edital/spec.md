# Feature Specification: Centro de Controle do Edital

**Feature Branch**: `claude/136-centro-de-controle-0cb557`, sobre a `main` em `0254fb91`

**Created**: 2026-11-09

**Status**: Implementada e mergeada (spec #442, implementação #443). *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Draft, para revisão antes do plano.

**Nenhuma regra de domínio nova.** Esta spec cria uma página de leitura sobre a derivação do
andamento da `127`. Não há migration, tabela, coluna, permissão, estado persistido, regra de
disponibilidade nem regra de autorização nova. Todo botão da página leva à tela real do ato, que
continua sendo a que autoriza e a que recusa.

**Input**: *"Centro de Controle do Edital (incremento 1 do plano de produção do estudo de
09/11/2026). Uma página nova do Edital publicado, numa rota própria ao lado do detalhe atual, com
link de ida e volta; o detalhe atual não muda. Quatro camadas da versão 2 do protótipo: (A) 'Onde
estamos' e os três estados separados e o mapa em três grupos, com o andamento da fase separado das
marcas de providência; (B) 'O que fazer agora', com o destaque por critério dito na tela, e o
detalhe da fase consultada com o roteiro em linguagem simples; (C) 'Onde cada lista está', só para
quem vê a matriz; (D) Administração e histórico, com Encerrar e Cancelar recolhidos. Nomes simples e
textos num módulo único de conceitos, marcados como provisórios. Toda situação vem da derivação da
127; nenhuma regra nova de disponibilidade nem de autorização. A fase consultada é distinta das
fases em curso. Orçamento de consultas fixo por Edital. CSP sem inline."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil e setecentos a quatro mil setecentos e cinquenta e nove;
> - os critérios de mil quatrocentos e setenta a mil quatrocentos e oitenta e nove;
> - os requisitos de experiência de trezentos e catorze a trezentos e vinte e nove.
>
> Os números não usados ficam livres, e a folga é de propósito. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 09/11/2026, nas `specs/` de todas as worktrees desta máquina, de todas as
> branches locais e de todas as branches remotas: requisito quatro mil seiscentos e oitenta e sete,
> critério mil quatrocentos e sessenta e seis, e UX-313, todos na worktree da `135`. A `135` reservou
> até o requisito quatro mil seiscentos e noventa e nove e o critério mil quatrocentos e sessenta e
> nove, e esta faixa começa depois da reserva. A pasta `136` não existia em lugar nenhum.
>
> **Como esta spec cita outras.**
> - Requisito de outra feature: pelo identificador e pela feature ("a FR-4120 da `127`"), e só os já
>   presentes na `main`. A `135` ainda não está nela; é citada pelo assunto.
> - Decisão de outra feature, e decisão do estudo: pelo assunto, ou pelo número por extenso ("a
>   primeira decisão do estudo"), nunca pelo identificador.
>
> **Origem.** O
> [estudo do Centro de Controle do Edital, de 09/11/2026](../../doc/estudo-centro-de-controle-2026-11-09/README.md)
> (PR #439): o plano de produção (`08-plano-de-producao.md`), que dá o escopo e os critérios de
> aceite desta spec, e a versão 2 do protótipo (`07-refinamento.md`), que dá o comportamento. O
> protótipo é referência de comportamento, e não código a copiar.

## Por que esta feature existe

O estudo de 09/11 perguntou se quem conduz, olhando um Edital publicado, consegue saber onde a
seleção está, o que já aconteceu, o que precisa fazer agora e o que vem depois. A resposta foi: **não
em palavras**.

O GPS já sabe quase tudo. A `127` lê os atos e dá, para cada ponto da jornada em cada lista, uma de
sete situações, com responsável, prazo e razão. O que falta é **dizer**:

1. **A situação do Edital é um selo só.** "Publicado" responde à situação administrativa e cala sobre
   a seleção. Num Edital que espera a semente e num que está convocando, o topo da página é o mesmo.
2. **Não há mapa.** A matriz por lista do "Andamento da seleção" tem tudo, mas é uma tabela de
   quinze colunas por Perfil, recolhida, e só para quem conduz ou audita.
3. **As providências não têm lugar na jornada.** "Emitir a ordem — PPP" não diz em que fase está, o
   que espera por ela, nem por que vem antes de outra.
4. **O vocabulário é o do GPS.** "Congelar a relação", "observar a extração", "apurar a ocupação" são
   termos certos, e exigem saber o que são para serem entendidos.
5. **A operação e a administração estão misturadas.** Encerrar e Cancelar — os gestos mais
   destrutivos — aparecem no mesmo cartão que a próxima ação da seleção.

### O que esta spec revê

**A `127` deixou de fora a barra de fases** (seção "Fica fora" daquela spec), e a recusa tinha uma
razão: o Edital **não tem** uma etapa atual, porque cada lista anda no seu ritmo, e uma barra única
mentiria. **O usuário decidiu, em 09/11, rever essa recusa** — é a primeira decisão do estudo,
tomada pela aprovação do conceito ("Representação de atividades paralelas — um dos maiores
acertos"). Esta spec a aplica conservando a razão da recusa e mudando a forma:

- **várias fases podem estar em curso ao mesmo tempo**, e o mapa as mostra todas;
- **nenhuma é eleita "a fase atual"** nem "a próxima"; a fase que a pessoa abre para ler é a fase
  **consultada**, e é visual e semanticamente distinta das fases **em curso**;
- nenhum percentual, e o resumo de cada fase diz "1 de 2 listas concluídas" quando for o caso.

A oitava decisão do estudo (o Processo agrega; o Centro é do Edital) também está tomada e só
delimita esta spec: nada aqui muda a página do Processo, que é a spec seguinte do plano.

### As decisões do estudo que seguem pendentes

**Nenhuma é tomada aqui.** O plano de produção as classifica pelo que bloqueiam, e nenhuma bloqueia o
desenvolvimento:

| Decisão do estudo | O que bloqueia | O que esta spec faz até lá |
|---|---|---|
| 2ª — onde mora o Centro | Só a troca do padrão (spec 138) | Rota própria, ao lado do detalhe, com link de ida e volta (D-001) |
| 3ª — os nomes das fases e dos passos | Nada; é o que a validação com operadores mede | Os nomes da versão 2, num módulo só, marcados como provisórios (D-006) |
| 4ª — o critério do destaque | **A liberação geral**, com a `135` | As três regras da versão 2, ditas na tela (D-005) |
| 5ª — observar a extração antes de congelar | Nada no Centro | Nada: a semente é *Ainda não começou* até haver relação congelada, como a derivação diz |
| 6ª — quem vê o detalhe por lista | Nada; só mudá-la exigiria decisão | A regra atual da `127` (quem conduz ou audita), testada no HTML (D-007) |
| 7ª — quem aprova os textos pedagógicos | **A liberação geral** | Os textos da versão 2, marcados como provisórios (D-006) |

**Liberação geral.** Esta spec entrega uma página nova numa rota própria. Ela **não** se torna o
padrão, e não deve ser divulgada a operadores como pronta, antes de três coisas, nenhuma delas desta
spec: a `135` implementada (sem ela, o destaque do C08 cai numa lista sem inscritos sem dizê-lo), a
validação com três a cinco operadores, e a quarta e a sétima decisões do estudo.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- a página do Edital publicado ou encerrado, numa rota própria, com as quatro camadas;
- o módulo de conceitos, com os nomes simples e as frases;
- o link de ida e volta entre a página nova e o detalhe atual;
- os testes de agregação, de coerência com o andamento, de papel, de orçamento, de acessibilidade e
  uma jornada no navegador.

**Fica fora:**
- qualquer mudança no detalhe atual além do link de ida (a troca do padrão é a spec 138);
- a página do Processo (spec 137);
- as correções da derivação (`135`): esta spec só **lê** `andamento` e `providencias`;
- a leitura do módulo de conceitos pelos "Termos desta tela" das telas de ato;
- o sorteio (sexta correção do plano anterior), que espera a quinta decisão do estudo;
- notificação, percentual, "fase atual" persistida, motor de workflow.

## Clarifications

Nenhuma pergunta aberta. As escolhas que esta spec faz por conta própria estão em *Decisões* e em
*Assumptions*, e o usuário pode revê-las antes do plano.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Saber onde a seleção está (Priority: P1)

Quem conduz abre o Centro de Controle de um Edital publicado. Sem rolar a página, lê em palavras em
que fases há algo em aberto e de quem é, a situação administrativa, as inscrições e o próprio papel,
e vê um mapa das oito fases em três grupos, com o andamento de cada uma e as marcas do que ela
oferece agora.

**Why this priority**: é a pergunta do estudo. Sem ela, o resto é uma lista de ações sem lugar.

**Independent Test**: nos cenários C06, C08 e C12 da `134`, como a presidência, a 1440 × 900 px, a
frase "Onde estamos", o mapa e a primeira providência (ou a frase de que não há nenhuma) aparecem
sem rolar.

**Acceptance Scenarios**:

1. **Given** o C12 (convocação em curso numa lista, classificação a emitir em outra), **When** a
   presidência abre o Centro, **Then** "Onde estamos" nomeia as fases com algo em aberto e diz quantas
   ações são suas e quantas aguardam prazo, com a primeira data.
2. **Given** o mesmo Edital, **When** a pessoa olha o mapa, **Then** mais de uma fase aparece *Em
   curso*, nenhuma é rotulada "atual", e o andamento de cada fase (sinal e palavra) é separado das
   marcas de providência (sua, de outro papel, aguarda até, impedida, nada a fazer agora).
3. **Given** uma fase em curso sem nenhuma providência (Vagas no C12), **When** a pessoa a lê no mapa,
   **Then** ela diz *Em curso* e "nada a fazer agora".
4. **Given** qualquer Edital publicado, **When** a pessoa lê o topo, **Then** a situação
   administrativa, as inscrições e o papel dela aparecem como três estados separados, cada um com
   rótulo.

---

### User Story 2 — Saber o que fazer agora, e por quê (Priority: P1)

A pessoa lê as ações que são dela, as que estão com outros papéis e as que esperam um prazo, uma
resposta ou uma correção. Quando uma das suas se destaca, a tela diz por quê. Quando nenhuma se
destaca, a tela diz que o GPS não escolhe a ordem.

**Why this priority**: é o que faz a página servir para agir. O critério dito na tela é o que separa
um destaque de uma prioridade inventada.

**Independent Test**: no C06, a ação destacada é "Fixar os participantes", com "Por que esta" e os
passos que esperam por ela. No C12, nenhuma é destacada, e a tela diz que o GPS não escolhe a ordem.
No C08, a única ação da presidência é destacada com "É a única ação sua disponível agora".

**Acceptance Scenarios**:

1. **Given** uma pessoa com uma ação sua só, **When** abre o Centro, **Then** ela vem destacada, com
   "Por que esta: é a única ação sua disponível agora".
2. **Given** várias ações suas, das quais só uma não é paralela e destrava passos seguintes da mesma
   fase, **When** a pessoa abre o Centro, **Then** essa vem destacada, com "Por que esta" e os nomes
   dos passos que esperam por ela; as demais aparecem em "Também sua".
3. **Given** várias ações suas sem nenhuma que satisfaça a regra anterior, **When** a pessoa abre o
   Centro, **Then** nenhuma é destacada, e a tela diz que todas já podem ser feitas e que o GPS não
   escolhe a ordem entre elas.
4. **Given** uma pessoa sem ação sua, com ações de outros papéis, **When** abre o Centro, **Then** lê
   "Nenhuma ação é sua agora" e as ações dos outros papéis, nomeados.
5. **Given** um Edital sem nenhuma providência, **When** a pessoa abre o Centro, **Then** lê "Nada em
   aberto", com o porquê.
6. **Given** uma ação destacada ou listada, **When** a pessoa segue o botão ou o link, **Then** chega à
   tela real do ato, a mesma que o detalhe atual oferece.
7. **Given** uma providência impedida, **When** a pessoa a lê, **Then** vê por quê e quem resolve, e o
   caminho para a Retificação quando ela o tem.

---

### User Story 3 — Entender uma fase, em linguagem simples (Priority: P2)

A pessoa escolhe uma fase no mapa e lê, ao lado de "O que fazer agora", o que a fase responde, o
roteiro dos passos dela na língua de quem conduz (com o termo do GPS ao lado), em que ponto cada
passo está, por que um passo ainda não começou, e, por lista, a situação de cada ponto.

**Why this priority**: é o que tira o vocabulário do GPS do caminho de quem não o domina, e o que
explica "por que o sorteio ainda não pode".

**Independent Test**: no C12, abrir a Classificação: o cartão dela recebe a marca de fase
consultada, a Convocação continua com a marca de em curso, e as duas são distintas para o olho e
para o leitor de tela.

**Acceptance Scenarios**:

1. **Given** a pessoa abre o Centro sem escolher fase, **When** a página carrega, **Then** a fase
   consultada é escolhida por regra fixa (a da ação destacada; senão, a primeira com ação sua, a
   paralela por último; senão, a primeira com algo em aberto; senão, a primeira em curso; senão, a
   última concluída).
2. **Given** a pessoa escolhe outra fase no mapa, **When** a página recarrega, **Then** o detalhe é o
   dessa fase, e só o cartão dela leva a marca de fase consultada.
3. **Given** o C06 (relação a congelar), **When** a pessoa consulta a Classificação, **Then** o roteiro
   diz "Fixar os participantes — no GPS: congelar a relação", com a frase curta, e o passo "Obter a
   semente pública" diz *Ainda não começou* com a razão que a derivação dá.
4. **Given** quem não vê a matriz (não conduz nem audita), **When** consulta uma fase por lista,
   **Then** lê que o detalhe por lista é de quem conduz ou audita, e o HTML não traz a tabela.
5. **Given** a pessoa quer o "por quê" de cada passo, **When** abre "Entenda os passos desta fase",
   **Then** lê, para cada passo, o porquê e o que acontece ao confirmar.

---

### User Story 4 — Ver onde cada lista está (Priority: P2)

Quem conduz ou audita lê, por Perfil, uma linha por lista com o andamento de cada fase por lista e o
que há agora naquela lista, e pode abrir a matriz completa da `127`.

**Why this priority**: as listas andam em ritmos diferentes, e é aqui que isso se vê.

**Independent Test**: no C12, como a presidência, a lista PPP aparece com o que falta nela; como o
Publicador, a seção não vem no HTML.

**Acceptance Scenarios**:

1. **Given** quem vê a matriz, **When** abre o Centro, **Then** a seção "Onde cada lista está" mostra,
   por Perfil, uma linha por lista, com o andamento por fase e o que há agora nela.
2. **Given** quem não vê a matriz, **When** abre o Centro, **Then** a seção não está no HTML.
3. **Given** dois Perfis no mesmo Edital, **When** quem vê a matriz abre o Centro, **Then** cada Perfil
   tem o seu bloco, e o detalhe da fase separa os dois.

---

### User Story 5 — Administrar sem esbarrar no irreversível (Priority: P3)

Documentos publicados, consultas, quem atuou e a validação do conteúdo ficam juntos, depois da
operação. Encerrar e Cancelar ficam recolhidos, e só para quem os tem.

**Why this priority**: tira o gesto destrutivo do lugar da próxima ação, sem tirar o acesso.

**Independent Test**: como o Gestor, Encerrar e Cancelar estão num bloco recolhido; como a avaliação,
não estão no HTML.

**Acceptance Scenarios**:

1. **Given** quem tem Encerrar ou Cancelar, **When** abre o Centro, **Then** os dois estão num bloco
   recolhido, depois da administração, com a advertência de irreversibilidade.
2. **Given** quem não os tem, **When** abre o Centro, **Then** eles não estão no HTML.
3. **Given** qualquer papel, **When** abre o Centro, **Then** encontra os documentos publicados, as
   consultas que os papéis dele abrem, quem atuou e a validação do conteúdo.

---

### User Story 6 — Ir e voltar entre as duas páginas (Priority: P3)

Durante a validação, o detalhe atual continua sendo a página do Edital. Quem está nele encontra o
Centro, e quem está no Centro volta ao detalhe.

**Acceptance Scenarios**:

1. **Given** o detalhe de um Edital publicado ou encerrado, **When** a pessoa o lê, **Then** encontra
   o link para o Centro de Controle.
2. **Given** o Centro, **When** a pessoa o lê, **Then** encontra o link para o detalhe.
3. **Given** um Edital antes da publicação, ou cancelado, **When** alguém pede o Centro, **Then** é
   levado ao detalhe, e o detalhe não oferece o link.

---

### Edge Cases

- **Edital sem providência**: o C14 encerrado, ou fixture. "Nada em aberto", com o porquê da `127`;
  o mapa continua mostrando o andamento.
- **Prazo vencido**: a providência e a marca dizem a data como a derivação a dá; o Centro não calcula
  vencimento.
- **Impedimento com "quem resolve"**: a providência diz por quê e quem resolve; o caminho da
  Retificação aparece para quem pode retificar.
- **Retificação em curso**: uma faixa diz que ela está em curso e pode mudar datas, vagas ou regras;
  a fase "Edital" fica *Em curso*.
- **Dois Perfis no mesmo Edital**: nenhum cenário da `134` tem; coberto por fixture de teste.
- **Lista sem inscritos**: o Centro mostra a providência como a derivação a dá. Com a `135`, ela diz
  que a lista é vazia; sem ela, não diz (risco declarado da liberação geral).
- **Processo encerrado ou cancelado**: nenhuma ação é "sua"; o papel diz que o Processo está
  encerrado.
- **A derivação falha**: o andamento volta `None` e o detalhe cai para o cartão de antes da `127`; o
  Centro leva ao detalhe, sem 500.
- **Fase pedida inexistente** (`?fase=xyz`): vale a regra fixa da fase consultada.
- **Quem não alcança o Edital** (outra unidade, ou inexistente): 404, como o detalhe.
- **Tela estreita**: a 375 px o mapa vira lista vertical, as tabelas rolam dentro da moldura, e a
  página não rola na horizontal.

## Requirements *(mandatory)*

### Functional Requirements

**A página e a rota**

- **FR-4700**: O sistema MUST oferecer, para o Edital publicado ou encerrado, uma página própria — o
  Centro de Controle —, numa rota distinta da do detalhe do Edital.
- **FR-4701**: A página MUST alcançar o Edital pela mesma porta do detalhe (escopo institucional e
  existência), e responder 404 nos mesmos casos em que o detalhe responde.
- **FR-4702**: Para o Edital antes da publicação, cancelado, ou cujo andamento não pôde ser derivado,
  a rota MUST levar ao detalhe do Edital, sem erro.
- **FR-4703**: O detalhe atual MUST ganhar só um link para o Centro, quando houver andamento, e MUST
  NOT mudar em mais nada; a suíte dele MUST passar sem alteração.
- **FR-4704**: O Centro MUST ter um link para o detalhe do Edital.

**A fonte das situações**

- **FR-4705**: Toda situação mostrada MUST vir do andamento da `127` (pontos, células, providências,
  alcance) e das funções que o detalhe já chama para documentos, consultas, Retificações em curso,
  participantes e validação; o Centro MUST NOT ler fato do banco que o detalhe não lê.
- **FR-4706**: O Centro MUST NOT acrescentar regra de disponibilidade nem de autorização. Cada botão e
  link de ato MUST levar à tela real do ato, a mesma que a providência ou a célula já levam.
- **FR-4707**: Quem não pode praticar um ato MUST NOT receber o link dele no Centro, e a tela real do
  ato MUST continuar recusando essa pessoa.

**As macrofases (camada A)**

- **FR-4708**: O mapa MUST ter oito fases, nesta ordem e nestes três grupos: Abertura (Edital,
  Inscrições), Seleção (Avaliação, Classificação, Resultado e recursos, Vagas) e Ocupação
  (Convocação, Conclusão). Os grupos MUST NOT mudar regra nenhuma.
- **FR-4709**: Cada ponto da jornada MUST pertencer a uma fase por regra fixa: relação, semente,
  sorteio e ordem → Classificação; corte e apuração → Vagas; resultado → Resultado e recursos;
  convocação → Convocação; Etapa governada pela faixa → Vagas; demais Etapas → Avaliação.
- **FR-4710**: O andamento de uma fase numa lista MUST ser *Concluída* se, e só se, todas as células
  dela forem *Feito* ou *Não se aplica* e ao menos uma for *Feito*; *Não se aplica* se todas forem
  *Não se aplica*; *Ainda não começou* se todas forem *Depois* ou *Não se aplica*; e *Em curso* em
  qualquer outro caso.
- **FR-4711**: O andamento da fase no Edital MUST juntar o das listas: *Concluída* se todas as que se
  aplicam estão concluídas; *Ainda não começou* se nenhuma começou; *Em curso* em qualquer outro caso,
  inclusive uma lista concluída ao lado de outra que não começou.
- **FR-4712**: A fase Edital MUST ser *Concluída* no Edital publicado ou encerrado, e *Em curso*
  enquanto houver Retificação em curso, com a nota de que ela pode mudar datas, vagas ou regras.
- **FR-4713**: A fase Inscrições MUST seguir o período de inscrições que o andamento já lê (abertas,
  encerradas, canceladas, futuras), com a quantidade enviada.
- **FR-4714**: A fase Conclusão MUST ser *Concluída* no Edital encerrado; *Em curso* quando todas as
  listas concluíram, dizendo que o encerramento é do Gestor; e *Ainda não começou* nos demais casos. Ela
  MUST NOT afirmar que o Edital pode ser encerrado: quem decide é a tela do ato.
- **FR-4715**: Cada fase MUST mostrar, separado do andamento, o que oferece agora: quantas ações são
  da pessoa, quantas de outro papel, a primeira data de espera, se há impedida, e "nada a fazer agora"
  quando está em curso sem providência.
- **FR-4716**: Cada providência do nível 1 da `127` MUST pertencer a exatamente uma fase, pela
  natureza dela (Etapa governada → Vagas; demais Etapas, distribuir, avaliar, consolidar, reavaliar →
  Avaliação; conferir → Convocação; recurso → Resultado e recursos; os atos de marco pela regra da
  FR-4709). A soma das providências das fases MUST ser o total do nível 1.
  *Revista pela `153` em 11/11/2026:* a passagem ao setor da formalização (definir, designar,
  exportar) → Conclusão (FR-6115 da `153`).
- **FR-4717**: A marca "sua" de uma fase MUST existir se, e só se, há providência da pessoa nela.

**Onde estamos (camada A)**

- **FR-4718**: A frase "Onde estamos" MUST nomear as fases que têm providência agora — e não contar
  frentes —, ou dizer "Nada em aberto agora", com as fases em curso, quando não houver providência; ou
  "Seleção concluída" quando a Conclusão estiver concluída.
- **FR-4719**: A segunda frase MUST dizer de quem é o que está em aberto: quantas ações são da pessoa,
  quantas estão com outros papéis, quantas aguardam prazo ou resposta (com a primeira data) e quantas
  estão impedidas.
- **FR-4720**: O topo MUST mostrar três estados separados e rotulados: a situação administrativa do
  Edital (com a do Processo), as inscrições, e o papel da pessoa no Edital.
- **FR-4721**: O papel da pessoa MUST ser dito a partir do alcance da `127` (conduz, acompanha,
  publica resultados, julga recursos, propõe Retificações), e dizer que nenhum ato é seu quando o
  Processo está encerrado.

**O que fazer agora (camada B)**

- **FR-4722**: O destaque MUST seguir três regras, nesta ordem: (1) uma só ação da pessoa → é ela;
  (2) várias, das quais exatamente uma não é paralela e destrava passos seguintes da mesma fase → é
  essa; (3) qualquer outro caso → nenhum destaque.
- **FR-4723**: Com destaque, a tela MUST escrever "Por que esta:" e a razão da regra, e, quando houver,
  os passos que esperam pela ação.
- **FR-4724**: Sem destaque e com mais de uma ação da pessoa, a tela MUST dizer que todas já podem
  ser feitas e que o GPS não escolhe a ordem entre elas.
- **FR-4725**: Uma ação é **paralela** quando é de Avaliação e nenhum marco dos Perfis lê a Etapa — os
  Perfis com marco são todos por sorteio e nenhum declara Etapa de habilitação. A tela MUST dizer que
  ela é paralela ao sorteio.
- **FR-4726**: O cartão MUST listar, nesta ordem: o destaque, as demais ações da pessoa, as que
  esperam prazo, resposta ou correção (impedidas primeiro, com por quê e quem resolve), e as de outros
  papéis (com o papel nomeado).
- **FR-4727**: Sem ação da pessoa, o cartão MUST dizer "Nenhuma ação é sua agora"; sem providência
  nenhuma, "Nada em aberto", com o porquê que a `127` dá.
- **FR-4728**: Cada Retificação em curso MUST aparecer no cartão, com a situação dela e o link quando
  ela aguarda a pessoa.
- **FR-4729**: Os atos cujo nome no GPS é jargão (relação, semente, ordem, corte, apuração) MUST ter o
  nome simples como título e o nome do GPS como "no GPS: …".

**O detalhe da fase consultada (camada B)**

- **FR-4730**: Uma fase de cada vez MUST ser a fase consultada, escolhida pela pessoa no mapa ou, sem
  escolha válida, pela regra fixa da US3, cenário 1.
- **FR-4731**: O cartão da fase consultada MUST levar `aria-current` e um texto para leitor de tela
  ("fase consultada"); as fases em curso MUST NOT levá-lo.
- **FR-4732**: O detalhe MUST dizer a pergunta que a fase responde, o andamento, as marcas, a nota e a
  menção de paralela quando houver.
- **FR-4733**: Para quem vê a matriz, o detalhe de uma fase por lista MUST trazer, por Perfil, o
  roteiro (os passos na ordem, cada um com nome simples, termo do GPS, frase curta, andamento, a razão
  quando ainda não começou, se há ação agora, e quantas listas fizeram) e a tabela por lista com a
  situação, o ato e a nota de cada célula.
- **FR-4734**: Para quem não vê a matriz, o detalhe de uma fase por lista MUST NOT trazer a tabela nem
  o roteiro por lista, e MUST dizer que esse detalhe é de quem conduz ou audita.
- **FR-4735**: As fases Edital, Inscrições e Conclusão MUST ter detalhe próprio: os documentos
  publicados, a linha das inscrições e o que o encerramento pede.
- **FR-4736**: O porquê e o "ao confirmar" de cada passo MUST ficar recolhidos, num bloco só por
  fase; a frase curta MUST ficar à vista.

**Onde cada lista está (camada C)**

- **FR-4737**: Para quem vê a matriz, uma seção MUST mostrar, por Perfil, uma linha por lista com o
  andamento de cada fase por lista e o que há agora nela (os atos a praticar, um por fase; ou a
  primeira espera ou impedimento; ou "Concluída").
- **FR-4738**: A seção MUST trazer, recolhida, a matriz completa da `127` e os destinos do marco que o
  detalhe já oferece.
- **FR-4739**: Para quem não vê a matriz, a seção MUST NOT estar no HTML.

**Administração e histórico (camada D)**

- **FR-4740**: Uma seção, depois da operação, MUST reunir os documentos publicados (com o link "o que
  mudou" das Retificações), as consultas que o conjunto de ações da pessoa oferece, os avisos aos
  candidatos para quem os lê, quem atuou e a validação do conteúdo.
- **FR-4741**: Encerrar e Cancelar MUST ficar num bloco recolhido, com a advertência de
  irreversibilidade, e só para quem o conjunto de ações já os oferece.

**Os conceitos**

- **FR-4742**: Os nomes das fases, dos grupos, dos passos e as frases pedagógicas MUST morar num
  módulo único, marcado como provisório, de modo que trocá-los seja editar uma tabela.
- **FR-4743**: Cada passo MUST ter nome simples, termo do GPS, frase curta, porquê e "ao confirmar".

**Técnico**

- **FR-4744**: O número de consultas do Centro MUST NOT crescer com o número de inscrições, no molde da
  FR-4120 da `127`, e MUST ter teto fixado por teste.
- **FR-4745**: Estilo MUST ir para arquivo estático da tela; nada inline (a CSP).
- **FR-4746**: A página MUST NOT rolar na horizontal a 375 px; o mapa MUST virar lista vertical em tela
  estreita.
- **FR-4747**: A ordem do teclado MUST seguir a ordem visual: o mapa, depois as providências.
- **FR-4748**: Os sinais do andamento MUST vir com palavra; cor nunca é a única pista.

### Experiência (UX)

- **UX-314**: O mapa desenha o andamento como borda e sinal do cartão, e as providências como marcas
  no rodapé dele; uma legenda recolhida ("Como ler o mapa") explica as duas leituras lado a lado.
- **UX-315**: A fase consultada tem realce próprio (contorno e fundo), diferente do sinal de em curso e
  diferente das marcas de ação.
- **UX-316**: A ação destacada vem num bloco com o rótulo "Sua próxima ação", o nome da fase, o botão
  "Abrir a tela" e o "Por que esta".
- **UX-317**: Na tela larga, "O que fazer agora" e o detalhe da fase ficam lado a lado; abaixo de 1180
  px, os grupos do mapa empilham; a 390 px, as fases viram lista vertical.
- **UX-318**: Uma linha no topo diz que a página está em validação e leva ao detalhe atual.

### Decisões

#### D-001 — Rota própria, ao lado do detalhe

O Centro mora em `/gestao/editais/<id>/centro/`. O detalhe não muda, salvo o link de ida. É o que a
estratégia aprovada pede ("mantendo a experiência anterior acessível durante a validação"), e adia a
segunda decisão do estudo para a troca do padrão.

#### D-002 — Fora do andamento, o detalhe

Antes da publicação, no cancelado, ou com a derivação indisponível, a rota leva ao detalhe (302). Uma
página "antes da publicação" duplicaria a trilha que o detalhe já desenha bem até ali (decisão sobre a
trilha da `127`).

#### D-003 — A macrofase é apresentação

A fase é um rótulo sobre pontos que a derivação já conhece: não é coluna, estado persistido nem "a"
fase do Edital. É a primeira decisão do estudo, tomada pelo usuário, que revê a recusa de barra de
fases da `127` conservando a razão dela.

#### D-004 — A fase da providência pela natureza, e a Etapa pelo identificador

A providência de Etapa é localizada pelo identificador da Etapa que a derivação põe na chave, e não
pelo nome no texto: o protótipo comparava nomes, e dois Perfis com Etapas homônimas o enganariam.

#### D-005 — O destaque das três regras, provisório

As três regras da versão 2. A quarta decisão do estudo (o critério) segue pendente e é bloqueante para
a liberação geral; até lá, a regra vale e é dita na tela.

#### D-006 — Os conceitos num módulo, provisórios

Os nomes e textos da versão 2, num módulo único com o aviso de provisórios, à espera da terceira e da
sétima decisões do estudo.

#### D-007 — Quem vê o detalhe por lista é quem via a matriz

A regra atual da `127` (quem conduz ou audita). Mudá-la seria a sexta decisão do estudo.

#### D-008 — A paralela ao sorteio pelos marcos dos Perfis

A Etapa é paralela quando nenhum marco a lê: todos os Perfis com marco classificam por sorteio e
nenhum declara Etapa de habilitação. O protótipo olhava um Perfil só; com dois Perfis, um de
pontuação, a Etapa não é paralela.

#### D-009 — A fase consultada pela URL

A escolha vai no endereço (`?fase=`), sem script: o link do cartão é navegação comum, funciona sem
JavaScript e pode ser compartilhado. Uma fase desconhecida cai na regra fixa.

### Key Entities

- **Macrofase**: rótulo de apresentação para um conjunto de pontos da jornada, com andamento (quatro
  valores) e as providências que caem nela. Não é persistida.
- **Passo do roteiro**: um ponto da jornada na língua de quem conduz, com nome simples, termo do GPS,
  frases e andamento agregado das listas.
- **Destaque**: a providência da pessoa escolhida por uma das três regras, com a razão e os passos que
  ela destrava.
- **Conceito**: as frases de um tipo de passo (nome simples, termo, curta, porquê, ao confirmar).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1470**: Nos C06, C08 e C12, como a presidência, a 1440 × 900 px, "Onde estamos", o mapa e a
  primeira providência (ou a frase de que não há nenhuma) aparecem sem rolar.
- **SC-1471**: No C06, o destaque é "Fixar os participantes", com "Por que esta"; no C12, não há
  destaque, e a tela diz que o GPS não escolhe a ordem; no C08, o destaque da presidência é
  "Classificar a lista".
- **SC-1472**: No C12, com a Classificação consultada, o cartão dela leva `aria-current` e o texto
  "fase consultada", e o da Convocação diz *Em curso* sem `aria-current`.
- **SC-1473**: Em todos os cenários testados, a marca "sua" de cada fase existe se, e só se, há
  providência da pessoa nela; o andamento de cada fase é *Concluída* se, e só se, todas as células
  estão *Feito* ou *Não se aplica* com ao menos um *Feito*; e a soma das providências das fases é o
  total do nível 1.
- **SC-1474**: Com presidência, avaliação, Gestor e Publicador nos C06, C08 e C12, quem não vê a matriz
  não recebe tabela por lista no HTML, "Nenhuma ação é sua agora" aparece quando é o caso, e Encerrar e
  Cancelar só aparecem, recolhidos, para quem os tem.
- **SC-1475**: Um papel sem a permissão de um ato não recebe o link dele, e a tela real do ato o
  recusa.
- **SC-1476**: O número de consultas do Centro é o mesmo com 3 e com 30 inscrições, e fica abaixo do
  teto fixado.
- **SC-1477**: A página não rola na horizontal a 375 px e não registra violação de CSP, nos C06, C08 e
  C12.
- **SC-1478**: A suíte do detalhe atual passa sem alteração, e os dois links (ida e volta) existem.
- **SC-1479**: Os guardiões de acessibilidade, estáticos, vocabulário, inventário de negativas e
  citações passam.
- **SC-1480**: Um Edital sem providência, um prazo, um impedimento com quem resolve, uma Retificação em
  curso e dois Perfis no mesmo Edital são desenhados como descritos nos casos-limite.

## Assumptions

- Os cenários de treinamento da `134` são a base dos testes de papel e da conferência no navegador;
  dois Perfis e a seleção concluída vêm de fixture, porque nenhum cenário os tem.
- O texto do C08 sobre a lista PPP sem inscritos depende da `135`; enquanto ela não estiver na `main`,
  o teste confere só o título do destaque.
- O Publicador é a pessoa com o papel de publicar (`resultado:publicar` entre as permissões); o Gestor
  é o papel com cancelar e gerir a comissão; presidência e avaliação vêm do vínculo com a comissão.
- A página é da área de gestão, com o mesmo leiaute, o mesmo seletor de identidade e as mesmas folhas
  comuns do detalhe.
