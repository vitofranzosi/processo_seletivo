# Feature Specification: A providência chega ao ato, e o ato volta ao Centro

**Feature Branch**: `claude/139-chegada-e-volta-2ea891`, sobre a `main` em `4ae78556`

**Created**: 2026-11-10

**Status**: Draft.

**Nenhuma regra de domínio nova.** Esta spec muda **para onde** um link leva dentro da tela de
destino, e acrescenta links a um bloco que já existe. Não há migration, rota, permissão, regra de
disponibilidade nem regra de autorização nova, e a derivação do andamento continua escolhendo a
mesma providência.

**Input**: *"Chegada ao ato e volta ao Centro (G1 e G2 do estudo de continuidade operacional). G2: a
URL da providência ganha um fragmento que leva ao lugar do ato na tela de destino — no sorteio, o
recorte da lista, a ocorrência para a semente, os recortes para o que é do marco; na convocação, as
chamadas para conferir documentos e a chamada da pessoa para o desfecho, e as seções que a tela já
tem para os demais atos; um id por recorte na tela do sorteio; as rotas não mudam; duas listas
juntadas numa providência chegam à seção comum. G1: o bloco 'Próximo nesta lista' das seis telas
ganha 'Voltar ao Centro de Controle do Edital' e cada item de 'Ainda neste marco' vira link quando é
da pessoa e tem URL. Não muda qual providência a derivação escolhe nem regra de disponibilidade; não
mexe na migalha nem acrescenta a frase sobre a semente; CSP sem inline."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil setecentos e sessenta a quatro mil setecentos e setenta e
>   nove;
> - os critérios de mil quatrocentos e noventa a mil quatrocentos e noventa e nove;
> - os requisitos de experiência de trezentos e dezenove a trezentos e vinte e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`. A faixa é a que a sessão
> paralela da `140` deixou para esta, nas notas compartilhadas das duas: a `140` tomou do requisito
> quatro mil e oitocentos em diante, e os requisitos de experiência de trezentos e trinta em diante;
> os de experiência desta ficam dentro da reserva da `136`, que não os gastou.
>
> O teto foi medido em 10/11/2026, nas `specs/` de todas as worktrees desta máquina e de todas as
> branches remotas: requisito quatro mil setecentos e quarenta e oito, critério mil quatrocentos e
> oitenta e UX-318, todos da `136`. A `136` reservou até o requisito quatro mil setecentos e
> cinquenta e nove e o critério mil quatrocentos e oitenta e nove, e os requisitos e critérios
> desta faixa começam depois da reserva. A `137` e a `138` estão reservadas pelo plano do Centro de
> Controle, sem pasta.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-4090 da `127`"); decisão de outra feature ou do estudo, pelo assunto ("a segunda decisão em
> aberto do estudo do Centro"), nunca pelo identificador.
>
> **Origem.** O
> [estudo de continuidade operacional do GPS, de 10/11/2026](../../doc/estudo-continuidade-operacional-2026-11-10/README.md)
> (PR #445): o inventário de melhorias (`03-inventario-de-melhorias.md`, M-01, M-02, M-07 e M-15), o
> plano de evolução (`05-plano-de-evolucao.md`, grupos G1 e G2) e os protótipos (`04-prototipos.md`,
> com as transformações em `prototipo/transformacoes/`), que mostram o "depois" sobre o HTML real. O
> protótipo é referência de comportamento, e não código a copiar.

## Por que esta feature existe

O estudo percorreu as jornadas do Centro de Controle do Edital (`136`) até as telas reais dos atos, e
de volta. O estado se mantém coerente; **a passagem se rompe** em duas pontas:

1. **Na ida, a providência leva ao topo da tela, e o ato fica longe.** "Fixar os participantes —
   Ampla" abre o sorteio no alto, e o botão de congelar está a 1.681 px, abaixo da ocorrência e do
   método. "Conferir os documentos" abre a convocação no alto, e as chamadas estão a 2.151 px. O
   parâmetro `?lista=` que a providência leva para o sorteio não rola a tela: o sorteio mostra todos
   os recortes do marco, e a lista escolhida é só mais um deles.
2. **Na volta, o bloco do próximo passo não volta.** Depois de um ato, a `127` mostra o "Próximo
   nesta lista" e o "Ainda neste marco" (a FR-4090 da `127`). A pessoa entende o resultado e o que
   vem a seguir, mas o ponto de onde partiu — o Centro — está a dois cliques, pela migalha e pelo
   detalhe. E o "Ainda neste marco" diz o que falta nas outras listas **em texto**, sem link, mesmo
   quando o ato é da própria pessoa.

As duas pontas são a mesma passagem, e as duas se resolvem com os mecanismos que já existem: o
endereço que a derivação já monta, os ids que as telas já têm, e o bloco que já aparece depois de
cada ato.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- o fragmento no endereço das providências do sorteio e da convocação (M-02);
- um id por recorte na tela do sorteio, o único alvo que faltava;
- o retorno ao Centro no bloco do próximo passo, depois de um ato (M-01);
- o link em cada item de "Ainda neste marco" que é da pessoa e tem endereço (M-07).

**Fica fora:**
- **qual** providência a derivação escolhe, em qualquer tela, e qualquer regra de disponibilidade —
  a escolha continua sendo a da `127`;
- a migalha de navegação: o lugar do Centro nela é a segunda decisão em aberto do estudo do Centro;
- a frase sobre fixar todas as listas antes de observar a semente: é a quinta decisão em aberto do
  estudo de continuidade, e é do usuário;
- a frase de sucesso do sorteio que diz "Falta publicar a classificação" sem dizer com quem (M-15) —
  ver D-003;
- as demais melhorias do estudo (G3 a G8), inclusive o "Próximo para esta pessoa" na tela dos
  documentos (M-08) e o "Voltar à convocação" dela;
- os achados funcionais F-1 a F-5 do estudo, que têm investigação própria.

## Clarifications

Nenhuma pergunta aberta. As escolhas que esta spec faz por conta própria estão em *Decisões* e em
*Assumptions*.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A providência do sorteio chega ao recorte da lista (Priority: P1)

Quem conduz abre o Centro no C06 (sorteio por fazer, duas listas) e clica em "Fixar os
participantes". Hoje a tela abre no topo, e o botão está a 1.681 px. Depois desta spec, a tela abre
nos recortes — ou no recorte da lista, quando a providência é de uma lista só —, e o botão está na
primeira dobra.

**Why this priority**: é a passagem mais longa medida pelo estudo, e o primeiro ato irreversível da
jornada do sorteio.

**Independent Test**: no C06, a 1440 × 900, o link "Abrir a tela" do Centro e o link da providência
de uma lista levam o título do recorte para dentro da primeira tela.

**Acceptance Scenarios**:

1. **Given** um marco por sorteio com uma lista por congelar, **When** a pessoa segue a providência
   dessa lista, **Then** a tela do sorteio abre com o recorte dessa lista no alto.
2. **Given** duas listas por congelar no mesmo marco, juntadas numa providência só, **When** a pessoa
   a segue, **Then** a tela abre nos recortes, e não no primeiro deles.
3. **Given** a semente por obter, **When** a pessoa segue a providência, **Then** a tela abre na
   ocorrência da fonte.
4. **Given** uma lista com a relação congelada e o sorteio por realizar, **When** a pessoa segue a
   providência, **Then** a tela abre no recorte dessa lista, onde está o botão do sorteio.

---

### User Story 2 — A providência da convocação chega às chamadas (Priority: P1)

No C12, quem confere documentos clica em "Conferir os documentos de 1 convocação". Hoje a
convocação abre no topo, e as chamadas estão a 2.151 px. Depois, abre nas chamadas praticadas. E
quando a convocação está pronta para o desfecho, "Registrar o desfecho" abre na chamada da pessoa,
onde está o formulário.

**Why this priority**: a convocação é a tela mais longa do GPS (3.500 px), e conferir e decidir são
os atos que se repetem por pessoa.

**Independent Test**: no C12, o link da providência de conferir leva o título "Chamadas praticadas"
para dentro da primeira tela; com uma chamada pronta para decidir, o da providência do desfecho leva
o título dessa chamada.

**Acceptance Scenarios**:

1. **Given** chamadas com documento a conferir, **When** a pessoa segue a providência de conferir,
   **Then** a convocação abre nas chamadas praticadas.
2. **Given** uma ou mais chamadas prontas para o desfecho, **When** a pessoa segue a providência,
   **Then** a convocação abre na **primeira** delas, na ordem em que a tela as lista.
3. **Given** titulares a convocar, comunicações a emitir, convocações vencidas ou vaga a ocupar pela
   fila, **When** a pessoa segue a providência, **Then** a convocação abre na seção que a tela já tem
   para esse ato.

---

### User Story 3 — Depois do ato, a volta ao Centro e o próximo alcançável (Priority: P1)

Quem conduz congela a relação da Ampla no C06. A tela confirma, diz o próximo nesta lista e, em
"Ainda neste marco", que a PPP ainda tem a relação por congelar. Hoje a PPP é texto, e voltar ao
Centro custa dois cliques. Depois, "PPP — congelar a relação" é link para o recorte da PPP, e o
bloco termina em "Voltar ao Centro de Controle do Edital".

**Why this priority**: é a volta da mesma passagem; sem ela, a ida melhora e a jornada continua
partida.

**Independent Test**: no C06, depois de congelar a Ampla, o bloco tem o link da PPP e o retorno ao
Centro; no C12, depois de conferir um documento, o bloco tem o retorno ao Centro.

**Acceptance Scenarios**:

1. **Given** um ato praticado numa das seis telas que mostram o bloco, **When** a resposta chega,
   **Then** o bloco termina em "Voltar ao Centro de Controle do Edital", que leva ao Centro deste
   Edital.
2. **Given** a tela aberta sem ato, **When** a pessoa a lê, **Then** nem o bloco nem o retorno
   aparecem.
3. **Given** um item de "Ainda neste marco" que é da pessoa e tem endereço, **When** o bloco aparece,
   **Then** o item é link para esse endereço, com o fragmento da US1 e da US2.
4. **Given** um item que é de outro papel, que espera ou que está impedido, **When** o bloco
   aparece, **Then** ele continua texto, como hoje.

### Edge Cases

- **Alvo ausente na tela de destino.** Se a seção do fragmento não estiver na tela — porque o estado
  mudou entre a leitura do Centro e o clique —, o navegador abre a tela no topo, como hoje. Nenhuma
  falha, nenhum aviso.
- **Quem não tem consulta.** A providência sem endereço continua sem endereço: o fragmento não cria
  link onde não havia.
- **A Ampla sem identificador de lista.** O recorte da ampla concorrência tem um id próprio, que não
  colide com o de nenhuma lista.
- **A tela ordenada por documentos.** A convocação aberta com `?ordem=documentos` reordena as
  chamadas; a providência nunca leva esse parâmetro, e a contagem da chamada segue a ordem padrão.
- **Duas listas na mesma tela com âncoras diferentes.** Juntadas numa providência (o caminho comum
  da `127`), chegam à seção que reúne os recortes, ou à que reúne as chamadas; com seções diferentes
  e sem seção comum, à tela sem fragmento.
- **O bloco sem andamento.** Quando a derivação não tem o que dizer, o bloco não aparece, e o retorno
  também não.

## Requirements *(mandatory)*

### Functional Requirements

**A providência chega ao ato (M-02)**

- **FR-4760**: O endereço da providência da relação e do sorteio de uma lista, num marco por sorteio,
  leva ao recorte dessa lista na tela do sorteio. A rota e os parâmetros continuam os de hoje.
- **FR-4761**: O endereço da providência da semente leva à ocorrência da fonte, na tela do sorteio.
- **FR-4762**: Cada recorte da tela do sorteio tem um identificador estável, derivado da lista, e o da
  ampla concorrência é próprio. É o mesmo identificador que a FR-4760 usa, de uma única fonte.
- **FR-4763**: O endereço da providência de conferir documentos leva às chamadas praticadas, na tela
  da convocação.
- **FR-4764**: O endereço da providência do desfecho leva à primeira chamada pronta para o desfecho,
  na ordem padrão da tela da convocação; sem como determiná-la, às chamadas praticadas.
- **FR-4765**: Os endereços das providências de convocar os titulares, emitir as comunicações ou
  registrar a publicação, registrar o não atendimento das vencidas e chamar a próxima da fila levam à
  seção que a tela da convocação já tem para cada um; o da resposta que se aguarda, às chamadas.
- **FR-4766**: Duas providências da mesma tela juntadas numa só (o caminho comum da `127`) levam à
  seção que reúne as âncoras de ambas; sem seção comum, à tela sem fragmento.
- **FR-4767**: A situação, o ato, o responsável, a razão e a ordem de toda providência continuam os
  mesmos; muda só o fragmento do endereço.

**Depois do ato (M-01 e M-07)**

- **FR-4768**: O bloco do próximo passo, nas seis telas que o mostram (sorteio, ordem, corte,
  ocupação, convocação e documentos da convocação), termina num link "Voltar ao Centro de Controle do
  Edital", que leva ao Centro deste Edital. Ele aparece só quando o bloco aparece, isto é, depois de
  um ato.
- **FR-4769**: Cada item de "Ainda neste marco" que é da pessoa (a regra "sua" do andamento) e tem
  endereço é link para esse endereço. Os demais continuam texto, com a mesma frase de hoje.
- **FR-4770**: A frase do bloco — o próximo desta lista, os itens das outras listas e a ordem deles —
  continua a mesma; muda só o que vira link e a linha do retorno.

**Restrições**

- **FR-4771**: Nada desta spec usa estilo ou script escrito no template; o que for estilo novo vai
  para a folha da gestão.

### Requisitos de experiência

- **UX-319**: A 1440 × 900, a providência do sorteio e a de conferir documentos, seguidas a partir do
  Centro, deixam o alvo — o título do recorte ou o das chamadas — dentro da primeira tela.
- **UX-320**: O retorno ao Centro é um link de texto, abaixo do bloco, e não um botão nem um painel:
  o bloco continua sendo o que diz o próximo, e o retorno é a saída.

### Key Entities

- **Providência**: a célula do andamento em aberto, com o seu endereço. Ganha um fragmento; nenhum
  campo novo.
- **Âncora do recorte**: o identificador de um recorte na tela do sorteio, derivado da lista.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1490**: No C06, a 1440 × 900, a distância entre o topo da janela e o botão de congelar, depois
  de seguir a providência a partir do Centro, cai de 1.681 px para dentro da primeira tela (menos de
  900 px).
- **SC-1491**: No C12, a 1440 × 900, seguir "Conferir os documentos" deixa o título "Chamadas
  praticadas" dentro da primeira tela (antes, a 2.151 px).
- **SC-1492**: Nas seis telas, depois de um ato, voltar ao Centro custa **um** clique (antes, dois).
- **SC-1493**: Nenhuma providência muda de situação, ato, responsável ou ordem, em todos os cenários
  de treinamento: a comparação das providências antes e depois, sem o fragmento, é idêntica.
- **SC-1494**: Nenhuma rota nova, nenhuma linha nova no inventário de negativas, nenhuma violação de
  CSP.

## Assumptions

- O navegador rola até o elemento do fragmento ao abrir a tela; nenhum script é preciso.
- A ordem padrão das chamadas na tela da convocação é a da leitura do recorte que a derivação já faz;
  é por isso que o número da chamada sai da mesma leitura.
- Quem vê o bloco do próximo passo alcança o Centro: a porta do Centro é o escopo do Edital, a mesma
  das seis telas; e, sem andamento, o Centro leva ao detalhe, e o bloco nem aparece.
- O texto "Voltar ao Centro de Controle do Edital" é o do protótipo, e acompanha os textos
  provisórios do Centro.

## Compatibilidade com regras anteriores

- **`127`**: o bloco do próximo passo e a derivação são os dela; esta spec só acrescenta links. O
  caminho comum de duas listas juntadas (item 15 da revisão da `127`) continua, com o fragmento.
- **`136`**: o Centro não muda; os seus links passam a chegar ao ato.
- **Inventário de negativas (`033`)**: nenhuma rota nova, nenhuma recusa nova.

## Decisões

### D-001 — O fragmento, e não um parâmetro que a tela leia

A tela do sorteio poderia ler `?lista=` e rolar até o recorte, com script. O fragmento faz o mesmo
sem script, sem mudar a view e sem passar pela CSP, e é o mecanismo que o navegador já tem. O
`?lista=` continua no endereço, porque a convocação o lê e o caminho comum da `127` o compara.

### D-002 — A semente leva à ocorrência, e não aos recortes

O pedido inicial falava dos recortes para o que é do marco. A semente é do marco, mas o ato dela —
observar — está na seção da ocorrência, e o protótipo a levava para lá. Levar aos recortes poria a
pessoa a 600 px do botão, de novo. O que é do marco e não tem seção própria — a semente impedida —
vai aos recortes.

### D-003 — M-15 fica fora

A frase de sucesso do sorteio diz "Falta publicar a classificação" sem dizer com quem; o bloco do
próximo passo, logo abaixo, diz "publicar a classificação, com quem publica resultado". Repetir o
papel na frase de sucesso duplicaria a informação na mesma dobra — o padrão que o estudo registrou
como M-23 —, e tirá-la mudaria a confirmação do próprio ato, que não é o bloco. Não coube
naturalmente; fica registrado para o G4, que reorganiza a tela do sorteio.

### D-004 — O retorno vem dos dados do bloco, e não do template

O endereço do Centro sai da mesma função que monta o bloco, e não de cada uma das seis telas. Uma
tela que passasse a mostrar o bloco ganharia o retorno sem lembrar dele, e o retorno nunca aparece
sem o bloco.
