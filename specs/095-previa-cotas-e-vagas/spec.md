# Feature Specification: Prévia interativa da classificação — fatia 2: recortes, concomitância e ocupação das vagas

**Feature Branch**: `claude/095-previa-cotas-e-vagas`, sobre a `main` em `e7e22b89`

**Created**: 2026-10-20

**Status**: Especificada — spec, plan, tasks e protótipo de cálculo no PR; implementação não iniciada
e não autorizada. Depende da interface da fatia 1 (`094`), que também não está autorizada. O merge é do
usuário.

**Input**: decisão do usuário de 19/10/2026, registrada na decisão 008 da `094`: as cotas ficaram fora
da fatia 1 e são a fatia 2 do mesmo produto — ampla como universo inteiro, Modalidades reservadas
(PPI e PcD nos Editais da amostra), cada uma com a sua ordem, concorrência concomitante, que vale
sempre e não se configura, e ocupação das vagas além do aviso da fatia 1, com reversão declarada,
cuja ausência significa que não reverte.

> **Faixa de identificadores.** Esta spec abre em **FR-2300** e **SC-870**. A `094` (PR #316, aberto)
> usa de 2200 a 2255 na faixa de requisitos e de 840 a 853 na de critérios — sem o prefixo aqui,
> porque ela ainda não está na `main` e a varredura de citações não a vê. O intervalo entre o teto
> dela e o começo desta é folga deliberada: a `094` já cresceu duas vezes por rodada de UX. Nenhuma
> branch remota nem worktree local usava `095` nem número acima desses, conferido em `git ls-tree` e
> `git grep` de todas as branches e em `specs/` de todas as worktrees em 20/10/2026.
>
> **Como esta spec cita a `094`.** Pelo número sem prefixo ("o requisito 2240 da `094`", "a decisão
> 013 da `094`"), pela mesma razão. Quando o #316 entrar na `main`, as citações podem ganhar o prefixo
> sem mudar de sentido.

---

## Por que esta feature existe

**A fatia 1 mostra uma ordem só, e o Edital com reserva tem uma por recorte.** Desde a `034`, todo
marco por pontuação em Perfil com Modalidade reservada emite uma ordem da ampla concorrência — o
universo inteiro, autodeclarados inclusive — e uma ordem de cada Modalidade reservada, só com os
autodeclarados nela (`FR-490`, `FR-492`, `FR-493` da `034`). Cada recorte tem corte próprio, e a
ocupação de cada um depende da ampla: quem ocupa vaga pela ampla não é computado no preenchimento da
reservada (`FR-252` da `016`). A prévia da fatia 1 calcula só a ampla, e diz que não simula o resto.

**O que o elaborador não prevê é a interação entre as três regras, e nenhuma delas é campo do
cartão.** A medição de 20/10 contra o motor oficial ([research.md](research.md), R-001) mostrou, num
Perfil de 10 vagas na ampla, 3 na PPI e 2 na PcD, alvo do quadro e nenhum suplente:

1. **A faixa da reservada é calculada sobre a ordem inteira da reservada**, incluindo quem já ocupa
   pela ampla. Com dois autodeclarados PPI entre os dez primeiros da ampla, a faixa da PPI — três
   posições — alcança esses dois e mais um. A apuração da PPI tira os dois, e restam **duas vagas
   reservadas sem ocupante**, embora haja um quarto autodeclarado classificado, fora da faixa.
2. **A reversão por saldo cede essas duas vagas à ampla na primeira apuração**, antes de qualquer
   faixa seguinte alcançar o quarto autodeclarado.
3. **A reversão por esgotamento nunca cede**, porque a regra de hoje considera que "há quem ocupar"
   enquanto a ordem da reservada tiver mais gente com posição do que vagas ocupadas — e conta, entre
   essa gente, quem já ocupa pela ampla.
4. **O alvo fixo e os suplentes são os mesmos números em todo recorte**: com alvo fixo 10, a faixa da
   PcD, de duas vagas, é de dez posições; com alvo do quadro e 5 suplentes, a da PPI, de três vagas,
   é de oito.
5. **Um empate não julgado na última vaga da ampla para também a apuração das reservadas**, porque
   elas dependem de saber quem ocupa pela ampla.

Nenhuma dessas consequências aparece em tela alguma antes do certame andar. As três primeiras nem
estão escritas: são o comportamento atual do motor, e esta spec as mostra como tal, sem decidir se
são a leitura certa da norma (D-004, DP-1, DP-2).

**A resposta é a mesma da fatia 1, estendida**: o mesmo botão, o mesmo painel, a mesma jornada e o
mesmo detalhe, agora com um recorte por Modalidade, a marca de quem ocuparia pela ampla, as quatro
quantidades da ocupação de cada recorte e o efeito da reversão declarada — tudo calculado pelo motor
oficial, com candidatos fictícios, sem gravar nada.

**Critério de sucesso do usuário**: o elaborador de um Perfil com reserva vê, para um candidato
autodeclarado fictício, em que lista ele ocuparia vaga, e, para cada recorte, quantas vagas ficariam
sem ocupante e se seriam cedidas à ampla — sob hipóteses declaradas, e sem que a prévia afirme o que
ela não calcula.

### O que a fatia 2 cobre, e o que fica fora

| Fatia 2 (esta spec) | Fora |
|---|---|
| Recortes: a ampla como universo inteiro e cada Modalidade reservada, com ordem e corte próprios | Sorteio, por lista ou não — decisão 007 da `094` |
| Concorrência concomitante, aplicada sempre, sem controle | Chamadas, aceites, desistências e efeitos de convocação (`019`) |
| As quatro quantidades da ocupação por recorte — publicadas, efetivas, ocupadas, faltando —, numa rodada | Faixa seguinte e encadeamento de apurações — D-002 |
| A reversão declarada, nas duas espécies, e a ausência dela | Cascata entre recortes por regra de chamada — decisão 006 da `016` |
| A fronteira das vagas de cada recorte, e a dependência das reservadas em relação à ampla | Remanejamento entre Perfis, que a reversão não alcança (`FR-246` da `016`) |
| Os participantes da Etapa seguinte como a união das faixas | Encadeamento entre marcos — decisão 017 da `094` |

**O que não muda, e não se negocia aqui:** nenhuma regra de classificação, corte, ocupação, reversão
ou publicação; nenhum rótulo do cartão nem do passo Perfis; nenhuma frase do documento publicado;
nenhum ato, evento de trilha ou gravação. O resultado oficial de toda ordem, corte e apuração —
inclusive do acervo — é o mesmo antes e depois desta feature. Os comportamentos atuais que esta spec
expõe (DP-1, DP-2) continuam como estão.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Ver a ordem de cada recorte e quem concorre em qual (Priority: P1)

O elaborador compõe o marco "Classificação para a Entrevista" do Perfil "Polo Serra", que declara as
Modalidades "PPI" e "PcD", com 10 vagas na linha geral, 3 na PPI e 2 na PcD. Ele aperta "Simular
classificação". A jornada abre como na fatia 1, e o marco agora diz, por recorte: *"Ampla concorrência
(todos os 30 candidatos): 10 avançariam. PPI (6 autodeclarados): 3 avançariam. PcD (3
autodeclarados): 2 avançariam."* No detalhe, um seletor de recorte troca a tabela; na da ampla, os
autodeclarados levam a Modalidade ao lado do nome; na da PPI, cada linha diz também a posição da
pessoa na ampla.

**Why this priority**: sem a ordem por recorte, nada do resto se lê: a concomitância, a ocupação e a
reversão são consequências de duas ordens sobre as mesmas pessoas.

**Independent Test**: num Perfil com duas Modalidades reservadas e qualquer população, cada recorte
mostra a ordem que o caminho oficial produziria para aquele recorte com os mesmos dados; a ampla
contém todos, e cada reservada só os autodeclarados nela.

**Acceptance Scenarios**:

1. **Given** um Perfil com PPI e PcD declaradas, **When** o painel abre, **Then** a jornada mostra no
   marco um resumo por recorte — ampla, PPI, PcD, nessa ordem —, e o da ampla diz que ela é o universo
   inteiro (FR-2301, FR-2302, FR-2310).
2. **Given** o detalhe aberto na ampla, **When** o elaborador escolhe "PPI" no seletor, **Then** a
   tabela passa a ser a ordem da PPI, com as mesmas pessoas fictícias e as mesmas notas, e cada linha
   diz a posição da pessoa na ampla (FR-2303, FR-2313, FR-2314).
3. **Given** um Perfil que declara uma Modalidade chamada "Ampla concorrência" e a aponta como a ampla,
   **When** o painel abre, **Then** ela não aparece como recorte reservado, e o recorte da ampla é o
   da linha geral (FR-2301).
4. **Given** um Perfil sem Modalidade reservada, **When** o painel abre, **Then** a classificação, o
   corte e a jornada são os da fatia 1, sem seletor de recorte (FR-2304).
5. **Given** o caso-limite "Reserva sem autodeclarados", **When** o recorte que ele esvazia é aberto,
   **Then** ele diz que ninguém concorreu nele na população fictícia, e não que falta calcular
   (FR-2305).

---

### User Story 2 — Ver onde cada um ocuparia vaga, e quantas ficariam sem ocupante (Priority: P1)

Depois do corte, num bloco marcado como hipótese, o painel mostra, por recorte, as quatro quantidades:
*"Ampla: 10 publicadas, 10 ocupadas, nenhuma sem ocupante. PPI: 3 publicadas, 1 ocupada, 2 sem
ocupante. PcD: 2 publicadas, 1 ocupada, 1 sem ocupante."* Logo abaixo, a razão: *"Ana e Bruno,
autodeclarados PPI, estão entre as 10 primeiras da ampla e ocupariam pela ampla. A vaga reservada
deles continua sendo da PPI. A faixa da PPI, de 3 posições, alcançou os dois e a Carla; o Diego,
autodeclarado PPI na 4ª posição da PPI, ficou fora da faixa — alcançá-lo seria uma faixa seguinte,
que a prévia não simula."* No detalhe da PPI, Ana e Bruno aparecem com a marca "ocuparia pela ampla".

**Why this priority**: é o que o elaborador não consegue prever e o que a medição de 20/10 mostrou —
vagas reservadas sem ocupante com autodeclarado classificado. Sem esta história, a prévia de um
Perfil com reserva mostraria ordens corretas e esconderia a consequência que importa.

**Independent Test**: para cada caso da matriz de equivalência, as quatro quantidades de cada recorte
e o conjunto dos que ocupariam pela ampla são os que as funções oficiais da apuração produzem com os
mesmos dados e as mesmas hipóteses.

**Acceptance Scenarios**:

1. **Given** dois autodeclarados PPI entre as 10 vagas da ampla, **When** a prévia é calculada,
   **Then** a ampla os conta como ocupantes, a PPI não os conta, e o painel diz que a vaga reservada
   continua na PPI — sem mostrar movimento de vaga entre listas (FR-2317).
2. **Given** um autodeclarado PPI na 12ª posição da ampla, com 10 vagas e 5 suplentes na ampla,
   **When** a prévia é calculada, **Then** ele está na faixa da ampla e **não** é marcado como
   ocupando pela ampla: suplente da ampla não ocupa vaga (FR-2318).
3. **Given** a situação da história, **When** a prévia é calculada, **Then** o painel diz quantas
   posições da faixa da PPI foram tomadas por quem ocupa pela ampla, quantos autodeclarados com posição
   ficaram além dela, e que a prévia não simula a faixa seguinte (FR-2319).
4. **Given** um empate residual de dois na 10ª posição da ampla, com 10 vagas, **When** a prévia é
   calculada, **Then** a ampla diz que a apuração pararia na 10ª, e a PPI e a PcD dizem que não foram
   avaliadas porque dependem de quem ocupa pela ampla — sem número nenhum de vagas ocupadas (FR-2323).
5. **Given** um empate residual na última vaga da PPI, **When** a prévia é calculada, **Then** só a
   PPI para; a ampla e a PcD são avaliadas (FR-2323).
6. **Given** um recorte sem linha no quadro de vagas, **When** a prévia é calculada, **Then** a
   ocupação dele aparece como não avaliada, e não como zero vaga (FR-2322).
7. **Given** o bloco da ocupação, **When** o elaborador o lê, **Then** ele diz as hipóteses — todos os
   que avançaram habilitados, nenhuma chamada, desistência ou movimento anterior, apuração sobre este
   marco — e que a prévia faz uma rodada só (FR-2320, FR-2321).
8. **Given** um Perfil sem Modalidade reservada, 10 vagas e alvo fixo 5, **When** a prévia é
   calculada, **Then** o bloco da ocupação mostra só a ampla, com 10 publicadas, 5 ocupadas e 5 vagas
   sem ocupante nesta hipótese — o que o aviso da fatia 1 não dizia (FR-2304, FR-2320).

---

### User Story 3 — Ver o efeito da reversão declarada, ou da ausência dela (Priority: P1)

O Perfil "Polo Serra" declara, no passo Perfis, a reversão *"A quantidade que ficou sem preencher"* — a espécie por saldo. O bloco da ocupação diz: *"A
PPI cederia 2 vagas à ampla concorrência deste Perfil, e a PcD cederia 1. A próxima apuração da ampla
leria 13 vagas efetivas; a prévia não refaz essa apuração."* O elaborador volta ao passo Perfis, troca
para *"Só quando a lista reservada esgota"* — por esgotamento —, grava, e reabre a prévia: *"Nenhuma vaga seria cedida: pela regra de hoje, a
PPI ainda tem quem ocupar — 6 autodeclarados com posição, 1 vaga ocupada."* Num terceiro Perfil, sem
declaração: *"Este Perfil não declara reversão: vaga reservada sem ocupante continua reservada."*

**Why this priority**: a espécie de reversão é escolha normativa que o elaborador faz no passo Perfis
sem ver efeito nenhum, e as duas espécies divergem justamente no caso da história 2.

**Independent Test**: para cada espécie declarada e para a ausência, a quantidade cedida por recorte é
a que a função oficial da reversão devolve com as quantidades da apuração e com o "há quem ocupar"
calculado como o caminho oficial o calcula.

**Acceptance Scenarios**:

1. **Given** um Perfil sem reversão declarada, **When** a prévia é calculada, **Then** o painel diz que
   ele não declara reversão e que vaga reservada sem ocupante continua reservada; nenhuma quantidade
   cedida aparece (FR-2326).
2. **Given** a reversão por saldo e duas vagas reservadas sem ocupante, **When** a prévia é calculada,
   **Then** o painel diz que as duas seriam cedidas à ampla do mesmo Perfil, e quantas vagas efetivas a
   próxima apuração da ampla leria, sem refazê-la (FR-2327, FR-2321).
3. **Given** a reversão por esgotamento e todos os autodeclarados PcD ocupando pela ampla, **When** a
   prévia é calculada, **Then** o painel diz que nenhuma vaga seria cedida porque, pela regra de hoje,
   a ordem da PcD ainda tem pessoas com posição além das vagas ocupadas — e identifica isso como
   comportamento atual, sem afirmar que é a leitura certa (FR-2328, FR-2337, DP-2).
4. **Given** qualquer espécie e nenhuma vaga sem ocupante, **When** a prévia é calculada, **Then** o
   painel diz que não há o que reverter (FR-2330).
5. **Given** a reversão alterada no passo Perfis e não gravada, **When** a prévia é recalculada,
   **Then** ela usa a espécie gravada, e diz de onde a leu (FR-2326, Assumptions).

---

### User Story 4 — Ver o processo seletivo com os recortes (Priority: P2)

Na jornada, a Entrevista, que o marco alimenta, diz: *"Até 12 pessoas poderiam participar: as 10 da
faixa da ampla e mais 2 que só a faixa da PPI ou da PcD alcança. Quem está nas duas faixas conta uma
vez."* O bloco da ocupação aparece depois do marco, marcado como hipótese, com uma linha por recorte.

**Why this priority**: o número de participantes da Etapa seguinte muda com a reserva, e o elaborador
dimensiona a Entrevista por ele. P2 porque as histórias 1 a 3 já entregam o cálculo.

**Independent Test**: num Perfil com reserva, o número de quem poderia participar da Etapa alimentada
é o tamanho da união, por pessoa, das faixas que o marco emitiria em cada recorte.

**Acceptance Scenarios**:

1. **Given** faixas por recorte que se sobrepõem, **When** a jornada é mostrada, **Then** a Etapa
   alimentada diz a união por pessoa, e quantas pessoas só as reservadas acrescentam (FR-2311).
2. **Given** a jornada, **When** o elaborador lê o marco, **Then** o resumo por recorte aparece ali, e a
   ocupação aparece fora da sequência de Etapas e marcos, como hipótese (FR-2310, FR-2312).
3. **Given** o corte da PPI impedido por empate sob `STRICT`, **When** a jornada é mostrada, **Then** o
   marco diz que o corte da PPI não seria emitido, a ampla e a PcD seguem, e a Etapa alimentada diz
   que o número depende do desempate da PPI (FR-2309, FR-2311).

---

### User Story 5 — Escolher um caso-limite de reserva (Priority: P2)

No seletor de população, além dos casos da fatia 1, o elaborador encontra os de reserva:
"Autodeclarado dentro das vagas da ampla", "Reserva com menos autodeclarados que vagas", "Reserva sem
autodeclarados", "Empate na última vaga da ampla", "Empate na última vaga da reservada" e "Alvo fixo
diferente das vagas da reservada". Cada um diz o que foi construído para mostrar e, quando a
configuração desfaz a situação, que ela não ocorre e por quê.

**Why this priority**: a população estável já traz a concomitância e a vaga sem ocupante; os
casos-limite servem à demonstração dirigida, como na fatia 1.

**Independent Test**: cada caso-limite, com a configuração de referência dele, produz a situação que o
nomeia.

**Acceptance Scenarios**:

1. **Given** "Reserva sem autodeclarados" e reversão por esgotamento, **When** a prévia é calculada,
   **Then** o recorte diz que ninguém concorreu nele, todas as vagas dele ficam sem ocupante, e o painel
   diz que seriam cedidas à ampla (FR-2305, FR-2327).
2. **Given** "Alvo fixo diferente das vagas da reservada", alvo fixo 10 e 2 vagas na PcD, **When** a
   prévia é calculada, **Then** o corte da PcD diz que a faixa é de 10 posições, o mesmo número da
   ampla, e não as 2 vagas da linha da PcD (FR-2307).
3. **Given** "Empate na última vaga da ampla", **When** a prévia é calculada, **Then** acontece o
   cenário 4 da história 2.

---

### User Story 6 — No celular e com leitor de tela (Priority: P3)

A 375 px, o seletor de recorte cabe na cabeça do detalhe, e o bloco da ocupação empilha um recorte por
vez. Com leitor de tela, o seletor é um controle nativo com rótulo, e o anúncio do recálculo diz o
resumo de cada recorte uma vez.

**Why this priority**: as mesmas razões da história 5 da `094`.

**Independent Test**: a 375 px, trocar de recorte e recalcular sem rolagem horizontal da página; o
anúncio contém o resumo por recorte.

**Acceptance Scenarios**:

1. **Given** a 375 px e três recortes, **When** o elaborador troca de recorte, **Then** a página não
   rola na horizontal (FR-2344).
2. **Given** o leitor de tela, **When** o painel se recalcula, **Then** o resumo de cada recorte é
   anunciado uma vez, sem reler as tabelas (FR-2344).

---

### Edge Cases

- **Modalidade declarada sem linha no quadro**: com alvo do quadro, o corte daquele recorte não é
  apurável, como no caminho oficial (`recorte_sem_linha_de_quadro`); a ordem aparece, a faixa e a
  ocupação não, e os outros recortes calculam (FR-2308, FR-2322).
- **Perfil com reserva e sem quadro nenhum**: nenhuma ocupação é avaliada, e o painel diz isso uma
  vez, e não por recorte.
- **Alvo do quadro e Modalidade apontada como ampla**: ela lê a linha geral, como `linha_do_quadro`
  faz no caminho oficial, e não é recorte (FR-2301).
- **Corte da ampla impedido sob `STRICT`**: a ocupação da ampla não é avaliada, e a das reservadas
  também não, porque depende de quem ocupa pela ampla (FR-2324).
- **Corte de uma reservada impedido**: só aquele recorte deixa de ter faixa e ocupação; a ampla e as
  outras reservadas seguem (FR-2309, FR-2324).
- **Marco sem regra de corte**: a ocupação de cada recorte é apurada sobre a ordem inteira do recorte,
  como `progrediram_em_ordem` faz no produto quando não há corte, e o painel diz isso.
- **Desfecho do empate não declarado e empate que atravessa a faixa de um recorte**: aquele recorte
  mostra as duas consequências, como na fatia 1, e a ocupação dele não é avaliada até a declaração.
- **A mesma pessoa no fim da faixa da ampla e no começo da faixa da reservada**: ela conta uma vez na
  Etapa seguinte (FR-2311), e ocupa pela ampla só se estiver entre as vagas da ampla (FR-2318).
- **Mais recortes do que a prévia cobre**: o painel diz o limite e não calcula (FR-2343).
- **Reversão declarada em Perfil sem Modalidade reservada**: não há o que reverter, e o painel não fala
  de reversão.
- **Soma das linhas do quadro diferente das vagas imediatas do Perfil**: a prévia lê cada linha como
  gravada, e não corrige nem completa a soma; a conferência é da publicação (`025`).
- **Percentual da Modalidade declarado**: não entra em conta nenhuma; a quantidade é a da linha do
  quadro (decisão 003 da `016`).

## Requirements *(mandatory)*

### Functional Requirements

#### Onde a fatia 2 mora

- **FR-2300**: A fatia 2 MUST estender a prévia da `094` — o mesmo botão, o mesmo painel, a jornada e
  o detalhe —, sem tela nova e sem controle novo no cartão do marco. O botão aparece nas mesmas
  condições da fatia 1 (D-001).

#### Os recortes

- **FR-2301**: Os recortes da prévia MUST ser os do caminho oficial, derivados do mesmo lugar que a
  classificação e a ocupação usam (`FR-491` da `034`): a ampla concorrência, sem lista, e cada
  Modalidade reservada declarada no Perfil, na ordem declarada. A Modalidade que o Perfil aponta como
  ampla MUST NOT virar recorte reservado (`FR-503` da `034`).
- **FR-2302**: O recorte da ampla MUST conter **todos** os candidatos fictícios, autodeclarados
  inclusive, e o painel MUST nomeá-lo como o universo inteiro (`FR-492`, `FR-493` da `034`).
- **FR-2303**: Cada Modalidade reservada MUST ter ordem própria, só com os autodeclarados nela,
  calculada pelas mesmas funções da ampla. O mesmo candidato MUST ter uma posição em cada ordem de que
  participa.
- **FR-2304**: Em Perfil sem Modalidade reservada, a classificação, o corte e a jornada MUST ser os da
  fatia 1, sem seletor de recorte; só o bloco da ocupação muda (FR-2320).
- **FR-2305**: Recorte sem nenhum autodeclarado na população MUST aparecer com ordem vazia e com a frase
  de que ninguém concorreu nele na população fictícia — e MUST NOT parecer pendência (`FR-492a` da
  `034`).
- **FR-2306**: A prévia MUST tratar toda Modalidade reservada pela mesma regra, qualquer que seja o
  nome. "PPI" e "PcD" são nomes que o Edital declara, e a prévia MUST NOT aplicar regra, texto ou
  cenário por nome de Modalidade (D-006).

#### O corte de cada recorte

- **FR-2307**: O corte de cada recorte MUST seguir a regra do marco como o caminho oficial a aplica: o
  alvo fixo e os suplentes são os mesmos números em todo recorte; o alvo do quadro é a linha do
  recorte. Quando o tamanho da faixa de uma reservada for diferente das vagas da linha dela, o painel
  MUST dizer os dois números e de onde vem cada parcela da faixa.
- **FR-2308**: Com alvo do quadro, recorte sem linha no quadro MUST aparecer com a ordem e com o corte
  não apurável, dito como tal e não como zero; os demais recortes MUST ser calculados.
- **FR-2309**: A recusa do corte sob `STRICT`, o desfecho não declarado e o empate que atravessa a
  faixa MUST ser avaliados por recorte, e a manchete MUST dizer em qual recorte o corte não seria
  emitido. A recusa num recorte MUST NOT impedir o cálculo dos outros (`FR-494` da `034`).

#### A jornada

- **FR-2310**: O ponto do marco simulado, na jornada, MUST mostrar um resumo por recorte — quantos
  compõem o recorte, quantos avançariam, se o corte seria emitido —, na ordem da FR-2301.
- **FR-2311**: A Etapa que o marco alimenta MUST dizer quantas pessoas poderiam participar como a
  **união, por pessoa**, das faixas de todos os recortes — a da ampla e a da Modalidade de cada um —,
  MUST dizer que quem está em duas faixas conta uma vez, e MUST dizer quantas pessoas só as reservadas
  acrescentam. Quando o corte de algum recorte não seria emitido, MUST dizer que o número depende dele.
- **FR-2312**: A ocupação MUST aparecer na jornada fora da sequência de Etapas e marcos, marcada como
  hipótese, com uma linha por recorte — como a apuração das vagas na fatia 1 (decisão 013 da `094`).

#### O detalhe

- **FR-2313**: O detalhe MUST oferecer um seletor de recorte, com a ampla escolhida ao abrir. Trocar de
  recorte MUST manter a população, o marco, a vista e o estado do "o que mudou".
- **FR-2314**: Na tabela da ampla, o autodeclarado MUST levar a Modalidade fictícia junto do nome. Na
  tabela de uma reservada, cada linha MUST dizer também a posição da pessoa na ampla, e quem ocuparia
  pela ampla MUST levar essa marca.
- **FR-2315**: A comparação de empates da fatia 1 MUST valer por recorte: um empate é do recorte em que
  acontece, e a frase de que linha ele atravessa MUST nomear o recorte.

#### A concorrência concomitante

- **FR-2316**: A concorrência concomitante MUST ser aplicada sempre, como no caminho oficial, e a
  prévia MUST NOT oferecer controle para ligá-la ou desligá-la. O painel MUST dizer que ela vale para
  todo Perfil com reserva e não é campo do Edital.
- **FR-2317**: Quem ocuparia vaga pela ampla MUST aparecer, na reservada, como "ocuparia pela ampla", e
  MUST NOT ser computado no preenchimento dela (`FR-252` da `016`). A vaga reservada MUST aparecer como
  continuando na reservada, e o painel MUST NOT mostrar movimento de vaga por causa disso (`FR-253` da
  `016`). Estando a pessoa dentro das vagas das duas listas, o painel MUST dizer que ela ocuparia pela
  ampla (`FR-254` da `016`).
- **FR-2318**: "Ocupar pela ampla" MUST significar estar entre os titulares da ampla — as primeiras
  vagas efetivas da sequência que avançou —, e não apenas na faixa dela. Suplente da ampla MUST NOT
  ser marcado como ocupando pela ampla.
- **FR-2319**: Quando pessoas que ocupariam pela ampla tomam posições da faixa de uma reservada, o
  painel MUST dizer quantas, quantos autodeclarados com posição ficaram além da faixa daquela
  reservada, e que alcançá-los é faixa seguinte, que a prévia não simula. A frase MUST descrever o
  comportamento atual, sem afirmar que é a leitura certa da norma (DP-1).

#### A ocupação

- **FR-2320**: Para cada recorte, a prévia MUST mostrar as quatro quantidades da apuração —
  publicadas, efetivas, ocupadas e faltando —, calculadas pelas funções oficiais, num bloco marcado
  como hipótese, com as hipóteses declaradas: todos os que avançaram habilitados na Etapa governada;
  nenhuma chamada, aceite, desistência, efeito de convocação ou movimento anterior; a apuração feita
  sobre este marco; as vagas publicadas da linha do quadro gravada.
- **FR-2321**: A prévia MUST fazer **uma rodada**: a ampla com as vagas publicadas, depois cada
  reservada sem quem ocuparia pela ampla, depois a reversão de cada reservada. Ela MUST NOT refazer a
  apuração da ampla com as vagas recebidas, nem encadear apurações ou faixas seguintes; quando houver
  vaga cedida, MUST dizer quantas vagas efetivas a próxima apuração da ampla leria, e que a prévia não
  a refaz (D-002).
- **FR-2322**: Recorte sem linha no quadro, ou Perfil sem quadro, MUST ter a ocupação dita como não
  avaliada, e MUST NOT mostrar zero vaga (`FR-242` da `016`).
- **FR-2323**: Empate residual que atravessa a fronteira das vagas da ampla MUST parar a ampla e MUST
  deixar as reservadas como não avaliadas, dizendo que dependem de quem ocupa pela ampla. Empate na
  fronteira das vagas de uma reservada MUST parar só aquela reservada.
- **FR-2324**: Corte não emitido num recorte MUST deixar a ocupação daquele recorte não avaliada; corte
  não emitido na ampla MUST deixar também as reservadas não avaliadas, pela mesma dependência.
- **FR-2325**: A prévia MUST NOT mostrar mais ocupadas que efetivas nem faltando negativo, e MUST
  chamar "faltando" de vagas sem ocupante nesta hipótese.

#### A reversão

- **FR-2326**: A espécie de reversão MUST ser lida do Perfil gravado, e o painel MUST dizer de onde a
  leu. Sem declaração, o painel MUST dizer que o Perfil não declara reversão e que vaga reservada sem
  ocupante continua reservada; MUST NOT presumir espécie nenhuma (`FR-245`, `FR-251` da `016`).
- **FR-2327**: Com reversão declarada, o painel MUST dizer, por reservada, quantas vagas seriam cedidas
  à ampla do **mesmo** Perfil, pela função oficial, e com a espécie nomeada pelo rótulo do passo
  Perfis — *"Só quando a lista reservada esgota"* ou *"A quantidade que ficou sem preencher"*. A reversão MUST aparecer como o que a apuração faria, e não como fato ocorrido.
- **FR-2328**: Para a espécie por esgotamento, "há quem ocupar" MUST ser calculado como o caminho
  oficial o calcula hoje, e o painel MUST dizer, quando nenhuma vaga for cedida por isso, quantas
  pessoas com posição a regra contou e quantas vagas estão ocupadas, identificando-o como comportamento
  atual (DP-2).
- **FR-2329**: A prévia MUST NOT mostrar reversão para outro Perfil, nem para outra Modalidade
  reservada (`FR-246` da `016`).
- **FR-2330**: Com reversão declarada e nenhuma vaga sem ocupante, o painel MUST dizer que não há o que
  reverter.

#### População e casos-limite

- **FR-2331**: A população estável MUST incluir, para cada Modalidade reservada, autodeclarados
  plantados a partir das fronteiras do momento da montagem: ao menos um dentro das vagas da ampla, ao
  menos um na faixa da ampla e além das vagas dela, e autodeclarados suficientes para preencher a
  faixa da reservada e deixar ao menos um além dela. A Modalidade de cada candidato MUST ser a mesma
  enquanto o painel estiver aberto, qualquer que seja o campo alterado (decisão 003 da `094`, D-003).
- **FR-2332**: Além dos casos-limite da fatia 1, a prévia MUST oferecer: autodeclarado dentro das vagas
  da ampla; reserva com menos autodeclarados que vagas; reserva sem autodeclarados; empate na última
  vaga da ampla; empate na última vaga da reservada; alvo fixo diferente das vagas da reservada. Cada
  um MUST dizer o que foi construído para mostrar e, quando a configuração o desfaz, que a situação não
  ocorre e por quê.
- **FR-2333**: Cada candidato fictício MUST ter no máximo uma Modalidade reservada, como a inscrição.

#### O que mudou

- **FR-2334**: O quadro "O que mudou" da fatia 1 MUST passar a dizer, por recorte, a situação do corte,
  o número dos que avançam e as quatro quantidades da ocupação, além da quantidade cedida pela reversão
  e do número de participantes da Etapa seguinte; e, como na fatia 1, MUST NOT comparar populações
  diferentes.

#### Vocabulário e limites do que se afirma

- **FR-2335**: O painel MUST dizer "ampla concorrência (todos os candidatos)", "reservada", "ocuparia
  pela ampla", "vaga sem ocupante nesta hipótese" e "seria cedida à ampla". Ele MUST NOT dizer que
  alguém foi convocado, aprovado, aceitou ou se matriculou (`FR-258` da `016`), nem chamar candidato
  de "cotista aprovado".
- **FR-2336**: A declaração do que a prévia não simula MUST passar a incluir: chamadas, aceites,
  desistências e efeitos de convocação; faixa seguinte; movimentos de vaga anteriores; encadeamento de
  apurações; cascata entre recortes por regra de chamada; remanejamento entre Perfis; o percentual da
  Modalidade, que fundamenta e não calcula; e o sorteio por lista.
- **FR-2337**: Onde a prévia mostrar comportamento que esta spec registra como pendente de decisão
  (DP-1, DP-2), o painel MUST descrevê-lo como comportamento atual e MUST NOT apresentá-lo como a leitura
  definitiva da norma. Esta feature MUST NOT alterar a regra, o rótulo nem o documento.

#### O motor

- **FR-2338**: A prévia MUST usar as mesmas funções de derivação dos recortes, leitura da linha do
  quadro, preparação do universo com recorte, ordenação, faixa, titulares, ocupantes, apuração e
  reversão que o caminho oficial usa.
- **FR-2339**: As duas decisões que o caminho oficial hoje toma dentro de funções que leem banco — quem
  ocupa pela ampla e se a reservada tem quem ocupar — MUST ser extraídas para funções puras chamadas
  pelos dois caminhos, sem mudar o resultado oficial, inclusive nos comportamentos registrados em DP-1
  e DP-2 e nos achados da R-002 (D-005).
- **FR-2340**: A equivalência entre prévia e caminho oficial MUST ser verificada por teste, com os
  mesmos dados pelos dois caminhos, cobrindo: ordem por recorte; faixa por recorte com alvo fixo e do
  quadro; recorte sem linha; concomitância dentro e fora das vagas da ampla; as quatro quantidades por
  recorte; reversão por saldo, por esgotamento e ausente; empate na fronteira da ampla e da reservada;
  ordem vazia. Uma alteração no motor oficial que a prévia não acompanhe MUST reprovar o teste.

#### Sem efeito, acesso e dados

- **FR-2341**: Abrir, recalcular, trocar recorte, trocar cenário e fechar a prévia MUST NOT gravar nada:
  nenhuma ordem, corte, apuração, movimento de vaga, evento de trilha, alteração de rascunho ou
  persistência de candidato fictício.
- **FR-2342**: A Modalidade dos candidatos MUST ser fictícia e identificada como tal. A prévia MUST NOT
  ler, exibir nem derivar autodeclaração, documento comprobatório ou qualquer dado de inscrição real,
  e MUST NOT associar Modalidade a nome de pessoa real.
- **FR-2343**: A prévia MUST cobrir até seis Modalidades reservadas, além da ampla (R-006 da
  pesquisa); acima disso, MUST dizer o limite e não calcular.

#### Acessibilidade e política de conteúdo

- **FR-2344**: O seletor de recorte MUST ser controle nativo com rótulo; a 375 px, trocar de recorte e
  ler o bloco da ocupação MUST NOT produzir rolagem horizontal da página; o anúncio do recálculo MUST
  conter o resumo de cada recorte uma vez.
- **FR-2345**: Seletor, blocos novos e recálculo MUST funcionar sob a política de conteúdo vigente,
  sem estilo nem script escritos no template, sem violação no console.

### Key Entities

- **Recorte da prévia**: a ampla (sem lista) ou uma Modalidade reservada do Perfil, com o rótulo da
  derivação oficial. Não é gravado.
- **Candidato fictício** *(estendido)*: ganha uma Modalidade reservada ou nenhuma — o campo que a
  fatia 1 já carregava nulo (decisão 008 da `094`).
- **Prévia de um recorte**: ordem, corte, quem ocuparia pela ampla (nas reservadas), as quatro
  quantidades, a quantidade cedida e o motivo de não ser avaliada, quando não for. Existe só na
  resposta.
- **Rodada de ocupação**: a sequência ampla → reservadas → reversão, com as hipóteses declaradas e o
  número de vagas efetivas que a próxima apuração da ampla leria. Existe só na resposta.
- **Participantes da Etapa seguinte**: a união, por pessoa, das faixas dos recortes.

## Decisões

### D-001 — A fatia 2 estende o painel da 094, e espera a interface dela

A jornada, o detalhe, a população estável, o "o que mudou", o recálculo por htmx e a CSP são da `094`;
esta spec acrescenta recortes, ocupação e reversão a cada um deles, sem duplicar nenhum. A
consequência é de ordem: a implementação desta spec começa depois da interface da fatia 1, que o
usuário ainda não autorizou. O que dá para fazer antes — a extração das funções puras e a equivalência
(D-005) — está separado nas tarefas, como a `094` separou as dela.

**Alternativa descartada**: uma tela de "simulação de reservas" à parte. Afastaria a consequência do
campo que a produz (alvo, suplentes, desfecho), e o elaborador teria de comparar duas telas para ver
que o alvo fixo vale também na PcD.

### D-002 — Uma rodada de ocupação, sem encadear

No produto, cada apuração é um ato; a reversão grava um movimento, e a apuração da ampla aparece
obsoleta com a causa dita — quem quiser o número novo emite (`causas_de_obsolescencia`, `016`). Não há
orquestração que refaça a ampla e, depois, as reservadas. A prévia faz o mesmo: apura a ampla com as
vagas publicadas, cada reservada sem os que ocupariam pela ampla, calcula a quantidade que cada
reservada cederia, e diz quantas vagas efetivas a próxima apuração da ampla leria — sem calculá-la.

**Alternativas descartadas.** Refazer a ampla com as vagas recebidas mostraria titulares a mais na
ampla, e os autodeclarados entre eles mudariam o preenchimento das reservadas, que mudaria a reversão:
uma iteração até o ponto fixo, que o produto não faz e que a prévia inventaria. Encadear faixas
seguintes exigiria simular continuação, déficit como causa (`FR-255` da `016`) e convocação — a mesma
orquestração que a decisão 017 da `094` adiou para os marcos.

### D-003 — A população estável ganha Modalidades plantadas nas fronteiras de cada recorte

Como na fatia 1, a população estável é montada uma vez, a partir das fronteiras do momento da montagem,
e nenhuma alteração de campo a refaz. A fatia 2 acrescenta a Modalidade: para cada reservada, um
autodeclarado dentro das vagas da ampla (a concomitância), um na faixa da ampla e além das vagas dela
(o suplente da ampla, que não ocupa), e autodeclarados suficientes para preencher a faixa da reservada
e deixar um além dela (o que a faixa seguinte alcançaria). As notas são as mesmas da fatia 1: a
Modalidade é atribuída a candidatos que já existem, nas posições da ampla que essas situações pedem, e
não muda a pontuação de ninguém. Remontar continua sendo ato explícito.

**Por que atribuir, e não acrescentar candidatos**: acrescentar mudaria a ordem da ampla em relação à
da fatia 1, e um Perfil que passasse a declarar uma Modalidade veria a ampla mudar sem que regra
nenhuma da ampla mudasse.

### D-004 — A prévia mostra o comportamento atual, inclusive onde ele é pendência

A medição de 20/10 encontrou dois comportamentos do motor que a norma dos Editais da amostra não
confirma nem desmente (DP-1, DP-2). A prévia existe para mostrar ao elaborador o que o motor faria, e
uma prévia que mostrasse outra coisa seria pior do que nenhuma; por isso ela calcula pelo motor e
descreve o efeito como comportamento atual, na forma que a `094` adotou para o desfecho do empate. A
decisão sobre a regra é do usuário, e esta spec não a toma.

### D-005 — "Quem ocupa pela ampla" e "há quem ocupar" saem para funções puras

As duas decisões moram hoje em funções de aplicação que leem banco: `selectors.ocupantes_da_ampla`
(titulares da ampla, a partir da ordem, do corte, do quadro, dos movimentos e dos efeitos) e
`movimento.ha_quem_ocupar` (posições com valor na ordem vigente, comparadas às vagas ocupadas). A
prévia precisa das mesmas decisões sobre candidatos fictícios. Pela mesma razão da decisão 004 da
`094`, a parte que decide sai para o domínio, e as consultas ficam onde estão; o caminho oficial passa
a chamar a função pura, e a equivalência é teste.

A extração MUST preservar o comportamento atual, inclusive os achados registrados na R-002: corrigir
um deles de passagem mudaria resultado oficial, e é decisão do usuário.

### D-006 — PPI e PcD são Modalidades declaradas, e não tipos

O sistema não conhece "PPI" nem "PcD": conhece Modalidades declaradas no Perfil, com código, nome e
fundamento, e a ampla apontada por identidade (`generalCompetitionModalityId`). A prévia segue a
mesma regra: qualquer número de reservadas, todas tratadas igual, com os nomes do Edital. Um cenário
"de PcD" seria regra por nome, que a `025` recusou para o quadro e a `016` para a reversão.

### D-007 — A jornada mostra todos os recortes; o detalhe, um por vez

A jornada responde "quantos avançam, para onde, e quantas vagas ficam sem ocupante", e essa resposta
precisa dos recortes juntos — a Etapa seguinte recebe a união deles. O detalhe responde "por que esta
pessoa está aqui", e a tabela de três recortes lado a lado não cabe nem se lê; daí o seletor. A troca
de recorte é um fragmento htmx, como a troca de vista da fatia 1.

### D-008 — O protótipo desta spec é de cálculo, e não visual

O protótipo navegável da `094` está no PR #316, que não está na `main`, e esta spec é um PR só com a
fatia 2. Estender aquele protótipo aqui obrigaria a copiar mil e quinhentas linhas de página ou a
depender de um PR aberto. O protótipo desta spec é um roteiro de reprodução
([`prototipo/reproducao.py`](prototipo/reproducao.py)) que monta populações por recorte e roda o motor
oficial de verdade — preparação com recorte, ordenação, faixa, titulares, apuração e reversão —,
produzindo as tabelas da R-001. É ele que sustenta as cinco consequências do início desta spec. A
extensão visual do protótipo da `094` fica como tarefa desta spec, depois do merge do #316.

## Decisões pendentes do usuário

Registradas, não decididas. Esta feature não altera nenhuma delas; o painel descreve o comportamento
atual (FR-2337). A medição está em [research.md](research.md), R-001.

### DP-1 — A faixa da reservada conta quem ocupa pela ampla

O corte de uma reservada é calculado sobre a ordem inteira dela, inclusive quem ocuparia pela ampla, e
a apuração tira essas pessoas depois. Com alvo do quadro, a faixa da reservada fica do tamanho das
vagas e, havendo concomitância, deixa vagas sem ocupante com autodeclarado classificado fora dela. O
caminho de saída existe — faixa seguinte por déficit (`FR-255` da `016`) —, mas, com reversão por
saldo, a primeira apuração cede essas vagas antes. O item 8.9 do 28/2026 fala em *"abrindo vaga para o
próximo suplente autodeclarado"*; se a reversão por saldo, nesse caso, cumpre o Edital do 57/2026 que
a declara, é leitura de norma.

### DP-2 — "Há quem ocupar" conta quem ocupa pela ampla

Sob reversão por esgotamento, a reservada só cede quando não há mais quem ocupar, e a regra de hoje
compara o número de pessoas com posição na ordem da reservada com as vagas ocupadas — contando quem já
ocupa pela ampla, que nunca ocupará a reservada. Numa reservada cujos autodeclarados todos ocupam pela
ampla, nenhuma vaga é cedida, nunca — e o rótulo do passo Perfis diz *"Só quando a lista reservada
esgota"*. Se "ausência de candidatos aprovados na reserva" (28/2026, 4.3)
inclui esse caso é leitura de norma.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-870**: No roteiro de compreensão estendido, ao menos 4 de cada 5 elaboradores respondem, olhando
  só a prévia, para um candidato autodeclarado apontado: em que lista ele ocuparia vaga, se a vaga
  reservada dele continua reservada, quantas vagas da reservada ficariam sem ocupante e se seriam
  cedidas à ampla.
- **SC-871**: Em 100% dos casos da matriz de equivalência (FR-2340), a prévia e o caminho oficial
  produzem as mesmas ordens, faixas, conjuntos de quem ocupa pela ampla, quantidades da apuração e
  quantidades cedidas, por recorte.
- **SC-872**: Em Perfil sem Modalidade reservada, 100% dos casos de equivalência da fatia 1 continuam
  produzindo a mesma classificação e o mesmo corte.
- **SC-873**: Na população estável, 100% das alterações de campo do cartão mantêm os mesmos candidatos,
  as mesmas notas e as mesmas Modalidades.
- **SC-874**: Em 100% dos recortes cuja ocupação não é avaliada, nenhuma quantidade de vagas aparece.
- **SC-875**: Em 100% dos Perfis sem reversão declarada, o painel diz que não reverte, e nenhuma
  quantidade cedida aparece.
- **SC-876**: O painel mostra o resultado novo em até 1 segundo depois da alteração de um campo, para
  populações de até 500 candidatos fictícios e até o limite de recortes da FR-2343.
- **SC-877**: Em qualquer sequência de aberturas, recálculos, trocas de recorte e de cenário, o banco
  recebe zero escritas e a trilha zero eventos.
- **SC-878**: A 375 px, trocar de recorte e ler a ocupação não produzem rolagem horizontal da página, e
  o console registra zero violações da política de conteúdo.

## Assumptions

- **LGPD (Princípio III da Constituição)**: autodeclaração étnico-racial e condição de pessoa com
  deficiência são dados pessoais sensíveis, e a prévia não trata nenhum. Os candidatos e as Modalidades
  deles são fictícios, gerados na resposta e descartados com ela; nenhuma inscrição, autodeclaração ou
  documento real é lido (FR-2342), nada é persistido (FR-2341), e nenhum registro de auditoria é
  produzido porque não há operação sobre dado de ninguém. Os nomes fictícios não carregam marca de
  Modalidade, para que a tela não associe nome a grupo.
- **Modalidades, quadro e reversão vêm do gravado.** As Modalidades declaradas, a ampla apontada, as
  linhas do quadro por Modalidade e a espécie de reversão são do passo Perfis, e a prévia os lê do
  rascunho gravado, como a fatia 1 já lê pesos, fatos e linha geral.
- **A habilitação é da pessoa, e não do recorte**: todos os que avançaram em algum recorte são supostos
  habilitados na Etapa governada, como na decisão 006 da `094`.
- **Uma Modalidade por candidato**, como uma inscrição (FR-2333).
- **A apuração da prévia não tem movimentos anteriores nem efeitos**: efetivas = publicadas em todo
  recorte, antes da reversão.
- **Os recortes vêm do mesmo derivador que a classificação e a ocupação usam**; o sorteio, que tem
  derivação própria (`FR-491a` da `034`), continua fora (decisão 007 da `094`).
- **O vocabulário de Modalidade, recorte, ampla e reversão é o da `016` e da `034`**, e a espécie de
  reversão é nomeada com o rótulo do passo Perfis.
