# Feature Specification: A jornada pública do portal — encontrar, começar, preparar e acompanhar

**Feature Branch**: `claude/072-jornada-publica` — criada sobre `claude/auditoria-processo-seletivo-ux-ef5de7`
(PR 276, a auditoria que esta feature implementa em parte), que parte da `main` `b4a1abf4`.

**Created**: 2026-10-12

**Status**: Draft — escopo e decisões Q1 a Q9 recebidos do responsável pelo produto em 12/10/2026

**Input**: a alternativa A da [auditoria de UX e conversão da jornada pública](../../doc/auditoria-ux-conversao-2026-10-12.md),
com o escopo recortado pelo responsável pelo produto: *"spec baseada na alternativa A, focada nas três
tarefas da jornada pública; sem analytics, identidade visual, arquivo de seleções, novo tipo de
seleção ou quantitativos por modalidade; cenários demonstráveis para visitante novo, candidato
recorrente e participante que procura resultado ou prazo de recurso; a jornada completa de uma
identidade nova, sem substituir o preenchimento por fixture."*

---

## Por que esta feature existe

### O problema

O portal público tem três tarefas: **encontrar** uma oportunidade, **começar** a inscrição nela e
**acompanhar** o certame de que se participa. Uma quarta atravessa as duas primeiras: **preparar** —
saber, antes de se identificar, tudo o que será pedido.

A página da seleção já é orientada à decisão desde a `024`. A vitrine e a passagem pela
identificação, não. A auditoria de 12/10 mediu, no banco de demonstração:

- **Encontrar.** Em todo celular medido, o formulário de consulta ocupa de 203 a 537 px antes do
  primeiro cartão (a 320 px, até 592). Em telas de 667 px de altura ou menos, nenhuma oportunidade
  aparece antes da rolagem; em nenhuma tela de celular o convite do primeiro cartão aparece. E o
  título do cartão é o do **Processo** — "Processo Seletivo Simplificado 2026", idêntico nos três
  cartões —, com o título do Edital abaixo, em corpo menor: a hierarquia oposta à da página da
  seleção.
- **Começar.** No celular, o primeiro "Inscrever-se nesta vaga" fica entre 1.223 e 1.350 px. Quem o
  toca sem sessão cai numa tela "Entrar" que não diz para qual vaga; depois do código e dos dados
  volta à página da vaga sem destaque nem mensagem, e precisa tocar o mesmo botão de novo sem saber
  por quê.
- **Preparar.** O Edital que pede o Requerimento de Matrícula no ato da inscrição não o anuncia na
  página pública; a pessoa descobre dentro do rascunho que "não consegue enviar a inscrição sem ele".
  E "Seus dados" pede CPF sem dizer para quê.
- **Acompanhar.** O cartão de um Edital com resultado preliminar publicado e prazo de recurso aberto
  diz só "Inscrições encerradas em 02/09/2026". O prazo para exercer um direito está na página da
  seleção, e a vitrine o cala.

As evidências, o método e o script de medição estão na auditoria
([diagnóstico](../../doc/auditoria-ux-conversao-2026-10-12/diagnostico.md),
[medições](../../doc/auditoria-ux-conversao-2026-10-12/medicoes.json)).

### O que esta feature não reconstrói

A consulta no endereço e sem script, o cartão com um único link, a marca de situação por cor e
palavra, o prazo com tempo restante, o cadastro reserva lido como oferta, os documentos anunciados
antes da identificação, o Cronograma e o histórico públicos, o acesso sem senha, a área do candidato
e as páginas de resultado ficam como estão. Nada aqui muda conteúdo publicado, regra de elegibilidade,
regra de inscrição ou o que se grava.

### Decisões recebidas do responsável pelo produto (12/10/2026)

