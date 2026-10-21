# Feature Specification: Prévia do sorteio — a ordem de cada lista, a ocupação das vagas e muitas rodadas, com semente fictícia

**Feature Branch**: `claude/sorteio-funcionamento-98c99f`, sobre a `main` em `14efe941`

**Created**: 2026-10-21

**Status**: Implementada em 21/10/2026, por autorização do usuário: o motor no PR #327 e a interface num
PR empilhado sobre ele. A validação com elaboradores (SC-925, SC-926, T033) fica aberta até o relato do
usuário. O merge é do usuário.

**Input**: pedido do usuário de 21/10/2026 — *"escreve a spec da prévia do sorteio reaproveitando o
motor da 095, com semente fictícia anunciada como tal"* —, depois de a conversa medir que quem compõe
um marco por sorteio não tem como ver, antes do certame, o que o sorteio faz com as cotas. As quatro
decisões que a spec precisava foram tomadas pelo usuário no mesmo dia, e estão em D-001 a D-004.

> **Faixa de identificadores.** Esta spec abre em **FR-2477** e **SC-925**. Teto medido em 21/10/2026
> em `specs/` de **todas as worktrees desta máquina** e na `main`: `FR-2476`, `SC-924`, `UX-222`.
> **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`, porque são lidas dentro da feature
> que as produziu.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-2301 da `095`"); decisão de outra feature, pelo número e pela feature ("a decisão 007 da `094`"),
> porque `D-` aqui é só desta spec.

---

## Por que esta feature existe

**A prévia da classificação simula todo marco, menos o que ordena por sorteio.** A `094` deixou o
sorteio de fora por decisão do usuário de 19/10/2026 (decisão 007 da `094`): *"a ordem por sorteio
nasce da semente, que não existe na composição"*. A `095`, que trouxe as cotas, herdou a exclusão. O
botão "Simular classificação" não aparece no cartão do marco por sorteio (FR-2200 da `094`), e o
painel diz que o sorteio não é simulado (FR-2254 da `094`).

**E o sorteio é o padrão dominante da amostra real do Cefor, quase sempre com cotas** (varredura da
`035`). É exatamente onde o elaborador mais precisaria de prévia, e onde ela falta.

### O que quem compõe não vê hoje — medido em 21/10/2026

| O que o sistema faz | Onde o elaborador descobre |
|---|---|
| O autodeclarado concorre **também** na ampla, e a ampla é sorteada com o universo inteiro (FR-252 da `016`; decisão 001 da `034`) | só na tela de ocupação, com o certame andando |
| Cada lista tem **ordem própria**: a chave do IFES-SORTEIO-SHA256-v1 leva a identidade do recorte, e a mesma pessoa tem uma posição na ampla e outra na reservada | em lugar nenhum da composição |
| Quem ocupa pela ampla **não é computado** na reservada, e a vaga reservada fica na reserva | só na ocupação |
| A faixa da reservada conta quem ocupa pela ampla, e sobra vaga reservada sem ocupante com autodeclarado classificado logo abaixo (DP-1 da `095`) | só na ocupação — ou na prévia da `095`, que não alcança sorteio |
| Sob reversão "por esgotamento", essa vaga nunca é cedida quando todos os autodeclarados ocupam pela ampla (DP-2 da `095`) | idem |
| O sistema **sorteia sempre**, mesmo com menos inscritos que vagas ([achado de 12/10](../../doc/achado-sorteio-condicionado-no-texto-e-incondicional-no-sistema.md)) | em lugar nenhum |

**E a única frase que fala disso na composição sugere o contrário.** O painel "Como preencher" do
marco diz que entram as inscrições *"do recorte — que é a lista em que a pessoa concorre: a ampla
concorrência, ou uma Modalidade de Concorrência"*. Lida ao pé da letra, cada pessoa estaria em uma
lista só. Corrigir a frase não é escopo desta spec (ver *Fora*): é achado registrado, e a decisão é do
usuário.

### Por que a sorte muda a leitura, e uma rodada só não basta

No marco por pontuação a ordem é função das notas: a mesma população dá sempre a mesma prévia. No
sorteio, **o que se quer saber é uma frequência**: com 10 vagas na ampla, 3 na PPI e 12 autodeclarados
PPI entre 58 inscritos, quantos PPI costumam cair entre os 10 primeiros da ampla? Com que frequência
sobra vaga de PPI sem ocupante? Uma rodada responde *"desta vez, 2"*, e o elaborador generalizaria de
um caso. Por isso a prévia mostra uma rodada em detalhe **e** o resumo de muitas (D-002).

### O motor existe — e isso delimita a feature

| Peça | Estado | Onde |
|---|---|---|
| Ordem do sorteio a partir de relação, recorte e semente | ✅ função pura | `sorteios/domain/chave.py` (`ordem`) |
| Material bruto → semente, pela regra publicada | ✅ função pura | `sorteios/domain/normalizacao.py` |
| Corte sobre uma ordem | ✅ o mesmo da `094` | `classificacao/domain/faixa.py` |
| Quem ocupa pela ampla, as quatro quantidades, a reversão | ✅ funções puras extraídas pela `095` (decisão 005 da `095`) | `ocupacao/domain/` |
| Painel, jornada, detalhe e seletor de recorte | ✅ da `094`/`095` | `interface/previa_da_classificacao.py` |
| **Ordem por sorteio sobre candidatos fictícios, com semente fictícia** | ❌ | — |
| **População informada por lista** | ❌ a da `095` é derivada das vagas | `classificacao/domain/cenarios_da_previa.py` |
| **Resumo de muitas rodadas** | ❌ | — |

A ordem do sorteio custa pouco: **0,9 ms** para uma lista de 500 números públicos, medido em
21/10/2026 nesta máquina, chamando `chave.ordem` vinte vezes. Uma rodada com 500 inscritos e seis
reservadas ordena no máximo ~1.000 números.

### O que esta spec cobre, e o que fica fora

| Cobre | Fora |
|---|---|
| O botão no cartão do marco por sorteio e o painel da `094` | A Retificação (decisão 009 da `094`) |
| Semente fictícia gerada pelo sistema, só leitura, anunciada como fictícia | Semente digitada, ou qualquer semente real (D-001; FR-030 da `021`) |
| A ordem de cada lista pelo algoritmo oficial, a ampla com o universo inteiro | A Modalidade declarada como ampla como lista própria do sorteio (D-005, registrada) |
| Corte, ocupação numa rodada e reversão, pelas funções da `095` | Convocação, aceite, desistência, indeferimento, faixa seguinte (D-004) |
| Resumo de muitas rodadas por recorte | Encadeamento entre marcos (decisão 017 da `094`) |
| População informada por lista, com sugestão | Etapa de habilitação antes do sorteio: a prévia supõe todos habilitados, como a `094` |
| — | A frase do "Como preencher" que sugere lista única: achado registrado, não corrigido |
| — | DP-1 e DP-2 da `095`: a prévia os mostra como comportamento atual e não os decide |

**O que não muda, e não se negocia aqui:** nenhuma regra do sorteio, da ordem, do corte, da ocupação
ou da reversão; nenhum rótulo do cartão nem do passo Perfis; nenhuma frase do documento publicado;
nenhum ato, evento de trilha ou gravação. O sorteio oficial de todo certame é o mesmo antes e depois
desta feature.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Simular o sorteio de cada lista com uma semente fictícia (Priority: P1)

O elaborador compõe o marco "Sorteio das vagas" do Perfil "Polo Serra", que declara as Modalidades
"PPI" e "PcD", com 10 vagas na linha geral, 3 na PPI e 2 na PcD, alvo do quadro e nenhum suplente. No
cartão, escolhe a forma "sorteio" e aperta "Simular sorteio". O painel abre com a população sugerida —
20 só na ampla, 6 PPI, 4 PcD — e uma faixa no topo: *"Semente fictícia: 048213 771904 302558 919007
116482. Gerada agora pelo sistema, só para esta prévia. No dia do certame, a semente sairá do concurso
que o Edital declarar, e a ordem será outra."* A jornada diz, no marco: *"Ampla concorrência (todos os
30 inscritos, autodeclarados inclusive): 10 avançariam. PPI (6 autodeclarados): 3 avançariam. PcD (4
autodeclarados): 2 avançariam."* No detalhe, a tabela da ampla mostra a posição sorteada de cada um,
com a Modalidade ao lado dos autodeclarados; a da PPI mostra também a posição de cada pessoa na ampla.
O elaborador aperta "Sortear de novo": a semente muda, e as ordens também.

**Why this priority**: é a feature. Sem a ordem de cada lista, nada do resto se lê, e a ordem da
ampla com os autodeclarados dentro é o fato que a composição hoje esconde.

**Independent Test**: para uma semente fictícia e uma população, a ordem de cada recorte é a que a
função oficial do sorteio produz com a mesma relação, o mesmo recorte e a mesma semente; a ampla
contém todos os inscritos, e cada reservada só os autodeclarados nela.

**Acceptance Scenarios**:

1. **Given** um marco cuja forma é sorteio, **When** o cartão é exibido, **Then** ele oferece "Simular
   sorteio", e não "Simular classificação" (FR-2477, FR-2478).
2. **Given** o painel aberto, **When** o elaborador o lê, **Then** a semente aparece no topo com o selo
   de fictícia e a frase de que no certame a semente será outra; não há campo para digitar semente
   (FR-2481, FR-2482, FR-2483).
3. **Given** o painel aberto, **When** o elaborador aperta "Sortear de novo", **Then** a semente é
   outra, gerada pelo sistema, e as ordens de todos os recortes são recalculadas com ela (FR-2484).
4. **Given** o painel aberto, **When** o elaborador muda a quantidade de inscritos de uma lista, **Then**
   a prévia recalcula **com a mesma semente**, e diz que a semente foi mantida para que a diferença
   seja efeito da mudança, e não da sorte (FR-2485).
5. **Given** o detalhe aberto na PPI, **When** o elaborador o lê, **Then** cada linha diz a posição da
   pessoa na ordem da PPI e a posição dela na ordem da ampla, e as duas são diferentes porque cada
   lista é sorteada à parte (FR-2493, FR-2494).
6. **Given** menos inscritos que vagas na ampla, **When** a prévia é calculada, **Then** todos recebem
   posição e o painel diz que o sistema sorteia mesmo assim, e que a posição importa para a ordem de
   chamada e para as listas de cota (FR-2496).
7. **Given** um Perfil sem Modalidade reservada, **When** o painel abre, **Then** há uma lista só, a
   ampla, sem seletor de recorte (FR-2492).

---

### User Story 2 — Ver, na rodada, quem ocuparia vaga em cada lista e o efeito da reversão (Priority: P1)

Na rodada exibida, dois autodeclarados PPI, Ana e Bruno, foram sorteados entre os 10 primeiros da
ampla. O bloco da ocupação, marcado como hipótese, diz: *"Ampla: 10 publicadas, 10 ocupadas. PPI: 3
publicadas, 1 ocupada, 2 sem ocupante. Ana e Bruno ocupariam pela ampla; a vaga reservada deles
continua sendo da PPI. A faixa da PPI, de 3 posições, alcançou os dois e a Carla; o Diego, 4º da PPI,
ficou fora da faixa. Este é o comportamento atual do sistema."* Como o Perfil declara reversão "A
quantidade que ficou sem preencher", o bloco acrescenta: *"A PPI cederia 2 vagas à ampla
concorrência deste Perfil."*

**Why this priority**: é a consequência que o elaborador não prevê. No sorteio ela é mais frequente que
na pontuação, porque a sorte espalha os autodeclarados pela ampla, e a faixa da reservada costuma ser
do tamanho das vagas.

**Independent Test**: para cada caso da matriz de equivalência, as quatro quantidades de cada recorte,
o conjunto dos que ocupariam pela ampla e as vagas cedidas são os que as funções oficiais produzem com
as mesmas ordens e as mesmas hipóteses.

**Acceptance Scenarios**:

1. **Given** dois autodeclarados PPI entre as 10 vagas da ampla, **When** a rodada é calculada, **Then**
   a ampla os conta como ocupantes, a PPI não, e o painel diz que a vaga reservada continua na PPI, sem
   mostrar movimento de vaga entre listas (FR-2497).
2. **Given** a situação da história, **When** o bloco é lido, **Then** ele diz quantas posições da faixa
   da PPI foram tomadas por quem ocupa pela ampla, quantos autodeclarados ficaram além dela, e que esse
   é o comportamento atual (FR-2498, FR-2507).
3. **Given** reversão "por saldo" declarada, **When** sobra vaga reservada sem ocupante, **Then** o
   bloco diz quantas a reservada cederia à ampla (FR-2499).
4. **Given** reversão "por esgotamento" e todos os autodeclarados da PPI ocupando pela ampla, **When**
   a rodada é calculada, **Then** o bloco diz que nada seria cedido e que esse é o comportamento atual
   (FR-2499, FR-2507).
5. **Given** nenhuma reversão declarada, **When** sobra vaga reservada, **Then** o bloco diz que o
   Edital não reverte e a vaga ficaria sem ocupante (FR-2499).
6. **Given** o marco sem regra de corte, **When** a prévia é calculada, **Then** as ordens aparecem, e o
   bloco da ocupação diz que sem corte não há faixa e o marco não chamaria ninguém, em vez de mostrar
   quantidades (FR-2500).

---

### User Story 3 — Ver o que acontece em muitas rodadas (Priority: P1)

Abaixo da rodada, um bloco *"Em 1.000 rodadas com esta população"* diz, por lista reservada: *"PPI:
sobrou ao menos uma vaga sem ocupante em 72% das rodadas; em média 2 autodeclarados ocuparam pela
ampla; com a reversão declarada, em média 1 vaga seria cedida à ampla."* E para a ampla: *"Em média,
3,4 das 10 vagas seriam ocupadas por autodeclarados."* (os números são os medidos pelo protótipo com
esta população — R-001 da [pesquisa](research.md).) O elaborador muda os
inscritos da PPI de 6 para 15 e vê a frequência mudar.

**Why this priority**: é a resposta à pergunta que o sorteio faz — com que frequência — e é o que
impede o elaborador de generalizar a partir da rodada que apareceu (D-002).

**Independent Test**: com a mesma semente exibida e a mesma população, o resumo é idêntico em duas
chamadas; e cada número do resumo é a agregação, rodada a rodada, do que a rodada detalhada mostraria
para a semente daquela rodada.

**Acceptance Scenarios**:

1. **Given** o painel aberto, **When** o elaborador lê o resumo, **Then** ele diz quantas rodadas foram
   feitas e que todas usam sementes fictícias derivadas da semente exibida (FR-2501, FR-2502).
2. **Given** a mesma semente e a mesma população, **When** o resumo é recalculado, **Then** os números
   são os mesmos (FR-2502).
3. **Given** "Sortear de novo", **When** a semente muda, **Then** o resumo também é recalculado, e a
   diferença entre os dois resumos é pequena — é a variação de amostragem, e não um resultado novo
   (FR-2502, SC-929).
4. **Given** um Perfil sem Modalidade reservada, **When** o resumo é lido, **Then** ele não fala de
   cotas: diz só que, na ampla, toda rodada ocupa as vagas até onde houver inscritos (FR-2503).
5. **Given** população com menos inscritos que vagas numa reservada, **When** o resumo é lido, **Then**
   ele diz que em 100% das rodadas sobra vaga, e quantas, sem chamar isso de probabilidade (FR-2503).

---

### User Story 4 — Informar quantos se inscrevem em cada lista (Priority: P2)

O painel mostra, acima da rodada, um número por lista: *"Só na ampla: 20 · PPI: 6 · PcD: 4"*, e a
frase *"A ampla será sorteada com os 30."* Os números vêm pré-preenchidos com uma sugestão. O
elaborador, que conhece a procura do curso, escreve 45 na ampla e 3 na PcD; a prévia recalcula com a
mesma semente.

**Why this priority**: sem notas, a procura por lista é a variável que decide se sobra vaga de cota
(D-003). P2 porque a sugestão já permite as histórias 1 a 3.

**Independent Test**: para quantidades informadas, a ampla tem a soma de todas as listas, cada
reservada tem a quantidade dela, e os nomes fictícios são estáveis entre recálculos.

**Acceptance Scenarios**:

1. **Given** o painel aberto pela primeira vez, **When** o elaborador o lê, **Then** cada lista tem uma
   quantidade sugerida, e o painel diz como ela foi sugerida (FR-2487).
2. **Given** uma quantidade alterada, **When** a prévia recalcula, **Then** a ampla passa a ter a nova
   soma, e as pessoas que já existiam mantêm o nome (FR-2488, FR-2490).
3. **Given** uma quantidade zero numa reservada, **When** a prévia recalcula, **Then** a lista diz que
   ninguém concorreu nela, que não seria sorteada nem apurada, e que a vaga dela não seria cedida
   à ampla, como comportamento atual (FR-2489).
4. **Given** quantidades cuja soma passa do limite, **When** o elaborador tenta recalcular, **Then** o
   painel diz o limite e não calcula (FR-2491).

---

### User Story 5 — No celular e com leitor de tela (Priority: P3)

As mesmas razões da história 5 da `094` e da história 6 da `095`: o painel é lido em celular por quem
compõe fora do escritório, e por leitor de tela.

**Why this priority**: herdada; as histórias 1 a 4 entregam valor sem ela.

**Independent Test**: a 375 px, trocar de lista, sortear de novo e mudar uma quantidade sem rolagem
horizontal da página; com leitor de tela, a semente, o selo de fictícia e o resumo são anunciados.

**Acceptance Scenarios**:

1. **Given** viewport de 375 px, **When** o elaborador sorteia de novo e troca de lista, **Then** a
   página não rola na horizontal (FR-2510).
2. **Given** leitor de tela, **When** a prévia é recalculada, **Then** a região do resultado anuncia que
   a semente mudou ou foi mantida (FR-2511).

---

### Edge Cases

- **Modalidade declarada como "Ampla concorrência"**: o sorteio oficial lhe dá lista própria (a
  derivação de `sorteios/application/previa.py`), e a ocupação não (a de `ocupacao`, que a prévia da
  `095` usa). A prévia segue a da ocupação e diz que não simula essa lista (D-005).
- **Reservada com zero inscritos**: a lista diz que ninguém concorreu. **Corrigido em 21/10/2026, na
  equivalência**: a primeira redação dizia que a reversão agiria sobre as vagas dela, e o caminho
  oficial não faz isso — a relação vazia é recusada (`relation_would_be_empty`), o corte e a apuração
  também, e nenhum movimento de vaga nasce. A prévia segue o oficial (FR-2489), e o achado está em
  [doc/achado-reservada-vazia-nao-reverte.md](../../doc/achado-reservada-vazia-nao-reverte.md).
- **Recorte sem linha no quadro de vagas**: a ocupação dele aparece como não avaliada, e não como zero
  vaga (como a FR-2322 da `095`).
- **Fonte de demonstração declarada no método** (só em desenvolvimento): a semente fictícia segue no
  formato da Loteria Federal, porque é o formato que o certame real terá.
- **Regra de normalização ainda não escolhida**: a prévia usa a da Loteria Federal (`DIGITOS_EM_SEQUENCIA`)
  e diz que supôs (D-007).
- **Ocorrência, data ou fonte do método ainda em branco**: a prévia calcula do mesmo jeito; o método
  completo é exigência da publicação, e não da prévia.
- **Mais de seis Modalidades reservadas**: o painel diz o limite e não calcula (como a FR-2343 da
  `095`).
- **Duas listas com as mesmas pessoas em ordens que parecem "erradas"**: a mesma pessoa em 1º na PPI e
  em 40º na ampla não é defeito; o painel explica que cada lista é sorteada à parte (FR-2494).
- **Recálculo concorrente de duas abas**: cada aba tem a sua semente; nenhuma afeta a outra, porque
  nada é gravado.

## Requirements *(mandatory)*

### Functional Requirements

#### Acesso

- **FR-2477**: O cartão de todo marco cuja forma de produção é **por sorteio** MUST oferecer o botão
  "Simular sorteio". Esta feature emenda a FR-2200 da `094`, que proibia botão em marco por sorteio.
- **FR-2478**: A prévia do sorteio MUST abrir no mesmo painel da `094`, fora do cartão, com a mesma
  jornada e o mesmo detalhe, e MUST NOT acrescentar ajuda visível ao cartão (FR-428 da `030`).
- **FR-2479**: A prévia do sorteio MUST existir só na composição do Edital, e MUST NOT ser oferecida na
  Retificação nem em tela alguma de condução do certame.
- **FR-2480**: Na jornada, o marco por sorteio MUST deixar de aparecer como "não simulado" (FR-2251 e
  FR-2254 da `094`): quando ele é o marco simulado, mostra o resultado; quando outro marco é o
  simulado, diz que o sorteio tem prévia própria no cartão dele.

#### A semente fictícia

- **FR-2481**: A semente de toda prévia MUST ser gerada pelo sistema, com aleatoriedade do servidor, no
  formato do material da Loteria Federal — cinco números de seis dígitos —, e normalizada pela regra
  declarada no método (D-007).
- **FR-2482**: O painel MUST exibir a semente no topo com o selo "semente fictícia", e a frase de que
  no certame a semente sairá do concurso declarado no Edital e a ordem será outra.
- **FR-2483**: A prévia MUST NOT oferecer campo, parâmetro ou caminho para informar semente, e o
  servidor MUST recusar semente que ele mesmo não tenha gerado para aquela prévia (D-001).
- **FR-2484**: "Sortear de novo" MUST gerar semente nova e recalcular a rodada e o resumo com ela.
- **FR-2485**: Mudar quantidade de inscritos, trocar de lista ou mudar o cartão e recalcular MUST manter
  a semente, e o painel MUST dizer que a manteve (D-006).
- **FR-2486**: Nenhuma semente da prévia MUST ser gravada, registrada em trilha ou exibida fora do
  painel.

#### A população

- **FR-2487**: O painel MUST oferecer uma quantidade por lista — "só na ampla" e uma por Modalidade
  reservada —, pré-preenchida com o dobro das vagas publicadas na linha de cada lista, e dez para a
  linha sem quantidade, e MUST dizer como sugeriu.
- **FR-2488**: A ampla MUST ser sorteada com a soma de todas as quantidades, e cada reservada só com os
  autodeclarados nela; o painel MUST dizer a soma com que a ampla é sorteada.
- **FR-2489**: Quantidade zero numa reservada MUST ser aceita, e a lista MUST dizer que ninguém concorreu
  nela na população fictícia. Como no caminho oficial, a lista vazia MUST NOT ser sorteada, cortada nem
  apurada — o sistema recusa a relação vazia —, e o painel MUST dizer que, por isso, a vaga dela fica
  sem ocupante e não é cedida à ampla, como comportamento atual ([achado de
  21/10](../../doc/achado-reservada-vazia-nao-reverte.md)).
- **FR-2490**: Os candidatos MUST ser fictícios e identificados como tal, com nomes estáveis entre
  recálculos: a pessoa que existia antes de uma mudança de quantidade mantém o nome e a Modalidade.
- **FR-2491**: A soma das quantidades MUST ter limite de 600 candidatos fictícios, o mesmo teto da
  população da `094`; acima dele, o painel MUST dizer o limite e não calcular.

#### A ordem de cada lista

- **FR-2492**: Os recortes MUST ser os da derivação oficial da ocupação (FR-2301 da `095`): a ampla, sem
  lista, e cada Modalidade reservada, na ordem declarada; a Modalidade apontada como ampla MUST NOT
  virar recorte reservado (D-005).
- **FR-2493**: A ordem de cada recorte MUST ser a do algoritmo publicado no método — hoje o
  IFES-SORTEIO-SHA256-v1 —, calculada pela mesma função que o sorteio oficial usa, sobre uma relação
  fictícia numerada como a oficial (de 1 a N, na ordem das inscrições fictícias) e com a identidade do
  recorte que o sorteio oficial usaria.
- **FR-2494**: O detalhe de cada reservada MUST mostrar, por pessoa, a posição na reservada e a posição
  na ampla, e o painel MUST dizer, uma vez, que cada lista é sorteada à parte e que posições diferentes
  são o esperado.
- **FR-2495**: O corte de cada recorte MUST ser o da regra declarada no cartão, pela mesma função da
  `094`. Como o sorteio não empata, a prévia do sorteio MUST NOT mostrar bloco de empate.
- **FR-2496**: Com menos inscritos que vagas num recorte, a prévia MUST sortear e dar posição a todos, e
  MUST dizer que o sistema sorteia mesmo assim.

#### A ocupação na rodada

- **FR-2497**: A rodada MUST mostrar, por recorte, as quatro quantidades da apuração — publicadas,
  efetivas, ocupadas, faltando — e quem ocuparia pela ampla, pelas funções oficiais da `095`, num bloco
  marcado como hipótese, com as hipóteses da FR-2320 da `095`: todos habilitados, nenhuma chamada,
  desistência ou movimento anterior, uma rodada só.
- **FR-2498**: Para cada reservada, o bloco MUST dizer quantas posições da faixa foram tomadas por quem
  ocupa pela ampla e quantos autodeclarados com posição ficaram além dela, e que alcançá-los seria uma
  faixa seguinte, que a prévia não simula.
- **FR-2499**: O bloco MUST dizer o efeito da reversão declarada no Perfil — quantas vagas cada
  reservada cederia à ampla —, ou que o Edital não reverte, quando não há declaração.
- **FR-2500**: Sem regra de corte no marco, o bloco da ocupação MUST dizer que não há faixa e que o
  marco não chamaria ninguém, e MUST NOT mostrar quantidades.

#### O resumo de muitas rodadas

- **FR-2501**: O painel MUST mostrar, abaixo da rodada, o resumo de 1.000 rodadas com a mesma população
  e as mesmas regras, e MUST dizer quantas rodadas fez. Se o plano medir que 1.000 não cabem no tempo
  da SC-928, o número MAY ser menor, nunca abaixo de 200, e o painel diz o número que usou.
- **FR-2502**: As sementes das rodadas do resumo MUST ser derivadas da semente exibida, de modo que a
  mesma semente e a mesma população produzam o mesmo resumo (D-006).
- **FR-2503**: Para cada reservada, o resumo MUST dizer: em quantas rodadas sobrou ao menos uma vaga sem
  ocupante, em porcentagem; a média de vagas sem ocupante; a média de autodeclarados que ocuparam pela
  ampla; e, com reversão declarada, a média de vagas cedidas e em quantas rodadas houve cessão. Para a
  ampla, a média de vagas ocupadas por autodeclarados. Quando o resultado é o mesmo em todas as
  rodadas, MUST dizer isso, e não uma porcentagem.
- **FR-2504**: Os números do resumo MUST ser a agregação do que a rodada detalhada mostraria para cada
  uma das sementes derivadas, pelas mesmas funções, sem atalho de cálculo próprio.
- **FR-2505**: O resumo MUST dizer que as frequências são da população fictícia informada e que mudam
  com ela, e MUST NOT ser apresentado como previsão do certame.

#### Linguagem e honestidade

- **FR-2506**: O painel MUST dizer o que a prévia do sorteio simula e o que não — convocação, aceite,
  desistência, indeferimento, faixa seguinte, encadeamento de marcos, Etapa de habilitação antes do
  sorteio — e MUST NOT afirmar que o certame foi simulado.
- **FR-2507**: Onde a prévia mostrar o comportamento registrado como pendente de decisão nas DP-1 e DP-2
  da `095`, o painel MUST descrevê-lo como comportamento atual, na forma da FR-2337 da `095`, e esta
  feature MUST NOT alterar a regra.
- **FR-2508**: A prévia MUST usar o vocabulário da `094` e da `095` — "avançariam", "ocuparia pela
  ampla", "sem ocupante", "cederia" — e "sortear", "sorteado" e "posição sorteada" para o que é do
  sorteio.

#### Sem efeito

- **FR-2509**: Abrir, recalcular, sortear de novo, trocar de lista, mudar quantidade e fechar a prévia
  MUST NOT gravar nada: nenhuma relação, ocorrência, semente, ordem, corte, apuração, movimento, evento
  de trilha, alteração de rascunho ou candidato fictício.

#### Acessibilidade e política de conteúdo

- **FR-2510**: O painel MUST caber em 375 px sem rolagem horizontal da página, com as tabelas largas em
  moldura que rola, como a `094`.
- **FR-2511**: A região do resultado MUST anunciar a leitores de tela que a prévia foi recalculada, e se
  a semente mudou ou foi mantida.
- **FR-2512**: Estilo e comportamento MUST viver em arquivos estáticos, sem estilo nem script embutido no
  template (CSP da `091`).

### Key Entities

- **Semente fictícia**: material no formato da Loteria Federal, gerado pelo servidor para uma prévia,
  normalizado pela regra do método; vive só na resposta e no formulário do painel, com prova de que foi
  o servidor que a gerou. Nunca é gravada.
- **População informada**: uma quantidade por lista, com a soma como universo da ampla; os candidatos
  fictícios que ela gera têm nome, Modalidade e número público estáveis entre recálculos.
- **Rodada**: a ordem de cada recorte para uma semente, o corte de cada um, e a ocupação numa rodada
  com a reversão declarada.
- **Resumo das rodadas**: a agregação, por recorte, de N rodadas com sementes derivadas da semente
  exibida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-925**: No roteiro de compreensão, ao menos 4 de cada 5 elaboradores respondem, olhando só a
  prévia de um marco por sorteio com PPI: se o autodeclarado PPI concorre também na ampla; se a vaga de
  PPI dele continua reservada quando ele entra pela ampla; e se, com a população mostrada, sobrar vaga
  de PPI sem ocupante é raro ou comum.
- **SC-926**: Ao menos 4 de cada 5 elaboradores dizem, sem ajuda, que a semente exibida não é a do
  certame e que a ordem real será outra.
- **SC-927**: Em 100% dos casos da matriz de equivalência, a ordem de cada recorte, as quatro
  quantidades, quem ocupa pela ampla e as vagas cedidas da rodada são iguais às do caminho oficial com a
  mesma relação, a mesma semente e as mesmas hipóteses.
- **SC-928**: Com até 500 candidatos fictícios e até seis reservadas, a rodada aparece em até 1 segundo
  depois de uma alteração, e o resumo completo em até 5 segundos.
- **SC-929**: Para uma mesma população, os resumos de duas sementes diferentes diferem, em cada
  porcentagem, em no máximo 5 pontos percentuais em ao menos 95% das execuções da matriz.
- **SC-930**: Em qualquer sequência de aberturas, recálculos e sorteios de novo, o banco recebe zero
  escritas e a trilha zero eventos.
- **SC-931**: Nenhuma requisição com semente forjada produz prévia: 100% são recusadas.

## Assumptions

- **A sugestão de população é o dobro das vagas de cada linha.** É um ponto de partida que já produz
  concorrência em toda lista; o elaborador a troca pela procura que conhece. O plano pode propor outra,
  desde que diga como sugeriu (FR-2487).
- **Todos habilitados.** Onde o Edital declara Etapa de habilitação antes do sorteio, a prévia supõe
  todos habilitados, como a decisão 006 da `094`, e diz que supõe.
- **O orçamento cabe.** A ordem de 500 números custa 0,9 ms (medido em 21/10/2026), e o protótipo do
  plano mediu a rodada inteira, com ocupação, em 1,6 ms e as 1.000 rodadas em 1,39 s, no pior caso da
  SC-928 (R-003 da [pesquisa](research.md)). A cláusula da FR-2501 que admite reduzir as rodadas fica
  como salvaguarda.
- **A margem da SC-929 é de amostragem.** Com 1.000 rodadas, o erro padrão de uma proporção é de no
  máximo ~1,6 ponto, e o da diferença entre dois resumos independentes, ~2,2 pontos; 5 pontos cobrem
  ~97% dos pares, o que deixa a meta de 95% com folga.
- **O algoritmo é um só.** O vocabulário de algoritmos tem hoje um elemento; se nascer outro, a prévia
  usa o declarado no método.

## Decisões

### D-001 — A semente é gerada pelo sistema, só leitura, e anunciada como fictícia

Decisão do usuário de 21/10/2026. O sistema gera uma semente nova a cada "Sortear de novo" e a exibe com
o selo de fictícia; ninguém a digita. É o que preserva ao pé da letra a FR-030 da `021` — nenhuma
simulação da ordem depois de conhecida a semente —: sem campo de semente, não há como a prévia receber
a do certame. As alternativas recusadas foram a semente digitável, que abre a dúvida *"e se eu digitar
os números reais?"*, e a semente fixa por Perfil, que esconde que o resultado depende da sorte.

O servidor recusar semente que não gerou (FR-2483) é a consequência técnica: um campo oculto do
formulário é um campo, e sem a prova de origem a decisão valeria só na tela.

### D-002 — Uma rodada em detalhe e o resumo de muitas

Decisão do usuário de 21/10/2026. Uma rodada só pode enganar: sobrar vaga de cota no sorteio depende
da sorte, e o elaborador generalizaria de um caso. O resumo de muitas rodadas responde à pergunta que o
sorteio faz — com que frequência. O custo é de tempo, e por isso a SC-928 tem orçamento próprio e a
FR-2501 admite menos rodadas, dizendo quantas.

### D-003 — A população é informada pelo elaborador, por lista

Decisão do usuário de 21/10/2026. Sem notas, a procura por lista é o que decide se sobra vaga de cota,
e uma população derivada das vagas, como a da `095`, esconderia justamente essa variável. Os campos
ficam no painel, fora do cartão, e por isso não esbarram na FR-428 da `030`. A alternativa automática,
com ou sem ajuste opcional, foi recusada.

### D-004 — Convocação, desistência, indeferimento e faixa seguinte ficam fora

Decisão do usuário de 21/10/2026, igual ao recorte da `095`. A convocação da `019` não tem as regras em
funções puras, e simular quem é chamado no lugar de quem não ocupa pede o encadeamento da faixa
seguinte, que a `095` também deixou de fora. É o próximo passo natural — o sorteio costuma vir antes da
análise documental, e o indeferimento é o caso típico —, e fica registrado aqui para a spec que o
fizer.

### D-005 — Os recortes são os da ocupação, e a lista da Modalidade declarada como ampla fica de fora

Decisão desta spec. Existem duas derivações dos recortes de um marco, medidas pela `034`: a do sorteio,
que dá lista própria à Modalidade declarada como "Ampla concorrência", e a da ocupação, que não dá,
porque a quantidade dela mora na linha geral. A prévia precisa da ocupação, e a ocupação só consome os
recortes dela; simular a lista extra produziria uma ordem que não leva a vaga nenhuma. A prévia segue
a derivação da ocupação e diz que não simula essa lista. **A divergência entre as duas derivações não é
resolvida aqui**: ela é do sorteio oficial, e a decisão é do usuário.

### D-006 — A semente fica até alguém pedir outra, e o resumo deriva dela

Decisão desta spec. Se mudar a quantidade de uma lista também trocasse a semente, o elaborador não
saberia separar o efeito da mudança do efeito da sorte. Por isso só "Sortear de novo" troca a semente
(FR-2485). E as sementes do resumo derivam da exibida (FR-2502), o que torna o resumo reproduzível:
mesma semente e mesma população, mesmo resumo — o que os testes de equivalência precisam.

### D-007 — A semente fictícia tem o formato da fonte real, e a regra declarada a normaliza

Decisão desta spec. A semente exibida tem a forma do material da Loteria Federal — cinco números de seis
dígitos —, e passa pela regra de normalização do método, como a real passará. Assim, a prévia ensina
também o que acontece no dia: *"estes cinco números viram a semente"*. Sem regra escolhida, a prévia
supõe `DIGITOS_EM_SEQUENCIA`, a da Loteria Federal, e diz que supôs.

### D-008 — Esta spec emenda três requisitos da `094`

A FR-2200 da `094` proíbe o botão em marco por sorteio, e a FR-2251 e a FR-2254 dizem que o sorteio
não é simulado. Esta feature os supera (FR-2477, FR-2480), por decisão do usuário de 21/10/2026, que
revê a decisão 007 da `094`. A `094` está na `main`; a emenda daqueles três requisitos, com a redação
anterior registrada, é feita no mesmo PR que implementar esta spec.

## Pendências do usuário

- **A frase do "Como preencher" do marco** (`_como_preencher_o_marco.html`) sugere que cada pessoa
  concorre em uma lista só. Corrigi-la é texto de composição, e não desta prévia.
- **A lista reservada vazia não reverte**, nem "por saldo" ([achado de
  21/10](../../doc/achado-reservada-vazia-nao-reverte.md)): é o caso mais comum de vaga reservada não
  preenchida, e os Editais 28/2026 e 57/2026 mandam reverter. A prévia mostra o comportamento atual.
- **As DP-1 e DP-2 da `095`** continuam abertas; a prévia do sorteio as torna mais visíveis, porque o
  resumo mostra com que frequência acontecem.
- **A divergência das derivações de recortes** (D-005) continua no sorteio oficial.
