# Feature Specification: Prévia interativa da classificação — fatia 1

**Feature Branch**: `claude/094-previa-da-classificacao`, sobre a `main` em `745f115f`

**Created**: 2026-10-19

**Status**: Especificada — spec, plan, tasks e protótipo no PR; implementação não iniciada. O merge é
do usuário.

**Input**: decisão do usuário de 19/10/2026, a partir de uma sessão real em que um elaborador não
conseguiu prever o efeito das regras de corte da etapa Classificação, e do achado
[`doc/achado-empate-estrito-tem-tres-leituras.md`](../../doc/achado-empate-estrito-tem-tres-leituras.md)
(PR vitofranzosi/processo_seletivo#315, aberto quando esta spec foi escrita). O achado é referência
obrigatória: esta spec mostra o que o motor faz, e não decide nenhuma das leituras que ele deixou em
aberto.

> **Faixa de identificadores.** Esta spec abre em **FR-2200** e **SC-840**. A `093` (PR #311, aberto)
> vai até o 2160 da faixa de requisitos e o 829 da de critérios — sem o prefixo aqui, porque ela ainda
> não está na `main` e a varredura de citações não a vê. Nenhuma branch aberta usava `094` nem número
> acima desses, conferido em `git ls-tree` e `git grep` de todas as branches remotas em 19/10/2026.

---

## Por que esta feature existe

**O elaborador declara a regra e só descobre o efeito com o certame andando.** O cartão do marco
pergunta pesos, arredondamento, critérios de desempate, alvo, suplentes, desfecho do empate, Etapa
governada e continuação — e nada na tela mostra o que essas respostas fazem com pessoas concretas. A
publicação aceita qualquer combinação válida, e a consequência aparece no dia de emitir a ordem, o
corte ou a apuração: com o Edital publicado, quando corrigir exige Retificação.

**O achado de 19/10 mostrou que nem quem acompanha o desenvolvimento acerta.** Três fatos dele
governam esta spec:

1. **O rótulo, o documento e o motor divergem.** Para `STRICT`, a tela diz *"A faixa para no alvo"*, o
   documento diz *"esse número não é ultrapassado"*, e o motor **recusa a emissão** do corte
   (`FR-195` da `014`).
2. **A recusa é na última posição de alvo + suplentes**, e não na do alvo (`FR-180`, `FR-181` da
   `014`). Com 10 + 5, o empate que importa é o da 15ª posição.
3. **A apuração da ocupação tem uma segunda recusa**, `EmpateNaFronteiraDoAlvo` (`R-002` da `019`), na
   fronteira das **vagas efetivas**, qualquer que seja o desfecho declarado — e nenhum texto a
   declara. Um empate na 10ª posição com 10 vagas deixa o corte sair e para a apuração.

**A resposta é deixar o elaborador ver.** Um botão no cartão abre, ao lado, uma prévia com candidatos
fictícios, calculada pelo mesmo motor que emite a ordem e o corte: quem ficou em que posição, por quê,
se alcança o corte e se progride à Etapa seguinte. Altera-se um campo, e a prévia se recalcula sobre o
que está digitado, sem gravar nada.

**Critério de sucesso do usuário**: o elaborador altera uma configuração e vê de imediato, com
candidatos fictícios, por que cada pessoa ficou naquela posição, se alcança o corte e se progride à
próxima etapa.

### O que a fatia 1 cobre, e o que fica para depois

| Fatia 1 (esta spec) | Fora da fatia 1 |
|---|---|
| Marco que ordena **pela pontuação**: Etapas enumeradas, pesos, operação, normalização, arredondamento | Marco que ordena **por sorteio** — registrado em D-007 |
| Critérios de desempate sucessivos, com valor ausente declarado | Recortes: ampla como universo inteiro, Modalidades reservadas, PPI, PcD (fatia 2) |
| Posições compartilhadas no empate residual | Concomitância (`FR-252` da `016`), que vale sempre e não se configura (fatia 2) |
| Regra de corte: alvo fixo ou do quadro, suplentes, desfecho, Etapa governada, continuação | Ocupação além do aviso de fronteira, movimentos, reversão declarada (fatia 2) |
| O aviso de que a apuração das vagas pararia num empate na fronteira das vagas | Retificação de Edital publicado — registrado em D-009 |

A fatia 2 é do mesmo produto, e a arquitetura desta fatia precisa admiti-la sem reescrita (D-008).

**O que não muda, e não se negocia aqui:** nenhuma regra de classificação, corte, ocupação ou
publicação. Nenhum rótulo existente do cartão, nenhuma frase do documento publicado. Nenhum ato,
nenhum evento de trilha, nenhuma gravação. O resultado oficial de toda ordem, corte e apuração —
inclusive do acervo — é o mesmo antes e depois desta feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Ver por que cada pessoa ficou onde ficou (Priority: P1)

O elaborador compõe o marco "Classificação final" do Perfil "Professor de Matemática": Prova Escrita e
Prova de Títulos, soma ponderada, dois critérios de desempate. No cartão, ele aperta "Simular
classificação". Ao lado do cartão abre um painel com candidatos fictícios — identificados como
fictícios —, cada um com as notas por Etapa, a pontuação combinada, a posição e uma frase que diz
**por que** ele está ali: pontuação distinta de todas; empatou na pontuação e o 1º critério o separou,
com os valores comparados; empatou em tudo e divide a posição; ou não tem posição, e por quê.

**Why this priority**: é o núcleo do critério de sucesso. Sem a explicação por linha, a prévia vira
mais uma tabela que o elaborador precisa interpretar sozinho — que é o problema de hoje.

**Independent Test**: com um marco por pontuação válido e qualquer cenário, o painel lista os
candidatos fictícios com posição, pontuação combinada na escala publicada e uma frase de motivo
por linha; a ordem e as posições são idênticas às que o caminho oficial produz com os mesmos dados.

**Acceptance Scenarios**:

1. **Given** um marco por pontuação com Etapas e arredondamento declarados, **When** o elaborador
   aperta "Simular classificação", **Then** o painel abre fora do cartão, nomeia o Perfil e o marco, e
   lista os candidatos fictícios do cenário padrão em ordem, cada um com o motivo da posição.
2. **Given** dois candidatos com a mesma pontuação combinada e um critério que os separa, **When** a
   prévia é calculada, **Then** a linha de cada um diz qual critério os separou, com o valor de cada
   um, e as posições são consecutivas.
3. **Given** dois candidatos iguais na pontuação e em todos os critérios declarados, **When** a prévia
   é calculada, **Then** os dois aparecem na mesma posição (por exemplo, 10ª e 10ª), a linha diz que
   nenhum critério declarado os separa e que o sistema não escolhe entre eles, e o candidato seguinte
   aparece na 12ª.
4. **Given** um candidato fictício sem nota numa Etapa enumerada, **When** a prévia é calculada,
   **Then** ele aparece sem posição, com o motivo nomeando a Etapa, e não com nota zero.
5. **Given** um critério com valor ausente declarado como "último no critério", e um candidato sem o
   fato que ele consome, **When** a prévia é calculada, **Then** a linha diz que ele ficou atrás
   naquele critério por não ter o valor.

---

### User Story 2 — Ver se alcança o corte e se progride, inclusive quando o corte não sai (Priority: P1)

Com a regra de corte declarada — alvo 10, 5 suplentes, Etapa governada "Entrevista" —, o painel mostra,
para cada candidato, a situação no corte (dentro do alvo, suplente, além do alvo por empate, fora da
faixa, sem posição) e a consequência para a Entrevista. Quando o empate atravessa a última posição da
faixa sob `STRICT`, o painel diz que **o corte não seria emitido**, em que posição e com quantos
empatados — como resultado da regra, e não como erro de preenchimento. Quando um empate cai na
fronteira das vagas, o painel avisa que **a apuração da ocupação pararia ali**, mesmo com o corte
saindo.

**Why this priority**: é o que o achado mostrou que ninguém prevê. A prévia que pintasse tudo de verde
num caso em que o motor recusa seria pior do que nenhuma prévia.

**Independent Test**: para cada linha da tabela de reprodução do achado (alvo 10, com e sem 5
suplentes, empate na 10ª ou na 15ª, `ADMITS_SURPLUS` e `STRICT`), o painel mostra o mesmo desfecho que
`faixa.calcular` e a apuração produzem com os mesmos dados.

**Acceptance Scenarios**:

1. **Given** alvo 10 sem suplentes, empate residual de dois na 10ª e `ADMITS_SURPLUS`, **When** a prévia
   é calculada, **Then** 11 progridem; os dois empatados aparecem com a mesma marca — empate na última
   posição da faixa, todos progridem pelo desfecho —, o resumo diz que 1 entrou além da faixa, e o
   painel avisa que a apuração das vagas pararia na posição 10, se as vagas forem 10.
2. **Given** a mesma configuração com `STRICT`, **When** a prévia é calculada, **Then** o painel diz que
   o corte não seria emitido, por empate residual de dois na 10ª posição, e que ninguém progride até
   que o desempate seja julgado ou o desfecho retificado; nenhuma linha aparece como "progride".
3. **Given** alvo 10 com 5 suplentes, empate de dois na 10ª, e qualquer desfecho, **When** a prévia é
   calculada, **Then** o corte sai com 15, nenhum por empate, e o aviso da fronteira das vagas aparece
   na posição 10.
4. **Given** alvo 10 com 5 suplentes, empate de dois na 15ª e `STRICT`, **When** a prévia é calculada,
   **Then** o painel diz que o corte não seria emitido, na posição 15 — a última da faixa, e não a do
   alvo.
5. **Given** um corte com Etapa governada "Entrevista" e continuação admitida, **When** a prévia é
   calculada, **Then** quem está na faixa aparece "progride para a Entrevista", e quem está fora
   aparece "não progride nesta faixa; o Edital admite faixa seguinte"; com continuação não admitida,
   "não progride; o Edital não admite faixa seguinte".
6. **Given** um marco que declara não governar Etapa alguma, **When** a prévia é calculada, **Then**
   quem está na faixa aparece "dentro da faixa; este corte não alimenta Etapa".
7. **Given** um marco sem regra de corte, **When** a prévia é calculada, **Then** o painel mostra a
   ordem e diz que o marco não corta: ninguém é excluído da Etapa seguinte por ele.

---

### User Story 3 — Mudar um campo e ver o efeito sem salvar (Priority: P2)

O elaborador troca o desfecho do empate de `ADMITS_SURPLUS` para `STRICT` no cartão, sem gravar. O painel
se recalcula sobre o que está digitado, com os mesmos candidatos fictícios, e passa a mostrar o corte
recusado. Ele acrescenta um critério de desempate, e o empate residual se desfaz. Nada foi salvo: o
rascunho, os atos e a trilha não mudaram.

**Why this priority**: é o que transforma a tabela em ferramenta de decisão. P2 porque as histórias 1 e
2, abertas sobre o que está digitado no momento do clique, já entregam valor.

**Independent Test**: com o painel aberto, alterar cada campo do marco que a prévia lê produz um novo
cálculo sobre o digitado; o banco não recebe nenhuma escrita, e a página não perde o que foi digitado.

**Acceptance Scenarios**:

1. **Given** o painel aberto, **When** o elaborador altera operação, normalização, escala, modo,
   Etapas enumeradas, critérios, valor ausente, espécie do alvo, alvo, suplentes, desfecho, Etapa
   governada ou continuação — os campos do cartão —, **Then** o painel se recalcula sobre o valor
   digitado, sem gravar. O peso não está na lista: é campo do passo Etapas, lido do gravado.
2. **Given** o painel aberto num cenário, **When** o elaborador altera um campo que não define
   fronteira (operação, critérios, desfecho, Etapa governada, continuação), **Then** os candidatos
   fictícios são os mesmos de antes, e só o resultado muda.
3. **Given** o painel aberto, **When** o elaborador altera alvo, suplentes ou espécie do alvo,
   **Then** o painel diz que o cenário foi reposicionado sobre a nova fronteira (D-003).
4. **Given** um campo apagado no meio da digitação (alvo vazio, por exemplo), **When** a prévia é
   pedida, **Then** o painel diz o que falta para calcular, e não mostra um resultado inventado.
5. **Given** uma série de aberturas e recálculos, **When** se conferem as tabelas do banco e a trilha,
   **Then** nada foi gravado.

---

### User Story 4 — Escolher um cenário predefinido (Priority: P2)

Dentro do painel, o elaborador escolhe entre cenários predefinidos: classificação sem empate,
desempate por critérios sucessivos, corte impedido por empate na última posição da faixa, empate na
fronteira das vagas, e valor ausente. Cada cenário diz o que foi construído para mostrar e, quando a
configuração digitada desfaz a situação, diz que ela não ocorre e por quê.

**Why this priority**: sem cenários, a prévia só mostra o caso feliz, e o elaborador não encontra os
casos que o achado descreve. P2 porque o cenário padrão já entrega as histórias 1 e 2.

**Independent Test**: cada cenário, com a configuração de referência dele, produz a situação que o
nomeia; com outra configuração, o painel diz se a situação ocorre ou não.

**Acceptance Scenarios**:

1. **Given** o cenário "Empate na última posição da faixa", alvo 10 e 5 suplentes, **When** o desfecho é
   `STRICT`, **Then** o painel mostra o corte impedido na 15ª; com `ADMITS_SURPLUS`, 16 progridem.
2. **Given** o cenário "Desempate por critérios sucessivos" e os critérios "maior pontuação na Prova
   Escrita", "menor data de nascimento" e "maior tempo de serviço", **When** a prévia é calculada,
   **Then** três candidatos empatam na pontuação, qualquer que seja o peso; o 1º critério não os separa
   (notas iguais), o 2º separa um deles, o 3º separa os outros dois, e cada linha diz qual critério agiu
   e qual não agiu, com os valores.
3. **Given** o mesmo cenário num marco cujos critérios só comparam pontuação de Etapa, **When** a
   prévia é calculada, **Then** os três dividem a mesma posição, e a linha de cada um diz que nenhum
   critério declarado os separa porque as notas são iguais.
4. **Given** o cenário "Empate na fronteira das vagas", **When** o corte sai, **Then** o aviso de que a
   apuração pararia aparece, com a posição e o tamanho do empate, qualquer que seja o desfecho.
5. **Given** o cenário "Classificação sem empate", **When** a prévia é calculada, **Then** nenhum aviso
   aparece, e o painel diz explicitamente que não houve empate em fronteira nenhuma.

---

### User Story 5 — No celular e com leitor de tela (Priority: P3)

A 375 px, o mesmo botão abre a prévia ocupando a tela, com um botão de fechar que devolve ao cartão.
Com leitor de tela, o botão anuncia o que abre, o painel tem nome, e o recálculo anuncia o resumo novo
sem reler a tabela inteira.

**Why this priority**: a composição é feita sobretudo no desktop, mas a gestão já é usada no celular
(`076` a `092`), e um painel lateral sem adaptação quebraria a página estreita.

**Independent Test**: a 375 px, abrir, recalcular, trocar cenário e fechar sem rolagem horizontal da
página; com leitor de tela, o painel é região nomeada e o resumo é anunciado.

**Acceptance Scenarios**:

1. **Given** a etapa Classificação a 375 px, **When** o elaborador aperta "Simular classificação",
   **Then** o painel ocupa a largura da tela, a tabela rola dentro dele se precisar, e a página não
   rola na horizontal.
2. **Given** o painel aberto no celular, **When** o elaborador fecha, **Then** o foco volta ao botão do
   cartão que o abriu.
3. **Given** o leitor de tela, **When** o painel se recalcula, **Then** o resumo novo (quantos
   progridem, se o corte sai, se há aviso) é anunciado uma vez.

---

### Edge Cases

- **Marco por sorteio, ou forma ainda não escolhida**: o botão não aparece no cartão (D-007).
- **Marco sem Etapa enumerada, ou só com Etapas decisórias**: só com portas, a pontuação é nula para
  todos e a ordem nasce dos critérios (`FR-077`, `FR-078` da `015`); a prévia mostra isso. Sem Etapa
  nenhuma, diz que o marco por pontuação precisa de ao menos uma.
- **Declaração incompleta que o motor exige** — escala ou modo do arredondamento, peso de Etapa
  enumerada, divisor zero: o painel nomeia o que falta e não calcula. O motor recusa esses casos com
  `RegraIncompleta`, e a prévia mostra a recusa, e não um padrão.
- **Desfecho do empate não declarado**: o motor não tem padrão (`FR-182` da `014`). Quando nenhum empate
  atravessa a faixa, o desfecho não importa e o painel diz isso; quando atravessa, o painel mostra as
  duas consequências, uma por desfecho, e diz que sem a declaração o Edital não publica.
- **Critério sem valor ausente declarado, num cenário em que algum candidato não tem o valor**: o painel
  diz que a declaração falta e não presume nenhuma das duas.
- **Critério que aponta Etapa não enumerada, ou fato não declarado no Perfil**: o motor lê valor
  ausente para todos; a prévia mostra o critério sem efeito, e diz por quê.
- **Alvo do quadro, sem linha geral no quadro do Perfil**: a prévia mostra a ordem, diz que o alvo não é
  apurável, e não lê ausência como zero (`FR-183` da `014`).
- **Alvo zero, ou alvo maior que o número de classificáveis**: zero não faz ninguém progredir; maior faz
  todos os classificáveis progredirem, e o painel diz que a faixa não se completa.
- **Faixa grande** (alvo do quadro de centenas): a tabela agrupa os trechos sem nada a dizer — "posições
  4 a 37: 34 candidatos com pontuações distintas, dentro do alvo" — e mostra por inteiro as linhas
  próximas de cada fronteira e as que têm empate ou não têm posição.
- **Mais Etapas enumeradas do que o cenário define notas**: o cenário tem notas para até quatro Etapas
  não decisórias; acima disso o painel diz que a prévia cobre até quatro, e não calcula (R-006).
- **Sem quadro de vagas no Perfil**: o aviso da fronteira das vagas não é avaliado, e o painel diz isso
  em vez de omitir.
- **Dois marcos no mesmo Perfil**: cada cartão tem o seu botão; o painel mostra um marco por vez e
  nomeia qual.
- **Marco ainda não gravado**: a prévia funciona sobre o digitado, como a recomposição do cartão.
- **Sessão expirada ou Edital fora do escopo**: a mesma negativa dos demais fragmentos da composição;
  nenhuma leitura de Edital alheio.
- **Rascunho local (053)**: abrir a prévia não altera o rascunho local nem o gravado.

## Requirements *(mandatory)*

### Functional Requirements

#### Acesso

- **FR-2200**: O cartão de todo marco cuja forma de produção é **pela pontuação** MUST oferecer o botão
  "Simular classificação". O botão MUST NOT aparecer em marco por sorteio nem em marco sem forma
  escolhida.
- **FR-2201**: A prévia MUST abrir num painel **fora do cartão**, contextual ao marco que a pediu, que
  nomeia o Perfil e o marco. O cartão MUST NOT ganhar texto de ajuda visível por causa desta feature:
  o botão é controle, e o resultado mora fora do cartão (D-001, `FR-428` da `030`).
- **FR-2202**: No desktop, o painel MUST ficar ao lado da composição, sem cobrir o cartão que o abriu.
  Na largura estreita, MUST ocupar a largura da tela, com botão de fechar. Em nenhuma largura a página
  MUST rolar na horizontal por causa do painel.
- **FR-2203**: Um painel por vez: pedir a prévia de outro marco MUST substituir o conteúdo e o nome. Fechar
  MUST devolver o foco ao botão que o abriu.

#### Os candidatos fictícios

- **FR-2204**: Os candidatos da prévia MUST ser fictícios, gerados por cenário, e MUST ser identificados
  como fictícios no painel. A prévia MUST NOT ler, exibir nem derivar dado de inscrição real.
- **FR-2205**: Para os mesmos cenário, Etapas enumeradas, fatos declarados do Perfil, alvo, suplentes e
  vagas, os candidatos fictícios MUST ser os mesmos — determinísticos, sem acaso. Alterar pesos,
  operação, arredondamento, critérios, desfecho, Etapa governada ou continuação MUST NOT alterá-los
  (D-003).
- **FR-2206**: Quando alvo, suplentes ou vagas mudam, o cenário MUST ser reposicionado sobre a nova
  fronteira, e o painel MUST dizer que foi.

#### O que cada linha diz

- **FR-2207**: Cada linha MUST mostrar a posição, o candidato fictício, as notas por Etapa enumerada, a
  pontuação combinada na escala e no modo publicados, e os valores de fato que algum critério consome.
- **FR-2208**: Posições compartilhadas MUST seguir a numeração do motor — quantos estão à frente mais
  um, com as posições consumidas puladas (`FR-026` da `015`) — e o painel MUST dizer que a posição é
  dividida e com quantos.
- **FR-2209**: Cada linha MUST dizer **por que** o candidato está ali, numa frase: pontuação distinta de
  todas; empatou na pontuação e foi separado por um critério, nomeado com os valores comparados; empatou
  em tudo e divide a posição, sem que o sistema escolha; ou não tem posição, com a causa (Etapa sem
  nota, eliminação).
- **FR-2210**: Quando um critério foi oferecido a um grupo e não o separou, a frase MUST dizer por quê:
  valores iguais, ou valor ausente com "o critério não se aplica" (`FR-071` da `015`).
- **FR-2211**: A explicação MUST sair da mesma partição que produz a ordem oficial, e não de uma segunda
  implementação da ordem (D-011).

#### O corte e a progressão

- **FR-2212**: Com regra de corte declarada, cada linha MUST mostrar a situação no corte: dentro do alvo;
  suplente (na faixa, além do alvo); empate na fronteira do alvo; empate na última posição da faixa,
  que progride pelo desfecho `ADMITS_SURPLUS`; fora da faixa; corte não emitido; ou sem posição. Os
  membros de um mesmo grupo de empate residual MUST receber a mesma situação: o motor não os ordena
  entre si, e a prévia MUST NOT sugerir que um deles é titular e o outro excedente.
- **FR-2213**: Cada linha MUST mostrar a consequência para a Etapa seguinte: progride para a Etapa
  governada, nomeada; dentro da faixa de corte que não alimenta Etapa; fora da faixa, com o que a
  continuação declarada permite; ou sem posição, que nunca entra na faixa (`FR-191` da `014`).
- **FR-2214**: O painel MUST resumir a faixa: alvo, suplentes, tamanho da faixa, quantos progridem,
  quantos por empate, quantos sem posição.
- **FR-2215**: Empate residual que atravessa a última posição da faixa sob `STRICT` MUST aparecer como
  **resultado**: o corte não seria emitido, com a posição e o tamanho do empate, e o que destrava —
  julgar o desempate ou retificar o desfecho. Nenhuma linha MUST aparecer como "progride" nesse caso.
  O painel MUST NOT apresentar a recusa como erro de preenchimento (D-005).
- **FR-2216**: Desfecho não declarado MUST NOT ser presumido. Quando nenhum empate atravessa a faixa, o
  painel MUST dizer que o desfecho não muda nada naquela configuração; quando atravessa, MUST mostrar as
  duas consequências, uma por desfecho, e dizer que sem a declaração o Edital não publica.
- **FR-2217**: Quando o empate atravessa a última posição da faixa com o desfecho declarado, o painel MUST
  dizer também o que o outro desfecho faria, como comparação.
- **FR-2218**: Alvo do quadro MUST ser lido da linha geral do quadro de vagas do Perfil, como gravada no
  rascunho, e o painel MUST dizer de onde veio o número. Sem a linha, o alvo MUST aparecer como não
  apurável, e não como zero.
- **FR-2219**: Marco sem regra de corte MUST mostrar a ordem e dizer que o marco não corta.

#### A fronteira das vagas

- **FR-2220**: Quando um grupo de empate residual entre os que progrediram fica parte dentro e parte fora
  das primeiras **vagas** — a linha geral do quadro do Perfil —, o painel MUST avisar que a apuração da
  ocupação **pararia** naquela posição, se fosse apurada sobre este marco, qualquer que seja o desfecho
  declarado (D-006, `R-002` da `019`).
- **FR-2221**: O aviso da fronteira das vagas MUST supor todos os que progrediram habilitados na Etapa
  governada, e MUST dizer que supõe. Sem quadro de vagas, MUST dizer que não foi avaliado.
- **FR-2222**: O painel MUST NOT exibir estado de sucesso — sem aviso, "tudo certo" — quando o corte não
  sairia ou quando a apuração pararia. Quando não há empate em fronteira nenhuma, MUST dizer isso
  explicitamente.

#### Recálculo e cenários

- **FR-2223**: A prévia MUST ser calculada sobre o marco **digitado**, lido pelo mesmo leitor que a
  gravação usa, e MUST se recalcular a cada alteração de campo que ela lê, sem gravar (D-002).
- **FR-2224**: O cálculo MUST acontecer no servidor. Nenhuma regra de combinação, ordenação, corte ou
  apuração MUST existir em código do navegador.
- **FR-2225**: A prévia MUST oferecer, no mínimo, os cenários: classificação sem empate; desempate por
  critérios sucessivos; corte impedido por empate residual na última posição da faixa; empate na
  fronteira das vagas; valor ausente (sem nota em Etapa, eliminado na Etapa do marco, fato ausente).
- **FR-2226**: Cada cenário MUST dizer o que foi construído para mostrar e, quando a configuração digitada
  desfaz a situação, MUST dizer que ela não ocorre e por quê.
- **FR-2227**: Declaração incompleta que o motor exige para calcular MUST ser nomeada no painel, campo a
  campo, sem resultado presumido.
- **FR-2228**: Faixas maiores que a tela MUST agrupar os trechos sem empate, sem fronteira e sem ausência
  numa linha que diz o intervalo e quantos são, e MUST mostrar por inteiro as linhas próximas de cada
  fronteira.

#### O comportamento pendente de decisão

- **FR-2229**: O painel MUST descrever o desfecho do empate pelo que o sistema faz hoje, identificado
  como comportamento atual, e MUST NOT apresentar como definitiva nenhuma das leituras pendentes do
  achado de 19/10 (DP-1 a DP-4). Esta feature MUST NOT alterar o rótulo do campo, a redação do
  documento nem a regra.

#### O motor

- **FR-2230**: A prévia MUST usar as mesmas funções de combinação, ordenação, faixa e apuração que o
  caminho oficial.
- **FR-2231**: A preparação do universo classificável — eliminação mais recente, pontuação ausente,
  combinação e montagem de quem tem e de quem não tem posição —, hoje dentro de `calcular_ordem`, MUST
  ser extraída para uma função pura, sem acesso a banco, chamada igualmente pelo caminho oficial e pela
  prévia. O recorte MUST ser parâmetro dela (D-004, D-008).
- **FR-2232**: A extração MUST NOT mudar o resultado oficial: a ordem, as posições, o empate residual, o
  critério que separou, os sem posição e os motivos, o universo do ato e a contagem de consultas do
  caminho oficial MUST permanecer os mesmos.
- **FR-2233**: A equivalência entre prévia e caminho oficial MUST ser verificada por teste, com os mesmos
  dados pelos dois caminhos, cobrindo classificação, posições compartilhadas, aplicação ordenada dos
  critérios, valor ausente, corte com e sem suplentes, `ADMITS_SURPLUS`, recusa por `STRICT` e recusa da
  fronteira das vagas. Uma alteração no motor oficial que a prévia não acompanhe MUST reprovar o teste.

#### Sem efeito oficial

- **FR-2234**: Abrir, recalcular, trocar cenário e fechar a prévia MUST NOT gravar nada: nenhum ato,
  nenhuma posição, nenhum corte, nenhuma apuração, nenhum evento de trilha, nenhuma alteração do
  rascunho ou de configuração, nenhuma persistência de candidato fictício.
- **FR-2235**: A prévia MUST exigir a mesma autorização da tela de composição que a contém, com a mesma
  negativa para Edital fora do escopo.

#### Acessibilidade e política de conteúdo

- **FR-2236**: O painel MUST ser região nomeada; o resumo do recálculo MUST ser anunciado uma vez por
  tecnologia assistiva; o botão MUST dizer o que abre.
- **FR-2237**: Painel, botão e recálculo MUST funcionar sob a política de conteúdo vigente — sem estilo
  nem script escritos no template —, sem violação no console.

### Key Entities

- **Cenário**: conjunto nomeado de candidatos fictícios, com o que foi construído para mostrar e a
  âncora de cada situação (posição relativa ao alvo, à faixa ou às vagas). Não é gravado.
- **Candidato fictício**: nome fictício, nota por Etapa enumerada (por ordem de enumeração), consequência
  por Etapa decisória, valor por fato declarado do Perfil, ou ausência declarada pelo cenário.
- **Prévia**: o resultado do cálculo — linhas, resumo da faixa, recusa do corte, aviso da fronteira das
  vagas, declarações que faltam. Existe só na resposta.
- **Universo classificável**: a função pura extraída — classificáveis e sem posição — que o caminho
  oficial e a prévia compartilham.

## Decisões

### D-001 — O botão fica no cartão, e o painel fora dele; a `FR-428` não precisa de emenda

A `FR-428` da `030` proíbe **texto de ajuda visível** dentro dos cartões de composição. Três leituras
foram conferidas:

- **O botão não é ajuda.** É controle de ação, como "Acrescentar critério" e "Remover este marco", que
  já estão no cartão. O rótulo dele nomeia o que ele faz, e não explica campo nenhum.
- **O painel não está no cartão.** Ele mora num contêiner da página, irmão da composição, como o bloco
  "Como preencher" da etapa (`FR-426`, `FR-427` da `030`), que é o precedente: a ajuda saiu do cartão para
  a etapa, e continua ancorada ao marco.
- **O conteúdo do painel não é ajuda de preenchimento.** É resultado de cálculo sobre o que foi
  digitado — a mesma natureza da prévia da aplicação a outros Perfis (`_previa_da_aplicacao.html`), que
  também mora fora do cartão.

Por isso a solução é a que o usuário sugeriu, e a `FR-428` fica como está. Se o usuário decidir que o
botão no cartão já fere a regra, a alternativa sem emenda é o botão na linha do marco na vista do
conjunto (`053`), que fica fora do cartão; ela foi descartada porque a vista do conjunto só existe com
script e o cartão é onde o campo é alterado.

### D-002 — Recálculo pelo leitor do formulário e por htmx, no servidor

O recálculo segue o padrão da recomposição do cartão (`FR-413` da `030`): o painel pede o fragmento com
`hx-include` do cartão, o servidor lê o marco digitado com `marco_do_formulario` — o mesmo leitor da
gravação —, calcula e devolve o painel. Nada de regra no navegador (a CSP proíbe script inline e
`hx-vals` com `js:`), e nenhuma segunda leitura do formulário. A diferença em relação à recomposição: o
alvo do troco é o painel, e não o cartão — trocar o cartão a cada tecla perderia o foco do campo.

### D-003 — Os candidatos dependem do cenário e das fronteiras, e de nada mais

Candidatos fixos em números absolutos esconderiam a fronteira assim que o alvo passasse do tamanho
do cenário: com alvo 40, um cenário de 18 pessoas faz todos progredirem e não mostra nada. Candidatos
gerados a cada recálculo mudariam o que se compara. A escolha é a do meio: cada cenário ancora as suas
situações em posições **relativas** — à última do alvo, à última da faixa, à última das vagas —, e os
candidatos são função determinística do cenário, das Etapas enumeradas, dos fatos declarados do Perfil
e dos três números (alvo, suplentes, vagas). Alterar pesos, critérios, desfecho, Etapa governada ou
continuação não muda ninguém; alterar um dos três números reposiciona o cenário, e o painel diz que
reposicionou.

O cenário "Empate na fronteira das vagas" ancora o empate nas **vagas**, e não na faixa: é o que mostra
o caso da primeira linha da reprodução do achado — com 10 vagas e 10 + 5, o empate na 10ª fica dentro da
faixa, o corte sai, e a apuração para.

### D-004 — A preparação do universo sai de `calcular_ordem` para uma função pura

Conferido no código em 19/10, em `745f115f`. `calcular_ordem` faz duas coisas: **consulta** —
`effective_version`, o recorte por `normalizar_recorte`, `restringir_a_participantes`, os Resultados
`vigentes` com o `order_by` que decide o colapso, as âncoras dos Resultados, os fatos — e **decide** —
quem tem a eliminação mais recente, quem não tem pontuação e por quê, a combinação, a montagem de
classificáveis e sem posição, e a chamada a `ordenar`. A segunda metade é a regra, e é a que a prévia
precisa; ela não lê banco, e só depende de dicionários que a primeira já monta.

A extração leva a segunda metade para `classificacao/domain`, e `calcular_ordem` passa a chamá-la. As
consultas ficam onde estão: o filtro do recorte continua na consulta (orçamento de consulta verificado
por teste), e a função pura recebe o recorte e o reaplica sobre o que recebeu, o que é idempotente no
caminho oficial e é o que a prévia da fatia 2 vai usar. A constante `ELIMINADA` passa a vir de um
vocabulário de domínio, e não de `ResultadoEtapa.Consequencia`, para que o módulo puro não importe
modelo.

Alternativa descartada: a prévia montar classificáveis por conta própria e chamar só `combinar` e
`ordenar`. Seriam duas montagens do mesmo universo, e a primeira regra nova de exclusão divergiria
em silêncio — exatamente o que a equivalência existe para impedir.

### D-005 — A recusa é resultado, e o painel diz o que destrava

O motor recusa a emissão sob `STRICT` com empate na última posição da faixa (`FR-195` da `014`). A prévia
mostra isso como o desfecho da regra: um bloco que diz "o corte não seria emitido", com posição e
tamanho do empate, e o que destrava. Não usa a aparência de erro de formulário, porque não há nada
errado no preenchimento: a regra está declarada e faz o que faz. Desenhá-la como erro levaria o
elaborador a "corrigir" o desfecho para fazer o aviso sumir — escolha normativa que é dele, e não da
tela.

### D-006 — A fronteira das vagas é aviso condicional, e supõe todos habilitados

A recusa da apuração depende de quem habilitou na Etapa governada, que na composição ainda não existe.
A prévia supõe todos habilitados — o caso em que a recusa mais aparece — e diz que supõe. O aviso é
condicional ("se a ocupação for apurada sobre este marco") porque a apuração é pedida por marco, e um
marco intermediário pode não ser o que a apuração usa. As vagas são as **publicadas** da linha geral do
quadro: na composição não há movimento, e efetivas e publicadas coincidem.

### D-007 — Sorteio fica fora da fatia 1

Decisão do usuário de 19/10/2026. A ordem por sorteio nasce da semente, que não existe na composição; uma
prévia dela exigiria semente fictícia e explicação do algoritmo, que é outro produto. O botão não aparece
em marco por sorteio, e nenhuma frase do painel finge cobri-lo.

### D-008 — A fatia 2 entra pelo recorte e pelo vocabulário da apuração, sem reescrita

A fatia 2 (ampla como universo inteiro, Modalidades reservadas, PPI, PcD, concomitância, ocupação,
reversão) entra por três portas que esta fatia deixa abertas, sem implementá-las:

- **O recorte é parâmetro da função extraída** (D-004). Nulo é a ampla, que é o universo inteiro e não
  uma Modalidade declarada (`FR-492`, `FR-493` da `034`); a reservada filtra pela Modalidade.
- **O candidato fictício já carrega uma Modalidade**, nula em toda a fatia 1, para que a fatia 2
  acrescente cenários sem mudar a forma.
- **A prévia chama a apuração pela função pura** (`titulares_iniciais`), que já recebe os ocupantes da
  ampla — a concomitância, que vale sempre, entra como dado, e não como configuração. A reversão,
  declarada ou não, entra por `quantidade_a_reverter`, também pura.

### D-009 — A prévia é da composição, e não da Retificação

A Retificação (`048`) tem tela e fluxo próprios, e o marco publicado já tem ordem real, que é o que se
deve olhar. Fica registrado como possibilidade, não como escopo.

### D-010 — O protótipo vive fora do código de produto

O protótipo desta spec mora em `specs/094-previa-da-classificacao/prototipo/`, com servidor próprio da
biblioteca padrão e entrada própria no `.claude/launch.json`. Ele importa as funções puras do motor
(`combinar`, `ordenar`, `faixa.calcular`, `titulares_iniciais`) e as executa de verdade; o que é
demonstrativo — a geração dos cenários, a função extraída, as frases — é marcado na tela como tal.
Ficar fora de `backend/processo_seletivo` evita que um protótipo entre nas varreduras, nos inventários e
nos guardiões do produto, e deixa claro que não é a implementação.

### D-011 — A explicação vem da partição do motor

A frase "separado pelo 2º critério" precisa saber quais critérios agiram sobre o grupo de cada
candidato. `ordenar` devolve só o último (`separado_por`). Recompor a trajetória fora dele seria uma
segunda ordenação. A solução é uma irmã de `ordenar` que devolve a mesma lista com a trajetória de cada
item — quais critérios foram oferecidos ao grupo dele e qual separou —, e `ordenar` passa a ser essa
irmã sem a trajetória. A igualdade das duas saídas, menos a chave nova, é teste.

## Decisões pendentes do usuário

Registradas, não decididas. Esta feature não altera nenhuma delas; o painel descreve o comportamento
atual e não adota leitura (FR-2229).

### DP-1 — O rótulo de `STRICT` no cartão

*"A faixa para no alvo"* nomeia a fronteira errada sempre que há suplentes, e não diz que o corte é
recusado. Corrigir o rótulo, ou o motor, é decisão do usuário. **Preferência preliminar do usuário (19/10):
preservar a recusa de emissão diante de empate residual** — o que, se confirmado, recai sobre o rótulo e
o documento, e não sobre o motor.

### DP-2 — O referente de "esse número" no documento

A frase *"Se houver empate na última posição, esse número não é ultrapassado"* segue uma frase que
publicou dois números (alvo e suplentes). Mudá-la mexe na unidade indivisível das frases do corte
(`FR-1375` da `069`) e no que os próximos Editais publicam; o acervo não se regenera.

### DP-3 — A fronteira das vagas efetivas merece declaração?

Hoje é recusa sem norma, de propósito (`R-002` da `019`). Declará-la seria campo novo no conteúdo
canônico. A prévia avisa, e não propõe campo.

### DP-4 — Suplentes e cadastro de reserva

A relação entre os dois quando há cadastro é a pendência DP-05 que `frases_do_corte` cita. A prévia não
mostra cadastro de reserva, e não sugere relação nenhuma.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-840**: Em teste de uso com ao menos cinco elaboradores, ao menos quatro respondem corretamente,
  olhando só a prévia, para um candidato apontado: por que ele ficou naquela posição, se alcança o corte
  e se progride à Etapa seguinte.
- **SC-841**: O painel mostra o resultado novo em até 1 segundo depois da alteração de um campo, para
  faixas de até 500 candidatos fictícios.
- **SC-842**: Em 100% dos casos da matriz de equivalência (FR-2233), a prévia e o caminho oficial
  produzem as mesmas posições, o mesmo empate residual, o mesmo critério que separou, a mesma faixa e a
  mesma recusa.
- **SC-843**: Em qualquer sequência de aberturas, recálculos, trocas de cenário e fechamentos, o banco
  recebe zero escritas e a trilha zero eventos.
- **SC-844**: Todos os testes existentes de classificação, corte e ocupação passam sem alteração depois da
  extração, e a contagem de consultas do caminho oficial não muda.
- **SC-845**: Nos cenários e configurações em que o corte não sairia ou a apuração pararia, 100% dos
  painéis mostram o bloco de recusa ou o aviso; em nenhum deles o painel diz que não houve problema.
- **SC-846**: A 375 px de largura, abrir, recalcular, trocar cenário e fechar não produzem rolagem
  horizontal da página; posição, candidato, motivo e situação ficam legíveis.
- **SC-847**: Zero violações da política de conteúdo no console do navegador em toda a jornada da prévia.

## Assumptions

- **LGPD (Princípio III da Constituição)**: a prévia não trata dado pessoal. Os candidatos são
  fictícios, gerados na resposta e descartados com ela; nenhuma inscrição real é lida (FR-2204), nada é
  persistido (FR-2234), e nenhum registro de auditoria é produzido porque não há operação sobre dado de
  ninguém. A leitura do rascunho é a mesma que a tela de composição já faz, com a mesma autorização
  (FR-2235).
- **Pesos, fatos e quadro vêm do gravado.** Pesos são da Etapa (passo Etapas), fatos declarados e quadro
  de vagas são do Perfil (passo Perfis); nenhum deles é campo do cartão do marco, e a prévia os lê do
  rascunho gravado, como a recomposição do cartão já faz com Etapas e fatos.
- **Até quatro Etapas não decisórias enumeradas.** Os cenários definem notas para até quatro; os Editais
  da amostra usam até três.
- **A Etapa do marco é a última enumerada**, como em `calcular_ordem`; o candidato "eliminado" do cenário
  de valor ausente é eliminado nela.
- **Todos os candidatos fictícios participam do marco**: a restrição a participantes
  (`restringir_a_participantes`) é consulta de banco sobre a progressão real, e a prévia não a simula.
- **A apuração da prévia não tem movimentos**: efetivas = publicadas da linha geral do quadro.
- **O vocabulário dos rótulos do painel é o do cartão** — ninguém precisa aprender termo novo
  (`FR-425` da `030`) — e a descrição do efeito do desfecho é do comportamento atual (FR-2229).