As nove questões da [priorização da auditoria](../../doc/auditoria-ux-conversao-2026-10-12/priorizacao.md#5-questões-para-o-responsável-pelo-produto):

| Questão | Decisão |
|---|---|
| Q1 — Instrumentação | Não incluir. Validar por percursos conduzidos. |
| Q2 — Identidade visual | Adiar para outro incremento. |
| Q3 — Encerradas e arquivo | Manter a organização atual. As encerradas não empurram as abertas na ordenação atual — as abertas vêm primeiro. |
| Q4 — Curso, cargo e bolsa | Estudar separadamente; nenhum campo novo agora. |
| Q5 — Campanhas | Página da seleção; âncora da vaga quando a campanha for específica de uma vaga. |
| Q6 — "Vaga" | Manter o termo, distinguindo na apresentação a denominação da quantidade. |
| Q7 — "Entrar" | Manter; acrescentar contexto nas telas de acesso. |
| Q8 — Quantidade por modalidade | Fora deste incremento. |
| Q9 — Próxima spec | Sim, com foco em encontrar, começar e acompanhar. |

## Clarifications

### Session 2026-10-12

- Q: Quando um Edital tem vários resultados vigentes e o prazo de recurso não é o mesmo para todos, como
  o cartão resume o prazo? → A: Opção A. Todos com recurso aberto e o mesmo término → o prazo uma vez.
  Só parte com recurso aberto, ou términos diferentes → "Recurso aberto para N de M resultados · o
  primeiro prazo termina em DD/MM às HHhMM", em que N conta os resultados vigentes com recurso aberto,
  M conta todos os resultados vigentes, e o primeiro término considera só os prazos abertos. Sem prazo
  aberto, nenhuma frase de prazo. Perfil, etapa e lista ficam na página da seleção.

## User Scenarios & Testing *(mandatory)*

Os cenários usam o banco de demonstração (`seed_demo`): o **Edital 01/2026**, aberto, com dois
Perfis — "Professor de Informática" (3 vagas imediatas e cadastro reserva, Campus Serra) e "Técnico de
Laboratório" (cadastro reserva sem vagas imediatas, Campus Vitória) — e Requerimento de Matrícula no
ato da inscrição; o **Edital 51/2026**, encerrado, com resultado preliminar publicado para uma lista e
prazo de recurso aberto; o **Edital 26/2026**, encerrado, por sorteio, sem resultado publicado.
Onde um cenário precisa de algo que o seed não produz, ele diz.

### User Story 1 — Quem chega pelo celular encontra uma oportunidade sem atravessar um formulário (Priority: P1)

Uma pessoa que nunca usou o portal abre `/selecoes/` no celular. Antes de rolar, ela precisa ver que
existe seleção aberta e de quê; o campo de busca continua à mão para quem já sabe o que procura, e os
demais filtros ficam a um toque. Cada cartão diz, primeiro, **qual Edital** — e logo abaixo, as vagas
de cada Perfil com a quantidade, e onde.

**Why this priority**: É a porta de entrada. Sem ela, o visitante que veio de uma divulgação geral vê
um formulário e o título repetido de um Processo antes de qualquer oportunidade.

**Independent Test**: Abrir a vitrine nas larguras e alturas de celular medidas pela auditoria e
conferir, pelo mesmo script de medição, o que cabe na primeira tela; ler os cartões do seed.

**Acceptance Scenarios**:

1. **Given** a vitrine sem consulta, numa tela de 375 × 667, **When** a página abre, **Then** o campo
   de busca e o título do Edital da primeira seleção aberta estão na primeira tela, e os filtros de
   situação, Perfil, unidade e ordenação estão recolhidos sob um controle identificado.
2. **Given** a vitrine com `?situacao=encerrado` no endereço, numa tela estreita, **When** a página
   abre, **Then** o grupo de filtros recolhidos aparece aberto, mostrando o filtro aplicado.
3. **Given** o cartão do Edital 01/2026, **When** a pessoa o lê, **Then** o título do cartão é o
   título do Edital; a linha seguinte diz "Professor de Informática — 3 vagas e cadastro reserva" e
   "Técnico de Laboratório — cadastro reserva", em forma que separa o nome do Perfil da quantidade;
   os lugares "Campus Serra" e "Campus Vitória" aparecem; o nome do Processo, o código e a unidade
   aparecem como dados de apoio, abaixo; e o número "01/2026" não aparece duas vezes no cartão.
4. **Given** a busca "Vitória", **When** a pessoa filtra, **Then** o Edital 01/2026 é encontrado pelo
   lugar de um dos seus Perfis.
5. **Given** a busca "enfermagem", sem resultado, **When** a página responde, **Then** uma única frase
   diz o que foi procurado e oferece o caminho para as seleções com inscrições abertas e para o
   catálogo inteiro.
6. **Given** a vitrine em tela larga (1280 px), **When** a página abre, **Then** a barra de consulta
   continua inteira e visível, como hoje.

---

### User Story 2 — Um visitante novo vai da vaga ao rascunho sem perder de vista o que escolheu (Priority: P1)

Uma pessoa sem identidade no sistema abre a página do Edital 01/2026 pelo celular — vinda de uma
campanha sobre a vaga de professor — e se inscreve. No alto da página ela vê o que a seleção oferece e
um atalho até as vagas. Ao tocar "Inscrever-se nesta vaga", cada tela da identificação diz para qual
vaga ela está se identificando; "Seus dados" diz por que o CPF é pedido; e, de volta à vaga, a página
mostra qual era e explica que falta confirmar.

**Why this priority**: É a passagem em que a decisão de participar se concretiza. A confirmação por
POST continua — ela impede que um endereço compartilhado crie inscrição em nome de quem só se
identificou —, e o que muda é que a tela passa a explicá-la.

**Independent Test**: Percorrer, com uma identidade nova, da página da seleção ao rascunho, passando
por e-mail, código, "Seus dados" **preenchido no formulário**, volta e confirmação — num teste de
aceitação que atravessa as telas pelo canal do candidato, e num percurso conduzido no navegador.

**Acceptance Scenarios**:

1. **Given** a página do Edital 01/2026 numa tela de 375 × 667, **When** ela abre, **Then** a primeira
   tela traz o resumo do que a seleção oferece — os dois Perfis, cada um com a quantidade — e uma ação
   que leva às vagas; cada Perfil do resumo leva à vaga correspondente.
2. **Given** a página aberta por `/selecoes/<edital>/#vaga-<perfil>`, **When** ela rola até a vaga,
   **Then** a vaga de destino se distingue das demais por mais de um meio além da cor.
3. **Given** uma pessoa sem sessão, **When** toca "Inscrever-se nesta vaga" no Perfil "Professor de
   Informática", **Then** a tela de acesso diz que ela está confirmando o e-mail para se inscrever em
   "Professor de Informática", do Edital 01/2026, e a do código repete essa identificação.
4. **Given** o código válido de um e-mail sem identidade, **When** a pessoa o confirma, **Then** "Seus
   dados" nomeia a vaga e diz para que nome e CPF serão usados; ela preenche nome e CPF no formulário e
   continua.
5. **Given** a volta à página da vaga depois de "Seus dados", **When** a página abre, **Then** a vaga
   escolhida está em destaque, e uma mensagem junto dela diz que a pessoa entrou e que tocar
   "Inscrever-se nesta vaga" abre a inscrição; ao tocar, o rascunho daquela vaga é aberto.
6. **Given** a mesma volta, **When** a pessoa recarrega a página, **Then** a mensagem não se repete.
7. **Given** um endereço de vaga com `?destino=` colado por terceiro, **When** a pessoa se identifica,
   **Then** nenhuma inscrição é aberta sem que ela toque "Inscrever-se nesta vaga".

---

### User Story 3 — Quem já tem identidade volta e se inscreve com o mesmo contexto (Priority: P2)

Uma candidata que já se inscreveu antes — e por isso já informou nome e CPF — abre outra seleção,
toca "Inscrever-se nesta vaga", confirma o e-mail e o código e volta à vaga sem passar por "Seus
dados". Com sessão aberta, o botão leva direto ao rascunho, como hoje.

**Why this priority**: É o caminho de quem acompanha várias seleções. Não pode regredir, e ganha o
mesmo contexto que o visitante novo.

**Independent Test**: Percorrer com identidade de núcleo cadastrado, sem sessão e com sessão.

**Acceptance Scenarios**:

1. **Given** uma identidade com nome e CPF, sem sessão, **When** a pessoa toca "Inscrever-se nesta
   vaga" e confirma e-mail e código, **Then** ela volta à vaga escolhida, em destaque e com a mensagem
   da User Story 2, sem passar por "Seus dados".
2. **Given** sessão aberta, **When** a pessoa toca "Inscrever-se nesta vaga", **Then** o rascunho é
   aberto diretamente, sem mensagem de volta.
3. **Given** uma identidade com rascunho já aberto naquela vaga, **When** a página da seleção abre,
   **Then** o convite continua sendo "Continuar inscrição", como hoje.

---

### User Story 4 — Antes de se identificar, a pessoa sabe tudo o que será pedido (Priority: P2)

Na página da seleção, além dos documentos de cada Perfil — que já são anunciados —, a pessoa vê que o
Edital pede o Requerimento de Matrícula no ato da inscrição, quando pede. Em "Seus dados", ela sabe
para que nome e CPF servem.

**Why this priority**: Descobrir uma exigência depois de se identificar é o defeito que a `009`
corrigiu para os documentos; o Requerimento ficou de fora.

**Independent Test**: Ler a página do Edital 01/2026 (pede na inscrição) e de um Edital que não pede,
ou pede só na convocação.

**Acceptance Scenarios**:

1. **Given** um Edital que pede o Requerimento de Matrícula no ato da inscrição, **When** a pessoa lê a
   seção de vagas, **Then** uma frase diz, antes do primeiro Perfil, que além dos documentos a inscrição
   pede o preenchimento do Requerimento de Matrícula.
2. **Given** um Edital que não pede o Requerimento, ou que o pede só na convocação, **When** a pessoa lê
   a seção de vagas, **Then** nenhuma frase sobre o Requerimento aparece.
3. **Given** "Seus dados", **When** a tela abre, **Then** ela diz para que nome e CPF são usados e que
   são pedidos uma única vez.

---

### User Story 5 — Quem participou acha, pela vitrine, o resultado e o prazo de recurso (Priority: P1)

Uma pessoa que se inscreveu no Edital 51/2026 abre a vitrine. O cartão dele diz que há resultado
publicado e até quando se pode recorrer, e o convite leva à seleção, onde estão os resultados por
Perfil, etapa e lista.

**Why this priority**: É prazo para exercer um direito. A página da seleção já o diz; a vitrine, onde a
pessoa procura primeiro, cala.

**Independent Test**: Ler os cartões do Edital 51/2026 (um resultado, prazo aberto) e do 26/2026 (sem
resultado). Os casos de vários resultados, de prazos diferentes e de prazo encerrado exigem dados que o
seed não produz e são cobertos por testes com cenário próprio.

**Acceptance Scenarios**:

1. **Given** o Edital 51/2026, com um resultado preliminar vigente e prazo de recurso aberto, **When** a
   pessoa lê o cartão, **Then** ele diz "Resultado preliminar publicado em 12/10/2026" e o prazo de
   recurso com data e hora, e o convite diz que leva aos resultados e ao prazo.
2. **Given** um Edital com três resultados vigentes em listas diferentes, só um deles com prazo aberto,
   **When** a pessoa lê o cartão, **Then** ele diz quantos resultados foram publicados e a data do mais
   recente, e "Recurso aberto para 1 de 3 resultados · o primeiro prazo termina em DD/MM às HHhMM" —
   **sem** uma frase de prazo que pareça valer para todos.
3. **Given** um Edital com dois resultados vigentes, ambos com recurso aberto mas com términos
   diferentes, **When** a pessoa lê o cartão, **Then** ele diz "Recurso aberto para 2 de 2 resultados ·
   o primeiro prazo termina em…", com o término mais próximo.
4. **Given** um Edital cujos resultados vigentes têm todos o mesmo prazo aberto, **When** a pessoa lê o
   cartão, **Then** o prazo é dito uma vez, sem qualificação.
5. **Given** um Edital com resultado vigente e prazo de recurso já encerrado, **When** a pessoa lê o
   cartão, **Then** o resultado é dito e nenhuma frase de prazo aparece.
6. **Given** um Edital cujo resultado preliminar foi sucedido pelo definitivo, **When** a pessoa lê o
   cartão, **Then** só o vigente conta — a publicação sucedida não entra em N, em M nem na data.
7. **Given** o Edital 26/2026, sem resultado publicado, **When** a pessoa lê o cartão, **Then** nenhuma
   frase de resultado ou de ausência de resultado aparece.
8. **Given** qualquer cartão com resultado, **When** a pessoa abre a seleção, **Then** a página diz, no
   mesmo instante de leitura, os mesmos resultados e prazos que o cartão resumiu.

---

### Edge Cases

- **Edital sem título próprio**: o título do cartão é o do Processo, como hoje; nenhum título vazio.
- **Título do Edital que já contém o número** (como "Edital 01/2026 — …"): o número não se repete na
  linha de apoio.
- **Mais de três Perfis**: o cartão nomeia três e diz quantos mais existem; um Edital de trinta polos
  não vira trinta linhas.
- **Perfil sem vagas imediatas e sem cadastro reserva**: o cartão diz o nome do Perfil sem inventar
  quantidade; nenhum "0 vagas" em destaque (a leitura da `024` para o zero continua valendo).
- **Perfis sem lugar declarado**: a linha de lugar não aparece; nenhuma frase de ausência.
- **Lugares repetidos entre Perfis**: cada lugar aparece uma vez.
- **Catálogo vazio**: a frase atual continua; não há formulário nem linha de contagem de abertas.
- **Nenhuma seleção aberta**: a linha de contagem diz que não há seleção com inscrições abertas agora,
  sem adjetivo.
- **Edital com Perfil que uma Retificação retirou, com resultado publicado**: o resultado conta no
  resumo do cartão, como conta na página (a `062` dá a ele o nome congelado).
- **Resultados de natureza diferente** (um preliminar e um definitivo vigentes): o cartão não atribui
  natureza ao conjunto.
- **Prazo de recurso que encerra entre o carregamento da vitrine e o da seleção**: cada página julga
  no seu instante; dentro de uma mesma página, um instante só.
- **Edital cancelado**: continua fora da vitrine; a página dele continua como está.
- **Destino que não é uma vaga** (a página do Edital, desde a `062`, ou nenhum): as telas de acesso não
  nomeiam vaga nenhuma, e a volta segue o caminho de hoje.
- **Destino de vaga de Edital que deixou de receber inscrição** entre o clique e a volta: a volta mostra
  a página da vaga como ela estiver, sem convite de inscrição — a mensagem não promete abrir inscrição.
- **Reconciliação de identidade** (e-mail com correspondência histórica, da `010`): a tela de
  reconciliação também nomeia a vaga quando o destino é uma vaga.
- **Sem script no navegador**: a busca, os filtros recolhidos, o atalho para as vagas, o destaque e a
  mensagem funcionam do mesmo jeito.
- **320 px de largura**: nenhuma rolagem lateral em nenhuma tela alterada.

## Requirements *(mandatory)*

Esta feature abre em **FR-1600** e **SC-600**. As specs 070 e 071, ainda não integradas, ocupam
faixas que terminam antes de 1.530 e de 570; o intervalo deixa folga para elas.

### Functional Requirements

#### Encontrar — a vitrine

- **FR-1600**: Em telas estreitas, a vitrine MUST mostrar o campo de busca sempre visível e MUST
  recolher os demais controles da consulta — unidade, situação, Perfil e ordenação, com o botão de
  aplicar — sob um único controle de abertura identificado por texto ("Mais filtros e ordenação").
- **FR-1601**: O grupo recolhido MUST abrir-se já na chegada quando algum dos controles recolhidos
  estiver aplicado na consulta, para que o filtro em vigor nunca fique escondido.
- **FR-1602**: Em telas largas, a barra de consulta MUST continuar inteira e visível, como hoje.
- **FR-1603**: O recolhimento MUST funcionar sem execução de script no navegador, e MUST preservar o
  que a consulta já garante: tudo no endereço, contagem do encontrado, caminho para limpar.
- **FR-1604**: O título de cada cartão — e o seu único link — MUST ser o título do Edital. Sem título de
  Edital, MUST ser o título do Processo.
- **FR-1605**: O título do Processo, o código do Processo, o número do Edital e a unidade MUST aparecer
  no cartão como dados de apoio, abaixo da oferta, com peso visual menor que o do título. A unidade
  MUST ser escrita pela sigla do registro de Unidades ("Cefor"), e não pela chave interna em caixa alta.
- **FR-1606**: Quando o título do Edital já contiver o número do Edital na forma `NN/AAAA`, o número
  MUST NOT ser repetido nos dados de apoio.
- **FR-1607**: O cartão MUST dizer a oferta **por Perfil**: o nome do Perfil e, separada dele, a
  quantidade — "N vaga(s)", "N vaga(s) e cadastro reserva" ou "cadastro reserva" quando não há vaga
  imediata e há reserva. Perfil sem vaga imediata e sem reserva MUST aparecer só pelo nome.
- **FR-1608**: O cartão MUST nomear no máximo três Perfis e, havendo mais, MUST dizer quantos mais
  existem. A soma das vagas de Perfis diferentes MUST NOT ser apresentada como número único.
- **FR-1609**: O cartão MUST dizer os lugares declarados pelos Perfis, cada lugar uma vez, no máximo
  três e "e mais N" além disso; sem lugar declarado, a linha MUST NOT existir.
- **FR-1610**: A busca textual da vitrine MUST alcançar também os lugares declarados pelos Perfis, além
  do que já alcança (título do Processo, título e número do Edital, unidade e nomes dos Perfis). Com
  busca ativa, os Perfis e os lugares que casam com o termo MUST vir primeiro no cartão, para que o
  limite de três da FR-1608 e da FR-1609 nunca esconda o que fez o cartão ser encontrado.
- **FR-1611**: O título da vitrine MUST ser "Processos seletivos", acompanhado da unidade quando o
  catálogo publicado for de uma unidade só; o título da aba do navegador MUST dizer o mesmo, e não
  "Seleções abertas".
- **FR-1612**: Abaixo do título, a vitrine MUST dizer quantas seleções estão com inscrições abertas
  agora — ou que não há nenhuma —, contadas pelo mesmo critério que forma o grupo "Inscrições
  abertas"; e o subtítulo MUST dizer o que a pessoa pode fazer na página, sem descrever a mecânica dela.
- **FR-1613**: Consulta sem resultado MUST ser dita numa frase só, que nomeia o que foi procurado e
  oferece o caminho para as seleções com inscrições abertas — quando houver alguma — e para o catálogo
  inteiro.
- **FR-1614**: Todos os cartões MUST trazer as mesmas informações nas mesmas posições, inclusive as
  novas desta feature, de modo que dois cartões continuem comparáveis sem releitura.

#### Começar — da seleção ao rascunho

- **FR-1615**: A página da seleção MUST trazer, no cabeçalho e antes do botão do Edital em PDF, o
  resumo do que a seleção oferece: cada Perfil com a quantidade, na forma da FR-1607, e cada um levando
  à vaga correspondente na página. Uma ação ao fim do resumo MUST levar à seção das vagas, com o texto
  "Ver vagas e inscrever-se" quando o Edital recebe inscrições e "Ver vagas" quando não recebe.
- **FR-1616**: Com mais de cinco Perfis, o resumo MUST nomear os cinco primeiros, dizer quantos mais
  existem e manter a ação para a seção das vagas.
- **FR-1617**: A vaga indicada no endereço da página — pela âncora da vaga, vinda da volta da
  identificação, de uma campanha ou de um compartilhamento — MUST se distinguir das demais por mais de
  um meio além da cor.
- **FR-1618**: O link "← Voltar aos resultados" MUST aparecer só quando a pessoa chegou por uma consulta
  da vitrine; sem consulta, o link MUST dizer "← Todas as seleções" e levar à vitrine sem filtro.
- **FR-1619**: Quando a identificação começa a caminho de uma vaga, a tela de acesso, a do código, a de
  reconciliação e "Seus dados" MUST nomear o Perfil e o Edital (número e título) a que a pessoa está se
  candidatando, e a tela de acesso MUST ter como título que ela está confirmando o e-mail para se
  inscrever. Sem destino de vaga, as telas MUST continuar como estão.
- **FR-1620**: O contexto da FR-1619 MUST derivar só do destino da identificação, e MUST ser idêntico
  exista ou não identidade para o e-mail informado — a equivalência de resposta da `010` (FR-020,
  FR-021) continua inteira.
- **FR-1621**: A tela do código MUST dizer onde procurar o código quando ele não chega (caixa de spam ou
  de promoções), junto do reenvio.
- **FR-1622**: Ao voltar da identificação para a página da vaga, a página MUST mostrar, junto da vaga
  escolhida, uma mensagem que diz que a pessoa entrou — com o e-mail com que entrou — e que tocar
  "Inscrever-se nesta vaga" abre a inscrição. A mensagem MUST aparecer uma única vez: recarregar a
  página não a repete.
- **FR-1623**: Se a vaga deixou de receber inscrição entre o clique e a volta, a mensagem MUST NOT
  convidar a abrir inscrição; a página mostra a vaga como ela estiver.
- **FR-1624**: Abrir o rascunho MUST continuar exigindo a confirmação explícita da pessoa na página da
  vaga, por envio de formulário. Nenhum destino de identificação MUST abrir inscrição sozinho.
- **FR-1625**: A confirmação de "Seus dados guardados" que hoje aparece fora de contexto, na tela da
  inscrição, MUST passar a fazer parte da mensagem de volta da FR-1622 quando a pessoa veio de "Seus
  dados" a caminho de uma vaga.

#### Preparar — o que será pedido

- **FR-1626**: Quando o Edital publicado pede o Requerimento de Matrícula no ato da inscrição, a seção
  das vagas MUST dizer, antes do primeiro Perfil, que além dos documentos a inscrição pede o
  preenchimento do Requerimento de Matrícula. Quando o Edital não o pede, ou o pede só na convocação, a
  frase MUST NOT existir.
- **FR-1627**: "Seus dados" MUST dizer para que nome e CPF são usados — identificar a pessoa nas
  inscrições e nos resultados — e que são pedidos uma única vez. O texto MUST ser validado por quem
  responde pela proteção de dados antes da publicação da feature.
- **FR-1628**: Os documentos anunciados por Perfil e o teto de inscrições por candidato MUST continuar
  anunciados como hoje, antes da identificação.

#### Acompanhar — resultado e prazo de recurso na vitrine

- **FR-1629**: O cartão de um Edital com resultado vigente publicado MUST dizer que há resultado
  publicado e a data da publicação mais recente: com um resultado vigente, "<natureza> publicado em
  DD/MM/AAAA"; com mais de um, quantos foram publicados e a data do mais recente.
- **FR-1630**: A natureza (preliminar ou definitivo) MUST ser dita no cartão só quando for a mesma para
  todos os resultados vigentes do Edital.
- **FR-1631**: Havendo prazo de recurso aberto para **todos** os resultados vigentes, e o mesmo prazo
  para todos, o cartão MUST dizer o prazo uma vez, com data e hora.
- **FR-1632**: Havendo prazo de recurso aberto para só parte dos resultados vigentes, ou términos
  diferentes entre os abertos, o cartão MUST dizer "Recurso aberto para N de M resultados · o primeiro
  prazo termina em DD/MM às HHhMM", em que N conta os resultados vigentes com recurso aberto, M conta
  todos os resultados vigentes, e o primeiro término é o mais próximo **entre os prazos abertos** — e
  MUST NOT escrever uma frase de prazo sem essa qualificação.
- **FR-1633**: Prazo de recurso encerrado MUST NOT aparecer no cartão. Edital sem resultado vigente MUST
  NOT ter frase de resultado nem de ausência de resultado.
- **FR-1634**: O convite do cartão MUST dizer para onde leva: aos resultados e ao prazo, quando há prazo
  aberto; aos resultados, quando há resultado sem prazo aberto; e o convite de hoje nos demais casos.
- **FR-1635**: O resumo do cartão MUST ser derivado das mesmas fontes e das mesmas regras de vigência e
  de prazo que a página da seleção usa, de modo que, num mesmo instante de leitura, cartão e página
  nunca discordem; dentro de uma página, todos os cartões MUST ser julgados no mesmo instante.
- **FR-1636**: O resumo do cartão MUST NOT anunciar fase, status agregado ou estado que nenhum ato
  registrou ("em andamento", "em análise", "concluído"): ele diz fatos datados.

#### Transversais

- **FR-1637**: Nenhum dado de navegação, clique, origem de visita ou percurso MUST ser registrado por
  esta feature.
- **FR-1638**: Nenhum texto novo desta feature MUST prometer aprovação, classificação, contratação,
  matrícula ou vaga, nem usar urgência que o prazo publicado não sustente. O vocabulário proibido que já
  vale para a área do candidato MUST passar a valer também para os textos novos da vitrine, da página
  da seleção e das telas de acesso.
- **FR-1639**: Toda tela alterada MUST continuar sem rolagem lateral de 320 a 1.440 px, operável por
  teclado, com foco visível, e com estado e prazo distinguíveis sem cor.
- **FR-1640**: A mensagem de volta (FR-1622) MUST ser anunciada a quem usa leitor de tela, e o controle
  de abertura dos filtros recolhidos (FR-1600) MUST expor o estado aberto ou fechado.

### Reconciliação com decisões anteriores

| Decisão anterior | Efeito desta feature |
|---|---|
| `024`, achado registrado sobre títulos repetidos ("conteúdo de quem elabora, não defeito de tela") | **Revisada** pela D-002: o conteúdo continua intocado; o que muda é a hierarquia do cartão. |
| `024`, FR-138 (o que a busca alcança) | **Estendida** pela FR-1610: o lugar passa a ser visto no cartão, e o que se vê é o que se busca. |
| `024`, FR-139 a FR-146a, a decisão 002 da `024` (consulta no endereço) e UX-017 | **Mantidas.** O recolhimento é de apresentação, sem script, e a consulta continua no endereço. |
| `024`, FR-144 (a volta preserva a consulta) | **Mantida.** Muda só o texto da volta quando não há consulta (FR-1618). |
| `024`, FR-136 e a decisão 007 da `024` (cadastro reserva como oferta) | **Mantidas**, e levadas ao cartão (FR-1607). |
| `024`, FR-137 (o convite anuncia a identificação) | **Mantida.** |
| `024`, FR-145, FR-147 a FR-149, UX-016, UX-019 | **Mantidas.** As informações novas ocupam posição fixa (FR-1614). |
| `024`, a decisão 008 da `024` e SC-047 (sem instrumentação) | **Mantidas** (FR-1637; Q1). |
| `024`, fora de escopo: renomear "Entrar"; identidade visual | **Mantidos** (Q7, Q2). |
| `009`, FR-014 (título do Edital na página) | **Estendida** ao cartão da vitrine (FR-1604). |
| `009`, convite por vaga e abertura por envio de formulário; `062`, a volta à vaga sem abrir rascunho | **Mantidos** (FR-1624); a tela passa a explicar a confirmação (FR-1622). |
| `009`, L4 da auditoria de UX (o convite abaixo da dobra, deixado como decisão de produto) | **Resolvido** pela FR-1615 sem escolher Perfil por ninguém. |
| `010`, FR-020 e FR-021 (resposta equivalente) | **Mantidas** (FR-1620). |
| `047`, a decisão 002 da `047` (nenhum status agregado) | **Mantida** (FR-1636). |
| `062`, FR-1155 (natureza e data na linha da lista, nunca no título da etapa ou do Perfil) | **Respeitada** no cartão pela FR-1630: a natureza só se generaliza quando é a de todos. |
| `062`, FR-1160 a FR-1162 (o caminho para a própria situação) | **Mantidas.** |
| `055`, FR-1013 (a consulta da Vitrine como modelo da gestão) | **Mantida.** A barra em tela larga não muda; o recolhimento vale só para tela estreita. |

### Key Entities

Nenhuma entidade nova, nenhum campo novo. A feature lê o que já existe:

- **Versão consolidada vigente do Edital**: título, número, Perfis (nome, vagas imediatas, tipo de
  reserva, lugar), período, e a declaração do Requerimento de Matrícula com o momento em que é pedido.
- **Unidade registrada**: a sigla que a vitrine passa a usar.
- **Publicação de resultado vigente**: natureza, data de publicação, Perfil, etapa, lista e a janela de
  recurso calculada pela regra que a página da seleção já usa.
- **Destino da identificação**: a vaga ou a página a que a pessoa volta depois de se identificar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-600**: Na vitrine do banco de demonstração, nas telas de 375 × 667, 360 × 800, 375 × 812 e
  390 × 844, o campo de busca e o título do Edital da primeira seleção aberta estão inteiros na primeira
  tela — medidos pelo script da auditoria. Em 320 × 568, o campo de busca está.
- **SC-601**: Na página da seleção do Edital 01/2026, nas mesmas telas de celular, o resumo da oferta e
  a ação que leva às vagas estão inteiros na primeira tela.
- **SC-602**: Nas 4 telas da identificação a caminho de uma vaga (acesso, código, reconciliação e "Seus
  dados"), o nome do Perfil e o número do Edital escolhidos aparecem em 4 de 4; sem destino de vaga, em
  0 de 4.
- **SC-603**: Num teste de aceitação que atravessa as telas pelo canal do candidato, uma identidade
  **nova** vai da página da seleção ao rascunho da vaga escolhida passando por e-mail, código, "Seus
  dados" preenchido no formulário, volta com mensagem e confirmação — e nenhum rascunho existe antes da
  confirmação.
- **SC-604**: Em cenários com 1, 3 e 5 resultados vigentes — com prazos todos iguais, parcialmente
  abertos, diferentes entre si e encerrados —, 100% dos cartões dizem o mesmo que a página da seleção no
  mesmo instante, e 0 cartões escrevem uma frase de prazo sem qualificação quando o prazo não vale para
  todos os resultados vigentes.
- **SC-605**: Um percurso conduzido com ao menos cinco pessoas de fora do projeto, no celular, cobrindo
  as quatro tarefas — encontrar, começar, preparar e acompanhar —, é realizado e registrado antes da
  publicação da feature, com o acerto e a hesitação de cada tarefa; ao menos quatro das cinco concluem
  cada tarefa sem ajuda.
- **SC-606**: Zero registros novos de navegação, clique ou origem, conferidos pela ausência de qualquer
  gravação nova nas telas alteradas.
- **SC-607**: Nenhuma tela alterada tem rolagem lateral em 320, 360, 375, 390, 768, 1280 e 1440 px.

## Decisões

### D-001 — A vitrine serve a três tarefas, e "preparar" atravessa duas delas

Encontrar, começar e acompanhar têm o mesmo peso nesta feature; otimizar só a conversão deixaria a
terceira em segundo plano, e é nela que estão prazos para exercer direitos. "Preparar" não é uma tela:
é o que as páginas de encontrar e começar dizem antes da identificação.

### D-002 — O título do cartão é o do Edital, e isto revisa um achado registrado da 024

A `024` viu os títulos repetidos e os atribuiu ao conteúdo de quem elabora, garantindo que número e
unidade continuassem distinguindo os cartões. Eles distinguem, mas em corpo de metadado, abaixo de um
título idêntico. A página da seleção já resolveu o mesmo problema pondo o título do Edital no alto
(`009`, FR-014). O cartão passa a fazer o mesmo; nenhum conteúdo publicado muda.

### D-003 — Busca à vista, filtros recolhidos, e só em tela estreita

A busca é o que serve na primeira tela a quem já sabe o que procura, e por isso não se recolhe. Os
demais controles somem atrás de um controle nativo de abertura, que funciona sem script e se abre
sozinho quando há filtro aplicado — escondê-lo apagaria a explicação da lista que a pessoa está
vendo. Em tela larga a barra ocupa uma linha só e é o modelo da gestão; recolhê-la ali não ganharia
nada.

### D-004 — Como resumir vários resultados e prazos num cartão

Um Edital pode ter vários Perfis, etapas e listas, cada lista com a sua cadeia, sua natureza e seu
prazo. O cartão os resume pela regra mais estreita que não faz um prazo de uma lista parecer valer
para todas:

1. **Resultado:** um vigente → a natureza e a data; vários → quantos e a data do mais recente; a
   natureza só quando é a de todos (FR-1629, FR-1630).
2. **Prazo:** aberto e com o mesmo término para todos os vigentes → dito uma vez; só parte aberta, ou
   términos diferentes → "Recurso aberto para N de M resultados · o primeiro prazo termina em…", com N
   os vigentes de prazo aberto, M todos os vigentes e o primeiro término só entre os abertos; nenhum
   aberto → nada (FR-1631 a FR-1633). Confirmado pelo responsável pelo produto em 12/10.
3. **Nunca** uma frase de prazo sem escopo quando o prazo não é de todos.

O nome de Perfil e lista fica na página da seleção, onde a árvore Perfil → etapa → lista da `062` já
o diz; trazê-lo para o cartão faria a vitrine crescer com o número de listas.

### D-005 — A identificação carrega a vaga, e a confirmação continua

O contexto vem do destino da identificação, e não do e-mail: por isso é idêntico para quem existe e
para quem não existe. A confirmação por formulário na página da vaga continua sendo a garantia de que
um endereço compartilhado não cria inscrição; o que muda é a tela dizer isso.

### D-006 — O Requerimento é anunciado só quando é pedido na inscrição

"Preparar" é o que se precisa para se inscrever. O Requerimento pedido na convocação não é exigido na
inscrição, e anunciá-lo na página pública faria a pessoa preparar o que talvez nunca lhe seja pedido.

### D-007 — Validação por percurso conduzido, sem instrumentação

Compreensão e conclusão de tarefa se verificam com pessoas, sem registrar navegação (Q1). Contar
rascunhos e envios mede a conclusão do que foi iniciado, e não conversão; nenhum critério desta
feature depende disso.

## O que esta feature não cobre, deliberadamente

- **Instrumentação** de qualquer espécie (Q1).
- **Identidade visual**, rodapé, favicon, assinatura institucional, prévia de compartilhamento (Q2; a
  auditoria os põe depois, conforme contribuição demonstrável).
- **Arquivo de seleções**, faixas "Acompanhe" e "Anteriores", cartão compacto de encerradas (Q3; e o
  cartão compacto contrariaria a UX-016).
- **Tipo da seleção** (curso, cargo, bolsa) e rótulos condicionais (Q4 — estudo separado).
- **Quantidade de vagas por modalidade** na página pública (Q8).
- **Sorteio e próximo Evento no cartão**: a página da seleção já os diz; o cartão resume só resultado e
  prazo de recurso.
- **Convocação**: não é pública; continua na área do candidato e no caminho "Entrar para ver minha
  situação" (062).
- **Endereço legível** e **página de Processo**.
- **Contraste do contorno de campo** (achado C-17 da auditoria): o token é compartilhado com a gestão e
  merece tratamento próprio.
- **Mudança no formulário da inscrição**, na revisão, no comprovante e na área do candidato.

## Assumptions

- O catálogo continua na ordem de dezenas de seleções simultâneas, como a `024` assumiu. O resumo de
  resultados não pode ser lido **uma consulta por cartão**: a leitura é feita de uma vez para os
  Editais da página. O processamento cresce com os dados lidos, e isso é aceitável; o que se evita é
  o número de consultas crescer com o número de cartões.
- "Tela estreita" e "tela larga" seguem o ponto em que a barra de consulta hoje deixa de caber numa
  linha; o plano fixa o valor.
- Os números do SC-600 e do SC-601 são do conteúdo do seed: servem para comparar antes e depois no
  mesmo banco, com o script versionado na auditoria.
- O limite de quatro em cinco do SC-605 é o ponto de partida proposto; o responsável pelo produto pode
  ajustá-lo antes do percurso.
- No percurso conduzido, o CPF de "Seus dados" é digitado pela própria pessoa participante; o agente
  que verifica a feature não digita CPF em formulário, e a parte automática da jornada (SC-603) usa os
  valores de teste do repositório através do formulário, e não por gravação direta.
- O texto de finalidade de "Seus dados" (FR-1627) depende de validação por quem responde pela proteção
  de dados; sem ela, a feature não se publica.
- Os testes que hoje afirmam textos da vitrine, da seleção e do acesso localizam compromissos; a
  reconciliação acima diz quais se mantêm, e os que mudam mudam junto com o texto.
